/*
 * Chitram Film FX kit (window.FX): the cinematic + viral finishing layer. ENGINE §4 "FX kit", MUSIC.md.
 * Load after motion-kit.js:  <script src="engine/fx-kit.js"></script>
 *
 * Same contract as MK: every call ADDS tweens to the one paused timeline at absolute time t, and
 * everything visible is a pure function of t (seeded noise, no Math.random, no rAF), so seek + render
 * stay frame-exact. Beat-locked calls take times from the music grid: window.MUSIC (audio/music.py fit
 * -> assets/<name>.beats.js): MUSIC.beats / downbeats / phrases / accents / drop.
 *
 *   Camera / energy   FX.punch · FX.beatPulse · FX.shake · FX.drift · FX.speedRamp
 *   Light / texture   FX.flash · FX.lightLeak · FX.grain · FX.vignette · FX.glow · FX.grade · FX.letterbox
 *   Transitions       FX.zoomBlur · FX.rgbSplit · FX.whiteOut · FX.beatCuts
 *   Music             FX.onBeats · FX.grid
 *   Music-video pack  FX.wiggle · FX.handheld · FX.rig · FX.zoomIn · FX.wipe · FX.slideWipe · FX.flip3d ·
 *                     FX.splatter · FX.tear · FX.dof · FX.popUp · FX.shine · FX.sweepLight · FX.zoom3d · FX.xyz ·
 *                     FX.parallax · FX.particles (dust/sparks/embers/confetti/snow/burst/bokeh)
 */
