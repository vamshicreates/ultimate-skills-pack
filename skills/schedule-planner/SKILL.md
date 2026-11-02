---
name: schedule-planner
description: Plan a film or series shoot from a mandatory complete bound script and optional pitch deck. Produce scene-based daily character calls, realistic setup and shooting blocks, breaks, wrap and rest planning in a PDF and editable Excel schedule. Use for production shoot scheduling, not post-production editing schedules or generic calendars.
---

# Schedule Planner

Create a workable shoot plan whose clock, characters, coverage and location moves agree. Default outputs are a readable PDF and an editable Excel workbook. Treat shoot-day count as a result of the scoped script and resources; do not copy a previous project's 24-day plan.

## Required input

The **complete bound script** for the requested film or episodes is mandatory. A **pitch deck is optional**. Locate and read every page of the actual script through its ending; inspect extraction/OCR failures. Read the whole deck when supplied to understand visual scale, performances and treatment.

If only a deck, synopsis or incomplete set of episodes is available, request the complete scoped script. Continue reviewing available material but do not call the resulting plan complete. A provisional schedule is permissible only when the user explicitly authorizes that narrower scope; identify deck-only sequences as provisional IDs, never fabricated printed scene numbers.

Use existing scene IDs, budget scope, availability and location information when available. Resolve consequential missing information while progressing on independent work. No shoot dates supplied means numbered active blocks, not invented bookings or consecutive calendar dates.

## Scene and character coverage

Build or check a ledger with episode, printed scene number, source pages, normalized location, original INT/EXT heading, practical production classification, story time, **on-camera cast**, background, dance/action/physical work, props, costume/injury states and sound requirements.

Track each embedded location/portion: room and courtyard inside one slugline, stair and open-top work, split-screen calls, VO over montage, phone inserts, classroom/mess/clinic action and scene bridges. Preserve printed IDs; use component IDs for a split, and distinguish pickup coverage from a second full scene call. Every required component needs a scheduled block. Compare indoor/outdoor/mixed counts to source scenes without counting the components as extra printed scenes.

Normalize aliases explicitly. Do not call performers solely because their name is mentioned, their photo is in a deck, or they provide prerecorded VO. Do call them for silent reactions, group masters and screen-call inserts when actually photographed. State whether distant call footage is staged locally, pre-recorded or requires a separate unit. Keep unresolved character names visible for writer/casting clarification.

## Consolidate before assigning the clock

Group by location cluster, daylight/night look, cast availability, wardrobe and physical continuity. Estimate coverage and scene complexity rather than dividing scene count or pages by a constant. Allow uninterrupted time for long dialogue, emotional work, rehearsed full routines, crowd control and controlled physical beats.

Prefer a single campus/site route and pre-rigged adjacent zones where the script allows. A one-camera unit cannot simultaneously shoot a second scene. A second camera helps same-scene coverage; it does not make two complete units. Distinguish prep rigging/technical rehearsal from photography days and disclose additional access/crew requirements.

If the user supplies a day ceiling, first test consolidation against all components and overhead. Present a justified revision when it will not fit; never compress by silently deleting scenes, breaks, setup or travel. If a detailed revision changes indoor/outdoor days or cast calls relative to a budget, state the change and flag the affected budget inputs for refresh.

## Plan every day in this order

1. **Scenes at the top:** episode, exact IDs/parts, location and day/night look; clearly mark provisional material.
2. **Characters and background:** list actual named characters required that day and estimated background/recurring performers. Then suggest actor/group call, camera-ready and release times, including makeup/wardrobe and warm-up.
3. **Unit clock:** crew call, first camera, planned scene blocks, short setup/relight/move durations, meal and comfort breaks, pickup reserve, camera wrap, media/de-rig and unit release. Do not describe camera wrap as the end of all work if the crew still has to strike/backup.
4. **Consolidation:** practical location route, reused lighting/marks, shot priority and which cast/background can leave after their complete coverage.
5. **Conditions before roll:** scene-specific props/playback, continuity, prep rehearsals, access and required specialist calls. Treat specialist/contract limits as inputs, not invented universal rules.

Use the local time zone and a 24-hour clock with explicit next-date markers. Store time internally as absolute integer minutes from that work block's start date (e.g. 01:30 next date = 1530). Timeline rows must be contiguous; breaks stop the unit, not conceal setup. Include realistic company moves and wardrobe resets. Do not promise ten hours of filming inside a twelve-hour call after also allocating meals, rigging and strike.

Do not hardcode one labour limit or night-light window as law. Check applicable agreements/official rules when advising on them; otherwise label proposed call/turnaround targets as planning assumptions. For dated exteriors, verify actual light windows and allow weather uncertainty. Group nights, protect recovery before early daylight work, and add calendar rest days separately from active shoot days.

## Outputs and checks

Read [references/model-and-delivery.md](references/model-and-delivery.md) for a compact schedule model, actor/event checks and output mechanics. [assets/example-schedule.json](assets/example-schedule.json) is fictional and demonstrates an overnight call; it is not a preferred day length or crew agreement.

- PDF: overview/master plan, spacing and assumptions, a separate clearly readable daily page where practical, and scene coverage / cast-call references. Keep each day's scenes above the timing table, repeat table headers when needed and show source script revision.
- Excel: master schedule, one tab per active day, character call matrix and concise plan notes where useful. Include every day's scene/cast information and editable clock inputs/durations. End times and master summaries must recalculate. Keep times numeric; handle midnight without losing the date offset. A cast matrix should follow one authoritative character list, not remain a disconnected snapshot.
- If text sub-times or actor call windows are not formula-linked to unit timing, say they require manual adjustment. Do not claim all planning data automatically reschedules.
- Keep one underlying model for both formats. Use the environment's applicable spreadsheet/PDF authoring tooling; do not embed project-specific absolute paths or a dependency on another custom skill's installation.

Run `python3 scripts/check_schedule.py schedule-model.json`. It checks declared component coverage, contiguous timelines, scene/cast references, actor readiness/releases and dated turnaround assumptions when supplied. Then manually check source completeness, feasibility of coverage rates, company moves, preparation, and continuity; the checker cannot prove those.

Reconcile daily minutes to elapsed call time, verify all intended scene portions appear, and spot-check cast against the source action. Test an ordinary duration edit and a midnight crossing in Excel, restore inputs, and inspect the final formulas. Render all daily views/PDF pages to catch clipping and orphaned rows. Deliver requested file links and briefly identify unresolved script, availability or location conditions. This skill does not authorize booking people/venues or publishing private script material.
