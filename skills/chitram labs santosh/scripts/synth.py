#!/usr/bin/env python3
"""
Chitram Film audio engine — renders a full soundtrack (score + SFX + optional voiceover)
from a JSON cue sheet. Deterministic: same cues -> same WAV.

    python3 synth.py cues.json out.wav

Needs: numpy, scipy (pip install numpy scipy). ffmpeg only when a voiceover is used.

Cue sheet (all times in seconds, absolute film time):
{
  "duration": 30,
  "mood": "warm",                 # warm | bright | dark | playful  (sets timbre & brightness)
  "bpm": 96,
  "chords": [ {"t": 0, "notes": "D3 A3 D4 E4 A4"}, {"t": 7, "notes": "B2 F#3 D4 F#4 A4 C#5"} ],
  "pulse":  {"from": 3, "to": 27, "gain": 0.5, "skip": [[15, 16]]},   # soft kick + offbeat plucks
  "piano":  [ {"t": 1.5, "note": "D5"} ],                               # sparse piano notes
  "plucks": [ {"t": 4.2, "note": "A5"} ],                               # soft plucks (shapes travelling)
  "sfx": [
    {"t": 10.9, "type": "shimmer"},          # glassy card lift / sparkle
    {"t": 15.0, "type": "whoosh", "dur": 1}, # light-streak whip / transition (pans L->R)
    {"t": 12.0, "type": "swoosh"},           # short airy swoosh (ribbons, bands, blob wipes)
    {"t": 23.3, "type": "riser", "dur": 1.2},# low riser into a section
    {"t": 3.0,  "type": "impact"},           # soft low thump (object lands / reveal)
    {"t": 5.0,  "type": "click"},            # UI click (toggles, dropdowns, karaoke words)
    {"t": 6.0,  "type": "tick"},             # tiny digital tick (glitch-block reveals)
    {"t": 7.0,  "type": "glitch"},           # short digital glitch burst
    {"t": 8.0,  "type": "pop"},              # bubbly pop (sticker / overshoot pop-in)
    {"t": 29.0, "type": "chime"}             # warm resolved chime (logo)
  ],
  "vo": {                                    # optional voiceover placement + ducking
    "file": "assets/vo.m4a", "tempo": 1.0, "gain": 1.0, "duck": 0.55,
    "phrases": [ {"src": [0.00, 1.19], "at": 0.35} ]   # source window -> film time
  },
  "end": {"fade": 0.9},
  "master": {"reverb": 0.45, "music_gain": 1.0}
}
Every field except "duration" is optional. Any "gain" can be set per cue.
"""
import json, os, subprocess, sys, tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
NOTE = {"C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4, "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11}
MOODS = {
    #          pad cutoff, pad gain, harmonics, pluck bright, piano gain, reverb
    "warm":    dict(cut=1400, pad=0.34, harm=0.25, pl=1800, pno=0.11, rev=0.45),
    "bright":  dict(cut=3200, pad=0.26, harm=0.45, pl=4200, pno=0.10, rev=0.38),
    "dark":    dict(cut=900,  pad=0.36, harm=0.18, pl=1400, pno=0.09, rev=0.55),
    "playful": dict(cut=2600, pad=0.22, harm=0.35, pl=5000, pno=0.12, rev=0.30),
}


