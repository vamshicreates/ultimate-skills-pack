# SOUND — pro sound design for every film and edit (add-on)

Use this whenever a film or an edit gets SFX, music or a final mix: motion films (ENGINE), short-form
(SHORTFORM §8) and long-form YouTube (LONGFORM §10). Sound is half of "premium": the same picture
with sound landing on the frame feels twice as expensive. Badly placed sound feels cheap at once.

**Default policy first.** Many creators add their own music in the app at upload. If the user (or a
memory) says *VO only / no music / no SFX*, deliver the voice alone (loudness-normalised) and do
nothing below. When they ask for a sound pass, do it **fully**, to this standard.

`$A` = `python $SKILL/audio`. You cannot listen, so you **measure and look**: every tool below prints
or draws what you would otherwise hear.

---

## 0. THE LAW of sound (breaking any of these is a failed job)

1. **The voice is sacred.** No SFX lands on a stressed syllable. Music and SFX duck under speech.
   After the mix, transcribe it (faster-whisper): every word must survive.
2. **Every sound is motivated by something visible** (a cut, a move, a pop, a hit, a reveal) or by a
   deliberate story beat. A sound with no picture event is noise.
3. **The anchor lands on the frame.** A hit's *transient* lands on the cut/impact frame. A whoosh's
   *peak* lands on the swap frame (it starts before). A riser's *end* lands on the hit. Never place a
   file by its start: library files carry 0.1–8 s of padding.
4. **One sound family per film.** Pick one whoosh family, one impact family and one UI/pop family, and
   repeat them, varied. A different style of sound on every cut sounds like a sample pack demo.
5. **Never the same file twice in a row.** Rotate 3–6 variants of a role, or vary them by rate
   (0.94–1.06) and gain (±2 dB). Identical repeats are the #1 tell of amateur sound.
6. **Hierarchy:** voice > key SFX (the reveal) > music > secondary SFX > texture. Spend the biggest
   sound on the one showpiece moment. Cuts between talking-head takes get **no** whoosh.
7. **Level-match before you judge.** Louder always seems better. The library is level-matched
   (body RMS → −18 dBFS) so `gain_db` means the same for every file.
8. **Deliver to spec:** −14 LUFS integrated, true peak ≤ −1 dBTP for YouTube/Instagram/TikTok/X/
   LinkedIn. Measure it; never claim it.

## 1. Sourcing: the skill ships NO audio — it finds sounds on the internet per film

Every sound is fetched for the job from licence-safe free sources, saved inside the film's folder,
credited, measured and indexed as that film's library. Nothing is reused blindly from an old pack, and
the skill folder stays audio-free.

```bash
$A/source.py kits                                              # profiles and their roles
$A/source.py kit cinematic --to films/<n>/assets/sfx --lib <n>  # a whole kit: whoosh, impact, boom, riser, sub, shimmer, glitch
$A/source.py sfx "metal door slam" --to films/<n>/assets/sfx --lib <n> --n 4   # one specific sound
#   kits: cinematic · trailer · viral · tech · musicvideo · ui · nature  (combine: run several into the same folder)
```
- **Sources (keyless):** Openverse (indexes Freesound), Mixkit. Optional keys add more: `FREESOUND_API_KEY`
  (full Freesound search), `PIXABAY_KEY`. Results are licence-filtered: only **CC0, PDM, CC BY, CC BY-SA,
  Mixkit Free, Pixabay** (commercial use + modification allowed). NC/ND are rejected automatically.
- **Credits:** every file is logged in `<to>/CREDITS.txt` (title, author, licence, URL). CC BY / BY-SA
  credits go in the post caption or video description; list them in the delivery note.
- **Pick by ear-substitute:** after a fetch, `$A/sfx_lib.py roles` shows each role's best fits from the
  film's library; `$A/sfx_lib.py sheet <lib>:<id> ...` draws the candidates; fetch again with a better
  query if a role is weak ("deep", "metallic", "airy", "short", "reverse"...). Name your query after the
  *material and motion* you see on screen, not the effect name only.
- **One library per film:** `"sfx_lib": "<n>"` in `mix.json` (or `spot --lib <n>`) restricts picks to
  that film's sounds. The registry is `audio/libraries.json`; each film's index lives in its own folder.
