#!/usr/bin/env python3
"""timeline.py: the hand-off layer between chitram-film and any NLE or external tool (CONNECTORS.md).

Every edit decision lives in ONE portable file, `timeline.json` (seconds, not frames). From it we export
the formats real editors open, so a connected tool (DaVinci Resolve MCP, Premiere, a render farm, a
human editor) receives an EDITABLE timeline, not only a baked MP4.

  python timeline.py from-edl  WORK out.timeline.json [--src footage.mp4] [--fps 25] [--size 1080x1920]
        sf.py's edl.json (keep segments) -> V1 picture + A1 dialogue, source in/out preserved
  python timeline.py add-mix   tl.json mix.json      mixdown.py config -> A2 music, A3/A4 SFX clips (anchored
                                                      starts resolved, library slices -> real in/out)
  python timeline.py add-markers tl.json markers.json   [{"t":3.2,"name":"BRIEF","note":"...","color":"blue","dur":2}]
  python timeline.py export    tl.json --otio x.otio --xml x.xml --edl x.edl --markers-edl m.edl --csv m.csv
  python timeline.py check     tl.json               overlaps, gaps, missing files, out-of-range sources

timeline.json:
{ "name": "founder-edit", "fps": 25, "width": 1080, "height": 1920,
  "tracks": [ {"name": "V1 A-cam", "kind": "video",
               "clips": [{"name": "take3", "src": "C:/footage/a.mp4", "src_in": 12.40, "src_out": 15.92,
                          "rec_in": 0.0, "speed": 1.0, "enabled": true}]},
              {"name": "A1 dialogue", "kind": "audio", "clips": [...]} ],
  "markers": [{"t": 3.2, "dur": 2.0, "name": "BRIEF", "note": "C left: DIRECTION -> BLOCKING ...", "color": "blue"}] }
rec_out = rec_in + (src_out - src_in) / speed.  Track order = stacking order (V1 bottom).
OTIO is written as plain JSON (no dependency); if `opentimelineio` is installed, `export` re-reads it to
prove it parses. Speed survives in OTIO (LinearTimeWarp); FCP7 XML/EDL carry speed as a note only —
check retimed clips in the NLE (see LONGFORM.md §8 on native retime).
"""
import json, os, subprocess, sys
from xml.sax.saxutils import escape

COLORS = {"red": "RED", "blue": "BLUE", "green": "GREEN", "yellow": "YELLOW", "purple": "PURPLE",
          "cyan": "CYAN", "pink": "PINK", "orange": "ORANGE", "white": "WHITE"}


def opt(a, name, default=None, cast=str):
    return cast(a[a.index(name) + 1]) if name in a and a.index(name) + 1 < len(a) else default


def load(p): return json.load(open(p, encoding="utf-8"))


def save(p, o):
    json.dump(o, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False); print("->", p)


def rec_out(c): return c["rec_in"] + (c["src_out"] - c["src_in"]) / c.get("speed", 1.0)


def absp(p, base=None):
    if os.path.isabs(p): return os.path.normpath(p)
    return os.path.normpath(os.path.join(base or os.getcwd(), p))


def ffprobe():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "audio"))
    try:
        from ffbin import ffmpeg
        ff = ffmpeg(); fp = os.path.join(os.path.dirname(ff), "ffprobe" + (".exe" if os.name == "nt" else ""))
        return fp if os.path.exists(fp) else "ffprobe"
    except SystemExit:
        return "ffprobe"


