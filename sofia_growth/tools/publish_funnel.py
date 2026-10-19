#!/usr/bin/env python3
"""Разбор воронки публикаций: где контент умирает и почему нет Reels.

Читает журналы публикатора только на чтение и отвечает на вопросы:
  * сколько единиц контента дошло до каждой стадии;
  * на какой стадии застревает каждый тип контента;
  * какие ошибки и блокировки повторяются;
  * когда была последняя успешная публикация каждого типа.

Ничего не публикует, не меняет состояние, не снимает HOLD.

Пример:
    python publish_funnel.py --studio "D:\\AI_CONTENT\\Sofia"
"""

from __future__ import annotations

import argparse
import datetime as dt
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _console import force_utf8  # noqa: E402
from ingest_insights import classify_source, discover  # noqa: E402

# Стадии в порядке продвижения: ключ — фрагмент статуса, значение — позиция.
FUNNEL_ORDER = (
    ("created", "создано"), ("queued", "в очереди"), ("render", "рендер"),
    ("review", "на ревью"), ("approve", "одобрено"), ("publish", "опубликовано"),
)
TERMINAL_BAD = ("reject", "fail", "block", "error", "cancel", "expired", "missing")

TYPE_COLUMNS = ("type", "media_type", "media_product_type", "content_type")
STATUS_COLUMNS = ("status", "state")
ERROR_COLUMNS = ("error_message", "failure_reason", "error", "detail")
DATE_COLUMNS = ("published_at", "created_at", "finished_at", "claimed_at", "updated_at")
REELS_HINTS = ("reel", "video", "clip")


def columns_of(connection: sqlite3.Connection, table: str) -> dict:
    try:
        return {c[1].lower(): c[1] for c in connection.execute(f'PRAGMA table_info("{table}")')}
    except sqlite3.Error:
        return {}


def pick(columns: dict, candidates: tuple) -> str | None:
    for name in candidates:
        if name in columns:
            return columns[name]
    return None


def is_reels(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in REELS_HINTS)


def stage_of(status: str) -> str:
    lowered = status.lower()
    for fragment in TERMINAL_BAD:
        if fragment in lowered:
            return f"ОТБРАКОВКА ({status})"
    for fragment, label in FUNNEL_ORDER:
        if fragment in lowered:
            return label
    return f"прочее ({status})"


def analyse_table(connection: sqlite3.Connection, table: str) -> dict | None:
    columns = columns_of(connection, table)
    status_column = pick(columns, STATUS_COLUMNS)
    if not status_column:
        return None
    type_column = pick(columns, TYPE_COLUMNS)
    error_column = pick(columns, ERROR_COLUMNS)
    date_column = pick(columns, DATE_COLUMNS)

    select = [f'"{status_column}" AS status']
    select.append(f'"{type_column}" AS kind' if type_column else "NULL AS kind")
    select.append(f'"{error_column}" AS error' if error_column else "NULL AS error")
    select.append(f'"{date_column}" AS moment' if date_column else "NULL AS moment")
    try:
        rows = connection.execute(f'SELECT {", ".join(select)} FROM "{table}"').fetchall()
    except sqlite3.Error:
        return None
    if not rows:
        return None

    by_status = Counter()
    by_kind_status = defaultdict(Counter)
    errors = Counter()
    last_success = {}
    for status, kind, error, moment in rows:
        status = str(status or "UNKNOWN")
        kind = str(kind or "UNKNOWN")
        by_status[status] += 1
        by_kind_status[kind][status] += 1
        if error and str(error).strip():
            errors[str(error).strip()[:160]] += 1
        if "publish" in status.lower() and moment:
            current = last_success.get(kind)
            moment = str(moment)
            if current is None or moment > current:
                last_success[kind] = moment
    return {"table": table, "rows": len(rows), "by_status": by_status,
            "by_kind_status": by_kind_status, "errors": errors,
            "last_success": last_success, "has_type": bool(type_column)}


