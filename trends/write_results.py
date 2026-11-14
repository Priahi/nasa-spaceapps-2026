"""Render trends/RESULTS.md from out/trends.json."""
import json
from pathlib import Path
T = Path(__file__).resolve().parent
d = json.load(open(T / "out/trends.json"))
def fm(v):
    a = abs(v)
    return f"{v:+,.0f}" if a >= 100 else f"{v:+,.2f}" if a >= 1 else f"{v:+.4f}"
def row(name, t):
    sig = "yes" if t["significant"] else "no"
    return f"| {name} | {t['years'][0]}–{t['years'][1]} | {t['trend']} | {t['p']:.4f} | {t['p_hamed_rao']:.4f} | {fm(t['sen_slope_per_year'])} [{fm(t['sen_ci95'][0])}, {fm(t['sen_ci95'][1])}] | {t['slope_pct_of_median_per_decade']:+.1f}% | {sig} |"
H = "| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |\n|---|---|---|---|---|---|---|---|"
L = ["# Trend Detective results (event work, Sat 14 Nov 2026 from 9:00 AM ET)", "",
     "Computed on the box CPU with `trends/analyze.py` (Mann-Kendall original test, two-sided, α = 0.05, via pymannkendall 1.4.3; "
     "Sen's slope with a 95% CI after Gilbert 1987; Hamed-Rao autocorrelation-corrected p shown as a robustness check). Annual values, one value per year. "
     "The fire, water and crop sections below use public no-login sources (NASA FIRMS, NASA POWER). The Earthdata layer at the end (GRACE/GRACE-FO, GPM IMERG, GLDAS, SMAP, MODIS MCD64A1) was pulled with a NASA Earthdata Login (`trends/earthdata_trends.py`, `trends/analyze_earthdata.py`, `trends/fetch_gesdisc.py`); provenance per dataset is in `earthdata/EARTHDATA.md`.", "",
     "## Datasets", "",
     "- **Fire:** NASA FIRMS MODIS Collection 6.1 (MCD14ML, Terra + Aqua) and VIIRS S-NPP 375 m (VNP14IMG) country archives for Canada and Argentina, aggregated to 0.25° cell-months by the Hot Spots harmonizer (MODIS type 0, confidence ≥ 30; VIIRS type 0, non-low confidence). Three series per region: harmonized VIIRS-equivalent count (2003–2011 model back-cast + 2012–2025 observed VIIRS), MODIS-only count, and summed MODIS fire radiative power (FRP). VIIRS-only 2012–2025 is also tested. Start year 2003 = first full year with both MODIS satellites (Aqua fire data begin mid-2002). Provinces: Natural Earth 1:50m admin-1 (public domain); each 0.25° cell is assigned by its centre point.",
     "- **Water:** NASA POWER daily `PRECTOTCORR` (bias-corrected precipitation from the MERRA-2 reanalysis), 1981–2025, on the MERRA-2 0.625° × 0.5° grid (35 cells per box). Boxes: eastern Spain incl. Valencia (2°W–1°E, 38–41°N), the SAR Change flood site; southern Ontario incl. Toronto (81–78°W, 43–46°N), a NISAR site in SAR Change. Indices: annual total, Rx1day (wettest day), and days with ≥ 20 mm.",
     "- **Crops:** NASA POWER daily `T2M_MIN`, `T2M_MAX`, `GWETROOT` (root-zone soil wetness) and `PRECTOTCORR` (MERRA-2 based), 1981–2025, central Iowa box (95–92°W, 41–44°N, 35 cells) and the cell nearest Story County (93.75°W, 42.0°N), the Field Shift site. Indices: frost-free season length (days between the last spring and first autumn day with Tmin ≤ 0 °C), last spring / first autumn frost dates, May–Sep corn growing degree days (base 10 °C, cap 30 °C), May–Sep mean root-zone wetness, May–Sep precipitation, Jun–Aug days with Tmax ≥ 32 °C.", ""]
f = d["fire"]
L += ["## Fire: annual active-fire activity, 2003–2025", "", "### Canada (national) and Argentina", "", H]
for reg, r in [("Canada", f["canada"]["Canada"]), ("Argentina", f["argentina"])]:
    L += [row(f"{reg} · harmonized count", r["harmonized_count"]), row(f"{reg} · MODIS-only count", r["modis_count"]), row(f"{reg} · MODIS FRP (GW, summed)", r["modis_frp"]), row(f"{reg} · VIIRS-only count", r["viirs_count"])]
L += ["", "### Canadian provinces and territories", "", H]
for n, r in f["canada"].items():
    if n == "Canada": continue
    if "note" in r: L.append(f"| {n} | – | {r['note']} ({r['modis_total']} MODIS detections) | | | | | |"); continue
    L += [row(f"{n} · harmonized", r["harmonized_count"]), row(f"{n} · MODIS-only", r["modis_count"]), row(f"{n} · MODIS FRP", r["modis_frp"])]
