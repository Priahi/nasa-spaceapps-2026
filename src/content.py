"""All copy and numbers for the combined site. Every number is copied from a results file in the demo data
(paths noted next to each block). One seed per run; nothing here is a published benchmark."""

SITE = {
    "title": "Orbit to Ground: an Earth-change intelligence pipeline from orbit to decision (NASA Space Apps 2026)",
    "tagline": "An Earth-change intelligence pipeline, from orbit to decision.",
    "team": "Parsa Riahi and Yara Riahi",
    "credit": "Built by Parsa Riahi and Yara Riahi · Toronto",
    "challenge": "Be An Earth System Trend Detective!",
    "challenge_url": "https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/",
    "author": "Parsa Riahi and Yara Riahi",
    "desc": "About 230 people died because of one day of rain in Valencia. Orbit to Ground turns NASA satellite data into the next move: a town-specific flood alert, wildfire crews staffed before May, and next season's crop map before planting. Built by Parsa Riahi and Yara Riahi in Toronto.",
    "built_on": "Built on open-source libraries (pandas, NumPy, LightGBM, PyTorch, ONNX Runtime, pymannkendall, Leaflet, GSAP, Lenis) and our own earlier code: the three tools started before the event, and the trend layer was computed during it (14 Nov 2026).",
}

CRITERIA = [
    ("Impact", "Addresses a real problem, and how many people it could help."),
    ("Creativity", "Original idea, or a meaningful improvement on existing ones."),
    ("Validity", "Scientifically grounded, technically feasible and usable."),
    ("Relevance", "Answers the challenge directly, with NASA data as a core part."),
    ("Presentation", "Clear, engaging story of the challenge, the solution and why it matters."),
]

