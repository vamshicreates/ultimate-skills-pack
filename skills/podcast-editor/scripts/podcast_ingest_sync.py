#!/usr/bin/env python3
"""
Cross-Platform (Windows & macOS) Multi-Camera & Audio Ingestion + Waveform Sync
for the Podcast Editor Skill (`podcast-editor`).

Scans `Camera 1`, `Camera 2`, `Camera 3` (plus any external audio files), probes media specs,
losslessly joins multi-chapter camera files if needed, and aligns all camera angles to a
single Master Audio Spine via audio envelope cross-correlation (0 LLM tokens).
"""

import argparse
import array
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".mxf", ".avi", ".webm", ".m4v", ".mts"}
AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".aif", ".aiff"}


def find_binary(name: str) -> str:
    """Locate ffmpeg / ffprobe across Windows and macOS."""
    found = shutil.which(name)
    if found:
        return found
    if platform.system() == "Darwin":
        for p in [f"/opt/homebrew/bin/{name}", f"/usr/local/bin/{name}"]:
            if os.path.exists(p):
                return p
    elif platform.system() == "Windows":
        exe = name if name.lower().endswith(".exe") else f"{name}.exe"
        local_appdata = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        prog_data = os.environ.get("ProgramData", r"C:\ProgramData")
        prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        win_candidates = [
            os.path.join(local_appdata, "Microsoft", "WinGet", "Links", exe),
            os.path.join(prog_data, "chocolatey", "bin", exe),
            os.path.join(r"C:\ffmpeg\bin", exe),
            os.path.join(prog_files, "ffmpeg", "bin", exe),
            os.path.join(str(Path.home()), "scoop", "shims", exe),
        ]
        for p in win_candidates:
            if os.path.exists(p):
                return p
    return name


def probe_media(path: Path) -> Dict[str, Any]:
    """Return video/audio stream metadata via ffprobe."""
    ffprobe = find_binary("ffprobe")
    cmd = [
        ffprobe,
        "-v", "error",
        "-show_entries", "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json",
        str(path),
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=30)
        data = json.loads(out)
    except Exception as exc:
        return {"path": str(path), "error": str(exc), "duration": 0.0, "has_video": False, "has_audio": False}

    streams = data.get("streams", [])
    fmt = data.get("format", {})
    duration = float(fmt.get("duration") or 0.0)

    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_streams = [s for s in streams if s.get("codec_type") == "audio"]

    fps = 30.0
    width = 1920
    height = 1080
    if v_stream:
        width = int(v_stream.get("width") or 1920)
        height = int(v_stream.get("height") or 1080)
        r_fps = str(v_stream.get("r_frame_rate") or "30/1")
        if "/" in r_fps:
            num, den = r_fps.split("/", 1)
            fps = round(float(num) / max(1.0, float(den)), 3)
        else:
            try:
                fps = round(float(r_fps), 3)
            except ValueError:
                fps = 30.0

    return {
        "path": str(path.resolve()),
        "name": path.name,
        "duration": round(duration, 3),
        "has_video": v_stream is not None,
        "has_audio": len(a_streams) > 0,
        "audio_stream_count": len(a_streams),
        "width": width if v_stream else None,
        "height": height if v_stream else None,
        "fps": fps if v_stream else None,
        "sample_rate": int(a_streams[0].get("sample_rate") or 48000) if a_streams else None,
        "channels": int(a_streams[0].get("channels") or 2) if a_streams else None,
    }


