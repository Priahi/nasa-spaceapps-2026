# Impact what-ifs: Orbit to Ground on three real cases

**Read this first.** Every estimate below is an **illustrative what-if**, not a measured outcome and not a prediction.
Each one takes a published, sourced relationship (for example "24 hours of warning cuts damage by 30%") and applies it to a sourced bill from a real event, showing all the arithmetic.
Our dashboards' alerts, dispatch and tasking are **simulated**: nothing was sent to anyone in 2024 or since.
We do **not** claim lives saved. Where we mention lives, we quote a published range for a *different* event, with its caveats, and we don't convert it into a number for ours.
Every URL below was fetched on 14 Nov 2026 and checked against the quoted figure.

The same idea runs through all three cases. NASA data (rain, radar, fire, crops) is turned into a **specific, local, actionable message earlier** than the message people actually got.
How much that is worth depends on how much earlier it arrives. The published evidence says the value climbs quickly over the first day and then **levels off**, so it doesn't keep adding 30% for every extra day.

---

## 1 · Flood: Valencia DANA, 29 October 2024 (SAR Change)

### Baseline facts (sourced)
| Fact | Value | Source |
|---|---|---|
| Deaths, Valencia region | 229 | El País, 26 Oct 2025 [F1] |
| Died before the 20:11 phone alert | **at least 156**, plus 37 more already in critical danger (193 of 229, 84%) | El País [F1] |
| First recorded death | 11:45 (a truck driver at the Benimodo ravine) | El País [F1] |
| Deaths over time (El País count, "at least") | 1 by 12:59 · 10 by 16:59 · 25 by 17:59 · 60 by 18:59 · 142 by 19:59 · 156 by 20:11. Worst hour 19:00–20:00: 82 deaths | El País [F1] |
| Where people died | at least 60% inside buildings: 50 in ground-floor flats, 33 in houses, 39 in garages, 12 in care homes | El País [F1] |
| AEMET red warning | 07:36 (El País gives 07:35) | Newtral; El País [F1][F2] |
| EFAS (European Flood Awareness System) notices | formal Turia river notification on 26 Oct; flash-flood notification email on **28 Oct at 07:23** for the Valencia region (39% chance of a 5-year flood and 17% of a 20-year flood from noon on 29 Oct). Not binding: it "invites monitoring" | EFAS 2024 missed-events report [F3]; El País, 28 Dec 2024 [F4] |
| First ES-Alert to phones | 20:11, "avoid any travel" | El País [F1]; Newtral [F2] |
| Insured bill (Consorcio de Compensación de Seguros, CCS) | more than 250,000 claims; over €4 bn paid; **estimated final cost about €4.8 bn**; vehicles: more than 140,000 claims, close to €1.2 bn | CCS magazine no. 23 [F5]; Government of Spain, 26 Nov 2025 [F6] |
| Total asset loss | **at least €17 bn** (about 20% of the €85.9 bn of assets in 89 affected municipalities, excluding Valencia city) | Ivie [F7] |
| First post-storm radar pass over our area | OPERA DSWx-S1, **31 Oct 18:02 UTC**, about 47 h after the 20:11 alert | our `earthdata/sar-change/opera_valencia.json` |
| First Copernicus EMS maps | first map published 31 Oct (optical, GeoEye); province-wide extent map on **2 Nov** (from Sentinel-1/2 images taken on 31 Oct): about 15,633 ha flooded and about 190,000 people potentially affected | ESA [F8] |

### What the published evidence says about lead time
| Lead time | Avoided damage | Source and caveat |
|---|---|---|
| 0 → 4 h | about 10% | Day (1970) curve, as reported by the National Hydrologic Warning Council [F9] |
| 4 → 12 h | **+12%** (about 22% in total at 12 h) | same [F9] |
| 24 h | **30%** ("Just 24 hours warning of a coming storm or heat wave can cut the ensuing damage by 30 percent") | Global Commission on Adaptation, *Adapt Now* (2019), Box ES.1 [F10]; repeated by UNEP [F11] |
| 48 h | **4–40%** across published studies; 32.85% when all warning pathways are combined (used for EFAS) | Pappenberger et al. (2015), *Env. Sci. & Policy* [F12] |
| Domestic property only | 4.5–7.3% | SNIFFER and others, cited in [F12] (a conservative floor) |

