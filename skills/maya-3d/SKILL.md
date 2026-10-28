---
name: maya-3d
description: Create, edit, and verify Autodesk Maya 3D projects from reference images or briefs, delivering native editable scenes and project assets on Windows or macOS.
---

# Maya 3D production

Use this skill when the requested deliverable is a Maya scene, model, material setup, animation, lighting setup, or render. It does not run AutoCAD. An image is visual evidence, not a complete 3D specification: infer hidden surfaces and dimensions conservatively and record consequential assumptions.

## Start each job

1. Inspect every supplied reference image at original resolution where possible. Record its pixel width, pixel height, and aspect ratio; then look for dimension labels, scale bars, technical drawing annotations, known-size objects, or dimensions stated by the user. Identify the main forms, silhouette, relative scale, materials, camera angle, lighting, text/logos, and any requested animation or output format. Preserve distinctive design details. Ask only for a missing choice that materially changes the model; otherwise choose a plausible interpretation and proceed.
2. Check the current OS, installed Maya version, available `mayapy`, render plug-ins, and project output location. Run `python scripts/maya_runner.py --probe` from this skill folder, or provide `--mayapy` explicitly. Maya must be installed and licensed to execute and verify Maya code. Do not claim a scene was tested in Maya if it was only syntax checked.
3. Read [references/image-to-scene.md](references/image-to-scene.md) for image-based work and [references/dimensions-and-scale.md](references/dimensions-and-scale.md) whenever an image, drawing, measurement, or Three.js handoff is involved. Read [references/scene-specification.md](references/scene-specification.md) before creating a multi-part image-based model. Read [references/platform-and-rendering.md](references/platform-and-rendering.md) when choosing execution, dependencies, rendering, or interchange formats. Check Autodesk documentation for the installed Maya version before using an unfamiliar or version-specific command.
4. Read [references/threejs-review.md](references/threejs-review.md) for both the preliminary blockout and final exported-model review.

## Create the shared specification

- Image analysis is the ideation stage. Before generating geometry, convert the observed design into `dimension_spec.json` and `scene_spec.json` using the templates in `assets/`. The scene specification is the shared contract for Three.js and Maya; Three.js does not independently infer a 3D design from pixels.
- Give every distinctive or structurally necessary component a Maya-safe semantic name. Mark important components `required`, including curves, trim, connectors, and small silhouette-defining parts that a broad blockout might otherwise omit.
- Define primitive or profile type, local dimensions, transform, material, attachment anchors, curve endpoints, connection tolerances, and symmetry pairs. Keep authoritative measurements separate from estimates and record confidence and assumptions in the dimension specification.
- Run `python scripts/validate_scene_spec.py PATH_TO_SCENE_SPEC.json`. Fix every schema error before generating Three.js or Maya geometry.

## Generate and approve the Three.js blockout

- For an image-based model with multiple parts, curved profiles, or attachment relationships, load `scene_spec.json` in `viewer/` before detailed Maya work. The viewer generates a meter-scale blockout from boxes, cylinders, spheres, tubes, and extruded profiles.
- Load `dimension_spec.json` and the reference image. Check required-part presence, overall dimensions, curve endpoint anchors, declared connections, symmetry, silhouette, and camera framing. Resolve every failed structural check; explicitly adjudicate warnings.
- Export the approved blockout GLB when a visual guide is useful in Maya. Treat it as a reference or interchange artifact. The shared specifications remain authoritative and prevent GLB triangulation or transform wrappers from becoming the procedural source.

## Build the deliverable

- Work in a dedicated Maya project. Keep `scenes/`, `sourceimages/`, `images/`, and the generating Python job together. Preserve the user's originals; copy reference images into `sourceimages/` when the scene depends on them. Use project-relative asset paths where Maya supports them.
- Create `dimension_spec.json` from `assets/dimension_spec_template.json` and `scene_spec.json` from `assets/scene_spec_template.json` before modeling. Treat pixel dimensions as camera and aspect-ratio evidence only. Use explicit real-world measurements as authoritative; mark estimates and their confidence. Never silently interpret pixels as centimeters, inches, or meters.
- Write a reproducible Python job exposing `build(project_dir: pathlib.Path) -> pathlib.Path`. Generate actual editable Maya geometry and scene nodes using `maya.cmds` (or the Maya Python API when needed). Make that job read the same scene and dimension specifications used by the Three.js blockout. Start from `assets/scene_job_from_spec.py` when its primitive vocabulary fits, or implement a purpose-built generator for production topology. Do not substitute a flat image plane or an imported triangulated blockout for the requested editable model.
- Set Maya linear units deliberately and drive major dimensions, curve control points, profiles, offsets, attachment anchors, and symmetry from the dimension specification. Avoid arbitrary literals for a measured component. When exporting glTF/GLB for Three.js, convert linear measurements to meters and retain semantic node names.
- Save the native source as `.ma` or `.mb` before any interchange export. `.ma` is a useful default for inspectable procedural scenes; `.mb` is appropriate when scene size or features warrant it. Export FBX, USD, OBJ, or Alembic only when the user asks or the downstream pipeline needs it, and check what each format preserves.
- After Maya production, export a self-contained GLB with semantic node names and meter scale. Copy the GLB, `dimension_spec.json`, and `scene_spec.json` into the deliverable project; use `viewer/` again to inspect hierarchy, visibility, wireframe, hard edges, bounds, required parts, connections, anchors, symmetry, and reference-image alignment. The native Maya scene remains the editable source of truth.
- Create materials, UVs/textures, lights, and cameras to the requested finish. Render a preview when Maya and the necessary renderer are available. Match the reference from at least the principal camera; inspect another view for depth, intersections, and unfinished backsides.
- Keep all generated files in the chosen project; avoid modifying the user's Maya preferences, global scripts, plug-in directories, or existing scenes. Never install Maya, plug-ins, or packages without a concrete need and authorization.

## Execute and verify

Run `python scripts/maya_runner.py --job PATH_TO_JOB.py --project PATH_TO_PROJECT` with normal Python. The launcher finds the installed `mayapy`, initializes Maya, calls `build(project_dir)`, checks the saved native scene, reopens it, and writes `maya_report.json`. See `assets/scene_job_template.py` for the job interface. On Windows, use `py -3` or `python` if needed. For Maya GUI use, load the job in a Python Script Editor tab and call its `build(Path(...))`; do not initialize `maya.standalone` inside the GUI.

Inspect the saved scene and any render rather than treating a successful script exit as visual approval. Check geometry counts, missing textures, relative paths, camera framing, materials, scale, render settings, and any warnings in `maya_report.json`. Compare measured scene extents and named anchor distances against `dimension_spec.json` within the declared tolerances. If the current machine lacks Maya, still deliver the source job and project assets, run ordinary Python syntax checks, and state precisely that native scene creation and render verification remain pending on a Maya machine.

Run `npm install` once in `viewer/`, then `npm run dev` for blockout generation and interactive review or `npm run build` for a static bundle. First load the shared scene specification to approve the preliminary blockout. After Maya production, load the exported GLB while retaining the same specifications and repeat the checks. Send corrections back to the named procedural Maya generator rather than editing the GLB as the master asset.

## Hand-off

Return links to the Maya project root, `dimension_spec.json`, `scene_spec.json`, approved blockout GLB, native scene, generating script, final GLB, preview, validation results, and Maya report when each exists. Briefly state the Maya version used, authoritative dimensions, estimated dimensions and confidence, what the reference did not reveal, and any remaining technical limitation. Never describe a script, blockout, or preview image alone as a completed Maya project.
