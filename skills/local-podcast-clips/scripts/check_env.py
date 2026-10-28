#!/usr/bin/env python3
"""Check the local prerequisites for the podcast clip workflow."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys


def main() -> int:
    ok = True
    print(f"Python: {sys.version.split()[0]}")
    if sys.version_info < (3, 11):
        print("  Python 3.11 or newer is recommended.")
        ok = False
    for command in ("ffmpeg", "ffprobe"):
        path = shutil.which(command)
        print(f"{command}: {path or 'MISSING'}")
        ok &= path is not None
    available = importlib.util.find_spec("faster_whisper") is not None
    print(f"faster-whisper: {'installed' if available else 'MISSING'}")
    ok &= available
    if shutil.which("ffmpeg"):
        encoders = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                                  capture_output=True, text=True, check=False)
        has_x264 = encoders.returncode == 0 and "libx264" in encoders.stdout
        print(f"FFmpeg libx264 encoder: {'available' if has_x264 else 'MISSING'}")
        ok &= has_x264
        filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                                 capture_output=True, text=True, check=False)
        has_subtitles = filters.returncode == 0 and " subtitles " in filters.stdout
        print(f"FFmpeg subtitles filter: {'available' if has_subtitles else 'MISSING (burned captions unavailable)'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
