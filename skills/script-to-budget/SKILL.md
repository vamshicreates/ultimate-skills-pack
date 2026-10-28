---
name: script-to-budget
description: Read a screenplay from an attachment or the Script folder, identify production cost drivers scene by scene, estimate a preliminary film budget, and deliver a sourced PDF with assumptions and cost-saving options. Use for script-to-budget requests, not detailed shooting schedules or storyboards.
---

# Script to Budget

Produce a preliminary, auditable production estimate from the **whole** screenplay. Default input folder: `$HOME/Documents/VamshiCreates/Script`. Default output folder: `Script/budget-reports/<script-stem>/`. A screenplay may also be supplied directly. Prefer the named or newly added revision; if several plausible revisions remain, identify the one used in the PDF.

## Workflow

1. Read every page through the ending. Use `scripts/extract_screenplay.py` for PDF, DOCX, FDX, Fountain, or TXT input; use OCR when a PDF page has little or no text. Inspect the extraction warnings and verify the first, middle, and final pages. Do not treat extraction failure as a scene with no requirements. Preserve scene headings and page or source references.
2. Build a scene ledger with stable IDs, printed scene numbers, source page, full heading, location, time of day, characters, and relevant requirements. Review each scene body, including material between headings. Count **scenes** separately from distinct **shooting locations** and **location areas**; repeated use of a place is one location but may require several days or resets. Mark uncertainty explicitly. Preserve evidence IDs/pages for action, music, crowd, vehicles, sets, VFX, children, animals, special effects, weather, and travel.
3. Derive a plausible shooting plan from the ledger: geography blocks, interior/exterior mix, days/nights, set build/reuse, travel, company moves, and technically difficult days. List assumptions about pages per day, number of units, work hours, travel, and postproduction. Do not equate scene count with shoot days.
4. Build a bottom-up budget from **quantity × unit rate** by department. Separate prep, principal photography, cast, locations, art, camera/lighting/grip/sound, transport/accommodation, catering, action/safety, music, VFX, post, legal/insurance/permits, and contingency as applicable. Avoid duplicate charges. Put star fees, rights, tax treatment, and financing/distribution costs in explicit inclusions or exclusions. Use current region-specific quotes or a producer-supplied rate card where available. If rates are assumptions, label them as planning assumptions, give low/base/high cases, and identify the largest sensitivities. Do not present a rough estimate as a vendor quote.
5. Offer script and scheduling options with a mechanism and rough saving range: location consolidation, fewer moves, block shooting, practical/set tradeoffs, day-for-night or day/night rewrites where creatively acceptable, crowd scaling, vehicle sharing, stunt/VFX alternatives, and contingency implications. Never silently rewrite the screenplay. Distinguish ideas from approved changes; do not subtract speculative savings from the base total.
6. Write a `budget-input.json` following [references/budget-schema.md](references/budget-schema.md) and render it with `scripts/render_budget.py`. Deliver the PDF and the editable JSON/scene ledger. The PDF must show script identity, revision/date, extraction quality, inventory counts with definitions, schedule assumptions, line items, low/base/high totals, exclusions, top risks, evidence, and optimization opportunities.
7. Validate arithmetic and coverage before delivery: source hash, last page read, printed scene sequence including alphanumeric inserts, no missing scene bodies, scene count versus PDF, night/evening distinction, unique location normalization, cost units, contingency base, and exact totals. Spot-check high-cost evidence against the original pages. Report any unresolved items.

## Trigger behavior

When asked to analyze a new file in `Script`, use this skill and create a new report folder named for that file. The skill itself does not run in the background. If the user asks for automatic monitoring, set up a Codex heartbeat or another authorized watcher that checks for changed file hashes and invokes this workflow once per new revision; notify only on a finished PDF or an actionable failure.

## Regional assumptions

Use the production region and currency supplied by the user. If absent, infer likely region from the script, label the inference, and ask for the filming region/rate card while continuing the script breakdown. Location permissions and charges vary by authority and site; check current official sources before treating a fee as factual. The estimate is a preliminary producer planning tool, not a binding production bid.
