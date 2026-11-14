# Speaker notes: Orbit to Ground (7 slides; the official demo is the 30 s video)

Times are 12-hour, local (Valencia CET, Alberta MDT). Slides and speech use rounded figures ("about 7:30 AM", "about 230 died", "more than 150 before the alert"); the exact values and sources stay in these notes. Tasking and alerts are always "simulated". Say "could have", never "would have saved". Elena is a composite. No lives number for Valencia.

## 1 · Hook: 29 October 2024
"On 29 October 2024, one town near Valencia got about 770 mm of rain in a day: roughly two and a half feet, more than one and a half times what the city of València gets in a whole year. The phone alert went out around 8 PM. By then, more than 150 people had died."
- Exact: 771.8 mm; alert 8:11 PM; at least 156 of 229 dead before it.
- Sources: AEMET event study (Turís 771.8 mm in 24 h); AEMET climate normals, València station 8416, 1981–2010: 475 mm a year; El País, 26 Oct 2025 (at least 156 of 229 died before the 8:11 PM alert).
- Units: 771.8 mm ÷ 25.4 = 30.4 in ÷ 12 = 2.53 ft ("about 2½ feet"). 771.8 ÷ 475 = 1.62 ("1.6 times a year").
- Image: our radar flood map, 31 Oct pass, 8 towns, captured from the live flood app (1600 px wide desktop view). No markers yet: slide 3 shows this same frame, classified and with actions.

## 2 · Imagine
"Imagine losing someone you love because no one knew how much rain was coming that day."
- The rain panel is our flood app's own chart (NASA GPM IMERG V07, NASA POWER cloud): 91 mm upstream on 29 Oct. The timeline on the right is our dashboard's simulated timeline (T+ clock), the same night rewound.
- "Elena is a composite, an emergency coordinator in Catarroja; 25 people died in her town."
- Slide (rounded): ~7:30 AM warning, ~noon first death, ~7 PM Poyo ravine surge, ~8 PM phone alert, "a 12-hour gap", about 230 died.
- Exact facts: 7:36 AM red warning (Newtral; El País gives 7:35 AM); 11:45 AM first recorded death (El País); 3–8 PM 616.8 mm at Turís (AEMET); 6:55 PM Poyo ravine at 2,282 m³/s (Reuters; La Vanguardia); 8:11 PM ES-Alert, at least 156 already dead (El País). 12 h 35 min from warning to alert; 229 deaths in the Valencia region.
- Units: 616.8 ÷ 475 = 1.30, "1.3 years of València's rain in one afternoon".

## 3 · Rewind with the decision tool (two stills of the slide-1 map + the official demo, which plays by itself)
"Same night, same data. The same map you just saw, now classified, then turned into actions. And here's the whole flow in 30 seconds."
- Left, ① same frame as slide 1, What changed: +47.0 km² more flood water in five days (30.7 → 77.7 km² new water, 26 → 31 Oct; 53.6 km² newly wet, 24.1 wet on both dates, 6.6 dried out). Most newly wet ground: Sueca +24.1 km², Sollana +10.6, València +6.1.
- Left, ② same frame, actions (simulated): Evacuate and flag, evacuation alert to 8 municipalities, rescue teams to Sueca and València, pull the next Sentinel-1 / OPERA pass. The 8 towns hold 75.8 km² of the new water.
- Right: the official 30-second demo. It starts by itself, muted, from the beginning when slide 3 opens and pauses when you move on; the Unmute button (or the controls) turns sound on. In the PPTX it also starts automatically.
- "Elena could have had a drafted alert for her town hours before the ~8 PM phone alert." (Slide rounds: ~90 mm, ~78 km², up from ~31, ~76 km² in 8 towns.) 91 mm upstream (IMERG), 99% cloud (POWER).

