---
name: film-cast-actor-database
description: Research a film's credited performers, infer evidence-based casting categories from their wider work, and publish a sourced actor database with recent-film evidence to Google Sheets. Use when a user supplies a film title or link for actor or casting research.
---

# Film cast actor database

Given a film title or URL, identify the exact film, research every identifiable credited performer, and deliver a live Google Sheet. Use the connected Google Sheets or Google Drive tools to create and populate the sheet when available. The user's request to build the database authorizes creating it in their connected account; do not change sharing permissions unless requested. If no connected cloud writer is available, produce a local workbook from `templates/actor_database_template.xlsx` and explain what connection is needed for cloud publishing. Never invent a Google Sheet URL.

## Output

Use two tabs:

1. **Actors**: exactly `Actor name`, `Potential possible roles`, `Real age`, `Checked on date`, `Instagram link`, `Source link`. One row per performer. Keep this primary tab concise.
2. **Film evidence**: `Actor name`, `Recent film #`, `Film`, `Release year`, `Credited character`, `Credit note`, `Film source`. Up to three rows per performer, most recent released films first. Use fewer when fewer can be verified. Put the full film source URL in the final column.

The blank workbook and CSV schemas in `templates/` are reference assets. For a live Sheet, create native tabs with the same headers, freeze the header, filter the rows, make URLs clickable, and check that the final row counts and links match the research notes. Use the user's provided master Sheet instead of making another when they ask to update it.

## Research the cast

- Resolve the film by title, year, language, and director. If still ambiguous, ask for the exact film.
- Start with the IMDb **full credits** page or another comprehensive cast source. Cross-check material gaps or disputed names with a second source such as official credits, a production site, a Google film listing, or Wikipedia. Browse current pages; never reconstruct a cast from memory.
- Include identified performers across leads, supporting parts, cameos, and credited voice work. Do not create rows for unnamed extras or assume that a character name identifies an actor. Deduplicate by person, not character.
- Preserve a source URL for each person. If sources conflict about whether someone is in the film, verify before inclusion and tell the user about unresolved cases.

## Research each performer

- Match the person's filmography to the cast identity. Do not merge people with similar names. Flag a questionable IMDb profile or credit in **Credit note** and leave uncertain fields blank.
- Find up to three **recent released feature films as of the checked date**. Exclude unreleased, filming, post-production, TV series, shorts, and music videos unless the user asks for them. Confirm release status and order when a current-year listing is ambiguous. A sequel repeating the same character does not prove range by itself.
- Copy the credited character only when a source shows it. Otherwise leave that cell blank and write `Character not listed` in **Credit note**. Mark uncredited, voice, or child-artist credits clearly. The title page in **Film source** must identify the film; retain actor-profile or character-page evidence in research notes when the title page omits the individual credit.
- Suggest 1–4 practical casting categories from several roles or a credible broader biography. Examples: main lead, father, mother, son, daughter, brother, sister, friend, comic supporting role, antagonist, teacher, police officer, or authority figure. Use `Main lead`, not `hero`. These are *possible future casting roles*, not descriptions of the source film's character. Do not infer a role from the source film's genre, a character name alone, the actor's appearance, or age alone. If evidence is thin, write `Needs casting review`.
- Verify date of birth or birth year from a credible source and calculate completed years on **Checked on date** in the user's time zone. Leave **Real age** blank when the birth information is missing or contradictory. A published age may be stale.
- Put only a full Instagram profile URL in **Instagram link**. Verify identity through the account itself, an official cross-link, or another credible explicit attribution. Do not invent usernames. Leave it blank when uncertain.
- **Source link** should support the person and, where possible, the age or broader work. It need not imply that one page proves every field. Keep the cast-list URL and other evidence in working notes.

## Publish and verify

- Read `references/cloud-sheets.md` when publishing to Google Sheets, including the connection and fallback rules. Keep authentication out of the skill files and output.
- Read `references/research-rules.md` when filmography, identity, age, or casting category decisions are unclear.
- Use Laya for discovery or cross-checking if available, then corroborate its leads with a source.
- Verify actor count, duplicates, film-evidence count, the three-film limit, URLs, empty-field handling, and the checked date. Report how many actors have suggested roles, verified ages, Instagram links, and one/two/three film entries. State notable unresolved identities or cast conflicts.
- Return the real live Sheet URL. If the user requests an export, provide the service-generated export link or instructions to download from Sheets. Do not present a local template as a published Sheet.
