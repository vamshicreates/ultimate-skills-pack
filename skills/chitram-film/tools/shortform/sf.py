#!/usr/bin/env python3
"""
sf.py: the short-form edit toolkit (see SHORTFORM.md). Footage in, a tight, naturally cut master
out, plus everything the build needs (word times, faces, cut list, cut-outs, mixed audio).

  python sf.py ingest   SRC WORK [--model small] [--lang auto]
        probe, transcribe (word times), speech energy, scene cuts, face track, flip-book sheets
  python sf.py plan     WORK [--pace natural|tight|relaxed] [--no-retakes] [--keep-fillers]
        propose the edit: remove dead air, fillers and false starts. Writes WORK/edl.json and
        WORK/edl.txt (read it, change it, then cut)
  python sf.py cut      SRC WORK [--size 1080x1920] [--fps 25] [--reframe face|center|none]
        render WORK/master.mp4 + master.wav from edl.json with natural cuts; remap the words
        (master_words.json) and list every cut (cuts.json, with jump-cut scores)
  python sf.py frames   VIDEO OUTDIR [--fps 25]            high-quality JPG sequence (%05d.jpg, from 0)
  python sf.py cutout   FRAMES OUTDIR --ranges 105-180,337-549 [--outline 16] [--color F7F1EC]
                        [--shadow 0.30] [--key-dark-bottom 0]   sticker cut-outs (RGBA webp)
  python sf.py halftone IN OUT [--mode dot|line] [--cell 9] [--ink 111216] [--paper none]
  python sf.py mix      --voice master.wav [--bed bed.wav] [--sfx sfx.wav] --out final.wav
                        [--duration 44] [--bed-gain 0.22] [--sfx-gain 0.55] [--lufs -14]
  python sf.py finish   IN.mp4 OUT.mp4 [--crf 14]           standard-range BT.709 delivery + strip

Needs: ffmpeg/ffprobe on PATH (or env FFMPEG=path/to/ffmpeg.exe), numpy, opencv-python-headless,
pillow; faster-whisper (ingest); rembg (cutout).
"""
import json, math, os, re, subprocess, sys, shutil, tempfile

