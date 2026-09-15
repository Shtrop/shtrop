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
from sofia.voice.benchmark import (
    MIN_CLIPS_PER_LANGUAGE,
    run_campaign,
    run_cross_language,
)
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
    reports: dict[Language, object] = {}
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
        reports[language] = report

    # One Sofia across languages: each language matching its own voiceprint is
    # not enough, so compare clips against the other languages' references.
    # Only compare pairs whose both languages were actually run, so
    # `--languages ru` is not judged against pairs that never had clips.
    from sofia.voice.benchmark import DEFAULT_PAIRS

    pairs = tuple(
        (a, b) for a, b in DEFAULT_PAIRS if a in reports and b in reports
    )
    cross = run_cross_language(team, reports, pairs=pairs, report_dir=reports_dir)

    out = reports_dir / "voice_benchmark_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {"languages": summary, "cross_language": cross.to_dict()},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

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
    print(f"\nCROSS-LANGUAGE IDENTITY: {cross.verdict.value}")
    if cross.results:
        # Show the worst result per pair: printing the first clip's verdict can
        # otherwise display PASS under a FAIL header.
        from sofia.core.gates import worst

        by_pair: dict[str, list] = {}
        for r in cross.results:
            by_pair.setdefault(r.name.split("#")[0].rsplit(".", 1)[-1], []).append(r)
        for pair, results in by_pair.items():
            verdict = worst([r.verdict for r in results])
            reason = next(
                (r.reason for r in results if r.verdict is verdict), ""
            )
            print(f"  {pair:<8} {verdict.value:<13} {reason[:70]}")
    elif pairs:
        print("  no pairs could be compared")
    else:
        print("  only one language was run; no pair to compare")

    print(f"\nreports: {reports_dir}")
    all_pass = all(s["verdict"] == "PASS" for s in summary.values())
    # Cross-language identity only gates the run when there was a pair to
    # compare. Running a single language is not a cross-language failure.
    cross_ok = (not pairs) or cross.verdict.value == "PASS"
    return 0 if all_pass and cross_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
