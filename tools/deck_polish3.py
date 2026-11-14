"""Third polish pass (run after deck_polish.py and deck_polish2.py; re-runnable).
Slide 1: the plain radar map (same live frame as slide 3, no markers yet).
Slide 3: two square stills of that same frame (What changed + recommended action), and the official demo as the only moving thing:
 it autoplays muted from 0 when slide 3 becomes active, pauses when it leaves, with an Unmute button.
Slides 5/6: one recorded click-through each (calendar -> staffing -> What if; slope map -> Act -> task -> What if), three big cards with
 the impact in money and area, one what-if line, arithmetic in the corner box."""
import os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); S = R + '/submission/'
L = 'https://nasa-spaceapps-2026.pages.dev'
def lp(n, alt):
    p = f'assets/shots/{n}.jpg'
    return (f'<img class="lp-poster" src="{p}" alt="{alt}" style="object-fit:contain"><video class="lp" autoplay muted loop playsinline preload="auto" poster="{p}" style="object-fit:contain">'
            f'<source src="clips/{n}.webm" type="video/webm"><source src="clips/{n}.mp4" type="video/mp4"></video>')
def section(s, num, html):
    a = s.index(f'<!-- {num} ·'); b = s.index('<!-- ', a + 5) if num < 7 else s.index('</body>')
    return s[:a] + html + s[b:]
