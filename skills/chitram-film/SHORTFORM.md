# SHORTFORM — premium short-form content edits (add-on)

Use this for any **edit of real footage** meant for Reels, Shorts, TikTok, LinkedIn or X, such as a
founder talk, a podcast clip, a creator video, an interview, a UGC ad, a tutorial, a vlog, an event
recap or a product demo. The creator gives the footage. You edit it into a piece that looks like a
top studio cut it.

It works on any content, with or without a reference, in any edit style. The creator may supply the
assets, or you may have to get them yourself. The quality bar does not change in any of these cases.

`DIRECTOR.md`, `ENGINE.md` and `EXAMPLES.md` still apply. This file adds what is special about
editing footage: **understanding the talk, natural cuts, the edit plan, assets, captions and
audio**. The gold standard is EXAMPLES #11 (the AASTHI founder edit), and its code is in
`references/brief-aasthi-founder.md` (the build is archived on D:).

`$SF` = `python $SKILL/tools/shortform/sf.py`. `ffmpeg` must be on PATH, or set `FFMPEG` to the
ffmpeg executable (a folder also works).

---

## 0. THE LAW of a premium edit (breaking any of these is a failed job)

1. **Understand before you cut.** Read the whole transcript and look at every flip-book sheet
   before you decide anything. Know what the person is *arguing*, not only what they said.
2. **The voice is sacred.** Never re-time, pitch-shift, reverb or synth-process the speaker. Cuts
   happen only in pauses, never inside a word. Captions show only words that were spoken, spelled
   right. Brand names and people's names are corrected by hand.
3. **Cuts must be invisible or intentional.** Every join is either hidden (a cut in a pause plus a
   punch-in, a world switch or an insert) or it is a deliberate editorial beat. A jump cut is never
   left bare.
4. **Every second earns its place.** Something meaningful changes every 1.5–3 s: a caption page, a
   label, a punch-in, an insert or a world switch. Never add motion for its own sake. The eye rests
   on the face whenever the face is the point.
5. **One visual system per edit.** Pick 1 caption voice, 1–2 accent colours, 2–3 transition kinds
   and 1 showpiece moment, and repeat them. Using every trick once looks cheap.
6. **Never cover the face.** Captions and labels go in the empty space. Mark the face region with
   `data-clear="face"`. On 9:16, the top 12 % and bottom 20 % are platform UI, so keep them clear.
7. **Truth.** Claims, numbers and names come only from the footage or from the creator. Never
   invent a statistic, a testimonial, a UI label or a person. Stock material never stands in for
   the real product or the real people.
8. **Prove it.** Run `check.mjs --strict` clean, read the contact sheet, listen to every cut
   (`--from/--to`), and probe the final file. Say honestly what you changed from the brief.

---

## 1. Ingest: know the footage (always first)

```bash
$SF ingest footage.mp4 work/ --model small --prompt "AASTHI, NRIs, KYC, Vamshi"
```
This writes the following files. Read `transcript.txt` and every sheet.

| File | What it gives you |
|---|---|
| `probe.json` | size, fps, duration, audio, colour range |
| `words.json`, `transcript.txt` | every word with its start/end time and a confidence score. It is transcribed **chunk by chunk**, so retakes are not hidden |
| `energy.npy` | speech energy every 10 ms, from which pauses and cut points are found |
| `scenes.json` | existing hard cuts (a multi-camera source or an already-edited clip) |
| `faces.json` | the face box, the side of the frame that is empty, and whether the speaker moves |
| `sheets/` | flip-book sheets at 2 fps (12 s per sheet) that you look at |

Other inputs:
- **Several clips:** ingest each one. Pick the best take of each idea, then order them by the
  story.
- **Non-English speech** (Telugu, Hindi, Tamil and others): add `--lang te`/`hi`/`ta` or leave it
  on auto-detect. Captions stay in the native script, so load a Noto font for that script
  (`npm i @fontsource/noto-sans-telugu`, copy the woff2 file and add an `@font-face`). Check the
  glyphs in a snapshot. Use Whisper `medium` or `large-v3` for accents or noisy rooms.
- **Fix the transcript:** low-confidence words and proper nouns are corrected in `words.json`
  before planning. Whisper writes "ASTEE" for AASTHI, for example. Always pass the brand words
  with `--prompt`.

