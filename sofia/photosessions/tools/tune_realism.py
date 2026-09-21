#!/usr/bin/env python3
"""Осмотр и правка узлов workflow, отвечающих за пластиковую кожу.

Показать, что стоит сейчас:
  python tools\\tune_realism.py "D:\\AI_CONTENT\\Sofia\\workflows\\sofia_flux_photo_api.json"

Сохранить исправленную копию (исходный файл НЕ трогается):
  python tools\\tune_realism.py "...\\sofia_flux_photo_api.json" --write "...\\sofia_flux_photo_real_api.json"
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

# Рекомендации против пластика: поле -> (целевое значение, причина)
TARGETS = {
    "guidance":        (2.0,  "высокий guidance выглаживает кожу"),
    "cfg":             (2.0,  "то же для SD-подобных графов"),
    "steps":           (40,   "больше шагов на низком guidance = детали без выглаживания"),
    "strength_model":  (0.8,  "LoRA: ниже 0.7 сходство рассыпается, выше 0.9 лицо воскует"),
    "strength_clip":   (0.8,  "то же по clip-ветке"),
    "lora_strength":   (0.8,  "LoRA: ниже 0.7 сходство рассыпается, выше 0.9 лицо воскует"),
    "weight":          (0.85, "PuLID/IPAdapter держит СХОДСТВО — не опускать ради текстуры"),
    "denoise":         (0.30, "высокий denoise на апскейле и детейлере стирает поры"),
}
# Каждое поле правим только в своём классе узлов.
# denoise основного сэмплера трогать НЕЛЬЗЯ: для txt2img он должен остаться 1.0.
FIELD_CLASSES = {
    "guidance":       ("fluxguidance", "guidance"),
    "cfg":            ("ksampler", "sampler"),
    "steps":          ("ksampler", "sampler", "basicscheduler", "scheduler"),
    "strength_model": ("lora",),
    "strength_clip":  ("lora",),
    "lora_strength":  ("lora",),
    "weight":         ("pulid", "ipadapter", "instantid"),
    "denoise":        ("detailer", "upscale", "facerestore", "codeformer", "gfpgan", "reactor"),
}


def relevant(class_type: str, field: str) -> bool:
    """Поле уместно, только если класс узла из его списка."""
    low = class_type.lower()
    allowed = FIELD_CLASSES.get(field, ())
    if field == "denoise":
        # сэмплер может содержать и denoise, и слово sampler в имени — исключаем явно
        if "sampler" in low and not any(s in low for s in allowed):
            return False
    return any(s in low for s in allowed)


def scan(graph: dict) -> list[tuple]:
    found = []
    for node_id, node in graph.items():
        ctype = str(node.get("class_type", ""))
        title = node.get("_meta", {}).get("title", "")
        for field, value in node.get("inputs", {}).items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                continue
            if field not in TARGETS or not relevant(ctype, field):
                continue
            target, why = TARGETS[field]
            found.append((node_id, ctype, title, field, value, target, why))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Настройка workflow против пластиковой кожи")
    ap.add_argument("workflow", type=Path)
    ap.add_argument("--write", type=Path, help="куда сохранить исправленную копию")
    ap.add_argument("--guidance", type=float, default=2.0)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--lora", type=float, default=0.8, help="вес LoRA")
    ap.add_argument("--identity", type=float, default=0.85,
                    help="вес PuLID/IPAdapter: он отвечает за сходство, не опускать ради текстуры")
    ap.add_argument("--denoise", type=float, default=0.30)
    args = ap.parse_args()

    graph = json.loads(args.workflow.read_text(encoding="utf-8"))
    if "nodes" in graph:
        print("Это формат редактора. Нужен Workflow -> Export (API).")
        return 2

    TARGETS["guidance"] = (args.guidance, TARGETS["guidance"][1])
    TARGETS["cfg"] = (args.guidance, TARGETS["cfg"][1])
    TARGETS["steps"] = (args.steps, TARGETS["steps"][1])
    for f in ("strength_model", "strength_clip", "lora_strength"):
        TARGETS[f] = (args.lora, TARGETS[f][1])
    TARGETS["weight"] = (args.identity, TARGETS["weight"][1])
    TARGETS["denoise"] = (args.denoise, TARGETS["denoise"][1])

    found = scan(graph)
    if not found:
        print("Подозрительных параметров не найдено — граф уже минимальный.")
        return 0

    print(f"Файл: {args.workflow}\n")
    print(f"{'узел':>5}  {'класс':<26} {'поле':<15} {'сейчас':>8} {'цель':>8}")
    print("-" * 74)
    changes = []
    for node_id, ctype, title, field, value, target, why in found:
        mark = " " if abs(value - target) < 1e-6 else "*"
        print(f"{node_id:>5}  {ctype[:26]:<26} {field:<15} {value:>8} {target:>8} {mark}")
        if mark == "*":
            changes.append((node_id, ctype, field, value, target, why))

    detailers = [(nid, str(n.get("class_type"))) for nid, n in graph.items()
                 if any(s in str(n.get("class_type", "")).lower()
                        for s in ("facedetailer", "facerestore", "codeformer", "gfpgan", "reactor"))]

    print("\nЧто менять:" if changes else "\nВсё уже в рекомендованных значениях.")
    for node_id, ctype, field, value, target, why in changes:
        print(f"  узел {node_id} ({ctype}): {field} {value} -> {target}  — {why}")
    if detailers:
        print("\nГлавный подозреваемый по пластику — детейлер/восстановление лица:")
        for node_id, ctype in detailers:
            print(f"  узел {node_id}: {ctype} — обойти целиком (bypass) и сравнить кадр")
        print("  Он же часто и ломает сходство: перерисовывает лицо своей моделью поверх LoRA.")
    print("\nСходство и пластик — разные рычаги:")
    print("  сходство слабое  -> вес PuLID/LoRA ВВЕРХ (0.85-0.95), детейлер выключить")
    print("  пластик          -> guidance ВНИЗ (1.8-2.2), denoise апскейла вниз, детейлер выключить")
    print("  подобрать вслепую долго — гоняйте сетку: tools\\ab_grid.py")

    if args.write:
        patched = copy.deepcopy(graph)
        for node_id, _, field, _, target, _ in changes:
            patched[node_id]["inputs"][field] = target
        if args.write.exists():
            print(f"\nФайл {args.write} уже существует — не перезаписываю.")
            return 1
        args.write.write_text(json.dumps(patched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nИсправленная копия: {args.write}")
        print(f"Исходный файл не изменён: {args.workflow}")
        print("\nПрогон на ней:")
        print(f'  powershell -ExecutionPolicy Bypass -File tools\\run_all.ps1 '
              f'-Workflow "{args.write}" -Sessions white_lace_morning -Variants 1')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
