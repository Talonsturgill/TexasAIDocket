// The real native story dialog, including focus, refresh, expiry and optional navigation.
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import {chromium} from 'playwright';

const site=path.resolve(process.env.SITE || 'docs');
const fixtures=JSON.parse(execFileSync(process.env.PYTHON || 'python3',['-c',String.raw`
import datetime as dt, json, re, sys
from pathlib import Path
sys.path.insert(0, 'scripts/site')
import csp, news_headlines as news
now = news.instant('2026-09-17T20:00:00Z')
first = {'title': 'Texas researchers use AI to improve winter flight safety',
         'url': 'https://dallasinnovates.com/news/browser-fixture/',
         'first_seen_at': '2026-09-17T19:00:00Z',
         'summary': 'Texas researchers test how drones respond to ice so aircraft can operate safely in Texas winters.'}
second = {'title': 'Texas plans a semiconductor fabrication facility in Bryan',
          'url': 'https://siliconangle.com/browser-fixture/',
          'first_seen_at': '2026-09-17T18:00:00Z',
          'summary': 'A semiconductor facility proposal will expand chip manufacturing capacity in Bryan, Texas.'}
states = {}
for name, rows in [
    ('normal', [first, second]),
    ('missing', [{**first, 'summary': ''}]),
    ('long', [{**first, 'title': 'Texas researchers test new AI tools for winter flight safety, regional electrical systems and infrastructure planning',
              'summary': ('Researchers are testing the equipment under controlled conditions and will publish the results. ' * 10)[:1000]}]),
    ('literal', [{**first, 'title': 'Texas AI research includes <img src=x onerror=window.__newsXSS=true> results',
                 'summary': 'The source reports a test result &lt;img src=x onerror=window.__newsXSS=true&gt;.'}]),
    ('aging', [{**first, 'first_seen_at': '2026-09-10T21:00:00Z'}, second]),
]:
    states[name] = news.snapshot({'articles': []}, now, {'articles': rows}, rotate=True)
updated = [{**first, 'summary': 'The updated source excerpt says Texas will publish the winter flight results.'}, second]
states['updated'] = news.snapshot({'articles': updated}, now + dt.timedelta(minutes=2),
                                  states['normal'], rotate=True)
original = Path(sys.argv[1], 'index.html').read_text()
out = {}
for name, state in states.items():
    body, count = re.subn(r'(<section class="hero rise">).*?(<h1\b)',
        lambda match: match[1] + '\n' + news.markup('2026-09-17', state) + '\n' + match[2],
        original, count=1, flags=re.S)
    assert count == 1
    body = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', body)
    out[name] = {'html': csp.apply(body), 'state': state}
print(json.dumps(out))
`,site],{encoding:'utf8',maxBuffer:8*1024*1024}));
const mime={'.css':'text/css','.js':'text/javascript','.woff2':'font/woff2','.png':'image/png',
  '.webp':'image/webp','.svg':'image/svg+xml'};
