"""Hot Spots x Earthdata: MODIS MCD64A1 v061 burned area (LP DAAC, Earthdata login), tile h11v03
(NE British Columbia / Alberta / Saskatchewan boreal, 50-60N), Apr-Oct monthly granules 2003-2025.
Annual burned area = pixels with a valid burn date (1-366) summed over the 7 monthly products x 500 m pixel area
(sinusoidal equal-area, 463.3127 m). Trend: Mann-Kendall + Sen's slope (same trend() as trends/analyze.py)."""
import json, sys, glob, re
from pathlib import Path
import numpy as np
from pyhdf.SD import SD
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
sys.path.insert(0, "/workspace/spaceapps-site/trends"); from analyze import trend
H = Path(__file__).resolve().parent; SRC = Path("/workspace/spaceapps-site/upgrades/mcd64")
PIX_KM2 = (463.31271653 ** 2) / 1e6
R = 6371007.181; T = 1111950.5197665233; NP = 2400; h, v = 11, 3
files = sorted(SRC.glob("MCD64A1.A*.h11v03.061.*.hdf"))
ann, unm = {}, {}; last = np.zeros((NP, NP), np.int16); y23 = np.zeros((NP, NP), np.int16); water = None
for f in files:
    y = int(re.search(r"\.A(\d{4})", f.name).group(1))
    b = SD(str(f)).select("Burn Date").get()
    if water is None: water = b == -2
    burned = b > 0
    ann[y] = ann.get(y, 0) + int(burned.sum()); unm.setdefault(y, []).append(float((b == -1).mean()))
    last[burned] = y
    if y == 2023: y23[burned] = b[burned]
yrs = sorted(ann); km2 = [ann[y] * PIX_KM2 for y in yrs]
assert all(len(unm[y]) == 7 for y in yrs), "need 7 months per year"
t = trend(yrs, km2, "km² burned, Apr–Oct, MCD64A1 tile h11v03")
# geolocation of pixel centres (sinusoidal -> lon/lat)
i = np.arange(NP) + 0.5; x = -20015109.354 + (h * NP + i) * (T / NP); yv = 10007554.677 - (v * NP + i) * (T / NP)
lat = np.degrees(yv / R); lon2d = np.degrees(x[None, :] / (R * np.cos(np.radians(lat))[:, None]))
out = {"product": "MCD64A1.061 (MODIS Terra+Aqua burned area, monthly, 500 m), LP DAAC", "tile": "h11v03",
       "months": "Apr–Oct", "files": len(files), "pixel_km2": round(PIX_KM2, 5),
       "lat_range": [round(float(lat.min()), 2), round(float(lat.max()), 2)],
       "annual_burned_km2": {str(y): round(k, 1) for y, k in zip(yrs, km2)},
       "mean_unmapped_fraction": {str(y): round(float(np.mean(unm[y])), 4) for y in yrs},
       "trend": t, "total_burned_km2_2003_2025": round(sum(km2), 1),
       "largest_year": {"year": yrs[int(np.argmax(km2))], "km2": round(max(km2), 1)},
       "land_pixels_km2": round(float((~water).sum()) * PIX_KM2, 0)}
(H / "mcd64_h11v03.json").write_text(json.dumps(out, indent=1))
# chart
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(10, 4.2), dpi=150)
ax.bar(yrs, km2, color="#f97316"); xs = np.array(yrs)
ax.plot(xs, np.median(km2) + t["sen_slope_per_year"] * (xs - np.median(xs)), color="#6366f1", lw=2, label=f"Sen's slope {t['sen_slope_per_year']:+.0f} km²/yr (MK p={t['p']:.3f}, {t['trend']})")
ax.set_ylabel("Burned area, Apr–Oct (km²)"); ax.set_title("MODIS MCD64A1 burned area, tile h11v03 (NE B.C. / Alberta / Saskatchewan boreal), 2003–2025", fontsize=10)
ax.legend(frameon=False, fontsize=9); fig.tight_layout(); fig.savefig(H / "mcd64_annual_burned_area.png"); plt.close(fig)
# map: year of most recent burn
fig, ax = plt.subplots(figsize=(8, 7), dpi=150); s = 4
L = np.where(last > 0, last, np.nan)[::s, ::s]; lo = lon2d[::s, ::s]; la = np.repeat(lat[::s, None], lo.shape[1], 1)
ax.set_facecolor("#0b1020")
ax.scatter(lo[water[::s, ::s]], la[water[::s, ::s]], s=0.3, c="#1e3a5f", marker="s", lw=0)
m = ~np.isnan(L); sc = ax.scatter(lo[m], la[m], c=L[m], s=0.6, cmap="plasma", vmin=2003, vmax=2025, marker="s", lw=0)
try:
    import shapely.geometry as sg
    gj = json.load(open("/workspace/spaceapps-site/trends/raw/ne50_admin1.geojson"))
    for ft in gj["features"]:
        if ft["properties"].get("admin") != "Canada": continue
        g = sg.shape(ft["geometry"]); gs = getattr(g, "geoms", [g])
        for p in gs: xx, yy = p.exterior.xy; ax.plot(xx, yy, color="#94a3b8", lw=0.5)
except Exception as e: print("outline skipped", e)
ax.set_xlim(np.nanmin(lo), np.nanmax(lo)); ax.set_ylim(lat.min(), lat.max()); ax.set_xlabel("lon"); ax.set_ylabel("lat")
cb = fig.colorbar(sc, ax=ax, shrink=0.7); cb.set_label("year of most recent burn (MCD64A1)")
ax.set_title("Burned since 2003, MODIS MCD64A1 tile h11v03", fontsize=10); fig.tight_layout(); fig.savefig(H / "mcd64_last_burn_year_map.png"); plt.close(fig)
print(json.dumps({k: out[k] for k in ("files", "largest_year", "total_burned_km2_2003_2025")}), t["trend"], t["p"], t["p_hamed_rao"], t["sen_slope_per_year"], t["sen_ci95"])
print(out["annual_burned_km2"])
