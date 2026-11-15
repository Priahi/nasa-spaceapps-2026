"""Writes ../app.json (overrides OG_APP actions + impact for the SAR dashboard; also read by page.py). Every number is computed here
from ../zones.json (OPERA DSWx-S1) or read from demos/sar-change/data/metrics.json; the p-values are the trend results already on the site
(NASA POWER wettest day p = 0.28, GPM IMERG p = 0.62). Outcomes stay qualitative."""
import json
from pathlib import Path
MOD = Path(__file__).resolve().parent.parent; ROOT = MOD.parents[2]
Z = json.loads((MOD / "zones.json").read_text()); T = Z["totals"]; zones = {z["name"]: z for z in Z["zones"]}
M = json.loads((ROOT / "demos/sar-change/data/metrics.json").read_text())
iou, otsu = M["test_water_iou"]["unet_final"], M["test_water_iou"]["otsu_per_chip"]; cpu = M["cpu_inference_s_per_512_tile"]["onnx_fp32"]["seconds"]
f1 = lambda v: f"{v:.1f}"
from decimal import Decimal, ROUND_HALF_UP
pct = lambda v: str(Decimal(str(v * 100)).quantize(Decimal("0.1"), ROUND_HALF_UP))  # 0.6635 -> 66.4, as everywhere else on the site
def tot(ns, k): return sum(zones[n][k] for n in ns)
def by(k): return sorted(zones, key=lambda n: -zones[n][k])
def lst(ns, k=3):
    if len(ns) > k: return ", ".join(ns[:k]) + f" and {len(ns) - k} more"
    return ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " and " + ns[-1]