PROJECTS = [
  {
    "slug": "hotspots", "n": "01",
    "name": "Hot Spots Harmonizer",
    "tagline": "One fire record from 2000 to 2025, on a single sensor scale.",
    "challenge": "Harmonization of MODIS and VIIRS Hot Spots",
    "challenge_url": "https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/",
    "card_img": "hotspots-card.webp", "hero_img": "hotspots-app.webp",
    "card_kpi": ("8.5%", "lower error than the best baseline on 2022–2025 Canada test data"),
    "problem": [
        "NASA has watched fires from orbit since 2000, but the record is split. MODIS (1 km pixels, from 2000) and VIIRS S-NPP (375 m pixels, from 2012) see fire differently: over Canada since 2012, VIIRS reports about 5.6 detections for every MODIS detection.",
        "So a fire manager can't put a 2005 season next to a 2023 season and trust the comparison. Hot Spots merges both records into one burning-activity calendar for any area, so a trend can be read across the sensor switch.",
    ],
    "steps": [
        ("Grid every detection", "NASA FIRMS country archives (MODIS C6.1 and VIIRS S-NPP) for Canada and Argentina, binned into 0.25° cell-months."),
        ("Start from an honest baseline", "An empirical-Bayes ratio per cell: how many VIIRS detections each MODIS detection is worth there, shrunk towards the regional ratio."),
        ("Learn what the ratio misses", "A LightGBM model corrects the baseline using MODIS fire power, day/night, Aqua/Terra and neighbouring months. Trained 2012–2020, tuned on 2021, tested on 2022–2025."),
        ("Say how sure it is", "Conformalized quantile intervals, calibrated per MODIS-count stratum, with a 90% coverage target."),
        ("Back-cast and flag", "2000–2011 MODIS is converted to VIIRS scale. Unusual months are flagged with a robust z-score (|z| > 3.5 against that calendar month's 26-year median)."),
        ("Put it in a browser", "Pick a region or draw any box: the calendar, disagreement map and CSV export are computed client-side from precomputed tiles."),
    ],
    "kpis": [
        {"v": 8.5, "dec": 1, "suf": "%", "vs": "RMSE 0.2844 vs 0.3109", "p": "Lower error than the best baseline on Canada's held-out 2022–2025 data (498,302 cell-months)."},
        {"v": 6.1, "dec": 1, "suf": "%", "vs": "RMSE 0.5191 vs 0.5530", "p": "Lower error than the best baseline in Argentina (193,472 test cell-months). Total-count bias fell from −24.4% to −1.6% after 2021 calibration."},
        {"v": 88.6, "dec": 1, "suf": "%", "vs": "target 90%", "p": "Interval coverage on cells where VIIRS saw fire, Canada. Argentina: 90.1%."},
        {"v": 11616131, "dec": 0, "suf": "", "vs": "MODIS + VIIRS", "p": "FIRMS detections behind the model (Canada and Argentina, 2000–2025)."},
        {"v": 22, "dec": 0, "suf": "", "vs": "Argentina: 14", "p": "Unusual months flagged across Canada's 26-year calendar."},
        {"neg": True, "v": 39.4, "dec": 1, "suf": "%", "vs": "baseline 16.7%", "p": "Honest miss: monthly-total error in Canada is worse than the baseline, even though per-cell error is better. Argentina too (16.6% vs 12.2%). Both are shown in the demo."},
    ],
    "data": [
        ("NASA FIRMS MODIS Collection 6.1 (MCD14ML)", "Active fire detections, Terra + Aqua, 2000–2025", "https://firms.modaps.eosdis.nasa.gov/"),
        ("NASA FIRMS VIIRS S-NPP 375 m (VNP14IMG)", "Active fire detections, 2012–2025", "https://firms.modaps.eosdis.nasa.gov/"),
        ("Esri / OpenStreetMap basemap via Leaflet", "Map context only", "https://leafletjs.com/"),
    ],
    "figs": [
        ("hotspots-calendar.webp", "Alberta: 2000–2025 harmonized calendar. Outlined cells are flagged months; the dashed line is 2012, when VIIRS starts.", "wide"),
        ("hotspots-argentina.webp", "Argentina Chaco preset: a different fire regime, peaking in the austral winter and spring.", ""),
        ("hotspots-fig04.webp", "Argentina: where the two sensors disagree most, per 0.25° cell, 2022–2025 (Colab run).", "light"),
    ],
    "criteria": {
        "Impact": "Gives fire managers and researchers a 26-year, single-scale fire calendar for any box on the map, so they can see whether a season is truly unusual.",
        "Creativity": "Learns the cross-sensor correction on top of a strong per-cell baseline, rather than one global ratio, and attaches calibrated uncertainty to every back-cast month.",
        "Validity": "Strict time split (train 2012–2020, tune 2021, test 2022–2025), four baselines and coverage checks. It reports where it loses (Canada monthly totals) as well as where it wins.",
        "Relevance": "Trend Detective: tests 23 years of NASA FIRMS fire activity per province with Mann-Kendall and Sen's slope, and shows why the sensor switch has to be harmonized before you call a trend. Built entirely on NASA FIRMS MODIS and VIIRS records.",
        "Presentation": "One-click presets, draw-your-own area, hover details, CSV export and a built-in briefing deck that explains each result in plain language.",
    },
    "limits": [
        "One seed per run; not a published benchmark.",
        "Two countries so far (Canada, Argentina). Only VIIRS S-NPP is used, not NOAA-20/21 yet.",
        "Intervals are summed over cells in the box; they are not a formal regional confidence interval.",
        "Back-cast years (2000–2011) carry model error and are labelled as such.",
    ],
  },
  {
    "slug": "sar-change", "n": "02",
    "name": "SAR Change: Valencia flood viewer",
    "tagline": "Radar sees the flood through the clouds. This viewer makes it readable.",
    "challenge": "Dancing with the SARs",
    "challenge_url": "https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/",
    "card_img": "sar-card.webp", "hero_img": "sar-app.webp",
    "card_kpi": ("3.0×", "the water overlap of the standard Otsu threshold on hand-labelled flood chips"),
    "problem": [
        "Floods arrive with the storm, so optical satellites usually see only cloud. Synthetic aperture radar sees through cloud, day or night, but radar images are hard to read for anyone who isn't a specialist.",
        "SAR Change takes the 29 October 2024 DANA flood in Valencia, Spain, and makes the radar change visible and explainable, with a path to NISAR L-band.",
    ],
    "steps": [
        ("Stack same-orbit radar", "26 Sentinel-1 RTC passes over four orbit tracks around Valencia (Sept–Dec 2024). Each orbit shares one colour stretch, so the time-lapse doesn't flicker."),
        ("Show the change", "Before/after swipe, time-lapse and a VV dB change map for three same-track pairs that bracket the flood."),
        ("Learn water from radar", "A U-Net trained on Sen1Floods11's hand-labelled chips, tuned with 14 Optuna trials, and compared against Otsu and a global VV threshold."),
        ("Explain the physics", "Why calm water looks dark, what VV and VH mean, and why NISAR's L-band can see flooding under vegetation where C-band can't."),
        ("Connect to NISAR", "NISAR L2 GCOV granules found through NASA CMR (Valencia 55, Toronto 67, Jasper 76), with public browse images in the viewer and hooks for full NISAR files."),
    ],
    "kpis": [
        {"v": 66.4, "dec": 1, "suf": "%", "vs": "water IoU, 90 test chips", "p": "U-Net water overlap on Sen1Floods11's official hand-labelled test split."},
        {"v": 21.8, "dec": 1, "suf": "%", "vs": "per-chip Otsu", "p": "The standard automatic threshold, on the same chips. A single tuned VV threshold reaches 46.8%."},
        {"v": 67.1, "dec": 1, "suf": "%", "vs": "VV 57.1% → VV+VH 65.1%", "p": "Channel ablation: adding VH and the VV/VH ratio each help."},
        {"v": 1.63, "dec": 2, "suf": " s", "vs": "ONNX FP32, CPU", "p": "Per 512×512 tile on a CPU. INT8 kept accuracy but was about 9× slower on that CPU, so FP32 stays."},
        {"v": 26, "dec": 0, "suf": "", "vs": "4 orbit tracks", "p": "Sentinel-1 radar passes in the Valencia viewer."},
        {"v": 198, "dec": 0, "suf": "", "vs": "55 + 67 + 76", "p": "NISAR L2 GCOV granules found via NASA CMR over Valencia, Toronto and Jasper."},
    ],
    "data": [
        ("NASA-ISRO NISAR L2 GCOV (metadata + browse)", "Granule search via NASA CMR; public browse images from ASF DAAC", "https://nisar.asf.alaska.edu/"),
        ("Sentinel-1 RTC (ESA Copernicus)", "VV/VH backscatter, 10 m, Valencia, Sept–Dec 2024; RTC via Microsoft Planetary Computer", "https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc"),
        ("Sen1Floods11 (CC-BY-4.0)", "Hand-labelled Sentinel-1 flood chips (Bonafilia et al., 2020)", "https://github.com/cloudtostreet/Sen1Floods11"),
        ("JRC Global Surface Water", "Permanent-water reference overlay on the test chips", "https://global-surface-water.appspot.com/"),
    ],
    "ba": ("sar-before.webp", "sar-after.webp", "26 Oct 2024 (3 days before)", "7 Nov 2024 (9 days after)",
           "Sentinel-1 false colour (VV, VH, VV/VH), ascending track 1755 over Valencia. Drag to compare. Dark areas are smooth surfaces such as standing water."),
    "figs": [
        ("sar-app2.webp", "Metrics tab: test water IoU against baselines, channel ablation and CPU timing.", "wide"),
    ],
    "criteria": {
        "Impact": "Floods are among the most costly disasters, and radar is often the only clear view during the event. Making SAR legible helps responders, journalists and the public.",
        "Creativity": "Pairs an interactive swipe and time-lapse with a plain-language physics explainer, and is honest about what C-band can't see and L-band NISAR can.",
        "Validity": "Scored on Sen1Floods11's official hand-labelled test split, against two classical baselines, with a channel ablation and CPU timing.",
        "Relevance": "Trend Detective: puts the Valencia flood in a 45-year NASA POWER rainfall record and asks whether extremes are trending there and in southern Ontario. The viewer uses real NISAR GCOV granules found via NASA CMR, with browse imagery in the app.",
        "Presentation": "Swipe, time-lapse and a 'why radar works here' tab turn a specialist dataset into a story anyone can follow.",
    },
    "limits": [
        "One seed (Colab attempt 1); the free GPU session ended before the trained weights were saved, so the viewer shows recorded metrics, not live inference.",
        "The NISAR browse images are from 2025–2026, not the 2024 flood. NISAR launched after the event; the flood itself is shown with Sentinel-1.",
        "Full NISAR .h5 products need an Earthdata login and aren't bundled.",
    ],
  },
  {
    "slug": "field-shift", "n": "03",
    "name": "Field Shift: rotation explorer",
    "tagline": "Try a crop rotation on your field and see the trade-offs before you plant.",
    "challenge": "Field Shift: Adapting Farms with NASA Data",
    "challenge_url": "https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/",
    "card_img": "field-card.webp", "hero_img": "field-app.webp",
    "card_kpi": ("0.8176", "next-season crop accuracy on 66,666 held-out pixels (macro-F1 0.5012)"),
    "problem": [
        "Farmers face shifting rainfall, heat, frost and declining soil health, and the rotation they pick this year shapes the soil for years.",
        "Field Shift combines NASA Earth observations with local soil, crop and farmer priorities for Story County, Iowa, at the scale of a 1.2 km tile.",
    ],
    "steps": [
        ("Read the field's history", "USDA Cropland Data Layer 2009–2025 at 30 m, grouped into 923 analysis tiles of 1.2 km."),
        ("Add NASA context", "NASADEM slope, NASA POWER climate (growing-degree days, frost, heat, rainfall, root-zone wetness), MODIS NDVI bare-soil months and SoilGrids texture and carbon."),
        ("Predict next season", "LightGBM predicts each pixel's next crop from five years of history plus terrain, soil, climate and NDVI. Trained to 2021, tuned on 2022–2023, tested on 2024–2025."),
        ("Score the trade-offs", "Five indicators per rotation: water demand (FAO-56 crop coefficients), erosion risk, nitrogen-fixing share, heat/frost exposure and soil-moisture stress."),
        ("Search for better plans", "Three reference rotations plus an NSGA-II search (48 individuals, 25 generations) that finds 36 non-dominated four-year plans. Sliders re-rank them by the farmer's own priorities."),
    ],
    "kpis": [
        {"v": 0.8176, "dec": 4, "suf": "", "vs": "Markov-2: 0.8136", "p": "Next-season crop accuracy on 66,666 held-out pixels (2024–2025)."},
        {"v": 0.5012, "dec": 4, "suf": "", "vs": "Markov-2: 0.4633", "p": "Macro-F1 across six crop classes. Adding NASA terrain, soil, climate and NDVI to crop history lifts it from 0.4582."},
        {"v": 0.811, "dec": 3, "suf": "", "vs": "1,495,561 pixels", "p": "Pixel accuracy of the full-county 2025 map."},
        {"v": 67, "dec": 0, "prefix": "−", "suf": "%", "vs": "water demand +13%", "p": "Erosion-risk index of a cover-crop rotation vs the current corn-soy rotation (county-typical field)."},
        {"v": 553, "dec": 0, "suf": " mm", "vs": "NASA POWER, 2015–2024", "p": "Median growing-season rainfall used in the climate panel."},
        {"neg": True, "v": 0.0351, "dec": 4, "suf": "", "vs": "raw: 0.016", "p": "Honest miss: temperature scaling made calibration worse (ECE), so the tool keeps the raw probabilities. Hay F1 is 0.33 and the rare 'other crop' class is 0."},
    ],
    "data": [
        ("NASA POWER", "Daily climate 2000–2024: temperature, rainfall, root-zone wetness", "https://power.larc.nasa.gov/"),
        ("NASADEM", "Elevation and slope (NASA JPL / LP DAAC)", "https://cmr.earthdata.nasa.gov/search/concepts/C1546314436-LPDAAC_ECS.html"),
        ("MODIS MOD13Q1 NDVI", "16-day vegetation index; bare-soil months", "https://lpdaac.usgs.gov/products/mod13q1v061/"),
        ("USDA NASS Cropland Data Layer", "30 m crop maps 2009–2025 (public domain)", "https://nassgeodata.gmu.edu/CropScape/"),
        ("ISRIC SoilGrids", "Clay, sand, organic carbon, pH, bulk density (CC-BY-4.0)", "https://www.isric.org/explore/soilgrids"),
    ],
    "figs": [
        ("field-map.webp", "Held-out 2025: the actual crop map, the model's prediction and where they disagree.", "wide light"),
        ("field-ablation.webp", "What each data layer adds (Colab full-county run).", "light"),
        ("field-cdl.webp", "Story County crop groups from the Cropland Data Layer.", "light"),
    ],
    "criteria": {
        "Impact": "Helps farmers and advisers compare rotations on soil, water and climate risk, field by field, before committing a season.",
        "Creativity": "Combines a next-season crop model with a multi-objective search, so farmers explore a trade-off frontier instead of getting one 'best' answer.",
        "Validity": "Temporal split, three baselines, ablation by data layer, calibration checks and per-class scores, including the classes it gets wrong.",
        "Relevance": "Trend Detective: 45 years of NASA POWER show central Iowa's frost-free season and growing degree days rising significantly, which changes the rotation question. NASA POWER, NASADEM and MODIS NDVI drive the indicators and the model.",
        "Presentation": "Click a tile, move five priority sliders and watch the ranked rotations update, with a plain-language note on each plan's benefits and risks.",
    },
    "limits": [
        "One seed per run; not a published benchmark. One county so far.",
        "Indicators are planning scores, not yield or evapotranspiration forecasts. Markets, leases and equipment aren't modelled.",
        "Cover crops aren't a CDL class; their effect on bare months is a documented assumption.",
        "SMAP, ECOSTRESS, GPM IMERG and GRACE aren't integrated yet (they need an Earthdata login).",
        "The tool supports farmer judgment and local agronomy; it doesn't replace them.",
    ],
  },
]


