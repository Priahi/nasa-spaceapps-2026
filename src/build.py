#!/usr/bin/env python3
"""Build the combined static site into ../dist.
   - copies the three static demo builds into /<slug>/app/ and applies the suite theme + back-links
   - renders the landing page and one story page per project from content.py
Usage: python3 src/build.py [--demos /path/to/nasa-spaceapps/deploy]"""
import html, json, re, shutil, sys
from pathlib import Path
from story import maps_block
from recs import APPS, PEOPLE_NOTE, rec_card, recs_block, impact_block, guide_data, app_data, BA, ba_html, metrics_strip
from content import SITE, PROJECTS, CRITERIA, TRENDS, GLOSSARY, STAKES, SYSTEM_PROBLEM, MODULES, UPGRADES

ROOT = Path(__file__).resolve().parent.parent
SRC, DIST = ROOT / "src", ROOT / "dist"
DEMOS = Path(sys.argv[sys.argv.index("--demos") + 1]) if "--demos" in sys.argv else ROOT / "demos"
SITE_URL = "https://nasa-spaceapps-2026.pages.dev"
import os
REPO_URL = "https://github.com/Priahi/nasa-spaceapps-2026"
SLIDES = []
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
    (out / "og-data.js").write_text("window.OG_SLUG=" + json.dumps(slug) + ";window.OG_APP=" + json.dumps(app_data(slug), ensure_ascii=False) + ";" + ("window.OG_IMPACT=true;" if (ROOT / "submission" / "impact.json").exists() else ""))
    idx = out / "index.html"; h = idx.read_text()
    h = re.sub(r'\s*<meta name="robots"[^>]*>', "", h)
    h = re.sub(r'(href|src)="/(?!/)', r'\1="', h)  # root-absolute assets -> relative (demo now lives under /<slug>/app/)
    h = h.replace("</head>", '  <link rel="stylesheet" href="suite-common.css" />\n  <link rel="stylesheet" href="suite-theme.css" />\n  <link rel="stylesheet" href="/shared/tokens.css" />\n  <link rel="stylesheet" href="/shared/c2.css" />\n  <link rel="stylesheet" href="/shared/shell.css" />\n  <script src="og-data.js"></script>\n  <script src="/shared/shell.js"></script>\n  <script src="/shared/c2.js"></script>\n  <script src="/shared/whatif.js" defer></script>\n</head>', 1)
    h = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + suite_bar(slug), h, count=1)
    # public-build wording (was written for the private preview)
    h = h.replace("NASA Space Apps 2026 · unlisted demo · not submitted", "NASA Space Apps 2026")
    h = h.replace("Unlisted demo build (static, precomputed from the local model run).", "Static build, precomputed from the model run.")
    h = h.replace("Unlisted demo, not submitted, not a published benchmark.", "One seed, not a published benchmark.")
    h = h.replace("Local demo for NASA International Space Apps Challenge 2026", "NASA International Space Apps Challenge 2026")
    h = h.replace("Cite every source in a Space Apps submission and disclose this pre-existing tooling. This is a local demo, not a submitted project and not a published benchmark.",
                  "All sources are cited above. Builds on our earlier code and open-source libraries. One seed, not a published benchmark.")
    h = h.replace("Cite every source in a Space Apps submission and disclose this pre-existing tooling.", "Builds on our earlier code and open-source libraries.")
    h = re.sub(r"<title>(.*?)</title>", lambda m: f"<title>{m.group(1)} · Parsa Riahi</title>\n  <meta name=\"author\" content=\"Parsa Riahi\" />", h, count=1)
    h = re.sub(r"(<footer[^>]*>)", lambda m: m.group(1) + f'<p class="og-credit">{html.escape(SITE["credit"])}.</p>', h, count=1)
    idx.write_text(h)
    for f in list(out.glob("*.js")) + list(out.glob("*.css")) + [idx]:
        if f.name.startswith("suite-"): continue
        t = f.read_text(); t2 = t.replace(" local demo.", " demo.")
        for a, b in RECOLOR.items(): t2 = re.sub(a, b, t2, flags=re.I)
        if slug == "field-shift": t2 = re.sub("#c4922c", "#6d28d9", t2, flags=re.I)
        if t2 != t: f.write_text(t2)

# ---------- page chrome ----------
def head(title, desc, path, img="og.png"):
    if SITE["author"] not in title: title = f"{title} · {SITE['author']}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}" />
<meta name="author" content="{e(SITE['author'])}" />
<meta property="og:site_name" content="Orbit to Ground · {e(SITE['credit'])}" />
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
<link rel="stylesheet" href="/shared/tokens.css" />
<link rel="stylesheet" href="/assets/css/site.css" />
<link rel="stylesheet" href="/assets/css/system.css" />
<link rel="stylesheet" href="/shared/c2.css" />
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
"""

def nav(active):
    items = [("/#night", "The night"), ("/#rewind", "Rewind"), ("/#fire", "Fire"), ("/#more", "Sectors")] + [(f"/{p['slug']}/", APPS[p["slug"]]["name"]) for p in PROJECTS] + [("/slides/", "Slides"), ("/#how", "Under the hood")]
    li = "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if h==active else ""}>{e(t)}</a></li>' for h, t in items)
    mi = "".join(f'<a href="{h}">{e(t)}</a>' for h, t in items)
    return f"""<header class="nav"><a class="brand" href="/"><span class="brand-dot" aria-hidden="true"></span>Orbit to Ground</a>
