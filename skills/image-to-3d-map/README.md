# Image-to-3D-Map Skill (`image-to-3d-map`)

Turn any dropped 2D map image (**Illustrated Campus/Venue Map**, **Architectural Floor Plan**, **Topographical Terrain Map**, or **Real Estate Site Plan**) into an interactive, mobile- and desktop-ready **Next.js + Three.js 3D Map** with **0ms host page load blocking** and **1-line universal embeddability** (`<three-d-map>`).

## Quick CLI Execution

```bash
node .agents/skills/image-to-3d-map/scripts/build_3d_map.mjs \
  --image "/path/to/your-map.png" \
  --mode "auto" \
  --title "Interactive 3D Map"
```

## Outputs Generated Automatically
1. **Standalone 3D Map Bundle (`<slug>-3d-map.html`):** 100% self-contained single-file 3D WebGL map with off-thread heightfield/wall reconstruction and interactive 3D pins.
2. **Next.js Non-Blocking Component (`<slug>-NextJsComponent.tsx`):** Uses `next/dynamic` (`{ ssr: false }`), `IntersectionObserver`, and `requestIdleCallback`.
3. **Universal 1-Line Embed (`<slug>-embed-snippet.html`):** Works in WordPress, Webflow, Shopify, Wix, plain HTML, Vue, Angular, or React.
