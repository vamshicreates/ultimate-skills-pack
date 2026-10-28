# Costume bible data contract — 1.0

UTF-8 JSON is the editable source of truth. Keep IDs stable across resumed runs. A missing value is `null`, not an invented fact. Records appear in script order unless a separate story-order field establishes chronology.

## Root and source

Required root keys: `schema_version` (`"1.0"`), `film`, `source`, `film_palette`, `characters`, `scenes`, `looks`, `states`, `appearances`, `continuity`, `assets`, `questions`.

`film`: `title`, `revision` (string or null), `design_status` (`proposed` or `approved`). Use approved only when the user has approved the represented design version.

`source`: `filename`, `sha256`, `scene_inventory_complete` (boolean), `units` (array), `warnings` (array of strings). Each unit has `id`, `locator`, `readable`, `reviewed`. Include every screenplay page or reproducibly numbered text section, including unreadable ones. Hash the actual script file. An inventory-complete flag alone cannot establish semantic coverage; verify against the source.

Evidence objects contain `unit_id`, `anchor`, `excerpt`. Use short exact excerpts and precise PDF-page or text-line anchors. `basis` values are `explicit`, `inferred`, `proposed`, `question`. Inferred/proposed/question records need a `rationale`. Scene appearance and continuity records need script evidence even if their visual execution is proposed. A fully proposed look may have no direct outfit excerpt, but needs rationale grounded in character/context. Supplied-reference provenance belongs in `reference_notes`; it does not become screenplay evidence.

Palette arrays contain objects with `name`, `hex` (`#RRGGBB`), `role`, `basis`, `rationale`. Rationale is required for every swatch. Role might be `shirt`, `lead silhouette`, or `background separation`. HEX is a design reference, not a measured fabric value.

## Characters

Required: `id`, `name`, `kind` (`individual` or `background_group`), `identity_notes`, `reference_notes`, `identity_asset_id` (asset ID or null). Names may include Telugu. Group background performers when their individual identities are irrelevant. Identity notes distinguish script facts from proposed traits in plain language.

## Scenes

Required: `id`, `printed_number` (string or null), `slugline`, `source_unit_ids`, `story_day` (string or null), `on_screen_character_ids`, `non_visual_character_ids`, `costume_assessed` (boolean), `palette` (array), `coordination_notes` (string).

Optional `story_order` (number/null), `chronology_notes`. Include voice-only or mentioned characters under non-visual only unless also visibly present. Every on-screen character must have at least one appearance record to satisfy coverage. A visible character with an unassigned look can be recorded using null look/state IDs, but the package remains incomplete. If a scene contains no visible people, explain that in coordination notes and use an empty palette if appropriate.

## Looks

Required: `id`, `character_id`, `name`, `basis`, `evidence`, `rationale`, `garments`, `palette`, `design_notes`, `look_asset_id` (asset ID/null).

Each garment has `item`, `description`, `material`, `colour`, `fit`, `details`. Use `unknown` when a real-world specification has not been chosen. These are proposed designs unless specifically grounded in script or approved references. Cover footwear/accessories as garments where relevant. Record practical duplicates/reset considerations in design notes as recommendations, not invented inventory counts.

## States

Required: `id`, `look_id`, `name`, `condition_notes`, `basis`, `evidence`, `rationale`, `requires_distinct_visual` (boolean), `state_asset_id` (asset ID/null).

Optional: `parent_state_id`, `reset_notes`. A clean base state may reuse its look board with `requires_distinct_visual: false`. Blood/damage/wetness changes visible enough to matter normally need a distinct visual. In notes describe wearer-left/right, front/back garment area, position, extent, and progression. A parent state must belong to the same look; avoid cycles.

## Appearances

Required: `id`, `scene_id`, `character_id`, `beat`, `look_id` (ID/null), `state_id` (ID/null), `basis`, `evidence`, `rationale`, `continuity_note`, `hair_makeup_notes`.

One row per character/scene/meaningful costume beat. For an unchanged outfit throughout the scene, `beat` can be `whole scene`. Distinct beats are needed when a change occurs within one scene. Look and state owners must match the character. Do not create visual appearance rows for non-visual characters.

## Continuity

Required: `id`, `from_appearance_id`, `to_appearance_id`, `relation`, `match_notes`, `basis`, `evidence`, `rationale`.

Relations: `same_state`, `progression`, `reset`, `costume_change`, `possible_match`.

- `same_state`: same character, look, and state.
- `progression`/`reset`: same character/look, different states.
- `costume_change`: same character, different looks.
- `possible_match`: uncertain relationship, `basis: question`.

Links can cross nonadjacent scenes or connect beats within a scene. From/to denotes the intended story progression, not necessarily ascending scene numbers. Repeated look/state appearances need explicit links; an unlinked repeat is a coverage gap. A repeated state after a story-time break may be `possible_match` pending review.

## Assets

Required: `id`, `path`, `kind`, `subject_id`, `caption`, `review_status`, `is_placeholder`.

- `path`: local PNG/JPEG/WebP path relative to the JSON file. Copy selected generation outputs into the film folder. External URLs and paths outside that folder are unsupported by the builder.
- `kind`: `character_board`, `look_board`, `state_board`.
- `subject_id`: matching character/look/state ID.
- `review_status`: `pending`, `passed`, `rejected`.
- `is_placeholder`: boolean; true for layout-only test artwork or unrendered substitute images.

Optional `prompt_path`, `provenance`. Generated art and user-approved reference photos can both be used, with provenance in caption or notes. Images need to be inspected before passed status. The compiler can check references and file headers, not visual correctness.

## Questions and completeness

Each question has `id`, `scene_ids` (possibly empty), `character_ids` (possibly empty), `text`, `owner`. Suggested owners: costume designer, director, script supervisor, production designer, DOP, hair/makeup.

The compiler calculates coverage, never accepts a user-written `complete` flag. A complete package requires all source units readable/reviewed; a full scene inventory; all scenes costume-assessed; every on-screen character assigned at every scene/beat; nonempty scene/film/look palettes where relevant; a board for every visible character and used look; distinct state artwork when required; every used asset passed and non-placeholder; and links for repeated look/state appearances.

Coverage completion does not imply that proposed designs are approved or open questions are resolved. Questions and source warnings remain visible in the PDF. Incomplete coverage requires `--allow-draft` and a DRAFT banner. A voice-only character does not need an identity board or a costume look.
