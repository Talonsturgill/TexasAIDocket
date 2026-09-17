// Production markup and CSP, with feed failures and time progression under browser control.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {execFileSync} from 'node:child_process';
import {chromium} from 'playwright';
const site=path.resolve(process.env.SITE || 'docs');
const state=JSON.parse(fs.readFileSync('ledger/news/latest.json','utf8'));
const fixtures=JSON.parse(execFileSync(process.env.PYTHON || 'python3',['-c',String.raw`
import json, re, sys
from pathlib import Path
sys.path.insert(0, 'scripts/site')
import csp, news_headlines as news
now = news.instant('2026-09-17T20:00:00Z')
article = {'title': 'Texas AI researchers open a new robotics laboratory to test autonomous systems for manufacturing and regional transportation',
           'url': 'https://dallasinnovates.com/news-browser-fixture/', 'first_seen_at': '2026-09-17T19:00:00Z'}
states = {'current': news.snapshot({'articles': []}, now, {'articles': [article]}),
          'empty': news.snapshot({'articles': []}, now)}
original = Path(sys.argv[1], 'index.html').read_text()
out = {}
for name, state in states.items():
    body, count = re.subn(r'(<section class="hero rise">).*?(<h1\b)',
                         lambda m: m[1] + '\n' + news.markup('2026-09-17', state) + '\n' + m[2], original, count=1, flags=re.S)
    assert count == 1
    body = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', body)
    out[name] = {'html': csp.apply(body), 'state': state}
print(json.dumps(out))
`,site],{encoding:'utf8',maxBuffer:8*1024*1024}));
const mime={'.css':'text/css','.js':'text/javascript','.woff2':'font/woff2','.webp':'image/webp','.svg':'image/svg+xml'};
const server=http.createServer((req,res)=>{
  const pathname=decodeURIComponent(req.url.split('?')[0]);
  for(const [name,fixture] of Object.entries(fixtures)) {
    if(pathname===`/__news_${name}.html`) return res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'}).end(fixture.html);
  }
  let file=path.join(site,pathname);
  if(!file.startsWith(site+path.sep)) return res.writeHead(403).end();
  try {
    if(fs.statSync(file).isDirectory()) file=path.join(file,'index.html');
    res.writeHead(200,{'Content-Type':mime[path.extname(file)] || 'text/html; charset=utf-8'});
    fs.createReadStream(file).pipe(res);
  } catch {res.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const url=`http://127.0.0.1:${server.address().port}`;
const executable=process.env.PLAYWRIGHT_CHROMIUM || '/opt/pw-browsers/chromium';
const browser=await chromium.launch(fs.existsSync(executable)?{executablePath:executable}:{});
const feed='https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/news-data/ledger/news/latest.json*';
let checked=0;
async function pageFor(state,width=390,payload=null) {
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
  await page.clock.install({time:new Date(state.checked_at)});
  await page.route(feed,route=>payload ? route.fulfill({json:payload,headers:{'access-control-allow-origin':'*'}}) : route.abort());
  return page;
}
async function loaded(page,pathname) {
  await page.goto(url+pathname);
  await page.waitForFunction(()=>document.querySelector('.news-chip')?.dataset.newsLoaded==='true');
  await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>document.getAnimations().forEach(a=>{if(a.effect?.getComputedTiming().iterations!==Infinity)a.finish();}));
}
try {
  const cases=[{pathname:'/',state,width:1440}];
  for(const [name,fixture] of Object.entries(fixtures)) for(const width of [1440,1024,768,600,480,390,360,320])
    cases.push({pathname:`/__news_${name}.html`,state:fixture.state,width});
  for(const {pathname,state,width} of cases) {
    const page=await pageFor(state,width);
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(/violates.*Content Security Policy|Refused to execute inline/.test(m.text()))errors.push(m.text());});
    await loaded(page,pathname);
    const chip=page.locator('.news-chip');
    assert.equal(await chip.count(),1);
    assert.equal(await chip.isVisible(),true);
    const size=await chip.evaluate(el=>({inside:el.scrollWidth<=el.clientWidth+1,right:el.getBoundingClientRect().right,
      height:el.getBoundingClientRect().height,overflow:document.documentElement.scrollWidth>innerWidth}));
    assert.ok(size.inside && size.height>=44 && size.right<=width && !size.overflow,JSON.stringify({width,...size}));
    if(state.selected) {
      assert.equal(await chip.getAttribute('href'),state.selected.url);
      assert.equal(await chip.locator('.news-source').textContent(),state.selected.publisher);
      assert.equal(await chip.locator('.news-title').textContent(),state.selected.title);
      assert.equal(await chip.locator('.news-label').textContent(),'Trending');
      assert.match(await chip.locator('.news-date').textContent(),/^[A-Z][a-z]+ \d{1,2}(st|nd|rd|th), \d{4}$/);
      await chip.focus();
      assert.equal(await chip.evaluate(el=>getComputedStyle(el).outlineStyle),'solid');
      const before=await page.locator('.hero h1').evaluate(el=>el.getBoundingClientRect().top);
      await page.clock.fastForward(37*3600000);
      assert.equal(await chip.getAttribute('href'),state.selected.url,'a missed refresh must keep the dated headline');
      assert.equal(await chip.locator('.news-label').textContent(),'Recent');
      const after=await page.locator('.hero h1').evaluate(el=>el.getBoundingClientRect().top);
      assert.ok(Math.abs(before-after)<1,JSON.stringify({pathname,width,before,after,chip:await chip.boundingBox()}));
      await page.reload();
      await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsLoaded==='true');
      assert.equal(await chip.getAttribute('href'),state.selected.url,'cached HTML must not erase a 36-hour-old story');
      await page.clock.fastForward(8*24*3600000);
      assert.equal(await chip.getAttribute('href'),'/articles/','week-old data is not passed off as fresh news');
    } else {
      assert.equal(await chip.getAttribute('data-news-status'),'empty');
      assert.equal(await chip.getAttribute('href'),'/articles/');
    }
    assert.deepEqual(errors,[]);
    await page.close();checked++;
  }
  const base=fixtures.current.state;
  const fresh=structuredClone(base);
  fresh.checked_at='2026-09-17T20:01:00Z';
  fresh.selected={...fresh.selected,title:'New AI technique makes surgery safer and more precise',url:'https://news.mit.edu/2026/ai-surgery/',publisher:'MIT News'};
  for(const initial of ['current','empty']) {
    const page=await pageFor(base,390,fresh);
    await loaded(page,`/__news_${initial}.html`);
    assert.equal(await page.locator('.news-title').textContent(),fresh.selected.title,'fresh data must replace old or empty HTML');
    await page.unroute(feed);
    await page.route(feed,route=>route.abort());
    await page.reload();
    await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsLoaded==='true');
    assert.equal(await page.locator('.news-title').textContent(),fresh.selected.title,'offline reload retains last successful data');
    await page.close();checked++;
  }
  const badStates=[
    {...fresh,checked_at:'2036-01-01T00:00:00Z'},
    {...fresh,checked_at:'2026-09-17T19:55:00Z'},
    {...fresh,selected:{...fresh.selected,url:'javascript:alert(1)'}},
    {...fresh,selected:{...fresh.selected,url:'https://news.mit.edu.evil.example/story'}},
    {...fresh,selected:{...fresh.selected,publisher:'Fake publisher'}},
    {...fresh,selected:null},
  ];
  for(const bad of badStates) {
    const page=await pageFor(base,390,bad);
    await loaded(page,'/__news_current.html');
    assert.equal(await page.locator('.news-title').textContent(),base.selected.title,'invalid or older data must not replace a good headline');
    await page.close();checked++;
  }
  console.log(`news headline: ${checked} layouts and feed recovery, outage, cached expiry, date, attribution and unsafe-payload cases passed`);
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
