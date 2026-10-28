#!/usr/bin/env node
// Render a Chitram film page to MP4, or capture snapshots / a contact sheet.
//
//   node bin/render.mjs <project> [--out film.mp4] [--fps 30] [--crf 17] [--workers 4]
//                        [--from 0] [--to 12] [--draft] [--audio path.wav] [--no-audio]
//   node bin/render.mjs <project> --at 1.5,4,9.2 [--sheet]      (PNG snapshots + contact sheet)
//   node bin/render.mjs <project> --at scenes                   (storyboard sheet: every scene midpoint)
//   node bin/render.mjs <project> --at every:2                  (a frame every 2 s)
//
// --draft = half resolution, 15 fps, fast preset (for review only).
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawn, spawnSync } from "node:child_process";
import { serve, launch, openFilm, parseArgs, resolveProject } from "./lib.mjs";

const args = parseArgs(process.argv.slice(2));
const { dir, entry } = resolveProject(args._[0]);
const ffmpeg = process.env.FFMPEG || "ffmpeg";

function run(cmd, a) {
  const r = spawnSync(cmd, a, { stdio: ["ignore", "ignore", "pipe"] });
  if (r.status !== 0) throw new Error(`${cmd} failed: ${r.stderr.toString().slice(-2000)}`);
}

async function snapshots(spec) {
  const { server, port } = await serve(dir);
  const browser = await launch();
  const { page, cfg, logs } = await openFilm(browser, port, entry);
  let times;
  if (spec === "scenes" || spec === "auto") {
    // storyboard sheet: midpoint of every scene container ([data-in]/[data-out]) + first and last frame
    times = await page.evaluate((D) => {
      const ts = new Set([0.4, Math.max(0, D - 0.2)]);
      document.querySelectorAll("[data-in],[data-out],[data-scene]").forEach((el) => {
        const a = el.dataset.in != null ? +el.dataset.in : 0, b = el.dataset.out != null ? +el.dataset.out : D;
        ts.add(+(((a + b) / 2)).toFixed(2));
      });
      return [...ts].sort((x, y) => x - y);
    }, cfg.duration);
    if (times.length < 4) times = Array.from({ length: 9 }, (_, i) => +((cfg.duration * (i + 0.5)) / 9).toFixed(2));
  } else if (String(spec).startsWith("every:")) {
    const st = parseFloat(String(spec).slice(6));
    times = []; for (let t = st / 2; t < cfg.duration; t += st) times.push(+t.toFixed(2));
  } else times = String(spec).split(",").map(Number);
  const outDir = path.join(dir, "snapshots");
  fs.mkdirSync(outDir, { recursive: true });
  const files = [];
  for (const t of times) {
    await page.evaluate((x) => window.__film.seek(x), t);
    const f = path.join(outDir, `t${t.toFixed(2).padStart(6, "0")}.png`);
    await page.screenshot({ path: f });
    files.push({ f, t });
  }
  if (args.sheet !== "false") {
    const cols = Math.min(3, files.length), w = 640, h = Math.round((w * cfg.height) / cfg.width);
    const html = `<html><body style="margin:0;background:#1a1a1a;font:14px monospace;color:#eee">
      <div style="display:grid;grid-template-columns:repeat(${cols},${w}px);gap:8px;padding:8px">
      ${files.map(({ f, t }) => `<div><div style="padding:4px 0">${t.toFixed(2)}s</div><img src="file://${f}" style="width:${w}px;height:${h}px;display:block"></div>`).join("")}
      </div></body></html>`;
    const sheetHtml = path.join(outDir, "_sheet.html");
    fs.writeFileSync(sheetHtml, html);
    const p2 = await browser.newPage({ viewport: { width: cols * (w + 8) + 8, height: 200 } });
    await p2.goto("file://" + sheetHtml);
    await p2.screenshot({ path: path.join(outDir, "contact-sheet.png"), fullPage: true });
    fs.unlinkSync(sheetHtml);
  }
  await browser.close(); server.close();
  files.forEach(({ f }) => console.log(f));
  if (args.sheet !== "false") console.log(path.join(outDir, "contact-sheet.png"));
  if (logs.length) console.log("\nPage problems:\n" + logs.join("\n"));
}

