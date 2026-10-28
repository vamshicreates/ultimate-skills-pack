# Script Doctor

A reusable Codex skill for reviewing micro-dramas, two-minute stories, short films, features, web-series pilots/episodes, and complete seasons or series. It provides coverage, emotional analysis, revision diagnosis, and fair comparisons across scripts of different lengths.

**Every evaluation saves an individual PDF locally**, alongside editable Markdown coverage. Each report contains the overall summary, what was analyzed, source page/scene references, scores when justified, strengths, improvement areas, and prioritized revision advice. A batch of 20 scripts produces 20 individual PDFs and an additional comparison PDF. Partial or unreadable scripts receive a clearly labeled limitations report.

Every episode gets its own report even when several episodes share one source file. A multi-episode review also gets a separate season/series synthesis PDF. Reports identify the format, dramatic unit, runtime or timing uncertainty, and the expectations used to judge that length.

## Use

Invoke `$script-doctor` with a screenplay or folder path. Example requests:

- “Use $script-doctor to read this screenplay, score the current draft out of 100, and give the three highest-value revisions.”
- “Use $script-doctor to evaluate every screenplay in this folder, write individual reports, and rank the complete drafts.”
- “Use $script-doctor with these reference screenplays as optional calibration. Judge my original script independently first.”
- “Use $script-doctor to compare these two drafts under the same rubric and explain improvements and regressions.”
- “Use $script-doctor to review this two-minute standalone story against its intended length, then save its PDF report.”
- “Use $script-doctor to review these 12 micro-drama episodes, give each a score and PDF, and assess continuity and the overall arc separately.”
- “Use $script-doctor to review this web-series pilot. Judge the pilot itself and clearly separate the future-series potential.”

The default rubric covers character, plot/conflict, emotional effectiveness, structure/pacing, dialogue, theme, cinematic storytelling, and originality/specificity. Optional reference scripts help establish concrete benchmarks without equating hit films with flawless writing.

## Judgment matched to length and format

A two-minute story can earn a high score through a specific choice and an earned emotional turn without feature-length arcs or subplots. Episodes are assessed for their own dramatic movement and their contribution to the ongoing story. Season/series scores require a complete declared unit and independent analysis; they are not averages of episode scores. See [the format and length guide](references/format-and-length.md).

Runtime changes the interpretation of craft, not the score formula. No per-minute penalty or length bonus is applied. Rankings default to comparable format/duration/unit groups; an overall mixed-format ranking can be provided when requested. The scoring helper preserves this context in JSON and CSV, while older scorecards remain compatible.

Language, cultural context, and genre shape the interpretation. The skill does not claim equal fluency in every language, direct experience of emotion, or the ability to predict a hit. Incomplete or materially uncertain readings are clearly scoped and excluded from definitive rankings. Calibration records are reusable files, not permanent model training.

## Global installation

Place this folder at `~/.codex/skills/script-doctor` on macOS or `%USERPROFILE%\.codex\skills\script-doctor` on Windows (or the `skills` folder under a custom `CODEX_HOME`). Copying works on both systems; a symlink is optional. Keep `SKILL.md`, `agents/`, `references/`, `assets/`, `scripts/`, and `requirements.txt` together. Reload skill discovery or start a new chat if needed.

This is a user-wide Codex installation, available from any project or working directory. A standalone copy does not depend on the original clone remaining in place. Exclude the clone's `.git`, `.venv`, and generated evaluation outputs when copying; create the Python environment at the installed location using the commands below. Do not move an existing virtual environment between locations or operating systems. Installation on one computer does not automatically install the skill on another computer.

You can also ask Codex: “Install the script-doctor skill globally from my private GitHub repository, vamshicreates/script-doctor.” GitHub access is needed to download the private repository; normal evaluation and local PDF export do not require a GitHub connection.

The skill instructions do not require an API key or a specific connector. Reading PDFs, DOCX, FDX, or scans depends on the document/OCR tools available in the host environment; unavailable parsing is reported, not silently skipped. The optional scoring helper requires Python 3.10+ and has no third-party dependencies.

## Local PDFs on Windows and macOS

The PDF exporter uses Python, Markdown-it, and local Chromium through Playwright. See [setup and export commands for both operating systems](references/local-pdf-output.md). No Microsoft Word or online conversion service is needed. Reports default to a new `evaluation/<run-id>/` folder beside the input, or your chosen local folder. Existing PDFs are preserved by default.

The exporter supports UTF-8 content and optional local font embedding for multilingual reports. Font coverage varies by machine; inspect the output and supply a suitable font when needed. An editable document can be supplied in addition to the required PDF.

The GitHub Actions workflow runs scoring and real PDF-export tests on Windows and macOS using synthetic reports only. No user screenplay or coverage is uploaded for testing.

## Scoring helper

The helper accepts manually reasoned category scores. It does **not** automatically evaluate a screenplay. Input format and usage are in [batch-evaluation.md](references/batch-evaluation.md).

```bash
python3 scripts/score_batch.py /absolute/path/scorecards.json \
  --json-out /absolute/path/ranking.json \
  --csv-out /absolute/path/ranking.csv
```

After installing the PDF dependencies and Chromium, run all checks with `python -m unittest discover -s tests -v` in that environment (`python3` where appropriate).

Keep source screenplays, private reference libraries, and evaluation outputs outside this repository. This package contains the reusable workflow and scoring code only.
