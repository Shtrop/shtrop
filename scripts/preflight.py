#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Readiness preflight.

Answers one question honestly: *what can this machine actually measure?*

Run it on the studio machine before a production pass. Anything it reports as
missing is not a warning to note and move past — it is a gate that will block,
by design.

    python scripts/preflight.py --config config/studio.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sofia.reel.backends import detect_reel_backends
from sofia.reel.gpu import GpuArbiter, WorkClass
from sofia.reel.measurements import contract as measurement_contract
from sofia.studio import build_studio
from sofia.voice.backends import detect_backends
from sofia.voice.contracts import Language

OK = "OK"
MISSING = "MISSING"


def _row(component: str, status: str, evidence: str, impact: str) -> dict:
    return {
        "component": component,
        "status": status,
        "evidence": evidence,
        "impact": impact,
    }


def collect(config: Path | None, lock_dir: str | None) -> dict:
    cfg = {}
    if config and config.exists():
        cfg = json.loads(config.read_text(encoding="utf-8"))

    voice = detect_backends(config)
    reel = detect_reel_backends(config)
    gpu = GpuArbiter(lock_dir=lock_dir or cfg.get("lock_dir"))
    state = gpu.state()

    rows: list[dict] = []

    rows.append(
        _row(
            "GPU",
            OK if state.available else MISSING,
            state.name or state.reason,
            "heavy video and lip-sync work cannot start" if not state.available else
            f"{state.free_vram_gb:.1f} GB VRAM free"
            if state.free_vram_gb is not None else "available",
        )
    )
    locks = gpu.active_production_locks()
    rows.append(
        _row(
            "Production locks",
            OK if not locks else "BUSY",
            ", ".join(locks) or "none held",
            "heavy work waits for production" if locks else "heavy work may start",
        )
    )

    rows.append(
        _row("TTS (XTTS)", OK if voice.tts.available() else MISSING, voice.tts.name,
             "voice generation is BLOCKED" if not voice.tts.available() else "can synthesise")
    )
    rows.append(
        _row("ASR", OK if voice.asr.available() else MISSING, voice.asr.name,
             "pronunciation + semantic gates report NOT_MEASURED and block"
             if not voice.asr.available() else "WER and semantics verifiable")
    )
    rows.append(
        _row("Speaker embedding", OK if voice.speaker.available() else MISSING,
             voice.speaker.name,
             "voice identity reports NOT_MEASURED and blocks"
             if not voice.speaker.available() else "identity verifiable")
    )
    for lang in Language:
        vp = voice.voiceprint(lang)
        rows.append(
            _row(
                f"Sofia voiceprint {lang.label}",
                OK if vp.available else MISSING,
                f"{len(vp.reference_clips)} reference clip(s)"
                + (f", embedding {vp.embedding_path}" if vp.embedding_path else ""),
                "identity FAILS: a generic fallback voice is not Sofia"
                if vp.is_generic_fallback else "canonical Sofia reference present",
            )
        )

    rows.append(
        _row("Video (ComfyUI)", OK if reel.video.available() else MISSING,
             reel.video.name,
             "shots cannot be rendered" if not reel.video.available() else "can render")
    )
    rows.append(
        _row("Lip-sync champion", OK if reel.lipsync.available() else MISSING,
             reel.lipsync.name,
             "talking shots cannot be synced or verified"
             if not reel.lipsync.available() else "can sync")
    )
    rows.append(
        _row("Editor (ffmpeg)", OK if reel.editor.available() else MISSING,
             reel.editor.name,
             "edit, cover and decode gate all block"
             if not reel.editor.available() else "can assemble and probe")
    )
    for name, backend in reel.challengers.items():
        rows.append(
            _row(f"Lip-sync challenger: {name}",
                 OK if backend.available() else MISSING, backend.name,
                 "challenger only; never replaces the champion untested")
        )

    refs = cfg.get("sofia_references", {})
    present = {k: v for k, v in refs.items() if v and Path(v).exists()}
    rows.append(
        _row("Sofia face references", OK if present else MISSING,
             f"{len(present)}/{len(refs)} registered paths exist",
             "face-critical shots cannot be sourced" if not present else "can source")
    )

    for work in WorkClass:
        ok, reason = gpu.may_run(work)
        rows.append(_row(f"May run {work.value}", OK if ok else "WAIT", reason,
                         "" if ok else "blocked right now"))

    blockers = [r for r in rows if r["status"] == MISSING]
    return {
        "rows": rows,
        "blockers": [r["component"] for r in blockers],
        "ready_for_production_reel": not blockers,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="")
    ap.add_argument("--lock-dir", default="")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--measurement-contract",
        action="store_true",
        help="print what a video / lip-sync backend must attach to each shot",
    )
    args = ap.parse_args()

    if args.measurement_contract:
        contract = measurement_contract()
        if args.json:
            print(json.dumps(contract, ensure_ascii=False, indent=2))
            return 0
        print(
            "Attach these to Shot.measurements. A gate whose numbers never "
            "arrive is NOT_MEASURED and blocks:\n"
        )
        for gate in ("video", "lipsync"):
            print(f"  {gate}:")
            for name, why in contract[gate].items():
                lower = " (lower is better)" if name in contract["lower_is_better"] else ""
                print(f"    {name}{lower}")
                print(f"        {why}")
            print()
        return 0

    config = Path(args.config) if args.config else None
    report = collect(config, args.lock_dir or None)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ready_for_production_reel"] else 1

    width = max(len(r["component"]) for r in report["rows"])
    print(f"{'Component'.ljust(width)}  Status   Evidence")
    print("-" * (width + 60))
    for r in report["rows"]:
        print(f"{r['component'].ljust(width)}  {r['status']:<7}  {r['evidence']}")
        if r["status"] != OK and r["impact"]:
            print(f"{' ' * width}           -> {r['impact']}")

    print()
    if report["ready_for_production_reel"]:
        print("READY: every verifier this pipeline needs is present.")
        return 0
    print(f"NOT READY: {len(report['blockers'])} blocker(s):")
    for b in report["blockers"]:
        print(f"  - {b}")
    print()
    print("These are gates, not warnings. A Reel produced now cannot reach PASS.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
