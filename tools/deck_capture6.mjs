// Polish captures: Field Shift drone/scout tasking zoomed out (whole map, no cut labels) and the flood app's What if? panel.
// Usage: node tools/deck_capture6.mjs [base]
import { chromium } from '/node_modules/playwright-core/index.mjs';
import { LEAFLET_HOOK } from './view_helpers.mjs';
const base = process.argv[2] || 'https://nasa-spaceapps-2026.pages.dev';
const out = new URL('../submission/assets/shots/', import.meta.url).pathname;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
let p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 });
await p.addInitScript(LEAFLET_HOOK);
await p.goto(`${base}/field-shift/app/#act=field-shift-4`, { waitUntil: 'networkidle' }); await p.waitForTimeout(5500);
await p.locator('.c2-card[data-id=field-shift-4] .c2-go').first().click(); await p.waitForTimeout(1800);
const z = await p.evaluate(() => { const m = (window.__maps || []).filter((m) => m._container && m._container.offsetParent); m.forEach((x) => x.setZoom(x.getZoom() - 1, { animate: false })); return m.map((x) => x.getZoom()); });
console.log('zoom', z); await p.waitForTimeout(1500);
await p.evaluate(() => scrollTo(0, 0)); await p.locator('#map').first().screenshot({ path: `${out}field-map-wide.png` }); console.log('field-map-wide');
await p.close();
p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
await p.goto(`${base}/sar-change/app/`, { waitUntil: 'networkidle' }); await p.waitForTimeout(3500);
const ok = await p.evaluate(() => { const e = document.querySelector('.wi-in'); if (!e) return false; e.setAttribute('data-wi', '1'); return true; });
if (ok) { const el = p.locator('[data-wi]').first(); await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(1200); await el.screenshot({ path: `${out}whatif-flood.png` }); console.log('whatif-flood', await el.evaluate((e) => (e.innerText.match(/\b\d{1,2}:\d{2}\b[^\n]{0,12}/g) || []).slice(0, 20))); }
await b.close();
