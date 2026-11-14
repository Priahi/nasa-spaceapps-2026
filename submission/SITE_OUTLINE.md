# Site outline: Orbit to Ground (WHY / WHAT / HOW)
Live: https://nasa-spaceapps-2026.pages.dev · Challenge: Be An Earth System Trend Detective! · Team GeoAI Toronto (Parsa Riahi)
Design: personal-site design system (Geist / Geist Mono, #07091a ground, blue #9ec1ff → violet #d4c4ff gradient, contour rules,
GSAP ScrollTrigger + Lenis, spotlight / border-beam cards, tier metric panels, pinned "engine" pipeline diagram). No outside brand names.

## Hero
- Eyebrow: NASA Space Apps 2026 · Be An Earth System Trend Detective!
- H1: Orbit to Ground
- Lede: An Earth-change intelligence pipeline, from orbit to decision. Three working modules (detect, confirm, adapt) turn NASA satellite data into decisions, and every module answers the same four questions: what is changing, where, how much, and is it significant?
- Proof row: 11,616,131 FIRMS detections harmonized (Detect) · 3.0× the water overlap of the standard Otsu threshold (Confirm) · 36 non-dominated rotation plans (Adapt)

## 01 WHY: change is fast, and the evidence is split
Stakes (cite exactly; sources linked on site):
- Fire: 14.6 Mha of Canada's forest burned in 2023; over 230,000 people evacuated (Natural Resources Canada, Forest fires).
- Flood: 230 confirmed deaths from the Oct–Nov 2024 DANA floods in Spain (222 in the Valencia region), 78 municipalities (Government of Spain, Info DANA, 29 Nov 2024).
- Soil: 33% of the world's land is moderately to highly degraded (FAO, Status of the World's Soil Resources, 2015).
Problem statement: Satellites already see these changes, but the evidence rarely reaches a decision intact. Fire records are split across sensors, so long trends can't be trusted. Optical satellites go blind under the storm clouds that cause floods. And the people choosing what to plant next year rarely get the land's history in a usable form. A single dramatic image can't tell anyone whether something is a trend.

## 02 WHAT: one system, three working modules + a trend layer (pinned pipeline diagram)
- 01 Detect · Hot Spots Harmonizer — Problem: the fire record switches sensors in 2012 (VIIRS sees ~5.6× more fire than MODIS), so 2005 and 2023 can't be compared. Delivers: one harmonized 2000–2025 fire calendar for any drawn area, calibrated uncertainty, unusual-month flags. Fact: 8.5% lower error than the best baseline (2022–2025 Canada test).
- 02 Confirm · SAR Change — Problem: floods come with cloud; radar sees through it but is hard to read. Delivers: radar before/after + time-lapse of Valencia, U-Net water model (66.4% IoU vs 21.8% Otsu), NASA OPERA DSWx-S1 radar water maps (new water 30.7 → 77.7 km² across the flood, 26→31 Oct 2024), 198 NISAR granules via NASA CMR.
- 03 Adapt · Field Shift — Problem: a farmer weighing soil, water, erosion and climate has scattered evidence. Delivers: next-season crop prediction (0.8176 accuracy vs 0.8136 Markov-2), 36 rotation plans ranked by the farmer's priorities.
- 04 Trend layer (connective tissue) — every module answers what / where / how much / significant, with Mann-Kendall + Sen's slope:
  - Fire: Canada MODIS detections +3,019/yr, 2003–2025, p = 0.035 (Argentina falling, p < 0.001).
  - Water: Valencia wettest-day rain no trend (p = 0.28, 1981–2025) while GRACE/GRACE-FO water storage is falling (−0.39 cm/yr, p = 0.002, 2003–2025): drying ground, then a flash flood. Southern Ontario storage rising (p = 0.014).
  - Crops: central Iowa frost-free season +0.43 days/yr (p = 0.006), first autumn frost later (p < 0.001), GDD rising; summer soil water flat; GRACE storage no trend (p = 0.57).
Module cards then show each project's best visual, problem statement, deliverables and a link to its full page + /app/.