def midi(n):
    if isinstance(n, (int, float)):
        return float(n)
    n = n.strip().upper()
    name = n[:-1] if n[-1].isdigit() else n
    octv = int(n[-1]) if n[-1].isdigit() else 4
    if len(name) > 1 and name[-1] == "-":
        name = name[:-1]
    return 12 * (octv + 1) + NOTE[name]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, f, o=2):
    return sosfilt(butter(o, min(f, SR / 2 - 100), "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, a, b, o=2):
    return sosfilt(butter(o, [max(20, a), min(SR / 2 - 100, b)], "band", fs=SR, output="sos"), x)


class Mix:
    def __init__(self, dur):
        self.N = int(SR * dur)
        self.L = np.zeros(self.N)
        self.R = np.zeros(self.N)

    def add(self, sig, start, gain=1.0, pan=0.0):
        i = int(start * SR)
        if i < 0:
            sig = sig[-i:]; i = 0
        n = min(len(sig), self.N - i)
        if n <= 0:
            return
        l = np.cos((pan + 1) * np.pi / 4) * 1.414
        r = np.sin((pan + 1) * np.pi / 4) * 1.414
        self.L[i:i + n] += sig[:n] * gain * l
        self.R[i:i + n] += sig[:n] * gain * r

    def add_stereo(self, L, R, start, gain=1.0):
        i = int(start * SR); n = min(len(L), self.N - i)
        if n > 0:
            self.L[i:i + n] += L[:n] * gain; self.R[i:i + n] += R[:n] * gain


def env(n, a, r):
    e = np.ones(n); ai = int(a * SR); ri = int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai) ** 2
    if ri: e[-ri:] *= np.linspace(1, 0, ri) ** 2
    return e


# ------------------------------ instruments ------------------------------
def pad(notes, dur, mood, rng):
    n = int(dur * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        f = hz(m)
        for det in (-0.07, 0.0, 0.07):
            ff = f * 2 ** (det / 12)
            s += np.sin(2 * np.pi * ff * tt + rng.uniform(0, 6)) * 0.6 + mood["harm"] * np.sin(4 * np.pi * ff * tt)
    s /= max(1, len(notes)) * 3
    s = lp(s, mood["cut"])
    return s * (1 + 0.08 * np.sin(2 * np.pi * 0.25 * tt))


def piano(m, dur=3.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = hz(m); s = np.zeros(n)
    for h, a in [(1, 1), (2, .45), (3, .22), (4, .12), (5, .06), (6, .03)]:
        s += a * np.sin(2 * np.pi * f * h * np.sqrt(1 + 0.0004 * h * h) * tt) * np.exp(-tt * (1.3 + h * 0.9))
    return lp(s * np.minimum(1, tt / 0.004), 5000)


def pluck(m, bright=1800, dur=0.45):
    n = int(dur * SR); tt = np.arange(n) / SR; f = hz(m)
    s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 12)
    return lp(s * np.minimum(1, tt / 0.002), bright)


def thump():
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 48 + 40 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)


def shimmer(rng):
    n = int(1.4 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for f, a, dc in [(2637, 1, 4), (3520, .7, 5), (4699, .5, 6), (5274, .35, 7), (7040, .2, 9)]:
        s += a * np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) * np.exp(-tt * dc) * np.minimum(1, tt / 0.02)
    nz = hp(rng.standard_normal(n), 6000) * np.exp(-tt * 8) * np.minimum(1, tt / 0.05) * 0.25
    return (s * 0.3 + nz) * np.linspace(0.6, 1, n)


def whoosh(rng, dur=1.0, lo=300, hi=3800):
    n = int((dur + 0.2) * SR); tt = np.arange(n) / SR
    nz = rng.standard_normal(n)
    fc = lo + (hi - lo) * np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 2
    w = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        seg = nz[max(0, i - 512): i + blk]
        y = bp(seg, fc[i] * 0.6, fc[i] * 1.6)
        w[i:i + blk] = y[-len(nz[i:i + blk]):]
    return w * np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 1.5


def riser(rng, dur, f0=45, f1=95):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (tt / dur)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    s += lp(rng.standard_normal(n), 600) * 0.6 * (tt / dur)
    return s * (tt / dur) ** 2 * np.minimum(1, (dur - tt) / 0.08)


def chime(root=74):
    n = int(3.2 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for m, a in [(root, 1), (root + 7, .7), (root + 12, .6), (root + 16, .35), (root + 19, .25)]:
        f = hz(m)
        for h, ha in [(1, 1), (2.76, .25), (5.4, .08)]:
            s += a * ha * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (1.6 + h * 0.8))
    return s * np.minimum(1, tt / 0.003)


def click(rng):
    n = int(0.05 * SR); tt = np.arange(n) / SR
    return (hp(rng.standard_normal(n), 2500) * np.exp(-tt * 180) * 0.8 + np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 120) * 0.5)


def tick(rng):
    n = int(0.035 * SR); tt = np.arange(n) / SR
    return np.sign(np.sin(2 * np.pi * 3200 * tt)) * np.exp(-tt * 160) * 0.35 + hp(rng.standard_normal(n), 5000) * np.exp(-tt * 200) * 0.3


def glitch(rng):
    n = int(0.22 * SR); out = np.zeros(n); i = 0
    while i < n:
        L = int(rng.uniform(0.008, 0.03) * SR)
        f = rng.choice([900, 1400, 2200, 3100, 4600])
        tt = np.arange(min(L, n - i)) / SR
        out[i:i + len(tt)] = np.sign(np.sin(2 * np.pi * f * tt)) * rng.uniform(0.15, 0.4)
        i += L + int(rng.uniform(0, 0.01) * SR)
    return lp(out, 7000) * np.linspace(1, 0.3, n)


