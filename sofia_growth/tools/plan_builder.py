#!/usr/bin/env python3
"""Сборка следующего контент-плана из бэклога трендов и growth memory.

Последнее звено цикла: решение движка превращается в конкретные слоты с хуками.
Генератор ничего не сочиняет — хуки берутся из `data/hook_bank.json`, приоритет
форматов из `trend_radar.py`, а вердикты по ним из реальных замеров.

План является предложением: он не ставит в очередь, не снимает HOLD и не
публикует.

Пример:
    python plan_builder.py --days 14 --out sofia_growth/plans/CONTENT_PLAN_next.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

WEEKDAY_RU = ("пн", "вт", "ср", "чт", "пт", "сб", "вс")
# Публикация вт-пт: рабочие дни дают более плотный отклик холодной аудитории.
PUBLISH_WEEKDAYS = (1, 2, 3, 4)
CAROUSEL_WEEKDAY = 2  # среда — слот под сохраняемую карусель
CAROUSEL_FORMAT = "fmt-saveable-carousel"
EXPERIMENT_SHARE = 0.2  # правило 80/20


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"FAIL: некорректный JSON в {path}: {exc}")


def backlog_from_radar(tools: Path, radar: Path, guardrails: Path, memory: Path) -> list[dict]:
    """Переиспользует trend_radar.py как единственный источник приоритета."""
    result = subprocess.run(
        [sys.executable, str(tools / "trend_radar.py"), "--json",
         "--radar", str(radar), "--guardrails", str(guardrails), "--memory", str(memory)],
        capture_output=True, text=True)
    if result.returncode not in (0, 2):
        sys.exit(f"FAIL: trend_radar.py вернул {result.returncode}\n{result.stderr[-800:]}")
    payload = json.loads(result.stdout)
    return payload.get("backlog", []), payload.get("stale", True)


def publish_dates(start: dt.date, days: int) -> list[dt.date]:
    return [start + dt.timedelta(days=offset) for offset in range(days)
            if (start + dt.timedelta(days=offset)).weekday() in PUBLISH_WEEKDAYS]


def pick_formats(backlog: list[dict], slots: int) -> tuple[list[dict], list[dict]]:
    """Делит бэклог на ядро и эксперименты по правилу 80/20.

    Ядро — подтверждённые замерами форматы; пока замеров нет, ядром служат
    два лучших по априорному score. Эксперименты берутся из остатка, чтобы
    формат не попал одновременно в ядро и в эксперименты.
    DROP-форматы исключаются полностью: память измерила, что они не работают.
    Карусельный слот выведен из обоих списков — у него отдельный слот в неделе.
    """
    def trusted(item: dict) -> bool:
        return bool(item.get("measured")) and item.get("evidence_label") == "REAL"

    usable = [item for item in backlog
              if item["status"] != "BLOCKED_BRAND_SAFETY"
              and item["id"] != CAROUSEL_FORMAT
              and not (trusted(item) and item["measured"].get("verdict") == "DROP")]
    core = [item for item in usable if trusted(item)] or usable[:2]
    core_ids = {item["id"] for item in core}
    experiments = [item for item in usable if item["id"] not in core_ids]
    experiment_slots = max(1, round(slots * EXPERIMENT_SHARE)) if experiments else 0
    return core, experiments[:experiment_slots]


def hook_for(hooks: dict, format_id: str, index: int) -> dict:
    options = hooks.get("formats", {}).get(format_id, [])
    if not options:
        return {"hook": "ЗАПОЛНИТЬ: хука для формата нет в hook_bank.json",
                "sendability": "ЗАПОЛНИТЬ"}
    return options[index % len(options)]


def success_criterion(item: dict, baseline: dict | None) -> str:
    lever = item["levers"][0]
    measured = item.get("measured") if item.get("evidence_label") == "REAL" else None
    if baseline and baseline.get("evidence_label", "REAL") != "REAL":
        baseline = None
    if measured and measured.get("sends_per_reach") is not None:
        current = measured["sends_per_reach"]
        return (f"удержать sends per reach не ниже {round(current * 100, 2)}% "
                f"(измерено на {measured['posts']} публикациях)")
    if baseline and baseline.get("sends_per_reach") is not None and lever == "sends":
        target = baseline["sends_per_reach"]
        return f"превысить baseline аккаунта {round(target * 100, 2)}% по sends per reach"
    return f"NOT_MEASURED: baseline по `{lever}` отсутствует, задать после первого замера"


def build(args) -> str:
    base = Path(__file__).resolve().parent.parent
    hooks = load_json(base / "data" / "hook_bank.json", {"formats": {}})
    memory = load_json(args.memory, {}) or {}
    baseline = memory.get("baseline")
    backlog, stale = backlog_from_radar(base / "tools", args.radar,
                                        base / "data" / "persona_guardrails.json", args.memory)
    if not backlog:
        sys.exit("BLOCKED: бэклог пуст — нечего ставить в план.")

    dates = publish_dates(args.start, args.days)
    core, experiments = pick_formats(backlog, len(dates))

    carousel = next((item for item in backlog if item["id"] == CAROUSEL_FORMAT), None)
    reel_dates = [d for d in dates if not (carousel and d.weekday() == CAROUSEL_WEEKDAY)]
    # Эксперименты занимают последние слоты периода: сначала набирается ядро.
    experiment_dates = set(reel_dates[-len(experiments):]) if experiments else set()

    rows, used, taken = [], {}, 0
    for date in dates:
        if carousel and date.weekday() == CAROUSEL_WEEKDAY:
            item, slot = carousel, "Карусель"
        elif date in experiment_dates:
            item = experiments[sorted(experiment_dates).index(date) % len(experiments)]
            slot = "Reel (эксперимент)"
        else:
            item = core[taken % len(core)]
            slot = "Reel (ядро)"
            taken += 1
        index = used.get(item["id"], 0)
        used[item["id"]] = index + 1
        rows.append({"date": date, "slot": slot, "item": item,
                     **hook_for(hooks, item["id"], index)})

    measured_count = sum(1 for row in rows if row["item"].get("evidence_label") == "REAL")
    dropped = [item for item in backlog
               if item.get("evidence_label") == "REAL"
               and (item.get("measured") or {}).get("verdict") == "DROP"]
    shadow = [item for item in backlog if item.get("evidence_label") == "SHADOW"]

    lines = [
        f"# Контент-план Sofia: {dates[0].isoformat()} — {dates[-1].isoformat()}",
        "",
        f"Сгенерировано: {dt.date.today().isoformat()} | слотов: {len(rows)} "
        f"(на реальных замерах: {measured_count}, гипотез: {len(rows) - measured_count})",
        "",
        "**Статус:** предложение. План не ставит в очередь, не снимает HOLD, не публикует.",
    ]
    if stale:
        lines.append("> WARN: трендовый радар устарел (>14 дн.) — обновить до постановки в работу.")
    if baseline and baseline.get("followers") is not None \
            and baseline.get("evidence_label", "REAL") == "REAL":
        lines.append(
            f"> Baseline аккаунта (REAL, {baseline.get('measured_at')}): "
            f"{baseline['followers']} подписчиков, sends per reach "
            f"{round((baseline.get('sends_per_reach') or 0) * 100, 2)}%.")
    elif baseline and baseline.get("evidence_label") in ("SHADOW", "MIXED"):
        lines.append(f"> Baseline аккаунта: `{baseline['evidence_label']}` — числа из теневого "
                     "контура, критериями успеха служить не могут.")
    else:
        lines.append("> Baseline аккаунта: `NOT_MEASURED` — критерии успеха задать после первого замера.")

    lines += [
        "",
        "## Слоты",
        "",
        "| Дата | День | Слот | Формат | Хук (первый кадр) | Кому перешлют | Доказательство |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        item = row["item"]
        measured = item.get("measured")
        evidence = (f"{item['evidence_label']} · {measured['verdict']}"
                    if measured else "PREDICTED")
        lines.append(
            f"| {row['date'].isoformat()} | {WEEKDAY_RU[row['date'].weekday()]} | {row['slot']} | "
            f"{item['title']} | {row['hook']} | {row['sendability']} | {evidence} |")

    lines += ["", "## Гипотезы и критерии", ""]
    seen = set()
    for row in rows:
        item = row["item"]
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        measured = item.get("measured")
        lines += [
            f"### {item['title']}",
            f"- Рычаг: `{item['levers'][0]}` → метрика решения: {item['kpi'][0]}",
            (f"- Статус: {item['evidence_label']}, вердикт `{measured['verdict']}` "
             f"на {measured['posts']} публикациях."
             + ("" if item["evidence_label"] == "REAL"
                else " Теневой контур — на план не влияет.")
             if measured else "- Статус: PREDICTED, формат ещё не измерен на аккаунте."),
            f"- Критерий: {success_criterion(item, baseline)}",
            f"- Стоимость производства: {item['production_cost']}",
            "",
        ]

    if shadow:
        lines += ["## Теневые замеры (на план не влияют)", "",
                  "Данные по этим форматам получены из обучающего/теневого контура и не "
                  "являются метриками Instagram, поэтому приоритет по ним не меняется:", ""]
        for item in shadow:
            measured = item["measured"]
            lines.append(f"- {item['title']} — `{measured['verdict']}` по теневым данным "
                         f"({measured['posts']} публикаций). Требует подтверждения реальными Insights.")
        lines.append("")

    if dropped:
        lines += ["## Исключено по данным", ""]
        for item in dropped:
            measured = item["measured"]
            lines.append(f"- **{item['title']}** — вердикт `DROP`: sends per reach "
                         f"{round((measured['sends_per_reach'] or 0) * 100, 2)}% "
                         f"на {measured['posts']} публикациях. В план не ставится.")
        lines.append("")

    lines += [
        "## Сквозные требования",
        "",
        "1. Хук в первом кадре: текст + движение + лицо. Без разгона.",
        "2. Ролик читается без контекста аккаунта (audition на неподписчиках).",
        "3. Колонка «кому перешлют» заполнена — иначе слот не идёт в производство.",
        "4. Петля: последний кадр стыкуется с первым.",
        "5. Все hard gates студии пройдены. Один обязательный FAIL блокирует очередь.",
        "6. AI-природа Sofia не маскируется.",
        "",
        "---",
        "Прогнозы помечены PREDICTED, измеренное — REAL. NOT_MEASURED не заменяется нулями.",
    ]
    return "\n".join(lines)


def main() -> int:
    base = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--radar", type=Path, default=base / "data" / "trend_radar.json")
    parser.add_argument("--memory", type=Path, default=base / "data" / "growth_memory.json")
    parser.add_argument("--days", type=int, default=14, help="горизонт плана в днях")
    parser.add_argument("--start", type=dt.date.fromisoformat, default=dt.date.today(),
                        help="дата начала, YYYY-MM-DD")
    parser.add_argument("--out", type=Path, help="куда записать план")
    args = parser.parse_args()

    text = build(args)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.out.with_suffix(args.out.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(args.out)
        print(f"Записано: {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
