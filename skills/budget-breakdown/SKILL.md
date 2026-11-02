---
name: budget-breakdown
description: Build a production budget from a mandatory complete bound script, with an optional pitch deck. Estimate cast, technicians, equipment, time, logistics and post-production; separate indoor/outdoor scenes and location access days; deliver a readable PDF and an editable Excel workbook with one tab per cost category.
---

# Budget Breakdown

Turn a complete bound script into a traceable production estimate and editable category budget. Use the user's requested production city, currency, quality level and estimate date. Do not carry a previous project's rates, cast, runtime or shoot-day count into a new project.

## Inputs and scope

- **Required: the complete bound script** for the requested film or episodes. A pitch deck, synopsis or trailer cannot replace it. Find attached/named files before asking for information already available.
- **Optional: a pitch deck.** Use it for treatment, audience, scale and proposed talent. Actor photographs and composer references are suggestions unless explicitly confirmed.
- Read every script page, including the ending and material between headings. Record source revision, file-page references and extraction/OCR gaps. Read the complete deck when supplied. Preserve printed scene numbers, including alphanumeric inserts, and distinguish printed page numbers from PDF pages.
- If pages/episodes are missing, identify them and request the complete script. Continue organizing readable material, but do not present a complete-project estimate. Only create a partial/provisional estimate when the user explicitly authorizes that scope; label its extrapolated sequences separately.
- Infer routine implementation choices. Ask only for missing decisions that materially affect the estimate, such as unknown filming region, star attachments or a binding spending ceiling.

## Build the evidence before pricing

Create a scene ledger: stable ID, episode, printed scene number, source pages, location cluster, INT/EXT/mixed, story day/night/evening, **on-camera characters**, background, action/dance, props/costume changes, sound/music, effects and special access.

Read action as well as dialogue. Capture recruitment montages, split calls, phone-screen footage, classrooms, stair approaches, doorway action, final performance coverage and location changes embedded inside one heading. Normalize character aliases without silently combining distinct people. A name mentioned in dialogue or heard in VO does not automatically create an on-set actor call.

Keep original headings and production classification side by side. Explain changes such as an open tower top classified outdoors despite an INT heading. Reconcile indoor + outdoor + mixed numbered scenes to the ledger once; embedded pieces add work, not extra printed scene counts.

Derive a rough location-blocked shoot plan and access requirements. Include ensemble coverage, choreography rehearsal, action, costume/light resets, nights, moves and rest. Distinguish active shoot days from calendar hold days and preparation access. Avoid assuming all elapsed call hours are productive camera hours. If a detailed schedule already exists, use its scene-based calls and explain any revisions.

## Price the production

Use **quantity × paid days/units × rate** for each line, with explicit person-days, kit-days and project-fee bases. Keep project fees at quantity 1 × units 1. Separate labour from equipment; detect bundled lenses, operators, generator fuel, drivers and stage technicians before charging them again.

Default categories, adjusted to the script:

1. Development and preparation: writer/director, producers, casting, recce, contracts, insurance.
2. Cast and background: named roles, small roles, recurring performers, crowd person-days, rehearsal pay, VO/ADR where applicable.
3. Choreography and specialist work: choreographer/assistant, controlled action, movement, intimacy or medic calls where supported by scenes.
4. Technicians: camera, direction, sound, lighting/grip, art, costume, HMU and production support, including prep/wrap days.
5. Equipment and power: main/extra cameras, lenses/media, support, lighting/grip, sound/timecode, playback, power/fuel, storage and backups.
6. Art, costume and consumables: dressing, props, duplicates, performance clothes, laundry, injury makeup, food/drink and restore.
7. Unit logistics: local/outstation transport, accommodation if needed, catering, peak-crowd top-ups, communication and facilities.
8. Music and post-production: picture/assistant edit, original songs/score, singers/lyrics, music rights, graphics/VFX, sound, colour, subtitles, QC and masters.

Research current regional rates using available connectors or browsing. Prefer dated vendor quotations and local published listings; record source URL/date, package contents and whether tax is included. Label every unsupported figure an **analyst planning allowance**, not a quote. Recheck old rate cards. Keep famous cast/composer fees and commercial song rights subject to specific quotes. Do not silently replace contracted talent or licensed music to meet the budget.

**Default location treatment for this workflow:** list locations and shoot, rehearsal, dressing/prelight and strike access; leave hire and permission fees **TBD and excluded from the priced total**, unless the user provides/requests priced locations. Shared partial access days overlap and must not be summed as total shoot days. Blank unknown amounts are not zero. Refundable deposits are cash requirements, not automatic expenses.

State the contingency percentage and its base. Separate direct cost, contingency and total. Explain taxes, licences, talent attachments, outstation costs, distribution/marketing and production-house markup as actual inclusions or exclusions. Do not invent a universal GST rate. If a range is useful, distinguish a judgement envelope from fully costed alternatives; preserve the user's chosen scope.

## Deliverables

Default to **PDF + .xlsx**, or follow an explicitly requested format. Use one underlying model for both. Read [references/model-and-delivery.md](references/model-and-delivery.md) when organizing data, formulas and output checks. The small fictional input in [assets/example-budget.json](assets/example-budget.json) illustrates the checker contract; its prices are not market benchmarks.

- PDF: dated overview, scope/source completeness, character implications, cast calls, rough schedule, location access table, separate indoor/outdoor/mixed scene lists, detailed category tables, contingency, exclusions, assumptions and source links. Repeat table headers; keep totals and labels readable without clipped columns or orphan rows.
- Excel: summary first; **one worksheet per cost category**, each item on its own row with ID, description, quantity, days/units, rate, calculated amount and basis. Include useful scene, schedule, cast and location schedules. Keep editable inputs distinct from formulas. Summary links to category subtotals; totals recalculate when rates or days change. Keep taxes and unknown locations visibly outside the included total rather than treating missing costs as fully funded.

Use the environment's spreadsheet/document tooling and applicable authoring skills. Keep numbers/times numeric and formulas editable. Avoid hardcoded local runtime paths in reusable deliverables. Publishing or sharing files externally requires the user's task authorization; this skill alone does not authorize it.

## Validation and handoff

Run `python3 scripts/check_budget.py budget-model.json` for the compact numeric model described in the reference. It checks line bases, missing included inputs, IDs, contingency and control totals. It does **not** verify source coverage, market rates, labour rules, spreadsheet formulas or document layout.

Reconcile every category and the total to the workbook and PDF. Change and restore a representative input to check summary propagation; confirm an intentionally waived zero remains valid and an unknown required input is exposed. Render and visually inspect outputs. Resolve extraction gaps, dropped scene portions, duplicated kits, omitted crowd meals and coverage/runtime assumptions before delivery. Mention remaining scope uncertainty plainly and provide links to the requested outputs.
