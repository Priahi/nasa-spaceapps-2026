# Orbit to Ground: story spine (pitch, deck, video, site)

Coach's advice (Plaud, "Pitch Story Strategy for Judges", 14 Nov 2026): lead with the single best human story,
told as before and after ("something bad happened, now rewind and see how the tool changes it"), aim for human value rather than money,
then tell a second story, and only then broaden it: "you're feeling that now, imagine it times twenty". Don't open with twenty use cases and then pick two.

## The acts

| # | Act | What the audience feels | Deck slide | Video |
|---|-----|-------------------------|-----------|-------|
| 1 | **Hook**: the night of 29 Oct 2024, Valencia | "This really happened." | 1 | 0–3 s |
| 2 | **Her night, as it happened** (real timeline, composite person) | the gap between the warning and the phone alert | 2 | 3–9 s |
| 3 | **Rewind, with Orbit to Ground** (rain signal → radar map → alert → dispatch → aid) | "that could have gone differently" | 3 | 9–25 s |
| 4 | **How it works + metrics** (under the hood) | "this is real, not a mock-up" | 4 | n/a |
| 5 | **Second story: fire**, a duty officer before the season | "and it works again" | 5 | 25–27 s |
| 6 | **Times twenty**: Field Shift and other *built* capabilities, then clearly labelled *future* uses | "imagine it times twenty" | 6 | 27–30 s montage |
| 7 | **Impact, team, close** | human value | 7 | end card |
| 8 | **Demos** (flood is the primary embed) + live links | try it | 8 | n/a |

## The person (story 1)

**Elena** is the municipal emergency coordinator in **Catarroja**, one of the 8 towns where our radar map finds the most new water.
She is an **illustrative composite**, not a real person. Always label her "Illustrative composite" in small text. Never give her quotes
taken from real victims, never attach real deaths to her, and never imply she existed. Her day only uses the public, sourced timeline below.

## What happened on 29 Oct 2024 (sourced; cite these, don't embellish)

| Time (CET) | Fact | Source |
|---|---|---|
| 07:36 | AEMET raises a **red warning** (first for the north interior of Valencia, the south coast soon after, and four zones by 09:48) | Newtral timeline; EchoGéo (2025) |
| all day | Turís station: **771.8 mm in 24 h** and **184.6 mm in one hour**, a Spanish national record (616.8 mm between 15:00 and 20:00) | AEMET event study; ECMWF Newsletter 183 |
| ~12:07 | The Poyo ravine passes its pre-alert threshold (**264 m³/s** around noon) | Reuters, 9 Nov 2024; The Conversation |
| 18:43 | The Poyo reaches **1,686 m³/s** and rising fast; **2,282 m³/s** at 18:55, before the gauge was destroyed | Reuters; La Vanguardia |
| 20:11 | First **ES-Alert** to phones across the province ("avoid any travel"), **about 12.5 h after the red warning** | Newtral; El País; EchoGéo |
| by 20:11 | **At least 156 of the 229 victims had already died**, and 37 more were in critical danger; more than 15,943 calls had reached 112 | El País, 26 Oct 2025 |
| total | **229 deaths** in the Valencia region (El País); EchoGéo counts 236 nationwide. Catarroja: 25. Paiporta: 45 | El País; EchoGéo |

Source URLs:
- AEMET, event study 28 Oct–4 Nov 2024 (PDF): https://www.aemet.es/documentos/es/conocermas/recursos_en_linea/publicaciones_y_estudios/estudios/estudio_28_oct_4_nov_2024.pdf
- ECMWF Newsletter 183, "Extreme precipitation in Spain's Valencia region": https://www.ecmwf.int/en/newsletter/183/news/extreme-precipitation-spains-valencia-region
- El País, "Cómo, dónde y a qué hora murieron las 229 víctimas de la dana" (26 Oct 2025): https://elpais.com/espana/2025-10-26/como-donde-y-a-que-hora-murieron-las-229-victimas-de-la-dana.html
- Newtral, "Cronología de los avisos por dana en Valencia": https://www.newtral.es/avisos-dana/20241031/
- Reuters, "How slow warnings, poor defences left Spain exposed to deadly floods" (9 Nov 2024): https://www.reuters.com/business/environment/spains-flood-disaster-was-its-worst-recent-history-heres-what-went-wrong-2024-11-09/
- La Vanguardia, "Hasta las 18:43 la CHJ no comunicó la gran crecida en el barranco del Poyo": https://www.lavanguardia.com/local/valencia/20250409/10568338/emergencias-juzgado-18-43-chj-comunico-gran-crecida-barranco-poyo.html
- EchoGéo, "Analyse d'une alerte massive arrivée tardivement… Valence, 29 octobre 2024": https://journals.openedition.org/echogeo/30425

## Rewind: what our tool shows for the same event (our real outputs only, worded as "could have")

1. **Rain signal (leading).** NASA GPM IMERG V07 daily, upstream box (lon −1.0 to −0.3, lat 39.2 to 39.6): **91.0 mm mean on 29 Oct,
   135.1 mm in the wettest 0.1° cell**, against a few mm on the days before. NASA POWER cloud amount: **99%** that day, so optical satellites were blind and radar was needed.
   The "alert when upstream rain passes 50 mm" rule is a **design example**, not a tested or measured result.
   Our series is the research-grade Final run; a live system would use IMERG's near-real-time runs. We have **not** tested their timing.
