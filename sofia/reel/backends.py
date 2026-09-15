"""Media backends for the Reel Production Team.

Same discipline as the Voice Team: each capability is a protocol, with a real
adapter for the studio machine and an explicit unavailable adapter everywhere
else. Nothing here ever invents a placeholder frame or a silent track — an
absent backend raises, and the critic that depended on it blocks.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Protocol, Sequence, runtime_checkable

from sofia.core.errors import BackendUnavailableError
from sofia.reel.contracts import Shot
from sofia.reel.shots import GeneratorProfile


def _resolve_binary(binary: str) -> str:
    """Resolve a tool on PATH, or accept an absolute path that is executable.

    ``ffmpeg`` additionally falls back to an ``imageio-ffmpeg`` bundled binary
    when one is installed, so a machine with the wheel but no system ffmpeg is
    reported as capable rather than missing.
    """
    found = shutil.which(binary)
    if found:
        return found
    if Path(binary).name.startswith("ffmpeg"):
        bundled = _imageio_ffmpeg()
        if bundled:
            return bundled
    return binary


def _imageio_ffmpeg() -> Optional[str]:
    try:
        import imageio_ffmpeg
    except Exception:  # noqa: BLE001 - optional dependency
        return None
    try:
        path = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        return None
    return path if path and os.path.isfile(path) else None


def _executable(path: str) -> bool:
    return bool(path) and (
        shutil.which(path) is not None
        or (os.path.isfile(path) and os.access(path, os.X_OK))
    )


@runtime_checkable
class VideoBackend(Protocol):
    name: str

    def available(self) -> bool: ...

    def render(self, shot: Shot, profile: GeneratorProfile, out_path: Path) -> Path: ...


@runtime_checkable
class LipSyncBackend(Protocol):
    name: str
    champion: bool

    def available(self) -> bool: ...

    def sync(self, video: Path, audio: Path, out_path: Path) -> Path: ...


@runtime_checkable
class EditorBackend(Protocol):
    """Cuts, transitions, ducking, subtitles burn-in, reframe, cover frame."""

    name: str

    def available(self) -> bool: ...

    def assemble(self, spec: dict, out_path: Path) -> Path: ...

    def probe(self, path: Path) -> dict: ...

    def extract_frame(self, video: Path, at_s: float, out_path: Path) -> Path: ...


class UnavailableVideo:
    def __init__(self, reason: str = "no video generation backend") -> None:
        self.name = "unavailable-video"
        self.reason = reason

    def available(self) -> bool:
        return False

    def render(self, shot: Shot, profile: GeneratorProfile, out_path: Path) -> Path:
        raise BackendUnavailableError(
            f"cannot render shot {shot.index} ({shot.function}): {self.reason}"
        )


class UnavailableLipSync:
    def __init__(self, reason: str = "no lip-sync backend") -> None:
        self.name = "unavailable-lipsync"
        self.champion = False
        self.reason = reason

    def available(self) -> bool:
        return False

    def sync(self, video: Path, audio: Path, out_path: Path) -> Path:
        raise BackendUnavailableError(f"cannot lip-sync: {self.reason}")


class UnavailableEditor:
    def __init__(self, reason: str = "no editor backend (ffmpeg missing)") -> None:
        self.name = "unavailable-editor"
        self.reason = reason

    def available(self) -> bool:
        return False

    def assemble(self, spec: dict, out_path: Path) -> Path:
        raise BackendUnavailableError(f"cannot assemble the edit: {self.reason}")

    def probe(self, path: Path) -> dict:
        raise BackendUnavailableError(f"cannot probe media: {self.reason}")

    def extract_frame(self, video: Path, at_s: float, out_path: Path) -> Path:
        raise BackendUnavailableError(f"cannot extract a cover frame: {self.reason}")

    def mix_audio(self, voice: Path, music: Path, out_path: Path, duck_db: float) -> Path:
        raise BackendUnavailableError(f"cannot mix audio: {self.reason}")


class ComfyUIBackend:
    """Adapter for the studio's local ComfyUI (Wan2.2 I2V / T2V workflows)."""

    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:8188",
        workflows: Optional[dict[str, str]] = None,
        timeout_s: float = 1800.0,
    ) -> None:
        self.name = "comfyui"
        self.endpoint = endpoint.rstrip("/")
        self.workflows = dict(workflows or {})
        self.timeout_s = timeout_s

    def available(self) -> bool:
        import urllib.request

        try:
            with urllib.request.urlopen(  # noqa: S310 - localhost only
                f"{self.endpoint}/system_stats", timeout=3
            ):
                return True
        except Exception:  # noqa: BLE001
            return False

    def render(self, shot: Shot, profile: GeneratorProfile, out_path: Path) -> Path:
        workflow = self.workflows.get(profile.name)
        if not workflow:
            raise BackendUnavailableError(
                f"no ComfyUI workflow registered for profile {profile.name!r}; "
                "register the studio's canonical workflow rather than improvising one"
            )
        if not Path(workflow).exists():
            raise BackendUnavailableError(f"workflow file missing: {workflow}")
        raise BackendUnavailableError(
            "ComfyUI job submission must run against the studio's canonical runner; "
            "this adapter refuses to reimplement the production graph"
        )


