#!/usr/bin/env python3
"""
Cross-Platform Universal Harvester for Blender Knowledge.
Extracts Blender tutorials from:
1. Online URLs (YouTube videos, playlists, or direct video streams via yt-dlp).
2. Local video files (.mp4, .mkv, .mov, .webm, .avi) located on disk.

Extracts transcripts, embedded/sidecar subtitles, chapters, and keyframe snapshots
without requiring any paid API tokens or ElevenLabs.

Compatible with macOS, Windows, and Linux.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SKILL_ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_ROOT / "references"
RAW_DATA_DIR = SKILL_ROOT / "data" / "harvested_raw"


def get_binary_path(binary_name: str) -> Optional[str]:
    """Find absolute path for a system tool."""
    path = shutil.which(binary_name)
    if path:
        return path
    
    # Common local search paths
    system = platform.system()
    home = Path.home()
    extra_paths = [
        home / ".local" / "bin" / binary_name,
        Path("/usr/local/bin") / binary_name,
        Path("/opt/homebrew/bin") / binary_name,
    ]
    if system == "Windows":
        extra_paths.extend([
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / binary_name / f"{binary_name}.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / binary_name / f"{binary_name}.exe",
        ])
    for ep in extra_paths:
        if ep.exists():
            return str(ep)
    return None


def clean_vtt_content(vtt_text: str) -> str:
    """Parse WebVTT or SRT text into clean, deduplicated timestamped blocks."""
    lines = vtt_text.splitlines()
    clean_lines = []
    seen = set()
    
    time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2}[\.,]\d{3}|\d{2}:\d{2}[\.,]\d{3})\s*-->")
    
    current_time = ""
    for line in lines:
        line = line.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        
        match = time_pattern.search(line)
        if match:
            current_time = match.group(1).replace(",", ".").split(".")[0]
            continue
            
        # Strip HTML/VTT tags
        text_clean = re.sub(r"<[^>]+>", "", line).strip()
        if not text_clean or text_clean.isdigit():
            continue
            
        if text_clean in seen:
            continue
        seen.add(text_clean)
        if len(seen) > 30:
            seen.clear()
            
        if current_time:
            clean_lines.append(f"[{current_time}] {text_clean}")
        else:
            clean_lines.append(text_clean)
            
    return "\n".join(clean_lines)


def fetch_video_metadata(url: str, ytdlp_path: str) -> Dict:
    """Fetch video title, description, chapters, and duration using yt-dlp."""
    cmd = [
        ytdlp_path,
        "--dump-json",
        "--skip-download",
        "--no-playlist",
        url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except Exception as e:
        print(f"[!] Warning: Failed to fetch full metadata: {e}")
        return {"title": "Unknown Title", "description": "", "chapters": [], "duration": 0}


def fetch_subtitles(url: str, output_prefix: Path, ytdlp_path: str) -> Optional[Path]:
    """Download best English subtitles or automatic captions from online URL."""
    cmd = [
        ytdlp_path,
        "--write-sub",
        "--write-auto-sub",
        "--sub-lang", "en.*,en",
        "--skip-download",
        "--sub-format", "vtt/srt/best",
        "--no-playlist",
        "-o", str(output_prefix),
        url
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        parent = output_prefix.parent
        stem = output_prefix.name
        matches = list(parent.glob(f"{stem}*.vtt")) + list(parent.glob(f"{stem}*.srt"))
        if matches:
            matches.sort(key=lambda p: len(p.name))
            return matches[0]
    except Exception as e:
        print(f"[!] Error fetching subtitles via yt-dlp: {e}")
    return None


def extract_local_subtitles(video_path: Path, output_file: Path, ffmpeg_path: str) -> Optional[Path]:
    """Extract embedded subtitle track or detect sidecar .srt/.vtt file for a local video."""
    # 1. Check sidecar file first (e.g. video.srt or video.vtt)
    sidecar_candidates = [
        video_path.with_suffix(".srt"),
        video_path.with_suffix(".vtt"),
        video_path.parent / f"{video_path.stem}.en.srt",
        video_path.parent / f"{video_path.stem}.en.vtt",
    ]
    for sc in sidecar_candidates:
        if sc.exists():
            print(f"[+] Found sidecar subtitle file: {sc}")
            shutil.copyfile(sc, output_file)
            return output_file

    # 2. Extract embedded subtitle track using ffmpeg
    cmd = [
        ffmpeg_path,
        "-i", str(video_path),
        "-map", "0:s:0",
        "-y",
        str(output_file)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=30)
        if output_file.exists() and output_file.stat().st_size > 0:
            print(f"[+] Extracted embedded subtitle track with ffmpeg")
            return output_file
    except Exception:
        pass
    return None


def extract_keyframes_from_input(source: str, timestamps: List[str], output_dir: Path, ffmpeg_path: str, is_local: bool, ytdlp_path: Optional[str] = None) -> List[str]:
    """Extract visual screenshots at specified timestamps from online stream or local file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_frames = []
    
    if not timestamps:
        return []
    
    stream_input = source
    if not is_local:
        if not ytdlp_path:
            return []
        cmd_url = [ytdlp_path, "-f", "bestvideo[height<=720]/best[height<=720]/best", "-g", source]
        try:
            stream_res = subprocess.run(cmd_url, capture_output=True, text=True, check=True)
            stream_input = stream_res.stdout.strip().splitlines()[0]
        except Exception as e:
            print(f"[!] Warning: Could not resolve stream URL for keyframe extraction: {e}")
            return []

    for i, ts in enumerate(timestamps):
        safe_ts = ts.replace(":", "-")
        out_img = output_dir / f"frame_{i:02d}_{safe_ts}.jpg"
        ff_cmd = [
            ffmpeg_path,
            "-ss", ts,
            "-i", stream_input,
            "-frames:v", "1",
            "-q:v", "3",
            "-y",
            str(out_img)
        ]
        try:
            subprocess.run(ff_cmd, capture_output=True, timeout=30)
            if out_img.exists():
                extracted_frames.append(str(out_img))
        except Exception as e:
            print(f"[!] Frame extraction timeout at {ts}: {e}")
            
    return extracted_frames


