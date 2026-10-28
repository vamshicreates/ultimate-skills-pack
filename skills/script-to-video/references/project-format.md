# Animatic manifest

For strict coverage, point `dialogue_ledger` at a JSON array of `{id, character, text}` entries. With `one_image_per_dialogue: true`, the helper rejects missing, extra, or changed lines and any reused image file between spoken turns.

Place `animatic.json` in the project root. Keep source screenplay, storyboard files, clean shot images, and dialogue clips nearby. The preparation helper writes only to `edit/` and replaces its generated files on rerun; keep manual NLE changes in a separate copy.

```json
{
  "title": "Example scene",
  "fps": 25,
  "width": 1920,
  "height": 1080,
  "captions": true,
  "one_image_per_dialogue": true,
  "dialogue_ledger": "dialogue_ledger.json",
  "shots": [
    {
      "id": "S001-SH001",
      "image": "shots/S001-SH001.png",
      "duration_s": 3.2,
      "camera": "Wide, static, entrance on screen left",
      "dialogue": [
        {
          "id": "S001-D001",
          "character": "Maya",
          "text": "We should leave now.",
          "audio": "voices/S001-D001.wav",
          "offset_s": 0.4
        }
      ]
    }
  ]
}
```

Each `shots[]` item is a distinct visual shot in timeline order. `one_image_per_dialogue: true` rejects shots with multiple dialogue turns, ensuring that every line is mapped to its own image. Add silent shots for establishing geography and reactions. Durations snap to the nearest output frame. Dialogue `offset_s` is measured from the shot's start. A dialogue clip must end inside its shot. Use a separate shot with an intentional reaction hold when the image should outlast the voice. IDs are stable across revisions; they connect screenplay lines, voice assets, boards, and the edit. All image and audio paths can be relative to the manifest or absolute. Canvas dimensions must be even. The helper checks asset existence, IDs, audio durations, and shot bounds before producing the EDL and OTIO timeline.

The bridge produces still-based animatic clips. Use video-use's EDL as the working render plan and update its ranges/overlays when refining pacing. The `.otio` preserves separate per-character audio files; its video track uses silent picture clips. The `render_sources` clips embed the same voice audio for video-use's current renderer, which expects a video source with audio. Do not stack those embedded-audio clips under the OTIO dialogue tracks in an NLE or dialogue will play twice.
