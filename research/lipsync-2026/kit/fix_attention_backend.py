#!/usr/bin/env python3
"""Приводит выбор attention-бэкенда в конфигах весов LongCat к тому, что реально
установлено в окружении.

В репозитории FlashAttention-2 включён в конфиге DiT по умолчанию, и на хосте без
flash-attn прогон падает внутри forward, хотя импорт проходит. Скрипт находит
config.json моделей, смотрит, какие бэкенды импортируются, и переключает флаги.
Если не установлено ничего, все флаги ставятся в False — это SDPA-ветка, которую
добавляет kit/longcat-compat.patch. Старый файл сохраняется рядом как
.bak-<timestamp>, запись атомарная.

    python fix_attention_backend.py ./weights/LongCat-Video-Avatar-1.5
    python fix_attention_backend.py ./weights/... --dry-run
"""
import argparse, importlib.util, json, os, shutil, subprocess, sys, tempfile, time

FLAGS = ("enable_flashattn3", "enable_flashattn2", "enable_xformers")


def have(mod: str) -> bool:
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ValueError):
        return False


def usable(mod: str) -> bool:
    """Модуль не просто найден, а импортируется. find_spec врёт про xformers,
    собранный под другую версию torch: файл на месте, импорт падает по ABI."""
    if not have(mod):
        return False
    try:
        return subprocess.run([sys.executable, "-c", f"import {mod}"],
                              capture_output=True, timeout=120).returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def pick_backend() -> str:
    """Лучший доступный: fa3 -> fa2 -> xformers. Пусто — значит SDPA-ветка из патча
    (в апстриме на её месте raise RuntimeError('Unsupported attention operations.'))."""
    if usable("flash_attn_interface"):
        return "enable_flashattn3"
    if usable("flash_attn"):
        return "enable_flashattn2"
    if usable("xformers"):
        return "enable_xformers"
    return ""


def find_configs(root: str) -> list:
    out = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if "config.json" in filenames:
            p = os.path.join(dirpath, "config.json")
            try:
                with open(p, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(cfg, dict) and any(k in cfg for k in FLAGS):
                out.append((p, cfg))
    return out


def write_atomic(path: str, cfg: dict) -> None:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = f"{path}.bak-{stamp}"
    n = 1
    while os.path.exists(backup):                  # не затираем существующий бэкап
        backup = f"{path}.bak-{stamp}-{n}"
        n += 1
    shutil.copy2(path, backup)                     # ничего не удаляем, только копия
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    print(f"    бэкап: {os.path.basename(backup)}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("weights_dir", nargs="?", default="./weights/LongCat-Video-Avatar-1.5")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--backend", choices=FLAGS, help="выбрать бэкенд вручную")
    a = p.parse_args()

    root = os.path.abspath(a.weights_dir)
    if not os.path.isdir(root):
        print(f"ОШИБКА: каталог весов не найден: {root}", file=sys.stderr)
        return 2

    backend = a.backend or pick_backend()
    installed = [m for m in ("flash_attn_interface", "flash_attn", "xformers") if usable(m)]
    print(f"установлено: {', '.join(installed) if installed else 'ничего из fa3/fa2/xformers'}")
    if not backend:
        print("выбран бэкенд: SDPA-ветка из longcat-compat.patch (все флаги в False)")
        print("  без патча апстрим кидает RuntimeError('Unsupported attention operations.') — "
              "проверьте, что патч наложен")
    else:
        print(f"выбран бэкенд: {backend}")

    configs = find_configs(root)
    if not configs:
        print(f"config.json с флагами attention в {root} не найден — "
              f"проверьте, что веса скачаны полностью", file=sys.stderr)
        return 1

    changed = 0
    for path, cfg in configs:
        desired = {f: (f == backend) for f in FLAGS if f in cfg}
        current = {f: bool(cfg.get(f)) for f in desired}
        rel = os.path.relpath(path, root)
        if current == desired:
            print(f"OK   {rel}: {current}")
            continue
        print(f"ПРАВКА {rel}: {current} -> {desired}")
        if a.dry_run:
            continue
        cfg.update(desired)
        write_atomic(path, cfg)
        changed += 1

    if a.dry_run:
        print("dry-run: файлы не изменены")
    else:
        print(f"изменено файлов: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
