// Capture fresh screenshots of the three demos (served from dist/) to use as site visuals.
import pkg from '/node_modules/playwright-core/index.mjs';
const { chromium } = pkg.chromium ? pkg : { chromium: pkg };
const base = process.argv[2] || 'http://127.0.0.1:8899';
const out = process.argv[3] || '/tmp/cap';
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const hide = () => p.addStyleTag({ content: '.suite-bar,.bf-launch{display:none!important}' });
// Hot Spots
await p.goto(base + '/hotspots/app/', { waitUntil: 'networkidle' }); await hide(); await p.waitForTimeout(2500);
await p.screenshot({ path: `${out}/hotspots-app.png` });
await p.selectOption('#preset', { label: 'Alberta' }).catch(async () => { const o = await p.$$eval('#preset option', os => os.map(o => o.value + '|' + o.textContent)); console.log(o); });
await p.waitForTimeout(3000);
const cal = await p.$('.calendar-pane'); await cal.screenshot({ path: `${out}/hotspots-calendar.png` });
await p.screenshot({ path: `${out}/hotspots-alberta.png` });
const opts = await p.$$eval('#preset option', os => os.map(o => o.textContent));
const chaco = opts.find(t => /chaco/i.test(t)); if (chaco) { await p.selectOption('#preset', { label: chaco }); await p.waitForTimeout(3000); await (await p.$(".calendar-pane")).screenshot({ path: `${out}/hotspots-argentina.png` }); }
// SAR
await p.goto(base + '/sar-change/app/', { waitUntil: 'networkidle' }); await hide(); await p.waitForTimeout(2500);
await p.screenshot({ path: `${out}/sar-app.png` });
await p.click('[data-tab="metrics"]'); await p.waitForTimeout(1200); await p.screenshot({ path: `${out}/sar-app2.png` });
// Field Shift
await p.goto(base + '/field-shift/app/', { waitUntil: 'networkidle' }); await hide(); await p.waitForTimeout(2500);
await p.screenshot({ path: `${out}/field-app.png` });
await p.evaluate(() => window.scrollTo(0, 650)); await p.waitForTimeout(800); await p.screenshot({ path: `${out}/field-app2.png` });
console.log('presets', opts.join(', '));
await b.close();
