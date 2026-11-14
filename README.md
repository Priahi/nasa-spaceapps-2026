# Orbit to Ground: an Earth-change intelligence pipeline, from orbit to decision

NASA Space Apps Challenge 2026 · **Be An Earth System Trend Detective!** · built solo by Parsa Riahi, Toronto

- Live site: **https://nasa-spaceapps-2026.pages.dev**
- Demo video (29 s): https://nasa-spaceapps-2026.pages.dev/submission/demo.mp4 · Slides: https://nasa-spaceapps-2026.pages.dev/submission/deck.pdf

## Why

Satellites already see fast Earth change, but the evidence rarely reaches a decision intact. Fire records are split across sensors (MODIS, then VIIRS from 2012), so long fire trends can't be trusted as-is. Optical satellites go blind under the storm clouds that cause floods. And the people choosing what to plant next year rarely get the land's history in a usable form. Real stakes, from public sources: 14.6 Mha of Canadian forest burned in 2023 (Natural Resources Canada); 230 deaths in the October–November 2024 DANA floods in Spain (Government of Spain); about a third of the world's land is moderately to highly degraded (FAO, 2015).

## What

One pipeline with three working modules and a shared trend layer:

| Step | Module | What it does | Page | Live tool |
|---|---|---|---|---|
| 01 Detect | Hot Spots Harmonizer | One consistent 2000–2025 fire record from MODIS + VIIRS, with calibrated uncertainty and unusual-month flags | [/hotspots/](https://nasa-spaceapps-2026.pages.dev/hotspots/) | [/hotspots/app/](https://nasa-spaceapps-2026.pages.dev/hotspots/app/) |
| 02 Confirm | SAR Change | Flood water through cloud and night from Sentinel-1 radar (NISAR-ready), Valencia 2024 | [/sar-change/](https://nasa-spaceapps-2026.pages.dev/sar-change/) | [/sar-change/app/](https://nasa-spaceapps-2026.pages.dev/sar-change/app/) |
| 03 Adapt | Field Shift | Next-season crop prediction and 36 ranked four-year rotation plans for Story County, Iowa | [/field-shift/](https://nasa-spaceapps-2026.pages.dev/field-shift/) | [/field-shift/app/](https://nasa-spaceapps-2026.pages.dev/field-shift/app/) |
| 04 Measure | Trend layer | What is changing, where, how much, and is it significant: Mann-Kendall + Sen's slope on 23–45-year NASA records, cross-checked across datasets | [/#trends](https://nasa-spaceapps-2026.pages.dev/#trends) | in each module page |

## How

- **Data:** NASA FIRMS (MODIS, VIIRS), NASA POWER, Sentinel-1 RTC, Sen1Floods11, NISAR metadata/browse, NASADEM, MODIS NDVI, USDA CDL, SoilGrids; with an Earthdata login: GRACE/GRACE-FO mascons, GPM IMERG, GLDAS, SMAP, OPERA DSWx-S1, MODIS MCD64A1 and HLS. Provenance: [`earthdata/EARTHDATA.md`](earthdata/EARTHDATA.md), [`trends/RESULTS.md`](trends/RESULTS.md), `model-code/PROVENANCE-*.md`.
- **Methods:** empirical-Bayes + LightGBM sensor harmonization with conformal intervals; U-Net on Sen1Floods11 vs Otsu; LightGBM next-season crop model + FAO-56 water demand + NSGA-II rotation search; Mann-Kendall (with Hamed-Rao check) and Sen's slope with 95% CI at α = 0.05.
- **Validation and limits:** time-split held-out tests against baselines (one seed each, not a published benchmark); honest misses are reported on the site. Trends show change, not cause; where datasets disagree (e.g. MERRA-2 vs GPM IMERG over southern Ontario) we say so.
- **Provenance of the work:** the three tools build on our own earlier code and open-source libraries and were developed before the event; the trend layer and the Earthdata upgrades were computed during the event on 14 Nov 2026.

Raw satellite downloads are not committed (see `.gitignore`); the fetch scripts in `trends/`, `earthdata/` and `upgrades/` re-create them. Earthdata scripts read credentials from `~/.netrc` or `EARTHDATA_USERNAME` / `EARTHDATA_PASSWORD`; nothing secret is stored here.

## Layout

- `src/` — site generator (`build.py`), copy and numbers (`content.py`), CSS/JS, fonts, images, demo theme overrides.
- `demos/` — static builds of the three interactive demos (copied into `dist/<slug>/app/` at build time).
- `model-code/` — the training, tiling and modelling code behind the demos, plus data provenance notes. Paths inside point at the original workstation layout; adjust `DATA_DIR`-style paths to run elsewhere.
- `trends/`, `earthdata/`, `upgrades/` — trend analysis and Earthdata upgrade scripts with their small outputs (JSON/PNG).
- `submission/` — deck, demo video, captions and form text.
- `tools/` — asset capture (`capture_assets.mjs`, `make_images.py`) and headless verification (`verify.mjs`).

## Build and deploy

```bash
python3 src/build.py                     # writes dist/
npx wrangler pages deploy dist --project-name nasa-spaceapps-2026 --branch main
node tools/verify.mjs https://nasa-spaceapps-2026.pages.dev shots live   # Playwright: status, console errors, screenshots
```

## Motion and design

GSAP + ScrollTrigger reveals (`data-fx="rise|stagger|wipe|parallax"`), Lenis smooth scroll on fine pointers, Magic UI-style border beam and spotlight cards, generated contour-line accents, Geist type. Honors `prefers-reduced-motion`.

## Data and credits

NASA FIRMS (MODIS C6.1 MCD14ML, VIIRS S-NPP VNP14IMG); NASA-ISRO NISAR L2 GCOV metadata (NASA CMR) and browse images (ASF DAAC); NASA POWER; NASADEM (LP DAAC); MODIS MOD13Q1 NDVI; ESA Copernicus Sentinel-1 RTC (via Microsoft Planetary Computer); Sen1Floods11 (CC-BY-4.0, Bonafilia et al. 2020); JRC Global Surface Water; USDA NASS Cropland Data Layer; ISRIC SoilGrids (CC-BY-4.0). Basemap tiles © Esri via Leaflet. GSAP (standard no-charge licence), Lenis (MIT), Geist fonts (SIL OFL).

Not affiliated with or endorsed by NASA.

## Honesty notes

- Every metric is one seed and not a published benchmark. Negative results (for example worse monthly-total error for Hot Spots, and worse calibration after temperature scaling for Field Shift) are shown next to the wins.
- AI disclosure: AI coding assistants helped write and refactor parts of the code, site and text. All models, metrics and figures come from our own runs on the public data listed.
- Includes pre-existing tooling, disclosed.

## Licence

Code: Apache-2.0 (see `LICENSE`). Data remain under their providers' terms.
