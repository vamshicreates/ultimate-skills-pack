#!/usr/bin/env python3
"""Mix a film audio package, master it, and mux it with the locked picture.

Usage: python finish_film.py --plan mix_plan.json [--validate-only] [--overwrite]
Requires FFmpeg and ffprobe on PATH; Python dependencies are standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SAFE_TITLE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,79}$")
MP4_VIDEO = {"h264", "hevc", "av1", "mpeg4"}


def command(args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Command failed: {' '.join(args[:3])}\n{result.stderr[-5000:]}")
    return result


def probe(path: Path) -> dict:
    return json.loads(command(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout)


def number(value: object, name: str, low: float, high: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not math.isfinite(result) or not low <= result <= high:
        raise ValueError(f"{name} must be between {low} and {high}")
    return result


def stream(info: dict, kind: str) -> dict | None:
    return next((item for item in info.get("streams", []) if item.get("codec_type") == kind), None)


def resolve_path(base: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("A required path is missing")
    return (base / value).resolve()


def read_plan(plan_file: Path) -> dict:
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    base = plan_file.resolve().parent
    title = str(plan.get("title", ""))
    if not SAFE_TITLE.fullmatch(title):
        raise ValueError("title needs 2-80 letters, digits, underscores, or hyphens")
    video = resolve_path(base, plan.get("video"))
    package = resolve_path(base, plan.get("audio_package"))
    out = resolve_path(base, plan.get("output_dir"))
    if not video.is_file() or not package.is_dir():
        raise ValueError("The locked video and audio package must exist")
    if out == package or out.is_relative_to(package):
        raise ValueError("output_dir must be separate from the source audio package")
    video_info = probe(video)
    video_stream = stream(video_info, "video")
    if video_stream is None:
        raise ValueError("The source has no video stream")
    duration = number(video_stream.get("duration") or video_info.get("format", {}).get("duration"), "video duration", 0.01, 86400)
    container = plan.get("container", "mp4")
    if container not in ("mp4", "mov"):
        raise ValueError("container must be mp4 or mov")
    if container == "mp4" and video_stream.get("codec_name") not in MP4_VIDEO:
        raise ValueError("This video codec cannot be copied into MP4; choose container mov or make a separate picture transcode")
    source_audio = plan.get("source_audio", {})
    mode = source_audio.get("mode", "keep")
    if mode not in ("keep", "replace"):
        raise ValueError("source_audio.mode must be keep or replace")
    audio_streams = [item for item in video_info.get("streams", []) if item.get("codec_type") == "audio"]
    source_index = int(source_audio.get("stream_index", 0))
    if mode == "keep" and not 0 <= source_index < len(audio_streams):
        raise ValueError("source_audio.stream_index does not select an existing audio stream; choose replace if the video has none")
    video_start = float(video_stream.get("start_time", 0))
    source_gain = number(source_audio.get("gain_db", 0), "source audio gain_db", -60, 12)
    mastering = plan.get("mastering", {})
    target_i = number(mastering.get("integrated_lufs", -16), "integrated_lufs", -40, -8)
    target_tp = number(mastering.get("true_peak_dbfs", -1.5), "true_peak_dbfs", -6, -0.1)
    target_lra = number(mastering.get("lra", 11), "lra", 1, 20)

    cues = []
    ids = set()
    if not isinstance(plan.get("cues"), list):
        raise ValueError("cues must be a list")
    for index, cue in enumerate(plan["cues"], 1):
        if not isinstance(cue, dict):
            raise ValueError(f"Cue {index} must be an object")
        cue_id = str(cue.get("id", ""))
        if not SAFE_TITLE.fullmatch(cue_id) or cue_id in ids:
            raise ValueError(f"Cue {index} needs a unique safe id")
        ids.add(cue_id)
        relative = Path(str(cue.get("asset", "")))
        asset = (package / relative).resolve()
        if not str(cue.get("asset", "")) or relative.is_absolute() or not asset.is_relative_to(package) or not asset.is_file():
            raise ValueError(f"{cue_id} asset missing or outside audio package")
        asset_info = probe(asset)
        if stream(asset_info, "audio") is None:
            raise ValueError(f"{cue_id} asset has no audio stream")
        asset_duration = number(asset_info.get("format", {}).get("duration"), f"{cue_id} asset duration", 0.001, 86400)
        start = number(cue.get("start_seconds"), f"{cue_id} start_seconds", 0, duration)
        source_in = number(cue.get("in_seconds", 0), f"{cue_id} in_seconds", 0, asset_duration)
        length = number(cue.get("duration_seconds", asset_duration - source_in), f"{cue_id} duration_seconds", 0.001, asset_duration)
        if source_in + length > asset_duration + 0.005 or start + length > duration + 0.05:
            raise ValueError(f"{cue_id} extends beyond its file or the picture")
        gain = number(cue.get("gain_db", 0), f"{cue_id} gain_db", -60, 12)
        fade_in = number(cue.get("fade_in_seconds", 0.01), f"{cue_id} fade_in_seconds", 0, length / 2)
        fade_out = number(cue.get("fade_out_seconds", 0.01), f"{cue_id} fade_out_seconds", 0, length / 2)
        cues.append({"id": cue_id, "asset": asset, "start": start, "in": source_in,
                     "duration": length, "gain": gain, "fade_in": fade_in, "fade_out": fade_out})
    if not cues and mode == "replace":
        raise ValueError("The plan has no audio: add a cue or keep production audio")
    return {"title": title, "video": video, "package": package, "out": out,
            "container": container, "video_info": video_info, "duration": duration,
            "mode": mode, "source_gain": source_gain, "source_index": source_index,
            "video_start": video_start, "cues": cues,
            "target_i": target_i, "target_tp": target_tp, "target_lra": target_lra}


def seconds(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def mix_audio(plan: dict, destination: Path) -> None:
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(plan["video"])]
    for cue in plan["cues"]:
        args += ["-i", str(cue["asset"])]
    filters = []
    labels = []
    if plan["mode"] == "keep":
        filters.append(f"[0:a:{plan['source_index']}]asetpts=PTS-{seconds(plan['video_start'])}/TB,aresample=48000:async=1:first_pts=0,aformat=channel_layouts=stereo,volume={seconds(plan['source_gain'])}dB,apad,atrim=duration={seconds(plan['duration'])}[source]")
        labels.append("[source]")
    for index, cue in enumerate(plan["cues"], 1):
        parts = [f"[{index}:a:0]atrim=start={seconds(cue['in'])}:duration={seconds(cue['duration'])}",
                 "asetpts=PTS-STARTPTS", "aresample=48000", "aformat=channel_layouts=stereo",
                 f"volume={seconds(cue['gain'])}dB"]
        if cue["fade_in"]:
            parts.append(f"afade=t=in:st=0:d={seconds(cue['fade_in'])}")
        if cue["fade_out"]:
            parts.append(f"afade=t=out:st={seconds(cue['duration']-cue['fade_out'])}:d={seconds(cue['fade_out'])}")
        parts += [f"adelay={round(cue['start'] * 48000)}S:all=1", "apad",
                  f"atrim=duration={seconds(plan['duration'])}[cue{index}]"]
        filters.append(",".join(parts))
        labels.append(f"[cue{index}]")
    if len(labels) == 1:
        filters.append(f"{labels[0]}anull[aout]")
    else:
        filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0,atrim=duration={seconds(plan['duration'])}[aout]")
    args += ["-filter_complex", ";".join(filters), "-map", "[aout]", "-vn", "-c:a", "pcm_f32le", "-ar", "48000", "-ac", "2", str(destination)]
    command(args)


def loudnorm_measure(path: Path, plan: dict) -> dict:
    filt = f"loudnorm=I={seconds(plan['target_i'])}:TP={seconds(plan['target_tp'])}:LRA={seconds(plan['target_lra'])}:print_format=json"
    result = command(["ffmpeg", "-hide_banner", "-i", str(path), "-af", filt, "-f", "null", "-"])
    matches = re.findall(r'\{\s*"input_i"[\s\S]*?\}', result.stderr)
    if not matches:
        raise RuntimeError("Could not read FFmpeg loudness measurements")
    measured = json.loads(matches[-1])
    for key in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset"):
        if not math.isfinite(float(measured[key])):
            raise RuntimeError("Premix is silent or has invalid loudness measurements")
    return measured


def master_audio(premix: Path, destination: Path, plan: dict, measured: dict) -> dict:
    filt = (
        f"loudnorm=I={seconds(plan['target_i'])}:TP={seconds(plan['target_tp'])}:LRA={seconds(plan['target_lra'])}"
        f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
        f":measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}"
        f":offset={measured['target_offset']}:linear=true:print_format=json"
    )
    result = command(["ffmpeg", "-hide_banner", "-y", "-i", str(premix), "-af", filt,
                      "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(destination)])
    matches = re.findall(r'\{\s*"input_i"[\s\S]*?\}', result.stderr)
    return json.loads(matches[-1]) if matches else {}


def mux_video(plan: dict, master: Path, destination: Path) -> None:
    command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(plan["video"]),
             "-i", str(master), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(destination)])


def verify_output(plan: dict, master: Path, final: Path) -> dict:
    master_info = probe(master)
    final_info = probe(final)
    master_stream = stream(master_info, "audio")
    final_audio = stream(final_info, "audio")
    final_video = stream(final_info, "video")
    if not master_stream or not final_audio or not final_video:
        raise RuntimeError("Final output is missing video or audio")
    if master_stream.get("sample_rate") != "48000" or master_stream.get("codec_name") != "pcm_s24le":
        raise RuntimeError("Master WAV is not 48 kHz, 24-bit PCM")
    if final_audio.get("codec_name") != "aac" or final_audio.get("sample_rate") != "48000":
        raise RuntimeError("Final video has an unexpected audio format")
    original = stream(plan["video_info"], "video")
    for field in ("codec_name", "width", "height", "r_frame_rate"):
        if final_video.get(field) != original.get(field):
            raise RuntimeError(f"Picture metadata changed: {field}")
    for field in ("nb_frames",):
        if original.get(field) and final_video.get(field) and original[field] != final_video[field]:
            raise RuntimeError("Picture frame count changed")
    output_duration = float(final_info["format"]["duration"])
    if abs(output_duration - plan["duration"]) > 0.1:
        raise RuntimeError("Final output duration differs from the locked picture")
    video_start = float(final_video.get("start_time", 0))
    audio_start = float(final_audio.get("start_time", 0))
    if abs(video_start - audio_start) > 0.05:
        raise RuntimeError("Final video and audio stream starts differ; inspect sync")
    return {"source_video_duration": plan["duration"], "final_duration": output_duration,
            "video_codec": final_video.get("codec_name"), "video_frames": final_video.get("nb_frames"),
            "audio_codec": final_audio.get("codec_name"), "master_codec": master_stream.get("codec_name"),
            "video_start": video_start, "audio_start": audio_start}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        raise RuntimeError("Python 3.11 or newer is required")
    for program in ("ffmpeg", "ffprobe"):
        if shutil.which(program) is None:
            raise RuntimeError(f"{program} is missing from PATH")
    plan = read_plan(args.plan)
    if args.validate_only:
        print(f"VALID: {len(plan['cues'])} cues fit the {plan['duration']:.3f}s locked picture")
        return
    out = plan["out"]
    out.mkdir(parents=True, exist_ok=True)
    master = out / f"{plan['title']}_Master_48k24.wav"
    final = out / f"{plan['title']}_Final_With_Audio.{plan['container']}"
    report = out / f"{plan['title']}_Render_Report.json"
    plan_copy = out / f"{plan['title']}_Mix_Plan.json"
    if not args.overwrite and any(path.exists() for path in (master, final, report, plan_copy)):
        raise FileExistsError("Output exists; choose a new output folder or pass --overwrite")
    with tempfile.TemporaryDirectory(prefix="film-finish-", dir=out) as temporary:
        premix = Path(temporary) / "premix.float.wav"
        mix_audio(plan, premix)
        measured = loudnorm_measure(premix, plan)
        mastering_result = master_audio(premix, master, plan, measured)
    mux_video(plan, master, final)
    checks = verify_output(plan, master, final)
    if args.plan.resolve() != plan_copy.resolve():
        shutil.copyfile(args.plan, plan_copy)
    report.write_text(json.dumps({
        "title": plan["title"], "picture": str(plan["video"]), "audio_package": str(plan["package"]),
        "source_audio_mode": plan["mode"], "source_audio_stream_index": plan["source_index"],
        "cue_ids": [cue["id"] for cue in plan["cues"]],
        "master_wav": str(master), "final_video": str(final), "mix_plan": str(plan_copy), "loudness": mastering_result,
        "checks": checks,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"DONE: {final}\nMASTER: {master}\nREPORT: {report}")


if __name__ == "__main__":
    main()
