# Basic YouTube Uploader (`basic-youtube-uploader`)

A simple, fast, and effective AI Agent Skill that identifies a video file in the local folder (`uploads/` or workspace), opens **YouTube Studio (`https://studio.youtube.com`)** via browser automation (using **Chrome** or automatically falling back to the **ChatGPT internal browser** if Chrome cannot be opened), uploads the video directly, writes a clean **Title** and **Description**, sets visibility to **Unlisted**, saves it, and returns the Unlisted YouTube link.

---

## ✨ What It Does (4 Simple Steps)

1. **Identifies the Local Video (`scripts/find_local_video.py`)**:
   - Scans `uploads/` (or the workspace / user-specified path) for `.mp4`, `.mov`, `.mkv`, or `.webm` files.
   - Generates a clean **Title** (`<= 100` chars) and **Description** from the video filename or user context with zero re-encoding or transcription overhead.
2. **Uploads Directly via Browser (Chrome or ChatGPT Internal Browser Fallback)**:
   - Opens `https://studio.youtube.com` in Chrome (`chrome-devtools`), or automatically falls back to the **ChatGPT internal browser** if Chrome is unavailable/unable to open.
   - Clicks **Create -> Upload videos** and attaches the local video file directly.
3. **Writes Title & Description (`Details` Tab)**:
   - Fills in the **Title** and **Description**, and selects *"No, it's not made for kids"* (required by YouTube Studio to save).
4. **Keeps It Unlisted & Saves (`Visibility` Tab)**:
   - Jumps straight to **Visibility**, selects **Unlisted**, clicks **Save**, logs the upload to `uploads/upload_history.json`, and returns the `https://youtu.be/<VIDEO_ID>` link in chat.

---

## 📂 Repository Structure

```text
basic-youtube-uploader/
├── SKILL.md                                 # Main 4-Step Agent Skill instruction file
├── README.md                                # Documentation & quickstart guide
├── LICENSE                                  # MIT License
├── references/
│   └── youtube_studio_ui_runbook.md         # Browser automation runbook for YouTube Studio
└── scripts/
    └── find_local_video.py                  # Fast local video finder & upload history logger
```

---

## 🚀 Installation & Usage

### Install into Your Workspace Skills Directory
```bash
git clone https://github.com/vamshicreates/basic-youtube-uploader.git .agents/skills/basic-youtube-uploader
```

### Find the Next Local Video to Upload
```bash
python3 .agents/skills/basic-youtube-uploader/scripts/find_local_video.py
```

### Target a Specific Video File
```bash
python3 .agents/skills/basic-youtube-uploader/scripts/find_local_video.py --path uploads/my_video.mp4
```
