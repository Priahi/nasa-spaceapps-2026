# NASA Space Apps 2026: project submission text (draft, NOT submitted)

**Team:** Parsa Riahi (built solo) · Toronto Local Event
**Challenge:** Be An Earth System Trend Detective! (https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/)
**Deadline:** Sun 15 Nov 2026, 11:59 PM ET

Paste each section into the matching field. Model metrics and trends come from `trends/RESULTS.md`, `earthdata/EARTHDATA.md`, `trends/out/trends.json`, `earthdata/*/*.json` and the apps' results files (mirrored in `src/content.py`). Event facts and impact what-ifs come from `submission/IMPACT.md` and `submission/impact.json`, with every source listed under References. Dollar and euro what-ifs are **illustrative estimates**, not measured outcomes; all alerts, dispatch and tasking in the apps are **simulated**. No lives-saved claims.

---

## Project Name
Orbit to Ground: Earth-change intelligence from orbit to decision

## High-Level Summary
*(about 150 words)*

On 29 October 2024, about 230 people died in the Valencia floods. More than 150 were dead when the phone alert came around 8 PM, 12 hours after the red warning, while NASA satellites logged the rain upstream. Orbit to Ground is one engine, with three working apps, that turns NASA satellite data into a local next move. Flood: rain and radar become a town-by-town map and a drafted alert; 12 hours earlier, published warning curves put about €1.1 bn of the €4.8 bn insured loss within reach. Fire: one 2000–2025 record flags risky Mays in winter, for 16 more days of readiness; each escaped fire stopped spares about 65,000 ha and about $25 M. Fields: a crop map ready before planting puts rye on 26,500 erosion-prone acres, worth about $1.2 M in a 2012-type drought. Its trend engine tests what is changing, where, how much, and whether it's significant. Money figures are illustrative; alerts are simulated.

## Link to Project Demo
- **Official demo video (29.5 s, under the 30-second limit; 1920×1080, silent, captioned):** https://spaceapps.parsariahi.com/submission/demo.mp4
  Captions: https://spaceapps.parsariahi.com/submission/demo.en.vtt · https://spaceapps.parsariahi.com/submission/demo.en.srt · also plays on the home page: https://spaceapps.parsariahi.com/#rewind
- **Alternative: the 7-slide deck:** https://spaceapps.parsariahi.com/submission/deck · PDF: https://spaceapps.parsariahi.com/submission/deck.pdf · PowerPoint: https://spaceapps.parsariahi.com/submission/deck.pptx · slide images: https://spaceapps.parsariahi.com/slides/

## Link to Final Project
https://spaceapps.parsariahi.com

Live apps (full screen): https://spaceapps.parsariahi.com/sar-change/app/ · https://spaceapps.parsariahi.com/hotspots/app/ · https://spaceapps.parsariahi.com/field-shift/app/
Code (public, Apache-2.0): https://github.com/Priahi/nasa-spaceapps-2026

## Detailed Project Description

### WHY: the problem
**Valencia, 29 October 2024.** About 230 people died because of one day of rain (El País counts 229 in the Valencia region). One town, Turís, got about 770 mm in a single day, about 1.6 years of València's normal rain. The danger was known: AEMET's red warning came around 7:30 AM. The first life was lost around noon, a driver at the Benimodo ravine. Around 7 PM the Poyo ravine became a river, and around 8 PM phones finally got the alert: "avoid any travel". By then more than 150 people had already died, at least 60% of them inside buildings. The rain was on the record: NASA's GPM IMERG satellite rain logged about 90 mm upstream that day, and radar can see flood water through the cloud that blinded optical satellites. The missing piece was a map that turned that evidence into a specific instruction for each town, hours earlier.

The same gap, between what satellites already see and what reaches the person who acts, repeats in two other places:

- **Fire (Alberta, Canada):** 2023 burned more than 14.6 million ha across Canada and evacuated more than 230,000 people (Natural Resources Canada). In Alberta, five of the 16 unusual fire months since 2000 were in May, including the 2016 Horse River (Fort McMurray) fire and 2023, yet crews were fully staffed only from early May. NASA's fire record also switches sensors in 2012 (MODIS 1 km to VIIRS 375 m; over Canada VIIRS reports about 5.6 detections per MODIS detection), so a fire manager can't fairly compare seasons or trust a 25-year trend.
- **Fields (Iowa, US):** in the 2012 drought, Iowa corn fell from 172 to 137 bushels an acre, about 20% (USDA NASS). The rotation a farmer chooses shapes the soil for years while frost dates, heat and moisture shift underneath, but the official crop map arrives about 11 months after the season and planting intentions are state-level only.
- **One engine:** behind all three is the challenge's question. One dramatic image can't tell anyone whether something is a trend, so every signal needs a tested answer to what is changing, where, how much, and whether it is significant.

**What-ifs (illustrative estimates, arithmetic in the Impact section):** an alert 12 hours earlier, around the red warning, would have landed before the first recorded death, and published warning curves put about €1.1 bn of Valencia's €4.8 bn insured loss within reach. Staffing Alberta's crews on 15 April instead of 1 May gives 16 more days of full readiness, and each escaped fire stopped spares about 65,000 ha (about the size of the City of Toronto) and about $25 M. Winter rye on Story County's 26,500 most erosion-prone acres is worth about $1.2 M net in a 2012-type drought, planned before planting.

### WHAT: one system, three working modules, one trend engine
Orbit to Ground runs from orbit to decision: NASA observations → a module that turns them into a usable map or model → a Trend Detective engine that issues a verdict → the person who decides (fire manager, flood responder, farmer). Every module page has the full live tool (embedded, plus full screen at `/app/`), its problem statement, results, honest misses, and an interactive trend widget: pick a region and a variable, and a verdict panel answers **what is changing, where, how much and is it significant**.

**01 Detect: Hot Spots Harmonizer.** One harmonized 2000–2025 fire calendar for any area you draw, with calibrated uncertainty and unusual-month flags. About 11.6 million NASA FIRMS detections (MODIS C6.1 and VIIRS S-NPP, Canada and Argentina) on a 0.25° grid. An empirical-Bayes per-cell ratio is the baseline; a LightGBM model corrects it (trained 2012–2020, tuned 2021, tested 2022–2025). On Canada's held-out data it has 8.5% lower error than the best baseline (RMSE 0.2844 vs 0.3109); in Argentina 6.1% lower. Conformal intervals reach 88.6% coverage against a 90% target. Honest miss: Canada's monthly-total error is worse than the baseline (39.4% vs 16.7%).
*Trend verdict:* Canada's annual fire activity is rising on all three MODIS-era series, 2003–2025: MODIS detections about +3,000 a year (95% CI +81 to +5,184, p = 0.035), harmonized count about +18,500 a year (p = 0.020), summed MODIS fire radiative power +367 GW a year (p = 0.011), all still significant after the Hamed-Rao autocorrelation check. Argentina is falling (MODIS about −1,900 a year, p < 0.001): same variable, opposite direction. An independent NASA product agrees: MODIS MCD64A1 burned area over tile h11v03 (the boreal forest of northeast British Columbia, Alberta and Saskatchewan, 50–60°N, Apr–Oct) rises by about 272 km² a year (95% CI +57 to +503, p = 0.0043), with 2023 the largest year (about 28,300 km² of about 106,000 km² burned over 2003–2025). This is one MODIS tile, not all of Canada. At province level the harmonized series is significant in Alberta, British Columbia, New Brunswick, Nova Scotia and Nunavut but MODIS alone is significant in none, so we label those calls tentative. VIIRS alone (14 years) is too short to show any significant trend, which is exactly why a harmonized long record is needed.