## 2. Understand the content (write this down in the edit plan)

Answer these six questions from the transcript and the sheets:

1. **Type:** founder or expert talk · podcast (1 or 2 speakers) · creator education · story or
   vlog · interview · UGC or ad · tutorial or screen recording · product demo · event.
2. **Spine:** the hook line, the problem, the turn, the proof points or list, the payoff, and the
   call to action. Write each one as the *exact spoken words* with their time codes.
3. **Structures in the speech:** lists ("four things"), numbers, contrasts ("not X, but Y"),
   questions, a named product or brand, before/after, places, time. **Each one is an opportunity
   for a graphic.**
4. **Emphasis words:** 1 per sentence at most. These are the words the speaker leans on
   (listen for them), the payoff noun, and numbers.
5. **Energy and register:** calm and trustworthy, confident and punchy, warm and personal, or
   luxurious. This decides the style (§5) and the pace (§3).
6. **Platform and length:** 20–45 s is ideal and 60 s is the maximum for Reels/Shorts, unless the
   creator says otherwise. If the talk runs long, cut whole ideas. Never speed up the voice.

**Hook lift:** if the strongest line comes late, you *may* open on it as a cold open, then return
to the start. This is permitted only when the meaning stays true, and you must state it in the
delivery note. Ask first if you are in collaborative mode.

## 3. The natural cut (the rough cut)

```bash
$SF plan work/ --pace natural          # tight = energetic creators, relaxed = luxury / emotional
#   -> read work/edl.txt, fix work/edl.json by hand if needed
$SF cut footage.mp4 work/ --size 1080x1920 --fps 25 --reframe face
#   -> work/master.mp4 + master.wav (the new timeline), master_words.json + words.js,
#      cuts.json + cuts.js (every join, with a jump score)
```

What `plan` does, and why the cuts feel natural:
- **The audio decides where pauses are,** not the ASR. Word timestamps drift by ±100 ms, so pauses
  come from the 10 ms speech energy.
- **Pauses are shortened, not removed.** A pause is kept at about 0.42 s after a sentence,
  0.26 s after a comma and 0.18 s mid-phrase (natural pace). Silence to zero sounds robotic. The
  kept time is split between the tail of the last syllable and the breath before the next word.
- **Every edge sits at the quietest 10 ms** near it, snapped to the frame grid, so picture and
  sound cut on the same instant. There is also a 12 ms audio fade at each join, so there are no
  clicks.
- **Fillers go:** um, uh, erm and hmm. Soft fillers (like, so, basically, you know) are only
  *flagged*, because they are often meaningful. Judge them by ear.
- **False starts go, whole:** when a phrase is restarted, the cut removes the attempt from its
  start up to the start of the retake. Two takes are never spliced mid-sentence.
- Keep segments shorter than 0.3 s that contain no word are dropped, because they flash on screen.

Your judgement on top of the tool:
- **Read `edl.txt` before cutting.** Keep a pause the speaker uses for effect, such as the beat
  before the punchline. Put it back by merging keep segments in `edl.json`.
- **Never cut mid-gesture if you can avoid it.** When a join lands on a big hand move, shift it
  within the pause.
- **Single-camera footage means every join is a jump cut.** `cuts.json` gives a `jump` score.
  Cover every join where `visible` is true, and every join inside a sentence, with one of these:
  1. a **punch-in** on the cut frame, alternating 1.00 ↔ 1.08 (tighter shots 1.00 ↔ 1.12)
     (`SF.punches`). Never zoom twice to the same scale in a row;
  2. a **world switch** or **insert** that starts on or just before the join (a graphic beat,
     B-roll, a screen or a product);
  3. for two-camera footage, **cut to the other angle.**
- **Reframing to 9:16** uses one static, face-centred crop. Premium edits do not wobble. If the
  subject walks, split the crops per segment instead of tracking frame by frame.
- **The master is the timeline:** film time = master time. Captions, labels and SFX are all timed
  from `master_words.json` (`SF.at(WORDS.words, "job")`).

## 4. The edit plan: turn the talk into beats

Write this plan before any code, in `brief.md`, using the house Production Prompt format
(DIRECTOR §9) followed by a Build Sheet. EXAMPLES #11 shows the level of detail required.

