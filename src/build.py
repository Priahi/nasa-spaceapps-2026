#!/usr/bin/env python3
"""Build the combined static site into ../dist.
   - copies the three static demo builds into /<slug>/app/ and applies the suite theme + back-links
   - renders the landing page and one story page per project from content.py
Usage: python3 src/build.py [--demos /path/to/nasa-spaceapps/deploy]"""
import html, json, re, shutil, sys
from pathlib import Path
from content import SITE, PROJECTS, CRITERIA, TRENDS, GLOSSARY, STAKES, SYSTEM_PROBLEM, MODULES, UPGRADES

ROOT = Path(__file__).resolve().parent.parent
SRC, DIST = ROOT / "src", ROOT / "dist"
DEMOS = Path(sys.argv[sys.argv.index("--demos") + 1]) if "--demos" in sys.argv else ROOT / "demos"
SITE_URL = "https://nasa-spaceapps-2026.pages.dev"
import os
REPO_URL = "https://github.com/Priahi/nasa-spaceapps-2026"
SHOW_REPO = os.environ.get("SHOW_REPO", "1") == "1"  # repo is public since 14 Nov 2026
DEMO_DIR = {"hotspots": "hotspots", "sar-change": "sar-change", "field-shift": "field-shift"}
THEME = {"hotspots": "hotspots.css", "sar-change": "sar.css", "field-shift": "field.css"}
e = html.escape
# UI greens/ambers -> suite blue/purple (UI chrome only; data colour ramps and crop-class colours in data/*.json are untouched)
RECOLOR = {"#5dcc8a": "#b9a6ff", "#0f2a22": "#1a1640", "#1f5a45": "#3d3480", "#d9f3e6": "#ece6ff", "#8fe3a1": "#c9bbff",
           "#3db8a0": "#d4c4ff", "#173a36": "#1d2350", "#1c2b20": "#12141c", "#2c5e3f": "#1d4ed8", "#3f7a54": "#6d28d9",
           "#8fb89a": "#9ab0e6", "#dce8de": "#dfe5f5", "#e8f0e8": "#eef1fa", "#eaf4ec": "#eef1fa", "#e8a317": "#c9bbff", "#f0b43c": "#c9bbff", "#f0d9a8": "#d4c4ff", "#f3e2bd": "#e6ddff", "#17140c": "#16133a"}

# ---------- demos ----------
def suite_bar(slug):
    links = "".join(f'<a href="/{p["slug"]}/"{" aria-current=\"page\"" if p["slug"]==slug else ""}>{e(p["name"].split(":")[0])}</a>' for p in PROJECTS)
    return (f'<div class="suite-bar"><a href="/{slug}/">&larr; Project page</a><span class="sp"><a class="home" href="/"><span class="dot"></span>All projects</a>{links}</span></div>'
            '<script>if(window.self!==window.top)document.documentElement.classList.add("in-frame");</script>')

def copy_demo(slug):
    src, out = DEMOS / DEMO_DIR[slug], DIST / slug / "app"
    shutil.copytree(src, out, ignore=shutil.ignore_patterns("_headers", "robots.txt"))
    shutil.copy(SRC / "demo-theme" / "common.css", out / "suite-common.css")
    shutil.copy(SRC / "demo-theme" / THEME[slug], out / "suite-theme.css")
    idx = out / "index.html"; h = idx.read_text()
    h = re.sub(r'\s*<meta name="robots"[^>]*>', "", h)
    h = re.sub(r'(href|src)="/(?!/)', r'\1="', h)  # root-absolute assets -> relative (demo now lives under /<slug>/app/)
    h = h.replace("</head>", '  <link rel="stylesheet" href="suite-common.css" />\n  <link rel="stylesheet" href="suite-theme.css" />\n</head>', 1)
    h = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + suite_bar(slug), h, count=1)
    # public-build wording (was written for the private preview)
    h = h.replace("NASA Space Apps 2026 · unlisted demo · not submitted", "NASA Space Apps 2026")
    h = h.replace("Unlisted demo build (static, precomputed from the local model run).", "Static build, precomputed from the model run.")
    h = h.replace("Unlisted demo, not submitted, not a published benchmark.", "One seed, not a published benchmark.")
    h = h.replace("Local demo for NASA International Space Apps Challenge 2026", "NASA International Space Apps Challenge 2026")
    h = h.replace("Cite every source in a Space Apps submission and disclose this pre-existing tooling. This is a local demo, not a submitted project and not a published benchmark.",
                  "All sources are cited above. Builds on our earlier code and open-source libraries. One seed, not a published benchmark.")
    h = h.replace("Cite every source in a Space Apps submission and disclose this pre-existing tooling.", "Builds on our earlier code and open-source libraries.")
    idx.write_text(h)
    for f in list(out.glob("*.js")) + list(out.glob("*.css")) + [idx]:
        if f.name.startswith("suite-"): continue
        t = f.read_text(); t2 = t.replace(" local demo.", " demo.")
        for a, b in RECOLOR.items(): t2 = re.sub(a, b, t2, flags=re.I)
        if slug == "field-shift": t2 = re.sub("#c4922c", "#6d28d9", t2, flags=re.I)
        if t2 != t: f.write_text(t2)

