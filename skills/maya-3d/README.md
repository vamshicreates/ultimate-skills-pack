# Maya 3D Codex Skill

A reusable Codex skill for creating, editing, and checking Autodesk Maya projects from reference images or written briefs. It guides Codex through image analysis, procedural Maya Python scene construction, project organization, materials, cameras, preview rendering, and handoff of an editable native scene.

## What it provides

- Image-to-scene workflow with explicit handling of hidden geometry and scale assumptions
- Dimension-aware modeling that separates pixel resolution from physical measurements
- A reusable `dimension_spec.json` template for units, anchors, tolerances, and measurement provenance
- A shared `scene_spec.json` contract for semantic parts, primitive or profile construction, anchors, connections, symmetry, and assumptions
- A Three.js preliminary blockout generator and final GLB reviewer with structural validation, part visibility, selection, wireframe, edge overlays, reference-image comparison, and dimension checks
- Cross-platform `mayapy` discovery for Windows and macOS
- Reusable Maya scene-job templates, including a specification-driven blockout builder
- Native `.ma` or `.mb` scene verification by reopening the generated scene
- Checks for renderable meshes and missing or external image assets
- Guidance for Arnold licensing, Maya projects, and common interchange formats

Autodesk Maya must be installed and licensed on the machine that creates or verifies a Maya scene. This repository does not install Maya or a Maya plug-in.

## Install

Copy this repository to your Codex skills directory:

- macOS: `${CODEX_HOME:-$HOME/.codex}/skills/maya-3d`
- Windows: `%CODEX_HOME%\skills\maya-3d`, or `%USERPROFILE%\.codex\skills\maya-3d` when `CODEX_HOME` is unset

Start a new Codex chat and invoke the skill with `$maya-3d`, attaching a reference image or describing the Maya project you want.

See [INSTALL.md](INSTALL.md) for platform notes.

## Check the Maya connection

From the repository directory, run:

```bash
python scripts/maya_runner.py --probe
```

To generate and validate the included sample scene:

```bash
python scripts/maya_runner.py \
  --job assets/scene_job_template.py \
  --project ./sample-project
```

On Windows, use `py -3` or `python` according to your Python installation. If Maya is installed in a custom location, pass `--mayapy PATH` or set `MAYA_PYTHON_EXECUTABLE`.

## Repository layout

```text
maya-3d/
├── SKILL.md
├── INSTALL.md
├── agents/openai.yaml
├── assets/dimension_spec_template.json
├── assets/scene_spec_template.json
├── assets/scene_job_from_spec.py
├── assets/scene_job_template.py
├── references/
│   ├── dimensions-and-scale.md
│   ├── image-to-scene.md
│   ├── platform-and-rendering.md
│   ├── scene-specification.md
│   └── threejs-review.md
├── viewer/
│   ├── index.html
│   ├── package.json
│   └── src/
└── scripts/maya_runner.py
```

## Specification-first hybrid workflow

1. Analyze the reference image and write `dimension_spec.json` plus `scene_spec.json`.
2. Validate the scene specification:

```bash
python scripts/validate_scene_spec.py PATH_TO_PROJECT/scene_spec.json
```

3. Generate and approve the structural Three.js blockout.
4. Build the editable Maya scene from the same specifications.
5. Export GLB from Maya and repeat the Three.js checks for final QA.

## Three.js blockout and review application

The repository includes a browser review tool powered by the official Three.js package. From `viewer/`, run:

```bash
npm install
npm run dev
```

Load `scene_spec.json` to generate a blockout from boxes, cylinders, spheres, tubes, and extruded profiles. Then load the project's `dimension_spec.json` and optional reference image. The viewer checks required parts, curve endpoint anchors, connections, symmetry, world-space dimensions, and expected-versus-actual size. It can export the approved blockout as GLB for Maya reference.

After Maya production, load the exported GLB with the same specifications to repeat the checks. Maya remains the authoritative editable scene.

## Validation status

The Python files, scene-specification validator, Three.js generator tests, production browser bundle, and skill metadata are checked in this repository. Native Maya scene and render validation require an installed Maya environment with a valid license.
