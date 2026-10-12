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
    assert.ok(['current','recent'].includes(await chip.getAttribute('data-news-status')));
    assert.equal(await chip.getAttribute('data-news-cadence'),'5000');
    assert.ok(['Trending','Recent'].includes(await chip.locator('.news-label').textContent()));
    const checked=Date.parse(await chip.getAttribute('data-checked-at'));
    assert.ok(checked>=Date.now()-18*3600000 && checked<=Date.now()+300000,'collection must be current');
    if(process.env.NEWS_CHECKED_AT) assert.ok(checked>=Date.parse(process.env.NEWS_CHECKED_AT),'this refresh must have reached the reader');
    const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('texas-ai-news-v2')));
    assert.equal(state.rotation_version,1);
    assert.equal(state.carousel_version,1,'published feed must contain story pools');
    const now=Date.now();
    const current=state.editions.filter(e=>Date.parse(e.starts_at)<=now).at(-1);
    const next=state.editions.find(e=>Date.parse(e.starts_at)>now);
    assert.ok(current,'a current edition must be ready');
    assert.ok(next || current.stories.length===1,'only a single-story quiet period may lack a distinct next edition');
    assert.ok(current.stories.length>=1 && current.stories.length<=10);
    assert.equal(await chip.locator('.news-slide').count(),current.stories.length);
    // Rotation reads cached metadata. Blocking the endpoint proves neither cadence needs it.
    await page.route('https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/news-data/ledger/news/latest.json*',route=>route.abort());
    const height=(await chip.boundingBox()).height;
    let last=await activeLink(page).getAttribute('data-news-url'), changedAt=null;
    const seen=new Set();
    for(let i=0;i<current.stories.length;i++) {
      const story=current.stories.find(s=>s.url===last);
      assert.ok(story,'visible link must belong to the current edition');
      const geography=await chip.evaluate(el=>JSON.parse(el.dataset.newsRelevance));
      const text=story.title+' '+(story.summary || '');
      assert.ok(new RegExp(geography.texas,'i').test(text) || new RegExp(geography.austin,'i').test(story.title) ||
        (story.publisher==='Dallas Innovates' && new RegExp(geography.local).test(story.title)), 'every visible story needs Texas evidence');
      assert.equal(await activeLink(page).locator('.news-title').textContent(),story.title);
      assert.equal(await activeLink(page).locator('.news-source').textContent(),story.publisher);
      assert.equal(await activeLink(page).locator('.news-date').getAttribute('datetime'),story.first_seen_at);
      assert.equal(await activeLink(page).evaluate(el=>el.tagName),'BUTTON');
      assert.equal(await activeLink(page).getAttribute('aria-haspopup'),'dialog');
      assert.ok(Math.abs((await chip.boundingBox()).height-height)<1,'headlines must share a stable height');
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      seen.add(last);
      if(current.stories.length>1) {
        await page.waitForFunction(previous=>document.querySelector('.news-slide[aria-hidden="false"] .news-link').dataset.newsUrl!==previous,last,{timeout:7500});
        const time=await page.evaluate(()=>performance.now());
        if(changedAt!==null) assert.ok(Math.abs(time-changedAt-5000)<750,`five-second cadence drifted to ${time-changedAt}ms`);
        changedAt=time;
        last=await activeLink(page).getAttribute('data-news-url');
      }
    }
    assert.equal(seen.size,current.stories.length);
    console.log(`news live ${width}px: ${seen.size} attributed headlines rotate every five seconds without layout shift or network requests`);
    const summaries=new Set();
    for(let i=0;i<current.stories.length;i++) {
      const url=await activeLink(page).getAttribute('data-news-url');
      const story=current.stories.find(s=>s.url===url);
      const location=page.url(),tabs=page.context().pages().length;
      await activeLink(page).click();
      const dialog=page.locator('#news-story');
      await page.waitForFunction(()=>document.querySelector('#news-story').open);
      assert.equal(page.url(),location);
      assert.equal(page.context().pages().length,tabs,'headline summaries stay on the page');
      assert.equal(await dialog.locator('.news-story-title').textContent(),story.title);
      assert.equal(await dialog.locator('.news-story-summary').textContent(),story.summary ||
        'A short summary is not available for this report. Read the source for the full story.');
      assert.equal(await dialog.locator('.news-story-publisher').textContent(),story.publisher);
      assert.equal(await dialog.locator('.news-story-date').getAttribute('datetime'),story.first_seen_at);
      assert.equal(await dialog.locator('.news-story-source').getAttribute('href'),story.url);
      assert.equal(await dialog.locator('.news-story-source').getAttribute('rel'),'noopener noreferrer');
      const bounds=await dialog.boundingBox();
      assert.ok(bounds.x>=0 && bounds.x+bounds.width<=width && bounds.y>=0 && bounds.y+bounds.height<=900);
      assert.ok(await dialog.evaluate(el=>el.scrollWidth<=el.clientWidth+1));
      assert.equal(await chip.getAttribute('data-news-playing'),'false');
      summaries.add(url);
      await dialog.locator('.news-story-close').click();
      await page.waitForFunction(()=>!document.querySelector('#news-story').open &&
        !document.documentElement.classList.contains('news-story-open'));
      if(current.stories.length>1) await chip.locator('.news-next').click();
    }
    assert.equal(summaries.size,current.stories.length);
    await page.mouse.move(0,0);
    await page.evaluate(()=>document.activeElement.blur());
    console.log(`news live ${width}px: ${summaries.size} source summaries open on-page with an optional full-article link`);
    if (!next) {
      assert.deepEqual(errors,[]);
      await page.close();
      continue;
    }
    await page.clock.install({time:new Date(next.starts_at)});
    await page.evaluate(()=>document.dispatchEvent(new Event('visibilitychange')));
    await page.waitForFunction(url=>document.querySelector('.news-slide[aria-hidden="false"] .news-link').dataset.newsUrl===url,next.selected.url);
    assert.equal(await activeLink(page).locator('.news-title').textContent(),next.selected.title);
    assert.equal(await chip.locator('.news-slide').count(),next.stories.length);
    if(next.stories.length>1) assert.notEqual(current.selected.url,next.selected.url);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    assert.deepEqual(errors,[]);
    console.log(`news live ${width}px: next six-hour story pool replaces the current pool while offline`);
    await page.close();
  }
} finally {await browser.close();}
