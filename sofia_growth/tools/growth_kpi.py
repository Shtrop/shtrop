#!/usr/bin/env python3
"""KPI роста подписчиков Sofia по фактическим Instagram Insights.

Только чтение и расчёт. Не ходит в сеть, не публикует, не пишет в canonical
state студии. Считает то, что реально измерено, и честно перечисляет то, что
измерить нечем.

Правило: отсутствующая метрика никогда не превращается в 0.

Вход — `followers_snapshots.json` (schema 2.0 от ingest_insights.py либо
схема 1.0 из ручного шаблона).

Пример:
    python growth_kpi.py --snapshots sofia_growth/data/followers_snapshots.json --summary
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

NOT_MEASURED = "NOT_MEASURED"

# Внешние ориентиры 2026 (открытые источники, не данные Sofia).
SENDS_PER_REACH_STRONG = 0.01
SENDS_PER_REACH_VIRAL = 0.03
PROFILE_CONVERSION_WEAK = 0.10
FOLLOWS_PER_1K_REACH_WEAK = 5.0
TARGET_MILESTONES = (1000, 10000, 50000)

# KPI, которые движок обязан либо посчитать, либо назвать NOT_MEASURED.
KPI_REGISTRY = (
    "followers_baseline", "growth_7d", "growth_30d", "growth_per_day",
    "reach", "follows_per_1k_reach", "profile_to_follow_conversion",
    "sends_per_reach", "saves_per_reach", "views", "watch_time",
    "average_watch_time", "retention", "unfollows", "net_follower_change",
    "best_posts", "worst_posts", "trend_attribution",
)


sys.path.insert(0, str(Path(__file__).resolve().parent))
from _console import force_utf8  # noqa: E402


def load(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(
            f"BLOCKED: файл снимков не найден: {path}\n"
            "Сначала собрать реальные данные: tools/ingest_insights.py --studio <корень студии>.\n"
            "Без реальных данных все KPI остаются NOT_MEASURED; нули не подставляются."
        )
    except json.JSONDecodeError as exc:
        sys.exit(f"FAIL: некорректный JSON в {path}: {exc}")
    if isinstance(payload, list):
        payload = {"snapshots": payload}
    return payload


def parse_dated(items: list[dict]) -> list[dict]:
    dated = []
    for item in items:
        try:
            item = dict(item)
            item["_date"] = dt.date.fromisoformat(item["date"])
        except (KeyError, TypeError, ValueError):
            continue
        dated.append(item)
    dated.sort(key=lambda entry: entry["_date"])
    return dated


def window(items: list[dict], days: int) -> list[dict]:
    """Срез последних `days` дней. days <= 0 — весь доступный диапазон."""
    if not items:
        return []
    if days <= 0:
        return list(items)
    cutoff = items[-1]["_date"] - dt.timedelta(days=days)
    return [item for item in items if item["_date"] >= cutoff]


def with_metrics(posts: list[dict]) -> list[dict]:
    """Публикации, у которых есть охват: только они участвуют в KPI."""
    return [post for post in posts if isinstance(post.get("reach"), (int, float))]


def total(items: list[dict], field: str) -> float | None:
    values = [i[field] for i in items if isinstance(i.get(field), (int, float))]
    return sum(values) if values else None


def mean(items: list[dict], field: str) -> float | None:
    values = [i[field] for i in items if isinstance(i.get(field), (int, float))]
    return sum(values) / len(values) if values else None


def sends_value(item: dict) -> float | None:
    """Пересылки публикации.

    В media insights Graph API этот сигнал называется `shares`; отдельного
    поля `sends` в выгрузке может не быть. Считать их разными метриками —
    значит потерять главный ранжирующий сигнал там, где он есть.
    """
    for field in ("sends", "shares"):
        value = item.get(field)
        if isinstance(value, (int, float)):
            return value
    return None


def total_sends(items: list[dict]) -> tuple[float | None, str | None]:
    """Сумма пересылок за окно и имя поля, из которого она взята."""
    for field in ("sends", "shares"):
        value = total(items, field)
        if value is not None:
            return value, field
    return None, None


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def fmt(value: float | None, digits: int = 2, suffix: str = "") -> str:
    return NOT_MEASURED if value is None else f"{round(value, digits):g}{suffix}"


def pct(value: float | None) -> str:
    return NOT_MEASURED if value is None else f"{round(value * 100, 3):g}%"


def follower_delta(items: list[dict]) -> tuple[float | None, float | None]:
    points = [i for i in items if isinstance(i.get("followers"), (int, float))]
    if len(points) < 2:
        return None, None
    delta = points[-1]["followers"] - points[0]["followers"]
    span = (points[-1]["_date"] - points[0]["_date"]).days
    return delta, (delta / span if span else None)


def compute(snapshots: list[dict], posts: list[dict], days: int) -> dict:
    recent = window(snapshots, days)
    week = window(snapshots, 7)
    month = window(snapshots, 30)
    latest = snapshots[-1] if snapshots else {}

    followers = latest.get("followers") if isinstance(latest.get("followers"), (int, float)) else None
    net_30d, per_day_30d = follower_delta(month)
    net_7d, _ = follower_delta(week)

    reach = total(recent, "reach")
    follows = total(recent, "follows")
    visits = total(recent, "profile_visits")
    sends, sends_field = total_sends(recent)
    saves = total(recent, "saves")

    follows_per_1k = ratio(follows, reach)
    metrics = {
        "window_days": days,
        "window_points": len(recent),
        "sends_field": sends_field,
        "latest_date": latest.get("date"),
        "followers_baseline": followers,
        "growth_7d": net_7d,
        "growth_30d": net_30d,
        "growth_per_day": per_day_30d,
        "net_follower_change": total(recent, "follows"),
        "reach": reach,
        "follows_per_1k_reach": follows_per_1k * 1000 if follows_per_1k is not None else None,
        "profile_to_follow_conversion": ratio(follows, visits),
        "sends_per_reach": ratio(sends, reach),
        "saves_per_reach": ratio(saves, reach),
        "views": total(recent, "views"),
        "watch_time": total(recent, "watch_time"),
        "average_watch_time": mean(recent, "average_watch_time"),
        "retention": mean(recent, "retention"),
        "unfollows": total(recent, "unfollows"),
    }
    metrics["rolling"] = {
        "7d": rolling_block(week),
        "30d": rolling_block(month),
    }
    metrics["best_posts"], metrics["worst_posts"] = rank_posts(posts, days, snapshots)
    metrics["trend_attribution"] = attribute(posts, days, snapshots)

    # Диапазон данных и наполненность окна: без них число вроде REACH: 376
    # выглядит как провал охвата, хотя это всего лишь узкое окно.
    measurable = with_metrics(posts)
    in_window = with_metrics(window(posts, days))
    metrics["data_span"] = (snapshots[0]["date"], snapshots[-1]["date"]) if snapshots else None
    metrics["data_span_days"] = ((snapshots[-1]["_date"] - snapshots[0]["_date"]).days
                                 if len(snapshots) > 1 else 0)
    metrics["posts_with_metrics_total"] = len(measurable)
    metrics["posts_with_metrics_in_window"] = len(in_window)
    return metrics


def rolling_block(items: list[dict]) -> dict:
    reach = total(items, "reach")
    net, per_day = follower_delta(items)
    return {
        "points": len(items),
        "net_followers": net,
        "per_day": per_day,
        "reach": reach,
        "sends_per_reach": ratio(total_sends(items)[0], reach),
        "saves_per_reach": ratio(total(items, "saves"), reach),
        "follows": total(items, "follows"),
    }


def post_score(post: dict) -> float | None:
    """Ранжирующая метрика публикации — sends per reach (главный сигнал 2026)."""
    return ratio(sends_value(post), post.get("reach"))


def rank_posts(posts: list[dict], days: int, snapshots: list[dict]) -> tuple[list, list]:
    if not posts or not snapshots:
        return [], []
    cutoff = snapshots[-1]["_date"] - dt.timedelta(days=days)
    scored = []
    for post in posts:
        if post["_date"] < cutoff:
            continue
        score = post_score(post)
        if score is None:
            continue
        scored.append({
            "date": post["date"],
            "media_id": post.get("media_id"),
            "permalink": post.get("permalink"),
            "media_type": post.get("media_type"),
            "format_id": post.get("format_id"),
            "trend_id": post.get("trend_id"),
            "sends_per_reach": score,
            "reach": post.get("reach"),
            "views": post.get("views"),
            "follows": post.get("follows"),
            "saves_per_reach": ratio(post.get("saves"), post.get("reach")),
        })
    if not scored:
        return [], []
    scored.sort(key=lambda item: item["sends_per_reach"], reverse=True)
    return scored[:3], scored[-3:][::-1]


def attribute(posts: list[dict], days: int, snapshots: list[dict]) -> list[dict]:
    """Атрибуция по lineage: группирует публикации по trend_id/format_id.
    Возвращает пусто, если lineage в данных реально нет."""
    if not posts or not snapshots:
        return []
    cutoff = snapshots[-1]["_date"] - dt.timedelta(days=days)
    groups: dict[tuple[str, str], list[dict]] = {}
    for post in posts:
        if post["_date"] < cutoff:
            continue
        key = post.get("trend_id") or post.get("format_id")
        if not key:
            continue
        kind = "trend_id" if post.get("trend_id") else "format_id"
        groups.setdefault((kind, key), []).append(post)

    rows = []
    for (kind, key), items in groups.items():
        reach = total(items, "reach")
        rows.append({
            "lineage": kind,
            "key": key,
            "posts": len(items),
            "reach": reach,
            "sends_per_reach": ratio(total_sends(items)[0], reach),
            "saves_per_reach": ratio(total(items, "saves"), reach),
            "follows": total(items, "follows"),
            "follows_per_1k_reach": (lambda r: r * 1000 if r is not None else None)(
                ratio(total(items, "follows"), reach)),
            # Одна публикация не доказывает повторяемость.
            "repeatable": len(items) >= 3,
        })
    rows.sort(key=lambda row: (row["sends_per_reach"] is None, -(row["sends_per_reach"] or 0)))
    return rows


def split_measured(metrics: dict) -> tuple[list[str], list[str]]:
    measured, missing = [], []
    for name in KPI_REGISTRY:
        value = metrics.get(name)
        empty = value is None or (isinstance(value, list) and not value)
        (missing if empty else measured).append(name)
    return measured, missing


def bottleneck(metrics: dict) -> str:
    sends = metrics["sends_per_reach"]
    conversion = metrics["profile_to_follow_conversion"]
    per_1k = metrics["follows_per_1k_reach"]
    if metrics["reach"] is None and per_1k is None:
        return f"{NOT_MEASURED}: без охвата и конверсии узкое место не определяется."
    if sends is not None and sends < SENDS_PER_REACH_STRONG:
        return ("Дистрибуция: sends per reach ниже 1%. Охват вне подписчиков ограничен на входе — "
                "работать над «переслать другу», а не над частотой постинга.")
    if conversion is not None and conversion < PROFILE_CONVERSION_WEAK:
        return ("Конверсия профиля: до профиля доходят, но не подписываются. Узкое место — "
                "шапка, закреплённые Reels и обещание аккаунта, а не контент ленты.")
    if per_1k is not None and per_1k < FOLLOWS_PER_1K_REACH_WEAK:
        return ("Релевантность: охват есть, подписок с него мало. Контент собирает случайную "
                "аудиторию — сузить тему и усилить повторяемость персоны.")
    return "Явного узкого места по имеющимся метрикам не видно; расширять то, что уже работает."


def next_action(metrics: dict) -> str:
    """Следующее изменение контент-плана, выведенное из данных."""
    attribution = [row for row in metrics["trend_attribution"] if row["repeatable"]]
    best = metrics["best_posts"][0] if metrics["best_posts"] else None
    parts = [bottleneck(metrics)]
    if attribution:
        top = attribution[0]
        parts.append(
            f"Масштабировать {top['lineage']}={top['key']}: {top['posts']} публикаций, "
            f"sends per reach {pct(top['sends_per_reach'])} — повторяемость подтверждена."
        )
        weak = [row for row in attribution if row["sends_per_reach"] is not None][-1:]
        if weak and weak[0]["key"] != top["key"]:
            parts.append(f"Свернуть {weak[0]['lineage']}={weak[0]['key']} "
                         f"(sends per reach {pct(weak[0]['sends_per_reach'])}).")
    elif best:
        parts.append(
            f"Лучший пост {best.get('format_id') or best.get('media_id')} даёт "
            f"sends per reach {pct(best['sends_per_reach'])}, но повторяемость не доказана "
            "(<3 публикаций формата) — добрать серию до 3, прежде чем переводить в ядро."
        )
    else:
        parts.append("Атрибуции нет: в данных отсутствует lineage публикация→тренд/формат. "
                     "Пока нельзя сказать, какой формат растит подписчиков.")
    return " ".join(parts)


def render(payload: dict, metrics: dict) -> str:
    measured, missing = split_measured(metrics)
    sources = payload.get("sources", [])
    evidence = payload.get("evidence_label", "REAL")
    lines = [
        "# KPI роста Sofia",
        "",
        f"Окно: {metrics['window_days'] or 'весь диапазон'} дн. | "
        f"последний снимок: {metrics['latest_date']} | точек в окне: {metrics['window_points']}",
        f"Диапазон данных: {metrics['data_span'][0]} — {metrics['data_span'][1]} "
        f"({metrics['data_span_days']} дн.) | публикаций с метриками: "
        f"{metrics['posts_with_metrics_in_window']} в окне из "
        f"{metrics['posts_with_metrics_total']} всего",
        f"Источники данных: {len(sources) or NOT_MEASURED} | доказательность: {evidence}",
    ]
    for source in sources:
        lines.append(f"  - [{source.get('evidence_label', 'REAL')}] `{source['path']}` "
                     f"(строк: {source.get('rows', '?')}, sha256:{source.get('sha256', '?')})")
    if evidence != "REAL":
        lines += ["",
                  f"> **ВНИМАНИЕ: доказательность {evidence}.** Данные получены из теневого или "
                  "обучающего контура и НЕ являются метриками Instagram. Все значения ниже "
                  "помечены соответственно и не могут служить основанием для выводов о "
                  "реальном росте подписчиков."]
    lines += [
        "",
        "| Метрика | Значение | Метка |",
        "|---|---|---|",
        f"| Подписчиков (baseline) | {fmt(metrics['followers_baseline'], 0)} | {label(metrics['followers_baseline'], evidence)} |",
        f"| Прирост за 7 дн. | {fmt(metrics['growth_7d'], 0)} | {label(metrics['growth_7d'], evidence)} |",
        f"| Прирост за 30 дн. | {fmt(metrics['growth_30d'], 0)} | {label(metrics['growth_30d'], evidence)} |",
        f"| Прирост в день | {fmt(metrics['growth_per_day'])} | {label(metrics['growth_per_day'], evidence)} |",
        f"| Охват за окно | {fmt(metrics['reach'], 0)} | {label(metrics['reach'], evidence)} |",
        f"| Follows на 1k охвата | {fmt(metrics['follows_per_1k_reach'])} | {label(metrics['follows_per_1k_reach'], evidence)} |",
        f"| Профиль → подписка | {pct(metrics['profile_to_follow_conversion'])} | {label(metrics['profile_to_follow_conversion'], evidence)} |",
        f"| Sends per reach | {pct(metrics['sends_per_reach'])} | "
        f"{label(metrics['sends_per_reach'], evidence)}"
        + (f" (из поля `{metrics['sends_field']}`)" if metrics.get("sends_field") else "") + " |",
        f"| Saves per reach | {pct(metrics['saves_per_reach'])} | {label(metrics['saves_per_reach'], evidence)} |",
        f"| Просмотры | {fmt(metrics['views'], 0)} | {label(metrics['views'], evidence)} |",
        f"| Watch time | {fmt(metrics['watch_time'], 0)} | {label(metrics['watch_time'], evidence)} |",
        f"| Средний watch time | {fmt(metrics['average_watch_time'])} | {label(metrics['average_watch_time'], evidence)} |",
        f"| Retention | {fmt(metrics['retention'])} | {label(metrics['retention'], evidence)} |",
        f"| Отписки | {fmt(metrics['unfollows'], 0)} | {label(metrics['unfollows'], evidence)} |",
        "",
        "## Rolling",
        "",
        "| Окно | Точек | Прирост | В день | Охват | Sends/reach | Saves/reach |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in ("7d", "30d"):
        block = metrics["rolling"][name]
        lines.append(
            f"| {name} | {block['points']} | {fmt(block['net_followers'], 0)} | {fmt(block['per_day'])} | "
            f"{fmt(block['reach'], 0)} | {pct(block['sends_per_reach'])} | {pct(block['saves_per_reach'])} |"
        )

    lines += ["", "## Лучшие и худшие публикации (по sends per reach)", ""]
    if metrics["best_posts"]:
        lines += ["| Ранг | Дата | Формат | Sends/reach | Охват | Follows |", "|---|---|---|---|---|---|"]
        for index, post in enumerate(metrics["best_posts"], start=1):
            lines.append(f"| ЛУЧШИЙ {index} | {post['date']} | "
                         f"{post.get('format_id') or post.get('media_type') or '—'} | "
                         f"{pct(post['sends_per_reach'])} | {fmt(post['reach'], 0)} | {fmt(post['follows'], 0)} |")
        for index, post in enumerate(metrics["worst_posts"], start=1):
            lines.append(f"| ХУДШИЙ {index} | {post['date']} | "
                         f"{post.get('format_id') or post.get('media_type') or '—'} | "
                         f"{pct(post['sends_per_reach'])} | {fmt(post['reach'], 0)} | {fmt(post['follows'], 0)} |")
    else:
        lines.append(f"{NOT_MEASURED}: в данных нет публикаций с охватом и пересылками.")

    lines += ["", "## Атрибуция тренд/формат → рост", ""]
    if metrics["trend_attribution"]:
        lines += ["| Lineage | Ключ | Публикаций | Sends/reach | Follows/1k охвата | Повторяемость |",
                  "|---|---|---|---|---|---|"]
        for row in metrics["trend_attribution"]:
            lines.append(f"| {row['lineage']} | {row['key']} | {row['posts']} | "
                         f"{pct(row['sends_per_reach'])} | {fmt(row['follows_per_1k_reach'])} | "
                         f"{'да' if row['repeatable'] else 'нет (<3 публикаций)'} |")
    else:
        lines.append(f"{NOT_MEASURED}: lineage публикация→тренд/формат в данных отсутствует.")

    lines += [
        "",
        "## Измеримость",
        "",
        f"**MEASURED ({len(measured)}):** {', '.join(measured) or '—'}",
        "",
        f"**NOT_MEASURED ({len(missing)}):** {', '.join(missing) or '—'}",
        "",
        "## Узкое место и следующее действие",
        "",
        next_action(metrics),
        "",
        "---",
        "REAL — из выгрузок Insights. PREDICTED — расчёт по текущему темпу, не обещание.",
        "Отсутствующие данные показаны как NOT_MEASURED и не заменяются нулями.",
    ]
    return "\n".join(lines)


def label(value, evidence: str = "REAL") -> str:
    """Метка значения. Теневой источник никогда не становится REAL."""
    if value is None:
        return NOT_MEASURED
    return evidence if evidence in ("SHADOW", "MIXED") else "REAL"


def summary_block(payload: dict, metrics: dict) -> str:
    measured, missing = split_measured(metrics)
    evidence = payload.get("evidence_label", "REAL")
    complete = (metrics["trend_attribution"] and metrics["followers_baseline"] is not None
                and metrics["sends_per_reach"] is not None)
    # Теневые данные не могут подтвердить цикл: механика работает, рост — нет.
    loop = "VERIFIED" if (complete and evidence == "REAL") else "PARTIAL"
    sources = payload.get("sources", [])
    span = metrics.get("data_span")
    window_note = (f"WINDOW: {metrics['window_days'] or 'весь диапазон'} дн. | "
                   f"публикаций с метриками в окне: {metrics['posts_with_metrics_in_window']} "
                   f"из {metrics['posts_with_metrics_total']}")
    lines = [
        f"EVIDENCE: {evidence}" + ("" if evidence == "REAL"
                                   else "  ← НЕ метрики Instagram, теневой/обучающий контур"),
        f"DATA SPAN: {span[0]} — {span[1]} ({metrics['data_span_days']} дн.)" if span
        else "DATA SPAN: NOT_MEASURED",
        window_note,
        "",
        f"FOLLOWERS BASELINE: {fmt(metrics['followers_baseline'], 0)}",
        f"30D GROWTH: {fmt(metrics['growth_30d'], 0)}",
        f"REACH: {fmt(metrics['reach'], 0)}",
        f"FOLLOWS PER REACH: {fmt(metrics['follows_per_1k_reach'])} на 1k охвата",
        f"PROFILE→FOLLOW CONVERSION: {pct(metrics['profile_to_follow_conversion'])}",
        f"SENDS PER REACH: {pct(metrics['sends_per_reach'])}",
        f"SAVES PER REACH: {pct(metrics['saves_per_reach'])}",
        "",
        f"MEASURED KPI: {', '.join(measured) or '—'}",
        f"NOT MEASURED KPI: {', '.join(missing) or '—'}",
        "",
        f"GROWTH LOOP: {loop}",
        "",
        "REAL DATA SOURCE:",
    ]
    lines += [f"  [{s.get('evidence_label', 'REAL')}] {s['path']}" for s in sources] \
        or [f"  {NOT_MEASURED}"]
    action = next_action(metrics)
    total_posts = metrics["posts_with_metrics_total"]
    in_window = metrics["posts_with_metrics_in_window"]
    if in_window < 3 and total_posts > in_window:
        action = (f"Окно {metrics['window_days']} дн. захватило только {in_window} публикаций "
                  f"с метриками из {total_posts} доступных — выводы по нему делать нельзя. "
                  f"Пересчитать по всему диапазону: --days 0. " + action)
    if evidence != "REAL":
        action = ("Реальных метрик Instagram нет — контент-план по этим данным не меняется. "
                  "Разбор теневых чисел приведён только как проверка механики: " + action)
    lines += ["", "NEXT GROWTH ACTION:", f"  {action}"]
    return "\n".join(lines)


def build_memory(payload: dict, metrics: dict, previous: dict | None) -> dict:
    """Growth memory: накапливает измеренные исходы форматов/трендов.

    Доказательность источника переносится в каждую запись: по теневым данным
    движок не станет менять приоритет форматов в реальном плане.
    """
    evidence = payload.get("evidence_label", "REAL")
    memory = previous or {"schema_version": "1.1", "entries": {}}
    memory["evidence_label"] = evidence
    memory.setdefault("entries", {})
    for row in metrics["trend_attribution"]:
        key = f"{row['lineage']}:{row['key']}"
        entry = memory["entries"].setdefault(key, {"observations": []})
        entry["lineage"] = row["lineage"]
        entry["key"] = row["key"]
        entry["posts"] = row["posts"]
        entry["sends_per_reach"] = row["sends_per_reach"]
        entry["follows_per_1k_reach"] = row["follows_per_1k_reach"]
        entry["repeatable"] = row["repeatable"]
        entry["verdict"] = verdict_for(row)
        entry["evidence_label"] = evidence
        entry["observations"].append({
            "measured_at": payload.get("generated_at") or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "window_days": metrics["window_days"],
            "posts": row["posts"],
            "sends_per_reach": row["sends_per_reach"],
        })
        entry["observations"] = entry["observations"][-12:]  # история не растёт бесконечно
    memory["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    memory["baseline"] = {
        "evidence_label": evidence,
        "followers": metrics["followers_baseline"],
        "sends_per_reach": metrics["sends_per_reach"],
        "saves_per_reach": metrics["saves_per_reach"],
        "follows_per_1k_reach": metrics["follows_per_1k_reach"],
        "profile_to_follow_conversion": metrics["profile_to_follow_conversion"],
        "measured_at": metrics["latest_date"],
    }
    return memory


def verdict_for(row: dict) -> str:
    if not row["repeatable"]:
        return "INSUFFICIENT"  # <3 публикаций — не доказательство
    value = row["sends_per_reach"]
    if value is None:
        return NOT_MEASURED
    if value >= SENDS_PER_REACH_VIRAL:
        return "SCALE"
    if value >= SENDS_PER_REACH_STRONG:
        return "KEEP"
    return "DROP"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    force_utf8()
    base = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--snapshots", type=Path, default=base / "data" / "followers_snapshots.json")
    parser.add_argument("--days", type=int, default=30,
                        help="окно расчёта в днях; 0 — весь доступный диапазон")
    parser.add_argument("--summary", action="store_true", help="короткий блок для отчёта владельцу")
    parser.add_argument("--json", action="store_true", help="выдать метрики как JSON")
    parser.add_argument("--out", type=Path, help="записать отчёт в файл")
    parser.add_argument("--write-memory", type=Path, nargs="?", const=base / "data" / "growth_memory.json",
                        help="обновить growth memory измеренными исходами")
    args = parser.parse_args()

    payload = load(args.snapshots)
    snapshots = parse_dated(payload.get("snapshots", []))
    posts = parse_dated(payload.get("posts", []))

    if not snapshots:
        print("# KPI роста Sofia\n\nВердикт: NOT_MEASURED — валидных снимков нет.\n"
              "Ни одну метрику посчитать нельзя; нули подставлять нельзя.")
        return 2

    metrics = compute(snapshots, posts, args.days)
    measured, missing = split_measured(metrics)

    if args.json:
        text = json.dumps({k: v for k, v in metrics.items()}, ensure_ascii=False, indent=2, default=str)
    elif args.summary:
        text = summary_block(payload, metrics)
    else:
        text = render(payload, metrics)

    if args.out:
        atomic_write(args.out, text)
        print(f"Записано: {args.out}")
    else:
        print(text)

    if args.write_memory:
        previous = None
        if args.write_memory.exists():
            try:
                previous = json.loads(args.write_memory.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                print(f"WARN: {args.write_memory} повреждён, память пересоздана", file=sys.stderr)
        memory = build_memory(payload, metrics, previous)
        atomic_write(args.write_memory, json.dumps(memory, ensure_ascii=False, indent=2))
        print(f"Growth memory обновлена: {args.write_memory} "
              f"(записей: {len(memory['entries'])})", file=sys.stderr)

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
