"""Compose tight deck frames from the tasking captures (submission/assets/shots/*.png -> comp-*.png)."""
from PIL import Image
from pathlib import Path
D = Path(__file__).resolve().parents[1] / "submission/assets/shots"; BG = (16, 20, 44)
def crop(n, x0, y0, x1, y1):
    im = Image.open(D / f"{n}.png").convert("RGB"); w, h = im.size
    return im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
def stack(parts, W=900, gap=18, pad=0):
    rs = [p.resize((W, round(p.height * W / p.width)), Image.LANCZOS) for p in parts]
    H = sum(r.height for r in rs) + gap * (len(rs) - 1) + 2 * pad
    out = Image.new("RGB", (W + 2 * pad, H), BG); y = pad
    for r in rs: out.paste(r, (pad, y)); y += r.height + gap
    return out
# slide 3 · 1 signal: the 91 mm / 99% cards over the chart around 29 Oct
stack([crop("flood-rain", .685, .19, .99, .58), crop("flood-rain", .10, .17, .48, .74)], pad=14).save(D / "comp-flood-signal.png")
# slide 3 · 2 radar map: the 8 towns
crop("flood-map-run", .36, .27, 1.0, 1.0).save(D / "comp-flood-map.png")
# slide 3 · 4 dispatch: towns with team markers + the task queue mid-run
stack([crop("flood-map-run", .40, .50, 1.0, .84), crop("flood-queue-run", 0, 0, 1, 1)], pad=14).save(D / "comp-flood-dispatch.png")
# slide 1 hook: towns, markers done
crop("flood-map-done", .34, .27, 1.0, 1.0).save(D / "comp-flood-hook.png")
# slide 5 / 6 side panels: queue mid-run + timeline after Send (simulated)
stack([crop("fire-queue-run", 0, 0, 1, 1), crop("fire-timeline", 0, 0, 1, 1)], pad=14).save(D / "comp-fire-tasking.png")
stack([crop("field-queue-run", 0, 0, 1, 1), crop("field-timeline", 0, 0, 1, 1)], pad=14).save(D / "comp-field-tasking.png")
stack([crop("flood-queue-done", 0, 0, 1, 1), crop("flood-timeline", 0, 0, 1, 1)], pad=14).save(D / "comp-flood-tasking.png")
for f in sorted(D.glob("comp-*.png")): print(f.name, Image.open(f).size)
