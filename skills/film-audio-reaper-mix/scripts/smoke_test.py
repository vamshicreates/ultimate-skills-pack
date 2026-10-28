#!/usr/bin/env python3
"""Exercise the REAPER session builder and WAV verifier with disposable media."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from contextlib import nullcontext
from pathlib import Path


def run(args: list[str]) -> None:
    subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", type=Path, help="Keep a new disposable session folder for an in-REAPER import and render test")
    args = parser.parse_args()
    for program in ("ffmpeg", "ffprobe"):
        if shutil.which(program) is None:
            raise RuntimeError(f"{program} is missing from PATH")
    scripts = Path(__file__).resolve().parent
    if args.keep:
        root = args.keep.resolve()
        if root.exists():
            raise FileExistsError(f"Disposable test folder already exists: {root}")
        root.mkdir(parents=True)
        workspace = nullcontext(str(root))
    else:
        workspace = tempfile.TemporaryDirectory(prefix="reaper-skill-smoke-")
    with workspace as temp:
        root = Path(temp)
        picture = root / "Picture_Master.mp4"
        package = root / "Example_Sound"
        cue_folder = package / "SC001_Opening" / "MUS001_Test_Music"
        cue_folder.mkdir(parents=True)
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
             "color=c=black:s=320x180:r=24:d=5", "-f", "lavfi", "-i",
             "sine=frequency=180:sample_rate=48000:duration=5", "-shortest", "-c:v", "mpeg4",
             "-q:v", "5", "-c:a", "aac", str(picture)])
        cue = cue_folder / "MUS001_Test_Music_mix.wav"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
             "sine=frequency=440:sample_rate=48000:duration=2", "-c:a", "pcm_s24le", str(cue)])
        plan = {
            "title": "Reaper_Smoke", "video": str(picture), "audio_package": str(package),
            "output_dir": str(root / "Output"),
            "source_audio": {"mode": "keep", "stream_index": 0, "gain_db": -4},
            "cues": [{"id": "MUS001", "asset": str(cue.relative_to(package)).replace("\\", "/"),
                      "start_seconds": 1.25, "gain_db": -6, "fade_in_seconds": 0.1,
                      "fade_out_seconds": 0.2}],
        }
        plan_file = root / "mix_plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")
        run([sys.executable, str(scripts / "prepare_session.py"), "--plan", str(plan_file), "--copy-video"])
        session = root / "Output" / "Reaper_Smoke_REAPER_Session"
        lua = (session / "00_Documents" / "Import_To_REAPER.lua").read_text(encoding="utf-8")
        assert "MUS001_Test_Music" in lua and "start = 1.25" in lua
        assert "__SESSION_DATA__" not in lua
        assert (session / "01_REAPER_Project" / "Media" / "Production" / "Production_Audio_48k24.wav").is_file()
        assert (session / "01_REAPER_Project" / "Media" / "Audio" /
                "SC001_Opening" / "MUS001_Test_Music" / "MUS001_Test_Music_mix.wav").is_file()
        local_plan = json.loads((session / "00_Documents" / "Mix_Plan.json").read_text(encoding="utf-8"))
        assert Path(local_plan["video"]).is_file()
        master = session / "02_Renders" / "Reaper_Smoke_Final_Mix_48k24.wav"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
             "sine=frequency=350:sample_rate=48000:duration=5", "-ac", "2", "-c:a", "pcm_s24le",
             str(master)])
        report = session / "02_Renders" / "Reaper_Smoke_Master_Report.json"
        run([sys.executable, str(scripts / "verify_master.py"), "--plan",
             str(session / "00_Documents" / "Mix_Plan.json"), "--master", str(master),
             "--report", str(report)])
        assert report.is_file()
    print("PASS: REAPER session preparation and WAV verification")
    if args.keep:
        print(f"IMPORT SCRIPT: {root / 'Output' / 'Reaper_Smoke_REAPER_Session' / '00_Documents' / 'Import_To_REAPER.lua'}")
    print("NEXT: run Import_To_REAPER.lua and render once inside REAPER on this PC")


if __name__ == "__main__":
    main()
