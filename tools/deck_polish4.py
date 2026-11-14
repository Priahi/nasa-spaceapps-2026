"""Fourth polish pass (run after deck_polish3.py; re-runnable). Slides 5-6 get a fixed, large map still from the live app
(fire: the Canada burn-history layer; fields: the 2025 crop classification map) that stays put while a smaller loop plays beside it.
Fire loop = deck-fire-map (mostly the burn-history layer). Cards one line each; 'How we estimated' is a 2-3 line muted box with its own
grid cell (full formulas live in SPEAKER_NOTES); footer keeps clear of the browser nav buttons."""
import os
from PIL import Image
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); S = R + '/submission/'; D = S + 'assets/shots/'
Image.open(D + 'map8-fire-raw.png').convert('RGB').crop((0, 280, 1950, 1556)).save(D + 'map8-fire.jpg', quality=90)
Image.open(D + 'map8-field-raw.png').convert('RGB').crop((330, 400, 1710, 1246)).save(D + 'map8-field.jpg', quality=90)
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
/* polish4 */
.ft{padding-right:200px;gap:28px}
.ft .pill{white-space:nowrap;flex:none}
.ft .src{text-align:right}
.v4{display:grid;grid-template-columns:minmax(0,1fr) 700px;grid-template-rows:auto 1fr;column-gap:28px;row-gap:14px;margin-top:16px;flex:1;min-height:0}
.v4 .map{grid-row:1;grid-column:1;position:relative;margin:0;height:650px;border-radius:18px;overflow:hidden;background:#0b0e20;box-shadow:0 14px 40px rgba(11,18,48,.22)}
.v4 .map img{width:100%;height:100%;object-fit:cover;object-position:center bottom;display:block}
.v4 .map figcaption{position:absolute;left:14px;top:14px;font:600 15px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:#fff;background:rgba(11,14,32,.82);padding:8px 12px;border-radius:10px}
.v4 .map .lg{position:absolute;left:14px;bottom:14px;display:flex;gap:14px;font:600 15px var(--font);color:#fff;background:rgba(11,14,32,.82);padding:8px 12px;border-radius:10px}
.v4 .map .lg i{display:inline-block;width:13px;height:13px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.v4 .right{grid-row:1 / span 2;grid-column:2;display:flex;flex-direction:column;gap:12px;min-height:0}
.v4 .loop{position:relative;width:700px;height:438px;border-radius:16px;overflow:hidden;background:#0b0e20;flex:none}
.v4 .loop img,.v4 .loop video{position:absolute;inset:0;width:100%;height:100%;display:block}
.v4 .loop video{z-index:1}
.v4 .loop .tk{position:absolute;right:10px;bottom:10px;z-index:2}
.v4 .how{font:600 14px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--water);margin-top:-4px}
.v4 .cards{display:flex;flex-direction:column;gap:10px}
.v4 .cards .st{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:10px 20px}
.v4 .cards .st strong{display:block;font-size:42px;line-height:1.05;letter-spacing:-.03em}
.v4 .cards .st strong small{font-size:26px;color:var(--muted);font-weight:600;letter-spacing:-.01em}
.v4 .cards .st span{display:block;font-size:19px;color:var(--muted);line-height:1.25;margin-top:2px}
.v4 .low{grid-row:2;grid-column:1;display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:16px;align-items:start;min-height:0}
.v4 .whatif{font-size:22px}
.v4 .est2{font-size:14px;line-height:1.4;color:#6b7280;border:1px dashed #c5cbd8;border-radius:12px;padding:9px 14px;background:rgba(255,255,255,.6)}
.v4 .est2 b{display:block;font:600 12px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:#8a93a6;margin-bottom:2px}
@media print{.v4 .loop video{display:none}}
'''
if '/* polish4 */' in s: a = s.index('\n/* polish4 */'); s = s[:a] + s[s.index('</style>', a):]
s = s.replace('</style>', css + '</style>', 1)
def slide(n, head, title, mapimg, mapalt, mapcap, legend, loop, loopalt, how, cards, whatif, est, pill, src):
    cs = ''.join(f'<div class="st"><strong>{a}</strong><span>{b}</span></div>' for a, b in cards)
    return f'''<!-- {n} · {'Fire' if n == 5 else 'Fields'} vertical -->
<section class="s">
{hd(head, n)} <h2 class="title" style="font-size:50px;margin-top:14px">{title}</h2>
 <div class="v4">
  <figure class="map"><img src="{mapimg}" alt="{mapalt}"><figcaption>{mapcap}</figcaption>{legend}</figure>
  <div class="right">
   <div class="loop shot">{lp(loop, loopalt)}<span class="tk">Tasking (simulated)</span></div>
   <div class="how">{how}</div>
   <div class="cards">{cs}</div>
  </div>
  <div class="low"><div class="whatif"><b>What if · illustrative estimate</b>{whatif}</div><div class="est2"><b>How we estimated</b>{est}</div></div>
 </div>
 <div class="ft"><span class="pill">{pill}</span><span class="src">{src}</span></div>
</section>
'''
s5 = slide(5, 'Story 2 · Hot Spots · wildfire', 'Fire: staff crews from the record, not a fixed date.',
  'assets/shots/map8-fire.jpg', 'Canada burn history: satellite fire detections per year, 2003-2025 average, on the live Hot Spots map',
  'Canada burn history · fires per year, 2003–2025', '',
  'deck-fire-map', 'Hot Spots live: the burn-history layer across Canada, the boreal belt and B.C., the burn calendar, then Assign crews (simulated)',
  'In the app: burn history → calendar flags May → Assign crews',
  [('~1,500 more fires', 'detected in Alberta each year than the year before (2003–2025 trend)'),
   ('+16 days', 'of full readiness: crews staffed 15 April instead of 1 May'),
   ('~65,000 ha <small>+ ~$25 M</small>', 'of forest and firefighting cost spared per escaped fire stopped')],
  'Each escaped May fire stopped spares an area about the size of the City of Toronto.',
  'Trend in NASA FIRMS detections; 15 Apr vs 1 May staffing; Alberta 2023 area and cost ÷ ~33 escapes. Full formulas in speaker notes.',
  'Illustrative estimate · staffing tasks simulated', 'NASA FIRMS (MODIS + VIIRS) · Alberta Forestry and Parks 2023–24 · Stocks et al. 2002 · StatCan · tiles © Esri')
lg6 = '<div class="lg">' + ''.join(f'<span><i style="background:{c}"></i>{t}</span>' for c, t in [('#f5c02c', 'Corn'), ('#2a8a4a', 'Soybean'), ('#a5d94a', 'Grass'), ('#a85a32', 'Hay'), ('#7a2bd6', 'Small grain')]) + '</div>'
s6 = slide(6, 'Story 3 · Field Shift · farms', "Fields: next season's crop map, before planting.",
  'assets/shots/map8-field.jpg', 'Story County, Iowa: crop classification map at 30 m (corn, soybean, grass, hay) on the live Field Shift map',
  'Story County, Iowa · crop map, 30 m', lg6,
  'deck-field-rye', 'Field Shift, Story County: slope map, the 92 steepest squares, Act: seed winter rye, task queued (simulated), What if? ~$1.2 M',
  'In the app: slope map → Act: winter rye → task → What if?',
  [('~$1.2 M', 'net in a 2012-type drought from winter rye on the steepest squares'),
   ('26,500 acres <small>≈ 10,700 ha</small>', 'of the most erosion-prone farmland protected'),
   ('Before planting', "our map is ready in February; USDA's arrives ~11 months later")],
  'Rye on the steepest fields costs a little most years and pays back in a dry one.',
  '~$44 an acre net in a drought (SARE 2012 yield gain × Iowa State costs) × 26,500 acres. Next-crop map ~82% vs ~81% from history alone. Full formulas in speaker notes.',
  'Illustrative · seeding tasks simulated', 'USDA NASS CDL · SARE/CTIC · Iowa State · NASA HLS · NASA POWER · NASA SRTM · tiles © Esri')
s = section(s, 5, s5); s = section(s, 6, s6)
open(p, 'w').write(s); print('ok')
