#!/usr/bin/env python3
"""Pre-render real Sentinel-1 RTC and Sen1Floods11 chips to web PNGs.

Never fabricates imagery. All pixels come from staged GeoTIFFs / NISAR browse PNGs.
"""
from __future__ import annotations

import csv
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image

ROOT = Path("/workspace/nasa-spaceapps")
SRC = ROOT / "data/dancing-with-the-sars"
APP = ROOT / "apps/02-sar-change"
TILES = APP / "tiles"
DATA = APP / "data"
MAX_EDGE = 1024
DANA = "2024-10-29"

ORBIT_META = {
    "des_0610": {
        "label": "Descending 06:10 UTC (track 0610, UTM 30N)",
        "pass": "descending",
        "time": "06:10",
    },
    "asc_1755": {
        "label": "Ascending 17:55 UTC (track 1755, UTM 31N)",
        "pass": "ascending",
        "time": "17:55",
    },
    "asc_1803": {
        "label": "Ascending 18:03 UTC (track 1803, UTM 30N)",
        "pass": "ascending",
        "time": "18:03",
    },
    "des_0602": {
        "label": "Descending 06:02 UTC (track 0602, UTM 31N)",
        "pass": "descending",
        "time": "06:02",
    },
}

# Primary same-orbit pairs around the 29 Oct 2024 DANA flood.
SWIPE_PAIRS = [
    {
        "id": "des0602_oct20_nov01",
        "orbit": "des_0602",
        "pre": "20241020T0602",
        "post": "20241101T0602",
        "title": "Descending 06:02: 20 Oct (9 days before) vs 1 Nov (3 days after)",
        "note": "Same orbit, same grid. Closest same-track pair bracketing the 29 Oct 2024 DANA flood.",
    },
    {
        "id": "asc1755_oct26_nov07",
        "orbit": "asc_1755",
        "pre": "20241026T1755",
        "post": "20241107T1755",
        "title": "Ascending 17:55: 26 Oct (3 days before) vs 7 Nov (9 days after)",
        "note": "Same orbit, same grid. Pre-event scene is the last acquisition before the flood.",
    },
    {
        "id": "des0610_oct25_nov06",
        "orbit": "des_0610",
        "pre": "20241025T0610",
        "post": "20241106T0610",
        "title": "Descending 06:10: 25 Oct (4 days before) vs 6 Nov (8 days after)",
        "note": "Same orbit, same grid.",
    },
]


def to_db(lin: np.ndarray) -> np.ndarray:
    return (10.0 * np.log10(np.clip(lin, 1e-7, None))).astype(np.float32)


def downsample(arr: np.ndarray, max_edge: int = MAX_EDGE) -> np.ndarray:
    h, w = arr.shape[-2:]
    scale = max(h, w) / max_edge
    if scale <= 1:
        return arr
    nh, nw = int(round(h / scale)), int(round(w / scale))
    # rasterio-free bilinear via PIL for 2D; keep nodata as nan
    def _one(a):
        finite = np.isfinite(a)
        fill = np.nanmedian(a[finite]) if finite.any() else 0.0
        tmp = np.where(finite, a, fill)
        im = Image.fromarray(tmp.astype(np.float32), mode="F").resize((nw, nh), Image.BILINEAR)
        out = np.array(im, dtype=np.float32)
        mask = np.array(
            Image.fromarray((finite.astype(np.uint8) * 255), mode="L").resize((nw, nh), Image.NEAREST)
        )
        out[mask == 0] = np.nan
        return out

    if arr.ndim == 2:
        return _one(arr)
    return np.stack([_one(arr[i]) for i in range(arr.shape[0])])


def stretch(a: np.ndarray, lo: float, hi: float) -> np.ndarray:
    out = (a - lo) / max(hi - lo, 1e-6)
    return np.clip(out, 0, 1)


def pctl_finite(a: np.ndarray, q: float) -> float:
    v = a[np.isfinite(a)]
    if v.size == 0:
        return 0.0
    return float(np.percentile(v, q))


