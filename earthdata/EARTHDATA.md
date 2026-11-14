# Earthdata provenance (Sat 14 Nov 2026)

All downloads below used the team's NASA Earthdata Login account through `~/.netrc` (written from an environment variable by `trends/setup_netrc.py`; the password is never printed or stored in this repo). Before Earthdata was added, the three modules (Hot Spots, SAR Change, Field Shift) used only public no-login data: FIRMS MODIS/VIIRS archives, Sentinel-1 RTC, NISAR browse PNGs, MODIS NDVI and NASA POWER.

GES DISC (GPM IMERG, GLDAS) returned 401/403 "pre-authorization required" until the NASA GESDISC DATA ARCHIVE application was approved on the account at 10:22 AM ET. After that, the full pulls succeeded.

## Summary table

| Module / layer | Dataset (DAAC) | Earthdata login | What was actually processed | Result |
|---|---|---|---|---|
| Hot Spots (original) | FIRMS MCD14ML MODIS C6.1 + VNP14IMG VIIRS archives | no | Canada / Argentina 0.25° cell-months, harmonized count 2003–2025 | Canada rising, Argentina falling (see trends/RESULTS.md) |
| SAR Change (original) | Sentinel-1 RTC; NISAR browse PNGs | no | Valencia 26 Oct vs 7 Nov 2024 change; NISAR plugin preview | unchanged |
| Field Shift (original) | MODIS NDVI; NASA POWER | no | Story County crop-rotation signal | unchanged |
| **Hot Spots + Earthdata** | MCD64A1 v061 burned area (LP DAAC) | **yes** | 161 monthly granules, tile h11v03 (NE B.C. / Alberta / Saskatchewan boreal, 50–60°N), Apr–Oct 2003–2025, 500 m burn-date pixels to km² | 106,035 km² burned 2003–2025; 2023 largest at 28,262 km²; MK increasing p = 0.0043, Sen +272 km²/yr [95% CI +57, +503] |
| **SAR Change + Earthdata** | OPERA L3 DSWx-S1 v1 (PO.DAAC) | **yes** | 44 files (B01_WTR + B03_CONF), tiles T30SYJ/T31SBD, 21 acquisitions 1 Oct–19 Nov 2024, AOI 0.75–0.2°W, 39.2–39.55°N; "usual water" = water in ≥ 80% of valid looks 1–28 Oct | New water outside usual water: 30.7 km² (26 Oct asc) → 77.7 km² (31 Oct asc), then 54.3 km² (1 Nov) and 40.6 km² (6 Nov) |
| **Field Shift + Earthdata (HLS)** | HLS v2.0 HLSL30 + HLSS30 (LP DAAC) | **yes** | 5 scenes, tile T15TVG, ≤ 5% cloud (red, NIR, Fmask), Story County bbox; NDVI with Fmask cloud/shadow/snow/water removed | Mid-summer NDVI median 0.90–0.91 in all scenes; 1 Aug 2024 vs 31 Jul 2025: median change −0.01 over 866 km² vegetated; 42.1 km² up > 0.1, 22.4 km² down > 0.1 |
| **Field Shift + Earthdata (SMAP)** | SMAP SPL3SMP_E v006, 9 km (NSIDC) | **yes** | 1,602 daily granules May–Sep 2015–2025, OPeNDAP subset (central Iowa, 32×33 EASE2 cells), AM+PM, recommended quality | Story County May–Sep mean 0.164–0.219 m³/m³; no trend (p = 0.47, n = 10); central Iowa no trend (p = 0.21, n = 11) |
| **Trend layer: GRACE/GRACE-FO** | TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4 (PO.DAAC) | **yes** | Global mascon file Apr 2002–Sep 2026 (46 MB, sha256 3522dd57…); land cells, deseasonalised annual means 2003–2025 (2017–18 gap) | Valencia decreasing −0.39 cm/yr (p = 0.0019); southern Ontario increasing +0.55 cm/yr (p = 0.014); central Iowa no trend (p = 0.57) |
| **Trend layer: GPM IMERG** | GPM_3IMERGM V07 (GES DISC) | **yes** | 999 monthly OPeNDAP subsets (Jan 1998–Sep 2025), 0.1°, three 3° boxes; trends on full years 1998–2024 (Oct–Dec 2025 not yet published: 404) | No significant trend in annual, Sep–Nov or wettest-month totals for Valencia, Ontario or Iowa; MERRA-2 Ontario annual decrease not confirmed |
| **Trend layer: GLDAS** | GLDAS_NOAH025_M v2.1 (GES DISC) | **yes** | 312 monthly OPeNDAP subsets, central Iowa (144 cells), May–Sep 2000–2025, 4 soil layers | No significant trend in any layer (p = 0.27–0.38) |

