// Speech events are simulated; the generated pages, editing, submission, CSS and CSP are real.
// This cannot certify microphone hardware or a browser vendor's remote recognition service.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { chromium } from 'playwright';

const site = path.resolve(process.env.SITE || 'docs');
const mime = { '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.woff2': 'font/woff2', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  let file = path.join(site, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(site + path.sep)) { res.writeHead(403).end(); return; }
  try {
    if (fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    res.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'text/html; charset=utf-8' });
    fs.createReadStream(file).pipe(res);
  } catch { res.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const executable = process.env.PLAYWRIGHT_CHROMIUM || '/opt/pw-browsers/chromium';
const browser = await chromium.launch(fs.existsSync(executable) ? { executablePath: executable } : {});
let checks = 0;
function check(label, condition) { assert.ok(condition, label); checks++; }
const mic = id => `.voice-input-button[aria-controls="${id}"]`;

async function pageFor(route = '/', width = 1280, support = 'standard') {
  const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
  await page.route('**/*', async route => {
    if (route.request().url().startsWith(origin)) return route.continue();
    return route.abort(); // Never send an enquiry, a scan, audio or an Ask request in this suite.
  });
  await page.addInitScript(mode => {
    window.speechSessions = [];
    window.submissions = [];
    window.policyErrors = [];
    document.addEventListener('securitypolicyviolation', e => window.policyErrors.push(e.violatedDirective));
    document.addEventListener('DOMContentLoaded', () => {
      document.querySelectorAll('form').forEach(form => form.addEventListener('submit', e => {
        window.submissions.push(e.target.querySelector('input,textarea')?.value);
        e.preventDefault();
        e.stopImmediatePropagation();
      }, true));
    });
    class FakeRecognition {
      constructor() { window.speechSessions.push(this); }
      start() { this.started = true; if (window.speechThrows) throw new Error('service unavailable'); if (!window.speechHold) this.onstart?.(); }
      stop() { this.stopped = true; } // Deliberately delayed, as real final results can arrive after stop().
      abort() { this.aborted = true; this.aborts = (this.aborts || 0) + 1; this.onend?.(); }
      result(parts) {
        this.onresult?.({ results: parts.map(([transcript, isFinal]) => Object.assign([{ transcript }], { isFinal })) });
      }
      error(error) { this.onerror?.({ error }); }
      end() { this.onend?.(); }
    }
    window.SpeechRecognition = mode === 'standard' ? FakeRecognition : undefined;
    window.webkitSpeechRecognition = mode === 'prefixed' ? FakeRecognition : undefined;
  }, support);
  await page.goto(origin + route);
  await page.locator(mic('contactmsg')).waitFor({ state: 'attached' });
  return page;
}
async function result(page, parts, index = -1) {
  await page.evaluate(({ parts, index }) => window.speechSessions.at(index).result(parts), { parts, index });
}

try {
  for (const route of ['/', '/record/']) {
    const page = await pageFor(route);
    check(`${route} starts without requesting speech`, await page.evaluate(() => speechSessions.length === 0));
    await page.fill('#askq', 'What is happening in Austin?');
    await page.evaluate(() => document.querySelector('#askq').setSelectionRange(21, 27));
    await page.click(mic('askq'));
    check('recording has an accessible stop action', await page.locator(mic('askq')).getAttribute('aria-pressed') === 'true');
    check('no visible tooltip copy was added', await page.locator(mic('askq')).getAttribute('title') === null);
    await result(page, [['Dal', false]]);
    await result(page, [['Dallas', true]]);
    check('interim replacement keeps surrounding text', await page.inputValue('#askq') === 'What is happening in Dallas?');
    check('speaking never submits', await page.evaluate(() => submissions.length === 0));
    await page.click(mic('askq'));
    check('second press stops the recognizer', await page.evaluate(() => speechSessions.at(-1).stopped));
    await result(page, [['Dallas County', true]]);
    await page.evaluate(() => speechSessions.at(-1).end());
    check('final result after stop is retained', await page.inputValue('#askq') === 'What is happening in Dallas County?');
    check('mic returns to idle', await page.locator(mic('askq')).getAttribute('aria-pressed') === 'false');
    await page.fill('#askq', 'What is happening in Travis County?');
    await page.click('#ask form button[type="submit"]');
    check('only explicit submission sends the edited query', await page.evaluate(() => submissions.length === 1 && submissions[0] === 'What is happening in Travis County?'));
    await page.click(mic('askq'));
    await page.locator('#askq').press('Enter');
    check('keyboard submission stops capture', await page.evaluate(() => speechSessions.at(-1).aborted && submissions.length === 2));
    check('no CSP violations', await page.evaluate(() => policyErrors.length === 0));
    await page.close();
  }

  const page = await pageFor();
  await page.click(mic('askq'));
  await result(page, [['Hello', true], ['Texas', false]]);
  await result(page, [['Hello', true], ['Texas Docket', true]]);
  check('multiple result segments do not repeat', await page.inputValue('#askq') === 'Hello Texas Docket');
  await page.fill('#askq', 'My correction');
  await result(page, [['late result', true]]);
  check('typing aborts and stale results cannot overwrite the correction', await page.inputValue('#askq') === 'My correction');
  check('manual edit stops recording', await page.evaluate(() => speechSessions.at(-1).aborted));

  for (const error of ['not-allowed', 'no-speech', 'network', 'audio-capture', 'service-not-allowed']) {
    await page.click(mic('askq'));
    await page.evaluate(error => speechSessions.at(-1).error(error), error);
    check(`${error} retains typed text`, await page.inputValue('#askq') === 'My correction');
    check(`${error} ends recording with an accessible reason`,
      await page.locator(mic('askq')).getAttribute('data-state') === 'error' &&
      (await page.locator(mic('askq')).getAttribute('aria-label')).length > 15);
    check(`${error} stays icon only`, await page.locator(mic('askq')).innerText() === '');
  }
  await page.evaluate(() => { window.speechThrows = true; });
  await page.click(mic('askq'));
  check('synchronous browser failure restores the button', await page.locator(mic('askq')).getAttribute('aria-pressed') === 'false');
  await page.evaluate(() => { window.speechThrows = false; });
  await page.click(mic('askq'));
  await page.keyboard.press('Escape');
  check('Escape stops capture', await page.evaluate(() => speechSessions.at(-1).aborted));
  await page.click(mic('askq'));
  await page.evaluate(() => speechSessions.at(-1).end());
  check('a silent end reports no speech', await page.locator(mic('askq')).getAttribute('data-state') === 'error');
  await page.click(mic('askq'));
  await page.evaluate(() => { document.querySelector('#askq').disabled = true; });
  check('disabling the field disables its microphone', await page.locator(mic('askq')).isDisabled());
  check('disabling the field stops capture', await page.evaluate(() => speechSessions.at(-1).aborted));
  await page.evaluate(() => { document.querySelector('#askq').disabled = false; });
  await page.click(mic('askq'));
  await page.keyboard.press('Tab');
  check('moving keyboard focus away stops capture', await page.evaluate(() => speechSessions.at(-1).aborted));
  await page.evaluate(() => { window.speechHold = true; });
  await page.click(mic('askq'));
  await page.keyboard.press('Escape');
  await page.evaluate(() => speechSessions.at(-1).onstart());
  check('a late permission callback cannot revive canceled capture', await page.evaluate(() => speechSessions.at(-1).aborts === 2));
  await page.evaluate(() => { window.speechHold = false; });

  await page.click('#askfbopen');
  await page.click(mic('askfbtext'));
  await result(page, [['Please check this source', true]]);
  await page.click(mic('askfbmail'));
  check('switching microphones ends the old session', await page.evaluate(() => speechSessions.at(-2).aborted));
  await result(page, [['stale feedback', true]], -2);
  check('old session cannot edit its field', await page.inputValue('#askfbtext') === 'Please check this source');
  await result(page, [['reader@example.test', true]]);
  check('email fields accept editable speech', await page.inputValue('#askfbmail') === 'reader@example.test');
  await page.keyboard.press('Escape');
  check('closing a dialog stops capture', await page.evaluate(() => speechSessions.at(-1).aborted));
  await page.close();

  const surfaces = {
    '/': ['askq', 'askfbtext', 'askfbmail', 'contactmsg', 'contactmail'],
    '/record/': ['askq', 'askfbtext', 'askfbmail', 'contactmsg', 'contactmail'],
    '/datacenters/': ['gsearch', 'rsearch', 'contactmsg', 'contactmail'],
    '/scan/': ['sc-mail', 'sc-note', 'contactmsg', 'contactmail'],
    '/services/': ['contactmsg', 'contactmail']
  };
  for (const [route, fields] of Object.entries(surfaces)) {
    const p = await pageFor(route, 390, 'prefixed');
    check(`${route} covers eligible text fields without extra microphones`,
      await p.locator('.voice-input-button').count() === fields.length);
    for (const id of fields) check(`${route} ${id} has exactly one control`, await p.locator(mic(id)).count() === 1);
    check(`${route} keeps buttons outside field labels`, await p.locator('label .voice-input-button').count() === 0);
    check(`${route} keeps link-pasting fields free of microphone controls`, await p.evaluate(() =>
      Array.from(document.querySelectorAll('input[inputmode="url"],input[autocomplete="url"],input[type="url"]'))
        .every(field => !document.querySelector('.voice-input-button[aria-controls="' + field.id + '"]'))));
    const target = fields[0];
    if (target === 'contactmsg') await p.click('#contactopen');
    await p.click(mic(target));
    await result(p, [['Texas', true]]);
    await p.evaluate(() => speechSessions.at(-1).end());
    check(`${route} supports Safari-style prefixed recognition`, await p.inputValue('#' + target) === 'Texas');
    check(`${route} does not submit dictated text`, await p.evaluate(() => submissions.length === 0));
    await p.close();
  }
  for (const width of [320, 360, 390, 430, 768, 1280]) {
    const p = await pageFor('/', width);
    for (const id of ['askq']) {
      const box = await p.locator(mic(id)).boundingBox();
      const send = await p.locator(`#${id}`).evaluate(el => {
        const r = el.form.querySelector('[type="submit"]').getBoundingClientRect();
        return { x: r.x, y: r.y, width: r.width, height: r.height };
      });
      check(`${width}px ${id} keeps a full touch target beside submit`, box.width >= 44 && box.height >= 44 && box.x + box.width <= send.x + 1);
      check(`${width}px ${id} stays within the phone width`, box.x >= 0 && send.x + send.width <= width);
    }
    await p.click('#askq');
    await p.click(mic('askq'));
    await result(p, [['What is the latest news about water and data centers in Travis County?', false]]);
    const box = await p.locator(mic('askq')).boundingBox();
    check(`${width}px active Ask keeps its mic visible`, box.x >= 0 && box.x + box.width <= width && box.y >= 0 && box.y + box.height <= 900);
    check(`${width}px has no page overflow`, await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await p.close();
  }
  const unsupported = await pageFor('/', 390, 'none');
  check('unsupported browser gives an honest disabled microphone', await unsupported.locator(mic('askq')).isDisabled());
  await unsupported.fill('#askq', 'Typing still works');
  check('unsupported browser keeps normal editing', await unsupported.inputValue('#askq') === 'Typing still works');
  await unsupported.close();
  console.log(`voice_input: ${checks} checks passed. Speech events simulated; no audio captured or forms sent.`);
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
