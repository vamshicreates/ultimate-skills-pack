#!/usr/bin/env python3
"""Render a synthetic picture and cue to validate the final-film toolchain."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(args: list[str]) -> None:
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(args[:3])}\n{result.stderr[-4000:]}")


def main() -> None:
    if sys.version_info < (3, 11):
        raise RuntimeError("Python 3.11 or newer is required")
    for program in ("ffmpeg", "ffprobe"):
        if shutil.which(program) is None:
            raise RuntimeError(f"{program} is missing from PATH")
    with tempfile.TemporaryDirectory(prefix="film-finish-smoke-") as temporary:
        base = Path(temporary)
        video = base / "picture.mp4"
        package = base / "Film_Sound"
        cue = package / "SC001_Smoke" / "MUS001_Smoke" / "MUS001_Smoke_mix.wav"
        cue.parent.mkdir(parents=True)
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
             "testsrc2=size=320x180:rate=24", "-f", "lavfi", "-i",
             "sine=frequency=440:sample_rate=48000", "-t", "2", "-c:v", "mpeg4", "-q:v", "2",
             "-c:a", "aac", "-b:a", "128k", str(video)])
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
             "sine=frequency=220:sample_rate=48000", "-t", "0.8", "-c:a", "pcm_s24le", str(cue)])
        plan = base / "mix_plan.json"
        plan.write_text(json.dumps({
            "title": "Smoke_Film", "video": str(video), "audio_package": str(package),
            "output_dir": str(base / "Final"), "source_audio": {"mode": "keep", "gain_db": -18},
            "mastering": {"integrated_lufs": -16, "true_peak_dbfs": -1.5, "lra": 11},
            "cues": [{"id": "MUS001", "asset": "SC001_Smoke/MUS001_Smoke/MUS001_Smoke_mix.wav",
                      "start_seconds": 0.5, "gain_db": -4, "fade_in_seconds": 0.02,
                      "fade_out_seconds": 0.1}],
        }), encoding="utf-8")
        run([sys.executable, str(ROOT / "finish_film.py"), "--plan", str(plan), "--validate-only"])
        run([sys.executable, str(ROOT / "finish_film.py"), "--plan", str(plan)])
        output = base / "Final"
        report = json.loads((output / "Smoke_Film_Render_Report.json").read_text(encoding="utf-8"))
        if report["checks"]["video_frames"] != "48":
            raise RuntimeError("The finished video did not retain its 48 picture frames")
        for name in ("Smoke_Film_Final_With_Audio.mp4", "Smoke_Film_Master_48k24.wav",
                     "Smoke_Film_Mix_Plan.json"):
            if not (output / name).is_file():
                raise RuntimeError(f"Missing output: {name}")
    print("PASS: picture frames, synchronized sound, master WAV, final video, and render report")


if __name__ == "__main__":
    main()