# ---------- page chrome ----------
def head(title, desc, path, img="og.png"):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}" />
<link rel="canonical" href="{SITE_URL}{path}" />
<meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(desc)}" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{SITE_URL}{path}" />
<meta property="og:image" content="{SITE_URL}/assets/img/{img}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="theme-color" content="#07091a" />
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml" />
<link rel="preload" href="/assets/fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin />
<link rel="stylesheet" href="/assets/css/site.css" />
<link rel="stylesheet" href="/assets/css/system.css" />
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
"""

def nav(active):
    items = [("/#why", "Why"), ("/#what", "What"), ("/#how", "How")] + [(f"/{p['slug']}/", p["name"].split(":")[0]) for p in PROJECTS]
    li = "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if h==active else ""}>{e(t)}</a></li>' for h, t in items)
    mi = "".join(f'<a href="{h}">{e(t)}</a>' for h, t in items)
    return f"""<header class="nav"><a class="brand" href="/"><span class="brand-dot" aria-hidden="true"></span>Orbit to Ground</a>
<nav aria-label="Main"><ul class="nav-links">{li}</ul></nav>
<button class="menu-btn" aria-expanded="false" aria-controls="menu">Menu</button></header>
<div class="menu" id="menu">{mi}</div>
"""

REPO_NOTE = f' Source code: <a href="{REPO_URL}">{REPO_URL.replace("https://","")}</a> (Apache-2.0).' if SHOW_REPO else " Code licence: Apache-2.0."
FOOT = f"""<footer class="site"><div class="wrap">
<p><strong>Orbit to Ground</strong> · NASA International Space Apps Challenge 2026 · {e(SITE['challenge'])} · Team {e(SITE['team'])} ({e(SITE['author'])}).{REPO_NOTE}</p>
<p>Data: NASA FIRMS, NASA-ISRO NISAR (via NASA CMR and ASF DAAC), NASA POWER, NASADEM, MODIS, plus ESA Copernicus Sentinel-1, Sen1Floods11, USDA NASS CDL and ISRIC SoilGrids. Province outlines: Natural Earth (public domain). Each project page lists its sources and licences. This site is not affiliated with or endorsed by NASA.</p>
<p>AI disclosure: AI coding assistants helped write and refactor parts of the code, site and text. All models, metrics and figures come from our own runs on the public data listed. Model metrics are one seed each, not a published benchmark. {e(SITE['built_on'])}</p>
</div></footer>
<script src="/assets/vendor/gsap.min.js" defer></script>
<script src="/assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="/assets/vendor/lenis.min.js" defer></script>
<script src="/assets/js/site.js" defer></script>
<script src="/assets/js/trends.js" defer></script>
</body></html>
"""

def kpi_html(k):
    pre = k.get("prefix", "")
    return (f'<div class="spot kpi-tile{" neg" if k.get("neg") else ""}"><div class="spot-body" style="padding:0">'
            f'<span class="vs">{e(k["vs"])}</span>'
            f'<strong class="{"" if k.get("neg") else "grad"}" data-count="{k["v"]}" data-dec="{k["dec"]}" data-prefix="{e(pre)}" data-suffix="{e(k["suf"])}">{e(pre)}{k["v"]}{e(k["suf"])}</strong>'
            f'<p>{e(k["p"])}</p></div></div>')

# ---------- landing ----------
LOGIN_KEYS = ("GRACE", "OPERA", "MCD64A1", "HLS v2", "SMAP", "IMERG", "GLDAS", "Earthdata login")
def login_cell(name):
    y = any(k in name for k in LOGIN_KEYS)
    return f'<td class="{"login-y" if y else "login-n"}">{"Earthdata login" if y else "Public, no login"}</td>'

def landing():
    def kpi(p): return f'<strong class="grad">{e(p["card_kpi"][0])}</strong><span>{e(p["card_kpi"][1])}</span>'
    stakes = "".join(f"""<li class="tier-card tier-{t}"><p class="tier-name">{e(x['theme'])}</p><strong>{e(x['big'])}</strong><p class="tier-text">{e(x['line'])}</p>
