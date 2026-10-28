#!/usr/bin/env python3
"""sync.py: sync camera angles / external audio to a reference by their sound (LONGFORM.md §3).

  python sync.py REF OTHER [OTHER...] [--window 90] [--out sync.json]

For each OTHER, finds the offset (seconds) so that  ref_time = other_time + offset, measured twice:
on a window at the START and at the END of the overlap. If the two disagree by more than one frame,
the clocks DRIFT (a phone or camera recording at 29.97 vs 30, or a long take): the report gives the
drift in ms/minute so you can split the clip or retime the audio. Works on any media ffmpeg can read.
Method: 2 kHz mono, onset-strength envelope, FFT cross-correlation, parabolic peak refinement.
Confidence = peak / 2nd-best peak (> 3 is solid; < 1.5 means the angles share no clear sound).
"""
import json, os, subprocess, sys
import numpy as np

SR = 2000
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "audio"))
from ffbin import ffmpeg
FF = ffmpeg()


def opt(a, name, default=None, cast=str):
    return cast(a[a.index(name) + 1]) if name in a and a.index(name) + 1 < len(a) else default


def pcm(path):
    r = subprocess.run([FF, "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def onset_env(x):
    hop = SR // 100                                     # 10 ms
    n = len(x) // hop
    e = np.log1p(100 * np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)))
    d = np.maximum(0, np.diff(e, prepend=e[:1]))        # rises only: claps, consonants, hits
    return (d - d.mean()) / (d.std() + 1e-9)


def xcorr(a, b, max_lag):
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
    c = np.concatenate([c[-max_lag:], c[:max_lag + 1]])     # lags -max..+max
    k = int(np.argmax(c)); pk = c[k]
    if 0 < k < len(c) - 1:                                  # parabolic refinement (sub-10 ms)
        y0, y1, y2 = c[k - 1], c[k], c[k + 1]; den = y0 - 2 * y1 + y2
        frac = 0.5 * (y0 - y2) / den if den else 0
    else:
        frac = 0
    mask = np.ones_like(c, bool); mask[max(0, k - 30):k + 31] = False
    second = c[mask].max() if mask.any() else 1e-9
    return (k - max_lag + frac), float(pk / max(second, 1e-9))


def offset(ref_env, oth_env, r0, coarse, win, pad=300):
    """Fine offset (s) for the ref window [r0, r0+win) (10 ms frames), searching +-pad frames around coarse."""
    a = ref_env[r0:r0 + win]
    b0 = max(0, int(r0 - coarse * 100) - pad)
    b = oth_env[b0:b0 + win + 2 * pad]
    if len(a) < 200 or len(b) < 200: return None, 0.0
    lag, conf = xcorr(a, b, win + 2 * pad)
    return (r0 - b0 + lag) / 100.0, conf


def blockmax(e, k=4):
    n = len(e) // k
    return e[:n * k].reshape(n, k).max(1)


def main(a):
    ref = a[0]; others = [x for x in a[1:] if not x.startswith("--") and x not in (opt(a, "--window"), opt(a, "--out"))]
    win = int(opt(a, "--window", 90, float) * 100)
    R = onset_env(pcm(ref)); res = {"ref": ref, "items": []}
    for o in others:
        O = onset_env(pcm(o))
        # coarse: whole-file correlation (decimated) to find the rough offset
        lag, _ = xcorr(blockmax(R), blockmax(O), max(len(R), len(O)) // 4)
        coarse = lag * 4 / 100.0
        # fine: a window at the start and one at the end of the overlap
        ov0 = max(0.0, coarse); ov1 = min(len(R) / 100, len(O) / 100 + coarse)
        w = min(win, int((ov1 - ov0) * 100) - 200)
        s_off, s_conf = offset(R, O, int((ov0 + .5) * 100), coarse, w)
        e_t = max(ov0 + .5, ov1 - w / 100 - .5)
        e_off, e_conf = offset(R, O, int(e_t * 100), coarse + ((s_off or coarse) - coarse), w)
        conf = min(s_conf, e_conf) if e_off is not None else s_conf
        item = {"file": o, "offset": round(s_off if s_off is not None else coarse, 4), "confidence": round(conf, 2),
                "end_offset": None if e_off is None else round(e_off, 4), "overlap": [round(ov0, 2), round(ov1, 2)]}
        if e_off is not None and s_off is not None and e_t - ov0 > 20:
            span_min = (e_t - ov0) / 60
            item["drift_ms_per_min"] = round((e_off - s_off) * 1000 / max(span_min, 1e-6), 2)
        res["items"].append(item)
        d = item.get("drift_ms_per_min")
        print(f"{os.path.basename(o)}: ref = other + {item['offset']:+.3f}s  (confidence {item['confidence']})"
              + (f"  end {item['end_offset']:+.3f}s  drift {d:+.1f} ms/min" if d is not None else "")
              + ("  << DRIFT: split or retime" if d is not None and abs(d) > 20 else "")
              + ("  << LOW CONFIDENCE: check by eye (clap/slate)" if item["confidence"] < 1.5 else ""))
    if opt(a, "--out"):
        json.dump(res, open(opt(a, "--out"), "w"), indent=1); print("->", opt(a, "--out"))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    main(sys.argv[1:])
