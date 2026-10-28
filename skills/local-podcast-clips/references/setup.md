# Setup on another laptop

This skill needs Python 3.11 or 3.12, FFmpeg with FFprobe and the `libx264` encoder, and the Python package `faster-whisper`. Burning captions also needs FFmpeg's `subtitles` filter. Install FFmpeg from a build linked on the [official FFmpeg download page](https://ffmpeg.org/download.html), or through the operating system's usual package manager, and ensure `ffmpeg` and `ffprobe` are on `PATH`.

From the skill folder on macOS Terminal, with Python 3.12 installed (use `python3.11` instead if that is your installed version):

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install faster-whisper
.venv/bin/python scripts/check_env.py
```

On Windows PowerShell, with Python 3.12 installed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install faster-whisper
.\.venv\Scripts\python.exe scripts\check_env.py
```

Use the virtual environment's Python for `transcribe.py` and `render_clip.py` too. These commands do not require PowerShell script activation. Keep `.venv` in the skill folder; Git ignores it.

The first transcription downloads the selected Whisper model. For Telugu, use a multilingual model such as `medium` or `large-v3`, not a name ending in `.en`. The script defaults to CPU with int8 computation so it does not need CUDA on either platform. `medium` is the default balance between speed and accuracy; try `small` if the CPU is too slow, or `large-v3` if the hardware permits and accuracy needs improvement. A Windows NVIDIA GPU can be used with `--device cuda` after installing the CUDA libraries required by faster-whisper. Explicitly set `--language te` and leave translation off to keep Telugu output. Verify code-switched English names and Telugu spelling by listening.

To burn Telugu captions, install a font with Telugu glyphs, such as Noto Sans Telugu, on the laptop. Run a short test export and inspect the shaped glyphs; a successful FFmpeg exit code does not prove the captions look correct. The default export leaves captions as a separate `.srt`, which can be corrected and imported into an editor.

The helper does a single continuous cut with a fixed crop position. Use `--position 0` for the left edge, `0.5` for center, or `1` for the right edge; values between these are allowed. It cannot automatically track a moving speaker or combine multiple camera angles.

The workflow uses no OpusClip key or credits. Model downloads and package installation need an internet connection once; subsequent transcription can run locally.