## 4 · What if? (illustrative, from submission/IMPACT.md)
- Lead with the big number: €4.8 bn insured loss (Consorcio de Compensación de Seguros), then ≈ €1.1 bn within reach of an alert 12 hours earlier. Say "illustrative estimate". The per-claim figure and the curve sit in the small "How we estimated" box.
- Headline exactly: "12 hours earlier = an alert before the first death. Published warning curves put about €1.1 bn of Valencia's €4.8 bn insured loss within reach."
- 22% × €4.8 bn = €1.06 bn. Curve: 13% at 6 h (2:11 PM), 22% at 12 h (8:11 AM), 30% at 24 h, ~33% at 48 h. It does not stack per day.
- Slide rounds the clock times (~2 PM, ~8 AM, ~noon) and claims (~250,000).
- Per claim: €4.8 bn ÷ 250,663 claims = €19,150, "about €19,000 a claim". Source: Consorcio de Compensación de Seguros, Consorseguros Digital no. 23 (250,663 claims as of 24 Nov 2025; estimated final cost about €4.8 bn).
- Water in city terms: 77.7 km² ÷ 134.65 km² = 0.577, "more than half the city of València". Source: Ajuntament de València, Recull 2024 (término municipal 13,465 ha).
- The gap was turning the 7:36 AM warning into a local alert, not detecting the rain. "Days earlier" is about the map: about 2 days before the first radar pass (31 Oct), 4 days before the Copernicus province-wide map (2 Nov).
- Comparison: AEMET (zone warning, not an instruction), EFAS (agency notices, not binding), ES-Alert (8:11 PM, "avoid any travel"), Copernicus EMS (maps from 31 Oct). Sources IMPACT.md [F1]–[F16].

