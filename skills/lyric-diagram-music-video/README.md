# Lyric-Diagram Music Video — a Claude skill

Give Claude **an audio file** and **its lyric sheet**, and it makes a music video **entirely in code**. Each lyric's key word is taught like a science lesson, while its object animates as a diagram. Every scene cuts exactly on the song's beat.

> **You give: an audio file + a lyric sheet. Claude gives: the finished MP4.** Works for any language: Telugu, Hindi, Tamil, Kannada, English and more.

**The look:** near-black `#0a0a0b` · one accent colour of your choice (default orange `#ff5a1f`) · cream `#ede6da` paper-form scenes with a red stamp · thin HUD corners · tiny mono labels and IPA readouts · Anek (Telugu/Devanagari/Latin) + JetBrains Mono · soft glow · film grain.

**What ends up on screen**
- An opening single accent-coloured line (the script's head-stroke), which moves with the intro voice
- The song title hanging from that line, syllable by syllable, with pronunciation
- A chart of the alphabet's consonants (by where the mouth makes them), with the title's sounds lighting up on the beat
- One scene per lyric phrase: the key word glows large while a diagram shows its meaning. For example: distance becomes a measured line and a stamp; running becomes footprints on every beat; a moment becomes a stopwatch; a rainbow becomes a prism; searching becomes a radar; circling becomes an orbit
- Letter maths taken from the lyrics, such as `క + ్ + ష = క్ష`
- The lyrics as captions (script + romanised + English)
- A finale where the sung title fills with light in a burst

---

## 1. Install

### Claude (claude.ai / desktop app)
Settings → Capabilities → Skills → **Upload skill**, then pick this folder zipped (`lyric-diagram-music-video.zip`).

### Claude Code (on your computer)
```bash
git clone https://github.com/vamshicreates/lyric-diagram-music-video.git
mkdir -p ~/.claude/skills
cp -r lyric-diagram-music-video ~/.claude/skills/
```
Or keep one copy and link it:
```bash
ln -s "$(pwd)/lyric-diagram-music-video" ~/.claude/skills/lyric-diagram-music-video
```

### What your computer needs (for rendering)
- **ffmpeg**
- **Node 18+** and **Playwright / Chromium** (`npx playwright install chromium`)
- **Python 3** with `numpy scipy` (`pip install numpy scipy`)
- For automatic lyric timing: `pip install faster-whisper` and a Whisper model. **large-v3** is best for Indian languages. If you have used Whisper before, it is probably already in `~/.cache/huggingface/hub`.

---

## 2. Use it

1. Put the song in a folder, e.g. `~/Music Video/assets/MySong.mp3`.
2. Add the lyrics: either a `lyrics.txt` next to the song (one line per sung line), or paste them in the chat.
3. Open Claude with that folder connected (Claude Code: `cd` into the folder and run `claude`) and say:

```
Use the lyric-diagram-music-video skill.
Song: assets/MySong.mp3
Language: Telugu
Lyrics: (paste here, or "see assets/lyrics.txt")
Make a 1-minute sample first.
```

4. Claude first asks **one question: your accent colour** (orange, blue, magenta, lime, or any hex). Then it will:
   1. **Find the beat**: BPM, bars, phrases and the real hits (band entrance, stops, drops)
   2. **Time your lyrics**: Whisper finds *when* each of your lines is sung. Your text is always kept as the truth
   3. **Storyboard**: one scene per phrase, each cut on a downbeat, with a diagram chosen for that line's meaning
   4. **Build** the video as one HTML page (`renderFrame(t)`)
   5. **Check a still of every scene** and fix overlaps or clipping before rendering
   6. **Render** a 1920×1080, 30 fps MP4 with the song, and put it in your folder
5. Watch the sample, ask for changes ("slower cuts", "bigger lyrics", "different diagram for line 3"), then say **"finish the full song"**.

**No lyrics?** Just leave them out. Claude transcribes the song, marks each line high / medium / low confidence, shows only the confident lines on screen, and gives you `LYRICS-DRAFT.md` to correct.

### Prompt examples
- `Make a lyric-diagram video for assets/song.mp3, Telugu. Lyric sheet: assets/lyrics.txt. Sample first.`
- `Same style for this Hindi song, assets/raat.mp3. Use Anek Devanagari. Lyrics below:`
- `Finish the full song. Bring the consonant chart back on every chorus.`
- `Make it 9:16 for Reels, 1080×1920.`
- `Accent colour: #2f7bff.` (answer to Claude's first question)

---

## 3. How long it takes

| Job | Time (roughly) |
|---|---|
| 1-minute sample | 1.5–2 hours (lyric timing ~30 min, build ~45 min, still checks ~20 min, render ~15 min) |
| Full 4-minute song | about 3 hours |

The render runs at about 2 frames per second on a laptop. Sending your own lyrics saves the most time.

---

## 4. What's inside

```
lyric-diagram-music-video/
├── SKILL.md                         instructions Claude follows (style rules, workflow, diagram list)
├── README.md                        this file
├── reference/
│   ├── template.index.html          the working code template (edit its SONG block)
│   ├── lyrics.js                    lyric-timing format
│   └── beats.js                     beat-grid format
├── scripts/
│   ├── repet_separate.py            vocal separation (numpy/scipy only)
│   ├── asr_chunks.py                phrase-by-phrase Whisper with word times
│   └── envelopes.py                 per-frame audio levels + oscilloscope data
└── assets/fonts/
    ├── AnekTelugu-VF.ttf            Telugu display font (OFL)
    └── DejaVuSansMono.ttf           mono font with IPA symbols
```

Run the scripts yourself if you like:
```bash
python3 scripts/repet_separate.py song.mp3 vocals.wav 0 300
python3 scripts/asr_chunks.py song.mp3 vocals.wav timing.json --model ~/models/faster-whisper-large-v3 --lang te
python3 scripts/envelopes.py song.mp3 assets/env.js --dur 300
```

---

## 5. Tips
- **Your lyrics are the truth.** Whisper only finds the timing, because sung words under a loud band are often misheard.
- For other scripts, swap the font: Anek Devanagari (Hindi), Anek Tamil, Anek Kannada, Anek Bangla and so on, all free on Google Fonts.
- Keep paper-form scenes to 2–3 per minute. They work as the "breath" between dark scenes.
- Only one accent colour (the one you chose). If a scene needs a rainbow, draw it in ink with **one** ray in the accent.

## Credits & licence
Skill by **Vamshi Creates**. Fonts: Anek Telugu (SIL Open Font License), DejaVu Sans Mono (free licence). Use your own music or music you have rights to.
