"""Story-led home page (coach structure): hook -> her night -> rewind -> fire -> times twenty.
Every fact comes from submission/STORY.md or the repo's own data files. Elena is an illustrative composite."""
import json
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parent.parent
SRC = {
  "aemet": ("AEMET", "https://www.aemet.es/documentos/es/conocermas/recursos_en_linea/publicaciones_y_estudios/estudios/estudio_28_oct_4_nov_2024.pdf"),
  "ecmwf": ("ECMWF", "https://www.ecmwf.int/en/newsletter/183/news/extreme-precipitation-spains-valencia-region"),
  "elpais": ("El País", "https://elpais.com/espana/2025-10-26/como-donde-y-a-que-hora-murieron-las-229-victimas-de-la-dana.html"),
  "newtral": ("Newtral", "https://www.newtral.es/avisos-dana/20241031/"),
  "reuters": ("Reuters", "https://www.reuters.com/business/environment/spains-flood-disaster-was-its-worst-recent-history-heres-what-went-wrong-2024-11-09/"),
  "norm": ("AEMET/WMO 1991–2020 normals, València", "https://www.nodc.noaa.gov/archive/arc0216/0253808/2.2/data/0-data/Region-6-WMO-Normals-9120/Spain/CSV/VALENCIA_8285.csv"),
  "aemetn": ("AEMET normals", "https://www.aemet.es/es/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=8416"),
  "vlc": ("Ajuntament de València, Recull 2024", "https://www.valencia.es/estadistica/Recull/Recull2024_Castellano.pdf"),
  "lv": ("La Vanguardia", "https://www.lavanguardia.com/local/valencia/20250409/10568338/emergencias-juzgado-18-43-chj-comunico-gran-crecida-barranco-poyo.html"),
}
def src(*ks): return '<span class="hs-src">Source: ' + ", ".join(f'<a href="{SRC[k][1]}" rel="noopener">{e(SRC[k][0])}</a>' for k in ks) + "</span>"

def tcard(time, label, big, unit, line, srcs, tone="", exact=""):
    return (f'<figure class="sv-fig hs-time {tone}"><p class="mono">{e(label)}</p><strong>{e(time)}</strong>'
            f'<div class="hs-big"><b>{e(big)}</b><span>{e(unit)}</span></div><p>{e(line)}</p>{src(*srcs)}{f'<span class="hs-src">Exact: {e(exact)}</span>' if exact else ""}</figure>')

def rain_svg():
    d = json.loads((ROOT / "demos/sar-change/ops/rain.json").read_text())["days"]
    W, H, l, r, t, b = 640, 330, 46, 14, 34, 40
    mx = 140; bw = (W - l - r) / len(d); out = ""
    for gv in (0, 50, 100):
        y = H - b - (H - b - t) * gv / mx
        out += f'<line x1="{l}" x2="{W-r}" y1="{y:.1f}" y2="{y:.1f}" class="g"/><text x="{l-6}" y="{y+4:.1f}" text-anchor="end">{gv}</text>'
    y50 = H - b - (H - b - t) * 50 / mx
    out += f'<line x1="{l}" x2="{W-r}" y1="{y50:.1f}" y2="{y50:.1f}" class="rule"/><text x="{W-r}" y="{y50-6:.1f}" text-anchor="end" class="rule-t">50 mm example rule</text>'
    for i, x in enumerate(d):
        h = (H - b - (H - b - t) * 0) - (H - b - (H - b - t) * x["mean"] / mx); xx = l + i * bw
        hot = x["d"] == "2024-10-29"
        out += f'<rect class="{"hot" if hot else "bar"}" x="{xx+1.5:.1f}" y="{H-b-h:.1f}" width="{bw-3:.1f}" height="{max(h,1):.1f}" rx="2"><title>{x["d"]}: {x["mean"]} mm mean, {x["max"]} mm wettest cell, {x["cloud"]}% cloud</title></rect>'
        if hot: out += f'<text class="val" x="{xx+bw+4:.1f}" y="{H-b-h+12:.1f}">29 Oct · 91.0 mm</text>'
        if x["d"] in ("2024-10-15", "2024-10-29", "2024-11-12"):
            out += f'<text x="{xx+bw/2:.1f}" y="{H-b+18}" text-anchor="middle">{int(x["d"][8:])} {"Oct" if x["d"][5:7]=="10" else "Nov"}</text>'
    return (f'<figure class="sv-fig hs-rain"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Daily rain upstream of Valencia, mm, 15 Oct to 20 Nov 2024. 29 October: 91 mm mean.">'
            f'<text x="{l}" y="18" class="cap">Daily rain upstream, mm · NASA GPM IMERG</text>{out}</svg>'
            '<figcaption>Mean over the upstream box. The wettest 10 km cell got 135.1 mm. Cloud cover that day: 99%. The 50 mm line is a design example, not a tested rule.</figcaption></figure>')

def alert_card(al):
    lines = "".join(f"<li>{e(x)}</li>" for x in al["lines"])
    return (f'<figure class="sv-fig hs-alert"><p class="hs-sim mono">Simulated · nothing is sent</p><p class="mono">{e(al["channel"])}</p>'
            f'<h4>{e(al["head"])}</h4><p class="to"><b>To:</b> {e(al["to"])}</p><ul>{lines}</ul><p class="fine">{e(al["src"])}</p>'
            '<span class="hs-send" aria-hidden="true">Approve and send (simulated)</span></figure>')

