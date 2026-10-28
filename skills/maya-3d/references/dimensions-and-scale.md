# Dimensions, scale, and camera matching

Use this procedure before building geometry from an image or preparing a Three.js review asset.

## Classify the available evidence

Record each measurement with its source and confidence. Use this priority order:

1. **User-supplied physical measurement** — authoritative unless measurements conflict.
2. **Dimension printed in a drawing or visible label** — authoritative after confirming the unit and the endpoints of the dimension line.
3. **Scale bar or drawing scale** — reliable only when the image has not been resized non-uniformly and the relevant plane can be rectified.
4. **Known-size reference object** — an estimate; state the assumed reference size.
5. **Proportional inference from another measured part** — an estimate derived from a documented ratio.
6. **Visual estimate only** — low confidence and unsuitable for manufacturing claims.

Always record raster width, raster height, and aspect ratio. These describe image sampling and camera framing; they do not provide physical scale. Never treat, for example, a 1920-pixel-wide image as a 1920-centimeter object.

## Perspective limits

A single pixel-to-unit scale is valid only for an orthographic drawing or for points on the same rectified plane. In a perspective photograph, apparent size changes with depth. If dimensions lie on a planar face, use its corners or vanishing directions to estimate a homography before measuring other features on that plane. Do not propagate that scale to features at a different depth.

Multiple views improve reconstruction. Prefer front, side, rear, top, or a turntable sequence with at least one shared known measurement. When only one view exists, lock the measured visible dimensions and mark depth and hidden geometry as estimates.

## Write the dimension specification

Copy `assets/dimension_spec_template.json` into the Maya project as `dimension_spec.json`. Include:

- source image pixel size and aspect ratio;
- Maya working unit and output unit;
- overall width, height, and depth when known;
- named measurements with endpoints or semantic anchors;
- symmetry pairs and attachment anchors;
- confidence and provenance for every inferred value;
- absolute or relative tolerance appropriate to the intended use.

Conflicting authoritative dimensions require clarification. Missing dimensions do not block a visualization model: select a plausible scale, mark it estimated, and keep all dependent values parametric so one later measurement can rescale or rebuild the model.

Create `scene_spec.json` alongside it from `assets/scene_spec_template.json`. Store construction geometry, semantic part names, local transforms, curve paths, attachment anchors, connections, and symmetry rules there. Both the preliminary Three.js blockout and Maya generator must consume these shared values rather than maintaining separate measurements.

## Drive Maya from measurements

- Set the Maya working unit explicitly, commonly centimeters, with `cmds.currentUnit(linear="cm")`.
- Store physical values in a parameters object and derive subordinate measurements from named values. Avoid scattered numeric literals.
- Place component origins and attachment anchors in world or documented local coordinates. Validate curve endpoints and mating surfaces against those anchors.
- For a measured curve, store its endpoints, intermediate control points or offsets, profile dimensions, and continuity requirement. Use a NURBS curve with Sweep Mesh for trim or rails and Loft for surfaces defined by multiple profiles.
- Distinguish geometric contact from welded topology. Separate manufactured parts may touch within tolerance without sharing vertices.

## Three.js and glTF handoff

glTF linear distances are meters. Convert a centimeter-based Maya scene by the exporter or with an explicit `0.01` scale conversion, then verify the loaded root and child world-space bounding boxes. Preserve semantic node names so the Three.js reviewer can map a selected mesh back to the Maya generator.

Use the source image aspect ratio for the comparison camera. For a perspective reference, match field of view or focal length and camera pose before evaluating silhouettes; image resolution alone cannot recover focal length or object depth. Keep the review canvas aspect equal to the source aspect to prevent stretching.

Recommended review metrics are:

- overall and per-part bounding-box dimensions;
- distances between named anchors;
- symmetry-plane deviation;
- silhouette intersection over union;
- contour distance;
- keypoint reprojection error;
- required-part presence and attachment status.

The Khronos glTF 2.0 specification defines a right-handed coordinate system with meters as its linear unit. Three.js `PerspectiveCamera` uses vertical field of view and width-to-height aspect ratio, so camera matching needs both the image aspect and a calibrated or estimated field of view.

## Sources

- [glTF 2.0 coordinate system and units](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#coordinate-system-and-units)
- [Three.js PerspectiveCamera](https://threejs.org/docs/pages/PerspectiveCamera.html)
- [Three.js responsive rendering and aspect ratio](https://threejs.org/manual/pages/responsive.html)
- [Maya Sweep Mesh](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-Modeling/files/GUID-1E33DECF-6D99-4B18-A5C7-403BCFF5E023.htm)
- [Maya Loft options](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-Modeling/files/GUID-F0E442D3-4F11-4D6D-B1D9-2A53D4CEED2A.htm)