<p class="tier-source"><a href="{x['url']}">{e(x['src'])}</a></p></li>""" for x, t in zip(STAKES, ("milestone", "category", "traction")))
    # pinned engine: three modules + trend layer
    parts = [(MODULES[p["slug"]]["role"], p["name"].split(":")[0], MODULES[p["slug"]]["statement"], p["card_kpi"][0] + " · " + p["card_kpi"][1], p["card_img"], f"/{p['slug']}/") for p in PROJECTS]
    parts.append(("Measure", "Trend layer", "Every module answers the same four questions: what is changing, where, by how much, and is it significant? Mann-Kendall and Sen's slope on 23 to 45 years of NASA records.", "Canada fire +3,019 detections/yr (p = 0.035) · Iowa frost-free +0.43 d/yr (p = 0.006)", "trend-layer.webp", "/#trends"))
    steps = "".join(f'<li class="{"active" if k == 0 else ""}"><span class="mono">0{k+1}</span><span class="role">{e(r)}</span><strong>{e(n)}</strong><p>{e(t)}</p><span class="engine-fact mono">{e(f)}</span></li>' for k, (r, n, t, f, im, h) in enumerate(parts))
    stage = "".join(f'<img src="/assets/img/{im}" alt="{e(n)}" class="{"on" if k == 0 else ""}" loading="lazy" />' for k, (r, n, t, f, im, h) in enumerate(parts))
    elist = "".join(f'<article><div class="engine-card"><img src="/assets/img/{im}" alt="{e(n)}" loading="lazy" /></div><p class="mono">0{k+1} · {e(r)}</p><h3>{e(n)}</h3><p>{e(t)}</p><p class="engine-fact mono">{e(f)}</p></article>' for k, (r, n, t, f, im, h) in enumerate(parts))
    mods = ""
    for k, p in enumerate(PROJECTS):
        M = MODULES[p["slug"]]
        li = "".join(f"<li>{e(d)}</li>" for d in M["delivers"])
        mods += f"""<article class="spot mod-card{' flip' if k % 2 else ''}" data-fx="rise"><span class="beam" aria-hidden="true"></span>
<a class="mod-media" href="/{p['slug']}/"><img src="/assets/img/{p['card_img']}" alt="{e(p['name'])} screenshot" loading="lazy" width="1200" height="750" /></a>
<div class="mod-body"><span class="num">Module {p['n']} · {e(M['role'])}</span><h3>{e(p['name'])}</h3>
<p class="stmt"><b style="color:var(--ink);font-weight:500">The problem.</b> {e(M['statement'])}</p><ul>{li}</ul>
<div class="kpi">{kpi(p)}</div>
<div class="actions" style="margin-top:1.1rem"><a class="btn" href="/{p['slug']}/">Open the module</a><a class="btn ghost" href="/{p['slug']}/app/">Live tool &nearr;</a></div></div></article>"""
    cases = ""
    for p in PROJECTS:
        t = TRENDS[p["slug"]]; c = t["case"]; ok, sigt = c["sig"]
        cases += f"""<a class="spot case" href="/{p['slug']}/#trend"><span class="corner" aria-hidden="true"></span><div class="spot-body"><span class="num">{p['n']} · {e(MODULES[p['slug']]['role'])} · {e(t['theme'])}</span><h3>{e(t['title'])}</h3>
