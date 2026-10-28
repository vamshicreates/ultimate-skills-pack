/*
 * Chitram Film motion kit (window.MK).
 *
 * Every effect is a function (tl, target, t, options) that ADDS tweens to the film's
 * single paused timeline at absolute time t. All effects are deterministic and seek-safe.
 * Build-time helpers (MK.laptop, MK.bokeh, ...) create DOM and return element refs.
 *
 * Rules the kit relies on:
 *  - Call kit functions only inside Film.build(tl => { ... }) (fonts are loaded there,
 *    so measuring text works).
 *  - Never put a CSS `transform` on an element you animate with x/y/scale/rotation;
 *    set starting transforms with tl.set(el, {...}, 0) instead.
 *  - Reveal an element once. To hide it later use MK.blurOut / MK.fadeOut / MK.dim.
 */
(function () {
  "use strict";
  const MK = {};
  const q = (x) => (typeof x === "string" ? document.querySelector(x) : x && x.jquery ? x[0] : x);
  const qa = (x) => (typeof x === "string" ? [...document.querySelectorAll(x)] : Array.isArray(x) ? x.map(q) : x instanceof NodeList ? [...x] : [q(x)]);
  const need = (el, name) => { if (!el) throw new Error("MK." + name + ": target not found"); return el; };
  MK.q = q; MK.qa = qa;

  /** Seeded PRNG (mulberry32). Use instead of Math.random. */
  MK.rng = function (seed) {
    let a = (seed >>> 0) || 1;
    return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  };
  /**
   * Custom cubic-bezier ease — the After Effects graph editor / CSS cubic-bezier() in code.
   *   ease: MK.bezier(0.16, 1, 0.3, 1)            // "luxury glide"
   * Named curves: MK.curves.glide, .snap, .settle, .anticipate, .easyEase, .whip
   */
  MK.bezier = function (x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = (t) => ((ax * t + bx) * t + cx) * t, sy = (t) => ((ay * t + by) * t + cy) * t;
    const dx = (t) => (3 * ax * t + 2 * bx) * t + cx;
    return function (x) {
      if (x <= 0) return 0; if (x >= 1) return 1;
      let t = x;
      for (let i = 0; i < 8; i++) { const e = sx(t) - x, d = dx(t); if (Math.abs(e) < 1e-6) break; if (Math.abs(d) < 1e-6) break; t -= e / d; }
      if (t < 0 || t > 1 || Math.abs(sx(t) - x) > 1e-4) { let lo = 0, hi = 1; t = x; for (let i = 0; i < 30; i++) { if (sx(t) < x) lo = t; else hi = t; t = (lo + hi) / 2; } }
      return sy(t);
    };
  };
  MK.curves = {
    easyEase: MK.bezier(0.33, 0, 0.67, 1),     // AE Easy Ease (33 % influence both sides)
    glide: MK.bezier(0.16, 1, 0.3, 1),         // luxury arrival, long soft tail
    snap: MK.bezier(0.2, 0.8, 0.2, 1),         // snappy UI arrival
    settle: MK.bezier(0.34, 1.36, 0.64, 1),    // small overshoot then settle
    anticipate: MK.bezier(0.68, -0.4, 0.32, 1.4), // dip back, overshoot forward
    whip: MK.bezier(0.7, 0, 0.3, 1),           // slow-fast-slow camera whip
    exit: MK.bezier(0.55, 0, 1, 0.45),         // accelerate away
  };

  /** Finite repeat count for yoyo loops that must end before `span` seconds. */
  MK.repeats = (span, period) => Math.max(0, Math.floor(span / period) - 1);

  function ensurePositioned(el) {
    const cs = getComputedStyle(el);
    if (cs.position === "static") el.style.position = "relative";
  }

  /* ============================== TEXT REVEALS ============================== */

  /** Light sweep across text (gradient clipped to glyphs). opts.color sets highlight. */
  MK.sweep = function (tl, target, t, o = {}) {
    const el = need(q(target), "sweep");
    ensurePositioned(el);
    let sw = el.querySelector(":scope > .mk-sweep");
    if (!sw) {
      sw = document.createElement("span");
      sw.className = "mk-sweep";
      sw.setAttribute("aria-hidden", "true");
      sw.innerHTML = el.innerHTML;
      el.appendChild(sw);
    }
    if (o.color) sw.style.setProperty("--mk-sweep", o.color);
    tl.fromTo(sw, { backgroundPosition: "140% 0" }, { backgroundPosition: "-40% 0", duration: o.dur || 1.3, ease: "power2.inOut" }, t);
    return tl;
  };

  /** Signature premium reveal: blur -> sharp, slight rise, optional light sweep. */
  MK.blurIn = function (tl, target, t, o = {}) {
    const el = need(q(target), "blurIn");
    const d = o.dur ?? 1.0;
    if (o.sweep !== false) MK.sweep(tl, el, t + d * 0.35, { color: o.sweepColor, dur: 1.3 });
    tl.fromTo(el, { opacity: 0, filter: `blur(${o.blur ?? 18}px)`, y: o.y ?? 16 },
      { opacity: 1, filter: "blur(0px)", y: 0, duration: d, ease: o.ease || "power2.out" }, t);
    return tl;
  };
  MK.blurOut = function (tl, target, t, o = {}) {
    tl.to(qa(target), { opacity: 0, filter: `blur(${o.blur ?? 12}px)`, y: o.y ?? -10, duration: o.dur ?? 0.5, ease: "power2.in" }, t);
    return tl;
  };
  MK.fadeIn = function (tl, target, t, o = {}) {
    tl.fromTo(qa(target), { opacity: 0, y: o.y ?? 10 }, { opacity: 1, y: 0, duration: o.dur ?? 0.7, ease: o.ease || "power2.out", stagger: o.stagger || 0 }, t);
    return tl;
  };
  MK.fadeOut = function (tl, target, t, o = {}) {
    tl.to(qa(target), { opacity: 0, duration: o.dur ?? 0.5, ease: "power1.in" }, t);
    return tl;
  };
  /** Dim a previous caption when the next one arrives (list/stack captions). */
  MK.dim = function (tl, target, t, o = {}) {
    tl.to(qa(target), { opacity: o.to ?? 0.28, duration: o.dur ?? 0.6, ease: "sine.inOut" }, t);
    return tl;
  };
  /** Pop in with overshoot (last line of a stack, badges, stickers). */
  MK.popIn = function (tl, target, t, o = {}) {
    tl.fromTo(qa(target), { opacity: 0, scale: o.from ?? 0.6, y: o.y ?? 0 },
      { opacity: 1, scale: 1, y: 0, duration: o.dur ?? 0.55, ease: o.ease || "back.out(2.2)", stagger: o.stagger || 0 }, t);
    return tl;
  };

  /**
   * Block wipe: a solid block grows over the text, the text appears under it, the block
   * leaves from the other side. Target must be shrink-to-fit (absolute, inline-block,
   * or a flex item with align-self:flex-start).
   */
  MK.blockWipe = function (tl, target, t, o = {}) {
    const el = need(q(target), "blockWipe");
    ensurePositioned(el);
    const d = o.dur ?? 0.7;
    let inner = el.querySelector(":scope > .mk-bwin");
    if (!inner) {
      inner = document.createElement("span");
      inner.className = "mk-bwin";
      inner.style.display = "inline-block";
      while (el.firstChild) inner.appendChild(el.firstChild);
      el.appendChild(inner);
    }
    const cover = document.createElement("span");
    cover.className = "mk-cover";
    cover.style.background = o.color || "currentColor";
    if (o.radius) cover.style.borderRadius = o.radius;
    el.appendChild(cover);
    const fromRight = o.dir === "right";
    tl.set(el, { opacity: 1 }, t);
    tl.fromTo(inner, { opacity: 0 }, { opacity: 1, duration: 0.01 }, t + d * 0.5);
    tl.fromTo(cover, { scaleX: 0, transformOrigin: fromRight ? "100% 50%" : "0% 50%" },
      { scaleX: 1, duration: d * 0.5, ease: "power3.in" }, t);
    tl.set(cover, { transformOrigin: fromRight ? "0% 50%" : "100% 50%" }, t + d * 0.5);
    tl.to(cover, { scaleX: 0, duration: d * 0.5, ease: "power3.out" }, t + d * 0.5);
    tl.set(el, { opacity: 0 }, 0); // hidden before its moment
    return tl;
  };

  /** Mask rise: the line slides up from behind an invisible edge. */
  MK.maskRise = function (tl, target, t, o = {}) {
    const el = need(q(target), "maskRise");
    let inner = el.querySelector(":scope > .mk-in");
    if (!inner) {
      el.classList.add("mk-mask");
      inner = document.createElement("span");
      inner.className = "mk-in";
      while (el.firstChild) inner.appendChild(el.firstChild);
      el.appendChild(inner);
    }
    tl.set(el, { opacity: 1 }, t);
    tl.fromTo(inner, { yPercent: 115 }, { yPercent: 0, duration: o.dur ?? 0.8, ease: o.ease || "power4.out" }, t);
    tl.set(el, { opacity: 0 }, 0);
    return tl;
  };

  /** Split into word spans once. Returns the spans. */
  MK.words = function (target) {
    const el = need(q(target), "words");
    if (el._mkWords) return el._mkWords;
    const text = el.textContent;
    el.textContent = "";
    const spans = [];
    text.split(/(\s+)/).forEach((tok) => {
      if (!tok) return;
      if (/^\s+$/.test(tok)) { el.appendChild(document.createTextNode(" ")); return; }
      const s = document.createElement("span");
      s.className = "mk-word";
      s.textContent = tok;
      el.appendChild(s);
      spans.push(s);
    });
    el._mkWords = spans;
    return spans;
  };

  /** Words rise one by one from masks. */
  MK.wordsRise = function (tl, target, t, o = {}) {
    const el = need(q(target), "wordsRise");
    const ws = MK.words(el);
    ws.forEach((w) => {
      if (w.parentNode.classList.contains("mk-wordmask")) return;
      const m = document.createElement("span");
      m.className = "mk-wordmask";
      w.parentNode.insertBefore(m, w); m.appendChild(w);
    });
    tl.set(el, { opacity: 1 }, t);
    tl.fromTo(ws, { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: o.dur ?? 0.6, ease: "power3.out", stagger: o.stagger ?? 0.08 }, t);
    tl.set(el, { opacity: 0 }, 0);
    return tl;
  };

  /** Typewriter with caret. cps = characters per second. Returns end time. */
  MK.typewriter = function (tl, target, t, o = {}) {
    const el = need(q(target), "typewriter");
    const cps = o.cps ?? 16;
    // wrap every character in place (keeps child spans such as highlight targets intact)
    const chars = [];
    const walk = (node) => {
      [...node.childNodes].forEach((ch) => {
        if (ch.nodeType === 3) {
          const frag = document.createDocumentFragment();
          [...ch.textContent].forEach((c) => { const s = document.createElement("span"); s.className = "mk-char"; s.textContent = c; frag.appendChild(s); chars.push(s); });
          node.replaceChild(frag, ch);
        } else if (ch.nodeType === 1 && !ch.classList.contains("mk-sweep")) walk(ch);
      });
    };
    walk(el);
    let caret = null;
    if (o.caret !== false) { caret = document.createElement("span"); caret.className = "mk-caret"; el.appendChild(caret); }
    tl.set(el, { opacity: 1 }, t);
    chars.forEach((c, i) => tl.set(c, { display: "inline" }, t + i / cps));
    const end = t + chars.length / cps;
    if (caret) {
      tl.fromTo(caret, { opacity: 1 }, { opacity: 0, duration: 0.01 }, t - 0.001);
      tl.set(caret, { opacity: 1 }, t);
      const blinkEnd = o.caretOff ?? end + 1.2;
      const n = Math.max(1, Math.floor((blinkEnd - end) / 0.5));
      for (let i = 0; i < n; i++) tl.set(caret, { opacity: i % 2 ? 1 : 0 }, end + 0.25 + i * 0.5);
      tl.set(caret, { opacity: 0 }, blinkEnd);
    }
    tl.set(el, { opacity: 0 }, 0);
    return end;
  };

  /**
   * Karaoke highlight: a pill moves word to word, each active word changes colour.
   * o.times: array of absolute start times per word (e.g. from a voiceover) or o.step.
   * Returns the array of word times (use them for click SFX).
   */
  MK.karaoke = function (tl, target, t, o = {}) {
    const el = need(q(target), "karaoke");
    el.classList.add("mk-karaoke");
    ensurePositioned(el);
    const ws = MK.words(el);
    const times = o.times || ws.map((_, i) => t + i * (o.step ?? 0.32));
    const pill = document.createElement("span");
    pill.className = "mk-kpill";
    pill.style.background = o.pill || "#C7F36B";
    el.appendChild(pill);
    const padX = o.padX ?? 0.18, padY = o.padY ?? 0.06;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    const box = (w) => ({ x: w.offsetLeft - padX * fs, y: w.offsetTop - padY * fs, width: w.offsetWidth + 2 * padX * fs, height: w.offsetHeight + 2 * padY * fs });
    const b0 = box(ws[0]);
    tl.set(pill, { x: b0.x, y: b0.y, width: b0.width, height: b0.height, opacity: 0 }, 0);
    tl.set(pill, { opacity: 1 }, times[0]);
    const base = o.color || getComputedStyle(el).color;
    ws.forEach((w, i) => {
      const b = box(w);
      if (i > 0) tl.to(pill, { x: b.x, y: b.y, width: b.width, height: b.height, duration: o.move ?? 0.14, ease: "power2.out" }, times[i]);
      tl.set(w, { color: o.active || "#0B1F1C" }, times[i]);
      if (i > 0) tl.set(ws[i - 1], { color: o.done || base }, times[i]);
    });
    if (o.end) { tl.to(pill, { opacity: 0, duration: 0.2 }, o.end); tl.set(ws[ws.length - 1], { color: o.done || base }, o.end); }
    return times;
  };

  /** Glitch-block reveal: RGB-split slices snap into the clean text. Returns tick times. */
  MK.glitchIn = function (tl, target, t, o = {}) {
    const el = need(q(target), "glitchIn");
    ensurePositioned(el);
    const rnd = MK.rng(o.seed ?? 11);
    const cols = o.colors || ["#C7F36B", "#2EE6C9"];
    const layers = cols.map((c) => {
      const g = document.createElement("span");
      g.className = "mk-glitch";
      g.setAttribute("aria-hidden", "true");
      g.innerHTML = el.innerHTML;
      g.style.color = c;
      el.appendChild(g);
      return g;
    });
    const steps = o.steps ?? 6, d = o.dur ?? 0.42, ticks = [];
    tl.set(el, { opacity: 1 }, t);
    for (let i = 0; i < steps; i++) {
      const at = t + (i / steps) * d;
      ticks.push(at);
      const y0 = Math.floor(rnd() * 70), y1 = Math.min(100, y0 + 12 + Math.floor(rnd() * 30));
      layers.forEach((g, k) => tl.set(g, { opacity: 0.9, x: (rnd() - 0.5) * 28 * (k ? -1 : 1), clipPath: `inset(${y0}% 0 ${100 - y1}% 0)` }, at));
      tl.set(el, { x: (rnd() - 0.5) * 10, clipPath: i < steps - 2 ? `inset(${Math.floor(rnd() * 40)}% 0 ${Math.floor(rnd() * 40)}% 0)` : "inset(0% 0 0% 0)" }, at);
    }
    tl.set(layers, { opacity: 0, x: 0 }, t + d);
    tl.set(el, { x: 0, clipPath: "inset(0% 0 0% 0)" }, t + d);
    tl.set(el, { opacity: 0 }, 0);
    return ticks;
  };

  /** Gradient highlight block that wipes across a word/phrase (behind the text). */
  MK.highlight = function (tl, target, t, o = {}) {
    const el = need(q(target), "highlight");
    el.classList.add("mk-hlwrap");
    const hl = document.createElement("span");
    hl.className = "mk-hl";
    hl.style.background = o.bg || "linear-gradient(90deg,#C7F36B,#10B981)";
    el.insertBefore(hl, el.firstChild);
    tl.fromTo(hl, { scaleX: 0 }, { scaleX: 1, duration: o.dur ?? 0.55, ease: "power3.inOut" }, t);
    if (o.textColor) tl.to(el, { color: o.textColor, duration: 0.2 }, t + (o.dur ?? 0.55) * 0.6);
    return tl;
  };

  /** Draw SVG strokes on (paths/lines/circles). */
  MK.lineDraw = function (tl, targets, t, o = {}) {
    const els = qa(targets);
    els.forEach((p, i) => {
      const len = p.getTotalLength ? p.getTotalLength() : 1000;
      tl.fromTo(p, { strokeDasharray: len, strokeDashoffset: o.reverse ? -len : len },
        { strokeDashoffset: 0, duration: o.dur ?? 1.2, ease: o.ease || "power2.inOut" }, t + i * (o.stagger ?? 0.12));
    });
    return tl;
  };
  /** Un-draw strokes (they retract toward their end). */
  MK.lineErase = function (tl, targets, t, o = {}) {
    qa(targets).forEach((p, i) => {
      const len = p.getTotalLength ? p.getTotalLength() : 1000;
      tl.to(p, { strokeDashoffset: -len, duration: o.dur ?? 0.8, ease: "power2.in" }, t + i * (o.stagger ?? 0.05));
    });
    return tl;
  };

  /* ============================== TRANSITIONS ============================== */

  /**
   * Light-streak whip. Streaks sweep across `layer`; if `stage` is given it is pushed
   * out with motion blur and pulled back in. Swap scene content at the returned time.
   */
  MK.whip = function (tl, t, o = {}) {
    const layer = need(q(o.layer), "whip(layer)");
    const W = Film.cfg.width, H = Film.cfg.height;
    const rnd = MK.rng(o.seed ?? 5);
    const cols = o.colors || ["#E3B34A", "#8F7CF8", "#fff3d6", "#7B6CF6"];
    const n = o.count ?? 9, dir = o.dir === "left" ? -1 : 1, d = o.dur ?? 0.8;
    for (let i = 0; i < n; i++) {
      const s = document.createElement("div");
      s.className = "mk-streak";
      const h = [3, 10, 2, 18, 6, 3, 26, 8, 2, 12][i % 10];
      s.style.top = H * 0.15 + i * (H * 0.7 / n) + rnd() * 40 + "px";
      s.style.height = h + "px";
      s.style.width = W * (0.7 + rnd() * 0.5) + "px";
      s.style.background = `linear-gradient(${dir > 0 ? 90 : 270}deg,rgba(0,0,0,0),${cols[i % cols.length]} 55%,rgba(255,255,255,.9) 80%,rgba(0,0,0,0))`;
      s.style.filter = `blur(${h > 10 ? 6 : 2}px)`;
      layer.appendChild(s);
      const at = t + i * 0.045;
      tl.fromTo(s, { x: -W * 1.4 * dir, opacity: 0 }, { x: W * 1.3 * dir, opacity: 1, duration: d * 0.95, ease: "power2.inOut" }, at);
      tl.to(s, { opacity: 0, duration: 0.2 }, at + d * 0.7);
    }
    const swap = t + d * 0.6;
    if (o.wash !== false) {
      const w = document.createElement("div");
      w.className = "layer";
      w.style.background = `linear-gradient(90deg,rgba(255,255,255,0),${o.washColor || "rgba(255,246,230,.85)"} 50%,rgba(255,255,255,0))`;
      layer.appendChild(w);
      tl.fromTo(w, { opacity: 0 }, { opacity: 1, duration: 0.22, ease: "power2.in" }, swap - 0.22);
      tl.to(w, { opacity: 0, duration: 0.45, ease: "power2.out" }, swap + 0.01);
    }
    if (o.stage) {
      const st = q(o.stage);
      tl.to(st, { x: 700 * dir, filter: "blur(14px)", duration: swap - t, ease: "power2.in" }, t);
      tl.fromTo(st, { x: -700 * dir, filter: "blur(14px)" }, { x: 0, filter: "blur(0px)", duration: 0.6, ease: "power3.out", immediateRender: false }, swap);
    }
    return swap;
  };

  /** Big rounded blob sweeps across as a wipe. Returns the time it fully covers the frame. */
  MK.blobWipe = function (tl, t, o = {}) {
    const layer = need(q(o.layer), "blobWipe(layer)");
    const W = Film.cfg.width, H = Film.cfg.height;
    const b = document.createElement("div");
    b.className = "mk-blob";
    b.style.width = W * 2.2 + "px"; b.style.height = H * 1.9 + "px";
    b.style.top = -H * 0.45 + "px"; b.style.left = "0px";
    b.style.background = o.color || "#F4EFE3";
    layer.appendChild(b);
    const d = o.dur ?? 1.0, dir = o.from === "left" ? -1 : 1;
    const cover = t + d * 0.5;
    tl.fromTo(b, { x: dir > 0 ? W * 1.05 : -W * 2.25, rotation: -6 * dir }, { x: -W * 0.6, rotation: 0, duration: d * 0.5, ease: "power3.in" }, t);
    if (o.exit !== false) tl.to(b, { x: dir > 0 ? -W * 2.4 : W * 1.1, rotation: 5 * dir, duration: d * 0.5, ease: "power3.out" }, cover);
    return cover;
  };

  /** Fade through a colour. Returns the time the frame is fully covered. */
  MK.fadeThrough = function (tl, t, o = {}) {
    const layer = need(q(o.layer), "fadeThrough(layer)");
    const c = document.createElement("div");
    c.className = "layer";
    c.style.background = o.color || "#000";
    c.style.opacity = "0";
    layer.appendChild(c);
    const d = o.dur ?? 0.8;
    tl.to(c, { opacity: 1, duration: d * 0.5, ease: "power1.in" }, t);
    tl.to(c, { opacity: 0, duration: d * 0.5, ease: "power1.out" }, t + d * 0.5 + (o.hold || 0));
    return t + d * 0.5;
  };

  /**
   * Scene-to-scene transition between two full-frame scene containers.
   *   swap = MK.transition(tl, t, { type, from: "#s1", to: "#s2", dur, dir, color, layer: "#fx" })
   * type: cut | crossfade | blur | zoom | push | whipPan | iris | blinds | shutter | dip
   * Velocity-matched: the outgoing side accelerates (…in), the incoming side decelerates (…out),
   * so the fastest moments meet at the swap. Scene containers must span the transition window
   * (their data-in <= t and data-out >= t + dur). Returns the swap time (midpoint).
   */
  MK.transition = function (tl, t, o = {}) {
    const A = q(o.from), B = q(o.to);
    if (!A || !B) throw new Error("MK.transition: from/to not found");
    const W = Film.cfg.width, H = Film.cfg.height;
    const type = o.type || "crossfade";
    const d = o.dur ?? ({ cut: 0, crossfade: 0.6, blur: 0.5, zoom: 0.55, push: 0.7, whipPan: 0.45, iris: 0.7, blinds: 0.8, shutter: 0.6, dip: 0.8 }[type] ?? 0.6);
    const mid = t + d / 2;
    const dir = o.dir || "left";
    const vx = dir === "left" ? -1 : dir === "right" ? 1 : 0, vy = dir === "up" ? -1 : dir === "down" ? 1 : 0;
    const coverLayer = () => need(q(o.layer || "#fx"), "transition(layer)");
    tl.set(B, { opacity: 0 }, 0);
    switch (type) {
      case "cut":
        tl.set(A, { opacity: 0 }, t); tl.set(B, { opacity: 1 }, t); return t;
      case "crossfade":
        tl.to(A, { opacity: 0, duration: d, ease: "power1.inOut" }, t);
        tl.to(B, { opacity: 1, duration: d, ease: "power1.inOut" }, t);
        return mid;
      case "blur":
        tl.to(A, { opacity: 0, filter: "blur(20px)", duration: d * 0.6, ease: "power2.in" }, t);
        tl.fromTo(B, { opacity: 0, filter: "blur(20px)" }, { opacity: 1, filter: "blur(0px)", duration: d * 0.7, ease: "power3.out", immediateRender: false }, t + d * 0.3);
        return mid;
      case "zoom":
        tl.to(A, { scale: 1.2, opacity: 0, filter: "blur(18px)", duration: d * 0.4, ease: "power3.in" }, t);
        tl.fromTo(B, { scale: 0.78, opacity: 0, filter: "blur(18px)" }, { scale: 1, opacity: 1, filter: "blur(0px)", duration: d * 0.8, ease: "expo.out", immediateRender: false }, t + d * 0.3);
        return t + d * 0.35;
      case "push":
        tl.to(A, { x: vx * W, y: vy * H, duration: d, ease: "power3.inOut" }, t);
        tl.fromTo(B, { x: -vx * W, y: -vy * H, opacity: 1 }, { x: 0, y: 0, duration: d, ease: "power3.inOut", immediateRender: false }, t);
        tl.set(B, { opacity: 1 }, t);
        return mid;
      case "whipPan":
        tl.to(A, { x: vx * 420 || -420, filter: "blur(24px)", opacity: 0, duration: d * 0.5, ease: "power3.in" }, t);
        tl.fromTo(B, { x: -(vx * 420 || -420), filter: "blur(24px)", opacity: 0 }, { x: 0, filter: "blur(0px)", opacity: 1, duration: d * 0.5, ease: "power3.out", immediateRender: false }, mid);
        return mid;
      case "iris": {
        const at = o.at || "50% 50%";
        tl.set(B, { opacity: 1, clipPath: `circle(0% at ${at})` }, t);
        tl.to(B, { clipPath: `circle(80% at ${at})`, duration: d, ease: "power2.inOut" }, t);
        tl.set(A, { opacity: 0 }, t + d);
        tl.set(B, { clipPath: "none" }, t + d);
        return mid;
      }
      case "blinds": case "shutter": {
        const L = coverLayer(); const n = type === "blinds" ? (o.strips || 8) : 2;
        const strips = [];
        for (let i = 0; i < n; i++) {
          const s = document.createElement("div");
          s.style.cssText = `position:absolute;left:0;width:${W}px;top:${(H / n) * i}px;height:${H / n + 1}px;background:${o.color || "#0B0B0E"};transform-origin:${type === "shutter" ? (i ? "50% 100%" : "50% 0%") : "50% 0%"}`;
          L.appendChild(s); strips.push(s);
        }
        const close = d * 0.45, st = type === "blinds" ? 0.035 : 0;
        strips.forEach((s, i) => {
          tl.fromTo(s, { scaleY: 0 }, { scaleY: 1, duration: close, ease: "power3.in" }, t + i * st);
          tl.set(s, { transformOrigin: type === "shutter" ? (i ? "50% 0%" : "50% 100%") : "50% 100%" }, mid + n * st);
          tl.to(s, { scaleY: 0, duration: close, ease: "power3.out" }, mid + n * st + 0.02 + i * st);
        });
        tl.set(A, { opacity: 0 }, mid + n * st); tl.set(B, { opacity: 1 }, mid + n * st);
        return mid + n * st;
      }
      case "dip": {
        const cover = MK.fadeThrough(tl, t, { layer: o.layer || "#fx", color: o.color || "#000", dur: d });
        tl.set(A, { opacity: 0 }, cover); tl.set(B, { opacity: 1 }, cover);
        return cover;
      }
      default: throw new Error("MK.transition: unknown type " + type);
    }
  };

  /** Horizontal blur-mask wipe-out of a line (text smears sideways and clears). */
  MK.blurWipeOut = function (tl, target, t, o = {}) {
    const el = need(q(target), "blurWipeOut");
    const d = o.dur ?? 0.6, dir = o.dir === "left" ? -1 : 1;
    tl.to(el, { x: 120 * dir, scaleX: 1.15, filter: "blur(16px)", opacity: 0, clipPath: dir > 0 ? "inset(0 0 0 100%)" : "inset(0 100% 0 0)", duration: d, ease: "power2.in" }, t);
    return tl;
  };

  /* ============================== AMBIENCE & MOTION ============================== */

  /** Defocused bokeh blooms. edges:true keeps them near the frame edges. Returns elements. */
  MK.bokeh = function (layer, o = {}) {
    const L = need(q(layer), "bokeh(layer)");
    const rnd = MK.rng(o.seed ?? 3);
    const W = Film.cfg.width, H = Film.cfg.height;
    const cols = o.colors || ["rgba(227,179,74,.5)", "rgba(123,108,246,.45)"];
    const els = [];
    for (let i = 0; i < (o.count ?? 6); i++) {
      const s = (o.size || [260, 520]);
      const d = s[0] + rnd() * (s[1] - s[0]);
      let x = rnd() * W, y = rnd() * H;
      if (o.edges !== false) { if (i % 2) x = rnd() < 0.5 ? -d * 0.35 : W - d * 0.65; else y = rnd() < 0.5 ? -d * 0.35 : H - d * 0.65; }
      const b = document.createElement("div");
      b.className = "mk-bokeh";
      const c = cols[i % cols.length];
      b.style.cssText += `left:${x}px;top:${y}px;width:${d}px;height:${d}px;background:radial-gradient(circle,${c} 0%,${c.replace(/[\d.]+\)$/, (m) => (parseFloat(m) * 0.35).toFixed(2) + ")")} 45%,rgba(0,0,0,0) 70%)`;
      L.appendChild(b);
      els.push(b);
    }
    return els;
  };

  /** Slow finite drift for ambient elements between start and end. */
  MK.drift = function (tl, targets, start, end, o = {}) {
    const rnd = MK.rng(o.seed ?? 9);
    qa(targets).forEach((el) => {
      const amp = o.amp ?? 40, off = rnd() * 0.5, span = end - start - off;
      const period = Math.min(o.period ?? 6, span);
      tl.to(el, { x: (rnd() - 0.5) * 2 * amp, y: (rnd() - 0.5) * 2 * amp, duration: period, ease: "sine.inOut", yoyo: true, repeat: MK.repeats(span, period) }, start + off);
    });
    return tl;
  };

  /** Floating hover bob (laptops, phones, cards). */
  MK.hover = function (tl, target, start, end, o = {}) {
    const p = Math.min(o.period ?? 1.7, end - start);
    tl.to(qa(target), { y: -(o.amp ?? 12), rotationZ: o.tilt || 0, duration: p, ease: "sine.inOut", yoyo: true, repeat: MK.repeats(end - start, p) }, start);
    return tl;
  };

  /** Breathing glow / bloom (scale + opacity). */
  MK.breathe = function (tl, target, start, end, o = {}) {
    const p = Math.min(o.period ?? 1.2, end - start);
    tl.to(qa(target), { scale: o.scale ?? 1.08, opacity: o.opacity ?? 0.8, duration: p, ease: "sine.inOut", yoyo: true, repeat: MK.repeats(end - start, p) }, start);
    return tl;
  };

  /** A card peels off a surface toward the camera. ghost = the original slot to dim. */
  MK.lift = function (tl, target, t, to = {}, o = {}) {
    const el = need(q(target), "lift");
    tl.set(el, { opacity: 1 }, t);
    if (o.ghost) tl.to(q(o.ghost), { opacity: o.ghostOpacity ?? 0.18, duration: 0.35 }, t);
    tl.fromTo(el, { z: 0, x: 0, y: 0, rotationX: 0, rotationY: 0, rotationZ: 0, scale: 1 },
      Object.assign({ duration: o.dur ?? 1.1, ease: o.ease || "power3.out" }, to), t);
    tl.set(el, { opacity: 0 }, 0);
    return tl;
  };
  /** Return lifted cards to the surface and hide them. */
  MK.settle = function (tl, targets, t, o = {}) {
    const els = qa(targets);
    tl.to(els, { z: 0, x: 0, y: 0, rotationX: 0, rotationY: 0, rotationZ: 0, scale: 1, duration: o.dur ?? 0.8, ease: "power2.inOut" }, t);
    tl.to(els, { opacity: 0, duration: 0.35 }, t + (o.dur ?? 0.8) * 0.7);
    if (o.ghosts) tl.to(qa(o.ghosts), { opacity: 1, duration: 0.3 }, t + (o.dur ?? 0.8) * 0.6);
    return tl;
  };

  /** Glossy specular sweep (pass the bar element, e.g. laptop.glossBar). */
  MK.gloss = function (tl, bar, t, o = {}) {
    tl.fromTo(q(bar), { x: o.from ?? -500 }, { x: o.to ?? 1400, duration: o.dur ?? 1.6, ease: "power2.inOut", immediateRender: false }, t);
    return tl;
  };

  /* ============================== SHAPE BUILDERS ============================== */

  /** Text riding a circle arc. Rotate the returned element to make the text travel. */
  MK.arcText = function (container, text, o = {}) {
    const C = need(q(container), "arcText");
    const wrap = document.createElement("div");
    wrap.className = "mk-arc";
    if (o.x != null) wrap.style.left = o.x + "px";
    if (o.y != null) wrap.style.top = o.y + "px";
    const r = o.radius ?? 320, fs = o.size ?? 44;
    const arc = o.arc ?? 360;
    const chars = [...text];
    const step = o.spacing ? (o.spacing * fs * 0.6 / r) * (180 / Math.PI) : arc / chars.length;
    const a0 = (o.start ?? -90) - (o.spacing ? (step * (chars.length - 1)) / 2 : 0);
    chars.forEach((ch, i) => {
      const s = document.createElement("span");
      s.textContent = ch;
      s.style.font = o.font || `600 ${fs}px Inter`;
      if (o.color) s.style.color = o.color;
      if (o.letterSpacing) s.style.letterSpacing = o.letterSpacing;
      const a = a0 + i * step;
      s.style.transform = `rotate(${a + 90}deg) translate(0,${-r}px) translate(-50%,0)`;
      wrap.appendChild(s);
    });
    C.appendChild(wrap);
    return wrap;
  };

  /**
   * Rotating 3D band (cylinder) of repeated text. Animate rotationY on the returned el.
   * o.tilt (deg, default -10) and o.roll (deg) angle the ring. Container needs perspective
   * (put it inside an element with style="perspective:1600px").
   */
  MK.band = function (container, text, o = {}) {
    const C = need(q(container), "band");
    const band = document.createElement("div");
    band.className = "mk-band";
    const n = o.faces ?? 14, r = o.radius ?? 700, h = o.height ?? 120;
    const w = 2 * r * Math.tan(Math.PI / n) + 1;
    for (let i = 0; i < n; i++) {
      const f = document.createElement("div");
      f.className = "mk-face";
      f.style.cssText += `width:${w}px;height:${h}px;left:${-w / 2}px;top:${-h / 2}px;transform:rotateY(${(360 / n) * i}deg) translateZ(${r}px);` +
        `background:${o.bg || "#C7F36B"};color:${o.color || "#0B1F1C"};font:${o.font || "800 56px Manrope"};`;
      f.textContent = Array.isArray(text) ? text[i % text.length] : text;
      band.appendChild(f);
    }
    // host pushes the ring back by its radius so the front face sits at natural size
    const host = document.createElement("div");
    host.className = "mk-bandhost";
    host.style.transform = `translateZ(${-r}px) rotateX(${o.tilt ?? -10}deg) rotateZ(${o.roll ?? 0}deg)`;
    if (o.x != null) host.style.left = o.x + "px";
    if (o.y != null) host.style.top = o.y + "px";
    host.appendChild(band);
    C.appendChild(host);
    return band;
  };

  /** Pale repeated typography wall. Returns row elements (use MK.wallScroll). */
  MK.typeWall = function (container, text, o = {}) {
    const C = need(q(container), "typeWall");
    const wall = document.createElement("div");
    wall.className = "mk-wall";
    const rows = [];
    for (let i = 0; i < (o.rows ?? 6); i++) {
      const r = document.createElement("div");
      r.className = "mk-row";
      r.style.font = o.font || "800 150px Manrope";
      r.style.color = o.color || "rgba(11,31,28,.07)";
      r.style.marginLeft = (i % 2 ? -300 : 0) + "px";
      r.textContent = (text + (o.sep ?? "  ·  ")).repeat(o.repeat ?? 6);
      wall.appendChild(r);
      rows.push(r);
    }
    C.appendChild(wall);
    return rows;
  };
  MK.wallScroll = function (tl, rows, start, end, o = {}) {
    rows.forEach((r, i) => tl.fromTo(r, { x: i % 2 ? -(o.dist ?? 400) : 0 }, { x: i % 2 ? 0 : -(o.dist ?? 400), duration: end - start, ease: "none" }, start));
    return tl;
  };

  /**
   * Glowing tube along an SVG path. Returns {core, glow, head}. Draw it with
   * MK.tubeDraw(tl, tube, t, dur) which also moves the bright head along the path.
   */
  MK.tube = function (svg, d, o = {}) {
    const S = need(q(svg), "tube(svg)");
    const ns = "http://www.w3.org/2000/svg";
    const id = "mkg" + Math.floor(MK.rng(d.length)() * 1e9);
    const defs = document.createElementNS(ns, "defs");
    defs.innerHTML = `<linearGradient id="${id}" x1="0" y1="0" x2="1" y2="0">${(o.colors || ["#2EE6C9", "#C7F36B"]).map((c, i, a) => `<stop offset="${i / (a.length - 1)}" stop-color="${c}"/>`).join("")}</linearGradient>` +
      `<filter id="${id}b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="${o.glow ?? 10}"/></filter>`;
    S.appendChild(defs);
    const mk = (w, extra) => { const p = document.createElementNS(ns, "path"); p.setAttribute("d", d); p.setAttribute("fill", "none"); p.setAttribute("stroke", `url(#${id})`); p.setAttribute("stroke-width", w); p.setAttribute("stroke-linecap", "round"); if (extra) p.setAttribute("filter", extra); S.appendChild(p); return p; };
    const glow = mk((o.width ?? 14) * 2.2, `url(#${id}b)`);
    const core = mk(o.width ?? 14);
    const head = document.createElementNS(ns, "circle");
    head.setAttribute("r", (o.width ?? 14) * 0.9); head.setAttribute("fill", o.headColor || "#fff"); head.setAttribute("opacity", "0");
    head.setAttribute("filter", `url(#${id}b)`);
    S.appendChild(head);
    return { core, glow, head };
  };
  MK.tubeDraw = function (tl, tube, t, dur, o = {}) {
    MK.lineDraw(tl, [tube.glow, tube.core], t, { dur, stagger: 0, ease: o.ease || "power1.inOut" });
    const len = tube.core.getTotalLength();
    const p = { v: 0 };
    tl.set(tube.head, { opacity: 1 }, t);
    tl.fromTo(p, { v: 0 }, { v: 1, duration: dur, ease: o.ease || "power1.inOut", onUpdate: () => { const pt = tube.core.getPointAtLength(p.v * len); tube.head.setAttribute("cx", pt.x); tube.head.setAttribute("cy", pt.y); } }, t);
    tl.to(tube.head, { opacity: 0, duration: 0.3 }, t + dur);
    return tl;
  };

  /** Rosette / flower mark as inline SVG (petals, gradient). Returns the <svg>. */
  MK.rosette = function (container, o = {}) {
    const C = need(q(container), "rosette");
    const n = o.petals ?? 8, s = o.size ?? 120, id = "mkr" + n + s;
    const g = (o.colors || ["#C7F36B", "#10B981"]);
    let petals = "";
    for (let i = 0; i < n; i++) petals += `<ellipse cx="50" cy="26" rx="${o.rx ?? 13}" ry="${o.ry ?? 24}" transform="rotate(${(360 / n) * i} 50 50)"/>`;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 100 100");
    svg.setAttribute("width", s); svg.setAttribute("height", s);
    svg.style.position = "absolute"; svg.style.overflow = "visible";
    svg.innerHTML = `<defs><linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset="1" stop-color="${g[1]}"/></linearGradient></defs>` +
      `<g fill="url(#${id})">${petals}</g><circle cx="50" cy="50" r="${o.core ?? 11}" fill="${o.coreColor || "#F4EFE3"}"/>`;
    C.appendChild(svg);
    return svg;
  };

  /* ============================== DEVICE RIGS ============================== */

  /**
   * CSS 3D laptop. Returns {stage, rig, bob, lid, screen, lifts, glossBar, floor}.
   * Put screen content inside `screen` (children with class "scr"); put peel-off cards
   * inside `lifts` (same coordinates as the screen). Animate `rig` for camera moves
   * (x, y, scale, rotationX, rotationY) and `bob` for hover.
   */
  MK.laptop = function (container, o = {}) {
    const C = need(q(container), "laptop");
    const sw = o.screenW ?? 1150, sh = o.screenH ?? 672;
    const lw = sw + 40, lh = sh + 48, bw = lw + 120, bd = Math.round(lh * 1.05);
    const stage = document.createElement("div");
    stage.className = "mk-stage";
    if (o.perspective) stage.style.perspective = o.perspective + "px";
    stage.innerHTML = `
      <div class="mk-rig"><div class="mk-floor"></div><div class="mk-bob">
        <div class="mk-base" style="left:${-bw / 2}px;top:0;width:${bw}px;height:${bd}px;transform:rotateX(90deg)">
          <div class="mk-spk" style="left:22px;top:46px;height:${bd * 0.49}px"></div><div class="mk-spk" style="right:22px;top:46px;height:${bd * 0.49}px"></div>
          <div class="mk-kb" style="left:${(bw - 1060) / 2}px;top:46px;width:1060px;height:${bd * 0.49}px"></div>
          <div class="mk-pad" style="left:${(bw - 600) / 2}px;top:${bd * 0.58}px;width:600px;height:${bd * 0.38}px"></div>
          <div class="mk-front" style="top:${bd}px;width:${bw}px"></div>
          <div class="mk-side" style="left:0;height:${bd}px;transform-origin:0 50%;transform:rotateY(90deg)"></div>
          <div class="mk-side" style="right:0;height:${bd}px;transform-origin:100% 50%;transform:rotateY(-90deg)"></div>
        </div>
        <div class="mk-lid" style="left:${-lw / 2}px;top:${-lh}px;width:${lw}px;height:${lh}px;transform:rotateX(${o.lidTilt ?? 9}deg)">
          <div class="mk-lidback"></div><div class="mk-rim"></div><div class="mk-bezel"><div class="mk-cam"></div></div>
          <div class="mk-screen" style="left:20px;top:20px;width:${sw}px;height:${sh}px"></div>
          <div class="mk-sheen" style="left:20px;top:20px;width:${sw}px;height:${sh}px"></div>
          <div class="mk-gloss" style="left:20px;top:20px;width:${sw}px;height:${sh}px"><div class="mk-glossbar"></div></div>
          <div class="mk-lifts" style="left:20px;top:20px;width:${sw}px;height:${sh}px"></div>
        </div></div></div>`;
    C.appendChild(stage);
    const kb = stage.querySelector(".mk-kb");
    [14, 14, 14, 13, 12, 9].forEach((n, ri) => {
      const r = document.createElement("div"); r.className = "mk-kr"; if (ri === 0) r.style.flex = ".6";
      for (let i = 0; i < n; i++) { const k = document.createElement("div"); k.className = "mk-k"; if (ri === 5 && i === 4) k.style.flex = "5.4"; if ((ri === 3 || ri === 4) && (i === 0 || i === n - 1)) k.style.flex = ri === 3 ? "1.8" : "2.3"; r.appendChild(k); }
      kb.appendChild(r);
    });
    if (o.shadow) stage.querySelector(".mk-floor").style.setProperty("--mk-shadow", o.shadow);
    return {
      stage, rig: stage.querySelector(".mk-rig"), bob: stage.querySelector(".mk-bob"), lid: stage.querySelector(".mk-lid"),
      screen: stage.querySelector(".mk-screen"), lifts: stage.querySelector(".mk-lifts"), glossBar: stage.querySelector(".mk-glossbar"),
      floor: stage.querySelector(".mk-floor"), screenW: sw, screenH: sh,
    };
  };

  /**
   * CSS 3D phone. Returns {stage, rig, phone, screen}. Rotate `phone` rotationZ:90 to go
   * landscape; resize/swap screen content at the same time for aspect-ratio changes.
   */
  MK.phone = function (container, o = {}) {
    const C = need(q(container), "phone");
    const w = o.w ?? 440, h = o.h ?? 900, bz = o.bezel ?? 16, r = o.radius ?? 68;
    const stage = document.createElement("div");
    stage.className = "mk-stage";
    stage.innerHTML = `<div class="mk-rig"><div class="mk-phone" style="left:${-w / 2}px;top:${-h / 2}px;width:${w}px;height:${h}px;--r:${r}px">
      <div class="mk-phone-back"></div><div class="mk-phone-body"></div>
      <div class="mk-phone-screen" style="left:${bz}px;top:${bz}px;width:${w - 2 * bz}px;height:${h - 2 * bz}px;border-radius:${r - bz}px"></div>
      ${o.island === false ? "" : '<div class="mk-phone-island"></div>'}</div></div>`;
    C.appendChild(stage);
    return { stage, rig: stage.querySelector(".mk-rig"), phone: stage.querySelector(".mk-phone"), screen: stage.querySelector(".mk-phone-screen") };
  };

  window.MK = MK;
})();
