# NASA Space Apps 2026: project submission text (draft, NOT submitted)

**Team:** GeoAI Toronto · **Member:** Parsa Riahi (solo) · **Local event:** Toronto
**Challenge:** Be An Earth System Trend Detective! (https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/)
**Deadline:** Sun 15 Nov 2026, 11:59 PM ET

Paste each section into the matching field. Every number comes from `trends/RESULTS.md`, `earthdata/EARTHDATA.md`, `trends/out/trends.json`, `earthdata/*/*.json` or the demos' results files (mirrored in `src/content.py`). The three outside "stakes" figures are quoted from the sources listed under References.

---

## Project Name
Orbit to Ground: Earth-change intelligence from orbit to decision

## High-Level Summary
*(about 150 words; the form asks for a short summary)*

Orbit to Ground is one connected system that turns NASA satellite data into decisions, built as three working modules and a shared trend engine. **Detect:** Hot Spots harmonizes MODIS and VIIRS active fires into one 2000–2025 record, so fire seasons can be compared across the 2012 sensor switch. **Confirm:** SAR Change maps the October 2024 Valencia flood with radar, which sees through cloud and at night, and is set up for NISAR. **Adapt:** Field Shift predicts next season's crop in Story County, Iowa, and ranks four-year rotations by a farmer's priorities. A Trend Detective layer answers the challenge's four questions for each module: what is changing, where, how much (Sen's slope with a 95% CI) and is it significant (Mann-Kendall). Findings: Canada's fire detections are rising (p = 0.035), confirmed by burned area; Valencia's rain isn't trending (p = 0.28) while its water storage is falling (p = 0.002); Iowa's frost-free season is getting longer (p = 0.006).

## Link to Project Demo
- 28-second video (1920×1080, captioned): https://nasa-spaceapps-2026.pages.dev/submission/demo.mp4 (captions: https://nasa-spaceapps-2026.pages.dev/submission/demo.en.srt; also playable on the home page: https://nasa-spaceapps-2026.pages.dev/#demo-video)
- 7-slide deck (alternative or supporting): https://nasa-spaceapps-2026.pages.dev/submission/deck.pdf

## Link to Final Project
https://nasa-spaceapps-2026.pages.dev

Full-screen live tools: https://nasa-spaceapps-2026.pages.dev/hotspots/app/ · https://nasa-spaceapps-2026.pages.dev/sar-change/app/ · https://nasa-spaceapps-2026.pages.dev/field-shift/app/
Code (public, Apache-2.0): https://github.com/Priahi/nasa-spaceapps-2026

## Detailed Project Description

### WHY: the problem
Earth is changing fast, and satellites already see it, but the evidence rarely reaches a decision intact. In 2023, more than 14.6 million hectares of Canada's forest burned and over 230,000 people were evacuated (Natural Resources Canada). The October–November 2024 DANA floods in Spain caused 230 confirmed deaths, 222 of them in the Valencia region (Government of Spain). And 33% of the world's land is moderately to highly degraded (FAO). Three gaps stand between the data and the people who act on it:

- **Detect (fire):** NASA's fire record switches sensors in 2012. MODIS (1 km, from 2000) and VIIRS (375 m, from 2012) count fire differently: over Canada since 2012, VIIRS reports about 5.6 detections for every MODIS detection. So a fire manager can't fairly compare a 2005 season with a 2023 one, or trust a 25-year trend.
- **Confirm (water):** floods arrive with the clouds. Optical satellites see cloud, not water. Radar sees through cloud, day and night, but radar images are hard to read for non-specialists, and a single flood map can't say whether floods are a trend.
- **Adapt (farms):** the rotation a farmer chooses shapes the soil for years, while frost dates, heat and moisture shift underneath it. The evidence for one field is scattered across agencies and formats.

Behind all three is the challenge's question: one dramatic image can't tell anyone whether something is a trend.

### WHAT: one system, three working modules, one trend engine
Orbit to Ground runs from orbit to decision: NASA observations → a module that turns them into a usable map or model → a Trend Detective engine that issues a verdict → the person who decides (fire manager, flood responder, farmer). Every module page has the full live tool (embedded, plus full screen at `/app/`), its problem statement, results, honest misses, and an interactive trend widget: pick a region and a variable, and a verdict panel answers **what is changing, where, how much and is it significant**.

