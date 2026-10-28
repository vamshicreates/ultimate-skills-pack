"""Final soundtrack from real audio files: voice on top, a music track whose DROP lands on a chosen
film moment, side-chain ducking under the voice, and SFX placed by their ANCHOR (the transient of a
hit, the peak of a whoosh, the end of a riser) so the sound lands on the frame. Two-pass loudness
normalised (default -14 LUFS, true peak -1 dBTP). See SOUND.md.

    python audio/mixdown.py mix.json assets/mix.wav

mix.json:
{
  "duration": 44.95,
  "sfx_lib": "myfilm",                                 # library fetched for this film (audio/source.py kit)
  "voice": "assets/vo/vo.wav",                         # optional; "voice_clean": true = 70 Hz high-pass
  "music": {"file": "assets/music/thunder.mp3", "drop_track": 20.15, "drop_film": 20.8,
            "gain": .55, "pre_gain": 2.4, "duck_db": -10, "fade_in": .6, "fade_out": 1.8},
  "sfx": [
    [t, "assets/sfx/whoosh.mp3", gain, pan],                       # legacy: file START at t, linear gain
    {"t": 3.48, "sfx": "hsl:184", "align": "peak", "gain_db": -8},  # library sound, its PEAK on 3.48 s
    {"t": 7.20, "sfx": "role:impact", "gain_db": -4, "pan": -.2},   # best fit for a role, rotated (no repeats)
    {"t": 9.00, "sfx": "hsl:222", "reverse": true, "align": "end"}, # a reversed boom = a riser ending ON 9.00
    {"t": 9.00, "sfx": "synth:sub", "gain_db": -8},                 # synthesized sub drop under the big hit
    {"t": 4.20, "sfx": "stack:hit"},                                # a designed layered recipe (sfx_lib.py stacks)
    {"t": 6.00, "sfx": "role:cut", "width": .5, "space": .15, "room": "hall", "sat": .2},  # processing per sound
    {"t": 12.1, "sfx": "assets/sfx/x.wav", "align": "onset", "rate": 1.04, "hp": 150, "lp": 9000,
     "fade_in": .02, "fade_out": .3, "max_len": 1.2}
  ],
  "sfx_duck_db": -4,       # SFX dip under speech (0 = off). Never let an SFX mask a stressed syllable.
  "sfx_glue": true, "reverb_gain": 1.0,   # SFX bus compression; overall reverb return level
  # rooms: room .6 s · plate 1.3 s · hall 2.4 s · cathedral 4.8 s (synthetic, decorrelated, damped)
  "lufs": -14, "true_peak": -1,   # delivery loudness (YouTube/IG/TikTok -14; broadcast -23/-24);
                                  # "lufs": null = a stem for an NLE (levels kept, peak-safe only)
  "master": .93            # only used if ffmpeg loudnorm is unavailable (soft-clip fallback)
}
align: start | onset (= hit, transient) | peak (loudest 10 ms) | end (end of the sound body). Library sounds
default to their role/shape anchor (hit->onset, whoosh->peak, riser->end); plain files to "start"
(and get measured on the fly when you ask for onset/peak/end).
Library sounds are level-matched (body RMS -> -18 dBFS) before gain_db, so gain_db means the same for
every file. drop_track: where the drop is in the music file (biggest 50 ms RMS jump, ENGINE §10.2).
Music never sits in the file if it is a copyrighted trending song — add those inside the app at upload.
Writes <out>.cues.txt: every SFX with its anchor, placed start and gain (check it against the cut list).
"""
import json, os, subprocess, sys, tempfile
import numpy as np
from scipy.io import wavfile

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ffbin import ffmpeg
import sfx_lib

FF = ffmpeg()
cfg_path = sys.argv[1]
cfg = json.load(open(cfg_path, encoding="utf-8")); out = sys.argv[2]
CFG_DIR = os.path.dirname(os.path.abspath(cfg_path))
N = int(cfg["duration"] * SR)
sfx_lib.ACTIVE = cfg.get("sfx_lib") or sfx_lib.ACTIVE      # this film's fetched library (audio/source.py)
_cache = {}


def find(p):
    if os.path.exists(p): return p
    q = os.path.join(CFG_DIR, p)
    if os.path.exists(q): return q
    raise SystemExit(f"audio file not found: {p}")


