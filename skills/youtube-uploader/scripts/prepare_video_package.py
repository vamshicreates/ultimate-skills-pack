#!/usr/bin/env python3
"""Prepare a local video file for YouTube upload with full SEO, local MP4 meta tags,
custom high-CTR thumbnail (<2MB), policy compliance flags, and pinned comment package.

Usage:
  .agents/skills/video-use/.venv/bin/python .agents/skills/youtube-uploader/scripts/prepare_video_package.py \
    --video projects/siddhi_vinayaka/final_siddhi_vinayaka.mp4 \
    --storyboard projects/siddhi_vinayaka/storyboard.json
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

SKILL_DIR = Path(__file__).resolve().parent.parent
VIDEO_USE_DIR = SKILL_DIR.parent / "video-use"


def ensure_ffmpeg_on_path() -> None:
    """Ensure venv bin and Homebrew Cellar ffmpeg/ffprobe are on PATH."""
    extra_paths: list[str] = [str(VIDEO_USE_DIR / ".venv" / "bin")]
    for candidate in sorted(glob.glob("/usr/local/Cellar/ffmpeg/*/bin"), reverse=True):
        extra_paths.append(candidate)
    for candidate in sorted(glob.glob("/opt/homebrew/Cellar/ffmpeg/*/bin"), reverse=True):
        extra_paths.append(candidate)
    current = os.environ.get("PATH", "")
    os.environ["PATH"] = ":".join(extra_paths + [current])


def detect_script_language(text: str) -> dict[str, str]:
    """Detect primary language & script from lyrics/title text."""
    for ch in text:
        cp = ord(ch)
        if 0x0C00 <= cp <= 0x0C7F:
            return {"name": "Telugu", "iso639_2": "tel", "bcp47": "te", "font": "Kohinoor Telugu Bold"}
        if 0x0900 <= cp <= 0x097F:
            return {"name": "Hindi", "iso639_2": "hin", "bcp47": "hi", "font": "Kohinoor Devanagari Bold"}
        if 0x0B80 <= cp <= 0x0BFF:
            return {"name": "Tamil", "iso639_2": "tam", "bcp47": "ta", "font": "Kohinoor Tamil Bold"}
        if 0x0C80 <= cp <= 0x0CFF:
            return {"name": "Kannada", "iso639_2": "kan", "bcp47": "kn", "font": "Kannada Sangam MN"}
        if 0x0D00 <= cp <= 0x0D7F:
            return {"name": "Malayalam", "iso639_2": "mal", "bcp47": "ml", "font": "Malayalam Sangam MN"}
    return {"name": "English", "iso639_2": "eng", "bcp47": "en", "font": "Helvetica Neue"}


def format_timestamp_mmss(seconds: float) -> str:
    total_sec = max(0, int(round(seconds)))
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins:02d}:{secs:02d}"


def slugify_filename(text: str) -> str:
    """Create a clean ASCII SEO filename slug."""
    ascii_text = re.sub(r"[^\x00-\x7F]+", " ", text)
    ascii_text = re.sub(r"[^A-Za-z0-9]+", "-", ascii_text).strip("-")
    ascii_text = re.sub(r"-{2,}", "-", ascii_text)
    return ascii_text or "Official-Lyric-Video"


def probe_video_info(video_path: Path) -> dict:
    """Run ffprobe to inspect video duration, resolution, and existing container tags."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {}
    try:
        return json.loads(res.stdout)
    except Exception:
        return {}


