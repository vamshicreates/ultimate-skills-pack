# Multi-Cam Podcast Editor (`podcast-editor`)

A cross-platform (**Windows and macOS**) AI Multi-Camera Podcast Editing Skill for **Adobe Premiere Pro** (Primary Default) and **DaVinci Resolve**.

Given three camera folders (`Camera 1`, `Camera 2`, `Camera 3`) and audio files, `podcast-editor`:
1. **Asks the user which software they prefer to edit with** (**Adobe Premiere Pro** or **DaVinci Resolve**) before touching the cut.
2. **Synchronizes all 3 camera angles and external audio tracks** to a single Master Audio Spine via FFT waveform cross-correlation (`0 LLM tokens`).
3. **Identifies active speakers via Hybrid Auto Voice Diarization** (**Per-Mic RMS Envelope Dominance** $\rightarrow$ **Local Voice Studio / Whisper** $\rightarrow$ **ElevenLabs Scribe fallback**) and compresses the transcript into `edit/takes_packed.md` at **1/10th the token footprint** (`video-use`).
4. **Classifies Camera Framing & Active-Speaker Lip Motion** (`scripts/podcast_vision_classifier.py`) to bind **`WIDE`** (Two-Shot / Group), **`CU_S0`** (Speaker A Close-Up), and **`CU_S1`** (Speaker B Close-Up) while verifying `person_in_frame: true`.
5. **Applies the Embedded Laya Non-Autoregressive Decision Model (`NandhaKishorM/laya`)** (`scripts/laya_decision_gate.py`) to select the optimal camera angle for every conversational turn (Close-Up on active solo speaker, Wide on cross-talk/banter/laughter/opening/monologue breathers).
6. **Executes the entire edit LIVE ON SCREEN in the foreground** inside Adobe Premiere Pro (via the bundled `127.0.0.1:8088` CEP Bridge) or DaVinci Resolve (via `DaVinciResolveScript` across `Media -> Edit -> Color -> Deliver`), and renders the final single-duration podcast master (`edit/final_podcast.mp4`) normalized to `-14 LUFS` EBU R128 with `30ms` boundary fades.

---

## 📂 Repository Structure

```text
podcast-editor/
├── SKILL.md                                  # Complete 6-Stage Agent Skill workflow & Hard Rules
├── README.md                                 # Quickstart & architecture documentation
├── LICENSE                                   # MIT License
├── .gitignore
├── assets/
│   └── cep_extension/                        # Auto-installed Premiere Pro CEP Bridge (127.0.0.1:8088)
│       ├── CSXS/manifest.xml
│       ├── index.html
│       └── host.jsx
└── scripts/
    ├── setup_podcast_editor.py               # Cross-platform zero-touch installer (Windows & macOS)
    ├── podcast_orchestrator.py               # End-to-end CLI coordinator & NLE Selection Gate
    ├── podcast_ingest_sync.py                # Camera 1/2/3 + Audio scanner & FFT waveform sync
    ├── podcast_voice_diarize.py              # Hybrid Auto diarizer (Per-Mic RMS -> Voice Studio/Whisper -> Scribe)
    ├── podcast_vision_classifier.py          # OpenCV/PIL Wide vs. Close-Up & active-speaker lip-motion binder
    ├── laya_decision_gate.py                 # Embedded NandhaKishorM/laya Router for multicam switching
    ├── podcast_edl_director.py               # Compiles edl.json, timeline_spec.json, .xml, .fcpxml, & .srt
    ├── live_premiere_podcast_builder.py      # Live foreground Adobe Premiere Pro timeline builder
    ├── live_davinci_podcast_builder.py       # Live foreground DaVinci Resolve timeline & color builder
    └── podcast_master_renderer.py            # Single-duration master MP4 renderer (-14 LUFS) & self-eval
```

---

## 🚀 Installation (Windows & macOS)

### Option 1: Zero-Touch via Antigravity Chat
> **"Install the skill from https://github.com/vamshicreates/podcast-editor into `.agents/skills/podcast-editor` and run `scripts/setup_podcast_editor.py`."**

### Option 2: 1-Line Terminal Install
- **macOS (zsh / bash):**
  ```bash
  git clone https://github.com/vamshicreates/podcast-editor.git .agents/skills/podcast-editor && python3 .agents/skills/podcast-editor/scripts/setup_podcast_editor.py
  ```
- **Windows (PowerShell / CMD):**
  ```powershell
  git clone https://github.com/vamshicreates/podcast-editor.git .agents/skills/podcast-editor ; python .agents/skills/podcast-editor/scripts/setup_podcast_editor.py
  ```

---

## 🎬 Usage

Organize your podcast shoot with three camera folders and audio:
```text
My_Podcast_Episode/
├── Camera 1/
├── Camera 2/
├── Camera 3/
└── Audio/ (or audio files inside Camera 1–3)
```

1. **Preflight Analysis (Sync + Diarization + Camera Role Classification + EDL)**:
   ```bash
   python3 .agents/skills/podcast-editor/scripts/podcast_orchestrator.py \
     --project-dir "/path/to/My_Podcast_Episode" \
     --mode preflight
   ```
2. **Live Foreground Edit in Adobe Premiere Pro (Primary) or DaVinci Resolve**:
   ```bash
   # Live in Adobe Premiere Pro:
   python3 .agents/skills/podcast-editor/scripts/podcast_orchestrator.py \
     --project-dir "/path/to/My_Podcast_Episode" \
     --mode execute \
     --nle premiere

   # Live in DaVinci Resolve:
   python3 .agents/skills/podcast-editor/scripts/podcast_orchestrator.py \
     --project-dir "/path/to/My_Podcast_Episode" \
     --mode execute \
     --nle davinci
   ```
   *(On Windows PowerShell/CMD, use `python` instead of `python3`).*
