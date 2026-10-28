"""SFX library manager: index any folder of sound effects, measure every file, and pick the right
sound for each edit event. See SOUND.md.

    python audio/sfx_lib.py index  "<folder>" --name hsl [--import]   measure + classify -> index
    python audio/sfx_lib.py list   [--lib hsl] [--cat whoosh]          one line per sound
    python audio/sfx_lib.py search "deep impact" [--cat impact] [--max 1.5] [--n 10]
    python audio/sfx_lib.py roles                                      the edit roles and their best fits
    python audio/sfx_lib.py stacks                                     designed cinematic layer recipes (stack:hit ...)
    python audio/sfx_lib.py pick   cut [--n 5] [--seed 3]               candidates for one role
    python audio/sfx_lib.py spot   events.json mix.json [--lib film]    events -> SFX cue list for mixdown.py
    python audio/sfx_lib.py sheet  hsl:137 hsl:105 ... [--out sheet.png]  draw envelopes (you can't listen: look)
    python audio/sfx_lib.py spec   mix.wav [--marks 3.2,7.5] [--out spec.png]   see a mix: hits, tails, sub, mud
    python audio/sfx_lib.py catalog [--out SFX-CATALOG.md]              markdown catalog of all libraries

Why measure: library files are often padded (a 0.4 s whoosh inside a 10 s file), and every sound has
its own anchor. A hit's TRANSIENT (onset) must land on the cut frame; a whoosh's PEAK must land on
the cut frame; a riser's END must land on the hit. The index stores, per file, in seconds from the
file start:
  start / end   audible region (above peak-45 dB)       dur    = end - start
  onset         transient arrival (peak-12 dB crossing)  peak   = loudest 10 ms
  shape         hit (fast attack) | swell (peak mid) | riser (peak at end) | bed (flat, long)
  rms_db / peak_db, centroid (Hz, bright vs dark), sub (share of energy < 120 Hz)

Registry: audio/libraries.json maps a short name (e.g. "hsl") to the folder + index. References in
cue files are "hsl:137" (the number in the file name) or "hsl:<file name>" or "role:<role>".
"""
import json, os, re, sys, glob, random

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "libraries.json")
AUDIO_EXT = (".wav", ".aif", ".aiff", ".flac", ".mp3", ".ogg", ".m4a")

# ------------------------------------------------------------------ classification (name first, then audio)
CATS = [  # order matters: first match wins
    ("riser",   r"reverse|riser|rise|swell|build|uplift|suck|tension"),
    ("glitch",  r"glitch|stutter|distort.*beep|data.?beep|bleep"),
    ("ui",      r"tech|interface|button|beep|digital|error|alarm|computer|notification"),
    ("whoosh",  r"whoosh|swoosh|swish|whip|swipe|pass.?by|fly.?by|woosh"),
    ("boom",    r"boom|explod|detonat|implo|thunder|bomb|braam|horn hit"),
    ("impact",  r"impact|hit|slam|thud|punch|downer|kick|stamp|crash|smash|808|bass drop|sub drop"),
    ("pop",     r"pop|bubble|pluck|blip"),
    ("click",   r"click|switch|latch|slider|tap|shutter|flick|snap|hang.?up"),
    ("chime",   r"bell|ding|chime|shimmer|gleam|sparkle|twinkle|glass"),
    ("tonal",   r"tone|pad|cello|note|drone|screech"),
    ("musical", r"snare|timpani|drum|roll|trombone|musical|cymbal"),
    ("foley",   r"page|flip|paper|zip|door|lighter|water|splash|drop|flag|fabric|board|scrape|"
                r"sizzle|blowtorch|weld|sword|gun|car|motor|chopper|helicop|lifter|heartbeat|breath|exhale"),
    ("animal",  r"dog|bark|howl|horse|neigh|gallop|trot|bird|seagull|squawk|elephant|monster|growl|roar|flap|flutter"),
    ("crowd",   r"crowd|cheer|group|audience|applause"),
]

NOVELTY = (r"dog|bark|howl|horse|gallop|trot|elephant|roar|motorbike|car rev|horn|helicop|door|zip|water|"
           r"splash|bubble|underwater|flame|fireball|snake|toothpaste|cigar|alien|robot|man eater|race track")
plain = lambda s: "character" not in s.get("tags", [])

