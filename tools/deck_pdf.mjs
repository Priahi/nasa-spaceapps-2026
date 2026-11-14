// Renders submission/deck.html -> submission/deck.pdf (links kept, posters in print) + submission/build/slide-N.png
import { chromium } from '/node_modules/playwright-core/index.mjs';
const dir = '/workspace/spaceapps-site/submission';
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(`file://${dir}/deck.html`, { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
await p.pdf({ path: `${dir}/deck.pdf`, width: '1920px', height: '1080px', printBackground: true });
await p.emulateMedia({ media: 'print' });
const n = await p.locator('section.s').count();
for (let i = 0; i < n; i++) await p.locator('section.s').nth(i).screenshot({ path: `${dir}/build/slide-${i + 1}.png` });
console.log('slides', n); await b.close();
