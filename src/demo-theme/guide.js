/* Guided steps inside each dashboard: See the map → What changed → Actions → Impact.
   Data comes from guide-data.js (generated at build from src/recs.py). Leaves the dashboard's own controls untouched. */
(function () {
  const D = window.OG_GUIDE, S = window.OG_SLUG; if (!D || !D[S]) return;
  const G = D[S], inFrame = window.self !== window.top, wide = () => window.innerWidth >= 1180;
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const STEPS = ["See the map", "What changed", "Actions", "Impact"];
  let cur = 0;
  const el = document.createElement("aside");
  el.className = "og-guide"; el.setAttribute("aria-label", "Guided steps");
  el.innerHTML = `<div class="og-top"><button class="og-toggle" type="button" aria-expanded="true"><span class="og-dot"></span><span class="og-tl">Guide</span><span class="og-st"></span><span class="og-car" aria-hidden="true">▾</span></button></div>
  <ol class="og-steps">${STEPS.map((t, i) => `<li><button type="button" data-i="${i}"><span>${i + 1}</span>${t}</button></li>`).join("")}</ol>
  <div class="og-panel" tabindex="-1"></div>
  <div class="og-nav"><button type="button" class="og-prev">← Back</button><button type="button" class="og-next">Next →</button></div>`;
  document.body.appendChild(el);
  const panel = el.querySelector(".og-panel");

  function run(cmd) {
    if (!cmd) return;
    const [k, v] = [cmd.slice(0, cmd.indexOf(":")), cmd.slice(cmd.indexOf(":") + 1)];
    const tab = (id) => { const b = document.querySelector(`nav.tabs button[data-tab="${id}"]`); if (b) b.click(); };
    if (k === "preset") { const s = document.getElementById("preset"); if (s && [...s.options].some((o) => o.value === v)) { s.value = v; s.dispatchEvent(new Event("change", { bubbles: true })); } const m = document.getElementById("map"); if (m) m.scrollIntoView({ behavior: "smooth", block: "center" }); }
    if (k === "tab") { tab(v); const p = document.getElementById("panel-" + v); if (p) p.scrollIntoView({ behavior: "smooth", block: "start" }); }
    if (k === "scroll" || k === "click") {
      const sel = k === "click" ? v.split(" ")[0] : v; const t = document.querySelector(sel); if (!t) return;
      const pn = t.closest("section.panel"); if (pn && !pn.classList.contains("active")) tab(pn.id.replace("panel-", ""));
      if (k === "click") { const bs = document.querySelectorAll(v); const b = bs[1] || bs[0]; if (b) b.click(); }
      setTimeout(() => t.scrollIntoView({ behavior: "smooth", block: "center" }), 60);
    }
    if (!wide()) collapse(true);
  }
  const btn = (b) => b ? `<button type="button" class="og-do" data-cmd="${esc(b[1])}">${esc(b[0])}</button>` : "";
  const recHTML = (r) => `<article class="og-rec"><img src="/assets/img/${esc(r.img)}" alt="" loading="lazy" /><div><span class="og-cls">${esc(r.cls)}</span>
    <p class="og-sat"><b>Satellite shows</b>${esc(r.sat)}</p><p class="og-act"><b>I will</b>${esc(r.act)}</p><p class="og-out"><b>Expected</b>${esc(r.out)}</p></div></article>`;
  function render() {
    el.querySelectorAll(".og-steps button").forEach((b, i) => { b.classList.toggle("on", i === cur); b.classList.toggle("done", i < cur); b.setAttribute("aria-current", i === cur ? "step" : "false"); });
    el.querySelector(".og-st").textContent = `Step ${cur + 1} of 4 · ${STEPS[cur]}`;
    el.querySelector(".og-prev").disabled = cur === 0;
    el.querySelector(".og-next").textContent = cur === 3 ? "Start again ↺" : "Next →";
    let h = "";
    if (cur === 0) h = `<p class="og-k">${esc(G.role)} · ${esc(G.who)}</p><h2>See the map</h2><p>${esc(G.guide.map)}</p>${btn(G.guide.map_btn)}`;
    if (cur === 1) h = `<p class="og-k">From orbit</p><h2>What changed</h2><ul class="og-shows">${G.shows.map((x) => `<li><strong>${esc(x.big)}</strong><span>${esc(x.line)}</span></li>`).join("")}</ul><p>${esc(G.guide.changed)}</p>${btn(G.guide.changed_btn)}`;
    if (cur === 2) h = `<p class="og-k">On the ground</p><h2>Recommended actions</h2><div class="og-recs">${G.recs.map(recHTML).join("")}</div><p class="og-fine">Photos are illustrative (AI-generated). Outcomes are qualitative.</p>`;
    if (cur === 3) h = `<p class="og-k">Two sides</p><h2>Impact</h2><div class="og-imp"><div><p class="og-k">What the satellites found</p>${G.impact.tech.map((t) => `<p><b>${esc(t[0])}</b> ${esc(t[1])}</p>`).join("")}</div>
      <div><p class="og-k">What changes for people</p>${G.impact.human.map((t) => `<p><b>${esc(t[0])}</b> ${esc(t[1])}</p>`).join("")}</div></div>
      <ul class="og-m">${G.metrics.map((m) => `<li class="${m.neg ? "neg" : ""}"><strong>${esc(m.v)}</strong><span>${esc(m.t)}</span></li>`).join("")}</ul><p class="og-fine">One seed per run, not a published benchmark.</p>
      <a class="og-do" href="${G.page}" target="_top">The full story →</a>`;
    panel.innerHTML = h; panel.scrollTop = 0;
    panel.querySelectorAll("[data-cmd]").forEach((b) => b.addEventListener("click", () => run(b.dataset.cmd)));
  }
  function collapse(c) {
    el.classList.toggle("closed", c); el.querySelector(".og-toggle").setAttribute("aria-expanded", String(!c));
    document.documentElement.classList.toggle("og-open", !c && wide());
    setTimeout(() => window.dispatchEvent(new Event("resize")), 260);
  }
  el.querySelector(".og-toggle").addEventListener("click", () => collapse(!el.classList.contains("closed")));
  el.querySelectorAll(".og-steps button").forEach((b) => b.addEventListener("click", () => { cur = +b.dataset.i; render(); if (el.classList.contains("closed")) collapse(false); }));
  el.querySelector(".og-prev").addEventListener("click", () => { if (cur > 0) { cur--; render(); } });
  el.querySelector(".og-next").addEventListener("click", () => { cur = cur === 3 ? 0 : cur + 1; render(); });
  window.addEventListener("resize", () => document.documentElement.classList.toggle("og-open", !el.classList.contains("closed") && wide()));
  render(); collapse(inFrame || !wide());
})();
