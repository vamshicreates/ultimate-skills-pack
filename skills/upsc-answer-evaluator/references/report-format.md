# Report data

UTF-8 JSON. All learner-facing strings are plain text; XML is escaped. Use ASCII punctuation for the bundled Helvetica font (other languages require an appropriate embedded font and visual verification). The renderer refuses unsupported characters rather than printing broken glyphs.

Required keys:

- `title`, `subtitle`, `review_date`, `metadata`, `question`, `verdict`: strings.
- `strengths`: 1-3 strings grounded in the answer.
- `feedback`: 1-4 objects with `location`, `student_excerpt`, `status`, `explanation`, `revision` (strings) and `source_ids` (list of source ID strings).
- `priorities`: exactly three strings.
- `model_outline`: 1-5 objects with `label`, `text` (strings) and `source_ids` (list).
- `notes`: 1-3 strings for genuine uncertainty, attribution or scope limits.
- `sources`: objects with `id`, `title`, `url`, `locator`, `checked` (strings). URLs must be HTTP(S); use the actual inspected document. Source IDs must be unique; all referenced IDs must exist.

Optional audit-only keys, not printed: `input_files`, `transcription_notes`, `claim_checks`, `rubric`, `word_count_method`, `research_limitations`. Keep these alongside the compact learner report so the workflow can later become a product without losing provenance.

Page 1 contains the question, verdict, strengths and four correction cards. Page 2 contains priorities, a model outline, notes and sources. Keep total printed copy around 650-850 words. Long data is rejected if it spills onto a third page. Each report source link includes a title and useful locator; full URLs remain in JSON and PDF annotations.