def probe_dur(p):
    try:
        r = subprocess.run([ffprobe(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                           capture_output=True, text=True)
        return float(r.stdout.strip())
    except Exception:
        return None


# ------------------------------------------------------------------ builders
def from_edl(a):
    work, out = a[0], a[1]
    edl = load(os.path.join(work, "edl.json"))
    probe = load(os.path.join(work, "probe.json")) if os.path.exists(os.path.join(work, "probe.json")) else {}
    src = absp(opt(a, "--src") or edl["src"])
    fps = opt(a, "--fps", None, float) or 25.0
    w, h = (opt(a, "--size") or f"{probe.get('width', 1920)}x{probe.get('height', 1080)}").split("x")
    q = lambda t: round(round(t * fps) / fps, 6)        # frame grid, same as sf.py cut
    v, au, t = [], [], 0.0
    for i, (k0, k1) in enumerate(edl["keep"]):
        k0, k1 = q(k0), q(k1)
        if k1 - k0 < 1 / fps: continue
        c = {"name": f"keep{i + 1:03d}", "src": src, "src_in": k0, "src_out": k1, "rec_in": round(t, 6)}
        v.append(dict(c)); au.append(dict(c)); t += k1 - k0
    tl = {"name": os.path.basename(os.path.normpath(work)), "fps": fps, "width": int(w), "height": int(h),
          "tracks": [{"name": "V1 picture", "kind": "video", "clips": v},
                     {"name": "A1 dialogue", "kind": "audio", "clips": au}],
          "markers": [{"t": 0, "name": "SOURCE", "note": f"{len(v)} keeps from {os.path.basename(src)}; "
                                                         f"{len(edl.get('removed', []))} cuts", "color": "white"}]}
    save(out, tl)


def add_mix(a):
    tlp, mixp = a[0], a[1]
    tl, mix = load(tlp), load(mixp)
    base = os.path.dirname(os.path.abspath(mixp))
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "audio")
    sys.path.insert(0, os.path.abspath(here))
    import sfx_lib
    if mix.get("music"):
        M = mix["music"]; off = M.get("drop_track", 0) - M.get("drop_film", 0)
        p = absp(M["file"], base); d = probe_dur(p) or mix["duration"] + max(0, off)
        s_in, r_in = (off, 0.0) if off >= 0 else (0.0, -off)
        tl["tracks"].append({"name": "A2 music", "kind": "audio", "clips": [
            {"name": os.path.basename(p), "src": p, "src_in": round(s_in, 4),
             "src_out": round(min(d, s_in + mix["duration"] - r_in), 4), "rec_in": round(r_in, 4),
             "note": f"drop at film {M.get('drop_film', 0)}s; duck {M.get('duck_db', -10)} dB under voice"}]})
    lanes, used = [[]], {}
    for ev in sfx_lib.expand(mix.get("sfx", [])):
        if isinstance(ev, list): ev = {"t": ev[0], "sfx": ev[1], "align": "start"}
        if str(ev["sfx"]).startswith("synth:"):                  # generated in the mix: only in the SFX stem
            tl.setdefault("markers", []).append({"t": ev["t"], "name": "SUB", "color": "purple",
                                                 "note": f"{ev['sfx']} (in the SFX stem, not a clip)"})
            continue
        s = sfx_lib.resolve(ev["sfx"], used, ev.get("seed", 0))
        if s:
            t0 = s["slice"][0] if "slice" in s else 0.0
            t1 = s["slice"][1] if "slice" in s else s["file_dur"]
            al = ev.get("align") or s.get("anchor") or "onset"
            anc = {"start": s["start"], "onset": s["onset"], "peak": s["peak"], "end": s.get("body_end", s["end"])}[al]
            if ev.get("reverse"):     # NLE gets the forward clip + a note; reverse it there (or use the mixed stem)
                al += " (REVERSED in mix)"
            src, name = s["path"], f"{s['lib']}:{s['id']} {s['name']}"
            rec = ev["t"] - (anc - t0)
        else:
            src = absp(ev["sfx"], base); t0, t1 = 0.0, probe_dur(src) or 1.0; rec = ev["t"]; name = os.path.basename(src); al = "start"
        if rec < 0: t0 -= rec; rec = 0.0
        c = {"name": name, "src": src, "src_in": round(t0, 4), "src_out": round(t1, 4), "rec_in": round(rec, 4),
             "note": f"{al} on {ev['t']:.3f}s, {ev.get('gain_db', 'gain ' + str(ev.get('gain', '')))} dB"}
        lane = next((ln for ln in lanes if not ln or rec_out(ln[-1]) <= c["rec_in"]), None)
        if lane is None: lane = []; lanes.append(lane)                  # as many lanes as overlaps need
        lane.append(c)
    for i, ln in enumerate(lanes):
        if ln: tl["tracks"].append({"name": f"A{3 + i} sfx", "kind": "audio", "clips": ln})
    save(tlp, tl)


def add_markers(a):
    tl = load(a[0]); tl.setdefault("markers", []).extend(load(a[1])); save(a[0], tl)


# ------------------------------------------------------------------ checks
def check(a):
    tl = load(a[0]); bad = 0
    for tr in tl["tracks"]:
        cl = sorted(tr["clips"], key=lambda c: c["rec_in"])
        for i, c in enumerate(cl):
            if not os.path.exists(c["src"]): print(f"MISSING  {tr['name']}: {c['src']}"); bad += 1
            if c["src_out"] <= c["src_in"]: print(f"EMPTY    {tr['name']}: {c['name']}"); bad += 1
            if i and rec_out(cl[i - 1]) > c["rec_in"] + 1e-4:
                print(f"OVERLAP  {tr['name']}: {cl[i - 1]['name']} -> {c['name']} at {c['rec_in']:.3f}s"); bad += 1
            if i and tr["kind"] == "video" and 1e-4 < c["rec_in"] - rec_out(cl[i - 1]) < 1.0:
                print(f"FLASH-GAP {tr['name']}: {c['rec_in'] - rec_out(cl[i - 1]):.3f}s before {c['name']} "
                      f"(a lower layer shows through: is that intended? LONGFORM.md §5)")
    print("timeline OK" if not bad else f"{bad} problem(s)")
    return bad


# ------------------------------------------------------------------ OTIO (plain JSON, schema-compatible)
def rt(sec, fps): return {"OTIO_SCHEMA": "RationalTime.1", "rate": float(fps), "value": float(round(sec * fps))}


def tr_(s, d, fps): return {"OTIO_SCHEMA": "TimeRange.1", "start_time": rt(s, fps), "duration": rt(d, fps)}


def file_url(p):
    p = os.path.abspath(p).replace("\\", "/")
    return "file:///" + p.lstrip("/") if not p.startswith("/") else "file://" + p


def to_otio(tl):
    fps = tl["fps"]; tracks = []
    for tr in tl["tracks"]:
        kids, t = [], 0.0
        for c in sorted(tr["clips"], key=lambda c: c["rec_in"]):
            if c["rec_in"] - t > 1e-6:
                kids.append({"OTIO_SCHEMA": "Gap.1", "name": "", "source_range": tr_(0, c["rec_in"] - t, fps),
                             "effects": [], "markers": [], "metadata": {}, "enabled": True})
            fx = []
            if c.get("speed", 1.0) != 1.0:
                fx.append({"OTIO_SCHEMA": "LinearTimeWarp.1", "name": "", "effect_name": "LinearTimeWarp",
                           "time_scalar": c["speed"], "metadata": {}})
            kids.append({"OTIO_SCHEMA": "Clip.2", "name": c["name"], "enabled": c.get("enabled", True),
                         "source_range": tr_(c["src_in"], c["src_out"] - c["src_in"], fps),
                         "media_references": {"DEFAULT_MEDIA": {
                             "OTIO_SCHEMA": "ExternalReference.1", "name": os.path.basename(c["src"]),
                             "target_url": file_url(c["src"]), "available_range": None, "metadata": {},
                             "available_image_bounds": None}},
                         "active_media_reference_key": "DEFAULT_MEDIA", "effects": fx, "markers": [],
                         "metadata": {"chitram": {k: c[k] for k in ("note",) if k in c}}})
            t = rec_out(c)
        tracks.append({"OTIO_SCHEMA": "Track.1", "name": tr["name"], "kind": "Video" if tr["kind"] == "video" else "Audio",
                       "children": kids, "source_range": None, "effects": [], "markers": [], "metadata": {},
                       "enabled": True})
    marks = [{"OTIO_SCHEMA": "Marker.2", "name": m["name"], "color": COLORS.get(m.get("color", "red"), "RED"),
              "marked_range": tr_(m["t"], m.get("dur", 0), fps), "comment": m.get("note", ""), "metadata": {}}
             for m in tl.get("markers", [])]
    return {"OTIO_SCHEMA": "Timeline.1", "name": tl["name"], "global_start_time": rt(3600, fps),
            "metadata": {"chitram": {"width": tl.get("width"), "height": tl.get("height")}},
            "tracks": {"OTIO_SCHEMA": "Stack.1", "name": "tracks", "children": tracks, "source_range": None,
                       "effects": [], "markers": marks, "metadata": {}, "enabled": True}}


# ------------------------------------------------------------------ FCP7 XML (xmeml v5: Premiere + Resolve import)
def to_xmeml(tl):
    fps = tl["fps"]; ntsc = abs(fps - round(fps)) > .001; tb = int(round(fps))
    F = lambda s: int(round(s * fps))
    rate = f"<rate><timebase>{tb}</timebase><ntsc>{'TRUE' if ntsc else 'FALSE'}</ntsc></rate>"
    files, fid, n = {}, [0], [0]

    def file_el(c, kind):
        if c["src"] in files:
            return f'<file id="{files[c["src"]]}"/>'
        fid[0] += 1; files[c["src"]] = f"file-{fid[0]}"
        d = probe_dur(c["src"]) or c["src_out"]
        med = (f"<video><samplecharacteristics><width>{tl.get('width', 1920)}</width><height>{tl.get('height', 1080)}"
               f"</height></samplecharacteristics></video>" if kind == "video" else "") + \
              "<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics>" \
              "<channelcount>2</channelcount></audio>"
        return (f'<file id="{files[c["src"]]}"><name>{escape(os.path.basename(c["src"]))}</name>'
                f'<pathurl>{escape(file_url(c["src"]).replace("file:///", "file://localhost/"))}</pathurl>{rate}'
                f"<duration>{F(d)}</duration><media>{med}</media></file>")

    def track(tr):
        items = []
        for c in sorted(tr["clips"], key=lambda c: c["rec_in"]):
            n[0] += 1
            note = (f"speed {c['speed']}x — set it in the NLE. " if c.get("speed", 1) != 1 else "") + c.get("note", "")
            items.append(
                f'<clipitem id="clipitem-{n[0]}"><name>{escape(c["name"])}</name>'
                f'<enabled>{"TRUE" if c.get("enabled", True) else "FALSE"}</enabled>'
                f"<duration>{F(c['src_out'])}</duration>{rate}<start>{F(c['rec_in'])}</start><end>{F(rec_out(c))}</end>"
                f"<in>{F(c['src_in'])}</in><out>{F(c['src_out'])}</out>{file_el(c, tr['kind'])}"
                + (f"<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>"
                   if tr["kind"] == "audio" else "")
                + (f"<comments><mastercomment1>{escape(note)}</mastercomment1></comments>" if note else "")
                + "</clipitem>")
        return "<track>" + "".join(items) + "</track>"

    vt = "".join(track(t) for t in tl["tracks"] if t["kind"] == "video")
    at = "".join(track(t) for t in tl["tracks"] if t["kind"] == "audio")
    end = max([rec_out(c) for t in tl["tracks"] for c in t["clips"]] + [0])
    marks = "".join(f"<marker><name>{escape(m['name'])}</name><comment>{escape(m.get('note', ''))}</comment>"
                    f"<in>{F(m['t'])}</in><out>{F(m['t'] + m['dur']) if m.get('dur') else -1}</out></marker>"
                    for m in tl.get("markers", []))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5"><sequence id="sequence-1">'
            f"<name>{escape(tl['name'])}</name><duration>{F(end)}</duration>{rate}"
            f"<timecode>{rate}<string>01:00:00:00</string><frame>{F(3600)}</frame><displayformat>NDF</displayformat></timecode>"
            f"<media><video><format><samplecharacteristics>{rate}<width>{tl.get('width', 1920)}</width>"
            f"<height>{tl.get('height', 1080)}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics>"
            f"</format>{vt}</video><audio>{at}</audio></media>{marks}</sequence></xmeml>\n")


