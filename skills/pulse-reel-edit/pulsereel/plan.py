"""Auto-plan a first-draft timeline in the reference style from analysis.json.

The draft follows the reference reel's structure (see references/style-reference.md):
  INTRO (start -> drop, moody):  colour pulses, blend, push-in close-up, HERO + title, b-roll breather
  DROP  (drop -> ~82%, airy):    white flash, b&w -> colour, bleach-out, 2-4 beat cuts on the beat
  OUTRO (last ~18%, overcast):   push, b&w beat, long final shot, exposure flicker, fade to grey
The agent then reviews the contact sheets and refines picks (see SKILL.md, step 4).
"""
from __future__ import annotations

import colorsys
from pathlib import Path

import numpy as np

from .media import save_json

# (beats, role, colour mode, transition-in, zoom, extra)
INTRO = [
    (2, "motion", "pulse", "blur", [1.0, 1.06], {}),
    (3, "motion", "bw_in", "blend", [1.04, 1.0], {}),
    (3, "close", "full", "blur", [1.0, 1.4], {"ramp_out": 0.0}),
    (5, "hero", "full", "push_right", [1.0, 1.05], {"title": True}),
    (4, "broll", "full", "blur", [1.0, 1.12], {}),
    (4, "calm", "full", "blur", [1.0, 1.06], {"dust": True}),
    (2, "calm", "full", "blur", [1.02, 1.08], {"dust": True}),
]
DROP = [
    (2, "calm", "bw_in", "flash", [1.05, 1.0], {"dust": True}),
    (3, "motion", "bw_in", "bleach", [1.0, 1.05], {}),
    (3, "motion", "pop_flood", "blur", [1.0, 1.06], {}),
    (3, "close", "full", "blur", [1.0, 1.08], {}),
    (1, "motion", "pop_out", "blur", [1.0, 1.0], {}),
    (2, "motion", "pop_flood", "blur", [1.0, 1.05], {}),
    (3, "calm", "full", "blur", [1.0, 1.06], {}),
    (3, "motion", "full", "blur", [1.0, 1.05], {}),
    (2, "motion", "full", "blur", [1.0, 1.04], {}),
    (4, "motion", "full", "blur", [1.0, 1.06], {}),
    (4, "calm", "full", "blur", [1.0, 1.06], {}),
    (4, "motion", "full", "blur", [1.0, 1.05], {}),
    (2, "motion", "full", "blur", [1.0, 1.04], {}),
]
OUTRO = [
    (2, "motion", "full", "push_left", [1.0, 1.04], {}),
    (2, "motion", "bw_hold", "blur", [1.0, 1.04], {}),
    (3, "motion", "full", "blur", [1.0, 1.05], {}),
    (6, "calm", "full", "blur", [1.0, 1.08], {"final": True}),
]
ROLE_W = {  # weights for (sharp, motion, colour, headroom, calmness)
    "motion": (0.30, 0.50, 0.20, 0.0, 0.0),
    "calm": (0.45, 0.0, 0.20, 0.05, 0.30),
    "close": (0.55, 0.0, 0.20, 0.0, 0.25),
    "hero": (0.40, 0.0, 0.15, 0.25, 0.20),
    "broll": (0.55, 0.35, 0.0, 0.0, 0.10),
}


def _fill(recipe, budget):
    out, used, i = [], 0, 0
    if budget <= 0:
        return out
    while used < budget:
        slot = recipe[i % len(recipe)]
        if i >= len(recipe):  # repeating: skip one-offs (title, final)
            slot = (slot[0], slot[1], slot[2] if slot[2] not in ("bw_in",) else "full",
                    "blur" if slot[3] in ("flash", "bleach", "push_right", "push_left") else slot[3], slot[4], {})
        b = min(slot[0], budget - used)
        out.append((b,) + slot[1:])
        used += b
        i += 1
    # avoid a trailing 1-beat slot: merge it into the previous one
    if len(out) > 1 and out[-1][0] < 2:
        prev = out[-2]
        out[-2] = (prev[0] + out[-1][0],) + prev[1:]
        out.pop()
    return out


def hue_to_hex(hue: float) -> str:
    r, g, b = colorsys.hsv_to_rgb((hue % 360) / 360.0, 0.84, 0.89)
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


