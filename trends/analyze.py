"""Trend Detective analysis: Mann-Kendall + Sen's slope (with 95% CI) on three themes.
Run: /workspace/nasa-spaceapps/venv/bin/python trends/analyze.py
Inputs (all public, no login):
  fire  : NASA FIRMS MODIS C6.1 + VIIRS S-NPP cell-months (0.25 deg) from the Hot Spots harmonizer tiles
          (filters: MODIS type 0, confidence >= 30; VIIRS type 0, confidence != low), Natural Earth admin-1 provinces.
  water : NASA POWER daily PRECTOTCORR (MERRA-2 based), MERRA-2 native 0.625 x 0.5 deg grid, 1981-2025.
  crops : NASA POWER daily T2M_MIN, T2M_MAX, GWETROOT, PRECTOTCORR (MERRA-2 based), 0.625 x 0.5 deg, 1981-2025."""
import json, math
from pathlib import Path
import numpy as np, pandas as pd, pymannkendall as mk
from scipy.stats import norm
from shapely.geometry import shape, Point
from shapely import STRtree, simplify

T = Path(__file__).resolve().parent
RAW, OUT = T / "raw", T / "out"; OUT.mkdir(exist_ok=True)
TILES = Path("/workspace/nasa-spaceapps/apps/01-hotspots/artifacts")
ALPHA = 0.05
Y0 = 2003  # first full year with both Terra and Aqua MODIS (Aqua fire data start mid-2002)

def sen_ci(x, alpha=ALPHA):
    """Sen's slope 95% CI (Gilbert 1987), using the MK variance without tie correction."""
    x = np.asarray(x, float); n = len(x)
    s = [(x[j] - x[i]) / (j - i) for i in range(n) for j in range(i + 1, n)]
    s = np.sort(s); N = len(s)
    var = n * (n - 1) * (2 * n + 5) / 18
    c = norm.ppf(1 - alpha / 2) * math.sqrt(var)
    lo, hi = int(round((N - c) / 2)) - 1, int(round((N + c) / 2))
    lo, hi = max(lo, 0), min(hi, N - 1)
    return float(s[lo]), float(s[hi])

def trend(years, x, unit):
    years = list(map(int, years)); x = np.asarray(x, float)
    r = mk.original_test(x); hr = mk.hamed_rao_modification_test(x)
    lo, hi = sen_ci(x)
    med = float(np.median(x))
    return {
        "years": [years[0], years[-1]], "n": len(x), "unit": unit,
        "trend": r.trend, "p": round(float(r.p), 5), "z": round(float(r.z), 3), "tau": round(float(r.Tau), 3),
        "sen_slope_per_year": round(float(r.slope), 5), "sen_ci95": [round(lo, 5), round(hi, 5)],
        "slope_pct_of_median_per_decade": (round(100 * 10 * r.slope / med, 2) if med else None),
        "p_hamed_rao": round(float(hr.p), 5), "significant": bool(r.p < ALPHA),
        "significant_autocorr_robust": bool(r.p < ALPHA and hr.p < ALPHA),
        "median": round(med, 4), "series": [round(float(v), 4) for v in x], "x": years,
    }