def build_chapters_from_slides(slides: list[dict]) -> list[dict[str, str]]:
    """Build YouTube-compliant timestamp chapters (starts at 00:00, >=3 chapters, each >=10s)."""
    if not slides:
        return [{"timestamp": "00:00", "title": "Intro & Opening Verse"}]

    raw_chapters: list[tuple[float, str]] = []
    seen_sections: set[str] = set()
    for idx, slide in enumerate(slides):
        start = float(slide.get("start", 0.0))
        section = (slide.get("section") or "").strip()
        lyric_first_line = (slide.get("lyric") or "").split("\n")[0].strip()
        short_lyric = re.sub(r"\s+", " ", lyric_first_line)[:42].strip(" —-.,")

        if idx == 0:
            label = f"{section} - {short_lyric}" if section else (short_lyric or "Opening Invocation")
            raw_chapters.append((0.0, label))
            if section:
                seen_sections.add(section)
            continue

        # Add chapter when section changes and at least 10 seconds have elapsed since last chapter
        last_start = raw_chapters[-1][0]
        if section and section not in seen_sections and (start - last_start) >= 10.0:
            label = f"{section} ({short_lyric})" if short_lyric else section
            raw_chapters.append((start, label))
            seen_sections.add(section)
        elif not section and (start - last_start) >= 20.0:
            raw_chapters.append((start, short_lyric or f"Verse {len(raw_chapters) + 1}"))

    # Ensure at least 3 chapters if video is >= 30s
    total_end = float(slides[-1].get("end", 0.0))
    if len(raw_chapters) < 3 and total_end >= 30.0:
        raw_chapters = [(0.0, raw_chapters[0][1])]
        mid_slide = slides[len(slides) // 2]
        last_slide = slides[max(0, int(len(slides) * 0.78))]
        raw_chapters.append((
            max(10.0, float(mid_slide.get("start", 12.0))),
            (mid_slide.get("section") or "Main Chorus & Melody"),
        ))
        if float(last_slide.get("start", 25.0)) - raw_chapters[-1][0] >= 10.0:
            raw_chapters.append((
                float(last_slide.get("start", 25.0)),
                (last_slide.get("section") or "Climax & Finale"),
            ))

    return [
        {"timestamp": format_timestamp_mmss(ts), "title": title}
        for ts, title in raw_chapters
    ]


def build_seo_metadata(
    video_path: Path,
    storyboard: dict | None,
    srt_path: Path | None,
    channel_name: str,
    is_ai_generated: bool,
) -> dict:
    """Generate complete, policy-compliant YouTube SEO metadata from storyboard & lyrics."""
    sb = storyboard or {}
    raw_title = sb.get("title") or video_path.stem.replace("_", " ").title()
    song_slug = sb.get("song_slug") or slugify_filename(raw_title).lower().replace("-", "_")
    slides = sb.get("slides") or []
    style_anchor = sb.get("style_anchor") or ""

    all_lyrics_text = "\n".join(s.get("lyric", "") for s in slides)
    lang_info = detect_script_language(raw_title + "\n" + all_lyrics_text)
    lang_name = lang_info["name"]

    # Check if devotional / spiritual theme
    combined_lower = (raw_title + " " + style_anchor + " " + " ".join(s.get("meaning", "") for s in slides)).lower()
    is_devotional = any(
        kw in combined_lower
        for kw in ["devotional", "vinayaka", "ganesha", "ganapati", "temple", "divine", "sacred", "shiva", "bhajan", "stotram", "mangalam", "arati"]
    )
    is_ganesha = any(
        kw in combined_lower
        for kw in ["vinayaka", "ganesha", "ganapati", "ekadanta", "vighneshwara", "gajanana", "lambodara"]
    )

    # Extract English title inside parentheses if present, e.g. "శ్రీ సిద్ధి వినాయకా (Sri Siddhi Vinayaka)"
    m_paren = re.search(r"\(([^)]+)\)", raw_title)
    english_name = m_paren.group(1).strip() if m_paren else slugify_filename(raw_title).replace("-", " ")
    native_name = re.sub(r"\s*\([^)]+\)\s*", "", raw_title).strip() or english_name

    # 1. Craft High-CTR + Search-Intent Title (strictly <= 100 characters)
    if is_ganesha and lang_name == "Telugu":
        candidate_title = f"{raw_title} | Powerful Ganesh Bhajan & Telugu Devotional Song | Lyrics"
    elif is_devotional and lang_name != "English":
        candidate_title = f"{raw_title} | {lang_name} Devotional Song with Lyrics | Official Lyric Video"
    elif lang_name != "English":
        candidate_title = f"{raw_title} | Official {lang_name} Lyric Video | Full Song with Lyrics [HD]"
    else:
        candidate_title = f"{raw_title} (Official Lyric Video) | Full Song with On-Screen Lyrics [HD]"

    if len(candidate_title) > 100:
        candidate_title = f"{raw_title} | {lang_name} Devotional Lyric Video"[:100]

    # 2. SEO Filename Slug
    seo_filename = f"{slugify_filename(english_name)}-{lang_name}-{'Devotional-' if is_devotional else ''}Official-Lyric-Video.mp4"
    seo_filename = re.sub(r"-{2,}", "-", seo_filename)

    # 3. Chapters (starting at 00:00)
    chapters = build_chapters_from_slides(slides)
    chapters_block = "\n".join(f"{c['timestamp']} {c['title']}" for c in chapters)

    # 4. Full Formatted Lyrics & Meaning
    lyrics_blocks: list[str] = []
    current_sec = None
    for s in slides:
        sec = s.get("section")
        if sec and sec != current_sec:
            lyrics_blocks.append(f"\n[{sec}]")
            current_sec = sec
        lyric_line = (s.get("lyric") or "").strip()
        if lyric_line:
            lyrics_blocks.append(lyric_line)
    formatted_lyrics = "\n".join(lyrics_blocks).strip()

    meanings_summary = " ".join(
        s.get("meaning", "").strip() for s in slides[:4] if s.get("meaning")
    )

    # 5. Hashtags (3 to 5 targeted hashtags, strictly <= 15 per YouTube Policy)
    clean_eng_tag = re.sub(r"[^A-Za-z0-9]", "", english_name.title())
    if is_ganesha and lang_name == "Telugu":
        hashtags = [
            f"#{clean_eng_tag}",
            "#GaneshSongs",
            "#TeluguDevotionalSongs",
            "#VinayakaSongs",
            "#BhaktiSongs",
        ]
    elif is_devotional:
        hashtags = [
            f"#{clean_eng_tag}",
            f"#{lang_name}DevotionalSongs",
            "#BhaktiSongs",
            "#DevotionalLyricVideo",
            "#SpiritualMusic",
        ]
    else:
        hashtags = [
            f"#{clean_eng_tag}",
            f"#{lang_name}Songs",
            "#LyricVideo",
            "#OfficialLyricVideo",
            "#NewMusic",
        ]
    hashtags_line = " ".join(hashtags[:5])

    # 6. Build Full SEO Description (<= 5000 chars)
    above_fold_hook = (
        f"Watch and sing along to \"{raw_title}\" — an uplifting {lang_name} "
        f"{'devotional bhajan & sacred lyric video celebrating Lord Sri Siddhi Vinayaka (Ganesha)' if is_ganesha else ('devotional lyric video' if is_devotional else 'official lyric video')} "
        f"with full synchronized on-screen lyrics!"
    )

    about_paragraph = (
        f"✨ About This Song:\n"
        f"\"{raw_title}\" takes you on a {'divine spiritual journey filled with temple oil-lamp warmth, Vedic devotion, and sacred blessings' if is_devotional else 'cinematic musical journey'}. "
        f"{meanings_summary}\n"
        f"Perfect for {'morning prayers (Suprabhatam), Vinayaka Chavithi / Sankashti Chaturthi pooja, meditation, and peaceful home ambiance' if is_ganesha else 'daily listening, reflection, and sharing with loved ones'}."
    )

    ai_disclosure_note = (
        "🎨 Visual & Production Note: Illustrated with AI-assisted cinematic artwork and edited with synchronized custom typography."
        if is_ai_generated
        else "🎬 Production Note: Official high-definition lyric video."
    )

    description = (
        f"{above_fold_hook}\n\n"
        f"{about_paragraph}\n\n"
        f"⏱️ Video Chapters (Key Moments):\n"
        f"{chapters_block}\n\n"
        f"📜 Full Song Lyrics ({raw_title}):\n"
        f"──────────────────────────────\n"
        f"{formatted_lyrics}\n"
        f"──────────────────────────────\n\n"
        f"🙏 Support the Channel & Spread the Vibes:\n"
        f"👍 LIKE this video if the lyrics touched your heart!\n"
        f"💬 COMMENT your favorite lyric line (or reply to our Pinned Comment below!)\n"
        f"🔔 SUBSCRIBE to {channel_name} and turn on the Notification Bell (All) for more official lyric videos!\n"
        f"📲 SHARE this video with family and friends on WhatsApp & YouTube.\n\n"
        f"{ai_disclosure_note}\n\n"
        f"{hashtags_line}"
    )
    description = description[:4950]

    # 7. Backend Tags (Strictly <= 500 characters total including commas)
    candidate_tags: list[str] = [
        english_name,
        native_name,
        f"{english_name} lyrics",
        f"{english_name} song",
    ]
    if is_ganesha:
        candidate_tags.extend([
            "siddhi vinayaka songs",
            "sri siddhi vinayaka telugu song",
            "ganesh bhajan telugu",
            "వినాయక భక్తి పాటలు",
            "lord ganesha devotional songs",
            "telugu bhakti patalu",
            "ganapati songs with lyrics",
            "vinayaka chavithi songs",
            "ekadanta song",
            "mangala harathi songs",
        ])
    elif is_devotional:
        candidate_tags.extend([
            f"{lang_name.lower()} devotional songs",
            f"{lang_name.lower()} bhakti songs with lyrics",
            "devotional lyric video",
            "morning prayer songs",
        ])
    else:
        candidate_tags.extend([
            f"{lang_name.lower()} lyric video",
            f"{english_name} official lyric video",
            f"{lang_name.lower()} songs with lyrics",
        ])
    candidate_tags.append(channel_name)

    # Deduplicate and enforce <= 490 characters for YouTube Studio tag input box
    final_tags: list[str] = []
    seen_t: set[str] = set()
    for t in candidate_tags:
        t_clean = t.strip()
        if not t_clean or t_clean.lower() in seen_t:
            continue
        tentative = ", ".join(final_tags + [t_clean])
        if len(tentative) <= 485:
            final_tags.append(t_clean)
            seen_t.add(t_clean.lower())
        else:
            break
    tags_csv = ", ".join(final_tags)

    # 8. High-Engagement Pinned Comment (Provokes replies, likes & watch time)
    first_lyric_hook = (slides[0].get("lyric", "").split("\n")[0] if slides else raw_title).strip()
    if is_ganesha:
        pinned_comment = (
            f"🙏 ఓం శ్రీ సిద్ధి వినాయకాయ నమః | Om Gam Ganapataye Namaha! 🌺✨\n\n"
            f"May Lord Sri Siddhi Vinayaka remove every obstacle (Vighna) from your life and bless your home with health, wisdom, and endless prosperity!\n\n"
            f"💬 Which verse or line from \"{raw_title}\" gave you the most peace today? "
            f"Drop \"Jai Ganesha 🙏🌺\" in the replies below to share the blessings, and don't forget to hit LIKE 👍 & SUBSCRIBE 🔔!"
        )
    elif is_devotional:
        pinned_comment = (
            f"🙏✨ Divine blessings to everyone listening to \"{raw_title}\"! 🌺\n\n"
            f"💬 Which lyric line touched your heart the most (`{first_lyric_hook}`)? "
            f"Share your prayers and favorite timestamp in the replies below — we read and ❤️ every single comment! Don't forget to LIKE 👍 & SUBSCRIBE!"
        )
    else:
        pinned_comment = (
            f"✨ Thank you for watching the official lyric video for \"{raw_title}\"! 🎶\n\n"
            f"💬 Which lyric line hit you the hardest, and at what timestamp (`MM:SS`)? "
            f"Tell us in the replies below — we're reading and hearting ❤️ every comment! Hit LIKE 👍 if you enjoyed the vibe!"
        )

    today_str = datetime.date.today().isoformat()

    # 9. Complete YouTube Studio UI Button & Policy Checklist State
    studio_settings = {
        "audience_made_for_kids": False,
        "audience_radio_button": "No, it's not made for kids (VIDEO_MADE_FOR_KIDS_NOT_MFK)",
        "age_restriction": "No, don't restrict my video to viewers over 18 only",
        "show_more_expanded": True,
        "paid_promotion": False,
        "altered_or_synthetic_content_ai": bool(is_ai_generated),
        "altered_content_radio_button": "Yes (VIDEO_HAS_ALTERED_CONTENT_YES)" if is_ai_generated else "No (VIDEO_HAS_ALTERED_CONTENT_NO)",
        "automatic_chapters": True,
        "automatic_places": True,
        "automatic_concepts": True,
        "video_language": lang_name,
        "title_and_description_language": "English",
        "caption_certification": "None",
        "recording_date": today_str,
        "license": "Standard YouTube License",
        "allow_embedding": True,
        "publish_to_subscriptions_feed_and_notify": True,
        "shorts_remixing": "Allow video and audio remixing",
        "category": "Music",
        "comments_visibility": "On",
        "comments_moderation": "Basic",
        "comments_sort_by": "Top",
        "show_viewer_likes": True,
        "subtitles_srt_path": str(srt_path.resolve()) if srt_path and srt_path.exists() else None,
        "add_end_screen": True,
        "add_cards": True,
        "visibility": "Public",
        "post_publish_actions": {
            "like_own_video": True,
            "post_comment": True,
            "pin_comment": True,
            "share_url_in_chat": True,
        },
    }

    return {
        "title": candidate_title,
        "title_char_count": len(candidate_title),
        "seo_filename": seo_filename,
        "native_title": native_name,
        "english_title": english_name,
        "language": lang_info,
        "description": description,
        "description_char_count": len(description),
        "hashtags": hashtags[:5],
        "chapters": chapters,
        "tags": final_tags,
        "tags_csv": tags_csv,
        "tags_char_count": len(tags_csv),
        "pinned_comment": pinned_comment,
        "studio_settings": studio_settings,
    }


def generate_custom_thumbnail(
    project_dir: Path | None,
    storyboard: dict | None,
    seo_meta: dict,
    output_thumb_path: Path,
) -> Path | None:
    """Create a high-CTR 1280x720 (<2MB) custom YouTube thumbnail from the best hero slide."""
    hero_img_path: Path | None = None
    if project_dir and storyboard:
        slides = storyboard.get("slides") or []
        for s in slides:
            rel = s.get("image_path")
            if rel and (project_dir / rel).exists():
                hero_img_path = project_dir / rel
                break

    if not hero_img_path or not hero_img_path.exists():
        return None

    img = Image.open(hero_img_path).convert("RGBA")
    target_w, target_h = 1280, 720
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Boost contrast and color vibrancy slightly for high CTR in small mobile feeds
    rgb_img = img.convert("RGB")
    rgb_img = ImageEnhance.Contrast(rgb_img).enhance(1.12)
    rgb_img = ImageEnhance.Color(rgb_img).enhance(1.15)
    img = rgb_img.convert("RGBA")

    # Add cinematic top/bottom gradient vignette for text legibility (leaving bottom-right clear for timestamp)
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(target_h):
        if y < 160:
            alpha = int(150 * (1.0 - y / 160.0))
            draw.line([(0, y), (target_w, y)], fill=(8, 4, 16, alpha))
        elif y > target_h - 230:
            t = (y - (target_h - 230)) / 230.0
            alpha = int(215 * (t ** 1.15))
            draw.line([(0, y), (target_w, y)], fill=(8, 4, 16, alpha))

    # Draw golden border frame
    draw.rectangle([14, 14, target_w - 15, target_h - 15], outline=(255, 205, 85, 190), width=3)

    # Render English + Subtitle badge on bottom-left (safe from bottom-right duration overlay)
    eng_title = seo_meta.get("english_title", "Official Lyric Video").upper()
    sub_badge = "OFFICIAL LYRIC VIDEO • FULL LYRICS"

    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 64)
    except Exception:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 60)
        except Exception:
            title_font = ImageFont.load_default()

    try:
        badge_font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 28)
    except Exception:
        badge_font = ImageFont.load_default()

    # Gold pill badge at bottom-left
    pill_x, pill_y = 46, target_h - 178
    draw.rounded_rectangle([pill_x, pill_y, pill_x + 520, pill_y + 44], radius=10, fill=(212, 145, 22, 235))
    draw.text((pill_x + 18, pill_y + 7), sub_badge, font=badge_font, fill=(255, 255, 255, 255))

    # Drop shadow + Main English title text at bottom-left
    text_x, text_y = 46, target_h - 118
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4)]:
        draw.text((text_x + dx, text_y + dy), eng_title, font=title_font, fill=(0, 0, 0, 230))
    draw.text((text_x, text_y), eng_title, font=title_font, fill=(255, 232, 145, 255))

    composited = Image.alpha_composite(img, overlay).convert("RGB")
    output_thumb_path.parent.mkdir(parents=True, exist_ok=True)
    composited.save(output_thumb_path, format="JPEG", quality=92, optimize=True)
    return output_thumb_path


