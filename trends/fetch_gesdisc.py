"""Fetch GPM IMERG V07 monthly precipitation and GLDAS Noah 2.1 monthly soil moisture as small OPeNDAP subsets
from NASA GES DISC through Earthdata Cloud OPeNDAP (Earthdata login via ~/.netrc). The on-prem GES DISC OPeNDAP
servers (gpm1/hydro1) returned 410 Service Retired on 14 Nov 2026. Needs the 'NASA GESDISC DATA ARCHIVE' app approved on the
Earthdata profile. Output: raw/gesdisc/<product>/<region>/<YYYYMM>.nc4 (cached)."""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
R = Path(__file__).resolve().parent / "raw" / "gesdisc"
BOX = {"valencia": (-2.0, 1.0, 38.0, 41.0), "ontario": (-81.0, -78.0, 43.0, 46.0), "iowa": (-95.0, -92.0, 41.0, 44.0)}
def imerg_idx(b):  # precipitation[time][lon][lat], 0.1 deg, centres -179.95.., -89.95..
    w, e, s, n = b
    return (int(round((w + 180) / 0.1)), int(round((e + 180) / 0.1)) - 1, int(round((s + 90) / 0.1)), int(round((n + 90) / 0.1)) - 1)
def gldas_idx(b):  # var[time][lat][lon], 0.25 deg, lon centres -179.875.., lat centres -59.875..
    w, e, s, n = b
    return (int(round((w + 180) / 0.25)), int(round((e + 180) / 0.25)) - 1, int(round((s + 60) / 0.25)), int(round((n + 60) / 0.25)) - 1)
def jobs():
    for reg in ("valencia", "ontario", "iowa"):
        x0, x1, y0, y1 = imerg_idx(BOX[reg])
        for y in range(1998, 2026):
            for m in range(1, 13):
                u = (f"https://opendap.earthdata.nasa.gov/collections/C2723754851-GES_DISC/granules/GPM_3IMERGM.07%3A3B-MO.MS.MRG.3IMERG.{y}{m:02d}01-S000000-E235959.{m:02d}.V07B.HDF5.dap.nc4"
                     f"?dap4.ce=/Grid/precipitation[0:0][{x0}:{x1}][{y0}:{y1}];/Grid/lon[{x0}:{x1}];/Grid/lat[{y0}:{y1}]")
                yield R / "imerg" / reg / f"{y}{m:02d}.nc4", u
    x0, x1, y0, y1 = gldas_idx(BOX["iowa"])
    for y in range(2000, 2026):
        for m in range(1, 13):
            sl = f"[0:0][{y0}:{y1}][{x0}:{x1}]"
            u = (f"https://opendap.earthdata.nasa.gov/collections/C1342986036-GES_DISC/granules/GLDAS_NOAH025_M.2.1%3AGLDAS_NOAH025_M.A{y}{m:02d}.021.nc4.dap.nc4"
                 f"?dap4.ce=/SoilMoi0_10cm_inst{sl};/SoilMoi10_40cm_inst{sl};/SoilMoi40_100cm_inst{sl};/RootMoist_inst{sl};/lat[{y0}:{y1}];/lon[{x0}:{x1}]")
            yield R / "gldas" / "iowa" / f"{y}{m:02d}.nc4", u
def get(job):
    out, url = job
    import urllib.parse
    b, ce = url.split("?dap4.ce=")
    url = b + "?dap4.ce=" + urllib.parse.quote(ce, safe="/;:_")
    if out.exists() and out.stat().st_size > 500: return "cached"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".part")
    r = subprocess.run(["curl", "-g", "-sS", "-L", "-n", "-c", str(Path.home() / ".urs_cookies"), "-b", str(Path.home() / ".urs_cookies"),
                        "--retry", "4", "--max-time", "180", "-o", str(tmp), "-w", "%{http_code}", url], capture_output=True, text=True)
    if r.stdout.strip() == "200" and tmp.stat().st_size > 500 and tmp.read_bytes()[:4] == b"\x89HDF": tmp.rename(out); return "ok"
    return f"fail {r.stdout.strip()} {out.name}"
if __name__ == "__main__":
    J = list(jobs())
    if "--test" in sys.argv: J = J[:1] + [j for j in J if "gldas" in str(j[0])][:1]
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(get, J))
    from collections import Counter; print(Counter(r.split()[0] for r in res)); print([r for r in res if r.startswith("fail")][:5])
