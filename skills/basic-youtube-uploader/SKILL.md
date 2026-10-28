---
name: basic-youtube-uploader
description: >-
  Simple, fast, and effective YouTube video uploader via browser automation (Chrome DevTools or
  ChatGPT internal browser fallback). Trigger this skill whenever the user asks to upload a video
  from the local folder (`uploads/` or workspace) to their YouTube channel as Unlisted or wants a
  quick, direct upload. Identifies the local video file, opens YouTube Studio in Chrome (or the
  ChatGPT internal browser if Chrome cannot be opened), uploads the video file directly, writes a
  clean Title and Description, sets visibility to Unlisted, saves the video, and returns the
  Unlisted YouTube link.
---

# Basic YouTube Uploader (`basic-youtube-uploader`)

Upload a local video file directly to the user's YouTube channel as **Unlisted** using browser access (`chrome-devtools`, or the **ChatGPT internal browser** if Chrome cannot be opened). Execute these **4 simple steps** effectively without unnecessary overhead—do **not** run audio transcription, ffmpeg re-encoding, thumbnail generation, tags, subtitles, end screens, cards, or post-publish comments unless explicitly requested by the user.

---

## 4-Step Workflow

### Step 1: Identify the Local Video File & Prepare Title + Description
Run the lightweight finder script [find_local_video.py](./scripts/find_local_video.py) to locate the target video in `uploads/` (or the workspace folder) and generate a clean default Title and Description:
```bash
python3 .agents/skills/basic-youtube-uploader/scripts/find_local_video.py
```
- If the user specified a particular file or folder, pass `--path <path/to/video.mp4>`.
- If the user provided a custom title or description in chat, use their text; otherwise, use the clean title (`<= 100` chars) and description derived from the video filename/context.

---

### Step 2: Open YouTube Studio & Upload the Video File Directly (Chrome or ChatGPT Internal Browser Fallback)
1. **Browser Selection & Fallback**:
   - First attempt to open or connect to Chrome via `chrome-devtools` (`list_pages` / `navigate_page`).
   - **Fallback**: If the agent is unable to open or connect to the external Chrome browser (e.g., Chrome is unavailable, locked, or fails to launch), **immediately fall back to the ChatGPT internal browser** (built-in agent browser tool) and perform the exact same YouTube Studio steps there.
2. Navigate to `https://studio.youtube.com` and inspect the page (`take_snapshot` or browser view).
   - *If not signed in*: Ask the user to sign in to their Google/YouTube account in the open browser window and wait for confirmation.
3. Click **`"Create"`** (top-right header button) -> click **`"Upload videos"`** (or click the dashboard `"Upload videos"` button directly).
4. Attach/upload the exact local `video_path` using the browser's file upload action on the `"Select files"` button (or `<input type="file">`).
5. Wait for the **Details** upload dialog (`ytcp-uploads-dialog`) to appear.

---

### Step 3: Write Title & Description (`Details` Tab)
On the **Details** tab (`take_snapshot`):
1. **Title**: Fill the Title textbox (`textbox "Add a title that describes your video..."` / `#title-textarea`) with the video **Title** (`<= 100` characters).
2. **Description**: Fill the Description textbox (`textbox "Tell viewers about your video..."` / `#description-textarea`) with the video **Description**.
3. **Audience (Required by YouTube to proceed)**: Ensure **`"No, it's not made for kids"`** (`radio "No, it's not made for kids"` / `VIDEO_MADE_FOR_KIDS_NOT_MFK`) is selected so YouTube Studio enables saving.
   - *Skip thumbnails, playlists, "Show more", tags, subtitles, end screens, and cards.*

---

### Step 4: Set Visibility to `Unlisted` & Save (`Visibility` Tab)
1. Jump directly to the **Visibility** step:
   - Either click the **`"Visibility"`** step button in the top stepper of the modal, OR click **`"Next"`** (`#next-button`) 3 times (`Details` -> `Video elements` -> `Checks` -> `Visibility`).
2. Under **Save or publish**, select the **`"Unlisted"`** radio button (`radio "Unlisted"` / `tp-yt-paper-radio-button[name="UNLISTED"]`).
3. Verify via `take_snapshot` that **`"Unlisted"`** is checked (`checked`) and copy the **Video link** (`https://youtu.be/<VIDEO_ID>`) shown in the right-hand video info card.
4. Click **`"Save"`** (`#done-button`).
5. Wait until the upload finishes transferring and the confirmation dialog appears (if the file is still uploading, wait for `"Video published"` / `"Video saved"` or `"Upload complete"` before closing).
6. Record the upload in `uploads/upload_history.json`:
   ```bash
   python3 .agents/skills/basic-youtube-uploader/scripts/find_local_video.py \
     --record "<video_path>" \
     --url "https://youtu.be/<VIDEO_ID>" \
     --title "<Title>"
   ```
7. Share the **Unlisted YouTube Link** (`https://youtu.be/<VIDEO_ID>`), **Title**, and **Description** with the user in chat.

---

## Reference
- Detailed selector & browser interaction notes: [youtube_studio_ui_runbook.md](./references/youtube_studio_ui_runbook.md)
