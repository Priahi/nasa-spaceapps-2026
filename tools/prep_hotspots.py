"""Precompute Hot Spots map layers from the shipped tiles (no new data): per-cell fire activity and Canada province outlines + trends.
Outputs demos/hotspots/data/fire_cells_<country>.json and demos/hotspots/data/provinces_canada.json."""
import json, numpy as np
from pathlib import Path
from shapely.geometry import shape, Point, mapping
from shapely import STRtree
R = Path(__file__).resolve().parents[1]; D = R / "demos/hotspots/data"
T = json.load(open(R / "trends/out/trends.json"))["fire"]
gj = json.load(open(R / "trends/raw/ne50_admin1.geojson"))
provs = [(f["properties"]["name"], shape(f["geometry"])) for f in gj["features"] if f["properties"]["admin"] == "Canada"]

def load(c):
    s = json.load(open(D / f"tiles_{c}.json")); buf = (D / f"tiles_{c}.bin").read_bytes()
    dt = {"float32": np.float32, "int16": np.int16, "uint8": np.uint8}
    return {col["name"]: np.frombuffer(buf, dtype=dt[col["dtype"]], count=s["n"], offset=col["offset"]) for col in s["columns"]}

def cells(c, tree=None):
    t = load(c); yrs = t["year"].astype(int) + 2000
    key = (t["gy"].astype(np.int64) + 50000) * 100000 + (t["gx"].astype(np.int64) + 50000); u, inv = np.unique(key, return_inverse=True)
    sel = (yrs >= 2003) & (yrs <= 2025); ny = 23
    tot = np.bincount(inv[sel], weights=t["v_equiv"][sel], minlength=len(u)) / ny
    may = np.bincount(inv[sel & (t["month"] == 5)], weights=t["v_equiv"][sel & (t["month"] == 5)], minlength=len(u)) / ny
    jul = np.bincount(inv[sel & (t["month"] == 7)], weights=t["v_equiv"][sel & (t["month"] == 7)], minlength=len(u)) / ny
    gy, gx = u // 100000 - 50000, u % 100000 - 50000
    out = []
    for i in range(len(u)):
        if tot[i] < 0.05: continue
        lat, lon = gy[i] * 0.25 + 0.125, gx[i] * 0.25 + 0.125
        row = [round(float(lat), 3), round(float(lon), 3), round(float(tot[i]), 2), round(float(may[i]), 2), round(float(jul[i]), 2)]
        if tree is not None:
            pt = Point(lon, lat); hit = tree.query(pt, predicate="intersects"); hit = hit if len(hit) else [tree.nearest(pt)]
            row.append(provs[int(hit[0])][0])
        out.append(row)
    return out

tree = STRtree([g for _, g in provs])
ca = cells("canada", tree)
json.dump({"cols": ["lat", "lon", "mean_annual", "may_mean", "jul_mean", "province"], "years": "2003-2025", "unit": "VIIRS-equivalent detections per year (harmonized)", "cell_deg": 0.25, "cells": ca}, open(D / "fire_cells_canada.json", "w"), separators=(",", ":"))
ar = cells("argentina")
json.dump({"cols": ["lat", "lon", "mean_annual", "may_mean", "jul_mean"], "years": "2003-2025", "unit": "VIIRS-equivalent detections per year (harmonized)", "cell_deg": 0.25, "cells": ar}, open(D / "fire_cells_argentina.json", "w"), separators=(",", ":"))
def rnd(o):
    if isinstance(o, float): return round(o, 3)
    if isinstance(o, (list, tuple)): return [rnd(x) for x in o]
    if isinstance(o, dict): return {k: rnd(v) for k, v in o.items()}
    return o
feats = []
for n, g in provs:
    r = T["canada"].get(n, {}); h = r.get("harmonized_count"); m = r.get("modis_count")
    feats.append({"type": "Feature", "properties": {"name": n, "h_slope": h and round(h["sen_slope_per_year"], 1), "h_p": h and h["p"], "m_slope": m and round(m["sen_slope_per_year"], 1), "m_p": m and m["p"],
        "mean_annual": round(sum(c[2] for c in ca if c[5] == n), 0)}, "geometry": mapping(g.simplify(0.06, preserve_topology=True))})
json.dump(rnd({"type": "FeatureCollection", "source": "Natural Earth 1:50m admin-1 (public domain); trends from trends/out/trends.json", "features": feats}), open(D / "provinces_canada.json", "w"), separators=(",", ":"))
print("cells", len(ca), len(ar), "total", round(sum(c[2] for c in ca)), "max", max(c[2] for c in ca))