def gray_png(a01: np.ndarray, path: Path, mask: np.ndarray | None = None) -> None:
    u8 = np.clip(a01 * 255, 0, 255).astype(np.uint8)
    if mask is None:
        Image.fromarray(u8, mode="L").save(path, optimize=True)
    else:
        rgba = np.stack([u8, u8, u8, np.where(mask, 255, 0).astype(np.uint8)], axis=-1)
        Image.fromarray(rgba, mode="RGBA").save(path, optimize=True)


def rgb_png(r: np.ndarray, g: np.ndarray, b: np.ndarray, path: Path, mask: np.ndarray | None = None) -> None:
    rgb = np.stack(
        [
            np.clip(r * 255, 0, 255).astype(np.uint8),
            np.clip(g * 255, 0, 255).astype(np.uint8),
            np.clip(b * 255, 0, 255).astype(np.uint8),
        ],
        axis=-1,
    )
    if mask is None:
        Image.fromarray(rgb, mode="RGB").save(path, optimize=True)
    else:
        rgba = np.concatenate([rgb, np.where(mask, 255, 0).astype(np.uint8)[..., None]], axis=-1)
        Image.fromarray(rgba, mode="RGBA").save(path, optimize=True)


def orbit_key(stem: str) -> str:
    # 20241020T0602_des__rtc
    date, passing, *_ = stem.split("_")
    tod = date.split("T")[1]
    return f"{passing}_{tod}"


def load_scene(path: Path) -> dict:
    with rasterio.open(path) as src:
        vv = src.read(1).astype(np.float32)
        vh = src.read(2).astype(np.float32)
        # linear power; 0 or non-finite is nodata
        nodata = (~np.isfinite(vv)) | (~np.isfinite(vh)) | (vv <= 0) | (vh <= 0)
        vv[nodata] = np.nan
        vh[nodata] = np.nan
        meta = {
            "crs": str(src.crs),
            "bounds": [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top],
            "width": src.width,
            "height": src.height,
            "transform": list(src.transform),
        }
    vv_db = to_db(vv)
    vh_db = to_db(vh)
    ratio_db = vv_db - vh_db  # dB difference == linear ratio
    vv_s = downsample(vv_db)
    vh_s = downsample(vh_db)
    ratio_s = downsample(ratio_db)
    return {"vv": vv_s, "vh": vh_s, "ratio": ratio_s, "meta": meta, "native": (src_shape := (meta["height"], meta["width"]))}