2. **Radar flood map (confirm).** NASA/JPL OPERA DSWx-S1 (Sentinel-1, 30 m): **77.7 km² of new water on 31 Oct**, up from 30.7 km² on 26 Oct (**+47.0 km² net**),
   mapped through cloud. **75.8 km²** of it sits in 8 municipalities: Sueca, València, Sollana, Silla, Alfafar, Catarroja, Cullera, Massanassa.
   Our own radar water model: **66.4% IoU** on 90 hand-labelled Sen1Floods11 test chips, against **21.8%** for the standard Otsu threshold (3.0×); 1.63 s per 512×512 tile on a CPU.
3. **Draft alert (simulated).** The dashboard drafts an alert to those 8 towns: the new-water area, the upstream rain, and "stay off low ground and flooded roads".
4. **Dispatch (simulated).** Rescue teams go to the flagged districts, and the next radar pass is queued.
   Damage teams also go to l'Horta Sud streets that radar can't see (dense streets: radar maps only 0.48 km² across 8 of those towns, so drones check them).
5. **Aid (simulated).** Farm recovery aid and insurance checks go to the Albufera paddy towns (Sueca, València, Sollana, Cullera).

Safe sentence: *"With an upstream rain signal and a radar map, Elena could have had a drafted alert for her town hours before 20:11, and a map of where the water went on day two."*
**Never** say lives would have been saved, that the alert would have gone out at a specific time, or that the tool predicts floods.

## Story 2: fire (chosen over Field Shift because its data is denser)

Decision, made 14 Nov from the data files:
- **Fire:** 11,616,131 NASA FIRMS detections behind Hot Spots, 2000–2025. That is **Canada 7,461,416** (MODIS 1,444,577 + VIIRS 6,016,839) plus Argentina 4,154,715
  (`demos/hotspots/data/extras.json`). Note that "11.6 M" covers both countries; Canada alone is **7.46 M**.
  Canada also has 94,239 MODIS and 103,306 VIIRS 0.25° cell-months, and 498,302 test cell-months.
- **Field:** 923 squares in one Iowa county (Story County), from `demos/field-shift/data/app_data.json` `fields`.
- Fire wins, so it is story 2 and Field Shift leads the "times twenty" slide.

**The duty officer** (an illustrative role, no name needed): a provincial wildfire duty officer in Alberta, planning staff and warnings before the season.
- Trend: detections rising **+1,503 a year in Alberta (p = 0.035)** and **+2,587 a year in B.C. (p = 0.045)**, 2003–2025, from harmonized FIRMS with Sen's slope.
  Tentative: the single-sensor check isn't significant. Canada-wide: **+3,019/yr (p = 0.035)**; boreal burned area **+272 km²/yr (p = 0.004)**.
- **May is the watch month:** 5 of Alberta's 16 unusual fire months since 2000 were in May (2011, 2016, 2019, 2023, 2025).
- Staffing alert (simulated): stage initial-attack crews before July and open seasonal hiring this spring. If the trend line holds, 2026 is about 41,000 detections in Alberta and 72,000 in B.C.
  This is a trend line, not a forecast; single years swing far wider (2023: 390,000 and 372,000).
- Pre-May community notice (simulated): "check your evacuation plan before May".
- Model: 8.5% lower error than the best baseline (RMSE 0.2844 vs 0.3109, Canada 2022–25); 88.6% interval coverage (target 90%).
  Honest miss: monthly-total error 39.4% vs a 16.7% baseline.

## Times twenty (one slide)

**Built** (live today):
- Field Shift: next-season crop for every 30 m pixel in Story County, Iowa (81.8% correct), a farmer view, and rye on the steep fields (the cover-crop rotation scores 67% lower erosion risk).
  Frost-free season +19 days since 1981 (p = 0.006).
- Hot Spots for Argentina too (4.15 M detections; falling −1,909 a year).
- Groundwater drop over eastern Spain (GRACE −0.39 cm/yr, p = 0.002).
- Burn calendar for any drawn area, and soil-water trend checks (GRACE, GLDAS, SMAP, IMERG: no trend).

**Future** (not built; label it "Future"): the same signal → map → alert → task loop for landslides after rain, drought and crop stress, coastal storm surge,
smoke and air quality for schools, and heat waves for care homes.

## Our numbers (single source of truth)
Flood: 91.0 mm / 135.1 mm upstream rain on 29 Oct; 99% cloud; 30.7 → 77.7 km² (+47.0 net); 8 towns hold 75.8 km²; IoU 66.4% vs 21.8% (3.0×); 1.63 s/tile; water held at 30–60 km² for 3 weeks over 7 passes; wettest-day rain trend p = 0.28 (no trend, so we don't claim one).
Fire: as above. Field: 0.8176 accuracy (crop history alone 0.8136), macro-F1 0.5012 (baseline 0.4633), 0.811 pixel accuracy, 22 km² got less green. Honest miss: hay F1 0.33.
Every model score is from one seed and is not a published benchmark.

## Wording rules
- Tasking, dispatch, alerts and messages are **simulated**. Say so wherever they appear.
- The composite person carries "Illustrative composite" in small text. Don't quote real victims or name real victims.
- Use "could have", never "would have saved". Make no lives-saved or time-saved claims, and no invented outcome numbers.
- The 50 mm rule is a design example. Trend lines are not forecasts.
- No AI-generation wording in the deck or video. No company, client or product names. The team is "Team GeoAI Toronto", Parsa Riahi (solo).
- Human value first, not money.
