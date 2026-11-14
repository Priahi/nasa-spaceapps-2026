"""SAR Change C2 assets from NASA/JPL OPERA DSWx-S1 (same grid and 'usual water' rule as upgrades/opera_valencia.py).
All real pixels, no model output:
  ../img/opera-{before,after,delta,still}.webp  cropped to the valid footprint and the flood focus (no no-data wedge, less open sea)
  ../zones.json  municipality outlines (OSM via Nominatim, ODbL) in crop-pixel coords + per-municipality km² stats
Copies of both go to demos/sar-change/ops/ for the dashboard."""
import json, shutil, warnings, numpy as np
from pathlib import Path
from PIL import Image
warnings.filterwarnings("ignore")
from opera_stack import load, W, S, E, N, RES, nx, ny, PX_KM2, ROOT
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import shape, mapping
from shapely.ops import transform as stransform

HERE = Path(__file__).resolve().parent; MOD = HERE.parent; IMG = MOD / "img"; IMG.mkdir(exist_ok=True)
OPS = ROOT / "demos/sar-change/ops"; OPS.mkdir(exist_ok=True)
dates, A = load()
valid = A <= 3; water = np.isin(A, [1, 3])
pre = np.array([d < "20241029" for d in dates])
usual = (valid[pre].sum(0) >= 3) & (water[pre].sum(0) >= 0.8 * valid[pre].sum(0))
ib, ia, il = dates.index("20241026T175436"), dates.index("20241031T180258"), dates.index("20241119T175502")
new = lambda i: water[i] & ~usual & valid[i]
nb, na, nl = new(ib), new(ia), new(il)
both = valid[ib] & valid[ia]
cols = np.where(both.mean(0) > 0.995)[0]; rows = np.where(both[:, cols.min():cols.max() + 1].mean(1) > 0.995)[0]
c0, c1, r0, r1 = int(cols.min()), int(cols.max()) + 1, int(rows.min()), int(rows.max()) + 1
FW, FS, FE, FN = -0.56, 39.20, -0.215, 39.52  # flood focus: Valencia city, l'Horta Sud, Albufera, Ribera Baixa coast
c0, c1 = max(c0, int((FW - W) / RES)), min(c1, int(round((FE - W) / RES))); r0, r1 = max(r0, int((N - FN) / RES)), min(r1, int(round((N - FS) / RES)))
print("crop cols", c0, c1, "rows", r0, r1)
NODATA, LAND, PERM = (16, 19, 38), (38, 44, 70), (30, 64, 175)
NEW, PRIOR, GONE = (56, 189, 248), (14, 116, 144), (245, 158, 11)
def save(img, name):
    Image.fromarray(img[r0:r1, c0:c1]).save(IMG / name, lossless=True, method=6); shutil.copy(IMG / name, OPS / name)
def base(i):
    img = np.zeros(A.shape[1:] + (3,), np.uint8); img[:] = NODATA; img[valid[i]] = LAND; img[usual & water[i]] = PERM; img[new(i)] = NEW; return img
save(base(ib), "opera-before.webp"); save(base(ia), "opera-after.webp")
d = np.zeros(A.shape[1:] + (3,), np.uint8); d[:] = NODATA; d[both] = LAND; d[usual] = PERM
d[nb & na] = PRIOR; d[na & ~nb] = NEW; d[nb & ~na & valid[ia]] = GONE; save(d, "opera-delta.webp")
s = np.zeros(A.shape[1:] + (3,), np.uint8); s[:] = NODATA; s[valid[il]] = LAND; s[usual] = PERM; s[nl] = NEW; save(s, "opera-still.webp")
km = lambda m: round(float(m.sum() * PX_KM2), 2)
cr = np.zeros_like(both); cr[r0:r1, c0:c1] = True
tot = {"before_date": "2024-10-26", "after_date": "2024-10-31", "last_date": "2024-11-19",
       "new_before_km2": km(nb), "new_after_km2": km(na), "added_km2": km(na & ~nb), "kept_km2": km(nb & na), "gone_km2": km(nb & ~na & valid[ia]),
       "still_km2": km(nl), "usual_km2": km(usual), "in_crop_after_km2": km(na & cr), "crop_px": [c0, r0, c1, r1], "size": [c1 - c0, r1 - r0], "grid_deg": RES,
       "crop_lonlat": [round(W + c0 * RES, 4), round(N - r1 * RES, 4), round(W + c1 * RES, 4), round(N - r0 * RES, 4)]}
print(tot)
from munis_osm import MUNIS as munis; T = from_bounds(W, S, E, N, nx, ny); zones = []
for name, m in munis.items():
    g = shape(m["geojson"])
    lab = rasterize([(mapping(g), 1)], out_shape=(ny, nx), transform=T, fill=0, dtype="uint8").astype(bool) & cr
    if lab.sum() * PX_KM2 < 1: continue
    px = stransform(lambda x, y, z=None: ((x - W) / RES - c0, (N - y) / RES - r0), g.simplify(0.0005, preserve_topology=True))
    polys = [px] if px.geom_type == "Polygon" else list(px.geoms)
    path = " ".join("M" + "L".join(f"{x:.0f},{y:.0f}" for x, y in p.exterior.coords) + "Z" for p in polys if p.area > 30)
    rp = g.representative_point(); rc = [round((rp.x - W) / RES - c0), round((N - rp.y) / RES - r0)]
    yy, xx = np.nonzero(na & lab)  # label anchor: middle of the zone's flood water when it has any (> 0.5 km²), else a point inside the town
    wc = [int(np.median(xx)) - c0, int(np.median(yy)) - r0] if len(xx) * PX_KM2 > 0.5 else rc
    zones.append({"name": name, "comarca": m["display"].split(",")[1].strip(), "d": path, "c": rc, "wc": wc,
                  "area_km2": km(lab), "new_before_km2": km(nb & lab), "new_after_km2": km(na & lab), "added_km2": km(na & ~nb & lab), "still_km2": km(nl & lab)})
zones.sort(key=lambda z: -z["new_after_km2"])
for z in zones[:14]: print(z["name"], z["comarca"], z["area_km2"], z["new_before_km2"], z["new_after_km2"], z["added_km2"], z["still_km2"])
out = {"source": "NASA/JPL OPERA DSWx-S1 v1 (PO.DAAC), B01_WTR, 30 m; municipality outlines © OpenStreetMap contributors (ODbL) via Nominatim",
       "rule": "New water = open water or inundated vegetation (WTR classes 1, 3) outside 'usual water' (water in >= 80% of valid looks, 1-28 Oct 2024).",
       "totals": tot, "zones": zones}
(MOD / "zones.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"))); shutil.copy(MOD / "zones.json", OPS / "zones.json")
print("zones", len(zones))