L += ["", "**Reading it:** fire activity is rising significantly across Canada as a whole on all three MODIS-era series and falling significantly in Argentina: the same variable trends in opposite directions in two regions. "
      "At province level the harmonized series is significant in Alberta, British Columbia, New Brunswick, Nova Scotia and Nunavut, but the single-sensor MODIS series is significant in none of them. "
      "The harmonized series joins a model back-cast (2003–2011) to observed VIIRS (2012+), so where only it is significant (especially the small eastern provinces), treat the result as tentative. "
      "The MODIS-only series is the conservative check. VIIRS alone (14 years) shows no significant trend anywhere: the record is too short. Terra's orbit drift after 2020 can also affect late MODIS counts.", ""]
w = d["water"]
L += ["## Water: precipitation, 1981–2025 (NASA POWER / MERRA-2)", "", H]
for reg, lab in [("valencia", "Eastern Spain (Valencia)"), ("ontario", "Southern Ontario (Toronto)")]:
    r = w[reg]
    L += [row(f"{lab} · annual total (mm)", r["annual_total"]), row(f"{lab} · Rx1day (mm)", r["rx1day"]), row(f"{lab} · days ≥ 20 mm", r["days_ge_20mm"])]
L += ["", "Per-cell maps (35 cells each, MK p < 0.05):", ""]
for reg, lab in [("valencia", "Eastern Spain"), ("ontario", "Southern Ontario")]:
    r = w[reg]
    L.append(f"- {lab}: annual total — {r['map_total']['n_sig_increasing']} cells significantly increasing, {r['map_total']['n_sig_decreasing']} decreasing; Rx1day — {r['map_rx1day']['n_sig_increasing']} increasing, {r['map_rx1day']['n_sig_decreasing']} decreasing.")
L += ["", "**Reading it:** the 2024 Valencia DANA flood doesn't show up as a significant long-term trend in eastern Spain's regional precipitation, wettest-day total or heavy-rain days in this reanalysis: one extreme event isn't a trend. At cell level, 8 of 35 cells show a significant rise in annual total, mostly in the south of the box but including the cell over Valencia (0.625°W, 39.5°N); no cell shows a significant rise in the wettest day, and one cell east of Valencia shows a decrease. "
      "Southern Ontario shows significant decreases in MERRA-2 wettest-day totals and heavy-rain days (both also significant after the Hamed-Rao correction); the drop in annual total is significant on the standard test (p = 0.006) but not after the autocorrelation correction (p = 0.052), so treat it as weaker evidence. "
      "Reanalysis precipitation trends can differ from rain-gauge records; the GPM IMERG cross-check is in the Earthdata layer below.", ""]
c = d["crops"]
L += ["## Crops: growing season, 1981–2025 (NASA POWER / MERRA-2)", "", H]
names = {"frost_free_days": "frost-free days", "last_spring_frost_doy": "last spring frost (day of year)", "first_fall_frost_doy": "first autumn frost (day of year)",
         "gdd_may_sep": "May–Sep corn GDD", "rootzone_wetness_may_sep": "May–Sep root-zone wetness", "precip_may_sep": "May–Sep precipitation (mm)", "hot_days_jja": "Jun–Aug days ≥ 32 °C"}
for k, lab in names.items():
    L += [row(f"Central Iowa · {lab}", c[k]["region"]), row(f"Story County cell · {lab}", c[k]["story_cell"])]
L += ["", "Per-cell maps (35 cells, MK p < 0.05): " + "; ".join(f"{lab}: {c[k]['map']['n_sig_increasing']} up / {c[k]['map']['n_sig_decreasing']} down" for k, lab in names.items()) + ".", "",
      "**Reading it:** central Iowa's frost-free season is getting significantly longer, mainly because the first autumn frost comes later (the spring frost date shows no significant change), and May–Sep growing degree days are rising. "
      "Growing-season root-zone wetness, precipitation and hot days show no significant trend. For Field Shift this means more heat and a longer autumn window, which matters for longer-season hybrids and for establishing cover crops after harvest, without a matching change in summer moisture.", "",
      "## Caveats", "", "- Linear-trend tests on annual values; no seasonal decomposition or change-point analysis.",
      "- Mann-Kendall assumes independent years; the Hamed-Rao column corrects for autocorrelation. Significance calls on this site use the standard test; where the two disagree we say so. The Hamed-Rao p is unstable for count series with many tied values (e.g. hot-day counts: MK p ≈ 0.3–0.4 but Hamed-Rao p < 0.001), so we don't treat those as trends.",
      "- Significance at α = 0.05 is not a statement about cause. Trends in reanalysis and fire-detection records can reflect sensor or model changes as well as real change.",
      "- MERRA-2 grid cells are about 55 km; county-scale features are smoothed."]
e = json.load(open(T / "out/earthdata_trends.json"))
def row2(name, t):
    pc = t.get("slope_pct_of_median_per_decade"); pc = f"{pc:+.1f}%" if pc is not None else "–"
    return f"| {name} | {t['years'][0]}–{t['years'][1]} (n={t['n']}) | {t['trend']} | {t['p']:.4f} | {t['p_hamed_rao']:.4f} | {fm(t['sen_slope_per_year'])} [{fm(t['sen_ci95'][0])}, {fm(t['sen_ci95'][1])}] | {pc} | {'yes' if t['significant'] else 'no'} |"