def print_report(path: Path, reports: list[dict]) -> dict:
    evidence, markers = classify_source(path)
    print(f"\n{path}")
    print(f"  доказательность: {evidence}"
          + (f" (маркеры: {', '.join(markers)})" if markers else ""))

    summary = {"reels_published": 0, "reels_total": 0, "reels_blocked": Counter(),
               "approved_unpublished": Counter()}
    for report in reports:
        print(f"\n  таблица `{report['table']}` — записей: {report['rows']}")
        print("    стадия / статус:")
        for status, count in report["by_status"].most_common():
            print(f"      {stage_of(status):<28} {status:<28} {count}")

        if report["has_type"]:
            print("    по типу контента:")
            for kind, statuses in sorted(report["by_kind_status"].items(),
                                         key=lambda item: -sum(item[1].values())):
                total = sum(statuses.values())
                published = sum(count for status, count in statuses.items()
                                if "publish" in status.lower())
                breakdown = ", ".join(f"{status}={count}"
                                      for status, count in statuses.most_common(6))
                print(f"      {kind:<16} всего {total:<5} опубликовано {published:<5} | {breakdown}")
                for status, count in statuses.items():
                    # Одобренное, но неопубликованное — уже прошло гейты качества:
                    # самая дешёвая правка во всей воронке.
                    if "approve" in status.lower() and "publish" not in status.lower():
                        summary["approved_unpublished"][kind] += count
                if is_reels(kind):
                    summary["reels_total"] += total
                    summary["reels_published"] += published
                    for status, count in statuses.items():
                        if any(bad in status.lower() for bad in TERMINAL_BAD) \
                                or "publish" not in status.lower():
                            summary["reels_blocked"][status] += count

        if report["errors"]:
            print("    частые ошибки и причины:")
            for message, count in report["errors"].most_common(5):
                print(f"      ×{count}  {message}")
        if report["last_success"]:
            print("    последняя успешная публикация по типу:")
            for kind, moment in sorted(report["last_success"].items()):
                print(f"      {kind:<16} {moment}")
    return summary


def main() -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, help="корень студии для автопоиска")
    parser.add_argument("--source", type=Path, action="append", default=[])
    args = parser.parse_args()

    sources = list(args.source)
    if args.studio:
        sources += [p for p in discover(args.studio)
                    if p.suffix.lower() in (".db", ".sqlite", ".sqlite3") and p not in sources]
    sources = [p for p in sources if p.exists()]
    if not sources:
        print("BLOCKED: журналов публикатора не найдено.")
        return 2

    totals = {"reels_published": 0, "reels_total": 0, "reels_blocked": Counter(),
              "approved_unpublished": Counter()}
    for path in sources:
        try:
            connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        except sqlite3.Error as exc:
            print(f"\n{path}\n  не открывается: {exc}")
            continue
        try:
            tables = [row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view')")]
            reports = [r for r in (analyse_table(connection, table) for table in tables) if r]
        finally:
            connection.close()
        if not reports:
            print(f"\n{path}\n  таблиц со статусами не найдено")
            continue
        summary = print_report(path, reports)
        totals["reels_published"] += summary["reels_published"]
        totals["reels_total"] += summary["reels_total"]
        totals["reels_blocked"] += summary["reels_blocked"]
        totals["approved_unpublished"] += summary["approved_unpublished"]

    print("\n" + "=" * 60)
    if totals["approved_unpublished"]:
        total_ready = sum(totals["approved_unpublished"].values())
        print(f"ГОТОВО, НО НЕ ОПУБЛИКОВАНО: {total_ready} единиц прошли гейты качества "
              "и остановились перед публикацией.")
        for kind, count in totals["approved_unpublished"].most_common():
            print(f"    {kind:<16} {count}")
        print("  Это самый дешёвый резерв охвата: контент уже сделан и одобрен.")
        print("  Публикация требует отдельного решения владельца и прохождения publish gate.")
        print()

    if totals["reels_total"] == 0:
        print("REELS: NOT_MEASURED — единиц контента типа Reels/видео в журналах нет.")
        print("  Видео не доходит даже до очереди публикации: искать причину в")
        print("  video-контуре и quality gate, а не в публикаторе.")
        return 1
    print(f"REELS: всего {totals['reels_total']}, опубликовано {totals['reels_published']}")
    if totals["reels_published"] == 0:
        print("  Ни один Reel не опубликован. Где застревает:")
        for status, count in totals["reels_blocked"].most_common(8):
            print(f"    {status:<32} {count}")
        print("  Это и есть блокер нефолловерского охвата.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
