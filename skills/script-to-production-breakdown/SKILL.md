---
name: script-to-production-breakdown
description: Extract a single film's screenplay into scene inventories, department requirements, and continuity dependencies with script evidence. Use for a complete production breakdown or a named category such as cast, locations, or props; outputs structured data and CSV reports for later planning skills.
---

# Script to Production Breakdown

Produce a reviewable production inventory for one film from its authoritative screenplay. A complete breakdown is the default when the user supplies the full script. A category request such as “props only” uses the same records and evidence rules, with the other categories marked unassessed. Respect an explicitly requested sample or scene range.

## Inputs and scope

- Required: the screenplay, attached or at a user-named local path. If absent, request it; do not select an unrelated film from the workspace.
- Accept readable PDF, DOCX, FDX, Fountain, TXT, and Markdown; use available extraction tools. Read the script itself, including action, dialogue, parentheticals, inserts, montages, and intercuts. File extensions alone do not guarantee readability.
- Support Telugu, English, transliterated Telugu, and mixed scripts. Preserve original names and wording; add normalized labels without silently merging similar names.
- Optional: film title, revision, existing breakdown, approved character aliases, actor mappings, and department notes. Human notes are identified by source and do not become screenplay facts.
- When competing drafts are supplied and the authoritative one is unclear, resolve the choice before a full extraction. If lock status is unstated, record `lock_status: unconfirmed` and proceed with the identified draft.

This skill inventories requirements. Prices, shoot-day calculations, creative rewrites, location bookings, costume design, storyboard generation, and final VFX methods belong to their respective workflows. A later skill may consume the saved breakdown.

## Read and index the screenplay

1. Create a film-specific output folder, normally beside the supplied script. Preserve source files and prior runs. Use a new revision folder for a different draft; retain IDs for unchanged scenes when a prior breakdown exists.
2. Record the source filename, SHA-256, revision, language, lock status, and extraction method. Track every source unit (PDF page or numbered text section), whether it was readable, and whether it was reviewed. Keep printed page numbers distinct from PDF page indices.
3. Read all supplied script units before finalizing cross-scene continuity. For long scripts, extract in batches and retain a progress ledger. OCR unreadable pages when available, preserve the original text, and flag uncertain names or passages. An unreadable page is a coverage gap, never evidence of an empty scene.
4. Inventory scenes in script order. Preserve printed numbers, including `12A`, omitted scenes, and repeated headings. Assign separate stable IDs such as `SC-001`; new insertions receive new IDs without renumbering existing records. Treat montages, intercuts, and scenes without headings explicitly so their contents are not lost or double-counted.
5. Preserve the full slugline, source anchors, story location, INT/EXT, and scripted time. `CONTINUOUS` and `LATER` are not automatically DAY or NIGHT. Record ambiguous boundaries and implied time as questions or inferences.

For text formats, use reproducible line anchors; for PDFs use actual PDF page indices. Count only screenplay units as reviewed, explaining any excluded title or front matter.

## Extract one requirement per record

Read [references/data-contract.md](references/data-contract.md) before writing the output. Use its categories, fields, and completion rules.

Cover locations, cast, costume, props, vehicles, animals, background/extras, special equipment, VFX, action/stunts, makeup/hair, art/set, sound, weather, practical effects, and lighting. Day/night and INT/EXT are scene fields; continuity links are separate records.

Apply these distinctions:

- **Explicit:** the script states it. Supply a short excerpt and precise source anchor.
- **Inferred:** a proposed requirement derived from a scripted event. Supply its anchor and reasoning; keep the proposed execution method distinguishable from the story need.
- **Question:** the text cannot settle the requirement. Record what needs confirmation and the relevant scene or source.

Do not infer crane, drone, lens, stunt method, rain rig, VFX duration, exact costume, or crowd count solely because one could be useful. For example, “a crowd fills the square” establishes a crowd but leaves headcount unknown. A disappearing building establishes an effect need; VFX versus practical execution remains a recommendation or question unless specified.

Track cast participation as visible speaking, visible non-speaking, off-screen voice, voice-over, or referenced only. Mentioned characters do not become on-set cast requirements. Characters and actors are separate: attach an actor only from an approved supplied mapping.

Keep scripted locations separate from eventual shooting venues. A house and its kitchen may share a parent location; identical wording does not prove two scenes share a venue. Preserve aliases and flag uncertain matches. Distinguish unique entities, scene appearances, and quantities: ten scenes containing a car do not mean ten cars.

Record wardrobe and makeup only to the detail supported by the script or approved references. A same-day match can be inferred, but do not invent a shirt colour. Distinguish handheld props from dressing and practical effects from VFX; link related requirements without duplicating their counted quantity.

## Resolve continuity across the full script

Track story chronology separately from script order. Link matching or changing costumes, carried props, injuries, blood/dirt, hair, vehicle condition, weather, set damage, and story time to the affected scene IDs. Each dependency names the element, the required state or change, evidence, and the reviewing department. If chronology is ambiguous, record the ambiguity rather than asserting a match.

Keep each scene category in one of three states: `present`, `none_identified`, or `not_assessed`. `none_identified` means the category was reviewed with no requirement found; it is not proof that a department needs nothing. Link open questions to scene IDs and give them a suggested department owner.

## Save and check the package

Write `breakdown.json` using the data contract, then run the bundled helper with absolute paths:

```bash
python3 <skill-folder>/scripts/build_reports.py <output-folder>/breakdown.json --out <output-folder>/reports
```

The helper validates references and coverage and writes:

- `scene-inventory.csv`
- `scene-requirements.csv` — long format, one requirement per row
- `entity-register.csv`
- `continuity-dependencies.csv`
- `review-questions.csv`
- `summary.md`

These CSV files are the reusable inputs for budget, location, costume, VFX, and shot-planning skills. They do not require a cast or cost database to perform extraction. Preserve IDs and evidence when passing data downstream.

Review the semantic result as well as the validator output: every requested scene and category assessed, all cast appearances grounded, repeated entities consistently linked, no invented quantities or equipment, and continuity links checked against the full script. The validator cannot verify whether an excerpt or interpretation is faithful to the screenplay.

If pages are missing or unreadable, produce a clearly labelled partial package for the readable scope and list the gaps. Do not mark it complete. For a requested sample, complete only that scope and report the whole-film coverage separately. Finish by linking the package and stating scene count, coverage gaps, and unresolved review questions. A finished AI breakdown is ready for department review, not automatically approved for production.
