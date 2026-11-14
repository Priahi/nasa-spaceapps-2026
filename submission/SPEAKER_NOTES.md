# Speaker notes: Orbit to Ground (7 slides; the official demo is the 30 s video)

Times are 12-hour, local (Valencia CET, Alberta MDT). Slides and speech use rounded figures ("about 7:30 AM", "about 230 died", "more than 150 before the alert"); the exact values and sources stay in these notes. Tasking and alerts are always "simulated". Say "could have", never "would have saved". Elena is a composite. No lives number for Valencia.

## 1 · Hook: 29 October 2024
"On 29 October 2024, one town near Valencia got about 770 mm of rain in a day: roughly two and a half feet, more than one and a half times what the city of València gets in a whole year. The phone alert went out around 8 PM. By then, more than 150 people had died."
- Exact: 771.8 mm; alert 8:11 PM; at least 156 of 229 dead before it.
- Sources: AEMET event study (Turís 771.8 mm in 24 h); AEMET climate normals, València station 8416, 1981–2010: 475 mm a year; El País, 26 Oct 2025 (at least 156 of 229 died before the 8:11 PM alert).
- Units: 771.8 mm ÷ 25.4 = 30.4 in ÷ 12 = 2.53 ft ("about 2½ feet"). 771.8 ÷ 475 = 1.62 ("1.6 times a year").
- Image: our radar flood map, 31 Oct pass, 8 towns, teams placed (simulated).

## 2 · Imagine
"Imagine losing someone you love because no one knew how much rain was coming that day."
- The rain panel is our flood app's own chart (NASA GPM IMERG V07, NASA POWER cloud): 91 mm upstream on 29 Oct. The timeline on the right is our dashboard's simulated timeline (T+ clock), the same night rewound.
- "Elena is a composite, an emergency coordinator in Catarroja; 25 people died in her town."
- Slide (rounded): ~7:30 AM warning, ~noon first death, ~7 PM Poyo ravine surge, ~8 PM phone alert, "a 12-hour gap", about 230 died.
- Exact facts: 7:36 AM red warning (Newtral; El País gives 7:35 AM); 11:45 AM first recorded death (El País); 3–8 PM 616.8 mm at Turís (AEMET); 6:55 PM Poyo ravine at 2,282 m³/s (Reuters; La Vanguardia); 8:11 PM ES-Alert, at least 156 already dead (El País). 12 h 35 min from warning to alert; 229 deaths in the Valencia region.
- Units: 616.8 ÷ 475 = 1.30, "1.3 years of València's rain in one afternoon".

## 3 · Rewind with the decision tool (four walkthrough loops + the official demo video, playable on the slide)
"Same night, same data. Rain signal, radar map, one alert to all 8 towns, teams and passes queued."
- 91 mm upstream (IMERG), 99% cloud (POWER). Radar 31 Oct: 77.7 km² new water outside normal water bodies (vs 30.7 km² on 26 Oct); 8 towns hold 75.8 km².
- The four frames are click-through loops of the live app: (1) radar before/after slider and water classified, (2) recommended actions, (3) teams and passes queued, (4) one alert to all 8 towns (simulated). The right column plays the official demo video (press play).
- "Elena could have had a drafted alert for her town hours before the ~8 PM phone alert." (Slide rounds: ~90 mm, ~78 km², up from ~31, ~76 km² in 8 towns.)

## 4 · What if? (illustrative, from submission/IMPACT.md)
- Headline exactly: "12 hours earlier = an alert before the first death. Published warning curves put about €1.1 bn of Valencia's €4.8 bn insured loss within reach."
- 22% × €4.8 bn = €1.06 bn. Curve: 13% at 6 h (2:11 PM), 22% at 12 h (8:11 AM), 30% at 24 h, ~33% at 48 h. It does not stack per day.
- Slide rounds the clock times (~2 PM, ~8 AM, ~noon) and claims (~250,000).
- Per claim: €4.8 bn ÷ 250,663 claims = €19,150, "about €19,000 a claim". Source: Consorcio de Compensación de Seguros, Consorseguros Digital no. 23 (250,663 claims as of 24 Nov 2025; estimated final cost about €4.8 bn).
- Water in city terms: 77.7 km² ÷ 134.65 km² = 0.577, "more than half the city of València". Source: Ajuntament de València, Recull 2024 (término municipal 13,465 ha).
- The gap was turning the 7:36 AM warning into a local alert, not detecting the rain. "Days earlier" is about the map: about 2 days before the first radar pass (31 Oct), 4 days before the Copernicus province-wide map (2 Nov).
- Comparison: AEMET (zone warning, not an instruction), EFAS (agency notices, not binding), ES-Alert (8:11 PM, "avoid any travel"), Copernicus EMS (maps from 31 Oct). Sources IMPACT.md [F1]–[F16].

