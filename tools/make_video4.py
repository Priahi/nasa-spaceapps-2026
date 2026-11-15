"""Demo videos v4 from tools/video_record4.mjs takes (1920x960 screencasts with a visible cursor) + tools/video_cards4.mjs cards.
Outputs: submission/demo.mp4 (<= 30 s, flood-led) + demo.en.srt/.vtt; submission/clips/{sar-change,hotspots,field-shift}.mp4 + posters;
submission/clips/loop-*.{mp4,webm} walkthrough loops (muted, no zoom/pan) + assets/shots/loop-*.jpg posters.
Captions sit in a 120 px bar under the app (never over the UI). Times are rounded 12-hour story times; tasking/alerts are simulated."""
import json, re, subprocess
from pathlib import Path
R = Path(__file__).resolve().parents[1]; S = R / "submission"; V = S / "build/video4"; OUT = S / "demo.mp4"
FONTS = R / "src/assets/fonts"; SH = S / "assets/shots"; CL = S / "clips"; CL.mkdir(exist_ok=True)
T = json.load(open(V / "takes.json"))
WM = "Tasking and alerts are simulated"; URL = "spaceapps.parsariahi.com"
def run(c): subprocess.run(c, check=True, capture_output=True)
def mk(name, a, b): m = T[name]["marks"]; return (m[a] if isinstance(a, str) else a), (m[b] if isinstance(b, str) else b)
def take(name, s0, s1, out, speed=1.0, bar=True, w=1920):
    d = (s1 - s0) / speed
    vf = f"trim=start={s0:.3f}:end={s1 + 0.3:.3f},setpts=(PTS-STARTPTS)/{speed:.4f},fps=30,scale={w}:-2:flags=lanczos" + (",pad=1920:1080:0:0:color=0x0b1020" if bar else "") + ",format=yuv420p,setsar=1"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{T[name]['dir']}/list.ffconcat",
         "-vf", vf + f",tpad=stop_mode=clone:stop_duration=1", "-t", f"{d:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(out)])
    return d
def card(k, d, out):
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-t", f"{d}", "-i", str(V / f"card-{k}.png"), "-vf", "scale=1920:1080,format=yuv420p,setsar=1", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-an", str(out)]); return d
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
def st(x): return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int(round((x%1)*1000)):03d}"
def ass(items, total, path):
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 2", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: Cap,Geist,40,&H00FBF6F4,&H00FBF6F4,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,60,60,54,1",
         "Style: Wm,Geist Mono,20,&H00E6DCD4,&H00E6DCD4,&H501A0907,&H501A0907,0,0,0,0,100,100,0,0,3,6,0,1,22,22,10,1",
         "Style: Url,Geist Mono,22,&H00FFD7A8,&H00FFD7A8,&H501A0907,&H501A0907,1,0,0,0,100,100,0,0,3,6,0,3,22,22,10,1", "",
         "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for t0, t1, cap in items: L.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Cap,,0,0,0,,{cap}")
    L.append(f"Dialogue: 0,{ts(0)},{ts(total)},Wm,,0,0,0,,{WM}"); L.append(f"Dialogue: 0,{ts(0)},{ts(total)},Url,,0,0,0,,{URL}"); Path(path).write_text("\n".join(L) + "\n")
def build(segs, out, tag):
    """segs: [(kind, args, caption)] kind 'card' (key, dur) or 'take' (name, a, b, speed)"""
    parts, caps, t = [], [], 0.0
    for i, (kind, a, cap) in enumerate(segs):
        o = V / f"{tag}-{i:02d}.mp4"
        if kind == "card": d = card(a[0], a[1], o)
        else: n, x, y, sp = a; s0, s1 = mk(n, x, y); d = take(n, s0, s1, o, sp)
        parts.append(o)
        if cap: caps.append((t, t + d, cap, kind == "take"))
        t += d
    lst = V / f"{tag}-parts.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts)); a = V / f"{tag}.ass"; ass([c[:3] for c in caps if c[3]], t, a)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", f"subtitles={a}:fontsdir={FONTS}", "-c:v", "libx264", "-preset", "slow",
         "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", "-an", str(out)])
    return t, caps