<div class="spark" data-spark="{c['spark']}"{f' data-mark="{c["mark"]}"' if c.get('mark') else ''} aria-hidden="true"></div>
<dl><dt>What</dt><dd>{e(c['what'])}</dd><dt>Where</dt><dd>{e(c['where'])}</dd><dt>How much</dt><dd>{e(c['how'])}</dd><dt>Significant?</dt><dd class="{'yes' if ok else 'no'}">{e(sigt)}</dd></dl>
<span class="go">Open the case &rarr;</span></div></a>"""
    gloss = "".join(f'<div class="spot"><div class="spot-body"><span class="eyebrow">0{i+1}</span><h3>{e(a)}</h3><p>{e(b)}</p></div></div>' for i, (a, b) in enumerate(GLOSSARY))
    seen, drows = set(), ""
    for p in PROJECTS:
        for a, b, u in p["data"] + TRENDS[p["slug"]]["data"]:
            if a in seen or "basemap" in a: continue
            seen.add(a); drows += f'<tr><td><a href="{u}">{e(a)}</a></td><td>{e(MODULES[p["slug"]]["role"])}</td><td>{e(b)}</td>{login_cell(a)}</tr>'
    methods = [("Detect", "Empirical-Bayes per-cell VIIRS/MODIS ratio, corrected by LightGBM; conformal intervals at a 90% target; robust z-score flags (|z| > 3.5); MODIS MCD64A1 burned area as a second, area-based record."),
               ("Confirm", "Sentinel-1 RTC stacks per orbit; U-Net trained on Sen1Floods11 (14 Optuna trials) against Otsu and a global threshold; OPERA DSWx-S1 water counted outside usual water."),
               ("Adapt", "LightGBM next-season crop model on CDL history plus NASADEM, POWER, NDVI and SoilGrids; FAO-56 water demand; NSGA-II search over four-year rotations; HLS 30 m NDVI and SMAP soil moisture for field-level context."),
               ("Measure", "One value per year; Mann-Kendall (two-sided, α = 0.05) and Sen's slope with a 95% CI; Hamed-Rao autocorrelation check; a second series wherever one exists (GRACE/GRACE-FO water storage, GPM IMERG rainfall, GLDAS and SMAP soil moisture).")]
    meth = "".join(f'<li><p><b style="color:var(--ink);font-weight:500">{e(a)}.</b> {e(b)}</p></li>' for a, b in methods)
    crit = "".join(f'<div class="spot crit"><div class="spot-body"><span class="tag">0{i+1}</span><h3>{e(c)}</h3><p>{e(d)}</p></div></div>' for i, (c, d) in enumerate(CRITERIA))
    return head(SITE["title"], SITE["desc"], "/") + nav("/") + f"""<main id="content">
<section class="hero"><div class="topo-hero" aria-hidden="true"></div><div class="wrap hero-copy">
<p class="chip"><i></i>NASA Space Apps 2026 · {e(SITE['challenge'])}</p>
<h1>Orbit to <span class="grad">Ground</span></h1>
<p class="lede">{e(SITE['tagline'])} Three working modules turn NASA satellite data into decisions: detect, confirm, adapt. Each one answers what is changing, where, how much, and whether it's significant.</p>
<div class="actions"><a class="btn" href="#what">See the system &darr;</a><a class="btn ghost" href="#demo-video">&#9654; Demo video</a><a class="btn ghost" href="/submission/deck.pdf">Slides (PDF)</a></div>
<ul class="proof">
<li><a href="/hotspots/"><span class="src">01 · Detect</span><strong class="grad" data-count="11616131" data-dec="0">11,616,131</strong><span class="t">NASA FIRMS fire detections behind the model, Canada and Argentina, 2000–2025</span></a></li>
<li><a href="/sar-change/"><span class="src">02 · Confirm</span><strong class="grad" data-count="3.0" data-dec="1" data-suffix="×">3.0×</strong><span class="t">the water overlap of the standard Otsu threshold, through cloud and night</span></a></li>
<li><a href="/field-shift/"><span class="src">03 · Adapt</span><strong class="grad" data-count="36" data-dec="0">36</strong><span class="t">non-dominated four-year rotation plans, ranked by the farmer's priorities</span></a></li>
</ul></div></section>

<section class="block" id="demo-video" style="padding-top:0"><div class="wrap">
<figure class="spot video-card" data-fx="rise"><span class="beam" aria-hidden="true"></span>
<video controls preload="metadata" playsinline src="/submission/demo.mp4"><track kind="captions" srclang="en" label="English" src="/submission/demo.en.vtt" /></video>
<figcaption><span class="mono">Demo · under 30 s</span> The three modules and the trend layer in one pass. <a href="/submission/demo.mp4">Download MP4</a> · <a href="/submission/demo.en.srt">Captions</a> · <a href="/submission/deck.pdf">Slides (PDF)</a></figcaption></figure>
</div></section>

<section class="section" id="why"><div class="wrap">
<div class="part-mark" data-fx="rise"><b>Why</b><span>01 · The problem</span></div>
<div class="split-head" data-fx="rise"><div><h2>Change is fast. The evidence is split.</h2></div><p>Three recent events, each seen from orbit, each with a decision that came too late or without the full record.</p></div>
<ul class="tier-list tier-list-lg tier-list-3" data-fx="stagger">{stakes}</ul>
<p class="problem-line" data-fx="rise">{e(SYSTEM_PROBLEM)}</p>
</div></section>

<div class="topo-rule" aria-hidden="true"></div>

<div id="what"></div>
<section class="engine" data-engine aria-labelledby="engine-heading">
<div class="engine-sticky wrap">
<div class="engine-copy"><p class="eyebrow">What · 02 · The system</p><h2 id="engine-heading">Three modules, one pipeline.</h2><ol class="engine-steps">{steps}</ol>
<div class="engine-cta"><a class="btn" href="#modules">Meet the modules</a><a class="btn ghost" href="#trends">The trend layer</a></div></div>
<div class="engine-stage" aria-live="polite">{stage}<p class="engine-hud mono">01 · Detect</p></div>
</div>
<div class="engine-list wrap"><p class="eyebrow">What · 02 · The system</p><h2>Three modules, one pipeline.</h2>{elist}</div>
</section>