**01 Detect: Hot Spots Harmonizer.** One harmonized 2000–2025 fire calendar for any area you draw, with calibrated uncertainty and unusual-month flags. 11,616,131 NASA FIRMS detections (MODIS C6.1 and VIIRS S-NPP, Canada and Argentina) on a 0.25° grid. An empirical-Bayes per-cell ratio is the baseline; a LightGBM model corrects it (trained 2012–2020, tuned 2021, tested 2022–2025). On Canada's held-out data it has 8.5% lower error than the best baseline (RMSE 0.2844 vs 0.3109); in Argentina 6.1% lower. Conformal intervals reach 88.6% coverage against a 90% target. Honest miss: Canada's monthly-total error is worse than the baseline (39.4% vs 16.7%).
*Trend verdict:* Canada's annual fire activity is rising on all three MODIS-era series, 2003–2025: MODIS detections +3,019 a year (95% CI +81 to +5,184, p = 0.035), harmonized count +18,497 a year (p = 0.020), summed MODIS fire radiative power +367 GW a year (p = 0.011), all still significant after the Hamed-Rao autocorrelation check. Argentina is falling (MODIS −1,909 a year, p < 0.001): same variable, opposite direction. An independent NASA product agrees: MODIS MCD64A1 burned area over tile h11v03 (the boreal forest of northeast British Columbia, Alberta and Saskatchewan, 50–60°N, Apr–Oct) rises by about 272 km² a year (95% CI +57 to +503, p = 0.0043), with 2023 the largest year (28,262 km² of 106,035 km² burned over 2003–2025). This is one MODIS tile, not all of Canada. At province level the harmonized series is significant in Alberta, British Columbia, New Brunswick, Nova Scotia and Nunavut but MODIS alone is significant in none, so we label those calls tentative. VIIRS alone (14 years) is too short to show any significant trend, which is exactly why a harmonized long record is needed.

**02 Confirm: SAR Change (Valencia, NISAR-ready).** An interactive radar flood viewer for the 29 October 2024 DANA flood: before/after swipe, time-lapse and change map from 26 Sentinel-1 RTC passes on four orbit tracks. A U-Net trained on Sen1Floods11 reaches 66.4% water IoU on the official hand-labelled test split, against 21.8% for per-chip Otsu (about 3×). As an independent check we added NASA/JPL OPERA DSWx-S1 radar water maps (21 acquisitions, 1 Oct–19 Nov 2024): new water outside the usual-water mask jumps from 30.7 km² on 26 Oct to 77.7 km² on 31 Oct, two days after the flood, then falls to 54.3 km² (1 Nov) and 40.6 km² (6 Nov). Caveats we show: the extra water is concentrated in the Albufera rice-paddy belt; new water was already rising before the flood (4 km² on 1 Oct), so the flood signal is the jump; and radar water products under-detect water in built-up areas, so the urban flooding in l'Horta Sud is under-represented. NISAR: 198 NISAR L2 GCOV granules (2025–2026) over Valencia, Toronto and Jasper were found via NASA CMR, with public browse images in the viewer. NISAR data begin after the 2024 flood, so the flood itself is shown with Sentinel-1; the viewer is set up so the same workflow can run on NISAR L-band, which can see flooding under vegetation, for the next event.
*Trend verdict:* 45 years of NASA POWER daily rain (1981–2025) show **no significant trend** in Valencia's wettest-day rain (+0.08 mm a year, p = 0.28), annual total (p = 0.24) or heavy-rain days (p = 0.44), and 27 years of GPM IMERG satellite rain (1998–2024) agree: no significant trend in annual (p = 0.62), Sep–Nov or wettest-month totals. One extreme flood isn't a trend. But GRACE/GRACE-FO shows total water storage over eastern Spain falling by 0.39 cm a year (95% CI −0.61 to −0.14, p = 0.0019, 2003–2025). Southern Ontario, a NISAR site in the viewer, gains water storage (+0.55 cm a year, p = 0.014). Its MERRA-2 reanalysis rain shows falling extremes, but GPM IMERG shows no trend there and doesn't confirm the reanalysis decrease, so we don't call a rainfall trend for Ontario.

**03 Adapt: Field Shift (Story County, Iowa).** A rotation explorer: click a 1.2 km tile, move five priority sliders (water demand, erosion, nitrogen fixing, heat/frost exposure, soil-moisture stress) and watch the ranked rotations update. USDA Cropland Data Layer 2009–2025, NASADEM, NASA POWER, MODIS NDVI and SoilGrids feed a LightGBM next-season crop model: 0.8176 accuracy and 0.5012 macro-F1 on 66,666 held-out pixels (2024–2025), against 0.8136 and 0.4633 for a Markov-2 baseline. An NSGA-II search finds 36 non-dominated four-year rotations. Honest miss: temperature scaling made calibration worse (ECE 0.0351 vs 0.016 raw), so the tool keeps raw probabilities.
*Trend verdict:* central Iowa's frost-free season is getting longer by 0.43 days a year (95% CI +0.12 to +0.67, p = 0.006; Story County cell +0.47, p = 0.002), about 19 days on the trend line since 1981. It's driven by a later first autumn frost (+0.40 days a year, p < 0.001, all 35 grid cells); the last spring frost hasn't moved significantly (p = 0.48). May–Sep corn growing degree days rise by 4.6 a year (p < 0.001). Summer water is steady on every source: NASA POWER root-zone wetness (p = 0.51) and May–Sep rain (p = 0.55), SMAP surface soil moisture (2015–2025, p = 0.21), GLDAS soil moisture in all layers (2000–2025, p = 0.27–0.38) and GRACE water storage (p = 0.57). Hot days show no significant trend either (p = 0.41). A longer, warmer season with the same water favours longer-season hybrids and cover crops after harvest, which the rotation explorer lets a farmer test.

