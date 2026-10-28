#!/usr/bin/env python3
"""
Asset prep for product references (screenshots, mockups, logos).

  crop     python3 prep_image.py crop   in.png out.png  x0 y0 x1 y1  [--scale 2] [--sharpen]
  unwarp   python3 prep_image.py unwarp in.png out.png  x1,y1 x2,y2 x3,y3 x4,y4  --size 1600x940
           (corners TL TR BR BL of a screen seen at an angle -> flat rectangle)
  key      python3 prep_image.py key    logo.png out.png [--bg white|black|auto] [--tol 60]
           (logo on a flat background -> transparent PNG, edge colours decontaminated, trimmed)
  probe    python3 prep_image.py probe  in.png  row=<y> | col=<x>
           (prints strong brightness transitions along a row/column: find screen edges fast)
  palette  python3 prep_image.py palette in.png [--n 6]   (dominant colours as hex)

Needs: pillow numpy opencv-python-headless
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def opt(a, k, d=None):
    return a[a.index(k) + 1] if k in a else d


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    cmd = a[0]
    if cmd == "crop":
        im = Image.open(a[1]).convert("RGBA")
        x0, y0, x1, y1 = map(int, a[3:7])
        im = im.crop((x0, y0, x1, y1))
        k = float(opt(a, "--scale", 1))
        if k != 1: im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        if "--sharpen" in a: im = im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=70, threshold=2))
        im.save(a[2]); print(a[2], im.size)
    elif cmd == "unwarp":
        import cv2
        src = cv2.imread(a[1], cv2.IMREAD_UNCHANGED)
        pts = np.float32([list(map(float, p.split(","))) for p in a[3:7]])
        w, h = map(int, opt(a, "--size", "1600x1000").split("x"))
        dst = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        M = cv2.getPerspectiveTransform(pts, dst)
        out = cv2.warpPerspective(src, M, (w, h), flags=cv2.INTER_LANCZOS4)
        cv2.imwrite(a[2], out); print(a[2], (w, h))
    elif cmd == "key":
        import cv2
        L = np.asarray(Image.open(a[1]).convert("RGB")).astype(np.float32)
        bg = opt(a, "--bg", "auto")
        if bg == "auto":
            corners = np.concatenate([L[:4, :4].reshape(-1, 3), L[-4:, -4:].reshape(-1, 3)])
            ref = corners.mean(0)
        else:
            ref = np.array([255, 255, 255] if bg == "white" else [0, 0, 0], np.float32)
        tol = float(opt(a, "--tol", 60))
        d = np.sqrt(((L - ref) ** 2).sum(2))
        mask = (d > tol).astype(np.uint8)
        er = cv2.erode(mask, np.ones((5, 5), np.uint8))
        rgb = cv2.inpaint(L.astype(np.uint8), (1 - er) * 255, 5, cv2.INPAINT_TELEA)
        alpha = cv2.GaussianBlur(np.clip((d - tol / 3) / (tol * 2.3), 0, 1), (0, 0), 0.6)
        ys, xs = np.where(mask)
        x0, x1, y0, y1 = max(0, xs.min() - 6), xs.max() + 7, max(0, ys.min() - 6), ys.max() + 7
        out = np.dstack([rgb, (alpha * 255).astype(np.uint8)])[y0:y1, x0:x1]
        Image.fromarray(out).save(a[2]); print(a[2], out.shape[1], "x", out.shape[0])
    elif cmd == "probe":
        g = np.asarray(Image.open(a[1]).convert("L")).astype(int)
        k, v = a[2].split("="); v = int(v)
        line = g[v] if k == "row" else g[:, v]
        jumps = [i for i in range(1, len(line)) if abs(line[i] - line[i - 1]) > 40]
        print(f"{k} {v}: transitions at", jumps)
    elif cmd == "palette":
        im = Image.open(a[1]).convert("RGB").resize((200, 200))
        n = int(opt(a, "--n", 6))
        q = im.quantize(colors=n, method=Image.MEDIANCUT)
        pal = q.getpalette()[: n * 3]
        counts = sorted(q.getcolors(), reverse=True)
        for c, i in counts:
            r, g, b = pal[i * 3: i * 3 + 3]
            print(f"#{r:02X}{g:02X}{b:02X}  {100 * c / 40000:.1f}%")
    else:
        print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main()
