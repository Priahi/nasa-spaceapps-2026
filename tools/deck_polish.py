"""Deck polish pass (re-runnable): slide 3 (four big flood frames + playable 30 s demo), slide 5 fire walk loop, slide 6 (lead time and
drought insurance first, honest accuracy note, wide tasking map), slide 7 (static large-label system figure + one-row sector strip).
Uses submission/clips/loop-*.mp4 walkthrough loops when they exist (posters extracted to assets/shots/), else static fallbacks."""
import os, re, subprocess
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); S = R + '/submission/'
L = 'https://nasa-spaceapps-2026.pages.dev'
def have(n): return os.path.exists(f'{S}clips/{n}.mp4')
def poster(src, dst, t=None):
    out = f'{S}assets/shots/{dst}.jpg'
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout or 2)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t if t is not None else d * 0.6), '-i', src, '-frames:v', '1', '-q:v', '3', out], check=True)
    return f'assets/shots/{dst}.jpg'
def media(names, fallback, alt, fit='cover'):
    for n in names:
        if have(n):
            p = poster(f'{S}clips/{n}.mp4', n)
            web = f'<source src="clips/{n}.webm" type="video/webm">' if os.path.exists(f'{S}clips/{n}.webm') else ''
            return (f'<img class="lp-poster" src="{p}" alt="{alt}" style="object-fit:{fit}"><video class="lp" autoplay muted loop playsinline preload="auto" poster="{p}" style="object-fit:{fit}">'
                    f'{web}<source src="clips/{n}.mp4" type="video/mp4"></video>'), n
    return f'<img src="assets/shots/{fallback}" alt="{alt}" style="object-fit:{fit};object-position:center">', None
used = []
def M(names, fb, alt, fit='cover'):
    h, n = media(names, fb, alt, fit); used.append(n or fb); return h
def section(s, num, html):
    a = s.index(f'<!-- {num} ·'); b = s.index('<!-- ', a + 5) if num < 7 else s.index('</body>')
    return s[:a] + html + s[b:]
p = S + 'deck.html'; s = open(p).read()
css = '''
/* polish (16:10) */
.rw3{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1.32fr);grid-template-rows:minmax(0,1fr) minmax(0,1fr);gap:18px;margin-top:20px;flex:1;min-height:0}
.rw3 .shot img{object-position:center}
.rw3 .lab{position:absolute;left:12px;top:12px;z-index:2;background:rgba(255,255,255,.95);color:var(--ink);font:600 17px var(--body,inherit);padding:7px 12px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.18)}
.rw3 .lab i{font-style:normal;display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--water);color:#fff;font:700 15px var(--mono);margin-right:8px}
.rw3 .vid{grid-row:1 / span 2;grid-column:3;display:flex;flex-direction:column;justify-content:center;gap:14px;background:none;box-shadow:none;border-radius:0;overflow:visible;position:static}
.rw3 .vid .frame{position:relative;border-radius:16px;overflow:hidden;background:#000;box-shadow:0 18px 50px rgba(11,18,48,.22);aspect-ratio:16/9}
.rw3 .vid .frame video,.rw3 .vid .frame img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#000;display:block}
.rw3 .vid video{z-index:1}
.rw3 .vid .k{font:600 15px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--water)}
.rw3 .vid h3{font-size:32px;line-height:1.15;letter-spacing:-.02em}
.rw3 .vid p{font-size:21px;color:var(--muted);line-height:1.35}
@media print{.rw3 .vid video{display:none}}
.sysfig{flex:1;min-height:0;margin-top:12px;display:flex;align-items:center;justify-content:center;background:#fff;border:1px solid var(--line);border-radius:16px;padding:4px}
.sysfig img{max-width:100%;max-height:100%;display:block}
.strip1{display:flex;align-items:center;gap:10px;margin-top:14px;white-space:nowrap}
.strip1 b{font-size:19px;margin-right:4px}
.strip1 .c{border-radius:999px;padding:7px 13px;font:600 17px var(--mono);background:#e6f4ea;color:#1e6b34}
.strip1 .c.f{background:transparent;color:#6b7280;border:1.5px dashed #aab1c4}
.strip1 .who{margin-left:auto;text-align:right;font-size:19px;color:var(--muted)}.strip1 .who b{font-size:24px;color:var(--ink)}
.honest{font-size:20px;color:var(--muted);line-height:1.35;border-left:4px solid #c9d3c0;padding:4px 0 4px 14px}.honest b{color:var(--ink)}
'''
if '/* polish (16:10) */' in s: a0 = s.index('/* polish (16:10) */'); s = s[:a0] + s[s.index('</style>', a0):]
s = s.replace('</style>', css + '.fw.s4 .cmp{font-size:17px;border-spacing:0 6px}.fw.s4 .cmp td{padding:7px 12px}\n.fw.s4 .tl{margin-top:16px}\n</style>', 1)
def hd(left, n): return f' <div class="hd"><span>{left}</span><span>{n} / 7</span></div>\n'
# ---- slide 3
fr = [(['loop-flood-slider', 'loop-flood-classify'], 'comp-flood-map.png', 'See: radar before / after'),
      (['loop-flood-actions'], 'comp-flood-signal.png', 'Decide: recommended actions'),
      (['loop-flood-task'], 'comp-flood-dispatch.png', 'Act: teams and passes queued'),
      (['loop-flood-alert'], 'flood-alert.png', 'Alert: all 8 towns at once')]
