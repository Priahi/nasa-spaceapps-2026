#!/usr/bin/env python3
"""v2 MODIS-to-VIIRS hotspot harmonizer (box CPU).

Fixes the Colab 01 Canada failure: the tuned LightGBM overfit 2012-2021
cell-intensity history (cell_v, cell_ratio) and under-predicted Canada's
extreme 2023-2025 fire years (0.3198 log1p RMSE, -63.5% bias, vs EB
baseline 0.3109). This script:

  * keeps the empirical-Bayes cell-ratio as a *baseline offset only*
  * trains LightGBM on the residual log-ratio, with no raw cell_v / cell_ratio
    / cell_m features (no intensity leakage)
  * adds physics features (FRP per hotspot, low-FRP fraction, night fraction,
    Aqua fraction, off-nadir pixel size)
  * calibrates Mondrian (stratified) CQR intervals so coverage on VIIRS-active
    cells is closer to the 90% target

Train years: 2012-2020. Val year: 2021. Test years: 2022-2025.
Every number is one seed, not a published benchmark.

Usage:
    /workspace/nasa-spaceapps/venv/bin/python train_harmonizer.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
import warnings
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

warnings.filterwarnings("ignore", category=UserWarning)

SEED = 0
CELL = 0.25
TEST_YEARS = [2022, 2023, 2024, 2025]
VAL_YEAR = 2021
YEARS_MODIS = list(range(2000, 2026))
YEARS_VIIRS = list(range(2012, 2026))
COUNTRIES = ["Canada", "Argentina"]
N_TRIALS = int(os.environ.get("N_TRIALS", "16"))
LOW_FRP_MW = 10.0
OFF_NADIR_PIX = 2.0
TARGET_COVER = 0.90
NOTE = "one seed, not a published benchmark"

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(
    os.environ.get(
        "DATA_DIR",
        "/workspace/nasa-spaceapps/data/modis-and-viirs-hot-spots/firms_country",
    )
)
ART = ROOT / "artifacts"
CACHE = ART / "cache"
MODEL_DIR = ART / "models"
for p in (ART, CACHE, MODEL_DIR):
    p.mkdir(parents=True, exist_ok=True)

np.random.seed(SEED)

# Residual-model features: contemporaneous MODIS physics + season/location
# + the EB offset itself. No raw cell_v / cell_ratio / cell_m intensity history.
FEATS = [
    "log1p_m_n",
    "log1p_eb",
    "log1p_frp_sum",
    "frp_per_hotspot",
    "m_frp_med",
    "frac_low_frp",
    "m_night",
    "m_aqua",
    "m_bright",
    "m_pix",
    "frac_off_nadir",
    "log1p_m_n_lag1",
    "log1p_m_n_lead1",
    "month_ratio",
    "lat",
    "lon",
    "msin",
    "mcos",
    "month",
]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def metrics(y, p, ym=None) -> dict:
    y = np.asarray(y, float)
    p = np.clip(np.asarray(p, float), 0, None)
    if len(y) == 0:
        return dict(rmse_log1p=None, mae=None, spearman=None, total_bias_pct=None)
    sp = spearmanr(y, p).correlation
    r = dict(
        rmse_log1p=round(float(np.sqrt(np.mean((np.log1p(y) - np.log1p(p)) ** 2))), 4),
        mae=round(float(np.mean(np.abs(y - p))), 4),
        spearman=round(float(sp), 4) if sp == sp else None,
        total_bias_pct=round(float(100.0 * (p.sum() - y.sum()) / max(y.sum(), 1.0)), 4),
    )
    if ym is not None:
        t = pd.DataFrame({"ym": ym, "y": y, "p": p}).groupby("ym").sum()
        t = t[t.y > 0]
        if len(t):
            r["monthly_total_mape_pct"] = round(float(100.0 * np.mean(np.abs(t.p - t.y) / t.y)), 4)
            spm = spearmanr(t.y, t.p).correlation
            r["monthly_total_spearman"] = round(float(spm), 4) if spm == spm else None
    return r


def grid_file(sensor: str, year: int, country: str) -> pd.DataFrame | None:
    fn = DATA_DIR / f"{sensor}_{year}_{country}.csv"
    if not fn.exists() or fn.stat().st_size < 100:
        return None
    if sensor == "modis":
        bcol = "brightness"
        want = {
            "latitude",
            "longitude",
            "brightness",
            "scan",
            "track",
            "acq_date",
            "satellite",
            "confidence",
            "frp",
            "daynight",
            "type",
        }
    else:
        bcol = "bright_ti4"
        want = {
            "latitude",
            "longitude",
            "bright_ti4",
            "scan",
            "track",
            "acq_date",
            "confidence",
            "frp",
            "daynight",
            "type",
        }
    d = pd.read_csv(fn, usecols=lambda c: c in want, low_memory=False)
    if d.empty:
        return None
    if "type" in d.columns:
        d = d[pd.to_numeric(d["type"], errors="coerce").fillna(-1) == 0]
    if sensor == "modis":
        d = d[pd.to_numeric(d["confidence"], errors="coerce") >= 30]
        sat = d["satellite"].astype(str).str.upper()
        d = d.copy()
        d["aqua"] = sat.str.startswith("A").astype("float32")
    else:
        d = d[d["confidence"].astype(str).str.lower() != "l"].copy()
    if d.empty:
        return None
    dt = pd.to_datetime(d["acq_date"], errors="coerce")
    d = d.loc[dt.notna()].copy()
    dt = dt.loc[d.index]
    d["ym"] = (dt.dt.year * 12 + dt.dt.month - 1).astype("int32")
    d["night"] = (d["daynight"].astype(str).str.upper() == "N").astype("float32")
    d["pix"] = (pd.to_numeric(d["scan"], errors="coerce").fillna(1.0) * pd.to_numeric(d["track"], errors="coerce").fillna(1.0)).astype("float32")
    d["frp"] = pd.to_numeric(d["frp"], errors="coerce").fillna(0.0).astype("float32")
    d["low_frp"] = (d["frp"] < LOW_FRP_MW).astype("float32")
    d["off_nadir"] = (d["pix"] >= OFF_NADIR_PIX).astype("float32")
    d["gy"] = np.floor(d["latitude"].to_numpy(dtype="float64") / CELL).astype("int32")
    d["gx"] = np.floor(d["longitude"].to_numpy(dtype="float64") / CELL).astype("int32")
    agg = dict(
        n=("frp", "size"),
        frp_sum=("frp", "sum"),
        frp_med=("frp", "median"),
        night=("night", "mean"),
        bright=(bcol, "mean"),
        pix=("pix", "mean"),
        frac_low_frp=("low_frp", "mean"),
        frac_off_nadir=("off_nadir", "mean"),
    )
    if sensor == "modis":
        agg["aqua"] = ("aqua", "mean")
    out = d.groupby(["gy", "gx", "ym"], sort=False).agg(**agg).reset_index()
    for c in out.columns:
        if c not in ("gy", "gx", "ym", "n"):
            out[c] = out[c].astype("float32")
    out["n"] = out["n"].astype("int32")
    out["gy"] = out["gy"].astype("int32")
    out["gx"] = out["gx"].astype("int32")
    out["ym"] = out["ym"].astype("int32")
    return out


def load_sensor(sensor: str, years: list[int], country: str) -> pd.DataFrame:
    cache = CACHE / f"{sensor}_{country}_{CELL}.parquet"
    if cache.exists():
        log(f"  cache hit {cache.name}")
        return pd.read_parquet(cache)
    parts = []
    for y in years:
        g = grid_file(sensor, y, country)
        if g is not None and len(g):
            parts.append(g)
            log(f"  {sensor} {country} {y}: {int(g.n.sum())} detections, {len(g)} cell-months")
        else:
            log(f"  {sensor} {country} {y}: empty")
        del g
    if not parts:
        raise RuntimeError(f"no {sensor} data for {country}")
    df = pd.concat(parts, ignore_index=True)
    df.to_parquet(cache, index=False)
    log(f"  wrote {cache} ({len(df)} rows)")
    return df


def add_time_geo(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["year"] = (df["ym"] // 12).astype("int16")
    df["month"] = (df["ym"] % 12 + 1).astype("int8")
    df["lat"] = ((df["gy"] + 0.5) * CELL).astype("float32")
    df["lon"] = ((df["gx"] + 0.5) * CELL).astype("float32")
    df["msin"] = np.sin(2 * np.pi * df["month"] / 12).astype("float32")
    df["mcos"] = np.cos(2 * np.pi * df["month"] / 12).astype("float32")
    return df


def finish_lags(df: pd.DataFrame, gm: pd.DataFrame) -> pd.DataFrame:
    key = gm[["gy", "gx", "ym", "m_n"]]
    df = df.merge(key.assign(ym=key.ym + 1).rename(columns={"m_n": "m_n_lag1"}), on=["gy", "gx", "ym"], how="left")
    df = df.merge(key.assign(ym=key.ym - 1).rename(columns={"m_n": "m_n_lead1"}), on=["gy", "gx", "ym"], how="left")
    df[["m_n_lag1", "m_n_lead1"]] = df[["m_n_lag1", "m_n_lead1"]].fillna(0)
    return df


def build_overlap(gm: pd.DataFrame, gv: pd.DataFrame) -> pd.DataFrame:
    """Dense cell x month table on 2012+ overlap, same universe as Colab 01."""
    obs = gm.merge(gv, on=["gy", "gx", "ym"], how="outer")
    obs = obs[obs.ym >= 2012 * 12].copy()
    fill = {c: 0 for c in obs.columns if c.startswith(("m_", "v_"))}
    obs = obs.fillna(fill)
    obs["year"] = (obs.ym // 12).astype("int16")
    tr_cells = obs[~obs.year.isin(TEST_YEARS)][["gy", "gx"]].drop_duplicates()
    months = np.arange(2012 * 12, (max(YEARS_VIIRS) + 1) * 12, dtype="int32")
    full = tr_cells.merge(pd.DataFrame({"ym": months}), how="cross")
    df = full.merge(obs, on=["gy", "gx", "ym"], how="outer")
    df = df.fillna({c: 0 for c in df.columns if c.startswith(("m_", "v_"))})
    df = add_time_geo(df)
    df = finish_lags(df, gm)
    return df


def cell_history(src: pd.DataFrame) -> pd.DataFrame:
    h = src.groupby(["gy", "gx"], sort=False).agg(
        cell_m=("m_n", "sum"),
        cell_v=("v_n", "sum"),
    ).reset_index()
    return h


def attach_history(df: pd.DataFrame, hist: pd.DataFrame) -> pd.DataFrame:
    out = df.merge(hist, on=["gy", "gx"], how="left")
    out["cell_m"] = out["cell_m"].fillna(0)
    out["cell_v"] = out["cell_v"].fillna(0)
    return out


def month_and_global_ratio(train: pd.DataFrame) -> tuple[pd.Series, float]:
    rg = float(train.v_n.sum() / max(train.m_n.sum(), 1.0))
    mr = train.groupby("month").apply(lambda g: float(g.v_n.sum() / max(g.m_n.sum(), 1.0)), include_groups=False)
    return mr, rg


def eb_pred(d: pd.DataFrame, mr: pd.Series, rg: float, k: float) -> np.ndarray:
    prior = d["month"].map(mr).fillna(rg).to_numpy(dtype="float64")
    cell_v = d["cell_v"].to_numpy(dtype="float64")
    cell_m = d["cell_m"].to_numpy(dtype="float64")
    m_n = d["m_n"].to_numpy(dtype="float64")
    return m_n * (cell_v + k * prior) / (cell_m + k)


def add_model_features(d: pd.DataFrame, mr: pd.Series, rg: float, k: float) -> pd.DataFrame:
    d = d.copy()
    d["month_ratio"] = d["month"].map(mr).fillna(rg).astype("float32")
    d["eb"] = eb_pred(d, mr, rg, k).astype("float32")
    m_n = d["m_n"].to_numpy(dtype="float64")
    frp = d["m_frp_sum"].to_numpy(dtype="float64")
    d["log1p_m_n"] = np.log1p(m_n).astype("float32")
    d["log1p_eb"] = np.log1p(d["eb"].to_numpy(dtype="float64")).astype("float32")
    d["log1p_frp_sum"] = np.log1p(np.clip(frp, 0, None)).astype("float32")
    d["frp_per_hotspot"] = np.where(m_n > 0, frp / np.maximum(m_n, 1.0), 0.0).astype("float32")
    d["log1p_m_n_lag1"] = np.log1p(d["m_n_lag1"].to_numpy(dtype="float64")).astype("float32")
    d["log1p_m_n_lead1"] = np.log1p(d["m_n_lead1"].to_numpy(dtype="float64")).astype("float32")
    for c in ("m_frp_med", "frac_low_frp", "m_night", "m_aqua", "m_bright", "m_pix", "frac_off_nadir"):
        if c not in d.columns:
            d[c] = np.float32(0)
        d[c] = d[c].fillna(0).astype("float32")
    return d


def fit_residual(params: dict, tr: pd.DataFrame, va: pd.DataFrame, rounds: int = 800) -> lgb.Booster:
    p = dict(
        objective="regression",
        metric="l2",
        learning_rate=0.05,
        num_leaves=31,
        min_data_in_leaf=200,
        feature_fraction=0.8,
        bagging_fraction=0.8,
        bagging_freq=1,
        lambda_l2=1.0,
        max_depth=6,
        verbose=-1,
        seed=SEED,
        num_threads=max(1, min(6, os.cpu_count() or 4)),
    )
    p.update(params)
    ytr = np.log1p(tr.v_n.to_numpy(dtype="float64")) - np.log1p(tr.eb.to_numpy(dtype="float64"))
    yva = np.log1p(va.v_n.to_numpy(dtype="float64")) - np.log1p(va.eb.to_numpy(dtype="float64"))
    return lgb.train(
        p,
        lgb.Dataset(tr[FEATS], ytr, free_raw_data=True),
        num_boost_round=rounds,
        valid_sets=[lgb.Dataset(va[FEATS], yva, free_raw_data=True)],
        callbacks=[lgb.early_stopping(80, verbose=False)],
    )


def apply_residual(model: lgb.Booster, d: pd.DataFrame, bias_corr: float = 0.0) -> np.ndarray:
    resid = model.predict(d[FEATS]) + bias_corr
    pred = np.expm1(np.log1p(d.eb.to_numpy(dtype="float64")) + resid)
    pred = np.clip(pred, 0, None)
    # When MODIS saw nothing the EB offset is already 0. Do not sprinkle tiny
    # positive counts across the huge zero class: that collapsed Spearman and
    # inflated monthly MAPE in the first v2 pass. VIIRS-only detections are
    # reflected in the interval, not the point estimate.
    m_n = d["m_n"].to_numpy(dtype="float64")
    pred = np.where(m_n <= 0, 0.0, pred)
    return pred


def fit_quantile(alpha: float, tr: pd.DataFrame, va: pd.DataFrame, rounds: int = 600) -> lgb.Booster:
    p = dict(
        objective="quantile",
        alpha=alpha,
        learning_rate=0.05,
        num_leaves=31,
        min_data_in_leaf=200,
        feature_fraction=0.8,
        bagging_fraction=0.8,
        bagging_freq=1,
        lambda_l2=2.0,
        max_depth=6,
        verbose=-1,
        seed=SEED,
        num_threads=max(1, min(6, os.cpu_count() or 4)),
    )
    ytr = np.log1p(tr.v_n.to_numpy(dtype="float64")) - np.log1p(tr.eb.to_numpy(dtype="float64"))
    yva = np.log1p(va.v_n.to_numpy(dtype="float64")) - np.log1p(va.eb.to_numpy(dtype="float64"))
    return lgb.train(
        p,
        lgb.Dataset(tr[FEATS], ytr, free_raw_data=True),
        num_boost_round=rounds,
        valid_sets=[lgb.Dataset(va[FEATS], yva, free_raw_data=True)],
        callbacks=[lgb.early_stopping(80, verbose=False)],
    )


def stratum_id(m_n: np.ndarray, edges: list[float]) -> np.ndarray:
    """Mondrian strata from contemporaneous MODIS count (known at inference)."""
    s = np.zeros(len(m_n), dtype="int8")
    s[m_n > 0] = 1
    if len(edges) >= 1:
        s[m_n > edges[0]] = 2
    if len(edges) >= 2:
        s[m_n > edges[1]] = 3
    return s


def conformal_quantile(scores: np.ndarray, level: float = TARGET_COVER) -> float:
    if len(scores) == 0:
        return 0.0
    q = min(1.0, level * (1.0 + 1.0 / len(scores)))
    return float(np.quantile(scores, q))


def mondrian_cqr(
    y_cal: np.ndarray,
    lo_cal: np.ndarray,
    hi_cal: np.ndarray,
    strata_cal: np.ndarray,
    lo: np.ndarray,
    hi: np.ndarray,
    strata: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Mondrian CQR with an active-cell-aware margin.

    A 90% quantile taken over all cells in a stratum is ~0 when the stratum
    is dominated by zeros (especially m_n==0). That leaves VIIRS-active
    cells under-covered. For each stratum we also compute a margin on the
    val rows with y>0 and take the max, which is conservative for overall
    coverage and much closer to the 90% target on active cells.
    """
    margins = {}
    margins_active = {}
    lo_out = lo.copy()
    hi_out = hi.copy()
    global_s = np.maximum(lo_cal - y_cal, y_cal - hi_cal)
    global_q = conformal_quantile(global_s)
    active_cal = y_cal > 0
    global_q_active = conformal_quantile(global_s[active_cal]) if active_cal.sum() >= 20 else global_q
    for s in sorted(set(strata_cal.tolist()) | set(strata.tolist())):
        mask_cal = strata_cal == s
        if mask_cal.sum() >= 30:
            sc = np.maximum(lo_cal[mask_cal] - y_cal[mask_cal], y_cal[mask_cal] - hi_cal[mask_cal])
            q_all = conformal_quantile(sc)
        else:
            q_all = global_q
        pos = mask_cal & active_cal
        if pos.sum() >= 20:
            sc_pos = np.maximum(lo_cal[pos] - y_cal[pos], y_cal[pos] - hi_cal[pos])
            q_pos = conformal_quantile(sc_pos, level=TARGET_COVER)
        else:
            q_pos = global_q_active
        q = max(q_all, q_pos)
        margins[int(s)] = round(float(q_all), 4)
        margins_active[int(s)] = round(float(q_pos), 4)
        m = strata == s
        lo_out[m] = lo[m] - q
        hi_out[m] = hi[m] + q
        # store the applied (max) margin under a combined map later
        margins[int(s)] = round(float(q), 4)
    lo_out = np.clip(lo_out, 0, None)
    hi_out = np.maximum(hi_out, lo_out)
    return lo_out, hi_out, {
        "per_stratum_margin": margins,
        "per_stratum_margin_active_only": margins_active,
        "global_margin": round(global_q, 4),
        "global_margin_active_only": round(float(global_q_active), 4),
        "cqr_note": "Applied margin is max(all-cells, VIIRS-active-cells) per MODIS-count stratum, calibrated on 2021. Conservative for overall coverage; aimed at ~90% on active cells.",
    }


