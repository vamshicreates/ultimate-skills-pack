# AASTHI — reference Production Brief (as delivered)

This is the brief behind `examples/aasthi/index.html`. It shows the target voice and level of
detail for DIRECTOR.md §9. The original client prompt was 30 s with no narration; a client
voiceover (36.2 s) arrived later, so the "VO REVISION" section at the end records how the film
was re-timed. The code implements the revised timing.

---

TITLE — AASTHI · premium fintech product film · 30 s (36.5 s with VO) · 16:9

FORMAT
16:9 · 1920×1080 · 30 fps · finish reveals by 28.5 s, hold logo + tagline to 30.0 s

STYLE
CRED-style luxury product film. Seamless studio void, glossy product lighting, slow weightless
camera, elegant lowercase serif typography, no people, no hard cuts. One continuous flowing film.

REFERENCES
REF1 = dark AASTHI hero page on a frontal silver MacBook → cropped screen texture. Keep exact.
REF2 = "Built for Trust" dark compliance grid on a 3/4 laptop → rebuilt in HTML, verbatim copy.
REF3 = "How It Works" light step-card page on a 3/4 laptop → rebuilt in HTML, verbatim copy.
REF4 = AASTHI violet "A" logo → keyed to transparent PNG. Preserve shape, gradient, proportions.
(The client's @Image labels did not match the files; refs were mapped by content.)

CREATIVE APPROACH
The story: you moved abroad → your investments don't have to → AASTHI brings India's private
markets to your laptop → apply, verify, get access → discover, review, choose → track everything
in one place → built on trust → AASTHI.
The laptop is the hero object. UI elements peel off the screen, float in 3D depth and return.
Typography floats in its own layer beside the laptop, never on the screen.

VISUAL SYSTEM
Background: seamless warm cream #F7F1EC studio void fading to mauve-brown #CDB3AA at the base; soft
wide floor shadow; faint gold #E3B34A and violet #7B6CF6 bokeh at the frame edges. Dark sections:
near-black #0B0B0E gradient with a subtle violet lift at the centre.
Brand colours: violet gradient #8F7CF8 → #2E2496 (logo, glows, streaks) · gold #E3B34A (accents,
icons, highlight words) · navy #1B2A5E (buttons, step numbers) · dark UI panels #111216 with thin
gold-edged icon tiles.
Materials: brushed-aluminium silver laptop, frosted glass and brushed-aluminium cards with soft
drop shadows and edge highlights, thin vertical light streaks, gold/violet light-streak whips.
Lighting: large soft key from the upper left, rim light on laptop edges, glossy specular sweeps.
No grain, no harsh flares.

TYPOGRAPHY
Headlines: Cormorant Garamond 500, lowercase, white on dark / #1A1A1A on cream, 84–118 px.
Captions: Inter 500, lowercase, tracked. Names and acronyms keep case (AASTHI, KYC, IFSCA, India, US).
Text blocks 30–50 % of frame width.

MOVEMENT
Weightless premium. Gentle orbits, dolly push-ins, arcs; the laptop hovers and rotates slowly.
Cards lift off the screen with ease-out, hang in depth with parallax, settle back with ease-in.
Text resolves from blur to sharp with a soft light sweep, then holds. Transitions: push-in through
the screen, light-streak whip, fades through black.

EXACT CHOREOGRAPHY (original 30 s)
00:00–00:03 | THE HOOK — near-black with a faint violet glow. "you moved to the US." fades in,
then "your investments don't need to." resolves from blur with a light sweep. Hold.
00:03–00:07 | THE LAPTOP RISES — background warms to the cream void; the laptop rises from below,
turning from three-quarter to front; hero page glows on screen; floor shadow blooms. Caption left
of the laptop: "invest in India. from anywhere."
00:07–00:10 | INTO THE BRAND — slow push-in past the gold headline toward the violet A-frame visual;
bokeh drift in the foreground; headline top-left: "with AASTHI, investing back home becomes simpler."
00:10–00:15 | APPLY · VERIFY · GET ACCESS — screen wipes to How It Works at a 3/4 angle; card 01,
card 03, then the navy "Apply for Access" button lift off one by one; captions "apply." →
"verify." → "get access."
00:15–00:16 | WHIP — fast gold-and-violet light-streak whip with motion blur.
00:16–00:21 | DISCOVER · REVIEW · CHOOSE — card 04 lifts; two frosted cards stack behind it, fanning;
captions "discover private-market opportunities." / "review the details." / "choose what works for you."
00:21–00:24 | ONE DASHBOARD — cards glide back; screen shows a dark AASTHI dashboard with a gold
line chart drawing on; "invest. track. stay updated. all from one dashboard."
00:24–00:27 | BUILT FOR TRUST — fade to black with rising vertical light streaks; shield, warning
and lock cards float out with gold rim light; "KYC verified." → "risk disclosed." → "IFSCA regulated."
00:27–00:30 | BRAND RESOLUTION — brief hero angle of the laptop with the Built for Trust screen;
fade to black; "AASTHI makes investing in India easier, wherever in the world you are."; the violet
A logo glows up with the "AASTHI" wordmark and "India's private markets. From anywhere."
Finish revealing everything by 00:28.5. Hold until 00:30; only the violet bloom breathes.

AUDIO
Premium minimal electronic score: warm pulse, airy pads, subtle piano. Glassy shimmer on each card
lift, clean whoosh on the whip, low risers into the trust section, warm resolved chime on the logo.
No narration, no vocals.

QUALITY AND CONSTRAINTS
Keep the laptop, finish and screen content consistent with the references. Do not redesign or
re-letter the UI. Every headline readable before it transitions. Generate only the specified copy.
Spell "AASTHI" exactly. Preserve the logo exactly. No people, hands, phones, extra devices, stock
footage, charts with fake numbers, excessive particles, harsh flares or watermarks.

---

## VO REVISION (client voiceover, 36.2 s, script read line by line)

Measured with `audio/align_vo.py --asr`; each phrase placed on its caption; VO tempo 1.08×; music
ducked 55 % under the voice. Film extended to 36.5 s because the closing lines need ~6 s.

| phrase | film time |
|---|---|
| you moved to the US. | 0.35 |
| your investments don't need to. | 1.60 (headline reveal moved to 1.4) |
| invest in India. / from anywhere. | 4.80 / 5.80 |
| with AASTHI, / investing back home becomes simpler. | 7.75 / 8.50 (headline exit moved to 10.15) |
| apply. / verify. / get access. | 11.10 / 12.35 / 13.55 |
| discover private-market opportunities. | 16.50 (caption moved to 16.45) |
| review the details. / choose what works for you. | 18.45 / 19.65 |
| invest. / track. / stay updated. / all from one dashboard. | 21.35 / 21.98 / 22.50 / 23.30 (headline split into 3 lines revealed with the words) |
| KYC verified. / risk disclosed. / IFSCA regulated. | 25.15 / 26.15 / 27.10 (trust section +0.5 s, cards 0.95 s apart) |
| AASTHI makes investing in India easier, / wherever in the world you are. | 29.15 / 31.55 |
| AASTHI. / India's private markets. / From anywhere. | 32.90 / 33.45 / 34.80 (logo lockup 32.85, hold to 36.5) |
