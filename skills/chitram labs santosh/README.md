# Chitram Film — studio edition (for Claude.ai and ChatGPT)

A knowledge-heavy motion-design skill: it understands ideas, product references and reference
videos, writes expert timecoded video prompts, and builds films as HTML/CSS/GSAP code with a
preview and an MP4 render path. 15 files — within the Claude.ai skill limit (200) and ChatGPT's
knowledge-file limit (20).

## Claude.ai
1. Upload `chitram-film-web.zip` where you add skills (the same place that rejected the big zip).
2. Make sure code execution is enabled for your account/workspace.
3. Just ask: "make a 30 s launch film for …", "break down this video and give me the prompt", or
   paste a timecoded prompt. The skill loads itself.

## ChatGPT (custom GPT)
1. Create a GPT → Configure.
2. Instructions: paste the whole of `GPT_INSTRUCTIONS.md`.
3. Knowledge: upload `references/DIRECTOR.md`, `references/EXAMPLES.md`, `references/MOTION.md`,
   `references/ENGINE.md`, `assets/runtime.js`, `assets/motion-kit.js`, `assets/kit.css`,
   `scripts/render.mjs`, `scripts/lib.mjs`, `scripts/check.mjs`, `scripts/synth.py`,
   `scripts/cues.example.json` (12 files).
4. Capabilities: turn on Code Interpreter & Data Analysis, Canvas, and Web Browsing.

## Rendering a film to MP4 on your computer
The chat builds the film folder; chat sandboxes usually have no browser, so render locally once:
```bash
npm i playwright-core@1.56.1 && npx playwright-core install chromium   # once; needs Node 18+ and ffmpeg
node scripts/render.mjs <film>/index.html --out film.mp4                # final video
node scripts/render.mjs <film>/index.html --at scenes                   # storyboard / contact sheet
node scripts/check.mjs  <film>/index.html                               # QA gate
python3 scripts/synth.py <film>/cues.json <film>/assets/score.wav       # score + SFX (numpy, scipy)
```
(`scripts/` needs `lib.mjs`, `render.mjs`, `check.mjs` together; put the film folder anywhere.)

## Files
```
SKILL.md                 the studio brain: pipeline, routing, non-negotiables
references/DIRECTOR.md   understanding, concepts, reference-video reading, the prompt format, rubric
references/EXAMPLES.md   10 complete gold-standard examples
references/MOTION.md     After Effects / Premiere / sound / colour / delivery craft, in code terms
references/ENGINE.md     build law, agent loop, film skeleton, kit API, recipes, verification, render
assets/                  runtime.js · motion-kit.js · kit.css (copied into every film)
scripts/                 render.mjs · lib.mjs · check.mjs · synth.py · cues.example.json
GPT_INSTRUCTIONS.md      paste into a custom GPT's Instructions
```
