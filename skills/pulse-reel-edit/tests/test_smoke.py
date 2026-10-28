"""End-to-end smoke test on synthetic footage (runs on macOS, Windows and Linux CI).

python tests/test_smoke.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pulsereel.media import ffmpeg_exe, probe  # noqa: E402


def make_footage(d: Path):
    ff = ffmpeg_exe()
    d.mkdir(parents=True, exist_ok=True)
    clips = [
        # vertical 60 fps clip with a moving red "dress"
        ("a_spin60.mp4", "testsrc2=size=720x1280:rate=60:duration=5,drawbox=x='200+120*sin(t*3)':y=500:w=320:h=520:color=red@1:t=fill"),
        ("b_pose.mp4", "testsrc2=size=720x1280:rate=30:duration=5,drawbox=x=220:y=600:w=280:h=500:color=red@1:t=fill"),
        ("c_wide169.mp4", "testsrc2=size=1280x720:rate=30:duration=5,drawbox=x='500+200*sin(t*2)':y=200:w=260:h=400:color=red@1:t=fill"),
        ("d_broll.mp4", "smptehdbars=size=720x1280:rate=30:duration=5"),
    ]
    for name, src in clips:
        subprocess.run([ff, "-y", "-v", "error", "-f", "lavfi", "-i", src, "-c:v", "libx264", "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p", str(d / name)], check=True)
    # 120 BPM click track with a louder second half (a 'drop' at 6 s)
    expr = "0.3*sin(2*PI*220*t)*exp(-40*mod(t,0.5))*(1+1.5*gte(t,6))+0.05*sin(2*PI*110*t)"
    subprocess.run([ff, "-y", "-v", "error", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=44100:d=20",
                    "-c:a", "libmp3lame", "-q:a", "4", str(d / "song.mp3")], check=True)


def run(*args):
    cmd = [sys.executable, str(ROOT / "pulse.py"), *map(str, args)]
    print("$", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        make_footage(td / "footage")
        work = td / "work"
        run("doctor")
        run("analyze", td / "footage", "--out", work, "--duration", 12)
        assert (work / "analysis.json").exists()
        assert list((work / "sheets").glob("*.jpg")), "no contact sheets"
        run("plan", work / "analysis.json", "--title", "Test", "--duration", 12,
            "--render-to", work / "renders" / "reel.mp4")
        run("render", work / "timeline.json", "--preview", "--no-mask")
        out = work / "renders" / "reel_preview.mp4"
        info = probe(out)
        assert abs(info.duration - 12) < 0.3, info.duration
        assert (info.width, info.height) == (540, 960), (info.width, info.height)
        run("qa", out, "--timeline", work / "timeline.json")
        assert (work / "renders" / "reel_preview_qa" / "rhythm.png").exists()
        run("luts", "--out", work / "luts")
        assert (work / "luts" / "pulse_moody.cube").exists()
        run("filmcraft", work / "timeline.json", "--script-only")
        assert (work / "filmcraft" / "filmcraft_plan.json").exists()
        print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
