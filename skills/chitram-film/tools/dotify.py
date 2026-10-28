"""Dot-matrix treatment (TixFox / Chopper / Zippet-dots look) for any illustration or cut-out PNG.

Each CELL x CELL cell becomes one square dot: outlines stay ink, flat colours keep their colour,
a Bayer-dithered darker tone shades toward the lower-right, a few paper-white sparkle dots sit on
the lit side. Transparent stays transparent.

    python tools/dotify.py in.png out.png [--cell 6] [--paper #EDECE8] [--strength .55]

--cell     dot pitch in source pixels. Pick it from the DISPLAY size: dots read best at 3-5 px on a
           1080p frame, so cell = source_height / display_height * 4 (e.g. 1680 px source shown at
           1000 px -> 7).
--paper    fill the gaps between dots inside the silhouette with a paper colour. Use it when the
           figure sits in front of busy line-art (gates, bars, grids) that must NOT show through.
           Leave it off on dark backgrounds (the gaps then read as a print screen).
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

B = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def dotify(im, cell=6, ink=(27, 27, 27), strength=.55, paper=None):
    a = np.asarray(im.convert("RGBA")).astype(float)
    H, W = a.shape[:2]
    gh, gw = H // cell, W // cell
    dot = max(1, cell - 1)
    out = np.zeros((gh * cell, gw * cell, 4), np.uint8)
    yy, xx = np.mgrid[0:gh, 0:gw]
    light = 1 - np.clip(xx / gw * .55 + yy / gh * .75, 0, 1)      # lit from the top-left
    for j in range(gh):
        for i in range(gw):
            c = a[j * cell:(j + 1) * cell, i * cell:(i + 1) * cell]
            if c[..., 3].mean() < 110:
                continue
            px = c[..., :3].reshape(-1, 3)[c[..., 3].reshape(-1) > 128]
            if len(px) == 0:
                continue
            col = np.median(px, axis=0); lum = col.mean()
            th = B[j % 4, i % 4]
            if lum < 70:
                rgb = ink
            elif light[j, i] * .9 + .35 < th * strength + .2:
                rgb = tuple(int(v * .62) for v in col)                  # shade dot (same hue, darker)
            elif light[j, i] > .82 and th < .12 and lum < 235:
                rgb = (250, 248, 242)                                    # sparkle
            else:
                rgb = tuple(int(v) for v in col)
            out[j * cell:j * cell + dot, i * cell:i * cell + dot] = (*rgb, 255)
    res = Image.fromarray(out)
    if paper:
        p = tuple(int(paper.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4))
        m = res.getchannel("A").filter(ImageFilter.MaxFilter(3)).point(lambda v: 255 if v else 0)
        bg = Image.new("RGBA", res.size, (*p, 0)); bg.putalpha(m); bg.alpha_composite(res); res = bg
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--cell", type=int, default=6)
    ap.add_argument("--paper", default=None)
    ap.add_argument("--strength", type=float, default=.55)
    o = ap.parse_args()
    im = Image.open(o.src).convert("RGBA")
    bb = im.getbbox()
    if bb: im = im.crop(bb)
    dotify(im, cell=o.cell, strength=o.strength, paper=o.paper).save(o.dst)
    print("dotified", o.dst)