**02 Confirm: SAR Change (Valencia, NISAR-ready).** An interactive radar flood viewer for the 29 October 2024 DANA flood: before/after swipe, time-lapse and change map from 26 Sentinel-1 RTC passes on four orbit tracks. A U-Net trained on Sen1Floods11 reaches 66.4% water IoU on the official hand-labelled test split, against 21.8% for per-chip Otsu (about 3×). As an independent check we added NASA/JPL OPERA DSWx-S1 radar water maps (21 acquisitions, 1 Oct–19 Nov 2024): new water outside the usual-water mask jumps from 30.7 km² on 26 Oct to 77.7 km² on 31 Oct, two days after the flood, then falls to 54.3 km² (1 Nov) and 40.6 km² (6 Nov). Caveats we show: the extra water is concentrated in the Albufera rice-paddy belt; new water was already rising before the flood (4 km² on 1 Oct), so the flood signal is the jump; and radar water products under-detect water in built-up areas, so the urban flooding in l'Horta Sud is under-represented. NISAR: 198 NISAR L2 GCOV granules (2025–2026) over Valencia, Toronto and Jasper were found via NASA CMR, with public browse images in the viewer. NISAR data begin after the 2024 flood, so the flood itself is shown with Sentinel-1; the viewer is set up so the same workflow can run on NISAR L-band, which can see flooding under vegetation, for the next event.
*Trend verdict:* 45 years of NASA POWER daily rain (1981–2025) show **no significant trend** in Valencia's wettest-day rain (+0.08 mm a year, p = 0.28), annual total (p = 0.24) or heavy-rain days (p = 0.44), and 27 years of GPM IMERG satellite rain (1998–2024) agree: no significant trend in annual (p = 0.62), Sep–Nov or wettest-month totals. One extreme flood isn't a trend. But GRACE/GRACE-FO shows total water storage over eastern Spain falling by 0.39 cm a year (95% CI −0.61 to −0.14, p = 0.0019, 2003–2025). Southern Ontario, a NISAR site in the viewer, gains water storage (+0.55 cm a year, p = 0.014). Its MERRA-2 reanalysis rain shows falling extremes, but GPM IMERG shows no trend there and doesn't confirm the reanalysis decrease, so we don't call a rainfall trend for Ontario.

**03 Adapt: Field Shift (Story County, Iowa).** A rotation explorer: click a 1.2 km tile, move five priority sliders (water demand, erosion, nitrogen fixing, heat/frost exposure, soil-moisture stress) and watch the ranked rotations update. USDA Cropland Data Layer 2009–2025, NASADEM, NASA POWER, MODIS NDVI and SoilGrids feed a LightGBM next-season crop model: 0.8176 accuracy and 0.5012 macro-F1 on about 67,000 held-out pixels (2024–2025), against 0.8136 and 0.4633 for a Markov-2 baseline. An NSGA-II search finds 36 non-dominated four-year rotations. Honest miss: temperature scaling made calibration worse (ECE 0.0351 vs 0.016 raw), so the tool keeps raw probabilities.
*Trend verdict:* central Iowa's frost-free season is getting longer by 0.43 days a year (95% CI +0.12 to +0.67, p = 0.006; Story County cell +0.47, p = 0.002), about 19 days on the trend line since 1981. It's driven by a later first autumn frost (+0.40 days a year, p < 0.001, all 35 grid cells); the last spring frost hasn't moved significantly (p = 0.48). May–Sep corn growing degree days rise by 4.6 a year (p < 0.001). Summer water is steady on every source: NASA POWER root-zone wetness (p = 0.51) and May–Sep rain (p = 0.55), SMAP surface soil moisture (2015–2025, p = 0.21), GLDAS soil moisture in all layers (2000–2025, p = 0.27–0.38) and GRACE water storage (p = 0.57). Hot days show no significant trend either (p = 0.41). A longer, warmer season with the same water favours longer-season hybrids and cover crops after harvest, which the rotation explorer lets a farmer test.

