"""Architecture figures for the deck (style from tools/figlib.py): inputs -> prep -> model -> output -> results, per model.
Every score is from submission/FORM.md / STORY.md. Output: submission/assets/shots/arch-1.png, arch-2.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); A = R + '/submission/build/arch/'; IMG = R + '/src/assets/img/'
OUT = R + '/submission/assets/shots/'
COLS = [(40, '① Inputs'), (440, '② Prepare'), (750, '③ Model'), (1110, '④ Output'), (1420, '⑤ Results and sources')]
def heads(F):
    for x, t in COLS: F.text(x, 40, t, 19, 700, INK)
def lane(F, y, title, color, inputs, prep, model, out_img, out_t, out_l, res_t, res_l, src):
    F.group(20, y, 1760, 380, title, dash=False, fill='#FBFCFE', stroke=color, lc=color, ls=17)
    # inputs: up to 2 thumbs with labels
    for k, (img, lab, sub) in enumerate(inputs):
        yy = y + 46 + k * 160
        F.img(44, yy, 120, 120, img); F.text(178, yy + 30, lab, 17, 600, INK); 
        for j, s in enumerate(sub): F.text(178, yy + 56 + j * 21, s, 14.5, 400, MUTED)
    F.arrow([(408, y + 190), (436, y + 190)])
    F.box(440, y + 80, 280, 220, 'data', prep[0], prep[1], ts=18, ls=15)
    F.arrow([(722, y + 190), (746, y + 190)])
    yy = y + 50
    for fam, t, l, h in model:
        F.box(750, yy, 330, h, fam, t, l, ts=18, ls=15); yy += h + 14
    F.arrow([(1082, y + 190), (1106, y + 190)])
    F.img(1110, y + 46, 140, 140, out_img); F.box(1110, y + 196, 280, 150, 'out', out_t, out_l, ts=17, ls=14.5)
    F.arrow([(1392, y + 190), (1416, y + 190)])
    F.box(1420, y + 46, 340, 270, 'classic', res_t, res_l, ts=19, ls=16)
    F.text(1420, y + 342, src, 13.5, 500, MUTED, mono=True)
def legend(F, y):
    F.legend(40, y, [('data', 'input data / preparation'), ('train', 'trained model'), ('classic', 'classical method / results'), ('out', 'output')], colw=300, size=15)

F = Fig(1800, 900); heads(F)
lane(F, 62, 'Flood · SAR Change (Valencia)', '#0369a1',
     [('sar-after.webp', 'Radar: Sentinel-1', ['C-band VV + VH', 'sees through cloud']),
      (A + 'rain.png', 'Rain: GPM IMERG', ['daily rain, mm', 'cloud cover, %'])],
     ('Prepare', ['512 × 512 tiles, dB', '~same grid, before / after', '~rain: upstream box mean', '~and wettest 0.1° cell']),
     [('train', 'U-Net water model', ['trained on Sen1Floods11', '~runs on a CPU (ONNX)'], 110),
      ('classic', 'Leading-signal rule', ['upstream rain > 50 mm', '~design example, not tested'], 110)],
     'opera-after.webp', 'Flood water map', ['77.7 km² new water', '~8 towns flagged, alert drafted'],
     'Results', ['66.4% water IoU', '~vs 21.8% Otsu threshold (3.0×)', '~90 hand-labelled test chips', '1.63 s per 512² tile, CPU', '~check: NASA/JPL OPERA DSWx-S1'],
     'Sen1Floods11 · GPM IMERG V07 · POWER')
lane(F, 462, 'Fire · Hot Spots (Canada)', '#c2410c',
     [('canada-fire-heat.webp', 'Thermal: NASA FIRMS', ['MODIS + VIIRS', '11.6 M detections'])],
     ('Prepare', ['0.25° grid, monthly', '~MODIS put on the VIIRS', '~scale (harmonized)', '~train 2012–20, test 2022–25']),
     [('classic', 'Empirical-Bayes baseline', ['per-cell ratio prior'], 92),
      ('train', 'LightGBM correction', ['+ conformal ranges', '~calibrated on 2021'], 110)],
     A + 'cal.png', 'Fire calendar + range', ['unusual months flagged', '~May = Alberta watch month'],
     'Results', ['8.5% lower error', '~RMSE 0.2844 vs 0.3109', '88.6% range coverage', '~target 90%', '~honest miss: monthly totals 39.4%'],
     'NASA FIRMS · held-out 2022–25')
legend(F, 868); F.render(OUT + 'arch-1.png')

F = Fig(1800, 900); heads(F)
lane(F, 62, 'Farms · Field Shift (Story County, Iowa)', '#4d7c0f',
     [(A + 'ndvi.png', 'Optical: HLS + MODIS', ['Landsat + Sentinel-2', 'NDVI greenness']),
      ('field-cdl.webp', 'Crop history + land', ['USDA CDL 2009–25', 'terrain, soil, climate'])],
     ('Prepare', ['30 m pixels, one grid', '~past crops, slope, soil,', '~frost dates, heat, greenness', '~train ≤2023, test 2024–25']),
     [('train', 'Next-season crop model', ['LightGBM, 6 crops'], 92),
      ('classic', 'Rotation search', ['NSGA-II, 4-year plans', '~36 non-dominated rotations'], 110)],
     A + 'crop.png', 'Crop map + plan', ['next crop, every 30 m pixel', '~scout list, farmer view'],
     'Results', ['81.8% next crop correct', '~vs 81.4% crop history alone', 'macro-F1 0.5012 vs 0.4633', '~66,666 held-out pixels', '~honest miss: hay F1 0.33'],
     'USDA NASS CDL · NASA HLS · MODIS · NASADEM')
lane(F, 462, 'Trend engine (all three)', '#3f63d6',
     [(A + 'grace.png', 'Water + climate', ['GRACE · GLDAS · SMAP', 'IMERG · POWER · FIRMS'])],
     ('Prepare', ['one value per year', '~per region or grid cell', '~second source for each']),
     [('classic', "Mann-Kendall + Sen's slope", ['95% CI, α = 0.05', '~Hamed-Rao autocorrelation', '~check'], 130)],
     A + 'trendmap.png', 'Trend maps', ['significant cells only', '~"no trend" said out loud'],
     'Results', ['Iowa frost-free +0.43 d/yr', '~p = 0.006', 'E. Spain water −0.39 cm/yr', '~GRACE, p = 0.002', '~Valencia wettest day p = 0.28'],
     'pymannkendall 1.4.3 · Gilbert (1987)')
legend(F, 868); F.render(OUT + 'arch-2.png')
print('ok')