def load(p):
    p = find(p)
    if p in _cache: return _cache[p]
    try:
        import soundfile as sf
        x, sr = sf.read(p, always_2d=True, dtype="float32")
        if sr != SR:
            import scipy.signal as ss
            x = ss.resample_poly(x, SR, sr, axis=0).astype(np.float32)
    except Exception:          # mp3/m4a etc.: decode with ffmpeg
        tmp = tempfile.mktemp(suffix=".wav")
        subprocess.run([FF, "-y", "-v", "error", "-i", p, "-ac", "2", "-ar", str(SR), tmp], check=True)
        x = wavfile.read(tmp)[1].astype(np.float32) / 32768; os.remove(tmp)
    x = x if x.ndim == 2 else x[:, None]
    x = np.repeat(x, 2, 1) if x.shape[1] == 1 else x[:, :2]
    _cache[p] = x
    return x


def place(buf, x, s, g=1.0, pan=0.0):
    """Add x into buf starting at sample s (may be negative: the head is cut)."""
    if s < 0: x = x[-s:]; s = 0
    e = min(len(buf), s + len(x))
    if e > s: buf[s:e] += x[:e - s] * (np.array([1 - max(0, pan), 1 + min(0, pan)]) * g)


def butter(x, kind, hz):
    import scipy.signal as ss
    sos = ss.butter(2, hz, kind, fs=SR, output="sos")
    return ss.sosfilt(sos, x, axis=0).astype(np.float32)


ROOMS = {"room": (.6, 7000), "plate": (1.3, 11000), "hall": (2.4, 6500), "cathedral": (4.8, 5000)}  # RT60 s, damping Hz
_ir = {}


def room_ir(name, predelay=.022):
    """Synthetic stereo reverb impulse: decorrelated noise, exponential RT60 decay, damped highs, unit energy."""
    if name in _ir: return _ir[name]
    rt, damp = ROOMS[name]
    n = int(rt * 1.15 * SR); t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    noise = rng.standard_normal((n, 2)).astype(np.float32)
    noise = butter(noise, "lowpass", damp)
    ir = noise * np.exp(-6.91 * t / rt)[:, None]
    ir[:int(.004 * SR)] *= np.linspace(0, 1, int(.004 * SR))[:, None]
    ir = np.concatenate([np.zeros((int(predelay * SR), 2), np.float32), ir])
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True)) + 1e-9
    _ir[name] = ir.astype(np.float32); return _ir[name]


def widen(x, w):
    """Stereo width 0-1: a short Haas delay on one side (<= 14 ms), mono-safe at w <= .6."""
    d = int(.004 * SR + .010 * SR * w)
    y = x.copy(); dl = np.concatenate([np.zeros((d,), np.float32), x[:-d, 1]]) if d < len(x) else x[:, 1]
    y[:, 1] = (1 - .45 * w) * x[:, 1] + .45 * w * dl
    y[:, 0] = (1 - .2 * w) * x[:, 0] + .2 * w * x[:, 1]
    return y


def saturate(x, amt):
    """Soft tape-style saturation 0-1: adds density and harmonics so hits read on phone speakers."""
    k = 1 + 5 * amt
    return (np.tanh(x * k) / np.tanh(k)).astype(np.float32)


def env_follow(sig, attack=.04, release=.28):
    env = np.convolve(np.abs(sig).max(1), np.ones(960) / 960, "same"); act = (env > .02).astype(np.float32)
    duck = np.zeros(len(sig), np.float32); y = 0.0; ac = np.exp(-1 / (attack * SR)); rc = np.exp(-1 / (release * SR))
    for i in range(0, len(sig), 64):
        c = ac if act[i] > y else rc; y = act[i] + (y - act[i]) * c ** 64; duck[i:i + 64] = y
    return duck


# ------------------------------------------------------------------ voice + music (as before)
voice = np.zeros((N, 2), np.float32)
if cfg.get("voice"):
    v = load(cfg["voice"])[:N] * cfg.get("voice_gain", 1.0)
    if cfg.get("voice_clean"): v = butter(v, "highpass", 70)
    voice[:len(v)] = v