**Beat rules**
- One beat = one idea = usually one sentence (2–8 s). A beat starts on the first word of its
  sentence, and a world switch lands 0.1 s before that word.
- **Hook (0–3 s):** the first frame already moves. The first spoken line is on screen as it is
  said, plus a name tag or a big label. Never open on a logo or a title card.
- **Map speech structures to graphics:**

| The speaker says | The edit shows |
|---|---|
| a list ("4 things", "first… second…") | cards or a checklist that **builds up** item by item, each on its spoken word |
| a number or statistic | a giant number behind the cut-out, or a counter. Use only the spoken number |
| a contrast ("not access, it's distance") | the first word gets struck through, then the second word is emphasised |
| a place, distance or journey | a map arc with pins that draws on |
| a question | a question-stack label, with a beat of silence kept after it |
| the product or brand | a logo badge, a real product screen in a browser or phone card, or the website |
| a process | numbered steps, or a line that connects icons |
| emotion or a story | stay on the face, slow push-in, minimal type (the restraint *is* the premium look) |
| the call to action | the end card: payoff line, then logo lock-up, held ≥ 1.5 s |

- **Two worlds, alternating:** (A) the real footage with captions and labels in the empty space,
  and (B) a graphic world where the speaker becomes a cut-out (collage, brand colour or blur
  plate). Put the problem on footage and the answers and lists on graphics. Switch worlds only on
  a sentence boundary.
- **Rhythm:** declare it before building (e.g. `hook·pop — BLUR — stack — BLUR — cards — WHIP —
  logo — hold`). The energy rises to **one** showpiece transition at 55–70 % (a whip or light
  streak into the product reveal), then settles into trust.
- **Pace by register:** tight means a new event every 0.8–1.5 s. Natural means every 1.5–3 s.
  Relaxed or luxury means every 3–5 s, with slow dissolves and a lot of air.

## 5. Style: from a reference, or chosen for the content

**With a reference edit:** watch it frame by frame (DIRECTOR §3). Write the Shot Log and the Style
DNA (palette, textures, the 3 type voices, the motion numbers, the transition inventory and the
layout rules). Then **keep its grammar and re-colour it** to the creator's brand. Never copy its
content, people or logos. `references/EDIT-LEARNS-aasthi-founder.md` is a complete study
of this kind. `references/STYLE-STUDIES.md` holds two more house references: **Gold Premium Talking
Head** (gold two-tier captions, gold UI beside the head, film-burn cuts, cream thought cards) and **Minimal Kinetic
Green** (faceless white/green kinetic type) — when the user says "my style" / "gold edit" / "green minimal", use these.

**Without a reference:** pick ONE house style from the content type and register. Do not mix
them.

| Style | Best for | System |
|---|---|---|
| **Editorial Collage** | founders, explainers, podcasts with lists | brand-colour grid paper + grain, sticker cut-out (16 px paper outline), paper labels in Anton caps, cream cards with line icons, blur-through-cuts, one whip. Captions: `label`, or hand-placed label stacks |
| **Clean Documentary** | thoughtful talks, interviews, stories, finance or health | footage-led, film-soft grade, `clean` captions (Inter 600, inactive words at 62 %), lower-third name tag, punch-ins, slow push, dissolves or fades only, a serif pull-quote for one line |
| **Bold Creator** | high-energy education, sales, fitness | `bold` captions (Anton 104 px, active word in the accent colour), tight pace, punch-ins on emphasis, B-roll pops with hard cuts, SFX on every pop. Keep it premium: 1 accent colour, no emojis, no rainbow words |
| **Luxury Serif** | fashion, jewellery, real estate, hospitality, food | `serif` captions (Instrument Serif italic), warm grade, letterboxed inserts, slow dissolves, lots of negative space, a gold hairline rule, relaxed pace |
| **Tech Product** | SaaS, apps, AI tools, tutorials | `karaoke` captions (a pill behind the active word), screen in a device or browser card, cursor zoom callouts, glass UI cards, a grid background world, clean whooshes |
| **Story Doc** | case studies, journeys, events | lower thirds, dated chapter cards, halftone archival photos (`$SF halftone`), map lines, dissolves, restrained music |

Whichever style you pick, write its exact tokens (hex values, fonts, sizes, the easing, and the
transition list) into the plan. Brand colours come from the creator's logo, site or deck
(`prep_image.py palette`).

