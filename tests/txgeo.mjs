/* txgeo.mjs — the slide cartography helper, tested where it actually runs.
 *
 * WHY THIS EXISTS. The Python map builder for the website has its own orientation test, and it
 * has it because the first Texas map rendered UPSIDE DOWN: Albers y grows northward and SVG y
 * grows downward, and nothing in either library objects. The slide engine reaches the same
 * geometry through a different path, d3 in a browser rather than Python, so it can be wrong in
 * exactly the same way while the Python test stays green.
 *
 * A map that is flipped, mirrored or mis-fitted does not throw. It renders, it looks like a
 * map, and it is wrong. Only an assertion about where a known place lands can catch it, so
 * that is what this does: Amarillo must sit above Laredo and El Paso must sit left of Houston.
 *
 *     node tests/txgeo.mjs
 */
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);

// The libraries are UMD builds. In a browser they attach to window; under Node they take the
// CommonJS branch, so the globals a slide would rely on are bound here by hand.
global.window = global;
global.d3 = require("../assets/js/d3.v7.min.js");
global.topojson = require("../assets/js/topojson-client.min.js");
require("../assets/js/txgeo.js");

const topo = require("../assets/geo/tx-counties.topo.json");

let failures = 0;
const check = (label, cond, extra = "") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) failures++;
};

const state = TXGeo.outline(topo);
const counties = TXGeo.counties(topo);

check("all 254 counties come through the topology", counties.features.length === 254,
      String(counties.features.length));
check("the outline merges to one shape, not 254", state.type === "MultiPolygon" ||
      state.type === "Polygon", state.type);
check("interior borders come back as a single mesh, so shared edges stroke once",
      TXGeo.borders(topo).type === "MultiLineString");

const EXT = [[80, 250], [1000, 1160]];
const proj = TXGeo.texasProjection(state, EXT);
const path = d3.geoPath(proj);
const b = path.bounds(state);
const w = b[1][0] - b[0][0], h = b[1][1] - b[0][1];

check("the fit stays inside the extent it was given",
      b[0][0] >= 79.9 && b[0][1] >= 249.9 && b[1][0] <= 1000.1 && b[1][1] <= 1160.1,
      JSON.stringify(b));
check("...and fills it on the constraining axis rather than floating in the middle",
      Math.abs(w - 920) < 0.5 || Math.abs(h - 910) < 0.5, `w=${w.toFixed(1)} h=${h.toFixed(1)}`);

// THE ORIENTATION CHECK. This is the whole reason the file exists.
const amarillo = proj(TXGeo.place("Amarillo"));
const laredo = proj(TXGeo.place("Laredo"));
const elPaso = proj(TXGeo.place("El Paso"));
const houston = proj(TXGeo.place("Houston"));

check("north renders above south, so the map is not upside down",
      amarillo[1] < laredo[1], `Amarillo y=${amarillo[1].toFixed(1)} Laredo y=${laredo[1].toFixed(1)}`);
check("west renders left of east, so the map is not mirrored",
      elPaso[0] < houston[0], `El Paso x=${elPaso[0].toFixed(1)} Houston x=${houston[0].toFixed(1)}`);
check("every anchor lands inside the frame it was fitted to",
      Object.keys(TXGeo.PLACES).every(k => {
        const p = proj(TXGeo.place(k));
        return p[0] > 60 && p[0] < 1020 && p[1] > 230 && p[1] < 1180;
      }),
      Object.keys(TXGeo.PLACES).filter(k => {
        const p = proj(TXGeo.place(k));
        return !(p[0] > 60 && p[0] < 1020 && p[1] > 230 && p[1] < 1180);
      }).join(", "));

// THE TRAP THE HEADER WARNS ABOUT, asserted rather than only described.
const full = TXGeo.texasProjection(state, [[0, 0], [1080, 1350]]);
const zoomed = TXGeo.zoomTo(full, state, TXGeo.place("Abilene"), [780, 470], 6);
const landed = zoomed(TXGeo.place("Abilene"));
check("zoomTo lands the target exactly where it was asked to",
      Math.abs(landed[0] - 780) < 0.5 && Math.abs(landed[1] - 470) < 0.5,
      JSON.stringify(landed.map(v => +v.toFixed(1))));
check("...and zooming actually scales rather than only panning",
      zoomed.scale() > TXGeo.texasProjection(state, [[0, 0], [1080, 1350]]).scale() * 5.9);

check("the projection agrees with the website's, so a slide and the site place things alike",
      TXGeo.FIT.parallels[0] === 27.6 && TXGeo.FIT.parallels[1] === 35.0 &&
      TXGeo.FIT.lon0 === 99.9 && TXGeo.FIT.lat0 === 31.2,
      JSON.stringify(TXGeo.FIT));

let threw = false;
try { TXGeo.place("Nome"); } catch { threw = true; }
check("an unknown place throws rather than returning a silent wrong point", threw);

console.log(failures ? `\ntxgeo: ${failures} FAILED` : "\ntxgeo: all passed");
process.exit(failures ? 1 : 0);
