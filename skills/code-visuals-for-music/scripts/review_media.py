#!/usr/bin/env python3
"""Extract a playback proof and a contact strip; never infer artistic approval."""
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path


def run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--seconds", type=float, default=4)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.start) or not math.isfinite(args.seconds) or args.start < 0 or args.seconds <= 0:
        parser.error("start must be nonnegative and seconds positive, both finite")
    if not all(shutil.which(tool) for tool in ("ffmpeg", "ffprobe")):
        parser.error("ffmpeg and ffprobe must be on PATH")
    source = args.media.resolve()
    try:
        meta = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(source)]))
        if not any(s.get("codec_type") == "video" for s in meta["streams"]):
            parser.error("source must have a video stream")
        duration = float(meta["format"]["duration"])
        if args.start >= duration:
            parser.error("start must be before the end of the video")
        span = min(args.seconds, duration - args.start)
        args.out.mkdir(parents=True, exist_ok=True)
        outputs = [args.out / n for n in ("proof.mp4", "strip.jpg", "metadata.json")]
        if any(p.exists() for p in outputs):
            parser.error("output files already exist; choose a fresh review directory")
        common = ["ffmpeg", "-nostdin", "-v", "error", "-n", "-ss", str(args.start), "-i", str(source), "-t", str(span)]
        run(common + ["-map", "0:v:0", "-map", "0:a:0?", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(outputs[0])])
        run(["ffmpeg", "-nostdin", "-v", "error", "-n", "-i", str(outputs[0]), "-vf",
             f"fps={8/span:.8f}:round=up,scale=480:-1,tile=4x2", "-frames:v", "1", str(outputs[1])])
        if not outputs[1].is_file():
            raise ValueError("frame strip was not produced")
        metadata = {"source": str(source), "start": args.start, "seconds": span, "probe": meta,
                    "note": "Review playback and strip. This extraction does not approve the motion or decode the complete source."}
        outputs[2].write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print("Created:", *outputs, sep="\n")
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print("ERROR:", getattr(exc, "stderr", None) or str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