<nav aria-label="Main"><ul class="nav-links">{li}</ul></nav>
<button class="menu-btn" aria-expanded="false" aria-controls="menu">Menu</button></header>
<div class="menu" id="menu">{mi}</div>
"""

REPO_NOTE = f' Source code: <a href="{REPO_URL}">{REPO_URL.replace("https://","")}</a> (Apache-2.0).' if SHOW_REPO else " Code licence: Apache-2.0."
FOOT = f"""<footer class="site"><div class="wrap">
<p><strong>Orbit to Ground</strong> · NASA International Space Apps Challenge 2026 · {e(SITE['challenge'])} · {e(SITE['credit'])}.{REPO_NOTE}</p>
<p>Data: NASA FIRMS, NASA-ISRO NISAR (via NASA CMR and ASF DAAC), NASA POWER, NASADEM, MODIS, plus ESA Copernicus Sentinel-1, Sen1Floods11, USDA NASS CDL and ISRIC SoilGrids. Province outlines: Natural Earth (public domain). Each project page lists its sources and licences. This site is not affiliated with or endorsed by NASA.</p>
<p>AI disclosure: AI coding assistants helped write and refactor parts of the code, site and text. All models, metrics and figures come from our own runs on the public data listed. Photos of people are AI-generated illustrations, not real people or events; every chart, map and number comes from data. Model metrics are one seed each, not a published benchmark. {e(SITE['built_on'])}</p>
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

# ---------- pages ----------
def shows_visual(key):
    v = _shows_visual(key)
    if key in ("mcd64_bars", "canada_line", "calendar"): return f'<div class="fire">{v}</div>'
    if key in ("opera_bars", "grace_line"): return f'<div class="water">{v}</div>'
    if key in ("frost_line",): return f'<div class="crop">{v}</div>'
    return v

def _shows_visual(key):
    if key == "heat_map":
        return ('<figure class="heat-fig"><img src="/assets/img/canada-fire-heat.webp" alt="Map of Canada: fire detections per 0.25° cell, 2003–2025 average. Brightest across the N.W.T., B.C., Saskatchewan and Alberta." width="1799" height="1223" loading="lazy" />'
                '<div class="heat-leg"><b>Fire detections per year, per 0.25° cell (≈ 28 km)</b><i></i><span class="ticks"><span>1</span><span>10</span><span>100</span><span>440</span></span></div>'
                '<figcaption>NASA FIRMS, harmonized to the VIIRS scale, 2003–2025 average · province outlines Natural Earth.</figcaption></figure>')
    from story import T, ED, MCD, OPERA, line_chart, bar_chart, img as simg, slider as sslider, _opera_bars, matrix, fmt
    if key == "mcd64_bars":
        t = MCD["trend"]; return bar_chart(t["x"], t["series"], "km²", "Burned area per Apr–Oct season, km² · NASA MODIS MCD64A1", hl=2023)
    if key == "canada_line":
        m = T["fire"]["canada"]["Canada"]["modis_count"]
        return line_chart(m["x"], m["series"], m["sen_slope_per_year"], "detections", "Fire detections per year, Canada · NASA FIRMS MODIS", ci=m["sen_ci95"], note=f"+{fmt(m['sen_slope_per_year'])}/yr · p = {m['p']:.3f}")
    if key == "calendar":
        return simg("hotspots-calendar.webp", "Alberta fire calendar, 2000–2025. Outlined squares are unusual months.")
    if key == "opera_slider":
        return sslider("opera-before.webp", "opera-after.webp", "26 Oct 2024", "31 Oct 2024")
    if key == "opera_bars":
        return _opera_bars([r for r in OPERA.get("series", []) if r["valid_frac"] >= 0.8])
    if key == "grace_line":
        g = ED["grace"]["valencia"]
        return line_chart(g["x"], g["series"], g["sen_slope_per_year"], "cm", "Stored water, eastern Spain, cm · NASA GRACE/GRACE-FO", dec=1, mark=2017, ci=g["sen_ci95"], note=f"{fmt(g['sen_slope_per_year'], 2)} cm/yr · p = {g['p']:.3f}")
    if key == "frost_line":
        ff = T["crops"]["frost_free_days"]["region"]
        return line_chart(ff["x"], ff["series"], ff["sen_slope_per_year"], "days", "Frost-free days per year, central Iowa · NASA POWER", ci=ff["sen_ci95"], note=f"+{ff['sen_slope_per_year']:.2f} d/yr · p = {ff['p']:.3f}")
    if key == "water_matrix":
        return matrix(only=[5])
    if key == "hls":
        return simg("hls-ndvi.webp", "NASA HLS 30 m greenness: 1 Aug 2024, 31 Jul 2025 and the change.", "light")
    return ""

def person_fig(src, alt, cls=""):
    return f'<figure class="person {cls}"><img src="/assets/img/{src}" alt="{e(alt)}" width="1280" height="720" /></figure>'

def step_head(n, kicker, title):
    return f'<div class="step-head" data-fx="rise"><span class="step-n">{n}</span><p class="eyebrow">{e(kicker)}</p>{f"<h2>{e(title)}</h2>" if title else ""}</div>'

def home_impact():
    out = ""
    def li(xs): return "".join(f"<li>{e(x)}</li>" for x in xs)
    for sl in ("hotspots", "sar-change", "field-shift"):
        A = APPS[sl]; it = BA[sl][0]
        out += (f'<article class="c2-imp"><header><span class="c2-cls">{e(A["name"])} · {e(it["user"])}</span><h3>{e(it["decision"])}</h3></header>'
                f'<div class="c2-ba"><div class="c2-b"><p>Before</p><ul>{li(it["before"])}</ul></div><span class="c2-arrow" aria-hidden="true">→</span>'
                f'<div class="c2-a"><p>With this tool</p><ul>{li(it["after"])}</ul></div></div>'
                f'<footer><div><b>{e(it["geo"]["v"])}</b><span>{e(it["geo"]["l"])}</span></div><div><b>{e(it["metric"]["v"])}</b><span>{e(it["metric"]["l"])}</span></div></footer>'
                f'<a class="more" href="/{sl}/#impact">More for {e(A["name"])} &rarr;</a></article>')
    return f'<div class="c2-impact home-imp" data-fx="rise"><div class="c2-imp-grid three">{out}</div></div>'

