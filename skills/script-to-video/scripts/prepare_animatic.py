#!/usr/bin/env python3
"""Turn approved storyboard stills and dialogue WAV/MP3 files into video-use sources.

Usage: python prepare_animatic.py project/animatic.json
Outputs live in project/edit/. No external voice or image generation occurs here.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def stamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def render_shot(image: Path, lines: list[dict], out: Path, seconds: float, fps: int, width: int, height: int, include_audio: bool) -> None:
    command = ["ffmpeg", "-y", "-loop", "1", "-framerate", str(fps), "-i", str(image)]
    if include_audio:
        if lines:
            for line in lines:
                command += ["-i", str(line["_audio_path"])]
        else:
            command += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    scale = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    command += ["-vf", scale, "-frames:v", str(round(seconds * fps)), "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p"]
    if include_audio:
        if lines:
            pieces = []
            for index, line in enumerate(lines, 1):
                offset_ms = round(float(line["offset_s"]) * 1000)
                pieces.append(f"[{index}:a]aresample=48000,adelay={offset_ms}:all=1[a{index}]")
            labels = "".join(f"[a{index}]" for index in range(1, len(lines) + 1))
            pieces.append(f"{labels}amix=inputs={len(lines)}:duration=longest:normalize=0,apad,atrim=duration={seconds:.6f}[aout]")
            command += ["-filter_complex", ";".join(pieces), "-map", "0:v", "-map", "[aout]"]
        else:
            command += ["-map", "0:v", "-map", "1:a", "-af", f"atrim=duration={seconds:.6f}"]
        command += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    else:
        command += ["-an"]
    command += ["-t", f"{seconds:.6f}", "-movflags", "+faststart", str(out)]
    run(command)


def otio_clip(name: str, path: Path, frames: int, fps: int, metadata: dict | None = None) -> dict:
    return {
        "OTIO_SCHEMA": "Clip.2", "name": name, "metadata": metadata or {},
        "source_range": {
            "OTIO_SCHEMA": "TimeRange.1",
            "start_time": {"OTIO_SCHEMA": "RationalTime.1", "value": 0, "rate": fps},
            "duration": {"OTIO_SCHEMA": "RationalTime.1", "value": frames, "rate": fps},
        },
        "media_reference": {"OTIO_SCHEMA": "ExternalReference.1", "target_url": path.as_uri()},
    }


def gap(frames: int, fps: int) -> dict:
    return {
        "OTIO_SCHEMA": "Gap.1",
        "source_range": {
            "OTIO_SCHEMA": "TimeRange.1",
            "start_time": {"OTIO_SCHEMA": "RationalTime.1", "value": 0, "rate": fps},
            "duration": {"OTIO_SCHEMA": "RationalTime.1", "value": frames, "rate": fps},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    root = manifest_path.parent
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    fps = int(data.get("fps", 25))
    width, height = int(data.get("width", 1920)), int(data.get("height", 1080))
    if fps <= 0 or width <= 0 or height <= 0 or width % 2 or height % 2:
        raise ValueError("fps must be positive and canvas dimensions must be positive even numbers")
    shots = data.get("shots") or []
    if not shots:
        raise ValueError("manifest needs at least one shot")
    if data.get("one_image_per_dialogue"):
        dialogue_images = []
        manifest_lines = {}
        for shot in shots:
            lines = shot.get("dialogue", [])
            if len(lines) > 1:
                raise ValueError(f'{shot["id"]}: one_image_per_dialogue requires a dedicated shot for each spoken turn')
            if lines:
                image = resolve(root, shot["image"])
                dialogue_images.append(image)
                line = lines[0]
                line_id = str(line["id"])
                if line_id in manifest_lines:
                    raise ValueError(f"duplicate dialogue ID: {line_id}")
                manifest_lines[line_id] = line
        if len(set(dialogue_images)) != len(dialogue_images):
            raise ValueError("one_image_per_dialogue requires a distinct image file for each spoken turn")
        if data.get("dialogue_ledger"):
            ledger_path = resolve(root, data["dialogue_ledger"])
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            expected = {str(line["id"]): line for line in ledger}
            if len(expected) != len(ledger):
                raise ValueError("dialogue ledger contains duplicate IDs")
            missing = sorted(set(expected) - set(manifest_lines))
            extra = sorted(set(manifest_lines) - set(expected))
            if missing or extra:
                raise ValueError(f"dialogue coverage mismatch; missing={missing}, extra={extra}")
            for line_id, line in manifest_lines.items():
                source = expected[line_id]
                if line.get("character") != source.get("character") or line.get("text") != source.get("text"):
                    raise ValueError(f"{line_id}: character or dialogue text differs from the ledger")
    edit = root / "edit"
    picture_dir, source_dir = edit / "picture", edit / "render_sources"
    picture_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    ids, line_ids = set(), set()
    sources, ranges, subtitles, voice_events, picture_clips = {}, [], [], [], []
    current_frames = 0
    for shot in shots:
        shot_id = str(shot["id"])
        if not re.fullmatch(r"[A-Za-z0-9_-]+", shot_id) or shot_id in ids:
            raise ValueError(f"invalid or duplicate shot ID: {shot_id}")
        ids.add(shot_id)
        image = resolve(root, shot["image"])
        if not image.is_file():
            raise FileNotFoundError(image)
        seconds = float(shot["duration_s"])
        frames = round(seconds * fps)
        if frames < 1:
            raise ValueError(f"{shot_id}: duration is shorter than one frame")
        seconds = frames / fps
        lines = shot.get("dialogue", [])
        if data.get("one_image_per_dialogue") and len(lines) > 1:
            raise ValueError(f"{shot_id}: one_image_per_dialogue requires a dedicated shot for each spoken turn")
        for line in lines:
            line_id = str(line["id"])
            if line_id in line_ids:
                raise ValueError(f"duplicate dialogue ID: {line_id}")
            line_ids.add(line_id)
            if not line.get("character") or not line.get("text"):
                raise ValueError(f"{line_id}: character and text are required")
            audio_path = resolve(root, line["audio"])
            if not audio_path.is_file():
                raise FileNotFoundError(audio_path)
            line["_audio_path"] = audio_path
            line["_duration"] = duration(audio_path)
            offset = float(line.get("offset_s", 0))
            if offset < 0 or offset + line["_duration"] > seconds + 0.005:
                raise ValueError(f"{line_id}: dialogue falls outside shot {shot_id}; extend the shot or move the line")
            line["offset_s"] = offset
            start_frame = current_frames + round(offset * fps)
            voice_events.append((start_frame, line_id, audio_path, line["_duration"], str(line["character"])))
            start = current_frames / fps + offset
            subtitles.append((start, start + line["_duration"], str(line["text"])))
        picture = picture_dir / f"{shot_id}.mp4"
        source = source_dir / f"{shot_id}.mp4"
        render_shot(image, lines, picture, seconds, fps, width, height, False)
        render_shot(image, lines, source, seconds, fps, width, height, True)
        sources[shot_id] = str(source)
        ranges.append({"source": shot_id, "start": 0, "end": seconds, "beat": shot_id, "reason": shot.get("camera", "")})
        picture_clips.append(otio_clip(shot_id, picture, frames, fps, {"camera": shot.get("camera", "")}))
        current_frames += frames
    edl = {
        "version": 1, "title": data.get("title", root.name), "sources": sources,
        "ranges": ranges, "grade": "", "overlays": [],
        "subtitles": str(edit / "master.srt") if data.get("captions", False) else None,
        "total_duration_s": current_frames / fps,
    }
    (edit / "edl.json").write_text(json.dumps(edl, indent=2), encoding="utf-8")
    subtitles.sort(key=lambda item: item[0])
    srt = "\n".join(
        f"{index}\n{stamp(start)} --> {stamp(end)}\n{text}\n"
        for index, (start, end, text) in enumerate(subtitles, 1)
    )
    (edit / "master.srt").write_text(srt, encoding="utf-8")
    # One voice lane per character preserves overlaps and gives editors individual clips.
    voice_tracks = []
    for character in dict.fromkeys(event[4] for event in voice_events):
        cursor = 0
        children = []
        for start_frame, line_id, audio_path, length, who in sorted(voice_events):
            if who != character:
                continue
            end_frame = start_frame + math.ceil(length * fps)
            if start_frame < cursor:
                raise ValueError(f"{line_id}: same-character dialogue overlaps on the editable audio lane")
            if start_frame > cursor:
                children.append(gap(start_frame - cursor, fps))
            children.append(otio_clip(line_id, audio_path, math.ceil(length * fps), fps, {"character": character}))
            cursor = end_frame
        voice_tracks.append({"OTIO_SCHEMA": "Track.1", "name": f"Dialogue - {character}", "kind": "Audio", "children": children})
    timeline = {
        "OTIO_SCHEMA": "Timeline.1", "name": data.get("title", root.name),
        "global_start_time": {"OTIO_SCHEMA": "RationalTime.1", "value": 0, "rate": fps},
        "tracks": {"OTIO_SCHEMA": "Stack.1", "name": "tracks", "children": [
            {"OTIO_SCHEMA": "Track.1", "name": "Storyboard picture", "kind": "Video", "children": picture_clips},
            *voice_tracks,
        ]},
    }
    (edit / "timeline.otio").write_text(json.dumps(timeline, indent=2), encoding="utf-8")
    print(f"Prepared {len(shots)} shots, {len(line_ids)} dialogue lines, {current_frames / fps:.2f}s in {edit}")


if __name__ == "__main__":
    main()
