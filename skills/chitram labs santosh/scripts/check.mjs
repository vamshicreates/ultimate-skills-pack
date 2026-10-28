#!/usr/bin/env node
// QA gate. Run before every full render:   node bin/check.mjs <project>
// Static:  determinism bans, external URLs, CSS animations, unknown fonts.
// Runtime: script errors, missing assets, timeline length, and a text audit sampled over
//          the whole film (off-frame / outside safe area, overlapping captions, text that
//          is not on screen long enough to read).
// Pixel pass: contrast of every caption against what is really behind it, busy backgrounds,
//          text over [data-clear] elements (mark screens/logos/faces you must not cover),
//          near-empty frames and harsh brightness flashes.   --fast skips the pixel pass.
// Exit code 1 if any ERROR is found (or any warning with --strict).
import fs from "node:fs";
import path from "node:path";
import { serve, launch, openFilm, parseArgs, resolveProject } from "./lib.mjs";

const args = parseArgs(process.argv.slice(2));
const { dir, entry } = resolveProject(args._[0]);
const errors = [], warns = [];
const E = (m) => errors.push(m), W = (m) => warns.push(m);

// ---------------- static ----------------
const html = fs.readFileSync(path.join(dir, entry), "utf8");
const localScripts = [...html.matchAll(/<script[^>]*src="([^"]+)"/g)].map((m) => m[1]).filter((s) => !/^https?:/.test(s) && !/engine\//.test(s) && !/(^|\/)(runtime|motion-kit|gsap(\.min)?)\.js$/.test(s));
const sources = [["" + entry, html], ...localScripts.map((s) => [s, fs.existsSync(path.join(dir, s)) ? fs.readFileSync(path.join(dir, s), "utf8") : ""])];
for (const [name, src] of sources) {
  const code = name.endsWith(".html") ? [...src.matchAll(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g)].map((m) => m[1]).join("\n") : src;
  if (/Math\.random\s*\(/.test(code)) E(`${name}: Math.random() — use MK.rng(seed)`);
  if (/Date\.now\s*\(|new Date\s*\(|performance\.now\s*\(/.test(code)) E(`${name}: clock reads (Date/performance.now) — frames must depend only on t`);
  if (/repeat\s*:\s*-1/.test(code)) E(`${name}: repeat:-1 — use MK.repeats(span, period)`);
  if (/\.play\s*\(\s*\)/.test(code)) E(`${name}: tl.play()/video.play() — the renderer seeks; never play`);
  if (/setTimeout|setInterval|requestAnimationFrame/.test(code)) W(`${name}: timers/rAF in film code — animation must live on the timeline`);
  if (/fetch\s*\(|XMLHttpRequest/.test(code)) E(`${name}: network fetch in film code — inline or bundle data`);
}
if (!/data-film/.test(html)) E("no [data-film] root");
if (!/data-duration="[\d.]+"/.test(html)) E("root is missing data-duration");
if (!/Film\.build\s*\(/.test(html)) E("no Film.build(tl => {...}) call");
const OKHOST = /^(https?:\/\/)(fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net)\//;
for (const m of html.matchAll(/(?:src|href)="(https?:\/\/[^"]+)"/g)) (OKHOST.test(m[1]) ? W : E)(OKHOST.test(m[1]) ? `uses ${m[1]} — needs network at render time (fine locally; offline: put gsap.min.js next to index.html)` : `external URL ${m[1]} — download it into assets/`);
if (/@keyframes|animation\s*:|animation-name/.test(html)) W("CSS @keyframes/animation found — not seekable; move it onto the GSAP timeline");
if (/transition\s*:\s*(?!none)/.test(html)) W("CSS transition found — frames may capture mid-transition; remove it");
for (const m of html.matchAll(/<video[^>]*src="([^"]+)"/g)) if (!/\.webm$/i.test(m[1])) W(`video ${m[1]}: Chromium may not decode H.264 — convert with tools/prep_video.sh (webm or image sequence)`);
// fonts
const faces = new Set();
const fontCss = [html];
const sharedEngine = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..", "engine");
for (const m of html.matchAll(/<link[^>]*href="([^"]+\.css)"/g)) {
  let p = path.join(dir, m[1]);
  if (!fs.existsSync(p) && m[1].startsWith("engine/")) p = path.join(sharedEngine, m[1].slice(7));
  if (fs.existsSync(p)) fontCss.push(fs.readFileSync(p, "utf8"));
}
for (const css of fontCss) for (const m of css.matchAll(/@font-face\s*{[^}]*font-family\s*:\s*["']?([^"';]+)["']?/g)) faces.add(m[1].trim().toLowerCase());
for (const m of html.matchAll(/fonts\.googleapis\.com\/css2?\?([^"]+)"/g))
  for (const f of m[1].split("&")) if (f.startsWith("family=")) faces.add(decodeURIComponent(f.slice(7).split(":")[0].replace(/\+/g, " ")).toLowerCase());
const generic = new Set(["serif", "sans-serif", "monospace", "system-ui", "ui-sans-serif", "cursive", "inherit", "initial"]);
const vars = {};
for (const css of fontCss) for (const m of css.matchAll(/(--[\w-]+)\s*:\s*([^;}]+)/g)) vars[m[1]] = m[2].trim();
const resolveVar = (v) => { let k = 0; while (/var\((--[\w-]+)\)/.test(v) && k++ < 5) v = v.replace(/var\((--[\w-]+)\)/, (_, n) => vars[n] || ""); return v; };
const used = new Set();
for (const m of html.matchAll(/font-family\s*:\s*([^;}"]+)/g)) used.add(resolveVar(m[1]).split(",")[0].replace(/['"]/g, "").trim().toLowerCase());
for (const m of html.matchAll(/font\s*:\s*[^;}"]*?\d+px(?:\/[\d.]+)?\s+['"]?([A-Za-z][^,;'"}]*)/g)) used.add(resolveVar(m[1].trim()).split(",")[0].replace(/['"]/g, "").trim().toLowerCase());
for (const f of used) if (f && !generic.has(f) && !faces.has(f)) W(`font "${f}" has no @font-face — it will fall back to a system font`);

// ---------------- runtime ----------------
const { server, port } = await serve(dir);
const browser = await launch();
let cfg;
try {
  const film = await openFilm(browser, port, entry, 0.5);
  cfg = film.cfg;
  const page = film.page;
  const netOK = /(fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net)/;
  film.logs.forEach((l) => (/requestfailed|http 4|pageerror/.test(l) && !netOK.test(l) ? E(l) : W(netOK.test(l) ? l + "  (no network here — fonts/CDN will load on a normal machine)" : l)));
  const tlDur = await page.evaluate(() => window.__film.timelineDuration());
  if (tlDur > cfg.duration + 0.05) W(`timeline runs to ${tlDur.toFixed(2)}s but film is ${cfg.duration}s — tweens after the end are cut`);
  const step = parseFloat(args.step || 0.2);
  const samples = [];
  for (let t = 0; t <= cfg.duration + 1e-6; t += step) {
    await page.evaluate((x) => window.__film.seek(x), t);
    const vis = await page.evaluate(({ W, H }) => {
      const out = [];
      const els = document.querySelectorAll(".t, [data-qa=text]");
      els.forEach((el, idx) => {
        if (!el.id) el.id = "__t" + idx;
        let op = 1, n = el, hidden = false, clipped = false;
        while (n && n.nodeType === 1) {
          const cs = getComputedStyle(n);
          op *= parseFloat(cs.opacity);
          if (cs.visibility === "hidden" || cs.display === "none") hidden = true;
          if (cs.clipPath && cs.clipPath !== "none") clipped = true;   // mid-wipe / iris: geometry unreliable
          n = n.parentElement;
        }
        // real text only: skip kit overlays (sweep / glitch clones) and measure glyph boxes
        let text = "", x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
        const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, { acceptNode: (nd) => nd.parentElement.closest(".mk-sweep,.mk-glitch,.sw,[aria-hidden=true]") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
        while (tw.nextNode()) {
          const nd = tw.currentNode;
          if (!nd.textContent.trim()) continue;
          const pe = nd.parentElement, pcs = getComputedStyle(pe);
          if (pcs.display === "none" || pcs.visibility === "hidden") continue;
          text += nd.textContent;
          const rg = document.createRange(); rg.selectNodeContents(nd);
          for (const r of rg.getClientRects()) { if (r.width < 1) continue; x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom); }
        }
        text = text.replace(/\s+/g, " ").trim();
        if (hidden || op < 0.6 || !text || x1 < x0) return;
        if (x1 <= 0 || y1 <= 0 || x0 >= W || y0 >= H) return;                 // entirely off-frame = not on screen
        out.push({ id: el.id, text: text.slice(0, 40), words: text.split(" ").length, op, clipped, x: x0, y: y0, w: x1 - x0, h: y1 - y0 });
      });
      const clear = [];
      document.querySelectorAll("[data-clear]").forEach((el, k) => {
        let op = 1, n = el, hid = false;
        while (n && n.nodeType === 1) { const cs = getComputedStyle(n); op *= parseFloat(cs.opacity); if (cs.visibility === "hidden" || cs.display === "none") hid = true; n = n.parentElement; }
        if (hid || op < 0.5) return;
        const r = el.getBoundingClientRect();
        if (r.width > 2 && r.height > 2) clear.push({ name: el.dataset.clear || el.id || "clear" + k, x: r.left, y: r.top, w: r.width, h: r.height });
      });
      return { out, clear };
    }, { W: cfg.width, H: cfg.height });
    samples.push({ t, vis: vis.out, clear: vis.clear });
  }
  const safeX = cfg.width * 0.04, safeY = cfg.height * 0.04;
  const reported = new Set();
  const onTime = {};
  const lastBox = {};
  for (const { t, vis, clear } of samples) {
    for (const v of vis) for (const c of clear) {
      const ix = Math.max(0, Math.min(v.x + v.w, c.x + c.w) - Math.max(v.x, c.x));
      const iy = Math.max(0, Math.min(v.y + v.h, c.y + c.h) - Math.max(v.y, c.y));
      const key = "cl" + v.id + c.name;
      if (ix * iy > 0.05 * v.w * v.h && !reported.has(key)) { reported.add(key); W(`t=${t.toFixed(1)}s "${v.text}" overlaps protected element [${c.name}]`); }
    }
    for (const v of vis) {
      if (v.op > 0.85) onTime[v.id] = onTime[v.id] || { text: v.text, words: v.words, runs: [], cur: null };
      const o = onTime[v.id];
      if (o && v.op > 0.85) { if (o.cur && Math.abs(o.cur.end - (t - step)) < 1e-6) o.cur.end = t; else { o.cur = { start: t, end: t }; o.runs.push(o.cur); } }
      const off = v.x < safeX || v.y < safeY || v.x + v.w > cfg.width - safeX || v.y + v.h > cfg.height - safeY;
      const key = "off" + v.id;
      const prevBox = lastBox[v.id]; lastBox[v.id] = v;
      const still = prevBox && Math.abs(prevBox.x - v.x) < 3 && Math.abs(prevBox.y - v.y) < 3;  // moving text may cross edges mid-transition
      if (off && still && !v.clipped && !reported.has(key)) { reported.add(key); W(`t=${t.toFixed(1)}s "${v.text}" is outside the 4% safe area (box ${Math.round(v.x)},${Math.round(v.y)} ${Math.round(v.w)}x${Math.round(v.h)})`); }
    }
    for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) {
      const a = vis[i], b = vis[j];
      if (a.id === b.id || a.clipped || b.clipped) continue;
      const ix = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x));
      const iy = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
      const small = Math.min(a.w * a.h, b.w * b.h);
      const key = "ov" + [a.id, b.id].sort().join("|");
      if (ix * iy > 0.12 * small && iy > 0.38 * Math.min(a.h, b.h) && !reported.has(key)) { reported.add(key); W(`t=${t.toFixed(1)}s overlapping text: "${a.text}" / "${b.text}"`); }
    }
  }
  for (const id in onTime) {
    const o = onTime[id];
    const longest = Math.max(0, ...o.runs.map((r) => r.end - r.start + step));
    const need = Math.min(2.5, 0.6 + o.words * 0.22);
    if (longest + step * 0.5 < need) W(`"${o.text}" is fully readable for only ${longest.toFixed(1)}s (needs ~${need.toFixed(1)}s for ${o.words} words)`);
  }
  if (!args.fast) {
    // ---------- pixel checks: contrast / busy background per text, empty frames, flashes ----------
    const stats = await browser.newPage();
    await stats.setContent("<canvas id=c></canvas>");
    const measure = (buf, rect) => stats.evaluate(async ({ b64, rect }) => {
      const img = new Image(); img.src = "data:image/jpeg;base64," + b64; await img.decode();
      const c = document.getElementById("c"); c.width = img.width; c.height = img.height;
      const g = c.getContext("2d"); g.drawImage(img, 0, 0);
      const r = rect || { x: 0, y: 0, w: img.width, h: img.height };
      const d = g.getImageData(Math.max(0, r.x), Math.max(0, r.y), Math.max(1, Math.min(img.width - r.x, r.w)), Math.max(1, Math.min(img.height - r.y, r.h))).data;
      const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      let sum = 0, sq = 0, n = 0;
      for (let i = 0; i < d.length; i += 16) { const L = 0.2126 * lin(d[i]) + 0.7152 * lin(d[i + 1]) + 0.0722 * lin(d[i + 2]); sum += L; sq += L * L; n++; }
      const mean = sum / n;
      // 4x4 grid of cell means (to tell a uniform flash from a travelling wipe)
      const cells = [];
      if (!rect) {
        const cw = Math.floor(img.width / 4), ch = Math.floor(img.height / 4);
        for (let gy = 0; gy < 4; gy++) for (let gx = 0; gx < 4; gx++) {
          const dd = g.getImageData(gx * cw, gy * ch, cw, ch).data; let cs = 0, cn = 0;
          for (let i = 0; i < dd.length; i += 32) { cs += 0.2126 * lin(dd[i]) + 0.7152 * lin(dd[i + 1]) + 0.0722 * lin(dd[i + 2]); cn++; }
          cells.push(cs / cn);
        }
      }
      return { mean, std: Math.sqrt(Math.max(0, sq / n - mean * mean)), cells };
    }, { b64: buf.toString("base64"), rect });
    const K = 0.5; // film page renders at deviceScaleFactor 0.5
    for (const id in onTime) {
      const o = onTime[id];
      const run = o.runs.sort((a, b) => (b.end - b.start) - (a.end - a.start))[0];
      if (!run) continue;
      const t = (run.start + run.end) / 2;
      await page.evaluate((x) => window.__film.seek(x), t);
      const info = await page.evaluate((id) => {
        const el = document.getElementById(id); if (!el) return null;
        const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, { acceptNode: (nd) => nd.parentElement.closest(".mk-sweep,.mk-glitch,.sw,[aria-hidden=true]") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
        let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9, color = null, size = 0, weight = 400;
        while (tw.nextNode()) { const nd = tw.currentNode; if (!nd.textContent.trim()) continue;
          const cs = getComputedStyle(nd.parentElement); if (!color) { color = cs.color; size = parseFloat(cs.fontSize); weight = parseInt(cs.fontWeight, 10); if (cs.webkitTextFillColor && cs.webkitTextFillColor !== cs.color && /rgba\(.*,\s*0\)/.test(cs.webkitTextFillColor)) color = null; }
          const rg = document.createRange(); rg.selectNodeContents(nd);
          for (const r of rg.getClientRects()) { if (r.width < 1) continue; x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom); } }
        el.dataset.qaVis = el.style.visibility; el.style.visibility = "hidden";
        return { color, size, weight, x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
      }, id);
      if (!info || !info.color) continue;
      await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
      const shot = await page.screenshot({ type: "jpeg", quality: 80 });
      await page.evaluate((id) => { const el = document.getElementById(id); el.style.visibility = el.dataset.qaVis || ""; }, id);
      const m = /rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?/.exec(info.color);
      if (!m || (m[4] !== undefined && parseFloat(m[4]) < 0.5)) continue;
      const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      const Lt = 0.2126 * lin(+m[1]) + 0.7152 * lin(+m[2]) + 0.0722 * lin(+m[3]);
      const bg = await measure(shot, { x: Math.round(info.x * K), y: Math.round(info.y * K), w: Math.round(info.w * K), h: Math.round(info.h * K) });
      const ratio = (Math.max(Lt, bg.mean) + 0.05) / (Math.min(Lt, bg.mean) + 0.05);
      const large = info.size >= 36 || (info.size >= 28 && info.weight >= 700);
      const need = large ? 3 : 4.5;
      if (ratio < need) W(`t=${t.toFixed(1)}s "${o.text}" low contrast ${ratio.toFixed(1)}:1 against its background (needs ${need}:1)`);
      else if (bg.std > 0.14 && ratio < 7) W(`t=${t.toFixed(1)}s "${o.text}" sits on a busy background (texture ${bg.std.toFixed(2)}) — add a scrim/blur or move it`);
    }
    const fstep = parseFloat(args["frame-step"] || 0.5);
    const frames = [];
    for (let t = 0; t <= cfg.duration + 1e-6; t += fstep) {
      await page.evaluate((x) => window.__film.seek(x), t);
      frames.push({ t, ...(await measure(await page.screenshot({ type: "jpeg", quality: 40 }))) });
    }
    let emptyRun = 0;
    for (const f of frames) {
      const inner = f.t > 0.6 && f.t < cfg.duration - 0.6;
      emptyRun = inner && f.std < 0.012 ? emptyRun + 1 : 0;
      if (emptyRun === 2) W(`t≈${(f.t - fstep).toFixed(1)}s near-empty frame for ≥${(fstep * 2).toFixed(1)}s (flat colour, nothing on screen)`);
    }
    for (let i = 1; i < frames.length; i++) {
      if (frames[i].mean - frames[i - 1].mean < 0.3) continue;
      let worst = 0;
      for (let t = frames[i - 1].t; t < frames[i].t - 1e-6; t += 0.1) {
        await page.evaluate((x) => window.__film.seek(x), t);
        const a = await measure(await page.screenshot({ type: "jpeg", quality: 40 }));
        await page.evaluate((x) => window.__film.seek(x), t + 0.1);
        const b = await measure(await page.screenshot({ type: "jpeg", quality: 40 }));
        const up = b.cells.filter((v, k) => v - a.cells[k] > 0.2).length;   // cells that brightened a lot
        if (up >= 12) worst = Math.max(worst, b.mean - a.mean);            // ≥75% of the frame at once = flash
      }
      if (worst > 0.25) W(`t≈${frames[i].t.toFixed(1)}s harsh brightness jump (+${(worst * 100).toFixed(0)}% in 0.1s) — reads as a flash; ease it over ≥0.4s`);
    }
  }
} catch (e) {
  E("runtime: " + (e.message || e));
} finally {
  await browser.close();
  server.close();
}

console.log(`\nchitram check — ${entry}${cfg ? ` (${cfg.width}x${cfg.height}, ${cfg.duration}s @ ${cfg.fps}fps)` : ""}`);
errors.forEach((m) => console.log("  ERROR  " + m));
warns.forEach((m) => console.log("  warn   " + m));
console.log(`\n${errors.length} error(s), ${warns.length} warning(s)`);
process.exit(errors.length || (args.strict && warns.length) ? 1 : 0);
