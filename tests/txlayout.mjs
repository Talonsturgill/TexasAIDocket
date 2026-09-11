/* txlayout.mjs — the illustration system's libraries, loaded where a planner loads them.
 *
 * WHY THIS EXISTS. `assets/js/txlayout.js` is read by two consumers that never share a
 * process: a slide in Chromium and a run planning its rotation in Node before any slide
 * exists. `txscene.js`, `txfig.js` and `txobjects.js` build sprites with no DOM at all until
 * a context draws them, so the whole catalogue can be instantiated here and every object
 * proved to have a footprint. A library that throws on load, or an object that comes back
 * with no width, would otherwise be found by tomorrow's run at frame 7.
 *
 *     node tests/txlayout.mjs
 */
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);

global.window = global;
require("../assets/js/txscene.js");
require("../assets/js/txfig.js");
require("../assets/js/txobjects.js");
require("../assets/js/txlayout.js");

let failures = 0;
const check = (label, cond, extra = "") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) failures++;
};

// the table
check("ten archetypes", TXLAYOUT.ARCHETYPES.length === 10, String(TXLAYOUT.ARCHETYPES.length));
check("a clean rotation passes", TXLAYOUT.check(["FULL_BLEED", "DOCUMENT", "FIGURE_SCALE", "OBJECT_AND_CAPTION", "GRID", "DIAGRAM", "CLOSE_CROP", "SPLIT_HORIZON", "FULL_BLEED"]).length === 0);
check("a consecutive repeat fails", TXLAYOUT.check(["FULL_BLEED", "FULL_BLEED", "GRID", "MAP", "DIAGRAM", "DOCUMENT"]).some(p => p.includes("repeat")));
check("two TYPE_AS_OBJECT fail", TXLAYOUT.check(["TYPE_AS_OBJECT", "GRID", "TYPE_AS_OBJECT", "MAP", "DIAGRAM", "CLOSE_CROP"]).some(p => p.includes("TYPE_AS_OBJECT")));
check("too few distinct fails on a long deck", TXLAYOUT.check(["GRID", "MAP", "GRID", "MAP", "GRID", "MAP", "GRID", "MAP", "GRID"]).some(p => p.includes("distinct")));
check("a name off the list fails", TXLAYOUT.check(["POSTER", "GRID"]).some(p => p.includes("not an archetype")));
check("every archetype has a reserve", TXLAYOUT.ARCHETYPES.every(a => { const r = TXLAYOUT.reserve(a); return r && r.w > 0 && r.h > 0; }));

// the catalogue
const list = TXOBJ.list();
check("the catalogue has at least forty objects", list.length >= 40, String(list.length));
let bad = [];
for (const it of list) {
  try {
    const s = TXOBJ.sprite(it.name, { seed: 3 });
    if (!(s.w > 0) || !(s.h > 0) || !s.parts.length) bad.push(it.name);
    // every part is one of the four kinds the bench draws
    for (const p of s.parts) if (!["poly", "rect", "ellipse", "line"].includes(p.type)) bad.push(it.name + ":" + p.type);
  } catch (e) { bad.push(it.name + ": " + e.message); }
}
check("every object builds with a positive footprint from the four part kinds", bad.length === 0, bad.join(", "));
check("a school bus is twelve metres and a person is under two", TXOBJ.sprite("school_bus").w > 11.5 && TXOBJ.sprite("school_bus").w < 12.5 && TXFIG.figure().h < 2 && TXFIG.figure().h > 1.6);
check("the Capitol is taller than the water tower is taller than the house",
      TXOBJ.sprite("capitol").h > TXOBJ.sprite("water_tower").h && TXOBJ.sprite("water_tower").h > TXOBJ.sprite("house").h);
check("an unknown object throws and names the list", (() => { try { TXOBJ.sprite("unicorn"); return false; } catch (e) { return /school_bus/.test(e.message); } })());

// figures
const poses = Object.keys(TXFIG.POSES);
check("every pose builds", poses.every(p => TXFIG.figure({ pose: p }).parts.length > 6), poses.join(","));
check("the front view builds", TXFIG.figure({ view: "front" }).parts.length > 6);
const crowdA = TXFIG.crowd(8, { seed: 5 }), crowdB = TXFIG.crowd(8, { seed: 5 });
check("a crowd is the same crowd for the same seed", JSON.stringify(crowdA.map(e => [e.dx, e.mirror, e.sprite.h])) === JSON.stringify(crowdB.map(e => [e.dx, e.mirror, e.sprite.h])));

// the bench's camera, with no canvas: projection is pure arithmetic
const S = TXSCENE.create({ getTransform: () => ({ a: 1 }) }, { w: 1080, h: 1350, eye: 1.5, horizon: 600, f: 800, light: { az: -40, el: 38 } });
check("the horizon is where the eye height lands at infinity", Math.abs(S.project(0, 1.5, 1e9)[1] - 600) < 1e-3);
check("the ground recedes toward the horizon", S.groundY(2) > S.groundY(20) && S.groundY(20) > 600);
check("a far thing is smaller than a near thing", S.ppm(40) < S.ppm(4));
check("a light too low to cast a usable shadow is refused", (() => { try { TXSCENE.create({}, { light: { az: 0, el: 1 } }); return false; } catch (e) { return true; } })());

console.log(failures ? `txlayout: ${failures} FAILED` : "txlayout: all passed");
process.exit(failures ? 1 : 0);
