# Windows installation and verification

Use PowerShell on the Windows PC. Python 3.11 or newer, Git, FFmpeg, and ffprobe must be installed. Get them from their official download pages if missing. Ensure `git`, `ffmpeg`, and `ffprobe` work in a new PowerShell window before continuing. FFmpeg and ffprobe normally come in the same FFmpeg `bin` directory; put that directory on `PATH`.

The public skill repository is `https://github.com/vamshicreates/film-audio-python`. Install it in the current Windows user's Codex skills folder. An existing installation can be updated with `git -C $SkillDir pull --ff-only` if it is a clean Git checkout. If it contains local edits, preserve those edits before updating.

```powershell
$SkillDir = Join-Path $HOME '.codex\skills\film-audio-python'
$VenvDir = Join-Path $HOME '.codex\venvs\film-audio-python'

New-Item -ItemType Directory -Force (Split-Path $SkillDir) | Out-Null
git clone https://github.com/vamshicreates/film-audio-python.git $SkillDir
py -3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'
py -3 -m venv $VenvDir
$Python = Join-Path $VenvDir 'Scripts\python.exe'
& $Python --version
& $Python -m pip install --upgrade pip
& $Python -m pip install -r (Join-Path $SkillDir 'requirements.txt')
ffmpeg -version
ffprobe -version
& $Python (Join-Path $SkillDir 'scripts\smoke_test.py')
```

To install the separate finishing skill from the same repository, copy its folder alongside the first skill and run its own test:

```powershell
$FinishDir = Join-Path $HOME '.codex\skills\film-audio-video-finish'
New-Item -ItemType Directory -Force $FinishDir | Out-Null
Copy-Item -Path (Join-Path $SkillDir 'skills\film-audio-video-finish\*') -Destination $FinishDir -Recurse -Force
& $Python (Join-Path $FinishDir 'scripts\smoke_test.py')
```

If `py -3` selects a Python older than 3.11, install a current Python and select it explicitly with the Python launcher (for example, `py -3.11`). Recreate the virtual environment with that interpreter. If `py` is unavailable but a suitable `python` command exists, use `python -m venv $VenvDir` after checking its version. Do not start film processing until the smoke test prints `PASS`.

The smoke test creates its files in a temporary directory and removes them afterward. It does not need a film. For a real film, keep all output in a separate project folder and use Windows paths or `pathlib.Path`; do not assume Unix `/tmp` or `python3` exists. The script examples in `SKILL.md` describe the output format; use `$Python` from this guide to run them in PowerShell.