def cases_scrolly():
    """Sticky chart + steps: each case swaps the chart (scroll or tabs). On narrow screens each step carries its own chart."""
    from story import T as _T, ED as _ED, MCD as _MCD, line_chart as _lc, bar_chart as _bc, _opera_bars, OPERA as _OP, fmt as _fmt
    t = _MCD["trend"]; g = _ED["grace"]["valencia"]; ff = _T["crops"]["frost_free_days"]["region"]
    C = [("fire", "Fire · Canada", "+272 km²/yr", "More burned ground every year in the boreal tile (NE B.C., Alberta, Sask.), 2003–2025. p = 0.004.", "/hotspots/",
          '<div class="fire">' + _bc(t["x"], t["series"], "km²", "Burned area per Apr–Oct season, km² · NASA MODIS MCD64A1", hl=2023) + "</div>"),
         ("flood", "Flood · Valencia", "77.7 km²", "New surface water two days after the October 2024 storm, up from 30.7 km², mapped by radar through cloud.", "/sar-change/",
          '<div class="water">' + _opera_bars([r for r in _OP.get("series", []) if r["valid_frac"] >= 0.8]) + "</div>"),
         ("season", "Season · Iowa", "+19 days", "Frost-free season about 19 days longer than in 1981 (+0.43 days a year, p = 0.006).", "/field-shift/",
          '<div class="crop">' + _lc(ff["x"], ff["series"], ff["sen_slope_per_year"], "days", "Frost-free days per year, central Iowa · NASA POWER", ci=ff["sen_ci95"], note=f"+{ff['sen_slope_per_year']:.2f} d/yr · p = {ff['p']:.3f}") + "</div>"),
         ("water", "Water · eastern Spain", "−0.39 cm/yr", "Stored water (ground, soil and surface) is falling, measured by gravity satellites since 2002. p = 0.002.", "/sar-change/#trend",
          '<div class="water">' + _lc(g["x"], g["series"], g["sen_slope_per_year"], "cm", "Stored water, eastern Spain, cm · NASA GRACE/GRACE-FO", dec=1, mark=2017, ci=g["sen_ci95"], note=f"{_fmt(g['sen_slope_per_year'], 2)} cm/yr · p = {g['p']:.3f}") + "</div>")]
    tabs = "".join(f'<button type="button" role="tab" data-case="{k}" aria-selected="{str(i == 0).lower()}">{e(lbl.split(" · ")[0])}</button>' for i, (k, lbl, *_r) in enumerate(C))
    panels = "".join(f'<div class="cs-panel beat-media{" on play" if i == 0 else ""}" data-case="{k}" role="tabpanel">{vis}</div>' for i, (k, _l, _b, _t, _h, vis) in enumerate(C))
    steps = "".join(f'<article class="cs-step{" on" if i == 0 else ""}" data-case="{k}"><p class="eyebrow">{e(lbl)}</p><strong class="grad">{e(b)}</strong><p>{e(txt)}</p>'
                    f'<a class="more" href="{h}">See what people do with it &rarr;</a><div class="cs-inline beat-media play">{vis}</div></article>' for i, (k, lbl, b, txt, h, vis) in enumerate(C))
    return f'<div class="cases" data-cases><div class="cs-stage"><div class="cs-tabs" role="tablist" aria-label="Choose a case">{tabs}</div><div class="cs-panels">{panels}</div></div><div class="cs-steps">{steps}</div></div>'

