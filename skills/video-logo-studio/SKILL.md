---
name: video-logo-studio
description: Remove or replace a visible logo in an authorized video, including optional PNG/JPEG reference matching, frame review, and branded badge overlays. Use when the user wants a clean copy or a new logo in the same place.
---

# Video Logo Studio

Work on video the user owns or is authorized to edit. Keep the original file and write a separate result. A logo obscures source pixels, so reconstruction can be visually convincing but cannot restore hidden detail exactly.

## Locate the mark

1. Inspect duration, dimensions, frame rate, streams, and representative frames with FFprobe/FFmpeg.
2. For a fixed mark, scan frames across the whole clip and propose a tight region. If the user supplies a PNG or JPEG of the mark, crop excess background and use shape or template matching at several sizes. Verify the match across scenes; a similar-looking title or sign is not enough.
3. Show a diagnostic frame with the proposed region. If confidence is low, inspect it and use a manually selected box. For moving marks, track the supplied template and check tracking after cuts or occlusions.

## Remove and refine

- Start with the smallest mask that covers the mark. A broad rectangular delogo can smear nearby text or faces.
- On detailed or changing backgrounds, examine troublesome frames and refine the mask or use clean neighboring frames for temporal reconstruction. Review every affected scene, not only one still.
- Preserve source resolution and frame rate. Use a high-fidelity video encode unless the user chooses another tradeoff. Copy the audio stream whenever the output container supports it.
- Do a full decode check and inspect frames from bright, dark, moving, and text-heavy sections. Report remaining visible artifacts honestly.

## Optional replacement logo

When the user wants a new mark, use their supplied image as the asset. Extract its visible artwork rather than scaling its outer blank margins. Match the former logo position and keep the image proportional. Preview on varied backgrounds. If the user requests a rounded badge with a moving edge spark, keep the lettering steady and animate only the badge edge. Preserve the audio and the cleaned source as separate files.

## Browser tool variant

For a no-account, no-server-storage website, process in the browser and make the reference image optional. Keep automatic fixed-logo detection and a manual box as fallbacks. Show the proposed region for review before rendering. State practical input limits and that a long high-resolution export can take several minutes or exceed device memory. Do not claim exact recovery under an opaque logo or zero compression loss from a high-fidelity encode.
