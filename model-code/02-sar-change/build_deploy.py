#!/usr/bin/env python3
"""Copy the static SAR demo plus the briefing deck into /workspace/nasa-spaceapps/deploy/sar-change/ (no screenshots, scripts or plugins)."""
import shutil
from pathlib import Path
SRC = Path(__file__).resolve().parent
OUT = Path("/workspace/nasa-spaceapps/deploy/sar-change")
SH = SRC.parent / "_shared"
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
for f in ("index.html", "app.js", "styles.css", "favicon.ico"): shutil.copy(SRC / f, OUT / f)
shutil.copytree(SRC / "data", OUT / "data"); shutil.copytree(SRC / "tiles", OUT / "tiles")
for f in ("briefing.js", "briefing.css"): shutil.copy(SH / f, OUT / f)
shutil.copy(SRC / "deploy_extra/briefing_content.js", OUT / "briefing_content.js")
shutil.copy(SRC / "deploy_extra/extras.json", OUT / "data/extras.json")
shutil.copytree(SRC / "deploy_extra/figs", OUT / "figs")
h = (OUT / "index.html").read_text()
h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n  <meta name="robots" content="noindex, nofollow">', 1)
h = h.replace("(local demo)</title>", "(NASA Space Apps demo)</title>")
h = h.replace('<link rel="stylesheet" href="styles.css">', '<link rel="stylesheet" href="styles.css">\n  <link rel="stylesheet" href="briefing.css">')
h = h.replace("NASA Space Apps 2026 · local demo · not submitted", "NASA Space Apps 2026 · unlisted demo · not submitted")
h = h.replace('<h1>Dancing with the SARs</h1>',
              '<h1 style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">Dancing with the SARs <button type="button" class="bf-inline" data-briefing-open="1">▶ Experiment briefing</button></h1>')
h = h.replace("Apache-2.0. Not deployed, not submitted, not a published benchmark.", "Apache-2.0. Unlisted demo, not submitted, not a published benchmark.")
h = h.replace('<script src="app.js"></script>', '<script src="app.js"></script>\n  <script src="briefing.js"></script>\n  <script src="briefing_content.js"></script>')
assert h.count("briefing") >= 4
(OUT / "index.html").write_text(h)
(OUT / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n")
(OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
print("built", OUT)
