"""Recommendations, two-sided impact and model metrics per app.
Every number is copied from a results file: trends/out/trends.json, trends/RESULTS.md, earthdata/*/*.json,
demos/*/data/*.json (calendar_alberta.json, metrics.json) or src/content.py. Outcomes are qualitative on purpose:
we have not measured yields, lives or money, so we never state them."""
import json
from html import escape as e

PEOPLE_NOTE = "Illustrative image (AI-generated), not a real person or event."

APPS = {
 "hotspots": {
  "name": "Hot Spots", "role": "Detect", "who": "Fire managers and community planners",
  "hero": ("people/fire-ops.webp", "A fire operations manager points at a map of fire hotspots on a wall screen"),
  "headline": "Know where fire is growing. Staff up before it arrives.",
  "line": "One 26-year fire record from NASA satellites, turned into crews, warnings and fuel work.",
  "problem": ("14.6 Mha", "of Canada's forest burned in 2023. Over 230,000 people were evacuated.", "mcd64-map.webp",
              "Last-burn year per 500 m pixel, NASA MODIS MCD64A1, 2003–2025"),
  "shows": [  # (big number, one-line caption, visual key)
    ("322k a year", "Fire detections across Canada, 2003–2025 average (VIIRS scale). Most burn in a belt across the N.W.T., B.C., Saskatchewan and Alberta.", "heat_map"),
    ("+272 km²/yr", "More ground burns every year in the boreal tile (NE B.C., Alberta, Sask.).", "mcd64_bars"),
    ("+3,019/yr", "Fire detections across Canada are rising (MODIS, 2003–2025).", "canada_line"),
    ("May", "Alberta's most-flagged unusual month: 5 of 16 since 2000.", "calendar"),
  ],
  "recs": [
    {"cls": "Crews & hiring", "img": "people/fire-crew.webp",
     "sat": "Detections in Alberta up ≈1,503 a year and B.C. ≈2,587 a year (2003–2025). July is Alberta's peak month.",
     "act": "Hire seasonal firefighters and pre-position crews in Alberta and B.C. before July.",
     "out": "Crews are in place for the busiest month, not called in after it starts.",
     "src": "Harmonized FIRMS record, Sen's slope, Alberta p = 0.035, B.C. p = 0.045. Tentative: the single-sensor check isn't significant."},
    {"cls": "Warn communities", "img": "people/community.webp",
     "sat": "May is Alberta's most-flagged unusual month: 5 of 16 flagged months (2011, 2016, 2019, 2023, 2025).",
     "act": "Put forest communities on notice by late April and check evacuation plans before May.",
     "out": "Warnings land before the early-season spikes the record keeps showing.",
     "src": "Hot Spots calendar, Alberta preset: robust z > 3.5 against each month's 2000–2025 median."},
    {"cls": "Fuel treatment", "img": "people/prescribed.webp",
     "sat": "Burned area in the boreal tile is rising +272 km² a year; 2023 burned 28,262 km².",
     "act": "Expand prescribed burns and fuel breaks around towns in that tile, starting where the last-burn map shows long-unburned ground.",
     "out": "Less fuel next to homes in the area where burned ground is growing fastest.",
     "src": "MODIS MCD64A1 tile h11v03, Mann-Kendall p = 0.004, 95% CI +57 to +503 km²/yr."},
    {"cls": "Next-season budget", "img": "people/fire-ops.webp",
     "sat": "Canada-wide fire power is rising +367 GW a year (p = 0.011). Argentina's detections are falling (−1,909 a year).",
     "act": "Budget next season for a rising national baseline, set region by region and reviewed each year with new data.",
     "out": "A budget built on a 23-year trend, not on last summer's headlines.",
     "src": "FIRMS MODIS FRP and MODIS-only counts, both significant after the Hamed-Rao check."},
  ],
  "sum": ("Fire is rising, tested twice", "Detections +3,019/yr (p = 0.035); burned area +272 km²/yr (p = 0.004)."),
  "impact": {
    "tech": [("One record, 2000–2025", "MODIS and VIIRS joined on one scale, so 2005 and 2023 compare fairly."),
             ("Rising, tested twice", "Detections +3,019/yr (p = 0.035) and burned area +272 km²/yr (p = 0.004).")],
    "human": [("Who", "Provincial fire managers, crews and community emergency planners."),
              ("Decision", "When to hire, where to stage crews, who to warn and where to treat fuel."),
              ("What changes", "Those calls rest on 23 years of evidence, not on one bad summer.")]},
  "metrics": [("8.5%", "lower error than the best baseline (RMSE 0.2844 vs 0.3109, Canada 2022–25)"),
              ("88.6%", "interval coverage, target 90%"),
              ("7.46 M", "NASA FIRMS detections over Canada (11.6 M with Argentina)"),
              ("39.4%", "honest miss: monthly-total error vs baseline 16.7%", "neg")],
  "guide": {"map": "Pick Alberta in the Region menu, or draw a box over any forest.", "map_btn": ("Show Alberta", "preset:alberta"),
            "changed": "Outlined squares in the calendar are unusual months. May and July light up again and again.",
            "changed_btn": ("Go to the calendar", "scroll:#calendar")},
 },
 "sar-change": {
  "name": "SAR Change", "role": "Confirm", "who": "Flood responders, city engineers and aid agencies",
  "hero": ("people/flood-ops.webp", "A flood response coordinator studies a radar flood map on a large screen"),
  "headline": "See the flood through the storm. Act on day two.",
  "line": "Radar maps the water when clouds hide it, then the 45-year record says how to plan for next time.",
  "problem": ("230", "people died in Spain's October 2024 DANA floods. Optical satellites saw only cloud.", "sar-after.webp",
              "Sentinel-1 radar over Valencia, 7 Nov 2024"),
  "shows": [
    ("77.7 km²", "New water two days after the flood, up from 30.7 km² (NASA OPERA, through cloud).", "opera_slider"),
    ("3 weeks", "Water stayed at 30–60 km² on all 7 radar passes to 19 Nov.", "opera_bars"),
    ("−0.39 cm/yr", "Stored ground water over eastern Spain is falling (GRACE, p = 0.002).", "grace_line"),
  ],
  "recs": [
    {"cls": "Evacuate & flag now", "img": "people/evacuate.webp",
     "sat": "New water jumped from 30.7 km² to 77.7 km² within two days of the 29 Oct storm, seen through cloud.",
     "act": "Flag and clear the districts inside the new-water footprint first, from the first radar pass after the storm.",
     "out": "Day-two decisions come from a cloud-proof map instead of waiting for clear skies.",
     "src": "NASA/JPL OPERA DSWx-S1, 30 m, passes with ≥ 80% valid pixels. My radar water model: IoU 66.4% vs 21.8% for the standard threshold."},
    {"cls": "Send damage teams", "img": "people/damage.webp",
     "sat": "Water stayed at 30–60 km² for three weeks. Radar misses water between buildings in l'Horta Sud.",
     "act": "Send damage-assessment teams to the areas still wet, and walk the l'Horta Sud streets even where the map looks dry.",
     "out": "Teams go where water lingers, and the radar's blind spot is covered on foot.",
     "src": "OPERA series 31 Oct–19 Nov 2024; urban under-detection is a known limit of radar water maps."},
    {"cls": "Drainage plan for next year", "img": "people/engineer.webp",
     "sat": "Annual rain is rising in 8 of 35 cells around Valencia, including the city's. The wettest day shows no trend (p = 0.28).",
     "act": "Add retention basins and drainage upgrades to next year's city plan, sized for the 2024 extreme rather than for a trend.",
     "out": "The plan is built on what happened and on what 45 years of data do and don't show.",
     "src": "NASA POWER 1981–2025 per-cell Mann-Kendall; GPM IMERG 1998–2024 also shows no trend (p = 0.62)."},
    {"cls": "Recovery aid & insurance", "img": "people/paddies.webp",
     "sat": "Most new water sits in the Albufera rice paddies, which had already risen from 4 to 31 km² before the storm.",
     "act": "Send farm recovery aid and crop-insurance checks to paddy owners, and treat urban losses as larger than the radar shows.",
     "out": "Aid reaches the farms the flood covered, with the urban gap flagged rather than missed.",
     "src": "OPERA 1 Oct–31 Oct 2024 series; the flood signal is the jump to 77.7 km²."},
  ],
  "sum": ("Flood mapped through cloud", "77.7 km² of new water two days after the storm; 30–60 km² for three weeks."),
  "impact": {
    "tech": [("Through cloud, day or night", "Radar water maps on day two: 77.7 km² of new water, 30–60 km² for three weeks."),
             ("Event vs trend", "Rain extremes show no trend (p = 0.28); stored water falls −0.39 cm/yr (p = 0.002).")],
    "human": [("Who", "Civil protection, damage assessors, city engineers, insurers and aid agencies."),
              ("Decision", "Who to evacuate, where to send teams, what to build and where aid goes."),
              ("What changes", "Action starts from a verified map, with its blind spots named.")]},
  "metrics": [("66.4%", "water IoU on 90 hand-labelled test chips"),
              ("3.0×", "the standard Otsu threshold (21.8%)"),
              ("1.63 s", "per 512×512 tile on a CPU"),
              ("p = 0.28", "no trend in wettest-day rain: I don't claim one", "neg")],
  "guide": {"map": "Drag the swipe to compare radar before and after the flood.", "map_btn": ("Show the swipe", "scroll:#swipeBox"),
            "changed": "Dark means smooth water. The new dark patches south of the city are the flood.",
            "changed_btn": ("Open the metrics", "tab:metrics")},
 },
 "field-shift": {
  "name": "Field Shift", "role": "Adapt", "who": "Farmers and crop advisers",
  "hero": ("people/farmer.webp", "A farmer at the edge of a corn field looks at a satellite field map on a tablet"),
  "headline": "A longer season, steady water. Plant for it now.",
  "line": "Your field's history plus 45 years of NASA climate data, turned into this season's plan.",
  "problem": ("33%", "of the world's land is degraded. The rotation picked this year shapes the soil for years.", "people/erosion.webp",
              "Spring erosion on a bare field"),
  "shows": [
    ("+19 days", "Iowa's frost-free season is about 19 days longer than in 1981 (p = 0.006).", "frost_line"),
    ("Steady", "Soil water shows no trend across GRACE, GLDAS, SMAP and IMERG.", "water_matrix"),
    ("22 km²", "of fields got less green between summer 2024 and 2025 (NASA HLS, 30 m).", "hls"),
  ],
  "recs": [
    {"cls": "Plant now", "img": "people/agronomist.webp",
     "sat": "The frost-free season is ≈19 days longer since 1981 (+0.43 days/yr), the first autumn frost comes later and heat units rise 4.6 GDD/yr.",
     "act": "Plant a longer-season corn hybrid on a test strip, and seed a cover crop right after harvest.",
     "out": "More of the season goes to growth. Yield is checked on the strip; I don't promise a number.",
     "src": "NASA POWER 1981–2025, central Iowa: frost-free p = 0.006 (95% CI +0.12 to +0.67 d/yr), first frost p < 0.001, GDD p < 0.001."},
    {"cls": "Rotate for soil", "img": "people/farmer.webp",
     "sat": "On a typical tile, a cover-crop rotation scores 67% lower erosion risk than corn-soy, for 13% more water demand.",
     "act": "Move the steepest tiles into the cover-crop rotation first.",
     "out": "Less bare soil in spring and autumn on the slopes most at risk.",
     "src": "Field Shift planning score from NASA NASADEM slope and MODIS NDVI bare-soil months. A planning index, not a measured soil loss."},
    {"cls": "Water & irrigation", "img": "people/soil.webp",
     "sat": "Soil water is steady: GRACE p = 0.57, GLDAS p = 0.27–0.38, SMAP 0.16–0.22 m³/m³ (p = 0.47). Summer rain shows no trend.",
     "act": "Keep a rain-fed plan and hold off on new irrigation spending. Check SMAP soil moisture each season.",
     "out": "Money stays out of irrigation the data doesn't call for, with a seasonal check in place.",
     "src": "Four independent NASA water records agree (agreement matrix). SMAP has 11 seasons, so its test is weak."},
    {"cls": "Scout these fields", "img": "people/scout.webp",
     "sat": "22 km² of fields got less green by more than 0.1 NDVI between 1 Aug 2024 and 31 Jul 2025.",
     "act": "Scout those patches first this summer.",
     "out": "Scouting time goes to the fields that changed.",
     "src": "NASA HLS v2.0, 30 m. Two dates from two sensors: it can't tell corn from soybeans."},
    {"cls": "Seed & input orders", "img": "people/agronomist.webp",
     "sat": "Next season's crop is predicted for every 30 m pixel in the county: 81.8% correct on held-out 2024–25 data.",
     "act": "Plan seed and input orders by predicted crop per tile, then confirm with each grower.",
     "out": "Orders start from a county-wide forecast instead of a blank sheet.",
     "src": "LightGBM, 66,666 test pixels. Crop history alone scores 81.4%, so NASA layers add a small, real gain (macro-F1 0.5012 vs 0.4633)."},
  ],
  "sum": ("Longer season, steady water", "+0.43 frost-free days/yr (p = 0.006); no trend in four NASA water records."),
  "impact": {
    "tech": [("Season is longer", "+0.43 frost-free days a year since 1981 (p = 0.006); first frost later (p < 0.001)."),
             ("Water is steady", "No trend in four independent NASA water records.")],
    "human": [("Who", "Farmers in Story County, Iowa, and their crop advisers."),
              ("Decision", "What to plant, when to cover, whether to irrigate and which fields to scout."),
              ("What changes", "The plan uses the extra weeks without betting on a wetter or drier summer.")]},
  "metrics": [("0.8176", "next-season crop accuracy (crop history alone 0.8136)"),
              ("0.5012", "macro-F1 across six crops (0.4633 baseline)"),
              ("0.811", "pixel accuracy, full-county 2025 map"),
              ("0.33", "honest miss: hay F1; rare 'other' class 0", "neg")],
  "guide": {"map": "Click any tile on the crop map, or pick a featured tile.", "map_btn": ("Pick a tile", "click:#featured button"),
            "changed": "Move the priority sliders. The ranked rotations update for that field.",
            "changed_btn": ("Go to the sliders", "scroll:#sliders")},
 },
}

