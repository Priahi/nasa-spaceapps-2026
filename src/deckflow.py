"""Home sections that follow the 7-slide deck, in more depth: hook -> imagine -> rewind (demo) -> flood what-if
-> fire -> fields -> one system. Numbers come from submission/impact.json + IMPACT.md + SPEAKER_NOTES.md (sourced there);
estimates are labelled illustrative, alerts and tasking simulated. No lives-saved claims."""
import json
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parent.parent
IMG = "/assets/img/home/"
CLIP = "/submission/clips/"

S = {  # label, url (all from IMPACT.md / SPEAKER_NOTES.md, fetched 14 Nov 2026)
  "aemet": ("AEMET event study", "https://www.aemet.es/documentos/es/conocermas/recursos_en_linea/publicaciones_y_estudios/estudios/estudio_28_oct_4_nov_2024.pdf"),
  "aemetn": ("AEMET normals 1981–2010, València", "https://www.aemet.es/es/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=8416&k=val"),
  "elpais": ("El País, 26 Oct 2025", "https://elpais.com/espana/2025-10-26/como-donde-y-a-que-hora-murieron-las-229-victimas-de-la-dana.html"),
  "newtral": ("Newtral", "https://www.newtral.es/avisos-dana/20241031/"),
  "opera": ("NASA/JPL OPERA DSWx-S1", "https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/"),
  "ccs": ("Consorcio de Compensación de Seguros", "https://consorsegurosdigital.com/en/numero-23/sumario/contributions/valencia_floods/"),
  "ivie": ("Ivie", "https://www.ivie.es/es_ES/la-dana-puede-haber-destruido-al-menos-el-20-de-los-85-900-millones-de-euros-de-activos-privados-y-publicos-localizados-en-los-municipios-inundados/"),
  "nhwc": ("NHWC 2006 (Day 1970 curve)", "https://water.usgs.gov/osw/pubs/Flood_Management_benefits_complete.pdf"),
  "gca": ("Global Commission on Adaptation 2019", "https://gca.org/wp-content/uploads/2019/09/GlobalCommission_Report_FINAL.pdf"),
  "papp": ("Pappenberger et al. 2015", "https://centaur.reading.ac.uk/40264/1/PappenbergerMonetaryBenefit.pdf"),
  "ahr": ("Rocha Silva et al. 2025, NHESS", "https://nhess.copernicus.org/articles/25/1501/2025/"),
  "undrr": ("UNDRR/WMO 2023", "https://www.undrr.org/reports/global-status-mhews-2023"),
  "esa": ("ESA (Copernicus EMS maps)", "https://www.esa.int/es/articles/about-us/directorates/earth-observation-programmes/devastating-floods-in-spain-witnessed-by-satellites"),
  "imerg": ("NASA GPM (IMERG latency)", "https://gpm.nasa.gov/resources/faq/what-determines-latency-imerg"),
  "vlc": ("Ajuntament de València, Recull 2024", "https://www.valencia.es/estadistica/Recull/Recull2024_Castellano.pdf"),
  "mnp17": ("MNP 2017, Horse River review", "https://open.alberta.ca/dataset/7cc619bd-56ce-488e-b007-cada28430589/resource/6c6560d3-0a8e-4550-b1d1-86e58409dea2/download/2016horseriverwildfirereview-mar2017.pdf"),
  "mnp25": ("MNP 2025, Alberta 2023 season", "https://open.alberta.ca/dataset/c8b32d6d-2b52-486d-a4f6-855ced2b9a71/resource/20e8af07-b2cd-43e4-b2e3-0eecbbd91a5b/download/pses-government-of-alberta-2023-spring-wildfire-post-incident-assessment-2025.pdf"),
  "ibc": ("Insurance Bureau of Canada", "https://www.newswire.ca/news-releases/northern-alberta-wildfire-costliest-insured-natural-disaster-in-canadian-history-585872181.html"),
  "twn": ("The Weather Network, 19 Jan 2024", "https://www.theweathernetwork.com/en/news/nature/outdoors/alberta-to-fully-staff-wildfire-crew-earlier-following-a-record-breaking-season"),
  "stocks": ("Stocks et al. 2002", "https://sites.ualberta.ca/~flanniga/publications/2003%20Stocks%20et%20al.%20J%20Geophys%20Res%20-%20Large%20forest%20fires.pdf"),
  "afp": ("Alberta Forestry and Parks Annual Report 2023–24", "https://open.alberta.ca/dataset/2dedbb29-e005-4802-bf6e-03bf77536add/resource/b86465e8-a8e3-45de-91d8-3fec19c700db/download/fp-annual-report-2023-2024.pdf"),
  "statcan": ("Statistics Canada, 2021 Census (Toronto)", "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?Lang=E&DGUIDlist=2021A00053520005"),
  "firms": ("NASA FIRMS", "https://www.earthdata.nasa.gov/data/tools/firms/faq"),
  "nass12": ("USDA NASS Crop Production 2012", "https://esmis.nal.usda.gov/sites/default/release-files/k3569432s/8s45qb85z/12579v877/CropProdSu-01-11-2013.pdf"),
  "fsa": ("USDA FSA prices", "https://www.fsa.usda.gov/sites/default/files/documents/2016_mya.pdf"),
  "sare": ("SARE/CTIC 2012–13 survey", "https://www.sare.org/wp-content/uploads/SARE-CTIC-CC-Survey-Report-V2.8.pdf"),
  "isu": ("Plastina et al. 2018, Iowa State", "https://www.card.iastate.edu/files/inline-files/plastina-180309.pdf"),
  "cdl": ("USDA NASS CDL FAQ", "https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php"),
  "pp": ("NASS Prospective Plantings, 31 Mar 2026", "https://release.nass.usda.gov/reports/pspl0326.pdf"),
}
def src(*ks, lead="Sources"):
    return f'<p class="dk-src"><span>{lead}:</span> ' + " · ".join(f'<a href="{S[k][1]}" rel="noopener">{e(S[k][0])}</a>' for k in ks) + "</p>"