The curve flattens after about a day: 30% at 24 h, but no study we found reaches 60% at 48 h. So "30% for **each** 24 h" is **not supported**, and we don't use it.

### What-if table (illustrative; damage only)
How the 6 h and 12 h factors were set: 6 h is a straight-line interpolation of the Day curve (10% + 12% × 2/8 = **13%**, our interpolation). 12 h = 22%, 24 h = 30% and 48 h = 32.85% (range 4–40%) come directly from the table above.
Both bills are multiplied by the same factor. This is an **upper bound**: it assumes everyone got the alert and acted on it, and much of the bill (buildings, roads, the €2.9 bn of infrastructure inside the Ivie figure) can't be moved out of the water.

| Alert sent | Clock time | When it lands, against the deaths El País dates | Avoided-damage factor | × €4.8 bn insured (CCS) | × €17 bn assets (Ivie) |
|---|---|---|---|---|---|
| Actual | 20:11, 29 Oct | after at least 156 deaths | baseline | – | – |
| **6 h earlier** | 14:11 | before at least 146 of those 156 (only 10 dated before 17:00) | 13% | **€0.62 bn** | €2.2 bn |
| **12 h earlier** | 08:11 (≈ AEMET red warning, 07:36) | **before the first recorded death (11:45)** and about 11 h before the worst hour | 22% | **€1.06 bn** | €3.7 bn |
| **24 h earlier** | 20:11, 28 Oct (EFAS notice already out at 07:23 that day) | before the rain peak | 30% | **€1.44 bn** | €5.1 bn |
| **48 h earlier** | 20:11, 27 Oct | before the rain | 32.85% (4–40%) | **€1.58 bn** (€0.19–1.92 bn) | €5.6 bn (€0.68–6.8 bn) |
| Floor (domestic property only, 12 h) | – | – | 7.3% | €0.35 bn | €1.24 bn |

Arithmetic: €4.8 bn × 0.13 = €0.62 bn; × 0.22 = €1.06 bn; × 0.30 = €1.44 bn; × 0.3285 = €1.58 bn; × 0.073 = €0.35 bn. €17 bn × the same factors.

### Lives: what we can and can't say
- **Fact, not a what-if:** an alert at 08:11 would have reached phones about 3.5 h before the first recorded death, and at 14:11 it would still have come before at least 146 of the 156 deaths dated before 20:11 [F1]. That is **people reached before the event**, not lives saved.
- **Content matters as much as timing.** At least 60% died indoors, 39 of them in garages [F1], and the real alert only said "avoid travel". A 2025 peer-reviewed simulation of Germany's 2021 Ahr Valley flash flood (134 deaths) found that the first warning came **13 h before the peak**, but only 17.5% of people got one with evacuation instructions. It also found that with timely warnings and fast evacuation, modelled deaths fell by **up to 80%**, and by 24.3% with better spreading of the warning alone. Telling people to evacuate at the last minute *raised* deaths; going upstairs was safer [F13].
  These are the Ahr's modelled numbers. **We do not apply them to Valencia.**
- Across countries, the UNDRR/WMO 2023 global status report finds that countries with limited early-warning coverage have **nearly six times** the disaster mortality of those with substantial coverage (4.05 vs 0.71 deaths per 100,000) [F14]. This is a correlation, not a causal estimate for one event.

### The honest "days earlier" claim
- **Hours, for the warning.** Our leading signal is observed rain (GPM IMERG). IMERG Early arrives about 4 h after observation and Late about 12–14 h after; the Final run we used for research arrives months later [F15]. We have **not** tested IMERG's near-real-time timing on this event.
  On 29 Oct the danger was already known: AEMET's red warning came at 07:36 and EFAS sent notices on 26 and 28 Oct. The 12 h scenario needs no new detection. What it needs is turning that signal into a drafted, town-specific alert with the right instructions, and that is what our dashboard does (simulated).
  The 24 h and 48 h rows rely on forecasts (AEMET, EFAS, ECMWF), which our tool doesn't make.
