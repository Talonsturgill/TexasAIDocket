/* deck/2026-10-08-nexus.js — the chassis for the 2026-10-08 deck: TxDOT launched the first phase of
 * Project Nexus at Fort Worth Alliance Airport on September 10th, the state's part of the federal
 * eVTOL Integration Pilot Program, and at the kickoff Merlin flew a Cessna Caravan to show software it
 * says handles takeoff, landing and the radio calls to air traffic control (tx-2026-0205).
 *
 * THE WORLD. lastLight, the house register, on an airfield in North Texas: the sun just down in the
 * west, a near black sky with one warm seam low on the key's side, the runway lights coming on. The
 * key rakes in low from the west south west at az -104 and el 6, so every lit face is the west face
 * and every cast runs east, long. That is the light a ramp photographer waits for, and it is the
 * light in which a runway's own lamps become the brightest thing in the frame.
 *
 * DIRECTIONS. +x is east, +z is south. az runs clockwise from +z toward +x, so the key sits at
 * (sin az, ., cos az), west and a little south. The runway lies along z (north and south), centred
 * on x = 0, N.RWY_W wide. Its lamps stand N.EDGE off the centreline every N.LAMP_STEP metres.
 *
 * THE HERO OBJECT. `turboprop_caravan`, a single engine high wing utility turboprop built in the kit's
 * conventions so Phase 17 can lift it into assets/js/kit/ unchanged. It is drawn to the proportions of
 * a 208B, about 12.7 m long with a 15.9 m span and 4.5 m tall, and it is ILLUSTRATIVE: unmarked, no
 * registration, no company livery, and no frame prints a dimension of it. Its STATE carries the deck:
 * parked with the prop stopped, taxiing with the disc turning and its lights on, rolling, in the air.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having no aircraft and nothing of an airfield:
 * `turboprop_caravan`, `airfield_lamp_row`, `windsock` and `control_tower`, below.
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, written in the frame's code where figure_bearing.py
 * checks them against figures.json. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("nexus.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "nexus",
    light: { az: -104, el: 6 },
    sky: { preset: "lastLight", haze: 0x1e2536 },
    ground: "#1A1C21",
    material: "#E4E4DE",
    accent: "#8FE0F0",
    grade: {
      exposure: 0,
      saturation: 1.04,
      contrast: 1.08,
      filmic: true,
      lift: [0.004, 0.005, 0.009],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.78, strength: 0.32, radius: 16 },
      grain: { amount: 0.02, size: 2, seed: 20261008 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261008;
  N.ACCENT = 0x8fe0f0;       /* comal_lit: the taxiway and the machine's path, the one accent */
  N.AMBER = 0xe8a33a;        /* the caution lamps, a light and never the accent */
  N.INK = "#F2EEE6";
  N.RWY_W = 30;              /* the runway's paved width, illustrative, which is the width that takes eight threshold stripes */
  N.EDGE = 15.6;             /* the edge lamps' offset from the centreline */
  N.LAMP_STEP = 60;          /* the edge lamps' spacing */

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---------------------------------------------------------------- geometry helpers */
  /* A LOFT through superellipse sections. Each station is { z, w, top, bot, n }: the half width, the
   * top and bottom heights and the squareness (2 round, 4 a rounded box). Caps both ends. Used for the
   * fuselage, the cowling, the cargo pod and the wheel fairings. */
  N.loft = function (THREE, st, seg) {
    seg = seg || 28; var pos = [], uv = [], idx = [];
    function ring(s) {
      var out = [], mid = (s.top + s.bot) / 2, h = (s.top - s.bot) / 2, e = 2 / (s.n || 2);
      for (var k = 0; k < seg; k++) { var a = k / seg * Math.PI * 2, c = Math.cos(a), si = Math.sin(a);
        out.push([s.w * Math.sign(c) * Math.pow(Math.abs(c), e), mid + h * Math.sign(si) * Math.pow(Math.abs(si), e), s.z]); }
      return out;
    }
    var rings = st.map(ring), L = Math.abs(st[0].z - st[st.length - 1].z) || 1;
    rings.forEach(function (r, i) { r.forEach(function (p, k) { pos.push(p[0], p[1], p[2]); uv.push(Math.abs(st[i].z - st[0].z) / L, k / seg); }); });
    for (var i = 0; i < rings.length - 1; i++) for (var k = 0; k < seg; k++) {
      var a = i * seg + k, b = i * seg + (k + 1) % seg, c = a + seg, d = b + seg; idx.push(a, b, c, b, d, c); }
    [0, rings.length - 1].forEach(function (ri, end) {
      var s = st[ri], ci = pos.length / 3; pos.push(0, (s.top + s.bot) / 2, s.z); uv.push(0.5, end);
      for (var k = 0; k < seg; k++) { var a = ri * seg + k, b = ri * seg + (k + 1) % seg; if (end) idx.push(ci, b, a); else idx.push(ci, a, b); }
    });
    var g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
    g.setIndex(idx); g.computeVertexNormals(); return g;
  };
  /* AN AIRFOIL SURFACE lofted along one axis. Each section is { s, le, chord, y, t } where s is the
   * position along the span axis, le the leading edge's z, chord its length aft (toward -z), y the chord
   * line's height and t the thickness ratio. axis "x" for a wing or a stabiliser, "y" for a fin (then
   * s is the height, y is the x offset). A cambered section: flat bottom, rounded nose, sharp tail. */
  N.foil = function (THREE, secs, axis) {
    var M = 18, pos = [], idx = [];
    function profile(sec) {
      var pts = [];
      for (var i = 0; i <= M; i++) { var x = 1 - i / M, yt = 5 * sec.t * (0.2969 * Math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x * x * x - 0.1036 * x * x * x * x); pts.push([x, yt + 0.02 * Math.sin(Math.PI * x) * (axis === "x" ? 1 : 0)]); }
      for (var j = 1; j < M; j++) { var x2 = j / M, yt2 = 5 * sec.t * (0.2969 * Math.sqrt(x2) - 0.126 * x2 - 0.3516 * x2 * x2 + 0.2843 * x2 * x2 * x2 - 0.1036 * x2 * x2 * x2 * x2); pts.push([x2, -yt2 * (axis === "x" ? 0.55 : 1)]); }
      return pts.map(function (p) { var z = sec.le - p[0] * sec.chord, h = p[1] * sec.chord; return axis === "x" ? [sec.s, sec.y + h, z] : [sec.y + h, sec.s, z]; });
    }
    var rings = secs.map(profile), n = rings[0].length;
    rings.forEach(function (r) { r.forEach(function (p) { pos.push(p[0], p[1], p[2]); }); });
    for (var i = 0; i < rings.length - 1; i++) for (var k = 0; k < n; k++) { var a = i * n + k, b = i * n + (k + 1) % n, c = a + n, d = b + n; idx.push(a, b, c, b, d, c); }
    [0, rings.length - 1].forEach(function (ri, end) { var base = ri * n; for (var k2 = 1; k2 < n - 1; k2++) { if (end) idx.push(base, base + k2, base + k2 + 1); else idx.push(base, base + k2 + 1, base + k2); } });
    var g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx);
    g = g.toNonIndexed(); g.computeVertexNormals(); return g;
  };

  /* ---------------------------------------------------------------- textures */
  /* SKIN: white paint over aluminium, panel lines every metre or so, rivet rows, exhaust soot aft of the
   * stack, oil and dust low on the belly, and the accent cheat line along the side. u runs along the
   * body (0 tail, 1 nose) and v around it. */
  N.skinTex = function (THREE, o) {
    if (N._skin) return N._skin;
    var c = document.createElement("canvas"); c.width = 2048; c.height = 512; var x = c.getContext("2d"), r = lcg(o && o.seed || 11);
    x.fillStyle = "#e9e8e2"; x.fillRect(0, 0, 2048, 512);
    for (var i = 0; i < 900; i++) { x.fillStyle = "rgba(" + (r() < 0.5 ? "60,62,66" : "255,255,255") + "," + (0.015 + r() * 0.03).toFixed(3) + ")"; x.fillRect(r() * 2048, r() * 512, 10 + r() * 90, 4 + r() * 20); }
    x.strokeStyle = "rgba(70,72,78,0.32)"; x.lineWidth = 1.2;
    for (var k = 0; k < 2048; k += 2048 / 13) { x.beginPath(); x.moveTo(k + (r() - 0.5) * 3, 0); x.lineTo(k, 512); x.stroke(); }
    for (var j = 64; j < 512; j += 128) { x.beginPath(); x.moveTo(0, j); x.lineTo(2048, j); x.stroke(); }
    x.fillStyle = "rgba(80,82,86,0.35)";
    for (var k2 = 0; k2 < 2048; k2 += 2048 / 13) for (var y = 6; y < 512; y += 9) x.fillRect(k2 + 5, y, 1.4, 1.4);
    /* the cheat line: the accent band both sides at belt height, with a thin dark keyline */
    [[8, 16], [238, 16]].forEach(function (b) { x.fillStyle = "#2b3a55"; x.fillRect(300, b[0], 1500, b[1]); x.fillStyle = "#2b2f38"; x.fillRect(300, b[0] + b[1] + 3, 1500, 4); });
    /* belly grime and exhaust soot, aft of the stack on the right (v about 0.75) */
    var g = x.createLinearGradient(0, 90, 0, 170); g.addColorStop(0, "rgba(60,55,48,0)"); g.addColorStop(0.5, "rgba(60,55,48,0.25)"); g.addColorStop(1, "rgba(60,55,48,0)");
    x.fillStyle = g; x.fillRect(0, 90, 2048, 80);
    var s = x.createLinearGradient(1860, 0, 1250, 0); s.addColorStop(0, "rgba(28,26,24,0.55)"); s.addColorStop(1, "rgba(28,26,24,0)");
    x.fillStyle = s; x.fillRect(1250, 262, 610, 50);
    /* THE WINDSHIELD, painted where the cowling climbs to the cabin roof (u 0.775 to 0.835, the top
     * of the section from 35 to 145 degrees round), dark glass with a sky sheen and a centre post */
    var wg = x.createLinearGradient(0, 300, 0, 470); wg.addColorStop(0, "#0b1016"); wg.addColorStop(0.5, "#1c2733"); wg.addColorStop(1, "#0b1016");
    x.fillStyle = wg; x.beginPath(); x.moveTo(1590, 306); x.lineTo(1712, 318); x.lineTo(1712, 450); x.lineTo(1590, 462); x.closePath(); x.fill();
    x.fillStyle = "#d9d8d2"; x.fillRect(1590, 380, 122, 7);
    x.strokeStyle = "rgba(20,22,26,0.9)"; x.lineWidth = 3; x.beginPath(); x.moveTo(1590, 306); x.lineTo(1712, 318); x.lineTo(1712, 450); x.lineTo(1590, 462); x.closePath(); x.stroke();
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; N._skin = t; return t;
  };
  /* RUNWAY PAINT on asphalt: a strip texture for a centreline dash, worn, rubber dark over it */
  N.paintMat = function (THREE) {
    return N._paint || (N._paint = new THREE.MeshStandardMaterial({ color: 0xd9d6cc, roughness: 0.82, metalness: 0, polygonOffset: true, polygonOffsetFactor: -2 }));
  };

  /* ---------------------------------------------------------------- the kit models this deck builds */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.turboprop_caravan) return;
    var skin = new THREE.MeshStandardMaterial({ color: 0xffffff, map: N.skinTex(THREE, {}), roughness: 0.34, metalness: 0.06 });
    var white = K.mat("nx-white", { color: 0xe6e5df, roughness: 0.36, metalness: 0.06, side: THREE.DoubleSide });
    var dark = K.mat("nx-dark", { color: 0x23262b, roughness: 0.5, metalness: 0.4 });
    var tyre = K.mat("nx-tyre", { color: 0x141416, roughness: 0.82 });
    var steel = K.mat("nx-steel", { color: 0x8c9096, roughness: 0.35, metalness: 0.85 });
    var glass = K.mat("nx-glass", { color: 0x0c1118, roughness: 0.05, metalness: 0.5, envMapIntensity: 1.6 });
    var bladeM = K.mat("nx-blade", { color: 0x1a1b1e, roughness: 0.55, metalness: 0.2 });
    var tipM = K.mat("nx-tip", { color: 0xd8b24a, roughness: 0.5, metalness: 0.2 });
    var red = K.finish.lamp(0xff2a1e, 6), green = K.finish.lamp(0x2cff6a, 6), strobe = K.finish.lamp(0xfff4e0, 7), land = K.finish.lamp(0xfff0d8, 9);

    /* FUSELAGE STATIONS, tail (-z) to spinner (+z), heights above the ground on its gear */
    var FUS = [
      { z: -6.62, w: 0.04, top: 2.86, bot: 2.76, n: 2 },
      { z: -6.4, w: 0.13, top: 2.93, bot: 2.62, n: 2.4 },
      { z: -5.0, w: 0.44, top: 2.96, bot: 2.04, n: 3 },
      { z: -3.6, w: 0.72, top: 2.99, bot: 1.36, n: 3.6 },
      { z: -2.8, w: 0.81, top: 3.0, bot: 1.06, n: 4 },
      { z: 2.6, w: 0.81, top: 3.0, bot: 1.05, n: 4 },
      { z: 3.2, w: 0.8, top: 2.94, bot: 1.07, n: 3.6 },
      { z: 3.9, w: 0.76, top: 2.6, bot: 1.13, n: 3 },
      { z: 5.0, w: 0.55, top: 2.44, bot: 1.33, n: 2.4 },
      { z: 5.95, w: 0.42, top: 2.31, bot: 1.55, n: 2.2 }
    ];
    var SPIN = [
      { z: 5.98, w: 0.27, top: 2.24, bot: 1.70, n: 2 },
      { z: 6.2, w: 0.22, top: 2.19, bot: 1.75, n: 2 },
      { z: 6.42, w: 0.02, top: 1.98, bot: 1.96, n: 2 }
    ];
    var POD = [
      { z: -3.5, w: 0.08, top: 1.2, bot: 1.12, n: 2 },
      { z: -2.6, w: 0.5, top: 1.12, bot: 0.74, n: 3 },
      { z: 2.4, w: 0.52, top: 1.1, bot: 0.7, n: 3 },
      { z: 3.3, w: 0.18, top: 1.14, bot: 0.98, n: 2 }
    ];
    var HUB = [0, 1.97, 6.12];

    function wing(side) {
      var s = side, secs = [
        { s: s * 0.7, le: 2.72, chord: 1.98, y: 3.02, t: 0.15 },
        { s: s * 4.4, le: 2.70, chord: 1.96, y: 3.08, t: 0.14 },
        { s: s * 7.6, le: 2.45, chord: 1.52, y: 3.17, t: 0.12 },
        { s: s * 7.94, le: 2.38, chord: 1.4, y: 3.18, t: 0.1 }
      ];
      if (s < 0) secs = secs.reverse();
      return N.foil(THREE, secs, "x");
    }
    function stab(side) {
      var s = side, secs = [{ s: s * 0.25, le: -5.05, chord: 1.45, y: 2.82, t: 0.1 }, { s: s * 3.12, le: -5.55, chord: 0.95, y: 2.86, t: 0.08 }];
      if (s < 0) secs = secs.reverse();
      return N.foil(THREE, secs, "x");
    }
    function fin() {
      return N.foil(THREE, [{ s: 2.85, le: -3.7, chord: 2.9, y: 0, t: 0.11 }, { s: 3.4, le: -4.9, chord: 1.75, y: 0, t: 0.11 }, { s: 4.52, le: -5.62, chord: 1.15, y: 0, t: 0.1 }], "y");
    }
    function wheel(parent, x, y, z, rad, wd, pant) {
      var w = new THREE.Mesh(new THREE.CylinderGeometry(rad, rad, wd, 28), tyre); w.rotation.z = Math.PI / 2; w.position.set(x, y, z); parent.add(w);
      var hub = new THREE.Mesh(new THREE.CylinderGeometry(rad * 0.45, rad * 0.45, wd + 0.02, 18), steel); hub.rotation.z = Math.PI / 2; hub.position.set(x, y, z); parent.add(hub);
      if (pant) { var p = new THREE.Mesh(N.loft(THREE, [{ z: z - rad * 1.5, w: 0.04, top: y + 0.06, bot: y, n: 2 }, { z: z - rad * 0.4, w: wd * 0.85, top: y + rad * 0.95, bot: y - rad * 0.2, n: 2.4 },
        { z: z + rad * 0.5, w: wd * 0.85, top: y + rad * 0.95, bot: y - rad * 0.2, n: 2.4 }, { z: z + rad * 1.4, w: 0.05, top: y + 0.3, bot: y + 0.18, n: 2 }], 22), white);
        p.position.x = x; parent.add(p); }
    }
    function propeller(parent, state, r, o) {
      var g = new THREE.Group(); g.position.set(HUB[0], HUB[1], HUB[2]);
      if (state === "disc") {
        /* A TURNING DISC reads as a blur, never as a hoop: a radial gradient in the blade colour, densest
         * at mid blade and faint at the root and the tips, with a barely visible arc where the tips run */
        if (!N._discTex) { var dc = document.createElement("canvas"); dc.width = dc.height = 256; var dx = dc.getContext("2d"), gr = dx.createRadialGradient(128, 128, 18, 128, 128, 128);
          gr.addColorStop(0, "rgba(20,21,24,0)"); gr.addColorStop(0.25, "rgba(20,21,24,0.22)"); gr.addColorStop(0.7, "rgba(20,21,24,0.16)"); gr.addColorStop(0.9, "rgba(216,178,74,0.08)"); gr.addColorStop(0.97, "rgba(20,21,24,0.04)"); gr.addColorStop(1, "rgba(20,21,24,0)");
          dx.fillStyle = gr; dx.fillRect(0, 0, 256, 256); N._discTex = new THREE.CanvasTexture(dc); N._discTex.colorSpace = THREE.SRGBColorSpace; }
        var dm = new THREE.MeshBasicMaterial({ map: N._discTex, transparent: true, depthWrite: false, side: THREE.DoubleSide });
        var disc = new THREE.Mesh(new THREE.CircleGeometry(1.36, 64), dm); g.add(disc);
      } else {
        var a0 = o.propAngle != null ? o.propAngle : r() * 1.2;
        for (var b = 0; b < 3; b++) {
          var bl = new THREE.Group(); bl.rotation.z = a0 + b * Math.PI * 2 / 3;
          /* a twisted, tapered blade as one mesh: a thin section along its length, the chord narrowing and the
           * pitch flattening outboard, the tip rounded, and the last tenth in the yellow tip paint */
          var bg = new THREE.BoxGeometry(0.24, 1.2, 0.045, 1, 16, 1), bp = bg.attributes.position;
          for (var vi = 0; vi < bp.count; vi++) { var vy = bp.getY(vi), t = (vy + 0.6) / 1.2, vx = bp.getX(vi), vz = bp.getZ(vi);
            var w = (0.62 + 0.38 * Math.sin(Math.min(1, t * 1.6) * Math.PI / 2)) * (t > 0.85 ? Math.sqrt(Math.max(0.05, 1 - (t - 0.85) / 0.15)) : 1);
            var ang = 0.85 - 0.6 * t, x2 = vx * w, z2 = vz * (1 - 0.4 * t);
            bp.setXYZ(vi, x2 * Math.cos(ang) - z2 * Math.sin(ang), vy + 0.76, x2 * Math.sin(ang) + z2 * Math.cos(ang)); }
          bg.computeVertexNormals();
          bl.add(new THREE.Mesh(bg, bladeM));
          var tg = new THREE.BoxGeometry(0.2, 0.12, 0.05, 1, 2, 1), tp = tg.attributes.position;
          for (var ti = 0; ti < tp.count; ti++) { var ty = tp.getY(ti), tx = tp.getX(ti) * 0.55, tz = tp.getZ(ti) * 0.6, ta = 0.85 - 0.6 * 0.95; tp.setXYZ(ti, tx * Math.cos(ta) - tz * Math.sin(ta), ty + 1.28, tx * Math.sin(ta) + tz * Math.cos(ta)); }
          tg.computeVertexNormals(); bl.add(new THREE.Mesh(tg, tipM));
          g.add(bl);
        }
      }
      parent.add(g);
    }

    K.define("turboprop_caravan", {
      size: [15.9, 4.6, 13.1],
      options: { state: "parked", prop: "stopped", lights: false, pod: true, pitch: 0 },
      note: "A single engine high wing utility turboprop to a 208B's proportions (about 12.7 m long, 15.9 m span, 4.5 m tall), unmarked, white with a navy cheat line: lofted fuselage, cowling and spinner, braced high wing with struts, strut braced stabiliser, swept fin with a dorsal, fixed tricycle gear with spring main legs and pants, a belly cargo pod, cabin windows, nav lights red left and green right, a red beacon on the fin and landing lights in the wing. prop stopped | disc (turning). lights true lights the nav lights, beacon, strobes and landing lights. pod false drops the cargo pod. pitch tilts the airframe nose up in degrees about the main wheels (for a rotation or a climb). Front is +z, origin on the ground between the main wheels.",
      make: function (o, r) {
        var root = new THREE.Group(), g = new THREE.Group(); root.add(g);
        var body = new THREE.Mesh(N.loft(THREE, FUS, 36), skin); g.add(body);
        var sp = new THREE.Mesh(N.loft(THREE, SPIN, 24), white); g.add(sp);
        /* cowling seam, air inlet under the spinner, exhaust stack on the right */
        var inlet = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.2, 0.3), dark); inlet.position.set(0, 1.55, 5.7); g.add(inlet);
        var ex = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.12, 0.42, 14), dark); ex.rotation.z = Math.PI / 2 - 0.3; ex.position.set(-0.6, 1.95, 5.2); g.add(ex);
        if (o.pod) g.add(new THREE.Mesh(N.loft(THREE, POD, 24), white));
        /* windshield and windows, dark glass proud of the skin */
        [-1, 1].forEach(function (sd) {
          var cw = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.42, 0.62), glass); cw.position.set(sd * 0.805, 2.5, 2.75); g.add(cw);
          for (var k = 0; k < 6; k++) { var wn = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.34, 0.4), glass); wn.position.set(sd * 0.812, 2.47, 1.7 - k * 0.74); g.add(wn); }
        });
        /* the wing, its struts, the flying surfaces */
        [-1, 1].forEach(function (sd) {
          var wm = new THREE.Mesh(wing(sd), white); g.add(wm);
          K.bar([sd * 0.78, 1.32, 1.75], [sd * 3.55, 2.98, 1.85], 0.055, white, 10, g);
          var st = new THREE.Mesh(stab(sd), white); g.add(st);
          /* wingtip lamps: red on the left (+x when facing +z), green on the right */
          var lamp = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 8), o.lights ? (sd > 0 ? red : green) : dark); lamp.position.set(sd * 7.96, 3.18, 2.15); g.add(lamp);
          if (o.lights) { var ll = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 10), land); ll.position.set(sd * 1.9, 3.05, 2.73); g.add(ll); }
        });
        var fm = new THREE.Mesh(fin(), white); g.add(fm);
        var dorsal = new THREE.Mesh(N.foil(THREE, [{ s: 2.9, le: -1.9, chord: 1.9, y: 0, t: 0.06 }, { s: 3.0, le: -3.6, chord: 0.4, y: 0, t: 0.05 }], "y"), white); g.add(dorsal);
        var bc = new THREE.Mesh(new THREE.SphereGeometry(0.08, 12, 8), o.lights ? red : dark); bc.position.set(0, 4.55, -5.65); g.add(bc);
        var tl = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), o.lights ? strobe : dark); tl.position.set(0, 2.88, -6.64); g.add(tl);
        /* antennas on the spine */
        K.bar([0, 3.0, 0.4], [0, 3.32, 0.2], 0.012, dark, 4, g); K.bar([0, 3.0, -1.6], [0, 3.28, -1.8], 0.012, dark, 4, g);
        /* gear: spring steel main legs, a nose leg under the cowl, pants on all three */
        [-1, 1].forEach(function (sd) { K.bar([sd * 0.55, 1.08, 0.35], [sd * 1.78, 0.38, 0.1], 0.06, steel, 10, g); wheel(g, sd * 1.86, 0.38, 0.1, 0.38, 0.2, true); });
        K.bar([0, 1.42, 4.95], [0, 0.34, 5.02], 0.05, steel, 10, g); wheel(g, 0, 0.33, 5.02, 0.33, 0.16, true);
        propeller(g, o.prop, r, o);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        if (o.pitch) { var pv = new THREE.Group(); root.remove(g); pv.add(g); pv.rotation.x = -o.pitch * Math.PI / 180; root.add(pv); }
        root.userData.hub = HUB.slice(); root.userData.keepOrigin = true;
        return root;
      }
    });

    /* AIRFIELD_LAMP_ROW: a row of runway or taxiway lamps along +z from the origin, `length` m at
     * `step` m, each a frangible stem and a lit head in `color`, `side` 1 or -1 offsetting the row. */
    K.define("airfield_lamp_row", {
      size: [0.4, 0.45, 600],
      anchor: "base",
      options: { length: 600, step: 60, color: 0xffe2a8, intensity: 7, fog: true },
      note: "A row of elevated airfield edge lamps along +z from the origin: a dark frangible stem and a lit glass head, `step` m apart over `length` m. color 0xffe2a8 for runway edge white, 0xe8a33a for caution amber, 0x4f8cff for taxiway blue, 0x2cff6a threshold green, 0xff2a1e end red.",
      make: function (o, r) {
        var g = new THREE.Group(), n = Math.floor(o.length / o.step) + 1, stems = [], heads = [];
        for (var i = 0; i < n; i++) { stems.push([0, 0, i * o.step, 0, 1]); heads.push([0, 0.36, i * o.step, 0, 1]); }
        g.add(K.instances(new THREE.CylinderGeometry(0.035, 0.05, 0.34, 8).translate(0, 0.17, 0), dark, stems));
        var hm = K.finish.lamp(o.color, o.intensity); if (o.fog === false) { hm = hm.clone(); hm.fog = false; }
        g.add(K.instances(new THREE.SphereGeometry(0.075, 12, 8), hm, heads));
        return g;
      }
    });

    /* WINDSOCK: a mast with a hoop frame and a striped cone streaming downwind toward `toward` radians */
    K.define("windsock", {
      size: [1.2, 6.4, 4.2],
      anchor: "base",
      options: { toward: 1.2, droop: 0.18 },
      note: "An airfield windsock: a 5.5 m galvanised mast on a concrete pad, a swivel hoop and a five band orange and white cone about 3.6 m long, streaming toward `toward` radians about y and drooping by `droop`.",
      make: function (o, r) {
        var g = new THREE.Group(), galv = K.finish.galvanized();
        K.box(1.0, 0.15, 1.0, K.finish.concrete(), 0, 0, 0, 0.02, g);
        K.cyl(0.05, 0.06, 5.5, galv, 0, 0.15, 0, 10, g);
        var sock = new THREE.Group(); sock.position.y = 5.55; sock.rotation.y = o.toward;
        var hoop = new THREE.Mesh(new THREE.TorusGeometry(0.46, 0.025, 8, 24), galv); hoop.position.z = 0.1; sock.add(hoop);
        var bands = 5, len = 3.6, or = K.mat("nx-sock-o", { color: 0xe8662a, roughness: 0.85, side: THREE.DoubleSide }), wh = K.mat("nx-sock-w", { color: 0xe8e4da, roughness: 0.85, side: THREE.DoubleSide });
        for (var b = 0; b < bands; b++) { var r0 = 0.45 - b * 0.055, r1 = 0.45 - (b + 1) * 0.055, cone = new THREE.Mesh(new THREE.CylinderGeometry(r1, r0, len / bands, 20, 1, true), b % 2 ? wh : or);
          cone.rotation.x = Math.PI / 2; cone.position.set(0, -o.droop * (b + 0.5) * 0.35, 0.1 + (b + 0.5) * len / bands); sock.add(cone); }
        g.add(sock);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* CONTROL_TOWER: a precast shaft and a glazed octagonal cab with a lit console glow, `height` m to
     * the cab floor. Front +z. */
    K.define("control_tower", {
      size: [14, 48, 14],
      anchor: "base",
      options: { height: 38, lit: true },
      note: "An airport traffic control tower: a base building, a tapered precast shaft with a stair window strip, a catwalk, an octagonal cab glazed all round and canted out, a dark roof with antennas and a beacon. lit true glows the cab's consoles amber.",
      make: function (o, r) {
        var g = new THREE.Group(), conc = K.mat("nx-tower", { color: 0xffffff, map: K.tex("concrete", { color: "#b9b4aa" }), roughness: 0.9 });
        K.box(16, 5, 12, conc, 0, 0, 3, 0.05, g);
        var sh = new THREE.Mesh(new THREE.CylinderGeometry(3.0, 3.6, o.height - 5, 8), conc); sh.position.y = 5 + (o.height - 5) / 2; sh.rotation.y = Math.PI / 8; g.add(sh);
        var strip = new THREE.Mesh(new THREE.BoxGeometry(0.6, o.height - 8, 0.2), K.finish.lamp(0xffc98a, o.lit ? 0.9 : 0)); strip.position.set(0, 5 + (o.height - 5) / 2, 3.35); g.add(strip);
        var deck = new THREE.Mesh(new THREE.CylinderGeometry(5.4, 4.2, 1.2, 8), conc); deck.position.y = o.height + 0.6; deck.rotation.y = Math.PI / 8; g.add(deck);
        var cab = new THREE.Mesh(new THREE.CylinderGeometry(5.6, 4.9, 4.2, 8, 1, true), K.mat("nx-cabglass", { color: 0x1b2632, roughness: 0.06, metalness: 0.6, emissive: o.lit ? 0x8a5a2a : 0x000000, emissiveIntensity: o.lit ? 0.55 : 0, side: THREE.DoubleSide, envMapIntensity: 1.4 }));
        cab.position.y = o.height + 3.3; cab.rotation.y = Math.PI / 8; g.add(cab);
        for (var k = 0; k < 8; k++) { var a = k / 8 * Math.PI * 2 + Math.PI / 8, mull = new THREE.Mesh(new THREE.BoxGeometry(0.18, 4.3, 0.18), dark); mull.position.set(Math.sin(a) * 5.25, o.height + 3.3, Math.cos(a) * 5.25); g.add(mull); }
        var roof = new THREE.Mesh(new THREE.CylinderGeometry(4.6, 6.2, 1.0, 8), dark); roof.position.y = o.height + 5.9; roof.rotation.y = Math.PI / 8; g.add(roof);
        K.cyl(0.08, 0.1, 5, steel, 1.2, o.height + 6.4, 0.8, 6, g); K.cyl(0.08, 0.1, 3.5, steel, -1.6, o.height + 6.4, -0.6, 6, g);
        var bcn = new THREE.Mesh(new THREE.SphereGeometry(0.3, 12, 8), red); bcn.position.set(1.2, o.height + 11.5, 0.8); g.add(bcn);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });
  };

  /* ---------------------------------------------------------------- the place, as primitives */
  /* Each is a primitive a frame places where its own composition wants it. None draws a frame. */
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  /* THE INFIELD, dry North Texas grass in October */
  N.infield = function (o) { o = o || {}; return N.TXT.ground(N.R, { surface: "grass", size: o.size || 9000, tile: o.tile || 7, seed: o.seed || 31, color: o.color || 0x6f6a4c }); };
  /* THE RUNWAY: asphalt `length` m along z from z0 to z0 - length (north is -z), with its paint: edge
   * stripes, a dashed centreline, threshold bars at the south end, and its lamps. */
  N.runway = function (o) {
    o = o || {}; var T = N.T, K = N.K, len = o.length || 3000, z0 = o.z0 == null ? 400 : o.z0, w = N.RWY_W;
    var a = new T.Mesh(new T.PlaneGeometry(w, len), new T.MeshStandardMaterial({ color: 0xffffff, map: N.asphaltTex(T, len), roughness: 0.88, metalness: 0 }));
    a.rotation.x = -Math.PI / 2; a.position.set(0, 0.02, z0 - len / 2); a.receiveShadow = true; a.userData.txWear = false; N.TXT.add(N.R, a);
    var paint = N.paintMat(T), g = new T.Group();
    if (o.edges !== false) [-1, 1].forEach(function (sd) { var e = new T.Mesh(new T.BoxGeometry(0.9, 0.02, len), paint); e.position.set(sd * (w / 2 - 1.2), 0.035, z0 - len / 2); g.add(e); });
    for (var z = z0 - 20; z > z0 - len; z -= 60) { var d = new T.Mesh(new T.BoxGeometry(0.9, 0.02, 36), paint); d.position.set(0, 0.035, z - 18); g.add(d); }
    /* THE THRESHOLD STRIPES, `stripes` of them in two groups either side of the centreline, 1.8 m wide and
     * 30 m long, a stripe numbered `accentStripe` (1 from the west edge) painted in the accent */
    if (o.threshold !== false) { var nS = o.stripes || 8, half = nS / 2, pitch = 3.0;
      for (var k = 0; k < nS; k++) { var sideK = k < half ? -1 : 1, j = k < half ? half - 1 - k : k - half, x = sideK * (2.4 + j * pitch + 0.9);
        var acc = o.accentStripe === k + 1, t = new T.Mesh(new T.BoxGeometry(1.8, 0.02, 30), acc ? N.accentPaint(T) : paint); t.position.set(x, acc ? 0.037 : 0.035, z0 - 21); g.add(t); } }
    g.children.forEach(function (m) { m.receiveShadow = true; m.userData.txWear = false; }); N.TXT.add(N.R, g);
    if (o.lamps !== false) [-1, 1].forEach(function (sd) {
      var row = K.make("airfield_lamp_row", { length: len - 40, step: N.LAMP_STEP, color: 0xffe2a8, intensity: o.lampI || 7, fog: o.lampFog !== false }); row.position.set(sd * N.EDGE, 0, z0 - len + 20); N.TXT.add(N.R, row);
      var amber = K.make("airfield_lamp_row", { length: 600, step: N.LAMP_STEP, color: N.AMBER, intensity: o.lampI || 7 }); amber.position.set(sd * N.EDGE, 0.002, z0 - len + 20); N.TXT.add(N.R, amber);
      var thr = K.make("airfield_lamp_row", { length: w, step: 3, color: 0x2cff6a, intensity: 6 }); thr.rotation.y = Math.PI / 2; thr.position.set(-w / 2, 0, z0 + 2); N.TXT.add(N.R, thr);
    });
    return g;
  };
  N.accentPaint = function (THREE) { return N._apaint || (N._apaint = new THREE.MeshStandardMaterial({ color: 0x8fe0f0, roughness: 0.8, metalness: 0, emissive: 0x8fe0f0, emissiveIntensity: 0.22, polygonOffset: true, polygonOffsetFactor: -3 })); };
  /* THE RADIO PATH, drawn to illustrate: one fine tube in the accent along a shallow arc from `a` to `b`
   * ([x, y, z]), rising `lift` metres at mid span, `r` metres thick. No rings, no glow halo. */
  N.callPath = function (a, b, o) {
    o = o || {}; var T = N.T, pts = [], n = 64, lift = o.lift == null ? 6 : o.lift;
    for (var i = 0; i <= n; i++) { var t = i / n; pts.push(new T.Vector3(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + lift * 4 * t * (1 - t), a[2] + (b[2] - a[2]) * t)); }
    var m = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts), 256, o.r || 0.05, 8, false),
      new T.MeshBasicMaterial({ color: new T.Color(0x8fe0f0).multiplyScalar(o.glow == null ? 0.9 : o.glow), fog: false, toneMapped: false }));
    m.userData.txWear = false; m.castShadow = false; N.TXT.add(N.R, m); m.castShadow = false; return m;
  };
  /* A YEAR BAR across the runway at z, inset lamps every `step` m in the accent, unfogged so the stage keeps it */
  N.yearBar = function (z, o) {
    o = o || {}; var T = N.T, list = [], w = N.RWY_W - 2, step = o.step || 1.5, h = o.h || 0.9;
    for (var x = -w / 2; x <= w / 2 + 0.01; x += step) list.push([x, h / 2, z, 0, 1]);
    var mat = new T.MeshBasicMaterial({ color: new T.Color(0x8fe0f0).multiplyScalar(o.glow || 1.6), fog: false, toneMapped: false });
    var im = N.K.instances(new T.CylinderGeometry(0.22, 0.22, h, 10), mat, list); im.userData.txWear = false; N.TXT.add(N.R, im); im.castShadow = false; im.receiveShadow = false; return im;
  };
  /* ASPHALT, a long strip texture: aggregate tooth, darker rubber down the centre third at the
   * touchdown zone, sealed cracks. u across, v along. */
  N.asphaltTex = function (THREE, len) {
    var c = document.createElement("canvas"); c.width = 256; c.height = 2048; var x = c.getContext("2d"), r = lcg(77);
    x.fillStyle = "#3a3b3d"; x.fillRect(0, 0, 256, 2048);
    for (var i = 0; i < 26000; i++) { var v = 40 + Math.floor(r() * 50); x.fillStyle = "rgba(" + v + "," + v + "," + (v + 2) + "," + (0.25 + r() * 0.4).toFixed(2) + ")"; x.fillRect(r() * 256, r() * 2048, 1 + r() * 2, 1 + r() * 2); }
    var g = x.createLinearGradient(0, 0, 256, 0); g.addColorStop(0, "rgba(10,10,12,0)"); g.addColorStop(0.35, "rgba(10,10,12,0.42)"); g.addColorStop(0.65, "rgba(10,10,12,0.42)"); g.addColorStop(1, "rgba(10,10,12,0)");
    x.fillStyle = g; x.fillRect(0, 1500, 256, 548);
    x.strokeStyle = "rgba(14,14,16,0.55)"; x.lineWidth = 1.4;
    for (var k = 0; k < 40; k++) { var px = r() * 256, py = r() * 2048; x.beginPath(); x.moveTo(px, py); for (var s = 0; s < 6; s++) { px += (r() - 0.5) * 30; py += 10 + r() * 30; x.lineTo(px, py); } x.stroke(); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1, Math.max(1, len / 400)); t.anisotropy = 8; return t;
  };
  /* THE RAMP, a concrete apron centred at [x, z], `w` by `d`, joints in metres */
  N.apron = function (x, z, w, d, o) { o = o || {}; var g = N.TXT.ground(N.R, { surface: "concrete", size: Math.max(w, d), tile: o.tile || 7.5, seed: o.seed || 19, joints: true, y: 0.03 }); g.position.x = x; g.position.z = z; g.scale.set(w / Math.max(w, d), 1, d / Math.max(w, d)); return g; };
  N.grass = function (area, o) { o = o || {}; return N.TXT.scatter(N.R, { kind: "grass", count: o.count || 9000, area: area, avoid: o.avoid, seed: o.seed || 9, scale: o.scale || [0.3, 0.6], colors: [0x8a8058, 0x6e6a48, 0x9c9066] }); };
  N.plane = function (o) { return N.K.make("turboprop_caravan", Object.assign({ seed: 3 }, o || {})); };
  N.installAll = function () { N.installKit(N.K, N.T, N.TXT); };

  /* ---------------------------------------------------------------- the frame shell */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 30, mapSize: map || 2048, radius: 5 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 90, shadowFar: o.shadowFar || 220, normalBias: o.normalBias == null ? 0.02 : o.normalBias };
  };
  /* THE DARK BAND THE TYPE STANDS IN. Light type on the dark field, and the band only ever DARKENS:
   * a navy black gradient from the top edge to below the dek, under 0.55 alpha. */
  N.shade = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 60 : o.pad;
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "6,8,14";
    if (bottom != null && a > 0) {
      var fade = o.fade || 180, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + a + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + (a * 0.85) + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  /* THE POST STEPS every frame takes before its grade: the dark band under the type, a dark band
   * under the footer, the dither. The frame still calls TXDECK.finish itself, last. */
  N.post = function (cx, o) {
    o = o || {};
    if (o.a !== 0) N.shade(cx, { a: o.a, to: o.to, fade: o.fade, pad: o.pad });
    var y0 = N.H - (o.veilH || 240), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(6,8,14," + (Math.min(0.5, o.veil == null ? 0.38 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 2.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };

  /* THE SHELL EVERY FRAME SHARES: the type styles, the furniture, the fit of the hook. Light type on
   * the dark field with a dark halo. */
  N.CSS = function () {
    var ink = N.INK, dek = "#E4DFD5", halo = "rgba(4,6,10,0.6)", halo2 = "rgba(4,6,10,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#0B0D12; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; color:' + ink + '; white-space:nowrap; z-index:12; }',
      '.lab.acc { color:#8FE0F0; }',
      ".hook, .dek, .tx-site, .kick, .src, .cap, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#E4DFD5" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 96, max: 128, maxLines: 2 });
    N.follow();
  };
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE;
    await document.fonts.ready;
    N.start(o);
    var TXT = typeof bench === "function" ? bench(THREE) : bench, K = initKit(THREE, TXT);
    N.K = K; N.TXT = TXT; N.installKit(K, THREE, TXT);
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
  };
  /* THE DECK'S EXPOSURE, one number for all nine, through the renderer's tone curve */
  N.EXPOSURE = 1.0;
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    N.R = TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * N.EXPOSURE * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 32, near: o.near || 0.05, far: o.far || 12000 });
    return N.R;
  };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) {
      d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px";
    });
  };
  N.glCanvas = function () {
    var c = document.createElement("canvas");
    c.width = N.W * 2; c.height = N.H * 2;
    return c;
  };
  N.develop = function (shot, glCanvas) {
    if (!shot || !shot.ok) throw new Error("the GPU frame came back black: " + JSON.stringify(shot));
    var cx = document.getElementById("art").getContext("2d");
    cx.scale(2, 2);
    cx.drawImage(glCanvas, 0, 0, N.W, N.H);
    return cx;
  };

  global.NX = N;
})(this);
