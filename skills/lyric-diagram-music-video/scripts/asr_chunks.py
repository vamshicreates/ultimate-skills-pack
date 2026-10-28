"""Phrase-chunked Whisper pass for sung lyrics (timing, not text truth).
usage: python3 asr_chunks.py song.mp3 separated.wav out.json --model /path/to/faster-whisper-large-v3 --lang te [--start 0 --dur 9999]
separated.wav: from repet_separate.py (used only to find vocal-activity chunks)."""
import sys, json, argparse, subprocess, numpy as np
from faster_whisper import WhisperModel
ap = argparse.ArgumentParser(); ap.add_argument("song"); ap.add_argument("sep"); ap.add_argument("out")
ap.add_argument("--model", required=True); ap.add_argument("--lang", default=None)
ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float, default=9999)
ap.add_argument("--threads", type=int, default=2); a = ap.parse_args()
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-ss",str(a.start),"-t",str(a.dur),"-i",p,"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
sep, org = load(a.sep), load(a.song)
hop = 160; e = np.array([np.sqrt(np.mean(sep[i:i+hop*4]**2)) for i in range(0, len(sep)-hop*4, hop)])
db = 20*np.log10(e+1e-6); act = db > np.percentile(db, 55); t = np.arange(len(act))*0.01
chunks, s, last = [], None, None
for i, on in enumerate(act):
    if on:
        if s is None: s = t[i]
        last = t[i]
    if s is not None and (t[i]-last > 0.35 or t[i]-s > 9):
        if last-s > 0.6: chunks.append((max(0, s-0.15), last+0.2))
        s = None
m = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=a.threads)
out = []
for c0, c1 in chunks:
    seg = org[int(c0*16000):int(c1*16000)]
    r, info = m.transcribe(seg, language=a.lang, beam_size=5, condition_on_previous_text=False, temperature=[0, .3],
        no_repeat_ngram_size=3, repetition_penalty=1.2, word_timestamps=True)
    r = list(r)
    row = {"s": round(c0+a.start, 2), "e": round(c1+a.start, 2), "text": " ".join(x.text.strip() for x in r),
           "words": [[round(w.start+c0+a.start, 2), round(w.end+c0+a.start, 2), w.word] for x in r for w in (x.words or [])]}
    out.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
