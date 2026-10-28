# Windows, macOS and Linux setup

Use Python 3.10 or newer. On Windows use `py -3` or `python`; on macOS/Linux use `python3` or `python`. Keep paths quoted when they contain spaces. The scripts use pathlib and explicit UTF-8; no macOS-specific paths or shell commands are required.

The repository installer with `--with-runtime` creates a shared ReportLab environment at `<Codex home>/skill-runtimes/mru-aicc-assessments`. Codex home is the configured `CODEX_HOME`, otherwise the current user's `.codex` folder. On Windows the interpreter is `Scripts/python.exe` inside that runtime; on macOS/Linux it is `bin/python`. Discover it from the current environment rather than copying a path from another machine. An available Codex bundled Python with ReportLab is also suitable.

Windows PowerShell report command (replace placeholders with real paths):

```powershell
& "C:\Users\YOUR_NAME\.codex\skill-runtimes\mru-aicc-assessments\Scripts\python.exe" "C:\Users\YOUR_NAME\.codex\skills\mru-aicc-assessment-3-self-avatar\scripts\build_report.py" "student.json" --output-dir "reports"
```

macOS/Linux report command:

```sh
"$HOME/.codex/skill-runtimes/mru-aicc-assessments/bin/python" "$HOME/.codex/skills/mru-aicc-assessment-3-self-avatar/scripts/build_report.py" "student.json" --output-dir "reports"
```

If `CODEX_HOME` is set, substitute that directory. For a manual isolated dependency setup, create a venv using the available Python, then run its Python with `-m pip install -r <installed-skill>/requirements.txt`. Do not assume that the system Python already contains ReportLab.

Google Drive/Sheets must be connected in the current Codex environment for live reads, uploads and spreadsheet writes. Installation alone does not grant file access. Use the available connected tools and Google Sheets skill when present; if that skill is absent, use the connected tool documentation directly. If no Google integration is available, generate the local assessment outputs and state that upload and sheet delivery remain pending. Do not claim a local CSV is a Google Sheets result.

FFmpeg and FFprobe are optional for media extraction. Find them using the current environment/PATH. The skills still require actual moving-picture and audio review for final video marks. Missing tools or inaccessible media must be reflected in assessment status.
