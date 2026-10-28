---
name: arsacre-style-editing
description: >-
  AI Agent Skill for replicating Arsacre's (@Arsacre / @arsacre5) advanced 3D motion design and kinetic explainer style.
  Activates when the user wants top-tier After Effects/Blender motion graphics, custom Bezier easing curves, 3D rotating
  device mockups, isometric UI cards, sleek liquid morph transitions, and modern SaaS/tech explainer aesthetics.
  Outputs complete keyframe easing parameters, expression scripts, and 3D compositing guides.
compatibility: Cross-platform (macOS, Windows, Linux). Works with After Effects, Blender, DaVinci Resolve (Fusion), Premiere Pro.
trigger-words: [arsacre style, arsacre motion design, 3d after effects edit, kinetic typography masterclass, saas explainer animation]
---

# Arsacre Style Editing (`arsacre-style-editing`)

A production framework for coding agents and motion designers to produce **elite, masterclass-level motion design and 3D kinetic animations** in the style of **Arsacre (@Arsacre / @arsacre5)**. Known for fluid bezier keyframe physics, 3D rotating device mockups, isometric vector UI layouts, and seamless morphing transitions.

---

## 1. Core Aesthetic DNA & Motion Principles

- **Tone & Persona:** Futuristic, ultra-polished, fluid, premium, design-forward.
- **The Core Rule of Motion:** *"No linear keyframes ever."* Every movement must have extreme easing influence (`Speed: 0` $
ightarrow$ `Peak` $
ightarrow$ `0`, with `85%` influence on the graph editor).
- **Visual Stance:** Complex tech concepts visualized as tactile, beautiful 3D digital objects with depth, reflections, and spatial hierarchy.

---

## 2. Keyframe Physics & Bezier Easing Curves

Arsacre's signature fluidity comes from extreme graph-editor shaping:
- **Snappy Pop Curve:**
  - Incoming Velocity: `0`, Incoming Influence: `85%`.
  - Outgoing Velocity: `0`, Outgoing Influence: `85%`.
- **After Effects ExtendScript for Snappy Keyframes:**
  ```javascript
  // Apply Arsacre 85% Bezier Easing to selected property
  var prop = app.project.activeItem.selectedLayers[0].selectedProperties[0];
  var easeIn = new KeyframeEase(0, 85);
  var easeOut = new KeyframeEase(0, 85);
  for (var i = 1; i <= prop.numKeys; i++) {
    prop.setTemporalEaseAtKey(i, [easeIn], [easeOut]);
  }
  ```

---

## 3. 3D Device Mockups & Isometric UI (Blender / After Effects)

- **3D Tech Mockups:**
  - iPhone 15/16 Pro or MacBook Pro floating in 3D space with subtle continuous rotation.
  - Screen displays live UI elements reacting to mouse clicks and scrolls.
  - Realistic metallic roughness reflections and glass refraction.
- **Isometric Grid Cards:**
  - 3D layer rotated at `X: 45°`, `Y: 0°`, `Z: 35°` (true isometric angle).
  - Floating interface buttons and cards stacked in Z-depth with variable shadow drop.

---

## 4. Typography & Kinetic Text

- **Fonts:** PP Neue Montreal, Syne, Neue Haas Grotesk, or Formula Condensed.
- **Kinetic Mechanics:**
  - Characters slide up from behind an invisible mask line (`Track Matte`).
  - Text scales down smoothly as camera pushes past it into the next scene.
  - 3D kinetic title rolls along X/Y rotation axes.

---

## 5. Color Palette & Dark-Mode Aesthetic

| Element | Hex Code | Description |
|---|---|---|
| Deep Space Black | `#090A0F` | Infinite background canvas |
| Surface Slate | `#141721` | Floating UI cards and panels |
| Electric Cobalt | `#2563EB` | Primary tech accent and glowing gradients |
| Cyber Emerald | `#10B981` | Success states, metrics, graph lines |
| Clean White | `#F8FAFC` | High-contrast typography |

---

## 6. Sound Design & Micro-Foley

- High-precision audio: Every keyframe movement has an exact micro-SFX counterpart.
- Mechanical keyboard clacks, digital laser chirps, smooth high-pass frequency whooshes, and sub-bass drops.\n