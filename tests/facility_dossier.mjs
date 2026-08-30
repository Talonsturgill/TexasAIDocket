// facility_dossier: the researched dossiers, read the way a reader reads them.
//
// THE FIRST CHECK IS THE ONE THAT MATTERS MOST, same as the calendar. Every dossier is a real
// page at its own url. The dialog is a convenience layered on top, and if the fetch fails, the
// script is off, or the browser has no <dialog>, the anchor still navigates and the reader
// still gets the whole thing. Nothing here is reachable only through script.
//
// The expected link count is COMPUTED from the two ledgers rather than typed. The registry
// carries repeated names on purpose, a second row being a re-certification, so a hardcoded
// number was wrong the moment one facility held two rows. It did, immediately.
//
//     SITE=docs node tests/facility_dossier.mjs

import { chromium } from "playwright";
/* Some environments ship a chromium whose build number does not match the npm package's
   pinned one. Where a preinstalled binary exists, use it rather than downloading a second
   copy; where it does not, let playwright resolve its own. Hardcoding either breaks the
   other, and this test has to run both on a dev container and on a CI runner. */
import fs from "node:fs";
import path from "node:path";
import http from "node:http";
const PREINSTALLED = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const LAUNCH = fs.existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {};
const SITE = path.resolve(process.env.SITE || "docs");

let fails = 0;
const ok = (label, cond, extra = "") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) fails++;
};

// OVER HTTP, not file://. The record page links a second stylesheet and the month anchors are
// real urls; file:// resolves both differently and would test a page nobody is served.
const TYPES = { ".css": "text/css", ".png": "image/png", ".webp": "image/webp", ".svg": "image/svg+xml",
                ".woff2": "font/woff2", ".json": "application/json", ".xml": "application/xml" };