def dispatch_card():
    rows = [("Rescue teams", "to the 8 flagged towns", "now"), ("Next radar pass", "queued for the flooded area", "next pass"),
            ("Damage teams + drones", "l'Horta Sud streets, where radar maps only 0.48 km² across 8 towns", "day 2"),
            ("Farm aid", "Albufera paddy towns", "after")]
    li = "".join(f'<li><b>{e(a)}</b><span>{e(b)}</span><em class="mono">{e(c)}</em></li>' for a, b, c in rows)
    return f'<figure class="sv-fig hs-disp"><p class="hs-sim mono">Simulated tasking</p><ol>{li}</ol></figure>'

def towns_card():
    towns = ["Sueca", "València", "Sollana", "Silla", "Alfafar", "Catarroja", "Cullera", "Massanassa"]
    li = "".join(f'<li class="{"her" if t == "Catarroja" else ""}">{e(t)}</li>' for t in towns)
    return f'<ul class="hs-towns">{li}</ul>'

def home_sections(story, slider, alert):
    night = story("night", "The flood · Valencia, 29 October 2024", "Imagine losing someone you love because no one knew how much rain was coming that day.",
      "Elena is the emergency coordinator in Catarroja, one of the 8 towns where radar later mapped flood water. She is an illustrative composite: her day follows the public timeline, not a real person.",
      [("About 7:30 AM · Warning", "A red warning, but no map.", "<p>The weather agency, AEMET, issues a red warning for Valencia. Elena has a forecast for the region. She has no picture of where the water will go.</p>",
        tcard("~7:30 AM", "29 Oct · CET", "Red", "warning for Valencia", "The highest level of weather warning.", ("aemet", "newtral"), exact="Red warning issued 7:36 AM CET.")),
       ("Around noon · Rain", "Upstream, the ravine stirs.", "<p>Inland at Turís, 771.8 mm of rain falls in 24 hours: <b>about 2.5 feet of water, 1.7 times what València gets in an average year</b> (457.9 mm). 184.6 mm (7.3 inches) falls in a single hour. The Poyo ravine passes its pre-alert level, 264 m³/s, around noon.</p>" + '<p class="fine">' + src("aemet", "lv", "aemetn", "norm") + "</p>",
        rain_svg()),
       ("About 7 PM · Surge", "The surge.", "<p>By about 7 PM the Poyo carries 1,686 m³/s, then 2,282 m³/s minutes later. More than six times the noon pre-alert level.</p>",
        tcard("~7 PM", "Poyo ravine · flow", "1,686", "m³/s", "2,282 m³/s minutes later.", ("lv",), "hot", exact="Gauge readings at 6:43 PM and 6:55 PM CET.")),
       ("About 8 PM · Alert", "The phones buzz at about 8 PM.", "<p>The ES-Alert reaches phones after a 12-hour gap from the red warning. By then, more than 150 of the people who died had already died. The 112 emergency line took more than 15,000 calls.</p>",
        tcard("~8 PM", "ES-Alert to phones", "12 h", "gap after the red warning", "About 230 deaths in the Valencia region.", ("elpais", "reuters"), "hot", exact="ES-Alert sent 8:11 PM CET, 12 h 35 min after the 7:36 AM red warning; at least 156 of 229 deaths before it; 15,943+ calls to 112."))])
    rewind = story("rewind", "Now rewind · the same night, with NASA data", "What Elena could have seen.",
      "Four steps, each shown in the live flood dashboard. Real satellite data; the alert and tasking are simulated.",
      [("29 Oct · Rain", "1. A rain signal upstream.", "<p>NASA's GPM IMERG measures <b>91 mm</b> of rain upstream that day (a fifth of València's average year, in one day), almost nine times the wettest day of the fortnight before (10.4 mm). Cloud cover is <b>99%</b>, so ordinary cameras in orbit see nothing below.</p>"
        "<p class=\"fine\">A rule like “flag 50 mm upstream” is a design example. We haven't tested near-real-time timing.</p>",
        '<figure class="sv-fig hs-time"><p class="mono">NASA GPM IMERG · 29 Oct, upstream</p><strong>91 mm</strong><div class="hs-big"><b>99%</b><span>cloud cover</span></div><p>135.1 mm in the wettest 10 km cell. Ordinary optical satellites see nothing through that cloud. Radar can.</p><span class="hs-src">Rain chart above: the same NASA record, day by day.</span></figure>'),
       ("31 Oct · Radar", "2. Radar sees through cloud.", "<p>NASA/JPL OPERA radar maps <b>77.7 km²</b> of new water, up from 30.7 km² (+47.0): <b>more than half the area of the city of València</b> (134.65 km²). 75.8 km² of it is in 8 towns, Catarroja among them.</p>"
        "<p>On held-out flood scenes, our own radar model scores 66.4% IoU, 3× a standard threshold method (21.8%).</p>" + towns_card() + '<p class="fine">' + src("vlc") + "</p>",
        slider("opera-before.webp", "opera-after.webp", "26 Oct 2024", "31 Oct 2024")),
       ("Simulated · Alert", "3. A drafted alert for her town.", "<p>The dashboard drafts one alert to all 8 towns: where the water is, the rain upstream, and what to do. Elena reviews it and approves.</p>", alert),
       ("Simulated · Dispatch", "4. The next move, for every team.", "<p>Rescue teams go to the flagged towns. The next radar pass is queued. Drones go to the streets radar can't see. Farm aid goes to the rice towns by the Albufera.</p>", dispatch_card())])
    return night, rewind

CSS = ""
