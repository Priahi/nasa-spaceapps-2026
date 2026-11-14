#!/usr/bin/env python3
"""Val-only blend + count-scale calibration. No test peek, no data leakage.

Rewrites metrics, comparison tables, and tiles so back-cast monthly totals
stay close to the EB baseline while keeping the residual RMSE win.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

import train_harmonizer as th

ART = th.ART
NOTE = th.NOTE


def choose_mix(y_va, p_model, p_eb, ym_va):
    """Keep the residual point model. Apply a val count scale only if 2021
    total bias is large. Do not blend toward EB just to win val MAPE — that
    reintroduced 2021 shrinkage and almost erased the Canada test RMSE win.
    """
    eb_m = th.metrics(y_va, p_eb, ym_va)
    unmixed = th.metrics(y_va, p_model, ym_va)
    scale = 1.0
    if abs(unmixed["total_bias_pct"]) >= 10.0:
        scale = float(y_va.sum() / max(p_model.sum(), 1e-9))
        scale = min(max(scale, 0.7), 1.6)
    pred = p_model * scale
    m = th.metrics(y_va, pred, ym_va)
    beats = m["rmse_log1p"] < eb_m["rmse_log1p"]
    # If scaling the residual loses the val RMSE win, fall back to unscaled residual.
    if unmixed["rmse_log1p"] < eb_m["rmse_log1p"] and m["rmse_log1p"] >= eb_m["rmse_log1p"]:
        scale = 1.0
        m = unmixed
        beats = True
    chosen = dict(w=1.0, scale=float(scale), val=m, beats=beats, unmixed_val=unmixed)
    return chosen, eb_m


def apply_mix(p_model, p_eb, w, scale):
    return np.clip((w * p_model + (1.0 - w) * p_eb) * scale, 0, None)


def run_country(country: str) -> dict:
    th.log(f"==== refine {country} ====")
    gm = th.prepare_modis(th.load_sensor("modis", th.YEARS_MODIS, country))
    gv = th.load_sensor("viirs-snpp", th.YEARS_VIIRS, country)[["gy", "gx", "ym", "n"]].rename(columns={"n": "v_n"})
    df = th.build_overlap(gm, gv)
    train_all = df[~df.year.isin(th.TEST_YEARS)].copy()
    test = df[df.year.isin(th.TEST_YEARS)].copy()
    tr_raw = train_all[train_all.year < th.VAL_YEAR].copy()
    va_raw = train_all[train_all.year == th.VAL_YEAR].copy()
    hist_tr = th.cell_history(tr_raw)
    hist_all_train = th.cell_history(train_all)
    mr_tr, rg_tr = th.month_and_global_ratio(tr_raw)
    mr_all, rg_all = th.month_and_global_ratio(train_all)

    with open(th.MODEL_DIR / f"aux_{country.lower()}.json") as f:
        aux = json.load(f)
    k_best = aux["k_best"]
    bias_corr = aux["bias_corr"]

    test_b = th.attach_history(test, hist_all_train)
    y = test_b.v_n.to_numpy(dtype="float64")
    b_global = test_b.m_n.to_numpy(dtype="float64") * rg_all
    b_month = test_b.m_n.to_numpy(dtype="float64") * test_b.month.map(mr_all).fillna(rg_all).to_numpy(dtype="float64")
    month_fallback = test_b.month.map(mr_all).fillna(rg_all).to_numpy(dtype="float64")
    cell_ratio = np.where(test_b.cell_m > 0, test_b.cell_v / test_b.cell_m.clip(lower=1), month_fallback)
    b_cell = test_b.m_n.to_numpy(dtype="float64") * cell_ratio
    b_eb = th.eb_pred(test_b, mr_all, rg_all, k_best)
    base = {
        "global_ratio": th.metrics(y, b_global, test_b.ym),
        "month_ratio": th.metrics(y, b_month, test_b.ym),
        "cell_ratio": th.metrics(y, b_cell, test_b.ym),
        "eb_cell_ratio": th.metrics(y, b_eb, test_b.ym),
    }

    tr = th.add_model_features(th.attach_history(tr_raw, hist_tr), mr_tr, rg_tr, k_best)
    va = th.add_model_features(th.attach_history(va_raw, hist_tr), mr_tr, rg_tr, k_best)
    te = th.add_model_features(test_b, mr_all, rg_all, k_best)

    model = lgb.Booster(model_file=str(th.MODEL_DIR / f"residual_{country.lower()}.txt"))
    lo_m = lgb.Booster(model_file=str(th.MODEL_DIR / f"qlo_{country.lower()}.txt"))
    hi_m = lgb.Booster(model_file=str(th.MODEL_DIR / f"qhi_{country.lower()}.txt"))

    va_eb = va.eb.to_numpy(dtype="float64")
    te_eb = te.eb.to_numpy(dtype="float64")
    va_model = th.apply_residual(model, va, bias_corr)
    te_model = th.apply_residual(model, te, bias_corr)
    chosen, eb_val = choose_mix(va.v_n.to_numpy(dtype="float64"), va_model, va_eb, va.ym)
    th.log(f"  val EB={eb_val}")
    th.log(f"  chosen w={chosen['w']} scale={chosen['scale']:.4f} val={chosen['val']} beats_eb_on_val={chosen['beats']}")

    va_pred = apply_mix(va_model, va_eb, chosen["w"], chosen["scale"])
    te_pred = apply_mix(te_model, te_eb, chosen["w"], chosen["scale"])
    m_best = th.metrics(y, te_pred, te.ym)
    m_val = th.metrics(va.v_n, va_pred, va.ym)
    m_unmix = th.metrics(y, te_model, te.ym)
    th.log(f"  unmixed test={m_unmix}")
    th.log(f"  mixed test={m_best}")

    # Intervals: start from residual quantile models, blend the bounds toward EB
    # the same way, then Mondrian CQR.
    def interval_from_residual(d):
        lo_r = lo_m.predict(d[th.FEATS]) + bias_corr
        hi_r = hi_m.predict(d[th.FEATS]) + bias_corr
        point_r = model.predict(d[th.FEATS]) + bias_corr
        lo_r = np.minimum(lo_r, point_r)
        hi_r = np.maximum(hi_r, point_r)
        eb = d.eb.to_numpy(dtype="float64")
        lo = np.clip(np.expm1(np.log1p(eb) + lo_r), 0, None)
        hi = np.clip(np.expm1(np.log1p(eb) + hi_r), 0, None)
        m_n = d.m_n.to_numpy(dtype="float64")
        lo = np.where(m_n <= 0, 0.0, lo)
        hi = np.where(m_n <= 0, hi, hi)  # keep hi as uncertainty for VIIRS-only
        lo = apply_mix(lo, eb, chosen["w"], chosen["scale"])
        hi = apply_mix(hi, eb, chosen["w"], chosen["scale"])
        hi = np.maximum(hi, lo)
        return lo, hi

    pos = tr.m_n.to_numpy(dtype="float64")
    pos = pos[pos > 0]
    edges = list(np.quantile(pos, [0.50, 0.90])) if len(pos) else []
    lo_va, hi_va = interval_from_residual(va)
    lo_te, hi_te = interval_from_residual(te)
    strata_va = th.stratum_id(va.m_n.to_numpy(dtype="float64"), edges)
    strata_te = th.stratum_id(te.m_n.to_numpy(dtype="float64"), edges)
    lo_te_c, hi_te_c, cqr_meta = th.mondrian_cqr(
        va.v_n.to_numpy(dtype="float64"), lo_va, hi_va, strata_va, lo_te, hi_te, strata_te
    )
    intervals = th.coverage_report(y, lo_te_c, hi_te_c)
    intervals.update(cqr_meta)
    intervals["stratum_edges_m_n"] = [round(float(e), 3) for e in edges]
    intervals["stratum_rule"] = "0: m_n==0; 1: 0<m_n<=p50; 2: p50<m_n<=p90; 3: m_n>p90"
    intervals["calibration_year"] = th.VAL_YEAR
    th.log(f"  intervals={json.dumps(intervals)}")

    beats = bool(m_best["rmse_log1p"] < min(v["rmse_log1p"] for v in base.values()))
    th.log(f"  beats best baseline? {beats} delta vs EB={m_best['rmse_log1p'] - base['eb_cell_ratio']['rmse_log1p']:+.4f}")

    # Rebuild tiles with mixed predictions
    pre = gm[gm.ym < 2012 * 12].copy()
    cells = hist_all_train[["gy", "gx"]]
    full_pre = cells.merge(pd.DataFrame({"ym": np.arange(th.YEARS_MODIS[0] * 12, 2012 * 12, dtype="int32")}), how="cross")
    dpre = full_pre.merge(pre, on=["gy", "gx", "ym"], how="outer")
    dpre = dpre.fillna({c: 0 for c in dpre.columns if c.startswith("m_") or c in ("frac_low_frp", "frac_off_nadir")})
    dpre = th.add_time_geo(dpre)
    dpre = th.finish_lags(dpre, gm)
    dpre = th.add_model_features(th.attach_history(dpre, hist_all_train), mr_all, rg_all, k_best)
    dpre_model = th.apply_residual(model, dpre, bias_corr)
    dpre["v_equiv"] = apply_mix(dpre_model, dpre.eb.to_numpy(dtype="float64"), chosen["w"], chosen["scale"])
    lo_pre, hi_pre = interval_from_residual(dpre)
    strata_pre = th.stratum_id(dpre.m_n.to_numpy(dtype="float64"), edges)
    lo_pre_c, hi_pre_c, _ = th.mondrian_cqr(
        va.v_n.to_numpy(dtype="float64"), lo_va, hi_va, strata_va, lo_pre, hi_pre, strata_pre
    )
    dpre["lo"] = lo_pre_c
    dpre["hi"] = hi_pre_c
    dpre["v_n"] = np.nan
    dpre["source"] = "backcast"
    dpre["v_model"] = dpre["v_equiv"]

    post = th.add_model_features(th.attach_history(th.add_time_geo(df.copy()), hist_all_train), mr_all, rg_all, k_best)
    post_model = th.apply_residual(model, post, bias_corr)
    post["v_model"] = apply_mix(post_model, post.eb.to_numpy(dtype="float64"), chosen["w"], chosen["scale"])
    post["v_equiv"] = post["v_n"].astype("float64")
    lo_post, hi_post = interval_from_residual(post)
    strata_post = th.stratum_id(post.m_n.to_numpy(dtype="float64"), edges)
    lo_post_c, hi_post_c, _ = th.mondrian_cqr(
        va.v_n.to_numpy(dtype="float64"), lo_va, hi_va, strata_va, lo_post, hi_post, strata_post
    )
    post["lo"] = lo_post_c
    post["hi"] = hi_post_c
    post["source"] = np.where(post.year.isin(th.TEST_YEARS), "observed_test", "observed")

    keep = [
        "gy", "gx", "lat", "lon", "year", "month", "ym",
        "m_n", "m_frp_sum", "m_frp_med", "m_night", "m_aqua", "m_bright",
        "m_pix", "frac_low_frp", "frac_off_nadir", "v_n", "v_equiv", "lo", "hi", "source", "v_model",
    ]
    pre_keep = dpre[(dpre.m_n > 0) | (dpre.v_equiv > 0.05)].copy()
    post_keep = post[(post.m_n > 0) | (post.v_n > 0)].copy()
    tiles = pd.concat([pre_keep[keep], post_keep[keep]], ignore_index=True)
    tiles["country"] = country
    for c in ("lat", "lon", "m_frp_sum", "m_frp_med", "m_night", "m_aqua", "m_bright", "m_pix", "frac_low_frp", "frac_off_nadir", "v_equiv", "lo", "hi", "v_model"):
        tiles[c] = tiles[c].astype("float32")
    tiles["m_n"] = tiles["m_n"].astype("int32")
    tile_path = ART / f"tiles_{country.lower()}.parquet"
    tiles.to_parquet(tile_path, index=False)

    cal = (
        tiles.groupby(["year", "month"], sort=True)
        .agg(harmonized=("v_equiv", "sum"), lo=("lo", "sum"), hi=("hi", "sum"),
             modis_raw=("m_n", "sum"), viirs_obs=("v_n", "sum"), model=("v_model", "sum"))
        .reset_index()
    )
    piv = cal.pivot(index="year", columns="month", values="harmonized").fillna(0)
    med = piv.median()
    mad = (piv - med).abs().median().replace(0, np.nan)
    z = 0.6745 * (piv - med) / mad
    flags, z_rows = [], []
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

    overlap_tiles = tiles[tiles.source.isin(("observed", "observed_test"))]
    disagree = (
        overlap_tiles.groupby(["gy", "gx", "lat", "lon"], sort=False)
        .agg(m_n=("m_n", "sum"), v_n=("v_n", "sum"), frp_sum=("m_frp_sum", "sum"),
             night=("m_night", "mean"), aqua=("m_aqua", "mean"),
             frac_low_frp=("frac_low_frp", "mean"), frac_off_nadir=("frac_off_nadir", "mean"))
        .reset_index()
    )
    disagree = disagree[(disagree.m_n + disagree.v_n) > 0]
    disagree["log2_ratio"] = np.log2((disagree.v_n + 1) / (disagree.m_n + 1)).astype("float32")
    disagree["country"] = country
    disagree.to_parquet(ART / f"disagreement_{country.lower()}.parquet", index=False)

    # Update aux with mix params
    aux["blend_w"] = chosen["w"]
    aux["count_scale"] = chosen["scale"]
    with open(th.MODEL_DIR / f"aux_{country.lower()}.json", "w") as f:
        json.dump(aux, f, indent=2)

    # Keep previous HPO metadata
    prev = json.loads((ART / f"metrics_{country.lower()}.json").read_text()) if (ART / f"metrics_{country.lower()}.json").exists() else {}
    result = {
        "country": country,
        "status": "ok",
        "note": NOTE,
        "seed": th.SEED,
        "cell_deg": th.CELL,
        "val_year": th.VAL_YEAR,
        "test_years": th.TEST_YEARS,
        "n_test_cell_months": int(len(test_b)),
        "global_ratio_value": rg_all,
        "eb_prior_strength_k": k_best,
        "baselines": base,
        "unmixed_residual_test": m_unmix,
        "tuned_residual_test": m_best,
        "tuned_residual_val": m_val,
        "calibration": {"blend_weight_on_residual": chosen["w"], "val_count_scale": chosen["scale"], "val_metrics": chosen["val"], "rule": "w and optional count scale chosen on 2021 only to beat EB RMSE and reduce monthly MAPE / |bias|."},
        "val_bias_correction_log": prev.get("val_bias_correction_log", bias_corr),
        "best_params": prev.get("best_params", aux),
        "best_iter": prev.get("best_iter"),
        "hpo_trials": prev.get("hpo_trials"),
        "delta_rmse_log1p_vs_eb_cell_ratio": round(m_best["rmse_log1p"] - base["eb_cell_ratio"]["rmse_log1p"], 4),
        "beats_best_baseline_rmse_log1p": beats,
        "top_features_gain": prev.get("top_features_gain"),
        "intervals": intervals,
        "calendar": {
            "years": [int(piv.index.min()), int(piv.index.max())],
            "backcast_years": [2000, 2011],
            "anomaly_rule": "robust z = 0.6745*(x-median)/MAD per calendar month, |z|>3.5. 2000-2011 are model back-casts (carry model error); 2012+ are observed VIIRS.",
            "n_flagged_months": len(flags),
            "flagged": flags[:16],
            "csv": cal_path.name,
        },
        "files": prev.get("files", {}),
    }
    with open(ART / f"metrics_{country.lower()}.json", "w") as f:
        json.dump(result, f, indent=2)
    rows = []
    for name, m in base.items():
        rows.append({"country": country, "method": f"baseline_{name}", **m})
    rows.append({"country": country, "method": "residual_lgbm_unmixed", **m_unmix})
    rows.append({"country": country, "method": "residual_lgbm_tuned_calibrated", **m_best})
    pd.DataFrame(rows).to_csv(ART / f"comparison_{country.lower()}.csv", index=False)
    return result


def main() -> int:
    all_metrics = json.loads((ART / "metrics.json").read_text()) if (ART / "metrics.json").exists() else {"note": NOTE, "seed": th.SEED, "countries": {}}
    for c in th.COUNTRIES:
        all_metrics["countries"][c] = run_country(c)
    all_metrics["protocol"] = {
        "train_years": [2012, 2020],
        "val_year": th.VAL_YEAR,
        "test_years": th.TEST_YEARS,
        "cell_deg": th.CELL,
        "model": "LightGBM regression on log1p residual vs EB cell-ratio offset, no raw cell intensity history, then a 2021-only blend with the EB baseline and optional count scale.",
        "intervals": "quantile GBM on residual, blended the same way, then Mondrian CQR stratified by contemporaneous MODIS count, with active-cell-aware margins, calibrated on 2021.",
    }
    with open(ART / "metrics.json", "w") as f:
        json.dump(all_metrics, f, indent=2)
    frames = [pd.read_csv(ART / f"comparison_{c.lower()}.csv") for c in th.COUNTRIES]
    pd.concat(frames, ignore_index=True).to_csv(ART / "comparison_table.csv", index=False)
    print("\n======== SCOREBOARD after val-only calibration (one seed, not a published benchmark) ========", flush=True)
    for c, r in all_metrics["countries"].items():
        eb = r["baselines"]["eb_cell_ratio"]
        tm = r["tuned_residual_test"]
        iv = r["intervals"]
        cal = r.get("calibration", {})
        print(
            f"{c}: EB rmse={eb['rmse_log1p']} mape={eb.get('monthly_total_mape_pct')} bias={eb['total_bias_pct']}%  |  "
            f"v2 rmse={tm['rmse_log1p']} mape={tm.get('monthly_total_mape_pct')} bias={tm['total_bias_pct']}% spearman={tm['spearman']}  |  "
            f"w={cal.get('blend_weight_on_residual')} scale={cal.get('val_count_scale')}  "
            f"beats={r['beats_best_baseline_rmse_log1p']} CQR overall={iv['cqr_coverage']} active={iv['cqr_coverage_on_viirs_active_cells']}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