<section class="section" id="modules" style="padding-top:2rem"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">What · the modules</p><h2>Each module is a full, working tool.</h2></div><p>Open any module for its live demo, results, figures and data. Every tool runs in your browser from precomputed NASA data.</p></div>
<div class="mod-list">{mods}</div></div></section>

<section class="section trend-sec" id="trends"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">What · the connective tissue</p><h2>Four questions in every module.</h2></div><p>The <a href="{SITE['challenge_url']}" style="color:var(--accent)">Trend Detective</a> layer: pick a variable, get the NASA record, plot it and test whether the change is real.</p></div>
<div class="case-grid" data-fx="stagger">{cases}</div>
<div class="glossary" style="margin-top:2rem" data-fx="stagger">{gloss}</div>
</div></section>

<div class="topo-rule" aria-hidden="true"></div>

<section class="section" id="how"><div class="wrap">
<div class="part-mark" data-fx="rise"><b>How</b><span>03 · Data, methods, validation</span></div>
<div class="split-head" data-fx="rise"><div><h2>Built on NASA data. Tested before trusted.</h2></div><p>Every number comes from our own runs on the public datasets below. Model metrics are one seed each, not a published benchmark.</p></div>
<div class="table-wrap" data-fx="rise"><table><thead><tr><th>Dataset</th><th>Module</th><th>How it's used</th><th>Access</th></tr></thead><tbody>{drows}</tbody></table></div>
<div class="two" style="margin-top:3rem">
<div data-fx="rise"><p class="eyebrow">Methods</p><ol class="facts">{meth}</ol></div>
<div data-fx="rise"><p class="eyebrow">Validation and limits</p>
<div class="honesty" style="grid-template-columns:1fr;margin-top:0">
<div><p class="mono">What holds up</p><p>Models are trained on earlier years and tested on later ones (fire 2022–2025, crops 2024–2025) and beat simple baselines. Trends are tested on a second series where one exists.</p></div>
<div><p class="mono">Where it falls short</p><p>Canada's monthly-total fire error is worse than the baseline (39.4% vs 16.7%). Province fire trends hold on the harmonized record but not MODIS alone, so we call them tentative. Trends show change, not cause. Where a second record disagrees, we say so: GPM IMERG satellite rainfall doesn't confirm the reanalysis drop in southern Ontario's rain extremes, so that claim is dropped.</p></div>
</div></div></div>
</div></section>

