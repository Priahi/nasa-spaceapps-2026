#!/usr/bin/env python3
"""Local demo app for NASA Space Apps Hot Spots harmonization.

Local FastAPI server; the public site uses the static build (build_static.py).

Startup:
    /workspace/nasa-spaceapps/venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765
    # then open http://127.0.0.1:8765/
"""
from __future__ import annotations

import io
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
STATIC = ROOT / "static"

PRESETS = {
    "canada": {
        "label": "Canada",
        "country": "Canada",
        "bbox": [-141.0, 41.7, -52.6, 83.1],
        "center": [-96.0, 60.0],
        "zoom": 3,
    },
    "canada-boreal": {
        "label": "Canada boreal",
        "country": "Canada",
        "bbox": [-141.0, 50.0, -60.0, 70.0],
        "center": [-100.0, 58.0],
        "zoom": 4,
    },
    "bc": {
        "label": "British Columbia",
        "country": "Canada",
        "bbox": [-139.1, 48.3, -114.0, 60.0],
        "center": [-126.5, 54.0],
        "zoom": 5,
    },
    "alberta": {
        "label": "Alberta",
        "country": "Canada",
        "bbox": [-120.0, 49.0, -110.0, 60.0],
        "center": [-115.0, 54.5],
        "zoom": 5,
    },
    "argentina": {
        "label": "Argentina",
        "country": "Argentina",
        "bbox": [-73.6, -55.1, -53.6, -21.8],
        "center": [-64.0, -38.0],
        "zoom": 4,
    },
    "chaco": {
        "label": "Argentina Chaco",
        "country": "Argentina",
        "bbox": [-64.5, -28.5, -57.5, -22.0],
        "center": [-61.0, -25.5],
        "zoom": 6,
    },
    "parana-delta": {
        "label": "Paraná Delta",
        "country": "Argentina",
        "bbox": [-60.8, -34.6, -58.1, -32.0],
        "center": [-59.4, -33.3],
        "zoom": 7,
    },
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

app = FastAPI(title="FIRMS Hot Spots Harmonizer (local demo)", docs_url=None, redoc_url=None)


def _load_metrics() -> dict:
    p = ART / "metrics.json"
    if not p.exists():
        return {"status": "not_ready", "note": "Run train_harmonizer.py first."}
    with open(p) as f:
        return json.load(f)


@lru_cache(maxsize=4)
def tiles(country: str) -> pd.DataFrame:
    p = ART / f"tiles_{country.lower()}.parquet"
    if not p.exists():
        raise FileNotFoundError(f"missing {p.name}; run train_harmonizer.py")
    return pd.read_parquet(p)


@lru_cache(maxsize=4)
def disagreement(country: str) -> pd.DataFrame:
    p = ART / f"disagreement_{country.lower()}.parquet"
    if not p.exists():
        raise FileNotFoundError(f"missing {p.name}")
    return pd.read_parquet(p)


def filter_bbox(df: pd.DataFrame, west: float, south: float, east: float, north: float) -> pd.DataFrame:
    return df[(df.lon >= west) & (df.lon <= east) & (df.lat >= south) & (df.lat <= north)]


def calendar_from(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["year", "month", "harmonized", "lo", "hi", "modis_raw", "viirs_obs", "model", "robust_z", "unusual", "source"])
    cal = (
        df.groupby(["year", "month"], sort=True)
        .agg(
            harmonized=("v_equiv", "sum"),
            lo=("lo", "sum"),
            hi=("hi", "sum"),
            modis_raw=("m_n", "sum"),
            viirs_obs=("v_n", "sum"),
            model=("v_model", "sum"),
        )
        .reset_index()
    )
    # source: if every row in that month is backcast, label backcast; else observed
    src = df.groupby(["year", "month"])["source"].agg(lambda s: "backcast" if (s == "backcast").all() else "observed")
    cal = cal.merge(src.rename("source"), on=["year", "month"], how="left")
    # Fill missing year-months with zeros so the heatmap is a complete 2000-2025 grid
    years = range(2000, 2026)
    full = pd.DataFrame({"year": np.repeat(list(years), 12), "month": list(range(1, 13)) * 26})
    cal = full.merge(cal, on=["year", "month"], how="left")
    for c in ("harmonized", "lo", "hi", "modis_raw", "viirs_obs", "model"):
        cal[c] = cal[c].fillna(0.0)
    default_src = pd.Series(np.where(cal["year"] < 2012, "backcast", "observed"), index=cal.index)
    cal["source"] = cal["source"].fillna(default_src)
    piv = cal.pivot(index="year", columns="month", values="harmonized").fillna(0)
    med = piv.median()
    mad = (piv - med).abs().median().replace(0, np.nan)
    z = 0.6745 * (piv - med) / mad
    z_rows = []
    for yy in z.index:
        for mm in z.columns:
            zz = z.loc[yy, mm]
            z_rows.append({"year": int(yy), "month": int(mm), "robust_z": None if zz != zz else float(zz)})
    cal = cal.merge(pd.DataFrame(z_rows), on=["year", "month"], how="left")
    cal["unusual"] = cal["robust_z"].abs() > 3.5
    return cal


@app.get("/api/health")
def health():
    ready = (ART / "metrics.json").exists() and (ART / "tiles_canada.parquet").exists()
    return {"ok": True, "ready": ready, "note": "one seed, not a published benchmark"}


@app.get("/api/meta")
def meta():
    m = _load_metrics()
    countries = {}
    for c, r in (m.get("countries") or {}).items():
        if r.get("status") != "ok":
            countries[c] = {"status": r.get("status", "unknown")}
            continue
        countries[c] = {
            "status": "ok",
            "baselines": r.get("baselines"),
            "tuned_residual_test": r.get("tuned_residual_test"),
            "delta_rmse_log1p_vs_eb_cell_ratio": r.get("delta_rmse_log1p_vs_eb_cell_ratio"),
            "beats_best_baseline_rmse_log1p": r.get("beats_best_baseline_rmse_log1p"),
            "intervals": r.get("intervals"),
            "calendar": r.get("calendar"),
            "top_features_gain": r.get("top_features_gain"),
            "best_params": r.get("best_params"),
            "global_ratio_value": r.get("global_ratio_value"),
            "eb_prior_strength_k": r.get("eb_prior_strength_k"),
        }
    return {
        "note": "one seed, not a published benchmark",
        "presets": PRESETS,
        "protocol": m.get("protocol"),
        "colab_v1_reference": m.get("colab_v1_reference"),
        "countries": countries,
        "citations": {
            "data": "NASA FIRMS (LANCE/MODAPS), MODIS Collection 6.1 (MCD14ML) and VIIRS S-NPP (VNP14IMG). https://firms.modaps.eosdis.nasa.gov/",
            "licence": "Apache-2.0 for this app and model code. NASA data has no restriction on use; cite FIRMS.",
        },
    }


@app.get("/api/disagreement")
def api_disagreement(
    country: str = Query(..., description="Canada or Argentina"),
    west: float = Query(...),
    south: float = Query(...),
    east: float = Query(...),
    north: float = Query(...),
    limit: int = Query(12000, ge=100, le=25000),
):
    country = country.title()
    try:
        d = filter_bbox(disagreement(country), west, south, east, north)
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    d = d[(d.m_n + d.v_n) > 0].copy()
    # Prefer the most active cells if we have to downsample
    if len(d) > limit:
        d = d.assign(_s=d.m_n + d.v_n).nlargest(limit, "_s").drop(columns="_s")
    cols = ["lat", "lon", "m_n", "v_n", "log2_ratio", "frp_sum", "night", "aqua", "frac_low_frp", "frac_off_nadir"]
    out = d[cols].replace({np.nan: None})
    return {
        "country": country,
        "n": int(len(out)),
        "truncated": int(len(d) >= limit),
        "cells": out.to_dict(orient="records"),
    }


@app.get("/api/calendar")
def api_calendar(
    country: str = Query(...),
    west: float = Query(...),
    south: float = Query(...),
    east: float = Query(...),
    north: float = Query(...),
):
    country = country.title()
    try:
        t = filter_bbox(tiles(country), west, south, east, north)
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    cal = calendar_from(t)
    # Why sensors disagree (overlap years only)
    ov = t[t.source.isin(("observed", "observed_test"))]
    reasons = {}
    if len(ov):
        m_tot = float(ov.m_n.sum())
        v_tot = float(ov.v_n.sum())
        reasons["overlap_modis_detections"] = int(m_tot)
        reasons["overlap_viirs_detections"] = int(v_tot)
        reasons["viirs_modis_ratio"] = None if m_tot == 0 else round(v_tot / m_tot, 3)
        # Small-fire months: cell-months whose mean low-FRP fraction is high, or FRP/hotspot is low
        # Compare ratio in low-FRP vs high-FRP cell-months (contemporaneous MODIS).
        low = ov[ov.frac_low_frp >= 0.6]
        high = ov[ov.frac_low_frp < 0.4]
        def ratio(g):
            mm, vv = float(g.m_n.sum()), float(g.v_n.sum())
            return None if mm == 0 else round(vv / mm, 3)
        reasons["ratio_mostly_small_fires_frp_lt_10mw"] = ratio(low) if len(low) else None
        reasons["ratio_mostly_larger_fires"] = ratio(high) if len(high) else None
        night = ov[ov.m_night >= 0.5]
        day = ov[ov.m_night < 0.5]
        reasons["ratio_mostly_night_modis"] = ratio(night) if len(night) else None
        reasons["ratio_mostly_day_modis"] = ratio(day) if len(day) else None
        aqua = ov[ov.m_aqua >= 0.5]
        terra = ov[ov.m_aqua < 0.5]
        reasons["ratio_mostly_aqua"] = ratio(aqua) if len(aqua) else None
        reasons["ratio_mostly_terra"] = ratio(terra) if len(terra) else None
        reasons["mean_night_fraction_modis"] = round(float(ov.m_night.mean()), 3) if len(ov) else None
        reasons["mean_aqua_fraction_modis"] = round(float(ov.m_aqua.mean()), 3) if len(ov) else None
        reasons["mean_low_frp_fraction"] = round(float(ov.frac_low_frp.mean()), 3) if len(ov) else None
        reasons["explanation"] = (
            "VIIRS (375 m) detects more small and cooler fires than MODIS (1 km). "
            "A higher VIIRS/MODIS ratio in low-FRP or night-heavy cell-months is the expected physical pattern, "
            "not a bug. The residual model learns that correction on top of an empirical-Bayes cell-ratio baseline."
        )
    flagged = cal[cal.unusual & cal.robust_z.notna()][["year", "month", "harmonized", "robust_z", "source"]].sort_values("robust_z", key=lambda s: s.abs(), ascending=False)
    records = []
    for r in cal.itertuples(index=False):
        records.append(
            {
                "year": int(r.year),
                "month": int(r.month),
                "harmonized": round(float(r.harmonized), 2),
                "lo": round(float(r.lo), 2),
                "hi": round(float(r.hi), 2),
                "modis_raw": int(r.modis_raw),
                "viirs_obs": None if (r.year < 2012) else int(r.viirs_obs) if r.viirs_obs == r.viirs_obs else 0,
                "model": round(float(r.model), 2),
                "robust_z": None if r.robust_z != r.robust_z else round(float(r.robust_z), 3),
                "unusual": bool(r.unusual) if r.unusual == r.unusual else False,
                "source": r.source,
            }
        )
    return {
        "country": country,
        "bbox": [west, south, east, north],
        "n_cell_months": int(len(t)),
        "note": "one seed, not a published benchmark. 2000-2011 values are model back-casts and carry model error; 2012+ are observed VIIRS. Uncertainty bands are Mondrian CQR 90% intervals on the model, summed over cells in the AOI (conservative, not a formal regional interval).",
        "anomaly_rule": "robust z = 0.6745*(x-median)/MAD per calendar month across 2000-2025; |z|>3.5 flagged as unusual.",
        "calendar": records,
        "flagged": flagged.head(16).to_dict(orient="records"),
        "reasons": reasons,
        "months": MONTHS,
    }


@app.get("/api/export.csv")
def api_export(
    country: str = Query(...),
    west: float = Query(...),
    south: float = Query(...),
    east: float = Query(...),
    north: float = Query(...),
):
    country = country.title()
    try:
        t = filter_bbox(tiles(country), west, south, east, north)
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    cal = calendar_from(t)
    buf = io.StringIO()
    buf.write("# Harmonized MODIS-VIIRS burning activity calendar\n")
    buf.write(f"# country={country} bbox=[{west},{south},{east},{north}]\n")
    buf.write("# 2000-2011: model back-cast (VIIRS-equivalent). 2012+: observed VIIRS S-NPP.\n")
    buf.write("# lo/hi: Mondrian CQR 90% model interval, summed over cells (not a formal regional interval).\n")
    buf.write("# unusual: |robust z| > 3.5 vs 2000-2025 per-month median/MAD.\n")
    buf.write("# one seed, not a published benchmark. Data: NASA FIRMS MODIS C6.1 and VIIRS S-NPP.\n")
    buf.write("# Licence: Apache-2.0 for this tool. Cite FIRMS: https://firms.modaps.eosdis.nasa.gov/\n")
    out = cal.copy()
    out = out.rename(columns={"harmonized": "harmonized_count", "lo": "model_lo", "hi": "model_hi", "robust_z": "robust_z_vs_month_climatology"})
    out.to_csv(buf, index=False)
    payload = buf.getvalue().encode("utf-8")
    fname = f"harmonized_calendar_{country.lower()}_{west:.2f}_{south:.2f}_{east:.2f}_{north:.2f}.csv"
    return Response(
        content=payload,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


if STATIC.exists():
    app.mount("/", StaticFiles(directory=str(STATIC), html=True), name="static")