# ------------------------------------------------------------------ CMX3600 EDL (+ Resolve marker EDL)
def tc(sec, fps):
    f = int(round(sec * fps)); fr = int(round(fps))
    return f"{f // (3600 * fr):02d}:{f // (60 * fr) % 60:02d}:{f // fr % 60:02d}:{f % fr:02d}"


def to_edl(tl, kind="video"):
    fps = tl["fps"]; L = [f"TITLE: {tl['name']}", "FCM: NON-DROP FRAME", ""]; n = 0
    tr = next((t for t in tl["tracks"] if t["kind"] == kind), None)
    for c in sorted(tr["clips"] if tr else [], key=lambda c: c["rec_in"]):
        n += 1
        L.append(f"{n:03d}  AX       {'V' if kind == 'video' else 'A'}     C        {tc(c['src_in'], fps)} "
                 f"{tc(c['src_out'], fps)} {tc(3600 + c['rec_in'], fps)} {tc(3600 + rec_out(c), fps)}")
        if c.get("speed", 1) != 1:
            L.append(f"M2   AX       {c['speed'] * fps:05.1f}                {tc(c['src_in'], fps)}")
        L += [f"* FROM CLIP NAME: {os.path.basename(c['src'])}", f"* SOURCE FILE: {c['src']}", ""]
    return "\n".join(L) + "\n"


