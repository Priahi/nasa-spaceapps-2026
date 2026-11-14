"""Earthdata-login trend layer -> out/earthdata_trends.json + PNG charts in out/.
  GRACE/GRACE-FO JPL RL06.3 mascon CRI v04 (PO.DAAC): via analyze_earthdata.grace() (land cells, deseasonalised annual-mean anomalies).
  SMAP L3 enhanced 9 km soil moisture SPL3SMP_E v006 (NSIDC): central Iowa + Story County cells, May-Sep mean, AM+PM, recommended-quality only.
  MCD64A1 v061 burned area (LP DAAC), tile h11v03: from earthdata/hot-spots/mcd64_h11v03.json.
  GPM IMERG V07 monthly (GPM_3IMERGM) + GLDAS Noah 2.1 monthly (GLDAS_NOAH025_M), GES DISC via Earthdata Cloud OPeNDAP subsets (trends/fetch_gesdisc.py). Tests: Mann-Kendall + Sen's slope via analyze.trend()."""
import json, glob, re
from pathlib import Path
import numpy as np, h5py
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from analyze import trend, OUT
from analyze_earthdata import grace, imerg, gldas
E = Path("/workspace/spaceapps-site/earthdata")
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})

def smap():
    rows = {}
    for f in sorted(glob.glob(str(E / "field-shift/raw/smap/*.nc4"))):
        d = re.search(r"_(\d{8})_", f).group(1); y, m = int(d[:4]), int(d[4:6])
        if not 5 <= m <= 9: continue
        h = h5py.File(f); vals = {}
        for g, s in (("AM", ""), ("PM", "_pm")):
            sm = h[f"Soil_Moisture_Retrieval_Data_{g}/soil_moisture{s}"][:].astype(float)
            q = h[f"Soil_Moisture_Retrieval_Data_{g}/retrieval_qual_flag{s}"][:]
            sm[(sm < 0) | ((q & 1) != 0)] = np.nan; vals[g] = sm
        st = np.stack([vals["AM"], vals["PM"]]); day = np.nanmean(st, axis=0) if np.isfinite(st).any() else None
        if day is None: continue
        rows.setdefault(y, []).append((day, st))
    out = {}
    for name, sl in (("central_iowa", (slice(None), slice(None))), ("story_county", (slice(18, 23), slice(14, 20)))):
        yrs, vals, ndays = [], [], {}
        for y in sorted(rows):
            dm = [np.nanmean(d[sl]) for d, _ in rows[y] if np.isfinite(d[sl]).sum() >= max(1, 0.3 * d[sl].size)]
            ndays[y] = len(dm)
            if len(dm) >= 60: yrs.append(y); vals.append(float(np.mean(dm)))
        t = trend(yrs, vals, "m³/m³ surface (0–5 cm) soil moisture, May–Sep mean of daily AM+PM box means, SMAP SPL3SMP_E")
        t["days_used_per_year"] = {str(y): ndays[y] for y in ndays}; out[name] = t
    return out

res = {"method": "Mann-Kendall (original + Hamed-Rao) and Sen's slope with 95% CI, alpha 0.05 (trends/analyze.py trend())",
       "grace": grace(), "smap_iowa": smap()}
mc = json.loads((E / "hot-spots/mcd64_h11v03.json").read_text()); res["mcd64_h11v03"] = mc["trend"]
res["imerg"] = imerg(); res["gldas_iowa"] = gldas()
res["notes"] = {"imerg": "GPM_3IMERGM V07 monthly mm/hr x hours in month; full years only (1998-2024; Oct-Dec 2025 not yet published, 404). Boxes include some sea (Valencia) and Great Lakes (Ontario).",
                "gldas": "GLDAS_NOAH025_M v2.1, central Iowa box (12x12 0.25 deg cells), May-Sep mean of monthly fields, 2000-2025."}
(OUT / "earthdata_trends.json").write_text(json.dumps(res, indent=1))

def chart(t, title, ylab, fn, color):
    fig, ax = plt.subplots(figsize=(9, 3.8), dpi=150); x = np.array(t["x"]); y = np.array(t["series"])
    ax.plot(x, y, "o-", color=color, lw=1.5, ms=4)
    ax.plot(x, np.median(y) + t["sen_slope_per_year"] * (x - np.median(x)), "--", color="#6366f1", lw=2,
            label=f"Sen's slope {t['sen_slope_per_year']:+.3g}/yr · MK p={t['p']:.3f} ({t['trend']})")
    ax.set_title(title, fontsize=10); ax.set_ylabel(ylab); ax.legend(frameon=False, fontsize=8); fig.tight_layout(); fig.savefig(OUT / fn); plt.close(fig)
lab = {"valencia": "Eastern Spain (Valencia)", "ontario": "Southern Ontario", "iowa": "Central Iowa"}
for r, t in res["grace"].items():
    chart(t, f"GRACE/GRACE-FO terrestrial water storage — {lab[r]} (annual-mean anomaly, 2017–18 gap)", "cm water equivalent", f"ed_grace_{r}.png", "#0ea5e9")
for r, t in res["smap_iowa"].items():
    chart(t, f"SMAP surface soil moisture, May–Sep mean — {r.replace('_', ' ').title()}, Iowa", "m³/m³", f"ed_smap_{r}.png", "#16a34a")
for r, d in res["imerg"].items():
    for k in ("annual_total", "son_total", "wettest_month"):
        chart(d[k], f"GPM IMERG V07 precipitation — {lab[r]} — {k.replace('_', ' ')}", "mm", f"ed_imerg_{r}_{k}.png", "#2563eb")
        print("imerg", r, k, d[k]["years"], d[k]["trend"], d[k]["p"], d[k]["p_hamed_rao"], d[k]["sen_slope_per_year"], d[k]["sen_ci95"], d[k]["slope_pct_of_median_per_decade"])
for k, t in res["gldas_iowa"].items():
    chart(t, f"GLDAS Noah 2.1 soil moisture, central Iowa — {t['unit'].split('soil moisture ')[1].split(',')[0]}, May–Sep mean", "kg/m²", f"ed_gldas_iowa_{k}.png", "#16a34a")
    print("gldas", k, t["years"], t["trend"], t["p"], t["p_hamed_rao"], t["sen_slope_per_year"], t["sen_ci95"], t["slope_pct_of_median_per_decade"])
for k, v in res["grace"].items(): print("grace", k, v["trend"], v["p"], v["p_hamed_rao"], v["sen_slope_per_year"], v["sen_ci95"])
for k, v in res["smap_iowa"].items(): print("smap", k, v["years"], v["n"], v["trend"], v["p"], v["p_hamed_rao"], v["sen_slope_per_year"], v["sen_ci95"], v["median"], v["days_used_per_year"])
