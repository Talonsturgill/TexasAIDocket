// Whole-archive layout and reader behavior, including the no-script fallback.
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import fs from 'node:fs';
import nodePath from 'node:path';
import http from 'node:http';
import { chromium } from 'playwright';

const site = nodePath.resolve(process.env.SITE || 'docs');
const mime = {'.css':'text/css','.js':'text/javascript','.woff2':'font/woff2',
  '.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'};
const server = http.createServer((req, res) => {
  let file = nodePath.join(site, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(site + nodePath.sep)) return res.writeHead(403).end();
  try {
    if (fs.statSync(file).isDirectory()) file = nodePath.join(file, 'index.html');
    res.writeHead(200, {'Content-Type':mime[nodePath.extname(file)] || 'text/html; charset=utf-8'});
    fs.createReadStream(file).pipe(res);
  } catch { res.writeHead(404).end(); }
});
if (!process.env.BASE_URL) await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = process.env.BASE_URL || `http://127.0.0.1:${server.address().port}`;
const path = '/articles/2026-09-18/';
const output = 'out/2026-09-18/tmp/article-review';
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
let checks = 0;
const check = (condition, label) => { assert.ok(condition, label); checks++; };

try {
  const dates = fs.readdirSync(nodePath.join(site, 'articles')).filter(name => /^\d{4}-\d{2}-\d{2}$/.test(name)).sort();
  check(dates.length > 0, 'the archive is not empty');
  for (const width of [1440, 390, 320]) {
    const page = await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    for (const date of dates) {
      await page.goto(`${base}/articles/${date}/`);
      await page.evaluate(() => document.fonts.ready);
      check(await page.locator('.article-edition').count() === 1, `${date} ${width} has the new article`);
      await page.locator('.edition-slide img').first().evaluate(image => image.decode());
      check(await page.locator('.edition-story > p').count() >= 2, `${date} ${width} has a narrative lead`);
      check(await page.locator('.edition-source-list > li').count() > 0, `${date} ${width} has source links`);
      check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${date} ${width} no overflow`);
      const slides = await page.locator('.edition-slide').count();
      await page.locator('.edition-track').focus();
      await page.keyboard.press('End');
      await page.waitForFunction(n => document.querySelector('.edition-count').textContent === `${n} of ${n}`, slides);
      check(await page.locator('[data-next]').isDisabled(), `${date} ${width} complete gallery`);
      if (['2026-08-16','2026-08-26','2026-08-29','2026-09-12'].includes(date)) {
        await page.locator('.edition-track').focus();
        await page.keyboard.press('Home');
        await page.evaluate(() => scrollTo(0, 0));
        await page.screenshot({path:`${output}/${date}-${width}.png`});
      }
    }
    check(errors.length === 0, `${width} archive scripts run cleanly ${errors.join('; ')}`);
    await page.close();
  }
  for (const width of [1440, 390, 320]) {
    const context = await browser.newContext({ viewport: { width, height: 1000 },
      reducedMotion: 'reduce', isMobile: width < 600, hasTouch: width < 600 });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base + path, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(() => document.querySelector('.edition-slide img').naturalWidth > 0);
    const count = page.locator('.edition-count');
    const track = page.locator('.edition-track');
    check(await page.locator('.edition-controls').isVisible(), `${width} gallery controls appear`);
    check(await page.locator('[data-previous]').isDisabled(), `${width} first slide has no previous`);
    await page.screenshot({ path: `${output}/${width}-opening.png` });
    await page.getByRole('button', { name: 'Next slide', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.edition-count').textContent === '2 of 9');
    await track.focus();
    await page.keyboard.press('End');
    await page.waitForFunction(() => document.querySelector('.edition-count').textContent === '9 of 9');
    check(await page.locator('[data-next]').isDisabled(), `${width} keyboard reaches last slide`);
    await page.getByRole('button', { name: 'Previous slide', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.edition-count').textContent === '8 of 9');
    await page.getByRole('button', { name: 'View all', exact: true }).click();
    check(await page.locator('.edition-gallery').evaluate(el => el.classList.contains('is-all')),
      `${width} expanded deck uses the full gallery`);
    for (const image of await page.locator('.edition-slide img').all()) {
      await image.scrollIntoViewIfNeeded();
      await image.evaluate(el => el.decode());
      check(await image.evaluate(el => el.naturalWidth > 0), `${width} slide image loads`);
    }
    await page.getByRole('button', { name: 'One at a time', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.edition-count').textContent === '8 of 9');
    await track.focus();
    await page.keyboard.press('Home');
    await page.waitForFunction(() => document.querySelector('.edition-count').textContent === '1 of 9');
    if (width === 390) {
      await track.scrollIntoViewIfNeeded();
      const box = await track.boundingBox();
      const cdp = await context.newCDPSession(page);
      const y = box.y + box.height / 2;
      await cdp.send('Input.dispatchTouchEvent', {type:'touchStart', touchPoints:[{x:box.x + box.width * .85,y}]});
      for (const fraction of [.7,.55,.4,.25,.1]) {
        await cdp.send('Input.dispatchTouchEvent', {type:'touchMove',touchPoints:[{x:box.x + box.width * fraction,y}]});
      }
      await cdp.send('Input.dispatchTouchEvent', {type:'touchEnd',touchPoints:[]});
      await page.waitForFunction(() => document.querySelector('.edition-count').textContent !== '1 of 9');
      checks++;
    }
    await page.getByRole('link', { name: 'Read the story' }).click();
    check(await page.locator('#story').evaluate(el => el.getBoundingClientRect().top < 180),
      `${width} story link jumps past artwork`);
    check(await page.locator('.edition-source-list > li').count() === 6, `${width} sources are deduplicated`);
    check(!(await page.locator('.edition-verified').evaluate(el => el.open)), `${width} detailed evidence starts folded`);
    await page.locator('.edition-verified summary').click();
    check(await page.locator('.edition-verified .claims > li').count() === 18, `${width} every claim is retained`);
    check(await page.locator('#claim-c18').isVisible(), `${width} final claim is readable`);
    await page.locator('.edition-verified summary').click();
    check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${width} no horizontal overflow`);
    check(errors.length === 0, `${width} no browser script errors ${errors.join('; ')}`);
    if (width !== 320) {
      await page.locator('#story').scrollIntoViewIfNeeded();
      await page.screenshot({path:`${output}/${width}-story.png`});
      await page.locator('.edition-sources').scrollIntoViewIfNeeded();
      await page.screenshot({path:`${output}/${width}-sources.png`});
    }
    await page.getByRole('link', {name:'Suggest a correction'}).click();
    check(await page.locator('#contactbox').isVisible(), `${width} correction opens the existing message form`);
    check((await page.locator('#contactmsg').inputValue()).includes('https://texasaidocket.com' + path),
      `${width} correction includes the article address`);
    await page.locator('#contactclose').click();
    await context.close();
  }
  const noScript = await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const page = await noScript.newPage();
  await page.goto(base + path);
  check(await page.locator('.edition-story').isVisible(), 'the article is readable without JavaScript');
  check(await page.locator('.edition-controls').isHidden(), 'inactive controls stay hidden without JavaScript');
  check(await page.locator('.edition-slide').count() === 9, 'all slides remain in the native scroll gallery');
  await page.locator('.edition-verified summary').click();
  check(await page.locator('#claim-c18').isVisible(), 'native evidence disclosure works without JavaScript');
  console.log(`article_edition: ${checks} reader checks passed`);
} finally {
  await browser.close();
  if (server.listening) await new Promise(resolve => server.close(resolve));
}
