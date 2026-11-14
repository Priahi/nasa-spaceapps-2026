"""Field Shift x Earthdata: HLS v2.0 (L30 Landsat + S30 Sentinel-2, LP DAAC, Earthdata login) 30 m NDVI over
Story County, Iowa (bbox -93.70,41.86,-93.23,42.21), MGRS tile T15TVG, Jul-Aug 2024/2025 scenes with <=5% cloud.
NDVI = (NIR-Red)/(NIR+Red) with Fmask cloud / adjacent / shadow / snow / water removed (bits 1-5)."""
import json, re
from pathlib import Path
import numpy as np, rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = Path(__file__).resolve().parent; SRC = Path("/workspace/spaceapps-site/upgrades/hls")
tr = Transformer.from_crs(4326, 32615, always_xy=True)
xs, ys = zip(*[tr.transform(x, y) for x in (-93.70, -93.23) for y in (41.86, 42.21)])
BB = (min(xs), min(ys), max(xs), max(ys))
def read(p):
    with rasterio.open(p) as r:
        w = from_bounds(*BB, r.transform); a = r.read(1, window=w).astype("float32"); return a, r.window_transform(w)
scenes = {}
for red in sorted(SRC.glob("HLS.*.B04.tif")):
    gid = red.name[:-8]; sensor = gid.split(".")[1]; nir = SRC / (gid + (".B05.tif" if sensor == "L30" else ".B8A.tif"))
    fm = SRC / (gid + ".Fmask.tif")
    if not (nir.exists() and fm.exists()): continue
    R, tfm = read(red); N, _ = read(nir); F, _ = read(fm); F = F.astype(np.int16)
    bad = (R == -9999) | (N == -9999) | (((F >> 1) & 0b11111) > 0) | (F == 255)
    R, N = R * 1e-4, N * 1e-4
    nd = np.where(bad, np.nan, (N - R) / np.maximum(N + R, 1e-6))
    y, doy = int(gid.split(".")[3][:4]), int(gid.split(".")[3][4:7])
    import datetime as dt; d = (dt.date(y, 1, 1) + dt.timedelta(doy - 1)).isoformat()
    scenes[gid] = {"date": d, "sensor": sensor, "valid_frac": round(float(np.isfinite(nd).mean()), 3),
                   "ndvi_median": round(float(np.nanmedian(nd)), 3), "ndvi_gt_0p7_frac": round(float(np.nanmean(nd[np.isfinite(nd)] > 0.7)), 3), "_a": nd}
order = sorted(scenes, key=lambda g: scenes[g]["date"])
a24 = [g for g in order if scenes[g]["date"].startswith("2024")][0]
a25 = min([g for g in order if scenes[g]["date"].startswith("2025")], key=lambda g: abs(int(scenes[g]["date"][5:7]) * 31 + int(scenes[g]["date"][8:]) - (int(scenes[a24]["date"][5:7]) * 31 + int(scenes[a24]["date"][8:]))))
A, B = scenes[a24]["_a"], scenes[a25]["_a"]; D = B - A; both = np.isfinite(D)
crop = both & ((A > 0.5) | (B > 0.5))  # vegetated in at least one year (cropland/grass/trees), urban/water excluded
pk = 0.0009  # km2 per 30 m pixel
res = {"product": "HLS v2.0 HLSL30 + HLSS30 (LP DAAC), 30 m", "aoi": "Story County, Iowa bbox -93.70,41.86,-93.23,42.21", "tile": "T15TVG",
       "scenes": {g: {k: v for k, v in s.items() if k != "_a"} for g, s in scenes.items()},
       "pair": {"2024": [a24, scenes[a24]["date"]], "2025": [a25, scenes[a25]["date"]]},
       "pair_valid_km2": round(float(both.sum()) * pk, 1), "pair_vegetated_km2": round(float(crop.sum()) * pk, 1),
       "ndvi_change_median_vegetated": round(float(np.nanmedian(D[crop])), 3),
       "vegetated_km2_ndvi_up_gt_0p1": round(float((crop & (D > 0.1)).sum()) * pk, 1),
       "vegetated_km2_ndvi_down_gt_0p1": round(float((crop & (D < -0.1)).sum()) * pk, 1),
       "note": "Single-date mid-summer NDVI difference between two different years/sensors; shows field-by-field contrast, not a crop-type classification."}
(H / "hls_story_county.json").write_text(json.dumps(res, indent=1))
fig, ax = plt.subplots(1, 3, figsize=(15, 5.4), dpi=140)
for k, (arr, t, cm, vv) in enumerate([(A, f"HLS NDVI {scenes[a24]['date']} ({scenes[a24]['sensor']})", "YlGn", (0, 1)),
                                       (B, f"HLS NDVI {scenes[a25]['date']} ({scenes[a25]['sensor']})", "YlGn", (0, 1)),
                                       (np.where(both, D, np.nan), "NDVI change (2025 − 2024)", "PuOr", (-0.4, 0.4))]):
    im = ax[k].imshow(arr, cmap=cm, vmin=vv[0], vmax=vv[1], interpolation="nearest"); ax[k].set_title(t, fontsize=10); ax[k].axis("off")
    fig.colorbar(im, ax=ax[k], shrink=0.7)
fig.suptitle("Story County, Iowa — HLS 30 m NDVI (cloud/shadow/water masked with Fmask)", fontsize=11); fig.tight_layout()
fig.savefig(H / "hls_story_county_ndvi.png"); plt.close(fig)
print(json.dumps({k: v for k, v in res.items() if k != "scenes"}, indent=1)); [print(g, {k: v for k, v in s.items() if k != "_a"}) for g, s in scenes.items()]
