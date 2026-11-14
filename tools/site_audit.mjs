// Headless site audit: crawl every same-host page, check every internal link + asset returns 200, console errors per page,
// app deep links, deck video readyState. Usage: node tools/site_audit.mjs [base]
import { chromium } from '/node_modules/playwright-core/index.mjs';
const base = (process.argv[2] || 'https://spaceapps.parsariahi.com').replace(/\/$/, ''); const host = new URL(base).host;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
const pages = new Set(), assets = new Map(), consoleErr = {}, bad = [], seen = new Set(), from = new Map();
const norm = (u, ref) => { try { const x = new URL(u, ref || base); if (x.host !== host) return null; x.hash = ''; return x.href; } catch { return null; } };
const queue = [base + '/'];
const isPage = (u) => { const p = new URL(u).pathname; return p.endsWith('/') || p.endsWith('.html') || !/\.[a-z0-9]{2,5}$/i.test(p); };
while (queue.length) {
  const u = queue.shift(); if (seen.has(u)) continue; seen.add(u); pages.add(u);
  const p = await ctx.newPage(); const errs = []; consoleErr[u] = errs;
  p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text().slice(0, 200) + ' @ ' + (m.location()?.url || '')); }); p.on('pageerror', (e) => errs.push('pageerror ' + e.message.slice(0, 200)));
  p.on('response', (r) => { const n = norm(r.url()); if (n && !isPage(n)) { assets.set(n, Math.max(assets.get(n) || 0, r.status() === 206 || r.status() === 304 ? 200 : r.status())); if (!from.has(n)) from.set(n, u); } });
  let st = 0; try { const r = await p.goto(u, { waitUntil: 'load', timeout: 45000 }); st = r ? r.status() : 0; await p.waitForTimeout(1500); } catch (e) { errs.push('goto ' + e.message.slice(0, 100)); }
  if (st !== 200) bad.push(['page', u, st, from.get(u)]);
  const refs = await p.evaluate(() => { const out = []; const add = (v) => v && out.push(v);
    document.querySelectorAll('a[href]').forEach((a) => add(a.getAttribute('href')));
    document.querySelectorAll('img[src],script[src],source[src],video[src],audio[src],iframe[src],track[src],embed[src]').forEach((e) => add(e.getAttribute('src')));
    document.querySelectorAll('video[poster]').forEach((e) => add(e.getAttribute('poster')));
    document.querySelectorAll('link[href]').forEach((e) => add(e.getAttribute('href')));
    document.querySelectorAll('[srcset]').forEach((e) => e.getAttribute('srcset').split(',').forEach((s) => add(s.trim().split(/\s+/)[0])));
    document.querySelectorAll('[style*="url("]').forEach((e) => (e.getAttribute('style').match(/url\(([^)]+)\)/g) || []).forEach((m) => add(m.slice(4, -1).replace(/['"]/g, ''))));
    return out; }).catch(() => []);
  for (const r of refs) { if (/^(mailto:|tel:|javascript:|data:|#)/.test(r)) continue; const n = norm(r, u); if (!n) continue; if (!from.has(n)) from.set(n, u);
    if (isPage(n)) { if (!seen.has(n)) queue.push(n); } else if (!assets.has(n)) assets.set(n, -1); }
  await p.close();
}
for (const [a, s] of assets) { if (s === 200) continue; let code = 0; try { const r = await fetch(a, { method: 'GET', redirect: 'follow' }); code = r.status; await r.body?.cancel(); } catch { code = -2; } assets.set(a, code); }
for (const [a, s] of assets) if (s !== 200) bad.push(['asset', a, s, from.get(a)]);
const deep = [['/sar-change/app/#act=sar-change-1', () => document.querySelector('#opsC2 .c2-card.sel')?.dataset.id],
  ['/sar-change/app/#alert=sar-change-1', () => !!document.querySelector('#opsC2 .c2-al:not([hidden]) .c2-send')],
  ['/hotspots/app/#act=hotspots-1', () => document.querySelector('.c2-card.sel')?.dataset.id],
  ['/hotspots/app/#alert=hotspots-1', () => !!document.querySelector('.c2-al:not([hidden]) .c2-send')],
  ['/hotspots/app/#view=canada', () => (document.querySelector('#canadaBtn')?.getAttribute('aria-pressed')) + ' | ' + document.body.className],
  ['/field-shift/app/#act=field-shift-4', () => document.querySelector('.c2-card.sel')?.dataset.id],
  ['/field-shift/app/#alert=field-shift-4', () => !!document.querySelector('.c2-al:not([hidden]) .c2-send')],
  ['/field-shift/app/#simple', () => document.querySelector('.fs-mode [aria-pressed=true]')?.dataset.mode],
  ['/sar-change/app/#demo', () => !!document.querySelector('#opsC2 .c2-al:not([hidden])')]];
const deepRes = [];
for (const [path, fn] of deep) { const p = await ctx.newPage(); const errs = []; p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text().slice(0, 160)); }); p.on('pageerror', (e) => errs.push(e.message.slice(0, 160)));
  await p.goto(base + path, { waitUntil: 'load' }); await p.waitForTimeout(3000); deepRes.push([path, await p.evaluate(fn).catch((e) => 'ERR ' + e.message), errs]); await p.close(); }
const dk = await ctx.newPage(); const dkErr = []; dk.on('console', (m) => { if (m.type() === 'error') dkErr.push(m.text().slice(0, 160)); });
await dk.goto(base + '/submission/deck.html', { waitUntil: 'load' }).catch((e) => dkErr.push(e.message));
await dk.evaluate(async () => { for (const v of document.querySelectorAll('video')) { v.muted = true; v.scrollIntoView(); try { v.load(); await v.play(); } catch {} await new Promise((r) => setTimeout(r, 600)); } });
await dk.waitForTimeout(4000);
const vids = await dk.evaluate(() => [...document.querySelectorAll('video')].map((v) => [v.currentSrc.split('/').slice(-1)[0], v.readyState, v.error && v.error.code]));
console.log(JSON.stringify({ base, pages: [...pages].length, pageList: [...pages], assets: assets.size, bad, consoleErrors: Object.fromEntries(Object.entries(consoleErr).filter(([, e]) => e.length)), deepRes, deckVideos: vids, deckErrors: dkErr }, null, 1));
await b.close();