def render_valencia() -> dict:
    src_dir = SRC / "s1_rtc_valencia"
    prov = json.loads((src_dir / "provenance.json").read_text())
    prov_by_file = {Path(p["file"]).name: p for p in prov}

    groups: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(src_dir.glob("*_rtc.tif")):
        groups[orbit_key(path.stem)].append(path)

    out_root = TILES / "valencia"
    out_root.mkdir(parents=True, exist_ok=True)
    manifest_orbits = []

    for oid, paths in groups.items():
        print(f"[valencia] orbit {oid} n={len(paths)}", flush=True)
        scenes = []
        # first pass: downsample + collect percentiles
        loaded = []
        for path in paths:
            rec = load_scene(path)
            rec["path"] = path
            rec["date"] = path.stem.split("_")[0]  # 20241020T0602
            rec["iso"] = f"{rec['date'][:4]}-{rec['date'][4:6]}-{rec['date'][6:8]}T{rec['date'][9:11]}:{rec['date'][11:13]}:00Z"
            loaded.append(rec)

        stack_vv = np.stack([r["vv"] for r in loaded])
        stack_vh = np.stack([r["vh"] for r in loaded])
        stack_ratio = np.stack([r["ratio"] for r in loaded])
        scale = {
            "vv": (pctl_finite(stack_vv, 2), pctl_finite(stack_vv, 98)),
            "vh": (pctl_finite(stack_vh, 2), pctl_finite(stack_vh, 98)),
            "ratio": (pctl_finite(stack_ratio, 2), pctl_finite(stack_ratio, 98)),
        }
        print(f"  stretch vv={scale['vv']} vh={scale['vh']} ratio={scale['ratio']}", flush=True)

        dates_out = []
        for rec in loaded:
            date = rec["date"]
            dest = out_root / oid / date
            dest.mkdir(parents=True, exist_ok=True)
            mask = np.isfinite(rec["vv"]) & np.isfinite(rec["vh"])
            vv01 = stretch(rec["vv"], *scale["vv"])
            vh01 = stretch(rec["vh"], *scale["vh"])
            r01 = stretch(rec["ratio"], *scale["ratio"])
            gray_png(vv01, dest / "vv.png", mask)
            gray_png(vh01, dest / "vh.png", mask)
            # False color: R=VV, G=VH, B=VV/VH ratio (all dB, orbit-stretched)
            rgb_png(vv01, vh01, r01, dest / "fcc.png", mask)
            pinfo = prov_by_file.get(rec["path"].name, {})
            dates_out.append(
                {
                    "id": date,
                    "iso": rec["iso"],
                    "day": f"{date[:4]}-{date[4:6]}-{date[6:8]}",
                    "orbit_pass": pinfo.get("orbit") or ORBIT_META[oid]["pass"],
                    "item": pinfo.get("item"),
                    "width": int(rec["vv"].shape[1]),
                    "height": int(rec["vv"].shape[0]),
                    "native_width": rec["meta"]["width"],
                    "native_height": rec["meta"]["height"],
                    "crs": rec["meta"]["crs"],
                    "bounds": rec["meta"]["bounds"],
                    "files": {
                        "vv": f"tiles/valencia/{oid}/{date}/vv.png",
                        "vh": f"tiles/valencia/{oid}/{date}/vh.png",
                        "fcc": f"tiles/valencia/{oid}/{date}/fcc.png",
                    },
                    "days_from_dana": (
                        __import__("datetime").date(int(date[:4]), int(date[4:6]), int(date[6:8]))
                        - __import__("datetime").date(2024, 10, 29)
                    ).days,
                }
            )
            rec["vv01"] = vv01
            rec["vh01"] = vh01
            rec["mask"] = mask

        # change maps for swipe pairs in this orbit
        by_date = {r["date"]: r for r in loaded}
        change_files = {}
        for pair in SWIPE_PAIRS:
            if pair["orbit"] != oid:
                continue
            pre, post = by_date[pair["pre"]], by_date[pair["post"]]
            # log-ratio of linear is difference of dB: post - pre (more negative often = smoother water)
            delta = post["vv"] - pre["vv"]
            # stretch symmetrically around 0 for a diverging-like gray, plus a color version
            lim = max(abs(pctl_finite(delta, 2)), abs(pctl_finite(delta, 98)), 1e-3)
            d01 = stretch(delta, -lim, lim)
            cdir = TILES / "change" / pair["id"]
            cdir.mkdir(parents=True, exist_ok=True)
            mask = pre["mask"] & post["mask"]
            gray_png(d01, cdir / "vv_dB_diff.png", mask)
            # cyan (flood / decrease) vs amber (increase)
            # d01=0 is -lim (decrease, water-like), d01=1 is +lim
            # paint decreases as cyan, increases as amber
            dec = np.clip((0.5 - d01) * 2, 0, 1)  # 1 when strong decrease
            inc = np.clip((d01 - 0.5) * 2, 0, 1)
            r = 0.08 + 0.85 * inc
            g = 0.18 + 0.45 * inc + 0.55 * dec
            b = 0.10 + 0.85 * dec
            rgb_png(r, g, b, cdir / "vv_change.png", mask)
            change_files[pair["id"]] = {
                "gray": f"tiles/change/{pair['id']}/vv_dB_diff.png",
                "color": f"tiles/change/{pair['id']}/vv_change.png",
                "stretch_db": [-lim, lim],
            }
            print(f"  change {pair['id']} stretch ±{lim:.2f} dB", flush=True)

        bounds = loaded[0]["meta"]["bounds"]
        manifest_orbits.append(
            {
                "id": oid,
                **ORBIT_META[oid],
                "crs": loaded[0]["meta"]["crs"],
                "bounds": bounds,
                "n_dates": len(dates_out),
                "stretch_db": {k: [float(a), float(b)] for k, (a, b) in scale.items()},
                "dates": dates_out,
                "change": change_files,
            }
        )
        # free
        del loaded, stack_vv, stack_vh, stack_ratio

    return {"orbits": manifest_orbits, "swipe_pairs": SWIPE_PAIRS, "event": {"name": "Valencia DANA flood", "date": DANA, "location": "Valencia, Spain"}}