def _view():
    p = ROOT / "src" / "impact_view.json"
    return json.loads(p.read_text()) if p.exists() else {}
def _imp():
    p = ROOT / "submission" / "impact.json"
    return json.loads(p.read_text()) if p.exists() else {}

def loop(name, poster, label, cap, cls="", webm=True):
    """Muted looping clip. No src until it nears the viewport (site.js), preload=none, poster first."""
    srcs = (f'<source data-src="{CLIP}{name}.webm" type="video/webm" />' if webm else "") + f'<source data-src="{CLIP}{name}.mp4" type="video/mp4" />'
    return (f'<figure class="dk-vid {cls}"><video class="lazyv" data-auto muted loop playsinline preload="none" poster="{IMG}{poster}.webp" width="1440" height="720" aria-label="{e(label)}">{srcs}</video>'
            f'<figcaption>{cap} <a class="dk-dl" href="{CLIP}{name}.mp4">MP4</a></figcaption></figure>')

def clip(name, poster, label, cap, secs):
    """Full app walkthrough: click to play (no autoplay), preload=none."""
    return (f'<figure class="dk-vid dk-clip"><video controls muted playsinline preload="none" poster="{IMG}{poster}.webp" width="1920" height="1080" aria-label="{e(label)}">'
            f'<source src="{CLIP}{name}.mp4" type="video/mp4" /></video><figcaption><span class="mono">Full walkthrough · {secs} s · no sound</span> {cap} <a class="dk-dl" href="{CLIP}{name}.mp4">MP4</a></figcaption></figure>')

