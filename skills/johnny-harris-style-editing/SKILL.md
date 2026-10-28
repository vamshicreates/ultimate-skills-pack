---
name: johnny-harris-style-editing
description: >-
  AI Agent Skill for replicating Johnny Harris's signature cinematic visual journalism editing style.
  Activates when the user wants hand-crafted analog-digital collage videos, 3D relief heightmap animations
  in Blender/After Effects, red and yellow wax-pencil annotations, real physical textures (torn paper, tape,
  photocopy artifacts), and emotional documentary pacing with raw Foley audio. Generates complete project
  manifests, 3D camera flight plans, and timeline specs.
compatibility: Cross-platform (macOS, Windows, Linux). Works with Premiere Pro, After Effects, Blender, DaVinci Resolve, Remotion.
trigger-words: [johnny harris style, 3d relief map, paper tear video, wax pencil annotation, analog collage documentary, visual journalism]
---

# Johnny Harris Style Editing (`johnny-harris-style-editing`)

A complete production framework for coding agents and editors to replicate **Johnny Harris's** industry-defining visual journalism style. Blends grand cinematic scale with tactile, human imperfection: raw handheld camera work, hand-crafted paper cutouts, wax-pencil scribbles, 3D topographic relief maps, and dynamic orchestral-acoustic scoring.

---

## 1. Core Aesthetic DNA & Creative Stance

- **Tone & Persona:** Passionate, vulnerable, investigative, epic yet personal.
- **Visual Stance:** Human hands building a physical investigation board in front of the viewer. Imperfections (ragged edges, tape strips, thumb marks, 12fps stop-motion jitter) reinforce authenticity and investigative grit.
- **The Contrast:** High-tech 3D terrain elevation models contrasted against low-tech crumpled physical paper and wax crayons.

---

## 2. Timeline Architecture & Pacing Rules

- **Pacing Dynamics:** Alternates between intimate, breathless conversational monologues and rapid-fire visual montages synchronized to musical builds.
- **Cut Frequency:**
  - *Vlog / Monologue:* 4.0 to 7.0 seconds. Minimal jump-cuts; prefers natural pauses and subtle camera zooms.
  - *Collage Sequences / Map Flights:* 0.8 to 2.2 seconds per visual beat.
- **The "Map as Anchor":** The map is not a one-off graphic; it is the recurring theatrical stage that the story always returns to.

---

## 3. Topographic 3D Relief Maps (Blender / After Effects)

- **Terrain Shader Setup:**
  - High-resolution Digital Elevation Model (DEM) heightmap piped into Displacement/Microdisplacement.
  - Diffuse map: Desaturated satellite imagery with warm highlights.
  - Sun / Key Light: Low-angle directional sun (elevation `22°`, rotation `315°`) to cast long, dramatic relief shadows across mountain ranges.
- **Camera Movement:**
  - Wide sweeping drone-style flight drifting along valley lines.
  - Focal length: `35mm` to `50mm` (cinematic perspective, not extreme wide-angle distortion).
- **Cartographic Markings:**
  - Bold route lines drawn in dynamic paths with wax-crayon texture.
  - Glowing red dots or vintage location pins dropping with a tactile bounce.

---

## 4. Analog Collage Elements & Paper Craft

- **Stop-Motion Jitter (The 12fps Rule):**
  - All paper cutouts, arrows, and photos operate at `12 fps` (Posterize Time) even when the main composition is `24 fps`.
  ```javascript
  // After Effects Expression on Paper Cutout Transform
  posterizeTime(12);
  wiggle(3, 4);
  ```
- **Torn Paper & Tape:**
  - Hand-torn edges with visible paper fiber fringe.
  - Semi-translucent yellowing cellophane tape or matte gray gaffer tape securing photos to the canvas.
- **Wax Pencil Annotations:**
  - Crimson Red (`#D12626`) and Amber Yellow (`#F5A623`) grease pencil circles, arrows, and underlines that animate on with slight jitter.

---

## 5. Color Grading & Film Emulation

- **Color Profile:** Warm Kodachrome / 16mm film emulation.
- **Shadows:** Lifted blacks with subtle deep teal/warm charcoal tone (`#1E2226`).
- **Highlights:** Creamy, soft roll-off; whites clamped to `92 IRE`.
- **Grain:** Heavy fine-grain organic 16mm film scan overlay (`Blend Mode: Overlay`, Opacity `18%`).

---

## 6. Sound Design & Foley Architecture

Johnny Harris edits are defined by dense, tactile Foley:
- **Paper Mechanics:** Loud, crisp paper tearing, cardboard slides, photograph card snaps.
- **Pencil & Marker:** Gritty graphite scribbles, squeaky grease markers on glass.
- **Film Gear:** Projector reel hum, slide carousel clicks, 8mm camera winding gears.
- **Music Bed:** Emotional indie folk, swelling cinematic strings, post-rock electric guitar swells. The music never stays flat—it constantly swells during revelations and drops to complete silence on punchline questions.

---

## 7. Implementation Recipes

### After Effects Hand-Drawn Arrow / Line Rig:
1. Create a Shape Layer with a Stroke width of `8px`.
2. Apply `Roughen Edges`: Border `4.0`, Edge Sharpness `0.8`, Fractal Influence `0.6`.
3. Add `Trim Paths`: Animate `End` from `0%` to `100%` over `14 frames`.
4. Apply expression to `Evolution` of Roughen Edges:
   ```javascript
   posterizeTime(12);
   time * 300;
   ```

### DaVinci Resolve Node Tree for Warm Archival Grade:
- `Node 1 (Exposure/Contrast)`: Lift shadows +0.03, lower highlight gain to 0.92.
- `Node 2 (Color Warper)`: Shift cyan/blue toward teal; warm midtones toward amber.
- `Node 3 (Halation)`: Subtle red fringe on high-contrast specular edges.
- `Node 4 (Film Grain)`: 16mm grain preset, size `0.8`, strength `0.35`.\n