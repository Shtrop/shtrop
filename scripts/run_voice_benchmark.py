#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Voice acceptance campaign for RU / UA / EN.

    python scripts/run_voice_benchmark.py --workdir <dir> --config config/studio.json

On the studio machine this measures the real Sofia voice. With ``--devkit`` it
runs the same harness on procedural audio, which proves the campaign machinery
without ever claiming a Sofia voice: identity and pronunciation stay
unverifiable, so no clip can pass.

A campaign reports rates only if at least 20 clips actually reached
verification and none was BLOCKED. Otherwise the rates are ``null`` — never
zero, never a pass.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sofia.voice.backends import detect_backends
from sofia.voice.benchmark import MIN_CLIPS_PER_LANGUAGE, run_campaign
from sofia.voice.contracts import Language
from sofia.voice.critics import VoiceThresholds
from sofia.voice.pipeline import VoiceTeam


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--config", default="")
    ap.add_argument("--devkit", action="store_true")
    ap.add_argument("--languages", default="ru,uk,en")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    workdir = Path(args.workdir)
    if args.devkit:
        from sofia.devkit.backends import build_dev_voice_backends

        backends = build_dev_voice_backends()
    else:
        backends = detect_backends(args.config or None)

    team = VoiceTeam(backends, workdir, thresholds=VoiceThresholds())
    reports_dir = workdir / "reports"

    summary: dict[str, dict] = {}
    for code in args.languages.split(","):
        language = Language(code.strip())
        report = run_campaign(
            team,
            language,
            limit=args.limit or None,
            report_dir=reports_dir,
        )
        summary[language.label] = {
            "verdict": report.verdict.value,
            "clips": report.total,
            "produced": report.produced,
            "verified": report.verified,
            "measurable": report.measurable,
            "tally": {
                v.value: report.count(v)
                for v in type(report.verdict)
                if report.count(v)
            },
            "first_pass_rate": report.first_pass_rate,
            "repair_rate": report.repair_rate,
            "final_pass_rate": report.final_pass_rate,
            "mean_wer": report.mean("wer"),
            "mean_identity": report.mean("identity"),
            "wall_s": round(report.wall_s, 1),
        }

    out = reports_dir / "voice_benchmark_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{'Lang':<5} {'Verdict':<13} {'Clips':>6} {'Made':>5} {'1st':>6} {'Final':>6}  Blockers")
    print("-" * 78)
    for label, s in summary.items():
        first = "n/a" if s["first_pass_rate"] is None else f"{s['first_pass_rate']:.0%}"
        final = "n/a" if s["final_pass_rate"] is None else f"{s['final_pass_rate']:.0%}"
        note = (
            ""
            if s["measurable"]
            else (
                f"NOT MEASURABLE: {s['verified']}/{s['clips']} clips verified "
                f"(need >= {MIN_CLIPS_PER_LANGUAGE})"
            )
        )
        print(
            f"{label:<5} {s['verdict']:<13} {s['clips']:>6} {s['produced']:>5} "
            f"{first:>6} {final:>6}  {note}"
        )
    print(f"\nreports: {reports_dir}")
    return 0 if all(s["verdict"] == "PASS" for s in summary.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
