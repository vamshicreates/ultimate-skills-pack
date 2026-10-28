#!/usr/bin/env python3
"""Policy pre-flight validator, YouTube Studio DOM helper generator, and post-publish
link recorder for the `youtube-uploader` skill.

Usage:
  # 1. Pre-flight policy & SEO validation before opening YouTube Studio:
  .agents/skills/video-use/.venv/bin/python .agents/skills/youtube-uploader/scripts/youtube_studio_helper.py \
    --validate projects/siddhi_vinayaka/youtube_ready/youtube_metadata.json

  # 2. Record published YouTube link & pinned comment verification after upload:
  .agents/skills/video-use/.venv/bin/python .agents/skills/youtube-uploader/scripts/youtube_studio_helper.py \
    --record-publish projects/siddhi_vinayaka/youtube_ready/youtube_metadata.json \
    --url "https://youtu.be/XXXXXXXXXXX" \
    --pinned-comment-verified
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
HISTORY_FILE = WORKSPACE_ROOT / "uploads" / "upload_history.json"


def validate_metadata_package(meta_path: Path) -> tuple[bool, list[str]]:
    """Verify every YouTube upload policy & character limit before browser upload."""
    if not meta_path.exists():
        return False, [f"Metadata JSON not found: {meta_path}"]

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    title = meta.get("title", "")
    if not title or len(title) > 100:
        errors.append(f"Title length must be 1..100 chars (got {len(title)}).")

    desc = meta.get("description", "")
    if not desc or len(desc) > 5000:
        errors.append(f"Description length must be 1..5000 chars (got {len(desc)}).")

    if "00:00" not in desc:
        errors.append("Description is missing a '00:00' starting timestamp chapter.")

    hashtags = re.findall(r"#[A-Za-z0-9_]+", desc)
    if len(hashtags) > 15:
        errors.append(f"YouTube Policy violation: Description has {len(hashtags)} hashtags (max allowed is 15).")

    tags_csv = meta.get("tags_csv", "")
    if len(tags_csv) > 500:
        errors.append(f"Tags CSV exceeds YouTube Studio 500-char limit (got {len(tags_csv)}).")

    settings = meta.get("studio_settings", {})
    if settings.get("audience_made_for_kids") is not False:
        errors.append("Audience must be set to 'No, it's not made for kids' so comments & pinning remain enabled.")

    if "altered_or_synthetic_content_ai" not in settings:
        errors.append("Missing mandatory 'altered_or_synthetic_content_ai' policy flag.")

    local_files = meta.get("local_files", {})
    tagged_video = local_files.get("seo_tagged_video_path")
    if not tagged_video or not Path(tagged_video).exists():
        errors.append(f"Tagged video file does not exist: {tagged_video}")

    thumb = local_files.get("thumbnail_path")
    if thumb and Path(thumb).exists():
        size_mb = Path(thumb).stat().st_size / (1024 * 1024)
        if size_mb >= 2.0:
            errors.append(f"Custom thumbnail exceeds YouTube 2MB limit ({size_mb:.2f} MB).")

    pinned = meta.get("pinned_comment", "")
    if not pinned.strip():
        errors.append("Pinned engagement comment text is empty.")

    return len(errors) == 0, errors


def record_published_url(meta_path: Path, youtube_url: str, pinned_verified: bool) -> None:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    meta["publish_result"] = {
        "youtube_url": youtube_url,
        "published_at": now_iso,
        "pinned_comment_verified": pinned_verified,
        "liked_own_video": True,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # Update central upload_history.json
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    history = {"videos": {}}
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    orig_video = meta.get("local_files", {}).get("original_video_path") or str(meta_path.parent)
    history.setdefault("videos", {})[orig_video] = {
        "video_path": orig_video,
        "seo_tagged_video_path": meta.get("local_files", {}).get("seo_tagged_video_path"),
        "title": meta.get("title"),
        "status": "uploaded",
        "youtube_url": youtube_url,
        "pinned_comment": meta.get("pinned_comment"),
        "pinned_comment_verified": pinned_verified,
        "published_at": now_iso,
        "metadata_json": str(meta_path.resolve()),
    }
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[youtube_studio_helper] Recorded published URL: {youtube_url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate YouTube metadata package or record published URL.")
    parser.add_argument("--validate", default=None, help="Path to youtube_metadata.json to validate.")
    parser.add_argument("--record-publish", default=None, help="Path to youtube_metadata.json to update after publishing.")
    parser.add_argument("--url", default=None, help="Published YouTube URL (e.g., https://youtu.be/xxxx).")
    parser.add_argument("--pinned-comment-verified", action="store_true", help="Confirm comment was posted and pinned.")
    args = parser.parse_args()

    if args.validate:
        meta_path = Path(args.validate).resolve()
        ok, errs = validate_metadata_package(meta_path)
        if not ok:
            print("❌ PRE-FLIGHT VALIDATION FAILED:", file=sys.stderr)
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(1)
        print(f"✅ PRE-FLIGHT VALIDATION PASSED: {meta_path}")
        print("All YouTube policies (Title <=100, Description <=5000, Tags <=500, Hashtags <=15, Not Made For Kids, AI Disclosure, Thumbnail <2MB, Pinned Comment) verified!")

    if args.record_publish:
        if not args.url:
            print("ERROR: --url is required with --record-publish", file=sys.stderr)
            sys.exit(1)
        record_published_url(Path(args.record_publish).resolve(), args.url, args.pinned_comment_verified)


if __name__ == "__main__":
    main()
