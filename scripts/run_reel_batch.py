#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reel batch benchmark: a controlled arm and a random arm.

    python scripts/run_reel_batch.py --workdir <dir> --controlled 5 --random 5

The controlled arm repeats one plan, which measures pipeline variance on
identical input. The random arm samples the plan pool, which measures
behaviour across content. One successful Reel is not repeatability; this is
what a repeatability claim would have to rest on.

Rates are reported only if every critical category was actually measured on
enough runs. Otherwise the batch is NOT_MEASURED — never 0%.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_plans import PLAN_POOL  # noqa: E402

from sofia.reel.benchmark import MIN_BATCH, run_batch  # noqa: E402
from sofia.reel.stages import AuthoredPlan  # noqa: E402
from sofia.studio import build_studio  # noqa: E402
from sofia.voice.contracts import Language  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--config", default="")
    ap.add_argument("--devkit", action="store_true")
    ap.add_argument("--controlled", type=int, default=5)
    ap.add_argument("--random", type=int, default=5)
    ap.add_argument("--seed", type=int, default=7)
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

        voice_backends = build_dev_voice_backends()
        reel_backends = build_dev_reel_backends(
            imageio_ffmpeg.get_ffmpeg_exe(), workdir
        )
        references = {"default": NOT_SOFIA}
        music = DevMusicBed()

    studio = build_studio(
        workdir,
        language=Language.RU,
        creative=AuthoredPlan(PLAN_POOL[0][1]),
        sofia_references=references,
        voice_backends=voice_backends,
        reel_backends=reel_backends,
        voice_config=args.config or None,
        reel_config=args.config or None,
    )
    studio.director.music_backend = music
    if args.devkit:
        studio.director.config.frame_width = 540
        studio.director.config.frame_height = 960

    growth = studio.growth.brief_director(
        trend="честный процесс вместо туториала по технике",
        audience="создатели коротких видео, 22-35",
        hook_hypothesis="прямой вопрос-возражение в первом кадре",
        target_kpi={"retention_3s": 0.75},
    )

    report = run_batch(
        studio.director,
        growth,
        PLAN_POOL,
        controlled=args.controlled,
        random_runs=args.random,
        diagnostic=args.devkit,
        report_dir=workdir / "reports",
        seed=args.seed,
    )

    data = report.to_dict()
    print(f"BATCH VERDICT: {data['verdict']}")
    print(f"runs: {data['runs_total']}  verified: {data['runs_verified']}")
    if not data["measurable"]:
        print(f"NOT MEASURABLE: {data['unmeasurable_reason']}")
    else:
        print(f"first-pass rate:  {data['first_pass_rate']:.0%}")
        print(f"repair rate:      {data['repair_rate']:.0%}")
        print(f"final pass rate:  {data['final_pass_rate']:.0%}")
        print(f"manual needed:    {data['manual_intervention_rate']:.0%}")

    mean_gpu = data["mean_estimated_gpu_s"]
    print(f"mean wall time:   {data['mean_wall_s']:.1f}s")
    print(
        "mean GPU (est):   "
        + (f"{mean_gpu:.0f}s" if mean_gpu is not None else "n/a")
    )
    print(
        "peak VRAM:        "
        + (
            f"{data['peak_vram_gb']:.0f} GB"
            if data["peak_vram_gb"] is not None
            else "n/a"
        )
    )
    print(f"total wall:       {data['total_wall_s']:.0f}s")
    if data["blocking_histogram"]:
        print("\nmost common blockers:")
        for name, count in list(data["blocking_histogram"].items())[:6]:
            print(f"  {count:>3}x  {name}")
    print(f"\nreport: {workdir/'reports'/'reel_batch.json'}")
    return 0 if data["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
