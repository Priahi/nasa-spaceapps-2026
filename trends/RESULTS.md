# Trend Detective results (event work, Sat 14 Nov 2026 from 9:00 AM ET)

Computed on the box CPU with `trends/analyze.py` (Mann-Kendall original test, two-sided, α = 0.05, via pymannkendall 1.4.3; Sen's slope with a 95% CI after Gilbert 1987; Hamed-Rao autocorrelation-corrected p shown as a robustness check). Annual values, one value per year. The fire, water and crop sections below use public no-login sources (NASA FIRMS, NASA POWER). The Earthdata layer at the end (GRACE/GRACE-FO, GPM IMERG, GLDAS, SMAP, MODIS MCD64A1) was pulled with a NASA Earthdata Login (`trends/earthdata_trends.py`, `trends/analyze_earthdata.py`, `trends/fetch_gesdisc.py`); provenance per dataset is in `earthdata/EARTHDATA.md`.

## Datasets

- **Fire:** NASA FIRMS MODIS Collection 6.1 (MCD14ML, Terra + Aqua) and VIIRS S-NPP 375 m (VNP14IMG) country archives for Canada and Argentina, aggregated to 0.25° cell-months by the Hot Spots harmonizer (MODIS type 0, confidence ≥ 30; VIIRS type 0, non-low confidence). Three series per region: harmonized VIIRS-equivalent count (2003–2011 model back-cast + 2012–2025 observed VIIRS), MODIS-only count, and summed MODIS fire radiative power (FRP). VIIRS-only 2012–2025 is also tested. Start year 2003 = first full year with both MODIS satellites (Aqua fire data begin mid-2002). Provinces: Natural Earth 1:50m admin-1 (public domain); each 0.25° cell is assigned by its centre point.
- **Water:** NASA POWER daily `PRECTOTCORR` (bias-corrected precipitation from the MERRA-2 reanalysis), 1981–2025, on the MERRA-2 0.625° × 0.5° grid (35 cells per box). Boxes: eastern Spain incl. Valencia (2°W–1°E, 38–41°N), the SAR Change flood site; southern Ontario incl. Toronto (81–78°W, 43–46°N), a NISAR site in SAR Change. Indices: annual total, Rx1day (wettest day), and days with ≥ 20 mm.
- **Crops:** NASA POWER daily `T2M_MIN`, `T2M_MAX`, `GWETROOT` (root-zone soil wetness) and `PRECTOTCORR` (MERRA-2 based), 1981–2025, central Iowa box (95–92°W, 41–44°N, 35 cells) and the cell nearest Story County (93.75°W, 42.0°N), the Field Shift site. Indices: frost-free season length (days between the last spring and first autumn day with Tmin ≤ 0 °C), last spring / first autumn frost dates, May–Sep corn growing degree days (base 10 °C, cap 30 °C), May–Sep mean root-zone wetness, May–Sep precipitation, Jun–Aug days with Tmax ≥ 32 °C.

## Fire: annual active-fire activity, 2003–2025

### Canada (national) and Argentina

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Canada · harmonized count | 2003–2025 | increasing | 0.0201 | 0.0019 | +18,497 [+1,122, +31,718] | +94.4% | yes |
| Canada · MODIS-only count | 2003–2025 | increasing | 0.0346 | 0.0048 | +3,019 [+81.00, +5,184] | +67.2% | yes |
| Canada · MODIS FRP (GW, summed) | 2003–2025 | increasing | 0.0112 | 0.0008 | +367 [+64.42, +653] | +73.8% | yes |
| Canada · VIIRS-only count | 2012–2025 | no trend | 0.2284 | 0.2284 | +32,582 [-16,076, +79,604] | +106.1% | no |
| Argentina · harmonized count | 2003–2025 | decreasing | 0.0043 | 0.0043 | -6,095 [-10,930, -2,444] | -32.9% | yes |
| Argentina · MODIS-only count | 2003–2025 | decreasing | 0.0006 | 0.0006 | -1,909 [-3,120, -1,122] | -32.1% | yes |
| Argentina · MODIS FRP (GW, summed) | 2003–2025 | decreasing | 0.0051 | 0.0051 | -101 [-182, -45.94] | -28.2% | yes |
| Argentina · VIIRS-only count | 2012–2025 | no trend | 1.0000 | 1.0000 | -196 [-5,353, +8,862] | -1.2% | no |

### Canadian provinces and territories

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Alberta · harmonized | 2003–2025 | increasing | 0.0346 | 0.0346 | +1,503 [+62.50, +3,718] | +82.0% | yes |
| Alberta · MODIS-only | 2003–2025 | no trend | 0.1256 | 0.1256 | +200 [-65.85, +812] | +48.5% | no |
| Alberta · MODIS FRP | 2003–2025 | no trend | 0.1130 | 0.1130 | +27.86 [-9.76, +143] | +62.9% | no |
| British Columbia · harmonized | 2003–2025 | increasing | 0.0447 | 0.0447 | +2,587 [+2.61, +7,521] | +78.3% | yes |
| British Columbia · MODIS-only | 2003–2025 | no trend | 0.1391 | 0.1391 | +362 [-95.00, +1,717] | +39.2% | no |
| British Columbia · MODIS FRP | 2003–2025 | no trend | 0.1130 | 0.1130 | +77.37 [-12.70, +217] | +91.6% | no |
| Manitoba · harmonized | 2003–2025 | no trend | 0.1696 | 0.1696 | +453 [-274, +1,520] | +37.5% | no |
| Manitoba · MODIS-only | 2003–2025 | no trend | 1.0000 | 1.0000 | +0.7500 [-153, +167] | +0.2% | no |
| Manitoba · MODIS FRP | 2003–2025 | no trend | 0.5974 | 0.5974 | +3.52 [-10.72, +17.18] | +16.2% | no |
| New Brunswick · harmonized | 2003–2025 | increasing | 0.0162 | 0.0012 | +8.65 [+1.76, +16.40] | +60.2% | yes |
| New Brunswick · MODIS-only | 2003–2025 | no trend | 0.3681 | 0.3681 | +0.2222 [-0.6875, +2.00] | +4.9% | no |
| New Brunswick · MODIS FRP | 2003–2025 | no trend | 0.5612 | 0.5612 | +0.0217 [-0.0363, +0.1434] | +18.1% | no |
| Newfoundland and Labrador · harmonized | 2003–2025 | no trend | 0.7917 | 0.7917 | +1.14 [-38.16, +34.84] | +6.2% | no |
| Newfoundland and Labrador · MODIS-only | 2003–2025 | no trend | 0.9159 | 0.8935 | +0.1765 [-9.13, +9.40] | +1.5% | no |
| Newfoundland and Labrador · MODIS FRP | 2003–2025 | no trend | 0.7116 | 0.7116 | -0.0434 [-1.13, +0.9579] | -3.0% | no |
| Nova Scotia · harmonized | 2003–2025 | increasing | 0.0004 | 0.0000 | +5.31 [+2.44, +10.42] | +82.9% | yes |
| Nova Scotia · MODIS-only | 2003–2025 | no trend | 0.8320 | 0.8320 | +0.3125 [-0.6667, +1.50] | +16.4% | no |
| Nova Scotia · MODIS FRP | 2003–2025 | no trend | 0.6726 | 0.6726 | +0.0051 [-0.0108, +0.0710] | +17.6% | no |
| Northwest Territories · harmonized | 2003–2025 | no trend | 0.0725 | 0.1134 | +2,725 [-115, +8,006] | +136.9% | no |
| Northwest Territories · MODIS-only | 2003–2025 | no trend | 0.0725 | 0.0160 | +446 [-23.20, +1,126] | +117.2% | no |
| Northwest Territories · MODIS FRP | 2003–2025 | no trend | 0.0572 | 0.0961 | +52.27 [-0.6800, +146] | +129.8% | no |
| Nunavut · harmonized | 2003–2025 | increasing | 0.0369 | 0.0023 | +1.67 [+0.1100, +5.98] | +59.5% | yes |
| Nunavut · MODIS-only | 2003–2025 | no trend | 0.4745 | 0.4745 | +0.2000 [-0.4286, +1.20] | +22.2% | no |
| Nunavut · MODIS FRP | 2003–2025 | no trend | 0.5974 | 0.4219 | +0.0022 [-0.0096, +0.0235] | +15.2% | no |
| Ontario · harmonized | 2003–2025 | no trend | 0.1130 | 0.0176 | +348 [-63.40, +1,534] | +61.4% | no |
| Ontario · MODIS-only | 2003–2025 | no trend | 0.6345 | 0.4835 | +26.45 [-39.69, +188] | +23.8% | no |
| Ontario · MODIS FRP | 2003–2025 | no trend | 0.5612 | 0.3543 | +2.39 [-4.44, +23.41] | +32.4% | no |
| Prince Edward Island | – | too few detections for a trend test (124 MODIS detections) | | | | | |
| Québec · harmonized | 2003–2025 | no trend | 0.6726 | 0.6726 | -37.49 [-329, +140] | -14.9% | no |
| Québec · MODIS-only | 2003–2025 | no trend | 0.3417 | 0.3417 | -20.00 [-72.40, +17.60] | -40.4% | no |
| Québec · MODIS FRP | 2003–2025 | no trend | 0.5974 | 0.5974 | -1.13 [-9.58, +4.25] | -19.8% | no |
| Saskatchewan · harmonized | 2003–2025 | no trend | 0.1015 | 0.1015 | +2,382 [-222, +6,882] | +114.8% | no |
| Saskatchewan · MODIS-only | 2003–2025 | no trend | 0.2908 | 0.2908 | +297 [-101, +1,059] | +51.2% | no |
| Saskatchewan · MODIS FRP | 2003–2025 | no trend | 0.1867 | 0.1867 | +24.66 [-14.47, +111] | +46.0% | no |
| Yukon · harmonized | 2003–2025 | no trend | 0.6345 | 0.6345 | +130 [-551, +876] | +12.9% | no |
| Yukon · MODIS-only | 2003–2025 | no trend | 0.4923 | 0.4923 | +32.00 [-89.88, +265] | +11.0% | no |
| Yukon · MODIS FRP | 2003–2025 | no trend | 0.5262 | 0.3564 | +4.99 [-13.87, +24.03] | +18.0% | no |

**Reading it:** fire activity is rising significantly across Canada as a whole on all three MODIS-era series and falling significantly in Argentina: the same variable trends in opposite directions in two regions. At province level the harmonized series is significant in Alberta, British Columbia, New Brunswick, Nova Scotia and Nunavut, but the single-sensor MODIS series is significant in none of them. The harmonized series joins a model back-cast (2003–2011) to observed VIIRS (2012+), so where only it is significant (especially the small eastern provinces), treat the result as tentative. The MODIS-only series is the conservative check. VIIRS alone (14 years) shows no significant trend anywhere: the record is too short. Terra's orbit drift after 2020 can also affect late MODIS counts.

## Water: precipitation, 1981–2025 (NASA POWER / MERRA-2)

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Eastern Spain (Valencia) · annual total (mm) | 1981–2025 | no trend | 0.2444 | 0.2444 | +0.9920 [-0.7526, +3.02] | +2.4% | no |
| Eastern Spain (Valencia) · Rx1day (mm) | 1981–2025 | no trend | 0.2776 | 0.2776 | +0.0801 [-0.0913, +0.2244] | +2.5% | no |
| Eastern Spain (Valencia) · days ≥ 20 mm | 1981–2025 | no trend | 0.4395 | 0.4395 | +0.0081 [-0.0135, +0.0321] | +3.8% | no |
| Southern Ontario (Toronto) · annual total (mm) | 1981–2025 | decreasing | 0.0056 | 0.0522 | -3.73 [-6.48, -1.22] | -5.3% | yes |
| Southern Ontario (Toronto) · Rx1day (mm) | 1981–2025 | decreasing | 0.0000 | 0.0000 | -0.2391 [-0.3155, -0.1483] | -9.6% | yes |
| Southern Ontario (Toronto) · days ≥ 20 mm | 1981–2025 | decreasing | 0.0000 | 0.0000 | -0.0597 [-0.0827, -0.0413] | -29.4% | yes |

Per-cell maps (35 cells each, MK p < 0.05):

- Eastern Spain: annual total — 8 cells significantly increasing, 0 decreasing; Rx1day — 0 increasing, 1 decreasing.
- Southern Ontario: annual total — 2 cells significantly increasing, 15 decreasing; Rx1day — 0 increasing, 23 decreasing.

**Reading it:** the 2024 Valencia DANA flood doesn't show up as a significant long-term trend in eastern Spain's regional precipitation, wettest-day total or heavy-rain days in this reanalysis: one extreme event isn't a trend. At cell level, 8 of 35 cells show a significant rise in annual total, mostly in the south of the box but including the cell over Valencia (0.625°W, 39.5°N); no cell shows a significant rise in the wettest day, and one cell east of Valencia shows a decrease. Southern Ontario shows significant decreases in MERRA-2 wettest-day totals and heavy-rain days (both also significant after the Hamed-Rao correction); the drop in annual total is significant on the standard test (p = 0.006) but not after the autocorrelation correction (p = 0.052), so treat it as weaker evidence. Reanalysis precipitation trends can differ from rain-gauge records; the GPM IMERG cross-check is in the Earthdata layer below.

## Crops: growing season, 1981–2025 (NASA POWER / MERRA-2)

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Central Iowa · frost-free days | 1981–2025 | increasing | 0.0056 | 0.0003 | +0.4288 [+0.1177, +0.6686] | +2.5% | yes |
| Story County cell · frost-free days | 1981–2025 | increasing | 0.0024 | 0.0000 | +0.4714 [+0.1818, +0.7143] | +2.8% | yes |
| Central Iowa · last spring frost (day of year) | 1981–2025 | no trend | 0.4812 | 0.1605 | -0.0770 [-0.2752, +0.1388] | -0.7% | no |
| Story County cell · last spring frost (day of year) | 1981–2025 | no trend | 0.4161 | 0.4161 | -0.0960 [-0.3077, +0.1600] | -0.9% | no |
| Central Iowa · first autumn frost (day of year) | 1981–2025 | increasing | 0.0001 | 0.0001 | +0.3951 [+0.2000, +0.6020] | +1.4% | yes |
| Story County cell · first autumn frost (day of year) | 1981–2025 | increasing | 0.0033 | 0.0033 | +0.3815 [+0.1304, +0.6111] | +1.3% | yes |
| Central Iowa · May–Sep corn GDD | 1981–2025 | increasing | 0.0004 | 0.0004 | +4.63 [+2.27, +6.75] | +3.0% | yes |
| Story County cell · May–Sep corn GDD | 1981–2025 | increasing | 0.0005 | 0.0005 | +5.57 [+2.79, +7.91] | +3.5% | yes |
| Central Iowa · May–Sep root-zone wetness | 1981–2025 | no trend | 0.5122 | 0.6000 | -0.0004 [-0.0017, +0.0011] | -0.7% | no |
| Story County cell · May–Sep root-zone wetness | 1981–2025 | no trend | 0.1648 | 0.1648 | -0.0012 [-0.0027, +0.0004] | -2.4% | no |
| Central Iowa · May–Sep precipitation (mm) | 1981–2025 | no trend | 0.5507 | 0.1998 | -0.9277 [-3.43, +2.57] | -1.8% | no |
| Story County cell · May–Sep precipitation (mm) | 1981–2025 | no trend | 0.3137 | 0.0281 | -1.77 [-4.91, +1.77] | -3.4% | no |
| Central Iowa · Jun–Aug days ≥ 32 °C | 1981–2025 | no trend | 0.4057 | 0.0000 | +0.0741 [-0.1225, +0.3500] | +7.3% | no |
| Story County cell · Jun–Aug days ≥ 32 °C | 1981–2025 | no trend | 0.2805 | 0.0000 | +0.1177 [-0.0833, +0.4688] | +8.4% | no |

Per-cell maps (35 cells, MK p < 0.05): frost-free days: 29 up / 0 down; last spring frost (day of year): 0 up / 0 down; first autumn frost (day of year): 35 up / 0 down; May–Sep corn GDD: 35 up / 0 down; May–Sep root-zone wetness: 0 up / 0 down; May–Sep precipitation (mm): 0 up / 0 down; Jun–Aug days ≥ 32 °C: 0 up / 0 down.

**Reading it:** central Iowa's frost-free season is getting significantly longer, mainly because the first autumn frost comes later (the spring frost date shows no significant change), and May–Sep growing degree days are rising. Growing-season root-zone wetness, precipitation and hot days show no significant trend. For Field Shift this means more heat and a longer autumn window, which matters for longer-season hybrids and for establishing cover crops after harvest, without a matching change in summer moisture.

## Earthdata layer (NASA Earthdata Login)

Same tests and conventions as above. Boxes: eastern Spain 2°W–1°E, 38–41°N; southern Ontario 81–78°W, 43–46°N; central Iowa 95–92°W, 41–44°N.

### Water storage: GRACE / GRACE-FO (JPL RL06.3 mascon CRI v04, PO.DAAC), 2003–2025

Monthly land-cell liquid-water-equivalent thickness, cos-lat weighted box mean, monthly climatology removed, annual mean of years with ≥ 6 months (2017 and 2018 dropped: GRACE→GRACE-FO gap). Units cm; % of median not meaningful for anomalies.

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Eastern Spain (Valencia) · water storage anomaly (cm) | 2003–2025 (n=21) | decreasing | 0.0019 | 0.0019 | -0.3853 [-0.6054, -0.1408] | – | yes |
| Southern Ontario · water storage anomaly (cm) | 2003–2025 (n=21) | increasing | 0.0144 | 0.0395 | +0.5468 [+0.1019, +0.9984] | – | yes |
| Central Iowa · water storage anomaly (cm) | 2003–2025 (n=21) | no trend | 0.5661 | 0.5511 | -0.1224 [-0.5239, +0.5608] | – | no |

### Precipitation: GPM IMERG V07 monthly (GPM_3IMERGM, GES DISC), 1998–2024

Box-mean monthly totals (mm/hr × hours in month), full calendar years only (Oct–Dec 2025 not yet published).

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Eastern Spain (Valencia) · annual total (mm) | 1998–2024 (n=27) | no trend | 0.6169 | 0.6169 | +1.78 [-4.40, +6.37] | +3.6% | no |
| Eastern Spain (Valencia) · Sep–Nov total (mm) | 1998–2024 (n=27) | no trend | 0.8025 | 0.8025 | +0.4322 [-3.24, +3.18] | +2.2% | no |
| Eastern Spain (Valencia) · wettest month (mm) | 1998–2024 (n=27) | no trend | 0.2110 | 0.2110 | +0.8063 [-0.7469, +2.35] | +7.5% | no |
| Southern Ontario · annual total (mm) | 1998–2024 (n=27) | no trend | 0.2783 | 0.0227 | +2.11 [-2.55, +7.12] | +2.2% | no |
| Southern Ontario · Sep–Nov total (mm) | 1998–2024 (n=27) | no trend | 0.7075 | 0.7075 | -0.7287 [-4.36, +2.99] | -2.9% | no |
| Southern Ontario · wettest month (mm) | 1998–2024 (n=27) | no trend | 0.3590 | 0.3590 | +0.4162 [-0.5347, +1.52] | +3.0% | no |
| Central Iowa · annual total (mm) | 1998–2024 (n=27) | no trend | 0.5047 | 0.5450 | -3.11 [-11.74, +6.33] | -3.1% | no |
| Central Iowa · Sep–Nov total (mm) | 1998–2024 (n=27) | no trend | 0.2783 | 0.2102 | +1.47 [-1.72, +5.71] | +6.7% | no |
| Central Iowa · wettest month (mm) | 1998–2024 (n=27) | no trend | 0.0874 | 0.0874 | -2.28 [-4.73, +0.3036] | -12.4% | no |

### Soil moisture: GLDAS Noah 2.1 monthly (GLDAS_NOAH025_M, GES DISC), central Iowa, 2000–2025

May–Sep mean of monthly fields, 144 cells (0.25°).

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Central Iowa · 0–10 cm (kg/m²) | 2000–2025 (n=26) | no trend | 0.2704 | 0.2704 | -0.0591 [-0.2050, +0.0823] | -2.0% | no |
| Central Iowa · 10–40 cm (kg/m²) | 2000–2025 (n=26) | no trend | 0.3780 | 0.3780 | -0.1857 [-0.6939, +0.3128] | -2.2% | no |
| Central Iowa · 40–100 cm (kg/m²) | 2000–2025 (n=26) | no trend | 0.3780 | 0.3780 | -0.4897 [-1.64, +0.8853] | -2.9% | no |
| Central Iowa · root zone 0–100 cm (kg/m²) | 2000–2025 (n=26) | no trend | 0.3546 | 0.3546 | -0.8052 [-2.54, +1.27] | -2.9% | no |

### Soil moisture: SMAP L3 enhanced 9 km (SPL3SMP_E v006, NSIDC), 2015–2025

Daily AM + PM retrievals, recommended quality only, May–Sep mean (years with ≥ 60 valid days). Short record (≤ 11 years): low power to detect trends.

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Central Iowa box · surface soil moisture (m³/m³) | 2015–2025 (n=11) | no trend | 0.2129 | 0.2129 | -0.0015 [-0.0062, +0.0029] | -7.3% | no |
| Story County cells · surface soil moisture (m³/m³) | 2015–2025 (n=10) | no trend | 0.4743 | 0.4743 | -0.0007 [-0.0061, +0.0046] | -3.4% | no |

### Fire: MODIS MCD64A1 v061 burned area (LP DAAC), tile h11v03, 2003–2025

Apr–Oct burned area (km²) over MODIS tile h11v03 (NE British Columbia / Alberta / Saskatchewan boreal, 50–60°N). Details in `earthdata/hot-spots/`.

| Series | Period | MK result | p | p (Hamed-Rao) | Sen's slope / yr [95% CI] | per decade, % of median | p < 0.05 |
|---|---|---|---|---|---|---|---|
| Tile h11v03 · burned area Apr–Oct (km²) | 2003–2025 (n=23) | increasing | 0.0043 | 0.0043 | +272 [+56.98, +503] | +140.3% | yes |

**Reading it:** GRACE shows eastern Spain losing terrestrial water storage (about −0.39 cm/yr, p = 0.002, robust to autocorrelation) and southern Ontario gaining it (+0.55 cm/yr, p = 0.014; the 2019–2021 high years weigh heavily), with no trend in central Iowa. GPM IMERG shows no significant trend in annual, autumn or wettest-month precipitation in any of the three boxes (1998–2024), consistent with the MERRA-2 result that the 2024 Valencia flood is an extreme event rather than part of a detectable regional trend; for southern Ontario IMERG does not reproduce the MERRA-2 decrease in annual total (MK p = 0.28; the Hamed-Rao p of 0.023 points the other way, upward, so we treat it as no trend), so that reanalysis signal is not confirmed. Central Iowa soil moisture shows no significant trend in GLDAS (2000–2025, all layers) or SMAP (2015–2025), matching the no-trend POWER root-zone result. MCD64A1 burned area in the boreal tile is rising significantly (+272 km²/yr, p = 0.004), consistent with the rising FIRMS fire counts for Canada, using a different MODIS product (2023: 28,262 km², the largest year).

- GRACE mascons are ~3° (~300 km); a 3° box spans only 2–4 mascons, so these are regional, not local, signals. Southern Ontario's box borders the Great Lakes; lake-level changes can leak into land mascons.
- IMERG and GLDAS boxes include some sea (Valencia) and lake surface (Ontario); GLDAS is a land-surface model driven partly by observations, not a direct measurement.

## Caveats

- Linear-trend tests on annual values; no seasonal decomposition or change-point analysis.
- Mann-Kendall assumes independent years; the Hamed-Rao column corrects for autocorrelation. Significance calls on this site use the standard test; where the two disagree we say so. The Hamed-Rao p is unstable for count series with many tied values (e.g. hot-day counts: MK p ≈ 0.3–0.4 but Hamed-Rao p < 0.001), so we don't treat those as trends.
- Significance at α = 0.05 is not a statement about cause. Trends in reanalysis and fire-detection records can reflect sensor or model changes as well as real change.
- MERRA-2 grid cells are about 55 km; county-scale features are smoothed.
