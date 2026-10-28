#!/usr/bin/env python3
"""Prepare a labeled REAPER session from a film-audio-video-finish mix plan.

Python 3.11+ and FFmpeg/ffprobe are required. Run on the computer with REAPER.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,79}$")
CATEGORIES = {"MUS": "MUSIC", "FOL": "FOLEY", "AMB": "AMBIENCE", "SFX": "SFX"}
VALID_CATEGORIES = {"MUSIC", "FOLEY", "AMBIENCE", "SFX", "OTHER"}


def run(args: list[str]) -> str:
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr[-3000:]}")
    return result.stdout


def probe(path: Path) -> dict:
    return json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))


def number(value: object, label: str, low: float, high: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number") from exc
    if not math.isfinite(result) or not low <= result <= high:
        raise ValueError(f"{label} must be between {low} and {high}")
    return result


def required_path(base: Path, value: object, label: str, kind: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} is missing")
    path = (base / value).resolve()
    if kind == "file" and not path.is_file():
        raise ValueError(f"{label} is not a file: {path}")
    if kind == "dir" and not path.is_dir():
        raise ValueError(f"{label} is not a folder: {path}")
    return path


def validate(plan_file: Path) -> dict:
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    base = plan_file.resolve().parent
    title = plan.get("title")
    if not isinstance(title, str) or not SAFE_ID.fullmatch(title):
        raise ValueError("title must be 2-80 safe filename characters")
    video = required_path(base, plan.get("video"), "video", "file")
    package = required_path(base, plan.get("audio_package"), "audio_package", "dir")
    output = required_path(base, plan.get("output_dir"), "output_dir", "new")
    session = output / f"{title}_REAPER_Session"
    if session.exists():
        raise FileExistsError(f"Session already exists: {session}")
    if session == package or session.is_relative_to(package) or package.is_relative_to(session):
        raise ValueError("The session must be separate from the source audio package")
    if session == video or video.is_relative_to(session):
        raise ValueError("The session cannot contain the source picture")

    video_info = probe(video)
    video_stream = next((s for s in video_info.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video_stream:
        raise ValueError("The picture has no video stream")
    duration = number(video_stream.get("duration") or video_info.get("format", {}).get("duration"),
                      "picture duration", 0.01, 86400)
    video_start = number(video_stream.get("start_time", 0), "video start time", -86400, 86400)
    audio_streams = [s for s in video_info.get("streams", []) if s.get("codec_type") == "audio"]
    source = plan.get("source_audio", {})
    if not isinstance(source, dict):
        raise ValueError("source_audio must be an object")
    mode = source.get("mode", "keep")
    if mode not in ("keep", "replace"):
        raise ValueError("source_audio.mode must be keep or replace")
    try:
        stream_index = int(source.get("stream_index", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("source_audio.stream_index must be an integer") from exc
    if mode == "keep" and not 0 <= stream_index < len(audio_streams):
        raise ValueError("Selected production audio stream is missing; set mode to replace only after checking dialogue")
    source_gain = number(source.get("gain_db", 0), "source_audio.gain_db", -60, 12)

    raw_cues = plan.get("cues")
    if not isinstance(raw_cues, list):
        raise ValueError("cues must be a list")
    if not raw_cues and mode == "replace":
        raise ValueError("No audio is selected")
    cues = []
    ids = set()
    for index, cue in enumerate(raw_cues, 1):
        if not isinstance(cue, dict):
            raise ValueError(f"Cue {index} must be an object")
        cue_id = cue.get("id")
        if not isinstance(cue_id, str) or not SAFE_ID.fullmatch(cue_id) or cue_id in ids:
            raise ValueError(f"Cue {index} needs a unique safe id")
        ids.add(cue_id)
        asset_value = cue.get("asset")
        if not isinstance(asset_value, str) or not asset_value:
            raise ValueError(f"{cue_id} has no asset")
        relative = Path(asset_value)
        asset = (package / relative).resolve()
        if relative.is_absolute() or not asset.is_relative_to(package) or not asset.is_file():
            raise ValueError(f"{cue_id} asset is missing or outside the package")
        info = probe(asset)
        if not any(s.get("codec_type") == "audio" for s in info.get("streams", [])):
            raise ValueError(f"{cue_id} asset has no audio")
        asset_duration = number(info.get("format", {}).get("duration"), f"{cue_id} duration", 0.001, 86400)
        start = number(cue.get("start_seconds"), f"{cue_id} start_seconds", 0, duration)
        source_in = number(cue.get("in_seconds", 0), f"{cue_id} in_seconds", 0, asset_duration)
        length = number(cue.get("duration_seconds", asset_duration - source_in),
                        f"{cue_id} duration_seconds", 0.001, asset_duration)
        if source_in + length > asset_duration + 0.005 or start + length > duration + 0.05:
            raise ValueError(f"{cue_id} extends beyond its file or picture")
        gain = number(cue.get("gain_db", 0), f"{cue_id} gain_db", -60, 12)
        fade_in = number(cue.get("fade_in_seconds", 0.01), f"{cue_id} fade_in_seconds", 0, length / 2)
        fade_out = number(cue.get("fade_out_seconds", 0.01), f"{cue_id} fade_out_seconds", 0, length / 2)
        category = cue.get("category") or CATEGORIES.get(cue_id[:3].upper(), "OTHER")
        if not isinstance(category, str) or category.upper() not in VALID_CATEGORIES:
            raise ValueError(f"{cue_id} category must be music, foley, ambience, sfx, or other")
        name = relative.stem
        if name.lower().endswith("_mix"):
            name = name[:-4]
        if name.startswith(cue_id + "_"):
            name = name[len(cue_id) + 1:]
        cues.append({"id": cue_id, "name": name or cue_id, "category": category.upper(),
                     "asset": asset, "relative": relative, "start": start, "duration": length,
                     "source_in": source_in, "gain_db": gain, "fade_in": fade_in,
                     "fade_out": fade_out})
    return {"title": title, "video": video, "package": package, "output": output,
            "session": session, "duration": duration, "video_start": video_start,
            "mode": mode, "stream_index": stream_index, "source_gain": source_gain, "cues": cues}


def lua_quote(value: str) -> str:
    escaped = (value.replace("\\", "\\\\").replace('"', '\\"')
               .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"))
    return f'"{escaped}"'


def lua_value(value: object) -> str:
    if value is None:
        return "nil"
    if isinstance(value, str):
        return lua_quote(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise ValueError("Lua data must contain finite numbers")
        return repr(value)
    if isinstance(value, list):
        return "{" + ", ".join(lua_value(item) for item in value) + "}"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{key} = {lua_value(item)}" for key, item in value.items()) + "}"
    raise TypeError(f"Unsupported Lua value: {type(value)}")


def extract_production(plan: dict, target: Path) -> None:
    start = f"{plan['video_start']:.9f}"
    duration = f"{plan['duration']:.9f}"
    filt = (f"[0:a:{plan['stream_index']}]asetpts=PTS-{start}/TB,"
            f"aresample=48000:async=1:first_pts=0,aformat=channel_layouts=stereo,"
            f"apad,atrim=duration={duration}[out]")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(plan["video"]),
         "-filter_complex", filt, "-map", "[out]", "-vn", "-ar", "48000", "-ac", "2",
         "-c:a", "pcm_s24le", str(target)])


def prepare(plan_file: Path, copy_video: bool) -> Path:
    plan = validate(plan_file)
    session = plan["session"]
    session.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{session.name}-", dir=session.parent))
    try:
        docs = temporary / "00_Documents"
        project = temporary / "01_REAPER_Project"
        renders = temporary / "02_Renders"
        media = project / "Media"
        for folder in (docs, media, renders):
            folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plan_file, docs / "Original_Mix_Plan.json")
        resolved_plan = json.loads(plan_file.read_text(encoding="utf-8"))
        resolved_plan["video"] = str(plan["video"])
        resolved_plan["audio_package"] = str(plan["package"])
        resolved_plan["output_dir"] = str(plan["output"])
        (docs / "Mix_Plan.json").write_text(json.dumps(resolved_plan, indent=2) + "\n", encoding="utf-8")
        source_docs = plan["package"] / "00_Documents"
        if source_docs.is_dir():
            for pattern in ("*_Sound_Breakdown.pdf", "*_Cue_Sheet.json"):
                for document in source_docs.glob(pattern):
                    shutil.copy2(document, docs / document.name)
        video_path = plan["video"]
        if copy_video:
            destination = media / "Picture" / video_path.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(video_path, destination)
            video_path = session / destination.relative_to(temporary)
            resolved_plan["video"] = str(video_path)
            (docs / "Mix_Plan.json").write_text(json.dumps(resolved_plan, indent=2) + "\n", encoding="utf-8")
        production_path = None
        if plan["mode"] == "keep":
            production = media / "Production" / "Production_Audio_48k24.wav"
            production.parent.mkdir(parents=True, exist_ok=True)
            extract_production(plan, production)
            production_path = session / production.relative_to(temporary)
        generated_cues = []
        for cue in plan["cues"]:
            destination = media / "Audio" / cue["relative"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                shutil.copy2(cue["asset"], destination)
            generated_cues.append({
                "id": cue["id"], "name": cue["name"], "category": cue["category"],
                "path": (session / destination.relative_to(temporary)).as_posix(),
                "start": cue["start"], "duration": cue["duration"],
                "source_in": cue["source_in"], "gain_db": cue["gain_db"],
                "fade_in": cue["fade_in"], "fade_out": cue["fade_out"],
            })
        rpp = session / "01_REAPER_Project" / f"{plan['title']}_Mix.rpp"
        data = {"project_path": rpp.as_posix(), "video_path": video_path.as_posix(),
                "production_path": production_path.as_posix() if production_path else None,
                "production_gain_db": plan["source_gain"], "duration": plan["duration"],
                "cues": generated_cues}
        template = (Path(__file__).resolve().parent.parent / "assets" / "import_template.lua").read_text(encoding="utf-8")
        (docs / "Import_To_REAPER.lua").write_text(
            template.replace("__SESSION_DATA__", lua_value(data)), encoding="utf-8")
        manifest = {"title": plan["title"], "picture": str(plan["video"]),
                    "picture_duration_seconds": plan["duration"], "picture_copied": copy_video,
                    "project": str(rpp), "expected_master": str(session / "02_Renders" / f"{plan['title']}_Final_Mix_48k24.wav"),
                    "source_audio_mode": plan["mode"], "cue_ids": [c["id"] for c in plan["cues"]]}
        (docs / "Session_Manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if session.exists():
            raise FileExistsError(f"Session appeared during preparation: {session}")
        temporary.rename(session)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return session


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--copy-video", action="store_true", help="Copy picture into the REAPER session for portability")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    for program in ("ffmpeg", "ffprobe"):
        if shutil.which(program) is None:
            raise RuntimeError(f"{program} is missing from PATH")
    if args.validate_only:
        plan = validate(args.plan)
        print(f"VALID: {len(plan['cues'])} cues fit the {plan['duration']:.3f}s picture")
    else:
        session = prepare(args.plan, args.copy_video)
        print(f"SESSION: {session}\nIMPORT SCRIPT: {session / '00_Documents' / 'Import_To_REAPER.lua'}")


if __name__ == "__main__":
    main()
