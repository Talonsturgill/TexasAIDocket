/* txgeo.js — Texas cartography helpers for slide code (requires d3 loaded).
 *
 * THE PROJECTION IS NOT A PREFERENCE. Texas spans roughly 13 degrees of
 * longitude and 11 of latitude, so a plate carree of lon/lat straight into
 * screen space stretches the Panhandle sideways and squashes the Valley. The
 * standard answer for a mid-latitude area this shape is an Albers equal-area
 * conic with the standard parallels set inside the state's own latitude range.
 * These numbers are the same ones scripts/site/texas_map.py uses to render the
 * 254-county map on the website, so a slide and the site agree about where
 * places are:
 *
 *     standard parallels   27.6 N and 35.0 N
 *     central meridian     99.9 W
 *     latitude of origin   31.2 N
 *
 * THE TRAP, WHICH IS WORTH MORE THAN THE PARAMETERS. Calling fitExtent with a
 * SMALL lon/lat bounding polygon distorts a conic fit badly: the result is a
 * giant fill disc and a mis-scaled map, and it does it without erroring. The
 * reliable recipe is to fit the FULL state first, then scale by a zoom factor
 * and re-translate so a chosen lon/lat lands at a chosen screen point.
 *
 * AT ZOOM ABOVE ROUGHLY 2, DRAW LAND AS STROKE ONLY. The polygon's far edges
 * project to enormous coordinates and any fill reads as a solid disc across
 * the whole frame.
 *
 * Usage:
 *   <script src="@@ASSETS@@/js/d3.v7.min.js"></script>
 *   <script src="@@ASSETS@@/js/topojson-client.min.js"></script>
 *   <script src="@@ASSETS@@/js/txgeo.js"></script>
 *
 *   const topo = await (await fetch("@@ASSETS@@/geo/tx-counties.topo.json")).json();
 *   const counties = TXGeo.counties(topo);          // FeatureCollection, 254
 *   const state    = TXGeo.outline(topo);           // merged state outline
 *
 *   const proj = TXGeo.texasProjection(state, [[80, 250], [1000, 1160]]);
 *   const path = d3.geoPath(proj);
 *   svg.append("path").attr("d", path(state)).attr("fill", "#241E2E");
 *
 *   // Regional zoom: put Abilene at screen (780, 470) at 6x.
 *   TXGeo.zoomTo(proj, state, TXGeo.place("Abilene"), [780, 470], 6);
 */
(function (global) {
  "use strict";

  /* Standard parallels, central meridian and latitude of origin. Kept as one
   * object so a slide can read them rather than retyping them, which is the
   * only way two files stay in agreement over time. */
  var FIT = { parallels: [27.6, 35.0], lon0: 99.9, lat0: 31.2 };

  /* A handful of anchors for zoom targets, as [lon, lat]. These are gauge-grade
   * coordinates for the places a Texas AI story actually lands in: the Permian,
   * the big metros, and the towns with announced large load. Anything not here
   * should come from assets/geo/tx-places.json, which carries all 254 county
   * centroids computed from the geometry rather than typed. */
  var PLACES = {
    "Abilene": [-99.7331, 32.4487],
    "Amarillo": [-101.8313, 35.2220],
    "Austin": [-97.7431, 30.2672],
    "Childress": [-100.2040, 34.4265],
    "Corpus Christi": [-97.3964, 27.8006],
    "Dallas": [-96.7970, 32.7767],
    "El Paso": [-106.4850, 31.7619],
    "Fort Worth": [-97.3308, 32.7555],
    "Houston": [-95.3698, 29.7604],
    "Laredo": [-99.5075, 27.5064],
    "Lubbock": [-101.8552, 33.5779],
    "Midland": [-102.0779, 31.9974],
    "Odessa": [-102.3676, 31.8457],
    "San Antonio": [-98.4936, 29.4241],
    "Waco": [-97.1467, 31.5493]
  };

  function feature(geo) {
    if (geo && geo.type === "FeatureCollection") return geo;
    if (geo && geo.type === "Feature") return geo;
    return { type: "Feature", geometry: geo };
  }

  /* Canonical Texas projection, fitted to whatever `geo` is inside `extent`
   * = [[x0,y0],[x1,y1]]. Pass the STATE outline, not a county, or see the trap
   * in the header. */
  function texasProjection(geo, extent) {
    if (typeof d3 === "undefined") throw new Error("TXGeo requires d3");
    return d3.geoConicEqualArea()
      .parallels(FIT.parallels)
      .rotate([FIT.lon0, 0])
      .center([0, FIT.lat0])
      .fitExtent(extent || [[0, 0], [1080, 1350]], feature(geo));
  }

  /* Zoom an already fitted projection so `lonlat` lands at screen `targetXY`
   * at `zoom` times the full-state scale. Mutates and returns `proj`. */
  function zoomTo(proj, geo, lonlat, targetXY, zoom) {
    if (!proj) proj = texasProjection(geo, [[0, 0], [1080, 1350]]);
    proj.scale(proj.scale() * (zoom || 1));
    var s = proj(lonlat);
    var t = proj.translate();
    proj.translate([t[0] + (targetXY[0] - s[0]), t[1] + (targetXY[1] - s[1])]);
    return proj;
  }

  /* The 254 counties as a FeatureCollection, from the committed TopoJSON. */
  function counties(topo) {
    if (typeof topojson === "undefined") throw new Error("TXGeo.counties requires topojson");
    var key = Object.keys(topo.objects)[0];
    return topojson.feature(topo, topo.objects[key]);
  }

  /* The state outline, merged from the county mesh. One polygon, no interior
   * borders, which is what a hero map wants behind everything else. */
  function outline(topo) {
    if (typeof topojson === "undefined") throw new Error("TXGeo.outline requires topojson");
    var key = Object.keys(topo.objects)[0];
    var o = topo.objects[key];
    return topojson.merge(topo, o.geometries || [o]);
  }

  /* Interior borders only, as a single mesh path. Drawing these as one path
   * rather than 254 strokes means a shared border is stroked once instead of
   * twice, which is the difference between a clean hairline and a doubled one. */
  function borders(topo) {
    if (typeof topojson === "undefined") throw new Error("TXGeo.borders requires topojson");
    var key = Object.keys(topo.objects)[0];
    return topojson.mesh(topo, topo.objects[key], function (a, b) { return a !== b; });
  }

  function place(name) {
    var p = PLACES[name];
    if (!p) throw new Error("TXGeo.place: unknown place " + name);
    return p.slice();
  }

  global.TXGeo = {
    texasProjection: texasProjection,
    zoomTo: zoomTo,
    counties: counties,
    outline: outline,
    borders: borders,
    place: place,
    PLACES: PLACES,
    FIT: FIT
  };
})(typeof window !== "undefined" ? window : globalThis);
