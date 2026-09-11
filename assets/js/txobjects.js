/* txobjects.js — the catalogue of things Texas is made of, drawn at TRUE SCALE in metres.
 *
 * WHY THIS EXISTS (2026-09-11). Every deck before this one drew its objects from scratch in
 * screen pixels, and the result was that a bus was a slab, a tower was a triangle, a building
 * was a rectangle with a grid of squares, and a judge wrote "clip art" or "a diagram of a
 * place" under twenty one decks in a row. Drawing a recognisable pump jack takes a working
 * knowledge of what a pump jack is: a samson post, a walking beam, a horsehead, a crank and a
 * counterweight, in the proportions the real machine has. That knowledge belongs in a file a
 * run can call, not in a prompt a run has to rediscover under a deadline.
 *
 * Every object here is a TXSCENE sprite: parts in metres, origin at the centre of the
 * footprint, y up, side elevation facing +x unless the entry says otherwise. Place it with
 * `S.sprite(TXOBJ.sprite("school_bus"), { X, Z, inks })` and it comes out the right size next
 * to a person, a pole and a house, because they are all in the same metres.
 *
 * FILLS. Bodies default to 'ink' (a two-colour print reads best as ink silhouettes with paper
 * cut-outs) and details to 'paper'. Pass `{ body: "accent" }` to paint ONE object in the
 * deck's accent, `{ body: "tone", tone: 0.4 }` for a mid value, or a hex. Windows and lamps
 * are 'paper' and carry `noShadow` so a shadow is the hull and never a sieve.
 *
 * VARIATION. Objects that come in populations (trees, houses) take `seed` and vary
 * deterministically, so a row of live oaks is a row of different oaks and the same row next
 * render.
 *
 * THE LIST. `TXOBJ.list()` returns every name with its footprint, and `examples/objects/`
 * carries a rendered contact sheet of all of them beside a 1.7 m figure, which is what a
 * director should look at before choosing a subject.
 */
