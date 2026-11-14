// Deck captures from the live dashboards' #demo states (simulation running on real data). Usage: node tools/deck_capture2.mjs [base] [names,comma]
import { chromium } from '/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const base = process.argv[2] || 'https://nasa-spaceapps-2026.pages.dev', only = process.argv[3] ? process.argv[3].split(',') : null;
const out = new URL('../submission/assets/shots/', import.meta.url).pathname; fs.mkdirSync(out, { recursive: true });
const SHOTS = [
  // fire
  { n: 'fire-map', u: '/hotspots/app/#demo', el: '#map' },
  { n: 'fire-alert', u: '/hotspots/app/#demo', el: '.c2-al' },
  { n: 'fire-notice-map', u: '/hotspots/app/#demo=hotspots-2', el: '#map' },
  { n: 'fire-notice-alert', u: '/hotspots/app/#demo=hotspots-2', el: '.c2-al' },
  { n: 'fire-calendar', u: '/hotspots/app/', el: '#calendar' },
  { n: 'fire-screen', u: '/hotspots/app/#demo', el: null },
  // field
  { n: 'field-map', u: '/field-shift/app/#demo=field-shift-2', el: '#map' },
  { n: 'field-scout-map', u: '/field-shift/app/#demo', el: '#map' },
  { n: 'field-screen', u: '/field-shift/app/#demo', el: null },
  { n: 'field-farmer', u: '/field-shift/app/', pre: '.fs-mode button', el: null },
  // flood (wait for the new flood deploy)
  { n: 'flood-map', u: '/sar-change/app/#demo', el: '#opsMap' },
  { n: 'flood-alert', u: '/sar-change/app/#demo', el: '.c2-al' },
  { n: 'flood-rain', u: '/sar-change/app/', el: '.ops-rain' },
  { n: 'flood-screen', u: '/sar-change/app/#demo', el: null },
];
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const errs = [];
for (const s of SHOTS) {
  if (only && !only.some((o) => s.n.startsWith(o))) continue;
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 }); p.on('pageerror', (e) => errs.push(s.n + ': ' + e.message));
  await p.goto(base + s.u, { waitUntil: 'networkidle' }); await p.waitForTimeout(7000);
  if (s.pre) { await p.locator(s.pre).first().click().catch(() => errs.push(s.n + ' pre')); await p.waitForTimeout(1500); }
  if (!s.el) { await p.screenshot({ path: `${out}${s.n}.png` }); console.log(s.n, 'viewport'); }
  else { const el = p.locator(s.el).first(); if (!(await el.count())) { errs.push(s.n + ' missing ' + s.el); await p.close(); continue; }
    await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(500); await el.screenshot({ path: `${out}${s.n}.png` }); const bb = await el.boundingBox(); console.log(s.n, Math.round(bb.width), Math.round(bb.height)); }
  await p.close();
}
console.log('errors', errs); await b.close();