def landing():
    stakes = "".join(f'<li class="stake"><strong class="grad">{e(x["big"])}</strong><p>{e(x["line"])}</p><a href="{x["url"]}">{e(x["src"])}</a></li>' for x in STAKES)
    people = ""
    for s in ("hotspots", "sar-change", "field-shift"):
        A = APPS[s]; src, alt = A["hero"]
        people += (f'<article class="pcard"><a href="/{s}/" class="pcard-img"><img src="/assets/img/{src}" alt="{e(alt)}" width="1280" height="720" /></a>'
                   f'<div class="pcard-body"><p class="eyebrow">{e(A["role"])} · {e(A["who"])}</p><h3>{e(A["headline"])}</h3>'
                   f'<div class="actions"><a class="btn launch" href="/{s}/app/">Launch {e(A["name"])}</a><a class="btn ghost" href="/{s}/">See the actions</a></div></div></article>')
    from story import T as _T, ED as _ED, MCD as _MCD, line_chart as _lc, fmt as _fmt, matrix as _mx, small_multiples as _sm, usecase_map as _um
    heads = [("+272 km²/yr", "more burned ground, boreal Canada", "/hotspots/"), ("77.7 km²", "flood water seen through cloud, Valencia", "/sar-change/"),
             ("+19 days", "longer frost-free season, Iowa", "/field-shift/"), ("−0.39 cm/yr", "stored water lost, eastern Spain", "#trend")]
    hn = "".join(f'<a class="hn" href="{h}"><strong class="grad">{e(b)}</strong><span>{e(l)}</span></a>' for b, l, h in heads)
    g = _ED["grace"]["valencia"]
    gl = _lc(g["x"], g["series"], g["sen_slope_per_year"], "cm", "Stored water, eastern Spain · NASA GRACE/GRACE-FO, cm", dec=1, mark=2017, ci=g["sen_ci95"], note=f"{_fmt(g['sen_slope_per_year'], 2)} cm/yr · p = {g['p']:.3f}")
    acts = ""
    for s in ("hotspots", "sar-change", "field-shift"):
        A = APPS[s]
        acts += (f'<div class="act-app"><div class="act-head"><img src="/assets/img/{A["hero"][0]}" alt="" width="96" height="96" loading="lazy" /><div><p class="eyebrow">{e(A["role"])} · {e(A["name"])}</p><h3>{e(A["who"])}</h3></div>'
                 f'<a class="btn launch" href="/{s}/app/">Launch</a></div>' + '<div class="recs compact">' + "".join(rec_card(r, i, True, s) for i, r in enumerate(A["recs"][:3])) + '</div>'
                 f'<a class="more" href="/{s}/#actions">All {len(A["recs"])} actions for {e(A["name"])} &rarr;</a></div>')
    imp = ""
    for s in ("hotspots", "sar-change", "field-shift"):
        A = APPS[s]; I = A["impact"]
        imp += (f'<div class="imp-row"><a class="imp-app" href="/{s}/#impact">{e(A["name"])}</a><div class="imp tech"><b>{e(A["sum"][0])}</b><span>{e(A["sum"][1])}</span></div>'
                f'<div class="imp-arrow" aria-hidden="true">→</div><div class="imp human"><b>{e(I["human"][1][1])}</b><span>{e(I["human"][0][1])}</span></div></div>')
    mall = '<ul class="mstrip">' + "".join(f'<li class="{m[2] if len(m) > 2 else ""}"><strong>{e(m[0])}</strong><span>{e(A["name"])}: {e(m[1])}</span></li>' for s in ("hotspots", "sar-change", "field-shift") for A in [APPS[s]] for m in A["metrics"][:2]) + "</ul>"
    seen, drows = set(), ""
    for p in PROJECTS:
        for a, b, u in p["data"] + TRENDS[p["slug"]]["data"]:
            if a in seen or "basemap" in a: continue
            seen.add(a); drows += f'<tr><td><a href="{u}">{e(a)}</a></td><td>{e(MODULES[p["slug"]]["role"])}</td><td>{e(b)}</td>{login_cell(a)}</tr>'
    methods = [("Detect", "Per-cell VIIRS/MODIS ratio corrected by LightGBM; conformal 90% intervals; robust z-score flags; MODIS MCD64A1 burned area."),
               ("Confirm", "Sentinel-1 RTC stacks; U-Net trained on Sen1Floods11 vs Otsu and a global threshold; NASA OPERA DSWx-S1 new water."),
               ("Adapt", "LightGBM next-season crop model on CDL + NASADEM, POWER, NDVI, SoilGrids; FAO-56 water; NSGA-II rotations; HLS and SMAP context."),
               ("Measure", "Mann-Kendall (α = 0.05) and Sen's slope with 95% CI, Hamed-Rao check, and a second NASA record wherever one exists.")]
    meth = "".join(f'<li><b>{e(a)}.</b> {e(b)}</li>' for a, b in methods)
    cases = ""
    for p in PROJECTS:
        t = TRENDS[p["slug"]]; c = t["case"]; ok, sigt = c["sig"]
        cases += (f'<a class="spot case" href="/{p["slug"]}/#trend"><div class="spot-body"><span class="num">{e(MODULES[p["slug"]]["role"])} · {e(t["theme"])}</span><h3>{e(t["title"])}</h3>'
                  f'<dl><dt>What</dt><dd>{e(c["what"])}</dd><dt>Where</dt><dd>{e(c["where"])}</dd><dt>How much</dt><dd>{e(c["how"])}</dd><dt>Significant?</dt><dd class="{"yes" if ok else "no"}">{e(sigt)}</dd></dl></div></a>')
    crit = "".join(f'<li><b>{e(c)}</b> {e(d)}</li>' for c, d in CRITERIA)
    from home import home_sections, alert_card, SRC as _HS
    from story import story as _story, slider as _slider
    sar = app_data("sar-change"); al = next(a["alert"] for a in sar["actions"] if a.get("alert"))
    night, rewind = home_sections(_story, _slider, alert_card(al))
    from arch import figures as _arch
    sectors = [("built", "Emergency management", "Flood · Valencia", "77.7 km² of new water mapped through 99% cloud; one drafted alert to 8 towns.", "/sar-change/app/#demo", "Open SAR Change"),
               ("built", "Wildfire services", "Fire · Canada", "7.46 M detections; May flagged as the watch month. Draw any area for its own burn calendar.", "/hotspots/app/#demo", "Open Hot Spots"),
               ("built", "Wildfire services", "Fire · Argentina", "4.15 M detections in the same tool. Here the trend falls: −1,909 a year.", "/hotspots/app/", "Open Hot Spots"),
               ("built", "Water resources", "Groundwater · eastern Spain", "Stored water falling 0.39 cm a year since 2002 (p = 0.002), from gravity satellites.", "/sar-change/#trend", "See the trend"),
               ("future", "Transport", "Landslides after rain", "Rain signal plus slope maps, to close roads before they slide.", "", ""),
               ("future", "Food security", "Drought and crop stress", "Soil water and greenness, to target aid before harvests fail.", "", ""),
               ("future", "Coastal cities", "Storm surge", "Radar water maps for low streets, the way we mapped Valencia.", "", ""),
               ("future", "Schools", "Smoke and air quality", "Fire detections plus wind, to move recess indoors in time.", "", ""),
               ("future", "Care homes", "Heat waves", "Surface heat by block, to send staff where it's hottest.", "", "")]
    def _sc(k, sec, t, d, u, lt):
        tag = "Built · live" if k == "built" else "Future · not built"
        link = f'<a class="more" href="{u}">{e(lt)} &rarr;</a>' if u else ""
        return f'<article class="x20 {k}"><span class="x20-tag mono">{tag}</span><p class="eyebrow">{e(sec)}</p><h3>{e(t)}</h3><p>{e(d)}</p>{link}</article>'
    sec_built = "".join(_sc(*x) for x in sectors if x[0] == "built")
    sec_fut = "".join(_sc(*x) for x in sectors if x[0] == "future")
    field_feat = ('<article class="x20 built eng-feat"><div class="eng-feat-copy"><span class="x20-tag mono">Built · live</span><p class="eyebrow">Agriculture · Iowa</p>'
                  '<h3>Field Shift: what each field grows next</h3><p>Trained on NASA optical, climate and terrain data with USDA crop labels, the model maps next season\'s crop for a whole county: <b>81.8%</b> accurate on a held-out year. A farmer view suggests rye on steep fields, for 67% lower erosion risk. The frost-free season is 19 days longer than in 1981 (p = 0.006).</p>'
                  '<a class="btn launch" href="/field-shift/app/">Open Field Shift</a></div>'
                  '<figure class="eng-map"><img src="/assets/img/field-map.webp" alt="Story County, Iowa, 2025: actual crops (USDA CDL), crops predicted by the model, and where they disagree (30.2% of farmed pixels)." width="1280" height="551" loading="lazy" />'
                  '<figcaption>Crop classification, Story County, Iowa, held-out 2025: actual (USDA CDL), predicted, and disagreement (30.2% of farmed pixels).</figcaption></figure></article>')
    eng_flow = '<ol class="eng-flow mono">' + "".join(f"<li>{x}</li>" for x in ("Satellite signal", "Map", "Drafted alert", "Task")) + "</ol>"
    return head(SITE["title"], SITE["desc"], "/") + nav("/") + f"""<main id="content">
<section class="hero hero-tight hs-hook" id="hook"><div class="topo-hero" aria-hidden="true"></div><div class="wrap hero-copy">
<p class="chip"><i></i>NASA Space Apps 2026 · {e(SITE['challenge'])}</p>
<p class="eyebrow">Valencia, Spain · 29 October 2024</p>
<h1>The red warning came around <span class="grad">7:30 AM</span>.<br/>The phone alert came around <span class="grad">8 PM</span>.</h1>
<p class="lede">About 230 people died in the Valencia region, after a 12-hour gap between warning and alert. This is one night told twice: as it happened, and rewound with NASA satellite data.</p>
<div class="actions"><a class="btn" href="#night">Start the story &darr;</a><a class="btn ghost" href="/sar-change/app/#demo">Open the flood dashboard</a><a class="btn ghost" href="#demo-video">&#9654; Demo video</a></div>
<p class="fine">Sources: <a href="{_HS['aemet'][1]}" rel="noopener">AEMET</a>, <a href="{_HS['elpais'][1]}" rel="noopener">El País</a>. Orbit to Ground turns NASA satellite data into the next move.</p>
</div></section>
{night}
{rewind}
<section class="section tight hs-could"><div class="wrap" data-fx="rise">
<p class="eyebrow">What could have changed</p>
<blockquote>With an upstream rain signal and a radar map, Elena could have had a drafted alert for her town hours before the 8 PM phone alert, and a map of where the water went on day two.</blockquote>
<p class="fine">A rewind, not a claim: alerts and tasking are simulated, and we make no claim about lives saved.</p>
<div class="actions"><a class="btn launch" href="/sar-change/app/#demo">Try the rewind in the flood dashboard</a><a class="btn ghost" href="/sar-change/">The flood project</a></div>
</div></section>

<section class="section tight" id="fire"><div class="wrap hs-fire">
<div class="hs-fire-copy" data-fx="rise"><p class="eyebrow">Second story · Canada, before fire season</p>
<h2>A duty officer staffs up before May, not after.</h2>
<ul class="hs-pts"><li><b>Rising.</b> Fire detections grow about 1,503 a year in Alberta (p = 0.035) and 2,587 in B.C. (p = 0.045), 2003–2025. Tentative: one sensor alone isn't significant.</li>
<li><b>May is the watch month.</b> 5 of Alberta's 16 unusual fire months since 2000 were in May.</li>
<li><b>The move (simulated).</b> Stage initial-attack crews before July, open seasonal hiring this spring, and tell forest communities to check evacuation plans before May.</li></ul>
<p class="fine">7.46 M NASA FIRMS detections over Canada. A 2026 trend line of about 41,000 (Alberta) and 72,000 (B.C.) is a trend line, not a forecast.</p>
<div class="actions"><a class="btn launch" href="/hotspots/app/#demo">Open Hot Spots</a><a class="btn ghost" href="/hotspots/">The fire project</a></div></div>
<div data-fx="rise">{shows_visual("heat_map")}</div>
</div></section>

<section class="section tight" id="more"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">One engine, many sectors</p><h2>Same engine. Every sector.</h2></div><p>Flood and fire run on one loop. Swap the satellite input and the same loop serves farms, water and cities. Built ones are live today; future ones are clearly marked.</p></div>
{eng_flow}
{field_feat}
<div class="x20-grid" data-fx="stagger">{sec_built}</div>
<div class="x20-grid fut" data-fx="stagger">{sec_fut}</div>
</div></section>

<section class="section tight" id="apps"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">Three dashboards</p><h2>Open them. Every number is live data.</h2></div><p>Each one shows the signal, the map and the next move, with alerts and tasking clearly marked as simulated.</p></div>
<div class="pcards">{people}</div></div></section>

<section class="section tight" id="demo-video"><div class="wrap">
<figure class="spot video-card" data-fx="rise"><video controls preload="metadata" playsinline src="/submission/demo.mp4"><track kind="captions" srclang="en" label="English" src="/submission/demo.en.vtt" /></video>
<figcaption><span class="mono">Demo video</span> <a href="/submission/demo.mp4">MP4</a> · <a href="/submission/demo.en.srt">Captions</a> · <a href="/submission/deck.pdf">Slides (PDF)</a></figcaption></figure>
</div></section>
""" + slides_strip(SLIDES) + f"""
<section class="section tight" id="how"><div class="wrap">
<div class="step-head" data-fx="rise"><p class="eyebrow">Under the hood</p><h2>Built on NASA data. Tested before trusted.</h2></div>
<h3 class="af-h">How each model works</h3>
{_arch()}
<p class="mstrip-k">Model accuracy · one seed per run, not a published benchmark</p>{mall}
<details class="deep"><summary>The four trend questions, per module</summary><div class="case-grid">{cases}</div></details>
<details class="deep"><summary>Do independent NASA records agree? · the agreement matrix</summary><div id="trend">{_mx()}</div></details>
<details class="deep"><summary>Compare regions · same test, three places</summary>{_sm()}</details>
<details class="deep"><summary>Data sources ({len(seen)})</summary><div class="table-wrap"><table><thead><tr><th>Dataset</th><th>Module</th><th>How it's used</th><th>Access</th></tr></thead><tbody>{drows}</tbody></table></div></details>
<details class="deep"><summary>Methods</summary><ul class="facts">{meth}</ul></details>
<details class="deep"><summary>Validation and limits</summary><ul class="facts"><li><b>What holds up.</b> Models trained on earlier years, tested on later ones, against simple baselines. Trends checked on a second NASA record where one exists.</li><li><b>Where it falls short.</b> Canada's monthly-total fire error is worse than the baseline (39.4% vs 16.7%). Provincial fire trends are tentative. Trends show change, not cause. GPM IMERG doesn't confirm the reanalysis drop in southern Ontario's rain extremes, so we don't claim it. The flood rewind uses archive data; we haven't tested near-real-time timing.</li></ul></details>
<details class="deep"><summary>Judging criteria</summary><ul class="facts">{crit}</ul></details>
<p class="fine center">{e(SITE['credit'])}</p>
</div></section>
</main>
""" + FOOT

