"""Footage analysis: probe every clip, score moments, and draw contact sheets
that the agent LOOKS AT before choosing shots."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .media import FrameReader, list_media, probe, save_json
from .looks import hue_mask

SHEET_COLS = 6
TILE_W = 240


def _sample_clip(info, every: float, protect_hue: float, tile_w: int):
    """Decode the clip at a low frame rate and return per-sample metrics + tiles."""
    tile_h = int(round(tile_w / max(info.aspect, 0.2)))
    tile_h += tile_h % 2
    # decode at native aspect (no crop) at small size
    rd = FrameReader(info, 0.0, info.duration + 1, tile_w, tile_h, fps=1.0 / every)
    step = 1
    rows, tiles, prev = [], [], None
    i = 0
    while True:
        f = rd.read()
        if f is None:
            break
        if i % step == 0:
            t = i / rd.fps
            g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
            sharp = float(cv2.Laplacian(g, cv2.CV_32F).var())
            motion = float(np.abs(g.astype(np.int16) - prev).mean()) if prev is not None else 0.0
            hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
            colour_cov = float(hue_mask(hsv, protect_hue).mean())
            top = g[: g.shape[0] // 3]
            headroom = float(1.0 / (1.0 + cv2.Laplacian(top, cv2.CV_32F).var() / 50.0))
            rows.append({"t": round(t, 2), "sharp": round(sharp, 1), "motion": round(motion, 2),
                         "colour": round(colour_cov, 3), "luma": round(float(g.mean()) / 255, 3),
                         "headroom": round(headroom, 3)})
            tiles.append((t, f.copy()))
            prev = g.astype(np.int16)
        i += 1
    rd.close()
    return rows, tiles


def _sheet(tiles, title: str, out: Path, max_tiles: int = 36):
    if not tiles:
        return None
    if len(tiles) > max_tiles:
        idx = np.linspace(0, len(tiles) - 1, max_tiles).round().astype(int)
        tiles = [tiles[k] for k in idx]
    th, tw = tiles[0][1].shape[:2]
    cols = min(SHEET_COLS, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    head = 34
    sheet = np.full((rows * th + head, cols * tw, 3), 20, np.uint8)
    cv2.putText(sheet, title[:80], (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    for k, (t, im) in enumerate(tiles):
        r, c = divmod(k, cols)
        y, x = head + r * th, c * tw
        sheet[y:y + th, x:x + tw] = im
        lab = f"{t:5.1f}s"
        cv2.rectangle(sheet, (x, y), (x + 62, y + 20), (0, 0, 0), -1)
        cv2.putText(sheet, lab, (x + 3, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 1, cv2.LINE_AA)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return str(out)


def best_windows(rows, length: float, n: int = 4):
    """Return up to n non-overlapping windows [t0, t0+length] ranked by a style score:
    sharp, moving (spins/fabric), and showing the protected colour."""
    if not rows:
        return []
    t = np.array([r["t"] for r in rows])
    def norm(a):
        a = np.asarray(a, float)
        return (a - a.min()) / (np.ptp(a) + 1e-6)
    s = 0.35 * norm(np.log1p([r["sharp"] for r in rows])) + 0.4 * norm([r["motion"] for r in rows]) \
        + 0.25 * norm([r["colour"] for r in rows])
    dt = (t[1] - t[0]) if len(t) > 1 else 0.5
    w = max(1, int(round(length / dt)))
    if len(s) <= w:
        return [{"t0": 0.0, "score": round(float(s.mean()), 3)}]
    win = np.convolve(s, np.ones(w) / w, mode="valid")
    out, used = [], np.zeros(len(win), bool)
    for k in np.argsort(-win):
        if used[k]:
            continue
        out.append({"t0": round(float(t[k]), 2), "score": round(float(win[k]), 3)})
        used[max(0, k - w):k + w] = True
        if len(out) >= n:
            break
    return out


def analyze_folder(folder: str | Path, out_dir: str | Path, song: str | None = None,
                   protect_hue: float = 0.0, every: float = 0.25, target_duration: float = 30.0):
    folder, out_dir = Path(folder), Path(out_dir)
    vids, auds = list_media(folder)
    if not vids:
        raise SystemExit(f"No video files found in {folder}")
    clips = []
    for k, v in enumerate(vids):
        info = probe(v)
        if info.duration <= 0.05 or info.width == 0:
            print(f"  skip (unreadable): {v.name}")
            continue
        print(f"  [{k + 1}/{len(vids)}] {v.name}: {info.width}x{info.height} {info.fps:.2f}fps "
              f"{info.duration:.1f}s{' HDR' if info.is_hdr else ''}")
        rows, tiles = _sample_clip(info, every, protect_hue, TILE_W if info.aspect < 1 else 320)
        cid = f"C{len(clips) + 1:02d}"
        sheet = _sheet(tiles, f"{cid}  {v.name}  ({info.duration:.1f}s, {info.fps:.0f}fps)",
                       out_dir / "sheets" / f"{cid}.jpg")
        cov = float(np.mean([r["colour"] for r in rows])) if rows else 0.0
        clips.append({
            "id": cid,
            "path": str(v.resolve()),
            "name": v.name,
            "probe": info.to_dict(),
            "slowmo_capable": info.fps >= 47,
            "kind": "subject" if cov > 0.02 else "broll",
            "colour_coverage": round(cov, 4),
            "median_luma": round(float(np.median([r["luma"] for r in rows])) if rows else 0.5, 3),
            "sheet": sheet,
            "samples": rows,
            "best_windows": best_windows(rows, 1.2),
        })
    music = None
    song_path = Path(song) if song else (auds[0] if auds else None)
    if song_path:
        from .beats import analyze_music
        print(f"  music: {song_path.name}")
        music = analyze_music(song_path, target_duration)
        print(f"    tempo {music['tempo']} BPM, drop at {music['drop']}s, suggested start {music['suggested_start']}s")
    else:
        print("  WARNING: no song found - pass --song. The edit is timed to the music.")
    result = {"footage_dir": str(folder.resolve()), "protect_hue": protect_hue, "clips": clips, "music": music}
    save_json(result, out_dir / "analysis.json")
    return result
