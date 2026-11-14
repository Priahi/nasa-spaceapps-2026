import { chromium } from '/node_modules/playwright-core/index.mjs';
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto('file:///workspace/spaceapps-site/submission/deck.html', { waitUntil: 'networkidle' });
console.log(JSON.stringify(await p.evaluate(() => [...document.querySelectorAll('video')].map((v) => { const s = v.closest('section'), r = v.getBoundingClientRect(), q = s.getBoundingClientRect(); return { slide: [...document.querySelectorAll('section')].indexOf(s) + 1, src: v.querySelector('source[type="video/mp4"]').getAttribute('src'), poster: v.getAttribute('poster'), x: r.left - q.left, y: r.top - q.top, w: r.width, h: r.height }; }))));
await b.close();