const server = http.createServer((rq, rs) => {
  let f = path.join(SITE, decodeURIComponent(rq.url.split("?")[0]));
  if (!f.startsWith(SITE)) { rs.writeHead(403).end(); return; }
  try { if (fs.statSync(f).isDirectory()) f = path.join(f, "index.html"); fs.statSync(f); }
  catch { rs.writeHead(404).end("no"); return; }
  rs.writeHead(200, { "content-type": TYPES[path.extname(f)] || "text/html" });
  fs.createReadStream(f).pipe(rs);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const ORIGIN = `http://127.0.0.1:${server.address().port}`;

const reg = JSON.parse(fs.readFileSync("ledger/gridwatch/datacenters.json", "utf8")).facilities;
const doss = JSON.parse(fs.readFileSync("ledger/facilities/dossiers.json", "utf8")).dossiers;
const have = new Set(doss.map((d) => d.name));
const EXPECT = reg.filter((r) => have.has(r.name)).length;

// WHERE THE ROSTER LIVES. The certified roster sat on /grid/ until the data centers tab took
// it, and this suite kept three copies of that path: the page it opens, the base it resolves
// hrefs against, and the phone block. The first would have gone red and the other two would
// have kept passing against a page with no roster on it, which is a suite disagreeing with
// itself. One name, used three times.
const ROSTER = "/datacenters/";

const browser = await chromium.launch(LAUNCH);

// ---------------------------------------------------------------- the page, with no script
{
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const p = await ctx.newPage();
  const r = await p.goto(`${ORIGIN}/facility/${doss[0].slug}/`, { waitUntil: "domcontentloaded" });
  ok("a dossier page serves with script disabled", r.status() === 200, String(r.status()));
  const n = await p.$$eval(".drow", (e) => e.length);
  ok("...and its facts are in the document", n > 0, `${n} rows`);
  const src = await p.$$eval(".dsources li", (e) => e.length);
  ok("...and so are its sources", src > 0, `${src} sources`);
  await ctx.close();
}

// ---------------------------------------------------------------- the roster links
{
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = [];
  p.on("pageerror", (e) => errs.push(String(e)));
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "domcontentloaded" });
  const n = await p.$$eval("a.dosslink", (a) => a.length);
  ok("every registry row with a dossier is a link", n === EXPECT, `${n} of ${EXPECT}`);

  // Every link resolves. A dossier whose page was never built is a 404 a reader finds first.
  const hrefs = await p.$$eval("a.dosslink", (a) => [...new Set(a.map((x) => x.getAttribute("href")))]);
  let dead = [];
  for (const h of hrefs) {
    const res = await p.request.get(new URL(h, `${ORIGIN}${ROSTER}`).href);
    if (!res.ok()) dead.push(h);
  }
  ok("every dossier link resolves", dead.length === 0, dead.join(", "));

  // SCROLLED TO AND WAITED FOR, rather than clicked where it happens to be. This timed out on
  // 2026-08-30 having passed on the run before it, with a diff that touched neither this page nor
  // this test. Playwright's click waits for the element to be visible, stable and hittable, and
  // the roster is a long page where the first dossier link can sit below the fold behind a header
  // that is still settling. Nothing is weakened: the assertion below is unchanged and it is still
  // the dialog's own content that has to appear.
  const _link = p.locator("a.dosslink").first();
  await _link.scrollIntoViewIfNeeded();
  await _link.click({ timeout: 15000 });
  const opened = await p
    .waitForFunction(() => {
      const d = document.getElementById("dossdlg");
      return d && d.open && d.querySelector(".drow");
    }, null, { timeout: 8000 })
    .then(() => true)
    .catch(() => false);
  ok("clicking a facility opens the dialog with its facts", opened);

  const seen = await p.evaluate(() => {
    const d = document.getElementById("dossdlg");
    return {
      facts: d.querySelectorAll(".drow").length,
      sources: d.querySelectorAll(".dsources li").length,
      gaps: d.querySelectorAll(".dgaps li").length,
      rungs: d.querySelectorAll(".drung").length,
      through: !!d.querySelector(".dossmore a"),
      styled: getComputedStyle(d).padding === "0px",
    };
  });
  ok("the dialog carries facts", seen.facts > 0, JSON.stringify(seen));
  ok("...and the sources behind them", seen.sources > 0, JSON.stringify(seen));
  ok("...and what is not public", seen.gaps > 0, JSON.stringify(seen));
  ok("...and a rung on every source", seen.rungs === seen.sources, JSON.stringify(seen));
  ok("...and a way through to the full page", seen.through, JSON.stringify(seen));
  ok("the second stylesheet reached the dialog", seen.styled, JSON.stringify(seen));

  await p.keyboard.press("Escape");
  ok("escape closes it", await p.evaluate(() => !document.getElementById("dossdlg").open));
  ok("no page errors", errs.length === 0, errs.slice(0, 2).join(" | "));
  await p.close();
}

// ---------------------------------------------------------------- the registry controls
{
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "domcontentloaded" });

  await p.fill("#rsearch", "a facility name that cannot exist");
  ok("a registry search can reach an empty result",
    await p.$$eval("#registry-roster tbody tr:not([hidden])", (rows) => rows.length) === 0);
  ok("...and explains the empty result", await p.locator("#rempty").isVisible());

  await p.click("#rclear");
  ok("clear restores the full registry",
    await p.$$eval("#registry-roster tbody tr:not([hidden])", (rows) => rows.length) === reg.length);

  if (EXPECT < reg.length) {
    await p.check("#rresearched");
    ok("the dossier filter keeps exactly the researched rows",
      await p.$$eval("#registry-roster tbody tr:not([hidden])", (rows) => rows.length) === EXPECT);
  } else {
    const coverage = await p.locator(".registryroster > .qnote").innerText();
    ok("complete dossier coverage is explained instead of presenting a no-op filter",
      await p.locator("#rresearched").count() === 0 &&
      coverage.includes(String(doss.length)) && coverage.includes(String(reg.length)), coverage);
  }

  const roleSpill = await p.$$eval(".registryroles .rrole", (roles) => roles.flatMap((role) => {
    const column = role.getBoundingClientRect();
    return [...role.querySelectorAll(".ops li")].map((row) => {
      const item = row.getBoundingClientRect();
      return { text: row.textContent.trim(), right: item.right, columnRight: column.right };
    }).filter((row) => row.right > row.columnRight + 1);
  }));
  ok("each registry role list stays inside its own column", roleSpill.length === 0,
    JSON.stringify(roleSpill.slice(0, 3)));
  await p.close();
}

