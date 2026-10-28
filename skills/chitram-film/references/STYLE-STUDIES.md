# Style studies: two reference edits, reverse-engineered

Two 9:16 references studied frame by frame (4 fps flipbooks + 5 fps zoomed crops + full-size detail
frames, colours sampled from pixels). Each one gets a Shot Log, a Style DNA, the exact build recipe
for this engine, and a reusable prompt template.

| Study | Source | Use it for |
|---|---|---|
| **A · Gold Premium Talking Head** | `Downloads/If you want your talking head video to bring in organic reach….mp4` — ONLY the right-hand "My edit" panel (the "$5 edit" panel, grid paper, "follow for more" are the promo wrapper; ignore them) | editing a person talking to camera: realtor, coach, founder, finance, explainer |
| **B · Minimal Kinetic Green** | `Downloads/Faceless video edit ⚡️Minimal visuals. Maximum impact….mp4` | faceless voice-over explainers, brand/marketing ideas, "carousel as video", no footage |

Both are what the client means by "this style". Keep their grammar; re-colour to the client's brand
only if asked (A's gold and B's green ARE the look; default to them).

---

## A · Gold Premium Talking Head ("My edit" panel)

**Specs of the panel:** 23.1 s, 30 fps, source 9:16, the panel is a rounded-corner (≈ 22 px at 1080w)
card. One speaker, locked-off camera, mid shot at a desk; beige wall, wood table, warm practical light.
The edit makes a $5 static talking head look premium with **four layers on top of the footage**:
(1) two-tier captions with a gold hero word, (2) gold 3D-ish graphics that pop beside the head,
(3) full-frame cutaway scenes (cream type card, grey 3D studio, stock B-roll), (4) punch-in/out
reframes + film-burn / bloom transitions. Something new appears every 0.4–0.8 s.

### A.1 Shot Log

