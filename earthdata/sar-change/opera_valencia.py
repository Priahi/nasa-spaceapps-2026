"""SAR Change upgrade: NASA/JPL OPERA DSWx-S1 (Sentinel-1 derived dynamic surface water, 30 m) over the Valencia DANA flood.
Mosaics MGRS tiles T30SYJ + T31SBD per acquisition onto a lat/lon grid over the flood zone, then counts open water +
inundated vegetation (WTR classes 1, 3) outside 'usual water' (water in >= 80% of valid pre-flood looks, Oct 1-28)."""
import glob, json, re
from collections import defaultdict
from pathlib import Path
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
from PIL import Image
D = Path(__file__).resolve().parent
W, S, E, N = -0.75, 39.20, -0.20, 39.55  # l'Horta Sud, Albufera and the Turia/Magro/Poyo basins
RES = 0.0003  # ~30 m
nx, ny = int(round((E - W) / RES)), int(round((N - S) / RES))
dst_t = from_bounds(W, S, E, N, nx, ny)
groups = defaultdict(list)
for f in sorted(glob.glob(str(D / "opera" / "*_B01_WTR.tif"))):
    m = re.search(r"DSWx-S1_(T\w+?)_(\d{8}T\d{6})Z_(\d{8}T\d{6})Z", f)
    groups[m.group(2)].append((m.group(3), m.group(1), f))
dates, stacks = [], []
for acq in sorted(groups):
    by_tile = {}
    for prod, tile, f in sorted(groups[acq]):  # keep the latest production per tile
        by_tile[tile] = f
    mos = np.full((ny, nx), 255, np.uint8)
    for f in by_tile.values():
        with rasterio.open(f) as src:
            tmp = np.full((ny, nx), 255, np.uint8)
            reproject(rasterio.band(src, 1), tmp, dst_transform=dst_t, dst_crs="EPSG:4326", resampling=Resampling.nearest, src_nodata=255, dst_nodata=255)
        sel = (mos == 255) & (tmp != 255); mos[sel] = tmp[sel]
    dates.append(acq); stacks.append(mos)
A = np.stack(stacks)
valid = A <= 3
water = np.isin(A, [1, 3])
pre = np.array([d < "20241029" for d in dates])
pre_valid = valid[pre].sum(0); pre_water = water[pre].sum(0)
usual = (pre_valid >= 3) & (pre_water >= 0.8 * pre_valid)
px_km2 = (RES * 111.32 * np.cos(np.deg2rad((S + N) / 2))) * (RES * 110.57)
rows = []
for i, d in enumerate(dates):
    v = valid[i]; new = water[i] & ~usual & v
    rows.append({"acq": d, "orbit": "ascending" if d[9:11] in ("17", "18") else "descending",
                 "valid_frac": round(float(v.mean()), 3), "water_km2": round(float((water[i] & v).sum() * px_km2), 2),
                 "new_water_km2": round(float(new.sum() * px_km2), 2)})
res = {"product": "OPERA_L3_DSWX-S1_V1 (NASA/JPL OPERA, PO.DAAC), B01_WTR layer", "aoi_lonlat": [W, S, E, N], "grid_deg": RES,
       "tiles": ["T30SYJ", "T31SBD"], "n_acquisitions": len(dates), "files_used": sum(len(v) for v in groups.values()),
       "usual_water_km2": round(float(usual.sum() * px_km2), 2), "pixel_km2": px_km2, "series": rows}
(D / "out").mkdir(exist_ok=True)
(D / "out" / "opera_valencia.json").write_text(json.dumps(res, indent=1))
for r in rows: print(r)
print("usual water km2", res["usual_water_km2"])
# maps: last valid pre-flood ascending look vs first post-flood look
def rgb(a):
    img = np.zeros(a.shape + (3,), np.uint8); img[:] = (16, 20, 44)
    img[a == 0] = (40, 46, 78); img[np.isin(a, [250, 251])] = (24, 28, 52)
    img[usual & np.isin(a, [1, 3])] = (95, 168, 255)
    img[~usual & np.isin(a, [1, 3])] = (212, 196, 255)
    return img
def best(cond):
    c = [i for i, d in enumerate(dates) if cond(d)]
    return max(c, key=lambda i: valid[i].mean()) if c else None
ib = dates.index("20241026T175436"); ia = dates.index("20241031T180258")  # closest valid looks either side of the 29 Oct flood
for tag, i in (("before", ib), ("after", ia)):
    Image.fromarray(rgb(A[i])).save(D / "out" / f"opera_{tag}_{dates[i][:8]}.png"); print(tag, dates[i])
res["map_before"], res["map_after"] = dates[ib], dates[ia]
(D / "out" / "opera_valencia.json").write_text(json.dumps(res, indent=1))