def hd(left, n): return f' <div class="hd"><span>{left}</span><span>{n} / 7</span></div>\n'
p = S + 'deck.html'; s = open(p).read()
css = '''
/* polish3 */
.r4{display:grid;grid-template-columns:350px minmax(0,1fr);gap:30px;margin-top:16px;flex:1;min-height:0}
.r4 .sq{display:flex;flex-direction:column;gap:16px}
.r4 .sq figure{margin:0}
.r4 .sq figcaption{font:600 15px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--water);margin-bottom:6px}
.r4 .sq figcaption i{font-style:normal;color:#8a5a00}
.r4 .sq img{display:block;width:350px;height:350px;border-radius:14px;box-shadow:0 12px 34px rgba(11,18,48,.22),0 0 0 1px rgba(11,18,48,.08)}
.r4 .vbig{display:flex;flex-direction:column;justify-content:center;min-height:0}
.r4 .frame{position:relative;width:100%;aspect-ratio:16/9;border-radius:18px;overflow:hidden;background:#000;box-shadow:0 18px 50px rgba(11,18,48,.25)}
.r4 .frame video,.r4 .frame img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#000;display:block}
.r4 .frame video{z-index:1}
.r4 .unmute{position:absolute;right:16px;top:16px;z-index:3;font:700 16px var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:10px 16px;border-radius:999px;border:0;background:rgba(255,255,255,.94);color:var(--ink);cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.25)}
.r4 .cap{display:flex;justify-content:space-between;align-items:baseline;gap:24px;margin-top:12px;font:400 22px/1.35 var(--font);letter-spacing:0;text-transform:none;color:var(--ink)}
.r4 .cap .k{font:600 15px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--water);display:block;margin-bottom:2px}
@media print{.r4 .frame video,.r4 .unmute{display:none}}
.v3{display:grid;grid-template-columns:minmax(0,1.32fr) minmax(0,1fr);gap:30px;margin-top:18px;flex:1;min-height:0}
.v3 .vis{display:flex;flex-direction:column;justify-content:center;min-height:0}
.v3 .vis .shot{width:100%;aspect-ratio:16/10;flex:none;background:#0b0e20}
.v3 .vis .how{margin-top:10px;font:600 15px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--water)}
.v3 .side{display:flex;flex-direction:column;gap:14px;min-height:0}
.v3 .big3 .st strong{font-size:52px}
.v3 .big3 .st strong small{font-size:30px;letter-spacing:-.02em;color:var(--muted);font-weight:600}
.v3 .big3 .st span{font-size:20px}
.v3 .est{font-size:14px}
'''
if '/* polish3 */' in s: a0 = s.index('/* polish3 */'); s = s[:a0] + s[s.index('</style>', a0):]
s = s.replace('</style>', css + '</style>', 1)
# ---- slide 1: plain map (markers come on slide 3)
old1 = s[s.index('<div class="shot fill"><img src="assets/shots/comp-flood-hook.png"'):]; old1 = old1[:old1.index('</div>') + 6]
s = s.replace(old1, '<div class="shot fill"><img src="assets/shots/comp-flood-hook.png" alt="Radar flood map of the 8 towns, 31 Oct 2024" style="object-position:center"><span class="tag">Radar flood map · 31 Oct · 8 towns</span></div>')
# ---- slide 3
s3 = f'''<!-- 3 · Rewind -->
<section class="s">
{hd('Story 1 · rewind, with Orbit to Ground', 3)} <h2 class="title" style="font-size:50px">Rewind. Same night, same data, with Orbit to Ground.</h2>
 <div class="r4">
  <div class="sq">
   <figure><figcaption>① Same map · what changed</figcaption><img src="assets/shots/sq-flood-change.png" alt="The slide-1 map classified: +47.0 km² more flood water in five days; Sueca, Sollana and València most newly wet"></figure>
   <figure><figcaption>② Same map · actions <i>(simulated)</i></figcaption><img src="assets/shots/sq-flood-act.png" alt="Evacuate and flag: evacuation alert to 8 municipalities, rescue teams to Sueca and València, next radar pass (simulated)"></figure>
  </div>
  <div class="vbig">
   <div class="frame"><img src="assets/shots/demo-poster.jpg" alt="Official demo video poster"><video id="demoVid" class="demo" controls muted playsinline preload="auto" poster="assets/shots/demo-poster.jpg"><source src="demo.mp4" type="video/mp4"></video><button class="unmute" id="demoUnmute" type="button">🔇 Unmute</button></div>
   <div class="cap"><span><span class="k">The official 30-second demo</span>Elena <b>could have</b> had a drafted alert for her town hours before the ~8 PM phone alert.</span><a href="{L}/sar-change/app/#demo" style="color:var(--accent);font-size:18px;white-space:nowrap">Open the flood app →</a></div>
  </div>
 </div>
 <div class="ft"><span class="pill">Hypothetical rewind · tasking and alerts are simulated</span><span class="src">NASA GPM IMERG V07 · NASA POWER · NASA/JPL OPERA DSWx-S1 · Sentinel-1 · town outlines © OpenStreetMap</span></div>
</section>

'''
s = section(s, 3, s3)
# ---- slide 5
s5 = f'''<!-- 5 · Fire vertical -->
<section class="s">
{hd('Story 2 · Hot Spots · wildfire', 5)} <h2 class="title" style="font-size:50px;margin-top:14px">Fire: staff crews from the record, not a fixed date.</h2>
 <div class="v3">
  <div class="vis">
   <div class="shot">{lp('deck-fire-ready', 'Hot Spots, Alberta: the 2026 outlook flags May, crews are tasked (simulated), and What if? shows +16 days and ~65,000 ha')}<span class="tk">Tasking (simulated)</span></div>
   <div class="how">In the app: Alberta's calendar flags May → Assign crews → What if? +16 days</div>
  </div>
  <div class="side">
   <div class="big3">
    <div class="st"><strong>~1,500 more fires</strong><span>detected by satellite in Alberta every year, compared with the year before (2003–2025 trend)</span></div>
    <div class="st"><strong>+16 days</strong><span>of full readiness: crews staffed 15 April instead of 1 May, because the record flags May</span></div>
    <div class="st"><strong>~65,000 ha <small>+ ~$25 M</small></strong><span>of forest and firefighting cost spared for every escaped fire those crews stop</span></div>
   </div>
   <div class="whatif"><b>What if · illustrative estimate</b>Each escaped May fire stopped spares an area about the size of the City of Toronto.</div>
   <div class="est"><b>How we estimated</b>~1,500 = Sen's slope of Alberta's yearly satellite fire detections, 2003–2025 (p = 0.035, tentative). +16 days = 15 Apr vs 1 May (Alberta's 2024 staffing date; Horse River began 1 May 2016). Per escape: 1,088 fires × 3% ≈ 33 escapes carry 97% of 2.2 M ha ≈ 65,000 ha each; Alberta spent $851 M on 2023 presuppression + response ÷ 2.2 M ha ≈ $387/ha × 65,000 ha ≈ $25 M. Toronto: 631 km². How many escapes earlier crews stop is the assumption; Horse River's initial attack was immediate.</div>
  </div>
 </div>
 <div class="ft"><span class="pill">Illustrative estimate · staffing tasks simulated</span><span class="src">NASA FIRMS (MODIS + VIIRS) · Alberta Forestry and Parks 2023–24 · MNP 2017/2025 · Stocks et al. 2002 · Statistics Canada</span></div>
</section>

'''
s = section(s, 5, s5)
# ---- slide 6
s6 = f'''<!-- 6 · Fields vertical -->
<section class="s">
{hd('Story 3 · Field Shift · farms', 6)} <h2 class="title" style="font-size:50px;margin-top:14px">Fields: next season's crop map, before planting.</h2>
 <div class="v3">
  <div class="vis">
   <div class="shot">{lp('deck-field-rye', 'Field Shift, Story County: slope map, the 92 steepest squares, Act: seed winter rye, task queued (simulated), What if? ~$1.2 M')}<span class="tk">Tasking (simulated)</span></div>
   <div class="how">In the app: slope map → 92 steepest squares → Act: seed winter rye → task → What if? ~$1.2 M</div>
  </div>
  <div class="side">
   <div class="big3">
    <div class="st"><strong>~$1.2 M</strong><span>net in a 2012-type drought from winter rye on the 92 steepest squares</span></div>
    <div class="st"><strong>26,500 acres <small>≈ 10,700 ha</small></strong><span>of the most erosion-prone farmland protected, picked square by square</span></div>
    <div class="st"><strong>Before planting</strong><span>our map is ready in February; USDA's crop map arrives ~11 months later</span></div>
   </div>
   <div class="whatif"><b>What if · illustrative estimate</b>Rye on the steepest fields costs a little most years and pays back in a dry one.</div>
   <div class="est"><b>How we estimated</b>(+11.1 bu × $6.89 − $32.09) ≈ $44 an acre × 26,500 acres ≈ $1.2 M in a drought year (SARE 2012 farmer survey × Iowa State costs); about 2.4× its seed and planting cost. Iowa corn fell 20% in 2012. Area: 92 squares of farmed 30 m pixels ≈ 107 km². Next-crop map ~82% right vs ~81% from crop history alone: a small edge. Frost-free season +19 days since 1981.</div>
  </div>
 </div>
 <div class="ft"><span class="pill">Illustrative estimate · seeding and scouting tasks simulated</span><span class="src">USDA NASS CDL + Crop Production 2012 · SARE/CTIC · Iowa State · NASA HLS · NASA POWER · NASA SRTM</span></div>
</section>

'''
s = section(s, 6, s6)
# ---- demo autoplay on slide 3 (muted, from 0; pause on leave) + unmute
js = '''<script id="demoAuto">
(function(){
  var v=document.getElementById('demoVid'), b=document.getElementById('demoUnmute'); if(!v) return;
  var sec=v.closest('section'), wantSound=false;
  function label(){ b.textContent = v.muted ? '🔇 Unmute' : '🔊 Mute'; }
  b.onclick=function(e){ e.stopPropagation(); wantSound=v.muted; v.muted=!v.muted; if(v.paused){ var p=v.play(); if(p&&p.catch)p.catch(function(){}); } label(); };
  v.addEventListener('volumechange',label);
  function enter(){ v.muted=!wantSound; try{ v.currentTime=0; }catch(e){} var p=v.play(); if(p&&p.catch) p.catch(function(){ v.muted=true; label(); v.play().catch(function(){}); }); label(); }
  new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting&&e.intersectionRatio>=.5) enter(); else if(e.intersectionRatio<.5) v.pause(); }); },{threshold:[0,.5]}).observe(sec);
})();
</script>
'''
if '<script id="demoAuto">' in s: a0 = s.index('<script id="demoAuto">'); s = s[:a0] + s[s.index('</script>', a0) + 10:]
s = s.replace('</body>', js + '</body>')
assert s.count('<section') == 7 and 'loop-flood-task' not in s
open(p, 'w').write(s); print('ok')
