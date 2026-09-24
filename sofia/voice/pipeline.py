"""VoiceTeam — the seven roles wired into one fail-closed pipeline.

    VoiceDirector -> VoiceGenerator -> {Pronunciation, Identity, Prosody,
    Semantic} critics -> VoiceRepairAgent -> re-verify

A clip is PASS only when every critical gate is present and passing. Any of
these blocks: pronunciation FAIL, identity FAIL, semantic FAIL, a critical
verifier ERROR, a critical verifier MISSING. There are no advisory-only
critical gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Sequence

from sofia.agents.base import (
    AgentContext,
    AgentResult,
    AgentSpec,
    Capability,
)
from sofia.core.errors import BackendUnavailableError
from sofia.core.gates import GateReport, GateResult, evaluate_gates
from sofia.core.verdict import Verdict
from sofia.voice.backends import VoiceBackends
from sofia.voice.critics import (
    CRITICAL_VOICE_GATES,
    PronunciationCritic,
    ProsodyCritic,
    SemanticCritic,
    VoiceIdentityCritic,
    VoiceThresholds,
)
from sofia.voice.contracts import (
    Language,
    VoiceArtifact,
    VoiceBrief,
    VoiceDefect,
    VoiceDiagnosis,
    VoiceVerdict,
)
from sofia.voice.director import VoiceDirector
from sofia.voice.generator import VoiceGenerator
from sofia.voice.repair import RepairPlan, VoiceRepairAgent

TEAM = "voice"


@dataclass
class VoiceTeam:
    """Executable Sofia Voice Team."""

    backends: VoiceBackends
    workdir: Path
    thresholds: VoiceThresholds = field(default_factory=VoiceThresholds)
    max_repairs: int = 2

    def __post_init__(self) -> None:
        self.workdir = Path(self.workdir)
        self.director = VoiceDirector()
        self.generator = VoiceGenerator(self.backends, self.workdir)
        self.repair_agent = VoiceRepairAgent()
        self.pronunciation = PronunciationCritic(self.backends, self.thresholds)
        self.identity = VoiceIdentityCritic(self.backends, self.thresholds)
        self.prosody = ProsodyCritic(self.backends, self.thresholds)
        self.semantic = SemanticCritic(self.backends, self.thresholds)

    # ---- verification ----------------------------------------------------
    def verify(
        self, artifact: VoiceArtifact
    ) -> tuple[GateReport, list[VoiceDiagnosis]]:
        """Run all four critics and aggregate fail-closed."""

        results: list[GateResult] = []
        diagnoses: list[VoiceDiagnosis] = []
        for critic in (self.pronunciation, self.identity, self.prosody, self.semantic):
            try:
                outcome = critic.review(artifact)
            except Exception as exc:  # noqa: BLE001 - a crashed critic blocks
                results.append(
                    GateResult(
                        name=critic.name,
                        verdict=Verdict.ERROR,
                        critical=True,
                        reason=f"critic crashed: {type(exc).__name__}: {exc}",
                    )
                )
                diagnoses.append(
                    VoiceDiagnosis(
                        VoiceDefect.NOT_MEASURED,
                        detail=f"{critic.role} crashed: {exc}",
                        critic=critic.role,
                    )
                )
                continue
            results.append(outcome.result)
            diagnoses.extend(outcome.diagnoses)
        report = evaluate_gates(results, required_critical=CRITICAL_VOICE_GATES)
        return report, diagnoses

    # ---- full clip -------------------------------------------------------
    def produce(
        self,
        brief: VoiceBrief,
        *,
        clip_id: str,
    ) -> VoiceVerdict:
        """Generate, verify and repair one clip.

        Returns a fail-closed verdict. A clip whose critical verifiers could not
        run is ``HOLD``/``FAIL`` — never PASS, and never silently downgraded.
        """

        repairs: list[dict[str, Any]] = []
        current = brief
        artifact: Optional[VoiceArtifact] = None

        for attempt in range(1, self.max_repairs + 2):
            try:
                artifact = self.generator.generate(
                    current, clip_id=clip_id, attempt=attempt
                )
            except BackendUnavailableError as exc:
                return VoiceVerdict(
                    verdict=Verdict.BLOCKED,
                    artifact=None,
                    report=evaluate_gates(
                        [
                            GateResult(
                                name="voice.generation",
                                verdict=Verdict.ERROR,
                                critical=True,
                                reason=str(exc),
                            )
                        ],
                        required_critical=("voice.generation",) + CRITICAL_VOICE_GATES,
                    ),
                    diagnoses=(
                        VoiceDiagnosis(
                            VoiceDefect.NOT_MEASURED,
                            locus=current.language.label,
                            detail=str(exc),
                            critic="VoiceGenerator",
                        ),
                    ),
                    repairs=repairs,
                    reason=f"voice generation unavailable: {exc}",
                )

            report, diagnoses = self.verify(artifact)
            if report.passed:
                return VoiceVerdict(
                    verdict=Verdict.PASS,
                    artifact=artifact,
                    report=report,
                    repairs=repairs,
                    reason="all critical voice gates passed",
                )

            if attempt > self.max_repairs:
                break

            plan: RepairPlan = self.repair_agent.plan(current, diagnoses)
            repairs.append(
                {
                    "attempt": attempt,
                    "blocking": [r.name for r in report.blocking],
                    **plan.to_dict(),
                }
            )
            if not plan.actionable:
                return VoiceVerdict(
                    verdict=_unrepairable_verdict(report),
                    artifact=artifact,
                    report=report,
                    diagnoses=diagnoses,
                    repairs=repairs,
                    reason=(
                        "no targeted repair can clear these defects: "
                        + "; ".join(plan.unrepairable or ["unknown"])
                    ),
                )
            current = plan.brief

        assert artifact is not None
        report, diagnoses = self.verify(artifact)
        return VoiceVerdict(
            verdict=_unrepairable_verdict(report),
            artifact=artifact,
            report=report,
            diagnoses=diagnoses,
            repairs=repairs,
            reason=(
                f"still blocking after {self.max_repairs} repair(s): "
                + ", ".join(r.name for r in report.blocking)
            ),
        )

    def speak(
        self,
        text: str,
        language: Language,
        *,
        clip_id: str,
        scene: str = "development",
        **brief_kwargs: Any,
    ) -> VoiceVerdict:
        """Convenience: director-brief then produce."""
        brief = self.director.brief(text, language, scene=scene, **brief_kwargs)
        return self.produce(brief, clip_id=clip_id)

    # ---- team status -----------------------------------------------------
    def readiness(self) -> dict:
        """Honest per-language readiness, from the backends actually present."""

        status = self.backends.status()
        langs = {}
        for lang in Language:
            vp = self.backends.voiceprint(lang)
            blockers = []
            if not status["tts"]["available"]:
                blockers.append("no TTS backend")
            if vp.is_generic_fallback:
                blockers.append("no Sofia reference voiceprint (generic voice is not Sofia)")
            if not status["asr"]["available"]:
                blockers.append("no ASR backend (pronunciation/semantic unverifiable)")
            if not status["speaker"]["available"]:
                blockers.append("no speaker-embedding backend (identity unverifiable)")
            langs[lang.label] = {
                "can_generate": status["tts"]["available"] and not vp.is_generic_fallback,
                "can_verify": status["asr"]["available"] and status["speaker"]["available"],
                "blockers": blockers,
            }
        return {"backends": status, "languages": langs}


def _unrepairable_verdict(report: GateReport) -> Verdict:
    """HOLD when we could not measure; FAIL when we measured and it is bad."""

    verdicts = {r.verdict for r in report.blocking}
    if verdicts & {Verdict.NOT_MEASURED, Verdict.MISSING, Verdict.ERROR}:
        return Verdict.HOLD
    return Verdict.FAIL


# --------------------------------------------------------------------------
# Agent specs — this is what makes the roles executable, not just documented.
# --------------------------------------------------------------------------
def build_voice_agents(team: VoiceTeam) -> list[AgentSpec]:
    """Wire the seven Voice Team roles as runnable agents."""

    def _direct(ctx: AgentContext) -> AgentResult:
        brief = team.director.brief(
            ctx.get("text", ""),
            Language(ctx.get("language", "ru")),
            scene=ctx.get("scene", "development"),
            scene_context=ctx.get("scene_context", ""),
            must_pronounce=tuple(ctx.get("must_pronounce", ())),
            target_duration_s=ctx.get("target_duration_s"),
        )
        return AgentResult(ok=True, output=brief, notes=f"briefed {brief.language.label}")

    def _generate(ctx: AgentContext) -> AgentResult:
        brief: VoiceBrief = ctx.get("brief")
        artifact = team.generator.generate(
            brief, clip_id=ctx.get("clip_id", ctx.reel_id), attempt=ctx.attempt
        )
        return AgentResult(
            ok=True,
            output=artifact,
            notes=f"generated via {artifact.backend}",
            artifacts={"voice": artifact.audio_path or ""},
        )

    def _critic(critic) -> Any:
        def run(ctx: AgentContext) -> AgentResult:
            outcome = critic.review(ctx.get("artifact"))
            return AgentResult(
                ok=outcome.result.verdict is Verdict.PASS,
                output=outcome,
                notes=f"{outcome.result.verdict.value}: {outcome.result.reason}",
            )

        return run

    def _repair(ctx: AgentContext) -> AgentResult:
        plan = team.repair_agent.plan(ctx.get("brief"), ctx.get("diagnoses", ()))
        return AgentResult(
            ok=plan.actionable,
            output=plan,
            notes=f"scope={plan.scope.value} changes={len(plan.changes)}",
        )

    return [
        AgentSpec(
            name="sofia.voice.director",
            role="VoiceDirector",
            capabilities=(Capability.VOICE_DIRECTION,),
            impl=_direct,
            team=TEAM,
            timeout_s=30,
            description="Decides language, emotion, pace, tone, style and scene context.",
        ),
        AgentSpec(
            name="sofia.voice.generator",
            role="VoiceGenerator",
            capabilities=(Capability.VOICE_GENERATION,),
            impl=_generate,
            team=TEAM,
            timeout_s=300,
            max_attempts=2,
            requires_gpu=True,
            description="Synthesises speech through the canonical Sofia TTS backend.",
        ),
        AgentSpec(
            name="sofia.voice.critic.pronunciation",
            role="PronunciationCritic",
            capabilities=(Capability.VOICE_PRONUNCIATION_QA,),
            impl=_critic(team.pronunciation),
            team=TEAM,
            timeout_s=180,
            description="WER, stress, numbers, names and borrowed words.",
        ),
        AgentSpec(
            name="sofia.voice.critic.identity",
            role="VoiceIdentityCritic",
            capabilities=(Capability.VOICE_IDENTITY_QA,),
            impl=_critic(team.identity),
            team=TEAM,
            timeout_s=180,
            description="The voice is still Sofia, including across RU/UA/EN.",
        ),
        AgentSpec(
            name="sofia.voice.critic.prosody",
            role="ProsodyCritic",
            capabilities=(Capability.VOICE_PROSODY_QA,),
            impl=_critic(team.prosody),
            team=TEAM,
            timeout_s=120,
            description="Rhythm, pauses, emotion, robotic delivery, overacting.",
        ),
        AgentSpec(
            name="sofia.voice.critic.semantic",
            role="SemanticCritic",
            capabilities=(Capability.VOICE_SEMANTIC_QA,),
            impl=_critic(team.semantic),
            team=TEAM,
            timeout_s=120,
            description="Spoken result must not change the script's meaning.",
        ),
        AgentSpec(
            name="sofia.voice.repair",
            role="VoiceRepairAgent",
            capabilities=(Capability.VOICE_REPAIR,),
            impl=_repair,
            team=TEAM,
            timeout_s=60,
            description="Repairs only the diagnosed word/phrase/sentence/prosody.",
        ),
    ]
