---
name: script-production-breakdown
description: Read a complete locked screenplay, inventory every scene, create production-ready scene breakdowns, and generate a nine-image 3x3 storyboard at the top of each scene package. Use when a script is attached or available locally and the user wants a pilot breakdown, production analysis, continuity report, or full scene-by-scene storyboard package.
---

# Script Production Breakdown

Turn a locked screenplay into a traceable production package. Read the complete script before interpreting individual scenes. Keep script facts distinct from production recommendations and unresolved questions.

## Choose the execution scope

Use one of these modes:

- **Pilot:** index the entire script, establish the continuity bibles, and finish two or three representative scenes. Use this by default when the user wants a sample before authorizing the complete screenplay.
- **Full:** finish every indexed scene and the master production summaries. Use this when the user explicitly requests the complete script.
- **Selected scenes:** finish only the user-named scenes while preserving the complete scene inventory and shared continuity data.

For a pilot, choose scenes that demonstrate different production demands: normally one performance/dialogue scene, one action or technically complex scene, and one visually atmospheric or continuity-heavy scene. Use the user's chosen scenes when provided. After delivering the pilot, stop with a resumable ledger and wait for the user to request the remaining scenes.

## Locate and validate the locked script

1. Prefer the script explicitly attached or named by the user. Otherwise, inspect the current project folder for PDF, DOCX, FDX, Fountain, or TXT screenplay candidates. `scripts/discover_script.py` can produce a ranked JSON inventory.
2. If several plausible locked revisions remain, ask which one is authoritative. Never combine revisions silently.
3. Extract and read the complete script, including title pages, scene headings, action, dialogue, parentheticals, transitions, montages, intercuts, inserts, and ending material.
4. For scanned or partially readable pages, use OCR where available and record uncertain passages. Do not treat extraction failure as an empty page or scene.
5. Record the source filename, revision label or date when present, format, page count, and extraction warnings in `script-manifest.json`.

## Inventory every scene

Identify headings such as `INT.`, `EXT.`, `INT./EXT.`, `EXT./INT.`, and `I/E.`. Preserve printed scene numbers separately and assign stable internal IDs in script order: `SC-001`, `SC-002`, and so on.

For every scene, record:

- source page or text range;
- full slugline;
- INT/EXT classification;
- location and sub-location;
- day, night, dawn, dusk, continuous, later, moving, or other modifier;
- characters present, including off-screen participants;
- a concise factual summary; and
- completion state: indexed, breakdown complete, storyboard complete, or reviewed.

Include opening or transitional material without a conventional slugline and flag ambiguous boundaries for review. Never call a package complete if indexed scenes remain unfinished.

## Build shared continuity bibles

Before generating storyboards, create internal bibles for recurring characters, costumes, makeup and injuries, hero props, vehicles, locations, sets, weather, story time, and visual style. Separate:

- facts stated by the screenplay;
- strong production inferences; and
- questions requiring human confirmation.

Track changes across scenes, including carried props, blood and dirt progression, costume changes, injuries, time-of-day transitions, screen geography, weather, vehicles, and set damage. Reuse approved character and location references throughout image generation.

## Produce each scene in the required order

Every finished scene must appear in this order:

1. scene ID, printed scene number when available, slugline, and source pages;
2. the finished 3x3 storyboard image;
3. scene summary and dramatic purpose;
4. complete production breakdown;
5. character table;
6. location and set requirements;
7. costume, makeup, props, sound, action, safety, and technical notes;
8. continuity dependencies; and
9. production risks and open questions.

The storyboard must appear before all narrative and production analysis so the reader receives the visual overview first. Follow the field definitions in [references/breakdown-schema.md](references/breakdown-schema.md).

## Generate the 3x3 storyboard

Create exactly one final 3x3 storyboard sheet for each finished scene. The nine images are sequential cells in the sheet, not nine required deliverable files. Do not publish a separate storyboard-plan document. Planning the nine beats is an internal generation step.

Map the scene into nine meaningful visual beats. Adapt the emphasis to the writing rather than forcing identical coverage on every scene. A useful default progression is:

1. location and geography;
2. character introduction or starting state;
3. first dramatic beat;
4. interaction or developing action;
5. reaction or relationship beat;
6. reveal or escalation;
7. critical insert, prop, or visual detail;
8. climax or decisive beat; and
9. ending image or transition.

When the scene contains fewer than nine major events, vary shot size, reaction, detail, blocking, and editorial emphasis without inventing story events. When it contains many events, select the nine beats that best communicate the complete scene.

Use the available image-generation capability and follow the installed image-generation guidance. Lock character identity, costume, location geography, props, time of day, lighting, aspect ratio, and art direction before generating scene sheets. Generate or edit source images internally if that improves consistency, but deliver the single 3x3 sheet unless the user asks for individual cells.

Keep generated art free of dialogue and dense typography. Add panel numbers and short captions outside the generated artwork during deterministic assembly so they remain legible. Inspect the finished sheet at delivery size. Regenerate or edit cells that contradict the script or continuity bible. Read [references/storyboard-guidelines.md](references/storyboard-guidelines.md) for visual and review rules.

## Write the production breakdown

Use concise production language. Cover every applicable department without filling irrelevant categories with invented requirements. For each item, identify whether it is directly stated, inferred for execution, or unresolved.

Required coverage includes:

- INT/EXT, location, set areas, scripted time, and recommended shoot condition;
- speaking characters, non-speaking characters, off-screen participants, extras, and crowds;
- costume, costume changes, makeup, hair, prosthetics, blood, dirt, and ageing;
- props, hero props, vehicles, animals, and special equipment;
- art direction, dressing, construction, graphics, practical effects, and resets;
- VFX, camera, rigging, playback, sound, weather, and environmental needs;
- action, fights, intimacy, stunts, choreography, hazards, and safety controls;
- continuity dependencies and scenes that must match; and
- production risks, missing information, and questions for department heads.

Do not convert creative interpretation into screenplay fact. Phrase recommendations as recommendations.

## Assemble the deliverables

Use the output structure in [references/deliverables.md](references/deliverables.md). Maintain:

- `script-manifest.json` for source and extraction data;
- `production-data.json` as the structured source of truth;
- `master-production-breakdown.md` for the readable package;
- `master-scene-summary.csv` for scheduling and filtering;
- `continuity-report.md` for cross-scene dependencies; and
- one folder per completed scene containing `storyboard-3x3.png` and `breakdown.md`.

In `master-production-breakdown.md`, embed each scene's storyboard immediately below its heading and before the breakdown. Keep filenames and scene IDs stable across resumed runs.

## Validate before delivery

Run:

```bash
python3 scripts/validate_project.py <production-breakdown-folder>
```

Then manually verify:

- the script was read through its final page;
- the declared scene count matches the inventory;
- every requested scene has one readable nine-cell storyboard;
- storyboards precede breakdown text in the master document;
- recurring characters, costumes, locations, props, injuries, weather, and time remain coherent;
- every production requirement is traceable to script text or marked as an inference;
- continuity links name the affected scene IDs; and
- incomplete, uncertain, or unrendered material is reported rather than hidden.

For a pilot, report the total indexed scene count, deliver the finished sample scenes, identify unresolved questions, and preserve the ledger for continuation.
