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

SAMPLERS = {"KSampler", "KSamplerAdvanced", "SamplerCustom", "SamplerCustomAdvanced"}
TEXT_NODES = {"CLIPTextEncode", "CLIPTextEncodeFlux", "CLIPTextEncodeSDXL"}
LATENT_NODES = {"EmptyLatentImage", "EmptySD3LatentImage", "EmptyLatentImagePresets"}
NOISE_NODES = {"RandomNoise", "KSamplerSelect"}


class Binding:
    """Куда в графе класть промпт, негатив, seed и размер кадра."""

    def __init__(self, positive=None, negative=None, seed=None, latent=None):
        self.positive = positive
        self.negative = negative
        self.seed = seed
        self.latent = latent

    def describe(self) -> str:
        return (f"positive={self.positive} negative={self.negative} "
                f"seed={self.seed} latent={self.latent}")

    def missing(self) -> list[str]:
        return [n for n, v in (("positive", self.positive), ("seed", self.seed)) if v is None]


def autodetect(graph: dict) -> Binding:
    """Найти узлы по структуре графа, а не по догадкам об именах."""
    b = Binding()

    def follow(ref):
        """Ссылка вида [node_id, output_index] -> id текстового узла."""
        if not isinstance(ref, list) or not ref:
            return None
        node_id = str(ref[0])
        node = graph.get(node_id)
        if node and node.get("class_type") in TEXT_NODES:
            return node_id
        return None

    for node_id, node in graph.items():
        ctype = node.get("class_type")
        inputs = node.get("inputs", {})
        if ctype in SAMPLERS:
            b.positive = b.positive or follow(inputs.get("positive"))
            b.negative = b.negative or follow(inputs.get("negative"))
            if "seed" in inputs and b.seed is None:
                b.seed = (node_id, "seed")
            elif "noise_seed" in inputs and b.seed is None:
                b.seed = (node_id, "noise_seed")
        if ctype in NOISE_NODES and "noise_seed" in inputs and b.seed is None:
            b.seed = (node_id, "noise_seed")
        if ctype in LATENT_NODES and b.latent is None:
            b.latent = node_id

    # Запасной вариант: по заголовку узла в ComfyUI.
    if b.positive is None or b.negative is None:
        for node_id, node in graph.items():
            if node.get("class_type") not in TEXT_NODES:
                continue
            title = str(node.get("_meta", {}).get("title", "")).lower()
            if b.positive is None and ("positive" in title or "промпт" in title):
                b.positive = node_id
            if b.negative is None and ("negative" in title or "негатив" in title):
                b.negative = node_id
    return b


def patch(graph: dict, binding: Binding, job: dict, seed: int) -> dict:
    g = copy.deepcopy(graph)
    g[binding.positive]["inputs"]["text"] = job["prompt"]
    if binding.negative:
        g[binding.negative]["inputs"]["text"] = job["negative_prompt"]
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
    args = ap.parse_args()

    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    graph = json.loads(args.workflow.read_text(encoding="utf-8"))
    if "nodes" in graph and "links" in graph:
        print("ОШИБКА: workflow сохранён в формате редактора. Нужен Export (API).", file=sys.stderr)
        return 2

    binding = autodetect(graph)
    if binding.missing():
        print(f"ОШИБКА: не найдены узлы графа: {', '.join(binding.missing())}.", file=sys.stderr)
        print(f"        Найдено: {binding.describe()}", file=sys.stderr)
        print("        Переименуйте текстовые узлы в 'positive'/'negative' и повторите.", file=sys.stderr)
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
