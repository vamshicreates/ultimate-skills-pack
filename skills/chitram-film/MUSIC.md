# MUSIC — choosing, fitting and cutting to music (for Reels/Shorts virality and every film)

Music is the fastest way to make an edit feel professional or amateur. This file is the music
supervisor + music editor: understand the video's concept, choose music that serves it (and the
platform), fit the track to the exact length, and cut the picture to the music. SOUND.md covers
SFX and the final mix; this file covers the score.

`$M` = `python $SKILL/audio/music.py`. You cannot listen: `analyse` + the sheet PNG are your ears.

---

## 0. THE LAW of music

1. **Concept first, track second.** Write the *music brief* (§1) before searching. A great track
   for the wrong feeling ruins a great edit.
2. **Voice wins.** Under a voiceover/talking head: instrumental only, no lead vocals, nothing busy
   in 1–4 kHz, ducked −10 to −16 dB (SOUND.md §5). Lyrics fight words.
3. **Cut to the music's structure, not just its beats.** Big changes on phrase starts (every 4/8
   bars), the reveal on the drop, the end on the music's real ending. Never let music just stop.
4. **The drop is the reveal.** Exactly one biggest musical moment = exactly one biggest visual moment.
5. **Legal first.** Never bake a copyrighted commercial song into the file. Trending/film songs are
   added *inside the Instagram app* (§4). Baked music must be licensed for the account type.
6. **Measure, then trust your eyes.** `analyse` gives BPM, bars, sections, drops; read the sheet
   PNG every time; fix the grid by hand if a section is mislabelled.

## 1. Understand the concept → write the music brief

Answer from the script/footage, in `brief.md`:

| Question | Examples of answers |
|---|---|
| **The feeling at the END** (what should the viewer feel when it finishes?) | inspired · curious · awe · trust · nostalgic · hyped · amused · tense → relieved |
| **The arc** | flat calm (explainer) · slow build → payoff (story, reveal) · high from frame 1 (hype, sport) · tension → release (thriller/trailer) · fun bounce (comedy) |
| **The job** | inform (music supports) · persuade (music lifts at the CTA) · entertain (music leads) |
| **Voice or no voice?** | VO/talking → instrumental bed, ducked · no voice → the music IS the voice: cut to it |
| **Pace** | calm 70–95 BPM · natural 95–115 · energetic 115–135 · hype 135–160 (half-time feel counts) |
| **Audience + culture** | Telugu/Indian audience → consider Tollywood BGM energy, folk hooks, Indian percussion; global tech → modern electronic |
| **The one drop moment** | the frame of the biggest reveal (product, result, logo, punchline) |
| **Platform plan** | trending audio added in-app · licensed track baked · original audio (§4) |

## 2. Concept → genre / mood map (starting points, not rules)

| Content | Feeling | Genre / sound | BPM | Notes |
|---|---|---|---|---|
| AI tool demo, tech explainer, SaaS | smart, modern, curious | minimal electronic, future garage, light synth pluck, lo-fi house | 100–122 | clean drums; drop on the "result" reveal |
| AI creative studio output reel (your page) | awe, "how?!" | cinematic hybrid (pulses + braams), dark synthwave, phonk for edgy | 90–140 | silence → drop on the first output frame |
| Breakdown / tutorial with VO | calm trust | lo-fi, soft piano + beat, ambient pulse | 75–95 | instrumental only, low mids carved |
| Founder / personal story | warm, inspiring | piano + strings swell, indie-folk guitar, Telugu melodic BGM | 70–100 | build to the payoff line, not before |
| Before/after, transformation | satisfying | beat-switch tracks (calm → drop), phonk, trap | 120–150 | the switch = the "after" |
| Fashion / luxury / product | confident, sleek | deep house, R&B instrumental, minimal techno | 115–125 | cut on the kick; slow-mo on the off-beat |
| Sports / gym / car | hype | phonk, drill, trailer hybrid, Tollywood mass BGM | 130–160 | velocity edit (§6), shake on 808 hits |
| Comedy / relatable | playful | quirky pizzicato, meme sounds, trending audio | any | timing of the punchline beats music choice |
| Trailer / film teaser | epic, tense | trailer hybrid: ostinato → braams → riser → silence → hit | 90–130 | SOUND.md stacks `trailer`, `blackout`, `tension_hit` |
| News / info (AI anchor) | serious, urgent | news pulse, ticking synth, low strings | 90–120 | music under the anchor at −16 dB |
| Nostalgia / memory | warm, wistful | lo-fi, vinyl, slowed + reverb, old Telugu melody vibe | 60–85 | grain + "faded-memory" grade (FX.grade) |