## 6. Assets: given, derived, fetched or drawn

Make an **asset list** in `brief.md` with one row per asset: what it is, where it comes from, and
its licence. Fill it in this priority order:

1. **Given by the creator:** logo, product screens, photos, B-roll, brand guide, music. Always
   use these first, and never alter a logo.
2. **Derived from the footage:** sticker cut-outs (`$SF cutout`), halftone or line-screen
   versions (`$SF halftone`), freeze frames, a blurred plate of the room (a copy of the footage
   with `filter: blur()`).
3. **From the creator's own public presence:** the logo and product screens from their website.
   Screenshot the real page in the browser, then crop or unwarp it (`prep_image.py`). Name the
   URL in the asset list.
4. **Drawn in code (the preferred way to fill gaps):** line icons as inline SVG, maps and arcs,
   charts from spoken numbers, UI rebuilt in HTML (ENGINE 6.13), grid, grain and gradients. These
   are always on-brand and licence-free.
5. **Free-licence stock** (Pexels, Unsplash, Pixabay, Mixkit), used only for generic B-roll or
   textures. **Ask the creator before downloading**, name the file, source and licence, and never
   use stock for the product, the team or customers.
6. **Music:** the creator's track, or a licensed track chosen and fitted with MUSIC.md (`audio/music.py fit`). Never bake commercial songs (MUSIC.md §4).

If a needed asset is missing and cannot be made truthfully (a customer logo, a real screenshot of
a feature), **ask for it** or design the beat without it. Never fake it.

Prepare the master and the cut-outs:
```bash
$SF frames work/master.mp4 films/<name>/assets/clip          # JPG sequence, q1, numbered from 0
$SF cutout films/<name>/assets/clip films/<name>/assets/cut --ranges 105-180,337-549 \
    --outline 16 --color F7F1EC [--key-dark-bottom 48]         # only the frames of graphic windows
$SF halftone photo.png assets/photo_ht.png --mode dot|line --cell 9 [--paper F7F1EC]
```
Cut-out lessons (learned in production):
- matte only the frame ranges you use (≈0.75 s/frame on a CPU);
- the matte keeps dark sofas, so key them with `--key-dark-bottom`;
- the ragged bottom edge goes off-frame, so shift the cut-out down 90–100 px;
- a world switch works best when the cut-out starts at scale 1 in the same place as the footage
  and then shrinks, so the room seems to vanish around the speaker.

## 7. Build (ENGINE rules, short-form kit)

```bash
node $SKILL/bin/init.mjs films/<name> --template shortform --size 1080x1920 --fps 25 \
     --duration <master + 1.5..2 s end hold> --frames <N> --face <x,y,w,h from faces.json>
cp work/words.js work/cuts.js films/<name>/assets/
```
The template has the footage world (`#footCam` with the image sequence and the face `data-clear`),
the graphic world (brand grid), `#caps` and `#fx`, and it loads `engine/shortform-kit.js` +
`engine/shortform.css`.

| SF call | Use |
|---|---|
| `SF.at(W, "four things")` | time of a spoken word or phrase (`{end:true}` gives its end, `{nth:1}` the 2nd match) |
| `SF.captions(tl, W, {style, maxWords, emphasis, skip})` | synced caption pages, with the active word highlighted. `skip` = graphic windows that carry their own text |
| `SF.pop(tl, sel, t, {rot})` | a sticker label or card pops in with back-out overshoot on its word (≈0.3 s) |
| `SF.typeOn(tl, sel, t)` | a spoken line types on per letter, rising and unblurring |
| `SF.blurCut(tl, T, out, in)` | world switch: 0.12 s blur out, cut, 0.22 s blur in |
| `SF.punches(tl, cam, CUTS)` / `SF.punch` | jump-cut cover / a punch-in on an emphasis word |
| `SF.push(tl, cam, t0, t1)` | a slow push through a long beat |
| `MK.whip`, `MK.lineDraw`, `MK.blurOut`, `MK.dim` | the showpiece whip, map arcs and ticks, exits |

