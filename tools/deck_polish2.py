"""Second polish pass (run after tools/deck_polish.py; re-runnable): slide 3 = one dispatch loop + a near-full-size demo video;
slide 4 leads with the €4.8 bn insured loss and ~€1.1 bn within reach; slides 5 and 6 simplified to headline + 3 big stat cards +
visual + one plain what-if line, with the arithmetic in a small muted 'How we estimated' corner box. Adds deck navigation
(next/prev buttons, arrow keys) and an IntersectionObserver that restarts each slide's loops when it becomes active."""
import os, re
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); S = R + '/submission/'
L = 'https://nasa-spaceapps-2026.pages.dev'
def lp(n, alt, fit='cover'):
    p = f'assets/shots/{n}.jpg'
    return (f'<img class="lp-poster" src="{p}" alt="{alt}" style="object-fit:{fit}"><video class="lp" autoplay muted loop playsinline preload="auto" poster="{p}" style="object-fit:{fit}">'
            f'<source src="clips/{n}.webm" type="video/webm"><source src="clips/{n}.mp4" type="video/mp4"></video>')
def section(s, num, html):
    a = s.index(f'<!-- {num} ·'); b = s.index('<!-- ', a + 5) if num < 7 else s.index('</body>')
    return s[:a] + html + s[b:]
