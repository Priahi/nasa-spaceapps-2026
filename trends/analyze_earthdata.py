"""Earthdata-login layer of the Trend Detective analysis (Mann-Kendall + Sen's slope, same helpers as analyze.py).
  GRACE/GRACE-FO : JPL RL06.3 mascon CRI v04 (TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4, PO.DAAC), lwe_thickness (cm),
                   land cells only, monthly -> deseasonalised anomaly -> annual mean (years with >= 6 months), box mean weighted by cos(lat).
  GPM IMERG      : GPM_3IMERGM V07 monthly precipitation (mm/hr -> mm/month), annual totals 1998-2024 (if fetched).
  GLDAS          : GLDAS_NOAH025_M 2.1 monthly soil moisture, Iowa, May-Sep means 2000-2025 (if fetched).
Merges results into out/trends.json under "earthdata"."""
import json, calendar
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
from analyze import trend, OUT, RAW
BOX = {"valencia": (-2.0, 1.0, 38.0, 41.0), "ontario": (-81.0, -78.0, 43.0, 46.0), "iowa": (-95.0, -92.0, 41.0, 44.0)}

def anom_trend(years, vals, unit):
    t = trend(years, vals, unit); t["slope_pct_of_median_per_decade"] = None; return t

def grace():
    ds = xr.open_dataset(RAW / "grace" / "grace.nc", decode_times=False)
    t0 = pd.Timestamp("2002-01-01"); time = t0 + pd.to_timedelta(ds["time"].values, unit="D")
    lon = ds["lon"].values; out = {}
    for reg, (w, e, s, n) in BOX.items():
        lw, le = w % 360, e % 360
        lonsel = (lon >= lw) & (lon <= le) if lw < le else ((lon >= lw) | (lon <= le))
        lat = ds["lat"].values; latsel = (lat >= s) & (lat <= n)
        sub = ds["lwe_thickness"].values[:, latsel][:, :, lonsel]
        land = ds["land_mask"].values[latsel][:, lonsel] > 0.5  # land cells only (CRI-filtered mascons)
        wts = np.cos(np.deg2rad(lat[latsel]))[:, None] * land
        series = pd.Series((sub * wts).sum(axis=(1, 2)) / wts.sum(), index=time)
        clim = series.groupby(series.index.month).transform("mean")
        an = (series - clim)
        g = an.groupby(an.index.year); cnt = g.count(); ann = g.mean()[cnt >= 6]
        ann = ann[(ann.index >= 2003) & (ann.index <= 2025)]
        r = anom_trend(list(ann.index), ann.values, "cm equivalent water thickness, annual mean anomaly (deseasonalised)")
        r["years_missing"] = [y for y in range(2003, 2026) if y not in ann.index]
        r["months"] = int(series.size); r["first_month"] = str(time[0].date()); r["last_month"] = str(time[-1].date())
        r["n_cells_0p5deg"] = int(land.sum()); r["n_mascons"] = int(len(np.unique(ds["mascon_ID"].values[latsel][:, lonsel][land])))
        out[reg] = r
    return out

def imerg():
    base = RAW / "gesdisc" / "imerg"; out = {}
    for reg in ("valencia", "ontario", "iowa"):
        files = sorted((base / reg).glob("*.nc4"))
        if len(files) < 300: continue
        tot = {}
        for f in files:
            y, m = int(f.stem[:4]), int(f.stem[4:])
            d = xr.open_dataset(f, group="Grid"); v = d["precipitation"].values.squeeze()  # (lon, lat), mm/hr monthly mean rate
            lat = d["lat"].values; w = np.cos(np.deg2rad(lat))
            mm = float(np.nansum(np.nanmean(v, axis=0) * w) / w.sum()) * 24 * calendar.monthrange(y, m)[1]
            tot.setdefault(y, {})[m] = mm
        yrs = [y for y in sorted(tot) if len(tot[y]) == 12]
        out[reg] = {"annual_total": trend(yrs, [sum(tot[y].values()) for y in yrs], "mm / yr, GPM IMERG V07 monthly (box mean, cos-lat weighted)"),
                    "son_total": trend(yrs, [tot[y][9] + tot[y][10] + tot[y][11] for y in yrs], "mm, Sep–Nov total, GPM IMERG V07 monthly (box mean)"),
                    "wettest_month": trend(yrs, [max(tot[y].values()) for y in yrs], "mm, wettest calendar month of the year, GPM IMERG V07 (box mean)"),
                    "monthly_mm": {str(y): [round(tot[y][m], 2) for m in range(1, 13)] for y in yrs}}
    return out

def gldas():
    files = sorted((RAW / "gesdisc" / "gldas" / "iowa").glob("*.nc4"))
    if len(files) < 120: return {}
    rows = []
    for f in files:
        y, m = int(f.stem[:4]), int(f.stem[4:])
        if not 5 <= m <= 9: continue
        d = xr.open_dataset(f)
        rows.append({"y": y, **{k: float(np.nanmean(d[k].values)) for k in ["SoilMoi0_10cm_inst", "SoilMoi10_40cm_inst", "SoilMoi40_100cm_inst", "RootMoist_inst"]}})
    df = pd.DataFrame(rows); g = df.groupby("y"); df = g.mean()[g.size() == 5]
    lab = {"SoilMoi0_10cm_inst": "0–10 cm", "SoilMoi10_40cm_inst": "10–40 cm", "SoilMoi40_100cm_inst": "40–100 cm", "RootMoist_inst": "root zone (0–100 cm)"}
    return {k: trend(list(df.index), df[k].values, f"kg/m² soil moisture {lab[k]}, May–Sep mean, GLDAS Noah 2.1 (central Iowa)") for k in lab}

if __name__ == "__main__":
    res = json.loads((OUT / "trends.json").read_text())
    ed = {"grace": grace() if (RAW / "grace" / "grace.nc").exists() else {}, "imerg": imerg(), "gldas": gldas()}
    res["earthdata"] = ed
    (OUT / "trends.json").write_text(json.dumps(res))
    for k, v in ed.items():
        for r, t in v.items():
            for kk, tt in (t.items() if "trend" not in t else [("", t)]):
                if isinstance(tt, dict) and "trend" in tt: print(k, r, kk, tt["trend"], "p", tt["p"], "pHR", tt["p_hamed_rao"], "sen", tt["sen_slope_per_year"], tt["sen_ci95"], tt["years"], tt.get("years_missing", ""))
