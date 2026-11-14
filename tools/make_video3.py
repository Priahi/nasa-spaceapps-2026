"""Story video: submission/demo.mp4 (<= 30 s): the Valencia flood rewind (~25 s), then a 5 s 'times twenty' montage.
Also slide-8 clips (submission/clips/*.mp4) and posters. Input: tools/video_record3.mjs + tools/video_cards3.mjs output."""
import json, re, subprocess
from pathlib import Path
R = Path(__file__).resolve().parents[1]; S = R / "submission"; V = S / "build/video3"; OUT = S / "demo.mp4"
FONTS = R / "src/assets/fonts"; SH = S / "assets/shots"; (S / "clips").mkdir(exist_ok=True)
clips = json.load(open(V / "clips.json"))
# (key, seconds, caption, crop x,y,w,h in 1920x1080 frame px or None, start offset s)
MAP_FIRE = (0, 57, 1200, 675); MAP_FIELD = (0, 200, 1200, 675); FLOOD = (420, 210, 1180, 664)  # in 1600x900 screencast px
SEG = [
 ("card:night", 2.6, "", None, 0),
 ("card:elena", 2.6, "", None, 0),
 ("img:flood-rain", 4.2, "Rain signal: 91 mm upstream, 99% cloud. Optical satellites are blind.", None, 0),
 ("flood-map", 7.8, "Radar maps 77.7 km² of new water. 8 towns flagged, teams dispatched.", FLOOD, 0.3),
 ("flood-alert", 7.8, "One alert for all 8 towns. It could have gone out hours before 20:11.", FLOOD, 0.3),
 ("fire", 1.7, "Fire: crews staged before July", MAP_FIRE, 1.2),
 ("field", 1.7, "Farms: rye on the steep fields", MAP_FIELD, 1.2),
 ("card:x20", 1.4, "", None, 0),
]
WM = "Tasking and alerts are simulated"
VF = "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p,setsar=1"
def enc(cmd, o): subprocess.run(cmd + ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(o)], check=True, capture_output=True)
def seg(k, d, o, crop=None, ss=0.0, speed=1.0):
    if k.startswith("card:"):
        enc(["ffmpeg", "-y", "-loop", "1", "-t", str(d), "-i", str(V / f"card-{k[5:]}.png"), "-vf", VF], o); return
    if k.startswith("img:"):   # a capture on the navy dashboard background, slow push-in
        n = int(d * 30)
        enc(["ffmpeg", "-y", "-i", str(SH / f"{k[4:]}.png"), "-t", str(d), "-vf",
             f"scale=1840:-2,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x10142c,zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1920x1080:fps=30,format=yuv420p,setsar=1"], o); return
    c = clips[k]; cf = f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else ""
    enc(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{c['dir']}/list.ffconcat", "-ss", f"{ss:.2f}",
         "-vf", f"setpts=PTS/{speed:.3f}," + cf + VF + f",tpad=stop_mode=clone:stop_duration={d}", "-t", str(d)], o)
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
def st(x): return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int(round((x%1)*1000)):03d}"
def ass(items, total, path, wm=True):
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: Cap,Geist,44,&H00FBF6F4,&H00FBF6F4,&H301A0907,&H301A0907,0,0,0,0,100,100,0,0,3,16,0,2,140,140,70,1",
         "Style: Wm,Geist Mono,22,&H00E6DCD4,&H00E6DCD4,&H501A0907,&H501A0907,0,0,0,0,100,100,0,0,3,6,0,9,24,24,18,1", "",
         "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    t = 0.0
    for cap, d in items:
        if cap: L.append(f"Dialogue: 0,{ts(t)},{ts(t + d)},Cap,,0,0,0,,{cap}")
        t += d
    if wm: L.append(f"Dialogue: 0,{ts(0)},{ts(total)},Wm,,0,0,0,,{WM}")
    Path(path).write_text("\n".join(L) + "\n")
def burn(parts, items, out):
    lst = V / (out.stem + "-parts.txt"); lst.write_text("".join(f"file '{p}'\n" for p in parts))
    total = sum(d for _, d in items); a = V / (out.stem + ".ass"); ass(items, total, a)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", f"subtitles={a}:fontsdir={FONTS}", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out)], check=True, capture_output=True)
    return total
if __name__ == "__main__":
    import sys
    parts = []
    for i, (k, d, cap, crop, ss) in enumerate(SEG):
        o = V / f"seg{i}.mp4"; seg(k, d, o, crop, ss, speed=max(1.0, (clips[k]["secs"] - ss) / d) if k in clips and k.startswith("flood") else 1.0); parts.append(o)
    total = burn(parts, [(cap, d) for k, d, cap, _, _ in SEG], OUT)
    srt, t, n = [], 0.0, 0
    for k, d, cap, _, _ in SEG:
        if cap: n += 1; srt.append(f"{n}\n{st(t)} --> {st(t + d)}\n{cap}\n")
        t += d
    (S / "demo.en.srt").write_text("\n".join(srt))
    (S / "demo.en.vtt").write_text("WEBVTT\n\n" + re.sub(r"(\d\d:\d\d:\d\d),(\d\d\d)", r"\1.\2", (S / "demo.en.srt").read_text()))
    # slide-8 clips at real speed
    APPS = {"sar-change": [("flood-map", "Radar flood map: 77.7 km² of new water, 8 towns flagged, teams dispatched (simulated)"), ("flood-alert", "Alert for all 8 towns, drafted and sent (simulated)")],
            "hotspots": [("fire", "Crews staged in Alberta and B.C. before the July peak (simulated)"), ("fire-notice", "Community notice before May, the watch month (simulated)")],
            "field-shift": [("field", "Winter rye on the 92 steepest squares (simulated)"), ("field-plan", "4-year plan approved, grower messaged (simulated)")]}
    posters = {"sar-change": "poster-sar", "hotspots": "poster-hotspots", "field-shift": "poster-field"}
    for app, ks in APPS.items():
        if any(k not in clips for k, _ in ks): print("skip", app); continue
        ps, items = [], []
        for k, cap in ks:
            d = round(clips[k]["secs"], 2); o = V / f"{k}-full.mp4"; seg(k, d, o); ps.append(o); items.append((cap, d))
        burn(ps, items, S / "clips" / f"{app}.mp4")
        at = items[0][1] * 0.8
        subprocess.run(["ffmpeg", "-y", "-ss", f"{at:.2f}", "-i", str(S / "clips" / f"{app}.mp4"), "-frames:v", "1", "-q:v", "3", str(SH / f"{posters[app]}.jpg")], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-ss", "14.0", "-i", str(OUT), "-frames:v", "1", "-q:v", "3", str(SH / "poster-demo.jpg")], check=True, capture_output=True)
    print("planned", round(total, 2), "s ->", OUT)