## 5 · Fire vertical (demo: /hotspots/app/#demo)
- Slide shows a fixed map (left, big): Canada's burn history from the live Hot Spots map, satellite fire detections per year, 2003–2025 average, one square = 0.25° (≈ 28 km), NASA FIRMS MODIS + VIIRS on one scale. Beside it a smaller loop, three cards (~1,500 more fires detected a year, +16 days of readiness, ~65,000 ha + ~$25 M spared per escaped fire stopped), one what-if line (about the size of the City of Toronto). The "How we estimated" box is only a pointer; the full formulas are the bullets below.
"Second story: a wildfire duty officer in Alberta, planning before the season."
- Loop (recorded on the live app at 1600 px wide, my own click-through, hard cuts; ~74% of it on the burn-history layer): full Canada, dragging along the burned belt → Canada boreal → British Columbia, panning from B.C. into Alberta → back to full Canada → the burn calendar (May 2016, 2019, 2023, 2025 flagged unusual) → Assign crews (simulated). The calendar flagging May in winter is where the 16 days come from: staffing moves to 15 April.
- Note: the in-app Crews & hiring card text says "before July" (national peak); the +16 days use Alberta's own 15 April staffing date (2024 policy).
- "~1,500 more fires": Sen's slope of Alberta's yearly harmonized satellite fire detections, +1,503 a year, 2003–2025 (Mann-Kendall p = 0.035, tentative; trends/RESULTS.md). These are detections, compared year over year on the trend; the app's 2026 outlook line uses a different fit (+2,347/yr), so quote the Sen's slope. B.C. +2,587 (p = 0.045). May = 5 of Alberta's 16 unusual months.
- +16 days: 15 April instead of 1 May (Alberta Wildfire's 2024 staffing date, The Weather Network 19 Jan 2024). Horse River started 1 May 2016 → 16 days; 2023 Drayton Valley started 23 Apr → 8 days.
- Per escape (illustrative): 1,088 fires × 3% ≈ 33 escapes carrying 97% of 2.2 M ha (Stocks et al. 2002 rule on Alberta 2023) = 2.13 M ha ÷ 33 = 65,380 ha ≈ "~65,000 ha".
- Money per escape (illustrative): Alberta spent $851 M on wildfire presuppression and response in 2023–24 (Alberta Forestry and Parks Annual Report 2023–24, incl. $793 M contingency) ÷ 2.2 M ha (2,211,900 ha, Alberta Wildfire 2023 seasonal statistics) = $385–387 per ha × 65,380 ha = $25.2–25.3 M ≈ "~$25 M". Assumes cost scales with area burned (it doesn't exactly; large fires dominate costs).
- Toronto: 65,380 ha = 653.8 km² vs City of Toronto land area 631.10 km² (Statistics Canada, 2021 Census Profile) → 1.04×, "about the size of the City of Toronto".
- 2016 caveat: Horse River burned 589,552 ha, moved 88,000 people, $8.9 bn; the MNP review found initial attack was immediate, so we don't claim staffing would have stopped it. How many escapes earlier crews stop is the assumption.
- Units (Statistics Canada / Atlas of Canada): Horse River 5,896 km² vs Prince Edward Island 5,660 km² (1.04×). For Q&A: Alberta 2023 2.2 M ha = 22,000 km² ≈ 3.9 × PEI; Canada 2023 14.6 M ha = 146,000 km² ≈ 2.0 × New Brunswick.
- Comparison: FIRMS (now), CWFIS (fire weather days), fixed staffing date. Sources IMPACT.md [W1]–[W9].

## 6 · Fields vertical (demo: /field-shift/app/#demo)
- Slide shows a fixed map (left, big): Story County, Iowa, 2025 crop classification at 30 m (corn, soybean, grass/pasture, hay, small grain; USDA NASS Cropland Data Layer) from the live Field Shift map. Beside it a smaller loop, three cards (~$1.2 M net in a drought year, 26,500 acres ≈ 10,700 ha protected, before planting) and one what-if line. The "How we estimated" box is only a pointer; full formulas below.
- Loop (recorded on the live app, my own click-through): slope map → Act → "Seed winter rye on the 92 steep squares" → Show on map (the 92 squares) → Approve cover crop → task queue (winter rye seed · 92 squares, drill rye after harvest; simulated) → What if?: ~$1.2 M.
- Money: (11.1 bu × $6.89 − $32.09) = $44.39 an acre × 26,500 acres = $1.18 M net in a 2012-type drought ("~$1.2 M"); gross +$2.03 M, cost −$0.85 M. About 2.4× seed and planting cost back (SARE/CTIC 2012–13 survey, self-reported; Iowa State 2015 costs). Usually negative in a normal year without grazing or cost-share.
- Area: 92 steepest squares = about 107 km² of farmed 30 m pixels = 26,500 acres (our app_data.json); 26,500 × 0.4047 = 10,724 ha ≈ "10,700 ha".
- Lead time: our next-season map in February, field-level; USDA CDL for a season ~11 months later; Prospective Plantings 31 March, state-level.
- Accuracy (secondary, corner box): next crop 81.8% on held-out 2024–25 vs 81.4% from crop history alone, a small edge. Iowa 2012 corn −20% (USDA NASS). Frost-free season +19 days since 1981 (NASA POWER). Sources IMPACT.md [A1]–[A7].

## 7 · One system, team, close
- Shared inputs (Sentinel-1 radar, FIRMS thermal, IMERG + POWER rain, HLS/Landsat/Sentinel-2 optical + CDL, GRACE + GLDAS) → one engine (Mann-Kendall + Sen's slope trend detection; per-signal models: U-Net water, empirical-Bayes + LightGBM + conformal fire range, LightGBM next-season crop + NSGA-II) → signal, map, alert, task → outputs per vertical.
- Results on the right edge: 66.4% water IoU vs 21.8% Otsu (90 hand-labelled chips); fire 8.5% lower error (RMSE 0.2844 vs 0.3109), 88.6% range coverage (target 90%); crop 81.8% vs 81.4%, macro-F1 0.5012 vs 0.4633; trends: Iowa frost-free +0.43 d/yr (p = 0.006), E. Spain water −0.39 cm/yr (GRACE, p = 0.002), Valencia wettest day p = 0.28 (no trend, said out loud).
- Strip: built = flood, wildfire, farms, groundwater; future = drought alerts, smoke + air, infrastructure, landslides. Civil uses only.
- Close: "I'm Parsa Riahi; I built this solo, in Toronto. See it. Decide. Act."