def pick_sen1_chips(n_per_country: int = 1, extra_spain: int = 3) -> list[str]:
    splits = SRC / "sen1floods11/splits/flood_handlabeled/flood_test_data.csv"
    label_dir = SRC / "sen1floods11/data/flood_events/HandLabeled/LabelHand"
    rows = list(csv.reader(splits.open()))
    scored = []
    for s1_name, lab_name in rows:
        lab_path = label_dir / lab_name
        if not lab_path.exists():
            continue
        with rasterio.open(lab_path) as src:
            lab = src.read(1)
        water = int((lab == 1).sum())
        valid = int((lab >= 0).sum())
        frac = water / max(valid, 1)
        country = s1_name.split("_")[0]
        scored.append((frac, water, country, s1_name, lab_name))
    scored.sort(reverse=True)
    picked = []
    seen = defaultdict(int)
    # first: highest-water chip per country
    for frac, water, country, s1, lab in scored:
        if seen[country] >= n_per_country:
            continue
        picked.append((frac, water, country, s1, lab))
        seen[country] += 1
    # extra Spain chips (challenge AOI is Valencia)
    for frac, water, country, s1, lab in scored:
        if country != "Spain":
            continue
        if any(p[3] == s1 for p in picked):
            continue
        picked.append((frac, water, country, s1, lab))
        if sum(1 for p in picked if p[2] == "Spain") >= 1 + extra_spain:
            break
    picked.sort(key=lambda x: (-(x[2] == "Spain"), -x[0]))
    return picked


