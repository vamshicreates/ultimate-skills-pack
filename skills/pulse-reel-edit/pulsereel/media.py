"""FFmpeg plumbing: locate ffmpeg, probe files, stream-decode frames, encode output.

Cross-platform: uses the system ffmpeg when it is on PATH, otherwise the static
binary that ships with the `imageio-ffmpeg` wheel (macOS, Windows, Linux).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".mts", ".m2ts", ".webm", ".mxf", ".3gp"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".aiff", ".aif", ".wma"}

_FFMPEG: str | None = None
_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW


def ffmpeg_exe() -> str:
    """Return a working ffmpeg path (env PULSE_FFMPEG > PATH > imageio-ffmpeg)."""
    global _FFMPEG
    if _FFMPEG:
        return _FFMPEG
    cand = os.environ.get("PULSE_FFMPEG") or shutil.which("ffmpeg")
    if not cand:
        try:
            import imageio_ffmpeg  # type: ignore

            cand = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "ffmpeg not found. Run `python -m pip install imageio-ffmpeg` "
                "or install ffmpeg and put it on PATH."
            ) from exc
    _FFMPEG = cand
    return cand


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, creationflags=_NO_WINDOW, **kw)


def popen(cmd: list[str], **kw) -> subprocess.Popen:
    return subprocess.Popen(cmd, creationflags=_NO_WINDOW, **kw)


@dataclass
class Probe:
    path: str
    duration: float
    width: int  # display width (after rotation)
    height: int
    fps: float
    codec: str
    pix_fmt: str
    transfer: str  # e.g. bt709, arib-std-b67 (HLG), smpte2084 (PQ)
    rotation: int
    has_audio: bool

    @property
    def is_hdr(self) -> bool:
        return self.transfer in ("arib-std-b67", "smpte2084") or "bt2020" in self.transfer

    @property
    def aspect(self) -> float:
        return self.width / max(1, self.height)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["is_hdr"] = self.is_hdr
        return d


def probe(path: str | Path) -> Probe:
    """Probe a media file by parsing `ffmpeg -i` (works without ffprobe)."""
    path = str(path)
    p = run([ffmpeg_exe(), "-hide_banner", "-i", path], capture_output=True, text=True,
            encoding="utf-8", errors="replace")
    err = p.stderr
    dur = 0.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", err)
    if m:
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    vline = None
    for line in err.splitlines():
        if re.search(r"Stream #\S+.*Video:", line) and "attached pic" not in line:
            vline = line
            break
    width = height = 0
    fps = 0.0
    codec = pix = transfer = ""
    if vline:
        m = re.search(r"Video:\s*([\w\-]+)", vline)
        codec = m.group(1) if m else ""
        after = vline.split("Video:", 1)[1]
        m = re.search(r",\s*([a-z0-9_]+)(?:\(([^)]*)\))?", after[len(codec) + 1:] if codec else after)
        # pix_fmt is the first token after the codec block that looks like yuv/rgb/etc.
        m = re.search(r"\b((?:yuv|yuvj|rgb|bgr|gbr|nv|p0|gray)[a-z0-9_]*)(?:\(([^)]*)\))?", after)
        if m:
            pix = m.group(1)
            if m.group(2):
                parts = [s.strip() for s in m.group(2).split(",")]
                # forms: "tv, bt709" | "tv, bt2020nc/bt2020/arib-std-b67" | "progressive"
                for s in parts:
                    if "/" in s:
                        transfer = s.split("/")[-1]
                    elif s in ("bt709", "smpte170m", "bt470bg", "bt2020nc"):
                        transfer = transfer or s
        m = re.search(r",\s*(\d{2,5})x(\d{2,5})", after)
        if m:
            width, height = int(m.group(1)), int(m.group(2))
        m = re.search(r"([\d.]+)\s*fps", after) or re.search(r"([\d.]+)\s*tbr", after)
        if m:
            fps = float(m.group(1))
    rot = 0
    m = re.search(r"rotation of\s*(-?[\d.]+)\s*degrees", err) or re.search(r"rotate\s*:\s*(-?\d+)", err)
    if m:
        rot = int(round(float(m.group(1)))) % 360
    if rot in (90, 270):
        width, height = height, width
    has_audio = bool(re.search(r"Stream #\S+.*Audio:", err))
    return Probe(path, dur, width, height, fps or 30.0, codec, pix, transfer or "bt709", rot, has_audio)


HDR_TONEMAP = (
    "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
    "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
)


class FrameReader:
    """Stream frames of one clip, cropped to `cover` the requested size.

    Frames come out as uint8 BGR arrays (h, w, 3) at the clip's native frame rate,
    starting at `t0`. `focus` = (fx, fy) in 0..1 picks which part survives the crop
    when the clip's aspect differs from the output (0.5, 0.5 = centre).
    """

    def __init__(self, info: Probe, t0: float, dur: float, w: int, h: int,
                 focus=(0.5, 0.5), tonemap: bool | None = None, fps: float | None = None):
        self.info, self.w, self.h = info, w, h
        self.fps = fps or (info.fps if info.fps > 1 else 30.0)
        fx, fy = focus
        vf = []
        use_tm = info.is_hdr if tonemap is None else tonemap
        if use_tm:
            vf.append(HDR_TONEMAP)
        vf.append(f"fps={self.fps:.6f}")
        vf.append(f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos")
        vf.append(f"crop={w}:{h}:(iw-{w})*{fx:.4f}:(ih-{h})*{fy:.4f}")
        self.vf = ",".join(vf)
        self.t0, self.dur = max(0.0, t0), max(0.05, dur)
        self._open()

    def _open(self):
        cmd = [ffmpeg_exe(), "-v", "error", "-ss", f"{self.t0:.4f}", "-i", self.info.path,
               "-t", f"{self.dur:.4f}", "-vf", self.vf, "-an", "-sn",
               "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
        self.proc = popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.nbytes = self.w * self.h * 3
        self.count = 0
        self.last = None
        # HDR filter chain may be unavailable in some ffmpeg builds: detect and retry plain.
        first = self.proc.stdout.read(self.nbytes)
        if len(first) < self.nbytes and "zscale" in self.vf:
            self.proc.kill()
            self.vf = self.vf.replace(HDR_TONEMAP + ",", "")
            sys.stderr.write(f"[pulse] HDR tonemap unavailable in this ffmpeg; decoding {Path(self.info.path).name} without it\n")
            self._open()
            return
        self._pending = first

    def read(self):
        if self._pending is not None:
            buf, self._pending = self._pending, None
        else:
            buf = self.proc.stdout.read(self.nbytes)
        if len(buf) < self.nbytes:
            return None
        self.count += 1
        self.last = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
        return self.last

    def close(self):
        try:
            self.proc.stdout.close()
            self.proc.kill()
            self.proc.wait(timeout=5)
        except Exception:
            pass


class Writer:
    """Pipe BGR frames into ffmpeg (H.264, yuv420p, faststart)."""

    def __init__(self, path: str | Path, w: int, h: int, fps: float, crf: int = 16,
                 preset: str = "medium", audio: str | None = None, audio_start: float = 0.0,
                 duration: float | None = None, audio_fade: float = 0.6, prores: bool = False):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        cmd = [ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
               "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-"]
        if audio:
            cmd += ["-ss", f"{audio_start:.4f}", "-i", str(audio)]
        if prores:
            cmd += ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"]
        else:
            cmd += ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
                    "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-colorspace", "bt709", "-movflags", "+faststart"]
        if audio:
            af = []
            if duration:
                af.append(f"afade=t=out:st={max(0, duration - audio_fade):.3f}:d={audio_fade:.3f}")
            cmd += ["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac" if not prores else "pcm_s16le",
                    "-b:a", "256k"]
            if af:
                cmd += ["-af", ",".join(af)]
            if duration:
                cmd += ["-t", f"{duration:.4f}"]
        cmd.append(self.path)
        self.proc = popen(cmd, stdin=subprocess.PIPE)

    def write(self, frame: np.ndarray):
        self.proc.stdin.write(np.ascontiguousarray(frame, dtype=np.uint8).tobytes())

    def close(self):
        self.proc.stdin.close()
        rc = self.proc.wait()
        if rc != 0:
            raise RuntimeError(f"ffmpeg encode failed for {self.path} (exit {rc})")


def extract_wav(src: str | Path, dst: str | Path, sr: int = 22050) -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    p = run([ffmpeg_exe(), "-y", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", str(sr), str(dst)],
            capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"could not read audio from {src}: {p.stderr[-400:]}")
    return dst


def list_media(folder: str | Path):
    folder = Path(folder)
    vids, auds = [], []
    for f in sorted(folder.rglob("*")):
        if not f.is_file() or f.name.startswith("."):
            continue
        ext = f.suffix.lower()
        if ext in VIDEO_EXT:
            vids.append(f)
        elif ext in AUDIO_EXT:
            auds.append(f)
    return vids, auds


def save_json(obj, path: str | Path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
