// Each production refresh checks the real homepage, cadence and offline edition replacement.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {waitForPublishedRefresh} from './news_live_wait.mjs';
const browser=await chromium.launch();
const activeLink=page=>page.locator('.news-slide[aria-hidden="false"] .news-link');
try {
  for(const width of [1440,390]) {
    const page=await browser.newPage({viewport:{width,height:900}});
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto('https://texasaidocket.com/',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.querySelector('.news-chip')?.dataset.newsLoaded==='true');
    if(process.env.NEWS_CHECKED_AT) await waitForPublishedRefresh(page,process.env.NEWS_CHECKED_AT);
    const chip=page.locator('.news-chip');
    assert.equal(await chip.isVisible(),true);
    assert.equal(await chip.getAttribute('data-news-status'),'current');
    assert.equal(await chip.getAttribute('data-news-cadence'),'5000');
    assert.equal(await chip.locator('.news-label').textContent(),'Trending');
    const checked=Date.parse(await chip.getAttribute('data-checked-at'));
    assert.ok(checked>=Date.now()-18*3600000 && checked<=Date.now()+300000,'collection must be current');
    if(process.env.NEWS_CHECKED_AT) assert.ok(checked>=Date.parse(process.env.NEWS_CHECKED_AT),'this refresh must have reached the reader');
    const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('texas-ai-news-v2')));
    assert.equal(state.rotation_version,1);
    assert.equal(state.carousel_version,1,'published feed must contain story pools');
    const now=Date.now();
    const current=state.editions.filter(e=>Date.parse(e.starts_at)<=now).at(-1);
    const next=state.editions.find(e=>Date.parse(e.starts_at)>now);
    assert.ok(current && next,'a distinct next edition must be ready');
    assert.ok(current.stories.length>=1 && current.stories.length<=5);
    assert.equal(await chip.locator('.news-slide').count(),current.stories.length);
    // Rotation reads cached metadata. Blocking the endpoint proves neither cadence needs it.
    await page.route('https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/news-data/ledger/news/latest.json*',route=>route.abort());
    const height=(await chip.boundingBox()).height;
    let last=await activeLink(page).getAttribute('href'), changedAt=null;
    const seen=new Set();
    for(let i=0;i<current.stories.length;i++) {
      const story=current.stories.find(s=>s.url===last);
      assert.ok(story,'visible link must belong to the current edition');
      assert.equal(await activeLink(page).locator('.news-title').textContent(),story.title);
      assert.equal(await activeLink(page).locator('.news-source').textContent(),story.publisher);
      assert.equal(await activeLink(page).locator('.news-date').getAttribute('datetime'),story.first_seen_at);
      assert.equal(await activeLink(page).getAttribute('rel'),'noopener noreferrer');
      assert.ok(Math.abs((await chip.boundingBox()).height-height)<1,'headlines must share a stable height');
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      seen.add(last);
      if(current.stories.length>1) {
        await page.waitForFunction(previous=>document.querySelector('.news-slide[aria-hidden="false"] .news-link').href!==previous,last,{timeout:7500});
        const time=await page.evaluate(()=>performance.now());
        if(changedAt!==null) assert.ok(Math.abs(time-changedAt-5000)<750,`five-second cadence drifted to ${time-changedAt}ms`);
        changedAt=time;
        last=await activeLink(page).getAttribute('href');
      }
    }
    assert.equal(seen.size,current.stories.length);
    console.log(`news live ${width}px: ${seen.size} attributed headlines rotate every five seconds without layout shift or network requests`);
    await page.clock.install({time:new Date(next.starts_at)});
    await page.evaluate(()=>document.dispatchEvent(new Event('visibilitychange')));
    await page.waitForFunction(url=>document.querySelector('.news-slide[aria-hidden="false"] .news-link').href===url,next.selected.url);
    assert.equal(await activeLink(page).locator('.news-title').textContent(),next.selected.title);
    assert.equal(await chip.locator('.news-slide').count(),next.stories.length);
    assert.notEqual(current.selected.url,next.selected.url);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    assert.deepEqual(errors,[]);
    console.log(`news live ${width}px: next six-hour story pool replaces the current pool while offline`);
    await page.close();
  }
} finally {await browser.close();}
