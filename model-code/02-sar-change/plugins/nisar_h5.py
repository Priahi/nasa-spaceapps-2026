#!/usr/bin/env python3
"""Saturday hook: extract HH/HV (or available polarizations) from a NISAR GCOV .h5 granule.

Full granules are ~1.5-7 GB and require a free Earthdata login. They are not
bundled with this local demo. After you download one (ASF DAAC / nisar.asf):

    python plugins/nisar_h5.py --h5 /path/to/NISAR_L2_PR_GCOV_....h5 --out-dir ./nisar_extracted

The script lists radar groups, writes a small JSON sidecar of attributes, and
(if h5py and a reasonable amount of RAM are available) extracts a decimated
HH/HV or RH/RV browse GeoTIFF or PNG. It does not phone home and does not
embed credentials.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def walk(g, prefix=""):
    items = []
    for k in g.keys():
        path = f"{prefix}/{k}" if prefix else k
        val = g[k]
        if hasattr(val, "keys"):
            items.extend(walk(val, path))
        else:
            shape = getattr(val, "shape", None)
            dtype = str(getattr(val, "dtype", ""))
            items.append({"path": path, "shape": list(shape) if shape is not None else None, "dtype": dtype})
    return items


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--h5", required=True, type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("nisar_extracted"))
    p.add_argument("--decimate", type=int, default=8, help="Integer decimation for the preview")
    args = p.parse_args(argv)

    if not args.h5.exists():
        print(
            f"NISAR granule not found at {args.h5}.\n"
            "Download a GCOV .h5 from ASF DAAC with your Earthdata login, then re-run.\n"
            "Staged CMR metadata and public browse PNGs are already in tiles/nisar/.",
            file=sys.stderr,
        )
        return 2

    try:
        import h5py
    except ImportError:
        print("h5py is not installed. pip install h5py", file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with h5py.File(args.h5, "r") as f:
        inventory = walk(f)
        (args.out_dir / "h5_inventory.json").write_text(json.dumps(inventory, indent=2))
        print(f"wrote {args.out_dir / 'h5_inventory.json'}  ({len(inventory)} datasets)")
        # Heuristic: prefer arrays whose path looks like a covariance / backscatter raster
        cands = [
            it for it in inventory
            if it["shape"] and len(it["shape"]) >= 2 and it["shape"][-1] > 256 and it["shape"][-2] > 256
        ]
        print(f"{len(cands)} large 2D+ datasets (possible imagery)")
        for it in cands[:12]:
            print(f"  {it['path']}  {it['shape']}  {it['dtype']}")
        # Try to extract the first two large 2-D arrays as a preview
        previews = []
        for it in cands[:2]:
            data = f[it["path"]][()]
            step = max(1, args.decimate)
            sl = (slice(None, None, step),) * 2
            if data.ndim > 2:
                data = data[0]
            small = data[sl]
            previews.append({"path": it["path"], "array": small})
        if previews:
            import numpy as np
            from PIL import Image
            for i, rec in enumerate(previews):
                a = rec["array"].astype(np.float32)
                a = np.where(np.isfinite(a), a, np.nan)
                # if linear, convert to dB
                if np.nanmedian(a) > 0 and np.nanmedian(a) < 1.5:
                    a = 10 * np.log10(np.clip(a, 1e-7, None))
                v = a[np.isfinite(a)]
                lo, hi = np.percentile(v, 2), np.percentile(v, 98)
                u8 = np.clip((a - lo) / max(hi - lo, 1e-6) * 255, 0, 255).astype(np.uint8)
                out = args.out_dir / f"preview_{i}.png"
                Image.fromarray(u8, "L").save(out)
                print(f"wrote {out} from {rec['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
