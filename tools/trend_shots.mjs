import pkg from '/node_modules/playwright-core/index.mjs';
const { chromium } = pkg.chromium ? pkg : { chromium: pkg };
const base = process.argv[2] || 'http://127.0.0.1:8899', out = process.argv[3] || '/workspace/spaceapps-site/shots/trends';
import fs from 'fs'; fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
for (const [vn, vp] of Object.entries({ desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 2 } })) {
  const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, hasTouch: !!vp.hasTouch, deviceScaleFactor: vp.deviceScaleFactor || 1 });
  for (const path of ['/', '/hotspots/', '/sar-change/', '/field-shift/']) {
    const p = await ctx.newPage(); const errs = [];
    p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto(base + path, { waitUntil: 'networkidle' });
    const sel = path === '/' ? '#trends' : '#trend';
    await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(1800);
    const name = path === '/' ? 'home' : path.replaceAll('/', '');
    if (path === '/hotspots/') { await p.locator('.pmap .prov').nth(0).click(); await p.locator('.seg button[data-v="modis_count"]').click(); }
    if (path === '/sar-change/') { await p.locator('.seg button[data-v="ontario"]').click(); }
    if (path === '/field-shift/') { await p.selectOption('.sel select', 'gdd_may_sep'); }
    await p.waitForTimeout(600);
    const tgt = path === '/' ? p.locator('#trends .case-grid') : p.locator('.tw');
    await tgt.screenshot({ path: `${out}/${name}-${vn}.png` });
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    const v = path === '/' ? await p.locator('[data-spark] svg').count() : await p.locator('.verdict .q').count();
    console.log(vn, path, 'errors', errs.length, errs.slice(0, 2), 'overflowX', ov, 'items', v);
    await p.close();
  }
}
await b.close();
