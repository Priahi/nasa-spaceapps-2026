/* Trend Detective widgets: interactive annual time series + Sen's slope, and trend maps.
   Data: /assets/data/trends.json, produced by trends/analyze.py (Mann-Kendall + Sen's slope). */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const UP = "#c39bff", DOWN = "#5fa8ff", FLAT = "rgba(190,205,255,.16)";
  const el = (tag, attrs, parent) => { const n = document.createElementNS(NS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; };
  const h = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const median = (a) => { const s = [...a].sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
  function fmt(v) {
    const a = Math.abs(v);
    if (a === 0) return "0";
    if (a >= 1000) return Math.round(v).toLocaleString("en-US");
    if (a >= 100) return v.toFixed(0);
    if (a >= 10) return v.toFixed(1);
    if (a >= 1) return v.toFixed(2);
    return v.toFixed(a >= 0.01 ? 3 : 4);
  }
  const sgn = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + fmt(Math.abs(v));
  const pfmt = (p) => (p < 0.001 ? "< 0.001" : p.toFixed(3));
  const colorOf = (t) => (!t || t.trend === "no trend" ? FLAT : t.trend === "increasing" ? UP : DOWN);

  /* ---------- chart ---------- */
  function chart(box, t, opts = {}) {
    box.innerHTML = "";
    const narrow = !opts.small && box.clientWidth && box.clientWidth < 520;
    const W = opts.w || (narrow ? 360 : 640), H = opts.h || (narrow ? 250 : 300), small = !!opts.small;
    const m = small ? { l: 4, r: 4, t: 6, b: 6 } : { l: narrow ? 50 : 58, r: 22, t: 16, b: 30 };
    const xs = t.x, ys = t.series;
    const x0 = xs[0], x1 = xs[xs.length - 1];
    let lo = Math.min(...ys), hi = Math.max(...ys); const pad = (hi - lo) * 0.08 || 1; lo -= pad; hi += pad;
    if (lo < 0 && Math.min(...ys) >= 0) lo = 0;
    let ticks = [];
    if (!small) { const raw = (hi - lo) / 4, mag = Math.pow(10, Math.floor(Math.log10(raw))), st = [1, 2, 2.5, 5, 10].map((k) => k * mag).find((k) => k >= raw);
      lo = Math.floor(lo / st) * st; hi = Math.ceil(hi / st) * st; for (let v = lo; v <= hi + st / 2; v += st) ticks.push(+v.toPrecision(12)); }
    const X = (x) => m.l + ((x - x0) / (x1 - x0)) * (W - m.l - m.r);
    const Y = (y) => H - m.b - ((y - lo) / (hi - lo)) * (H - m.t - m.b);
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, class: "tchart-svg", role: "img", "aria-label": opts.label || "time series" }, box);
    if (!small) {
      for (const v of ticks) { const y = Y(v); el("line", { x1: m.l, x2: W - m.r, y1: y, y2: y, class: "grid" }, svg); el("text", { x: m.l - 8, y: y + 4, "text-anchor": "end", class: "ax" }, svg).textContent = fmt(v); }
      const step = (x1 - x0) > 30 ? 10 : 5;
      for (let yr = Math.ceil(x0 / step) * step; yr <= x1; yr += step) el("text", { x: X(yr), y: H - 8, "text-anchor": "middle", class: "ax" }, svg).textContent = yr;
    }
    const d = xs.map((x, i) => `${i ? "L" : "M"}${X(x).toFixed(1)},${Y(ys[i]).toFixed(1)}`).join("");
    el("path", { d, class: "series" }, svg);
    const b = t.sen_slope_per_year, a = median(ys.map((y, i) => y - b * xs[i]));
    el("line", { x1: X(x0), y1: Y(a + b * x0), x2: X(x1), y2: Y(a + b * x1), class: "sen", stroke: t.trend === "no trend" ? "#8b95ad" : colorOf(t), "stroke-dasharray": t.trend === "no trend" ? "6 5" : "none" }, svg);
    if (opts.mark) { const yr = opts.mark; if (yr >= x0 && yr <= x1) { el("line", { x1: X(yr), x2: X(yr), y1: m.t, y2: H - m.b, class: "mark" }, svg); if (!small) el("text", { x: X(yr) + 4, y: m.t + 10, class: "ax mk" }, svg).textContent = opts.markLabel || yr; } }
    if (small) return;
    const dots = xs.map((x, i) => el("circle", { cx: X(x), cy: Y(ys[i]), r: 3.2, class: "pt" }, svg));
    const guide = el("line", { y1: m.t, y2: H - m.b, class: "guide", opacity: 0 }, svg);
    const tip = h("div", "ttip"); box.appendChild(tip);
    const move = (ev) => {
      const r = svg.getBoundingClientRect(), px = ((ev.clientX - r.left) / r.width) * W;
      let i = Math.round(((px - m.l) / (W - m.l - m.r)) * (xs.length - 1)); i = Math.max(0, Math.min(xs.length - 1, i));
      dots.forEach((c, j) => c.classList.toggle("on", j === i));
      guide.setAttribute("x1", X(xs[i])); guide.setAttribute("x2", X(xs[i])); guide.setAttribute("opacity", 1);
      tip.innerHTML = `<b>${xs[i]}</b> ${fmt(ys[i])}<span>trend line ${fmt(a + b * xs[i])}</span>`;
      tip.style.left = `${(X(xs[i]) / W) * 100}%`; tip.style.opacity = 1;
    };
    svg.addEventListener("pointermove", move); svg.addEventListener("pointerdown", move);
    svg.addEventListener("pointerleave", () => { guide.setAttribute("opacity", 0); tip.style.opacity = 0; dots.forEach((c) => c.classList.remove("on")); });
  }

  /* ---------- verdict (the four detective questions) ---------- */
  function verdict(box, t, what, where) {
    const sig = t.p < 0.05, hr = t.p_hamed_rao;
    const robust = sig ? (hr < 0.05 ? "Still significant after correcting for autocorrelation (Hamed-Rao p " + pfmt(hr) + ")." : "Not significant after correcting for autocorrelation (Hamed-Rao p " + pfmt(hr) + "), so treat as weaker evidence.") : "";
    const dir = t.trend === "increasing" ? "Rising" : t.trend === "decreasing" ? "Falling" : "No clear trend";
    box.innerHTML = `
      <div class="q"><span>What is changing?</span><p>${esc(what)}</p></div>
      <div class="q"><span>Where?</span><p>${esc(where)} · ${t.years[0]}–${t.years[1]} (${t.n} years)</p></div>
      <div class="q"><span>How much?</span><p><b class="${sig ? "grad" : ""}">${sgn(t.sen_slope_per_year)}</b> per year <small>(95% CI ${sgn(t.sen_ci95[0])} to ${sgn(t.sen_ci95[1])})</small>${t.slope_pct_of_median_per_decade == null ? `<br><small>≈ ${sgn(10 * t.sen_slope_per_year)} per decade</small>` : `<br><small>≈ ${t.slope_pct_of_median_per_decade > 0 ? "+" : ""}${t.slope_pct_of_median_per_decade.toFixed(1)}% of the typical year per decade</small>`}</p></div>
      <div class="q verdict-${sig ? (t.trend === "increasing" ? "up" : "down") : "none"}"><span>Is it significant?</span><p><b>${sig ? "Yes" : "No"}</b>: ${dir.toLowerCase()} (Mann-Kendall p ${pfmt(t.p)}, α 0.05). <small>${esc(robust)}</small></p></div>`;
  }

  function seg(container, label, items, value, onChange) {
    const wrap = h("div", "seg"); wrap.setAttribute("role", "group"); wrap.setAttribute("aria-label", label);
    const lab = h("span", "seg-l", esc(label)); wrap.appendChild(lab);
    items.forEach(([v, txt]) => { const b = h("button", "", esc(txt)); b.type = "button"; b.dataset.v = v; b.setAttribute("aria-pressed", v === value); b.onclick = () => { wrap.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b)); onChange(v); }; wrap.appendChild(b); });
    container.appendChild(wrap); return wrap;
  }
  function select(container, label, items, value, onChange) {
    const wrap = h("label", "sel"); wrap.innerHTML = `<span class="seg-l">${esc(label)}</span>`;
    const s = document.createElement("select"); items.forEach(([v, txt]) => { const o = document.createElement("option"); o.value = v; o.textContent = txt; if (v === value) o.selected = true; s.appendChild(o); });
    s.onchange = () => onChange(s.value); wrap.appendChild(s); container.appendChild(wrap); return s;
  }
  function legend(box, extra) {
    box.innerHTML = `<span><i style="background:${UP}"></i>significant rise</span><span><i style="background:${DOWN}"></i>significant fall</span><span><i style="background:${FLAT}"></i>no significant trend</span>${extra || ""}`;
  }

  /* ---------- grid map (POWER cells) ---------- */
  function gridMap(box, cells, opts = {}) {
    box.innerHTML = "";
    const lons = [...new Set(cells.map((c) => c.lon))].sort((a, b) => a - b), lats = [...new Set(cells.map((c) => c.lat))].sort((a, b) => a - b);
    const dx = lons[1] - lons[0], dy = lats[1] - lats[0];
    const minx = lons[0] - dx / 2, maxx = lons.at(-1) + dx / 2, miny = lats[0] - dy / 2, maxy = lats.at(-1) + dy / 2;
    const kx = Math.cos(((miny + maxy) / 2) * Math.PI / 180);
    const W = box.clientWidth && box.clientWidth < 460 ? Math.max(240, box.clientWidth - 56) : 400, H = Math.round((W * (maxy - miny)) / ((maxx - minx) * kx));
    const svg = el("svg", { viewBox: `-50 -4 ${W + 54} ${H + 26}`, class: "gmap", role: "img", "aria-label": opts.label || "trend map" }, box);
    const X = (lon) => ((lon - minx) / (maxx - minx)) * W, Y = (lat) => H - ((lat - miny) / (maxy - miny)) * H;
    const maxAbs = Math.max(...cells.map((c) => Math.abs(c.slope))) || 1;
    cells.forEach((c) => {
      const sig = c.p < 0.05, col = c.slope > 0 ? UP : DOWN, op = sig ? 0.95 : 0.12 + 0.3 * Math.abs(c.slope) / maxAbs;
      const r = el("rect", { x: X(c.lon - dx / 2) + 1, y: Y(c.lat + dy / 2) + 1, width: X(minx + dx) - 2, height: Y(maxy - dy) - 2, rx: 4, fill: col, "fill-opacity": op, class: sig ? "cell sig" : "cell" }, svg);
      el("title", {}, r).textContent = `${Math.abs(c.lon).toFixed(3)}°${c.lon < 0 ? "W" : "E"}, ${c.lat.toFixed(1)}°N: ${c.trend} (p ${pfmt(c.p)}), Sen ${sgn(c.slope)}/yr`;
    });
    (opts.pins || []).forEach(([lon, lat, name]) => { el("circle", { cx: X(lon), cy: Y(lat), r: 5, class: "pin" }, svg); el("text", { x: X(lon) + 8, y: Y(lat) + 4, class: "pin-t" }, svg).textContent = name; });
    lons.forEach((lon, i) => { if (i % 2 === 0) el("text", { x: X(lon), y: H + 16, "text-anchor": "middle", class: "ax" }, svg).textContent = `${Math.abs(lon).toFixed(1)}°${lon < 0 ? "W" : "E"}`; });
    lats.forEach((lat, i) => { if (i % 2 === 0) el("text", { x: -4, y: Y(lat) + 4, "text-anchor": "end", class: "ax" }, svg).textContent = `${lat.toFixed(1)}°N`; });
  }

  /* ---------- widgets ---------- */
  const FIRE_VARS = [["harmonized_count", "Harmonized count"], ["modis_count", "MODIS only"], ["modis_frp", "MODIS FRP"], ["viirs_count", "VIIRS only"]];
  const FIRE_WHAT = { harmonized_count: "Active-fire detections per year, on the VIIRS scale (Hot Spots harmonized record: model back-cast 2003–2011, observed VIIRS 2012+)", modis_count: "MODIS active-fire detections per year (single sensor, Terra + Aqua)", modis_frp: "Total MODIS fire radiative power per year (GW, summed over detections): how much energy the fires released", viirs_count: "VIIRS S-NPP active-fire detections per year (observed only, from 2012)" };
  function fireWidget(root, D) {
    const F = D.fire, regions = Object.keys(F.canada).filter((k) => !F.canada[k].note);
    let reg = "Canada", v = "harmonized_count";
    const ctr = h("div", "tw-ctrl"), body = h("div", "tw-body"), mapBox = h("div", "tw-map"), right = h("div", "tw-right"), chartBox = h("div", "tchart"), ver = h("div", "verdict"), leg = h("div", "legend");
    root.append(ctr, body); body.append(mapBox, right); right.append(chartBox, ver);
    const get = () => (reg === "Argentina" ? F.argentina : F.canada[reg])[v];
    const sel = select(ctr, "Region", [...regions.map((r) => [r, r === "Canada" ? "Canada (all)" : r]), ["Argentina", "Argentina (all)"]], reg, (r) => { reg = r; draw(); });
    seg(ctr, "Series", FIRE_VARS, v, (x) => { v = x; draw(); });
    const svg = el("svg", { viewBox: `0 0 ${F.map.w} ${F.map.h}`, class: "pmap", role: "img", "aria-label": "Map of Canadian provinces coloured by fire trend" }, mapBox);
    mapBox.appendChild(leg); const fcap = h("p", "map-cap", "Click a province. Argentina is tested as one national series (no map)."); mapBox.appendChild(fcap);
    const paths = {};
    for (const [name, d] of Object.entries(F.map.paths)) {
      const p = el("path", { d, class: "prov", tabindex: F.canada[name] && !F.canada[name].note ? 0 : -1 }, svg); el("title", {}, p); paths[name] = p;
      if (F.canada[name] && !F.canada[name].note) { p.addEventListener("click", () => { reg = name; sel.value = name; draw(); }); p.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); p.dispatchEvent(new Event("click")); } }); }
    }
    function draw() {
      for (const [name, p] of Object.entries(paths)) {
        const r = F.canada[name], t = r && !r.note ? r[v] : null;
        p.setAttribute("fill", t ? colorOf(t) : "url(#none)"); p.classList.toggle("nodata", !t); p.classList.toggle("on", name === reg || reg === "Canada");
        p.querySelector("title").textContent = t ? `${name}: ${t.trend} (p ${pfmt(t.p)}), ${sgn(t.sen_slope_per_year)}/yr` : `${name}: too few detections to test`;
      }
      mapBox.classList.toggle("dim", reg === "Argentina");
      const t = get();
      chart(chartBox, t, { label: `${reg} ${v} per year`, mark: v === "harmonized_count" ? 2012 : null, markLabel: "VIIRS starts" });
      verdict(ver, t, FIRE_WHAT[v], reg === "Canada" ? "All of Canada" : reg === "Argentina" ? "All of Argentina" : reg + ", Canada");
    }
    el("defs", {}, svg).innerHTML = '<pattern id="none" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="rgba(190,205,255,.05)"/><line x1="0" y1="0" x2="0" y2="6" stroke="rgba(190,205,255,.25)" stroke-width="1.5"/></pattern>';
    legend(leg, '<span><i class="hatch"></i>too few detections</span>');
    draw();
  }

  const WATER_VARS = [["annual_total", "Annual total"], ["rx1day", "Wettest day"], ["days_ge_20mm", "Heavy-rain days"], ["imerg", "Annual total (GPM IMERG)"], ["grace", "Water storage (GRACE)"]];
  const ED_WHAT = { grace: "Total water storage (all water on and under the land), annual mean anomaly in cm of equivalent water, GRACE/GRACE-FO JPL mascons", imerg: "Total precipitation per year (mm), GPM IMERG V07 satellite rainfall" };
  const edSeries = (D, v, reg) => (D.earthdata && D.earthdata[v] && D.earthdata[v][reg]) || null;
  function edMap(box, cap, t, v) { box.innerHTML = `<div class="ed-ph"><b>${v === "grace" ? "GRACE / GRACE-FO" : "GPM IMERG"}</b><span>${v === "grace" ? "Gravity satellites weigh the water. Mascons are about 3° (~300 km) wide, so this box is one regional value, not a map." : "Satellite rainfall, 0.1° grid, averaged over the box."}</span></div>`; cap.textContent = v === "grace" ? `Monthly ${t.first_month.slice(0, 7)} to ${t.last_month.slice(0, 7)}, seasonal cycle removed, annual means.${t.years_missing && t.years_missing.length ? " No annual value for " + t.years_missing.join(", ") + " (GRACE to GRACE-FO gap)." : ""}` : "Annual totals from monthly files, 1998–2024. The box includes some sea (Valencia) or Great Lakes (Ontario)."; }
  const WATER_WHAT = { annual_total: "Total precipitation per year (mm, regional mean)", rx1day: "Rain on the wettest day of the year (mm, Rx1day)", days_ge_20mm: "Days per year with ≥ 20 mm of rain" };
  const WATER_REG = { valencia: ["Eastern Spain (Valencia)", [[-0.38, 39.47, "Valencia"]]], ontario: ["Southern Ontario (Toronto)", [[-79.38, 43.65, "Toronto"]]] };
  function waterWidget(root, D) {
    const Wd = D.water; let reg = "valencia", v = "rx1day";
    const ctr = h("div", "tw-ctrl"), body = h("div", "tw-body"), mapCol = h("div", "tw-map"), mapBox = h("div", ""), cap = h("p", "map-cap"), right = h("div", "tw-right"), chartBox = h("div", "tchart"), ver = h("div", "verdict"), leg = h("div", "legend");
    root.append(ctr, body); body.append(mapCol, right); mapCol.append(mapBox, cap, leg); right.append(chartBox, ver);
    seg(ctr, "Region", Object.entries(WATER_REG).map(([k, x]) => [k, x[0]]), reg, (x) => { reg = x; draw(); });
    seg(ctr, "Index", WATER_VARS.filter(([k]) => !["grace", "imerg"].includes(k) || (D.earthdata && D.earthdata[k] && Object.keys(D.earthdata[k]).length)), v, (x) => { v = x; draw(); });
    legend(leg, '<span><i class="ring"></i>p &lt; 0.05 cell</span>');
    function draw() {
      if (v === "grace" || v === "imerg") { const t = edSeries(D, v, reg); if (t) { leg.style.display = "none"; edMap(mapBox, cap, t, v); chart(chartBox, t, { label: ED_WHAT[v], mark: v === "grace" ? 2017 : null, markLabel: "GRACE → GRACE-FO gap" }); verdict(ver, t, ED_WHAT[v], WATER_REG[reg][0]); return; } }
      leg.style.display = "";
      const R = Wd[reg], mk = v === "annual_total" ? "map_total" : "map_rx1day";
      gridMap(mapBox, R[mk].cells, { pins: WATER_REG[reg][1], label: "Per-cell trend map" });
      cap.textContent = `Each square is one MERRA-2 cell (0.625° × 0.5°). Map: ${v === "annual_total" ? "annual total" : "wettest day"}: ${R[mk].n_sig_increasing} of ${R[mk].cells.length} cells rise significantly, ${R[mk].n_sig_decreasing} fall.`;
      chart(chartBox, R[v], { label: WATER_WHAT[v], mark: reg === "valencia" ? 2024 : null, markLabel: "2024 DANA flood" });
      verdict(ver, R[v], WATER_WHAT[v], WATER_REG[reg][0]);
    }
    draw();
  }

  const CROP_VARS = [["frost_free_days", "Frost-free days"], ["first_fall_frost_doy", "First autumn frost"], ["last_spring_frost_doy", "Last spring frost"], ["gdd_may_sep", "Corn GDD"], ["rootzone_wetness_may_sep", "Root-zone wetness"], ["precip_may_sep", "May–Sep rain"], ["hot_days_jja", "Hot days"], ["gldas_root", "Soil moisture (GLDAS)"], ["grace", "Water storage (GRACE)"]];
  const CROP_WHAT = { frost_free_days: "Length of the frost-free season (days from last spring to first autumn frost, Tmin ≤ 0 °C)", first_fall_frost_doy: "Date of the first autumn frost (day of year; higher = later)", last_spring_frost_doy: "Date of the last spring frost (day of year; lower = earlier)", gdd_may_sep: "Corn growing degree days, May–Sep (base 10 °C, cap 30 °C)", rootzone_wetness_may_sep: "Root-zone soil wetness, May–Sep mean (0–1, NASA POWER GWETROOT)", precip_may_sep: "Growing-season precipitation, May–Sep (mm)", hot_days_jja: "Summer days (Jun–Aug) with Tmax ≥ 32 °C" };
  function cropWidget(root, D) {
    const C = D.crops; let v = "frost_free_days", sc = "region";
    const ctr = h("div", "tw-ctrl"), body = h("div", "tw-body"), mapCol = h("div", "tw-map"), mapBox = h("div", ""), cap = h("p", "map-cap"), right = h("div", "tw-right"), chartBox = h("div", "tchart"), ver = h("div", "verdict"), leg = h("div", "legend");
    root.append(ctr, body); body.append(mapCol, right); mapCol.append(mapBox, cap, leg); right.append(chartBox, ver);
    select(ctr, "Indicator", CROP_VARS.filter(([k]) => k === "grace" ? edSeries(D, "grace", "iowa") : k === "gldas_root" ? D.earthdata && D.earthdata.gldas && D.earthdata.gldas.RootMoist_inst : true), v, (x) => { v = x; draw(); });
    seg(ctr, "Scale", [["region", "Central Iowa"], ["story_cell", "Story County cell"]], sc, (x) => { sc = x; draw(); });
    legend(leg, '<span><i class="ring"></i>p &lt; 0.05 cell</span>');
    function draw() {
      if (v === "grace" || v === "gldas_root") {
        const t = v === "grace" ? edSeries(D, "grace", "iowa") : D.earthdata.gldas.RootMoist_inst;
        leg.style.display = "none";
        if (v === "grace") edMap(mapBox, cap, t, "grace"); else { mapBox.innerHTML = '<div class="ed-ph"><b>GLDAS Noah 2.1</b><span>Land-surface model soil moisture, 0.25° grid, averaged over central Iowa. Root zone = 0–100 cm.</span></div>'; cap.textContent = "Monthly 2000 onward, May–Sep mean per year."; }
        const what = v === "grace" ? ED_WHAT.grace : "Root-zone soil moisture (0–100 cm, kg/m²), May–Sep mean, GLDAS Noah 2.1";
        chart(chartBox, t, { label: what, mark: v === "grace" ? 2017 : null, markLabel: "GRACE → GRACE-FO gap" }); verdict(ver, t, what, "Central Iowa (95–92°W, 41–44°N)"); return;
      }
      leg.style.display = "";
      const M = C[v].map;
      gridMap(mapBox, M.cells, { pins: [[-93.47, 42.03, "Story County"]], label: "Per-cell trend map, central Iowa" });
      cap.textContent = `Central Iowa, 35 MERRA-2 cells: ${M.n_sig_increasing} rise significantly, ${M.n_sig_decreasing} fall.`;
      chart(chartBox, C[v][sc], { label: CROP_WHAT[v] });
      verdict(ver, C[v][sc], CROP_WHAT[v], sc === "region" ? "Central Iowa (95–92°W, 41–44°N)" : "Story County, Iowa (MERRA-2 cell at 93.75°W, 42.0°N)");
    }
    draw();
  }

  function sparks(D) {
    document.querySelectorAll("[data-spark]").forEach((n) => {
      const path = n.dataset.spark.split(".");
      let t = D; for (const k of path) t = t && t[k];
      n.classList.add("tchart"); if (t && t.series) chart(n, t, { small: true, w: 300, h: 90, mark: n.dataset.mark ? +n.dataset.mark : null });
    });
  }

  const roots = document.querySelectorAll("[data-trend],[data-spark]");
  if (!roots.length) return;
  fetch("/assets/data/trends.json").then((r) => r.json()).then((D) => {
    document.querySelectorAll("[data-trend]").forEach((root) => {
      root.classList.add("ready");
      ({ fire: fireWidget, water: waterWidget, crops: cropWidget })[root.dataset.trend](root, D);
    });
    sparks(D);
  }).catch((err) => { document.querySelectorAll("[data-trend]").forEach((r) => (r.innerHTML = '<p class="map-cap">Trend data failed to load. The full results are in trends/RESULTS.md.</p>')); console.warn(err); });
})();
