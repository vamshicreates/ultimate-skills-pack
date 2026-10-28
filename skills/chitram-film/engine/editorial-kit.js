/* Editorial kit — word-locked, hand-made motion for voice-driven films (global ED).
   Load after motion-kit.js. Proven in personal/content/santhosh-intro (collage → ikigai type → dotted
   characters). Every function takes the paused timeline `tl` and absolute seconds.

   ED.onTwos(tl, fps=12)                   whole film holds each pose 2 frames → stop-motion / hand-made feel
   const T = ED.wordClock(VO)              T(line, wordIndex) → film time of that spoken word (audio/tts_vo.py)
   ED.setWin(sel, in, out)                 set data-in/out from code (times computed from the word clock)
   ED.ik(tl, host, opts)                   ikigai line: words fade in on the voice; a solid circle glides onto a
                                           key word and the text INVERTS inside it (two text layers + clip-path)
     opts {x, y, size, center, italic, color, light, circle, words:[[text, t, css]], kfs:[{t, i, r, dx, dur}]}
     kfs: first = circle pops in (back-out) on word i with radius r; later = glide to word i / resize;
          r:0 = shrink away. Partial cover of a long word ("inters|ection") is the look — keep it.
   ED.iris(tl, x, y, color, t, dur=.38)    colour circle grows from (x,y) to cover → swap scenes under it
                                           (returns the cover time; set the old scene's data-out to it)
   ED.tear(tl, sel, t, dur=.5)             torn-paper wipe: outgoing layer ripped away right→left + paper rim
   ED.boil(tl, selector, D)                paper boil: ±1.2 px / ±0.5° jitter per held frame on every match
   ED.pushThrough(tl, room, dark, x, y, t) camera pushes INTO a point (a laptop screen) while a dark world opens
                                           from that point (Zippet move) — the best "reveal" beat; put the drop here
   ED.walk(tl, el, t0, t1, dx, per=.17)    bob-walk on twos for flat characters (y ±12, rotate ±1.2°) + travel
   ED.jump(tl, el, t, fromX, toX, h, dur)  arc jump (sin), lean and slight shrink — "leaves the crowd" moment
*/
(function () {
  const $ = (s) => (typeof s === "string" ? document.querySelector(s) : s);
  const ease3 = (x) => (x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const backOut = (x) => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  const ED = {};
  // start loading the editorial serif now, so Film.build's fonts.ready wait includes it
  if (document.fonts && document.fonts.load) ["400 40px Gara", "italic 400 40px Gara"].forEach((f) => document.fonts.load(f).catch(() => {}));
  ED.onTwos = (tl, fps = 12) => { const S = 1 / fps, s0 = tl.seek.bind(tl); tl.seek = (t, x) => s0(Math.floor(t / S + 1e-6) * S, x); return S; };
  ED.wordClock = (VO) => { const W = []; VO.words.forEach((w) => (W[w.line] = W[w.line] || []).push(w.t)); return (l, k) => W[l][k]; };
  ED.setWin = (sel, a, b) => { const e = $(sel); e.dataset.in = a; e.dataset.out = b; };

  ED.ik = (tl, host, o) => {
    const D = Film.cfg.duration, H = $(host);
    H.style.cssText = `position:absolute;left:${o.x}px;top:${o.y}px;${o.center ? "width:0" : ""}`;
    const mk = (color) => {
      const L = document.createElement("div");
      L.style.cssText = `position:absolute;left:0;top:0;white-space:nowrap;font:${o.italic ? "italic " : ""}400 ${o.size}px/1.2 ${o.font || "Gara, Georgia, serif"};color:${color};${o.center ? "transform:translateX(-50%)" : ""}`;
      o.words.forEach(([w, , st]) => { const s = document.createElement("span"); s.textContent = w; s.style.cssText = "display:inline-block;margin-right:.24em;" + (st || ""); L.appendChild(s); });
      return L;
    };
    const dark = mk(o.color || "#2B2B2B"), light = mk(o.light || "#EDECE8"), circ = document.createElement("div");
    circ.style.cssText = `position:absolute;left:0;top:0;border-radius:50%;background:${o.circle || "#2B2B2B"};opacity:0`;
    H.append(dark, circ, light);
    const ds = [...dark.children], ls = [...light.children];
    o.words.forEach(([, t], i) => tl.fromTo([ds[i], ls[i]], { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .24, ease: "power2.out" }, t - .03));
    // measure lazily and again once webfonts are loaded (measuring before the font arrives puts the circle off the word)
    let half = 0, K = [], measuredLoaded = false;
    const measure = () => {
      half = o.center ? dark.offsetWidth / 2 : 0;
      const at = (i, dx = 0) => ({ x: ds[i].offsetLeft + ds[i].offsetWidth * .5 - half + dx, y: ds[i].offsetTop + ds[i].offsetHeight * .56 });
      K = (o.kfs || []).map((k) => ({ ...k, ...at(k.i, k.dx || 0) }));
      measuredLoaded = !document.fonts || document.fonts.status === "loaded";
    };
    measure();
    const state = (tt) => {
      if (!measuredLoaded) measure();
      if (!K.length || tt < K[0].t) return null;
      let s = { x: K[0].x, y: K[0].y, r: K[0].r * backOut(Math.min(1, (tt - K[0].t) / .32)) };
      for (let j = 1; j < K.length && tt >= K[j].t; j++) {
        const e = ease3(Math.min(1, (tt - K[j].t) / (K[j].dur || .4))), a = K[j - 1];
        s = { x: a.x + (K[j].x - a.x) * e, y: a.y + (K[j].y - a.y) * e, r: a.r + (K[j].r - a.r) * e };
      }
      return s;
    };
    tl.to({}, { duration: D, ease: "none", onUpdate() {
      const s = state(tl.time());
      if (!s || s.r <= .5) { circ.style.opacity = 0; light.style.clipPath = "circle(0px at 0 0)"; return; }
      circ.style.opacity = 1; circ.style.width = circ.style.height = 2 * s.r + "px";
      circ.style.left = s.x - s.r + "px"; circ.style.top = s.y - s.r + "px";
      light.style.clipPath = `circle(${s.r}px at ${s.x + half}px ${s.y}px)`;
    } }, 0);
    return H;
  };

  ED.iris = (tl, x, y, color, t, dur = .38, layer = "#fx") => {
    const c = document.createElement("div"), R = 1300;
    c.style.cssText = `position:absolute;left:${x - R}px;top:${y - R}px;width:${2 * R}px;height:${2 * R}px;border-radius:50%;background:${color};transform:scale(0)`;
    $(layer).appendChild(c);
    tl.fromTo(c, { scale: 0 }, { scale: 1, duration: dur, ease: "power3.in", immediateRender: false }, t);
    tl.set(c, { opacity: 1 }, 0); tl.set(c, { opacity: 0 }, t + dur + 1 / 12);
    return t + dur;
  };

  ED.tear = (tl, sel, t, dur = .5, layer = "#fx", seed = 11) => {
    const R = MK.rng(seed), J = Array.from({ length: 20 }, () => (R() - .5) * 70), J2 = J.map((j) => j + 14 + R() * 26);
    const W = Film.cfg.width, H = Film.cfg.height, el = $(sel), rim = document.createElement("div");
    rim.style.cssText = "position:absolute;inset:0;background:#FBF8F1;opacity:0"; $(layer).appendChild(rim);
    const P = { x: W + 180 }, poly = (x, A) => A.map((j, i) => `${x + j}px ${(i / (A.length - 1)) * H}px`);
    tl.set(rim, { opacity: 1 }, t); tl.set(rim, { opacity: 0 }, t + dur + 1 / 12);
    tl.fromTo(P, { x: W + 180 }, { x: -260, duration: dur, ease: "power2.inOut", onUpdate: () => {
      const a = poly(P.x, J), b = poly(P.x, J2).reverse();
      el.style.clipPath = `polygon(0 0, ${a.join(",")}, 0 ${H}px)`; rim.style.clipPath = `polygon(${a.join(",")}, ${b.join(",")})`;
    } }, t);
  };

  ED.boil = (tl, selector, D, amp = 2.4, rot = 1, fps = 12) => {
    const els = [...document.querySelectorAll(selector)];
    const h = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
    tl.to({}, { duration: D, ease: "none", onUpdate() {
      const s = Math.round(tl.time() * fps);
      els.forEach((el, i) => { el.style.translate = `${((h(s * 7 + i) - .5) * amp).toFixed(2)}px ${((h(s * 13 + i * 3) - .5) * amp).toFixed(2)}px`; el.style.rotate = `${((h(s * 5 + i * 11) - .5) * rot).toFixed(2)}deg`; });
    } }, 0);
  };

  ED.pushThrough = (tl, room, dark, x, y, t, dur = .5) => {
    tl.to(room, { scale: 7, transformOrigin: `${x}px ${y}px`, duration: dur, ease: "power3.in" }, t - .15);
    const P = { r: 0 }, d = $(dark); d.style.clipPath = `circle(0px at ${x}px ${y}px)`;
    tl.fromTo(P, { r: 0 }, { r: 2300, duration: dur - .05, ease: "power3.in", onUpdate: () => { d.style.clipPath = `circle(${P.r}px at ${x}px ${y}px)`; } }, t);
    return t + dur;   // ← land the music drop here
  };

  ED.walk = (tl, el, t0, t1, dx, per = .17, phase = 0) => {
    tl.fromTo(el, { x: 0 }, { x: dx, duration: t1 - t0, ease: "none" }, t0);
    for (let k = 0; t0 + k * per < t1; k++) tl.set(el, { y: k % 2 ? -12 : 0, rotation: k % 2 ? 1.2 : -1.2 }, t0 + k * per + phase);
  };

  ED.jump = (tl, el, t, fromX, toX, h = 330, dur = .55, flip = true) => {
    const J = { p: 0 }, e = $(el);
    tl.fromTo(J, { p: 0 }, { p: 1, duration: dur, ease: "power1.inOut", onUpdate: () => {
      const x = fromX + (toX - fromX) * J.p, y = -Math.sin(J.p * Math.PI) * h + J.p * 40;
      e.style.transform = `translate(${x}px, ${y}px)${flip ? " scaleX(-1)" : ""} rotate(${-J.p * 14}deg) scale(${1 - J.p * .25})`;
    } }, t);
    return t + dur;
  };
  window.ED = ED;
})();
