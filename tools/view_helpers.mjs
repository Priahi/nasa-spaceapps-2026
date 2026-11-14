// Shared helpers for deck captures and video recording: explicit map views and focal crops.
import fs from 'fs';
export const VIEWS = JSON.parse(fs.readFileSync(new URL('./capture_views.json', import.meta.url))).focal;
// Grab every Leaflet map the page creates (window.__maps) so we can set its view explicitly.
export const LEAFLET_HOOK = () => {
  let _L; Object.defineProperty(window, 'L', { configurable: true, get() { return _L; }, set(v) { _L = v; try { v.Map.addInitHook(function () { (window.__maps = window.__maps || []).push(this); }); } catch (e) {} } });
};
export async function fitLeaflet(p, key) {
  const b = VIEWS[key].bounds;
  const ok = await p.evaluate((b) => { const m = (window.__maps || []).filter((m) => m._container && m._container.offsetParent); if (!m.length) return false;
    m.forEach((x) => { x.invalidateSize(); x.fitBounds(b, { padding: [12, 12], animate: false }); }); return true; }, b);
  await p.waitForTimeout(900); return ok;
}
// Screen-space union bbox of the named town outlines (SAR ops map) + pad, clamped to the map element.
export async function townsBox(p, key, within = '#opsMap') {
  const { towns, pad } = VIEWS[key];
  return p.evaluate(([towns, pad, within]) => {
    const W = document.querySelector(within).getBoundingClientRect(); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    towns.forEach((n) => { const el = document.querySelector(`${within} path[data-n="${n}"]`); if (!el) return; const r = el.getBoundingClientRect(); x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom); });
    if (x0 > x1) return { x: W.left, y: W.top, width: W.width, height: W.height };
    const px = (x1 - x0) * pad, py = (y1 - y0) * pad; x0 = Math.max(W.left, x0 - px); y0 = Math.max(W.top, y0 - py); x1 = Math.min(W.right, x1 + px); y1 = Math.min(W.bottom, y1 + py);
    return { x: x0 + scrollX, y: y0 + scrollY, width: x1 - x0, height: y1 - y0 };
  }, [towns, pad, within]);
}
export async function centerOn(p, box) { await p.evaluate((b) => scrollTo(0, Math.max(0, b.y + b.height / 2 - innerHeight / 2)), box); await p.waitForTimeout(500); }
