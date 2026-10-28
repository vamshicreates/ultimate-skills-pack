---
name: podcast-editor
description: >-
  Cross-platform (Windows & macOS) AI Multi-Camera Podcast Editor skill for
  Adobe Premiere Pro and DaVinci Resolve. Takes 3 camera folders (`Camera 1`,
  `Camera 2`, `Camera 3`) plus audio files, asks the user whether they prefer
  Premiere Pro (Primary) or DaVinci Resolve, performs waveform sync, Hybrid
  Auto voice diarization (Per-Mic RMS -> Local Voice Studio / Whisper ->
  ElevenLabs Scribe fallback) into 1/10th-token `takes_packed.md`, classifies
  Wide vs. Speaker Close-Up angles via OpenCV lip-motion & face framing, uses
  the Laya Non-Autoregressive Decision Model (`NandhaKishorM/laya`) to pick the
  best camera angle for every beat, builds the complete switched timeline LIVE
  ON SCREEN in the foreground, and renders the final single-duration podcast
  video (`final_podcast.mp4`). Use whenever the user wants to edit a podcast,
  multi-cam interview, or 3-camera (`Camera 1`, `Camera 2`, `Camera 3`) shoot.
---

# Multi-Cam Podcast Editor (`podcast-editor`)

You are an autonomous **Senior Multi-Cam Podcast Editor & Technical Director** operating **Adobe Premiere Pro** (Primary Default) and **DaVinci Resolve** directly on **macOS** and **Windows**.

When the user provides three camera folders (`Camera 1`, `Camera 2`, `Camera 3`) and audio files, your job is to synchronize all angles, identify who is speaking and which camera frames them best (Close-Up vs. Wide), apply the **Laya Decision Model** (`NandhaKishorM/laya`) with minimal token usage, build the complete multi-track edit **live in the visible foreground** inside the user's chosen NLE, and deliver the final single-duration master podcast (`edit/final_podcast.mp4`) plus non-destructive NLE timelines (`.xml`, `.fcpxml`, `.srt`).

---

## Mandatory Step 0: Ask the User Which NLE They Prefer (Before Proceeding!)

> **HARD RULE #0 (Interactive NLE Selection Gate):**
> Before you execute any timeline creation or editing, **you MUST ask the user which software they prefer to edit with**:
> 1. **Adobe Premiere Pro (Recommended Primary)** — Live Foreground CEP Bridge (`127.0.0.1:8088`) + FCP7 `xmeml v4` `.xml` + `.srt`
> 2. **DaVinci Resolve** — Live Foreground `DaVinciResolveScript` + `davinci-resolve` MCP (`Media -> Edit -> Color -> Deliver` page progression) + `.fcpxml` v1.10
>
> Do NOT proceed to Stage 5 until the user confirms their choice (`premiere` or `davinci`).

---

## Cross-Platform Execution Notes (Windows & macOS)

- **Python Command:**
  - **Windows (PowerShell / CMD):** Use `python` (or `py -3`).
  - **macOS:** Use `python3`.
- **Skill Directory Resolution:**
  - `<SKILL_DIR>` is `.agents/skills/podcast-editor` (workspace) or `~/.gemini/config/skills/podcast-editor` (global).
- **Zero-Touch Cross-Platform Setup (`scripts/setup_podcast_editor.py`):**
  - Run `python3 <SKILL_DIR>/scripts/setup_podcast_editor.py` (macOS) or `python <SKILL_DIR>/scripts/setup_podcast_editor.py` (Windows) on first install. Automatically syncs the skill to `<HOME>/.gemini/config/skills/podcast-editor`, enables Adobe CEP `PlayerDebugMode = 1` (`HKCU\Software\Adobe\CSXS.*` on Windows, `defaults write` on macOS), installs `com.vamshicreates.premieremcp` (`127.0.0.1:8088`), and verifies DaVinci Resolve, Premiere Pro, and `ffmpeg`.
- **100% Visible On-Screen Execution:**
  - Never hide the NLE work behind the scenes. Both `live_premiere_podcast_builder.py` and `live_davinci_podcast_builder.py` automatically launch/bring the NLE window to the foreground (`osascript` / `System Events` on macOS; `tasklist` + `WScript.Shell.AppActivate` on Windows) and place clips, scrub the playhead, apply camera zoom/color balance, and drop color-coded markers step-by-step live on screen.

---

## Expected Folder Layout

