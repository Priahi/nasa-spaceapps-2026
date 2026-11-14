# Parallel work: shared API (owner: Hot Spots / integration worker)

Published 12:40 ET. Build: `python3 src/build.py` → `dist/`. Local preview: `python3 -m http.server 8899 -d dist`.
**Only the integration worker deploys or pushes.** Don't edit files outside your folders (list at the end).

## 1. Shared tokens — `src/shared/tokens.css` → served at `/shared/tokens.css`
Auto-injected into every dashboard `<head>` (after the app's own CSS). Defines `--og-*` tokens and aliases the
names the apps already use (`--bg --bg-2 --card --panel --ink --text --muted --line --border --accent --accent-2 --danger --font --mono`),
so `var(--bg)` etc. now resolve to the site palette. Dark theme everywhere (site = navy `#07091a`, periwinkle `#9ec1ff` / lilac `#d4c4ff`, Geist).
- Surfaces: `--og-bg #07091a`, `--og-bg-2 #10142c`, `--og-card #121733`, `--og-card-2 #182046`
- Text: `--og-ink #f4f6fb`, `--og-muted #b7c0d6`, `--og-faint #8b95ad`, `--og-on-accent #071018`
- Lines: `--og-line`, `--og-line-strong`; brand `--og-accent`, `--og-accent-2`, `--og-grad`
- Status (UI only): `--og-ok --og-warn --og-bad --og-info`
- Data ramps: fire `--og-fire-0..5` (dark brown → amber → pale yellow); water `--og-water-perm` (deep blue, permanent), `--og-water-new` (cyan, new flood water), `--og-water-gone` (amber, water lost), `--og-dry`;
  crops `--og-crop-corn --og-crop-soy --og-crop-wheat --og-crop-cover --og-crop-fallow`
- Type/shape: `--og-font`, `--og-mono`, `--og-r 14px`, `--og-r-sm 9px`, `--og-shadow`
Rules: no hard-coded greens/ambers for UI chrome; no black+green; purple is NOT for fire data. Remove app-specific `:root` palettes or point them at `--og-*`.
The old right-side guide panel (`guide.js`) is **no longer injected**; decision support must live inside the dashboard layout.

## 2. Data for each dashboard — `og-data.js` (auto-generated, loaded before your app JS)
`window.OG_SLUG` and `window.OG_APP = { slug, name, role, who, page, actions:[...], impact:[...], metrics:[{v,t,neg}] }`
- `actions[i] = { id:"<slug>-N", cls, title (the "I will"), sat, out, src, verb:"Dispatch", tasks:[{asset, label, eta}] }`
- `impact[i] = { user, decision, before:[..], after:[..], geo:{v,l}, metric:{v,l} }` (before → after, qualitative; numbers are real inputs)
Source: `src/recs.py` (`APPS`, `C2`, `BA`). **To change your module's copy without touching recs.py**, create
`src/modules/<slug>/app.json`; any top-level key there (e.g. `"actions"`, `"impact"`) replaces the default in `OG_APP`.
Real numbers only; outcomes stay qualitative.

## 3. C2 component — `src/shared/c2.js` + `c2.css` → `window.OGC2` (auto-injected into every dashboard)
```js
const c2 = OGC2.mount(elOrSelector, {
  app: OG_SLUG, title: "Recommended actions", kicker: "Decision support", user: "Civil-protection duty officer",
  actions: OG_APP.actions,                       // or your own array, same shape
  onSelect(action /* or null */) { /* recolor/highlight map layers, show the asset */ },
  onApprove(action, approved /* bool, false = undo */) { /* e.g. mark zones as 'tasked' */ },
  onTask(action, task, status /* "Tasked"|"In progress"|"Done" */) { /* optional: move an asset icon */ },
  onReset() { /* clear highlights */ }
});
c2.select(id); c2.approve(id); c2.reset();      // programmatic control
OGC2.impact(elOrSelector, OG_APP.impact, { title: "Impact", note: "Qualitative: we haven't measured lives, yields or costs." });
OGC2.icon("drone")  // inline SVG; assets: drone camera satellite crew notice engineer sensor plan seed truck
window.addEventListener("og:c2", e => e.detail /* {type:select|approve|withdraw|task|reset, app, action, task, status} */);
```
Renders: action cards (class tag, title, Satellite shows / I will / Expected, asset chips, primary verb button = approve/undo,
"Show on map" toggle) + a task queue (Queued → Tasked → In progress → Done, simulated timers) + a timeline, with one
**"Simulated tasking"** badge and a one-line disclaimer. Responsive: 2 columns ≥ 900 px, stacked below; full-width buttons < 520 px.
Place the mount element **in the main layout** (e.g. under/next to the map), not a fixed side panel. Layer changes are your job via the callbacks.

## 4. Project pages (`/<slug>/`) — per-module hooks, no need to edit build.py
Create any of these in `src/modules/<slug>/`:
- `page.py` with `def override(slug, secs, A) -> secs`: `secs` is a dict of section HTML keyed
  `hero problem satellite actions impact try trend how pager` (each a full `<section ...>...</section>` string). Replace, add new keys,
  and optionally set `secs["_order"] = [...]` to reorder. `A` = `recs.APPS[slug]`. You may `from recs import BA, C2, APPS`
  and `from story import line_chart, bar_chart, slider, img, T, ED, MCD, OPERA`.
- `page.css` → linked in that page's `<head>` as `/<slug>/m/page.css`; `page.js` → deferred script `/<slug>/m/page.js`.
- Any other files (images etc.) under `src/modules/<slug>/` are copied to `/<slug>/m/...`.
Site tokens on project pages: `src/assets/css/site.css` vars (`--bg --ink --accent ...`) — same values as tokens.css.

## 5. Ownership
- SAR worker: `demos/sar-change/**`, `src/demo-theme/sar.css`, `src/modules/sar-change/**`.
- Field Shift worker: `demos/field-shift/**`, `src/demo-theme/field.css`, `src/modules/field-shift/**`.
- Integration worker (me): everything else — `src/shared/**`, `src/build.py`, `src/recs.py`, `src/story.py`, `src/content.py`, site CSS/JS, `demos/hotspots/**`, home page, deploy, push.
Need a change in a shared file? Write it in your report (or a note at the bottom of this file under "Requests") and I'll apply it.
Photo tags: I'm removing visible "Illustrative" labels site-wide (build.py/recs.py). Don't add new ones.

## 6. Checks before reporting
Desktop 1440, tablet 768, mobile 390: no horizontal overflow, 0 console errors, dashboard still works. Real numbers only; no names of
the owner's other sites/companies/products/clients; no secrets.

## Requests
(append here)

### Update 12:58 ET
- `onSelect(action, { source })`: `source` is `"show"` (user pressed "Show on map"), `"approve"` (auto-select on approve) or `"api"`. Scroll your map into view only for `"show"`.
- `OGC2.impact` now wraps cards in `.c2-imp-grid` (auto-fit, min 340 px).
- Deep link: site pages link each action to `/<slug>/app/#act=<action id>` (e.g. `#act=sar-change-1`). Please call `c2.select(id)` on load when the hash matches (Hot Spots does: `/act=([\w-]+)/.exec(location.hash)`).
- Note: the shared box was restored from a snapshot around 12:37 ET; if your files look older than expected, check them.
