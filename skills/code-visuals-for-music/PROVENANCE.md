# Provenance

Created for Vamshi Creates as a reusable hybrid music-visual skill.

## Chitram

Reviewed repository: https://github.com/santhoshkota11/chitram-frame1

Reviewed revision: `9ef907933cc97dbdcb0ff997868e08246d695a0f`.

Relevant upstream components:

- `MUSICVIDEO.md`: song-driven planning, evolving recurring sets, and shot/transition review.
- `engine/runtime.js`: seekable song-time composition and custom per-frame callbacks.
- `engine/motion-kit.js`, `engine/fx-kit.js`: text, SVG paths, cameras, and effects.
- `audio/music.py`: beat and section candidates from signal analysis.
- `bin/render.mjs`, `bin/check.mjs`: frame rendering, previews, and visual diagnostics.

This package contains original integration guidance and helpers. It does not vendor those components or apply its license to them. The reviewed upstream root had no explicit license file; review upstream terms before redistributing its implementation. Local integration requires obtaining upstream separately.

## Python workflow

Generalized lessons from a local music-video production: signal analysis, separated visual assets, anchor-aligned character cels, procedural paths, bounded rendering, targeted dialogue alignment, and FFmpeg verification. The rejected render is not included or presented as a quality benchmark. The skill explicitly addresses its weaknesses through motion proofs, reference fidelity, and narrative review.

No songs, personal transcripts, production images, credentials, or local project paths are included.
