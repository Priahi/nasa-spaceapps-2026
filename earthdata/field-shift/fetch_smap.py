"""SMAP L3 enhanced 9 km radiometer soil moisture (SPL3SMP_E v006, NSIDC DAAC) subsets over central Iowa via
Earthdata Cloud OPeNDAP (Earthdata login from ~/.netrc). May-Sep, 2015-2025. EASE-Grid 2.0 rows 247-278, cols 910-942."""
import json, subprocess, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
R = Path(__file__).resolve().parent / "raw" / "smap"
CC = "C2938664763-NSIDC_CPRD"; RS = "[247:278][910:942]"
def granules():
    out = []
    for y in range(2015, 2026):
        u = (f"https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id={CC}"
             f"&temporal={y}-05-01T00:00:00Z,{y}-09-30T23:59:59Z&page_size=2000")
        for e in json.load(urllib.request.urlopen(u))["feed"]["entry"]:
            out.append(e["title"])
    return out
def ce():
    v = []
    for g in ("AM", "PM"):
        s = "" if g == "AM" else "_pm"
        for n in ("soil_moisture", "retrieval_qual_flag"):
            v.append(f"/Soil_Moisture_Retrieval_Data_{g}/{n}{s}{RS}")
    v += ["/Soil_Moisture_Retrieval_Data_AM/latitude" + RS, "/Soil_Moisture_Retrieval_Data_AM/longitude" + RS]
    return ";".join(v)
def get(t):
    f = R / (t.replace(".h5", ".nc4"))
    if f.exists() and f.stat().st_size > 1000: return "cached"
    u = f"https://opendap.earthdata.nasa.gov/collections/{CC}/granules/{t}.dap.nc4?dap4.ce=" + urllib.parse.quote(ce(), safe="/;:_")
    for _ in range(4):
        r = subprocess.run(["curl", "-sS", "-L", "-n", "-c", str(Path.home()/".urs_cookies"), "-b", str(Path.home()/".urs_cookies"),
                            "--max-time", "120", "-o", str(f) + ".tmp", "-w", "%{http_code}", u], capture_output=True, text=True)
        if r.stdout.strip() == "200": Path(str(f) + ".tmp").rename(f); return "ok"
    return "fail " + r.stdout.strip()
if __name__ == "__main__":
    import sys, urllib.parse
    gs = granules(); print(len(gs), "granules", flush=True)
    if len(sys.argv) > 1: gs = gs[: int(sys.argv[1])]
    with ThreadPoolExecutor(16) as ex:
        res = list(ex.map(get, gs))
    from collections import Counter; print(Counter(r.split()[0] for r in res)); print([r for r in res if r.startswith("fail")][:5])
