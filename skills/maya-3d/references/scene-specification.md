# Shared scene specification

`scene_spec.json` is the structural contract between image analysis, the Three.js blockout, and the Maya generator. Copy `assets/scene_spec_template.json` into each project and replace the example with evidence from the supplied references.

## Coordinate and unit rules

- Use a right-handed coordinate system with Y up and -Z forward so the Three.js blockout matches glTF conventions.
- Declare `units` as `mm`, `cm`, `m`, `in`, or `ft`. Three.js converts values to meters; the Maya template converts values to centimeters.
- Positions and path points are local to their part. Anchors are project-world coordinates.
- Rotations are XYZ Euler angles in degrees.
- Keep physical evidence and confidence in `dimension_spec.json`; use `scene_spec.json` for construction and structural relationships.

## Supported blockout parts

| Type | Required fields | Purpose |
|---|---|---|
| `box` | `size: [x, y, z]` | Primary masses and panels |
| `cylinder` | `radius`, `height` | Wheels, posts, shafts, round bodies |
| `sphere` | `radius` | Rounded joints and approximate volumes |
| `tube` | `path`, `radius` | Rails, roof curves, cables, trim, handles |
| `extrude` | `profile`, `depth` | Profile-driven panels and prismatic shapes |

Every part requires a unique Maya-safe `name`. Use letters, numbers, and underscores, beginning with a letter or underscore. Add `required: true` for every component whose absence would change identity, silhouette, function, or connection integrity.

## Structural constraints

- Define world-space `anchors` for important attachment points. Bind a tube with `startAnchor` and `endAnchor` so its endpoints are tested.
- Add `connections` with `from`, `to`, and `maxGap` to detect floating parts using world-space bounds.
- Add `symmetryPairs` with `left`, `right`, `axis`, and optional `tolerance` to check mirrored placement.
- Keep tolerances appropriate to the intended use. Visualization assets can use broader tolerances than manufacturing references.
- Record every unobserved or estimated construction decision in `assumptions`.

## Validate and consume

Run:

```bash
python scripts/validate_scene_spec.py PROJECT/scene_spec.json
```

The command returns nonzero when the structure cannot be generated safely. After validation, load the specification in the Three.js viewer. The viewer builds the blockout and reports required-part, endpoint-anchor, connection, symmetry, and overall-dimension results.

The Maya job must read the same specifications. `assets/scene_job_from_spec.py` provides a starting implementation for the supported blockout vocabulary. Production assets commonly need a customized job for subdivision topology, NURBS surfaces, booleans, UVs, rigging, and renderer-specific shading.

## Revision discipline

When review finds a missing or disconnected component, revise `scene_spec.json` first, regenerate the blockout, and then rebuild Maya. If the structural specification is correct but production topology is wrong, update the Maya generator without changing the intended measurements or anchors.
