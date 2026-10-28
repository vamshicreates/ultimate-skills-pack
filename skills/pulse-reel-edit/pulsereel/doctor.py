"""Environment check: everything the skill needs, with the fix for each missing piece."""
from __future__ import annotations

import importlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = [("numpy", "numpy"), ("cv2", "opencv-python"), ("PIL", "pillow"), ("librosa", "librosa"),
            ("scipy", "scipy"), ("matplotlib", "matplotlib"), ("imageio_ffmpeg", "imageio-ffmpeg")]
OPTIONAL = [("rembg", '"rembg[cpu]"', "titles behind the subject"),
            ("onnxruntime", "onnxruntime", "titles behind the subject")]


def filmcraft_cli() -> str | None:
    """Locate filmcraft-cli (FilmCraft from the ArtCraft suite)."""
    env = os.environ.get("FILMCRAFT_CLI")
    if env and Path(env).exists():
        return env
    w = shutil.which("filmcraft-cli")
    if w:
        return w
    home = Path.home()
    cands = []
    if sys.platform == "win32":
        la = os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local"))
        cands += [Path(la) / "Programs" / "ArtCraft" / "FilmCraft" / "filmcraft-cli.exe",
                  Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "ArtCraft" / "FilmCraft" / "filmcraft-cli.exe",
                  Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "ArtCraft" / "FilmCraft" / "filmcraft-cli.exe",
                  Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "FilmCraft" / "filmcraft-cli.exe"]
    else:
        cands += [home / "bin" / "filmcraft-cli", home / ".local" / "bin" / "filmcraft-cli",
                  Path("/usr/local/bin/filmcraft-cli"), Path("/opt/homebrew/bin/filmcraft-cli"),
                  Path("/usr/bin/filmcraft-cli"), home / "Applications" / "filmcraft-cli" / "filmcraft-cli"]
    for c in cands:
        if c.exists():
            return str(c)
    return None


def doctor(verbose: bool = True) -> bool:
    ok = True

    def say(flag, msg):
        if verbose:
            print(f"  [{'ok' if flag is True else ('--' if flag is None else '!!')}] {msg}")

    print(f"pulse-reel-edit doctor  ({platform.system()} {platform.machine()}, Python {sys.version.split()[0]})")
    if sys.version_info < (3, 10):
        say(False, "Python 3.10+ required")
        ok = False
    for mod, pkg in REQUIRED:
        try:
            importlib.import_module(mod)
            say(True, f"{mod}")
        except Exception:
            say(False, f"{mod} missing -> python -m pip install {pkg}")
            ok = False
    for mod, pkg, why in OPTIONAL:
        try:
            importlib.import_module(mod)
            say(True, f"{mod} (optional: {why})")
        except Exception:
            say(None, f"{mod} not installed (optional: {why}) -> python -m pip install {pkg}")
    try:
        from .media import ffmpeg_exe, run

        ff = ffmpeg_exe()
        enc = run([ff, "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        say(True, f"ffmpeg: {ff}")
        if "libx264" not in enc:
            say(False, "ffmpeg has no libx264 encoder -> python -m pip install -U imageio-ffmpeg")
            ok = False
    except Exception as exc:
        say(False, f"ffmpeg: {exc}")
        ok = False
    font = ROOT / "assets" / "fonts" / "GreatVibes-Regular.ttf"
    say(font.exists() or False, f"title font {'found' if font.exists() else 'missing: ' + str(font)}")
    ok = ok and font.exists()
    fc = filmcraft_cli()
    if fc:
        try:
            v = subprocess.run([fc, "--version"], capture_output=True, text=True, timeout=20).stdout.strip()
        except Exception:
            v = ""
        say(True, f"FilmCraft CLI: {fc} {v}")
    else:
        say(None, "FilmCraft CLI not found (optional: edit inside FilmCraft via MCP). See README > FilmCraft. "
                  "Set FILMCRAFT_CLI=/path/to/filmcraft-cli if it is installed somewhere else.")
    print("ready." if ok else "fix the [!!] items above, then run doctor again.")
    return ok