C = {  # captions (12-hour rounded story times only; no exact clock times)
 "slider": "Rewind with my tool. 1 · Drag the radar slider: before (26 Oct) ↔ after (31 Oct), through cloud",
 "classify": "2 · Flood classification: new water outside normal rivers, about 47 km² more in 5 days",
 "preview": "3 · Preview each recommended action on the map",
 "dispatch": "4 · Dispatch: teams placed in the 8 towns. Queued → Tasked → In progress → Done",
 "alert": "5 · Alert everyone: one draft for all 8 towns, then Send (simulated)",
}
import os; ONLY = [x for x in os.environ.get("ONLY", "").split(",") if x]
if __name__ == "__main__":
    # 1. official demo (<= 30 s)
    DEMO = [("card", ("night", 3.0), "Imagine losing someone you love because no one knew how much rain was coming that day. Red warning about 7:30 AM; phone alert about 8 PM."),
            ("take", ("flood", 0.9, 7.6, 1.97), C["slider"]),
            ("take", ("flood", "classify", T["flood"]["marks"]["classify"] + 4.4, 1.83), C["classify"]),
            ("take", ("flood", "preview", T["flood"]["marks"]["preview"] + 5.6, 1.87), C["preview"]),
            ("take", ("flood", "dispatch", 38.6, 1.875), C["dispatch"]),
            ("take", ("flood", "alert", "end", 2.0), C["alert"]),
            ("card", ("impact", 3.0), "What if (illustrative estimate): an alert 12 hours earlier, about 8 AM, comes before the first death. About €1.1 bn of the €4.8 bn insured loss within reach."),
            ("take", ("fire", "dispatch", T["fire"]["marks"]["dispatch"] + 3.0, 1.76), "Fire: crews staged in Alberta and B.C. before the July peak"),
            ("take", ("field", "dispatch", T["field"]["marks"]["dispatch"] + 3.0, 1.76), "Farms: drone and scout sent to about 110 uncertain squares"),
            ("card", ("close", 2.3), "One engine, every sector: signal → map → task → alert. Try it live: spaceapps.parsariahi.com · Parsa Riahi · solo build.")]
    total, caps = build(DEMO, OUT, "demo")
    assert total <= 30.0, total
    (S / "demo.en.srt").write_text("\n".join(f"{i + 1}\n{st(a)} --> {st(b)}\n{c}\n" for i, (a, b, c, _) in enumerate(caps)))
    (S / "demo.en.vtt").write_text("WEBVTT\n\n" + re.sub(r"(\d\d:\d\d:\d\d),(\d\d\d)", r"\1.\2", (S / "demo.en.srt").read_text()))
    run(["ffmpeg", "-y", "-ss", f"{caps[4][0] + 2.5:.2f}", "-i", str(OUT), "-frames:v", "1", "-q:v", "3", str(SH / "poster-demo.jpg")])
    print("demo", round(total, 2), "s")
    # 2. per-app clips (light speed-up)
    m = lambda n, k: T[n]["marks"][k]
    APPS = {
     "sar-change": ("poster-sar", [("take", ("flood", 0.0, "classify", 1.25), C["slider"]), ("take", ("flood", "classify", "preview", 1.25), C["classify"]),
                    ("take", ("flood", "preview", "dispatch", 1.25), C["preview"]), ("take", ("flood", "dispatch", "alert", 1.25), C["dispatch"]),
                    ("take", ("flood", "alert", "end", 1.25), C["alert"]), ("card", ("close", 2.5), "")]),
     "hotspots": ("poster-hotspots", [("take", ("fire", 0.0, "preview", 1.5), "1 · Full Canada fire map (NASA FIRMS), then the province trend"),
                  ("take", ("fire", "preview", m("fire", "preview") + 8.4, 1.5), "2 · Preview the recommended actions on the map"),
                  ("take", ("fire", "dispatch", "alert", 1.5), "3 · Approve crews: placed in Alberta and B.C., queue runs to Done (simulated)"),
                  ("take", ("fire", "alert", "end", 1.5), "4 · Draft the duty-officer alert, then Send (simulated)")]),
     "field-shift": ("poster-field", [("take", ("field", 0.0, "preview", 1.5), "1 · Crop map: every 30 m field, Crops 2025"),
                  ("take", ("field", "preview", "dispatch", 1.5), "2 · Act tab: preview each recommended action on the map"),
                  ("take", ("field", "dispatch", "alert", 1.5), "3 · Scout: drone survey + walk-through tasked, queue to Done (simulated)"),
                  ("take", ("field", "alert", "end", 1.5), "4 · Draft the grower advisory, then Send (simulated)")]),
    }
    for app, (poster, segs) in APPS.items():
        if any(s[0] == "take" and s[1][0] not in T for s in segs): print("skip", app); continue
        if ONLY and app not in ONLY: continue
        d, cp = build(segs, CL / f"{app}.mp4", app)
        run(["ffmpeg", "-y", "-ss", f"{cp[2][0] + 2.0:.2f}", "-i", str(CL / f"{app}.mp4"), "-frames:v", "1", "-q:v", "3", str(SH / f"{poster}.jpg")])
        print(app, round(d, 2), "s")
    # 3. walkthrough loops: real cursor + clicks, no zoom/pan, 1440 px wide, muted
    LOOPS = {"flood-slider": [("flood", 0.9, 7.6, 1.0)], "flood-classify": [("flood", "classify", m("flood", "classify") + 6.0, 1.0)],
             "flood-actions": [("flood", "preview", m("flood", "preview") + 8.0, 1.2)], "flood-task": [("flood", "dispatch", m("flood", "dispatch") + 9.0, 1.25)],
             "flood-alert": [("flood", "alert", "end", 1.1)],
             "fire-walk": [("fire", 0.4, 3.2, 1.15), ("fire", "preview", m("fire", "preview") + 2.6, 1.15), ("fire", "dispatch", m("fire", "dispatch") + 3.4, 1.15)],
             "field-walk": [("field", 0.4, 3.0, 1.15), ("field", "preview", m("field", "preview") + 3.4, 1.15), ("field", "dispatch", m("field", "dispatch") + 3.2, 1.15)]}
    for name, ws in ({} if ONLY else LOOPS).items():
        if any(w[0] not in T for w in ws): print("skip", name); continue
        ps = []
        for i, (n, a, b, sp) in enumerate(ws): s0, s1 = mk(n, a, b); o = V / f"loop-{name}-{i}.mp4"; take(n, s0, s1, o, sp, bar=False, w=1440); ps.append(o)
        lst = V / f"loop-{name}.txt"; lst.write_text("".join(f"file '{p}'\n" for p in ps))
        mp4, webm = CL / f"loop-{name}.mp4", CL / f"loop-{name}.webm"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-an", "-r", "24", "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)])
        run(["ffmpeg", "-y", "-i", str(mp4), "-an", "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "40", "-row-mt", "1", str(webm)])
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout)
        run(["ffmpeg", "-y", "-ss", f"{dur * 0.7:.2f}", "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(SH / f"loop-{name}.jpg")])
        print(name, round(dur, 2), "s", round(mp4.stat().st_size / 1e6, 2), "MB mp4", round(webm.stat().st_size / 1e6, 2), "MB webm")
