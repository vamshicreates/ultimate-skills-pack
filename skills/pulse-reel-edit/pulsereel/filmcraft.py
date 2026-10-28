"""Build the edit inside FilmCraft (the open-source, Premiere-class editor from the ArtCraft suite)
through its MCP server (`filmcraft-cli mcp`).

Two modes:
  baked  - every shot is rendered with the full pulse look (exactly what `render` makes) and laid on V1,
           music on A1, beats as markers. Edit order/trims/music in FilmCraft; the look is locked in.
  native - the ORIGINAL clips are cut on the beat inside FilmCraft and the style is rebuilt with
           FilmCraft's own effects, all keyframed and editable:
             Lumetri Color (our .cube look + exposure correction)  -> grade
             Leave Color (protected colour, keyframed amount)      -> colour pop
             Gaussian Blur (keyframed blurriness)                  -> focus pulse
             Motion scale keyframes                                -> push-ins
             Push / Cross Dissolve / Dip to White transitions      -> push, blend, flash, bleach
             Title plate (PNG sequence with the subject cut-out)   -> text behind the subject (V2)
             Adjustment layer + Noise                              -> grain (V3)

Headless (default) writes a .fcproj you open in FilmCraft. With --bridge the same commands drive the
running FilmCraft app live (start it with `filmcraft --control 9876`), so you watch the timeline build.
"""
from __future__ import annotations

import base64
import copy
import json
import math
import os
import subprocess
from pathlib import Path

import cv2
import numpy as np

from . import fx
from .doctor import filmcraft_cli
from .looks import LOOKS, shot_correction, write_cube
from .media import FrameReader, probe, save_json
from .plan import hue_to_hex
from .render import ShotRenderer, blur_curve, colour_curve, render
from .timeline import load, look_at

TPS = 254_016_000_000  # FilmCraft ticks per second


def ticks(sec: float) -> int:
    return int(round(sec * TPS))


class FilmCraftMCP:
    """Minimal MCP (JSON-RPC over stdio) client for `filmcraft-cli mcp`."""

    def __init__(self, cli: str, bridge: str | None = None, log: list | None = None):
        args = [cli, "mcp"] + (["--bridge", bridge] if bridge else [])
        self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, encoding="utf-8", env=os.environ.copy())
        self._id = 0
        self.log = log if log is not None else []
        r = self._rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                     "clientInfo": {"name": "pulse-reel-edit", "version": "1.0"}})
        if "result" not in r:
            raise RuntimeError(f"FilmCraft MCP did not initialise: {r}")
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _send(self, obj):
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()

    def _rpc(self, method, params):
        self._id += 1
        self._send({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})
        while True:
            line = self.p.stdout.readline()
            if not line:
                err = self.p.stderr.read()[-800:] if self.p.poll() is not None else ""
                raise RuntimeError(f"FilmCraft MCP closed the connection. {err}")
            msg = json.loads(line)
            if msg.get("id") == self._id:
                return msg

    def tool(self, name: str, args: dict, check: bool = True):
        r = self._rpc("tools/call", {"name": name, "arguments": args})
        res = r.get("result", {})
        content = res.get("content", [])
        texts = [c.get("text", "") for c in content if c.get("type") == "text"]
        images = [c for c in content if c.get("type") == "image"]
        self.log.append({"tool": name, "arguments": args, "ok": not res.get("isError"), "reply": (texts[0][:300] if texts else "")})
        if res.get("isError") or "error" in r:
            msg = texts[0] if texts else json.dumps(r.get("error"))
            if check:
                raise RuntimeError(f"{name} {json.dumps(args)[:200]} -> {msg}")
            return None
        if images:
            return images
        try:
            return json.loads(texts[0]) if texts else None
        except Exception:
            return texts[0] if texts else None

    def run(self, cid: str, params: dict | None = None, check: bool = True):
        return self.tool("command_run", {"id": cid, "params": params or {}}, check=check)

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()