## 5 · Fire vertical (demo: /hotspots/app/#demo)
"Second story: a wildfire duty officer in Alberta, planning before the season."
- Map: all of Canada, fires per year (2003–2025 average, 0.25° squares), cropped to the fire extent (B.C. to Quebec, south of 62°N). 11.6 M detections.
- Loop: Alberta + B.C. with crews, hiring and camera tasks placed; queue moving (simulated).
- Slide rounds: nearly 12 M detections, ~1,500 and ~2,600 more a year, ~1,100 fires, ~5,900 km².
- Trend: Alberta +1,503 detections a year (p = 0.035); B.C. +2,587 (p = 0.045). May = 5 of Alberta's 16 unusual months.
- What if (headline exactly): staffing on 15 April instead of 1 May = 16 more days of readiness; 1,088 × 3% ≈ 33 escapes carrying 97% of 2.2 M ha ≈ 65,000 ha each. 2023 Drayton Valley started 23 Apr (8 days).
- 2016 caveat: Horse River started 1 May, burned 589,552 ha, moved 88,000 people, $8.9 bn; the MNP review found initial attack was immediate, so we don't claim staffing would have stopped it. Readiness across the season.
- Units (Statistics Canada / Atlas of Canada, land and freshwater area by province): Horse River 589,552 ha = 5,896 km² vs Prince Edward Island 5,660 km² → "more than all of PEI" (1.04×). For Q&A: Alberta 2023 2.2 M ha = 22,000 km² ≈ 3.9 × PEI, or 30% of New Brunswick (72,908 km²); Canada 2023 14.6 M ha (if asked) = 146,000 km² ≈ 2.0 × New Brunswick.
- Comparison: FIRMS (now), CWFIS (fire weather days), fixed staffing date. Sources IMPACT.md [W1]–[W9].

## 6 · Fields vertical (demo: /field-shift/app/#demo)
- Lead with the lead time: the next-season map is ready in February, before planting; the USDA CDL for a season arrives about 11 months later. Then the drought-insurance figure, about $1.2 M.
- Accuracy, said honestly as a secondary point: ~82% vs ~81% from crop history alone is a small edge; the value is timing plus the attached climate trend.
- Crop map: Story County, Iowa, every 30 m pixel (USDA NASS CDL in our app). Next-season crop 81.8% correct on held-out 2024–25 (crop history alone 81.4%).
- Tasking: drone survey and scouts on 114 squares, queue moving (simulated).
- Slide rounds: ~82% vs ~81%; (~11 bu × ~$6.90 − ~$32) ≈ $44/acre × ~26,500 acres ≈ $1.2 M.
- What if (headline exactly): "In a 2012-type drought, rye on the 92 steepest squares is worth about $1.2 M net." (11.1 bu × $6.89 − $32.09) = $44.39/acre × 26,500 acres = $1.18 M. Drought insurance: small cost most years, about 2.4× its cost back in 2012 (SARE/CTIC survey). Iowa 2012 corn −20% (USDA NASS).
- Lead time: USDA CDL for a season arrives about 11 months later; Prospective Plantings 31 March, state-level; our map in February, field-level. Sources IMPACT.md [A1]–[A7].

## 7 · One system, team, close
- Shared inputs (Sentinel-1 radar, FIRMS thermal, IMERG + POWER rain, HLS/Landsat/Sentinel-2 optical + CDL, GRACE + GLDAS) → one engine (Mann-Kendall + Sen's slope trend detection; per-signal models: U-Net water, empirical-Bayes + LightGBM + conformal fire range, LightGBM next-season crop + NSGA-II) → signal, map, alert, task → outputs per vertical.
- Results on the right edge: 66.4% water IoU vs 21.8% Otsu (90 hand-labelled chips); fire 8.5% lower error (RMSE 0.2844 vs 0.3109), 88.6% range coverage (target 90%); crop 81.8% vs 81.4%, macro-F1 0.5012 vs 0.4633; trends: Iowa frost-free +0.43 d/yr (p = 0.006), E. Spain water −0.39 cm/yr (GRACE, p = 0.002), Valencia wettest day p = 0.28 (no trend, said out loud).
- Strip: built = flood, wildfire, farms, groundwater; future = drought alerts, smoke + air, infrastructure, landslides. Civil uses only.
- Close: "I'm Parsa Riahi; I built this solo, in Toronto. See it. Decide. Act."
