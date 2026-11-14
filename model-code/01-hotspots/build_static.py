#!/usr/bin/env python3
"""Precompute the FastAPI responses into static files for a static (no-backend) deploy.
Output: /workspace/nasa-spaceapps/deploy/hotspots/ . Uses app.py functions directly, so numbers match the local API."""
import json, shutil, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import app as A

OUT = Path("/workspace/nasa-spaceapps/deploy/hotspots")
if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "data").mkdir(parents=True)
(OUT / "figs").mkdir()

def dump(obj, p):
    with open(p, "w") as f:
        json.dump(obj, f, separators=(",", ":"), default=lambda o: o.item() if hasattr(o, "item") else str(o))

dump(A.meta(), OUT / "data/meta.json")
for key, p in A.PRESETS.items():
    w, s, e, n = p["bbox"]
    cal = A.api_calendar(country=p["country"], west=w, south=s, east=e, north=n)
    dump(cal, OUT / f"data/calendar_{key}.json")
for c in ("Canada", "Argentina"):
    d = A.disagreement(c)
    d = d[(d.m_n + d.v_n) > 0]
    cols = ["lat", "lon", "m_n", "v_n", "log2_ratio", "frp_sum", "night", "aqua", "frac_low_frp", "frac_off_nadir"]
    dump({"country": c, "cells": d[cols].replace({np.nan: None}).to_dict(orient="records")}, OUT / f"data/disagreement_{c.lower()}.json")
    # Binary columnar tiles for client-side custom AOI (same math as app.calendar_from)
    t = A.tiles(c)
    src_code = t.source.map({"backcast": 0, "observed": 1, "observed_test": 2}).astype(np.uint8).values
    parts = [
        ("gx", t.gx.astype(np.int16).values), ("gy", t.gy.astype(np.int16).values),
        ("year", (t.year - 2000).astype(np.uint8).values), ("month", t.month.astype(np.uint8).values),
        ("source", src_code),
    ]
    for col in ("m_n", "v_n", "v_equiv", "lo", "hi", "v_model", "frac_low_frp", "m_night", "m_aqua"):
        parts.append((col, t[col].astype(np.float32).values))
    # order: float32 first for alignment
    parts.sort(key=lambda kv: -kv[1].dtype.itemsize)
    schema, off, buf = [], 0, bytearray()
    for name, arr in parts:
        b = arr.tobytes(); schema.append({"name": name, "dtype": str(arr.dtype), "offset": off}); buf += b; off += len(b)
    (OUT / f"data/tiles_{c.lower()}.bin").write_bytes(bytes(buf))
    dump({"n": int(len(t)), "cell_deg": 0.25, "lat": "gy*0.25+0.125", "lon": "gx*0.25+0.125", "source_codes": ["backcast", "observed", "observed_test"], "columns": schema}, OUT / f"data/tiles_{c.lower()}.json")
    assert np.allclose(t.lat.values, t.gy.values * 0.25 + 0.125) and np.allclose(t.lon.values, t.gx.values * 0.25 + 0.125)

for f in Path("static").iterdir():
    shutil.copy(f, OUT / f.name)
for i in range(1, 13):
    shutil.copy(f"/workspace/colab_queue/runs/01_nasa_firms_harmonization/fig_{i:02d}.png", OUT / f"figs/fig_{i:02d}.png")
for f in Path("screenshots").glob("*.png"):
    shutil.copy(f, OUT / "figs" / f.name)
print("built", OUT)

# ---- static deploy: shim, briefing deck, noindex ----
SH = Path("/workspace/nasa-spaceapps/apps/_shared")
for f in ("briefing.js", "briefing.css"):
    shutil.copy(SH / f, OUT / f)
for f in Path("static_deploy").iterdir():
    shutil.copy(f, OUT / f.name)
html = (OUT / "index.html").read_text()
html = html.replace('<meta charset="utf-8" />', '<meta charset="utf-8" />\n  <meta name="robots" content="noindex, nofollow" />', 1)
html = html.replace("— local demo</title>", "— NASA Space Apps demo</title>")
html = html.replace('<link rel="stylesheet" href="/style.css" />', '<link rel="stylesheet" href="/style.css" />\n  <link rel="stylesheet" href="/briefing.css" />')
html = html.replace('<button type="button" id="csvBtn" class="btn primary">Download CSV</button>',
    '<button type="button" id="csvBtn" class="btn primary">Download CSV</button>\n      <button type="button" class="bf-inline" data-briefing-open="1">▶ Experiment briefing</button>')
html = html.replace("Local NASA Space Apps demo.", "NASA Space Apps 2026 demo.")
html = html.replace("Local demo only — not a public deployment.", "Unlisted demo build (static, precomputed from the local model run).")
html = html.replace('<script src="/app.js"></script>', '<script src="/static_api.js"></script>\n  <script src="/app.js"></script>\n  <script src="/briefing.js"></script>\n  <script src="/briefing_content.js"></script>')
(OUT / "index.html").write_text(html)
shutil.copy("deploy_extra/extras.json", OUT / "data/extras.json")
shutil.copy("artifacts/metrics.json", OUT / "data/metrics_v2.json")
(OUT / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n")
(OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
print("static deploy ready")
