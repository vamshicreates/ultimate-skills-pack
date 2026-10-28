#!/usr/bin/env python3
"""Fast, lightweight helper to identify a local video file for YouTube upload
and generate a clean Title and Description without re-encoding or transcribing.

Usage:
  # Find the next un-uploaded video (or newest video) in `uploads/` or workspace:
  python3 .agents/skills/basic-youtube-uploader/scripts/find_local_video.py

  # Or target a specific file/folder:
  python3 .agents/skills/basic-youtube-uploader/scripts/find_local_video.py --path uploads/my_video.mp4

  # Record a completed Unlisted upload in `uploads/upload_history.json`:
  python3 .agents/skills/basic-youtube-uploader/scripts/find_local_video.py --record "/abs/path/video.mp4" --url "https://youtu.be/xyz"
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = SKILL_DIR.parent.parent.parent
UPLOADS_DIR = WORKSPACE_ROOT / "uploads"
HISTORY_FILE = UPLOADS_DIR / "upload_history.json"

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


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


def clean_title_from_filename(video_path: Path) -> str:
    """Turn a raw video filename into a clean, readable YouTube title (<= 100 chars)."""
    stem = video_path.stem
    # Remove common prefix/suffix noise like 'final_'
    stem = re.sub(r"^final[_-]+", "", stem, flags=re.IGNORECASE)
    # Replace underscores with pipe or spaces
    stem = stem.replace(" _ ", " | ").replace("_", " ")
    # Collapse multiple spaces
    stem = re.sub(r"\s+", " ", stem).strip()
    if not stem:
        stem = "New Video Upload"
    # Title-case if all lowercase
    if stem == stem.lower():
        stem = stem.title()
    return stem[:100].strip()


def build_simple_description(title: str, video_path: Path) -> str:
    """Generate a clean, simple description from the video title."""
    return (
        f"{title}\n\n"
        f"Uploaded via Vamshi Creates.\n"
        f"File: {video_path.name}"
    )


def find_candidate_videos(search_root: Path | None = None, include_uploaded: bool = False) -> list[Path]:
    """Scan `uploads/`, `projects/*/`, and workspace root for local video files."""
    history = load_history().get("videos", {})
    candidates: list[Path] = []

    if search_root and search_root.is_file():
        return [search_root.resolve()]

    dirs_to_scan = [UPLOADS_DIR, WORKSPACE_ROOT / "projects", WORKSPACE_ROOT]
    if search_root and search_root.is_dir():
        dirs_to_scan.insert(0, search_root)

    seen: set[Path] = set()
    for folder in dirs_to_scan:
        if not folder.exists():
            continue
        if folder == WORKSPACE_ROOT / "projects":
            items = sorted(folder.glob("*/final_*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        else:
            items = sorted(
                (p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        for item in items:
            resolved = item.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            rec = history.get(str(resolved), {})
            if not include_uploaded and rec.get("status") == "uploaded":
                continue
            candidates.append(resolved)

    return candidates


def record_upload(video_path: Path, youtube_url: str, title: str, visibility: str = "UNLISTED") -> dict:
    history = load_history()
    resolved = str(video_path.resolve())
    entry = {
        "video_path": resolved,
        "title": title,
        "visibility": visibility,
        "status": "uploaded",
        "youtube_url": youtube_url,
        "uploaded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    history.setdefault("videos", {})[resolved] = entry
    save_history(history)
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description="Identify local video and prepare simple Title & Description for Unlisted YouTube upload.")
    parser.add_argument("--path", type=str, default=None, help="Specific video file or folder to check.")
    parser.add_argument("--include-uploaded", action="store_true", help="Include videos already marked as uploaded.")
    parser.add_argument("--record", type=str, default=None, help="Record a finished upload for the given video path.")
    parser.add_argument("--url", type=str, default=None, help="YouTube URL when using --record.")
    parser.add_argument("--title", type=str, default=None, help="Optional custom title.")
    args = parser.parse_args()

    if args.record:
        vpath = Path(args.record).resolve()
        title = args.title or clean_title_from_filename(vpath)
        rec = record_upload(vpath, args.url or "", title, visibility="UNLISTED")
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        return

    target = Path(args.path).resolve() if args.path else None
    candidates = find_candidate_videos(target, include_uploaded=args.include_uploaded)
    if not candidates and not args.include_uploaded:
        # Fallback to most recent video even if previously uploaded
        candidates = find_candidate_videos(target, include_uploaded=True)

    if not candidates:
        print(json.dumps({"error": "No video files (.mp4, .mov, .mkv, .webm) found in uploads/ or workspace."}, indent=2))
        sys.exit(1)

    selected = candidates[0]
    title = clean_title_from_filename(selected)
    description = build_simple_description(title, selected)

    result = {
        "video_path": str(selected),
        "filename": selected.name,
        "size_mb": round(selected.stat().st_size / (1024 * 1024), 2),
        "title": title,
        "description": description,
        "visibility": "UNLISTED",
        "all_candidates": [str(c) for c in candidates],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
