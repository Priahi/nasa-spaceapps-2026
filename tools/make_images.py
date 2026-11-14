"""Turn captured screenshots and run figures into web-sized WebP assets (+ PNG social cards)."""
from PIL import Image
from pathlib import Path
CAP = Path("/tmp/cap"); D = Path(__file__).resolve().parent.parent
I = D / "src/assets/img"; DEM = D / "demos"
def cover(src, dst, w=1200, h=750, q=82):
    im = Image.open(src).convert("RGB"); s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS).crop((0, 0, w, h)); im.save(I / dst, "WEBP", quality=q); return im
def fit(src, dst, w, q=85):
    im = Image.open(src).convert("RGB")
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(I / dst, "WEBP", quality=q)
for name, src in [("hotspots-card", CAP / "hotspots-app.png"), ("sar-card", CAP / "sar-app.png"), ("field-card", CAP / "field-app.png")]:
    im = cover(src, name + ".webp"); im.crop((0, 0, 1200, 630)).save(I / (name + "-og.png"))
fit(CAP / "hotspots-calendar.png", "hotspots-calendar.webp", 1600)
fit(CAP / "hotspots-argentina.png", "hotspots-argentina.webp", 1200)
fit(DEM / "hotspots/figs/fig_04.png", "hotspots-fig04.webp", 1200, 88)
fit(CAP / "sar-app2.png", "sar-app2.webp", 1400)
fit(DEM / "field-shift/data/colab_run/crop_map.png", "field-map.webp", 1600, 88)
fit(DEM / "field-shift/data/colab_run/crop_ablation.png", "field-ablation.webp", 1200, 88)
fit(DEM / "field-shift/data/cdl_2025_map.png", "field-cdl.webp", 1200, 88)
S = DEM / "sar-change/tiles/valencia/asc_1755"
fit(S / "20241026T1755/fcc.png", "sar-before.webp", 1100, 80)
fit(S / "20241107T1755/fcc.png", "sar-after.webp", 1100, 80)
# landing social card: three cards side by side
cards = [Image.open(I / f"{n}-card.webp").resize((400, 250)) for n in ("hotspots", "sar", "field")]
og = Image.new("RGB", (1200, 630), (7, 9, 26))
for k, c in enumerate(cards): og.paste(c, (k * 400, 190))
og.save(I / "og.png")
for p in sorted(I.iterdir()): print(p.name, p.stat().st_size // 1024, "KB", Image.open(p).size if p.suffix != ".svg" else "")