const server=http.createServer((req,res)=>{
  const pathname=decodeURIComponent(req.url.split('?')[0]);
  for(const [name,fixture] of Object.entries(fixtures))
    if(pathname===`/__popup_${name}.html`) return res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'}).end(fixture.html);
  let file=path.join(site,pathname);
  if(!file.startsWith(site+path.sep)) return res.writeHead(403).end();
  try {
    if(fs.statSync(file).isDirectory()) file=path.join(file,'index.html');
    res.writeHead(200,{'Content-Type':mime[path.extname(file)] || 'text/html; charset=utf-8'});
    fs.createReadStream(file).pipe(res);
  } catch {res.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const browser=await chromium.launch();
const feed='**/news-data/ledger/news/latest.json*';
const activeControl=page=>page.locator('.news-slide[aria-hidden="false"] .news-link');
let checked=0;
const errorsFor=new WeakMap();
async function reader(name='normal',width=390,height=844,motion='reduce',touch=false,modal=true) {
  const state=fixtures[name].state;
  const page=await browser.newPage({viewport:{width,height},reducedMotion:motion,hasTouch:touch,isMobile:touch});
  const errors=[];
  errorsFor.set(page,errors);
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(/violates.*Content Security Policy|Refused to execute inline/.test(m.text()))errors.push(m.text());});
  if(!modal) await page.addInitScript(()=>{HTMLDialogElement.prototype.showModal=undefined;});
  await page.clock.install({time:new Date(state.checked_at)});
  let incoming=state;
  await page.route(feed,r=>r.fulfill({json:incoming,headers:{'access-control-allow-origin':'*'}}));
  await page.goto(`http://127.0.0.1:${server.address().port}/__popup_${name}.html`);
  await page.waitForFunction(()=>document.querySelector('.news-chip')?.dataset.newsLoaded==='true');
  await page.evaluate(()=>document.fonts.ready);
  await page.evaluate(()=>document.getAnimations().forEach(a=>{if(a.effect?.getComputedTiming().iterations!==Infinity)a.finish();}));
  assert.deepEqual(errors,[]);
  assert.equal(await page.locator('main').evaluate(el=>el.querySelector('h1,h2').tagName),'H1',
    'the hidden reading dialog must not replace the page heading');
  return {page,state,update:value=>{incoming=value;}};
}
async function show(page,state) {
  const url=await activeControl(page).getAttribute('data-news-url');
  const story=state.editions.flatMap(e=>e.stories).find(s=>s.url===url);
  assert.equal(await activeControl(page).evaluate(el=>el.tagName),'BUTTON');
  const location=page.url(), tabs=page.context().pages().length;
  await activeControl(page).click();
  await page.waitForFunction(()=>document.querySelector('#news-story').open);
  assert.equal(page.url(),location,'opening the summary must stay on this page');
  assert.equal(page.context().pages().length,tabs,'opening a summary must not create a tab');
  const dialog=page.locator('#news-story');
  assert.equal(await dialog.locator('.news-story-title').textContent(),story.title);
  assert.equal(await dialog.locator('.news-story-summary').textContent(),story.summary ||
    'A short summary is not available for this report. Read the source for the full story.');
  assert.equal(await dialog.locator('.news-story-publisher').textContent(),story.publisher);
  assert.equal(await dialog.locator('.news-story-date').getAttribute('datetime'),story.first_seen_at);
  assert.equal(await dialog.locator('.news-story-source').getAttribute('href'),story.url);
  assert.equal(await dialog.locator('.news-story-source').getAttribute('target'),'_blank');
  assert.equal(await dialog.locator('.news-story-source').getAttribute('rel'),'noopener noreferrer');
  assert.equal(await dialog.evaluate(el=>el.matches(':modal')),true);
  assert.equal(await page.locator('html').evaluate(el=>el.classList.contains('news-story-open')),true);
  assert.deepEqual(errorsFor.get(page),[]);
  return story;
}
async function closed(page) {
  // Native dialog close dispatches after the rendering step; advance that step under the fake clock.
  await page.clock.runFor(50);
  await page.waitForFunction(()=>!document.querySelector('#news-story').open &&
    !document.documentElement.classList.contains('news-story-open'));
}
try {
  for(const name of ['normal','long']) for(const width of [1440,390,320]) {
    const {page,state}=await reader(name,width);
    await show(page,state);
    const bounds=await page.locator('#news-story').boundingBox();
    assert.ok(bounds.x>=0 && bounds.y>=0 && bounds.x+bounds.width<=width && bounds.y+bounds.height<=844);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    assert.ok(await page.locator('#news-story').evaluate(el=>el.scrollWidth<=el.clientWidth+1));
    const url=await activeControl(page).getAttribute('data-news-url');
    await page.clock.runFor(16000);
    assert.equal(await activeControl(page).getAttribute('data-news-url'),url);
    await page.locator('.news-story-close').click();
    await closed(page);
    assert.equal(await page.locator('html').evaluate(el=>el.classList.contains('news-story-open')),false);
    await page.close();checked++;
  }
  for(const key of ['Enter','Space']) {
    const {page}=await reader();
    await activeControl(page).focus();
    await page.keyboard.press(key);
    await page.waitForFunction(()=>document.querySelector('#news-story').open);
    await page.keyboard.press('Shift+Tab');
    assert.equal(await page.locator('.news-story-close').evaluate(el=>el===document.activeElement),true,
      'reverse Tab from the title reaches the preceding close control');
    for(const direction of ['Tab','Shift+Tab']) {
      const visited=new Set();
      for(let i=0;i<6;i++) {
        await page.keyboard.press(direction);
        assert.equal(await page.evaluate(()=>!!document.activeElement.closest('#news-story')),true,'focus stays in the native modal');
        visited.add(await page.evaluate(()=>document.activeElement.className));
        assert.equal(await page.evaluate(()=>getComputedStyle(document.activeElement).outlineStyle),'solid',
          'the active modal control has a visible keyboard focus ring');
      }
      assert.ok(visited.has('news-story-close') && visited.has('news-story-source'),
        'both keyboard directions reach close and the optional source');
    }
    await page.keyboard.press('Escape');
    await closed(page);
    assert.equal(await activeControl(page).evaluate(el=>el===document.activeElement),true,'keyboard close restores the headline');
    await page.close();checked++;
  }
  {
    const {page}=await reader();
    await page.locator('.news-next').click();
    assert.equal(await page.locator('#news-story').evaluate(el=>el.open),false,'navigation controls remain separate');
    for(const target of ['label','padding']) {
      const title=await activeControl(page).locator('.news-title').textContent();
      if(target==='label') await page.locator('.news-label').click();
      else await page.locator('.news-chip').click({position:{x:5,y:5}});
      await page.waitForFunction(()=>document.querySelector('#news-story').open);
      assert.equal(await page.locator('.news-story-title').textContent(),title,'the entire story box opens its summary');
      await page.locator('.news-story-close').click();
      await closed(page);
    }
    await page.close();checked++;
  }
  {
    const {page,state}=await reader('normal',390,844,'no-preference');
    await show(page,state);
    await page.mouse.move(0,0);
    await page.locator('.news-story-close').click();
    await closed(page);
    await page.mouse.move(0,0);
    const url=await activeControl(page).getAttribute('data-news-url');
    await page.clock.runFor(5100);
    assert.notEqual(await activeControl(page).getAttribute('data-news-url'),url,'pointer dismissal resumes the five-second carousel');
    await page.close();checked++;
  }
  {
    const {page,state}=await reader();
    await show(page,state);
    await page.mouse.click(5,5);
    await closed(page);
    await page.close();checked++;
  }
  {
    const {page}=await reader('normal',390,844,'no-preference',true);
    await page.evaluate(()=>{
      document.activeElement.blur();
      const control=document.querySelector('.news-next');
      control.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch'}));
      control.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerType:'touch'}));
      control.dispatchEvent(new MouseEvent('click',{bubbles:true,detail:1}));
    });
    const url=await activeControl(page).getAttribute('data-news-url');
    assert.equal(await page.evaluate(()=>document.activeElement.tagName),'BODY','simulate a touch browser that does not focus tapped buttons');
    await page.clock.runFor(16000);
    assert.equal(await activeControl(page).getAttribute('data-news-url'),url,
      'manual touch selection stays paused without hover or button focus');
    assert.equal(await page.locator('.news-chip').getAttribute('data-news-playing'),'false');
    await page.close();checked++;
  }
  {
    const {page,state}=await reader('normal',390,844,'reduce',false,false);
    const link=activeControl(page);
    assert.equal(await link.evaluate(el=>el.tagName),'A','an unsupported modal keeps a working source link');
    const url=await link.getAttribute('href');
    assert.ok(state.editions[0].stories.some(s=>s.url===url));
    assert.equal(await page.locator('#news-story').isVisible(),false);
    await page.context().route(url,r=>r.fulfill({contentType:'text/html',body:'<title>Compatibility source link</title>'}));
    const opened=page.waitForEvent('popup');
    await link.click();
    const source=await opened;
    await source.waitForLoadState();
    assert.equal(source.url(),url);
    await source.close();await page.close();checked++;
  }
  {
    const {page,state}=await reader();
    const story=await show(page,state);
    await page.route(feed,r=>r.abort());
    const next=state.editions[1];
    await page.clock.fastForward(Date.parse(next.starts_at)-Date.parse(state.checked_at)+100);
    assert.equal(await page.locator('.news-story-title').textContent(),story.title);
    assert.equal(await page.locator('.news-story-summary').textContent(),story.summary);
    assert.equal(await page.locator('.news-chip').getAttribute('data-edition-at'),state.editions[0].starts_at,
      'an offline edition change does not replace the opener while reading');
    await page.locator('.news-story-close').click();
    await closed(page);
    assert.equal(await page.locator('.news-chip').getAttribute('data-edition-at'),next.starts_at,
      'closing applies the queued six-hour edition');
    await page.close();checked++;
  }
  {
    const {page}=await reader('normal',390,844,'no-preference',true);
    const url=await activeControl(page).getAttribute('data-news-url');
    await activeControl(page).tap();
    await page.waitForFunction(()=>document.querySelector('#news-story').open);
    await page.clock.runFor(16000);
    assert.equal(await activeControl(page).getAttribute('data-news-url'),url);
    await page.locator('.news-story-close').tap();
    await closed(page);
    await page.clock.runFor(5100);
    assert.notEqual(await activeControl(page).getAttribute('data-news-url'),url,'touch dismissal resumes rotation');
    await page.close();checked++;
  }
  for(const name of ['missing','literal']) {
    const {page,state}=await reader(name);
    await show(page,state);
    assert.equal(await page.locator('#news-story img, #news-story script').count(),0);
    assert.equal(await page.evaluate(()=>window.__newsXSS),undefined);
    await page.close();checked++;
  }
  {
    const {page,state,update}=await reader();
    const story=await show(page,state);
    await page.clock.runFor(120000);
    update(fixtures.updated.state);
    await page.evaluate(()=>dispatchEvent(new Event('online')));
    await page.waitForFunction(checked=>document.querySelector('.news-chip').dataset.checkedAt===checked,fixtures.updated.state.checked_at);
    assert.equal(await page.locator('.news-story-summary').textContent(),story.summary,'refresh does not rewrite text being read');
    await page.locator('.news-story-close').click();
    await closed(page);
    await activeControl(page).click();
    assert.equal(await page.locator('.news-story-summary').textContent(),fixtures.updated.state.articles.find(s=>s.url===story.url).summary,
      'the next opening receives an updated source excerpt even within the same edition');
    await page.close();checked++;
  }
  {
    const {page,state}=await reader('aging');
    const old=state.articles.find(s=>s.first_seen_at==='2026-09-10T21:00:00Z');
    if(await activeControl(page).getAttribute('data-news-url')!==old.url) await page.locator('.news-next').click();
    await show(page,state);
    await page.route(feed,r=>r.abort());
    await page.clock.fastForward(2*3600000);
    assert.equal(await page.locator('#news-story').evaluate(el=>el.open),true);
    assert.equal(await page.locator('.news-story-title').textContent(),old.title,'expiry does not dismiss an open reading view');
    await page.locator('.news-story-close').click();
    await closed(page);
    assert.notEqual(await activeControl(page).getAttribute('data-news-url'),old.url,'closing removes the expired story');
    await page.close();checked++;
  }
  {
    const {page,state}=await reader();
    const story=await show(page,state);
    await page.context().route(story.url,r=>r.fulfill({contentType:'text/html',body:'<title>Source link test</title>'}));
    const popup=page.waitForEvent('popup');
    await page.locator('.news-story-source').click();
    const source=await popup;
    await source.waitForLoadState();
    assert.equal(source.url(),story.url,'only the explicit full article action opens a source tab');
    assert.equal(await source.evaluate(()=>window.opener),null);
    assert.equal(await page.locator('#news-story').evaluate(el=>el.open),true);
    await source.close();await page.close();checked++;
  }
  console.log(`news popup: ${checked} responsive, keyboard, focus, pause, refresh, expiry and optional-source cases passed`);
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
