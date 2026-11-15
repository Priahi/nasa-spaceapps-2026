/* SAR Change page: scroll-driven "what changed" stage (26 Oct -> 31 Oct -> change -> 19 Nov). */
(() => {
  const sc = document.querySelector(".sc"); if (!sc) return;
  const steps = [...sc.querySelectorAll(".sc-step")], lys = [...sc.querySelectorAll(".sc-ly")], badge = sc.querySelector(".sc-badge");
  const set = (k) => {
    lys.forEach((l) => l.classList.toggle("on", l.dataset.ly === k));
    steps.forEach((s) => s.classList.toggle("on", s.dataset.ly === k));
    sc.dataset.ly = k;
    const s = steps.find((x) => x.dataset.ly === k);
    if (s && badge) badge.innerHTML = `<b>${s.querySelector("strong").textContent}</b><span>${s.querySelector(".u").textContent}</span>`;
  };
  const io = new IntersectionObserver((es) => { es.forEach((en) => { if (en.isIntersecting) set(en.target.dataset.ly); }); }, { rootMargin: "-45% 0px -45% 0px" });
  const wide = matchMedia("(min-width: 861px)");
  if (steps[0] && steps[0].parentElement) { steps[0].parentElement.setAttribute("role", "group"); steps[0].parentElement.setAttribute("aria-label", "Radar passes"); }
  steps.forEach((s) => { if (wide.matches) io.observe(s); s.setAttribute("role", "button"); s.tabIndex = 0; s.addEventListener("click", () => set(s.dataset.ly)); s.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); set(s.dataset.ly); } }); });
  wide.addEventListener("change", (m) => steps.forEach((s) => m.matches ? io.observe(s) : io.unobserve(s)));
  set(steps[0].dataset.ly);
})();