// ---------------------------------------------------------------- the network is still a set of links
{
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  // This block measures rendered motion and label opacity, so the stylesheet is part of the
  // thing under test. A DOM-ready page can still be waiting on that file in a slow workspace.
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "load" });
  const node = p.locator(".gnode").first();
  const point = node.locator(".ghit");
  // The atlas hero now earns the first screen, so the relationship field begins below it.
  // A bounding box does not scroll a locator into view. Move the same point a reader is about
  // to use onto the screen before measuring or the mouse would be aimed outside the viewport.
  await node.scrollIntoViewIfNeeded();
  const key = await node.getAttribute("data-k");
  const href = await node.getAttribute("href");
  // The link also contains a standing company label, so its full bounding box can be much
  // wider than the point a reader aims at. Exercise the point itself.
  const before = await point.boundingBox();
  const x = before.x + before.width / 2;
  const y = before.y + before.height / 2;
  await p.mouse.move(x, y);
  await p.waitForTimeout(900);
  const after = await point.boundingBox();
  const shift = Math.hypot(
    after.x + after.width / 2 - x,
    after.y + after.height / 2 - y,
  );
  const under = await p.evaluate(({ x, y }) => {
    const hit = document.elementFromPoint(x, y);
    return hit && hit.closest(".gnode")?.getAttribute("data-k");
  }, { x, y });
  ok("a network point holds still while the pointer is on it", shift < 3, `${shift.toFixed(1)}px`);
  ok("...so the same point remains under the pointer", under === key, `${under} instead of ${key}`);
  ok("the stable readout names the point",
    (await p.locator("#grname").textContent()).trim().length > 0 &&
    await p.locator("#grlink").getAttribute("href") === href);
  const visibleLabels = await p.$$eval(".glabel", (labels) => labels
    .filter((el) => Number.parseFloat(getComputedStyle(el).opacity) > 0.2)
    .map((el) => el.textContent.trim()));
  ok("a focused neighborhood keeps one readable company name",
    visibleLabels.length === 1 && visibleLabels[0].length > 0, visibleLabels.join(" | "));

  const destination = new URL(href, p.url()).href;
  const registry = p.url();
  const popupPromise = p.context().waitForEvent("page");
  await p.keyboard.down("Control");
  try {
    await p.mouse.click(x, y);
  } finally {
    await p.keyboard.up("Control");
  }
  const second = await popupPromise;
  /* A popup begins life as about:blank. `waitForLoadState` can therefore resolve against that
     first document while the destination navigation is still in flight; reading the URL or
     opener in that gap races the context teardown. Wait for the resolved company itself. */
  await second.waitForURL(destination, { waitUntil: "domcontentloaded" });
  ok("a modified point click opens the resolved company in a second page",
    second.url() === destination, second.url());
  ok("...and leaves the registry on its original page", p.url() === registry, p.url());
  ok("the second page cannot reach back through window.opener",
    await second.evaluate(() => window.opener === null));
  await second.close();

  // A line is evidence, not decoration. Keyboard focus has to reveal the exact certified rows
  // that caused the relationship, including routes to the dossiers already in this build.
  const graphData = await p.$eval("#gdata", (el) => JSON.parse(el.textContent));
  const firstEdge = graphData.edges[0];
  await p.locator('.gedgehit[data-i="0"]').focus();
  const edgeReadout = await p.evaluate(() => ({
    name: document.getElementById("grname").textContent,
    facilities: [...document.querySelectorAll("#grconnections .grfacilities li")]
      .map((li) => li.textContent.trim()),
    hrefs: [...document.querySelectorAll("#grconnections .grfacilities a")]
      .map((a) => a.getAttribute("href")),
  }));
  ok("a network line names both companies",
    edgeReadout.name.includes(graphData.nodes.find((n) => n.k === firstEdge.a).n) &&
    edgeReadout.name.includes(graphData.nodes.find((n) => n.k === firstEdge.b).n),
    edgeReadout.name);
  ok("...and reveals every certified row behind it",
    edgeReadout.facilities.length === firstEdge.f.length &&
    firstEdge.f.every((f) => edgeReadout.facilities.includes(f.n)),
    JSON.stringify(edgeReadout));
  ok("...with every researched row linked to its dossier",
    firstEdge.f.filter((f) => f.u).every((f) => edgeReadout.hrefs.includes(f.u)),
    JSON.stringify(edgeReadout.hrefs));

  const finalDestination = new URL(href, p.url()).href;
  await Promise.all([
    p.waitForURL(finalDestination),
    p.mouse.click(x, y),
  ]);
  ok("the point can be clicked without chasing it", p.url() === finalDestination, p.url());
  await p.close();
}

