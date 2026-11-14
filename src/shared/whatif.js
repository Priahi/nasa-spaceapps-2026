/* "What if?" historical-case impact panel. Reads /shared/impact.json (copied at build time from
   submission/impact.json). If the file is missing or has no entry for this app, nothing is shown.
   Every figure comes from that file; the panel is labelled as an illustrative estimate. */
(function () {
  const ALIAS = { "sar-change": ["sar-change", "flood", "valencia", "sar"], hotspots: ["hotspots", "fire", "canada", "hot-spots"], "field-shift": ["field-shift", "field", "iowa", "crop", "crops"] };
  const slug = window.OG_SLUG || (location.pathname.split("/").filter(Boolean)[0] || "");
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const human = (k) => k.replace(/[_-]+/g, " ").replace(/^./, (c) => c.toUpperCase());
  const SKIP = new Set(["title", "case", "name", "slug", "app", "id", "label", "note", "disclaimer", "sources", "source", "src", "headline", "summary"]);
  function pick(d) {
    const keys = ALIAS[slug] || [slug]; const pools = [d, d && d.cases, d && d.apps, d && d.dashboards].filter(Boolean);
    for (const pool of pools) {
      if (Array.isArray(pool)) { const hit = pool.find((x) => x && keys.some((k) => [x.slug, x.app, x.id, x.key, x.module].map((v) => String(v || "").toLowerCase()).includes(k))); if (hit) return hit; }
      else for (const k of keys) if (pool[k] && typeof pool[k] === "object") return pool[k];
    }
    return null;
  }
  function val(v) {
    if (v == null) return "";
    if (Array.isArray(v)) return "<ul>" + v.map((x) => `<li>${typeof x === "object" ? val(x) : esc(x)}</li>`).join("") + "</ul>";
    if (typeof v === "object") {
      if ("value" in v || "v" in v) return `<b>${esc(v.value ?? v.v)}</b>${v.unit ? " " + esc(v.unit) : ""}${v.label || v.l ? ` <span>${esc(v.label || v.l)}</span>` : ""}${v.note ? ` <small>${esc(v.note)}</small>` : ""}`;
      return "<dl>" + Object.entries(v).map(([k, x]) => `<dt>${esc(human(k))}</dt><dd>${val(x)}</dd>`).join("") + "</dl>";
    }
    return esc(v);
  }
  function srcs(c) {
    const s = c.sources || c.source || c.src; if (!s) return "";
    const arr = Array.isArray(s) ? s : [s];
    return '<p class="wi-src">Sources: ' + arr.map((x) => typeof x === "string" ? (/^https?:/.test(x) ? `<a href="${esc(x)}" rel="noopener">${esc(x.replace(/^https?:\/\/(www\.)?/, "").split("/")[0])}</a>` : esc(x)) : (x.url ? `<a href="${esc(x.url)}" rel="noopener">${esc(x.name || x.label || x.url)}</a>` : esc(x.name || x.label || ""))).join(", ") + "</p>";
  }
  function render(c, d) {
    const title = c.title || c.case || c.name || c.headline || "Historical case";
    const rows = Object.entries(c).filter(([k, v]) => !SKIP.has(k) && v !== "" && v != null);
    const note = c.note || c.disclaimer || (d && (d.note || d.disclaimer)) || "";
    const sec = document.createElement("section");
    sec.className = "og-strip og-whatif"; sec.id = "whatif"; sec.setAttribute("aria-label", "What if? Historical case");
    sec.innerHTML = `<div class="wi-in"><p class="wi-tag">What if? · Illustrative estimate, not a measured result</p><h2>${esc(title)}</h2>${c.summary ? `<p class="wi-sum">${esc(c.summary)}</p>` : ""}`
      + `<div class="wi-grid">${rows.map(([k, v]) => `<div class="wi-cell"><p class="wi-k">${esc(human(k))}</p><div class="wi-v">${val(v)}</div></div>`).join("")}</div>`
      + `<p class="wi-fine">${note ? esc(note) + " " : ""}A rule-of-thumb estimate (see sources), applied to a past event. It is not a forecast and not a claim of lives saved. Alerts and tasking in this dashboard are simulated.</p>${srcs(c)}</div>`;
    const work = document.querySelector(".og-work"); if (!work) return;
    const after = work.nextElementSibling && work.nextElementSibling.id === "calendar" ? work.nextElementSibling : work;
    after.insertAdjacentElement("afterend", sec);
    const bar = document.querySelector(".og-bar, .ops-bar, header .og-actions");
    if (bar && !document.getElementById("whatifLink")) { const a = document.createElement("a"); a.id = "whatifLink"; a.className = "og-b"; a.href = "#whatif"; a.textContent = "What if? ↓"; a.addEventListener("click", (ev) => { ev.preventDefault(); sec.scrollIntoView({ behavior: "smooth", block: "start" }); }); bar.appendChild(a); }
  }
  function go() {
    if (!window.OG_IMPACT) return; // build found no submission/impact.json: stay hidden (and avoid a 404 in the console)
    fetch("/shared/impact.json", { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)).then((d) => { const c = d && pick(d); if (c) render(c, d); }).catch(() => {});
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
})();
