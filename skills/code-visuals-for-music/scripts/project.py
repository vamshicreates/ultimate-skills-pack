#!/usr/bin/env python3
"""Validate a music-visual manifest and export an external browser data script."""
import argparse
import json
import math
import re
from pathlib import Path


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(p, base, require_media=False):
    errors, warnings = [], []
    if not isinstance(p, dict):
        return ["project must be an object"], warnings
    if type(p.get("version")) is not int or p["version"] != 1:
        errors.append("version must be 1")
    for key in ("title", "audio"):
        if not isinstance(p.get(key), str) or not p[key].strip():
            errors.append(f"{key} must be a nonempty string")
    duration = p.get("duration")
    if not number(duration) or duration <= 0:
        return errors + ["duration must be a finite positive number"], warnings
    for key in ("width", "height"):
        if type(p.get(key)) is not int or p[key] <= 0 or p[key] % 2:
            errors.append(f"{key} must be a positive even integer")
    if not number(p.get("fps")) or p["fps"] <= 0:
        errors.append("fps must be a finite positive number")
    mode = p.get("lyric_mode")
    if mode not in ("none", "selected", "full"):
        errors.append("lyric_mode must be none, selected, or full")
    if mode == "full":
        warnings.append("Full lyric coverage needs review against the complete vocal; ranges cannot prove it.")
    for key in ("bpm", "drop"):
        value = p.get(key)
        if value is not None and (not number(value) or (value <= 0 if key == "bpm" else not 0 <= value < duration)):
            errors.append(f"invalid {key}")
    for key in ("beats", "downbeats", "phrases", "accents"):
        times = p.get(key, [])
        if not isinstance(times, list):
            errors.append(f"{key} must be an array")
            continue
        previous = -1
        for t in times:
            if not number(t) or not 0 <= t < duration or t <= previous:
                errors.append(f"{key} must contain increasing finite times within the song")
                break
            previous = t
    required_text = {
        "sections": ("id", "label"), "shots": ("id", "event", "action", "transition"),
        "lyrics": ("text",), "dialogue": ("text", "speaker"), "proofs": ("file", "status")}
    for key, text_keys in required_text.items():
        rows = p.get(key, [] if key in ("dialogue", "proofs") else None)
        if not isinstance(rows, list):
            errors.append(f"{key} must be an array")
            continue
        if not rows and (key in ("shots", "sections") or key == "lyrics" and mode in ("selected", "full")):
            errors.append(f"{key} cannot be empty for this project")
        if key == "lyrics" and rows and mode == "none":
            errors.append("lyric_mode none conflicts with nonempty lyrics")
        previous, covered, ids = -1, 0, set()
        for i, row in enumerate(rows):
            tag = f"{key}[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{tag} must be an object")
                continue
            for field in text_keys:
                if not isinstance(row.get(field), str) or not row[field].strip():
                    errors.append(f"{tag}.{field} must be nonempty text")
            start, end = row.get("start"), row.get("end")
            if not number(start) or not number(end) or not 0 <= start < end <= duration:
                errors.append(f"{tag} needs 0 <= start < end <= duration")
                continue
            if key != "proofs" and start < previous:
                errors.append(f"{key} must be ordered by start time")
            previous = start
            if key in ("shots", "sections"):
                ident = row.get("id")
                if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", ident):
                    errors.append(f"{tag}.id must be a valid HTML identifier")
                elif ident in ids:
                    errors.append(f"duplicate {key} id: {ident}")
                else:
                    ids.add(ident)
                if start > covered + 1e-6:
                    (errors if key == "shots" else warnings).append(f"{key} gap: {covered:g}–{start:g}s")
                if key == "sections" and start < covered - 1e-6:
                    errors.append(f"{tag} overlaps the previous section")
                covered = max(covered, end)
            if key in ("lyrics", "dialogue"):
                if type(row.get("verified")) is not bool:
                    errors.append(f"{tag}.verified must be boolean")
                elif not row["verified"]:
                    warnings.append(f"{tag} wording/timing is unverified")
            if key == "proofs":
                if row.get("status") not in ("pending", "pass", "revise"):
                    errors.append(f"{tag}.status must be pending, pass, or revise")
                elif row["status"] != "pass":
                    warnings.append(f"{tag} motion review: {row['status']}")
                if require_media and isinstance(row.get("file"), str) and not (base / row["file"]).is_file():
                    errors.append(f"{tag} proof file missing")
        if key in ("shots", "sections") and covered < duration - 1e-6:
            (errors if key == "shots" else warnings).append(f"{key} ends at {covered:g}s before song end")
    if not p.get("proofs"):
        warnings.append("No motion proof recorded; this manifest is not evidence of visual quality.")
    energy = p.get("energy", [])
    if not isinstance(energy, list):
        errors.append("energy must be an array")
    else:
        previous = -1
        for sample in energy:
            if not isinstance(sample, dict):
                errors.append("energy samples must be objects")
                break
            t, value = sample.get("t"), sample.get("value")
            if not number(t) or not previous < t < duration or t < 0 or not number(value) or not 0 <= value <= 1:
                errors.append("energy requires increasing in-range times and values in [0,1]")
                break
            previous = t
    if require_media and isinstance(p.get("audio"), str) and not (base / p["audio"]).is_file():
        errors.append("source audio file missing relative to manifest")
    return errors, warnings


def export(p):
    music = {key: p.get(key, []) for key in ("beats", "downbeats", "phrases", "accents")}
    music.update(duration=p["duration"], bpm=p.get("bpm"), drop=p.get("drop"),
                 sections=[dict(row, t0=row["start"], t1=row["end"]) for row in p["sections"]])
    def encode(value):
        return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    return "// Generated timing data; load as a local external script.\nwindow.CVM = " + encode(p) + ";\nwindow.MUSIC = " + encode(music) + ";\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "export"))
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--require-media", action="store_true")
    args = parser.parse_args()
    if args.command == "export" and not args.out:
        parser.error("export needs --out")
    if args.out and args.out.resolve() == args.manifest.resolve():
        parser.error("output must not overwrite the manifest")
    try:
        p = json.loads(args.manifest.read_text(encoding="utf-8"))
        errors, warnings = validate(p, args.manifest.resolve().parent, args.require_media)
        for warning in warnings:
            print("WARNING:", warning)
        for error in errors:
            print("ERROR:", error)
        if errors:
            return 1
        if args.command == "export":
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(export(p), encoding="utf-8")
            print("Exported:", args.out)
        print("Timing structure valid. Artistic quality and lyric accuracy require separate review.")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print("ERROR:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
