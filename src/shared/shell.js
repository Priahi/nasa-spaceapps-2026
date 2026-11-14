/* Orbit to Ground dashboard shell: dock tabs. Markup: .og-tabs > button[data-pane=x] + #pane-x.og-pane inside .og-dock.
   OGShell.show("x") activates a pane; OGShell.reveal(el) activates the pane containing el. Links to #pane-x or to an element
   inside a pane open that pane. */
(function () {
  "use strict";
  function show(id, opts) {
    const pane = document.getElementById("pane-" + id); if (!pane) return false;
    const dock = pane.closest(".og-dock") || document;
    dock.querySelectorAll(".og-pane").forEach((p) => { p.hidden = p !== pane; });
    dock.querySelectorAll(".og-tabs [data-pane]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.pane === id)));
    if (!(opts && opts.keepScroll)) { const body = pane.closest(".og-dock-body"); if (body && getComputedStyle(body).overflowY === "auto") body.scrollTop = 0; }
    window.dispatchEvent(new CustomEvent("og:pane", { detail: { id } }));
    return true;
  }
  function reveal(el) { const p = el && el.closest && el.closest(".og-pane"); if (p && p.hidden) show(p.id.replace(/^pane-/, ""), { keepScroll: true }); }
  document.addEventListener("click", (ev) => {
    const b = ev.target.closest(".og-tabs [data-pane]"); if (b) { show(b.dataset.pane); return; }
    const a = ev.target.closest('a[href^="#"]'); if (!a) return;
    const t = document.getElementById(a.getAttribute("href").slice(1)); if (!t) return;
    const p = t.classList.contains("og-pane") ? t : t.closest(".og-pane"); if (!p) return;
    ev.preventDefault(); reveal(t); if (t.classList.contains("og-pane")) show(t.id.replace(/^pane-/, ""));
    setTimeout(() => t.scrollIntoView({ behavior: "smooth", block: "nearest" }), 30);
  });
  document.addEventListener("keydown", (ev) => {
    const b = ev.target.closest && ev.target.closest(".og-tabs [data-pane]"); if (!b || !["ArrowLeft", "ArrowRight"].includes(ev.key)) return;
    const all = [...b.parentElement.querySelectorAll("[data-pane]")], i = all.indexOf(b), n = all[(i + (ev.key === "ArrowRight" ? 1 : all.length - 1)) % all.length];
    n.focus(); show(n.dataset.pane);
  });
  /* the workspace fills the viewport below the bars above it */
  function fit() { document.querySelectorAll(".og-work").forEach((w) => { const t = Math.round(w.getBoundingClientRect().top + window.scrollY); w.style.setProperty("--og-top", t + "px"); }); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fit); else fit();
  window.addEventListener("load", fit); window.addEventListener("resize", fit);
  /* bring an element in the dock into view. Desktop: scroll the page (the map column is sticky, so it stays on screen),
     leaving room for the sticky dock head. Narrow screens: leave the page where it is, so the map stays in view. */
  function scrollDock(el) {
    if (!el) return; reveal(el); if (window.innerWidth < 1024) return;
    const head = el.closest(".og-dock") && el.closest(".og-dock").querySelector(".og-dock-head");
    const off = (head ? head.getBoundingClientRect().height : 0) + 10, y = el.getBoundingClientRect().top - off;
    if (Math.abs(y) > 4) window.scrollBy({ top: y, behavior: "auto" });
  }
  /* keep map text readable: hide labels that sit under fixed overlays, then nudge markers off labels/overlays/each other.
     fixed, hideable, movers: arrays of elements. Uses the CSS translate property, so it composes with Leaflet's transform. */
  function declutter(movers, fixed, hideable) {
    const vis = (e) => e && e.getClientRects().length && getComputedStyle(e).visibility !== "hidden";
    const R = [], pad = 3, box = (r) => ({ l: r.left, r: r.right, t: r.top, b: r.bottom });
    const hit = (q) => R.some((o) => q.l < o.r + pad && q.r > o.l - pad && q.t < o.b + pad && q.b > o.t - pad);
    (fixed || []).forEach((e) => { if (vis(e)) R.push(box(e.getBoundingClientRect())); });
    (hideable || []).forEach((e) => { e.style.visibility = ""; if (!vis(e)) return; const q = box(e.getBoundingClientRect()); if (hit(q)) e.style.visibility = "hidden"; else R.push(q); });
    (movers || []).forEach((e) => {
      e.style.translate = ""; if (!vis(e)) return; const r = e.getBoundingClientRect(), w = r.width + 6, h = r.height + 6;
      const offs = [[0, 0], [w, 0], [-w, 0], [0, -h], [0, h], [w, -h], [-w, -h], [w, h], [-w, h], [2 * w, 0], [-2 * w, 0], [0, 2 * h], [0, -2 * h], [2 * w, h], [-2 * w, -h]];
      for (const [dx, dy] of offs) { const q = { l: r.left + dx, r: r.right + dx, t: r.top + dy, b: r.bottom + dy }; if (!hit(q)) { if (dx || dy) e.style.translate = `${dx}px ${dy}px`; R.push(q); return; } }
      R.push(box(r));
    });
  }
  window.OGShell = { show, reveal, fit, scrollDock, declutter };
})();
