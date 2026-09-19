// End-to-end production check used by every six-hour refresh, after data publication.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {waitForPublishedRefresh} from './news_live_wait.mjs';
const browser=await chromium.launch();
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
    assert.equal(await chip.locator('.news-label').textContent(),'Trending');
    const checked=Date.parse(await chip.getAttribute('data-checked-at'));
    assert.ok(checked>=Date.now()-18*3600000 && checked<=Date.now()+300000,'collection must be current');
    if(process.env.NEWS_CHECKED_AT) assert.ok(checked>=Date.parse(process.env.NEWS_CHECKED_AT),'this refresh must have reached the reader');
    assert.ok(await chip.locator('.news-source').textContent());
    assert.ok(await chip.locator('.news-date').textContent());
    assert.match(await chip.getAttribute('href'),/^https:\/\//);
    assert.ok((await chip.locator('.news-title').textContent()).length>=20);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    assert.deepEqual(errors,[]);
    console.log(`news live ${width}px: ${await chip.locator('.news-title').textContent()}`);
    // Each production run proves the deployed runtime will actually rotate without another
    // network response. Advancing the browser clock does not change the published feed.
    const state=await page.evaluate(()=>JSON.parse(localStorage.getItem('texas-ai-news-v2')));
    assert.equal(state.rotation_version,1,'deployed feed must include scheduled rotation');
    const now=Date.now();
    const current=state.editions.filter(e=>Date.parse(e.starts_at)<=now).at(-1);
    const next=state.editions.find(e=>Date.parse(e.starts_at)>now);
    assert.ok(current && next,'a distinct next edition must be ready');
    assert.equal(await chip.getAttribute('href'),current.selected.url,'reader must see the current scheduled edition');
    assert.notEqual(current.selected.url,next.selected.url,'six-hour update must change the headline');
    await page.route('https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/news-data/ledger/news/latest.json*',route=>route.abort());
    await page.clock.install({time:new Date(next.starts_at)});
    await page.evaluate(()=>document.dispatchEvent(new Event('visibilitychange')));
    await page.waitForFunction(url=>document.querySelector('.news-chip').href===url,next.selected.url);
    assert.equal(await chip.locator('.news-title').textContent(),next.selected.title);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    console.log(`news live ${width}px: verified next six-hour edition without a network refresh`);
    await page.close();
  }
} finally {await browser.close();}
