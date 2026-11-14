// Story cards for the 30 s video v4 (light palette, plain wording, rounded story times and counts). Output: submission/build/video4/card-*.png
import { chromium } from '/node_modules/playwright-core/index.mjs';
import fs from 'fs';
const out = '/workspace/spaceapps-site/submission/build/video4'; fs.mkdirSync(out, { recursive: true });
const font = 'file:///workspace/spaceapps-site/src/assets/fonts/Geist-Variable.woff2', mono = 'file:///workspace/spaceapps-site/src/assets/fonts/GeistMono-Variable.woff2';
const css = `@font-face{font-family:G;src:url(${font}) format("woff2");font-weight:100 900}@font-face{font-family:M;src:url(${mono}) format("woff2");font-weight:100 900}*{margin:0;box-sizing:border-box}
body{width:1920px;height:1080px;font-family:G;color:#0b1230;display:flex;flex-direction:column;justify-content:center;padding:0 160px 40px;
background:radial-gradient(1200px 600px at 0% -20%,rgba(158,193,255,.55),transparent 60%),radial-gradient(1000px 560px at 105% -10%,rgba(212,196,255,.55),transparent 58%),#f4f6fc}
.k{font:600 26px M;letter-spacing:.14em;text-transform:uppercase;color:#0369a1}h1{font-size:150px;letter-spacing:-.055em;font-weight:600;line-height:.95;margin-top:20px}
p{font-size:50px;color:#47506b;margin-top:30px;line-height:1.3}p b{color:#0b1230}.ill{font:500 22px M;letter-spacing:.08em;text-transform:uppercase;color:#6b7590;margin-top:26px}
.g{background:linear-gradient(120deg,#3f63d6,#7b5bd6);-webkit-background-clip:text;color:transparent}
.row{display:flex;gap:22px;margin-top:44px;flex-wrap:wrap}.row div{border-radius:18px;padding:20px 26px;font-size:32px;background:#fff;border:1px solid rgba(11,18,48,.12)}.row .f{background:transparent;border:2px dashed #aab1c4;color:#47506b}
.lab{font:700 20px M;letter-spacing:.14em;text-transform:uppercase}`;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const card = async (name, h) => { fs.writeFileSync(`${out}/card.html`, `<style>${css}</style>${h}`); await p.goto(`file://${out}/card.html`); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300); await p.screenshot({ path: `${out}/card-${name}.png` }); };
await card('night', `<span class="k">Valencia, Spain · 29 October 2024</span><h1 style="font-size:100px;line-height:1.04;letter-spacing:-.045em">Imagine losing someone you love because <span style="color:#b42318">no one knew how much rain was coming</span> that day.</h1><p style="font-size:42px">Red warning: <b>about 7:30 AM</b>. Phone alert: <b>about 8 PM</b>. More than <b>150</b> people had already died.</p>`);
await card('impact', `<span class="k" style="color:#3f63d6">What if · illustrative estimate</span><h1 style="font-size:96px;line-height:1.03">An alert 12 hours earlier, about 8 AM, comes before the first death.</h1><p style="font-size:42px">Published warning curves put about <b>€1.1 bn</b> of Valencia's <b>€4.8 bn</b> insured loss within reach.</p><span class="ill">Illustrative what-if, not a measured outcome · Day (1970) warning curve · CCS insured loss</span>`);
await card('close', `<span class="k" style="color:#3f63d6">One engine, every sector</span><h1 style="font-size:112px">Signal → map → task → alert.</h1>
<div class="row"><div><span class="lab" style="color:#1e6b34">Built</span> Flood · Fire · Farms</div><div class="f"><span class="lab">Next</span> Drought · Air quality · Infrastructure · Landslides</div></div>
<p style="font-size:30px;margin-top:50px;color:#47506b">Try it live</p><p style="font:600 64px M;letter-spacing:-.01em;color:#3f63d6;margin-top:6px">spaceapps.parsariahi.com</p><span class="ill" style="font-size:26px">Parsa Riahi · solo build</span>`);
await b.close(); console.log('cards ok');
