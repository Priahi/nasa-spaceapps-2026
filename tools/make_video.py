"""Compose submission/demo.mp4 (<= 30 s, 1920x1080, H.264, burned-in English captions) from the recorded clips."""
import json, subprocess
from pathlib import Path
B = Path("/workspace/spaceapps-site/submission/build"); V = B / "video"; OUT = B.parent / "demo.mp4"
clips = json.load(open(V / "clips.json"))
SEG = [("card:title", 1.8, "Three full NASA-data tools, each with a trend investigation on top"),
       ("landing", 5.1, "The four questions: what is changing, where, how much, and is it significant?"),
       ("fire", 4.4, "Fire, by province: Canada's MODIS fire detections rose about 3,000 a year since 2003 (p = 0.035)"),
       ("hotapp", 2.9, "Hot Spots Harmonizer: 11.6M NASA FIRMS detections in one 2000–2025 calendar"),
       ("sar", 3.0, "SAR Change: radar sees the 2024 Valencia flood through the clouds"),
       ("water", 3.1, "Valencia's wettest-day rain shows no significant trend (p = 0.28); Ontario's is falling"),
       ("fieldapp", 3.0, "Field Shift: compare crop rotations against your own priorities"),
       ("crops", 3.0, "Iowa: autumn frost comes later, so the frost-free season is getting longer (p = 0.006)"),
       ("card:end", 2.2, "Every trend shows its slope, 95% CI and p-value. Live now.")]
parts = []
for i, (k, d, _) in enumerate(SEG):
    o = V / f"seg{i}.mp4"
    vf = "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p,setsar=1"
    if k.startswith("card:"):
        cmd = ["ffmpeg", "-y", "-loop", "1", "-t", str(d), "-i", str(B / f"card-{k[5:]}.png"), "-vf", vf]
    else:
        c = clips[k]; assert c["secs"] >= d - 0.05, (k, c["secs"], d)
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{c['dir']}/list.ffconcat", "-ss", "0.30", "-t", str(d), "-vf", vf + f",tpad=stop_mode=clone:stop_duration={d}", "-t", str(d)]
    subprocess.run(cmd + ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(o)], check=True, capture_output=True)
    parts.append(o)
(V / "parts.txt").write_text("".join(f"file '{p}'\n" for p in parts))
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Cap,Geist,44,&H00FBF6F4,&H00FBF6F4,&H281A0907,&H281A0907,0,0,0,0,100,100,0,0,3,16,0,2,140,140,78,1",
       "Style: Wm,Geist Mono,20,&H00D6C0B7,&H00D6C0B7,&H401A0907,&H401A0907,0,0,0,0,100,100,0,0,3,6,0,3,28,28,18,1", "",
       "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
t = 0.0; total = sum(d for _, d, _ in SEG)
for k, d, cap in SEG:
    ass.append(f"Dialogue: 0,{ts(t)},{ts(t + d)},Cap,,0,0,0,,{cap}"); t += d
ass.append(f"Dialogue: 0,{ts(0)},{ts(total)},Wm,,0,0,0,,AI-assisted code · real screen captures, no AI-generated imagery")
(V / "captions.ass").write_text("\n".join(ass) + "\n")
fontsdir = "/workspace/spaceapps-site/src/assets/fonts"
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(V / "parts.txt"), "-vf", f"subtitles={V/'captions.ass'}:fontsdir={fontsdir}",
                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(OUT)], check=True, capture_output=True)
# also ship captions as a sidecar SRT
srt, t = [], 0.0
def st(x): return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int(round((x%1)*1000)):03d}"
for i, (k, d, cap) in enumerate(SEG, 1):
    srt.append(f"{i}\n{st(t)} --> {st(t + d)}\n{cap}\n"); t += d
(B.parent / "demo.en.srt").write_text("\n".join(srt))
print("planned", round(total, 2), "s ->", OUT)
