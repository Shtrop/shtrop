"""Shot-type routing: the right generator profile for the right shot.

Requiring Sofia's face in a shot that does not need it wastes GPU, invites
identity failures and flattens the visual language. This module makes the
routing explicit and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from sofia.reel.contracts import Shot, ShotType, StoryBeat


@dataclass(frozen=True)
class GeneratorProfile:
    """How a shot type should be generated."""

    name: str
    model: str
    resolution: str
    fps: int
    needs_identity_gate: bool
    needs_lipsync: bool
    vram_gb: float
    est_seconds_per_second: float
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "model": self.model,
            "resolution": self.resolution,
            "fps": self.fps,
            "needs_identity_gate": self.needs_identity_gate,
            "needs_lipsync": self.needs_lipsync,
            "vram_gb": self.vram_gb,
            "est_seconds_per_second": self.est_seconds_per_second,
            "notes": self.notes,
        }


#: Profiles follow the studio's proven branch: 720p for identity work, native
#: 24 fps. Cheap shot types deliberately avoid the identity pipeline.
PROFILES: Mapping[ShotType, GeneratorProfile] = {
    ShotType.FACE_CRITICAL: GeneratorProfile(
        name="identity_first_720p",
        model="wan2.2-i2v+pulid",
        resolution="720x1280",
        fps=24,
        needs_identity_gate=True,
        needs_lipsync=False,
        vram_gb=22.0,
        est_seconds_per_second=55.0,
        notes="IDENTITY_FIRST: strict identity gate, never lower the threshold.",
    ),
    ShotType.TALKING: GeneratorProfile(
        name="talking_720p_lipsync",
        model="wan2.2-i2v+pulid+lipsync",
        resolution="720x1280",
        fps=24,
        needs_identity_gate=True,
        needs_lipsync=True,
        vram_gb=24.0,
        est_seconds_per_second=75.0,
        notes="Face and mouth both gated; the champion lip-sync model applies.",
    ),
    ShotType.PAYOFF: GeneratorProfile(
        name="payoff_720p",
        model="wan2.2-i2v+pulid",
        resolution="720x1280",
        fps=24,
        needs_identity_gate=True,
        needs_lipsync=False,
        vram_gb=22.0,
        est_seconds_per_second=55.0,
    ),
    ShotType.MEDIUM: GeneratorProfile(
        name="medium_720p",
        model="wan2.2-i2v",
        resolution="720x1280",
        fps=24,
        needs_identity_gate=False,
        needs_lipsync=False,
        vram_gb=16.0,
        est_seconds_per_second=35.0,
        notes="Face may be present but is not the subject; soft identity check only.",
    ),
    ShotType.B_ROLL: GeneratorProfile(
        name="broll_1080p_fast",
        model="wan2.2-t2v-fast",
        resolution="1080x1920",
        fps=24,
        needs_identity_gate=False,
        needs_lipsync=False,
        vram_gb=12.0,
        est_seconds_per_second=18.0,
        notes="No face required — cheapest path, best visual variety.",
    ),
    ShotType.DETAIL: GeneratorProfile(
        name="detail_macro",
        model="wan2.2-t2v-fast",
        resolution="1080x1920",
        fps=24,
        needs_identity_gate=False,
        needs_lipsync=False,
        vram_gb=10.0,
        est_seconds_per_second=14.0,
        notes="Hands, cup, screen, texture. No identity pipeline at all.",
    ),
    ShotType.TRANSITION: GeneratorProfile(
        name="transition_cheap",
        model="procedural",
        resolution="1080x1920",
        fps=24,
        needs_identity_gate=False,
        needs_lipsync=False,
        vram_gb=0.0,
        est_seconds_per_second=1.0,
        notes="Editor-side; no video model needed.",
    ),
}


def profile_for(shot_type: ShotType) -> GeneratorProfile:
    return PROFILES[shot_type]


def assign_profiles(shots: Sequence[Shot]) -> list[Shot]:
    """Stamp each shot with the profile its type dictates."""
    for shot in shots:
        shot.generator_profile = profile_for(shot.shot_type).name
    return list(shots)


def estimated_cost(shots: Sequence[Shot]) -> dict:
    """Predicted GPU cost of a shot list, and what face routing saved."""

    total = 0.0
    naive = 0.0
    face_shots = 0
    talking = profile_for(ShotType.TALKING)
    for shot in shots:
        prof = profile_for(shot.shot_type)
        total += prof.est_seconds_per_second * shot.duration_s
        # The naive alternative: force the talking/face pipeline everywhere.
        naive += talking.est_seconds_per_second * shot.duration_s
        if shot.shot_type.needs_face:
            face_shots += 1
    return {
        "estimated_gpu_s": round(total, 1),
        "naive_all_face_gpu_s": round(naive, 1),
        "saved_gpu_s": round(naive - total, 1),
        "face_critical_shots": face_shots,
        "total_shots": len(shots),
        "peak_vram_gb": max(
            (profile_for(s.shot_type).vram_gb for s in shots), default=0.0
        ),
    }


def validate_story(shots: Sequence[Shot]) -> list[str]:
    """A Reel must be SETUP -> DEVELOPMENT -> PAYOFF, and every scene must work.

    Returns a list of structural problems; empty means the arc is sound.
    """

    problems: list[str] = []
    if not shots:
        return ["reel has no shots"]

    beats = [s.beat for s in shots]
    if beats[0] not in (StoryBeat.HOOK, StoryBeat.SETUP):
        problems.append(
            f"reel opens on {beats[0].value}; the first shot must hook or set up"
        )
    for required in (StoryBeat.SETUP, StoryBeat.DEVELOPMENT, StoryBeat.PAYOFF):
        if required not in beats:
            problems.append(f"story arc is missing a {required.value} beat")

    order = {
        StoryBeat.HOOK: 0,
        StoryBeat.SETUP: 1,
        StoryBeat.DEVELOPMENT: 2,
        StoryBeat.PAYOFF: 3,
        StoryBeat.CTA: 4,
    }
    ranks = [order[b] for b in beats]
    if any(b < a for a, b in zip(ranks, ranks[1:])):
        problems.append(
            "beats are out of order: "
            + " -> ".join(b.value for b in beats)
        )

    if not any(s.voice_line for s in shots):
        problems.append("reel has no talking segment")
    if not any(s.shot_type in (ShotType.B_ROLL, ShotType.DETAIL) for s in shots):
        problems.append("reel has no B-roll or detail shot (one portrait is not a reel)")

    for shot in shots:
        if not shot.description.strip():
            problems.append(f"shot {shot.index} has no described function")
        if shot.duration_s <= 0:
            problems.append(f"shot {shot.index} has non-positive duration")
    return problems
