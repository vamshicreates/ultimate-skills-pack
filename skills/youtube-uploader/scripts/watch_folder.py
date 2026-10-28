#!/usr/bin/env python3
"""Watch local folders (`uploads/` and `projects/*/final_*.mp4`) for newly added videos,
verify the file write is finished via ffprobe, automatically update local MP4 meta tags
and generate the full YouTube SEO upload package via `prepare_video_package.py`.

Usage:
  # Scan once for any newly added videos in `uploads/` or `projects/`:
  .agents/skills/video-use/.venv/bin/python .agents/skills/youtube-uploader/scripts/watch_folder.py --scan-once

  # Run as a continuous background folder watcher:
  .agents/skills/video-use/.venv/bin/python .agents/skills/youtube-uploader/scripts/watch_folder.py --watch --interval 5
"""

from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = SKILL_DIR.parent.parent.parent
VIDEO_USE_PYTHON = SKILL_DIR.parent / "video-use" / ".venv" / "bin" / "python"
PREPARE_SCRIPT = SKILL_DIR / "scripts" / "prepare_video_package.py"
DEFAULT_UPLOADS_DIR = WORKSPACE_ROOT / "uploads"
HISTORY_FILE = DEFAULT_UPLOADS_DIR / "upload_history.json"

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


def ensure_ffmpeg_on_path() -> None:
    extra_paths: list[str] = [str(SKILL_DIR.parent / "video-use" / ".venv" / "bin")]
    for candidate in sorted(glob.glob("/usr/local/Cellar/ffmpeg/*/bin"), reverse=True):
        extra_paths.append(candidate)
    for candidate in sorted(glob.glob("/opt/homebrew/Cellar/ffmpeg/*/bin"), reverse=True):
        extra_paths.append(candidate)
    current = os.environ.get("PATH", "")
    os.environ["PATH"] = ":".join(extra_paths + [current])


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"videos": {}}


def save_history(history: dict) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def wait_until_file_complete(video_path: Path, stability_seconds: float = 2.0) -> bool:
    """Wait until file size stops changing and ffprobe validates a readable video stream."""
    if not video_path.exists():
        return False
    prev_size = video_path.stat().st_size
    if prev_size == 0:
        return False
    time.sleep(stability_seconds)
    if not video_path.exists():
        return False
    curr_size = video_path.stat().st_size
    if curr_size != prev_size or curr_size < 1024:
        return False

    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,duration",
        "-of", "json",
        str(video_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0


def discover_candidate_videos(watch_dirs: list[Path]) -> list[Path]:
    """Find top-level video files in `uploads/` and final exported videos in `projects/*/`."""
    candidates: list[Path] = []
    for d in watch_dirs:
        if not d.exists():
            continue
        if d.name == "projects":
            for p in sorted(d.glob("*/final_*.mp4")):
                if p.is_file():
                    candidates.append(p.resolve())
        else:
            for item in sorted(d.iterdir()):
                if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
                    candidates.append(item.resolve())
    return candidates


def process_new_video(video_path: Path, channel: str, history: dict) -> dict | None:
    key = str(video_path)
    existing = history.get("videos", {}).get(key)
    if existing and existing.get("status") in {"prepared", "uploaded"}:
        return None

    print(f"[watch_folder] Detected new video file: {video_path}")
    if not wait_until_file_complete(video_path):
        print(f"[watch_folder] File still being written or incomplete, skipping for now: {video_path}")
        return None

    python_bin = str(VIDEO_USE_PYTHON) if VIDEO_USE_PYTHON.exists() else sys.executable
    cmd = [
        python_bin,
        str(PREPARE_SCRIPT),
        "--video", str(video_path),
        "--channel", channel,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[watch_folder] ERROR preparing {video_path}:\n{res.stderr}", file=sys.stderr)
        return None

    print(res.stdout.strip())

    project_dir = video_path.parent
    meta_json_path = project_dir / "youtube_ready" / "youtube_metadata.json"
    record = {
        "video_path": str(video_path),
        "detected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "prepared",
        "metadata_json": str(meta_json_path) if meta_json_path.exists() else None,
        "youtube_url": None,
        "pinned_comment_verified": False,
    }
    history.setdefault("videos", {})[key] = record
    save_history(history)
    return record


def main() -> None:
    ensure_ffmpeg_on_path()
    parser = argparse.ArgumentParser(description="Monitor local folder for new videos to prepare and upload to YouTube.")
    parser.add_argument("--watch", action="store_true", help="Continuously watch folders for new video files.")
    parser.add_argument("--scan-once", action="store_true", default=True, help="Scan folders once and prepare any new videos.")
    parser.add_argument("--interval", type=float, default=5.0, help="Polling interval in seconds when --watch is active.")
    parser.add_argument("--channel", default="Vamshi Creates", help="YouTube Channel name.")
    parser.add_argument("--folder", action="append", default=[], help="Additional folder path(s) to watch.")
    args = parser.parse_args()

    DEFAULT_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    watch_dirs = [DEFAULT_UPLOADS_DIR, WORKSPACE_ROOT / "projects"]
    for extra in args.folder:
        watch_dirs.append(Path(extra).resolve())

    history = load_history()

    if not args.watch:
        candidates = discover_candidate_videos(watch_dirs)
        prepared_now = []
        for c in candidates:
            rec = process_new_video(c, args.channel, history)
            if rec:
                prepared_now.append(rec)
        print(f"[watch_folder] Scan complete. Total tracked: {len(history.get('videos', {}))}, Newly prepared: {len(prepared_now)}")
        return

    print(f"[watch_folder] Watching {[str(d) for d in watch_dirs]} every {args.interval}s...")
    try:
        while True:
            history = load_history()
            for c in discover_candidate_videos(watch_dirs):
                process_new_video(c, args.channel, history)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[watch_folder] Stopped.")


if __name__ == "__main__":
    main()
