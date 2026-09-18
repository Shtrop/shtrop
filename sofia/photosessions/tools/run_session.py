#!/usr/bin/env python3
"""Прогон фотосессии через локальный ComfyUI и сохранение кадров на диск.

Запускать НА МАШИНЕ СТУДИИ, где подняты ComfyUI и Sofia LoRA/PuLID.
Скрипт ничего не публикует и ничего не удаляет: только ставит задачи в очередь
ComfyUI и пишет новые PNG. Существующие файлы не перезаписываются.

Пример:
  python tools/run_session.py ^
      --batch build/golden_gym/batch.json ^
      --workflow D:\\AI_CONTENT\\Sofia\\workflows\\sofia_flux_api.json ^
      --out D:\\AI_CONTENT\\Sofia\\generated\\golden_gym

Workflow должен быть выгружен из ComfyUI в API-формате
(Workflow -> Export (API)), иначе в нём не будет нужных полей.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

SAMPLER_HINTS = ("sampler", "guider")
LATENT_HINTS = ("emptylatent", "emptysd3latent", "emptyimage", "latentimagepresets")
SEED_FIELDS = ("seed", "noise_seed", "rand_seed")
POSITIVE_FIELDS = ("text", "positive_prompt", "positive", "prompt")
NEGATIVE_FIELDS = ("negative_prompt", "negative", "text")
NEGATIVE_MARKERS = ("worst quality", "low quality", "blurry", "deformed", "watermark", "jpeg artifacts")


def is_text_node(class_type: str) -> bool:
    """Любой текстовый энкодер: CLIPTextEncode, T5TextEncode, WanVideoTextEncode, ..."""
    c = class_type.lower()
    return "text" in c and ("encode" in c or "prompt" in c)


def text_field(node: dict, fields: tuple) -> str | None:
    """Первое строковое поле узла из перечисленных."""
    inputs = node.get("inputs", {})
    for field in fields:
        if isinstance(inputs.get(field), str):
            return field
    return None


class Binding:
    """Куда в графе класть промпт, негатив, seed и размер кадра."""

    def __init__(self, positive=None, negative=None, seed=None, latent=None):
        self.positive = positive   # (node_id, field)
        self.negative = negative   # (node_id, field)
        self.seed = seed           # (node_id, field)
        self.latent = latent       # node_id

    def describe(self) -> str:
        return (f"positive={self.positive} negative={self.negative} "
                f"seed={self.seed} latent={self.latent}")

    def missing(self) -> list[str]:
        return [n for n, v in (("positive", self.positive), ("seed", self.seed)) if v is None]


def autodetect(graph: dict) -> Binding:
    """Найти узлы по структуре графа: от сэмплера через guidance к текстовому энкодеру."""
    b = Binding()

    def follow(ref, fields, depth=6, seen=None):
        """Пройти по ссылке [node_id, idx] до текстового узла, минуя guidance-обёртки."""
        seen = seen or set()
        if not isinstance(ref, list) or not ref or depth <= 0:
            return None
        node_id = str(ref[0])
        if node_id in seen:
            return None
        seen.add(node_id)
        node = graph.get(node_id)
        if not node:
            return None
        if is_text_node(node.get("class_type", "")):
            field = text_field(node, fields)
            return (node_id, field) if field else None
        for value in node.get("inputs", {}).values():
            hit = follow(value, fields, depth - 1, seen)
            if hit:
                return hit
        return None

    for node_id, node in graph.items():
        ctype = str(node.get("class_type", ""))
        low = ctype.lower()
        inputs = node.get("inputs", {})

        if any(h in low for h in SAMPLER_HINTS):
            if b.positive is None:
                for key in ("positive", "conditioning", "text_embeds", "guider"):
                    b.positive = b.positive or follow(inputs.get(key), POSITIVE_FIELDS)
            if b.negative is None:
                b.negative = follow(inputs.get("negative"), NEGATIVE_FIELDS)
        if b.seed is None:
            field = next((f for f in SEED_FIELDS if isinstance(inputs.get(f), (int, float))), None)
            if field and (any(h in low for h in SAMPLER_HINTS) or "noise" in low):
                b.seed = (node_id, field)
        if b.latent is None and any(h in low for h in LATENT_HINTS) and "width" in inputs:
            b.latent = node_id

    # Узел с двумя текстовыми полями сразу (Wan-подобные графы).
    if b.positive is None or b.negative is None:
        for node_id, node in graph.items():
            if not is_text_node(str(node.get("class_type", ""))):
                continue
            inputs = node.get("inputs", {})
            if isinstance(inputs.get("positive_prompt"), str) and isinstance(inputs.get("negative_prompt"), str):
                b.positive = b.positive or (node_id, "positive_prompt")
                b.negative = b.negative or (node_id, "negative_prompt")
                break

    # Запасной вариант: по заголовку узла или по содержимому (негатив выдаёт себя списком артефактов).
    if b.positive is None or b.negative is None:
        candidates = []
        for node_id, node in graph.items():
            if not is_text_node(str(node.get("class_type", ""))):
                continue
            field = text_field(node, ("text", "prompt"))
            if not field:
                continue
            title = str(node.get("_meta", {}).get("title", "")).lower()
            value = str(node["inputs"][field]).lower()
            looks_negative = ("negative" in title or "негатив" in title
                              or any(m in value for m in NEGATIVE_MARKERS))
            candidates.append((node_id, field, title, looks_negative))
        for node_id, field, title, looks_negative in candidates:
            if looks_negative and b.negative is None:
                b.negative = (node_id, field)
            elif not looks_negative and b.positive is None:
                b.positive = (node_id, field)

    # Любой seed-подобный числовой вход, если структура не помогла.
    if b.seed is None:
        for node_id, node in graph.items():
            field = next((f for f in SEED_FIELDS
                          if isinstance(node.get("inputs", {}).get(f), (int, float))), None)
            if field:
                b.seed = (node_id, field)
                break
    return b


def parse_ref(value: str, with_field: bool = True):
    """Разбор ручного указания узла: '6:text' или '27'."""
    if not value:
        return None
    if not with_field:
        return value.split(":")[0]
    node_id, _, field = value.partition(":")
    return (node_id, field or "text")


def patch(graph: dict, binding: Binding, job: dict, seed: int) -> dict:
    g = copy.deepcopy(graph)
    node_id, field = binding.positive
    g[node_id]["inputs"][field] = job["prompt"]
    if binding.negative:
        node_id, field = binding.negative
        g[node_id]["inputs"][field] = job["negative_prompt"]
    node_id, field = binding.seed
    g[node_id]["inputs"][field] = seed
    if binding.latent:
        latent_inputs = g[binding.latent]["inputs"]
        latent_inputs["width"] = job["width"]
        latent_inputs["height"] = job["height"]
        latent_inputs["batch_size"] = 1
    return g


def post(server: str, path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"http://{server}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(server: str, path: str) -> dict:
    with urllib.request.urlopen(f"http://{server}{path}", timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_for(server: str, prompt_id: str, timeout: int) -> dict:
    """Дождаться готовности задачи и вернуть её history-запись."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        history = get_json(server, f"/history/{prompt_id}")
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"ComfyUI не отдал результат за {timeout} c (prompt_id={prompt_id})")


