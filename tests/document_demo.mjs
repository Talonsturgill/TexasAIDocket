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
  console.log(`document_demo: ${assertions} assertions passed`);
} finally { await browser.close(); await new Promise(resolve => server.close(resolve)); }
