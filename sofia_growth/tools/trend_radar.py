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

KPI_BY_LEVER = {
    "sends": "sends_per_reach (цель 1-2%, >3% — вирусный разнос через DM)",
    "watch_time": "total_watch_seconds / reach и доля досмотров",
    "skip_rate": "удержание на 2-й секунде",
    "saves": "saves_per_reach",
    "profile_visits": "profile_visits и follows_per_profile_visit",
    "likes": "likes_per_reach",
}


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


def score_signal(signal: dict) -> tuple[float, list[str]]:
    levers = FORMAT_LEVERS.get(signal["id"], ["watch_time"])
    lever_value = max(LEVER_WEIGHTS.get(lever, 0.3) for lever in levers)
    fit = FIT_SCORE.get(signal.get("sofia_fit", "medium"), 0.65)
    confidence = CONFIDENCE_SCORE.get(signal.get("confidence", "medium"), 0.7)
    cost = COST_PENALTY.get(signal.get("production_cost", "medium"), 0.8)
    return round(lever_value * fit * confidence * cost, 3), levers


def build_backlog(radar: dict, guardrails: dict) -> list[dict]:
    blocked = guardrails.get("brand_safety_block", [])
    backlog = []
    for signal in radar.get("format_signals", []):
        flags = brand_safety_flags(signal, blocked)
        score, levers = score_signal(signal)
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
                "status": "BLOCKED_BRAND_SAFETY" if flags else "PROPOSED",
                "brand_safety_flags": flags,
                "source": signal.get("source", ""),
                "evidence_label": "PREDICTED",
            }
        )
    backlog.sort(key=lambda item: item["score"], reverse=True)
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
        "| # | Формат | Score | Рычаг | Fit | Cost | Confidence | Статус |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for index, item in enumerate(backlog[:top], start=1):
        lines.append(
            f"| {index} | {item['title']} | {item['score']} | {', '.join(item['levers'])} | "
            f"{item['sofia_fit']} | {item['production_cost']} | {item['confidence']} | {item['status']} |"
        )

    lines += ["", "## Гипотезы и что измерять", ""]
    for index, item in enumerate(backlog[:top], start=1):
        lines += [
            f"### {index}. {item['title']}",
            f"- Гипотеза: формат поднимет `{item['levers'][0]}` относительно baseline последних 14 дней.",
            f"- Метрика решения: {item['kpi'][0]}",
            "- Критерий успеха: задать по фактическому baseline (сейчас NOT_MEASURED без данных аккаунта).",
            f"- Источник сигнала: {item['source']}",
            "",
        ]
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
    parser.add_argument("--top", type=int, default=8, help="сколько позиций показать")
    parser.add_argument("--max-age-days", type=int, default=14, help="порог свежести радара")
    parser.add_argument("--json", action="store_true", help="вывести backlog как JSON")
    parser.add_argument("--out", type=Path, help="записать отчёт в файл (создаёт, не удаляет)")
    args = parser.parse_args()

    radar = load_json(args.radar)
    guardrails = load_json(args.guardrails)
    backlog = build_backlog(radar, guardrails)
    age = radar_age_days(radar, dt.date.today())

    if args.json:
        output = json.dumps(
            {
                "radar_date": radar.get("radar_date"),
                "radar_age_days": age,
                "stale": age is None or age > args.max_age_days,
                "evidence_label": "PREDICTED",
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
