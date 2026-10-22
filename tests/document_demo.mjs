// Drive real state transitions over HTTP. External forms and services are never submitted.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { chromium } from 'playwright';

const SITE = path.resolve(process.env.SITE || 'docs');
const SCREENSHOTS = process.env.DEMO_SCREENSHOTS;
const types = {'.js':'text/javascript', '.css':'text/css', '.woff2':'font/woff2', '.json':'application/json', '.svg':'image/svg+xml', '.png':'image/png', '.avif':'image/avif', '.webp':'image/webp'};
const server = http.createServer((req, res) => {
  const name = decodeURIComponent(new URL(req.url, 'http://local').pathname);
  let file = path.resolve(SITE, '.' + name);
  if (file !== SITE && !file.startsWith(SITE + path.sep)) { res.writeHead(403).end(); return; }
  try { if (fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    const body = fs.readFileSync(file); res.writeHead(200, {'content-type':types[path.extname(file)] || 'text/html; charset=utf-8'}).end(body);
  } catch { res.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const binary = process.env.PLAYWRIGHT_CHROMIUM || '/opt/pw-browsers/chromium';
const browser = await chromium.launch(fs.existsSync(binary) ? {executablePath:binary} : {});
let assertions = 0;
const check = (label, condition) => { assert.ok(condition, label); assertions++; console.log(`ok ${label}`); };
const anchorEvidence = [];
// Visibility alone passes when the sticky masthead covers the first labels. Measure the
// settled native fragment landing, including real fonts and the section's reveal transition.
async function checkServicesAnchor(page, label) {
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => {
    const start = document.querySelector('#start');
    return location.hash === '#start' && scrollY > 0 && getComputedStyle(start).opacity === '1';
  });
  // Poll from the test process so settling also works with page scripts disabled.
  let previous, stable = 0;
  for (let sample = 0; sample < 50 && stable < 3; sample++) {
    await new Promise(resolve => setTimeout(resolve,100));
    const top = await page.locator('#start').evaluate(el => el.getBoundingClientRect().top);
    stable = previous !== undefined && Math.abs(top - previous) < 0.1 ? stable + 1 : 0;
    previous = top;
  }
  assert.ok(stable >= 3,`${label} fragment scroll settles`);
  const geometry = await page.evaluate(() => {
    const header = document.querySelector('.masthead');
    const rect = selector => {
      const r = document.querySelector(selector).getBoundingClientRect();
      return {top:r.top, bottom:r.bottom};
    };
    return {header:rect('.masthead'), sticky:getComputedStyle(header).position === 'sticky',
      start:rect('#start'), heading:rect('#start h2'), nameLabel:rect('label[for="lf-name"]'),
      nameInput:rect('#lf-name'), companyLabel:rect('label[for="lf-co"]'),
      viewport:{width:innerWidth,height:innerHeight}, scrollY};
  });
  anchorEvidence.push({label, ...geometry});
  if (SCREENSHOTS) {
    fs.mkdirSync(SCREENSHOTS,{recursive:true});
    await page.screenshot({path:path.join(SCREENSHOTS,label+'.png')});
    fs.writeFileSync(path.join(SCREENSHOTS,'services-anchor.json'),JSON.stringify(anchorEvidence,null,2)+'\n');
  }
  const edge = geometry.sticky ? geometry.header.bottom : 0;
  check(`${label} enquiry heading clears the navigation`, geometry.heading.top >= edge && geometry.heading.bottom <= geometry.viewport.height);
  if (geometry.viewport.width >= 896) {
    check(`${label} first labels and input clear the navigation`,
      geometry.nameLabel.top >= edge && geometry.companyLabel.top >= edge &&
      geometry.nameInput.top >= edge && geometry.nameInput.bottom <= geometry.viewport.height);
  }
}
try {
  for (const mode of [
    {name:'desktop-dark', width:1440, height:1000, colorScheme:'dark'},
    {name:'mobile-light-preference', width:390, height:844, colorScheme:'light', isMobile:true, hasTouch:true},
  ]) {
    const context = await browser.newContext({viewport:{width:mode.width,height:mode.height},colorScheme:mode.colorScheme,
      isMobile:mode.isMobile,hasTouch:mode.hasTouch,reducedMotion:'reduce'});
    const page = await context.newPage();
    const errors = [], external = [], csp = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => { if (!request.url().startsWith(origin) && !request.url().startsWith('data:')) external.push(request.url()); });
    await context.route('**/*', route => route.request().url().startsWith(origin) ? route.continue() : route.abort());
    await page.addInitScript(() => { window.demoCsp=[]; document.addEventListener('securitypolicyviolation', event => window.demoCsp.push(event.violatedDirective)); });
    await page.goto(origin + '/services/document-demo/');
    await page.waitForFunction(() => document.querySelector('#di-count').textContent.includes('5 of 5'));
    const count = () => page.locator('[data-entry]:visible').count();
    check(`${mode.name} starts with every source`, await count() === 5);
    check(`${mode.name} reduced-motion hero actions are immediately visible`, await page.locator('.di-hero .ctarow').evaluate(el => getComputedStyle(el).opacity === '1'));
    check(`${mode.name} source dates retain their year`, (await page.locator('.di-provenance').textContent()).includes('August 14th, 2026'));
    check(`${mode.name} has no horizontal overflow`, await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    const links = await page.locator('[data-source-link]').evaluateAll(nodes => nodes.map(n => n.href));
    check(`${mode.name} links exact official PDF pages`, links.every(u => u.startsWith('https://www.tceq.texas.gov/downloads/permitting/stormwater/general/multi-sector/2026-msgp-renewal.pdf#page=')) && links.map(u => u.split('=')[1]).join(',') === '48,49,65,65,69');
    await page.getByRole('button', {name:'Supporting records', exact:true}).click();
    check(`${mode.name} supporting-records example`, await count() === 1 && await page.locator('[data-entry="supporting-records"]').isVisible());
    await page.getByRole('button', {name:'Plan revisions', exact:true}).click();
    check(`${mode.name} plan-revision example`, await count() === 1 && await page.locator('[data-entry="plan-versions"]').isVisible());
    await page.getByRole('button', {name:'Clear filters', exact:true}).click();
    await page.fill('#di-query', 'MONITORING');
    await page.selectOption('#di-category', 'Record details');
    check(`${mode.name} keyword and topic intersect`, await count() === 1 && await page.locator('[data-entry="record-details"]').isVisible());
    await page.selectOption('#di-status', 'needs-review');
    await page.locator('#review-record-details').focus();
    await page.selectOption('#review-record-details', 'reviewed');
    check(`${mode.name} status filter follows changed state`, await count() === 0);
    check(`${mode.name} keyboard focus is preserved`, await page.evaluate(() => document.activeElement.id === 'di-status'));
    await page.selectOption('#di-status', 'reviewed');
    check(`${mode.name} reviewed filter finds passage`, await count() === 1);
    await page.selectOption('#review-record-details', 'question');
    await page.selectOption('#di-status', 'question');
    check(`${mode.name} question queue finds passage`, await count() === 1);
    check(`${mode.name} global review counts update`, (await page.locator('#di-review-count').textContent()).includes('1 with a question'));
    await page.getByRole('button', {name:'Reset review', exact:true}).click();
    check(`${mode.name} reset clears status filter and state`, await count() === 1 && await page.locator('#di-status').inputValue() === '' && await page.locator('#review-record-details').inputValue() === 'needs-review');
    await page.fill('#di-query', '<script>unknown facility</script>');
    check(`${mode.name} no match is honest`, await count() === 0 && await page.locator('#di-empty').isVisible());
    await page.getByRole('button', {name:'Clear filters', exact:true}).click();
    await page.getByRole('button', {name:'Clear filters', exact:true}).click();
    check(`${mode.name} repeated clear is stable`, await count() === 5);
    await page.selectOption('#review-supporting-records', 'question');
    await page.reload();
    check(`${mode.name} reload starts a clean review`, await page.locator('#review-supporting-records').inputValue() === 'needs-review');
    check(`${mode.name} no browser storage is written`, await page.evaluate(() => sessionStorage.length === 0 && localStorage.length === 0));
    await page.getByRole('link', {name:'Discuss one workflow',exact:true}).click();
    check(`${mode.name} CTA reaches Services enquiry`, page.url().endsWith('/services/#start') && await page.locator('#servicesform').isVisible());
    await checkServicesAnchor(page,mode.name+'-cross-page');
    check(`${mode.name} existing contact fields remain`, await page.locator('#servicesform input[name="email"]').count() === 1 && await page.locator('#servicesform textarea[name="message"]').count() === 1);
    await page.goBack();
    check(`${mode.name} back returns to working demo`, await page.locator('#di-query').isVisible());
    await page.evaluate(() => window.scrollTo(0, 0));
    if (SCREENSHOTS) {
      fs.mkdirSync(SCREENSHOTS,{recursive:true});
      await page.screenshot({path:path.join(SCREENSHOTS,mode.name+'.png'),fullPage:true});
      await page.screenshot({path:path.join(SCREENSHOTS,mode.name+'-top.png')});
      await page.locator('#di-query').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(SCREENSHOTS,mode.name+'-index.png')});
      await page.getByRole('button', {name:'Supporting records',exact:true}).click();
      await page.locator('[data-entry="supporting-records"] summary').click();
      await page.locator('[data-entry="supporting-records"]').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(SCREENSHOTS,mode.name+'-source.png')});
    }
    csp.push(...await page.evaluate(() => window.demoCsp));
    check(`${mode.name} demo has no CSP violations`, csp.length === 0);
    check(`${mode.name} demo has no page errors`, errors.length === 0);
    check(`${mode.name} no external requests or form submissions`, external.length === 0);
    await context.close();
  }
  const context = await browser.newContext({javaScriptEnabled:false});
  const page = await context.newPage();
  await page.goto(origin + '/services/document-demo/');
  check('no-script sample remains readable', await page.locator('[data-entry]:visible').count() === 5);
  check('no-script source links remain available', await page.locator('[data-source-link]').count() === 5);
  check('no-script controls are not misleading', !await page.locator('#di-query').isVisible());
  await context.close();
  for (const mode of [
    {name:'reported-desktop',width:1180,height:757,reducedMotion:'no-preference'},
    {name:'wrapped-desktop',width:897,height:757,reducedMotion:'reduce'},
    {name:'tablet',width:768,height:1024,reducedMotion:'reduce',isMobile:true,hasTouch:true},
    {name:'small-phone',width:320,height:700,reducedMotion:'reduce',isMobile:true,hasTouch:true},
    {name:'no-script-desktop',width:1180,height:757,javaScriptEnabled:false,reducedMotion:'reduce'},
  ]) {
    const {name, width, height, ...options} = mode;
    const context = await browser.newContext({...options,viewport:{width,height}});
    const page = await context.newPage();
    const external = [], errors = [];
    page.on('pageerror',error => errors.push(error.message));
    page.on('console',message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('response',response => { if (response.status() >= 400) errors.push(response.url()); });
    await context.route('**/*',route => {
      if (route.request().url().startsWith(origin)) return route.continue();
      external.push(route.request().url());
      return route.abort();
    });
    await page.goto(origin+'/services/#start');
    await checkServicesAnchor(page,mode.name+'-direct');
    await page.goto(origin+'/services/');
    const cta = page.getByRole('link',{name:'Discuss one workflow',exact:true}).first();
    await cta.click();
    await checkServicesAnchor(page,mode.name+'-same-page');
    // Repeat the same hash after the reader has moved away, then activate it with Enter.
    await cta.focus();
    await page.keyboard.press('Enter');
    await checkServicesAnchor(page,mode.name+'-repeat-keyboard');
    for (let tab = 0; tab < 6 && await page.locator('#lf-name').evaluate(el => el !== document.activeElement); tab++) {
      await page.keyboard.press('Tab');
    }
    check(`${mode.name} keyboard reaches the name field`,await page.locator('#lf-name').evaluate(el => el === document.activeElement));
    const field = await page.locator('#lf-name').boundingBox();
    const label = await page.locator('label[for="lf-name"]').boundingBox();
    const edge = await page.locator('.masthead').evaluate(el => getComputedStyle(el).position === 'sticky' ? el.getBoundingClientRect().bottom : 0);
    check(`${mode.name} focused name field and label stay readable`,label.y >= edge && field.y + field.height <= mode.height);
    if (name === 'reported-desktop') {
      for (const resizedWidth of [897,390,1180]) {
        await page.setViewportSize({width:resizedWidth,height});
        await cta.focus();
        await page.keyboard.press('Enter');
        await checkServicesAnchor(page,`${name}-resized-${resizedWidth}`);
      }
    }
    await page.goto(origin+'/services/document-demo/');
    await page.getByRole('link',{name:'Discuss one workflow',exact:true}).click();
    await checkServicesAnchor(page,mode.name+'-cross-page');
    await page.goBack();
    await page.goForward();
    await checkServicesAnchor(page,mode.name+'-history');
    check(`${mode.name} anchor navigation has no page errors ${JSON.stringify(errors)}`,errors.length === 0);
    check(`${mode.name} anchor navigation makes no external requests`,external.length === 0);
    await context.close();
  }
  console.log(`document_demo: ${assertions} assertions passed`);
} finally { await browser.close(); await new Promise(resolve => server.close(resolve)); }
