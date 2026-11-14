"""One combined system figure for the deck (style: tools/figlib.py), sized so every label is >= 18 px on a 1920-wide slide:
shared inputs -> one engine (trend detection + per-signal models) -> signal / map / alert / task -> outputs + results per vertical.
Scores only from submission/FORM.md / STORY.md. Output: submission/assets/shots/arch-system.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); A = R + '/submission/build/arch/'
OUT = R + '/submission/assets/shots/'
F = Fig(1800, 770)
for x, t in [(20, '① Shared inputs'), (420, '② One engine'), (840, '③ Decision loop'), (1130, '④ Outputs and results, per vertical')]:
    F.text(x, 36, t, 23, 700, INK)
ins = [('sar-after.webp', 'Radar', 'Sentinel-1 SAR'), ('canada-fire-heat.webp', 'Thermal', 'NASA FIRMS'),
       (A + 'rain.png', 'Rain', 'GPM IMERG + POWER'), (A + 'ndvi.png', 'Optical', 'HLS + USDA crop map'),
       (A + 'grace.png', 'Water', 'GRACE + GLDAS')]
for k, (img, lab, sub) in enumerate(ins):
    y = 64 + k * 134
    F.img(20, y, 96, 96, img); F.text(130, y + 40, lab, 23, 650, INK); F.text(130, y + 72, sub, 20, 400, MUTED)
    F.arrow([(372, y + 48), (414, y + 48)])
F.group(420, 56, 390, 664, None, dash=False, fill='#F5F7FD', stroke='#3f63d6')
F.box(438, 72, 354, 124, 'classic', 'Trend detection', ["~Mann-Kendall + Sen's slope", '~"no trend" said out loud'], ts=23, ls=20)
F.text(438, 236, 'Per-signal models', 20, 700, MUTED)
for k, (t, l) in enumerate([('Water model', '~U-Net: radar → water'), ('Fire model', '~LightGBM + conformal range'), ('Crop model', '~LightGBM + NSGA-II plans')]):
    F.box(438, 252 + k * 154, 354, 132, 'train', t, [l], ts=23, ls=20)
F.arrow([(812, 388), (836, 388)])
for k, (t, l) in enumerate([('Signal', '~rain, heat, trend'), ('Map', '~where it is'), ('Alert', '~drafted (simulated)'), ('Task', '~queued (simulated)')]):
    y = 64 + k * 168
    F.box(840, y, 250, 128, 'out' if k < 2 else 'gate', t, [l], ts=24, ls=20)
    if k < 3: F.arrow([(965, y + 130), (965, y + 164)])
rows = [('#0369a1', 'Flood · water map, town alert', ['~66.4% water IoU vs 21.8% (Otsu)', '~Sen1Floods11 · NASA/JPL OPERA']),
        ('#c2410c', 'Fire · burn calendar, staffing', ['~8.5% lower error; 88.6% range coverage', '~NASA FIRMS, held-out 2022–25']),
        ('#4d7c0f', 'Farms · crop map, scout list', ['~81.8% next crop vs 81.4% history alone', '~USDA CDL · NASA HLS, 2024–25']),
        ('#3f63d6', 'Trends · all three', ['~E. Spain water −0.39 cm/yr (p = 0.002)', '~Iowa frost-free +0.43 d/yr (p = 0.006)'])]
for k, (c, t, l) in enumerate(rows):
    y = 64 + k * 168
    F.arrow([(1094, 388), (1112, 388), (1112, y + 64), (1126, y + 64)])
    F.rect(1130, y, 12, 136, fill=c, stroke=c, rx=4)
    F.box(1150, y, 630, 136, 'classic', t, l, ts=24, ls=20)
F.legend(20, 756, [('classic', 'classical method / result'), ('train', 'trained model'), ('out', 'output'), ('gate', 'simulated step')], colw=380, size=20)
F.render(OUT + 'arch-system.png'); print('ok')
