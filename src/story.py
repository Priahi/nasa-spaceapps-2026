"""Scroll-driven data stories (signal -> change -> confidence -> nuance -> decision).
Every number here is read from trends/out/*.json, earthdata/*/*.json or quoted from src/content.py findings."""
import json, statistics
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parent.parent
def _j(p):
    f = ROOT / p
    return json.loads(f.read_text()) if f.exists() else {}
T = _j("trends/out/trends.json"); ED = _j("trends/out/earthdata_trends.json")
MCD = _j("earthdata/hot-spots/mcd64_h11v03.json"); OPERA = _j("earthdata/sar-change/opera_valencia.json")

def fmt(v, d=0):
    s = f"{v:,.{d}f}"
    return s.replace("-", "−")

# ---------- charts ----------
def line_chart(xs, ys, slope, unit, label, mark=None, W=640, H=340, dec=0, gap_years=(), ci=None, note=None, mini=False):
    m = dict(l=58, r=18, t=26, b=34)
    x0, x1 = min(xs), max(xs); lo, hi = min(ys), max(ys); pad = (hi - lo) * 0.12 or 1; lo -= pad; hi += pad
    X = lambda x: m["l"] + (x - x0) / (x1 - x0) * (W - m["l"] - m["r"])
    Y = lambda y: H - m["b"] - (y - lo) / (hi - lo) * (H - m["t"] - m["b"])
    icpt = statistics.median([y - slope * x for x, y in zip(xs, ys)])
    # split the data line at gaps
    segs, cur = [], []
    for i, (x, y) in enumerate(zip(xs, ys)):
        if cur and x - xs[i - 1] > 1: segs.append(cur); cur = []
        cur.append((x, y))
    segs.append(cur)
    data = "".join(f'<path class="dl" pathLength="1" d="M{" L".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in s)}" />' for s in segs if len(s) > 1)
    dots = "".join(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="3"><title>{x}: {fmt(y, dec)} {e(unit)}</title></circle>' for x, y in zip(xs, ys))
    tl = f'<path class="tl" pathLength="1" d="M{X(x0):.1f},{Y(icpt + slope * x0):.1f} L{X(x1):.1f},{Y(icpt + slope * x1):.1f}" />'
    band = ""
    if ci:
        xm = statistics.median(xs); ym = icpt + slope * xm
        f = lambda sl, x: ym + sl * (x - xm)
        pts = [(x0, f(ci[0], x0)), (x1, f(ci[0], x1)), (x1, f(ci[1], x1)), (x0, f(ci[1], x0))]
        pts = [(x, min(max(y, lo), hi)) for x, y in pts]
        band = f'<polygon class="ci" points="{" ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts)}" />'
    if note:
        ye = icpt + slope * x1
        tl += f'<text class="ann" x="{X(x1)-4:.1f}" y="{Y(ye) + (-12 if slope >= 0 else 20):.1f}" text-anchor="end">{e(note)}</text>'
    step = (hi - lo) / 4; ticks = ""
    for k in range(5):
        v = lo + step * k
        ticks += f'<line class="g" x1="{m["l"]}" x2="{W-m["r"]}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" /><text x="{m["l"]-8}" y="{Y(v)+4:.1f}" text-anchor="end">{fmt(v, dec if abs(hi-lo) < 20 else 0)}</text>'
    yrs = [y for y in range(x0, x1 + 1) if y % 5 == 0]
    ticks += "".join(f'<text x="{X(y):.1f}" y="{H-12}" text-anchor="middle">{y}</text>' for y in yrs)
    mk = f'<line class="mk" x1="{X(mark):.1f}" x2="{X(mark):.1f}" y1="{m["t"]}" y2="{H-m["b"]}" />' if mark else ""
    return (f'<figure class="sv-fig{" mini" if mini else ""}"><svg class="sv line" viewBox="0 0 {W} {H}" role="img" aria-label="{e(label)}">{ticks}{band}{mk}{data}{tl}{dots}</svg>' +
            (f'<figcaption>{e(label)}</figcaption></figure>' if mini else f'<figcaption><span class="key dl"></span>yearly value <span class="key tl"></span>Sen\'s slope{" <span class=\"key ci\"></span>95% CI band" if ci else ""} · {e(label)}</figcaption></figure>'))

def bar_chart(xs, ys, unit, label, hl=None, W=640, H=300):
    m = dict(l=58, r=12, t=30, b=30); mx = max(ys) * 1.12; bw = (W - m["l"] - m["r"]) / len(xs)
    Y = lambda v: (H - m["t"] - m["b"]) * v / mx
    out = ""
    for gv in _nice(mx):
        gy = H - m["b"] - Y(gv); out += f'<line class="g" x1="{m["l"]}" x2="{W-m["r"]}" y1="{gy:.1f}" y2="{gy:.1f}" /><text x="{m["l"]-8}" y="{gy+4:.1f}" text-anchor="end">{fmt(gv)}</text>'
    for i, (x, v) in enumerate(zip(xs, ys)):
        h = Y(v); bx = m["l"] + i * bw
        out += f'<rect class="b{" hl" if x == hl else ""}" style="--i:{i}" x="{bx+1.5:.1f}" y="{H-m["b"]-h:.1f}" width="{bw-3:.1f}" height="{h:.1f}" rx="2"><title>{x}: {fmt(v)} {e(unit)}</title></rect>'
        if x % 5 == 0: out += f'<text x="{bx+bw/2:.1f}" y="{H-10}" text-anchor="middle">{x}</text>'
        if x == hl: out += f'<text class="val" x="{bx+bw/2-4:.1f}" y="{H-m["b"]-h-8:.1f}" text-anchor="end">{x}: {fmt(v)} {e(unit)}</text>'
    return f'<figure class="sv-fig"><svg class="sv bars" viewBox="0 0 {W} {H}" role="img" aria-label="{e(label)}">{out}</svg><figcaption>{e(label)}</figcaption></figure>'

def _nice(mx):
    raw = mx / 4; mag = 10 ** len(str(int(raw))) / 10
    step = next(s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw)
    return [step * k for k in range(1, int(mx // step) + 1)]

def img(src, alt, cls=""):
    return f'<figure class="sv-fig img {cls}"><img src="/assets/img/{src}" alt="{e(alt)}" loading="lazy" /><figcaption>{e(alt)}</figcaption></figure>'

def slider(b, a, lb, la, ratio="1200 / 979"):
    return (f'<figure class="sv-fig"><div class="ba" style="aspect-ratio:{ratio}"><img src="/assets/img/{b}" alt="Before: {e(lb)}" /><img class="after" src="/assets/img/{a}" alt="After: {e(la)}" />'
            f'<span class="lab l">{e(lb)}</span><span class="lab r">{e(la)}</span><span class="handle" aria-hidden="true"></span>'
            f'<input type="range" min="0" max="100" value="50" aria-label="Compare before and after" /></div><figcaption>Drag to compare. OPERA DSWx-S1 surface water, 30 m.</figcaption></figure>')

def callout(big, unit, line, sub=""):
    return (f'<figure class="sv-fig callout-big"><p class="mono">What this means</p><strong class="grad">{e(big)}</strong><span class="u">{e(unit)}</span>'
            f'<p>{e(line)}</p>{f"<small>{e(sub)}</small>" if sub else ""}</figure>')

# ---------- agreement matrix ----------
def _t(path, *keys):
    d = path
    for k in keys:
        d = (d or {}).get(k)
    return d or {}
def rec(name, t, note=""):
    if not t: return None
    sig = t.get("significant"); tr = t.get("trend", "")
    arrow = "↑" if sig and tr == "increasing" else "↓" if sig and tr == "decreasing" else "–"
    cls = "up" if arrow == "↑" else "down" if arrow == "↓" else "flat"
    p = t["p"]; ps = "p < 0.001" if p < 0.001 else f"p = {p:.3f}" if p < 0.1 else f"p = {p:.2f}"
    return (name, arrow, cls, ps, note)

def matrix_rows():
    f = _t(T, "fire", "canada", "Canada"); w = T.get("water", {}); c = T.get("crops", {})
    imv, imo, imi = _t(ED, "imerg", "valencia"), _t(ED, "imerg", "ontario"), _t(ED, "imerg", "iowa")
    g = ED.get("grace", {}); gl = ED.get("gldas_iowa", {}); sm = ED.get("smap_iowa", {})
    def wv(reg, k): return _t(w, reg, k) or _t(w, reg, "region", k)
    rows = [
        ("Is fire activity in Canada rising?", "agree", "All four agree: rising", [rec("FIRMS harmonized count", f.get("harmonized_count")), rec("FIRMS MODIS-only count", f.get("modis_count")), rec("MODIS fire radiative power", f.get("modis_frp")), rec("MCD64A1 burned area (one tile)", MCD.get("trend"))]),
        ("Is fire activity in Argentina changing?", "agree", "All three agree: falling, the opposite of Canada", [rec("FIRMS MODIS-only count", _t(T, "fire", "argentina", "modis_count")), rec("FIRMS harmonized count", _t(T, "fire", "argentina", "harmonized_count")), rec("MODIS fire radiative power", _t(T, "fire", "argentina", "modis_frp"))]),
        ("Are Valencia's rain extremes rising?", "agree", "Reanalysis and satellite agree: no trend", [rec("MERRA-2 wettest day (NASA POWER)", wv("valencia", "rx1day")), rec("GPM IMERG wettest month", imv.get("wettest_month")), rec("GPM IMERG annual total", imv.get("annual_total"))]),
        ("Is eastern Spain's stored water changing?", "single", "One record: falling", [rec("GRACE/GRACE-FO water storage", g.get("valencia"))]),
        ("Are southern Ontario's rain extremes falling?", "disagree", "Records disagree: not claimed", [rec("MERRA-2 wettest day (NASA POWER)", wv("ontario", "rx1day")), rec("GPM IMERG wettest month", imo.get("wettest_month")), rec("GPM IMERG annual total", imo.get("annual_total"))]),
        ("Is Iowa's water changing?", "agree", "Five records agree: steady", [rec("GRACE/GRACE-FO water storage", g.get("iowa")), rec("GLDAS root-zone soil moisture", gl.get("RootMoist_inst")), rec("SMAP surface soil moisture", sm.get("central_iowa"), "11 seasons"), rec("GPM IMERG annual total", imi.get("annual_total")), rec("POWER root-zone wetness", _t(c, "rootzone_wetness_may_sep", "region"))]),
        ("Is Iowa's growing season getting longer?", "single", "One source, two scales: longer", [rec("POWER frost-free days, central Iowa", _t(c, "frost_free_days", "region")), rec("POWER frost-free days, Story County cell", _t(c, "frost_free_days", "story_cell")), rec("POWER first autumn frost", _t(c, "first_fall_frost_doy", "region"))]),
    ]
    return [(q, k, v, [r for r in rs if r]) for q, k, v, rs in rows]

def matrix(only=None):
    rows = matrix_rows()
    if only: rows = [rows[i] for i in only]
    out = ""
    for q, kind, verdict, recs in rows:
        chips = "".join(f'<li class="{c}"><b>{a}</b><span>{e(n)}</span><em>{e(p)}{" · " + e(nt) if nt else ""}</em></li>' for n, a, c, p, nt in recs)
        out += f'<div class="mx-row"><div class="mx-q"><p>{e(q)}</p><span class="mx-v {kind}">{e(verdict)}</span></div><ul class="mx-recs">{chips}</ul></div>'
    return (f'<figure class="sv-fig mx"><div class="mx-legend mono"><span class="up">↑ significant rise</span><span class="down">↓ significant fall</span><span class="flat">– no significant trend</span></div>{out}'
            f'<figcaption>Mann-Kendall test at α = 0.05 on one value per year. Each row asks one question of several independent NASA records.</figcaption></figure>')

# ---------- story shell ----------
def story(sid, eyebrow, title, intro, beats, app=None):
    """beats: list of (kicker, heading, html_text, media_html)"""
    if app: beats = beats[:-1] + [(beats[-1][0], beats[-1][1], beats[-1][2] + f'<a class="btn launch" href="{app}">Launch the dashboard</a>', beats[-1][3])]
    bh = "".join(f'<article class="beat{" is-active" if i == 0 else ""}" data-beat="{i}"><p class="beat-k mono">{e(k)}</p><h3>{e(h)}</h3>{t}<div class="beat-media">{m}</div></article>' for i, (k, h, t, m) in enumerate(beats))
    st = "".join(f'<div class="story-panel{" on" if i == 0 else ""}" data-beat="{i}">{m}</div>' for i, (k, h, t, m) in enumerate(beats))
    dots = "".join(f'<li class="{"on" if i == 0 else ""}">{e(k.split("·")[-1].strip())}</li>' for i, (k, h, t, m) in enumerate(beats))
    return f"""<section class="section story" id="{sid}" data-story><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">{e(eyebrow)}</p><h2>{e(title)}</h2></div><p>{e(intro)}</p></div>
<div class="story-grid"><div class="story-beats">{bh}</div>
<div class="story-stage"><div class="story-stage-in">{st}</div><ol class="story-dots mono">{dots}</ol></div></div>
</div></section>"""

def P(*ps): return "".join(f"<p>{x}</p>" for x in ps)
def plain_p(p):
    if p < 0.001: return "less than 1 time in 1,000"
    n = round(p * 1000)
    if n < 10: return f"about {n} times in 1,000"
    return f"about {round(p * 100)} times in 100"

# ---------- module stories ----------
def hotspots_story():
    m = T["fire"]["canada"]["Canada"]["modis_count"]; mt = MCD["trend"]; yrs = MCD["trend"]["x"]; km = MCD["trend"]["series"]
    lo, hi = m["sen_ci95"]
    return story("story", "The data story · Detect", "From scattered detections to a fire record you can trust.",
        "Five beats: the raw signal, what changed, how sure we are, where it gets subtle, and who acts on it.", [
        ("01 · The signal", "11.6 million fire detections, two sensors.", P("NASA FIRMS records every fire a satellite sees: MODIS since 2000, VIIRS since 2012. We use 11.6 million of them: 7.46 million over Canada and 4.15 million over Argentina. Over Canada since 2012, VIIRS reports about 5.6 times more fire than MODIS for the same ground, so the raw record jumps when the sensor changes.", "Hot Spots joins them into one 2000–2025 calendar per area, so a 2005 season and a 2023 season sit on the same scale."),
         img("hotspots-card.webp", "The harmonized fire calendar for Canada in the live tool: FIRMS detections per 0.25° cell.")),
        ("02 · What changed", "Burned area is climbing, and 2023 stands out.", P(f"MODIS MCD64A1 burned area for tile h11v03 (the boreal forest of northeastern BC, Alberta and Saskatchewan) shows the ground that actually burned each April–October. 2023 burned <b>{fmt(MCD['largest_year']['km2'])} km²</b>, more than double any earlier season in the record.", f"Across 2003–2025 the Sen's slope is <b>+{fmt(mt['sen_slope_per_year'])} km² a year</b>."),
         img("mcd64-map.webp", "Year each 500 m pixel last burned since 2003 (MCD64A1, tile h11v03).") + bar_chart(yrs, km, "km²", "Burned area per April–October season, MCD64A1 tile h11v03, 2003–2025.", hl=2023)),
        ("03 · How sure we are", "Four independent views agree.", P(f"MODIS detections over Canada rise by <b>+{fmt(m['sen_slope_per_year'])} a year</b>. The 95% confidence interval runs from +{fmt(lo)} to +{fmt(hi)}: wide, but every plausible slope is above zero.", f"p = {m['p']:.3f} means that if there were no real trend, a pattern this one-directional would turn up by chance {plain_p(m['p'])}. The harmonized count (p = 0.020), fire radiative power (p = 0.011) and MCD64A1 burned area (p = {mt['p']:.3f}) all point the same way."),
         line_chart(m["x"], m["series"], m["sen_slope_per_year"], "detections", "MODIS active-fire detections per year, Canada, 2003–2025", ci=m["sen_ci95"], note=f"+{fmt(m['sen_slope_per_year'])}/yr · p = {m['p']:.3f}") + matrix(only=[0])),
        ("04 · The nuance", "Where we hold back.", P("At province level the harmonized series is significant in five provinces but MODIS-only in none. The harmonized record joins a model back-cast (2003–2011) to observed VIIRS (2012 on), so a step at 2012 can pass for a trend. We call those tentative.", "MCD64A1 here is one tile, not all of Canada, and the biggest season sits at the end of the record. Monthly-total error for Canada is worse than the baseline (39.4% vs 16.7%), even though per-cell error is better."),
         img("hotspots-calendar.webp", "Alberta: harmonized 2000–2025 calendar. The dashed line marks 2012, when VIIRS starts.")),
        ("05 · Who acts on it", "A record that's comparable across 2012.", P("Fire-management agencies and forest planners compare seasons to set crews, budgets and prevention work. A record that doesn't jump when the sensor changes means a busy season reads as a busy season, not a sensor artefact.", "Unusual-month flags and calibrated intervals tell an analyst which months to check first, and how much to trust each number."),
         callout(f"+{fmt(mt['sen_slope_per_year'])} km²", "more burned ground each year", "In northeastern BC, Alberta and Saskatchewan, 2003–2025 (MCD64A1, p = 0.004).", "One tile; 95% CI +57 to +503 km² a year.")),
    ], app="/hotspots/app/")

def sar_story():
    ser = [r for r in OPERA.get("series", []) if r["valid_frac"] >= 0.8]
    g = ED["grace"]["valencia"]; im = ED["imerg"]["valencia"]
    return story("story", "The data story · Confirm", "Seeing a flood through the storm that caused it.",
        "Five beats: the raw radar, what changed, how sure we are, where it gets subtle, and who acts on it.", [
        ("01 · The signal", "Radar sees through the cloud.", P("On 29 October 2024 a DANA storm dropped extreme rain on Valencia; 229 people died in the Valencia region. Under that cloud, optical satellites saw nothing useful.", "Sentinel-1 radar works through cloud and at night. Smooth water reflects the radar pulse away, so it shows up dark. SAR Change turns those images into a water map anyone can read."),
         img("sar-after.webp", "Sentinel-1 radar false colour over Valencia after the flood (VV, VH, VV/VH).")),
        ("02 · What changed", "New water more than doubled in five days.", P("NASA/JPL's OPERA surface-water product, made from the same radar, counts water outside the lagoon and the sea. It rose from <b>30.7 km²</b> on 26 October to <b>77.7 km²</b> on 31 October, two days after the storm."),
         slider("opera-before.webp", "opera-after.webp", "26 Oct 2024", "31 Oct 2024")),
        ("03 · How sure we are", "Two independent water maps, one jump.", P("Our U-Net, trained on hand-labelled Sen1Floods11 chips, reaches 66.4% water IoU on 90 test chips: 3.0× the standard Otsu threshold (21.8%). OPERA is built separately by NASA/JPL and shows the same jump on 31 October, then 30–60 km² of standing water for three weeks.", f"On the longer scale, rain and storage tell different stories. Satellite rainfall (GPM IMERG, 1998–2024) shows no trend (annual p = {im['annual_total']['p']:.2f}). GRACE says the ground itself has been losing water: {fmt(g['sen_slope_per_year'], 2)} cm a year, p = {g['p']:.3f}, a pattern that would turn up by chance {plain_p(g['p'])} if nothing were changing."),
         _opera_bars(ser) + matrix(only=[2, 3])),
        ("04 · The nuance", "What the radar can't see.", P("The Albufera rice paddies were already filling before the storm (4 km² on 1 October, 31 km² on 26 October), so only the jump to 77.7 km² is the flood. Radar misses water between buildings, so the urban flooding in l'Horta Sud is under-detected, and much of it drained before the first pass.", "NISAR's L-band GCOV products start in October 2025, after this flood, so the viewer is NISAR-ready rather than NISAR-built. One extreme event isn't a trend."),
         img("sar-before.webp", "The same radar view before the flood. Built-up areas scatter strongly, which hides water in the streets.")),
        ("05 · Who acts on it", "Where the water stayed.", P("Civil protection, responders and insurers need to know where water is standing days later, not just where it fell. A radar map available through cloud tells them where to send pumps, check access and verify claims first.", "The trend layer adds the slow story: rain extremes aren't trending, but stored water is falling. Planners should prepare for the extreme event itself rather than expect a steady rise in rain."),
         callout("77.7 km²", "of new surface water on 31 October", "Up from 30.7 km² five days earlier (OPERA DSWx-S1, 30 m).", "The Albufera paddies were already rising; urban water is under-detected.")),
    ], app="/sar-change/app/")

def _opera_bars(ser):
    seen, rows = set(), []
    for r in ser:
        if r["acq"][:8] in seen: continue
        seen.add(r["acq"][:8]); rows.append(r)
    W, H, m = 640, 280, dict(l=44, r=10, t=28, b=30); mx = max(r["new_water_km2"] for r in rows) * 1.15; bw = (W - m["l"] - m["r"]) / len(rows)
    out = ""
    for gv in (20, 40, 60, 80):
        if gv > mx: break
        gy = H - m["b"] - (H - m["t"] - m["b"]) * gv / mx; out += f'<line class="g" x1="{m["l"]}" x2="{W-m["r"]}" y1="{gy:.1f}" y2="{gy:.1f}" /><text x="{m["l"]-6}" y="{gy+4:.1f}" text-anchor="end">{gv}</text>'
    for i, r in enumerate(rows):
        v = r["new_water_km2"]; h = (H - m["t"] - m["b"]) * v / mx; x = m["l"] + i * bw; post = r["acq"] >= "20241029"
        out += f'<rect class="b{" hl" if post else ""}" style="--i:{i}" x="{x+1.5:.1f}" y="{H-m["b"]-h:.1f}" width="{bw-3:.1f}" height="{h:.1f}" rx="2"><title>{r["acq"][:4]}-{r["acq"][4:6]}-{r["acq"][6:8]}: {v} km²</title></rect>'
        if i % 4 == 0: out += f'<text x="{x+bw/2:.1f}" y="{H-10}" text-anchor="middle">{int(r["acq"][6:8])} {"Oct" if r["acq"][4:6] == "10" else "Nov"}</text>'
    return f'<figure class="sv-fig"><svg class="sv bars" viewBox="0 0 {W} {H}" role="img" aria-label="New water per radar pass">{out}</svg><figcaption>New water outside usual water, km², per OPERA pass (≥ 80% valid pixels). Lighter bars: after the 29 October storm.</figcaption></figure>'

def field_story():
    ff = T["crops"]["frost_free_days"]["region"]; lo, hi = ff["sen_ci95"]
    return story("story", "The data story · Adapt", "From a field's history to next season's plan.",
        "Five beats: the raw signal, what changed, how sure we are, where it gets subtle, and who acts on it.", [
        ("01 · The signal", "Every field, every year, from orbit.", P("Story County, Iowa, is mostly corn and soybeans. USDA's Cropland Data Layer gives each 30 m field a crop label every year since 2009, and NASA's Harmonized Landsat and Sentinel-2 (HLS) shows how green each field is in mid-summer.", "Field Shift learns from that history, plus NASA terrain, climate and NDVI, to predict next season's crop."),
         img("field-cdl.webp", "Story County crop map from the USDA Cropland Data Layer: corn, soybeans, hay, grass and developed land.")),
        ("02 · What changed", "The growing season is about 19 days longer.", P(f"NASA POWER daily temperatures for central Iowa, 1981–2025, show the frost-free season growing by <b>+{ff['sen_slope_per_year']:.2f} days a year</b>. Most of it comes from autumn: the first frost now arrives later (p < 0.001), while the last spring frost hasn't moved (p = 0.48). Corn growing degree days rise too (p < 0.001)."),
         line_chart(ff["x"], ff["series"], ff["sen_slope_per_year"], "days", "Frost-free season length, central Iowa, 1981–2025", ci=ff["sen_ci95"], note=f"+{ff['sen_slope_per_year']:.2f} d/yr · p = {ff['p']:.3f}")),
        ("03 · How sure we are", "Longer season, steady water.", P(f"The 95% confidence interval for the season trend is +{lo:.2f} to +{hi:.2f} days a year, entirely above zero. p = {ff['p']:.3f}: a pattern this strong would turn up by chance {plain_p(ff['p'])} with no real trend. The Story County cell agrees (p = 0.002).", "Water is the other half of the decision. GRACE, GLDAS, SMAP, GPM IMERG and NASA POWER all find no significant trend in Iowa's water, so a longer season isn't coming with less water."),
         matrix(only=[5, 6])),
        ("04 · The nuance", "What the satellites can't tell apart.", P("Mid-summer NDVI is near saturation over both corn and soybeans, so HLS shows field-by-field contrast but can't separate crop types. Crop labels come from the Cropland Data Layer, not from HLS. SMAP soil moisture covers only 11 seasons, too short for a strong test.", "The crop model is honest about its limits: hay F1 is 0.33, the rare 'other crop' class is 0, and temperature scaling made calibration worse, so the tool keeps the raw probabilities."),
         img("hls-ndvi.webp", "HLS 30 m NDVI, Story County: 1 Aug 2024, 31 Jul 2025 and the change between them.", "light")),
        ("05 · Who acts on it", "Next season's plan, weighed honestly.", P("A farmer or agronomist decides what to plant next year and how to rotate over four. A later first frost with steady water widens the window after harvest, which favours longer-season hybrids and cover crops: options the rotation explorer lets them test.", "It ranks 36 non-dominated four-year plans by the farmer's own weights on five indicators: water demand, erosion risk, nitrogen-fixing share, heat and frost exposure, and soil-moisture stress."),
         callout("≈19 days", "longer frost-free season since 1981", f"Central Iowa, NASA POWER, +{ff['sen_slope_per_year']:.2f} days a year (p = {ff['p']:.3f}).", "With no significant trend in Iowa's water across five records.")),
    ], app="/field-shift/app/")

def small_multiples():
    def cell(title, t, unit, dec=0):
        sig = t["significant"]; v = ("rising" if t["trend"] == "increasing" else "falling") if sig else "no trend"
        ps = "p < 0.001" if t["p"] < 0.001 else f"p = {t['p']:.3f}" if t["p"] < 0.1 else f"p = {t['p']:.2f}"
        return (f'<div class="sm-cell {"sig" if sig else "ns"}"><p class="sm-t">{e(title)}</p><p class="sm-v mono">{e(v)} · {ps}</p>'
                + line_chart(t["x"], t["series"], t["sen_slope_per_year"], unit, f"{title}, {unit}", dec=dec, W=320, H=170, ci=t["sen_ci95"], mini=True) + '</div>')
    g = ED["grace"]; im = ED["imerg"]
    fc, fa = T["fire"]["canada"]["Canada"]["modis_count"], T["fire"]["argentina"]["modis_count"]
    rows = [("Fire detections · FIRMS MODIS-only (per year)", [("Canada", fc), ("Argentina", fa)], "detections", 0),
            ("Water storage · GRACE/GRACE-FO (cm)", [("Eastern Spain", g["valencia"]), ("Southern Ontario", g["ontario"]), ("Central Iowa", g["iowa"])], "cm", 1),
            ("Annual rain · GPM IMERG (mm)", [("Eastern Spain", im["valencia"]["annual_total"]), ("Southern Ontario", im["ontario"]["annual_total"]), ("Central Iowa", im["iowa"]["annual_total"])], "mm", 0)]
    out = "".join(f'<p class="sm-row mono">{e(rt)}</p><div class="sm-grid">' + "".join(cell(n, t, u, d) for n, t in cells) + '</div>' for rt, cells, u, d in rows)
    return f'<figure class="sv-fig sm">{out}<figcaption>Same test, same scale of evidence, three places. Shaded band: 95% CI of Sen\'s slope. Highlighted: significant at α = 0.05.</figcaption></figure>'

def trend_story():
    g = ED["grace"]["valencia"]; im = ED["imerg"]["valencia"]["annual_total"]
    return story("trend-story", "The trend layer · Measure", "Is it a trend, or one bad year?",
        "The same four questions in every module, and the same discipline: test it, then check it against a second record.", [
        ("01 · Weigh the water", "Gravity satellites weigh the ground.", P("GRACE and GRACE-FO measure tiny changes in Earth's gravity as water moves. Over eastern Spain, total stored water (soil, groundwater, lakes) has fallen since 2003, with a gap in 2017–2018 between the two missions."),
         line_chart(g["x"], g["series"], g["sen_slope_per_year"], "cm", "GRACE/GRACE-FO total water storage anomaly, eastern Spain, cm", dec=1, mark=2017, ci=g["sen_ci95"], note=f"{fmt(g['sen_slope_per_year'], 2)} cm/yr · p = {g['p']:.3f}")),
        ("02 · Test it", "A slope, a range, a probability.", P(f"Sen's slope: <b>{fmt(g['sen_slope_per_year'], 2)} cm a year</b>, the median of every pairwise slope, so one odd year can't drag it. The 95% range is {fmt(g['sen_ci95'][0], 2)} to {fmt(g['sen_ci95'][1], 2)}: every plausible value is a loss.", f"Mann-Kendall p = {g['p']:.3f}: if nothing were changing, a run this one-directional would turn up {plain_p(g['p'])}. It survives the autocorrelation check too."),
         callout(f"{fmt(g['sen_slope_per_year'], 2)} cm", "of stored water lost per year", "Eastern Spain, 2003–2025, GRACE/GRACE-FO (p = 0.002).", "95% CI −0.61 to −0.14 cm a year.")),
        ("03 · Compare places", "Same question, three places, different answers.", P("Run the identical test on each region. Stored water is falling in eastern Spain and rising in southern Ontario, while Iowa's is flat. Satellite rainfall shows no significant trend in any of the three.", "That's what a trend detective should find: change is local, and a single global headline would hide it."),
         small_multiples()),
        ("04 · Check it twice", "Where records agree, and where they don't.", P(f"Valencia's rain doesn't trend in reanalysis or in satellite rainfall (IMERG annual p = {im['p']:.2f}). In southern Ontario the reanalysis says rain extremes are falling, but satellite rainfall doesn't confirm it, so we don't claim it."),
         matrix()),
    ])

def chain():
    """Connecting narrative across modules: each finding feeds the next decision."""
    mt = MCD["trend"]; ff = T["crops"]["frost_free_days"]["region"]; g = ED["grace"]["valencia"]
    steps = [
        ("01 · Detect", "/hotspots/", f"+{fmt(mt['sen_slope_per_year'])} km²", "more burned ground a year, northeastern BC to Saskatchewan (p = 0.004)", "Fire agencies plan seasons on a record that doesn't jump at the 2012 sensor switch.", "Flags where the land is changing, so the next look goes there."),
        ("02 · Confirm", "/sar-change/", "77.7 km²", "of new water two days after the Valencia storm, seen through cloud", "Responders send pumps and checks to where water is still standing.", "Turns an event into verified ground truth the trend layer can test."),
        ("03 · Adapt", "/field-shift/", "≈19 days", "longer frost-free season in central Iowa since 1981 (p = 0.006)", "A farmer weighs 36 rotation plans by their own priorities.", "Puts the land's history to work in next season's plan."),
        ("04 · Measure", "/#trend-story", f"{fmt(g['sen_slope_per_year'], 2)} cm/yr", "stored water lost in eastern Spain, while rain shows no trend", "Planners learn which changes are trends to plan around and which are one-offs to respond to.", "Feeds back to Detect: where to watch next."),
    ]
    cards = "".join(f'<li class="spot chain-card" style="--i:{i}"><a href="{h}"><p class="mono">{e(k)}</p><strong class="grad">{e(n)}</strong><span class="u">{e(u)}</span>'
                    f'<p class="dec"><b>Decision it changes.</b> {e(d)}</p><p class="feeds"><b>Feeds the next step.</b> {e(f)}</p></a></li>' for i, (k, h, n, u, d, f) in enumerate(steps))
    return f"""<section class="section chain-sec" id="story"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">What · one story</p><h2>Each finding feeds the next decision.</h2></div><p>Detect where the land is changing, confirm it when optical satellites can't see, adapt the plan on the ground, and measure whether it's a trend worth planning around.</p></div>
<ol class="chain" data-fx="stagger">{cards}</ol></div></section>"""

STORIES = {"hotspots": hotspots_story, "sar-change": sar_story, "field-shift": field_story}

# ---------- use cases and user flows ----------
# Default flows describe what each dashboard actually does; replaced by submission/STORY.md content when available.
FLOWS = {  # from submission/STORY.md section 4 (six users, screens named as in the live dashboards)
  "hotspots": [
    {"user": "Provincial fire-management analyst", "where": "Alberta or British Columbia",
     "start": "2023 was enormous, but they can't say whether their province is in a multi-year rise: VIIRS sees about 5.6× more fire than MODIS since 2012, so 2005 and 2023 aren't in the same units.",
     "steps": ["Pick the Alberta or B.C. preset, or draw a fire district.", "Read the disagreement map and the held-out test card, including the monthly-total miss.", "Scroll the 2000–2025 calendar: unusual months outlined, hover for count, z-score and interval; download the CSV.", "On the module page, switch the trend between harmonized, MODIS-only and fire radiative power."],
     "decision": "Brief a national rise on the conservative record (MODIS-only +3,019 detections a year, p = 0.035), but not a provincial trend where MODIS-only isn't significant.",
     "end": "One calendar that can sit next to a 2005 season, a CSV, a known error, and a trend statement no stronger than the conservative test.",
     "benefits": "Fire managers, and the communities their season plans protect.", "improves": "Saying whether fire is really rising, at the right scale, without mistaking the 2012 sensor switch for change."},
    {"user": "Community emergency planner", "where": "A town or regional district",
     "start": "They need to know whether this month is unusual for their area, in words a mayor can use.",
     "steps": ["Draw a box around the community.", "Read the calendar for that box; a cyan outline marks a month with |z| > 3.5 against its 26-year median.", "Hover for the z-score and interval; download the CSV for the briefing pack."],
     "decision": "Either \"this month is flagged unusual against the 2000–2025 median for this box\" or \"it isn't\", with the interval attached.",
     "end": "A single calendar tile and a sentence that is dated, bounded and honest.",
     "benefits": "Local officials and the residents they brief.", "improves": "Deciding whether a month warrants extra readiness, based on the area's own record rather than a national headline."}],
  "sar-change": [
    {"user": "Flood-response coordinator", "where": "Valencia / l'Horta Sud",
     "start": "After 29 October 2024 the sky is closed, the public can't read a radar image, and there's a risk of treating one disaster as proof that autumns are getting wetter.",
     "steps": ["Viewer tab: swipe before/after on the same orbit (26 Oct vs 7 Nov), then scrub the time-lapse.", "Read \"Why radar works here\".", "On the module page: OPERA new water, 30.7 → 77.7 km², with the paddy and urban caveats.", "Trend layer: no rain trend in POWER or IMERG; GRACE storage falling."],
     "decision": "Brief the flood as a cloud-proof, quantified jump in new water, with urban flooding undercounted, and not as evidence of a wetter climate.",
     "end": "A swipeable radar story, an OPERA number with a date, and tested climate context that prevents a false trend claim.",
     "benefits": "Responders and the residents they need to reach.", "improves": "Showing where water went when optical satellites are blind, without overstating what one event means."},
    {"user": "Municipal engineer or insurer", "where": "Valencia region",
     "start": "They need a footprint for drainage design or a loss estimate, and a view on whether this is the new normal.",
     "steps": ["Swipe the radar and read the OPERA series.", "Apply the caveats: paddies already filling before the storm, urban water under-detected.", "Read the trend layer and the GRACE mascon map: drying storage, no rain trend."],
     "decision": "Treat urban loss as larger than the radar footprint, and plan for an extreme event on a drying water-storage background, not a proven rise in extreme rain.",
     "end": "A bounded statement: what the radar saw, what it missed, and what the 20- to 45-year tests do and don't support.",
     "benefits": "Ratepayers and policyholders in flood-prone districts.", "improves": "Sizing drainage or cover from evidence with its limits stated, rather than from one image."}],
  "field-shift": [
    {"user": "Story County farmer", "where": "Story County, Iowa",
     "start": "They run corn-soy and keep hearing the climate is changing, but don't have their field's history, their priorities and a tested season-length statement in one place.",
     "steps": ["Click a 1.2 km tile on the 2025 crop map, or pick the county-typical tile.", "Move the priority sliders: water demand, erosion risk, nitrogen-fixing share, heat/frost exposure, soil-moisture stress.", "Compare current corn-soy with the ranked four-year plans, the trade-off table and the Pareto front.", "Read the trend layer: longer, warmer season; no significant water trend."],
     "decision": "Pick a rotation that uses the longer autumn window (a cover crop after harvest, or a longer-season hybrid) without budgeting for a wetter or drier summer.",
     "end": "A shortlist scored to their own weights, a tested climate statement, and a reminder to check it with a local agronomist.",
     "benefits": "The farm, and the soil and water it depends on.", "improves": "Choosing next season's rotation with the trade-offs visible, instead of repeating last year by default."},
    {"user": "Agronomist or crop advisor", "where": "Advising several Iowa farms",
     "start": "They won't recommend a tool they can't audit; they need to know where the model is weak and which climate claims hold up.",
     "steps": ["Plan a rotation on a tile, as the farmer would.", "Open \"How we scored it\" and \"Model honesty\": baselines, ablation, the calibration miss, the 2025 disagreement map.", "Read the HLS and SMAP caveats and the crop and water trends."],
     "decision": "Use the tool to talk through season length and trade-offs, and override it on hay, rare crop classes and any soil-moisture trend claim.",
     "end": "They can point at a tile and say what is tested, what is a weighted score, and what still needs a field walk.",
     "benefits": "The farmers they advise.", "improves": "Giving advice that separates tested trends from model guesses."}],
}
PINS = [("hotspots", "Detect", "Canadian boreal forest", 55.0, -115.0, "r", -10), ("hotspots", "Detect", "Argentina", -31.0, -62.0, "r", 0),
        ("sar-change", "Confirm", "Valencia, Spain", 39.47, -0.38, "r", 0), ("sar-change", "Confirm", "Southern Ontario (NISAR site)", 43.65, -79.38, "r", -14),
        ("field-shift", "Adapt", "Story County, Iowa", 42.04, -93.47, "l", 16)]
LAND = (Path(__file__).parent / "land110.path").read_text() if (Path(__file__).parent / "land110.path").exists() else ""

def usecase_map():
    W, H = 1000, 500; lat0, lat1 = 75, -60
    sy = lambda lat: (90 - lat) / 180 * H; sx = lambda lon: (lon + 180) / 360 * W
    y0, y1 = sy(lat0), sy(lat1)
    pins = ""
    for i, (slug, role, name, la, lo, side, dy) in enumerate(PINS):
        x, y = sx(lo), sy(la) ; left = side == "l"; yl = y + dy
        pins += (f'<a href="/{slug}/app/" class="pin {slug}" style="--i:{i}"><circle class="halo" cx="{x:.1f}" cy="{y:.1f}" r="14" /><circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" />'
                 f'<text x="{x + (-12 if left else 12):.1f}" y="{yl - 2:.1f}" text-anchor="{"end" if left else "start"}">{e(name)}</text>'
                 f'<text class="r" x="{x + (-12 if left else 12):.1f}" y="{yl + 13:.1f}" text-anchor="{"end" if left else "start"}">{e(role)}</text></a>')
    return (f'<figure class="sv-fig ucmap"><svg class="sv map" viewBox="0 {y0:.0f} {W} {y1 - y0:.0f}" role="img" aria-label="Where the three dashboards are used: study areas and roles">'
            f'<path class="land" d="{LAND}" />{pins}</svg><figcaption>Study areas. Tap a point to launch that dashboard. Land outlines: Natural Earth (public domain).</figcaption></figure>')

def flow_html(f, slug):
    steps = "".join(f'<li class="fl-step"><span class="mono">Step {i + 1}</span><p>{e(s)}</p></li>' for i, s in enumerate(f["steps"]))
    return (f'<div class="flow" data-fx="rise"><div class="fl-head"><p class="mono">{e(f["where"])}</p><h3>{e(f["user"])}</h3></div>'
            f'<ol class="fl-track"><li class="fl-start"><span class="mono">Before</span><p>{e(f["start"])}</p></li>{steps}'
            f'<li class="fl-dec"><span class="mono">Decision</span><p>{e(f["decision"])}</p></li><li class="fl-end"><span class="mono">After</span><p>{e(f["end"])}</p></li></ol>'
            f'<dl class="fl-ben"><div><dt>Who benefits</dt><dd>{e(f["benefits"])}</dd></div><div><dt>Decision it improves</dt><dd>{e(f["improves"])}</dd></div></dl>'
            f'<p class="fl-note">An illustrative journey built from what the dashboard does today, not a field-tested outcome.</p>'
            f'<a class="btn launch" href="/{slug}/app/">Launch the dashboard</a></div>')

def usecases_home():
    flows = "".join(flow_html(f, slug) for slug in ("hotspots", "sar-change", "field-shift") for f in FLOWS[slug])
    return f"""<section class="section" id="use-cases"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">What · who it's for</p><h2>From a stuck situation to a better decision.</h2></div><p>Each dashboard is built around a person with a decision to make. Here's where they work, what they start with, the steps they take, and where they end up.</p></div>
<div data-fx="rise">{usecase_map()}</div>
<div class="flows">{flows}</div></div></section>"""

def usecases_module(slug):
    flows = "".join(flow_html(f, slug) for f in FLOWS[slug])
    return f"""<section class="section" id="use-case" style="padding-top:2rem"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">Who uses it</p><h2>One person, one decision, start to finish.</h2></div><p>The path through the dashboard, from the situation they start in to the decision it changes.</p></div>
<div class="flows">{flows}</div></div></section>"""


MAPS = {
  "hotspots": [("map-canada-fire-province-sen-slope.webp", "Sen's slope of annual fire detections per province, 2003–2025: harmonized (left) vs MODIS-only (right). Faded provinces are not significant. Harmonized is significant in five provinces; MODIS-only in none, so provincial rises are tentative.")],
  "sar-change": [("map-power-precip-per-cell-sen-slope.webp", "Per-cell trends in NASA POWER (MERRA-2) precipitation, 1981–2025, 35 cells per box. Eastern Spain: 8 cells with a significant rise in annual total, none in the wettest day. Southern Ontario's decreases here are not confirmed by GPM IMERG."),
                 ("map-grace-mascon-sen-slope.webp", "GRACE/GRACE-FO mascon trends, 2003–2025 (cm a year, clipped at ±2). The Valencia box sits in a flat-to-drying area; Great Lakes mascons are rising. Faded mascons are not significant.")],
  "field-shift": [("map-power-iowa-growing-season-per-cell-sen-slope.webp", "Per-cell trends across central Iowa, 1981–2025: frost-free season (29 of 35 cells significantly longer) and May–September growing degree days (35 of 35 rising)."),
                  ("map-grace-mascon-sen-slope.webp", "GRACE/GRACE-FO mascon trends, 2003–2025. The Iowa box sits in the flat zone, consistent with no significant water-storage trend (p = 0.57).")],
}
def maps_block(slug):
    ms = MAPS.get(slug) or []
    figs = "".join(f'<figure class="fig light wide" data-fx="rise"><img src="/assets/img/{f}" alt="{e(c)}" loading="lazy" /><figcaption>{e(c)}</figcaption></figure>' for f, c in ms)
    return f'<div class="sec-head" style="margin-top:3rem" data-fx="rise"><p class="eyebrow">Where it is changing</p><h3 style="font-weight:500;font-size:1.5rem;margin:.3rem 0 0">Trend maps</h3></div><div class="figs">{figs}</div>' if figs else ""
