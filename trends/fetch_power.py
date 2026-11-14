"""Fetch NASA POWER daily regional data (0.5 deg grid, MERRA-2 based) one parameter-year per request (API limits).
No login. Cached to raw/power/<region>_<param>_<year>.json."""
import json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
OUT = Path(__file__).parent / "raw/power"
REGIONS = {
    "valencia": (-2.0, 1.0, 38.0, 41.0),   # eastern Spain incl. Valencia (SAR Change AOI)
    "ontario":  (-81.0, -78.0, 43.0, 46.0),  # southern Ontario incl. Toronto (NISAR AOI in SAR Change)
    "iowa":     (-95.0, -92.0, 41.0, 44.0),  # central Iowa incl. Story County (Field Shift AOI)
}
JOBS = [("valencia", "PRECTOTCORR"), ("ontario", "PRECTOTCORR"), ("iowa", "PRECTOTCORR"),
        ("iowa", "T2M_MIN"), ("iowa", "T2M_MAX"), ("iowa", "GWETROOT")]
YEARS = range(1981, 2026)
def get(job):
    reg, par, yr = job
    f = OUT / f"{reg}_{par}_{yr}.json"
    if f.exists() and f.stat().st_size > 1000: return "cached"
    w, e, s, n = REGIONS[reg]
    u = (f"https://power.larc.nasa.gov/api/temporal/daily/regional?parameters={par}&community=AG&longitude-min={w}&longitude-max={e}"
         f"&latitude-min={s}&latitude-max={n}&start={yr}0101&end={yr}1231&format=json")
    for t in range(5):
        try:
            with urllib.request.urlopen(u, timeout=300) as r: data = r.read()
            json.loads(data)["features"]; f.write_bytes(data); return "ok"
        except Exception as ex:
            time.sleep(5 * (t + 1)); err = ex
    return f"FAIL {job} {err}"
jobs = [(r, p, y) for r, p in JOBS for y in YEARS]
with ThreadPoolExecutor(4) as ex:
    for i, res in enumerate(ex.map(get, jobs)):
        if res.startswith("FAIL") or i % 20 == 0: print(i, res, flush=True)
print("done", len(list(OUT.glob("*.json"))))
