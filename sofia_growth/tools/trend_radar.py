#!/usr/bin/env python3
"""Ранжирование трендовых сигналов в backlog экспериментов роста Sofia.

Только чтение и расчёт. Скрипт ничего не публикует, не трогает canonical state
студии и не пишет в D:\\AI_CONTENT\\Sofia. Результат — предложение (PREDICTED),
а не метрика.

Пример:
    python3 sofia_growth/tools/trend_radar.py \
        --radar sofia_growth/data/trend_radar.json \
        --guardrails sofia_growth/data/persona_guardrails.json \
        --top 8
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

# Рычаг роста -> вес. Основано на подтверждённых ranking-сигналах 2026:
# sends per reach и watch time тянут нефолловерский охват сильнее лайков.
LEVER_WEIGHTS = {
    "sends": 1.00,      # DM-пересылки: главный источник охвата вне подписчиков
    "watch_time": 0.90,  # суммарные секунды с повторами
    "skip_rate": 0.80,   # удержание в первые 1-2 секунды
    "saves": 0.55,       # сохранения: профильные визиты и отложенный возврат
    "profile_visits": 0.50,
    "likes": 0.25,       # работают в основном на охват среди подписчиков
}

# Какие рычаги двигает формат. Ключи — id из format_signals.
FORMAT_LEVERS = {
    "fmt-raw-single-take": ["skip_rate", "watch_time"],
    "fmt-flop-core": ["sends", "saves"],
    "fmt-10-10-habits": ["sends", "skip_rate"],
    "fmt-this-or-that": ["watch_time", "sends"],
    "fmt-transition-sketch-to-reality": ["skip_rate", "watch_time"],
    "fmt-storytime-direct-to-camera": ["watch_time", "profile_visits"],
    "fmt-saveable-carousel": ["saves", "profile_visits"],
}

FIT_SCORE = {"high": 1.0, "medium": 0.65, "low": 0.3}
CONFIDENCE_SCORE = {"high": 1.0, "medium": 0.7, "low": 0.45}
# Стоимость производства как штраф: GPU — ограниченный ресурс (один тяжёлый job).
COST_PENALTY = {"low": 1.0, "medium": 0.8, "high": 0.55}

# Множители по РЕАЛЬНО измеренному исходу формата (growth_memory.json).
# Память побеждает априорную оценку: измеренное важнее предсказанного.
# Приоритет доказательства. Измеренный победитель обязан стоять выше догадки,
# а измеренный проигравший — ниже неё, каким бы привлекательным ни был априорный
# score: данные аккаунта весомее эвристики.
EVIDENCE_PRIORITY = {"SCALE": 3, "KEEP": 2, "INSUFFICIENT": 1, "NOT_MEASURED": 1, "DROP": 0}
UNMEASURED_PRIORITY = 1

MEMORY_MULTIPLIER = {
    "SCALE": 1.6,   # повторяемо и выше 3% sends per reach
    "KEEP": 1.25,   # повторяемо и выше 1%
    "DROP": 0.35,   # повторяемо и ниже 1% — сворачивать
    "INSUFFICIENT": 1.0,  # <3 публикаций: не доказательство ни в одну сторону
    "NOT_MEASURED": 1.0,
}

KPI_BY_LEVER = {
    "sends": "sends_per_reach (цель 1-2%, >3% — вирусный разнос через DM)",
    "watch_time": "total_watch_seconds / reach и доля досмотров",
    "skip_rate": "удержание на 2-й секунде",
    "saves": "saves_per_reach",
    "profile_visits": "profile_visits и follows_per_profile_visit",
    "likes": "likes_per_reach",
}


def load_memory(path: Path) -> dict:
    """Growth memory необязательна: без неё скоринг остаётся чисто априорным."""
    if not path or not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"WARN: growth memory повреждена, игнорируется: {path}", file=sys.stderr)
        return {}
    return payload.get("entries", {})


def memory_entry(memory: dict, signal_id: str) -> dict | None:
    """Ищет измеренный исход формата по lineage-ключам."""
    for key in (f"format_id:{signal_id}", f"trend_id:{signal_id}"):
        if key in memory:
            return memory[key]
    return None


def load_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        sys.exit(f"FAIL: файл не найден: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"FAIL: некорректный JSON в {path}: {exc}")


def radar_age_days(radar: dict, today: dt.date) -> int | None:
    raw = radar.get("radar_date")
    if not raw:
        return None
    try:
        return (today - dt.date.fromisoformat(raw)).days
    except ValueError:
        return None


def brand_safety_flags(signal: dict, blocked: list[str]) -> list[str]:
    haystack = f"{signal.get('title', '')} {signal.get('detail', '')}".lower()
    return [term for term in blocked if term.lower() in haystack]


def score_signal(signal: dict, entry: dict | None) -> tuple[float, list[str], float]:
    levers = FORMAT_LEVERS.get(signal["id"], ["watch_time"])
    lever_value = max(LEVER_WEIGHTS.get(lever, 0.3) for lever in levers)
    fit = FIT_SCORE.get(signal.get("sofia_fit", "medium"), 0.65)
    confidence = CONFIDENCE_SCORE.get(signal.get("confidence", "medium"), 0.7)
    cost = COST_PENALTY.get(signal.get("production_cost", "medium"), 0.8)
    prior = lever_value * fit * confidence * cost
    multiplier = MEMORY_MULTIPLIER.get((entry or {}).get("verdict", "NOT_MEASURED"), 1.0)
    return round(prior * multiplier, 3), levers, round(prior, 3)


def build_backlog(radar: dict, guardrails: dict, memory: dict) -> list[dict]:
    blocked = guardrails.get("brand_safety_block", [])
    backlog = []
    for signal in radar.get("format_signals", []):
        flags = brand_safety_flags(signal, blocked)
        entry = memory_entry(memory, signal["id"])
        score, levers, prior = score_signal(signal, entry)
        backlog.append(
            {
                "id": signal["id"],
                "title": signal["title"],
                "score": score,
                "levers": levers,
                "kpi": [KPI_BY_LEVER[lever] for lever in levers],
                "sofia_fit": signal.get("sofia_fit", "medium"),
                "production_cost": signal.get("production_cost", "medium"),
                "confidence": signal.get("confidence", "medium"),
                "prior_score": prior,
                "evidence_priority": (EVIDENCE_PRIORITY.get(entry.get("verdict"), 1)
                                      if entry else UNMEASURED_PRIORITY),
                "status": "BLOCKED_BRAND_SAFETY" if flags else "PROPOSED",
                "brand_safety_flags": flags,
                "source": signal.get("source", ""),
                # Метка повышается до REAL только там, где формат действительно измерен.
                "evidence_label": "REAL" if entry else "PREDICTED",
                "measured": {
                    "verdict": entry.get("verdict"),
                    "posts": entry.get("posts"),
                    "sends_per_reach": entry.get("sends_per_reach"),
                    "repeatable": entry.get("repeatable"),
                } if entry else None,
            }
        )
    # Сначала уровень доказательства, затем численный score внутри уровня.
    backlog.sort(key=lambda item: (item["evidence_priority"], item["score"]), reverse=True)
    return backlog


def render(radar: dict, backlog: list[dict], top: int, age: int | None, max_age: int) -> str:
    lines = [
        "# Backlog экспериментов роста (PREDICTED)",
        "",
        f"Radar date: {radar.get('radar_date', 'unknown')} | "
        f"возраст: {age if age is not None else 'unknown'} дн. | "
        f"порог свежести: {max_age} дн.",
        "",
    ]
    if age is None:
        lines.append("> WARN: не удалось определить дату радара — считать данные непроверенными.\n")
    elif age > max_age:
        lines.append(f"> WARN: радар устарел ({age} дн.). Обновить до постановки в план.\n")

    lines += [
        "| # | Формат | Score | Рычаг | Fit | Cost | Доказательство | Измерено |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for index, item in enumerate(backlog[:top], start=1):
        measured = item.get("measured")
        measured_cell = (f"{measured['verdict']} ({measured['posts']} публ., "
                         f"s/r {round((measured['sends_per_reach'] or 0) * 100, 2)}%)"
                         if measured else "—")
        lines.append(
            f"| {index} | {item['title']} | {item['score']} | {', '.join(item['levers'])} | "
            f"{item['sofia_fit']} | {item['production_cost']} | {item['evidence_label']} | {measured_cell} |"
        )

    lines += ["", "## Гипотезы и что измерять", ""]
    for index, item in enumerate(backlog[:top], start=1):
        measured = item.get("measured")
        lines += [f"### {index}. {item['title']}"]
        if measured:
            lines += [
                f"- Измерено (REAL): {measured['posts']} публикаций, "
                f"sends per reach {measured['sends_per_reach']}, вердикт `{measured['verdict']}`.",
                f"- Априорный score был {item['prior_score']}, с учётом памяти — {item['score']}.",
            ]
        else:
            lines += [
                f"- Гипотеза (PREDICTED): формат поднимет `{item['levers'][0]}` относительно baseline.",
                "- Критерий успеха: задать по фактическому baseline; без данных — NOT_MEASURED.",
            ]
        lines += [f"- Метрика решения: {item['kpi'][0]}", f"- Источник сигнала: {item['source']}", ""]
    lines += [
        "---",
        "Все оценки — PREDICTED (AI ANALYSIS). Это не метрики Instagram.",
        "План не снимает FROZEN и не разрешает публикацию.",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--radar", type=Path, default=base / "data" / "trend_radar.json")
    parser.add_argument("--guardrails", type=Path, default=base / "data" / "persona_guardrails.json")
    parser.add_argument("--memory", type=Path, default=base / "data" / "growth_memory.json",
                        help="growth memory с измеренными исходами форматов")
    parser.add_argument("--top", type=int, default=8, help="сколько позиций показать")
    parser.add_argument("--max-age-days", type=int, default=14, help="порог свежести радара")
    parser.add_argument("--json", action="store_true", help="вывести backlog как JSON")
    parser.add_argument("--out", type=Path, help="записать отчёт в файл (создаёт, не удаляет)")
    args = parser.parse_args()

    radar = load_json(args.radar)
    guardrails = load_json(args.guardrails)
    memory = load_memory(args.memory)
    backlog = build_backlog(radar, guardrails, memory)
    age = radar_age_days(radar, dt.date.today())

    if args.json:
        output = json.dumps(
            {
                "radar_date": radar.get("radar_date"),
                "radar_age_days": age,
                "stale": age is None or age > args.max_age_days,
                "memory_entries": len(memory),
                "backlog": backlog,
            },
            ensure_ascii=False,
            indent=2,
        )
    else:
        output = render(radar, backlog, args.top, age, args.max_age_days)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.out.with_suffix(args.out.suffix + ".tmp")
        tmp.write_text(output, encoding="utf-8")
        tmp.replace(args.out)
        print(f"Записано: {args.out}")
    else:
        print(output)

    # Устаревший радар — сигнал «обновить перед планированием», не отказ.
    return 2 if age is None or age > args.max_age_days else 0


if __name__ == "__main__":
    raise SystemExit(main())