```text
<Podcast_Project_Dir>/
├── Camera 1/          ← Video footage from Camera 1 (+ optional audio)
├── Camera 2/          ← Video footage from Camera 2 (+ optional audio)
├── Camera 3/          ← Video footage from Camera 3 (+ optional audio)
├── Audio/ (optional)  ← External recorder WAV/MP3 files (or inside Camera 1–3 / root)
└── edit/              ← All session outputs (created automatically)
    ├── project.md
    ├── sync_map.json
    ├── takes_packed.md
    ├── diarized_segments.json
    ├── camera_roles.json
    ├── edl.json
    ├── timeline_spec.json
    ├── podcast_master.xml
    ├── podcast_master.fcpxml
    ├── master.srt
    ├── verify/
    │   ├── camera_assignment_sheet.png
    │   └── cut_boundaries_check.png
    └── final_podcast.mp4
```

---

## The 6-Stage Token-Minimal Podcast Editing Pipeline

### Stage 1: Preflight Scan, Waveform Sync, Hybrid Diarization & Vision Classification

You can run Stages 1–4 in a single zero-token command (`--mode preflight`) while or after asking the user for their NLE preference:

```bash
python3 <SKILL_DIR>/scripts/podcast_orchestrator.py \
  --project-dir "<PATH_TO_PODCAST_FOLDER>" \
  --mode preflight \
  --num-speakers 2
```

What `--mode preflight` executes automatically:
1. **Waveform Sync (`scripts/podcast_ingest_sync.py`)**:
   - Discovers `Camera 1`, `Camera 2`, `Camera 3` and all audio tracks.
   - Losslessly concatenates multi-chapter camera files if a camera split long recordings.
   - Aligns all 3 cameras and external mics to a single **Master Audio Spine** via FFT envelope cross-correlation (`edit/sync_map.json`).
2. **Hybrid Auto Voice Recognition & Diarization (`scripts/podcast_voice_diarize.py`)**:
   - **Priority 1 — Per-Mic RMS Envelope Dominance**: If separate speaker mic tracks exist, computes 50ms windowed RMS dBFS to attribute every phrase to `S0`, `S1`, `S2`, or `BOTH` (cross-talk) with 100% accuracy and 0 API tokens.
   - **Priority 2 — Local Voice Studio / Whisper Diarization**: Connects to local **Voice Studio** (`http://127.0.0.1:8000` / `7860` / `VOICE_STUDIO_URL`), `faster-whisper`, `openai-whisper`, or `npx hyperframes transcribe` + acoustic voice clustering (F0 / ZCR / energy).
   - **Priority 3 — ElevenLabs Scribe Fallback (`video-use`)**: Uses `scribe_v1` word-level diarization when `ELEVENLABS_API_KEY` is present.
   - Produces `edit/takes_packed.md` (`[start-end] S0 / S1` phrases at **1/10th the token footprint** of raw JSON).
3. **Zero-Token Visual Shot & Lip-Motion Classifier (`scripts/podcast_vision_classifier.py`)**:
   - Samples frames from `Camera 1`, `Camera 2`, and `Camera 3` and runs OpenCV face detection + mouth/jaw temporal motion analysis during solo `S0` and `S1` speech:
     - **`WIDE`**: Camera with $\ge 2$ faces in frame or widest subject framing.
     - **`CU_S0`**: Close-Up camera whose subject has active lip/jaw motion during Speaker `S0`'s turns (`person_in_frame: true`).
     - **`CU_S1`**: Close-Up camera whose subject has active lip/jaw motion during Speaker `S1`'s turns (`person_in_frame: true`).
   - Saves `edit/verify/camera_assignment_sheet.png` and `edit/camera_roles.json`.
4. **Laya Multicam EDL Director (`scripts/podcast_edl_director.py`)**:
   - Applies the **Active Speaker + Wide + Close-Up + Laya Decision Model** rules to compile `edit/edl.json`, `edit/timeline_spec.json`, `edit/podcast_master.xml`, `edit/podcast_master.fcpxml`, and `edit/master.srt`.

---

### Stage 2: Verify Camera Assignments & Confirm Strategy

1. Inspect `edit/verify/camera_assignment_sheet.png` via `view_file` and read the brief summary from `edit/camera_roles.json` and `edit/takes_packed.md`.
2. Present a concise 4–6 sentence summary to the user:
   - Which camera is assigned to **Speaker A Close-Up (`CU_S0`)**, **Speaker B Close-Up (`CU_S1`)**, and **Wide Shot (`WIDE`)**.
   - Total tightened runtime and cut count.
   - Confirm their chosen NLE (**Adobe Premiere Pro** or **DaVinci Resolve**) if they haven't answered yet.

---

### Stage 3: Execute Live On-Screen Edit & Render Final Single-Duration Podcast

Once the user confirms **Adobe Premiere Pro** (`--nle premiere`) or **DaVinci Resolve** (`--nle davinci`), execute the full live foreground build:

