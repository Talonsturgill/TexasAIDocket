// End-to-end production check used by every six-hour refresh, after data publication.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const browser=await chromium.launch();
try {
  for(const width of [1440,390]) {
    const page=await browser.newPage({viewport:{width,height:900}});
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto('https://texasaidocket.com/',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.querySelector('.news-chip')?.dataset.newsLoaded==='true');
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
    await page.close();
  }
} finally {await browser.close();}
