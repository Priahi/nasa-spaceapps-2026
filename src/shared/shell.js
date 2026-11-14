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
  /* scroll an element to the top of its dock body without moving the page (desktop); on narrow screens scroll the page */
  function scrollDock(el) {
    if (!el) return; reveal(el); const body = el.closest(".og-dock-body");
    if (body && getComputedStyle(body).overflowY === "auto") { body.scrollTop += el.getBoundingClientRect().top - body.getBoundingClientRect().top - 8; }
    /* narrow screens: leave the page where it is, so the map stays in view */
  }
  window.OGShell = { show, reveal, fit, scrollDock };
})();
