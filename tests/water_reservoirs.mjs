/* water_reservoirs.mjs — the water map is an interaction, not a picture of one.
 *
 * The map's data and geometry are checked in Python. This drives the browser-only promises:
 * every visible vessel is a real link, its centre stays under the pointer as it magnifies,
 * the water moves inside it, keyboard and touch routes land on the same detail record, and
 * the detail page renders the exact daily series that the open water record carries.
 *
 *     SITE=docs node tests/water_reservoirs.mjs
 */
import { chromium } from "playwright";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";

const SITE = path.resolve(process.env.SITE || "docs");
const PREINSTALLED = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const LAUNCH = fs.existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {};
let failures = 0;
const ok = (label, cond, extra = "") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) failures++;
};

const TYPES = { ".css":"text/css", ".js":"text/javascript", ".json":"application/json",
  ".svg":"image/svg+xml", ".woff2":"font/woff2", ".png":"image/png", ".webp":"image/webp",
  ".xml":"application/xml", ".txt":"text/plain" };
const server = http.createServer((request, response) => {
  const pathname = decodeURIComponent(request.url.split("?")[0]);
  let file = path.resolve(SITE, "." + pathname);
  if (!file.startsWith(SITE + path.sep) && file !== SITE) {
    response.writeHead(403).end(); return;
  }
  try {
    if (fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
    fs.statSync(file);
  } catch {
    response.writeHead(404).end("no"); return;
  }
  response.writeHead(200, {"content-type": TYPES[path.extname(file)] || "text/html"});
  fs.createReadStream(file).pipe(response);
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const ORIGIN = `http://127.0.0.1:${server.address().port}`;

const feed = JSON.parse(fs.readFileSync(path.join(SITE, "waterwatch.json"), "utf8"));
const live = feed.readings.filter((row) => row.verified && row.reservoirs);
const latest = live.at(-1);
const atlas = JSON.parse(fs.readFileSync("assets/geo/tx-reservoirs.json", "utf8")).reservoirs;
const slug = (key) => key.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const expected = Object.entries(latest.reservoirs)
  .filter(([key, row]) => atlas[key]?.texas && row && row.capacity_af)
  .map(([key, row]) => ({key, row, route:`/water/reservoir/${slug(key)}/`}));

const browser = await chromium.launch(LAUNCH);
const errors = [];
const page = await browser.newPage({viewport:{width:1280,height:920}});
page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
page.on("pageerror", (error) => errors.push(error.message));

console.log("=== the map ===");
await page.goto(`${ORIGIN}/water/`, {waitUntil:"load"});
const links = page.locator("svg.resmap a.reslink");
const restingPanel = await page.evaluate(() => ({
  picker:document.getElementById("reservoir-picker").value,
  hidden:document.getElementById("reservoir-open").hidden,
  display:getComputedStyle(document.getElementById("reservoir-open")).display,
  href:document.getElementById("reservoir-open").getAttribute("href"),
}));
ok("the empty readout offers no dead link",
  restingPanel.picker === "" && restingPanel.hidden && restingPanel.display === "none"
    && restingPanel.href === null,
  JSON.stringify(restingPanel));
ok("one detail link exists for every mapped reservoir",
  await links.count() === expected.length, `${await links.count()} vs ${expected.length}`);
const hrefs = await links.evaluateAll((nodes) => nodes.map((node) => node.getAttribute("href")));
ok("every map route is unique", new Set(hrefs).size === hrefs.length, String(hrefs.length));
const missing = expected.filter(({route}) =>
  !fs.existsSync(path.join(SITE, route, "index.html")));
ok("every map route was generated", missing.length === 0,
  missing.slice(0, 4).map((x) => x.route).join(", "));

const target = page.locator('svg.resmap a.reslink[href="reservoir/amistad/"]');
await target.evaluate((node) => node.scrollIntoView(
  {block:"center", inline:"center", behavior:"instant"}));
await page.waitForTimeout(360);
await page.mouse.move(2, 2);
// A new page inherits the browser process's pointer coordinate. If that coordinate happens to
// land on this marker, moving away begins the same transition this check is about. Let that
// transition finish before measuring the resting size.
await page.waitForTimeout(360);
const vessel = target.locator(".res");
const vesselState = () => vessel.evaluate((node) => {
  const hit = node.querySelector(".hit");
  const point = new DOMPoint(Number(hit.getAttribute("cx")), Number(hit.getAttribute("cy")))
    .matrixTransform(hit.getScreenCTM());
  const transform = getComputedStyle(node).transform;
  const matrix = transform === "none" ? new DOMMatrix() : new DOMMatrix(transform);
  return {clientX:point.x,clientY:point.y,x:point.x + scrollX,y:point.y + scrollY,
    scale:Math.hypot(matrix.a, matrix.b),hover:node.parentElement.matches(":hover")};
});
const before = await vesselState();
await page.mouse.move(before.clientX, before.clientY);
await page.waitForFunction(() => {
  const node = document.querySelector('svg.resmap a.reslink[href="reservoir/amistad/"] .res');
  const value = getComputedStyle(node).transform;
  if (value === "none") return false;
  const matrix = new DOMMatrix(value);
  return Math.hypot(matrix.a, matrix.b) > 1.4;
}, null, {timeout:2500}).catch(() => {});
const after = await vesselState();
ok("hover magnifies the vessel without moving it off the pointer",
  !before.hover && after.hover && after.scale > 1.4
    && Math.hypot(before.x - after.x, before.y - after.y) < 1.1,
  JSON.stringify({before, after}));
const hoverState = await target.evaluate((link) => {
  const flow = link.querySelector(".flow");
  const at = document.elementFromPoint(
    link.getBoundingClientRect().left + link.getBoundingClientRect().width / 2,
    link.getBoundingClientRect().top + link.getBoundingClientRect().height / 2);
  return {name:document.getElementById("reservoir-name").textContent.trim(),
    open:document.getElementById("reservoir-open").getAttribute("href"),
    flowAnimation:getComputedStyle(flow).animationName,
    flowOpacity:Number(getComputedStyle(flow).opacity),
    waterFill:getComputedStyle(link.querySelector(".wf")).fill,
    hit:at?.closest("a.reslink") === link};
});
ok("hover reads the exact reservoir into the stable panel",
  /Amistad/.test(hoverState.name) && hoverState.open === "reservoir/amistad/",
  JSON.stringify(hoverState));
ok("the whoosh is running inside gradient-lit water",
  hoverState.flowAnimation === "wwhoosh" && hoverState.flowOpacity > .5
    && /reservoir-water/.test(hoverState.waterFill), JSON.stringify(hoverState));
ok("the enlarged vessel remains the pointer's hit target", hoverState.hit);

const keyboard = page.locator('svg.resmap a.reslink[href="reservoir/travis/"]');
await keyboard.focus();
ok("keyboard focus drives the same readout",
  /Travis/.test(await page.locator("#reservoir-name").textContent()));
await Promise.all([page.waitForURL("**/water/reservoir/travis/"), page.keyboard.press("Enter")]);

console.log("=== one reservoir ===");
const travisRows = live.flatMap((day) => {
  const row = day.reservoirs.Travis;
  return row && row.capacity_af ? [{...row, date:day.date}] : [];
});
const travisLatest = travisRows.at(-1);
ok("the map's keyboard link lands on the named record",
  /Lake Travis/.test(await page.locator("h1").textContent()), await page.title());
ok("the detail page prints its latest computed storage",
  (await page.locator("main").innerText()).includes(Math.round(travisLatest.storage_af).toLocaleString("en-US")));
ok("the detail trend and table contain the whole verified series",
  await page.locator("svg.reservoir-trend circle.point").count() === travisRows.length
    && await page.locator("table.reservoir-table tbody tr").count() === travisRows.length,
  `${await page.locator("svg.reservoir-trend circle.point").count()} points and `
    + `${await page.locator("table.reservoir-table tbody tr").count()} rows for ${travisRows.length}`);

const orbCard = page.locator(".reservoir-orb-card");
await orbCard.scrollIntoViewIfNeeded();
// The pointer can land at the same screen coordinate after the map navigation. Move it clear
// first so the next movement is a real event rather than a no-op at an unchanged coordinate.
await page.mouse.move(2, 2);
await page.waitForTimeout(50);
const orbBox = await orbCard.boundingBox();
const atRest = await page.locator(".reservoir-orb-wrap")
  .evaluate((node) => getComputedStyle(node).transform);
await page.mouse.move(orbBox.x + orbBox.width * .82, orbBox.y + orbBox.height * .2, {steps:4});
await page.waitForFunction((rest) => {
  const card = document.querySelector(".reservoir-orb-card");
  const orb = document.querySelector(".reservoir-orb-wrap");
  return card?.dataset.tiltX === "right" && card?.dataset.tiltY === "top"
    && getComputedStyle(orb).transform !== rest;
}, atRest);
const awakeState = await page.locator(".reservoir-orb-wrap").evaluate((node) => ({
  computed:getComputedStyle(node).transform,
  tiltX:node.parentElement.dataset.tiltX, tiltY:node.parentElement.dataset.tiltY,
}));
const detailFlow = await page.locator(".reservoir-orb .flow").first()
  .evaluate((node) => getComputedStyle(node).animationName);
ok("the dimensional gauge follows the pointer", awakeState.computed !== atRest
  && awakeState.tiltX === "right" && awakeState.tiltY === "top",
  `${atRest} -> ${JSON.stringify(awakeState)}`);
ok("its internal current moves on interaction", detailFlow === "detailwhoosh", detailFlow);
await page.goBack({waitUntil:"load"});
const restored = await page.evaluate(() => ({
  picker:document.getElementById("reservoir-picker")?.value,
  name:document.getElementById("reservoir-name")?.textContent.trim(),
  open:document.getElementById("reservoir-open")?.getAttribute("href"),
}));
ok("back navigation restores one coherent map selection",
  restored.picker === "reservoir/travis/" && /Travis/.test(restored.name)
    && restored.open === "reservoir/travis/", JSON.stringify(restored));

console.log("=== click and touch routes ===");
const clickPage = await browser.newPage({viewport:{width:1100,height:850}});
await clickPage.goto(`${ORIGIN}/water/`);
await Promise.all([
  clickPage.waitForURL("**/water/reservoir/amistad/"),
  clickPage.locator('svg.resmap a.reslink[href="reservoir/amistad/"]').click(),
]);
ok("a direct click opens the reservoir page", clickPage.url().endsWith("/water/reservoir/amistad/"),
  clickPage.url());
await clickPage.close();

const phone = await browser.newPage({viewport:{width:390,height:844},hasTouch:true,isMobile:true});
await phone.goto(`${ORIGIN}/water/`);
await Promise.all([
  phone.waitForURL("**/water/reservoir/canyon/"),
  phone.locator("#reservoir-picker").selectOption("reservoir/canyon/"),
]);
const phoneFit = await phone.evaluate(() =>
  document.documentElement.scrollWidth - document.documentElement.clientWidth);
ok("the touch finder opens the same detail record", phone.url().endsWith("/water/reservoir/canyon/"));
ok("the reservoir page does not spill off a phone", phoneFit <= 1, String(phoneFit));
await phone.close();

console.log("=== reduced motion ===");
const stillContext = await browser.newContext({viewport:{width:900,height:800},reducedMotion:"reduce"});
const still = await stillContext.newPage();
await still.goto(`${ORIGIN}/water/reservoir/travis/`);
const stillCard = still.locator(".reservoir-orb-card");
const stillBox = await stillCard.boundingBox();
await still.mouse.move(stillBox.x + stillBox.width * .8, stillBox.y + stillBox.height * .2);
await stillCard.hover();
const stillState = await still.evaluate(() => ({
  transform:getComputedStyle(document.querySelector(".reservoir-orb-wrap")).transform,
  animation:getComputedStyle(document.querySelector(".reservoir-orb .flow")).animationName,
}));
ok("reduced motion keeps the gauge still",
  stillState.transform === "none" && stillState.animation === "none", JSON.stringify(stillState));
await stillContext.close();

ok("the interaction throws no browser error", errors.length === 0, errors.slice(0, 4).join(" | "));
await page.close();
await browser.close();
await new Promise((resolve) => server.close(resolve));
if (failures) {
  console.error(`\nwater_reservoirs: ${failures} FAILED`);
  throw new Error(`${failures} reservoir interaction check(s) failed`);
}
console.log("\nwater_reservoirs: all passed");
