# Dancing with the SARs — local demo

Interactive radar viewer for the 29 October 2024 DANA flood in Valencia, Spain. Built from staged, real Sentinel-1 RTC GeoTIFFs, Sen1Floods11 hand-labelled chips, and public NISAR GCOV browse PNGs.

Live static build: https://nasa-spaceapps-2026.pages.dev/sar-change/app/

## Start

```bash
python3 /workspace/nasa-spaceapps/apps/02-sar-change/serve.py --host 127.0.0.1 --port 8020
```

Then open http://127.0.0.1:8020/

## What is in here

- Before/after swipe and a same-orbit time-lapse of Sentinel-1 RTC (VV, VH, and a VV/VH false-color product). Color stretch is shared within each orbit so the time-lapse does not flicker.
- A VV dB change map for three same-track pairs that bracket the flood.
- Sen1Floods11 official test chips with hand-label, Otsu, and JRC overlays.
- A physics panel on VV/VH, dielectric/roughness, and why NISAR L-band can see inundation under a canopy where C-band fails. Honest about dates: NISAR browses are 2025–2026, not images of the 2024 flood.
- Metrics from Colab attempt 1 (one seed, not a published benchmark). ONNX weights were not saved when the free T4 runtime ended.
- CLI hooks for Saturday: `plugins/infer.py` and `plugins/nisar_h5.py`.

## Rebuild tiles

```bash
/workspace/nasa-spaceapps/venv/bin/python scripts/render_tiles.py
```

## Licence

Original software: Apache-2.0. Dataset licences are listed on the Citations tab.