Statistics: Mann-Kendall (original + Hamed-Rao) and Sen's slope with 95% CI, α = 0.05, using `trend()` from `trends/analyze.py`.

## Per-module details

### Hot Spots: `earthdata/hot-spots/`
- `mcd64_h11v03.py` writes `mcd64_h11v03.json` (annual km², unmapped fraction per year, trend), `mcd64_annual_burned_area.png` and `mcd64_last_burn_year_map.png`.
- Raw data: `upgrades/mcd64/` (161 HDF4 files, 800 MB).
- Annual Apr–Oct km²: 2003 1,826 · 2015 10,649 · 2016 4,355 · 2019 4,920 · 2021 6,370 · 2023 28,262 · 2024 10,866 · 2025 12,560 (full list in the JSON).
- Caveats: this is one MODIS tile, not all of Canada. Pixel area is the 500 m sinusoidal cell (0.21466 km²).

### SAR Change: `earthdata/sar-change/`
- Processed by the site worker with `opera_valencia.py`, which writes `opera_valencia.json`, `opera_before_20241026.png` and `opera_after_20241031.png`.
- Raw data: `upgrades/opera/` (38 MB).
- Caveats:
  - The extra water is concentrated in the Albufera rice-paddy belt around the lake.
  - New water was already rising before the flood, from 4 km² on 1 Oct to 31 km² on 26 Oct, so the flood signal is the jump to 77.7 km² on 31 Oct.
  - SAR water products under-detect water in built-up areas, so the urban flooding in l'Horta Sud is under-represented.
  - The 19 Nov T30SYJ look has only 29.5% valid pixels and should be ignored.
- NISAR GCOV doesn't exist for this event. The NISAR GCOV collections at ASF begin Oct 2025, after the Oct 2024 flood, and CMR has no granules for this AOI.

### Field Shift: `earthdata/field-shift/`
- HLS: `hls_story.py` writes `hls_story_county.json` and `hls_story_county_ndvi.png`. Raw data: `upgrades/hls/` (201 MB).
  - Single mid-summer dates are near NDVI saturation, so the map shows field-by-field contrast, not crop type.
  - The 1 Aug 2024 Sentinel-2 scene covers only about 60% of the bbox.
- SMAP: `fetch_smap.py` downloads the data and `smap_story.py` writes `smap_story_county.json` (daily series, May–Sep means, trends), `smap_story_county_daily.png`, `ed_smap_story_county.png` and `ed_smap_central_iowa.png`. Raw data: `field-shift/raw/smap/` (57 MB).
  - The record covers only 11 seasons, so the test has low power.
  - In 2022 the Story County cells had only 57 valid days, below the 60-day threshold, so that year is excluded from the Story County trend.

### Trend layer: `trends/` (copies in `earthdata/trends/`)
- Scripts: `trends/fetch_gesdisc.py` (IMERG + GLDAS OPeNDAP subsets into `trends/raw/gesdisc/`, 47 MB), `trends/analyze_earthdata.py` (writes `trends/out/trends.json["earthdata"]`) and `trends/earthdata_trends.py` (writes `trends/out/earthdata_trends.json` + `ed_*.png`).
- Charts: `ed_grace_{valencia,ontario,iowa}.png`, `ed_imerg_{region}_{annual_total,son_total,wettest_month}.png`, `ed_gldas_iowa_*.png` and `ed_smap_*.png`.
- `trends/RESULTS.md` is regenerated by `trends/write_results.py` and now includes the "Earthdata layer" section.

Total Earthdata volume downloaded: about 1.2 GB.
