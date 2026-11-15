/* "What if?" historical-case panel. Reads /shared/impact.json (built from submission/impact.json, written from
   submission/IMPACT.md, plus src/impact_view.json for comparison rows and links). Hidden when the file is missing.
   Illustrative estimates only: no lives-saved claims, and the avoided-damage curve flattens after ~24 h. */
(function () {
  const KEY = { "sar-change": "flood", hotspots: "fire", "field-shift": "field" }[window.OG_SLUG || ""];
  // Story times are shown rounded, in 12-hour time ("20:11" -> "about 8 PM", "11:45" -> "around noon").
  // Exact times stay in the cited sources. Relative T+ times and ISO stamps are left alone.
  const NAMED = { "07:36": "about 7:30 AM", "07:23": "about 7:30 AM", "11:45": "around noon", "12:07": "around noon" };
  const round = (h, mi) => { const k = `${String(h).padStart(2, "0")}:${mi}`; if (NAMED[k]) return NAMED[k]; let H = +h + (+mi >= 30 ? 1 : 0); H %= 24; return H === 12 ? "around noon" : H === 0 ? "around midnight" : `about ${(H % 12) || 12} ${H < 12 ? "AM" : "PM"}`; };
  const t12 = (s) => String(s).replace(/(^|[^\d+:T])([01]?\d|2[0-3]):([0-5]\d)(?![\d:])(?!\s?[AP]M)/g, (m, p, h, mi) => p + round(h, mi))
    .replace(/before at least (\d+) of the (\d+) pre-about (\d+ [AP]M) deaths/g, "before nearly all of the deaths dated before about $3").replace(/([AP]M|noon) (\d{1,2} [A-Z][a-z]{2})/g, "$1, $2")
    // safety net: never show a doubled AM/PM suffix; when two stack up, the last one is the source's own
    .replace(/\b(?:[AP]M\s*)+([AP]M)\b/g, "$1").replace(/\bnoon\s+[AP]M\b/g, "noon").replace(/\bpre-(about|around) /g, "before $1 ");
  const esc = (s) => t12(String(s == null ? "" : s)).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const pct = (f) => `${Math.round(f * 1000) / 10}%`;
  const n = (x) => Number(x).toLocaleString("en-US");
  const kpi = (b, l) => `<div class="wi-kpi"><b>${b}</b><span>${l}</span></div>`;
  const table = (head, rows) => `<div class="wi-tw"><table class="wi-t"><thead><tr>${head.map((h) => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  const compare = (v) => (v && v.compare ? `<h3>How it compares with what exists today</h3><div class="wi-cmp">${v.compare.map(([a, b, c]) => `<div class="wi-cell"><p class="wi-k">${esc(a)}</p><p>${esc(b)}</p><p class="wi-us"><b>Orbit to Ground:</b> ${esc(c)}</p></div>`).join("")}</div>` : "");
  const sources = (v) => (v && v.sources ? `<div class="wi-src"><span>Sources:</span><ul>${v.sources.map(([l, u]) => `<li><a href="${esc(u)}" rel="noopener">${esc(l)}</a></li>`).join("")}</ul></div>` : "");

  function flood(c) {
    const B = c.baseline;
    let h = `<div class="wi-kpis">${kpi("hours", "earlier alert: the danger was known (red warning " + esc(B.red_warning) + "); the gap was turning it into a town-specific alert")}${kpi("~2 days", "earlier map: the rain signal arrives before the first radar map (31 Oct); ~4 days before the Copernicus EMS extent map (2 Nov)")}${kpi("more than " + Math.floor(B.died_before_alert / 10) * 10, "of about " + Math.round(B.deaths / 10) * 10 + " people who died had died before the phone alert at about 8 PM; first recorded death " + esc(B.first_death))}</div>`;
    h += `<h3>If the alert had gone out earlier (damage only, upper bound)</h3>`;
    h += table(["Alert", "Clock time", "When it lands", "Avoided-damage factor", `× €${B.insured_cost_eur_bn} bn insured`], c.scenarios.map((s) => [
      `<b>${s.hours_earlier} h earlier</b>`, esc(s.alert_time), esc(s.people),
      `${pct(s.factor)}${s.factor_range ? ` (${pct(s.factor_range[0])}–${pct(s.factor_range[1])})` : ""}<small>${esc(s.factor_source)}</small>`,
      `<b>€${s.avoided_insured_eur_bn} bn</b>${s.avoided_insured_range_eur_bn ? ` <small>(€${s.avoided_insured_range_eur_bn[0]}–${s.avoided_insured_range_eur_bn[1]} bn)</small>` : ""}`]));
    h += `<p class="wi-fine">The published curve flattens after about a day: 30% at 24 h, 4–40% at 48 h. It is <b>not</b> 30% for each extra 24 h. The 24 h and 48 h rows rely on forecasts (AEMET, EFAS), which our tool doesn't make. Upper bound: assumes everyone got the alert and acted, and much of the bill can't be moved out of the water. Floor (domestic property only): ${pct(c.floor_domestic_only.factor)}, €${c.floor_domestic_only.avoided_insured_eur_bn} bn.</p>`;
    const AFF = 190000; // people potentially affected, Copernicus EMS extent map via ESA (IMPACT.md F8)
    h += `<p class="wi-fine"><b>Per person.</b> The €${B.insured_cost_eur_bn} bn insured loss is about €${n(Math.round(B.insured_cost_eur_bn * 1e9 / AFF / 1000) * 1000)} for each of the ~${n(AFF)} people potentially affected (ESA); the 12 h row (€${c.scenarios[1].avoided_insured_eur_bn} bn) is about €${n(Math.round(c.scenarios[1].avoided_insured_eur_bn * 1e9 / AFF / 100) * 100)} each.</p>`;
    h += `<p class="wi-fine"><b>Lives.</b> We give no lives number for Valencia. An earlier alert means people reached before the water, not lives saved. ${esc(c.lives_context)}</p>`;
    return h;
  }
  // Province areas (km²), Statistics Canada table 15.6
  const PEI = 5660, NS = 55284;
  const times = (ha, km2) => { const x = ha / 100 / km2; return x >= 1.95 ? `${(Math.round(x * 10) / 10)} times` : x >= 0.9 ? "about" : `${Math.round(x * 100)}% of`; };
  function fire(c) {
    const B = c.baseline;
    let h = `<div class="wi-kpis">${kpi("months ahead", "the harmonized record flags May as Alberta's watch month in winter, before the season")}${kpi("+" + c.readiness_days_gained[0].days_with_15_apr_staffing + " days", "of full readiness in 2016 with staffing on 15 April instead of 1 May")}${kpi("~" + n(Math.round(c.per_escape_ha / 1000) * 1000) + " ha", "spared per escaped fire prevented (" + n(Math.round(c.per_escape_ha / 100)) + " km², " + times(c.per_escape_ha, PEI) + " Prince Edward Island; Alberta 2023 average; illustrative)")}</div>`;
    h += `<h3>Readiness across the whole season</h3>`;
    h += table(["Season", "First big fire", "Full readiness first, with 15 April staffing"], c.readiness_days_gained.map((r) => [`<b>${r.season}</b>`, esc(r.first_big_fire), `<b>${r.days_with_15_apr_staffing} days</b>`]));
    h += table(["Escapes prevented (assumption)", "Area not burned", "Share of the 2023 season"], c.scenarios.map((s) => [`<b>${s.escapes_prevented}</b>`, `~${n(Math.round(s.ha / 1000) * 1000)} ha <small>${n(Math.round(s.ha / 100))} km² · ${times(s.ha, PEI)} P.E.I.</small>`, pct(s.share)]));
    h += `<p class="wi-fine">For scale: Horse River (May 2016) burned about ${n(Math.round(B.horse_river_ha / 10000) * 10000)} ha (about ${n(Math.round(B.horse_river_ha / 100 / 100) * 100)} km², ${times(B.horse_river_ha, PEI)} the size of Prince Edward Island), moved ${n(B.evacuated_2016)} people and cost $${B.insured_cad_bn} bn insured, about $${B.total_cad_bn} bn in total: roughly $${n(Math.round(B.total_cad_bn * 1e9 / B.evacuated_2016 / 1000) * 1000)} per person evacuated. Alberta 2023: ${(B.ab_2023_ha / 1e6).toFixed(1)} M ha, ${times(B.ab_2023_ha, PEI)} Prince Edward Island. Canada 2023: ${(B.canada_2023_ha / 1e6).toFixed(1)} M ha, ${times(B.canada_2023_ha, NS)} the area of Nova Scotia. Escape rule: ${esc(B.escape_rule)}. ${esc(c.caveat)} The value is readiness across the season, not stopping one fire.</p>`;
    return h;
  }
  function field(c) {
    const B = c.baseline, S = c.scenario;
    let h = `<div class="wi-kpis">${kpi("before planting", "next-season map per 30 m pixel about February; the season's own crop map arrives ~11 months later")}${kpi("~$" + S.net_usd_m.toFixed(1) + " M", "net in a 2012-type drought for rye on the 92 steepest squares (" + n(S.acres) + " acres; illustrative)")}${kpi(B.iowa_corn_yield_2011 + " → " + B.iowa_corn_yield_2012, "Iowa corn, bu/acre, 2011 → 2012 drought (about $" + B.iowa_shortfall_usd_bn + " bn shortfall, roughly $" + n(Math.round(B.iowa_shortfall_usd_bn * 1e9 / 3046355 / 10) * 10) + " per Iowan, 2010 Census)")}</div>`;
    h += `<h3>Rye on the steep fields works like drought insurance</h3>`;
    h += table(["Item", "Per acre", `× ${n(S.acres)} acres`], [
      ["Extra corn in a 2012-type drought (+" + B.cover_crop_corn_gain_bu + " bu × $" + B.price_usd_bu_2012 + ")", "+$" + S.gross_per_acre, "+$" + S.gross_usd_m + " M"],
      ["Cover-crop cost (seed + planting, Iowa mean)", "−$" + B.cover_crop_cost_usd_acre, "−$" + (S.gross_usd_m - S.net_usd_m).toFixed(2) + " M"],
      ["<b>Net in a drought year</b>", "<b>+$" + S.net_per_acre + "</b>", "<b>+$" + S.net_usd_m + " M</b>"],
      ["In a normal year", esc(S.normal_year), "–"]]);
    h += `<p class="wi-fine">It costs a little in most years and pays in drought years. The +${B.cover_crop_corn_gain_bu} bu/acre is a self-reported national farmer survey (SARE 2012), not a trial; Iowa results will differ. ${esc(c.lead_time)}</p>`;
    return h;
  }
  function render(d) {
    const c = d[KEY]; if (!c) return; const v = (d._view || {})[KEY];
    const body = KEY === "flood" ? flood(c) : KEY === "fire" ? fire(c) : field(c);
    const sec = document.createElement("section");
    sec.className = "og-strip og-whatif"; sec.id = "whatif"; sec.setAttribute("aria-label", "What if? Historical case");
    sec.innerHTML = `<div class="wi-in"><p class="wi-tag">What if? · Illustrative estimate, not a measured result</p><h2>${esc(c.case)}</h2><p class="wi-sum">${esc(c.headline)}</p>${body}${compare(v)}`
      + `<p class="wi-fine">${esc(d._note || "")}</p>${sources(v)}</div>`;
    const work = document.querySelector(".og-work"); if (!work) return;
    const after = work.nextElementSibling && work.nextElementSibling.id === "calendar" ? work.nextElementSibling : work;
    after.insertAdjacentElement("afterend", sec);
    const bar = document.querySelector(".og-bar, .ops-bar");
    if (bar && !document.getElementById("whatifLink")) { const a = document.createElement("a"); a.id = "whatifLink"; a.className = "og-b"; a.href = "#whatif"; a.textContent = "What if? ↓"; a.addEventListener("click", (ev) => { ev.preventDefault(); sec.scrollIntoView({ behavior: "smooth", block: "start" }); }); bar.appendChild(a); }
    if (/whatif/.test(location.hash)) setTimeout(() => sec.scrollIntoView({ block: "start" }), 600);
  }
  function go() {
    if (!window.OG_IMPACT || !KEY) return; // no submission/impact.json at build time: stay hidden (and no 404 in the console)
    fetch("/shared/impact.json", { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)).then((d) => { if (d) render(d); }).catch(() => {});
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
})();