- **Days, for the map.** It was 99% cloudy on 29 Oct (NASA POWER, our run), so optical satellites were blind. With only Sentinel-1A in orbit, Sentinel-1 had a 12-day repeat cycle; Sentinel-1C launched on 5 Dec 2024 and restored 6 days [F16].
  The first post-storm radar map over our area came on 31 Oct, about 2 days after the rain. The first province-wide EMS extent map came on 2 Nov, about 4 days after [F8].
  So the rain signal gives **about 2 days of warning that the satellites can't give**, and **NISAR** (L-band, sees flooding under vegetation) adds more radar passes for the next event. That is the honest version of "2–3 days earlier when the satellites aren't passing over".

### Slide headline
> **12 hours earlier = an alert before the first death. Published warning curves put about €1.1 bn of Valencia's €4.8 bn insured loss within reach (illustrative what-if: 22% × €4.8 bn).**

### How it compares with what exists today
| Today | What it does | Gap on 29 Oct | How Orbit to Ground differs |
|---|---|---|---|
| **AEMET warnings** | official weather warnings by zone (red at 07:36) | a weather warning isn't an instruction to the public; it was 12.5 h before phones were alerted [F1][F2] | turns the rain signal into a drafted, **town-specific** alert ("go up, keep out of garages and ground floors") ready to send (simulated) |
| **EFAS** (and GloFAS globally) | flood-probability notices to authorities, up to 48 h ahead for flash floods [F3][F4] | went to agencies by email, wasn't binding, underestimated the size (17% for a 20-year flood) [F4] | doesn't replace EFAS forecasts. It adds observed NASA rain + radar evidence on one screen with a task queue, so a notice becomes an action |
| **ES-Alert** | broadcast to phones | sent at 20:11 with "avoid travel" only [F1] | the dashboard pre-fills the message and the target towns from the map, cutting the decision step (simulated; no real ES-Alert link) |
| **Copernicus EMS rapid mapping** | expert flood maps after activation (activated 29 Oct) [F8] | first maps 31 Oct; province-wide extent 2 Nov [F8] | open NASA OPERA radar water every pass (31 Oct, our run), linked to rain, trend tests and simulated dispatch; NISAR-ready. Complements EMS, not faster for the first map |

---

## 2 · Fire: Alberta, the May 2016 Horse River (Fort McMurray) fire and the 2023 season (Hot Spots)

### Baseline facts (sourced)
| Fact | Value | Source |
|---|---|---|
| Horse River fire | spotted 1 May 2016 at 16:03, about 2 ha; final size 589,552 ha | MNP review for Alberta (2017) [W1] |
| Evacuated | almost 88,000 | KPMG post-incident assessment [W2]; MNP 2025 [W3] |
| Cost | **$3.58 bn insured** (IBC); total monetary impact **almost $8.9 bn** as of May 2017; 1,989 structures lost or damaged | IBC [W4]; MNP 2025 [W3] |
| Readiness in 2016 | snow gone by mid-April, ≥2 weeks early; some resources were still in a "spring start-up" mindset before 1 May. Recommendation 1: be fully ready the week after snow disappears **or 1 May, whichever comes sooner** | MNP review [W1] |
| Honest caveat | initial attack on Horse River was immediate, and "it is not possible to determine whether any alternative decisions … would have resulted in a different outcome" | MNP review [W1] |
| Alberta 2023 | first local evacuation order 29 Apr; 1,088 fires; about 2.2 M ha; about 38,000 evacuated; 0 wildfire deaths | MNP 2025 [W3] |
| Staffing date | Alberta Wildfire "doesn't typically have full staff … until the beginning of May"; for 2024 it moved full staffing to **15 April**. The Drayton Valley fire started on 23 Apr 2023 | The Weather Network, 19 Jan 2024 [W5] |
| Why the start matters | about 97% of Canadian fires are held below 200 ha; the 3% that escape cause **97% of the area burned** (1959–97) | Stocks et al. (2002), *JGR* [W6] |
| Canada 2023 | more than 230,000 people evacuated; more than 14.6 M ha burned | Natural Resources Canada [W7] |

