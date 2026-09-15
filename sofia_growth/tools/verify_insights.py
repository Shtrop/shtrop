#!/usr/bin/env python3
"""Сверка выгрузки Insights с журналом реально опубликованного контента.

Отвечает на вопрос, который нельзя решить по имени папки: описывает ли файл
метрик реальные публикации Instagram или это симуляция.

Метод: собрать из журналов публикатора множество подтверждённых
`instagram_media_id` / `remote_post_id` и проверить, сколько media_id из
выгрузки в него попадает. Совпадение идентификаторов с реально
опубликованным контентом — сильное доказательство подлинности; отсутствие
совпадений — сильное доказательство обратного.

Только чтение. Ничего не публикует и не меняет.

Пример:
    python verify_insights.py --studio "D:\\AI_CONTENT\\Sofia"
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_insights import (  # noqa: E402
    classify_source, discover, is_post_record, read_source,
)

PROOF_COLUMNS = ("instagram_media_id", "remote_post_id", "remote_media_id", "ig_media_id")
NULLISH = ("", "none", "null", "n/a", "pending", "0")
# Доля совпавших идентификаторов, начиная с которой файл считается подлинным.
MATCH_THRESHOLD = 0.5


def published_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return ids
    try:
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view')")]
        for table in tables:
            try:
                columns = {c[1].lower(): c[1] for c in connection.execute(f'PRAGMA table_info("{table}")')}
            except sqlite3.Error:
                continue
            for proof in PROOF_COLUMNS:
                if proof not in columns:
                    continue
                try:
                    for (value,) in connection.execute(f'SELECT "{columns[proof]}" FROM "{table}"'):
                        if value is None:
                            continue
                        text = str(value).strip()
                        if text.lower() not in NULLISH:
                            ids.add(text)
                except sqlite3.Error:
                    continue
    finally:
        connection.close()
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, help="корень студии для автопоиска")
    parser.add_argument("--insights", type=Path, action="append", default=[],
                        help="файл метрик для проверки (CSV/JSONL)")
    parser.add_argument("--journal", type=Path, action="append", default=[],
                        help="база с журналом публикаций")
    args = parser.parse_args()

    insights = list(args.insights)
    journals = list(args.journal)
    if args.studio:
        for path in discover(args.studio):
            if path.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
                if path not in journals:
                    journals.append(path)
            elif path not in insights:
                insights.append(path)

    insights = [p for p in insights if p.exists()]
    journals = [p for p in journals if p.exists()]
    if not insights:
        print("BLOCKED: файлов метрик не найдено.")
        return 2
    if not journals:
        print("BLOCKED: журналов публикаций не найдено — сверять не с чем.")
        return 2

    confirmed: set[str] = set()
    print("Журналы публикаций:")
    for path in journals:
        found = published_ids(path)
        evidence, _ = classify_source(path)
        print(f"  [{evidence}] {path} — подтверждённых идентификаторов: {len(found)}")
        confirmed |= found
    print(f"\nВсего уникальных подтверждённых публикаций: {len(confirmed)}")
    if not confirmed:
        print("\nBLOCKED: подтверждённых публикаций нет — сверка невозможна.")
        return 2

    exit_code = 1
    print("\nСверка выгрузок метрик:")
    for path in insights:
        rows = [row for row in read_source(path) if is_post_record(row)]
        ids = [str(row["media_id"]) for row in rows if row.get("media_id")]
        matched = [value for value in ids if value in confirmed]
        evidence, markers = classify_source(path)
        share = len(matched) / len(ids) if ids else 0.0
        print(f"\n  {path}")
        print(f"    метка по пути: {evidence}"
              + (f" (маркеры: {', '.join(markers)})" if markers else ""))
        print(f"    строк с media_id: {len(ids)} | совпало с опубликованными: {len(matched)} "
              f"({round(share * 100, 1)}%)")
        if not ids:
            print("    ВЕРДИКТ: NOT_MEASURED — идентификаторов публикаций в файле нет")
        elif share >= MATCH_THRESHOLD:
            print(f"    ВЕРДИКТ: ID_MATCH_CONFIRMED — файл описывает реально опубликованный контент.")
            if evidence != "REAL":
                print(f"    Метка SHADOW поставлена по пути и опровергается фактом. Чтобы учесть")
                print(f"    файл как реальный, передать его в ingest явным доверием:")
                print(f'      --trust "{path}"')
            exit_code = 0
        else:
            print("    ВЕРДИКТ: NO_MATCH — идентификаторы не совпадают с опубликованным "
                  "контентом. Считать реальными метриками нельзя.")

    print("\nСверка по идентификаторам — доказательство подлинности, а не имя папки.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