def svg_path(geom, proj):
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    d = []
    for p in polys:
        ring = np.asarray(p.exterior.coords)
        pts = [proj(lon, lat) for lon, lat in ring]
        d.append("M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + "Z")
    return "".join(d)

# ---------------- fire ----------------
def fire():
    gj = json.load(open(RAW / "ne50_admin1.geojson"))
    provs = [(f["properties"]["name"], shape(f["geometry"])) for f in gj["features"] if f["properties"]["admin"] == "Canada"]
    t = pd.read_parquet(TILES / "tiles_canada.parquet")
    t = t[(t.year >= Y0) & (t.year <= 2025)]
    cells = t[["lat", "lon"]].drop_duplicates().reset_index(drop=True)
    tree = STRtree([g for _, g in provs])
    names = []
    for lat, lon in zip(cells.lat, cells.lon):
        pt = Point(lon, lat); hit = tree.query(pt, predicate="intersects")
        if len(hit) == 0:  # coastal/ocean centroid: nearest province
            hit = [tree.nearest(pt)]
        names.append(provs[int(hit[0])][0])
    cells["prov"] = names
    t = t.merge(cells, on=["lat", "lon"])
    years = list(range(Y0, 2026))
    res = {}
    groups = [("Canada", t)] + [(n, t[t.prov == n]) for n, _ in provs]
    for name, g in groups:
        a = g.groupby("year").agg(harm=("v_equiv", "sum"), modis=("m_n", "sum"), frp=("m_frp_sum", "sum"), viirs=("v_n", "sum")).reindex(years, fill_value=0)
        if a.modis.sum() < 200: res[name] = {"note": "too few detections for a trend test", "modis_total": int(a.modis.sum())}; continue
        v = a.loc[2012:2025, "viirs"]
        res[name] = {
            "harmonized_count": trend(years, a.harm, "VIIRS-equivalent detections / yr"),
            "modis_count": trend(years, a.modis, "MODIS detections / yr"),
            "modis_frp": trend(years, a.frp / 1000.0, "GW total MODIS FRP / yr"),
            "viirs_count": trend(list(range(2012, 2026)), v, "VIIRS detections / yr"),
            "modis_total": int(a.modis.sum()),
        }
    # map geometry (simple equirectangular, cos(60) aspect), simplified
    W, H = 900, 620
    proj = lambda lon, lat: ((lon + 141.5) / (141.5 - 52) * W, (84 - lat) / (84 - 41.5) * H)
    geo = {n: svg_path(simplify(g, 0.08), proj) for n, g in provs}
    # Argentina national (same harmonizer) for a second region
    ta = pd.read_parquet(TILES / "tiles_argentina.parquet"); ta = ta[(ta.year >= Y0) & (ta.year <= 2025)]
    aa = ta.groupby("year").agg(harm=("v_equiv", "sum"), modis=("m_n", "sum"), frp=("m_frp_sum", "sum"), viirs=("v_n", "sum")).reindex(years, fill_value=0)
    arg = {"harmonized_count": trend(years, aa.harm, "VIIRS-equivalent detections / yr"), "modis_count": trend(years, aa.modis, "MODIS detections / yr"),
           "modis_frp": trend(years, aa.frp / 1000.0, "GW total MODIS FRP / yr"), "viirs_count": trend(list(range(2012, 2026)), aa.loc[2012:2025, "viirs"], "VIIRS detections / yr")}
    return {"canada": res, "argentina": arg, "map": {"w": W, "h": H, "paths": geo}}

# ---------------- POWER helpers ----------------
def load_power(region, par):
    frames = []
    for f in sorted((RAW / "power").glob(f"{region}_{par}_*.json")):
        d = json.load(open(f))
        for ft in d["features"]:
            lon, lat = ft["geometry"]["coordinates"][:2]
            s = ft["properties"]["parameter"][par]
            frames.append(pd.DataFrame({"lon": lon, "lat": lat, "date": list(s.keys()), "v": list(s.values())}))
    df = pd.concat(frames); df["date"] = pd.to_datetime(df["date"], format="%Y%m%d"); df.loc[df.v <= -999, "v"] = np.nan
    return df

def grid_trends(annual, unit):
    """annual: DataFrame index year, columns (lon,lat) -> per-cell trend summary for the map."""
    cells = []
    for (lon, lat), s in annual.items():
        s = s.dropna()
        if len(s) < 20: continue
        r = mk.original_test(s.values)
        cells.append({"lon": lon, "lat": lat, "trend": r.trend, "p": round(float(r.p), 4), "slope": round(float(r.slope), 4)})
    sig_up = sum(c["trend"] == "increasing" for c in cells); sig_dn = sum(c["trend"] == "decreasing" for c in cells)
    return {"unit": unit, "cells": cells, "n_cells": len(cells), "n_sig_increasing": sig_up, "n_sig_decreasing": sig_dn}

# ---------------- water ----------------
def water():
    out = {}
    for reg in ["valencia", "ontario"]:
        p = load_power(reg, "PRECTOTCORR"); p["year"] = p.date.dt.year
        tot = p.groupby(["year", "lon", "lat"]).v.sum().unstack(["lon", "lat"])
        rx1 = p.groupby(["year", "lon", "lat"]).v.max().unstack(["lon", "lat"])
        wet20 = (p.assign(w=p.v >= 20).groupby(["year", "lon", "lat"]).w.sum()).unstack(["lon", "lat"])
        yrs = list(tot.index)
        out[reg] = {
            "annual_total": trend(yrs, tot.mean(axis=1), "mm / yr (regional mean)"),
            "rx1day": trend(yrs, rx1.mean(axis=1), "mm, wettest day of the year (regional mean of cell maxima)"),
            "days_ge_20mm": trend(yrs, wet20.mean(axis=1), "days / yr with >= 20 mm (regional mean)"),
            "map_rx1day": grid_trends(rx1, "mm / yr"), "map_total": grid_trends(tot, "mm / yr per yr"),
            "n_cells": tot.shape[1],
        }
    return out

# ---------------- crops ----------------
def crops():
    tmin, tmax = load_power("iowa", "T2M_MIN"), load_power("iowa", "T2M_MAX")
    gw, pr = load_power("iowa", "GWETROOT"), load_power("iowa", "PRECTOTCORR")
    d = tmin.rename(columns={"v": "tmin"}).merge(tmax.rename(columns={"v": "tmax"}), on=["lon", "lat", "date"])
    d["year"] = d.date.dt.year; d["doy"] = d.date.dt.day_of_year; d["month"] = d.date.dt.month
    # corn GDD (base 10 C, cap 30 C), May-Sep
    tx, tn = d.tmax.clip(upper=30), d.tmin.clip(lower=10)
    d["gdd"] = ((tx.clip(lower=10) + tn.clip(upper=30)) / 2 - 10).clip(lower=0)
    gs = d[d.month.between(5, 9)]
    gdd = gs.groupby(["year", "lon", "lat"]).gdd.sum().unstack(["lon", "lat"])
    def ffs(g):
        fr = g[g.tmin <= 0]
        spring = fr[fr.doy < 182].doy.max(); fall = fr[fr.doy >= 182].doy.min()
        return (fall - spring - 1) if pd.notna(spring) and pd.notna(fall) else np.nan
    frost = d.groupby(["year", "lon", "lat"]).apply(ffs, include_groups=False).unstack(["lon", "lat"])
    last_spring = d[(d.tmin <= 0) & (d.doy < 182)].groupby(["year", "lon", "lat"]).doy.max().unstack(["lon", "lat"])
    first_fall = d[(d.tmin <= 0) & (d.doy >= 182)].groupby(["year", "lon", "lat"]).doy.min().unstack(["lon", "lat"])
    gw["year"], gw["month"] = gw.date.dt.year, gw.date.dt.month
    gwet = gw[gw.month.between(5, 9)].groupby(["year", "lon", "lat"]).v.mean().unstack(["lon", "lat"])
    pr["year"], pr["month"] = pr.date.dt.year, pr.date.dt.month
    gsp = pr[pr.month.between(5, 9)].groupby(["year", "lon", "lat"]).v.sum().unstack(["lon", "lat"])
    hot = d[d.month.between(6, 8)].assign(h=lambda x: x.tmax >= 32).groupby(["year", "lon", "lat"]).h.sum().unstack(["lon", "lat"])
    yrs = list(gdd.index)
    sc = (-93.75, 42.0)  # MERRA-2 grid cell (0.625 x 0.5 deg) nearest Story County centre (-93.465, 42.035)
    def both(df, unit):
        return {"region": trend(yrs, df.mean(axis=1), unit + " (central Iowa mean)"), "story_cell": trend(yrs, df[sc], unit + " (Story County cell)"), "map": grid_trends(df, unit)}
    return {
        "frost_free_days": both(frost, "frost-free days (last spring to first fall Tmin <= 0 C)"),
        "last_spring_frost_doy": both(last_spring, "day of year of last spring frost"),
        "first_fall_frost_doy": both(first_fall, "day of year of first fall frost"),
        "gdd_may_sep": both(gdd, "corn GDD May-Sep (base 10 C, cap 30 C)"),
        "rootzone_wetness_may_sep": both(gwet, "GWETROOT May-Sep mean (0-1)"),
        "precip_may_sep": both(gsp, "mm May-Sep"),
        "hot_days_jja": both(hot, "Jun-Aug days with Tmax >= 32 C"),
        "n_cells": gdd.shape[1],
    }

if __name__ == "__main__":
    res = {"method": {"test": "Mann-Kendall (original), two-sided, alpha 0.05; Hamed-Rao autocorrelation-corrected p also reported",
                      "slope": "Sen's slope with 95% CI (Gilbert 1987)", "library": "pymannkendall 1.4.3"},
           "fire": fire(), "water": water(), "crops": crops()}
    (OUT / "trends.json").write_text(json.dumps(res))
    print("wrote", OUT / "trends.json")