# ------------------------------------------------------------------ title plates
def render_title_plates(tl: dict, out_dir: Path, W: int, H: int, fps: float) -> list[dict]:
    """Transparent PNG sequences of each title with the subject cut-out baked in."""
    plates = []
    if not tl["titles"]:
        return plates
    masker = fx.SubjectMasker(work_w=448)
    tl_nt = copy.deepcopy(tl)
    tl_nt["titles"] = []
    for n, ti in enumerate(tl["titles"]):
        d = out_dir / f"title_{n + 1:02d}"
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.png"):
            old.unlink()
        k0, k1 = int(round(ti["start"] * fps)), int(round(ti["end"] * fps))
        idx = 0
        for si, s in enumerate(tl["shots"]):
            sk0, sk1 = int(round(s["start"] * fps)), int(round((s["start"] + s["dur"]) * fps))
            a, b = max(k0, sk0), min(k1, sk1)
            if a >= b:
                continue
            sr = ShotRenderer(tl_nt, si, W, H, fps, a, b, lambda name: None, None, False)
            masker.reset()
            for k, frame in sr.frames():
                m = masker(frame) if (masker.ok and ti.get("behind_subject", True)) else None
                rgba = fx.title_rgba(frame.shape, ti, k / fps - ti["start"], ti["end"] - ti["start"], m)
                cv2.imwrite(str(d / f"title_{idx:05d}.png"), rgba)
                idx += 1
        plates.append({"dir": str(d), "first": str(d / "title_00000.png"), "start": k0 / fps,
                       "dur": idx / fps, "frames": idx})
        print(f"  title plate '{ti['text']}': {idx} frames -> {d}")
    return plates


