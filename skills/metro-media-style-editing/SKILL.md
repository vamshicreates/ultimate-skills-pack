---
name: metro-media-style-editing
description: >-
  AI Agent Skill for replicating Metro Media House's (@metromediahouse) executive authority and high-converting B2B talking-head style.
  Activates when the user wants corporate thought-leadership videos, CEO/founder podcast recuts (Diary of a CEO style),
  clean word-by-word opacity subtitles, authoritative lower-thirds, curated archival B-roll, and broadcast-grade audio mastering.
  Outputs clean multi-track NLE templates, executive subtitle specs, and broadcast audio workflows.
compatibility: Cross-platform (macOS, Windows, Linux). Works with Premiere Pro, After Effects, DaVinci Resolve, CapCut.
trigger-words: [metro media style, executive talking head, diary of a ceo edit, b2b thought leadership video, corporate podcast recut]
---

# Metro Media Style Editing (`metro-media-style-editing`)

A production framework for coding agents and editors to craft **executive-level, high-authority thought-leadership content** in the style of **Metro Media House (@metromediahouse)**. Tailored for enterprise leaders, venture capitalists, and premium podcasts (e.g., *The Diary of a CEO*). Combines intimate multi-camera framing with refined typography, curated archival B-roll, and broadcast-grade audio mastering.

---

## 1. Core Aesthetic DNA & Brand Authority

- **Tone & Persona:** Executive, intelligent, reflective, inspiring, premium.
- **Visual Stance:** *"Substance over noise."* Avoids obnoxious cartoon sound effects and childish emojis. Focuses on the weight of the speaker's words, using subtle camera shifts and premium editorial pacing.
- **Atmosphere:** Warm studio lighting with high contrast, shallow depth of field (f/1.4–f/2.0), and rich natural shadows.

---

## 2. Multi-Cam Switching & Pacing Rules

- **Camera Setup:**
  - *Cam A (Wide Master):* Captures physical gestures, posture, and conversational environment.
  - *Cam B (Close-Up Profile):* 85mm lens tight on eyes and mouth; cuts to Cam B during vulnerability or profound revelations.
- **Pacing:** Conversational, unhurried, yet tightly trimmed (no dead pauses longer than 0.3s). Cuts occur on the downbeat of key philosophical phrases.

---

## 3. Subtitles & Typography

- **Font:** Inter, SF Pro Display, or Neue Haas Grotesk.
- **The Word-by-Word Opacity Technique:**
  - Full sentence is visible on screen in muted gray (`Opacity: 35%`).
  - As each word is spoken, it illuminates to pure white (`Opacity: 100%`) with a subtle 2px scale bump.
  - Never obscures the speaker's face; positioned safely in the lower-third or center-chest zone.

---

## 4. Curated B-Roll & Visual Accents

- **Archival Selection:** Premium black-and-white historical footage, slow-motion urban architecture, or subtle macro shots of nature/technology.
- **Transitions:** Smooth J-cuts (audio of B-roll begins 12 frames before video cut) and L-cuts to maintain natural conversational continuity.

---

## 5. Color Grading & Studio Look

- **Color Profile:** Neutral, cinematic studio grade.
- **Shadows:** Deep, velvety blacks with gentle shadow lift.
- **Skin Tones:** Completely natural, healthy, and authentic.

---

## 6. Broadcast Audio Mastering

- **Loudness Standards:** Mastered strictly to `-16.0 LUFS` (YouTube) or `-14.0 LUFS` (Instagram/TikTok) with True Peak at `-1.0 dBFS`.
- **Signal Chain:**
  1. High-Pass Filter at `75Hz`.
  2. Surgical Notch EQ removing room resonance (often `250Hz` and `450Hz`).
  3. Multiband Compression (taming harsh sibilance at `5–8kHz`).
  4. Subtle optical tube saturation adding vocal warmth.
- **Music:** Minimal ambient piano or warm neoclassical strings, mastered at `-22dB` beneath speech.\n