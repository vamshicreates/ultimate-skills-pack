# Batch evaluation and scoring helper

## Maintain a complete reading record

Inventory the supplied folder before assessing it. Assign stable IDs; record source path, title, draft/version, language, genre, format, evaluation unit, runtime/timing basis, comparison group, candidate/reference role, and input readability. For series, also record series/season and episode identity/order; a file may contain several episode scripts. Detect duplicates or multiple versions and state how they are treated. Do not select a few convenient files from a larger requested batch without accounting for the rest.

Create a separate evaluation output folder, for example:

```text
evaluation/<run-id>/
  manifest.md
  rubric.json
  calibration-profile.md     # Only when references are used
  notes/<script-id>.md       # Read ranges, scene ledger, evidence, confidence
  reports/<script-id>.md
  pdf/report-<script-id>.pdf  # Required, one for every script
  scorecards.json
  comparison.md
  pdf/report-comparison.pdf  # Additional batch overview
  ranking.json
  ranking.csv
```

Process one complete script at a time, using ordered reading chunks if needed. After each chunk, save source locators, causal/relationship changes, setups, payoffs, emotional turns, and unresolved questions. Track the ranges actually read. Before final scoring, revisit both earlier setups and later consequences. Summaries support continuity but do not replace reading the full source.

The manifest should account for every input as pending, reading, complete, partial, or unreadable, with reasons where necessary. Unreadable files remain visible in the final comparison. Do not mark an entire batch complete while any requested full assessment remains unfinished; report the completed work and the specific remaining blocker honestly.

Track PDF delivery separately from reading status: editable report path, PDF path, export result, and visual/content verification. Export each report as soon as its assessment is ready using [local-pdf-output.md](local-pdf-output.md); do not wait for the entire batch. A partial/unreadable input still gets a local PDF explaining the limitation. At the end, reconcile the input inventory with the individual PDFs one-to-one and export the comparison as an additional PDF. Twenty candidate scripts require twenty individual PDFs plus one comparison PDF, even if some individual reports can only document a reading limitation.

For a series, reconcile PDFs with the episode inventory rather than source-file count, and include a separate series/season synthesis. Default to comparable format/duration/unit groups as described in [format-and-length.md](format-and-length.md). Keep season/series scores separate from their episode scores. If the comparative or series pass changes a score or finding, update the affected Markdown and regenerate its PDF before delivery.

Freeze the rubric and weights for the batch. Score independently before comparing candidates. Then re-read decisive scenes for the leaders and close calls, checking for recency, reputation, and genre bias. Revisions to earlier scores must have reasons in the report. Do not adjust scores simply to create a wider ranking spread.

## Deterministic helper

The helper validates editorial scorecards and performs arithmetic. It cannot validate whether the script was actually read or whether the judgments are sound; those require the evidence records.

Run from the skill directory, using paths appropriate to the user's output folder:

```bash
python3 scripts/score_batch.py /absolute/path/evaluation/scorecards.json \
  --json-out /absolute/path/evaluation/ranking.json \
  --csv-out /absolute/path/evaluation/ranking.csv
```

Omit output flags to print JSON. Existing output files are preserved unless `--overwrite` is supplied. The helper uses Python's standard library only.

Input example (illustrative scores, not an assessment of a real screenplay):

```json
{
  "rubric_id": "script-doctor-v1",
  "weights": {
    "character": 15, "plot": 15, "emotion": 20, "structure": 15,
    "dialogue": 10, "theme": 10, "cinematic": 10, "specificity": 5
  },
  "scripts": [
    {
      "id": "candidate-01",
      "title": "Example draft",
      "source": "scripts/example.fountain",
      "draft": "Draft 2",
      "role": "candidate",
      "language": "Telugu",
      "genre": "Family drama",
      "format": "micro_drama",
      "evaluation_unit": "standalone",
      "runtime_minutes": 2,
      "runtime_basis": "user_stated",
      "comparison_group": "two-minute-standalone",
      "rubric_id": "script-doctor-v1",
      "read_status": "complete",
      "confidence": "medium",
      "limitations": [],
      "scores": {
        "character": 7, "plot": 6.5, "emotion": 7.5, "structure": 6,
        "dialogue": 7, "theme": 7, "cinematic": 6.5, "specificity": 7
      }
    }
  ]
}
```

Use `role: "reference"` to retain a reference assessment without ranking it. Use `read_status` of `complete`, `partial`, or `unreadable`; the helper rejects pending work. Use `confidence` of `high`, `medium`, or `low`. Overall confidence reflects material limitations in positive-weight categories, not a blind average. A low-confidence structural or linguistic judgment makes the full assessment provisional. Describe the reason in `limitations`, and keep per-category confidence and evidence in the individual report.

For new assessments, record the following context. Legacy scorecards without these fields remain valid and use the `all` comparison group:

- `format`: `micro_drama`, `short_film`, `feature`, `web_series`, `other`, or `unspecified` when genuinely unknown. A serialized micro-drama can use `micro_drama` with unit `episode`.
- `evaluation_unit`: `standalone`, `episode`, `pilot`, `season`, `series`, `excerpt`, `treatment`, or `unspecified`. A complete episode can be fully read even if other episodes are absent; a whole-season claim requires the entire declared season. Excerpt/treatment scopes never receive a whole-script total, even if the supplied excerpt was read completely.
- `runtime_minutes`: a positive numeric target or estimate, or `null`; `runtime_basis`: `user_stated`, `timed_read`, `estimated`, or `unknown` when runtime is null. Include the full timing explanation, target-versus-estimate distinction, or range in the report. Do not reduce an uncertain range to false precision just to fill this field.
- `comparison_group`: a nonempty editorial label grouping similar forms, durations, and units. Ranks and close calls are calculated independently within each group. When omitted with format/unit metadata, the default is `<format>/<evaluation_unit>`; this fallback does not automatically separate different durations. Choose explicit groups for substantially different target lengths. For an explicitly requested mixed-format overall ranking, run a separate comparison assigning the included candidates one shared group and preserve the within-format results.
- Optional `series_id` and `episode_id`: nonempty strings to retain episode identity in JSON/CSV.

These fields provide scope and comparability; they do not alter category scores or apply runtime-based bonuses. A season/series score must be reasoned independently in its own group rather than generated from an episode average. The helper does not infer runtime, determine whether an arc is complete, or verify actual reading coverage.

All eight score keys are required, with values in half-point steps from 0 to 10 or `null` for unassessed. Only complete readings with all positive-weight categories scored and medium/high confidence receive a total. Others remain unscored and unranked with reasons; their available category scores are retained. Reference rows can receive eligible totals but no candidate rank.

Default weights must use `script-doctor-v1`. Custom weights require a different rubric ID, must sum to 100, and apply identically to every row. Do not combine independently weighted scorecards. Rescore under a common framework or produce separate comparisons.

Ranking uses displayed integer totals within each comparison group. Exact ties share a rank; IDs only determine display order within a tie. Each eligible candidate lists other candidates in its own group within two displayed points as close calls, not statistically equivalent scores. This relation need not be transitive, so do not turn a chain of close calls into a single tie group. The written comparison explains substantive tradeoffs rather than claiming one-point superiority is definitive. Groups use the same frozen rubric; different weights still require separate scoring runs.
