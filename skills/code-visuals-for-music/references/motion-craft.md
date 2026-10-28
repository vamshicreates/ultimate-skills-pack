# Motion craft and evidence

## Select a construction method per shot

| Intent | Useful construction | Evidence needed |
|---|---|---|
| Flowing musical line | SVG/Canvas curve with moving samples | Continuity, thickness, rhythm |
| Line becomes an object | Matched path topology or authored in-between drawings | Shape readability through the transformation |
| Running/jumping actor | Rig or coherent authored cels, grounded trajectory | Contacts, weight transfer, silhouette, landing |
| Detailed painted world | Separated plates with masks and independent motion | No duplicated subjects or stretching of embedded objects |
| Speaking portrait | Layered facial poses, gestures, viseme timing where available | Eye focus, pauses, consistent face and handset |
| Depth travel | Staged foreground/middle/background and occlusion | Perspective, scale, overlap and a legible destination |

## Character invariants

Keep anatomy, costume, face, and line style consistent across cels. Generated sprite sheets need inspection; their rows are not necessarily animation order. Align hips/root and feet where appropriate, not just the head. Use explicit metadata for pivot, planted-foot contact, bounds, and playback order.

A planted foot stays attached to its surface during contact. The pelvis carries weight; the airborne phase changes the trajectory. Test a run in place and on the actual path. If contacts fail, repair anchors/poses or use a better technique before adding glow and camera movement.

Use anticipation, action, recovery, and secondary movement. Vary gaze, posture, and intent with the story. Repeated cels can support locomotion, but a repeating loop cannot carry every emotional moment.

## Preserve the concept

Compare rendered frames with the chosen reference at equal size. Check framing, proportions, line density, color relationships, edge quality, and depth. A familiar palette alone does not establish a match.

Extract background plates without baked-in actors or duplicates of paths that will be animated. Do not mesh-warp an entire painting when only clouds or cloth should move. Keep masks, overscan, and edges clean throughout the full motion range.

Design a small set of motivated transitions: follow a path into the next space, match a shape, reveal through an eye, or carry a gesture across the cut. Repeated zooms and crossfades are not substitutes for the requested transformations.

## Proof review

Inspect at normal playback speed and slow/frame-step speed. Sample stills alone can miss jerks, accidental pose swaps, and text that flashes too briefly.

For each proof, record pass/fail/revise with an artifact and timecode:

- **Reference fidelity:** recognizably the intended world and cast.
- **Action:** the viewer can identify what changed and why.
- **Motion:** contacts, silhouettes, continuity, weight, and transitions hold up.
- **Music:** specific accents and pacing align; speech remains understandable.
- **Text:** correct display language, readable duration, placement, and no collision.
- **Technical:** output duration, resolution, audio, and decoding are correct.

Fix the failed dimension directly. More particles do not fix character acting; stronger bloom does not fix drawing quality; sharper encoding does not fix a weak story. A helper's technical pass never overrides a user's visual rejection.