<section class="section" id="judging"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">For the judges</p><h2>Scored on five criteria.</h2></div><p>One submission to {e(SITE['challenge'])}, team {e(SITE['team'])}. Each module page maps its work to the <a href="https://www.spaceappschallenge.org/resources/judging-awards-guide/" style="color:var(--accent)">2026 criteria</a>.</p></div>
<div class="grid g5" data-fx="stagger">{crit}</div>
</div></section>
</main>
""" + FOOT

# ---------- opera chart (static SVG) ----------
def opera_svg():
    f = ROOT / "upgrades" / "out" / "opera_valencia.json"
    if not f.exists(): return ""
    d = json.loads(f.read_text()); rows = []
    for r in d["series"]:
        if r["valid_frac"] < 0.8: continue
        k = r["acq"][:8]
        if rows and rows[-1]["acq"][:8] == k: continue
        rows.append(r)
    W, H, m = 960, 330, 40; mt = 58; mx = max(r["new_water_km2"] for r in rows) * 1.15; bw = (W - 2 * m) / len(rows)
    bars = ""
    for gv in (20, 40, 60, 80):
        if gv > mx: break
        gy = H - m - (H - m - mt) * gv / mx
        bars += f'<line x1="{m}" x2="{W-m}" y1="{gy:.1f}" y2="{gy:.1f}" stroke="rgba(255,255,255,.08)" /><text x="{m-6}" y="{gy+4:.1f}" text-anchor="end">{gv}</text>'
    for i, r in enumerate(rows):
        h = (H - m - mt) * r["new_water_km2"] / mx; x = m + i * bw
        post = r["acq"] >= "20241029"
        bars += f'<rect class="bar{" post" if post else ""}" x="{x+2:.1f}" y="{H-m-h:.1f}" width="{bw-4:.1f}" height="{h:.1f}" rx="3"><title>{r["acq"][:4]}-{r["acq"][4:6]}-{r["acq"][6:8]} {r["orbit"]}: {r["new_water_km2"]} km²</title></rect>'
        if r["new_water_km2"] == max(x["new_water_km2"] for x in rows): bars += f'<text class="val" x="{x+bw/2:.1f}" y="{H-m-h-10:.1f}" text-anchor="start">{r["new_water_km2"]:.1f} km²</text>'
        if i % 3 == 0: bars += f'<text x="{x+bw/2:.1f}" y="{H-m+16}" text-anchor="middle">{int(r["acq"][6:8])} {"Oct" if r["acq"][4:6]=="10" else "Nov"}</text>'
    fx = m + next(i for i, r in enumerate(rows) if r["acq"] >= "20241029") * bw
    return (f'<svg class="opera-chart" viewBox="0 0 {W} {H}" role="img" aria-label="New surface water outside usual water, km², per OPERA DSWx-S1 pass, October to November 2024">'
            f'<line x1="{fx-1:.1f}" x2="{fx-1:.1f}" y1="{mt-30}" y2="{H-m}" stroke="#d4c4ff" stroke-dasharray="3 4" /><text x="{fx-8:.1f}" y="{mt-18}" text-anchor="end">29 Oct flood</text>{bars}'
            "</svg>")

# ---------- project pages ----------
def project(i, p):
    prev_p, next_p = PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
    M = MODULES[p["slug"]]; T = TRENDS[p["slug"]]; U = UPGRADES.get(p["slug"])
    probs = "".join(f"<p>{e(t)}</p>" for t in p["problem"])
    steps = "".join(f'<li data-n="{j+1:02d}"><h3>{e(a)}</h3><p>{e(b)}</p></li>' for j, (a, b) in enumerate(p["steps"]))
    kpis = "".join(kpi_html(k) for k in p["kpis"])
    data = "".join(f'<tr><td>{e(a)}</td><td>{e(b)}</td>{login_cell(a)}<td><a href="{u}">source</a></td></tr>' for a, b, u in p["data"] + T["data"])
    figs = "".join(f'<figure class="fig {c}" data-fx="rise"><img src="/assets/img/{f}" alt="{e(cap)}" loading="lazy" /><figcaption>{e(cap)}</figcaption></figure>' for f, cap, c in p["figs"])
    crit = "".join(f'<div class="spot crit"><div class="spot-body"><span class="tag">{e(c)}</span><p style="color:var(--ink);margin-top:.5rem">{e(p["criteria"][c])}</p></div></div>' for c, _ in CRITERIA)
    limits = "".join(f"<li>{e(l)}</li>" for l in p["limits"])
    deliv = "".join(f"<li>{e(d)}</li>" for d in M["delivers"])
    finds = "".join(f"<li><b>{e(a)}</b> {e(b)}</li>" for a, b in T["findings"])
    def slider(b, a, lb, la, cap, ratio="996 / 1024", title="The flood, through the clouds", eyebrow="Before and after"):
        return f"""<section class="block"><div class="wrap"><div class="sec-head" data-fx="rise"><p class="eyebrow">{e(eyebrow)}</p><h2>{e(title)}</h2></div>
<figure data-fx="rise" style="max-width:820px;margin:0 auto"><div class="ba" style="aspect-ratio:{ratio}"><img src="/assets/img/{b}" alt="Before: {e(lb)}" /><img class="after" src="/assets/img/{a}" alt="After: {e(la)}" />
<span class="lab l">{e(lb)}</span><span class="lab r">{e(la)}</span><span class="handle" aria-hidden="true"></span>
<input type="range" min="0" max="100" value="50" aria-label="Compare before and after" /></div><figcaption style="text-align:center">{e(cap)}</figcaption></figure></div></section>"""
    ba = slider(*p["ba"]) if p.get("ba") else ""
    up = ""
    if U and U.get("ba"):
        chart = opera_svg() if U.get("series") == "opera" else ""
        up = (slider(*U["ba"], ratio="1200 / 979", title=U["title"], eyebrow="Earthdata upgrade · NASA OPERA") +
              f'<section class="block" style="padding-top:0"><div class="wrap"><div class="prose" data-fx="rise" style="max-width:820px"><p>{e(U["text"])}</p><p style="color:var(--faint)">{e(U["note"])}</p></div><figure class="opera-fig" data-fx="rise"><p class="eyebrow" style="margin:0 0 .5rem">New water outside usual water, km² · OPERA DSWx-S1, 30 m</p>{chart}<figcaption>Each bar is one radar pass with at least 80% valid pixels. Hover or tap a bar for its date and area.</figcaption></figure></div></section>')
    elif U:
        uf = "".join(f'<figure class="fig {c}" data-fx="rise"><img src="/assets/img/{f}" alt="{e(cap)}" loading="lazy" /><figcaption>{e(cap)}</figcaption></figure>' for f, cap, c in U["figs"])
        up = f"""<section class="block"><div class="wrap"><div class="sec-head" data-fx="rise"><p class="eyebrow">{e(U['eyebrow'])}</p><h2>{e(U['title'])}</h2></div>
