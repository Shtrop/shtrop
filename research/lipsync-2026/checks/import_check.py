#!/usr/bin/env python3
"""Эмулирует хост без triton / flash-attn (типичный Windows) и проверяет,
что LongCat-Video всё равно импортируется.

Блокировка ставится на builtins.__import__ и срабатывает только для файлов
самого LongCat-Video: сторонние библиотеки (torch, transformers) продолжают
пользоваться реально установленными пакетами, поэтому проверка изолирует
именно зависимость кода репозитория, а не всего окружения.

usage: import_check.py [путь_к_клону_LongCat-Video]
"""
import builtins, importlib, os, sys

BLOCKED = {"triton", "flash_attn", "flash_attn_interface"}
REPO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "LongCat-Video")
_real_import = builtins.__import__


def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] in BLOCKED:
        caller = (globals or {}).get("__file__", "")
        if caller and os.path.abspath(caller).startswith(REPO):
            raise ModuleNotFoundError(
                f"No module named '{name}' (эмуляция окружения без него)")
    return _real_import(name, globals, locals, fromlist, level)


builtins.__import__ = guarded_import
sys.path.insert(0, REPO)

rc = 0
for t in ("longcat_video.modules.attention",
          "longcat_video.modules.avatar.attention",
          "longcat_video.modules.avatar.longcat_video_dit_avatar"):
    try:
        importlib.import_module(t)
        print(f"OK   {t}")
    except Exception as e:
        print(f"FAIL {t}: {type(e).__name__}: {e}")
        rc = 1
sys.exit(rc)
