# Schedule model and delivery

## Compact checker contract

The checker requires Python 3.9 or newer. Dated turnaround checks also need an available IANA timezone database (system data or Python's `tzdata` package). `scripts/check_schedule.py` accepts a JSON object with:

- `timezone`: a nonempty local zone identifier for display/context.
- `scenes`: a unique list of required component IDs, e.g. `"31.room"`, `"31.exit"`. Keep a separate ledger mapping components to the original printed ID and source pages. These components do not increase the printed scene count.
- `days`: a nonempty array of active blocks with unique `id`, integer `call_start`, `call_end`, `events` and `calls`.
- Optional `date`: actual ISO start date of each unit block, for dated turnaround checks. Either all day blocks have dates or none do. Undated work blocks make no promise of consecutive dates.
- Optional `minimum_turnaround_minutes`: the agreed/planning target, only checked when all blocks have real dates. The checker does not prescribe a legal limit.
- Optional `minimum_break_minutes_per_day`: a caller-supplied planning/agreement target. It is not a default labour rule.

Event: `start`, `end` (absolute integer local minutes), `kind`, optional `description`, `scene_refs` and `cast`. Kinds: `Setup`, `Blocking`, `Shoot`, `Break`, `Move`, `Buffer`, `Wrap`. Events completely partition `call_start` through `call_end`. A shoot event requires nonempty `scene_refs` and an explicit `cast` list (empty only for genuine empty plates/objects). Other events cannot declare scene coverage. All IDs must exist in `scenes`.

Actor call: unique `character`, `call`, `ready`, `release`. These are absolute minutes in that unit's local date. The condition `unit call <= actor call <= ready <= release <= unit release` must hold in this simplified model. If real HMU/advance/late-release shifts extend beyond the main unit, explicitly represent and review those shifts rather than silently dropping the time to pass this checker.

Every character in a shoot event must have a matching call and be ready/released around the entire event. Split a long scene event when a performer is only present for part of it and is being released early. An early release cannot be justified by a scene that still includes that character after release. Prerecorded VO needs no live actor call unless actually recorded during that event.

Scene components are covered by the union of shoot-event references. The checker detects missing and unknown components but cannot establish that the component inventory itself includes every part of the script. It accepts multiple visits to a component for pickups; explain them in the ledger.

For dates spanning daylight-saving clock changes, the checker deliberately refuses a timeline crossing an offset change. Use an explicit-offset timeline/check for that site/date. Do not treat a timezone's nominal clock offset as globally constant.

## Timed planning pattern

Start with call capacity and subtract setup, movement, blocking, meals/comfort breaks, pickup reserve and wrap. Assign scene work only to remaining capacity. Do not reuse a numerical day template without testing its workload and setting it to the applicable agreement. Setup within a scene block and a separate setup row must not count the same minutes twice.

For a long night scene, three large scene blocks around breaks may work better than many rushed setups. For a sports/action day, stage harder work in suitable light/temperature windows and place shaded dialogue/inserts between them. Rehearsals, specialist availability and cast continuity remain explicit conditions, not assumed savings.

## Excel mechanics

Use a numeric unit-call input and numeric duration inputs. First start references the call; subsequent starts reference the prior end. End = start + duration/1440. Round serial arithmetic enough to make the midnight boundary display reliably (e.g. `ROUND(...,10)`). Use a time format with date-offset indication or a separate numeric day-offset column; plain `hh:mm` alone conceals a next-date release.

Master rows link to the owning daily tab's call, wrap and duration totals. Cast matrix counts exact normalized tokens/IDs or uses a flat character/day call table. Avoid substring matching that treats `Security guard` as also matching `Security guard 1`. Keep the editable source authoritative and explain whether actor window edits propagate.

In the PDF, actor group call windows may be condensed, but all named characters must still be listed and available for their blocks. In a detailed interchange model, represent each actor individually for checking. Provisional deck-only events must remain distinct and cannot be presented as fully scripted scenes.

## Validation examples

The bundled overnight example should report 720 elapsed minutes and both scene components covered. Mutating the second shoot to end after its actor releases should fail. Moving one event start without moving the previous end should fail. Adding a required scene with no shoot block should fail. Dated calls below a supplied turnaround target should fail. None of these checks validates dialogue quality, market rates or safety choreography.
