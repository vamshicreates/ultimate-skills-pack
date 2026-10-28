# Cue sheet JSON for the PDF breakdown

Create one JSON document for the whole picture. The PDF builder requires every scene to include all five category objects: `music`, `foley`, `ambience`, `sfx`, and `silence`. Each object contains `cues`. For an unused category, give an empty list and a specific `none_reason`.

Time strings should state both a readable timecode and the source frame index or presentation timestamp. Use the picture master's actual timing; the following values only illustrate the shape. `asset` is a path relative to the film sound package root. The delivered file must exist before final handoff.

```json
{
  "film_title": "Example Film",
  "source_file": "picture_master.mov",
  "frame_rate": "24/1",
  "duration": "00:12:34:00",
  "version": "2026-10-11",
  "scenes": [
    {
      "id": "SC001",
      "name": "Opening Road",
      "time": "00:00:00:00–00:00:12:00 (frames 0–287)",
      "picture": "A lone person walks toward a distant light; cut to a close-up of shoes at frame 96.",
      "production_audio": "No dialogue. Existing wind is faint; inspect whether it is usable.",
      "sound_direction": "Begin sparse and grounded. Let the first visible footfall establish scale before music enters.",
      "music": {
        "cues": [
          {
            "id": "MUS001",
            "name": "Opening_Tension",
            "time": "00:00:04:00–00:00:12:00 (frames 96–287)",
            "sync": "Enter after the shoe close-up; add a low pulse on frame 144.",
            "description": "Muted low A pulse, narrow airy pad, no melody; intensity slowly rises toward the cut.",
            "method": "Original Python synthesis and composition; 48 kHz, 24-bit WAV.",
            "mix": "Keep below footfalls; leave the speech range open for the next scene.",
            "status": "delivered",
            "asset": "SC001_Opening_Road/MUS001_Opening_Tension/MUS001_Opening_Tension_mix.wav"
          }
        ]
      },
      "foley": {
        "cues": [
          {
            "id": "FOL001",
            "name": "Gravel_Footsteps",
            "time": "00:00:00:12–00:00:11:18 (frames 12–282)",
            "sync": "Individual heel and toe contacts follow visible steps.",
            "description": "Dry gravel crunch with changing weight and distance as the person approaches.",
            "method": "Layered from user-owned recordings, with pitch and level variation.",
            "mix": "Center-biased, slightly wider as the person nears the camera.",
            "status": "delivered",
            "asset": "SC001_Opening_Road/FOL001_Gravel_Footsteps/FOL001_Gravel_Footsteps.wav"
          }
        ]
      },
      "ambience": {
        "cues": [],
        "none_reason": "Production wind is retained; no replacement ambience is needed."
      },
      "sfx": {
        "cues": [],
        "none_reason": "No designed transition or impact is needed in this scene."
      },
      "silence": {
        "cues": [],
        "none_reason": "No deliberate full silence in this scene."
      }
    }
  ]
}
```

For a `silence` cue, include the same ID, name, time, sync, description, method, mix, and status fields. It has no `asset` because the absence of sound is intentional. The PDF generator validates unique scene and cue IDs, required detail fields, and absence reasons.