# ---------- per-module hooks (see /PARALLEL.md) ----------
MODDIR = SRC / "modules"
def names_default(): return ["hero", "problem", "satellite", "actions", "impact", "try", "trend", "how", "pager"]
def _modname(slug): return slug.replace("-", "_")
def module_override(slug, secs, A):
    f = MODDIR / slug / "page.py"
    if not f.exists(): return secs
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"mod_{_modname(slug)}", f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.override(slug, dict(secs), A) if hasattr(m, "override") else secs
def module_head(slug):
    return f'<link rel="stylesheet" href="/{slug}/m/page.css" />\n' if (MODDIR / slug / "page.css").exists() else ""
def module_foot(slug):
    return f'<script src="/{slug}/m/page.js" defer></script>\n' if (MODDIR / slug / "page.js").exists() else ""
def copy_module(slug):
    d = MODDIR / slug
    if not d.exists(): return
    out = DIST / slug / "m"; out.mkdir(parents=True, exist_ok=True)
    for f in d.rglob("*"):
        if f.is_file() and f.suffix != ".py" and "__pycache__" not in f.parts:
            t = out / f.relative_to(d); t.parent.mkdir(parents=True, exist_ok=True); shutil.copy(f, t)

def project(i, p):
    prev_p, next_p = PROJECTS[i - 1], PROJECTS[(i + 1) % len(PROJECTS)]
    s = p["slug"]; A = APPS[s]; M = MODULES[s]; T = TRENDS[s]; U = UPGRADES.get(s)
    big, pline, pimg, pcap = A["problem"]
    shows = "".join(f'<div class="show{" flip" if k % 2 else ""}" data-fx="rise"><div class="show-vis beat-media play">{shows_visual(key)}</div>'
                    f'<div class="show-txt"><strong class="grad">{e(b)}</strong><p>{e(l)}</p></div></div>' for k, (b, l, key) in enumerate(A["shows"]))
    kpis = "".join(kpi_html(k) for k in p["kpis"])
    steps = "".join(f'<li><b>{e(a)}.</b> {e(b)}</li>' for a, b in p["steps"])
    limits = "".join(f"<li>{e(l)}</li>" for l in p["limits"])
    data = "".join(f'<tr><td>{e(a)}</td><td>{e(b)}</td>{login_cell(a)}<td><a href="{u}">source</a></td></tr>' for a, b, u in p["data"] + T["data"])
    figs = "".join(f'<figure class="fig {c}"><img src="/assets/img/{f}" alt="{e(cap)}" loading="lazy" /><figcaption>{e(cap)}</figcaption></figure>' for f, cap, c in p["figs"])
    finds = "".join(f"<li><b>{e(a)}</b> {e(b)}</li>" for a, b in T["findings"])
    crit = "".join(f'<li><b>{e(c)}.</b> {e(p["criteria"][c])}</li>' for c, _ in CRITERIA)
    upt = f'<details class="deep"><summary>Earthdata upgrade · {e(U["title"])}</summary><div class="prose"><p>{e(U["text"])}</p><p class="fine">{e(U["note"])}</p></div>{("<figure class=opera-fig>" + opera_svg() + "</figure>") if U.get("series") == "opera" else ""}</details>' if U else ""
    title = f"{p['name']} · Orbit to Ground"
    secs = {}
    secs["hero"] = f"""<section class="mod-hero"><div class="topo-hero" aria-hidden="true"></div><div class="wrap mod-hero-in">
<div class="mod-hero-txt"><p class="chip"><i></i>Module {p['n']} · {e(M['role'])} · {e(A['name'])}</p>
<h1>{e(A['headline'])}</h1><p class="lede">{e(A['line'])}</p>
<div class="actions"><a class="btn launch" href="/{s}/app/">Launch dashboard</a><a class="btn ghost" href="#actions">See the actions</a></div></div>
{person_fig(*A['hero'], cls="hero-person")}</div></section>
"""
    secs["problem"] = f"""<section class="section tight" id="problem"><div class="wrap">
{step_head(1, "The problem", "")}
<div class="problem-pic" data-fx="rise"><img src="/assets/img/{pimg}" alt="{e(pcap)}" loading="lazy" /><div class="pp-txt"><strong class="grad">{e(big)}</strong><p>{e(pline)}</p><small>{e(pcap)}</small></div></div>
</div></section>
"""
    secs["satellite"] = f"""<section class="section tight" id="satellite"><div class="wrap">
{step_head(2, "What the satellite shows", "")}
<div class="shows">{shows}</div></div></section>
"""
    secs["actions"] = f"""<section class="section tight" id="actions"><div class="wrap">
{step_head(3, "What I'll do", f"{len(A['recs'])} actions, each tied to a satellite result.")}
{recs_block(s)}
<p class="fine">Outcomes are qualitative: we haven't measured yields, lives or costs. Each button opens the dashboard with that action selected; tasking there is simulated.</p>
</div></section>
"""
    secs["impact"] = f"""<section class="section tight" id="impact"><div class="wrap">
{step_head(4, "Impact", "Before → with this tool.")}
{ba_html(BA[s])}
<p class="mstrip-k">Backed by the model and the trend tests · one seed, not a published benchmark</p>{metrics_strip(s)}
</div></section>
"""
    secs["try"] = f"""<section class="section tight" id="try"><div class="wrap">
<div class="step-head" data-fx="rise"><p class="eyebrow">Try it</p><h2>The dashboard, with the same steps built in.</h2></div>
<div class="demo-frame" data-fx="rise"><div class="demo-bar"><i></i><i></i><i></i><span>/{s}/app/</span><a href="/{s}/app/">Full screen &nearr;</a></div>
<iframe src="/{s}/app/" title="{e(p['name'])} live demo" loading="lazy" allow="fullscreen"></iframe></div>
<div class="actions center"><a class="btn launch" href="/{s}/app/">Launch dashboard</a></div>
</div></section>
"""
    secs["trend"] = f"""<section class="section tight trend-sec" id="trend"><div class="wrap">
<div class="step-head" data-fx="rise"><p class="eyebrow">Trend test · {e(T['theme'])}</p><h2>{e(T['title'])}</h2></div>
<div class="tw" data-trend="{T['widget']}" data-fx="rise"><noscript><p class="map-cap">The interactive trend chart needs JavaScript.</p></noscript></div>
<details class="deep"><summary>What the tests found</summary><ul class="findings">{finds}</ul><p class="fine">Mann-Kendall (α = 0.05) and Sen's slope with 95% CI, one value per year.</p></details>
<details class="deep"><summary>Trend maps</summary>{maps_block(s)}</details>
</div></section>
"""
    secs["how"] = f"""<section class="section tight" id="how"><div class="wrap">
<div class="step-head" data-fx="rise"><p class="eyebrow">How</p><h2>Method, data and limits</h2></div>
<details class="deep"><summary>Model results</summary><div class="kpis k3">{kpis}</div><p class="fine">Held-out test data vs baselines. One seed per run, not a published benchmark.</p></details>
{upt}
<details class="deep"><summary>Inside the tool</summary><div class="figs">{figs}</div></details>
<details class="deep"><summary>The approach</summary><ul class="facts">{steps}</ul></details>
<details class="deep"><summary>Limits we know about</summary><ul class="facts">{limits}</ul></details>
<details class="deep"><summary>Data sources</summary><div class="table-wrap"><table><thead><tr><th>Dataset</th><th>How it's used</th><th>Access</th><th>Link</th></tr></thead><tbody>{data}</tbody></table></div></details>
<details class="deep"><summary>Judging criteria</summary><ul class="facts">{crit}</ul><p class="fine">First designed around the Space Apps 2026 brief <a href="{p['challenge_url']}">{e(p['challenge'])}</a>; here it is the {e(M['role']).lower()} module of one system in {e(SITE['challenge'])}.</p></details>
</div></section>
"""
    secs["pager"] = f"""<section class="block"><div class="wrap pager">
<a class="spot" href="/{prev_p['slug']}/"><div class="spot-body"><small>&larr; Module {prev_p['n']}</small><b>{e(prev_p['name'])}</b></div></a>
<a class="spot" href="/{next_p['slug']}/" style="text-align:right"><div class="spot-body"><small>Module {next_p['n']} &rarr;</small><b>{e(next_p['name'])}</b></div></a>
</div></section>
"""
    secs = module_override(s, secs, A)
    order = secs.pop("_order", names_default())
    return (head(title, p["tagline"], f"/{s}/", p["card_img"].replace(".webp", "-og.png")).replace("</head>", module_head(s) + "</head>", 1) + nav(f"/{s}/")
            + '<main id="content">\n' + "\n".join(secs[k] for k in order if secs.get(k)) + "</main>\n" + module_foot(s) + FOOT)

