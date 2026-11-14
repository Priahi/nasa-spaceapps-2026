import pkg from '/node_modules/playwright-core/index.mjs';
const { chromium } = pkg.chromium ? pkg : { chromium: pkg };
const d = '/workspace/spaceapps-site/submission/build';
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(`file://${d}/cards.html`, { waitUntil: 'networkidle' }); await p.waitForTimeout(500);
for (const id of ['title', 'end']) await p.locator('#' + id).screenshot({ path: `${d}/card-${id}.png` });
await b.close();
