"""Reel Production Team wiring: every logical role as a runnable agent.

A role appears here only if it is genuinely executed by
:class:`~sofia.reel.director.ReelDirector`. Roles carried by an existing agent
(the Voice Team, the editor backend) are registered as thin logical agents
rather than as new processes — the requirement is that the role is really
invoked, not that it owns a PID.
"""

from __future__ import annotations

from typing import Any

from sofia.agents.base import AgentContext, AgentResult, AgentSpec, Capability
from sofia.core.verdict import Verdict
from sofia.reel.director import ReelDirector

TEAM = "reel"


def build_reel_agents(director: ReelDirector) -> list[AgentSpec]:
    """Wire the Reel Production Team."""

    def _trend(ctx: AgentContext) -> AgentResult:
        out = director.trend_agent.run(ctx.get("growth"))
        return AgentResult(ok=True, output=out, notes=f"trend={out['trend']}")

    def _idea(ctx: AgentContext) -> AgentResult:
        plan = director.idea_agent.run(ctx.get("growth"), director.config.language)
        return AgentResult(ok=True, output=plan, notes=f"idea={plan.idea[:60]}")

    def _hook(ctx: AgentContext) -> AgentResult:
        hook = director.hook_agent.run(ctx.get("plan"))
        return AgentResult(ok=True, output=hook, notes=f"hook={hook[:60]}")

    def _script(ctx: AgentContext) -> AgentResult:
        lines = director.script_agent.run(ctx.get("plan"))
        return AgentResult(ok=True, output=lines, notes=f"{len(lines)} script lines")

    def _storyboard(ctx: AgentContext) -> AgentResult:
        shots = director.storyboard_agent.run(ctx.get("lines"))
        return AgentResult(ok=True, output=shots, notes=f"{len(shots)} shots")

    def _shot_director(ctx: AgentContext) -> AgentResult:
        shots, cost = director.shot_director.run(ctx.get("shots"))
        shots = director.source_selector.run(shots)
        return AgentResult(
            ok=True,
            output=(shots, cost),
            notes=f"profiles assigned; est {cost['estimated_gpu_s']}s GPU "
            f"(saved {cost['saved_gpu_s']}s vs all-face)",
        )

    def _video(ctx: AgentContext) -> AgentResult:
        director._render_shots(ctx.reel_id, ctx.get("shots"))
        return AgentResult(ok=True, notes="shots rendered")

    def _voice(ctx: AgentContext) -> AgentResult:
        results = director._produce_voice(
            ctx.reel_id,
            ctx.get("shots"),
            ctx.get("assets"),
            strict=bool(ctx.get("strict", True)),
        )
        return AgentResult(ok=True, output=results, notes=f"{len(results)} voice clips")

    def _lipsync(ctx: AgentContext) -> AgentResult:
        director._lipsync(ctx.reel_id, ctx.get("shots"), ctx.get("assets"))
        return AgentResult(ok=True, notes="talking shots lip-synced")

    def _edit(ctx: AgentContext) -> AgentResult:
        director._edit(
            ctx.reel_id,
            ctx.get("brief"),
            ctx.get("plan"),
            ctx.get("shots"),
            ctx.get("assets"),
            ctx.get("voice_results", {}),
        )
        return AgentResult(ok=True, notes="edit assembled")

    def _subtitles(ctx: AgentContext) -> AgentResult:
        outcome = director.subtitle_critic.review(
            ctx.get("subtitles"),
            spoken_text=ctx.get("spoken_text", ""),
            language=director.config.language,
            video_duration_s=ctx.get("video_duration_s"),
            text_top=director.config.subtitle_text_top,
            text_bottom=director.config.subtitle_text_bottom,
        )
        return AgentResult(
            ok=outcome.result.verdict is Verdict.PASS, output=outcome,
            notes=outcome.result.reason,
        )

    def _music(ctx: AgentContext) -> AgentResult:
        outcome = director.audio_critic.review(
            voice_stem=ctx.get("voice_stem"),
            music_stem=ctx.get("music_stem"),
            final_mix=ctx.get("final_mix"),
        )
        return AgentResult(
            ok=outcome.result.verdict is Verdict.PASS, output=outcome,
            notes=outcome.result.reason,
        )

    def _cover(ctx: AgentContext) -> AgentResult:
        outcome = director.cover_critic.review(
            ctx.get("cover"), ctx.get("cover_measurements", {})
        )
        return AgentResult(
            ok=outcome.result.verdict is Verdict.PASS, output=outcome,
            notes=outcome.result.reason,
        )

    def _reel_critic(ctx: AgentContext) -> AgentResult:
        outcome = director.story_critic.review(
            ctx.get("brief"), ctx.get("shots"), caption=ctx.get("caption", "")
        )
        return AgentResult(
            ok=outcome.result.verdict is Verdict.PASS, output=outcome,
            notes=outcome.result.reason,
        )

    def _repair(ctx: AgentContext) -> AgentResult:
        decision = director.repair_router.route(ctx.get("diagnoses", ()))
        return AgentResult(
            ok=decision.actionable,
            output=decision,
            notes=f"resume_from={decision.resume_from.value} "
            f"components={decision.components}",
        )

    def _final(ctx: AgentContext) -> AgentResult:
        report = director.final_gate.evaluate(ctx.get("results", ()))
        return AgentResult(
            ok=report.passed, output=report, notes=f"final verdict {report.verdict.value}"
        )

    def _direct(ctx: AgentContext) -> AgentResult:
        result = director.produce(
            ctx.reel_id,
            ctx.get("growth"),
            perceptual_samples=ctx.get("perceptual_samples", ()),
            cover_measurements=ctx.get("cover_measurements"),
        )
        return AgentResult(
            ok=result.verdict is Verdict.PASS,
            output=result,
            notes=f"{result.verdict.value}: {result.reason}",
        )

    def spec(name, role, caps, impl, **kw) -> AgentSpec:
        return AgentSpec(
            name=name,
            role=role,
            capabilities=tuple(caps),
            impl=impl,
            team=TEAM,
            **kw,
        )

    return [
        spec("sofia.reel.director", "ReelDirector", (Capability.REEL_DIRECTION,), _direct,
             timeout_s=7200, description="Single logical owner of the Reel, end to end."),
        spec("sofia.reel.trend", "TrendAgent", (Capability.TREND_RESEARCH,), _trend,
             timeout_s=120, description="Consumes Growth Engine trend/KPI/audience input."),
        spec("sofia.reel.idea", "IdeaAgent", (Capability.IDEA,), _idea,
             timeout_s=180, description="Idea and content purpose from the trend."),
        spec("sofia.reel.hook", "HookAgent", (Capability.HOOK,), _hook,
             timeout_s=120, description="Owns the opening beat."),
        spec("sofia.reel.script", "ScriptAgent", (Capability.SCRIPT,), _script,
             timeout_s=180, description="Beat-complete, speakable script."),
        spec("sofia.reel.storyboard", "StoryboardAgent", (Capability.STORYBOARD,),
             _storyboard, timeout_s=180,
             description="Every scene gets an explicit on-screen function."),
        spec("sofia.reel.shot_director", "ShotDirector", (Capability.SHOT_DIRECTION,),
             _shot_director, timeout_s=180,
             description="Shot types, generator profiles and source selection."),
        spec("sofia.reel.video", "VideoAgent", (Capability.VIDEO_GENERATION,), _video,
             timeout_s=5400, requires_gpu=True, max_attempts=2,
             description="Renders each shot with its type's profile."),
        spec("sofia.reel.voice", "VoiceTeam", (Capability.VOICE_GENERATION,), _voice,
             timeout_s=1800,
             description="Delegates to the Sofia Voice Team (fail-closed)."),
        spec("sofia.reel.lipsync", "LipSyncAgent", (Capability.LIPSYNC,), _lipsync,
             timeout_s=3600, requires_gpu=True,
             description="Champion lip-sync; new models enter only as challengers."),
        spec("sofia.reel.editor", "EditorAgent", (Capability.EDIT,), _edit,
             timeout_s=1800,
             description="Cuts, pacing, B-roll, ducking, safe zones, transitions."),
        spec("sofia.reel.subtitles", "SubtitleAgent", (Capability.SUBTITLES,), _subtitles,
             timeout_s=300,
             description="Subtitles must match real speech, timing and safe zones."),
        spec("sofia.reel.music", "Music/SFX Agent", (Capability.MUSIC_SFX,), _music,
             timeout_s=600,
             description="Music must not mask the voice; ducking is verified."),
        spec("sofia.reel.cover", "CoverAgent", (Capability.COVER,), _cover,
             timeout_s=300, description="Per-reel cover candidate and its QA."),
        spec("sofia.reel.critic", "ReelCritic", (Capability.REEL_QA,), _reel_critic,
             timeout_s=600, description="Hook, story, scene function, CTA, caption match."),
        spec("sofia.reel.repair", "RepairAgent", (Capability.REPAIR_ROUTING,), _repair,
             timeout_s=120, description="Routes each defect to the narrowest component."),
        spec("sofia.reel.final_gate", "FinalGate", (Capability.FINAL_GATE,), _final,
             timeout_s=600,
             description="Aggregates every category fail-closed; decode is not enough."),
    ]