Craft rules:
- **Captions:** there is one caption system for the whole edit. Captions sit in the chest band
  (`--cap-top` ≈ 1250–1350 px at 1920 tall) or the empty side, and never on the face. Use
  `maxWords` 2–3 for 9:16, and inactive words dimmed rather than hidden. Where a beat shows its
  own labels of the same words, `skip` that window: text on screen twice is noise.
- **Brand casing survives uppercase styles.** Write `NRI<span class="keep">s</span>`, and never
  let AASTHI become Aasthi.
- **Text behind the subject** (a giant word behind the cut-out) is placed so the head overlaps
  only the bottom of the letters. Verify it on a snapshot.
- **The end card** holds for at least 1.5 s after the last word, with the logo sharp and the
  tagline readable. If the footage ends first, the cut-out holds its last frame.
- Grain, grid and background sit on one layer across beats, so nothing jumps at the cuts.

## 8. Audio: the voice on top, always

**Real SFX, placed by anchor:** fetch this film's sounds (`audio/source.py kit`) and follow SOUND.md (§2 grammar, §4 layers, §7
spot → mixdown). Feed `spot` from `work/cuts.json` (world switches) and the `SF.*` call times (pops,
punch-ins, blur-cuts); `mixdown.py` then takes `"voice": "work/master.wav"`, ducks music and SFX
under it and normalises to −14 LUFS. Music: choose and fit it with MUSIC.md (`music.py fit` → `music_fit.wav`).

```bash
python3 $SKILL/audio/music.py fit track.mp3 --duration <d> --drop-at <reveal> --out work/bed.wav   # music edit
python3 $SKILL/audio/mixdown.py films/<name>/sfx.json work/sfx.wav   # SFX stem: {"lufs": null, "sfx": [...]}
$SF mix --voice work/master.wav --bed work/bed.wav --sfx work/sfx.wav \
        --out films/<name>/assets/final_audio.wav --duration <film duration> [--clean]
```
- The voice is untouched (gain 1.0). `--clean` adds only a 70 Hz high-pass filter and a
  de-click. The bed sits at ×0.22 and is **side-chain ducked** under the voice. SFX sit at ×0.55.
  The mix is two-pass loudness-normalised to −14 LUFS with a true peak of −1 dB.
- SFX: a soft pop on each label or card, a whoosh on each world switch (peaking on the cut
  frame), a whip whoosh, a chime on the logo, and a riser into the payoff. Keep SFX quiet under
  speech, and never let one land on top of a stressed syllable.
- Change chords at beat starts, 0.3 s early (J-cut feel). Skip the pulse during the whip, and
  fade out over the end hold.

## 9. QA and delivery

```bash
node $SKILL/bin/check.mjs films/<name> --strict
node $SKILL/bin/render.mjs films/<name> --at scenes           # contact sheet: read it
node $SKILL/bin/render.mjs films/<name> --from 9 --to 15 --draft    # listen across the joins
node $SKILL/bin/render.mjs films/<name> --out films/<name>/out/raw.mp4 --crf 14
$SF finish films/<name>/out/raw.mp4 films/<name>/out/<name>.mp4     # BT.709 standard range + strip
```

The short-form checklist:
- [ ] The first frame moves, and the hook line is on screen by 0.5 s.
- [ ] No bare jump cut. Every join is hidden or intentional. No click and no clipped syllable at
      any join.
- [ ] Every caption matches the audio word for word, the brand is spelled right, and nothing
      covers the face.
- [ ] Every label or card lands on its spoken word (±2 frames).
- [ ] There is 1 showpiece transition and 2–3 transition kinds in total.
- [ ] Text stays out of the top 12 % and bottom 20 %.
- [ ] Loudness is ≈ −14 LUFS and the voice sits clearly above the music.
- [ ] The end card holds ≥ 1.5 s. The file is 1080×1920, 25/30 fps, H.264 + AAC, BT.709.

The delivery note gives: the file, its duration and resolution; what was cut (seconds removed,
fillers, false starts); the style and why it was chosen; the asset list with sources; and any
deviation (a hook lift, a pause kept on purpose).

## 10. Edits to an existing short-form edit

Follow ENGINE §E (surgical changes). Re-timing requests ("tighter", "keep that pause") change
`edl.json`, then re-run `cut`. **Everything timed from `SF.at()` follows automatically.** Times
written by hand must be shifted by the change in duration before that point, and the change must
be stated.
