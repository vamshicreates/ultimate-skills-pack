"""Timeline (edit decision list) model, defaults and validation.

A timeline is plain JSON so an agent can read and edit it. See references/timeline-schema.md.
"""
from __future__ import annotations

import copy
from pathlib import Path

from .media import load_json, save_json

DEFAULTS = {
    "version": 1,
    "output": {"width": 1080, "height": 1920, "fps": 30, "path": "renders/reel.mp4", "crf": 16, "preset": "medium"},
    "music": {"path": None, "start": 0.0, "fade_out": 0.6},
    "protect": {"hue": 0.0, "width": 18.0, "min_sat": 0.28, "keep": 0.5},
    "grade": {"enabled": True, "correction": True, "white_balance": False, "target_luma": 0.45,
              "sections": [{"start": 0.0, "look": "natural"}]},
    "pulse": {"max_sigma": 14.0, "pre": 0.30, "post": 0.42, "intro": True,
              "breath_every_beats": 4, "breath_strength": 0.45, "min_shot_for_breath": 1.6},
    "beats": [],
    "events": [],
    "texture": {"dust": [], "dust_strength": 0.35, "grain": 0.014},
    "shots": [],
    "titles": [],
}

SHOT_DEFAULTS = {"in": 0.0, "dur": 1.2, "speed": 1.0, "ramp_in": 0.0, "ramp_out": 0.0, "ramp_mult": 2.0,
                 "zoom": [1.0, 1.05], "focus": [0.5, 0.5], "center": [0.5, 0.45], "color": "full",
                 "transition": "blur", "exposure": 0.0, "pulse": True}

TRANSITIONS = {"blur", "cut", "push_left", "push_right", "blend", "flash", "bleach"}
COLOR_MODES = {"full", "pop_in", "bw_in", "pop_out", "pop_hold", "pop_flood", "pulse", "bw_hold"}
TRANSITION_FRAMES = {"push_left": 4, "push_right": 4, "blend": 6}


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load(path: str | Path) -> dict:
    tl = load_json(path)
    return normalize(tl, base_dir=Path(path).resolve().parent)


def normalize(tl: dict, base_dir: Path | None = None) -> dict:
    tl = _merge(DEFAULTS, tl)
    base_dir = base_dir or Path.cwd()

    def absol(p):
        if not p:
            return p
        pp = Path(p)
        return str(pp if pp.is_absolute() else (base_dir / pp).resolve())

    if tl["music"].get("path"):
        tl["music"]["path"] = absol(tl["music"]["path"])
    tl["output"]["path"] = absol(tl["output"]["path"])
    t = 0.0
    shots = []
    errors = []
    for i, s in enumerate(tl["shots"]):
        s = _merge(SHOT_DEFAULTS, s)
        s.setdefault("id", f"S{i + 1:02d}")
        s["clip"] = absol(s["clip"])
        if not Path(s["clip"]).exists():
            errors.append(f"{s['id']}: clip not found: {s['clip']}")
        if s["transition"] not in TRANSITIONS:
            errors.append(f"{s['id']}: transition '{s['transition']}' not in {sorted(TRANSITIONS)}")
        if isinstance(s["color"], str) and s["color"] not in COLOR_MODES:
            errors.append(f"{s['id']}: color '{s['color']}' not in {sorted(COLOR_MODES)}")
        if s["dur"] <= 0:
            errors.append(f"{s['id']}: dur must be > 0")
        s["start"] = round(t, 4)
        t += float(s["dur"])
        shots.append(s)
    tl["shots"] = shots
    tl["duration"] = round(float(tl.get("duration") or t), 4)
    if errors:
        raise ValueError("Timeline problems:\n  - " + "\n  - ".join(errors))
    return tl


def save(tl: dict, path: str | Path):
    clean = copy.deepcopy(tl)
    for s in clean.get("shots", []):
        s.pop("start", None)
    save_json(clean, path)


def look_at(tl: dict, t: float) -> str:
    look = "natural"
    for sec in sorted(tl["grade"]["sections"], key=lambda s: s["start"]):
        if t + 1e-6 >= sec["start"]:
            look = sec["look"]
    return look