**Mood tells from the analysis:** major key + bright (> 2.5 kHz) + fast = happy/hype; minor key +
dark (< 1.5 kHz) = serious/tense/cinematic; slow + low energy range = calm. A big `drop_jump_db`
(> 8 dB) = a strong reveal track; a flat energy curve = a bed for voice.

## 3. Finding the track: the self-sourcing loop (internet only, every time)

The skill carries no music. For every job it researches what is trending NOW, then finds, downloads,
measures and ranks licence-safe tracks that fit the brief.

1. **The creator's own track** (or one they name) always wins. Analyse it and go to §5.
2. **Research the trend, live.** `python $SKILL/audio/source.py trends --region India --niche "<niche>"`
   prints the WebSearch queries; run them (newest sources first; trends die in days). Note in `brief.md`:
   sound + artist, rising/peak/decay, which section creators use, its feel/BPM, and whether the account
   type may use it. A trending song is used **in-app only** (§4), never baked.
3. **Find licence-safe music that fits the brief** (and, if a trend matters, *the same feel* as it):
   ```bash
   python $SKILL/audio/source.py music "dark cinematic trailer" --bpm 120 --mood dark --min 30           --to films/<n>/assets/music --n 6
   ```
   Searches Openverse (Jamendo + Wikimedia: CC BY / BY-SA / CC0 only), Mixkit (free licence) and, with
   `PIXABAY_KEY`, Pixabay; downloads the candidates, runs `music.py analyse` on each and writes
   `candidates.md` ranked by tempo fit, mood/mode, drop strength and length, with a sheet per track.
   Query with genre + mood + use ("phonk drift", "lofi chill study", "epic trailer hybrid", "indian
   percussion upbeat", "corporate tech minimal", "emotional piano strings").
4. **Choose by looking**, not by rank alone: read the top 2–3 sheets (drop where you need it? intro short
   enough? energy arc matches the story?). Check the licence fits the platform. Under a voiceover reject
   tracks with sung vocals (check the title/tags/description; when unsure, choose instrumental).
5. **AI-generated music** (when a connector exists, CONNECTORS.md): generate from the brief (genre, BPM,
   mood, "instrumental, no vocals", "drop at 0:12"); still `analyse` it, generators drift.
6. **Credits:** `<to>/CREDITS.txt` holds title, author, licence and URL of every downloaded track; put CC BY
   credits in the caption/description and the delivery note.

## 4. Instagram / Reels: what actually matters (2026)

- **Audio is a ranking input.** Instagram's ranking predictions include whether a viewer will tap
  through to the audio page, and every Reel using a sound is listed on that sound's page, so a
  rising sound can give a new account extra discovery. Whether trending audio itself boosts reach is
  contested: treat it as discovery, never as a substitute for the hook and watch time.
- **Finding trending audio:** Professional dashboard → *Trending audio* (up to ~50 tracks; US, mobile
  only), or the small ↗ arrow next to a sound name in the Reels feed. Jump on a *rising* sound
  within 1–2 days; skip sounds already in decay (flat growth, parodies). Trends often show up on
  TikTok 1–2 weeks earlier.
- **Account type changes the library.** Business accounts can only use the smaller Meta Sound
  Collection (commercially cleared, roughly 14k tracks); creator/personal accounts see the wider
  library for non-commercial use. A song being *available* in the app is not a licence. That
  licence does not travel to YouTube/LinkedIn/TikTok or paid ads.
- **Original audio:** posting your own sound (your VO, your mix) creates an "Original audio" page
  others can reuse, credited to you. For a creator/studio page, a recognisable signature sound (your
  intro hit, your VO line) compounds.
- **The practical workflow for trending sounds:**
  1. Get a guide copy of the sound's used section (the creator screen-records or downloads it for
     editing only). `$M analyse guide.m4a`.
  2. Build the cut to that grid (`fit --ending hard` with the exact section, or `cuts`).
  3. Deliver the MP4 with **no music** (VO/SFX only, or the guide muted) and a note:
     "In Instagram, add sound '<name>', start the clip at 0:14, Reels volume: music 30 %, original 100 %."
  4. If the creator wants a baked version for YouTube/other platforms: use a licensed track instead.
