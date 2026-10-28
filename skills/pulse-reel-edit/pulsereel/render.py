"""Render a timeline to a finished reel.

Per shot:   decode -> time-remap (slow-mo + ramps) -> zoom/pan -> light correction -> look LUT
            -> colour pop (protected colour) -> title (behind the subject)
Across cuts: push / blend transitions
Global:     focus-pulse blur -> flash / bleach / flicker / fade-to-grey -> dust -> grain -> encode
"""
from __future__ import annotations

import math
import time
from pathlib import Path

import cv2
import numpy as np

from . import fx
from .looks import LOOKS, apply_gain, apply_lut_bgr, colour_pop, full_lut, shot_correction
from .media import FrameReader, Writer, probe
from .timeline import TRANSITION_FRAMES, look_at


# ------------------------------------------------------------------ curves
def _bump(t, c, pre, post):
    if c - pre <= t <= c:
        return fx.ease_in_out((t - (c - pre)) / pre) if pre > 0 else 1.0
    if c < t <= c + post:
        return 1.0 - fx.ease_out((t - c) / post) if post > 0 else 0.0
    return 0.0


def blur_curve(tl: dict, n_frames: int, fps: float) -> np.ndarray:
    """Focus pulse: blur peaks at every soft cut and breathes on beats inside long shots."""
    P = tl["pulse"]
    smax, pre, post = float(P["max_sigma"]), float(P["pre"]), float(P["post"])
    shots = tl["shots"]
    beats = np.array(tl.get("beats") or [], float)
    bp = float(np.median(np.diff(beats))) if len(beats) > 2 else 0.42
    curve = np.zeros(n_frames, np.float32)
    ts = np.arange(n_frames) / fps
    events = []
    if P.get("intro", True):
        events.append((0.0, 1.0, 0.0, post * 1.4))
    for i, s in enumerate(shots):
        tr = s["transition"]
        if i > 0 and tr != "cut" and s.get("pulse", True):
            strength = 0.75 if tr in ("push_left", "push_right") else 1.0
            events.append((s["start"], strength * s.get("blur_scale", 1.0), pre, post))
        every = int(P.get("breath_every_beats") or 0)
        if every and s["dur"] >= float(P["min_shot_for_breath"]) and s.get("pulse", True) and len(beats):
            inner = beats[(beats > s["start"] + 2 * bp - 1e-3) & (beats < s["start"] + s["dur"] - 2 * bp + 1e-3)]
            for k, b in enumerate(inner):
                if k % every == 0:
                    events.append((float(b), float(P["breath_strength"]), pre * 0.7, post * 0.7))
    for c, amp, a, b in events:
        lo, hi = int(max(0, (c - a) * fps)), int(min(n_frames, (c + b) * fps + 2))
        for k in range(lo, hi):
            curve[k] = max(curve[k], amp * _bump(ts[k], c, a, b))
    return curve * smax


def colour_curve(mode, u: float, dur: float, keep: float):
    """(rest, keep) saturation multipliers at time u (s) into a shot."""
    if isinstance(mode, list):  # custom keyframes [[sec, rest, keep], ...]
        ks = sorted(mode)
        if u <= ks[0][0]:
            return ks[0][1], ks[0][2]
        for (t0, r0, k0), (t1, r1, k1) in zip(ks, ks[1:]):
            if t0 <= u <= t1:
                p = fx.ease_in_out((u - t0) / max(1e-6, t1 - t0))
                return r0 + (r1 - r0) * p, k0 + (k1 - k0) * p
        return ks[-1][1], ks[-1][2]
    e = fx.ease_in_out
    if mode == "full":
        return 1.0, 1.0
    if mode == "pop_hold":
        return 0.0, keep
    if mode == "bw_hold":
        return 0.0, 0.0
    if mode == "pop_in":
        p = e((u - 0.08) / 0.4)
        return p, keep + (1 - keep) * p
    if mode == "bw_in":
        k1 = e(u / 0.18) * keep
        p = e((u - 0.15) / 0.42)
        return p, k1 + (1 - k1) * p
    if mode == "pop_out":
        p = e((u - (dur - 0.45)) / 0.4)
        return 1 - p, 1 - (1 - keep) * p
    if mode == "pop_flood":
        p = e((u - dur * 0.62) / 0.35)
        return p, keep + (1 - keep) * p
    if mode == "pulse":  # selective -> full -> selective (the opening shots)
        up = e(u / max(0.2, dur * 0.4))
        down = e((u - dur * 0.62) / max(0.15, dur * 0.33))
        p = up * (1 - down)
        return p, keep + (1 - keep) * p
    return 1.0, 1.0