def pic(name, alt, w, h, cap="", small=False, cls=""):
    ss = f' srcset="{IMG}{name}-640.webp 640w, {IMG}{name}.webp {w}w" sizes="(max-width: 700px) 100vw, 60vw"' if small else ""
    return (f'<figure class="dk-pic {cls}"><img src="{IMG}{name}.webp"{ss} alt="{e(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async" />'
            + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")

def stat(big, line, tone=""):
    return f'<div class="dk-stat {tone}"><b>{big}</b><span>{line}</span></div>'

def table(head, rows, cap=""):
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    tr = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="table-wrap dk-tw" tabindex="0" role="region" aria-label="{e(cap or head[0])} (table)"><table class="dk-t{" wide" if len(head) > 4 else ""}">{f"<caption>{cap}</caption>" if cap else ""}<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

def compare(key, us="Orbit to Ground"):
    rows = _view().get(key, {}).get("compare", [])
    if not rows: return ""
    return ('<div class="dk-cmp">' + "".join(f'<article><p class="eyebrow">{e(a)}</p><p>{e(b)}</p><p class="dk-us"><b>{us}:</b> {e(c)}</p></article>' for a, b, c in rows) + "</div>")

def tag(t, cls="sim"): return f'<span class="dk-tag {cls} mono">{e(t)}</span>'

def sec_head(n, kicker, title, lede=""):
    return (f'<div class="dk-head" data-fx="rise"><p class="eyebrow"><span class="dk-n mono">{n} / 7</span> {e(kicker)}</p><h2>{title}</h2>'
            + (f'<p class="lede">{lede}</p>' if lede else "") + "</div>")

# ---------- 1 · hook ----------
def hero():
    return f"""<section class="hero dk-hero" id="hook"><div class="topo-hero" aria-hidden="true"></div><div class="wrap dk-hero-grid">
<div class="dk-hero-copy">
<p class="chip"><i></i>NASA Space Apps 2026 · Be An Earth System Trend Detective!</p>
<p class="eyebrow">Valencia, Spain · 29 Oct 2024</p>
<h1>About <span class="grad">230 people</span> died because of one day of rain.</h1>
<div class="dk-hero-stats">
{stat("150+", "were already dead when the phone alert went out, around 8 PM", "hot")}
{stat("~1.6 yrs", "of València's rain fell on one town in a single day (~770 mm, about 2½ feet)")}
{stat("12 hours", "from the red weather warning, around 7:30 AM, to that phone alert")}
</div>
<p class="lede">The rain was measured from orbit as it fell. What no one had was a map that turned it into an alert for each town. Orbit to Ground turns NASA satellite data into that next move, for floods, fire and farms.</p>
<div class="actions"><a class="btn" href="#night">Start the story &darr;</a><a class="btn ghost" href="#rewind">&#9654; Watch the 30-second demo</a><a class="btn ghost" href="/sar-change/app/#demo">Open the flood app</a></div>
{src("aemet", "aemetn", "newtral", "elpais")}
</div>
<figure class="dk-hero-map"><img src="{IMG}hero-flood-map.webp" srcset="{IMG}hero-flood-map-640.webp 640w, {IMG}hero-flood-map.webp 900w" sizes="(max-width: 959px) 92vw, 40vw" alt="Radar flood map of the Valencia area, 31 October 2024: new surface water in blue across 8 towns including València, Catarroja, Sollana and Sueca." width="900" height="953" fetchpriority="high" decoding="async" />
<figcaption>Radar flood map, 31 Oct 2024, 8 towns · NASA/JPL OPERA DSWx-S1, from our flood app</figcaption></figure>
</div></section>"""

def bridge():
    return f"""<section class="section tight dk-bridge"><div class="wrap" data-fx="rise">
<p class="eyebrow">The rain was on the record</p>
<h2>NASA's satellites logged <span class="grad">~90 mm</span> upstream that day.</h2>
<p class="lede">What no one had was a map that turned it into an alert for Elena's town. So rewind the same night, with the same data.</p>
<p class="dk-src"><span>Rain:</span> NASA GPM IMERG V07 (91 mm upstream mean, 29 Oct) · cloud: NASA POWER (99%)</p>
</div></section>"""

# ---------- 3 · rewind ----------
def rewind_intro():
    return f"""<section class="section dk-sec" id="rewind"><div class="wrap">
{sec_head(3, "Story 1 · rewind, with Orbit to Ground", "Rewind. Same night, same data, with Orbit to Ground.", "The official 30-second demo starts by itself, muted, when you reach it. Captions are on; turn on sound with the button or the controls.")}
<div class="dk-demo-grid">
<figure class="dk-vid dk-demo"><video id="demoVideo" class="lazyv" data-auto data-once controls muted playsinline preload="none" poster="{IMG}p-demo.webp" width="1920" height="1080" aria-label="Official demo, 30 seconds: the Valencia flood rewound in the flood app, then fire and farms.">
<source data-src="/submission/demo.mp4" type="video/mp4" /><track kind="captions" srclang="en" label="English" src="/submission/demo.en.vtt" default /></video>
<button type="button" class="dk-unmute" aria-pressed="false">&#128263; Unmute</button>
<figcaption><span class="mono">Official demo · 30 s · captions</span> <a href="/submission/demo.mp4">MP4</a> · <a href="/submission/demo.en.srt">Captions (SRT)</a></figcaption></figure>
<div class="dk-stills">
{pic("flood-change", "Flood app, What changed: +47.0 km² more flood water in five days, 26 to 31 Oct 2024; most newly wet ground in Sueca (+24.1 km²), Sollana (+10.6) and València (+6.1).", 800, 800, "① Same map · what changed: +47 km² of flood water in five days")}
{pic("flood-act", "Flood app, Evacuate and flag: an evacuation alert to 8 municipalities, rescue teams to Sueca and València, and the next Sentinel-1 radar pass pulled. Simulated.", 800, 800, "② Same map · actions " + tag("Simulated"))}
</div></div>
<p class="dk-quote" data-fx="rise">Elena could have had a drafted alert for her town hours before the ~8 PM phone alert.</p>
<p class="fine center">Hypothetical rewind on archive data · alerts and tasking are simulated · no claim about lives saved.</p>
</div></section>"""

def rewind_loops():
    L = [("loop-flood-slider", "p-flood-slider", "Flood app: dragging the date slider from 26 to 31 October as new water appears.", "Slide through the radar passes"),
         ("loop-flood-classify", "p-flood-classify", "Flood app: What changed classifies each pixel as newly wet, wet on both dates or dried out.", "What changed, pixel by pixel"),
         ("loop-flood-actions", "p-flood-actions", "Flood app: action cards preview where each team goes on the map.", "Preview each action on the map"),
         ("loop-flood-task", "p-flood-task", "Flood app: dispatch moves through queued, tasked, in progress and done. Simulated.", "Dispatch to done " + tag("Simulated")),
         ("loop-flood-alert", "p-flood-alert", "Flood app: Alert everyone opens a drafted alert to 8 towns, then Send. Simulated, nothing is sent.", "Alert everyone, then send " + tag("Simulated"))]
    g = "".join(loop(n, p, l, c) for n, p, l, c in L)
    return f"""<section class="section tight dk-sec"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">Inside the flood app</p><h2>Five moves, recorded on the live app.</h2></div><p>Each clip loops while it's on screen and stops when you scroll past. Real NASA and ESA data; the alert and dispatch are simulated.</p></div>
<div class="dk-loops">{g}</div>
{clip("sar-change", "p-sar", "Full walkthrough of the SAR Change flood app, 40 seconds, no sound.", "The flood app end to end.", 40)}
<div class="actions center"><a class="btn launch" href="/sar-change/app/#demo">Try the rewind yourself</a><a class="btn ghost" href="/sar-change/">The flood project</a></div>
</div></section>"""

# ---------- 4 · flood what-if ----------
def flood_whatif():
    F = _imp().get("flood", {}); sc = F.get("scenarios", [])
    tl = "".join(f'<li class="{c}"><b>{t}</b><span>{l}</span></li>' for t, l, c in [
        ("~7:30 AM", "Red warning. The danger is known.", ""), ("~8 AM", "What if: the town alert goes out 12 h earlier, drafted by the dashboard " + tag("Simulated"), "us"),
        ("~noon", "First recorded death, a driver at the Benimodo ravine.", "hot"), ("~8 PM", "The real phone alert. More than 150 already dead.", "hot")])
    names = {6: "~2 PM, 29 Oct", 12: "~8 AM, 29 Oct", 24: "~8 PM, 28 Oct", 48: "~8 PM, 27 Oct"}
    lands = {6: "before nearly all of the deaths dated before ~8 PM", 12: "before the first recorded death (~noon)", 24: "before the rain peak; relies on forecasts, not our signal", 48: "before the rain; forecast-based"}
    rows = [[f'{s["hours_earlier"]} h earlier', names.get(s["hours_earlier"], ""), lands.get(s["hours_earlier"], ""), f'{round(s["factor"] * 100)}%' + (f' ({round(s["factor_range"][0]*100)}–{round(s["factor_range"][1]*100)}%)' if s.get("factor_range") else ""),
             f'€{s["avoided_insured_eur_bn"]:.2f} bn', f'€{s["avoided_assets_eur_bn"]:.1f} bn'] for s in sc]
    tbl = table(["Alert sent", "Clock time", "When it lands", "Damage avoidable", "of €4.8 bn insured", "of €17 bn assets"], rows,
                "Illustrative upper bound: assumes everyone got the alert and acted. The curve levels off after about a day; it does not add 30% per day.") if rows else ""
    return f"""<section class="section dk-sec" id="whatif"><div class="wrap">
{sec_head(4, "Story 1 · what if it had been there?", "12 hours earlier = an alert before the first death.")}
<div class="dk-big2" data-fx="stagger">
<div class="dk-mega"><b>€4.8 bn</b><span>insured loss in the Valencia floods, about €19,000 for each of ~250,000 claims (Consorcio de Compensación de Seguros)</span></div>
<div class="dk-mega us"><b>≈ €1.1 bn</b><span>within reach of an alert 12 hours earlier, from published warning curves {tag("Illustrative estimate", "est")}</span></div>
</div>
<div class="dk-two">
<div><h3 class="dk-h3">The same morning, with the alert moved up</h3><ol class="dk-tl">{tl}</ol></div>
<div><h3 class="dk-h3">How we estimated</h3><p>Published curves: <b>13%</b> of flood damage avoidable with 6 hours of warning, <b>22%</b> at 12 h, <b>30%</b> at 24 h, and <b>~33%</b> at 48 h. Then it levels off. 22% × €4.8 bn ≈ €1.1 bn. The ~78 km² of new water is more than half the area of the city of València.</p>
<p class="fine">No lives number for Valencia. We quote one for a different flood: in a peer-reviewed simulation of Germany's 2021 Ahr Valley flood, timely warnings with fast evacuation cut modelled deaths by up to 80%. We don't apply it here.</p></div>
</div>
{tbl}
<h3 class="dk-h3">How it compares with what exists today</h3>
{compare("flood")}
<details class="deep"><summary>Hours for the alert, days for the map</summary><ul class="facts">
<li><b>Hours, for the alert.</b> The danger was known: AEMET's red warning came around 7:30 AM and EFAS had sent notices on 26 and 28 Oct. The 12-hour case needs no new detection. It needs that signal turned into a drafted, town-specific alert with the right instructions. That is what the dashboard does (simulated).</li>
<li><b>Days, for the map.</b> It was 99% cloudy, so optical satellites were blind. The first post-storm radar map came on 31 Oct, about 2 days later; the first province-wide Copernicus map on 2 Nov, about 4 days later. The rain signal arrives before either. NISAR adds more radar passes for the next event.</li>
<li><b>What we haven't tested.</b> Near-real-time IMERG timing on this event (we used the research run). The 24 h and 48 h rows rely on forecasts, which our tool doesn't make.</li></ul></details>
{src("ccs", "ivie", "nhwc", "gca", "papp", "elpais", "newtral", "esa", "imerg", "ahr", "vlc")}
</div></section>"""

# ---------- 5 · fire ----------
def fire():
    return f"""<section class="section dk-sec" id="fire"><div class="wrap">
{sec_head(5, "Story 2 · Hot Spots · wildfire", "Fire: staff crews from the record, not a fixed date.", "A wildfire duty officer in Alberta plans in winter. The 26-year satellite record says May is the month to watch.")}
<div class="dk-media2">
{pic("fire-map", "Hot Spots app, Canada burn history: satellite fire detections per year, 2003–2025 average, on a 0.25° grid; the boreal belt from British Columbia through Alberta and Saskatchewan glows brightest.", 1400, 916, "Canada burn history · fires per year, 2003–2025 · NASA FIRMS MODIS + VIIRS on one scale, 0.25° squares", small=True, cls="dk-wide")}
{loop("deck-fire-map", "p-fire-map", "Hot Spots app: full Canada, the boreal belt, a pan from British Columbia into Alberta, the burn calendar flagging May, then Assign crews (simulated).", "In the app: burn history → calendar flags May → Assign crews " + tag("Simulated"))}
</div>
<div class="dk-stats3" data-fx="stagger">
{stat("~1,500", "more fires detected in Alberta each year than the year before (2003–2025 trend, p = 0.035, tentative)")}
{stat("+16 days", "of full readiness: crews staffed 15 April instead of 1 May")}
{stat("~65,000 ha + ~$25 M", "of forest and firefighting cost spared per escaped fire stopped " + tag("Illustrative", "est"), "us")}
</div>
<p class="dk-quote small" data-fx="rise">Each escaped May fire stopped spares an area about the size of the City of Toronto.</p>
<div class="dk-two">
<div><h3 class="dk-h3">Why May</h3><ul class="facts"><li><b>The record.</b> 5 of Alberta's 16 unusual fire months since 2000 were in May, including 2016 (Horse River, Fort McMurray) and 2023. B.C. rises too, about +2,600 a year (p = 0.045).</li>
<li><b>The date.</b> Alberta staffed fully by 1 May; for 2024 it moved to 15 April. Horse River started on 1 May 2016: 0 days of margin. In 2023 the first big fire came on 23 April, before full staffing.</li>
<li><b>Why the start matters.</b> About 97% of Canadian fires are held small; the 3% that escape burn 97% of the area.</li></ul></div>
<div><h3 class="dk-h3">How we estimated</h3>{table(["Step", "Value"], [["Alberta 2023 fires × 3% escaped", "1,088 × 3% ≈ 33 escapes"], ["97% of 2.2 M ha ÷ 33", "≈ 65,000 ha per escape"], ["$851 M wildfire cost ÷ 2.2 M ha", "≈ $385 per ha"], ["$385 × 65,000 ha", "≈ $25 M per escape"], ["65,000 ha vs Toronto (631 km²)", "≈ 1.04 ×"]])}
<p class="fine">An assumption, not a finding: we found no source linking staffing dates to escape rates, so the number of escapes stopped is the input you vary. In 2016 initial attack on Horse River was immediate; we don't claim earlier crews could have stopped it.</p></div>
</div>
<h3 class="dk-h3">How it compares with what exists today</h3>
{compare("fire")}
{clip("hotspots", "p-hotspots", "Full walkthrough of the Hot Spots fire app, 26 seconds, no sound.", "The fire app end to end.", 26)}
<div class="actions center"><a class="btn launch" href="/hotspots/app/#demo">Open Hot Spots</a><a class="btn ghost" href="/hotspots/app/#view=canada">Full Canada map</a><a class="btn ghost" href="/hotspots/">The fire project</a></div>
{src("firms", "mnp17", "mnp25", "twn", "stocks", "afp", "statcan", "ibc")}
</div></section>"""

# ---------- 6 · fields ----------
def fields():
    return f"""<section class="section dk-sec" id="fields"><div class="wrap">
{sec_head(6, "Story 3 · Field Shift · farms", "Fields: next season's crop map, before planting.", "A farm adviser in Story County, Iowa, decides in winter where winter rye goes. The model maps next season's crop for every 30 m square.")}
<div class="dk-media2">
{pic("field-map", "Field Shift app: Story County, Iowa, 2025 crop classification at 30 m: corn in yellow, soybean in green, with grass, hay and small grain.", 1380, 846, "Story County, Iowa · crop map, 30 m · corn, soybean, grass, hay, small grain · USDA NASS CDL labels", small=True, cls="dk-wide")}
{loop("loop-field-walk", "p-field-walk", "Field Shift app: slope map, Act: winter rye on the 92 steepest squares, task queue, then What if? about $1.2 M. Simulated.", "In the app: slope map → winter rye → task → What if? " + tag("Simulated"))}
</div>
<div class="dk-stats3" data-fx="stagger">
{stat("~$1.2 M", "net in a 2012-type drought from winter rye on the steepest squares " + tag("Illustrative", "est"), "us")}
{stat("26,500 acres", "≈ 10,700 ha of the most erosion-prone farmland protected")}
{stat("Before planting", "our map is ready in February; USDA's for that season arrives ~11 months later")}
</div>
<p class="dk-quote small" data-fx="rise">Rye on the steepest fields costs a little most years and pays back in a dry one: drought insurance.</p>
<div class="dk-two">
<div><h3 class="dk-h3">How we estimated</h3>{table(["Item", "Per acre", "× 26,500 acres"], [["Extra corn in a 2012-type drought: 11.1 bu × $6.89", "+$76", "+$2.0 M"], ["Rye seed + planting (Iowa mean)", "−$32", "−$0.85 M"], ["<b>Net in a drought year</b>", "<b>+$44</b>", "<b>≈ +$1.2 M</b>"], ["In a normal year", "usually negative", "–"]])}
<p class="fine">The yield gain is a national, self-reported farmer survey from 2012, not a trial; Iowa results will differ. The 67% lower erosion figure is a planning score from our model, not measured soil loss.</p></div>
<div><h3 class="dk-h3">What the model gets right, and where it doesn't</h3><ul class="facts"><li><b>81.8%</b> of 30 m squares get the right next crop on held-out 2024–25 data, against 81.4% from crop history alone: a small edge, one county, one seed.</li>
<li><b>Climate is shifting.</b> The frost-free season is about 19 days longer than in 1981 (p = 0.006). Summer soil water shows no trend, and we say so.</li>
<li><b>2012 was costly.</b> Iowa corn fell from 172 to 137 bushels an acre (−20%).</li></ul></div>
</div>
<h3 class="dk-h3">How it compares with what exists today</h3>
{compare("field")}
{clip("field-shift", "p-field", "Full walkthrough of the Field Shift farm app, 25 seconds, no sound.", "The farm app end to end.", 25)}
<div class="actions center"><a class="btn launch" href="/field-shift/app/#demo">Open Field Shift</a><a class="btn ghost" href="/field-shift/">The farms project</a></div>
{src("nass12", "fsa", "sare", "isu", "cdl", "pp")}
</div></section>"""

# ---------- 7 · system ----------
def system(sec_built, sec_fut, mstrip):
    return f"""<section class="section dk-sec" id="system"><div class="wrap">
{sec_head(7, "One system · how it works", "Shared NASA inputs, one engine, one loop: signal → map → alert → task.")}
<ol class="eng-flow mono dk-flow" aria-label="The decision loop"><li>Signal</li><li>Map</li><li>Alert {tag("Simulated")}</li><li>Task {tag("Simulated")}</li></ol>
<figure class="dk-pic dk-arch"><a href="{IMG}arch-system.webp"><img src="{IMG}arch-system.webp" srcset="{IMG}arch-system-640.webp 640w, {IMG}arch-system.webp 1800w" sizes="(max-width: 1120px) 100vw, 1120px" alt="System diagram. Shared inputs: radar (Sentinel-1), thermal (NASA FIRMS), rain (GPM IMERG and NASA POWER), optical (HLS and Sentinel-2 with CDL labels) and water (GRACE and GLDAS). One engine: Mann-Kendall and Sen's slope trend detection plus per-signal models (U-Net water, fire range model, next-season crop model). Decision loop: signal, map, alert, task. Outputs per vertical: flood water map and town alert, fire burn calendar and staffing, farms crop map and rye list, and trends for all three." width="1800" height="770" loading="lazy" decoding="async" /></a>
<figcaption>Inputs → one engine → the decision loop → results per sector. Larger per-model diagrams are under the hood.</figcaption></figure>
<p class="mstrip-k">Results · one seed per run, not a published benchmark</p>{mstrip}
<h3 class="dk-h3">Same engine, every sector</h3>
<div class="x20-grid" data-fx="stagger">{sec_built}</div>
<div class="x20-grid fut" data-fx="stagger">{sec_fut}</div>
<p class="dk-credit">Parsa Riahi · built solo · Toronto</p>
<p class="fine center">Civil uses only · tasking and alerts are simulated · not affiliated with NASA</p>
</div></section>"""

def deck_links(strip):
    return f"""<section class="section tight dk-sec" id="deck"><div class="wrap">
<div class="split-head" data-fx="rise"><div><p class="eyebrow">The deck</p><h2>Seven slides, with video inside.</h2></div><p>The same story in seven slides. The PowerPoint version plays the demo and the walkthrough loops on its own.</p></div>
<div class="actions"><a class="btn" href="/submission/deck.html">Open the deck</a><a class="btn ghost" href="/submission/deck.pptx" download>Slides with video (PPTX)</a><a class="btn ghost" href="/submission/deck.pdf">Slides (PDF)</a><a class="btn ghost" href="/slides/">Slide images</a></div>
{strip}
</div></section>"""
