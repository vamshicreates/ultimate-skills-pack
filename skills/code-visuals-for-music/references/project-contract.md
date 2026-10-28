# Project data contract (version 1)

`project.json` is the handoff between analysis, art direction, and the browser timeline. All timestamps are finite seconds on the source song clock. Paths are relative to the manifest. The exporter preserves them; copy media into the film and set its `data-audio` separately.

See [the synthetic example](../assets/example-project.json).

## Required

- `version`: `1`.
- `title`: a nonempty string.
- `audio`: path to the source media.
- `duration`: positive number, measured from the media.
- `width`, `height`: positive even integer output dimensions.
- `fps`: positive number (fractional rates such as 29.97 are supported).
- `lyric_mode`: `none`, `selected`, or `full`. This declares scope, not proven completeness.
- `sections`: nonoverlapping ordered `{id, start, end, label}` objects.
- `shots`: ordered `{id, start, end, event, action, transition}` objects. Gaps are errors; adjacent shots may overlap for transitions. Coverage must span the song. IDs must be unique and valid HTML identifiers matching `[A-Za-z][A-Za-z0-9_-]*`.
- `lyrics`: ordered `{start, end, text, source_text?, meaning?, verified}` cues. Empty is allowed for `none`; lyric modes `selected` and `full` require cues.

## Optional

- `dialogue`: ordered `{start, end, text, speaker, verified}` cues.
- `bpm`: positive number or `null` when unknown.
- `beats`, `downbeats`, `phrases`, `accents`: strictly increasing times in `[0, duration)`.
- `drop`: a verified highlight time or `null`; do not fabricate one for a song without it.
- `energy`: ordered `{t, value}` normalized samples; `value` in `[0, 1]`.
- `proofs`: `{file, start, end, status}` with status `pending`, `pass`, or `revise`. Status is a human/agent review record, not set automatically by a renderer.
- `notes`: production assumptions and limitations.

The validator checks ranges, structure, scene coverage, and optional media existence. It warns about unknown lyric verification, missing/pending proofs, and incomplete section coverage. It cannot establish transcript truth, actual lyric coverage, visual quality, or whether a reviewer really watched a proof.

The browser export is a local external `.js` file containing `window.CVM` and `window.MUSIC`. Do not interpolate lyric strings into raw HTML; use `textContent`. Keep this timing export with the editable project.
