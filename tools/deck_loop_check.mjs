// Navigate the deck 1 -> 7 with its own next control; on slides with loops, sample currentTime and prove it advances and wraps.
// Usage: node tools/deck_loop_check.mjs <deck url>
import { chromium } from '/node_modules/playwright-core/index.mjs';
const url = process.argv[2];
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(url, { waitUntil: 'networkidle' }); await p.waitForTimeout(1200);
const out = [];
for (let i = 1; i <= 7; i++) {
  if (i > 1) { await p.click('#deckNext'); }
  await p.waitForTimeout(600);
  const info = await p.evaluate((i) => { const s = document.querySelectorAll('section.s')[i - 1]; return [...s.querySelectorAll('video.lp')].map((v) => ({ src: (v.currentSrc || '').split('/').pop(), dur: +v.duration.toFixed(2), loop: v.loop, muted: v.muted, inline: v.playsInline, preload: v.preload })); }, i);
  if (!info.length) { out.push({ slide: i, loops: 0, num: await p.textContent('#deckNum') }); continue; }
  const samples = []; const t0 = Date.now();
  while (Date.now() - t0 < 10000) { samples.push(await p.evaluate((i) => [...document.querySelectorAll('section.s')[i - 1].querySelectorAll('video.lp')].map((v) => [v.currentTime, v.readyState, v.paused]), i)); await p.waitForTimeout(250); }
  info.forEach((v, k) => { const ts = samples.map((s) => s[k][0]); let wraps = 0, adv = 0; for (let j = 1; j < ts.length; j++) { if (ts[j] < ts[j - 1] - 0.5) wraps++; else if (ts[j] > ts[j - 1]) adv++; }
    out.push({ slide: i, num: null, ...v, readyState: samples.at(-1)[k][1], paused: samples.at(-1)[k][2], firstT: +ts[0].toFixed(2), maxT: +Math.max(...ts).toFixed(2), advancingSamples: adv + '/' + (ts.length - 1), wraps }); });
}
console.log(JSON.stringify(out, null, 0).replace(/\},\{/g, '},\n{'));
await b.close();