### HOW: data, methods and validation
- **Trend engine:** one value per year per region or grid cell; two-sided Mann-Kendall test (α = 0.05) and Sen's slope with a 95% CI (pymannkendall 1.4.3, Gilbert 1987), plus a Hamed-Rao autocorrelation-corrected p as a robustness check. Per-cell maps show where a trend is significant.
- **Held-out years:** every model is trained on earlier years and tested on later ones, against simple baselines.
- **Second source:** fire counts are checked on MODIS-only, harmonized and fire-power series and against MCD64A1 burned area; reanalysis rain against GPM IMERG; soil water against SMAP, GLDAS and GRACE. Province trends that hold on one series only are labelled tentative.
- **Autocorrelation:** where the standard and Hamed-Rao tests disagree we say so (southern Ontario's MERRA-2 annual rain drop: p = 0.006 standard, p = 0.052 corrected, and not confirmed by GPM IMERG, so we don't call it).
- **Limits we show:** one seed per model, not a published benchmark; trends show change, not cause; GRACE mascons are about 300 km, so water-storage trends are regional; SMAP covers only 11 seasons (low power); MERRA-2 cells are about 55 km.
- **Tools:** Python (pandas, NumPy, LightGBM, PyTorch, ONNX Runtime, Optuna, pymannkendall, rasterio), JavaScript (Leaflet, GSAP, Lenis), static HTML/CSS on Cloudflare Pages. Everything runs in the browser from precomputed data; no server needed.

### Impact
All figures below are **illustrative what-ifs**: each applies a published, sourced relationship to a sourced bill from a real event, with the arithmetic shown. They are not measured outcomes or predictions, nothing was sent to anyone, and we make no lives-saved claim. Full working: `submission/IMPACT.md`.

**Flood (Valencia, 29 Oct 2024).** The insured bill is about €4.8 bn (Consorcio de Compensación de Seguros, CCS). Published lead-time curves put avoided damage at about 22% with 12 hours of warning (Day 1970 curve, National Hydrologic Warning Council) and about 30% at 24 hours (Global Commission on Adaptation, *Adapt Now*), levelling off after that (Pappenberger et al. 2015). An alert around 8 AM instead of 8 PM, close to the 7:30 AM red warning, lands before the first recorded death around noon (El País) and puts 22% × €4.8 bn ≈ **€1.1 bn within reach**. That is an upper bound: it assumes everyone got the alert and acted, and much of the bill can't be moved out of the water. The 12-hour case needs no new detection, only turning the known signal into a town-specific instruction (go up, keep out of garages and ground floors).

**Fire (Alberta).** The harmonized record shows Alberta's fire detections rising by about 1,500 a year (p = 0.035, tentative) and May as the risky month, known in winter. Staffing on 15 April (Alberta's own 2024 target, The Weather Network) instead of 1 May (MNP 2016 review) gives **+16 days** of full readiness. About 3% of Canadian fires escape and cause 97% of the area burned (Stocks et al. 2002); on Alberta 2023 (about 1,090 fires, about 2.2 M ha; MNP 2025) that is about 33 escapes of about **65,000 ha each**, about the City of Toronto's 631 km² (Statistics Canada). At about $385 per hectare (Alberta's wildfire cost of about $851 M over 2.2 M ha; Alberta Forestry and Parks Annual Report 2023–24), each escape stopped is worth about **$25 M** in firefighting cost alone. We don't claim staffing would have stopped any particular fire; the number of escapes prevented is the assumption you vary.

**Fields (Story County, Iowa).** In the 2012 drought, fields after cover crops yielded about 11 bushels an acre more corn (SARE/CTIC 2012–13 survey, self-reported). At $6.89 a bushel (USDA FSA) minus about $32 an acre for rye seed and planting (Iowa State University, Plastina et al.), rye on the 92 steepest squares, about **26,500 acres**, nets about **$1.2 M** in a 2012-type drought year; in normal years it usually costs a little, so it works like insurance. Our next-season map is ready around February, **before planting**, at 30 m.

**Compared with existing tools.** We complement them; we don't replace them.

