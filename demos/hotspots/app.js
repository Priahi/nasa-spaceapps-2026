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
  const map = L.map("map", { worldCopyJump: true, preferCanvas: true, zoomSnap: 0.25 }).setView([58, -96], 3);
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", { attribution: "Tiles &copy; Esri", maxZoom: 16 }).addTo(map);
  const layers = { fire: L.layerGroup(), trend: L.layerGroup(), ratio: L.layerGroup() };
  const boxLayer = L.layerGroup().addTo(map), taskLayer = L.layerGroup().addTo(map);
  if ("ResizeObserver" in window) new ResizeObserver(() => map.invalidateSize()).observe($("map"));
  const fitCanada = () => map.fitBounds([[42, -141], [70, -52]]);

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
    $("kpis").innerHTML = `<h2>${esc(presetLabel())}</h2><dl class="kpi-grid">
        <div><dt>Peak month</dt><dd>${MON[peak]}</dd><small>most fires, 2000–2025</small></div>
        <div><dt>Biggest year</dt><dd>${top}</dd><small>${big(byYear[top])} fires</small></div>
        <div><dt>Unusual months</dt><dd>${flags.length}</dd><small>${flags.length ? `most often ${MON[fmMon]} (${fmMax})` : "none flagged"}</small></div>
        <div><dt>2025</dt><dd>${big(byYear[2025])}</dd><small>fires detected</small></div></dl>` + outlook(rows, byYear);
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
    return `<section class="outlook" aria-label="What to expect in 2026">
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
    let html = `<table class="cal" id="calTable"><caption class="sr">Fires per month, 2000–2025</caption><thead><tr><th scope="col"></th>${MON.map((m, i) => `<th scope="col" data-m="${i + 1}">${m}</th>`).join("")}</tr></thead><tbody>`;
    for (let y = 2000; y <= 2025; y++) {
      html += `<tr class="${y === 2012 ? "split" : ""}${y < 2012 ? " bc" : ""}"><th scope="row" class="year">${y}</th>`;
      for (let m = 1; m <= 12; m++) {
        const r = byYM.get(`${y}-${m}`) || { harmonized: 0 }, t = maxLog > 0 ? Math.log10((r.harmonized || 0) + 1) / maxLog : 0;
        html += `<td class="${r.unusual ? "unusual" : ""}" data-year="${y}" data-month="${m}" style="background:${(r.harmonized || 0) < 0.5 ? "#151a33" : fireCol(t)}"></td>`;
      }
      html += "</tr>";
    }
    host.innerHTML = html + "</tbody></table>";
    const mx = Math.pow(10, maxLog), tk = [1, 10, 100, 1000, 10000, 100000].filter((v) => v <= mx * 1.01);
    $("calLegend").innerHTML = `<div class="cl-bar"><i style="background:linear-gradient(90deg,#151a33 0%, ${FIRE.map((s, i) => `rgb(${s}) ${8 + (i / (FIRE.length - 1)) * 92}%`).join(",")})"></i>
      <span class="ticks"><span>0</span>${tk.map((v) => `<span>${big(v)}</span>`).join("")}</span><small>fires per month (log scale)</small></div>
      <ul class="cl-keys"><li><i class="k-unusual"></i>unusual month</li><li><i class="k-bc"></i>2000–2011: modelled from MODIS</li><li><i class="k-split"></i>2012: VIIRS starts</li></ul>`;
    const flags = (data.calendar || []).filter((r) => r.unusual).sort((a, b) => (b.robust_z || 0) - (a.robust_z || 0));
    $("flagNote").textContent = flags.length ? `${flags.length} months stand out against that month's 2000–2025 median (robust z > 3.5). Click one.` : "No month stands out in this area.";
    $("flagList").innerHTML = flags.slice(0, 16).map((r) => `<li><button type="button" data-y="${r.year}" data-m="${r.month}"><b>${MON[r.month - 1]} ${r.year}</b><span>${big(r.harmonized)} fires · z ${fmt(r.robust_z, 1)}</span></button></li>`).join("");
    $("flagList").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => pulseCell(+b.dataset.y, +b.dataset.m)));
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
      const rows = [["Global ratio", r.baselines.global_ratio], ["Month ratio", r.baselines.month_ratio], ["Cell ratio", r.baselines.cell_ratio], ["EB cell ratio", r.baselines.eb_cell_ratio], ["Residual LightGBM (ours)", r.tuned_residual_test, true]];
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
    if (fly !== false) { if (key === "canada") fitCanada(); else map.fitBounds([[p.bbox[1], p.bbox[0]], [p.bbox[3], p.bbox[2]]], { padding: [16, 16], maxZoom: 7 }); }
    if (changed && state.layer === "fire") drawFire();
    return refresh();
  }
  $("preset").addEventListener("change", () => usePreset($("preset").value));

  /* ---------- decision support (simulated) ---------- */
  // MODIS sinusoidal tile h11v03 (50–60°N), the burned-area tile behind +272 km²/yr: x from -7,783,459 m to -6,671,509 m.
  const R_E = 6371007.181, X0 = -7783459.0, X1 = -6671509.0;
  const tileH11V03 = (() => { const pts = [], lon = (x, lat) => (x / (R_E * Math.cos(lat * Math.PI / 180))) * 180 / Math.PI;
    for (let lat = 50; lat <= 60; lat++) pts.push([lat, lon(X0, lat)]); for (let lat = 60; lat >= 50; lat--) pts.push([lat, lon(X1, lat)]); return pts; })();
  const pin = (k, cls) => L.divIcon({ className: "hs-pin " + (cls || ""), html: `<span>${window.OGC2 ? OGC2.icon(k) : ""}</span>`, iconSize: [30, 30], iconAnchor: [15, 15] });
  const PLAN = {
    "hotspots-1": { months: [7], view: "trend", provinces: ["Alberta", "British Columbia"], asset: "crew", pick: (c) => (c[5] === "Alberta" || c[5] === "British Columbia" ? c[4] : -1), n: 6,
      note: "Alberta and B.C.: rising (tentative). Crews staged at the cells with the most July fires." },
    "hotspots-2": { months: [5], view: "fire", asset: "notice", pick: (c) => c[3], n: 8, ring: true, note: "Cells with the most May fires: where early-season notice goes first." },
    "hotspots-3": { months: [], view: "fire", tile: true, asset: "drone", note: "MODIS MCD64A1 tile h11v03 (NE B.C., Alberta, Sask.): burned area +272 km²/yr (p = 0.004)." },
    "hotspots-4": { months: [], view: "trend", asset: "plan", note: "Province trends, 2003–2025. Coloured = significant rise; grey = no significant trend." },
  };
  async function showAction(a) {
    taskLayer.clearLayers(); state.action = null; $("mapTask").hidden = true;
    if (!a) { highlightMonths(); return; }
    const P = PLAN[a.id] || {}; state.action = Object.assign({ id: a.id }, P); highlightMonths();
    if (state.country !== "Canada") await usePreset("canada", false);
    if (P.view && P.view !== state.layer) setLayer(P.view);
    const d = await fireCells("Canada"), marks = [];
    if (P.provinces) { if (!state.provs) state.provs = await getJSON("data/provinces_canada.json");
      L.geoJSON({ type: "FeatureCollection", features: state.provs.features.filter((f) => P.provinces.includes(f.properties.name)) }, { style: { color: "#fbbf24", weight: 2.5, fill: false }, interactive: false }).addTo(taskLayer); }
    if (P.tile) { const poly = L.polygon(tileH11V03, { color: "#fbbf24", weight: 2.5, dashArray: "6 4", fillColor: "#f97316", fillOpacity: 0.12, interactive: false }).addTo(taskLayer); marks.push(poly.getBounds().getCenter()); }
    if (P.pick) {
      const top = d.cells.map((c) => [P.pick(c), c]).filter((x) => x[0] > 0).sort((x, y) => y[0] - x[0]), chosen = [];
      for (const [, c] of top) { if (chosen.every((o) => Math.hypot(o[0] - c[0], (o[1] - c[1]) * 0.5) > 1.6)) chosen.push(c); if (chosen.length >= (P.n || 6)) break; }
      chosen.forEach((c) => { if (P.ring) L.circle([c[0], c[1]], { radius: 60000, color: "#fbbf24", weight: 1.5, fillOpacity: 0.06, interactive: false }).addTo(taskLayer); marks.push(L.latLng(c[0], c[1])); });
    }
    marks.forEach((ll) => L.marker(ll, { icon: pin(P.asset, "pending"), keyboard: false, interactive: false }).addTo(taskLayer));
    if (P.provinces) map.fitBounds([[48, -140], [61, -109]]);
    else if (P.tile) map.fitBounds(L.polygon(tileH11V03).getBounds(), { padding: [20, 20] });
    else if (P.view === "trend") fitCanada();
    else if (marks.length) map.fitBounds(L.latLngBounds(marks).pad(0.3), { maxZoom: 6 });
    $("mapTask").hidden = false; $("mapTask").innerHTML = `<b>${esc(a.cls)}</b><span>${esc(P.note || "")}</span>`;
  }
  function taskState(cls) { document.querySelectorAll(".hs-pin").forEach((p) => { p.classList.remove("pending", "tasked", "done"); p.classList.add(cls); }); }
  const toMap = () => $("mapSec").scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });

  function mountC2() {
    const A = window.OG_APP; if (!window.OGC2 || !A) return;
    const c2 = OGC2.mount("#c2", { app: "hotspots", title: "Recommended actions", kicker: "Decide & task", user: "Provincial fire managers and community planners", actions: A.actions,
      onSelect: (a, o) => { showAction(a); if (a && o && o.source === "show") toMap(); },
      onApprove: (a, on) => { if (state.action && state.action.id === a.id) taskState(on ? "tasked" : "pending"); },
      onTask: (a, t, s) => { if (s === "Done" && state.action && state.action.id === a.id) taskState("done"); },
      onReset: () => showAction(null) });
    OGC2.impact("#impactHost", A.impact, { title: "Impact: before → with this tool", note: "Qualitative on purpose: we haven't measured lives, hectares or costs. The numbers are the satellite results and model tests behind each decision." });
    const m = /act=([\w-]+)/.exec(location.hash); if (m && c2) setTimeout(() => { c2.select(m[1]); toMap(); }, 700);
  }

  async function boot() {
    try {
      const meta = await getJSON("/api/meta"); state.meta = meta;
      $("preset").innerHTML = Object.entries(meta.presets).map(([k, p]) => `<option value="${k}">${esc(p.label)}</option>`).join("") + '<option value="custom" hidden>Custom area</option>';
      renderMetrics(meta); mountC2(); setLayer("fire");
      await usePreset("canada", true);
    } catch (err) { setStatus(`Failed to start: ${err.message}`, true); console.error(err); }
  }
  boot();
})();
