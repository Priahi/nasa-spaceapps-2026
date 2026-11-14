"""Short muted looping clips for deck.html (3-6 s, < 2 MB each) + poster JPGs for the PDF.
Sources: tools/video_record3.mjs screencasts (1600x900 CSS px) and real captures in submission/assets/shots.
Usage: python3 tools/make_loops.py"""
import json, subprocess
from pathlib import Path
R = Path(__file__).resolve().parents[1]; S = R / "submission"; V = S / "build/video3"; SH = S / "assets/shots"; O = S / "clips"; O.mkdir(exist_ok=True)
clips = json.load(open(V / "clips.json"))
def run(c): subprocess.run(c, check=True, capture_output=True)
def enc(inp, vf, name, d):
    mp4, webm = O / f"loop-{name}.mp4", O / f"loop-{name}.webm"
    run(["ffmpeg", "-y", *inp, "-vf", vf + ",fps=24,format=yuv420p", "-t", str(d), "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-movflags", "+faststart", str(mp4)])
    run(["ffmpeg", "-y", "-i", str(mp4), "-an", "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "38", "-row-mt", "1", str(webm)])
    run(["ffmpeg", "-y", "-sseof", "-0.2", "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(SH / f"loop-{name}.jpg")])
    print(name, d, "s", round(mp4.stat().st_size / 1e6, 2), "MB mp4", round(webm.stat().st_size / 1e6, 2), "MB webm")
def cast(k, ss, d, crop, w, speed=1.0):
    c = clips[k]; x, y, cw, ch = crop
    enc(["-f", "concat", "-safe", "0", "-i", f"{c['dir']}/list.ffconcat", "-ss", f"{ss:.2f}"], f"setpts=(PTS-STARTPTS)/{speed:.3f},crop={cw}:{ch}:{x}:{y},scale={w}:-2:flags=lanczos", k.replace('-dss', '') if k != 'flood-dss' else 'flood', d)
if __name__ == "__main__":
    # flood DSS: zones + assets placed on the radar map (sticky map, before the page scrolls)
    cast("flood-dss", 0.5, 4.0, (130, 178, 760, 690), 1000)
    # fire: crews + hiring placed on Alberta/B.C., queue starts
    cast("fire", 0.2, 4.4, (0, 57, 980, 640), 980)
    # field: slow pan over the real crop classification map (Crops 2025, 30 m)
    n = 5 * 24
    enc(["-loop", "1", "-framerate", "24", "-i", str(SH / "field-crop-map.png")], f"scale=2400:-2,zoompan=z='1+0.16*sin(PI*on/{n})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1200x862:fps=24", "field", 5)
    # architecture: a highlight sweeps the five columns (inputs -> results)
    enc(["-loop", "1", "-framerate", "24", "-i", str(SH / "arch-1.png")], "scale=1800:-2,drawbox=x='mod(t,5)/5*1800-60':y=0:w=330:h=ih:color=0x3f63d6@0.10:t=fill", "arch", 5)
