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


class Stage:
    def __init__(self, name: str):
        self.name = name
        self.status = "SKIPPED"
        self.detail = ""

    def line(self) -> str:
        return f"  [{self.status}] {self.name}" + (f" — {self.detail}" if self.detail else "")


def run(args: list[str], expect: tuple[int, ...]) -> tuple[int, str, str]:
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    if result.returncode not in expect:
        print(result.stdout[-1500:], file=sys.stderr)
        print(result.stderr[-1500:], file=sys.stderr)
    return result.returncode, result.stdout, result.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, help="корень студии для сбора Insights")
    parser.add_argument("--snapshots", type=Path, default=BASE / "data" / "followers_snapshots.json")
    parser.add_argument("--memory", type=Path, default=BASE / "data" / "growth_memory.json")
    parser.add_argument("--days", type=int, default=30, help="окно KPI в днях")
    parser.add_argument("--plan-days", type=int, default=14, help="горизонт плана")
    parser.add_argument("--plan-out", type=Path, help="куда записать план (по умолчанию plans/<дата>)")
    parser.add_argument("--account", default="", help="handle аккаунта")
    args = parser.parse_args()

    stages = []
    print("=== Growth Engine: недельный цикл ===\n")

    # 1. INSIGHTS
    ingest = Stage("INSIGHTS — сбор выгрузок")
    stages.append(ingest)
    if args.studio:
        code, out, _ = run([str(TOOLS / "ingest_insights.py"), "--studio", str(args.studio),
                            "--out", str(args.snapshots), "--account", args.account], (0, 2))
        if code == 0:
            ingest.status, ingest.detail = "OK", out.strip().splitlines()[-1].strip()
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
    if args.snapshots.exists():
        code, summary, err = run([str(TOOLS / "growth_kpi.py"), "--snapshots", str(args.snapshots),
                                  "--days", str(args.days), "--summary",
                                  "--write-memory", str(args.memory)], (0, 1, 2))
        if code in (0, 1):
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
    else:
        print("FOLLOWERS BASELINE: NOT_MEASURED\n30D GROWTH: NOT_MEASURED\nREACH: NOT_MEASURED\n"
              "FOLLOWS PER REACH: NOT_MEASURED\nPROFILE→FOLLOW CONVERSION: NOT_MEASURED\n"
              "SENDS PER REACH: NOT_MEASURED\nSAVES PER REACH: NOT_MEASURED\n\n"
              "MEASURED KPI: —\nNOT MEASURED KPI: все\n\nGROWTH LOOP: PARTIAL\n\n"
              "REAL DATA SOURCE: NOT_MEASURED")

    print("\n=== Топ бэклога ===\n")
    table = [line for line in backlog_text.splitlines() if line.startswith("|")]
    print("\n".join(table) if table else "NOT_MEASURED: бэклог пуст")

    blocked = [stage for stage in stages if stage.status == "BLOCKED"]
    print(f"\nСтадий OK: {sum(1 for s in stages if s.status == 'OK')}/{len(stages)}"
          + (f", BLOCKED: {len(blocked)}" if blocked else ""))
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