// ---------------------------------------------------------------- one resolver for pointer readout and navigation
// Every visible centre and every overlapping target sample uses the same nearest point for the
// readout and for the navigation request. Aborting the request keeps the field loaded so the
// test can exercise the entire drawing rather than proving one convenient point.
{
  // The nearest-point resolver now belongs only to the desktop spatial field. Phone readers
  // receive named relationship controls below, so geometry is exercised at the field's actual
  // desktop size rather than forcing the hidden canvas back into a narrow viewport for a test.
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  // The samples are geometry captured once and then walked. Freeze only this page's animation
  // clock so a later overlap is still the overlap the test measured at the start.
  await p.addInitScript(() => {
    window.requestAnimationFrame = () => 0;
    window.cancelAnimationFrame = () => {};
  });
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "load" });
  // The redesigned atlas has a real opening act above the graph. Bring the live field into the
  // viewport before sampling screen coordinates; otherwise every valid point is correctly below
  // the phone screen and the geometry test would be measuring the hero instead of the graph.
  await p.locator("#gfield").scrollIntoViewIfNeeded();
  const fieldScrollY = await p.evaluate(() => scrollY);
  await p.evaluate(() => {
    window.__companyActivations = [];
    window.__captureCompanyActivation = (event) => {
      window.__companyActivations.push(event.detail);
      event.preventDefault();
    };
    document.getElementById("gfield").addEventListener(
      "companyactivate", window.__captureCompanyActivation);
  });
  const samples = await p.evaluate(() => {
    const graph = JSON.parse(document.getElementById("gdata").textContent);
    const byKey = new Map(graph.nodes.map((node) => [node.k, node]));
    const rows = [...document.querySelectorAll(".gnode")].map((node) => {
      const key = node.getAttribute("data-k");
      const dot = node.querySelector(".gdot").getBoundingClientRect();
      const hit = node.querySelector(".ghit").getBoundingClientRect();
      return {
        key,
        name: byKey.get(key).n,
        href: new URL(node.getAttribute("href"), location.href).href,
        x: dot.x + dot.width / 2,
        y: dot.y + dot.height / 2,
        r: Math.min(hit.width, hit.height) / 2,
      };
    });
    const nearest = (x, y) => rows.reduce((best, row) => {
      const d = Math.hypot(row.x - x, row.y - y);
      if (d > row.r || (best && d > best.d)) return best;
      return { ...row, d };
    }, null);
    const field = document.getElementById("gfield").getBoundingClientRect();
    const visible = (x, y) => {
      const painted = document.elementFromPoint(x, y);
      return x >= Math.max(0, field.left) && y >= Math.max(0, field.top) &&
        x < Math.min(document.documentElement.clientWidth, field.right) &&
        y < Math.min(innerHeight, field.bottom) && !!painted?.closest("#gfield");
    };
    const centers = rows.filter((row) => visible(row.x, row.y)).map((row) => {
      const expected = nearest(row.x, row.y);
      return { x: row.x, y: row.y, key: expected.key, name: expected.name,
               href: expected.href, kind: "center" };
    });
    const overlaps = [];
    const seen = new Set();
    for (let i = 0; i < rows.length; i++) for (let j = i + 1; j < rows.length; j++) {
      const a = rows[i], b = rows[j];
      if (Math.hypot(a.x - b.x, a.y - b.y) >= a.r + b.r) continue;
      const x = (a.x + b.x) / 2, y = (a.y + b.y) / 2;
      if (!visible(x, y) || Math.hypot(a.x - x, a.y - y) > a.r ||
          Math.hypot(b.x - x, b.y - y) > b.r) continue;
      const expected = nearest(x, y);
      const id = `${Math.round(x)}:${Math.round(y)}:${expected.key}`;
      if (!seen.has(id)) {
        seen.add(id);
        overlaps.push({ x, y, key: expected.key, name: expected.name,
                        href: expected.href, kind: "overlap" });
      }
    }
    const lookup = Object.fromEntries(rows.map((row) => [row.key, {
      name: row.name, href: row.href,
    }]));
    return { centers, overlaps, lookup };
  });
  ok("every visible company dot has a centre sample", samples.centers.length > 0,
    String(samples.centers.length));
  ok("the desktop field contains overlapping target regions", samples.overlaps.length > 0,
    String(samples.overlaps.length));
  const disagreements = [];
  for (const sample of [...samples.centers, ...samples.overlaps]) {
    // A pointer click can focus a partly clipped SVG anchor and let the browser reveal it. Restore
    // the sampled field position so every subsequent screen coordinate still names the geometry
    // captured above; the production resolver itself remains responsible for the chosen node.
    await p.evaluate((y) => {
      document.documentElement.style.scrollBehavior = "auto";
      window.scrollTo(0, y);
    }, fieldScrollY);
    await p.mouse.move(sample.x, sample.y);
    const selected = await p.evaluate(() => ({
      name: document.getElementById("grname").textContent.trim(),
      href: new URL(document.getElementById("grlink").getAttribute("href"), location.href).href,
    }));
    const beforeActivation = await p.evaluate(() => window.__companyActivations.length);
    await p.mouse.click(sample.x, sample.y);
    const activation = await p.evaluate(() => ({
      count: window.__companyActivations.length,
      asked: window.__companyActivations.at(-1) || null,
    }));
    const asked = activation.asked;
    const resolved = asked && samples.lookup[asked.key];
    const askedHref = asked ? new URL(asked.href, p.url()).href : "";
    // A visible centre has one expected owner. An overlap has more than one valid target, so
    // its contract is that the field chooses once and gives that same choice to the readout and
    // activation path.
    const wrongCenter = sample.kind === "center" && asked?.key !== sample.key;
    if (activation.count !== beforeActivation + 1 || !asked || !resolved || wrongCenter ||
        selected.name !== resolved?.name || selected.href !== resolved?.href ||
        askedHref !== resolved?.href) {
      disagreements.push({ sample, selected, activation });
    }
  }
  ok("nearest point, readout and destination agree at every centre and overlap",
    disagreements.length === 0, JSON.stringify(disagreements.slice(0, 3)));

  await p.evaluate(() => document.getElementById("gfield").removeEventListener(
    "companyactivate", window.__captureCompanyActivation));
  const overlap = samples.overlaps[0];
  if (overlap) {
    await p.evaluate((y) => window.scrollTo(0, y), fieldScrollY);
    await p.mouse.move(overlap.x, overlap.y);
  }
  const middleSelection = await p.evaluate(() => ({
    name: document.getElementById("grname").textContent.trim(),
    href: new URL(document.getElementById("grlink").getAttribute("href"), location.href).href,
  }));
  if (overlap) {
    const registry = p.url();
    const backgroundPromise = p.context().waitForEvent("page");
    await p.mouse.click(overlap.x, overlap.y, { button: "middle" });
    const background = await backgroundPromise;
    await background.waitForURL(middleSelection.href, { waitUntil: "domcontentloaded" });
    ok("a middle click in an overlap opens the resolved company",
      background.url() === middleSelection.href,
      `${background.url()} instead of ${middleSelection.name} at ${middleSelection.href}`);
    ok("...and leaves the registry open", p.url() === registry, p.url());
    ok("the middle-click destination has no opener",
      await background.evaluate(() => window.opener === null));
    await background.close();
  }
  await p.close();
}

