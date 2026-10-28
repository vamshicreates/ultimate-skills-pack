#!/usr/bin/env node
// Scaffold a new film project:   node bin/init.mjs <dir> [--duration 30] [--size 1920x1080] [--fps 30]
// Copies the engine (runtime, kit, fonts, gsap) into <dir>/engine so the project is self-contained.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "./lib.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const skill = path.resolve(here, "..");
const args = parseArgs(process.argv.slice(2));
const dest = path.resolve(args._[0] || "film");
const [w, h] = String(args.size || "1920x1080").split("x").map(Number);
const duration = args.duration || 30, fps = args.fps || 30;

if (fs.existsSync(path.join(dest, "index.html")) && !args.force) { console.error(`${dest}/index.html exists (use --force)`); process.exit(1); }
fs.mkdirSync(path.join(dest, "assets"), { recursive: true });
fs.cpSync(path.join(skill, "engine"), path.join(dest, "engine"), { recursive: true });
// --template shortform  -> 9:16 talking-head edit (footage world + graphic world + synced captions)
const tplName = args.template === "shortform" ? "shortform.html" : "index.html";
let tpl = fs.readFileSync(path.join(skill, "template", tplName), "utf8");
tpl = tpl.replaceAll("{{W}}", w).replaceAll("{{H}}", h).replaceAll("{{DURATION}}", duration).replaceAll("{{FPS}}", fps);
if (tplName === "shortform.html") {
  // --frames N --face x,y,w,h (from sf.py: frames count, faces.json summary.box_px)
  const [fx, fy, fw, fh] = String(args.face || `${Math.round(w * .3)},${Math.round(h * .15)},${Math.round(w * .4)},${Math.round(h * .25)}`).split(",");
  tpl = tpl.replaceAll("{{FRAMES}}", args.frames || Math.round(duration * fps))
    .replaceAll("{{FACE_X}}", fx).replaceAll("{{FACE_Y}}", fy).replaceAll("{{FACE_W}}", fw).replaceAll("{{FACE_H}}", fh);
}
fs.writeFileSync(path.join(dest, "index.html"), tpl);
// sound starts from a mix sheet (SOUND.md / MUSIC.md): voice, music fitted to the cut, anchored library SFX
fs.writeFileSync(path.join(dest, "mix.json"), JSON.stringify({ duration: +duration, voice: null, music: null, sfx: [],
  lufs: -14, true_peak: -1 }, null, 1));
console.log(`Film project ready: ${dest}
  edit      ${path.join(dest, "index.html")}
  preview   node ${path.join(skill, "bin/preview.mjs")} ${dest}
  check     node ${path.join(skill, "bin/check.mjs")} ${dest}
  snapshot  node ${path.join(skill, "bin/render.mjs")} ${dest} --at 1,5,10
  music     python3 ${path.join(skill, "audio/music.py")} analyse <track.mp3>      (MUSIC.md: beats, drop, sections)
  audio     python3 ${path.join(skill, "audio/mixdown.py")} ${path.join(dest, "mix.json")} ${path.join(dest, "assets/mix.wav")}
  render    node ${path.join(skill, "bin/render.mjs")} ${dest} --out ${path.join(dest, "out/film.mp4")}`);
