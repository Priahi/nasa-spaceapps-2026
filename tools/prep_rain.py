"""NASA GPM IMERG V07 daily (Final) + NASA POWER cloud amount over the Valencia (Poyo/Magro) upstream box.
Box: lon -1.0..-0.3, lat 39.2..39.6 (0.1 deg cells). Output: demos/sar-change/ops/rain.json"""
import datetime as dt, json, re, subprocess, statistics
D0, D1 = dt.date(2024, 10, 15), dt.date(2024, 11, 20)
I0, I1, J0, J1 = 1790, 1796, 1292, 1295
out = []
d = D0
while d <= D1:
    s = d.strftime("%Y%m%d")
    url = (f"https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDF.07/{d:%Y}/{d:%m}/"
           f"3B-DAY.MS.MRG.3IMERG.{s}-S000000-E235959.V07B.nc4.ascii?precipitation%5B0:0%5D%5B{I0}:{I1}%5D%5B{J0}:{J1}%5D")
    txt = subprocess.run(["curl", "-s", "-n", "-L", "-c", "/tmp/gck", "-b", "/tmp/gck", "--max-time", "60", url], capture_output=True, text=True).stdout
    vals = [float(x) for line in txt.splitlines() if line.startswith("precipitation.precipitation[") for x in line.split(",")[1:]]
    assert vals, (s, txt[:200])
    out.append({"d": d.isoformat(), "mean": round(statistics.fmean(vals), 1), "max": round(max(vals), 1)})
    print(s, out[-1]["mean"], out[-1]["max"])
    d += dt.timedelta(days=1)
import urllib.request
p = json.load(urllib.request.urlopen(f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=CLOUD_AMT&community=AG&longitude=-0.65&latitude=39.4&start={D0:%Y%m%d}&end={D1:%Y%m%d}&format=JSON"))
cl = p["properties"]["parameter"]["CLOUD_AMT"]
for r in out:
    v = cl.get(r["d"].replace("-", ""))
    r["cloud"] = None if v is None or v < 0 else round(v)
json.dump({"source": "NASA GPM IMERG V07 Final daily (0.1°), mean and wettest cell over lon -1.0 to -0.3, lat 39.2 to 39.6 (upstream of Valencia); cloud: NASA POWER CLOUD_AMT (CERES SYN1deg), daily % at 39.4N 0.65W",
           "days": out}, open("demos/sar-change/ops/rain.json", "w"), separators=(",", ":"))
