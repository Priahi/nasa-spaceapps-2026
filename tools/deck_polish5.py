"""Fifth polish pass (run after deck_polish4.py; re-runnable). Big type carries the human number, not dates.
Slide 1: headline 'About 230 people died because of one day of rain.', three big numbers (150+ before the ~8 PM alert,
~1.6 years of rain in one day, the 12-hour gap), date and place in a small kicker; map kept.
Slide 2 builds on it instead of repeating: the moments become plain-English lines (time small), and the closing box says
the rain was on NASA's record while the town-level alert was not."""
import os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); S = R + '/submission/'
p = S + 'deck.html'; s = open(p).read()
def section(s, num, html):
    a = s.index(f'<!-- {num} ·'); b = s.index('<!-- ', a + 5)
    return s[:a] + html + s[b:]
css = '''
/* polish5 */
.h1x{font-size:84px;line-height:1.0;letter-spacing:-.045em;font-weight:600;margin:0}
.k1{font:600 20px var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--water);margin:0}
.n3{display:flex;flex-direction:column;gap:14px}
.n3 div{display:flex;align-items:baseline;gap:20px;background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:14px 24px}
.n3 strong{flex:none;min-width:215px;font-size:64px;line-height:1;letter-spacing:-.045em;color:#b42318}
.n3 span{font-size:24px;line-height:1.28;color:var(--muted)}
.n3 span b{color:var(--ink);font-weight:600}
.facts.h b{display:block;font:600 28px var(--font);letter-spacing:-.02em;line-height:1.1;color:var(--ink)}
.facts.h .late b{color:#b42318}
.facts.h span{font-size:17px}
.facts.h time{display:inline;font:600 17px var(--mono);letter-spacing:0;color:var(--water)}
'''
if '/* polish5 */' in s: a = s.index('\n/* polish5 */'); s = s[:a] + s[s.index('</style>', a):]
s = s.replace('</style>', css + '</style>', 1)
s1 = '''<!-- 1 · Hook -->
<section class="s">
 <div class="hd"><span>NASA Space Apps 2026 · <b>Be An Earth System Trend Detective!</b> · Orbit to Ground</span><span>1 / 7</span></div>
 <div class="split">
  <div class="stack" style="gap:24px">
   <p class="k1">Valencia, Spain · 29 Oct 2024</p>
   <h1 class="h1x">About 230 people died because of one day of rain.</h1>
   <div class="n3">
    <div><strong>150+</strong><span>were already dead when the phone alert went out, around <b>8 PM</b></span></div>
    <div><strong>~1.6 yrs</strong><span>of València's rain fell on one town <b>in a single day</b> (~770 mm, about 2½ feet)</span></div>
    <div><strong>12 hours</strong><span>from the red weather warning, around 7:30 AM, <b>to that phone alert</b></span></div>
   </div>
  </div>
  <div class="shot fill"><img src="assets/shots/comp-flood-hook.png" alt="Radar flood map of the 8 towns, 31 Oct 2024" style="object-position:center"><span class="tag">Radar flood map · 31 Oct · 8 towns</span></div>
 </div>
 <div class="ft"><span class="src">AEMET event study (Turís) · AEMET normals, València 1981–2010: 475 mm a year · Newtral · El País, 26 Oct 2025 · map: NASA/JPL OPERA DSWx-S1</span><span>Built by Parsa Riahi and Yara Riahi · Toronto</span></div>
</section>

'''
s = section(s, 1, s1)
# slide 2: build, don't repeat
a = s.index('<!-- 2 ·'); b = s.index('<!-- ', a + 5); s2 = s[a:b]
fa = s2.index(' <div class="facts'); fb = s2.index(' <div class="ft">')
s2 = s2[:fa] + ''' <div class="facts h" style="margin-top:auto">
  <div><b>The danger was known</b><span>red warning for the province · <time>~7:30 AM</time></span></div>
  <div><b>The first life lost</b><span>a driver at the Benimodo ravine · <time>~noon</time></span></div>
  <div><b>The ravine became a river</b><span>the Poyo surges into the towns · <time>~7 PM</time></span></div>
  <div class="late"><b>"Avoid any travel"</b><span>the only phone alert, too late · <time>~8 PM</time></span></div>
 </div>
 <div class="gap" style="margin-top:16px;padding:16px 26px"><strong style="font-size:40px;white-space:nowrap">The rain was on the record.</strong><span style="font-size:24px">NASA's satellites logged ~90 mm upstream that day. What no one had was a map that turned it into an alert for Elena's town.</span></div>
''' + s2[fb:]
s2 = s2.replace('Story 1 · Valencia, 29 October 2024', 'Story 1 · Valencia · what it felt like on the ground')
s = s[:a] + s2 + s[b:]
open(p, 'w').write(s); print('ok')
# speaker notes
n = S + 'SPEAKER_NOTES.md'; t = open(n).read()
a = t.index('## 1 · Hook'); b = t.index('- Exact: 771.8 mm')
t = t[:a] + '''## 1 · Hook: about 230 people died because of one day of rain
"About 230 people died because of one day of rain. In Valencia, on 29 October 2024, more than 150 of them were already dead when the phone alert went out, around 8 PM. One town got about 770 mm in a day, roughly two and a half feet, about 1.6 years of València's rain. And twelve hours passed between the red warning and that alert."
- Slide (rounded): headline "About 230 people died…"; 150+ before the ~8 PM alert; ~1.6 yrs of rain in a single day; 12 hours. Date and place are only the small kicker.
- Exact: 229 deaths in the Valencia region (El País, 26 Oct 2025, which also gives at least 156 of the 229 dead before the 8:11 PM ES-Alert); red warning 7:36 AM (Newtral) → 12 h 35 min gap; 771.8 mm at Turís in 24 h (AEMET).
- Note "in a single day", not "one afternoon": 771.8 mm is the 24 h total (1.62 years). The afternoon alone (3–8 PM) was 616.8 mm = 1.30 years.
''' + t[b:]
a = t.index('## 2 · Imagine'); b = t.index('- The rain panel is')
t = t[:a] + '''## 2 · Imagine
"Imagine losing someone you love because no one knew how much rain was coming that day."
- Builds on slide 1 (which gave the toll, the rain and the 12-hour gap): here the same day as four moments, in words, with the times small: the danger was known (~7:30 AM red warning), the first life lost (~noon, Benimodo ravine), the ravine became a river (~7 PM Poyo surge), "avoid any travel" (~8 PM, the only phone alert). Closing box: the rain was on NASA's record (~90 mm upstream, IMERG); what was missing was a map that turned it into an alert for Elena's town.
''' + t[b:]
t = t.replace('- Slide (rounded): ~7:30 AM warning, ~noon first death, ~7 PM Poyo ravine surge, ~8 PM phone alert, "a 12-hour gap", about 230 died.\n', '')
open(n, 'w').write(t); print('notes ok')