def coverage_report(y, lo, hi) -> dict:
    y = np.asarray(y, float)
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    inside = (y >= lo) & (y <= hi)
    active = y > 0
    return dict(
        target_coverage=TARGET_COVER,
        cqr_coverage=round(float(inside.mean()), 4),
        cqr_coverage_on_viirs_active_cells=round(float(inside[active].mean()), 4) if active.any() else None,
        cqr_coverage_on_zero_cells=round(float(inside[~active].mean()), 4) if (~active).any() else None,
        mean_width_cqr=round(float(np.mean(hi - lo)), 4),
        mean_width_cqr_active=round(float(np.mean((hi - lo)[active])), 4) if active.any() else None,
        n_active=int(active.sum()),
        n_total=int(len(y)),
    )


def hpo(tr: pd.DataFrame, va: pd.DataFrame) -> tuple[dict, list]:
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    history = []

    def objective(trial: "optuna.Trial") -> float:
        ps = dict(
            num_leaves=trial.suggest_int("num_leaves", 8, 63),
            min_data_in_leaf=trial.suggest_int("min_data_in_leaf", 80, 800, log=True),
            learning_rate=trial.suggest_float("learning_rate", 0.02, 0.1, log=True),
            feature_fraction=trial.suggest_float("feature_fraction", 0.5, 0.95),
            lambda_l2=trial.suggest_float("lambda_l2", 0.1, 30.0, log=True),
            max_depth=trial.suggest_int("max_depth", 4, 8),
        )
        try:
            model = fit_residual(ps, tr, va)
            pred = apply_residual(model, va)
            val = metrics(va.v_n, pred)["rmse_log1p"]
            history.append({"params": ps, "val_rmse_log1p": val, "best_iter": int(model.best_iteration or 0)})
            log(f"    trial {trial.number}: val_rmse={val:.4f} iter={int(model.best_iteration or 0)} {ps}")
            return val
        except Exception as e:
            log(f"    trial {trial.number} failed: {e}")
            return 1e9

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(objective, n_trials=N_TRIALS, timeout=12 * 60, catch=(Exception,))
    best = dict(study.best_params)
    log(f"  HPO best val RMSE log1p={study.best_value:.4f} params={best}")
    return best, history


