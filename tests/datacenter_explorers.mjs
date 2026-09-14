// Reader journeys for the company network and the certification explorer.
// Called by facility_dossier.mjs, so the existing browser gate covers both.
import crypto from "node:crypto";

const canonical = (value) => Array.isArray(value) ? value.map(canonical) :
  value && typeof value === "object" ? Object.fromEntries(Object.keys(value).sort().map(k => [k, canonical(value[k])])) : value;
const recordId = row => crypto.createHash("sha256").update(JSON.stringify(canonical(row))).digest("hex").slice(0, 16);
const normalise = name => name.toLowerCase().trim().replace(/[.,'\"]/g, " ").replace(/\s+/g, " ")
  .replace(/\b(llc|l\s?l\s?c|inc|incorporated|ltd|limited|lp|l\s?p|corporation|corp|company|co|holdings|us|usa)\b/g, " ")
  .replace(/\s+/g, " ").trim();
const qkey = key => `[data-key=${JSON.stringify(key)}]`;

export async function testExplorers({ browser, origin, route, registry, ok }) {
  const url = origin + route;
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  p.on("pageerror", error => errors.push(String(error)));
  await p.goto(url, { waitUntil: "load" });
  const graph = await p.$eval("#cedata", el => JSON.parse(el.textContent));
  const records = await p.$eval("#fxdata", el => JSON.parse(el.textContent));
  const source = Object.fromEntries(registry.map(row => [recordId(row), row]));
  const byKey = Object.fromEntries(graph.nodes.map(n => [n.key, n]));
  const sourceParties = row => ["owners", "occupants", "operators"].flatMap(role => row[role] || []);

  ok("every certification has a separate selectable record", records.length === registry.length &&
    new Set(records.map(r => r.id)).size === registry.length && records.every(r => source[r.id]));
  ok("every filed party survives with the spelling in that certification", records.every(r =>
    ["owner", "occupant", "operator"].every(role => JSON.stringify(r.r[role].map(party => party.n)) ===
      JSON.stringify(source[r.id][role + "s"] || []))));

  const expectedPairs = new Map();
  for (const [id, row] of Object.entries(source)) {
    const keys = [...new Set(sourceParties(row).map(normalise).filter(k => byKey[k]))].sort();
    for (let a = 0; a < keys.length; a++) for (let b = a + 1; b < keys.length; b++) {
      const pair = JSON.stringify([keys[a], keys[b]]);
      if (!expectedPairs.has(pair)) expectedPairs.set(pair, []);
      expectedPairs.get(pair).push(id);
    }
  }
  ok("every network line has both companies on the same original certification", graph.edges.every(edge =>
    edge.f.every(f => source[f.id] && [edge.a, edge.b].every(key => sourceParties(source[f.id]).map(normalise).includes(key)))));
  ok("the network neither loses nor invents a sourced company pair", graph.edges.length === expectedPairs.size &&
    graph.edges.every(e => JSON.stringify(e.f.map(r => r.id).sort()) ===
      JSON.stringify((expectedPairs.get(JSON.stringify([e.a, e.b])) || []).sort())));
  ok("line weights count facility names while preserving repeated certifications", graph.edges.every(edge =>
    edge.w === new Set(edge.f.map(f => source[f.id].name)).size));
  ok("every company point counts distinct facility names in the original registry", graph.nodes.every(node =>
    node.reach === new Set(registry.filter(row => sourceParties(row).map(normalise).includes(node.key)).map(row => row.name)).size));

  const hrefs = new Set(graph.nodes.map(n => n.u).concat(records.flatMap(r =>
    [r.u, ...Object.values(r.r).flat().map(party => party.u)]).filter(Boolean)));
  const dead = [];
  for (const href of hrefs) if (!(await p.request.get(new URL(href, url).href)).ok()) dead.push(href);
  ok("every company and facility route offered by either explorer serves", dead.length === 0, dead.join(", "));

  await p.fill("#gsearch", "no such company in this registry");
  ok("an empty network search explains its scope", await p.locator("#ceresults").textContent().then(s => s.includes("No company")));
  await p.locator("#gsearch").press("Escape");
  ok("Escape closes network search results", await p.locator("#ceresults").isHidden());
  const mostConnected = graph.nodes.toSorted((a, b) =>
    graph.edges.filter(e => e.a === b.key || e.b === b.key).length - graph.edges.filter(e => e.a === a.key || e.b === a.key).length)[0];
  await p.fill("#gsearch", mostConnected.name);
  await p.locator("#gsearch").press("ArrowDown");
  await p.keyboard.press("Enter");
  ok("keyboard search brings the chosen company into focus", await p.locator("#cename").textContent() === mostConnected.name);
  await p.locator("#cenodes button").first().focus();
  const key = await p.locator("#cenodes button").first().getAttribute("data-key");
  await p.keyboard.press("Enter");
  ok("a keyboard-selected point opens evidence without leaving the page", p.url() === url &&
    (await p.locator("#cereadout h4").textContent()).includes(byKey[key].name));

  const allNeighbors = new Set();
  do {
    for (const key of await p.$$eval("#cenodes button", list => list.map(el => el.dataset.key))) allNeighbors.add(key);
    if (!(await p.locator("#cenext").isEnabled())) break;
    await p.click("#cenext");
  } while (true);
  const expectedNeighbors = graph.edges.filter(e => e.a === mostConnected.key || e.b === mostConnected.key)
    .map(e => e.a === mostConnected.key ? e.b : e.a);
  ok("paging reaches every connection and identifies the partial view", allNeighbors.size === expectedNeighbors.length &&
    expectedNeighbors.every(k => allNeighbors.has(k)) && (await p.locator("#cescope").textContent()).includes(`of ${expectedNeighbors.length}`));
  const neighbor = (await p.locator("#cenodes button").first().getAttribute("data-key"));
  await p.locator("#cenodes button").first().click();
  await p.click(".cefollow");
  ok("following a connected company recenters the web", await p.locator("#cename").textContent() === byKey[neighbor].name);
  await p.click("#cemode");
  ok("the overview includes the whole network", await p.locator("#cenodes button").count() === graph.nodes.length &&
    (await p.locator("#cescope").textContent()).includes(`${graph.nodes.length} companies`));
  await p.locator(`#cenodes ${qkey(graph.initial)}`).click();
  ok("choosing an overview point restores its readable neighborhood", await p.locator("#cename").textContent() === byKey[graph.initial].name &&
    await p.locator("#cemode").getAttribute("aria-pressed") === "false");

  const certificate = records.find(r => source[r.id].name === "Cedarvale, Barslow/Pyote TX Data Center" && source[r.id].effective === "2026-03-16");
  await p.selectOption("#fxselect", certificate.id);
  ok("a repeated facility name opens the selected date and parties", await p.locator("#fxdate").textContent().then(s => s.includes("2026")) &&
    await p.locator("#fxroles").textContent().then(s => certificate.r.operator.every(party => s.includes(party.n))));
  const allSelections = [];
  for (const record of records) {
    await p.selectOption("#fxselect", record.id);
    const rendered = await p.evaluate(() => ({name:document.getElementById("fxname").textContent,
      date:document.getElementById("fxdate").textContent, names:[...document.querySelectorAll("#fxroles cite")].map(x=>x.textContent)}));
    const expected = Object.values(record.r).flat().map(party => party.n);
    if (rendered.name !== record.n || !rendered.date.includes(record.d) || JSON.stringify(rendered.names) !== JSON.stringify(expected)) allSelections.push(record.id);
  }
  ok("every certification can be read with all of its exact filed parties", allSelections.length === 0, allSelections.join(", "));
  ok("both explorers run without page errors", errors.length === 0, errors.join(" | "));
  await p.close();

  for (const width of [320, 390, 430, 1280]) {
    const ctx = await browser.newContext({viewport:{width,height:844},isMobile:width < 600,hasTouch:width < 600,reducedMotion:"reduce"});
    const p = await ctx.newPage();
    await p.goto(url, {waitUntil:"load"});
    const bad = [];
    // All company names, including the longest, at every target width.
    for (const company of graph.nodes) {
      await p.fill("#gsearch", company.name);
      await p.locator(`#ceresults ${qkey(company.key)}`).click();
      const fit = await p.evaluate(() => {
        const box = document.getElementById("ceplot").getBoundingClientRect();
        const nodes = [...document.querySelectorAll("#cenodes .cenode")].map(n => {
          const r=n.getBoundingClientRect(); return {name:n.textContent,x:r.x,y:r.y,right:r.right,bottom:r.bottom,w:r.width,h:r.height};
        });
        return {wide:document.documentElement.scrollWidth-document.documentElement.clientWidth,
          spills:nodes.filter(n=>n.x<box.x-1||n.right>box.right+1||n.y<box.y-1||n.bottom>box.bottom+1),
          small:nodes.filter(n=>n.w<44||n.h<44),
          overlaps:nodes.filter((n,i)=>nodes.some((o,j)=>j>i&&n.x<o.right&&n.right>o.x&&n.y<o.bottom&&n.bottom>o.y))};
      });
      if (fit.wide || fit.spills.length || fit.small.length || fit.overlaps.length) bad.push({company:company.name,...fit});
    }
    ok(`${width}px keeps every focused company readable, separated and within the diagram`, bad.length === 0, JSON.stringify(bad.slice(0,3)));

    const wrongPoints = [];
    for (const company of graph.nodes) {
      await p.click("#cemode");
      const dot = p.locator(`#cenodes ${qkey(company.key)} .cedot`);
      await dot.scrollIntoViewIfNeeded();
      const rect = await dot.boundingBox();
      const x = rect.x + rect.width / 2, y = rect.y + rect.height / 2;
      if (width < 600) await p.touchscreen.tap(x, y);
      else {
        await p.mouse.move(x,y);
        const hovered = await p.locator("#cenodes .hovered").getAttribute("data-key");
        if (hovered !== company.key) wrongPoints.push({wanted:company.key,hovered});
        await p.mouse.click(x,y);
      }
      const selected = await p.locator("#cename").textContent();
      if (selected !== company.name) wrongPoints.push({wanted:company.name,selected});
    }
    ok(`${width}px selects the drawn company at every overview point, even in an overlap`, wrongPoints.length === 0, JSON.stringify(wrongPoints.slice(0,3)));

    await p.fill("#gsearch", byKey[graph.initial].name);
    await p.locator(`#ceresults ${qkey(graph.initial)}`).click();
    const connection = p.locator("#cenodes button").first();
    const key = await connection.getAttribute("data-key");
    const edge = graph.edges.find(e => [e.a,e.b].includes(graph.initial) && [e.a,e.b].includes(key));
    if (width < 600) {
      await connection.tap();
      ok(`${width}px opens connection evidence with a touch`, await p.locator("#cesheet").evaluate(d => d.open) &&
        (await p.locator("#cesheet h4").textContent()).includes(byKey[key].name));
      ok(`${width}px keeps the background still while evidence is open`,
        await p.evaluate(()=>getComputedStyle(document.documentElement).overflow === "hidden"));
      await p.click("#cesheetclose");
      ok(`${width}px closes the sheet and returns to the same point`, await p.locator("#cesheet").evaluate(d => !d.open) &&
        await p.evaluate(key => document.activeElement?.dataset.key === key,key));
      await connection.tap();
    } else await connection.click();
    if (edge.f.length > 2) await p.locator(".cerecordmore summary").click();
    const evidenceIds = await p.$$eval("#cereadout [data-record]", list => list.map(el => el.dataset.record));
    ok(`${width}px reveals every certification behind the selected line`, evidenceIds.length === edge.f.length && edge.f.every(r=>evidenceIds.includes(r.id)));
    const record = edge.f[0];
    await p.locator(`#cereadout [data-record="${record.id}"]`).click();
    ok(`${width}px opens the exact certification from the network`, await p.inputValue("#fxselect") === record.id &&
      await p.locator("#fxname").textContent() === record.n && await p.evaluate(()=>document.activeElement?.id === "fxname"));
    // A native dialog's close event arrives after the click handler. Restoring an expanded
    // evidence list then used to move the selected record below the screen after the jump.
    await p.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    const recordPosition = await p.locator("#fxname").boundingBox();
    ok(`${width}px lands the expanded-evidence journey on a visible certification`,
      recordPosition.y >= 0 && recordPosition.y + recordPosition.height <= p.viewportSize().height,
      JSON.stringify(recordPosition));
    ok(`${width}px leaves the page usable after the evidence sheet closes`, await p.locator("#cesheet").evaluate(d=>!d.open) &&
      await p.locator("#fxselect").isVisible() && await p.locator("#fxback").isVisible() &&
      await p.evaluate(()=>getComputedStyle(document.documentElement).overflow !== "hidden"));
    await ctx.close();
  }
  // Default motion matters here: CSS smooth scrolling keeps the destination in flight while
  // the native close event returns the expanded evidence list to the document.
  const moving = await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  const movingPage = await moving.newPage();
  await movingPage.goto(url,{waitUntil:"load"});
  await movingPage.locator("#cenodes button").first().tap();
  await movingPage.locator(".cerecordmore summary").click();
  await movingPage.locator("#cereadout [data-record]").first().click();
  await movingPage.waitForTimeout(1000); // Read the landing after the browser's smooth scroll finishes.
  const movingPosition = await movingPage.locator("#fxname").boundingBox();
  ok("default phone motion lands the expanded-evidence journey on the selected record",
    movingPosition.y >= 0 && movingPosition.y + movingPosition.height <= 844,JSON.stringify(movingPosition));
  await moving.close();
  const nojs = await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const staticPage = await nojs.newPage();
  await staticPage.goto(url, {waitUntil:"load"});
  ok("without JavaScript every network company remains a real profile link", await staticPage.locator(".cefallback a").count() === graph.nodes.length &&
    await staticPage.locator(".cefallback").isVisible() && await staticPage.locator(".ceinteractive").isHidden());
  ok("without JavaScript a sourced certification and its parties still render", await staticPage.locator("#fxname").textContent().then(Boolean) &&
    await staticPage.locator("#fxroles cite").count() > 0 && await staticPage.locator(".fxpicker").isHidden());
  await nojs.close();
}
