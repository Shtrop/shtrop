#!/usr/bin/env python3
"""Сборка финальных промптов фотосессий Sofia из sessions/*.json.

Источник истины — JSON-файлы сессий и common/persona_lock.json.
Скрипт НИЧЕГО не публикует и не трогает GPU: только рендерит артефакты в build/.

Выход:
  build/<slug>/BRIEF.md          — человекочитаемый бриф сессии (10 кадров)
  build/<slug>/prompts/<id>.txt  — готовый positive/negative промпт на кадр
  build/<slug>/batch.json        — плоский список задач для очереди ComfyUI
  build/INDEX.md                 — сводка по всем сессиям
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def compose_prompt(lock: dict, session: dict, shot: dict, index: int = 0) -> str:
    """Личность -> гардероб -> поза -> подача -> живая кожа -> оптика -> плёнка -> свет -> сцена -> хвосты."""
    parts = [
        lock["persona"]["identity_prompt"],
        session["wardrobe"]["prompt"],
        shot["pose"],
        session.get("allure", ""),
        lock.get("realism_tail", ""),
        shot["camera"],
        session.get("film", ""),
        shot["light"],
        # свой огрех живой съёмки на каждый кадр, по кругу
        (lock.get("camera_flaws") or [""])[index % len(lock.get("camera_flaws") or [""])],
        session["location"]["prompt"],
    ]
    if shot.get("headphones"):
        parts.insert(2, "white over-ear headphones resting around her neck")
    parts.append(lock.get("allure_tail", ""))
    parts.append(lock["quality_tail"])
    return ", ".join(p.strip().rstrip(",") for p in parts if p)


def shot_seed(session: dict, index: int) -> int:
    return session["base_seed"] + index + 1


def render_brief(lock: dict, session: dict, jobs: list[dict]) -> str:
    tech = lock["tech_defaults"]
    lines = [
        f"# {session['title_ru']} ({session['title']})",
        "",
        f"**ID сессии:** `{session['session_id']}` · **Кадров:** {len(jobs)} · "
        f"**Формат:** {session['aspect']} · **Base seed:** {session['base_seed']}",
        "",
        f"**Референс:** {session['reference_source']}",
        "",
        f"**Настроение:** {session['mood_ru']}",
        "",
        "**Подача (слой на каждом кадре):**",
        "",
        "```text",
        session.get("allure", "—"),
        "```",
        "",
        "## Гардероб (единый для всех кадров)",
        "",
        f"`{session['wardrobe']['code']}` — {session['wardrobe']['notes_ru']}",
        "",
        "```text",
        session["wardrobe"]["prompt"],
        "```",
        "",
        "## Локация",
        "",
        session["location"]["notes_ru"],
        "",
        "```text",
        session["location"]["prompt"],
        "```",
        "",
        "## Раскадровка",
        "",
        "| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |",
        "|---|------|-----|-----------------|----------|------|",
    ]
    for job in jobs:
        lines.append(
            f"| {job['id']} | {job['title_ru']} | {job['priority']} | "
            f"{job['camera'].split(',')[0]} | {'да' if job['headphones'] else '—'} | {job['seed']} |"
        )

    lines += [
        "",
        f"Наушники на шее: {sum(j['headphones'] for j in jobs)}/{len(jobs)} кадров "
        f"(канон-ориентир — {int(lock['persona']['signature_markers']['headphones_on_neck_ratio_target'] * 100)}% по всему дню, не по одной сессии).",
        "",
        "## Технический прогон",
        "",
        f"- Pipeline: {tech['pipeline']}",
        f"- Разрешение: {tech['base_resolution']}, апскейл {tech['upscale']}",
        f"- Steps {tech['steps']}, guidance {tech['guidance']}, sampler `{tech['sampler']}`",
        f"- Плёнка сессии: {session.get('film', '—')}",
        "- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно",
        f"- LoRA `{tech['lora_weight']}`, PuLID `{tech['pulid_weight']}` — подставить из persona config",
        f"- Seed: {tech['seed_policy']}; по {tech['batch_per_shot']} варианта на кадр",
        f"- GPU: {tech['gpu']}",
        "",
        "## Промпты по кадрам",
        "",
    ]
    for job in jobs:
        lines += [
            f"### {job['id']} — {job['title_ru']}",
            "",
            f"*{job['priority']} · seed {job['seed']}*",
            "",
            "```text",
            job["prompt"],
            "```",
            "",
        ]
    return "\n".join(lines)


def build_session(lock: dict, session: dict) -> list[dict]:
    out_dir = BUILD / session["slug"]
    prompts_dir = out_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    jobs = []
    for index, shot in enumerate(session["shots"]):
        job = {
            "id": shot["id"],
            "title_ru": shot["title_ru"],
            "priority": shot["priority"],
            "camera": shot["camera"],
            "headphones": bool(shot.get("headphones")),
            "seed": shot_seed(session, index),
            "prompt": compose_prompt(lock, session, shot, index),
            "negative_prompt": lock["negative_prompt"],
            "width": int(lock["tech_defaults"]["base_resolution"].split("x")[0]),
            "height": int(lock["tech_defaults"]["base_resolution"].split("x")[1]),
            "steps": lock["tech_defaults"]["steps"],
            "guidance": lock["tech_defaults"]["guidance"],
            "batch": lock["tech_defaults"]["batch_per_shot"],
        }
        # Хиро-кадры получают больше вариантов сида под отбор.
        if job["priority"] == "hero":
            job["batch"] = lock["tech_defaults"]["batch_per_shot"] * 2
        jobs.append(job)

        (prompts_dir / f"{job['id']}.txt").write_text(
            f"# {job['id']} — {job['title_ru']} (seed {job['seed']})\n\n"
            f"POSITIVE:\n{job['prompt']}\n\n"
            f"NEGATIVE:\n{job['negative_prompt']}\n",
            encoding="utf-8",
        )

    (out_dir / "batch.json").write_text(
        json.dumps(
            {
                "session_id": session["session_id"],
                "slug": session["slug"],
                "aspect": session["aspect"],
                "publish": False,
                "mode": "local-only",
                "jobs": jobs,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "BRIEF.md").write_text(render_brief(lock, session, jobs), encoding="utf-8")
    return jobs


def main() -> None:
    lock = load(ROOT / "common" / "persona_lock.json")
    index_lines = [
        "# Сборка фотосессий Sofia",
        "",
        "Сгенерировано `tools/build_prompts.py` из `sessions/*.json`. Редактировать надо исходные JSON, а не этот каталог.",
        "",
        "| Сессия | Наряд | Кадров | Hero | Каталог |",
        "|--------|-------|--------|------|---------|",
    ]
    total = 0
    for path in sorted((ROOT / "sessions").glob("*.json")):
        session = load(path)
        jobs = build_session(lock, session)
        total += len(jobs)
        heroes = sum(j["priority"] == "hero" for j in jobs)
        index_lines.append(
            f"| `{session['session_id']}` {session['title_ru']} | {session['wardrobe']['code']} | "
            f"{len(jobs)} | {heroes} | [`{session['slug']}/`]({session['slug']}/BRIEF.md) |"
        )
        print(f"{session['session_id']}: {len(jobs)} кадров -> build/{session['slug']}/")

    index_lines += ["", f"**Всего кадров: {total}.** Режим `local-only`, публикация выключена."]
    (BUILD / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Итого {total} кадров. Индекс: build/INDEX.md")


if __name__ == "__main__":
    main()
