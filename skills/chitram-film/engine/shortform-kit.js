/* Chitram Film: short-form edit kit (global SF). Load after motion-kit.js. See SHORTFORM.md.
 *
 * Talking-head / podcast / creator edits: word-synced captions, sticker labels, world switches,
 * punch-ins that hide jump cuts. Everything is placed on the one paused timeline (deterministic).
 *
 *   <script src="assets/words.js"></script>      // window.WORDS = master_words.json (sf.py cut writes it)
 *   SF.captions(tl, WORDS.words, { box: "#caps", style: "clean", skip: [[4.2, 7.1]] })
 *   SF.pop(tl, "#k1", 0.96, { rot: -2 })          // sticker label on its spoken word
 *   SF.typeOn(tl, "#s2a", 4.36)                   // per-letter rise + unblur (spoken line)
 *   SF.blurCut(tl, 4.20, "#footWrap", "#worldWrap")
 *   SF.punches(tl, "#footCam", CUTS, { scales: [1, 1.08] })   // alternate zoom on every jump cut
 *   SF.at(WORDS.words, "job")                     // start time of the first word matching "job"
 */
(function () {
  const SF = {};
  const q = (s) => (typeof s === "string" ? document.querySelector(s) : s);
  const norm = (w) => String(w).toLowerCase().replace(/[^\p{L}\p{N}']/gu, "");

  /** time of the n-th (0-based) word matching text (a single word or a phrase) after `after` s */
  SF.at = function (words, text, o = {}) {
    const want = String(text).split(/\s+/).map(norm).filter(Boolean);
    let n = o.nth || 0;
    for (let i = 0; i < words.length; i++) {
      if (words[i].s < (o.after || 0)) continue;
      if (want.every((w, k) => words[i + k] && norm(words[i + k].w) === w)) {
        if (n-- === 0) return o.end ? words[i + want.length - 1].e : words[i].s;
      }
    }
    throw new Error(`SF.at: "${text}" not found in the transcript`);
  };

  /** sticker/label pop: back-out overshoot that settles on its tilt (one reveal per element) */
  SF.pop = function (tl, sel, t, o = {}) {
    const rot = o.rot || 0;
    tl.fromTo(sel, { opacity: 0, scale: o.from ?? 0.35, rotation: rot - (o.spin ?? 8) },
      { opacity: 1, scale: 1, rotation: rot, duration: o.dur ?? 0.3, ease: o.ease || "back.out(2.4)" }, t);
    return t + (o.dur ?? 0.3);
  };

  /** per-letter type-on: each letter rises and unblurs (spoken-line voice). Lines: <span class="ln"> */
  SF.typeOn = function (tl, sel, t, o = {}) {
    const el = q(sel);
    const lines = el.querySelectorAll(".ln").length ? [...el.querySelectorAll(".ln")] : [el];
    const chars = [];
    lines.forEach((ln) => {
      const txt = ln.textContent; ln.textContent = "";
      for (const c of txt) { const s = document.createElement("span"); s.className = "ch"; s.textContent = c; ln.appendChild(s); chars.push(s); }
    });
    tl.set(el, { opacity: 1 }, t);
    tl.fromTo(chars, { opacity: o.from ?? 0, y: o.y ?? 22, filter: `blur(${o.blur ?? 6}px)` },
      { opacity: 1, y: 0, filter: "blur(0px)", duration: o.dur ?? 0.26, stagger: o.per ?? 0.03, ease: "power3.out" }, t);
    return t + (o.per ?? 0.03) * chars.length + (o.dur ?? 0.26);
  };

  /** world switch: blur-through-cut (outgoing blurs 0.12 s, hard swap at T, incoming unblurs 0.22 s) */
  SF.blurCut = function (tl, T, outEl, inEl, o = {}) {
    const px = o.px ?? 30, a = o.out ?? 0.12, b = o.in ?? 0.22;
    tl.to(outEl, { filter: `blur(${px}px)`, duration: a, ease: "power2.in" }, T - a);
    tl.set(outEl, { opacity: 0, filter: "blur(0px)" }, T);
    tl.set(inEl, { opacity: 1, filter: `blur(${px}px)` }, T);
    tl.to(inEl, { filter: "blur(0px)", duration: b, ease: "power2.out" }, T);
    return T;
  };

  /** jump-cut cover: hard zoom change exactly on the cut frame (editorial punch-in / punch-out).
   *  cuts = [{t}] from cuts.json (or plain times). Alternates the scales so no two neighbours match. */
  SF.punches = function (tl, cam, cuts, o = {}) {
    const scales = o.scales || [1, 1.08];
    const only = o.onlyVisible !== false;
    let k = 0;
    tl.set(cam, { scale: scales[0] }, 0);
    (cuts || []).forEach((c) => {
      const t = typeof c === "number" ? c : c.t;
      if (only && typeof c === "object" && c.visible === false) return;
      if ((o.skip || []).some(([a, b]) => t >= a && t <= b)) return;
      k = (k + 1) % scales.length;
      tl.set(cam, { scale: scales[k] }, t);
    });
  };

  /** punch-in on an emphasis word (hard set, not a tween: reads as a cut, not a zoom) */
  SF.punch = function (tl, cam, t, scale = 1.08) { tl.set(cam, { scale }, t); };

  /** slow push the whole beat (never perfectly still) */
  SF.push = function (tl, cam, t0, t1, from = 1, to = 1.05) {
    tl.fromTo(cam, { scale: from }, { scale: to, duration: t1 - t0, ease: "sine.inOut", immediateRender: false }, t0);
  };

  /** Word-synced captions from the transcript.
   *  styles (engine/shortform.css): clean · bold · serif · label · karaoke
   *  o: box (container), style, maxWords 3, maxChars 18, gap 0.34 (a pause starts a new page),
   *     lead 0.04, hold 0.3, emphasis [words] (accent colour), skip [[t0,t1]] (graphic windows with
   *     their own text), upper (bool), from/to (film window), anim "rise"|"pop"|"none" */
  SF.captions = function (tl, words, o = {}) {
    const box = q(o.box || "#caps");
    const maxW = o.maxWords || 3, maxC = o.maxChars || 18, gap = o.gap ?? 0.34;
    const lead = o.lead ?? 0.04, hold = o.hold ?? 0.3, anim = o.anim || "rise";
    const emph = new Set((o.emphasis || []).map(norm));
    const skip = o.skip || [];
    const inSkip = (t) => skip.some(([a, b]) => t >= a - 0.02 && t < b);
    const ws = words.filter((w) => w.s >= (o.from ?? 0) && w.s < (o.to ?? 1e9) && !inSkip(w.s));
    // paginate: sentence ends, commas, pauses, word/char limits
    const pages = [];
    let cur = [];
    ws.forEach((w, i) => {
      const prev = ws[i - 1];
      const brk = cur.length && (cur.length >= maxW ||
        (cur.map((x) => x.w).join(" ") + " " + w.w).length > maxC ||
        w.s - prev.e > gap || /[.?!,;:]$/.test(prev.w) || inSkip((prev.e + w.s) / 2));
      if (brk) { pages.push(cur); cur = []; }
      cur.push(w);
    });
    if (cur.length) pages.push(cur);
    const out = [];
    pages.forEach((pg, pi) => {
      const el = document.createElement("div");
      el.className = `t sfcap ${o.style || "clean"}`;
      el.dataset.synced = "1";        // check.mjs: read while heard, so 0.5 s on screen is enough
      const spans = pg.map((w) => {
        const s = document.createElement("span");
        s.className = "w" + (emph.has(norm(w.w)) ? " em" : "");
        s.textContent = (o.upper ? w.w.toUpperCase() : w.w).replace(/^-/, "");
        el.appendChild(s); el.appendChild(document.createTextNode(" "));
        return s;
      });
      box.appendChild(el);
      const t0 = Math.max(0, pg[0].s - lead);
      const next = pages[pi + 1];
      let t1 = pg[pg.length - 1].e + hold;
      if (next) t1 = Math.min(t1, next[0].s - lead);
      skip.forEach(([a, b]) => { if (a > t0 && a < t1) t1 = a; });
      t1 = Math.max(t1, t0 + 0.2);
      if (anim === "pop") tl.fromTo(el, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.16, ease: "back.out(2)" }, t0);
      else if (anim === "rise") tl.fromTo(el, { opacity: 0, y: 14, filter: "blur(4px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.14, ease: "power3.out" }, t0);
      else tl.set(el, { opacity: 1 }, t0);
      tl.set(el, { opacity: 0 }, t1);
      // active word (class swap through GSAP's core attr plugin, so seeking backwards restores it)
      pg.forEach((w, k) => {
        const sp = spans[k], base = sp.className;
        const off = k + 1 < pg.length ? Math.max(t0, pg[k + 1].s) : t1;
        tl.set(sp, { attr: { class: base + " on" } }, Math.max(t0, w.s));
        if (off > Math.max(t0, w.s)) tl.set(sp, { attr: { class: base } }, off);
      });
      out.push({ el, t0, t1, text: pg.map((w) => w.w).join(" ") });
    });
    return out;
  };

  window.SF = SF;
})();