| Today | What it does | What Orbit to Ground adds |
|---|---|---|
| AEMET warnings and EFAS flood notices | zone-level weather warnings (red at about 7:30 AM) and probability notices to agencies, days ahead | turns the rain and radar signal into a drafted, town-specific public alert with instructions (simulated) |
| ES-Alert phone broadcast | reached phones around 8 PM with "avoid any travel" | the dashboard pre-fills the message and target towns from the map (simulated; no real link) |
| Copernicus EMS rapid mapping | expert flood maps after activation; first maps 31 Oct, province-wide extent 2 Nov | open NASA OPERA radar water on every pass, tied to rain, trend tests and a task queue; NISAR-ready |
| NASA FIRMS and CWFIS | where it's burning now, and daily fire weather | one 26-year single-scale fire record with trend tests per province, and a pre-season readiness list |
| USDA Cropland Data Layer and Prospective Plantings | what *was* planted, about 11 months after the season; state-level intentions | a per-field next-season map before planting, with the climate trend attached |

Who benefits: flood responders and town officials, fire managers, farmers and advisers, and students and journalists, who get a worked example of reading a trend correctly (significance, effect size, uncertainty and a second source).

### What's next
Add rain-gauge checks; add NOAA-20/21 VIIRS; run SAR Change on NISAR L-band for the next flood; load full NISAR L-band products; extend Field Shift beyond one county; let anyone pick a variable and a place and get the four answers, with uncertainty.

### Built on earlier work (disclosure)
The three modules build on our own earlier code and open-source libraries, and were started before the event. During the event weekend we added the Trend Detective layer (data fetch, statistics, interactive charts), the Earthdata additions (GRACE/GRACE-FO, OPERA DSWx-S1, MCD64A1, HLS, GPM IMERG, GLDAS, SMAP) and the combined orbit-to-decision system, site, deck and video. Model metrics are one seed each.

## Use of Artificial Intelligence (AI)
Yes. General-purpose AI coding and writing assistants (large-language-model chat and code-editor tools) helped write and refactor parts of the code (data pipelines, web front end, chart components, the deck and video build scripts) and helped draft and edit the text. The concept, the choice of variables, regions and cases, and the interpretation of results are mine. All models, metrics, trends and figures come from my own runs on the public data listed, or are quoted from the sources under References; no number was generated by an AI. The demo video and the deck use real screen captures of the live apps, data maps and plain text cards; they contain no AI-generated images, video or voice (the video is silent with captions). The website uses AI-generated photos of people (fire crews, flood responders, farmers) to show who acts on the results; none shows a real person, place or event, and the site footer says so. The coordinator "Elena" in the pitch story is an illustrative composite character, labelled as such; the event timeline around her is sourced. Dashboard tasking (drones, camera revisits, crews, notices, alerts) is simulated; no real systems are contacted.

## NASA Data
- **NASA FIRMS active fires:** MODIS Collection 6.1 (MCD14ML, Terra + Aqua) and VIIRS S-NPP 375 m (VNP14IMG), Canada and Argentina, 2000–2025. Hot Spots harmonizer and fire trends. https://firms.modaps.eosdis.nasa.gov/
- **MODIS MCD64A1.061 burned area** (LP DAAC), tile h11v03, Apr–Oct 2003–2025. Independent fire-trend check. https://lpdaac.usgs.gov/products/mcd64a1v061/
- **NASA-ISRO NISAR L2 GCOV** granule metadata (2025–2026) via **NASA CMR**, browse images from **ASF DAAC**. SAR Change (NISAR-ready workflow). https://asf.alaska.edu/nisar/
- **NASA/JPL OPERA DSWx-S1** surface water from radar (PO.DAAC), Valencia, Oct–Nov 2024. SAR Change. https://podaac.jpl.nasa.gov/dataset/OPERA_L3_DSWX-S1_V1
- **GRACE/GRACE-FO** JPL mascon RL06.3 CRI v04 total water storage (PO.DAAC), 2002–2026. Water trends. https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4
- **NASA POWER** daily PRECTOTCORR, T2M_MIN, T2M_MAX, GWETROOT (MERRA-2 based), 1981–2025, and daily CLOUD_AMT (CERES SYN1deg based), 15 Oct–20 Nov 2024 at 39.4° N, 0.65° W. Rain and growing-season trends; Field Shift climate indicators; SAR Change cloud-cover context. https://power.larc.nasa.gov/
- **NASADEM** elevation and slope (LP DAAC). Field Shift. https://lpdaac.usgs.gov/products/nasadem_hgtv001/
- **MODIS MOD13Q1 NDVI** (LP DAAC). Field Shift. https://lpdaac.usgs.gov/products/mod13q1v061/
- **HLS v2.0 HLSL30 + HLSS30** 30 m (LP DAAC), Story County mid-summer 2024 and 2025. Field Shift field-scale NDVI. https://lpdaac.usgs.gov/products/hlss30v002/
- **GPM IMERG V07** monthly precipitation (GPM_3IMERGM, GES DISC), 1998–2024. Cross-check of the rain trends. https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGM_07/summary
- **GPM IMERG V07 Final daily** precipitation (GPM_3IMERGDF, GES DISC, OPeNDAP subset), upstream of Valencia (lon −1.0 to −0.3, lat 39.2 to 39.6), 15 Oct–20 Nov 2024. SAR Change rain leading signal. https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary
- **GLDAS Noah 2.1** monthly soil moisture (GLDAS_NOAH025_M, GES DISC), central Iowa, 2000–2025. https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary
- **SMAP L3 enhanced 9 km** soil moisture (SPL3SMP_E v006, NSIDC DAAC), central Iowa, May–Sep 2015–2025. https://nsidc.org/data/spl3smp_e/versions/6

