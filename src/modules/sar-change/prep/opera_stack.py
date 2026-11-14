"""Shared loader: OPERA DSWx-S1 B01_WTR mosaics on the same grid as upgrades/opera_valencia.py (cached to npz)."""
import glob, re, numpy as np
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
W, S, E, N = -0.75, 39.20, -0.20, 39.55; RES = 0.0003
nx, ny = int(round((E - W) / RES)), int(round((N - S) / RES))
PX_KM2 = (RES * 111.32 * np.cos(np.deg2rad((S + N) / 2))) * (RES * 110.57)
CACHE = Path.home() / ".cache/opera_stack.npz"
def load():
    if CACHE.exists():
        z = np.load(CACHE, allow_pickle=True); return list(z["dates"]), z["A"]
    import rasterio
    from rasterio.warp import reproject, Resampling
    from rasterio.transform import from_bounds
    dst_t = from_bounds(W, S, E, N, nx, ny)
    groups = defaultdict(list)
    for f in sorted(glob.glob(str(ROOT / "upgrades/opera/*_B01_WTR.tif"))):
        m = re.search(r"DSWx-S1_(T\w+?)_(\d{8}T\d{6})Z_(\d{8}T\d{6})Z", f); groups[m.group(2)].append((m.group(3), m.group(1), f))
    dates, stacks = [], []
    for acq in sorted(groups):
        by_tile = {}
        for prod, tile, f in sorted(groups[acq]): by_tile[tile] = f
        mos = np.full((ny, nx), 255, np.uint8)
        for f in by_tile.values():
            with rasterio.open(f) as src:
                tmp = np.full((ny, nx), 255, np.uint8)
                reproject(rasterio.band(src, 1), tmp, dst_transform=dst_t, dst_crs="EPSG:4326", resampling=Resampling.nearest, src_nodata=255, dst_nodata=255)
            sel = (mos == 255) & (tmp != 255); mos[sel] = tmp[sel]
        dates.append(acq); stacks.append(mos)
    A = np.stack(stacks); CACHE.parent.mkdir(parents=True, exist_ok=True); np.savez_compressed(CACHE, dates=np.array(dates), A=A); return dates, A