# role -> (categories, extra filter, default anchor, what it is for)
ROLES = {
    "cut":        (["whoosh"], lambda s: plain(s) and .12 <= s["dur"] <= .7 and s["shape"] != "multi", "peak",
                   "quick whoosh on a hard cut / blur cut / world switch; peak ON the cut frame"),
    "whip":       (["whoosh"], lambda s: plain(s) and .25 <= s["dur"] <= 1.2 and s["shape"] in ("swell", "riser"), "peak",
                   "whip pan / push-through / zoom transition; peak on the swap frame"),
    "swoosh":     (["whoosh"], lambda s: plain(s) and s["dur"] <= .6 and s["sub"] < .6, "peak",
                   "soft, light swoosh for text / card / label sliding in"),
    "transition": (["whoosh"], lambda s: plain(s) and .9 <= s["dur"] <= 3.5 and s["sub"] > .3, "peak",
                   "heavy showpiece transition (1 per film)"),
    "riser":      (["riser", "whoosh"], lambda s: plain(s) and (s["cat"] == "riser" or s["shape"] == "riser"), "end",
                   "build into a reveal; its END lands on the hit"),
    "impact":     (["impact", "boom"], lambda s: s["rise"] <= .2 and s["dur"] <= 2.5 and "heart" not in s["name"].lower(), "onset",
                   "hit on a key word, title slam, strike-through"),
    "boom":       (["boom", "impact"], lambda s: s["dur"] >= .4 and s["sub"] > .3, "onset",
                   "cinematic boom for the biggest reveal / logo / trailer hit"),
    "sub":        (["impact", "boom"], lambda s: s["sub"] > .85 and s["rise"] <= .2, "onset",
                   "sub drop under a cut to black or a big reveal (felt, not heard)"),
    "pop":        (["pop", "click"], lambda s: s["dur"] <= .5, "onset",
                   "label / sticker / card / bubble pop-in"),
    "click":      (["click"], lambda s: s["dur"] <= .6, "onset",
                   "UI tap, cursor click, toggle, checkbox tick"),
    "ui":         (["ui"], lambda s: True, "onset",
                   "screen / data / interface beeps, typing feel"),
    "glitch":     (["glitch"], lambda s: True, "onset",
                   "glitch transition, error, digital disruption"),
    "ding":       (["chime"], lambda s: True, "onset",
                   "logo chime, success tick, 'idea' moment, sparkle on a magic reveal"),
    "shutter":    (["click"], lambda s: "shutter" in s["name"].lower(), "onset",
                   "photo / freeze frame / screenshot"),
    "page":       (["foley"], lambda s: "page" in s["name"].lower() or "paper" in s["name"].lower(), "onset",
                   "page turn, card flip, collage paper"),
    "tension":    (["musical"], lambda s: re.search(r"snare|timpani", s["name"].lower()), "end",
                   "snare / timpani roll building to a reveal; END on the hit"),
    "tonal":      (["tonal", "impact", "chime"], lambda s: re.search(r"tonal|pad|cello|note|tone|gleam", s["name"].lower()), "onset",
                   "tonal hit / pad swell for an emotional beat"),
    "heartbeat":  (["foley", "impact"], lambda s: "heart" in s["name"].lower(), "onset", "tension pulse"),
    "fail":       (["musical"], lambda s: "trombone" in s["name"].lower(), "start", "comedic fail (rare)"),
    "breath":     (["foley"], lambda s: "breath" in s["name"].lower() or "exhale" in s["name"].lower(), "start",
                   "human breath, relief, calm"),
}


PREFER = {r: ("hit",) for r in ("impact", "boom", "sub", "pop", "click", "ding", "ui", "shutter", "heartbeat")}
PREFER.update({r: ("swell",) for r in ("cut", "whip", "swoosh", "transition")})


