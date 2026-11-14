/* Field Shift briefing, written for a non-technical audience.
   Numbers: data/colab_run/results.json (Colab full-county run), data/metrics.json (local box run),
   data/app_data.json (strategies, NSGA-II, POWER climate, tiles) and data/extras.json (R16 from colab_hpo round 2, box prototype from PLAN.md). */
(async function () {
  const B = window.Briefing;
  const [R, L, A, X] = await Promise.all(["data/colab_run/results.json", "data/metrics.json", "data/app_data.json", "data/extras.json"].map((u) => fetch(u).then((r) => r.json())));
  const f4 = (v) => (+v).toFixed(4), f1 = (v) => (+v).toFixed(1);
  const pc = (v) => Math.round(100 * v) + "%", pc1 = (v) => (100 * v).toFixed(1) + "%";
  const nf = (v) => Number(v).toLocaleString("en-US");
  const bl = R.baselines, lg = R.lgbm, ab = R.ablation, cal = R.calibration, obj = A.objectives;
  const R16 = X.r16_eurosat_croptype, PROTO = X.plan_box_prototype;
  const S = Object.fromEntries(A.strategies.map((s) => [s.id, s]));
  const ci = (id, k) => S[id].county_indicators[k];
  const chg = (a, b) => Math.round((100 * (b - a)) / a);
  const clim = A.climate_yearly, last10 = clim.slice(-10);
  const med = (xs) => { const s = xs.slice().sort((a, b) => a - b); const n = s.length; return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2; };
  const PRED = { persistence: "Same crop as this year", corn_soy_alternation: "Corn ↔ soy alternation", markov2: "Best rule of thumb (last two years)" };

  const strat = (k, lab, lowerBetter) => B.bars(A.strategies.map((s) => ({ label: s.name, value: s.county_indicators[k] })), { fmt: (v) => v.toFixed(3), labelWidth: 260, rowH: 30, axis: `${lab} (relative score; ${lowerBetter ? "lower" : "higher"} is better)` });

  const slides = [
    {
      kicker: "In one minute",
      title: "A farm planning tool that shows the trade-offs of switching crop rotations",
      html: `<div class="bf-onemin">
        <div><h3>The problem</h3><p>Story County, Iowa is almost all corn and soybeans. A farmer considering hay, small grains or a cover crop wants to see what changes for their own field.</p></div>
        <div><h3>What we built</h3><p>Pick a field-sized square on the map, say what matters to you, and compare rotations on water use, soil erosion, nitrogen, heat/frost and dry-soil risk, using NASA and USDA data.</p></div>
        <div><h3>Does the model work?</h3><p>It predicts next year's crop correctly ${pc(lg.acc)} of the time on years it never saw, slightly ahead of the best rule of thumb (${pc(bl.markov2.acc)}) and clearly better on less common crops.</p></div>
        <div><h3>Where it falls short</h3><p>It is weak on hay and never got the rare "other crops" class right, and a step meant to make its confidence more honest made it slightly worse.</p></div></div>`,
      why: "Farmers can explore a switch on screen before risking a season on it, with the uncertainty shown instead of hidden.",
      expert: `<p>LightGBM next-season crop model (6 classes), temporal split train ≤2021 / val ${R.val_years.join("–")} / test ${R.test_years.join("–")}, seed ${R.seed}, ${R.hpo_trials} Optuna trials, ${nf(R.n_test)} test pixels. Planning indicators: FAO-56 Kc, NASADEM slope × bare-soil months, NASA POWER. NSGA-II search. ${B.esc(A.disclaimer)}</p>`,
    },
    {
      kicker: "The problem",
      title: "Most of the county repeats corn then soybeans, year after year",
      body: ["Corn–soy is familiar and profitable, but bare soil after harvest can wash away on slopes, and two crops give pests an easy cycle.", "Alternatives exist, but each one changes water use, erosion and nitrogen differently on each field."],
      visual: B.fig("data/cdl_history.png", "USDA crop maps of Story County for 2016, 2020 and 2025 (our local run)."),
      why: "Advice that ignores the field's slope, soil and recent history is hard for a farmer to trust.",
      expert: `<p>USDA NASS Cropland Data Layer 2009–2025, 30 m. Test-year class shares (Colab): ${Object.entries(R.test_class_share).map(([k, v]) => `${k} ${pc1(v)}`).join(", ")}.</p>`,
    },
    {
      kicker: "The data",
      title: "Seventeen years of crop maps plus NASA terrain, climate and vegetation data",
      body: ["USDA crop maps tell us what grew on every 30 m patch since 2009. NASA adds the shape of the land (NASADEM), the weather (NASA POWER) and how green the fields got each season (MODIS). Soil maps (SoilGrids) add clay, sand and organic matter.", `We split the county into ${A.fields.length} squares about 1.2 km across, so each one is roughly a farm.`],
      visual: `<div class="bf-grid">${B.fig("data/slope_tiles.png", "NASADEM slope and the 1.2 km analysis squares.")}${B.fig("data/cdl_2025_map.png", "2025 crop map used in the app.")}</div>`,
      why: "All of these datasets are free and national, so the same tool can work for other counties.",
      expert: `<ul>${A.citations.map((c) => `<li>${B.esc(c.item)}. ${B.esc(c.credit)} (${B.esc(c.licence)})</li>`).join("")}</ul><p>SMAP, ECOSTRESS, GPM IMERG and GRACE are named in the challenge but need an Earthdata login; not in this build.</p>`,
    },
    {
      kicker: "How it works",
      title: "Learn from each field's history, then score possible rotations",
      visual: B.flow([
        ["1 · History", `What grew on each patch over the last ${R.n_lags} years`],
        ["2 · Context", "Slope, soil, last season's weather and greenness"],
        ["3 · Prediction", "What is likely next year, and how sure we are"],
        ["4 · Scores", "Water, erosion, nitrogen, heat/frost and dry-soil risk for each 4-year plan"],
        ["5 · Search", "Find plans that aren't beaten on every score by another plan"],
        ["6 · Your weights", "Sliders re-rank the plans for your priorities"],
      ]),
      body: ["The prediction shows what the field's history makes likely. The scores show what would change if you chose differently."],
      why: "Farmers stay in charge: the tool lays out the options and doesn't tell anyone what to plant.",
      expert: `<p>Features: ${R.n_lags} crop lags, crop counts, NASADEM terrain, SoilGrids 0–5 cm, previous-season POWER climate, MODIS MOD13Q1 NDVI peak. Colab best params ${B.esc(JSON.stringify(R.best_params))}. NSGA-II: ${B.esc(A.pareto.note)}</p>`,
    },
    {
      kicker: "The bar to beat",
      title: "Simple rules already guess next year's crop most of the time",
      body: [`Because farms alternate, "corn after soy, soy after corn" is right ${pc(bl.corn_soy_alternation.acc)} of the time. The best rule of thumb, which looks at the last two years, is right ${pc(bl.markov2.acc)} of the time. "Same as this year" is right only ${pc(bl.persistence.acc)}.`],
      visual: B.bars(Object.entries(PRED).map(([k, l]) => ({ label: l, value: bl[k].acc })), { min: 0, max: 1, fmt: pc, labelWidth: 300, axis: "Share of fields where next year's crop was guessed right (test years 2024–25)" }),
      why: "A model only adds value if it beats rules farmers and agronomists already use in their heads.",
      expert: `<table class="bf-table"><thead><tr><th>Baseline</th><th>Accuracy</th><th>Macro-F1</th></tr></thead><tbody>${Object.entries(PRED).map(([k, l]) => `<tr><td>${k}</td><td class="n">${f4(bl[k].acc)}</td><td class="n">${f4(bl[k].macro_f1)}</td></tr>`).join("")}</tbody></table><p>Markov-2 = most common next crop given the previous two years.</p>`,
    },
    {
      kicker: "Result",
      title: `Our model guesses next year's crop right ${pc(lg.acc)} of the time, a bit better than the best rule`,
      body: [`On ${nf(R.n_test)} sample patches from 2024–2025, which it never saw in training, the model was right ${pc1(lg.acc)} of the time vs ${pc1(bl.markov2.acc)} for the best rule. The bigger gain is on less common crops: its score that weighs every crop equally is ${pc(lg.macro_f1)} vs ${pc(bl.markov2.macro_f1)}.`],
      visual: `<div class="bf-grid"><div><h3>Right overall</h3>${B.bars([{ label: "Best rule of thumb", value: bl.markov2.acc }, { label: "Our model", value: lg.acc, hl: true }], { min: 0.7, max: 0.85, fmt: pc1, labelWidth: 170, rowH: 34, axis: "axis starts at 70%" })}</div><div><h3>Fair to every crop</h3>${B.bars([{ label: "Best rule of thumb", value: bl.markov2.macro_f1 }, { label: "Our model", value: lg.macro_f1, hl: true }], { min: 0.4, max: 0.55, fmt: pc1, labelWidth: 170, rowH: 34, axis: "axis starts at 40%" })}</div></div>`,
      why: "The farmers most likely to use this are the ones trying something other than corn–soy, so doing better on less common crops matters more than the headline.",
      expert: `<p>Colab full-county run (seed ${R.seed}, ${nf(R.n_pixels_sampled)} sampled pixels: ${nf(R.n_train)} / ${nf(R.n_val)} / ${nf(R.n_test)}, runtime ${f1(R.runtime_seconds)} s): accuracy ${f4(lg.acc)}, macro-F1 ${f4(lg.macro_f1)}; Δ vs Markov-2 +${f4(lg.delta_acc_vs_markov2)} acc, +${f4(lg.delta_macro_f1_vs_markov2)} macro-F1. Top features: ${lg.top_features_gain.map((x) => x[0]).join(", ")}.</p>`,
    },
    {
      kicker: "A second, independent run",
      title: "A smaller run on our own computer tells the same story",
      body: [`Before the big run, we trained on ${nf(L.n_pixels_sampled)} patches on our own machine (a different random sample and seed). Again the model edged the best rule: ${pc1(L.lgbm.acc)} vs ${pc1(L.baselines.markov2.acc)} right, and ${pc(L.lgbm.macro_f1)} vs ${pc(L.baselines.markov2.macro_f1)} on the equal-weight score.`, `An even earlier tiny prototype (${B.esc(PROTO.note.replace("Box CPU, ", "").replace(", one seed.", ""))}) roughly tied the rule.`],
      visual: `<table class="bf-table"><thead><tr><th>Run</th><th>Best rule right</th><th>Our model right</th><th>Best rule, equal-weight</th><th>Our model, equal-weight</th></tr></thead><tbody>
        <tr class="hl"><td>Colab full county (${nf(R.n_test)} test patches)</td><td class="n">${pc1(bl.markov2.acc)}</td><td class="n">${pc1(lg.acc)}</td><td class="n">${pc1(bl.markov2.macro_f1)}</td><td class="n">${pc1(lg.macro_f1)}</td></tr>
        <tr><td>Our computer (${nf(L.n_test)} test patches)</td><td class="n">${pc1(L.baselines.markov2.acc)}</td><td class="n">${pc1(L.lgbm.acc)}</td><td class="n">${pc1(L.baselines.markov2.macro_f1)}</td><td class="n">${pc1(L.lgbm.macro_f1)}</td></tr>
        <tr><td>Tiny prototype (20k patches, test year 2020)</td><td class="n">${pc1(PROTO.rows[2][1])}</td><td class="n">${pc1(PROTO.rows[3][1])}</td><td class="n">${pc1(PROTO.rows[2][2])}</td><td class="n">${pc1(PROTO.rows[3][2])}</td></tr></tbody></table>`,
      why: "Getting a similar result twice with different samples makes it less likely to be a fluke.",
      expert: `<p>Local box run: ${B.esc(L.caveat)} ${L.hpo_trials} Optuna trials, best params ${B.esc(JSON.stringify(L.best_params))}. Persistence ${f4(L.baselines.persistence.acc)} / ${f4(L.baselines.persistence.macro_f1)}, corn–soy ${f4(L.baselines.corn_soy_alternation.acc)} / ${f4(L.baselines.corn_soy_alternation.macro_f1)}. Prototype rows (acc, macro-F1): ${PROTO.rows.map((r) => `${B.esc(r[0])} ${r[1]} / ${r[2]}`).join("; ")}. Source: <code class="bf">${B.esc(PROTO.source)}</code>.</p>`,
    },
    {
      kicker: "Crop by crop",
      title: "Strong on corn, soybeans and grass; weak on hay; never right on \"other crops\"",
      body: [`For corn the model scores ${pc(lg.per_class_f1.corn)}, soybeans ${pc(lg.per_class_f1.soy)} and grass ${pc(lg.per_class_f1.grass)}. Hay is ${pc(lg.per_class_f1.hay)}, and "other crops" is ${pc(lg.per_class_f1.other_crop)}: it never got that class right. Those two crops cover only ${pc1(R.test_class_share.hay)} and ${pc1(R.test_class_share.other_crop)} of test patches.`],
      visual: B.bars(Object.entries(lg.per_class_f1).map(([k, v]) => ({ label: k.replace("_", " "), value: v, hl: v > 0.7, neg: v < 0.25 })), { min: 0, max: 1, fmt: pc, labelWidth: 140, rowH: 30, axis: "Per-crop score (F1: balance of catching that crop and not falsely predicting it)" }),
      why: "When the model is unsure, as it often is for diversified rotations, the app says so and suggests asking an agronomist.",
      expert: `<p>Per-class F1, Colab: ${Object.entries(lg.per_class_f1).map(([k, v]) => `${k} ${v}`).join(", ")}. Local run: ${Object.entries(L.lgbm.per_class_f1).map(([k, v]) => `${k} ${v}`).join(", ")}.</p>${B.fig("data/colab_run/crop_confusion_calibration.png", "Colab: confusion matrix and reliability diagram, test 2024–2025.")}`,
    },
    {
      kicker: "Whole-county check",
      title: `Across the whole county, the 2025 prediction matched the real crop on ${pc(R.map.pixel_accuracy_full_county)} of farmland`,
      body: [`We predicted 2025 for every one of ${nf(R.map.farmed_pixels)} farmed 30 m patches and compared with the USDA map. ${pc1(R.map.disagreement_frac)} of patches disagree; the map shows where.`],
      visual: B.fig("data/colab_run/crop_map.png", "2025: USDA actual crops, our prediction, and where they disagree."),
      why: "Seeing where the model is wrong tells local experts which fields need a closer look.",
      expert: `<p>Full-county ${R.map.year}: pixel accuracy ${f4(R.map.pixel_accuracy_full_county)}, disagreement ${R.map.disagreement_frac}, ${nf(R.map.farmed_pixels)} farmed pixels.</p>`,
    },
    {
      kicker: "What we tested",
      title: "Land shape and soil help the most; weather and greenness help on rarer crops",
      body: [`Using crop history alone, the model was right ${pc1(ab.history_only.acc)} of the time. Adding slope and soil raised that to ${pc1(ab["+terrain_soil"].acc)}. Adding weather and greenness then lowered overall accuracy slightly (to ${pc1(ab["+ndvi (full)"].acc)}) but kept improving the score that treats every crop equally (from ${pc(ab.history_only.macro_f1)} to ${pc(ab["+ndvi (full)"].macro_f1)}).`, "We kept the full model because the rarer crops matter for this tool."],
      visual: `<div class="bf-grid"><div><h3>Right overall</h3>${B.bars(Object.entries(ab).map(([k, v]) => ({ label: k, value: v.acc, hl: k.includes("full") })), { min: 0.8, max: 0.83, fmt: pc1, labelWidth: 160, rowH: 30, axis: "axis starts at 80%" })}</div><div><h3>Fair to every crop</h3>${B.bars(Object.entries(ab).map(([k, v]) => ({ label: k, value: v.macro_f1, hl: k.includes("full") })), { min: 0.4, max: 0.52, fmt: pc1, labelWidth: 160, rowH: 30, axis: "axis starts at 40%" })}</div></div>`,
      why: "This shows NASA's terrain and climate data do real work, not just decoration.",
      expert: `<table class="bf-table"><thead><tr><th>Arm</th><th>Colab acc</th><th>Colab macro-F1</th><th>Local acc</th><th>Local macro-F1</th></tr></thead><tbody>${Object.keys(ab).map((k) => `<tr><td>${k}</td><td class="n">${f4(ab[k].acc)}</td><td class="n">${f4(ab[k].macro_f1)}</td><td class="n">${f4(L.ablation[k].acc)}</td><td class="n">${f4(L.ablation[k].macro_f1)}</td></tr>`).join("")}</tbody></table><div class="bf-grid">${B.fig("data/colab_run/crop_ablation.png", "Colab ablation figure.")}${B.fig("data/crop_ablation.png", "Local-run ablation figure.")}</div>`,
    },
    {
      kicker: "How sure is it?",
      title: "Its confidence was already honest; our fix made it slightly worse",
      body: [`When the model says it's 90% sure, it should be right about 90% of the time. On the test years its raw confidence was off by about ${pc1(cal.test_ece_before)} on average. A standard correction step (temperature scaling) raised that to ${pc1(cal.test_ece_after)}, and the same happened in the local run (${pc1(L.calibration.test_ece_before)} → ${pc1(L.calibration.test_ece_after)}).`, "So we show the raw confidence."],
      visual: `<div class="bf-grid">${B.fig("data/colab_run/crop_confusion_calibration.png", "Right: confidence vs actual accuracy. Close to the diagonal is good.")}${B.fig("data/crop_confusion_calibration.png", "Same check on the local run.")}</div>`,
      why: "Farmers deciding on a field should see how sure the tool is, and we shouldn't make that number look better than it is.",
      expert: `<table class="bf-table"><thead><tr><th></th><th>Colab before</th><th>Colab after (T = ${cal.temperature})</th><th>Local before</th><th>Local after (T = ${f4(L.calibration.temperature)})</th></tr></thead><tbody><tr><td>ECE (${cal.ece_bins} bins)</td><td class="n">${f4(cal.test_ece_before)}</td><td class="n">${f4(cal.test_ece_after)}</td><td class="n">${f4(L.calibration.test_ece_before)}</td><td class="n">${f4(L.calibration.test_ece_after)}</td></tr><tr><td>NLL</td><td class="n">${f4(cal.test_nll_before)}</td><td class="n">${f4(cal.test_nll_after)}</td><td class="n">${f4(L.calibration.test_nll_before)}</td><td class="n">${f4(L.calibration.test_nll_after)}</td></tr></tbody></table><p>${B.esc(cal.method)}.</p>`,
    },
    {
      kicker: "Rotation options",
      title: `Adding a winter cover crop cuts the erosion score by about ${-chg(ci("current_corn_soy", "erosion_risk"), ci("cover_crop_conservation", "erosion_risk"))}%, but uses more water`,
      body: [`Across the county, the cover-crop rotation scores ${-chg(ci("current_corn_soy", "erosion_risk"), ci("cover_crop_conservation", "erosion_risk"))}% lower erosion risk than plain corn–soy and ${chg(ci("current_corn_soy", "water_demand"), ci("cover_crop_conservation", "water_demand"))}% higher water demand. The small-grain/hay rotation lowers erosion by ${-chg(ci("current_corn_soy", "erosion_risk"), ci("diversified_small_grain_hay", "erosion_risk"))}% and water demand by ${-chg(ci("current_corn_soy", "water_demand"), ci("diversified_small_grain_hay", "water_demand"))}%, with a smaller nitrogen-fixing share.`],
      visual: `<div class="bf-grid"><div><h3>Erosion risk</h3>${strat("erosion_risk", "Erosion risk", true)}</div><div><h3>Water demand</h3>${strat("water_demand", "Water demand", true)}</div></div>`,
      why: `There's no free lunch, and the tool shows it. The computer search also found ${A.pareto.typical_field.length} four-year plans for a typical square that no other plan beats on every score at once (some are unusual, e.g. continuous soy, so they need an agronomist's eye).`,
      expert: `<table class="bf-table"><thead><tr><th>Strategy</th><th>Sequence</th>${obj.keys.map((k) => `<th>${B.esc(obj.labels[k])} (${obj.sense[k]})</th>`).join("")}</tr></thead><tbody>${A.strategies.map((s) => `<tr><td>${B.esc(s.name)}</td><td>${s.sequence.join(" → ")}</td>${obj.keys.map((k) => `<td class="n">${s.county_indicators[k].toFixed(3)}</td>`).join("")}</tr>`).join("")}</tbody></table><p>${obj.keys.map((k) => `<b>${B.esc(obj.labels[k])}:</b> ${B.esc(obj.help[k])}`).join("<br>")}</p><p>Cover-crop years assume winter rye (not a CDL class).</p>`,
    },
    {
      kicker: "Climate context",
      title: `The last ten growing seasons had a median of ${Math.round(med(last10.map((y) => y.gs_precip)))} mm of rain`,
      body: [`NASA POWER weather for the county centre, ${clim[0].year}–${clim[clim.length - 1].year}, is used for the heat, frost and dry-soil scores. We use the median of the last ten years, not a forecast.`],
      visual: B.bars(last10.map((y) => ({ label: String(y.year), value: y.gs_precip })), { fmt: (v) => Math.round(v) + " mm", labelWidth: 70, rowH: 24, axis: "April–September rainfall, NASA POWER" }),
      why: "Planning scores tied to recent local weather are more relevant than national averages.",
      expert: `<p>Last-10-year medians: growing-season precipitation ${f1(med(last10.map((y) => y.gs_precip)))} mm, GDD ${f1(med(last10.map((y) => y.gs_gdd)))}, spring frost days ${med(last10.map((y) => y.frost_days_spring))}, heat days ${med(last10.map((y) => y.heat_days))}. Point: ${A.aoi.center.join(", ")}.</p>`,
    },
    {
      kicker: "Related experiment",
      title: `From satellite photos alone, a small model told crop types apart ${pc(R16.test_accuracy)} of the time`,
      body: [`In a separate test on European satellite photos (EuroSAT), a small model distinguished annual crops, permanent crops and pasture correctly ${pc1(R16.test_accuracy)} of the time, versus ${pc(R16.baseline_accuracy)} for always guessing the most common type.`],
      visual: `<div class="bf-grid">${B.fig("figs/r16_examples.png", "EuroSAT crop-type examples (Colab round 2).")}${B.fig("figs/r16_metrics.png", "Scores by setting.")}</div>`,
      why: "Reading crops straight from imagery could extend this tool to places without a USDA-style crop map.",
      expert: `<p>R16 (Colab T4, seed ${R16.seed}, ${R16.epochs} epochs): ${B.esc(R16.dataset)} (${R16.classes.join(", ")}), ${nf(R16.n_train)} / ${nf(R16.n_select)} / ${nf(R16.n_test)}, chosen ${B.esc(R16.chosen_config)}, test accuracy ${R16.test_accuracy} vs majority ${R16.baseline_accuracy}. Sentinel-2 RGB (ESA), not NASA data. Licence ${B.esc(R16.licence)}. Source: <code class="bf">${B.esc(R16.source)}</code>.</p>`,
    },
    {
      kicker: "What we're running at the event",
      title: "Planned next steps (no results yet)",
      body: ["These are planned. None has been run, so there are no numbers."],
      html: `<ul class="bf-plan">
        <li><b>NASA soil moisture (SMAP)</b> for real dry-soil risk instead of a proxy. Needs a free Earthdata login.</li>
        <li><b>NASA ECOSTRESS evapotranspiration</b> for measured water use.</li>
        <li><b>GPM IMERG rainfall</b> and <b>GRACE groundwater</b> for longer-term water risk.</li>
        <li><b>HLS time-series model</b> of crop growth through the season.</li>
        <li><b>More counties and more seeds</b>, and training that pays more attention to rare crops.</li>
        <li><b>Check scores against field trials</b> and extension-service data, and ask farmers to set default priorities.</li></ul>`,
      why: "Real NASA water and soil data would turn the planning scores from estimates into measurements.",
    },
    {
      kicker: "Limits",
      title: "Planning scores, not forecasts",
      body: ["Results come from one county with one training run per experiment. The water, erosion and nitrogen scores are transparent relative estimates, not field measurements or yield forecasts.", "Prices, leases, labour and equipment aren't modelled. The tool supports a farmer's judgement and doesn't replace it."],
      why: "Use it to start a conversation with an agronomist, not to end one.",
      expert: `<p>${B.esc(A.disclaimer)}</p>`,
    },
    {
      kicker: "Glossary",
      title: "Words used in this briefing",
      html: B.glossary([
        ["Rotation", "The order of crops grown on a field over several years, e.g. corn → soybeans → corn → soybeans."],
        ["Cover crop", "A crop such as winter rye, grown between main crops to protect the soil."],
        ["CDL", "USDA's Cropland Data Layer: a yearly map of what grew on every 30 m patch."],
        ["NASADEM", "NASA's elevation map, used for slope."],
        ["NASA POWER", "NASA's daily weather and solar data for any point."],
        ["MODIS NDVI", "A NASA satellite measure of how green the vegetation is."],
        ["Accuracy", "Share of patches where next year's crop was guessed right."],
        ["Equal-weight score (macro-F1)", "Averages how well each crop is predicted, so rare crops count as much as corn."],
        ["Rule of thumb (Markov-2)", "Predict the crop that most often follows the last two years' crops."],
        ["Confidence error (ECE)", "How far stated confidence is from actual accuracy. Lower is better."],
        ["Search-found plan", "A four-year plan from the trade-off search: no other plan is better on every score at once."],
      ]),
    },
    {
      kicker: "How to use the demo",
      title: "Pick a square, set your priorities, compare plans",
      html: `<div class="bf-grid"><div class="bf-card"><h3>1 · Pick a square</h3><p>Click the map, or a featured square: steepest, flattest, most and least certain, most bare soil, most hay/grass.</p></div>
        <div class="bf-card"><h3>2 · Read the field card</h3><p>Crop history, slope, soil and flags such as "low confidence: ask your agronomist".</p></div>
        <div class="bf-card"><h3>3 · Set priorities</h3><p>Move the sliders for water, erosion, nitrogen, heat/frost and dry soil. Rankings update instantly.</p></div>
        <div class="bf-card"><h3>4 · Compare</h3><p>Strategy cards, the trade-off table and the chart of water vs erosion.</p></div>
        <div class="bf-card"><h3>5 · Check the model</h3><p>The <b>Model honesty</b> tab has every number; <b>Citations</b> lists every dataset.</p></div></div>
        <p class="bf-cap">Code: Apache-2.0. Pre-existing tooling, disclosed. Press Esc to return.</p>`,
    },
  ];
  B.init({ deck: "Field Shift", slides });
})();
