"""Shareable deck with video inside: submission/deck.pptx = the 7 rendered slide PNGs as full-bleed backgrounds, with demo.mp4 and the
walkthrough loops embedded as real movie shapes at their on-slide positions (aspect kept, fitted inside each frame).
Positions come from tools/deck_video_rects.mjs (run it first: node tools/deck_video_rects.mjs > submission/build/video_rects.json)."""
import json, os, subprocess
from pptx import Presentation
from pptx.util import Emu
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); S = R + '/submission/'
rects = json.load(open(S + 'build/video_rects.json'))
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
        sl.shapes.add_movie(mp4, Emu(int(x * k)), Emu(int(y * k)), Emu(int(w * k)), Emu(int(h * k)), poster_frame_image=S + r['poster'], mime_type='video/mp4')
    notes = {3: 'Click a video to play. The official demo is the 30-second video on the right; also at https://nasa-spaceapps-2026.pages.dev/submission/demo.mp4'}
    if i in notes: sl.notes_slide.notes_text_frame.text = notes[i]
prs.save(S + 'deck.pptx'); print('deck.pptx', round(os.path.getsize(S + 'deck.pptx') / 1e6, 1), 'MB')
