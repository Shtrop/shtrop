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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_insights import (  # noqa: E402
    ID_MATCH_THRESHOLD as MATCH_THRESHOLD,
    classify_source, discover, is_post_record, published_ids, read_source,
)


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
    strict: set[str] = set()
    print("Журналы публикаций:")
    for path in journals:
        found = published_ids(path)
        evidence, _ = classify_source(path)
        print(f"  [{evidence}] {path} — подтверждённых идентификаторов: {len(found)}")
        confirmed |= found
        if evidence == "REAL":
            strict |= found
    print(f"\nВсего уникальных подтверждённых публикаций: {len(confirmed)}")
    print(f"Из них в журналах без теневых маркеров (строгий анкер): {len(strict)}")
    if not confirmed:
        print("\nBLOCKED: подтверждённых публикаций нет — сверка невозможна.")
        return 2

    exit_code = 1
    print("\nСверка выгрузок метрик:")
    for path in insights:
        rows = [row for row in read_source(path) if is_post_record(row)]
        ids = [str(row["media_id"]) for row in rows if row.get("media_id")]
        evidence, markers = classify_source(path)
        matched = [value for value in ids if value in confirmed]
        matched_strict = [value for value in ids if value in strict]
        share = len(matched) / len(ids) if ids else 0.0
        share_strict = len(matched_strict) / len(ids) if ids else 0.0
        print(f"\n  {path}")
        print(f"    метка по пути: {evidence}"
              + (f" (маркеры: {', '.join(markers)})" if markers else ""))
        print(f"    строк с media_id: {len(ids)}")
        print(f"    совпало со всеми журналами: {len(matched)} ({round(share * 100, 1)}%)")
        print(f"    совпало со строгим анкером: {len(matched_strict)} "
              f"({round(share_strict * 100, 1)}%)")
        if not ids:
            print("    ВЕРДИКТ: NOT_MEASURED — идентификаторов публикаций в файле нет")
        elif share_strict >= MATCH_THRESHOLD:
            print("    ВЕРДИКТ: ID_MATCH_CONFIRMED — файл описывает реально опубликованный контент.")
            print("    Движок признает его реальным автоматически, без ручных флагов.")
            exit_code = 0
        elif share >= MATCH_THRESHOLD:
            print("    ВЕРДИКТ: ID_MATCH_CONFIRMED по нестрогому анкеру.")
            print("    Совпадения подтверждаются журналом, лежащим в теневом каталоге, поэтому")
            print("    автоматически файл реальным НЕ станет. Если вы подтверждаете, что журнал")
            print("    содержит настоящие публикации, добавьте к запуску цикла:")
            print(f'      --trust "{path}"')
            exit_code = 0
        else:
            print("    ВЕРДИКТ: NO_MATCH — идентификаторы не совпадают с опубликованным "
                  "контентом. Считать реальными метриками нельзя.")

    print("\nСверка по идентификаторам — доказательство подлинности, а не имя папки.")
    print("Неполное совпадение — норма, если журнал снят раньше выгрузки метрик:")
    print("публикации, сделанные после снимка журнала, в нём просто отсутствуют.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
