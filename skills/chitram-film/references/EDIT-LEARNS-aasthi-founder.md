# Edit Learns: blue-grid editorial collage edit

One notebook: what I learned studying `Video-28430.mp4` frame by frame (12 s, 25 fps), how to rebuild it, and what applying it to the AASTHI founder edit taught me.

## Contents
1. Shot log, frame by frame
2. Style DNA: assets, textures, type, colour, motion
3. How to recreate it (research notes)
4. Production prompt and reusable template
5. Lessons from applying it (AASTHI · Vamshi founder edit)

## The five things that make this edit look premium
1. **One colour world:** royal blue #415BFC + white + B&W photography only, on grid paper with grain.
2. **Print textures on video:** sticker-outlined cut-outs, halftone dots and line-screen photos, paper labels.
3. **The collage accumulates:** cards stack up while a virtual 2D camera pans between them (3–5 f moves, constant drift).
4. **Words sit on the speech:** every card, label and letter lands on the spoken word, with back-out overshoot pops.
5. **Transitions mean something:** blur-through-cut switches worlds, the whip switches shots, and the ending is a poster.

---

## 1. Shot log, frame by frame
**Source:** `C:\Users\kota santhosh\Downloads\Video-28430.mp4`
**Specs:** 12.00 s · 25 fps (300 frames, f0–f299) · 1276×718 (16:9) · H.264 High · AAC HE stereo 44.1 kHz
**Detected hard cuts (scene > 0.25):** 4.52 s (f113) and 7.84 s (f196). Every other change happens *inside* a composite (camera moves, pops, blur-outs).
**Method:** all 297 frames were extracted into flip-book sheets with frame numbers and timecodes, and read in order. Full-size detail frames were pulled at 1.6, 5.6, 8.6, 10.2 and 11.5 s. Colours were sampled from pixels.

> Frame numbers are 25 fps: `f = t × 25`. 1 frame = 0.04 s.

---

### Beat map (summary)

| # | Time (s) | Frames | World | What happens | Out |
|---|---|---|---|---|---|
| 1 | 0.00–1.08 | f0–27 | Blue grid collage | Speaker-A sticker cutout settles; caption "I have written for" types on word by word | caption snaps off |
| 2 | 1.08–2.12 | f27–53 | Blue grid collage | Speaker slides right; **TELEVISION** card pops in at left | camera pans left |
| 3 | 2.12–2.84 | f53–71 | Blue grid collage | **FILM** card swings in from the right | camera pans back and pushes in |
| 4 | 2.84–3.60 | f71–90 | Blue grid collage | **RADIO** card flies in over the TV card (stacking) | – |
| 5 | 3.60–4.52 | f90–113 | Blue grid collage | **PRINT ADS** card pops in; camera pans right; hold | gaussian blur-out → CUT |
| 6 | 4.52–5.96 | f113–149 | Live podcast footage (Speaker A) | Blur-in; sticker captions stack on the right: I HAVE / **WRITTEN** / ALL KIND / OF STUFFS | horizontal whip pan |
| 7 | 5.96–7.84 | f149–196 | Live podcast footage (Speaker B) | Question stacks on the left: WHEN DID YOU / STARTED MAKING / **MONEY** / OF YOU / DOING CONTENT | gaussian blur-out → CUT |
| 8 | 7.84–9.52 | f196–238 | Clean blue grid | Halftone cutout rises from below; "When … was" → giant **19** behind the subject → "i was … like a" | blur + fade to empty blue |
| 9 | 9.52–10.76 | f238–269 | Clean blue grid | Halftone hand flies in holding a cheque; **PAY CHEQUE** fades up in huge condensed type | cheque dissolves under the type |
| 10 | 10.76–12.00 | f269–299 | Clean blue grid | Line-screen halftone head pops onto the "C" of CHEQUE with a drop shadow; hold to the end | end (no outro) |

Rhythm: `pop·pop·pop·pop — BLUR — stack-stack — WHIP — stack-stack — BLUR — rise·19 — BLUR — fly·TYPE·pop`
Average beat ≈ 1.2 s. Something new enters every **0.3–0.7 s**, so the eye never rests longer than about 18 frames.

---

### Beat-by-beat, frame by frame