<div class="prose" data-fx="rise" style="max-width:820px"><p>{e(U['text'])}</p><p style="color:var(--faint)">{e(U['note'])}</p></div><div class="figs" style="margin-top:1.5rem">{uf}</div></div></section>"""
    title = f"{p['name']} · Orbit to Ground"
    return head(title, p["tagline"], f"/{p['slug']}/", p["card_img"].replace(".webp", "-og.png")) + nav(f"/{p['slug']}/") + f"""<main id="content">
<section class="hero short"><div class="topo-hero" aria-hidden="true"></div><div class="wrap hero-copy">
<p class="chip"><i></i>Module {p['n']} · {e(M['role'])} · {e(SITE['challenge'])}</p>
<h1>{e(p['name'])}</h1>
<p class="lede">{e(p['tagline'])}</p>
<div class="actions"><a class="btn" href="#demo">Try the live tool &darr;</a><a class="btn ghost" href="#trend">See the trend</a><a class="btn ghost" href="/{p['slug']}/app/">Open full screen</a></div>
</div></section>

<section class="block" id="demo" style="padding-top:1rem"><div class="wrap">
<div class="demo-frame" data-fx="rise"><div class="demo-bar"><i></i><i></i><i></i><span>{e(SITE_URL.replace('https://',''))}/{p['slug']}/app/</span><a href="/{p['slug']}/app/">Full screen &nearr;</a></div>
<iframe src="/{p['slug']}/app/" title="{e(p['name'])} live demo" loading="lazy" allow="fullscreen"></iframe></div>
<p class="demo-note">Interactive and fully static: everything runs in your browser from precomputed data. Use the "Experiment briefing" button inside the tool for a guided walkthrough.</p>
</div></section>

<section class="section" id="why"><div class="wrap">
<div class="part-mark" data-fx="rise"><b>Why</b><span>The problem this module solves</span></div>
<div class="two"><div data-fx="rise"><p class="problem-line" style="margin-top:0">{e(M['statement'])}</p></div>
<div class="prose" data-fx="rise">{probs}</div></div>
</div></section>

<div class="topo-rule" aria-hidden="true"></div>

<section class="section" style="padding-bottom:2rem"><div class="wrap">
<div class="part-mark" data-fx="rise"><b>What</b><span>{e(M['verb'])}</span></div>
<div class="split-head" data-fx="rise"><div><h2>What the module delivers.</h2></div><ul class="findings" style="margin:0">{deliv}</ul></div>
<div class="kpis k3" data-fx="stagger">{kpis}</div>
<p class="demo-note">Held-out test data, compared against baselines. One seed per run, not a published benchmark.</p>
</div></section>
{ba}
<section class="block"><div class="wrap"><div class="sec-head" data-fx="rise"><p class="eyebrow">Visuals</p><h2>Inside the tool</h2></div><div class="figs">{figs}</div></div></section>
{up}
<section class="block trend-sec" id="trend"><div class="wrap">
<div class="sec-head" data-fx="rise"><p class="eyebrow">Trend layer · {e(T['theme'])}</p><h2>{e(T['title'])}</h2><p>{e(T['intro'])}</p></div>
<div class="tw" data-trend="{T['widget']}" data-fx="rise"><noscript><p class="map-cap">The interactive trend chart needs JavaScript. The findings are listed below.</p></noscript></div>
<ul class="findings" data-fx="rise">{finds}</ul>
<p class="demo-note">Mann-Kendall (α = 0.05) and Sen's slope with 95% CI, one value per year. Hover or tap the chart for yearly values.</p>
</div></section>

<div class="topo-rule" aria-hidden="true"></div>

<section class="section"><div class="wrap">
<div class="part-mark" data-fx="rise"><b>How</b><span>Approach, data and limits</span></div>
<div class="two"><div data-fx="rise"><p class="eyebrow">The approach</p><ol class="steps"><span class="bar" aria-hidden="true"></span>{steps}</ol></div>
<div data-fx="rise"><p class="eyebrow">Limits we know about</p><div class="callout"><ul style="margin:0;padding-left:1.1rem">{limits}</ul></div></div></div>
<div class="table-wrap" style="margin-top:2.5rem" data-fx="rise"><table><thead><tr><th>Dataset</th><th>How it's used</th><th>Access</th><th>Link</th></tr></thead><tbody>{data}</tbody></table></div>
</div></section>

