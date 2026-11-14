// Story cards for the 30 s video (light palette, no AI wording). Output: submission/build/video3/card-*.png
import { chromium } from '/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const out = '/workspace/spaceapps-site/submission/build/video3'; fs.mkdirSync(out, { recursive: true });
const font = 'file:///workspace/spaceapps-site/src/assets/fonts/Geist-Variable.woff2', mono = 'file:///workspace/spaceapps-site/src/assets/fonts/GeistMono-Variable.woff2';
const css = `@font-face{font-family:G;src:url(${font}) format("woff2");font-weight:100 900}@font-face{font-family:M;src:url(${mono}) format("woff2");font-weight:100 900}*{margin:0;box-sizing:border-box}
body{width:1920px;height:1080px;font-family:G;color:#0b1230;display:flex;flex-direction:column;justify-content:center;padding:0 160px;
background:radial-gradient(1200px 600px at 0% -20%,rgba(158,193,255,.55),transparent 60%),radial-gradient(1000px 560px at 105% -10%,rgba(212,196,255,.55),transparent 58%),#f4f6fc}
.k{font:600 26px M;letter-spacing:.14em;text-transform:uppercase;color:#0369a1}h1{font-size:150px;letter-spacing:-.055em;font-weight:600;line-height:.95;margin-top:20px}
p{font-size:50px;color:#47506b;margin-top:30px;line-height:1.3}p b{color:#0b1230}.ill{font:500 22px M;letter-spacing:.08em;text-transform:uppercase;color:#6b7590;margin-top:22px}
.g{background:linear-gradient(120deg,#3f63d6,#7b5bd6);-webkit-background-clip:text;color:transparent}
.av{width:120px;height:120px;border-radius:50%;background:linear-gradient(135deg,#bcd3ff,#d4c4ff);display:grid;place-items:center;font-size:54px;font-weight:600}
.row{display:flex;gap:22px;margin-top:44px;flex-wrap:wrap}.row div{border-radius:18px;padding:20px 26px;font-size:32px;background:#fff;border:1px solid rgba(11,18,48,.12)}.row .f{background:transparent;border:2px dashed #aab1c4;color:#47506b}
.lab{font:700 20px M;letter-spacing:.14em;text-transform:uppercase}`;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const card = async (name, h) => { fs.writeFileSync(`${out}/card.html`, `<style>${css}</style>${h}`); await p.goto(`file://${out}/card.html`); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300); await p.screenshot({ path: `${out}/card-${name}.png` }); };
await card('night', `<span class="k">Valencia, Spain · 29 October 2024</span><h1 style="font-size:104px;line-height:1.04;letter-spacing:-.045em">Imagine losing someone you love because <span style="color:#b42318">no one knew how much rain was coming</span> that day.</h1><p style="font-size:40px">The phone alert went out at <b>20:11</b>. At least <b>156</b> people had already died.</p>`);
await card('impact', `<span class="k" style="color:#3f63d6">What if · illustrative estimate</span><h1 style="font-size:104px;line-height:1.02">12 hours earlier = an alert before the first death.</h1><p style="font-size:42px">Published warning curves put about <b>€1.1 bn</b> of Valencia's <b>€4.8 bn</b> insured loss within reach (22% × €4.8 bn).</p><span class="ill">Illustrative what-if, not a measured outcome · El País · CCS · Day (1970) curve</span>`);
await card('elena', `<div style="display:flex;gap:34px;align-items:center"><div class="av">E</div><div><h1 style="font-size:96px;margin:0">Elena</h1><p style="margin-top:8px;font-size:42px">Emergency coordinator, Catarroja</p></div></div>
<p style="font-size:64px;color:#0b1230;font-weight:600;letter-spacing:-.03em;margin-top:60px">Rewind. <span class="g">Same night, with Orbit to Ground.</span></p><span class="ill">Illustrative composite · hypothetical rewind</span>`);
await card('x20', `<span class="k" style="color:#3f63d6">One engine, many sectors</span><h1 style="font-size:110px">Signal → map → alert → task.</h1>
<div class="row"><div><span class="lab" style="color:#1e6b34">Built</span> Flood · Fire · Farms · Groundwater</div><div class="f"><span class="lab">Future</span> Drought · Air quality · Infrastructure · Landslides</div></div>
<p style="font-size:40px;margin-top:46px">nasa-spaceapps-2026.pages.dev</p>`);
await b.close(); console.log('cards ok');
