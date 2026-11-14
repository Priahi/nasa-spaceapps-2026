"""One combined system figure for the deck (style: tools/figlib.py): shared inputs -> one engine (trend detection + per-signal models)
-> signal / map / alert / task -> outputs per vertical, with results and sources on the right edge.
Scores only from submission/FORM.md / STORY.md. Output: submission/assets/shots/arch-system.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); A = R + '/submission/build/arch/'
OUT = R + '/submission/assets/shots/'
F = Fig(1800, 860)
for x, t in [(30, '① Shared inputs (open NASA + partner data)'), (440, '② One engine'), (850, '③ Decision loop'), (1130, '④ Outputs per vertical'), (1470, '⑤ Results and sources')]:
    F.text(x, 34, t, 19, 700, INK)
# 1 inputs
ins = [('sar-after.webp', 'Radar: Sentinel-1 SAR', 'VV + VH, sees through cloud'),
       ('canada-fire-heat.webp', 'Thermal: NASA FIRMS', 'MODIS + VIIRS, 11.6 M detections'),
       (A + 'rain.png', 'Rain: GPM IMERG + POWER', 'daily rain, cloud cover'),
       (A + 'ndvi.png', 'Optical: HLS, Landsat, S-2', '+ USDA crop history (CDL)'),
       (A + 'grace.png', 'Water: GRACE + GLDAS', 'groundwater, soil moisture')]
for k, (img, lab, sub) in enumerate(ins):
    y = 62 + k * 150
    F.img(30, y, 104, 104, img); F.text(146, y + 40, lab, 17, 650, INK); F.text(146, y + 64, sub, 14.5, 400, MUTED)
    F.arrow([(398, y + 52), (436, y + 52)])
# 2 engine
F.group(440, 56, 370, 740, 'One engine', dash=False, fill='#F5F7FD', stroke='#3f63d6', lc='#3f63d6', ls=17)
F.box(462, 92, 326, 150, 'classic', 'Trend detection', ["Mann-Kendall + Sen's slope", '~Hamed-Rao autocorrelation check', '~p-values; "no trend" said out loud'], ts=18, ls=15)
F.text(462, 276, 'Per-signal models', 16, 700, MUTED)
F.box(462, 290, 326, 140, 'train', 'U-Net water model', ['radar → water, 30 m', '~trained on Sen1Floods11', '~1.63 s per tile on a CPU'], ts=18, ls=15)
F.box(462, 444, 326, 160, 'train', 'Fire range model', ['empirical-Bayes baseline', '~+ LightGBM correction', '~+ conformal ranges (calibrated)'], ts=18, ls=15)
F.box(462, 618, 326, 160, 'train', 'Next-season crop model', ['LightGBM, 6 crops, 30 m', '~+ NSGA-II 4-year rotations', '~trained ≤2023, tested 2024–25'], ts=18, ls=15)
F.arrow([(812, 425), (846, 425)])
# 3 loop
steps = [('Signal', ['rain, heat, trend', '~crosses a threshold']), ('Map', ['where: water, fire,', '~crop, per town / cell']), ('Alert', ['drafted message', '~(simulated)']), ('Task', ['crews, drones, passes', '~queue (simulated)'])]
for k, (t, l) in enumerate(steps):
    y = 80 + k * 182
    F.box(850, y, 240, 130, 'out' if k < 2 else 'gate', t, l, ts=19, ls=15)
    if k < 3: F.arrow([(970, y + 132), (970, y + 178)])
F.curve('M 1092 690 C 1126 690, 1126 145, 1092 145', c='#7b5bd6', dash=True)
# 4 outputs + 5 results
rows = [('#0369a1', 'Flood · SAR Change', 'opera-after.webp', ['water map by town', '~8-town alert, teams placed'],
         ['66.4% water IoU', '~vs 21.8% Otsu threshold (3.0×)', '~90 hand-labelled chips', '~Sen1Floods11 · NASA/JPL OPERA']),
        ('#c2410c', 'Fire · Hot Spots', A + 'cal.png', ['burn calendar + range', '~staffing, May notice'],
         ['8.5% lower error', '~RMSE 0.2844 vs 0.3109', '~88.6% range coverage (target 90%)', '~NASA FIRMS, held-out 2022–25']),
        ('#4d7c0f', 'Farms · Field Shift', A + 'crop.png', ['crop map, every 30 m', '~scout list, rye plan'],
         ['81.8% next crop correct', '~vs 81.4% crop history alone', '~macro-F1 0.5012 vs 0.4633', '~USDA CDL · NASA HLS, 2024–25']),
        ('#3f63d6', 'Trends · all three', A + 'trendmap.png', ['trend maps', '~significant cells only'],
         ['Iowa frost-free +0.43 d/yr', '~p = 0.006 (POWER)', '~E. Spain water −0.39 cm/yr', '~GRACE p = 0.002 · wettest day p = 0.28'])]
for k, (c, t, img, l, res) in enumerate(rows):
    y = 62 + k * 190
    F.arrow([(1094, 425), (1112, 425), (1112, y + 80), (1126, y + 80)], head=True)
    F.img(1130, y, 90, 90, img); F.box(1230, y, 200, 160, 'out', t, l, ts=16, ls=14)
    F.rect(1130, y + 100, 90, 6, fill=c, stroke=c, rx=3)
    F.arrow([(1432, y + 80), (1466, y + 80)])
    F.box(1470, y, 310, 160, 'classic', res[0], res[1:], ts=18, ls=14.5)
F.legend(30, 830, [('data', 'shared input'), ('classic', 'classical method / results'), ('train', 'trained model'), ('out', 'output'), ('gate', 'simulated step')], colw=300, size=15)
F.render(OUT + 'arch-system.png'); print('ok')
