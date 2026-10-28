// Shared helpers: static server (with Range support for video), browser launch, film loading.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const SKILL_ENGINE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "engine");

const MIME = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".webp": "image/webp", ".gif": "image/gif", ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".otf": "font/otf",
  ".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".ogg": "audio/ogg", ".webm": "video/webm", ".mp4": "video/mp4",
};

export function serve(rootDir, listenPort = 0) {
  const root = path.resolve(rootDir);
  const server = http.createServer((req, res) => {
    const url = decodeURIComponent(req.url.split("?")[0]);
    let file = path.join(root, url);
    if (!file.startsWith(root)) { res.writeHead(403); return res.end(); }
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
    // projects may omit their own engine/ copy: fall back to the skill's shared engine folder
    if (!fs.existsSync(file) && url.startsWith("/engine/")) {
      const shared = path.join(SKILL_ENGINE, url.slice("/engine/".length));
      if (shared.startsWith(SKILL_ENGINE) && fs.existsSync(shared)) file = shared;
    }
    if (!fs.existsSync(file)) { res.writeHead(404); return res.end("not found: " + url); }
    const stat = fs.statSync(file);
    const type = MIME[path.extname(file).toLowerCase()] || "application/octet-stream";
    const range = req.headers.range;
    if (range) {
      const m = /bytes=(\d*)-(\d*)/.exec(range);
      const start = m[1] ? parseInt(m[1], 10) : 0;
      const end = m[2] ? parseInt(m[2], 10) : stat.size - 1;
      res.writeHead(206, { "Content-Type": type, "Content-Range": `bytes ${start}-${end}/${stat.size}`, "Accept-Ranges": "bytes", "Content-Length": end - start + 1 });
      return fs.createReadStream(file, { start, end }).pipe(res);
    }
    res.writeHead(200, { "Content-Type": type, "Content-Length": stat.size, "Accept-Ranges": "bytes", "Cache-Control": "no-cache" });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((resolve) => server.listen(listenPort, "127.0.0.1", () => resolve({ server, port: server.address().port })));
}

export function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const tries = ["playwright", "playwright-core"];
  for (const t of tries) { try { return require(t); } catch {} }
  try {
    const g = execSync("npm root -g").toString().trim();
    for (const t of tries) { try { return require(path.join(g, t)); } catch {} }
  } catch {}
  throw new Error("Playwright not found. Run `npm install` inside the skill folder, then `npx playwright-core install chromium`.");
}

export async function launch() {
  const { chromium } = loadPlaywright();
  const args = ["--disable-web-security", "--autoplay-policy=no-user-gesture-required", "--force-color-profile=srgb",
    "--disable-lcd-text", "--font-render-hinting=none", "--hide-scrollbars", "--mute-audio"];
  const opts = { args, headless: true };
  if (process.env.CHROME_PATH) opts.executablePath = process.env.CHROME_PATH;
  return chromium.launch(opts);
}

/** Open the film page, wait for Film.build to finish. Returns {page, cfg}. */
export async function openFilm(browser, port, entry, scale = 1) {
  const probe = await browser.newPage();
  { const lg = [path.join(process.env.FILM_DIR || "", "gsap.min.js"), process.env.GSAP_PATH || ""].find((f) => f && fs.existsSync(f));
    if (lg) await probe.route(/gsap(\.min)?\.js(\?.*)?$/, (r) => r.fulfill({ path: lg, contentType: "text/javascript" })); }
  await probe.goto(`http://127.0.0.1:${port}/${entry}`, { waitUntil: "load" });
  await probe.waitForFunction(() => window.__film && window.__film.cfg, null, { timeout: 30000 });
  const cfg = await probe.evaluate(() => window.__film.cfg);
  await probe.close();
  const page = await browser.newPage({ viewport: { width: cfg.width, height: cfg.height }, deviceScaleFactor: scale });
  const logs = [];
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") logs.push(`[${m.type()}] ${m.text()}`); });
  page.on("pageerror", (e) => logs.push(`[pageerror] ${e.message}`));
  page.on("requestfailed", (r) => logs.push(`[requestfailed] ${r.url()}`));
  page.on("response", (r) => { if (r.status() >= 400) logs.push(`[http ${r.status()}] ${r.url()}`); });
  const localGsap = [path.join(process.env.FILM_DIR || "", "gsap.min.js"), process.env.GSAP_PATH || ""].find((f) => f && fs.existsSync(f));
  if (localGsap) await page.route(/gsap(\.min)?\.js(\?.*)?$/, (r) => r.fulfill({ path: localGsap, contentType: "text/javascript" }));
  await page.goto(`http://127.0.0.1:${port}/${entry}`, { waitUntil: "load" });
  await page.waitForFunction(() => window.__film, null, { timeout: 30000 });
  await page.evaluate(() => Promise.race([window.__film.ready, new Promise((_, rej) => setTimeout(() => rej(new Error("Film.build() never finished (script error?)")), 60000))]));
  return { page, cfg, logs };
}

export function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const [k, v] = a.slice(2).split("=");
      if (v !== undefined) out[k] = v;
      else if (i + 1 < argv.length && !argv[i + 1].startsWith("--")) out[k] = argv[++i];
      else out[k] = true;
    } else out._.push(a);
  }
  return out;
}

export function resolveProject(p) {
  const abs = path.resolve(p || ".");
  const r = fs.existsSync(abs) && fs.statSync(abs).isFile() ? { dir: path.dirname(abs), entry: path.basename(abs) } : { dir: abs, entry: "index.html" };
  process.env.FILM_DIR = r.dir;
  return r;
}
