---
name: recordly
description: >-
  Create polished product demo videos, screen recordings, walkthroughs, and `.recordly` timeline
  projects with auto-zooms, cursor smoothing/click effects, styled wallpaper/gradient frames,
  rounded corners, drop shadows, webcam bubble overlays, annotations, auto-captions, and headless
  MP4/GIF export using Recordly (webadderallorg/Recordly). Trigger whenever the user mentions
  Recordly, `.recordly` project files, Screen Studio-style auto-zoom screen recordings, cursor
  polish, or Recordly extensions.
---

# Recordly (`recordly`)

Open-source screen recorder and motion-driven demo video editor ([webadderallorg/Recordly](https://github.com/webadderallorg/Recordly)) installed in `.agents/skills/recordly`.

Use this skill to:
1. **Generate `.recordly` Project Files Programmatically**: Turn any raw MP4/WebM screen capture into a styled `.recordly` project with smooth camera zooms (`ZoomRegion`), cursor effects (`tahoe`, `macos`, `figma`, `ripple`, `spotlight`, `echo`), wallpapers/gradients, padding, rounded corners, drop shadows, trims, speed ramps, annotations, auto-captions, and webcam bubble overlays.
2. **Headless / Automated MP4 Export**: Render `.recordly` projects or raw recordings directly to polished MP4 videos via Recordly's built-in `RECORDLY_SMOKE_EXPORT=1` automation pipeline.
3. **Install or Launch Recordly on macOS**: Install the latest prebuilt `Recordly.app` release (with macOS quarantine removal) or build/run from source inside `.agents/skills/recordly`.
4. **Author Recordly Extensions**: Build custom render hooks, cursor effects, frames, wallpapers, and settings panels using the Recordly Extension API ([EXTENSIONS.md](./EXTENSIONS.md)).

---

## Quick CLI Workflows ([recordly-cli.mjs](./scripts/recordly-cli.mjs))

### 1. Install Recordly Desktop App on macOS (`/Applications/Recordly.app`)
Downloads the latest `.dmg` for the current Mac architecture (`arm64` / `x64`), installs `Recordly.app` into `/Applications`, and strips the macOS Gatekeeper quarantine attribute:
```bash
node .agents/skills/recordly/scripts/recordly-cli.mjs install-mac
```

### 2. Generate a Styled `.recordly` Project from Any Video
Create a `.recordly` project file with custom zoom regions (`startMs:endMs:depth:cx:cy`, where `depth` is `1`–`6` corresponding to `1.25x`–`5.0x` zoom, and `cx`/`cy` are normalized `0`–`1` coordinates), speed ramps (`startMs:endMs:speed`), trims (`startMs:endMs`), cursor styling, and background frame:
```bash
node .agents/skills/recordly/scripts/recordly-cli.mjs create-project \
  --video "/absolute/path/to/raw-screen.mp4" \
  --output "/absolute/path/to/demo.recordly" \
  --wallpaper "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)" \
  --padding 24 \
  --border-radius 8 \
  --shadow 0.65 \
  --cursor-style tahoe \
  --click-effect ripple \
  --zoom "1000:3500:3:0.35:0.45" \
  --zoom "5000:8000:2:0.70:0.30" \
  --speed "8500:12000:1.5" \
  --quality high \
  --fps 60
```

### 3. Headless Export (`.recordly` Project or Raw Video -> MP4)
Render and export without manual GUI clicks using Recordly's `RECORDLY_SMOKE_EXPORT=1` automation flags:
```bash
node .agents/skills/recordly/scripts/recordly-cli.mjs export \
  --input "/absolute/path/to/demo.recordly" \
  --output "/absolute/path/to/demo-polished.mp4" \
  --quality high \
  --fps 60
```

### 4. Open in Recordly Editor GUI
```bash
node .agents/skills/recordly/scripts/recordly-cli.mjs open "/absolute/path/to/demo.recordly"
```

---

## `.recordly` Project JSON Schema Reference

A `.recordly` file is a JSON document conforming to `EditorProjectData` ([projectPersistence.ts](./src/components/video-editor/projectPersistence.ts) & [types.ts](./src/components/video-editor/types.ts)):

```json
{
  "version": 2,
  "videoPath": "/absolute/path/to/recording.mp4",
  "editor": {
    "wallpaper": "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
    "shadowIntensity": 0.6,
    "backgroundBlur": 0,
    "zoomMotionBlur": 0.35,
    "connectZooms": true,
    "zoomInEasing": "recordly",
    "zoomOutEasing": "recordly",
    "connectedZoomEasing": "glide",
    "showCursor": true,
    "loopCursor": false,
    "cursorStyle": "tahoe",
    "cursorClickEffect": "ripple",
    "cursorClickEffectColor": "#2563EB",
    "cursorSize": 3.0,
    "cursorSmoothing": 0.67,
    "cursorMotionBlur": 0.6,
    "cursorClickBounce": 2,
    "cursorSway": 0.4,
    "borderRadius": 8,
    "padding": { "top": 20, "bottom": 20, "left": 20, "right": 20, "linked": true },
    "cropRegion": { "x": 0, "y": 0, "width": 1, "height": 1 },
    "zoomRegions": [
      {
        "id": "zoom-1",
        "startMs": 1000,
        "endMs": 3500,
        "depth": 3,
        "focus": { "cx": 0.5, "cy": 0.5 },
        "mode": "manual"
      }
    ],
    "trimRegions": [],
    "speedRegions": [],
    "annotationRegions": [],
    "audioRegions": [],
    "autoCaptions": [],
    "aspectRatio": "16:9",
    "exportEncodingMode": "balanced",
    "exportQuality": "high",
    "mp4FrameRate": 60,
    "exportFormat": "mp4"
  }
}
```

### Key Field Values
- **Zoom Depth (`depth`)**: `1` (`1.25×`), `2` (`1.5×`), `3` (`1.8×`, default), `4` (`2.2×`), `5` (`3.5×`), `6` (`5.0×`).
- **Zoom Easing**: `"recordly"` | `"glide"` | `"smooth"` | `"snappy"` | `"linear"`.
- **Cursor Styles (`cursorStyle`)**: `"tahoe"` (default), `"tahoe-inverted"`, `"macos"`, `"windows11"`, `"dot"`, `"figma"`.
- **Click Effects (`cursorClickEffect`)**: `"none"` | `"spotlight"` | `"ripple"` | `"echo"`.
- **Playback Speeds (`SpeedRegion.speed`)**: `0.25` | `0.5` | `0.75` | `1.25` | `1.5` | `1.75` | `2`.
- **Annotations (`AnnotationRegion.type`)**: `"text"` | `"image"` | `"figure"` (arrows) | `"blur"`.

---

## Building from Source or Running Dev Mode

If modifying Recordly's renderer/Electron source or running locally without `/Applications/Recordly.app`:
```bash
cd .agents/skills/recordly
npm install
npm run dev
```
For a packaged macOS `.dmg` build:
```bash
npm run build:mac
```

## Detailed References in This Skill Folder
- [README.md](./README.md) — Overview, features, and platform notes.
- [EXTENSIONS.md](./EXTENSIONS.md) — Recordly Extension API (`registerRenderHook`, `registerCursorEffect`, `registerFrame`, `registerWallpaper`, `registerCursorStyle`).
- [docs/timeline-sequence.md](./docs/timeline-sequence.md) — Clip sequence timing, contiguous cuts, and boundary snapping.
- [src/components/video-editor/projectPersistence.ts](./src/components/video-editor/projectPersistence.ts) — Full `.recordly` serialization and normalization implementation.
- [src/components/video-editor/smokeExportConfig.ts](./src/components/video-editor/smokeExportConfig.ts) — Headless/automated export query and environment parameters.
