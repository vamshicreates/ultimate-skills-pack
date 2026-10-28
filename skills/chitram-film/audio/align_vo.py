#!/usr/bin/env python3
"""
Split a voiceover into phrases so each phrase can be placed on its caption.

    python3 align_vo.py voiceover.m4a [--noise -40] [--gap 0.25] [--asr]

Prints JSON: [{"src": [start, end], "text": "..."}]  -> map each phrase to its caption time (ENGINE §10)
and add "at": <film time> to each (the time its caption appears).

--asr  also runs offline speech recognition (pip install pocketsphinx) to label each
       phrase. It is rough; use it only to identify which script line a phrase is.
Needs ffmpeg.
"""
import json, re, subprocess, sys, tempfile, os, wave


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(1)
    src = a[0]
    noise = a[a.index("--noise") + 1] if "--noise" in a else "-40"
    gap = a[a.index("--gap") + 1] if "--gap" in a else "0.25"
    r = subprocess.run(["ffmpeg", "-i", src, "-af", f"silencedetect=noise={noise}dB:d={gap}", "-f", "null", "-"], capture_output=True, text=True)
    hh, mm, ss = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr).groups()
    dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    edges, cur = [], 0.0
    for s, e in zip(starts, ends):
        if s - cur > 0.08: edges.append([round(cur, 3), round(s, 3)])
        cur = e
    if dur - cur > 0.08: edges.append([round(cur, 3), round(dur, 3)])
    out = [{"src": e, "dur": round(e[1] - e[0], 2), "text": ""} for e in edges]
    if "--asr" in a:
        try:
            from pocketsphinx import Decoder
            tmp = tempfile.mktemp(suffix=".wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", tmp], check=True)
            w = wave.open(tmp, "rb"); pcm = w.readframes(w.getnframes()); os.unlink(tmp)
            dec = Decoder(samprate=16000)
            for o in out:
                s, e = o["src"]
                dec.start_utt(); dec.process_raw(pcm[int(s * 16000) * 2:int(e * 16000) * 2], full_utt=True); dec.end_utt()
                h = dec.hyp(); o["text"] = h.hypstr if h else ""
        except ImportError:
            print("pocketsphinx not installed; skipping --asr", file=sys.stderr)
    print("[\n" + ",\n".join("  " + json.dumps(o) for o in out) + "\n]")


if __name__ == "__main__":
    main()