# ------------------------------------------------------------------ per-shot stream
class ShotRenderer:
    def __init__(self, tl, idx, W, H, fps, k_from, k_to, luts, masker, preview):
        self.tl, self.s, self.idx = tl, tl["shots"][idx], idx
        self.W, self.H, self.fps = W, H, fps
        self.k_from, self.k_to = k_from, k_to
        self.luts, self.masker, self.preview = luts, masker, preview
        s = self.s
        self.info = probe(s["clip"])
        z0, z1 = s["zoom"] if isinstance(s["zoom"], (list, tuple)) else (s["zoom"], s["zoom"])
        self.z0, self.z1 = float(z0), float(z1)
        self.zc = min(1.6, max(1.0, self.z0, self.z1))
        self.W0, self.H0 = int(math.ceil(W * self.zc / 2) * 2), int(math.ceil(H * self.zc / 2) * 2)
        self._time_map()
        self.titles = [t for t in tl["titles"] if t["start"] < (k_to / fps) and t["end"] > (k_from / fps)]

    def _speed_at(self, u):
        s = self.s
        sp, d = float(s["speed"]), float(s["dur"])
        mult = float(s.get("ramp_mult", 2.0))
        ri, ro = float(s.get("ramp_in", 0)) * d, float(s.get("ramp_out", 0)) * d
        if ri > 0 and u < ri:
            return sp * (mult + (1 - mult) * fx.ease_out(u / ri))
        if ro > 0 and u > d - ro:
            return sp * (1 + (mult - 1) * fx.ease_in((u - (d - ro)) / ro))
        return sp

    def _time_map(self):
        s, fps = self.s, self.fps
        ks = np.arange(self.k_from, self.k_to)
        us = ks / fps - s["start"]
        src = np.empty(len(ks))
        # integrate speed from shot start (u=0 -> s.in); handles before start run backwards at base speed
        acc = float(s["in"])
        k0 = int(round(s["start"] * fps))
        pos = {}
        for k in range(k0, self.k_to):
            pos[k] = acc
            acc += self._speed_at((k - k0) / fps) / fps
        for k in range(self.k_from, k0):
            pos[k] = float(s["in"]) - (k0 - k) * float(s["speed"]) / fps
        for j, k in enumerate(ks):
            src[j] = pos[k]
        dur_src = max(0.0, self.info.duration - 0.05)
        self.src = np.clip(src, 0.0, dur_src)
        self.us = us

    def frames(self):
        s, info = self.s, self.info
        t0 = float(self.src.min())
        span = float(self.src.max() - t0) + 3.0 / max(info.fps, 1)
        fxy = s.get("focus", [0.5, 0.5])
        rd = FrameReader(info, t0, span, self.W0, self.H0, focus=fxy)
        nf = rd.fps
        # light correction gains from a few frames in the used range
        gains = None
        if self.tl["grade"]["enabled"] and self.tl["grade"].get("correction", True):
            pr = FrameReader(info, t0, max(0.2, span), 90, 160, fps=4)
            smp = []
            while True:
                f = pr.read()
                if f is None or len(smp) > 8:
                    break
                smp.append(f)
            pr.close()
            look_name = s.get("look") or look_at(self.tl, s["start"])
            tgt = LOOKS.get(look_name, {}).get("target_luma") if isinstance(look_name, str) else None
            gains = shot_correction(smp, float(tgt or self.tl["grade"].get("target_luma", 0.45)),
                                    wb_strength=0.25 if self.tl["grade"].get("white_balance", False) else 0.0)
            if s.get("exposure"):
                gains = gains * (2 ** float(s["exposure"]))
        elif s.get("exposure"):
            gains = np.full(3, 2 ** float(s["exposure"]), np.float32)
        lut = None
        if self.tl["grade"]["enabled"]:
            lut = self.luts(s.get("look") or look_at(self.tl, s["start"]))
        buf = {}
        cur = -1
        last = None
        keep = float(self.tl["protect"]["keep"])
        P = self.tl["protect"]
        if self.masker is not None:
            self.masker.reset()
        for j, k in enumerate(range(self.k_from, self.k_to)):
            jf = (self.src[j] - t0) * nf
            ja, jb = int(math.floor(jf)), int(math.floor(jf)) + 1
            frac = jf - ja
            while cur < jb:
                f = rd.read()
                if f is None:
                    break
                cur += 1
                buf[cur] = f
                last = f
                for old in [x for x in buf if x < ja]:
                    del buf[old]
            fa = buf.get(ja, last)
            fb = buf.get(jb, fa)
            if fa is None:
                fa = fb = np.zeros((self.H0, self.W0, 3), np.uint8)
            frame = fa if (frac < 0.2 or fb is None) else (fb if frac > 0.8 else cv2.addWeighted(fa, 1 - frac, fb, frac, 0))
            frame = self._warp(frame, self.us[j])
            if gains is not None:
                frame = apply_gain(frame, gains)  # gains are in BGR order
            if lut is not None:
                frame = apply_lut_bgr(frame, lut)
            rest, kp = colour_curve(s["color"], self.us[j], s["dur"], keep)
            frame = colour_pop(frame, rest, kp, float(P["hue"]), float(P["width"]), float(P["min_sat"]))
            t_abs = k / self.fps
            for ti in self.titles:
                if ti["start"] <= t_abs < ti["end"]:
                    m = self.masker(frame) if (self.masker is not None and ti.get("behind_subject", True)) else None
                    frame = fx.draw_title(frame, ti, t_abs - ti["start"], ti["end"] - ti["start"], m)
            yield k, frame
        rd.close()

    def _warp(self, frame, u):
        d = max(1e-3, float(self.s["dur"]))
        p = fx.ease_in_out(min(max(u / d, 0), 1))
        z = self.z0 + (self.z1 - self.z0) * p
        cx, cy = self.s.get("center", [0.5, 0.45])
        pan = self.s.get("pan")
        if pan:
            (px0, py0), (px1, py1) = pan
            cx, cy = cx + px0 + (px1 - px0) * p, cy + py0 + (py1 - py0) * p
        vw, vh = self.W0 / z, self.H0 / z
        x0 = min(max(cx * self.W0 - vw / 2, 0), self.W0 - vw)
        y0 = min(max(cy * self.H0 - vh / 2, 0), self.H0 - vh)
        sc = self.W / vw
        M = np.array([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]], np.float32)
        if abs(sc - 1) < 1e-3 and abs(x0) < 1e-3 and abs(y0) < 1e-3 and frame.shape[1] == self.W:
            return frame
        return cv2.warpAffine(frame, M, (self.W, self.H), flags=cv2.INTER_CUBIC if not self.preview else cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT)