def pop():
    n = int(0.12 * SR); tt = np.arange(n) / SR
    f = 380 + 900 * np.exp(-tt * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 30)


def swoosh(rng, dur=0.45):
    return whoosh(rng, dur, 900, 6000) * 0.8


# ------------------------------ voiceover ------------------------------
def load_vo(vo, base):
    path = vo["file"] if os.path.isabs(vo["file"]) else os.path.join(base, vo["file"])
    tempo = float(vo.get("tempo", 1.0))
    af = ["highpass=f=70", "acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=2"]
    t = tempo
    while t > 2.0: af.append("atempo=2.0"); t /= 2.0
    while t < 0.5: af.append("atempo=0.5"); t /= 0.5
    if abs(t - 1) > 1e-4: af.append(f"atempo={t:.5f}")
    tmp = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ac", "2", "-ar", str(SR), "-af", ",".join(af), tmp], check=True)
    _, x = wavfile.read(tmp); os.unlink(tmp)
    return x.astype(np.float64) / 32768.0, tempo


def main(cue_path, out_path):
    cues = json.load(open(cue_path))
    base = os.path.dirname(os.path.abspath(cue_path))
    D = float(cues["duration"])
    mood = dict(MOODS.get(cues.get("mood", "warm"), MOODS["warm"]))
    rng = np.random.default_rng(cues.get("seed", 3))
    M = Mix(D)

    # pads
    chords = sorted([c for c in cues.get("chords", []) if float(c["t"]) < D], key=lambda c: float(c["t"]))
    for k, c in enumerate(chords):
        st = float(c["t"]); en = min(D, float(chords[k + 1]["t"])) if k + 1 < len(chords) else D
        notes = [midi(n) for n in (c["notes"].split() if isinstance(c["notes"], str) else c["notes"])]
        seg = pad(notes, en - st + 1.2, mood, rng)
        s = seg * env(len(seg), min(c.get("attack", 1.0), (en - st) * 0.5), 1.2)
        g = c.get("gain", mood["pad"])
        M.add(s, st, g, -0.25); M.add(np.roll(s, 480), st, g, 0.25)

    # pulse
    p = cues.get("pulse")
    if p:
        beat = 60.0 / float(cues.get("bpm", 96)); x = float(p.get("from", 0)); skip = p.get("skip", [])
        def root(t):
            if not chords: return 38.0
            cur = [c for c in chords if float(c["t"]) <= t] or [chords[0]]
            first = cur[-1]["notes"]
            return midi(first.split()[0] if isinstance(first, str) else first[0])
        while x < float(p.get("to", D)):
            if not any(a <= x < b for a, b in skip):
                M.add(thump(), x, p.get("gain", 0.5))
                if p.get("pluck", True):
                    r = root(x)
                    M.add(pluck(r + 24, mood["pl"], 0.35), x + beat / 2, 0.07, 0.3)
                    M.add(pluck(r + 31, mood["pl"], 0.35), x + beat * 0.75, 0.045, -0.3)
            x += beat

    for n in cues.get("piano", []):
        M.add(piano(midi(n["note"]), n.get("dur", 3.0)), n["t"], n.get("gain", mood["pno"]), rng.uniform(-.4, .4))
    for n in cues.get("plucks", []):
        M.add(pluck(midi(n["note"]), mood["pl"], 0.5), n["t"], n.get("gain", 0.12), n.get("pan", rng.uniform(-.5, .5)))

    # sfx
    for s in cues.get("sfx", []):
        t = float(s["t"]); ty = s["type"]; g = s.get("gain")
        if ty == "shimmer": M.add(shimmer(rng), t, g or 0.10, rng.uniform(-.6, .6))
        elif ty in ("whoosh", "swoosh"):
            w = whoosh(rng, s.get("dur", 1.0)) if ty == "whoosh" else swoosh(rng, s.get("dur", 0.45))
            pans = np.linspace(-0.9, 0.9, len(w)) * (1 if s.get("dir", "lr") == "lr" else -1)
            M.add_stereo(w * np.cos((pans + 1) * np.pi / 4), w * np.sin((pans + 1) * np.pi / 4), t - 0.05, g or (0.9 if ty == "whoosh" else 0.5))
        elif ty == "riser": M.add(riser(rng, s.get("dur", 1.2), s.get("f0", 45), s.get("f1", 95)), t, g or 0.18)
        elif ty == "impact":
            M.add(thump(), t, g or 0.5)
            M.add(lp(rng.standard_normal(int(1.5 * SR)), 400) * np.exp(-np.arange(int(1.5 * SR)) / SR * 3) * 0.3, t, g or 0.5)
        elif ty == "chime":
            M.add(chime(midi(s.get("root", "D5"))), t, g or 0.16)
            tt = np.arange(int(2.0 * SR)) / SR
            M.add(np.sin(2 * np.pi * hz(midi(s.get("root", "D5")) - 36) * tt) * np.exp(-tt * 1.4) * np.minimum(1, tt / 0.02), t, 0.3)
        elif ty == "click": M.add(click(rng), t, g or 0.22, rng.uniform(-.2, .2))
        elif ty == "tick": M.add(tick(rng), t, g or 0.16, rng.uniform(-.3, .3))
        elif ty == "glitch": M.add(glitch(rng), t, g or 0.20)
        elif ty == "pop": M.add(pop(), t, g or 0.30, rng.uniform(-.3, .3))
        else: print("unknown sfx type:", ty, file=sys.stderr)

    # reverb
    irn = int(2.6 * SR); it = np.arange(irn) / SR
    irL = lp(rng.standard_normal(irn) * np.exp(-it * 2.4), 6000); irR = lp(rng.standard_normal(irn) * np.exp(-it * 2.4), 6000)
    irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
    wet = cues.get("master", {}).get("reverb", mood["rev"])
    oL = M.L * 0.8 + fftconvolve(M.L, irL)[:M.N] * wet
    oR = M.R * 0.8 + fftconvolve(M.R, irR)[:M.N] * wet
    music = np.stack([oL, oR], 1)
    peak = np.max(np.abs(music)) or 1
    music = music / peak * 0.6 * cues.get("master", {}).get("music_gain", 1.0)

    # voiceover
    V = np.zeros_like(music)
    vo = cues.get("vo")
    if vo:
        x, tempo = load_vo(vo, base)
        PRE, POST = 0.04, 0.10
        for ph in vo["phrases"]:
            a, b = ph["src"]; dst = float(ph["at"])
            i0 = int(max(0, a / tempo - PRE) * SR); i1 = min(len(x), int((b / tempo + POST) * SR))
            seg = x[i0:i1].copy(); n = len(seg)
            if n < 10: continue
            f = int(0.012 * SR); g = min(n // 2, int(0.06 * SR))
            seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-g:] *= np.linspace(1, 0, g)[:, None]
            j = int((dst - PRE) * SR); m = min(n, M.N - j)
            if m > 0: V[j:j + m] += seg[:m] * ph.get("gain", 1.0)
        vr = np.stack([fftconvolve(V[:, 0], irL)[:M.N], fftconvolve(V[:, 1], irR)[:M.N]], 1)
        V = V + vr * 0.08
        V = V / (np.max(np.abs(V)) or 1) * 0.80 * vo.get("gain", 1.0)
        envv = np.convolve(np.abs(V).max(1), np.ones(int(0.03 * SR)) / int(0.03 * SR), "same")
        act = (envv > 0.02).astype(float)
        duck = np.zeros(M.N); a_c = np.exp(-1 / (0.06 * SR)); r_c = np.exp(-1 / (0.35 * SR)); y = 0.0
        for k in range(0, M.N, 48):
            c = a_c if act[k] > y else r_c; y = c * y + (1 - c) * act[k]; duck[k:k + 48] = y
        music = music * (1 - vo.get("duck", 0.55) * duck)[:, None]

    out = music + V
    fade = np.ones(M.N)
    fi = int(cues.get("end", {}).get("fade", 0.9) * SR)
    if fi: fade[-fi:] = np.linspace(1, 0, fi) ** 1.5
    fin = int(0.05 * SR); fade[:fin] = np.linspace(0, 1, fin)
    out = np.tanh(out * fade[:, None] * 1.05)
    out = out / (np.max(np.abs(out)) or 1) * 0.92
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wavfile.write(out_path, SR, (out * 32767).astype(np.int16))
    print(f"wrote {out_path}  ({D:.2f}s, rms {np.sqrt((out ** 2).mean()):.3f})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2])