# ------------------------------------------------------------------ builders
def _keys(values: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """Thin a sampled curve to keyframes: keep ends, turning points and changes > tol."""
    if not values:
        return []
    out = [values[0]]
    for i in range(1, len(values) - 1):
        t, v = values[i]
        pv, nv = values[i - 1][1], values[i + 1][1]
        turning = (v - pv) * (nv - v) <= 0 and abs(nv - pv) > 1e-6
        if turning or abs(v - out[-1][1]) > tol:
            out.append((t, v))
    out.append(values[-1])
    dedup = [out[0]]
    for t, v in out[1:]:
        if t - dedup[-1][0] > 1e-4:
            dedup.append((t, v))
    return dedup


def build_filmcraft(timeline_path: str, project: str | None = None, mode: str = "baked", cli: str | None = None,
                    render_first: bool = True, execute: bool = True, bridge: str | None = None,
                    export: str | None = None, check_frames: bool = True):
    tl = load(timeline_path)
    base = Path(timeline_path).resolve().parent
    fcdir = base / "filmcraft"
    fcdir.mkdir(parents=True, exist_ok=True)
    project = str(Path(project).resolve()) if project else str(base / "reel.fcproj")
    O = tl["output"]
    W, H, fps, D = int(O["width"]), int(O["height"]), float(O["fps"]), float(tl["duration"])
    cli = cli or filmcraft_cli()
    if not cli and execute:
        raise SystemExit("filmcraft-cli not found. Install FilmCraft (see README > FilmCraft) or pass --cli PATH, "
                         "or use --script-only and run the steps through the FilmCraft MCP tools.")

    # looks as .cube files (used by Lumetri in native mode, handy in baked mode too)
    looks = sorted({s.get("look") or look_at(tl, s["start"]) for s in tl["shots"]})
    cubes = {}
    for name in looks:
        if name in LOOKS and name != "none":
            cubes[name] = str(write_cube(name, fcdir / "luts" / f"pulse_{name}.cube"))

    if mode == "baked" and render_first:
        print("Rendering styled shots for FilmCraft …")
        render(copy.deepcopy(tl), out_path=str(fcdir / "reel_full.mp4"), split_dir=str(fcdir / "shots"))
    plates = render_title_plates(tl, fcdir / "titles", W, H, fps) if mode == "native" else []

    log: list = []
    if not execute:
        _write_script(tl, mode, fcdir, cubes, plates, project)
        return
    mcp = FilmCraftMCP(cli, bridge=bridge, log=log)
    try:
        mcp.run("file.newProject", {"name": Path(project).stem})
        seq = mcp.run("file.newSequence", {"name": "Pulse Reel", "width": W, "height": H, "fps": fps,
                                            "video": 3, "audio": 2})
        # music
        if tl["music"].get("path"):
            mid = mcp.tool("media_import", {"paths": [tl["music"]["path"]]})["items"][0]
            mcp.run("timeline.place", {"item": mid, "track": "A1", "video": False, "seconds": 0,
                                       "sourceIn": ticks(float(tl["music"].get("start", 0))), "duration": ticks(D)})
        if mode == "baked":
            shot_files = [fcdir / "shots" / f"{s['id']}.mov" for s in tl["shots"]]
            missing = [str(p) for p in shot_files if not p.exists()]
            if missing:
                raise SystemExit(f"missing baked shots (run without --no-render): {missing[:3]}")
            ids = mcp.tool("media_import", {"paths": [str(p) for p in shot_files]})["items"]
            for s, item, f in zip(tl["shots"], ids, shot_files):
                dur = probe(f).duration
                mcp.run("timeline.place", {"item": item, "track": "V1", "audio": False, "seconds": s["start"],
                                           "duration": ticks(min(dur, s["dur"] + 0.5 / fps))})
        else:
            _native(mcp, tl, W, H, fps, D, cubes, plates)
        # beat markers + section markers
        for b in tl.get("beats", []):
            if 0 <= b < D:
                mcp.run("markers.add", {"target": "program", "time": ticks(b), "name": "beat"}, check=False)
        for sec in tl["grade"]["sections"]:
            mcp.run("markers.add", {"target": "program", "time": ticks(sec["start"]), "name": f"look: {sec['look']}",
                                    "color": "Rose"}, check=False)
        mcp.run("file.saveAs", {"path": project})
        print(f"FilmCraft project: {project}")
        if check_frames:
            outs = []
            for s in tl["shots"][:: max(1, len(tl["shots"]) // 6)]:
                t = s["start"] + s["dur"] * 0.6
                r = mcp.tool("render_frame", {"seconds": round(t, 3)}, check=False)
                if isinstance(r, list) and r and r[0].get("data"):
                    p = fcdir / "check" / f"frame_{t:06.2f}.png"
                    p.parent.mkdir(exist_ok=True)
                    p.write_bytes(base64.b64decode(r[0]["data"]))
                    outs.append(str(p))
            if outs:
                print(f"  check frames: {fcdir / 'check'}")
        if export:
            print(f"Exporting from FilmCraft -> {export} …")
            mcp.run("file.exportMedia", {"path": str(Path(export).resolve()), "format": "h264", "wait": True,
                                         "bitrateMode": "vbr1Pass", "bitrateKbps": 24000})
    finally:
        save_json(log, fcdir / "filmcraft_mcp_log.json")
        mcp.close()


def _native(mcp: FilmCraftMCP, tl, W, H, fps, D, cubes, plates):
    P = tl["protect"]
    sig = blur_curve(tl, int(round(D * fps)) + 1, fps)
    # looks go into the project's LUT library once (embedded in the .fcproj, so it stays portable)
    lut_refs = {}
    for name, path in cubes.items():
        r = mcp.run("lut.import", {"path": path, "name": f"pulse {name}"})
        lut_refs[name] = r["ref"]
    items = {}
    paths = sorted({s["clip"] for s in tl["shots"]})
    ids = mcp.tool("media_import", {"paths": paths})["items"]
    items = dict(zip(paths, ids))
    clips = []
    for i, s in enumerate(tl["shots"]):
        info = probe(s["clip"])
        cover = max(W / max(1, info.width), H / max(1, info.height)) * 100.0
        sp = float(s["speed"])
        src_len = min(s["dur"] * sp, max(0.05, info.duration - s["in"]))
        r = mcp.run("timeline.place", {"item": items[s["clip"]], "track": "V1", "audio": False, "seconds": s["start"],
                                       "sourceIn": ticks(s["in"]), "duration": ticks(src_len)})
        cid = r["clips"][0]
        if abs(sp - 1) > 1e-3:
            mcp.run("clip.speedDuration", {"clips": [cid], "speed": round(sp * 100, 3), "ripple": False,
                                           "interpolation": "frameBlending"}, check=False)
        t0, t1 = s["start"], s["start"] + s["dur"]
        z0, z1 = (s["zoom"] if isinstance(s["zoom"], list) else [s["zoom"], s["zoom"]])
        mcp.run("effects.setParam", {"clip": cid, "effect": "motion", "param": "scale", "value": cover * z0,
                                     "time": ticks(t0), "keyframe": True})
        if abs(z1 - z0) > 1e-3:
            mcp.run("effects.setParam", {"clip": cid, "effect": "motion", "param": "scale", "value": cover * z1,
                                         "time": ticks(t1 - 1 / fps), "keyframe": True})
        # grade: Lumetri with our look LUT + exposure correction
        look = s.get("look") or look_at(tl, s["start"])
        if tl["grade"]["enabled"] and look in lut_refs:
            mcp.run("effects.apply", {"clips": [cid], "effect": "lumetri"})
            mcp.run("lumetri.setInputLut", {"clip": cid, "lut": lut_refs[look]})
            if tl["grade"].get("correction", True):
                rd = FrameReader(info, s["in"], max(0.3, src_len), 90, 160, fps=4)
                smp = []
                while len(smp) < 8:
                    f = rd.read()
                    if f is None:
                        break
                    smp.append(f)
                rd.close()
                g = shot_correction(smp, LOOKS[look].get("target_luma", 0.45))
                stops = float(np.log2(max(1e-3, float(np.mean(g))))) + float(s.get("exposure", 0))
                if abs(stops) > 0.02:
                    mcp.run("effects.setParam", {"clip": cid, "effect": "lumetri", "param": "exposure",
                                                 "value": round(stops, 3)}, check=False)
        # colour pop: Leave Color, amount = how much of everything else is greyed
        if s["color"] != "full":
            mcp.run("effects.apply", {"clips": [cid], "effect": "leave_color"})
            mcp.run("effects.setParam", {"clip": cid, "effect": "leave_color", "param": "color",
                                         "value": hue_to_hex(P["hue"])})
            samples = []
            for k in range(int(round(s["dur"] * fps)) + 1):
                u = k / fps
                rest, _ = colour_curve(s["color"], u, s["dur"], float(P["keep"]))
                samples.append((t0 + u, round(100 * (1 - rest), 1)))
            for t, v in _keys(samples, 8.0):
                mcp.run("effects.setParam", {"clip": cid, "effect": "leave_color", "param": "amount", "value": v,
                                             "time": ticks(t), "keyframe": True})
        # focus pulse: Gaussian Blur keyframes (blurriness ~ 2.5 x sigma at 1080 wide)
        k0, k1 = int(round(t0 * fps)), int(round(t1 * fps))
        samples = [(k / fps, round(float(sig[min(k, len(sig) - 1)]) * 2.5 * W / 1080, 1)) for k in range(k0, k1 + 1)]
        if max(v for _, v in samples) > 0.5:
            mcp.run("effects.apply", {"clips": [cid], "effect": "gaussian_blur"})
            mcp.run("effects.setParam", {"clip": cid, "effect": "gaussian_blur", "param": "repeat_edge", "value": True},
                    check=False)
            for t, v in _keys(samples, 3.0):
                mcp.run("effects.setParam", {"clip": cid, "effect": "gaussian_blur", "param": "blurriness", "value": v,
                                             "time": ticks(t), "keyframe": True})
        clips.append(cid)
        # transition into this shot
        tr = s["transition"]
        spec = {"push_right": ("push", 4, "From West"), "push_left": ("push", 4, "From East"),
                "blend": ("cross_dissolve", 6, None), "flash": ("dip_to_white", 4, None),
                "bleach": ("dip_to_white", 18, None)}.get(tr)
        if i > 0 and spec:
            res = mcp.run("sequence.applyVideoTransition", {"clip": cid, "effect": spec[0], "frames": spec[1],
                                                            "edge": "in"}, check=False)
            if res and spec[2]:
                mcp.run("sequence.setTransition", {"transition": res["transition"],
                                                   "params": {"direction": spec[2]}}, check=False)
    # end events on the clips they touch: flicker (exposure) and fade to grey (saturation)
    for e in tl.get("events", []):
        if e["type"] not in ("flicker", "fade_grey"):
            continue
        for s, cid in zip(tl["shots"], clips):
            a, b = max(e["t"], s["start"]), min(e["t"] + e["dur"], s["start"] + s["dur"])
            if a >= b:
                continue
            mcp.run("effects.apply", {"clips": [cid], "effect": "lumetri"}, check=False)
            if e["type"] == "flicker":
                rng = np.random.default_rng(5)
                t = a
                while t < b:
                    mcp.run("effects.setParam", {"clip": cid, "effect": "lumetri", "param": "exposure",
                                                 "value": round(float(rng.choice([-1, 1]) * rng.uniform(0.2, 0.5)), 2),
                                                 "time": ticks(t), "keyframe": True}, check=False)
                    t += 2 / fps
            else:
                for t, v in ((a, 100.0), (b, 15.0)):
                    mcp.run("effects.setParam", {"clip": cid, "effect": "lumetri", "param": "saturation", "value": v,
                                                 "time": ticks(t), "keyframe": True}, check=False)
    # titles (V2): transparent PNG sequences, subject cut-out baked in
    for pl in plates:
        if not pl["frames"]:
            continue
        it = mcp.tool("media_import", {"paths": [pl["first"]], "image_sequence": True})["items"][0]
        mcp.run("timeline.place", {"item": it, "track": "V2", "audio": False, "seconds": pl["start"],
                                   "duration": ticks(pl["dur"])}, check=False)
    # grain (V3): adjustment layer + Noise
    if float(tl["texture"].get("grain", 0)) > 0:
        adj = mcp.run("file.newAdjustmentLayer", {"seconds": D}, check=False)
        aid = (adj or {}).get("item") if isinstance(adj, dict) else None
        if aid:
            r = mcp.run("timeline.place", {"item": aid, "track": "V3", "seconds": 0, "duration": ticks(D)}, check=False)
            if r:
                mcp.run("effects.apply", {"clips": r["clips"], "effect": "noise"}, check=False)
                mcp.run("effects.setParam", {"clip": r["clips"][0], "effect": "noise", "param": "amount",
                                             "value": round(float(tl["texture"]["grain"]) * 250, 1)}, check=False)


def _write_script(tl, mode, fcdir, cubes, plates, project):
    """No CLI available: write the plan for an agent to replay with the FilmCraft MCP tools."""
    plan = {
        "how_to": "Replay with the FilmCraft MCP tools: media_import the files, then command_run each step, "
                  "substituting the item / clip ids returned. See references/filmcraft.md.",
        "mode": mode, "project": project, "sequence": {"width": tl["output"]["width"], "height": tl["output"]["height"],
                                                        "fps": tl["output"]["fps"]},
        "music": tl["music"], "luts": cubes, "title_plates": plates,
        "shots": [{k: s[k] for k in ("id", "clip", "in", "dur", "speed", "zoom", "color", "transition", "start")}
                  for s in tl["shots"]],
        "beats": tl.get("beats", []), "events": tl.get("events", []),
    }
    p = fcdir / "filmcraft_plan.json"
    save_json(plan, p)
    print(f"Wrote {p} (replay through the FilmCraft MCP tools)")