- **Your own sounds** (a creator's pack, a purchased library): `$A/sfx_lib.py index "<folder>" --name <n>`
  works on any folder; packs inside one file are split into slices (`<n>:142.3`).

```bash
$A/sfx_lib.py roles                         # every edit role, its anchor and its 3 best fits (this film's library)
$A/sfx_lib.py pick whip --n 6 --seed 2      # candidates for one role (shuffled)
$A/sfx_lib.py search "deep metal impact" --max 2
$A/sfx_lib.py sheet <n>:12 <n>:5 --out sheet.png   # envelopes + onset/peak marks: READ the png
```

What the index measures per sound (seconds from the file start): `start/end` (audible region),
`onset` (transient arrival), `peak` (loudest 10 ms), `body_end`, `dur` (body, above peak −20 dB),
`shape` (hit · swell · riser · bed · multi), `rms_db`, `centroid` (Hz: bright vs dark), `sub` (share of
energy below 120 Hz), `tags`. If a sound's name is misleading, trust the measurements and the sheet.

## 2. Event → sound grammar (the spotting table)

| Picture event | Role | Anchor | Default gain | Notes |
|---|---|---|---|---|
| hard cut between worlds / blur-cut | `cut` | peak on cut frame | −8 dB | short (0.15–0.7 s body). Not on talking-head jump cuts |
| whip pan, push-through, zoom transition | `whip` | peak on swap frame | −6 | length ≈ the move; ends as the new shot settles |
| text / card / label slides in | `swoosh` | peak when it arrives | −12 | light and short; skip it when the voice is speaking a key word |
| sticker / card / bubble pops | `pop` | onset on scale-overshoot frame | −10 | quiet; every pop in a list gets a varied pop |
| cursor click, toggle, checkbox | `click` | onset on the click frame | −12 | one per real click in a screen recording |
| screen / data / typing feel | `ui` | onset | −14 | under the voice; texture, not music |
| glitch transition / error | `glitch` | onset on the first glitched frame | −10 | 1–2 per film max |
| key word slam, title, strike-through | `impact` | onset on the frame the word lands | −4 | add `synth:sub` −8 for weight |
| biggest reveal, logo, trailer moment | `boom` (+ `riser` before) | onset | −3 | the ONE showpiece; riser END on the same frame |
| build into a reveal | `riser` or reversed boom | end on the hit | −8 | `"reverse": true` turns any boom/whoosh into a riser |
| cut to black / big statement | `sub` / `synth:sub` | onset | −6 | felt more than heard; check on phone-size speakers |
| logo resolve, success, "idea" | `ding` | onset on the lock frame | −9 | bright: keep it short, low-pass if it stings |
| photo / freeze frame / screenshot | `shutter` | onset | −10 | pan bursts ±0.2–0.35 for a montage |
| page turn, collage paper | `page` | onset | −12 | collage / editorial styles only |
| emotional beat | `tonal` | onset | −8 | sparingly; never under a sad line as a cliché |
| tension | `tension` / `heartbeat` | end / onset | −10 | rolls end on the reveal |

Gains are relative to the level-matched sound; the master is normalised afterwards, so judge
*balance*, not absolute level. Under active speech, go 3–6 dB lower and high-pass at 120–150 Hz.

## 3. Sync: where exactly a sound goes

- **Hits:** transient on the frame. If it feels late, nudge **one frame early**; never more than
  2 frames late. Audio arriving early is forgiven far more than audio arriving late.
- **Whooshes:** three moments: *prepare* (rise as the move starts), *cross* (the peak at the fastest
  point or the cut) and *release* (the tail tells distance and stop). Peak on the cross; length ≈
  the move. A dissolve wants a swell, not a whoosh. A fast swipe wants a sharp, short whoosh.
- **Risers:** end exactly on the hit; cut the riser dead at the hit (`max_len`), let the boom take over.
- **J-cut the music:** chord changes / drops 0.3–1.0 s *before* the picture section changes; the
  drop itself on the biggest reveal (`drop_film`).
- **Pre-lap SFX:** the sound of the next scene may start 2–6 frames before the cut (a whoosh's
  prepare, a room tone); it pulls the eye across the cut.
- **Lists:** pops on each item's *spoken word*, not on a grid; vary each one.
- **Get times from the build, never by eye:** kit calls return times (`MK.*`, `SF.at`, `ED.*`
  word clock), `work/cuts.json` lists every join, `timeline.py` lists every clip edge.

## 4. Layering recipes (max 3–4 layers: transient · body · sub · air)

| Moment | Layers (anchor all to the same frame unless noted) |
|---|---|
| **Title slam** | `whip` peak 2 frames before → `impact` onset → `synth:sub` −8 → optional reverb tail of a `boom` −14 |
| **Showpiece reveal / logo** | reversed `boom` (`reverse`, end on frame) → `boom` onset −3 → `synth:sub` −8 → `ding` onset −12 on the lock |
| **World switch (collage)** | `cut` peak on frame → `page` onset −14, 1 frame after |
| **Card stack builds** | per card: `pop` onset (rotate variants, `rate` 0.96–1.04) + `swoosh` −14 peak 2 frames before |
| **Glitch transition** | `glitch` slice onset → `cut` peak on the clean frame |
| **Screen demo** | `click` per real click, `ui` −16 texture under typing, `whip` on zoom-ins |
| **Montage of photos** | `shutter` bursts panned L/R ±0.3, a `riser` under the montage ending on the next title |
| **Cut to black** | `synth:sub` onset + `boom` tail −10; then 0.3–0.6 s of real silence (silence is a sound) |

Shift secondary layers ±1–2 frames so they don't mask each other; the primary hit stays on the frame.

## 4b. Making it cinematic: stacks and processing

A single dry library file sounds like a sample pack. Trailer sound is **layered** (transient + body +
sub + air/tail), **placed in a space** (reverb), **wide** and **dense** (saturation), then **glued**.
`mixdown.py` does all four. The quickest route is a designed **stack**: one cue that expands into
processed layers (`python audio/sfx_lib.py stacks` lists them).

| Stack | Use on | Layers |
|---|---|---|
| `stack:hit` | key word, title slam | whip peak −40 ms → saturated impact + short hall → `synth:sub` |
| `stack:reveal` | showpiece, logo | reversed boom (riser) ending on t → boom + big hall, wide → long sub |
| `stack:trailer` | braam-style trailer hit | saturated boom + tonal impact in a cathedral → long sub |
| `stack:whoosh_hit` | a transition that lands on a hit | wide whoosh peak −30 ms → impact |
| `stack:transition` | big world change | heavy wide whoosh + low sub |
| `stack:cut` | snappy cut / world switch | short wide whoosh, a touch of plate |
| `stack:pop` | card/sticker pop | air swoosh → pop |
| `stack:glitch` | glitch transition | glitch slice → short whoosh |
| `stack:drop` | reinforce a music drop / beat switch | sub + low boom (40 Hz high-pass) |
| `stack:blackout` | cut to black, big statement | boom into a cathedral tail + sub, then silence |
| `stack:tension_hit` | riser into a hit | riser (end on t) → impact → sub |
| `stack:ui` · `stack:ding` | screen click · logo lock / success | click + soft UI · plate-reverbed ding, low-passed |

`{"t": 12.0, "sfx": "stack:reveal", "gain_db": -2}` (gain_db shifts the whole stack). In `events.json`
for `spot`: `{"t": 12.0, "stack": "reveal"}`.

Per-sound processing (any cue): `space` 0–1 = reverb send, `room` = `room` (.6 s) · `plate` (1.3 s,
bright) · `hall` (2.4 s) · `cathedral` (4.8 s); `width` 0–1 = stereo spread (mono-safe ≤ .6); `sat` 0–1 =
saturation (hits read on phone speakers); `hp` / `lp` Hz. Bus: `"sfx_glue": true` (3:1 glue compressor),
`"reverb_gain"`. Tails are high-passed at 180 Hz so reverbs never muddy the voice.

**See the result:** `python audio/sfx_lib.py spec assets/mix.wav --marks 3.2,7.5,12` draws a
spectrogram with your cut times as blue lines: every transient should sit on a line, tails should
fade cleanly, the sub should sit under the big moments only.

## 5. The mix (voice on top, always)

- **Voice:** gain 1.0, never re-timed, pitched or reverbed. `voice_clean` = 70 Hz high-pass only.
- **Music:** ×0.4–0.6, side-chain ducked −10 dB under the voice (attack 40 ms, release 280 ms).
  Long-form talking: duck deeper (−14 to −18) or leave music out between chapters.
- **SFX bus:** ×0.8, ducked −4 dB under speech (`sfx_duck_db`). High-pass non-sub SFX at 120–150 Hz
  (`hp`) when they sit under dialogue; low-pass (`lp` 6–9 kHz) for distance or to soften bright dings.
- **Pan:** centre for editorial sounds; ±0.2–0.35 only for movement that crosses the frame or for
  montage variety. Everything must still work in mono (phones).
- **Density:** short-form tight = SFX on every pop and world switch; documentary / interview = almost
  none (punch-ins are silent); luxury = a few soft swells; tech = clicks and UI texture. At most one
  heavy hit per 8–10 s; listener fatigue kills retention.
- **Silence:** a beat of near-silence before the payoff makes the payoff land. Duck everything for it.

## 6. Loudness and delivery specs

| Destination | Integrated | True peak | Notes |
|---|---|---|---|
| YouTube, Instagram Reels, TikTok, X, LinkedIn, Facebook | −14 LUFS | −1 dBTP | platforms normalise *down*; louder masters gain nothing and lose dynamics. LRA ≤ 11 |
| Podcast / voice-only | −16 LUFS | −1 dBTP | dialogue anchored ≈ −18 to −20 LUFS short-term |
| Broadcast (EBU R128 / ATSC A/85) | −23 / −24 LUFS | −1 / −2 dBTP | only when asked |
| Stem for an NLE / the user's own mix | `"lufs": null` | peak-safe | keep relative levels; label the stem |

Sample peak, RMS, true peak and LUFS are different measures; name the one you measured.

## 7. Workflow (spot → mix → verify)

```bash
# 0. fetch this film's sounds (§1), e.g. source.py kit cinematic --to films/<n>/assets/sfx --lib <n>
# 1. spot: write events from the build's real times
cat > films/<name>/events.json <<'EOF'
[{"t": 3.48, "role": "cut"}, {"t": 7.20, "role": "impact"}, {"t": 7.20, "sfx": "synth:sub", "gain_db": -8},
 {"t": 12.0, "role": "boom"}, {"t": 12.0, "role": "boom", "reverse": true}, {"t": 14.6, "role": "ding"}]
EOF
$A/sfx_lib.py spot films/<name>/events.json films/<name>/mix.json --lib <n>   # picks + rotates sounds, writes the "sfx" list
#    then add "voice"/"music" to mix.json (see mixdown.py docstring), and hand-tune gain_db/pan/rate
# 2. mix
$A/mixdown.py films/<name>/mix.json films/<name>/assets/mix.wav     # -> mix.wav + mix.wav.cues.txt
# 3. verify (you can't listen: measure and look)
cat films/<name>/assets/mix.wav.cues.txt                     # every anchor vs the cut list / kit times
$A/sfx_lib.py sheet <n>:12 <n>:5 --out sheet.png             # look at the sounds you chose
ffmpeg -i films/<name>/assets/mix.wav -af ebur128=peak=true -f null -   # I ≈ -14, TP ≤ -1
node $SKILL/bin/render.mjs films/<name> --from 6 --to 9 --draft          # the section around each big hit
```

`mixdown.py` cue fields: `t`, `sfx` (`<lib>:12` · `<lib>:142.3` · `role:whip` · `stack:hit` · `synth:sub[:len]` · a
path), `align` (`onset`/`hit`, `peak`, `end`, `start`), `gain_db`, `pan`, `rate`, `reverse`, `hp`,
`lp`, `fade_in`, `fade_out`, `max_len`, `seed`, `note`. Old `[t, file, gain, pan]` cues still work.
For an NLE hand-off, also export the SFX as clips (`tools/timeline/timeline.py add-mix`).

## 8. When the library lacks a sound

1. Fetch again with a sharper query (`source.py sfx "<material + motion>"`), use a slice, a reversed or re-pitched variant.
2. `tools/mixkit.py` (free licence, no credit) or `tools/commons.py --audio` (log CC credits).
3. A reversed / re-pitched library sound, a stack (§4b), or `synth:sub` (the old `synth.py` is retired: it sounded synthetic).
4. A connected generator (CONNECTORS.md), e.g. ElevenLabs text-to-SFX: prompt the *material and
   motion* ("short dry cloth whoosh, close, fast attack"), `duration` 0.5–30 s, `prompt_influence`
   ≈ 0.5 for literal sounds. Index the results like any library (`sfx_lib.py index <folder> --name <n>`).
Log every external file with its source and licence in the delivery note. Never use commercial
songs in the file; trending sounds are added in the app at upload.

## 9. Sound QA checklist

- [ ] Every cue in `cues.txt` sits on a real picture event (±1 frame); no anchor lands on a stressed syllable.
- [ ] No file repeats back-to-back; one family per role.
- [ ] One showpiece sound; booms ≤ 1 per 8–10 s.
- [ ] The voice transcribes cleanly from the final mix; music ducks under every line.
- [ ] Measured: integrated −14 LUFS (or the asked spec), true peak ≤ −1 dBTP.
- [ ] The draft render of each big moment was checked; the delivery note lists the sounds and sources.
