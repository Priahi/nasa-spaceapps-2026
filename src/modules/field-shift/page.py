"""Field Shift project page: concrete before -> after impact for two named users, with their photos.
Copy lives in app.json (also used by the dashboard via OG_APP.impact). Every number is from the repo's results files:
POWER frost-free trend (trends/out), HLS change (earthdata/field-shift/hls_story_county.json),
model metrics (demos/field-shift/data/colab_run/results.json), flag counts (demos/field-shift/data/app_data.json)."""
import json
from html import escape as e
from pathlib import Path

HERE = Path(__file__).parent

def _impact_html():
    items = json.loads((HERE / "app.json").read_text())["impact"]
    li = lambda xs: "".join(f"<li>{e(x)}</li>" for x in xs)
    return "".join(
        f'<article class="c2-imp fs-imp"><img class="fs-imp-img" src="/assets/img/people/{e(it["img"])}.webp" alt="{e(it["alt"])}" loading="lazy" width="1280" height="720" />'
        f'<header><span class="c2-cls">{e(it["user"])}</span><h3>{e(it["decision"])}</h3></header>'
        f'<div class="c2-ba"><div class="c2-b"><p>Before</p><ul>{li(it["before"])}</ul></div><span class="c2-arrow" aria-hidden="true">→</span>'
        f'<div class="c2-a"><p>With Field Shift</p><ul>{li(it["after"])}</ul></div></div>'
        f'<footer><div><b>{e(it["geo"]["v"])}</b><span>{e(it["geo"]["l"])}</span></div><div><b>{e(it["metric"]["v"])}</b><span>{e(it["metric"]["l"])}</span></div></footer></article>'
        for it in items)

def override(slug, secs, A):
    imp = secs.get("impact", "")
    start = imp.find('<div class="c2-impact"')
    if start < 0:
        return secs
    stop = imp.find('<p class="mstrip-k"', start)  # keep the metrics strip that follows
    secs["impact"] = imp[:start] + f'<div class="c2-impact fs-impact" data-fx="rise">{_impact_html()}</div>\n' + (imp[stop:] if stop > 0 else "</div></section>\n")
    return secs
