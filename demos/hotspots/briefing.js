/* Experiment briefing deck (slide-style panels inside each demo).
   Usage: Briefing.init({ deck: "...", slides: [{kicker, title, html}], launchLabel }).
   Open with the floating button, an element with [data-briefing-open], or the URL hash #briefing / #briefing-3.
   Keys: Left/Right, PageUp/PageDown, Space, Home/End, Esc. Mouse wheel and touch swipe also move slides. */
(function () {
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // Horizontal bar chart (SVG) built from real numbers.
  function bars(rows, opt) {
    opt = opt || {};
    const W = opt.width || 760, rowH = opt.rowH || 34, labW = opt.labelWidth || 260, pad = 70;
    const max = opt.max != null ? opt.max : Math.max.apply(null, rows.map((r) => r.value)) * 1.08;
    const min = opt.min || 0;
    const H = rows.length * rowH + 30;
    const fmt = opt.fmt || ((v) => v.toFixed(4));
    let s = `<svg class="bf-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(opt.aria || "bar chart")}">`;
    rows.forEach((r, i) => {
      const y = 8 + i * rowH;
      const w = Math.max(2, ((r.value - min) / (max - min)) * (W - labW - pad));
      const col = r.color || (r.hl ? "#5dcc8a" : r.neg ? "#ef8b6b" : "#4a6286");
      s += `<text x="${labW - 10}" y="${y + rowH / 2 + 1}" text-anchor="end" fill="#d3dcea" font-size="14" font-family="system-ui,sans-serif" dominant-baseline="middle">${esc(r.label)}</text>`;
      s += `<rect x="${labW}" y="${y + 5}" width="${w}" height="${rowH - 12}" rx="4" fill="${col}"/>`;
      s += `<text x="${labW + w + 8}" y="${y + rowH / 2 + 1}" fill="#fff" font-size="14" font-family="ui-monospace,Menlo,monospace" dominant-baseline="middle">${esc(fmt(r.value))}</text>`;
    });
    if (opt.axis) s += `<text x="${W - 4}" y="${H - 6}" text-anchor="end" fill="#9aa8bd" font-size="12" font-family="system-ui,sans-serif">${esc(opt.axis)}</text>`;
    return s + "</svg>";
  }

  function flow(steps) {
    return '<div class="bf-flow">' + steps.map((st, i) =>
      (i ? '<div class="bf-arrow">→</div>' : "") + `<div class="bf-step"><b>${esc(st[0])}</b><small>${st[1]}</small></div>`
    ).join("") + "</div>";
  }

  function kpis(items) {
    return '<div class="bf-kpis">' + items.map((k) => `<div class="bf-kpi ${k[2] || ""}"><b>${esc(k[0])}</b><span>${k[1]}</span></div>`).join("") + "</div>";
  }

  function fig(src, cap) {
    return `<figure style="margin:0"><div class="bf-fig"><img src="${esc(src)}" alt="${esc(cap)}"></div><p class="bf-cap">${cap}</p></figure>`;
  }

  // Structured layman slide: plain body, a visual, a "why it matters" line, and expert details folded away.
  function renderBody(sl) {
    let h = "";
    if (sl.body) h += `<div class="bf-body">${[].concat(sl.body).map((x) => `<p>${x}</p>`).join("")}</div>`;
    if (sl.visual) h += `<div class="bf-visual">${sl.visual}</div>`;
    if (sl.html) h += sl.html;
    if (sl.why) h += `<div class="bf-why"><b>Why it matters</b><span>${sl.why}</span></div>`;
    if (sl.expert) h += `<details class="bf-expert"><summary>For the experts: exact numbers and method</summary><div class="bf-expert-in">${sl.expert}</div></details>`;
    return h;
  }

  function glossary(items) {
    return '<dl class="bf-gloss">' + items.map(([t, d]) => `<div><dt>${esc(t)}</dt><dd>${d}</dd></div>`).join("") + "</dl>";
  }

  function init(cfg) {
    const slides = cfg.slides || [];
    let idx = 0, open = false, wheelLock = 0;
    const ov = document.createElement("div");
    ov.className = "bf-overlay";
    ov.setAttribute("role", "dialog");
    ov.setAttribute("aria-label", "Experiment briefing");
    ov.innerHTML = `
      <div class="bf-top"><span class="bf-deck">Experiment briefing · ${esc(cfg.deck || "")}</span>
        <span class="bf-count" id="bfCount"></span><button class="bf-btn" id="bfClose" title="Back to the demo (Esc)">Back to demo ✕</button></div>
      <div class="bf-stage"><div class="bf-track" id="bfTrack">${slides.map((sl, i) =>
        `<section class="bf-slide" data-i="${i}" aria-roledescription="slide" aria-label="${i + 1} of ${slides.length}"><div class="bf-slide-inner">
          ${sl.kicker ? `<div class="bf-kicker">${esc(sl.kicker)}</div>` : ""}<h2>${esc(sl.title)}</h2>${renderBody(sl)}</div></section>`).join("")}</div></div>
      <div class="bf-bottom"><button class="bf-btn" id="bfPrev">← Prev</button>
        <div class="bf-dots" id="bfDots">${slides.map((_, i) => `<button class="bf-dot" data-i="${i}" aria-label="Slide ${i + 1}"></button>`).join("")}</div>
        <span class="bf-hint">← → keys · scroll · swipe · Esc</span><button class="bf-btn" id="bfNext">Next →</button></div>`;
    document.body.appendChild(ov);
    const track = ov.querySelector("#bfTrack");

    function go(i, fromHash) {
      idx = Math.max(0, Math.min(slides.length - 1, i));
      track.style.transform = `translateX(${-100 * idx}%)`;
      ov.querySelector("#bfCount").textContent = `${idx + 1} / ${slides.length} · ${slides[idx].title}`;
      ov.querySelectorAll(".bf-dot").forEach((d, j) => d.classList.toggle("on", j === idx));
      ov.querySelector("#bfPrev").disabled = idx === 0;
      ov.querySelector("#bfNext").disabled = idx === slides.length - 1;
      const sl = ov.querySelectorAll(".bf-slide")[idx]; if (sl) sl.scrollTop = 0;
      if (!fromHash) history.replaceState(null, "", `#briefing-${idx + 1}`);
    }
    function show(i, fromHash) { open = true; ov.classList.add("open"); document.documentElement.style.overflow = "hidden"; go(i || 0, fromHash); }
    function hide() { open = false; ov.classList.remove("open"); document.documentElement.style.overflow = ""; history.replaceState(null, "", location.pathname + location.search); }

    ov.querySelector("#bfClose").onclick = hide;
    ov.querySelector("#bfPrev").onclick = () => go(idx - 1);
    ov.querySelector("#bfNext").onclick = () => go(idx + 1);
    ov.querySelectorAll(".bf-dot").forEach((d) => (d.onclick = () => go(+d.dataset.i)));
    document.addEventListener("keydown", (e) => {
      if (!open) return;
      if (["ArrowRight", "PageDown", " "].includes(e.key)) { e.preventDefault(); go(idx + 1); }
      else if (["ArrowLeft", "PageUp"].includes(e.key)) { e.preventDefault(); go(idx - 1); }
      else if (e.key === "Home") go(0);
      else if (e.key === "End") go(slides.length - 1);
      else if (e.key === "Escape") hide();
    });
    ov.addEventListener("wheel", (e) => {
      const sl = ov.querySelectorAll(".bf-slide")[idx];
      const dy = e.deltaY || e.deltaX;
      // let tall slides scroll internally first
      if (sl && dy > 0 && sl.scrollTop + sl.clientHeight < sl.scrollHeight - 2) return;
      if (sl && dy < 0 && sl.scrollTop > 2) return;
      const now = Date.now(); if (now - wheelLock < 650 || Math.abs(dy) < 25) return;
      wheelLock = now; go(idx + (dy > 0 ? 1 : -1));
    }, { passive: true });
    let tx = null;
    ov.addEventListener("touchstart", (e) => { tx = e.touches[0].clientX; }, { passive: true });
    ov.addEventListener("touchend", (e) => { if (tx == null) return; const dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 60) go(idx + (dx < 0 ? 1 : -1)); tx = null; }, { passive: true });

    const btn = document.createElement("button");
    btn.className = "bf-launch"; btn.type = "button"; btn.id = "briefingLaunch";
    btn.textContent = cfg.launchLabel || "▶ Experiment briefing";
    btn.onclick = () => show(0);
    if (!document.querySelector("[data-briefing-open]")) document.body.appendChild(btn);
    else { btn.style.display = "none"; document.body.appendChild(btn); }
    document.querySelectorAll("[data-briefing-open]").forEach((el) => el.addEventListener("click", (e) => { e.preventDefault(); show(+(el.dataset.briefingOpen || 1) - 1); }));

    function fromHash() { const m = /^#briefing(?:-(\d+))?$/.exec(location.hash); if (m) show(m[1] ? +m[1] - 1 : 0, true); }
    window.addEventListener("hashchange", fromHash);
    fromHash();
    window.Briefing.open = show; window.Briefing.close = hide;
  }

  window.Briefing = { init, bars, flow, kpis, fig, esc, glossary };
})();
