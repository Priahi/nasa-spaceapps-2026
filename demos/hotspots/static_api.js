/* Static-hosting shim for the Hot Spots demo.
   Answers the same /api/* requests the FastAPI app serves, from precomputed files in data/:
   presets use exact server-computed JSON; a hand-drawn AOI is aggregated in the browser from the
   same cell-month tiles with the same math as app.py calendar_from(). */
(function () {
  const realFetch = window.fetch.bind(window);
  const cache = {};
  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const getJ = (u) => (cache[u] = cache[u] || realFetch(u).then((r) => { if (!r.ok) throw new Error(r.status + " " + u); return r.json(); }));
  let META = null;
  const metaP = getJ("data/meta.json").then((m) => (META = m));

  function presetFor(country, b) {
    for (const [k, p] of Object.entries(META.presets)) {
      if (p.country.toLowerCase() === country.toLowerCase() && p.bbox.every((v, i) => Math.abs(v - b[i]) < 1e-9)) return k;
    }
    return null;
  }

  async function tiles(country) {
    const c = country.toLowerCase();
    if (cache["bin_" + c]) return cache["bin_" + c];
    cache["bin_" + c] = (async () => {
      const schema = await getJ(`data/tiles_${c}.json`);
      const buf = await (await realFetch(`data/tiles_${c}.bin`)).arrayBuffer();
      const T = { n: schema.n };
      const ctor = { float32: Float32Array, int16: Int16Array, uint8: Uint8Array };
      schema.columns.forEach((col) => { T[col.name] = new ctor[col.dtype](buf, col.offset, schema.n); });
      return T;
    })();
    return cache["bin_" + c];
  }

  const median = (a) => { const s = a.filter((x) => !Number.isNaN(x)).sort((x, y) => x - y); const n = s.length; if (!n) return NaN; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };

  async function calendar(country, w, s, e, n) {
    const T = await tiles(country);
    const Y = 26, agg = {};
    for (let y = 0; y < Y; y++) for (let m = 1; m <= 12; m++) agg[y * 12 + m - 1] = { harmonized: 0, lo: 0, hi: 0, modis_raw: 0, viirs_obs: 0, model: 0, rows: 0, allBack: true };
    const ov = []; let nCells = 0;
    for (let i = 0; i < T.n; i++) {
      const lat = T.gy[i] * 0.25 + 0.125, lon = T.gx[i] * 0.25 + 0.125;
      if (lon < w || lon > e || lat < s || lat > n) continue;
      nCells++;
      const k = T.year[i] * 12 + T.month[i] - 1, a = agg[k];
      if (!a) continue;
      a.harmonized += T.v_equiv[i]; a.lo += T.lo[i]; a.hi += T.hi[i]; a.modis_raw += T.m_n[i];
      if (!Number.isNaN(T.v_n[i])) a.viirs_obs += T.v_n[i];
      a.model += T.v_model[i]; a.rows++; if (T.source[i] !== 0) a.allBack = false;
      if (T.source[i] !== 0) ov.push(i);
    }
    // robust z per calendar month across 2000-2025
    const z = {};
    for (let m = 1; m <= 12; m++) {
      const col = []; for (let y = 0; y < Y; y++) col.push(agg[y * 12 + m - 1].harmonized);
      const med = median(col); let mad = median(col.map((x) => Math.abs(x - med))); if (mad === 0) mad = NaN;
      for (let y = 0; y < Y; y++) z[y * 12 + m - 1] = 0.6745 * (col[y] - med) / mad;
    }
    const records = [];
    for (let y = 0; y < Y; y++) for (let m = 1; m <= 12; m++) {
      const k = y * 12 + m - 1, a = agg[k], year = 2000 + y, zz = z[k];
      const src = a.rows ? (a.allBack ? "backcast" : "observed") : (year < 2012 ? "backcast" : "observed");
      records.push({ year, month: m, harmonized: +a.harmonized.toFixed(2), lo: +a.lo.toFixed(2), hi: +a.hi.toFixed(2), modis_raw: Math.trunc(a.modis_raw),
        viirs_obs: year < 2012 ? null : Math.trunc(a.viirs_obs), model: +a.model.toFixed(2), robust_z: Number.isNaN(zz) ? null : +zz.toFixed(3),
        unusual: !Number.isNaN(zz) && Math.abs(zz) > 3.5, source: src });
    }
    const reasons = {};
    if (ov.length) {
      const sum = (idx, col) => idx.reduce((t, i) => t + (Number.isNaN(T[col][i]) ? 0 : T[col][i]), 0);
      const ratio = (idx) => { const mm = sum(idx, "m_n"), vv = sum(idx, "v_n"); return mm === 0 ? null : +(vv / mm).toFixed(3); };
      const mean = (col) => +(ov.reduce((t, i) => t + T[col][i], 0) / ov.length).toFixed(3);
      const f = (pred) => ov.filter(pred);
      reasons.overlap_modis_detections = Math.trunc(sum(ov, "m_n"));
      reasons.overlap_viirs_detections = Math.trunc(sum(ov, "v_n"));
      reasons.viirs_modis_ratio = ratio(ov);
      const low = f((i) => T.frac_low_frp[i] >= 0.6), high = f((i) => T.frac_low_frp[i] < 0.4);
      reasons.ratio_mostly_small_fires_frp_lt_10mw = low.length ? ratio(low) : null;
      reasons.ratio_mostly_larger_fires = high.length ? ratio(high) : null;
      const night = f((i) => T.m_night[i] >= 0.5), day = f((i) => T.m_night[i] < 0.5);
      reasons.ratio_mostly_night_modis = night.length ? ratio(night) : null;
      reasons.ratio_mostly_day_modis = day.length ? ratio(day) : null;
      const aq = f((i) => T.m_aqua[i] >= 0.5), te = f((i) => T.m_aqua[i] < 0.5);
      reasons.ratio_mostly_aqua = aq.length ? ratio(aq) : null;
      reasons.ratio_mostly_terra = te.length ? ratio(te) : null;
      reasons.mean_night_fraction_modis = mean("m_night");
      reasons.mean_aqua_fraction_modis = mean("m_aqua");
      reasons.mean_low_frp_fraction = mean("frac_low_frp");
      reasons.explanation = "VIIRS (375 m) detects more small and cooler fires than MODIS (1 km). A higher VIIRS/MODIS ratio in low-FRP or night-heavy cell-months is the expected physical pattern, not a bug. The residual model learns that correction on top of an empirical-Bayes cell-ratio baseline.";
    }
    const flagged = records.filter((r) => r.unusual).sort((a, b) => Math.abs(b.robust_z) - Math.abs(a.robust_z)).slice(0, 16);
    return { country, bbox: [w, s, e, n], n_cell_months: nCells, computed: "in-browser from static tiles", calendar: records, flagged, reasons, months: MONTHS,
      note: "one seed, not a published benchmark. 2000-2011 values are model back-casts; 2012+ are observed VIIRS. Bands are Mondrian CQR 90% model intervals summed over AOI cells." };
  }

  async function calendarAny(country, b) {
    await metaP;
    const k = presetFor(country, b);
    if (k) return getJ(`data/calendar_${k}.json`);
    return calendar(country, b[0], b[1], b[2], b[3]);
  }

  async function disagreement(country, w, s, e, n, limit) {
    const d = await getJ(`data/disagreement_${country.toLowerCase()}.json`);
    let cells = d.cells.filter((c) => c.lon >= w && c.lon <= e && c.lat >= s && c.lat <= n && (c.m_n + c.v_n) > 0);
    const trunc = cells.length >= limit;
    if (cells.length > limit) cells = cells.slice().sort((a, b) => (b.m_n + b.v_n) - (a.m_n + a.v_n)).slice(0, limit);
    return { country, n: cells.length, truncated: trunc ? 1 : 0, cells };
  }

  const json = (o) => new Response(JSON.stringify(o), { status: 200, headers: { "Content-Type": "application/json" } });
  window.fetch = async function (input, init) {
    const url = typeof input === "string" ? input : input.url;
    if (!/^\/api\//.test(url)) return realFetch(input, init);
    const u = new URL(url, location.href), p = Object.fromEntries(u.searchParams);
    const title = (s) => s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
    const b = ["west", "south", "east", "north"].map((k) => +p[k]);
    try {
      if (u.pathname === "/api/meta") return json(await metaP);
      if (u.pathname === "/api/health") return json({ ok: true, ready: true, static: true });
      if (u.pathname === "/api/calendar") return json(await calendarAny(title(p.country), b));
      if (u.pathname === "/api/disagreement") return json(await disagreement(title(p.country), b[0], b[1], b[2], b[3], +(p.limit || 12000)));
    } catch (err) { return new Response(JSON.stringify({ error: String(err) }), { status: 503 }); }
    return new Response("not found", { status: 404 });
  };

  // CSV export without a server: same header block and columns as /api/export.csv
  document.addEventListener("click", async (ev) => {
    const btn = ev.target.closest && ev.target.closest("#csvBtn");
    if (!btn) return;
    ev.stopImmediatePropagation(); ev.preventDefault();
    const lbl = document.getElementById("aoiLabel").textContent;
    const m = /AOI (-?[\d.]+), (-?[\d.]+) to (-?[\d.]+), (-?[\d.]+)\s+·\s+(\w+)/.exec(lbl);
    if (!m) return;
    const b = m.slice(1, 5).map(Number), country = m[5];
    const cal = await calendarAny(country, window.__hotspotsBBox || b);
    const lines = [
      "# Harmonized MODIS-VIIRS burning activity calendar",
      `# country=${country} bbox=[${(window.__hotspotsBBox || b).join(",")}]`,
      "# 2000-2011: model back-cast (VIIRS-equivalent). 2012+: observed VIIRS S-NPP.",
      "# lo/hi: Mondrian CQR 90% model interval, summed over cells (not a formal regional interval).",
      "# unusual: |robust z| > 3.5 vs 2000-2025 per-month median/MAD.",
      "# one seed, not a published benchmark. Data: NASA FIRMS MODIS C6.1 and VIIRS S-NPP.",
      "# Licence: Apache-2.0 for this tool. Cite FIRMS: https://firms.modaps.eosdis.nasa.gov/",
      "year,month,harmonized_count,model_lo,model_hi,modis_raw,viirs_obs,model,source,robust_z_vs_month_climatology,unusual",
    ];
    cal.calendar.forEach((r) => lines.push([r.year, r.month, r.harmonized, r.lo, r.hi, r.modis_raw, r.viirs_obs == null ? "" : r.viirs_obs, r.model, r.source, r.robust_z == null ? "" : r.robust_z, r.unusual ? "True" : "False"].join(",")));
    const blob = new Blob([lines.join("\n") + "\n"], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `harmonized_calendar_${country.toLowerCase()}_${b.map((v) => v.toFixed(2)).join("_")}.csv`;
    document.body.appendChild(a); a.click(); a.remove();
  }, true);
})();