### HOW: data, methods and validation
- **Trend engine:** one value per year per region or grid cell; two-sided Mann-Kendall test (α = 0.05) and Sen's slope with a 95% CI (pymannkendall 1.4.3, Gilbert 1987), plus a Hamed-Rao autocorrelation-corrected p as a robustness check. Per-cell maps show where a trend is significant.
- **Held-out years:** every model is trained on earlier years and tested on later ones, against simple baselines.
- **Second source:** fire counts are checked on MODIS-only, harmonized and fire-power series and against MCD64A1 burned area; reanalysis rain against GPM IMERG; soil water against SMAP, GLDAS and GRACE. Province trends that hold on one series only are labelled tentative.
- **Autocorrelation:** where the standard and Hamed-Rao tests disagree we say so (southern Ontario's MERRA-2 annual rain drop: p = 0.006 standard, p = 0.052 corrected, and not confirmed by GPM IMERG, so we don't call it).
- **Limits we show:** one seed per model, not a published benchmark; trends show change, not cause; GRACE mascons are about 300 km, so water-storage trends are regional; SMAP covers only 11 seasons (low power); MERRA-2 cells are about 55 km.
- **Tools:** Python (pandas, NumPy, LightGBM, PyTorch, ONNX Runtime, Optuna, pymannkendall, rasterio), JavaScript (Leaflet, GSAP, Lenis), static HTML/CSS on Cloudflare Pages. Everything runs in the browser from precomputed data; no server needed.

### Impact
Fire managers get a single-scale 26-year record and an honest test of whether fire is really increasing in their area. Flood responders and the public get radar evidence that works through cloud and night, and learn why one flood doesn't prove a trend. Farmers and advisers see how their growing season has shifted and test rotations that fit it. Students and journalists get a worked example of reading a trend correctly: significance, effect size, uncertainty and a second series.

### What's next
Add rain-gauge checks; add NOAA-20/21 VIIRS; run SAR Change on NISAR L-band for the next flood; load full NISAR L-band products; extend Field Shift beyond one county; let anyone pick a variable and a place and get the four answers, with uncertainty.

### Built on earlier work (disclosure)
The three modules build on our own earlier code and open-source libraries, and were started before the event. During the event weekend we added the Trend Detective layer (data fetch, statistics, interactive charts), the Earthdata additions (GRACE/GRACE-FO, OPERA DSWx-S1, MCD64A1, HLS, GPM IMERG, GLDAS, SMAP) and the combined orbit-to-decision system, site, deck and video. Model metrics are one seed each.

## Use of Artificial Intelligence (AI)
Yes. AI coding assistants helped write and refactor parts of the code (data pipelines, web front end, chart components, the deck and video build scripts) and helped draft and edit the text. The concept, the choice of variables and regions, and the interpretation of results are ours. All models, metrics, trends and figures come from our own runs on the public data listed; no number was generated by an AI. The demo video uses real screen captures of the live site and tools; the illustrative photos appear in it only as they appear on the site. The site and deck also use AI-generated photos of people (fire crews, flood responders, farmers) to show who acts on the results; each one is labelled "Illustrative" and none shows a real person, place or event. No AI-generated video or voice is used, and every chart, map and number comes from data. The site footer and the video carry an AI-assistance notice.

