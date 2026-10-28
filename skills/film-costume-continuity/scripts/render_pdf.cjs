#!/usr/bin/env node
// Render an already-built local costume book without remote network access.
const fs = require('fs');
const path = require('path');
const { pathToFileURL, fileURLToPath } = require('url');

async function main() {
  const argv = process.argv.slice(2);
  if (!argv[0]) throw new Error('Usage: render_pdf.cjs book.html [--out book.pdf] [--browser executable] [--preview page.png]');
  const input = fs.realpathSync(argv[0]);
  let output = input.replace(/\.html?$/i, '') + '.pdf';
  let browserPath;
  let preview;
  for (let i = 1; i < argv.length; i += 2) {
    if (!argv[i + 1]) throw new Error(`Missing value for ${argv[i]}`);
    if (argv[i] === '--out') output = argv[i + 1];
    else if (argv[i] === '--browser') browserPath = argv[i + 1];
    else if (argv[i] === '--preview') preview = argv[i + 1];
    else throw new Error(`Unknown option: ${argv[i]}`);
  }
  output = path.resolve(output);
  if (output === input) throw new Error('PDF destination cannot replace the HTML source');
  let chromium;
  try { ({ chromium } = require('playwright')); }
  catch { throw new Error('Playwright unavailable. Use the discovered workspace Node packages via NODE_PATH.'); }
  if (!browserPath && !fs.existsSync(chromium.executablePath())) {
    throw new Error('The matching Playwright browser is unavailable. Locate an installed Chromium and pass --browser <absolute-executable>.');
  }
  const browser = await chromium.launch({ headless: true, ...(browserPath ? { executablePath: browserPath } : {}) });
  try {
    const page = await browser.newPage({ javaScriptEnabled: false, viewport: { width: 1000, height: 1350 } });
    const root = path.dirname(input);
    await page.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.protocol === 'data:') return route.continue();
      if (url.protocol === 'file:') {
        let resource;
        try { resource = fs.realpathSync(fileURLToPath(url)); } catch { return route.abort(); }
        const relative = path.relative(root, resource);
        if (!relative.startsWith('..' + path.sep) && relative !== '..' && !path.isAbsolute(relative)) return route.continue();
      }
      return route.abort();
    });
    await page.goto(pathToFileURL(input).href, { waitUntil: 'load' });
    await page.evaluate(async () => { await document.fonts.ready; });
    const broken = await page.locator('img').evaluateAll(images => images.filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src')));
    if (broken.length) throw new Error(`Broken images: ${broken.join(', ')}`);
    await page.emulateMedia({ media: 'print' });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 2);
    if (overflow) throw new Error('Book overflows horizontally; fix the content or CSS before PDF export');
    fs.mkdirSync(path.dirname(output), { recursive: true });
    await page.pdf({ path: output, format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="font-size:8px;color:#697578;width:100%;text-align:center">Costume &amp; Continuity · <span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
    if (preview) await page.screenshot({ path: path.resolve(preview), fullPage: false });
    console.log(JSON.stringify({ pdf: output, imageInstances: await page.locator('img').count() }));
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
