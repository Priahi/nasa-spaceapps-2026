// Headless verification: status, console errors, failed requests; desktop + mobile full-page screenshots; demo interaction checks.
import pkg from '/node_modules/playwright-core/index.mjs';
const { chromium } = pkg.chromium ? pkg : { chromium: pkg };
import fs from 'fs';
const base = process.argv[2] || 'http://127.0.0.1:8899';
const out = process.argv[3] || '/workspace/spaceapps-site/shots';
const tag = process.argv[4] || 'local';
fs.mkdirSync(out, { recursive: true });
const paths = ['/', '/hotspots/', '/sar-change/', '/field-shift/', '/hotspots/app/', '/sar-change/app/', '/field-shift/app/'];
const vps = { desktop: { width: 1440, height: 900, isMobile: false }, mobile: { width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } };
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const report = [];
for (const [vn, vp] of Object.entries(vps)) {
  const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: vp.isMobile, hasTouch: !!vp.hasTouch, deviceScaleFactor: vp.deviceScaleFactor || 1 });
  for (const path of paths) {
    const p = await ctx.newPage();
    const errs = [], bad = [];
    p.on('pageerror', e => errs.push('pageerror: ' + e.message));
    p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
    p.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });
    p.on('requestfailed', r => { if (!/favicon/.test(r.url())) bad.push('failed ' + r.url() + ' ' + (r.failure()?.errorText || '')); });
    const resp = await p.goto(base + path, { waitUntil: 'networkidle', timeout: 120000 });
    await p.waitForTimeout(2500);
    // scroll through to trigger reveals/count-ups and lazy iframes
    if (!path.includes('/app/')) {
      const h = await p.evaluate(() => document.body.scrollHeight);
      for (let y = 0; y < h; y += Math.round(vp.height * 0.7)) { await p.evaluate(yy => window.scrollTo(0, yy), y); await p.waitForTimeout(220); }
      await p.waitForTimeout(1500); await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(600);
    }
    const name = (path === '/' ? 'home' : path.replace(/^\/|\/$/g, '').replace(/\//g, '_'));
    const checks = {};
    if (path === '/hotspots/app/') {
      checks.status = await p.textContent('#status');
      const opts = await p.$$eval('#preset option', os => os.map(o => o.value));
      await p.selectOption('#preset', opts.find(v => /alberta/i.test(v)) || opts[3]); await p.waitForTimeout(2500);
      checks.afterPreset = await p.textContent('#status');
      checks.calendarCells = await p.$$eval('#calendar *', n => n.length);
    }
    if (path === '/sar-change/app/') {
      await p.click('[data-tab="metrics"]'); await p.waitForTimeout(800);
      checks.metricsVisible = await p.isVisible('#panel-metrics');
      await p.click('[data-tab="viewer"]'); await p.waitForTimeout(500);
      checks.imgs = await p.$$eval('#panel-viewer img, #panel-viewer canvas', n => n.length);
    }
    if (path === '/field-shift/app/') {
      const s = await p.$('#sliders input[type=range]');
      if (s) { await s.evaluate(el => { el.value = 95; el.dispatchEvent(new Event('input', { bubbles: true })); }); await p.waitForTimeout(600); }
      checks.strategyCards = await p.$$eval('#strategyCards > *', n => n.length);
      checks.firstCard = (await p.textContent('#strategyCards')).slice(0, 80);
    }
    if (path === '/sar-change/') {
      const r = await p.$('.ba input'); if (r) { await r.evaluate(el => { el.value = 20; el.dispatchEvent(new Event('input')); }); checks.baX = await p.$eval('.ba', el => el.style.getPropertyValue('--x')); }
    }
    if (!path.includes('/app/') && path !== '/') {
      const fr = p.frames().find(f => f.url().includes('/app/')); checks.iframeLoaded = !!fr && (await fr.title()).length > 0;
    }
    const overflow = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    await p.screenshot({ path: `${out}/${tag}_${vn}_${name}.png`, fullPage: !path.includes('/app/') });
    report.push({ viewport: vn, path, status: resp.status(), errors: errs, badRequests: bad, horizontalOverflow: overflow, checks });
    await p.close();
  }
  await ctx.close();
}
await b.close();
fs.writeFileSync(`${out}/${tag}_report.json`, JSON.stringify(report, null, 1));
for (const r of report) console.log(r.viewport.padEnd(8), String(r.status), r.path.padEnd(20), 'errs', r.errors.length, 'bad', r.badRequests.length, r.horizontalOverflow ? 'OVERFLOW' : '', JSON.stringify(r.checks).slice(0, 160), r.errors.concat(r.badRequests).slice(0, 3).join(' | ').slice(0, 300));
