import { chromium } from "playwright";
import { resolve } from "node:path";
const b = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
const p = await b.newPage({ viewport:{width:600,height:400}, colorScheme:"dark", deviceScaleFactor:5 });
await p.setContent(`<body style="margin:0;background:#08060F;display:grid;place-items:center;height:400px">
<div style="width:140px;height:140px">${(await (async()=>{
  const { execSync } = await import('node:child_process');
  return execSync('python3 -c "import sys; sys.path.insert(0,\\'scripts/site\\'); import sky; print(sky.tumbleweed_svg())"',
    {cwd: process.cwd()}).toString();
})())}</div>
<style>svg{width:100%;height:100%}svg path{fill:none;stroke:#E0956A;stroke-width:1.6;stroke-linecap:round;opacity:.65}</style>
</body>`);
await p.waitForTimeout(400);
await p.screenshot({ path: `${process.env.OUT}/weed-zoom.png`, clip:{x:200,y:120,width:200,height:180} });
await b.close(); console.log("ok");
