// Story-video clips (1600x900 CSS -> 1920x1080). Real interactions on the live dashboards; tasking/alerts are the dashboards' simulation.
// Usage: node tools/video_record3.mjs [base] [clip,clip]
import { chromium } from '/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const base = process.argv[2] || 'https://nasa-spaceapps-2026.pages.dev', only = process.argv[3] ? process.argv[3].split(',') : null;
const out = new URL('../submission/build/video3/', import.meta.url).pathname; fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const errs = []; const metaF = `${out}clips.json`; const meta = fs.existsSync(metaF) ? JSON.parse(fs.readFileSync(metaF)) : {};
const click = async (p, sel, wait = 700) => { const el = p.locator(sel).first(); await el.click({ timeout: 4000 }).catch(() => errs.push('click ' + sel)); await p.waitForTimeout(wait); };
const scrollTo = (p, sel, off = 60, ms = 700) => p.evaluate(([s, o, ms]) => new Promise((r) => { const el = document.querySelector(s); if (!el) return r(); const y = el.getBoundingClientRect().top + scrollY - o, s0 = scrollY, t0 = performance.now();
  const f = (t) => { const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; window.scrollTo(0, s0 + (y - s0) * e); k < 1 ? requestAnimationFrame(f) : r(); }; requestAnimationFrame(f); }), [sel, off, ms]);
const CLIPS = {
  // montage: fire, crews approved -> zones + assets + queue run
  'fire': { url: '/hotspots/app/', act: async (p) => { await p.waitForTimeout(300); await click(p, '#c2 .c2-card[data-id=hotspots-1] .c2-go', 4200); } },
  // montage: field, rye on steep squares approved
  'field': { url: '/field-shift/app/', prep: async (p) => { await click(p, '.og-tabs [data-pane=act]', 800); }, act: async (p) => { await p.waitForTimeout(300); await click(p, '#c2 .c2-card[data-id=field-shift-2] .c2-go', 4200); } },
  'fire-notice': { url: '/hotspots/app/', act: async (p) => { await p.waitForTimeout(300); await click(p, '#c2 .c2-card[data-id=hotspots-2] .c2-go', 2600); await click(p, '#c2 .c2-card[data-id=hotspots-2] .c2-alrt', 1600); await click(p, '.c2-send', 2400); } },
  'field-plan': { url: '/field-shift/app/', prep: async (p) => { await click(p, '.og-tabs [data-pane=act]', 800); }, act: async (p) => { await p.waitForTimeout(300); await click(p, '#c2 .c2-card[data-id=field-shift-1] .c2-go', 2600); await click(p, '#c2 .c2-card[data-id=field-shift-1] .c2-alrt', 1600); await click(p, '.c2-send', 2400); } },
  // flood (record after the new flood deploy): rain signal, then approve dispatch on the map, then alert everyone
  'flood-rain': { url: '/sar-change/app/', prep: async (p) => { await p.evaluate(() => { const el = document.querySelector('.ops-rain'); el && el.scrollIntoView({ block: 'center' }); }); await p.waitForTimeout(900); }, act: async (p) => { await p.waitForTimeout(4200); } },
  'flood-map': { url: '/sar-change/app/', act: async (p) => { await p.waitForTimeout(600); await click(p, '#opsC2 .c2-card[data-id=sar-change-1] .c2-show', 1400); await click(p, '#opsC2 .c2-card[data-id=sar-change-1] .c2-go', 5600); } },
  'flood-alert': { url: '/sar-change/app/#act=sar-change-1', act: async (p) => { await p.waitForTimeout(500); await click(p, '#opsC2 .c2-card[data-id=sar-change-1] .c2-go', 1200); await click(p, '#opsC2 .c2-card[data-id=sar-change-1] .c2-alrt', 1800); await click(p, '.c2-send', 3400); } },
};
for (const [name, c] of Object.entries(CLIPS)) {
  if (only ? !only.includes(name) : name.startsWith('flood')) continue;
  const ctx = await b.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1.2 }); const p = await ctx.newPage(); p.on('pageerror', (e) => errs.push(name + ' ' + e.message));
  await p.goto(base + c.url, { waitUntil: 'networkidle' }); await p.waitForTimeout(3500); if (c.prep) await c.prep(p);
  const cdp = await ctx.newCDPSession(p); const frames = [];
  cdp.on('Page.screencastFrame', async (f) => { frames.push({ t: f.metadata.timestamp, d: f.data }); try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch {} });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 1920, maxHeight: 1080 }); await p.waitForTimeout(250);
  const t0 = Date.now() / 1000; await c.act(p); const t1 = Date.now() / 1000; await cdp.send('Page.stopScreencast'); await ctx.close();
  const dir = `${out}${name}`; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const L = ['ffconcat version 1.0']; frames.forEach((f, i) => fs.writeFileSync(`${dir}/f${String(i).padStart(5, '0')}.jpg`, Buffer.from(f.d, 'base64')));
  for (let i = 0; i < frames.length; i++) { const d = i + 1 < frames.length ? frames[i + 1].t - frames[i].t : Math.max(0.05, t1 - frames[i].t); L.push(`file f${String(i).padStart(5, '0')}.jpg`, `duration ${d.toFixed(4)}`); }
  L.push(`file f${String(frames.length - 1).padStart(5, '0')}.jpg`); fs.writeFileSync(`${dir}/list.ffconcat`, L.join('\n') + '\n');
  meta[name] = { dir, frames: frames.length, secs: +(t1 - t0).toFixed(2) }; console.log(name, frames.length, 'frames', (t1 - t0).toFixed(2), 's');
}
fs.writeFileSync(metaF, JSON.stringify(meta, null, 1)); console.log('errors', errs); await b.close();
