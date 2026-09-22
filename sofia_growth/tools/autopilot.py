#!/usr/bin/env python3
"""Автопилот Growth Engine: прогон цикла без участия человека.

Запускается планировщиком на машине студии. Делает то же, что владелец делал
бы руками раз в неделю, и оставляет след, по которому видно, отработал ли он.

Что делает:
  1. Прогоняет недельный цикл (блокеры, Insights, KPI, память, бэклог, план).
  2. Пишет полный отчёт локально — там реальные метрики аккаунта.
  3. Пишет операционный статус без метрик аудитории: стадии, вердикт блокеров,
     сколько Reels опубликовано и сколько файлов вне формата.
  4. Ведёт журнал прогонов, чтобы тихий сбой был виден.
  5. По флагу --push отправляет в ветку только безопасные артефакты.

Чего НЕ делает никогда: не публикует в соцсети, не снимает HOLD и FROZEN,
не трогает canonical state студии, ничего не удаляет. Публикация остаётся
решением владельца — автопилот её не касается.

Пример (планировщик):
    python autopilot.py --studio "D:\\AI_CONTENT\\Sofia" ^
        --media-dir "D:\\AI_CONTENT\\Sofia\\video_ready" --push
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _console import force_utf8, run_tool  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
TOOLS = BASE / "tools"

STAGE_PATTERN = re.compile(r"\[(OK|SKIPPED|BLOCKED|FAILED)\]\s+([^\n—]+)")
VERDICT_PATTERN = re.compile(r"ВЕРДИКТ:\s*(\w+)")
REELS_PATTERN = re.compile(r"Reels опубликовано\s+(\d+)")
REELS_TOTAL_PATTERN = re.compile(r"Reels в очереди\s+(\d+)")
RATIO_PATTERN = re.compile(r"Вне соотношения\s+(\d+)")
RESOLUTION_PATTERN = re.compile(r"Ниже минимума ширины\s+(\d+)")

# Метрики аудитории из операционного статуса исключены: репозиторий может
# быть публичным, а охват и подписчики — данные аккаунта, не операционные.
def first_int(pattern: re.Pattern, text: str) -> int | None:
    match = pattern.search(text)
    return int(match.group(1)) if match else None


def run_cycle(args) -> tuple[int, str]:
    cycle_args = [str(TOOLS / "growth_cycle.py"), "--days", str(args.days),
                  "--plan-days", str(args.plan_days)]
    if args.studio:
        cycle_args += ["--studio", str(args.studio)]
    if args.media_dir:
        cycle_args += ["--media-dir", str(args.media_dir)]
    if args.account:
        cycle_args += ["--account", args.account]
    if args.blocker_history:
        cycle_args += ["--blocker-history", str(args.blocker_history)]
    if args.snapshots:
        cycle_args += ["--snapshots", str(args.snapshots)]
    if args.memory:
        cycle_args += ["--memory", str(args.memory)]
    result = run_tool(cycle_args)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def extract_status(output: str) -> dict:
    stages = {name.strip(): state for state, name in STAGE_PATTERN.findall(output)}
    verdict = VERDICT_PATTERN.search(output)
    return {
        "stages": stages,
        "blockers_verdict": verdict.group(1) if verdict else "NOT_MEASURED",
        "reels_published": first_int(REELS_PATTERN, output),
        "reels_queued": first_int(REELS_TOTAL_PATTERN, output),
        "media_ratio_violations": first_int(RATIO_PATTERN, output),
        "media_resolution_violations": first_int(RESOLUTION_PATTERN, output),
        "cycle_reported_failure": "[FAILED]" in output,
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def append_log(path: Path, entry: dict, keep: int = 60) -> None:
    log = {"schema_version": "1.0", "runs": []}
    if path.exists():
        try:
            log = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"WARN: {path} повреждён, журнал начат заново", file=sys.stderr)
    log.setdefault("runs", []).append(entry)
    log["runs"] = log["runs"][-keep:]
    atomic_write(path, json.dumps(log, ensure_ascii=False, indent=2))


def git(args: list[str]) -> tuple[int, str]:
    import subprocess
    result = subprocess.run(["git", "-C", str(BASE.parent), *args],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def push_safe_artifacts(status_path: Path, branch: str) -> str:
    """Отправляет только безопасные артефакты: статус, план, радар.

    Полный отчёт KPI не коммитится: в нём реальные метрики аккаунта, а
    репозиторий может быть публичным.
    """
    paths = [str(status_path.relative_to(BASE.parent)),
             "sofia_growth/plans", "sofia_growth/data/trend_radar.json"]
    code, out = git(["add", *paths])
    if code != 0:
        return f"git add не прошёл: {out.strip()[:200]}"
    code, out = git(["diff", "--cached", "--quiet"])
    if code == 0:
        return "нечего коммитить: изменений нет"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    code, out = git(["-c", "user.name=Sofia Autopilot",
                     "-c", "user.email=noreply@anthropic.com",
                     "commit", "-m", f"Autopilot: прогон цикла {stamp}"])
    if code != 0:
        return f"commit не прошёл: {out.strip()[:200]}"
    code, out = git(["push", "origin", branch])
    return "запушено" if code == 0 else f"push не прошёл: {out.strip()[:200]}"


def main() -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, help="корень студии")
    parser.add_argument("--media-dir", type=Path, help="каталог готового медиа")
    parser.add_argument("--account", default="", help="handle аккаунта")
    parser.add_argument("--days", type=int, default=0, help="окно KPI; 0 — весь диапазон")
    parser.add_argument("--plan-days", type=int, default=14)
    parser.add_argument("--report-dir", type=Path, default=BASE / "reports" / "autopilot",
                        help="куда класть полный отчёт (остаётся локальным)")
    parser.add_argument("--status", type=Path, default=BASE / "data" / "autopilot_status.json")
    parser.add_argument("--blocker-history", type=Path,
                        default=BASE / "data" / "blocker_status.json",
                        help="где хранить историю состояния блокеров")
    parser.add_argument("--snapshots", type=Path, help="файл снимков аккаунта")
    parser.add_argument("--memory", type=Path, help="файл growth memory")
    parser.add_argument("--log", type=Path, default=BASE / "data" / "autopilot_log.json")
    parser.add_argument("--push", action="store_true",
                        help="отправить безопасные артефакты в ветку")
    parser.add_argument("--branch", default="claude/fervent-ramanujan-ey6m7b")
    args = parser.parse_args()

    started = dt.datetime.now(dt.timezone.utc)
    print(f"=== Автопилот Growth Engine · {started.isoformat(timespec='seconds')} ===\n")

    code, output = run_cycle(args)
    print(output.rstrip())

    status = extract_status(output)
    status["measured_at"] = started.isoformat(timespec="seconds")
    status["cycle_exit_code"] = code
    status["studio_reachable"] = bool(args.studio and args.studio.exists())

    report_path = args.report_dir / f"cycle_{started.strftime('%Y-%m-%d_%H%M')}.md"
    atomic_write(report_path, output)
    atomic_write(args.status, json.dumps(status, ensure_ascii=False, indent=2))

    entry = {"started_at": status["measured_at"], "exit_code": code,
             "blockers_verdict": status["blockers_verdict"],
             "failed_stage": status["cycle_reported_failure"],
             "report": str(report_path)}
    if args.push:
        entry["push"] = push_safe_artifacts(args.status, args.branch)
        print(f"\nPush: {entry['push']}")
    append_log(args.log, entry)

    print(f"\nОтчёт: {report_path}")
    print(f"Статус: {args.status}")
    print(f"Журнал прогонов: {args.log}")
    print(f"Вердикт блокеров: {status['blockers_verdict']}")

    if status["cycle_reported_failure"]:
        print("\nВНИМАНИЕ: стадия цикла завершилась ошибкой — смотреть отчёт.")
        return 2
    return 0 if code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
