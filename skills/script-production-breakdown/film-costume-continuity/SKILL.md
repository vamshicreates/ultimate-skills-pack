---
name: film-costume-continuity
description: Design character look boards, scene-specific costumes, coordinated colour palettes, and visual costume continuity for one entire screenplay, then assemble a detailed PDF costume bible. Use when the user supplies a film script and wants character-to-scene-to-costume planning with generated designs and links between repeated or changing looks.
---

# Film Costume and Continuity

Create a complete character, costume, colour, and continuity bible for one film. Deliver a detailed visual PDF plus editable structured data. The default scope is the entire supplied screenplay, not a few sample scenes.

Interpret “character storyboard” in this workflow as a character look board and costume reference sheets. Add narrative shot storyboards only if separately requested. A screenshot of a sample planning table is a formatting reference, not an actual screenplay, cast reference, or costume instruction.

## Inputs and screenplay coverage

Required: the attached or explicitly named screenplay. If it is missing, request it before running a film breakdown. Optional: actor/character references, approved looks, period/location references, director notes, production palette, and an existing production breakdown. Preserve reference roles and file provenance.

Use the complete authoritative draft. Read action and dialogue as well as headings. Record the source hash, revision, page/section coverage, and extraction warnings. Use OCR where necessary; unreadable pages remain gaps. If draft choice is genuinely ambiguous, resolve it before committing to designs. An unconfirmed lock status can be recorded without stopping.

Support Telugu, English, and mixed-language scripts; preserve original names with stable IDs. Retain printed scene numbers separately from internal IDs. Inventory every supplied scene, including flashbacks, songs, montages, intercuts, dream sequences, and unheaded material. Separate script order from story chronology. Referenced or voice-only characters do not automatically require costumes. Track visible background performers as practical costume groups when individual identities are unnecessary.

An existing breakdown may seed this work, but compare its source hash/revision and verify costume-relevant passages against the screenplay. Do not require a separate skill or a cost database to begin.

## Plan characters, looks, and states

Read [references/data-contract.md](references/data-contract.md) before authoring `costume-bible.json`.

1. Establish each character's visual identity, age range, story context, occupation, silhouette, grooming, and palette only to the degree supported by the script or supplied references. Label additional design choices as proposals. When no actor reference exists, create a fictional proposed identity and keep it consistent across the film.
2. Design one base look per distinct outfit. Describe garment pieces, silhouette, fit, fabric/texture, pattern, colour, layers, footwear, accessories, fastenings, and relevant hair/makeup. Give a story or scene reason for the choices. Scripted details and approved references take precedence over a new design preference.
3. Represent condition changes as states of that look: clean, wet, dusty, torn, progressively blood-stained, repaired, or reset. Track wearer-left/right, garment panel, position, size, and severity of visible changes. A new shirt colour is a look change; blood on the same shirt is normally a state change.
4. Map every visible character or background group in every scene to a look and state. Use multiple appearance records when an outfit or condition changes within the scene; label the beat. Do not assume adjacent scene numbers imply the same story day, or that a later script scene follows an earlier one chronologically.
5. Link repeated or changing appearances explicitly. For example: `SC-004 / Ravi / Look L-001 / State ST-002: same costume as SC-001, now with a blood stain on wearer-left upper chest`. Include the matched reference image and the relevant garment details. If same-costume continuity is uncertain, label the link as a question instead of silently locking the match.

Track exact repeats, condition progression, resets, and outfit changes separately. Continuity is between appearances of the same character; matching colour alone does not establish the same outfit. Any duplicate garments or cleaning/reset quantities are proposed department decisions unless supplied by production.

## Coordinate colour across the movie

Give each look named colour swatches with HEX values, usage, and rationale. Build a film palette and scene palettes showing relationships among characters, background costumes, and scripted or proposed set colours. Explain intentional harmony, contrast, character separation, and changes over the character arc without changing screenplay facts.

Keep script-specified colours distinct from proposed colours. Identify assumptions about unknown sets or lighting. Use colour names and patterns alongside swatches so the document works in grayscale. HEX values and AI artwork are design references, not calibrated fabric or camera matches; physical swatches and camera tests remain production checks.

## Generate and inspect the visual references

Read [references/visuals-and-pdf.md](references/visuals-and-pdf.md) when designing boards and assembling the PDF. Use the available built-in image-generation capability following its current guidance. If the image-generation skill is installed, read it for tool use. Do not silently substitute a paid API/CLI path, stock pictures, generic silhouettes, or text-only prompts for requested character and costume artwork.

Create a stable identity board for each visible character or background group, a costume board for each unique look, and a distinct state reference when a visible change needs to be matched. Use front/back/side or detail views as the look requires. Generate related variants using saved references so identity, tailoring, accessories, and garment geography remain consistent. Reuse a saved look/state image for repeats instead of generating a fresh interpretation per scene.

Save generation prompts and selected images in the film's output folder. Inspect every selected asset for identity, garment pieces, colour family, accessories, condition, and orientation. Mark assets passed only after inspection. Mark synthetic layout fixtures or placeholders explicitly; they cannot satisfy final visual coverage. Generated continuity references are design targets, not photographs of completed on-set wardrobe.

If generation is unavailable or a persistent blocker prevents an asset, preserve progress and report exactly what is missing. A draft PDF may document the gaps; do not call it the completed whole-film visual bible. Resume from stable IDs without discarding accepted designs or regenerating unaffected assets.

## Build the detailed PDF

Keep one film and revision per output folder, normally `<film>-costume-bible/`, containing `costume-bible.json`, `assets/`, `prompts/`, and generated reports. Preserve the script and prior revisions.

Run the bundled builder with available Python:

```bash
python3 <skill-folder>/scripts/build_book.py <film-folder>/costume-bible.json --out <film-folder>/book
```

It validates coverage, relationships, palettes, and asset files, then creates a local HTML costume bible with a copied assets folder, a character/scene/costume CSV, a continuity CSV, and a coverage report. Keep the HTML and its assets together. Add `--allow-draft` only when intentionally rendering a clearly labelled incomplete package. `--validate-only` checks the data without writing the book. The helper cannot judge script interpretation or artwork fidelity.

Render the HTML to PDF with the bundled browser helper:

```bash
node <skill-folder>/scripts/render_pdf.cjs <film-folder>/book/costume-bible.html --out <film-folder>/book/costume-bible.pdf
```

Use the installed workspace runtime/dependency discovery to locate Node and Playwright if they are not on the default path. The renderer uses locally installed Chromium; it does not install browsers or contact external sites. When module resolution needs it, set `NODE_PATH` to the discovered package directory. `--browser <absolute-executable>` selects an already available Chromium. If rendering fails, preserve the HTML/data, fix the concrete failure, and report any remaining PDF blocker.

The PDF must include: source/coverage and design status; film palette; character identity boards; every costume look with garment specifications and colour swatches; condition references; every scene's cast-costume-state assignments and colour coordination; a cross-scene continuity register; and unresolved questions with evidence. Show visual references beside continuity information. Use the same image for an exact repeat and an edited state reference for a change. Do not replace scene coverage with a summary of unique outfits.

Render and inspect the PDF at readable size, including long tables, image-heavy pages, Telugu names when present, scene transitions, and the final page. Check for cropped garments, missing glyphs, clipped notes, broken assets, and blank overflow pages. Confirm that every inventoried visible appearance is represented, every continuity link resolves, and all requested visuals are present. Report extraction/design completeness separately from human approval. Deliver the PDF as the primary link and the editable JSON/CSV as supporting files.
