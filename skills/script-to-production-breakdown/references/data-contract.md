# Breakdown data contract — version 1

Use UTF-8 JSON. The canonical file is `breakdown.json`; CSV reports are derived views. Do not put multiple films or drafts in one breakdown. Unknown scalar values use `null`; unknown counts never use zero. Arrays are empty only when no records have been identified, with the scene's assessment state supplying context.

## Root structure

```json
{
  "schema_version": "1.0",
  "film": {"title": "Example", "revision": "Draft 3", "lock_status": "confirmed"},
  "source": {
    "filename": "screenplay.pdf",
    "sha256": "64-character lowercase SHA-256",
    "extraction_method": "PDF text extraction",
    "languages": ["Telugu", "English"],
    "units": [{"id": "PDF-001", "locator": "PDF page 1", "readable": true, "reviewed": true}],
    "warnings": []
  },
  "scope": {"mode": "full", "scene_ids": [], "categories": ["all"]},
  "scenes": [],
  "entities": [],
  "requirements": [],
  "continuity": [],
  "questions": []
}
```

`lock_status`: `confirmed` or `unconfirmed`. `scope.mode`: `full`, `selected`, or `sample`. For `selected` and `sample`, list requested scene IDs in `scope.scene_ids`. `full` addresses every inventoried scene. `scope.categories` is `["all"]` or a nonempty list of category keys. Index all supplied source material even if only selected scenes need departmental extraction. If the user supplies only an excerpt, mark `scope.mode: selected`, describe the excerpt in source warnings, and do not claim whole-film coverage.

Every evidence object has `unit_id`, `anchor`, and `excerpt`, for example:

```json
{"unit_id": "PDF-001", "anchor": "PDF page 1, scene 12A, action paragraph 2", "excerpt": "Ravi picks up the torn letter."}
```

Keep excerpts short and exact. Evidence points into the supplied screenplay; separate user reference notes belong in `notes`. The source units must cover all screenplay pages or text sections, including any unreadable ones.

## Categories

`locations`, `cast`, `costume`, `props`, `vehicles`, `animals`, `background`, `special_equipment`, `vfx`, `stunts`, `makeup_hair`, `art_set`, `sound`, `weather`, `practical_effects`, `lighting`.

## Scenes

Required fields:

- `id`: stable internal ID, e.g. `SC-001`.
- `printed_number`: original number or `null`.
- `slugline`: original heading or a labelled description for unheaded material.
- `source_unit_ids`: nonempty list of source unit IDs.
- `int_ext`: `INT`, `EXT`, `INT/EXT`, `EXT/INT`, or `UNKNOWN`.
- `script_time`: original wording or `null`.
- `summary`: brief factual account.
- `category_status`: object with every category key and one of `present`, `none_identified`, `not_assessed`.

Optional: `story_day`, `parent_scene_id`, `notes`. Array order is script order, independent of numeric ID. Omitted printed scenes may be documented in source warnings rather than created as active scenes. Each scene entry represents one identified boundary; related montage/intercut segments can point to their parent without duplicating requirements.

## Entities

Required: `id`, `category`, `name`, `aliases` (array). Example:

```json
{"id": "E-001", "category": "cast", "name": "రవి", "aliases": ["RAVI"], "actor_name": null}
```

Use one entity for a confidently matched recurring character, prop, costume look, story location, or other requirement. Create a separate entity when identity is uncertain and add a review question. `actor_name` is optional and only populated from a supplied mapping. An entity name is not evidence of its appearance in a scene; requirements provide that link. Names need not be globally unique.

## Requirements

Each record links one scene to one requirement:

```json
{
  "id": "R-001",
  "scene_id": "SC-001",
  "entity_id": "E-001",
  "category": "cast",
  "description": "Ravi speaks and handles the letter.",
  "status": "explicit",
  "evidence": [{"unit_id": "PDF-001", "anchor": "PDF page 1, scene 12A", "excerpt": "RAVI: Give me the letter."}],
  "rationale": null,
  "quantity": null,
  "quantity_unit": null,
  "participation": "visible_speaking",
  "subject_entity_id": null,
  "notes": null
}
```

Required fields: `id`, `scene_id`, `entity_id`, `category`, `description`, `status`, `evidence`, `quantity`, `quantity_unit`. `entity_id` can be `null` for a requirement that has not been resolved to a reusable entity. `status`: `explicit`, `inferred`, or `question`. All require nonempty evidence; an inference also requires a nonempty `rationale`.

`quantity` is a nonnegative number or `null`; a known quantity requires a unit. Do not estimate a precise crowd or duplicate count without marking it inferred and explaining it. `subject_entity_id` can link a costume, injury, or carried prop to its character. An actor's dialogue line count is not an estimate of shoot duration.

Cast requirements require `participation`: `visible_speaking`, `visible_non_speaking`, `off_screen_voice`, `voice_over`, `referenced_only`, or `uncertain`. Referenced-only participation must remain distinguishable in reports and downstream cast counts.

## Continuity

Required: `id`, `scene_ids` (at least two distinct valid scenes), `element`, `dependency`, `department`, `status`, `evidence`. Optional `entity_id`, `rationale`, `notes`. The dependency describes the match or state transition, including its direction when known. Use the same evidence/status rules as requirements. If only one scene is supplied, place its unresolved cross-scene match in questions rather than inventing another scene ID.

## Questions

Required: `id`, `scene_ids` (valid IDs or empty for a film-wide issue), `department`, `question`, `evidence` (may be empty for a source/extraction problem). Optional `requirement_id`. Questions are unresolved, not an approval log.

## Completion and counting

The helper reports `complete_for_requested_scope` only when all supplied screenplay units are readable and reviewed and all requested categories in requested scenes are assessed. This is extraction coverage, not department approval. Source warnings and review questions remain visible even when extraction coverage is complete.

A `present` category needs at least one corresponding requirement; `none_identified` and `not_assessed` must not have requirement records. A partial run can preserve unassessed scenes. Empty scene inventories are invalid. Unknown source pages make the result partial even if every readable scene has been assessed.

Report unique entities and requirement appearances separately. Separate referenced-only cast from participating cast. Story-location counts are not booked-venue counts; scene counts are not shoot days; scripted VFX requirements do not establish VFX shot count or duration.
