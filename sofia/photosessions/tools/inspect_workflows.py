#!/usr/bin/env python3
"""Осмотр workflow ComfyUI: какой годится для прогона фотосессии.

Запускать на машине студии:
  python tools\\inspect_workflows.py D:\\AI_CONTENT\\Sofia\\workflows

Для каждого файла показывает: API-формат или нет, видео это или фото,
и получается ли автоматически привязать позитив, негатив, seed и размер кадра.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("rs", Path(__file__).with_name("run_session.py"))
rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rs)

VIDEO_HINTS = ("i2v", "t2v", "wan", "video", "reel", "anim", "latentsync", "svd")
PHOTO_HINTS = ("flux", "photo", "foto", "image", "portrait", "sdxl", "pulid")


def kind(path: Path, graph: dict) -> str:
    """Фото или видео — по именам узлов, а не только по имени файла."""
    classes = " ".join(str(n.get("class_type", "")) for n in graph.values()).lower()
    name = path.name.lower()
    if any(h in classes or h in name for h in VIDEO_HINTS):
        return "видео"
    if any(h in classes or h in name for h in PHOTO_HINTS):
        return "фото"
    return "неясно"


def inspect(path: Path) -> dict:
    try:
        graph = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"path": path, "api": False, "note": f"не читается: {exc}"}
    if not isinstance(graph, dict) or "nodes" in graph:
        return {"path": path, "api": False, "note": "формат редактора, нужен Export (API)"}
    if not any(isinstance(v, dict) and "class_type" in v for v in graph.values()):
        return {"path": path, "api": False, "note": "не похоже на граф ComfyUI"}

    binding = rs.autodetect(graph)
    return {
        "path": path,
        "api": True,
        "kind": kind(path, graph),
        "nodes": len(graph),
        "binding": binding,
        "missing": binding.missing(),
    }


def main() -> int:
    argv = [a for a in sys.argv[1:] if a != "--pick"]
    pick_only = "--pick" in sys.argv     # печатать только путь годного фото-графа
    targets = [Path(a) for a in argv] or [Path.cwd()]
    files: list[Path] = []
    for target in targets:
        if target.is_dir():
            files.extend(sorted(target.rglob("*.json")))
        elif target.exists():
            files.append(target)
        else:
            print(f"нет такого пути: {target}", file=sys.stderr)

    if not files:
        print("JSON-файлы не найдены", file=sys.stderr)
        return 2

    usable = []
    if not pick_only:
        print(f"Осмотрено файлов: {len(files)}\n")
    for path in files:
        info = inspect(path)
        if not info["api"]:
            if not pick_only:
                print(f"[--] {path.name}\n     {info['note']}")
            continue
        if not pick_only:
            verdict = "ГОДЕН" if not info["missing"] else f"не хватает: {', '.join(info['missing'])}"
            flag = "ok" if not info["missing"] else "!!"
            print(f"[{flag}] {path.name}  ({info['kind']}, узлов {info['nodes']})")
            print(f"     {info['binding'].describe()}")
            print(f"     {verdict}")
            print(f"     {path}")
        if not info["missing"]:
            usable.append(info)

    if pick_only:
        photo = [i for i in usable if i["kind"] == "фото"]
        if not photo:
            print("фото-workflow не найден", file=sys.stderr)
            return 3
        print(photo[0]["path"])
        return 0

    print()
    photo = [i for i in usable if i["kind"] == "фото"]
    if photo:
        print("Для фотосессии брать:")
        for info in photo:
            print(f"  --workflow \"{info['path']}\"")
    elif usable:
        print("Фото-workflow не найден. Годные по структуре, но похожие на видео:")
        for info in usable:
            print(f"  {info['path']}  ({info['kind']})")
        print("Нужен фото-граф (FLUX + Sofia LoRA/PuLID), выгруженный через Workflow -> Export (API).")
    else:
        print("Ни один workflow не пригоден. Выгрузите фото-граф через Workflow -> Export (API)")
        print("и посмотрите его узлы: python tools\\run_session.py --list-nodes ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
