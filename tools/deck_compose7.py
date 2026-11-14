"""Slide 1 + slide 3 flood frames (same live session, same map extent) -> comp-flood-hook.png, sq-flood-change.png, sq-flood-act.png."""
from PIL import Image
from pathlib import Path
D = Path(__file__).resolve().parents[1] / "submission/assets/shots"; BG = (11, 14, 32); S = 1200
L = lambda n: Image.open(D / f"flood7-{n}.png").convert("RGB")
def fitw(im, w): return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
def mapband(im, h):  # same frame, scaled to the square width, trimmed evenly top/bottom
    m = fitw(im, S); t = max(0, (m.height - h) // 2); return m.crop((0, t, S, t + h))
def square(parts_top, mapim, parts_bot, pad=26):
    k = (S - 2 * pad) / max(p.width for p in parts_top + parts_bot)  # one scale for all UI parts
    top = [fitw(p, round(p.width * k)) for p in parts_top]; bot = [fitw(p, round(p.width * k)) for p in parts_bot]
    used = sum(p.height + pad for p in top + bot) + (pad if top else 0)
    out = Image.new("RGB", (S, S), (parts_top + parts_bot)[-1].getpixel((4, 4))); y = pad if top else 0
    for p in top: out.paste(p, (pad, y)); y += p.height + pad // 2
    mh = S - y - sum(p.height + pad // 2 for p in bot) - (pad if bot else 0)
    out.paste(mapband(mapim, mh), (0, y)); y += mh + pad // 2
    for p in bot: out.paste(p, (pad, y)); y += p.height + pad // 2
    return out
# slide 1: the plain radar map (no markers), same extent as slide 3
L("map-plain").save(D / "comp-flood-hook.png")
head = L("head"); head = head.crop((0, 0, head.width, 178))          # "+47.0 km² more flood water in five days"
rank = L("rank"); rank = rank.crop((0, 0, rank.width, 345))          # top 3 towns
square([head], L("map-change"), [rank]).save(D / "sq-flood-change.png")
card = L("card"); tag = card.crop((14, 14, card.width - 14, 125)); chips = card.crop((14, 680, card.width * 3 // 5, 995))
square([tag], L("map-act"), [chips]).save(D / "sq-flood-act.png")
for n in ["comp-flood-hook", "sq-flood-change", "sq-flood-act"]: print(n, Image.open(D / f"{n}.png").size)
