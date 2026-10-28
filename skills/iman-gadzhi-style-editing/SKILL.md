---
name: iman-gadzhi-style-editing
description: >-
  AI Agent Skill for replicating the high-end personal brand, luxury lifestyle, and high-retention
  editing style of Iman Gadzhi. Activates for entrepreneurial videos, viral YouTube essays, 3D financial
  asset renders (coins, cards), retro film burns, VHS glitches, kinetic grotesque typography, and
  aggressive sound design (808 drops, cash registers, metallic whooshes). Outputs complete editing
  instructions, After Effects motion expressions, and multi-track timelines.
compatibility: Cross-platform (macOS, Windows, Linux). Works with Premiere Pro, After Effects, DaVinci Resolve, Remotion.
trigger-words: [iman gadzhi style, luxury video edit, high retention editing, 3d coin animation, film burn transitions, agency video edit]
---

# Iman Gadzhi Style Editing (`iman-gadzhi-style-editing`)

A production framework for coding agents and editors to create **ultra-high-retention, luxury personal brand content** in the style of **Iman Gadzhi**. Blends high-status cinematic lifestyle B-roll with aggressive short-interval motion graphics, 3D renders, vintage film burns, and heavy bass-driven audio engineering.

---

## 1. Core Aesthetic DNA & Creative Philosophy

- **Tone & Persona:** Elite, aspirational, unapologetic, strategic, charismatic.
- **Visual Stance:** *"Maximum sensory retention with high-status polish."* Every concept is reinforced by a bespoke 3D asset, archival clip, or kinetic typography pop within 2 seconds.
- **Visual Contrast:** High-end supercars and luxury penthouses blended with retro tech (CRT monitors, cassette tapes, newspaper archives) to communicate timeless wealth and modern leverage.

---

## 2. Timeline Architecture & Retention Rules

- **The 2-Second Rule:** A visual event must occur every 1.5 to 2.5 seconds (B-roll cut, zoom punch-in, 3D asset pop, or sound-synced sound effect).
- **A-Roll Execution:**
  - Multi-cam setup (Wide 24mm + Tight 85mm).
  - Rapid scale punch-ins (100% $
ightarrow$ 115% $
ightarrow$ 130%) on punchlines or critical declarations.
  - Zero dead air: All breaths and vocal hesitations clipped out with frame-blended jump cuts.

---

## 3. 3D Elements & Visual Effects (VFX)

- **3D Floating Assets (Blender / After Effects Element 3D):**
  - Gold bullion bars, spinning gold coins, black metal credit cards, luxury watches, and chess pieces.
  - Renders feature strong metallic roughness maps, specular reflections, and chromatic dispersion.
- **Film Overlays & Burns:**
  - 8mm and 16mm film burns (Kodak 500T).
  - CRT TV scanlines and VHS tape distortion glitches during historical or educational callbacks.
  - Light leaks used as rapid transition wipes between distinct concepts.

---

## 4. Typography & Title Design

- **Primary Font:** Druk Wide Bold, Monument Extended, Futura Bold, or Neue Haas Grotesk.
- **Styling:**
  - Heavy All-Caps with neon green, luxury gold, or electric blue edge glow.
  - Fast-tracked single-word or two-word subtitle reveals.
  - Words punch into frame with an elastic bounce.

### After Effects Elastic Scale In Expression
Apply to `Scale` of text or graphic:
```javascript
// Iman Gadzhi snappy elastic pop
var n = 0;
if (numKeys > 0) {
  n = nearestKey(time).index;
  if (key(n).time > time) n--;
}
if (n == 0) {
  t = 0;
} else {
  t = time - key(n).time;
}
if (n > 0 && t < 1) {
  var v = velocityAtTime(key(n).time - 0.001);
  var amp = 0.06;
  var freq = 4.0;
  var decay = 8.0;
  value + (v / 100) * amp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t);
} else {
  value;
}
```

---

## 5. Color Grading & Palette

- **Grade:** Rich, high-contrast, saturated luxury look.
- **Shadows:** Crushed deep blacks (`#050505`) with subtle teal/green undertones.
- **Midtones / Skin:** Healthy, bronzed, warm golden skin tones.
- **Accents:** Neon Emerald Green (`#00E676`) and Sovereign Gold (`#FFD700`).

---

## 6. Sound Design & Audio Architecture

- **Voiceover:** Ultra-crisp, deep proximity effect (Shure SM7B profile). Bass boosted at `100Hz`, de-essed at `6kHz`.
- **Impact SFX:**
  - 808 sub-bass drops on thesis statements.
  - Heavy metallic swooshes, gun chamber clicks, coin clinks.
  - Cash register bell ("cha-ching") on profit/revenue mentions.
- **Music:** Aggressive dark trap, modern phonk, or cinematic synthwave; sidechain-ducked `-14dB` under speech.\n