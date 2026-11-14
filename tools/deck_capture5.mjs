// Flood app panels for the story slide: the app's own rain panel and radar time-lapse timeline.
import { chromium } from '/node_modules/playwright-core/index.mjs';
const base = process.argv[2] || 'https://nasa-spaceapps-2026.pages.dev';
const out = new URL('../submission/assets/shots/', import.meta.url).pathname;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
await p.goto(base + '/sar-change/app/', { waitUntil: 'networkidle' }); await p.waitForTimeout(4000);
await p.locator('#rainSec').scrollIntoViewIfNeeded(); await p.waitForTimeout(2500);
await p.locator('#rainSec').screenshot({ path: out + 'flood-rain-panel.png' }); console.log('rain');
await p.click('#tab-viewer'); await p.waitForTimeout(2000);
await p.selectOption('#mode', 'timelapse'); await p.waitForTimeout(2500);
const mx = await p.$eval('#tlRange', (r) => +r.max);
const idx = await p.evaluate(() => { const t = [...document.querySelectorAll('#tlTicks *')].map((e) => e.textContent); return t; }); console.log('ticks', idx);
const want = +(process.argv[3] ?? -1);
if (want >= 0) await p.$eval('#tlRange', (r, v) => { r.value = v; r.dispatchEvent(new Event('input', { bubbles: true })); r.dispatchEvent(new Event('change', { bubbles: true })); }, want);
await p.waitForTimeout(3000);
const tl = p.locator('#tlBox');
if (await tl.count()) { await tl.scrollIntoViewIfNeeded(); await p.waitForTimeout(2500); await tl.screenshot({ path: out + 'flood-timelapse' + (want >= 0 ? '-' + want : '') + '.png' }); console.log('tl'); }
await b.close();
