#!/usr/bin/env python3
"""Недельный цикл Growth Engine одной командой.

Порядок: INSIGHTS → KPI → GROWTH MEMORY → TREND BACKLOG → CONTENT PLAN → отчёт.

Каждая стадия сообщает свой статус: `OK`, `SKIPPED` или `BLOCKED`. Стадия,
оставшаяся без данных, не подменяется нулями и не прерывает цикл молча —
следующие стадии просто работают на том, что реально есть.

Ничего не публикуется, HOLD не снимается, canonical state студии не меняется.

Пример (на машине студии):
    python growth_cycle.py --studio "D:\\AI_CONTENT\\Sofia"

Пример (без доступа к студии — пересборка плана по уже собранным данным):
    python growth_cycle.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TOOLS = BASE / "tools"


sys.path.insert(0, str(Path(__file__).resolve().parent))
from _console import force_utf8, run_tool  # noqa: E402


class Stage:
    def __init__(self, name: str):
        self.name = name
        self.status = "SKIPPED"
        self.detail = ""

    def line(self) -> str:
        return f"  [{self.status}] {self.name}" + (f" — {self.detail}" if self.detail else "")


def run(args: list[str], expect: tuple[int, ...]) -> tuple[int, str, str]:
    result = run_tool(args)
    if result.returncode not in expect:
        print(result.stdout[-1500:], file=sys.stderr)
        print(result.stderr[-1500:], file=sys.stderr)
    return result.returncode, result.stdout or "", result.stderr or ""


def main() -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, help="корень студии для сбора Insights")
    parser.add_argument("--snapshots", type=Path, default=BASE / "data" / "followers_snapshots.json")
    parser.add_argument("--memory", type=Path, default=BASE / "data" / "growth_memory.json")
    parser.add_argument("--days", type=int, default=0,
                        help="окно KPI в днях; 0 (по умолчанию) — весь доступный диапазон")
    parser.add_argument("--plan-days", type=int, default=14, help="горизонт плана")
    parser.add_argument("--plan-out", type=Path, help="куда записать план (по умолчанию plans/<дата>)")
    parser.add_argument("--account", default="", help="handle аккаунта")
    parser.add_argument("--trust", type=Path, action="append", default=[],
                        help="явно доверять источнику вопреки маркерам пути")
    args = parser.parse_args()

    stages = []
    print("=== Growth Engine: недельный цикл ===\n")

    # 0. Были ли реальные публикации — от этого зависит смысл всех метрик.
    publishes = Stage("PUBLISH EVIDENCE — были ли реальные публикации")
    stages.append(publishes)
    if args.studio:
        code, out, _ = run([str(TOOLS / "publish_evidence.py"), "--studio", str(args.studio)],
                           (0, 1, 2))
        verdict = next((line.split(":", 1)[1].strip() for line in out.splitlines()
                        if line.startswith("PUBLISH EVIDENCE:")), "NOT_MEASURED")
        publishes.status = "OK" if code == 0 else "BLOCKED"
        publishes.detail = verdict
    else:
        publishes.detail = "--studio не задан"
    print(publishes.line())

    # 1. INSIGHTS
    ingest = Stage("INSIGHTS — сбор выгрузок")
    stages.append(ingest)
    if args.studio:
        ingest_args = [str(TOOLS / "ingest_insights.py"), "--studio", str(args.studio),
                       "--out", str(args.snapshots), "--account", args.account]
        for path in args.trust:
            ingest_args += ["--trust", str(path)]
        code, out, _ = run(ingest_args, (0, 2, 3))
        if code in (0, 3):
            ingest.status = "OK"
            evidence = next((line.split(":", 1)[1].strip() for line in out.splitlines()
                             if line.strip().startswith("доказательность:")), "?")
            verified = sum(1 for line in out.splitlines() if "подтверждена сверкой" in line)
            ingest.detail = f"доказательность {evidence}"
            if verified:
                ingest.detail += f", подтверждено сверкой media_id: {verified}"
        else:
            ingest.status = "BLOCKED"
            ingest.detail = "источников не найдено, снимки не перезаписаны"
    else:
        ingest.detail = "--studio не задан, используются уже собранные снимки"
    print(ingest.line())

    # 2-3. KPI + GROWTH MEMORY
    kpi = Stage("KPI + GROWTH MEMORY")
    stages.append(kpi)
    summary = ""
    kpi_error = ""
    if args.snapshots.exists():
        code, summary, err = run([str(TOOLS / "growth_kpi.py"), "--snapshots", str(args.snapshots),
                                  "--days", str(args.days), "--summary",
                                  "--write-memory", str(args.memory)], (0, 1, 2))
        if not summary.strip():
            # Молча подставить NOT_MEASURED вместо упавшего расчёта нельзя:
            # это выдало бы сбой за отсутствие данных.
            kpi.status = "FAILED"
            kpi.detail = "расчёт не дал вывода — см. ошибку ниже"
            kpi_error = (err or "").strip()
        elif code in (0, 1):
            kpi.status = "OK"
            kpi.detail = ("все KPI измерены" if code == 0 else "часть KPI NOT_MEASURED")
        else:
            kpi.status = "BLOCKED"
            kpi.detail = "валидных снимков нет"
    else:
        kpi.status = "BLOCKED"
        kpi.detail = f"нет файла {args.snapshots.name} — сначала собрать Insights"
    print(kpi.line())

    # 4. TREND BACKLOG
    radar = Stage("TREND — бэклог с учётом замеров")
    stages.append(radar)
    code, backlog_text, _ = run([str(TOOLS / "trend_radar.py"), "--memory", str(args.memory),
                                 "--top", "5"], (0, 2))
    radar.status = "OK"
    radar.detail = "радар свежий" if code == 0 else "WARN: радар устарел (>14 дн.)"
    print(radar.line())

    # 5. CONTENT PLAN
    plan = Stage("CONTENT PLAN")
    stages.append(plan)
    start = dt.date.today() + dt.timedelta(days=1)
    plan_out = args.plan_out or BASE / "plans" / f"CONTENT_PLAN_{start.isoformat()}_{args.plan_days}d.md"
    code, _, _ = run([str(TOOLS / "plan_builder.py"), "--memory", str(args.memory),
                      "--days", str(args.plan_days), "--start", start.isoformat(),
                      "--out", str(plan_out)], (0,))
    plan.status = "OK"
    plan.detail = str(plan_out.relative_to(BASE.parent) if BASE.parent in plan_out.parents else plan_out)
    print(plan.line())

    print("\n=== Отчёт владельцу ===\n")
    if summary.strip():
        print(summary.strip())
    elif kpi_error:
        print("ОТЧЁТ НЕ ПОСТРОЕН: расчёт KPI завершился ошибкой.")
        print("Подставлять NOT_MEASURED вместо упавшего расчёта нельзя — это разные вещи.")
        print("\nОшибка:")
        for line in kpi_error.splitlines()[-12:]:
            print(f"  {line}")
    else:
        print("ОТЧЁТ НЕ ПОСТРОЕН: снимков с метриками нет.")
        print("Сначала собрать Insights: tools/ingest_insights.py --studio <корень студии>.")

    print("\n=== Топ бэклога ===\n")
    table = [line for line in backlog_text.splitlines() if line.startswith("|")]
    print("\n".join(table) if table else "NOT_MEASURED: бэклог пуст")

    blocked = [stage for stage in stages if stage.status == "BLOCKED"]
    failed = [stage for stage in stages if stage.status == "FAILED"]
    print(f"\nСтадий OK: {sum(1 for s in stages if s.status == 'OK')}/{len(stages)}"
          + (f", BLOCKED: {len(blocked)}" if blocked else "")
          + (f", FAILED: {len(failed)}" if failed else ""))
    return 2 if failed else (1 if blocked else 0)


if __name__ == "__main__":
    raise SystemExit(main())
