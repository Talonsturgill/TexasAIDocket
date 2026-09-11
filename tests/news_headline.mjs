// Real generated markup and CSP, with a fixed clock so archived builds stay testable.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { chromium } from 'playwright';
const site = path.resolve(process.env.SITE || 'docs');
const state = JSON.parse(fs.readFileSync('ledger/news/latest.json', 'utf8'));
const mime = { '.css':'text/css', '.js':'text/javascript', '.woff2':'font/woff2', '.webp':'image/webp', '.svg':'image/svg+xml' };
const server = http.createServer((req,res) => {
  let file = path.join(site, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(site + path.sep)) return res.writeHead(403).end();
  try {
    if (fs.statSync(file).isDirectory()) file=path.join(file,'index.html');
    res.writeHead(200, {'Content-Type':mime[path.extname(file)] || 'text/html; charset=utf-8'});
    fs.createReadStream(file).pipe(res);
  } catch { res.writeHead(404).end(); }
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const url=`http://127.0.0.1:${server.address().port}`;
const executable=process.env.PLAYWRIGHT_CHROMIUM || '/opt/pw-browsers/chromium';
const browser=await chromium.launch(fs.existsSync(executable)?{executablePath:executable}:{});
let checked=0;
try {
  for (const width of [1440,1024,768,600,480,390,360,320]) {
    const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
    await page.clock.install({time:new Date(state.checked_at)});
    await page.goto(url);
    await page.evaluate(()=>document.fonts.ready);
    const chip=page.locator('.news-chip');
    if (!state.selected) {
      assert.equal(await chip.count(),0); await page.close();continue;
    }
    assert.equal(await chip.isVisible(),true);
    assert.equal(await chip.locator('.news-title').textContent(),state.selected.title);
    assert.equal(await chip.locator('.news-source').textContent(),state.selected.publisher);
    assert.equal(await chip.getAttribute('href'),state.selected.url.replaceAll('&amp;','&'));
    assert.equal(await chip.getAttribute('target'),'_blank');
    assert.ok((await chip.getAttribute('rel')).includes('noopener'));
    const sizes=await chip.evaluate(el=>{
      const r=el.getBoundingClientRect(), h=document.querySelector('.hero h1').getBoundingClientRect();
      return {width:r.width,height:r.height,right:r.right,inside:el.scrollWidth<=el.clientWidth+1,
              gap:h.top-r.bottom,overflow:document.documentElement.scrollWidth>innerWidth};
    });
    assert.ok(sizes.inside && sizes.height>=44 && sizes.right<=width && !sizes.overflow,JSON.stringify({width,...sizes}));
    assert.ok(sizes.gap>=15,JSON.stringify({width,...sizes}));
    await chip.focus();
    assert.equal(await chip.evaluate(el=>getComputedStyle(el).outlineStyle),'solid');
    await page.clock.fastForward(Date.parse(state.expires_at)-Date.parse(state.checked_at)+200);
    assert.equal(await chip.isVisible(),false,'cached headline must expire without another deploy');
    await page.close(); checked++;
  }
  // A newly loaded, already-stale cached page must also hide the link immediately.
  const page=await browser.newPage();
  await page.clock.install({time:new Date(Date.parse(state.expires_at || state.checked_at)+1000)});
  await page.goto(url);
  assert.equal(await page.locator('.news-chip').isVisible(),false);
  await page.close();
  console.log(`news headline: ${checked} desktop/phone layouts, attribution, focus and expiry passed`);
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