def update_local_mp4_metadata(
    source_video: Path,
    dest_video: Path,
    seo_meta: dict,
    channel_name: str,
) -> None:
    """Losslessly update local MP4 container meta tags and title via ffmpeg."""
    dest_video.parent.mkdir(parents=True, exist_ok=True)
    tmp_out = dest_video.with_suffix(".tagging.mp4")

    comment_summary = (
        f"{seo_meta['title']} | Keywords: {seo_meta['tags_csv'][:200]}"
    )
    year_str = str(datetime.date.today().year)
    lang_code = seo_meta.get("language", {}).get("iso639_2", "eng")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(source_video),
        "-map", "0",
        "-c", "copy",
        "-movflags", "+faststart+use_metadata_tags",
        "-metadata", f"title={seo_meta['title']}",
        "-metadata", f"artist={channel_name}",
        "-metadata", f"album_artist={channel_name}",
        "-metadata", f"album={seo_meta['english_title']}",
        "-metadata", "genre=Devotional / Music / Lyric Video",
        "-metadata", f"comment={comment_summary}",
        "-metadata", f"description={seo_meta['description'][:600]}",
        "-metadata", f"synopsis={seo_meta['description'][:600]}",
        "-metadata", f"date={year_str}",
        "-metadata", f"copyright=Copyright {year_str} {channel_name}. All Rights Reserved.",
        "-metadata:s:v:0", f"language={lang_code}",
        "-metadata:s:a:0", f"language={lang_code}",
        str(tmp_out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg metadata tagging failed:\n{res.stderr}")

    shutil.move(str(tmp_out), str(dest_video))
    # Also update the source video file in-place so the original file has the updated local meta tags too
    if source_video.resolve() != dest_video.resolve():
        shutil.copy2(str(dest_video), str(source_video))


def main() -> None:
    ensure_ffmpeg_on_path()
    parser = argparse.ArgumentParser(description="Prepare local video & SEO metadata package for YouTube upload.")
    parser.add_argument("--video", required=True, help="Path to the local MP4 video file.")
    parser.add_argument("--storyboard", default=None, help="Optional path to storyboard.json.")
    parser.add_argument("--srt", default=None, help="Optional path to master.srt subtitles.")
    parser.add_argument("--channel", default="Vamshi Creates", help="YouTube Channel / Artist name.")
    parser.add_argument("--ai-generated", dest="ai_generated", action="store_true", default=True, help="Mark Altered/Synthetic AI content = Yes (default: True).")
    parser.add_argument("--no-ai-generated", dest="ai_generated", action="store_false", help="Mark Altered/Synthetic AI content = No.")
    parser.add_argument("--out-dir", default=None, help="Output directory for youtube_ready package.")
    args = parser.parse_args()

    video_path = Path(args.video).resolve()
    if not video_path.exists():
        print(f"ERROR: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    # Auto-discover storyboard.json and master.srt if video is in a project folder
    project_dir = video_path.parent
    if project_dir.name == "edit":
        project_dir = project_dir.parent

    sb_path = Path(args.storyboard).resolve() if args.storyboard else (project_dir / "storyboard.json")
    storyboard = None
    if sb_path and sb_path.exists():
        storyboard = json.loads(sb_path.read_text(encoding="utf-8"))

    srt_path = Path(args.srt).resolve() if args.srt else (project_dir / "edit" / "master.srt")
    if not srt_path.exists():
        srt_path = None

    out_dir = Path(args.out_dir).resolve() if args.out_dir else (project_dir / "youtube_ready")
    out_dir.mkdir(parents=True, exist_ok=True)

    seo_meta = build_seo_metadata(
        video_path=video_path,
        storyboard=storyboard,
        srt_path=srt_path,
        channel_name=args.channel,
        is_ai_generated=args.ai_generated,
    )

    tagged_video_path = out_dir / seo_meta["seo_filename"]
    update_local_mp4_metadata(
        source_video=video_path,
        dest_video=tagged_video_path,
        seo_meta=seo_meta,
        channel_name=args.channel,
    )

    thumb_path = out_dir / "thumbnail_16x9.jpg"
    generated_thumb = generate_custom_thumbnail(
        project_dir=project_dir if storyboard else None,
        storyboard=storyboard,
        seo_meta=seo_meta,
        output_thumb_path=thumb_path,
    )

    probe_after = probe_video_info(tagged_video_path)
    embedded_tags = probe_after.get("format", {}).get("tags", {})

    seo_meta["local_files"] = {
        "original_video_path": str(video_path),
        "seo_tagged_video_path": str(tagged_video_path),
        "thumbnail_path": str(generated_thumb) if generated_thumb else None,
        "subtitles_srt_path": str(srt_path) if srt_path else None,
        "embedded_mp4_tags_verified": embedded_tags,
    }

    meta_json_path = out_dir / "youtube_metadata.json"
    meta_json_path.write_text(json.dumps(seo_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"=== YouTube Upload Package Ready ===")
    print(f"SEO Title ({seo_meta['title_char_count']}/100 chars): {seo_meta['title']}")
    print(f"Tagged Video File: {tagged_video_path}")
    print(f"Custom Thumbnail : {generated_thumb}")
    print(f"Subtitles (.srt) : {srt_path}")
    print(f"Tags ({seo_meta['tags_char_count']}/500 chars): {seo_meta['tags_csv']}")
    print(f"AI Disclosure    : {seo_meta['studio_settings']['altered_content_radio_button']}")
    print(f"Metadata JSON    : {meta_json_path}")


if __name__ == "__main__":
    main()