def render_sen1(picked: list[tuple]) -> list[dict]:
    s1_dir = SRC / "sen1floods11/data/flood_events/HandLabeled/S1Hand"
    lab_dir = SRC / "sen1floods11/data/flood_events/HandLabeled/LabelHand"
    otsu_dir = SRC / "sen1floods11/data/flood_events/HandLabeled/S1OtsuLabelHand"
    jrc_dir = SRC / "sen1floods11/data/flood_events/HandLabeled/JRCWaterHand"
    out_root = TILES / "sen1"
    out_root.mkdir(parents=True, exist_ok=True)
    items = []
    for frac, water, country, s1_name, lab_name in picked:
        chip_id = s1_name.replace("_S1Hand.tif", "")
        print(f"[sen1] {chip_id} water_frac={frac:.3f}", flush=True)
        with rasterio.open(s1_dir / s1_name) as src:
            vv = src.read(1).astype(np.float32)  # already dB
            vh = src.read(2).astype(np.float32)
            bounds = [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top]
            crs = str(src.crs)
        with rasterio.open(lab_dir / lab_name) as src:
            lab = src.read(1)
        otsu = None
        otsu_name = lab_name.replace("LabelHand", "S1OtsuLabelHand")
        if (otsu_dir / otsu_name).exists():
            with rasterio.open(otsu_dir / otsu_name) as src:
                otsu = src.read(1)
        jrc = None
        jrc_name = lab_name.replace("LabelHand", "JRCWaterHand")
        if (jrc_dir / jrc_name).exists():
            with rasterio.open(jrc_dir / jrc_name) as src:
                jrc = src.read(1)

        mask = np.isfinite(vv) & np.isfinite(vh)
        vv01 = stretch(vv, pctl_finite(vv, 2), pctl_finite(vv, 98))
        vh01 = stretch(vh, pctl_finite(vh, 2), pctl_finite(vh, 98))
        ratio = vv - vh
        r01 = stretch(ratio, pctl_finite(ratio, 2), pctl_finite(ratio, 98))
        dest = out_root / chip_id
        dest.mkdir(parents=True, exist_ok=True)
        gray_png(vv01, dest / "vv.png", mask)
        gray_png(vh01, dest / "vh.png", mask)
        rgb_png(vv01, vh01, r01, dest / "fcc.png", mask)

        # label overlay: nodata transparent, dry dark, water cyan
        h, w = lab.shape
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[lab == 0] = (30, 30, 36, 180)
        rgba[lab == 1] = (0, 200, 220, 220)
        Image.fromarray(rgba, "RGBA").save(dest / "label.png", optimize=True)

        if otsu is not None:
            rgba = np.zeros((h, w, 4), np.uint8)
            rgba[otsu == 0] = (30, 30, 36, 180)
            rgba[otsu == 1] = (255, 170, 40, 220)
            Image.fromarray(rgba, "RGBA").save(dest / "otsu.png", optimize=True)
        if jrc is not None:
            rgba = np.zeros((h, w, 4), np.uint8)
            rgba[jrc == 1] = (70, 110, 255, 200)
            Image.fromarray(rgba, "RGBA").save(dest / "jrc.png", optimize=True)

        items.append(
            {
                "id": chip_id,
                "country": country,
                "split": "official Sen1Floods11 hand-labelled test",
                "water_frac": round(float(frac), 4),
                "water_pixels": int(water),
                "bounds": bounds,
                "crs": crs,
                "width": int(w),
                "height": int(h),
                "files": {
                    "vv": f"tiles/sen1/{chip_id}/vv.png",
                    "vh": f"tiles/sen1/{chip_id}/vh.png",
                    "fcc": f"tiles/sen1/{chip_id}/fcc.png",
                    "label": f"tiles/sen1/{chip_id}/label.png",
                    **({"otsu": f"tiles/sen1/{chip_id}/otsu.png"} if otsu is not None else {}),
                    **({"jrc": f"tiles/sen1/{chip_id}/jrc.png"} if jrc is not None else {}),
                },
            }
        )
    return items


def render_nisar() -> list[dict]:
    meta = json.loads((SRC / "nisar_granules_cmr.json").read_text())
    out_root = TILES / "nisar"
    out_root.mkdir(parents=True, exist_ok=True)
    items = []
    for city in ("valencia", "toronto", "jasper"):
        local = {p.name: p for p in (SRC / "nisar_browse" / city).glob("*.png")}
        city_items = []
        for rec in meta[city]:
            title = rec["title"]
            local_png = None
            # staged browse filename is the title + .png
            cand = f"{title}.png"
            if cand in local:
                local_png = local[cand]
            if local_png is None:
                continue
            dest = out_root / city
            dest.mkdir(parents=True, exist_ok=True)
            im = Image.open(local_png).convert("RGB")
            w, h = im.size
            scale = max(w, h) / 900
            if scale > 1:
                im = im.resize((int(w / scale), int(h / scale)), Image.LANCZOS)
            web_name = f"{title[:80]}.jpg"
            im.save(dest / web_name, quality=86, optimize=True)
            city_items.append(
                {
                    "title": title,
                    "start": rec["start"],
                    "collection": rec["collection"],
                    "size_mb_h5": rec["size_mb"],
                    "h5": rec["h5"],
                    "browse_urls": rec["browse"],
                    "file": f"tiles/nisar/{city}/{web_name}",
                    "native_px": [w, h],
                }
            )
        # also keep a compact catalog of all granules (no imagery if not staged)
        items.append(
            {
                "city": city,
                "n_granules_cmr": len(meta[city]),
                "n_browse_staged": len(city_items),
                "date_range": [
                    min(x["start"] for x in meta[city]),
                    max(x["start"] for x in meta[city]),
                ],
                "collections": sorted({x["collection"] for x in meta[city]}),
                "staged": city_items,
            }
        )
        print(f"[nisar] {city}: {len(city_items)} staged browses / {len(meta[city])} CMR granules", flush=True)
    return items


