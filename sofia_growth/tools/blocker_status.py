#!/usr/bin/env python3
"""Трекер состояния блокеров публикации: сдвинулись они или нет.

Цикл роста меряет метрики аккаунта, но рост упирается не в них, а в три
блокера. Этот скрипт считает их состояние по журналам и медиа, сохраняет
снимок и показывает изменение с прошлого раза — чтобы было видно, работает
ли починка, а не только «стало ли больше подписчиков».

Отслеживается:
  1. REELS      — сколько единиц типа reel/video есть и сколько опубликовано.
  2. ФОРМАТ     — файлы вне допустимого соотношения или ниже минимума ширины.
  3. EVIDENCE   — сколько доказательств не заполняется и сколько разжалований.
  плюс РЕЗЕРВ   — одобренное, но неопубликованное.

Только чтение. Ничего не публикует и не меняет состояние студии.

Пример:
    python blocker_status.py --studio "D:\\AI_CONTENT\\Sofia" \
        --media-dir "D:\\AI_CONTENT\\Sofia\\video_ready"
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _console import force_utf8  # noqa: E402
from ingest_insights import discover  # noqa: E402
from publish_doctor import (  # noqa: E402
    EVIDENCE_PATTERN, MIN_IMAGE_WIDTH, MIN_VIDEO_WIDTH, SERVICE_FILE_HINTS,
    image_size, nearest_ratio, video_size,
)
from publish_funnel import REELS_HINTS, TERMINAL_BAD, columns_of, pick  # noqa: E402

TYPE_COLUMNS = ("type", "media_type", "content_type")
STATUS_COLUMNS = ("status", "state")
ERROR_COLUMNS = ("error_message", "failure_reason", "detail")
MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".mp4", ".mov"}


def scan_journals(paths: list[Path]) -> dict:
    """Состояние очереди: типы, статусы, доказательства."""
    by_kind: dict[str, Counter] = {}
    evidence = Counter()
    demotions = 0
    caption_failures = 0

    for path in paths:
        try:
            connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        except sqlite3.Error:
            continue
        try:
            tables = [row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view')")]
            for table in tables:
                columns = columns_of(connection, table)
                status_column = pick(columns, STATUS_COLUMNS)
                type_column = pick(columns, TYPE_COLUMNS)
                error_column = pick(columns, ERROR_COLUMNS)

                if status_column and type_column:
                    try:
                        rows = connection.execute(
                            f'SELECT "{type_column}", "{status_column}" FROM "{table}"').fetchall()
                    except sqlite3.Error:
                        rows = []
                    for kind, status in rows:
                        bucket = by_kind.setdefault(str(kind or "UNKNOWN").lower(), Counter())
                        bucket[str(status or "UNKNOWN").lower()] += 1

                if error_column:
                    try:
                        rows = connection.execute(
                            f'SELECT "{error_column}" FROM "{table}"').fetchall()
                    except sqlite3.Error:
                        rows = []
                    for (value,) in rows:
                        if not value:
                            continue
                        text = str(value)
                        evidence.update(m.lower() for m in EVIDENCE_PATTERN.findall(text))
                        if "demoted to review" in text:
                            demotions += 1
                        if "no_caption_passed_guard" in text:
                            caption_failures += 1
        finally:
            connection.close()

    reels_total = reels_published = 0
    approved_unpublished = 0
    for kind, statuses in by_kind.items():
        published = sum(count for status, count in statuses.items() if "publish" in status)
        if any(hint in kind for hint in REELS_HINTS):
            reels_total += sum(statuses.values())
            reels_published += published
        approved_unpublished += sum(
            count for status, count in statuses.items()
            if "approve" in status and "publish" not in status)

    return {
        "reels_total": reels_total,
        "reels_published": reels_published,
        "approved_unpublished": approved_unpublished,
        "evidence_keys_missing": len(evidence),
        "evidence_missing_total": sum(evidence.values()),
        "caption_failures": caption_failures,
        "demotions": demotions,
        "by_kind": {kind: dict(statuses) for kind, statuses in sorted(by_kind.items())},
    }


def scan_media(media_dir: Path | None) -> dict:
    """Сколько публикуемых файлов не проходит по формату и разрешению."""
    if not media_dir or not media_dir.exists():
        return {"checked": None, "ratio_violations": None, "resolution_violations": None}

    checked = ratio_bad = resolution_bad = 0
    for path in media_dir.rglob("*"):
        if path.suffix.lower() not in MEDIA_SUFFIXES:
            continue
        if any(hint in path.name.lower() for hint in SERVICE_FILE_HINTS):
            continue
        is_video = path.suffix.lower() in (".mp4", ".mov")
        size = video_size(path) if is_video else image_size(path)
        if not size:
            continue
        checked += 1
        width, height = size
        if nearest_ratio(width, height)[2] > 0.01:
            ratio_bad += 1
        if width < (MIN_VIDEO_WIDTH if is_video else MIN_IMAGE_WIDTH):
            resolution_bad += 1
    return {"checked": checked, "ratio_violations": ratio_bad,
            "resolution_violations": resolution_bad}


def delta(current, previous) -> str:
    """Изменение с прошлого снимка, со знаком и направлением."""
    if current is None or previous is None:
        return ""
    change = current - previous
    if change == 0:
        return "  (без изменений)"
    return f"  ({change:+d})"


def verdict(current: dict) -> tuple[str, list[str]]:
    """Общий вердикт и что именно ещё держит рост."""
    open_blockers = []
    if current["reels_total"] and not current["reels_published"]:
        open_blockers.append(
            f"REELS: {current['reels_total']} в очереди, опубликовано 0 — "
            "нефолловерского охвата нет")
    if current.get("resolution_violations"):
        open_blockers.append(
            f"ФОРМАТ: {current['resolution_violations']} файлов ниже минимальной ширины")
    elif current.get("ratio_violations"):
        open_blockers.append(
            f"ФОРМАТ: {current['ratio_violations']} файлов вне допустимого соотношения")
    if current["evidence_keys_missing"] >= 5:
        open_blockers.append(
            f"EVIDENCE: {current['evidence_keys_missing']} ключей не заполняется, "
            f"{current['demotions']} разжалований одобренного")
    return ("BLOCKED" if open_blockers else "CLEAR"), open_blockers


def main() -> int:
    force_utf8()
    base = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, help="корень студии")
    parser.add_argument("--media-dir", type=Path, help="каталог с готовым медиа")
    parser.add_argument("--history", type=Path, default=base / "data" / "blocker_status.json")
    parser.add_argument("--no-write", action="store_true", help="не сохранять снимок")
    args = parser.parse_args()

    if not args.studio and not args.media_dir:
        parser.error("нужен --studio и/или --media-dir")

    journals = []
    if args.studio:
        journals = [p for p in discover(args.studio)
                    if p.suffix.lower() in (".db", ".sqlite", ".sqlite3")]
    if not journals and not args.media_dir:
        print("BLOCKED: журналов публикатора не найдено.")
        return 2

    current = scan_journals(journals) if journals else {
        "reels_total": 0, "reels_published": 0, "approved_unpublished": 0,
        "evidence_keys_missing": 0, "evidence_missing_total": 0,
        "caption_failures": 0, "demotions": 0, "by_kind": {}}
    current.update(scan_media(args.media_dir))
    current["measured_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    history = {"schema_version": "1.0", "snapshots": []}
    if args.history.exists():
        try:
            history = json.loads(args.history.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"WARN: {args.history} повреждён, история начата заново", file=sys.stderr)
    previous = history.get("snapshots", [])[-1] if history.get("snapshots") else None

    print("=== Состояние блокеров публикации ===\n")
    if previous:
        print(f"Сравнение с {previous['measured_at'][:16]}\n")
    else:
        print("Первый снимок: сравнивать пока не с чем.\n")

    rows = [
        ("Reels в очереди", "reels_total"),
        ("Reels опубликовано", "reels_published"),
        ("Одобрено, не опубликовано", "approved_unpublished"),
        ("Файлов проверено", "checked"),
        ("Вне соотношения", "ratio_violations"),
        ("Ниже минимума ширины", "resolution_violations"),
        ("Ключей evidence пустует", "evidence_keys_missing"),
        ("Отбраковок подписи", "caption_failures"),
        ("Разжалований одобренного", "demotions"),
    ]
    for label, key in rows:
        value = current.get(key)
        shown = "NOT_MEASURED" if value is None else str(value)
        change = delta(value, (previous or {}).get(key))
        print(f"  {label:<28} {shown:<14}{change}")

    if current.get("by_kind"):
        print("\n  По типу контента (всего / опубликовано):")
        for kind, statuses in current["by_kind"].items():
            total = sum(statuses.values())
            published = sum(count for status, count in statuses.items() if "publish" in status)
            blocked = sum(count for status, count in statuses.items()
                          if any(bad in status for bad in TERMINAL_BAD))
            print(f"    {kind:<14} {total:<5} / {published:<5}"
                  + (f"  отбраковано: {blocked}" if blocked else ""))

    state, open_blockers = verdict(current)
    print(f"\n  ВЕРДИКТ: {state}")
    for item in open_blockers:
        print(f"    • {item}")
    if state == "CLEAR":
        print("    Блокеры, которые видны по данным, закрыты.")

    if not args.no_write:
        history.setdefault("snapshots", []).append(current)
        history["snapshots"] = history["snapshots"][-24:]  # история не растёт бесконечно
        args.history.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.history.with_suffix(args.history.suffix + ".tmp")
        tmp.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(args.history)
        print(f"\n  Снимок сохранён: {args.history}")

    return 0 if state == "CLEAR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