def harvest_source(target: str, category: str = "recipes", keyframe_interval_sec: int = 180) -> Dict:
    """Harvest transcript, metadata, and keyframes from either a YouTube URL or a Local Video File."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_binary_path("ffmpeg")
    ytdlp_bin = get_binary_path("yt-dlp")
    
    target_path = Path(target).expanduser().resolve()
    is_local_file = target_path.exists() and target_path.is_file()
    
    if is_local_file:
        print(f"[*] Detected Local Video File: {target_path}")
        video_id = target_path.stem
        safe_title = re.sub(r"[^\w\-_\. ]", "", target_path.stem).strip().replace(" ", "_")[:50]
        video_dir = RAW_DATA_DIR / f"local_{video_id}_{safe_title}"
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Subtitles / Transcript
        sub_file = None
        if ffmpeg_bin:
            sub_file = extract_local_subtitles(target_path, video_dir / "extracted_subs.srt", ffmpeg_bin)
            
        transcript_text = ""
        if sub_file and sub_file.exists():
            raw_text = sub_file.read_text(encoding="utf-8", errors="ignore")
            transcript_text = clean_vtt_content(raw_text)
            (video_dir / "clean_transcript.txt").write_text(transcript_text, encoding="utf-8")
            print(f"[+] Saved clean transcript ({len(transcript_text.splitlines())} lines)")
        else:
            print("[!] No embedded or sidecar subtitles found for local video.")
            
        # Duration via ffprobe or ffmpeg
        duration = 0
        if ffmpeg_bin:
            probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(target_path)]
            try:
                p_out = subprocess.check_output(probe_cmd, text=True, stderr=subprocess.DEVNULL).strip()
                duration = int(float(p_out))
            except Exception:
                duration = 600  # 10 min fallback
                
        # Generate sample keyframe timestamps
        keyframe_timestamps = []
        for sec in range(min(60, duration // 4), duration, keyframe_interval_sec):
            m, s = divmod(sec, 60)
            h, m = divmod(m, 60)
            keyframe_timestamps.append(f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}")
            if len(keyframe_timestamps) >= 8:
                break
                
        frames = []
        if ffmpeg_bin and keyframe_timestamps:
            print(f"[*] Extracting keyframes from local video...")
            frames = extract_keyframes_from_input(str(target_path), keyframe_timestamps[:8], video_dir / "frames", ffmpeg_bin, is_local=True)
            print(f"[+] Extracted {len(frames)} keyframes.")
            
        meta = {
            "title": target_path.stem.replace("_", " ").title(),
            "channel": "Local Library",
            "chapters": [],
            "duration": duration
        }
        source_url = f"file://{target_path}"

    else:
        # Online / YouTube URL
        if not ytdlp_bin:
            raise RuntimeError("yt-dlp binary not found. Run scripts/install.py first.")
            
        print(f"[*] Detected Online Video URL: {target}")
        meta = fetch_video_metadata(target, ytdlp_bin)
        video_id = meta.get("id", "video")
        safe_title = re.sub(r"[^\w\-_\. ]", "", meta.get("title", video_id)).strip().replace(" ", "_")[:50]
        video_dir = RAW_DATA_DIR / f"{video_id}_{safe_title}"
        video_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[*] Downloading transcript / captions...")
        sub_prefix = video_dir / "transcript"
        sub_file = fetch_subtitles(target, sub_prefix, ytdlp_bin)
        
        transcript_text = ""
        if sub_file and sub_file.exists():
            raw_text = sub_file.read_text(encoding="utf-8", errors="ignore")
            transcript_text = clean_vtt_content(raw_text)
            (video_dir / "clean_transcript.txt").write_text(transcript_text, encoding="utf-8")
            print(f"[+] Saved clean transcript ({len(transcript_text.splitlines())} lines)")
        else:
            print("[!] No auto-subtitles found.")
            
        chapters = meta.get("chapters") or []
        keyframe_timestamps = []
        if chapters:
            print(f"[+] Found {len(chapters)} chapters:")
            for ch in chapters:
                start = int(ch.get("start_time", 0))
                m, s = divmod(start, 60)
                h, m = divmod(m, 60)
                ts_str = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
                keyframe_timestamps.append(ts_str)
        else:
            duration = int(meta.get("duration", 0))
            if duration > 0:
                for sec in range(min(60, duration // 4), duration, keyframe_interval_sec):
                    m, s = divmod(sec, 60)
                    h, m = divmod(m, 60)
                    keyframe_timestamps.append(f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}")
                    if len(keyframe_timestamps) >= 8:
                        break

        frames = []
        if ffmpeg_bin and keyframe_timestamps:
            print(f"[*] Extracting keyframes from online stream...")
            frames = extract_keyframes_from_input(target, keyframe_timestamps[:8], video_dir / "frames", ffmpeg_bin, is_local=False, ytdlp_path=ytdlp_bin)
            print(f"[+] Extracted {len(frames)} keyframes.")
        source_url = target

    # Assemble packet
    packet = {
        "id": video_id,
        "title": meta.get("title", ""),
        "channel": meta.get("channel", meta.get("uploader", "Source")),
        "url": source_url,
        "category": category,
        "clean_transcript_path": str(video_dir / "clean_transcript.txt") if transcript_text else None,
        "keyframes": frames,
        "chapters": meta.get("chapters", []),
        "video_dir": str(video_dir)
    }
    
    (video_dir / "metadata.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"\n[SUCCESS] Knowledge harvested successfully into: {video_dir}")
    print(f"Run the knowledge distiller to format into references/{category}/")
    return packet


def main():
    parser = argparse.ArgumentParser(description="Harvest Blender knowledge from YouTube or local video files without paid APIs.")
    parser.add_argument("--source", "--url", "-s", "-u", required=True, 
                        help="YouTube URL OR local video file path (/path/to/tutorial.mp4)")
    parser.add_argument("--category", "-c", default="recipes", 
                        choices=["recipes", "shaders", "modifiers", "topology"], 
                        help="Target knowledge category")
    parser.add_argument("--interval", type=int, default=180, help="Seconds between keyframes if no chapters")
    
    args = parser.parse_args()
    harvest_source(args.source, args.category, args.interval)


if __name__ == "__main__":
    main()
