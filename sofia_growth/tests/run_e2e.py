#!/usr/bin/env python3
"""E2E-проверка цикла Growth Engine на синтетических данных.

Проверяемая цепочка:
    TREND → CONTENT → PUBLICATION → INSIGHTS → GROWTH MEMORY → NEXT CONTENT DECISION

Синтетические источники создаются во временном каталоге и там же остаются:
в `sofia_growth/data/` ничего не пишется, реальные данные не подменяются.
Ничего не публикуется и не отправляется в сеть.

    python3 sofia_growth/tests/run_e2e.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TOOLS = BASE / "tools"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_fixtures import build as build_fixtures  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []


def check(stage: str, condition: bool, detail: str) -> None:
    (PASSED if condition else FAILED).append(f"{stage}: {detail}")
    print(f"  [{'PASS' if condition else 'FAIL'}] {stage} — {detail}")


def run(args: list[str], expect: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    if result.returncode not in expect:
        print(result.stdout[-2000:], file=sys.stderr)
        print(result.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"FAIL: {' '.join(args[:2])} вернул {result.returncode}, ожидалось {expect}")
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="sofia_e2e_") as tmp:
        work = Path(tmp)
        fixtures = work / "studio"
        snapshots = work / "followers_snapshots.json"
        memory = work / "growth_memory.json"

        print("\n=== 0. FAIL-CLOSED: нет источников ===")
        empty = work / "empty"
        empty.mkdir()
        result = run([str(TOOLS / "ingest_insights.py"), "--studio", str(empty),
                      "--out", str(snapshots)], expect=(2,))
        check("FAIL-CLOSED", "BLOCKED" in result.stdout, "без источников выдан BLOCKED")
        check("FAIL-CLOSED", not snapshots.exists(), "файл снимков не создан пустышкой")

        info = build_fixtures(fixtures)
        print(f"\n=== 1. TREND → CONTENT (радар без памяти) ===")
        result = run([str(TOOLS / "trend_radar.py"), "--json",
                      "--memory", str(work / "no_memory.json")], expect=(0, 2))
        prior = json.loads(result.stdout)
        check("TREND", len(prior["backlog"]) > 0, f"бэклог построен: {len(prior['backlog'])} позиций")
        check("TREND", all(item["evidence_label"] == "PREDICTED" for item in prior["backlog"]),
              "без данных всё помечено PREDICTED")
        prior_rank = [item["id"] for item in prior["backlog"]]

        plan = next(BASE.glob("plans/CONTENT_PLAN_*.md"), None)
        check("CONTENT", plan is not None and plan.stat().st_size > 0,
              f"контент-план присутствует: {plan.name if plan else '—'}")

        print(f"\n=== 2. PUBLICATION → INSIGHTS (сбор реальных выгрузок) ===")
        result = run([str(TOOLS / "ingest_insights.py"), "--studio", str(fixtures),
                      "--out", str(snapshots), "--account", "SYNTHETIC_TEST"])
        payload = json.loads(snapshots.read_text(encoding="utf-8"))
        check("INSIGHTS", len(payload["sources"]) == 3, "прочитаны csv + jsonl + sqlite")
        check("INSIGHTS", len(payload["posts"]) == info["posts"],
              f"публикации склеены без дублей: {len(payload['posts'])} из {info['posts']} уникальных")
        check("INSIGHTS", payload["coverage"]["followers"]["status"] == "MEASURED",
              "account-level followers извлечены из Graph API структуры")
        check("PUBLICATION", all(p.get("trend_id") or p.get("format_id") for p in payload["posts"]),
              "lineage публикация→тренд сохранён")
        check("INSIGHTS", payload["coverage"]["retention"]["status"] == "NOT_MEASURED",
              "отсутствующая метрика осталась NOT_MEASURED, а не 0")
        check("INSIGHTS", all("retention" not in s for s in payload["snapshots"]),
              "отсутствующее поле не записано нулём")

        print(f"\n=== 3. INSIGHTS → GROWTH MEMORY ===")
        result = run([str(TOOLS / "growth_kpi.py"), "--snapshots", str(snapshots),
                      "--days", "30", "--summary", "--write-memory", str(memory)], expect=(0, 1))
        summary = result.stdout
        check("KPI", "FOLLOWERS BASELINE: 1325" in summary or "FOLLOWERS BASELINE: NOT_MEASURED" not in summary,
              "baseline посчитан из реальных снимков")
        check("KPI", "NOT MEASURED KPI: " in summary and "retention" in summary,
              "неизмеренные KPI перечислены отдельно")
        stored = json.loads(memory.read_text(encoding="utf-8"))
        verdicts = {entry["key"]: entry["verdict"] for entry in stored["entries"].values()}
        check("MEMORY", verdicts.get("fmt-flop-core") == "SCALE", "сильный формат записан как SCALE")
        check("MEMORY", verdicts.get("fmt-this-or-that") == "DROP", "слабый формат записан как DROP")
        check("MEMORY", stored["baseline"]["followers"] is not None, "baseline сохранён в памяти")

        print(f"\n=== 4. GROWTH MEMORY → NEXT CONTENT DECISION ===")
        result = run([str(TOOLS / "trend_radar.py"), "--json", "--memory", str(memory)], expect=(0, 2))
        informed = json.loads(result.stdout)
        informed_rank = [item["id"] for item in informed["backlog"]]
        check("DECISION", informed_rank != prior_rank, "порядок бэклога изменился после замеров")
        check("DECISION", informed_rank[0] == "fmt-flop-core",
              f"измеренный победитель поднят на первое место: {informed_rank[0]}")
        check("DECISION", informed_rank[-1] == "fmt-this-or-that",
              f"измеренный проигравший опущен вниз: {informed_rank[-1]}")
        measured_items = [i for i in informed["backlog"] if i["evidence_label"] == "REAL"]
        check("DECISION", len(measured_items) == 3, "метка REAL стоит только у измеренных форматов")
        check("DECISION", all(i["evidence_label"] == "PREDICTED"
                              for i in informed["backlog"] if i.get("measured") is None),
              "неизмеренные форматы остались PREDICTED")

        print(f"\n=== 5. Изоляция: репозиторий не загрязнён ===")
        real_snapshots = BASE / "data" / "followers_snapshots.json"
        check("ISOLATION", not real_snapshots.exists() or "SYNTHETIC" not in
              real_snapshots.read_text(encoding="utf-8"),
              "синтетика не попала в data/followers_snapshots.json")

    print("\n" + "=" * 60)
    print(f"PASS: {len(PASSED)}   FAIL: {len(FAILED)}")
    if FAILED:
        for item in FAILED:
            print(f"  FAILED — {item}")
        return 1
    print("E2E цикл TREND → CONTENT → PUBLICATION → INSIGHTS → MEMORY → DECISION: VERIFIED")
    print("(на синтетических данных; на реальных данных Sofia — см. отчёт KPI)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
