#!/usr/bin/env python3
"""Saturday hook: run the trained Sen1Floods11 U-Net ONNX weights on a VV/VH tile.

This demo ships WITHOUT the trained weights (the Colab T4 session ended before
ONNX export was saved). Drop the file in and run:

    python plugins/infer.py --onnx /path/to/unet_vv_vh_ratio.onnx \\
        --vv vv.tif --vh vh.tif --out pred.png

Expected ONNX input
    name: input
    shape: [1, 3, H, W]  float32
    channels: [VV_dB, VH_dB, (VV_dB - VH_dB)]  (or [VV] / [VV, VH]
               depending on the ablation that is shipped)
    values: already in dB, no further normalisation is applied here other than
            the per-channel mean/std written to a sidecar JSON if present.

Expected ONNX output
    name: output (or the first output)
    shape: [1, 2, H, W] or [1, 1, H, W]  logits or water probability.

The script tiles at 512 px with 64 px overlap and cosine blending, matching the
Colab notebook. It never downloads weights and never requires a GPU.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def cosine_weights(n: int, overlap: int) -> np.ndarray:
    w = np.ones(n, np.float32)
    if overlap <= 0:
        return w
    t = np.linspace(0, np.pi, overlap, dtype=np.float32)
    ramp = 0.5 * (1 - np.cos(t))
    w[:overlap] = ramp
    w[-overlap:] = ramp[::-1]
    return w


def to_db(a: np.ndarray) -> np.ndarray:
    if np.nanmedian(a) > 1.5:  # already looks like dB (Sen1Floods11 range)
        return a.astype(np.float32)
    return (10.0 * np.log10(np.clip(a, 1e-7, None))).astype(np.float32)


def load_band(path: Path) -> np.ndarray:
    try:
        import rasterio
        with rasterio.open(path) as src:
            return src.read(1).astype(np.float32)
    except Exception:
        from PIL import Image
        return np.array(Image.open(path), dtype=np.float32)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--onnx", required=True, type=Path, help="Path to the trained U-Net ONNX file")
    p.add_argument("--vv", required=True, type=Path)
    p.add_argument("--vh", type=Path, default=None, help="Optional VH band (recommended)")
    p.add_argument("--out", type=Path, default=Path("pred_water.png"))
    p.add_argument("--tile", type=int, default=512)
    p.add_argument("--overlap", type=int, default=64)
    p.add_argument("--channels", choices=["vv", "vv_vh", "vv_vh_ratio"], default="vv_vh_ratio")
    p.add_argument("--norm-json", type=Path, default=None, help="Optional {mean:[...], std:[...]} sidecar")
    args = p.parse_args(argv)

    if not args.onnx.exists():
        print(
            f"ONNX weights not found at {args.onnx}.\n"
            "Train / export them on Saturday (Colab T4 retry of notebook 02) and pass --onnx.",
            file=sys.stderr,
        )
        return 2

    try:
        import onnxruntime as ort
    except ImportError:
        print("onnxruntime is not installed. pip install onnxruntime", file=sys.stderr)
        return 2

    vv = to_db(load_band(args.vv))
    if args.vh is not None:
        vh = to_db(load_band(args.vh))
    else:
        vh = np.full_like(vv, np.nan)
    ratio = vv - vh
    if args.channels == "vv":
        x = np.stack([vv])
    elif args.channels == "vv_vh":
        x = np.stack([vv, vh])
    else:
        x = np.stack([vv, vh, ratio])

    if args.norm_json and args.norm_json.exists():
        n = json.loads(args.norm_json.read_text())
        mean = np.asarray(n["mean"], np.float32)[:, None, None]
        std = np.asarray(n["std"], np.float32)[:, None, None]
        x = (x - mean) / np.clip(std, 1e-6, None)

    session = ort.InferenceSession(str(args.onnx), providers=["CPUExecutionProvider"])
    inp = session.get_inputs()[0]
    out_name = session.get_outputs()[0].name
    print(f"ONNX input {inp.name} {inp.shape}  output {out_name}")

    C, H, W = x.shape
    tile, ov = args.tile, args.overlap
    stride = tile - ov
    acc = np.zeros((H, W), np.float32)
    wgt = np.zeros((H, W), np.float32)
    wy = cosine_weights(tile, ov)[:, None]
    wx = cosine_weights(tile, ov)[None, :]
    win = wy * wx

    ys = list(range(0, max(H - tile, 0) + 1, stride)) or [0]
    xs = list(range(0, max(W - tile, 0) + 1, stride)) or [0]
    if ys[-1] + tile < H:
        ys.append(max(H - tile, 0))
    if xs[-1] + tile < W:
        xs.append(max(W - tile, 0))

    for y in ys:
        for x0 in xs:
            patch = np.zeros((1, C, tile, tile), np.float32)
            y2, x2 = min(y + tile, H), min(x0 + tile, W)
            ph, pw = y2 - y, x2 - x0
            patch[0, :, :ph, :pw] = np.nan_to_num(x[:, y:y2, x0:x2], nan=0.0)
            feed = {inp.name: patch}
            pred = session.run([out_name], feed)[0]
            if pred.ndim == 4 and pred.shape[1] == 2:
                water = pred[0, 1]
            elif pred.ndim == 4:
                water = pred[0, 0]
            else:
                water = np.squeeze(pred)
            acc[y:y2, x0:x2] += water[:ph, :pw] * win[:ph, :pw]
            wgt[y:y2, x0:x2] += win[:ph, :pw]

    prob = np.divide(acc, np.maximum(wgt, 1e-6))
    mask = (prob > 0.5).astype(np.uint8)
    # preview PNG: water cyan, dry dark
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 0:3] = (20, 24, 30)
    rgba[..., 3] = 255
    rgba[mask == 1] = (0, 200, 220, 255)
    from PIL import Image
    args.out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba).save(args.out)
    print(f"wrote {args.out}  water_frac={float(mask.mean()):.4f}  mean_prob={float(prob.mean()):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
