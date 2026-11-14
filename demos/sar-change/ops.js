/* SAR Change flood-ops view: OPERA water layers + municipality zones + the shared C2 decision support (window.OGC2).
   Tasking is SIMULATED: nothing here contacts a real drone, camera, satellite, crew or alert system.
   Every number comes from OG_APP (built from src/modules/sar-change/app.json) or ops/zones.json (NASA OPERA DSWx-S1). */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const APP = window.OG_APP || {}, K = APP.kpi || null, ACTS = APP.actions || [];
  const map = $("opsMap"); if (!map) return;
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const f1 = (v) => (+v).toFixed(1), f2 = (v) => (+v).toFixed(2);
  const W = 1150, H = 1068;
  let zones = [], byName = {}, layer = "swipe", split = 50, sel = null, c2 = null;
  const approved = {};

  if (K) document.querySelectorAll("[data-k]").forEach((el) => { const k = el.dataset.k; if (K[k] != null) el.textContent = (k === "net" ? "+" : "") + f1(K[k]); });

  const SW = { land: "#262c46", perm: "var(--og-water-perm, #1e40af)", new: "var(--og-water-new, #38bdf8)", kept: "#0e7490", gone: "var(--og-water-gone, #f59e0b)" };
  const LEG = {
    swipe: [[SW.new, "New flood water"], [SW.perm, "Usual water: sea, lagoon, rivers"], [SW.land, "Dry land"]],
    delta: [[SW.new, "Newly wet since 26 Oct"], [SW.kept, "Wet on both dates"], [SW.gone, "Dried out"], [SW.perm, "Usual water"]],
    still: [[SW.new, "Still flooded on 19 Nov"], [SW.perm, "Usual water"], [SW.land, "Dry land"]],
  };
  const legendHTML = (l, title) => `<b>${esc(title)}</b>` + LEG[l].map(([c, t]) => `<span><i class="sw" style="background:${c}"></i>${esc(t)}</span>`).join("")
    + `<span class="zl"><i class="sw ln"></i>Town outline</span>`;
  const LAB = {
    swipe: [["Before", "26 Oct 2024 · Sentinel-1A radar", K ? `${f1(K.before)} km² new water` : ""], ["After", "31 Oct 2024 · Sentinel-1A radar", K ? `${f1(K.after)} km² new water` : ""]],
    delta: [["What changed", "26 → 31 Oct 2024 · OPERA difference", K ? `+${f1(K.net)} km² net` : ""], null],
    still: [["3 weeks later", "19 Nov 2024 · Sentinel-1A radar", K ? `${f1(K.still)} km² still wet` : ""], null],
  };
  const labHTML = (x) => { if (!x) return ""; const [d, sn] = x[1].split(" · "); return `<b>${esc(x[0])}</b><span>${esc(d)}${sn ? `<small> · ${esc(sn)}</small>` : ""}</span><em>${esc(x[2])}</em>`; };
  const dl = $("deltaLegend"); if (dl) dl.innerHTML = legendHTML("delta", "Legend");

  function setLayer(l) {
    layer = l; map.dataset.layer = l;
    document.querySelectorAll(".ops-toolbar [data-layer]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.layer === l)));
    $("opsLegend").innerHTML = legendHTML(l, "Legend"); const l2 = $("opsLegend2"); if (l2) l2.innerHTML = legendHTML(l, "Legend");
    $("labL").innerHTML = labHTML(LAB[l][0]); $("labR").innerHTML = labHTML(LAB[l][1]); $("labR").hidden = !LAB[l][1];
    drawLabels();
  }
  function setSplit(p) { split = Math.max(0, Math.min(100, p)); map.style.setProperty("--split", split + "%"); map.classList.toggle("split-l", split < 12); map.classList.toggle("split-r", split > 88); $("opsHandle").setAttribute("aria-valuenow", String(Math.round(split))); }
  document.querySelectorAll(".ops-toolbar [data-layer]").forEach((b) => b.addEventListener("click", () => { setLayer(b.dataset.layer); if (b.dataset.layer === "delta" && window.OGShell) OGShell.show("change"); }));
  $("opsTowns").addEventListener("change", (e) => map.classList.toggle("no-towns", !e.target.checked));
  let drag = false;
  const mv = (x) => { const r = map.getBoundingClientRect(); setSplit(((x - r.left) / r.width) * 100); };
  map.addEventListener("pointerdown", (e) => {
    if (layer !== "swipe" || e.target.closest(".ops-asset, .ops-sel, .ops-legend, button, a")) return;
    drag = true; mv(e.clientX); try { map.setPointerCapture(e.pointerId); } catch (_) {}
  });
  map.addEventListener("pointermove", (e) => { if (drag) mv(e.clientX); });
  ["pointerup", "pointercancel", "lostpointercapture"].forEach((t) => map.addEventListener(t, () => { drag = false; }));
  $("opsHandle").addEventListener("keydown", (e) => { if (e.key === "ArrowLeft") setSplit(split - 5); if (e.key === "ArrowRight") setSplit(split + 5); });

  /* zones */
  const svg = $("opsZones"), labs = document.createElement("div"); labs.className = "ops-labs"; map.insertBefore(labs, $("opsAssets"));
  const kOf = (z) => layer === "delta" ? z.added_km2 : layer === "still" ? z.still_km2 : z.new_after_km2;
  function drawZones() {
    svg.innerHTML = zones.map((z) => `<path class="z" data-n="${esc(z.name)}" d="${z.d}" vector-effect="non-scaling-stroke"><title>${esc(z.name)}: ${f1(z.new_after_km2)} km² new water on 31 Oct</title></path>`).join("");
  }
  function drawLabels() {
    if (!zones.length) return;
    const on = sel ? new Set(sel.zones || []) : null, alt = sel ? new Set(sel.zones_alt || []) : new Set();
    const show = zones.filter((z) => on ? (on.has(z.name) || alt.has(z.name)) : z.new_after_km2 >= 2);
    const placed = [];
    const ord = show.slice().sort((a, b) => kOf(b) - kOf(a));
    labs.innerHTML = ord.map((z) => {
      const a = alt.has(z.name) && !(on && on.has(z.name));
      const v = a ? "radar blind spot" : `${f1(kOf(z))} km²`;
      const c = (a ? z.c : (z.wc || z.c)); let x = (c[0] / W) * 100, y = (c[1] / H) * 100;
      for (let t = 0; t < 6 && placed.some((p) => Math.abs(p[0] - x) < 11 && Math.abs(p[1] - y) < (on ? 5.2 : 3.4)); t++) y += on ? 5.4 : 3.6;
      y = Math.min(95, y); placed.push([x, y]);
      return `<span class="zlab${a ? " alt" : ""}${on ? " sel" : ""}" style="left:${x}%;top:${y}%"><b>${esc(z.name)}</b>${on ? `<i>${esc(v)}</i>` : ""}</span>`;
    }).join("");
  }
  function paint() {
    const on = sel ? new Set(sel.zones || []) : new Set(), alt = sel ? new Set(sel.zones_alt || []) : new Set(), done = sel && approved[sel.id];
    svg.querySelectorAll(".z").forEach((p) => { const n = p.dataset.n; p.classList.toggle("on", on.has(n)); p.classList.toggle("alt", alt.has(n) && !on.has(n)); p.classList.toggle("tasked", !!done && (on.has(n) || alt.has(n))); });
    map.classList.toggle("has-sel", !!sel);
    drawLabels(); drawAssets(); drawSel();
    document.querySelectorAll("#opsPick button").forEach((b) => b.setAttribute("aria-pressed", String(!!sel && b.dataset.id === sel.id)));
  }
  /* tasked assets on the map */
  const taskState = {};
  function drawAssets() {
    const box = $("opsAssets");
    if (!sel) { box.innerHTML = ""; requestAnimationFrame(declutter); return; }
    const main = (sel.zones || []).map((n) => byName[n]).filter(Boolean), alt = (sel.zones_alt || []).map((n) => byName[n]).filter(Boolean);
    box.innerHTML = (sel.tasks || []).map((t, k) => {
      const pool = t.asset === "drone" && alt.length ? alt : main; const z = pool[k % Math.max(1, pool.length)] || main[0];
      if (!z) return ""; const zc = (pool === alt ? z.c : (z.wc || z.c));
      const st = taskState[sel.id + "|" + t.label] || (approved[sel.id] ? "Queued" : "Proposed");
      const dx = [0, 5, -5][k % 3], dy = [-7, 6, 9][k % 3];
      return `<div class="ops-asset" data-s="${esc(st)}" title="${esc(t.label)} · ${esc(st)} (simulated)" style="left:${Math.min(92, Math.max(8, (zc[0] / W) * 100 + dx))}%;top:${Math.min(92, Math.max(8, (zc[1] / H) * 100 + dy))}%">
        ${window.OGC2 ? OGC2.icon(t.asset) : ""}<span>${esc(t.label)}</span><em>${esc(st)}</em></div>`;
    }).join("");
    requestAnimationFrame(declutter);
  }
  function declutter() {
    if (!window.OGShell || !OGShell.declutter) return;
    const q = (sel) => [...map.querySelectorAll(sel)];
    OGShell.declutter(q(".ops-asset"), q(".ops-side-lab, .ops-legend, .ops-handle i"), q(".zlab"));
  }
  window.addEventListener("resize", () => requestAnimationFrame(declutter));
  function drawSel() {
    const box = $("opsSel");
    if (!sel) { box.hidden = true; return; }
    const zs = (sel.zones || []).map((n) => byName[n]).filter(Boolean);
    const sum = zs.reduce((s, z) => s + kOf(z), 0);
    const unit = layer === "delta" ? "km² newly wet" : layer === "still" ? "km² still wet" : "km² new water";
    box.hidden = false;
    box.innerHTML = `<span class="k">${esc(sel.cls)}</span><span><b>${zs.length}</b> towns · <b>${f1(sum)}</b> ${unit}${(sel.zones_alt || []).length ? ` · <b>${sel.zones_alt.length}</b> blind-spot` : ""}</span>
      <button type="button" class="ops-go${approved[sel.id] ? " done" : ""}">${approved[sel.id] ? "Approved · Undo" : esc(sel.verb || "Approve")}</button>`;
    box.querySelector(".ops-go").addEventListener("click", () => c2 && c2.approve(sel.id));
  }

  /* action picker under the map */
  $("opsPick").innerHTML = `<span class="lbl">Show an action on the map</span>` + ACTS.map((a, i) => `<button type="button" data-id="${esc(a.id)}" aria-pressed="false"><i>${i + 1}</i>${esc(a.short || a.cls)}</button>`).join("");
  $("opsPick").addEventListener("click", (e) => { const b = e.target.closest("button[data-id]"); if (b && c2) { c2.select(b.dataset.id); } });

  function select(a) {
    sel = a || null;
    if (sel && sel.layer) { const L = sel.layer === "after" ? "swipe" : sel.layer; if (L !== layer) setLayer(L); if (L === "swipe") setSplit(0); }
    paint();
  }
  function bringMap() {
    const r = map.getBoundingClientRect();
    if (r.top < 0 || r.bottom > window.innerHeight) map.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
  }

  function mountC2() {
    if (!window.OGC2 || !ACTS.length) { $("opsC2").innerHTML = '<p class="ops-note">Decision support failed to load.</p>'; return; }
    c2 = OGC2.mount("#opsC2", {
      app: "sar-change", dock: true, kicker: "Decision support · Valencia flood", title: "Recommended actions", user: "Civil-protection duty officer and partner teams",
      actions: ACTS,
      onSelect(a) { select(a); if (a && window.innerWidth < 1024) bringMap(); },
      onApprove(a, ok) { if (ok) approved[a.id] = true; else { delete approved[a.id]; Object.keys(taskState).forEach((k) => { if (k.startsWith(a.id + "|")) delete taskState[k]; }); } if (sel && sel.id === a.id) paint(); },
      onTask(a, t, status) { taskState[a.id + "|" + t.label] = status; if (sel && sel.id === a.id) drawAssets(); },
      onReset() { Object.keys(approved).forEach((k) => delete approved[k]); Object.keys(taskState).forEach((k) => delete taskState[k]); select(null); },
    });
    if (APP.impact && APP.impact.length) {
      OGC2.impact("#opsImpact", APP.impact, { title: "Impact: who decides what, before → after", note: "Outcomes are qualitative: we haven't measured lives, damage or cost. The numbers are the real inputs: OPERA water areas and our model's test scores (one seed, not a published benchmark)." });
      document.querySelectorAll("#opsImpact .c2-imp").forEach((el, i) => { const it = APP.impact[i]; if (it && it.img) el.insertAdjacentHTML("afterbegin", `<img class="ops-imp-img" src="/assets/img/${esc(it.img)}" alt="" loading="lazy" width="1152" height="864">`); });
    }
    /* the always-visible "Alert everyone (simulated)" button opens the 8-town alert draft */
    const AL = ACTS.find((a) => a.alert && (a.zones || []).length) || ACTS.find((a) => a.alert);
    const ab = $("opsAlertAll");
    if (ab && AL) { $("opsAlertSub").textContent = (AL.zones || []).length ? `${AL.zones.length} towns` : "draft";
      ab.addEventListener("click", () => { if (window.OGShell) OGShell.show("act"); c2.alert(AL.id, { quiet: true, source: "alert" });
        const box = $("opsC2").querySelector(".c2-al"); if (box) { if (window.innerWidth >= 1024 && window.OGShell) OGShell.scrollDock(box); else box.scrollIntoView({ behavior: "auto", block: "start" }); const sb = box.querySelector(".c2-send"); if (sb) sb.focus({ preventScroll: true }); } });
      /* narrow screens: float a copy of the button once the toolbar one has scrolled off screen */
      const ph = document.createElement("span"); ph.className = "ops-alert-ph"; ab.after(ph);
      if ("IntersectionObserver" in window) new IntersectionObserver(([en]) => { const fl = !en.isIntersecting && en.boundingClientRect.top < 0 && window.innerWidth < 1024; if (fl === ab.classList.contains("float")) return;
        if (fl) { const r = ab.getBoundingClientRect(); ph.style.cssText = `display:block;width:${r.width}px;height:${r.height}px;flex:0 0 auto;${window.innerWidth <= 560 ? "flex-basis:100%;" : ""}`; } else ph.style.cssText = "";
        ab.classList.toggle("float", fl); document.body.classList.toggle("alert-float", fl); }).observe(ph);
    } else if (ab) ab.hidden = true;
    const m = /act=([\w-]+)/.exec(location.hash); if (m && ACTS.some((a) => a.id === m[1])) { c2.select(m[1]); setTimeout(() => window.OGShell && OGShell.scrollDock($("opsC2").querySelector(`[data-id="${m[1]}"]`)), 300); }
    // #demo or #demo=<id>: capture state for the video and slides (select, approve: tasks run to Done in ~5 s, open the alert draft)
    const dm = /demo(?:=([\w-]+))?/.exec(location.hash);
    if (dm) { const id = dm[1] && ACTS.some((a) => a.id === dm[1]) ? dm[1] : "sar-change-1"; c2.select(id);
      setTimeout(() => { c2.approve(id); if ((ACTS.find((a) => a.id === id) || {}).alert) c2.alert(id, { quiet: true }); if (window.OGShell) OGShell.scrollDock($("opsC2").querySelector(`[data-id="${id}"]`)); }, 900); }
  }

  function rank() {
    const top = zones.filter((z) => z.added_km2 >= 0.1).sort((a, b) => b.added_km2 - a.added_km2).slice(0, 8), mx = top.length ? top[0].added_km2 : 1;
    $("opsRank").innerHTML = top.map((z) => `<li><span>${esc(z.name)}</span><i style="--w:${(z.added_km2 / mx) * 100}%"></i><b>+${f1(z.added_km2)}</b></li>`).join("");
    const a2 = ACTS.find((a) => (a.zones_alt || []).length);
    if (a2 && K) $("blindNote").innerHTML = `<b>Radar blind spot.</b> In ${esc(a2.zones_alt.slice(0, 3).join(", "))} and ${a2.zones_alt.length - 3} more l'Horta Sud towns, radar maps only ${f2(K.blind_km2)} km² of new water. Water between buildings hides from radar, so those streets need drones and people.`;
  }

  /* leading signal: NASA GPM IMERG daily rain upstream + NASA POWER cloud, with the Sentinel-1 pass dates used above */
  function rain(R) {
    const D = R.days || [], host = $("rainChart"); if (!host || !D.length) return;
    const PASS = { "2024-10-26": "Before pass", "2024-10-31": "After pass", "2024-11-19": "3 weeks later" };
    const w = 900, h = 230, m = { l: 46, r: 46, t: 30, b: 34 }, n = D.length, bw = (w - m.l - m.r) / n;
    const mx = Math.ceil(Math.max(...D.map((d) => d.mean)) / 25) * 25, Y = (v) => h - m.b - (v / mx) * (h - m.t - m.b), YC = (v) => h - m.b - (v / 100) * (h - m.t - m.b);
    const X = (i) => m.l + i * bw;
    let s = "";
    [0, mx / 2, mx].forEach((v) => { s += `<line class="g" x1="${m.l}" x2="${w - m.r}" y1="${Y(v)}" y2="${Y(v)}"/><text class="ax" x="${m.l - 6}" y="${Y(v) + 4}" text-anchor="end">${v}</text>`; });
    s += `<text class="ax" x="${m.l - 6}" y="${m.t - 14}" text-anchor="end">mm</text><text class="ax cl" x="${w - 2}" y="${m.t - 14}" text-anchor="end">cloud %</text>`;
    [0, 50, 100].forEach((v) => { s += `<text class="ax cl" x="${w - m.r + 6}" y="${YC(v) + 4}">${v}</text>`; });
    D.forEach((d, i) => {
      const big = d.mean >= 50;
      s += `<rect class="rb${big ? " hot" : ""}" x="${(X(i) + 1.5).toFixed(1)}" y="${Y(d.mean).toFixed(1)}" width="${(bw - 3).toFixed(1)}" height="${(h - m.b - Y(d.mean)).toFixed(1)}" rx="2"><title>${d.d}: ${d.mean} mm upstream average, ${d.max} mm wettest cell, cloud ${d.cloud == null ? "n/a" : d.cloud + "%"}</title></rect>`;
      if (PASS[d.d]) s += `<line class="pass" x1="${X(i) + bw / 2}" x2="${X(i) + bw / 2}" y1="${m.t}" y2="${h - m.b}"/><text class="pl" x="${X(i) + bw / 2 + (i > n - 6 ? -4 : 4)}" y="${m.t + 10}" text-anchor="${i > n - 6 ? "end" : "start"}">${PASS[d.d]}</text>`;
      const dd = +d.d.slice(8); if (dd === 15 || dd === 1 || dd === 20 || dd === 29) s += `<text class="ax" x="${X(i) + bw / 2}" y="${h - 12}" text-anchor="middle">${dd} ${d.d.slice(5, 7) === "10" ? "Oct" : "Nov"}</text>`;
    });
    const pts = D.map((d, i) => d.cloud == null ? null : `${(X(i) + bw / 2).toFixed(1)},${YC(d.cloud).toFixed(1)}`).filter(Boolean).join(" ");
    s += `<polyline class="cloud" points="${pts}"/>`;
    const pk = D.reduce((a, b) => (b.mean > a.mean ? b : a), D[0]), pi = D.indexOf(pk);
    s += `<text class="ann" x="${X(pi) - 6}" y="${Y(pk.mean) + 34}" text-anchor="end">29 Oct: ${pk.mean} mm (wettest cell ${pk.max} mm)</text>`;
    host.innerHTML = `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet">${s}</svg>
      <div class="ops-rain-leg"><span><i class="sw rb"></i>Daily rain, upstream average (mm)</span><span><i class="sw hot"></i>Day over 50 mm</span><span><i class="ln cl"></i>Cloud cover (%)</span><span><i class="ln ps"></i>Sentinel-1 radar pass</span></div>`;
    const over = D.filter((d) => d.mean >= 50), cl = D.find((d) => d.d === "2024-10-29");
    $("rainNotes").innerHTML = `<li><b>${pk.mean} mm</b><span>average rain upstream on ${+pk.d.slice(8)} Oct, ${pk.max} mm in the wettest 10 km cell. ${over.length === 1 ? "The only day over 50 mm in these five weeks." : ""}</span></li>
      <li><b>${cl && cl.cloud != null ? cl.cloud + "%" : "n/a"}</b><span>cloud cover that day. Optical satellites can't see the ground; radar can.</span></li>
      <li><b>2 days</b><span>from the rain peak (29 Oct) to the first radar map of the water (31 Oct). A rain rule like "over 50 mm upstream" could have raised the flag on day zero; the radar then shows where the water went.</span></li>`;
    $("rainCap").textContent = "Rain: " + R.source.split("; cloud")[0] + ". Cloud: NASA POWER (CERES SYN1deg) daily cloud amount at 39.4° N, 0.65° W. IMERG days are UTC. Reanalysis and satellite rain smooth local extremes; rain gauges in the storm core recorded more.";
  }
  fetch("ops/rain.json").then((r) => r.json()).then(rain).catch((e) => console.warn("rain", e));

  setLayer("swipe"); setSplit(50);
  fetch("ops/zones.json").then((r) => r.json()).then((Z) => {
    zones = Z.zones || []; zones.forEach((z) => { byName[z.name] = z; });
    drawZones(); rank(); mountC2(); paint();
  }).catch((e) => { console.warn("zones", e); mountC2(); });

  /* tabs: let the radar-image swipe resize when its tab opens */
  document.querySelectorAll("nav.tabs button").forEach((b) => b.addEventListener("click", () => setTimeout(() => window.dispatchEvent(new Event("resize")), 30)));
  /* radar-image tab: on-image date / sensor labels mirror the caption */
  const sync = () => {
    const sel1 = $("orbit"), orbit = sel1 && sel1.selectedOptions[0] ? sel1.selectedOptions[0].textContent.split(" (")[0] : "";
    const L = $("s1LabL"), R = $("s1LabR"); if (!L || !R) return;
    L.innerHTML = `<b>Before</b><span>${esc(($("preCap").textContent || "").replace(/\s+\(before\)/, ""))}</span><em>Sentinel-1 · ${esc(orbit)}</em>`;
    R.innerHTML = `<b>After</b><span>${esc(($("postCap").textContent || "").replace(/\s+\(after\)/, ""))}</span><em>Sentinel-1 · ${esc(orbit)}</em>`;
  };
  ["preCap", "postCap"].forEach((id) => { const el = $(id); if (el) new MutationObserver(sync).observe(el, { childList: true, characterData: true, subtree: true }); });
})();
