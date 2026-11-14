# Field Shift — local demo (Story County, Iowa)

Farmer-facing rotation explorer. Compares a current corn-soy rotation, a diversified small-grain/hay rotation, a cover-crop conservation rotation, and non-dominated sequences from a small NSGA-II search, scored against farmer-weighted priorities.

Live static build: https://nasa-spaceapps-2026.pages.dev/field-shift/app/

## Start

```bash
python3 /workspace/nasa-spaceapps/apps/03-field-shift/serve.py --host 127.0.0.1 --port 8030
```

Then open http://127.0.0.1:8030/

The page needs `data/app_data.json`, which is written by the model script.

## Rebuild the model and simulator

```bash
/workspace/nasa-spaceapps/venv/bin/python scripts/run_model.py
```

Uses only staged local data under `/workspace/nasa-spaceapps/data/adapting-farms-with-nasa-data/`. No network, no Colab, no changes to `/workspace/colab_queue/STATUS.md`.

## Honest scope

- Next-season LightGBM is trained on a sample of farmed 30 m pixels, temporal split train ≤ 2021 / val 2022–2023 / test 2024–2025. One seed, not a published benchmark.
- Indicators use FAO-56-style crop coefficients, NASADEM slope, MODIS bare-soil months, NASA POWER GDD/frost/heat and root-zone wetness. They are planning scores, not yield or ET forecasts.
- Cover-crop years assume winter rye (not a CDL class). SMAP / ECOSTRESS / GPM IMERG / GRACE are not included (Earthdata login).
- The tool supports, and does not replace, farmer judgment and local agronomy.

## Colab Full-County Run (2024–25)

The Model honesty tab also shows a larger personal-Colab CPU run, loaded from `data/colab_run/`:

- `results.json` — parsed metrics from `/workspace/colab_queue/runs/03_nasa_crop_rotation/all_output.txt`
- `crop_ablation.png`, `crop_confusion_calibration.png`, `crop_map.png` (aliases of `fig_01.png`–`fig_03.png`)

Headline numbers (seed 0, 25 trials, 66,666 test pixels): LightGBM **0.8176** accuracy / **0.5012** macro-F1 vs Markov-2 **0.8136** / **0.4633**. Temperature scaling slightly worsened test ECE **0.016 → 0.0351**. The 2025 full-county map is **0.811** pixel accuracy over 1,495,561 farmed pixels (30.2% disagreement). **One seed, not a published benchmark.** The local sample run on this machine is kept next to it and is also one seed.

## Licence

Original software: Apache-2.0. Dataset licences are listed on the Citations tab.