z1 = [n for n in by("new_after_km2") if zones[n]["new_after_km2"] >= 1.0]
z2w = [n for n in by("still_km2") if zones[n]["still_km2"] >= 1.0]
z2b = [n for n in ["Paiporta", "Picanya", "Benetússer", "Sedaví", "Aldaia", "Alaquàs", "Xirivella", "Albal", "Beniparrell"] if n in zones]
z3 = [n for n in by("added_km2") if zones[n]["comarca"] in ("l'Horta Sud", "Comarca de València") and zones[n]["added_km2"] >= 0.1]
z4 = [n for n in by("new_after_km2") if (zones[n]["comarca"] == "la Ribera Baixa" or n == "València") and zones[n]["new_after_km2"] >= 1.0]
blind = tot(z2b, "new_after_km2")
actions = [
 {"id": "sar-change-1", "cls": "Evacuate & flag", "verb": "Dispatch", "layer": "after", "zones": z1, "img": "people/evacuate.webp", "user": "Civil-protection duty officer", "short": "Evacuate",
  "title": f"Clear the {len(z1)} municipalities inside the new-water footprint first: {lst(z1)}.",
  "sat": f"New water jumped from {f1(T['new_before_km2'])} to {f1(T['new_after_km2'])} km² between 26 and 31 Oct, mapped through cloud. These {len(z1)} hold {f1(tot(z1, 'new_after_km2'))} km² of it.",
  "out": "Rescue and evacuation start from a radar map on day two instead of from phone calls.",
  "src": "NASA/JPL OPERA DSWx-S1, 30 m; municipality outlines from OpenStreetMap.",
  "tasks": [{"asset": "notice", "label": f"Evacuation alert to {len(z1)} municipalities", "eta": "now"},
            {"asset": "crew", "label": f"Rescue teams to {z1[0]} and {z1[1]}", "eta": "now"},
            {"asset": "satellite", "label": "Pull the next Sentinel-1 / OPERA pass", "eta": "next pass"}]},
 {"id": "sar-change-2", "cls": "Damage teams", "verb": "Assign teams", "layer": "still", "zones": z2w, "zones_alt": z2b, "img": "people/damage.webp", "user": "Damage-assessment lead", "short": "Damage teams",
  "title": f"Send damage teams to the {len(z2w)} municipalities still wet three weeks later, and drone-survey the streets of {len(z2b)} l'Horta Sud towns where radar sees almost no water.",
  "sat": f"{f1(T['still_km2'])} km² was still new water on 19 Nov. In {', '.join(z2b[:3])} and nearby towns, radar maps only {blind:.2f} km²: water between buildings is a known radar blind spot.",
  "out": "Teams go where water lingers, and the radar's blind spot is covered by drones and on foot.",
  "src": "OPERA DSWx-S1 pass of 19 Nov 2024; urban under-detection is a documented limit of radar water maps.",
  "tasks": [{"asset": "crew", "label": f"Damage teams to {z2w[0]} and {z2w[1]}", "eta": "this week"},
            {"asset": "drone", "label": f"Drone street survey: {', '.join(z2b[:3])}", "eta": "this week"},
            {"asset": "camera", "label": "Street-camera check for standing water", "eta": "today"}]},
 {"id": "sar-change-3", "cls": "Drainage plan", "verb": "Add to plan", "layer": "delta", "zones": z3, "img": "people/engineer.webp", "user": "City drainage engineer", "short": "Drainage plan",
  "title": f"Put retention basins and drainage upgrades for {lst(z3, 4)} into next year's plan, sized for the 2024 event.",
  "sat": f"Water spread into these towns on the Albufera's edge: +{f1(tot(z3, 'added_km2'))} km² of newly wet ground. The year's wettest day shows no 45-year trend (p = 0.28), so size for the event, not for a trend.",
  "out": "The plan is built on what happened, and on what 45 years of rain data do and don't show.",
  "src": "OPERA DSWx-S1 change 26 → 31 Oct 2024; NASA POWER 1981–2025 wettest day, Mann-Kendall p = 0.28 (GPM IMERG 1998–2024 agrees, p = 0.62).",
  "tasks": [{"asset": "engineer", "label": "Retention-basin and drainage study", "eta": "this year"},
            {"asset": "plan", "label": "Line in next year's municipal plan", "eta": "next budget"},
            {"asset": "sensor", "label": "Re-check with each new OPERA flood map", "eta": "each event"}]},
 {"id": "sar-change-4", "cls": "Farm aid & insurance", "verb": "Approve aid", "layer": "after", "zones": z4, "img": "people/paddies.webp", "user": "Agriculture recovery officer", "short": "Farm aid",
  "title": f"Send farm recovery aid and crop-insurance checks to rice growers in {lst(z4, 4)}.",
  "sat": f"Most new water sits in the Albufera rice paddies: {f1(tot(z4, 'new_after_km2'))} km² in these {len(z4)} municipalities, {f1(zones[z4[0]]['new_after_km2'])} km² in {z4[0]} alone.",
  "out": "Aid reaches the farms the flood covered, with urban losses flagged as larger than radar shows.",
  "src": "OPERA DSWx-S1, 31 Oct 2024. The paddies were already filling before the storm (4 → 31 km², 1–26 Oct).",
  "tasks": [{"asset": "plan", "label": f"Crop-insurance checks: {z4[0]}, {z4[1]}", "eta": "this month"},
            {"asset": "truck", "label": "Recovery aid to paddy owners", "eta": "this month"}]},
]
impact = [
 {"user": "Emergency manager (civil protection)", "decision": "Which towns to clear first after the storm", "img": "people/flood-ops.webp",
  "before": ["Optical satellites see only cloud", "Towns ranked from calls and road reports"],
  "after": ["A water map from the first radar pass after the storm, ranked by municipality", f"{len(z1)} municipalities flagged on day two; l'Horta Sud streets checked by drone"],
  "geo": {"v": f"{f1(T['new_after_km2'])} km²", "l": f"new water on 31 Oct, up from {f1(T['new_before_km2'])} km² on 26 Oct (NASA OPERA)"},
  "metric": {"v": f"{pct(iou)}%", "l": f"water IoU of our radar model vs {pct(otsu)}% for the Otsu threshold (Sen1Floods11 test, 90 chips)"}},
 {"user": "City drainage engineer", "decision": "What to build before the next storm", "img": "people/engineer.webp",
  "before": ["Upgrades sized for an assumed rising trend in extreme rain", "No map of where the water actually spread"],
  "after": [f"Basins and drains planned for {lst(z3, 4)}", "Sized for the 2024 event; the 45-year record shows no trend in the wettest day"],
  "geo": {"v": f"+{f1(tot(z3, 'added_km2'))} km²", "l": "newly wet ground in those towns, 26 → 31 Oct"},
  "metric": {"v": f"{cpu:.2f} s", "l": "per 512 × 512 tile on a CPU (ONNX), so a fresh map takes minutes, not days"}},
]
kpi = {"before": T["new_before_km2"], "after": T["new_after_km2"], "net": round(T["new_after_km2"] - T["new_before_km2"], 2), "added": T["added_km2"],
       "gone": T["gone_km2"], "kept": T["kept_km2"], "still": T["still_km2"], "iou": iou, "otsu": otsu, "cpu_s": cpu, "blind_km2": round(blind, 2), "n_blind": len(z2b)}
(MOD / "app.json").write_text(json.dumps({"actions": actions, "impact": impact, "kpi": kpi}, ensure_ascii=False, indent=1))
for a in actions: print(a["cls"], "|", a["title"], "|", a["sat"])
print(kpi)
