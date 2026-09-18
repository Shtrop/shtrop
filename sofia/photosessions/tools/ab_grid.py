#!/usr/bin/env python3
"""Сетка перебора: один кадр во всех сочетаниях guidance x вес identity x вес LoRA.

Нужна, чтобы подобрать параметры по результату, а не наугад. Каждое сочетание
складывается в свою подпапку, имя папки — сами параметры.

  python tools\\ab_grid.py --batch build\\corset_cellar\\batch.json --shot S28-01 ^
      --workflow D:\\AI_CONTENT\\Sofia\\workflows\\sofia_flux_photo_api.json ^
      --out "%USERPROFILE%\\Desktop\\Фотосессия\\_grid"
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import itertools
import json
import sys
import uuid
from pathlib import Path

_spec = importlib.util.spec_from_file_location("rs", Path(__file__).with_name("run_session.py"))
rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rs)

def main() -> int:
    ap = argparse.ArgumentParser(description="Сетка подбора параметров на одном кадре")
    ap.add_argument("--batch", required=True, type=Path)
    ap.add_argument("--workflow", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--shot", help="id кадра, по умолчанию первый в сессии")
    ap.add_argument("--server", default="127.0.0.1:8188")
    ap.add_argument("--guidance", nargs="*", type=float, default=[1.8, 2.2, 3.5])
    ap.add_argument("--identity", nargs="*", type=float, default=[0.75, 0.9])
    ap.add_argument("--lora", nargs="*", type=float, default=[0.8])
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--no-detailer", action="store_true",
                    help="глушить детейлер: он и воскует кожу, и ломает сходство")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    graph = json.loads(args.workflow.read_text(encoding="utf-8"))
    if "nodes" in graph:
        print("Workflow в формате редактора. Нужен Export (API).", file=sys.stderr)
        return 2

    job = next((j for j in batch["jobs"] if j["id"] == args.shot), None) if args.shot \
        else batch["jobs"][0]
    if job is None:
        print(f"Кадр {args.shot} не найден в {args.batch}", file=sys.stderr)
        return 2

    binding = rs.autodetect(graph)
    if binding.missing():
        print(f"Не найдены узлы: {', '.join(binding.missing())}. {binding.describe()}", file=sys.stderr)
        return 2

    combos = list(itertools.product(args.guidance, args.identity, args.lora))
    print(f"Кадр {job['id']}, seed {job['seed']}, сочетаний {len(combos)}")
    print(f"Привязка: {binding.describe()}")
    print(f"Детейлер: {'заглушен' if args.no_detailer else 'как в графе'}")
    print(f"Каталог: {args.out}\n")
    if args.dry_run:
        for g, i, l in combos:
            print(f"  guidance {g} · identity {i} · lora {l}")
        return 0

    client_id = str(uuid.uuid4())
    made, failed = [], []
    for guidance, identity, lora in combos:
        tag = f"g{guidance}_id{identity}_lora{lora}" + ("_nodet" if args.no_detailer else "")
        out_dir = args.out / tag
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"  {tag}")
        try:
            g = rs.set_weights(graph, identity, lora, args.no_detailer)
            g = rs.patch(g, binding, job, job["seed"], guidance, args.steps)
            queued = rs.post(args.server, "/prompt", {"prompt": g, "client_id": client_id})
            record = rs.wait_for(args.server, queued["prompt_id"], args.timeout)
            files = rs.save_images(args.server, record, out_dir, f"{job['id']}_{tag}")
            made.append({"tag": tag, "guidance": guidance, "identity": identity, "lora": lora,
                         "files": [str(f) for f in files]})
        except Exception as exc:
            print(f"      СБОЙ: {exc}")
            failed.append({"tag": tag, "error": str(exc)})

    (args.out / "grid_manifest.json").write_text(json.dumps(
        {"shot": job["id"], "seed": job["seed"], "published": False,
         "made": made, "failed": failed}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nГотово: {len(made)} вариантов, сбоев {len(failed)}")
    print(f"Сравнивайте кожу и сходство между папками. Манифест: {args.out / 'grid_manifest.json'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
