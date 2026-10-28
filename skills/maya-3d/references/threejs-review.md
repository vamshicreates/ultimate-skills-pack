# Three.js blockout and review workflow

Three.js is pinned in `viewer/` from the official `mrdoob/three.js` project. It serves two controlled roles: preliminary structural blockout before detailed Maya work and final inspection after Maya exports GLB. Image analysis and the shared specifications provide the design intent.

## Preliminary blockout

1. Complete and validate `dimension_spec.json` and `scene_spec.json`.
2. From `viewer/`, run `npm install` and `npm run dev`.
3. Load `scene_spec.json`. The viewer constructs supported primitives and curves at glTF meter scale.
4. Load `dimension_spec.json` and the reference image.
5. Resolve failed required-part, endpoint-anchor, connection, symmetry, and dimension checks. Inspect the silhouette from the reference camera and at least one secondary angle.
6. Export the approved blockout GLB when it helps Maya layout. Retain the specifications as the procedural authority.

The preliminary blockout is successful when the component inventory, major proportions, curve endpoints, and attachment relationships are approved. It is not expected to have production topology, final UVs, or final materials.

## Maya production

Generate the Maya scene from the same specifications. Use `assets/scene_job_from_spec.py` as a starting point for compatible primitives, then replace or refine blockout geometry with purpose-built Maya operations. Save the editable `.ma` or `.mb` before interchange export.

Do not make the imported GLB the only source of a production asset. glTF commonly contains triangulated geometry and may introduce transform wrappers. Map corrections to semantic part names and update the procedural generator.

## Final review

1. Export a self-contained GLB from Maya with semantic names and meter scale.
2. Validate the GLB with the Khronos glTF Validator when available.
3. Load the final GLB, the same two specifications, and the reference image in the viewer.
4. Use part visibility, selection, bounding boxes, wireframe, and hard-edge overlays to inspect completeness, topology symptoms, silhouette, scale, and attachment quality.
5. Correct failures in the Maya generator, rebuild the native scene, and repeat the export and review.

## Interpret results

- A missing named part means the scene specification or Maya generator is incomplete.
- A tube endpoint outside its anchor tolerance means the generating curve or transform is wrong.
- A connection failure means declared parts are separated beyond their allowed world-space gap.
- A symmetry failure means mirrored part centers do not agree after reflection across the declared axis.
- Correct structure with a wrong overall bound usually indicates a scale, axis, root-transform, or exporter problem.
- A silhouette mismatch with correct dimensions usually points to camera calibration, curvature, or part shape.
- Wireframe and edge views can reveal insufficient bevel segments, unexpected triangulation, disconnected shells, and missing support loops. Confirm topology in Maya.

## Sources

- [Official Three.js repository](https://github.com/mrdoob/three.js)
- [Three.js GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html)
- [Three.js GLTFExporter](https://threejs.org/docs/pages/GLTFExporter.html)
- [Three.js OrbitControls](https://threejs.org/docs/pages/OrbitControls.html)
- [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator)
