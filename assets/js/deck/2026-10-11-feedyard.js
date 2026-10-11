/* deck/2026-10-11-feedyard.js — the chassis for the 2026-10-11 deck: West Texas A&M University wins a
 * USDA grant to build a research feedlot beside its Nance Ranch near Canyon, where feeding, health and
 * handling can be tested with "traditional and artificial intelligence-powered approaches"
 * (tx-2026-0207).
 *
 * THE WORLD. lastLight, the house register: a near black Panhandle sky with one warm seam low in the
 * west. THE LIGHT IS THE SUN'S OWN on the evening the release was dated, 6:50 p.m. Central Daylight
 * Time on October 7th, over the Randall County centroid in the committed gazetteer, computed in the
 * run's compute.py from NOAA's solar equations: elevation 6.1 degrees, bearing 259.1, which is engine
 * azimuth -79.1. So the key is low in the west, a touch south of west: on camera LEFT whenever the
 * camera looks north, every lit face is a west face, and every cast runs long to the east.
 *
 * DIRECTIONS. +x is east, +z is south. az runs from +z toward +x, so the key sits at
 * (sin az, ., cos az): with az -79.1 that is west and a little south of the subject, and low.
 *
 * THE HERO OBJECT. One section of a concrete fence line FEED BUNK, built here as `feed_bunk`: a precast
 * J section with its low lip on the pen side (+z), a pipe neck rail over it on posts, the pen's
 * concrete apron, and a windrow of ration in the throat. Its STATE carries the deck: full, eaten down,
 * one head through the rail, a row of them, a plan of them.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `feed_bunk` (above), `feedlot_pens`
 * (a plan of pens on feed alleys, instanced, for the aerial frames) and `ear_tag` (a blank yellow
 * visual tag of the panel kind). Each is built in the kit's conventions so Phase 17 can lift it into
 * assets/js/kit/ unchanged. The cattle are the kit's own `cattle`, Hereford steers.
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, written in the frame's code where figure_bearing.py
 * checks them against figures.json. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("feedyard.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "feedyard",
    light: { az: -79.1, el: 6.1 },
    sky: { preset: "lastLight" },
    ground: "#0A0909",
    material: "#BDB3A2",
    accent: "#E0956A",
    grade: {
      exposure: 0,
      saturation: 1.04,
      contrast: 1.08,
      filmic: true,
      lift: [0.004, 0.003, 0.006],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.85, strength: 0.2, radius: 12 },
      grain: { amount: 0.02, size: 2, seed: 20261011 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261011;
  N.ACCENT = 0xe0956a;       /* dusk gold, the deck's one accent: the ear tag and the AI sentence */
  N.INK = "#EEEAE0";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---------------------------------------------------------------- textures */
  /* THE RATION, a finishing ration seen close: steam flaked corn in pale gold flakes over a darker
   * mixed ground of silage and supplement, with a few longer stems of hay. Tiles every 0.6 m. */
  N.rationTex = function (THREE) {
    if (N._ration) return N._ration;
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(31);
    x.fillStyle = "#6e5a36"; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 2600; i++) { var v = 70 + Math.floor(r() * 60); x.fillStyle = "rgba(" + (v + 30) + "," + (v + 14) + "," + (v - 18) + "," + (0.4 + r() * 0.4).toFixed(2) + ")"; x.beginPath(); x.ellipse(r() * 512, r() * 512, 1 + r() * 4, 0.6 + r() * 2, r() * 3.2, 0, 7); x.fill(); }
    for (var j = 0; j < 900; j++) {
      var cx = r() * 512, cy = r() * 512, a = r() * 3.2, rx = 4 + r() * 7, ry = 2.5 + r() * 4.5;
      var t = 0.75 + r() * 0.25;
      x.fillStyle = "rgba(" + Math.floor(232 * t) + "," + Math.floor(196 * t) + "," + Math.floor(112 * t) + ",0.95)";
      x.beginPath(); x.ellipse(cx, cy, rx, ry, a, 0, 7); x.fill();
      x.strokeStyle = "rgba(120,90,40,0.35)"; x.lineWidth = 0.8; x.stroke();
    }
    for (var k = 0; k < 70; k++) { x.strokeStyle = "rgba(170,150,90," + (0.4 + r() * 0.3).toFixed(2) + ")"; x.lineWidth = 1 + r() * 1.2; x.beginPath(); var x0 = r() * 512, y0 = r() * 512, aa = r() * 6.3, L = 18 + r() * 40; x.moveTo(x0, y0); x.lineTo(x0 + Math.cos(aa) * L, y0 + Math.sin(aa) * L); x.stroke(); }
    var tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace; tx.wrapS = tx.wrapT = THREE.RepeatWrapping; tx.anisotropy = 8;
    N._ration = tx; return tx;
  };
  N.rationBump = function (THREE) {
    if (N._rbump) return N._rbump;
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(37);
    x.fillStyle = "#606060"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < 1400; i++) { var v = 110 + Math.floor(r() * 120); x.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; x.beginPath(); x.ellipse(r() * 256, r() * 256, 2 + r() * 3.5, 1.2 + r() * 2, r() * 3, 0, 7); x.fill(); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; N._rbump = t; return t;
  };
  /* PEN DIRT, the packed manure and soil of a feedlot pen floor: dark brown, hoof pocked, drier and
   * paler on the high ground. A plane texture, tiles every 4 m. */
  N.penTex = function (THREE) {
    if (N._pen) return N._pen;
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(41);
    x.fillStyle = "#4a3a2c"; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 260; i++) { var g = x.createRadialGradient(0, 0, 0, 0, 0, 1); var cx = r() * 512, cy = r() * 512, rr = 20 + r() * 70, v = r();
      x.save(); x.translate(cx, cy); x.scale(rr, rr * (0.5 + r() * 0.6));
      g.addColorStop(0, v < 0.5 ? "rgba(98,80,60,0.35)" : "rgba(36,28,20,0.35)"); g.addColorStop(1, "rgba(0,0,0,0)");
      x.fillStyle = g; x.fillRect(-1, -1, 2, 2); x.restore(); }
    for (var j = 0; j < 2400; j++) { x.fillStyle = "rgba(24,18,12," + (0.25 + r() * 0.35).toFixed(2) + ")"; x.beginPath(); x.ellipse(r() * 512, r() * 512, 1.5 + r() * 2.5, 1 + r() * 2, r() * 3, 0, 7); x.fill(); }
    for (var k = 0; k < 1600; k++) { x.fillStyle = "rgba(150,128,100," + (0.12 + r() * 0.2).toFixed(2) + ")"; x.fillRect(r() * 512, r() * 512, 1 + r() * 1.5, 1 + r() * 1.5); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    N._pen = t; return t;
  };

  /* ---------------------------------------------------------------- the kit models this deck builds */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.feed_bunk) return;
    var conc = K.finish.concrete();
    var pipe = K.mat("fy-pipe", { color: 0x8f9493, roughness: 0.5, metalness: 0.55 });
    var ration = K.mat("fy-ration", { color: 0xffffff, map: N.rationTex(THREE), bumpMap: N.rationBump(THREE), bumpScale: 2.2, roughness: 0.95, metalness: 0 });

    /* A FENCE LINE FEED BUNK, one straight run of precast J section along x, the pen on +z and the feed
     * alley on -z. Sizes from the planning guides a Texas yard builds to: a pen side lip about 0.46 m
     * (18 in) over the apron, a throat about 0.61 m (24 in) wide, a back wall about 0.76 m (30 in)
     * toward the alley, a 3.66 m (12 ft) concrete apron on the pen side, a 4.5 in pipe neck rail on
     * posts every 3.05 m (10 ft). `fill` 0..1 is the ration's windrow height in the throat, `bites`
     * eats gaps out of it where heads have been, `apron` false drops the slab, `rail` false the rail. */
    K.define("feed_bunk", {
      size: [12.2, 1.35, 4.6],
      options: { length: 12.2, fill: 0.8, bites: 0, apron: true, rail: true, railH: 1.25, post: 3.05, seed: 3 },
      note: "A precast concrete fence line feed bunk along x: a J section with its low lip (0.46 m) on the pen side (+z), a 0.61 m throat and a 0.76 m back wall to the feed alley (-z), a 3.66 m concrete apron on the pen side, a pipe neck rail on posts every 3.05 m set in the lip, and a windrow of finishing ration in the throat (fill 0..1; bites eats seeded gaps). Origin on the apron's top at the lip's outer face, centred in x. userData.throat gives the throat's centre line z and the ration top y.",
      make: function (o, r) {
        var g = new THREE.Group(), L = +o.length || 12.2;
        /* the section, in the y,z plane, extruded along x: lip outer face at z = 0 */
        var s = new THREE.Shape();
        s.moveTo(0.0, 0.0); s.lineTo(0.0, 0.40); s.quadraticCurveTo(0.0, 0.46, -0.06, 0.46);
        s.lineTo(-0.12, 0.46); s.lineTo(-0.14, 0.30);
        s.quadraticCurveTo(-0.17, 0.16, -0.42, 0.16); s.quadraticCurveTo(-0.70, 0.16, -0.73, 0.32);
        s.lineTo(-0.75, 0.76); s.lineTo(-0.90, 0.76); s.lineTo(-0.92, 0.0); s.lineTo(0.0, 0.0);
        var pts = s.getPoints(10);
        var shape = new THREE.Shape(pts.map(function (p) { return new THREE.Vector2(p.x, p.y); }));
        var geo = new THREE.ExtrudeGeometry(shape, { depth: L, bevelEnabled: true, bevelThickness: 0.012, bevelSize: 0.012, bevelSegments: 2, curveSegments: 10 });
        geo.translate(0, 0, -L / 2);
        geo.rotateY(-Math.PI / 2);   /* shape x (pen to alley) now runs along z, extrusion along x */
        K.uvBox(geo, 3.0);
        var bunk = new THREE.Mesh(geo, conc); g.add(bunk);
        /* the joints between precast sections, every 3.05 m, a dark hairline down each face */
        var jm = K.mat("fy-joint", { color: 0x2a2724, roughness: 1 });
        for (var jx = -L / 2 + 3.05; jx < L / 2 - 0.1; jx += 3.05) {
          K.box(0.012, 0.77, 0.012, jm, jx, -0.005, -0.927, 0, g);   /* the joint down the back wall's alley face */
          K.box(0.012, 0.47, 0.012, jm, jx, -0.005, 0.006, 0, g);    /* and down the lip's pen face */
        }
        if (o.apron !== false) {
          var ap = new THREE.BoxGeometry(L, 0.15, 3.66); ap.translate(0, -0.075, 1.83); K.uvBox(ap, 3.0);
          g.add(new THREE.Mesh(ap, conc));
          for (var ax = -L / 2 + 3.05; ax < L / 2 - 0.1; ax += 3.05) K.box(0.01, 0.002, 3.66, jm, ax, 0.0, 1.83, 0, g);
        }
        /* the windrow of ration in the throat: a mound along x, a grid in (x, across), ragged on top,
         * with bites eaten out of it where heads have been */
        var fill = Math.max(0, Math.min(1, +o.fill));
        if (fill > 0.02) {
          var nx = Math.max(16, Math.round(L * 10)), nu = 14, pos = [], idx = [], uv = [], bites = [];
          for (var b = 0; b < (o.bites || 0); b++) bites.push([-L / 2 + 0.4 + r() * (L - 0.8), 0.25 + r() * 0.35, 0.25 + r() * 0.5]);
          for (var ix = 0; ix <= nx; ix++) {
            var X = -L / 2 + 0.04 + (L - 0.08) * ix / nx, k = 1;
            bites.forEach(function (bt) { var d = Math.abs(X - bt[0]) / bt[1]; if (d < 1) k = Math.min(k, bt[2] + (1 - bt[2]) * d * d); });
            for (var iu = 0; iu <= nu; iu++) {
              var u = -1 + 2 * iu / nu, w = 0.27;
              var h = fill * 0.24 * k * Math.pow(Math.max(0, 1 - u * u), 0.55) * (0.88 + 0.12 * Math.sin(X * 9.1 + u * 5.3) * Math.cos(X * 2.7 - u));
              pos.push(X, h, u * w); uv.push(X / 0.6, (u * w) / 0.6);
            }
          }
          for (var a = 0; a < nx; a++) for (var c2 = 0; c2 < nu; c2++) { var i0 = a * (nu + 1) + c2, i1 = i0 + nu + 1; idx.push(i0, i0 + 1, i1, i1, i0 + 1, i1 + 1); }
          var rg = new THREE.BufferGeometry();
          rg.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); rg.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
          rg.setIndex(idx); rg.computeVertexNormals();
          var rm = new THREE.Mesh(rg, ration); rm.position.set(0, 0.17, -0.43); g.add(rm);
        }
        if (o.rail !== false) {
          var n = Math.max(2, Math.round(L / o.post) + 1), dx = L / (n - 1);
          for (var q = 0; q < n; q++) {
            var x = -L / 2 + q * dx;
            K.cyl(0.057, 0.057, o.railH - 0.4, pipe, x, 0.44, -0.06, 14, g);
            var dome = new THREE.Mesh(new THREE.SphereGeometry(0.06, 14, 6, 0, Math.PI * 2, 0, Math.PI / 2), pipe); dome.position.set(x, o.railH + 0.04, -0.06); g.add(dome);
          }
          K.bar([-L / 2 - 0.05, o.railH - 0.02, 0.0], [L / 2 + 0.05, o.railH - 0.02, 0.0], 0.0365, pipe, 12, g);
        }
        g.userData.keepOrigin = true;
        g.userData.throat = { z: -0.43, top: 0.17 + fill * 0.24 };
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A PLAN OF PENS ON FEED ALLEYS, for the aerial frames: rows of pens back to back across a feed
     * alley, each pen a dirt floor fenced in pipe on three sides with a bunk along its alley side.
     * rows: [{ n, w, d }] pens per row, pen width along the bunk and depth away from it, in metres.
     * Rows pair across an alley (alley m wide). Fences and bunks are instanced and merged, so a plan
     * of a hundred and more pens stays one draw per material. `lit` lists pen indices (in row order)
     * whose floors carry the lit tone. userData.pens lists every pen's centre [x, z], w, d and row. */
    K.define("feedlot_pens", {
      size: [200, 1.4, 160],
      options: { rows: [{ n: 10, w: 12, d: 40 }, { n: 10, w: 12, d: 40 }], alley: 9, gapRow: 6, floor: 0x46392c, seed: 4 },
      note: "A plan of feedlot pens in rows back to back across feed alleys: each pen a dirt floor fenced in pipe rail on three sides with a concrete fence line bunk on its alley side. rows [{ n, w, d }] in metres, alley width m, gapRow m between pairs. Instanced. userData.pens [{ x, z, w, d, row, i }].",
      make: function (o, r) {
        var g = new THREE.Group(), rows = o.rows || [], pens = [], z = 0, idx = 0;
        var posts = [], rails = [], bunks = [];
        var dirt = K.mat("fy-pendirt", { color: 0xffffff, map: N.penTex(THREE), roughness: 0.97 });
        for (var ri = 0; ri < rows.length; ri++) {
          var R0 = rows[ri], W = R0.n * R0.w, x0 = -W / 2, facing = (ri % 2 === 0) ? -1 : 1;
          /* pens of an even row face +z toward the alley after them; odd rows face -z toward the alley before them */
          var zBunk = facing < 0 ? z + R0.d : z;
          for (var i = 0; i < R0.n; i++) {
            var cx = x0 + (i + 0.5) * R0.w, cz = z + R0.d / 2;
            pens.push({ x: cx, z: cz, w: R0.w, d: R0.d, row: ri, i: idx++ });
            var fl = new THREE.PlaneGeometry(R0.w - 0.2, R0.d - 0.2); fl.rotateX(-Math.PI / 2);
            var uv = fl.attributes.uv; for (var u = 0; u < uv.count; u++) uv.setXY(u, uv.getX(u) * (R0.w / 4) + i * 0.37, uv.getY(u) * (R0.d / 4) + ri * 0.61);
            var fm = new THREE.Mesh(fl, dirt); fm.position.set(cx, 0.012, cz); fm.receiveShadow = true; g.add(fm);
          }
          /* fence posts every 3 m along the back line and every divider */
          var back = facing < 0 ? z : z + R0.d;
          for (var xx = x0; xx <= x0 + W + 0.01; xx += 3) posts.push([xx, back]);
          for (var d = 0; d <= R0.n; d++) { var dxp = x0 + d * R0.w; for (var zz = z; zz <= z + R0.d + 0.01; zz += 3) posts.push([dxp, zz]); rails.push([dxp, z, dxp, z + R0.d]); }
          rails.push([x0, back, x0 + W, back]);
          bunks.push({ x0: x0, x1: x0 + W, z: zBunk, facing: facing });
          z += R0.d + ((ri % 2 === 0) ? (o.alley || 9) : (o.gapRow || 6));
        }
        var pg = new THREE.CylinderGeometry(0.06, 0.06, 1.5, 6); pg.translate(0, 0.75, 0);
        K.instances(pg, pipe, posts.map(function (p) { return [p[0], 0, p[1], 0, 1]; }), g);
        var railMeshes = [];
        rails.forEach(function (rl) { [0.75, 1.4].forEach(function (h) { railMeshes.push(K.bar([rl[0], h, rl[1]], [rl[2], h, rl[3]], 0.035, pipe, 5)); }); });
        if (railMeshes.length) g.add(K.merge(railMeshes, pipe));
        var bm = [];
        bunks.forEach(function (b) {
          var L = b.x1 - b.x0, bx = (b.x0 + b.x1) / 2;
          var m1 = new THREE.Mesh(new THREE.BoxGeometry(L, 0.76, 0.9)); m1.position.set(bx, 0.38, b.z - b.facing * 0.45); bm.push(m1);
          var m2 = new THREE.Mesh(new THREE.BoxGeometry(L, 0.15, 3.66)); m2.position.set(bx, 0.075, b.z + b.facing * 1.83); bm.push(m2);
        });
        bm.forEach(function (m) { K.uvBox(m.geometry, 3.0); });
        if (bm.length) g.add(K.merge(bm, conc));
        g.userData.pens = pens; g.userData.keepOrigin = true; g.userData.depth = z;
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A SURVEY STAKE, the pine lath a crew drives to mark a building's corner: 38 x 9 mm, 1.22 m long with a
     * cut point, driven about 0.25 m, a tail of pale flagging tied near the top. Origin at its foot on the
     * ground. */
    var lath = K.mat("fy-lath", { color: 0xeee2cc, roughness: 0.85, map: K.tex("wood") });
    var flag = K.mat("fy-flag", { color: 0xe8e4d8, roughness: 0.7, side: THREE.DoubleSide });
    K.define("survey_stake", {
      size: [0.04, 0.98, 0.04],
      anchor: "base",
      options: { lean: 0.03, seed: 1 },
      note: "A pine survey lath, 38 x 9 mm, standing 0.97 m out of the ground with a lean, and a 0.4 m tail of pale flagging tied 8 cm from its top. Origin at its foot.",
      make: function (o, r) {
        var g = new THREE.Group(), h = 0.97;
        var stick = K.box(0.038, h, 0.009, lath, 0, 0, 0, 0.001, g);
        var knot = new THREE.Mesh(new THREE.BoxGeometry(0.046, 0.025, 0.017), flag); knot.position.set(0, h - 0.08, 0); g.add(knot);
        for (var k = 0; k < 2; k++) {
          var tail = new THREE.Mesh(new THREE.PlaneGeometry(0.03, 0.4, 1, 6), flag);
          var pp = tail.geometry.attributes.position; for (var i = 0; i < pp.count; i++) { var y = pp.getY(i); pp.setZ(i, Math.pow((0.2 - y) / 0.4, 2) * (0.05 + 0.04 * k)); }
          tail.geometry.computeVertexNormals();
          tail.position.set(0.02 + k * 0.012, h - 0.29, 0.006); tail.rotation.set(0, 0.5 + k * 0.6 + (r() - 0.5) * 0.4, 0.06 - k * 0.1); g.add(tail);
        }
        g.rotation.z = o.lean;
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A LETTER PAGE CLIPPED TO A RAIL, US letter (0.216 x 0.279 m) hung from a 32 mm binder clip whose jaw
     * bites the rail at the origin. The sheet hangs on -y, faces +z, curls its lower edge toward +z by
     * `curl` metres. Blank: anything legible on it is DOM type set on its projected rect, never pixels.
     * userData.page is the sheet mesh. */
    var paper = K.mat("fy-paper", { color: 0xf1ede3, roughness: 0.92, side: THREE.DoubleSide });
    var clipM = K.mat("fy-clip", { color: 0x1a1a1c, roughness: 0.35, metalness: 0.6 });
    var wire = K.mat("fy-wire", { color: 0xc7c9cb, roughness: 0.2, metalness: 1 });
    K.define("clipped_page", {
      size: [0.216, 0.32, 0.05],
      anchor: "base",
      options: { curl: 0.015, seed: 1 },
      note: "A blank US letter sheet hung from a 32 mm black binder clip with two wire handles, the clip's bite at the origin, the sheet on -y facing +z, its lower edge curled toward +z. userData.page is the sheet.",
      make: function (o) {
        var g = new THREE.Group(), W = 0.216, H = 0.279;
        var geo = new THREE.PlaneGeometry(W, H, 6, 14); geo.translate(0, -H / 2 - 0.012, 0);
        var pos = geo.attributes.position;
        for (var i = 0; i < pos.count; i++) { var y = pos.getY(i), t = Math.max(0, (-y - H * 0.7) / (H * 0.3)); pos.setZ(i, 0.004 + o.curl * t * t); }
        geo.computeVertexNormals();
        var page = new THREE.Mesh(geo, paper); g.add(page);
        var jaw = new THREE.Mesh(new THREE.BoxGeometry(0.032, 0.022, 0.012), clipM); jaw.position.set(0, -0.008, 0.008); g.add(jaw);
        [-1, 1].forEach(function (q) { K.bar([q * 0.012, 0.003, 0.012], [q * 0.009, 0.03, 0.022], 0.0012, wire, 6, g); K.bar([q * 0.009, 0.03, 0.022], [0, 0.034, 0.024], 0.0012, wire, 6, g); });
        g.userData.page = page;
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A BLANK PANEL EAR TAG, the large visual tag a feedyard reads across a pen: a rounded yellow
     * panel on a neck, with its stud. Nothing printed on it. Faces +z, hangs from its stud at the
     * origin. */
    var tagM = K.mat("fy-tag", { color: N.ACCENT, roughness: 0.5, metalness: 0, emissive: N.ACCENT, emissiveIntensity: 0.3 });
    K.define("ear_tag", {
      size: [0.075, 0.1, 0.006],
      anchor: "base",
      options: { scale: 1, seed: 1 },
      note: "A blank panel ear tag, 75 x 100 mm, in the deck's accent: a rounded panel on a short neck under a stud, origin at the stud. Nothing is printed on it.",
      make: function (o) {
        var g = new THREE.Group(), sh = new THREE.Shape(), w = 0.0375, h = 0.1;
        sh.moveTo(-0.008, 0); sh.lineTo(0.008, 0); sh.lineTo(0.012, -0.022);
        sh.quadraticCurveTo(w, -0.03, w, -0.05); sh.lineTo(w, -h + 0.012); sh.quadraticCurveTo(w, -h, w - 0.012, -h);
        sh.lineTo(-w + 0.012, -h); sh.quadraticCurveTo(-w, -h, -w, -h + 0.012); sh.lineTo(-w, -0.05);
        sh.quadraticCurveTo(-w, -0.03, -0.012, -0.022); sh.lineTo(-0.008, 0);
        var geo = new THREE.ExtrudeGeometry(sh, { depth: 0.0022, bevelEnabled: true, bevelThickness: 0.0008, bevelSize: 0.0008, bevelSegments: 2 });
        g.add(new THREE.Mesh(geo, tagM));
        var stud = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.01, 12), tagM); stud.rotation.x = Math.PI / 2; stud.position.set(0, -0.004, 0.003); g.add(stud);
        g.scale.setScalar(o.scale || 1);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });
  };

  /* ---------------------------------------------------------------- the place, as calls */
  /* A HEREFORD STEER. The kit animal faces +z, so ry is atan2(dx, dz) of the way it faces: Math.PI faces
   * -z, into a bunk on the alley side, and 0 faces +z, away from it. */
  /* THE HEREFORD WHITE TAKES THE YARD'S WARMTH, not the sky's blue: the kit's white hide and legs are
   * tinted toward a warm neutral in their own material, so the cool fill can't turn them lilac. The
   * light is untouched. */
  N.warmWhites = function (obj) {
    var T = N.T, warm = new T.Color(1.0, 0.92, 0.80);
    obj.traverse(function (m) {
      if (!m.isMesh || !m.material || !m.material.color) return;
      var c = m.material.color, lum = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
      if (lum > 0.55) { m.material = m.material.clone(); m.material.color.multiply(warm); }
    });
    return obj;
  };
  N.steer = function (x, z, o) {
    o = o || {};
    var c = N.warmWhites(N.K.make("cattle", { breed: "hereford", sex: "steer", seed: o.seed || 3 }));
    c.position.set(x, o.y || 0, z); c.rotation.y = o.ry || 0; N.TXT.add(N.R, c); N.TXT.contact(N.R, c);
    return c;
  };
  /* A HERD AT DISTANCE, instanced: one kit steer built once and every mesh of it instanced at each
   * [x, z, ry] in `list`, so a plan of pens can hold hundreds of animals in a handful of draws. */
  N.herd = function (list, o) {
    o = o || {};
    var T = N.T, proto = N.warmWhites(N.K.make("cattle", { breed: "hereford", sex: "steer", seed: o.seed || 3 })), g = new T.Group();
    proto.updateMatrixWorld(true);
    var M = new T.Matrix4(), Q = new T.Quaternion(), S = new T.Vector3(1, 1, 1), P = new T.Vector3(), E = new T.Euler();
    proto.traverse(function (m) {
      if (!m.isMesh) return;
      var im = new T.InstancedMesh(m.geometry, m.material, list.length);
      list.forEach(function (it, i) {
        E.set(0, it[2] || 0, 0); Q.setFromEuler(E); P.set(it[0], 0, it[1]); M.compose(P, Q, S);
        im.setMatrixAt(i, M.clone().multiply(m.matrixWorld));
      });
      im.instanceMatrix.needsUpdate = true; im.castShadow = true; im.receiveShadow = true; g.add(im);
    });
    N.TXT.add(N.R, g);
    return g;
  };
  /* A BLANK TAG IN A STEER'S EAR. The kit ear is the mesh drawn back faced (its outer hide), so the ear
   * nearest a world point is found among those, and the tag hangs from the ear's lower edge, turned to
   * face along the ear. `toward` is the world point the tag should be on the side of (the camera). */
  N.tagEar = function (steer, toward, o) {
    o = o || {};
    var T = N.T; steer.updateMatrixWorld(true);
    var ears = [];
    steer.traverse(function (m) { if (m.isMesh && m.material && m.material.side === T.BackSide) ears.push(m); });
    if (!ears.length) throw new Error("no ear found on the steer");
    var tp = new T.Vector3(toward[0], toward[1], toward[2]), best = null, bd = 1e9;
    ears.forEach(function (e) { var b = new T.Box3().setFromObject(e), c = b.getCenter(new T.Vector3()), d = c.distanceTo(tp); if (d < bd) { bd = d; best = { b: b, c: c }; } });
    var tag = N.K.make("ear_tag", { scale: o.scale || 1 });
    /* hung on the ear's camera face, a hand's width below its centre, so a camera above the head still sees it */
    var dir = tp.clone().sub(best.c), hl = Math.max(1e-6, Math.hypot(dir.x, dir.z));
    tag.position.set(best.c.x + dir.x / hl * 0.05, Math.max(best.b.min.y + 0.01, best.c.y + (o.lift == null ? -0.05 : o.lift)), best.c.z + dir.z / hl * 0.05);
    tag.rotation.y = Math.atan2(dir.x, dir.z);
    N.TXT.add(N.R, tag);
    return tag;
  };
  N.bunk = function (o) {
    o = o || {};
    var b = N.K.make("feed_bunk", Object.assign({ seed: 3 }, o));
    N.TXT.add(N.R, b); N.TXT.contact(N.R, b);
    return b;
  };
  N.penFloor = function (x0, z0, x1, z1, y) {
    var T = N.T, g = new T.PlaneGeometry(x1 - x0, z1 - z0); g.rotateX(-Math.PI / 2);
    var uv = g.attributes.uv; for (var i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * (x1 - x0) / 4, uv.getY(i) * (z1 - z0) / 4);
    var m = new T.Mesh(g, N.K.mat("fy-pendirt", { color: 0xffffff, map: N.penTex(T), roughness: 0.97 }));
    m.position.set((x0 + x1) / 2, y == null ? 0.004 : y, (z0 + z1) / 2); m.receiveShadow = true; N.R.scene.add(m);
    return m;
  };

  /* ---------------------------------------------------------------- the frame, as primitives */
  /* A FEEDYARD YARD LAMP, the one practical the deck allows: a high pressure sodium head on a pole
   * over the feed alley, as feedyards run them for the evening feeding. It is a lamp in the world,
   * never a second sun: it lights a pool on the bunk throat and the near pen, and the deck's one
   * key still sets every long cast. x, z the pole's foot; o.at the point the head aims at. */
  N.yardLight = function (x, z, o) {
    o = o || {};
    var T = N.T, K = N.K, h = o.h || 9, at = o.at || [x, 0, z], g = new T.Group();
    var steel = K.mat("fy-pole", { color: 0x8c8a86, metalness: 0.6, roughness: 0.5 });
    var pg = new T.CylinderGeometry(0.07, 0.11, h, 10); pg.translate(0, h / 2, 0);
    var pole = new T.Mesh(pg, steel); pole.position.set(x, 0, z); g.add(pole);
    var dx = at[0] - x, dz = at[2] - z, d = Math.max(0.01, Math.hypot(dx, dz)), arm = Math.min(1.6, d);
    var hx = x + dx / d * arm, hz = z + dz / d * arm;
    var ag = new T.CylinderGeometry(0.04, 0.04, arm, 8); ag.rotateZ(Math.PI / 2);
    var am = new T.Mesh(ag, steel); am.position.set((x + hx) / 2, h - 0.15, (z + hz) / 2); am.rotation.y = -Math.atan2(dz, dx); g.add(am);
    var head = new T.Mesh(new T.BoxGeometry(0.55, 0.16, 0.34), steel); head.position.set(hx, h - 0.2, hz); head.rotation.y = -Math.atan2(dz, dx); g.add(head);
    var lens = new T.Mesh(new T.PlaneGeometry(0.46, 0.26), new T.MeshBasicMaterial({ color: 0xffd9a0 }));
    lens.rotation.x = Math.PI / 2; lens.rotation.z = Math.atan2(dz, dx); lens.position.set(hx, h - 0.29, hz); g.add(lens);
    g.traverse(function (m) { if (m.isMesh && m !== lens) { m.castShadow = true; m.receiveShadow = true; } });
    N.TXT.add(N.R, g);
    var sp = new T.SpotLight(o.color || 0xffbe78, o.i == null ? 900 : o.i, 0, o.angle || 0.62, o.penumbra == null ? 0.75 : o.penumbra, 2);
    sp.position.set(hx, h - 0.32, hz); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = o.shadow !== false;
    sp.shadow.mapSize.set(2048, 2048); sp.shadow.camera.near = 0.5; sp.shadow.camera.far = h * 4;
    sp.shadow.bias = -0.00002; sp.shadow.normalBias = 0.02;
    N.R.scene.add(sp); N.R.scene.add(sp.target);
    return sp;
  };
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 12, mapSize: map || 2048, radius: 5 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 40, shadowFar: o.shadowFar || 120, normalBias: o.normalBias == null ? 0.02 : o.normalBias };
  };
  /* THE DARK BAND THE TYPE STANDS IN. Light type on the dark field, and the band only ever DARKENS. */
  N.shade = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 60 : o.pad;
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "6,5,8";
    if (bottom != null && a > 0) {
      var fade = o.fade || 180, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + a + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + (a * 0.85) + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  N.post = function (cx, o) {
    o = o || {};
    if (o.a !== 0) N.shade(cx, { a: o.a, to: o.to, fade: o.fade, pad: o.pad });
    var y0 = N.H - (o.veilH || 240), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(6,5,8," + (Math.min(0.5, o.veil == null ? 0.38 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 2.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };
  /* a DOM leader from a label's edge to a projected point, ending short of the glyphs */
  N.leader = function (svg, from, to) {
    var l = document.createElementNS("http://www.w3.org/2000/svg", "line");
    l.setAttribute("x1", from[0]); l.setAttribute("y1", from[1]); l.setAttribute("x2", to[0]); l.setAttribute("y2", to[1]);
    l.setAttribute("stroke", N.INK); l.setAttribute("stroke-width", "2"); l.setAttribute("stroke-opacity", "0.85"); svg.appendChild(l);
    var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", to[0]); c.setAttribute("cy", to[1]); c.setAttribute("r", "5"); c.setAttribute("fill", N.INK); svg.appendChild(c);
  };
  N.labelAt = function (id, p, dx, dy) {
    var s = N.project(N.T, N.R, p), el = document.getElementById(id);
    el.style.left = Math.round(s[0] + (dx || 0)) + "px"; el.style.top = Math.round(s[1] + (dy || 0)) + "px";
    return s;
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#DCD6C8", halo = "rgba(3,4,8,0.6)", halo2 = "rgba(3,4,8,0.45)", acc = "#" + ("000000" + N.ACCENT.toString(16)).slice(-6).toUpperCase();
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#0A0909; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      '.lab.acc { color:' + acc + '; }',
      ".hook, .dek, .tx-site, .kick, .src, .cap, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#DCD6C8" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 80, max: 104, maxLines: 2 });
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
  N.EXPOSURE = 1.0;
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    N.R = TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * N.EXPOSURE * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 32, near: o.near || 0.02, far: o.far || 8000 });
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

  global.CH = N;
})(this);