def main():
    TILES.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    valencia = render_valencia()
    picked = pick_sen1_chips()
    sen1 = render_sen1(picked)
    nisar = render_nisar()

    metrics = {
        "caveat": "One seed, not a published benchmark. Colab T4 attempt 1 reached these numbers, then the free GPU runtime ended before the final cell embedded PNGs or ONNX weights. Figures will be recovered on a T4 retry.",
        "dataset": "Sen1Floods11 official hand-labelled test split (90 chips), C-band Sentinel-1 VV/VH",
        "seed": 42,
        "hpo": {"best_valid_water_iou": 0.6286, "trials": 14, "pruned": 5},
        "test_water_iou": {
            "unet_final": 0.6635,
            "otsu_per_chip": 0.2181,
            "global_vv_threshold": 0.4682,
            "all_dry": 0.0,
        },
        "channel_ablation_test_water_iou": {
            "vv": 0.5713,
            "vv_vh": 0.651,
            "vv_vh_ratio": 0.6713,
        },
        "cpu_inference_s_per_512_tile": {
            "onnx_fp32": {"seconds": 1.6289, "water_iou_30chip_subset": 0.7067, "size_mb": 17.3},
            "onnx_int8": {"seconds": 14.3556, "water_iou_30chip_subset": 0.7078, "size_mb": 5.5},
            "torch_fp32": {"seconds": 2.3825},
        },
        "note_int8": "Dynamic INT8 quantization preserved water IoU on the 30-chip subset but was slower than FP32 on Colab CPU (not an edge device).",
        "source": "/workspace/colab_queue/runs/02_nasa_sar_flood_hpo/attempt1_numbers.txt",
    }

    citations = [
        {
            "item": "Sen1Floods11",
            "credit": "Bonafilia, Tellman, Anderson, Issenberg (2020). Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1. CVPR EarthVision.",
            "licence": "CC-BY-4.0",
            "url": "https://github.com/cloudtostreet/Sen1Floods11",
        },
        {
            "item": "Sentinel-1 RTC over Valencia",
            "credit": "Copernicus Sentinel-1 SAR, radiometrically terrain-corrected (RTC) via Microsoft Planetary Computer / ASF. Event context: 29 Oct 2024 DANA flood, Valencia, Spain.",
            "licence": "Copernicus Sentinel open access (CC-BY-SA compatible attribution).",
            "url": "https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc",
        },
        {
            "item": "NISAR GCOV browse imagery and CMR metadata",
            "credit": "NASA-ISRO SAR (NISAR) Level-2 Geocoded Polarimetric Covariance (GCOV). Browse PNGs and granule metadata from NASA CMR / ASF DAAC. Full .h5 granules require a free Earthdata login and are not bundled in this local demo.",
            "licence": "NASA open data.",
            "url": "https://nisar.asf.alaska.edu/",
        },
        {
            "item": "JRC Global Surface Water (permanent water prior in Sen1Floods11)",
            "credit": "Pekel, Cottam, Gorelick, Belward (2016). High-resolution mapping of global surface water and its long-term changes. Nature.",
            "licence": "Copernicus / JRC open data.",
            "url": "https://global-surface-water.appspot.com/",
        },
    ]

    manifest = {
        "title": "Dancing with the SARs — local demo",
        "challenge": "https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/",
        "licence": "Apache-2.0",
        "valencia": valencia,
        "sen1floods11": sen1,
        "nisar": nisar,
        "metrics": metrics,
        "citations": citations,
        "hooks": {
            "onnx_infer": "plugins/infer.py",
            "nisar_h5": "plugins/nisar_h5.py",
            "note": "Drop Saturday's trained ONNX weights and Earthdata-downloaded NISAR .h5 granules into these hooks. This demo ships without those files.",
        },
    }
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (DATA / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (DATA / "citations.json").write_text(json.dumps(citations, indent=2))
    print("WROTE", DATA / "manifest.json", flush=True)


if __name__ == "__main__":
    main()
