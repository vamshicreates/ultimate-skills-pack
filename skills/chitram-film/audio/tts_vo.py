"""Temporary (or final) TTS voiceover with WORD timings, tightened pauses, placed on the film timeline.
Outputs everything a word-locked film needs:
    <out>/vo.wav            full-film-length voice track
    <out>/timeline.json     {"duration", "words":[{line, w, t}]}   (film time of every word)
    <out>/timeline.js       window.VO = {...}  → load it in index.html; cut/caption on T(line, word)

    python audio/tts_vo.py lines.txt assets/vo [--voice te-IN-MohanNeural] [--rate +14%] [--tempo 1.14]
        [--start .35] [--gap .3] [--tail 2.0]

lines.txt: one spoken line per row (a beat of the film). Code-mix is fine.
Voices that worked:
  · Telugu + English code-mix (Tenglish): te-IN-MohanNeural (male) / te-IN-ShrutiNeural — the Telugu voice
    reads the English words acceptably; en-* voices SKIP Telugu script, never use them for Tenglish.
    Write the Telugu parts in Telugu script, the English parts in Latin script.
  · English: en-US-AndrewMultilingualNeural, en-US-AnaNeural (child), en-IN-PrabhatNeural.
Pace: TTS reads slowly and leaves ~1 s between sentences. Tighten = keep every word, shrink every
silence to <= 80 ms inside a phrase and <= 240 ms after a stop, then atempo 1.06–1.14 (no pitch change).
"..." in the text makes long pauses — write commas instead.
Needs: pip install edge-tts ; ffmpeg (FFMPEG env var or tools/bin).
"""
import argparse, asyncio, sys, json, os, shutil, subprocess
import numpy as np
from scipy.io import wavfile

ap = argparse.ArgumentParser()
ap.add_argument("lines"); ap.add_argument("out")
ap.add_argument("--voice", default="te-IN-MohanNeural"); ap.add_argument("--rate", default="+14%")
ap.add_argument("--tempo", type=float, default=1.14); ap.add_argument("--start", type=float, default=.35)
ap.add_argument("--gap", type=float, default=.3); ap.add_argument("--tail", type=float, default=2.0)
ap.add_argument("--in-gap", type=float, default=.08); ap.add_argument("--stop-gap", type=float, default=.24)
o = ap.parse_args()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ffbin import ffmpeg
FF = ffmpeg()
SR = 48000
LINES = [l.strip() for l in open(o.lines, encoding="utf-8") if l.strip()]
os.makedirs(o.out, exist_ok=True)


async def synth():
    import edge_tts
    meta = []
    for i, text in enumerate(LINES):
        c = edge_tts.Communicate(text, o.voice, rate=o.rate, boundary="WordBoundary")
        words = []
        with open(f"{o.out}/l{i}.mp3", "wb") as f:
            async for ch in c.stream():
                if ch["type"] == "audio": f.write(ch["data"])
                elif ch["type"] == "WordBoundary":
                    words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
        meta.append({"text": text, "words": words})
    return meta

meta = asyncio.run(synth())
out_words, chunks, t_film = [], [], o.start
for i, L in enumerate(meta):
    wav = f"{o.out}/l{i}.wav"
    subprocess.run([FF, "-y", "-v", "error", "-i", f"{o.out}/l{i}.mp3", "-af", f"atempo={o.tempo}", "-ar", str(SR), "-ac", "1", wav], check=True)
    x = wavfile.read(wav)[1].astype(np.float32) / 32768
    ws, pieces, tl = L["words"], [], 0.0
    t_film += o.gap if i else 0
    for k, w in enumerate(ws):
        a = w["t"] / o.tempo - (.03 if k == 0 else 0)
        nxt = ws[k + 1]["t"] / o.tempo if k + 1 < len(ws) else len(x) / SR
        end = (w["t"] + w["d"]) / o.tempo
        stop = k + 1 < len(ws) and any(p in L["text"].split(ws[k + 1]["w"])[0][-3:] for p in ".?!")
        keep = min(nxt - end, o.stop_gap if stop else o.in_gap) if k + 1 < len(ws) else min(nxt - end, .12)
        seg = x[int(max(a, 0) * SR): int((end + keep) * SR)]
        out_words.append({"line": i, "w": w["w"], "t": round(t_film + tl + (.03 if k == 0 else 0), 3)})
        pieces.append(seg); tl += len(seg) / SR
    y = np.concatenate(pieces); f = int(.004 * SR); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    chunks.append((t_film, y)); t_film += len(y) / SR
    print(f"line {i}: {len(y) / SR:5.2f}s ends {t_film:5.2f}")
total = round(t_film + o.tail, 2)
full = np.zeros(int(total * SR), np.float32)
for t0, y in chunks: s = int(t0 * SR); full[s:s + len(y)] += y
full /= max(1e-6, np.abs(full).max()) / .89
wavfile.write(f"{o.out}/vo.wav", SR, (full * 32767).astype(np.int16))
tlj = {"duration": total, "words": out_words}
json.dump(tlj, open(f"{o.out}/timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
open(f"{o.out}/timeline.js", "w", encoding="utf-8").write("window.VO=" + json.dumps(tlj, ensure_ascii=False) + ";\n")
print("film length", total, "→ set data-duration to this")
for i in range(len(meta)):
    print(i, " ".join(f'{k}:{w["w"]}' for k, w in enumerate(meta[i]["words"])))   # index map for T(line, k)
