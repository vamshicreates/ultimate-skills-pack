"""Frame effects: focus pulse blur, flash/bleach exposure, push slide, frame blend,
dust specks, film grain, and the depth-layered title (text behind the subject)."""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------ easing
def ease_in_out(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = min(max(t, 0.0), 1.0)
    return t ** 3


# ------------------------------------------------------------------ blur
def lens_blur(frame: np.ndarray, sigma: float) -> np.ndarray:
    """Defocus-style blur. Large radii are done at reduced resolution (fast, and the
    softness hides the resample). A touch of highlight bloom keeps it 'lens' rather than 'smear'."""
    if sigma < 0.35:
        return frame
    h, w = frame.shape[:2]
    if sigma > 6:
        k = 4 if sigma > 14 else 2
        small = cv2.resize(frame, (w // k, h // k), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), sigma / k)
        out = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        out = cv2.GaussianBlur(frame, (0, 0), sigma)
    if sigma > 3:
        # bloom: brightest parts spread a little more
        f = out.astype(np.float32)
        hi = np.clip(f - 200, 0, None)
        hi = cv2.GaussianBlur(hi, (0, 0), sigma * 1.5)
        out = np.clip(f + hi * min(0.6, sigma / 30), 0, 255).astype(np.uint8)
    return out


def motion_blur_h(frame: np.ndarray, length: int) -> np.ndarray:
    if length < 3:
        return frame
    k = np.zeros((1, length), np.float32)
    k[0, :] = 1.0 / length
    return cv2.filter2D(frame, -1, k)


# ------------------------------------------------------------------ exposure
def exposure_white(frame: np.ndarray, amount: float, desat: float = 0.0) -> np.ndarray:
    """amount 0..1 pushes toward white (flash / bleach). desat 0..1 removes colour."""
    if amount <= 0.001 and desat <= 0.001:
        return frame
    f = frame.astype(np.float32)
    if desat > 0:
        y = (f @ np.array([0.0722, 0.7152, 0.2126], np.float32))[..., None]
        f = y + (f - y) * (1 - desat)
    if amount > 0:
        # screen-like lift: highlights blow first, like overexposure
        f = 255 - (255 - f) * (1 - amount) ** 1.5
    return np.clip(f, 0, 255).astype(np.uint8)


def exposure_gain(frame: np.ndarray, stops: float) -> np.ndarray:
    if abs(stops) < 0.005:
        return frame
    g = 2 ** stops
    lut = np.clip(np.arange(256, dtype=np.float32) * g, 0, 255).astype(np.uint8)
    return lut[frame]


def global_desat(frame: np.ndarray, amount: float, tint=(0.94, 0.97, 1.0)) -> np.ndarray:
    """Fade to grey (amount 1 = fully grey). `tint` (B, G, R) warms the grey slightly."""
    if amount <= 0.001:
        return frame
    f = frame.astype(np.float32)
    y = (f @ np.array([0.0722, 0.7152, 0.2126], np.float32))[..., None]
    grey = y * np.array(tint, np.float32)
    return np.clip(f + (grey - f) * amount, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ transitions
def push(a: np.ndarray, b: np.ndarray, p: float, direction: int = 1, blur: bool = True) -> np.ndarray:
    """Slide transition. p 0..1. direction 1 = new shot enters from the left, pushing right."""
    h, w = a.shape[:2]
    e = ease_in_out(p)
    off = int(round(e * w)) * direction
    out = np.empty_like(a)
    if direction > 0:
        out[:, off:] = a[:, : w - off] if off < w else out[:, off:]
        out[:, :off] = b[:, w - off:] if off > 0 else out[:, :off]
    else:
        off = -off
        out[:, : w - off] = a[:, off:] if off < w else out[:, : w - off]
        out[:, w - off:] = b[:, : off] if off > 0 else out[:, w - off:]
    if blur:
        speed = math.sin(math.pi * min(max(p, 0), 1))
        out = motion_blur_h(out, int(speed * w * 0.12) | 1)
    return out


def blend(a: np.ndarray, b: np.ndarray, p: float) -> np.ndarray:
    return cv2.addWeighted(a, 1 - p, b, p, 0)


# ------------------------------------------------------------------ texture
class Dust:
    """Sparse floating specks (light drizzle / dust in the air), screen-blended."""

    def __init__(self, w, h, n=70, seed=7):
        rng = np.random.default_rng(seed)
        self.w, self.h = w, h
        self.p = rng.random((n, 2)) * [w, h]
        self.v = (rng.random((n, 2)) - [0.5, -0.2]) * [w * 0.002, h * 0.004]
        self.r = rng.choice([1, 1, 1, 2, 2, 3], n) * max(1, w // 1080)
        self.a = rng.random(n) * 0.5 + 0.25
        self.ph = rng.random(n) * 6.28

    def render(self, frame: np.ndarray, k: int, strength: float = 0.5) -> np.ndarray:
        if strength <= 0:
            return frame
        layer = np.zeros(frame.shape[:2], np.float32)
        pos = (self.p + self.v * k) % [self.w, self.h]
        tw = 0.6 + 0.4 * np.sin(self.ph + k * 0.25)
        for (x, y), r, a, t in zip(pos.astype(int), self.r, self.a, tw):
            cv2.circle(layer, (int(x), int(y)), int(r), float(a * t), -1, cv2.LINE_AA)
        layer = cv2.GaussianBlur(layer, (0, 0), 0.8)[..., None] * (255 * strength)
        f = frame.astype(np.float32)
        return np.clip(255 - (255 - f) * (255 - layer) / 255, 0, 255).astype(np.uint8)


class Grain:
    def __init__(self, w, h, seed=3, n=8):
        rng = np.random.default_rng(seed)
        self.tiles = []
        for _ in range(n):
            g = rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32)
            g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)
            self.tiles.append(g)

    def render(self, frame: np.ndarray, k: int, strength: float = 0.03) -> np.ndarray:
        if strength <= 0:
            return frame
        g = self.tiles[k % len(self.tiles)][..., None] * (255 * strength)
        f = frame.astype(np.float32)
        mid = 1 - np.abs(f / 127.5 - 1) ** 2  # grain mostly in mid-tones
        return np.clip(f + g * mid, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ title
def hex_to_bgr(hx: str):
    hx = hx.lstrip("#")
    r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
    return (b, g, r)


def find_font(name: str | None) -> str:
    cands = []
    if name:
        cands += [Path(name), ROOT / "assets" / "fonts" / name]
    cands += [ROOT / "assets" / "fonts" / "GreatVibes-Regular.ttf"]
    for c in cands:
        if c.exists():
            return str(c)
    raise FileNotFoundError("Title font not found. Put a .ttf in assets/fonts/ or pass an absolute path.")


@lru_cache(maxsize=16)
def text_layer(text: str, font_path: str, size: int, color: str, stroke: int = 0,
               shadow: float = 0.35, letter_spacing: float = 0.0):
    """Render the title once as premultiplied BGRA float layers (colour, alpha)."""
    font = ImageFont.truetype(font_path, size)
    pad = size
    tmp = Image.new("L", (10, 10))
    bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font, stroke_width=stroke)
    W, H = bbox[2] - bbox[0] + 2 * pad, bbox[3] - bbox[1] + 2 * pad
    alpha = Image.new("L", (W, H), 0)
    ImageDraw.Draw(alpha).text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=255, stroke_width=stroke)
    a = np.asarray(alpha, np.float32) / 255.0
    sh = np.asarray(alpha.filter(ImageFilter.GaussianBlur(size * 0.08)), np.float32) / 255.0 * shadow
    sh = np.roll(sh, (int(size * 0.015), int(size * 0.01)), (0, 1))
    return a, sh


def title_layer(shape, spec: dict, t_rel: float, dur: float, subject_mask: np.ndarray | None,
                scale: float = 1.0):
    """Compute one title as (region, colour BGR, text alpha, shadow alpha) for frame `shape`.
    Animation 'blur_rise' (reference): blurs in, rises ~4% of height, warms from orange to final colour."""
    h, w = shape[:2]
    size = int(spec.get("size", 200) * scale * w / 1080)
    font = find_font(spec.get("font"))
    a, sh = text_layer(spec["text"], font, size, spec.get("color", "#E3262E"),
                       int(spec.get("stroke", 0)), float(spec.get("shadow", 0.22)))
    anim = spec.get("anim", "blur_rise")
    t_in, t_out = float(spec.get("in", 0.6)), float(spec.get("out", 0.25))
    p_in = ease_out(t_rel / t_in) if t_in > 0 else 1.0
    p_out = 1.0 - ease_in((t_rel - (dur - t_out)) / t_out) if t_out > 0 and t_rel > dur - t_out else 1.0
    opacity = min(p_in, p_out) * float(spec.get("opacity", 1.0))
    if opacity <= 0.003:
        return None
    blur, dy = 0.0, 0.0
    col = np.array(hex_to_bgr(spec.get("color", "#E3262E")), np.float32)
    if anim == "blur_rise":
        blur = (1 - p_in) * size * 0.12
        dy = (1 - p_in) * h * 0.04 - t_rel * h * float(spec.get("drift", 0.004))
        warm = np.array(hex_to_bgr(spec.get("color_in", "#FF7A1A")), np.float32)
        col = warm + (col - warm) * p_in
    al, shd = a, sh
    if blur > 0.4:
        al = cv2.GaussianBlur(a, (0, 0), blur)
        shd = cv2.GaussianBlur(sh, (0, 0), blur)
    th, tw = al.shape
    cx, cy = spec.get("pos", [0.5, 0.2])
    x0 = int(cx * w - tw / 2)
    y0 = int(cy * h - th / 2 + dy)
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(w, x0 + tw), min(h, y0 + th)
    if fx1 <= fx0 or fy1 <= fy0:
        return None
    ax0, ay0 = fx0 - x0, fy0 - y0
    A = al[ay0:ay0 + fy1 - fy0, ax0:ax0 + fx1 - fx0] * opacity
    S = shd[ay0:ay0 + fy1 - fy0, ax0:ax0 + fx1 - fx0] * opacity
    if subject_mask is not None and spec.get("behind_subject", True):
        hole = 1.0 - subject_mask[fy0:fy1, fx0:fx1]
        A = A * hole
        S = S * hole
    return (fy0, fy1, fx0, fx1), col, A, S


def draw_title(frame: np.ndarray, spec: dict, t_rel: float, dur: float, subject_mask: np.ndarray | None,
               scale: float = 1.0) -> np.ndarray:
    lay = title_layer(frame.shape, spec, t_rel, dur, subject_mask, scale)
    if lay is None:
        return frame
    (fy0, fy1, fx0, fx1), col, A, S = lay
    out = frame.copy()
    roi = out[fy0:fy1, fx0:fx1].astype(np.float32)
    roi = roi * (1 - S[..., None])  # soft drop shadow
    roi = roi * (1 - A[..., None]) + col * A[..., None]
    out[fy0:fy1, fx0:fx1] = np.clip(roi, 0, 255).astype(np.uint8)
    return out


def title_rgba(shape, spec: dict, t_rel: float, dur: float, subject_mask: np.ndarray | None) -> np.ndarray:
    """Transparent BGRA plate of the title (subject occlusion baked in) for editors (FilmCraft/Resolve)."""
    h, w = shape[:2]
    out = np.zeros((h, w, 4), np.uint8)
    lay = title_layer(shape, spec, t_rel, dur, subject_mask)
    if lay is None:
        return out
    (fy0, fy1, fx0, fx1), col, A, S = lay
    a_tot = 1 - (1 - S) * (1 - A)
    c = (col[None, None, :] * A[..., None]) / np.maximum(a_tot[..., None], 1e-4)
    out[fy0:fy1, fx0:fx1, :3] = np.clip(c, 0, 255).astype(np.uint8)
    out[fy0:fy1, fx0:fx1, 3] = np.clip(a_tot * 255, 0, 255).astype(np.uint8)
    return out


# ------------------------------------------------------------------ subject mask
class SubjectMasker:
    """Person/subject cut-out for depth-layered titles. Uses rembg (u2net_human_seg) when
    installed; otherwise returns None and titles are drawn in front."""

    def __init__(self, model: str = "u2net_human_seg", work_w: int = 384):
        self.ok = False
        self.prev = None
        self.work_w = work_w
        try:
            from rembg import new_session, remove  # type: ignore

            self._remove = remove
            self.session = new_session(model)
            self.ok = True
        except Exception as exc:  # pragma: no cover
            print(f"[pulse] subject mask unavailable ({exc.__class__.__name__}): titles will sit in front. "
                  f"Install with: python -m pip install \"rembg[cpu]\"")

    def reset(self):
        self.prev = None

    def __call__(self, frame: np.ndarray) -> np.ndarray | None:
        if not self.ok:
            return None
        h, w = frame.shape[:2]
        ww = self.work_w
        hh = int(round(h * ww / w))
        small = cv2.resize(frame, (ww, hh), interpolation=cv2.INTER_AREA)
        m = self._remove(small, session=self.session, only_mask=True)
        m = np.asarray(m, np.float32) / 255.0
        if m.ndim == 3:
            m = m[..., 0]
        if self.prev is not None:
            m = 0.6 * m + 0.4 * self.prev  # temporal smoothing against edge flicker
        self.prev = m
        m = cv2.GaussianBlur(m, (0, 0), 1.2)
        return cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