def prepare_modis(raw: pd.DataFrame) -> pd.DataFrame:
    g = raw.rename(
        columns={
            "n": "m_n",
            "frp_sum": "m_frp_sum",
            "frp_med": "m_frp_med",
            "night": "m_night",
            "bright": "m_bright",
            "pix": "m_pix",
            "frac_low_frp": "frac_low_frp",
            "frac_off_nadir": "frac_off_nadir",
            "aqua": "m_aqua",
        }
    )
    if "m_aqua" not in g.columns:
        g["m_aqua"] = np.float32(0)
    return g


def run_country(country: str) -> dict:
    t0 = time.time()
    log(f"==== {country}: loading ====")
    gm = prepare_modis(load_sensor("modis", YEARS_MODIS, country))
    gv = load_sensor("viirs-snpp", YEARS_VIIRS, country)[["gy", "gx", "ym", "n"]].rename(columns={"n": "v_n"})
    log(f"  MODIS detections={int(gm.m_n.sum())} cell-months={len(gm)}")
    log(f"  VIIRS detections={int(gv.v_n.sum())} cell-months={len(gv)}")

    log(f"==== {country}: building overlap table ====")
    df = build_overlap(gm, gv)
    log(f"  overlap rows={len(df):,}")

    # History and ratios from the model-training split only (2012-2020) when
    # fitting; EB baseline reported on test uses 2012-2021 train (standard).
    train_all = df[~df.year.isin(TEST_YEARS)].copy()  # 2012-2021
    test = df[df.year.isin(TEST_YEARS)].copy()
    tr_raw = train_all[train_all.year < VAL_YEAR].copy()  # 2012-2020
    va_raw = train_all[train_all.year == VAL_YEAR].copy()  # 2021

    hist_tr = cell_history(tr_raw)
    hist_all_train = cell_history(train_all)
    mr_tr, rg_tr = month_and_global_ratio(tr_raw)
    mr_all, rg_all = month_and_global_ratio(train_all)

    # Pick EB shrinkage k on the val year, history from 2012-2020 only (no leak).
    tr_eb = attach_history(tr_raw, hist_tr)
    va_eb = attach_history(va_raw, hist_tr)
    ks = [1, 3, 10, 30, 100, 300, 1000]
    k_best = min(ks, key=lambda k: metrics(va_eb.v_n, eb_pred(va_eb, mr_tr, rg_tr, k))["rmse_log1p"])
    log(f"  EB prior k={k_best} (selected on {VAL_YEAR})")

    # Test baselines use 2012-2021 history (same protocol as Colab 01).
    test_b = attach_history(test, hist_all_train)
    y = test_b.v_n.to_numpy(dtype="float64")
    b_global = test_b.m_n.to_numpy(dtype="float64") * rg_all
    b_month = test_b.m_n.to_numpy(dtype="float64") * test_b.month.map(mr_all).fillna(rg_all).to_numpy(dtype="float64")
    month_fallback = test_b.month.map(mr_all).fillna(rg_all).to_numpy(dtype="float64")
    cell_ratio = np.where(test_b.cell_m > 0, test_b.cell_v / test_b.cell_m.clip(lower=1), month_fallback)
    b_cell = test_b.m_n.to_numpy(dtype="float64") * cell_ratio
    b_eb = eb_pred(test_b, mr_all, rg_all, k_best)
    base = {
        "global_ratio": metrics(y, b_global, test_b.ym),
        "month_ratio": metrics(y, b_month, test_b.ym),
        "cell_ratio": metrics(y, b_cell, test_b.ym),
        "eb_cell_ratio": metrics(y, b_eb, test_b.ym),
    }
    log(f"  baselines: {json.dumps(base)}")

    # Residual model: train on 2012-2020, val 2021, history/ratios from 2012-2020.
    tr = add_model_features(attach_history(tr_raw, hist_tr), mr_tr, rg_tr, k_best)
    va = add_model_features(attach_history(va_raw, hist_tr), mr_tr, rg_tr, k_best)
    # For test predictions we keep the same model (no 2021 refit) so CQR stays valid.
    # EB offset on test still uses 2012-2021 history, matching the reported baseline.
    te = add_model_features(test_b, mr_all, rg_all, k_best)

    log(f"==== {country}: default residual model ====")
    default_model = fit_residual({}, tr, va)
    default_pred_va = apply_residual(default_model, va)
    default_bias = float(np.median((np.log1p(va.v_n.to_numpy(dtype="float64")) - np.log1p(va.eb.to_numpy(dtype="float64"))) - default_model.predict(va[FEATS])))
    default_pred = apply_residual(default_model, te, default_bias)
    m_default = metrics(y, default_pred, te.ym)
    log(f"  default+val-bias-corr={default_bias:.4f} test={m_default}")

    reused = None
    prev_path = ART / f"metrics_{country.lower()}.json"
    if os.environ.get("REUSE_PARAMS", "1") == "1" and prev_path.exists():
        with open(prev_path) as f:
            prev = json.load(f)
        reused = prev.get("best_params")
    if reused:
        log(f"==== {country}: reusing saved HPO params {reused} ====")
        best_params, hpo_hist = reused, []
    else:
        log(f"==== {country}: HPO ({N_TRIALS} trials, 12 min cap) ====")
        best_params, hpo_hist = hpo(tr, va)
    best_model = fit_residual(best_params, tr, va)
    va_pred_raw = apply_residual(best_model, va)
    # Constant residual bias correction from the val year only (no test peek).
    bias_corr = float(np.median((np.log1p(va.v_n.to_numpy(dtype="float64")) - np.log1p(va.eb.to_numpy(dtype="float64"))) - best_model.predict(va[FEATS])))
    va_pred = apply_residual(best_model, va, bias_corr)
    te_pred = apply_residual(best_model, te, bias_corr)
    m_best = metrics(y, te_pred, te.ym)
    m_val = metrics(va.v_n, va_pred, va.ym)
    log(f"  tuned val={m_val}")
    log(f"  tuned test={m_best} bias_corr={bias_corr:.4f}")

    # Feature importance
    imp = sorted(zip(FEATS, best_model.feature_importance("gain")), key=lambda x: -x[1])

    # Intervals: residual quantile GBM + Mondrian CQR on the val year.
    log(f"==== {country}: Mondrian CQR intervals ====")
    lo_m = fit_quantile(0.05, tr, va)
    hi_m = fit_quantile(0.95, tr, va)

    def interval_from_residual(d, lo_model, hi_model):
        lo_r = lo_model.predict(d[FEATS]) + bias_corr
        hi_r = hi_model.predict(d[FEATS]) + bias_corr
        # keep lo <= residual point <= hi on the residual scale before expm1
        point_r = best_model.predict(d[FEATS]) + bias_corr
        lo_r = np.minimum(lo_r, point_r)
        hi_r = np.maximum(hi_r, point_r)
        eb = d.eb.to_numpy(dtype="float64")
        lo = np.clip(np.expm1(np.log1p(eb) + lo_r), 0, None)
        hi = np.clip(np.expm1(np.log1p(eb) + hi_r), 0, None)
        hi = np.maximum(hi, lo)
        return lo, hi

    lo_va, hi_va = interval_from_residual(va, lo_m, hi_m)
    lo_te, hi_te = interval_from_residual(te, lo_m, hi_m)
    pos = tr.m_n.to_numpy(dtype="float64")
    pos = pos[pos > 0]
    edges = list(np.quantile(pos, [0.50, 0.90])) if len(pos) else []
    strata_va = stratum_id(va.m_n.to_numpy(dtype="float64"), edges)
    strata_te = stratum_id(te.m_n.to_numpy(dtype="float64"), edges)
    lo_te_c, hi_te_c, cqr_meta = mondrian_cqr(
        va.v_n.to_numpy(dtype="float64"), lo_va, hi_va, strata_va, lo_te, hi_te, strata_te
    )
    # Also apply CQR to val just for a diagnostic (these are calibration numbers).
    lo_va_c, hi_va_c, _ = mondrian_cqr(
        va.v_n.to_numpy(dtype="float64"), lo_va, hi_va, strata_va, lo_va, hi_va, strata_va
    )
    intervals = coverage_report(y, lo_te_c, hi_te_c)
    intervals.update(cqr_meta)
    intervals["stratum_edges_m_n"] = [round(float(e), 3) for e in edges]
    intervals["stratum_rule"] = "0: m_n==0; 1: 0<m_n<=p50; 2: p50<m_n<=p90; 3: m_n>p90 (p50/p90 from 2012-2020 MODIS-positive cells)"
    intervals["calibration_year"] = VAL_YEAR
    intervals["raw_quantile_coverage"] = coverage_report(y, lo_te, hi_te)["cqr_coverage"]
    log(f"  intervals={json.dumps(intervals)}")

    best_eb = base["eb_cell_ratio"]["rmse_log1p"]
    beats = bool(m_best["rmse_log1p"] < min(v["rmse_log1p"] for v in base.values()))
    log(f"  beats best baseline? {beats}  delta vs EB={m_best['rmse_log1p'] - best_eb:+.4f}")

    # ---- Back-cast 2000-2011 and build compact tiles for the app ----
    log(f"==== {country}: back-cast + tiles ====")
    pre = gm[gm.ym < 2012 * 12].copy()
    cells = hist_all_train[["gy", "gx"]]
    full_pre = cells.merge(pd.DataFrame({"ym": np.arange(YEARS_MODIS[0] * 12, 2012 * 12, dtype="int32")}), how="cross")
    dpre = full_pre.merge(pre, on=["gy", "gx", "ym"], how="outer")
    dpre = dpre.fillna({c: 0 for c in dpre.columns if c.startswith("m_") or c in ("frac_low_frp", "frac_off_nadir")})
    dpre = add_time_geo(dpre)
    dpre = finish_lags(dpre, gm)
    # Back-cast uses 2012-2021 history / ratios (standard for production back-cast)
    # but the *model weights* stay the 2012-2020 fit so CQR remains valid.
    dpre = add_model_features(attach_history(dpre, hist_all_train), mr_all, rg_all, k_best)
    dpre["v_equiv"] = apply_residual(best_model, dpre, bias_corr)
    lo_pre, hi_pre = interval_from_residual(dpre, lo_m, hi_m)
    strata_pre = stratum_id(dpre.m_n.to_numpy(dtype="float64"), edges)
    lo_pre_c, hi_pre_c, _ = mondrian_cqr(
        va.v_n.to_numpy(dtype="float64"), lo_va, hi_va, strata_va, lo_pre, hi_pre, strata_pre
    )
    dpre["lo"] = lo_pre_c
    dpre["hi"] = hi_pre_c
    dpre["v_n"] = np.nan
    dpre["source"] = "backcast"

    # Overlap + test years: observed VIIRS is the official harmonized value;
    # store the model prediction too for the metrics / disagreement views.
    post = add_model_features(attach_history(add_time_geo(df.copy()), hist_all_train), mr_all, rg_all, k_best)
    # df already has lags from build_overlap
    post["v_equiv"] = post["v_n"].astype("float64")  # observed VIIRS
    post["v_model"] = apply_residual(best_model, post, bias_corr)
    lo_post, hi_post = interval_from_residual(post, lo_m, hi_m)
    strata_post = stratum_id(post.m_n.to_numpy(dtype="float64"), edges)
    lo_post_c, hi_post_c, _ = mondrian_cqr(
        va.v_n.to_numpy(dtype="float64"), lo_va, hi_va, strata_va, lo_post, hi_post, strata_post
    )
    post["lo"] = lo_post_c
    post["hi"] = hi_post_c
    post["source"] = np.where(post.year.isin(TEST_YEARS), "observed_test", "observed")

    keep = [
        "gy", "gx", "lat", "lon", "year", "month", "ym",
        "m_n", "m_frp_sum", "m_frp_med", "m_night", "m_aqua", "m_bright",
        "m_pix", "frac_low_frp", "frac_off_nadir", "v_n", "v_equiv", "lo", "hi", "source",
    ]
    post = post.copy()
    if "v_model" not in post.columns:
        post["v_model"] = post["v_equiv"]
    # Compact: drop pure-zero rows (no MODIS, no VIIRS, tiny back-cast).
    pre_keep = dpre[(dpre.m_n > 0) | (dpre.v_equiv > 0.05)].copy()
    pre_keep["v_model"] = pre_keep["v_equiv"]
    post_keep = post[(post.m_n > 0) | (post.v_n > 0)].copy()
    tiles = pd.concat(
        [
            pre_keep[keep + ["v_model"]],
            post_keep[keep + ["v_model"]],
        ],
        ignore_index=True,
    )
    tiles["country"] = country
    for c in ("lat", "lon", "m_frp_sum", "m_frp_med", "m_night", "m_aqua", "m_bright", "m_pix", "frac_low_frp", "frac_off_nadir", "v_equiv", "lo", "hi", "v_model"):
        tiles[c] = tiles[c].astype("float32")
    tiles["m_n"] = tiles["m_n"].astype("int32")
    # v_n is nan on backcast
    tile_path = ART / f"tiles_{country.lower()}.parquet"
    tiles.to_parquet(tile_path, index=False)
    log(f"  tiles {tile_path.name}: {len(tiles):,} rows, {tile_path.stat().st_size/1e6:.1f} MB")

    # Country-level calendar (harmonized: backcast 2000-2011, observed VIIRS 2012+)
    cal = (
        tiles.groupby(["year", "month"], sort=True)
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
    # For 2012+ the 'lo'/'hi' bands belong to the *model*, not to observed VIIRS.
    # Expose both, but the calendar value is harmonized (observed after 2012).
    piv = cal.pivot(index="year", columns="month", values="harmonized").fillna(0)
    med = piv.median()
    mad = (piv - med).abs().median().replace(0, np.nan)
    z = 0.6745 * (piv - med) / mad
    flags = []
    z_rows = []
    for yy in z.index:
        for mm in z.columns:
            zz = z.loc[yy, mm]
            if zz == zz:
                z_rows.append({"year": int(yy), "month": int(mm), "robust_z": float(zz)})
                if abs(zz) > 3.5:
                    flags.append([int(yy), int(mm), round(float(zz), 4)])
    flags = sorted(flags, key=lambda f: -abs(f[2]))
    cal = cal.merge(pd.DataFrame(z_rows), on=["year", "month"], how="left")
    cal["unusual"] = cal["robust_z"].abs() > 3.5
    cal_path = ART / f"calendar_{country.lower()}.csv"
    cal.to_csv(cal_path, index=False)

    # Cell-level disagreement (overlap years, including test)
    overlap_tiles = tiles[tiles.source.isin(("observed", "observed_test"))]
    disagree = (
        overlap_tiles.groupby(["gy", "gx", "lat", "lon"], sort=False)
        .agg(
            m_n=("m_n", "sum"),
            v_n=("v_n", "sum"),
            frp_sum=("m_frp_sum", "sum"),
            night=("m_night", "mean"),
            aqua=("m_aqua", "mean"),
            frac_low_frp=("frac_low_frp", "mean"),
            frac_off_nadir=("frac_off_nadir", "mean"),
        )
        .reset_index()
    )
    disagree = disagree[(disagree.m_n + disagree.v_n) > 0]
    disagree["log2_ratio"] = np.log2((disagree.v_n + 1) / (disagree.m_n + 1)).astype("float32")
    disagree["country"] = country
    disagree_path = ART / f"disagreement_{country.lower()}.parquet"
    disagree.to_parquet(disagree_path, index=False)

    # Persist model
    model_path = MODEL_DIR / f"residual_{country.lower()}.txt"
    best_model.save_model(str(model_path))
    lo_m.save_model(str(MODEL_DIR / f"qlo_{country.lower()}.txt"))
    hi_m.save_model(str(MODEL_DIR / f"qhi_{country.lower()}.txt"))
    aux = dict(
        country=country,
        cell_deg=CELL,
        seed=SEED,
        k_best=k_best,
        bias_corr=bias_corr,
        rg_all=rg_all,
        mr_all={int(k): float(v) for k, v in mr_all.items()},
        edges=edges,
        feats=FEATS,
        note=NOTE,
    )
    with open(MODEL_DIR / f"aux_{country.lower()}.json", "w") as f:
        json.dump(aux, f, indent=2)

    elapsed = round(time.time() - t0, 1)
    result = {
        "country": country,
        "status": "ok",
        "note": NOTE,
        "seed": SEED,
        "cell_deg": CELL,
        "val_year": VAL_YEAR,
        "test_years": TEST_YEARS,
        "n_test_cell_months": int(len(test_b)),
        "global_ratio_value": rg_all,
        "eb_prior_strength_k": k_best,
        "baselines": base,
        "default_residual_test": m_default,
        "tuned_residual_test": m_best,
        "tuned_residual_val": m_val,
        "val_bias_correction_log": round(bias_corr, 6),
        "best_params": best_params,
        "best_iter": int(best_model.best_iteration or 0),
        "hpo_trials": N_TRIALS,
        "delta_rmse_log1p_vs_eb_cell_ratio": round(m_best["rmse_log1p"] - best_eb, 4),
        "beats_best_baseline_rmse_log1p": beats,
        "top_features_gain": [[k, round(float(v), 2)] for k, v in imp],
        "intervals": intervals,
        "calendar": {
            "years": [int(piv.index.min()), int(piv.index.max())],
            "backcast_years": [2000, 2011],
            "anomaly_rule": "robust z = 0.6745*(x-median)/MAD per calendar month, |z|>3.5. 2000-2011 are model back-casts (carry model error); 2012+ are observed VIIRS.",
            "n_flagged_months": len(flags),
            "flagged": flags[:16],
            "csv": cal_path.name,
        },
        "files": {
            "tiles": tile_path.name,
            "disagreement": disagree_path.name,
            "calendar": cal_path.name,
            "model": model_path.name,
        },
        "elapsed_s": elapsed,
    }
    with open(ART / f"metrics_{country.lower()}.json", "w") as f:
        json.dump(result, f, indent=2)

    # Flat comparison table
    rows = []
    for name, m in base.items():
        rows.append({"country": country, "method": f"baseline_{name}", **m})
    rows.append({"country": country, "method": "residual_lgbm_default", **m_default})
    rows.append({"country": country, "method": "residual_lgbm_tuned", **m_best})
    pd.DataFrame(rows).to_csv(ART / f"comparison_{country.lower()}.csv", index=False)
    log(f"==== {country} done in {elapsed}s  tuned_rmse={m_best['rmse_log1p']} eb={best_eb} beats={beats} ====")
    # Free big frames
    del df, train_all, test, tr_raw, va_raw, tr, va, te, dpre, post, tiles, gm, gv
    return result


def main() -> int:
    log(f"train_harmonizer v2  seed={SEED}  cell={CELL}  trials={N_TRIALS}  data={DATA_DIR}")
    log(f"note: {NOTE}")
    all_metrics = {
        "note": NOTE,
        "seed": SEED,
        "protocol": {
            "train_years": [2012, 2020],
            "val_year": VAL_YEAR,
            "test_years": TEST_YEARS,
            "cell_deg": CELL,
            "model": "LightGBM regression on log1p residual vs empirical-Bayes cell-ratio offset. No raw cell_v/cell_ratio/cell_m features.",
            "intervals": "quantile GBM on residual + Mondrian CQR stratified by contemporaneous MODIS count bins, calibrated on 2021.",
        },
        "colab_v1_reference": {
            "Canada": {
                "eb_cell_ratio_rmse_log1p": 0.3109,
                "tuned_lgbm_rmse_log1p": 0.3198,
                "tuned_lgbm_bias_pct": -63.4729,
                "tuned_lgbm_spearman": 0.3471,
                "no_cell_history_rmse_log1p": 0.2875,
                "cqr_coverage_active": 0.5912,
            },
            "Argentina": {
                "eb_cell_ratio_rmse_log1p": 0.5530,
                "tuned_lgbm_rmse_log1p": 0.4843,
                "tuned_lgbm_bias_pct": 11.0662,
                "cqr_coverage_active": 0.8229,
            },
        },
        "countries": {},
    }
    ok = True
    for c in COUNTRIES:
        try:
            all_metrics["countries"][c] = run_country(c)
        except Exception:
            ok = False
            log(f"FAILED {c}\n{traceback.format_exc()}")
            all_metrics["countries"][c] = {"status": "failed", "error": traceback.format_exc()[-2000:]}
    out = ART / "metrics.json"
    with open(out, "w") as f:
        json.dump(all_metrics, f, indent=2)
    # Combined comparison table
    frames = []
    for c in COUNTRIES:
        p = ART / f"comparison_{c.lower()}.csv"
        if p.exists():
            frames.append(pd.read_csv(p))
    if frames:
        pd.concat(frames, ignore_index=True).to_csv(ART / "comparison_table.csv", index=False)
    log(f"wrote {out}")
    # Print a short scoreboard
    print("\n======== SCOREBOARD (one seed, not a published benchmark) ========", flush=True)
    for c, r in all_metrics["countries"].items():
        if r.get("status") != "ok":
            print(f"{c}: FAILED", flush=True)
            continue
        eb = r["baselines"]["eb_cell_ratio"]
        tm = r["tuned_residual_test"]
        iv = r["intervals"]
        print(
            f"{c}: EB rmse={eb['rmse_log1p']} bias={eb['total_bias_pct']}%  |  "
            f"v2 residual RMSE={tm['rmse_log1p']} bias={tm['total_bias_pct']}% spearman={tm['spearman']}  |  "
            f"beats_EB={r['beats_best_baseline_rmse_log1p']}  "
            f"CQR overall={iv['cqr_coverage']} active={iv['cqr_coverage_on_viirs_active_cells']}",
            flush=True,
        )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
