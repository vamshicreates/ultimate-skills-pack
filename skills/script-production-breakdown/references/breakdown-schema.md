# Scene breakdown schema

Use these fields for each scene. Omit categories that are genuinely irrelevant, but do not omit a relevant requirement merely because it is difficult to source.

## Scene identity

| Field | Requirement |
|---|---|
| `scene_id` | Stable ID such as `SC-001` |
| `printed_scene_number` | Screenplay number when present |
| `slugline` | Full source heading |
| `source_pages` | Printed or extracted page range |
| `int_ext` | `INT`, `EXT`, `INT/EXT`, `EXT/INT`, `I/E`, or unresolved |
| `location` | Primary location |
| `sub_location` | Specific room, area, vehicle, or zone |
| `script_time` | Day, night, dawn, dusk, continuous, later, or source wording |
| `recommended_shoot_condition` | Production recommendation, clearly labeled |
| `estimated_script_length` | Page-eighth estimate when reliable |

## Scene explanation

- **Factual summary:** What happens, without added interpretation.
- **Dramatic purpose:** What the scene establishes, changes, reveals, or resolves.
- **Production overview:** The few requirements most likely to determine schedule, department preparation, or risk.

## Department breakdown

| Category | Record |
|---|---|
| Cast | Speaking, featured, non-speaking, voice-only, and off-screen characters |
| Background | Extras, crowd scale, grouping, business, duplicates, and special casting |
| Costume | Outfit, changes, multiples, distressing, wet work, blood, doubles, continuity |
| Makeup and hair | Look, progression, prosthetics, injuries, dirt, sweat, ageing, reset needs |
| Props | Hand props, set props, consumables, breakaways, practical electronics |
| Hero props | Story-critical props requiring close-up or duplicate control |
| Vehicles | Picture vehicles, action vehicles, doubles, towing, process requirements |
| Animals | Species, number, behavior, trainer, welfare, doubles, restrictions |
| Art and set | Construction, dressing, signage, graphics, practicals, ageing, damage, resets |
| Special effects | Atmospheric, mechanical, breakaway, fire, smoke, rain, wind, blood rigs |
| VFX | Removal, extension, compositing, environment, screen replacement, tracking needs |
| Camera and grip | Movement, rigging, constrained space, stabilization, specialty coverage |
| Lighting | Motivation, time of day, practicals, flicker, interactive light, continuity |
| Sound | Dialogue risks, room tone, wild tracks, effects, playback, music on set |
| Action and stunts | Choreography, falls, fights, driving, weapons, water, heights, doubles |
| Safety | Hazards, coordinator needs, controlled access, protective or medical measures |
| Weather | Scripted condition, continuity, practical method, cover-set implications |
| Special equipment | Cranes, dollies, drones, process trailer, rain tower, remote head, specialty rigs |

## Character table

For every character present, record:

- visible, off-screen, voice-only, or referenced;
- costume;
- makeup and hair;
- carried or handled props;
- physical and emotional condition relevant to performance or continuity; and
- arrival state and departure state.

## Continuity dependency

Each dependency must identify:

- the element being tracked;
- preceding and following scene IDs;
- the required match or change;
- the responsible department when evident; and
- unresolved timing or story-order questions.

## Evidence status

Tag material in structured data as:

- `explicit`: directly stated or visibly required by the screenplay;
- `inferred`: a production interpretation needed to execute the scene; or
- `question`: unresolved and requiring confirmation.

Do not tag an interpretation as `explicit` merely because it is likely.