(function (global) {
  "use strict";

  var SC = global.TXSCENE;
  if (!SC) throw new Error("txobjects.js needs txscene.js loaded first");

  var R = {};   // the registry: name -> function(opts) -> parts, plus metadata

  function rng(seed) {
    var t = (seed >>> 0) || 1;
    return function () { t += 0x6D2B79F5; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; };
  }
  function body(o) { return o.body || "ink"; }
  function rect(x, y, w, h, fill, extra) { var p = { type: "rect", x: x, y: y, w: w, h: h, fill: fill }; if (extra) for (var k in extra) p[k] = extra[k]; return p; }
  function poly(pts, fill, extra) { var p = { type: "poly", pts: pts, fill: fill }; if (extra) for (var k in extra) p[k] = extra[k]; return p; }
  function ell(cx, cy, rx, ry, fill, extra) { var p = { type: "ellipse", cx: cx, cy: cy, rx: rx, ry: ry, fill: fill }; if (extra) for (var k in extra) p[k] = extra[k]; return p; }
  function line(pts, width, fill, extra) { var p = { type: "line", pts: pts, width: width, fill: fill }; if (extra) for (var k in extra) p[k] = extra[k]; return p; }
  function wheel(cx, r, bodyFill) {
    // a paper arch ring around an ink tyre with a paper hub reads on any body colour
    return [ell(cx, r, r * 1.12, r * 1.12, "paper", { noShadow: true }), ell(cx, r, r, r, "ink"), ell(cx, r, r * 0.42, r * 0.42, "paper", { noShadow: true })];
  }
  function windows(x0, y, n, w, h, gap, fill) {
    var out = [];
    for (var i = 0; i < n; i++) out.push(rect(x0 + i * (w + gap), y, w, h, fill || "paper", { noShadow: true }));
    return out;
  }

  /* ------------------------------------------------------------- vehicles */

  R.school_bus = { size: [12.0, 3.1], make: function (o) {
    var b = body(o), P = [];
    // conventional (Type C) bus: hood ahead of a tall body, black rub rails, a stop arm
    P.push(rect(-6.0, 0.62, 10.4, 2.5, b, { r: 0.18 }));
    P.push(poly([[4.4, 0.62], [6.0, 0.62], [6.0, 1.55], [5.7, 1.75], [4.4, 1.75]], b));
    P.push(poly([[4.4, 1.75], [5.6, 1.75], [4.4, 3.05]], b));            // the windshield rake
    P = P.concat(windows(-5.55, 1.9, 6, 1.32, 0.9, 0.36));               // side windows
    P.push(rect(4.55, 1.85, 0.95, 1.1, "paper", { noShadow: true }));   // windshield
    P.push(rect(-6.0, 1.45, 10.4, 0.12, "paper", { noShadow: true }));  // rub rail
    P.push(rect(-6.0, 0.95, 10.4, 0.10, "paper", { noShadow: true }));
    P.push(rect(-5.9, 3.05, 11.4, 0.14, b));                             // roof cap
    P.push(rect(-5.2, 3.19, 0.5, 0.18, b)); P.push(rect(3.6, 3.19, 0.5, 0.18, b)); // roof hatches
    P.push(rect(5.55, 2.55, 0.3, 0.35, "paper", { noShadow: true }));   // warning lamp
    P.push(rect(-5.9, 2.55, 0.3, 0.35, "paper", { noShadow: true }));
    P = P.concat(wheel(-3.7, 0.52, b), wheel(3.9, 0.52, b));
    return P;
  } };

  R.sedan = { size: [4.7, 1.45], make: function (o) {
    var b = body(o), P = [];
    P.push(poly([[-2.35, 0.42], [-2.3, 0.75], [-1.5, 0.82], [-0.9, 1.35], [0.85, 1.38], [1.7, 0.85], [2.35, 0.78], [2.35, 0.42]], b));
    P.push(poly([[-1.3, 0.85], [-0.75, 1.27], [-0.05, 1.28], [-0.05, 0.85]], "paper", { noShadow: true }));   // rear glass
    P.push(poly([[0.1, 0.85], [0.1, 1.28], [0.75, 1.28], [1.45, 0.85]], "paper", { noShadow: true }));        // windshield
    if (o.sensor) { P.push(rect(-0.32, 1.38, 0.64, 0.18, b, { r: 0.06 })); P.push(ell(0, 1.62, 0.22, 0.14, b)); }  // a robotaxi puck
    P = P.concat(wheel(-1.45, 0.34, b), wheel(1.5, 0.34, b));
    return P;
  } };

  R.pickup = { size: [5.9, 1.95], make: function (o) {
    var b = body(o), P = [];
    P.push(poly([[-2.95, 0.5], [-2.95, 1.3], [-0.55, 1.3], [-0.55, 1.35], [-0.35, 1.9], [1.35, 1.9], [2.0, 1.25], [2.95, 1.15], [2.95, 0.5]], b));
    P.push(poly([[-0.35, 1.32], [-0.2, 1.78], [1.25, 1.78], [1.85, 1.32]], "paper", { noShadow: true }));   // cab glass
    P.push(rect(0.72, 1.32, 0.08, 0.46, b, { noShadow: true }));                                          // door pillar
    P.push(rect(-2.85, 1.18, 2.25, 0.08, "paper", { noShadow: true }));                                   // bed rail
    P = P.concat(wheel(-2.0, 0.42, b), wheel(2.0, 0.42, b));
    return P;
  } };

  R.truck_semi = { size: [17.0, 4.1], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-8.5, 1.15, 13.6, 2.95, b));                                                  // trailer
    P.push(rect(-8.45, 1.15, 13.5, 0.06, "paper", { noShadow: true }));
    P.push(poly([[5.3, 0.45], [5.3, 3.9], [6.9, 3.9], [7.45, 3.2], [7.8, 2.2], [8.5, 1.9], [8.5, 0.45]], b));   // tractor
    P.push(poly([[6.95, 2.3], [6.95, 3.3], [7.35, 3.3], [7.75, 2.3]], "paper", { noShadow: true }));        // windshield
    P.push(rect(8.05, 1.05, 0.55, 0.65, "paper", { noShadow: true }));                                      // headlamp
    P.push(rect(5.5, 3.9, 1.3, 0.2, b));                                                                   // fairing
    P = P.concat(wheel(-6.1, 0.5, b), wheel(-4.9, 0.5, b), wheel(4.2, 0.5, b), wheel(5.5, 0.5, b), wheel(7.5, 0.5, b));
    return P;
  } };

  R.ambulance = { size: [6.7, 2.7], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-3.35, 0.6, 4.6, 2.1, b));
    P.push(poly([[1.25, 0.6], [1.25, 2.4], [2.2, 2.4], [2.8, 1.6], [3.35, 1.45], [3.35, 0.6]], b));
    P.push(poly([[1.35, 1.6], [1.35, 2.3], [2.1, 2.3], [2.6, 1.6]], "paper", { noShadow: true }));
    P.push(rect(-3.0, 1.9, 1.0, 0.5, "paper", { noShadow: true }));
    P.push(rect(-3.35, 1.25, 4.6, 0.22, "accent", { noShadow: true }));
    P.push(rect(-2.4, 2.7, 1.2, 0.18, "accent", { noShadow: true }));
    P = P.concat(wheel(-2.2, 0.42, b), wheel(2.3, 0.42, b));
    return P;
  } };

  /* ------------------------------------------------------------- the grid */

  R.utility_pole = { size: [2.4, 12.0], make: function (o) {
    var b = body(o), P = [];
    P.push(line([[0, 0], [0, 12]], 0.32, b));
    P.push(line([[-1.2, 11.1], [1.2, 11.1]], 0.16, b));                    // crossarm
    P.push(line([[-0.7, 10.4], [0, 11.05]], 0.06, b)); P.push(line([[0.7, 10.4], [0, 11.05]], 0.06, b));  // braces
    [-1.05, 0, 1.05].forEach(function (x) { P.push(rect(x - 0.07, 11.18, 0.14, 0.32, b)); });         // insulators
    if (o.transformer) { P.push(rect(0.2, 8.6, 0.62, 0.95, b, { r: 0.05 })); P.push(line([[0.5, 9.55], [0.5, 10.9]], 0.05, b)); }
    return P;
  } };

  R.transmission_tower = { size: [12.0, 42.0], make: function (o) {
    var b = body(o), P = [], H = o.height || 42, W = o.base || 9;
    // legs taper from the base to a waist under the lowest arm, then run parallel
    var waistY = H * 0.62, waistW = 2.4;
    P.push(line([[-W / 2, 0], [-waistW / 2, waistY], [-waistW / 2, H]], 0.34, b));
    P.push(line([[W / 2, 0], [waistW / 2, waistY], [waistW / 2, H]], 0.34, b));
    // the peak
    P.push(line([[-waistW / 2, H], [0, H + 3.0], [waistW / 2, H]], 0.24, b));
    // cross bracing below the waist, a zigzag between the legs
    var n = 8, prevL = [-W / 2, 0];
    for (var i = 1; i <= n; i++) {
      var t = i / n, y = waistY * t, hw = (W / 2) * (1 - t) + (waistW / 2) * t;
      var px = (i % 2 ? 1 : -1) * hw;
      P.push(line([[prevL[0], prevL[1]], [px, y]], 0.14, b));
      P.push(line([[-prevL[0], prevL[1]], [-px, y]], 0.14, b));
      P.push(line([[-hw, y], [hw, y]], 0.12, b));
      prevL = [px, y];
    }
    // three crossarms with insulator strings and a conductor stub
    [[waistY + 2, 12], [waistY + 8, 10.5], [H - 1, 9]].forEach(function (a) {
      var y = a[0], w = a[1];
      P.push(line([[-w / 2, y], [w / 2, y]], 0.26, b));
      P.push(line([[-w / 2 + 0.6, y - 1.6], [-waistW / 2, y + 1.2]], 0.12, b));
      P.push(line([[w / 2 - 0.6, y - 1.6], [waistW / 2, y + 1.2]], 0.12, b));
      P.push(line([[-w / 2 + 0.3, y - 0.1], [-w / 2 + 0.3, y - 2.6]], 0.14, b));
      P.push(line([[w / 2 - 0.3, y - 0.1], [w / 2 - 0.3, y - 2.6]], 0.14, b));
    });
    P.push(line([[-1.0, H + 3.0], [1.0, H + 3.0]], 0.18, b));
    return P;
  } };

  R.wind_turbine = { size: [8.0, 150.0], make: function (o) {
    var b = body(o), P = [], hub = o.hub || 95, blade = o.blade || 58, ang = (o.angle == null ? 12 : o.angle) * Math.PI / 180;
    P.push(poly([[-2.2, 0], [2.2, 0], [1.3, hub - 2], [-1.3, hub - 2]], b));       // tapered tower
    P.push(rect(-2.6, hub - 2.2, 6.0, 3.6, b, { r: 0.6 }));                          // nacelle
    P.push(ell(2.9, hub - 0.3, 1.2, 1.4, b));                                        // hub cone
    for (var i = 0; i < 3; i++) {
      var a = ang + i * Math.PI * 2 / 3;
      var dx = Math.sin(a), dy = Math.cos(a), nx = dy, ny = -dx;
      var w0 = 1.6, w1 = 0.5;
      P.push(poly([[2.9 + nx * w0 * 0.5, hub - 0.3 + ny * w0 * 0.5], [2.9 - nx * w0 * 0.5, hub - 0.3 - ny * w0 * 0.5],
                   [2.9 + dx * blade - nx * w1 * 0.5, hub - 0.3 + dy * blade - ny * w1 * 0.5], [2.9 + dx * blade + nx * w1 * 0.5, hub - 0.3 + dy * blade + ny * w1 * 0.5]], b));
    }
    return P;
  } };

  R.pump_jack = { size: [7.5, 5.2], make: function (o) {
    var b = body(o), P = [], tilt = (o.angle == null ? 8 : o.angle) * Math.PI / 180;
    P.push(rect(-3.6, 0, 5.4, 0.4, b));                                              // skid
    P.push(line([[-0.3, 0.4], [0.6, 4.6], [1.5, 0.4]], 0.32, b));                    // samson post
    P.push(line([[0.6, 0.4], [0.6, 4.6]], 0.22, b));
    P.push(rect(-3.3, 0.4, 1.3, 1.1, b));                                            // motor and gearbox
    P.push(ell(-2.05, 1.7, 0.75, 0.75, b));                                          // crank disc
    P.push(ell(-2.05, 1.7, 0.28, 0.28, "paper", { noShadow: true }));
    // walking beam pivoting on the post
    var bx = 0.6, by = 4.6, L1 = 3.1, L2 = 2.9;
    var hx = bx + Math.cos(tilt) * L1, hy = by + Math.sin(tilt) * L1;               // horsehead end
    var tx = bx - Math.cos(tilt) * L2, ty = by - Math.sin(tilt) * L2;               // tail end
    P.push(line([[tx, ty], [hx, hy]], 0.36, b));
    // the horsehead: a curved face hanging off the beam end
    P.push(poly([[hx - 0.2, hy + 0.45], [hx + 0.5, hy + 0.35], [hx + 0.95, hy - 0.2], [hx + 0.95, hy - 1.1], [hx + 0.55, hy - 1.35], [hx + 0.15, hy - 1.1], [hx - 0.2, hy - 0.4]], b));
    P.push(line([[hx + 0.9, hy - 1.0], [hx + 0.9, 0.9]], 0.08, b));                  // bridle and polished rod
    P.push(rect(hx + 0.55, 0.4, 0.7, 0.55, b));                                      // wellhead
    P.push(line([[tx, ty], [-2.05 + 0.6, 1.7 + 0.35]], 0.14, b));                    // pitman arm
    P.push(ell(-2.05 + 0.6, 1.7 + 0.35, 0.4, 0.4, b));                                // counterweight
    return P;
  } };

  R.substation = { size: [22.0, 12.0], make: function (o) {
    var b = body(o), P = [];
    // a gantry of lattice with insulators, and three transformers with bushings
    [-9, 9].forEach(function (x) { P.push(line([[x, 0], [x, 11]], 0.4, b)); for (var y = 1; y < 11; y += 2) { P.push(line([[x - 0.5, y], [x + 0.5, y + 2]], 0.08, b)); P.push(line([[x + 0.5, y], [x - 0.5, y + 2]], 0.08, b)); } });
    P.push(line([[-9.3, 11], [9.3, 11]], 0.36, b));
    for (var i = -6; i <= 6; i += 3) { P.push(line([[i, 10.8], [i, 9.4]], 0.16, b)); P.push(ell(i, 9.1, 0.32, 0.32, b)); }
    [-5.5, 0, 5.5].forEach(function (x, k) {
      P.push(rect(x - 2.2, 0.3, 4.4, 3.6, b, { r: 0.1 }));
      P.push(rect(x - 2.6, 0, 5.2, 0.3, b));
      for (var j = -1; j <= 1; j++) { P.push(line([[x + j * 1.1, 3.9], [x + j * 1.1, 5.6]], 0.26, b)); P.push(ell(x + j * 1.1, 5.75, 0.24, 0.24, b)); }
      P.push(rect(x - 2.5, 0.8, 0.28, 2.6, "paper", { noShadow: true }));            // radiator fins
      P.push(rect(x + 2.22, 0.8, 0.28, 2.6, "paper", { noShadow: true }));
    });
    return P;
  } };

  R.data_center = { size: [130.0, 16.0], make: function (o) {
    var b = body(o), P = [], L = o.length || 130, H = o.height || 13;
    P.push(rect(-L / 2, 0, L, H, b));
    P.push(rect(-L / 2 + 1.5, H, L - 3, 1.2, b));                                    // parapet
    // rooftop chillers, a row of them, which is what says data center rather than warehouse
    var n = Math.max(3, Math.floor(L / 11));
    for (var i = 0; i < n; i++) { var x = -L / 2 + 5 + i * (L - 10) / (n - 1); P.push(rect(x - 3.2, H + 1.2, 6.4, 3.0, b)); P.push(rect(x - 2.6, H + 1.6, 5.2, 0.5, "paper", { noShadow: true })); P.push(ell(x - 1.4, H + 4.2, 0.9, 0.35, "paper", { noShadow: true })); P.push(ell(x + 1.4, H + 4.2, 0.9, 0.35, "paper", { noShadow: true })); }
    // a louvre band, a service door, no windows
    P.push(rect(-L / 2 + 2, H * 0.55, L - 4, 1.6, "paper", { noShadow: true }));
    for (var k = 0; k < 6; k++) P.push(rect(-L / 2 + 2, H * 0.55 + 0.2 + k * 0.24, L - 4, 0.08, b, { noShadow: true }));
    P.push(rect(-L / 2 + 8, 0, 2.4, 3.2, "paper", { noShadow: true }));
    P.push(rect(L / 2 - 14, 0, 6, 4.6, "paper", { noShadow: true }));               // loading door
    return P;
  } };

  R.power_plant = { size: [70.0, 62.0], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-35, 0, 46, 22, b));                                                 // turbine hall
    P.push(poly([[-35, 22], [11, 22], [11, 26], [-12, 30], [-35, 26]], b));
    P.push(rect(12, 0, 16, 14, b));                                                  // HRSG block
    P.push(line([[22, 14], [22, 60]], 4.2, b, { cap: "butt" }));                     // stack
    P.push(line([[33, 0], [33, 58]], 3.6, b, { cap: "butt" }));
    P.push(rect(-33, 4, 42, 1.2, "paper", { noShadow: true }));
    P.push(rect(-33, 9, 42, 1.2, "paper", { noShadow: true }));
    return P;
  } };

  R.cooling_tower = { size: [90.0, 130.0], make: function (o) {
    var b = body(o), P = [], pts = [], H = 130;
    for (var i = 0; i <= 16; i++) { var t = i / 16, y = t * H, r = 30 + 15 * Math.pow(Math.abs(t - 0.62) / 0.62, 1.6) * (t < 0.62 ? 1 : 0.55); pts.push([r, y]); }
    var left = pts.map(function (p) { return [-p[0], p[1]]; }).reverse();
    P.push(poly(pts.concat(left), b));
    P.push(line([[-42, 0], [-42, 6]], 0.6, b)); P.push(line([[42, 0], [42, 6]], 0.6, b));
    return P;
  } };

  R.solar_panel = { size: [4.2, 2.6], make: function (o) {
    var b = body(o), P = [], a = (o.tilt == null ? 25 : o.tilt) * Math.PI / 180;
    P.push(line([[0, 0], [0, 1.4]], 0.16, b));
    var dx = Math.cos(a) * 2.0, dy = Math.sin(a) * 2.0;
    P.push(poly([[-dx, 1.4 - dy + 0.12], [dx, 1.4 + dy + 0.12], [dx, 1.4 + dy - 0.12], [-dx, 1.4 - dy - 0.12]], b));
    P.push(line([[-dx * 0.9, 1.4 - dy * 0.9 + 0.2], [dx * 0.9, 1.4 + dy * 0.9 + 0.2]], 0.06, "paper", { noShadow: true }));
    return P;
  } };

  R.battery_container = { size: [12.2, 2.9], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-6.1, 0.2, 12.2, 2.7, b));
    for (var i = 0; i < 5; i++) P.push(rect(-5.6 + i * 2.35, 0.6, 1.9, 1.9, "paper", { noShadow: true }));
    for (var k = 0; k < 5; k++) for (var j = 0; j < 4; j++) P.push(rect(-5.5 + k * 2.35, 0.8 + j * 0.42, 1.7, 0.12, b, { noShadow: true }));
    P.push(rect(-6.3, 0, 12.6, 0.2, b));
    return P;
  } };

  R.server_rack = { size: [0.6, 2.1], make: function (o) {
    var b = body(o), P = [], n = 12;
    P.push(rect(-0.3, 0, 0.6, 2.1, b));
    for (var i = 0; i < n; i++) { P.push(rect(-0.24, 0.12 + i * 0.16, 0.48, 0.1, "paper", { noShadow: true })); P.push(rect(0.14, 0.14 + i * 0.16, 0.05, 0.05, "accent", { noShadow: true })); }
    return P;
  } };

  /* ------------------------------------------------------------- water and land */

  R.water_tower = { size: [12.0, 38.0], make: function (o) {
    var b = body(o), P = [], H = o.height || 38, r = 5.0;
    var tankY = H - 10;
    // legs: four, three visible in elevation, splayed
    [[-5.2, -2.6], [0, 0], [5.2, 2.6]].forEach(function (l) { P.push(line([[l[0], 0], [l[1], tankY + 1]], 0.34, b)); });
    for (var y = 5; y < tankY; y += 8) {
      var t = y / tankY, hw = 5.2 * (1 - t) + 2.6 * t, y2 = Math.min(tankY, y + 8), t2 = y2 / tankY, hw2 = 5.2 * (1 - t2) + 2.6 * t2;
      P.push(line([[-hw, y], [hw, y]], 0.1, b));
      P.push(line([[-hw, y], [hw2, y2]], 0.08, b)); P.push(line([[hw, y], [-hw2, y2]], 0.08, b));
    }
    P.push(line([[0, 0], [0, tankY]], 0.5, b));                                     // riser
    P.push(rect(-r, tankY, 2 * r, 6.5, b));                                          // tank shell
    P.push(poly([[-r, tankY], [r, tankY], [r * 0.5, tankY - 3.2], [-r * 0.5, tankY - 3.2]], b));   // bottom cone
    P.push(poly([[-r - 0.3, tankY + 6.5], [r + 0.3, tankY + 6.5], [0, tankY + 10]], b));           // roof
    P.push(rect(-r + 0.4, tankY + 2.4, 2 * r - 0.8, 1.8, "paper", { noShadow: true }));           // the band a town paints its name on
    P.push(line([[-r - 0.6, tankY + 6.3], [r + 0.6, tankY + 6.3]], 0.12, b));                     // catwalk
    return P;
  } };

  R.windmill = { size: [3.0, 11.0], make: function (o) {
    var b = body(o), P = [], H = 9.5, a0 = (o.angle || 0) * Math.PI / 180;
    P.push(line([[-1.4, 0], [-0.35, H]], 0.14, b)); P.push(line([[1.4, 0], [0.35, H]], 0.14, b));
    for (var y = 1.5; y < H; y += 1.6) { var t = y / H, hw = 1.4 * (1 - t) + 0.35 * t; P.push(line([[-hw, y], [hw, y]], 0.06, b)); P.push(line([[-hw, y], [hw * 0.8, y + 1.6]], 0.05, b)); }
    P.push(rect(-0.4, H, 0.8, 0.5, b));
    var cx = 0.35, cy = H + 0.25;
    for (var i = 0; i < 18; i++) { var a = a0 + i * Math.PI * 2 / 18; P.push(poly([[cx + Math.cos(a) * 0.3, cy + Math.sin(a) * 0.3], [cx + Math.cos(a + 0.18) * 1.25, cy + Math.sin(a + 0.18) * 1.25], [cx + Math.cos(a - 0.05) * 1.25, cy + Math.sin(a - 0.05) * 1.25]], b)); }
    P.push(ell(cx, cy, 1.28, 1.28, "none", { stroke: true, strokePx: 2 }));
    P.push(line([[-0.2, H + 0.25], [-1.9, H + 0.6]], 0.08, b)); P.push(poly([[-1.9, H + 1.1], [-1.9, H + 0.1], [-2.7, H + 0.6]], b));   // tail vane
    return P;
  } };

  R.stock_tank = { size: [8.0, 1.0], make: function (o) {
    var b = body(o), P = [];
    P.push(poly([[-4, 0], [4, 0], [3.6, 0.9], [-3.6, 0.9]], b));
    P.push(ell(0, 0.9, 3.6, 0.5, "tone", { tone: 0.55, noShadow: true }));
    return P;
  } };

  R.live_oak = { size: [16.0, 11.0], make: function (o) {
    var b = body(o), P = [], r = rng(o.seed || 1), spread = o.spread || 15, h = o.height || 11;
    // a short, heavy trunk that leans and splits low, and a canopy wider than it is tall
    var lean = (r() - 0.5) * 1.2;
    P.push(poly([[-0.9, 0], [0.9, 0], [0.7 + lean, 2.6], [-0.5 + lean, 2.6]], b));
    P.push(line([[lean, 2.4], [lean - spread * 0.28, 4.8], [lean - spread * 0.4, 5.6]], 0.6, b));
    P.push(line([[lean, 2.4], [lean + spread * 0.25, 5.0], [lean + spread * 0.42, 5.4]], 0.55, b));
    P.push(line([[lean, 2.4], [lean + 0.4, 5.2], [lean + 1.2, 7.0]], 0.5, b));
    var n = 9 + Math.floor(r() * 4);
    for (var i = 0; i < n; i++) {
      var t = i / (n - 1), x = lean + (t - 0.5) * spread * (0.9 + r() * 0.2);
      var cy = 3.6 + Math.sin(t * Math.PI) * (h - 5.5) * (0.55 + r() * 0.45) + 1.2;
      var rx = spread * (0.14 + r() * 0.1), ry = (h - 3.5) * (0.22 + r() * 0.14);
      P.push(ell(x, cy, rx, ry, b));
    }
    return P;
  } };

  R.pine = { size: [7.0, 26.0], make: function (o) {
    var b = body(o), P = [], r = rng(o.seed || 1), h = o.height || 26;
    P.push(poly([[-0.35, 0], [0.35, 0], [0.18, h * 0.6], [-0.18, h * 0.6]], b));
    var n = 6;
    for (var i = 0; i < n; i++) { var t = i / (n - 1), y = h * (0.45 + 0.5 * t), w = 3.2 * (1 - t * 0.75) * (0.85 + r() * 0.3); P.push(ell((r() - 0.5) * 1.2, y, w, h * 0.06 + r() * 0.8, b)); }
    P.push(poly([[-1.0, h * 0.9], [1.0, h * 0.9], [0, h]], b));
    return P;
  } };

  R.mesquite = { size: [8.0, 6.0], make: function (o) {
    var b = body(o), P = [], r = rng(o.seed || 1);
    var trunks = 2 + Math.floor(r() * 2);
    for (var k = 0; k < trunks; k++) { var x0 = (k - (trunks - 1) / 2) * 0.6, x1 = x0 + (r() - 0.5) * 4, x2 = x1 + (r() - 0.5) * 3; P.push(line([[x0, 0], [x1, 2.4 + r()], [x2, 4.2 + r() * 1.2]], 0.28, b)); P.push(line([[x1, 2.4 + r()], [x1 + (r() - 0.5) * 3.5, 3.6 + r()]], 0.16, b)); }
    var n = 7;
    for (var i = 0; i < n; i++) P.push(ell((r() - 0.5) * 7, 3.6 + r() * 2.2, 1.2 + r() * 1.4, 0.55 + r() * 0.5, b));
    return P;
  } };

  R.cattle = { size: [2.5, 1.5], make: function (o) {
    var b = body(o), P = [];
    P.push(poly([[-1.15, 0.65], [-1.25, 1.3], [-0.9, 1.42], [0.55, 1.4], [0.85, 1.3], [1.0, 1.05], [1.0, 0.7], [0.7, 0.6], [-0.9, 0.6]], b));   // body
    P.push(poly([[0.85, 1.35], [1.05, 1.5], [1.35, 1.35], [1.45, 1.05], [1.4, 0.8], [1.2, 0.72], [0.95, 0.85], [0.85, 1.1]], b));             // head
    P.push(line([[1.0, 1.5], [1.35, 1.65]], 0.06, b)); P.push(line([[0.9, 1.48], [0.75, 1.62]], 0.06, b));                                    // horns
    [-0.95, -0.7, 0.55, 0.8].forEach(function (x) { P.push(line([[x, 0.65], [x, 0.05]], 0.16, b)); });
    P.push(line([[-1.2, 1.25], [-1.35, 0.45]], 0.06, b));
    return P;
  } };

  R.fence_post = { size: [0.2, 1.4], make: function (o) { return [line([[0, 0], [0, 1.4]], 0.14, body(o))]; } };

  /* ------------------------------------------------------------- buildings */

  R.house = { size: [16.0, 6.0], make: function (o) {
    var b = body(o), P = [], r = rng(o.seed || 1), two = o.style === "two_story";
    var W = two ? 13 : 16, H = two ? 6.0 : 3.1;
    P.push(rect(-W / 2, 0, W, H, b));
    var pitch = two ? 2.6 : 2.2;
    P.push(poly([[-W / 2 - 0.6, H], [W / 2 + 0.6, H], [W / 2 - 3.5, H + pitch], [-W / 2 + 3.5, H + pitch]], b));       // hipped roof
    // windows, a door, a garage door, a chimney
    var gx = W / 2 - 5.2;
    P.push(rect(gx, 0, 4.9, 2.3, "paper", { noShadow: true }));
    for (var k = 1; k < 4; k++) P.push(rect(gx, k * 0.55, 4.9, 0.06, b, { noShadow: true }));
    P.push(rect(-W / 2 + 1.2, 0.9, 1.4, 1.4, "paper", { noShadow: true }));
    P.push(rect(-W / 2 + 3.6, 0.9, 1.4, 1.4, "paper", { noShadow: true }));
    P.push(rect(-W / 2 + 6.2, 0, 1.0, 2.2, "paper", { noShadow: true }));
    if (two) { P.push(rect(-W / 2 + 1.2, 3.8, 1.4, 1.4, "paper", { noShadow: true })); P.push(rect(-W / 2 + 3.6, 3.8, 1.4, 1.4, "paper", { noShadow: true })); P.push(rect(gx + 0.8, 3.8, 1.4, 1.4, "paper", { noShadow: true })); }
    if (r() < 0.6) P.push(rect(-W / 2 + 4.5 + r() * 3, H + pitch * 0.4, 0.7, pitch * 0.8 + 0.4, b));
    return P;
  } };

  R.school = { size: [60.0, 8.0], make: function (o) {
    var b = body(o), P = [], L = o.length || 60;
    P.push(rect(-L / 2, 0, L, 4.6, b));
    P.push(rect(-6, 0, 12, 7.2, b));                                                 // the entrance block
    P.push(rect(-2.4, 0, 4.8, 3.0, "paper", { noShadow: true }));                    // doors
    P.push(rect(-0.06, 0, 0.12, 3.0, b, { noShadow: true }));
    P.push(rect(-4.5, 4.9, 9, 1.4, "paper", { noShadow: true }));                    // the name band
    var n = Math.floor((L / 2 - 8) / 2.6);
    for (var i = 0; i < n; i++) { P.push(rect(8 + i * 2.6, 1.4, 1.9, 1.8, "paper", { noShadow: true })); P.push(rect(-8 - i * 2.6 - 1.9, 1.4, 1.9, 1.8, "paper", { noShadow: true })); }
    P.push(line([[-L / 2 + 6, 0], [-L / 2 + 6, 10]], 0.12, b));                       // flagpole
    P.push(rect(-L / 2 + 6.06, 8.6, 1.5, 1.0, "accent", { noShadow: true }));
    return P;
  } };

  R.civic_facade = { size: [30.0, 20.0], make: function (o) {
    var b = body(o), P = [], W = o.width || 30, cols = o.columns || 6;
    // steps, a plinth, a colonnade, an entablature, a pediment, and windows either side
    P.push(poly([[-W / 2 - 2, 0], [W / 2 + 2, 0], [W / 2 + 1, 1.6], [-W / 2 - 1, 1.6]], b));
    P.push(rect(-W / 2, 1.6, W, 12.5, b));
    var cw = W * 0.42, x0 = -cw / 2;
    P.push(rect(x0 - 0.8, 1.6, cw + 1.6, 0.9, "tone", { tone: 0.35 }));
    for (var i = 0; i < cols; i++) { var x = x0 + i * cw / (cols - 1); P.push(line([[x, 2.5], [x, 11.2]], 0.9, "paper", { cap: "butt", noShadow: true })); P.push(rect(x - 0.65, 11.0, 1.3, 0.5, "paper", { noShadow: true })); P.push(rect(x - 0.6, 2.5, 1.2, 0.35, "paper", { noShadow: true })); }
    P.push(rect(x0 - 1.2, 11.5, cw + 2.4, 1.6, b));
    P.push(poly([[x0 - 1.6, 13.1], [x0 + cw + 1.6, 13.1], [0, 13.1 + cw * 0.19]], b));
    P.push(poly([[x0 - 0.4, 13.5], [x0 + cw + 0.4, 13.5], [0, 13.5 + cw * 0.14]], "paper", { noShadow: true }));
    P.push(rect(-1.4, 2.5, 2.8, 4.6, "paper", { noShadow: true }));                  // door
    var wn = Math.floor((W / 2 - cw / 2 - 1.5) / 2.4);
    for (var k = 0; k < wn; k++) for (var row = 0; row < 2; row++) { var wx = cw / 2 + 1.5 + k * 2.4; P.push(rect(wx, 3.2 + row * 4.4, 1.5, 2.8, "paper", { noShadow: true })); P.push(rect(-wx - 1.5, 3.2 + row * 4.4, 1.5, 2.8, "paper", { noShadow: true })); }
    if (o.dome) { P.push(rect(-4.5, 14.1, 9, 3.4, b)); P.push(ell(0, 17.5, 4.6, 3.4, b)); P.push(rect(-0.6, 20.6, 1.2, 1.8, b)); }
    return P;
  } };

  R.capitol = { size: [100.0, 95.0], make: function (o) {
    // The Texas Capitol's centre section: the rusticated base, the portico, the drum with its
    // colonnade, the dome, the lantern and the figure on top. 94 m to the star.
    var b = body(o), P = [];
    P.push(rect(-50, 0, 100, 4.5, b));                                               // terrace
    P.push(rect(-46, 4.5, 92, 20, b));                                               // main block, three storeys
    for (var i = 0; i < 14; i++) for (var row = 0; row < 3; row++) { var wx = -43 + i * 6.4; if (Math.abs(wx + 1) < 12) continue; P.push(rect(wx, 7 + row * 5.6, 2.2, 3.6, "paper", { noShadow: true })); }
    P.push(rect(-12, 4.5, 24, 22, b));                                               // central pavilion
    for (var c = 0; c < 6; c++) { var cx = -9 + c * 3.6; P.push(line([[cx, 10], [cx, 22]], 1.1, "paper", { cap: "butt", noShadow: true })); }
    P.push(poly([[-12.5, 22.5], [12.5, 22.5], [0, 28]], b));                          // pediment
    P.push(rect(-3, 4.5, 6, 5.5, "paper", { noShadow: true }));                        // the entrance arch
    P.push(rect(-15, 26, 30, 8, b));                                                 // attic under the drum
    P.push(rect(-11.5, 34, 23, 16, b));                                              // drum
    for (var d = 0; d < 9; d++) { var dx = -9.6 + d * 2.4; P.push(line([[dx, 36], [dx, 48]], 0.7, "paper", { cap: "butt", noShadow: true })); }
    P.push(rect(-13, 50, 26, 2, b));
    P.push(ell(0, 51, 12.5, 14, b));                                                 // the dome
    for (var w = 0; w < 5; w++) { var ang = -0.9 + w * 0.45; P.push(rect(Math.sin(ang) * 10.5 - 0.6, 53 + Math.cos(ang) * 6 - 2, 1.2, 2.6, "paper", { noShadow: true })); }
    P.push(rect(-3.6, 64, 7.2, 8, b));                                               // lantern
    for (var l = 0; l < 3; l++) P.push(rect(-2.6 + l * 2.2, 65.5, 0.9, 4.5, "paper", { noShadow: true }));
    P.push(ell(0, 72.5, 3.9, 3.4, b));
    P.push(rect(-0.5, 75, 1.0, 2.5, b));
    P.push(line([[0, 77.5], [0, 82]], 1.6, b));                                       // the Goddess of Liberty, at this scale a stroke
    P.push(ell(0, 82.6, 0.6, 0.7, b));
    P.push(poly([[0, 84.5], [0.9, 82.9], [-0.9, 82.9]], b));
    return P;
  } };

  R.hospital = { size: [60.0, 30.0], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-30, 0, 60, 6, b));
    P.push(rect(-16, 6, 32, 22, b));
    for (var row = 0; row < 5; row++) for (var i = 0; i < 9; i++) P.push(rect(-14.5 + i * 3.4, 8 + row * 4, 2.2, 2.2, "paper", { noShadow: true }));
    P.push(rect(-4, 0, 8, 4.2, "paper", { noShadow: true }));
    P.push(rect(-8, 26, 16, 2.4, "paper", { noShadow: true }));
    P.push(rect(-1.2, 27.5, 2.4, 0.7, "accent", { noShadow: true })); P.push(rect(-0.35, 26.65, 0.7, 2.4, "accent", { noShadow: true }));
    return P;
  } };

  R.warehouse = { size: [90.0, 12.0], make: function (o) {
    var b = body(o), P = [], L = o.length || 90;
    P.push(rect(-L / 2, 0, L, 11, b));
    P.push(rect(-L / 2, 11, L, 0.8, b));
    var n = Math.floor(L / 9);
    for (var i = 0; i < n; i++) P.push(rect(-L / 2 + 3 + i * 9, 0, 3.6, 4.2, "paper", { noShadow: true }));
    P.push(rect(-L / 2 + 2, 8.2, L - 4, 0.9, "paper", { noShadow: true }));
    return P;
  } };

  R.strip_mall = { size: [40.0, 6.0], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-20, 0, 40, 5.2, b));
    P.push(rect(-21, 5.2, 42, 1.2, b));
    for (var i = 0; i < 5; i++) { P.push(rect(-19 + i * 8, 0.2, 6.2, 3.0, "paper", { noShadow: true })); P.push(rect(-18.6 + i * 8, 3.6, 5.4, 1.1, "paper", { noShadow: true })); }
    return P;
  } };

  /* ------------------------------------------------------------- street furniture */

  R.road_sign = { size: [2.0, 3.0], make: function (o) {
    var b = body(o), P = [], kind = o.kind || "shield";
    if (kind === "stop") { P.push(line([[0, 0], [0, 1.9]], 0.1, b)); var pts = []; for (var i = 0; i < 8; i++) { var a = Math.PI / 8 + i * Math.PI / 4; pts.push([Math.cos(a) * 0.45, 2.35 + Math.sin(a) * 0.45]); } P.push(poly(pts, "accent")); P.push(rect(-0.3, 2.28, 0.6, 0.14, "paper", { noShadow: true })); }
    else { P.push(line([[-0.6, 0], [-0.6, 1.6]], 0.1, b)); P.push(line([[0.6, 0], [0.6, 1.6]], 0.1, b)); P.push(rect(-0.9, 1.6, 1.8, 1.2, "paper", { r: 0.08, stroke: true, strokePx: 2 })); }
    return P;
  } };

  R.billboard = { size: [14.6, 12.0], make: function (o) {
    var b = body(o), P = [], W = o.width || 14.6, H = o.height || 4.3, up = o.up || 7.5;
    P.push(line([[0, 0], [0, up]], 0.9, b, { cap: "butt" }));
    P.push(rect(-W / 2, up, W, H, "paper", { stroke: true, strokePx: 2 }));
    P.push(line([[-W / 2 + 0.4, up - 0.6], [W / 2 - 0.4, up - 0.6]], 0.2, b));
    P.push(line([[-W / 2 + 0.4, up - 0.6], [-W / 2 + 0.4, up]], 0.14, b)); P.push(line([[W / 2 - 0.4, up - 0.6], [W / 2 - 0.4, up]], 0.14, b));
    for (var i = -1; i <= 1; i++) P.push(line([[i * W * 0.3, up + H], [i * W * 0.3 + 0.7, up + H + 0.9]], 0.1, b));
    return P;
  }, panel: function (o) { var W = o.width || 14.6, H = o.height || 4.3, up = o.up || 7.5; return { x: -W / 2, y: up, w: W, h: H }; } };

  R.camera_pole = { size: [1.2, 4.5], make: function (o) {
    var b = body(o), P = [];
    P.push(line([[0, 0], [0, 4.2]], 0.1, b));
    P.push(poly([[-0.55, 4.55], [0.55, 4.55], [0.55, 4.05], [-0.55, 4.05]], b));    // solar panel
    P.push(rect(-0.14, 3.2, 0.34, 0.24, b, { r: 0.03 }));                           // the camera unit
    P.push(rect(0.2, 3.26, 0.1, 0.12, "paper", { noShadow: true }));
    return P;
  } };

  R.streetlight = { size: [3.0, 10.0], make: function (o) {
    var b = body(o), P = [];
    P.push(line([[0, 0], [0, 9.4], [2.4, 9.8]], 0.2, b));
    P.push(rect(2.0, 9.6, 1.0, 0.3, b));
    return P;
  } };

  R.traffic_signal = { size: [8.0, 6.5], make: function (o) {
    var b = body(o), P = [];
    P.push(line([[0, 0], [0, 6.0], [7.0, 6.0]], 0.3, b));
    [3.0, 5.5].forEach(function (x) { P.push(rect(x - 0.3, 4.5, 0.6, 1.5, b, { r: 0.06 })); P.push(ell(x, 5.6, 0.16, 0.16, "paper", { noShadow: true })); P.push(ell(x, 5.15, 0.16, 0.16, "paper", { noShadow: true })); P.push(ell(x, 4.7, 0.16, 0.16, "accent", { noShadow: true })); });
    return P;
  } };

  /* ------------------------------------------------------------- interiors */

  R.desk = { size: [1.6, 1.2], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-0.8, 0.72, 1.6, 0.05, b));
    P.push(line([[-0.72, 0], [-0.72, 0.72]], 0.05, b)); P.push(line([[0.72, 0], [0.72, 0.72]], 0.05, b));
    P.push(rect(0.15, 0.1, 0.55, 0.62, b));
    if (o.monitor !== false) { P.push(rect(-0.25, 0.77, 0.06, 0.16, b)); P.push(rect(-0.5, 0.93, 0.56, 0.36, b, { r: 0.02 })); P.push(rect(-0.47, 0.96, 0.5, 0.3, "paper", { noShadow: true })); }
    return P;
  } };

  R.office_chair = { size: [0.7, 1.2], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-0.3, 0.42, 0.55, 0.06, b));
    P.push(poly([[-0.34, 0.42], [-0.22, 0.42], [-0.16, 1.05], [-0.3, 1.1]], b));
    P.push(line([[-0.05, 0.42], [-0.05, 0.1]], 0.06, b)); P.push(line([[-0.35, 0.05], [0.25, 0.05]], 0.05, b));
    return P;
  } };

  R.student_desk = { size: [0.9, 0.85], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-0.05, 0.7, 0.55, 0.04, b));
    P.push(line([[0.0, 0], [0.0, 0.7]], 0.04, b)); P.push(line([[0.45, 0], [0.45, 0.7]], 0.04, b));
    P.push(rect(-0.42, 0.42, 0.34, 0.04, b));
    P.push(poly([[-0.42, 0.42], [-0.36, 0.42], [-0.32, 0.8], [-0.42, 0.82]], b));
    P.push(line([[-0.36, 0], [-0.36, 0.42]], 0.04, b)); P.push(line([[-0.1, 0], [-0.1, 0.42]], 0.04, b));
    return P;
  } };

  R.dais = { size: [9.0, 1.3], make: function (o) {
    // the bench a commission or a committee sits behind: a long front panel, a top, a
    // raised centre, microphone stalks. Figures sit behind it on chairs at seat 0.6.
    var b = body(o), P = [], L = o.length || 9, seats = o.seats || 5;
    P.push(rect(-L / 2, 0, L, 1.1, b));
    P.push(rect(-L / 2 - 0.1, 1.1, L + 0.2, 0.08, b));
    P.push(rect(-L / 2 + 0.2, 0.3, L - 0.4, 0.55, "tone", { tone: 0.3, noShadow: true }));
    for (var i = 0; i < seats; i++) { var x = -L / 2 + (i + 0.5) * L / seats; P.push(line([[x, 1.18], [x + 0.1, 1.55]], 0.03, b)); P.push(ell(x + 0.11, 1.58, 0.04, 0.04, b)); }
    return P;
  } };

  R.podium = { size: [0.7, 1.25], make: function (o) {
    var b = body(o), P = [];
    P.push(poly([[-0.3, 0], [0.3, 0], [0.36, 1.1], [-0.36, 1.18]], b));
    P.push(line([[0.1, 1.15], [0.2, 1.5]], 0.03, b)); P.push(ell(0.21, 1.53, 0.04, 0.04, b));
    return P;
  } };

  R.hospital_bed = { size: [2.2, 1.3], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-1.05, 0.55, 2.1, 0.18, b));
    P.push(poly([[-1.05, 0.73], [-0.35, 0.73], [-0.35, 1.05], [-1.05, 1.15]], "paper", { stroke: true, strokePx: 2 }));   // the raised head
    P.push(rect(-0.35, 0.73, 1.4, 0.22, "paper", { stroke: true, strokePx: 2 }));
    P.push(line([[-1.1, 0.4], [-1.1, 1.25]], 0.05, b)); P.push(line([[1.1, 0.4], [1.1, 0.95]], 0.05, b));
    P.push(rect(-0.9, 0.25, 1.8, 0.3, b));
    [-0.85, 0.85].forEach(function (x) { P.push(ell(x, 0.1, 0.1, 0.1, b)); });
    return P;
  } };

  R.filing_box = { size: [0.4, 0.28], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-0.2, 0, 0.4, 0.26, b)); P.push(rect(-0.21, 0.24, 0.42, 0.05, b));
    P.push(rect(-0.12, 0.08, 0.24, 0.06, "paper", { noShadow: true }));
    return P;
  } };

  R.pallet_boxes = { size: [1.2, 1.7], make: function (o) {
    var b = body(o), P = [], rows = o.rows || 5;
    P.push(rect(-0.6, 0, 1.2, 0.14, b));
    for (var r = 0; r < rows; r++) for (var c = 0; c < 3; c++) { P.push(rect(-0.58 + c * 0.4, 0.16 + r * 0.3, 0.36, 0.26, b)); P.push(rect(-0.5 + c * 0.4, 0.24 + r * 0.3, 0.2, 0.05, "paper", { noShadow: true })); }
    return P;
  } };

  R.voting_booth = { size: [0.9, 1.6], make: function (o) {
    var b = body(o), P = [];
    P.push(line([[-0.3, 0], [-0.3, 1.0]], 0.04, b)); P.push(line([[0.3, 0], [0.3, 1.0]], 0.04, b));
    P.push(rect(-0.4, 1.0, 0.8, 0.55, b));
    P.push(rect(-0.32, 1.05, 0.64, 0.45, "paper", { noShadow: true }));
    P.push(rect(-0.4, 0.85, 0.8, 0.15, b));
    return P;
  } };

  /* ------------------------------------------------------------- flying and small */

  R.drone = { size: [1.0, 0.3], make: function (o) {
    var b = body(o), P = [];
    P.push(rect(-0.18, 0, 0.36, 0.14, b, { r: 0.04 }));
    P.push(line([[-0.42, 0.12], [0.42, 0.12]], 0.04, b));
    [-0.42, 0.42].forEach(function (x) { P.push(ell(x, 0.18, 0.2, 0.03, b)); });
    return P;
  } };

  R.helicopter = { size: [13.0, 3.8], make: function (o) {
    var b = body(o), P = [];
    P.push(poly([[-1.8, 0.8], [1.8, 0.6], [2.6, 1.4], [2.2, 2.4], [0.4, 2.7], [-1.6, 2.4], [-2.2, 1.6]], b));
    P.push(poly([[-2.2, 1.6], [-6.4, 2.2], [-6.4, 2.6], [-1.8, 2.4]], b));
    P.push(poly([[1.2, 1.5], [2.3, 1.5], [2.1, 2.3], [0.6, 2.5]], "paper", { noShadow: true }));
    P.push(rect(-0.3, 2.7, 0.4, 0.5, b)); P.push(line([[-6.2, 3.2], [6.2, 3.2]], 0.16, b));
    P.push(line([[-6.4, 2.3], [-6.4, 3.4]], 0.1, b)); P.push(ell(-6.4, 2.85, 0.15, 0.8, b));
    P.push(line([[-1.4, 0.0], [1.6, 0.0]], 0.08, b)); P.push(line([[-1.0, 0.0], [-0.9, 0.8]], 0.06, b)); P.push(line([[1.2, 0.0], [1.1, 0.7]], 0.06, b));
    return P;
  } };

  /* ------------------------------------------------------------- API */

  var OBJ = {};

  OBJ.sprite = function (name, o) {
    var e = R[name];
    if (!e) throw new Error("TXOBJ: no object named '" + name + "'. Names: " + Object.keys(R).join(", "));
    o = o || {};
    var parts = e.make(o);
    var s = SC.sprite(parts, { kind: name });
    if (e.panel) s.panel = e.panel(o);
    return s;
  };
  OBJ.list = function () { return Object.keys(R).map(function (k) { return { name: k, w: R[k].size[0], h: R[k].size[1] }; }); };
  OBJ.has = function (name) { return !!R[name]; };

  // A wire between two world points at given heights: a catenary drawn in screen space, so
  // a row of poles reads as a line and not as a row of poles.
  OBJ.wire = function (S, a, b, o) {
    o = o || {};
    var ctx = S.ctx, n = 24, sag = o.sag == null ? 0.6 : o.sag;
    ctx.save(); ctx.strokeStyle = o.ink || "#1B1830"; ctx.lineWidth = o.width || 1.2; ctx.beginPath();
    for (var i = 0; i <= n; i++) {
      var t = i / n, X = a[0] + (b[0] - a[0]) * t, Z = a[1] + (b[1] - a[1]) * t;
      var Y = a[2] + (b[2] - a[2]) * t - sag * 4 * t * (1 - t);
      var p = S.project(X, Y, Z);
      if (i === 0) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]);
    }
    ctx.stroke(); ctx.restore();
  };

  // A fence line: posts every `step` metres from (x0,z0) to (x1,z1) with `wires` strands.
  OBJ.fence = function (S, a, b, o) {
    o = o || {};
    var step = o.step || 3, wires = o.wires || 4, h = o.height || 1.3;
    var dx = b[0] - a[0], dz = b[1] - a[1], len = Math.sqrt(dx * dx + dz * dz), n = Math.max(1, Math.round(len / step));
    var post = SC.sprite([line([[0, 0], [0, h]], 0.14, o.body || "ink")]);
    var pts = [];
    for (var i = 0; i <= n; i++) pts.push([a[0] + dx * i / n, a[1] + dz * i / n]);
    // far to near
    pts.sort(function (p, q) { return q[1] - p[1]; });
    for (var w = 1; w <= wires; w++) { var y = h * w / (wires + 0.5); for (var k = 0; k < n; k++) OBJ.wire(S, [pts[k][0], pts[k][1], y], [pts[k + 1][0], pts[k + 1][1], y], { sag: 0.02, ink: o.ink, width: o.width || 0.9 }); }
    for (var j = 0; j < pts.length; j++) { if (o.shadow !== false) S.shadow(post, { X: pts[j][0], Z: pts[j][1], ink: o.ink, alpha: o.shadowAlpha == null ? 0.25 : o.shadowAlpha }); S.sprite(post, { X: pts[j][0], Z: pts[j][1], inks: o.inks }); }
  };

  OBJ.registry = R;
  global.TXOBJ = OBJ;
})(typeof window !== "undefined" ? window : globalThis);