## NASA Data
- **NASA FIRMS active fires:** MODIS Collection 6.1 (MCD14ML, Terra + Aqua) and VIIRS S-NPP 375 m (VNP14IMG), Canada and Argentina, 2000–2025. Hot Spots harmonizer and fire trends. https://firms.modaps.eosdis.nasa.gov/
- **MODIS MCD64A1.061 burned area** (LP DAAC), tile h11v03, Apr–Oct 2003–2025. Independent fire-trend check. https://lpdaac.usgs.gov/products/mcd64a1v061/
- **NASA-ISRO NISAR L2 GCOV** granule metadata (2025–2026) via **NASA CMR**, browse images from **ASF DAAC**. SAR Change (NISAR-ready workflow). https://asf.alaska.edu/nisar/
- **NASA/JPL OPERA DSWx-S1** surface water from radar (PO.DAAC), Valencia, Oct–Nov 2024. SAR Change. https://podaac.jpl.nasa.gov/dataset/OPERA_L3_DSWX-S1_V1
- **GRACE/GRACE-FO** JPL mascon RL06.3 CRI v04 total water storage (PO.DAAC), 2002–2026. Water trends. https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4
- **NASA POWER** daily PRECTOTCORR, T2M_MIN, T2M_MAX, GWETROOT (MERRA-2 based), 1981–2025. Rain and growing-season trends; Field Shift climate indicators. https://power.larc.nasa.gov/
- **NASADEM** elevation and slope (LP DAAC). Field Shift. https://lpdaac.usgs.gov/products/nasadem_hgtv001/
- **MODIS MOD13Q1 NDVI** (LP DAAC). Field Shift. https://lpdaac.usgs.gov/products/mod13q1v061/
- **HLS v2.0 HLSL30 + HLSS30** 30 m (LP DAAC), Story County mid-summer 2024 and 2025. Field Shift field-scale NDVI. https://lpdaac.usgs.gov/products/hlss30v002/
- **GPM IMERG V07** monthly precipitation (GPM_3IMERGM, GES DISC), 1998–2024. Cross-check of the rain trends. https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGM_07/summary
- **GLDAS Noah 2.1** monthly soil moisture (GLDAS_NOAH025_M, GES DISC), central Iowa, 2000–2025. https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary
- **SMAP L3 enhanced 9 km** soil moisture (SPL3SMP_E v006, NSIDC DAAC), central Iowa, May–Sep 2015–2025. https://nsidc.org/data/spl3smp_e/versions/6

## Space Agency Partner Data
- **ESA Copernicus Sentinel-1** RTC backscatter (VV/VH, 10 m), Valencia, Sept–Dec 2024, via Microsoft Planetary Computer. https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc
- **ISRO** is NASA's partner on NISAR (L-band and S-band SAR); NISAR GCOV granules as above.
- Sen1Floods11 (hand-labelled Sentinel-1 flood chips) is derived from ESA Copernicus Sentinel-1 data.

## References
**Stakes figures**
- Natural Resources Canada, *Forest fires* (2023 season: over 14.6 million ha burned, over 230,000 people evacuated). https://natural-resources.canada.ca/our-natural-resources/forests/wildland-fires-insects-disturbances/forest-fires/13143
- Government of Spain, *Info DANA: actualización de datos*, 29 Nov 2024 (230 confirmed deaths, 222 in the Comunitat Valenciana, 78 municipalities). https://www.lamoncloa.gob.es/info-dana/paginas/2024/291124-datos-seguimiento-actuaciones-gobierno.aspx
- FAO and ITPS (2015), *Status of the World's Soil Resources* (33% of land moderately to highly degraded). https://www.fao.org/newsroom/detail/soils-are-endangered-but-the-degradation-can-be-rolled-back/en (FAO news release on the report)

**Other data**
- Bonafilia, D., Tellman, B., Anderson, T., Issenberg, E. (2020). Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1. CVPR Workshops. CC-BY-4.0.
- USDA NASS Cropland Data Layer (public domain). ISRIC SoilGrids (CC-BY-4.0). JRC Global Surface Water. Natural Earth admin-1 boundaries (public domain). Esri / OpenStreetMap basemap via Leaflet (map context only).

**Methods**
- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica* 13, 245–259.
- Kendall, M. G. (1975). *Rank Correlation Methods*. Griffin, London.
- Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. *JASA* 63, 1379–1389.
- Gilbert, R. O. (1987). *Statistical Methods for Environmental Pollution Monitoring*. Van Nostrand Reinhold.
- Hamed, K. H., Rao, A. R. (1998). A modified Mann-Kendall trend test for autocorrelated data. *J. Hydrology* 204, 182–196.
- Hussain, M., Mahmud, I. (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests. *JOSS* 4(39), 1556.
- Ke, G. et al. (2017). LightGBM. NeurIPS. Ronneberger, O. et al. (2015). U-Net. MICCAI. Deb, K. et al. (2002). NSGA-II. *IEEE TEC* 6(2).

**Software:** pandas, NumPy, LightGBM, PyTorch, ONNX Runtime, Optuna, pymannkendall, Leaflet, GSAP, Lenis, Playwright, FFmpeg. Fonts: Geist (SIL OFL). Code licence: Apache-2.0. Not affiliated with or endorsed by NASA.
