/* Dancing with the SARs local demo. No network calls except same-origin data/. */
(() => {
  const $ = (id) => document.getElementById(id);
  const state = {
    manifest: null,
    mode: "swipe",
    product: "fcc",
    orbitId: null,
    pairId: null,
    split: 50,
    tlIndex: 0,
    playing: false,
    playTimer: null,
    chipId: null,
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

  function orbitById(id) {
    return state.manifest.valencia.orbits.find((o) => o.id === id);
  }
  function pairById(id) {
    return state.manifest.valencia.swipe_pairs.find((p) => p.id === id);
  }
  function dateRec(orbit, dateId) {
    return orbit.dates.find((d) => d.id === dateId);
  }
  function srcFor(rec, product) {
    return rec.files[product] || rec.files.fcc;
  }

  function fillControls() {
    const orbitSel = $("orbit");
    const pairSel = $("pair");
    orbitSel.innerHTML = "";
    state.manifest.valencia.orbits.forEach((o) => {
      const opt = document.createElement("option");
      opt.value = o.id;
      opt.textContent = `${o.label} — ${o.n_dates} dates`;
      orbitSel.appendChild(opt);
    });
    // default to the 06:02 descending pair (closest same-track bracket of DANA)
    const defPair = state.manifest.valencia.swipe_pairs[0];
    state.orbitId = defPair.orbit;
    state.pairId = defPair.id;
    orbitSel.value = state.orbitId;
    refillPairs();
    pairSel.value = state.pairId;
  }

  function refillPairs() {
    const pairSel = $("pair");
    const pairs = state.manifest.valencia.swipe_pairs.filter((p) => p.orbit === $("orbit").value);
    pairSel.innerHTML = "";
    pairs.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.title;
      pairSel.appendChild(opt);
    });
    if (pairs.length) {
      if (!pairs.some((p) => p.id === state.pairId)) state.pairId = pairs[0].id;
      pairSel.value = state.pairId;
    }
    pairSel.disabled = pairs.length === 0;
  }

  function setSwipeSplit(pct) {
    state.split = Math.max(0, Math.min(100, pct));
    $("beforeClip").style.width = state.split + "%";
    $("swipeHandle").style.left = state.split + "%";
    $("swipeHandle").setAttribute("aria-valuenow", String(Math.round(state.split)));
    // keep the before image the same width as the after image
    const after = $("afterImg");
    if (after.complete && after.naturalWidth) {
      const w = after.getBoundingClientRect().width;
      $("beforeImg").style.width = w + "px";
    }
  }

  function bindSwipe() {
    const box = $("swipeBox");
    const handle = $("swipeHandle");
    let dragging = false;
    const move = (clientX) => {
      const r = box.getBoundingClientRect();
      setSwipeSplit(((clientX - r.left) / r.width) * 100);
    };
    handle.addEventListener("pointerdown", (e) => {
      dragging = true;
      handle.setPointerCapture(e.pointerId);
    });
    handle.addEventListener("pointerup", () => { dragging = false; });
    handle.addEventListener("pointercancel", () => { dragging = false; });
    handle.addEventListener("pointermove", (e) => { if (dragging) move(e.clientX); });
    box.addEventListener("pointerdown", (e) => {
      if (e.target.closest(".swipe-handle")) return;
      dragging = true;
      move(e.clientX);
      box.setPointerCapture(e.pointerId);
    });
    box.addEventListener("pointermove", (e) => { if (dragging && e.pressure !== 0) move(e.clientX); });
    box.addEventListener("pointerup", () => { dragging = false; });
    handle.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") setSwipeSplit(state.split - 5);
      if (e.key === "ArrowRight") setSwipeSplit(state.split + 5);
    });
    window.addEventListener("resize", () => setSwipeSplit(state.split));
    $("afterImg").addEventListener("load", () => setSwipeSplit(state.split));
  }

  function renderSwipe() {
    const pair = pairById(state.pairId);
    if (!pair) return;
    const orbit = orbitById(pair.orbit);
    const pre = dateRec(orbit, pair.pre);
    const post = dateRec(orbit, pair.post);
    $("beforeImg").src = srcFor(pre, state.product);
    $("afterImg").src = srcFor(post, state.product);
    $("preCap").textContent = formatDay(pre) + "  (before)";
    $("postCap").textContent = formatDay(post) + "  (after)";
    $("modeHint").textContent = pair.note;
    const ch = orbit.change && orbit.change[pair.id];
    if (ch) {
      $("changeBox").hidden = false;
      $("changeImg").src = ch.color;
    } else {
      $("changeBox").hidden = true;
    }
    $("swipeBox").hidden = false;
    $("swipeCap").hidden = false;
    $("tlBox").hidden = true;
  }

  function formatDay(rec) {
    const d = rec.days_from_dana;
    const rel = d === 0 ? "event day" : d < 0 ? `${-d} day${d === -1 ? "" : "s"} before` : `${d} day${d === 1 ? "" : "s"} after`;
    return `${rec.day}  (${rel})`;
  }

  function renderTimelapse() {
    const orbit = orbitById(state.orbitId);
    const dates = orbit.dates;
    $("tlRange").max = String(dates.length - 1);
    if (state.tlIndex >= dates.length) state.tlIndex = 0;
    $("tlRange").value = String(state.tlIndex);
    $("tlTicks").innerHTML = dates
      .map((d) => {
        const mark = d.days_from_dana >= 0 && d.days_from_dana <= 3 ? ' style="color:var(--amber)"' : "";
        return `<span${mark}>${d.day.slice(5)}</span>`;
      })
      .join("");
    const rec = dates[state.tlIndex];
    $("tlImg").src = srcFor(rec, state.product);
    const side = rec.days_from_dana < 0 ? "before DANA" : rec.days_from_dana === 0 ? "event day" : "after DANA";
    $("tlCap").textContent = `${formatDay(rec)} · ${orbit.label} · ${state.product.toUpperCase()} · ${side}. Shared color stretch across this orbit.`;
    $("swipeBox").hidden = true;
    $("swipeCap").hidden = true;
    $("changeBox").hidden = true;
    $("tlBox").hidden = false;
    $("modeHint").textContent = "Only dates from the selected orbit are shown, so look angle and grid stay fixed. The amber tick marks sit just after 29 October.";
  }

  function stopPlay() {
    state.playing = false;
    if (state.playTimer) clearInterval(state.playTimer);
    state.playTimer = null;
    $("playBtn").textContent = "Play";
  }

  function togglePlay() {
    if (state.playing) { stopPlay(); return; }
    state.playing = true;
    $("playBtn").textContent = "Pause";
    state.playTimer = setInterval(() => {
      const orbit = orbitById(state.orbitId);
      state.tlIndex = (state.tlIndex + 1) % orbit.dates.length;
      renderTimelapse();
    }, 700);
  }

  function renderChips() {
    const grid = $("chipGrid");
    if (grid.dataset.ready) return;
    grid.innerHTML = "";
    state.manifest.sen1floods11.forEach((c, i) => {
      const btn = document.createElement("button");
      btn.className = "chip";
      btn.type = "button";
      btn.dataset.id = c.id;
      btn.innerHTML = `<img src="${c.files.fcc}" alt="${c.id}"><figcaption>${c.country} · water ${(c.water_frac * 100).toFixed(1)}%</figcaption>`;
      btn.addEventListener("click", () => selectChip(c.id));
      grid.appendChild(btn);
      if (i === 0) state.chipId = state.chipId || c.id;
    });
    grid.dataset.ready = "1";
    if (state.chipId) selectChip(state.chipId);
  }

  function selectChip(id) {
    state.chipId = id;
    const c = state.manifest.sen1floods11.find((x) => x.id === id);
    document.querySelectorAll(".chip").forEach((el) => el.classList.toggle("selected", el.dataset.id === id));
    $("sen1Base").src = srcFor(c, state.product);
    $("sen1Title").textContent = c.id.replace(/_/g, " ");
    $("sen1Meta").textContent = `${c.split}. Hand-labelled water covers ${(c.water_frac * 100).toFixed(1)}% of valid pixels (${c.water_pixels.toLocaleString()} px). ${c.crs}.`;
    $("sen1Ov1").src = c.files.label || "";
    $("sen1Ov2").src = c.files.otsu || "";
    $("sen1Ov3").src = c.files.jrc || "";
    syncOverlays();
  }

  function syncOverlays() {
    $("sen1Ov1").style.opacity = $("ovLabel").checked ? "0.72" : "0";
    $("sen1Ov2").style.opacity = $("ovOtsu").checked ? "0.72" : "0";
    $("sen1Ov3").style.opacity = $("ovJrc").checked ? "0.72" : "0";
  }

  function applyMode() {
    const mode = state.mode;
    $("valenciaView").hidden = mode === "sen1";
    $("sen1View").hidden = mode !== "sen1";
    $("orbitWrap").hidden = mode === "sen1";
    $("pairWrap").hidden = mode !== "swipe";
    $("playBtn").hidden = mode !== "timelapse";
    if (mode !== "timelapse") stopPlay();
    if (mode === "swipe") renderSwipe();
    if (mode === "timelapse") renderTimelapse();
    if (mode === "sen1") {
      $("modeHint").textContent = "Official Sen1Floods11 hand-labelled test chips. Cyan is the hand label, amber is the per-chip Otsu baseline, blue is JRC permanent water.";
      renderChips();
    }
  }

  function barRow(label, value, max, kind) {
    const pct = Math.max(0, Math.min(100, (value / max) * 100));
    return `<div class="bar-row"><span>${label}</span><div class="bar ${kind}"><span style="width:${pct}%"></span></div><span class="num">${value.toFixed(4)}</span></div>`;
  }

  function renderMetrics() {
    const m = state.manifest.metrics;
    $("metricCaveat").textContent = m.caveat;
    const iou = m.test_water_iou;
    $("iouBars").innerHTML = [
      barRow("U-Net (final)", iou.unet_final, 1, "win"),
      barRow("Global VV threshold", iou.global_vv_threshold, 1, "base"),
      barRow("Per-chip Otsu", iou.otsu_per_chip, 1, "base"),
      barRow("All-dry", iou.all_dry, 1, "base"),
    ].join("");
    const ab = m.channel_ablation_test_water_iou;
    $("ablateBars").innerHTML = [
      barRow("VV only", ab.vv, 1, "base"),
      barRow("VV + VH", ab.vv_vh, 1, ""),
      barRow("VV + VH + ratio", ab.vv_vh_ratio, 1, "win"),
    ].join("");
    const inf = m.cpu_inference_s_per_512_tile;
    $("inferTable").innerHTML = `
      <thead><tr><th>Runtime</th><th class="num">Seconds / 512 tile</th><th class="num">Water IoU (30-chip subset)</th><th class="num">Size</th></tr></thead>
      <tbody>
        <tr><td>ONNX FP32</td><td class="num">${inf.onnx_fp32.seconds.toFixed(4)}</td><td class="num">${inf.onnx_fp32.water_iou_30chip_subset.toFixed(4)}</td><td class="num">${inf.onnx_fp32.size_mb} MB</td></tr>
        <tr><td>PyTorch FP32</td><td class="num">${inf.torch_fp32.seconds.toFixed(4)}</td><td class="num">—</td><td class="num">—</td></tr>
        <tr><td>ONNX INT8</td><td class="num">${inf.onnx_int8.seconds.toFixed(4)}</td><td class="num">${inf.onnx_int8.water_iou_30chip_subset.toFixed(4)}</td><td class="num">${inf.onnx_int8.size_mb} MB</td></tr>
      </tbody>`;
    $("int8Note").textContent = m.note_int8;
  }

  function renderNisar() {
    const host = $("nisarCatalog");
    if (host.dataset.ready) return;
    host.innerHTML = state.manifest.nisar.map((city) => {
      const figs = city.staged.map((s) => `
        <figure>
          <img src="${s.file}" alt="${s.title}">
          <figcaption>${city.city} · ${s.start.slice(0, 10)} · ${s.collection}<br>${s.title.slice(0, 72)}…</figcaption>
        </figure>`).join("");
      return `<h3 style="text-transform:capitalize">${city.city}</h3>
        <p class="hint">${city.n_browse_staged} public browse previews staged of ${city.n_granules_cmr} CMR granules (${city.date_range[0].slice(0, 10)} to ${city.date_range[1].slice(0, 10)}). Collections: ${city.collections.join(", ")}.</p>
        <div class="nisar-grid">${figs}</div>`;
    }).join("");
    host.dataset.ready = "1";
  }

  function renderCitations() {
    $("citeList").innerHTML = state.manifest.citations.map((c) =>
      `<li><strong>${c.item}.</strong> ${c.credit} Licence: ${c.licence}. ${c.url ? `<a href="${c.url}">${c.url}</a>` : ""}</li>`
    ).join("");
  }

  function wire() {
    $("mode").addEventListener("change", (e) => { state.mode = e.target.value; applyMode(); });
    $("product").addEventListener("change", (e) => {
      state.product = e.target.value;
      applyMode();
    });
    $("orbit").addEventListener("change", (e) => {
      state.orbitId = e.target.value;
      refillPairs();
      state.pairId = $("pair").value;
      state.tlIndex = 0;
      applyMode();
    });
    $("pair").addEventListener("change", (e) => { state.pairId = e.target.value; renderSwipe(); });
    $("tlRange").addEventListener("input", (e) => { state.tlIndex = Number(e.target.value); renderTimelapse(); });
    $("playBtn").addEventListener("click", togglePlay);
    ["ovLabel", "ovOtsu", "ovJrc"].forEach((id) => $(id).addEventListener("change", syncOverlays));
    document.querySelector('button[data-tab="nisar"]').addEventListener("click", renderNisar);
  }

  fetch("data/manifest.json")
    .then((r) => {
      if (!r.ok) throw new Error("manifest.json missing — run scripts/render_tiles.py");
      return r.json();
    })
    .then((m) => {
      state.manifest = m;
      fillControls();
      bindSwipe();
      wire();
      renderMetrics();
      renderCitations();
      applyMode();
      setSwipeSplit(50);
      $("loadStatus").textContent = `Loaded ${m.valencia.orbits.reduce((n, o) => n + o.n_dates, 0)} Sentinel-1 dates · ${m.sen1floods11.length} Sen1Floods11 chips · ${m.nisar.reduce((n, c) => n + c.n_browse_staged, 0)} NISAR browses.`;
    })
    .catch((err) => {
      $("loadStatus").textContent = "Failed to load data/manifest.json: " + err.message;
    });
})();
