#!/usr/bin/env python3
"""Расчёт KPI роста подписчиков Sofia по фактическим снимкам аккаунта.

Только чтение. Скрипт не ходит в Instagram, не публикует и не пишет в
canonical state студии. Он считает KPI из снимков, которые выгрузил
analytics-контур, и честно помечает отсутствующие данные как NOT_MEASURED.

Правило: отсутствующая метрика никогда не превращается в 0.

Пример:
    python3 sofia_growth/tools/growth_kpi.py --snapshots sofia_growth/data/followers_snapshots.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

NOT_MEASURED = "NOT_MEASURED"

# Ориентиры 2026 из открытых источников (не из аккаунта Sofia).
SENDS_PER_REACH_STRONG = 0.01   # 1% — сильный показатель
SENDS_PER_REACH_VIRAL = 0.03    # 3%+ — разнос через DM
# Реалистичный таймлайн: 1k за 60-90 дней при работающем цикле.
TARGET_MILESTONES = (1000, 10000, 50000)


def load_snapshots(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"BLOCKED: файл снимков не найден: {path}\n"
                 f"Выгрузить его из analytics-контура студии или заполнить по шаблону "
                 f"followers_snapshots.template.json. Без реальных данных KPI = NOT_MEASURED.")
    except json.JSONDecodeError as exc:
        sys.exit(f"FAIL: некорректный JSON в {path}: {exc}")

    snapshots = payload.get("snapshots", payload if isinstance(payload, list) else [])
    dated = []
    for snapshot in snapshots:
        raw_date = snapshot.get("date")
        try:
            snapshot["_date"] = dt.date.fromisoformat(raw_date)
        except (TypeError, ValueError):
            print(f"WARN: пропущен снимок без корректной даты: {raw_date!r}", file=sys.stderr)
            continue
        dated.append(snapshot)
    dated.sort(key=lambda item: item["_date"])
    return dated


def window(snapshots: list[dict], days: int) -> list[dict]:
    if not snapshots:
        return []
    last = snapshots[-1]["_date"]
    cutoff = last - dt.timedelta(days=days)
    return [item for item in snapshots if item["_date"] >= cutoff]


def total(snapshots: list[dict], field: str) -> float | None:
    values = [item[field] for item in snapshots if isinstance(item.get(field), (int, float))]
    return sum(values) if values else None


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or not denominator:
        return None
    return numerator / denominator


def fmt(value: float | None, suffix: str = "", digits: int = 2) -> str:
    return NOT_MEASURED if value is None else f"{round(value, digits)}{suffix}"


def follower_growth(snapshots: list[dict]) -> tuple[float | None, float | None]:
    """Возвращает (чистый прирост за окно, прирост в день)."""
    points = [item for item in snapshots if isinstance(item.get("followers"), (int, float))]
    if len(points) < 2:
        return None, None
    delta = points[-1]["followers"] - points[0]["followers"]
    span = (points[-1]["_date"] - points[0]["_date"]).days
    return delta, (delta / span if span else None)


def eta_days(current: float | None, per_day: float | None, target: int) -> str:
    if current is None or per_day is None or per_day <= 0:
        return NOT_MEASURED
    if current >= target:
        return "достигнуто"
    return f"~{round((target - current) / per_day)} дн. (PREDICTED)"


def verdict_for_sends(value: float | None) -> str:
    if value is None:
        return NOT_MEASURED
    if value >= SENDS_PER_REACH_VIRAL:
        return "PASS (вирусный разнос через DM)"
    if value >= SENDS_PER_REACH_STRONG:
        return "PASS (сильно)"
    return "WARN (ниже ориентира 1%)"


def report(snapshots: list[dict], days: int) -> tuple[str, int]:
    if not snapshots:
        return ("# KPI роста Sofia\n\nВердикт: NOT_MEASURED — валидных снимков нет.\n"
                "Ни одну метрику нельзя посчитать; нули подставлять нельзя.\n"), 2

    recent = window(snapshots, days)
    latest = snapshots[-1]
    followers = latest.get("followers") if isinstance(latest.get("followers"), (int, float)) else None

    net, per_day = follower_growth(recent)
    reach = total(recent, "reach")
    sends = total(recent, "sends")
    saves = total(recent, "saves")
    visits = total(recent, "profile_visits")
    follows = total(recent, "follows")

    sends_per_reach = ratio(sends, reach)
    saves_per_reach = ratio(saves, reach)
    follows_per_1k_reach = ratio(follows, reach)
    follows_per_1k_reach = follows_per_1k_reach * 1000 if follows_per_1k_reach is not None else None
    follow_rate_from_visits = ratio(follows, visits)

    measured = [net, reach, sends, saves, visits, follows]
    known = sum(1 for value in measured if value is not None)

    lines = [
        "# KPI роста Sofia",
        "",
        f"Окно: {days} дн. | последний снимок: {latest['_date'].isoformat()} | "
        f"снимков в окне: {len(recent)}",
        f"Покрытие данными: {known}/{len(measured)} метрик.",
        "",
        "| Метрика | Значение | Метка | Комментарий |",
        "|---|---|---|---|",
        f"| Подписчиков сейчас | {fmt(followers, digits=0)} | "
        f"{'REAL' if followers is not None else NOT_MEASURED} | из снимка аккаунта |",
        f"| Чистый прирост за окно | {fmt(net, digits=0)} | "
        f"{'REAL' if net is not None else NOT_MEASURED} | followers[последний] - followers[первый] |",
        f"| Прирост в день | {fmt(per_day)} | "
        f"{'REAL' if per_day is not None else NOT_MEASURED} | основной индикатор цикла |",
        f"| Follows на 1k охвата | {fmt(follows_per_1k_reach)} | "
        f"{'REAL' if follows_per_1k_reach is not None else NOT_MEASURED} | конверсия охвата в подписку |",
        f"| Follows / профильный визит | {fmt(follow_rate_from_visits)} | "
        f"{'REAL' if follow_rate_from_visits is not None else NOT_MEASURED} | качество профиля и шапки |",
        f"| Sends per reach | {fmt(sends_per_reach, digits=4)} | "
        f"{'REAL' if sends_per_reach is not None else NOT_MEASURED} | {verdict_for_sends(sends_per_reach)} |",
        f"| Saves per reach | {fmt(saves_per_reach, digits=4)} | "
        f"{'REAL' if saves_per_reach is not None else NOT_MEASURED} | сохранения тянут возвраты |",
        f"| Охват за окно | {fmt(reach, digits=0)} | "
        f"{'REAL' if reach is not None else NOT_MEASURED} | знаменатель всех ratio |",
        "",
        "## Прогноз по вехам (PREDICTED, при текущем темпе)",
        "",
        "| Веха | Оценка |",
        "|---|---|",
    ]
    for milestone in TARGET_MILESTONES:
        lines.append(f"| {milestone} подписчиков | {eta_days(followers, per_day, milestone)} |")

    lines += [
        "",
        "## Узкое место",
        "",
        bottleneck(follows_per_1k_reach, sends_per_reach, reach, follow_rate_from_visits),
        "",
        "---",
        "REAL — из снимков аккаунта. PREDICTED — расчёт по текущему темпу, не обещание.",
        "Отсутствующие данные показаны как NOT_MEASURED и не заменяются нулями.",
    ]

    exit_code = 0 if known == len(measured) else (1 if known else 2)
    return "\n".join(lines), exit_code


def bottleneck(follows_per_1k: float | None, sends_per_reach: float | None,
               reach: float | None, follow_from_visits: float | None) -> str:
    """Называет самый вероятный ограничитель роста по имеющимся данным."""
    if reach is None and follows_per_1k is None:
        return f"{NOT_MEASURED}: без охвата и конверсии узкое место не определяется."
    if sends_per_reach is not None and sends_per_reach < SENDS_PER_REACH_STRONG:
        return ("Дистрибуция: sends per reach ниже 1%. Охват вне подписчиков ограничен на входе — "
                "работать над «переслать другу», а не над частотой постинга.")
    if follow_from_visits is not None and follow_from_visits < 0.1:
        return ("Конверсия профиля: люди доходят до профиля, но не подписываются. "
                "Узкое место — шапка, закреплённые Reels и обещание аккаунта, а не контент ленты.")
    if follows_per_1k is not None and follows_per_1k < 5:
        return ("Релевантность: охват есть, подписок с него мало. Контент собирает случайную "
                "аудиторию — сузить тему и усилить повторяемость персоны.")
    return "Явного узкого места по имеющимся метрикам не видно; расширять то, что уже работает."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--snapshots", type=Path, default=base / "data" / "followers_snapshots.json")
    parser.add_argument("--days", type=int, default=14, help="окно расчёта в днях")
    parser.add_argument("--out", type=Path, help="записать отчёт в файл (создаёт, не удаляет)")
    args = parser.parse_args()

    snapshots = load_snapshots(args.snapshots)
    text, code = report(snapshots, args.days)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.out.with_suffix(args.out.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(args.out)
        print(f"Записано: {args.out}")
    else:
        print(text)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
