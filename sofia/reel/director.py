"""ReelDirector — one logical owner, accountable for the finished Reel.

The director is not a dispatcher that calls generators in order. It holds the
brief (purpose, audience, trend, hook, arc, shot list, emotions, voice,
continuity, expected KPI), owns the Reel's lease, checkpoints every stage so
work resumes instead of restarting, routes repairs to the narrowest component,
and answers for the FinalGate verdict.

Publishing stays on HOLD: the best outcome this class can produce is
``READY_FOR_OWNER_REVIEW``. It has no publish path at all.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from sofia.agents.base import AgentContext, Capability
from sofia.agents.ownership import OwnershipRegistry
from sofia.agents.runner import AgentRunner
from sofia.core.artifacts import is_usable
from sofia.core.checkpoint import CheckpointStore, StageState
from sofia.core.errors import BackendUnavailableError, OwnershipError
from sofia.core.gates import GateResult, evaluate_gates
from sofia.core.paths import safe_component
from sofia.core.verdict import Evidence, Measurement, Verdict
from sofia.reel.backends import ReelBackends
from sofia.reel.contracts import (
    GrowthInput,
    ReelAssets,
    ReelBrief,
    ReelDefect,
    ReelDiagnosis,
    ReelResult,
    Shot,
    ShotType,
)
from sofia.reel.critics import (
    FINAL_GATE_CATEGORIES,
    AudioMixCritic,
    CoverCritic,
    EditorCritic,
    FinalGate,
    LipSyncCritic,
    PerceptualReviewGate,
    PerceptualSample,
    ReelThresholds,
    StoryCritic,
    SubtitleCritic,
    VideoQACritic,
)
from sofia.reel.gpu import GpuArbiter, GpuBusy, WorkClass
from sofia.reel.scorecard import score_categories, world_class
from sofia.reel.repair_router import RepairDecision, RepairRouter
from sofia.reel.shots import profile_for
from sofia.reel.stages import (
    AuthoredPlan,
    ContentPlan,
    CreativeSource,
    HookAgent,
    IdeaAgent,
    ScriptAgent,
    ShotDirector,
    SourceSelector,
    StoryboardAgent,
    TrendAgent,
    build_reel_brief,
)
from sofia.reel.audio_mix import build_voice_track, duck_offline
from sofia.reel.subtitles import (
    build_cues,
    estimate_text_extent,
    write_ass,
    write_srt,
)
from sofia.voice.audio import analyse_wav
from sofia.voice.contracts import Language, VoiceVerdict
from sofia.voice.pipeline import VoiceTeam

#: Publishing is fail-closed and this module has no way to change it.
PUBLISHING_HOLD = True
TERMINAL_APPROVED_STATE = "READY_FOR_OWNER_REVIEW"


@dataclass
class ReelDirectorConfig:
    workdir: Path
    language: Language = Language.RU
    max_repair_rounds: int = 2
    target_duration_s: float = 22.0
    sofia_references: Mapping[str, str] = field(default_factory=dict)
    subtitle_text_top: float = 0.62
    subtitle_text_bottom: float = 0.78
    frame_width: int = 1080
    frame_height: int = 1920


class ReelDirector:
    """The single logical owner of one Reel."""

    name = "sofia.reel.director"
    role = "ReelDirector"

    def __init__(
        self,
        config: ReelDirectorConfig,
        *,
        voice_team: VoiceTeam,
        backends: ReelBackends,
        creative: CreativeSource,
        runner: Optional[AgentRunner] = None,
        ownership: Optional[OwnershipRegistry] = None,
        checkpoints: Optional[CheckpointStore] = None,
        gpu: Optional[GpuArbiter] = None,
        thresholds: Optional[ReelThresholds] = None,
        music_backend: Any = None,
        growth: Any = None,
    ) -> None:
        self.config = config
        self.workdir = Path(config.workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.voice_team = voice_team
        self.backends = backends
        self.creative = creative
        self.runner = runner
        self.ownership = ownership or OwnershipRegistry(self.workdir / "leases")
        self.checkpoints = checkpoints or CheckpointStore(self.workdir / "checkpoints")
        self.gpu = gpu or GpuArbiter()
        self.thresholds = thresholds or ReelThresholds()
        self.music_backend = music_backend
        #: The Growth Engine, when one is attached. Every finished Reel is fed
        #: back to it so the next decision sees what happened to this one.
        self.growth = growth
        #: Growth bookkeeping failures. Recorded rather than raised, because a
        #: broken analytics sink must not change a Reel's verdict — but a
        #: silently broken one looks exactly like a studio that made nothing,
        #: so it surfaces in status().
        self.growth_errors: list[str] = []

        # Logical roles carried by this director's team.
        self.trend_agent = TrendAgent()
        self.idea_agent = IdeaAgent(creative)
        self.hook_agent = HookAgent()
        self.script_agent = ScriptAgent()
        self.storyboard_agent = StoryboardAgent()
        self.shot_director = ShotDirector()
        self.source_selector = SourceSelector(config.sofia_references)
        self.repair_router = RepairRouter()
        self.final_gate = FinalGate()

        self.story_critic = StoryCritic(self.thresholds)
        self.video_critic = VideoQACritic(backends, self.thresholds)
        self.lipsync_critic = LipSyncCritic(backends, self.thresholds)
        self.subtitle_critic = SubtitleCritic()
        self.audio_critic = AudioMixCritic(self.thresholds)
        self.cover_critic = CoverCritic()
        self.editor_critic = EditorCritic()
        self.perceptual_gate = PerceptualReviewGate()
        #: Which repair round is being rendered. It tags every artifact path,
        #: so a repair writes alongside the take it replaces instead of over
        #: it — NO-DELETE applies to the evidence of a failed attempt too.
        self._repair_round = 0

    # ---- lifecycle -------------------------------------------------------
    @staticmethod
    def _slug(reel_id: str, repair_round: int = 0) -> str:
        """The on-disk form of a reel id, tagged with the repair round.

        Checkpoints and leases already sanitise their own filenames; artifact
        paths must do the same or a crafted id would write outside workdir.
        The ``.rN`` tag keeps each repair round's output separate: the take
        that failed stays on disk as the evidence for why it was repaired.
        """
        base = safe_component(reel_id, fallback="reel")
        return base if repair_round == 0 else f"{base}.r{repair_round}"

    def claim(self, reel_id: str) -> None:
        """Take exclusive ownership. A second director is rejected."""
        self.ownership.acquire(reel_id, self.name, ttl_s=6 * 3600)

    def resume_point(self, reel_id: str) -> StageState:
        return self.checkpoints.resume_point(reel_id)

    def _checkpoint(
        self,
        reel_id: str,
        stage: StageState,
        *,
        artifacts: Optional[Mapping[str, str]] = None,
        payload: Optional[Mapping[str, Any]] = None,
        allow_regression: bool = False,
    ) -> None:
        self.checkpoints.advance(
            reel_id,
            stage,
            self.name,
            artifacts=artifacts,
            payload=payload,
            allow_regression=allow_regression,
        )

    # ---- the pipeline ----------------------------------------------------
    def produce(
        self,
        reel_id: str,
        growth: GrowthInput,
        *,
        perceptual_samples: Sequence[PerceptualSample] = (),
        cover_measurements: Optional[Mapping[str, Optional[float]]] = None,
        resume: bool = True,
        diagnostic: bool = False,
    ) -> ReelResult:
        """Run the Reel end to end, resuming from the last good stage.

        ``diagnostic=True`` keeps going past a blocking stage so one run
        surfaces every defect instead of one per attempt. It records each block
        as a diagnosis and **forces a non-PASS verdict**: a diagnostic run can
        never approve a Reel, whatever the downstream gates say.
        """

        self.claim(reel_id)
        # Per Reel, not per director: the round budget and the artifact tag
        # belong to this production, not to whatever ran before it.
        self._repair_round = 0
        assets = ReelAssets()
        started = StageState.CREATED if not resume else self.resume_point(reel_id)
        diagnoses: list[ReelDiagnosis] = []
        repairs: list[dict] = []
        brief: Optional[ReelBrief] = None
        plan: Optional[ContentPlan] = None

        try:
            # -- BRIEF: trend -> idea -> purpose -> hook -> script ----------
            trend = self._invoke(Capability.TREND_RESEARCH, reel_id, growth=growth)
            plan = self._invoke(Capability.IDEA, reel_id, growth=growth)
            hook = self._invoke(Capability.HOOK, reel_id, plan=plan)
            lines = self._invoke(Capability.SCRIPT, reel_id, plan=plan)
            brief = build_reel_brief(
                reel_id, plan, growth, self.config.language,
                target_duration_s=self.config.target_duration_s,
            )
            self._checkpoint(
                reel_id,
                StageState.BRIEF_DONE,
                payload={"trend": trend, "hook": hook, "plan": plan.to_dict()},
            )
            self._checkpoint(
                reel_id,
                StageState.SCRIPT_DONE,
                payload={"lines": [ln.to_dict() for ln in lines]},
            )

            # -- STORYBOARD / SHOT LIST / SOURCE SELECTION -----------------
            shots = self._invoke(Capability.STORYBOARD, reel_id, lines=lines)
            shots, cost = self._invoke(Capability.SHOT_DIRECTION, reel_id, shots=shots)
            # Resume: reattach artifacts a previous run already produced, so a
            # lost session re-uses finished renders instead of paying for them
            # twice.
            if resume:
                self._rehydrate(reel_id, shots, assets)
            assets.shots = shots
            self._checkpoint(
                reel_id,
                StageState.SHOTS_DONE,
                payload={
                    "shots": [s.to_dict() for s in shots],
                    "gpu_cost_estimate": cost,
                },
            )

            # -- VOICE (light/voice work may proceed while GPU is busy) ----
            voice_results = self._stage(
                diagnostic,
                diagnoses,
                ReelDefect.VOICE,
                "voice",
                lambda: self._invoke(
                    Capability.VOICE_GENERATION,
                    reel_id,
                    shots=shots,
                    assets=assets,
                    strict=not diagnostic,
                ),
                default={},
            )
            self._checkpoint(
                reel_id,
                StageState.VOICE_DONE,
                artifacts={f"voice.{k}": v for k, v in assets.voice_clips.items()},
            )

            # -- VIDEO (heavy: waits for production) -----------------------
            self._stage(
                diagnostic,
                diagnoses,
                ReelDefect.SHOT,
                "video",
                lambda: self._invoke(
                    Capability.VIDEO_GENERATION,
                    reel_id,
                    shots=shots,
                    # _render_shots asks the arbiter itself, backend-aware.
                    gpu_cleared=True,
                ),
            )
            self._checkpoint(
                reel_id,
                StageState.VIDEO_DONE,
                payload={"shots": [s.to_dict() for s in shots]},
            )

            # -- LIP-SYNC (heavy) ------------------------------------------
            self._stage(
                diagnostic,
                diagnoses,
                ReelDefect.LIPSYNC,
                "lipsync",
                lambda: self._invoke(
                    Capability.LIPSYNC,
                    reel_id,
                    shots=shots,
                    assets=assets,
                    gpu_cleared=True,
                ),
            )
            self._checkpoint(
                reel_id,
                StageState.LIPSYNC_DONE,
                payload={"shots": [s.to_dict() for s in shots]},
            )

            # -- EDIT / MUSIC / SFX / SUBTITLES / COVER --------------------
            self._stage(
                diagnostic,
                diagnoses,
                ReelDefect.EDIT,
                "edit",
                lambda: self._invoke(
                    Capability.EDIT,
                    reel_id,
                    brief=brief,
                    plan=plan,
                    shots=shots,
                    assets=assets,
                    voice_results=voice_results,
                ),
            )
            self._checkpoint(
                reel_id,
                StageState.EDIT_DONE,
                artifacts={
                    k: v
                    for k, v in {
                        "edit": assets.edit,
                        "subtitles": assets.subtitles,
                        "cover": assets.cover,
                        "music": assets.music,
                    }.items()
                    if v
                },
            )

        except (BackendUnavailableError, GpuBusy) as exc:
            stage = self.resume_point(reel_id)
            diagnoses.append(
                ReelDiagnosis(
                    ReelDefect.NOT_MEASURED,
                    detail=f"{type(exc).__name__}: {exc}",
                    critic=self.role,
                )
            )
            report = evaluate_gates(
                [
                    GateResult(
                        name="reel.production",
                        verdict=Verdict.ERROR,
                        critical=True,
                        reason=str(exc),
                    )
                ],
                required_critical=("reel.production",) + FINAL_GATE_CATEGORIES,
            )
            self._checkpoint(reel_id, StageState.HELD, allow_regression=True)
            return self._close_growth_loop(ReelResult(
                reel_id=reel_id,
                verdict=Verdict.BLOCKED,
                stage=stage,
                brief=brief,
                assets=assets,
                report=report,
                diagnoses=diagnoses,
                reason=f"production stopped at {stage.value}: {exc}",
                owner=self.name,
            ), diagnostic=diagnostic)

        # -- FINAL QA ------------------------------------------------------
        def run_final_qa() -> ReelResult:
            return self._final_qa(
                reel_id,
                brief,
                plan,
                assets,
                voice_results,
                perceptual_samples=perceptual_samples,
                cover_measurements=cover_measurements or {},
                repairs=repairs,
                diagnostic=diagnostic,
                carried_diagnoses=diagnoses,
            )

        result = run_final_qa()
        if diagnostic:
            # A diagnostic run reports what it found; repairing it would be
            # chasing defects that were deliberately walked past.
            return result
        return self._repair_until_settled(
            result,
            run_final_qa,
            reel_id=reel_id,
            brief=brief,
            plan=plan,
            shots=shots,
            assets=assets,
            voice_results=voice_results,
            repairs=repairs,
        )

    # ---- repair ----------------------------------------------------------
    def _repair_until_settled(
        self,
        result: ReelResult,
        run_final_qa: Callable[[], ReelResult],
        *,
        reel_id: str,
        brief: Optional[ReelBrief],
        plan: Optional[ContentPlan],
        shots: Sequence[Shot],
        assets: ReelAssets,
        voice_results: Mapping[int, VoiceVerdict],
        repairs: list[dict],
    ) -> ReelResult:
        """Regenerate what the router named, up to the configured round budget.

        A repair only rebuilds a component and asks the same gates again — it
        never re-decides a verdict, so this loop cannot turn a failing Reel into
        a passing one by itself. It stops on the first round that has nothing
        regenerable to try, which includes every unmeasurable gate: no amount
        of re-rendering makes a missing verifier appear.
        """

        while (
            result.verdict is not Verdict.PASS
            and self._repair_round < self.config.max_repair_rounds
        ):
            decision = self.repair_router.route(result.diagnoses)
            stages, skipped = self._repairable(decision)
            if not decision.actionable or not stages:
                repairs.append(
                    {
                        "round": self._repair_round + 1,
                        "regenerated": [],
                        "reason": self._why_not_repairable(decision, skipped),
                    }
                )
                return result

            self._repair_round += 1
            repairs.append(
                {
                    "round": self._repair_round,
                    "components": list(decision.components),
                    "stages": list(stages),
                    "shots": list(decision.shot_indices),
                    "rolled_back_to": decision.resume_from.value,
                    "skipped": skipped,
                }
            )
            self._checkpoint(
                reel_id,
                decision.resume_from,
                allow_regression=True,
                payload={"repair_round": self._repair_round},
            )
            try:
                voice_results = self._regenerate(
                    reel_id,
                    stages,
                    brief=brief,
                    plan=plan,
                    shots=shots,
                    assets=assets,
                    voice_results=voice_results,
                    shot_indices=decision.shot_indices,
                )
            except (BackendUnavailableError, GpuBusy) as exc:
                repairs.append(
                    {
                        "round": self._repair_round,
                        "aborted": f"{type(exc).__name__}: {exc}",
                    }
                )
                return result
            result = run_final_qa()

        if result.verdict is not Verdict.PASS:
            repairs.append(
                {
                    "round": self._repair_round,
                    "reason": (
                        f"repair budget exhausted after {self._repair_round} "
                        "round(s); the Reel is held for the owner rather than "
                        "retried indefinitely"
                    ),
                }
            )
        return result

    # ---- repair ----------------------------------------------------------
    #: Which stages have to be re-run to clear a defect in each component.
    #: Downstream stages are included because they consume what was repaired:
    #: a re-rendered shot has to be lip-synced and re-cut, or the final file
    #: still carries the old take.
    _REPAIR_STAGES: Mapping[str, tuple[str, ...]] = {
        "VideoAgent": ("video", "lipsync", "edit"),
        "VoiceTeam": ("voice", "lipsync", "edit"),
        "LipSyncAgent": ("lipsync", "edit"),
        "EditorAgent": ("edit",),
        "SubtitleAgent": ("edit",),
        "Music/SFX Agent": ("edit",),
        "CoverAgent": ("edit",),
    }
    _STAGE_ORDER: tuple[str, ...] = ("voice", "video", "lipsync", "edit")

    def _repairable(
        self, decision: RepairDecision
    ) -> tuple[tuple[str, ...], list[str]]:
        """Split a decision into stages this director can re-run, and the rest.

        A defect in the creative plan routes to HookAgent, ScriptAgent or the
        ShotDirector. With an authored creative source those agents would hand
        back the same plan they handed back the first time, so re-running them
        is not a repair — it is a loop. Those components are reported as needing
        a human, not retried.
        """

        wanted: set[str] = set()
        skipped: list[str] = []
        for component in decision.components:
            stages = self._REPAIR_STAGES.get(component)
            if stages is None:
                skipped.append(component)
                continue
            wanted.update(stages)
        return tuple(s for s in self._STAGE_ORDER if s in wanted), skipped

    @staticmethod
    def _why_not_repairable(decision: RepairDecision, skipped: Sequence[str]) -> str:
        if decision.full_stop:
            return (
                "not repairable by regenerating anything: "
                + "; ".join(decision.unrepairable[:3])
            )
        if skipped:
            return (
                f"{', '.join(skipped)} would have to re-author the creative plan, "
                "which is a human decision here"
            )
        if not decision.routes:
            return "no defect carried a repair route"
        return "nothing left to regenerate"

    def _regenerate(
        self,
        reel_id: str,
        stages: Sequence[str],
        *,
        brief: ReelBrief,
        plan: Optional[ContentPlan],
        shots: Sequence[Shot],
        assets: ReelAssets,
        voice_results: Mapping[int, VoiceVerdict],
        shot_indices: Sequence[int],
    ) -> dict[int, VoiceVerdict]:
        """Re-run only the named stages, and only for the affected shots.

        Clearing an artifact path is what makes the stage redo the work: every
        stage skips a shot whose artifact is already usable, so the shots that
        were fine keep their takes and only the routed ones are paid for again.
        """

        affected = set(shot_indices)
        targets = [s for s in shots if not affected or s.index in affected]
        results = dict(voice_results)

        if "voice" in stages:
            for shot in targets:
                assets.voice_clips.pop(str(shot.index), None)
            results.update(
                self._invoke(
                    Capability.VOICE_GENERATION,
                    reel_id,
                    shots=targets,
                    assets=assets,
                    strict=False,
                )
            )
        if "video" in stages:
            for shot in targets:
                shot.video_path = None
                shot.lipsync_path = None
            self._invoke(
                Capability.VIDEO_GENERATION, reel_id, shots=targets, gpu_cleared=True
            )
        if "lipsync" in stages:
            for shot in targets:
                shot.lipsync_path = None
            self._invoke(
                Capability.LIPSYNC,
                reel_id,
                shots=shots,
                assets=assets,
                gpu_cleared=True,
            )
        if "edit" in stages:
            self._invoke(
                Capability.EDIT,
                reel_id,
                brief=brief,
                plan=plan,
                shots=shots,
                assets=assets,
                voice_results=results,
            )
        return results

    def _invoke(self, capability: Capability, reel_id: str, **params: Any) -> Any:
        """Dispatch a role through the execution infrastructure.

        When a runner is attached every role goes through it, so each
        invocation is timed, ownership-checked, timeout-bounded, retried per
        policy and written to the execution log. That log is the evidence that
        a role really ran, as opposed to merely being declared.
        """

        if self.runner is None:
            raise BackendUnavailableError(
                "no AgentRunner attached; roles must execute through the "
                "agent infrastructure"
            )
        ctx = AgentContext(
            reel_id=reel_id, owner=self.name, workdir=str(self.workdir), params=params
        )
        return self.runner.run(capability, ctx).output

    def _rehydrate(
        self, reel_id: str, shots: Sequence[Shot], assets: ReelAssets
    ) -> int:
        """Reattach artifacts from the last checkpoint that still exist on disk.

        Only artifacts that are *complete* are restored. A file left half
        written by an interrupted run exists and is not empty, so a presence
        check would happily reuse a fragment; each one is decoded instead.
        """

        checkpoint = self.checkpoints.load(reel_id)
        if checkpoint is None:
            return 0
        previous = {s.get("index"): s for s in checkpoint.payload.get("shots", [])}
        restored = 0
        for shot in shots:
            prior = previous.get(shot.index, {})
            for field in ("video_path", "lipsync_path"):
                path = prior.get(field)
                if self._usable_video(path):
                    setattr(shot, field, path)
                    restored += 1
        for key, path in checkpoint.payload.get("artifacts", {}).items():
            if key.startswith("voice.") and is_usable(path, kind="wav"):
                assets.voice_clips.setdefault(key.split(".", 1)[1], path)
                restored += 1
        return restored

    def _delivered_runtime(self, final_path: Optional[str]) -> Optional[float]:
        """The runtime of the file that will actually play, or ``None``.

        ``None`` is returned rather than the planned duration, so a caller that
        cannot read the file reports "not measured" instead of quietly checking
        the plan against itself.
        """

        if not final_path or not Path(final_path).exists():
            return None
        probe = getattr(self.backends.editor, "probe", None)
        if not callable(probe):
            return None
        try:
            info = probe(Path(final_path))
        except Exception:  # noqa: BLE001 - an unreadable file is not a runtime
            return None
        duration = float(info.get("format", {}).get("duration", 0.0) or 0.0)
        return duration or None

    def _usable_video(self, path: Optional[str]) -> bool:
        """Whether a rendered clip is complete enough to reuse."""
        probe = getattr(self.backends.editor, "probe", None)
        return is_usable(path, kind="video", probe=probe if callable(probe) else None)

    def _stage(
        self,
        diagnostic: bool,
        diagnoses: list[ReelDiagnosis],
        defect: ReelDefect,
        label: str,
        fn: Callable[[], Any],
        *,
        default: Any = None,
    ) -> Any:
        """Run a stage; in diagnostic mode record the block and carry on."""
        try:
            return fn()
        except (BackendUnavailableError, GpuBusy) as exc:
            if not diagnostic:
                raise
            diagnoses.append(
                ReelDiagnosis(
                    defect,
                    locus=label,
                    detail=f"{type(exc).__name__}: {exc}",
                    critic=self.role,
                )
            )
            return default

    # ---- stage implementations ------------------------------------------
    def _produce_voice(
        self,
        reel_id: str,
        shots: Sequence[Shot],
        assets: ReelAssets,
        *,
        strict: bool = True,
    ) -> dict[int, VoiceVerdict]:
        """Voice work continues even when the GPU is busy with production."""

        results: dict[int, VoiceVerdict] = {}
        for shot in shots:
            if not shot.voice_line.strip():
                continue
            brief = self.voice_team.director.brief(
                shot.voice_line,
                self.config.language,
                scene=shot.beat.value.lower(),
                scene_context=shot.description,
                emotion=shot.emotion,
                target_duration_s=shot.duration_s,
            )
            verdict = self.voice_team.produce(
                brief, clip_id=f"{reel_id}.shot{shot.index}"
            )
            results[shot.index] = verdict
            if verdict.verdict is not Verdict.PASS and strict:
                raise BackendUnavailableError(
                    f"voice for shot {shot.index} did not pass: "
                    f"{verdict.verdict.value} — {verdict.reason}"
                )
            if verdict.artifact and verdict.artifact.audio_path:
                # Non-passing clips are still placed on the timeline in a
                # diagnostic run so downstream stages are measured on real
                # audio. The voice gate still fails; see _voice_gate.
                assets.voice_clips[str(shot.index)] = verdict.artifact.audio_path
        if not results:
            raise BackendUnavailableError("reel has no talking segment at all")
        return results

    def _render_shots(self, reel_id: str, shots: Sequence[Shot]) -> None:
        for shot in shots:
            out = self.workdir / "shots" / f"{self._slug(reel_id, self._repair_round)}.shot{shot.index}.mp4"
            if self._usable_video(shot.video_path):
                continue  # resumed: this shot is already rendered and decodes
            if self._usable_video(str(out)):
                shot.video_path = str(out)
                continue
            profile = profile_for(shot.shot_type)
            # A backend that renders on CPU does not queue behind production.
            backend_needs_gpu = getattr(self.backends.video, "requires_gpu", True)
            if profile.vram_gb > 0 and backend_needs_gpu:
                self.gpu.require(
                    f"VideoAgent[{profile.name}]",
                    reel_id,
                    work=WorkClass.HEAVY,
                    vram_gb=profile.vram_gb,
                )
            shot.video_path = str(self.backends.video.render(shot, profile, out))

    def _lipsync(
        self, reel_id: str, shots: Sequence[Shot], assets: ReelAssets
    ) -> None:
        for shot in shots:
            if not shot.shot_type.needs_lipsync:
                continue
            synced = self.workdir / "lipsync" / f"{self._slug(reel_id, self._repair_round)}.shot{shot.index}.mp4"
            if self._usable_video(shot.lipsync_path):
                continue
            if self._usable_video(str(synced)):
                shot.lipsync_path = str(synced)
                continue
            audio = assets.voice_clips.get(str(shot.index))
            if not audio:
                raise BackendUnavailableError(
                    f"talking shot {shot.index} has no verified voice clip"
                )
            if not self.backends.lipsync.available():
                raise BackendUnavailableError(
                    f"talking shot {shot.index} cannot be lip-synced: the champion "
                    "lip-sync model is not available on this machine"
                )
            if getattr(self.backends.lipsync, "requires_gpu", True):
                self.gpu.require(
                    "LipSyncAgent", reel_id, work=WorkClass.HEAVY, vram_gb=20.0
                )
            shot.lipsync_path = str(
                self.backends.lipsync.sync(
                    Path(shot.video_path or ""), Path(audio), synced
                )
            )

    def _edit(
        self,
        reel_id: str,
        brief: ReelBrief,
        plan: ContentPlan,
        shots: Sequence[Shot],
        assets: ReelAssets,
        voice_results: Mapping[int, VoiceVerdict],
    ) -> None:
        """Assemble picture and sound: cuts, voice timeline, music, ducking,
        subtitles, cover.

        Subtitles are built from the *verified* speech (the ASR transcript of
        what was actually said) and only fall back to the script line when the
        voice clip itself passed. They are never invented from the script for a
        clip that failed.
        """

        total = sum(s.duration_s for s in shots)

        # --- voice timeline -------------------------------------------------
        segments: list[tuple[str, float, float]] = []
        placed: list[tuple[str, float]] = []
        cursor = 0.0
        for shot in shots:
            if shot.voice_line.strip():
                verdict = voice_results.get(shot.index)
                artifact = verdict.artifact if verdict else None
                spoken = (
                    artifact.transcript
                    if artifact and artifact.transcript
                    else shot.voice_line
                )
                segments.append((spoken, cursor, cursor + shot.duration_s))
                clip = assets.voice_clips.get(str(shot.index))
                if clip:
                    placed.append((clip, cursor))
            cursor += shot.duration_s

        # --- subtitles ------------------------------------------------------
        cues = build_cues(segments)
        assets.subtitles = str(
            write_srt(cues, self.workdir / "subtitles" / f"{self._slug(reel_id, self._repair_round)}.srt")
        )
        # The burn-in copy carries explicit PlayRes/margins so what is rendered
        # matches what the subtitle critic verified.
        burn_in = write_ass(
            cues,
            self.workdir / "subtitles" / f"{self._slug(reel_id, self._repair_round)}.ass",
            width=self.config.frame_width,
            height=self.config.frame_height,
            safe_bottom=self.config.subtitle_text_bottom,
        )
        top, bottom = estimate_text_extent(
            cues,
            height=self.config.frame_height,
            safe_bottom=self.config.subtitle_text_bottom,
        )
        self._subtitle_extent = (top, bottom)

        # --- audio: voice track, music bed, verified ducking ----------------
        # What was actually laid on the timeline, measured from the clips. A
        # generated clip is asked for the shot's length but comes back however
        # long the words take, and an overrun plays over the next clip rather
        # than pushing it along.
        self._voice_spans = []
        for clip, start in placed:
            try:
                length = analyse_wav(clip).duration_s
            except Exception:  # noqa: BLE001 - an unreadable clip is caught by the voice gate
                continue
            self._voice_spans.append((Path(clip).name, start, length))

        audio_track: Optional[str] = None
        if placed:
            voice_track = build_voice_track(
                placed, self.workdir / "audio" / f"{self._slug(reel_id, self._repair_round)}.voice.wav", total_s=total
            )
            assets.voice_clips["_track"] = str(voice_track)
            if self.music_backend is not None:
                music = self.music_backend.generate(
                    self.workdir / "audio" / f"{self._slug(reel_id, self._repair_round)}.music.wav", total
                )
                assets.music = str(music)
                mixer = getattr(self.backends.editor, "mix_audio", None)
                out = self.workdir / "audio" / f"{self._slug(reel_id, self._repair_round)}.mix.wav"
                if callable(mixer):
                    audio_track = str(
                        mixer(
                            Path(voice_track),
                            Path(music),
                            out,
                            self.thresholds.min_voice_over_music_db,
                        )
                    )
                else:
                    audio_track = str(
                        duck_offline(
                            voice_track,
                            music,
                            out,
                            target_headroom_db=self.thresholds.min_voice_over_music_db,
                        )
                    )
            else:
                audio_track = str(voice_track)

        # --- picture --------------------------------------------------------
        clips = [s.lipsync_path or s.video_path for s in shots]
        spec = {
            "clips": [c for c in clips if c],
            "fps": 24,
            "subtitles": assets.subtitles,
            "subtitles_burn": str(burn_in),
            "audio": audio_track,
            "music": assets.music,
            "duck_db": self.thresholds.min_voice_over_music_db,
            "height": self.config.frame_height,
            "width": self.config.frame_width,
            "safe_zones": {
                "top": self.config.subtitle_text_top,
                "bottom": self.config.subtitle_text_bottom,
            },
        }
        out = self.workdir / "edit" / f"{self._slug(reel_id, self._repair_round)}.mp4"
        assets.edit = str(self.backends.editor.assemble(spec, out))
        assets.final = assets.edit

        # --- cover ----------------------------------------------------------
        cover_at = min(1.0, max(0.2, shots[0].duration_s * 0.5)) if shots else 0.5
        slug = self._slug(reel_id, self._repair_round)
        assets.cover = str(
            self.backends.editor.extract_frame(
                Path(assets.final), cover_at, self.workdir / "cover" / f"{slug}.jpg"
            )
        )
        # A second copy in a format the stdlib can decode, so cover composition
        # is measurable without an image library.
        try:
            self._cover_ppm = str(
                self.backends.editor.extract_frame(
                    Path(assets.final), cover_at, self.workdir / "qa" / f"{slug}.cover.ppm"
                )
            )
        except BackendUnavailableError:
            self._cover_ppm = None

    # ---- final QA --------------------------------------------------------
    def _final_qa(
        self,
        reel_id: str,
        brief: ReelBrief,
        plan: Optional[ContentPlan],
        assets: ReelAssets,
        voice_results: Mapping[int, VoiceVerdict],
        *,
        perceptual_samples: Sequence[PerceptualSample],
        cover_measurements: Mapping[str, Optional[float]],
        repairs: list[dict],
        diagnostic: bool = False,
        carried_diagnoses: Sequence[ReelDiagnosis] = (),
    ) -> ReelResult:
        results: list[GateResult] = []
        diagnoses: list[ReelDiagnosis] = list(carried_diagnoses)

        def collect(outcome) -> None:
            results.append(outcome.result)
            diagnoses.extend(outcome.diagnoses)

        results.append(
            self.final_gate.decode_gate(assets.final, self.backends, self.thresholds)
        )
        collect(
            self.story_critic.review(
                brief, assets.shots, caption=plan.caption if plan else ""
            )
        )
        collect(self.video_critic.review(assets.shots))
        results.append(_voice_gate(voice_results))
        collect(self.lipsync_critic.review(assets.shots))
        # The runtime that actually plays, read from the file. Everything that
        # reasons from the shot list is checked against this, so a dropped clip
        # or a truncated encode cannot leave the gates measuring a programme
        # that was never assembled.
        delivered_s = self._delivered_runtime(assets.final)
        collect(
            self.editor_critic.review(
                final_path=assets.final,
                shots=assets.shots,
                mix_path=_audio_for_analysis(assets),
                editor=self.backends.editor,
                workdir=self.workdir,
                music_bpm=getattr(self.music_backend, "bpm", None),
                delivered_runtime_s=delivered_s,
                voice_spans=getattr(self, "_voice_spans", None),
            )
        )

        transcripts = [
            v.artifact.transcript for v in voice_results.values() if v.artifact
        ]
        verified_speech = bool(transcripts) and all(t for t in transcripts)
        spoken = " ".join(
            (v.artifact.transcript or v.artifact.brief.text)
            for v in voice_results.values()
            if v.artifact
        )
        # Not the planned total: cues have to fit the file that will play.
        # Measured placement of the burned-in text, not the declared intention.
        extent = getattr(
            self,
            "_subtitle_extent",
            (self.config.subtitle_text_top, self.config.subtitle_text_bottom),
        )
        collect(
            self.subtitle_critic.review(
                assets.subtitles,
                spoken_text=spoken,
                language=brief.language,
                video_duration_s=delivered_s,
                text_top=extent[0],
                text_bottom=extent[1],
                verified=verified_speech,
            )
        )
        collect(
            self.audio_critic.review(
                voice_stem=assets.voice_clips.get("_track"),
                music_stem=assets.music,
                final_mix=_audio_for_analysis(assets),
                sfx=tuple(assets.sfx),
            )
        )
        collect(
            self.cover_critic.review(
                assets.cover,
                cover_measurements,
                cover_ppm=getattr(self, "_cover_ppm", None),
            )
        )
        collect(self.perceptual_gate.review(perceptual_samples))

        if diagnostic:
            # A diagnostic run gathered evidence past a known block. It reports
            # what it found and can never approve the Reel.
            results.append(
                GateResult(
                    name="reel.production",
                    verdict=Verdict.HOLD,
                    critical=True,
                    reason=(
                        "diagnostic run: the pipeline continued past a blocking "
                        "stage to collect evidence, so this result is never an "
                        "approval"
                    ),
                )
            )

        report = self.final_gate.evaluate(results)
        scores = score_categories(report)
        claim = world_class(scores, self.thresholds)

        if report.passed and not diagnostic:
            self._checkpoint(reel_id, StageState.FINAL_QA)
            self._checkpoint(reel_id, StageState.READY_FOR_OWNER_REVIEW)
            return self._close_growth_loop(ReelResult(
                reel_id=reel_id,
                verdict=Verdict.PASS,
                stage=StageState.READY_FOR_OWNER_REVIEW,
                brief=brief,
                assets=assets,
                report=report,
                scores=scores,
                quality_claim=claim,
                reason=(
                    f"all {len(FINAL_GATE_CATEGORIES)} critical categories passed; "
                    f"state={TERMINAL_APPROVED_STATE} (publishing remains on HOLD)"
                ),
                owner=self.name,
            ), diagnostic=diagnostic)

        decision: RepairDecision = self.repair_router.route(diagnoses)
        repairs.append(
            {
                "blocking": [r.name for r in report.blocking],
                **decision.to_dict(),
            }
        )
        verdict = _blocked_verdict(report)
        stage = StageState.HELD if verdict is Verdict.HOLD else StageState.FAILED
        self._checkpoint(reel_id, stage, allow_regression=True)
        return self._close_growth_loop(ReelResult(
            reel_id=reel_id,
            verdict=verdict,
            stage=stage,
            brief=brief,
            assets=assets,
            report=report,
            diagnoses=diagnoses,
            repairs=repairs,
            scores=scores,
            quality_claim=claim,
            reason=(
                "blocking: "
                + ", ".join(f"{r.name}={r.verdict.value}" for r in report.blocking)
            ),
            owner=self.name,
        ), diagnostic=diagnostic)

    def _close_growth_loop(
        self, result: ReelResult, *, diagnostic: bool = False
    ) -> ReelResult:
        """Report the finished Reel to the Growth Engine, if one is attached.

        A failure to record must never change the Reel's verdict, so the error
        is captured instead of raised — and kept, so a permanently broken growth
        engine is distinguishable from a studio that produced nothing.
        """
        if self.growth is None:
            return result
        try:
            self.growth.observe(result, diagnostic=diagnostic)
        except Exception as exc:  # noqa: BLE001 - bookkeeping never alters a verdict
            self.growth_errors.append(
                f"{result.reel_id}: {type(exc).__name__}: {exc}"
            )
        return result

    # ---- reporting -------------------------------------------------------
    def status(self, reel_id: str) -> dict:
        cp = self.checkpoints.load(reel_id)
        lease = self.ownership.current(reel_id)
        return {
            "reel_id": reel_id,
            "stage": cp.stage.value if cp else StageState.CREATED.value,
            "owner": lease.owner if lease else None,
            "journal": self.checkpoints.journal(reel_id),
            "journal_integrity": self.checkpoints.journal_integrity(reel_id),
            "publishing": "HOLD" if PUBLISHING_HOLD else "OPEN",
            "growth_errors": list(self.growth_errors),
            "gpu": self.gpu.status(),
            "voice_backends": self.voice_team.backends.status(),
            "reel_backends": self.backends.status(),
        }


# ---- gate helpers --------------------------------------------------------
def _voice_gate(voice_results: Mapping[int, VoiceVerdict]) -> GateResult:
    if not voice_results:
        return GateResult(
            name="reel.voice",
            verdict=Verdict.MISSING,
            critical=True,
            reason="no voice was produced for this reel",
        )
    failing = [
        (idx, v) for idx, v in voice_results.items() if v.verdict is not Verdict.PASS
    ]
    if failing:
        return GateResult(
            name="reel.voice",
            verdict=Verdict.FAIL,
            critical=True,
            reason="; ".join(
                f"shot {idx}: {v.verdict.value} {v.reason}" for idx, v in failing[:3]
            ),
        )
    return GateResult(
        name="reel.voice",
        verdict=Verdict.PASS,
        critical=True,
        reason=f"{len(voice_results)} voice clip(s) passed every critical voice gate",
    )


def _audio_for_analysis(assets: ReelAssets) -> Optional[str]:
    """The mixed WAV is what the loudness analyser can read directly.

    The muxed MP4 is the deliverable, but PCM analysis needs the uncompressed
    mix; they are the same programme, so measuring the mix is honest.
    """
    mix = Path(str(assets.edit or "")).parent.parent / "audio"
    if assets.final:
        candidate = mix / (Path(assets.final).stem + ".mix.wav")
        if candidate.exists():
            return str(candidate)
    track = assets.voice_clips.get("_track")
    return track


def _blocked_verdict(report) -> Verdict:
    verdicts = {r.verdict for r in report.blocking}
    if verdicts & {Verdict.NOT_MEASURED, Verdict.MISSING, Verdict.ERROR}:
        return Verdict.HOLD
    return Verdict.FAIL


