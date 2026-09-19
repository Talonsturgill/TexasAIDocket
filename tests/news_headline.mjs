// Production markup and CSP, with feed failures and time progression under browser control.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {execFileSync} from 'node:child_process';
import {chromium} from 'playwright';
import {waitForPublishedRefresh} from './news_live_wait.mjs';
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
      const retained=(state.editions?.at(-1)?.selected || state.selected).url;
      assert.equal(await chip.getAttribute('href'),retained,'a missed refresh must use the reserve queue, then keep its dated last headline');
      assert.equal(await chip.locator('.news-label').textContent(),'Recent');
      const after=await page.locator('.hero h1').evaluate(el=>el.getBoundingClientRect().top);
      // Aging the same headline must not shift the page. A different queued headline can
      // wrap onto another line; check its actual bounds instead of forcing the old height.
      if(retained===state.selected.url)
        assert.ok(Math.abs(before-after)<1,JSON.stringify({pathname,width,before,after,chip:await chip.boundingBox()}));
      assert.ok(await chip.evaluate(el=>el.scrollWidth<=el.clientWidth+1 &&
        el.getBoundingClientRect().height>=44 && document.documentElement.scrollWidth<=innerWidth));
      await page.reload();
      await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsLoaded==='true');
      assert.equal(await chip.getAttribute('href'),retained,'cached HTML must retain the last scheduled story');
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
  // Exercise the production verifier against delayed delivery, then a permanently stale feed.
  {
    const page=await pageFor(base,390,base);
    await loaded(page,'/__news_current.html');
    await page.unroute(feed);
    let requests=0;
    await page.route(feed,route=>route.fulfill({json:++requests<2?base:fresh,headers:{'access-control-allow-origin':'*'}}));
    assert.equal(await waitForPublishedRefresh(page,fresh.checked_at,{timeout:5000,pollInterval:20}),fresh.checked_at);
    assert.equal(requests,2,'publication check must wait through stale responses');
    await page.close();checked++;
  }
  {
    const page=await pageFor(base,390,base);
    await loaded(page,'/__news_current.html');
    await assert.rejects(waitForPublishedRefresh(page,fresh.checked_at,{timeout:1500,pollInterval:20}),/did not reach the reader/);
    await page.close();checked++;
  }
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
    {...fresh,selected:{...fresh.selected,title:'A new chapter for MIT Reads',
      url:'https://news.mit.edu/2026/new-chapter-mit-reads-0918',publisher:'MIT News',
      feed:'https://news.mit.edu/rss/topic/artificial-intelligence2'}},
    {...fresh,selected:{...fresh.selected,title:'A community reading program opens today',
      url:'https://openai.com/index/community-reading',publisher:'OpenAI',feed:'https://openai.com/news/rss.xml'}},
  ];
  for(const bad of badStates) {
    const page=await pageFor(base,390,bad);
    await loaded(page,'/__news_current.html');
    assert.equal(await page.locator('.news-title').textContent(),base.selected.title,'invalid or older data must not replace a good headline');
    await page.close();checked++;
  }
  const offTopic=badStates[badStates.length-2];
  for(const initial of ['current','empty']) {
    const page=await pageFor(base,390,offTopic);
    await page.addInitScript(data=>localStorage.setItem('texas-ai-news-v2',JSON.stringify(data)),offTopic);
    await loaded(page,`/__news_${initial}.html`);
    assert.notEqual(await page.locator('.news-title').textContent(),offTopic.selected.title,
      'an off-topic cached story and live response must not override relevant reporting');
    assert.equal(await page.locator('.news-chip').getAttribute('href'),initial==='current'?base.selected.url:'/articles/');
    await page.close();checked++;
  }
  // An unchanged feed and a complete network outage must still change what readers see
  // at the six-hour boundary. A reload must choose the same edition as an already-open tab.
  if(state.rotation_version===1) {
    for(const width of [1440,390]) {
      const page=await pageFor(state,width,state);
      await loaded(page,'/');
      const initial=await page.locator('.news-chip').getAttribute('href');
      await page.unroute(feed);
      await page.route(feed,route=>route.abort());
      for(const edition of state.editions.slice(1)) {
        const delta=Date.parse(edition.starts_at)-await page.evaluate(()=>Date.now())+100;
        await page.clock.fastForward(delta);
        assert.equal(await page.locator('.news-chip').getAttribute('href'),edition.selected.url);
        assert.notEqual(edition.selected.url,initial);
        await page.reload();
        await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsLoaded==='true');
        assert.equal(await page.locator('.news-chip').getAttribute('href'),edition.selected.url,'reload retains current edition');
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      }
      await page.close();checked++;
    }
    for(const mutation of ['irrelevant','unsafe','repeat','wrong-slot']) {
      const bad=structuredClone(state);
      bad.checked_at=new Date(Date.parse(state.checked_at)+60000).toISOString();
      if(mutation==='irrelevant') bad.editions[1].selected.title='A new chapter for MIT Reads';
      if(mutation==='unsafe') bad.editions[1].selected.url='javascript:alert(1)';
      if(mutation==='repeat') bad.editions[1].selected=structuredClone(bad.selected);
      if(mutation==='wrong-slot') bad.editions[1].starts_at=bad.editions[0].starts_at;
      const page=await pageFor(state,390,bad);
      await loaded(page,'/');
      assert.equal(await page.locator('.news-chip').getAttribute('data-checked-at'),state.checked_at,'invalid reserve must be rejected');
      await page.close();checked++;
    }
  }
  console.log(`news headline: ${checked} layouts and feed recovery, outage, cached expiry, date, attribution and unsafe-payload cases passed`);
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
