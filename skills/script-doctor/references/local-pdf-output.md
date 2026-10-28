# Required local PDF delivery

## Delivery contract

Every script or episode evaluation produces its own PDF on the user's local filesystem, including micro-dramas and two-minute stories. Retain editable Markdown coverage as well. Include overall summary, format/unit/runtime and timing basis, scope of analysis, scores where justified, evidence and source locations, strengths, weaknesses, improvement priorities, and uncertainty as described in [report-format.md](report-format.md). A report about a partial or unreadable input must say what could and could not be assessed; do not invent content to fill sections. Episodes contained in one file still receive separate PDFs. Add a series/season synthesis PDF for multi-episode reviews; it does not replace individual episode reports.

Save each script's report immediately after its evaluation. Use a new run folder for later evaluations so earlier reports survive. The default is `evaluation/<run-id>/` beside a single source file or inside the supplied batch folder. Use the user's requested local folder when given. If that location cannot be written, use an authorized local workspace and clearly state the actual destination. Never silently switch to cloud storage.

The run folder contains `reports/<script-id>.md` and `pdf/report-<script-id>.pdf`. Assign unique, portable IDs such as `script-01-draft-2`. Keep the actual title, source path, draft, and language inside the report. For batches, also retain an input/output manifest and export `comparison.md` as an additional PDF. A combined report does not replace individual files.

## Cross-platform setup

Use Python 3.10+ and install `requirements.txt` into an available environment. A virtual environment avoids changing system packages. From the skill directory:

macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

Use the installed Python command if the Windows `py` launcher is unavailable. These commands do not require activating a shell script or changing PowerShell execution policy. An existing environment with the dependencies and Chromium can be reused. If available in Codex, inspect bundled workspace dependencies before installing anything.

The renderer uses Playwright's local Chromium PDF engine so complex-script shaping is handled by a browser. It does not require Microsoft Word, AppleScript, COM, or a macOS-specific executable. The skill itself contains no fixed home-directory paths. Dependency/browser installation needs network access once; rendering uses local content and blocks resource requests. No screenplay or report is sent to a PDF service.

## Export

Write complete UTF-8 Markdown coverage first. Use real headings, paragraphs, lists, and concise tables. Avoid images, raw HTML, or unusually wide tables; image references are rendered as text and HTML is escaped. Tables can continue over pages with repeated header rows. Very long findings are easier to read as prose outside a score table.

macOS example, using a path relative to the skill directory:

```bash
.venv/bin/python scripts/export_reports.py "/path/to/evaluation/run-01/reports/script-01.md" --output-dir "/path/to/evaluation/run-01/pdf"
```

Windows example:

```powershell
.\.venv\Scripts\python.exe scripts\export_reports.py "C:\Scripts\evaluation\run-01\reports\script-01.md" --output-dir "C:\Scripts\evaluation\run-01\pdf"
```

Pass multiple report files or a dedicated reports folder to export several at once. A folder reads its immediate `.md` files, not nested directories. Pass the comparison Markdown explicitly or place it in that dedicated folder. This helper formats authored coverage; it does not analyze screenplay source files, invent scores, or check the completeness of the evaluator's reasoning.

Output filenames start with `report-` and use a Windows-safe normalized source stem. Non-Latin-only stems receive a deterministic short identifier; titles inside the PDF remain unchanged. Colliding normalized names are rejected before writing. Existing PDFs are preserved unless `--overwrite` is explicitly chosen. Successful exports print source path, absolute PDF path, page count, and byte count as JSON lines. Save these paths in the evaluation manifest.

## Languages and fonts

Use `--language te`, `--language hi`, or another language tag for the report language, independently of the screenplay's language. Original script quotations may remain in another language. Installed system fonts are used by default; Windows and macOS can have different coverage.

For missing glyphs or to obtain consistent typography across machines, provide local font files with repeated `--font` options. TTF, OTF, WOFF, and WOFF2 files are embedded in the rendering document. Choose fonts that cover every script used; do not assume one font covers all languages. Respect their embedding licenses. For example:

```text
python scripts/export_reports.py script-01.md --output-dir pdf --language te --font NotoSansTelugu.ttf --font NotoSans.ttf
```

Never silently transliterate or replace source quotations just to make the PDF render. Correct the font coverage and re-export. Browser shaping does not establish linguistic competence in the evaluation itself.

## Verify and deliver

The helper checks the PDF structure, page count, and presence of extractable text. After generation, reopen each file, check that the expected title, key sections, score and end of the report survived, and inspect rendering for clipping, broken tables, blank pages, and missing glyphs. For a batch with a shared template, inspect representative pages plus all unusual cases, languages, and long tables. Verify each file's content and existence, and confirm the count matches the input manifest.

When fonts or dependencies fail, retain the editable report and clearly mark PDF delivery unfinished. Use an equivalent local PDF tool if available and verify its result; do not rename a text file to `.pdf` or claim a Markdown-only output satisfies delivery.

Link to the actual absolute local PDF path in the final response. For a large batch, provide the local folder/index link, the comparison PDF, and the count of separate reports. Generated reports stay outside the skill repository and are not pushed to GitHub.

Implementation references: [Playwright PDF API](https://playwright.dev/python/docs/api/class-page#page-pdf) and [markdown-it-py HTML safety](https://markdown-it-py.readthedocs.io/en/latest/security.html).
