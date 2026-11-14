// Demo-video takes v4 (1600x800 CSS -> 1920x960 frames; make_video4.py adds a 120 px caption bar -> 1920x1080).
// One continuous take per app with a visible, smoothly moving cursor and real clicks/drags on the live dashboards.
// Each take logs step marks (seconds from take start) used for captions and the cut of demo.mp4.
// Tasking and alerts are the dashboards' own simulation: nothing is sent anywhere.
// Usage: node tools/video_record4.mjs [base] [take,take]
import { chromium } from '/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const base = process.argv[2] || 'https://nasa-spaceapps-2026.pages.dev', only = process.argv[3] ? process.argv[3].split(',') : null;
const out = new URL('../submission/build/video4/', import.meta.url).pathname; fs.mkdirSync(out, { recursive: true });
const W = 1600, H = 800;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars'] });
const errs = []; const metaF = `${out}takes.json`; const meta = fs.existsSync(metaF) ? JSON.parse(fs.readFileSync(metaF)) : {};
// visible cursor overlay (pointer-events none) driven by the real mouse events
const CURSOR = () => { const mk = () => { if (document.getElementById('vcur')) return; const s = document.createElement('style');
  s.textContent = `#vcur{position:fixed;left:0;top:0;width:30px;height:30px;z-index:2147483647;pointer-events:none;transform:translate(-100px,-100px);filter:drop-shadow(0 2px 3px rgba(0,0,0,.45))}
  #vcur svg{width:30px;height:30px}#vcur .rp{position:absolute;left:-17px;top:-17px;width:34px;height:34px;border-radius:50%;border:3px solid #fbbf24;opacity:0;transform:scale(.4)}
  #vcur.dn .rp{animation:vrp .5s ease-out}@keyframes vrp{0%{opacity:.95;transform:scale(.4)}100%{opacity:0;transform:scale(1.5)}}`;
  document.head.appendChild(s); const c = document.createElement('div'); c.id = 'vcur';
  c.innerHTML = '<span class="rp"></span><svg viewBox="0 0 24 24"><path d="M3 2l7.5 19 2.6-7.6L21 11z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  document.body.appendChild(c);
  addEventListener('mousemove', (e) => { c.style.transform = `translate(${e.clientX - 3}px,${e.clientY - 2}px)`; }, true);
  addEventListener('mousedown', () => { c.classList.remove('dn'); void c.offsetWidth; c.classList.add('dn'); }, true); };
  if (document.body) mk(); else addEventListener('DOMContentLoaded', mk); };
