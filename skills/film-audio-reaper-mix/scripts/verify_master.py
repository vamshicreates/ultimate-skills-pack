#!/usr/bin/env python3
"""Verify a REAPER film-audio WAV against the locked picture and measure loudness."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
from pathlib import Path


def command(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr[-3000:]}")
    return result


def probe(path: Path) -> dict:
    return json.loads(command(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--master", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    for executable in ("ffmpeg", "ffprobe"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"{executable} is missing from PATH")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    picture = (args.plan.resolve().parent / plan["video"]).resolve()
    if not picture.is_file() or not args.master.is_file():
        raise FileNotFoundError("Picture or master WAV is missing")
    picture_info = probe(picture)
    master_info = probe(args.master)
    video = next((s for s in picture_info.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in master_info.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise ValueError("Picture video or master audio stream is missing")
    picture_duration = float(video.get("duration") or picture_info["format"]["duration"])
    master_duration = float(audio.get("duration") or master_info["format"]["duration"])
    if not math.isfinite(picture_duration) or not math.isfinite(master_duration):
        raise ValueError("Invalid duration")
    if abs(picture_duration - master_duration) > 0.1:
        raise ValueError(f"Master duration {master_duration:.3f}s differs from picture {picture_duration:.3f}s")
    if audio.get("codec_name") != "pcm_s24le" or audio.get("sample_rate") != "48000" or audio.get("channels") != 2:
        raise ValueError("Master must be stereo 48 kHz 24-bit PCM WAV")
    if len([s for s in master_info.get("streams", []) if s.get("codec_type") == "audio"]) != 1:
        raise ValueError("Master must contain one audio stream")
    analysis = command(["ffmpeg", "-hide_banner", "-i", str(args.master), "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
    blocks = re.findall(r'\{\s*"input_i"[\s\S]*?\}', analysis.stderr)
    if not blocks:
        raise RuntimeError("FFmpeg did not return loudness measurements")
    measured = json.loads(blocks[-1])
    integrated_lufs = float(measured["input_i"])
    true_peak_dbfs = float(measured["input_tp"])
    if not math.isfinite(integrated_lufs) or not math.isfinite(true_peak_dbfs):
        raise ValueError("The master is silent or loudness measurement failed")
    report = {
        "title": plan.get("title"), "picture": str(picture), "master": str(args.master.resolve()),
        "picture_duration_seconds": picture_duration, "master_duration_seconds": master_duration,
        "sample_rate_hz": 48000, "channels": 2, "codec": "pcm_s24le",
        "integrated_lufs": integrated_lufs, "true_peak_dbfs": true_peak_dbfs,
        "delivery_target_from_plan": plan.get("mastering"),
        "note": "Measurements do not replace listening and sync review in REAPER.",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"VALID: {master_duration:.3f}s, {integrated_lufs:.1f} LUFS, {true_peak_dbfs:.1f} dBTP\nREPORT: {args.report}")


if __name__ == "__main__":
    main()
