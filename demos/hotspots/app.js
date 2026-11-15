/* Hot Spots dashboard: fire activity map, burn calendar, simulated decision support. One seed, not a published benchmark. */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const FIRE = [[42, 29, 20], [124, 45, 18], [194, 65, 12], [249, 115, 22], [251, 191, 36], [253, 230, 138]];
  const RATIO = [[56, 104, 178], [120, 160, 214], [206, 216, 236], [246, 222, 196], [240, 150, 90], [196, 60, 30]];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const state = { meta: null, presetKey: "canada", country: "Canada", bbox: [-141.0, 41.7, -52.6, 83.1], drawing: false, startLatLng: null,
    layer: "fire", cal: null, dis: null, cells: {}, provs: null, action: null, fireMax: 0 };

  function ramp(stops, t) {
    t = Math.max(0, Math.min(1, t)); const p = t * (stops.length - 1), i = Math.min(stops.length - 2, Math.floor(p)), f = p - i, a = stops[i], b = stops[i + 1];
    return `rgb(${Math.round(a[0] + (b[0] - a[0]) * f)},${Math.round(a[1] + (b[1] - a[1]) * f)},${Math.round(a[2] + (b[2] - a[2]) * f)})`;
  }
  const fireCol = (t) => ramp(FIRE, t);
  const ratioCol = (v) => ramp(RATIO, (Math.max(-3, Math.min(3, v)) + 3) / 6);
  const fmt = (n, d) => (n === null || n === undefined || Number.isNaN(n) ? "—" : Number(n).toFixed(d));
  const big = (n) => (n == null ? "—" : n >= 10000 ? Math.round(n / 1000).toLocaleString("en-US") + "k" : Math.round(n).toLocaleString("en-US"));
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const q = (o) => new URLSearchParams(o).toString();
  async function getJSON(u) { const r = await fetch(u); if (!r.ok) throw new Error(`${r.status} ${u}`); return r.json(); }
  function setStatus(msg, err) { const el = $("status"); el.textContent = msg; el.className = "status" + (err ? " err" : ""); }

  /* ---------- map ---------- */
  if (window.OGShell) OGShell.fit(); // size the workspace before the map takes its first view
  const map = L.map("map", { worldCopyJump: true, preferCanvas: true, zoomSnap: 0.25, zoomControl: false });
  L.control.zoom({ position: "bottomright" }).addTo(map);
  /* every programmatic view goes through fitTo(); while the user hasn't panned or zoomed, a resize refits the same bounds,
     so the data never ends up cropped when the layout settles after load. */
  const DATA_BOUNDS = L.latLngBounds([[41.6, -141.4], [82.1, -52.4]]); // all Canada fire cells (0.25°), 2003–2025
  let lastFit = null, userMoved = false;
  function fitTo(b, opts) { lastFit = [L.latLngBounds(b), Object.assign(opts && opts.paddingTopLeft ? {} : { padding: [12, 12] }, opts || {})]; userMoved = false; map.fitBounds(lastFit[0], Object.assign({ animate: false }, lastFit[1])); }
  ["mousedown", "wheel", "touchstart", "keydown", "dblclick"].forEach((ev) => $("map").addEventListener(ev, (e) => { if (!e.target.closest || !e.target.closest(".og-ovl, .leaflet-control")) userMoved = true; }, { passive: true }));
  fitTo(DATA_BOUNDS, ovlPad()); // set the first view before any tile loads, so no tile request is cancelled
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", { attribution: "Tiles &copy; Esri", maxZoom: 16 }).addTo(map);
  map.createPane("labels"); map.getPane("labels").style.zIndex = 450; map.getPane("labels").style.pointerEvents = "none";
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}", { pane: "labels", maxZoom: 16 }).addTo(map);
  const layers = { fire: L.layerGroup(), trend: L.layerGroup(), ratio: L.layerGroup() };
  const boxLayer = L.layerGroup().addTo(map), taskLayer = L.layerGroup().addTo(map), assetLayer = L.layerGroup().addTo(map);
  if ("ResizeObserver" in window) new ResizeObserver(() => { const r = $("map").getBoundingClientRect(); if (!r.width || !r.height) return; map.invalidateSize({ pan: false }); if (lastFit && !userMoved) map.fitBounds(lastFit[0], Object.assign({ animate: false }, lastFit[1])); }).observe($("map"));
  // Keep every detection clear of the layer tabs (top) and the legend (bottom-left) so the full view is uncropped.
  function ovlPad() {
    const m = $("map").getBoundingClientRect(), tabs = document.querySelector(".og-stage .og-seg"), leg = $("mapLegend");
    const top = tabs ? Math.max(12, tabs.getBoundingClientRect().bottom - m.top + 8) : 12;
    const bot = leg && leg.offsetHeight && m.height > 420 ? Math.min(m.height * 0.4, leg.getBoundingClientRect().height + 16) : 12;
    return { paddingTopLeft: [12, top], paddingBottomRight: [12, bot] };
  }
  const fitCanada = () => fitTo(DATA_BOUNDS, ovlPad());

  function setBBox(bbox, country) {
    state.bbox = bbox.map(Number); window.__hotspotsBBox = state.bbox; if (country) state.country = country;
    const [w, s, e, n] = state.bbox; boxLayer.clearLayers();
    L.rectangle([[s, w], [n, e]], { color: "#9ec1ff", weight: 1.5, dashArray: "5 5", fill: false, interactive: false }).addTo(boxLayer);
    $("aoiLabel").textContent = `AOI ${w.toFixed(2)}, ${s.toFixed(2)} to ${e.toFixed(2)}, ${n.toFixed(2)}  ·  ${state.country}`;
  }
  async function fireCells(country) { const c = country.toLowerCase(); if (!state.cells[c]) state.cells[c] = getJSON(`data/fire_cells_${c}.json`); return state.cells[c]; }
  async function drawFire() {
    const d = await fireCells(state.country); layers.fire.clearLayers();
    state.fireMax = Math.max(...d.cells.map((r) => r[2])); const mx = Math.log10(1 + state.fireMax);
    d.cells.forEach((r) => { const t = Math.log10(1 + r[2]) / mx;
      L.rectangle([[r[0] - 0.125, r[1] - 0.125], [r[0] + 0.125, r[1] + 0.125]], { stroke: false, fillColor: fireCol(t), fillOpacity: 0.35 + 0.6 * t, interactive: false }).addTo(layers.fire); });
    legend();
  }
  async function drawTrend() {
    if (!state.provs) state.provs = await getJSON("data/provinces_canada.json");
    layers.trend.clearLayers();
    const mx = Math.max(1, ...state.provs.features.filter((f) => f.properties.h_p != null && f.properties.h_p < 0.05).map((f) => f.properties.h_slope));
    L.geoJSON(state.provs, {
      style: (f) => { const p = f.properties, s = p.h_p != null && p.h_p < 0.05;
        return { color: "rgba(190,205,255,.45)", weight: 1, fillColor: s ? fireCol(0.35 + 0.65 * p.h_slope / mx) : "#2a3150", fillOpacity: s ? 0.85 : 0.55 }; },
      onEachFeature: (f, l) => { const p = f.properties;
        l.bindTooltip(`<b>${esc(p.name)}</b><br>${p.h_slope == null ? "Too few detections to test" : `Harmonized: ${p.h_slope > 0 ? "+" : ""}${big(p.h_slope)}/yr, p = ${fmt(p.h_p, 3)}${p.h_p < 0.05 ? "" : " (not significant)"}<br>MODIS only: ${p.m_slope > 0 ? "+" : ""}${big(p.m_slope)}/yr, p = ${fmt(p.m_p, 3)}`}`, { sticky: true }); }
    }).addTo(layers.trend);
    legend();
  }
  function drawRatio() {
    layers.ratio.clearLayers();
    ((state.dis && state.dis.cells) || []).forEach((c) => {
      L.circleMarker([c.lat, c.lon], { radius: Math.max(2, Math.min(7, Math.log1p((c.m_n || 0) + (c.v_n || 0)) * 0.7)), stroke: false, fillOpacity: 0.8, fillColor: ratioCol(c.log2_ratio || 0) })
        .bindTooltip(`MODIS ${c.m_n} · VIIRS ${c.v_n}<br>log2 ratio ${fmt(c.log2_ratio, 2)}`, { sticky: true }).addTo(layers.ratio);
    });
    legend();
  }
  function legend() {
    const box = $("mapLegend"), grad = (st) => `linear-gradient(90deg, ${st.map((s, i) => `rgb(${s}) ${(i / (st.length - 1)) * 100}%`).join(",")})`;
    if (state.layer === "fire") box.innerHTML = `<b>Fires per year, 2003–2025 average</b><i class="bar" style="background:${grad(FIRE)}"></i><span class="ticks"><span>1</span><span>10</span><span>100</span><span>${big(state.fireMax)}</span></span><small>One square = one 0.25° cell (≈ 28 km). VIIRS-equivalent detections.</small>`;
    else if (state.layer === "trend") box.innerHTML = `<b>Trend in fires per year, 2003–2025</b><i class="bar" style="background:${grad(FIRE.slice(2))}"></i><span class="ticks"><span>rising</span><span>rising fastest</span></span><small><i class="sw" style="background:#2a3150"></i> no significant trend · Mann-Kendall, α 0.05. Hover a province.</small>`;
    else box.innerHTML = `<b>VIIRS vs MODIS, 2012–2025</b><i class="bar" style="background:${grad(RATIO)}"></i><span class="ticks"><span>MODIS sees more</span><span>VIIRS sees more</span></span><small>Why harmonizing matters: the newer sensor sees more small fires.</small>`;
    if (state.action && state.action.noteTxt) box.insertAdjacentHTML("beforeend", `<small class="hs-tnote"><b>${esc(state.action.cls || "")}:</b> ${esc(state.action.noteTxt)} Tasking is simulated.</small>`);
  }
  function setLayer(k) {
    state.layer = k; Object.entries(layers).forEach(([n, l]) => (n === k ? l.addTo(map) : l.remove()));
    document.querySelectorAll("[data-layer]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.layer === k)));
    if (k === "fire") drawFire(); else if (k === "trend") drawTrend(); else drawRatio();
  }
  document.querySelectorAll("[data-layer]").forEach((b) => b.addEventListener("click", () => setLayer(b.dataset.layer)));

  /* ---------- KPIs ---------- */
  const presetLabel = () => (state.meta && state.presetKey !== "custom" && state.meta.presets[state.presetKey] ? state.meta.presets[state.presetKey].label : "Custom area");
  function kpis(cal) {
    const rows = cal.calendar || [], byYear = {}, byMon = Array(12).fill(0);
    rows.forEach((r) => { byYear[r.year] = (byYear[r.year] || 0) + (r.harmonized || 0); byMon[r.month - 1] += r.harmonized || 0; });
    const yrs = Object.keys(byYear).map(Number), top = yrs.reduce((a, b) => (byYear[b] > byYear[a] ? b : a), yrs[0]);
    const peak = byMon.indexOf(Math.max(...byMon)), flags = rows.filter((r) => r.unusual), fm = Array(12).fill(0); flags.forEach((r) => fm[r.month - 1]++);
    const fmMax = Math.max(...fm), fmMon = fm.indexOf(fmMax);
    $("kpis").innerHTML = `<p class="og-h hs-reg">${esc(presetLabel())} · 2000–2025</p><ul class="og-kpis hs-kpis">
        <li><small>Peak month</small><b>${MON[peak]}</b><span>most fires</span></li>
        <li><small>Biggest year</small><b>${top}</b><span>${big(byYear[top])} fires</span></li>
        <li><small>Unusual</small><b>${flags.length}</b><span>${flags.length ? `months, most ${MON[fmMon]}` : "none flagged"}</span></li>
        <li><small>2025</small><b>${big(byYear[2025])}</b><span>fires</span></li></ul>`;
    $("outlookHost").innerHTML = outlook(rows, byYear);
  }

  /* 2026 outlook: from past seasons only (Sen-slope trend line over 2003–2025 + each month's 2012–2025 median). Not a weather forecast. */
  function outlook(rows, byYear) {
    const ys = Object.keys(byYear).map(Number).filter((y) => y >= 2003 && y <= 2025).sort((a, b) => a - b); if (ys.length < 10) return "";
    const sl = []; for (let i = 0; i < ys.length; i++) for (let j = i + 1; j < ys.length; j++) sl.push((byYear[ys[j]] - byYear[ys[i]]) / (ys[j] - ys[i]));
    const med = (a) => { const b = a.slice().sort((x, y) => x - y), k = b.length >> 1; return b.length % 2 ? b[k] : (b[k - 1] + b[k]) / 2; };
    const b = med(sl), a = med(ys.map((y) => byYear[y] - b * y)), proj = Math.max(0, a + b * 2026);
    const last = ys.slice(-10).map((y) => byYear[y]), lo = Math.min(...last), hi = Math.max(...last);
    const mon = Array.from({ length: 12 }, (_, m) => med(rows.filter((r) => r.month === m + 1 && r.year >= 2012).map((r) => r.harmonized || 0)));
    const mm = Math.max(...mon, 1), pk = mon.indexOf(Math.max(...mon));
    const fl = Array(12).fill(0); rows.forEach((r) => { if (r.unusual && r.year >= 2011) fl[r.month - 1]++; });
    const watch = fl.map((c, i) => [c, i]).filter(([c]) => c >= 2).sort((x, y) => y[0] - x[0]).slice(0, 3);
    return `<section class="outlook og-card" aria-label="What to expect in 2026">
      <h3>What to expect in 2026 <span>from past seasons, not a weather forecast</span></h3>
      <div class="ol-row"><div><b>${big(proj)}</b><small>fires on the 2003–2025 trend line (${b >= 0 ? "+" : "−"}${big(Math.abs(b))}/yr)</small></div>
        <div><b>${big(lo)}–${big(hi)}</b><small>range of the last 10 years</small></div></div>
      <div class="ol-bars" role="img" aria-label="Typical fires per month, 2012–2025 median">${mon.map((v, i) => `<i class="${i === pk ? "pk" : ""}${fl[i] >= 2 ? " w" : ""}" style="--h:${Math.max(3, Math.round((v / mm) * 100))}%" title="${MON[i]}: median ${big(v)} fires (2012–2025)${fl[i] ? `, unusual ${fl[i]}× since 2011` : ""}"></i>`).join("")}</div>
      <div class="ol-mon">${MON.map((m) => `<span>${m[0]}</span>`).join("")}</div>
      <p class="fine">Peak: <b>${MON[pk]}</b> (median month, 2012–2025).${watch.length ? ` Watch: ${watch.map(([c, i]) => `<b>${MON[i]}</b> (unusual ${c}× since 2011)`).join(", ")}.` : ""}</p>
    </section>`;
  }

  /* ---------- calendar ---------- */
  function renderCalendar(data) {
    state.cal = data;
    const host = $("calHost"), byYM = new Map(); let maxLog = 0;
    (data.calendar || []).forEach((r) => { byYM.set(`${r.year}-${r.month}`, r); maxLog = Math.max(maxLog, Math.log10((r.harmonized || 0) + 1)); });
    // months down, years across: a short, wide strip that fits under the map
    const YRS = []; for (let y = 2000; y <= 2025; y++) YRS.push(y);
    let html = `<table class="cal" id="calTable"><caption class="sr">Fires per month, 2000–2025</caption><thead><tr><th scope="col"></th>${YRS.map((y) => `<th scope="col" class="yr${y === 2012 ? " split" : ""}">${y % 5 === 0 || y === 2012 || y === 2025 ? `'${String(y).slice(2)}` : ""}</th>`).join("")}</tr></thead><tbody>`;
    for (let m = 1; m <= 12; m++) {
      html += `<tr><th scope="row" class="mon" data-m="${m}">${MON[m - 1]}</th>`;
      YRS.forEach((y) => {
        const r = byYM.get(`${y}-${m}`) || { harmonized: 0 }, t = maxLog > 0 ? Math.log10((r.harmonized || 0) + 1) / maxLog : 0;
        html += `<td class="${r.unusual ? "unusual" : ""}${y === 2012 ? " split" : ""}${y < 2012 ? " bc" : ""}" data-year="${y}" data-month="${m}" style="background:${(r.harmonized || 0) < 0.5 ? "#151a33" : fireCol(t)}"></td>`;
      });
      html += "</tr>";
    }
    host.innerHTML = html + "</tbody></table>";
    const mx = Math.pow(10, maxLog), tk = [1, 10, 100, 1000, 10000, 100000].filter((v) => v <= mx * 1.01);
    $("calLegend").innerHTML = `<div class="cl-bar"><i style="background:linear-gradient(90deg,#151a33 0%, ${FIRE.map((s, i) => `rgb(${s}) ${8 + (i / (FIRE.length - 1)) * 92}%`).join(",")})"></i>
      <span class="ticks"><span>0</span>${tk.map((v) => `<span>${big(v)}</span>`).join("")}</span><small>fires / month (log)</small></div>
      <ul class="cl-keys"><li><i class="k-unusual"></i>unusual</li><li><i class="k-bc"></i>2000–11 modelled from MODIS</li><li><i class="k-split"></i>VIIRS from 2012</li></ul>`;
    const flags = (data.calendar || []).filter((r) => r.unusual).sort((a, b) => (b.robust_z || 0) - (a.robust_z || 0));
    $("flagNote").textContent = flags.length ? `${flags.length} months stand out against that month's 2000–2025 median (robust z > 3.5). Click one.` : "No month stands out in this area.";
    $("flagList").innerHTML = flags.slice(0, 16).map((r) => `<li><button type="button" data-y="${r.year}" data-m="${r.month}"><b>${MON[r.month - 1]} ${r.year}</b><span>${big(r.harmonized)} fires · z ${fmt(r.robust_z, 1)}</span></button></li>`).join("");
    $("flagList").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => pulseCell(+b.dataset.y, +b.dataset.m)));
    const tb = document.querySelector('.og-tabs [data-pane="flags"]'); if (tb) tb.innerHTML = `Unusual<i>${flags.length}</i>`;
    const tip = $("tooltip");
    host.querySelectorAll("td[data-year]").forEach((td) => {
      td.addEventListener("mouseenter", (ev) => {
        const r = byYM.get(`${td.dataset.year}-${td.dataset.month}`); if (!r) return; tip.hidden = false;
        tip.innerHTML = `<strong>${MON[r.month - 1]} ${r.year}</strong> · ${r.source === "backcast" ? "modelled from MODIS" : "observed VIIRS"}<br>Fires: ${fmt(r.harmonized, 0)}` +
          (r.lo != null ? `<br>Model 90% interval: ${fmt(r.lo, 0)}–${fmt(r.hi, 0)}` : "") + `<br>MODIS raw: ${r.modis_raw}` + (r.viirs_obs == null ? "" : ` · VIIRS: ${r.viirs_obs}`) +
          `<br>Robust z: ${r.robust_z == null ? "—" : fmt(r.robust_z, 2)}${r.unusual ? " · <b>unusual</b>" : ""}`;
        posTip(ev);
      });
      td.addEventListener("mousemove", posTip); td.addEventListener("mouseleave", () => (tip.hidden = true));
    });
    highlightMonths();
  }
  function posTip(ev) { const t = $("tooltip"); t.style.left = Math.min(ev.clientX + 12, innerWidth - 250) + "px"; t.style.top = ev.clientY + 12 + "px"; }
  function pulseCell(y, m) { const td = document.querySelector(`#calTable td[data-year="${y}"][data-month="${m}"]`); if (!td) return; td.scrollIntoView({ block: "nearest", inline: "nearest" }); td.classList.remove("pulse"); void td.offsetWidth; td.classList.add("pulse"); }
  function highlightMonths() {
    const months = (state.action && state.action.months) || [];
    document.querySelectorAll("#calTable th[data-m], #calTable td").forEach((n) => n.classList.toggle("hl", months.includes(+(n.dataset.m || n.dataset.month))));
  }

  /* ---------- reasons + metrics ---------- */
  function renderReasons(rs) {
    const host = $("reasons");
    if (!rs || !Object.keys(rs).length) { host.textContent = "No overlap detections in this area."; return; }
    const items = [["VIIRS / MODIS ratio (2012–2025)", rs.viirs_modis_ratio], ["… mostly small fires (FRP < 10 MW)", rs.ratio_mostly_small_fires_frp_lt_10mw], ["… mostly larger fires", rs.ratio_mostly_larger_fires],
      ["… mostly night MODIS passes", rs.ratio_mostly_night_modis], ["… mostly day MODIS passes", rs.ratio_mostly_day_modis], ["MODIS detections", rs.overlap_modis_detections], ["VIIRS detections", rs.overlap_viirs_detections]];
    host.innerHTML = `<dl class="rs">${items.map(([k, v]) => `<dt>${k}</dt><dd>${v == null ? "—" : v}</dd>`).join("")}</dl><p class="fine">${esc(rs.explanation || "")}</p>`;
  }
  function renderMetrics(meta) {
    const c = meta.countries || {}; let html = "";
    for (const name of ["Canada", "Argentina"]) {
      const r = c[name]; if (!r || r.status !== "ok") continue;
      const rows = [["Global ratio", r.baselines.global_ratio], ["Month ratio", r.baselines.month_ratio], ["Cell ratio", r.baselines.cell_ratio], ["EB cell ratio", r.baselines.eb_cell_ratio], ["Residual LightGBM (mine)", r.tuned_residual_test, true]];
      html += `<h3>${name}</h3><table class="metrics"><thead><tr><th>Method</th><th>RMSE log1p</th><th>Bias %</th><th>Spearman</th><th>Monthly MAPE %</th></tr></thead><tbody>` +
        rows.map(([l, m, best]) => `<tr class="${best ? "best" : ""}"><td>${l}</td><td class="num">${fmt(m.rmse_log1p, 4)}</td><td class="num">${fmt(m.total_bias_pct, 2)}</td><td class="num">${fmt(m.spearman, 3)}</td><td class="num">${fmt(m.monthly_total_mape_pct, 2)}</td></tr>`).join("") + "</tbody></table>";
      const iv = r.intervals || {};
      html += `<p class="fine">Interval coverage ${fmt(iv.cqr_coverage, 3)} (90% target). ${r.beats_best_baseline_rmse_log1p ? "Beats the best simple baseline on log1p RMSE." : "Does not beat the best simple baseline on this seed."}</p>`;
    }
    $("metrics").innerHTML = html;
  }

  /* ---------- load ---------- */
  async function refresh() {
    const [w, s, e, n] = state.bbox, country = state.country;
    setStatus(`Loading ${presetLabel()}…`);
    try {
      const [cal, dis] = await Promise.all([getJSON(`/api/calendar?${q({ country, west: w, south: s, east: e, north: n })}`), getJSON(`/api/disagreement?${q({ country, west: w, south: s, east: e, north: n })}`)]);
      state.dis = dis; renderCalendar(cal); kpis(cal); renderReasons(cal.reasons);
      if (state.layer === "ratio") drawRatio();
      setStatus(`${presetLabel()}: ${dis.n.toLocaleString("en-US")} cells, 2000–2025 calendar loaded.`);
    } catch (err) { setStatus(`Failed to load: ${err.message}`, true); }
  }
  function enableDraw(on) { state.drawing = on; $("drawBtn").classList.toggle("active", on); $("drawBtn").textContent = on ? "Click two corners…" : "Draw a box"; map.getContainer().style.cursor = on ? "crosshair" : ""; }
  map.getContainer().addEventListener("click", (domEv) => {
    if (!state.drawing) return; if (domEv.target.closest && domEv.target.closest(".leaflet-control-container")) return;
    domEv.stopPropagation(); const ll = map.mouseEventToLatLng(domEv);
    if (!state.startLatLng) { state.startLatLng = ll; return; }
    const a = state.startLatLng; state.startLatLng = null; enableDraw(false); state.presetKey = "custom"; $("preset").value = "custom";
    setBBox([Math.min(a.lng, ll.lng), Math.min(a.lat, ll.lat), Math.max(a.lng, ll.lng), Math.max(a.lat, ll.lat)], state.country); refresh();
  }, true);
  $("drawBtn").addEventListener("click", () => { state.startLatLng = null; enableDraw(!state.drawing); });
  function usePreset(key, fly) {
    const p = state.meta.presets[key]; if (!p) return Promise.resolve();
    state.presetKey = key; $("preset").value = key; const changed = p.country !== state.country; setBBox(p.bbox, p.country);
    if (fly !== false) { if (key === "canada") fitCanada(); else fitTo([[p.bbox[1], p.bbox[0]], [p.bbox[3], p.bbox[2]]], { padding: [16, 16], maxZoom: 7 }); }
    if (changed && state.layer === "fire") drawFire();
    return refresh();
  }
  $("preset").addEventListener("change", () => usePreset($("preset").value));
  // Full Canada view (also deep link #view=canada): every Canada detection in frame, uncropped.
  function fullCanada() { if (state.c2 && state.action) state.c2.select(null); if (state.action) showAction(null); return usePreset("canada", true).then(() => { legend(); requestAnimationFrame(fitCanada); }); }
  $("canadaBtn").addEventListener("click", fullCanada);

  /* ---------- decision support (simulated) ---------- */
  // MODIS sinusoidal tile h11v03 (50–60°N), the burned-area tile behind +272 km²/yr: x from -7,783,459 m to -6,671,509 m.
  const R_E = 6371007.181, X0 = -7783459.0, X1 = -6671509.0;
  const tileH11V03 = (() => { const pts = [], lon = (x, lat) => (x / (R_E * Math.cos(lat * Math.PI / 180))) * 180 / Math.PI;
    for (let lat = 50; lat <= 60; lat++) pts.push([lat, lon(X0, lat)]); for (let lat = 60; lat >= 50; lat--) pts.push([lat, lon(X1, lat)]); return pts; })();
  const pin = (k, cls) => L.divIcon({ className: "hs-pin " + (cls || ""), html: `<span>${window.OGC2 ? OGC2.icon(k) : ""}</span>`, iconSize: [30, 30], iconAnchor: [15, 15] });
  const PLAN = {
    "hotspots-1": { months: [7], view: "trend", provinces: ["Alberta", "British Columbia"], asset: "crew", pick: (c) => (c[5] === "Alberta" || c[5] === "British Columbia" ? c[4] : -1), n: 6,
      unit: "July hot-spot cells", note: "Alberta and B.C.: rising (tentative). Crews staged at the cells with the most July fires." },
    "hotspots-2": { months: [5], view: "fire", asset: "notice", pick: (c) => c[3], n: 8, ring: true, unit: "May hot-spot cells", note: "Cells with the most May fires: where early-season notice goes first." },
    "hotspots-3": { months: [], view: "fire", tile: true, asset: "drone", unit: "MODIS burned-area tile", note: "MODIS MCD64A1 tile h11v03 (NE B.C., Alberta, Sask.): burned area +272 km²/yr (p = 0.004)." },
    "hotspots-4": { months: [], view: "trend", rising: true, asset: "plan", unit: "provinces with a significant rise", note: "Province trends, 2003–2025. Coloured = significant rise; grey = no significant trend." },
  };
  // Simulated tasking on the map: each queued task gets a marker at a target, and moves Proposed -> Queued -> Tasked -> In progress -> Done.
  const taskSt = {}; let zoneLayers = [], targets = [];
  const ZS = { pending: { color: "#fbbf24", fillColor: "#f97316", fillOpacity: 0.12 }, tasked: { color: "#9ec1ff", fillColor: "#9ec1ff", fillOpacity: 0.16 }, done: { color: "#6ee7b7", fillColor: "#6ee7b7", fillOpacity: 0.16 } };
  function drawAssets() {
    assetLayer.clearLayers(); const a = state.action; if (!a || !a.tasks || !targets.length) return;
    a.tasks.forEach((t, k) => {
      const st = taskSt[a.id + "|" + t.label] || "Proposed", ll = targets[k % targets.length];
      const html = `<div class="og-asset" data-s="${esc(st)}" style="margin-top:${(Math.floor(k / targets.length) * 26) - 22}px">${window.OGC2 ? OGC2.icon(t.asset) : ""}<span class="lb">${esc(t.label)}</span><em>${esc(st)}</em></div>`;
      L.marker(ll, { icon: L.divIcon({ className: "og-pin", html, iconSize: [0, 0] }), keyboard: false, interactive: false, zIndexOffset: 500 }).addTo(assetLayer);
    });
  }
  function zoneState() {
    const a = state.action; if (!a) return; const ts = (a.tasks || []).map((t) => taskSt[a.id + "|" + t.label]).filter(Boolean);
    const cls = !ts.length ? "pending" : ts.every((x) => x === "Done") ? "done" : "tasked";
    zoneLayers.forEach((l) => l.setStyle && l.setStyle(ZS[cls])); taskState(cls === "pending" ? "pending" : cls);
    selbar();
  }
  function selbar() {
    const box = $("mapSelbar"), a = state.action; if (!a) { box.hidden = true; return; }
    const on = state.c2 && state.c2.state.approved[a.id];
    box.hidden = false;
    box.innerHTML = `<span class="k">${esc(a.cls || "")}</span><span><b>${a.nTargets || 0}</b> ${esc(a.unit || "targets")}</span><button type="button" class="${on ? "done" : ""}">${on ? "Approved · Undo" : esc(a.verb || "Approve")}</button>`;
    box.querySelector("button").onclick = () => state.c2 && state.c2.approve(a.id);
  }
  async function showAction(a) {
    taskLayer.clearLayers(); assetLayer.clearLayers(); zoneLayers = []; targets = []; state.action = null; $("mapTask").hidden = true;
    if (!a) { highlightMonths(); selbar(); return; }
    const P = PLAN[a.id] || {}; state.action = Object.assign({ id: a.id, cls: a.cls, verb: a.verb, tasks: a.tasks }, P); highlightMonths();
    if (state.country !== "Canada") await usePreset("canada", false);
    if (P.view && P.view !== state.layer) setLayer(P.view);
    const d = await fireCells("Canada"), marks = [];
    if (P.provinces || P.rising) { if (!state.provs) state.provs = await getJSON("data/provinces_canada.json");
      const fs = state.provs.features.filter((f) => P.provinces ? P.provinces.includes(f.properties.name) : f.properties.h_p != null && f.properties.h_p < 0.05 && f.properties.h_slope > 0);
      const g = L.geoJSON({ type: "FeatureCollection", features: fs }, { style: Object.assign({ weight: 2.5, dashArray: "6 4" }, ZS.pending), interactive: false }).addTo(taskLayer);
      g.eachLayer((l) => zoneLayers.push(l));
      if (P.rising) g.eachLayer((l) => marks.push(l.getBounds().getCenter()));
      state.action.nTargets = fs.length; }
    if (P.tile) { const poly = L.polygon(tileH11V03, Object.assign({ weight: 2.5, dashArray: "6 4", interactive: false }, ZS.pending)).addTo(taskLayer); zoneLayers.push(poly); marks.push(poly.getBounds().getCenter()); state.action.nTargets = 1; }
    if (P.pick) {
      const top = d.cells.map((c) => [P.pick(c), c]).filter((x) => x[0] > 0).sort((x, y) => y[0] - x[0]), chosen = [];
      for (const [, c] of top) { if (chosen.every((o) => Math.hypot(o[0] - c[0], (o[1] - c[1]) * 0.5) > 1.6)) chosen.push(c); if (chosen.length >= (P.n || 6)) break; }
      chosen.forEach((c) => { const r = L.circle([c[0], c[1]], Object.assign({ radius: 60000, weight: 1.5, interactive: false }, ZS.pending)).addTo(taskLayer); zoneLayers.push(r); marks.push(L.latLng(c[0], c[1])); });
      state.action.nTargets = chosen.length;
    }
    marks.forEach((ll) => L.marker(ll, { icon: pin(P.asset, "pending"), keyboard: false, interactive: false }).addTo(taskLayer));
    targets = marks.slice(0, Math.max(1, Math.min(marks.length, (a.tasks || []).length)));
    if (P.provinces) fitTo([[48, -140], [61, -109]]);
    else if (P.tile) fitTo(L.polygon(tileH11V03).getBounds(), { padding: [40, 40] });
    else if (P.view === "trend") fitCanada();
    else if (marks.length) fitTo(L.latLngBounds(marks).pad(0.3), { maxZoom: 6 });
    state.action.noteTxt = P.note || ""; legend();
    drawAssets(); zoneState();
  }
  function taskState(cls) { document.querySelectorAll(".hs-pin").forEach((p) => { p.classList.remove("pending", "tasked", "done"); p.classList.add(cls); }); }
  const desk = () => window.innerWidth >= 1024;
  const toMap = () => { if (!desk()) $("mapSec").scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" }); };

  function mountC2() {
    const A = window.OG_APP; if (!window.OGC2 || !A) return;
    $("actN").textContent = A.actions.length;
    const c2 = OGC2.mount("#c2", { app: "hotspots", dock: true, title: "Recommended actions", kicker: "Decide & task", user: "Provincial fire managers and community planners", actions: A.actions,
      onSelect: (a, o) => { showAction(a); if (a && o && (o.source === "show" || o.source === "api")) toMap(); },
      onApprove: (a, on) => { (a.tasks || []).forEach((t) => { const k = a.id + "|" + t.label; if (on) taskSt[k] = "Queued"; else delete taskSt[k]; }); if (state.action && state.action.id === a.id) { drawAssets(); zoneState(); } },
      onTask: (a, t, s) => { taskSt[a.id + "|" + t.label] = s; if (state.action && state.action.id === a.id) { drawAssets(); zoneState(); } },
      onReset: () => { Object.keys(taskSt).forEach((k) => delete taskSt[k]); showAction(null); } });
    state.c2 = c2;
    OGC2.impact("#impactHost", A.impact, { title: "Impact: before → with this tool", note: "Qualitative on purpose: I haven't measured lives, hectares or costs. The numbers are the satellite results and model tests behind each decision." });
    // Deep links: #act=<id> selects an action; #alert=<id> opens its simulated alert (c2.js);
    // #demo or #demo=<id> is the capture state: select, approve (tasks run to Done in ~5 s) and open the alert draft.
    const m = /act=([\w-]+)/.exec(location.hash); if (m && c2) setTimeout(() => { c2.select(m[1]); toMap(); }, 700);
    const dm = /demo(?:=([\w-]+))?/.exec(location.hash);
    if (dm && c2) { const id = dm[1] || "hotspots-1"; setTimeout(() => { c2.select(id); setTimeout(() => { c2.approve(id); if ((A.actions.find((x) => x.id === id) || {}).alert) c2.alert(id, { quiet: true }); if (window.OGShell) OGShell.scrollDock(document.querySelector(`#c2 .c2-card[data-id="${id}"]`)); }, 900); }, 700); }
  }

  async function boot() {
    try {
      const meta = await getJSON("/api/meta"); state.meta = meta;
      $("preset").innerHTML = Object.entries(meta.presets).map(([k, p]) => `<option value="${k}">${esc(p.label)}</option>`).join("") + '<option value="custom" hidden>Custom area</option>';
      renderMetrics(meta); mountC2(); setLayer("fire");
      await usePreset("canada", true);
      if (/view=canada/.test(location.hash)) fullCanada();
    } catch (err) { setStatus(`Failed to start: ${err.message}`, true); console.error(err); }
  }
  boot();
})();