let cur = { x: W * 0.62, y: H * 0.55 };
const ease = (k) => (k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
async function glide(p, x, y, ms = 650) { const x0 = cur.x, y0 = cur.y, n = Math.max(8, Math.round(ms / 16));
  for (let i = 1; i <= n; i++) { const k = ease(i / n); await p.mouse.move(x0 + (x - x0) * k, y0 + (y - y0) * k); await p.waitForTimeout(16); } cur = { x, y }; }
async function box(p, sel) { const el = p.locator(sel).first(); await el.waitFor({ state: 'visible', timeout: 5000 }).catch(() => errs.push('vis ' + sel)); return el.boundingBox({ timeout: 3000 }).catch(() => null); }
// smooth window scroll so el sits below the sticky dock head (or at off px from the top)
const scrollTo = (p, sel, off = 120, ms = 700) => p.evaluate(([s, o, ms]) => new Promise((r) => { const el = document.querySelector(s); if (!el) return r(); document.documentElement.style.scrollBehavior = 'auto'; document.body.style.scrollBehavior = 'auto'; const y = Math.max(0, el.getBoundingClientRect().top + scrollY - o), s0 = scrollY, t0 = performance.now();
  const f = (t) => { const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; window.scrollTo(0, s0 + (y - s0) * e); k < 1 ? requestAnimationFrame(f) : r(); }; requestAnimationFrame(f); }), [sel, off, ms]);
async function click(p, sel, wait = 700, ms = 650) { const bb = await box(p, sel); if (!bb) { errs.push('click ' + sel); return; }
  await glide(p, bb.x + bb.width / 2, bb.y + bb.height / 2, ms); await p.waitForTimeout(140);
  for (let i = 0; i < 3; i++) { const b2 = await box(p, sel); if (!b2) break; const x = b2.x + b2.width / 2, y = b2.y + b2.height / 2; if (Math.abs(x - cur.x) < 3 && Math.abs(y - cur.y) < 3) break; await glide(p, x, y, 300); await p.waitForTimeout(120); } await p.mouse.down(); await p.waitForTimeout(80); await p.mouse.up(); await p.waitForTimeout(wait); }
async function hover(p, sel, wait = 400, ms = 600) { const bb = await box(p, sel); if (bb) await glide(p, bb.x + bb.width / 2, bb.y + bb.height / 2, ms); await p.waitForTimeout(wait); }

const TAKES = {
  // flood: slider -> classification -> action previews -> dispatch + queue -> Alert everyone -> send
  'flood': { url: '/sar-change/app/', prep: async (p) => { await p.evaluate(() => scrollTo(0, 0)); }, act: async (p, m) => {
    await p.waitForTimeout(500);
    m('slider'); const mp = await box(p, '#opsMap');
    const yy = mp.y + mp.height * 0.58; await glide(p, mp.x + mp.width * 0.5, yy, 700); await p.waitForTimeout(150); await p.mouse.down();
    await glide(p, mp.x + mp.width * 0.88, yy, 1500); await p.waitForTimeout(300); await glide(p, mp.x + mp.width * 0.1, yy, 2000); await p.waitForTimeout(300);
    await glide(p, mp.x + mp.width * 0.55, yy, 1100); await p.mouse.up(); await p.waitForTimeout(500);
    m('classify'); await click(p, '.ops-toolbar [data-layer=delta]', 2600); await hover(p, '#pane-change #wcH', 1600);
    m('preview'); await click(p, '.og-dock [data-pane=act]', 700);
    for (const id of ['sar-change-1', 'sar-change-2', 'sar-change-3']) { await scrollTo(p, `#opsC2 .c2-card[data-id=${id}]`, 130, 600); await p.waitForTimeout(150); await click(p, `#opsC2 .c2-card[data-id=${id}] .c2-show`, 1700); }
    await scrollTo(p, '#opsC2 .c2-card[data-id=sar-change-1]', 130, 700); await p.waitForTimeout(200);
    m('dispatch'); await click(p, '#opsC2 .c2-card[data-id=sar-change-1] .c2-go', 1300);
    m('queue'); await scrollTo(p, '#opsC2 .c2-q', 130, 800); await hover(p, '#opsC2 .c2-q .c2-tasks', 4600, 700);
    m('alert'); await scrollTo(p, 'body', 0, 700); await click(p, '#opsAlertAll', 2600);
    m('send'); await click(p, '#opsC2 .c2-send', 2600);
    m('end'); } },
  // fire: full-Canada map + province trend -> action previews -> crews tasked + queue -> alert draft -> send
  'fire': { url: '/hotspots/app/', act: async (p, m) => {
    await p.waitForTimeout(400);
    m('map'); await click(p, '#canadaBtn', 2200); await click(p, '.og-stage [data-layer=trend], [data-layer=trend]', 2400);
    m('preview'); for (const id of ['hotspots-1', 'hotspots-2', 'hotspots-3']) { await scrollTo(p, `#c2 .c2-card[data-id=${id}]`, 130, 600); await p.waitForTimeout(150); await click(p, `#c2 .c2-card[data-id=${id}] .c2-show`, 1600); }
    await scrollTo(p, '#c2 .c2-card[data-id=hotspots-1]', 130, 700);
    m('dispatch'); await click(p, '#c2 .c2-card[data-id=hotspots-1] .c2-go', 600); await hover(p, '#map', 2600, 900);
    m('queue'); await scrollTo(p, '#c2 .c2-q', 130, 800); await hover(p, '#c2 .c2-q .c2-tasks', 2600, 700);
    await scrollTo(p, '#c2 .c2-card[data-id=hotspots-1]', 130, 700);
    m('alert'); await click(p, '#c2 .c2-card[data-id=hotspots-1] .c2-alrt', 1400); await scrollTo(p, '#c2 .c2-send', 520, 700); await p.waitForTimeout(900);
    if (!(await p.locator('#c2 .c2-send').count())) { errs.push('no draft, retry'); await click(p, `#c2 .c2-alrt`, 1400); } m('send'); await click(p, '#c2 .c2-send', 2400);
    m('end'); } },
  // field: crop map -> Act tab previews -> drone + scout tasking + queue -> alert draft -> send
  'field': { url: '/field-shift/app/', act: async (p, m) => {
    await p.waitForTimeout(400);
    m('map'); await click(p, '#layers [data-layer=crops]', 2600);
    m('preview'); await click(p, '.og-tabs [data-pane=act]', 900);
    for (const id of ['field-shift-1', 'field-shift-2', 'field-shift-4']) { await scrollTo(p, `#c2 .c2-card[data-id=${id}]`, 130, 600); await p.waitForTimeout(150); await click(p, `#c2 .c2-card[data-id=${id}] .c2-show`, 1600); }
    m('dispatch'); await click(p, '#c2 .c2-card[data-id=field-shift-4] .c2-go', 1200);
    m('queue'); await scrollTo(p, '#c2 .c2-q', 130, 800); await hover(p, '#c2 .c2-q .c2-tasks', 4200, 700);
    await scrollTo(p, '#c2 .c2-card[data-id=field-shift-4]', 130, 700);
    m('alert'); await click(p, '#c2 .c2-card[data-id=field-shift-4] .c2-alrt', 1400); await scrollTo(p, '#c2 .c2-send', 520, 700); await p.waitForTimeout(900);
    if (!(await p.locator('#c2 .c2-send').count())) { errs.push('no draft, retry'); await click(p, `#c2 .c2-alrt`, 1400); } m('send'); await click(p, '#c2 .c2-send', 2400);
    m('end'); } },
};
for (const [name, c] of Object.entries(TAKES)) {
  if (only && !only.includes(name)) continue;
  const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1.2, colorScheme: 'dark' }); await ctx.addInitScript(CURSOR);
  const p = await ctx.newPage(); p.on('pageerror', (e) => errs.push(name + ' ' + e.message));
  await p.goto(base + c.url, { waitUntil: 'load', timeout: 60000 }); await p.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {}); await p.waitForTimeout(3500); if (c.prep) await c.prep(p);
  cur = { x: W * 0.62, y: H * 0.55 }; await p.mouse.move(cur.x, cur.y); await p.waitForTimeout(300);
  const cdp = await ctx.newCDPSession(p); const frames = [];
  cdp.on('Page.screencastFrame', async (f) => { frames.push({ t: f.metadata.timestamp, d: f.data }); try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch {} });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 1920, maxHeight: 960 }); await p.waitForTimeout(300);
  const marks = {}; let t0 = null; const m = (k) => { marks[k] = +(Date.now() / 1000 - t0).toFixed(3); };
  t0 = Date.now() / 1000; await c.act(p, m); await p.waitForTimeout(200); const t1 = Date.now() / 1000; await cdp.send('Page.stopScreencast'); await ctx.close();
  const dir = `${out}${name}`; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  // drop frames before t0 so concat time 0 == t0; first kept frame is held from t0
  const fr = frames.filter((f) => f.t >= t0 - 0.5); const L = ['ffconcat version 1.0'];
  fr.forEach((f, i) => fs.writeFileSync(`${dir}/f${String(i).padStart(5, '0')}.jpg`, Buffer.from(f.d, 'base64')));
  for (let i = 0; i < fr.length; i++) { const st = i === 0 ? t0 : fr[i].t, d = i + 1 < fr.length ? fr[i + 1].t - st : Math.max(0.05, t1 - st); L.push(`file f${String(i).padStart(5, '0')}.jpg`, `duration ${Math.max(0.001, d).toFixed(4)}`); }
  L.push(`file f${String(fr.length - 1).padStart(5, '0')}.jpg`); fs.writeFileSync(`${dir}/list.ffconcat`, L.join('\n') + '\n');
  meta[name] = { dir, frames: fr.length, secs: +(t1 - t0).toFixed(2), marks, base }; fs.writeFileSync(metaF, JSON.stringify(meta, null, 1)); console.log(name, fr.length, 'frames', (t1 - t0).toFixed(2), 's', JSON.stringify(marks));
}
fs.writeFileSync(metaF, JSON.stringify(meta, null, 1)); console.log('errors', errs); await b.close();
