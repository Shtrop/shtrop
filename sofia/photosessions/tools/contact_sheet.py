#!/usr/bin/env python3
"""Контактный лист по отрисованным кадрам: один HTML со всеми превью.

  python tools\\contact_sheet.py "%USERPROFILE%\\Desktop\\Фотосессия"

Собирает index.html в корне каталога: кадры сгруппированы по сессиям, под каждым
подпись с id, seed и размером файла. Открывается двойным кликом, работает без сети.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

CSS = """
:root{--bg:#101211;--card:#181b19;--line:#272c29;--ink:#e8ece8;--dim:#9aa39b;--acc:#54cfa0}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
     font:14px/1.5 "Segoe UI",system-ui,sans-serif;padding:24px}
h1{font-size:24px;margin:0 0 4px}
.sub{color:var(--dim);margin-bottom:24px}
h2{font-size:17px;margin:32px 0 4px;padding-top:14px;border-top:1px solid var(--line)}
.meta{color:var(--dim);font-size:12px;margin-bottom:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:6px;overflow:hidden}
img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;background:#000}
figcaption{padding:7px 9px;font-size:11px;color:var(--dim);
           font-family:Consolas,ui-monospace,monospace;word-break:break-all}
figcaption b{color:var(--ink);font-weight:600}
a{color:var(--acc)}
.empty{color:var(--dim);padding:20px;border:1px dashed var(--line);border-radius:6px}
"""


def human(size: int) -> str:
    return f"{size/1024:.0f} КБ" if size < 1024 * 1024 else f"{size/1048576:.1f} МБ"


def main() -> int:
    ap = argparse.ArgumentParser(description="Контактный лист по отрисованным кадрам")
    ap.add_argument("root", type=Path, help="каталог с папками сессий")
    ap.add_argument("--out", type=Path, help="куда сохранить index.html (по умолчанию в корень)")
    args = ap.parse_args()

    root: Path = args.root
    if not root.is_dir():
        print(f"Нет такого каталога: {root}")
        return 2
    out = args.out or (root / "index.html")

    sessions = []
    total = 0
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        images = sorted(folder.glob("*.png"))
        if not images:
            continue
        total += len(images)
        sessions.append((folder, images))

    parts = [f"<style>{CSS}</style>",
             "<h1>Фотосессии Sofia</h1>",
             f'<p class="sub">{len(sessions)} сессий · {total} кадров · {html.escape(str(root))}</p>']

    if not sessions:
        parts.append('<p class="empty">Кадров пока нет. Запустите прогон и соберите лист заново.</p>')

    for folder, images in sessions:
        manifest = folder / "run_manifest.json"
        note = ""
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                note = (f" · сгенерировано {len(data.get('generated', []))}"
                        f" · сбоев {len(data.get('failed', []))}")
            except Exception:
                note = ""
        parts.append(f"<h2>{html.escape(folder.name)}</h2>")
        parts.append(f'<p class="meta">{len(images)} кадров{html.escape(note)}</p>')
        parts.append('<div class="grid">')
        for img in images:
            rel = html.escape(f"{folder.name}/{img.name}")
            stem = img.stem
            shot = stem.split("_")[0]
            seed = next((s[4:] for s in stem.split("_") if s.startswith("seed")), "")
            parts.append(
                f'<figure><a href="{rel}" target="_blank"><img src="{rel}" loading="lazy" '
                f'alt="{html.escape(shot)}"></a>'
                f'<figcaption><b>{html.escape(shot)}</b> · seed {html.escape(seed)} · '
                f'{human(img.stat().st_size)}</figcaption></figure>')
        parts.append("</div>")

    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Контактный лист: {out}")
    print(f"Сессий {len(sessions)}, кадров {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
