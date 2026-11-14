# Speaker notes: Orbit to Ground story deck (8 slides; the official demo is the 30 s video)

The spine and wording rules are in `submission/STORY.md`. "Elena" is an **illustrative composite**: say so out loud once, on slide 2.

## 1 · Hook: 29 October 2024
"On the 29th of October 2024, one town near Valencia got 771.8 millimetres of rain in a single day, a Spanish record for one hour. The alert reached people's phones at 8:11 that evening. By then, at least 156 people had died."
- Sources: AEMET event study (Turís 771.8 mm / 24 h, 184.6 mm / 1 h); El País, 26 Oct 2025 (at least 156 of 229 died before the 20:11 alert).
- The map on the right is our own radar flood map (NASA/JPL OPERA DSWx-S1, 31 Oct), with the dashboard simulation running.

## 2 · The night as it happened
"Meet Elena. She's a composite, an emergency coordinator in Catarroja, one of the towns that flooded."
- 07:36: AEMET red warning (Newtral; EchoGéo; El País gives 07:35).
- 15:00–20:00: 616.8 mm at Turís (AEMET). It was cloudy all day, so optical satellites couldn't see the ground.
- 18:43: the Poyo ravine hits 1,686 m³/s, then 2,282 m³/s at 18:55, before the gauge was destroyed (Reuters; La Vanguardia).
- 20:11: the first ES-Alert to the whole province, "avoid any travel" (Newtral; El País; EchoGéo). More than 15,943 calls had reached 112 by then (El País).
- 12 h 35 min passed between 07:36 and 20:11. Deaths: 229 in the Valencia region (El País); EchoGéo counts 236 nationwide, with 25 in Catarroja.
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

## 4 · Under the hood
- Radar water U-Net trained on Sen1Floods11: 66.4% IoU on the 90-chip hand-labelled test split vs 21.8% for per-chip Otsu; 1.63 s per 512×512 tile on a CPU (ONNX).
- Fire: LightGBM on an empirical-Bayes baseline, 11,616,131 FIRMS detections (Canada 7,461,416 + Argentina 4,154,715). Trained 2012–20, tuned 2021, tested 2022–25: RMSE 0.2844 vs 0.3109 (8.5% lower); 88.6% conformal coverage (target 90%). Honest miss: monthly totals 39.4% vs 16.7%.
- Field Shift: next-season crop 0.8176 accuracy and 0.5012 macro-F1 on 66,666 held-out pixels (Markov-2 baseline: 0.8136 / 0.4633).
- Trends: Mann-Kendall + Sen's slope with Hamed-Rao checks. Valencia's wettest-day rain shows no trend (p = 0.28), so we don't claim one.
- Everything is one seed and not a published benchmark.

## 5 · Story 2: fire (chosen over Field Shift for data density: 7.46 M Canadian FIRMS detections vs 923 Iowa squares)
"Second story: a wildfire duty officer in Alberta, planning before the season."
- Detections are rising +1,503 a year in Alberta (p = 0.035) and +2,587 in B.C. (p = 0.045), 2003–2025, on the harmonized series. Tentative: the single-sensor check isn't significant.
- May is the watch month: 5 of Alberta's 16 unusual months since 2000 (2011, 2016, 2019, 2023, 2025).
- Staffing alert (simulated): stage crews before the July peak. Pre-May community notice (simulated): check evacuation plans.
- The trend line is not a forecast.

## 6 · Times twenty
"You're feeling that now. Imagine it times twenty."
- Built: Field Shift (81.8% next crop, farmer view, rye on the 92 steepest squares), Hot Spots for Argentina, the GRACE groundwater drop over eastern Spain (−0.39 cm/yr, p = 0.002), and the burn calendar for any area.
- Future (not built): landslides after rain, drought and crop stress, smoke for schools, heat for care homes. It's the same signal → map → alert → task loop.

## 7 · Impact, team, close
- Human value, before → after, for three people. Each claim is tied to a real number on the slide.
- Team GeoAI Toronto, Parsa Riahi (solo), Toronto.

## 8 · Demos
- Flood demo first: the rain signal, the radar map with dispatch running, then the alert sent (simulated). Live links open each app in its demo state.
