/* Hot Spots experiment briefing, written for a non-technical audience.
   Numbers: data/meta.json (v2 box run, artifacts/metrics.json) and data/extras.json
   (Colab v1 RESULT lines, E2/E10 from colab_gpu + research_plan, box prototype from PLAN.md). */
(async function () {
  const B = window.Briefing;
  const [meta, X, M2] = await Promise.all(["data/meta.json", "data/extras.json", "data/metrics_v2.json"].map((u) => fetch(u).then((r) => r.json())));
  const C = M2.countries, P = meta.protocol, V1 = X.firms_v1_colab;
  const ca = C.Canada, ar = C.Argentina;
  const f4 = (v) => (+v).toFixed(4), f2 = (v) => (+v).toFixed(2), f3 = (v) => (+v).toFixed(3), f1 = (v) => (+v).toFixed(1);
  const nf = (v) => Number(v).toLocaleString("en-US");
  const pc = (v) => Math.round(100 * v) + "%";
  const lower = (base, mine) => Math.round((100 * (base - mine)) / base);
  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const ym = (f) => `${MON[f[1] - 1]} ${f[0]}`;
  const caLow = lower(ca.baselines.eb_cell_ratio.rmse_log1p, ca.tuned_residual_test.rmse_log1p);
  const arLow = lower(ar.baselines.eb_cell_ratio.rmse_log1p, ar.tuned_residual_test.rmse_log1p);
  const D = { Canada: V1.FIRMS_DATA_CANADA, Argentina: V1.FIRMS_DATA_ARGENTINA };
  const AB = { Canada: V1.FIRMS_CANADA_ABLATION, Argentina: V1.FIRMS_ARGENTINA_ABLATION };
  const LG = { Canada: V1.FIRMS_CANADA_LGBM, Argentina: V1.FIRMS_ARGENTINA_LGBM };
  const IV = { Canada: V1.FIRMS_CANADA_INTERVALS, Argentina: V1.FIRMS_ARGENTINA_INTERVALS };
  const METHODS = [["global_ratio", "One conversion factor for everything"], ["month_ratio", "One factor per month"], ["cell_ratio", "One factor per map square"], ["eb_cell_ratio", "Per-square factor, steadied for sparse areas (best simple method)"]];
  const E2 = X.e2_burn_scars, E10 = X.e10_cpu_speed, PROTO = X.plan_box_prototype;

  function metricTable(r) {
    const row = (l, m, cls) => `<tr class="${cls || ""}"><td>${l}</td><td class="n">${f4(m.rmse_log1p)}</td><td class="n">${f3(m.mae)}</td><td class="n">${f3(m.spearman)}</td><td class="n">${f2(m.total_bias_pct)}</td><td class="n">${f2(m.monthly_total_mape_pct)}</td></tr>`;
    return `<table class="bf-table"><thead><tr><th>Method</th><th>RMSE log1p</th><th>MAE</th><th>Spearman</th><th>Total bias %</th><th>Monthly-total MAPE %</th></tr></thead><tbody>` +
      METHODS.map(([k, l]) => row(l, r.baselines[k])).join("") + row("Our model (v2 residual LightGBM, blended on 2021)", r.tuned_residual_test, "hl") +
      row("Our model before the 2021 blend step", r.unmixed_residual_test) + "</tbody></table>";
  }

  function resultSlide(name, low) {
    const r = C[name], m = r.tuned_residual_test, bl = r.baselines;
    const rows = METHODS.map(([k, l]) => ({ label: l.replace(" (best simple method)", ""), value: bl[k].rmse_log1p }));
    rows.push({ label: "Our model", value: m.rmse_log1p, hl: true });
    return {
      kicker: `Result · ${name} · years the model never saw (${P.test_years[0]}–${P.test_years[P.test_years.length - 1]})`,
      title: `${name}: our model's average error is about ${low}% lower than the best simple method`,
      body: [`We hid ${P.test_years[0]}–${P.test_years[P.test_years.length - 1]} from the model, then asked it to predict how many VIIRS fire detections each map square got each month from the MODIS detections alone. Shorter bars are better.`],
      visual: B.bars(rows, { min: Math.min(...rows.map((x) => x.value)) * 0.85, max: Math.max(...rows.map((x) => x.value)) * 1.03, labelWidth: 330, axis: "Average error per map square per month (lower is better; the axis does not start at zero)", aria: `${name} error by method` }),
      why: name === "Canada"
        ? "Fire managers comparing today's season with the early 2000s get numbers on the same scale, square by square, instead of a jump caused by a new satellite."
        : "The same method works on a very different fire regime (farm and grassland burning, not boreal forest), so it isn't tuned to one country.",
      expert: metricTable(r) + `<p>${nf(r.intervals.n_total)} held-out cell-months at ${P.cell_deg}°. Δ RMSE vs EB cell ratio ${f4(r.delta_rmse_log1p_vs_eb_cell_ratio)}. Train ${P.train_years.join("–")}, validate ${P.val_year}. Best params ${B.esc(JSON.stringify(r.best_params))}. ${r.hpo_trials || ""} Optuna trials. One seed, not a published benchmark.</p>`,
    };
  }

  const ablRows = (c) => [["full", "Everything (first model)"], ["no_cell_history", "Without each square's own past"], ["no_lag_lead", "Without last/next month"], ["no_frp_bright_pix", "Without fire intensity, brightness, pixel size"], ["count_only", "Only the MODIS count"]]
    .map(([k, l]) => ({ label: l, value: AB[c][k].rmse_log1p, hl: k === "no_cell_history", neg: k === "full" && c === "Canada" }));
  const ablTable = (c) => `<table class="bf-table"><thead><tr><th>${c} arm (Colab v1)</th><th>RMSE log1p</th><th>Bias %</th><th>Monthly-total MAPE %</th><th>Monthly-total Spearman</th></tr></thead><tbody>` +
    Object.entries(AB[c]).filter(([k, v]) => typeof v === "object" && v.rmse_log1p != null).map(([k, v]) => `<tr><td>${k}</td><td class="n">${f4(v.rmse_log1p)}</td><td class="n">${f2(v.total_bias_pct)}</td><td class="n">${f2(v.monthly_total_mape_pct)}</td><td class="n">${f3(v.monthly_total_spearman)}</td></tr>`).join("") + "</tbody></table>";

  const slides = [
    {
      kicker: "In one minute",
      title: "We put 26 years of satellite fire records on one consistent scale",
      html: `<div class="bf-onemin">
        <div><h3>The problem</h3><p>NASA's older fire satellite (MODIS) and newer one (VIIRS) count the same fires very differently. VIIRS spots about ${f1(ca.global_ratio_value)}× more fire pixels in Canada. A 25-year fire history that mixes them is misleading.</p></div>
        <div><h3>What we built</h3><p>A model that translates every old MODIS month into "what VIIRS could have seen", with a range of uncertainty, for any area you draw on a map.</p></div>
        <div><h3>Does it work?</h3><p>On years it never saw, its average error is about ${caLow}% lower than the best simple method in Canada and ${arLow}% lower in Argentina.</p></div>
        <div><h3>Where it falls short</h3><p>Our first version lost to the simple method in Canada. The current one still does worse on whole-country monthly totals, so for those we show the simple method too.</p></div></div>`,
      why: "Firefighters, planners and insurers can ask \"was this month really unusual?\" and trust that the answer isn't just a satellite change.",
      expert: `<p>All results: one seed, not a published benchmark. Model: LightGBM on the log1p residual over an empirical-Bayes cell-ratio offset, Mondrian conformal intervals. Data: NASA FIRMS MODIS C6.1 and VIIRS S-NPP country archives.</p>`,
    },
    {
      kicker: "The problem",
      title: "Two satellites, two very different fire counts",
      body: ["MODIS has flown since 2000 with big 1 km pixels and is near the end of its life. VIIRS has flown since 2012 with 375 m pixels, so it catches smaller and cooler fires that MODIS misses.", "Joining the two records naively creates a fake jump in fire activity in 2012."],
      visual: B.fig("figs/fig_08.png", "Canada, yearly totals: raw MODIS (dotted) vs our translated VIIRS-scale series (red). The gap is the sensor difference, not the fires."),
      why: "Climate and fire-season trend claims depend on a consistent record. Without one, a better camera looks like a worse fire problem.",
      expert: `<p>VIIRS/MODIS global ratio: Canada ${f2(ca.global_ratio_value)}, Argentina ${f2(ar.global_ratio_value)} (training years). Annual series from the Colab v1 run.</p>`,
    },
    {
      kicker: "The data",
      title: `Over ${Math.floor((D.Canada.modis_detections + D.Canada.viirs_detections + D.Argentina.modis_detections + D.Argentina.viirs_detections) / 1e6)} million NASA fire detections across two countries`,
      body: [`Canada: ${nf(D.Canada.modis_detections)} MODIS and ${nf(D.Canada.viirs_detections)} VIIRS detections. Argentina: ${nf(D.Argentina.modis_detections)} MODIS and ${nf(D.Argentina.viirs_detections)} VIIRS detections.`, `We grouped them into map squares about 25 km across (${P.cell_deg}°) and months, from 2000 to 2025. No login was needed: these are NASA FIRMS public archives.`],
      visual: `<div class="bf-grid">${B.fig("figs/fig_10.png", "Canada: where VIIRS sees relatively more fire (red) than MODIS, 2022–2025.")}${B.fig("figs/fig_04.png", "Argentina: same map.")}</div>`,
      why: "Canada (big forest fires) and Argentina (farm and grassland burning) test the method on two very different kinds of fire.",
      expert: `<p>${B.esc(meta.citations.data)} Cell-months with detections: Canada MODIS ${nf(D.Canada.modis_cell_months)}, VIIRS ${nf(D.Canada.viirs_cell_months)}; Argentina MODIS ${nf(D.Argentina.modis_cell_months)}, VIIRS ${nf(D.Argentina.viirs_cell_months)}. Features per cell-month: MODIS count, FRP sum/median, brightness, night and Aqua fractions, pixel size, low-FRP and off-nadir fractions, month, lat/lon, lag/lead months.</p>`,
    },
    {
      kicker: "How it works",
      title: "Start with a simple conversion, then let a model learn the corrections",
      visual: B.flow([
        ["1 · Grid", "Count MODIS and VIIRS fires per map square per month"],
        ["2 · Simple conversion", "Each square gets its own VIIRS-to-MODIS factor, pulled toward the average where data are thin"],
        ["3 · Learned correction", "A model learns when that factor is off, e.g. small, cool or night-time fires"],
        ["4 · Uncertainty range", "Each estimate gets a range meant to hold the true value 9 times out of 10"],
        ["5 · Calendar", "Translate 2000–2011, then flag months that are far outside normal"],
      ]),
      body: ["The model only learns the correction on top of the simple conversion. That keeps it sensible in places with little data."],
      why: "A method that starts from the obvious answer and explains its corrections is easier for agencies to trust and audit.",
      expert: `<p>${B.esc(P.model)} Intervals: ${B.esc(P.intervals)} EB prior strength k = ${ca.eb_prior_strength_k}. Anomaly rule: robust z = 0.6745·(x − median)/MAD per calendar month, |z| &gt; 3.5. Split: train ${P.train_years.join("–")}, validate ${P.val_year}, test ${P.test_years.join(", ")}.</p>`,
    },
    {
      kicker: "The bar to beat",
      title: "Four simple methods most teams would use",
      body: ["Before trusting a model, we compare it with simple, explainable rules. The best of them, a per-square factor that is steadied in sparse areas, is the one we have to beat."],
      visual: `<table class="bf-table"><thead><tr><th>Simple method</th><th>Canada average error</th><th>Argentina average error</th></tr></thead><tbody>${METHODS.map(([k, l]) => `<tr class="${k === "eb_cell_ratio" ? "hl" : ""}"><td>${l}</td><td class="n">${f4(ca.baselines[k].rmse_log1p)}</td><td class="n">${f4(ar.baselines[k].rmse_log1p)}</td></tr>`).join("")}</tbody></table>`,
      why: "If a fancy model can't beat a one-line rule, nobody should use it. We show the rule's numbers next to ours.",
      expert: `<p>Error = RMSE on log1p(VIIRS count) per cell-month. Global ratio: Canada ${f2(ca.global_ratio_value)}×, Argentina ${f2(ar.global_ratio_value)}×. EB = empirical-Bayes (gamma-Poisson) shrinkage of each cell's ratio toward the global ratio.</p>`,
    },
    resultSlide("Canada", caLow),
    resultSlide("Argentina", arLow),
    {
      kicker: "Honest trade-off",
      title: "Better square by square, but worse at whole-country monthly totals",
      body: [`For a single map square, our model is closer. But when you add up a whole country for a month, the simple method is closer: its monthly totals are off by ${f1(ca.baselines.eb_cell_ratio.monthly_total_mape_pct)}% on average in Canada vs ${f1(ca.tuned_residual_test.monthly_total_mape_pct)}% for our model (Argentina ${f1(ar.baselines.eb_cell_ratio.monthly_total_mape_pct)}% vs ${f1(ar.tuned_residual_test.monthly_total_mape_pct)}%).`, `In Argentina a final adjustment step cut a systematic undercount from ${f1(ar.unmixed_residual_test.total_bias_pct)}% to ${f1(ar.tuned_residual_test.total_bias_pct)}%, at a small cost in per-square error.`],
      visual: B.bars([{ label: "Canada · simple method", value: ca.baselines.eb_cell_ratio.monthly_total_mape_pct, hl: true }, { label: "Canada · our model", value: ca.tuned_residual_test.monthly_total_mape_pct, neg: true }, { label: "Argentina · simple method", value: ar.baselines.eb_cell_ratio.monthly_total_mape_pct, hl: true }, { label: "Argentina · our model", value: ar.tuned_residual_test.monthly_total_mape_pct, neg: true }], { fmt: (v) => v.toFixed(1) + "%", labelWidth: 230, axis: "Average error of whole-country monthly totals (lower is better)" }),
      why: "If you need a national monthly number for a report, use the simple method. If you need local detail, use the model. The app shows both.",
      expert: `<p>Monthly-total MAPE: Canada EB ${f2(ca.baselines.eb_cell_ratio.monthly_total_mape_pct)} vs v2 ${f2(ca.tuned_residual_test.monthly_total_mape_pct)}; Argentina EB ${f2(ar.baselines.eb_cell_ratio.monthly_total_mape_pct)} vs v2 ${f2(ar.tuned_residual_test.monthly_total_mape_pct)}. Argentina blend on 2021: unmixed RMSE ${f4(ar.unmixed_residual_test.rmse_log1p)}, bias ${f2(ar.unmixed_residual_test.total_bias_pct)}% → blended RMSE ${f4(ar.tuned_residual_test.rmse_log1p)}, bias ${f2(ar.tuned_residual_test.total_bias_pct)}% (scale 1.3025, from artifacts/refine.log). Total bias v2: Canada ${f2(ca.tuned_residual_test.total_bias_pct)}%.</p>`,
    },
    {
      kicker: "Our first attempt",
      title: "Version 1 lost to the simple method in Canada, and that taught us why",
      body: [`Our first model (run on Google Colab) had an average error of ${f4(LG.Canada.tuned_test.rmse_log1p)} in Canada, worse than the simple method's ${f4(V1.FIRMS_CANADA_BASELINES.eb_cell_ratio.rmse_log1p)}, and undercounted fires by ${Math.abs(Math.round(LG.Canada.tuned_test.total_bias_pct))}%. In Argentina it did win (${f4(LG.Argentina.tuned_test.rmse_log1p)} vs ${f4(V1.FIRMS_ARGENTINA_BASELINES.eb_cell_ratio.rmse_log1p)}).`, "The cause: it was memorizing each square's past fire totals instead of learning how the satellites differ. Version 2 removes that memory and only learns corrections."],
      visual: B.bars([{ label: "Simple method", value: V1.FIRMS_CANADA_BASELINES.eb_cell_ratio.rmse_log1p }, { label: "Version 1 (Colab)", value: LG.Canada.tuned_test.rmse_log1p, neg: true }, { label: "Version 1 without the memory", value: AB.Canada.no_cell_history.rmse_log1p }, { label: "Version 2 (this app)", value: ca.tuned_residual_test.rmse_log1p, hl: true }], { min: 0.25, max: 0.33, labelWidth: 260, axis: "Canada average error (lower is better; axis starts at 0.25)" }),
      why: "Showing the failure and the fix is how people on the ground can tell this isn't a cherry-picked result.",
      expert: `<p>Colab v1 tuned LightGBM (${LG.Canada.best_params.objective}, ${LG.Canada.hpo_trials} Optuna trials): Canada RMSE ${f4(LG.Canada.tuned_test.rmse_log1p)}, Spearman ${f3(LG.Canada.tuned_test.spearman)}, bias ${f2(LG.Canada.tuned_test.total_bias_pct)}%, Δ vs EB +${f4(LG.Canada.delta_rmse_log1p_vs_eb_cell_ratio)}. Argentina (${LG.Argentina.best_params.objective}): RMSE ${f4(LG.Argentina.tuned_test.rmse_log1p)}, Δ ${f4(LG.Argentina.delta_rmse_log1p_vs_eb_cell_ratio)}. Untuned defaults: Canada RMSE ${f4(LG.Canada.default_params_test.rmse_log1p)} (diverged), Argentina ${f4(LG.Argentina.default_params_test.rmse_log1p)}. v1 top features included raw <code class="bf">cell_v</code>, <code class="bf">cell_ratio</code>, <code class="bf">cell_active</code>.</p>${B.fig("figs/fig_07.png", "Canada v1: baselines vs LightGBM and every ablation arm.")}`,
    },
    {
      kicker: "What we tested (version 1)",
      title: "Removing the memory helped in both countries; removing timing or fire-intensity clues hurt",
      body: ["We switched off one group of clues at a time to see which ones matter. Shorter bars are better."],
      visual: `<div class="bf-grid"><div><h3>Canada</h3>${B.bars(ablRows("Canada"), { min: 0.25, max: 0.36, labelWidth: 290, rowH: 30, axis: "average error (axis starts at 0.25)" })}</div><div><h3>Argentina</h3>${B.bars(ablRows("Argentina"), { min: 0.45, max: 0.57, labelWidth: 290, rowH: 30, axis: "average error (axis starts at 0.45)" })}</div></div>`,
      html: `<p>We also tried smaller (≈10 km) and bigger (≈50 km) map squares. Bigger squares gave better country-wide monthly totals in both countries (Canada ${f1(AB.Canada["cell_0.5deg"].monthly_total_mape_pct)}% vs ${f1(AB.Canada["cell_0.1deg"].monthly_total_mape_pct)}% error for the smallest; Argentina ${f1(AB.Argentina["cell_0.5deg"].monthly_total_mape_pct)}% vs ${f1(AB.Argentina["cell_0.1deg"].monthly_total_mape_pct)}%).</p>`,
      why: "Knowing which clues matter tells agencies what data they must keep collecting: month-to-month timing and fire intensity.",
      expert: ablTable("Canada") + ablTable("Argentina") + `<p>${B.esc(AB.Canada.note)}</p>`,
    },
    {
      kicker: "Uncertainty",
      title: "Our ranges now contain the true value about 9 times in 10 where fires burned",
      body: [`Every estimate comes with a low–high range. We aimed for the true value to fall inside 90% of the time. Where fires actually happened, version 1 managed only ${pc(IV.Canada.cqr_coverage_on_viirs_active_cells)} in Canada and ${pc(IV.Argentina.cqr_coverage_on_viirs_active_cells)} in Argentina. Version 2 reaches ${pc(ca.intervals.cqr_coverage_on_viirs_active_cells)} and ${pc(ar.intervals.cqr_coverage_on_viirs_active_cells)}.`],
      visual: B.bars([{ label: "Canada · version 1", value: IV.Canada.cqr_coverage_on_viirs_active_cells, neg: true }, { label: "Canada · version 2", value: ca.intervals.cqr_coverage_on_viirs_active_cells, hl: true }, { label: "Argentina · version 1", value: IV.Argentina.cqr_coverage_on_viirs_active_cells }, { label: "Argentina · version 2", value: ar.intervals.cqr_coverage_on_viirs_active_cells, hl: true }, { label: "Target", value: 0.9, color: "#f0b43c" }], { min: 0, max: 1, fmt: (v) => Math.round(v * 100) + "%", labelWidth: 200, axis: "How often the range contains the true count, in squares that burned" }),
      why: "Emergency managers need to know how sure a number is. Canada is still a little under the 90% target, and we say so.",
      expert: `<table class="bf-table"><thead><tr><th></th><th>Canada v1</th><th>Canada v2</th><th>Argentina v1</th><th>Argentina v2</th></tr></thead><tbody>
        <tr><td>Coverage, all cell-months</td><td class="n">${f3(IV.Canada.cqr_coverage)}</td><td class="n">${f3(ca.intervals.cqr_coverage)}</td><td class="n">${f3(IV.Argentina.cqr_coverage)}</td><td class="n">${f3(ar.intervals.cqr_coverage)}</td></tr>
        <tr><td>Coverage, VIIRS-active</td><td class="n">${f3(IV.Canada.cqr_coverage_on_viirs_active_cells)}</td><td class="n">${f3(ca.intervals.cqr_coverage_on_viirs_active_cells)}</td><td class="n">${f3(IV.Argentina.cqr_coverage_on_viirs_active_cells)}</td><td class="n">${f3(ar.intervals.cqr_coverage_on_viirs_active_cells)}</td></tr>
        <tr><td>Mean width (all)</td><td class="n">${f2(IV.Canada.mean_width_cqr)}</td><td class="n">${f2(ca.intervals.mean_width_cqr)}</td><td class="n">${f2(IV.Argentina.mean_width_cqr)}</td><td class="n">${f2(ar.intervals.mean_width_cqr)}</td></tr>
        <tr><td>Mean width (active)</td><td class="n">—</td><td class="n">${f2(ca.intervals.mean_width_cqr_active)}</td><td class="n">—</td><td class="n">${f2(ar.intervals.mean_width_cqr_active)}</td></tr></tbody></table>
        <p>v1: quantile GBM + global CQR (margin ${IV.Canada.cqr_margin}). v2: ${B.esc(ca.intervals.cqr_note)} The wider v2 ranges are the price of honest coverage.</p>`,
    },
    {
      kicker: "The product",
      title: `The calendar flags ${ca.calendar.n_flagged_months} unusual months in Canada; 2023 stands out by far`,
      body: [`Each row is a year and each column a month. Brighter means more fire. Stars mark months far outside normal for that time of year. In Canada the top three are ${ym(ca.calendar.flagged[0])}, ${ym(ca.calendar.flagged[1])} and ${ym(ca.calendar.flagged[2])}. In Argentina (${ar.calendar.n_flagged_months} flagged) they are ${ym(ar.calendar.flagged[0])}, ${ym(ar.calendar.flagged[1])} and ${ym(ar.calendar.flagged[2])}.`],
      visual: `<div class="bf-grid">${B.fig("figs/fig_09.png", "Canada calendar. Above the white line: 2000–2011 translated from MODIS.")}${B.fig("figs/fig_03.png", "Argentina calendar, same rule.")}</div>`,
      why: "A fire agency can show, on one page, whether this season is unusual compared with 26 years, not just compared with the VIIRS years.",
      expert: `<p>v2 flagged (year, month, robust z) Canada: ${ca.calendar.flagged.slice(0, 8).map((f) => `${f[0]}-${f[1]} (${f1(f[2])})`).join(", ")}. Argentina: ${ar.calendar.flagged.slice(0, 8).map((f) => `${f[0]}-${f[1]} (${f1(f[2])})`).join(", ")}. Colab v1 flagged ${V1.FIRMS_CANADA_CALENDAR.n_flagged_months} (Canada) and ${V1.FIRMS_ARGENTINA_CALENDAR.n_flagged_months} (Argentina) with the same rule. Months before 2012 are back-casts and carry model error. Figures from the Colab v1 run.</p>`,
    },
    {
      kicker: "Checking the fit",
      title: "Predicted and real monthly fire counts move together",
      body: ["Each left panel compares predicted and real counts for every square and month. Each right panel tracks whole-country monthly totals over the hidden years."],
      visual: `<div class="bf-grid">${B.fig("figs/fig_12.png", "Canada: predicted vs real, 2022–2025.")}${B.fig("figs/fig_06.png", "Argentina: predicted vs real, 2022–2025.")}</div>`,
      why: "You can see by eye where the model follows the real season and where it misses peaks.",
      expert: `<div class="bf-grid">${B.fig("figs/fig_11.png", "Canada v1 Optuna TPE history.")}${B.fig("figs/fig_05.png", "Argentina v1 Optuna TPE history (30 trials).")}</div><div class="bf-grid">${B.fig("figs/fig_02.png", "Argentina annual totals.")}${B.fig("figs/fig_01.png", "Argentina v1 ablation figure.")}</div><p>v1 Spearman (cell-month): Canada ${f3(LG.Canada.tuned_test.spearman)}, Argentina ${f3(LG.Argentina.tuned_test.spearman)}; v2: ${f3(ca.tuned_residual_test.spearman)}, ${f3(ar.tuned_residual_test.spearman)}.</p>`,
    },
    {
      kicker: "What the model pays attention to",
      title: "After the simple conversion, fire intensity and night-time fires matter most in Canada",
      body: ["The longest bar is the simple conversion itself. In Canada the next clues are how intense the fires are and how many are seen at night (small, cool fires VIIRS catches and MODIS misses). In Argentina the MODIS count and the neighbouring months matter most."],
      visual: `<div class="bf-grid"><div><h3>Canada</h3>${B.bars(ca.top_features_gain.slice(0, 6).map(([k, v]) => ({ label: k, value: v })), { fmt: (v) => Math.round(v).toLocaleString("en-US"), labelWidth: 150, rowH: 28 })}</div><div><h3>Argentina</h3>${B.bars(ar.top_features_gain.slice(0, 6).map(([k, v]) => ({ label: k, value: v })), { fmt: (v) => Math.round(v).toLocaleString("en-US"), labelWidth: 150, rowH: 28 })}</div></div>`,
      why: "The model's priorities match the physics of the two satellites, which is a sanity check people can follow.",
      expert: `<p>LightGBM split gain, v2. <code class="bf">log1p_eb</code> = EB offset; <code class="bf">m_frp_med</code> = median fire radiative power; <code class="bf">m_night</code> = share of night overpasses; lag1/lead1 = previous/next month MODIS count. Full lists: Canada ${ca.top_features_gain.map((x) => x[0]).join(", ")}.</p>`,
    },
    {
      kicker: "Related fire experiment",
      title: "Mapping burn scars from NASA's HLS imagery: a small early test",
      body: [`Separately, we trained a small model to outline burned land in NASA Harmonized Landsat–Sentinel (HLS) images. On ${E2.n_val_scenes} test scenes, its outline overlapped the true burn scar by ${pc(E2.model_burn_iou)}; a do-nothing baseline that calls everything unburned scores 0%.`, `A copy of a similar small model ran in ${E10.onnx_fp32_ms} milliseconds per image on an ordinary computer processor, about ${Math.round(E10.pytorch_ms / E10.onnx_fp32_ms)}× faster than the standard setup.`],
      why: "Hotspots say where fire was seen; burn scars say what actually burned. Together they could check each other. This was a tiny test, so treat it as a promising start, not a result.",
      expert: `<p>E2 (Colab T4, Nov 10): ${B.esc(E2.model)}, ${E2.n_train_scenes} train / ${E2.n_val_scenes} val scenes, ${E2.steps} steps. mIoU ${E2.model_miou} vs ${E2.baseline} ${E2.baseline_miou}; burn IoU ${E2.model_burn_iou} vs ${E2.baseline_burn_iou}. Source: <code class="bf">${B.esc(E2.source)}</code>.</p><p>E10 (box CPU): ${B.esc(E10.what)}. ONNX FP32 ${E10.onnx_fp32_ms} ms (mIoU ${E10.miou_fp32}), PyTorch ${E10.pytorch_ms} ms, ONNX INT8 ${E10.onnx_int8_ms} ms (mIoU ${E10.miou_int8}). Source: <code class="bf">${B.esc(E10.source)}</code>.</p>`,
    },
    {
      kicker: "Earliest prototype",
      title: "Our first box test was too small to tell anything, so we scaled up",
      body: ["Before the full run, we tried the idea on a tiny slice of Canada (2012–2015, one test year) on our own computer. The model roughly tied the per-month rule, which told us we needed all the years and a calibration step."],
      visual: `<table class="bf-table"><thead><tr><th>Method (tiny prototype)</th><th>Average error</th><th>Ranking agreement</th><th>Bias %</th></tr></thead><tbody>${PROTO.rows.map((r) => `<tr><td>${B.esc(r[0])}</td><td class="n">${r[1].toFixed(3)}</td><td class="n">${r[2].toFixed(3)}</td><td class="n">${r[3] > 0 ? "+" : ""}${r[3]}</td></tr>`).join("")}</tbody></table>`,
      why: "Small tests are cheap and catch bad ideas early, but their numbers aren't evidence. We only report them here for completeness.",
      expert: `<p>${B.esc(PROTO.note)} RMSE log1p, Spearman, total bias. Source: <code class="bf">${B.esc(PROTO.source)}</code>.</p>`,
    },
    {
      kicker: "What we're running at the event",
      title: "Planned next steps (no results yet)",
      body: ["These are planned or queued. None has been run yet, so there are no numbers."],
      html: `<ul class="bf-plan">
        <li><b>NASA–IBM Prithvi foundation model on burn scars.</b> Queued as Colab notebook 05 (Prithvi-EO-2.0-300M, frozen, on HLS Burn Scars). Waiting on a free GPU.</li>
        <li><b>More satellites.</b> Add NOAA-20 and NOAA-21 VIIRS and the FIRMS area API, so any area worldwide works. Needs a free FIRMS key.</li>
        <li><b>Cross-check with burned area.</b> Compare with NASA MCD64A1 burned-area maps. Needs a free Earthdata login.</li>
        <li><b>Fire weather.</b> Add NASA POWER dryness and wind as clues.</li>
        <li><b>Count fires, not pixels.</b> Group detections into fire events.</li>
        <li><b>Steadier estimates for sparse regions.</b> A hierarchical Bayesian count model.</li>
        <li><b>More seeds and countries</b> so results come with error bars.</li></ul>`,
      why: "The event is where we turn a working prototype into a tool any agency can point at its own region.",
    },
    {
      kicker: "Limits",
      title: "What this does not prove yet",
      body: ["Every result here comes from a single training run on two countries and one VIIRS satellite. It is a strong prototype, not a published benchmark.", "Years before 2012 are translated, not observed. They assume the 2012–2025 relationship between the satellites held earlier too."],
      why: "Use the calendar for context and planning, and check flagged months against local records before acting on them.",
      expert: `<p>Total bias on held-out years: Canada ${f2(ca.tuned_residual_test.total_bias_pct)}%, Argentina ${f2(ar.tuned_residual_test.total_bias_pct)}%. MODIS sensor drift not modelled. AOI bands are summed per-cell intervals (conservative), not formal regional intervals.</p>`,
    },
    {
      kicker: "Glossary",
      title: "Words used in this briefing",
      html: B.glossary([
        ["MODIS", "NASA instrument on the Terra and Aqua satellites (since 2000) with 1 km pixels."],
        ["VIIRS", "Newer instrument (since 2012) with 375 m pixels. It sees smaller fires."],
        ["FIRMS", "NASA's Fire Information for Resource Management System, which publishes the fire detections."],
        ["Detection / hotspot", "One satellite pixel flagged as burning at one moment."],
        ["Map square (cell)", "A ≈25 km grid square (0.25°). We count detections per square per month."],
        ["Simple method (baseline)", "A conversion factor anyone could compute. Our model has to beat it."],
        ["Average error", "How far predictions are from reality on average, on a scale that treats 10→20 like 100→200 (RMSE of log counts)."],
        ["Hidden years (test)", "2022–2025 were kept away from the model until the final check."],
        ["Uncertainty range", "A low–high band meant to contain the true value 9 times out of 10 (conformal prediction)."],
        ["Unusual month", "A month far outside the 26-year normal for that calendar month (robust z-score above 3.5)."],
        ["Back-cast", "Our estimate of what VIIRS could have seen in 2000–2011, before it flew."],
        ["Bias", "Systematic over- or undercounting, as a percentage of the total."],
      ]),
    },
    {
      kicker: "How to use the demo",
      title: "Pick a region, read the calendar, download the table",
      html: `<div class="bf-grid"><div class="bf-card"><h3>1 · Choose an area</h3><p>Use the <b>Region</b> menu or <b>Draw box on map</b> and click two corners.</p></div>
        <div class="bf-card"><h3>2 · Read the map</h3><p>Each dot is a map square. Red: the new satellite sees relatively more fire. Blue: the old one does.</p></div>
        <div class="bf-card"><h3>3 · Read the calendar</h3><p>Rows are years, columns months. Outlined cells are unusual months. Hover for the count and its range.</p></div>
        <div class="bf-card"><h3>4 · Why they disagree</h3><p>The side panel compares small vs large fires, day vs night, and the two MODIS satellites for your area.</p></div>
        <div class="bf-card"><h3>5 · Download</h3><p><b>Download CSV</b> gives the month-by-year table with ranges and flags.</p></div></div>
        <p class="bf-cap">Data: NASA FIRMS. Code: Apache-2.0. Pre-existing tooling, disclosed. Press Esc to return to the demo.</p>`,
    },
  ];
  B.init({ deck: "Hot Spots: one fire record", slides });
})();
