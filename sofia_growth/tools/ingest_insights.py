#!/usr/bin/env python3
"""Сбор реальных Instagram Insights Sofia в единый снимок для Growth Engine.

Читает существующие локальные источники студии и складывает их в
`data/followers_snapshots.json`. Второй analytics pipeline не создаётся:
скрипт только читает то, что уже выгрузил канонический collector.

Поддерживаемые источники:
  * `post_insights.csv`      — построчные метрики публикаций
  * `ig_insights.jsonl`      — account/media insights, один JSON на строку
  * `content_queue.db` и любые SQLite с analytics/insights-таблицами
  * любой CSV/JSONL, переданный через --source

Жёсткие правила:
  * ничего не выдумывать: отсутствующее поле НЕ пишется и НЕ становится 0;
  * ничего не удалять: запись только в --out через temp → atomic replace;
  * никаких сетевых вызовов, токенов и публикаций.

Пример:
    python ingest_insights.py --studio "D:\\AI_CONTENT\\Sofia" \
        --out sofia_growth/data/followers_snapshots.json
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

# Канонические поля снимка аккаунта.
ACCOUNT_FIELDS = (
    "followers", "reach", "follows", "profile_visits", "sends", "saves",
    "views", "watch_time", "average_watch_time", "retention", "shares",
    "comments", "likes", "reel_plays", "profile_activity", "unfollows",
    "follower_conversion", "impressions", "posted_reels",
)

# Канонические поля публикации.
POST_FIELDS = (
    "reach", "views", "impressions", "sends", "saves", "likes", "comments",
    "shares", "follows", "profile_visits", "watch_time", "average_watch_time",
    "retention", "reel_plays",
)

# Как реальные выгрузки называют те же метрики. Ключ — канон, значения — алиасы.
# Имена взяты из Graph API Insights и типовых экспортов; список расширяемый.
ALIASES: dict[str, tuple[str, ...]] = {
    "date": ("date", "day", "timestamp", "end_time", "created_at", "published_at", "snapshot_date"),
    "followers": ("followers", "follower_count", "followers_count", "total_followers"),
    "reach": ("reach", "accounts_reached", "unique_accounts_reached"),
    "impressions": ("impressions", "total_impressions"),
    "follows": ("follows", "new_followers", "follows_gained", "accounts_followed", "follower_gains"),
    "unfollows": ("unfollows", "follows_lost", "follower_losses"),
    "profile_visits": ("profile_visits", "profile_views", "profile_visit"),
    "profile_activity": ("profile_activity", "profile_links_taps", "website_clicks"),
    "sends": ("sends", "shares_dm", "dm_sends", "sent", "forwards"),
    "shares": ("shares", "share_count", "shared"),
    "saves": ("saves", "saved", "save_count", "bookmarks"),
    "likes": ("likes", "like_count", "likes_count"),
    "comments": ("comments", "comments_count", "comment_count"),
    "views": ("views", "video_views", "total_views", "plays"),
    "reel_plays": ("reel_plays", "ig_reels_video_view_total_count", "plays_count"),
    "watch_time": ("watch_time", "ig_reels_video_view_total_time", "total_watch_time", "video_view_total_time"),
    "average_watch_time": ("average_watch_time", "ig_reels_avg_watch_time", "avg_watch_time"),
    "retention": ("retention", "retention_rate", "completion_rate", "avg_completion"),
    "posted_reels": ("posted_reels", "reels_published", "published_reels"),
    "follower_conversion": ("follower_conversion", "follow_rate", "conversion_rate"),
    # Идентификаторы и lineage публикации.
    "media_id": ("media_id", "id", "ig_id", "post_id", "content_id"),
    "permalink": ("permalink", "url", "link", "permalink_url"),
    "media_type": ("media_type", "type", "format", "content_type"),
    "caption": ("caption", "text", "title"),
    "trend_id": ("trend_id", "trend", "signal_id", "radar_id"),
    "format_id": ("format_id", "format", "template", "content_format"),
    "experiment_id": ("experiment_id", "experiment", "ab_variant", "variant"),
}

REVERSE_ALIAS = {alias: canon for canon, names in ALIASES.items() for alias in names}

# Признаки теневого/симулированного контура в пути или имени файла.
# Политика студии: не выдавать shadow, synthetic и predicted за метрики Instagram.
SHADOW_MARKERS = (
    "shadow", "synthetic", "simulat", "sim_", "mock", "sandbox", "fixture",
    "dry_run", "dryrun", "no_publish", "nopublish", "sample", "example",
    "learning_", "training", "backtest", "replay", "what_if",
)

# Значения, которые означают «данных нет». В 0 они НЕ превращаются.
NULLISH = {"", "none", "null", "n/a", "na", "nan", "-", "unknown", "undefined"}


def normalize_key(raw: str) -> str | None:
    key = str(raw).strip().lower().replace(" ", "_").replace("-", "_")
    return REVERSE_ALIAS.get(key)


def parse_number(raw) -> float | int | None:
    """Строка → число. Пустое/UNKNOWN → None, никогда не 0."""
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return raw
    text = str(raw).strip().replace("\u00a0", "").replace(" ", "")
    if text.lower() in NULLISH:
        return None
    text = text.replace("%", "").replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        return None
    return int(value) if value.is_integer() else value


def parse_date(raw) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if text.lower() in NULLISH:
        return None
    if text.isdigit() and len(text) >= 10:  # unix timestamp
        try:
            return dt.datetime.fromtimestamp(int(text[:10]), dt.timezone.utc).date().isoformat()
        except (ValueError, OSError):
            return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(text[:10], fmt).date().isoformat()
        except ValueError:
            continue
    try:  # ISO с временем и таймзоной
        return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


def normalize_record(raw: dict) -> dict:
    """Приводит произвольную строку выгрузки к каноническим полям."""
    record: dict = {}
    for key, value in raw.items():
        canon = normalize_key(key)
        if canon is None:
            continue
        if canon == "date":
            parsed = parse_date(value)
            if parsed:
                record["date"] = parsed
        elif canon in ("media_id", "permalink", "media_type", "caption",
                       "trend_id", "format_id", "experiment_id"):
            text = str(value).strip() if value is not None else ""
            if text and text.lower() not in NULLISH:
                record[canon] = text
        else:
            number = parse_number(value)
            if number is not None:
                record[canon] = number
    return record


def flatten(payload: dict) -> dict:
    """Разворачивает вложенный объект в плоские пары. Верхний уровень главнее."""
    flat: dict = {}
    for key, value in payload.items():
        if isinstance(value, dict):
            for nested_key, nested_value in flatten(value).items():
                flat.setdefault(nested_key, nested_value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for nested_key, nested_value in flatten(item).items():
                        flat.setdefault(nested_key, nested_value)
        else:
            flat[key] = value
    return flat


def expand_insights(payload: dict) -> list[dict]:
    """Разворачивает ответ Graph API Insights в записи по датам.

    Graph API отдаёт метрику как {"name": "follower_count", "values":
    [{"value": N, "end_time": ...}]}. Плоское разворачивание теряет имя
    метрики и молча выбрасывает все account-level данные, поэтому имя
    берётся из `name`, а значение и дата — из соответствующей записи `values`.
    Разбивки (breakdown-объекты) не угадываются и пропускаются.
    """
    rows_by_date: dict[str, dict] = {}
    data = payload.get("data")
    if isinstance(data, list):
        for metric in data:
            if not isinstance(metric, dict):
                continue
            name = metric.get("name") or metric.get("metric")
            if not name:
                continue
            pairs: list[tuple] = []
            values = metric.get("values")
            if isinstance(values, list):
                pairs += [(entry.get("end_time"), entry["value"])
                          for entry in values
                          if isinstance(entry, dict) and "value" in entry]
            total_value = metric.get("total_value")
            if isinstance(total_value, dict) and "value" in total_value:
                pairs.append((metric.get("end_time"), total_value["value"]))
            if not pairs and "value" in metric:
                pairs.append((metric.get("end_time"), metric["value"]))
            for when, value in pairs:
                if isinstance(value, (dict, list)):
                    continue  # breakdown без однозначного числа — не угадываем
                date = parse_date(when) or parse_date(payload.get("day")) or ""
                row = rows_by_date.setdefault(date, {})
                row[str(name)] = value
                if date:
                    row["date"] = date

    if not rows_by_date:
        return [flatten(payload)]

    scalars = {k: v for k, v in payload.items() if not isinstance(v, (dict, list))}
    return [{**scalars, **row} for row in rows_by_date.values()]


def read_csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(8192)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return [dict(row) for row in csv.DictReader(handle, dialect=dialect)]


def read_jsonl_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                print(f"WARN: {path.name}:{number} — строка не является JSON, пропущена", file=sys.stderr)
                continue
            if isinstance(payload, dict):
                rows.extend(expand_insights(payload))
    return rows


def read_sqlite_rows(path: Path) -> list[dict]:
    """Читает таблицы, где есть дата и хотя бы одна известная метрика."""
    rows: list[dict] = []
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        print(f"WARN: {path} не открывается только на чтение: {exc}", file=sys.stderr)
        return rows
    connection.row_factory = sqlite3.Row
    try:
        tables = [r[0] for r in connection.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view')")]
        for table in tables:
            try:
                columns = [c[1] for c in connection.execute(f'PRAGMA table_info("{table}")')]
            except sqlite3.Error:
                continue
            canon = {normalize_key(c) for c in columns} - {None}
            metrics = canon & set(ACCOUNT_FIELDS + POST_FIELDS)
            if "date" not in canon or not metrics:
                continue  # таблица не про метрики — не угадываем
            try:
                for row in connection.execute(f'SELECT * FROM "{table}"'):
                    record = normalize_record(dict(row))
                    if record.get("date"):
                        record["_table"] = table
                        rows.append(record)
            except sqlite3.Error as exc:
                print(f"WARN: {path.name}.{table} не читается: {exc}", file=sys.stderr)
    finally:
        connection.close()
    return rows


DISCOVERY_PATTERNS = (
    "post_insights.csv", "ig_insights.jsonl", "content_queue.db",
    "*insights*.csv", "*insights*.jsonl", "*insights*.db",
    "*analytics*.db", "*analytics*.csv", "*analytics*.jsonl",
    "*followers*.csv", "*followers*.jsonl",
)

SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "backups"}


def discover(studio: Path) -> list[Path]:
    found: list[Path] = []
    if not studio.exists():
        return found
    for pattern in DISCOVERY_PATTERNS:
        for path in studio.rglob(pattern):
            if path.is_file() and not any(part in SKIP_DIRS for part in path.parts):
                found.append(path)
    return sorted(set(found))


def read_source(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix in (".csv", ".tsv"):
        return [normalize_record(row) for row in read_csv_rows(path)]
    if suffix in (".jsonl", ".ndjson"):
        return [normalize_record(row) for row in read_jsonl_rows(path)]
    if suffix in (".db", ".sqlite", ".sqlite3"):
        return read_sqlite_rows(path)
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [normalize_record(flatten(item)) for item in payload if isinstance(item, dict)]
        if payload.get("snapshots"):
            return [normalize_record(flatten(item)) for item in payload["snapshots"] if isinstance(item, dict)]
        return [normalize_record(row) for row in expand_insights(payload)]
    print(f"WARN: неизвестный формат источника: {path}", file=sys.stderr)
    return []


def classify_source(path: Path) -> tuple[str, list[str]]:
    """Определяет, реальные это метрики платформы или теневой контур.

    Теневые/обучающие выгрузки выглядят как настоящие, но метриками Instagram
    не являются. Пометить их REAL — значит построить весь план роста на
    выдуманных числах, поэтому классификация делается по пути, а решение
    остаётся консервативным: при любом совпадении источник считается SHADOW.
    """
    haystack = str(path).lower().replace("\\", "/")
    hits = [marker for marker in SHADOW_MARKERS if marker in haystack]
    return ("SHADOW" if hits else "REAL"), hits


def file_fingerprint(path: Path) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    stat = path.stat()
    return {
        "path": str(path),
        "bytes": stat.st_size,
        "modified_at": dt.datetime.fromtimestamp(stat.st_mtime, dt.timezone.utc).isoformat(),
        "sha256": digest.hexdigest()[:16],
    }


def is_post_record(record: dict) -> bool:
    return bool(record.get("media_id") or record.get("permalink"))


def merge_snapshots(records: list[dict]) -> list[dict]:
    """Склеивает записи одной даты. Конфликт значений разрешается максимумом
    для счётчиков накопления и последним непустым для остального."""
    by_date: dict[str, dict] = {}
    for record in records:
        date = record.get("date")
        if not date:
            continue
        target = by_date.setdefault(date, {"date": date})
        for field in ACCOUNT_FIELDS:
            if field not in record:
                continue
            if field in target and field == "followers":
                target[field] = max(target[field], record[field])
            else:
                target[field] = record[field]
    return [by_date[key] for key in sorted(by_date)]


def merge_posts(posts: list[dict]) -> list[dict]:
    """Склеивает одну и ту же публикацию, пришедшую из нескольких источников.

    Без этого пост, лежащий и в post_insights.csv, и в content_queue.db,
    посчитался бы дважды — охват и атрибуция были бы завышены вдвое.
    Ключ — media_id, иначе permalink, иначе дата+тип. При конфликте числовых
    значений берётся большее: счётчики Insights только накапливаются,
    большее значение — более поздний замер.
    """
    merged: dict[tuple, dict] = {}
    for post in posts:
        key = (post.get("media_id") or post.get("permalink")
               or f"{post.get('date')}|{post.get('media_type', '')}",)
        target = merged.get(key)
        if target is None:
            merged[key] = dict(post)
            continue
        for field, value in post.items():
            if field not in target:
                target[field] = value
            elif isinstance(value, (int, float)) and isinstance(target[field], (int, float)):
                target[field] = max(target[field], value)
    return list(merged.values())


def aggregate_posts_to_days(posts: list[dict]) -> list[dict]:
    """Суммирует метрики публикаций по дням — источник дневных агрегатов,
    когда account-level выгрузки нет."""
    by_date: dict[str, dict] = {}
    summable = ("reach", "impressions", "sends", "saves", "likes", "comments",
                "shares", "follows", "profile_visits", "views", "reel_plays", "watch_time")
    for post in posts:
        date = post.get("date")
        if not date:
            continue
        target = by_date.setdefault(date, {"date": date, "posted_reels": 0})
        for field in summable:
            if field in post:
                target[field] = target.get(field, 0) + post[field]
        if str(post.get("media_type", "")).upper() in ("REELS", "REEL", "VIDEO"):
            target["posted_reels"] += 1
    for record in by_date.values():
        if not record.get("posted_reels"):
            record.pop("posted_reels", None)
    return list(by_date.values())


def coverage(snapshots: list[dict], posts: list[dict]) -> dict:
    report = {}
    for field in ACCOUNT_FIELDS:
        present = sum(1 for item in snapshots if field in item)
        report[field] = {
            "present": present,
            "total": len(snapshots),
            "status": "MEASURED" if present else "NOT_MEASURED",
        }
    for field in POST_FIELDS:
        present = sum(1 for item in posts if field in item)
        report[f"post.{field}"] = {
            "present": present,
            "total": len(posts),
            "status": "MEASURED" if present else "NOT_MEASURED",
        }
    return report


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    base = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, default=Path(r"D:\AI_CONTENT\Sofia"),
                        help="корень студии для автопоиска источников")
    parser.add_argument("--source", type=Path, action="append", default=[],
                        help="явный источник (можно повторять)")
    parser.add_argument("--out", type=Path, default=base / "data" / "followers_snapshots.json")
    parser.add_argument("--account", default="", help="handle аккаунта для метаданных")
    parser.add_argument("--dry-run", action="store_true", help="показать найденное, ничего не писать")
    args = parser.parse_args()

    sources = list(args.source) + [p for p in discover(args.studio) if p not in args.source]
    sources = [p for p in sources if p.exists()]

    if not sources:
        print("BLOCKED: реальных источников Instagram Insights не найдено.")
        print(f"  Искал в: {args.studio}")
        print(f"  Шаблоны: {', '.join(DISCOVERY_PATTERNS)}")
        print("  Ничего не записано. Подставлять нули вместо метрик нельзя.")
        print("  Запустить на машине со студией или указать путь через --source.")
        return 2

    print(f"Найдено источников: {len(sources)}")
    account_records: list[dict] = []
    post_records: list[dict] = []
    source_meta = []
    for path in sources:
        rows = read_source(path)
        posts = [r for r in rows if is_post_record(r)]
        accounts = [r for r in rows if not is_post_record(r) and r.get("date")]
        post_records.extend(posts)
        account_records.extend(accounts)
        meta = file_fingerprint(path)
        evidence, hits = classify_source(path)
        meta.update({"rows": len(rows), "post_rows": len(posts), "account_rows": len(accounts),
                     "evidence_label": evidence, "shadow_markers": hits})
        source_meta.append(meta)
        flag = f"  [{evidence}]" + (f" маркеры: {', '.join(hits)}" if hits else "")
        print(f"  {path} — строк: {len(rows)} (публикаций: {len(posts)}, дневных: {len(accounts)})")
        print(flag)

    # Дедупликация до агрегации: иначе пост из двух источников удвоит охват.
    unique_posts = merge_posts([p for p in post_records if p.get("date")])
    duplicates = len(post_records) - len(unique_posts)
    if duplicates > 0:
        print(f"  склеено дублей публикаций между источниками: {duplicates}")

    # Дневные агрегаты из публикаций дополняют account-level, но не затирают его.
    snapshots = merge_snapshots(aggregate_posts_to_days(unique_posts) + account_records)
    posts = sorted(unique_posts, key=lambda p: p["date"])

    if not snapshots:
        print("BLOCKED: источники прочитаны, но ни одной датированной записи с метриками нет.")
        return 2

    labels = {meta["evidence_label"] for meta in source_meta if meta.get("rows")}
    if not labels:
        overall = "NOT_MEASURED"
    elif labels == {"REAL"}:
        overall = "REAL"
    elif labels == {"SHADOW"}:
        overall = "SHADOW"
    else:
        overall = "MIXED"  # смесь нельзя считать реальной: считаем по слабейшему звену

    note = ("Собрано из локальных выгрузок студии. Отсутствующие поля опущены, "
            "а не заполнены нулями. NULL/UNKNOWN != 0.")
    if overall != "REAL":
        note += (" ВНИМАНИЕ: часть или все источники относятся к теневому/обучающему "
                 "контуру. Это НЕ метрики Instagram и не могут служить основанием "
                 "для выводов о реальном росте.")

    payload = {
        "schema_version": "2.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "account": args.account or "UNKNOWN",
        "evidence_label": overall,
        "note": note,
        "sources": source_meta,
        "coverage": coverage(snapshots, posts),
        "snapshots": snapshots,
        "posts": posts,
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if overall != "REAL":
        shadow_paths = [m["path"] for m in source_meta if m["evidence_label"] == "SHADOW"]
        print(f"\nВНИМАНИЕ — доказательность источников: {overall}")
        for item in shadow_paths:
            print(f"  теневой контур: {item}")
        print("  Эти данные НЕ являются метриками Instagram. Движок пометит все KPI как")
        print("  SHADOW и не будет менять по ним контент-план.")

    if args.dry_run:
        print(f"\nDRY-RUN: снимков {len(snapshots)}, публикаций {len(posts)}. Файл не записан.")
        print(f"Доказательность: {overall}")
        return 0

    atomic_write(args.out, text)
    measured = [f for f, c in payload["coverage"].items() if c["status"] == "MEASURED"]
    print(f"\nЗаписано: {args.out}")
    print(f"  снимков: {len(snapshots)} ({snapshots[0]['date']} — {snapshots[-1]['date']})")
    print(f"  публикаций: {len(posts)}")
    print(f"  измеренных полей: {len(measured)} из {len(payload['coverage'])}")
    print(f"  доказательность: {overall}")
    return 0 if overall == "REAL" else 3


if __name__ == "__main__":
    raise SystemExit(main())
