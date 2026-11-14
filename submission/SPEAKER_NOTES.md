# Speaker notes: Orbit to Ground story deck (10 slides; the official demo is the 30 s video)

The spine and wording rules are in `submission/STORY.md`. "Elena" is an **illustrative composite**: say so out loud once, on slide 2.

## 1 · Hook: 29 October 2024
"On the 29th of October 2024, one town near Valencia got 771.8 millimetres of rain in a single day, a Spanish record for one hour. The alert reached people's phones at 8:11 that evening. By then, at least 156 people had died."
- Sources: AEMET event study (Turís 771.8 mm / 24 h, 184.6 mm / 1 h); El País, 26 Oct 2025 (at least 156 of 229 died before the 20:11 alert).
- The map on the right is our own radar flood map (NASA/JPL OPERA DSWx-S1, 31 Oct), with the dashboard simulation running.

## 2 · Imagine
"Imagine losing someone you love because no one knew how much rain was coming that day."
- Pause. Then point at the rain panel: it is our flood app's own chart (NASA GPM IMERG V07, NASA POWER cloud). One bar towers over five weeks: 91 mm upstream on 29 Oct.
- The timeline on the right is our dashboard's simulated timeline (T+ clock), the same night rewound. Say "simulated".
- "Elena is a composite, an emergency coordinator in Catarroja; 25 people died in her town."
- Facts row: 07:36 red warning (Newtral; El País gives 07:35); 11:45 first recorded death (El País); 18:55 Poyo ravine 2,282 m³/s (Reuters; La Vanguardia); 20:11 ES-Alert, at least 156 already dead (El País). 12 h 35 min between warning and alert; 229 deaths in the Valencia region.
- Don't quote or name real victims.

## 3 · Rewind, with Orbit to Ground
"Now rewind. Same night, same public NASA data."
1. Signal: GPM IMERG V07 daily, upstream box. 91.0 mm mean on 29 Oct and 135.1 mm in the wettest cell; the days before had a few mm. NASA POWER cloud amount was 99%, so optical was blind and radar was needed.
   An alert rule like "upstream rain over 50 mm" is a **design example**. We used the research-grade Final run; a live system would use the near-real-time IMERG runs, and we haven't tested their timing.
2. Map: OPERA DSWx-S1, 30.7 → 77.7 km² of new water (26 → 31 Oct, +47.0 km² net); 75.8 km² of it is in 8 towns, including Catarroja.
   The first post-storm radar pass came on 31 Oct, two days later, so the map is for response and recovery, not the warning itself.
3. Alert: one alert drafted for all 8 towns (simulated; nothing is sent).
4. Dispatch: rescue teams to the flagged towns, drones to the l'Horta Sud streets that radar under-detects (only 0.48 km² mapped there), and the next pass queued. Aid goes to the paddy towns. All simulated.
- Say "could have". Never "would have saved lives".

## 4 · Story 2: fire (chosen over Field Shift for data density: 7.46 M Canadian FIRMS detections vs 923 Iowa squares)
"Second story: a wildfire duty officer in Alberta, planning before the season."
- Left: all of Canada, fires per year (2003–2025 average, 0.25° squares), cropped to the fire extent (B.C. to Quebec, south of 62°N). 11.6 M detections in the full record.
- Right: the Alberta and B.C. map with crews and hiring placed, and the task queue moving (simulated).
- Detections are rising +1,503 a year in Alberta (p = 0.035) and +2,587 in B.C. (p = 0.045), 2003–2025, on the harmonized series. Tentative: the single-sensor check isn't significant.
- May is the watch month: 5 of Alberta's 16 unusual months since 2000 (2011, 2016, 2019, 2023, 2025).
- Staffing alert (simulated): stage crews before the July peak. Pre-May community notice (simulated): check evacuation plans.
- The trend line is not a forecast.

## 5 · One engine, many sectors
"One engine: signal, map, alert, task. Swap the satellite input and it serves another sector."
- Left: Field Shift's crop map for Story County, Iowa, every 30 m pixel (USDA NASS CDL 2025 layer in our app); next-season crop 81.8% correct on held-out 2024–25.
- Built: emergency management (flood), wildfire, agriculture, groundwater trend (GRACE −0.39 cm/yr, p = 0.002). Future, not built: drought alerts, smoke advisories, infrastructure exposure, landslide watch. Civil uses only.

## 6–7 · Under the hood (architecture figures)
- Each row: data in → prepare → model → output → results with sources.
- Radar water U-Net trained on Sen1Floods11: 66.4% IoU on the 90-chip hand-labelled test split vs 21.8% for per-chip Otsu; 1.63 s per 512×512 tile on a CPU (ONNX).
- Fire: LightGBM on an empirical-Bayes baseline, 11,616,131 FIRMS detections (Canada 7,461,416 + Argentina 4,154,715). Trained 2012–20, tuned 2021, tested 2022–25: RMSE 0.2844 vs 0.3109 (8.5% lower); 88.6% conformal coverage (target 90%). Honest miss: monthly totals 39.4% vs 16.7%.
- Field Shift: next-season crop 0.8176 accuracy and 0.5012 macro-F1 on 66,666 held-out pixels (Markov-2 baseline: 0.8136 / 0.4633).
- Trends: Mann-Kendall + Sen's slope with Hamed-Rao checks. Valencia's wettest-day rain shows no trend (p = 0.28), so we don't claim one.
- Everything is one seed and not a published benchmark.


## 8 · What if? (illustrative estimates from submission/IMPACT.md)
- Flood headline: "12 hours earlier = an alert before the first death. Published warning curves put about €1.1 bn of Valencia's €4.8 bn insured loss within reach." 22% × €4.8 bn = €1.06 bn. Curve: 13% at 6 h, 22% at 12 h, 30% at 24 h, ~33% at 48 h. It does not stack per day.
- The gap on 29 Oct was turning the 07:36 warning into a local alert, not detecting the rain. "Days earlier" is about the map: the rain signal came about 2 days before the first post-storm radar pass (31 Oct) and about 4 days before the Copernicus province-wide map (2 Nov). No lives number for Valencia.
- Fire headline: staffing on 15 April instead of 1 May = 16 more days of readiness; each escape prevented spares about 65,000 ha (1,088 × 3% ≈ 33 escapes carrying 97% of 2.2 M ha). Readiness across the season, not the outcome of the 2016 fire.
- Farms headline: in a 2012-type drought, rye on the 92 steepest squares is worth about $1.2 M net ((11.1 bu × $6.89 − $32.09) × 26,500 acres). Frame it as drought insurance.
- Always say "illustrative estimate". Sources: IMPACT.md [F1]–[F16], [W1]–[W9], [A1]–[A7].

## 9 · Human value, team, close
- Human value, before → after, for three people. Each claim is tied to a real number on the slide.
- Team GeoAI Toronto, Parsa Riahi (solo), Toronto.

## 10 · Demos
- Flood demo first: the radar map with teams placed, "Alert everyone (simulated)" sent to all 8 towns, and the task queue running to Done. Live links open each app in its demo state.
