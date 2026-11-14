/* Field Shift dashboard: pick a field -> set priorities -> choose a 4-year plan -> act (simulated tasking) -> impact.
   Same-origin data only: data/app_data.json (squares, plans, indicators, climate) and data/colab_run/results.json (model metrics).
   Ranking is the original weighted score: mean over the five indicators of (1 - value) or value (nitrogen), weighted by priority. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const BASE_YEAR = 2026;
  const state = { data: null, colab: null, fieldId: null, weights: {}, mapImg: null, layer: "crops", planId: null, showAll: false,
    marks: { plan: new Set(), scout: false, cover: false }, c2: null, c2Actions: null, hover: null, fromHash: false };

  /* ---------- crops: names, colours (same as the CDL map image), icons ---------- */
  const ICON = {
    corn: '<path d="M12 3c2.6 0 4 3.2 4 7.2S14.6 18.8 12 21c-2.6-2.2-4-6.8-4-10.8S9.4 3 12 3z"/><path d="M10 7.5h4M9.4 11h5.2M9.8 14.5h4.4"/>',
    soy: '<path d="M5 19c-1-7 5-14 14-14 1 7-5 14-14 14z"/><circle cx="9.5" cy="14.5" r="1.3"/><circle cx="12.5" cy="11.5" r="1.3"/><circle cx="15.5" cy="8.5" r="1.3"/>',
    hay: '<rect x="3" y="7" width="18" height="11" rx="2.5"/><path d="M8.5 7v11M15.5 7v11"/>',
    grass: '<path d="M5 20c1.5-4.5 2-9 2-14M11 20c0-4.5 1-8 3.5-12M17 20c0-3.5 1.5-6.5 4-8.5M2 20h20"/>',
    other_crop: '<path d="M12 21V9"/><path d="M12 9c-2-1-3-3-3-5.5 2 .3 3 2.3 3 5.5zM12 9c2-1 3-3 3-5.5-2 .3-3 2.3-3 5.5zM12 14c-2.5-.6-4-2.4-4-4.6 2.4.5 4 2.1 4 4.6zM12 14c2.5-.6 4-2.4 4-4.6-2.4.5-4 2.1-4 4.6zM12 19c-2.5-.6-4-2.4-4-4.6 2.4.5 4 2.1 4 4.6zM12 19c2.5-.6 4-2.4 4-4.6-2.4.5-4 2.1-4 4.6z"/>',
    non_ag: '<path d="M4 20h16M7 20v-6l5-4 5 4v6"/>',
    cover: '<path d="M12 21v-8"/><path d="M12 13c0-4-3-6.5-7-6.5 0 4 3 6.5 7 6.5zM12 13c0-4 3-6.5 7-6.5 0 4-3 6.5-7 6.5z"/>',
  };
  const CROP = { corn: "Corn", soy: "Soybean", hay: "Hay", grass: "Grass / pasture", other_crop: "Small grain", non_ag: "Not farmed" };
  const COVER_C = "#2dd4bf";
  const ico = (k, cls = "fs-ico") => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${ICON[k] || ICON.non_ag}</svg>`;
  const color = (c) => (state.data.map.colors[c] || "#8b95ad");
  const split = (t) => ({ crop: t.replace("+cover", ""), cover: t.endsWith("+cover") });
  const cropLabel = (t) => { const s = split(t); return CROP[s.crop] + (s.cover ? " + winter rye" : ""); };

  function chip(token, year, opts = {}) {
    const s = split(token);
    return `<span class="fs-chip${opts.guess ? " guess" : ""}${opts.small ? " sm" : ""}" style="--c:${color(s.crop)}" title="${esc(year + ": " + cropLabel(token))}">
      <span class="fs-chip-ic">${ico(s.crop)}</span><small>${year}${opts.guess ? " guess" : ""}</small><b>${esc(CROP[s.crop])}</b>${s.cover ? `<em style="--cc:${COVER_C}">${ico("cover", "fs-ico xs")}+ rye</em>` : ""}${opts.extra ? `<em class="pc">${esc(opts.extra)}</em>` : ""}</span>`;
  }
  const seqChips = (seq) => `<div class="fs-seq">${seq.map((t, i) => chip(t, BASE_YEAR + i)).join('<span class="fs-arr" aria-hidden="true">→</span>')}</div>`;
  const seqText = (seq) => seq.map((t, i) => `${BASE_YEAR + i} ${cropLabel(t)}`).join(" → ");

  /* ---------- priorities: plain-language meaning, scale, and the formula from model-code/03-field-shift/scripts/run_model.py ---------- */
  const PRIO = {
    erosion_risk: { t: "Keep soil on the field", s: "Erosion risk", lower: true,
      what: "How exposed the soil is to washing away: the field's slope times the months the ground is bare.",
      scale: "Index, lower is better. Today's corn–soybean on a typical field scores about 0.22; adding winter rye cuts it to about 0.07.",
      how: "Each year: (slope in degrees ÷ 8) × (bare months ÷ 8), averaged over the four years. Bare months: corn or soybean 6, small grain 5, hay 1.5, grass 1, any crop followed by winter rye 2. Slope from NASA NASADEM.",
      lv: ["Ignored: erosion doesn't change the ranking.", "Counts the same as the other factors.", "Top priority: plans with fewer bare months rise, most of all on slopes."] },
    water_demand: { t: "Use less water", s: "Water demand", lower: true,
      what: "How thirsty the crops are across the four years, compared with a reference grass.",
      scale: "FAO-56 crop coefficient, from about 0.85 (grass every year) to 1.35 (corn + rye). Lower is better. A relative index, not litres.",
      how: "Average of each year's mid-season crop coefficient: corn 1.20, soybean 1.05, small grain 1.00, hay 0.95, grass 0.85, plus 0.15 when winter rye follows the crop.",
      lv: ["Ignored: thirsty crops aren't penalised.", "Counts the same as the other factors.", "Top priority: less thirsty crops rise."] },
    soil_moisture_stress: { t: "Ride out dry spells", s: "Drought stress", lower: true,
      what: "How much the crops would suffer when the root zone is dry, at this county's recent soil wetness.",
      scale: "Index from 0 (no stress) up. Lower is better. Corn–soybean scores about 0.20 here.",
      how: "Each year: the crop's drought sensitivity (corn 0.8, soybean 0.7, small grain 0.6, hay 0.5, grass 0.4) × how far NASA POWER root-zone wetness (median of the last ten years) sits below 0.65. Averaged over the four years.",
      lv: ["Ignored: drought sensitivity doesn't count.", "Counts the same as the other factors.", "Top priority: hardier crops rise."] },
    n_fixing_share: { t: "Grow your own nitrogen", s: "Nitrogen from legumes", lower: false,
      what: "The share of years in crops that put nitrogen back into the soil.",
      scale: "0 to 1, higher is better. Corn–soybean scores 0.5.",
      how: "Average over four years of: soybean 1, hay 0.6 (alfalfa or mixed hay), grass 0.2, small grain 0.15, corn 0. Not a fertiliser recommendation.",
      lv: ["Ignored.", "Counts the same as the other factors.", "Top priority: more soybean and hay years rise."] },
    heat_frost_exposure: { t: "Avoid heat and frost", s: "Heat and frost", lower: true,
      what: "Risk of a season too short for the crop, spring frost, and very hot days.",
      scale: "0 to 1, lower is better.",
      how: "0.45 × growing-degree-day shortfall for the crop + 0.30 × (spring frost days ÷ 20, capped at 1) + 0.25 × (days at or above 32 °C ÷ 20, capped at 1), from NASA POWER ten-year medians.",
      lv: ["Ignored.", "Counts the same as the other factors.", "Top priority."] },
  };
  const MAIN = ["erosion_risk", "water_demand", "soil_moisture_stress"], MORE = ["n_fixing_share", "heat_frost_exposure"];
  const LEVELS = ["Ignore", "Matters", "Top priority"];

  /* ---------- scoring (unchanged from the original tool) ---------- */
  const fieldById = (id) => state.data.fields.find((f) => f.id === id);
  const curField = () => (state.fieldId ? fieldById(state.fieldId) : null);
  function weightedScore(ind, w) {
    const sense = state.data.objectives.sense; let s = 0, n = 0;
    for (const k of state.data.objectives.keys) { const u = sense[k] === "max" ? ind[k] : 1 - ind[k]; const wt = w[k] ?? 1; s += wt * u; n += wt; }
    return n ? s / n : 0;
  }
  const median = (arr) => { const a = arr.filter(Number.isFinite).sort((x, y) => x - y); return a.length ? a[Math.floor(a.length / 2)] : 1; };
  let TYP_SLOPE = 1;
  const NAMED = {
    current_corn_soy: { name: "Today's corn–soybean", tag: "What most fields do now" },
    diversified_small_grain_hay: { name: "Corn, soybean, small grain, hay", tag: "Diversified" },
    cover_crop_conservation: { name: "Corn–soybean + winter rye", tag: "Conservation" },
  };
  function autoName(seq) {
    const base = seq.map((t) => split(t).crop), cover = seq.some((t) => split(t).cover);
    const uniq = [...new Set(base)], cnt = (c) => base.filter((x) => x === c).length;
    let n;
    if (uniq.length === 1) n = `${CROP[uniq[0]]}, all four years`;
    else { const top = uniq.slice().sort((a, b) => cnt(b) - cnt(a)); n = cnt(top[0]) >= 3 ? `Mostly ${CROP[top[0]].toLowerCase()}, one year ${CROP[top[1]].toLowerCase()}` : top.map((c, i) => (i ? CROP[c].toLowerCase() : CROP[c])).join(" and "); }
    return n + (cover ? " + winter rye" : "");
  }
  const backToBack = (seq) => seq.some((t, i) => i > 0 && ["corn", "soy"].includes(split(t).crop) && split(t).crop === split(seq[i - 1]).crop);
  function indForField(opt, field) {
    if (opt.kind === "named") { const st = opt.src; return field && st.field_indicators && st.field_indicators[field.id] ? st.field_indicators[field.id] : st.county_indicators; }
    const p = opt.src; let ind = { water_demand: p.water_demand, erosion_risk: p.erosion_risk, n_fixing_share: p.n_fixing_share, heat_frost_exposure: p.heat_frost_exposure, soil_moisture_stress: p.soil_moisture_stress };
    if (field) ind = { ...ind, erosion_risk: Math.min(1, p.erosion_risk * (TYP_SLOPE > 0 ? field.slope / TYP_SLOPE : 1)) }; // same slope scaling as the original tool
    return ind;
  }
  let ALL_OPTS = [];
  function buildOptions() {
    const named = state.data.strategies.map((st) => ({ kind: "named", id: st.id, name: (NAMED[st.id] || {}).name || st.name, tag: (NAMED[st.id] || {}).tag || "", sequence: st.sequence, why: st.why, benefits: st.benefits, risks: st.risks, gaps: st.gaps, src: st }));
    const used = new Set(named.map((s) => s.sequence.join("|")));
    const extra = [];
    const add = (arr, which) => (arr || []).forEach((p) => { const key = which + ":" + p.sequence.join("|"); if (used.has(key) || used.has(p.sequence.join("|"))) return; used.add(key);
      extra.push({ kind: "search", id: "s_" + key, which, name: autoName(p.sequence), tag: "Found by the trade-off search", sequence: p.sequence, skip: backToBack(p.sequence), mset: p.sequence.slice().sort().join("|"),
        why: "A four-year plan from the NSGA-II trade-off search: no other plan beats it on every factor at once.",
        benefits: "Sits on the trade-off front for the five factors.", risks: "Treat it as a prompt for your agronomist, not a prescription.", gaps: "Yields, labour, markets and equipment are not modelled.", src: p }); });
    add(state.data.pareto.typical_field, "typical"); add(state.data.pareto.steepest_field, "steepest");
    ALL_OPTS = named.concat(extra);
  }
  function optionsFor(field, w = state.weights) {
    const steep = field && field.id === state.data.pareto.steepest_field_id;
    const named = ALL_OPTS.filter((o) => o.kind === "named").map((o) => ({ ...o, indicators: indForField(o, field) }));
    let search = ALL_OPTS.filter((o) => o.kind === "search" && o.which === (steep ? "steepest" : "typical") && !o.skip).map((o) => ({ ...o, indicators: indForField(o, field) }));
    named.concat(search).forEach((o) => { o.score = weightedScore(o.indicators, w); });
    search.sort((a, b) => b.score - a.score);
    const seen = new Set(); search = search.filter((o) => (seen.has(o.mset) ? false : (seen.add(o.mset), true))).slice(0, 3);
    return named.concat(search).sort((a, b) => b.score - a.score);
  }

  /* ---------- step 1: field ---------- */
  const FEAT = { T3106: "Steepest field", T1730: "Flattest field", T0119: "Surest forecast", T1821: "Least sure forecast", T0216: "Most bare soil", T0102: "Hay and grass field" };
  function renderFeatured() {
    const items = [{ id: "", label: "County typical", reason: "Median slope and soils" }].concat((state.data.featured || []).map((f) => ({ id: f.id, label: FEAT[f.id] || f.id, reason: f.reason })));
    $("featured").innerHTML = items.map((b) => `<button type="button" data-id="${b.id}" title="${esc(b.reason)}" aria-pressed="${(b.id || null) === state.fieldId}">${esc(b.label)}</button>`).join("");
    $("featured").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => selectField(b.dataset.id || null)));
  }
  const ha = (f) => Math.round(f.n_pixels * 0.09); // farmed 30 m pixels x 0.09 ha
  function renderField() {
    const f = curField();
    $("fieldTitle").textContent = f ? `Field square ${f.id}` : "County typical field";
    $("fieldTag").textContent = f ? (FEAT[f.id] || "") : "Median slope and soils";
    $("fieldTag").hidden = !$("fieldTag").textContent;
    if (!f) {
      $("fieldMeta").innerHTML = `<div><b>${TYP_SLOPE.toFixed(1)}°</b><span>median slope</span></div><div><b>${state.data.fields.length}</b><span>squares in the county</span></div>`;
      $("history").innerHTML = `<p class="fs-fine">Pick a square on the map to see its crop history.</p>`; $("flags").innerHTML = ""; return;
    }
    $("fieldMeta").innerHTML = `<div><b>${f.slope.toFixed(1)}°</b><span>slope${f.slope > TYP_SLOPE * 1.25 ? " · steep" : ""}</span></div>
      <div><b>${ha(f)} ha</b><span>farmed (${Math.round(ha(f) * 2.471)} acres)</span></div>
      <div><b>${f.clay.toFixed(0)}% clay</b><span>${f.sand.toFixed(0)}% sand · pH ${f.ph.toFixed(1)}</span></div>
      <div><b>${f.ndvi_peak_2024 != null ? f.ndvi_peak_2024.toFixed(2) : "n/a"}</b><span>peak greenness 2024</span></div>`;
    const hist = f.history.slice(-6);
    $("history").innerHTML = hist.map((h) => chip(h.crop, h.year, { small: true })).join("") + `<span class="fs-arr" aria-hidden="true">→</span>` + chip(f.pred_2026, 2026, { small: true, guess: true, extra: Math.round(f.pred_confidence * 100) + "% sure" });
    $("flags").innerHTML = (f.flags || []).map((t) => `<p class="fs-flag">${esc(t)}</p>`).join("");
  }

  /* ---------- step 2: priorities ---------- */
  function prioHTML(k) {
    const P = PRIO[k], v = state.weights[k], li = Math.round(v / 50);
    const same = k === "heat_frost_exposure" && state.heatFlat ? `<p class="fs-note">Every plan scores ${state.heatFlat} here today, so this factor doesn't change the ranking.</p>` : "";
    return `<div class="fs-prio" data-k="${k}">
      <div class="fs-prio-top"><div><h3>${esc(P.t)}</h3><p class="fs-prio-s">${esc(P.s)} · ${P.lower ? "lower is better" : "higher is better"}</p></div>
        <button type="button" class="fs-i" aria-expanded="false" aria-controls="tip-${k}" title="What this means">i</button></div>
      <input type="range" min="0" max="100" step="50" value="${v}" data-key="${k}" aria-label="${esc(P.t)}: how much it matters" aria-valuetext="${LEVELS[li]}">
      <div class="fs-ticks" aria-hidden="true">${LEVELS.map((l, i) => `<span class="${i === li ? "on" : ""}">${l}</span>`).join("")}</div>
      <p class="fs-prio-eff" id="eff-${k}">${esc(P.lv[li])}</p>
      <div class="fs-tip" id="tip-${k}" hidden><p><b>What it is.</b> ${esc(P.what)}</p><p><b>Scale.</b> ${esc(P.scale)}</p><p><b>How it's computed.</b> ${esc(P.how)}</p>${same}</div>
    </div>`;
  }
  function renderSliders() {
    $("sliders").innerHTML = MAIN.map(prioHTML).join(""); $("sliders2").innerHTML = MORE.map(prioHTML).join("");
    document.querySelectorAll(".fs-prio input").forEach((inp) => inp.addEventListener("input", () => {
      const k = inp.dataset.key, v = Number(inp.value); state.weights[k] = v; const li = Math.round(v / 50);
      inp.setAttribute("aria-valuetext", LEVELS[li]);
      inp.parentElement.querySelectorAll(".fs-ticks span").forEach((s, i) => s.classList.toggle("on", i === li));
      $("eff-" + k).textContent = PRIO[k].lv[li]; update();
    }));
    document.querySelectorAll(".fs-i").forEach((b) => b.addEventListener("click", () => { const t = $(b.getAttribute("aria-controls")); const o = t.hidden; t.hidden = !o; b.setAttribute("aria-expanded", String(o)); }));
  }

  /* ---------- step 3: plans ---------- */
  const DELTA_KEYS = ["erosion_risk", "water_demand", "soil_moisture_stress", "n_fixing_share"];
  function deltas(o, base) {
    return DELTA_KEYS.map((k) => {
      const a = o.indicators[k], b = base.indicators[k]; const pct = b ? (a - b) / b * 100 : 0;
      const good = PRIO[k].lower ? pct < -0.5 : pct > 0.5, bad = PRIO[k].lower ? pct > 0.5 : pct < -0.5;
      const txt = Math.abs(pct) < 0.5 ? "same" : (pct > 0 ? "+" : "−") + Math.abs(pct).toFixed(0) + "%";
      return `<li class="${good ? "good" : bad ? "bad" : ""}" title="${esc(PRIO[k].s)}: ${a.toFixed(3)} vs ${b.toFixed(3)} for today's corn–soybean"><span>${esc(PRIO[k].s)}</span><b>${txt}</b></li>`;
    }).join("");
  }
  function renderStrategies() {
    const field = curField(), opts = optionsFor(field), base = opts.find((o) => o.id === "current_corn_soy");
    if (!opts.some((o) => o.id === state.planId)) state.planId = opts[0].id;
    const shown = state.showAll ? opts : opts.slice(0, 4);
    if (!shown.some((o) => o.id === state.planId)) shown.push(opts.find((o) => o.id === state.planId));
    $("strategyCards").innerHTML = shown.map((o) => {
      const i = opts.indexOf(o), sel = o.id === state.planId, fit = Math.round(o.score * 100);
      return `<article class="fs-plan${sel ? " sel" : ""}${i === 0 ? " best" : ""}" data-id="${esc(o.id)}">
        <div class="fs-plan-top"><span class="fs-rank">${i === 0 ? "Best match" : "#" + (i + 1)}</span><span class="fs-ptag ${o.kind}">${esc(o.tag)}</span><span class="fs-fit" title="Fit for your priorities, out of 100"><b>${fit}</b> fit</span></div>
        <h3>${esc(o.name)}</h3>
        ${seqChips(o.sequence)}
        ${o.id === "current_corn_soy" ? `<p class="fs-fine">The baseline: other plans are compared with this one.</p>` : `<ul class="fs-delta" aria-label="Compared with today's corn–soybean">${deltas(o, base)}</ul>`}
        <details class="fs-why"><summary>Why, and the risks</summary><p>${esc(o.why)}</p><p><b>Benefits.</b> ${esc(o.benefits)}</p><p><b>Risks.</b> ${esc(o.risks)} ${esc(o.gaps)}</p></details>
        <div class="fs-plan-btns"><button type="button" class="fs-btn${sel ? " on" : ""}" data-pick="${esc(o.id)}" aria-pressed="${sel}">${sel ? "Selected · on the map" : "Choose this plan"}</button>
        ${sel ? `<a class="fs-btn primary" href="#pane-act">Act on it →</a>` : ""}</div>
      </article>`;
    }).join("") + (opts.length > 4 ? `<button type="button" class="fs-btn ghost fs-more-btn" id="morePlans">${state.showAll ? "Show fewer plans" : `Show ${opts.length - 4} more plans`}</button>` : "");
    $("strategyCards").querySelectorAll("[data-pick]").forEach((b) => b.addEventListener("click", () => pickPlan(b.dataset.pick)));
    const mb = $("morePlans"); if (mb) mb.addEventListener("click", () => { state.showAll = !state.showAll; renderStrategies(); });
    renderTable(opts);
  }
  function pickPlan(id) {
    state.planId = id; setLayer("fit"); renderStrategies(); renderPareto(); refreshC2();
    if (window.innerWidth < 1024) $("mapSec").scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function renderTable(opts) {
    const keys = state.data.objectives.keys;
    $("tradeTable").innerHTML = `<thead><tr><th>Plan</th><th>2026 → 2029</th><th class="num">Fit</th>${keys.map((k) => `<th class="num">${esc(PRIO[k].s)}</th>`).join("")}</tr></thead><tbody>` +
      opts.map((o) => `<tr class="${o.id === state.planId ? "sel" : ""}"><td>${esc(o.name)}</td><td>${esc(o.sequence.map(cropLabel).join(" → "))}</td><td class="num">${Math.round(o.score * 100)}</td>${keys.map((k) => `<td class="num">${o.indicators[k].toFixed(3)}</td>`).join("")}</tr>`).join("") + "</tbody>";
  }

  /* ---------- map + layers ---------- */
  const LAYERS = [{ id: "crops", t: "Crops 2025" }, { id: "forecast", t: "2026 forecast" }, { id: "fit", t: "Plan fit" }, { id: "erosion", t: "Slope" }, { id: "scout", t: "Scout list" }];
  const FLAG = { low: /Low model confidence/, slope: /Above-average slope/, repeat: /same cash crop/ };
  const FLAGC = { low: "#fbbf24", repeat: "#f87171", slope: "#d4c4ff" };
  const hasFlag = (f, k) => (f.flags || []).some((t) => FLAG[k].test(t));
  const flagKind = (f) => (hasFlag(f, "low") ? "low" : hasFlag(f, "repeat") ? "repeat" : hasFlag(f, "slope") ? "slope" : null);
  const SLOPE_RAMP = ["#1b2140", "#3b3a5c", "#7a5a3a", "#c98a3e", "#f3c27a"];
  let SLOPE_Q = [];
  function mix(a, b, t) { const p = (h) => [1, 3, 5].map((j) => parseInt(h.slice(j, j + 2), 16)); const A = p(a), B = p(b); return "#" + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, "0")).join(""); }
  function rampColor(r, t) { const x = Math.max(0, Math.min(0.9999, t)) * (r.length - 1), i = Math.floor(x); return mix(r[i], r[i + 1], x - i); }
  function slopeT(s) { let i = 0; while (i < SLOPE_Q.length && s > SLOPE_Q[i]) i++; return i / SLOPE_Q.length; }

  function renderLayers() {
    $("layers").innerHTML = LAYERS.map((l) => `<button type="button" role="radio" aria-checked="${l.id === state.layer}" data-layer="${l.id}">${esc(l.t)}</button>`).join("");
    $("layers").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => setLayer(b.dataset.layer)));
  }
  function setLayer(id) { state.layer = id; $("layers").querySelectorAll("button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.layer === id))); drawMap(); }

  let FIT = null;
  function computeFit() {
    // For the chosen plan, on each square: its score minus the best of the named plans, under your priorities.
    const plan = ALL_OPTS.find((o) => o.id === state.planId); if (!plan) return (FIT = null);
    const others = ALL_OPTS.filter((o) => o.kind === "named" && o.id !== plan.id);
    const m = {}; let win = 0;
    state.data.fields.forEach((f) => {
      const s = weightedScore(indForField(plan, f), state.weights);
      const best = Math.max(...others.map((o) => weightedScore(indForField(o, f), state.weights)));
      m[f.id] = s - best; if (s - best >= 0) win++;
    });
    FIT = { m, win, name: plan.name };
  }
  /* Leaflet map: USDA CDL 2025 reprojected to Web Mercator (data/geo.json) on a basemap, with the 1.2 km analysis squares as polygons. */
  let LM = null, SQ = {}, CDL = null, ASSETS = null, GEO = null, lastFit = null, userMoved = false;
  /* every programmatic view goes through fitTo(); until the user pans or zooms, a resize (layout settling, Farmer/Full switch) refits the same view */
  function fitTo(b, opts) { lastFit = [L.latLngBounds(b), Object.assign({ padding: [12, 12] }, opts || {})]; userMoved = false; LM.fitBounds(lastFit[0], Object.assign({}, lastFit[1], { animate: false })); }
  const SQ_BASE = { color: "rgba(7,9,26,.55)", weight: 0.6, opacity: 1, fillOpacity: 0, dashArray: null };
  function initMap(geo) {
    GEO = geo; if (window.OGShell) OGShell.fit();
    LM = L.map("map", { zoomControl: false, zoomSnap: 0.25, preferCanvas: true });
    L.control.zoom({ position: "bottomright" }).addTo(LM);
    const b = L.latLngBounds(geo.bounds); fitTo(b); LM.setMaxBounds(b.pad(0.6));
    let minSet = false; const setMin = () => { const r = $("map").getBoundingClientRect(); if (minSet || !r.width || !r.height) return; LM.setMinZoom(Math.max(0, Math.floor(LM.getBoundsZoom(b)) - 1)); minSet = true; }; setMin();
    ["mousedown", "wheel", "touchstart", "keydown", "dblclick"].forEach((ev) => $("map").addEventListener(ev, (e) => { if (!e.target.closest || !e.target.closest(".og-ovl, .leaflet-control")) userMoved = true; }, { passive: true }));
    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", { attribution: "Tiles &copy; Esri · Crops: USDA NASS CDL 2025", maxZoom: 16 }).addTo(LM);
    LM.createPane("labels"); LM.getPane("labels").style.zIndex = 650; LM.getPane("labels").style.pointerEvents = "none";
    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}", { pane: "labels", maxZoom: 16 }).addTo(LM);
    CDL = L.imageOverlay(geo.image, b, { className: "fs-cdl", interactive: false }).addTo(LM);
    const rend = L.canvas({ padding: 0.3 });
    state.data.fields.forEach((f) => {
      const c = geo.squares[f.id]; if (!c) return;
      const pg = L.polygon(c, Object.assign({ renderer: rend, bubblingMouseEvents: false }, SQ_BASE)).addTo(LM);
      pg.on("click", () => selectField(f.id));
      pg.on("mouseover", () => { state.hover = f.id; styleSq(f); }); pg.on("mouseout", () => { state.hover = null; styleSq(f); });
      pg.bindTooltip(() => { const last = f.history[f.history.length - 1]; return `<b>${f.id}</b> · ${esc(CROP[last.crop])} in ${last.year}<br>2026 guess ${esc(CROP[f.pred_2026])} (${Math.round(f.pred_confidence * 100)}%) · ${f.slope.toFixed(1)}° slope`; }, { sticky: true, direction: "top", offset: [0, -8] });
      SQ[f.id] = pg;
    });
    ASSETS = L.layerGroup().addTo(LM);
    if ("ResizeObserver" in window) new ResizeObserver(() => { const r = $("map").getBoundingClientRect(); if (!r.width || !r.height) return; LM.invalidateSize({ pan: false }); setMin(); if (lastFit && !userMoved) LM.fitBounds(lastFit[0], Object.assign({}, lastFit[1], { animate: false })); }).observe($("map"));
  }
  const ZONE = { Proposed: "#d4c4ff", Queued: "#fbbf24", Tasked: "#9ec1ff", "In progress": "#9ec1ff", Done: "#6ee7b7" };
  function sqStyle(f) {
    const L_ = state.layer; let st = Object.assign({}, SQ_BASE);
    if (L_ === "crops") st = Object.assign(st, { color: "rgba(7,9,26,.35)", weight: 0.4 });
    else if (L_ === "forecast") st = Object.assign(st, { fillColor: color(f.pred_2026), fillOpacity: 0.3 + 0.6 * f.pred_confidence });
    else if (L_ === "erosion") st = Object.assign(st, { fillColor: rampColor(SLOPE_RAMP, slopeT(f.slope)), fillOpacity: 0.9 });
    else if (L_ === "fit" && FIT) { const v = FIT.m[f.id]; st = Object.assign(st, v >= 0 ? { fillColor: mix("#5b7bd6", "#d4c4ff", Math.min(1, v / FIT.max)), fillOpacity: 0.92 } : { fillColor: "#20263f", fillOpacity: 0.75 }); }
    else if (L_ === "scout") { const k = flagKind(f); st = Object.assign(st, k ? { fillColor: FLAGC[k], fillOpacity: 0.9 } : { fillColor: "#161b33", fillOpacity: 0.55 }); }
    if (state.marks.plan.has(f.id)) st = Object.assign(st, { color: "#6ee7b7", weight: 3 });
    if (state.marks.scout && hasFlag(f, "low")) st = Object.assign(st, { color: "#fbbf24", weight: 2, dashArray: "3 3" });
    if (state.marks.cover && hasFlag(f, "slope")) st = Object.assign(st, { color: COVER_C, weight: 2, dashArray: "2 2" });
    const z = state.zone && state.zone.ids.has(f.id) ? zoneStatus() : null;
    if (z) st = Object.assign(st, { color: ZONE[z] || "#d4c4ff", weight: 2.2, dashArray: z === "Proposed" ? "4 3" : null });
    if (state.hover === f.id) st = Object.assign(st, { color: "#ffffff", weight: 1.6 });
    if (state.fieldId === f.id) st = Object.assign(st, { color: "#ffffff", weight: 3.5, dashArray: null });
    return st;
  }
  function styleSq(f) { const pg = SQ[f.id]; if (pg) { pg.setStyle(sqStyle(f)); if (state.fieldId === f.id) pg.bringToFront(); } }
  function drawMap() {
    if (!LM) return;
    if (state.layer === "fit") { computeFit(); if (FIT) FIT.max = Math.max(0.0001, ...Object.values(FIT.m)); }
    CDL.setOpacity(state.layer === "crops" ? 1 : 0.22);
    state.data.fields.forEach(styleSq);
    const sel = curField(); if (sel && SQ[sel.id]) SQ[sel.id].bringToFront();
    drawAssets(); renderLegend(); selbar();
  }

  function renderLegend() {
    const L = state.layer, sw = (c, t) => `<span><i style="background:${c}"></i>${esc(t)}</span>`;
    let lg = "", note = "";
    if (L === "crops") { lg = ["corn", "soy", "hay", "grass", "other_crop", "non_ag"].map((k) => sw(color(k), CROP[k])).join(""); note = "USDA cropland map 2025, 30 m. Squares are 1.2 km. White outline: your field."; }
    if (L === "forecast") { lg = ["corn", "soy", "grass"].map((k) => sw(color(k), CROP[k])).join("") + `<span class="fs-lg-t">Paler = less sure</span>`; note = "The model's guess for each square's main crop in 2026."; }
    if (L === "erosion") { lg = `<span class="fs-ramp" style="background:linear-gradient(90deg,${SLOPE_RAMP.join(",")})"></span><span class="fs-lg-t">flat → steep (${state.minSlope.toFixed(1)}° to ${state.maxSlope.toFixed(1)}°)</span>`; note = "Slope from NASA NASADEM. Steeper squares lose more soil when bare."; }
    if (L === "fit") { lg = sw("#d4c4ff", "This plan fits best") + sw("#20263f", "Another plan fits better"); note = FIT ? `“${FIT.name}” is the best fit on ${FIT.win} of ${state.data.fields.length} squares for your priorities.` : ""; }
    if (L === "scout") { const c = state.flagCounts; lg = sw(FLAGC.low, `Forecast unsure (${c.low})`) + sw(FLAGC.repeat, `Same cash crop twice (${c.repeat})`) + sw(FLAGC.slope, `Steep (${c.slopeOnly})`); note = "Squares worth a visit before planting."; }
    if (state.zone && state.zone.action) lg += `<span class="fs-lg-t mk"><i style="background:transparent;border:2px dashed ${ZONE[zoneStatus()] || "#d4c4ff"}"></i>Target: ${esc(state.zone.unit)} · ${esc(zoneStatus() || "")} (simulated)</span>`;
    else if (state.marks.plan.size || state.marks.scout || state.marks.cover) lg += `<span class="fs-lg-t mk">Outlined: approved work</span>`;
    $("mapLegend").innerHTML = lg; $("mapNote").textContent = note;
  }

  /* simulated tasking on the map: the selected action's target squares light up; approved tasks get markers that move
     Proposed -> Queued -> Tasked -> In progress -> Done (driven by the shared C2 component's simulated timers). */
  const taskSt = {};
  const center = (id) => SQ[id] ? SQ[id].getBounds().getCenter() : null;
  function targetsFor(id) {
    const F = state.data.fields, f = curField(), typ = F.slice().sort((a, b) => Math.abs(a.slope - TYP_SLOPE) - Math.abs(b.slope - TYP_SLOPE))[0];
    if (id === "field-shift-1" || id === "field-shift-5") return { ids: [(f || typ).id], unit: f ? `field ${f.id}` : "typical field" };
    if (id === "field-shift-2") { const ids = F.filter((x) => hasFlag(x, "slope")).sort((a, b) => b.slope - a.slope).map((x) => x.id); return { ids, unit: "steep squares" }; }
    if (id === "field-shift-4") { const ids = F.filter((x) => hasFlag(x, "low")).sort((a, b) => a.pred_confidence - b.pred_confidence).map((x) => x.id); return { ids, unit: "squares to scout" }; }
    if (id === "field-shift-3") { const ids = F.filter((x) => x.row % 11 === 5 && x.col % 11 === 5).map((x) => x.id); return { ids, unit: "soil-moisture check points" }; }
    return { ids: [], unit: "" };
  }
  function zoneStatus() {
    const a = state.zone && state.zone.action; if (!a) return null; const ts = (a.tasks || []).map((t) => taskSt[a.id + "|" + t.label]).filter(Boolean);
    if (!ts.length) return "Proposed"; if (ts.every((x) => x === "Done")) return "Done"; if (ts.some((x) => x === "In progress")) return "In progress"; if (ts.some((x) => x === "Tasked")) return "Tasked"; return "Queued";
  }
  function drawAssets() {
    if (!ASSETS) return; ASSETS.clearLayers(); const z = state.zone; if (!z || !z.action) return;
    const pts = z.list.slice(0, Math.max(1, (z.action.tasks || []).length)).map(center).filter(Boolean); if (!pts.length) return;
    (z.action.tasks || []).forEach((t, k) => {
      const st = taskSt[z.action.id + "|" + t.label] || "Proposed", ll = pts[k % pts.length];
      const html = `<div class="og-asset" data-s="${esc(st)}" style="margin-top:${(Math.floor(k / pts.length) * 26) - 20}px">${window.OGC2 ? OGC2.icon(t.asset) : ""}<span class="lb">${esc(t.label)}</span><em>${esc(st)}</em></div>`;
      L.marker(ll, { icon: L.divIcon({ className: "og-pin", html, iconSize: [0, 0] }), keyboard: false, interactive: false, zIndexOffset: 500 }).addTo(ASSETS);
    });
  }
  function selbar() {
    const box = $("mapSelbar"), z = state.zone; if (!box) return; if (!z || !z.action) { box.hidden = true; return; }
    const on = state.c2 && state.c2.state.approved[z.action.id];
    box.hidden = false;
    box.innerHTML = `<span class="k">${esc(z.action.cls || "")}</span><span><b>${z.list.length}</b> ${esc(z.unit)}</span><button type="button" class="${on ? "done" : ""}">${on ? "Approved · Undo" : esc(z.action.verb || "Approve")}</button>`;
    box.querySelector("button").onclick = () => state.c2 && state.c2.approve(z.action.id);
  }
  function showZone(a) {
    if (!a) { state.zone = null; drawMap(); return; }
    const t = targetsFor(a.id); state.zone = { action: a, ids: new Set(t.ids), unit: t.unit };
    state.zone.list = t.ids;
    drawMap();
    if (LM && t.ids.length) { const bb = L.latLngBounds(t.ids.map((id) => SQ[id] && SQ[id].getBounds()).filter(Boolean).reduce((acc, x) => acc.concat([x.getSouthWest(), x.getNorthEast()]), []));
      /* no fly animation: an animated zoom cancels basemap tiles mid-flight */
      if (t.ids.length <= 2) fitTo(bb.pad(2.5), { maxZoom: 12.5, padding: [0, 0] }); else fitTo(GEO.bounds); }
  }
  function selectField(id) {
    state.fieldId = id || null;
    document.querySelectorAll("#featured button").forEach((b) => b.setAttribute("aria-pressed", String((b.dataset.id || null) === state.fieldId)));
    renderField(); update();
  }
  function update() {
    if (state.zone && state.zone.action) { const t = targetsFor(state.zone.action.id); state.zone.ids = new Set(t.ids); state.zone.list = t.ids; state.zone.unit = t.unit; }
    renderStrategies(); drawMap(); renderPareto(); refreshC2(); renderSimple(); }

  /* ---------- farmer view: the same data in plain sentences for one field ---------- */
  function renderSimple() {
    const body = $("simpleBody"); if (!body || !state.data) return;
    const f = curField(), opts = optionsFor(f), plan = opts.find((o) => o.id === state.planId) || opts[0];
    $("simplePick").innerHTML = [["", "Typical field"]].concat(Object.entries(FEAT)).map(([id, t]) => `<button type="button" data-id="${id}" aria-pressed="${String((id || null) === state.fieldId)}">${esc(id ? t : t)}</button>`).join("");
    const hist = f ? f.history.slice(-3) : [];
    const steep = f && f.slope > TYP_SLOPE * 1.25, cover = plan.sequence.some((t) => split(t).cover);
    body.innerHTML = `
      <article class="fs-s-card"><h3><i>1</i>What you grew</h3>
        ${f ? `<div class="fs-s-chips">${hist.map((h) => chip(h.crop, h.year, { small: true })).join("")}</div><p>${f.id} · ${ha(f)} ha · slope ${f.slope.toFixed(1)}°${steep ? " (steeper than most)" : ""}</p>`
            : `<p>Pick one of the fields above, or a square on the map below.</p>`}</article>
      <article class="fs-s-card"><h3><i>2</i>What the land and weather show</h3>
        <ul><li><b>Season:</b> about 19 days longer without frost than in 1981, so longer-season varieties have room.</li>
        <li><b>Soil water:</b> steady. No trend in four NASA records, so no case for new irrigation.</li>
        ${f && f.bare_frac_2024 != null ? `<li><b>Bare soil:</b> ${Math.round(f.bare_frac_2024 * 100)}% of this field was bare at some point in 2024${steep ? "; on a slope that means erosion risk" : ""}.</li>` : ""}</ul></article>
      <article class="fs-s-card hi"><h3><i>3</i>Grow next</h3>
        <p class="fs-s-big">${chip(plan.sequence[0], BASE_YEAR)}</p>
        <p>Then: ${esc(plan.sequence.slice(1).map((t, i) => `${BASE_YEAR + 1 + i} ${cropLabel(t)}`).join(" → "))}.</p>
        ${f ? `<p class="fs-fine">On its own history the model expects ${esc(CROP[f.pred_2026].toLowerCase())} here in 2026 (${Math.round(f.pred_confidence * 100)}% confidence).${cover ? " Winter rye after harvest keeps the soil covered." : ""}</p>` : ""}
        <div class="fs-s-btns"><button type="button" class="c2-btn c2-primary" data-s="approve">Approve plan</button><button type="button" class="c2-btn c2-ghost" data-s="alert">Draft message to grower</button><button type="button" class="c2-btn c2-ghost" data-s="full">See why</button></div></article>`;
  }
  function setMode(m) {
    /* Farmer view adds the plain-language cards above the map; the map, legend and data stay visible in both modes */
    const simple = m === "simple"; $("s-simple").hidden = !simple;
    document.querySelectorAll(".fs-mode [data-mode]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.mode === m)));
    document.querySelectorAll(".fs-steps a").forEach((a) => a.classList.toggle("dim", simple));
    if (window.OGShell) OGShell.fit(); window.dispatchEvent(new Event("resize"));
    if (simple) $("s-simple").scrollIntoView({ block: "nearest" });
  }
  document.addEventListener("click", (ev) => {
    const mb = ev.target.closest(".fs-mode [data-mode]"); if (mb) return setMode(mb.dataset.mode);
    const pk = ev.target.closest("#simplePick button"); if (pk) return selectField(pk.dataset.id || null);
    const sb = ev.target.closest("#simpleBody [data-s]"); if (!sb) return;
    if (sb.dataset.s === "full") { setMode("full"); if (window.OGShell) OGShell.show("plan"); return; }
    if (!state.c2) return;
    if (sb.dataset.s === "approve") { setMode("full"); if (window.OGShell) OGShell.show("act"); if (!state.c2.state.approved["field-shift-1"]) state.c2.approve("field-shift-1"); document.querySelector('#c2 .c2-card[data-id="field-shift-1"]').scrollIntoView({ behavior: "smooth", block: "nearest" }); }
    if (sb.dataset.s === "alert") { setMode("full"); state.c2.alert("field-shift-1"); }
  });
  document.addEventListener("click", (ev) => { const g = ev.target.closest("[data-go]"); if (g && window.OGShell) OGShell.show(g.dataset.go); });

  /* ---------- step 4: act (shared C2 component, simulated tasking). Ids match the project page's #act=field-shift-N links. ---------- */
  function actionDefs() {
    const f = curField(), opts = optionsFor(f), plan = opts.find((o) => o.id === state.planId) || opts[0];
    const where = f ? `field ${f.id}` : "the typical field", c26 = split(plan.sequence[0]).crop, area = f ? ` for ${ha(f)} ha` : "";
    const cover = plan.sequence.some((t) => split(t).cover), C = state.flagCounts;
    const last3 = f ? f.history.slice(-3).map((h) => `${h.year} ${CROP[h.crop] || h.crop}`).join(", ") : "";
    const growerAlert = { channel: "Message to grower", to: f ? `Grower of field ${f.id}` : "Growers with typical fields", area: f ? `Field ${f.id} (${ha(f)} ha, highlighted)` : "Typical field, Story County",
      head: `Your plan for 2026–2029: ${seqText(plan.sequence)}`,
      lines: [].concat(last3 ? [`Last three years on this field: ${last3}.`] : [])
        .concat(f ? [`The model expects ${CROP[f.pred_2026].toLowerCase()} on this field in 2026 (${Math.round(f.pred_confidence * 100)}% confidence).`] : [])
        .concat(["The frost-free season is about 19 days longer than in 1981, and soil water shows no trend.", "Reply to confirm or ask your adviser to change it."]),
      src: "USDA Cropland Data Layer 2009–2025; NASA HLS, SMAP, GRACE; Field Shift model (one seed, not a published benchmark)." };
    const scoutAlert = { channel: "Field advisory · co-op members", to: "Growers with flagged squares", area: `Scout list (${C.low} squares on the map)`,
      head: `Scout before planting: ${C.low} squares flagged`,
      lines: ["22.4 km² of fields lost more than 0.1 greenness (NDVI) between Aug 2024 and Jul 2025.", `The 2026 crop forecast is unsure on ${C.low} squares. A drone pass, then a walk-through, is booked before planting.`],
      src: "NASA HLS (Landsat + Sentinel-2, 30 m); Field Shift model." };
    return [
      { id: "field-shift-1", cls: "Rotation plan", verb: "Approve plan", alert: growerAlert, title: `Approve “${plan.name}” for ${where}`,
        sat: "The frost-free season is about 19 days longer than in 1981 (+0.43 days a year, p = 0.006), and soil water shows no trend.",
        act: seqText(plan.sequence), out: "The next four years on this field are set, with the longer season in mind.",
        tasks: [{ asset: "plan", label: `Record 2026–2029 plan · ${where}` }].concat(c26 === "corn" ? [{ asset: "seed", label: "Longer-season corn hybrid on a test strip" }] : []).concat([{ asset: "crew", label: "Send to grower for sign-off" }]) },
      { id: "field-shift-2", cls: "Soil cover", verb: "Approve cover crop", title: `Seed winter rye on the ${C.slopeAll} steep squares`,
        sat: "On a typical field, winter rye cuts the erosion score by 67% for 13% more water demand (a planning score, not measured soil loss).",
        act: "Drill winter rye right after harvest on the steepest squares first.", out: "Less bare soil in spring and autumn on the slopes most at risk.",
        tasks: [{ asset: "seed", label: `Winter rye seed · ${C.slopeAll} squares` }, { asset: "crew", label: "Drill rye after harvest" }] },
      { id: "field-shift-3", cls: "Water", verb: "Approve", title: "Hold off on new irrigation; check soil moisture each season",
        sat: "No trend in soil water: GRACE p = 0.57, GLDAS p = 0.27–0.38, SMAP p = 0.47.",
        act: "Keep a rain-fed plan and add a seasonal NASA SMAP soil-moisture check.", out: "No irrigation spending the data doesn't call for, with a check in place if that changes.",
        tasks: [{ asset: "sensor", label: "Seasonal SMAP soil-moisture check" }] },
      { id: "field-shift-4", cls: "Scouting", verb: "Assign scouting", alert: scoutAlert, title: `Scout the ${C.low} squares where the forecast is unsure`,
        sat: `22.4 km² of fields lost more than 0.1 greenness (NDVI) between 1 Aug 2024 and 31 Jul 2025 (NASA HLS, 30 m). The forecast is unsure on ${C.low} squares.`,
        act: "Send a drone pass, then a scout on foot, before planting.", out: "Scouting time goes where the land changed or the model is unsure.",
        tasks: [{ asset: "drone", label: `Drone survey · ${C.low} squares` }, { asset: "crew", label: "Scout walk-through and notes" }] },
      { id: "field-shift-5", cls: "Seed and inputs", verb: "Order seed", title: `Order ${CROP[c26].toLowerCase()} seed${area}`,
        sat: "The next-crop forecast is 81.8% right on held-out 2024–25 fields (crop history alone: 81.4%).",
        act: `Book 2026 ${CROP[c26].toLowerCase()} seed for ${where}${cover ? ", plus winter rye for after harvest" : ""}. Confirm with the grower.`, out: "Seed is booked from the plan, not from last year's order sheet.",
        tasks: [{ asset: "seed", label: `Reserve ${CROP[c26].toLowerCase()} seed · ${where}${area}` }].concat(cover ? [{ asset: "seed", label: "Reserve winter rye seed" }] : []).concat([{ asset: "truck", label: "Schedule delivery before planting" }]) },
    ];
  }
  const LAYER_FOR = { "field-shift-1": "fit", "field-shift-2": "erosion", "field-shift-3": "crops", "field-shift-4": "scout", "field-shift-5": "forecast" };
  function mountC2() {
    if (!window.OGC2) { $("c2").innerHTML = `<p class="fs-fine">The action queue didn't load.</p>`; return; }
    const defs = actionDefs(); state.c2Actions = defs;
    state.c2 = window.OGC2.mount("#c2", {
      app: "field-shift", dock: true, kicker: "Decision support", title: "Recommended actions", user: "Farmer, agronomist or co-op",
      actions: defs,
      onSelect: (a) => { if (a) { state.layer = LAYER_FOR[a.id] || "crops"; $("layers").querySelectorAll("button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.layer === state.layer))); }
        showZone(a); if (a && window.innerWidth < 1024 && !state.fromHash) $("mapSec").scrollIntoView({ behavior: "smooth", block: "start" }); },
      onTask: (a, t, s) => { taskSt[a.id + "|" + t.label] = s; drawMap(); },
      onApprove: (a, on) => {
        (a.tasks || []).forEach((t) => { const k = a.id + "|" + t.label; if (on) taskSt[k] = "Queued"; else delete taskSt[k]; });
        if (a.id === "field-shift-1") { const f = curField(); if (f) { if (on) state.marks.plan.add(f.id); else state.marks.plan.delete(f.id); } }
        if (a.id === "field-shift-4") state.marks.scout = on;
        if (a.id === "field-shift-2") state.marks.cover = on;
        drawMap();
      },
      onReset: () => { state.marks = { plan: new Set(), scout: false, cover: false }; Object.keys(taskSt).forEach((k) => delete taskSt[k]); drawMap(); refreshC2(); },
      foot: "Simulated: shows how an approved plan would become seed orders, drone surveys and scouting jobs. No real supplier, drone or crew is contacted.",
    });
  }
  function refreshC2() {
    // Keep proposed cards in sync with the chosen field and plan; approved cards keep what was approved.
    if (!state.c2 || !state.c2Actions) return; const approved = state.c2.state.approved;
    actionDefs().forEach((d) => {
      const card = document.querySelector(`#c2 .c2-card[data-id="${d.id}"]`); if (!card || approved[d.id]) return;
      const src = state.c2Actions.find((x) => x.id === d.id); if (src) Object.assign(src, d);
      card.querySelector(".c2-act").textContent = d.title;
      const dds = card.querySelectorAll(".c2-flow dd"); if (dds[0]) dds[0].textContent = d.sat; if (dds[1]) dds[1].textContent = d.act;
      const as = card.querySelector(".c2-assets"); if (as) as.innerHTML = d.tasks.map((t) => `<li>${window.OGC2.icon(t.asset)}<span>${esc(t.label)}</span></li>`).join("");
    });
  }
  function deepLink() {
    // /field-shift/app/#act=field-shift-N (links from the project page): open that action and its map layer.
    if (/alert=/.test(location.hash) && window.OGShell) OGShell.show("act");
    const dm = /^#demo(?:=([\w-]+))?$/.exec(location.hash);
    if (dm && state.c2) { // capture state for the video and slides: select, approve (tasks run to Done in ~5 s), open the alert draft
      const id = dm[1] || "field-shift-4"; if (window.OGShell) OGShell.show("act"); state.fromHash = true; state.c2.select(id); state.fromHash = false;
      setTimeout(() => { if (!state.c2.state.approved[id]) state.c2.approve(id); const d = (state.c2Actions || []).find((x) => x.id === id); if (d && d.alert) state.c2.alert(id, { quiet: true }); if (window.OGShell) OGShell.scrollDock(document.querySelector(`#c2 .c2-card[data-id="${id}"]`)); }, 900); return; }
    const m = /^#act=([\w-]+)$/.exec(location.hash); if (!m || !state.c2) return;
    if (window.OGShell) OGShell.show("act");
    const card = document.querySelector(`#c2 .c2-card[data-id="${CSS.escape(m[1])}"]`); if (!card) return;
    if (!card.classList.contains("sel")) { state.fromHash = true; state.c2.select(m[1]); state.fromHash = false; }
    setTimeout(() => { if (window.OGShell) OGShell.scrollDock(card); }, 120);
  }

  /* ---------- step 5: impact (copy from OG_APP.impact = src/modules/field-shift/app.json when present) ---------- */
  function renderImpact() {
    const C = state.colab, FC = state.flagCounts;
    const OG = window.OG_APP && Array.isArray(window.OG_APP.impact) && window.OG_APP.impact.length && window.OG_APP.impact.every((x) => x.img) ? window.OG_APP.impact : null;
    const P = OG || [
      { img: "farmer", alt: "A farmer at the edge of a corn field checks a field map on a tablet", user: "Farmer", decision: "What to plant on each field for 2026–2029, and whether to add a cover crop.",
        before: ["Plants corn, then soybean, out of habit.", "Plans the season from memory of when frost comes."],
        after: ["Has a four-year plan per field, ranked by what matters to them.", "Plans for a frost-free season about 19 days longer than in 1981.", "Puts winter rye on steep fields: erosion score 67% lower (a planning score)."],
        geo: { v: "+0.43 d/yr", l: "frost-free season, NASA POWER 1981–2025, p = 0.006" }, metric: { v: (C.lgbm.acc * 100).toFixed(1) + "%", l: `next-crop accuracy vs ${(C.baselines.markov2.acc * 100).toFixed(1)}% from crop history alone` } },
      { img: "agronomist", alt: "An agronomist reviews field data on a tablet with a grower", user: "Agronomist or co-op", decision: "Which fields to scout first, and how much of each seed to stock.",
        before: ["Scouts in drive-by order.", "Starts seed orders from last year's sheet.", "Weighs irrigation on a hunch."],
        after: [`Scouts the ${FC.low} squares where the forecast is unsure, and the 22.4 km² that lost greenness, first.`, "Stocks seed from a 30 m next-crop forecast for every field in the county.", "Holds off on irrigation spending: four NASA water records show no trend."],
        geo: { v: "22.4 km²", l: "fields with NDVI down by more than 0.1, NASA HLS, Aug 2024 → Jul 2025" }, metric: { v: C.lgbm.macro_f1.toFixed(4), l: `macro-F1 across six crops vs ${C.baselines.markov2.macro_f1.toFixed(4)} from crop history alone` } },
    ];
    $("people").innerHTML = P.map((p) => `<article class="fs-person c2-imp">
      <img src="../../assets/img/people/${esc(p.img)}.webp" alt="${esc(p.alt)}" loading="lazy" width="1280" height="720">
      <header><span class="c2-cls">${esc(p.user)}</span><h3>${esc(p.decision)}</h3></header>
      <div class="c2-ba"><div class="c2-b"><p>Before</p><ul>${p.before.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div><span class="c2-arrow" aria-hidden="true">→</span>
      <div class="c2-a"><p>With Field Shift</p><ul>${p.after.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div></div>
      <footer><div><b>${esc(p.geo.v)}</b><span>${esc(p.geo.l)}</span></div><div><b>${esc(p.metric.v)}</b><span>${esc(p.metric.l)}</span></div></footer></article>`).join("");
    $("impGeo").innerHTML = [["+19 days", "longer frost-free season since 1981 (+0.43 d/yr, p = 0.006)"], ["No trend", "in soil water: GRACE p = 0.57, GLDAS p = 0.27–0.38"], ["22.4 km²", "of fields got less green, summer 2024 → 2025 (HLS, 30 m)"]].map(([a, b]) => `<li><b>${a}</b><span>${b}</span></li>`).join("");
    $("impHum").innerHTML = [["Plant", "for the longer season, field by field"], ["Protect", "steep fields with winter rye (−67% erosion score)"], ["Save", "irrigation money the data doesn't call for"]].map(([a, b]) => `<li><b>${a}</b><span>${b}</span></li>`).join("");
    $("impMetrics").innerHTML = [[C.lgbm.acc.toFixed(4), `next-crop accuracy (crop history alone ${C.baselines.markov2.acc.toFixed(4)})`], [C.lgbm.macro_f1.toFixed(4), `macro-F1, six crops (crop history alone ${C.baselines.markov2.macro_f1.toFixed(4)})`], [C.map.pixel_accuracy_full_county.toFixed(3), `pixel accuracy, full-county 2025 map (${C.map.farmed_pixels.toLocaleString("en-US")} pixels)`], [C.lgbm.per_class_f1.hay.toFixed(2), "honest miss: hay F1 (rare 'other' class 0)", "neg"]]
      .map(([v, t, n]) => `<li class="${n || ""}"><strong>${v}</strong><span>${esc(t)}</span></li>`).join("");
  }

  /* ---------- evidence ---------- */
  function renderPareto() {
    const canvas = $("pareto"), ctx = canvas.getContext("2d"), w = canvas.width, h = canvas.height; ctx.clearRect(0, 0, w, h);
    const pad = { l: 56, r: 18, t: 18, b: 44 }, opts = optionsFor(curField());
    const xs = opts.map((o) => o.indicators.water_demand), ys = opts.map((o) => o.indicators.erosion_risk);
    const x0 = Math.min(...xs) - 0.04, x1 = Math.max(...xs) + 0.04, y0 = Math.max(0, Math.min(...ys) - 0.02), y1 = Math.max(...ys) + 0.02;
    const X = (v) => pad.l + (v - x0) / (x1 - x0 || 1) * (w - pad.l - pad.r), Y = (v) => h - pad.b - (v - y0) / (y1 - y0 || 1) * (h - pad.t - pad.b);
    ctx.strokeStyle = "rgba(190,205,255,.28)"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, h - pad.b); ctx.lineTo(w - pad.r, h - pad.b); ctx.stroke();
    ctx.fillStyle = "#b7c0d6"; ctx.font = "13px Geist, system-ui, sans-serif";
    ctx.fillText("Water demand (crop coefficient) →", pad.l, h - 12);
    ctx.save(); ctx.translate(18, h - pad.b); ctx.rotate(-Math.PI / 2); ctx.fillText("Erosion score →", 0, 0); ctx.restore();
    opts.forEach((o) => {
      const sel = o.id === state.planId; ctx.beginPath(); ctx.arc(X(o.indicators.water_demand), Y(o.indicators.erosion_risk), sel ? 9 : o.kind === "named" ? 7 : 5.5, 0, Math.PI * 2);
      ctx.fillStyle = o.kind === "named" ? "#d4c4ff" : "#9ec1ff"; ctx.fill(); if (sel) { ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 2.5; ctx.stroke(); }
      if (o.kind === "named" || sel) { ctx.fillStyle = "#dfe5f5"; ctx.fillText(o.name, Math.min(w - 240, X(o.indicators.water_demand) + 12), Y(o.indicators.erosion_risk) + 4); }
    });
    $("paretoNote").textContent = state.data.pareto.note + " Plans that grow corn or soybean in the same field two years running are left out.";
  }
  function renderClimate() {
    const canvas = $("clim"), ctx = canvas.getContext("2d"), w = canvas.width, h = canvas.height; ctx.clearRect(0, 0, w, h);
    const rows = state.data.climate_yearly.filter((r) => r.year >= 2000 && r.gs_precip != null); if (!rows.length) return;
    const pad = { l: 44, r: 44, t: 26, b: 26 }, maxP = Math.max(...rows.map((r) => r.gs_precip)), gs = rows.map((r) => r.gs_gdd), gmin = Math.min(...gs) * 0.95, gmax = Math.max(...gs) * 1.02, bw = (w - pad.l - pad.r) / rows.length, H = h - pad.t - pad.b;
    rows.forEach((r, i) => { ctx.fillStyle = "rgba(158,193,255,.55)"; const bh = r.gs_precip / maxP * H; ctx.fillRect(pad.l + i * bw + bw * 0.15, h - pad.b - bh, bw * 0.7, bh); });
    ctx.strokeStyle = "#facc15"; ctx.lineWidth = 2.2; ctx.beginPath();
    rows.forEach((r, i) => { const x = pad.l + i * bw + bw / 2, y = h - pad.b - (r.gs_gdd - gmin) / (gmax - gmin) * H; if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); }); ctx.stroke();
    ctx.font = "12px Geist, system-ui, sans-serif"; ctx.fillStyle = "#b7c0d6"; ctx.fillText(`Bars: Apr–Sep rain, max ${Math.round(maxP)} mm`, pad.l, 14);
    ctx.fillStyle = "#facc15"; ctx.fillText("Line: growing degree days", pad.l + 230, 14);
    ctx.fillStyle = "#b7c0d6"; ctx.fillText(String(rows[0].year), pad.l, h - 6); ctx.fillText(String(rows[rows.length - 1].year), w - pad.r - 30, h - 6);
  }
  function barBlock(host, items, key) {
    const max = Math.max(...items.map((it) => it[1][key]));
    host.innerHTML = items.map(([label, rec, kind]) => `<div class="fs-bar ${kind}"><span>${esc(label)}</span><div><i style="width:${Math.max(2, rec[key] / max * 100)}%"></i></div><b>${rec[key].toFixed(3)}</b></div>`).join("");
  }
  const LABEL_AB = (k) => ({ history_only: "Crop history only", "+terrain_soil": "+ NASADEM terrain and soil", "+climate": "+ NASA POWER climate", "+ndvi (full)": "+ MODIS greenness (all)" }[k] || k.replace(/_/g, " "));
  const BASES = (b, l) => [["Same as last year", b.persistence, "base"], ["Corn/soy alternation", b.corn_soy_alternation, "base"], ["Crop-history table", b.markov2, "base"], ["Our model", l, "ours"]];
  function renderModel() {
    const m = state.data.metrics; $("modelCaveat").textContent = m.caveat;
    barBlock($("baseBars"), BASES(m.baselines, m.lgbm), "acc");
    barBlock($("abBars"), Object.entries(m.ablation).map(([k, v]) => [LABEL_AB(k), v, ""]), "acc");
    const c = m.calibration; $("calText").textContent = `Accuracy shown. ${c.method}: ECE ${c.test_ece_before.toFixed(4)} → ${c.test_ece_after.toFixed(4)} (slightly worse, so the raw probabilities are kept).`;
    $("calImg").src = "data/crop_confusion_calibration.png"; $("abImg").src = "data/crop_ablation.png"; $("histImg").src = "data/cdl_history.png"; $("slopeImg").src = "data/slope_tiles.png";
  }
  function renderColab() {
    const c = state.colab, local = state.data.metrics; $("colabCaveat").textContent = c.caveat;
    barBlock($("colabBars"), BASES(c.baselines, c.lgbm), "acc");
    const pc = c.lgbm.per_class_f1;
    $("colabText").textContent = `Accuracy shown. Macro-F1: crop-history table ${c.baselines.markov2.macro_f1.toFixed(4)}, our model ${c.lgbm.macro_f1.toFixed(4)}. Per-crop F1: corn ${pc.corn.toFixed(3)}, soybean ${pc.soy.toFixed(3)}, hay ${pc.hay.toFixed(3)}, grass ${pc.grass.toFixed(3)}, other ${pc.other_crop.toFixed(3)}, not farmed ${pc.non_ag.toFixed(3)}.`;
    barBlock($("colabAbBars"), Object.entries(c.ablation).map(([k, v]) => [LABEL_AB(k), v, ""]), "acc");
    const nf = (v) => Number(v).toLocaleString("en-US");
    const rows = [["Pixels sampled / tested", `${nf(local.n_pixels_sampled)} / ${nf(local.n_test)}`, `${nf(c.n_pixels_sampled)} / ${nf(c.n_test)}`],
      ["Accuracy", local.lgbm.acc.toFixed(3), c.lgbm.acc.toFixed(3)], ["Macro-F1", local.lgbm.macro_f1.toFixed(3), c.lgbm.macro_f1.toFixed(3)],
      ["Crop-history table accuracy / macro-F1", `${local.baselines.markov2.acc.toFixed(3)} / ${local.baselines.markov2.macro_f1.toFixed(3)}`, `${c.baselines.markov2.acc.toFixed(3)} / ${c.baselines.markov2.macro_f1.toFixed(3)}`],
      ["Calibration error (ECE) before → after scaling", `${local.calibration.test_ece_before.toFixed(4)} → ${local.calibration.test_ece_after.toFixed(4)}`, `${c.calibration.test_ece_before.toFixed(4)} → ${c.calibration.test_ece_after.toFixed(4)}`],
      ["2025 full-county pixel accuracy", "not computed", `${c.map.pixel_accuracy_full_county.toFixed(3)} on ${nf(c.map.farmed_pixels)} pixels`]];
    $("colabCompare").innerHTML = `<table class="fs-table"><thead><tr><th>Metric</th><th class="num">Smaller run</th><th class="num">Full-county run</th></tr></thead><tbody>${rows.map((r) => `<tr><th>${esc(r[0])}</th><td class="num">${esc(r[1])}</td><td class="num">${esc(r[2])}</td></tr>`).join("")}</tbody></table>`;
    $("colabAbImg").src = "data/colab_run/crop_ablation.png"; $("colabCalImg").src = "data/colab_run/crop_confusion_calibration.png"; $("colabMapImg").src = "data/colab_run/crop_map.png";
  }
  function renderHelp() {
    const o = state.data.objectives;
    $("objHelp").innerHTML = `<p>Each plan gets five factor values for the chosen field. For the fit, each is turned so higher is better (1 − value; nitrogen as is), then averaged with your settings as weights (Ignore = 0, Matters = 1, Top priority = 2) and shown × 100. Water demand is a crop coefficient near 1, so it lowers every plan's fit by a similar amount: compare fits between plans, not against 100.</p>` +
      o.keys.map((k) => `<h3>${esc(PRIO[k].t)} <small>${esc(PRIO[k].s)} · ${o.sense[k] === "min" ? "lower is better" : "higher is better"}</small></h3><p>${esc(PRIO[k].how)}</p>`).join("");
    $("disclaimer").textContent = state.data.disclaimer;
  }
  function renderCitations() {
    $("citeList").innerHTML = state.data.citations.map((c) => `<li><b>${esc(c.item)}.</b> ${esc(c.credit)} Licence: ${esc(c.licence)}. ${c.url ? `<a href="${esc(c.url)}">${esc(c.url)}</a>` : ""}</li>`).join("");
  }

  /* ---------- step nav ---------- */
  function stepNav() {
    const links = [...document.querySelectorAll(".fs-steps a")];
    const io = new IntersectionObserver((es) => es.forEach((en) => { if (en.isIntersecting) links.forEach((a) => a.classList.toggle("on", a.dataset.step === en.target.dataset.step)); }), { rootMargin: "-40% 0px -55% 0px" });
    document.querySelectorAll("section[data-step]").forEach((s) => io.observe(s));
    document.querySelectorAll("[data-open]").forEach((b) => b.addEventListener("click", () => { const d = document.querySelector(b.dataset.open); if (d) { d.open = true; d.scrollIntoView({ behavior: "smooth", block: "start" }); } }));
  }

  Promise.all([
    fetch("data/app_data.json").then((r) => { if (!r.ok) throw new Error("app_data.json missing"); return r.json(); }),
    fetch("data/colab_run/results.json").then((r) => { if (!r.ok) throw new Error("colab_run/results.json missing"); return r.json(); }),
    fetch("data/geo.json").then((r) => { if (!r.ok) throw new Error("geo.json missing"); return r.json(); }),
  ]).then(([data, colab, geo]) => {
    state.data = data; state.colab = colab;
    data.objectives.keys.forEach((k) => { state.weights[k] = 50; });
    TYP_SLOPE = median(data.fields.map((f) => f.slope));
    const sl = data.fields.map((f) => f.slope).sort((a, b) => a - b);
    SLOPE_Q = [0.2, 0.4, 0.6, 0.8].map((q) => sl[Math.floor(q * (sl.length - 1))]); state.minSlope = sl[0]; state.maxSlope = sl[sl.length - 1];
    const hv = new Set(); data.strategies.forEach((s) => Object.values(s.field_indicators || {}).forEach((v) => hv.add(v.heat_frost_exposure.toFixed(2)))); if (hv.size === 1) state.heatFlat = [...hv][0];
    const fc = { low: 0, repeat: 0, slopeOnly: 0, slopeAll: 0 };
    data.fields.forEach((f) => { if (hasFlag(f, "low")) fc.low++; if (flagKind(f) === "repeat") fc.repeat++; if (flagKind(f) === "slope") fc.slopeOnly++; if (hasFlag(f, "slope")) fc.slopeAll++; });
    state.flagCounts = fc;
    buildOptions();
    renderLayers(); renderFeatured(); renderSliders(); renderField(); renderHelp(); renderModel(); renderColab(); renderCitations(); renderClimate(); renderImpact();
    renderStrategies(); renderPareto();
    initMap(geo); drawMap();
    mountC2(); stepNav(); deepLink(); window.addEventListener("hashchange", deepLink);
    renderSimple(); if (/simple/.test(location.hash)) setMode("simple");
    window.addEventListener("hashchange", () => { if (/simple/.test(location.hash)) setMode("simple"); });
    $("loadStatus").textContent = `Loaded ${data.fields.length} field squares · ${colab.n_test.toLocaleString("en-US")} test pixels in the full-county run.`;
  }).catch((err) => { $("loadStatus").textContent = "Couldn't load the results: " + err.message; console.warn(err); });
})();
