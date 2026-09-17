#!/usr/bin/env python3
"""Осмотр источников: какие поля в них есть и какие движок распознаёт.

Только чтение: печатает структуру и не меняет ни одного файла. Нужен, когда
источник найден, но строк из него извлечено мало или ноль — так видно, какие
колонки/таблицы не попали в словарь алиасов.

Пример:
    python inspect_sources.py --studio "D:\\AI_CONTENT\\Sofia"
    python inspect_sources.py --source "D:\\...\\content_queue.db"
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _console import force_utf8  # noqa: E402
from ingest_insights import (  # noqa: E402
    ACCOUNT_FIELDS, POST_FIELDS, classify_source, discover, expand_insights,
    normalize_key, read_csv_rows,
)

KNOWN = set(ACCOUNT_FIELDS + POST_FIELDS)


def show_columns(columns: list[str], indent: str = "      ") -> None:
    recognised, unknown = [], []
    for column in columns:
        canon = normalize_key(column)
        (recognised if canon else unknown).append(f"{column} → {canon}" if canon else column)
    print(f"{indent}распознано ({len(recognised)}): {', '.join(recognised) or '—'}")
    print(f"{indent}НЕ распознано ({len(unknown)}): {', '.join(unknown) or '—'}")


def inspect_sqlite(path: Path) -> None:
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        print(f"    не открывается: {exc}")
        return
    try:
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view')")]
        if not tables:
            print("    таблиц нет")
            return
        for table in tables:
            try:
                columns = [c[1] for c in connection.execute(f'PRAGMA table_info("{table}")')]
                count = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            except sqlite3.Error as exc:
                print(f"    {table}: не читается ({exc})")
                continue
            canon = {normalize_key(c) for c in columns} - {None}
            has_date = "date" in canon
            metrics = canon & KNOWN
            lineage = canon & {"media_id", "permalink"}
            if has_date and metrics:
                verdict = "ИСПОЛЬЗУЕТСЯ: метрики"
            elif has_date and lineage:
                verdict = "ИСПОЛЬЗУЕТСЯ: lineage публикаций"
            elif not has_date:
                verdict = "пропускается: нет колонки с датой"
            else:
                verdict = "пропускается: нет ни метрик, ни идентификатора публикации"
            print(f"    таблица `{table}` — строк: {count} — {verdict}")
            show_columns(columns)
    finally:
        connection.close()


def inspect_csv(path: Path) -> None:
    rows = read_csv_rows(path)
    print(f"    строк: {len(rows)}")
    if rows:
        show_columns(list(rows[0]))


def inspect_jsonl(path: Path) -> None:
    keys, count = set(), 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            count += 1
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                for record in expand_insights(payload):
                    keys.update(record)
            if count >= 200:
                break
    print(f"    строк просмотрено: {count}")
    show_columns(sorted(keys))


def main() -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, help="корень студии для автопоиска")
    parser.add_argument("--source", type=Path, action="append", default=[])
    args = parser.parse_args()

    sources = list(args.source)
    if args.studio:
        sources += [p for p in discover(args.studio) if p not in sources]
    sources = [p for p in sources if p.exists()]
    if not sources:
        print("BLOCKED: источников не найдено.")
        return 2

    for path in sources:
        evidence, hits = classify_source(path)
        print(f"\n{path}")
        print(f"  доказательность: {evidence}" + (f" (маркеры: {', '.join(hits)})" if hits else ""))
        suffix = path.suffix.lower()
        if suffix in (".db", ".sqlite", ".sqlite3"):
            inspect_sqlite(path)
        elif suffix in (".csv", ".tsv"):
            inspect_csv(path)
        elif suffix in (".jsonl", ".ndjson"):
            inspect_jsonl(path)
        else:
            print("    формат не осматривается")
    print("\nНераспознанные колонки добавляются в ALIASES в tools/ingest_insights.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