FF = os.environ.get("FFMPEG") or "ffmpeg"
if os.path.isdir(FF):
    FF = os.path.join(FF, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
FP = os.path.join(os.path.dirname(FF), "ffprobe" + (".exe" if os.name == "nt" else "")) if os.path.dirname(FF) else "ffprobe"
if not shutil.which(FP) and not os.path.exists(FP):
    FP = "ffprobe"

FILLERS = {"um", "umm", "uh", "uhh", "uhm", "erm", "er", "ah", "ahh", "hmm", "mm", "mhm", "eh"}
SOFT_FILLERS = {"like", "basically", "actually", "literally", "so", "right", "okay", "you know", "i mean"}


# ------------------------------------------------------------------ helpers
def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        sys.exit(f"command failed: {' '.join(map(str, cmd[:6]))} ...\n{r.stderr[-1500:]}")
    return r


def opt(a, name, default=None, cast=str):
    if name in a:
        return cast(a[a.index(name) + 1])
    return default


def probe(src):
    r = run([FP, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", src])
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    fr = v["avg_frame_rate"] if v else "0/1"
    n, d = (fr.split("/") + ["1"])[:2]
    rot = 0
    for sd in (v or {}).get("side_data_list", []):
        if "rotation" in sd:
            rot = int(sd["rotation"])
    w, h = (v["width"], v["height"]) if v else (0, 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    return {"duration": float(j["format"]["duration"]), "width": w, "height": h,
            "fps": round(float(n) / float(d or 1), 3) if float(d or 1) else 0,
            "has_audio": a is not None, "audio_rate": int(a["sample_rate"]) if a else 0,
            "pix_fmt": v.get("pix_fmt") if v else None, "color_range": v.get("color_range") if v else None,
            "color_space": v.get("color_space") if v else None}


def load_wav_mono(src, sr=16000):
    import numpy as np
    r = subprocess.run([FF, "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                       capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0, sr


def energy_db(x, sr, hop=0.01):
    import numpy as np
    n = int(sr * hop)
    m = len(x) // n
    fr = x[: m * n].reshape(m, n)
    rms = np.sqrt((fr ** 2).mean(1) + 1e-12)
    return 20 * np.log10(rms + 1e-9)          # one value per 10 ms


def speech_threshold(db):
    import numpy as np
    return max(np.percentile(db, 15) + 6, np.percentile(db, 90) - 32)


def silences(db, min_len=0.12):
    """[(start, end)] of quiet runs >= min_len seconds (10 ms energy frames)"""
    import numpy as np
    q = db < speech_threshold(db)
    out, i, n = [], 0, len(q)
    while i < n:
        if q[i]:
            j = i
            while j < n and q[j]:
                j += 1
            if (j - i) / 100 >= min_len:
                out.append((i / 100, j / 100))
            i = j
        else:
            i += 1
    return out


def speech_chunks(db, split=0.45, max_len=25.0):
    """speech spans separated by pauses >= split s; long spans re-split at their longest pause"""
    total = len(db) / 100
    sil = [s for s in silences(db, 0.2)]
    cuts = [s for s in sil if s[1] - s[0] >= split]
    spans, cur = [], 0.0
    for s0, s1 in cuts:
        if s0 > cur:
            spans.append([cur, s0])
        cur = s1
    if total > cur:
        spans.append([cur, total])
    out = []
    while spans:
        c0, c1 = spans.pop(0)
        if c1 - c0 <= max_len:
            if c1 - c0 >= 0.15:
                out.append((c0, c1))
            continue
        inner = [s for s in sil if s[0] > c0 + 1 and s[1] < c1 - 1]
        if not inner:
            out.append((c0, c1)); continue
        s0, s1 = max(inner, key=lambda s: s[1] - s[0])
        spans[:0] = [[c0, s0], [s1, c1]]
    return out


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ ingest
def ingest(a):
    src, work = a[0], a[1]
    os.makedirs(work, exist_ok=True)
    info = probe(src)
    info["src"] = os.path.abspath(src)
    save(os.path.join(work, "probe.json"), info)
    print(f"probe: {info['width']}x{info['height']} {info['fps']}fps {info['duration']:.2f}s audio={info['has_audio']}")

    # 1. speech energy (natural cut points) + speech chunks
    if info["has_audio"]:
        import numpy as np
        x, sr = load_wav_mono(src)
        db = energy_db(x, sr)
        np.save(os.path.join(work, "energy.npy"), db)

    # 2. transcript with word times, chunk by chunk. Whisper run over a whole take silently
    #    swallows retakes and repeated lines; transcribing each pause-separated chunk on its own
    #    keeps every spoken attempt, so plan can find false starts.
    if info["has_audio"] and "--no-asr" not in a:
        from faster_whisper import WhisperModel
        model = opt(a, "--model", "small")
        lang = opt(a, "--lang", "auto")
        prompt = opt(a, "--prompt", None)     # brand words / names, e.g. "AASTHI, NRIs, KYC"
        m = WhisperModel(model, device="cpu", compute_type="int8")
        chunks = speech_chunks(db)
        print(f"asr: {len(chunks)} speech chunks")
        out, langs = [], {}
        for c0, c1 in chunks:
            a0, a1 = max(0, int((c0 - 0.1) * sr)), min(len(x), int((c1 + 0.1) * sr))
            segs, ti = m.transcribe(x[a0:a1], word_timestamps=True, vad_filter=False, initial_prompt=prompt,
                                    language=None if lang == "auto" else lang, condition_on_previous_text=False)
            langs[ti.language] = langs.get(ti.language, 0) + (c1 - c0)
            off = a0 / sr
            for s in segs:
                ws = [{"w": w.word.strip(), "s": round(w.start + off, 2), "e": round(w.end + off, 2),
                       "p": round(w.probability, 2)} for w in (s.words or []) if w.word.strip()]
                if not ws:
                    continue
                out.append({"s": ws[0]["s"], "e": ws[-1]["e"], "text": s.text.strip(), "words": ws})
                print(f"  {ws[0]['s']:6.2f}-{ws[-1]['e']:6.2f} {s.text.strip()}", flush=True)
        ti_lang = max(langs, key=langs.get) if langs else "unknown"

        class _T: language = ti_lang
        ti = _T()
        save(os.path.join(work, "words.json"), {"lang": ti.language, "segments": out})
        with open(os.path.join(work, "transcript.txt"), "w", encoding="utf-8") as f:
            f.write(f"# language: {ti.language}   (index  start-end  word  [prob])\n")
            i = 0
            for s in out:
                f.write(f"\n## {s['s']:.2f}-{s['e']:.2f}  {s['text']}\n")
                for w in s["words"]:
                    flag = "  <- low confidence" if w["p"] < 0.5 else ""
                    f.write(f"{i:4d}  {w['s']:6.2f}-{w['e']:6.2f}  {w['w']}{flag}\n")
                    i += 1
        print(f"transcript: {sum(len(s['words']) for s in out)} words, language {ti.language}")

    # 3. scene cuts (multi-camera sources, existing edits)
    r = subprocess.run([FF, "-hide_banner", "-i", src, "-vf", "select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    cuts = [round(float(t), 3) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    save(os.path.join(work, "scenes.json"), cuts)
    print(f"scene cuts: {len(cuts)} {cuts[:12]}")

    # 4. face track (5 fps) -> where the face is, where the empty side is
    faces = face_track(src, info)
    save(os.path.join(work, "faces.json"), faces)
    if faces["summary"]:
        print(f"face: {faces['summary']}")

    # 5. flip-book sheets: 2 fps, 6x4 = 12 s per sheet
    sd = os.path.join(work, "sheets")
    os.makedirs(sd, exist_ok=True)
    run([FF, "-v", "error", "-y", "-i", src, "-vf", "fps=2,scale=320:-2,tile=6x4", "-q:v", "4",
         os.path.join(sd, "sheet_%02d.jpg")])
    n = len([f for f in os.listdir(sd) if f.endswith(".jpg")])
    print(f"sheets: {n} in {sd}  (cell k of sheet s = time (s-1)*12 + k*0.5 s, k from 0, row-major)")


def face_track(src, info, fps=5):
    import cv2, numpy as np
    casc = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
    cap = cv2.VideoCapture(src)
    vf = cap.get(cv2.CAP_PROP_FPS) or info["fps"] or 25
    step = max(1, round(vf / fps))
    track, i = [], 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if i % step == 0:
            H, W = fr.shape[:2]
            s = 480 / max(W, H)
            g = cv2.cvtColor(cv2.resize(fr, (int(W * s), int(H * s))), cv2.COLOR_BGR2GRAY)
            f = casc.detectMultiScale(g, 1.1, 5, minSize=(int(24 * s * 2), int(24 * s * 2)))
            if len(f):
                x, y, w, h = max(f, key=lambda b: b[2] * b[3])
                track.append({"t": round(i / vf, 2), "x": round(x / s / W, 4), "y": round(y / s / H, 4),
                              "w": round(w / s / W, 4), "h": round(h / s / H, 4)})
        i += 1
    cap.release()
    summ = None
    if track:
        arr = np.array([[f["x"], f["y"], f["w"], f["h"]] for f in track])
        med = np.median(arr, 0)
        cx = med[0] + med[2] / 2
        W, H = info["width"], info["height"]
        summ = {"box_px": [int(med[0] * W), int(med[1] * H), int(med[2] * W), int(med[3] * H)],
                "center_x": round(float(cx), 3), "moves_x": round(float(np.std(arr[:, 0] + arr[:, 2] / 2)), 3),
                "empty_side": "right" if cx < 0.45 else "left" if cx > 0.55 else "both (centred)",
                "coverage": round(len(track) / max(1, i // step), 2)}
    return {"fps": fps, "track": track, "summary": summ}


# ------------------------------------------------------------------ plan (the natural edit)
PACE = {  # max silence kept after: sentence end, comma, mid-phrase
    "relaxed": (0.55, 0.34, 0.24),
    "natural": (0.42, 0.26, 0.18),
    "tight":   (0.30, 0.20, 0.12),
}


def plan(a):
    import numpy as np
    work = a[0]
    info = load(os.path.join(work, "probe.json"))
    W = load(os.path.join(work, "words.json"))
    words = [w for s in W["segments"] for w in s["words"]]
    db = np.load(os.path.join(work, "energy.npy"))
    pace = opt(a, "--pace", "natural")
    k_sent, k_comma, k_mid = PACE[pace]
    sil = silences(db, 0.12)                  # the truth about pauses comes from the audio, not the ASR

    drop = [False] * len(words)
    reason = [""] * len(words)
    if "--keep-fillers" not in a:
        for i, w in enumerate(words):
            if norm(w["w"]) in FILLERS:
                drop[i], reason[i] = True, "filler"
    # false starts / retakes: a 3-word run repeated within 14 words / 8 s -> keep the later take.
    # The dropped span runs from where the first ATTEMPT began to where the retake begins (phrase
    # boundaries), so two takes are never spliced mid-sentence.
    def boundary(m):   # a new phrase starts at word m
        return m == 0 or bool(re.search(r"[.?!,;:]$", words[m - 1]["w"])) or words[m]["s"] - words[m - 1]["e"] >= 0.3

    if "--no-retakes" not in a:
        N = [norm(w["w"]) for w in words]
        i = 0
        while i < len(words) - 3:
            hit = None
            for j in range(i + 1, min(len(words) - 2, i + 15)):
                if N[i:i + 3] == N[j:j + 3] and all(N[i:i + 3]) and words[j]["s"] - words[i]["s"] < 8:
                    hit = j
            if hit:
                a0 = i
                while not boundary(a0):
                    a0 -= 1
                b0 = hit
                while b0 > i + 1 and not boundary(b0):
                    b0 -= 1
                if b0 <= i:
                    b0 = hit
                for k in range(a0, b0):
                    if not drop[k]:
                        drop[k], reason[k] = True, "false start (retake follows)"
                i = hit
            else:
                i += 1

    kept = [i for i in range(len(words)) if not drop[i]]
    if not kept:
        sys.exit("nothing left to keep")

    def quiet_point(t0, t1):
        a0, a1 = max(0, int(t0 * 100)), min(len(db), int(t1 * 100) + 1)
        if a1 - a0 < 2:
            return (t0 + t1) / 2
        return (a0 + int(np.argmin(db[a0:a1]))) / 100

    def keep_for(t):
        """pause length to keep after the last kept word that starts before t"""
        prev = [i for i in kept if words[i]["s"] < t]
        txt = words[prev[-1]]["w"] if prev else ""
        return k_sent if re.search(r"[.?!]$", txt) else k_comma if re.search(r"[,;:â€“â€”-]$", txt) else k_mid

    removes = []
    # A. dropped words (fillers, false starts): cut from the end of the last kept sound to the next kept sound
    k = 0
    while k < len(words):
        if not drop[k]:
            k += 1; continue
        j = k
        while j < len(words) and drop[j]:
            j += 1
        prev_e = words[k - 1]["e"] if k > 0 else max(0.0, words[k]["s"] - 0.1)
        next_s = words[j]["s"] if j < len(words) else words[j - 1]["e"] + 0.3
        # snap to real silence edges near the word edges
        after = [s for s in sil if prev_e - 0.25 <= s[0] <= words[k]["s"] + 0.05]
        before = [s for s in sil if words[j - 1]["e"] - 0.05 <= s[1] <= next_s + 0.25]
        c0 = (after[0][0] if after else prev_e) + 0.05
        c1 = (before[-1][1] if before else next_s) - 0.08
        keep = keep_for(c0)
        c0 += min(keep * 0.5, 0.12)
        if c1 - c0 > 0.08:
            removes.append({"from": round(c0, 3), "to": round(c1, 3),
                            "why": ", ".join(sorted(set(reason[x] for x in range(k, j)))),
                            "text": " ".join(words[x]["w"] for x in range(k, j))})
        k = j
    # B. pauses: every quiet run longer than the pace allows gets shortened (keep a breath each side)
    head = max(0.0, words[kept[0]]["s"] - 0.15)
    tail = min(info["duration"], words[kept[-1]]["e"] + 0.45)
    for s0, s1 in sil:
        if s1 <= head or s0 >= tail:
            continue
        keep = keep_for(s0 + 0.01)
        L = s1 - s0
        if L <= keep + 0.06:
            continue
        pad_out = min(keep * 0.55, 0.16)
        pad_in = keep - pad_out
        c0 = quiet_point(s0 + pad_out, s0 + pad_out + 0.04)
        c1 = quiet_point(s1 - pad_in - 0.04, s1 - pad_in)
        if c1 - c0 > 0.06:
            removes.append({"from": round(c0, 3), "to": round(c1, 3), "why": f"pause {L:.2f}s -> {keep:.2f}s", "text": ""})

    # merge overlapping removals
    removes.sort(key=lambda r: r["from"])
    merged = []
    for r in removes:
        if merged and r["from"] <= merged[-1]["to"] + 0.02:
            m = merged[-1]
            m["to"] = max(m["to"], r["to"])
            m["why"] = ", ".join(x for x in dict.fromkeys((m["why"] + ", " + r["why"]).split(", ")) if x)
            m["text"] = (m["text"] + " " + r["text"]).strip()
        else:
            merged.append(dict(r))
    removes = merged

    keeps, cur = [], head
    for r in removes:
        if r["from"] > cur:
            keeps.append([round(cur, 3), r["from"]])
        cur = max(cur, r["to"])
    keeps.append([round(cur, 3), round(tail, 3)])
    # a sliver shorter than 0.3 s with no word in it flashes on screen: drop it
    keeps = [k for k in keeps if k[1] - k[0] >= 0.3 or any(k[0] <= words[i]["s"] < k[1] for i in kept)]
    total = sum(b - a for a, b in keeps)
    edl = {"src": info["src"], "pace": pace, "source_duration": info["duration"], "keep": keeps,
           "removed": removes, "result_duration": round(total, 2),
           "drop_words": [i for i in range(len(words)) if drop[i]],
           "flags": [{"i": i, "t": w["s"], "w": w["w"]} for i, w in enumerate(words)
                     if norm(w["w"]) in SOFT_FILLERS and not drop[i]]}
    save(os.path.join(work, "edl.json"), edl)
    with open(os.path.join(work, "edl.txt"), "w", encoding="utf-8") as f:
        f.write(f"pace {pace}: {info['duration']:.2f}s -> {total:.2f}s  ({len(removes)} cuts)\n\nREMOVED\n")
        for r in removes:
            f.write(f"  {r['from']:7.2f}-{r['to']:7.2f}  {r['to'] - r['from']:.2f}s  {r['why']}  {r['text']}\n")
        f.write("\nKEEP\n")
        for k in keeps:
            said = " ".join(words[i]["w"] for i in kept if k[0] <= (words[i]["s"] + words[i]["e"]) / 2 < k[1]
                            or (i == kept[0] and k is keeps[0]))
            f.write(f"  {k[0]:7.2f}-{k[1]:7.2f}  {said}\n")
        if edl["flags"]:
            f.write("\nSOFT FILLERS KEPT (judge by ear; delete via the keep list if they are verbal tics)\n")
            for fl in edl["flags"]:
                f.write(f"  #{fl['i']} {fl['t']:.2f} {fl['w']}\n")
    print(open(os.path.join(work, "edl.txt"), encoding="utf-8").read())


# ------------------------------------------------------------------ cut (render the master)
def cut(a):
    import numpy as np
    src, work = a[0], a[1]
    info = load(os.path.join(work, "probe.json"))
    edl = load(os.path.join(work, "edl.json"))
    fps = opt(a, "--fps", None, float) or (25.0 if abs(info["fps"] - 25) < 1 else 30.0 if info["fps"] >= 29 else 25.0)
    size = opt(a, "--size", None)
    reframe = opt(a, "--reframe", "face")
    W, H = info["width"], info["height"]
    tw, th = (map(int, size.split("x"))) if size else (W, H)

    # quantise every edge to the output frame grid, so audio and picture cut on the same instant
    q = lambda t: round(round(t * fps) / fps, 6)
    keeps = [[q(k0), q(k1)] for k0, k1 in edl["keep"] if q(k1) - q(k0) >= 1 / fps]

    # crop for the target aspect (static, premium: no wobbling auto-reframe)
    crop = ""
    if (tw, th) != (W, H):
        ar = tw / th
        if W / H > ar:            # source wider -> crop width
            cw, ch = int(round(H * ar / 2) * 2), H
            cx = 0.5
            if reframe == "face":
                ft = load(os.path.join(work, "faces.json"))
                if ft["summary"]:
                    cx = ft["summary"]["center_x"]
            x = int(min(max(cx * W - cw / 2, 0), W - cw))
            crop = f"crop={cw}:{ch}:{x}:0,"
        else:                     # source taller -> crop height (keep head room: bias up)
            cw, ch = W, int(round(W / ar / 2) * 2)
            y = int((H - ch) * 0.35)
            crop = f"crop={cw}:{ch}:0:{y},"
    vfx = f"{crop}scale={tw}:{th}:flags=lanczos,fps={fps},format=yuv420p"

    parts, n = [], len(keeps)
    for i, (k0, k1) in enumerate(keeps):
        d = k1 - k0
        fi = 0.012 if i > 0 else 0.0
        fo = 0.012 if i < n - 1 else 0.0
        parts.append(f"[0:v]trim=start={k0}:end={k1},setpts=PTS-STARTPTS[v{i}];")
        af = f"[0:a]atrim=start={k0}:end={k1},asetpts=PTS-STARTPTS"
        if fi:
            af += f",afade=t=in:st=0:d={fi}"
        if fo:
            af += f",afade=t=out:st={d - fo:.4f}:d={fo}"
        parts.append(af + f"[a{i}];")
    fc = "".join(parts) + "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac];[vc]{vfx}[vo]"
    fcf = os.path.join(work, "cut_filter.txt")
    with open(fcf, "w", encoding="utf-8") as f:
        f.write(fc)
    master = os.path.join(work, "master.mp4")
    print(f"cutting {n} segments -> {tw}x{th} @ {fps} fps ...")
    run([FF, "-v", "error", "-y", "-i", src, "-filter_complex_script", fcf, "-map", "[vo]", "-map", "[ac]",
         "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", master])
    run([FF, "-v", "error", "-y", "-i", master, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le",
         os.path.join(work, "master.wav")])

    # remap words: source time -> master time
    offs, acc = [], 0.0
    for k0, k1 in keeps:
        offs.append((k0, k1, acc))
        acc += k1 - k0

    def home(t):   # the keep segment a source time belongs to (nearest one if it fell in a cut)
        return min(offs, key=lambda o: 0 if o[0] <= t <= o[1] else min(abs(t - o[0]), abs(t - o[1])))

    def remap(t, seg):
        k0, k1, o = seg
        return round(o + (min(max(t, k0), k1) - k0), 3)

    Wd = load(os.path.join(work, "words.json"))
    dropped = set(edl.get("drop_words", []))
    out_words, idx = [], 0
    for s in Wd["segments"]:
        for w in s["words"]:
            i, idx = idx, idx + 1
            if i in dropped:
                continue
            seg = home((w["s"] + w["e"]) / 2)       # ASR word edges drift; the midpoint decides
            ns, ne = remap(w["s"], seg), remap(w["e"], seg)
            if ne - ns < 0.06:
                ne = round(ns + 0.12, 3)
            out_words.append({"w": w["w"], "s": ns, "e": ne})
    # sentences for planning
    sents, cur = [], []
    for w in out_words:
        cur.append(w)
        if re.search(r"[.?!]$", w["w"]):
            sents.append({"s": cur[0]["s"], "e": cur[-1]["e"], "text": " ".join(x["w"] for x in cur)})
            cur = []
    if cur:
        sents.append({"s": cur[0]["s"], "e": cur[-1]["e"], "text": " ".join(x["w"] for x in cur)})
    mw = {"lang": Wd.get("lang"), "fps": fps, "duration": round(acc, 3), "words": out_words, "sentences": sents}
    save(os.path.join(work, "master_words.json"), mw)
    with open(os.path.join(work, "words.js"), "w", encoding="utf-8") as f:   # <script src="assets/words.js">
        f.write("window.WORDS = " + json.dumps(mw, ensure_ascii=False) + ";\n")

    # cut list with a jump-cut score (how visible the join is)
    import cv2
    cap = cv2.VideoCapture(master)
    cuts, t = [], 0.0
    for k0, k1, o in offs[1:]:
        f = int(round(o * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, f - 1)); ok1, A = cap.read()
        ok2, B = cap.read()
        score = None
        if ok1 and ok2:
            g = lambda im: cv2.cvtColor(cv2.resize(im, (96, int(96 * im.shape[0] / im.shape[1]))), cv2.COLOR_BGR2GRAY).astype(np.float32)
            score = round(float(np.abs(g(A) - g(B)).mean()), 2)
        cuts.append({"t": round(o, 3), "frame": f, "src_from": k0, "jump": score,
                     "visible": bool(score is not None and score > 2.0)})
    cap.release()
    save(os.path.join(work, "cuts.json"), cuts)
    with open(os.path.join(work, "cuts.js"), "w", encoding="utf-8") as f:
        f.write("window.CUTS = " + json.dumps(cuts) + ";\n")
    vis = sum(c["visible"] for c in cuts)
    print(f"master: {master}  {acc:.2f}s  {len(cuts)} cuts ({vis} visible jump cuts -> cover each: punch-in, world switch or insert)")
    print(f"words:  {os.path.join(work, 'master_words.json')}  ({len(out_words)} words, {len(sents)} sentences)")


# ------------------------------------------------------------------ frames
def frames(a):
    vid, out = a[0], a[1]
    fps = opt(a, "--fps", None)
    os.makedirs(out, exist_ok=True)
    vf = ["-vf", f"fps={fps}"] if fps else []
    run([FF, "-v", "error", "-y", "-i", vid, *vf, "-q:v", "1", "-start_number", "0", os.path.join(out, "%05d.jpg")])
    n = len([f for f in os.listdir(out) if f.endswith(".jpg")])
    print(f'{n} frames -> <img class="full" data-seq="{out.replace(os.sep, "/")}/%05d.jpg" data-first="0" '
          f'data-count="{n}" data-seq-fps="{fps or probe(vid)["fps"]}" data-at="0">')


# ------------------------------------------------------------------ cutout (sticker person)
def cutout(a):
    import numpy as np, cv2
    from PIL import Image
    from rembg import new_session, remove
    fr_dir, out = a[0], a[1]
    ranges = [tuple(map(int, r.split("-"))) for r in opt(a, "--ranges").split(",")]
    outline = opt(a, "--outline", 16, int)
    color = np.array([int(opt(a, "--color", "F7F1EC")[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
    shadow = opt(a, "--shadow", 0.30, float)
    key_dark = opt(a, "--key-dark-bottom", 0, int)      # e.g. 48: key near-black pixels (dark sofa) ...
    band = opt(a, "--key-band", 0.75, float)            # ... in the bottom (1-band) of the frame
    model = opt(a, "--model", "u2net_human_seg")
    mask_dir = os.path.join(out, "_mask")
    os.makedirs(mask_dir, exist_ok=True); os.makedirs(out, exist_ok=True)
    sess = new_session(model)
    fp = lambda f: os.path.join(fr_dir, f"{f:05d}.jpg")
    for a0, b0 in ranges:
        for f in range(a0, b0 + 1):
            p = os.path.join(mask_dir, f"{f:05d}.png")
            if not os.path.exists(p):
                remove(Image.open(fp(f)), session=sess, only_mask=True).save(p)
        print(f"masks {a0}-{b0} done", flush=True)
    load_m = lambda f: cv2.imread(os.path.join(mask_dir, f"{f:05d}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32)
    ks = outline * 2 + 1
    k_stroke = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks, ks))
    for a0, b0 in ranges:
        for f in range(a0, b0 + 1):
            m = 0.5 * load_m(f) + 0.25 * load_m(max(a0, f - 1)) + 0.25 * load_m(min(b0, f + 1))   # temporal smooth
            m = np.clip((m - 60) * (255 / 150), 0, 255)
            bgr = cv2.imread(fp(f))
            Hh = bgr.shape[0]
            if key_dark:
                gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                dark = (gray < key_dark).astype(np.uint8); dark[: int(Hh * band), :] = 0
                dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
                m[dark > 0] = 0
            nb, lab, st, _ = cv2.connectedComponentsWithStats((m > 127).astype(np.uint8))
            if nb > 1:
                keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
                m = m * cv2.dilate((lab == keep).astype(np.uint8), np.ones((9, 9), np.uint8))
            m = cv2.GaussianBlur(m, (3, 3), 0)
            alpha = m / 255.0
            if outline > 0:
                s = cv2.dilate((m > 110).astype(np.uint8) * 255, k_stroke).astype(np.float32)
                s = cv2.GaussianBlur(s, (15, 15), 0)
                s = np.clip((s - 110) * (255 / 40), 0, 255) / 255.0
            else:
                s = alpha.copy()
            sh = np.zeros_like(s)
            if shadow > 0:
                sh = cv2.GaussianBlur(s, (0, 0), 14)
                sh = np.roll(np.roll(sh, 14, 0), 8, 1) * shadow
                sh[:14, :] = 0; sh[:, :8] = 0                     # np.roll wraps: clear the wrapped band
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
            stroke = s if outline > 0 else np.zeros_like(s)
            out_a = stroke + sh * (1 - stroke)
            col = color * stroke[..., None] / np.maximum(out_a, 1e-6)[..., None]
            fin_a = alpha + out_a * (1 - alpha)
            fin = (rgb * alpha[..., None] + col * out_a[..., None] * (1 - alpha[..., None])) / np.maximum(fin_a, 1e-6)[..., None]
            img = np.dstack([np.clip(fin, 0, 255), np.clip(fin_a * 255, 0, 255)]).astype(np.uint8)
            Image.fromarray(img, "RGBA").save(os.path.join(out, f"{f:05d}.webp"), quality=92, alpha_quality=100, method=4)
        print(f"cut-outs {a0}-{b0} done", flush=True)
    print(f'use: <img class="full" data-seq="{out.replace(os.sep, "/")}/%05d.webp" data-first="<range start>" '
          f'data-count="<range length>" data-seq-fps="<fps>" data-at="<film time of range start>">')


# ------------------------------------------------------------------ halftone (print texture for photos)
def halftone(a):
    import numpy as np, cv2
    from PIL import Image
    src, dst = a[0], a[1]
    mode = opt(a, "--mode", "dot")
    cell = opt(a, "--cell", 9, int)
    ink = np.array([int(opt(a, "--ink", "111216")[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)
    paper = opt(a, "--paper", "none")
    im = Image.open(src).convert("RGBA")
    rgba = np.array(im)
    alpha = rgba[..., 3].astype(np.float32) / 255
    g = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    sel = g[alpha > 0.5] if (alpha > 0.5).any() else g.ravel()
    lo, hi = np.percentile(sel, 2), np.percentile(sel, 98)
    g = np.clip((g - lo) / max(hi - lo, 1e-3), 0, 1)  # auto-levels on the subject, like a print
    H, W = g.shape
    S = 4                                             # supersample for smooth dots
    big = cv2.resize(g, (W * S, H * S), interpolation=cv2.INTER_LINEAR)
    yy, xx = np.mgrid[0:H * S, 0:W * S].astype(np.float32)
    c = cell * S
    if mode == "line":
        ang = np.deg2rad(45)
        u = (xx * np.cos(ang) + yy * np.sin(ang)) % c
        dist = np.abs(u - c / 2) / (c / 2)               # 0 at the line centre
        inkmask = dist < (1 - big)
    else:
        ang = np.deg2rad(45)
        u = xx * np.cos(ang) + yy * np.sin(ang)
        v = -xx * np.sin(ang) + yy * np.cos(ang)
        du, dv = (u % c) - c / 2, (v % c) - c / 2
        r = np.sqrt(du ** 2 + dv ** 2) / (c / 2 * 1.414)
        inkmask = r < np.sqrt(2 * (1 - big) / np.pi)      # dot area = ink coverage = 1 - grey
    m = cv2.resize(inkmask.astype(np.float32), (W, H), interpolation=cv2.INTER_AREA)
    out = np.zeros((H, W, 4), np.uint8)
    if paper == "none":
        out[..., :3] = ink
        out[..., 3] = np.clip(m * alpha * 255, 0, 255)
    else:
        pc = np.array([int(paper[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
        out[..., :3] = np.clip(pc * (1 - m[..., None]) + ink * m[..., None], 0, 255)
        out[..., 3] = np.clip(alpha * 255, 0, 255)
    Image.fromarray(out, "RGBA").save(dst)
    print(f"halftone ({mode}, cell {cell}) -> {dst}")


# ------------------------------------------------------------------ mix (voice on top, always)
def loudnorm_2pass(inp, out, lufs, extra_af=""):
    r = subprocess.run([FF, "-hide_banner", "-i", inp, "-af", f"{extra_af}loudnorm=I={lufs}:TP=-1.0:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    j = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    af = (f"{extra_af}loudnorm=I={lufs}:TP=-1.0:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    run([FF, "-v", "error", "-y", "-i", inp, "-af", af, "-ar", "48000", "-c:a", "pcm_s16le", out])
    return j


def mix(a):
    voice = opt(a, "--voice"); bed = opt(a, "--bed"); sfx = opt(a, "--sfx"); out = opt(a, "--out")
    dur = opt(a, "--duration", None, float)
    bg = opt(a, "--bed-gain", 0.22, float); sg = opt(a, "--sfx-gain", 0.55, float)
    vg = opt(a, "--voice-gain", 1.0, float)
    lufs = opt(a, "--lufs", -14.0, float)
    clean = "--clean" in a        # gentle: high-pass 70 Hz + de-click; never reverb, never pitch
    ins = ["-i", voice]
    vchain = f"volume={vg}" + (",highpass=f=70,adeclick" if clean else "")
    fc = f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,{vchain},asplit=2[v][vk];"
    mixin, k = ["[v]"], 1
    if bed:
        ins += ["-i", bed]
        fc += (f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={bg}[b];"
               f"[b][vk]sidechaincompress=threshold=0.02:ratio=6:attack=25:release=450:makeup=1[bd];")
        mixin.append("[bd]"); k += 1
    else:
        fc += "[vk]anullsink;"
    if sfx:
        ins += ["-i", sfx]
        fc += f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={sg}[s];"
        mixin.append("[s]"); k += 1
    fc += "".join(mixin) + f"amix=inputs={len(mixin)}:duration=first:normalize=0"
    if dur:
        fc += f",apad=whole_dur={dur},atrim=0:{dur}"
    fc += "[m]"
    tmp = tempfile.mktemp(suffix=".wav")
    run([FF, "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[m]", "-ar", "48000", "-c:a", "pcm_s16le", tmp])
    j = loudnorm_2pass(tmp, out, lufs)
    os.unlink(tmp)
    print(f"mix -> {out}  (was {j['input_i']} LUFS, now {lufs} LUFS, true peak <= -1 dB)")


# ------------------------------------------------------------------ finish (delivery)
def finish(a):
    src, dst = a[0], a[1]
    crf = opt(a, "--crf", 14, int)
    info = probe(src)
    rng = "pc" if info.get("pix_fmt", "").startswith("yuvj") or info.get("color_range") == "pc" else "tv"
    inm = info.get("color_space") if info.get("color_space") in ("bt709", "bt470bg", "smpte170m") else "bt601"
    inm = {"bt470bg": "bt601", "smpte170m": "bt601"}.get(inm, inm)
    vf = f"scale=in_range={rng}:out_range=tv:in_color_matrix={inm}:out_color_matrix=bt709,format=yuv420p"
    run([FF, "-v", "error", "-y", "-i", src, "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
         "-profile:v", "high", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-color_range", "tv", "-c:a", "copy", "-movflags", "+faststart", dst])
    o = probe(dst)
    strip = os.path.splitext(dst)[0] + "_strip.jpg"
    step = max(1, int(o["duration"] * o["fps"] / 8))
    run([FF, "-v", "error", "-y", "-i", dst, "-vf", f"select='not(mod(n\\,{step}))',scale=270:-2,tile=8x1",
         "-frames:v", "1", strip])
    print(f"finish -> {dst}  {o['width']}x{o['height']} {o['fps']}fps {o['duration']:.2f}s audio={o['has_audio']}  strip {strip}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("ingest", "plan", "cut", "frames", "cutout", "halftone", "mix", "finish"):
        print(__doc__); sys.exit(1)
    globals()[sys.argv[1]](sys.argv[2:])