class FfmpegEditor:
    """Editor backed by ffmpeg — cuts, concat, ducking, subtitles, cover frame."""

    def __init__(
        self,
        binary: str = "ffmpeg",
        probe_binary: str = "ffprobe",
        *,
        resolve: bool = True,
    ) -> None:
        self.name = "ffmpeg"
        self.binary = _resolve_binary(binary) if resolve else binary
        self.probe_binary = _resolve_binary(probe_binary) if resolve else probe_binary

    def available(self) -> bool:
        return _executable(self.binary)

    def probe(self, path: Path) -> dict:
        """Return an ffprobe-shaped dict, falling back to ffmpeg when needed.

        Some installs ship ffmpeg without ffprobe. Parsing ``ffmpeg -i`` output
        is a real decode attempt, so the decode gate stays meaningful either
        way.
        """
        if not self.available():
            raise BackendUnavailableError("ffmpeg is not available")
        if _executable(self.probe_binary):
            proc = subprocess.run(
                [
                    self.probe_binary,
                    "-v",
                    "error",
                    "-show_format",
                    "-show_streams",
                    "-of",
                    "json",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if proc.returncode != 0:
                raise BackendUnavailableError(
                    f"ffprobe failed: {proc.stderr.strip()[:300]}"
                )
            return json.loads(proc.stdout)
        return self._probe_with_ffmpeg(path)

    def _probe_with_ffmpeg(self, path: Path) -> dict:
        proc = subprocess.run(
            [self.binary, "-hide_banner", "-i", str(path), "-f", "null", "-"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        text = proc.stderr
        if "Invalid data found" in text or "No such file" in text:
            raise BackendUnavailableError(f"file does not decode: {path}")
        m = re.search(r"Duration:\s*(\d+):(\d\d):(\d\d(?:\.\d+)?)", text)
        if not m:
            raise BackendUnavailableError(f"could not read a duration from {path}")
        duration = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        streams: list[dict] = []
        for sm in re.finditer(r"Stream #\d+:\d+.*?: (Video|Audio): ([^,\s]+)", text):
            streams.append(
                {"codec_type": sm.group(1).lower(), "codec_name": sm.group(2)}
            )
        return {
            "format": {"duration": f"{duration:.3f}", "filename": str(path)},
            "streams": streams,
        }

    def extract_frame(self, video: Path, at_s: float, out_path: Path) -> Path:
        if not self.available():
            raise BackendUnavailableError("ffmpeg is not available")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [
                self.binary,
                "-y",
                "-ss",
                f"{at_s:.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(out_path),
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if proc.returncode != 0 or not out_path.exists():
            raise BackendUnavailableError(
                f"cover frame extraction failed: {proc.stderr.strip()[:300]}"
            )
        return out_path

    def mix_audio(
        self, voice: Path, music: Path, out_path: Path, duck_db: float = 12.0
    ) -> Path:
        """Mix the voice over the music bed with a real sidechain compressor."""
        if not self.available():
            raise BackendUnavailableError("ffmpeg is not available")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ratio = max(2.0, min(20.0, duck_db / 2.0))
        graph = (
            "[1:a]asplit=2[sc][mus];"
            f"[mus][sc]sidechaincompress=threshold=0.02:ratio={ratio:.1f}:"
            "attack=20:release=350[ducked];"
            "[0:a][ducked]amix=inputs=2:duration=first:dropout_transition=0,"
            "alimiter=limit=0.9[out]"
        )
        proc = subprocess.run(
            [
                self.binary, "-y",
                "-i", str(voice),
                "-i", str(music),
                "-filter_complex", graph,
                "-map", "[out]",
                "-c:a", "pcm_s16le",
                str(out_path),
            ],
            capture_output=True,
            text=True,
            timeout=900,
        )
        if proc.returncode != 0 or not out_path.exists():
            raise BackendUnavailableError(
                f"audio mix failed: {proc.stderr.strip()[-400:]}"
            )
        return out_path

    def assemble(self, spec: dict, out_path: Path) -> Path:
        """Assemble the edit from a declarative spec.

        The spec is produced by :mod:`sofia.reel.stages` (clips, music bed,
        ducking, subtitle file, safe zones). Assembly runs through the studio's
        canonical edit graph; this adapter only executes it.
        """
        if not self.available():
            raise BackendUnavailableError("ffmpeg is not available")
        clips: Sequence[str] = spec.get("clips", ())
        if not clips:
            raise BackendUnavailableError("edit spec contains no clips")
        missing = [c for c in clips if not Path(c).exists()]
        if missing:
            raise BackendUnavailableError(f"edit spec references missing clips: {missing}")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        list_file = out_path.parent / f"{out_path.stem}.concat.txt"
        list_file.write_text(
            "\n".join(f"file '{Path(c).as_posix()}'" for c in clips) + "\n",
            encoding="utf-8",
        )
        cmd = [self.binary, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file)]
        audio_track = spec.get("audio")
        if audio_track:
            cmd += ["-i", str(audio_track)]
        cmd += [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(spec.get("fps", 24)),
        ]
        burn = spec.get("subtitles_burn") or spec.get("subtitles")
        if burn:
            cmd += [
                "-vf",
                _subtitle_filter(
                    str(burn),
                    height=int(spec.get("height", 960)),
                    safe_bottom=float(spec.get("safe_zones", {}).get("bottom", 0.80)),
                    font_size=spec.get("subtitle_font_size"),
                ),
            ]
        if audio_track:
            cmd += ["-map", "0:v:0", "-map", "1:a:0", "-shortest"]
        cmd += ["-c:a", "aac", "-b:a", "192k", str(out_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if proc.returncode != 0 or not out_path.exists():
            raise BackendUnavailableError(
                f"edit assembly failed: {proc.stderr.strip()[:400]}"
            )
        return out_path


def _escape_filter_path(path: str) -> str:
    """Escape a path for use inside an ffmpeg filter argument."""
    return path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def _subtitle_filter(
    path: str,
    *,
    height: int,
    safe_bottom: float,
    font_size: Optional[int] = None,
) -> str:
    """Burn subtitles in *above* the bottom safe zone.

    The renderer's default places text hard against the bottom edge, inside the
    platform UI zone, and re-wraps lines at its own font size. Both are set
    explicitly here so what is burned in matches what the subtitle verifier
    checked.
    """

    escaped = _escape_filter_path(path)
    if path.lower().endswith(".ass"):
        # The ASS file already carries PlayRes, style and margins, so nothing is
        # overridden here.
        return f"subtitles={escaped}"
    margin_v = max(24, int(round(height * (1.0 - safe_bottom))))
    size = font_size or max(20, int(round(height * 0.036)))
    style = (
        f"FontSize={size},Alignment=2,MarginV={margin_v},"
        "MarginL=48,MarginR=48,BorderStyle=1,Outline=2,Shadow=0,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H90000000,WrapStyle=2"
    )
    return f"subtitles={escaped}:force_style='{style}'"


class LatentSyncBackend:
    """The proven champion lip-sync path used by the studio."""

    def __init__(self, runner: str = "", champion: bool = True) -> None:
        self.name = "latentsync-champion"
        self.champion = champion
        self.runner = runner

    def available(self) -> bool:
        return bool(self.runner) and Path(self.runner).exists()

    def sync(self, video: Path, audio: Path, out_path: Path) -> Path:
        if not self.available():
            raise BackendUnavailableError(
                "the champion lip-sync runner is not present on this machine"
            )
        raise BackendUnavailableError(
            "lip-sync must run through the studio's canonical runner; this adapter "
            "refuses to rebuild the production graph from memory"
        )


@dataclass
class ReelBackends:
    """The media backends the Reel team was given."""

    video: VideoBackend
    lipsync: LipSyncBackend
    editor: EditorBackend
    challengers: dict[str, LipSyncBackend] = field(default_factory=dict)

    @classmethod
    def unavailable(cls, reason: str) -> "ReelBackends":
        return cls(
            video=UnavailableVideo(reason),
            lipsync=UnavailableLipSync(reason),
            editor=UnavailableEditor(reason),
        )

    def status(self) -> dict:
        return {
            "video": {"name": self.video.name, "available": self.video.available()},
            "lipsync": {
                "name": self.lipsync.name,
                "available": self.lipsync.available(),
                "champion": getattr(self.lipsync, "champion", False),
            },
            "editor": {"name": self.editor.name, "available": self.editor.available()},
            "lipsync_challengers": {
                k: v.available() for k, v in self.challengers.items()
            },
        }


def detect_reel_backends(config_path: Optional[str | Path] = None) -> ReelBackends:
    """Wire real backends where present; otherwise fail closed."""

    cfg: dict = {}
    if config_path and Path(config_path).exists():
        cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))

    video: VideoBackend = ComfyUIBackend(
        endpoint=cfg.get("comfyui_endpoint", "http://127.0.0.1:8188"),
        workflows=cfg.get("comfyui_workflows", {}),
    )
    if not video.available():
        video = UnavailableVideo("ComfyUI is not reachable on this machine")

    lipsync: LipSyncBackend = LatentSyncBackend(runner=cfg.get("lipsync_runner", ""))
    if not lipsync.available():
        lipsync = UnavailableLipSync("champion lip-sync runner not present")

    editor: EditorBackend = FfmpegEditor(
        binary=cfg.get("ffmpeg", "ffmpeg"), probe_binary=cfg.get("ffprobe", "ffprobe")
    )
    if not editor.available():
        editor = UnavailableEditor("ffmpeg/ffprobe not on PATH")

    # New technologies (LongCat, HighSync, ...) enter only as challengers and
    # never replace the champion without a won benchmark.
    challengers: dict[str, LipSyncBackend] = {}
    for name, runner in (cfg.get("lipsync_challengers") or {}).items():
        challengers[name] = LatentSyncBackend(runner=runner, champion=False)

    return ReelBackends(
        video=video, lipsync=lipsync, editor=editor, challengers=challengers
    )
