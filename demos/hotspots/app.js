/* Local FIRMS Hot Spots demo. One seed, not a published benchmark. */
(function () {
  const $ = (id) => document.getElementById(id);
  const state = {
    meta: null,
    presetKey: "canada",
    country: "Canada",
    bbox: [-141.0, 41.7, -52.6, 83.1],
    drawing: false,
    rect: null,
    startLatLng: null,
    layer: null,
  };

  const map = L.map("map", { worldCopyJump: true, preferCanvas: true }).setView([60, -96], 3);
  L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
    attribution: "Tiles &copy; Esri",
    maxZoom: 16,
  }).addTo(map);
  const cellsLayer = L.layerGroup().addTo(map);
  const boxLayer = L.layerGroup().addTo(map);

  function ratioColor(v) {
    // RdBu-like, v in [-3, 3]
    const x = Math.max(-3, Math.min(3, v));
    const t = (x + 3) / 6;
    const stops = [
      [33, 102, 172],
      [103, 169, 207],
      [209, 229, 240],
      [247, 247, 247],
      [253, 219, 199],
      [239, 138, 98],
      [178, 24, 43],
    ];
    const p = t * (stops.length - 1);
    const i = Math.min(stops.length - 2, Math.floor(p));
    const f = p - i;
    const a = stops[i], b = stops[i + 1];
    const r = Math.round(a[0] + (b[0] - a[0]) * f);
    const g = Math.round(a[1] + (b[1] - a[1]) * f);
    const bl = Math.round(a[2] + (b[2] - a[2]) * f);
    return `rgb(${r},${g},${bl})`;
  }

  function inferno(t) {
    // compact inferno-like ramp, t in [0,1]
    t = Math.max(0, Math.min(1, t));
    const stops = [
      [0, 0, 4],
      [40, 11, 84],
      [101, 21, 111],
      [159, 42, 99],
      [212, 72, 66],
      [245, 125, 21],
      [250, 193, 39],
      [252, 255, 164],
    ];
    const p = t * (stops.length - 1);
    const i = Math.min(stops.length - 2, Math.floor(p));
    const f = p - i;
    const a = stops[i], b = stops[i + 1];
    return `rgb(${Math.round(a[0] + (b[0] - a[0]) * f)},${Math.round(a[1] + (b[1] - a[1]) * f)},${Math.round(a[2] + (b[2] - a[2]) * f)})`;
  }

  function fmt(n, d) {
    if (n === null || n === undefined || Number.isNaN(n)) return "—";
    return Number(n).toFixed(d);
  }

  function q(params) {
    return new URLSearchParams(params).toString();
  }

  async function getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    return res.json();
  }

  function setStatus(msg, err) {
    const el = $("status");
    el.textContent = msg;
    el.className = err ? "err" : "";
  }

  function currentBBox() {
    return state.bbox;
  }

  function setBBox(bbox, country, fly) {
    state.bbox = bbox.map(Number);
    window.__hotspotsBBox = state.bbox;
    if (country) state.country = country;
    const [w, s, e, n] = state.bbox;
    boxLayer.clearLayers();
    state.rect = L.rectangle([[s, w], [n, e]], {
      color: "#e8a317",
      weight: 2,
      fillOpacity: 0.04,
    }).addTo(boxLayer);
    $("aoiLabel").textContent = `AOI ${w.toFixed(2)}, ${s.toFixed(2)} to ${e.toFixed(2)}, ${n.toFixed(2)}  ·  ${state.country}`;
    if (fly) {
      map.fitBounds([[s, w], [n, e]], { padding: [20, 20], maxZoom: 7 });
    }
  }

  function fillPresets(presets) {
    const sel = $("preset");
    sel.innerHTML = "";
    Object.entries(presets).forEach(([k, p]) => {
      const o = document.createElement("option");
      o.value = k;
      o.textContent = p.label;
      sel.appendChild(o);
    });
    sel.value = "canada";
  }

  function renderMetrics(meta) {
    const host = $("metrics");
    const c = meta.countries || {};
    let html = "";
    for (const name of ["Canada", "Argentina"]) {
      const r = c[name];
      if (!r || r.status !== "ok") {
        html += `<p>${name}: metrics not ready.</p>`;
        continue;
      }
      const rows = [
        ["baseline global ratio", r.baselines.global_ratio, false],
        ["baseline month ratio", r.baselines.month_ratio, false],
        ["baseline cell ratio", r.baselines.cell_ratio, false],
        ["baseline EB cell ratio", r.baselines.eb_cell_ratio, false],
        ["v2 residual LightGBM (tuned)", r.tuned_residual_test, true],
      ];
      const ref = (meta.colab_v1_reference || {})[name];
      html += `<h3 style="margin:0.4rem 0 0.3rem;font-size:0.85rem;">${name}</h3>`;
      html += `<table class="metrics"><thead><tr><th>Method</th><th>RMSE log1p</th><th>Bias %</th><th>Spearman</th><th>Monthly MAPE %</th></tr></thead><tbody>`;
      rows.forEach(([label, m, best]) => {
        html += `<tr class="${best && r.beats_best_baseline_rmse_log1p ? "best" : ""}"><td>${label}</td><td class="num">${fmt(m.rmse_log1p, 4)}</td><td class="num">${fmt(m.total_bias_pct, 2)}</td><td class="num">${fmt(m.spearman, 3)}</td><td class="num">${fmt(m.monthly_total_mape_pct, 2)}</td></tr>`;
      });
      if (ref) {
        html += `<tr class="ref"><td>Colab v1 tuned LGBM (before fix)</td><td class="num">${fmt(ref.tuned_lgbm_rmse_log1p, 4)}</td><td class="num">${fmt(ref.tuned_lgbm_bias_pct, 2)}</td><td class="num">${fmt(ref.tuned_lgbm_spearman, 3)}</td><td class="num">—</td></tr>`;
      }
      html += `</tbody></table>`;
      const iv = r.intervals || {};
      html += `<p class="fine">CQR coverage overall ${fmt(iv.cqr_coverage, 3)}, on VIIRS-active cells ${fmt(iv.cqr_coverage_on_viirs_active_cells, 3)} (90% target). ${r.beats_best_baseline_rmse_log1p ? "Beats the best simple baseline on log1p RMSE." : "Does not beat the best simple baseline on this seed."}</p>`;
    }
    host.innerHTML = html;
  }

  function renderReasons(reasons) {
    const host = $("reasons");
    if (!reasons || !Object.keys(reasons).length) {
      host.textContent = "No overlap detections in this AOI.";
      return;
    }
    const items = [
      ["VIIRS / MODIS ratio (2012–2025)", reasons.viirs_modis_ratio],
      ["Ratio, mostly small fires (FRP < 10 MW)", reasons.ratio_mostly_small_fires_frp_lt_10mw],
      ["Ratio, mostly larger fires", reasons.ratio_mostly_larger_fires],
      ["Ratio, mostly night MODIS overpasses", reasons.ratio_mostly_night_modis],
      ["Ratio, mostly day MODIS overpasses", reasons.ratio_mostly_day_modis],
      ["Ratio, mostly Aqua", reasons.ratio_mostly_aqua],
      ["Ratio, mostly Terra", reasons.ratio_mostly_terra],
      ["Mean MODIS night fraction", reasons.mean_night_fraction_modis],
      ["Mean Aqua fraction", reasons.mean_aqua_fraction_modis],
      ["Mean low-FRP fraction", reasons.mean_low_frp_fraction],
      ["MODIS detections in AOI", reasons.overlap_modis_detections],
      ["VIIRS detections in AOI", reasons.overlap_viirs_detections],
    ];
    let html = '<div class="reasons"><dl>';
    items.forEach(([k, v]) => {
      html += `<dt>${k}</dt><dd>${v === null || v === undefined ? "—" : v}</dd>`;
    });
    html += `</dl><p>${reasons.explanation || ""}</p></div>`;
    host.innerHTML = html;
  }

  function renderCalendar(data) {
    const host = $("calendar");
    const months = data.months || ["J","F","M","A","M","J","J","A","S","O","N","D"];
    const byYM = new Map();
    let maxLog = 0;
    (data.calendar || []).forEach((r) => {
      byYM.set(`${r.year}-${r.month}`, r);
      maxLog = Math.max(maxLog, Math.log10((r.harmonized || 0) + 1));
    });
    const years = [];
    for (let y = 2000; y <= 2025; y++) years.push(y);
    let html = `<table class="cal" id="calTable"><thead><tr><th></th>`;
    months.forEach((m) => { html += `<th>${m[0]}</th>`; });
    html += `</tr></thead><tbody>`;
    years.forEach((y) => {
      html += `<tr class="${y === 2012 ? "split" : ""}"><th class="year">${y}</th>`;
      for (let m = 1; m <= 12; m++) {
        const r = byYM.get(`${y}-${m}`) || { harmonized: 0, unusual: false, source: y < 2012 ? "backcast" : "observed" };
        const t = maxLog > 0 ? Math.log10((r.harmonized || 0) + 1) / maxLog : 0;
        const cls = `${r.unusual ? "unusual" : ""} ${r.source === "backcast" ? "backcast" : ""}`;
        html += `<td class="${cls}" data-year="${y}" data-month="${m}" style="background:${inferno(t)}"></td>`;
      }
      html += `</tr>`;
    });
    html += `</tbody></table>`;
    host.innerHTML = html;

    const tip = $("tooltip");
    host.querySelectorAll("td[data-year]").forEach((td) => {
      td.addEventListener("mouseenter", (ev) => {
        const r = byYM.get(`${td.dataset.year}-${td.dataset.month}`);
        if (!r) return;
        const mon = months[r.month - 1] || r.month;
        tip.hidden = false;
        tip.innerHTML = `<strong>${mon} ${r.year}</strong> · ${r.source}<br>` +
          `Harmonized count: ${fmt(r.harmonized, 1)}<br>` +
          (r.source === "backcast" || r.lo != null ? `Model 90% interval: ${fmt(r.lo, 1)} – ${fmt(r.hi, 1)}<br>` : "") +
          `MODIS raw: ${r.modis_raw}<br>` +
          (r.viirs_obs === null || r.viirs_obs === undefined ? "VIIRS: not yet flying<br>" : `VIIRS observed: ${r.viirs_obs}<br>`) +
          `Robust z: ${r.robust_z === null || r.robust_z === undefined ? "—" : fmt(r.robust_z, 2)}` +
          (r.unusual ? " · unusual month" : "");
        positionTip(ev);
      });
      td.addEventListener("mousemove", positionTip);
      td.addEventListener("mouseleave", () => { tip.hidden = true; });
    });
  }

  function positionTip(ev) {
    const tip = $("tooltip");
    tip.style.left = ev.clientX + 12 + "px";
    tip.style.top = ev.clientY + 12 + "px";
  }

  function renderCells(payload) {
    cellsLayer.clearLayers();
    (payload.cells || []).forEach((c) => {
      const r = L.circleMarker([c.lat, c.lon], {
        radius: Math.max(2, Math.min(8, Math.log1p((c.m_n || 0) + (c.v_n || 0)) * 0.7)),
        color: ratioColor(c.log2_ratio || 0),
        weight: 0.5,
        fillOpacity: 0.75,
        fillColor: ratioColor(c.log2_ratio || 0),
      });
      r.bindTooltip(
        `cell ${c.lat.toFixed(2)}, ${c.lon.toFixed(2)}<br>MODIS ${c.m_n} · VIIRS ${c.v_n}<br>log2 ratio ${fmt(c.log2_ratio, 2)}`,
        { sticky: true }
      );
      r.addTo(cellsLayer);
    });
  }

  async function refresh() {
    const [w, s, e, n] = currentBBox();
    const country = state.country;
    setStatus(`Loading ${country} AOI…`);
    try {
      const [cal, dis] = await Promise.all([
        getJSON(`/api/calendar?${q({ country, west: w, south: s, east: e, north: n })}`),
        getJSON(`/api/disagreement?${q({ country, west: w, south: s, east: e, north: n })}`),
      ]);
      renderCalendar(cal);
      renderReasons(cal.reasons);
      renderCells(dis);
      setStatus(`Loaded ${dis.n} cells and a 2000–2025 calendar for this AOI. One seed, not a published benchmark.`);
    } catch (err) {
      setStatus(`Failed to load AOI data: ${err.message}`, true);
    }
  }

  function enableDraw(on) {
    state.drawing = on;
    $("drawBtn").classList.toggle("active", on);
    $("drawBtn").textContent = on ? "Click two corners…" : "Draw box on map";
    map.getContainer().style.cursor = on ? "crosshair" : "";
  }

  // Listen on the container (capture) so clicks inside the current AOI rectangle or on
  // canvas-drawn cell markers still count as box corners (Leaflet's canvas renderer swallows them).
  map.getContainer().addEventListener("click", (domEv) => {
    if (!state.drawing) return;
    if (domEv.target.closest && domEv.target.closest(".leaflet-control-container")) return;
    domEv.stopPropagation();
    const ev = { latlng: map.mouseEventToLatLng(domEv) };
    if (!state.startLatLng) {
      state.startLatLng = ev.latlng;
      return;
    }
    const a = state.startLatLng;
    const b = ev.latlng;
    state.startLatLng = null;
    enableDraw(false);
    const west = Math.min(a.lng, b.lng);
    const east = Math.max(a.lng, b.lng);
    const south = Math.min(a.lat, b.lat);
    const north = Math.max(a.lat, b.lat);
    // Keep the country of the current preset; user can switch preset if they cross countries.
    setBBox([west, south, east, north], state.country, false);
    refresh();
  }, true);

  $("drawBtn").addEventListener("click", () => {
    state.startLatLng = null;
    enableDraw(!state.drawing);
  });

  $("preset").addEventListener("change", () => {
    const key = $("preset").value;
    const p = state.meta.presets[key];
    state.presetKey = key;
    setBBox(p.bbox, p.country, true);
    refresh();
  });

  $("csvBtn").addEventListener("click", () => {
    const [w, s, e, n] = currentBBox();
    const url = `/api/export.csv?${q({ country: state.country, west: w, south: s, east: e, north: n })}`;
    const a = document.createElement("a");
    a.href = url;
    a.download = "";
    document.body.appendChild(a);
    a.click();
    a.remove();
  });

  async function boot() {
    try {
      const meta = await getJSON("/api/meta");
      state.meta = meta;
      if (!meta.countries || !Object.values(meta.countries).some((c) => c.status === "ok")) {
        setStatus("Model artifacts are not ready yet. Run train_harmonizer.py first.", true);
        return;
      }
      fillPresets(meta.presets);
      renderMetrics(meta);
      const p = meta.presets.canada;
      setBBox(p.bbox, p.country, true);
      await refresh();
    } catch (err) {
      setStatus(`Failed to start: ${err.message}`, true);
    }
  }

  boot();
})();
