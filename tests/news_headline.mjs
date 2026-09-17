// Real generated markup and CSP, with a fixed clock so archived builds stay testable.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { execFileSync } from 'node:child_process';
import { chromium } from 'playwright';
const site = path.resolve(process.env.SITE || 'docs');
const state = JSON.parse(fs.readFileSync('ledger/news/latest.json', 'utf8'));
// Exercise both outcomes on every run, even when the collected snapshot is empty. Generate
// fixtures with the production renderer and rebuild their CSP hashes; never bypass the policy.
const fixtures = JSON.parse(execFileSync(process.env.PYTHON || 'python3', ['-c', String.raw`
import json, re, sys
from pathlib import Path
sys.path.insert(0, 'scripts/site')
import csp, news_headlines as news
now = news.instant('2026-09-11T20:00:00Z')
article = {
    'title': 'Texas AI researchers open a new robotics laboratory to test autonomous systems for manufacturing and regional transportation',
    'url': 'https://dallasinnovates.com/news-browser-fixture/',
    'first_seen_at': '2026-09-11T19:00:00Z',
}
states = {
    'current': news.snapshot({'articles': []}, now, {'articles': [article]}),
    'empty': news.snapshot({'articles': []}, now),
}
original = Path(sys.argv[1], 'index.html').read_text()
out = {}
for name, state in states.items():
    body, count = re.subn(r'(<section class="hero rise">).*?(<h1\b)',
                         lambda m: m[1] + '\n' + news.markup('2026-09-11', state) + '\n' + m[2],
                         original, count=1, flags=re.S)
    assert count == 1, 'homepage hero fixture target missing'
    body = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', body)
    out[name] = {'html': csp.apply(body), 'state': state}
print(json.dumps(out))
`, site], {encoding:'utf8',maxBuffer:8*1024*1024}));
const mime = { '.css':'text/css', '.js':'text/javascript', '.woff2':'font/woff2', '.webp':'image/webp', '.svg':'image/svg+xml' };
const server = http.createServer((req,res) => {
  const pathname=decodeURIComponent(req.url.split('?')[0]);
  for (const [name, fixture] of Object.entries(fixtures)) {
    if (pathname === `/__news_${name}.html`) {
      return res.writeHead(200, {'Content-Type':'text/html; charset=utf-8'}).end(fixture.html);
    }
  }
  let file = path.join(site, pathname);
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
const unavailable='Fresh headlines are temporarily unavailable.';
async function assertEmpty(chip) {
  assert.equal(await chip.isVisible(),true,'the bar must remain visible without a current story');
  assert.equal(await chip.getAttribute('data-news-status'),'empty');
  assert.equal(await chip.locator('.news-title').textContent(),unavailable);
  assert.equal(await chip.getAttribute('href'),null,'an expired story must no longer be a link');
  assert.equal(await chip.locator('.news-source').isVisible(),false);
}
try {
  const cases=[{pathname:'/',state,width:1440}];
  for (const [name, fixture] of Object.entries(fixtures)) {
    for (const width of [1440,1024,768,600,480,390,360,320]) {
      cases.push({pathname:`/__news_${name}.html`,state:fixture.state,width});
    }
  }
  for (const {pathname,state,width} of cases) {
    const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
    const errors=[];
    page.on('pageerror', error=>errors.push(error.message));
    page.on('console', message=>{
      if (/Refused to execute inline script/.test(message.text())) errors.push(message.text());
    });
    await page.clock.install({time:new Date(state.checked_at)});
    await page.goto(url+pathname);
    await page.evaluate(()=>document.fonts.ready);
    // A reduced-motion animation can still have a staggered delay. The mocked JS clock
    // does not advance the compositor clock; finish finite entrance animations before
    // measuring geometry so the test cannot compare two different entrance frames.
    await page.evaluate(()=>document.getAnimations().forEach(animation=>{
      if (animation.effect?.getComputedTiming().iterations !== Infinity) animation.finish();
    }));
    const chip=page.locator('.news-chip');
    assert.equal(await chip.count(),1);
    assert.equal(await chip.isVisible(),true);
    const sizes=await chip.evaluate(el=>{
      const r=el.getBoundingClientRect(), h=document.querySelector('.hero h1').getBoundingClientRect();
      return {width:r.width,height:r.height,right:r.right,inside:el.scrollWidth<=el.clientWidth+1,
              gap:h.top-r.bottom,overflow:document.documentElement.scrollWidth>innerWidth};
    });
    assert.ok(sizes.inside && sizes.height>=44 && sizes.right<=width && !sizes.overflow,JSON.stringify({viewport:width,...sizes}));
    assert.ok(sizes.gap>=15,JSON.stringify({viewport:width,...sizes}));
    if (state.selected) {
      assert.equal(await chip.getAttribute('data-news-status'),'current');
      assert.equal(await chip.locator('.news-title').textContent(),state.selected.title);
      assert.equal(await chip.locator('.news-source').textContent(),state.selected.publisher);
      assert.equal(await chip.getAttribute('href'),state.selected.url);
      assert.equal(await chip.getAttribute('target'),'_blank');
      assert.ok((await chip.getAttribute('rel')).includes('noopener'));
      await chip.focus();
      assert.equal(await chip.evaluate(el=>getComputedStyle(el).outlineStyle),'solid');
      const heroTop=await page.locator('.hero h1').evaluate(el=>el.getBoundingClientRect().top);
      await page.clock.fastForward(Date.parse(state.expires_at)-Date.parse(state.checked_at)+200);
      await assertEmpty(chip);
      assert.equal(await chip.evaluate(el=>document.activeElement===el),false);
      assert.ok(Math.abs(heroTop-await page.locator('.hero h1').evaluate(el=>el.getBoundingClientRect().top))<1,
                'retiring a headline must preserve the hero position');
      // Cached HTML loaded after expiry must retire the link before the reader can use it.
      await page.reload();
      await assertEmpty(page.locator('.news-chip'));
    } else {
      await assertEmpty(chip);
      assert.equal(await chip.evaluate(el=>el.tabIndex),-1);
    }
    assert.deepEqual(errors,[],'the production CSP must allow the retirement script');
    await page.close(); checked++;
  }
  console.log(`news headline: ${checked} generated/fixture layouts, attribution, focus, empty state and cached expiry passed`);
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