SLUGS = ["hotspots", "sar-change", "field-shift"]

# ---- C2 decision-support data: verb + simulated tasks per rec (same order as APPS[slug]["recs"]) ----
C2 = {
 "hotspots": [
  ("Assign crews", [("crew", "Stage initial-attack crews in Alberta and B.C.", "before July"), ("plan", "Open seasonal firefighter hiring", "spring"), ("satellite", "Watch flagged cells on each VIIRS pass", "every pass")]),
  ("Send notice", [("notice", "Pre-season notice to forest communities", "late April"), ("plan", "Check evacuation plans", "before May"), ("camera", "Cue lookout cameras on the May watch list", "May")]),
  ("Approve work", [("drone", "Drone survey of long-unburned ground near towns", "this spring"), ("crew", "Prescribed-burn crew", "burn window"), ("plan", "Fuel-break work order", "this season")]),
  ("Approve budget", [("plan", "Regional baseline budget line", "next season"), ("sensor", "Annual refresh with new FIRMS data", "yearly")]),
 ],
 "sar-change": [
  ("Dispatch", [("notice", "Evacuation alert to districts in the new-water footprint", "now"), ("crew", "Rescue teams to flagged districts", "now"), ("satellite", "Pull the next Sentinel-1 / OPERA pass", "next pass")]),
  ("Assign teams", [("crew", "Damage teams to areas still wet", "this week"), ("drone", "Drone survey of l'Horta Sud streets (radar blind spot)", "this week")]),
  ("Add to plan", [("engineer", "Retention-basin and drainage study", "this year"), ("plan", "Line in next year's city plan", "next budget")]),
  ("Approve aid", [("plan", "Crop-insurance checks for Albufera paddies", "this month"), ("truck", "Recovery aid to paddy owners", "this month")]),
 ],
 "field-shift": [
  ("Schedule", [("seed", "Longer-season hybrid on a test strip", "planting"), ("seed", "Cover crop right after harvest", "harvest"), ("sensor", "Strip yield check", "harvest")]),
  ("Apply rotation", [("plan", "Move the steepest tiles to the cover-crop rotation", "next season")]),
  ("Approve plan", [("sensor", "Seasonal SMAP soil-moisture check", "each season"), ("plan", "Hold new irrigation spending", "this year")]),
  ("Assign scout", [("drone", "Drone scout of fields that lost greenness", "early summer"), ("crew", "Field scout visit", "early summer")]),
  ("Draft orders", [("plan", "Seed and input orders by predicted crop", "winter"), ("notice", "Confirm the plan with each grower", "winter")]),
 ],
}