def extract_envelope_100hz(media_path: Path, max_sec: float = 300.0) -> Tuple[List[float], float]:
    """
    Extract a 100 Hz amplitude envelope (10ms bins) from the first `max_sec` seconds of a file,
    plus the overall peak dBFS. Works in pure Python (with optional numpy speedup).
    """
    ffmpeg = find_binary("ffmpeg")
    with tempfile.TemporaryDirectory() as tmp:
        wav_path = Path(tmp) / "env.wav"
        cmd = [
            ffmpeg, "-y",
            "-t", str(max_sec),
            "-i", str(media_path),
            "-vn", "-ac", "1", "-ar", "8000", "-c:a", "pcm_s16le",
            str(wav_path),
        ]
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        if proc.returncode != 0 or not wav_path.exists():
            return [], -100.0

        envelope: List[float] = []
        peak_sample = 0
        # 8000 Hz -> 80 samples per 10ms bin (100 Hz envelope)
        bin_size = 80
        with wave.open(str(wav_path), "rb") as w:
            raw = w.readframes(w.getnframes())
            samples = array.array("h", raw)
            n = len(samples)
            for i in range(0, n, bin_size):
                chunk = samples[i : i + bin_size]
                if not chunk:
                    break
                c_max = max(max(chunk), -min(chunk))
                if c_max > peak_sample:
                    peak_sample = c_max
                mean_abs = sum(abs(x) for x in chunk) / len(chunk)
                envelope.append(mean_abs / 32768.0)

        peak_db = 20.0 * math.log10(peak_sample / 32768.0) if peak_sample > 0 else -100.0
        return envelope, round(peak_db, 2)


