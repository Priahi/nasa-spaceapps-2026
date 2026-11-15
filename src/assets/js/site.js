/* Motion layer: Lenis smooth scroll + GSAP ScrollTrigger reveals ([data-fx]),
   spotlight cards, count-up stats, scroll-drawn step rail, before/after slider. Honors prefers-reduced-motion. */
(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = window.matchMedia("(pointer: fine)").matches;
  const hasGsap = typeof window.gsap !== "undefined";
  if (hasGsap && window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

  // Nav border + mobile menu
  const nav = document.querySelector(".nav");
  const onScroll = () => nav && nav.classList.toggle("scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  const btn = document.querySelector(".menu-btn"), menu = document.getElementById("menu");
  if (btn && menu) btn.addEventListener("click", () => { const o = menu.classList.toggle("open"); btn.setAttribute("aria-expanded", String(o)); });

  // Light / dark: follows the system until the visitor picks one
  const root = document.documentElement, tb = document.querySelector(".theme-btn");
  const label = () => tb && tb.setAttribute("aria-label", root.dataset.theme === "light" ? "Switch to dark theme" : "Switch to light theme");
  if (tb) { label(); tb.addEventListener("click", () => { root.dataset.theme = root.dataset.theme === "light" ? "dark" : "light"; try { localStorage.setItem("og-theme", root.dataset.theme); } catch (_) {} label(); }); }
  const mq = window.matchMedia("(prefers-color-scheme: light)");
  if (mq.addEventListener) mq.addEventListener("change", (ev) => { let t = null; try { t = localStorage.getItem("og-theme"); } catch (_) {} if (!t) { root.dataset.theme = ev.matches ? "light" : "dark"; label(); } });

  // Spotlight cursor glow
  document.querySelectorAll(".spot").forEach((el) => el.addEventListener("mousemove", (e) => {
    const r = el.getBoundingClientRect(); el.style.setProperty("--mx", e.clientX - r.left + "px"); el.style.setProperty("--my", e.clientY - r.top + "px");
  }));

  // Before/after slider
  document.querySelectorAll(".ba").forEach((ba) => {
    const input = ba.querySelector("input");
    const set = (v) => ba.style.setProperty("--x", v + "%");
    if (input) { input.addEventListener("input", () => set(input.value)); set(input.value); }
  });

  // Case selector: sticky chart that swaps with the step in view (wide screens) or with the tabs; phones show each step's own chart.
  document.querySelectorAll("[data-cases]").forEach((cs) => {
    const tabs = [...cs.querySelectorAll("[data-case][role=tab]")], panels = [...cs.querySelectorAll(".cs-panel")], steps = [...cs.querySelectorAll(".cs-step")];
    const set = (k) => {
      tabs.forEach((t) => t.setAttribute("aria-selected", String(t.dataset.case === k)));
      panels.forEach((p) => { const on = p.dataset.case === k; p.classList.toggle("on", on); if (on) p.classList.add("play"); });
      steps.forEach((s) => s.classList.toggle("on", s.dataset.case === k));
    };
    const wideQ = window.matchMedia("(min-width: 960px)");
    tabs.forEach((t) => t.addEventListener("click", () => {
      set(t.dataset.case);
      const st = steps.find((s) => s.dataset.case === t.dataset.case);
      if (st && wideQ.matches) window.scrollTo({ top: st.getBoundingClientRect().top + scrollY - innerHeight * 0.4, behavior: reduce ? "auto" : "smooth" });
    }));
    steps.forEach((s) => s.addEventListener("click", (ev) => { if (!ev.target.closest("a")) set(s.dataset.case); }));
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting && wideQ.matches) set(en.target.dataset.case); }), { rootMargin: "-45% 0px -45% 0px" });
      steps.forEach((s) => io.observe(s));
    }
  });

  // Count-up numbers: <strong data-count="0.8176" data-dec="4" data-prefix="" data-suffix="">
  function fmt(v, el) {
    const d = +(el.dataset.dec || 0), s = d ? v.toFixed(d) : Math.round(v).toLocaleString("en-US");
    return (el.dataset.prefix || "") + s + (el.dataset.suffix || "");
  }
  const counts = document.querySelectorAll("[data-count]");
  counts.forEach((el) => { el.textContent = fmt(+el.dataset.count, el); });

  // Scroll stories: sticky stage on wide screens, inline media on phones. Charts animate when their beat is active.
  const stories = document.querySelectorAll("[data-story]");
  const wide = window.matchMedia("(min-width: 960px)");
  if (stories.length && "IntersectionObserver" in window) {
    if (wide.matches) document.documentElement.classList.add("story-js");
    stories.forEach((st) => {
      const beats = Array.from(st.querySelectorAll(".beat")), panels = Array.from(st.querySelectorAll(".story-panel")), dots = Array.from(st.querySelectorAll(".story-dots li"));
      const setActive = (k) => {
        beats.forEach((b, j) => b.classList.toggle("is-active", j === k));
        panels.forEach((p, j) => { p.classList.toggle("on", j === k); if (j === k) p.classList.add("play"); });
        dots.forEach((d, j) => d.classList.toggle("on", j === k));
      };
      const io = new IntersectionObserver((ents) => ents.forEach((en) => {
        if (!en.isIntersecting) return;
        const k = beats.indexOf(en.target); setActive(k);
      }), { rootMargin: wide.matches ? "-45% 0px -45% 0px" : "0px 0px -25% 0px" });
      beats.forEach((b) => io.observe(b));
      const io2 = new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("play"); io2.unobserve(en.target); } }), { rootMargin: "0px 0px -15% 0px" });
      st.querySelectorAll(".beat-media").forEach((m) => io2.observe(m));
    });
  } else document.querySelectorAll(".beat-media, .story-panel").forEach((m) => m.classList.add("play"));
  if (reduce) document.querySelectorAll(".beat-media, .story-panel").forEach((m) => m.classList.add("play"));

  // Lazy videos: no source until near the viewport (preload=none + poster first). Muted loops play only while
  // on screen and pause when off. Reduced motion: never autoplay; show controls instead.
  const vids = document.querySelectorAll("video.lazyv");
  const arm = (v) => { if (v.dataset.armed) return; v.dataset.armed = "1"; v.querySelectorAll("source[data-src]").forEach((s) => { s.src = s.dataset.src; }); v.load(); };
  vids.forEach((v) => { if (reduce) { v.removeAttribute("data-auto"); v.controls = true; v.addEventListener("play", () => arm(v), { once: true }); v.addEventListener("pointerdown", () => arm(v), { once: true }); } });
  if ("IntersectionObserver" in window) {
    const near = new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) { arm(en.target); near.unobserve(en.target); } }), { rootMargin: "300px 0px" });
    const vis = new IntersectionObserver((ents) => ents.forEach((en) => {
      const v = en.target; if (!v.hasAttribute("data-auto")) return;
      if (en.isIntersecting && en.intersectionRatio >= 0.5) {
        if (v.dataset.once && v.dataset.played) return;
        arm(v); if (v.dataset.once && !v.dataset.played) { try { v.currentTime = 0; } catch (_) {} }
        v.dataset.played = "1"; const pr = v.play(); if (pr && pr.catch) pr.catch(() => { v.controls = true; });
      } else if (!v.paused) v.pause();
    }), { threshold: [0, 0.5] });
    vids.forEach((v) => { if (!reduce) near.observe(v); vis.observe(v); });
  } else vids.forEach((v) => { arm(v); v.controls = true; });
  // the official demo: Unmute button; pause when the user scrolls away happens above
  document.querySelectorAll(".dk-unmute").forEach((b) => {
    const v = b.parentElement.querySelector("video"); if (!v) return;
    b.addEventListener("click", () => { arm(v); v.muted = false; b.setAttribute("aria-pressed", "true"); const pr = v.play(); if (pr && pr.catch) pr.catch(() => {}); });
    v.addEventListener("volumechange", () => b.setAttribute("aria-pressed", String(!v.muted)));
  });

  if (reduce || !hasGsap) return;

  // Pinned pipeline diagram (desktop only; the stacked list is the fallback)
  document.querySelectorAll("[data-engine]").forEach((eng) => {
    if (!window.ScrollTrigger || !window.matchMedia("(min-width: 960px)").matches) return;
    const lis = Array.from(eng.querySelectorAll(".engine-steps li"));
    const imgs = Array.from(eng.querySelectorAll(".engine-stage img"));
    const hud = eng.querySelector(".engine-hud");
    if (!lis.length) return;
    eng.classList.add("is-pinned");
    let cur = -1;
    const setIdx = (k) => {
      if (k === cur) return; cur = k;
      lis.forEach((li, j) => { li.classList.toggle("active", j === k); li.classList.toggle("done", j < k); });
      imgs.forEach((im, j) => im.classList.toggle("on", j === k));
      if (hud) hud.textContent = lis[k].querySelector(".mono").textContent + " · " + lis[k].querySelector(".role").textContent;
    };
    setIdx(0);
    lis.forEach((li, j) => li.addEventListener("click", () => {
      const st = eng.offsetTop + (eng.offsetHeight - innerHeight) * (j + 0.5) / lis.length;
      window.scrollTo({ top: st, behavior: "smooth" });
    }));
    ScrollTrigger.create({ trigger: eng, start: "top top", end: "bottom bottom",
      onUpdate: (self) => setIdx(Math.min(lis.length - 1, Math.floor(self.progress * lis.length))) });
  });

  // Smooth scroll on fine pointers only (same settings as the personal site)
  if (fine && window.Lenis) {
    const lenis = new Lenis({ lerp: 0.1, smoothWheel: true, syncTouch: false, anchors: { offset: -96 } });
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000)); gsap.ticker.lagSmoothing(0);
  }

  // onFirstEnter: only animate things that start below the fold, so nothing on screen ever flashes.
  function onFirstEnter(el, prepare, enter, rootMargin) {
    let first = true;
    const io = new IntersectionObserver(([en]) => {
      if (first) { first = false; if (en.isIntersecting || en.boundingClientRect.top < innerHeight) { io.disconnect(); return; } prepare(); return; }
      if (en.isIntersecting) { io.disconnect(); enter(); }
    }, { rootMargin: rootMargin || "0px 0px -8% 0px" });
    io.observe(el);
  }

  document.querySelectorAll("[data-fx]").forEach((el) => {
    const fx = el.dataset.fx;
    if (fx === "rise") onFirstEnter(el, () => gsap.set(el, { autoAlpha: 0, y: 28 }), () => gsap.to(el, { autoAlpha: 1, y: 0, duration: 0.8, ease: "power3.out", clearProps: "transform" }));
    else if (fx === "stagger") { const items = Array.from(el.children); onFirstEnter(el, () => gsap.set(items, { autoAlpha: 0, y: 24 }), () => gsap.to(items, { autoAlpha: 1, y: 0, duration: 0.7, stagger: 0.08, ease: "power3.out", clearProps: "transform" })); }
    else if (fx === "wipe") onFirstEnter(el, () => gsap.set(el, { clipPath: "inset(0% 100% 0% 0%)" }), () => gsap.to(el, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.1, ease: "power3.inOut", clearProps: "clipPath" }));
    else if (fx === "parallax") { const d = +(el.dataset.depth || 12); gsap.fromTo(el, { yPercent: -d / 2 }, { yPercent: d / 2, ease: "none", scrollTrigger: { trigger: el, start: "top bottom", end: "bottom top", scrub: true } }); }
  });

  // Count up when the stat scrolls in
  counts.forEach((el) => {
    const target = +el.dataset.count, o = { v: 0 };
    onFirstEnter(el, () => { el.textContent = fmt(0, el); }, () => gsap.to(o, { v: target, duration: 1.4, ease: "power2.out", onUpdate: () => { el.textContent = fmt(o.v, el); }, onComplete: () => { el.textContent = fmt(target, el); } }), "0px 0px -5% 0px");
  });

  // Step rail fills as you scroll through it
  document.querySelectorAll(".steps").forEach((list) => {
    const bar = list.querySelector(".bar"); if (!bar) return;
    gsap.fromTo(bar, { scaleY: 0 }, { scaleY: 1, ease: "none", scrollTrigger: { trigger: list, start: "top 75%", end: "bottom 60%", scrub: 0.6 } });
  });

  // Re-measure after images and the demo iframe settle
  window.addEventListener("load", () => ScrollTrigger.refresh());
})();