#### Beat 1 · 0.00–1.08 (f0–f27): hook caption
- **Frame / subject:** saturated royal-blue background (#415BFC) with a faint 1 px white grid (≈19 columns across) and paper-grain texture. The centre and top are slightly lighter, like a soft top-light vignette. Speaker A sits centred as a **sticker cutout**: a live-footage crop with a rounded-rectangle bottom edge, the head and shoulders following the silhouette, and a thick **irregular white outline** (about 8–10 px at 718p, wider above the hair).
- **Motion:**
  - f0–f5: the cutout **scales down** from about 135 % to 100 %, fast ease-out (a "drop onto the table" settle). f0–f1 show purple chromatic fringing and motion blur on the edges.
  - f5–f27: locked. The live footage inside the cutout keeps playing (lip sync).
- **Type:** caption sits under the cutout, left-aligned to the cutout's left edge. White, small (≈3.3 % of frame height), clean geometric sans (Inter/SF-style, Medium). It reveals **letter by letter within each word**, and every new word starts about 1 line-height lower, then rises onto the baseline while fading and unblurring:
  - "I" f2–f3 · "have" f4–f9 · "written" f10–f17 · "for" f17–f22 (≈ 6 frames per word, synced to speech)
  - holds f22–f26
- **Out:** f27, the caption **disappears on a hard cut** (no fade) at the moment the next move starts.

#### Beat 2 · 1.08–2.12 (f27–f53): TELEVISION
- f27: speaker cutout begins sliding **right and down** (to about x = 62 %), with motion blur f28–f31. It scales up about 10 % because the whole camera is pushing in.
- f28: the **TELEVISION card** appears as a tiny thumbnail (≈8 % scale) at upper-left. By f29 it is ≈85 %, f30 overshoots to ≈110 % with blur, and f31–f35 settle to 100 % (a back-out pop, about 7 frames).
- **Card anatomy:** white rounded card (radius ≈ 16 px, near-white #F4F4F6) with a soft drop shadow. Inside is a blue rounded square in the same blue as the background, holding a **B&W cut-out photo of a vintage TV whose antenna breaks out above the blue square**, which gives a pop-out 3D feel. Below it the label "TELEVISION" is set in a heavy **extended/wide** sans, all caps, blue (#2F4BE0).
- f31–f51: the whole composition **drifts slowly** (the card creeps right about 2 % of the frame) so it never feels frozen.
- f52–f53: **camera pan left.** The full composite translates left about 30 % of the frame in 3–4 frames with motion blur. The FILM card enters from the right edge.

#### Beat 3 · 2.12–2.84 (f53–f71): FILM
- FILM card arrives **oversized (~115 %)** and tilted, then settles to 100 % by f58. It holds a **B&W clapperboard rotated about −25°** that breaks out of the blue square.
- The TV card is now cut off at the left edge and the speaker sits left of centre, so the layout alternates between left-heavy and right-heavy.
- f58–f70: slow drift.

#### Beat 4 · 2.84–3.60 (f71–f90): RADIO
- f71–f72: camera pans **back right** and pushes in. The **RADIO card flies in from the lower left** on top of the TV card (cards **stack like a collage**, never replace each other). The radio photo is tilted about −15° and breaks out of its square.
- f72–f77: push-in continues until the FILM card slides off the right edge (only a sliver stays).
- f78–f89: hold with drift. Layout: TV card behind at top-left, RADIO in front, speaker centre-right, FILM sliver at the right edge.

#### Beat 5 · 3.60–4.52 (f90–f113): PRINT ADS → blur exit
- f90: **PRINT ADS card** pops from a tiny thumbnail at lower-middle, then f91 is ≈60 %, f92 overshoots with a tilt, and f93–f95 settle. The photo is a **B&W magazine cover ("PREVIEW" masthead)** fanned over a second magazine.
- f95–f99: **camera pans right** (everything moves left). RADIO goes to the left edge, the speaker sits left-centre, and PRINT ADS lands centre-right with the FILM card peeking out behind it at the top right.
- f99–f109: hold.
- f110–f112 (0.12 s): **gaussian blur ramps** 0 → very heavy (≈40 px) while the brightness lifts slightly.
- f113: **CUT** to the next shot, already blurred.

#### Beat 6 · 4.52–5.96 (f113–f149): live footage, Speaker A + sticker captions
- **Frame:** real podcast set, wide shot. Speaker A sits in a grey armchair. The studio has black acoustic foam with red panels, a silver lamp, a mic boom, two black mugs in the foreground and a blue LED wall on the right with a glowing "Open…" logo.
- f113–f117: **blur-in** from heavy to sharp (5 frames, ease-out). Together with the 3-frame blur-out this makes a **blur-through-cut** transition of about 8 frames.
- **Sticker caption stack on the right** (x ≈ 70–95 % of frame, over the empty blue wall):
  - Each line is a **white paper label** (rectangle, no radius, tiny shadow) with a slight individual rotation (−3° to −10°, alternating).
  - Font: **condensed bold grotesk in caps** (Bebas Neue / Oswald Bold / Anton family), black.
  - The **emphasis word is larger and blue (#2F4BE0)**.
  - "I HAVE" pops in at f116 · "**WRITTEN**" at f117 (bigger, blue, −10°) · "ALL KIND" at f122 (enters at ~40 % scale, snaps to 100 % in 2 frames) · "OF STUFFS" at f133 (same pop).
  - Every label **pops with overshoot** (≈40 % → 110 % → 100 % in 3–4 frames) exactly on the spoken word.
- f145–f149: **WHIP PAN.** A strong horizontal directional blur hits while the image offsets left, and the offset wraps around, so the caption stack **repeats/tiles** in f148–f149. This is the classic Offset plus Directional Blur whip.

#### Beat 7 · 5.96–7.84 (f149–f196): live footage, Speaker B + question stack
- f150–f155: the incoming shot slides in from the right under the same directional blur and settles by f155 (whip total ≈ 10 frames, 5.80–6.20).
- **Frame:** Speaker B (beige overshirt, white tee) in an armchair, leaning back, with a mic in front. It is the same studio seen from the reverse side.
- **Caption stack now on the LEFT** (it mirrors the previous shot, because it sits in the empty space on the side the speaker is not facing):
  - "WHEN DID YOU" rides in with the whip (f152) and is readable by f155.
  - "STARTED MAKING" f159 (small) · "**MONEY**" f166 (large, blue, pops with overshoot, −5°) · "OF YOU" f173 (small) · "DOING CONTENT" f181.
- f192–f195: gaussian blur-out (4 frames).
- f196: **CUT** to clean blue.

#### Beat 8 · 7.84–9.52 (f196–f238): "When I was 19"
- f196: empty blue grid (a 1-frame breath).
- f197–f203: a **halftone B&W cutout** of Speaker A (arms crossed, jacket, glasses, from an older photo) **rises from below the frame**. It starts heavily blurred and unblurs as it rises, arriving at f203 with an ease-out. This cutout has **no white sticker stroke**, just a soft blue glow edge. That signals a different visual register (a memory or photo, not live).
- f199–f204: "When" (left of the subject) and "was" (right) fade and unblur in, rising slightly. White, medium-bold sans (Inter SemiBold style), ≈6 % of frame height.
- f208–f214: a **giant "19"** rises and fades in **behind the subject** (text-behind-subject layering). Pale lavender-white (#E4E7FF, ~90 %), black-weight grotesk, ≈55 % of frame height, the "1" left of the head and the "9" right of it.
- f218–f221: "When"/"was" blur out.
- f222–f228: "**i was**" (left, lowercase i) and "**like a**" (right, with a small raised "a") blur-fade in. They are slightly smaller and rise into place.
- f229–f234: hold.
- f235–f238: the whole layer **gaussian blurs and fades** to empty blue. f238–f239 are pure blue (breath).

#### Beat 9 · 9.52–10.76 (f238–f269): the cheque
- f240–f245: a **coarse-dot halftone hand** holding a clean paper **cheque** flies in from the **top right**. It enters rotated about −20° and blurred, then rotates to about −3° while travelling down-left to the centre-right, easing out and settling by f246.
- The cheque is sharp and clean (not halftoned). It reads "3,50,000", "Three lakh fifty thousand rupee only" and "Tanmay bhat", in handwritten-script fields. The **texture contrast** (dotted hand vs. clean paper) makes the object read as the hero.
- f246–f257: the hand floats with a small wobble.
- f258–f269: "**PAY CHEQUE**" fades up behind and over the cheque. The type is **huge ultra-condensed caps** (Anton / Druk Condensed / Bebas family) filling ≈85 % of the frame width, ≈55 % of its height.
  - "PAY" ramps opacity f258–f262, starting slightly lower and rising.
  - "CHEQUE" reveals **left to right as a per-character opacity ramp** f261–f268. Its right letters are still translucent lavender while its left letters are already white.
  - The cheque and hand dissolve out under it, f262–f264.
  - Solid white by f269.

#### Beat 10 · 10.76–12.00 (f269–f299): the face on the word
- f269–f274: type holds alone.
- f275–f278: a **line-screen halftone head** (diagonal-line dither, young Speaker A with glasses) pops in centred on the "C" of CHEQUE. It scales from ≈20 % with blur, overshoots, and settles. It has a **soft grey drop shadow offset down-right**, like a paper cutout lying on the poster.
- f278–f299: hold with a tiny scale drift. The clip ends on the hold with no outro and no fade.

---

### Transitions used (count)
| Type | Where | Length |
|---|---|---|
| Hard cut of an element (caption snap-off) | 1.08 | 0 f |
| Camera pan/push inside the composite | 2.08, 2.84, 3.80 | 3–5 f each |
| **Gaussian blur-out → cut → blur-in** | 4.52 (A), 7.84 (to clean blue) | 3 f out + 5 f in |
| **Directional whip pan with offset wrap** | 5.80–6.20 | ≈10 f |
| Blur + fade to empty background | 9.40–9.52 | 4 f + 2 f hold |
| Object fly-in / type fade over the object | 9.60, 10.32 | 6–10 f |

### Sound (not heard; inferred)
The audio stream exists (HE-AAC 64 kb/s), but it was not listened to. From the edit rhythm, these are **likely**: a pop/click on every card and label pop, a whoosh on the whip at 5.80 and on the blur transitions, a riser or impact under the giant "19" and "PAY CHEQUE", with dialogue running continuously underneath. The captions are timed to the speech.

---

## 2. Style DNA: assets, textures, type, colour, motion
This is the style with the content removed, so the grammar can be moved onto any podcast or talking-head clip.

### Style DNA (one glance)
```
Name:         "Blue-grid editorial collage" podcast edit (a mixed-media, print-inspired talking-head style)
Structure:    hook caption → list of cards (collage builds up) → live clip + sticker captions
              → reverse shot + question stack → memory beat (halftone + giant number) → object proof → poster payoff
Rhythm:       new element every 0.3–0.7 s; beats 1–2 s; blur transitions ≈ 8 f; one whip
Camera:       virtual 2D camera over a flat collage (pans ±30 % width in 3–5 f, slow push-ins, constant drift)
Worlds:       two worlds alternate: (1) flat blue graphic table, (2) real studio footage. Blur links them.
Transitions:  blur-through-cut ×2, directional whip with offset wrap ×1, blur-fade-to-bg ×1, camera pans ×3
Type:         3 voices: small clean sans (spoken captions), condensed caps on paper labels (stickers),
              huge black/condensed display (payoff words and numbers)
Palette:      one royal blue + white + B&W photography. No other hues.
Signature:    1) sticker-outlined cutouts and white cards whose B&W objects break out of the frame
              2) halftone photo treatments (dot, coarse dot, line-screen) on a blue grid-paper texture
              3) giant word or number behind the subject, then a face placed ON the word
Density:      1 speaker + ≤ 3 cards, or 1 speaker + 1 caption stack. ~35–50 % empty blue.
```

### Palette (sampled from pixels)
| Token | Hex | Use |
|---|---|---|
| `--blue` | **#415BFC** (range #394DFC–#4A68FE) | the only background colour; inner square of the cards |
| `--blue-hi` | #6782FF | top/centre light falloff, grid lines blended over the blue |
| `--ink-blue` | ≈ #2F4BE0 | card labels, emphasis words on sticker captions |
| `--paper` | #F4F4F6 | cards, sticker labels |
| `--white` | #FFFFFF | spoken captions, "When/was", PAY CHEQUE |
| `--lavender` | ≈ #E4E7FF | giant "19" (a white that is slightly tinted by the blue) |
| `--ink` | #111111 | halftone dots, black sticker text |

Rule: **everything is blue, white or B&W photo.** Colour photos appear only as live footage, and even that is graded so the blue LED wall echoes the brand blue.

### Textures & surface
1. **Grid paper:** 1 px lines, white at ≈ 12–15 % opacity. The cell is ≈ 67 px at 1276 wide (≈ **100 px at 1920×1080**), square.
2. **Paper grain:** fine fibre/noise overlay (≈ 4–8 % opacity, multiply or overlay), static rather than boiling.
3. **Light falloff:** a soft radial lift at the top-centre with slightly darker corners (a vignette). It keeps the flat blue from looking digital.
4. **Halftone photography.** Three different screens, each with a meaning:
   - **Round dot, fine** (Beat 8 cutout): a "memory" or archive photo.
   - **Round dot, coarse ~6 px** (the hand): a prop, graphic and loud.
   - **Diagonal line-screen** (final head): the poster payoff, like engraved newsprint.
5. **Sticker outline** on live cutouts: a thick, slightly uneven white stroke (≈ 8–10 px at 718p, ≈ 14 px at 1080p) grown from the alpha, with a rounded-rect bottom crop.
6. **Soft shadows:** a big soft drop shadow under the cards (y 8–12 px, blur 30, black at 20 %) and a hard-ish offset shadow on the final head (x +10, y +10, blur 12, 35 %).

### Asset list (what to prepare)
| Asset | How it's made |
|---|---|
| Speaker cutouts (live) | rotoscope or AI matte of podcast footage; crop the bottom to a rounded rect; white stroke |
| Old photos of the speaker | B&W, high contrast, background removed, halftone (dot or line) |
| Object cards (TV, film clapper, radio, magazine) | stock PNG of a vintage object → desaturate, raise contrast, cut out → place over a blue rounded square inside a white card so the object **breaks the top edge**. Label in extended heavy caps. |
| Hand + cheque | stock hand PNG (coarse halftone) + a clean paper prop mocked up with script fonts |
| Sticker labels | white rectangles sized to the text, individually rotated −10°…+4° |
| Background plate | #415BFC + grid + grain + vignette, 1 still layer that sits under everything |

### Type system (identified by look; the exact fonts in the reference are unknown)
| Voice | Look | Close free matches | Size (1080p) | Motion |
|---|---|---|---|---|
| Spoken caption | clean geometric sans, sentence case, white | Inter Medium, Manrope | 34–40 px | per-letter type-on, each word rises 1 line and unblurs |
| Card label | **extended/wide** heavy caps, blue | Archivo Black Expanded, Unbounded Black, Syne ExtraBold | 36–44 px | pops with the card |
| Sticker caption | **condensed bold caps**, black on white label, emphasis word blue and ×1.6 | Bebas Neue, Oswald Bold, Anton | 50–70 px (emphasis 90–110) | scale-pop with overshoot per line |
| Big story words | medium/semibold sans, white | Inter SemiBold | 64–80 px | blur-fade and rise |
| Giant number | black-weight grotesk, lavender, behind the subject | Inter Black, Archivo Black | ≈ 600 px tall | rise and fade, sits behind the cutout |
| Poster payoff | **ultra-condensed caps**, white, filling the frame | Anton, Bebas Neue, Druk Condensed (paid), League Gothic | ≈ 600 px tall | per-character opacity ramp left→right |

### Motion grammar (numbers you can reuse at 25 fps)
| Move | Frames | Curve | Notes |
|---|---|---|---|
| Card/label **pop** | 5–7 f | back-out: 8 % → 85 % → 110 % → 100 % | add 2–3 f of motion blur on the overshoot |
| Cutout **settle** | 5–6 f | 135 % → 100 %, expo-out | open on it for the hook |
| **Camera pan** in the collage | 3–5 f | fast in/out, motion-blurred | the whole comp moves, cards act as parallax planes |
| **Idle drift** | continuous | linear, ≈ 2 % of the frame per second | nothing is ever perfectly still |
| **Per-letter type-on** | ≈ 1 f per letter | each word starts ~1 line lower and rises | synced to the spoken word |
| **Blur-through-cut** | 3 f out + 5 f in | ease-in to ≈ 40 px, then ease-out to 0 | used to switch *worlds* (graphic ↔ footage) |
| **Whip pan** | ≈ 10 f | Offset shift ±full width + directional blur 90°, length ≈ 250 | used between two *shots of the same world* |
| **Rise from below** | 6–7 f | expo-out, blur 30 → 0 | for "memory" cutouts |
| **Object fly-in** | 6 f | from off-frame corner, −20° → −3°, ease-out + a small wobble | hero props |
| **Per-char opacity reveal** | 8–10 f | text-animator offset ramp | poster words |

### Layout rules the editor follows
- Captions always go in the **empty side** of the frame, opposite where the speaker faces (right for Speaker A, left for Speaker B). They never cover a face.
- The collage **accumulates**: cards stack and overlap and never swap out cleanly, which reads as "the list keeps growing".
- Emphasis = **one word per line group** in blue and bigger (WRITTEN, MONEY).
- Payoff words are set **bigger than the subject**, and the subject is then layered behind (19) or on top (PAY CHEQUE face).
- Graphic beats run 1–1.7 s. Footage beats are 1.5–1.9 s, long enough for one spoken phrase.

---

## 3. How to recreate it (research notes)
These techniques come from online tutorials (sources at the bottom) and are matched to what the frames show.
Each technique lists three routes: **AE** (After Effects), **PR** (Premiere Pro), **CF** (our chitram-film HTML/GSAP engine).

---

### 1. Blue grid-paper background
- **AE/PR:** solid #415BFC → **Grid** effect (size ≈ 100 px at 1080p, border 1 px, white, blend at 12–15 %) → a paper-texture still (Pexels/Envato "paper texture") set to Multiply or Overlay at 5–8 % → an Ellipse mask vignette or a **Gradient Ramp** (top centre #6782FF → edges #394DFC) on Soft Light.
- **CF:** a `#bg` div with `background: radial-gradient(at 50% 0%, #6782FF33, transparent 60%), #415BFC`, plus two `repeating-linear-gradient` layers (0° and 90°, 1 px white at 0.13 every 100 px) and a grain PNG overlay at 6 %.

### 2. Cutting the speaker out (the "sticker" person)
- **AE:** **Roto Brush 2/3** on the podcast clip. Then *Refine Edge*, and freeze the roto for the shot.
  - Rounded bottom: add a rounded-rectangle mask set to *Intersect* across the lower torso.
- **Sticker outline:** duplicate the layer → **Fill** (white) → **Simple Choker** with a negative Choke Matte (≈ −10 to −15 at 1080p, which *expands* the alpha) → place it under the original.
  - Lumpy, hand-cut edge: add **Turbulent Displace** (amount 10, size 30) to the stroke copy only.
  - Alternative stack: *Fill + Simple Choker + CC Composite* on one layer.
- **PR:** use Ultra Key / Object mask (Premiere 25+), or roto in AE via Dynamic Link.
- **CF:** pre-key the clip (e.g. `tools/prep_video.sh` or an AI matte → WebM/ProRes 4444 with alpha). The outline is a CSS `filter: drop-shadow()` stack: 8 × `drop-shadow(0 0 0 #fff)` offsets at 7 px in a circle. Or render the stroke into the matte beforehand, which is more reliable.

### 3. Halftone photos (dot, coarse dot, line-screen)
- **AE native method (Boris FX / Motion Array):**
  1. Pre-comp the B&W photo. Add a white solid, then a black solid "Dots" layer with **CC Ball Action** (Ball Size 18–20, Grid Spacing ≈ 5).
  2. Put an adjustment layer above with **Camera Lens Blur**: Blur Map = the photo pre-comp, Source = *Effects & Masks*, ✔ *Invert Blur Map*.
  3. On the same adjustment layer, add **Levels** and raise Input Black until the light dots go solid.
  4. Add Curves on the source to crush the shadows first.
- **AE quick method:** *Color Halftone* (Stylize), or **BCC Halftone** with Dot Shape = Circle (dots) or **Lines** (the line-screen head at the end), Color Scheme = B&W, and HT Scale for coarse vs. fine.
- **Photoshop route** (easiest for stills): Image → Mode → Grayscale → Bitmap → *Halftone Screen* (Round, 45°, 30–45 lpi for coarse; Line shape for line-screen). Export a PNG with alpha.
- **CF:** prepare the halftone PNGs offline (Photoshop, or a Python/OpenCV halftone). Don't do halftone live in the browser. Put them in `assets/`.

### 4. Object cards that "break out" of their frame
- Build in AE or Figma: a white rounded rect (r 16) → blue rounded square (r 8) → B&W object PNG → **duplicate the object and mask the duplicate to only the part that sits above the blue square** (the antenna or clapper tip), placed above everything. The object then reads as coming out of the card.
- Label in an extended heavy font with tracking +2 %, blue #2F4BE0.
- Shadow: *Drop Shadow* with distance 10, softness 40, 20 %.
- **CF:** card = `div.card > div.well > img.obj`. The well uses `overflow:hidden`, and a second `img.obj.pop` is clipped by `clip-path: inset(0 0 72% 0)` above it. Or, simpler, allow `overflow:visible` and place the PNG so its top pokes out.

### 5. Pops, overshoot and the 2D "camera"
- **AE:** keyframe Scale 8 → 110 → 100 over 6 f. Use the Graph Editor for a steep ease-out, or an **overshoot/bounce expression** (inertial bounce). Turn on **Motion Blur** (shutter 180°+).
  - For camera pans, parent every card and cutout to a **Null "CAM"** and keyframe the null's Position and Scale (3–5 f moves with hard ease). Add a `wiggle(0.5, 4)` or a linear drift for idle motion.
- **PR:** Transform effect (with its own shutter angle 180–360° for blur) on a nested collage sequence.
- **CF:** `MK.popIn(tl, el, t, {from:.08, ease:'back.out(2.2)'})` for cards and labels. Put the collage in a `#cam` wrapper and tween its `x/scale` over 0.12–0.2 s with `MK.curves.snap`. Add a linear idle drift on `#cam` for the full beat.

### 6. Spoken caption: per-letter type-on with word rise
- **AE text animator:** Animate → **Opacity 0 %** + add **Position Y +40** + **Blur 10**. The Range Selector is *Based On: Characters*, Shape *Ramp Up*, and Offset is keyframed −100 → 100 % (about 1 frame per character).
  - To have each word rise separately, add a second animator *Based On: Words*.
- Sync to speech: generate a transcript (Premiere *Speech to Text*), then place each word's start at its spoken time.
- **CF:** split into `<span>` letters and stagger `fromTo({opacity:0, y:14, filter:'blur(6px)'}, …)` at 0.04 s per letter, with word groups offset in time to the VO (`audio/align_vo.py` gives phrase times).

### 7. Sticker captions (paper-label stacks)
- Each line is its **own** text layer plus a white Shape rectangle behind it (pick-whip the rectangle size to `sourceRectAtTime()`), rotated −10°…+4°, alternating.
- Emphasis word: blue #2F4BE0, 1.6× size.
- Pop each line on its spoken word: Scale 40 → 110 → 100 over 3–4 f.
- In Premiere, save one line as a **.MOGRT** and duplicate it. Kinetic-caption template packs do the same thing.
- Placement: the empty side of the frame, opposite the speaker's eyeline.
- **CF:** `div.label` stacks (`display:inline-block; background:#F4F4F6; transform:rotate(-4deg)`), each with `MK.popIn` at its word time.

### 8. Blur-through-cut (switching between the graphic world and footage)
- **PR/AE:** put an adjustment layer over the cut with **Gaussian Blur** (Repeat Edge Pixels ✔). Blurriness 0 → 40 over the last 3 f of the outgoing shot, then 40 → 0 over the first 5 f of the incoming one. Optionally add Exposure +0.3 at the peak. Place a whoosh at the cut.
- **CF:** the kit's `blur` transition, or tween `filter: blur()` on `#stage` 0 → 24 px (0.12 s) → swap scenes → 24 → 0 (0.2 s).

### 9. Whip pan with offset wrap (5.80 s)
From the tutvid whip-pan method, which matches the tiled/repeated captions seen at f148–149:
1. Put an **adjustment layer** across the cut: 5 f before and 10 f after.
2. **Offset** effect: animate *Shift Center To* from 960 → −960 (a full width at 1080p) across the adjustment layer. This wraps the image, which is why the caption stack appears twice mid-whip.
3. **Directional Blur:** Direction 90°, Blur Length 250 at the cut frame, 0 at both ends.
4. Optionally add **Posterize** Level 15 at the cut and 255 at the ends.
5. Use ease-out on the first keyframes, ease-in on the last, and Auto-Bezier in the middle. Save it as a preset.
6. Add a whoosh SFX, peaking on the cut.
- **CF:** the kit's `whipPan` transition (velocity-matched) or `MK.whip(tl, t, {dir:'left', dur:.4})`.

### 10. Giant word or number behind the subject ("19")
- **AE:** cutout layer (roto or PNG) on top → text layer "19" in the middle → background at the bottom. Animate the text Position Y +80 → 0 and Opacity 0 → 90 % over 6 f.
  - With moving footage, duplicate the clip, roto the top copy and keep the untouched copy underneath (the standard *text behind subject* method).
- **CF:** z-order `#bg` < `#bigNum` < `#cutout`. `gsap.fromTo('#bigNum', {y:80, opacity:0}, {y:0, opacity:.9, duration:.24, ease:'expo.out'})`.

### 11. Poster payoff (PAY CHEQUE + face on the word)
- The type reveals with a text animator set to Opacity 20 % → 100 %, Based On *Characters*, Offset ramped left → right over 8–10 f. "PAY" leads "CHEQUE" by about 3 f.
- The prop (hand + cheque) cross-dissolves out underneath during the same frames.
- Face: line-screen halftone PNG, popped in (Scale 20 → 108 → 100, 4 f) over the "C", with a **Drop Shadow** (distance 12, direction 135°, softness 15, 35 %).
- **CF:** split letters, stagger opacity 0.2 → 1 at 0.03 s per char, then `MK.popIn('#face', …)` with `filter: drop-shadow(10px 10px 8px rgba(0,0,0,.35))`.

### 12. Sound design (recommended; the reference audio was not heard)
- Pop, click or paper-flick on every card and label (−18 dB, short).
- Whoosh on the blur-through-cuts and the whip (peak on the cut frame).
- A soft riser into "19" and a low thump on "PAY CHEQUE".
- Dialogue stays on top. Duck the music −8 dB under speech.
- **CF:** `audio/synth.py` cues `click`, `whoosh`, `tick`; `pulse` off during whips.

---

### Sources
- [Boris FX: Create a Halftone Effect in After Effects (2 methods)](https://borisfx.com/blog/create-after-effects-halftone-plugin-2-methods/)
- [Motion Array: How to Create a Halftone Effect in After Effects](https://motionarray.com/learn/after-effects/halftone-effect-after-effects/)
- [Lesterbanks: How to Make a Halftone Effect in After Effects](https://lesterbanks.com/2022/07/how-to-make-a-halftone-effect-in-after-effects/)
- [YouTube: Halftone effect with customizable dots, no plugins](https://www.youtube.com/watch?v=izniIsXyX7k)
- [Creation Effects: Mixed media collage animations from footage](https://www.creationeffects.com/mixed-media-effect)
- [Envato Tuts+: Collage animation in After Effects](https://photography.tutsplus.com/articles/collage-animation-in-after-effects--cms-93666)
- [aejuice: How to add a stroke to an image in After Effects](https://aejuice.com/blog/how-to-add-a-stroke-to-an-image-in-after-effects/)
- [Modulate: Add an outline to an image, how stroke effects work](https://modulate.to/effects/outline/)
- [Creative COW: Stroke my alpha channel](https://creativecow.net/forums/thread/stroke-my-alpha-channel/)
- [YouTube: Put text behind a subject using RotoBrush](https://www.youtube.com/watch?v=1ufGi84pguE)
- [PremiumBeat: 5 ways to punch up a boring shot with the Rotobrush](https://www.premiumbeat.com/blog/rotobrush-after-effects-tutorial/)
- [tutvid: Whip pan blurring transition in Premiere Pro](https://tutvid.com/premiere-pro/whip-pan-blurring-transition-effect-premiere-pro/)
- [Miracamp: Whip transition in Premiere Pro](https://www.miracamp.com/learn/premiere-pro/whip-transition)
- [Miracamp: How to add motion blur in Premiere Pro](https://www.miracamp.com/learn/premiere-pro/motion-blur)
- [Creative COW: Text blur reveal (After Effects)](https://creativecow.net/after-effects-tutorial-text-blur-reveal/)
- [Adobe: Animating text in After Effects](https://helpx.adobe.com/after-effects/using/animating-text.html)
- [Sickboat: Kinetic type in Premiere Pro + After Effects](https://sickboat.com/blogs/blog/how-to-add-kinetic-type-in-premiere-pro-after-effects-kinetic-type-tutorial)
- [YouTube: Viral podcast reel editing in Premiere Pro](https://www.youtube.com/watch?v=cnt5mAHvWJI)
- [YouTube: Documentary-style paper texture effects in After Effects](https://www.youtube.com/watch?v=HEfXX_sOvKA)
- [Shutterstock: Enhance stills in your documentary with After Effects](https://www.shutterstock.com/blog/tips-to-enhance-stills-in-documentary-film)

---

## 4. Production prompt and reusable template
### A. Production Prompt: *description of the reference Video-28430.mp4*
> This describes the reference itself, content included. Names and figures on screen (e.g. the cheque) belong to the reference and must be replaced with the client's own truth when the style is reused.

```
Create a complete 12-second, 16:9 podcast-clip edit in a blue-grid editorial collage style,
turning a talking-head podcast moment ("I have written for television, film, radio, print ads…
when I was 19 I was like a… pay cheque") into a kinetic mixed-media piece.

Style: print-inspired mixed media. Flat royal-blue grid paper, B&W halftone cut-outs,
white sticker outlines, paper-label captions, giant condensed type. Fast, witty, editorial;
think magazine collage in motion. Must not be glossy, 3D, neon or gradient-heavy.

REFERENCES
@Footage1 = podcast wide shots of Speaker A and Speaker B in a red/black foam studio → live beats + rotoscoped sticker cut-outs.
@Photo1   = old B&W photo of Speaker A, arms crossed → halftone "memory" cut-out.
@Photo2   = young Speaker A head → line-screen halftone for the final poster.
@Props    = vintage TV, clapperboard, radio, magazine cover, hand holding a cheque → B&W PNG cut-outs.

CREATIVE APPROACH
The story: hook caption → the list of media builds up as a collage → live proof with sticker captions
→ the other host asks the money question → memory beat "When I was 19" → the cheque → PAY CHEQUE poster.
Two worlds alternate: the flat blue graphic table and the real studio footage, linked by blur-through-cuts
and one whip pan. Captions always sit in the empty half of the frame, away from the speaker's face.

VISUAL SYSTEM
Background: #415BFC with a 1 px white grid (100 px cells at 1080p, 13 %), paper grain 6 %, soft top-centre lift #6782FF.
Brand colours: blue #415BFC, ink-blue #2F4BE0, paper #F4F4F6, white #FFFFFF, lavender #E4E7FF, ink #111111.
Materials: sticker cut-outs with a 14 px uneven white outline; white rounded cards (r 16) with a blue inner well;
B&W objects breaking out of the well; halftone dots (fine, coarse) and line-screen; soft drop shadows.
Lighting: flat, graphic; live footage keeps its practical studio light.
Typography: captions Inter Medium 38 px white sentence case; card labels extended black caps 40 px #2F4BE0;
sticker captions Bebas Neue/Oswald Bold caps 60 px black on paper labels, emphasis word 100 px #2F4BE0;
story words Inter SemiBold 72 px white; giant number Inter Black ≈600 px lavender; payoff Anton ≈600 px white.

MOVEMENT
A virtual 2D camera over the collage: 3–5-frame pans (±30 % width) with motion blur, slow push-ins and a constant
linear drift. Every card and label pops with back-out overshoot (8→110→100 % in 6 f). Captions type on letter by
letter, each word rising from one line below. World switches use blur-through-cut (3 f out, 5 f in); the shot-to-shot
switch uses a directional whip with an offset wrap (10 f).

EXACT 12-SECOND CHOREOGRAPHY
0.00–1.08s | HOOK
Blue grid. Speaker A sticker cut-out settles 135→100 % in 6 f, centred. Below it, left-aligned, "I have written for"
types on word by word, synced to speech (I · have · written · for). Holds 0.16 s, then snaps off at 1.08.
1.08–2.12s | TELEVISION
The speaker slides right to x 62 % while the camera pushes in 10 %. The "TELEVISION" card (vintage TV breaking out of the
blue well) pops in at the upper left: 8→110→100 % in 7 f. Everything drifts. At 2.08 the camera pans left 30 % in 4 f.
2.12–2.84s | FILM
The "FILM" card (clapperboard at −25°) swings in from the right, oversized, and settles. The TV card crops at the left edge.
2.84–3.60s | RADIO
The camera pans back right and pushes in. The "RADIO" card (radio at −15°) flies in from the lower left, stacking over the TV card.
The FILM card slides to a sliver at the right edge.
3.60–4.52s | PRINT ADS → BLUR
The "PRINT ADS" card (fanned magazine covers) pops in, the camera pans right, and it holds 0.4 s. Gaussian blur 0→40 px over 3 f; CUT.
4.52–5.96s | LIVE, SPEAKER A
Wide studio shot blurs in (5 f). On the right, over the blue LED wall, white paper labels stack and pop on the spoken words:
"I HAVE" / "WRITTEN" (blue, big, −10°) / "ALL KIND" / "OF STUFFS". Whip left at 5.80 (offset wrap + directional blur 250).
5.96–7.84s | LIVE, SPEAKER B
The reverse shot of Speaker B lands from the whip. On the left: "WHEN DID YOU" / "STARTED MAKING" / "MONEY" (blue, big) /
"OF YOU" / "DOING CONTENT", each popping on its word. Blur-out 4 f; CUT to clean blue at 7.84.
7.84–9.52s | WHEN I WAS 19
A halftone cut-out of Speaker A (arms crossed) rises from below, unblurring, and settles at 8.12. "When" (left) and "was" (right)
blur-fade in. A giant lavender "19" rises behind the subject at 8.32–8.56. "When/was" blur out; "i was" and "like a"
blur in at 8.88–9.12. The whole layer blurs and fades to empty blue by 9.52.
9.52–10.76s | THE CHEQUE
A coarse-halftone hand holding a clean cheque flies in from the top right (−20°→−3°, 6 f) and wobbles.
From 10.32, "PAY CHEQUE" fills the frame in white ultra-condensed caps, revealing left→right per character, while the
cheque dissolves underneath. Solid by 10.76.
10.76–12.00s | POSTER
At 11.00 a line-screen halftone head pops onto the "C" (20→108→100 %, 4 f) with a down-right drop shadow.
Finish revealing everything by 11.12. Hold the poster until 12.00. Only a tiny scale drift moves.

AUDIO
The dialogue carries the clip. Paper pop/click on every card and label; whoosh on the blur-cuts and the whip; soft riser
into "19"; low thump on "PAY CHEQUE". Music (if any) ducked −8 dB under the speech. (The reference audio was not heard.)

QUALITY AND CONSTRAINTS
Every caption is readable before it leaves. Captions never cover a face. Only spoken words appear as captions.
Palette stays blue, white and B&W. No colour props, no gradients beyond the soft top lift, no lens flares, no watermarks.
```

---

### B. Reusable template: "blue-grid collage podcast edit" (fill in for any clip)

```
Create a complete <N>-second, <16:9 | 9:16> podcast-clip edit for <SHOW/CLIENT>, in the blue-grid editorial collage style.

Inputs to gather: podcast footage (2 angles if possible), transcript with word times, 1–2 old photos of the guest,
3–5 object PNGs that illustrate the list the guest speaks, 1 hero prop for the payoff line.

Beat plan (keep these proportions; scale to N):
 0–9 %    HOOK        sticker cut-out settles; first spoken phrase types on beneath
 9–38 %   LIST BUILD  one card per listed noun, pops on the spoken word; 2D camera pans between them; cards stack
 38–50 %  LIVE A      blur-through-cut to footage; paper-label caption stack on the empty side; emphasis word blue
 50–65 %  LIVE B      whip to the reverse angle; the question as a label stack on the opposite side
 65–79 %  MEMORY      clean blue; halftone old photo rises; big number/word behind the subject; 2 story words each side
 79–100 % PAYOFF      hero prop flies in; payoff words fill the frame; halftone face pops on the key letter; hold

System: #415BFC · grid 100 px at 13 % · grain 6 % · paper #F4F4F6 · ink-blue #2F4BE0 · B&W halftone photography only.
Motion: pop 6 f back-out · pan 4 f blurred · blur-through-cut 3+5 f · whip 10 f · drift always on.
Type: Inter (captions) · extended black caps (card labels) · Bebas/Oswald (stickers) · Anton (payoff).
Rules: captions = spoken words only; never over a face; one emphasis word per stack; ≥ 35 % empty blue.
```

### C. Checklist before exporting an edit in this style
- [ ] Every card or label pop lands on the spoken word, within ±2 frames.
- [ ] The grid and grain sit on one background layer (not per scene), so they don't jump at the cuts.
- [ ] Sticker outlines are the same width on every live cut-out.
- [ ] Halftone type is consistent in meaning: dots = memory/props, lines = poster.
- [ ] Each caption is on screen for ≥ 0.6 s + 0.22 s × words.
- [ ] Blur transitions only switch worlds, and the whip only switches shots.
- [ ] The last frame is a finished poster (the hold is ≥ 0.9 s).

---

## 5. Lessons from applying it (AASTHI · Vamshi founder edit, 9:16)

- **Re-colour the system, keep the grammar.** Royal blue became AASTHI violet #5B4FDB. Emphasis labels are violet with gold #E3B34A text, and paper is AASTHI cream #F7F1EC. The logo sits on a cream badge, because a violet logo on a violet world disappears.
- **9:16 layout.** Captions go in the chest band (y ≈ 1050–1500) on the side away from the face, never in the top 12 % or bottom 20 %. Mark the face region `data-clear` so the checker flags any caption over it.
- **World switch = background drop.** Cut to the violet world with the cut-out at scale 1 (same position as the footage), then shrink it. The room seems to vanish around him, which reads as a match cut.
- **Sticker cut-outs from talking-head footage.** Use rembg `u2net_human_seg` (≈0.75 s/frame on CPU) and cache the masks. Smooth each mask over 3 frames (0.25/0.5/0.25), keep the largest blob, and bake a 16 px cream outline and a soft shadow into RGBA WebP. Only matte the frames of the world windows.
- **Pitfalls hit:** `np.roll` shadows wrap around (zero the wrapped rows). Dark sofas survive the matte, so key near-black pixels in the bottom band. The ragged bottom edge gets pushed off-frame by shifting the cut-out down ~90–100 px.
- **Text behind the subject needs measuring.** Place the giant word so the head overlaps only the bottom of the letters (e.g. "JOB.", "4", "IN INDIA."), then verify on a snapshot.
- **Uppercase styles break brand casing.** `text-transform: uppercase` turns NRIs into NRIS; wrap the lowercase letter in a `text-transform:none` span.
- **Audio: never run the founder's voice through the synth.** It adds reverb and saturation. Instead, keep the voice untouched and mix a separate music bed (sidechain-ducked, ×0.22) plus SFX (×0.55) with ffmpeg. The result is about −14 LUFS with the voice on top.
- **Keep source quality.** Extract frames at `-q:v 1` and render at CRF 14. Then re-encode the renderer's full-range output to standard-range BT.709 so the colours match the original on every platform.
- **Environment gotcha:** a stray `FFMPEG` env var pointing at a folder breaks render.mjs. Set `FFMPEG` to the actual ffmpeg.exe.
- **End card:** hold ≥ 1.5 s after the last word (extended 42 → 44 s) so the tagline can be read.
