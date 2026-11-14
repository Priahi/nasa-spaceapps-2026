// Deck loops v7 (my own clips, not the demo-video takes): real click-throughs on the live dashboards, recorded at 2x,
// each phase cropped to the panel that carries it, then joined into one 1200x750 loop (tools/deck_loops7.py).
//  fire:  Alberta -> 2026 outlook (May is the watch month) -> Actions: Crews & hiring -> Assign crews (simulated queue) -> What if: +16 days, ~65,000 ha
//  field: Slope map -> 92 steep squares on the map -> Act: seed winter rye -> Approve (simulated queue) -> What if: ~$1.2 M
// Usage: node tools/deck_loops7.mjs [base] [fire,field]
import { chromium } from 'playwright-core';
import fs from 'fs';
const base = process.argv[2] || 'https://spaceapps.parsariahi.com', only = process.argv[3] ? process.argv[3].split(',') : null;
const out = new URL('../submission/build/loops7/', import.meta.url).pathname; fs.mkdirSync(out, { recursive: true });
const W = 1600, H = 800;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--hide-scrollbars', '--force-device-scale-factor=2'] });
const errs = [];
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
let cur = { x: W * 0.8, y: H * 0.4 };
const ease = (k) => (k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
async function glide(p, x, y, ms = 600) { const x0 = cur.x, y0 = cur.y, n = Math.max(8, Math.round(ms / 16));
  for (let i = 1; i <= n; i++) { const k = ease(i / n); await p.mouse.move(x0 + (x - x0) * k, y0 + (y - y0) * k); await p.waitForTimeout(16); } cur = { x, y }; }
async function box(p, sel) { const el = typeof sel === 'string' ? p.locator(sel).first() : sel; await el.waitFor({ state: 'visible', timeout: 2500 }).catch(() => errs.push('vis ' + sel)); return el.boundingBox({ timeout: 3000 }).catch(() => null); }
const scrollY = (p, y, ms = 700) => p.evaluate(([y, ms]) => new Promise((r) => { document.documentElement.style.scrollBehavior = 'auto'; const s0 = window.scrollY, t0 = performance.now();
  const f = (t) => { const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; window.scrollTo(0, s0 + (y - s0) * e); k < 1 ? requestAnimationFrame(f) : r(); }; requestAnimationFrame(f); }), [y, ms]);
const topOf = (p, sel) => p.evaluate((s) => { const e = document.querySelector(s); return e ? e.getBoundingClientRect().top + window.scrollY : 0; }, sel);
async function click(p, sel, wait = 700, ms = 600) { const bb = await box(p, sel); if (!bb) { errs.push('click ' + sel); return; }
  await glide(p, bb.x + bb.width / 2, bb.y + bb.height / 2, ms); await p.waitForTimeout(120); await p.mouse.down(); await p.waitForTimeout(80); await p.mouse.up(); await p.waitForTimeout(wait); }
async function hover(p, sel, wait = 400, ms = 600) { const bb = await box(p, sel); if (bb) await glide(p, bb.x + bb.width / 2, bb.y + bb.height / 2, ms); await p.waitForTimeout(wait); }
const tab = (p, scope, t) => p.locator(`${scope} button, ${scope} [role=tab]`, { hasText: t }).first();
// crop boxes are CSS px in the viewport; phases switch crops
const TAKES = {
  fire: { url: '/hotspots/app/', prep: async (p) => { await p.locator('select#preset, select').first().selectOption('alberta'); await p.waitForTimeout(4500); await p.evaluate(() => scrollTo(0, 0)); },
    act: async (p, m) => {
      const dock = { x: 1012, y: 76, w: 588, h: 368 };
      m('outlook', dock); await p.waitForTimeout(300); await click(p, tab(p, '.og-dock', '2026 outlook'), 900);
      await hover(p, p.locator('.og-dock').getByText('Watch:', { exact: false }).first(), 1600, 700);
      m('actions', dock); await click(p, tab(p, '.og-dock', 'Actions'), 800);
      await hover(p, '.c2-card[data-id=hotspots-1]', 700);
      await click(p, '.c2-card[data-id=hotspots-1] .c2-go', 900);
      const qy = await topOf(p, '.c2-q'); await scrollY(p, Math.max(0, qy - 200), 800); await hover(p, '.c2-q', 1500, 500);
      const wy = await topOf(p, '#whatif .wi-kpis'); m('whatif', { x: 90, y: 40, w: 1420, h: 760 }); await scrollY(p, wy - 56, 10); await p.waitForTimeout(150);
      await hover(p, '#whatif .wi-kpis > :nth-child(2)', 1500, 700); await hover(p, '#whatif table tr:nth-child(1)', 1600, 600);
      m('end'); } },
  field: { url: '/field-shift/app/', prep: async (p) => { await p.evaluate(() => scrollTo(0, 0)); },
    act: async (p, m) => {
      const map = { x: 0, y: 76, w: 1012, h: 632 }, dock = { x: 1012, y: 76, w: 588, h: 368 };
      m('map', map); await click(p, p.locator('button', { hasText: /^Slope$/ }).first(), 1800);
      m('act', dock); await click(p, '.og-tabs [data-pane=act]', 800);
      const cy = await topOf(p, '.c2-card[data-id=field-shift-2]'); await scrollY(p, Math.max(0, cy - 230), 600);
      await hover(p, '.c2-card[data-id=field-shift-2]', 600);
      await click(p, '.c2-card[data-id=field-shift-2] .c2-show', 300);
      m('map2', map); await scrollY(p, 0, 10); await p.waitForTimeout(1600);
      m('go', dock); await scrollY(p, Math.max(0, cy - 230), 10); await click(p, '.c2-card[data-id=field-shift-2] .c2-go', 900);
      const qy = await topOf(p, '.c2-q'); await scrollY(p, Math.max(0, qy - 200), 800); await hover(p, '.c2-q', 1500, 500);
      const wy = await topOf(p, '#whatif .wi-kpis'); m('whatif', { x: 90, y: 40, w: 1420, h: 760 }); await scrollY(p, wy - 56, 10); await p.waitForTimeout(150);
      await hover(p, '#whatif .wi-kpis > :nth-child(2)', 1500, 700); await hover(p, '#whatif table tr:nth-child(3)', 1500, 600);
      m('end'); } },
};
const meta = {};
for (const [name, c] of Object.entries(TAKES)) {
  if (only && !only.includes(name)) continue;
  const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2, colorScheme: 'dark' }); await ctx.addInitScript(CURSOR);
  const p = await ctx.newPage(); p.on('pageerror', (e) => errs.push(name + ' ' + e.message));
  await p.goto(base + c.url, { waitUntil: 'load', timeout: 60000 }); await p.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {}); await p.waitForTimeout(3500); await c.prep(p);
  cur = { x: W * 0.8, y: H * 0.4 }; await p.mouse.move(cur.x, cur.y); await p.waitForTimeout(300);
  const cdp = await ctx.newCDPSession(p); const frames = [];
  cdp.on('Page.screencastFrame', async (f) => { frames.push({ t: f.metadata.timestamp, d: f.data }); try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch {} });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: W * 2, maxHeight: H * 2 }); await p.waitForTimeout(400);
  const marks = []; let t0 = Date.now() / 1000; const m = (k, crop) => marks.push({ k, t: +(Date.now() / 1000 - t0).toFixed(3), crop });
  await c.act(p, m); await p.waitForTimeout(150); const t1 = Date.now() / 1000; await cdp.send('Page.stopScreencast'); await ctx.close();
  const dir = `${out}${name}`; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const fr = frames.filter((f) => f.t >= t0 - 0.5);
  fr.forEach((f, i) => fs.writeFileSync(`${dir}/f${String(i).padStart(5, '0')}.jpg`, Buffer.from(f.d, 'base64')));
  meta[name] = { dir, t0, t1, frames: fr.map((f, i) => ({ i, t: +(Math.max(0, f.t - t0)).toFixed(3) })), marks, secs: +(t1 - t0).toFixed(2) };
  console.log(name, fr.length, 'frames', (t1 - t0).toFixed(2), 's', marks.map((x) => x.k + '@' + x.t).join(' '));
}
fs.writeFileSync(`${out}takes.json`, JSON.stringify(meta, null, 1)); console.log('errors', errs); await b.close();
