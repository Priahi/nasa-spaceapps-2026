#!/usr/bin/env python3
"""Collect every real NASA-relevant result on the box into small JSON files the briefing decks read.
Parsed programmatically where the source is machine-readable; prose sources are transcribed with the
exact source path and the quoted source line, so every number is traceable."""
import json, re, shutil
from pathlib import Path

APPS = Path("/workspace/nasa-spaceapps/apps")
CQ = Path("/workspace/colab_queue/runs")

def result_lines(path):
    out = {}
    for line in Path(path).read_text(errors="ignore").splitlines():
        m = re.match(r"^RESULT_([A-Z0-9_]+) (\{.*\})\s*$", line)
        if m:
            out[m.group(1)] = json.loads(m.group(2))
    return out

def quote(path, needle):
    for line in Path(path).read_text().splitlines():
        if needle in line:
            return line.strip()
    raise SystemExit(f"quote not found in {path}: {needle}")

GPU = "/workspace/colab_gpu/GPU_RESULTS_ALL.md"
BOX = "/workspace/research_plan/BOX_PROGRESS.md"
PLAN = "/workspace/nasa-spaceapps/PLAN.md"
R2 = json.load(open("/workspace/colab_hpo/round2_personal/results.json"))

# ---- 01 Hot Spots ----
v1 = result_lines(CQ / "01_nasa_firms_harmonization/all_output.txt")
v1["source"] = str(CQ / "01_nasa_firms_harmonization/all_output.txt")
hs = {
    "firms_v1_colab": v1,
    "e2_burn_scars": {
        "source": GPU, "quote": quote(GPU, "E2 burn scars"),
        "data": "NASA HLS Burn Scars (Harmonized Landsat Sentinel-2)", "model": "TinyUNet (Prithvi not loaded)",
        "n_train_scenes": 32, "n_val_scenes": 8, "steps": 250,
        "model_miou": 0.6084, "model_burn_iou": 0.3657, "baseline": "all-unburned", "baseline_miou": 0.4234, "baseline_burn_iou": 0.0,
    },
    "e10_cpu_speed": {
        "source": BOX, "quote": quote(BOX, "- E10: ONNX FP32 8.8 ms"),
        "what": "CPU retrain of the E2 TinyUNet, not the Colab weights",
        "onnx_fp32_ms": 8.8, "pytorch_ms": 49.56, "onnx_int8_ms": 23.67, "miou_fp32": 0.4746, "miou_int8": 0.4745,
    },
    "plan_box_prototype": {
        "source": PLAN, "quote": quote(PLAN, "Smoke test (box CPU, Canada, 2012-2015"),
        "rows": [["Global ratio (3.84×)", 1.100, 0.432, 33.3], ["Per-month ratio", 0.969, 0.434, 15.7], ["LightGBM Poisson, 50 rounds, no tuning", 0.968, 0.452, -39.6]],
        "note": "Box CPU, Canada 2012-2015 subsample, test year 2015, one seed. Too small to conclude anything.",
    },
}
# ---- 02 SAR ----
sar = {
    "e8_first_attempt": {
        "source": GPU, "quote": quote(GPU, "E8 Sen1Floods11 (official"),
        "n_train": 252, "n_val": 89, "model": "TinyUNet w32 d2", "steps": 400, "crop": 128,
        "model_miou": 0.5647, "model_water_iou": 0.2268, "baseline": "all-dry", "baseline_miou": 0.5122, "baseline_water_iou_as_recorded": 0.1348,
    },
    "plan_box_prototype": {
        "source": PLAN, "quote": quote(PLAN, "Smoke test (box CPU, 12 train/val/test chips"),
        "otsu_water_iou": 0.190, "unet_water_iou": 0.453, "cpu_s_per_512_tile": 0.08,
        "note": "12 train/val/test chips, 1 epoch, one seed. Untrained-scale prototype.",
    },
    "r17_oscd_change": {k: R2["R17"][k] for k in ("dataset", "licence", "seed", "epochs", "n_train", "n_select", "n_test", "chosen_config", "test_f1", "difference_test_f1", "no_change_f1", "cities")},
    "e5_oscd_lora": {
        "source": GPU, "quote": quote(GPU, "E5 OSCD change detection"),
        "lora_f1": 0.0844, "lora_precision": 0.0867, "lora_recall": 0.0823, "lora_off_linear_f1": 0.1058, "train_crops": 40, "val_crops": 24, "steps": 80,
    },
}
sar["r17_oscd_change"]["source"] = "/workspace/colab_hpo/round2_personal/results.json"
# ---- 03 Field Shift ----
fs = {
    "r16_eurosat_croptype": {k: R2["R16"][k] for k in ("dataset", "licence", "classes", "seed", "epochs", "n_train", "n_select", "n_test", "baseline_accuracy", "chosen_config", "test_accuracy")},
    "plan_box_prototype": {
        "source": PLAN, "quote": quote(PLAN, "Smoke test (box CPU, 20k pixels"),
        "rows": [["Persistence", 0.348, 0.355], ["Corn/soy alternation", 0.705, 0.508], ["Markov-2 table", 0.817, 0.509], ["LightGBM, 60 rounds, no tuning", 0.824, 0.499]],
        "note": "Box CPU, 20k pixels, test year 2020, one seed.",
    },
}
fs["r16_eurosat_croptype"]["source"] = "/workspace/colab_hpo/round2_personal/results.json"

def write(app_dir, obj, figs=()):
    d = APPS / app_dir / "deploy_extra"
    d.mkdir(exist_ok=True)
    (d / "extras.json").write_text(json.dumps(obj, indent=1))
    fd = d / "figs"; fd.mkdir(exist_ok=True)
    for src, name in figs:
        shutil.copy(src, fd / name)

PNG = Path("/workspace/colab_hpo/round2_personal/pngs")
write("01-hotspots", hs)
write("02-sar-change", sar, [(PNG / "r17_examples.png", "r17_examples.png"), (PNG / "r17_metrics.png", "r17_metrics.png")])
write("03-field-shift", fs, [(PNG / "r16_examples.png", "r16_examples.png"), (PNG / "r16_metrics.png", "r16_metrics.png")])
print("v1 tags:", sorted(k for k in v1 if k != "source"))
print("ok")
