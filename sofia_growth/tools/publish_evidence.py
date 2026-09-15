#!/usr/bin/env python3
"""Проверка: были ли у Sofia реальные внешние публикации.

От этого зависит, могут ли вообще существовать настоящие метрики Instagram.
Скрипт читает журналы публикатора только на чтение и считает признаки
подтверждённой удалённой публикации: непустые `instagram_media_id`,
`remote_post_id`, `permalink`, `published_at`, а также израсходованные
canary-одобрения.

Ничего не публикует, не меняет состояние и не снимает HOLD.

Пример:
    python publish_evidence.py --source "D:\\AI_CONTENT\\Sofia\\...\\content_queue.db"
    python publish_evidence.py --studio "D:\\AI_CONTENT\\Sofia"
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _console import force_utf8  # noqa: E402
from ingest_insights import classify_source, discover  # noqa: E402

# Колонки, непустое значение в которых означает состоявшуюся удалённую публикацию.
REMOTE_PROOF = ("instagram_media_id", "remote_post_id", "remote_media_id", "ig_media_id")
# Косвенные признаки: сами по себе публикацию не доказывают.
SOFT_PROOF = ("permalink", "published_at", "instagram_container_id", "consumed_at")
NULLISH = ("", "none", "null", "n/a", "pending", "0")


def count_non_null(connection: sqlite3.Connection, table: str, column: str) -> int:
    try:
        rows = connection.execute(f'SELECT "{column}" FROM "{table}"').fetchall()
    except sqlite3.Error:
        return 0
    return sum(1 for (value,) in rows
               if value is not None and str(value).strip().lower() not in NULLISH)


def status_breakdown(connection: sqlite3.Connection, table: str, column: str) -> dict:
    try:
        rows = connection.execute(
            f'SELECT "{column}", COUNT(*) FROM "{table}" GROUP BY "{column}"').fetchall()
    except sqlite3.Error:
        return {}
    return {str(key): count for key, count in rows}


def inspect(path: Path) -> dict:
    evidence, markers = classify_source(path)
    result = {"path": str(path), "evidence_label": evidence, "markers": markers,
              "hard": 0, "soft": 0, "tables": []}
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        result["error"] = str(exc)
        return result
    try:
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view')")]
        for table in tables:
            try:
                columns = [c[1] for c in connection.execute(f'PRAGMA table_info("{table}")')]
                total = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            except sqlite3.Error:
                continue
            lower = {c.lower(): c for c in columns}
            hard = {name: count_non_null(connection, table, lower[name])
                    for name in REMOTE_PROOF if name in lower}
            soft = {name: count_non_null(connection, table, lower[name])
                    for name in SOFT_PROOF if name in lower}
            if not hard and not soft:
                continue
            entry = {"table": table, "rows": total, "hard": hard, "soft": soft}
            for status_column in ("status", "state"):
                if status_column in lower:
                    entry["statuses"] = status_breakdown(connection, table, lower[status_column])
                    break
            result["tables"].append(entry)
            result["hard"] += sum(hard.values())
            result["soft"] += sum(soft.values())
    finally:
        connection.close()
    return result


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
        print("BLOCKED: баз данных публикатора не найдено.")
        return 2

    total_hard = total_soft = 0
    real_hard = 0
    for path in sources:
        report = inspect(path)
        print(f"\n{report['path']}")
        print(f"  доказательность источника: {report['evidence_label']}"
              + (f" (маркеры: {', '.join(report['markers'])})" if report["markers"] else ""))
        if report.get("error"):
            print(f"  не читается: {report['error']}")
            continue
        if not report["tables"]:
            print("  признаков публикации нет ни в одной таблице")
        for entry in report["tables"]:
            print(f"  таблица `{entry['table']}` — строк: {entry['rows']}")
            for name, count in entry["hard"].items():
                print(f"      ПРЯМОЕ подтверждение `{name}`: непустых {count}")
            for name, count in entry["soft"].items():
                print(f"      косвенный признак `{name}`: непустых {count}")
            if entry.get("statuses"):
                shown = ", ".join(f"{k}={v}" for k, v in sorted(
                    entry["statuses"].items(), key=lambda item: -item[1])[:6])
                print(f"      статусы: {shown}")
        total_hard += report["hard"]
        total_soft += report["soft"]
        if report["evidence_label"] == "REAL":
            real_hard += report["hard"]

    print("\n" + "=" * 60)
    if total_hard == 0:
        verdict = "NOT_MEASURED"
        detail = ("Прямых подтверждений удалённой публикации нет. Реальных метрик "
                  "Instagram существовать не может — считать нечего.")
    elif real_hard == 0:
        verdict = "SHADOW"
        detail = (f"Подтверждений найдено {total_hard}, но все они в теневом/обучающем "
                  "контуре. Как доказательство реальных публикаций не засчитываются.")
    else:
        verdict = "REAL_PUBLISH_CONFIRMED"
        detail = (f"Подтверждений удалённой публикации в реальном контуре: {real_hard}. "
                  "Реальные Insights по ним могут существовать — искать выгрузку "
                  "или запросить через существующий collector.")
    print(f"PUBLISH EVIDENCE: {verdict}")
    print(f"  {detail}")
    print(f"  прямых признаков: {total_hard} | косвенных: {total_soft}")
    return 0 if verdict == "REAL_PUBLISH_CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