<section class="block"><div class="wrap">
<div class="sec-head" data-fx="rise"><p class="eyebrow">For the judges</p><h2>How it maps to the criteria</h2></div>
<div class="grid g5" data-fx="stagger">{crit}</div>
<p class="demo-note">First designed around the related Space Apps 2026 brief <a href="{p['challenge_url']}" style="color:var(--accent)">{e(p['challenge'])}</a>; here it is the {e(M['role']).lower()} module of one system in {e(SITE['challenge'])}</p>
</div></section>

<section class="block"><div class="wrap pager">
<a class="spot" href="/{prev_p['slug']}/"><div class="spot-body"><small>&larr; Module {prev_p['n']}</small><b>{e(prev_p['name'])}</b></div></a>
<a class="spot" href="/{next_p['slug']}/" style="text-align:right"><div class="spot-body"><small>Module {next_p['n']} &rarr;</small><b>{e(next_p['name'])}</b></div></a>
</div></section>
</main>
""" + FOOT

def _is_trend(d): return isinstance(d, dict) and "series" in d and "x" in d and "p" in d
def _first_trend(d, prefer=()):
    if _is_trend(d): return d
    if isinstance(d, dict):
        for k in prefer:
            if _is_trend(d.get(k)): return d[k]
        for v in d.values():
            t = _first_trend(v, prefer)
            if t: return t
    return None

def merge_earthdata():
    """Merge Earthdata-worker outputs into the site data file (normalized for trends.js)."""
    f = DIST / "assets/data/trends.json"; D = json.loads(f.read_text())
    ed = dict(D.get("earthdata") or {})
    srcs = []
    for g in (ROOT / "trends/out/trends.json", ROOT / "trends/out/earthdata_trends.json"):
        if g.exists():
            x = json.loads(g.read_text()); srcs.append(x.get("earthdata", x) if "earthdata" in x else x)
    for x in srcs:
        for reg, v in (x.get("grace") or {}).items():
            if _is_trend(v): ed.setdefault("grace", {})[reg] = v
        im = x.get("imerg") or {}
        for reg, v in im.items():
            t = _first_trend(v, ("annual_total",))
            if t: ed.setdefault("imerg", {})[reg] = t
        gl = x.get("gldas") or x.get("gldas_iowa") or {}
        t = _first_trend(gl, ("RootMoist_inst", "root", "rootzone", "central_iowa"))
        if t: ed.setdefault("gldas", {})["RootMoist_inst"] = t
    D["earthdata"] = ed; f.write_text(json.dumps(D, separators=(",", ":")))
    return {k: list(v.keys()) for k, v in ed.items() if isinstance(v, dict)}

def main():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copytree(SRC / "assets", DIST / "assets")
    print("earthdata:", merge_earthdata())
    (DIST / "index.html").write_text(landing())
    for i, p in enumerate(PROJECTS):
        copy_demo(p["slug"])
        (DIST / p["slug"] / "index.html").write_text(project(i, p))
    (DIST / "404.html").write_text(head("Not found · Orbit to Ground", SITE["desc"], "/404") + nav("") +
        '<main id="content"><section class="hero short"><div class="wrap hero-copy"><h1>Page not found</h1><p class="lede">That page doesn\'t exist.</p><div class="actions"><a class="btn" href="/">Back to the projects</a></div></div></section></main>' + FOOT)
    shutil.copy(SRC / "assets/img/favicon.ico", DIST / "favicon.ico")
    sub = DIST / "submission"; sub.mkdir(exist_ok=True)
    for fn in ("demo.mp4", "demo.en.srt", "deck.pdf"):
        if (ROOT / "submission" / fn).exists(): shutil.copy(ROOT / "submission" / fn, sub / fn)
        else: print("WARNING: missing submission/" + fn)
    if (sub / "demo.en.srt").exists():
        import re as _re
        (sub / "demo.en.vtt").write_text("WEBVTT\n\n" + _re.sub(r"(\d\d:\d\d:\d\d),(\d\d\d)", r"\1.\2", (sub / "demo.en.srt").read_text()))
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    urls = ["/"] + [f"/{p['slug']}/" for p in PROJECTS] + [f"/{p['slug']}/app/" for p in PROJECTS]
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls) + "</urlset>\n")
    (DIST / "_headers").write_text("/assets/*\n  Cache-Control: public, max-age=3600\n/submission/*.srt\n  Content-Type: text/plain; charset=utf-8\n/submission/*.vtt\n  Content-Type: text/vtt; charset=utf-8\n/submission/*\n  Cache-Control: public, max-age=600\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    n = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"built {DIST} ({n} files)")

if __name__ == "__main__":
    main()
