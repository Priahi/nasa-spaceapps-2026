// Fixed map stills for slides 5-6: the Canada burn-history layer (Hot Spots) and the crop classification map (Field Shift), 2x.
import { chromium } from 'playwright-core';
const base = process.argv[2] || 'https://spaceapps.parsariahi.com', D = new URL('../submission/assets/shots/', import.meta.url).pathname;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const ctx = await b.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2, colorScheme: 'dark' });
const p = await ctx.newPage();
await p.goto(base + '/hotspots/app/', { waitUntil: 'networkidle' }); await p.waitForTimeout(4000);
await p.selectOption('#preset', 'canada-boreal'); await p.waitForTimeout(3500); await p.mouse.move(1500, 880);
const mb = await p.locator('.leaflet-container').first().boundingBox(); console.log('hs map', mb);
await p.screenshot({ path: D + 'map8-fire-raw.png', clip: mb });
await p.goto(base + '/field-shift/app/', { waitUntil: 'networkidle' }); await p.waitForTimeout(5000);
console.log(await p.evaluate(() => [...document.querySelectorAll('.og-stage button, .og-layers button, [data-layer]')].map(e => (e.dataset.layer || '') + ':' + e.innerText.trim().slice(0, 25)).join(' | ')));
await p.mouse.move(1500, 880);
const fb = await p.locator('.leaflet-container, .maplibregl-map, canvas').first().boundingBox(); console.log('fs map', fb);
await p.screenshot({ path: D + 'map8-field-raw.png', clip: fb });
await p.locator('[data-layer=forecast]').first().click(); await p.waitForTimeout(3500); await p.mouse.move(1500, 880);
await p.screenshot({ path: D + 'map8-field-fc-raw.png', clip: fb });
console.log(await p.evaluate(() => document.querySelector('.og-legend, .leaflet-bottom.leaflet-left')?.innerText || ''));
await b.close();