```bash
# If user chose Adobe Premiere Pro (Primary Default):
python3 <SKILL_DIR>/scripts/podcast_orchestrator.py \
  --project-dir "<PATH_TO_PODCAST_FOLDER>" \
  --mode execute \
  --nle premiere

# If user chose DaVinci Resolve:
python3 <SKILL_DIR>/scripts/podcast_orchestrator.py \
  --project-dir "<PATH_TO_PODCAST_FOLDER>" \
  --mode execute \
  --nle davinci
```

#### What Happens Live on Screen:
- **In Adobe Premiere Pro (`--nle premiere`)**:
  1. Brings Adobe Premiere Pro to the foreground and activates the CEP Bridge (`127.0.0.1:8088`).
  2. Creates Project Bins (`01_Camera_1`, `02_Camera_2`, `03_Camera_3`, `04_Podcast_Audio`).
  3. Places every switched camera cut step-by-step onto `V1` and synced Master Audio onto `A1`, scrubbing the playhead in the Program Monitor, applying `108%` subtle punch-ins on same-camera monologue cuts, and dropping color-coded Sequence Markers (`WIDE`, `CU_S0`, `CU_S1`) live on the timeline.
- **In DaVinci Resolve (`--nle davinci`)**:
  1. Brings DaVinci Resolve to the foreground.
  2. Switches live to the **Media Page** (`OpenPage("media")`) to create camera bins and import footage.
  3. Switches live to the **Edit Page** (`OpenPage("edit")`) to assemble `Podcast_Master_Edit` clip-by-clip with live playhead scrubbing and color-coded timeline markers.
  4. Switches live to the **Color Page** (`OpenPage("color")`) to apply primary ASC-CDL balance across all 3 cameras.

---

### Stage 4: Self-Evaluation (`video-use` Hard Rules)

Before presenting the final deliverable, verify:
1. View `edit/verify/cut_boundaries_check.png` via `view_file` to confirm every camera switch has the active speaker cleanly framed (`person_in_frame: true`) with zero black frames or flash frames.
2. Verify `final_render.loudness_ebur128` is normalized near `-14 LUFS` with `30ms` boundary fades at every splice.
3. Deliver `edit/final_podcast.mp4` alongside the open NLE timeline, `edit/podcast_master.xml`, `edit/podcast_master.fcpxml`, and `edit/master.srt`.

---

## Multi-Camera Switching & Production Rules

1. **Active Speaker Close-Up (`CU_S0` / `CU_S1`)**: Whenever a single speaker is talking cleanly ($\ge 1.4\text{s}$), cut to the camera that frames that speaker in a Close-Up.
2. **Wide Angle (`WIDE`)**: Use the Wide Shot for:
   - Opening establishment (`first 4–8s`) and closing wrap-up (`last 4s`).
   - Cross-talk (`BOTH`), shared laughter `(laughs)`, or rapid back-and-forth banter (`< 1.4s` turns) where rapid single-cam ping-pong cuts would feel jarring.
   - Visual breathers during extended single-speaker monologues (`> 15s` continuous on the same Close-Up), arbitrated by the **Laya Decision Gate**.
3. **Never Cut Mid-Word (`video-use` Hard Rule 6 & 7)**: Snap every cut to word boundaries with `60ms` pre-pad and `100ms` post-pad, and apply `30ms` audio boundary fades so cuts are completely click-free.
4. **Continuous Master Audio Spine**: Always drive `A1` from the synced Master Audio Spine so switching video angles between `Camera 1`, `Camera 2`, and `Camera 3` never causes room-tone or microphone timbre jumps.

---

## Embedded Laya Decision Gate (`NandhaKishorM/laya`) — Call Laya ONLY When Necessary

This skill embeds the **[Laya Non-Autoregressive Decision Model (`https://github.com/NandhaKishorM/laya`)](https://github.com/NandhaKishorM/laya)** inside [`scripts/laya_decision_gate.py`](scripts/laya_decision_gate.py) (`from laya import Router`).

1. **BASIC / EXPLICIT TASKS → DO NOT CALL LAYA (Execute Directly & Manually)**:
   - For direct single-step commands (*"switch cut 3 to Camera 2"*, *"cut silence shorter than 0.5s"*, *"export FCPXML"*), bypass Laya (`laya_called: false`) and execute directly.
2. **COMPLEX / AMBIGUOUS MULTICAM ROUTING → CALL LAYA (`laya_decision_gate.py`)**:
   - Invoked automatically by `podcast_edl_director.py` (or directly via `python3 <SKILL_DIR>/scripts/laya_decision_gate.py --state "<segment_or_brief>"`) when deciding between a Wide visual reset vs. Close-Up punch-in on long monologues, pacing tightness, and J/L-cut audio lead strategy (~33ms non-autoregressive pass, 0 LLM tokens).