def to_marker_edl(tl):
    """Resolve: Timeline > Import > Timeline Markers from EDL."""
    fps = tl["fps"]; L = [f"TITLE: {tl['name']} markers", "FCM: NON-DROP FRAME", ""]
    for i, m in enumerate(tl.get("markers", []), 1):
        a = tc(3600 + m["t"], fps); b = tc(3600 + m["t"] + max(m.get("dur", 0), 1 / fps), fps)
        col = "Resolve" + "Color" + m.get("color", "blue").capitalize()
        L += [f"{i:03d}  001      V     C        {a} {b} {a} {b}",
              f" |C:{col} |M:{m['name']}: {m.get('note', '')[:180]} |D:{max(1, int(round(m.get('dur', 0) * fps)))}", ""]
    return "\n".join(L) + "\n"


def export(a):
    tl = load(a[0])
    if opt(a, "--otio"):
        p = opt(a, "--otio"); json.dump(to_otio(tl), open(p, "w", encoding="utf-8"), indent=1); print("->", p)
        try:
            import opentimelineio as otio
            t = otio.adapters.read_from_file(p)
            print(f"   otio re-read OK: {len(t.tracks)} tracks, {t.duration().to_seconds():.2f}s")
        except ImportError:
            print("   (pip install opentimelineio to verify the file parses)")
    for flag, fn in (("--xml", to_xmeml), ("--edl", to_edl), ("--markers-edl", to_marker_edl)):
        if opt(a, flag):
            open(opt(a, flag), "w", encoding="utf-8").write(fn(tl)); print("->", opt(a, flag))
    if opt(a, "--csv"):
        with open(opt(a, "--csv"), "w", encoding="utf-8") as f:
            f.write("timecode,seconds,duration,name,note,color\n")
            for m in tl.get("markers", []):
                f.write(f"{tc(3600 + m['t'], tl['fps'])},{m['t']:.3f},{m.get('dur', 0)},\"{m['name']}\","
                        f"\"{m.get('note', '').replace(chr(34), chr(39))}\",{m.get('color', '')}\n")
        print("->", opt(a, "--csv"))


if __name__ == "__main__":
    cmds = {"from-edl": from_edl, "add-mix": add_mix, "add-markers": add_markers, "export": export, "check": check}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__); sys.exit(1)
    r = cmds[sys.argv[1]](sys.argv[2:])
    sys.exit(1 if sys.argv[1] == "check" and r else 0)
