// Slide 1 + slide 3 flood frames from ONE live session (same map extent): plain radar map, What changed classification, dispatch markers,
// plus the town ranking and the approved action card. Usage: node tools/deck_capture7.mjs [base]
import { chromium } from 'playwright-core';
import fs from 'fs';
const base = process.argv[2] || 'https://spaceapps.parsariahi.com';
const out = new URL('../submission/assets/shots/', import.meta.url).pathname;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 3 });
await p.goto(`${base}/sar-change/app/#act=sar-change-1`, { waitUntil: 'networkidle' }); await p.waitForTimeout(5500);
await p.locator('.c2-card[data-id=sar-change-1] .c2-go').first().click(); await p.waitForTimeout(7500);
const top = async () => { await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(400); };
await top();
// the slide-1 frame: right 64.7% x bottom 73.8% of the radar map (the 8 towns, coast to Cullera)
const F = await p.evaluate(() => { const M = document.querySelector('#opsMap').getBoundingClientRect();
  return { x: M.left + .353 * M.width + scrollX, y: M.top + .262 * M.height + scrollY, width: M.width * .647, height: M.height * .738 }; });
console.log('focal', F);
const hide = (on) => p.evaluate((on) => { let s = document.getElementById('_hideA'); if (!s) { s = document.createElement('style'); s.id = '_hideA'; document.head.appendChild(s); } s.textContent = on ? '#opsMap .ops-assets{visibility:hidden!important}' : ''; }, on);
const shot = async (name) => { await top(); await p.screenshot({ path: `${out}${name}.png`, clip: F, fullPage: true }); console.log(name); };
await shot('flood7-map-act');
await hide(true); await shot('flood7-map-plain');
await p.locator('.ops-toolbar button', { hasText: 'What changed' }).first().click(); await p.waitForTimeout(2500);
await shot('flood7-map-change');
// card with the approved action (chips) — switch the dock back to Actions
await p.locator('.og-dock button, .og-dock [role=tab]', { hasText: 'What changed' }).first().click(); await p.waitForTimeout(1500);
await p.locator('#opsRank').first().scrollIntoViewIfNeeded(); await p.waitForTimeout(500);
const rk = await p.evaluate(() => {
  const r = (e) => e.getBoundingClientRect(); const h3 = document.querySelector('#pane-change h3.og-h'), ol = document.querySelector('#opsRank'), li = ol.querySelectorAll('li')[4];
  const wc = document.querySelector('#whatChanged'), sp = document.querySelector('#pane-change .ops-split');
  const L = Math.min(r(h3).left, r(ol).left) - 10, R = r(ol).right + 10;
  return { rank: { x: L, y: r(h3).top - 10, width: R - L, height: r(li).bottom - r(h3).top + 20 },
           head: { x: L, y: r(wc).top - 8, width: R - L, height: r(sp).bottom - r(wc).top + 16 } };
});
for (const [k, c] of Object.entries(rk)) { await p.screenshot({ path: `${out}flood7-${k}.png`, clip: c }); console.log('flood7-' + k, c); }
await p.locator('.og-dock button, .og-dock [role=tab]', { hasText: 'Actions' }).first().click(); await p.waitForTimeout(1200);
const card = p.locator('.c2-card[data-id=sar-change-1]').first(); await card.scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
await card.screenshot({ path: `${out}flood7-card.png` }); console.log('flood7-card');
await b.close();
