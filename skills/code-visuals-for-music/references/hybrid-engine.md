# Python ↔ Chitram integration

## Responsibilities

| Layer | Owner | Output |
|---|---|---|
| Media inspection | Python/ffprobe | Source duration, rate, channels, dimensions |
| Audio analysis | Python, optionally Chitram `audio/music.py` | Candidate beats, accents, energy and sections |
| Transcript alignment | Chosen ASR/alignment backend plus review | Timed lyrics and dialogue with verification status |
| Asset preparation | Python/Pillow or available image tools | Transparent parts, background plates, anchor metadata |
| Composition | Chitram HTML/SVG/Canvas + GSAP | One seekable master timeline |
| Custom effects | Python prebake or browser per-frame callback | Reusable sequence or deterministic state |
| Export | Chitram renderer + FFmpeg | MP4 with source audio |

Select the simplest technique that achieves the requested look. Keep a Python-only renderer if it already delivers the requested motion. A migration is justified by a measurable improvement in control, quality, or iteration.

## Obtain and inspect the engine

The upstream revision reviewed for this package is recorded in `PROVENANCE.md`. Recheck API signatures when using another revision.

```bash
git clone https://github.com/santhoshkota11/chitram-frame1.git /path/to/chitram-frame1
```

Inspect its package/install files before running setup. Its reviewed root package depends on `playwright-core@1.56.1` and vendors GSAP. Install dependencies in the engine directory, then provision the matching Chromium using its instructions. Install Python audio dependencies in an isolated environment. Do not assume system Python has SciPy or Pillow.

Initialize a film using the actual song duration and requested output dimensions:

```bash
node /path/to/chitram-frame1/bin/init.mjs /path/to/film --duration 60 --size 1920x1080 --fps 30
```

Here `60` is an example duration. Replace it with the probed source duration. The upstream initializer copies its engine into the film; inspect dependency terms before sharing that project publicly.

## Timing bridge

Run the included exporter against the reviewed project manifest:

```bash
python3 scripts/project.py export /path/to/project.json --out /path/to/film/assets/project.js
```

Load `assets/project.js` before `Film.build`. It defines:

- `window.CVM`: the project data, including shots, lyric/dialogue cues, sections, and optional energy samples.
- `window.MUSIC`: duration, BPM, beats, downbeats, phrases, accents, sections, and selected drop for `FX.grid()` compatibility.

Every time is in seconds on the untrimmed source-audio clock. Set the film root's `data-audio` to the media path relative to the **film**, not the manifest. If a source is trimmed, retime every cue once and record the offset; never separately offset audio, captions, and scenes.

For analysis, Chitram's `audio/music.py analyse` writes JSON that can inform the manifest. It estimates section labels from energy and assumes 4/4 for downbeats. Manually review important boundaries and speech breaks. The bridge does not automatically endorse or import those labels.

## Original composition pattern

```javascript
Film.build(tl => {
  const project = window.CVM;
  for (const shot of project.shots) {
    const element = document.getElementById(shot.id);
    if (!element) throw new Error(`Missing shot ${shot.id}`);
    element.dataset.in = shot.start;
    element.dataset.out = shot.end;
    // Author action inside each shot. This visibility window is not animation.
  }
  Film.onFrame(t => {
    // Evaluate custom curves, particles, sprite selection, and acting from t.
    // Do not integrate velocity into a mutable position here.
  });
});
```

Use nested wrappers for camera motion, actor travel, body pose, and secondary movement so they do not fight over the same transform. Use SVG path drawing for line reveals; substantial shape morphing requires compatible geometry or a custom interpolator. Chitram's neon-path helper does not supply arbitrary character morphs.

For Python effects too expensive to recompute in the browser, prebake an image sequence and use upstream `data-seq`, `data-seq-fps`, `data-count`, and `data-at`. Transparent PNG frames preserve alpha. Check a first/middle/last frame for scale and premultiplication halos. Avoid exporting a giant PNG sequence when a vector representation suffices.

## Preview and render

```bash
node /path/to/chitram-frame1/bin/preview.mjs /path/to/film
node /path/to/chitram-frame1/bin/render.mjs /path/to/film --from 12 --to 20 --draft
node /path/to/chitram-frame1/bin/check.mjs /path/to/film --strict
node /path/to/chitram-frame1/bin/render.mjs /path/to/film --out /path/to/film/out/film.mp4
ffprobe -v error -show_streams -show_format -of json /path/to/film/out/film.mp4
ffmpeg -v error -i /path/to/film/out/film.mp4 -f null -
```

The browser renderer captures and encodes individual frames. It may be slower for large blurs and layered effects; benchmark the real scene. Its QA samples frames and text boxes; a clean result is not proof of reference fidelity, fluent acting, transcript accuracy, or comprehensive flash safety.

If Chitram is unavailable, preserve the project data and prototype with the available renderer. Explain the changed implementation. Never claim a Chitram render or preview was tested when only the source code was inspected.
