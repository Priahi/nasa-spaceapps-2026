import pkg from '/node_modules/playwright-core/index.mjs';
const { chromium } = pkg.chromium ? pkg : { chromium: pkg };
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const [url, sel, out, w, frac] = process.argv.slice(2);
const p = await (await b.newContext({ viewport: { width: +w || 1440, height: 900 } })).newPage();
await p.goto(url, { waitUntil: 'networkidle' }); await p.waitForTimeout(1200);
await p.evaluate(([s, f]) => { const el = document.querySelector(s); const top = el.getBoundingClientRect().top + scrollY; window.scrollTo(0, top + (el.offsetHeight - innerHeight) * (+f || 0)); }, [sel, frac]);
await p.waitForTimeout(1800); await p.screenshot({ path: out }); await b.close();
