# timeline.json reference

`python pulse.py plan` writes a draft; you refine it by hand. Times are in seconds. Paths can be
absolute or relative to the timeline file.

```jsonc
{
  "output":  {"width": 1080, "height": 1920, "fps": 30, "path": "renders/reel.mp4", "crf": 16},
  "music":   {"path": "song.mp3", "start": 41.86, "fade_out": 0.6},   // start = where in the song the reel begins
  "duration": 30.0,
  "protect": {"hue": 0, "width": 18, "min_sat": 0.28, "keep": 0.5}, // colour kept in colour-pop (0 = red); keep = its saturation while popped
  "grade": {
    "enabled": true, "correction": true, "white_balance": false,
    "sections": [{"start": 0, "look": "moody"}, {"start": 9.62, "look": "airy"}, {"start": 24.69, "look": "overcast"}]
  },
  "pulse":   {"max_sigma": 14, "pre": 0.30, "post": 0.42, "intro": true,
              "breath_every_beats": 4, "breath_strength": 0.45, "min_shot_for_breath": 1.6},
  "beats":   [0.0, 0.418, ...],                                   // relative to music.start; plan fills this
  "events":  [
    {"t": 9.62, "type": "flash", "dur": 0.14},                    // white flash (the drop)
    {"t": 10.20, "type": "bleach", "dur": 0.30},                  // bleach to white into the next cut
    {"t": 28.5, "type": "flicker", "dur": 0.7},                   // exposure flicker
    {"t": 29.2, "type": "fade_grey", "dur": 0.75},                // fade to grey at the end
    {"t": 12.0, "type": "dip_black", "dur": 0.2}                  // optional
  ],
  "texture": {"dust": [[7.5, 10.4]], "dust_strength": 0.35, "grain": 0.014},
  "shots": [
    {
      "id": "S01", "clip": "footage/A001.MOV",
      "in": 3.20,            // source time where the shot starts
      "dur": 0.836,          // timeline length (the plan snaps these to beats; keep cuts on beats)
      "speed": 0.5,          // 0.5 = half-speed slow motion (needs 60 fps+ source for smoothness)
      "ramp_in": 0.0, "ramp_out": 0.18, "ramp_mult": 2.0,  // fraction of the shot spent speeding up into the next cut
      "zoom": [1.0, 1.06],   // digital push-in start -> end (1.4 = the reference face push-in)
      "center": [0.5, 0.45], // zoom centre (0..1)
      "focus": [0.5, 0.5],   // which part survives the crop when the clip is not 9:16 (0.5 = centre)
      "pan": [[0, 0], [0.02, 0]], // optional drift of the zoom centre
      "color": "pulse",      // full | pop_in | bw_in | pop_out | pop_hold | pop_flood | pulse | bw_hold | [[sec, rest, keep], ...]
      "transition": "blur",  // how this shot ENTERS: blur | cut | push_left | push_right | blend | flash | bleach
      "look": null,          // override the section look for this shot
      "exposure": 0.0,       // extra stops for this shot
      "pulse": true,         // false = no focus pulse at this cut
      "blur_scale": 1.0
    }
  ],
  "titles": [
    {"text": "Baby", "start": 3.69, "end": 5.56, "font": "GreatVibes-Regular.ttf", "size": 230,
     "color": "#E3262E", "color_in": "#FF7A1A", "pos": [0.5, 0.2], "behind_subject": true,
     "anim": "blur_rise", "in": 0.6, "out": 0.25, "drift": 0.004, "shadow": 0.22}
  ]
}
```

## Colour modes

| Mode | What happens over the shot |
|---|---|
| `full` | full colour |
| `pulse` | pop → full colour by 40 % → back to pop at the end (the opening shots) |
| `bw_in` | starts fully B&W, the protected colour appears first, then everything floods in (~0.5 s) |
| `pop_in` | starts popped (only the protected colour), floods to full in 0.4 s |
| `pop_out` | full, drains to popped in the last 0.45 s |
| `pop_hold` | popped the whole shot |
| `pop_flood` | popped until ~62 %, then floods to full |
| `bw_hold` | fully B&W |
| `[[t, rest, keep], …]` | custom keyframes: `rest` = saturation of everything else, `keep` = of the protected colour |

## Looks

`moody`, `airy`, `overcast`, `natural` (light correction only), `none`. Compare them on any clip with
`python pulse.py lookbook clip.mov`. Export them as `.cube` with `python pulse.py luts`.
