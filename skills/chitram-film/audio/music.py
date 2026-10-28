"""music.py: understand a music track and cut it to the picture (MUSIC.md).

  python audio/music.py analyse TRACK [--out track.music.json]        tempo, beats, bars, phrases, sections,
                                                                      drop, accents, key/mode, energy -> json + png
  python audio/music.py fit TRACK --duration 30 [--drop-at 12.4 [--drop 1]] [--start 31.2 | --skip-intro]
                         [--ending natural|fade|hard] --out assets/music_fit.wav
        a music EDIT exactly --duration long: starts on a downbeat, the drop lands on --drop-at (film
        time), splices only on downbeats (phrase-aligned when possible, 40 ms equal-power crossfade),
        loops a section if the track is too short, ends on the track's real ending. Writes
        music_fit.wav + music_fit.json (film-time grid) + music_fit.beats.js (window.MUSIC for the engine)
  python audio/music.py cuts music_fit.json [--every beat|bar|2bar|phrase] [--min 0.6] [--from 0 --to 30]
        suggested cut / effect times on the grid, strongest first-class (drop > phrase > bar > beat)
  python audio/music.py sheet track.music.json [--out sheet.png]     see the music: energy, beats, bars,
                                                                      sections, drop (you can't listen: look)

Method (no librosa needed): 22.05 kHz mono, log-spectral flux onset envelope (11.6 ms hop), tempo by
autocorrelation with a log-normal prior around 110 BPM (octave errors checked), beats by dynamic
programming (Ellis 2007), downbeats = the 4/4 phase whose beats carry the most low-band (kick) flux and
harmonic change, sections by a bar-level novelty curve snapped to 4-bar phrases, drop = the largest
energy jump into a high-energy section, key by Krumhansl-Schmuckler chroma profiles.
Assumes 4/4 (nearly all Reels / trailer / pop music). Always LOOK at the sheet before trusting it.
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ffbin import ffmpeg

SR = 22050
HOP = 256
FPS = SR / HOP          # onset frames per second (86.13)


def opt(a, name, default=None, cast=str):
    return cast(a[a.index(name) + 1]) if name in a and a.index(name) + 1 < len(a) else default


def decode(path, sr=SR, ch=1):
    r = subprocess.run([ffmpeg(), "-v", "error", "-i", path, "-vn", "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.float32)
    return x.reshape(-1, ch) if ch > 1 else x


# ------------------------------------------------------------------ features
def spectra(x, n_fft=2048):
    pad = np.concatenate([np.zeros(n_fft // 2, np.float32), x, np.zeros(n_fft // 2, np.float32)])
    n = 1 + (len(pad) - n_fft) // HOP
    idx = np.arange(n_fft)[None, :] + HOP * np.arange(n)[:, None]
    win = np.hanning(n_fft).astype(np.float32)
    X = np.abs(np.fft.rfft(pad[idx] * win, axis=1)).astype(np.float32)
    f = np.fft.rfftfreq(n_fft, 1 / SR)
    return X, f


def onset_envelopes(X, f):
    L = np.log1p(100 * X)
    d = np.maximum(0, np.diff(L, axis=0, prepend=L[:1]))
    full = d.sum(1)
    lp = (X[:, f < 150] ** 2).sum(1)                                # LINEAR sub power: kicks, not hats
    low = np.maximum(0, np.diff(np.sqrt(lp), prepend=np.sqrt(lp[:1])))
    full = full - np.convolve(full, np.ones(16) / 16, "same")          # remove slow trend: keep transients
    full = np.maximum(0, full); full /= full.std() + 1e-9
    low /= low.std() + 1e-9
    return full, low


def chroma(X, f):
    m = (f > 60) & (f < 4200)
    pitch = np.round(12 * np.log2(f[m] / 440.0) + 69).astype(int) % 12
    C = np.zeros((X.shape[0], 12), np.float32)
    for k in range(12):
        C[:, k] = X[:, m][:, pitch == k].sum(1)
    return C / (C.sum(1, keepdims=True) + 1e-9)


# ------------------------------------------------------------------ tempo + beats
def tempo(env):
    e = env - env.mean()
    n = len(e); size = 1 << int(np.ceil(np.log2(2 * n)))
    ac = np.fft.irfft(np.abs(np.fft.rfft(e, size)) ** 2)[:n]
    lags = np.arange(int(FPS * 60 / 200), int(FPS * 60 / 55))
    bpm = 60 * FPS / lags
    prior = np.exp(-0.5 * (np.log2(bpm / 110) / 0.9) ** 2)
    score = ac[lags] / (ac[0] + 1e-9) * prior
    k = int(np.argmax(score)); l = lags[k]
    if 0 < k < len(lags) - 1:                                  # parabolic refinement of the lag
        y0, y1, y2 = score[k - 1], score[k], score[k + 1]; den = y0 - 2 * y1 + y2
        l = l + (0.5 * (y0 - y2) / den if den else 0)
    return 60 * FPS / l


def track_beats(env, bpm, tight=100.0):
    period = 60 * FPS / bpm
    n = len(env)
    local = np.convolve(env, np.exp(-0.5 * ((np.arange(-int(period), int(period) + 1)) / (period / 32)) ** 2), "same")
    C = local.copy(); back = -np.ones(n, int)
    lo, hi = int(round(period / 2)), int(round(2 * period))
    w = np.arange(lo, hi + 1)
    pen = -tight * np.log(w / period) ** 2
    for t in range(hi, n):
        cand = C[t - w] + pen
        j = int(np.argmax(cand)); C[t] = local[t] + cand[j]; back[t] = t - w[j]
    tail = C[max(0, n - int(period)):]
    t = n - len(tail) + int(np.argmax(tail))
    beats = []
    while t >= 0:
        beats.append(t); t = back[t]
    beats = np.array(beats[::-1], float)
    # snap each beat to the strongest onset within +-25 ms (sub-frame accuracy)
    r = int(.025 * FPS); out = []
    for b in beats.astype(int):
        a0, a1 = max(0, b - r), min(n, b + r + 1)
        k = a0 + int(np.argmax(env[a0:a1])) if env[a0:a1].max() > env[b] * 1.2 else b
        out.append(k)
    return np.array(out) / FPS


def downbeat_phase(beats, low, C):
    idx = np.clip((beats * FPS).astype(int), 0, len(low) - 1)
    kick = np.array([low[max(0, i - 2):i + 3].max() for i in idx])
    ch = np.r_[0, np.abs(np.diff(C[idx], axis=0)).sum(1)]          # harmonic change arrives on the 1
    sc = [kick[p::4].mean() + 0.8 * ch[p::4].mean() for p in range(4)]
    return int(np.argmax(sc))


# ------------------------------------------------------------------ structure
def bar_features(x, beats, downs, X, f, C):
    feats = []
    for i in range(len(downs) - 1):
        a, b = downs[i], downs[i + 1]
        seg = x[int(a * SR):int(b * SR)]
        fa, fb = int(a * FPS), int(b * FPS)
        S = X[fa:fb]
        rms = 10 * np.log10((seg ** 2).mean() + 1e-12)
        low = 10 * np.log10((S[:, f < 150] ** 2).sum(1).mean() + 1e-12)
        high = 10 * np.log10((S[:, f > 4000] ** 2).sum(1).mean() + 1e-12)
        cen = float((S.mean(0) * f).sum() / (S.mean(0).sum() + 1e-9))
        feats.append([rms, low, high, cen / 1000, *C[fa:fb].mean(0) * 4])
    return np.array(feats)


def sections(F, downs, first_phrase=0, min_bars=4):
    nb = len(F)
    if nb < 8:
        return [(0, nb)]
    Z = (F - F.mean(0)) / (F.std(0) + 1e-9)
    nov = np.zeros(nb)
    for i in range(2, nb - 1):
        k = min(4, i, nb - i)
        nov[i] = np.linalg.norm(Z[i:i + k].mean(0) - Z[i - k:i].mean(0))
    nov[[(i - first_phrase) % 4 == 0 for i in range(nb)]] *= 1.35   # phrase-aligned boundaries are likelier
    cuts = [0]
    for i in np.argsort(-nov):
        if nov[i] < np.percentile(nov, 70) or i < min_bars or i > nb - 2: continue
        if all(abs(i - c) >= min_bars for c in cuts): cuts.append(int(i))
    cuts = sorted(cuts) + [nb]
    return [(cuts[k], cuts[k + 1]) for k in range(len(cuts) - 1)]


KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def key_of(C):
    v = C.mean(0); best = (-2, "", "")
    for k in range(12):
        for prof, mode in ((MAJ, "major"), (MIN, "minor")):
            r = np.corrcoef(v, np.roll(prof, k))[0, 1]
            if r > best[0]: best = (r, KEYS[k], mode)
    return best[1], best[2], round(float(best[0]), 2)


def analyse(path):
    x = decode(path)
    dur = len(x) / SR
    X, f = spectra(x)
    Xo, fo = spectra(x, 1024)                                   # short window: transients not smeared early
    env, low = onset_envelopes(Xo, fo)
    bpm = tempo(env)
    beats = track_beats(env, bpm)
    # rigid grid for fixed-tempo music (nearly all Reels/trailer/pop): fit the tempo line, then choose the
    # phase that best explains kick + onset energy over the WHOLE track (hats on the "and" can't capture it)
    k = np.arange(len(beats))
    slope, icpt = np.polyfit(k, beats, 1) if len(beats) > 8 else (60 / bpm, beats[0] if len(beats) else 0)
    resid = beats - (icpt + slope * k) if len(beats) > 8 else np.zeros(1)
    live = len(beats) > 8 and np.std(resid) > .035             # drifting tempo: keep the tracked beats
    if not live:
        score_env = env + 2.5 * low
        best, best_ph = -1, 0.0
        for ph in np.arange(0, slope, .004):
            g = np.arange(ph, len(env) / FPS, slope)
            idx = np.clip(np.round(g * FPS).astype(int), 0, len(env) - 1)
            sc = sum(score_env[np.clip(idx + d, 0, len(env) - 1)] for d in (-1, 0, 1)).mean()
            if sc > best: best, best_ph = sc, ph
        beats = np.arange(best_ph, len(x) / SR - .05, slope)
    bpm = 60 / slope if len(beats) > 8 else bpm
    C = chroma(X, f)
    ph = downbeat_phase(beats, low, C)
    downs = beats[ph::4]
    F = bar_features(x, beats, downs, X, f, C) if len(downs) > 2 else np.zeros((0, 16))
    secs = sections(F, downs) if len(F) else []
    rms_bar = F[:, 0] if len(F) else np.array([])
    if len(rms_bar):                                            # graded on this track's own dynamic range
        mx, mn = np.percentile(rms_bar, 95), np.percentile(rms_bar, 5); rg = max(3.0, mx - mn)
        hi_e, lo_e = mx - .3 * rg, mn + .3 * rg
    else:
        lo_e = hi_e = 0
    S = []
    for k, (a, b) in enumerate(secs):
        e = float(F[a:b, 0].mean())
        lvl = "high" if e >= hi_e else "low" if e <= lo_e else "mid"
        S.append({"t0": round(float(downs[a]), 3), "t1": round(float(downs[min(b, len(downs) - 1)]), 3),
                  "bars": [int(a), int(b)], "energy_db": round(e, 1), "level": lvl})
    for k, s in enumerate(S):                                   # musical labels from level + position
        prev = S[k - 1]["level"] if k else None
        nxt = S[k + 1]["level"] if k + 1 < len(S) else None
        s["label"] = ("intro" if k == 0 and s["level"] != "high" else
                      "outro" if k == len(S) - 1 and s["level"] != "high" else
                      "drop/chorus" if s["level"] == "high" else
                      "build" if nxt == "high" and s["level"] in ("mid", "low") else
                      "break" if prev == "high" and s["level"] == "low" else "verse")
    drop = None; best = 0; drops = []
    for k in range(1, len(S)):
        jump = S[k]["energy_db"] - S[k - 1]["energy_db"]
        if S[k]["level"] == "high" and jump > 2.5: drops.append({"t": S[k]["t0"], "jump_db": round(jump, 1)})
        if S[k]["level"] == "high" and jump > best: best, drop = jump, S[k]["t0"]
    # accents: the strongest transients (for flashes, hits, speed-ramp landings)
    pk = [i for i in range(1, len(env) - 1) if env[i] > env[i - 1] and env[i] >= env[i + 1] and env[i] > 3.0]
    pk = sorted(pk, key=lambda i: -env[i])[:40]
    accents = sorted(round(i / FPS, 3) for i in pk)
    hop50 = int(.05 * SR)                                      # where the music audibly ends (ring-out included)
    r50 = 20 * np.log10(np.sqrt(np.add.reduceat(x ** 2, np.arange(0, len(x), hop50)) / hop50) + 1e-9)
    alive = np.flatnonzero(r50 > r50.max() - 35)
    music_end = float((alive[-1] + 1) * .05) if len(alive) else dur
    key, mode, kconf = key_of(C)
    cen = float((X.mean(0) * f).sum() / (X.mean(0).sum() + 1e-9))
    loud = 10 * np.log10((x ** 2).mean() + 1e-12)
    res = {"file": os.path.abspath(path), "duration": round(dur, 3), "bpm": round(float(bpm), 2),
           "beats": [round(float(b), 3) for b in beats], "downbeats": [round(float(b), 3) for b in downs],
           "phrases": [round(float(b), 3) for b in downs[::4]], "sections": S, "drop": drop, "drops": drops,
           "drop_jump_db": round(best, 1), "music_end": round(music_end, 3), "accents": accents, "key": key, "mode": mode, "key_conf": kconf,
           "brightness_hz": int(cen), "rms_db": round(float(loud), 1),
           "energy_curve": [round(float(v), 1) for v in rms_bar],
           "tempo_class": ("slow" if bpm < 80 else "medium-slow" if bpm < 95 else "medium" if bpm < 110 else
                           "medium-fast" if bpm < 128 else "fast")}
    return res


# ------------------------------------------------------------------ the edit (fit to picture)
def fit(a):
    path = a[0]; D = opt(a, "--duration", None, float)
    if not D: raise SystemExit("--duration is required")
    A = analyse(path)
    out = opt(a, "--out", os.path.splitext(path)[0] + "_fit.wav")
    ending = opt(a, "--ending", "natural")
    drop_at = opt(a, "--drop-at", None, float)
    y = decode(path, 48000, 2); TR = len(y) / 48000
    downs = np.array(A["downbeats"]); phrases = np.array(A["phrases"])
    if len(downs) < 4: raise SystemExit("could not find bars in this track (no steady beat?)")
    bar = float(np.median(np.diff(downs)))
    # 1) where the film's t=0 sits in the track
    use_drop = A["drop"]
    if opt(a, "--drop") is not None and A["drops"]:             # --drop 1 = the first drop, 2 = the second ...
        use_drop = A["drops"][min(len(A["drops"]), opt(a, "--drop", 1, int)) - 1]["t"]
    A["drop"] = use_drop
    if drop_at is not None and use_drop is not None:
        start = use_drop - drop_at
    elif opt(a, "--start"):
        start = downs[np.argmin(np.abs(downs - opt(a, "--start", 0, float)))]
    elif "--skip-intro" in a and len(A["sections"]) > 1:
        start = A["sections"][1]["t0"]
    else:
        start = downs[0] if downs[0] < 2 * bar else 0.0
    lead = max(0.0, -start); start = max(0.0, start)           # film opens before the track can: silence lead-in
    # 2) the ending block: the last 2 bars + the natural ring-out (or nothing for fade/hard endings)
    if ending == "natural":                                     # the last 2 audible bars + their ring-out
        mend = A.get("music_end", TR)
        live = downs[downs <= mend - .25 * bar]
        e0 = live[-3] if len(live) >= 3 else live[0]
        E = (float(e0), min(TR, mend + 1.0))
    else:
        E = None
    need = D - lead
    segs = []                                                   # [(track_t0, track_t1)] played in order
    if E:
        body_need = need - (E[1] - E[0])
        if body_need <= 0:                                      # very short film: just the ending tail
            segs = [(max(0.0, E[1] - need), E[1])]
        else:
            t = start; got = 0.0
            while got < body_need - 1e-3:
                avail_end = E[0]                                # play forward until the ending block
                cand = downs[(downs > t + .5 * bar) & (downs <= avail_end + 1e-3)]
                if not len(cand):
                    raise SystemExit("track too short to fit; try --ending fade")
                target = t + (body_need - got)
                if target <= cand[-1] + .5 * bar:               # finish this run on the downbeat nearest the target
                    pick = cand[np.argmin(np.abs(cand - target))]
                    pick = phrases[np.argmin(np.abs(phrases - target))] if (np.abs(phrases - target).min() < .5 * bar) else pick
                    segs.append((t, float(pick))); got += pick - t; break
                segs.append((t, float(cand[-1]))); got += cand[-1] - t
                loop = [s for s in A["sections"] if s["level"] in ("high", "mid") and s["t1"] - s["t0"] >= 4 * bar]
                t = (loop[-1] if loop else A["sections"][0])["t0"]   # loop back to a full section, on its downbeat
            segs.append(E)
    else:
        segs = [(start, min(TR, start + need))]
    # 3) render with 40 ms equal-power crossfades at each splice (always on a downbeat)
    xf = int(.04 * 48000)
    buf = np.zeros((int(round(lead * 48000)), 2), np.float32)
    film_map = []; ft = lead
    for k, (t0, t1) in enumerate(segs):
        seg = y[int(t0 * 48000):int(t1 * 48000)].copy()
        film_map.append((ft, t0, t1)); ft += t1 - t0
        if k and len(buf) > xf and len(seg) > xf:
            fo = np.cos(np.linspace(0, np.pi / 2, xf))[:, None]; fi = np.sin(np.linspace(0, np.pi / 2, xf))[:, None]
            buf[-xf:] = buf[-xf:] * fo + seg[:xf] * fi; seg = seg[xf:]
        buf = np.concatenate([buf, seg])
    N = int(round(D * 48000))
    if len(buf) >= N:
        fo = int(.35 * 48000) if ending != "hard" else int(.012 * 48000)
        buf = buf[:N]
        if ending == "fade": fo = int(min(3.0, D / 4) * 48000)
        buf[-fo:] *= np.linspace(1, 0, fo)[:, None] ** (2 if ending == "fade" else 1)
    else:
        buf = np.concatenate([buf, np.zeros((N - len(buf), 2), np.float32)])
    import soundfile as sf
    sf.write(out, buf, 48000, subtype="PCM_24")

    def to_film(times):
        o = []
        for t in times:
            for f0, t0, t1 in film_map:
                if t0 - 1e-3 <= t < t1 - 1e-3 and 0 <= f0 + t - t0 < D: o.append(round(f0 + t - t0, 3))
        return sorted(set(o))
    rep = {"source": A["file"], "duration": D, "bpm": A["bpm"], "key": f"{A['key']} {A['mode']}",
           "segments": [{"film": round(f0, 3), "track": [round(t0, 3), round(t1, 3)]} for f0, t0, t1 in film_map],
           "beats": to_film(A["beats"]), "downbeats": to_film(A["downbeats"]), "phrases": to_film(A["phrases"]),
           "accents": to_film(A["accents"]), "drop": (to_film([A["drop"]]) or [None])[0] if A["drop"] else None,
           "sections": [], "ending": ending, "lead_silence": round(lead, 3)}
    for s in A["sections"]:
        for f0, t0, t1 in film_map:
            a0, a1 = max(s["t0"], t0), min(s["t1"], t1)
            if a1 - a0 > .2:
                rep["sections"].append({"t0": round(f0 + a0 - t0, 3), "t1": round(f0 + a1 - t0, 3),
                                        "label": s["label"], "level": s["level"]})
    base = os.path.splitext(out)[0]
    json.dump(rep, open(base + ".json", "w"), indent=1)
    with open(base + ".beats.js", "w") as fjs:
        fjs.write("window.MUSIC = " + json.dumps({k: rep[k] for k in ("bpm", "beats", "downbeats", "phrases", "accents",
                                                                       "drop", "sections", "duration")}) + ";\n")
    print(f"fit -> {out}  {D:.2f}s  {A['bpm']} BPM {A['key']} {A['mode']}  splices at film "
          f"{[round(f0, 2) for f0, _, _ in film_map[1:]]}  drop at film {rep['drop']}  ending={ending}")
    print(f"     grid -> {base}.json, {base}.beats.js  ({len(rep['beats'])} beats, {len(rep['downbeats'])} bars)")
    return rep


def cuts(a):
    R = json.load(open(a[0]))
    every = opt(a, "--every", "bar"); mn = opt(a, "--min", .6, float)
    t0, t1 = opt(a, "--from", 0, float), opt(a, "--to", R.get("duration", 1e9), float)
    grid = {"beat": R["beats"], "bar": R["downbeats"], "2bar": R["downbeats"][::2], "phrase": R["phrases"]}[every]
    rank = lambda t: ("DROP" if R.get("drop") and abs(t - R["drop"]) < .02 else
                      "phrase" if any(abs(t - p) < .02 for p in R["phrases"]) else
                      "bar" if any(abs(t - p) < .02 for p in R["downbeats"]) else "beat")
    last = -1e9
    for t in grid:
        if t0 <= t <= t1 and t - last >= mn:
            print(f"{t:8.3f}  {rank(t)}"); last = t


def sheet(a):
    from PIL import Image, ImageDraw
    R = json.load(open(a[0])) if a[0].endswith(".json") else analyse(a[0])
    out = opt(a, "--out", os.path.splitext(a[0])[0] + "_music.png")
    D = R.get("duration"); W, H = 1600, 260
    x = decode(R["file"] if "file" in R else R["source"])
    if "segments" in R:                                         # a fit report: draw the fitted wav instead
        import soundfile as sf
        fw = os.path.splitext(a[0])[0] + ".wav"
        if os.path.exists(fw): x = sf.read(fw)[0].mean(1)
    img = Image.new("RGB", (W, H), (16, 16, 20)); d = ImageDraw.Draw(img)
    cols = {"high": (220, 70, 70), "mid": (200, 150, 60), "low": (70, 110, 200)}
    for s in R.get("sections", []):
        x0, x1 = int(s["t0"] / D * W), int(s["t1"] / D * W)
        d.rectangle([x0, 30, x1, 50], fill=cols.get(s["level"], (90, 90, 90)))
        d.text((x0 + 3, 34), s["label"], fill=(255, 255, 255))
    hop = max(1, len(x) // W)
    rms = np.array([np.sqrt((x[i * hop:(i + 1) * hop] ** 2).mean() + 1e-12) for i in range(W)])
    db = 20 * np.log10(rms + 1e-9); top = np.percentile(db, 99)
    for i in range(W):                                        # RMS in dB over a 40 dB window: dynamics visible
        h = int(np.clip((db[i] - top + 40) / 40, 0, 1) * 80)
        d.line([(i, 150 - h), (i, 150 + h)], fill=(120, 170, 230))
    for b in R["beats"]: d.line([(int(b / D * W), 232), (int(b / D * W), 240)], fill=(150, 150, 150))
    for b in R["downbeats"]: d.line([(int(b / D * W), 226), (int(b / D * W), 246)], fill=(255, 255, 255))
    for b in R["phrases"]: d.line([(int(b / D * W), 56), (int(b / D * W), 226)], fill=(90, 90, 110))
    if R.get("drop") is not None:
        xd = int(R["drop"] / D * W); d.line([(xd, 26), (xd, 250)], fill=(255, 60, 60), width=3)
        d.text((xd + 4, 60), f"DROP {R['drop']:.2f}s", fill=(255, 120, 120))
    step = 5 if D > 40 else 2
    for k in range(0, int(D) + 1, step): d.text((int(k / D * W) + 2, 4), f"{k}s", fill=(180, 180, 180))
    d.text((W - 360, 4), f"{R['bpm']} BPM  {R.get('key', '')} {R.get('mode', '')}  {D:.1f}s", fill=(255, 255, 255))
    img.save(out); print("->", out, "(white ticks = bars, grey = beats, vertical = 4-bar phrases, red = drop)")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("analyse", "analyze", "fit", "cuts", "sheet"):
        print(__doc__); sys.exit(1)
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd in ("analyse", "analyze"):
        R = analyse(a[0])
        out = opt(a, "--out", os.path.splitext(a[0])[0] + ".music.json")
        json.dump(R, open(out, "w"), indent=1)
        print(f"{os.path.basename(a[0])}: {R['duration']}s  {R['bpm']} BPM ({R['tempo_class']})  {R['key']} {R['mode']} "
              f"(conf {R['key_conf']})  brightness {R['brightness_hz']} Hz  drop {R['drop']} (+{R['drop_jump_db']} dB)"
              f"  all drops {[d['t'] for d in R['drops']]}")
        for s in R["sections"]:
            print(f"   {s['t0']:7.2f}-{s['t1']:7.2f}  bars {s['bars'][0]:3d}-{s['bars'][1]:3d}  {s['level']:<4} {s['energy_db']:6.1f} dB  {s['label']}")
        print("->", out); sheet([out])
    elif cmd == "fit":
        r = fit(a); sheet([os.path.splitext(opt(a, "--out", os.path.splitext(a[0])[0] + "_fit.wav"))[0] + ".json"])
    elif cmd == "cuts":
        cuts(a)
    else:
        sheet(a)


if __name__ == "__main__":
    main()
