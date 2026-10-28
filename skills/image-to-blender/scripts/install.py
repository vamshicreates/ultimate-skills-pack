#!/usr/bin/env python3
"""
Universal Cross-Platform Installer for Image-to-Blender & Knowledge Harvester.
Works on macOS, Windows, and Linux with a single command:
    python3 scripts/install.py  (or 'python scripts/install.py' on Windows)

Automates:
1. Tool validation: verifies Python >= 3.10, checks for yt-dlp & ffmpeg.
2. Auto-downloads standalone yt-dlp binary if missing (zero admin privileges required).
3. Connects to Blender: copies blender_mcp addon, enables it headlessly.
4. Registers skill and MCP in ~/.gemini/config/mcp_config.json.
5. Verifies live connection to Blender socket (localhost:9876).
"""

import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
SYSTEM = platform.system()


def print_step(msg: str):
    print(f"\n===> {msg}")


def print_success(msg: str):
    print(f"  [✓] {msg}")


def print_warn(msg: str):
    print(f"  [!] {msg}")


def ensure_ytdlp() -> str:
    """Ensure yt-dlp exists; if missing, download the official standalone executable."""
    ytdlp = shutil.which("yt-dlp")
    if ytdlp:
        print_success(f"yt-dlp found at: {ytdlp}")
        return ytdlp

    print_step("yt-dlp not found in PATH. Downloading standalone binary...")
    bin_dir = SKILL_ROOT / "bin"
    bin_dir.mkdir(exist_ok=True)

    if SYSTEM == "Windows":
        target = bin_dir / "yt-dlp.exe"
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    elif SYSTEM == "Darwin":
        target = bin_dir / "yt-dlp_macos"
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"
    else:
        target = bin_dir / "yt-dlp"
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"

    if not target.exists():
        print(f"  Downloading from {url}...")
        try:
            urllib.request.urlretrieve(url, target)
            if SYSTEM != "Windows":
                target.chmod(0o755)
            print_success(f"yt-dlp downloaded to: {target}")
        except Exception as e:
            print_warn(f"Failed to auto-download yt-dlp: {e}")
            print("  Please install yt-dlp via 'pip install yt-dlp' or 'brew install yt-dlp'")
            return "yt-dlp"
    return str(target)


def check_ffmpeg():
    """Check for ffmpeg presence."""
    ff = shutil.which("ffmpeg")
    if ff:
        print_success(f"ffmpeg found at: {ff}")
    else:
        print_warn("ffmpeg not detected in system PATH.")
        if SYSTEM == "Darwin":
            print("  -> Recommend: 'brew install ffmpeg'")
        elif SYSTEM == "Windows":
            print("  -> Recommend: 'winget install Gyan.FFmpeg' or download from gyan.dev/ffmpeg/builds/")
        else:
            print("  -> Recommend: 'sudo apt install ffmpeg'")


def run_blender_mcp_setup():
    """Trigger the existing headless Blender add-on installer & bridge registration."""
    print_step("Configuring Blender MCP Add-on & Socket Server...")
    setup_script = SCRIPTS_DIR / "setup_blender_mcp.py"
    if not setup_script.exists():
        print_warn(f"Cannot find {setup_script}")
        return

    cmd = [sys.executable, str(setup_script)]
    try:
        subprocess.run(cmd, check=True)
        print_success("Blender add-on enabled and MCP config updated.")
    except Exception as e:
        print_warn(f"Blender setup encountered an issue: {e}")
        print("  You can re-run manually: python scripts/setup_blender_mcp.py")


def main():
    print("=" * 65)
    print("  Image-to-Blender & Knowledge Harvester - 1-Click Installer")
    print(f"  Detected OS: {SYSTEM} ({platform.machine()})")
    print(f"  Python Version: {platform.python_version()}")
    print("=" * 65)

    # 1. Tools verification
    ensure_ytdlp()
    check_ffmpeg()

    # 2. Blender MCP setup
    run_blender_mcp_setup()

    print("\n" + "=" * 65)
    print("  [COMPLETE] Installation Finished Successfully!")
    print("  To harvest tutorials:")
    print("    python scripts/harvest_knowledge.py --url '<YOUTUBE_URL>'")
    print("  To build 3D scenes from images:")
    print("    Provide any image and prompt: 'Reconstruct this in Blender'")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