# Designed cinematic stacks: one cue -> 2-4 processed layers (transient + body + sub + air/tail).
# dt = seconds relative to the cue time; gain_db is added to the cue's own gain_db (default 0).
# Processing keys (mixdown.py): space (reverb send 0-1) + room (room|plate|hall|cathedral), width (0-1),
# sat (0-1 saturation), hp/lp (Hz), max_len, reverse.
STACKS = {
    "hit": ("key word / title slam: whip in, punchy impact, sub, short hall", [
        {"sfx": "role:whip", "dt": -.04, "gain_db": -12, "align": "peak", "width": .4},
        {"sfx": "role:impact", "gain_db": -3, "sat": .35, "space": .22, "room": "hall"},
        {"sfx": "synth:sub", "gain_db": -9}]),
    "reveal": ("showpiece reveal / logo: reversed-boom riser INTO a boom + sub + big hall", [
        {"sfx": "role:boom", "reverse": True, "align": "end", "gain_db": -10, "width": .5, "space": .25, "room": "hall"},
        {"sfx": "role:boom", "gain_db": -2, "sat": .2, "space": .35, "room": "hall", "width": .3},
        {"sfx": "synth:sub:2.4", "gain_db": -7}]),
    "trailer": ("braam-style trailer hit: boom + tonal impact + sub, saturated, cathedral tail", [
        {"sfx": "role:boom", "gain_db": -3, "sat": .5, "space": .4, "room": "cathedral", "width": .4},
        {"sfx": "role:tonal", "gain_db": -8, "sat": .3, "space": .3, "room": "cathedral"},
        {"sfx": "synth:sub:2.8", "gain_db": -6}]),
    "whoosh_hit": ("transition that lands on a hit: whoosh peak just before, impact on the frame", [
        {"sfx": "role:whip", "dt": -.03, "gain_db": -6, "align": "peak", "width": .5, "space": .12, "room": "plate"},
        {"sfx": "role:impact", "gain_db": -6, "sat": .25, "space": .18, "room": "hall"}]),
    "transition": ("big world change: heavy whoosh, wide, low sub under the swap", [
        {"sfx": "role:transition", "gain_db": -4, "align": "peak", "width": .6, "space": .18, "room": "hall"},
        {"sfx": "synth:sub:1.2", "gain_db": -13}]),
    "cut": ("snappy cut: short whoosh, wide, dry-ish", [
        {"sfx": "role:cut", "gain_db": -7, "align": "peak", "width": .45, "space": .08, "room": "plate"}]),
    "pop": ("card / sticker pop: air swoosh into a pop", [
        {"sfx": "role:swoosh", "dt": -.05, "gain_db": -16, "align": "peak", "width": .3},
        {"sfx": "role:pop", "gain_db": -9, "space": .1, "room": "room"}]),
    "glitch": ("glitch transition: glitch slice + short whoosh on the clean frame", [
        {"sfx": "role:glitch", "gain_db": -9, "width": .4, "max_len": .6},
        {"sfx": "role:cut", "gain_db": -12, "align": "peak"}]),
    "drop": ("reinforce a music drop / beat switch: sub + low boom", [
        {"sfx": "synth:sub:1.6", "gain_db": -6},
        {"sfx": "role:boom", "gain_db": -9, "hp": 35, "space": .25, "room": "hall", "max_len": 2.5}]),
    "blackout": ("cut to black / big statement: boom into a long tail, then silence", [
        {"sfx": "role:boom", "gain_db": -5, "space": .5, "room": "cathedral", "max_len": 3.5, "width": .4},
        {"sfx": "synth:sub:2.0", "gain_db": -7}]),
    "tension_hit": ("riser ending on an impact + sub", [
        {"sfx": "role:riser", "align": "end", "gain_db": -8, "width": .5, "space": .15, "room": "hall"},
        {"sfx": "role:impact", "gain_db": -4, "sat": .3, "space": .2, "room": "hall"},
        {"sfx": "synth:sub", "gain_db": -9}]),
    "ui": ("screen interaction: click + soft UI texture", [
        {"sfx": "role:click", "gain_db": -11, "space": .06, "room": "room"},
        {"sfx": "role:ui", "dt": .02, "gain_db": -18, "max_len": .4}]),
    "ding": ("logo lock / success: bright ding in a plate, low-passed", [
        {"sfx": "role:ding", "gain_db": -9, "lp": 9000, "space": .3, "room": "plate", "width": .3}]),
}


def expand(events):
    """Expand 'stack:<name>' cues into their layers (mixdown.py and timeline.py both call this)."""
    out = []
    for ev in events:
        if isinstance(ev, dict) and str(ev.get("sfx", "")).startswith("stack:"):
            name = ev["sfx"][6:]
            if name not in STACKS: raise SystemExit(f"unknown stack {name}; have: {', '.join(STACKS)}")
            for k, L in enumerate(STACKS[name][1]):
                e = {kk: vv for kk, vv in L.items() if kk != "dt"}
                e["t"] = round(ev["t"] + L.get("dt", 0), 4)
                e["gain_db"] = L.get("gain_db", -6) + ev.get("gain_db", 0)
                for kk in ("pan", "seed"):
                    if kk in ev: e[kk] = ev[kk]
                e["note"] = f"stack:{name}[{k}]" + (f" {ev['note']}" if ev.get("note") else "")
                out.append(e)
        else:
            out.append(ev)
    return out


def classify(name, st):
    n = name.lower().replace("_", " ")
    for cat, rx in CATS:
        if re.search(rx, n):
            return cat
    # unnamed: guess from the sound
    if st["shape"] == "hit":
        return "impact" if st["sub"] > .2 else "click" if st["dur"] < .3 else "impact"
    if st["shape"] in ("swell", "riser"):
        return "whoosh"
    return "tonal"


# ------------------------------------------------------------------ analysis
def bursts(env, pk, gap=15, thr=25):
    """Separate sounds inside one file: runs above peak-`thr` dB, split by >= `gap` frames (10 ms) of quiet."""
    import numpy as np
    act = np.flatnonzero(env > pk - thr)
    if len(act) == 0: return []
    out, a, b = [], act[0], act[0]
    for k in act[1:]:
        if k - b > gap: out.append((a, b + 1)); a = k
        b = k
    out.append((a, b + 1))
    return out