lab = {"valencia": "Eastern Spain (Valencia)", "ontario": "Southern Ontario", "iowa": "Central Iowa"}
EL = ["## Earthdata layer (NASA Earthdata Login)", "",
      "Same tests and conventions as above. Boxes: eastern Spain 2°W–1°E, 38–41°N; southern Ontario 81–78°W, 43–46°N; central Iowa 95–92°W, 41–44°N.", "",
      "### Water storage: GRACE / GRACE-FO (JPL RL06.3 mascon CRI v04, PO.DAAC), 2003–2025", "",
      "Monthly land-cell liquid-water-equivalent thickness, cos-lat weighted box mean, monthly climatology removed, annual mean of years with ≥ 6 months (2017 and 2018 dropped: GRACE→GRACE-FO gap). Units cm; % of median not meaningful for anomalies.", "", H]
EL += [row2(f"{lab[r]} · water storage anomaly (cm)", t) for r, t in e["grace"].items()]
EL += ["", "### Precipitation: GPM IMERG V07 monthly (GPM_3IMERGM, GES DISC), 1998–2024", "",
       "Box-mean monthly totals (mm/hr × hours in month), full calendar years only (Oct–Dec 2025 not yet published).", "", H]
for r, d in e["imerg"].items():
    EL += [row2(f"{lab[r]} · annual total (mm)", d["annual_total"]), row2(f"{lab[r]} · Sep–Nov total (mm)", d["son_total"]), row2(f"{lab[r]} · wettest month (mm)", d["wettest_month"])]
EL += ["", "### Soil moisture: GLDAS Noah 2.1 monthly (GLDAS_NOAH025_M, GES DISC), central Iowa, 2000–2025", "", "May–Sep mean of monthly fields, 144 cells (0.25°).", "", H]
glab = {"SoilMoi0_10cm_inst": "0–10 cm", "SoilMoi10_40cm_inst": "10–40 cm", "SoilMoi40_100cm_inst": "40–100 cm", "RootMoist_inst": "root zone 0–100 cm"}
EL += [row2(f"Central Iowa · {glab[k]} (kg/m²)", t) for k, t in e["gldas_iowa"].items()]
EL += ["", "### Soil moisture: SMAP L3 enhanced 9 km (SPL3SMP_E v006, NSIDC), 2015–2025", "",
       "Daily AM + PM retrievals, recommended quality only, May–Sep mean (years with ≥ 60 valid days). Short record (≤ 11 years): low power to detect trends.", "", H]
EL += [row2(f"{'Central Iowa box' if k == 'central_iowa' else 'Story County cells'} · surface soil moisture (m³/m³)", t) for k, t in e["smap_iowa"].items()]
EL += ["", "### Fire: MODIS MCD64A1 v061 burned area (LP DAAC), tile h11v03, 2003–2025", "",
       "Apr–Oct burned area (km²) over MODIS tile h11v03 (NE British Columbia / Alberta / Saskatchewan boreal, 50–60°N). Details in `earthdata/hot-spots/`.", "", H, row2("Tile h11v03 · burned area Apr–Oct (km²)", e["mcd64_h11v03"])]
EL += ["", "**Reading it:** GRACE shows eastern Spain losing terrestrial water storage (about −0.39 cm/yr, p = 0.002, robust to autocorrelation) and southern Ontario gaining it (+0.55 cm/yr, p = 0.014; the 2019–2021 high years weigh heavily), with no trend in central Iowa. "
       "GPM IMERG shows no significant trend in annual, autumn or wettest-month precipitation in any of the three boxes (1998–2024), consistent with the MERRA-2 result that the 2024 Valencia flood is an extreme event rather than part of a detectable regional trend; for southern Ontario IMERG does not reproduce the MERRA-2 decrease in annual total (MK p = 0.28; the Hamed-Rao p of 0.023 points the other way, upward, so we treat it as no trend), so that reanalysis signal is not confirmed. "
       "Central Iowa soil moisture shows no significant trend in GLDAS (2000–2025, all layers) or SMAP (2015–2025), matching the no-trend POWER root-zone result. "
       "MCD64A1 burned area in the boreal tile is rising significantly (+272 km²/yr, p = 0.004), consistent with the rising FIRMS fire counts for Canada, using a different MODIS product (2023: 28,262 km², the largest year).", "",
       "- GRACE mascons are ~3° (~300 km); a 3° box spans only 2–4 mascons, so these are regional, not local, signals. Southern Ontario's box borders the Great Lakes; lake-level changes can leak into land mascons.",
       "- IMERG and GLDAS boxes include some sea (Valencia) and lake surface (Ontario); GLDAS is a land-surface model driven partly by observations, not a direct measurement.", ""]
L = L[:L.index("## Caveats")] + EL + L[L.index("## Caveats"):]
(T / "RESULTS.md").write_text("\n".join(L) + "\n")
print("ok")
