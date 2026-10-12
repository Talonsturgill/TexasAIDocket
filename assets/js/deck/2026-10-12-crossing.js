/* deck/2026-10-12-crossing.js — the chassis for the 2026-10-12 deck: UT San Antonio's solar powered
 * flood warning node, a prototype that runs a compressed machine learning model on its own
 * microcontroller and reads the water with four optical sensors mounted at different heights
 * (tx-2026-0141).
 *
 * THE WORLD. floodlit: a black sky after a storm over a low water crossing on the Hill Country edge of
 * Bexar County, lit by the one thing a crossing at night actually has, a cobra head streetlight on the
 * north west bank. The release says flood risk spikes at "low-water crossings in San Antonio" (c16)
 * long before regional alerts, and a flash flood is a night event as often as not, so the deck stands
 * at night under that lamp rather than in the house lastLight register, which four of the last five
 * decks used. THE LIGHT IS THE LAMP'S: azimuth -135 (from the north west), elevation 48, a high cold
 * key, so on a camera looking south every lit face is a north west face and every cast runs to the
 * south east, short. The water carries the lamp and the faint sky.
 *
 * DIRECTIONS. +x is east, +z is south. az runs from +z toward +x, so the key sits at
 * (sin az, ., cos az): with az -135 that is north west of the subject, and high.
 *
 * THE PLACE. One LOW WATER CROSSING, built here: a two lane road running north to south (along z)
 * dips down two asphalt approaches onto a concrete slab laid across a creek channel that runs west to
 * east (along x). A row of culvert mouths on the slab's downstream (east) face. The flood plain is
 * the ground at y = 0, the banks rise to about two metres either side, and the FLOODWATER is one
 * plane at a level each frame sets. Built on TXT.ground's own mesh, displaced, so the ground keeps the
 * engine's surface, its wear and its macro variation.
 *
 * THE HERO OBJECT. One FLOOD NODE, built here as `flood_node`: a galvanized post on a footing, a
 * small solar panel facing south, a grey enclosure holding the microcontroller and its battery, a
 * whip antenna for the long range radio, a rain gauge and a radiation shield on arms, and a sensor
 * rail carrying FOUR optical water level sensors at four heights. Its STATE carries the deck: the
 * water reaches one, two or three of its sensors and each wet sensor's ring lights in the accent,
 * beacon amber, at one intensity, never a ramp.
 * The release names no mounting heights, no housing and no installation site, so every one of these
 * is drawn to illustrate and the deks say so.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `flood_node`, `depth_gauge` (the
 * white water depth marker a Texas crossing carries) and `low_water_crossing` (the slab, approaches
 * and culverts). Each is built in the kit's conventions so Phase 17 can queue the lift.
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, written in the frame's code where figure_bearing.py
 * checks them against figures.json. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("crossing.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "crossing",
    light: { az: -135, el: 48 },
    sky: { preset: "floodlit", horizon: 0x04060a, haze: 0x06080d, glow: 0.12, horizonGlow: 0.06 },   /* the stock floodlit horizon read as a slate haze band (L* 17) on the audition; the storm has cleared and the night is black to the ground */
    ground: "#0C0D10",
    material: "#B9B4A8",
    accent: "#FFA21F",
    grade: {
      exposure: 0,
      saturation: 1.04,
      contrast: 1.08,
      filmic: true,
      lift: [0.003, 0.004, 0.007],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.82, strength: 0.24, radius: 12 },
      grain: { amount: 0.02, size: 2, seed: 20261012 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261012;
  N.ACCENT = 0xffa21f;       /* beacon amber, the deck's one accent: a sensor ring the water has reached. Not red,
                              * because a red ring reads as an alarm that fired, a verdict a prototype with no field
                              * test can't carry (c19). Amber is the flashing beacon on a Texas flood sign. */
  N.INK = "#ECEAE4";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---------------------------------------------------------------- textures */
  /* THE WATER'S SURFACE, a tiling normal map of fine wind ripple crossed with a slow current streak
   * running east, so the floodwater reads as moving water carrying the sky and never as a mirror. */
  N.rippleNormal = function (THREE) {
    if (N._ripple) return N._ripple;
    var S = 256, c = document.createElement("canvas"); c.width = c.height = S; var x = c.getContext("2d");
    var h = new Float32Array(S * S), r = lcg(77);
    var waves = []; for (var k = 0; k < 14; k++) waves.push([1 + Math.floor(r() * 6), Math.floor(r() * 5) - 2, r() * 6.28, 0.3 + r() * 0.7]);
    for (var j = 0; j < S; j++) for (var i = 0; i < S; i++) {
      var u = i / S, v = j / S, s = 0;
      for (var w = 0; w < waves.length; w++) { var q = waves[w]; s += q[3] * Math.sin(6.2832 * (q[0] * u + q[1] * v) + q[2]); }
      s += 0.6 * Math.sin(6.2832 * (2 * v + 0.3 * Math.sin(6.2832 * u * 3)));   /* the current, across x */
      h[j * S + i] = s;
    }
    var id = x.createImageData(S, S), d = id.data;
    for (var jj = 0; jj < S; jj++) for (var ii = 0; ii < S; ii++) {
      var dx = h[jj * S + (ii + 1) % S] - h[jj * S + (ii + S - 1) % S], dy = h[((jj + 1) % S) * S + ii] - h[((jj + S - 1) % S) * S + ii];
      var nx = -dx * 0.5, ny = -dy * 0.5, nz = 1, l = Math.sqrt(nx * nx + ny * ny + nz * nz), o = (jj * S + ii) * 4;
      d[o] = (nx / l * 0.5 + 0.5) * 255; d[o + 1] = (ny / l * 0.5 + 0.5) * 255; d[o + 2] = (nz / l * 0.5 + 0.5) * 255; d[o + 3] = 255;
    }
    x.putImageData(id, 0, 0);
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.NoColorSpace;
    N._ripple = t; return t;
  };
  /* THE GAUGE FACE, a white enamel board with a black tick every half foot and a heavier bar every
   * foot, no numerals (the deck prints none in the world), weathered at the foot where water sits. */
  N.gaugeTex = function (THREE) {
    if (N._gauge) return N._gauge;
    var c = document.createElement("canvas"); c.width = 128; c.height = 1024; var x = c.getContext("2d"), r = lcg(41);
    x.fillStyle = "#e9e7e0"; x.fillRect(0, 0, 128, 1024);
    var feet = 5, px = 1024 / feet;   /* the board spans five feet, top at 0 */
    for (var f = 0; f <= feet * 2; f++) {
      var y = 1024 - f * px / 2, major = f % 2 === 0;
      x.fillStyle = "#121212"; x.fillRect(major ? 10 : 46, y - (major ? 12 : 6), major ? 108 : 72, major ? 24 : 12);
    }
    for (var s = 0; s < 900; s++) { x.fillStyle = "rgba(90,70,40," + (r() * 0.25).toFixed(2) + ")"; x.fillRect(r() * 128, 1024 - Math.pow(r(), 2.2) * 420, 1 + r() * 3, 1 + r() * 3); }
    var g = x.createLinearGradient(0, 1024, 0, 640); g.addColorStop(0, "rgba(70,55,30,0.55)"); g.addColorStop(1, "rgba(70,55,30,0)");
    x.fillStyle = g; x.fillRect(0, 640, 128, 384);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    N._gauge = t; return t;
  };
  /* THE SOLAR CELLS, a dark blue polycrystalline face in a grid of cells with silver bus lines. */
  N.cellTex = function (THREE) {
    if (N._cell) return N._cell;
    var c = document.createElement("canvas"); c.width = 256; c.height = 192; var x = c.getContext("2d"), r = lcg(9);
    x.fillStyle = "#0d1626"; x.fillRect(0, 0, 256, 192);
    for (var j = 0; j < 4; j++) for (var i = 0; i < 6; i++) {
      var X = 6 + i * 41.5, Y = 6 + j * 45;
      x.fillStyle = "rgb(" + (16 + r() * 10 | 0) + "," + (32 + r() * 14 | 0) + "," + (62 + r() * 18 | 0) + ")"; x.fillRect(X, Y, 38, 41);
      x.fillStyle = "rgba(190,200,210,0.55)"; x.fillRect(X, Y + 13, 38, 1); x.fillRect(X, Y + 27, 38, 1);
    }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    N._cell = t; return t;
  };

  /* THE NODE IN PARTS, flood_node's own explode option: the same parts, made by the same calls, laid flat
   * on the ground in rows the way a kit is laid out before assembly. Rows run along x, the front row at
   * +z. userData.rows gives each row's z. */
  N.explodeNode = function (K, THREE, TXT, o) {
    var g = new THREE.Group(), galv = K.finish.galvanized(), conc = K.finish.concrete();
    var alu = K.mat("fc-alu", { color: 0xffffff, map: N.brushedTex(THREE), metalness: 0.75, roughness: 0.38 });
    var box = K.mat("fc-encl", { color: 0xffffff, map: N.enclosureTex(THREE), roughness: 0.5, metalness: 0 });
    var dark = K.mat("fc-dark", { color: 0x16181b, roughness: 0.5, metalness: 0.1 });
    var lens = K.mat("fc-lens", { color: 0x0b0d10, roughness: 0.05, metalness: 0.2, clearcoat: 1, clearcoatRoughness: 0.02, envMapIntensity: 1.6 }, true);
    var white = K.mat("fc-white", { color: 0xe6e6e0, roughness: 0.6 });
    var cells = K.mat("fc-cells", { color: 0xffffff, map: N.cellTex(THREE), roughness: 0.18, metalness: 0.3, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 1.4 }, true);
    var rows = [-0.9, -0.3, 0.25, 0.7];
    /* back row: the post in two lengths, lying along x */
    [[-0.75, 1.3], [0.65, 1.3]].forEach(function (p) { var c = K.mesh(new THREE.CylinderGeometry(0.032, 0.032, p[1], 20), galv, p[0], 0.032, rows[0], g); c.rotation.z = Math.PI / 2; });
    /* second row: the panel flat, the enclosure, the footing ring, the rain gauge on its side */
    var pg = TXT.roundedBox(0.44, 0.32, 0.028, 0.006, alu); pg.rotation.x = -Math.PI / 2; pg.position.set(-1.0, 0.014, rows[1]); g.add(pg);
    var face = new THREE.Mesh(new THREE.PlaneGeometry(0.41, 0.29), cells); face.rotation.x = -Math.PI / 2; face.position.set(-1.0, 0.029, rows[1]); g.add(face);
    K.box(0.24, 0.13, 0.3, box, -0.35, 0, rows[1], 0.012, g);
    K.cyl(0.2, 0.22, 0.12, conc, 0.3, 0, rows[1], 24, g);
    var rg = K.mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.24, 24), white, 0.95, 0.075, rows[1], g); rg.rotation.z = Math.PI / 2;
    var ant = K.mesh(new THREE.CylinderGeometry(0.0045, 0.006, 0.6, 8), dark, 1.35, 0.006, rows[1], g); ant.rotation.z = Math.PI / 2;
    /* third row: the rail, lying along x, its four sensors facing up */
    var lv = (o.levels || [0.2, 0.48, 0.8, 1.16]);
    K.box(1.3, 0.03, 0.05, alu, 0, 0, rows[2], 0.004, g);
    /* front row: the four sensors in a row, the repeated unit, then the six shield plates */
    for (var i = 0; i < 4; i++) {
      var x = -1.05 + i * 0.26;
      K.box(0.065, 0.055, 0.06, dark, x, 0, rows[3], 0.006, g);
      var ln = K.mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.012, 24), lens, x, 0.06, rows[3], g);
      K.mesh(new THREE.TorusGeometry(0.024, 0.006, 8, 28), K.mat("fc-ring", { color: 0x3a3f44, roughness: 0.4, metalness: 0.5 }), x, 0.058, rows[3], g).rotation.x = Math.PI / 2;
    }
    for (var p = 0; p < 6; p++) K.cyl(0.07, 0.075, 0.012, white, 0.12 + p * 0.19, 0, rows[3], 20, g);
    g.userData.rows = rows; g.userData.keepOrigin = true;
    return g;
  };

  /* SURFACES THAT CARRY DETAIL. Measured on the first full render: the enclosure, the rail and the
   * asphalt rendered as flat plates (0.05 to 0.17 of their cells carried any detail). Real ones don't. */
  N.canvasTex = function (THREE, key, w, h, paint, repeat) {
    N._tex = N._tex || {}; if (N._tex[key]) return N._tex[key];
    var c = document.createElement("canvas"); c.width = w; c.height = h; paint(c.getContext("2d"), w, h, lcg(key.length * 131 + 7));
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    if (repeat) t.repeat.set(repeat[0], repeat[1]);
    N._tex[key] = t; return t;
  };
  /* the enclosure's face: moulded polycarbonate tooth, a pale rating label with grey lines, four screw heads */
  N.enclosureTex = function (THREE) {
    return N.canvasTex(THREE, "enclosure", 256, 320, function (x, w, h, r) {
      x.fillStyle = "#c9ccc6"; x.fillRect(0, 0, w, h);
      for (var i = 0; i < 9000; i++) { var v = 140 + Math.floor(r() * 90); x.fillStyle = "rgba(" + v + "," + (v + 3) + "," + (v - 2) + ",0.55)"; x.fillRect(r() * w, r() * h, 2, 2); }
      x.fillStyle = "rgba(70,72,68,0.6)"; for (var k = 0; k < 6; k++) x.fillRect(0, 40 + k * 46, w, 3);
      x.fillStyle = "#e8e6df"; x.fillRect(58, 96, 140, 92); x.strokeStyle = "#9a9a94"; x.lineWidth = 2; x.strokeRect(58, 96, 140, 92);
      x.fillStyle = "#77787a"; for (var j = 0; j < 7; j++) x.fillRect(70, 110 + j * 11, 60 + r() * 56, 4);
      x.fillStyle = "#1c1d1f"; [[20, 20], [w - 20, 20], [20, h - 20], [w - 20, h - 20]].forEach(function (p) { x.beginPath(); x.arc(p[0], p[1], 8, 0, 7); x.fill(); x.strokeStyle = "#8d8f90"; x.lineWidth = 2; x.beginPath(); x.moveTo(p[0] - 5, p[1]); x.lineTo(p[0] + 5, p[1]); x.stroke(); });
      var g = x.createLinearGradient(0, h, 0, h * 0.45); g.addColorStop(0, "rgba(64,56,42,0.7)"); g.addColorStop(1, "rgba(64,56,42,0)"); x.fillStyle = g; x.fillRect(0, h * 0.45, w, h * 0.55);
      /* silt runs from under the lid seam where rain sheets off it, each a thin streak fading downward */
      for (var s = 0; s < 46; s++) { var sx = r() * w, sl = 40 + r() * 200, gs = x.createLinearGradient(0, 30, 0, 30 + sl); gs.addColorStop(0, "rgba(58,52,40," + (0.25 + r() * 0.35).toFixed(2) + ")"); gs.addColorStop(1, "rgba(58,52,40,0)"); x.fillStyle = gs; x.fillRect(sx, 30, 1 + r() * 3, sl); }
    });
  };
  /* satin aluminium, brushed along its length */
  N.brushedTex = function (THREE) {
    return N.canvasTex(THREE, "brushed", 64, 512, function (x, w, h, r) {
      x.fillStyle = "#c4c8cc"; x.fillRect(0, 0, w, h);
      for (var i = 0; i < 700; i++) { var v = 150 + Math.floor(r() * 90); x.fillStyle = "rgba(" + v + "," + v + "," + (v + 4) + ",0.5)"; x.fillRect(r() * w, r() * h, 1, 20 + r() * 120); }
      for (var j = 0; j < 40; j++) { x.fillStyle = "rgba(60,58,52," + (0.15 + r() * 0.3).toFixed(2) + ")"; x.fillRect(r() * w, r() * h, 2 + r() * 4, 2 + r() * 6); }
    });
  };
  /* wet asphalt: aggregate in a dark binder, glints where stones break the surface */
  N.asphaltTex = function (THREE) {
    return N.canvasTex(THREE, "asphalt", 512, 512, function (x, w, h, r) {
      x.fillStyle = "#2a2b2d"; x.fillRect(0, 0, w, h);
      for (var i = 0; i < 30000; i++) { var v = 30 + Math.floor(r() * 40); x.fillStyle = "rgb(" + v + "," + v + "," + (v + 2) + ")"; var sz = 0.6 + r() * 1.6; x.fillRect(r() * w, r() * h, sz, sz * (0.6 + r() * 0.6)); }
      for (var j = 0; j < 500; j++) { x.fillStyle = "rgba(170,172,176," + (0.3 + r() * 0.5).toFixed(2) + ")"; x.fillRect(r() * w, r() * h, 1.5, 1.5); }
      for (var k = 0; k < 14; k++) { x.strokeStyle = "rgba(8,8,9,0.6)"; x.lineWidth = 1 + r() * 2; x.beginPath(); var a = r() * w, b = r() * h; x.moveTo(a, b); for (var q = 0; q < 6; q++) { a += (r() - 0.5) * 60; b += (r() - 0.3) * 50; x.lineTo(a, b); } x.stroke(); }
    }, [1, 1]);
  };

  /* ---------------------------------------------------------------- the kit models this deck builds */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.flood_node) return;
    var galv = K.finish.galvanized(), conc = K.finish.concrete();
    var alu = K.mat("fc-alu", { color: 0xc8ccd0, metalness: 0.8, roughness: 0.35 });
    var box = K.mat("fc-encl", { color: 0xcfd2cc, roughness: 0.45, metalness: 0 });
    var dark = K.mat("fc-dark", { color: 0x16181b, roughness: 0.5, metalness: 0.1 });
    var lens = K.mat("fc-lens", { color: 0x0b0d10, roughness: 0.05, metalness: 0.2, clearcoat: 1, clearcoatRoughness: 0.02, envMapIntensity: 1.6 }, true);
    var white = K.mat("fc-white", { color: 0xe6e6e0, roughness: 0.6 });
    var cells = K.mat("fc-cells", { color: 0xffffff, map: N.cellTex(THREE), roughness: 0.18, metalness: 0.3, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 1.4 }, true);

    /* A FLOOD NODE on its post, at the post's foot (anchor base). Sizes are a prototype's, drawn to
     * illustrate: a 2.6 m galvanized pipe post on a round footing, a sensor rail on the post's front
     * (+z) carrying four optical sensors at `levels` (metres above the footing), an enclosure at 1.5 m,
     * a 0.42 m panel at the top facing +z tilted `tilt` degrees, an antenna, a rain gauge on an arm to
     * -x and a radiation shield on an arm to +x. `wet` is the water's height above the foot: every
     * sensor under it lights its ring in the deck's accent. userData.sensors gives each sensor's lens
     * centre in the model's frame, and userData.enclosure the enclosure's centre. */
    K.define("flood_node", {
      size: [0.9, 2.95, 0.6],
      anchor: "base",
      options: { levels: [0.2, 0.48, 0.8, 1.16], wet: 0, tilt: 32, led: false, explode: false, seed: 5 },
      note: "A solar powered flood warning node on a galvanized post (prototype, drawn to illustrate): footing, sensor rail with four optical water level sensors at `levels` m on the post's +z face, a grey enclosure at 1.5 m with a status lamp, a south facing panel at the top tilted `tilt` deg, a whip antenna, a rain gauge on an arm to -x and a radiation shield on an arm to +x. `wet` m of water lights every sensor under it in the deck accent. userData.sensors and userData.enclosure give positions in the model frame.",
      make: function (o, r) {
        if (o.explode) return N.explodeNode(K, THREE, TXT, o);
        var g = new THREE.Group(), lv = (o.levels || [0.2, 0.48, 0.8, 1.16]).slice(0, 4), wet = +o.wet || 0;
        var foot = K.cyl(0.2, 0.22, 0.12, conc, 0, -0.02, 0, 24, g);
        K.cyl(0.032, 0.032, 2.62, galv, 0, 0.08, 0, 20, g);
        K.cyl(0.036, 0.036, 0.02, galv, 0, 2.7, 0, 20, g);
        /* the sensor rail: an aluminium channel standing off the post on two clamps */
        var railTop = lv[lv.length - 1] + 0.16;
        K.box(0.05, railTop - 0.06, 0.03, alu, 0, 0.06, 0.075, 0.004, g);
        [0.12, railTop - 0.1].forEach(function (y) { K.box(0.09, 0.035, 0.07, galv, 0, y, 0.04, 0.006, g); });
        var sensors = [];
        lv.forEach(function (h, i) {
          var under = wet > h + 0.01;
          K.box(0.065, 0.06, 0.055, dark, 0, h - 0.03, 0.115, 0.006, g);
          var ln = K.mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.012, 24), lens, 0, h, 0.148, g); ln.rotation.x = Math.PI / 2; ln.name = "sensor" + i;
          var amber = N.accentMat(THREE);
          var ring = K.mesh(new THREE.TorusGeometry(0.026, 0.008, 8, 28), under ? amber : K.mat("fc-ring", { color: 0x3a3f44, roughness: 0.4, metalness: 0.5 }), 0, h, 0.149, g);
          if (under) K.box(0.058, 0.05, 0.002, amber, 0, h - 0.025, 0.1435, 0, g);   /* the housing's face lit amber behind its lens */
          ring.userData.txAccent = under; ring.userData.txWear = false;
          if (under) { var halo = new THREE.PointLight(N.ACCENT, 0.12, 0.5, 2); halo.position.set(0, h, 0.2); g.add(halo); }
          sensors.push([0, h, 0.15]);
        });
        /* the cable from the rail up the post to the enclosure */
        K.bar([0.02, railTop - 0.04, 0.06], [0.02, 1.36, 0.06], 0.007, dark, 6, g);
        /* the enclosure, a gasketed polycarbonate box with a lid seam, two cable glands and a lamp */
        K.box(0.24, 0.3, 0.13, box, 0, 1.36, 0.1, 0.012, g).name = "enclosure";
        K.box(0.245, 0.012, 0.135, K.mat("fc-seam", { color: 0x7d807c, roughness: 0.6 }), 0, 1.6, 0.1, 0, g);
        [-0.05, 0.05].forEach(function (x) { K.cyl(0.012, 0.014, 0.03, dark, x, 1.33, 0.1, 10, g); });
        if (o.led === true) K.mesh(new THREE.SphereGeometry(0.009, 12, 8), K.finish.lamp(0x8cff9a, 3.2), 0.085, 1.58, 0.168, g);
        /* the long range radio's whip antenna from the enclosure's top */
        K.cyl(0.014, 0.016, 0.04, dark, 0.07, 1.66, 0.1, 10, g);
        K.cyl(0.0045, 0.006, 0.6, dark, 0.07, 1.7, 0.1, 8, g).name = "antenna";
        /* the radiation shield for temperature and humidity on an arm to +x, a stack of white plates */
        K.bar([0.03, 2.02, 0], [0.32, 2.02, 0], 0.012, galv, 8, g);
        for (var p = 0; p < 6; p++) K.cyl(0.07 - p * 0.002, 0.075 - p * 0.002, 0.012, white, 0.36, 1.92 + p * 0.026, 0, 20, g);
        K.cyl(0.02, 0.02, 0.05, white, 0.36, 2.08, 0, 10, g).name = "shield";
        /* the tipping bucket rain gauge on an arm to -x */
        K.bar([-0.03, 2.22, 0], [-0.3, 2.22, 0], 0.012, galv, 8, g);
        K.cyl(0.075, 0.075, 0.24, white, -0.34, 2.12, 0, 24, g).name = "rain";
        K.cyl(0.078, 0.078, 0.012, alu, -0.34, 2.36, 0, 24, g);
        /* the panel at the top, its face toward +z, tilted back */
        var pg = new THREE.Group(); pg.position.set(0, 2.66, 0.02); pg.rotation.x = -(90 - (o.tilt || 32)) * Math.PI / 180; g.add(pg);
        var frame = TXT.roundedBox(0.44, 0.32, 0.028, 0.006, alu); pg.add(frame);
        var face = new THREE.Mesh(new THREE.PlaneGeometry(0.41, 0.29), cells); face.position.z = 0.0145; face.name = "panel"; pg.add(face);
        K.bar([0, 2.55, 0], [0, 2.66, 0.02], 0.014, galv, 8, g);
        g.userData.sensors = sensors; g.userData.enclosure = [0, 1.51, 0.1]; g.userData.panel = [0, 2.66, 0.02];
        g.userData.foot = foot;
        return g;
      }
    });

    /* A RAIN COLUMN, a clear acrylic measuring tube on an aluminium base with a cap, a hairline tick every
     * 2.5 cm and no numerals, its water filled to `fill` m above the base's top. Lit from behind it glows.
     * Anchor base. */
    K.define("rain_column", {
      size: [0.14, 0.62, 0.14],
      anchor: "base",
      options: { height: 0.56, d: 0.08, fill: 0.4, seed: 1 },
      note: "A clear acrylic rain measuring column on an aluminium base, a tick every 2.5 cm, no numerals, water filled to `fill` m above the base. Anchor base.",
      make: function (o) {
        var g = new THREE.Group(), H = o.height || 0.56, R0 = (o.d || 0.08) / 2, f = Math.max(0, Math.min(H - 0.01, +o.fill || 0));
        K.cyl(R0 + 0.025, R0 + 0.03, 0.03, alu, 0, 0, 0, 32, g);
        var glass = K.mat("fc-acrylic", { color: 0x9aa4ad, roughness: 0.04, metalness: 0, transmission: 0.0, transparent: true, opacity: 0.16, clearcoat: 1, clearcoatRoughness: 0.02, envMapIntensity: 1.2 }, true);
        N.keepAlpha(glass);
        var tube = K.cyl(R0, R0, H, glass, 0, 0.03, 0, 40, g); tube.renderOrder = 3;
        var water = K.mat("fc-rain", { color: 0x4a6a80, emissive: 0x7ea6c8, emissiveIntensity: 0.8, roughness: 0.1, transparent: true, opacity: 0.88 });
        N.keepAlpha(water);
        K.cyl(R0 - 0.004, R0 - 0.004, f, water, 0, 0.032, 0, 40, g);
        K.cyl(R0 - 0.003, R0 - 0.003, 0.004, new THREE.MeshBasicMaterial({ color: 0xf2f8ff }), 0, 0.03 + f - 0.002, 0, 40, g);   /* the meniscus, a bright line */
        /* the empty glass above the water is dark, so the remainder reads as its own band under the rim */
        if (H - f > 0.002) K.cyl(R0 - 0.002, R0 - 0.002, H - f - 0.002, new THREE.MeshBasicMaterial({ color: 0x07090c }), 0, 0.03 + f + 0.003, 0, 40, g);
        /* the graduations, a fine tick every 2.5 cm and a long one every 10 cm, white on the glass */
        var tick = new THREE.MeshBasicMaterial({ color: 0xdfe6ee, fog: false });
        for (var k = 1; 0.025 * k < H - 0.01; k++) { var y = 0.025 * k, big = k % 4 === 0; K.box(big ? 0.04 : 0.018, big ? 0.004 : 0.0025, 0.002, tick, 0, 0.03 + y, R0 + 0.0008, 0, g); }
        K.cyl(R0 + 0.008, R0 + 0.008, 0.014, K.mat("fc-rim", { color: 0xdfe4e8, metalness: 0.9, roughness: 0.2 }), 0, 0.03 + H, 0, 32, g);
        g.userData.waterTop = 0.03 + f; g.userData.top = 0.044 + H;
        return g;
      }
    });

    /* A WATER DEPTH GAUGE, the white board on a post that stands at the edge of a Texas low water
     * crossing: five feet of board with a bar every foot and a tick every half foot, its zero at the
     * slab, on a galvanized U channel post. Anchor base at the post's foot. */
    K.define("depth_gauge", {
      size: [0.2, 2.0, 0.1],
      anchor: "base",
      options: { zero: 0, seed: 2 },
      note: "A white water depth gauge board (five feet, a bar every foot, a tick every half foot, no numerals) on a galvanized U channel post, its zero `zero` m above the post's foot. Anchor base.",
      make: function (o) {
        var g = new THREE.Group(), z0 = +o.zero || 0, H = 1.524;
        K.box(0.05, z0 + H + 0.2, 0.04, galv, 0, -0.1, -0.03, 0.004, g);
        var face = K.mat("fc-gauge", { color: 0xffffff, map: N.gaugeTex(THREE), roughness: 0.55 });
        var board = K.box(0.16, H, 0.014, face, 0, z0, 0.0, 0.003, g);
        g.userData.zero = z0;
        return g;
      }
    });

    /* A LOW WATER CROSSING at caller coordinates (keepOrigin): a 7.3 m road along z dropping down two
     * asphalt approaches from `bank` m to a concrete slab `slab` m high and `span` m long across a
     * channel running along x, with white edge lines, a row of `culverts` pipe mouths on the slab's
     * downstream (+x) face and riprap at their outfall. userData.roadY(z) gives the road surface. */
    K.define("low_water_crossing", {
      size: [9, 2.4, 60],
      options: { span: 12, slab: 0.32, bank: 2.2, ramp: 16, width: 7.3, culverts: 3, seed: 4 },
      note: "A Texas low water crossing at caller coordinates: a concrete slab across a channel running along x, asphalt approaches up to bank height either side along z, white edge lines, culvert mouths on the slab's downstream +x face with riprap. userData.roadY(z) is the road surface height.",
      make: function (o, r) {
        var g = new THREE.Group(); g.userData.keepOrigin = true;
        var W = o.width, S = o.span, s = o.slab, B = o.bank, Rm = o.ramp;
        var roadY = function (z) { var a = Math.abs(z) - S / 2; if (a <= 0) return s; if (a >= Rm) return B; var t = a / Rm; return s + (B - s) * t * t * (3 - 2 * t); };
        g.userData.roadY = roadY;
        /* the slab, a thick concrete deck with its downstream lip */
        var sg = new THREE.BoxGeometry(W + 1.2, s + 0.25, S); sg.translate(0, (s - 0.25) / 2, 0); K.uvBox(sg, 3.0);
        /* the slab after the storm is wet: the same concrete map, darker and glossy */
        var wetConc = K.mat("fc-wetconc", { color: 0x6e6c68, map: K.tex("concrete"), roughness: 0.32, metalness: 0, envMapIntensity: 1.1 });
        g.add(new THREE.Mesh(sg, wetConc));
        /* the approaches: a ribbon following roadY, asphalt on top, raised on an embankment of its own */
        var at = N.asphaltTex(THREE).clone(); at.needsUpdate = true; at.repeat.set(1, 1);
        var asph = K.mat("fc-asph", { color: 0x9a9a9a, map: at, roughness: 0.22, metalness: 0, envMapIntensity: 1.6 });   /* wet asphalt after a storm, dark and glossy */
        var line = K.mat("fc-line", { color: 0x8a8781, roughness: 0.6 });   /* worn paint, dimmer than the post's rim */
        [-1, 1].forEach(function (sd) {
          var n = 40, pos = [], idx = [], z0 = sd * S / 2, z1 = sd * (S / 2 + Rm + 6);
          for (var i = 0; i <= n; i++) {
            var z = z0 + (z1 - z0) * i / n, y = roadY(z) + 0.02;
            pos.push(-W / 2, y, z, W / 2, y, z, -W / 2 - 1.8, Math.min(y - 0.6, y) - 0.9, z, W / 2 + 1.8, y - 1.5, z);
          }
          for (var j = 0; j < n; j++) {
            var a = j * 4;
            if (sd < 0) idx.push(a, a + 1, a + 4, a + 4, a + 1, a + 5); else idx.push(a, a + 4, a + 1, a + 1, a + 4, a + 5);
          }
          var uvs = []; for (var u = 0; u < pos.length; u += 3) uvs.push(pos[u] / 2, pos[u + 2] / 2);   /* metres, so the aggregate is its real size */
          var geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2)); geo.setIndex(idx); geo.computeVertexNormals();
          g.add(new THREE.Mesh(geo, asph));
          /* the white edge lines, a hand's width in from each edge */
          [-W / 2 + 0.25, W / 2 - 0.25].forEach(function (lx) {
            var lp = [], li = [];
            for (var i2 = 0; i2 <= n; i2++) { var z2 = z0 + (z1 - z0) * i2 / n, y2 = roadY(z2) + 0.026; lp.push(lx - 0.07, y2, z2, lx + 0.07, y2, z2); }
            for (var k2 = 0; k2 < n; k2++) { var b = k2 * 2; if (sd < 0) li.push(b, b + 1, b + 2, b + 2, b + 1, b + 3); else li.push(b, b + 2, b + 1, b + 1, b + 2, b + 3); }
            var lg = new THREE.BufferGeometry(); lg.setAttribute("position", new THREE.Float32BufferAttribute(lp, 3)); lg.setIndex(li); lg.computeVertexNormals();
            g.add(new THREE.Mesh(lg, line));
          });
        });
        /* the culvert mouths on the downstream face, dark pipe throats in the concrete */
        var nC = o.culverts || 3;
        for (var c = 0; c < nC; c++) {
          var cz = -S / 2 + S * (c + 0.5) / nC;
          var ring = K.mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.3, 28, 1, true), conc, W / 2 + 0.62, s - 0.52, cz, g); ring.rotation.z = Math.PI / 2;
          var throat = K.mesh(new THREE.CircleGeometry(0.4, 28), K.mat("fc-throat", { color: 0x050505, roughness: 1 }), W / 2 + 0.6, s - 0.52, cz, g); throat.rotation.y = Math.PI / 2;
        }
        /* riprap at the outfall, a skirt of broken stone */
        var rock = K.mat("fc-rock", { color: 0x8b8578, roughness: 0.95 }), list = [];
        for (var q = 0; q < 90; q++) list.push([W / 2 + 1.0 + r() * 3.2, -0.12 + r() * 0.08, (r() - 0.5) * (S + 2), r() * 6.28, 0.18 + r() * 0.26]);
        var rg = new THREE.IcosahedronGeometry(0.5, 1); rg.scale(1, 0.62, 0.85); K.instances(rg, rock, list, g);
        return g;
      }
    });
  };

  /* ---------------------------------------------------------------- the place */
  /* THE BANKS. TXT.ground stays FLAT at y = 0, the flood plain the water covers, because the stage's
   * pool decal and the engine's ground fog assume a flat ground: a displaced ground mesh pokes up out
   * of the decal and stays lit to the horizon (measured on the probe, a pale band of bank at L* 55).
   * The banks are their own mesh on the ground's own textures, rising from the flood plain within
   * `half` m of the channel's line (z = 0) to `bank` m by `half + rise`, with a seeded wander so no bank
   * is a ruler line. Being ordinary geometry, the stage veils them into the dark. Returns height(x, z). */
  N.terrain = function (THREE, TXT, R, o) {
    o = o || {};
    var half = o.half || 9, rise = o.rise || 12, B = o.bank || 2.2, size = o.size || 260, tile = o.tile || 6;
    var floor = o.flooded ? -6 : 0;   /* a flooded frame drops the flood plain out of the way of the reflections */
    /* the frame calls TXT.ground itself and hands the mesh here, so its own code shows the plane it stands on */
    var gnd = o.ground || TXT.ground(R, { surface: o.surface || "dirt", size: size, tile: tile, seed: o.seed || 12, y: floor });
    var r = lcg(o.seed || 12), ph = [r() * 6, r() * 6, r() * 6];
    var h = function (x, z) {
      var w = 1.6 * Math.sin(x * 0.045 + ph[0]) + 0.9 * Math.sin(x * 0.11 + ph[1]);
      var a = Math.abs(z - w) - half; if (a <= 0) return 0;
      var t = Math.min(1, a / rise), v = B * t * t * (3 - 2 * t);
      v += 0.25 * t * Math.sin(x * 0.21 + z * 0.13 + ph[2]);
      /* the road's corridor: the bank never rises through the approaches, it falls away beside them */
      if (o.road) { var ax = Math.abs(x) - o.road.half; if (ax < 2.5) { var ry = o.road.y(z) - 0.25 - Math.max(0, ax) * 0.5; v = Math.min(v, ry); } }
      return Math.max(0, v);
    };
    var geo = new THREE.PlaneGeometry(size, size, 220, 220), p = geo.attributes.position;
    for (var i = 0; i < p.count; i++) { var x = p.getX(i), z = -p.getY(i), y = h(x, z); p.setZ(i, y > 0.001 ? y : floor - 0.05); }
    p.needsUpdate = true; geo.computeVertexNormals();
    var gm = gnd.material, bankMat = new THREE.MeshStandardMaterial({ color: o.tint || 0x55534c, map: gm.map, roughnessMap: gm.roughnessMap,
      bumpMap: gm.bumpMap, bumpScale: gm.bumpScale, roughness: 1, metalness: 0, envMapIntensity: 0.5 });
    var bank = new THREE.Mesh(geo, bankMat); bank.rotation.x = -Math.PI / 2; bank.receiveShadow = true; bank.castShadow = false;
    R.scene.add(bank);
    N.groundMesh = gnd; N.bankMesh = bank; N.heightAt = h;
    return h;
  };
  /* THE FLOODWATER, one sheet at `level` over the whole place: murky, carrying the sky through IBL,
   * rippled by the normal map, a slow current across x. Every bank above it hides it. */
  N.water = function (THREE, R, o) {
    o = o || {};
    var t = N.rippleNormal(THREE).clone(); t.needsUpdate = true; t.repeat.set(o.repeat || 30, o.repeat || 30);
    var m = new THREE.MeshPhysicalMaterial({ color: o.color || 0x120f0b, roughness: o.rough == null ? 0.16 : o.rough, metalness: 0,
      normalMap: t, normalScale: new THREE.Vector2(o.wave || 0.22, o.wave || 0.22), clearcoat: 0.6, clearcoatRoughness: 0.08, envMapIntensity: o.env == null ? 0.55 : o.env });
    if (o.opacity != null) { m.transparent = true; m.opacity = o.opacity; N.keepAlpha(m); }
    var w = new THREE.Mesh(new THREE.PlaneGeometry(o.size || 260, o.size || 260, 1, 1), m);
    w.rotation.x = -Math.PI / 2; w.position.y = o.level; w.receiveShadow = true;
    w.userData.txWear = false;
    R.scene.add(w); N.waterMesh = w;
    return w;
  };
  /* A REFLECTION, the honest cheap kind: the object mirrored about the water's plane under a water
   * surface that is translucent, so the node and the lamp stand on their own image the way a thing does
   * on still floodwater at night. Shadows off on the copy, and it takes no contact. The water stays
   * OPAQUE (murky floodwater hides what is under it), and the copy is drawn after it, translucent and
   * without a depth test, so the image lies ON the surface. Nothing may stand in front of the image
   * on screen, which a frame's composition keeps true. */
  N.mirror = function (obj, level) {
    var m = obj.clone(true);
    m.position.y = 2 * level - obj.position.y; m.scale.y = -obj.scale.y;
    /* only what stands ABOVE the water is reflected: the copy is clipped to below the surface */
    N.R.renderer.localClippingEnabled = true;
    var plane = new N.T.Plane(new N.T.Vector3(0, -1, 0), level);
    m.traverse(function (c) {
      if (c.isMesh) {
        c.castShadow = false; c.receiveShadow = false; c.renderOrder = 5;
        var mm = c.material.clone(); mm.clippingPlanes = [plane]; mm.transparent = true; mm.opacity = (mm.opacity || 1) * (N.reflectK == null ? 0.5 : N.reflectK);
        mm.depthTest = false; mm.depthWrite = false; N.keepAlpha(mm); c.material = mm;
      }
      if (c.isLight) c.visible = false;
    });
    N.R.scene.add(m);
    return m;
  };
  /* the lamp's streak on the water, a soft vertical band of light under the lamp head toward the camera */
  N.streak = function (THREE, R, head, level, o) {
    o = o || {};
    var c = document.createElement("canvas"); c.width = 64; c.height = 256; var g = c.getContext("2d");
    var gr = g.createRadialGradient(32, 128, 2, 32, 128, 128); gr.addColorStop(0, "rgba(235,240,255,0.9)"); gr.addColorStop(0.35, "rgba(200,210,240,0.35)"); gr.addColorStop(1, "rgba(200,210,240,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 256);
    var r = lcg(o.seed || 8); g.globalCompositeOperation = "destination-out";
    g.filter = "blur(1.5px)";
    for (var i = 0; i < 160; i++) { g.fillStyle = "rgba(0,0,0," + (0.2 + r() * 0.5).toFixed(2) + ")"; g.beginPath(); g.ellipse(r() * 64, r() * 256, 4 + r() * 18, 0.8 + r() * 1.8, 0, 0, 6.283); g.fill(); }
    g.filter = "none";
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    var m = new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, opacity: o.opacity || 0.5 });
    m.userData.additive = true; N.keepAlpha(m);
    var pl = new THREE.Mesh(new THREE.PlaneGeometry(o.w || 1.2, o.len || 14), m);
    pl.rotation.x = -Math.PI / 2;
    var cam = R.camera.position, dx = cam.x - head[0], dz = cam.z - head[2], L = Math.sqrt(dx * dx + dz * dz) || 1;
    pl.rotation.z = Math.atan2(dx, dz);
    var mid = (o.len || 14) / 2 + (o.start || 1);
    pl.position.set(head[0] + dx / L * mid, level + 0.012, head[2] + dz / L * mid);
    R.scene.add(pl);
    return pl;
  };
  /* A WAKE where the current meets a standing thing: a pale torn ring on the surface around its foot,
   * drawn out downstream (+x, the current's way), so the waterline on the post is a line a reader sees. */
  N.wake = function (THREE, R, x, z, level, o) {
    o = o || {};
    var c = document.createElement("canvas"); c.width = c.height = 256; var g = c.getContext("2d"), r = lcg(o.seed || 21);
    for (var i = 0; i < 420; i++) {
      var a = r() * 6.283, rad = 34 + r() * 26 + (Math.cos(a) > 0 ? Math.cos(a) * 70 * r() : 0);
      g.fillStyle = "rgba(220,218,206," + (0.12 + r() * 0.5).toFixed(2) + ")";
      g.beginPath(); g.ellipse(128 + Math.cos(a) * rad, 128 + Math.sin(a) * rad * 0.55, 2 + r() * 7, 1 + r() * 2, a, 0, 6.283); g.fill();
    }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    var m = N.keepAlpha(new THREE.MeshStandardMaterial({ map: t, transparent: true, depthWrite: false, roughness: 0.7, opacity: o.opacity || 0.85 }));
    var w = new THREE.Mesh(new THREE.PlaneGeometry(o.size || 1.2, o.size || 1.2), m);
    w.rotation.x = -Math.PI / 2; w.position.set(x + (o.size || 1.2) * 0.12, level + 0.006, z); w.renderOrder = 6;
    R.scene.add(w);
    return w;
  };
  /* THE LAMP BROKEN ON MOVING WATER, a soft pool of ripple glints laid on the surface around a point,
   * fading to nothing at its rim: what a cold lamp does to wind-ruffled floodwater near the camera,
   * which the IBL from a black sky can't. Additive, so it only ever lightens the water it sits on. */
  N.glitter = function (THREE, R, x, z, level, o) {
    o = o || {};
    var S = 512, c = document.createElement("canvas"); c.width = c.height = S; var g = c.getContext("2d"), r = lcg(o.seed || 17);
    for (var i = 0; i < (o.count || 1800); i++) {
      var a = r() * 6.283, d = Math.sqrt(r()) * S / 2, px = S / 2 + Math.cos(a) * d, py = S / 2 + Math.sin(a) * d;
      var fall = Math.pow(1 - d / (S / 2), 1.6), al = fall * (0.15 + r() * 0.6);
      g.fillStyle = "rgba(220,228,245," + al.toFixed(3) + ")"; g.beginPath(); g.ellipse(px, py, 3 + r() * 14, 0.7 + r() * 1.6, 0, 0, 6.283); g.fill();
    }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    var m = new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, opacity: o.opacity || 0.45, fog: false });
    m.userData.additive = true; N.keepAlpha(m);
    var w = new THREE.Mesh(new THREE.PlaneGeometry(o.w || 10, o.d || 6), m);
    w.rotation.x = -Math.PI / 2; w.position.set(x, level + 0.004, z); w.renderOrder = 4; R.scene.add(w);
    return w;
  };
  /* THE WATER'S EDGE ON THE ROAD, a torn lapping line of foam across the approach where the flood
   * meets the asphalt, so the road visibly goes UNDER rather than ending at a dark edge. */
  N.lap = function (THREE, R, roadY, level, halfW, o) {
    o = o || {};
    var z = 0, sgn = o.side || 1;
    for (var k = 0; k < 400; k++) { var zz = sgn * (6 + k * 0.05); if (roadY(zz) >= level) { z = zz; break; } }
    var c = document.createElement("canvas"); c.width = 512; c.height = 64; var g = c.getContext("2d"), r = lcg(o.seed || 31);
    for (var i = 0; i < 900; i++) { var y = 32 + (r() - 0.5) * 24 * Math.pow(r(), 0.5); g.fillStyle = "rgba(214,212,200," + (0.1 + r() * 0.45).toFixed(2) + ")"; g.beginPath(); g.ellipse(r() * 512, y, 2 + r() * 10, 0.6 + r() * 2.2, 0, 0, 6.283); g.fill(); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    var m = N.keepAlpha(new THREE.MeshStandardMaterial({ map: t, transparent: true, depthWrite: false, roughness: 0.7, opacity: o.opacity || 0.85 }));
    var f = new THREE.Mesh(new THREE.PlaneGeometry(halfW * 2 + 1.5, o.w || 0.9), m);
    f.rotation.x = -Math.PI / 2; f.position.set(0, level + 0.008, z); f.renderOrder = 6; R.scene.add(f);
    return z;
  };
  /* foam where the current breaks over the slab's downstream lip, a pale band of streaks */
  N.foam = function (THREE, R, x, z0, z1, y, o) {
    o = o || {};
    var c = document.createElement("canvas"); c.width = 64; c.height = 512; var g = c.getContext("2d"), r = lcg(o.seed || 3);
    for (var i = 0; i < 260; i++) { var a = 0.15 + r() * 0.5; g.fillStyle = "rgba(225,220,205," + a.toFixed(2) + ")"; g.fillRect(r() * 64, r() * 512, 2 + r() * 20, 1 + r() * 3); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    var m = N.keepAlpha(new THREE.MeshStandardMaterial({ map: t, transparent: true, roughness: 0.6, depthWrite: false, opacity: o.opacity || 0.8 }));
    var f = new THREE.Mesh(new THREE.PlaneGeometry(o.w || 1.4, Math.abs(z1 - z0)), m);
    f.rotation.x = -Math.PI / 2; f.position.set(x, y + 0.01, (z0 + z1) / 2); R.scene.add(f);
    return f;
  };

  /* THE STREETLIGHT'S LAMP, the deck's key made visible: a kit streetlight whose head carries an
   * emissive lens and a point light, so the floodwater shows the lamp's streak wherever the camera
   * looks back toward it. The declared key still does the shadows. */
  N.lamp = function (THREE, x, z, o) {
    o = o || {};
    var m = N.K.make("streetlight", { height: o.height || 9 });
    var gy = N.heightAt ? N.heightAt(x, z) : 0;
    m.position.set(x, gy, z); m.rotation.y = o.ry || 0;
    N.TXT.add(N.R, m); N.TXT.contact(N.R, m);
    m.updateMatrixWorld(true);
    var b = new THREE.Box3().setFromObject(m), head = [0, b.max.y - 0.35, 0];
    var reach = o.reach || 3.0, dir = new THREE.Vector3(0, 0, 1).applyAxisAngle(new THREE.Vector3(0, 1, 0), o.ry || 0);
    head = [x + dir.x * reach, b.max.y - 0.4, z + dir.z * reach];
    var pl = new THREE.PointLight(0xe8eeff, o.i == null ? 30 : o.i, o.dist || 45, 2); pl.position.set(head[0], head[1], head[2]); N.R.scene.add(pl);
    var bulb = new THREE.Mesh(new THREE.SphereGeometry(0.16, 16, 10), new THREE.MeshBasicMaterial({ color: 0xf4f7ff })); bulb.scale.y = 0.35;
    bulb.position.set(head[0], head[1] - 0.05, head[2]); N.R.scene.add(bulb);
    m.userData.head = head; (N._lamps = N._lamps || []).push(head);
    return m;
  };
  /* THE RAIN, falling through the frame and caught by the lamps. Measured on the first full render:
   * the night between the subject and the sky read as a flat plate, under the detail line on five
   * frames. A flood frame is a wet night, so the rain is the world's own texture, never a screen: each
   * streak is a crossed pair of thin quads standing in the camera's frustum, as long as one drop falls
   * in a sixtieth of a second, bright near a lamp and dim away from one, and the fog takes the far ones.
   * Called after TXT.frame, since it fills what the camera sees. */
  N.rain = function (THREE, R, o) {
    o = o || {};
    var cam = R.camera; cam.updateMatrixWorld(true);
    var n = o.count || 1100, near = o.near || 1.6, far = o.far || 28, len = o.len || 0.16, w = o.w || 0.0035;
    var a = new THREE.PlaneGeometry(w, len), b = a.clone(); b.rotateY(Math.PI / 2);
    var g = new THREE.BufferGeometry(), pa = a.attributes.position.array, pb = b.attributes.position.array;
    var pos = new Float32Array(pa.length + pb.length); pos.set(pa); pos.set(pb, pa.length);
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    var ia = a.index.array, idx = []; for (var i = 0; i < ia.length; i++) idx.push(ia[i]); for (i = 0; i < ia.length; i++) idx.push(ia[i] + 4);
    g.setIndex(idx);
    var m = new THREE.MeshBasicMaterial({ color: 0xdfe6f2, transparent: true, depthWrite: false, opacity: o.opacity || 0.4 });
    m.userData.additive = true; N.keepAlpha(m);
    var mesh = new THREE.InstancedMesh(g, m, n), r = lcg(o.seed || 1012), M = new THREE.Matrix4(), q = new THREE.Quaternion(), S = new THREE.Vector3(1, 1, 1);
    var lights = (o.lights || N._lamps || []).map(function (h) { return new THREE.Vector3(h[0], h[1], h[2]); });
    var tilt = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0.4).normalize(), o.slant == null ? 0.08 : o.slant);
    var col = new THREE.Color(), p = new THREE.Vector3(), base = o.base == null ? 0.0 : o.base, amber = new THREE.Color(N.ACCENT), glows = (o.glows || N._glows || []).map(function (h) { return new THREE.Vector3(h[0], h[1], h[2]); });
    for (i = 0; i < n; i++) {
      var d = near + Math.pow(r(), 1.6) * (far - near);
      p.set((r() * 2.2 - 1.1), (r() * 2.2 - 1.1), 0.5).unproject(cam).sub(cam.position).normalize().multiplyScalar(d).add(cam.position);
      var lit = base; lights.forEach(function (L) { var k = p.distanceTo(L) / (o.reach || 3.5); lit += 1.2 / (1 + k * k); });
      lit = Math.min(1, lit) * Math.min(1, (d - near) / 1.2 + 0.25);
      /* the open sky carries no rain anyone can see: streaks fade out above the lamp heads */
      lit *= Math.max(0, Math.min(1, (o.ceiling || 7) - p.y) / 3);
      /* and thins where the type sits: the upper part of the frame, so a drop never cuts a letter */
      var ndc = p.clone().project(cam); if (ndc.y > (o.typeLine == null ? 0.05 : o.typeLine)) lit *= 0.3;
      col.setRGB(lit, lit, lit * 1.04);
      /* the drops falling through the amber pool take its colour */
      glows.forEach(function (G) { var k = p.distanceTo(G) / 0.8, a = 0.45 * Math.exp(-k * k); col.r += amber.r * a; col.g += amber.g * a; col.b += amber.b * a; });
      /* the nearest drops cross more of the frame in one exposure, longer and softer */
      S.set(1, 1 + Math.max(0, 5 - d) * 0.5, 1);
      /* no rain inside a closed thing the frame names, a glass column or a room */
      if (o.exclude && o.exclude.some(function (e) { return Math.hypot(p.x - e[0], p.z - e[1]) < e[2]; })) S.set(0, 0, 0);
      M.compose(p, tilt, S); mesh.setMatrixAt(i, M); mesh.setColorAt(i, col);
    }
    mesh.frustumCulled = false; mesh.userData.txWear = false; mesh.castShadow = false; mesh.receiveShadow = false;
    R.scene.add(mesh);
    return mesh;
  };
  /* THE ACCENT AS A LAMP: no fog, no tone curve, so the pixel is the declared #FFA21F.
   * AND EVERY TRANSLUCENT LAYER KEEPS THE FRAMEBUFFER OPAQUE. Measured on the first renders: a
   * translucent water, glow or reflection over the amber wrote framebuffer alpha under 1, the WebGL
   * canvas then composited onto the page at that alpha, and #FFA21F printed at half value, #805000.
   * N.keepAlpha blends colour as usual and adds alpha, so a translucent layer never thins the frame. */
  N.keepAlpha = function (m) {
    var T = N.T;
    m.blending = T.CustomBlending; m.blendEquation = T.AddEquation;
    if (m.userData && m.userData.additive) { m.blendSrc = T.SrcAlphaFactor; m.blendDst = T.OneFactor; }
    else { m.blendSrc = T.SrcAlphaFactor; m.blendDst = T.OneMinusSrcAlphaFactor; }
    m.blendEquationAlpha = T.AddEquation; m.blendSrcAlpha = T.OneFactor; m.blendDstAlpha = T.OneFactor;
    return m;
  };
  N.ACCENT_GAIN = 1.0;
  N.accentMat = function (THREE) {
    if (N._accentMat) return N._accentMat;
    var c = new THREE.Color(N.ACCENT); c.multiplyScalar(N.ACCENT_GAIN);
    N._accentMat = new THREE.MeshBasicMaterial({ color: c, toneMapped: false, fog: false });
    return N._accentMat;
  };
  /* THE PLACE every exterior frame stands in: the banks on the frame's own ground, the floodwater at a
   * level and the crossing's depth gauge. Returns the level. A frame still builds its own subject. */
  N.place = function (THREE, TXT, R, X, gnd, o) {
    o = o || {};
    N.terrain(THREE, TXT, R, { ground: gnd, half: 9, rise: 12, bank: 2.2, seed: 12, flooded: true, road: { half: 4.3, y: X.userData.roadY } });
    N.water(THREE, R, { level: o.level, opacity: o.opacity, wave: o.wave });
    if (o.gauge !== false) { var gg = N.K.make("depth_gauge", { zero: 0.32 }); gg.position.set(-4.6, 0, 5.8); N.TXT.add(R, gg); N.gaugeMesh = gg; }
    return o.level;
  };
  /* the water's level between two of the node's sensors, so `wet` of them are under it */
  N.levelFor = function (wet, levels, lift) {
    var L = levels || [0.2, 0.48, 0.8, 1.16], v = (L[wet - 1] + L[wet]) / 2 + (lift || 0);
    if (L.filter(function (h) { return h < v; }).length !== wet) throw new Error("the water does not reach exactly " + wet + " sensors");
    return v;
  };
  /* SEAT A NODE so its highest wet sensor straddles the waterline: the ring's upper half above the
   * surface, lit, and its lower half under it. The water reaches exactly `wet` sensors. Returns the
   * base height the node stands at and the wet depth to make it with. */
  N.seat = function (wet, level, levels) {
    var L = levels || [0.2, 0.48, 0.8, 1.16], base = level - L[wet - 1] - 0.004;
    if (L.filter(function (h) { return base + h < level + 0.02; }).length !== wet) throw new Error("the seat does not wet exactly " + wet + " sensors");
    return { y: base, wet: level - base + 0.02 };
  };
  /* the amber the water carries where it meets a wet sensor: a soft pool on the surface round the post */
  N.wetGlow = function (THREE, R, x, z, level, o) {
    o = o || {};
    var c = document.createElement("canvas"); c.width = c.height = 128; var g = c.getContext("2d");
    var gr = g.createRadialGradient(64, 64, 2, 64, 64, 64); gr.addColorStop(0, "rgba(255,162,31,1)"); gr.addColorStop(0.32, "rgba(255,162,31,1)"); gr.addColorStop(0.55, "rgba(255,162,31,0.42)"); gr.addColorStop(0.78, "rgba(255,162,31,0.1)"); gr.addColorStop(1, "rgba(255,162,31,0)");   /* the lit water at the post, brightest at the post and falling away: light on water, not a disc */
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    var m = new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, toneMapped: false, fog: false, opacity: o.opacity || 1.0 });
    N.keepAlpha(m);
    var d = new THREE.Mesh(new THREE.PlaneGeometry(o.r || 0.7, (o.r || 0.7) * 0.7), m);
    d.rotation.x = -Math.PI / 2; d.position.set(x, level + 0.01, z); d.renderOrder = 7; R.scene.add(d);
    (N._glows = N._glows || []).push([x, level + 0.3, z]);
    return d;
  };
  N.node = function (x, z, o) {
    o = Object.assign({ seed: 5 }, o || {});
    var m = N.K.make("flood_node", o);
    var gy = o.y != null ? o.y : (N.heightAt ? N.heightAt(x, z) : 0);
    m.position.set(x, gy, z); if (o.ry) m.rotation.y = o.ry;
    N.TXT.add(N.R, m); N.TXT.contact(N.R, m, { y: gy + 0.005 });
    return m;
  };
  N.gauge = function (x, z, o) {
    o = o || {};
    var m = N.K.make("depth_gauge", o);
    var gy = o.y != null ? o.y : (N.heightAt ? N.heightAt(x, z) : 0);
    m.position.set(x, gy, z); if (o.ry) m.rotation.y = o.ry;
    N.TXT.add(N.R, m);
    return m;
  };
  N.crossing = function (o) {
    var m = N.K.make("low_water_crossing", o || {});
    N.TXT.add(N.R, m);
    return m;
  };

  /* ---------------------------------------------------------------- frame furniture */
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  /* a point on a kit model, in world space, from the model's own frame */
  /* a named part of a kit model, in world space, wherever K.make's recentring moved it */
  N.part = function (THREE, obj, name) {
    obj.updateMatrixWorld(true);
    var m = obj.getObjectByName(name); if (!m) throw new Error("no part named " + name);
    var b = new THREE.Box3().setFromObject(m), c = b.getCenter(new THREE.Vector3());
    return [c.x, c.y, c.z];
  };
  N.world = function (THREE, obj, p) {
    obj.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).applyMatrix4(obj.matrixWorld);
    return [v.x, v.y, v.z];
  };
  /* AIM SO A POINT LANDS WHERE THE LAYOUT WANTS IT: from a fixed camera position, solve the look target
   * so that `point` projects to screen (sx, sy). A close camera makes a hand-typed look target swing
   * hundreds of pixels per centimetre, which is what this replaces. Returns the look target. */
  N.aim = function (THREE, R, TXT, from, point, sx, sy, fov) {
    var look = point.slice(), cam = R.camera;
    for (var it = 0; it < 40; it++) {
      TXT.frame(R, { fov: fov, from: from, look: look });
      var q = N.project(THREE, R, point);
      var ex = q[0] - sx, ey = q[1] - sy;
      if (Math.abs(ex) < 0.5 && Math.abs(ey) < 0.5) break;
      cam.updateMatrixWorld(true);
      var right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0), up = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 1);
      var d = new THREE.Vector3(look[0] - from[0], look[1] - from[1], look[2] - from[2]).length();
      var k = 2 * d * Math.tan(fov * Math.PI / 360) / N.H;
      look = [look[0] + right.x * ex * k - up.x * ey * k, look[1] + right.y * ex * k - up.y * ey * k, look[2] + right.z * ex * k - up.z * ey * k];
    }
    return look;
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
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "5,6,9";
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
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(5,6,9," + (Math.min(0.5, o.veil == null ? 0.38 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  /* A RESERVE under one line of type: a feathered dark patch behind the element, so a horizon, a
   * water edge or a lit floor never runs through its glyphs. It only darkens, and only there. */
  N.knock = function (cx, els, a) {
    (els || []).forEach(function (el) {
      if (typeof el === "string") el = document.querySelector(el);
      if (!el) return;
      var r = el.getBoundingClientRect();
      cx.save(); cx.filter = "blur(12px)"; cx.fillStyle = "rgba(5,6,9," + (a == null ? 0.82 : a) + ")";
      cx.fillRect(r.left - 18, r.top - 10, r.width + 36, r.height + 20); cx.restore();
    });
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
    var ink = N.INK, dek = "#D9D6CE", halo = "rgba(3,4,8,0.6)", halo2 = "rgba(3,4,8,0.45)", acc = "#" + ("000000" + N.ACCENT.toString(16)).slice(-6).toUpperCase();
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#07090B; }",
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
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D9D6CE" });
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