def analyse(path, x=None, sr=None):
    import numpy as np, soundfile as sf
    if x is None:
        x, sr = sf.read(path, always_2d=True, dtype="float32")
    ch = x.shape[1]
    m = x.mean(1)
    hop = int(sr * .01)
    n = max(1, len(m) // hop)
    fr = m[:n * hop].reshape(n, hop)
    pw = (fr ** 2).mean(1)
    env = 10 * np.log10(pw + 1e-12)
    pk = env.max()
    if pk < -90:
        return None
    floor = np.percentile(env, 10)
    tail_thr = max(pk - 45, floor + 8, -85)          # audible tail, but never the file's noise floor
    body = np.where(env > pk - 20)[0]                 # the sound itself (what you hear as "the whoosh")
    b0, b1 = body[0], body[-1] + 1
    loud = np.where(env > min(tail_thr, pk - 21))[0]
    s, e = min(loud[0], b0), max(loud[-1] + 1, b1)   # audible region (with tail)
    on = b0 + int(np.argmax(env[b0:b1] > pk - 12))    # transient arrival
    p = int(np.argmax(env))
    bdur = (b1 - b0) * .01
    bl = bursts(env, pk)                              # a file of 5 whooshes is a pack, not one sound
    events = len(bl)
    rise, fall = (p - b0) * .01, (b1 - p) * .01
    rel = (p - b0) / max(1, b1 - b0)
    if events >= 3 and bdur > 1.2:
        shape = "multi"
    elif rise <= .12 and rise <= .25 * fall:          # fast attack, long decay: a hit / boom
        shape = "hit"
    elif rel >= .7 and bdur > .3:
        shape = "riser"
    elif bdur > 4 and np.std(env[b0:b1]) < 5:
        shape = "bed"
    else:
        shape = "swell"
    dur = bdur
    seg = m[b0 * hop:b1 * hop]
    seg = seg[:sr * 4] if len(seg) > sr * 4 else seg
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2 if len(seg) > 64 else np.ones(2)
    f = np.fft.rfftfreq(len(seg), 1 / sr) if len(seg) > 64 else np.array([0, 1])
    tot = spec.sum() + 1e-12
    return {
        "sr": sr, "ch": ch, "file_dur": round(len(m) / sr, 3),
        "start": round(s * .01, 3), "end": round(e * .01, 3), "body_end": round(b1 * .01, 3),
        "rise": round(rise, 3), "fall": round(fall, 3),
        "dur": round(dur, 3), "tail": round((e - b1) * .01, 3), "events": int(events),
        "onset": round(on * .01, 3), "peak": round(p * .01, 3), "shape": shape,
        "peak_db": round(float(20 * np.log10(np.abs(x).max() + 1e-9)), 1),
        "rms_db": round(float(10 * np.log10(pw[b0:b1].mean() + 1e-12)), 1),
        "centroid": int((f * spec).sum() / tot), "sub": round(float(spec[f < 120].sum() / tot), 2),
        "_bursts": [(round(a * .01, 3), round(b * .01, 3)) for a, b in bl],
    }


def slices(x, sr, st):
    """Child entries for a pack: each burst + its tail (until the next burst), analysed on its own."""
    out, bl = [], st["_bursts"]
    for k, (a, b) in enumerate(bl):
        t0 = max(0.0, a - .03)
        t1 = min(bl[k + 1][0] - .02 if k + 1 < len(bl) else st["end"], b + 2.5)
        if t1 - t0 < .08: continue
        sub = analyse(None, x[int(t0 * sr):int(t1 * sr)], sr)
        if not sub: continue
        for key in ("start", "end", "body_end", "onset", "peak"): sub[key] = round(sub[key] + t0, 3)
        sub["slice"] = [round(t0, 3), round(t1, 3)]
        sub.pop("_bursts", None)
        out.append(sub)
    return out


def tags(name, st):
    t = set(w for w in re.split(r"[^a-z]+", name.lower()) if len(w) > 2 and w not in ("hsoundlibrary", "wav", "aif"))
    t.add("short" if st["dur"] < .5 else "medium" if st["dur"] < 1.5 else "long")
    t.add("bright" if st["centroid"] > 3500 else "dark" if st["centroid"] < 900 else "mid")
    if st["sub"] > .35: t.add("sub")
    if re.search(NOVELTY, name.lower()): t.add("character")   # a whoosh with a story in it: use on purpose only
    t.add(st["shape"])
    return sorted(t)


# ------------------------------------------------------------------ registry
def reg():
    return json.load(open(REG, encoding="utf-8")) if os.path.exists(REG) else {}


def save_reg(r):
    json.dump(r, open(REG, "w", encoding="utf-8"), indent=1)


def load_lib(name):
    r = reg()
    if name not in r:
        raise SystemExit(f"library '{name}' not registered; run: sfx_lib.py index <folder> --name {name}")
    idx = json.load(open(os.path.join(HERE, r[name]["index"]), encoding="utf-8"))
    root = r[name].get("imported") or r[name]["path"]
    root = root if os.path.isabs(root) else os.path.join(HERE, root)
    for s in idx:
        s["lib"] = name
        s["path"] = os.path.join(root, s["file"])
    return idx


ACTIVE = os.environ.get("CHITRAM_SFX_LIB")   # restrict picks to one film's library (mixdown sets it from mix.json)


def all_sounds(lib=None):
    out = []
    lib = lib or ACTIVE
    if not reg():
        raise SystemExit("no SFX library yet: fetch one for this film first -> python audio/source.py kit cinematic --to films/<n>/assets/sfx --lib <n>")
    for n in ([lib] if lib else reg().keys()):
        out += load_lib(n)
    return out


def num_id(fname):
    m = re.search(r"_(\d+)_", fname) or re.search(r"(\d+)", fname)
    return m.group(1) if m else None


def resolve(ref, used=None, seed=0):
    """'hsl:137' | 'hsl:<file>' | 'role:cut' | a path -> sound dict (path + anchors). None for plain paths
    and for 'synth:' sounds (mixdown.py makes those)."""
    if ref.startswith("synth:") or ref.startswith("stack:"):
        return None
    if ref.startswith("role:"):
        c = candidates(ref[5:])
        if not c: raise SystemExit(f"no sound fits role {ref}")
        used = used if used is not None else {}
        k = used.get(ref, seed)
        recent = used.setdefault("__recent", [])             # files of the last 4 cues, across ALL roles
        pool = c[:max(6, min(len(c), 8))]
        for j in range(len(pool)):                           # rotate through the best 6-8, skipping recent files
            pick = pool[(k + j) % len(pool)]
            if pick["path"] + str(pick.get("slice")) not in recent: break
        used[ref] = k + j + 1
        recent.append(pick["path"] + str(pick.get("slice"))); del recent[:-4]
        return pick
    if ":" in ref and not os.path.exists(ref) and not re.match(r"^[A-Za-z]:[\\/]", ref):
        lib, key = ref.split(":", 1)
        for s in load_lib(lib):
            if s["id"] == key or s["file"] == key or os.path.splitext(s["file"])[0] == key:
                return s
        raise SystemExit(f"{ref}: not in library {lib}")
    return None


def candidates(role, lib=None):
    cats, ok, anchor, _ = ROLES[role]
    c = [s for s in all_sounds(lib) if s["cat"] in cats and "pack" not in s["tags"] and ok(s)]
    # best first: the role's own category before fallbacks, then cleaner (less padding), then medium level
    want = PREFER.get(role)
    c.sort(key=lambda s: (cats.index(s["cat"]), 0 if not want or s["shape"] in want else 1,
                          abs(s["rms_db"] + 15) / 6 + s["dur"] / 4 - (s["sub"] if role in ("sub", "boom") else 0)))
    for s in c:
        s["anchor"] = anchor
    return c


def anchor_time(s, anchor=None):
    a = anchor or s.get("anchor") or {"hit": "onset", "riser": "end"}.get(s["shape"], "peak")
    return {"onset": s["onset"], "peak": s["peak"], "end": s.get("body_end", s["end"]), "start": s["start"]}[a], a


# ------------------------------------------------------------------ commands
def cmd_index(a):
    folder = a[0]
    name = opt(a, "--name") or re.sub(r"[^a-z0-9]", "", os.path.basename(os.path.normpath(folder)).lower())[:8]
    files = sorted(f for f in glob.glob(os.path.join(folder, "**", "*"), recursive=True)
                   if f.lower().endswith(AUDIO_EXT) and "__MACOSX" not in f and not os.path.basename(f).startswith("._"))
    imp = "--import" in a
    dest = os.path.join(HERE, "library", name) if imp else None
    if dest: os.makedirs(dest, exist_ok=True)
    idx = []
    import numpy as np, soundfile as sf
    for i, f in enumerate(files):
        try:
            x, sr = sf.read(f, always_2d=True, dtype="float32")
            st = analyse(f, x, sr)
        except Exception as e:
            print("skip", f, e); continue
        if not st: print("silent", f); continue
        rel = os.path.relpath(f, folder).replace("\\", "/")
        base = os.path.splitext(os.path.basename(f))[0]
        nid = num_id(base) or str(i)
        if any(s["id"] == nid for s in idx): nid = f"{nid}b"
        st.update({"id": nid, "file": rel, "name": re.sub(r"^H_SoundLibrary_\d+_", "", base).replace("_", " ")})
        cat = classify(st["name"], st)
        pack = st["shape"] == "multi" and 2 <= st["events"] <= 16 and cat in ("whoosh", "click", "ui", "glitch", "pop", "chime")
        kids = slices(x, sr, st) if pack else []
        if st["shape"] == "multi" and not kids:      # one sound with echoes (a boom in a hall): judge its attack
            st["shape"] = "hit" if st["rise"] <= .12 and st["rise"] <= .25 * st["fall"] else "swell"
        st.pop("_bursts", None)
        shift = 0.0
        if dest:   # trimmed 48 kHz FLAC copy: only the audible part, 30 ms pre-roll, 80 ms fade-out
            s0 = max(0, int((st["start"] - .03) * sr)); e0 = min(len(x), int((st["end"] + .15) * sr))
            shift = s0 / sr
            y = x[s0:e0].copy(); fo = min(len(y), int(.08 * sr)); y[-fo:] *= np.linspace(1, 0, fo)[:, None]
            if sr != 48000:
                import scipy.signal as ss
                y = ss.resample_poly(y, 48000, sr, axis=0).astype("float32")
            out = os.path.join(dest, f"{nid}_{base[-40:]}.flac".replace(" ", "_"))
            sf.write(out, y, 48000, subtype="PCM_24")
            st["file_dur"] = round(len(y) / 48000, 3); st["sr"] = 48000
            st["file"] = os.path.basename(out); st["source"] = rel
        for e in [st] + kids:
            for k in ("start", "end", "body_end", "onset", "peak"): e[k] = round(e[k] - shift, 3)
            if "slice" in e: e["slice"] = [round(max(0, e["slice"][0] - shift), 3), round(e["slice"][1] - shift, 3)]
        st["cat"] = cat
        st["tags"] = tags(st["name"], st)
        if kids: st["tags"].append("pack")
        idx.append(st)
        for k, c in enumerate(kids, 1):   # each sound of a pack is addressable: hsl:137.3
            c.update({"id": f"{nid}.{k}", "file": st["file"], "name": f"{st['name']} #{k}", "sr": st["sr"],
                      "ch": st["ch"], "file_dur": st["file_dur"]})
            if "source" in st: c["source"] = st["source"]
            c["cat"] = classify(st["name"], c) if st["cat"] not in ("whoosh", "impact", "boom") else st["cat"]
            c["tags"] = tags(st["name"], c) + ["slice"]
            idx.append(c)
        if i % 25 == 0: print(f"{i}/{len(files)} {st['name']}")
    if dest:                                          # imported copies live in the skill
        os.makedirs(os.path.join(HERE, "library"), exist_ok=True)
        ip = os.path.join("library", f"{name}.index.json")
    else:                                             # a film's fetched sounds: the index stays with the film
        ip = os.path.abspath(os.path.join(folder, "_sfx_index.json"))
    json.dump(idx, open(os.path.join(HERE, ip), "w", encoding="utf-8"), indent=0)
    r = reg()
    r[name] = {"path": os.path.abspath(folder), "index": ip.replace("\\", "/"), "count": len(idx)}
    if dest: r[name]["imported"] = f"library/{name}"
    save_reg(r)
    cats = {}
    for s in idx: cats[s["cat"]] = cats.get(s["cat"], 0) + 1
    print(f"indexed {len(idx)} sounds as '{name}' -> audio/{ip}\n", json.dumps(cats))


def line(s):
    return (f"{s['lib']}:{s['id']:<5} {s['cat']:<8} {s['shape']:<6} dur {s['dur']:5.2f}s  onset {s['onset']:5.2f} "
            f"peak {s['peak']:5.2f}  {s['rms_db']:6.1f} dB  {s['centroid']:5d} Hz sub {s['sub']:.2f}  {s['name']}")


def cmd_list(a):
    lib, cat = opt(a, "--lib"), opt(a, "--cat")
    for s in all_sounds(lib):
        if not cat or s["cat"] == cat: print(line(s))


def cmd_search(a):
    q = [w for w in re.split(r"\W+", a[0].lower()) if w]
    cat, mx, n = opt(a, "--cat"), opt(a, "--max", 99, float), opt(a, "--n", 10, int)
    res = []
    for s in all_sounds(opt(a, "--lib")):
        if cat and s["cat"] != cat or s["dur"] > mx: continue
        hay = " ".join([s["name"].lower(), s["cat"]] + s["tags"])
        sc = sum(2 if re.search(rf"\b{re.escape(w)}", s["name"].lower()) else 1 if w in hay else 0 for w in q)
        if sc: res.append((-sc, s["dur"], s))
    for _, _, s in sorted(res, key=lambda r: r[:2])[:n]: print(line(s))


def cmd_roles(a):
    for r, (cats, _, anc, what) in ROLES.items():
        c = candidates(r)
        print(f"{r:<11} anchor={anc:<5} {len(c):3d} fits  {what}")
        for s in c[:3]: print("     ", line(s))


def cmd_pick(a):
    c = candidates(a[0], opt(a, "--lib"))
    rnd = random.Random(opt(a, "--seed", 0, int)); top = c[:12]; rnd.shuffle(top)
    for s in top[:opt(a, "--n", 5, int)]: print(line(s))


def cmd_spot(a):
    """events.json: [{"t": 3.48, "role": "cut"}, {"t": 7.2, "role": "impact", "gain_db": -3}, ...]
    or {"events": [...], "voice": ..., "music": ...}.  Writes/merges the "sfx" list of a mixdown.py config."""
    global ACTIVE
    ACTIVE = opt(a, "--lib") or ACTIVE
    ev = json.load(open(a[0], encoding="utf-8"))
    ev = ev["events"] if isinstance(ev, dict) else ev
    out = a[1]
    cfg = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}
    used, sfx, last = {}, [], {}
    for e in sorted(ev, key=lambda e: e["t"]):
        if e.get("stack") or str(e.get("sfx", "")).startswith("stack:"):
            st = e.get("sfx") or f"stack:{e['stack']}"
            sfx.append({"t": e["t"], "sfx": st, "gain_db": e.get("gain_db", 0), **({"pan": e["pan"]} if "pan" in e else {}),
                        "note": e.get("note", STACKS[st[6:]][0])})
            continue
        ref = e.get("sfx") or f"role:{e['role']}"
        s = resolve(ref, used, e.get("seed", 0))
        if s and last.get(e.get("role")) == s["id"]:           # never the same file twice in a row
            s = resolve(ref, used)
        if s: last[e.get("role")] = s["id"]
        item = {"t": e["t"], "sfx": f"{s['lib']}:{s['id']}" if s else ref,
                "align": e.get("align") or ("end" if e.get("reverse") else None) or (s or {}).get("anchor") or "onset",
                "gain_db": e.get("gain_db", DEFAULT_GAIN.get(e.get("role"), -6)), "pan": e.get("pan", 0)}
        for k in ("fade_in", "fade_out", "max_len", "rate", "reverse", "hp", "lp", "note"):
            if k in e: item[k] = e[k]
        if "note" not in item and s: item["note"] = f"{e.get('role', '')}: {s['name']}"
        sfx.append(item)
    cfg["sfx"] = sfx
    cfg.setdefault("duration", round(max(e["t"] for e in ev) + 2, 2))
    json.dump(cfg, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for i in sfx: print(f"{i['t']:7.2f}  {i['sfx']:<17} align={i.get('align', 'stack'):<5} {i['gain_db']:+.0f} dB  {i.get('note', '')}")
    print(f"-> {out}  ({len(sfx)} cues). Then: python audio/mixdown.py {out} assets/mix.wav")


DEFAULT_GAIN = {  # dB relative to the file's own level; the mix bus is normalised later. Under speech, go lower.
    "cut": -8, "whip": -6, "swoosh": -12, "transition": -4, "riser": -8, "impact": -4, "boom": -3, "sub": -6,
    "pop": -10, "click": -12, "ui": -14, "glitch": -10, "ding": -9, "shutter": -10, "page": -12,
    "tension": -10, "tonal": -8, "heartbeat": -8, "fail": -8, "breath": -12,
}


def cmd_sheet(a):
    import numpy as np, soundfile as sf
    from PIL import Image, ImageDraw
    refs = [r for r in a if not r.startswith("--") and r != opt(a, "--out")]
    out = opt(a, "--out", "sfx_sheet.png")
    W, rowh = 1400, 92
    img = Image.new("RGB", (W, rowh * len(refs) + 10), (18, 18, 22)); d = ImageDraw.Draw(img)
    for i, ref in enumerate(refs):
        s = resolve(ref) or {"path": ref, "name": os.path.basename(ref), "start": 0}
        x, sr = sf.read(s["path"], always_2d=True, dtype="float32")
        if "end" not in s:
            s.update(analyse(s["path"]))
        t0, t1 = max(0, s["start"] - .05), s["end"] + .1
        seg = np.abs(x[int(t0 * sr):int(t1 * sr)].mean(1))
        y0 = i * rowh + 22; span = W - 220
        cols = np.array_split(seg, span) if len(seg) > span else [seg]
        for c, v in enumerate(cols):
            h = int(min(1, (v.max() if len(v) else 0) * 1.4) * 60)
            d.line([(210 + c, y0 + 30 - h // 2), (210 + c, y0 + 30 + h // 2)], fill=(120, 190, 255))
        for k, col in (("onset", (255, 200, 60)), ("peak", (255, 80, 80))):
            px = 210 + int((s[k] - t0) / (t1 - t0) * span)
            d.line([(px, y0 - 4), (px, y0 + 64)], fill=col, width=2)
        d.text((8, y0), f"{ref}", fill=(240, 240, 240))
        d.text((8, y0 + 16), f"{s.get('cat', '')} {s.get('shape', '')}", fill=(170, 170, 170))
        d.text((8, y0 + 32), f"{s['dur']:.2f}s  {s.get('rms_db', 0)} dB", fill=(170, 170, 170))
        d.text((210, y0 - 16), f"{s['name']}   [{t0:.2f}-{t1:.2f}s]  yellow=onset red=peak", fill=(200, 200, 200))
    img.save(out); print("->", out)


def cmd_spec(a):
    """Spectrogram of a mix/stem with a seconds ruler and optional marks: see transients, tails, sub, mud."""
    import numpy as np, soundfile as sf
    from PIL import Image, ImageDraw
    from scipy.signal import stft
    x, sr = sf.read(a[0], always_2d=True); m = x.mean(1)
    marks = [float(v) for v in (opt(a, "--marks") or "").split(",") if v]
    out = opt(a, "--out", os.path.splitext(a[0])[0] + "_spec.png")
    f, t, Z = stft(m, sr, nperseg=2048, noverlap=1536)
    S = 20 * np.log10(np.abs(Z) + 1e-9)
    fi = np.unique(np.geomspace(1, len(f) - 1, 320).astype(int)); S = np.clip((S[fi] + 90) / 80, 0, 1)
    W = max(900, min(2400, int(len(m) / sr * 100)))
    img = Image.fromarray((np.flipud(S) * 255).astype(np.uint8)).resize((W, 320)).convert("RGB"); d = ImageDraw.Draw(img)
    D = len(m) / sr; step = 1 if D <= 30 else 5
    for k in range(0, int(D) + 1, step):
        xx = int(k / D * W); d.line([(xx, 0), (xx, 8)], fill=(255, 80, 80)); d.text((xx + 2, 10), f"{k}s", fill=(255, 200, 200))
    for mk in marks:
        xx = int(mk / D * W); d.line([(xx, 24), (xx, 320)], fill=(80, 200, 255))
    for hz, lab in ((100, "100Hz"), (1000, "1k"), (8000, "8k")):
        yy = 320 - int(np.searchsorted(f[fi], hz) / len(fi) * 320); d.text((W - 44, yy - 6), lab, fill=(160, 255, 160))
    img.save(out); print("->", out, "(blue lines = --marks; bottom = sub, top = air)")


def cmd_catalog(a):
    out = opt(a, "--out", os.path.join(os.path.dirname(HERE), "SFX-CATALOG.md"))
    lines = ["# SFX catalog (generated by audio/sfx_lib.py catalog — do not edit by hand)", "",
             "Columns: ref · category · shape · audible length · anchor offsets (s from file start) · level · brightness",
             "Use `ref` in cue files (`\"sfx\": \"hsl:137\"`). Roles → `python audio/sfx_lib.py roles`.", ""]
    for lib in reg():
        sounds = load_lib(lib)
        lines += [f"## {lib} — {len(sounds)} sounds", f"source: `{reg()[lib]['path']}`", ""]
        for cat in sorted({s["cat"] for s in sounds}):
            lines += [f"### {cat}", "", "| ref | name | shape | dur | onset | peak | dB | Hz | sub |", "|---|---|---|---|---|---|---|---|---|"]
            for s in sorted((s for s in sounds if s["cat"] == cat), key=lambda s: s["dur"]):
                lines.append(f"| {lib}:{s['id']} | {s['name']} | {s['shape']} | {s['dur']:.2f} | {s['onset']:.2f} | "
                             f"{s['peak']:.2f} | {s['rms_db']} | {s['centroid']} | {s['sub']} |")
            lines.append("")
    open(out, "w", encoding="utf-8").write("\n".join(lines)); print("->", out)


def opt(a, name, default=None, cast=str):
    return cast(a[a.index(name) + 1]) if name in a and a.index(name) + 1 < len(a) else default


if __name__ == "__main__":
    def cmd_stacks(a):
        for k, (d, L) in STACKS.items():
            print(f"stack:{k:<12} {d}")
            for l in L: print("      ", {kk: vv for kk, vv in l.items()})
    cmds = {"stacks": cmd_stacks, "index": cmd_index, "list": cmd_list, "search": cmd_search, "roles": cmd_roles, "pick": cmd_pick,
            "spot": cmd_spot, "sheet": cmd_sheet, "spec": cmd_spec, "catalog": cmd_catalog}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__); sys.exit(1)
    cmds[sys.argv[1]](sys.argv[2:])
