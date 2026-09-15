#!/usr/bin/env python3
"""Export the Agent and Workflow registries from the *live* registry.

These files are generated, never hand-maintained, so the documented team can
never drift from the team that actually exists.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sofia.agents.base import Capability
from sofia.core.checkpoint import pipeline_stages
from sofia.reel.critics import FINAL_GATE_CATEGORIES
from sofia.reel.repair_router import ROUTES
from sofia.reel.shots import PROFILES
from sofia.studio import build_studio
from sofia.voice.contracts import Language
from sofia.voice.corpus import coverage
from sofia.voice.critics import CRITICAL_VOICE_GATES

OUT = Path(__file__).resolve().parents[1] / "sofia" / "registry"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        studio = build_studio(tmp)
        registry = studio.factory.registry

        agents = {
            "generated_by": "scripts/export_registries.py",
            "note": (
                "Generated from the live AgentRegistry. 'executable' means the "
                "role has an implementation the runner can invoke; a role "
                "without one is spec-only and cannot be routed to."
            ),
            "total": len(registry),
            "executing": registry.executing(),
            "spec_only": registry.spec_only(),
            "teams": {
                team: [s.to_dict() for s in registry.team(team)]
                for team in sorted({s.team for s in registry})
            },
            "capabilities": {
                cap.value: [s.name for s in registry.providers(cap)]
                for cap in Capability
            },
        }
        (OUT / "AGENT_REGISTRY.json").write_text(
            json.dumps(agents, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        workflows = {
            "generated_by": "scripts/export_registries.py",
            "workflows": {
                "voice_clip": {
                    "owner": "VoiceDirector",
                    "steps": [
                        "VoiceDirector.brief",
                        "VoiceGenerator.generate",
                        "PronunciationCritic.review",
                        "VoiceIdentityCritic.review",
                        "ProsodyCritic.review",
                        "SemanticCritic.review",
                        "VoiceRepairAgent.plan (targeted)",
                        "re-verify",
                    ],
                    "critical_gates": list(CRITICAL_VOICE_GATES),
                    "fail_closed": True,
                    "outcomes": ["PASS", "REPAIR", "HOLD", "FAIL", "BLOCKED"],
                },
                "voice_acceptance_campaign": {
                    "owner": "VoiceDirector",
                    "min_clips_per_language": 20,
                    "coverage": {
                        lang.label: coverage(lang) for lang in Language
                    },
                },
                "reel_e2e": {
                    "owner": "ReelDirector",
                    "single_owner": True,
                    "stages": [s.value for s in pipeline_stages()],
                    "pipeline": [
                        "TREND", "IDEA", "CONTENT PURPOSE", "HOOK", "SCRIPT",
                        "STORYBOARD", "SHOT LIST", "SOURCE SELECTION",
                        "VIDEO GENERATION", "VIDEO QA", "VOICE", "VOICE QA",
                        "LIP-SYNC", "LIP-SYNC QA", "EDIT", "MUSIC", "SFX",
                        "SUBTITLES", "COVER", "FINAL PERCEPTUAL QA",
                        "APPROVAL", "QUEUE",
                    ],
                    "final_gate_categories": list(FINAL_GATE_CATEGORIES),
                    "terminal_state_on_pass": "READY_FOR_OWNER_REVIEW",
                    "publishing": "HOLD (no publish path exists in code)",
                },
                "repair_routing": {
                    "owner": "RepairAgent",
                    "routes": {d.value: r.to_dict() for d, r in ROUTES.items()},
                },
                "shot_profiles": {
                    "owner": "ShotDirector",
                    "profiles": {k.value: v.to_dict() for k, v in PROFILES.items()},
                },
            },
        }
        (OUT / "WORKFLOW_REGISTRY.json").write_text(
            json.dumps(workflows, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(f"wrote {OUT/'AGENT_REGISTRY.json'}")
    print(f"wrote {OUT/'WORKFLOW_REGISTRY.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