- **Telugu/Indian context:** film songs and folk hooks (e.g. Pushpa 2, Telangana folk tracks) drive
  huge reuse on Reels; Tamil/Telugu versions of big Hindi songs trend in parallel. These are label-
  owned: in-app only, never baked. Trial Reels (public accounts with 1,000+ followers, shown to
  non-followers only) are the clean way to A/B a trending sound vs original audio on the same edit.

## 5. Fit the track to the picture

```bash
$M analyse track.mp3                       # -> track.music.json + track.music_music.png  (READ the png)
$M fit track.mp3 --duration 30 --drop-at 12.4 [--drop 1] --out films/<name>/assets/music_fit.wav
#   drop of the music on film 12.4 s, splices only on downbeats (phrases when possible), loops a full
#   section if the track is short, ends on the track's real ending (--ending natural|fade|hard)
#   -> music_fit.wav + music_fit.json (film-time grid) + music_fit.beats.js (window.MUSIC) + sheet
$M cuts films/<name>/assets/music_fit.json --every bar --min 0.8      # cut list on the grid
```
Then in `mix.json`: `"music": {"file": "assets/music_fit.wav", "gain": .55, "duck_db": -12, "fade_in": .02, "fade_out": .3}`
(the fit already starts at film 0, so no `drop_track/drop_film`), and in the film page
`<script src="assets/music_fit.beats.js"></script>` → `FX.grid()` gives the beats, bars, phrases,
accents, drop and sections in **film time**.

Fit rules: start on a downbeat (or the first bar of the section you want); if the film opens before
the music can, the fit inserts silence (a cold open) — often stronger. Look at the fit sheet: every
splice should sit on a phrase line, and the ending should ring out, not stop.

## 6. Cutting picture to music (the editor's grammar)

| Music moment | Picture |
|---|---|
| **Downbeat (the "1")** | hard cuts, new shot, scene change |
| **Phrase start (every 4 bars)** | section change, new chapter, world switch, a bigger transition |
| **Beat (2, 3, 4)** | small accents: text pops, punch-ins, flashes; not every one |
| **Accent hits** (snare/808/hit, `accents`) | `FX.flash`, `FX.shake`, an SFX stack, a stamp of text |
| **Build** (rising energy before a drop) | tension: tighter shots, faster cuts (halve the interval), `FX.drift`, a riser SFX; can mute to near-silence 1 beat before the drop |
| **Drop** | THE reveal: `FX.zoomBlur`/`FX.whiteOut` + `FX.flash` + `FX.shake`, `stack:drop`/`stack:reveal`, the hero shot |
| **Break / breakdown** | breathe: slow-mo, longer holds, emotion, the key VO line |
| **Ending** | the logo/CTA lands on the last downbeat; hold ≥ 1.5 s of ring-out |

- **Rhythm is not a metronome.** Cutting only on every downbeat is dull: mix bar cuts with 2-bar
  holds, double-time cuts in the build, a held shot through a phrase. Break the pattern on purpose
  once per section.
- **Cut slightly early?** No: cut ON the beat frame (the grid is measured at the transient). If a cut
  feels late on a fast whip, start the motion 2–3 frames earlier so it *lands* on the beat.
- **Velocity edit (viral):** `FX.speedRamp` the footage — normal → slow-mo (0.2–0.35×) through the
  move → snap to 2–4× INTO the beat → normal; plus `FX.punch` on the landing. Best with phonk / trap /
  hard beats; use on 2–3 moments, not every shot.
- **Beat-synced photo/clip reveals:** `FX.beatCuts(tl, scenes, FX.grid().downbeats, {punch, flash})`.
- **Speech + music:** VO phrases start just after a downbeat; leave the drop free of words.
- **Shorts length:** cut the music edit to the platform length (Reels 7–30 s sweet spot, ≤ 90 s);
  loop-friendly endings (last bar flows into the first) raise replays.

## 7. Music QA checklist

- [ ] Music brief written; the chosen track's sheet read (BPM, key/mood, drops, sections fit the arc).
- [ ] Licence fits the account and every platform it will be posted to (or it's in-app only).
- [ ] Fit is the exact duration; splices sit on phrase/bar lines; the ending rings out.
- [ ] The drop lands on the biggest visual moment (± 1 frame); cuts sit on the grid.
- [ ] Under voice: instrumental, ducked, every word intelligible (transcribe the mix).
- [ ] Mix measured at −14 LUFS / −1 dBTP (SOUND.md §6).
- [ ] Delivery note says which music is baked, or exactly which in-app sound to add and where.
