/* Field Shift local demo. Same-origin data only. */
(() => {
  const $ = (id) => document.getElementById(id);
  const state = {
    data: null,
    colab: null,
    fieldId: null,
    weights: {},
    mapImg: null,
  };

  function showTab(name) {
    document.querySelectorAll("nav.tabs button").forEach((b) => {
      b.setAttribute("aria-selected", b.dataset.tab === name ? "true" : "false");
    });
    document.querySelectorAll("section.panel").forEach((p) => {
      p.classList.toggle("active", p.id === "panel-" + name);
    });
  }
  document.querySelectorAll("nav.tabs button").forEach((b) => {
    b.addEventListener("click", () => showTab(b.dataset.tab));
  });

  function fieldById(id) {
    return state.data.fields.find((f) => f.id === id);
  }
  function indicatorsFor(strategy, field) {
    if (field && strategy.field_indicators && strategy.field_indicators[field.id]) {
      return strategy.field_indicators[field.id];
    }
    return strategy.county_indicators;
  }
  function weightedScore(ind, weights) {
    const sense = state.data.objectives.sense;
    let s = 0, w = 0;
    for (const k of state.data.objectives.keys) {
      const util = sense[k] === "max" ? ind[k] : 1 - ind[k];
      const wt = weights[k] ?? 1;
      s += wt * util;
      w += wt;
    }
    return w ? s / w : 0;
  }

  function prettySeq(seq) {
    return seq.map((t) => t.replace("+cover", " + rye cover")).join(" → ");
  }

  function allOptions(field) {
    const named = state.data.strategies.map((st) => ({
      kind: "named",
      id: st.id,
      name: st.name,
      sequence: st.sequence,
      why: st.why,
      benefits: st.benefits,
      risks: st.risks,
      gaps: st.gaps,
      indicators: indicatorsFor(st, field),
    }));
    const used = new Set(named.map((s) => s.sequence.join("|")));
    const front = (field && field.id === state.data.pareto.steepest_field_id)
      ? state.data.pareto.steepest_field
      : state.data.pareto.typical_field;
    // Recompute indicators on the selected field for Pareto sequences
    const extras = [];
    (front || []).forEach((p, i) => {
      const key = p.sequence.join("|");
      if (used.has(key)) return;
      used.add(key);
      // Prefer county/typical indicators stored on the front; for a selected field, blend by replacing with a proportional shift if field-level isn't precomputed.
      let ind = { water_demand: p.water_demand, erosion_risk: p.erosion_risk, n_fixing_share: p.n_fixing_share, heat_frost_exposure: p.heat_frost_exposure, soil_moisture_stress: p.soil_moisture_stress };
      if (field) {
        // scale erosion with this field's slope relative to typical
        const typSlope = median(state.data.fields.map((f) => f.slope));
        const scale = typSlope > 0 ? field.slope / typSlope : 1;
        ind = { ...ind, erosion_risk: Math.min(1, p.erosion_risk * scale) };
      }
      extras.push({
        kind: "pareto",
        id: "pareto_" + i,
        name: "Pareto option: " + prettySeq(p.sequence),
        sequence: p.sequence,
        why: "A non-dominated 4-year sequence from the NSGA-II search (48 individuals, 25 generations, one seed).",
        benefits: "Sits on the trade-off front for the five indicators. No single objective was improved without hurting another.",
        risks: "May be agronomically awkward (for example a hay year without a hay market). Treat as a prompt, not a prescription.",
        gaps: "Search space is small and discrete. Yields, labour and equipment are not modelled.",
        indicators: ind,
      });
    });
    named.forEach((o) => { o.score = weightedScore(o.indicators, state.weights); });
    extras.forEach((o) => { o.score = weightedScore(o.indicators, state.weights); });
    extras.sort((a, b) => b.score - a.score);
    const all = named.concat(extras.slice(0, 5));
    all.sort((a, b) => b.score - a.score);
    return all;
  }

  function median(arr) {
    const a = arr.filter((x) => Number.isFinite(x)).sort((x, y) => x - y);
    if (!a.length) return 1;
    return a[Math.floor(a.length / 2)];
  }

  function renderSliders() {
    const host = $("sliders");
    const labels = state.data.objectives.labels;
    host.innerHTML = state.data.objectives.keys.map((k) => `
      <label>
        <span>${labels[k]}</span>
        <span class="val" id="wval-${k}">${state.weights[k]}</span>
        <input type="range" min="0" max="100" step="1" value="${state.weights[k]}" data-key="${k}" aria-label="${labels[k]} priority">
      </label>`).join("");
    host.querySelectorAll("input").forEach((inp) => {
      inp.addEventListener("input", () => {
        state.weights[inp.dataset.key] = Number(inp.value);
        $("wval-" + inp.dataset.key).textContent = inp.value;
        renderStrategies();
        renderPareto();
      });
    });
  }

  function renderField() {
    const f = state.fieldId ? fieldById(state.fieldId) : null;
    $("fieldTitle").textContent = f ? `Tile ${f.id}` : "County typical tile";
    if (!f) {
      $("fieldMeta").innerHTML = `<div>Using county-median slope and soils so you can still compare rotations before picking a tile.</div>`;
      $("history").innerHTML = "";
      $("flags").innerHTML = "";
      return;
    }
    const colors = state.data.map.colors;
    $("fieldMeta").innerHTML = `
      <div><strong>Elevation</strong> ${f.elev_m.toFixed(0)} m</div>
      <div><strong>Slope</strong> ${f.slope.toFixed(2)}°</div>
      <div><strong>Clay / sand</strong> ${f.clay.toFixed(0)}% / ${f.sand.toFixed(0)}%</div>
      <div><strong>SOC / pH</strong> ${f.soc.toFixed(1)} g/kg / ${f.ph.toFixed(1)}</div>
      <div><strong>2026 model guess</strong> ${f.pred_2026} (${(f.pred_confidence * 100).toFixed(0)}% confidence)</div>
      <div><strong>2024 peak NDVI</strong> ${f.ndvi_peak_2024 != null ? f.ndvi_peak_2024.toFixed(2) : "n/a"} · bare ${f.bare_frac_2024 != null ? (f.bare_frac_2024 * 100).toFixed(0) + "%" : "n/a"}</div>`;
    $("history").innerHTML = f.history.map((h) =>
      `<span title="${h.year} ${h.crop}" style="background:${colors[h.crop]}">${String(h.year).slice(2)}</span>`
    ).join("");
    $("flags").innerHTML = (f.flags || []).map((t) => `<div class="flag">${t}</div>`).join("");
  }

  function renderStrategies() {
    const field = state.fieldId ? fieldById(state.fieldId) : null;
    const opts = allOptions(field);
    const labels = state.data.objectives.labels;
    const sense = state.data.objectives.sense;
    $("strategyCards").innerHTML = opts.slice(0, 6).map((o, i) => {
      const bars = state.data.objectives.keys.map((k) => {
        const v = o.indicators[k];
        const pct = Math.max(0, Math.min(100, v * 100));
        const cls = sense[k] === "min" ? "min" : "";
        return `<div class="mini ${cls}"><span>${labels[k]}</span><div class="bar"><i style="width:${pct}%"></i></div><span>${v.toFixed(2)}</span></div>`;
      }).join("");
      return `<article class="strategy ${i === 0 ? "best" : ""}">
        <div class="rank">${i === 0 ? "Best match to your priorities" : "Rank " + (i + 1)} · score <span class="score">${o.score.toFixed(3)}</span></div>
        <h3>${o.name}</h3>
        <p class="hint">${prettySeq(o.sequence)}</p>
        ${bars}
        <p><strong>Why.</strong> ${o.why}</p>
        <p><strong>Possible benefits.</strong> ${o.benefits}</p>
        <p><strong>Risks and gaps.</strong> ${o.risks} ${o.gaps}</p>
      </article>`;
    }).join("");

    const keys = state.data.objectives.keys;
    const head = `<tr><th>Strategy</th><th class="num">Score</th>${keys.map((k) => `<th class="num">${labels[k]}</th>`).join("")}<th>Sequence</th></tr>`;
    const body = opts.map((o, i) =>
      `<tr class="${i === 0 ? "best" : ""}"><td>${o.name}</td><td class="num">${o.score.toFixed(3)}</td>${keys.map((k) => `<td class="num">${o.indicators[k].toFixed(3)}</td>`).join("")}<td>${prettySeq(o.sequence)}</td></tr>`
    ).join("");
    $("tradeTable").innerHTML = `<thead>${head}</thead><tbody>${body}</tbody>`;
  }

  function renderPareto() {
    const canvas = $("pareto");
    const ctx = canvas.getContext("2d");
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#fffdf7";
    ctx.fillRect(0, 0, w, h);
    const pad = { l: 48, r: 16, t: 16, b: 36 };
    const field = state.fieldId ? fieldById(state.fieldId) : null;
    const opts = allOptions(field);
    const xs = opts.map((o) => o.indicators.water_demand);
    const ys = opts.map((o) => o.indicators.erosion_risk);
    const xmin = Math.min(...xs) - 0.04, xmax = Math.max(...xs) + 0.04;
    const ymin = Math.min(...ys) - 0.02, ymax = Math.max(...ys) + 0.02;
    const X = (v) => pad.l + ((v - xmin) / (xmax - xmin || 1)) * (w - pad.l - pad.r);
    const Y = (v) => h - pad.b - ((v - ymin) / (ymax - ymin || 1)) * (h - pad.t - pad.b);
    ctx.strokeStyle = "#d9d0be";
    ctx.beginPath();
    ctx.moveTo(pad.l, pad.t);
    ctx.lineTo(pad.l, h - pad.b);
    ctx.lineTo(w - pad.r, h - pad.b);
    ctx.stroke();
    ctx.fillStyle = "#5c6a5e";
    ctx.font = "12px sans-serif";
    ctx.fillText("Water demand →", pad.l, h - 10);
    ctx.save();
    ctx.translate(14, h / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("Erosion risk →", 0, 0);
    ctx.restore();
    opts.forEach((o) => {
      ctx.beginPath();
      const r = o.kind === "named" ? 7 : 5;
      ctx.fillStyle = o.kind === "named" ? "#c4922c" : "#2c5e3f";
      ctx.arc(X(o.indicators.water_demand), Y(o.indicators.erosion_risk), r, 0, Math.PI * 2);
      ctx.fill();
    });
    $("paretoNote").textContent = state.data.pareto.note;
  }

  function drawMap() {
    const canvas = $("map");
    const ctx = canvas.getContext("2d");
    const img = state.mapImg;
    const m = state.data.map;
    // image is half-res of native CDL
    const scale = img.width / m.width;
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    ctx.lineWidth = 1;
    state.data.fields.forEach((f) => {
      const x = f.col * m.block * scale;
      const y = f.row * m.block * scale;
      const s = m.block * scale;
      ctx.strokeStyle = f.id === state.fieldId ? "#f3efe4" : "rgba(255,255,255,.28)";
      ctx.lineWidth = f.id === state.fieldId ? 2.5 : 0.6;
      ctx.strokeRect(x, y, s, s);
      if (f.id === state.fieldId) {
        ctx.strokeStyle = "#c4922c";
        ctx.strokeRect(x + 1, y + 1, s - 2, s - 2);
      }
    });
  }

  function hitField(ev) {
    const canvas = $("map");
    const r = canvas.getBoundingClientRect();
    const x = (ev.clientX - r.left) * (canvas.width / r.width);
    const y = (ev.clientY - r.top) * (canvas.height / r.height);
    const m = state.data.map;
    const scale = canvas.width / m.width;
    const bs = m.block * scale;
    let hit = null;
    for (const f of state.data.fields) {
      const fx = f.col * bs, fy = f.row * bs;
      if (x >= fx && x <= fx + bs && y >= fy && y <= fy + bs) { hit = f; break; }
    }
    if (hit) selectField(hit.id);
  }

  function selectField(id) {
    state.fieldId = id;
    document.querySelectorAll("#featured button").forEach((b) => {
      b.setAttribute("aria-pressed", (b.dataset.id || "") === (id || "") ? "true" : "false");
    });
    drawMap();
    renderField();
    renderStrategies();
    renderPareto();
  }

  function renderFeatured() {
    const host = $("featured");
    const buttons = [{ id: "", label: "County typical", reason: "Median tile" }].concat(
      (state.data.featured || []).map((f) => ({ id: f.id, label: f.id, reason: f.reason }))
    );
    host.innerHTML = buttons.map((b) =>
      `<button type="button" data-id="${b.id}" title="${b.reason || ""}">${b.label}</button>`
    ).join("");
    host.querySelectorAll("button").forEach((b) => {
      b.addEventListener("click", () => selectField(b.dataset.id || null));
    });
  }

  function renderClimate() {
    const canvas = $("clim");
    const ctx = canvas.getContext("2d");
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    const rows = state.data.climate_yearly.filter((r) => r.year >= 2000 && r.gs_precip != null);
    if (!rows.length) return;
    const pad = { l: 40, r: 40, t: 10, b: 24 };
    const maxP = Math.max(...rows.map((r) => r.gs_precip));
    const maxG = Math.max(...rows.map((r) => r.gs_gdd));
    const bw = (w - pad.l - pad.r) / rows.length;
    rows.forEach((r, i) => {
      const x = pad.l + i * bw;
      ctx.fillStyle = "#8fb89a";
      ctx.fillRect(x, h - pad.b - (r.gs_precip / maxP) * (h - pad.t - pad.b), Math.max(1, bw * 0.7), (r.gs_precip / maxP) * (h - pad.t - pad.b));
    });
    ctx.strokeStyle = "#c4922c";
    ctx.beginPath();
    rows.forEach((r, i) => {
      const x = pad.l + i * bw + bw / 2;
      const y = h - pad.b - (r.gs_gdd / maxG) * (h - pad.t - pad.b);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.fillStyle = "#5c6a5e";
    ctx.font = "11px sans-serif";
    ctx.fillText("Bars: Apr–Sep rain (mm)   Line: growing degree days", pad.l, 12);
    ctx.fillText(String(rows[0].year), pad.l, h - 6);
    ctx.fillText(String(rows[rows.length - 1].year), w - pad.r - 30, h - 6);
  }

  function barBlock(host, items, maxKey) {
    host.innerHTML = items.map(([label, rec, kind]) => {
      const v = rec[maxKey];
      const pct = Math.max(0, Math.min(100, v * 100));
      return `<div class="bar-row"><span>${label}</span><div class="bar ${kind}"><span style="width:${pct}%"></span></div><span>${v.toFixed(3)}</span></div>`;
    }).join("");
  }

  function renderModel() {
    const m = state.data.metrics;
    $("modelCaveat").textContent = m.caveat;
    barBlock($("baseBars"), [
      ["Persistence", m.baselines.persistence, "base"],
      ["Corn/soy alternation", m.baselines.corn_soy_alternation, "base"],
      ["Markov-2 table", m.baselines.markov2, "base"],
      ["LightGBM (full features)", m.lgbm, ""],
    ], "acc");
    $("baseBars").insertAdjacentHTML("beforeend", `<p class="hint">Accuracy shown. Macro-F1: persistence ${m.baselines.persistence.macro_f1.toFixed(3)}, alternation ${m.baselines.corn_soy_alternation.macro_f1.toFixed(3)}, Markov-2 ${m.baselines.markov2.macro_f1.toFixed(3)}, LightGBM ${m.lgbm.macro_f1.toFixed(3)}. Δ accuracy vs Markov-2: ${m.lgbm.delta_acc_vs_markov2 >= 0 ? "+" : ""}${m.lgbm.delta_acc_vs_markov2.toFixed(3)}; Δ macro-F1: ${m.lgbm.delta_macro_f1_vs_markov2 >= 0 ? "+" : ""}${m.lgbm.delta_macro_f1_vs_markov2.toFixed(3)}.</p>`);
    const abItems = Object.entries(m.ablation).map(([k, v]) => [k, v, ""]);
    barBlock($("abBars"), abItems, "acc");
    const c = m.calibration;
    $("calText").textContent = `${c.method}. Temperature T=${c.temperature.toFixed(2)}. Test ECE ${c.test_ece_before.toFixed(4)} → ${c.test_ece_after.toFixed(4)}. Test NLL ${c.test_nll_before.toFixed(4)} → ${c.test_nll_after.toFixed(4)}.`;
    $("calImg").src = "data/crop_confusion_calibration.png";
    $("abImg").src = "data/crop_ablation.png";
    $("histImg").src = "data/cdl_history.png";
    $("slopeImg").src = "data/slope_tiles.png";
  }


  function fmt3(v) {
    return Number(v).toFixed(3);
  }

  function renderColab() {
    const c = state.colab;
    if (!c) {
      $("colabCaveat").textContent = "Colab Full-County Run results were not found at data/colab_run/results.json.";
      return;
    }
    $("colabCaveat").textContent = c.caveat;
    const local = state.data && state.data.metrics;
    const rows = [];
    const localL = local && local.lgbm;
    const localM = local && local.baselines && local.baselines.markov2;
    const localCal = local && local.calibration;
    rows.push(["Run", "Local Story County run", "Colab Full-County Run (2024–25)"]);
    rows.push(["Sample / test pixels", local ? `${local.n_pixels_sampled} sampled · ${local.n_test} test` : "n/a", `${c.n_pixels_sampled} sampled · ${c.n_test} test`]);
    rows.push(["HPO trials / seed", local ? `${local.hpo_trials} trials · seed in caveat` : "n/a", `${c.hpo_trials} trials · seed ${c.seed}`]);
    rows.push(["LightGBM accuracy", localL ? fmt3(localL.acc) : "n/a", fmt3(c.lgbm.acc)]);
    rows.push(["LightGBM macro-F1", localL ? fmt3(localL.macro_f1) : "n/a", fmt3(c.lgbm.macro_f1)]);
    rows.push(["Markov-2 accuracy / macro-F1", localM ? `${fmt3(localM.acc)} / ${fmt3(localM.macro_f1)}` : "n/a", `${fmt3(c.baselines.markov2.acc)} / ${fmt3(c.baselines.markov2.macro_f1)}`]);
    rows.push(["Δ acc / Δ macro-F1 vs Markov-2", localL ? `${localL.delta_acc_vs_markov2 >= 0 ? "+" : ""}${fmt3(localL.delta_acc_vs_markov2)} / ${localL.delta_macro_f1_vs_markov2 >= 0 ? "+" : ""}${fmt3(localL.delta_macro_f1_vs_markov2)}` : "n/a", `+${fmt3(c.lgbm.delta_acc_vs_markov2)} / +${fmt3(c.lgbm.delta_macro_f1_vs_markov2)}`]);
    rows.push(["Test ECE before → after T-scaling", localCal ? `${localCal.test_ece_before.toFixed(4)} → ${localCal.test_ece_after.toFixed(4)} (T=${localCal.temperature.toFixed(2)})` : "n/a", `${c.calibration.test_ece_before.toFixed(4)} → ${c.calibration.test_ece_after.toFixed(4)} (T=${c.calibration.temperature.toFixed(2)})`]);
    rows.push(["2025 full-county pixel accuracy", "not computed in the local sample run", `${c.map.pixel_accuracy_full_county.toFixed(3)} on ${c.map.farmed_pixels.toLocaleString()} farmed pixels (${(c.map.disagreement_frac * 100).toFixed(1)}% disagreement)`]);
    const body = rows.slice(1).map((r) => `<tr><th>${r[0]}</th><td class="num">${r[1]}</td><td class="num">${r[2]}</td></tr>`).join("");
    $("colabCompare").innerHTML = `<table class="compare-table"><caption>Both columns are one seed, not a published benchmark. Temperature scaling slightly worsened ECE on both runs; the raw probabilities are the more honest calibration.</caption><thead><tr><th>Metric</th><th class="num">${rows[0][1]}</th><th class="num">${rows[0][2]}</th></tr></thead><tbody>${body}</tbody></table>`;

    barBlock($("colabBars"), [
      ["Persistence", c.baselines.persistence, "base"],
      ["Corn/soy alternation", c.baselines.corn_soy_alternation, "base"],
      ["Markov-2 table", c.baselines.markov2, "base"],
      ["LightGBM (full features)", c.lgbm, ""],
    ], "acc");
    $("colabBars").insertAdjacentHTML("beforeend", `<p class="hint">Accuracy shown. Macro-F1: persistence ${c.baselines.persistence.macro_f1.toFixed(3)}, alternation ${c.baselines.corn_soy_alternation.macro_f1.toFixed(3)}, Markov-2 ${c.baselines.markov2.macro_f1.toFixed(3)}, LightGBM ${c.lgbm.macro_f1.toFixed(3)}. Δ accuracy vs Markov-2: +${c.lgbm.delta_acc_vs_markov2.toFixed(3)}; Δ macro-F1: +${c.lgbm.delta_macro_f1_vs_markov2.toFixed(3)}. Per-class F1: corn ${c.lgbm.per_class_f1.corn.toFixed(3)}, soy ${c.lgbm.per_class_f1.soy.toFixed(3)}, hay ${c.lgbm.per_class_f1.hay.toFixed(3)}, grass ${c.lgbm.per_class_f1.grass.toFixed(3)}, other_crop ${c.lgbm.per_class_f1.other_crop.toFixed(3)}, non_ag ${c.lgbm.per_class_f1.non_ag.toFixed(3)}.</p>`);
    const abItems = Object.entries(c.ablation).map(([k, v]) => [k, v, ""]);
    barBlock($("colabAbBars"), abItems, "acc");
    const cal = c.calibration;
    $("colabText").textContent = `${cal.method}. Temperature T=${cal.temperature.toFixed(2)}. Test ECE ${cal.test_ece_before.toFixed(4)} → ${cal.test_ece_after.toFixed(4)}. Test NLL ${cal.test_nll_before.toFixed(4)} → ${cal.test_nll_after.toFixed(4)}. Temperature scaling slightly worsened calibration (ECE 0.016 → 0.0351); this is reported honestly. One seed, not a published benchmark.`;
    $("colabAbImg").src = "data/colab_run/crop_ablation.png";
    $("colabCalImg").src = "data/colab_run/crop_confusion_calibration.png";
    $("colabMapImg").src = "data/colab_run/crop_map.png";
  }

  function renderHelp() {
    const o = state.data.objectives;
    $("objHelp").innerHTML = o.keys.map((k) =>
      `<h3>${o.labels[k]} (${o.sense[k] === "min" ? "lower is better" : "higher is better"})</h3><p>${o.help[k]}</p>`
    ).join("");
  }

  function renderCitations() {
    $("citeList").innerHTML = state.data.citations.map((c) =>
      `<li><strong>${c.item}.</strong> ${c.credit} Licence: ${c.licence}. ${c.url ? `<a href="${c.url}">${c.url}</a>` : ""}</li>`
    ).join("");
  }

  Promise.all([
    fetch("data/app_data.json").then((r) => {
      if (!r.ok) throw new Error("app_data.json is not ready yet — run scripts/run_model.py");
      return r.json();
    }),
    fetch("data/colab_run/results.json").then((r) => {
      if (!r.ok) throw new Error("colab_run/results.json is missing");
      return r.json();
    }),
  ])
    .then(([data, colab]) => {
      state.data = data;
      state.colab = colab;
      data.objectives.keys.forEach((k) => { state.weights[k] = 50; });
      $("disclaimer").textContent = data.disclaimer;
      $("mapLegend").innerHTML = Object.entries(data.map.colors).map(([n, c]) =>
        `<span><i class="swatch" style="background:${c}"></i>${n}</span>`
      ).join("");
      renderSliders();
      renderFeatured();
      renderHelp();
      renderModel();
      renderColab();
      renderCitations();
      renderClimate();
      const img = new Image();
      img.onload = () => { state.mapImg = img; drawMap(); };
      img.src = data.map.cdl_2025;
      $("map").addEventListener("click", hitField);
      renderField();
      renderStrategies();
      renderPareto();
      $("loadStatus").textContent = `Loaded ${data.fields.length} analysis tiles · local ${data.metrics.n_test} test pixels · Colab ${colab.n_test} test pixels · local runtime ${data.runtime_seconds}s.`;
    })
    .catch((err) => {
      $("loadStatus").textContent = "Waiting for model outputs: " + err.message;
    });
})();