# ---- concrete impact: before -> after for a named user and decision (qualitative; numbers are the real inputs) ----
BA = {
 "hotspots": [
  {"user": "Provincial fire duty officer", "decision": "Where and when to stage crews next season",
   "before": ["Two satellite records that don't compare: VIIRS sees about 5.6× more fire than MODIS since 2012", "Staffing set from last summer's headlines"],
   "after": ["One 2000–2025 fire calendar on a single scale, for any area", "Crews hired and staged in Alberta and B.C. before July, the peak month"],
   "geo": {"v": "+1,503/yr", "l": "Alberta detections, harmonized (p = 0.035, tentative)"}, "metric": {"v": "8.5%", "l": "lower error than the best baseline (2022–25)"}},
  {"user": "Community emergency planner", "decision": "When to put forest communities on notice",
   "before": ["Notice goes out once smoke is visible"],
   "after": ["Notice by late April, evacuation plans checked before May"],
   "geo": {"v": "5 of 16", "l": "unusual months in Alberta fell in May"}, "metric": {"v": "88.6%", "l": "interval coverage (target 90%)"}},
 ],
 "sar-change": [
  {"user": "Civil-protection duty officer", "decision": "Which districts to clear first after the storm",
   "before": ["Optical satellites see only cloud", "Districts ranked from calls and road reports"],
   "after": ["A water map from the first radar pass after the storm", "Districts inside the new-water footprint cleared first; l'Horta Sud walked on foot"],
   "geo": {"v": "77.7 km²", "l": "new water two days after the flood (NASA OPERA)"}, "metric": {"v": "66.4%", "l": "water IoU vs 21.8% for the standard threshold"}},
  {"user": "City drainage engineer", "decision": "What to build for next year",
   "before": ["Sized for an assumed rising trend in extreme rain"],
   "after": ["Sized for the 2024 extreme; the 45-year record shows no trend in the wettest day"],
   "geo": {"v": "p = 0.28", "l": "wettest-day rain, NASA POWER 1981–2025"}, "metric": {"v": "p = 0.62", "l": "GPM IMERG 1998–2024 agrees: no trend"}},
 ],
 "field-shift": [
  {"user": "Crop adviser, Story County, Iowa", "decision": "What to plant on each field next season",
   "before": ["Same hybrid and rotation as last year", "Season length assumed unchanged since the 1980s"],
   "after": ["Longer-season hybrid trialled on a strip, cover crop after harvest", "Steepest tiles moved into a cover-crop rotation first"],
   "geo": {"v": "+19 days", "l": "frost-free season vs 1981 (p = 0.006)"}, "metric": {"v": "0.8176", "l": "next-season crop accuracy (history alone 0.8136)"}},
  {"user": "Farmer", "decision": "Whether to spend on irrigation",
   "before": ["Irrigation bought against a drier future"],
   "after": ["Rain-fed plan kept, with a SMAP soil-moisture check each season"],
   "geo": {"v": "4 of 4", "l": "NASA water records show no trend"}, "metric": {"v": "0.811", "l": "pixel accuracy, full-county 2025 map"}},
 ],
}

