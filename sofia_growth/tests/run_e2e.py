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

        print(f"\n=== 5. NEXT DECISION → CONTENT PLAN ===")
        plan_blind = work / "plan_blind.md"
        plan_informed = work / "plan_informed.md"
        run([str(TOOLS / "plan_builder.py"), "--memory", str(work / "no_memory.json"),
             "--days", "14", "--start", "2026-09-16", "--out", str(plan_blind)])
        run([str(TOOLS / "plan_builder.py"), "--memory", str(memory),
             "--days", "14", "--start", "2026-09-16", "--out", str(plan_informed)])
        blind_text = plan_blind.read_text(encoding="utf-8")
        informed_text = plan_informed.read_text(encoding="utf-8")
        check("PLAN", "REAL · SCALE" not in blind_text,
              "без замеров план целиком PREDICTED")
        check("PLAN", "REAL · SCALE" in informed_text,
              "после замеров подтверждённый формат помечен REAL")
        check("PLAN", "Исключено по данным" in informed_text
              and "this-or-that" in informed_text.split("Исключено по данным")[1],
              "формат с вердиктом DROP исключён из слотов с указанием причины")
        slots = informed_text.split("## Гипотезы")[0]
        check("PLAN", "this-or-that" not in slots, "DROP-формат не попал ни в один слот")
        check("PLAN", "1325 подписчиков" in informed_text,
              "baseline из памяти подставлен в критерии плана")

        print(f"\n=== 6. Полный цикл одной командой ===")
        cycle_snapshots = work / "cycle_snapshots.json"
        cycle_memory = work / "cycle_memory.json"
        cycle_plan = work / "cycle_plan.md"
        result = run([str(TOOLS / "growth_cycle.py"), "--studio", str(fixtures),
                      "--snapshots", str(cycle_snapshots), "--memory", str(cycle_memory),
                      "--plan-out", str(cycle_plan), "--account", "SYNTHETIC_TEST"], expect=(0, 1))
        check("CYCLE", result.stdout.count("[OK]") == 4, "все 4 стадии цикла прошли")
        check("CYCLE", "FOLLOWERS BASELINE: 1325" in result.stdout,
              "отчёт владельцу содержит реальный baseline")
        check("CYCLE", cycle_plan.exists() and cycle_plan.stat().st_size > 0,
              "план создан автоматически")

        print(f"\n=== 7. Цикл без данных остаётся честным ===")
        result = run([str(TOOLS / "growth_cycle.py"), "--snapshots", work / "absent.json",
                      "--memory", work / "absent_memory.json",
                      "--plan-out", str(work / "plan_nodata.md")], expect=(0, 1))
        check("NO-DATA", "[BLOCKED] KPI" in result.stdout, "стадия KPI честно помечена BLOCKED")
        check("NO-DATA", "FOLLOWERS BASELINE: NOT_MEASURED" in result.stdout,
              "без данных baseline остаётся NOT_MEASURED, а не 0")
        check("NO-DATA", "GROWTH LOOP: PARTIAL" in result.stdout,
              "цикл без данных объявлен PARTIAL, а не VERIFIED")

        print(f"\n=== 8. Теневой контур не выдаётся за реальные метрики ===")
        shadow_dir = work / "evidence" / "learning_shadow" / "analytics"
        build_fixtures(shadow_dir)
        shadow_snapshots = work / "shadow_snapshots.json"
        shadow_memory = work / "shadow_memory.json"
        result = run([str(TOOLS / "ingest_insights.py"), "--studio", str(shadow_dir),
                      "--out", str(shadow_snapshots)], expect=(3,))
        check("SHADOW", "ВНИМАНИЕ" in result.stdout and "SHADOW" in result.stdout,
              "теневой источник распознан по пути и помечен")
        shadow_payload = json.loads(shadow_snapshots.read_text(encoding="utf-8"))
        check("SHADOW", shadow_payload["evidence_label"] == "SHADOW",
              "снимок помечен SHADOW, а не REAL")

        result = run([str(TOOLS / "growth_kpi.py"), "--snapshots", str(shadow_snapshots),
                      "--days", "30", "--summary", "--write-memory", str(shadow_memory)],
                     expect=(0, 1))
        check("SHADOW", "EVIDENCE: SHADOW" in result.stdout,
              "отчёт владельцу открывается меткой EVIDENCE: SHADOW")
        check("SHADOW", "GROWTH LOOP: PARTIAL" in result.stdout,
              "цикл на теневых данных не объявляется VERIFIED")
        check("SHADOW", "REAL DATA SOURCE:\n  [SHADOW]" in result.stdout,
              "источник в отчёте помечен как теневой")

        result = run([str(TOOLS / "trend_radar.py"), "--json", "--memory", str(shadow_memory)],
                     expect=(0, 2))
        shadow_backlog = json.loads(result.stdout)["backlog"]
        check("SHADOW", all(item["evidence_label"] != "REAL" for item in shadow_backlog),
              "теневые замеры не дают метку REAL в бэклоге")
        shadow_rank = [item["id"] for item in shadow_backlog]
        check("SHADOW", shadow_rank == prior_rank,
              "порядок бэклога не изменился: теневые данные не двигают приоритет")

        shadow_plan = work / "shadow_plan.md"
        run([str(TOOLS / "plan_builder.py"), "--memory", str(shadow_memory),
             "--days", "14", "--start", "2026-09-16", "--out", str(shadow_plan)])
        shadow_text = shadow_plan.read_text(encoding="utf-8")
        check("SHADOW", "REAL · SCALE" not in shadow_text,
              "теневой вердикт не попал в план как подтверждённый")
        check("SHADOW", "Теневые замеры (на план не влияют)" in shadow_text,
              "план явно перечисляет теневые замеры отдельным разделом")
        check("SHADOW", "1325 подписчиков" not in shadow_text,
              "теневой baseline не выдаётся за реальный")

        print(f"\n=== 9. Lineage публикатора и доказательства публикации ===")
        import sqlite3
        queue = work / "queue" / "content_queue.db"
        queue.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(queue)
        connection.execute("CREATE TABLE content_items (id INTEGER, created_at TEXT, "
                           "published_at TEXT, permalink TEXT, type TEXT, status TEXT, "
                           "instagram_media_id TEXT)")
        connection.executemany("INSERT INTO content_items VALUES (?,?,?,?,?,?,?)", [
            (1, "2026-09-01", "2026-09-02", "https://example.invalid/p/AAA", "REELS",
             "published", "17874771153567012"),
            (2, "2026-09-03", None, None, "REELS", "rendered", None)])
        connection.execute("CREATE TABLE publish_attempt_journal (id INTEGER, created_at TEXT, "
                           "status TEXT, remote_post_id TEXT)")
        connection.executemany("INSERT INTO publish_attempt_journal VALUES (?,?,?,?)",
                               [(1, "2026-09-02", "succeeded", "17874771153567012"),
                                (2, "2026-09-03", "failed", None)])
        connection.commit()
        connection.close()

        queue_out = work / "queue_snapshots.json"
        run([str(TOOLS / "ingest_insights.py"), "--source", str(queue), "--out", str(queue_out)])
        queue_payload = json.loads(queue_out.read_text(encoding="utf-8"))
        ids = [post.get("media_id") for post in queue_payload["posts"]]
        check("LINEAGE", ids == ["17874771153567012"],
              "таблица публикаций без метрик даёт lineage по реальному media_id")
        check("LINEAGE", all(not key.startswith("_") for post in queue_payload["posts"]
                             for key in post),
              "служебные поля не утекают в выходной файл")

        result = run([str(TOOLS / "publish_evidence.py"), "--source", str(queue)], expect=(0,))
        check("PUBLISH", "REAL_PUBLISH_CONFIRMED" in result.stdout,
              "подтверждённая удалённая публикация распознана")

        empty_queue = work / "queue" / "empty_queue.db"
        connection = sqlite3.connect(empty_queue)
        connection.execute("CREATE TABLE content_items (id INTEGER, created_at TEXT, "
                           "published_at TEXT, permalink TEXT, status TEXT, "
                           "instagram_media_id TEXT)")
        connection.execute("INSERT INTO content_items VALUES (1,'2026-09-01',NULL,NULL,"
                           "'blocked_by_gate',NULL)")
        connection.commit()
        connection.close()
        result = run([str(TOOLS / "publish_evidence.py"), "--source", str(empty_queue)], expect=(1,))
        check("PUBLISH", "PUBLISH EVIDENCE: NOT_MEASURED" in result.stdout,
              "без удалённых публикаций вердикт NOT_MEASURED, а не ноль публикаций")

        print(f"\n=== 10. Подлинность выгрузки решается сверкой ID, а не путём ===")
        import csv as csv_module
        vroot = work / "verify"
        vshadow = vroot / "evidence" / "learning_shadow" / "analytics"
        vshadow.mkdir(parents=True)
        real_ids = [f"178747711535670{i:02d}" for i in range(12)]
        vdb = vroot / "queue" / "content_queue.db"
        vdb.parent.mkdir(parents=True)
        connection = sqlite3.connect(vdb)
        connection.execute("CREATE TABLE content_items (id INTEGER, created_at TEXT, "
                           "published_at TEXT, permalink TEXT, type TEXT, status TEXT, "
                           "instagram_media_id TEXT)")
        connection.executemany("INSERT INTO content_items VALUES (?,?,?,?,?,?,?)", [
            (i, "2026-09-01", f"2026-09-{i + 1:02d}", f"https://example.invalid/p/{i}",
             "REELS", "published", media) for i, media in enumerate(real_ids)])
        connection.commit()
        connection.close()

        genuine = vshadow / "post_insights.csv"
        with genuine.open("w", encoding="utf-8", newline="") as handle:
            writer = csv_module.DictWriter(handle, fieldnames=[
                "id", "media_type", "timestamp", "permalink", "reach", "saved", "shares"])
            writer.writeheader()
            for index, media in enumerate(real_ids):
                writer.writerow({"id": media, "media_type": "REELS",
                                 "timestamp": f"2026-09-{index + 1:02d}T04:30:46+0000",
                                 "permalink": f"https://example.invalid/p/{index}",
                                 "reach": 800 + index * 10, "saved": 9 + index,
                                 "shares": 12 + index})
        forged = vshadow / "fake_insights.csv"
        with forged.open("w", encoding="utf-8", newline="") as handle:
            writer = csv_module.DictWriter(handle, fieldnames=["id", "timestamp", "reach", "shares"])
            writer.writeheader()
            for index in range(10):
                writer.writerow({"id": f"9999{index:03d}",
                                 "timestamp": f"2026-09-{index + 1:02d}", "reach": 100, "shares": 1})

        result = run([str(TOOLS / "verify_insights.py"), "--studio", str(vroot)], expect=(0, 1))
        genuine_block = result.stdout.split("post_insights.csv")[1].split("fake_insights.csv")[0]
        check("VERIFY", "ID_MATCH_CONFIRMED" in genuine_block,
              "выгрузка с реальными media_id подтверждена сверкой, несмотря на путь shadow")
        forged_block = result.stdout.split("fake_insights.csv")[1]
        check("VERIFY", "NO_MATCH" in forged_block,
              "выгрузка с выдуманными id не проходит сверку")

        vout = work / "verified_snapshots.json"
        result = run([str(TOOLS / "ingest_insights.py"), "--source", str(genuine),
                      "--out", str(vout)], expect=(3,))
        check("TRUST", json.loads(vout.read_text(encoding="utf-8"))["evidence_label"] == "SHADOW",
              "без явного доверия файл остаётся SHADOW")
        result = run([str(TOOLS / "ingest_insights.py"), "--source", str(genuine),
                      "--out", str(vout), "--trust", str(genuine)], expect=(0,))
        verified = json.loads(vout.read_text(encoding="utf-8"))
        check("TRUST", verified["evidence_label"] == "REAL" and verified["trusted_overrides"],
              "явное доверие переводит проверенный файл в REAL и фиксирует это в файле")

        result = run([str(TOOLS / "growth_kpi.py"), "--snapshots", str(vout),
                      "--days", "30", "--summary"], expect=(0, 1))
        check("SHARES", "SENDS PER REACH: NOT_MEASURED" not in result.stdout,
              "sends per reach считается из поля shares, как его отдаёт Graph API")

        print(f"\n=== 11. Изоляция: репозиторий не загрязнён ===")
        real_snapshots = BASE / "data" / "followers_snapshots.json"
        check("ISOLATION", not real_snapshots.exists() or "SYNTHETIC" not in
              real_snapshots.read_text(encoding="utf-8"),
              "синтетика не попала в data/followers_snapshots.json")

        check("ISOLATION", not (BASE / "plans" / "CONTENT_PLAN_2026-09-16_14d.md").exists(),
              "тестовые планы не записаны в plans/")

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