def compute_sync_offset_sec(ref_env: List[float], target_env: List[float], max_lag_sec: float = 15.0) -> Tuple[float, float]:
    """
    Compute time offset (in seconds) of `target_env` relative to `ref_env` at 100 Hz resolution.
    Positive offset `d` means: `target` audio starts at `t = d` on the `ref` timeline
    (or equivalently, `source_time = master_time - offset_sec`).
    Returns (offset_sec, confidence).
    """
    if not ref_env or not target_env or len(ref_env) < 50 or len(target_env) < 50:
        return 0.0, 0.0

    # Try numpy FFT cross-correlation first for sub-10ms speed
    try:
        import numpy as np  # type: ignore

        a = np.array(ref_env, dtype=np.float64)
        b = np.array(target_env, dtype=np.float64)
        a = a - np.mean(a)
        b = b - np.mean(b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0, 0.0

        n_fft = 1 << (len(a) + len(b) - 1).bit_length()
        corr = np.fft.irfft(np.fft.rfft(a, n_fft) * np.conj(np.fft.rfft(b, n_fft)), n_fft)
        max_lag_bins = int(round(max_lag_sec * 100.0))

        # Positive lags: indices 0 .. max_lag_bins
        pos_lags = corr[: min(max_lag_bins + 1, len(corr))]
        # Negative lags: indices n_fft - max_lag_bins .. n_fft - 1
        neg_start = max(len(pos_lags), n_fft - max_lag_bins)
        neg_lags = corr[neg_start:]

        best_pos_idx = int(np.argmax(pos_lags)) if len(pos_lags) else 0
        best_pos_val = float(pos_lags[best_pos_idx]) if len(pos_lags) else -1e9

        best_neg_idx = int(np.argmax(neg_lags)) if len(neg_lags) else 0
        best_neg_val = float(neg_lags[best_neg_idx]) if len(neg_lags) else -1e9

        if best_pos_val >= best_neg_val:
            lag_bins = best_pos_idx
            peak_corr = best_pos_val
        else:
            lag_bins = (neg_start + best_neg_idx) - n_fft
            peak_corr = best_neg_val

        confidence = float(min(1.0, max(0.0, peak_corr / (norm_a * norm_b))))
        if confidence < 0.12:
            return 0.0, round(confidence, 3)
        return round(lag_bins / 100.0, 3), round(confidence, 3)
    except ImportError:
        pass

    # Pure-Python fallback (downsampled 25 Hz search)
    step = 4
    a_ds = ref_env[::step]
    b_ds = target_env[::step]
    mean_a = sum(a_ds) / len(a_ds)
    mean_b = sum(b_ds) / len(b_ds)
    a_c = [x - mean_a for x in a_ds]
    b_c = [x - mean_b for x in b_ds]
    norm_a = math.sqrt(sum(x * x for x in a_c))
    norm_b = math.sqrt(sum(x * x for x in b_c))
    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0, 0.0

    max_lag = int(round(max_lag_sec * 25.0))
    best_lag = 0
    best_val = -1e9
    n_a, n_b = len(a_c), len(b_c)
    for lag in range(-max_lag, max_lag + 1):
        s = 0.0
        for j in range(n_b):
            i = j + lag
            if 0 <= i < n_a:
                s += a_c[i] * b_c[j]
        if s > best_val:
            best_val = s
            best_lag = lag

    conf = min(1.0, max(0.0, best_val / (norm_a * norm_b)))
    if conf < 0.12:
        return 0.0, round(conf, 3)
    return round(best_lag / 25.0, 3), round(conf, 3)


def locate_camera_folders(project_dir: Path, explicit_cams: List[Optional[str]]) -> Dict[str, Path]:
    """
    Locate Camera 1, Camera 2, Camera 3 directories inside `project_dir` or from explicit paths.
    Matches 'Camera 1', 'Camera_1', 'Camera1', 'Cam 1', 'Cam_1', 'Cam1' case-insensitively.
    """
    cam_map: Dict[str, Path] = {}
    for idx, exp in enumerate(explicit_cams, start=1):
        if exp:
            p = Path(exp).resolve()
            if p.exists():
                cam_map[f"Camera {idx}"] = p

    if len(cam_map) == 3 or not project_dir.exists():
        return cam_map

    subdirs = [d for d in sorted(project_dir.iterdir()) if d.is_dir() and not d.name.startswith(".") and d.name.lower() != "edit"]
    for idx in (1, 2, 3):
        key = f"Camera {idx}"
        if key in cam_map:
            continue
        pat = re.compile(rf"^(camera|cam)[\s_\-]*0*{idx}\b", re.IGNORECASE)
        for d in subdirs:
            if pat.search(d.name):
                cam_map[key] = d.resolve()
                break

    return cam_map


def join_or_select_camera_video(cam_label: str, cam_path: Path, edit_sources_dir: Path) -> Tuple[Optional[Path], List[Path]]:
    """
    Given a camera folder (or direct video file), return `(primary_video_path, all_audio_files_in_folder)`.
    If multiple video segments exist in the folder, concatenate them losslessly into `edit/sources/`.
    """
    if cam_path.is_file():
        return cam_path.resolve(), []

    videos = sorted([f.resolve() for f in cam_path.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTS and not f.name.startswith(".")])
    audios = sorted([f.resolve() for f in cam_path.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTS and not f.name.startswith(".")])

    if not videos:
        return None, audios
    if len(videos) == 1:
        return videos[0], audios

    # Concatenate multiple camera chapter files losslessly
    edit_sources_dir.mkdir(parents=True, exist_ok=True)
    safe_name = cam_label.replace(" ", "_")
    joined_path = edit_sources_dir / f"{safe_name}_joined.mp4"
    if joined_path.exists():
        return joined_path, audios

    concat_txt = edit_sources_dir / f"{safe_name}_concat.txt"
    lines = [f"file '{v.resolve().as_posix().replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for v in videos]
    concat_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ffmpeg = find_binary("ffmpeg")
    subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(joined_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=300,
    )
    return (joined_path if joined_path.exists() else videos[0]), audios


def build_mixed_master_audio(audio_files: List[Path], out_wav: Path) -> Optional[Path]:
    """Mix multiple individual speaker mic files into a single synced master WAV for the timeline spine."""
    if not audio_files:
        return None
    if len(audio_files) == 1:
        return audio_files[0]

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = find_binary("ffmpeg")
    inputs: List[str] = []
    for a in audio_files:
        inputs.extend(["-i", str(a)])
    n = len(audio_files)
    filter_str = f"amix=inputs={n}:duration=longest:dropout_transition=0,dynaudnorm=f=150:g=15"
    cmd = [ffmpeg, "-y"] + inputs + ["-filter_complex", filter_str, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out_wav)]
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    return out_wav if (proc.returncode == 0 and out_wav.exists()) else audio_files[0]


def ingest_and_sync_podcast(
    project_dir: Path,
    cam1: Optional[str] = None,
    cam2: Optional[str] = None,
    cam3: Optional[str] = None,
    audio_paths: Optional[List[str]] = None,
    edit_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    project_dir = project_dir.resolve()
    edit_dir = (edit_dir or (project_dir / "edit")).resolve()
    edit_dir.mkdir(parents=True, exist_ok=True)
    sources_dir = edit_dir / "sources"

    cam_folders = locate_camera_folders(project_dir, [cam1, cam2, cam3])
    cameras_info: Dict[str, Dict[str, Any]] = {}
    discovered_audios: List[Path] = []

    if audio_paths:
        for ap in audio_paths:
            p = Path(ap).resolve()
            if p.is_dir():
                discovered_audios.extend(sorted([f.resolve() for f in p.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTS]))
            elif p.is_file():
                discovered_audios.append(p)

    # Also check project root and an optional `Audio/` folder for external audio files
    if project_dir.exists():
        for f in sorted(project_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in AUDIO_EXTS and not f.name.startswith("."):
                if f.resolve() not in discovered_audios:
                    discovered_audios.append(f.resolve())
            elif f.is_dir() and f.name.lower() in ("audio", "audios", "mics", "sound"):
                for af in sorted(f.iterdir()):
                    if af.is_file() and af.suffix.lower() in AUDIO_EXTS and not af.name.startswith("."):
                        if af.resolve() not in discovered_audios:
                            discovered_audios.append(af.resolve())

    cam_envelopes: Dict[str, List[float]] = {}
    for cam_key in ("Camera 1", "Camera 2", "Camera 3"):
        folder = cam_folders.get(cam_key)
        if not folder:
            continue
        vid_path, folder_audios = join_or_select_camera_video(cam_key, folder, sources_dir)
        for fa in folder_audios:
            if fa not in discovered_audios:
                discovered_audios.append(fa)
        if vid_path and vid_path.exists():
            meta = probe_media(vid_path)
            env, peak_db = extract_envelope_100hz(vid_path)
            cam_envelopes[cam_key] = env
            meta["peak_dbfs"] = peak_db
            meta["folder"] = str(folder)
            meta["folder_audio_files"] = [str(a) for a in folder_audios]
            cameras_info[cam_key] = meta

    # Probe external audio files
    audio_tracks_info: List[Dict[str, Any]] = []
    audio_envelopes: Dict[str, List[float]] = {}
    for idx, a_path in enumerate(discovered_audios):
        a_meta = probe_media(a_path)
        env, peak_db = extract_envelope_100hz(a_path)
        a_meta["peak_dbfs"] = peak_db
        a_meta["track_id"] = f"Audio_{idx + 1}"
        audio_tracks_info.append(a_meta)
        audio_envelopes[str(a_path)] = env

    # Determine Master Audio Spine
    master_audio_path: Optional[str] = None
    master_audio_mode = "camera_embedded"
    ref_env: List[float] = []

    active_ext_audios = [a for a in audio_tracks_info if a.get("peak_dbfs", -100.0) > -55.0]
    if len(active_ext_audios) == 1:
        master_audio_path = active_ext_audios[0]["path"]
        master_audio_mode = "single_external_master"
        ref_env = audio_envelopes.get(master_audio_path, [])
    elif len(active_ext_audios) >= 2:
        # Check if one file is clearly named "master" / "mix" or if they are per-speaker stems
        master_candidates = [a for a in active_ext_audios if any(k in Path(a["path"]).stem.lower() for k in ("master", "mix", "full", "podcast"))]
        if master_candidates:
            master_audio_path = master_candidates[0]["path"]
            master_audio_mode = "named_external_master"
            ref_env = audio_envelopes.get(master_audio_path, [])
        else:
            mixed_wav = sources_dir / "Podcast_Master_Mix.wav"
            built = build_mixed_master_audio([Path(a["path"]) for a in active_ext_audios], mixed_wav)
            if built:
                master_audio_path = str(built.resolve())
                master_audio_mode = "multi_mic_stems_mixed"
                ref_env, _ = extract_envelope_100hz(built)
    if not master_audio_path and cameras_info:
        # Pick the camera with the cleanest / loudest embedded audio
        best_cam = max(cameras_info.keys(), key=lambda k: cameras_info[k].get("peak_dbfs", -100.0))
        master_audio_path = cameras_info[best_cam]["path"]
        master_audio_mode = f"camera_audio ({best_cam})"
        ref_env = cam_envelopes.get(best_cam, [])

    # Align each camera against the Master Audio Spine
    for cam_key, meta in cameras_info.items():
        c_env = cam_envelopes.get(cam_key, [])
        if meta["path"] == master_audio_path:
            offset_sec, conf = 0.0, 1.0
        else:
            offset_sec, conf = compute_sync_offset_sec(ref_env, c_env)
        meta["sync_offset_sec"] = offset_sec
        meta["sync_confidence"] = conf

    # Also align individual external audio stems against Master Audio Spine
    for a_meta in audio_tracks_info:
        a_env = audio_envelopes.get(a_meta["path"], [])
        if a_meta["path"] == master_audio_path:
            a_meta["sync_offset_sec"] = 0.0
            a_meta["sync_confidence"] = 1.0
        else:
            off, cf = compute_sync_offset_sec(ref_env, a_env)
            a_meta["sync_offset_sec"] = off
            a_meta["sync_confidence"] = cf

    # Determine canonical sequence settings (resolution, fps, master duration)
    first_cam = next(iter(cameras_info.values()), {})
    seq_width = int(first_cam.get("width") or 1920)
    seq_height = int(first_cam.get("height") or 1080)
    seq_fps = float(first_cam.get("fps") or 30.0)
    master_duration = max(
        [float(m.get("duration", 0.0)) for m in cameras_info.values()]
        + [float(a.get("duration", 0.0)) for a in audio_tracks_info]
        + [0.0]
    )

    sync_payload = {
        "status": "success" if cameras_info else "error",
        "os": platform.system(),
        "project_dir": str(project_dir),
        "edit_dir": str(edit_dir),
        "sequence_defaults": {
            "width": seq_width,
            "height": seq_height,
            "fps": seq_fps,
            "master_duration_sec": round(master_duration, 3),
        },
        "master_audio": {
            "path": master_audio_path,
            "mode": master_audio_mode,
        },
        "cameras": cameras_info,
        "external_audio_tracks": audio_tracks_info,
    }

    sync_path = edit_dir / "sync_map.json"
    sync_path.write_text(json.dumps(sync_payload, indent=2), encoding="utf-8")
    return sync_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest Camera 1, Camera 2, Camera 3 + Audio and compute waveform sync")
    parser.add_argument("--project-dir", type=Path, default=Path("."), help="Root folder containing Camera 1, Camera 2, Camera 3")
    parser.add_argument("--cam1", type=str, default=None, help="Explicit path to Camera 1 folder or video")
    parser.add_argument("--cam2", type=str, default=None, help="Explicit path to Camera 2 folder or video")
    parser.add_argument("--cam3", type=str, default=None, help="Explicit path to Camera 3 folder or video")
    parser.add_argument("--audio", nargs="*", default=None, help="Optional explicit audio file(s) or folder")
    parser.add_argument("--edit-dir", type=Path, default=None, help="Output edit directory (default: <project-dir>/edit)")
    args = parser.parse_args()

    res = ingest_and_sync_podcast(
        project_dir=args.project_dir,
        cam1=args.cam1,
        cam2=args.cam2,
        cam3=args.cam3,
        audio_paths=args.audio,
        edit_dir=args.edit_dir,
    )
    print(json.dumps(res, indent=2))
    return 0 if res.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
