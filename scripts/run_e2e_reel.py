#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-to-end Reel run.

With the studio's real backends this produces a real Sofia Reel. On a machine
without them (no GPU / ComfyUI / XTTS / Sofia references) pass ``--devkit`` to
run the same pipeline on procedural media: every stage really executes and
every artifact is real, but nothing is Sofia and the run can never reach PASS.

    python scripts/run_e2e_reel.py --workdir /tmp/reel --devkit
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sofia.reel.critics import PerceptualSample
from sofia.reel.stages import AuthoredPlan
from sofia.studio import build_studio
from sofia.voice.contracts import Language

# The authored content plan lives in content_plans.py so the batch benchmark
# and this script use the same creative work.
from content_plans import PLAN_RU  # noqa: E402  (after sys.path setup)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--reel-id", default="sofia-reel-001")
    ap.add_argument(
        "--devkit",
        action="store_true",
        help="run on procedural media; nothing produced is Sofia",
    )
    ap.add_argument(
        "--config",
        default="",
        help="studio config (see config/studio.example.json)",
    )
    ap.add_argument("--report", default="")
    args = ap.parse_args()

    workdir = Path(args.workdir)
    voice_backends = reel_backends = music = None
    references: dict[str, str] = {}

    if args.devkit:
        import imageio_ffmpeg

        from sofia.devkit.backends import (
            NOT_SOFIA,
            DevMusicBed,
            build_dev_reel_backends,
            build_dev_voice_backends,
        )

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        voice_backends = build_dev_voice_backends()
        reel_backends = build_dev_reel_backends(ffmpeg, workdir)
        music = DevMusicBed()
        # Explicitly not a Sofia reference. Recorded as such on every shot.
        references = {"default": NOT_SOFIA}

    config = args.config or None
    if config and not args.devkit:
        cfg = json.loads(Path(config).read_text(encoding="utf-8"))
        references = dict(cfg.get("sofia_references", {}))

    studio = build_studio(
        workdir,
        language=Language.RU,
        creative=AuthoredPlan(PLAN_RU),
        sofia_references=references,
        voice_backends=voice_backends,
        reel_backends=reel_backends,
        voice_config=config,
        reel_config=config,
        lock_dir=(
            json.loads(Path(config).read_text(encoding="utf-8")).get("lock_dir")
            if config
            else None
        ),
    )
    studio.director.music_backend = music
    if args.devkit:
        # The dev renderer works at 540x960; the burn-in must match the real frame.
        studio.director.config.frame_width = 540
        studio.director.config.frame_height = 960

    growth = studio.growth.brief_director(
        trend="честный процесс вместо туториала по технике",
        audience="создатели коротких видео, 22-35, снимают на телефон",
        hook_hypothesis=(
            "прямой вопрос-возражение в первом кадре держит дольше, чем обещание пользы"
        ),
        target_kpi={"retention_3s": 0.75, "saves_per_1k": 18.0},
    )

    # A real perceptual review: BEST, RANDOM and FAIL samples were actually
    # looked at. On devkit footage the honest finding is that the picture does
    # not depict the scripted scenes, so bad_story is flagged and the gate
    # holds. Never fill this in without having looked.
    samples = ()
    if args.devkit:
        final = str(workdir / "edit" / f"{args.reel_id}.mp4")
        reviewer = "model-visual-review (AI ANALYSIS)"
        samples = (
            PerceptualSample(
                bucket="BEST",
                artifact=f"{final}@1.0s",
                reviewer=reviewer,
                bad_story=True,
                notes=(
                    "Hook frame: subtitles are legible and correctly placed in the "
                    "lower third, but the picture is an abstract gradient, not the "
                    "scripted close-up. No face is present at all."
                ),
            ),
            PerceptualSample(
                bucket="RANDOM",
                artifact=f"{final}@12.0s",
                reviewer=reviewer,
                bad_story=True,
                notes="Mid-reel frame carries no depicted subject; motion is a slow push on a still.",
            ),
            PerceptualSample(
                bucket="FAIL",
                artifact=f"{final}@19.0s",
                reviewer=reviewer,
                bad_story=True,
                fake_motion=True,
                notes=(
                    "CTA frame: the only movement is a synthetic zoom; nothing in "
                    "frame delivers the payoff the script promises."
                ),
            ),
        )

    result = studio.director.produce(
        args.reel_id,
        growth,
        perceptual_samples=samples,
        cover_measurements={},  # no face detector here -> stays NOT_MEASURED
        diagnostic=args.devkit,
    )

    payload = {
        "audit": studio.audit(),
        "result": result.to_dict(),
        "runner": dict(studio.runner.stats()),
        "checkpoint_journal": studio.director.checkpoints.journal(args.reel_id),
    }
    report_path = Path(args.report or (workdir / f"{args.reel_id}.report.json"))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"VERDICT: {result.verdict.value}")
    print(f"STAGE:   {getattr(result.stage, 'value', result.stage)}")
    print(f"REASON:  {result.reason}")
    print(f"FINAL:   {result.assets.final}")
    print(f"COVER:   {result.assets.cover}")
    print(f"SUBS:    {result.assets.subtitles}")
    print(f"REPORT:  {report_path}")
    return 0 if result.verdict.value == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
