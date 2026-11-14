"""Field Shift x Earthdata: SMAP SPL3SMP_E v006 (NSIDC) 9 km surface soil moisture, Story County cells (EASE2 rows 265-269,
cols 924-929) and central Iowa box, May-Sep 2015-2025. Recommended-quality retrievals only (retrieval_qual_flag bit 0 = 0), AM+PM averaged.
Outputs: smap_story_county.json (daily Story County series + May-Sep means + trend from trends/out/earthdata_trends.json) and a PNG."""
import json, glob, re, datetime as dt
from pathlib import Path
import numpy as np, h5py
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = Path(__file__).resolve().parent
ser = {}
for f in sorted(glob.glob(str(H / "raw/smap/*.nc4"))):
    d = re.search(r"_(\d{8})_", f).group(1); h = h5py.File(f); st = []
    for g, s in (("AM", ""), ("PM", "_pm")):
        sm = h[f"Soil_Moisture_Retrieval_Data_{g}/soil_moisture{s}"][18:23, 14:20].astype(float)
        q = h[f"Soil_Moisture_Retrieval_Data_{g}/retrieval_qual_flag{s}"][18:23, 14:20]
        sm[(sm < 0) | ((q & 1) != 0)] = np.nan; st.append(sm)
    day = np.nanmean(np.stack(st), axis=0)  # same rule as trends/earthdata_trends.py: AM/PM mean per cell, >=30% cells valid
    if np.isfinite(day).sum() >= max(1, 0.3 * day.size): ser[d] = float(np.nanmean(day))
tr = json.load(open("/workspace/spaceapps-site/trends/out/earthdata_trends.json"))["smap_iowa"]
by = {}
for d, v in ser.items(): by.setdefault(int(d[:4]), []).append((dt.date(int(d[:4]), int(d[4:6]), int(d[6:])).timetuple().tm_yday, v))
out = {"product": "SMAP L3 enhanced radiometer soil moisture SPL3SMP_E v006 (NSIDC DAAC), 9 km EASE-Grid 2.0, 0–5 cm",
       "aoi": "Story County, Iowa (30 EASE2 9 km cells) + central Iowa box 95–92°W, 41–44°N", "granules": len(glob.glob(str(H / 'raw/smap/*.nc4'))),
       "story_county_may_sep_mean": {str(y): round(float(np.mean([v for _, v in by[y]])), 4) for y in sorted(by)},
       "story_county_valid_days": {str(y): len(by[y]) for y in sorted(by)},
       "trend_story_county": {k: tr["story_county"][k] for k in ("years", "n", "trend", "p", "p_hamed_rao", "sen_slope_per_year", "sen_ci95", "median")},
       "trend_central_iowa": {k: tr["central_iowa"][k] for k in ("years", "n", "trend", "p", "p_hamed_rao", "sen_slope_per_year", "sen_ci95", "median")},
       "daily_story_county": {d: round(v, 4) for d, v in ser.items()}}
(H / "smap_story_county.json").write_text(json.dumps(out, indent=1))
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(10, 4), dpi=150)
for y in sorted(by):
    x, v = zip(*sorted(by[y])); ax.plot(x, v, lw=2.2 if y in (2024, 2025) else 0.7, color={2024: "#f97316", 2025: "#6366f1"}.get(y, "#94a3b8"), alpha=1 if y in (2024, 2025) else 0.6, label=str(y) if y in (2024, 2025) else None)
ax.plot([], [], color="#94a3b8", lw=0.7, label="2015–2023")
ax.set_xticks([121, 152, 182, 213, 244, 273]); ax.set_xticklabels(["May", "Jun", "Jul", "Aug", "Sep", "Oct"])
ax.set_ylabel("surface soil moisture (m³/m³)"); ax.legend(frameon=False, fontsize=8)
ax.set_title("SMAP 9 km soil moisture, Story County, Iowa — daily, May–Sep 2015–2025", fontsize=10); fig.tight_layout(); fig.savefig(H / "smap_story_county_daily.png")
print(out["story_county_may_sep_mean"], out["story_county_valid_days"])
