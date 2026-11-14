"""Crop the dashboard's Sentinel-1 RTC tiles to the largest no-data-free rectangle of each descending orbit's swipe pair
(removes the black wedges outside the swath; the ascending orbits have none). Idempotent via 'crop_px' in the manifest.
Also makes the fully valid ascending 17:55 pair (26 Oct, same day as the OPERA 'before' look) the default swipe pair."""
import json, numpy as np
from PIL import Image
from pathlib import Path
D = Path(__file__).resolve().parents[4] / "demos/sar-change"
man = json.loads((D / "data/manifest.json").read_text())
def max_rect(M):
    h, w = M.shape; hist = np.zeros(w, int); best = (0, 0, 0, 0, 0)
    for r in range(h):
        hist = np.where(M[r], hist + 1, 0); st = []
        for c in range(w + 1):
            hh = hist[c] if c < w else 0; s = c
            while st and st[-1][1] >= hh:
                s, sh = st.pop(); a = sh * (c - s)
                if a > best[0]: best = (a, r - sh + 1, s, r + 1, c)
            st.append((s, hh))
    return best[1:]
def valid(f): return np.asarray(Image.open(D / f).convert("RGB")).max(2) > 0
pairs = {p["orbit"]: p for p in man["valencia"]["swipe_pairs"]}
for o in man["valencia"]["orbits"]:
    if o.get("crop_px"): print("skip", o["id"]); continue
    if o["id"].startswith("asc"): o["crop_px"] = [0, 0, 0, 0]; print("no wedge", o["id"]); continue
    dd = {d["id"]: d for d in o["dates"]}; p = pairs.get(o["id"])
    keys = [p["pre"], p["post"]] if p else [o["dates"][len(o["dates"]) // 2]["id"]]
    M = np.logical_and.reduce([valid(dd[k]["files"]["fcc"]) for k in keys])
    k = 8; Ms = M[: M.shape[0] // k * k, : M.shape[1] // k * k].reshape(M.shape[0] // k, k, M.shape[1] // k, k).mean((1, 3)) > 0.5  # dark-water specks count as valid
    r0, c0, r1, c1 = [int(v) * k for v in max_rect(Ms)]; r0 += 2; c0 += 2; r1 -= 2; c1 -= 2
    print(o["id"], M.shape, "->", (r0, c0, r1, c1), f"{(r1-r0)*(c1-c0)/M.size:.0%} kept")
    files = [f for d in o["dates"] for f in d["files"].values()] + [v for c in (o.get("change") or {}).values() for kk, v in c.items() if kk in ("gray", "color")]
    for f in files: Image.open(D / f).crop((c0, r0, c1, r1)).save(D / f, optimize=True)
    x0, y0, x1, y1 = o["bounds"]; W0, H0 = M.shape[1], M.shape[0]; sx, sy = (x1 - x0) / W0, (y1 - y0) / H0
    nb = [x0 + c0 * sx, y1 - r1 * sy, x0 + c1 * sx, y1 - r0 * sy]; o["bounds"] = nb; o["crop_px"] = [c0, r0, c1, r1]
    for d in o["dates"]: d["width"], d["height"], d["bounds"] = c1 - c0, r1 - r0, nb
man["valencia"]["swipe_pairs"].sort(key=lambda p: p["orbit"] != "asc_1755")
(D / "data/manifest.json").write_text(json.dumps(man, indent=2))