| # | time (s) | frame / subject | camera / motion | type & graphics | in → out |
|---|---|---|---|---|---|
| 1 | 0.0–0.2 | talking head, wide-mid, hands clasped | locked | — | — |
| 2 | 0.2–0.6 | same | locked | 2-tier caption at chest: small white "What's the" + big gold **Difference** | blur-in → blur-dissolve out |
| 3 | 0.6–1.6 | **punch-in 115 %**, speaker right of centre | hard punch | bronze frame card (cream inner, flat illustration of house inspection) pops top-left beside head, 0.6→1.0 scale back-out; label "Home Inspection" types on L→R in the card footer | — → card slides out right |
| 4 | 1.6–2.3 | punch-in, speaker left | hard reframe (mirror side) | card enters from right: "Home Appraisal" (blue 3D house + magnifier) | — → film burn |
| 5 | 2.3–2.5 | **film-burn / light-leak** rising from bottom: orange-gold glow + dust particles dissolving the frame | — | — | burn → wide |
| 6 | 2.5–3.0 | wide | locked | "When you get on" small → **agreement** gold, words fade in one by one | — |
| 7 | 3.0–3.4 | punch-in 120 % | hard punch | top-left 2-tier: "on a" + gold **property** (left aligned, beside head) | **zoom-blur** (defocus pull, 3–4 f) |
| 8 | 3.5–4.7 | wide | locked | small "you get your offer"; a **gold bevelled bar wipes L→R** (0.3 s) then white bold **Accepted** appears in it (badge/stamp) | — |
| 9 | 4.7–4.9 | **white bloom** — soft white circle grows from centre over his chest to fill frame | — | — | bloom → cream card |
| 10 | 5.0–6.4 | **cream card** full panel: gradient #FAF4E1 (top) → #FBF9F7 (bottom) | locked | small black sans, word-by-word fade (prev words solid, new word grey→black): "You have the ability" / "to have your own" | cut |
| 11 | 6.5–7.3 | cream card | locked | **3D render** (magnifier over cut-away house) pops 0.8→1.0; above it a gold pill grows from a 20 px dash → full width (0.3 s), then "Home Inspection" white text fades in | cut to footage |
| 12 | 7.3–8.8 | wide | locked | plain subtitles only, 1–2 words, small white, centred at chest: "And what" · "that means" · "is that" · "you're going" · "to hire" | cut |
| 13 | 8.8–9.9 | **stock B-roll** full panel: two inspectors with hard hats; background desaturated grey, people in colour, dark vignette | slow push | top: small "your own" + bold white caps **HOME**, then big gold **Inspector** under it | cut |
| 14 | 10.0–11.2 | punch-in | locked | **UI toggle chips** right of head: white dot appears → pill extends right → label: orange pill "Heating", then blue pill "Cooling" (0.4 s apart) | cut |
| 15 | 11.3–14.6 | wide | locked | **5 gold circle icons** (house, tools, shower, bath, washer) arc over his head like a halo, each pops from a dot (stagger 0.05 s); caption "make sure things are" + gold **functioning right.** (letters write on L→R) | film burn |
| 16 | 14.6–14.8 | film burn #2 (same as 5) | — | — | burn |
| 17 | 14.8–16.0 | wide | locked | subtitles: "an appraisal is," · "on the other" · "hand, is" | cut |
| 18 | 16.2–18.3 | **grey 3D studio**: white classical **BANK** building, diagonal window-light shafts across grey floor | locked; light shafts static | black small sans top "when the bank sends" (word fade); a **businessman cut-out walks forward out of the bank** (fades in from 0 → 100 % while walking) ; "their own representatives" | cut |
| 19 | 18.4–19.7 | wide | locked | "making sure that the" + gold **property** | — |
| 20 | 19.8–21.4 | wide | locked | **gold number counter** $45 362 → $95 992 rolling, growing 0.8→1.2; a **dashed white selection box** (Figma bounding box) appears round it; 3D $100 bills fly/tumble past the lens top→bottom | bills clear |
| 21 | 21.6–23.1 | punch-in | locked | gold coin-badge icon (3 coloured houses) pops above caption "other homes in their" + gold **neighbourhood** | end |

**Rhythm:** `cap · CARD·card · BURN · cap · punch · ZBLUR · BADGE · BLOOM · cream-type · 3D+pill · subs · BROLL · chips · HALO+cap · BURN · subs · 3D-SCENE · cap · COUNTER+money · badge`
Average beat ≈ 1.1 s. Framing changes (punch / wide / cutaway) every 1–2 s, never > 2.2 s on one framing.

### A.2 Style DNA

```
Structure:    hook question → definition graphics → full-screen idea card → B-roll proof → metaphor scene → money → payoff word
Rhythm:       0.4–0.8 s between new elements; framing change every 1–2 s; 21 beats / 23 s
Camera:       one locked talking head made dynamic ONLY by punch-ins (100 % ↔ 115–120 %), reframing the speaker left/right
              of centre to make room for graphics on the other side
Transitions:  hard cut (default) · film-burn light leak ×2 (gold/orange, rising from bottom, with dust) · white bloom → cream ×1 ·
              zoom-blur defocus ×1
Type:         Poppins. Two tiers: setup words small white Poppins 500 (≈ 3 % of frame h) over the PAYOFF word in Poppins 700
              (≈ 6.5 % h) filled with a gold gradient + soft drop shadow. Payoff words: Difference, agreement, property,
              Accepted, Inspector, functioning right, neighbourhood. Plain subtitle mode between hero words: small white,
              1–3 words, centred at chest height (≈ 52 % down).
              On cream/grey cards: black Poppins 400, word-by-word (new word fades grey → black).
Palette:      footage warm beige (#CAB7B1 wall, wood #B0653A) · gold gradient #F0D088 → #D8A880 → #B08040 (text, bars, icons) ·
              cream card #FAF4E1 → #FBF9F7 · grey studio #8C8C8C / #F2F2F2 · accent chips orange #E8955A, blue #5AA7E0 · white
Graphics:     gold-bevelled UI: rounded bars, pills, circle badges with inner glow + 1 px darker gold rim + drop shadow;
              3D renders (magnifier house, bank, money) — clay/Blender-style, soft studio light; flat illustrations framed in a
              bronze card; stock B-roll with grey-desat background
Signature:    1) the gold payoff word under a small white setup line  2) gold UI (bar-then-word "Accepted", growing pill,
              icon halo round the head)  3) film-burn light-leak transitions  4) cream full-screen "thought card"
Density:      speaker + ≤ 1 graphic group + 1 caption; graphics sit BESIDE the head (never over the face); caption at chest
Sound (inferred, not heard): whoosh on each card, pop/click on chips & icons, riser into burns, cash/coin SFX on the counter,
              soft bed under voice
```