// ---------------------------------------------------------------- keyboard access to the company field
{
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "load" });
  const node = p.locator(".gnode").first();
  await node.focus();
  const focused = await p.evaluate(() => {
    const el = document.activeElement;
    const graph = JSON.parse(document.getElementById("gdata").textContent);
    const key = el?.getAttribute("data-k");
    const item = graph.nodes.find((n) => n.k === key);
    return {
      node: !!el?.matches(".gnode"),
      name: item?.n || "",
      readName: document.getElementById("grname")?.textContent.trim() || "",
      href: el?.getAttribute("href") || "",
      readHref: document.getElementById("grlink")?.getAttribute("href") || "",
    };
  });
  ok("a company point takes keyboard focus", focused.node, JSON.stringify(focused));
  ok("keyboard focus updates the stable readout",
    focused.name === focused.readName && focused.href === focused.readHref,
    JSON.stringify(focused));
  const destination = new URL(focused.href, p.url()).href;
  await Promise.all([p.waitForURL(destination), p.keyboard.press("Enter")]);
  ok("enter opens the focused company", p.url() === destination, p.url());
  await p.close();
}

// ---------------------------------------------------------------- the company field on a phone
{
  const p = await browser.newPage({ viewport: { width: 390, height: 780 },
                                    isMobile: true, hasTouch: true });
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "load" });
  await p.locator("#gmobile").scrollIntoViewIfNeeded();

  const phoneSurface = await p.evaluate(() => ({
    navigator: getComputedStyle(document.getElementById("gmobile")).display,
    desktopField: getComputedStyle(document.querySelector(".gworkspace")).display,
    pageWide: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    cards: [...document.querySelectorAll(".gmrelationship")].map((card) => ({
      names: [...card.querySelectorAll(".gmcompany")].map((name) => name.textContent.trim()),
      height: card.querySelector(".gmtrigger").getBoundingClientRect().height,
      edge: card.getAttribute("data-edge"),
    })),
  }));
  ok("the phone replaces the mystery-dot canvas with a named relationship navigator",
    phoneSurface.navigator !== "none" && phoneSurface.desktopField === "none" &&
    phoneSurface.cards.length >= 4 &&
    phoneSurface.cards.every((card) => card.names.length === 2 && card.names.every(Boolean)),
    JSON.stringify(phoneSurface));
  ok("the mobile relationship navigator needs no horizontal page or nested pan",
    phoneSurface.pageWide <= 0, JSON.stringify(phoneSurface));
  ok("every named relationship is a generous phone control",
    phoneSurface.cards.every((card) => card.height >= 63.5), JSON.stringify(phoneSurface.cards));

  const graph = await p.$eval("#gdata", (el) => JSON.parse(el.textContent));
  const first = graph.edges[0];
  await p.locator('.gmrelationship[data-edge="0"] .gmtrigger').click();
  const selected = await p.$eval('.gmrelationship[data-edge="0"]', (card) => ({
    expanded: card.classList.contains("selected") &&
      card.querySelector(".gmtrigger").getAttribute("aria-expanded") === "true",
    facilities: [...card.querySelectorAll(".gmevidence .grfacilities li")]
      .map((row) => row.textContent.trim()),
    hrefs: [...card.querySelectorAll(".gmevidence .grfacilities a")]
      .map((link) => link.getAttribute("href")),
    evidenceInside: card.contains(card.querySelector(".gmevidence")),
  }));
  ok("one phone tap expands the exact evidence inside the chosen relationship",
    selected.expanded && selected.evidenceInside &&
    selected.facilities.length === first.f.length &&
    first.f.every((facility) => selected.facilities.includes(facility.n)),
    JSON.stringify(selected));
  ok("every researched shared row remains a direct dossier route on a phone",
    first.f.filter((facility) => facility.u).every((facility) =>
      selected.hrefs.includes(facility.u)), JSON.stringify(selected.hrefs));

  await p.fill("#gsearch", "Amazon");
  const searched = await p.evaluate(() => ({
    status: document.getElementById("gmstatus").textContent.trim(),
    cards: [...document.querySelectorAll(".gmrelationship")].map((card) =>
      card.textContent.replace(/\s+/g, " ").trim()),
  }));
  ok("company search redraws the phone navigator around that named company",
    searched.status.includes("Amazon Data Services") && searched.cards.length > 0 &&
    searched.cards.every((card) => card.includes("Amazon Data Services")),
    JSON.stringify(searched));

  await p.selectOption("#grole", "owner");
  const ownerEdges = await p.$$eval(".gmrelationship", (cards) =>
    cards.map((card) => Number(card.getAttribute("data-edge"))));
  const byKey = Object.fromEntries(graph.nodes.map((node) => [node.k, node]));
  ok("role emphasis also filters the named phone relationships",
    ownerEdges.length > 0 && ownerEdges.every((index) => {
      const edge = graph.edges[index];
      return byKey[edge.a].o.owner && byKey[edge.b].o.owner;
    }), JSON.stringify(ownerEdges));
  await p.close();
}

