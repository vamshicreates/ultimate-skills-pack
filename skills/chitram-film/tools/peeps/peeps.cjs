/* Open Peeps character generator (CC0, Pablo Stanley — github.com/opeepsfun/open-peeps).
   Renders busts (the library's Effigy) and FULL-BODY standing figures (composed here), including a
   back view, from a JSON spec → SVG files. Rasterise with rasterize.mjs, then tools/dotify.py.

   one-time setup (inside tools/peeps):  node setup.cjs
   usage:  node tools/peeps/peeps.cjs spec.json out_dir

   spec.json = { "name": { kind, body, head, face, beard, acc, skin, top, pants, shoes, back } , ... }
     kind : "bust" (bodies: Computer Explaining PointingUp Paper Coffee Gaming TeeArmsCrossed Hoodie
                    PoloSweater ButtonShirt Turtleneck BlazerBlackTee … see cjs/body/effigy)
            "stand" (bodies: WalkingColorTee WalkingColorPants RestingColorPants EasingColorPants
                    Dancer (arm out — use as a jump) PointingFingerColorPants CrossArmColorPants
                    ShirtColorPants BlazerColorTee Polkadots …; *ColorTee colours the tee via `top`)
     head : Pomp (quiff) ShortOne..ShortFive MediumBangs Bun LongHair Afro Hijab Turban …
     face : Smile BigSmile Calm Driven Explaining Serious Awe Cute Tired Concerned Solemn …
     beard: FullMedium Goatee MustacheThin …   acc: Sunglasses Glasses …
     back : true → back-of-head view (head filled with hair colour, no face) — the "back shot".
   Matching a real person: pick head/beard/accessory/skin that echo their photo (quiff + beard +
   black sunglasses worked); keep ONE outfit colour across all their poses. */
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const fs = require("fs"), path = require("path");
const C = path.join(__dirname, "cjs");
const r = (p, o) => React.createElement(require(path.join(C, p + ".js")).default, o);
const INK = "#1B1B1B";

function bust(s) {
  const { Effigy } = require(path.join(C, "Effigy.js"));
  const skin = s.skin || "#F2B48C";
  return renderToStaticMarkup(React.createElement(Effigy, {
    body: { type: s.body || "Computer", options: { outlineColor: INK, skinColor: skin, topColor: s.top || "#34C263", computerColor: s.device || "#F26B1D" } },
    head: { type: s.head || "Pomp", options: { outlineColor: INK, skinColor: s.back ? INK : skin, hairColor: INK } },
    face: { type: s.face || "Smile", options: { outlineColor: INK } },
    ...(s.beard ? { beard: { type: s.beard, options: { outlineColor: INK } } } : {}),
    ...(s.acc ? { accessory: { type: s.acc, options: { outlineColor: INK } } } : {}),
  }));
}

function stand(s) {
  const skin = s.skin || "#F2B48C";
  const o = { outlineColor: INK, skinColor: skin, topColor: s.top || "#34C263", pantsColor: s.pants || "#2B2B2B", shoesColor: s.shoes || "#F26B1D" };
  const back = !!s.back;
  // head sits on the standing body at this offset (measured; same part offsets as Effigy)
  const H = React.createElement("g", { transform: `translate(${s.dx ?? 290} ${s.dy ?? -40})` },
    React.createElement("g", { transform: "translate(342,190)" }, r("head/" + (s.head || "Pomp"), { outlineColor: INK, skinColor: back ? INK : skin, hairColor: INK })),
    !back && React.createElement("g", { transform: "translate(531,366)" }, r("face/" + (s.face || "Smile"), { outlineColor: INK })),
    !back && s.beard && React.createElement("g", { transform: "translate(495,498) scale(0.98 1)" }, r("beard/" + s.beard, { outlineColor: INK })),
    !back && s.acc && React.createElement("g", { transform: "translate(419,421)" }, r("accessory/" + s.acc, { outlineColor: INK })));
  return renderToStaticMarkup(React.createElement("svg", { xmlns: "http://www.w3.org/2000/svg", viewBox: "0 100 1950 3200", width: 975, height: 1600, overflow: "visible" },
    React.createElement("g", { transform: "translate(147,639)" }, r("body/standing/" + (s.body || "WalkingColorTee"), o)), H));
}

const spec = JSON.parse(fs.readFileSync(process.argv[2], "utf8")), out = process.argv[3] || "peeps_svg";
fs.mkdirSync(out, { recursive: true });
for (const [n, s] of Object.entries(spec)) {
  fs.writeFileSync(path.join(out, n + ".svg"), (s.kind === "stand" ? stand : bust)(s));
  console.log("svg", n);
}
