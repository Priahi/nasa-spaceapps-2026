"""Shareable deck with video inside: submission/deck.pptx = the 7 rendered slide PNGs as full-bleed backgrounds, with demo.mp4 and the
walkthrough loops embedded as real movie shapes at their on-slide positions (aspect kept, fitted inside each frame).
Positions come from tools/deck_video_rects.mjs (run it first: node tools/deck_video_rects.mjs > submission/build/video_rects.json)."""
import json, os, subprocess
from lxml import etree
from pptx import Presentation
from pptx.util import Emu
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); S = R + '/submission/'
rects = json.load(open(S + 'build/video_rects.json'))
NS = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
def autoplay(slide, spid, dur_ms, loop, mute):
    # PowerPoint "Start: Automatically" (+ loop/mute for walkthroughs): replace python-pptx's click-to-play timing
    rep = ' repeatCount="indefinite"' if loop else ''; mu = ' mute="1"' if mute else ''
    xml = (f'<p:timing {NS}><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
      '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
      '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
      '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
      '<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
      f'<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="{dur_ms}" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>'
      '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
      '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
      '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
      f'<p:video><p:cMediaNode vol="80000"{mu}><p:cTn id="7"{rep} fill="hold" display="0"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
      f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>'
      '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
    el = slide._element; old = el.find('{http://schemas.openxmlformats.org/presentationml/2006/main}timing')
    new = etree.fromstring(xml)
    if old is not None: el.replace(old, new)
    else: el.append(new)
def secs(path): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout)
prs = Presentation(); prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
k = 12192000 / 1920
def dims(path):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip().split(',')
    return int(o[0]), int(o[1])
for i in range(1, 8):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    sl.shapes.add_picture(f'{S}build/slide-{i}.png', 0, 0, prs.slide_width, prs.slide_height)
    for r in [r for r in rects if r['slide'] == i]:
        mp4 = S + r['src']; vw, vh = dims(mp4)
        sc = min(r['w'] / vw, r['h'] / vh); w, h = vw * sc, vh * sc; x = r['x'] + (r['w'] - w) / 2; y = r['y'] + (r['h'] - h) / 2
        mv = sl.shapes.add_movie(mp4, Emu(int(x * k)), Emu(int(y * k)), Emu(int(w * k)), Emu(int(h * k)), poster_frame_image=S + r['poster'], mime_type='video/mp4')
        autoplay(sl, mv.shape_id, int(secs(mp4) * 1000), loop=True, mute=True)
    notes = {3: 'The official demo starts by itself when this slide opens (PowerPoint/Keynote); click it to pause. Also at https://spaceapps.parsariahi.com/submission/demo.mp4'}
    if i in notes: sl.notes_slide.notes_text_frame.text = notes[i]
prs.save(S + 'deck.pptx'); print('deck.pptx', round(os.path.getsize(S + 'deck.pptx') / 1e6, 1), 'MB')