## Space Agency Partner Data
- **ESA Copernicus Sentinel-1** RTC backscatter (VV/VH, 10 m), Valencia, Sept–Dec 2024, via Microsoft Planetary Computer. https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc
- **ISRO** is NASA's partner on NISAR (L-band and S-band SAR); NISAR GCOV granules as above.
- Sen1Floods11 (hand-labelled Sentinel-1 flood chips) is derived from ESA Copernicus Sentinel-1 data.

## References
**Event facts: Valencia, 29 October 2024** (the coordinator "Elena" is an illustrative composite, not a real person)
- El País, 26 Oct 2025, *Cómo, dónde y a qué hora murieron las 229 víctimas de la dana* (229 deaths; at least 156 before the 20:11 ES-Alert; first death 11:45 at the Benimodo ravine; at least 60% indoors). https://elpais.com/espana/2025-10-26/como-donde-y-a-que-hora-murieron-las-229-victimas-de-la-dana.html
- Newtral, *Cronología de los avisos por dana en Valencia* (AEMET red warning 07:36; ES-Alert 20:11). https://www.newtral.es/avisos-dana/20241031/
- AEMET (2024), event study 28 Oct–4 Nov 2024 (Turís: 771.8 mm in 24 h, 184.6 mm in 1 h). https://www.aemet.es/documentos/es/conocermas/recursos_en_linea/publicaciones_y_estudios/estudios/estudio_28_oct_4_nov_2024.pdf
- AEMET climate normals 1981–2010, València (475 mm a year; "about 1.6 years of rain" = 771.8 ÷ 475). https://www.aemet.es/es/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=8416&k=val
- Government of Spain, *Info DANA*, 29 Nov 2024 (230 confirmed deaths nationally, 222 in the Comunitat Valenciana). https://www.lamoncloa.gob.es/info-dana/paginas/2024/291124-datos-seguimiento-actuaciones-gobierno.aspx
- ECMWF Newsletter 183, *Extreme precipitation in Spain's Valencia region* (national 1, 6 and 12 h records). https://www.ecmwf.int/en/newsletter/183/news/extreme-precipitation-spains-valencia-region
- Reuters, 9 Nov 2024, *How slow warnings, poor defences left Spain exposed to deadly floods* (Poyo ravine 264 m³/s around noon, 1,686 m³/s at 18:43, 2,282 m³/s shortly after). https://www.reuters.com/business/environment/spains-flood-disaster-was-its-worst-recent-history-heres-what-went-wrong-2024-11-09/
- La Vanguardia, 9 Apr 2025, *Hasta las 18:43 la CHJ no comunicó la gran crecida en el barranco del Poyo*. https://www.lavanguardia.com/local/valencia/20250409/10568338/emergencias-juzgado-18-43-chj-comunico-gran-crecida-barranco-poyo.html
- EchoGéo (2025), *Analyse d'une alerte massive arrivée tardivement lors des inondations survenues à Valence* (deaths by town: Catarroja 25, Paiporta 45). https://journals.openedition.org/echogeo/30425
- NASA GPM IMERG V07 Final daily, our run (91 mm mean upstream on 29 Oct; listed under NASA Data).

