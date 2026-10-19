#!/usr/bin/env python3
"""Генерация СИНТЕТИЧЕСКИХ источников Insights для проверки Growth Engine.

Эти данные выдуманы и существуют только для проверки механики цикла.
Они НИКОГДА не попадают в репозиторий и не являются метриками Sofia:
файлы пишутся во временный каталог, переданный аргументом.

Имена колонок намеренно взяты «как в жизни» (Graph API и типовые экспорты),
чтобы проверить сопоставление алиасов в ingest_insights.py.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

MARKER = "SYNTHETIC_FIXTURE_NOT_REAL_SOFIA_DATA"

# Формат → (sends/reach, follows на публикацию). Один сильный, один слабый:
# так проверяется, что память умеет и повышать, и понижать приоритет.
FORMATS = {
    "fmt-flop-core": (0.038, 22),      # ожидаемый вердикт SCALE
    "fmt-this-or-that": (0.004, 4),    # ожидаемый вердикт DROP
    "fmt-raw-single-take": (0.014, 12),  # ожидаемый вердикт KEEP
}


def build(target: Path) -> dict:
    target.mkdir(parents=True, exist_ok=True)
    start = dt.date.today() - dt.timedelta(days=29)
    (target / "README_FIXTURES.txt").write_text(
        f"{MARKER}\nВыдуманные данные для E2E-проверки. Не использовать как метрики.\n",
        encoding="utf-8")

    posts, day_rows = [], []
    followers = 1180
    for offset in range(30):
        day = start + dt.timedelta(days=offset)
        reach_day = 0
        if offset % 2 == 0:  # публикация через день
            format_id = list(FORMATS)[(offset // 2) % len(FORMATS)]
            sends_rate, follows = FORMATS[format_id]
            reach = 3100 + offset * 40
            reach_day = reach
            posts.append({
                "published_at": day.isoformat(),
                "media_id": f"SYNTH_{offset:03d}",
                "permalink": f"https://example.invalid/{MARKER.lower()}/{offset:03d}",
                "media_type": "REELS",
                "format": format_id,
                "trend_id": format_id,
                "reach": reach,
                "shares_dm": round(reach * sends_rate),
                "saved": round(reach * 0.012),
                "like_count": round(reach * 0.05),
                "comments_count": round(reach * 0.004),
                "follows": follows,
                "profile_views": follows * 7,
                "ig_reels_avg_watch_time": 8.4,
                # Намеренно отсутствует retention: проверка, что NOT_MEASURED сохраняется.
            })
            followers += follows - 3
        day_rows.append({"day": day.isoformat(), "follower_count": followers,
                         "reach": reach_day, "profile_views": 0})

    # 1. post_insights.csv — построчные метрики публикаций.
    csv_path = target / "post_insights.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(posts[0]))
        writer.writeheader()
        writer.writerows(posts)

    # 2. ig_insights.jsonl — account-level во вложенном виде Graph API.
    jsonl_path = target / "ig_insights.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in day_rows:
            handle.write(json.dumps({
                "object": "instagram_account",
                "data": [
                    {"name": "follower_count", "period": "day",
                     "values": [{"value": row["follower_count"], "end_time": row["day"]}]},
                ],
                "day": row["day"],
            }, ensure_ascii=False) + "\n")

    # 3. content_queue.db — lineage публикаций.
    db_path = target / "content_queue.db"
    if db_path.exists():
        db_path.unlink()
    connection = sqlite3.connect(db_path)
    connection.execute(
        "CREATE TABLE publication_lineage (date TEXT, media_id TEXT, format_id TEXT, "
        "trend_id TEXT, reach INTEGER, sends INTEGER, saves INTEGER)")
    connection.executemany(
        "INSERT INTO publication_lineage VALUES (?,?,?,?,?,?,?)",
        [(p["published_at"], p["media_id"], p["format"], p["trend_id"],
          p["reach"], p["shares_dm"], p["saved"]) for p in posts])
    # Таблица без метрик — проверка, что она игнорируется, а не угадывается.
    connection.execute("CREATE TABLE queue_settings (key TEXT, value TEXT)")
    connection.execute("INSERT INTO queue_settings VALUES ('marker', ?)", (MARKER,))
    connection.commit()
    connection.close()

    return {"dir": target, "posts": len(posts), "days": len(day_rows),
            "files": [csv_path, jsonl_path, db_path]}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: make_fixtures.py <target_dir>")
    info = build(Path(sys.argv[1]))
    print(f"{MARKER}: публикаций {info['posts']}, дней {info['days']}, каталог {info['dir']}")
