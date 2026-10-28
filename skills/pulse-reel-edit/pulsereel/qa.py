"""QA: measure a rendered reel the same way the reference was measured, and draw
(1) a contact sheet (6 frames/s) and (2) a rhythm chart (blur / colour / brightness vs beats & cuts).
The agent opens both images and compares them with the reference targets."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .media import FrameReader, probe, save_json

REFERENCE_TARGETS = {
    "avg_shot_seconds": [0.8, 1.6],
    "cuts_in_blur_peak_pct": 75,
    "cuts_on_beat_pct": 80,
    "blur_peaks_per_10s": [5, 12],
}


def measure(video: str | Path):
    info = probe(video)
    w = 270
    h = int(round(w / info.aspect)) // 2 * 2
    rd = FrameReader(info, 0, info.duration + 1, w, h)
    rows, prev = [], None
    while True:
        f = rd.read()
        if f is None:
            break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        hue, sat = hsv[..., 0], hsv[..., 1].astype(np.float32)
        red = ((hue < 10) | (hue > 170)) & (sat > 60)
        rows.append({
            "sharp": float(cv2.Laplacian(g, cv2.CV_32F).var()),
            "sat_rest": float(sat[~red].mean()) if (~red).any() else 0.0,
            "sat_red": float(sat[red].mean()) if red.any() else 0.0,
            "luma": float(g.mean()),
            "diff": float(np.abs(g.astype(np.int16) - prev).mean()) if prev is not None else 0.0,
        })
        prev = g.astype(np.int16)
    rd.close()
    return info, rows


def qa(video: str | Path, timeline: dict | None = None, out_dir: str | Path | None = None) -> dict:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    video = Path(video)
    out_dir = Path(out_dir or video.parent / (video.stem + "_qa"))
    out_dir.mkdir(parents=True, exist_ok=True)
    info, rows = measure(video)
    fps = info.fps
    t = np.arange(len(rows)) / fps
    sharp = np.array([r["sharp"] for r in rows])
    ls = np.log(np.maximum(sharp, 1e-3))
    lo, hi = np.percentile(ls, 3), np.percentile(ls, 97)
    blur = 1 - np.clip((ls - lo) / (hi - lo + 1e-6), 0, 1)
    cuts = [s["start"] for s in timeline["shots"][1:]] if timeline else []
    beats = timeline.get("beats", []) if timeline else []

    # metrics
    metrics = {"duration": round(info.duration, 2), "fps": fps, "width": info.width, "height": info.height}
    if cuts:
        metrics["shots"] = len(cuts) + 1
        metrics["avg_shot_seconds"] = round(info.duration / (len(cuts) + 1), 2)
        win = int(0.12 * fps)
        inpk = [blur[max(0, int(c * fps) - win):int(c * fps) + win + 1].max() > 0.6 for c in cuts]
        metrics["cuts_in_blur_peak_pct"] = round(100 * float(np.mean(inpk)), 1)
        if beats:
            bb = np.array(beats)
            metrics["cuts_on_beat_pct"] = round(100 * float(np.mean([np.min(np.abs(bb - c)) < 0.05 for c in cuts])), 1)
    from scipy.signal import find_peaks

    pk, _ = find_peaks(blur, height=0.6, distance=int(0.3 * fps))
    metrics["blur_peaks_per_10s"] = round(len(pk) / max(info.duration, 1e-3) * 10, 1)
    metrics["targets"] = REFERENCE_TARGETS

    # rhythm chart
    fig, ax = plt.subplots(3, 1, figsize=(20, 8), sharex=True)
    for a in ax:
        for b in beats:
            a.axvline(b, c="#f0a030", lw=0.6, alpha=0.5)
        for c in cuts:
            a.axvline(c, c="#d00", lw=1.1, ls="--")
    ax[0].fill_between(t, blur, color="#5b7bd5", alpha=0.6)
    ax[0].set_ylabel("blur (focus pulse)")
    ax[1].plot(t, [r["sat_rest"] / 150 for r in rows], c="#2a9d8f", lw=1.8, label="colour: everything else")
    ax[1].plot(t, [r["sat_red"] / 230 for r in rows], c="#e63946", lw=1.8, label="colour: protected (red)")
    ax[1].legend(loc="upper right")
    ax[1].set_ylabel("saturation")
    ax[2].plot(t, [r["luma"] / 255 for r in rows], c="#222", lw=1.8)
    ax[2].set_ylabel("brightness")
    ax[2].set_xlabel("seconds  (orange = beats, red dashed = cuts)")
    ax[2].set_xticks(np.arange(0, info.duration + 1, 1))
    fig.suptitle(f"{video.name}: {metrics}", fontsize=9)
    plt.tight_layout()
    chart = out_dir / "rhythm.png"
    plt.savefig(chart, dpi=70)
    plt.close(fig)

    # contact sheets: every 5th frame, 18 per sheet
    sheets = []
    tw = 200
    th = int(round(tw / info.aspect)) // 2 * 2
    rd = FrameReader(info, 0, info.duration + 1, tw, th, fps=fps / 5.0)
    tiles = []
    k = 0
    while True:
        f = rd.read()
        if f is None:
            break
        f = f.copy()
        cv2.rectangle(f, (0, 0), (70, 18), (0, 0, 0), -1)
        cv2.putText(f, f"{k * 5 / fps:5.2f}s", (2, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1, cv2.LINE_AA)
        tiles.append(f)
        k += 1
    rd.close()
    for s0 in range(0, len(tiles), 18):
        chunk = tiles[s0:s0 + 18]
        while len(chunk) % 6:
            chunk.append(np.zeros_like(tiles[0]))
        rows_im = [np.hstack(chunk[r:r + 6]) for r in range(0, len(chunk), 6)]
        p = out_dir / f"sheet_{s0 // 18 + 1:02d}.jpg"
        cv2.imwrite(str(p), np.vstack(rows_im), [cv2.IMWRITE_JPEG_QUALITY, 85])
        sheets.append(str(p))
    report = {"video": str(video), "metrics": metrics, "chart": str(chart), "sheets": sheets}
    save_json(report, out_dir / "qa.json")
    return report