# ---------- Trend Detective layer (event work; numbers from trends/out/trends.json, see trends/RESULTS.md) ----------
GLOSSARY = [
    ("Trend", "A steady rise or fall over many years, not a single bad year. We test one value per year."),
    ("Mann-Kendall test", "Compares every pair of years: does the later year tend to be higher (or lower)? It doesn't assume a straight line or a bell curve."),
    ("Sen's slope", "The median change per year across all pairs of years. A single extreme year can't drag it much. We show it with a 95% confidence interval."),
    ("Significant (p < 0.05)", "Data with no real trend would look this trendy less than 5% of the time. It's evidence of change, not proof of a cause."),
]

TRENDS = {
  "hotspots": {
    "theme": "Fire", "widget": "fire",
    "title": "Is fire activity in Canada increasing?",
    "intro": "23 years of NASA FIRMS active fires (2003–2025), summed per province and tested with Mann-Kendall and Sen's slope. Switch between the harmonized record, the single-sensor MODIS record and fire radiative power to see which trends hold up.",
    "case": {"spark": "fire.canada.Canada.modis_count", "what": "MODIS active-fire detections per year", "where": "Canada, 2003–2025",
             "how": "+3,019 a year (95% CI +81 to +5,184), about +67% of a typical year per decade", "sig": (True, "Yes, p = 0.035")},
    "findings": [
        ("Canada: rising on every MODIS-era series.", "Harmonized count +18,497 a year (p = 0.020), MODIS-only +3,019 a year (p = 0.035) and MODIS fire radiative power, summed over all detections, +367 GW a year (p = 0.011). All three are still significant after the autocorrelation correction."),
        ("Argentina: falling.", "The same tests give a significant decrease: MODIS-only −1,909 detections a year (p < 0.001), about −32% of a typical year per decade. Same variable, opposite trend in a different place."),
        ("Provinces: be careful.", "The harmonized series is significant in Alberta, British Columbia, New Brunswick, Nova Scotia and Nunavut, but MODIS-only is significant in none of them. The harmonized record joins a model back-cast (2003–2011) to observed VIIRS (2012+), so a jump at 2012 can look like a trend. Where only the harmonized series is significant, treat it as tentative."),
        ("VIIRS alone is too short.", "With 14 years (2012–2025), no region shows a significant VIIRS-only trend. This is why a harmonized long record matters, and why it needs checking."),
    ],
    "data": [("NASA FIRMS MODIS + VIIRS (trend layer)", "Annual detections and FRP per province, 2003–2025; Mann-Kendall + Sen's slope", "https://firms.modaps.eosdis.nasa.gov/"),
             ("MODIS MCD64A1.061 burned area (module upgrade)", "Monthly 500 m burned area, tile h11v03, Apr–Oct 2003–2025; Mann-Kendall + Sen's slope", "https://lpdaac.usgs.gov/products/mcd64a1v061/"),
             ("Natural Earth admin-1 boundaries", "Province outlines for the trend map (public domain)", "https://www.naturalearthdata.com/")],
  },
  "sar-change": {
    "theme": "Water", "widget": "water",
    "title": "Was the Valencia flood part of a trend?",
    "intro": "A flood map shows one event. To ask if heavy rain is changing, we tested 45 years (1981–2025) of NASA POWER daily precipitation over eastern Spain (around Valencia) and southern Ontario (around Toronto, a NISAR site in the viewer): annual totals, the wettest day of each year, and heavy-rain days.",
    "case": {"spark": "water.valencia.rx1day", "mark": 2024, "what": "Rain on the wettest day of each year (Rx1day)", "where": "Eastern Spain (Valencia), 1981–2025",
             "how": "+0.08 mm a year (95% CI −0.09 to +0.22)", "sig": (False, "No, p = 0.28")},
    "findings": [
        ("Valencia: no significant trend in extremes.", "Wettest-day rain +0.08 mm a year (p = 0.28) and heavy-rain days (p = 0.44) don't trend in this reanalysis record. The 2024 DANA flood was extreme, but one extreme isn't a trend."),
        ("Annual totals: a patchy rise.", "8 of the 35 cells around Valencia show a significant rise in annual precipitation, including the cell over the city; the regional mean doesn't (p = 0.24)."),
        ("Southern Ontario: a reanalysis signal satellites don't confirm.", "In MERRA-2 reanalysis (NASA POWER), wettest-day rain falls −0.24 mm a year and days with ≥ 20 mm fall −0.06 a year (both p < 0.001). GPM IMERG satellite rainfall over 1998–2024 shows no significant trend in the annual total (p = 0.28) or the wettest month (p = 0.36), so we don't claim Ontario's rain extremes are falling."),
        ("Drying ground, then a flash flood.", "GRACE/GRACE-FO gravity satellites show total water storage over eastern Spain falling by about 0.39 cm a year over 2003–2025 (p = 0.002, Earthdata login). Rain extremes didn't trend, but the land was holding less water before the DANA struck. Southern Ontario's storage is rising (+0.55 cm a year, p = 0.014)."),
        ("Cross-checked with satellite rainfall.", "GPM IMERG V07 (monthly, 0.1°, Earthdata login) over 1998–2024 agrees for eastern Spain: no significant trend in the annual total (p = 0.62), the September–November total (p = 0.80) or the wettest month (p = 0.21). One extreme event isn't a trend."),
    ],
    "data": [("NASA POWER daily PRECTOTCORR (trend layer)", "Daily precipitation 1981–2025 (MERRA-2 based), 35 cells per region; Mann-Kendall + Sen's slope", "https://power.larc.nasa.gov/"),
             ("GRACE/GRACE-FO JPL mascon RL06.3 CRI v04 (trend layer)", "Monthly total water storage 2002–2026, land cells over eastern Spain and southern Ontario; deseasonalised annual means", "https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4"),
             ("GPM IMERG V07 monthly GPM_3IMERGM (trend layer)", "Satellite rainfall, 0.1°, eastern Spain and southern Ontario boxes, 1998–2024: annual, Sep–Nov and wettest-month totals", "https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGM_07/summary"),
             ("NASA/JPL OPERA DSWx-S1 (module upgrade)", "Radar-derived surface water, 30 m, 18 passes 1 Oct–19 Nov 2024 over the Valencia flood zone", "https://podaac.jpl.nasa.gov/dataset/OPERA_L3_DSWX-S1_V1"),
             ("GPM IMERG V07 Final daily GPM_3IMERGDF (dashboard)", "Daily satellite rainfall, 0.1°, upstream of Valencia (lon −1.0 to −0.3, lat 39.2 to 39.6), 15 Oct–20 Nov 2024: box mean and wettest cell", "https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary"),
             ("NASA POWER daily CLOUD_AMT (dashboard)", "Daily cloud amount (CERES SYN1deg based) at 39.4° N, 0.65° W, 15 Oct–20 Nov 2024", "https://power.larc.nasa.gov/")],
  },
  "field-shift": {
    "theme": "Crops", "widget": "crops",
    "title": "Is the growing season in Iowa changing?",
    "intro": "Rotation choices depend on season length, heat and soil water. We built seven growing-season indicators from 45 years (1981–2025) of NASA POWER daily data for central Iowa and the Story County cell where Field Shift runs, and tested each for a trend.",
    "case": {"spark": "crops.frost_free_days.region", "what": "Frost-free season length", "where": "Central Iowa, 1981–2025",
             "how": "+0.43 days a year (95% CI +0.12 to +0.67), about 19 days longer on the trend line over 1981–2025", "sig": (True, "Yes, p = 0.006")},
    "findings": [
        ("A longer frost-free season.", "+0.43 days a year across central Iowa (p = 0.006); +0.47 in the Story County cell (p = 0.002). On the Sen trend line that's about 19 days longer between 1981 and 2025."),
        ("Autumn is driving it.", "The first autumn frost is getting later by about 0.4 days a year (p < 0.001, all 35 cells significant). The last spring frost shows no significant change (p = 0.48)."),
        ("More heat for corn.", "May–Sep growing degree days rise by about 4.6 a year (p < 0.001, all 35 cells), roughly +3% of a typical season per decade."),
        ("Water underground is steady.", "Three independent records agree there's no significant trend in Iowa's water: GRACE/GRACE-FO total water storage, 2003–2025 (p = 0.57); GLDAS Noah land-model soil moisture at every depth to 1 m, May–September 2000–2025 (p = 0.27 to 0.38); and SMAP satellite surface soil moisture, 2015–2025 (p = 0.21, a short record with low power). GPM IMERG annual rain shows no trend either (p = 0.50)."),
        ("No change in summer water.", "Root-zone wetness (p = 0.51), May–Sep rain (p = 0.55) and hot days ≥ 32 °C (p = 0.41) show no significant trend. A longer, warmer season with the same water favours longer-season hybrids and cover crops after harvest, which is what the rotation explorer lets you test."),
    ],
    "data": [("NASA POWER daily T2M_MIN, T2M_MAX, GWETROOT, PRECTOTCORR (trend layer)", "1981–2025 growing-season indicators, central Iowa (35 cells) and Story County; Mann-Kendall + Sen's slope", "https://power.larc.nasa.gov/"),
             ("GRACE/GRACE-FO JPL mascon RL06.3 CRI v04 (trend layer)", "Monthly total water storage 2002–2026, land cells over central Iowa; deseasonalised annual means", "https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4"),
             ("NASA HLS v2.0 HLSL30 + HLSS30 (module upgrade)", "30 m NDVI, Story County, two mid-summer scenes (1 Aug 2024, 31 Jul 2025)", "https://lpdaac.usgs.gov/products/hlss30v002/"),
             ("NASA SMAP L3 enhanced soil moisture SPL3SMP_E (module upgrade)", "9 km surface soil moisture, Story County and central Iowa, May–Sep means 2015–2025; Mann-Kendall + Sen's slope", "https://nsidc.org/data/spl3smp_e"),
             ("GLDAS Noah 2.1 monthly GLDAS_NOAH025_M (trend layer)", "Soil moisture at four depths to 1 m, central Iowa, May–Sep means 2000–2025", "https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary"),
             ("GPM IMERG V07 monthly GPM_3IMERGM (trend layer)", "Satellite rainfall, 0.1°, central Iowa box, annual totals 1998–2024", "https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGM_07/summary")],
  },
}