### Our signal (from our own runs, in STORY.md)
Five of Alberta's 16 unusual fire months since 2000 were in **May**, including 2016 and 2023. Alberta detections are rising by +1,503 a year (p = 0.035, tentative).
This is known **in winter, months before the season**, from the harmonized 2000–2025 FIRMS record. It's a trend and a seasonal pattern, not a forecast of any one fire.

### What-if table (illustrative)
**A. Days of full readiness before the first big fires** (dates sourced; the 15 April target is Alberta's own 2024 policy [W5])
| Season | First big fire / evacuation | Full staffing (actual practice) | With a pre-season "May watch" flag → full staffing on 15 Apr |
|---|---|---|---|
| 2016 | Horse River, 1 May | target "by 1 May" → 0 days of margin [W1] | **16 days** of full readiness first |
| 2023 | Drayton Valley fire 23 Apr; first evacuation order 29 Apr | early May [W5] → fires came about 1–2 weeks **before** full staffing | **8 days** before the first fire; 14 days before the first evacuation order |

**B. What each escape avoided is worth** (uses the Canadian 3%/97% rule [W6] on Alberta 2023 [W3]; this is our assumption, since Alberta's own split wasn't sourced)
- Escaped fires: 1,088 × 3% ≈ **33**. They carry 97% × 2.2 M ha ≈ 2.13 M ha, about **65,000 ha per escape** on average.

| Escapes prevented by earlier staffing | Area not burned | Share of the 2023 season |
|---|---|---|
| 1 | about 65,000 ha | 3.0% |
| 2 | about 131,000 ha | 5.9% |
| 5 | about 327,000 ha | 14.9% |

For scale, one escaped May fire next to a town (Horse River) cost $3.58 bn insured and about $8.9 bn in total, and moved 88,000 people [W2][W3][W4].
We don't claim staffing would have stopped that fire (see the MNP caveat). We found no source that links staffing dates to escape rates, so the number of escapes prevented is the assumption you vary.

### Slide headline
> **The data flags May months ahead: staffing on 15 April instead of 1 May gives 16 more days of readiness. Every escape prevented spares about 65,000 ha (illustrative, Alberta 2023), and one escaped May fire cost $8.9 bn in 2016.**

### How it compares with what exists today
| Today | What it does | How Orbit to Ground differs |
|---|---|---|
| **NASA FIRMS** | active fires within about 3 h of a satellite pass worldwide; real-time and ultra-real-time (minutes) for the US and Canada; "well suited for … near real-time alert systems" [W8] | FIRMS says *where it's burning now*. We harmonize MODIS (2000–) and VIIRS (2012–) into **one 26-year, single-scale record** so seasons can be compared and trends tested (Mann-Kendall, p-values). That matters more now that FIRMS reports Suomi NPP is no longer delivering new data, so another sensor change is under way [W8] |
| **CWFIS** (Natural Resources Canada) | daily national fire weather, fire behaviour and occurrence maps since 1994, from more than 2,500 weather stations plus satellite hotspots; "not designed for operational fire management purposes" [W9] | CWFIS covers days, from weather. We add the **multi-year, per-province** view (is May getting worse here?) and a simulated pre-season task list: hiring, crew staging, community notices |
| **Provincial readiness by fixed date** (Alberta: 1 May, now 15 Apr) [W1][W5] | calendar-based | set the date from the province's own satellite record of unusual months, reviewed every winter |

---

## 3 · Farms: the 2012 US drought and Iowa (Field Shift)

### Baseline facts (sourced)
| Fact | Value | Source |
|---|---|---|
| Iowa corn yield | 172 bu/acre (2011) → **137 bu/acre (2012)**, −20% | USDA NASS *Crop Production 2012 Summary* [A1] |
| Iowa corn production | 2,356.4 M bu → 1,876.9 M bu (**−479.5 M bu**) | NASS [A1] |
| Corn price, 2012/13 marketing year | **$6.89/bu** (US season average) | USDA FSA [A2] |
| US crop-insurance indemnities, 2012 | **$16.99 bn**, a record, "largely the result of the severe drought" | USDA figures reported by the American Soybean Association [A3] |
| Cover crops in the 2012 drought | corn **+11.1 bu/acre (+9.6%)** and soybeans +4.9 bu/acre (+11.6%) after cover crops, compared with similar fields without them | SARE/CTIC 2012–13 Cover Crop Survey [A4] (self-reported farmer survey, not a trial) |
| Cover-crop cost in Iowa (2015) | seed $17.70/acre + custom planting $14.39/acre before corn (mean), not counting termination. "Iowa farmers tend to obtain negative annual returns on cover crops" unless they get grazing or cost-share benefits | Plastina et al., Iowa State (2018) [A5] |
| When the USDA crop map comes out | the Cropland Data Layer (CDL) is released after the season (2012 CDL: 31 Jan 2013; 2025 CDL: 27 Feb 2026). 2025 overall crop accuracy: 75.4% | NASS CDL FAQ [A6] |
| Planting intentions | NASS *Prospective Plantings*, released 31 Mar 2026, **state-level** (Iowa corn 13.1 M acres) | NASS [A7] |

Value of Iowa's 2012 corn shortfall (our arithmetic): 479.5 M bu × $6.89 = **about $3.3 bn**. This is illustrative: it values the gap at the 2012 national price and ignores the small change in harvested area.

### Our signal (from our own runs)
Next-season crop for every 30 m pixel in Story County: 0.8176 accuracy (crop history alone: 0.8136), from one seed, so it's not a benchmark.
The frost-free season is +19 days since 1981 (p = 0.006), while summer water shows no trend.
The farmer view ranks winter rye for the **92 steepest squares**: about **107 km², or 26,500 farmed acres** (our `app_data.json`: farmed 30 m pixels × 900 m²).

### What-if table (illustrative; one drought year like 2012)
Assumes all 26,500 acres are in corn with a rye cover crop, and that the SARE 2012 survey average applies. SARE is self-reported and national; Iowa results will differ.

| Item | Per acre | × 26,500 acres (92 steepest squares) |
|---|---|---|
| Extra corn in a 2012-type drought: 11.1 bu × $6.89 | +$76.48 | +$2.03 M |
| Cover-crop cost (seed + planting, 2015 Iowa mean) | −$32.09 | −$0.85 M |
| **Net in a drought year** | **+$44.39** | **+$1.18 M** |
| In a normal year | usually negative without grazing or cost-share [A5] | – |

So rye on the steep fields works like **insurance that pays in drought years**: it costs a little in most years and paid back about 2.4× its seed and planting cost in 2012 (per SARE). It also cuts erosion (the 67% lower erosion *score* is a planning score from our model, not measured soil loss).

### Lead time
Our next-season map can be made as soon as the previous year's CDL is out (about February), **before planting**, at **30 m pixel** level.
The official alternatives are state-level intentions (31 March) and the CDL *for that season*, which arrives about **11 months later** (for example, the 2026 season's CDL is due around February 2027, going by past release dates [A6]).

### Slide headline
> **In a 2012-type drought, rye on Story County's 92 steepest squares is worth about $1.2 M net (illustrative: +11.1 bu/acre × $6.89 − $32/acre, SARE 2012 survey × ISU costs), and our map is ready before planting instead of 11 months after.**

### How it compares with what exists today
| Today | What it does | How Orbit to Ground differs |
|---|---|---|
| **USDA NASS Cropland Data Layer** | the best crop map of what *was* planted, released about Feb of the next year; 75–82% overall crop accuracy in recent years [A6] | we predict *next* season per pixel, before planting (0.8176, one county, one seed: a different task, so the accuracies aren't directly comparable) |
| **NASS Prospective Plantings / Crop Progress** | state-level surveys (31 Mar) and weekly state progress [A7] | field-level, with the climate trend (frost-free days, soil water) attached |
| **Cover-crop programs** | cost-share by application | ranks the fields where rye pays off most (steep, erosion-prone) using NASA DEM, POWER, SMAP and GRACE trends |

---

## Sources (all fetched and checked on 14 Nov 2026)
**Flood**
- [F1] El País, "Cómo, dónde y a qué hora murieron las 229 víctimas de la dana", 26 Oct 2025. https://elpais.com/espana/2025-10-26/como-donde-y-a-que-hora-murieron-las-229-victimas-de-la-dana.html
- [F2] Newtral, "Cronología de los avisos por dana en Valencia". https://www.newtral.es/avisos-dana/20241031/
- [F3] CEMS-EFAS, "Analysis of feedback on notifications and missed events reports 2024". https://european-flood.emergency.copernicus.eu/sites/default/files/CEMS-EFAS_Overview-of-all-reported-missed-events-during-2024_1.pdf
- [F4] El País, "El sistema europeo avisó del riesgo de inundación en Valencia días antes de la dana, pero subestimó su magnitud", 28 Dec 2024. https://elpais.com/clima-y-medio-ambiente/2024-12-28/el-sistema-europeo-aviso-del-riesgo-de-inundacion-en-valencia-dias-antes-de-la-dana-pero-subestimo-su-magnitud.html
- [F5] Consorseguros Digital no. 23, "The 2024 Valencia Floods: The Ultimate Test for the Spanish Insurance System". https://consorsegurosdigital.com/en/numero-23/sumario/contributions/valencia_floods/
- [F6] La Moncloa, "El Consorcio de Compensación de Seguros supera los 4.000 millones…", 26 Nov 2025. https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/economia-comercio-empresa/paginas/2025/261125-indemnizacion-dana.aspx
- [F7] Ivie, "La dana puede haber destruido al menos el 20% de los 85.900 millones de euros de activos…". https://www.ivie.es/es_ES/la-dana-puede-haber-destruido-al-menos-el-20-de-los-85-900-millones-de-euros-de-activos-privados-y-publicos-localizados-en-los-municipios-inundados/
- [F8] ESA, "Devastating floods in Spain witnessed by satellites". https://www.esa.int/es/articles/about-us/directorates/earth-observation-programmes/devastating-floods-in-spain-witnessed-by-satellites
- [F9] National Hydrologic Warning Council (2006), *Flood management benefits of USGS streamgaging program*, p. 30 (Day 1970 curve). https://water.usgs.gov/osw/pubs/Flood_Management_benefits_complete.pdf
- [F10] Global Commission on Adaptation (2019), *Adapt Now*, Box ES.1 (source: Hallegatte 2012, World Bank WP 6058). https://gca.org/wp-content/uploads/2019/09/GlobalCommission_Report_FINAL.pdf
- [F11] UNEP, Climate Information and Early Warning Systems. https://www.unep.org/en/what-we-do/climate-action/climate-transparency/climate-information-and-early-warning-systems
- [F12] Pappenberger et al. (2015), "The monetary benefit of early flood warnings in Europe", *Env. Sci. & Policy* 51. https://centaur.reading.ac.uk/40264/1/PappenbergerMonetaryBenefit.pdf
- [F13] Rocha Silva, Eleutério, Apel, Kreibich (2025), "Assessing the impact of early warning and evacuation on human losses during the 2021 Ahr Valley flood…", *NHESS* 25, 1501. https://nhess.copernicus.org/articles/25/1501/2025/
- [F14] UNDRR/WMO, *Global Status of Multi-Hazard Early Warning Systems 2023*. https://www.undrr.org/reports/global-status-mhews-2023
- [F15] NASA GPM, "What determines the latency of IMERG?" https://gpm.nasa.gov/resources/faq/what-determines-latency-imerg and https://gpm.nasa.gov/data/imerg
- [F16] Copernicus Data Space Ecosystem, Sentinel-1 documentation. https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html

**Fire**
- [W1] MNP for Alberta Agriculture and Forestry (2017), *A Review of the 2016 Horse River Wildfire*. https://open.alberta.ca/dataset/7cc619bd-56ce-488e-b007-cada28430589/resource/6c6560d3-0a8e-4550-b1d1-86e58409dea2/download/2016horseriverwildfirereview-mar2017.pdf
- [W2] KPMG, *May 2016 Wood Buffalo Wildfire Post-Incident Assessment Report*. https://open.alberta.ca/dataset/accfd27e-5e08-4f6c-8cd9-188be0e1e1b2/resource/541f276f-2fb4-4789-a41f-ef5ce7c0eec5/download/2016-wildfire-kpmg-report.pdf
- [W3] MNP for the Alberta Emergency Management Agency (2025), *Government of Alberta 2023 Spring Wildfire Post-Incident Assessment*. https://open.alberta.ca/dataset/c8b32d6d-2b52-486d-a4f6-855ced2b9a71/resource/20e8af07-b2cd-43e4-b2e3-0eecbbd91a5b/download/pses-government-of-alberta-2023-spring-wildfire-post-incident-assessment-2025.pdf
- [W4] Insurance Bureau of Canada, 7 Jul 2016. https://www.newswire.ca/news-releases/northern-alberta-wildfire-costliest-insured-natural-disaster-in-canadian-history-585872181.html
- [W5] The Weather Network, "Alberta to fully staff wildfire crew earlier…", 19 Jan 2024. https://www.theweathernetwork.com/en/news/nature/outdoors/alberta-to-fully-staff-wildfire-crew-earlier-following-a-record-breaking-season
- [W6] Stocks et al. (2002), "Large forest fires in Canada, 1959–1997", *JGR* 107, 8149. https://sites.ualberta.ca/~flanniga/publications/2003%20Stocks%20et%20al.%20J%20Geophys%20Res%20-%20Large%20forest%20fires.pdf
- [W7] Natural Resources Canada, Forest fires. https://natural-resources.canada.ca/our-natural-resources/forests/wildland-fires-insects-disturbances/forest-fires/13143
- [W8] NASA Earthdata, FIRMS FAQ. https://www.earthdata.nasa.gov/data/tools/firms/faq
- [W9] Natural Resources Canada, Current wildland fire activity (CWFIS). https://natural-resources.canada.ca/forests-forestry/wildland-fires/current-wildland-fire-activity-cwfis

**Farms**
- [A1] USDA NASS, *Crop Production 2012 Summary* (Jan 2013). https://esmis.nal.usda.gov/sites/default/release-files/k3569432s/8s45qb85z/12579v877/CropProdSu-01-11-2013.pdf
- [A2] USDA FSA, marketing-year average prices. https://www.fsa.usda.gov/sites/default/files/documents/2016_mya.pdf
- [A3] American Soybean Association, "As Expected, New Record Set on 2012 Indemnities", 25 Apr 2013. https://soygrowers.com/news-releases/as-expected-new-record-set-on-2012-indemnities-2/
- [A4] SARE/CTIC, *2012–2013 Cover Crop Survey*, p. 26. https://www.sare.org/wp-content/uploads/SARE-CTIC-CC-Survey-Report-V2.8.pdf
- [A5] Plastina et al. (2018), *Economics of Cover Crops*, Iowa State University. https://www.card.iastate.edu/files/inline-files/plastina-180309.pdf
- [A6] USDA NASS, Cropland Data Layer FAQ. https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php
- [A7] USDA NASS, *Prospective Plantings*, 31 Mar 2026. https://release.nass.usda.gov/reports/pspl0326.pdf

## What we could not source (so we don't claim it)
- A lead-time → **fatality** curve for Valencia. We quote the Ahr 2021 simulation's own percentages and don't convert them into Valencia lives.
- Any study supporting **+30% per additional day**. Published values level off at about 30–40% by 48 h.
- The latency of NASA POWER's daily precipitation (its documentation page didn't load). We cite IMERG latency instead.
- Near-real-time IMERG performance on 29 Oct 2024 (we used the Final run).
- A Canadian study that measures how much **earlier staffing raises initial-attack success**, and Alberta's own escape share. CIFFC initial-attack statistics weren't retrieved. The number of escapes prevented is a free assumption.
- An Iowa-only 2012 indemnity total from USDA RMA (only the national $16.99 bn, via the American Soybean Association).
