/* Dancing with the SARs briefing, written for a non-technical audience.
   Numbers: data/metrics.json (Colab 02 attempt 1, /workspace/colab_queue/runs/02_nasa_sar_flood_hpo/attempt1_numbers.txt),
   data/manifest.json, data/extras.json (E8 + E5 from colab_gpu, R17 from colab_hpo/round2_personal, box prototype from PLAN.md). */
(async function () {
  const B = window.Briefing;
  const [M, man, X] = await Promise.all(["data/metrics.json", "data/manifest.json", "data/extras.json"].map((u) => fetch(u).then((r) => r.json())));
  const t = M.test_water_iou, ab = M.channel_ablation_test_water_iou, cpu = M.cpu_inference_s_per_512_tile;
  const f4 = (v) => (+v).toFixed(4), f2 = (v) => (+v).toFixed(2);
  const pc = (v) => Math.round(100 * v) + "%";
  const orbits = man.valencia.orbits, nDates = orbits.reduce((s, o) => s + o.n_dates, 0), nis = man.nisar, pairs = man.valencia.swipe_pairs;
  const E8 = X.e8_first_attempt, PROTO = X.plan_box_prototype, R17 = X.r17_oscd_change, E5 = X.e5_oscd_lora;
  const xOtsu = (t.unet_final / t.otsu_per_chip).toFixed(1);
  const moreThr = Math.round(100 * (t.unet_final / t.global_vv_threshold - 1));
  const unet = `<svg class="bf-svg" viewBox="0 0 820 270" role="img" aria-label="U-Net diagram: 3 encoder blocks, bottleneck, 3 decoder blocks with skip connections">
    <defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#f0b43c"/></marker></defs>
    <g font-family="system-ui,sans-serif" font-size="12" fill="#d3dcea">
    <rect x="8" y="70" width="96" height="110" rx="8" fill="#16243a" stroke="#3ce0f0"/><text x="56" y="100" text-anchor="middle" fill="#fff" font-weight="600">Input (3 ch)</text>
    <text x="56" y="122" text-anchor="middle">VV dB</text><text x="56" y="140" text-anchor="middle">VH dB</text><text x="56" y="158" text-anchor="middle">VV−VH ratio</text>
    <rect x="130" y="50" width="70" height="150" rx="6" fill="#1e3354" stroke="#4a6286"/><text x="165" y="128" text-anchor="middle" fill="#fff">w</text>
    <rect x="225" y="75" width="70" height="100" rx="6" fill="#1e3354" stroke="#4a6286"/><text x="260" y="128" text-anchor="middle" fill="#fff">2w</text>
    <rect x="320" y="95" width="70" height="60" rx="6" fill="#1e3354" stroke="#4a6286"/><text x="355" y="128" text-anchor="middle" fill="#fff">4w</text>
    <rect x="410" y="108" width="70" height="34" rx="6" fill="#3a2a10" stroke="#f0b43c"/><text x="445" y="129" text-anchor="middle" fill="#fff">8w + dropout</text>
    <rect x="500" y="95" width="70" height="60" rx="6" fill="#173a36" stroke="#5dcc8a"/><text x="535" y="128" text-anchor="middle" fill="#fff">4w</text>
    <rect x="595" y="75" width="70" height="100" rx="6" fill="#173a36" stroke="#5dcc8a"/><text x="630" y="128" text-anchor="middle" fill="#fff">2w</text>
    <rect x="690" y="50" width="70" height="150" rx="6" fill="#173a36" stroke="#5dcc8a"/><text x="725" y="128" text-anchor="middle" fill="#fff">w</text>
    <rect x="776" y="85" width="38" height="80" rx="8" fill="#0e3a40" stroke="#3ce0f0"/><text x="795" y="125" text-anchor="middle" fill="#fff" font-weight="600" transform="rotate(-90 795 125)">water / dry</text>
    <path d="M165 46 C 300 0, 590 0, 722 46" stroke="#3ce0f0" stroke-dasharray="4 4" fill="none" marker-end="url(#ar)"/>
    <path d="M260 71 C 360 35, 530 35, 628 71" stroke="#3ce0f0" stroke-dasharray="4 4" fill="none" marker-end="url(#ar)"/>
    <path d="M355 91 C 410 66, 480 66, 533 91" stroke="#3ce0f0" stroke-dasharray="4 4" fill="none" marker-end="url(#ar)"/>
    <text x="260" y="222" text-anchor="middle" fill="#9aa8bd">encoder: conv blocks, 2× max-pool</text>
    <text x="630" y="222" text-anchor="middle" fill="#9aa8bd">decoder: 2× transposed conv + skip concat</text>
    <text x="410" y="252" text-anchor="middle" fill="#9aa8bd">Loss: class-weighted cross-entropy + w·Dice · OneCycle LR · AMP on GPU · 1×1 conv head, 2 classes</text></g></svg>`;
  const slides = [
    {
      kicker: "In one minute",
      title: `My model maps flooded land about ${Math.round(t.unet_final / t.otsu_per_chip)}× better than the standard automatic method`,
      html: `<div class="bf-onemin">
        <div><h3>The problem</h3><p>Floods come with storms and clouds, so ordinary satellite photos often show nothing. Radar satellites see through cloud, day or night.</p></div>
        <div><h3>What I built</h3><p>An interactive radar viewer for the October 2024 Valencia flood, plus a model that outlines water in radar images.</p></div>
        <div><h3>Does it work?</h3><p>On flood images it had never seen, its water map overlapped the true flood area by ${pc(t.unet_final)}, versus ${pc(t.otsu_per_chip)} for the standard automatic method and ${pc(t.global_vv_threshold)} for a single brightness cut-off.</p></div>
        <div><h3>Where it falls short</h3><p>The model was tested on a global flood dataset, not on Valencia itself. Its saved files were lost when the free cloud computer shut down, so the charts here are rebuilt from the printed results.</p></div></div>`,
      why: "Emergency managers and insurers need a flood map within hours, whatever the weather. Radar plus a tested model can provide it.",
      expert: `<p>U-Net, Sen1Floods11 official hand-labelled test split (90 chips), test water IoU ${f4(t.unet_final)} vs per-chip Otsu ${f4(t.otsu_per_chip)} and global VV threshold ${f4(t.global_vv_threshold)}. Seed ${M.seed}. ${B.esc(M.caveat)}</p>`,
    },
    {
      kicker: "The problem",
      title: "On 29 October 2024 an extreme storm flooded the Valencia region",
      body: ["A slow-moving storm system (a \"DANA\") brought extreme rain and flooding to the Valencia region in Spain. Storms bring cloud, and ordinary camera satellites can't see through it.", "Radar satellites send their own microwave signal and listen for the echo, so they can image the ground through cloud and at night."],
      visual: B.fig("tiles/change/" + pairs[0].id + "/vv_change.png", `Real radar, no model: change in radar brightness, ${B.esc(pairs[0].title)}. Cyan areas got much darker, which is typical of standing water.`),
      why: "In the first hours after a flood, rescue teams and relief agencies need to know where the water is. A map that doesn't wait for clear skies saves time.",
      expert: `<p>VV dB difference (post − pre), same orbit and grid. ${B.esc(pairs[0].note)}</p>`,
    },
    {
      kicker: "The data",
      title: `${nDates} radar passes over Valencia, a global set of hand-drawn flood maps, and NASA's new NISAR`,
      body: [`<b>Sentinel-1 radar</b>: ${nDates} passes over Valencia from ${orbits.length} different satellite tracks, before and after the flood.`, `<b>Sen1Floods11</b>: radar images from floods worldwide where people drew the true water by hand. I use its official test set of 90 images to score the model; ${man.sen1floods11.length} of them can be browsed in the app.`, `<b>NISAR</b> (NASA–ISRO): NASA's catalogue lists ${nis.map((n) => `${n.n_granules_cmr} images over ${n.city[0].toUpperCase() + n.city.slice(1)}`).join(", ")}. These are from 2025–2026, after the flood, and show what I will plug in next.`],
      visual: `<div class="bf-grid">${B.fig("tiles/sen1/Spain_5650136/fcc.png", "A Sen1Floods11 test image from Spain (radar, false colour).")}${B.fig("tiles/sen1/Spain_5650136/label.png", "Its hand-drawn water map.")}${B.fig("tiles/nisar/valencia/" + "NISAR_L2_PR_GCOV_034_066_D_069_2005_DHDH_M_20261028T185318_20261028T185353_P0503.jpg", "A NISAR L-band preview over Valencia, 28 Oct 2026 (not the 2024 flood).")}</div>`,
      why: "Scoring on hand-drawn maps from many countries is what makes the accuracy number believable outside one city.",
      expert: `<p>Sentinel-1 RTC via Planetary Computer / ASF. Orbits: ${orbits.map((o) => `${B.esc(o.label)} (${o.n_dates})`).join("; ")}. Sen1Floods11 (Bonafilia et al. 2020, CC-BY-4.0). NISAR L2 GCOV browse: ${nis.reduce((s, n) => s + n.n_browse_staged, 0)} staged; full .h5 granules need Earthdata login. JRC Global Surface Water as permanent-water prior.</p>`,
    },
    {
      kicker: "Why radar works",
      title: "Calm water reflects radar away like a mirror, so floods look dark",
      body: ["Radar bounces off rough ground and plants back toward the satellite. A flat water surface bounces it away, so flooded fields suddenly turn dark in the image.", "NISAR uses a longer radar wavelength than Sentinel-1. It passes through leaves, so it can reveal water hidden under orchards and wetland vegetation."],
      why: "Valencia's orange groves and the Albufera wetland are exactly where shorter-wavelength radar can miss water. NISAR is built for that.",
      expert: `<p>VV = vertical transmit/receive; VH = cross-pol, sensitive to vegetation volume scattering. Specular reflection lowers VV over smooth water; high dielectric constant of water raises sensitivity to wet soil. C-band ≈5.6 cm (Sentinel-1) vs L-band ≈24 cm (NISAR); L-band double-bounce brightens flooded forest.</p>`,
    },
    {
      kicker: "How it works",
      title: "A model that looks at each radar image and colours in the water",
      body: ["I feed the model three versions of each radar image: two polarisations (VV and VH) and the ratio between them. It shrinks the image to understand the big picture, then rebuilds it at full detail and labels every pixel as water or dry."],
      visual: unet,
      why: "This kind of model (a U-Net) is small enough to run on an ordinary computer during an emergency.",
      expert: `<p>U-Net: 3 encoder blocks (w, 2w, 4w) with max-pool, 8w bottleneck with dropout, 3 decoder blocks with transposed conv + skip concat, 1×1 conv head (2 classes). Loss: class-weighted cross-entropy + w·Dice. OneCycle LR, AMP. Optuna: ${M.hpo.trials} trials (${M.hpo.pruned} pruned) × 10 epochs; searched width {16, 32, 48}, lr 2e-4–3e-3, water weight 1–6, Dice weight 0–1, crop {128, 256}, dropout 0–0.3. Best validation water IoU ${f4(M.hpo.best_valid_water_iou)}. Final 40 epochs; ablation arms 20. The chosen width was not saved.</p>`,
    },
    {
      kicker: "The bar to beat",
      title: "Three simple ways to find water, and how well they do",
      body: ["\"Call everything dry\" finds no water at all. The standard automatic method (Otsu) picks a brightness cut-off separately for each image. A single cut-off learned from training images does better."],
      visual: B.bars([{ label: "Call everything dry", value: t.all_dry }, { label: "Standard automatic cut-off (Otsu)", value: t.otsu_per_chip }, { label: "One cut-off learned from training", value: t.global_vv_threshold }], { min: 0, max: 0.8, fmt: (v) => pc(v), labelWidth: 290, axis: "Overlap between predicted and true flood area (higher is better)" }),
      why: "Many operational flood maps still use simple cut-offs like these. Any model has to clearly beat them to be worth adopting.",
      expert: `<p>Water IoU, official test split: all-dry ${f4(t.all_dry)}, per-chip Otsu on VV ${f4(t.otsu_per_chip)}, global VV threshold (grid-searched on train chips) ${f4(t.global_vv_threshold)}. IoU aggregated over chips; unlabelled pixels ignored.</p>`,
    },
    {
      kicker: "Result",
      title: `My model's flood map overlaps the true flood about ${xOtsu}× more than the standard method`,
      body: [`On 90 flood images it had never seen, the predicted water overlapped the hand-drawn water by ${pc(t.unet_final)}. That's about ${xOtsu}× the standard automatic method (${pc(t.otsu_per_chip)}) and ${moreThr}% more than the best single cut-off (${pc(t.global_vv_threshold)}).`],
      visual: B.bars([{ label: "Call everything dry", value: t.all_dry }, { label: "Standard automatic cut-off", value: t.otsu_per_chip }, { label: "Best single cut-off", value: t.global_vv_threshold }, { label: "My model", value: t.unet_final, hl: true }], { min: 0, max: 0.8, fmt: (v) => pc(v), labelWidth: 230, axis: "Overlap between predicted and true flood area (higher is better)" }),
      why: "Fewer missed flooded streets and fewer false alarms means relief goes to the right neighbourhoods first.",
      expert: `<p>Test water IoU ${f4(t.unet_final)}; Δ vs global threshold +${f4(t.unet_final - t.global_vv_threshold)}, vs Otsu +${f4(t.unet_final - t.otsu_per_chip)}. Best validation IoU during tuning ${f4(M.hpo.best_valid_water_iou)}. Charts rebuilt from printed numbers; original PNGs lost when the Colab runtime ended.</p>`,
    },
    {
      kicker: "What I tested",
      title: "Each extra radar view helps the model find more water",
      body: [`Using only one radar view (VV), the overlap was ${pc(ab.vv)}. Adding the second view (VH) raised it to ${pc(ab.vv_vh)}, and adding the ratio between them to ${pc(ab.vv_vh_ratio)}. Nothing else changed between these three runs.`, `Honest note: this shorter 3-view run (${pc(ab.vv_vh_ratio)}) scored a little above my longer final model (${pc(t.unet_final)}). With a single run each, that gap is within normal run-to-run variation, so I don't claim longer training helps.`],
      visual: B.bars([{ label: "VV only", value: ab.vv }, { label: "VV + VH", value: ab.vv_vh }, { label: "VV + VH + ratio", value: ab.vv_vh_ratio, hl: true }], { min: 0.5, max: 0.7, fmt: (v) => pc(v), labelWidth: 200, axis: "Overlap with true flood area (axis starts at 50%)" }),
      why: "Both polarisations are free from Sentinel-1 and NISAR. Using both is a cheap win for any flood service.",
      expert: `<p>Channel ablation, test water IoU, 20-epoch arms: VV ${f4(ab.vv)}, VV+VH ${f4(ab.vv_vh)}, VV+VH+ratio ${f4(ab.vv_vh_ratio)}. Final tuned model (40 epochs): ${f4(t.unet_final)}.</p>`,
    },
    {
      kicker: "Speed",
      title: "A flood map tile takes under 2 seconds on an ordinary computer",
      body: [`Converted to a standard format (ONNX), the model maps a 512×512-pixel tile in ${f2(cpu.onnx_fp32.seconds)} seconds on a regular processor, faster than the original setup (${f2(cpu.torch_fp32.seconds)} s).`, `A compressed version is a third of the size (${cpu.onnx_int8.size_mb} MB vs ${cpu.onnx_fp32.size_mb} MB) and just as accurate, but it was about ${Math.round(cpu.onnx_int8.seconds / cpu.onnx_fp32.seconds)}× slower on this computer, so I don't use it.`],
      visual: B.bars([{ label: "Standard format (ONNX)", value: cpu.onnx_fp32.seconds, hl: true }, { label: "Original (PyTorch)", value: cpu.torch_fp32.seconds }, { label: "Compressed (INT8)", value: cpu.onnx_int8.seconds, neg: true }], { fmt: (v) => v.toFixed(2) + " s", labelWidth: 220, axis: "Seconds per 512 px tile on a regular processor (lower is better)" }),
      why: "Emergency teams don't always have GPUs or fast internet. A model that runs on a laptop is usable in the field.",
      expert: `<table class="bf-table"><thead><tr><th>Runtime</th><th>s / tile</th><th>Water IoU (30-chip subset)</th><th>Size</th></tr></thead><tbody><tr><td>ONNX FP32</td><td class="n">${cpu.onnx_fp32.seconds}</td><td class="n">${cpu.onnx_fp32.water_iou_30chip_subset}</td><td class="n">${cpu.onnx_fp32.size_mb} MB</td></tr><tr><td>PyTorch FP32</td><td class="n">${cpu.torch_fp32.seconds}</td><td class="n">—</td><td class="n">—</td></tr><tr><td>ONNX dynamic INT8</td><td class="n">${cpu.onnx_int8.seconds}</td><td class="n">${cpu.onnx_int8.water_iou_30chip_subset}</td><td class="n">${cpu.onnx_int8.size_mb} MB</td></tr></tbody></table><p>${B.esc(M.note_int8)}</p>`,
    },
    {
      kicker: "Valencia, before and after",
      title: "Three before-and-after pairs show the flood from different angles",
      body: ["Each image compares the same satellite track before and after 29 October. Cyan means the ground got much darker on radar, typical of standing water. These are real measurements, not model output."],
      visual: `<div class="bf-grid">${pairs.map((p) => B.fig("tiles/change/" + p.id + "/vv_change.png", B.esc(p.title))).join("")}</div>`,
      why: "Looking from several tracks and times helps separate real flooding from one-off noise.",
      expert: `<p>VV dB difference per same-track pair; shared stretch per orbit. Pairs: ${pairs.map((p) => B.esc(p.id)).join(", ")}. Not a model mask; the U-Net numbers come from Sen1Floods11.</p>`,
    },
    {
      kicker: "How I got here",
      title: "My first flood model was much weaker; tuning and more data fixed that",
      body: [`My first try (10 Nov, a tiny model trained briefly on small image crops) only reached ${pc(E8.model_water_iou)} water overlap. An even earlier test on my own computer, on just 12 images for one pass, reached ${pc(PROTO.unet_water_iou)} versus ${pc(PROTO.otsu_water_iou)} for the standard method.`, `The full run, with tuning and 40 training passes, reached ${pc(t.unet_final)} on the official test set.`],
      visual: B.bars([{ label: "Box prototype (12 images, 1 pass)", value: PROTO.unet_water_iou }, { label: "First Colab try (Nov 10)", value: E8.model_water_iou, neg: true }, { label: "Full tuned model", value: t.unet_final, hl: true }], { min: 0, max: 0.8, fmt: (v) => pc(v), labelWidth: 270, axis: "Water overlap. Earlier runs used different, smaller test sets, so compare with care." }),
      why: "I show the weak early numbers so judges can see the improvement came from method, not luck in picking a result.",
      expert: `<p>E8 (Colab T4): ${B.esc(E8.model)}, ${E8.n_train} train / ${E8.n_val} val chips (official hand-labelled), ${E8.steps} steps, crop ${E8.crop}. mIoU ${E8.model_miou} vs ${E8.baseline} ${E8.baseline_miou}; water IoU ${E8.model_water_iou} (all-dry water IoU recorded as ${E8.baseline_water_iou_as_recorded}). Source: <code class="bf">${B.esc(E8.source)}</code>.</p><p>Box prototype: ${B.esc(PROTO.note)} Otsu ${PROTO.otsu_water_iou}, U-Net ${PROTO.unet_water_iou}, CPU ${PROTO.cpu_s_per_512_tile} s per 512 px tile (untrained-scale model). Source: <code class="bf">${B.esc(PROTO.source)}</code>.</p>`,
    },
    {
      kicker: "Related change-detection experiments",
      title: "Spotting new buildings between two satellite photos is much harder",
      body: [`I also tried a related task: finding where cities changed between two Sentinel-2 photos (the OSCD dataset). My best small model balanced catches and false alarms at ${pc(R17.test_f1)}, a little above a simple pixel-difference rule (${pc(R17.difference_test_f1)}).`, `A larger pretrained model fine-tuned on very little data did worse than leaving it untouched (${pc(E5.lora_f1)} vs ${pc(E5.lora_off_linear_f1)}). Both results are weak and I treat them as such.`],
      visual: `<div class="bf-grid">${B.fig("figs/r17_examples.png", "OSCD change detection examples (Colab round 2).")}${B.fig("figs/r17_metrics.png", "OSCD scores by model.")}</div>`,
      why: "Floods change the surface far more strongly than new buildings do, which is why the flood model works and urban change still needs work.",
      expert: `<p>R17 (Colab T4, seed ${R17.seed}, ${R17.epochs} epochs): ${B.esc(R17.dataset)}, train ${R17.cities.train.length} / select ${R17.cities.select.length} / test ${R17.cities.test.length} cities (${R17.cities.test.join(", ")}). Chosen ${B.esc(R17.chosen_config)}: test F1 ${R17.test_f1} vs difference threshold ${R17.difference_test_f1}, no-change ${R17.no_change_f1}. Licence ${B.esc(R17.licence)}. E5: DINOv2-small + LoRA r8, ${E5.train_crops} train / ${E5.val_crops} val crops, ${E5.steps} steps: F1 ${E5.lora_f1} (P ${E5.lora_precision}, R ${E5.lora_recall}) vs LoRA-off ${E5.lora_off_linear_f1}. Sources: <code class="bf">${B.esc(R17.source)}</code>, <code class="bf">${B.esc(E5.source)}</code>.</p>`,
    },
    {
      kicker: "What I'm running at the event",
      title: "Planned next steps (no results yet)",
      body: ["These are planned or queued. None has finished, so there are no numbers."],
      html: `<ul class="bf-plan">
        <li><b>Re-run the flood model on a free GPU</b> to recover its saved weights and figures (Colab notebook 02 is uploaded and waiting for GPU quota).</li>
        <li><b>Finish the two steps that didn't complete</b> in that run: a pretrained-feature comparison (DINOv2, frozen) and the model's own water map for Valencia.</li>
        <li><b>Real NISAR data.</b> Load a full NISAR L-band image and run the model on it. Needs a free Earthdata login.</li>
        <li><b>Compare with NASA OPERA's water product</b> (DSWx) over Valencia. Also needs Earthdata.</li>
        <li><b>Retrain on L-band</b> and compare C- vs L-band under vegetation.</li>
        <li><b>Change detection at proper scale</b> (Colab notebook 04: official OSCD test cities, calibrated confidence and active learning). Queued, not run.</li>
        <li><b>More layers:</b> wetlands, fire scars and crop change.</li></ul>`,
      why: "NISAR is new. Being among the first to run a tested flood model on its data is the core of this challenge.",
    },
    {
      kicker: "Limits",
      title: "What this does not prove yet",
      body: ["All numbers come from one training run. The model was scored on a global flood dataset, not on Valencia, where there's no hand-drawn truth. The Valencia maps are raw radar changes, not model output.", "The NISAR previews are from 2025–2026, after the flood. I use them to show the data format, not as images of the event."],
      why: "Treat the model as a fast first draft of the flood extent that local teams should confirm, not a final map.",
      expert: `<p>Seed ${M.seed}. ONNX weights and figures not saved (free T4 runtime ended after RESULT_FILES). Full NISAR .h5 granules (~1.5–7 GB) not processed.</p>`,
    },
    {
      kicker: "Glossary",
      title: "Words used in this briefing",
      html: B.glossary([
        ["Radar (SAR)", "Synthetic-aperture radar. The satellite sends microwaves and records the echo, so it works through cloud and at night."],
        ["Sentinel-1", "European radar satellites using C-band (≈5.6 cm wavelength)."],
        ["NISAR", "New NASA–ISRO radar satellite with L-band (≈24 cm), which passes through vegetation."],
        ["VV / VH", "Two ways of sending and receiving the radar signal (polarisations). Together they tell water, soil and plants apart."],
        ["Overlap (IoU)", "Area where predicted and true flood agree, divided by the area either one marks as flood. 100% is perfect."],
        ["Otsu", "The standard automatic way to pick a brightness cut-off for each image."],
        ["Sen1Floods11", "A public set of radar flood images from many countries with hand-drawn water."],
        ["U-Net", "A common image model that labels every pixel."],
        ["Test set", "Images kept hidden from the model until the final score."],
        ["F1", "One number balancing how many real changes are caught and how many alarms are false."],
        ["ONNX", "A standard file format that lets the model run fast on ordinary computers."],
      ]),
    },
    {
      kicker: "How to use the demo",
      title: "Swipe, scrub, compare",
      html: `<div class="bf-grid"><div class="bf-card"><h3>Before / after</h3><p>Pick an <b>Orbit</b> and a <b>Pair</b>, then drag the handle across the image. The change map appears below.</p></div>
        <div class="bf-card"><h3>Time-lapse</h3><p>Set <b>Mode</b> to Time-lapse and scrub or press Play through every pass on one track.</p></div>
        <div class="bf-card"><h3>Test images</h3><p>Set Mode to Sen1Floods11 chips. Click an image and toggle the hand-drawn water, the standard method and known permanent water.</p></div>
        <div class="bf-card"><h3>Tabs</h3><p><b>Why radar works here</b>, <b>Metrics</b>, <b>NISAR</b> previews and <b>Citations</b>.</p></div></div>
        <p class="bf-cap">Code: Apache-2.0. Data credits on the Citations tab. Pre-existing tooling, disclosed. Press Esc to return.</p>`,
    },
  ];
  B.init({ deck: "Dancing with the SARs", slides });
})();
