---
name: vox-style-editing
description: >-
  AI Agent Skill for replicating the iconic Vox-style journalistic explainer video editing aesthetic.
  Activates when the user wants explainer videos, educational journalism, flat 2D motion graphics,
  newspaper/document cutout collages, yellow highlighter text reveals, animated vector maps (GeoLayers),
  and tactile mechanical sound design (typewriters, paper rustles, camera clicks). Produces complete
  timeline blueprints, After Effects expression rigs, Premiere Pro/FCPXML multi-track sequence manifests,
  and FFmpeg prototyping pipelines.
compatibility: Cross-platform (macOS, Windows, Linux). Works with Premiere Pro, After Effects, DaVinci Resolve, Remotion, and FFmpeg.
trigger-words: [vox style, vox explainer, journalistic explainer, newspaper cutout video, yellow highlight edit, animated map explainer]
---

# Vox Style Editing (`vox-style-editing`)

A comprehensive production framework for coding agents and video editors to architect, script, and assemble **Vox-style journalistic explainers**. Replicates Vox's signature visual grammar: flat 2D graphic design, archival paper and headline cutouts, tactile marker annotations, clean vector maps, and mechanical sound design.

---

## 1. Core Aesthetic DNA & Editorial Philosophy

- **Tone & Persona:** Authoritative, intellectually curious, accessible, investigative.
- **Visual Stance:** Treat information as physical material. Archival documents, articles, treaties, and charts are brought onto the screen like physical artifacts inspected on a well-lit desk.
- **Core Principle:** *"Every graphic must answer a specific question."* Never use motion graphics for mere decoration; every visual transition advances the argument.

---

## 2. Timeline Architecture & Pacing Rules

- **Target Cut Frequency:** 3.0 to 4.5 seconds on A-roll; graphics and text accents trigger every 1.5 to 2.0 seconds.
- **Narrative Arc (5-Beat Explainer Structure):**
  1. *The Hook / Paradox (0:00 - 0:45):* Present a known fact, followed immediately by an anomaly ("We all know X, but why does Y happen?").
  2. *The Context / Origins (0:45 - 2:30):* Archival dive using newspaper clippings and historical maps.
  3. *The Mechanism (2:30 - 6:00):* Vector diagrams, charts, and data visualizations breaking down the engine of the problem.
  4. *The Complication (6:00 - 8:30):* Counter-arguments, unexpected consequences, global implications.
  5. *The Resolution / Takeaway (8:30 - End):* Wide-lens philosophical synthesis with a returning thematic motif.

---

## 3. Typography & Text Animation

- **Primary Headline Font:** Balto Bold, GT America Compressed, Knockout, or Anton (All-Caps, tightly tracked `-20`).
- **Secondary / Body Font:** Georgia, Minion Pro, or GT Sectra (editorial serif for document citations).
- **Data / Coordinates:** Roboto Mono or Space Mono.
- **The Signature Yellow Highlighter:**
  - Background accent: `#FFF200` or `#FFE600`.
  - Stroke: Animated horizontal trim paths wiping left-to-right beneath or behind charcoal text (`#1A1A1A`).
  - Round caps, slight tilt (1.5° to 3°) to mimic natural marker hand pressure.

### After Effects Expression: Marker Highlight Wipe
Apply to `End` of Trim Paths on a Shape Layer:
```javascript
// Vox Marker Ease-In-Out with subtle hand hesitation
var tStart = inPoint;
var dur = 0.45;
ease(time, tStart, tStart + dur, 0, 100);
```

---

## 4. Motion Graphics & Visual Effects (VFX)

- **Document Cutout Treatment:**
  - Drop shadow: Distance `18px`, Softness `45px`, Opacity `18%`, Angle `135°`.
  - Paper Texture Overlay: Subtle warm recycled paper texture (`Blend Mode: Multiply`, Opacity `12%`).
  - Subtle floating wiggle on documents:
    ```javascript
    // Subtle float expression on Layer Position
    w = wiggle(0.8, 6);
    [w[0], w[1]];
    ```
- **Map Visualizations:**
  - Clean flat vector maps (GeoLayers 3 or QGIS SVG exports).
  - Borders in `#1A1A1A` with thickness `2px`.
  - Disputed/highlighted territories pulse gently or fill with Vox Yellow with diagonal hatching.
- **Split-Screen Comparisons:**
  - Strict 50/50 or 60/40 vertical dividers with a clean `2px` slate border.

---

## 5. Color Palette & Tone

| Element | Hex Code | Purpose |
|---|---|---|
| Background Slate | `#F4F4F0` | Warm, non-sterile off-white desk paper tone |
| Deep Charcoal | `#1A1A1A` | Primary typography and vector outlines |
| Signature Yellow | `#FFF200` | Critical emphasis, highlighter pens, main metric |
| Editorial Cyan | `#00A8CC` | Secondary comparative metric / water on maps |
| Editorial Crimson | `#E63946` | Warning, negative trend, opposition party |

---

## 6. Sound Design & Audio Engineering

- **Dialogue Mastering:** Clean, intimate podcast presence. High-pass filter at `80Hz`, gentle dip at `350Hz`, air boost at `12kHz`. Mastered to `-16 LUFS` (YouTube standard).
- **Tactile Mechanical Foley:**
  - Marker squeak: Synced to the exact frame the highlight begins.
  - Paper rustle/drop: Placed 2 frames before a document hits the desk.
  - Typewriter / mechanical keyboard click: Per word or letter reveal on typewriter text.
  - Camera shutter / flash: On archival still-photo reveals.
- **Music Bed:** Minimalist neo-classical, marimba-driven ostinatos, clean upbeat electro-acoustic rhythms (e.g., Steve Reich-inspired marimbas or warm Rhodes piano chords). Ducked `-18dB` under dialogue.

---

## 7. Implementation Recipes

### Premiere Pro Multi-Track Layout:
- `V3`: Kinetic text highlights, lower-third tags, marker shape layers.
- `V2`: Archival newspaper scans, map animations, cutout overlays.
- `V1`: Primary presenter A-roll or solid background card (`#F4F4F0`).
- `A1`: Voiceover / A-Roll dialogue.
- `A2`: Foley & Tactile Sound Effects (marker squeaks, paper drops, clicks).
- `A3`: Music Bed (sidechain-ducked to dialogue).

### FFmpeg Quick-Prototype Recipe (Add Paper Texture & High-Contrast Grade):
```bash
ffmpeg -i input_clip.mp4 -i paper_texture.jpg -filter_complex "[0:v]eq=contrast=1.12:brightness=-0.02:saturation=0.95[vid];  [1:v]scale=1920:1080,format=rgba,colorchannelmixer=aa=0.12[tex];  [vid][tex]blend=all_mode='multiply'[outv]" -map "[outv]" -map 0:a -c:v libx264 -pix_fmt yuv420p -c:a aac output_vox.mp4
```\n