/* Orbit to Ground: shared decision-support (C2-style) component. SIMULATED tasking only: nothing here talks to a real drone,
   camera, satellite, crew or alerting system. API documented in /PARALLEL.md. No dependencies. */
(function () {
  "use strict";
  const ICON = {
    drone: '<path d="M5 5l4 4m6 6 4 4M19 5l-4 4M9 15l-4 4"/><circle cx="5" cy="5" r="2.2"/><circle cx="19" cy="5" r="2.2"/><circle cx="5" cy="19" r="2.2"/><circle cx="19" cy="19" r="2.2"/><rect x="9" y="9" width="6" height="6" rx="1.5"/>',
    camera: '<path d="M3 8h4l2-3h6l2 3h4v11H3z"/><circle cx="12" cy="13" r="3.5"/>',
    satellite: '<path d="M13 7l4 4-6 6-4-4z"/><path d="M7 13l-4 4m14-6 4-4M10 4l3 3M17 11l3 3"/><path d="M15 19a5 5 0 0 0 4-4"/>',
    crew: '<circle cx="8" cy="8" r="3"/><circle cx="16" cy="9" r="2.5"/><path d="M2.5 20a5.5 5.5 0 0 1 11 0M13 20a4 4 0 0 1 8 0"/>',
    notice: '<path d="M4 10v4h3l6 4V6L7 10z"/><path d="M17 9a4 4 0 0 1 0 6M19.5 6.5a7.5 7.5 0 0 1 0 11"/>',
    engineer: '<path d="M4 20h16M6 20V10l6-5 6 5v10"/><path d="M10 20v-5h4v5"/>',
    sensor: '<circle cx="12" cy="12" r="2"/><path d="M8 8a5.5 5.5 0 0 0 0 8M16 8a5.5 5.5 0 0 1 0 8M5 5a10 10 0 0 0 0 14M19 5a10 10 0 0 1 0 14"/>',
    plan: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/>',
    seed: '<path d="M12 21V11"/><path d="M12 11C12 6 8 4 4 4c0 5 3 7 8 7zM12 13c0-4 3-6 8-6 0 4-3 6-8 6z"/>',
    truck: '<path d="M2 6h11v10H2zM13 10h4l3 3v3h-7z"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="16.5" cy="17.5" r="1.8"/>'
  };
  const STEPS = ["Queued", "Tasked", "In progress", "Done"];
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const icon = (k) => `<svg class="c2-ico" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${ICON[k] || ICON.plan}</svg>`;
  const clock = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const fire = (type, detail) => window.dispatchEvent(new CustomEvent("og:c2", { detail: Object.assign({ type }, detail) }));
  const reduce = () => window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  function mount(target, cfg) {
    const root = typeof target === "string" ? document.querySelector(target) : target;
    if (!root) return null;
    const A = cfg.actions || [];
    const st = { sel: null, approved: {}, tasks: [], log: [], timers: [] };
    root.classList.add("c2");
    root.innerHTML = `
      <div class="c2-head">
        <div><p class="c2-kick">${esc(cfg.kicker || "Decision support")}</p><h2 class="c2-title">${esc(cfg.title || "Recommended actions")}</h2>
        ${cfg.user ? `<p class="c2-user">For: <b>${esc(cfg.user)}</b></p>` : ""}</div>
        <div class="c2-hr"><span class="c2-sim" title="A demo of how approved actions would be handed to people and machines. Nothing is sent anywhere.">Simulated tasking</span>
        <button type="button" class="c2-btn c2-ghost c2-reset">Reset</button></div>
      </div>
      <div class="c2-grid">
        <ol class="c2-list" aria-label="Recommended actions">${A.map((a, i) => `
          <li class="c2-card" data-id="${esc(a.id)}" tabindex="-1">
            <div class="c2-card-top"><span class="c2-cls">${esc(a.cls || "Action")}</span><span class="c2-state" data-s="proposed">Proposed</span></div>
            <h3 class="c2-act">${esc(a.title || a.act)}</h3>
            <dl class="c2-flow">
              <div><dt>Satellite shows</dt><dd>${esc(a.sat)}</dd></div>
              ${a.act && a.title ? `<div><dt>I will</dt><dd>${esc(a.act)}</dd></div>` : ""}
              <div><dt>Expected</dt><dd>${esc(a.out)}</dd></div>
            </dl>
            ${(a.tasks || []).length ? `<ul class="c2-assets">${a.tasks.map((t) => `<li>${icon(t.asset)}<span>${esc(t.label)}</span></li>`).join("")}</ul>` : ""}
            <div class="c2-btns">
              <button type="button" class="c2-btn c2-primary c2-go">${esc(a.verb || "Approve")}</button>
              <button type="button" class="c2-btn c2-ghost c2-show" aria-pressed="false">Show on map</button>
            </div>
          </li>`).join("")}
        </ol>
        <aside class="c2-side">
          <section class="c2-q"><h3>Task queue</h3><p class="c2-empty">No tasks yet. Approve an action to queue its tasks.</p><ul class="c2-tasks" aria-live="polite"></ul></section>
          <section class="c2-tl"><h3>Timeline</h3><ol class="c2-log"></ol></section>
        </aside>
      </div>
      <p class="c2-foot">${esc(cfg.foot || "Simulated: shows how an approved action would be handed to crews, sensors and alerting. No real drones, cameras, satellites or alerts are contacted.")}</p>`;
    const $ = (s) => root.querySelector(s), $$ = (s) => [...root.querySelectorAll(s)];
    const card = (id) => root.querySelector(`.c2-card[data-id="${CSS.escape(id)}"]`);
    const byId = (id) => A.find((a) => a.id === id);

    function log(msg) { st.log.unshift({ t: clock(), msg }); $(".c2-log").innerHTML = st.log.slice(0, 14).map((l) => `<li><time>${l.t}</time><span>${esc(l.msg)}</span></li>`).join(""); }
    function renderTasks() {
      $(".c2-empty").hidden = st.tasks.length > 0;
      $(".c2-tasks").innerHTML = st.tasks.map((t) => `<li class="c2-task" data-s="${t.s}">${icon(t.asset)}<div><b>${esc(t.label)}</b><small>${esc(t.from)}${t.eta ? " · " + esc(t.eta) : ""}</small>
        <div class="c2-steps" role="progressbar" aria-valuemin="0" aria-valuemax="3" aria-valuenow="${t.s}" aria-valuetext="${STEPS[t.s]}">${STEPS.map((n, i) => `<i class="${i <= t.s ? "on" : ""}"></i>`).join("")}</div></div><span class="c2-pill">${STEPS[t.s]}</span></li>`).join("");
    }
    function setState(id, s, label) { const c = card(id); if (!c) return; const el = c.querySelector(".c2-state"); el.dataset.s = s; el.textContent = label; c.dataset.s = s; }

    function select(id, opts) {
      const same = st.sel === id && !(opts && opts.keep);
      st.sel = same ? null : id;
      $$(".c2-card").forEach((c) => { const on = c.dataset.id === st.sel; c.classList.toggle("sel", on); c.querySelector(".c2-show").setAttribute("aria-pressed", String(on)); c.querySelector(".c2-show").textContent = on ? "Showing on map" : "Show on map"; });
      const a = st.sel ? byId(st.sel) : null;
      try { cfg.onSelect && cfg.onSelect(a, { source: (opts && opts.source) || "api" }); } catch (e) { console.warn("c2 onSelect", e); }
      fire("select", { app: cfg.app, action: a });
      return a;
    }
    function approve(id) {
      const a = byId(id); if (!a) return;
      if (st.approved[id]) { // undo
        delete st.approved[id]; st.tasks = st.tasks.filter((t) => t.aid !== id); renderTasks(); setState(id, "proposed", "Proposed");
        card(id).querySelector(".c2-go").textContent = a.verb || "Approve"; log(`Withdrawn: ${a.title || a.act}`);
        try { cfg.onApprove && cfg.onApprove(a, false); } catch (e) { console.warn(e); } fire("withdraw", { app: cfg.app, action: a }); return;
      }
      st.approved[id] = true; setState(id, "approved", "Approved"); card(id).querySelector(".c2-go").textContent = "Undo";
      if (st.sel !== id) select(id, { keep: true, source: "approve" });
      log(`Approved: ${a.title || a.act}`);
      try { cfg.onApprove && cfg.onApprove(a, true); } catch (e) { console.warn(e); }
      fire("approve", { app: cfg.app, action: a });
      (a.tasks || []).forEach((t, k) => {
        const task = { aid: id, asset: t.asset, label: t.label, eta: t.eta, from: a.cls || a.title, s: 0 };
        st.tasks.push(task); log(`Queued: ${t.label}`);
        const step = reduce() ? 250 : 1100;
        [1, 2, 3].forEach((s) => st.timers.push(setTimeout(() => {
          if (!st.approved[id] || !st.tasks.includes(task)) return;
          task.s = s; renderTasks(); log(`${STEPS[s]}: ${t.label}`);
          try { cfg.onTask && cfg.onTask(a, task, STEPS[s]); } catch (e) { console.warn(e); }
          fire("task", { app: cfg.app, action: a, task, status: STEPS[s] });
          if (s === 3 && st.tasks.filter((x) => x.aid === id).every((x) => x.s === 3)) setState(id, "done", "Tasks done");
        }, step * (s + k * 0.6))));
      });
      renderTasks();
    }
    function reset() {
      st.timers.forEach(clearTimeout); st.timers = []; st.approved = {}; st.tasks = []; st.log = [];
      A.forEach((a) => { setState(a.id, "proposed", "Proposed"); card(a.id).querySelector(".c2-go").textContent = a.verb || "Approve"; });
      renderTasks(); $(".c2-log").innerHTML = ""; if (st.sel) select(st.sel);
      try { cfg.onReset && cfg.onReset(); } catch (e) { console.warn(e); } fire("reset", { app: cfg.app });
    }
    root.addEventListener("click", (ev) => {
      const c = ev.target.closest(".c2-card"); if (ev.target.closest(".c2-reset")) return reset();
      if (!c) return; if (ev.target.closest(".c2-go")) return approve(c.dataset.id); if (ev.target.closest(".c2-show")) return select(c.dataset.id, { source: "show" });
    });
    renderTasks();
    return { select, approve, reset, state: st, root };
  }

  /* Before -> after impact cards. items: [{user, decision, before, after, geo:{v,l}, metric:{v,l}}] */
  function impact(target, items, opts) {
    const root = typeof target === "string" ? document.querySelector(target) : target; if (!root) return;
    opts = opts || {};
    root.classList.add("c2-impact");
    root.innerHTML = (opts.title ? `<h2 class="c2-title">${esc(opts.title)}</h2>` : "") + `<div class="c2-imp-grid">` + items.map((it) => `
      <article class="c2-imp">
        <header><span class="c2-cls">${esc(it.user)}</span><h3>${esc(it.decision)}</h3></header>
        <div class="c2-ba"><div class="c2-b"><p>Before</p><ul>${[].concat(it.before).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
        <span class="c2-arrow" aria-hidden="true">→</span>
        <div class="c2-a"><p>With this tool</p><ul>${[].concat(it.after).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div></div>
        <footer>${it.geo ? `<div><b>${esc(it.geo.v)}</b><span>${esc(it.geo.l)}</span></div>` : ""}${it.metric ? `<div><b>${esc(it.metric.v)}</b><span>${esc(it.metric.l)}</span></div>` : ""}</footer>
      </article>`).join("") + `</div>` + (opts.note ? `<p class="c2-foot">${esc(opts.note)}</p>` : "");
  }
  window.OGC2 = { mount, impact, icon, ICONS: Object.keys(ICON) };
})();