def save_images(server: str, record: dict, out_dir: Path, stem: str) -> list[Path]:
    saved = []
    for node_output in record.get("outputs", {}).values():
        for index, image in enumerate(node_output.get("images", []), start=1):
            query = urllib.parse.urlencode({
                "filename": image["filename"],
                "subfolder": image.get("subfolder", ""),
                "type": image.get("type", "output"),
            })
            target = out_dir / f"{stem}_{index:02d}.png"
            if target.exists():
                print(f"      пропуск, файл уже есть: {target.name}")
                continue
            with urllib.request.urlopen(f"http://{server}/view?{query}", timeout=120) as resp:
                target.write_bytes(resp.read())
            saved.append(target)
            print(f"      сохранено: {target}")
    return saved


def main() -> int:
    ap = argparse.ArgumentParser(description="Прогон сессии Sofia через ComfyUI")
    ap.add_argument("--batch", required=True, type=Path, help="build/<slug>/batch.json")
    ap.add_argument("--workflow", required=True, type=Path, help="workflow в API-формате")
    ap.add_argument("--out", required=True, type=Path, help="каталог для PNG")
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--shots", nargs="*", help="только эти кадры, например S01-01 S01-07")
    ap.add_argument("--variants", type=int, help="переопределить число вариантов на кадр")
    ap.add_argument("--timeout", type=int, default=900, help="ожидание одного кадра, с")
    ap.add_argument("--dry-run", action="store_true", help="показать план и выйти")
    ap.add_argument("--list-nodes", action="store_true",
                    help="показать узлы workflow и выйти (диагностика привязки)")
    ap.add_argument("--positive", help="узел позитива вручную, например 6:text")
    ap.add_argument("--negative", help="узел негатива вручную, например 7:text")
    ap.add_argument("--seed-node", help="узел seed вручную, например 25:noise_seed")
    ap.add_argument("--latent-node", help="узел латента вручную, например 27")
    args = ap.parse_args()

    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    graph = json.loads(args.workflow.read_text(encoding="utf-8"))
    if "nodes" in graph and "links" in graph:
        print("ОШИБКА: workflow сохранён в формате редактора. Нужен Export (API).", file=sys.stderr)
        return 2

    if args.list_nodes:
        print(f"Узлы workflow {args.workflow.name}:\n")
        for node_id, node in sorted(graph.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
            ctype = node.get("class_type", "?")
            title = node.get("_meta", {}).get("title", "")
            fields = []
            for key, value in node.get("inputs", {}).items():
                if isinstance(value, str) and len(value) > 0:
                    preview = value[:60].replace("\n", " ")
                    fields.append(f"{key}='{preview}'")
                elif isinstance(value, (int, float)) and key in SEED_FIELDS + ("width", "height", "batch_size"):
                    fields.append(f"{key}={value}")
            mark = " <- текстовый" if is_text_node(ctype) else ""
            print(f"  {node_id:>4}  {ctype}{mark}" + (f"  [{title}]" if title else ""))
            for f in fields:
                print(f"        {f}")
        print(f"\nАвтопривязка: {autodetect(graph).describe()}")
        return 0

    binding = autodetect(graph)
    if args.positive:
        binding.positive = parse_ref(args.positive)
    if args.negative:
        binding.negative = parse_ref(args.negative)
    if args.seed_node:
        binding.seed = parse_ref(args.seed_node)
    if args.latent_node:
        binding.latent = parse_ref(args.latent_node, with_field=False)

    if binding.missing():
        print(f"ОШИБКА: не найдены узлы графа: {', '.join(binding.missing())}.", file=sys.stderr)
        print(f"        Найдено: {binding.describe()}", file=sys.stderr)
        print("        Посмотрите граф: --list-nodes, затем укажите узлы вручную:", file=sys.stderr)
        print("        --positive <id>:<поле> --negative <id>:<поле> --seed-node <id>:<поле>", file=sys.stderr)
        return 2

    jobs = batch["jobs"]
    if args.shots:
        wanted = set(args.shots)
        jobs = [j for j in jobs if j["id"] in wanted]
        if not jobs:
            print(f"ОШИБКА: кадры {sorted(wanted)} не найдены в {args.batch}", file=sys.stderr)
            return 2

    total = sum(args.variants or j["batch"] for j in jobs)
    print(f"Сессия {batch['session_id']} ({batch['slug']}): {len(jobs)} кадров, {total} изображений")
    print(f"Привязка к графу: {binding.describe()}")
    print(f"Каталог: {args.out}")
    if args.dry_run:
        for j in jobs:
            print(f"  {j['id']}: seed {j['seed']}, вариантов {args.variants or j['batch']}")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    client_id = str(uuid.uuid4())
    manifest, failed = [], []

    for job in jobs:
        variants = args.variants or job["batch"]
        print(f"  {job['id']} — {variants} вариант(ов), базовый seed {job['seed']}")
        for v in range(variants):
            seed = job["seed"] * 100 + v
            try:
                queued = post(args.server, "/prompt",
                              {"prompt": patch(graph, binding, job, seed), "client_id": client_id})
                record = wait_for(args.server, queued["prompt_id"], args.timeout)
                files = save_images(args.server, record, args.out, f"{job['id']}_seed{seed}")
                manifest.append({"id": job["id"], "seed": seed,
                                 "files": [str(f) for f in files]})
            except Exception as exc:  # сеть, таймаут, ошибка графа
                print(f"      СБОЙ: {exc}")
                failed.append({"id": job["id"], "seed": seed, "error": str(exc)})

    report = args.out / "run_manifest.json"
    report.write_text(json.dumps(
        {"session_id": batch["session_id"], "slug": batch["slug"], "published": False,
         "generated": manifest, "failed": failed},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\nГотово: {len(manifest)} изображений, сбоев {len(failed)}")
    print(f"Манифест: {report}")
    print("Публикация НЕ выполнялась — только запись на диск.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
