# YouTube Uploader & SEO View-Optimizer Skill (`youtube-uploader`)

An end-to-end AI Agent Skill for **local MP4 metadata tagging, lyric-driven YouTube SEO generation, 2026 YouTube Studio policy compliance (including AI/Altered Content disclosure), button-by-button Studio browser automation, and post-publish engagement boosting (Like + Pinned Comment)**.

---

## ✨ Key Capabilities

1. **Local Folder Watcher (`scripts/watch_folder.py`)**:
   - Monitors `uploads/` and `projects/*/final_*.mp4` (`--scan-once` or continuous `--watch` daemon).
   - Verifies file completion via `ffprobe` before triggering the preparation & upload pipeline.
2. **Pre-Upload Local MP4 Container Tagging (`scripts/prepare_video_package.py`)**:
   - Embeds `moov`/`udta` metadata atoms directly into the local `.mp4` container (`title`, `artist`, `album_artist`, `album`, `genre`, `comment`, `description`, `synopsis`, `date`, `copyright`, stream `language`, plus `+faststart` header optimization) using `ffmpeg -c copy`.
   - Renames/exports the file to a clean SEO filename slug (`<Song-Title-Language-Official-Lyric-Video>.mp4`).
3. **Lyrics- & Storyboard-Driven YouTube SEO Engine**:
   - **High-CTR Bilingual Title (`<= 100` chars)**: Combines native script + English transliteration + genre/deity keyword + format qualifier.
   - **LLM-Optimized Description (`<= 5,000` chars)**:
     - 2-line above-the-fold search snippet hook (`<= 150` chars)
     - Story & meaning of the song
     - Interactive `00:00` Timestamp Chapters (`>= 3` chapters, each `>= 10s`)
     - Full formatted song lyrics for long-tail lyric search ranking
     - Subscribe CTA + AI production transparency note
     - 3 to 5 targeted hashtags at the bottom (strictly `<= 15` per YouTube policy)
   - **Backend Tags (`<= 500` chars total)**: Exact-match titles, transliterations, common misspellings, and niche lyric hooks.
   - **Custom 16:9 High-CTR Thumbnail (`1280x720`, `< 2MB`)**: Auto-generated from the hero slide with bold title typography placed on the bottom-left (safe from YouTube's bottom-right duration badge).
4. **Full 2026 YouTube Studio Policy & UI Button Execution (`references/youtube_studio_ui_runbook.md`)**:
   - **Audience (COPPA)**: Selects **`"No, it's not made for kids"`** (`VIDEO_MADE_FOR_KIDS_NOT_MFK`) so comments, pinned comments, end screens, and notifications stay active.
   - **Expands `"Show more"`** and selects:
     - **Altered / Synthetic Content (AI Disclosure)**: **`"Yes"`** (`VIDEO_HAS_ALTERED_CONTENT_YES`) when AI visuals or synthetic vocals are used.
     - **Automatic Chapters, Places & Concepts**: All 3 enabled.
     - **Tags (`<= 500` chars)**, **Video Language**, **Recording Date**, **Standard YouTube License**, **Allow Embedding**, **Notify Subscribers**, **Shorts Remixing (`Allow video and audio remixing`)**, **Category (`Music`)**, and **Comments (`On`, Sort by `Top`)**.
   - **Video Elements**: Uploads `.srt` Subtitles (`master.srt`), adds an **End Screen** (`1 video + 1 subscribe`), and adds a midpoint **Info Card**.
   - **Checks & Visibility**: Verifies Copyright reads `"No issues found"`, sets Visibility to **`"Public"`**, and publishes.
5. **Post-Publish View-Velocity Booster**:
   - Opens the live watch page (`https://www.youtube.com/watch?v=<VIDEO_ID>`), **Likes** the video, posts a lyric-specific **engagement-provoking comment**, **Pins** the comment to the top of the comment section, and shares the live YouTube link in chat.

---

## 📂 Repository Structure

```text
youtube-uploader/
├── SKILL.md                                    # Main 10-Step Agent Skill instruction file
├── README.md                                   # Documentation & quickstart guide
├── LICENSE                                     # MIT License
├── references/
│   ├── youtube_upload_policies_2026.md         # 2026 YouTube Policies (AI Disclosure, COPPA, Spam, Tags, Copyright)
│   ├── youtube_studio_ui_runbook.md            # Button-by-button YouTube Studio browser automation runbook
│   └── youtube_seo_and_engagement_playbook.md  # SEO formulas, chapter rules, thumbnail rules & pinned comment templates
├── scripts/
│   ├── watch_folder.py                         # Local folder watcher (`--scan-once` or `--watch`)
│   ├── prepare_video_package.py                # Local MP4 metadata tagger, thumbnail generator & SEO JSON builder
│   └── youtube_studio_helper.py                # Pre-flight policy validator (`--validate`) & publish logger (`--record-publish`)
└── examples/
    └── sample_youtube_metadata.json            # Complete sample output schema
```

---

## 🚀 Installation & Usage

### Install into Your Workspace Skills Directory
```bash
git clone https://github.com/vamshicreates/youtube-uploader.git .agents/skills/youtube-uploader
```

### 1. Scan Local Folders & Prepare Any New Video
```bash
python3 .agents/skills/youtube-uploader/scripts/watch_folder.py --scan-once
```

### 2. Prepare a Specific Video + Storyboard Package
```bash
python3 .agents/skills/youtube-uploader/scripts/prepare_video_package.py \
  --video projects/<song_slug>/final_<song_slug>.mp4 \
  --storyboard projects/<song_slug>/storyboard.json \
  --channel "Vamshi Creates" \
  --ai-generated
```

### 3. Validate Policy & Character Limits Before Upload
```bash
python3 .agents/skills/youtube-uploader/scripts/youtube_studio_helper.py \
  --validate projects/<song_slug>/youtube_ready/youtube_metadata.json
```
