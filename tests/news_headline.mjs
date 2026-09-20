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
titles = ['AI diagnoses pancreatic cancer in screening trials', 'ChatGPT faces new school privacy rules',
          'Anthropic releases smaller coding models', 'AI forecasts hurricanes along the coast',
          'AI accelerators reduce electricity consumption', 'Robots use AI to sort textile waste',
          'AI video raises election security concerns', 'AI deciphers ancient manuscripts',
          'AI forecasts volcanic eruptions from seismic signals', 'AI optimizes freight delivery routes',
          'AI helps astronomers map distant galaxies']
rows = [{**article, 'title': 'Texas ' + title, 'url': 'https://dallasinnovates.com/fixture-' + str(i)}
        for i, title in enumerate(titles)]
for name, count in [('ten', 10), ('two', 2), ('one', 1), ('oversized', 11)]:
    news.STORIES_PER_EDITION = count
    states[name] = news.snapshot({'articles': []}, now, {'articles': rows[:count]}, rotate=True)
news.STORIES_PER_EDITION = 10
old = {**rows[1], 'first_seen_at': '2026-09-10T21:00:00Z'}
states['aging'] = news.snapshot({'articles': []}, now,
    {'articles': [article, old], 'editions': [{'starts_at': news.stamp(news.edition_start(now)),
                                            'selected': old}]}, rotate=True)
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
const activeLink = page => page.locator('.news-slide[aria-hidden="false"] .news-link');
async function pageFor(state,width=390,payload=null) {
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
  // Install before the runtime starts timers. Switching clocks after a real-time rotation
  // leaves native timeouts outside the fake clock's cancellation and pause controls.
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
  for(const name of ['current','empty']) for(const width of [1440,1024,768,600,480,390,360,320])
    cases.push({pathname:`/__news_${name}.html`,state:fixtures[name].state,width});
  for(const {pathname,state,width} of cases) {
    const page=await pageFor(state,width);
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(/violates.*Content Security Policy|Refused to execute inline/.test(m.text()))errors.push(m.text());});
    await loaded(page,pathname);
    const chip=page.locator('.news-chip');
    assert.equal(await chip.count(),1);
    assert.equal(await chip.isVisible(),true);
    assert.equal(await chip.evaluate(el=>getComputedStyle(el).opacity),'1','the news strip must be fully painted');
    const size=await chip.evaluate(el=>({inside:el.scrollWidth<=el.clientWidth+1,right:el.getBoundingClientRect().right,
      height:el.getBoundingClientRect().height,overflow:document.documentElement.scrollWidth>innerWidth}));
    assert.ok(size.inside && size.height>=44 && size.right<=width && !size.overflow,JSON.stringify({width,...size}));
    if(state.selected) {
      assert.equal(await activeLink(page).getAttribute('href'),state.selected.url);
      assert.equal(await activeLink(page).locator('.news-source').textContent(),state.selected.publisher);
      assert.equal(await activeLink(page).locator('.news-title').textContent(),state.selected.title);
      assert.equal(await chip.locator('.news-label').textContent(),Date.parse(state.checked_at)-Date.parse(state.selected.first_seen_at)>=72*3600000?'Recent':'Trending');
      assert.match(await activeLink(page).locator('.news-date').textContent(),/^[A-Z][a-z]+ \d{1,2}(st|nd|rd|th)$/);
      await activeLink(page).focus();
      assert.equal(await activeLink(page).evaluate(el=>getComputedStyle(el).outlineStyle),'solid');
      await activeLink(page).evaluate(el=>el.blur());
      await page.clock.runFor(1);
      await page.mouse.move(0,0);
      const before=await page.locator('.hero h1').evaluate(el=>el.getBoundingClientRect().top);
      await page.clock.fastForward(37*3600000);
      const retained=(state.editions?.at(-1)?.selected || state.selected).url;
      assert.equal(await activeLink(page).getAttribute('href'),retained,'a missed refresh must use the reserve queue, then keep its dated last headline');
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
      assert.equal(await activeLink(page).getAttribute('href'),retained,'cached HTML must retain the last scheduled story');
      await page.clock.fastForward(8*24*3600000);
      assert.equal(await activeLink(page).getAttribute('href'),'/articles/','week-old data is not passed off as fresh news');
    } else {
      assert.equal(await chip.getAttribute('data-news-status'),'empty');
      assert.equal(await activeLink(page).getAttribute('href'),'/articles/');
    }
    assert.deepEqual(errors,[]);
    await page.close();checked++;
  }
  const base=fixtures.current.state;
  const fresh=structuredClone(base);
  fresh.checked_at='2026-09-17T20:01:00Z';
  fresh.selected={...fresh.selected,title:'Texas AI technique makes surgery safer and more precise',url:'https://news.mit.edu/2026/ai-surgery/',publisher:'MIT News'};
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
    assert.equal(await activeLink(page).locator('.news-title').textContent(),fresh.selected.title,'fresh data must replace old or empty HTML');
    await page.unroute(feed);
    await page.route(feed,route=>route.abort());
    await page.reload();
    await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsLoaded==='true');
    assert.equal(await activeLink(page).locator('.news-title').textContent(),fresh.selected.title,'offline reload retains last successful data');
    await page.close();checked++;
  }
  const badStates=[
    {...fresh,checked_at:'2036-01-01T00:00:00Z'},
    {...fresh,checked_at:'2026-09-17T19:55:00Z'},
    {...fresh,selected:{...fresh.selected,url:'javascript:alert(1)'}},
    {...fresh,selected:{...fresh.selected,url:'https://news.mit.edu.evil.example/story'}},
    {...fresh,selected:{...fresh.selected,publisher:'Fake publisher'}},
    {...fresh,selected:null},
    {...fresh,selected:{...fresh.selected,title:'Bitdeer AI to lease 65MW data center in Johor, Malaysia',url:'https://www.datacenterdynamics.com/en/news/malaysia/',publisher:'Data Center Dynamics'}},
    {...fresh,selected:{...fresh.selected,title:'Cybersecurity researchers gain access to OpenAI repository using Claude',url:'https://siliconangle.com/global-ai/',publisher:'SiliconANGLE'}},
    {...fresh,selected:{...fresh.selected,title:'A new chapter for MIT Reads',
      url:'https://news.mit.edu/2026/new-chapter-mit-reads-0918',publisher:'MIT News',
      feed:'https://news.mit.edu/rss/topic/artificial-intelligence2'}},
    {...fresh,selected:{...fresh.selected,title:'A community reading program opens today',
      url:'https://openai.com/index/community-reading',publisher:'OpenAI',feed:'https://openai.com/news/rss.xml'}},
  ];
  for(const bad of badStates) {
    const page=await pageFor(base,390,bad);
    await loaded(page,'/__news_current.html');
    assert.equal(await activeLink(page).locator('.news-title').textContent(),base.selected.title,'invalid or older data must not replace a good headline');
    await page.close();checked++;
  }
  for(const offTopic of [badStates[6],badStates[7],badStates[badStates.length-2]]) {
  for(const initial of ['current','empty']) {
    const page=await pageFor(base,390,offTopic);
    await page.addInitScript(data=>localStorage.setItem('texas-ai-news-v2',JSON.stringify(data)),offTopic);
    await loaded(page,`/__news_${initial}.html`);
    assert.notEqual(await activeLink(page).locator('.news-title').textContent(),offTopic.selected.title,
      'an off-topic cached story and live response must not override relevant reporting');
    assert.equal(await activeLink(page).getAttribute('href'),initial==='current'?base.selected.url:'/articles/');
    await page.close();checked++;
  }
  }
  // An expired lead is removed on its own deadline. An offline reader keeps the
  // remaining valid story, even though the cached snapshot's original lead has expired.
  {
    const sample=fixtures.aging.state,page=await pageFor(sample,390,sample);
    await loaded(page,'/__news_aging.html');
    assert.equal(await page.locator('.news-slide').count(),2);
    await page.unroute(feed);
    await page.route(feed,route=>route.abort());
    await page.clock.fastForward(2*3600000);
    const retained=sample.editions[0].stories[1];
    assert.equal(await activeLink(page).getAttribute('href'),retained.url);
    assert.equal(await page.locator('.news-slide').count(),1);
    await page.reload();
    await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsLoaded==='true');
    assert.equal(await activeLink(page).getAttribute('href'),retained.url);
    await page.clock.fastForward(7*24*3600000);
    assert.equal(await activeLink(page).getAttribute('href'),'/articles/');
    await page.close();checked++;
  }
  // A full ten-story carousel and quiet one/two-story pools reuse reporting across
  // refreshes. Neither a cached repeat nor an offline twelve-hour return is invalid.
  for(const name of ['ten','two','one']) for(const width of [1440,390]) {
    const sample=fixtures[name].state;
    const page=await pageFor(sample,width,sample);
    await loaded(page,`/__news_${name}.html`);
    const chip=page.locator('.news-chip');
    const count=sample.editions[0].stories.length;
    assert.equal(await chip.locator('.news-slide').count(),count);
    const height=(await chip.boundingBox()).height;
    for(const story of sample.editions[0].stories) {
      assert.equal(await activeLink(page).getAttribute('href'),story.url);
      assert.equal(await activeLink(page).locator('.news-date').getAttribute('datetime'),story.first_seen_at);
      assert.ok(Math.abs((await chip.boundingBox()).height-height)<1);
      if(count>1) await chip.locator('.news-next').click();
    }
    await page.evaluate(()=>document.activeElement.blur());
    await page.mouse.move(0,0);
    await page.unroute(feed);
    await page.route(feed,route=>route.abort());
    for(const edition of sample.editions.slice(1)) {
      await page.clock.fastForward(Date.parse(edition.starts_at)-await page.evaluate(()=>Date.now())+100);
      assert.equal(await activeLink(page).getAttribute('href'),edition.selected.url);
      assert.equal(await chip.locator('.news-slide').count(),edition.stories.length);
    }
    await page.reload();
    await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsLoaded==='true');
    assert.equal(await activeLink(page).getAttribute('href'),sample.editions.at(-1).selected.url);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.close();checked++;
  }
  {
    const sample=fixtures.ten.state,bad=structuredClone(fixtures.oversized.state);
    bad.checked_at=new Date(Date.parse(sample.checked_at)+60000).toISOString();
    const page=await pageFor(sample,390,bad);
    await loaded(page,'/__news_ten.html');
    assert.equal(await page.locator('.news-chip').getAttribute('data-checked-at'),sample.checked_at,
      'eleven distinct valid stories must still exceed the pool bound');
    assert.equal(await page.locator('.news-slide').count(),10);
    await page.close();checked++;
  }
  // An unchanged feed and a complete network outage must still change what readers see
  // at the six-hour boundary. A reload must choose the same edition as an already-open tab.
  if(state.rotation_version===1) {
    for(const width of [1440,390]) {
      const page=await pageFor(state,width,state);
      await loaded(page,'/');
      let previous=await activeLink(page).getAttribute('href');
      await page.unroute(feed);
      await page.route(feed,route=>route.abort());
      for(const edition of state.editions.slice(1)) {
        const delta=Date.parse(edition.starts_at)-await page.evaluate(()=>Date.now())+100;
        await page.clock.fastForward(delta);
        assert.equal(await activeLink(page).getAttribute('href'),edition.selected.url);
        if(edition.stories.length>1) assert.notEqual(edition.selected.url,previous);
        previous=edition.selected.url;
        await page.reload();
        await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsLoaded==='true');
        assert.equal(await activeLink(page).getAttribute('href'),edition.selected.url,'reload retains current edition');
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      }
      await page.close();checked++;
    }
    for(const mutation of ['irrelevant','non-Texas','unsafe','repeat','wrong-slot']) {
      const bad=structuredClone(state);
      bad.checked_at=new Date(Date.parse(state.checked_at)+60000).toISOString();
      if(mutation==='irrelevant') {bad.editions[1].selected.title='A new chapter for MIT Reads';delete bad.editions[1].selected.summary;}
      if(mutation==='non-Texas') {bad.editions[1].selected.title='AI infrastructure expands in Malaysia';delete bad.editions[1].selected.summary;}
      if(mutation==='unsafe') bad.editions[1].selected.url='javascript:alert(1)';
      if(mutation==='repeat') {
        const entry=bad.editions[1],repeat=entry.stories.find(s=>s.url===bad.selected.url);
        entry.selected=repeat;
        entry.stories=[repeat,...entry.stories.filter(s=>s.url!==repeat.url)];
      }
      if(mutation==='wrong-slot') bad.editions[1].starts_at=bad.editions[0].starts_at;
      const page=await pageFor(state,390,bad);
      await loaded(page,'/');
      assert.equal(await page.locator('.news-chip').getAttribute('data-checked-at'),state.checked_at,'invalid reserve must be rejected');
      await page.close();checked++;
    }
  }
  if(state.carousel_version===1) {
    for(const width of [1440,390]) {
      const page=await pageFor(state,width,state);
      await page.emulateMedia({reducedMotion:'no-preference',colorScheme:width===1440?'light':'dark'});
      let requests=0;
      await page.unroute(feed);
      await page.route(feed,route=>{requests++;return route.fulfill({json:state,headers:{'access-control-allow-origin':'*'}});});
      await loaded(page,'/');
      const chip=page.locator('.news-chip');
      const stories=state.editions[0].stories;
      assert.equal(await chip.getAttribute('data-news-cadence'),'5000');
      assert.equal(await chip.locator('.news-slide').count(),stories.length);
      assert.ok(stories.length>=1 && stories.length<=10,'use only the qualifying Texas stories');
      const height=(await chip.boundingBox()).height;
      let last=await activeLink(page).getAttribute('href'), changedAt=null;
      const seen=new Set([last]);
      for(let i=0;i<stories.length;i++) {
        await page.waitForFunction(previous=>document.querySelector('.news-slide[aria-hidden="false"] .news-link').href!==previous,last,{timeout:7000});
        const time=await page.evaluate(()=>performance.now());
        if(changedAt!==null) assert.ok(Math.abs(time-changedAt-5000)<650,`cadence ${time-changedAt}ms`);
        changedAt=time;
        last=await activeLink(page).getAttribute('href');seen.add(last);
        const story=stories.find(s=>s.url===last);
        assert.ok(story,'only an edition member may be shown');
        assert.equal(await activeLink(page).locator('.news-title').textContent(),story.title);
        assert.equal(await activeLink(page).locator('.news-source').textContent(),story.publisher);
        assert.equal(await activeLink(page).locator('.news-date').getAttribute('datetime'),story.first_seen_at);
        assert.ok(Math.abs((await chip.boundingBox()).height-height)<1,'headline rotation must not move the page');
        assert.equal(await chip.locator('.news-slide:not([inert])').count(),1,'only the active link belongs in keyboard navigation');
      }
      assert.equal(seen.size,stories.length);
      assert.equal(requests,1,'headline rotation must make no additional feed or publisher requests');
      await chip.hover();
      await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsPlaying==='false');
      last=await activeLink(page).getAttribute('href');
      await page.clock.fastForward(16000);
      assert.equal(await activeLink(page).getAttribute('href'),last,'hover freezes the visible story');
      await chip.locator('.news-next').click();
      const next=await activeLink(page).getAttribute('href');
      assert.notEqual(next,last);
      assert.equal(await chip.getAttribute('data-news-playing'),'false');
      await page.mouse.move(0,0);
      await page.clock.fastForward(16000);
      assert.equal(await activeLink(page).getAttribute('href'),next,'manual browsing stays paused');
      assert.equal(await chip.locator('.news-slides').getAttribute('aria-live'),'polite');
      await chip.locator('.news-prev').click();
      await page.waitForFunction(url=>document.querySelector('.news-slide[aria-hidden="false"] .news-link').href===url,last,{timeout:2000});
      assert.equal(await activeLink(page).getAttribute('href'),last);
      await activeLink(page).focus();
      await page.mouse.move(0,0);
      await page.clock.fastForward(16000);
      assert.equal(await activeLink(page).getAttribute('href'),last,'keyboard focus freezes the link');
      // Crossing an edition while a reader has paused must not replace their active link.
      const following=state.editions[1];
      await page.clock.fastForward(Date.parse(following.starts_at)-await page.evaluate(()=>Date.now())+100);
      assert.equal(await activeLink(page).getAttribute('href'),last);
      await chip.locator('.news-next').click();
      assert.equal(await activeLink(page).getAttribute('href'),following.stories[0].url,'manual navigation safely installs a pending edition');
      assert.equal(await chip.locator('.news-slide').count(),following.stories.length);
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      await page.close();checked++;
    }
    {
      const page=await pageFor(state,390,state);
      await loaded(page,'/');
      const chip=page.locator('.news-chip');
      const first=await activeLink(page).getAttribute('href');
      await page.clock.fastForward(16000);
      assert.equal(await activeLink(page).getAttribute('href'),first,'reduced motion starts paused');
      assert.equal(await chip.getAttribute('data-news-playing'),'false');
      assert.equal(await chip.locator('.news-toggle,.news-count').count(),0);
      await chip.locator('.news-next').click();
      assert.notEqual(await activeLink(page).getAttribute('href'),first,'reduced motion supports manual navigation');
      await chip.locator('.news-prev').click();
      await page.mouse.move(0,0);
      await page.evaluate(()=>document.activeElement.blur());
      await page.clock.runFor(1);
      await page.emulateMedia({reducedMotion:'no-preference'});
      await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsPlaying==='true');
      await page.clock.runFor(4000);
      assert.equal(await activeLink(page).getAttribute('href'),first,'headlines must not advance before the five-second interval');
      await page.clock.runFor(1100);
      const second=await activeLink(page).getAttribute('href');
      assert.notEqual(second,first,'rotation resumes after leaving controls and restoring motion');
      await page.evaluate(()=>{
        Object.defineProperty(document,'hidden',{configurable:true,value:true});
        document.dispatchEvent(new Event('visibilitychange'));
      });
      await page.clock.fastForward(16000);
      assert.equal(await activeLink(page).getAttribute('href'),second,'background tabs do not rotate');
      await page.evaluate(()=>{
        Object.defineProperty(document,'hidden',{configurable:true,value:false});
        document.dispatchEvent(new Event('visibilitychange'));
      });
      await page.clock.runFor(5001);
      assert.notEqual(await activeLink(page).getAttribute('href'),second);
      await page.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));
      await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsPlaying==='false');
      const offscreen=await activeLink(page).getAttribute('href');
      await page.clock.fastForward(16000);
      assert.equal(await activeLink(page).getAttribute('href'),offscreen,'offscreen headlines do not rotate');
      await chip.scrollIntoViewIfNeeded();
      await page.waitForFunction(()=>document.querySelector('.news-chip').dataset.newsPlaying==='true');
      await page.mouse.move(0,0);
      await activeLink(page).dispatchEvent('pointerdown',{pointerType:'touch'});
      const pressed=await activeLink(page).getAttribute('href');
      await page.clock.fastForward(16000);
      assert.equal(await activeLink(page).getAttribute('href'),pressed,'touch presses freeze the destination');
      await activeLink(page).dispatchEvent('pointercancel',{pointerType:'touch'});
      await page.clock.runFor(5100);
      assert.notEqual(await activeLink(page).getAttribute('href'),pressed,'cancelled touch resumes rotation');
      await page.close();checked++;
    }
    for(const mutation of ['irrelevant','non-Texas','unsafe','duplicate','empty','oversized','missing-version','legacy-version']) {
      const bad=structuredClone(state);
      bad.checked_at=new Date(Date.parse(state.checked_at)+60000).toISOString();
      const stories=bad.editions[0].stories;
      if(mutation==='irrelevant') {stories[2].title='A new chapter for MIT Reads';delete stories[2].summary;}
      if(mutation==='non-Texas') {stories[2].title='AI infrastructure expands in Malaysia';delete stories[2].summary;}
      if(mutation==='unsafe') stories[2].url='javascript:alert(1)';
      if(mutation==='duplicate') stories[2]=structuredClone(stories[1]);
      if(mutation==='empty') stories.length=0;
      if(mutation==='oversized') stories.push(structuredClone(stories[1]));
      if(mutation==='missing-version') delete bad.carousel_version;
      if(mutation==='legacy-version') delete bad.rotation_version;
      const page=await pageFor(state,390,bad);
      await loaded(page,'/');
      assert.equal(await page.locator('.news-chip').getAttribute('data-checked-at'),state.checked_at,'every supporting story must be validated');
      await page.close();checked++;
    }
  }
  console.log(`news headline: ${checked} layouts and feed recovery, outage, cached expiry, date, attribution and unsafe-payload cases passed`);
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
