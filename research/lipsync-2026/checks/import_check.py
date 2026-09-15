#!/usr/bin/env python3
"""Эмулирует хост без triton / flash-attn (типичный Windows) и проверяет,
что LongCat-Video всё равно импортируется.

Блокировка ставится на builtins.__import__ и срабатывает только для файлов
самого LongCat-Video: сторонние библиотеки (torch, transformers) продолжают
пользоваться реально установленными пакетами, поэтому проверка изолирует
именно зависимость кода репозитория, а не всего окружения.

Коды возврата:
    0 — импорт проходит;
    1 — упирается именно в triton/flash-attn (патч не наложен);
    3 — не установлены обычные зависимости (einops, numpy и т.п.) — проверку
        нужно повторить после pip install, блокером это не считается.

usage: import_check.py [путь_к_клону_LongCat-Video]
"""
import builtins, importlib, os, sys

PATCH_BLOCKERS = {"triton", "flash_attn", "flash_attn_interface"}   # что чинит патч
# для самопроверки чекера: IMPORT_CHECK_BLOCK_EXTRA=einops имитирует отсутствие пакета
BLOCKED = PATCH_BLOCKERS | {m for m in os.environ.get("IMPORT_CHECK_BLOCK_EXTRA", "").split(",") if m}
REPO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "LongCat-Video")
_real_import = builtins.__import__


def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] in BLOCKED:
        caller = (globals or {}).get("__file__", "")
        if caller and os.path.abspath(caller).startswith(REPO):
            raise ModuleNotFoundError(
                f"No module named '{name}' (эмуляция окружения без него)", name=name)
    return _real_import(name, globals, locals, fromlist, level)


builtins.__import__ = guarded_import
sys.path.insert(0, REPO)

rc, missing_deps = 0, set()
for t in ("longcat_video.modules.attention",
          "longcat_video.modules.avatar.attention",
          "longcat_video.modules.avatar.longcat_video_dit_avatar"):
    try:
        importlib.import_module(t)
        print(f"OK   {t}")
    except ModuleNotFoundError as e:
        root = (e.name or "").split(".")[0]
        if root in PATCH_BLOCKERS:
            print(f"FAIL {t}: нет '{root}' — патч не наложен или снят")
            rc = 1
        else:
            print(f"SKIP {t}: не установлена зависимость '{root}'")
            missing_deps.add(root)
            rc = max(rc, 3)
    except Exception as e:
        print(f"FAIL {t}: {type(e).__name__}: {e}")
        rc = 1

if missing_deps and rc == 3:
    print("зависимости не установлены: " + ", ".join(sorted(missing_deps)))
    print("это не блокер патча — повторите проверку после установки requirements")
sys.exit(rc)