class Picker:
    def __init__(self, clips):
        self.clips = clips
        allrows = [r for c in clips for r in c["samples"]]
        def rng(key, log=False):
            v = np.array([r[key] for r in allrows], float)
            if log:
                v = np.log1p(v)
            return np.percentile(v, 5), np.percentile(v, 95)
        self.n = {"sharp": rng("sharp", True), "motion": rng("motion"), "colour": rng("colour"),
                  "headroom": rng("headroom")}
        self.used = {c["id"]: [] for c in clips}
        self.count = {c["id"]: 0 for c in clips}
        self.last = None

    def _norm(self, key, v):
        lo, hi = self.n[key]
        if key == "sharp":
            v = np.log1p(v)
        return float(np.clip((v - lo) / (hi - lo + 1e-6), 0, 1))

    def pick(self, role, need):
        best = None
        if role == "broll":
            pool = [c for c in self.clips if c["kind"] == "broll"] or self.clips
        else:
            pool = [c for c in self.clips if c["kind"] != "broll"] or self.clips
        wS, wM, wC, wH, wQ = ROLE_W[role]
        for c in pool:
            rows = c["samples"]
            if not rows:
                continue
            dur = c["probe"]["duration"]
            dt = rows[1]["t"] - rows[0]["t"] if len(rows) > 1 else 0.25
            w = max(1, int(round(need / dt)))
            for i in range(0, max(1, len(rows) - w + 1)):
                t0 = rows[i]["t"]
                if t0 + need > dur - 0.05 and dur > need:
                    continue
                if any(not (t0 + need <= a or t0 >= b) for a, b in self.used[c["id"]]):
                    continue
                seg = rows[i:i + w]
                sh = self._norm("sharp", np.mean([r["sharp"] for r in seg]))
                mo = self._norm("motion", np.mean([r["motion"] for r in seg]))
                co = self._norm("colour", np.mean([r["colour"] for r in seg]))
                hr = self._norm("headroom", np.mean([r["headroom"] for r in seg]))
                score = wS * sh + wM * mo + wC * co + wH * hr + wQ * (1 - mo)
                score -= 0.12 * self.count[c["id"]]
                if self.last == c["id"]:
                    score -= 0.35
                if best is None or score > best[0]:
                    best = (score, c, t0)
        if best is None:  # everything used: allow reuse, take the longest clip's start
            c = max(self.clips, key=lambda c: c["probe"]["duration"])
            best = (0.0, c, 0.0)
        _, c, t0 = best
        self.used[c["id"]].append((t0, t0 + need))
        self.count[c["id"]] += 1
        self.last = c["id"]
        return c, t0


