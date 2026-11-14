// Tasking captures for the story deck: map with asset markers mid-run and done, task queue mid-run and done, alert draft, timeline after Send (simulated).
// Usage: node tools/deck_capture3.mjs [base] [app,app]
import { chromium } from '/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const base = process.argv[2] || 'https://nasa-spaceapps-2026.pages.dev', only = process.argv[3] ? process.argv[3].split(',') : null;
const out = new URL('../submission/assets/shots/', import.meta.url).pathname; fs.mkdirSync(out, { recursive: true });
const APPS = [
  { key: 'flood', url: '/sar-change/app/', id: 'sar-change-1', map: '#opsMap', extra: [['flood-rain', '.ops-rain']] },
  { key: 'fire', url: '/hotspots/app/', id: 'hotspots-1', map: '#map' },
  { key: 'notice', url: '/hotspots/app/', id: 'hotspots-2', map: '#map' },
  { key: 'field', url: '/field-shift/app/', id: 'field-shift-4', map: '#map' },
];
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const errs = [];
// union box of the asset markers (+ pad), clamped to the map element, in page coords
async function focal(p, mapSel, pad) {
  return p.evaluate(([m, pad]) => {
    const M = document.querySelector(m).getBoundingClientRect(); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9, n = 0;
    document.querySelectorAll(`${m} .og-asset, ${m} [class*=asset-]`).forEach((e) => { const r = e.getBoundingClientRect(); if (!r.width || r.width > M.width * .8) return; n++; x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom); });
    if (!n) return { x: M.left + scrollX, y: M.top + scrollY, width: M.width, height: M.height, n };
    x0 = Math.max(M.left, x0 - pad); y0 = Math.max(M.top, y0 - pad); x1 = Math.min(M.right, x1 + pad); y1 = Math.min(M.bottom, y1 + pad);
    // at least 65% of the map width, so the context stays readable
    const minW = M.width * .65; if (x1 - x0 < minW) { const add = (minW - (x1 - x0)) / 2; x0 = Math.max(M.left, x0 - add); x1 = Math.min(M.right, x0 + minW); }
    // keep at least 16:10-ish
    const w = x1 - x0, h = y1 - y0, want = 1.5;
    if (w / h < want) { const add = (h * want - w) / 2; x0 = Math.max(M.left, x0 - add); x1 = Math.min(M.right, x1 + add); }
    else { const add = (w / want - h) / 2; y0 = Math.max(M.top, y0 - add); y1 = Math.min(M.bottom, y1 + add); }
    return { x: x0 + scrollX, y: y0 + scrollY, width: x1 - x0, height: y1 - y0, n };
  }, [mapSel, pad]);
}
const shotEl = async (p, sel, name) => { const el = p.locator(sel).first(); if (!(await el.count()) || !(await el.isVisible())) { errs.push(name + ' missing ' + sel); return; } await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(250); await el.screenshot({ path: `${out}${name}.png` }); console.log(name); };
const shotMap = async (p, a, name) => { await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(200); const c = await focal(p, a.map, 90); await p.screenshot({ path: `${out}${name}.png`, clip: c, fullPage: true }); console.log(name, Math.round(c.width), Math.round(c.height), 'markers', c.n); };
for (const a of APPS) {
  if (only && !only.includes(a.key)) continue;
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 }); p.on('pageerror', (e) => errs.push(a.key + ': ' + e.message));
  await p.goto(`${base}${a.url}#act=${a.id}`, { waitUntil: 'networkidle' }); await p.waitForTimeout(5500);
  for (const [n, s] of a.extra || []) await shotEl(p, s, n);
  const card = `.c2-card[data-id=${a.id}]`;
  await p.locator(`${card} .c2-go`).first().click().catch(() => errs.push(a.key + ' go')); await p.waitForTimeout(2300);
  // mid-run: map + queue as close together as possible
  await shotMap(p, a, `${a.key}-map-run`); await shotEl(p, '.c2-q', `${a.key}-queue-run`);
  await p.waitForTimeout(5000);
  await shotMap(p, a, `${a.key}-map-done`);
  await p.locator(`${card} .c2-alrt`).first().click().catch(() => errs.push(a.key + ' alrt')); await p.waitForTimeout(1200);
  await shotEl(p, '.c2-al', `${a.key}-alert`);
  await p.locator('.c2-send').first().click().catch(() => errs.push(a.key + ' send')); await p.waitForTimeout(1500);
  await shotEl(p, '.c2-tl', `${a.key}-timeline`); await shotEl(p, '.c2-q', `${a.key}-queue-done`);
  await p.evaluate(() => scrollTo(0, 0)); await p.screenshot({ path: `${out}${a.key}-screen.png` }); console.log(a.key + '-screen');
  await p.close();
}
console.log('errors', errs); await b.close();
