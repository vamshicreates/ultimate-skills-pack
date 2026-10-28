#!/usr/bin/env python3
"""Check the local audio/PDF toolchain without using a film or network access."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "MUS001_Windows_Smoke"


def run(*arguments: str) -> None:
    result = subprocess.run(arguments, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {arguments[0]}\n{result.stderr or result.stdout}")


def main() -> None:
    if sys.version_info < (3, 11):
        raise RuntimeError("Python 3.11 or newer is required")
    for program in ("ffmpeg", "ffprobe"):
        path = shutil.which(program)
        if path is None:
            raise RuntimeError(f"{program} is missing from PATH")
        run(path, "-version")

    with tempfile.TemporaryDirectory(prefix="film-audio-smoke-") as temporary:
        package = Path(temporary) / "Film_Sound"
        cue_dir = package / "SC001_Smoke" / NAME
        cue_dir.parent.mkdir(parents=True)
        spec = {
            "name": NAME,
            "duration": 1.0,
            "seed": 7,
            "events": [
                {"start": 0.0, "duration": 0.9, "instrument": "pad", "pitch": "A3", "gain": 0.2},
                {"start": 0.2, "duration": 0.2, "instrument": "pluck", "pitch": "E5", "gain": 0.2},
            ],
        }
        spec_path = package / "smoke_spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        run(sys.executable, str(ROOT / "scripts" / "render_score.py"), "--spec", str(spec_path), "--out", str(cue_dir))

        mix = cue_dir / f"{NAME}_mix.wav"
        if not mix.is_file():
            raise RuntimeError("The labeled music mix is missing")
        with wave.open(str(mix), "rb") as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()) != (2, 3, 48000, 48000):
                raise RuntimeError("Music mix is not 48 kHz, 24-bit stereo with the expected duration")
            if not any(audio.readframes(audio.getnframes())):
                raise RuntimeError("Music mix is silent")
        for instrument in ("pad", "pluck"):
            stem = cue_dir / f"{NAME}_{instrument}" / f"{NAME}_{instrument}.wav"
            if not stem.is_file():
                raise RuntimeError(f"Labeled {instrument} stem is missing")

        probe = subprocess.run(
            [shutil.which("ffprobe"), "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate,channels", "-of", "json", str(mix)],
            check=True, capture_output=True, text=True,
        )
        stream = json.loads(probe.stdout)["streams"][0]
        if stream != {"codec_name": "pcm_s24le", "sample_rate": "48000", "channels": 2}:
            raise RuntimeError(f"ffprobe reported unexpected WAV format: {stream}")

        sheet = {
            "film_title": "Windows Smoke Test",
            "source_file": "none",
            "frame_rate": "24/1",
            "duration": "00:00:01:00",
            "version": "smoke",
            "scenes": [{
                "id": "SC001", "name": "Smoke", "time": "00:00:00:00-00:00:01:00 (frames 0-23)",
                "picture": "Synthetic validation scene.", "production_audio": "No source audio.",
                "sound_direction": "Verify labeled assets and PDF references.",
                "music": {"cues": [{
                    "id": "MUS001", "name": NAME, "time": "00:00:00:00-00:00:01:00 (frames 0-23)",
                    "sync": "Starts on frame 0.", "description": "Locally synthesized pad and pluck.",
                    "method": "Python synthesis.", "mix": "Stereo reference only.", "status": "delivered",
                    "asset": mix.relative_to(package).as_posix(),
                }]},
                "foley": {"cues": [], "none_reason": "No physical action in the synthetic scene."},
                "ambience": {"cues": [], "none_reason": "No environment in the synthetic scene."},
                "sfx": {"cues": [], "none_reason": "No effect event in the synthetic scene."},
                "silence": {"cues": [], "none_reason": "Music plays throughout the synthetic scene."},
            }],
        }
        sheet_path = package / "smoke_sheet.json"
        sheet_path.write_text(json.dumps(sheet), encoding="utf-8")
        pdf = package / "Smoke_Breakdown.pdf"
        run(sys.executable, str(ROOT / "scripts" / "build_breakdown_pdf.py"), "--sheet", str(sheet_path), "--out", str(pdf), "--assets-root", str(package))
        if not pdf.is_file() or not pdf.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError("The scene breakdown PDF is missing or invalid")

    print("PASS: Python, FFmpeg, labeled 24-bit audio stems, and scene breakdown PDF")


if __name__ == "__main__":
    main()