# ---------- the system: WHY / WHAT / HOW ----------
STAKES = [  # every figure is quoted from the linked public source
    {"theme": "Fire", "big": "14.6 Mha", "line": "of Canada's forest burned in the 2023 season, and over 230,000 people were evacuated.",
     "src": "Natural Resources Canada, Forest fires", "url": "https://natural-resources.canada.ca/forests-forestry/wildland-fires/forest-fires"},
    {"theme": "Flood", "big": "230", "line": "confirmed deaths from the October–November 2024 DANA floods in Spain (222 in the Valencia region), across 78 municipalities.",
     "src": "Government of Spain, Info DANA update, 29 Nov 2024", "url": "https://www.lamoncloa.gob.es/info-dana/paginas/2024/291124-datos-seguimiento-actuaciones-gobierno.aspx"},
    {"theme": "Soil", "big": "33%", "line": "of the world's land is moderately to highly degraded by erosion, compaction, salinization and pollution.",
     "src": "FAO, Status of the World's Soil Resources (2015)", "url": "https://www.fao.org/newsroom/detail/soils-are-endangered-but-the-degradation-can-be-rolled-back/en"},
]
SYSTEM_PROBLEM = ("Satellites already see these changes, but the evidence rarely reaches a decision intact. Fire records are split across sensors, so long trends can't be trusted. "
                  "Optical satellites go blind under the storm clouds that cause floods. And the people choosing what to plant next year rarely get the land's history in a usable form. "
                  "A single dramatic image can't tell anyone whether something is a trend.")