def _mod_json(slug):
    from pathlib import Path
    f = Path(__file__).parent / "modules" / slug / "app.json"
    return json.loads(f.read_text()) if f.exists() else {}

# ---- alert drafts per action (SIMULATED in the dashboards: "Send" only writes to the on-page timeline) ----
ALERTS = {
 "hotspots": {
  0: {"channel": "Duty-officer alert · provincial fire centres", "to": "Alberta and B.C. wildfire duty officers", "area": "Alberta + British Columbia (outlined on the map)",
      "head": "Fire season staffing: Alberta and B.C. peak in July",
      "lines": ["Satellite fire detections are rising about 1,503 a year in Alberta and 2,587 a year in B.C. (2003–2025).",
                "If that trend line holds, a typical 2026 brings about 41,000 detections in Alberta and 72,000 in B.C. Single years swing far wider: 2023 brought 390,000 and 372,000.",
                "Ask: stage initial-attack crews before July and open seasonal hiring this spring."],
      "src": "NASA FIRMS MODIS + VIIRS, harmonized to the VIIRS scale; Sen slope trend line (not a weather forecast)."},
  1: {"channel": "Community notice · forest communities", "to": "Residents and councils of forest communities near the flagged May cells", "area": "Top May fire cells (pins on the map)",
      "head": "Fire season can start early: check your evacuation plan before May",
      "lines": ["5 of Alberta's 16 unusual fire months since 2000 were in May (2011, 2016, 2019, 2023, 2025), more than any other month.",
                "Know your evacuation route, keep a go-bag ready and sign up for your province's official alerts."],
      "src": "NASA FIRMS, Hot Spots burn calendar (robust z > 3.5 against each month's 2000–2025 median)."},
 },
}

