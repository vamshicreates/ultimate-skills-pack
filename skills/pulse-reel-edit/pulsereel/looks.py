"""Colour: per-shot light correction, the three reference grades, the protected-colour
mask used for the 'colour pop', and .cube LUT export for DaVinci Resolve / FilmCraft.

Every look is a pure function on RGB floats in 0..1. The renderer bakes each look into a
full 256^3 lookup table once (cached on disk), so applying it per frame is a single gather;
the same function is sampled to write a 33^3 .cube, so Resolve gets the identical look.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------- look presets
# Tuned against frame measurements of the reference reel (see references/style-reference.md).
LOOKS: dict[str, dict] = {
    # 0 - drop: dark, moody. Crushed blacks, muted teal-greens, cool grey sky, deep red.
    "moody": {
        "target_luma": 0.38, "exposure": -0.15, "contrast": 0.22, "pivot": 0.42, "black_lift": 0.0, "black_crush": 0.025,
        "shoulder": 0.25, "warmth": 0.0, "sat": 0.94,
        "bands": [
            {"hue": 110, "width": 55, "sat": 0.66, "lum": 0.84, "shift": 7},    # greens -> darker, slightly teal
            {"hue": 205, "width": 45, "sat": 0.40, "lum": 0.95, "shift": 0},    # sky / blues -> grey
            {"hue": 0, "width": 22, "sat": 1.12, "lum": 0.90, "shift": -3},     # reds deep and rich (crimson)
            {"hue": 25, "width": 16, "sat": 0.92, "lum": 1.0, "shift": 0},      # skin calm
        ],
        "shadow_tint": [0.03, 0.05, 0.05], "shadow_amt": 0.2,
        "high_tint": [0.92, 0.93, 0.94], "high_amt": 0.12,
    },
    # drop - ~80%: airy. Bright, highlights rolling into cream, pastel yellow-greens, bright red.
    "airy": {
        "target_luma": 0.55, "exposure": 0.38, "contrast": 0.08, "pivot": 0.45, "black_lift": 0.035, "black_crush": 0.0,
        "shoulder": 0.65, "warmth": 0.02, "sat": 1.0,
        "bands": [
            {"hue": 100, "width": 55, "sat": 0.82, "lum": 1.10, "shift": -8},   # greens -> fresh yellow-green
            {"hue": 205, "width": 50, "sat": 0.25, "lum": 1.10, "shift": -25},  # sky -> cream
            {"hue": 0, "width": 24, "sat": 1.10, "lum": 1.0, "shift": -6},      # keep reds red, not orange
            {"hue": 25, "width": 14, "sat": 0.95, "lum": 1.03, "shift": 0},
        ],
        "shadow_tint": [0.10, 0.06, 0.05], "shadow_amt": 0.15,
        "high_tint": [1.0, 0.972, 0.90], "high_amt": 0.55,
    },
    # last ~20%: rich greens + overcast teal-grey sky.
    "overcast": {
        "target_luma": 0.45, "exposure": -0.05, "contrast": 0.16, "pivot": 0.45, "black_lift": 0.0, "black_crush": 0.015,
        "shoulder": 0.3, "warmth": -0.03, "sat": 1.0,
        "bands": [
            {"hue": 105, "width": 55, "sat": 1.08, "lum": 0.92, "shift": 4},
            {"hue": 205, "width": 50, "sat": 0.35, "lum": 0.98, "shift": -15},
            {"hue": 0, "width": 22, "sat": 1.08, "lum": 0.97, "shift": -3},
        ],
        "shadow_tint": [0.03, 0.06, 0.06], "shadow_amt": 0.22,
        "high_tint": [0.90, 0.94, 0.94], "high_amt": 0.2,
    },
    # 'light correction only': tidy contrast + saturation, no stylisation.
    "natural": {
        "target_luma": 0.45, "exposure": 0.0, "contrast": 0.08, "pivot": 0.45, "black_lift": 0.0, "black_crush": 0.01,
        "shoulder": 0.3, "warmth": 0.0, "sat": 1.05, "bands": [],
        "shadow_tint": [0, 0, 0], "shadow_amt": 0.0, "high_tint": [1, 1, 1], "high_amt": 0.0,
    },
    "none": {},
}


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / (d + 1e-9), 0)
    gc = np.where(m, (mx - g) / (d + 1e-9), 0)
    bc = np.where(m, (mx - b) / (d + 1e-9), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = np.where(m, (h / 6.0) % 1.0, 0.0)
    s = np.where(mx > 1e-6, d / (mx + 1e-9), 0)
    return np.stack([h * 360.0, s, mx], -1)


def hsv_to_rgb(hsv):
    h = (hsv[..., 0] / 360.0) % 1.0
    s, v = hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6.0)
    f = h * 6.0 - i
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    i = i.astype(np.int32) % 6
    conds = [i == k for k in range(6)]
    r = np.select(conds, [v, q, p, p, t, v])
    g = np.select(conds, [t, v, v, q, p, p])
    b = np.select(conds, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1)


def _hue_weight(h, center, width):
    d = np.abs(((h - center) + 180.0) % 360.0 - 180.0)
    return _smoothstep(width, width * 0.35, d)


def apply_look(rgb: np.ndarray, p: dict) -> np.ndarray:
    """rgb: float array (..., 3) in 0..1 -> graded float array."""
    if not p:
        return rgb
    x = rgb.astype(np.float32)
    w = p.get("warmth", 0.0)
    x = x * np.array([1 + w, 1 + w * 0.15, 1 - w], np.float32)
    # exposure in a gamma-ish domain + soft shoulder so highlights roll off instead of clipping hard
    x = x * (2.0 ** p.get("exposure", 0.0))
    sh = p.get("shoulder", 0.0)
    if sh > 0:
        k = 0.72
        over = np.maximum(x - k, 0)
        x = np.where(x > k, k + (1 - k) * (1 - np.exp(-over / ((1 - k) * (1 + sh)))) , x)
    x = np.clip(x, 0, 1)
    # contrast S-curve around pivot
    c, pv = p.get("contrast", 0.0), p.get("pivot", 0.45)
    if c:
        y = x - pv
        x = pv + y * (1 + c) / (1 + c * np.abs(y) * 2.0)
    x = np.clip(x, 0, 1)
    bl, bc = p.get("black_lift", 0.0), p.get("black_crush", 0.0)
    if bc:
        x = np.clip((x - bc) / (1 - bc), 0, 1)
    if bl:
        x = bl + x * (1 - bl)
    # hue-selective adjustments
    bands = p.get("bands", [])
    if bands or p.get("sat", 1.0) != 1.0:
        hsv = rgb_to_hsv(x)
        h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
        smul = np.ones_like(s)
        vmul = np.ones_like(v)
        hadd = np.zeros_like(h)
        chroma_w = _smoothstep(0.04, 0.18, s)
        for b in bands:
            wgt = _hue_weight(h, b["hue"], b["width"]) * chroma_w
            smul *= 1 + (b.get("sat", 1) - 1) * wgt
            vmul *= 1 + (b.get("lum", 1) - 1) * wgt
            hadd += b.get("shift", 0) * wgt
        s = np.clip(s * smul * p.get("sat", 1.0), 0, 1)
        v = np.clip(v * vmul, 0, 1)
        x = hsv_to_rgb(np.stack([h + hadd, s, v], -1))
    # split toning
    lum = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    lum = lum[..., None]
    sa = p.get("shadow_amt", 0.0)
    if sa:
        wsh = (1 - _smoothstep(0.0, 0.45, lum)) * sa
        x = x + (np.array(p["shadow_tint"], np.float32) - x) * wsh * 0.5
    ha = p.get("high_amt", 0.0)
    if ha:
        whi = _smoothstep(0.55, 1.0, lum) * ha
        tint = np.array(p["high_tint"], np.float32)
        tint = tint / max(float(tint @ np.array([0.2126, 0.7152, 0.0722], np.float32)), 1e-3)
        x = x + (tint * lum - x) * whi  # luminance-preserving hue shift of the highlights
    return np.clip(x, 0, 1)


# ---------------------------------------------------------------- LUT baking
def _cache_dir() -> Path:
    base = os.environ.get("PULSE_CACHE") or (Path.home() / ".cache" / "pulse-reel-edit")
    d = Path(base) / "luts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def look_params(name_or_dict) -> dict:
    if isinstance(name_or_dict, dict):
        return name_or_dict
    if name_or_dict not in LOOKS:
        raise KeyError(f"unknown look '{name_or_dict}'. Options: {', '.join(LOOKS)}")
    return LOOKS[name_or_dict]


def full_lut(name_or_dict) -> np.ndarray | None:
    """256^3 x 3 uint8 table in BGR order, indexed by (R<<16)|(G<<8)|B. Cached on disk."""
    p = look_params(name_or_dict)
    if not p:
        return None
    key = hashlib.sha1(json.dumps(p, sort_keys=True).encode()).hexdigest()[:12]
    f = _cache_dir() / f"lut256_{key}.npy"
    if f.exists():
        try:
            return np.load(f, mmap_mode=None)
        except Exception:
            f.unlink(missing_ok=True)
    out = np.empty((256 ** 3, 3), np.uint8)
    lv = np.arange(256, dtype=np.float32) / 255.0
    chunk = 256 * 256 * 16  # 16 red levels per chunk
    for r0 in range(0, 256, 16):
        r = np.repeat(lv[r0:r0 + 16], 256 * 256)
        g = np.tile(np.repeat(lv, 256), 16)
        b = np.tile(lv, 256 * 16)
        rgb = np.stack([r, g, b], -1)
        y = apply_look(rgb, p)
        out[r0 * 65536:(r0 + 16) * 65536] = (y[:, ::-1] * 255 + 0.5).astype(np.uint8)
    np.save(f, out)
    return out


def apply_lut_bgr(frame: np.ndarray, lut: np.ndarray | None) -> np.ndarray:
    if lut is None:
        return frame
    f = frame.astype(np.int32)
    idx = (f[..., 2] << 16) | (f[..., 1] << 8) | f[..., 0]
    return lut[idx]


def write_cube(name_or_dict, path: str | Path, size: int = 33, title: str | None = None):
    p = look_params(name_or_dict)
    lv = np.linspace(0, 1, size, dtype=np.float32)
    # .cube order: red changes fastest, then green, then blue
    b, g, r = np.meshgrid(lv, lv, lv, indexing="ij")
    rgb = np.stack([r.ravel(), g.ravel(), b.ravel()], -1)
    y = apply_look(rgb, p) if p else rgb
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        fh.write(f'TITLE "{title or (name_or_dict if isinstance(name_or_dict, str) else "pulse look")}"\n')
        fh.write(f"LUT_3D_SIZE {size}\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n")
        for v in y:
            fh.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
    return path


# ---------------------------------------------------------------- correction
def shot_correction(frames: list[np.ndarray], target_luma: float = 0.45, strength: float = 0.7,
                    wb_strength: float = 0.0, max_stops: float = 0.75) -> np.ndarray:
    """Per-shot gains (B, G, R multipliers) that normalise exposure and gently neutralise
    colour casts (grey-world on the mid-tones). Returns float32[3]."""
    if not frames:
        return np.ones(3, np.float32)
    acc = []
    for f in frames:
        sm = cv2.resize(f, (90, 160), interpolation=cv2.INTER_AREA).reshape(-1, 3).astype(np.float32) / 255
        acc.append(sm)
    px = np.concatenate(acc)
    lum = px @ np.array([0.0722, 0.7152, 0.2126], np.float32)
    med = float(np.median(lum))
    gain = np.clip(target_luma / max(med, 1e-3), 2 ** -max_stops, 2 ** max_stops) ** strength
    mids = px[(lum > 0.2) & (lum < 0.8)]
    wb = np.ones(3, np.float32)
    if wb_strength > 0 and len(mids) > 100:
        mean = mids.mean(0)
        wb = (mean.mean() / np.maximum(mean, 1e-3)) ** wb_strength
        wb = np.clip(wb, 0.93, 1.07)  # gentle: remove casts, keep intentional warmth
    return (wb * gain).astype(np.float32)


def apply_gain(frame: np.ndarray, gains: np.ndarray) -> np.ndarray:
    if gains is None or np.allclose(gains, 1, atol=1e-3):
        return frame
    lut = np.clip(np.arange(256, dtype=np.float32)[None, :] * gains[:, None], 0, 255).astype(np.uint8)
    out = np.empty_like(frame)
    for c in range(3):
        out[..., c] = lut[c][frame[..., c]]
    return out


# ---------------------------------------------------------------- colour pop
def hue_mask(hsv_cv: np.ndarray, hue_deg: float = 0.0, width: float = 18.0, min_sat: float = 0.28,
             feather: float = 10.0) -> np.ndarray:
    """Soft 0..1 mask of pixels near `hue_deg` (0 = red). hsv_cv: OpenCV HSV uint8 (H 0..179)."""
    h = hsv_cv[..., 0].astype(np.float32) * 2.0
    s = hsv_cv[..., 1].astype(np.float32) / 255.0
    v = hsv_cv[..., 2].astype(np.float32) / 255.0
    d = np.abs(((h - hue_deg) + 180.0) % 360.0 - 180.0)
    m = _smoothstep(width + feather, width, d) * _smoothstep(min_sat, min_sat + 0.15, s) * _smoothstep(0.08, 0.2, v)
    return m.astype(np.float32)


def colour_pop(frame: np.ndarray, rest: float, keep: float, hue_deg: float = 0.0,
               width: float = 18.0, min_sat: float = 0.28, mask: np.ndarray | None = None) -> np.ndarray:
    """Scale saturation: `keep` for the protected colour, `rest` for everything else
    (1 = untouched, 0 = grey)."""
    if rest >= 0.999 and keep >= 0.999:
        return frame
    f = frame.astype(np.float32)
    if mask is None:
        small = cv2.resize(frame, (frame.shape[1] // 4, frame.shape[0] // 4), interpolation=cv2.INTER_AREA)
        m = hue_mask(cv2.cvtColor(small, cv2.COLOR_BGR2HSV), hue_deg, width, min_sat)
        m = cv2.GaussianBlur(m, (0, 0), 1.5)
        mask = cv2.resize(m, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
    fac = (mask * keep + (1 - mask) * rest)[..., None]
    y = (f @ np.array([0.0722, 0.7152, 0.2126], np.float32))[..., None]
    return np.clip(y + (f - y) * fac, 0, 255).astype(np.uint8)


def lookbook(src: str, out: str, t: float | None = None, names=("none", "natural", "moody", "airy", "overcast")):
    """Grid of one frame through every look (plus light correction), for choosing looks."""
    from .media import FrameReader, probe

    info = probe(src)
    w = 360
    h = int(round(w / info.aspect)) // 2 * 2
    if Path(src).suffix.lower() in (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"):
        frame = cv2.resize(cv2.imread(src), (w, h), interpolation=cv2.INTER_AREA)
    else:
        rd = FrameReader(info, t if t is not None else info.duration / 2, 0.5, w, h)
        frame = rd.read()
        rd.close()
    tiles = []
    for n in names:
        tgt = LOOKS.get(n, {}).get("target_luma", 0.45)
        f = frame if n == "none" else apply_lut_bgr(apply_gain(frame, shot_correction([frame], tgt)), full_lut(n))
        f = f.copy()
        cv2.rectangle(f, (0, 0), (w, 26), (0, 0, 0), -1)
        cv2.putText(f, n if n != "none" else "original", (6, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(f)
    cv2.imwrite(out, np.hstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 88])
    return out
