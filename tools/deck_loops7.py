"""Join the deck_loops7.mjs takes into 1200x750 loops: each phase cropped to its panel (2x frames), sped up a little, hard cuts.
Writes submission/clips/deck-fire-ready.{mp4,webm}, deck-field-rye.{mp4,webm} and posters in submission/assets/shots/."""
import json, subprocess, shutil, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]; B = R / "submission/build/loops7"; OUT = R / "submission/clips"; SH = R / "submission/assets/shots"
OW, OH, BG = 1200, 750, "0x0b0e20"
# seconds each phase gets in the loop (the 2x recording runs slow; each phase is retimed to its target)
TARGET = {"firemap": {"canada": 2.6, "boreal": 2.2, "bc": 3.6, "canada2": 2.2, "cal": 2.0, "crews": 1.8}, "fire": {"outlook": 3.6, "actions": 5.2, "whatif": 4.0}, "field": {"map": 2.4, "act": 3.0, "map2": 1.8, "go": 2.8, "whatif": 3.6}}
# crop overrides (CSS px in the 1600x800 viewport)
CROP = {("fire", "outlook"): dict(x=1012, y=76, w=588, h=420), ("fire", "actions"): dict(x=1012, y=76, w=588, h=420),
        ("fire", "whatif"): dict(x=90, y=40, w=1420, h=760), ("field", "whatif"): dict(x=90, y=40, w=1420, h=760),
        ("field", "act"): dict(x=1012, y=76, w=588, h=420), ("field", "go"): dict(x=1012, y=76, w=588, h=420)}
NAMES = {"firemap": "deck-fire-map", "fire": "deck-fire-ready", "field": "deck-field-rye"}
POSTER_AT = {"firemap": "bc", "fire": "actions", "field": "go"}
meta = json.loads((B / "takes.json").read_text())
if len(sys.argv) > 1: meta = {k: v for k, v in meta.items() if k in sys.argv[1].split(",")}
def run(*a): subprocess.run(a, check=True, capture_output=True)
for name, t in meta.items():
    d = Path(t["dir"]); fr = t["frames"]; mk = t["marks"]; segs = []
    for k in range(len(mk) - 1):
        ph, a, z = mk[k]["k"], mk[k]["t"], mk[k + 1]["t"]; c = CROP.get((name, ph), mk[k]["crop"])
        sel = [f for f in fr if a <= f["t"] < z]
        prev = [f for f in fr if f["t"] < a]
        if prev: sel = [dict(prev[-1], t=a)] + sel  # hold the last frame before the phase from its start
        lst = d / f"seg{k}.txt"; L = ["ffconcat version 1.0"]
        for i, f in enumerate(sel):
            dur = (sel[i + 1]["t"] if i + 1 < len(sel) else z) - f["t"]
            L += [f"file f{f['i']:05d}.jpg", f"duration {max(0.001, dur):.4f}"]
        L.append(f"file f{sel[-1]['i']:05d}.jpg"); lst.write_text("\n".join(L) + "\n")
        sp = max(1.0, (z - a) / TARGET[name][ph])
        x, y, w, h = [round(2 * c[q]) for q in ("x", "y", "w", "h")]
        vf = f"crop={w}:{h}:{x}:{y},scale={OW}:{OH}:force_original_aspect_ratio=decrease:flags=lanczos,pad={OW}:{OH}:(ow-iw)/2:(oh-ih)/2:color={BG},setpts=PTS/{sp},fps=30,format=yuv420p"
        seg = d / f"seg{k}.mp4"; run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", vf, "-c:v", "libx264", "-crf", "16", "-preset", "slow", str(seg))
        segs.append(seg)
        if ph == POSTER_AT[name]: run("ffmpeg", "-y", "-loglevel", "error", "-sseof", "-0.4", "-i", str(seg), "-frames:v", "1", "-q:v", "2", str(SH / f"{NAMES[name]}.jpg"))
    cl = d / "segs.txt"; cl.write_text("".join(f"file '{s.name}'\n" for s in segs))
    mp4 = OUT / f"{NAMES[name]}.mp4"; webm = OUT / f"{NAMES[name]}.webm"
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(cl), "-c:v", "libx264", "-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-an", str(mp4))
    run("ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "36", "-row-mt", "1", "-an", str(webm))
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout.strip()
    print(name, mp4.name, dur, "s", mp4.stat().st_size // 1024, "KB mp4", webm.stat().st_size // 1024, "KB webm")
