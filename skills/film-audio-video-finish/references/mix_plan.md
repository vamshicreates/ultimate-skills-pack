# Machine-readable mix plan

The first skill's cue sheet is the creative/source record. This mix plan is an exact rendering decision list for one locked picture. Use seconds measured from the first presented video frame. For constant-frame-rate video, derive them from frame numbers and the rational frame rate; for variable-frame-rate video, use presentation timestamps. Check each cue against picture and sound before final render.

```json
{
  "title": "Film_Name",
  "video": "../Picture_Master.mov",
  "audio_package": "../Film_Name_Sound",
  "output_dir": "../Film_Name_Final",
  "container": "mp4",
  "source_audio": {"mode": "keep", "stream_index": 0, "gain_db": 0},
  "mastering": {"integrated_lufs": -16, "true_peak_dbfs": -1.5, "lra": 11},
  "cues": [
    {
      "id": "MUS001",
      "asset": "SC001_Opening/MUS001_Opening_Tension/MUS001_Opening_Tension_mix.wav",
      "start_seconds": 4.0,
      "gain_db": -8,
      "fade_in_seconds": 0.1,
      "fade_out_seconds": 0.3
    },
    {
      "id": "FOL001",
      "asset": "SC001_Opening/FOL001_Gravel_Footsteps/FOL001_Gravel_Footsteps.wav",
      "start_seconds": 0.5,
      "gain_db": -3,
      "fade_in_seconds": 0.005,
      "fade_out_seconds": 0.02
    }
  ]
}
```

Paths are absolute or relative to this JSON file, except `asset`, which is relative to `audio_package`. Use forward slashes in JSON on Windows too. `container` is `mp4` or `mov`; MP4 stream copy supports H.264, HEVC, AV1, and MPEG-4 video. Choose MOV for ProRes and other MOV-native picture streams. `source_audio.mode` is `keep` or `replace`; `stream_index` selects the source video's audio stream, starting at zero. `replace` excludes the source video's audio, so check for dialogue first. Cue `start_seconds` places the first audible sample. Optional `in_seconds` and `duration_seconds` trim from the cue file; omitting them uses the full file. Gain is in dB; fade fields default to 0.01 second. Every listed asset must exist, be audio, and fit within the picture duration. Silence cues have no asset and are represented by gaps or level automation rather than a file.
