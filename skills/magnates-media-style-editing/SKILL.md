---
name: magnates-media-style-editing
description: >-
  AI Agent Skill for replicating the cinematic business documentary style of MagnatesMedia.
  Activates when the user wants dark, suspenseful corporate thrillers, 2.5D parallax photo manipulation,
  dramatic rim lighting, cinematic noir grading, orchestral suspense music, and deep trailer sound design
  (braams, sub-booms, ticking clocks). Outputs full 3D camera layer layouts, timeline structures, and
  audio design specs.
compatibility: Cross-platform (macOS, Windows, Linux). Works with Premiere Pro, After Effects, DaVinci Resolve, Blender.
trigger-words: [magnatesmedia style, business documentary, 2.5d parallax photo, corporate thriller edit, cinematic noir documentary]
---

# MagnatesMedia Style Editing (`magnates-media-style-editing`)

A production framework for coding agents and editors to engineer **cinematic corporate thriller documentaries** in the style of **MagnatesMedia**. Transforms static company histories and financial reports into high-stakes Hollywood-style dramas using multiplane 2.5D parallax, dramatic atmospheric lighting, and high-impact trailer sound design.

---

## 1. Core Aesthetic DNA & Storytelling Engine

- **Tone & Persona:** Cinematic, dramatic, suspenseful, epic, forensic.
- **The Core Premise:** *"Every business story is a crime story or a Greek tragedy."* Greed, hubris, betrayal, and catastrophic downfall are emphasized visually and sonically.
- **Visual Stance:** Dark, atmospheric 3D spaces where historical figures emerge from shadows with cinematic depth and particle haze.

---

## 2. Timeline Architecture & Pacing Rules

- **Pacing Pattern:** Tension $
ightarrow$ Build-Up $
ightarrow$ False Climax $
ightarrow$ The Crash $
ightarrow$ Aftermath.
- **Cut Frequency:**
  - *Exposition & Setup:* 4.0 to 6.0 seconds with slow, sweeping 3D camera drift.
  - *The Climax / Downfall Montage:* Rapid 0.8 to 1.5 second cuts synced to heavy trailer percussion.
- **Suspense Pauses:** Complete audio silence / sub-bass drops for 1.5 seconds right before revealing major figures or financial fraud.

---

## 3. The 2.5D Parallax Photo System

Every key historical photograph is deconstructed into a 3D parallax scene:
1. **Photoshop / Masking Pass:**
   - Layer 1 (Foreground): Floating money, burning documents, or barbed wire.
   - Layer 2 (Subject): The CEO / magnate isolated cleanly using refine edge.
   - Layer 3 (Midground): Office furniture, boardroom table, stock tickers.
   - Layer 4 (Background): Generative AI-filled background, dark skyscrapers, storm clouds.
2. **After Effects 3D Camera Setup:**
   - 3D Camera (`50mm` or `85mm` telephoto lens).
   - Space layers in Z-depth (`0`, `-400`, `600`, `1800`).
   - Enable Depth of Field (`Aperture: 28px`, `Blur Level: 120%`).
   - Slow continuous camera dolly: Z-position moves forward 350 units over 5 seconds.
3. **Rim Light & Volumetric Glow:**
   - Add an amber, emerald, or crimson edge-light glow behind the subject using Layer Styles (`Inner Shadow` + `Drop Shadow` set to `Screen`).

---

## 4. Typography & Title Design

- **Primary Font:** Cinematic Trajan, Cinzel, Bodoni Poster, or Cormorant Garamond.
- **Treatment:**
  - Gold metallic gradient or stark bloody red.
  - Slow letter-spacing expansion (`Tracking: 150` $
ightarrow$ `350` over 6 seconds).
  - Subtle light-sweep flare moving across the gold metallic bevel.
- **Lower Thirds:** Minimalist gold bar with clean serif name and year of event.

---

## 5. Color Grading & Palette (The Noir Look)

| Element | Color Value | Description |
|---|---|---|
| Deep Black | `#08090C` | Crushed shadows, heavy vignette |
| Corporate Navy | `#0D1B2A` | Cold corporate atmosphere |
| Wealth Gold | `#D4AF37` | Symbol of luxury, capital, ambition |
| Catastrophe Red | `#B00020` | Bankruptcy, scandal, criminal indictment |

---

## 6. Sound Design & Trailer Audio Architecture

- **Trailer Impacts:** Low-frequency braams, cinematic anvil clangs, sub-bass booms on every chapter title.
- **Tension Elements:** Rhythmic clock ticking (increasing in BPM), cello drone sustains, high-frequency riser whistles.
- **Environmental Foley:** Boardroom door slams, heavy leather chair creaks, fountain pen signing contracts, gavel strikes.
- **Music:** Dark orchestral hybrid: Hans Zimmer-style ostinatos, heavy brass, ticking percussion, and somber piano chords.

---

## 7. After Effects Parallax Camera Drift Expression

Apply to `Position` of the 3D Camera:
```javascript
// Slow continuous cinematic dolly with subtle organic breath
var speed = 40; // pixels per second
var startPos = value;
var zOffset = time * speed;
var breath = wiggle(0.3, 8);
[startPos[0] + breath[0], startPos[1] + breath[1], startPos[2] - zOffset];
```\n