def slide_list():
    """Newest deck files at build time: slide PNGs from submission/build, titles from submission/deck.html."""
    import re as _re
    bd = ROOT / "submission" / "build"; files = sorted(bd.glob("slide-*.png"), key=lambda f: int(_re.findall(r"\d+", f.stem)[0]))
    titles = []
    dh = ROOT / "submission" / "deck.html"
    if dh.exists():
        for sec in _re.split(r"<section", dh.read_text())[1:]:
            h = _re.search(r"<h[12][^>]*>(.*?)</h[12]>", sec, _re.S)
            titles.append(_re.sub(r"<[^>]+>", "", h.group(1)).strip() if h else "")
    out = []
    for i, f in enumerate(files):
        out.append((i + 1, f, titles[i] if i < len(titles) and titles[i] else f"Slide {i + 1}"))
    return out

def copy_slides():
    sl = slide_list(); d = DIST / "slides" / "img"; d.mkdir(parents=True, exist_ok=True)
    for n, f, t in sl:
        try:
            from PIL import Image
            im = Image.open(f).convert("RGB"); im.save(d / f"slide-{n}.webp", quality=86)
            im.thumbnail((640, 360)); im.save(d / f"slide-{n}-thumb.webp", quality=80)
        except Exception:
            shutil.copy(f, d / f"slide-{n}.webp")
    return sl

