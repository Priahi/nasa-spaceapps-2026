# FIRMS Hot Spots Harmonizer (local demo)

Local-only NASA Space Apps prep for **Harmonization of MODIS and VIIRS Hot Spots**.
Live static build: https://nasa-spaceapps-2026.pages.dev/hotspots/app/

Every metric in this folder is **one seed, not a published benchmark**.

## What's in here

- `train_harmonizer.py` — v2 residual LightGBM on top of an empirical-Bayes cell-ratio baseline. No raw `cell_v` / `cell_ratio` / `cell_m` features (the leak that made the Colab v1 Canada model lose to the simple baseline on 2023-2025). Mondrian CQR intervals, stratified by contemporaneous MODIS count.
- `app.py` — FastAPI + static Leaflet map, AOI box / presets, 2000-2025 calendar, metrics, CSV export.
- `artifacts/` — metrics JSON, comparison tables, compact cell-month parquet tiles, calendars, models.
- `screenshots/` — Playwright smoke-test captures.

Data used: NASA FIRMS country archives already staged at
`/workspace/nasa-spaceapps/data/modis-and-viirs-hot-spots/firms_country/`
(MODIS C6.1 2000-2025 and VIIRS S-NPP 2012-2025, Canada and Argentina).

## Train (box CPU)

```bash
/workspace/nasa-spaceapps/venv/bin/python -u /workspace/nasa-spaceapps/apps/01-hotspots/train_harmonizer.py
```

## Run the local app

```bash
cd /workspace/nasa-spaceapps/apps/01-hotspots
/workspace/nasa-spaceapps/venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765/

## Smoke test

```bash
python3 /workspace/nasa-spaceapps/apps/01-hotspots/smoke_test.py --base http://127.0.0.1:8765
```

## Licence and citation

Apache-2.0 for this tool and model code. NASA FIRMS data has no restriction on use; cite FIRMS:
https://firms.modaps.eosdis.nasa.gov/
