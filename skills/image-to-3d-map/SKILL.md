---
name: image-to-3d-map
description: >-
  Convert any dropped 2D map image (Illustrated Campus/Venue/Theme Park map,
  Architectural Floor Plan, Geographic/Topographical Terrain map, or Real Estate
  Master Site Plan) into a complete, non-blocking interactive 3D WebGL map built
  with Next.js and Three.js. Produces a mobile + desktop responsive 3D map,
  off-main-thread Web Worker depth/normal/wall extrusion, interactive 3D pins,
  and a universal <three-d-map> embed snippet that works in any website or CMS
  with 0ms host page load blocking. Activate whenever the user drops a map image
  or asks to build an interactive 3D map for a website.
---

# Image-to-3D-Map (`image-to-3d-map`)

Turn any 2D map image into a production-ready, mobile- and desktop-optimized **Next.js + Three.js Interactive 3D Map** that **never blocks host website loading** and can be embedded into **any website or platform** (WordPress, Webflow, Shopify, Wix, plain HTML, Vue, Angular, React, or Next.js).

---

## Skill Directory & Core Engine Paths

- **Skill Directory (`<SKILL_DIR>`):**
  `$HOME/Documents/VamshiCreates/AntiGravity/VamshiCreates/.agents/skills/image-to-3d-map` (or `~/.gemini/config/skills/image-to-3d-map`)
- **Automated Skill Builder Script:**
  [`scripts/build_3d_map.mjs`](scripts/build_3d_map.mjs)
- **Next.js + Three.js Studio Root:**
  `$HOME/Documents/VamshiCreates/AntiGravity/VamshiCreates/map-3d-studio`

---

## The 4 Supported Map Modes (Auto-Detected & Configurable)

Whenever the user provides an image, inspect it using `view_file` and select (or let `mode: "auto"` classify) the matching archetype:

1. **`campus` (Illustrated / Venue / Campus / Festival / Theme Park Maps)**
   - **3D Behavior:** Tactile displaced 3D relief surface + extruded hero landmarks + 3D water basins + glowing curved 3D navigation tubes + interactive floating pins.
2. **`floorplan` (Architectural Floor Plans & Blueprints)**
   - **3D Behavior:** Adaptive contrast wall/partition detector extrudes 2D walls into razor-sharp vertical 3D architectural walls (`InstancedMesh`) and interior furniture at half-height, with room labels and tour paths.
3. **`terrain` (Geographic / Topographical / Satellite Maps)**
   - **3D Behavior:** Multi-pass smoothed elevation mesh with alpine peaks, valleys, tangent-space Sobel normal mapping, specular 3D water plane, and summit markers.
4. **`siteplan` (Real Estate Master Plans & Parcel Layouts)**
   - **3D Behavior:** Extrudes lot parcels and building footprints in 3D, adds availability status badges (`available`, `reserved`, `sold`), and enables the interactive **Sun Azimuth & Time-of-Day Shadow Simulator**.

---

## Step-by-Step Execution Pipeline

### Stage 1: Visual Inspection & Landmark Coordinate Extraction
1. View the user's dropped image using `view_file`.
2. Identify the map archetype (`campus`, `floorplan`, `terrain`, or `siteplan`).
3. Visually locate 4–8 key points of interest (rooms, buildings, summits, or lots) on the image and estimate their normalized coordinates:
   - `x`: `-0.5` (left edge) to `+0.5` (right edge), `0.0` is center.
   - `z`: `-0.5` (top edge) to `+0.5` (bottom edge), `0.0` is center.

### Stage 2: Execute `build_3d_map.mjs`
Run the self-contained skill builder script with the extracted pins JSON:

```bash
node $HOME/Documents/VamshiCreates/AntiGravity/VamshiCreates/.agents/skills/image-to-3d-map/scripts/build_3d_map.mjs \
  --image "/absolute/path/to/dropped-image.png" \
  --mode "auto" \
  --title "Custom Map Title" \
  --pins '[{"id":"p1","title":"Main Hub","subtitle":"Zone A","description":"Primary landmark","x":-0.15,"z":-0.12,"color":"#38bdf8","status":"open"}]'
```

### Stage 3: Verify & Present the 3 Deliverables
Present the generated outputs clearly to the user:
1. **Live Interactive Preview Links:**
   - Standalone 3D Map HTML: `http://localhost:3005/maps/<slug>/<slug>-3d-map.html`
   - Next.js `/embed` Engine URL: `http://localhost:3005/embed?src=/maps/<slug>.<ext>&title=...&mode=...`
2. **Universal `<three-d-map>` Embed Snippet** (for WordPress, Webflow, Shopify, Wix, plain HTML, Vue, React).
3. **Next.js Non-Blocking Component** (`<slug>-NextJsComponent.tsx`).