def app_data(slug):
    """Everything a dashboard needs for OGC2.mount / OGC2.impact. src/modules/<slug>/app.json keys override."""
    A = APPS[slug]
    acts = []
    for i, r in enumerate(A["recs"]):
        verb, tasks = C2[slug][i] if i < len(C2[slug]) else ("Approve", [])
        acts.append({"id": f"{slug}-{i + 1}", "cls": r["cls"], "title": r["act"], "sat": r["sat"], "out": r["out"], "src": r["src"],
                     "verb": verb, "tasks": [{"asset": a, "label": l, "eta": t} for a, l, t in tasks]})
        if i in ALERTS.get(slug, {}): acts[-1]["alert"] = ALERTS[slug][i]
    d = {"slug": slug, "name": A["name"], "role": A["role"], "who": A["who"], "page": f"/{slug}/", "actions": acts, "impact": BA[slug],
         "metrics": [{"v": m[0], "t": m[1], "neg": len(m) > 2} for m in A["metrics"]]}
    d.update(_mod_json(slug))
    return d

def rec_card(r, i, compact=False, slug=None):
    verb = C2[slug][i][0] if slug and i < len(C2.get(slug, [])) else None
    cta = (f'<a class="btn rec-cta" href="/{slug}/app/#act={slug}-{i + 1}">{e(verb)} <span aria-hidden="true">→</span></a>' if verb else "")
    return (f'<article class="rec{" compact" if compact else ""}" style="--i:{i}">'
            + ("" if compact else f'<div class="rec-img"><img src="/assets/img/{r["img"]}" alt="" loading="lazy" width="1152" height="864" /></div>')
            + f'<div class="rec-body"><span class="rec-cls">{e(r["cls"])}</span>'
            f'<ol class="rec-flow"><li class="sat"><b>Satellite shows</b><span>{e(r["sat"])}</span></li>'
            f'<li class="act"><b>I will</b><span>{e(r["act"])}</span></li>'
            f'<li class="out"><b>Expected</b><span>{e(r["out"])}</span></li></ol>'
            f'<div class="rec-foot">{cta}<details class="rec-src"><summary>Evidence</summary><p>{e(r["src"])}</p></details></div></div></article>')

