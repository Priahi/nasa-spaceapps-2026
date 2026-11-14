"""Canada fire heat map (site image): mean annual harmonized detections per 0.25° cell, 2003–2025, over province outlines."""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parents[1]
C = json.load(open(R / "demos/hotspots/data/fire_cells_canada.json"))["cells"]
P = json.load(open(R / "demos/hotspots/data/provinces_canada.json"))["features"]
S = 2; W, H = 900 * S, 620 * S
X = lambda lon: (lon + 141.5) / (141.5 - 52) * W
Y = lambda lat: (84 - lat) / (84 - 41.5) * H
RAMP = [(42, 29, 20), (124, 45, 18), (194, 65, 12), (249, 115, 22), (251, 191, 36), (253, 230, 138)]
def ramp(t):
    t = max(0, min(1, t)); p = t * (len(RAMP) - 1); i = min(len(RAMP) - 2, int(p)); f = p - i; a, b = RAMP[i], RAMP[i + 1]
    return tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
def rings(g):
    polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    for poly in polys: yield [(X(x), Y(y)) for x, y in poly[0]]
for f in P:
    for r in rings(f["geometry"]): d.polygon(r, fill=(22, 27, 56, 255))
mx = math.log10(1 + max(c[2] for c in C))
for lat, lon, v, *_ in sorted(C, key=lambda c: c[2]):
    t = math.log10(1 + v) / mx
    d.rectangle([X(lon - .125), Y(lat + .125), X(lon + .125) + 1, Y(lat - .125) + 1], fill=ramp(t) + (255,))
for f in P:
    for r in rings(f["geometry"]): d.line(r + [r[0]], fill=(190, 205, 255, 120), width=S)
bb = im.getbbox(); im = im.crop((max(0, bb[0] - 8), max(0, bb[1] - 8), min(W, bb[2] + 8), min(H, bb[3] + 8)))
im.save(R / "src/assets/img/canada-fire-heat.webp", quality=88, method=6)
print(im.size)
