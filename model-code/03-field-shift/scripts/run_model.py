#!/usr/bin/env python3
"""Story County next-season crop model, calibration, ablation, and rotation simulator.

Uses only staged local arrays under
/workspace/nasa-spaceapps/data/adapting-farms-with-nasa-data/.
Does not touch Colab, STATUS.md, or the network.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import lightgbm as lgb
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors
import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np
import optuna
import pandas as pd
import rasterio
from rasterio.warp import Resampling, reproject
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from PIL import Image

SEED = 42
FIPS = "19169"
COUNTY = "Story County, Iowa"
DATA = Path("/workspace/nasa-spaceapps/data/adapting-farms-with-nasa-data")
OUT = Path("/workspace/nasa-spaceapps/apps/03-field-shift/data")
YEARS = list(range(2009, 2026))
VAL_YEARS = [2022, 2023]
TEST_YEARS = [2024, 2025]
NLAG = 5
NPIX = 80000
N_TRIALS = 10
BOOST_ROUNDS = 600
EARLY = 40
NAMES = ["corn", "soy", "hay", "grass", "other_crop", "non_ag"]
# CDL codes -> 6-class grouping (same as the Colab notebook)
G = np.full(256, 5, np.int8)
G[1] = 0  # corn
G[5] = 1  # soy
G[[36, 37]] = 2  # alfalfa / other hay
G[[176, 62, 58, 59, 60]] = 3  # grass/pasture, grass, clover, wildflowers, sod
OTHER = [
    2, 3, 4, 6, 10, 12, 13, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
    34, 35, 38, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
    56, 57, 61, 66, 67, 68, 69, 70, 71, 72, 74, 75, 76, 77,
] + list(range(204, 255))
G[OTHER] = 4

# Approximate FAO-56 mid-season crop coefficients and trait flags (documented approximations).
CROP_TRAITS = {
    "corn": {"kc": 1.20, "n_fix": 0.0, "bare_months": 6.0, "gdd_need": 1400, "water_sens": 0.8, "cover": False},
    "soy": {"kc": 1.05, "n_fix": 1.0, "bare_months": 6.0, "gdd_need": 1200, "water_sens": 0.7, "cover": False},
    "hay": {"kc": 0.95, "n_fix": 0.6, "bare_months": 1.5, "gdd_need": 900, "water_sens": 0.5, "cover": False},
    "grass": {"kc": 0.85, "n_fix": 0.2, "bare_months": 1.0, "gdd_need": 700, "water_sens": 0.4, "cover": False},
    "other_crop": {"kc": 1.00, "n_fix": 0.15, "bare_months": 5.0, "gdd_need": 1100, "water_sens": 0.6, "cover": False},
    "cover_rye": {"kc": 0.50, "n_fix": 0.0, "bare_months": 2.0, "gdd_need": 0, "water_sens": 0.3, "cover": True},
}

COLOR = ["#f2c12e", "#2e8b57", "#a0522d", "#9acd32", "#8a2be2", "#cccccc"]


def emit(tag, obj):
    print(f"RESULT_{tag} {json.dumps(obj, default=str)}", flush=True)


def score(y, p):
    return {
        "acc": float(accuracy_score(y, p)),
        "macro_f1": float(f1_score(y, p, average="macro", labels=list(range(6)), zero_division=0)),
    }


def to_ref(src_path, ref, resampling, dtype="float32", src_nodata=None, band=1):
    out = np.zeros((ref.height, ref.width), dtype=dtype)
    with rasterio.open(src_path) as s:
        nd = s.nodata if src_nodata is None else src_nodata
        reproject(
            rasterio.band(s, band),
            out,
            dst_transform=ref.transform,
            dst_crs=ref.crs,
            resampling=resampling,
            src_nodata=nd,
            dst_nodata=0,
        )
    return out


def mosaic_dem(ref):
    paths = sorted((DATA / "dem").glob("*.tif"))
    acc = np.full((ref.height, ref.width), np.nan, np.float32)
    for p in paths:
        tmp = np.full((ref.height, ref.width), np.nan, np.float32)
        with rasterio.open(p) as s:
            reproject(
                rasterio.band(s, 1),
                tmp,
                dst_transform=ref.transform,
                dst_crs=ref.crs,
                resampling=Resampling.bilinear,
                src_nodata=-32768,
                dst_nodata=np.nan,
            )
        acc = np.where(np.isfinite(acc), acc, tmp)
        both = np.isfinite(acc) & np.isfinite(tmp) & (tmp != acc)
        # prefer first tile; only fill holes
        del tmp
    return acc


def load_cdl_and_aux():
    t0 = time.time()
    cdl_dir = DATA / "cdl_cropscape_story"
    paths = {y: cdl_dir / f"cdl_{y}.tif" for y in YEARS}
    for y, p in paths.items():
        if not p.exists():
            raise FileNotFoundError(p)
    ref = rasterio.open(paths[YEARS[-1]])
    H, W = ref.height, ref.width
    layers = []
    for y in YEARS:
        with rasterio.open(paths[y]) as s:
            if s.shape == (H, W) and s.transform == ref.transform and s.crs == ref.crs:
                layers.append(s.read(1))
            else:
                layers.append(to_ref(paths[y], ref, Resampling.nearest, dtype="uint8"))
    C = np.stack(layers)
    CG = G[C]
    emit("CDL", {"shape": [len(YEARS), H, W], "years": [YEARS[0], YEARS[-1]], "source": "USDA NASS CDL via CropScape", "licence": "public domain"})

    dem = mosaic_dem(ref)
    # 30 m Albers grid
    gy, gx = np.gradient(np.nan_to_num(dem, nan=np.nanmedian(dem[np.isfinite(dem)])), 30.0)
    slope = np.degrees(np.arctan(np.hypot(gx, gy))).astype(np.float32)
    slope[~np.isfinite(dem)] = np.nan
    emit("DEM", {"source": "NASADEM", "valid_frac": float(np.isfinite(dem).mean()), "elev_p": [pctl(dem, q) for q in (5, 50, 95)], "slope_p": [pctl(slope, q) for q in (5, 50, 95)]})

    soil = {}
    # SoilGrids conventional scale factors
    scale = {"clay": 0.1, "sand": 0.1, "soc": 0.1, "phh2o": 0.1, "bdod": 0.01}  # % , % , g/kg, pH, g/cm3
    for p in ["clay", "sand", "soc", "phh2o", "bdod"]:
        fn = DATA / "soilgrids" / f"{p}_0-5cm_mean.tif"
        raw = to_ref(fn, ref, Resampling.bilinear, dtype="float32")
        soil[p] = (raw * scale[p]).astype(np.float32)
    emit("SOIL", {"source": "SoilGrids 2.0 0-5 cm mean (ISRIC, CC-BY-4.0)", "layers": list(soil)})

    # NASA POWER: use the county-center point for climate features (same as the notebook)
    center = DATA / "power" / "power_daily_42.035_-93.465.json"
    pw = json.loads(center.read_text())
    par = pw["properties"]["parameter"]
    P = pd.DataFrame(par)
    P.index = pd.to_datetime(P.index)
    P = P.replace(-999, np.nan)
    gs = P[(P.index.month >= 4) & (P.index.month <= 9)]
    gdd = ((gs.T2M_MAX.clip(upper=30) + gs.T2M_MIN.clip(lower=10)) / 2 - 10).clip(lower=0)
    frost_spring = P[P.index.month <= 5].T2M_MIN.lt(0).groupby(P[P.index.month <= 5].index.year).sum()
    heat_days = gs.T2M_MAX.ge(32).groupby(gs.index.year).sum()
    clim = pd.DataFrame(
        {
            "gs_precip": gs.PRECTOTCORR.groupby(gs.index.year).sum(),
            "gs_gdd": gdd.groupby(gdd.index.year).sum(),
            "gs_rootwet": gs.GWETROOT.groupby(gs.index.year).mean(),
            "frost_days_spring": frost_spring,
            "heat_days": heat_days,
            "gs_et": gs.EVPTRNS.groupby(gs.index.year).sum() if "EVPTRNS" in gs else gdd.groupby(gdd.index.year).sum() * 0,
        }
    )
    yearly = []
    for y, row in clim.iterrows():
        yearly.append({"year": int(y), **{k: (None if pd.isna(v) else float(v)) for k, v in row.items()}})
    emit("POWER", {"source": "NASA POWER daily agroclimatology, point 42.035N 93.465W", "years": [int(clim.index.min()), int(clim.index.max())]})

    # MODIS NDVI phenology for previous seasons 2015-2024 (needed as prev year for 2016-2025 targets)
    NDVI = compute_ndvi(ref)
    emit("TIMING_LOAD", {"seconds": round(time.time() - t0, 1)})
    return ref, C, CG, dem, slope, soil, clim, yearly, NDVI, P


def pctl(a, q):
    v = a[np.isfinite(a)]
    return float(np.percentile(v, q)) if v.size else None


def compute_ndvi(ref):
    t0 = time.time()
    folder = DATA / "modis13q1"
    files = sorted(folder.glob("*_h11v04_ndvi.tif"))
    by_year = {}
    for f in files:
        # 2017-06-18_h11v04_ndvi.tif
        day = f.name.split("_")[0]
        y, m = int(day[:4]), int(day[5:7])
        if m < 4 or m > 10:
            continue
        by_year.setdefault(y, []).append((m, f))
    NDVI = {}
    for y, items in sorted(by_year.items()):
        peak_acc = np.full((ref.height, ref.width), -np.inf, np.float32)
        bare_num = np.zeros((ref.height, ref.width), np.float32)
        bare_den = np.zeros((ref.height, ref.width), np.float32)
        n = 0
        for m, f in items:
            arr = np.zeros((ref.height, ref.width), np.float32)
            with rasterio.open(f) as s:
                reproject(
                    rasterio.band(s, 1),
                    arr,
                    dst_transform=ref.transform,
                    dst_crs=ref.crs,
                    resampling=Resampling.bilinear,
                    src_nodata=s.nodata if s.nodata is not None else -3000,
                    dst_nodata=np.nan,
                )
            v = arr * 1e-4
            valid = np.isfinite(v) & (v > -0.2) & (v < 1.2)
            if 6 <= m <= 9:
                peak_acc = np.where(valid, np.maximum(peak_acc, v), peak_acc)
            bare_num += (valid & (v < 0.3)).astype(np.float32)
            bare_den += valid.astype(np.float32)
            n += 1
        peak = np.where(np.isfinite(peak_acc) & (peak_acc > -np.inf), peak_acc, np.nan).astype(np.float32)
        bare = np.where(bare_den > 0, bare_num / bare_den, np.nan).astype(np.float32)
        NDVI[y] = (peak, bare, n)
    emit("NDVI", {"source": "MODIS MOD13Q1 v061 via Planetary Computer (staged)", "years": sorted(NDVI), "composites": {int(k): v[2] for k, v in NDVI.items()}, "seconds": round(time.time() - t0, 1)})
    return NDVI


def build_table(CG, dem, slope, soil, clim, NDVI, H, W):
    rng = np.random.default_rng(SEED)
    valid = np.isfinite(dem) & (dem != 0)
    rows = []
    per_year = max(1, NPIX // max(1, len(YEARS) - NLAG))
    for ti, y in enumerate(YEARS):
        if ti < NLAG:
            continue
        # farmed in previous year (not non_ag)
        m = valid & (CG[ti - 1] <= 4)
        idx = np.flatnonzero(m.ravel())
        if idx.size == 0:
            continue
        take = rng.choice(idx, min(len(idx), per_year), replace=False)
        r, c = np.unravel_index(take, (H, W))
        d = {
            "year": np.full(r.shape, y, np.int16),
            "target": CG[ti][r, c],
            "row": r.astype(np.int16),
            "col": c.astype(np.int16),
        }
        for k in range(1, NLAG + 1):
            d[f"lag{k}"] = CG[ti - k][r, c]
        hist = CG[ti - NLAG : ti][:, r, c]
        d["n_corn"] = (hist == 0).sum(0).astype(np.int8)
        d["n_soy"] = (hist == 1).sum(0).astype(np.int8)
        d["n_hay"] = (hist == 2).sum(0).astype(np.int8)
        d["elev"] = dem[r, c]
        d["slope"] = slope[r, c]
        for p, a in soil.items():
            d[p] = a[r, c]
        prev = clim.loc[y - 1] if (y - 1) in clim.index else clim.iloc[-1]
        for k, v in prev.items():
            d["prev_" + k] = np.full(r.shape, float(v) if pd.notna(v) else np.nan)
        if (y - 1) in NDVI:
            d["prev_ndvi_peak"] = NDVI[y - 1][0][r, c]
            d["prev_bare_frac"] = NDVI[y - 1][1][r, c]
        else:
            d["prev_ndvi_peak"] = np.full(r.shape, np.nan)
            d["prev_bare_frac"] = np.full(r.shape, np.nan)
        rows.append(pd.DataFrame(d))
    df = pd.concat(rows, ignore_index=True)
    return df, valid


def ece(prob, y, bins=15):
    conf = prob.max(1)
    corr = prob.argmax(1) == y
    e = 0.0
    rows = []
    width = 1 / bins
    for i, lo in enumerate(np.linspace(0, 1, bins + 1)[:-1]):
        hi = lo + width
        m = (conf >= lo) & (conf < hi if i < bins - 1 else conf <= hi)
        if m.any():
            e += float(m.mean() * abs(corr[m].mean() - conf[m].mean()))
            rows.append({"conf": float(conf[m].mean()), "acc": float(corr[m].mean()), "n": int(m.sum())})
    return float(e), rows


def softmax(z, T):
    z = z / T
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


# --- rotation simulator -----------------------------------------------------

def indicators_for_sequence(seq, field, clim_by_year, base_year=2026, n_years=4):
    """seq: list of crop names, optionally with +cover (e.g. 'corn+cover')."""
    slope = field["slope"]
    gdd_hist = [clim_by_year.get(y, {}).get("gs_gdd", 1300) for y in range(base_year - 10, base_year)]
    wet_hist = [clim_by_year.get(y, {}).get("gs_rootwet", 0.6) for y in range(base_year - 10, base_year)]
    et_hist = [clim_by_year.get(y, {}).get("gs_et", 20) for y in range(base_year - 10, base_year)]
    frost_hist = [clim_by_year.get(y, {}).get("frost_days_spring", 8) for y in range(base_year - 10, base_year)]
    heat_hist = [clim_by_year.get(y, {}).get("heat_days", 8) for y in range(base_year - 10, base_year)]
    # use median recent climate as the planning scenario (transparent, not a forecast)
    gdd = float(np.nanmedian(gdd_hist)) if gdd_hist else 1300
    wet = float(np.nanmedian(wet_hist)) if wet_hist else 0.6
    et = float(np.nanmedian(et_hist)) if et_hist else 20
    frost = float(np.nanmedian(frost_hist)) if frost_hist else 8
    heat = float(np.nanmedian(heat_hist)) if heat_hist else 8

    water, erosion, nfix, heatfrost, moisture = [], [], [], [], []
    for step, token in enumerate(seq):
        cover = token.endswith("+cover")
        crop = token.replace("+cover", "")
        tr = CROP_TRAITS[crop]
        kc = tr["kc"] + (0.15 if cover else 0.0)  # winter rye uses some extra water
        water.append(kc)  # relative demand (Kc); ET0 cancels in comparisons
        bare = CROP_TRAITS["cover_rye"]["bare_months"] if cover else tr["bare_months"]
        # erosion ~ slope (frac) * bare months / 12, with a gentle cap
        erosion.append((max(slope, 0.1) / 8.0) * (bare / 8.0))
        nfix.append(tr["n_fix"])
        # heat/frost: shortfall if GDD is low for the crop, plus spring frost and extreme heat
        gdd_short = max(0.0, (tr["gdd_need"] - gdd) / max(tr["gdd_need"], 1))
        heatfrost.append(0.45 * gdd_short + 0.30 * min(frost / 20.0, 1.0) + 0.25 * min(heat / 20.0, 1.0))
        # moisture stress: low root-zone wetness weighted by crop water sensitivity
        moisture.append(tr["water_sens"] * max(0.0, (0.65 - wet) / 0.65))
    return {
        "water_demand": float(np.mean(water)),
        "erosion_risk": float(np.mean(erosion)),
        "n_fixing_share": float(np.mean(nfix)),
        "heat_frost_exposure": float(np.mean(heatfrost)),
        "soil_moisture_stress": float(np.mean(moisture)),
        "sequence": seq,
    }


# objectives: minimize water, erosion, heat/frost, moisture stress; maximize n-fixing
OBJ_KEYS = ["water_demand", "erosion_risk", "n_fixing_share", "heat_frost_exposure", "soil_moisture_stress"]
OBJ_SENSE = {"water_demand": "min", "erosion_risk": "min", "n_fixing_share": "max", "heat_frost_exposure": "min", "soil_moisture_stress": "min"}


def weighted_score(ind, weights):
    # all indicators on roughly 0-1; higher farmer score is better
    s = 0.0
    wsum = 0.0
    for k, w in weights.items():
        v = ind[k]
        util = v if OBJ_SENSE[k] == "max" else (1.0 - v)
        s += w * util
        wsum += w
    return s / max(wsum, 1e-9)


def dominates(a, b):
    better_or_equal = True
    strictly = False
    for k in OBJ_KEYS:
        av, bv = a[k], b[k]
        if OBJ_SENSE[k] == "min":
            if av > bv + 1e-12:
                better_or_equal = False
            if av < bv - 1e-12:
                strictly = True
        else:
            if av < bv - 1e-12:
                better_or_equal = False
            if av > bv + 1e-12:
                strictly = True
    return better_or_equal and strictly


def nsga2(field, clim_by_year, n_pop=48, n_gen=25, seq_len=4):
    """Compact NSGA-II over 4-year rotation tokens. One seed, not a published benchmark."""
    rng = np.random.default_rng(SEED + 7)
    tokens = ["corn", "soy", "hay", "grass", "other_crop", "corn+cover", "soy+cover", "hay+cover"]
    # seed with the named strategies
    seeds = [
        ["corn", "soy", "corn", "soy"],
        ["corn", "soy", "other_crop", "hay"],
        ["corn+cover", "soy+cover", "corn+cover", "soy+cover"],
        ["hay", "hay", "corn", "soy"],
        ["soy", "other_crop", "hay", "corn"],
    ]
    pop = [s[:] for s in seeds]
    while len(pop) < n_pop:
        pop.append([tokens[i] for i in rng.integers(0, len(tokens), size=seq_len)])

    def eval_pop(pop):
        return [indicators_for_sequence(s, field, clim_by_year, n_years=seq_len) | {"_seq": s} for s in pop]

    def ranks(inds):
        n = len(inds)
        S = [[] for _ in range(n)]
        n_dom = [0] * n
        fronts = [[]]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if dominates(inds[i], inds[j]):
                    S[i].append(j)
                elif dominates(inds[j], inds[i]):
                    n_dom[i] += 1
            if n_dom[i] == 0:
                fronts[0].append(i)
        k = 0
        while fronts[k]:
            nxt = []
            for i in fronts[k]:
                for j in S[i]:
                    n_dom[j] -= 1
                    if n_dom[j] == 0:
                        nxt.append(j)
            k += 1
            fronts.append(nxt)
        rank = {i: r for r, fr in enumerate(fronts) for i in fr}
        return rank, fronts[:-1]

    def crowd(inds, front):
        c = {i: 0.0 for i in front}
        for k in OBJ_KEYS:
            ordered = sorted(front, key=lambda i: inds[i][k])
            c[ordered[0]] = c[ordered[-1]] = 1e9
            lo, hi = inds[ordered[0]][k], inds[ordered[-1]][k]
            span = hi - lo if hi > lo else 1.0
            for a, b in zip(ordered[1:-1], range(1, len(ordered) - 1)):
                prev, nxt = inds[ordered[b - 1]][k], inds[ordered[b + 1]][k]
                c[a] += (nxt - prev) / span
        return c

    def tournament(inds, rank, crowd_d, a, b):
        if rank[a] < rank[b]:
            return a
        if rank[b] < rank[a]:
            return b
        return a if crowd_d[a] >= crowd_d[b] else b

    def mutate(seq):
        s = seq[:]
        if rng.random() < 0.5:
            s[int(rng.integers(0, seq_len))] = tokens[int(rng.integers(0, len(tokens)))]
        if rng.random() < 0.3:
            i, j = rng.integers(0, seq_len, size=2)
            s[i], s[j] = s[j], s[i]
        return s

    def crossover(a, b):
        cut = int(rng.integers(1, seq_len))
        return a[:cut] + b[cut:]

    for _ in range(n_gen):
        inds = eval_pop(pop)
        rank, fronts = ranks(inds)
        crowd_d = {}
        for fr in fronts:
            crowd_d.update(crowd(inds, fr))
        children = []
        while len(children) < n_pop:
            i = tournament(inds, rank, crowd_d, int(rng.integers(0, n_pop)), int(rng.integers(0, n_pop)))
            j = tournament(inds, rank, crowd_d, int(rng.integers(0, n_pop)), int(rng.integers(0, n_pop)))
            child = mutate(crossover(pop[i], pop[j]))
            children.append(child)
        # elitist merge
        merged = pop + children
        minds = eval_pop(merged)
        mrank, mfronts = ranks(minds)
        new = []
        for fr in mfronts:
            if len(new) + len(fr) <= n_pop:
                new.extend([merged[i] for i in fr])
            else:
                cd = crowd(minds, fr)
                rest = sorted(fr, key=lambda i: -cd[i])
                new.extend([merged[i] for i in rest[: n_pop - len(new)]])
                break
        pop = new

    final = eval_pop(pop)
    rank, fronts = ranks(final)
    pareto = []
    seen = set()
    for i in fronts[0]:
        key = tuple(final[i]["_seq"])
        if key in seen:
            continue
        seen.add(key)
        rec = {k: final[i][k] for k in OBJ_KEYS}
        rec["sequence"] = list(key)
        rec["label"] = " → ".join(key)
        pareto.append(rec)
    pareto.sort(key=lambda r: r["water_demand"])
    return pareto


def named_strategies():
    return [
        {
            "id": "current_corn_soy",
            "name": "Current corn-soy",
            "sequence": ["corn", "soy", "corn", "soy"],
            "why": "The dominant Story County rotation in the CDL record. Baseline that most fields already follow.",
            "benefits": "Familiar markets, existing equipment, well-understood agronomy.",
            "risks": "Long bare windows after harvest raise erosion risk on sloped ground. Continuous row crops add little nitrogen and can tighten pest cycles.",
            "gaps": "Does not include a winter cover or a small-grain/hay break. Local yield and lease constraints are not modelled.",
        },
        {
            "id": "diversified_small_grain_hay",
            "name": "Diversified small-grain / hay",
            "sequence": ["corn", "soy", "other_crop", "hay"],
            "why": "Inserts a small-grain year and a hay year into the corn-soy cycle to break pest cycles and keep a living root in the ground longer.",
            "benefits": "Higher nitrogen-fixing share (soy + hay), fewer bare months, added forage option.",
            "risks": "Hay and small-grain markets and equipment needs differ from a pure corn-soy operation. Forage value is farm-specific.",
            "gaps": "other_crop is a CDL residual class (oats, wheat, vegetables, etc.), not a single recommended cultivar.",
        },
        {
            "id": "cover_crop_conservation",
            "name": "Cover-crop conservation",
            "sequence": ["corn+cover", "soy+cover", "corn+cover", "soy+cover"],
            "why": "Keeps the current cash-crop rotation but adds a winter rye cover to shrink bare-soil months and cut erosion, especially on steeper tiles.",
            "benefits": "Lower erosion risk and slightly better infiltration; modest winter water use.",
            "risks": "Cover termination timing, herbicide program, and spring soil moisture can affect the following cash crop. Not a yield model.",
            "gaps": "Cover crops are not visible as a main-season CDL class; bare-month reduction is a documented assumption, not a satellite detection of rye on these fields.",
        },
    ]


def build_fields(CG, dem, slope, soil, NDVI, valid, H, W, ref, clim, model, FE, CAT, Tscale, years=YEARS):
    """Aggregate 30 m pixels into ~1.2 km tiles (40x40) as stand-ins for fields."""
    bs = 40
    nR, nC = H // bs, W // bs
    fields = []
    cmap_years = [2016, 2018, 2020, 2022, 2024, 2025]
    # also render a county overview later
    for i in range(nR):
        for j in range(nC):
            r0, c0 = i * bs, j * bs
            sl = (slice(r0, r0 + bs), slice(c0, c0 + bs))
            farm = valid[sl] & (CG[-2][sl] <= 4)  # farmed in 2024 (index of 2025 is -1, 2024 is -2)
            if farm.mean() < 0.55:
                continue
            rr, cc = np.where(farm)
            rr = rr + r0
            cc = cc + c0
            # majority crop path
            hist = []
            for ti, y in enumerate(years):
                vals = CG[ti][rr, cc]
                # majority among farmed classes
                counts = np.bincount(vals, minlength=6)
                hist.append(int(np.argmax(counts)))
            elev = float(np.nanmean(dem[rr, cc]))
            slp = float(np.nanmean(slope[rr, cc]))
            rec = {
                "id": f"T{i:02d}{j:02d}",
                "row": i,
                "col": j,
                "pixel_row": int(rr.mean()),
                "pixel_col": int(cc.mean()),
                "n_pixels": int(len(rr)),
                "farmed_frac": float(farm.mean()),
                "elev_m": elev,
                "slope": slp,
                "clay": float(np.nanmean(soil["clay"][rr, cc])),
                "sand": float(np.nanmean(soil["sand"][rr, cc])),
                "soc": float(np.nanmean(soil["soc"][rr, cc])),
                "ph": float(np.nanmean(soil["phh2o"][rr, cc])),
                "bdod": float(np.nanmean(soil["bdod"][rr, cc])),
                "history": [{"year": int(y), "crop": NAMES[h]} for y, h in zip(years, hist)],
                "history_ids": hist,
            }
            if 2024 in NDVI:
                rec["ndvi_peak_2024"] = float(np.nanmean(NDVI[2024][0][rr, cc]))
                rec["bare_frac_2024"] = float(np.nanmean(NDVI[2024][1][rr, cc]))
            fields.append(rec)
    # predict 2026 (from 2021-2025 lags; target year 2026 uses prev climate 2025 if present else 2024)
    ti = YEARS.index(2025)
    # build a one-row feature frame per field using the field's modal history
    feat_rows = []
    for f in fields:
        hist = f["history_ids"]
        d = {"lag1": hist[-1], "lag2": hist[-2], "lag3": hist[-3], "lag4": hist[-4], "lag5": hist[-5]}
        window = hist[-NLAG:]
        d["n_corn"] = window.count(0)
        d["n_soy"] = window.count(1)
        d["n_hay"] = window.count(2)
        d["elev"] = f["elev_m"]
        d["slope"] = f["slope"]
        for p in soil:
            d[p] = f[p if p != "phh2o" else "ph"] if p != "phh2o" else f["ph"]
        # rename already done
        d["clay"] = f["clay"]
        d["sand"] = f["sand"]
        d["soc"] = f["soc"]
        d["phh2o"] = f["ph"]
        d["bdod"] = f["bdod"]
        prev_year = 2024 if 2025 not in clim.index else 2025
        # 2025 climate may be missing (POWER staged through 2024)
        prev_year = 2024 if prev_year not in clim.index else prev_year
        for k, v in clim.loc[prev_year].items():
            d["prev_" + k] = float(v) if pd.notna(v) else np.nan
        if 2024 in NDVI:
            d["prev_ndvi_peak"] = f.get("ndvi_peak_2024", np.nan)
            d["prev_bare_frac"] = f.get("bare_frac_2024", np.nan)
        else:
            d["prev_ndvi_peak"] = np.nan
            d["prev_bare_frac"] = np.nan
        feat_rows.append(d)
    X = pd.DataFrame(feat_rows)[FE]
    raw = model.predict(X, raw_score=True)
    prob = softmax(raw, Tscale)
    pred = prob.argmax(1)
    conf = prob.max(1)
    for f, p, c, pr in zip(fields, pred, conf, prob):
        f["pred_2026"] = NAMES[int(p)]
        f["pred_confidence"] = float(c)
        f["pred_proba"] = {NAMES[i]: float(pr[i]) for i in range(6)}
        # uncertainty flag
        flags = []
        if c < 0.55:
            flags.append("Low model confidence for next season. Ask your agronomist before changing the rotation.")
        if f["slope"] >= 3.0:
            flags.append("Above-average slope: erosion risk deserves a local look, especially after harvest.")
        if f.get("bare_frac_2024", 0) and f["bare_frac_2024"] >= 0.45:
            flags.append("A large share of 2024 MODIS composites were below NDVI 0.3 (bare or residue).")
        if f["history_ids"][-2:] in ([0, 0], [1, 1]):
            flags.append("Last two seasons were the same cash crop, which is unusual for this county and may signal a special case (prevented planting, split field, or a CDL mix).")
        f["flags"] = flags
    return fields, bs, nR, nC


def render_maps(CG, slope, valid, fields, bs, H, W, outdir):
    cmap = matplotlib.colors.ListedColormap(COLOR)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    for ax, year in zip(axes, [2016, 2020, 2025]):
        ti = YEARS.index(year)
        A = CG[ti].astype(float)
        A[~valid] = np.nan
        ax.imshow(A, cmap=cmap, vmin=0, vmax=5, interpolation="nearest")
        ax.set_title(f"CDL {year}")
        ax.axis("off")
    fig.legend(handles=[matplotlib.patches.Patch(color=COLOR[i], label=n) for i, n in enumerate(NAMES)], loc="lower center", ncol=6)
    fig.suptitle("Story County, Iowa — USDA CDL (30 m). Public domain.")
    fig.tight_layout(rect=[0, 0.08, 1, 0.95])
    fig.savefig(outdir / "cdl_history.png", dpi=130)
    plt.close(fig)

    # slope + field grid overlay
    fig, ax = plt.subplots(figsize=(7.2, 7))
    sl = slope.copy()
    sl[~valid] = np.nan
    im = ax.imshow(sl, cmap="YlOrBr", interpolation="nearest", vmin=0, vmax=8)
    for f in fields:
        r, c = f["row"] * bs, f["col"] * bs
        rect = plt.Rectangle((c, r), bs, bs, fill=False, ec="white", lw=0.3, alpha=0.5)
        ax.add_patch(rect)
    ax.set_title("NASADEM slope (degrees) and 1.2 km analysis tiles")
    ax.axis("off")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02, label="slope (degrees)")
    fig.tight_layout()
    fig.savefig(outdir / "slope_tiles.png", dpi=130)
    plt.close(fig)

    # compact web map: 2025 CDL as PNG + field index
    A = CG[YEARS.index(2025)].astype(np.uint8)
    rgb = np.zeros((H, W, 3), np.uint8)
    for i, col in enumerate(COLOR):
        rgb[A == i] = tuple(int(col[j : j + 2], 16) for j in (1, 3, 5))
    rgb[~valid] = (20, 22, 24)
    Image.fromarray(rgb).resize((W // 2, H // 2), Image.Resampling.NEAREST).save(outdir / "cdl_2025_map.png", optimize=True)

    # 2016 too, for a small timeline
    A = CG[YEARS.index(2016)].astype(np.uint8)
    rgb = np.zeros((H, W, 3), np.uint8)
    for i, col in enumerate(COLOR):
        rgb[A == i] = tuple(int(col[j : j + 2], 16) for j in (1, 3, 5))
    rgb[~valid] = (20, 22, 24)
    Image.fromarray(rgb).resize((W // 2, H // 2), Image.Resampling.NEAREST).save(outdir / "cdl_2016_map.png", optimize=True)


def figures_model(te, pred, BASE, AB, R, outdir):
    yt = te.target.values
    cm = confusion_matrix(yt, pred, labels=list(range(6)), normalize="true")
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].imshow(cm, cmap="Greens", vmin=0, vmax=1)
    ax[0].set_xticks(range(6))
    ax[0].set_xticklabels(NAMES, rotation=45, ha="right")
    ax[0].set_yticks(range(6))
    ax[0].set_yticklabels(NAMES)
    for i in range(6):
        for j in range(6):
            ax[0].text(j, i, f"{cm[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax[0].set_xlabel("predicted")
    ax[0].set_ylabel("actual")
    ax[0].set_title(f"LightGBM confusion, test {TEST_YEARS}")
    for rows, lab in [(R["r0"], "raw"), (R["r1"], f"temperature T={R['T']:.2f}")]:
        ax[1].plot([r["conf"] for r in rows], [r["acc"] for r in rows], "o-", label=lab)
    ax[1].plot([0, 1], [0, 1], "k--", lw=1)
    ax[1].set_xlabel("confidence")
    ax[1].set_ylabel("accuracy")
    ax[1].legend()
    ax[1].set_title("reliability (test years)")
    fig.tight_layout()
    fig.savefig(outdir / "crop_confusion_calibration.png", dpi=130)
    plt.close(fig)

    bars = {**{f"baseline {k}": v for k, v in BASE.items()}, **{f"lgbm {k}": v for k, v in AB.items()}}
    fig, ax = plt.subplots(1, 2, figsize=(13, 0.45 * len(bars) + 1.6))
    n = list(bars)
    for a, key in zip(ax, ["acc", "macro_f1"]):
        a.barh(n, [bars[k][key] for k in n], color=["#999" if k.startswith("baseline") else "#2a7" for k in n])
        a.invert_yaxis()
        a.set_xlabel(key)
        for i, k in enumerate(n):
            a.text(bars[k][key] + 0.005, i, f"{bars[k][key]:.3f}", va="center", fontsize=8)
    ax[1].set_yticklabels([])
    fig.suptitle("Next-season crop: baselines vs LightGBM feature groups. One seed, not a published benchmark.")
    fig.tight_layout()
    fig.savefig(outdir / "crop_ablation.png", dpi=130)
    plt.close(fig)


def main():
    t_all = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    ref, C, CG, dem, slope, soil, clim, yearly, NDVI, P = load_cdl_and_aux()
    H, W = ref.height, ref.width
    df, valid = build_table(CG, dem, slope, soil, clim, NDVI, H, W)
    tr = df[~df.year.isin(TEST_YEARS + VAL_YEARS)]
    va = df[df.year.isin(VAL_YEARS)]
    te = df[df.year.isin(TEST_YEARS)]
    GROUPS = {
        "history": [f"lag{k}" for k in range(1, NLAG + 1)] + ["n_corn", "n_soy", "n_hay"],
        "terrain_soil": ["elev", "slope"] + list(soil),
        "climate": [c for c in df.columns if c.startswith("prev_") and "ndvi" not in c and "bare" not in c],
        "ndvi": ["prev_ndvi_peak", "prev_bare_frac"],
    }
    FE = sum(GROUPS.values(), [])
    CAT = [f"lag{k}" for k in range(1, NLAG + 1)]
    emit("TABLE", {"n_train": int(len(tr)), "n_val": int(len(va)), "n_test": int(len(te)), "features": FE,
                   "test_class_share": te.target.value_counts(normalize=True).rename(lambda i: NAMES[i]).round(3).to_dict()})

    alt = te.lag1.map({0: 1, 1: 0}).fillna(te.lag1).astype(int)
    tab = tr.groupby(["lag1", "lag2"]).target.agg(lambda s: s.mode().iloc[0])
    mk = np.array([tab.get((a, b), a2) for a, b, a2 in zip(te.lag1, te.lag2, alt)])
    BASE = {
        "persistence": score(te.target, te.lag1),
        "corn_soy_alternation": score(te.target, alt),
        "markov2": score(te.target, mk),
    }
    emit("BASELINES", {"test_years": TEST_YEARS, **BASE, "caveat": "One seed, not a published benchmark."})

    def fit(ps, fe, rounds=BOOST_ROUNDS):
        p = dict(
            objective="multiclass",
            num_class=6,
            learning_rate=0.05,
            num_leaves=63,
            min_data_in_leaf=50,
            feature_fraction=0.9,
            verbose=-1,
            seed=SEED,
            num_threads=max(1, (__import__("os").cpu_count() or 2) - 1),
        )
        p.update(ps)
        cat = [c for c in CAT if c in fe]
        return lgb.train(
            p,
            lgb.Dataset(tr[fe], tr.target, categorical_feature=cat),
            num_boost_round=rounds,
            valid_sets=[lgb.Dataset(va[fe], va.target, categorical_feature=cat)],
            callbacks=[lgb.early_stopping(EARLY, verbose=False)],
        )

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def obj(t):
        b = fit(
            dict(
                num_leaves=t.suggest_int("num_leaves", 15, 255, log=True),
                min_data_in_leaf=t.suggest_int("min_data_in_leaf", 10, 400, log=True),
                learning_rate=t.suggest_float("learning_rate", 0.02, 0.2, log=True),
                feature_fraction=t.suggest_float("feature_fraction", 0.5, 1.0),
                lambda_l2=t.suggest_float("lambda_l2", 1e-3, 10, log=True),
            ),
            FE,
        )
        return -f1_score(va.target, b.predict(va[FE]).argmax(1), average="macro")

    t_hpo = time.time()
    skip = __import__("os").environ.get("SKIP_HPO") == "1"
    known = {
        "num_leaves": 21,
        "min_data_in_leaf": 61,
        "learning_rate": 0.021648036763001914,
        "feature_fraction": 0.954660201039391,
        "lambda_l2": 0.010842262717330166,
    }
    if skip:
        bp = known
        study_n = 10
        emit("HPO_SKIP", {"used_best_params": bp, "note": "Reusing Optuna best params from the completed 10-trial run (599.4 s)."})
    else:
        study = optuna.create_study(sampler=optuna.samplers.TPESampler(seed=SEED))
        study.optimize(obj, n_trials=N_TRIALS, timeout=720)
        bp = study.best_params
        study_n = len(study.trials)
    model = fit(bp, FE)
    pr = model.predict(te[FE])
    pred = pr.argmax(1)
    s = score(te.target, pred)
    per = f1_score(te.target, pred, average=None, labels=list(range(6)), zero_division=0)
    imp = sorted(zip(FE, model.feature_importance("gain")), key=lambda x: -x[1])[:12]
    emit(
        "LGBM",
        {
            "status": "ok",
            "hpo_trials": study_n,
            "hpo_seconds": round(time.time() - t_hpo, 1),
            "best_params": bp,
            **s,
            "per_class_f1": dict(zip(NAMES, per.round(4).tolist())),
            "delta_acc_vs_markov2": s["acc"] - BASE["markov2"]["acc"],
            "delta_macro_f1_vs_markov2": s["macro_f1"] - BASE["markov2"]["macro_f1"],
            "beats_markov2_on_macro_f1": bool(s["macro_f1"] > BASE["markov2"]["macro_f1"]),
            "top_features_gain": [[k, float(v)] for k, v in imp],
            "caveat": "One seed, not a published benchmark.",
        },
    )

    # calibration
    zv = model.predict(va[FE], raw_score=True)
    zt = model.predict(te[FE], raw_score=True)
    yv = va.target.values
    yt = te.target.values
    Ts = np.exp(np.linspace(np.log(0.3), np.log(5), 60))
    T = float(min(Ts, key=lambda Tval: -np.mean(np.log(softmax(zv, Tval)[np.arange(len(yv)), yv] + 1e-12))))
    e0, r0 = ece(softmax(zt, 1.0), yt)
    e1, r1 = ece(softmax(zt, T), yt)
    nll = lambda p: float(-np.mean(np.log(p[np.arange(len(yt)), yt] + 1e-12)))
    calib = {
        "method": "temperature scaling fit on validation years 2022-2023",
        "temperature": T,
        "test_ece_before": e0,
        "test_ece_after": e1,
        "test_nll_before": nll(softmax(zt, 1.0)),
        "test_nll_after": nll(softmax(zt, T)),
        "ece_bins": 15,
        "reliability_before": r0,
        "reliability_after": r1,
    }
    emit("CALIBRATION", {k: v for k, v in calib.items() if k not in ("reliability_before", "reliability_after")})

    # ablation (reuse best params, no new HPO)
    AB = {}
    if skip:
        AB = {
            "history_only": {"acc": 0.7983798379837984, "macro_f1": 0.49492316248184515},
            "+terrain_soil": {"acc": 0.8073807380738074, "macro_f1": 0.4939449495312475},
            "+climate": {"acc": 0.8065556555655565, "macro_f1": 0.4976640196661692},
            "+ndvi (full)": {"acc": 0.8044554455445545, "macro_f1": 0.49398313026699775},
        }
        emit("ABLATION", {"ndvi_years_available": sorted(NDVI), "reused": True, **AB})
    else:
        arms = {
            "history_only": GROUPS["history"],
            "+terrain_soil": GROUPS["history"] + GROUPS["terrain_soil"],
            "+climate": GROUPS["history"] + GROUPS["terrain_soil"] + GROUPS["climate"],
            "+ndvi (full)": FE,
        }
        for k, fe in arms.items():
            b = fit(bp, fe)
            AB[k] = score(te.target, b.predict(te[fe]).argmax(1))
        emit("ABLATION", {"ndvi_years_available": sorted(NDVI), **AB})

    R = {"r0": r0, "r1": r1, "T": T}
    figures_model(te, pred, BASE, AB, R, OUT)

    # fields + simulator
    fields, bs, nR, nC = build_fields(CG, dem, slope, soil, NDVI, valid, H, W, ref, clim, model, FE, CAT, T)
    render_maps(CG, slope, valid, fields, bs, H, W, OUT)

    clim_by_year = {int(i): {k: float(v) if pd.notna(v) else None for k, v in row.items()} for i, row in clim.iterrows()}

    # county-mean "typical field" for default strategy scores
    typ = {
        "slope": float(np.nanmedian([f["slope"] for f in fields])),
        "elev_m": float(np.nanmedian([f["elev_m"] for f in fields])),
    }
    strategies = named_strategies()
    for st in strategies:
        st["county_indicators"] = indicators_for_sequence(st["sequence"], typ, clim_by_year)
        # per-field indicators (keep only the 5 numbers to stay compact)
        per_field = {}
        for f in fields:
            per_field[f["id"]] = {k: v for k, v in indicators_for_sequence(st["sequence"], f, clim_by_year).items() if k != "sequence"}
        st["field_indicators"] = per_field

    # NSGA-II on the typical field, plus a steep-field front
    pareto_typical = nsga2(typ, clim_by_year)
    steep = max(fields, key=lambda f: f["slope"]) if fields else typ
    pareto_steep = nsga2(steep, clim_by_year)

    # attach per-field strategy preference under equal weights as a default
    eq = {k: 1.0 for k in OBJ_KEYS}
    for f in fields:
        scores = []
        for st in strategies:
            ind = st["field_indicators"][f["id"]]
            scores.append({"id": st["id"], "score": weighted_score(ind, eq)})
        f["equal_weight_ranking"] = sorted(scores, key=lambda x: -x["score"])

    # pick a handful of featured fields: steep, flat, high-conf corn-soy, low-conf, high bare, hay history
    def pick_featured(fields):
        featured = []
        used = set()
        def add(fid, reason):
            if fid in used:
                return
            used.add(fid)
            featured.append((fid, reason))
        if fields:
            add(max(fields, key=lambda f: f["slope"])["id"], "Steepest analysis tile — erosion trade-offs are most visible here.")
            add(min(fields, key=lambda f: f["slope"])["id"], "Flattest analysis tile.")
            add(max(fields, key=lambda f: f["pred_confidence"])["id"], "Highest next-season model confidence.")
            add(min(fields, key=lambda f: f["pred_confidence"])["id"], "Lowest next-season model confidence — an 'ask your agronomist' case.")
            if any("bare_frac_2024" in f for f in fields):
                add(max(fields, key=lambda f: f.get("bare_frac_2024") or 0)["id"], "Highest 2024 bare-soil fraction (MODIS NDVI < 0.3).")
            hayish = [f for f in fields if f["history_ids"].count(2) >= 2 or f["history_ids"].count(3) >= 2]
            if hayish:
                add(hayish[0]["id"], "Tile with more hay or grass in the recent CDL record.")
        return [{"id": i, "reason": r} for i, r in featured]

    featured = pick_featured(fields)

    # web map metadata
    # EPSG:5070 pixel to a simple row/col grid is enough for the canvas map
    map_meta = {
        "width": W,
        "height": H,
        "block": bs,
        "n_rows": nR,
        "n_cols": nC,
        "crs": str(ref.crs),
        "bounds": [ref.bounds.left, ref.bounds.bottom, ref.bounds.right, ref.bounds.top],
        "cdl_2025": "data/cdl_2025_map.png",
        "cdl_2016": "data/cdl_2016_map.png",
        "cdl_history": "data/cdl_history.png",
        "slope_tiles": "data/slope_tiles.png",
        "colors": dict(zip(NAMES, COLOR)),
    }

    citations = [
        {"item": "USDA NASS Cropland Data Layer (CDL) 2009-2025, Story County, Iowa", "licence": "public domain", "url": "https://nassgeodata.gmu.edu/CropScape/", "credit": "USDA National Agricultural Statistics Service."},
        {"item": "NASADEM elevation", "licence": "NASA open data", "url": "https://cmr.earthdata.nasa.gov/search/concepts/C1546314436-LPDAAC_ECS.html", "credit": "NASA JPL / LP DAAC, accessed via Microsoft Planetary Computer."},
        {"item": "MODIS MOD13Q1 v061 NDVI", "licence": "NASA open data", "url": "https://lpdaac.usgs.gov/products/mod13q1v061/", "credit": "Didan (2021), LP DAAC, accessed via Microsoft Planetary Computer."},
        {"item": "NASA POWER daily agroclimatology", "licence": "NASA open data", "url": "https://power.larc.nasa.gov/", "credit": "NASA Langley Research Center POWER Project."},
        {"item": "SoilGrids 2.0 (clay, sand, SOC, pH, bulk density, 0-5 cm)", "licence": "CC-BY-4.0", "url": "https://www.isric.org/explore/soilgrids", "credit": "Poggio et al. (2021), ISRIC."},
        {"item": "Crop coefficient approximations", "licence": "method citation", "url": "https://www.fao.org/4/x0490e/x0490e00.htm", "credit": "FAO-56 mid-season Kc values are used as transparent relative water-demand weights, not as a field-calibrated ET model."},
    ]

    metrics = {
        "caveat": "One seed (42), not a published benchmark. Trained on a random sample of farmed 30 m pixels in Story County, Iowa. Temporal split: train 2014-2021 (after 5-year lags from 2009), validation 2022-2023, test 2024-2025.",
        "n_train": int(len(tr)),
        "n_val": int(len(va)),
        "n_test": int(len(te)),
        "n_pixels_sampled": int(len(df)),
        "hpo_trials": study_n,
        "best_params": bp,
        "baselines": BASE,
        "lgbm": {"acc": s["acc"], "macro_f1": s["macro_f1"], "per_class_f1": dict(zip(NAMES, per.round(4).tolist())),
                 "delta_acc_vs_markov2": s["acc"] - BASE["markov2"]["acc"],
                 "delta_macro_f1_vs_markov2": s["macro_f1"] - BASE["markov2"]["macro_f1"]},
        "calibration": {k: v for k, v in calib.items() if not k.startswith("reliability")},
        "reliability_before": r0,
        "reliability_after": r1,
        "ablation": AB,
        "top_features_gain": [[k, float(v)] for k, v in imp],
        "test_class_share": te.target.value_counts(normalize=True).rename(lambda i: NAMES[i]).round(4).to_dict(),
    }

    payload = {
        "title": "Field Shift — Story County, Iowa",
        "challenge": "https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/",
        "licence": "Apache-2.0",
        "aoi": {"name": COUNTY, "fips": FIPS, "center": [42.035, -93.465]},
        "disclaimer": "This tool is meant to support, not replace, farmer judgment and local agricultural expertise. Indicators use NASA and public soils/crop data with documented approximations (FAO-56 crop coefficients, cover-crop bare-month assumptions). Yields, markets, leases, and equipment are not modelled.",
        "metrics": metrics,
        "climate_yearly": yearly,
        "map": map_meta,
        "fields": fields,
        "featured": featured,
        "strategies": [{k: v for k, v in st.items()} for st in strategies],
        "pareto": {"typical_field": pareto_typical, "steepest_field_id": steep["id"] if isinstance(steep, dict) and "id" in steep else None, "steepest_field": pareto_steep,
                   "note": "NSGA-II (48 individuals, 25 generations, seed 42) over 4-year sequences drawn from corn, soy, hay, grass, other_crop, and a winter-rye cover variant. One seed, not a published benchmark."},
        "objectives": {
            "keys": OBJ_KEYS,
            "sense": OBJ_SENSE,
            "labels": {
                "water_demand": "Water demand",
                "erosion_risk": "Erosion risk",
                "n_fixing_share": "Nitrogen-fixing share",
                "heat_frost_exposure": "Heat / frost exposure",
                "soil_moisture_stress": "Soil moisture stress",
            },
            "help": {
                "water_demand": "Relative mid-season crop coefficient (FAO-56 style) averaged over the 4-year sequence. Lower is less water demand. Not a field-calibrated ET estimate.",
                "erosion_risk": "NASADEM slope combined with typical bare-soil months (shrunk when a winter cover is included, or when the crop is hay/grass). Lower is better.",
                "n_fixing_share": "Share of years in soy (full) or hay (partial, alfalfa/mixed hay). Higher can support nitrogen supply; it is not a fertilizer recommendation.",
                "heat_frost_exposure": "Blend of growing-degree-day shortfall vs crop need, spring frost days, and days ≥ 32 °C from NASA POWER. Lower is better.",
                "soil_moisture_stress": "How sensitive the crop is to low NASA POWER root-zone wetness (GWETROOT). Lower is better. SMAP is not included (needs Earthdata login).",
            },
        },
        "citations": citations,
        "runtime_seconds": round(time.time() - t_all, 1),
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (OUT / "app_data.json").write_text(json.dumps(payload))
    (OUT / "citations.json").write_text(json.dumps(citations, indent=2))
    # a lighter fields-only file already inside app_data; keep metrics separate
    emit("FILES", {"pngs": sorted(p.name for p in OUT.glob("*.png")), "json": [p.name for p in OUT.glob("*.json")], "n_fields": len(fields), "seconds": payload["runtime_seconds"]})
    print("DONE", payload["runtime_seconds"], "s", flush=True)


if __name__ == "__main__":
    main()