(function () {
  "use strict";
  const FX = {};
  const q = (x) => (typeof x === "string" ? document.querySelector(x) : x);
  const qa = (x) => (typeof x === "string" ? [...document.querySelectorAll(x)] : Array.isArray(x) ? x.map(q) : [q(x)]);
  const root = () => document.querySelector("[data-film]");
  const rng = (seed) => { let a = (seed >>> 0) || 1; return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
  const layer = (id, z) => {
    let el = document.getElementById(id);
    if (!el) {
      el = document.createElement("div"); el.id = id;
      el.style.cssText = `position:absolute;inset:0;pointer-events:none;z-index:${z}`;
      root().appendChild(el);
    }
    return el;
  };

  /* ------------------------------------------------------------------ music grid */
  /** The film's music grid (window.MUSIC from music.py), or an empty grid. */
  FX.grid = () => window.MUSIC || { beats: [], downbeats: [], phrases: [], accents: [], drop: null, bpm: 120 };
  /** Call fn(t, i) for every time in `times` inside [from, to), at most one per `min` seconds. */
  FX.onBeats = function (times, fn, o = {}) {
    const dur = (window.__film && window.__film.cfg.duration) || 1e9;
    const from = o.from ?? 0, to = Math.min(o.to ?? 1e9, dur), min = o.min ?? 0, every = o.every ?? 1;
    let last = -1e9, k = 0;
    (times || []).forEach((t) => {
      if (t < from || t >= to) return;
      if ((k++ % every) !== 0 || t - last < min) return;
      fn(t, k - 1); last = t;
    });
  };

  /* ------------------------------------------------------------------ camera / energy */
  /** Beat zoom punch: snap in on t, ease back (velocity-edit "hit"). Animate a wrapper, not the footage. */
  FX.punch = function (tl, target, t, o = {}) {
    const s = o.scale ?? 1.08, dur = o.dur ?? .32, attack = o.attack ?? .045;
    tl.to(target, { scale: s, duration: attack, ease: "power2.out", overwrite: false }, t - attack * .5);
    tl.to(target, { scale: o.rest ?? 1, duration: dur, ease: "expo.out" }, t + attack * .5);
  };
  /** Small pulse on every beat (or every Nth) between from/to: the edit "breathes" with the music. */
  FX.beatPulse = function (tl, target, beats, o = {}) {
    FX.onBeats(beats || FX.grid().beats, (t) => FX.punch(tl, target, t, { scale: o.scale ?? 1.025, dur: o.dur ?? .22, attack: .03 }),
      { from: o.from, to: o.to, every: o.every ?? 1 });
  };
  /** Camera shake: decaying seeded noise (impact, bass drop, explosion). freq = shakes per second. */
  FX.shake = function (tl, target, t, o = {}) {
    const dur = o.dur ?? .45, amp = o.amp ?? 16, rot = o.rot ?? 1.2, freq = o.freq ?? 26, r = rng(o.seed ?? Math.round(t * 1000));
    const n = Math.max(2, Math.round(dur * freq)), kf = [];
    for (let i = 1; i <= n; i++) {
      const d = Math.pow(1 - i / n, o.decay ?? 1.6);
      kf.push({ x: (r() * 2 - 1) * amp * d, y: (r() * 2 - 1) * amp * d * .8, rotation: (r() * 2 - 1) * rot * d, duration: dur / n, ease: "none" });
    }
    kf.push({ x: 0, y: 0, rotation: 0, duration: .04 });
    tl.to(target, { keyframes: kf }, t);
  };
  /** Slow handheld drift over a window (seeded, smooth): makes static frames feel shot, not rendered. */
  FX.drift = function (tl, target, t0, t1, o = {}) {
    const amp = o.amp ?? 8, period = o.period ?? 2.2, r = rng(o.seed ?? 7), kf = [];
    for (let t = t0; t < t1; t += period) kf.push({ x: (r() * 2 - 1) * amp, y: (r() * 2 - 1) * amp * .6, rotation: (r() * 2 - 1) * .35, duration: Math.min(period, t1 - t), ease: "sine.inOut" });
    tl.to(target, { keyframes: kf }, t0);
  };
  /**
   * Speed ramp / velocity edit on footage (<video data-at> or <img data-seq>): keys [[filmT, speed], ...]
   * e.g. [[2.0,1],[2.4,.25],[3.1,.25],[3.25,3],[3.6,1]] = slow-mo into a whip, snap back on the beat.
   * Speeds are eased (smoothstep) between keys; source time is integrated so motion never jumps.
   * Writes data-remap; the runtime seeks the footage through it. src0 = source seconds at the first key.
   */
  FX.speedRamp = function (target, keys, o = {}) {
    const el = q(target), at = parseFloat(el.dataset.at || "0");
    const src0 = o.src0 ?? (keys[0][0] - at) * parseFloat(el.dataset.rate || "1");
    const dt = 1 / 120, map = [[keys[0][0], src0]];
    let src = src0;
    for (let i = 1; i < keys.length; i++) {
      const [ta, sa] = keys[i - 1], [tb, sb] = keys[i];
      for (let t = ta + dt; t <= tb + 1e-9; t += dt) {
        const u = (t - ta) / (tb - ta), e = u * u * (3 - 2 * u);
        src += (sa + (sb - sa) * e) * dt; map.push([+t.toFixed(5), +src.toFixed(5)]);
      }
    }
    el.dataset.remap = JSON.stringify(map); el._remap = null;
    return src;                                                      // source time at the last key
  };

  /* ------------------------------------------------------------------ light / texture */
  /** Full-frame flash (white = impact, colour = brand hit). Peaks ON t. */
  FX.flash = function (tl, t, o = {}) {
    const L = layer("fxFlash", 90), f = document.createElement("div");
    f.style.cssText = `position:absolute;inset:0;background:${o.color || "#fff"};opacity:0;mix-blend-mode:${o.blend || "screen"}`;
    L.appendChild(f);
    tl.to(f, { opacity: o.peak ?? .85, duration: o.attack ?? .035, ease: "none" }, t - (o.attack ?? .035));
    tl.to(f, { opacity: 0, duration: o.dur ?? .22, ease: "power2.out" }, t);
    return f;
  };
  /** Light leak / film burn: warm gradients sweep across the frame (memory, transition, warmth). */
  FX.lightLeak = function (tl, t, o = {}) {
    const L = layer("fxLeak", 80), dur = o.dur ?? 1.4, r = rng(o.seed ?? Math.round(t * 997));
    const cols = o.colors || ["rgba(255,140,40,.9)", "rgba(255,60,90,.75)", "rgba(255,220,150,.8)"];
    const side = o.from || (r() < .5 ? "left" : "right");
    const el = document.createElement("div");
    el.style.cssText = `position:absolute;inset:-20%;opacity:0;mix-blend-mode:screen;filter:blur(${o.blur ?? 40}px);` +
      `background:radial-gradient(40% 55% at 30% 40%, ${cols[0]}, transparent 70%),radial-gradient(35% 45% at 65% 60%, ${cols[1]}, transparent 70%),radial-gradient(25% 30% at 50% 30%, ${cols[2]}, transparent 70%)`;
    L.appendChild(el);
    const dx = side === "left" ? -35 : 35;
    tl.fromTo(el, { xPercent: dx, opacity: 0 }, { xPercent: -dx * .6, duration: dur, ease: "sine.inOut", immediateRender: false }, t);
    tl.set(el, { opacity: 0 }, 0);
    tl.to(el, { opacity: o.peak ?? .9, duration: dur * .35, ease: "sine.out" }, t);
    tl.to(el, { opacity: 0, duration: dur * .5, ease: "sine.in" }, t + dur * .5);
    return el;
  };
  /** Film grain over the whole film (or a window): seeded noise frames, `fps` new grains per second. */
  FX.grain = function (tl, o = {}) {
    const L = layer("fxGrain", 85), n = o.frames ?? 8, size = o.size ?? 160, cfg = window.__film.cfg;
    const urls = [], r = rng(o.seed ?? 11);
    for (let k = 0; k < n; k++) {
      const c = document.createElement("canvas"); c.width = c.height = size;
      const g = c.getContext("2d"), im = g.createImageData(size, size);
      for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() - .5) * 255 * (o.contrast ?? 1); im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
      g.putImageData(im, 0, 0); urls.push(c.toDataURL());
    }
    L.style.mixBlendMode = o.blend || "overlay"; L.style.opacity = o.opacity ?? .12;
    L.style.backgroundSize = `${(o.scale ?? 2) * size}px`; L.style.imageRendering = "pixelated";
    const t0 = o.from ?? 0, t1 = o.to ?? cfg.duration, fps = o.fps ?? 24, p = { f: 0 };
    tl.to(p, { f: (t1 - t0) * fps, duration: t1 - t0, ease: "none",
      onUpdate: () => { const i = Math.floor(p.f) % n; L.style.backgroundImage = `url(${urls[i]})`; L.style.backgroundPosition = `${(i * 37) % size}px ${(i * 61) % size}px`; } }, t0);
    return L;
  };
  /** Vignette (static or animated in): darkens the corners, pulls the eye to the centre. */
  FX.vignette = function (tl, o = {}) {
    const L = layer("fxVignette", 84);
    L.style.background = `radial-gradient(ellipse at 50% 50%, transparent ${o.inner ?? 55}%, rgba(0,0,0,${o.strength ?? .55}) 100%)`;
    if (o.at != null) { tl.set(L, { opacity: 0 }, 0); tl.to(L, { opacity: 1, duration: o.dur ?? .6 }, o.at); }
    return L;
  };
  /** Bloom/glow on text or a logo (soft halo in its own colour). */
  FX.glow = function (target, o = {}) {
    qa(target).forEach((el) => { el.style.filter = `drop-shadow(0 0 ${o.size ?? 18}px ${o.color || "currentColor"}) drop-shadow(0 0 ${(o.size ?? 18) * 2.5}px ${o.color2 || o.color || "currentColor"})`; });
  };
  const GRADES = {
    "teal-orange": "contrast(1.12) saturate(1.15) sepia(.12) hue-rotate(-8deg)",
    "warm-film": "contrast(1.06) saturate(1.08) sepia(.22) brightness(1.02)",
    "cold-thriller": "contrast(1.18) saturate(.8) hue-rotate(10deg) brightness(.95)",
    "bleach": "contrast(1.25) saturate(.55) brightness(1.03)",
    "mono-noir": "grayscale(1) contrast(1.3) brightness(.95)",
    "punch": "contrast(1.15) saturate(1.3)",
    "faded-memory": "contrast(.9) saturate(.75) sepia(.25) brightness(1.06)",
  };
  /** CSS colour grade on footage/an image (applied, or tweened in at o.at). Presets: FX.grades. */
  FX.grade = function (tl, target, preset, o = {}) {
    const f = GRADES[preset] || preset;
    if (o.at == null) qa(target).forEach((el) => (el.style.filter = f));
    else tl.to(target, { filter: f, duration: o.dur ?? .5, ease: "sine.inOut" }, o.at);
  };
  FX.grades = Object.keys(GRADES);
  /** Cinematic letterbox bars slide in (2.39:1 by default) — trailer / "this is serious" moments. */
  FX.letterbox = function (tl, t, o = {}) {
    const cfg = window.__film.cfg, L = layer("fxBars", 88);
    // landscape: true 2.39:1 bars. Vertical (9:16): a 2.39 crop would eat 75 % of the frame, so default to
    // thin cinema bars (9 % each) unless o.ratio / o.bar is given.
    const vertical = cfg.height > cfg.width;
    const bar = o.bar ?? (o.ratio || !vertical ? Math.max(0, (cfg.height - cfg.width / (o.ratio ?? 2.39)) / 2) : cfg.height * .09);
    const mk = (top) => { const b = document.createElement("div"); b.style.cssText = `position:absolute;left:0;right:0;height:${bar}px;background:${o.color || "#000"};${top ? "top:0" : "bottom:0"}`; L.appendChild(b); return b; };
    const a = mk(true), b = mk(false);
    tl.fromTo(a, { yPercent: -100 }, { yPercent: 0, duration: o.dur ?? .6, ease: "power3.out" }, t);
    tl.fromTo(b, { yPercent: 100 }, { yPercent: 0, duration: o.dur ?? .6, ease: "power3.out" }, t);
    if (o.out != null) { tl.to(a, { yPercent: -100, duration: .5, ease: "power2.in" }, o.out); tl.to(b, { yPercent: 100, duration: .5, ease: "power2.in" }, o.out); }
    return [a, b];
  };

  /* ------------------------------------------------------------------ transitions */
  /** Zoom-blur transition: outgoing rushes into the lens, incoming lands from it. Swap = t. Add FX.flash(t) for punch. */
  FX.zoomBlur = function (tl, from, to, t, o = {}) {
    const d = o.dur ?? .36, z = o.zoom ?? 1.35, b = o.blur ?? 14;
    tl.to(from, { scale: z, filter: `blur(${b}px) brightness(1.25)`, duration: d / 2, ease: "power3.in" }, t - d / 2);
    if (o.hideTo !== false) tl.set(to, { autoAlpha: 0 }, 0);
    tl.set(from, { autoAlpha: 0 }, t);
    tl.fromTo(to, { autoAlpha: 1, scale: 1 / z * 1.6, filter: `blur(${b}px) brightness(1.25)` },
      { scale: 1, filter: "blur(0px) brightness(1)", duration: d / 2 + .1, ease: "power3.out", immediateRender: false }, t);
    return t;
  };
  /** RGB split / chromatic glitch on an element for `dur` (trailer glitch, beat switch, error). */
  FX.rgbSplit = function (tl, target, t, o = {}) {
    const el = q(target), id = "fxrgb" + Math.round(t * 1000) + Math.floor(rng(t * 1e3)() * 1e6);
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", 0); svg.setAttribute("height", 0); svg.style.position = "absolute";
    svg.innerHTML = `<filter id="${id}" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
      <feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/>
      <feOffset in="r" dx="0" dy="0" result="ro"/>
      <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1 0" result="gb"/>
      <feOffset in="gb" dx="0" dy="0" result="gbo"/>
      <feBlend in="ro" in2="gbo" mode="screen"/></filter>`;
    root().appendChild(svg);
    const [ro, gbo] = svg.querySelectorAll("feOffset"), px = o.px ?? 14, dur = o.dur ?? .28;
    tl.set(el, { filter: `url(#${id})` }, t);
    const r = rng(Math.round(t * 1000)), kf = [];
    for (let i = 0; i < 6; i++) kf.push({ attr: { dx: (r() * 2 - 1) * px * (1 - i / 6) }, duration: dur / 6, ease: "steps(1)" });
    tl.to(ro, { keyframes: kf }, t);
    tl.to(gbo, { keyframes: kf.map((k) => ({ ...k, attr: { dx: -k.attr.dx } })) }, t);
    tl.set(el, { filter: "none" }, t + dur);
  };
  /** White-out: the frame burns to white, swap underneath, comes back (drop / big reveal). */
  FX.whiteOut = function (tl, t, o = {}) {
    const f = FX.flash(tl, t, { peak: 1, attack: o.attack ?? .25, dur: o.dur ?? .45, color: o.color || "#fff", blend: "normal" });
    return t;
  };
  /**
   * Beat cuts: show `scenes` one after another, each cut landing exactly on a music time.
   * scenes = selectors/elements (full-frame); times = cut times (first scene shows from `start`).
   * Optional punch / flash / shake on every cut. Returns the cut times used.
   */
  FX.beatCuts = function (tl, scenes, times, o = {}) {
    const S = qa(scenes), T = [o.start ?? 0, ...times].slice(0, S.length);
    S.forEach((s, i) => tl.set(s, { autoAlpha: 0 }, 0));
    S.forEach((s, i) => {
      if (i >= T.length) return;
      tl.set(s, { autoAlpha: 1 }, T[i]);
      if (i + 1 < T.length) tl.set(s, { autoAlpha: 0 }, T[i + 1]);
      if (i && o.punch) FX.punch(tl, s, T[i], { scale: o.punch === true ? 1.06 : o.punch });
      if (i && o.flash) FX.flash(tl, T[i], { peak: o.flash === true ? .35 : o.flash, dur: .14 });
      if (i && o.shake) FX.shake(tl, s, T[i], { amp: o.shake === true ? 10 : o.shake, dur: .25 });
    });
    return T.slice(1);
  };


  /* ================================================================== MUSIC-VIDEO ANIMATION PACK
   * Camera moves, 3D, transitions and particles for photos, footage, cut-outs, type and logos.
   * Continuous moves (wiggle, handheld, particles) are per-frame painters (Film.onFrame) and use the CSS
   * `translate`/`rotate`/`scale` properties, which STACK on top of GSAP transforms, so a wiggling layer
   * can still be punched/shaken/flipped without the effects fighting.
   */
  const W_ = () => window.__film.cfg.width, H_ = () => window.__film.cfg.height;
  const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  // smooth 1-D value noise in [-1, 1]: deterministic, continuous (cosine-interpolated lattice)
  const noise = (t, seed) => { const i = Math.floor(t), f = t - i, u = (1 - Math.cos(f * Math.PI)) / 2;
    return (hash(i + seed * 101.3) * (1 - u) + hash(i + 1 + seed * 101.3) * u) * 2 - 1; };
  let partN = 0;
  const persp = (el, p = 1400) => { const par = el.parentElement; if (par && !par.style.perspective) par.style.perspective = p + "px"; };

  /** AE-style wiggle(freq, amp): organic random motion on position / rotation / scale between t0 and t1. */
  FX.wiggle = function (tl, target, t0, t1, o = {}) {
    const els = qa(target), f = o.freq ?? 3, a = o.amp ?? 14, r = o.rot ?? 2, s = o.scale ?? 0, seed = o.seed ?? 3;
    const ramp = o.ramp ?? .25;
    window.Film.onFrame((t) => els.forEach((el, k) => {
      if (t < t0 || t > t1) { el.style.translate = ""; el.style.rotate = ""; if (s) el.style.scale = ""; return; }
      const env = Math.min(1, (t - t0) / ramp, (t1 - t) / ramp), x = t * f;
      el.style.translate = `${(noise(x, seed + k) * a * env).toFixed(2)}px ${(noise(x, seed + k + 7) * a * env).toFixed(2)}px`;
      el.style.rotate = `${(noise(x, seed + k + 13) * r * env).toFixed(3)}deg`;
      if (s) el.style.scale = (1 + noise(x, seed + k + 21) * s * env).toFixed(4);
    }));
  };
  /** Handheld camera: slow body sway + fast micro jitter (shot on a phone / documentary feel). */
  FX.handheld = function (tl, target, t0, t1, o = {}) {
    const els = qa(target), a = o.amp ?? 10, seed = o.seed ?? 5;
    window.Film.onFrame((t) => els.forEach((el) => {
      if (t < t0 || t > t1) { el.style.translate = ""; el.style.rotate = ""; return; }
      const x = noise(t * .45, seed) * a + noise(t * 6, seed + 3) * a * .12, y = noise(t * .38, seed + 1) * a * .7 + noise(t * 7, seed + 4) * a * .1;
      el.style.translate = `${x.toFixed(2)}px ${y.toFixed(2)}px`;
      el.style.rotate = `${(noise(t * .3, seed + 2) * .6 + noise(t * 5, seed + 5) * .06).toFixed(3)}deg`;
    }));
  };
  /** Camera rig: nested wrappers so moves never fight: rig.move (handheld/wiggle) > rig.shake > rig.punch > content. */
  FX.rig = function (target) {
    const el = q(target), mk = (cls) => { const d = document.createElement("div"); d.className = cls; d.style.cssText = "position:absolute;inset:0;transform-origin:50% 50%"; return d; };
    const move = mk("rig-move"), shake = mk("rig-shake"), punch = mk("rig-punch");
    el.parentElement.insertBefore(move, el); move.appendChild(shake); shake.appendChild(punch); punch.appendChild(el);
    return { move, shake, punch, content: el };
  };

  /** Zoom-in transition: push INTO a point of the outgoing scene, land on the next one zooming out of it. */
  FX.zoomIn = function (tl, from, to, t, o = {}) {
    const d = o.dur ?? .5, x = o.x ?? "50%", y = o.y ?? "50%", z = o.zoom ?? 4;
    tl.set(from, { transformOrigin: `${x} ${y}` }, 0);
    tl.to(from, { scale: z, filter: `blur(${o.blur ?? 10}px)`, duration: d * .55, ease: "power4.in" }, t - d * .55);
    tl.set(from, { autoAlpha: 0 }, t);
    if (o.hideTo !== false) tl.set(to, { autoAlpha: 0 }, 0);
    tl.fromTo(to, { autoAlpha: 1, scale: o.landFrom ?? 1.5, filter: `blur(${o.blur ?? 10}px)` },
      { scale: 1, filter: "blur(0px)", duration: d * .7, ease: "expo.out", immediateRender: false }, t);
    return t;
  };
  /** Wipe an element IN (or OUT) with clip-path. dir: left|right|up|down|all (box closes/opens on all sides)
   *  |center-h|center-v|diag. soft: feathered via a blur on the edge layer is not possible with clip-path, so
   *  pair with FX.sweepLight for a glowing edge. */
  FX.wipe = function (tl, target, t, o = {}) {
    const d = o.dur ?? .6, out = o.mode === "out", dir = o.dir || "left";
    const shut = { left: "inset(0 100% 0 0)", right: "inset(0 0 0 100%)", up: "inset(100% 0 0 0)", down: "inset(0 0 100% 0)",
      all: "inset(50% 50% 50% 50%)", "center-h": "inset(0 50% 0 50%)", "center-v": "inset(50% 0 50% 0)",
      diag: "polygon(0 0, 0 0, 0 0, 0 0)" }[dir];
    const open = dir === "diag" ? "polygon(0 0, 200% 0, 0 200%, 0 0)" : "inset(0 0 0 0)";
    if (!out) tl.set(target, { clipPath: shut, autoAlpha: 1 }, 0);
    tl.fromTo(target, { clipPath: out ? open : shut }, { clipPath: out ? shut : open, duration: d, ease: o.ease || "power3.inOut", immediateRender: false }, t);
    return t + d;
  };
  /** Slight slide wipe: outgoing pushes ~12% left/right with motion blur, incoming slides in from the other side. */
  FX.slideWipe = function (tl, from, to, t, o = {}) {
    const d = o.dur ?? .38, s = (o.dir === "right" ? 1 : -1) * (o.dist ?? 12), over = 1 + 2 * Math.abs(s) / 100 + .03;
    // both scenes move together through the swap (no gap where a lower layer could flash through)
    tl.to(from, { xPercent: s, scale: over, filter: "blur(8px)", duration: d, ease: "power3.in" }, t - d);   // overscale: no edge gap
    tl.to(from, { autoAlpha: 0, duration: d * .5, ease: "power1.in" }, t - d * .1);
    if (o.hideTo !== false) tl.set(to, { autoAlpha: 0 }, 0);
    tl.fromTo(to, { xPercent: -s, scale: over, autoAlpha: 0, filter: "blur(8px)" },
      { xPercent: 0, scale: 1, autoAlpha: 1, filter: "blur(0px)", duration: d + .1, ease: "power3.out", immediateRender: false }, t - d * .4);
    return t;
  };
  /** 3D flip transition (card turn): outgoing rotates away on Y (or X), incoming completes the turn. */
  FX.flip3d = function (tl, from, to, t, o = {}) {
    const d = o.dur ?? .55, ax = o.axis === "x" ? "rotationX" : "rotationY", sg = o.reverse ? -1 : 1;
    [from, to].forEach((x) => { persp(q(x), o.perspective ?? 1600); gsap.set(x, { backfaceVisibility: "hidden", transformStyle: "preserve-3d" }); });
    if (o.hideTo !== false) tl.set(to, { autoAlpha: 0 }, 0);
    if (o.backdrop !== false) {                                   // what the viewer sees behind the turning card
      const bd = document.createElement("div"), f = q(from);
      bd.style.cssText = `position:absolute;inset:0;background:${o.backdrop || "#0b0b0e"};visibility:hidden`;
      f.parentElement.insertBefore(bd, f);
      tl.set(bd, { visibility: "visible" }, t - d / 2); tl.set(bd, { visibility: "hidden" }, t + d / 2 + .1);
    }
    tl.to(from, { [ax]: 90 * sg, scale: .92, duration: d / 2, ease: "power2.in" }, t - d / 2);
    tl.set(from, { autoAlpha: 0 }, t);
    tl.fromTo(to, { [ax]: -90 * sg, scale: .92, autoAlpha: 1 }, { [ax]: 0, scale: 1, duration: d / 2 + .08, ease: "back.out(1.4)", immediateRender: false }, t);
    return t;
  };
  /** Paint splatter transition: ink blobs burst over the frame (full cover at t), swap, then shrink away.
   *  zoom: also punch the incoming scene in. colors: brand inks. Blobs are seeded, so every render matches. */
  FX.splatter = function (tl, t, o = {}) {
    const L = layer("fxSplat", 87), r = rng(o.seed ?? Math.round(t * 991)), n = o.count ?? 9, d = o.dur ?? .55;
    const cols = o.colors || ["#111", "#E8572A", "#F2C14E"], W = W_(), H = H_();
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.style.cssText = "position:absolute;inset:0;width:100%;height:100%;overflow:visible";
    const blobs = [];
    for (let i = 0; i < n; i++) {
      const cx = r() * W, cy = r() * H, R = Math.max(W, H) * (.32 + r() * .3), pts = [], m = 26;
      for (let k = 0; k < m; k++) {                                 // irregular rim + finger-like spikes
        const a = k / m * Math.PI * 2, spike = r() < .3 ? 1.25 + r() * .35 : 1;
        const rr = R * (.78 + r() * .22) * spike; pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
      }
      // smooth closed Catmull-Rom curve through the rim points -> wet, organic ink edge
      let dd = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
      for (let k = 0; k < m; k++) {
        const p0 = pts[(k - 1 + m) % m], p1 = pts[k], p2 = pts[(k + 1) % m], p3 = pts[(k + 2) % m];
        const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
        dd += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
      }
      const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
      p.setAttribute("d", dd + " Z");
      p.setAttribute("fill", cols[i % cols.length]); p.style.transformOrigin = `${cx}px ${cy}px`; p.style.transformBox = "view-box";
      svg.appendChild(p); blobs.push(p);
      for (let k = 0; k < 4; k++) {                                  // satellite droplets
        const c = document.createElementNS("http://www.w3.org/2000/svg", "circle"), a = r() * 6.28, dd = R * (1.1 + r() * .5);
        c.setAttribute("cx", cx + Math.cos(a) * dd); c.setAttribute("cy", cy + Math.sin(a) * dd); c.setAttribute("r", 8 + r() * 30);
        c.setAttribute("fill", cols[i % cols.length]); c.style.transformOrigin = `${cx}px ${cy}px`; c.style.transformBox = "view-box";
        svg.appendChild(c); blobs.push(c);
      }
    }
    L.appendChild(svg);
    tl.set(blobs, { scale: 0 }, 0);
    blobs.forEach((b, i) => tl.to(b, { scale: 1, duration: d * .6, ease: "expo.out" }, t - d * .6 + (i % 5) * .012));
    blobs.forEach((b, i) => tl.to(b, { scale: 0, duration: d * .6, ease: "power2.inOut" }, t + .04 + (i % 4) * .015));
    if (o.zoomTarget) tl.fromTo(o.zoomTarget, { scale: 1.25 }, { scale: 1, duration: .6, ease: "expo.out", immediateRender: false }, t);
    return t;
  };
  /** Torn-paper transition (ED.tear if the editorial kit is loaded, else a jagged paper edge sweep). */
  FX.tear = function (tl, target, t, o = {}) {
    if (window.ED && window.ED.tear) return window.ED.tear(tl, target, t, o.dur ?? .5, o.layer || "#fx", o.seed ?? 11);
    const el = q(target), W = W_(), H = H_(), R = rng(o.seed ?? 11), J = Array.from({ length: 22 }, () => (R() - .5) * 70);
    const P = { x: W + 180 }, d = o.dur ?? .5;
    tl.fromTo(P, { x: W + 180 }, { x: -260, duration: d, ease: "power2.inOut", immediateRender: false,
      onUpdate: () => { el.style.clipPath = `polygon(0 0, ${J.map((j, i) => `${P.x + j}px ${(i / (J.length - 1)) * H}px`).join(",")}, 0 ${H}px)`; } }, t);
    tl.set(el, { autoAlpha: 0 }, t + d);
  };
  /** Depth of field: keep the subject sharp, blur the background (and optionally foreground); rack focus at o.at. */
  FX.dof = function (tl, o = {}) {
    const bg = o.bg && qa(o.bg), fg = o.fg && qa(o.fg), amt = o.blur ?? 10;
    if (bg) tl.set(bg, { filter: `blur(${amt}px)`, scale: o.bgScale ?? 1.04 }, o.from ?? 0);
    if (o.at != null && o.subject) {                                // rack focus: subject goes soft, background sharpens
      tl.to(o.subject, { filter: `blur(${amt}px)`, duration: o.dur ?? .7, ease: "sine.inOut" }, o.at);
      if (bg) tl.to(bg, { filter: "blur(0px)", duration: o.dur ?? .7, ease: "sine.inOut" }, o.at);
    }
    if (fg) tl.set(fg, { filter: `blur(${amt * 1.6}px)` }, o.from ?? 0);
  };
  /** Pop-up: squash -> overshoot -> settle, with a slight tilt and a soft shadow lift (stickers, cards, emojis, cut-outs). */
  FX.popUp = function (tl, target, t, o = {}) {
    const els = qa(target), st = o.stagger ?? .06;
    tl.set(els, { autoAlpha: 0, scale: 0 }, 0);
    els.forEach((el, i) => {
      const t0 = t + i * st, rot = o.rot ?? (i % 2 ? 6 : -6);
      tl.set(el, { autoAlpha: 1, scaleX: .2, scaleY: .2, rotation: rot * 2, y: o.y ?? 40 }, t0);
      tl.to(el, { scaleX: 1.12, scaleY: .9, y: 0, rotation: -rot * .4, duration: .14, ease: "power3.out" }, t0);
      tl.to(el, { scaleX: .96, scaleY: 1.06, rotation: rot * .2, duration: .1, ease: "sine.inOut" }, t0 + .14);
      tl.to(el, { scaleX: 1, scaleY: 1, rotation: 0, duration: .22, ease: "back.out(2)" }, t0 + .24);
    });
  };
  /** Shine: a glossy reflection band sweeps across a logo / card / text / product (premium touch). */
  FX.shine = function (tl, target, t, o = {}) {
    qa(target).forEach((el, i) => {
      if (getComputedStyle(el).position === "static") el.style.position = "relative";
      el.style.overflow = "hidden";
      const b = document.createElement("div");
      b.style.cssText = `position:absolute;top:-50%;bottom:-50%;width:${o.width ?? 35}%;left:-60%;pointer-events:none;mix-blend-mode:${o.blend || "screen"};` +
        `background:linear-gradient(90deg,transparent,${o.color || "rgba(255,255,255,.75)"},transparent);transform:rotate(${o.angle ?? 20}deg)`;
      el.appendChild(b);
      tl.fromTo(b, { left: "-60%" }, { left: "130%", duration: o.dur ?? .8, ease: "power2.inOut", immediateRender: false }, t + i * (o.stagger ?? .1));
    });
  };
  /** Sweep light: an anamorphic light beam crosses the whole frame (beat accent, reveal, chapter start). */
  FX.sweepLight = function (tl, t, o = {}) {
    const L = layer("fxSweep", 86), el = document.createElement("div"), W = W_();
    el.style.cssText = `position:absolute;top:-30%;bottom:-30%;width:${o.width ?? 22}%;left:0;mix-blend-mode:screen;opacity:0;` +
      `background:linear-gradient(90deg,transparent,${o.color || "rgba(255,240,210,.85)"},transparent);filter:blur(${o.blur ?? 18}px);transform:rotate(${o.angle ?? 12}deg)`;
    L.appendChild(el);
    const fromX = o.dir === "left" ? W * 1.2 : -W * .4, toX = o.dir === "left" ? -W * .4 : W * 1.2, d = o.dur ?? .9;
    tl.fromTo(el, { x: fromX, opacity: 0 }, { x: toX, duration: d, ease: "power2.inOut", immediateRender: false }, t);
    tl.to(el, { opacity: o.peak ?? .9, duration: d * .3 }, t); tl.to(el, { opacity: 0, duration: d * .3 }, t + d * .7);
    return el;
  };
  /** 3D zoom on the Z axis: the element flies from depth to the lens (or past it, o.through) in perspective. */
  FX.zoom3d = function (tl, target, t, o = {}) {
    const el = q(target); persp(el, o.perspective ?? 1200);
    const d = o.dur ?? .8;
    tl.fromTo(el, { z: o.from ?? -1400, autoAlpha: o.fade === false ? 1 : 0, filter: "blur(6px)" },
      { z: o.to ?? 0, autoAlpha: 1, filter: "blur(0px)", duration: d, ease: o.ease || "expo.out", immediateRender: false }, t);
    if (o.through) tl.to(el, { z: 900, autoAlpha: 0, filter: "blur(10px)", duration: o.throughDur ?? .45, ease: "power3.in" }, o.through);
  };
  /** XYZ 3D move: rotate on X/Y/Z axes while zooming in Z (orbiting cards, 3D logo turn, tilted product). */
  FX.xyz = function (tl, target, t, o = {}) {
    const el = q(target); persp(el, o.perspective ?? 1400);
    gsap.set(el, { transformStyle: "preserve-3d" });
    const from = o.from || { rotationX: 25, rotationY: -35, rotationZ: -6, z: -600 };
    const to = o.to || { rotationX: 0, rotationY: 0, rotationZ: 0, z: 0 };
    tl.fromTo(el, from, { ...to, duration: o.dur ?? 1.2, ease: o.ease || "power3.out", immediateRender: false }, t);
  };
  /** 2.5D parallax dolly: layers = [{el, depth}] (0 = far background, 1 = foreground cut-out). The camera
   *  pushes / pans and nearer layers move more: turns one photo + its cut-out into a 3D-feeling shot. */
  FX.parallax = function (tl, layers, t0, t1, o = {}) {
    const push = o.push ?? .12, pan = o.pan ?? 0;
    layers.forEach(({ el, depth }) => tl.fromTo(el, { scale: 1, xPercent: 0 },
      { scale: 1 + push * (.3 + depth), xPercent: pan * (.2 + depth), duration: t1 - t0, ease: o.ease || "sine.inOut", immediateRender: false }, t0));
  };
  /** Particles on a canvas, a pure function of t. type: dust | sparks | embers | confetti | snow | burst | bokeh.
   *  burst: everything explodes from (x, y) at o.at. Others drift continuously between from/to. */
  FX.particles = function (tl, o = {}) {
    const W = W_(), H = H_(), L = layer(o.id || ("fxPart" + (++partN)), o.z ?? 83);
    const c = document.createElement("canvas"); c.width = W; c.height = H; c.style.cssText = "position:absolute;inset:0;width:100%;height:100%";
    if (o.blend) c.style.mixBlendMode = o.blend; L.appendChild(c);
    const g = c.getContext("2d"), type = o.type || "dust", n = o.count ?? (type === "confetti" ? 140 : type === "burst" ? 90 : 70);
    const R = rng(o.seed ?? 9), cols = o.colors || ({ sparks: ["#FFD27A", "#FFF3C4", "#FF9F45"], embers: ["#FF6A2A", "#FFB347"],
      confetti: ["#E8572A", "#F2C14E", "#4ECDC4", "#FFFFFF", "#9B5DE5"], snow: ["#FFFFFF"], dust: ["rgba(255,240,220,.9)"],
      burst: ["#FFFFFF", "#FFD27A"], bokeh: ["rgba(255,210,150,.35)", "rgba(150,200,255,.3)"] }[type] || ["#fff"]);
    const P = Array.from({ length: n }, () => ({ x: R(), y: R(), s: R(), a: R() * 6.283, v: .4 + R(), w: R() * 6.283, c: cols[Math.floor(R() * cols.length)] }));
    const from = o.from ?? 0, to = o.to ?? window.__film.cfg.duration, at = o.at ?? from;
    window.Film.onFrame((t) => {
      g.clearRect(0, 0, W, H);
      if (t < from || t > to) return;
      const fade = Math.min(1, (t - from) / .3, (to - t) / .3);
      P.forEach((p) => {
        let x, y, size, alpha = fade;
        if (type === "burst") {
          const lt = t - at; if (lt < 0) return;
          const sp = (o.speed ?? 1400) * p.v, life = .9 + p.s * .6; if (lt > life) return;
          x = (o.x ?? W / 2) + Math.cos(p.a) * sp * (1 - Math.exp(-lt * 3)) / 3; y = (o.y ?? H / 2) + Math.sin(p.a) * sp * (1 - Math.exp(-lt * 3)) / 3 + 260 * lt * lt;
          size = (2 + p.s * 5) * (1 - lt / life); alpha = 1 - lt / life;
        } else {
          const lt = t - from, rise = { sparks: -160, embers: -110, snow: 90, confetti: 260, dust: -12, bokeh: -6 }[type] ?? 0;
          x = (p.x * W + Math.sin(lt * .6 * p.v + p.w) * 40 + (type === "confetti" ? Math.sin(lt * 2 + p.w) * 60 : 0)) % W;
          y = ((p.y * H + rise * p.v * lt) % H + H) % H;
          size = type === "bokeh" ? 30 + p.s * 90 : type === "confetti" ? 6 + p.s * 8 : 1 + p.s * (type === "dust" ? 2.4 : 3.5);
          if (type === "sparks" || type === "embers") alpha *= .5 + .5 * Math.sin(lt * 9 * p.v + p.w);
        }
        g.globalAlpha = Math.max(0, Math.min(1, alpha)) * (o.opacity ?? 1); g.fillStyle = p.c;
        if (type === "confetti") { g.save(); g.translate(x, y); g.rotate(p.w + (t - from) * 4 * p.v); g.fillRect(-size / 2, -size / 4, size, size / 2); g.restore(); }
        else { g.beginPath(); g.arc(x, y, size, 0, 6.283); g.fill(); }
      });
      g.globalAlpha = 1;
    });
    return c;
  };

  window.FX = FX;
})();
