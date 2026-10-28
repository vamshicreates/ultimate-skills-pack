#!/usr/bin/env python3
"""pulse-reel-edit: beat-synced 'focus pulse + colour pop' reel editor.

  python pulse.py doctor
  python pulse.py analyze  <footage_dir> [--song song.mp3] [--out work]
  python pulse.py plan     work/analysis.json [--title "Baby"] [--duration 30] [--out work/timeline.json]
  python pulse.py render   work/timeline.json [--preview] [--grade none] [--split-shots DIR]
  python pulse.py qa       renders/reel.mp4 --timeline work/timeline.json
  python pulse.py lookbook clip.mov [--t 3.2]            # compare looks on one frame
  python pulse.py luts     [--out luts/]                 # .cube files for DaVinci Resolve / FilmCraft
  python pulse.py filmcraft work/timeline.json [--mode native|baked] [--bridge 127.0.0.1:9876]

Works the same on macOS, Windows and Linux (Python 3.10+).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def cmd_doctor(a):
    from pulsereel.doctor import doctor

    sys.exit(0 if doctor(verbose=True) else 1)


def cmd_analyze(a):
    from pulsereel.analyze import analyze_folder

    print(f"Analysing {a.footage} …")
    hue = {"red": 0, "orange": 25, "yellow": 55, "green": 120, "teal": 175, "blue": 215, "purple": 275, "pink": 330}
    ph = hue.get(str(a.protect).lower(), None)
    ph = float(a.protect) if ph is None else ph
    res = analyze_folder(a.footage, a.out, a.song, protect_hue=ph, target_duration=a.duration)
    print(f"\nWrote {Path(a.out) / 'analysis.json'}  ({len(res['clips'])} clips)")
    print(f"Contact sheets: {Path(a.out) / 'sheets'}  <- LOOK at these before planning")


def cmd_plan(a):
    from pulsereel.media import load_json
    from pulsereel.plan import auto_plan
    from pulsereel.timeline import save

    an = load_json(a.analysis)
    looks = [s.strip() for s in a.looks.split(",")] if a.looks else None
    tl = auto_plan(an, duration=a.duration, title=a.title, looks=looks, out_path=a.render_to,
                   music_start=a.music_start, slowmo_speed=a.slowmo, width=a.width, height=a.height, fps=a.fps)
    out = a.out or str(Path(a.analysis).with_name("timeline.json"))
    save(tl, out)
    print(f"Wrote {out}: {len(tl['shots'])} shots, {tl['duration']}s, music start {tl['music']['start']}s")
    for s in tl["shots"]:
        print(f"  {s['id']}  {s['dur']:5.2f}s  in={s['in']:7.2f}  x{s['speed']:<4}  {s['color']:<9} {s['transition']:<10} {s['note']}")


def cmd_render(a):
    from pulsereel.render import render
    from pulsereel.timeline import load

    tl = load(a.timeline)
    render(tl, out_path=a.out, preview=a.preview, grade=a.grade, split_dir=a.split_shots,
           prores=a.prores, no_titles_mask=a.no_mask)


def cmd_qa(a):
    from pulsereel.qa import qa
    from pulsereel.timeline import load

    tl = load(a.timeline) if a.timeline else None
    rep = qa(a.video, tl, a.out)
    print(rep["metrics"])
    print(f"Chart: {rep['chart']}")
    for s in rep["sheets"]:
        print(f"Sheet: {s}")


def cmd_luts(a):
    from pulsereel.looks import LOOKS, write_cube

    out = Path(a.out)
    for name in LOOKS:
        if name == "none":
            continue
        p = write_cube(name, out / f"pulse_{name}.cube", title=f"pulse-reel-edit {name}")
        print(f"  {p}")


def cmd_lookbook(a):
    from pulsereel.looks import lookbook

    out = a.out or str(Path(a.source).with_suffix("")) + "_lookbook.jpg"
    print(lookbook(a.source, out, a.t))


def cmd_filmcraft(a):
    from pulsereel.filmcraft import build_filmcraft

    build_filmcraft(a.timeline, project=a.project, mode=a.mode, cli=a.cli, render_first=not a.no_render,
                    execute=not a.script_only, bridge=a.bridge, export=a.export)


def main(argv=None):
    p = argparse.ArgumentParser(prog="pulse", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("doctor", help="check Python packages, ffmpeg, fonts, FilmCraft")
    s.set_defaults(fn=cmd_doctor)

    s = sub.add_parser("analyze", help="probe + score every clip, beat-map the song, draw contact sheets")
    s.add_argument("footage")
    s.add_argument("--song", help="music file (default: first audio file in the footage folder)")
    s.add_argument("--out", default="work")
    s.add_argument("--protect", default="red", help="colour kept during colour-pop: red|orange|yellow|green|teal|blue|purple|pink or a hue in degrees")
    s.add_argument("--duration", type=float, default=30.0, help="target reel length, used to pick the music window")
    s.set_defaults(fn=cmd_analyze)

    s = sub.add_parser("plan", help="auto-draft a timeline in the reference style")
    s.add_argument("analysis")
    s.add_argument("--out")
    s.add_argument("--title", help="script word(s) placed behind the subject on the hero shot, e.g. 'Baby'")
    s.add_argument("--duration", type=float, default=30.0)
    s.add_argument("--looks", help="comma list for intro,drop,outro (default moody,airy,overcast) or one look: natural")
    s.add_argument("--music-start", type=float, help="override where in the song the reel starts (seconds)")
    s.add_argument("--slowmo", type=float, default=0.5, help="playback speed for 48fps+ clips (0.5 = half speed)")
    s.add_argument("--render-to", default="renders/reel.mp4")
    s.add_argument("--width", type=int, default=1080)
    s.add_argument("--height", type=int, default=1920)
    s.add_argument("--fps", type=int, default=30)
    s.set_defaults(fn=cmd_plan)

    s = sub.add_parser("render", help="render a timeline")
    s.add_argument("timeline")
    s.add_argument("--out")
    s.add_argument("--preview", action="store_true", help="half resolution, fast encode")
    s.add_argument("--grade", choices=["on", "none"], default="on", help="'none' = skip correction + look (for grading in DaVinci)")
    s.add_argument("--split-shots", help="also write one file per shot into this folder (FilmCraft/Resolve handoff)")
    s.add_argument("--prores", action="store_true", help="ProRes 422 HQ .mov intermediate instead of H.264")
    s.add_argument("--no-mask", action="store_true", help="skip subject cut-out (titles drawn in front)")
    s.set_defaults(fn=cmd_render)

    s = sub.add_parser("qa", help="measure a render: rhythm chart + contact sheets")
    s.add_argument("video")
    s.add_argument("--timeline")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_qa)

    s = sub.add_parser("luts", help="export the looks as .cube LUTs")
    s.add_argument("--out", default="luts")
    s.set_defaults(fn=cmd_luts)

    s = sub.add_parser("lookbook", help="one frame through every look, side by side")
    s.add_argument("source", help="clip or still image")
    s.add_argument("--t", type=float, help="time in the clip (default: middle)")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_lookbook)

    s = sub.add_parser("filmcraft", help="build the edit as a FilmCraft project (headless CLI or MCP script)")
    s.add_argument("timeline")
    s.add_argument("--project", help="output .fcproj (default next to the timeline)")
    s.add_argument("--mode", choices=["baked", "native"], default="native",
                   help="native = original clips + FilmCraft effects, all editable (default); baked = pre-styled shots, exact look")
    s.add_argument("--bridge", help="drive the running FilmCraft app live, e.g. 127.0.0.1:9876 (start it with: filmcraft --control 9876)")
    s.add_argument("--export", help="also export the FilmCraft sequence to this .mp4")
    s.add_argument("--cli", help="path to filmcraft-cli (default: auto-detect)")
    s.add_argument("--no-render", action="store_true", help="reuse existing split shots")
    s.add_argument("--script-only", action="store_true", help="only write the command script (for the MCP command_batch tool)")
    s.set_defaults(fn=cmd_filmcraft)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
