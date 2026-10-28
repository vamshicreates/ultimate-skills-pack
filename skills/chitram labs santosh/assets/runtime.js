/*
 * Chitram Film runtime — the seekable-page contract.
 *
 * A film is one HTML page. Its root element carries:
 *   <div id="film" data-film data-duration="30" data-fps="30"
 *        data-width="1920" data-height="1080" data-audio="assets/score.wav">
 *
 * The page builds ONE paused GSAP timeline inside Film.build(fn). The renderer
 * (bin/render.mjs) then calls window.__film.seek(t) for every frame and
 * screenshots the viewport. Anything visible must be a pure function of t.
 *
 * Extras handled here so authors don't have to:
 *   [data-in] / [data-out]          -> element is visibility:hidden outside [in, out)
 *   <video data-at="12" data-offset="0.5">   -> seeked to (t - at + offset), awaited
 *   <img data-seq="assets/clip/%05d.jpg" data-at="12" data-seq-fps="30" data-count="90">
 *                                   -> image-sequence footage (most robust footage path)
 *   ?preview in the URL, or a data-preview attribute on the root -> interactive player with scrubber + audio
 *   (never leave data-preview on for rendering; the renderer ignores the player but it adds a bar)
 */
(function () {
  "use strict";
  const root = document.querySelector("[data-film]");
  if (!root) throw new Error("Film: no [data-film] root element");
  const cfg = {
    duration: parseFloat(root.dataset.duration),
    fps: parseFloat(root.dataset.fps || "30"),
    width: parseInt(root.dataset.width || "1920", 10),
    height: parseInt(root.dataset.height || "1080", 10),
    audio: root.dataset.audio || null,
  };
  if (!(cfg.duration > 0)) throw new Error("Film: data-duration is required");
  root.style.width = cfg.width + "px";
  root.style.height = cfg.height + "px";

  let tl = null;
  let resolveReady;
  const ready = new Promise((r) => (resolveReady = r));
  const errors = [];
  window.addEventListener("error", (e) => errors.push(String(e.message || e)));

  function pad(n, w) { n = String(n); while (n.length < w) n = "0" + n; return n; }
  function seqSrc(pattern, i) {
    return pattern.replace(/%0(\d)d/, (_, w) => pad(i, +w)).replace("%d", String(i));
  }

  function applyTimed(t) {
    const els = document.querySelectorAll("[data-in],[data-out]");
    for (const el of els) {
      const a = el.dataset.in != null ? parseFloat(el.dataset.in) : -1e9;
      const b = el.dataset.out != null ? parseFloat(el.dataset.out) : 1e9;
      const on = t >= a && t < b;
      el.style.visibility = on ? "" : "hidden";
    }
  }

  async function syncVideos(t) {
    const vids = document.querySelectorAll("video[data-at]");
    const jobs = [];
    for (const v of vids) {
      const at = parseFloat(v.dataset.at);
      const off = parseFloat(v.dataset.offset || "0");
      const rate = parseFloat(v.dataset.rate || "1");
      let local = (t - at) * rate + off;
      const dur = isFinite(v.duration) ? v.duration : 0;
      local = Math.max(0, Math.min(Math.max(0, dur - 0.001), local));
      if (Math.abs(v.currentTime - local) < 0.0005 && v.readyState >= 2) continue;
      jobs.push(new Promise((res) => {
        const done = () => { v.removeEventListener("seeked", done); res(); };
        v.addEventListener("seeked", done);
        v.currentTime = local;
        setTimeout(done, 3000);
      }));
    }
    await Promise.all(jobs);
  }

  async function syncSequences(t) {
    const imgs = document.querySelectorAll("img[data-seq]");
    const jobs = [];
    for (const img of imgs) {
      const at = parseFloat(img.dataset.at || "0");
      const fps = parseFloat(img.dataset.seqFps || cfg.fps);
      const count = parseInt(img.dataset.count, 10);
      const start = parseInt(img.dataset.first || "1", 10);
      let i = Math.floor((t - at) * fps + 1e-6);
      i = Math.max(0, Math.min(count - 1, i));
      const src = seqSrc(img.dataset.seq, start + i);
      if (img.getAttribute("src") === src) continue;
      img.setAttribute("src", src);
      jobs.push(img.decode().catch(() => {}));
    }
    await Promise.all(jobs);
  }

  async function seek(t) {
    await ready;
    t = Math.max(0, Math.min(cfg.duration, t));
    tl.seek(t, false);
    applyTimed(t);
    await Promise.all([syncVideos(t), syncSequences(t)]);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    return t;
  }

  async function preload() {
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    const imgs = [...document.images].filter((i) => !i.dataset.seq);
    await Promise.all(imgs.map((i) => (i.complete ? i.decode() : new Promise((r) => { i.onload = r; i.onerror = r; }).then(() => i.decode())).catch(() => {})));
    const vids = [...document.querySelectorAll("video")];
    await Promise.all(vids.map((v) => (v.readyState >= 2 ? null : new Promise((r) => {
      v.muted = true; v.preload = "auto";
      v.addEventListener("loadeddata", r, { once: true }); v.addEventListener("error", r, { once: true });
      setTimeout(r, 8000); v.load();
    }))));
  }

  const Film = {
    cfg,
    root,
    /** Build the film. fn(tl) receives a fresh paused timeline. Runs after fonts/images load. */
    build(fn) {
      preload().then(() => {
        tl = gsap.timeline({ paused: true });
        fn(tl);
        tl.seek(0, false);
        applyTimed(0);
        resolveReady();
        if (/[?&]preview/.test(location.search) || root.hasAttribute("data-preview")) startPreview();
      }).catch((e) => { errors.push(String(e && e.stack || e)); console.error(e); });
    },
    get timeline() { return tl; },
  };
  window.Film = Film;
  window.__film = {
    cfg, seek, ready, errors,
    timelineDuration: () => (tl ? tl.duration() : 0),
  };

  /* ---------------- preview player (browser only, never used by the renderer) --------------- */
  function startPreview() {
    const s = document.createElement("style");
    s.textContent = `html,body{overflow:hidden;background:#111}
      #__pv{position:fixed;left:0;right:0;bottom:0;height:44px;background:rgba(0,0,0,.85);display:flex;gap:10px;align-items:center;padding:0 12px;font:12px/1 monospace;color:#ddd;z-index:99999}
      #__pv input{flex:1} #__pv button{background:#333;color:#fff;border:0;padding:6px 10px;border-radius:4px}`;
    document.head.appendChild(s);
    const bar = document.createElement("div");
    bar.id = "__pv";
    bar.innerHTML = `<button id="__pp">play</button><input id="__sc" type="range" min="0" max="${cfg.duration}" step="0.001" value="0"><span id="__tm">0.00</span>`;
    document.body.appendChild(bar);
    const fit = () => {
      const k = Math.min(innerWidth / cfg.width, (innerHeight - 44) / cfg.height);
      root.style.transformOrigin = "0 0";
      root.style.transform = `scale(${k})`;
    };
    fit(); addEventListener("resize", fit);
    const audio = cfg.audio ? new Audio(cfg.audio) : null;
    let playing = false, t0 = 0, p0 = 0;
    const sc = bar.querySelector("#__sc"), tm = bar.querySelector("#__tm"), pp = bar.querySelector("#__pp");
    const show = (t) => { tl.seek(t, false); applyTimed(t); syncVideos(t); syncSequences(t); sc.value = t; tm.textContent = t.toFixed(2); };
    const loop = (now) => {
      if (!playing) return;
      const t = p0 + (now - t0) / 1000;
      if (t >= cfg.duration) { playing = false; pp.textContent = "play"; if (audio) audio.pause(); show(cfg.duration); return; }
      show(t); requestAnimationFrame(loop);
    };
    pp.onclick = () => {
      playing = !playing; pp.textContent = playing ? "pause" : "play";
      if (playing) { p0 = +sc.value; t0 = performance.now(); if (audio) { audio.currentTime = p0; audio.play(); } requestAnimationFrame(loop); }
      else if (audio) audio.pause();
    };
    sc.oninput = () => { playing = false; pp.textContent = "play"; if (audio) audio.pause(); show(+sc.value); };
    addEventListener("keydown", (e) => {
      if (e.code === "Space") { e.preventDefault(); pp.onclick(); }
      if (e.code === "ArrowRight") show(Math.min(cfg.duration, +sc.value + 1 / cfg.fps));
      if (e.code === "ArrowLeft") show(Math.max(0, +sc.value - 1 / cfg.fps));
    });
  }
})();
