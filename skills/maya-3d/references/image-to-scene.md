# Reference image to editable Maya scene

## Interpret the image

- Separate visible facts from inferred geometry. Follow [dimensions-and-scale.md](dimensions-and-scale.md) to record raster size, extract explicit measurements, establish units, and mark estimates. A single photograph cannot establish unseen surfaces or exact measurements.
- Build a part list before modeling: primary masses, cutouts, trim, repeated components, transparent parts, decals/text, ground or environment, and optional moving parts. Encode that inventory, its construction types, anchors, connections, and symmetry in `scene_spec.json`. Mark silhouette-defining curves and trim as required parts. Prioritize silhouette and proportion, then large color regions, then detail.
- Determine whether the object needs a clean production mesh, concept visualization, riggable topology, or 3D-print-ready geometry. These require different topology and verification. If unspecified, make an editable visualization mesh rather than asserting manufacturing accuracy.
- Use an image plane or camera reference only as a guide. Keep it separate from renderable geometry; do not count the plane as the model. Autodesk documents `cmds.imagePlane(fileName=..., camera=...)` and image plane placement in the Maya command and lighting help.

## Construct

- Generate and approve the Three.js structural blockout from `scene_spec.json` before detailed Maya work. Then build Maya from the same specification, using the blockout GLB as an optional visual guide. Keep object parts distinct and named; use groups such as `GEO`, `LOOK`, `LIGHTS`, and `CAMERAS` when useful.
- Move from broad shapes to bevels, openings, seams, and repeated details. Use instances or procedural loops for repetition. Use booleans only where they give clean, maintainable topology; inspect their result.
- Make UVs and textures when they affect the requested appearance. Use shader node networks available in the installed Maya version. Store texture images under `sourceimages/`; inspect actual file node paths after saving and reopening.
- Set color management, material response, lighting, focal length, camera composition, and render size deliberately. A viewport screenshot is useful for a quick check, but a final preview should come from the chosen renderer if available.

## Acceptance checks

1. Native `.ma` or `.mb` opens in the target Maya version with nonempty renderable geometry and no missing required assets.
2. Principal view reproduces the important silhouette, color layout, and design features of the input. Side or rear view contains plausible modeled depth rather than a camera-facing facade.
3. Topology and shading have no obvious holes, flipped normals, accidental intersections, or broken UVs for the requested use.
4. Project contains the generating job, reference assets, saved scene, and a preview or a clear reason why rendering was unavailable.
5. Any hidden geometry, dimensions, typography, and material properties invented from an ambiguous image are documented in the delivery note.
6. Scene bounds, named anchor distances, curve endpoints, declared connections, and symmetry pairs agree with `dimension_spec.json` and `scene_spec.json` within their stated tolerances.
