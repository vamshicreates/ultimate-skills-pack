---
name: gawx-art-style-editing
description: >-
  AI Agent Skill for replicating Gawx Art's (@GawxArt / @gawx_art) kinetic creative vlog and doodle art editing style.
  Activates when the user wants mixed-media video editing, frame-by-frame doodle animations, stop-motion frame drops
  (8-12fps), energetic match-cuts, street-art and sketchbook aesthetics, and ultra-tactile Foley (marker squeaks,
  spray cans, paper cuts). Outputs frame-boil expressions, mixed-media timeline setups, and percussive audio maps.
compatibility: Cross-platform (macOS, Windows, Linux). Works with Premiere Pro, After Effects, DaVinci Resolve, Photoshop.
trigger-words: [gawx art style, gawx style edit, doodle animation video, mixed media vlog, stop motion edit, streetwear video edit]
---

# Gawx Art Style Editing (`gawx-art-style-editing`)

A production framework for coding agents and editors to create **hyper-kinetic, mixed-media creative vlogs** in the signature style of **Gawx Art (@GawxArt)**. Blends real-world filmmaking with frame-by-frame digital doodle animations, stop-motion textures, energetic match cuts, and tactile physical Foley.

---

## 1. Core Aesthetic DNA & Creative Energy

- **Tone & Persona:** Youthful, boundless creative energy, artistic, rebellious, hyper-focused.
- **Visual Stance:** *"Art coming alive in the real world."* The screen is a dynamic sketchbook where reality is constantly drawn over, painted, torn, and reassembled.
- **Signature Style:** Bright primary colors, bold black comic outlines, animated eyes/horns/lightning doodled on real footage, and high-tempo beat synchronization.

---

## 2. Frame-by-Frame Doodle Animation (The Boil Effect)

- **The Boil / Jitter:**
  - Doodles are drawn with 3 slightly varying frames that cycle at `10 fps` or `12 fps` to create an organic, trembling hand-drawn aesthetic.
- **After Effects Boil Expression (Apply to Time Remap of a 3-frame doodle loop):**
  ```javascript
  // Gawx 3-frame doodle loop at 10 fps
  var fps = 10;
  var numFrames = 3;
  posterizeTime(fps);
  (Math.floor(time * fps) % numFrames) * thisComp.frameDuration;
  ```
- **Elements:** Electric lightning bolts, doodle crown over head, anime action lines, flame trails on flying objects, playful sound effect words ("BAM!", "POW!", "SKRRR").

---

## 3. Stop-Motion Rhythm & Fast Match Cuts

- **Frame Rate Shifts:** Real footage runs at `24fps` or `60fps`, but montage and transition sequences deliberately drop to `8fps` or `12fps` using `Posterize Time` to simulate claymation/stop-motion.
- **Whip & Match Cuts:** Camera movements end on a fast whip-pan or snap-zoom, cutting seamlessly into a frame moving in the identical vector direction.

---

## 4. Typography & Graphic Design

- **Font Style:** Custom hand-drawn lettering, chunky comic graffiti fonts, or distressed cut-out letters from magazines.
- **Colors:** Vibrant cartoon yellow (`#FFE500`), spray-can hot pink (`#FF0055`), electric cyan (`#00F5D4`), and deep ink black (`#111111`).

---

## 5. Sound Design & Percussive Foley

- **Tactile Artist Foley:**
  - Posca marker squeaks and tips clicking on canvas.
  - Spray paint can marble shaking and pressurized nozzle hisses.
  - X-Acto blade slicing cardboard, paper crumples, tape tears.
- **Music:** High-energy boom-bap hip-hop, lo-fi drum breaks, scratch transitions, and heavy bass lines. Every drum snare is synchronized with a doodle pop or frame cut.\n