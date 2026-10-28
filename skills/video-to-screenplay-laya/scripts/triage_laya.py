#!/usr/bin/env python3
"""Suggest text-only labels for caption windows; never drop source material."""

import argparse
import json
import re
import sys
from pathlib import Path


TIMESTAMP = re.compile(r"(\d+):(\d+):(\d+)[,.](\d{1,3})")
LABELS = {"A": "dialogue", "B": "lyrics", "C": "other_or_unclear"}


def seconds(value):
    match = TIMESTAMP.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Invalid SRT time: {value!r}")
    hours, minutes, secs, millis = (int(part) for part in match.groups())
    return hours * 3600 + minutes * 60 + secs + millis / 10 ** len(match.group(4))


def parse_srt(source):
    blocks = re.split(r"\n\s*\n", source.replace("\r\n", "\n").strip())
    cues = []
    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        time_index = next((i for i, line in enumerate(lines) if " --> " in line), None)
        if time_index is None:
            continue
        start_text, end_text = lines[time_index].split(" --> ", 1)
        start = seconds(start_text)
        end = seconds(end_text.split()[0])
        if end <= start:
            raise ValueError(f"SRT cue has non-positive duration: {lines[time_index]}")
        utterance = " ".join(line.strip() for line in lines[time_index + 1 :] if line.strip())
        if utterance:
            cues.append({"start": start, "end": end, "text": utterance})
    return sorted(cues, key=lambda cue: (cue["start"], cue["end"]))


def make_windows(cues, window_seconds, max_chars):
    windows = []
    current = []
    for cue in cues:
        current_text_length = sum(len(item["text"]) + 1 for item in current)
        if current and (cue["start"] - current[0]["start"] >= window_seconds or current_text_length + len(cue["text"]) > max_chars):
            windows.append(current)
            current = []
        current.append(cue)
    if current:
        windows.append(current)
    return [
        {
            "index": index,
            "start": group[0]["start"],
            "end": max(cue["end"] for cue in group),
            "text": " ".join(cue["text"] for cue in group),
            "cue_count": len(group),
            "candidate": "unclassified",
            "review_required": True,
        }
        for index, group in enumerate(windows, 1)
    ]


def label_windows(windows, model):
    try:
        from laya import Router
    except ImportError as exc:
        raise RuntimeError("Laya is missing. Install it in an isolated Python environment with `python -m pip install laya`.") from exc

    router = Router()
    question = {
        "segment_kind": {
            "type": "choice",
            "instructions": "Classify this film subtitle excerpt by what the words most likely represent. If the text alone cannot tell, choose C.",
            "criteria": {
                "A": "ordinary spoken dialogue or speech between characters",
                "B": "lyrics sung as part of a song",
                "C": "uncertain, non-speech text, or other content",
            },
        }
    }
    for window in windows:
        answer = router.predict(window["text"], question, model=model)["answers"]["segment_kind"]
        choice = answer.get("choice")
        window["candidate"] = LABELS.get(choice, "other_or_unclear")
        window["laya_choice"] = choice
        if answer.get("answer_confidence") is not None:
            window["laya_confidence_unvalidated"] = answer["answer_confidence"]
    return windows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captions", type=Path, help="Source-time SRT captions")
    parser.add_argument("--output", required=True, type=Path, help="Output JSON path")
    parser.add_argument("--window-seconds", type=float, default=25.0)
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--model", choices=("english", "multilingual"), default="multilingual")
    parser.add_argument("--dry-run", action="store_true", help="Parse and group captions without importing Laya")
    args = parser.parse_args(argv)
    if args.window_seconds <= 0 or args.max_chars <= 0:
        parser.error("--window-seconds and --max-chars must be positive")

    cues = parse_srt(args.captions.read_text(encoding="utf-8-sig"))
    if not cues:
        parser.error("No timestamped, nonempty SRT cues found")
    windows = make_windows(cues, args.window_seconds, args.max_chars)
    if not args.dry_run:
        label_windows(windows, args.model)
    output = {
        "source_srt": str(args.captions.resolve()),
        "model": None if args.dry_run else args.model,
        "text_only": True,
        "review_required_for_all": True,
        "captioned_windows_only": True,
        "windows": windows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(windows)} caption windows to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