def slides_strip(sl):
    if not sl: return ""
    cards = "".join(f'<a class="slide-thumb" href="/slides/#slide-{n}"><img src="/slides/img/slide-{n}-thumb.webp" alt="Slide {n}: {e(t)}" loading="lazy" width="640" height="360" /><span class="mono">{n:02d}</span><b>{e(t)}</b></a>' for n, f, t in sl)
    return f"""<section class="section" id="slides" style="padding-top:2rem"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">The deck</p><h2>{len(sl)} slides, same story.</h2></div><p>Read the slides right here, or download the PDF. <span class="actions" style="display:inline-flex;margin:.6rem 0 0"><a class="btn" href="/slides/">View the slides</a><a class="btn ghost" href="/submission/deck.pdf">Download PDF</a></span></p></div>
<div class="slide-strip" data-fx="rise">{cards}</div></div></section>"""

def slides_page(sl):
    slides = "".join(f'<figure class="slide" id="slide-{n}"><img src="/slides/img/slide-{n}.webp" alt="Slide {n}: {e(t)}" {"loading=\"lazy\" " if n > 1 else ""}width="1920" height="1080" /><figcaption><span class="mono">{n:02d} / {len(sl):02d}</span>{e(t)}</figcaption></figure>' for n, f, t in sl)
    dots = "".join(f'<a href="#slide-{n}" aria-label="Slide {n}">{n}</a>' for n, f, t in sl)
    return head("Slides · Orbit to Ground", "The Orbit to Ground deck: " + SITE["desc"], "/slides/") + nav("/slides/") + f"""<main id="content">
<section class="hero short"><div class="topo-hero" aria-hidden="true"></div><div class="wrap hero-copy">
<p class="chip"><i></i>NASA Space Apps 2026 · {e(SITE['challenge'])}</p><h1>The slides</h1>
<p class="lede">{len(sl)} slides: the problem, the system, and one trend question per module, answered with NASA data.</p>
<div class="actions"><a class="btn" href="/submission/deck.pdf">Download PDF</a><a class="btn ghost" href="/#demo-video">&#9654; Demo video</a><a class="btn ghost" href="/">Back to the site</a></div></div></section>
<section class="block" style="padding-top:0"><div class="wrap slides-wrap"><nav class="slide-dots mono" aria-label="Jump to slide">{dots}</nav><div class="slides">{slides}</div></div></section>
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
    for f in (ROOT / "trends/out/maps").glob("*.png") if (ROOT / "trends/out/maps").exists() else []:
        try:
            from PIL import Image
            Image.open(f).convert("RGB").save(DIST / "assets/img" / ("map-" + f.stem.replace("_", "-") + ".webp"), quality=88)
        except Exception as ex: print("map convert failed", f, ex)
    global SLIDES
    SLIDES = copy_slides()
    (DIST / "slides").mkdir(exist_ok=True); (DIST / "slides" / "index.html").write_text(slides_page(SLIDES))
    (DIST / "index.html").write_text(landing())
    shutil.copytree(SRC / "shared", DIST / "shared", dirs_exist_ok=True)
    for i, p in enumerate(PROJECTS):
        copy_demo(p["slug"]); copy_module(p["slug"])
        (DIST / p["slug"] / "index.html").write_text(project(i, p))
    (DIST / "404.html").write_text(head("Not found · Orbit to Ground", SITE["desc"], "/404") + nav("") +
        '<main id="content"><section class="hero short"><div class="wrap hero-copy"><h1>Page not found</h1><p class="lede">That page doesn\'t exist.</p><div class="actions"><a class="btn" href="/">Back to the projects</a></div></div></section></main>' + FOOT)
    shutil.copy(SRC / "assets/img/favicon.ico", DIST / "favicon.ico")
    sub = DIST / "submission"; sub.mkdir(exist_ok=True)
    # What-if panel data (another worker writes submission/impact.json); dashboards hide the panel until it exists
    imp = ROOT / "submission" / "impact.json"; out_imp = DIST / "shared" / "impact.json"
    if imp.exists():
        dimp = json.loads(imp.read_text()); vw = ROOT / "src" / "impact_view.json"
        if vw.exists(): dimp["_view"] = {k: v for k, v in json.loads(vw.read_text()).items() if not k.startswith("_")}
        out_imp.write_text(json.dumps(dimp, ensure_ascii=False).replace("would have", "could have"))  # site wording rule
    elif out_imp.exists(): out_imp.unlink()
    # deck.html (slide 8 embeds the demo videos) + its assets and the per-app clips
    if (ROOT / "submission" / "deck.html").exists():
        shutil.copy(ROOT / "submission" / "deck.html", sub / "deck.html")
        for d in ("assets",):
            if (ROOT / "submission" / d).exists(): shutil.copytree(ROOT / "submission" / d, sub / d, dirs_exist_ok=True)
        if (ROOT / "submission" / "clips").exists(): shutil.copytree(ROOT / "submission" / "clips", sub / "clips", dirs_exist_ok=True)
    for fn in ("demo.mp4", "demo.en.srt", "deck.pdf"):
        if (ROOT / "submission" / fn).exists(): shutil.copy(ROOT / "submission" / fn, sub / fn)
        else: print("WARNING: missing submission/" + fn)
    if (sub / "demo.en.srt").exists():
        import re as _re
        (sub / "demo.en.vtt").write_text("WEBVTT\n\n" + _re.sub(r"(\d\d:\d\d:\d\d),(\d\d\d)", r"\1.\2", (sub / "demo.en.srt").read_text()))
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    urls = ["/", "/slides/"] + [f"/{p['slug']}/" for p in PROJECTS] + [f"/{p['slug']}/app/" for p in PROJECTS]
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls) + "</urlset>\n")
    (DIST / "_headers").write_text("/assets/*\n  Cache-Control: public, max-age=3600\n/submission/*.srt\n  Content-Type: text/plain; charset=utf-8\n/submission/*.vtt\n  Content-Type: text/vtt; charset=utf-8\n/submission/*\n  Cache-Control: public, max-age=600\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    bust_cache()
    n = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"built {DIST} ({n} files)")

def bust_cache():
    """Append ?v=<content hash> to every local .js/.css URL in the built HTML, so a browser never pairs new HTML with an
    old cached script or stylesheet (e.g. /assets/* is cached for an hour)."""
    import hashlib
    rx = re.compile(r'((?:src|href)=")([^"?#:]+\.(?:js|css))(")')
    memo = {}
    for page in DIST.rglob("*.html"):
        if "submission" in page.relative_to(DIST).parts: continue
        h = page.read_text()
        def rep(m):
            u = m.group(2); f = (DIST / u.lstrip("/")) if u.startswith("/") else (page.parent / u)
            try: f = f.resolve(strict=True)
            except OSError: return m.group(0)
            if f not in memo: memo[f] = hashlib.sha256(f.read_bytes()).hexdigest()[:10]
            return f"{m.group(1)}{u}?v={memo[f]}{m.group(3)}"
        h2 = rx.sub(rep, h)
        if h2 != h: page.write_text(h2)

if __name__ == "__main__":
    main()