def hd(left, n): return f' <div class="hd"><span>{left}</span><span>{n} / 7</span></div>\n'
p = S + 'deck.html'; s = open(p).read()
css = '''
/* polish2 */
.r3{display:grid;grid-template-columns:minmax(0,.5fr) minmax(0,1.7fr);gap:26px;margin-top:18px;flex:1;min-height:0}
.r3 .left{display:flex;flex-direction:column;gap:14px;min-height:0}
.r3 .left .shot{flex:1;min-height:0}
.r3 .left .shot img{object-position:center}
.r3 .left p{font-size:21px;line-height:1.3}
.r3 .vbig{display:flex;flex-direction:column;justify-content:center;min-height:0}
.r3 .vbig .frame{position:relative;width:100%;aspect-ratio:16/9;border-radius:18px;overflow:hidden;background:#000;box-shadow:0 18px 50px rgba(11,18,48,.25)}
.r3 .vbig .frame video,.r3 .vbig .frame img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#000;display:block}
.r3 .vbig .frame video{z-index:1}
.r3 .vbig .cap{display:flex;justify-content:space-between;align-items:baseline;margin-top:10px;font-size:19px;color:var(--muted)}
.r3 .vbig .cap .k{font:600 15px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--water)}
@media print{.r3 .vbig .frame video{display:none}}
.v2{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:28px;margin-top:20px;flex:1;min-height:0}
.v2 .vis{display:grid;grid-template-rows:minmax(0,1fr) minmax(0,1fr);gap:16px;min-height:0}
.v2 .side{display:flex;flex-direction:column;gap:14px;min-height:0}
.big3{display:flex;flex-direction:column;gap:14px}
.big3 .st{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:16px 22px}
.big3 .st strong{display:block;font-size:50px;line-height:1.02;letter-spacing:-.035em}
.big3 .st span{display:block;font-size:21px;color:var(--muted);line-height:1.3;margin-top:4px}
.whatif{font-size:24px;line-height:1.3;padding:14px 20px;border-radius:16px;background:#f3fbf5;border:1px solid #bfe3c9}
.whatif b{display:block;font:600 14px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:#1e6b34;margin-bottom:4px}
.est{margin-top:auto;align-self:flex-end;max-width:100%;font-size:14.5px;line-height:1.38;color:#6b7280;background:rgba(255,255,255,.7);border:1px dashed #c5cbd8;border-radius:12px;padding:10px 14px}
.est b{font:600 12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:#8a93a6;display:block;margin-bottom:3px}
.f4{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:28px;margin-top:22px;align-items:center}
.f4 .hero strong{display:block;font-size:140px;line-height:.95;letter-spacing:-.05em}
.f4 .hero .lbl{font-size:24px;color:var(--muted);margin-top:6px}
.f4 .hero .reach{margin-top:18px;font-size:30px;line-height:1.2}.f4 .hero .reach b{font-size:84px;letter-spacing:-.04em;color:#1e6b34}
.f4 .hero .ill{display:inline-block;margin-top:10px;font:700 14px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:#8a5a00;background:#fff7e6;border:1px solid #f5d79a;border-radius:8px;padding:5px 10px}
.f4 .cmp{font-size:18px;border-spacing:0 8px}.f4 .cmp td{padding:10px 12px}
.dnav{position:fixed;right:18px;bottom:18px;display:flex;gap:8px;z-index:50}
.dnav button{font:600 18px var(--mono);width:48px;height:48px;border-radius:50%;border:1px solid var(--line);background:#fff;box-shadow:0 4px 14px rgba(0,0,0,.12);cursor:pointer}
.dnav span{align-self:center;font:600 14px var(--mono);color:var(--muted);background:#fff;border-radius:8px;padding:4px 8px}
@media print{.dnav{display:none}}
'''
if '/* polish2 */' in s: a0 = s.index('/* polish2 */'); s = s[:a0] + s[s.index('</style>', a0):]
s = s.replace('</style>', css + '</style>', 1)
# ---- slide 3
s3 = f'''<!-- 3 · Rewind -->
<section class="s">
{hd('Story 1 · rewind, with Orbit to Ground', 3)} <h2 class="title" style="font-size:50px">Rewind. Same night, same data, with Orbit to Ground.</h2>
 <div class="r3">
  <div class="left">
   <div class="shot">{lp('loop-flood-task', 'Dispatch: teams and passes queued to the flagged towns (simulated)')}<span class="tag">Dispatch · teams + passes</span><span class="tk">Simulated</span></div>
   <p>Elena <b>could have</b> had a drafted alert for her town hours before the ~8 PM phone alert.</p>
  </div>
  <div class="vbig">
   <div class="frame"><img src="assets/shots/demo-poster.jpg" alt="Official demo video poster"><video controls preload="metadata" playsinline poster="assets/shots/demo-poster.jpg"><source src="demo.mp4" type="video/mp4"></video></div>
   <div class="cap"><span class="k">The official 30-second demo · press play</span><a href="{L}/sar-change/app/#demo" style="color:var(--accent)">Open the flood demo →</a></div>
  </div>
 </div>
 <div class="ft"><span class="pill">Hypothetical rewind · tasking and alerts are simulated</span><span class="src">NASA GPM IMERG V07 · NASA POWER · NASA/JPL OPERA DSWx-S1 · Sentinel-1</span></div>
</section>

'''
s = section(s, 3, s3)
# ---- slide 4
s4 = f'''<!-- 4 · Flood what-if -->
<section class="s">
{hd('Story 1 · what if it had been there?', 4)} <h2 class="title" style="font-size:48px;margin-top:14px">12 hours earlier = an alert before the first death.</h2>
 <div class="f4">
  <div class="hero">
   <strong>€4.8 bn</strong>
   <div class="lbl">insured loss in the Valencia floods (Consorcio de Compensación de Seguros)</div>
   <div class="reach"><b>≈ €1.1 bn</b><br>within reach of an alert 12 hours earlier</div>
   <span class="ill">Illustrative estimate</span>
  </div>
  <div>
   <table class="cmp"><tr><th>Today</th><th>Gap on 29 Oct</th><th>Orbit to Ground adds</th></tr>
    <tr><td>AEMET warning</td><td class="gap">red at ~7:30 AM, by zone; not an instruction to the public</td><td class="us">a drafted, town-specific alert (simulated)</td></tr>
    <tr><td>EFAS notices</td><td class="gap">emailed to agencies, not binding</td><td class="us">observed NASA rain + radar on one screen, with a task queue</td></tr>
    <tr><td>ES-Alert</td><td class="gap">~8 PM, "avoid any travel" only</td><td class="us">message and target towns pre-filled from the map (simulated)</td></tr>
    <tr><td>Copernicus EMS</td><td class="gap">first maps 31 Oct; province-wide 2 Nov</td><td class="us">radar water each pass, linked to rain and dispatch</td></tr>
   </table>
  </div>
 </div>
 <div class="tl" style="margin-top:26px">
  <div class="t"><time style="font-size:44px">~7:30 AM</time><h4 style="font-size:24px">Red warning</h4><p style="font-size:19px">The danger is known.</p></div>
  <div class="t"><time style="font-size:44px;color:#1e6b34">~8 AM</time><h4 style="font-size:24px">What if: the town alert goes out</h4><p style="font-size:19px">12 h earlier; drafted by the dashboard (simulated)</p></div>
  <div class="t"><time style="font-size:44px">~noon</time><h4 style="font-size:24px">First recorded death</h4><p style="font-size:19px">a driver at the Benimodo ravine</p></div>
  <div class="t late"><time style="font-size:44px">~8 PM</time><h4 style="font-size:24px">The real phone alert</h4><p style="font-size:19px">more than 150 already dead</p></div>
 </div>
 <div class="est" style="max-width:62%"><b>How we estimated</b>Published warning curves: 13% of damage avoidable at 6 h, 22% at 12 h, 30% at 24 h, ~33% at 48 h (levels off; does not stack per day). 22% × €4.8 bn ≈ €1.1 bn. That's ~€19,000 per claim over ~250,000 claims; ~78 km² of new water = more than half the city of València. No lives number for Valencia. Sources: Day (1970) via NHWC · GCA 2019 · Pappenberger 2015 · CCS · El País · València Recull 2024.</div>
 <div class="ft"><span class="pill">Illustrative estimate · alerts simulated</span><span class="src"><a href="{L}/sar-change/app/#demo" style="color:var(--accent)">The flood app's What if? panel →</a></span></div>
</section>

'''
s = section(s, 4, s4)
# ---- slide 5
s5 = f'''<!-- 5 · Fire vertical -->
<section class="s">
{hd('Story 2 · Hot Spots · wildfire', 5)} <h2 class="title" style="font-size:50px;margin-top:14px">Fire: staff crews from the record, not a fixed date.</h2>
 <div class="v2">
  <div class="vis">
   <div class="shot"><img src="assets/shots/fire-canada-extent.png" alt="Fires per year across Canada, B.C. to Quebec" style="object-fit:cover;object-position:center"><span class="tag">Canada · fires per year, 2003–2025</span></div>
   <div class="shot">{lp('loop-fire-walk', 'Hot Spots walkthrough: Alberta and B.C. staffing, tasks queued (simulated)')}<span class="tag">Alberta + B.C. · staffing walkthrough</span><span class="tk">Tasking (simulated)</span></div>
  </div>
  <div class="side">
   <div class="big3">
    <div class="st"><strong>~1,500 more</strong><span>fires detected each year in Alberta (rising trend)</span></div>
    <div class="st"><strong>May</strong><span>Alberta's watch month: 5 of its 16 unusual fire months</span></div>
    <div class="st"><strong>+16 days</strong><span>of full readiness if crews are staffed 15 April</span></div>
   </div>
   <div class="whatif"><b>What if · illustrative</b>Crews in place before the first big May fire, every season.</div>
   <div class="est"><b>How we estimated</b>~1,100 fires × 3% ≈ 33 escapes carrying ~97% of 2.2 M ha ≈ 65,000 ha each. 2016 Horse River (~5,900 km², more than PEI, $8.9 bn) started 1 May; initial attack was immediate, so we don't claim it would have been stopped. Today: FIRMS shows fires now, CWFIS fire weather; staffing is a fixed date. Trends p = 0.035 (AB), 0.045 (B.C.).</div>
   <div class="dl"><a class="btn" href="{L}/hotspots/app/#demo">Open Hot Spots →</a></div>
  </div>
 </div>
 <div class="ft"><span class="pill">Illustrative estimate · staffing tasks simulated</span><span class="src">NASA FIRMS (MODIS + VIIRS) · MNP 2017 · KPMG · IBC · Statistics Canada areas</span></div>
</section>

'''
s = section(s, 5, s5)
# ---- slide 6
s6 = f'''<!-- 6 · Fields vertical -->
<section class="s">
{hd('Story 3 · Field Shift · farms', 6)} <h2 class="title" style="font-size:50px;margin-top:14px">Fields: next season's crop map, before planting.</h2>
 <div class="v2">
  <div class="vis">
   <div class="shot">{lp('loop-field-walk', 'Field Shift walkthrough: crop map, forecast and scout list')}<span class="tag">Field Shift walkthrough · Story County, Iowa</span></div>
   <div class="shot"><img src="assets/shots/field-map-wide-crop.png" alt="Drone survey and scouts tasked to 114 squares" style="object-position:center"><span class="tag" style="top:auto;bottom:12px">Drone + scouts · 114 squares</span><span class="tk">Tasking (simulated)</span></div>
  </div>
  <div class="side">
   <div class="big3">
    <div class="st"><strong>Before planting</strong><span>our map is ready in February; USDA's crop map arrives ~11 months later</span></div>
    <div class="st"><strong>~$1.2 M</strong><span>drought insurance: rye on the 92 steepest squares in a 2012-type drought</span></div>
    <div class="st"><strong>~82% <small style="font-size:26px;color:var(--muted)">vs ~81%</small></strong><span>next crop right per 30 m pixel, vs crop history alone: a small edge</span></div>
   </div>
   <div class="whatif"><b>What if · illustrative</b>Rye on the steepest fields costs a little most years and pays back in a dry one.</div>
   <div class="est"><b>How we estimated</b>(~11 bu × ~$6.90 − ~$32) ≈ $44 an acre × ~26,500 acres ≈ $1.2 M. About 2.4× its seed and planting cost back in 2012 (SARE survey); Iowa's 2012 corn fell 20%. USDA Prospective Plantings: 31 March, state-level. Frost-free season +19 days since 1981.</div>
   <div class="dl"><a class="btn" href="{L}/field-shift/app/#demo">Open Field Shift →</a></div>
  </div>
 </div>
 <div class="ft"><span class="pill">Illustrative estimate · scouting and drone tasks simulated</span><span class="src">USDA NASS CDL + Crop Production 2012 · SARE/CTIC · Iowa State · NASA HLS · NASA POWER</span></div>
</section>

'''
s = section(s, 6, s6)
# ---- navigation + loop restarts
js = '''<div class="dnav"><button id="deckPrev" aria-label="Previous slide">‹</button><span id="deckNum">1 / 7</span><button id="deckNext" aria-label="Next slide">›</button></div>
<script>
(function(){
  var S=[].slice.call(document.querySelectorAll('section.s')), cur=0;
  function go(i){ i=Math.max(0,Math.min(S.length-1,i)); cur=i; S[i].scrollIntoView({block:'start'}); num(); }
  function num(){ var n=document.getElementById('deckNum'); if(n) n.textContent=(cur+1)+' / '+S.length; }
  document.getElementById('deckNext').onclick=function(){ go(cur+1); };
  document.getElementById('deckPrev').onclick=function(){ go(cur-1); };
  addEventListener('keydown',function(e){ if(e.key==='ArrowRight'||e.key==='PageDown'||e.key===' '){e.preventDefault();go(cur+1);} if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();go(cur-1);} });
  var loops=[].slice.call(document.querySelectorAll('video.lp'));
  loops.forEach(function(v){ v.muted=true; v.loop=true; v.playsInline=true; v.preload='auto';
    v.addEventListener('ended',function(){ v.currentTime=0; v.play(); }); });
  function start(sec){ sec.querySelectorAll('video.lp').forEach(function(v){ v.muted=true; v.loop=true; try{ v.currentTime=0; }catch(e){} var p=v.play(); if(p&&p.catch) p.catch(function(){}); }); }
  var io=new IntersectionObserver(function(es){ es.forEach(function(e){ var i=S.indexOf(e.target);
    if(e.isIntersecting&&e.intersectionRatio>=.5){ cur=i; num(); start(e.target); }
    else if(!e.isIntersecting){ e.target.querySelectorAll('video.lp').forEach(function(v){ v.pause(); }); } }); },{threshold:[0,.5]});
  S.forEach(function(x){ io.observe(x); });
})();
</script>
'''
if '<div class="dnav">' in s: s = s[:s.index('<div class="dnav">')] + s[s.index('</script>', s.index('<div class="dnav">')) + 10:]
s = s.replace('</body>', js + '</body>')
assert s.count('<section') == 7
open(p, 'w').write(s); print('ok')