MODULES = {
  "hotspots": {"role": "Detect", "verb": "Detect change from orbit",
      "statement": "Fire managers can't compare a 2005 fire season with a 2023 one, because NASA's fire record switches sensors in 2012 and VIIRS sees about 5.6 times more fire than MODIS. Without one consistent record, no one can say if fire is really increasing.",
      "delivers": ["One harmonized 2000–2025 fire calendar for any area you draw", "Calibrated uncertainty and unusual-month flags", "Fire trends per province, checked on a second record"]},
  "sar-change": {"role": "Confirm", "verb": "Confirm through cloud and night",
      "statement": "During a flood the sky is covered, so optical satellites see cloud, not water. Radar sees through it day and night, but responders and the public can't read radar images, and one flood map can't say if floods are a trend.",
      "delivers": ["Radar before/after and time-lapse of the Valencia flood", "A water model that triples the standard threshold's overlap", "NASA OPERA radar water maps and NISAR granules, plus 45-year rain and 23-year water-storage trends"]},
  "field-shift": {"role": "Adapt", "verb": "Adapt on the ground",
      "statement": "A farmer choosing next year's rotation has to weigh soil, water, erosion and a changing climate, but the satellite evidence for their own field is scattered across agencies and formats.",
      "delivers": ["Next-season crop prediction from 2009–2025 crop maps plus NASA terrain, climate and NDVI", "36 rotation plans ranked by the farmer's own priorities", "Growing-season trends: longer frost-free season, more heat, steady soil water"]},
}

