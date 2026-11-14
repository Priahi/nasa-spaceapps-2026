// Records short real-interaction clips of the site at 1920x1080 for the 30 s demo video.
import pkg from '/node_modules/playwright-core/index.mjs';
const { chromium } = pkg.chromium ? pkg : { chromium: pkg };
import fs from 'fs';
const base = process.argv[2] || 'http://127.0.0.1:8899';
const out = '/workspace/spaceapps-site/submission/build/video';
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const meta = {};
const W = 1920, H = 1080;
async function clip(name, url, prep, act) {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 810 }, deviceScaleFactor: 4 / 3 });
  const p = await ctx.newPage();
  await p.goto(base + url, { waitUntil: 'networkidle' });
  if (prep) await prep(p);
  const cdp = await ctx.newCDPSession(p); const frames = [];
  cdp.on('Page.screencastFrame', async (f) => { frames.push({ t: f.metadata.timestamp, d: f.data }); try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch {} });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: W, maxHeight: H, everyNthFrame: 1 });
  await p.waitForTimeout(300);
  const tStart = Date.now() / 1000;
  await act(p);
  const tEnd = Date.now() / 1000;
  await cdp.send('Page.stopScreencast'); await ctx.close();
  const dir = `${out}/${name}`; fs.mkdirSync(dir, { recursive: true });
  let lines = ['ffconcat version 1.0'];
  frames.forEach((f, i) => { fs.writeFileSync(`${dir}/f${String(i).padStart(5, '0')}.jpg`, Buffer.from(f.d, 'base64')); });
  for (let i = 0; i < frames.length; i++) { const dur = i + 1 < frames.length ? frames[i + 1].t - frames[i].t : Math.max(0.05, tEnd - frames[i].t); lines.push(`file f${String(i).padStart(5, '0')}.jpg`, `duration ${dur.toFixed(4)}`); }
  lines.push(`file f${String(frames.length - 1).padStart(5, '0')}.jpg`);
  fs.writeFileSync(`${dir}/list.ffconcat`, lines.join('\n') + '\n');
  meta[name] = { dir, frames: frames.length, first: frames[0]?.t, tStart, tEnd, secs: tEnd - tStart };
  console.log(name, frames.length, 'frames', (tEnd - tStart).toFixed(2), 's', 'lead', (tStart - frames[0].t).toFixed(2));
}
const smooth = async (p, y, ms) => p.evaluate(([y, ms]) => new Promise((r) => { const s = scrollY, t0 = performance.now(); const f = (t) => { const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; scrollTo(0, s + (y - s) * e); k < 1 ? requestAnimationFrame(f) : r(); }; requestAnimationFrame(f); }), [y, ms]);
const top = (p, sel, off = 90) => p.evaluate(([s, o]) => document.querySelector(s).getBoundingClientRect().top + scrollY - o, [sel, off]);

// 1 landing hero -> case files
await clip('landing', '/', async (p) => { await p.waitForTimeout(1800); }, async (p) => {
  await p.waitForTimeout(1300);
  const y = await top(p, '#trends', 40); await smooth(p, y, 1600); await p.waitForTimeout(500);
  const y2 = await top(p, '#trends .case-grid', 96); await smooth(p, y2, 700); await p.waitForTimeout(1300);
});
// 2 fire trend widget
await clip('fire', '/hotspots/', async (p) => { for (let k = 0; k < 3; k++) { const y = await top(p, '#trend .tw', 76); await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(900); } }, async (p) => {
  await p.waitForTimeout(900);
  await p.locator('.pmap path').nth(1).click(); await p.waitForTimeout(1100);  // British Columbia
  await p.locator('.seg button[data-v="modis_count"]').click(); await p.waitForTimeout(1100);
  await p.selectOption('.sel select', 'Canada'); await p.waitForTimeout(1300);
});
// 3 hotspots app
await clip('hotapp', '/hotspots/app/', async (p) => { await p.waitForTimeout(2500); }, async (p) => { await p.waitForTimeout(600); await p.selectOption('select', { index: 1 }); await p.waitForTimeout(2400); });
// 4 SAR before/after slider
await clip('sar', '/sar-change/', async (p) => { for (let k = 0; k < 3; k++) { const y = await top(p, '.ba', 84); await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(900); } }, async (p) => {
  const r = await p.locator('.ba').boundingBox(); const yy = r.y + r.height / 2;
  await p.mouse.move(r.x + r.width * 0.5, yy); await p.mouse.down();
  for (let i = 0; i <= 30; i++) { await p.mouse.move(r.x + r.width * (0.5 - 0.4 * Math.sin(i / 30 * Math.PI)), yy); await p.waitForTimeout(40); }
  for (let i = 0; i <= 20; i++) { await p.mouse.move(r.x + r.width * (0.5 + 0.38 * Math.sin(i / 20 * Math.PI)), yy); await p.waitForTimeout(40); }
  await p.mouse.up(); await p.waitForTimeout(500);
});
// 5 water trend widget
await clip('water', '/sar-change/', async (p) => { for (let k = 0; k < 3; k++) { const y = await top(p, '#trend .tw', 76); await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(900); } }, async (p) => {
  await p.waitForTimeout(1400); await p.locator('.seg button[data-v="ontario"]').click(); await p.waitForTimeout(1800);
});
// 6 field shift app sliders
await clip('fieldapp', '/field-shift/app/', async (p) => { await p.waitForTimeout(2500); }, async (p) => {
  const s = p.locator('input[type=range]').first(); const bb = await s.boundingBox();
  if (bb) { await p.mouse.move(bb.x + bb.width * 0.5, bb.y + bb.height / 2); await p.mouse.down(); for (let i = 0; i <= 25; i++) { await p.mouse.move(bb.x + bb.width * (0.5 + 0.45 * i / 25), bb.y + bb.height / 2); await p.waitForTimeout(40); } await p.mouse.up(); }
  await p.waitForTimeout(1800);
});
// 7 crops trend widget
await clip('crops', '/field-shift/', async (p) => { for (let k = 0; k < 3; k++) { const y = await top(p, '#trend .tw', 76); await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(900); } }, async (p) => {
  await p.waitForTimeout(1300); await p.selectOption('.sel select', 'first_fall_frost_doy'); await p.waitForTimeout(1800);
});
fs.writeFileSync(`${out}/clips.json`, JSON.stringify(meta, null, 1));
await b.close();