### A.3 How to build it in this engine (SHORTFORM + kits)

| Move | Build |
|---|---|
| two-tier gold caption | `SF.captions` custom style `goldtier`: `.setup{font:500 34px Poppins;color:#fff}` `.hero{font:700 72px/0.95 Poppins;background:linear-gradient(180deg,#F6DE9A,#D8A86A 55%,#B07E3E);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 3px 6px rgba(0,0,0,.35))}`; hero word enters `blur(8px)→0, opacity 0→1, y +10→0` 0.25 s power3.out; whole stack exits blur-dissolve 0.2 s |
| letter write-on (functioning right.) | `MK.typewriter` / clip-path inset(0 100% 0 0)→inset(0) 0.4 s, linear |
| punch-in / reframe | `SF.punch` 1.0→1.15 (hard, 0 f) with x offset ±8 % so the face sits on one third and graphics take the other |
| gold card pop | `MK.popIn` scale 0.6→1.0 back.out(1.6) 0.3 s, from the side of the head; exit x +40 px + fade 0.2 s |
| gold bar → word (Accepted) | bar `scaleX 0→1` transform-origin left 0.3 s power2.out, then text `MK.fadeIn` 0.15 s; bar = linear-gradient(#D9B46A,#A87838) + inset 0 1px 0 rgba(255,255,255,.5) + 2 px #8A6430 border, radius 6 px |
| growing pill | width 20 px → auto 0.3 s back.out, label fades in after 0.1 s; chips: white dot `scale 0→1` then pill extends |
| icon halo | 5 circles (gold gradient, white line icon) on an arc 110° above the head, `MK.popIn` from 0 stagger 0.05 s; idle `MK.breathe` 2 % |
| number counter | GSAP tween on an object `{v:45362}` → 95992, 1.4 s power1.out, `textContent=Math.round(v)`, scale 0.8→1.2; dashed box = 2 px dashed #fff rect `opacity 0→1` around it |
| money rain | 6–10 PNG bill cut-outs (Commons/own render), each falls y −20 % → 120 % with rotate ±40°, z-scale 1.4–2.2 (near lens), 0.9–1.3 s, stagger 0.07 |
| film burn | full-frame overlay: radial gradients #FFB347/#FF7A1A screen-blended rising y 100 %→−20 % in 0.25 s + noise dust layer; or a free light-leak clip (`mixkit.py`) in `screen` mode |
| white bloom | white radial-gradient circle at chest scale 0→6, 0.2 s power2.in, hard cut under it to the cream card |
| zoom-blur | `SF.blurCut` (blur 0→14 px + scale 1→1.08 over 3 f, cut, reverse) |
| cream thought card | full-frame div gradient #FAF4E1→#FBF9F7; `MK.words` word-by-word 0.12 s/word, new word #9A9A9A→#111 |
| grey 3D scene | stage #9A9A9A floor + white wall, 2–3 diagonal light-shaft polygons (white, 35 % opacity, blur 6 px), hero 3D PNG centred, cut-out person `ED.walk` + opacity 0→1 over 1 s |
| B-roll grade | stock clip, `filter: saturate(.25)` on a background-key copy + colour subject on top (or just saturate .55 + vignette) |

### A.4 Prompt template (fill per job)

```
Edit this <N>-second 9:16 talking-head video in the Gold Premium style.
Footage: <who, framing, room>. Keep the voice untouched; cut silences/retakes naturally.
Captions: Poppins; setup words small white (500, 34 px at 1080w) above one gold-gradient PAYOFF word (700, 72 px,
#F6DE9A→#D8A86A→#B07E3E, soft shadow), at chest height, beside or below the face, never over it. Payoff words: <list from
the script>. Between payoffs, plain 1–3-word white subtitles at chest.
Reframe: punch 100 %↔115 % every 1–2 s, speaker shifted to one third, graphics on the free side.
Graphics (on the spoken word): <word → graphic> e.g. "inspection" → bronze card with illustration pops beside head;
"accepted" → gold bar wipes L→R then the word; "<list>" → gold circle icon halo over the head; "<amount>" → gold
counter with dashed selection box + money rain.
Cutaways: <idea line> → cream full-screen thought card with black word-by-word type; <metaphor> → grey 3D studio scene with
window-light shafts and a 3D <object>; <proof> → stock B-roll, grey-desaturated background, gold title.
Transitions: hard cuts; gold film-burn light leak at <2 times>; white bloom into the cream card; one zoom-blur.
Sound: whoosh on cards, pop on icons/chips, riser into burns, coin/cash on the counter, low bed ducked under the voice.
```

---

## B · Minimal Kinetic Green (faceless)

**Specs:** 26.4 s, 30 fps, 720×1280. Pure white world, one green, black type, no footage. A voice-over
(inferred) is visualised as type + simple infographic objects. "Minimal visuals, maximum impact":
one idea per screen, transitions are motion-blur moves, nothing ever just fades.

### B.1 Shot Log

| # | time (s) | frame / subject | camera / motion | type & graphics | in → out |
|---|---|---|---|---|---|
| 1 | 0.0–0.3 | white | **zoom-out from ~400 %** with heavy motion blur | **Attention** (black Inter/SF 600) lands at centre | — |
| 2 | 0.3–1.2 | white; thin green circle outlines (1.5 px, #6FD66A) drift in corners | slow drift | "is" fades in grey→black, **expensive** in green types on L→R; soft green radial glow behind; tiny green "$" particles float up | **whip-rotate** into dial |
| 3 | 1.25–2.4 | **watch dial** macro: green arc with hollow node dots, black ornate clock hand (needle), fine tick marks, small rotated labels | dial slowly rotates; hand sweeps | "Because" (black sans) + **every second** (green italic serif) + 3-line small grey paragraph | **rotational motion-blur** |
| 4 | 2.6–3.8 | white; 4 **green L-shaped viewfinder corner brackets** | brackets + content dolly in (scale 0.9→1.05) | "Your audience" sans + **spends** green italic serif; row of 5 people icons (green, centre one black inside small focus brackets); small grey 2-line paragraph | **zoom-blur out** |
| 5 | 4.2–6.0 | white | slight push | "Trying to understand" (types on letters, last letters grey); behind it 3 **outlined green "?"** marks pop; **4 testimonial cards** (white, 1 px border, avatar, 3 lines, green ★★★★★) pop in around at different depths (small→normal, blur→sharp) | **vertical whip** |
| 6 | 6.0–6.9 | white | **progress ring travels** diagonally bottom-left → centre → upper-right while scaling | ring (grey track, green arc + green glow) with counter 4→8→12→16, caption "Is a second" | blur off |
| 7 | 7.0–11.0 | white | locked, final small scale-down | **green hexagon badges** (#0DA200, white line icon, black corner-bracket accents) pop from small one by one; each gets a **black leader line** that draws, then label types: "Losing prospects" → "Losing momentum" → "Losing opportunities" (3-hex triangle) | scale-down + fade |
| 8 | 11.2–12.8 | white | locked | **one word at a time**, centre, green Inter with soft glow, each word replaces the last (0.25 s/word): "The" "brands" "leading" "the" "market." | blur out |
| 9 | 13.0–13.8 | white | — | **Aren't louder.** black italic serif, blur-in letters, then shrinks 100→45 % | — |
| 10 | 14.0–21.0 | white; huge blurred pale-green rings drift slowly in the background | — | **pill cloud** builds in rows: filled green pill/white text ("They're cleare.", "They remove friction", "They accelerate understanding") alternating with black-outline pill/black text ("Sharper", "More intentional", "They make decisions feel effortless"); each slides in from the side with horizontal motion blur, 0.6–1.2 s apart | cluster slides off |
| 11 | 21.2–23.0 | white | — | **typewriter**, letter by letter: "Because clarity isn't an advantage" (black Inter 400) | **slide left with blur** |
| 12 | 23.3–24.4 | white | slide continues | old line greyed on the left; **It's leverage.** bold black; a **green hand-drawn ellipse draws around it** (0.3 s) with a green outer glow | cut |
| 13 | 24.5–26.0 | white | — | creator logo mark + handle, handle **decodes from random glyphs** (scramble) | black |

**Rhythm:** `ZOOM · type+glow · WHIP · dial · RBLUR · brackets · ZBLUR · ???+cards · VWHIP · ring travel · hex·hex·hex · word·word·word·word·word · serif · pill·pill·pill·pill·pill·pill · typewriter · SLIDE · CIRCLE · scramble`
13 beats / 26 s (avg 2 s), but a new element every ~0.5 s.

### B.2 Style DNA

```
Structure:    claim (Attention is expensive) → why (every second) → who (your audience) → problem (trying to understand,
              losing ×3) → contrast (leaders aren't louder) → list of benefits (pills) → thesis (clarity = leverage) → logo
Rhythm:       one idea per screen, ~2 s per beat, a new element every ~0.5 s, words land on the VO
Camera:       virtual 2D camera — zoom-throughs, rotations, whips; every scene change is a MOTION-BLURRED move, never a dissolve
Transitions:  zoom-out-from-giant ×1 · whip-rotate ×2 · zoom-blur ×1 · vertical whip ×1 · horizontal slide-blur ×2 · cut ×2
Type:         two voices only: neutral grotesk (Inter / SF Pro Display 500–600, black #111) + italic serif (Instrument Serif /
              Playfair italic) for the emotional word, in green. Hero line ≈ 4 % of frame h; body paragraphs tiny (≈ 1.2 %, grey)
              as texture. Reveal modes: type-on L→R, word-by-word grey→black, blur-in.
Palette:      white #FFFFFF · ink #111111 · grey #9A9A9A · green #10C101 (pills/text) · deep green #0DA200 (hexes) ·
              glow green #E7FEE4 (radial glows, blurred background rings)
Graphics:     thin-line infographic objects: watch dial, viewfinder brackets, people icons, progress ring, hexagon badges with
              leader lines, pill tags, hand-drawn ellipse. All flat, one colour, crisp 1.5–2 px strokes.
Signature:    1) green-word-in-black-sentence with soft glow  2) motion-blur camera moves between every scene
              3) pill-tag cloud that builds up  4) hand-drawn green circle on the thesis
Density:      one hero line + ≤ 1 object group; ≥ 60 % white space
Sound (inferred): ticking under the dial, whooshes on every blur move, soft clicks on pills, tiny swell on "leverage"
```

### B.3 How to build it in this engine

| Move | Build |
|---|---|
| zoom-out landing | word at scale 4 + `filter: blur(18px)` → scale 1 blur 0, 0.3 s expo.out |
| green word + glow | `<span class=g>` color #10C101, behind it a 420 px radial-gradient(#E7FEE4, transparent) `MK.fadeIn`; type-on via clip-path |
| italic serif emotion word | Instrument Serif italic, green, `MK.blurIn` 0.3 s |
| whip-rotate / slide-blur | `MK.whip` (or GSAP: outgoing group rotate 0→25°/x −60 % with `blur 0→20px` 0.15 s; incoming from the opposite side, 0.18 s) |
| zoom-blur | `SF.blurCut` / scale 1→1.6 + blur 0→16 px 0.15 s, cut, next scene 1.3→1 |
| watch dial | SVG: arc stroke #10C101 3 px with circle nodes (white fill, 1.5 px stroke), 60 tick lines, black needle path; group rotate −8°→+6° over the beat, needle rotate 20° |
| viewfinder brackets | 4 SVG L paths (#10C101, 3 px) at the corners; `scale .9→1.05` linear over the beat |
| people row | 5 Open Peeps / simple person glyph icons (icon-level, allowed), centre one black with 4 tiny brackets |
| testimonial cards | HTML cards (white, 1 px #E6E6E6, radius 10, avatar, 3 text lines, ★ in green); `MK.popIn` with `blur 6→0` and different depths (scale .6–1) — copy must be the client's real reviews or abstract lines |
| progress ring | SVG circle, `stroke-dashoffset` tween, number counter, drop-shadow 0 0 12px #10C10166; the whole group tweens along a diagonal path |
| hexagon + leader line | SVG hex #0DA200 with white line icon, `MK.popIn` back.out; then `MK.lineDraw` 2-segment polyline 0.25 s; label `MK.typewriter` |
| one-word kinetic | each word replaces the last at centre, 0.2–0.3 s, enter blur 8→0 + scale .9→1 |
| pill cloud | flex-wrap rows; filled pill (#10C101, white text) / outline pill (1.5 px #111); each enters `x ±120 %` with blur 12→0 0.35 s power3.out |
| background rings | 3 huge circles stroke 60 px #E7FEE4, `blur(10px)`, `MK.drift` slow rotation/translation |
| typewriter | `MK.typewriter` 0.05 s/char |
| circle-over-word | `ED.ik`-style hand-drawn ellipse (SVG path, stroke #10C101 3 px, glow), `MK.lineDraw` 0.35 s; previous text dims to #BBB |
| logo scramble | `MK.glitchIn` / per-char random glyph cycling 0.6 s then resolve |

### B.4 Prompt template

```
Create a <N>-second 9:16 faceless kinetic-type explainer in the Minimal Kinetic Green style for <topic/brand>.
World: pure white, ink #111, one green #10C101 (deep #0DA200, glow #E7FEE4). No footage, no people photos.
Type: Inter 500–600 for sentences; Instrument Serif italic green for the one emotional word per line; tiny grey paragraphs as texture.
One idea per screen, a new element every ~0.5 s, words land on the VO.
Beats: <claim line> lands with a zoom-out from giant · <why line> over a thin-line object (dial / ring / brackets) ·
<problem> with outlined icons + pop-in cards · <3 consequences> as green hexagon badges with leader-line labels ·
<contrast line> one word at a time, then a black italic serif line · <benefits list> as a pill-tag cloud (filled green / black
outline alternating) · <thesis> typewritten, slides left, last phrase circled by a hand-drawn green ellipse · logo with
text-scramble.
Every scene change is a motion-blurred camera move (zoom-blur, whip-rotate, slide-blur) — no plain dissolves.
Sound: ticks, whooshes on every blur move, soft clicks on pills, swell on the thesis.
```

---

## When to pick which
- Client has **footage of themselves talking** → A (Gold Premium Talking Head). B's moves can be borrowed for the
  full-screen cutaway cards (cream card can use B's pill cloud or hexes, re-coloured gold).
- **No footage / faceless / VO only / carousel-to-video** → B.
- Never mix both palettes in one film; one accent colour per film.
