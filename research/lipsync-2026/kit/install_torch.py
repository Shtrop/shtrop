#!/usr/bin/env python3
"""Ставит сборку torch под конкретную видеокарту.

Зачем: колёса torch с PyPI под Windows собраны без CUDA, и любая установка
requirements может затереть ими рабочую CUDA-сборку. Плюс у новых карт своя
нижняя граница: Blackwell (RTX 50xx, sm_120) поддерживается только с torch 2.7
и колёс cu128 и новее — на cu124 прогон падает уже на первом ядре.

    python install_torch.py --dry-run      # показать, что будет сделано
    python install_torch.py                # поставить подходящую сборку
    python install_torch.py --channel cu128 --torch-version 2.7.1
"""
import argparse, importlib.metadata as md, re, shutil, subprocess, sys

# нижняя граница по архитектуре: compute capability -> (минимальный torch, канал)
ARCH_RULES = [
    (12.0, "2.7", "cu128"),   # Blackwell: RTX 50xx
    (9.0, "2.4", "cu124"),    # Hopper
    (8.0, "2.4", "cu124"),    # Ampere/Ada
]
DEFAULT_CHANNEL = "cu124"
INDEX = "https://download.pytorch.org/whl/{channel}"


def compute_caps() -> list:
    if not shutil.which("nvidia-smi"):
        return []
    for query in ("compute_cap", "compute_cap,name"):
        try:
            out = subprocess.run(
                ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=15, check=True).stdout
        except (subprocess.SubprocessError, OSError):
            continue
        caps = []
        for line in (l.strip() for l in out.splitlines() if l.strip()):
            m = re.match(r"^(\d+\.\d+)", line)
            if m:
                caps.append(float(m.group(1)))
        if caps:
            return caps
    return []


def installed_version(name: str):
    try:
        return md.version(name)
    except md.PackageNotFoundError:
        return None


def current_torch() -> tuple:
    try:
        import torch
    except ImportError:
        return (None, None)
    return (torch.__version__, torch.version.cuda)


def plan(caps: list, channel: str, version: str) -> tuple:
    cap = max(caps) if caps else None
    min_ver = None
    if cap is not None:
        for threshold, mv, ch in ARCH_RULES:
            if cap >= threshold:
                min_ver, auto_channel = mv, ch
                break
        else:
            auto_channel = DEFAULT_CHANNEL
    else:
        auto_channel = DEFAULT_CHANNEL
    return (channel or auto_channel, version, min_ver, cap)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--channel", help="cu124 / cu128 / cu130; по умолчанию по архитектуре GPU")
    p.add_argument("--torch-version", default="", help="например 2.7.1; пусто — последняя в канале")
    p.add_argument("--with-vision", action="store_true",
                   help="поставить torchvision, даже если его сейчас нет")
    p.add_argument("--with-xformers", action="store_true",
                   help="доставить xformers: без него LongCat падает, запасной ветки нет")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    caps = compute_caps()
    channel, version, min_ver, cap = plan(caps, a.channel, a.torch_version)
    have_ver, have_cuda = current_torch()

    print(f"GPU compute capability : {cap if cap is not None else 'не определена (нет nvidia-smi)'}")
    print(f"установлен torch       : {have_ver or 'нет'}"
          f"{'' if have_cuda is None else f' (CUDA {have_cuda})'}")
    if have_ver and have_cuda is None:
        print("  ВНИМАНИЕ: это CPU-сборка, CUDA в ней нет — прогон на GPU невозможен")
    if min_ver:
        print(f"минимальный torch      : {min_ver} (для sm_{int(cap*10)})")
    print(f"канал колёс            : {channel}")

    spec = f"torch=={version}" if version else "torch"
    # спутники обязаны быть из того же канала: torchvision, собранный под другой torch,
    # падает на импорте с "operator torchvision::nms does not exist"
    companions = [n for n in ("torchvision", "torchaudio") if installed_version(n)]
    if a.with_vision and "torchvision" not in companions:
        companions.append("torchvision")
    if companions:
        print(f"спутники из того же канала : {', '.join(companions)}")
    pkgs = [spec] + companions
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall",
           *pkgs, "--index-url", INDEX.format(channel=channel)]
    print("команда:", " ".join(cmd))
    if a.dry_run:
        print("dry-run: установка не выполняется")
        return 0

    rc = subprocess.run(cmd).returncode
    if rc != 0:
        # частый случай на больших колёсах: битая докачка и несовпадение sha256
        # ("THESE PACKAGES DO NOT MATCH THE HASHES") — повторяем мимо кеша
        print("pip не отработал; повторяю без кеша (битая загрузка — обычная причина)",
              file=sys.stderr)
        rc = subprocess.run(cmd + ["--no-cache-dir", "--retries", "5", "--timeout", "60"]).returncode
    if rc != 0:
        print(f"pip завершился с кодом {rc}", file=sys.stderr)
        return rc

    if a.with_xformers:
        # xformers тянет свою версию torch; из канала pytorch она совпадает с нашей,
        # а запасной вариант ставим с --no-deps, чтобы torch не подменился
        print("==> ставлю xformers")
        rc = subprocess.run([sys.executable, "-m", "pip", "install", "xformers",
                             "--index-url", INDEX.format(channel=channel)]).returncode
        if rc != 0:
            print("xformers из канала pytorch не встал; пробую PyPI без подмены torch",
                  file=sys.stderr)
            rc = subprocess.run([sys.executable, "-m", "pip", "install", "xformers",
                                 "--no-deps"]).returncode
        if rc != 0:
            print("xformers установить не удалось — без него прогон невозможен", file=sys.stderr)
            return rc

    print("готово: перезапустите проверку — python preflight.py --repo <dir>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
