#!/usr/bin/env python3
"""
Zero-Touch Cross-Platform Installer & Verifier for `podcast-editor` (Windows & macOS).

Automates on both Windows and macOS:
1. Mirrors the skill into `<HOME>/.gemini/config/skills/podcast-editor` (using `Path.home()` so it works
   identically in Windows PowerShell/CMD and macOS zsh/bash).
2. Enables Adobe CEP `PlayerDebugMode = 1` across `CSXS.9`–`CSXS.12` (`HKCU\\Software\\Adobe\\CSXS.*` on Windows,
   `defaults write com.adobe.CSXS.*` on macOS — no admin required).
3. Installs the bundled Premiere Pro CEP HTTP Bridge (`assets/cep_extension` -> `com.vamshicreates.premieremcp`)
   into `%APPDATA%\\Adobe\\CEP\\extensions` (Windows) or `~/Library/Application Support/Adobe/CEP/extensions` (macOS).
4. Checks DaVinci Resolve and Adobe Premiere Pro installations, `ffmpeg`/`ffprobe` binaries, and optionally
   installs the `laya` neural decision model (`--install-laya`).
"""

import argparse
import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from laya_decision_gate import install_laya_package  # noqa: E402
from live_davinci_podcast_builder import get_resolve_paths  # noqa: E402
from live_premiere_podcast_builder import ensure_cep_extension_installed, find_premiere_executable  # noqa: E402
from podcast_ingest_sync import find_binary  # noqa: E402


def sync_to_global_skills_dir() -> Dict[str, Any]:
    """Copy the skill to `<HOME>/.gemini/config/skills/podcast-editor` across Windows & macOS."""
    global_target = (Path.home() / ".gemini" / "config" / "skills" / "podcast-editor").resolve()
    src_root = SKILL_ROOT.resolve()
    if src_root == global_target:
        return {"synced": True, "global_skill_path": str(global_target), "note": "Already running from global skill path"}

    try:
        global_target.parent.mkdir(parents=True, exist_ok=True)
        if global_target.exists():
            shutil.rmtree(global_target)
        shutil.copytree(
            src_root,
            global_target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store"),
        )
        return {"synced": True, "global_skill_path": str(global_target)}
    except Exception as exc:
        return {"synced": False, "global_skill_path": str(global_target), "error": str(exc)}


def run_setup(install_laya: bool = False) -> Dict[str, Any]:
    cep_res = ensure_cep_extension_installed()
    global_sync = sync_to_global_skills_dir()
    ppro_bin = find_premiere_executable()
    resolve_info = get_resolve_paths()
    ffmpeg_bin = find_binary("ffmpeg")
    ffprobe_bin = find_binary("ffprobe")

    laya_status: Dict[str, Any] = {"installed_check": False}
    if install_laya:
        laya_status = install_laya_package()
    else:
        try:
            import importlib.util

            laya_status = {"installed": importlib.util.find_spec("laya") is not None}
        except Exception:
            laya_status = {"installed": False}

    return {
        "status": "ready",
        "os": platform.system(),
        "platform_release": platform.release(),
        "python_executable": sys.executable,
        "global_skill_sync": global_sync,
        "ffmpeg": ffmpeg_bin,
        "ffprobe": ffprobe_bin,
        "premiere_pro": {
            "installed": ppro_bin is not None,
            "executable": ppro_bin,
            "cep_bridge_setup": cep_res,
            "priority": "primary",
        },
        "davinci_resolve": {
            "installed": resolve_info.get("installed", False),
            "app_path": resolve_info.get("app_path"),
            "scripting_api_dir": resolve_info.get("api_dir"),
            "priority": "secondary",
        },
        "laya_decision_model": laya_status,
        "next_step": "Ask the user whether they prefer to edit with Adobe Premiere Pro (Primary) or DaVinci Resolve.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-platform setup for podcast-editor (Windows & macOS)")
    parser.add_argument("--install-laya", action="store_true", help="Also run `pip install laya` during setup")
    args = parser.parse_args()

    res = run_setup(install_laya=args.install_laya)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