vduck = env_follow(voice) if cfg.get("voice") else np.zeros(N, np.float32)
music = np.zeros((N, 2), np.float32)
M = cfg.get("music")
if M:
    m = load(M["file"]); off = int((M.get("drop_track", 0) - M.get("drop_film", 0)) * SR)
    seg = m[off:off + N] if off >= 0 else np.concatenate([np.zeros((-off, 2), np.float32), m[:N + off]])
    music[:len(seg)] = seg
    pre = int(M.get("drop_film", 0) * SR); music[:pre] *= M.get("pre_gain", 1.0)
    fi = int(M.get("fade_in", .5) * SR); music[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(M.get("fade_out", 1.5) * SR); music[-fo:] *= np.linspace(1, 0, fo)[:, None]
    depth = 1 - 10 ** (M.get("duck_db", -10) / 20)
    music *= (1 - depth * vduck)[:, None] * M.get("gain", .55)

# ------------------------------------------------------------------ SFX, placed by anchor
sfx = np.zeros((N, 2), np.float32)
sends = {}                                                     # reverb send buffers per room
used, report = {}, []
for ev in sfx_lib.expand(cfg.get("sfx", [])):
    if isinstance(ev, list):                                   # legacy [t, file, gain, pan]
        ev = {"t": ev[0], "sfx": ev[1], "gain": ev[2] if len(ev) > 2 else .5, "pan": ev[3] if len(ev) > 3 else 0,
              "align": "start"}
    ref = ev["sfx"]
    s = None if ref.startswith("synth:") else sfx_lib.resolve(ref, used, ev.get("seed", 0))
    if ref.startswith("synth:"):                               # synth:sub = 32-80 Hz pitch-drop boom, felt on phones
        L = float(ref.split(":")[2]) if ref.count(":") > 1 else 1.8
        tt = np.arange(int(L * SR)) / SR; f = 32 + 48 * np.exp(-tt / .12)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / .55); y[:240] *= np.linspace(0, 1, 240)
        x = np.stack([y, y], 1).astype(np.float32) * .5; level = 1.0; default = "start"; name = ref
        anchors = {"start": 0, "onset": 0, "peak": .02, "end": L}
    elif s:
        x = load(s["path"])
        t_begin = s["slice"][0] if "slice" in s else 0.0
        t_end = s["slice"][1] if "slice" in s else len(x) / SR
        x = x[int(t_begin * SR):int(t_end * SR)].copy()
        anchors = {k: s.get(k, 0) - t_begin for k in ("start", "onset", "peak")}
        anchors["end"] = s.get("body_end", s["end"]) - t_begin
        level = 10 ** ((-18 - s["rms_db"]) / 20) if ev.get("norm", True) else 1.0
        default = s.get("anchor") or {"hit": "onset", "riser": "end"}.get(s["shape"], "peak")
        name = f"{s['lib']}:{s['id']} {s['name']}"
    else:
        x = load(ref).copy(); level = 1.0; default = "start"; name = ref; anchors = None
    align = {"hit": "onset", "transient": "onset"}.get(ev.get("align", default), ev.get("align", default))
    if anchors is None and (align != "start" or ev.get("reverse")):   # plain file: measure it now
        st = sfx_lib.analyse(None, x, SR)
        anchors = {"start": st["start"], "onset": st["onset"], "peak": st["peak"], "end": st["body_end"]}
    anchors = anchors or {"start": 0}
    if ev.get("reverse"):                                     # reversed boom/whoosh = riser; anchors mirror
        L = len(x) / SR; x = x[::-1].copy()
        anchors = {"start": 0, "end": L - anchors.get("onset", 0), "peak": L - anchors.get("peak", 0),
                   "onset": L - anchors.get("end", L)}
        if "align" not in ev: align = "end"
    rate = ev.get("rate", 1.0)                                # small variation: 0.94-1.06 (pitch + speed)
    if rate != 1.0:
        import scipy.signal as ss
        x = ss.resample(x, int(len(x) / rate), axis=0).astype(np.float32)
        anchors = {k: v / rate for k, v in anchors.items()}
    if ev.get("hp"): x = butter(x, "highpass", ev["hp"])
    if ev.get("lp"): x = butter(x, "lowpass", ev["lp"])
    a = anchors.get(align, 0.0)
    if ev.get("max_len"):
        cut = int((a + ev["max_len"]) * SR)
        if cut < len(x):
            fo = min(cut, int(.12 * SR)); x = x[:cut]; x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    if ev.get("fade_in"): k = min(len(x), int(ev["fade_in"] * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if ev.get("fade_out"): k = min(len(x), int(ev["fade_out"] * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
    if ev.get("sat"): x = saturate(x / (np.abs(x).max() + 1e-9) * .9, ev["sat"]) * (np.abs(x).max() + 1e-9) / .9
    if ev.get("width"): x = widen(x, min(1.0, ev["width"]))
    g = ev["gain"] if "gain" in ev else 10 ** (ev.get("gain_db", -6) / 20)
    start = int(round((ev["t"] - a) * SR))
    place(sfx, x, start, g * level, ev.get("pan", 0))
    if ev.get("space"):                                        # reverb send (post-fader)
        room = ev.get("room", "hall")
        if room not in ROOMS: raise SystemExit(f"room {room}? use {', '.join(ROOMS)}")
        sends.setdefault(room, np.zeros((N, 2), np.float32))
        place(sends[room], x, start, g * level * ev["space"], ev.get("pan", 0))
    report.append(f"{ev['t']:8.3f}s  {align:<5} anchor {a:5.3f}s -> starts {start / SR:8.3f}s  "
                  f"{20 * np.log10(max(g * level, 1e-6)):+6.1f} dB  {name}" + (f"  ({ev['note']})" if ev.get("note") else ""))

from scipy.signal import fftconvolve
for room, buf in sends.items():                                # one convolution per room; tail kept clean of mud
    if not buf.any(): continue
    wet = np.stack([fftconvolve(buf[:, c], room_ir(room)[:, c])[:N] for c in (0, 1)], 1).astype(np.float32)
    sfx += butter(wet, "highpass", 180) * cfg.get("reverb_gain", 1.0)
if cfg.get("sfx_glue", True) and sfx.any():                   # bus glue: gentle 3:1 compression, 8 ms / 140 ms
    lvl = np.sqrt(np.convolve((sfx ** 2).mean(1), np.ones(480) / 480, "same")) + 1e-9
    thr = 10 ** (-20 / 20) * np.abs(sfx).max()
    gr = np.where(lvl > thr, (thr / lvl) ** (1 - 1 / 3), 1.0).astype(np.float32)
    y = 1.0; a_c, r_c = np.exp(-1 / (.008 * SR)), np.exp(-1 / (.14 * SR)); sm = np.empty_like(gr)
    for i in range(0, N, 32):
        c = a_c if gr[i] < y else r_c; y = gr[i] + (y - gr[i]) * c ** 32; sm[i:i + 32] = y
    sfx *= sm[:, None]

duck_db = cfg.get("sfx_duck_db", -4 if cfg.get("voice") else 0)
if duck_db:
    sfx *= (1 - (1 - 10 ** (duck_db / 20)) * vduck)[:, None]

# ------------------------------------------------------------------ master
mix = voice + music + sfx * cfg.get("sfx_gain", .8)
lufs, tp = cfg.get("lufs", -14), cfg.get("true_peak", -1)
pk = max(1e-6, np.abs(mix).max())
tmp = out + ".pre.wav"
wavfile.write(tmp, SR, (mix / max(pk, 1.0) * 32767 * .98).astype(np.int16))   # headroom-safe pre-master
try:
    if lufs is None:                                            # a stem for an NLE: keep relative levels
        raise StopIteration
    r = subprocess.run([FF, "-hide_banner", "-i", tmp, "-af", f"loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    j = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    af = (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run([FF, "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le", out], check=True)
    note = f"loudness {j['input_i']} -> {lufs} LUFS, true peak <= {tp} dBTP"
except StopIteration:
    os.replace(tmp, out); open(tmp, "w").close(); note = "stem: not loudness-normalised (lufs: null)"
except Exception as e:                                          # fallback: the old soft-clip master
    mix = np.tanh(mix / pk * 1.25) * cfg.get("master", .93)
    wavfile.write(out, SR, (mix * 32767).astype(np.int16)); note = f"loudnorm failed ({e}); soft-clipped"
os.remove(tmp)
with open(out + ".cues.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")
print("wrote", out, round(N / SR, 2), "s,", len(report), "sfx;", note, "\ncue report:", out + ".cues.txt")