**Impact what-ifs: flood**
- Consorcio de Compensación de Seguros, Consorseguros Digital no. 23 (more than 250,000 claims; estimated final cost about €4.8 bn). https://consorsegurosdigital.com/en/numero-23/sumario/contributions/valencia_floods/
- La Moncloa, 26 Nov 2025 (CCS has paid over €4 bn). https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/economia-comercio-empresa/paginas/2025/261125-indemnizacion-dana.aspx
- National Hydrologic Warning Council (2006), Day (1970) lead-time curve, p. 30 (about 22% avoided damage at 12 h). https://water.usgs.gov/osw/pubs/Flood_Management_benefits_complete.pdf
- Global Commission on Adaptation (2019), *Adapt Now*, Box ES.1 (24 h warning cuts damage by 30%). https://gca.org/wp-content/uploads/2019/09/GlobalCommission_Report_FINAL.pdf
- Pappenberger et al. (2015), *The monetary benefit of early flood warnings in Europe*, Env. Sci. & Policy 51 (4–40% at 48 h). https://centaur.reading.ac.uk/40264/1/PappenbergerMonetaryBenefit.pdf
- El País, 28 Dec 2024 (EFAS notices before the DANA). https://elpais.com/clima-y-medio-ambiente/2024-12-28/el-sistema-europeo-aviso-del-riesgo-de-inundacion-en-valencia-dias-antes-de-la-dana-pero-subestimo-su-magnitud.html
- ESA, *Devastating floods in Spain witnessed by satellites* (Copernicus EMS map timing). https://www.esa.int/es/articles/about-us/directorates/earth-observation-programmes/devastating-floods-in-spain-witnessed-by-satellites

**Impact what-ifs: fire**
- MNP for Alberta (2017), *A Review of the 2016 Horse River Wildfire* (readiness by 1 May). https://open.alberta.ca/dataset/7cc619bd-56ce-488e-b007-cada28430589/resource/6c6560d3-0a8e-4550-b1d1-86e58409dea2/download/2016horseriverwildfirereview-mar2017.pdf
- MNP for the Alberta Emergency Management Agency (2025), *2023 Spring Wildfire Post-Incident Assessment* (1,088 fires, about 2.2 M ha). https://open.alberta.ca/dataset/c8b32d6d-2b52-486d-a4f6-855ced2b9a71/resource/20e8af07-b2cd-43e4-b2e3-0eecbbd91a5b/download/pses-government-of-alberta-2023-spring-wildfire-post-incident-assessment-2025.pdf
- The Weather Network, 19 Jan 2024 (Alberta moves full staffing to 15 April). https://www.theweathernetwork.com/en/news/nature/outdoors/alberta-to-fully-staff-wildfire-crew-earlier-following-a-record-breaking-season
- Stocks et al. (2002), *Large forest fires in Canada, 1959–1997*, JGR 107 (3% of fires cause 97% of area burned). https://sites.ualberta.ca/~flanniga/publications/2003%20Stocks%20et%20al.%20J%20Geophys%20Res%20-%20Large%20forest%20fires.pdf
- Alberta Forestry and Parks, *Annual Report 2023–24* (wildfire cost about $851 M). https://open.alberta.ca/dataset/2dedbb29-e005-4802-bf6e-03bf77536add/resource/b86465e8-a8e3-45de-91d8-3fec19c700db/download/fp-annual-report-2023-2024.pdf
- Statistics Canada, 2021 Census Profile, City of Toronto (land area 631.10 km²). https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?Lang=E&DGUIDlist=2021A00053520005
- Insurance Bureau of Canada, 7 Jul 2016 (Horse River: $3.58 bn insured). https://www.newswire.ca/news-releases/northern-alberta-wildfire-costliest-insured-natural-disaster-in-canadian-history-585872181.html
- Natural Resources Canada, *Forest fires* (2023: more than 14.6 M ha burned, more than 230,000 evacuated). https://natural-resources.canada.ca/our-natural-resources/forests/wildland-fires-insects-disturbances/forest-fires/13143
- NASA Earthdata, FIRMS FAQ. https://www.earthdata.nasa.gov/data/tools/firms/faq
- Natural Resources Canada, CWFIS. https://natural-resources.canada.ca/forests-forestry/wildland-fires/current-wildland-fire-activity-cwfis

