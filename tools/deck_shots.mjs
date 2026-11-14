import pkg from '/node_modules/playwright-core/index.mjs';
const { chromium } = pkg.chromium ? pkg : { chromium: pkg };
const base = 'http://127.0.0.1:8899', out = '/workspace/spaceapps-site/submission/build';
import fs from 'fs'; fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
for (const s of ['hotspots', 'sar-change', 'field-shift']) {
  const p = await ctx.newPage(); await p.goto(`${base}/${s}/`, { waitUntil: 'networkidle' });
  await p.locator('#trend').scrollIntoViewIfNeeded(); await p.waitForTimeout(1500);
  await p.locator('.tw').screenshot({ path: `${out}/trend-${s}.png` });
  await p.close();
}
await b.close();
