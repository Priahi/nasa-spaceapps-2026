// Navigate the deck 1 -> 7 with its own next control (default Chrome autoplay policy, no flags).
// Slide 3: the official demo must start by itself (muted) from ~0 and advance; it must pause once slide 4 is active.
// Loop slides: sample currentTime for (duration + 2.5 s) and prove it advances and wraps.
// Usage: node tools/deck_loop_check.mjs <deck url>
import { chromium } from '/node_modules/playwright-core/index.mjs';
const url = process.argv[2];
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto(url, { waitUntil: 'networkidle' }); await p.waitForTimeout(1200);
const out = []; const demo = () => p.evaluate(() => { const v = document.getElementById('demoVid'); return v ? { t: +v.currentTime.toFixed(2), paused: v.paused, muted: v.muted, rs: v.readyState, controls: v.controls } : null; });
for (let i = 1; i <= 7; i++) {
  if (i > 1) { await p.click('#deckNext'); }
  if (i === 3) { const s = []; const t0 = Date.now(); while (Date.now() - t0 < 4000) { s.push(await demo()); await p.waitForTimeout(250); }
    const ts = s.map((x) => x.t); let adv = 0; for (let j = 1; j < ts.length; j++) if (ts[j] > ts[j - 1]) adv++;
    out.push({ slide: 3, demo: 'demo.mp4', firstT: ts[0], tAfter4s: ts.at(-1), advancingSamples: adv + '/' + (ts.length - 1), paused: s.at(-1).paused, muted: s.at(-1).muted, readyState: s.at(-1).rs, controls: s.at(-1).controls, unmuteButton: await p.isVisible('#demoUnmute') }); }
  await p.waitForTimeout(600);
  if (i === 4) { const d = await demo(); out.push({ slide: 4, demoPausedAfterLeaving3: d.paused, demoT: d.t }); }
  const info = await p.evaluate((i) => { const s = document.querySelectorAll('section.s')[i - 1]; return [...s.querySelectorAll('video.lp')].map((v) => ({ src: (v.currentSrc || '').split('/').pop(), dur: +v.duration.toFixed(2), loop: v.loop, muted: v.muted, inline: v.playsInline, preload: v.preload })); }, i);
  if (!info.length) { if (i !== 3 && i !== 4) out.push({ slide: i, loops: 0, num: await p.textContent('#deckNum') }); continue; }
  const samples = []; const t0 = Date.now(); const span = Math.max(10, Math.max(...info.map((v) => v.dur || 0)) + 2.5) * 1000;
  while (Date.now() - t0 < span) { samples.push(await p.evaluate((i) => [...document.querySelectorAll('section.s')[i - 1].querySelectorAll('video.lp')].map((v) => [v.currentTime, v.readyState, v.paused]), i)); await p.waitForTimeout(250); }
  info.forEach((v, k) => { const ts = samples.map((s) => s[k][0]); let wraps = 0, adv = 0; for (let j = 1; j < ts.length; j++) { if (ts[j] < ts[j - 1] - 0.5) wraps++; else if (ts[j] > ts[j - 1]) adv++; }
    out.push({ slide: i, ...v, readyState: samples.at(-1)[k][1], paused: samples.at(-1)[k][2], firstT: +ts[0].toFixed(2), maxT: +Math.max(...ts).toFixed(2), advancingSamples: adv + '/' + (ts.length - 1), wraps }); });
}
console.log(JSON.stringify(out, null, 0).replace(/\},\{/g, '},\n{'));
await b.close();
