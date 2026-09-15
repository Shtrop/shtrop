#!/usr/bin/env python3
"""Преконтроль окружения перед прогоном LongCat-Video-Avatar 1.5.

Проверяет то, что реально ломает запуск: версию python, torch с CUDA, объём
VRAM, свободное место под веса, ffmpeg, attention-бэкенд. Ничего не меняет.

    python preflight.py --repo ./LongCat-Video --vram_budget_gb 24
Коды возврата: 0 — можно запускать, 1 — есть FAIL.
"""
import argparse, importlib.util, os, shutil, subprocess, sys

WEIGHTS_GB = 60          # грубая оценка места под базовую модель + avatar-1.5
results = []


def add(level: str, name: str, detail: str) -> None:
    results.append((level, name, detail))


def have(mod: str) -> bool:
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ValueError):
        return False


def check_python() -> None:
    v = f"{sys.version_info.major}.{sys.version_info.minor}"
    if v in ("3.10", "3.11", "3.12"):
        add("PASS", "python", f"{v} ({sys.executable})")
    else:
        add("FAIL", "python", f"{v} — torch==2.6.0 не имеет колёс; нужен 3.10-3.12")


def check_torch() -> None:
    if not have("torch"):
        add("FAIL", "torch", f"не установлен в {sys.executable}")
        return
    import torch
    add("PASS", "torch", torch.__version__)
    if torch.cuda.is_available():
        n = torch.cuda.device_count()
        names = ", ".join(torch.cuda.get_device_name(i) for i in range(n))
        add("PASS", "cuda", f"{n} GPU: {names}")
    else:
        add("FAIL", "cuda", "torch.cuda.is_available() == False — прогон невозможен")


def check_vram(budget_gb: float) -> None:
    if not shutil.which("nvidia-smi"):
        add("NOT_MEASURED", "vram", "nvidia-smi не найден")
        return
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.used,name",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15, check=True).stdout
    except (subprocess.SubprocessError, OSError) as e:
        add("NOT_MEASURED", "vram", f"nvidia-smi не отработал: {e}")
        return
    for line in (l for l in out.splitlines() if l.strip()):
        total, used, name = [x.strip() for x in line.split(",", 2)]
        free_gb = (int(total) - int(used)) / 1024
        lvl = "PASS" if free_gb >= budget_gb else "WARN"
        add(lvl, "vram", f"{name}: свободно {free_gb:.1f} GB из {int(total)/1024:.1f} "
                         f"(бюджет {budget_gb} GB)")


def check_disk(repo: str) -> None:
    target = repo if os.path.isdir(repo) else os.path.dirname(os.path.abspath(repo)) or "."
    try:
        free_gb = shutil.disk_usage(target).free / 2**30
    except OSError as e:
        add("NOT_MEASURED", "диск", str(e))
        return
    lvl = "PASS" if free_gb >= WEIGHTS_GB else "WARN"
    add(lvl, "диск", f"свободно {free_gb:.0f} GB на {target} (под веса нужно ~{WEIGHTS_GB} GB)")


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg"):
        add("PASS", "ffmpeg", shutil.which("ffmpeg"))
    else:
        add("WARN", "ffmpeg", "не найден в PATH — сохранение видео со звуком не отработает")


def check_backend() -> None:
    found = [m for m in ("flash_attn_interface", "flash_attn", "xformers") if have(m)]
    if found:
        add("PASS", "attention", ", ".join(found))
    else:
        add("WARN", "attention", "нет ни flash-attn, ни xformers — встроенная ветка, "
                                 "медленнее и прожорливее по памяти")


def check_repo(repo: str) -> None:
    demo = os.path.join(repo, "run_demo_avatar_single_audio_to_video.py")
    if not os.path.isfile(demo):
        add("FAIL", "репозиторий", f"{repo}: нет демо-скрипта, сначала setup.sh/setup.ps1")
        return
    src = os.path.join(repo, "longcat_video", "modules", "attention.py")
    try:
        with open(src, encoding="utf-8") as f:
            head = "".join(f.readlines()[:15])
    except OSError as e:
        add("WARN", "репозиторий", f"не прочитать attention.py: {e}")
        return
    if "from ..block_sparse_attention.bsa_interface import flash_attn_bsa_3d" in head:
        add("FAIL", "патч", "longcat-compat.patch не наложен (импорт triton остался)")
    else:
        add("PASS", "патч", "longcat-compat.patch наложен")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default="./LongCat-Video")
    p.add_argument("--vram_budget_gb", type=float, default=24.0)
    a = p.parse_args()

    check_python()
    check_torch()
    check_vram(a.vram_budget_gb)
    check_disk(a.repo)
    check_ffmpeg()
    check_backend()
    check_repo(a.repo)

    width = max(len(n) for _, n, _ in results)
    print("--- преконтроль ---")
    for lvl, name, detail in results:
        print(f"  {lvl:<13} {name:<{width}}  {detail}")
    fails = [r for r in results if r[0] == "FAIL"]
    print(f"итог: {'FAIL' if fails else 'PASS'} "
          f"({len(fails)} блокирующих, {sum(1 for r in results if r[0] == 'WARN')} предупреждений)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
