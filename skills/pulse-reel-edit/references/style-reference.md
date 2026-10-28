# Style reference: what the reference reel does (measured)

Source: a 31 s, 720×1280, 30 fps fashion/dance reel (girl in a red ball gown, mountains and meadow,
song at **~143.5 BPM**, so one beat = **0.418 s**). All 928 frames were measured for sharpness (Laplacian
variance), saturation (red vs everything else), brightness and frame difference, and set against
librosa beat tracking. These numbers are the targets the engine's defaults were tuned to.

## The signature, in one line

**The whole picture breathes in and out of focus on the music, the colour drains and floods back in
waves while the red dress stays red, and nearly every cut is hidden inside a blur peak.**

## Measured rhythm

| Metric | Reference | Engine default |
|---|---|---|
| Shots | 26 in 31 s | from the beat grid |
| Average shot | 1.2 s (≈ 2.9 beats) | 2–4 beats, hero 5, outro 6 |
| Cuts on a beat (±50 ms) | ~all | 100 % (cuts placed on detected beats) |
| Cuts inside a blur peak | ~90 % | 100 % (blur bump centred on each soft cut) |
| Blur peaks | ~8 per 10 s | 8–13 per 10 s |
| Peak blur | ≈ σ 8 px at 720 w (σ 12–14 at 1080 w) | `pulse.max_sigma` 14 |
| Blur ramp | rises ~0.3 s before the cut, decays ~0.4 s after | `pre` 0.30, `post` 0.42 |
| Drop | white flash + switch to the airy grade at 9.7 s (31 %) | drop at ~31 % of the reel |

## Shot list (reference)

| # | Time | Shot | Colour | Transition in |
|---|---|---|---|---|
| 1 | 0.00–0.13 | back, walking, B&W, blurred | B&W | opens blurred |
| 2 | 0.13–0.85 | back, arms up, dress flare | B&W → colour → fades | blur |
| 3 | 0.85–2.00 | back walk → turns to camera | pink → red | frame-blend dissolve |
| 4 | 2.00–3.45 | face close-up, slow digital push-in 100→150 % | full | dress fabric sweeps across lens (in camera) |
| 5 | 3.53–5.67 | hand pose, **"Baby" script title behind her head** | full | push / slide (3–4 frames, motion blur) |
| 6 | 5.67–7.20 | river b-roll, push-in | full | blur |
| 7 | 7.20–8.87 | hand pose, closer | full | blur |
| 8 | 8.87–9.70 | wide, hand on chest, cream sky | full | blur |
| 9 | 9.73–10.60 | closer, hand on chest | out of white, B&W → colour → bleach | **white flash (drop)** |
| 10 | 10.60–11.90 | front twirl, arms up | white-out B&W → red returns first → full | bleach to white |
| 11 | 11.90–13.33 | wide walk/turn | colour pop held (grey world, muted pink dress) → floods | blur |
| 12 | 13.33–14.75 | fabric whips past lens, reveals smile | full | blur |
| 13 | 14.75–15.20 | tilted smile | full | blur |
| 14 | 15.20–16.20 | spin, drains to B&W/pop, back | pop | blur |
| 15–20 | 16.2–24.3 | looking up, back arms up, waving, arms out, arms up | full, airy | blur, every 2–4 beats |
| 21 | 24.33–25.23 | wide spin, warm | full | blur |
| 22 | 25.23–25.80 | green background, bending | full, rich green | push / slide |
| 23 | 25.80–26.60 | bending, smiling | B&W | blur |
| 24 | 26.60–27.75 | fabric fan arc | full | blur |
| 25 | 27.75–30.13 | low angle, overcast sky, back arch | full; **exposure flicker** 29.5–30.2 | blur |
| 26 | 30.13–30.93 | final | **fade to grey** | — |

## Colour (three grade sections)

| Section | Look | Measured |
|---|---|---|
| start → drop | **moody** | near-black shadows (3, 9, 5), muted dark greens, cool grey sky, deep red (181, 26, 26) |
| drop → ~82 % | **airy** | highlights blown to cream (254, 254, 247), lifted, pastel yellow-greens, bright red (235, 66, 60) |
| last ~18 % | **overcast** | rich greens (28, 39, 30 shadows), teal-grey overcast sky, red (220, 49, 47) |

**Colour pop**: during the grey phases the non-red saturation drops to ~0–10 % while the red keeps
~40–60 % (muted pink-red). Colour floods back over ~0.4 s, usually as the shot comes into focus.

## Title

Bold brush-script word ("Baby") in the dress's red, ~20 % from the top, **behind the subject**
(her head and crown hide letters as she moves). It blurs in, warms from orange to red, and drifts up.
It is affected by the global focus pulse too. Font used here: Great Vibes (OFL), bundled.

## Texture

Faint floating dust/drizzle specks in a few shots (8–10.5 s), light grain, no letterbox, no vignette.

## What the raw footage must give you (in-camera)

- **Spins and fabric flares**: the dress is the motion. Shoot them at 60/120 fps.
- **Fabric across the lens**: the natural wipes at 2.0 s and 13.3 s. Code can't fake these.
- **One calm hero shot with headroom** for the title.
- **A b-roll breather** (river, landscape) before the drop.
- **One strong colour on the subject.** The colour pop protects one hue.