cells = ''
for i, (names, fb, lab) in enumerate(fr):
    tk = '<span class="tk">Simulated</span>' if i >= 2 else ''
    cells += f'  <div class="shot">{M(names, fb, lab)}<span class="lab"><i>{i+1}</i>{lab}</span>{tk}</div>\n'
dp = poster(S + 'demo.mp4', 'demo-poster', 1.2)
s3 = f'''<!-- 3 · Rewind -->
<section class="s">
{hd('Story 1 · rewind, with Orbit to Ground', 3)} <h2 class="title" style="font-size:52px">Rewind. Same night, same data, with Orbit to Ground.</h2>
 <div class="rw3">
{cells}  <div class="vid">
   <span class="k">The official 30-second demo</span>
   <div class="frame"><img src="{dp}" alt="Demo video poster"><video controls preload="metadata" playsinline poster="{dp}"><source src="demo.mp4" type="video/mp4"></video></div>
   <h3>Elena <b>could have</b> had a drafted alert for her town hours before the ~8 PM phone alert.</h3>
   <p>Rain signal → radar map → one alert to 8 towns → teams queued. Press play, or <a href="{L}/sar-change/app/#demo" style="color:var(--accent)">open the flood demo →</a></p>
  </div>
 </div>
 <div class="ft"><span class="pill">Hypothetical rewind · tasking and alerts are simulated</span><span class="src">NASA GPM IMERG V07 · NASA POWER · NASA/JPL OPERA DSWx-S1 · Sentinel-1</span></div>
</section>

'''
s = section(s, 3, s3)
# ---- slide 5: fire walkthrough loop in the AB/BC frame
a = s.index('<!-- 5 ·'); b = s.index('<!-- 6 ·')
s5 = s[a:b]
m = re.search(r'<div class="shot">(?:(?!</div>).)*?Alberta \+ B\.C\. · staffing</span><span class="tk">Tasking \(simulated\)</span></div>', s5, re.S)
if m: s5 = s5.replace(m.group(0), f'<div class="shot">{M(["loop-fire-walk"], "loop-fire.jpg", "Hot Spots walkthrough: Alberta and B.C. staffing, tasks queued (simulated)")}<span class="tag">Alberta + B.C. · staffing</span><span class="tk">Tasking (simulated)</span></div>')
s = s[:a] + s5 + s[b:]
# ---- slide 6
s6 = f'''<!-- 6 · Fields vertical -->
<section class="s">
{hd('Story 3 · Field Shift · the whole farm vertical', 6)} <h2 class="title" style="font-size:46px;margin-top:14px"><span class="k crop" style="margin-bottom:8px">Story County, Iowa · every 30 m pixel</span>Next season's crop map before planting, and rye on the steepest fields as drought insurance.</h2>
 <div class="vert">
  <div class="l">
   <div class="shot">{M(["loop-field-walk"], "field-crop-map.png", "Field Shift walkthrough: crop map, forecast and scout list")}<span class="tag">Field Shift · crop map → scout list</span></div>
   <div class="shot"><img src="assets/shots/field-map-wide-crop.png" alt="Drone survey and scouts tasked to 114 squares" style="object-position:center"><span class="tag" style="top:auto;bottom:12px">Drone + scouts · 114 squares</span><span class="tk">Tasking (simulated)</span></div>
  </div>
  <div class="r">
   <div class="mini">
    <div class="card"><span class="k crop-t">Lead time</span><strong>Before planting</strong><p>Our map is ready in February. The USDA crop map (CDL) for a season arrives ~11 months later.</p></div>
    <div class="card"><span class="k crop-t">Drought insurance</span><strong>~$1.2 M</strong><p>net, rye on the 92 steepest squares in a 2012-type drought</p></div>
   </div>
   <div class="card wf"><span class="k crop-t">What if · illustrative</span><h3>It costs a little in most years and pays back in a dry one.</h3>
    <p class="ar">(~11 bu × ~$6.90 − ~$32) ≈ $44 an acre<br>× ~26,500 acres ≈ $1.2 M</p>
    <p>About 2.4× its seed and planting cost back in 2012 (SARE survey). Iowa's 2012 corn fell 20%.</p></div>
   <p class="honest"><b>Accuracy, honestly:</b> ~82% of 30 m pixels get next season's crop right, vs ~81% from crop history alone. A small edge; the value is having the map before planting, with the climate trend attached (+19 frost-free days since 1981). USDA's Prospective Plantings comes 31 March, state-level only.</p>
   <div class="dl" style="margin-top:auto"><a class="btn" href="{L}/field-shift/app/#demo">Open Field Shift →</a><a class="btn ghost" href="{L}/submission/clips/field-shift.mp4">▶ Demo clip</a></div>
  </div>
 </div>
 <div class="ft"><span class="pill">Illustrative estimate · scouting and drone tasks are simulated</span><span class="src">USDA NASS CDL + Crop Production 2012 · USDA FSA · SARE/CTIC 2012–13 survey · Iowa State (Plastina 2018) · NASA HLS · NASA POWER</span></div>
</section>

'''
s = section(s, 6, s6)
# ---- slide 7
chips = ''.join(f'<span class="c">✓ {x}</span>' for x in ['Flood', 'Wildfire', 'Farms', 'Groundwater']) + '<b style="margin-left:10px">Next:</b>' + ''.join(f'<span class="c f">{x}</span>' for x in ['Drought', 'Smoke', 'Infrastructure', 'Landslides'])
s7 = f'''<!-- 7 · System + close -->
<section class="s">
{hd('One system · how it works', 7)} <h2 class="title" style="font-size:40px;margin-top:10px">Shared NASA inputs, one engine, one loop: signal → map → alert → task.</h2>
 <div class="sysfig"><img src="assets/shots/arch-system.png" alt="Shared inputs feed one engine of trend detection and per-signal models, then the signal, map, alert, task loop, then outputs and results per vertical"></div>
 <div class="strip1"><b>Same engine, every sector:</b>{chips}<div class="who"><b>Parsa Riahi</b> · built solo</div></div>
 <div class="ft"><span class="src">One seed each, not a published benchmark · civil uses only · tasking and alerts are simulated · not affiliated with NASA</span><span><a href="deck.pptx" download style="color:var(--accent)">Slides with video (PPTX)</a> · <a href="deck.pdf" style="color:var(--accent)">PDF</a> · <span class="grad" style="font-weight:600">See it. Decide. Act.</span></span></div>
</section>
'''
s = section(s, 7, s7)
assert s.count('<section') == 7
open(p, 'w').write(s); print('media:', used)
