// SVG → transparent PNG (cropped to content) with the skill's Chromium.
//   node tools/peeps/rasterize.mjs <svg_dir> <png_dir> [height=1200]
import { chromium } from "playwright-core";
import fs from "node:fs"; import path from "node:path";
const [src, dst, h = "1200"] = process.argv.slice(2);
fs.mkdirSync(dst, { recursive: true });
const b = await chromium.launch(); const p = await b.newPage();
for (const f of fs.readdirSync(src).filter((f) => f.endsWith(".svg"))) {
  let svg = fs.readFileSync(path.join(src, f), "utf8");
  svg = svg.replace(/(<svg[^>]*?)\s(width|height)=(['"])[^'"]*\3/g, "$1").replace(/(<svg[^>]*?)\s(width|height)=(['"])[^'"]*\3/g, "$1").replace("<svg", `<svg height="${h}"`);
  await p.setContent(`<html><body style="margin:0;background:transparent"><div id="w" style="display:inline-block">${svg}</div></body></html>`);
  const out = path.join(dst, f.replace(".svg", ".png"));
  await p.locator("#w svg").screenshot({ path: out, omitBackground: true });
  console.log("png", out);
}
await b.close();