def auto_plan(analysis: dict, duration: float = 30.0, title: str | None = None,
              looks: list[str] | None = None, out_path: str = "renders/reel.mp4",
              music_start: float | None = None, slowmo_speed: float = 0.5, normal_speed: float = 1.0,
              width: int = 1080, height: int = 1920, fps: int = 30) -> dict:
    clips = analysis["clips"]
    music = analysis.get("music")
    if music:
        start = float(music["suggested_start"] if music_start is None else music_start)
        beats_abs = np.array(music["beats"], float)
        bp = float(np.median(np.diff(beats_abs)))
        rel = beats_abs[beats_abs >= start - 1e-6] - start
        drop_rel = float(music["drop"]) - start
        if not (0.15 * duration <= drop_rel <= 0.5 * duration):
            drop_rel = 0.31 * duration
    else:
        start, bp = 0.0, 0.42
        rel = np.arange(0, duration + 4, bp)
        drop_rel = 0.31 * duration
    if len(rel) == 0 or rel[0] > 0.05:
        rel = np.concatenate([[0.0], rel])
    rel = np.concatenate([rel, rel[-1] + bp * np.arange(1, 200)])  # extrapolate past the song end
    total = int(np.searchsorted(rel, duration - 0.2))
    pre = int(np.argmin(np.abs(rel - drop_rel)))
    outro = max(8, int(round(total * 0.19)))
    mid = max(4, total - pre - outro)
    slots = _fill(INTRO, pre) + _fill(DROP, mid) + _fill(OUTRO, total - pre - mid)
    drop_slot = len(_fill(INTRO, pre))
    outro_slot = drop_slot + len(_fill(DROP, mid))

    picker = Picker(clips)
    shots, events, titles, dust = [], [], [], []
    bi = 0
    for n, (beats, role, colour, trans, zoom, extra) in enumerate(slots):
        t0 = float(rel[bi])
        bi_end = bi + beats
        t1 = float(rel[bi_end]) if n < len(slots) - 1 else duration
        dur = round(t1 - t0, 4)
        bi = bi_end
        speed = normal_speed
        ramp_out = 0.18 if role == "motion" else 0.0
        # choose clip first (speed depends on clip fps)
        need_slow = dur * slowmo_speed * (1 + ramp_out)
        need_norm = dur * normal_speed * (1 + ramp_out)
        clip, src_in = picker.pick(role, need_slow)
        if clip["slowmo_capable"]:
            speed = slowmo_speed
        else:
            # re-pick window length for real-time playback if clip is long enough
            if clip["probe"]["duration"] >= src_in + need_norm:
                speed = normal_speed
            else:
                speed = max(0.5, (clip["probe"]["duration"] - src_in) / (dur * (1 + ramp_out)))
        shot = {
            "id": f"S{n + 1:02d}", "clip": clip["path"], "in": round(src_in, 3), "dur": dur,
            "speed": round(speed, 3), "ramp_out": ramp_out, "zoom": zoom, "color": colour,
            "transition": trans if n > 0 else "blur",
            "note": f"{role} | {clip['id']} {clip['name']}",
        }
        if extra.get("ramp_out") is not None:
            shot["ramp_out"] = extra["ramp_out"]
        shots.append(shot)
        if extra.get("title") and title:
            titles.append({"text": title, "start": round(t0 + 0.1, 3), "end": round(t1 - 0.04, 3),
                           "font": "GreatVibes-Regular.ttf", "size": 230, "color": hue_to_hex(analysis.get("protect_hue", 0)),
                           "color_in": "#FF7A1A", "pos": [0.5, 0.2], "behind_subject": True, "anim": "blur_rise"})
        if extra.get("dust"):
            dust.append([t0, t1])
        if trans == "flash":
            events.append({"t": round(t0, 3), "type": "flash", "dur": 0.14})
        if trans == "bleach":
            events.append({"t": round(t0 - 0.3, 3), "type": "bleach", "dur": 0.3})
        if extra.get("final"):
            events.append({"t": round(max(t0, duration - 1.5), 3), "type": "flicker", "dur": 0.7})
            events.append({"t": round(duration - 0.8, 3), "type": "fade_grey", "dur": 0.75})
    # merge dust ranges
    merged = []
    for a, b in sorted(dust):
        if merged and a <= merged[-1][1] + 0.05:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])

    looks = looks or ["moody", "airy", "overcast"]
    if len(looks) == 1:
        sections = [{"start": 0.0, "look": looks[0]}]
    else:
        t_drop = float(sum(s["dur"] for s in shots[:drop_slot]))
        t_out = float(sum(s["dur"] for s in shots[:outro_slot]))
        sections = [{"start": 0.0, "look": looks[0]}, {"start": round(t_drop, 3), "look": looks[1 % len(looks)]},
                    {"start": round(t_out, 3), "look": looks[2 % len(looks)]}]
    tl = {
        "version": 1,
        "output": {"width": width, "height": height, "fps": fps, "path": out_path, "crf": 16},
        "music": {"path": music["path"] if music else None, "start": round(start, 3), "fade_out": 0.6},
        "duration": round(duration, 3),
        "protect": {"hue": analysis.get("protect_hue", 0.0), "width": 18, "min_sat": 0.28, "keep": 0.5},
        "grade": {"enabled": True, "correction": True, "white_balance": False, "target_luma": 0.45, "sections": sections},
        "pulse": {"max_sigma": 14, "pre": 0.30, "post": 0.42, "intro": True, "breath_every_beats": 4,
                  "breath_strength": 0.45, "min_shot_for_breath": 1.6},
        "beats": [round(float(b), 4) for b in rel if b <= duration + 1e-6],
        "events": events,
        "texture": {"dust": merged, "dust_strength": 0.35, "grain": 0.014},
        "shots": shots,
        "titles": titles,
    }
    return tl