# ---------- Earthdata upgrades to the modules (processed during the event; see upgrades/PROVENANCE.md) ----------
UPGRADES = {
  "sar-change": {
    "title": "NASA OPERA confirms the water",
    "text": "We added NASA/JPL OPERA DSWx-S1, a surface-water map made from Sentinel-1 radar at 30 m, downloaded with an Earthdata login. 18 radar passes between 1 October and 19 November 2024 cover the coast south of Valencia. Outside water that was already there in early October, new water rose from 30.7 km² on 26 October to 77.7 km² on 31 October, two days after the flood, then stayed between about 30 and 60 km² for the next three weeks.",
    "note": "Read it with care. Most of the new water sits in the Albufera rice paddies around the lagoon, and it was already rising before the flood (from 4 km² on 1 October to 31 km² on 26 October), so the flood signal is the jump to 77.7 km². Radar water maps miss water between buildings, so the urban flooding in l'Horta Sud is under-detected, and much of it had drained by the first pass. Passes with under 80% valid pixels are left out.",
    "ba": ("opera-before.webp", "opera-after.webp", "26 Oct 2024 (before)", "31 Oct 2024 (2 days after)",
           "OPERA DSWx-S1 water classes, about 0.63–0.20°W, 39.20–39.55°N. Purple: water that wasn't there in early October. Blue: usual water (Albufera lagoon, sea, port)."),
    "series": "opera",
  },
}