def recs_block(slug, compact=False):
    A = APPS[slug]
    return f'<div class="recs n{len(A["recs"])}">' + "".join(rec_card(r, i, compact, slug) for i, r in enumerate(A["recs"])) + "</div>"

def metrics_strip(slug):
    return '<ul class="mstrip">' + "".join(f'<li class="{m[2] if len(m) > 2 else ""}"><strong>{e(m[0])}</strong><span>{e(m[1])}</span></li>' for m in APPS[slug]["metrics"]) + "</ul>"

def impact_block(slug):
    I = APPS[slug]["impact"]
    tech = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in I["tech"])
    hum = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in I["human"])
    return (f'<div class="impact"><div class="imp tech"><p class="imp-k">From orbit</p><h3>What the satellites found</h3><ul>{tech}</ul></div>'
            f'<div class="imp-arrow" aria-hidden="true">→</div>'
            f'<div class="imp human"><p class="imp-k">On the ground</p><h3>What changes for people</h3><ul>{hum}</ul></div></div>'
            f'<p class="mstrip-k">Backed by the model and the trend tests · one seed, not a published benchmark</p>{metrics_strip(slug)}')

def guide_data():
    """JSON for the in-dashboard stepper."""
    out = {}
    for s in SLUGS:
        A = APPS[s]
        out[s] = {"name": A["name"], "role": A["role"], "who": A["who"], "guide": A["guide"],
                  "shows": [{"big": b, "line": l} for b, l, _ in A["shows"]],
                  "recs": [{k: r[k] for k in ("cls", "sat", "act", "out", "src", "img")} for r in A["recs"]],
                  "impact": A["impact"], "metrics": [{"v": m[0], "t": m[1], "neg": len(m) > 2} for m in A["metrics"]],
                  "page": f"/{s}/"}
    return out


def ba_html(items, title=None):
    """Server-rendered twin of OGC2.impact (same classes; styled by /shared/c2.css)."""
    def li(xs): return "".join(f"<li>{e(x)}</li>" for x in ([xs] if isinstance(xs, str) else xs))
    cards = "".join(
        f'<article class="c2-imp"><header><span class="c2-cls">{e(it["user"])}</span><h3>{e(it["decision"])}</h3></header>'
        f'<div class="c2-ba"><div class="c2-b"><p>Before</p><ul>{li(it["before"])}</ul></div><span class="c2-arrow" aria-hidden="true">→</span>'
        f'<div class="c2-a"><p>With this tool</p><ul>{li(it["after"])}</ul></div></div>'
        f'<footer><div><b>{e(it["geo"]["v"])}</b><span>{e(it["geo"]["l"])}</span></div><div><b>{e(it["metric"]["v"])}</b><span>{e(it["metric"]["l"])}</span></div></footer></article>'
        for it in items)
    return f'<div class="c2-impact" data-fx="rise">{f"<h3 class=c2-title>{e(title)}</h3>" if title else ""}<div class="c2-imp-grid">{cards}</div></div>'