## 03 HOW: data, methods, validation, limits
- NASA data table with a column "Earthdata login?" (FIRMS, POWER, CMR/ASF NISAR browse, NASADEM, MODIS NDVI = no login; GRACE/GRACE-FO mascons, OPERA DSWx-S1 = Earthdata login; others added as the Earthdata worker delivers).
- Methods: harmonizer (empirical-Bayes ratio + LightGBM + conformal intervals), U-Net on Sen1Floods11, LightGBM crop model + NSGA-II, Mann-Kendall + Sen's slope (95% CI) + Hamed-Rao check.
- Validation: held-out later years, baselines, second-series checks, honest misses (Canada monthly-total fire error 39.4% vs 16.7% baseline; Ontario annual rain drop not robust to autocorrelation).
- Limits: one seed per model; trends show change, not cause; GPM IMERG / GLDAS pending GES DISC access.

## Project pages (/hotspots/, /sar-change/, /field-shift/) — full, unchanged demos
Hero → live demo iframe (+ full screen /app/) → WHY (problem statement) → WHAT (results, visuals, Earthdata upgrade, trend layer) → HOW (approach, data with login column, limits) → judging criteria.

## Update 10:30 AM ET — module upgrades now live on the site (Earthdata login)
- Detect / Hot Spots: MODIS MCD64A1 burned area, tile h11v03 (~50–60°N, western Canada), Apr–Oct 2003–2025: +272 km²/yr (Sen, 95% CI +57 to +503), MK p = 0.004 (Hamed-Rao p = 0.004). Largest season 2023: 28,262 km². Caveat: one tile; 2023 at the end of the record.
- Confirm / SAR Change: OPERA DSWx-S1, 18 passes: new water 30.7 km² (26 Oct) → 77.7 km² (31 Oct), then ~30–60 km² for three weeks. Mostly the Albufera wetland and rice fields.
- Adapt / Field Shift: HLS 30 m NDVI, Story County, 1 Aug 2024 vs 31 Jul 2025: median change −0.01; 42 km² greener, 22 km² less green (>0.1). Two dates only, not a trend. SMAP L3 enhanced: May–Sep 0.19–0.23 m³/m³ in 2015–2018; too short to test (p = 0.73), context only.
- Trend layer: GRACE/GRACE-FO in the water and crops widgets (Valencia −0.39 cm/yr p = 0.002; Ontario +0.55 cm/yr p = 0.014; Iowa no trend p = 0.57). GPM IMERG / GLDAS pending (being fetched).
- Section labels on site: big "Why / What / How" part marks; landing "What" is a pinned 4-step pipeline 01 Detect · 02 Confirm · 03 Adapt · 04 Measure.

## Update 10:40 AM ET — IMERG / GLDAS / SMAP wired in
- Ontario: the MERRA-2 drop in rain extremes is NOT confirmed by GPM IMERG (annual p = 0.28, wettest month p = 0.36). Site no longer claims Ontario extremes are falling.
- Valencia: IMERG 1998–2024 no trend (annual p = 0.62, Sep–Nov p = 0.80, wettest month p = 0.21).
- Iowa: GLDAS soil moisture no trend at any depth (p = 0.27–0.38); SMAP 2015–2025 no trend (Story County p = 0.47, central Iowa p = 0.21); IMERG annual no trend (p = 0.50); GRACE no trend (p = 0.57).
- Caveats on site: Albufera paddies already rising before the flood (4 → 31 km², 1–26 Oct); urban flooding under-detected by SAR; HLS can't separate crop types.

## 14 Nov 2026, 11:40–12:30 ET pass: less text, people, actions, impact
- Every page now reads: 1 problem (picture + one number) → 2 what the satellite shows (chart/map + one number) → 3 actions ("Satellite shows → I will → Expected", 4–5 per app, different classes) → 4 impact (geospatial finding vs human impact, plus a real model-metrics strip). Methods, data, limits, trend findings and judging moved into collapsible "deep dive" panels.
- Illustrative AI-generated photos of the people who use each tool, labelled "Illustrative" on every image. No logos, brands or real people.
- Each dashboard (/hotspots/app/, /sar-change/app/, /field-shift/app/) now has a 4-step guide (See the map → What changed → Actions → Impact) as a right-hand panel on desktop and a bottom sheet on phones, with buttons that drive the dashboard (Alberta preset, swipe, metrics tab, featured tile). Tabs are larger and higher-contrast.
- Mobile pass at 390×844 and 768×1024: centred headings, cards and images; no horizontal overflow; 44 px tap targets.
- Fixed: section titles no longer hide under the sticky nav; SAR story IoU corrected to 66.4% vs 21.8% (metrics.json).
