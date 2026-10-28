"""Per-frame audio envelopes + oscilloscope samples -> assets/env.js
usage: python3 envelopes.py song.mp3 out/env.js --dur 69 --fps 30"""
import sys, json, argparse, subprocess, numpy as np
from scipy.signal import butter, sosfilt
ap = argparse.ArgumentParser(); ap.add_argument("song"); ap.add_argument("out"); ap.add_argument("--dur", type=float, default=9999); ap.add_argument("--fps", type=int, default=30); a = ap.parse_args()
sr = 24000; hop = sr // a.fps
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-t",str(a.dur),"-i",a.song,"-ac","1","-ar",str(sr),"-f","s16le","-"],capture_output=True).stdout, np.int16).astype(float)/32768
voc = sosfilt(butter(4, [300, 3400], "bandpass", fs=sr, output="sos"), x); low = sosfilt(butter(4, 150, "lowpass", fs=sr, output="sos"), x)
def env(s): n = len(s)//hop; return 20*np.log10(np.array([np.sqrt(np.mean(s[i*hop:(i+1)*hop]**2)) for i in range(n)])+1e-7)
nm = lambda d, lo, hi: np.clip((d-lo)/(hi-lo), 0, 1)
def ar(e, att=.6, rel=.12):
    o = np.zeros_like(e); p = 0
    for i, v in enumerate(e): p += (v-p)*(att if v > p else rel); o[i] = p
    return o
osc = [[round(float(v), 3) for v in voc[i*hop:i*hop+hop][::max(1, hop//96)][:96]] for i in range(len(x)//hop)]
o = {"fps": a.fps, "all": [round(float(q), 3) for q in ar(nm(env(x), -40, -6))], "voc": [round(float(q), 3) for q in ar(nm(env(voc), -45, -10))],
     "low": [round(float(q), 3) for q in ar(nm(env(low), -40, -8), .7, .2)], "osc": osc}
open(a.out, "w").write("window.ENV=" + json.dumps(o, separators=(",", ":")) + ";")