async function renderVideo() {
  const draft = !!args.draft;
  const { server, port } = await serve(dir);
  const browser = await launch();
  const first = await openFilm(browser, port, entry, draft ? 0.5 : 1);
  const cfg = first.cfg;
  const fps = parseFloat(args.fps || (draft ? 15 : cfg.fps));
  const from = parseFloat(args.from || 0), to = Math.min(cfg.duration, parseFloat(args.to || cfg.duration));
  const total = Math.round((to - from) * fps);
  const workers = Math.max(1, Math.min(parseInt(args.workers || Math.min(4, os.cpus().length), 10), total));
  const crf = args.crf || (draft ? 28 : 17);
  const preset = draft ? "veryfast" : args.preset || "medium";
  const out = path.resolve(args.out || path.join(dir, "out", draft ? "draft.mp4" : "film.mp4"));
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "chitram-"));
  const per = Math.ceil(total / workers);
  const t0 = Date.now();
  let done = 0;
  const tick = () => {
    done++;
    if (done % 15 === 0 || done === total) {
      const el = (Date.now() - t0) / 1000;
      process.stdout.write(`\r  frames ${done}/${total}  ${(done / el).toFixed(1)} fps  eta ${Math.max(0, (total - done) / (done / el)).toFixed(0)}s   `);
    }
  };

  async function worker(w, page) {
    const a = w * per, b = Math.min(total, a + per);
    if (a >= b) return null;
    const seg = path.join(tmp, `seg${String(w).padStart(2, "0")}.mp4`);
    const ff = spawn(ffmpeg, ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-i", "-",
      "-c:v", "libx264", "-preset", preset, "-crf", String(crf), "-pix_fmt", "yuv420p", "-profile:v", "high",
      "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", seg], { stdio: ["pipe", "ignore", "pipe"] });
    let err = ""; ff.stderr.on("data", (d) => (err += d));
    const closed = new Promise((res, rej) => ff.on("close", (c) => (c === 0 ? res() : rej(new Error("ffmpeg: " + err)))));
    for (let i = a; i < b; i++) {
      const t = from + i / fps;
      await page.evaluate((x) => window.__film.seek(x), t);
      const buf = await page.screenshot({ type: "jpeg", quality: draft ? 85 : 97 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
      tick();
    }
    ff.stdin.end();
    await closed;
    return seg;
  }

  const pages = [first.page];
  for (let w = 1; w < workers; w++) pages.push((await openFilm(browser, port, entry, draft ? 0.5 : 1)).page);
  console.log(`Rendering ${entry}: ${total} frames @ ${fps}fps, ${workers} workers${draft ? " (draft)" : ""}`);
  const segs = (await Promise.all(pages.map((p, w) => worker(w, p)))).filter(Boolean);
  await browser.close(); server.close();
  process.stdout.write("\n");

  const list = path.join(tmp, "list.txt");
  fs.writeFileSync(list, segs.map((s) => `file '${s}'`).join("\n"));
  const video = path.join(tmp, "video.mp4");
  run(ffmpeg, ["-y", "-f", "concat", "-safe", "0", "-i", list, "-c", "copy", video]);

  const audio = args["no-audio"] ? null : args.audio ? path.resolve(args.audio) : cfg.audio ? path.join(dir, cfg.audio) : null;
  if (audio && fs.existsSync(audio)) {
    run(ffmpeg, ["-y", "-i", video, "-ss", String(from), "-t", String(to - from), "-i", audio, "-map", "0:v", "-map", "1:a",
      "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out]);
  } else {
    if (audio) console.warn("audio file not found: " + audio);
    run(ffmpeg, ["-y", "-i", video, "-c", "copy", "-movflags", "+faststart", out]);
  }
  fs.rmSync(tmp, { recursive: true, force: true });
  const secs = ((Date.now() - t0) / 1000).toFixed(1);
  const mb = (fs.statSync(out).size / 1e6).toFixed(1);
  console.log(`Done: ${out}  (${mb} MB, ${(to - from).toFixed(2)}s, rendered in ${secs}s)`);
  if (first.logs.length) console.log("\nPage problems during render:\n" + first.logs.join("\n"));
}

(async () => {
  try {
    if (args.at) await snapshots(String(args.at));
    else await renderVideo();
  } catch (e) { console.error("\nRENDER FAILED: " + (e.stack || e)); process.exit(1); }
})();
