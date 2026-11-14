"""Model architecture figures for 'Under the hood': inputs -> model -> outputs -> results, with sources.
Paper-style figure look (light ground, thin ink, toned boxes). Numbers from src/recs.py metrics / STORY.md."""
from html import escape as e

TONE = {"sar": "blue", "thermal": "orange", "rain": "violet", "optical": "green"}
PIPES = [
 ("Flood · SAR Change", [("sar", "SAR radar", "Sentinel-1 RTC (ASF DAAC)"), ("sar", "Surface water", "NASA/JPL OPERA DSWx-S1"), ("rain", "Precipitation", "NASA GPM IMERG V07")],
  ("U-Net segmentation", ["trained on Sen1Floods11", "+ rain-signal rule (design example)"]),
  ("Flood water map", ["30 m, new water vs usual", "per-town km²"]),
  ("66.4% IoU", ["3.0× Otsu threshold (21.8%)", "1.63 s per tile on a CPU"])),
 ("Fire · Hot Spots", [("thermal", "Thermal anomalies", "NASA FIRMS MODIS + VIIRS"), ("optical", "Burned area", "NASA MODIS MCD64A1")],
  ("LightGBM + conformal", ["VIIRS/MODIS ratio per cell", "90% intervals, robust z-scores"]),
  ("Fire calendar + trend", ["detections per 0.25° cell", "unusual months flagged"]),
  ("8.5% lower error", ["RMSE 0.2844 vs 0.3109", "88.6% interval coverage"])),
 ("Field · Field Shift", [("optical", "Optical", "NASA HLS v2 · MODIS NDVI"), ("rain", "Climate + rain", "NASA POWER"), ("optical", "Terrain + soil + labels", "NASADEM · SoilGrids · USDA CDL")],
  ("LightGBM next-crop", ["+ FAO-56 water balance", "+ NSGA-II rotations"]),
  ("Next-crop map", ["six crop classes", "rotation plan per field"]),
  ("81.8% accuracy", ["macro-F1 0.501 (0.463 baseline)", "full-county map 81.1%"])),
]

def _box(x, y, w, h, tone, title, lines, size=15):
    rows = 1 + len(lines); lead = size + 5; top = y + h / 2 - ((rows - 1) * lead) / 2 + size * .35
    t = f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="af-box af-{tone}"/><text x="{x+w/2}" y="{top:.1f}" text-anchor="middle" class="af-title" style="font-size:{size}px">{e(title)}</text>'
    for i, l in enumerate(lines): t += f'<text x="{x+w/2}" y="{top+(i+1)*lead:.1f}" text-anchor="middle" class="af-small" style="font-size:{size-3}px">{e(l)}</text>'
    return t + "</g>"

def _arrow(d): return f'<path d="{d}" class="af-arrow" marker-end="url(#af-head)"/>'
HEAD = '<defs><marker id="af-head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" class="af-headp"/></marker></defs>'

def wide(p):
    name, ins, mdl, out, res = p
    W, H = 1100, 330; bw, bh, gap = 230, 78, 22; y0 = 46
    s = f'<text x="20" y="24" class="af-label">Inputs · NASA data</text><text x="330" y="24" class="af-label">Model</text><text x="610" y="24" class="af-label">Output</text><text x="870" y="24" class="af-label">Result · held-out test</text>'
    mid = y0 + (len(ins) * (bh + gap) - gap) / 2
    for i, (k, t, src) in enumerate(ins):
        y = y0 + i * (bh + gap); s += _box(20, y, bw, bh, TONE[k], t, [src])
        s += _arrow(f"M {20+bw} {y+bh/2} C {290} {y+bh/2}, {290} {mid}, {326} {mid}")
    s += _box(330, mid - 60, 240, 120, "ink", mdl[0], mdl[1], 16)
    s += _arrow(f"M 570 {mid} L 606 {mid}"); s += _box(610, mid - 50, 220, 100, "grey", out[0], out[1])
    s += _arrow(f"M 830 {mid} L 866 {mid}"); s += _box(870, mid - 50, 210, 100, "red" if False else "violet", res[0], res[1], 17)
    return f'<svg class="af-wide" viewBox="0 0 {W} {H}" role="img" aria-label="{e(name)}: inputs to model to output to result">{HEAD}{s}</svg>'

def tall(p):
    name, ins, mdl, out, res = p
    W = 420; bw = 380; y = 30; s = '<text x="20" y="20" class="af-label">Inputs · NASA data</text>'
    for k, t, src in ins: s += _box(20, y, bw, 62, TONE[k], t, [src], 17); y += 72
    s += _arrow(f"M 210 {y-6} L 210 {y+22}"); y += 30
    s += _box(20, y, bw, 100, "ink", mdl[0], mdl[1], 18); y += 100
    s += _arrow(f"M 210 {y+2} L 210 {y+28}"); y += 32
    s += _box(20, y, bw, 84, "grey", out[0], out[1], 17); y += 84
    s += _arrow(f"M 210 {y+2} L 210 {y+28}"); y += 32
    s += _box(20, y, bw, 90, "violet", res[0], res[1], 19); y += 104
    return f'<svg class="af-tall" viewBox="0 0 {W} {y}" role="img" aria-label="{e(name)}: inputs to model to output to result">{HEAD}{s}</svg>'

def figures():
    out = ""
    for n, p in enumerate(PIPES, 1):
        srcs = " · ".join(dict.fromkeys(src for _k, _t, src in p[1]))
        out += (f'<figure class="af" data-fx="rise"><p class="af-name mono">{e(p[0])}</p><div class="af-pad">{wide(p)}{tall(p)}</div>'
                f'<figcaption><strong>Figure {n}.</strong> {e(p[0].split(" · ")[1])}: from satellite inputs to a tested result. Sources: {e(srcs)}. Results are one seed on held-out data, not a published benchmark.</figcaption></figure>')
    leg = '<ul class="af-legend">' + "".join(f'<li><i class="af-{TONE[k]}"></i>{l}</li>' for k, l in (("sar", "SAR radar"), ("thermal", "Thermal"), ("rain", "Precipitation / climate"), ("optical", "Optical / land"))) + "</ul>"
    return f'{leg}<div class="af-list">{out}</div>'
