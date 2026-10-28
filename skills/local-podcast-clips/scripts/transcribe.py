#!/usr/bin/env python3
"""Transcribe a local podcast file to timestamped JSON and SRT."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, remainder = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{remainder:03}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--language", default="te", help="Whisper language code; te is Telugu")
    parser.add_argument("--model", default="medium", help="Multilingual Whisper model, e.g. medium or large-v3")
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--compute-type", default="int8", help="CTranslate2 compute type; int8 works on CPU")
    parser.add_argument("--output", required=True, type=Path, help="Output stem without extension")
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"source not found: {args.source}")
    if args.language != "en" and args.model.endswith(".en"):
        parser.error("An .en model cannot transcribe Telugu; use a multilingual model")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        parser.error("faster-whisper is missing; see references/setup.md")

    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    iterator, info = model.transcribe(
        str(args.source), language=args.language, task="transcribe", word_timestamps=True,
        vad_filter=True,
    )
    segments = []
    for segment in iterator:
        segments.append({
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": segment.text.strip(),
            "words": [
                {"start": round(word.start, 3), "end": round(word.end, 3), "text": word.word}
                for word in (segment.words or []) if word.start is not None and word.end is not None
            ],
        })
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix(".json").write_text(json.dumps({
        "source": str(args.source.resolve()), "language": info.language,
        "model": args.model, "segments": segments,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cues = [f"{i}\n{srt_time(item['start'])} --> {srt_time(item['end'])}\n{item['text']}\n"
            for i, item in enumerate(segments, 1)]
    output.with_suffix(".srt").write_text("\n".join(cues), encoding="utf-8")
    print(f"Wrote {len(segments)} segments: {output.with_suffix('.json')}")
    print(f"Captions: {output.with_suffix('.srt')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
