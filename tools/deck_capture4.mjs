// Full-data map captures for the deck: whole-Canada fire map (Hot Spots, fire activity layer) and the Field Shift crop classification map.
import { chromium } from '/node_modules/playwright-core/index.mjs';
import { LEAFLET_HOOK } from './view_helpers.mjs';
const base = process.argv[2] || 'https://nasa-spaceapps-2026.pages.dev';
const out = new URL('../submission/assets/shots/', import.meta.url).pathname;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const errs = [];
async function shot(url, steps, sel, name, vp = { width: 1600, height: 1000 }) {
  const ctx = await b.newContext({ viewport: vp, deviceScaleFactor: 2 }); await ctx.addInitScript(LEAFLET_HOOK); const p = await ctx.newPage(); p.on('pageerror', (e) => errs.push(name + ' ' + e.message));
  await p.goto(base + url, { waitUntil: 'networkidle' }); await p.waitForTimeout(5000);
  for (const s of steps) { if (s.click) { await p.locator(s.click).first().click().catch(() => errs.push(name + ' click ' + s.click)); } if (s.js) await p.evaluate(s.js); await p.waitForTimeout(s.wait ?? 1500); }
  await p.locator(sel).first().screenshot({ path: `${out}${name}.png` }); console.log(name); await ctx.close();
}
await shot('/hotspots/app/', [{ click: '#mapSec [data-layer=fire]', wait: 1500 }, { js: () => (window.__maps || []).forEach((m) => { m.invalidateSize(); m.options.zoomSnap = 0.1; m.fitBounds([[41, -141], [63, -52]], { animate: false, padding: [0, 0] }); }), wait: 3500 }], '#map', 'fire-canada-full', { width: 1600, height: 1100 });
if (!process.argv[3]) await shot('/field-shift/app/', [{ click: '#layers [data-layer=crops], #layers [data-layer=crop], #layers button', wait: 2500 }], '#map', 'field-crop-map');
if (!process.argv[3]) await shot('/field-shift/app/', [{ click: '#layers [data-layer=forecast]', wait: 2500 }], '#map', 'field-forecast-map');
console.log('errors', errs); await b.close();