UPGRADES["hotspots"] = {
  "title": "Burned area, mapped and tested",
  "eyebrow": "Earthdata upgrade · MODIS MCD64A1",
  "text": "We added the MODIS MCD64A1 burned-area product (500 m, monthly), downloaded with an Earthdata login: 161 monthly files for tile h11v03, which covers the boreal forest of northeastern British Columbia, Alberta and Saskatchewan, about 50–60°N, April to October, 2003–2025. Detections tell you where fire burned at the moment of an overpass; burned area tells you how much ground it took. Summed per season, burned area in this tile rose by about 272 km² a year (Sen's slope, 95% CI +57 to +503; Mann-Kendall p = 0.004, also significant after the Hamed-Rao check). 2023 was the largest season at 28,262 km².",
  "note": "One MODIS tile, not all of Canada. A single huge year (2023) sits at the end of the record, so the slope is sensitive to the last few seasons. Unmapped pixels average 1–3% per season.",
  "figs": [("mcd64-annual.webp", "Burned area per April–October season, MCD64A1 tile h11v03, 2003–2025.", "light"),
           ("mcd64-map.webp", "Year each pixel last burned since 2003, MCD64A1 tile h11v03 (about 50–60°N).", "")]}
UPGRADES["field-shift"] = {
  "title": "Field by field at 30 m",
  "eyebrow": "Earthdata upgrade · NASA HLS",
  "text": "We added NASA's Harmonized Landsat and Sentinel-2 (HLS v2.0, 30 m), downloaded with an Earthdata login, for Story County, Iowa (tile T15TVG). Comparing clear mid-summer scenes on 1 August 2024 (Sentinel-2) and 31 July 2025 (Landsat) over 866 km² of vegetated land, the median NDVI change is −0.01; 42 km² got greener by more than 0.1 and 22 km² got less green by more than 0.1.",
  "note": "Two single dates from two sensors in two years. Mid-summer NDVI is near saturation over both corn and soybeans, so HLS here can't separate crop types: it shows field-by-field contrast, not a crop map or a trend. The 2024 Sentinel-2 scene covers only about 60% of the county. We also processed SMAP enhanced L3 surface soil moisture (9 km, Earthdata login, 1,602 daily files): May–September means of 0.16 to 0.22 m³/m³ in Story County over 2015–2025, with no significant trend (p = 0.47; central Iowa p = 0.21). Eleven seasons is a short record.",
  "figs": [("hls-ndvi.webp", "HLS 30 m NDVI, Story County: 1 Aug 2024, 31 Jul 2025 and the change between them (cloud, shadow and water masked).", "light wide")]}