// ---------------------------------------------------------------- the phone
{
  const p = await browser.newPage({ viewport: { width: 390, height: 780 }, isMobile: true, hasTouch: true });
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "domcontentloaded" });
  const atlasFit = await p.evaluate(() => {
    const mobile = document.getElementById("gmobile").getBoundingClientRect();
    const search = document.getElementById("gsearch").getBoundingClientRect();
    const role = document.getElementById("grole").getBoundingClientRect();
    const tiles = [...document.querySelectorAll(".dctile")].map((el) => el.getBoundingClientRect());
    const plate = document.querySelector(".dcmobileplate").getBoundingClientRect();
    return {
      mobileHeight: mobile.height,
      plateHeight: plate.height,
      plateImage: getComputedStyle(document.querySelector(".dcmobileplate"), "::before")
        .backgroundImage,
      searchBottom: search.bottom,
      roleTop: role.top,
      tileLefts: tiles.map((r) => Math.round(r.left)),
      tileWidths: tiles.map((r) => Math.round(r.width)),
    };
  });
  ok("the mobile relationship navigator has a real rendered surface",
    atlasFit.mobileHeight > 200, JSON.stringify(atlasFit));
  ok("the atlas art gets a distinct visible phone composition",
    atlasFit.plateHeight >= 220 && atlasFit.plateImage.includes("datacenter-atlas-relief"),
    JSON.stringify(atlasFit));
  ok("the graph controls stack instead of shrinking side by side",
    atlasFit.roleTop >= atlasFit.searchBottom - 1, JSON.stringify(atlasFit));
  ok("the four atlas figures form a compact two by two phone summary",
    new Set(atlasFit.tileLefts).size === 2 && new Set(atlasFit.tileWidths).size === 1,
    JSON.stringify(atlasFit));
  const rosterFit = await p.evaluate(() => {
    const wrap = document.querySelector(".rtwrap");
    const row = document.querySelector(".rtable tbody tr");
    return {
      overflow: getComputedStyle(wrap).overflow,
      height: getComputedStyle(wrap).maxHeight,
      row: getComputedStyle(row).display,
      wide: wrap.scrollWidth - wrap.clientWidth,
    };
  });
  ok("the phone roster uses cards with no nested scroll",
    rosterFit.overflow === "visible" && rosterFit.height === "none" &&
    rosterFit.row === "block" && rosterFit.wide <= 0, JSON.stringify(rosterFit));
  await p.click("a.dosslink");
  await p.waitForFunction(() => document.getElementById("dossdlg")?.open, null, { timeout: 8000 }).catch(() => {});
  const m = await p.evaluate(() => {
    const d = document.getElementById("dossdlg");
    const r = d.getBoundingClientRect();
    return {
      w: Math.round(r.width), vw: innerWidth,
      over: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      cols: getComputedStyle(document.querySelector(".drow")).gridTemplateColumns,
    };
  });
  ok("the dialog takes the phone screen", m.w <= m.vw + 1 && m.w > m.vw - 40, JSON.stringify(m));
  ok("nothing scrolls sideways behind it", m.over <= 0, JSON.stringify(m));
  ok("a fact stacks to one column", !m.cols.trim().includes(" "), JSON.stringify(m));
  await p.close();
}

await browser.close();
server.close();
console.log(fails ? `\nfacility_dossier: ${fails} FAILED` : "\nfacility_dossier: all passed");
process.exit(fails ? 1 : 0);
