# Deliverable format

## Project structure

```text
production-breakdown/
|-- script-manifest.json
|-- production-data.json
|-- master-production-breakdown.md
|-- master-scene-summary.csv
|-- continuity-report.md
`-- scenes/
    |-- SC-001/
    |   |-- storyboard-3x3.png
    |   `-- breakdown.md
    `-- SC-002/
        |-- storyboard-3x3.png
        `-- breakdown.md
```

Do not create a public storyboard-plan file. If working notes are needed, keep them as internal run state or inside structured generation metadata that is not presented as a deliverable.

## Scene document order

```markdown
# SC-001 — INT. LOCATION — NIGHT

**Printed scene:** 1  
**Source pages:** 1–3  
**Script time:** Night

![SC-001 nine-cell storyboard](storyboard-3x3.png)

## Scene summary

## Dramatic purpose

## Production breakdown

## Characters

## Location and set

## Costume, makeup, hair, and props

## Camera, lighting, sound, and technical requirements

## Action, stunts, and safety

## Continuity dependencies

## Production risks and open questions
```

The image must be the first substantial scene content after its identifying metadata.

## Master scene summary CSV

Use one row per scene with, at minimum:

```text
scene_id,printed_scene_number,slugline,source_pages,int_ext,location,sub_location,script_time,characters,extras,key_requirements,continuity_flags,completion_state
```

Use a consistent separator inside multi-value cells and quote values containing commas.

## Structured data

`production-data.json` is the source of truth for resuming work. Include:

- source-script identity;
- declared and indexed scene counts;
- scene order;
- extraction warnings;
- shared character, costume, location, prop, vehicle, and continuity bibles;
- per-scene facts, inferences, questions, and completion state;
- storyboard path and review state; and
- unresolved cross-scene dependencies.

Keep scene IDs and file paths stable when adding later batches.
