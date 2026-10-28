#!/usr/bin/env python3
"""Export one podcast excerpt and clip-relative SRT with FFmpeg."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def seconds(value: str) -> float:
    parts = value.split(":")
    if len(parts) > 3:
        raise argparse.ArgumentTypeError("time must be seconds or HH:MM:SS")
    try:
        numbers = [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("time must be seconds or HH:MM:SS") from exc
    if any(number < 0 for number in numbers):
        raise argparse.ArgumentTypeError("time cannot be negative")
    result = 0.0
    for number in numbers:
        result = result * 60 + number
    return result


def srt_time(value: float) -> str:
    millis = round(value * 1000)
    hours, rest = divmod(millis, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, rest = divmod(rest, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{rest:03}"


def make_cues(data: dict, start: float, end: float) -> list[tuple[float, float, str]]:
    cues = []
    for segment in data.get("segments", []):
        words = [word for word in segment.get("words", [])
                 if word["end"] > start and word["start"] < end]
        if words:
            for offset in range(0, len(words), 6):
                group = words[offset:offset + 6]
                text = "".join(word["text"] for word in group).strip()
                cue_start = max(start, group[0]["start"]) - start
                cue_end = min(end, group[-1]["end"]) - start
                if text and cue_end > cue_start:
                    cues.append((cue_start, cue_end, text))
        elif not segment.get("words") and segment["end"] > start and segment["start"] < end:
            cue_start = max(start, segment["start"]) - start
            cue_end = min(end, segment["end"]) - start
            if segment["text"].strip() and cue_end > cue_start:
                cues.append((cue_start, cue_end, segment["text"].strip()))
    return cues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--transcript", type=Path, help="JSON written by transcribe.py")
    parser.add_argument("--start", required=True, type=seconds)
    parser.add_argument("--end", required=True, type=seconds)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--aspect", choices=("9:16", "16:9", "1:1", "source"), default="9:16")
    parser.add_argument("--position", type=float, default=0.5, help="Horizontal crop position, 0=left, 1=right")
    parser.add_argument("--burn-subtitles", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        parser.error(f"source not found: {source}")
    if output == source:
        parser.error("output must differ from source")
    if output.suffix.lower() != ".mp4":
        parser.error("output must end in .mp4")
    if not 0 <= args.position <= 1:
        parser.error("--position must be between 0 and 1")
    if args.end <= args.start:
        parser.error("--end must be later than --start")
    if args.burn_subtitles and not args.transcript:
        parser.error("--burn-subtitles requires --transcript")
    if output.exists() and not args.overwrite:
        parser.error(f"output exists: {output}; pass --overwrite to replace it")
    srt = output.with_suffix(".srt")
    if args.transcript and srt.exists() and not args.overwrite:
        parser.error(f"captions exist: {srt}; pass --overwrite to replace them")

    duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(source),
    ], text=True).strip())
    if args.end > duration + 0.1:
        parser.error(f"--end exceeds source duration ({duration:.2f}s)")

    cues = []
    if args.transcript:
        data = json.loads(args.transcript.read_text(encoding="utf-8"))
        cues = make_cues(data, args.start, args.end)
        if args.burn_subtitles and not cues:
            parser.error("no captions overlap this excerpt")

    sizes = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
    filters = []
    if args.aspect != "source":
        width, height = sizes[args.aspect]
        filters.append(
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height}:x=(iw-ow)*{args.position}:y=(ih-oh)/2,setsar=1"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    srt_text = "\n".join(
        f"{number}\n{srt_time(cue_start)} --> {srt_time(cue_end)}\n{text}\n"
        for number, (cue_start, cue_end, text) in enumerate(cues, 1)
    )
    with tempfile.TemporaryDirectory(prefix="podcast-clip-") as tmp:
        if args.burn_subtitles:
            Path(tmp, "captions.srt").write_text(srt_text, encoding="utf-8")
            filters.append("subtitles=captions.srt")
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error",
                   "-ss", str(args.start), "-i", str(source),
                   "-t", str(args.end - args.start),
                   "-map", "0:v:0", "-map", "0:a?", "-sn"]
        if filters:
            command += ["-vf", ",".join(filters)]
        command += ["-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-y" if args.overwrite else "-n", str(output)]
        subprocess.run(command, cwd=tmp, check=True)
    if args.transcript:
        srt.write_text(srt_text, encoding="utf-8")
        print(f"Captions: {srt} ({len(cues)} cues)")
    print(f"Video: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