# ------------------------------------------------------------------ main
def render(tl: dict, out_path: str | None = None, preview: bool = False, grade: str | None = None,
           split_dir: str | None = None, prores: bool = False, no_titles_mask: bool = False,
           progress: bool = True) -> str:
    t_start = time.time()
    O = tl["output"]
    W, H, fps = int(O["width"]), int(O["height"]), float(O["fps"])
    if preview:
        W, H = W // 2 // 2 * 2, H // 2 // 2 * 2
    if grade == "none":
        tl["grade"]["enabled"] = False
    out_path = out_path or O["path"]
    if preview and out_path == O["path"]:
        p = Path(out_path)
        out_path = str(p.with_name(p.stem + "_preview" + p.suffix))
    n = int(round(tl["duration"] * fps))
    shots = tl["shots"]

    # frame ranges per shot incl. transition handles
    kstart = [int(round(s["start"] * fps)) for s in shots] + [n]
    hpre = [0] * len(shots)
    hpost = [0] * len(shots)
    trans = {}
    for i in range(1, len(shots)):
        L = TRANSITION_FRAMES.get(shots[i]["transition"], 0)
        if L:
            a = L // 2
            b = L - a
            trans[i] = (kstart[i] - a, kstart[i] + b, shots[i]["transition"])
            hpost[i - 1] = b
            hpre[i] = a
    ranges = [(max(0, kstart[i] - hpre[i]), min(n, kstart[i + 1] + hpost[i])) for i in range(len(shots))]

    lut_cache = {}

    def luts(name):
        if name not in lut_cache:
            if progress:
                print(f"  preparing look '{name}' (cached after first use)…")
            lut_cache[name] = full_lut(name)
        return lut_cache[name]

    masker = None
    if tl["titles"] and not no_titles_mask:
        masker = fx.SubjectMasker(work_w=256 if preview else 448)
        if not masker.ok:
            masker = None

    sigma = blur_curve(tl, n, fps) * (W / 1080.0)
    ev = tl.get("events", [])
    dust = fx.Dust(W, H) if tl["texture"].get("dust") else None
    grain = fx.Grain(W, H) if float(tl["texture"].get("grain", 0)) > 0 else None
    rng = np.random.default_rng(11)

    music = tl["music"]
    wr = Writer(out_path, W, H, fps, crf=23 if preview else int(O.get("crf", 16)),
                preset="veryfast" if preview else O.get("preset", "medium"),
                audio=music.get("path"), audio_start=float(music.get("start", 0)),
                duration=tl["duration"], audio_fade=float(music.get("fade_out", 0.6)), prores=prores)
    split_writers = {}

    active = {}
    gens = {}
    next_shot = 0
    flicker_seq = {}
    for k in range(n):
        t = k / fps
        while next_shot < len(shots) and ranges[next_shot][0] <= k:
            sr = ShotRenderer(tl, next_shot, W, H, fps, ranges[next_shot][0], ranges[next_shot][1], luts, masker, preview)
            gens[next_shot] = sr.frames()
            next_shot += 1
        frames_now = {}
        for i in list(gens):
            if ranges[i][0] <= k < ranges[i][1]:
                try:
                    kk, fr = next(gens[i])
                    frames_now[i] = fr
                except StopIteration:
                    pass
            if k >= ranges[i][1] - 1:
                gens.pop(i, None)
        # which shot owns this frame
        cur = max(i for i in range(len(shots)) if kstart[i] <= k) if k >= kstart[0] else 0
        frame = None
        for i, (a, b, kind) in trans.items():
            if a <= k < b and (i - 1) in frames_now and i in frames_now:
                p = (k - a + 0.5) / (b - a)
                A, B = frames_now[i - 1], frames_now[i]
                if kind == "blend":
                    frame = fx.blend(A, B, p)
                elif kind == "push_left":
                    frame = fx.push(A, B, p, direction=-1)
                else:
                    frame = fx.push(A, B, p, direction=1)
        if frame is None:
            frame = frames_now.get(cur)
            if frame is None and frames_now:
                frame = frames_now[sorted(frames_now)[-1]]
            if frame is None:
                frame = np.zeros((H, W, 3), np.uint8)

        # -------- global stage
        frame = fx.lens_blur(frame, float(sigma[k]))
        white = desat = stops = grey = 0.0
        for e in ev:
            et, ed, kind = float(e["t"]), float(e.get("dur", 0.2)), e["type"]
            if kind == "flash":
                if et - 1.0 / fps <= t <= et + ed:
                    pk = 1.0 if t <= et + 0.5 / fps else 1 - fx.ease_out((t - et) / ed)
                    white = max(white, pk * float(e.get("strength", 1.0)))
                    desat = max(desat, pk)
            elif kind == "bleach":
                if et <= t <= et + ed:
                    pk = fx.ease_in((t - et) / ed)
                elif et + ed < t <= et + ed + 0.3:
                    pk = 1 - fx.ease_out((t - et - ed) / 0.3)
                else:
                    pk = 0
                white = max(white, 0.88 * pk * float(e.get("strength", 1.0)))
                desat = max(desat, 0.9 * pk)
            elif kind == "flicker":
                if et <= t <= et + ed:
                    key = (et, k // 2)
                    if key not in flicker_seq:
                        flicker_seq[key] = float(rng.choice([-1, 1]) * rng.uniform(0.15, 0.4))
                    stops += flicker_seq[key] * float(e.get("strength", 1.0))
            elif kind == "fade_grey":
                if t >= et:
                    pk = fx.ease_in_out((t - et) / ed)
                    grey = max(grey, pk * float(e.get("strength", 0.85)))
                    stops -= 0.25 * pk
            elif kind == "dip_black":
                if et <= t <= et + ed:
                    stops -= 6 * math.sin(math.pi * (t - et) / ed)
        if stops:
            frame = fx.exposure_gain(frame, stops)
        if white or desat:
            frame = fx.exposure_white(frame, white, desat)
        if grey:
            frame = fx.global_desat(frame, grey)
        if dust is not None:
            for a, b in tl["texture"]["dust"]:
                if a <= t <= b:
                    edge = min(1.0, (t - a) / 0.3, (b - t) / 0.3)
                    frame = dust.render(frame, k, float(tl["texture"].get("dust_strength", 0.35)) * edge)
                    break
        if grain is not None:
            frame = grain.render(frame, k, float(tl["texture"]["grain"]))
        wr.write(frame)
        if split_dir:
            sid = shots[cur]["id"]
            if sid not in split_writers:
                for w_ in split_writers.values():
                    w_.close()
                split_writers.clear()
                split_writers[sid] = Writer(Path(split_dir) / f"{sid}.mov", W, H, fps, prores=prores, crf=12)
            split_writers[sid].write(frame)
        if progress and (k % int(fps) == 0 or k == n - 1):
            el = time.time() - t_start
            print(f"\r  rendering {k + 1}/{n} frames  ({el:.0f}s)", end="", flush=True)
    wr.close()
    for w_ in split_writers.values():
        w_.close()
    if progress:
        print(f"\n  wrote {out_path}  in {time.time() - t_start:.0f}s")
    return out_path