**Impact what-ifs: fields**
- SARE/CTIC, *2012–2013 Cover Crop Survey*, p. 26 (corn +11.1 bu/acre after cover crops in the 2012 drought). https://www.sare.org/wp-content/uploads/SARE-CTIC-CC-Survey-Report-V2.8.pdf
- Plastina et al. (2018), *Economics of Cover Crops*, Iowa State University (seed $17.70 + planting $14.39 per acre). https://www.card.iastate.edu/files/inline-files/plastina-180309.pdf
- USDA FSA, marketing-year average prices (corn 2012/13: $6.89/bu). https://www.fsa.usda.gov/sites/default/files/documents/2016_mya.pdf
- USDA NASS, *Crop Production 2012 Summary* (Iowa corn 172 → 137 bu/acre). https://esmis.nal.usda.gov/sites/default/release-files/k3569432s/8s45qb85z/12579v877/CropProdSu-01-11-2013.pdf
- USDA NASS, Cropland Data Layer FAQ (release dates and accuracy). https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php
- USDA NASS, *Prospective Plantings*, 31 Mar 2026. https://release.nass.usda.gov/reports/pspl0326.pdf

**Other data**
- Bonafilia, D., Tellman, B., Anderson, T., Issenberg, E. (2020). Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1. CVPR Workshops. CC-BY-4.0.
- USDA NASS Cropland Data Layer (public domain). ISRIC SoilGrids (CC-BY-4.0). JRC Global Surface Water. Natural Earth admin boundaries (public domain). Town outlines from OpenStreetMap via Nominatim (© OpenStreetMap contributors, ODbL).
- Basemap: Esri World Dark Gray Canvas tiles (sources: Esri, © OpenStreetMap contributors and others) shown through Leaflet, map context only.

**Methods**
- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica* 13, 245–259.
- Kendall, M. G. (1975). *Rank Correlation Methods*. Griffin, London.
- Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. *JASA* 63, 1379–1389.
- Gilbert, R. O. (1987). *Statistical Methods for Environmental Pollution Monitoring*. Van Nostrand Reinhold.
- Hamed, K. H., Rao, A. R. (1998). A modified Mann-Kendall trend test for autocorrelated data. *J. Hydrology* 204, 182–196.
- Hussain, M., Mahmud, I. (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests. *JOSS* 4(39), 1556.
- Ke, G. et al. (2017). LightGBM. NeurIPS. Ronneberger, O. et al. (2015). U-Net. MICCAI. Deb, K. et al. (2002). NSGA-II. *IEEE TEC* 6(2).

**Software and fonts:** Python: pandas, NumPy, SciPy, scikit-learn, scikit-image, LightGBM, PyTorch, ONNX Runtime, Optuna, pymannkendall, rasterio, pyproj, Shapely, pystac-client, Matplotlib, Pillow, python-pptx. JavaScript: Leaflet, GSAP with ScrollTrigger, Lenis. Build and capture: Playwright, FFmpeg. Fonts: Geist and Geist Mono (SIL Open Font License), self-hosted. Hosting: static files on Cloudflare Pages. Code licence: Apache-2.0.

**Images:** photos of people on the website are AI-generated illustrations (disclosed in the site footer); all maps, charts and app captures come from the data above.

Not affiliated with or endorsed by NASA.
