/* deck/2026-10-15-transcript.js — the chassis for the 2026-10-15 deck: a deposition transcript made
 * with an AI platform, struck by a Montgomery County trial court because no certified shorthand
 * reporter prepared it, and argued before the Supreme Court of Texas on October 6th, 2026, which has
 * not ruled (tx-2026-0127).
 *
 * THE WORLD. lastLight, the house register: the sun just down in the west south west, one warm seam
 * low on the key's side, a near black sky. THE LIGHT is azimuth -58, elevation 7: a low raking key
 * from the west south west, so every lit face is a west or south face and every cast runs long to the
 * east north east. The case is undecided, and the hour after sunset is the light of a question still
 * open. The 9:00 a.m. argument is never shown outdoors: the court frames are windowless rooms.
 *
 * DIRECTIONS. +x is east, +z is south. az runs from +z toward +x, so the key sits at
 * (sin az, ., cos az): with az -58 that is west south west of the subject, and low.
 *
 * TWO PLACES ONE CASE TRAVELLED BETWEEN, both drawn to illustrate. MONTGOMERY COUNTY: loblolly pine,
 * iron sandy clay and pine straw, a one storey brick office whose corner room holds the deposition,
 * and a classical county courthouse (the kit's). THE COURT: a flamed granite stair with one riser per
 * calendar month from the strike to the argument (figures.json months_struck_to_argued), climbing to a
 * limestone front with lit bronze doors, and a windowless walnut courtroom (the kit's dais, podium,
 * seal and flags in a TXT.interior room). No real building is claimed and the deks say so.
 *
 * THE HERO OBJECT. One bound DEPOSITION TRANSCRIPT, built here as `deposition_transcript`: letter
 * leaves 0.216 x 0.279 m in a 28 mm block, a clear front cover, a black back cover, two chrome screw
 * posts on the left edge. Closed, face down, or open at its last leaf, where the right page is a
 * certificate page whose signature rule and seal box are printed in the deck's one accent, bluebonnet,
 * the blue of certifying ink. It is drawn to illustrate: no source describes the real transcript's
 * pages, and no surface says the real page was blank.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `deposition_transcript`,
 * `video_camera_tripod`, `loblolly_pine`, `granite_stair`, `court_front`, `brick_office`,
 * `lectern_rail` and `rule_page`. Each is built in the kit's conventions so Phase 17 can queue the lift.
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, written in the frame's code where figure_bearing.py
 * checks them against figures.json. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("transcript.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "transcript",
    light: { az: -58, el: 7 },
    sky: { preset: "lastLight", glow: 0.24, horizonGlow: 0.12, stars: 0.55 },   /* the stock seam read as a broad tan wash through a long lens on the audition; the house register keeps it a narrow band */
    ground: "#08060F",
    material: "#C9BBA0",
    accent: "#4E5FA8",
    grade: {
      exposure: 0,
      saturation: 1.03,
      contrast: 1.08,
      filmic: true,
      lift: [0.003, 0.003, 0.006],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.24,
      bloom: { threshold: 0.8, strength: 0.22, radius: 12 },
      grain: { amount: 0.02, size: 2, seed: 20261015 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261015;
  N.ACCENT = 0x4e5fa8;       /* bluebonnet, the deck's one accent: certification, the blue of certifying ink. It
                              * marks the certified court reporter clause, the reporters' five minutes and the
                              * certificate's signature rule, printed unlit at its hex on pale paper and brass. */
  N.INK = "#ECE6DA";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---------------------------------------------------------------- textures */
  N.canvasTex = function (THREE, key, w, h, paint, repeat) {
    N._tex = N._tex || {};
    if (N._tex[key]) return N._tex[key];
    var c = document.createElement("canvas"); c.width = w; c.height = h; paint(c.getContext("2d"), w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
    N._tex[key] = t; return t;
  };
  /* PAPER TOOTH, a fine cream fibre with a faint mottle, so a raking key shows the sheet is paper */
  function tooth(x, w, h, seed, base) {
    var r = lcg(seed); x.fillStyle = base || "#ece4d2"; x.fillRect(0, 0, w, h);
    for (var i = 0; i < w * h / 40; i++) { var v = r(); x.fillStyle = "rgba(" + (v < 0.5 ? "120,104,80," : "255,252,240,") + (0.04 + r() * 0.06).toFixed(3) + ")"; x.fillRect(r() * w, r() * h, 1 + r() * 2, 1); }
  }
  /* A TRANSCRIPT PAGE: the margin's line ticks (25 lines), a double margin rule and the Q and A rhythm
   * of grey bars, never a legible glyph. */
  N.pageTex = function (THREE, seed) {
    return N.canvasTex(THREE, "page" + seed, 432, 558, function (x, w, h) {
      tooth(x, w, h, seed);
      var r = lcg(seed * 3 + 1), top = 60, step = (h - 110) / 25;
      x.fillStyle = "rgba(60,55,50,0.55)"; x.fillRect(64, 30, 1.5, h - 60); x.fillRect(69, 30, 1.5, h - 60);
      for (var i = 0; i < 25; i++) {
        var y = top + i * step;
        x.fillStyle = "rgba(70,64,58,0.5)"; x.fillRect(36, y, 14, 4);
        var q = i % 3 === 0, ind = q ? 92 : 118, len = (q ? 0.35 : 0.45) + r() * (q ? 0.35 : 0.5);
        x.fillStyle = "rgba(55,50,46," + (0.42 + r() * 0.12).toFixed(2) + ")"; x.fillRect(ind, y - 1, (w - ind - 40) * Math.min(1, len), 6);
      }
    });
  };
  /* THE CERTIFICATE PAGE: a heading bar, a short paragraph of grey bars, and the space for the
   * signature rule and seal box, which are drawn as separate unlit accent geometry over it. */
  N.certTex = function (THREE) {
    return N.canvasTex(THREE, "cert", 432, 558, function (x, w, h) {
      tooth(x, w, h, 91);
      var r = lcg(77);
      x.fillStyle = "rgba(45,42,40,0.62)"; x.fillRect(w * 0.3, 60, w * 0.4, 10);
      for (var i = 0; i < 9; i++) { x.fillStyle = "rgba(55,50,46,0.45)"; x.fillRect(60, 110 + i * 22, (w - 120) * (0.6 + r() * 0.4), 6); }
    });
  };
  /* A PAGE OF THE RULES: a column of grey bars above and below the clause the DOM sets, so the sheet
   * reads as a printed rule book page while the rule's own words stay vector type. */
  N.ruleTex = function (THREE) {
    return N.canvasTex(THREE, "rule", 432, 558, function (x, w, h) {
      tooth(x, w, h, 63, "#efe8d8");
      var r = lcg(63);
      for (var i = 0; i < 6; i++) { x.fillStyle = "rgba(55,50,46,0.4)"; x.fillRect(40, 34 + i * 16, (w - 80) * (0.7 + r() * 0.3), 5); }
      for (var j = 0; j < 7; j++) { x.fillStyle = "rgba(55,50,46,0.4)"; x.fillRect(40, h - 150 + j * 16, (w - 80) * (0.6 + r() * 0.4), 5); }
    });
  };
  /* FLAMED GRANITE, pink Texas granite with its feldspar flecks and dark mica */
  N.graniteTex = function (THREE) {
    return N.canvasTex(THREE, "granite2", 512, 512, function (x, w, h) {
      var r = lcg(51); x.fillStyle = "#7c6a66"; x.fillRect(0, 0, w, h);
      /* WRAPPED, so a tile has no seam: every mark is drawn again at its eight neighbours' offsets */
      function at(fn) { for (var dx = -1; dx <= 1; dx++) for (var dy = -1; dy <= 1; dy++) fn(dx * w, dy * h); }
      /* a low drift of crystal size, small enough that it reads as grain at the stair's distance */
      for (var b = 0; b < 170; b++) { var cx0 = r() * w, cy0 = r() * h, rr = 6 + r() * 18, dk = r() < 0.5; at(function (ox, oy) { var gg = x.createRadialGradient(cx0 + ox, cy0 + oy, 0, cx0 + ox, cy0 + oy, rr); gg.addColorStop(0, dk ? "rgba(44,36,36,0.3)" : "rgba(180,150,140,0.26)"); gg.addColorStop(1, "rgba(0,0,0,0)"); x.fillStyle = gg; x.fillRect(cx0 + ox - rr, cy0 + oy - rr, rr * 2, rr * 2); }); }
      /* feldspar, quartz and black mica, the three crystals a flamed pink granite shows */
      for (var i = 0; i < 30000; i++) { var v = r(), c = v < 0.38 ? "168,120,108" : v < 0.62 ? "28,24,26" : v < 0.84 ? "140,124,120" : "214,206,200"; x.fillStyle = "rgba(" + c + "," + (0.25 + r() * 0.35).toFixed(2) + ")"; var sz = 1 + r() * 2.2; x.fillRect(r() * w, r() * h, sz, sz); }
      /* the bed joint and the head joint of one block, so a face reads as coursed stone and a seam lands on a joint */
      x.fillStyle = "rgba(14,10,10,0.85)"; x.fillRect(0, 0, w, 5); x.fillRect(0, 0, 5, h);
      x.fillStyle = "rgba(190,170,160,0.2)"; x.fillRect(0, 5, w, 2); x.fillRect(5, 0, 2, h);
    }, true);
  };

  N.accentMat = function (THREE) {
    if (N._accentMat) return N._accentMat;
    N._accentMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(N.ACCENT), toneMapped: false, fog: false });
    return N._accentMat;
  };

  N.installKit = function (K, THREE, TXT) {
    if (K.registry.deposition_transcript) return;
    var chrome = K.finish.chrome();
    var paper = K.mat("tr-paper", { color: 0xe9e1cf, roughness: 0.92 });
    var paperEdge = K.mat("tr-edge", { color: 0xd9cfb9, roughness: 0.95 });
    var back = K.mat("tr-back", { color: 0x141414, roughness: 0.55 });
    var clear = K.mat("tr-clear", { color: 0xffffff, roughness: 0.08, metalness: 0, transparent: true, opacity: 0.18, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 1.8 }, true);
    var black = K.mat("tr-black", { color: 0x111214, roughness: 0.45, metalness: 0.1 });
    var alu = K.mat("tr-alu", { color: 0xb9bdc2, metalness: 0.8, roughness: 0.32 });
    var rubber = K.finish.rubber();

    /* THE DEPOSITION TRANSCRIPT, lying flat, +z toward the reader. Closed it is a 0.216 x 0.028 x 0.279
     * m block. `face` 'down' turns it over so the black back is up. `open` lays it open at its last leaf:
     * the left page a page of testimony, the right page the certificate, its signature rule and seal box
     * in the accent, printed unlit. userData.rule gives the signature rule's centre in the model frame. */
    K.define("deposition_transcript", {
      size: [0.236, 0.028, 0.285],
      options: { open: 0, face: "up", leaves: 0.026, seed: 3 },
      note: "A bound deposition transcript, drawn to illustrate: letter leaves 0.216 x 0.279 m in a 26 mm block, a clear front cover, a black back cover, two chrome screw posts at the left edge. face up | down; open 1 lays it open at its last leaf, a certificate page whose signature rule and seal box are printed in the deck accent.",
      make: function (o, r) {
        var g = new THREE.Group(), W = 0.216, D = 0.279, T = o.leaves || 0.026;
        if (!o.open) {
          var body = new THREE.Group();
          K.box(W + 0.004, 0.0012, D + 0.004, back, 0, 0, 0, 0, body);
          var nL = 7;
          for (var i = 0; i < nL; i++) {
            var dz = (r() - 0.5) * 0.0024, dx = (r() - 0.5) * 0.0018;
            K.box(W - 0.002, T / nL * 0.98, D - 0.002, i === nL - 1 ? K.mat("tr-top" + o.seed, { color: 0xffffff, roughness: 0.9, map: N.pageTex(THREE, o.seed) }) : paperEdge, dx, 0.0012 + i * T / nL, dz, 0, body);
          }
          K.box(W + 0.004, 0.0006, D + 0.004, clear, 0, 0.0012 + T, 0, 0, body);
          [-1, 1].forEach(function (s) { K.cyl(0.0045, 0.0045, T + 0.004, chrome, -W / 2 + 0.012, -0.0005, s * 0.07, 20, body); K.cyl(0.0065, 0.0065, 0.0012, chrome, -W / 2 + 0.012, T + 0.0018, s * 0.07, 20, body); });
          if (o.face === "down") { body.rotation.z = Math.PI; body.position.y = T + 0.0024; }
          g.add(body);
          return g;
        }
        /* open: two pages tilted a few degrees up toward the spine at x = 0, posts at the spine */
        var lp = new THREE.Group(), rp = new THREE.Group(), half = T / 2;
        K.box(W + 0.004, 0.0012, D + 0.004, clear, 0, 0, 0, 0, lp);
        K.box(W, half, D, paperEdge, 0, 0.0012, 0, 0, lp);
        var pl = new THREE.Mesh(new THREE.PlaneGeometry(W - 0.004, D - 0.004), K.mat("tr-pl" + o.seed, { color: 0xffffff, roughness: 0.9, map: N.pageTex(THREE, o.seed + 5) }));
        pl.rotation.x = -Math.PI / 2; pl.position.y = 0.0012 + half + 0.0004; lp.add(pl);
        lp.position.x = -W / 2 - 0.004; lp.rotation.z = -0.06; g.add(lp);
        K.box(W + 0.004, 0.0012, D + 0.004, back, 0, 0, 0, 0, rp);
        K.box(W, half, D, paperEdge, 0, 0.0012, 0, 0, rp);
        var pr = new THREE.Mesh(new THREE.PlaneGeometry(W - 0.004, D - 0.004), K.mat("tr-cert", { color: 0xffffff, roughness: 0.9, map: N.certTex(THREE) }));
        pr.rotation.x = -Math.PI / 2; pr.position.y = 0.0012 + half + 0.0004; rp.add(pr);
        /* the signature rule and the seal box, in the accent, unlit */
        var acc = N.accentMat(THREE), yTop = 0.0012 + half + 0.0008;
        var rule = new THREE.Mesh(new THREE.PlaneGeometry(0.12, 0.006), acc); rule.rotation.x = -Math.PI / 2; rule.position.set(0.03, yTop, 0.072); rp.add(rule);
        var lbl = new THREE.Mesh(new THREE.PlaneGeometry(0.05, 0.0035), K.mat("tr-gray", { color: 0x5a554e, roughness: 0.9 })); lbl.rotation.x = -Math.PI / 2; lbl.position.set(0.005, yTop, 0.08); rp.add(lbl);
        var seal = new THREE.Group();
        var fill = new THREE.Mesh(new THREE.PlaneGeometry(0.046, 0.046), acc); fill.rotation.x = -Math.PI / 2; seal.add(fill);   /* the seal box, printed solid in certifying ink */
        seal.position.set(-0.055, yTop, 0.085); rp.add(seal);
        rp.position.x = W / 2 + 0.004; rp.rotation.z = 0.06; g.add(rp);
        [-1, 1].forEach(function (s) { K.cyl(0.0045, 0.0045, half + 0.01, chrome, 0, 0, s * 0.07, 20, g); });
        g.userData.keepOrigin = true;
        g.userData.rule = [W / 2 + 0.004 + 0.03, yTop, 0.072];
        return g;
      }
    });

    /* A VIDEO CAMERA ON ITS TRIPOD, the deposition's video record: a black camcorder 0.32 m long with a
     * lens hood, a flip screen on its left side, a top handle, on a fluid head at `height` on three
     * aluminium legs with rubber feet. Lens faces +z. */
    K.define("video_camera_tripod", {
      size: [0.95, 1.36, 0.95],
      anchor: "base",
      options: { height: 1.2, spread: 0.45, screen: true, seed: 2 },
      note: "A camcorder on a fluid head tripod, drawn to illustrate: body 0.32 x 0.14 x 0.15 m with lens hood, flip screen and top handle, lens height `height` m facing +z, three aluminium legs spread `spread` m.",
      make: function (o, r) {
        var g = new THREE.Group(), H = o.height || 1.2, S = o.spread || 0.45;
        var head = [0, H - 0.12, 0];
        for (var k = 0; k < 3; k++) {
          var a = k * 2.094 + 0.5, foot = [Math.sin(a) * S, 0.02, Math.cos(a) * S];
          K.bar(head, [foot[0] * 0.5, H * 0.5, foot[2] * 0.5], 0.012, alu, 8, g);
          K.bar([foot[0] * 0.5, H * 0.5, foot[2] * 0.5], foot, 0.009, alu, 8, g);
          K.cyl(0.016, 0.016, 0.03, rubber, foot[0], 0, foot[2], 10, g);
          K.bar([foot[0] * 0.25, H * 0.42, foot[2] * 0.25], [0, H * 0.4, 0], 0.005, alu, 6, g);
        }
        K.cyl(0.04, 0.045, 0.08, black, 0, H - 0.16, 0, 20, g);
        K.box(0.09, 0.03, 0.12, black, 0, H - 0.085, 0, 0.006, g);
        var bh = K.bar([0.05, H - 0.07, -0.05], [0.33, H - 0.03, -0.32], 0.008, black, 8, g);
        var body = K.box(0.13, 0.14, 0.3, K.mat("cam-body", { color: 0x16171a, roughness: 0.5, metalness: 0.15 }), 0, H - 0.055, 0.03, 0.02, g);
        var lens = K.cyl(0.042, 0.042, 0.11, black, 0, 0, 0, 28, null); lens.rotation.x = Math.PI / 2; lens.position.set(0, H + 0.015, 0.23); g.add(lens);
        var hood = K.cyl(0.062, 0.046, 0.06, black, 0, 0, 0, 28, null); hood.rotation.x = Math.PI / 2; hood.position.set(0, H + 0.015, 0.31); g.add(hood);
        var glass = new THREE.Mesh(new THREE.CircleGeometry(0.036, 28), K.finish.glass(0x10141a)); glass.position.set(0, H + 0.015, 0.338); g.add(glass);
        K.box(0.03, 0.02, 0.2, black, 0, H + 0.085, 0.02, 0.005, g);
        K.bar([0, H + 0.105, -0.07], [0, H + 0.105, 0.11], 0.011, black, 10, g);
        if (o.screen) {
          var lcd = K.box(0.012, 0.066, 0.1, black, -0.075, H - 0.013, 0.1, 0.003, g);
          /* the flip screen, lit in the deck accent: the certified video record, which is what the employee's lawyer argued it is (c13) */
          var sc = new THREE.Mesh(new THREE.PlaneGeometry(0.09, 0.056), o.screen === "accent" ? N.accentMat(THREE) : K.mat("cam-lcd", { color: 0x0c0e12, emissive: 0x5d6b7a, emissiveIntensity: 0.55, roughness: 0.2 })); sc.rotation.y = -Math.PI / 2; sc.position.set(-0.0815, H + 0.02, 0.1); g.add(sc);
        }
        g.userData.lens = [0, H + 0.015, 0.34];
        return g;
      }
    });

    /* A LOBLOLLY PINE, the Piney Woods' tree: a straight trunk self pruned to about two thirds of its
     * height, plated red brown bark, a few dead branch stubs, and a crown of dark needle clumps in the
     * top third. Height `height` m. Drawn mostly in silhouette. */
    K.define("loblolly_pine", {
      size: [7, 22, 7],
      anchor: "base",
      options: { height: 22, seed: 1 },
      note: "Loblolly pine, Pinus taeda: a straight self pruned trunk (0.45 m at breast height) to about two thirds of `height`, plated bark, dead stubs, a crown of dark needle clumps in the top third.",
      make: function (o, r) {
        var g = new THREE.Group(), H = o.height || 22, crown0 = H * (0.62 + r() * 0.06);
        var bark = K.mat("lob-bark", { color: 0xffffff, map: K.tex("bark"), roughness: 0.95 });
        var tr = K.cyl(0.13, 0.26, H * 0.97, bark, 0, 0, 0, 14, g); tr.geometry = K.uvBox(tr.geometry, 1.0);
        var stub = K.mat("lob-stub", { color: 0x3a2c22, roughness: 0.95 });
        for (var s = 0; s < 7; s++) { var y = H * (0.3 + r() * 0.3), a = r() * 6.28, l = 0.4 + r() * 0.6; K.bar([0, y, 0], [Math.cos(a) * l, y + 0.25, Math.sin(a) * l], 0.025, stub, 5, g); }
        var needles = K.mat("lob-needle", { color: 0x1f2a1f, roughness: 0.9 }), needles2 = K.mat("lob-needle2", { color: 0x2a3524, roughness: 0.9 });
        var geo = new THREE.IcosahedronGeometry(1, 1);
        for (var c = 0; c < 26; c++) {
          var cy = crown0 + r() * (H - crown0), t = (cy - crown0) / (H - crown0), rad = (1 - t * 0.7) * (2.6 + r() * 0.8), ang = r() * 6.28;
          var m = new THREE.Mesh(geo, r() < 0.5 ? needles : needles2);
          m.position.set(Math.cos(ang) * rad * r(), cy, Math.sin(ang) * rad * r());
          var sc = 0.9 + r() * 0.9; m.scale.set(sc * 1.3, sc * 0.55, sc * 1.3); m.rotation.y = r() * 6.28;
          if (c < 14) K.bar([0, cy - 0.3, 0], [m.position.x * 0.8, cy, m.position.z * 0.8], 0.05, stub, 5, g);
          g.add(m);
        }
        return g;
      }
    });

    /* THE GRANITE STAIR, `steps` risers of 0.165 m and treads of 0.38 m climbing along -z, `width` m wide,
     * flamed pink granite, a bronze nosing strip on every tread, limestone cheek walls, then a landing
     * `landing` m deep. The bottom riser's foot is at the origin's z. userData.tread(i) gives the centre
     * top of tread i (0 is the plaza in front of the first riser, steps is the landing). */
    K.define("granite_stair", {
      size: [14, 3, 12],
      options: { steps: 1, width: 14, rise: 0.165, run: 0.38, landing: 5, cheeks: "both", seed: 4 },
      note: "A flamed pink granite stair of `steps` risers (0.165 m) and treads (0.38 m) climbing along -z, `width` m wide, bronze nosing strips, limestone cheek walls and a landing `landing` m deep. userData.tread(i) is the centre top of tread i.",
      make: function (o, r) {
        var g = new THREE.Group(), n = o.steps, Wd = o.width, rise = o.rise, run = o.run, L = o.landing;
        var gt = N.graniteTex(THREE);
        var gran = K.mat("st-gran", { color: 0x6c605d, map: gt, bumpMap: gt, bumpScale: 0.8, roughness: 0.82 });
        var bronze = K.mat("st-bronze", { color: 0x8c7658, metalness: 0.62, roughness: 0.34 });   /* worn by feet, so it reads by its own light as well as the sky it reflects */
        var lime = K.mat("st-lime", { color: 0x8c826e, map: K.tex("limestone"), roughness: 0.88 });
        for (var i = 0; i < n; i++) {
          var h = (i + 1) * rise, z0 = -i * run;
          /* each course its own block of stone, a shade lighter or darker than its neighbours, as a quarried stair is */
          var tint = 0.74 + r() * 0.52, gm = K.mat("st-gran" + i, { color: new THREE.Color(0x6c605d).multiplyScalar(tint), map: gt, bumpMap: gt, bumpScale: 0.8, roughness: 0.82 });
          var b = K.box(Wd, h, run, gm, 0, 0, z0 - run / 2, 0, g); b.geometry = K.uvBox(b.geometry, 0.7);
          K.box(Wd - 0.02, 0.02, 0.05, bronze, 0, h - 0.016, z0 - 0.01, 0, g);   /* the nosing stands 15 mm proud of the riser, so it throws a line of shadow under itself */
        }
        var top = n * rise, lz = -n * run;
        var land = K.box(Wd, top, L, gran, 0, 0, lz - L / 2, 0, g); land.geometry = K.uvBox(land.geometry, 0.7);
        (o.cheeks === "both" ? [-1, 1] : o.cheeks === "left" ? [-1] : o.cheeks === "right" ? [1] : []).forEach(function (s) {
          var len = n * run + L, cw = K.box(0.6, top + 0.45, len, lime, s * (Wd / 2 + 0.3), 0, -len / 2, 0.02, g); cw.geometry = K.uvBox(cw.geometry, 1.6);
        });
        g.userData.keepOrigin = true;
        g.userData.tread = function (i) { return i <= 0 ? [0, 0, 0.4] : i >= n ? [0, top, lz - 0.6] : [0, i * rise, -(i - 0.5) * run]; };
        g.userData.top = top; g.userData.depth = n * run;
        return g;
      }
    });

    /* A LIMESTONE COURT FRONT for the top of the stair: a Cordova cream wall `w` m wide and `h` tall,
     * pilasters, a cornice, a recessed entry with two pairs of bronze framed glass doors lit warm from
     * inside, and a row of dark tall windows above. Faces +z, its foot at y = 0. */
    K.define("court_front", {
      size: [30, 14, 3],
      options: { w: 30, h: 14, seed: 6 },
      note: "An illustrative limestone court front facing +z: pilasters, cornice, a recessed entry of two lit bronze and glass door pairs, tall dark windows above.",
      make: function (o, r) {
        var g = new THREE.Group(), w = o.w, h = o.h;
        var lime = K.mat("cf-lime", { color: 0xa89c84, map: K.tex("limestone"), roughness: 0.86 });
        var bronze = K.mat("cf-bronze", { color: 0x5e4630, metalness: 0.85, roughness: 0.4 });
        /* THE LIT GLASS: a lobby seen through the doors, brighter toward its floor, a push bar and a mid rail
         * across each leaf and a pale ceiling light, so the doors read as glass with a room behind them */
        var glassTex = N.canvasTex(THREE, "cf-glass2", 128, 288, function (x, w, h) {
          /* the lobby behind the glass: a warm back wall, a paler floor running back to it, a ceiling in shade */
          var wall = x.createLinearGradient(0, 0, 0, h * 0.64); wall.addColorStop(0, "#3c2614"); wall.addColorStop(1, "#b07a44"); x.fillStyle = wall; x.fillRect(0, 0, w, h * 0.64);
          var fl = x.createLinearGradient(0, h * 0.64, 0, h); fl.addColorStop(0, "#d8a868"); fl.addColorStop(1, "#8a5e34"); x.fillStyle = fl; x.fillRect(0, h * 0.64, w, h * 0.36);
          x.fillStyle = "rgba(255,226,180,0.35)"; x.fillRect(w * 0.3, h * 0.05, w * 0.4, h * 0.012);   /* a ceiling fixture's line, not a hotspot */
          x.fillStyle = "rgba(30,18,10,0.6)"; x.fillRect(w * 0.12, h * 0.4, w * 0.1, h * 0.26); x.fillRect(w * 0.7, h * 0.36, w * 0.16, h * 0.3);   /* a bench and a doorway at the back */
          /* the leaf's own mullions and push bar, bronze against the light */
          x.fillStyle = "#2a1c10"; x.fillRect(0, 0, w * 0.07, h); x.fillRect(w * 0.93, 0, w * 0.07, h); x.fillRect(0, 0, w, h * 0.035); x.fillRect(0, h * 0.965, w, h * 0.035); x.fillRect(0, h * 0.52, w, h * 0.022);
          x.fillStyle = "#6a4a2a"; x.fillRect(w * 0.15, h * 0.47, w * 0.7, h * 0.016);
          /* the glass's own reflection, one soft diagonal of the plaza's dark */
          var rf = x.createLinearGradient(0, 0, w, h); rf.addColorStop(0.35, "rgba(0,0,0,0)"); rf.addColorStop(0.5, "rgba(10,8,12,0.28)"); rf.addColorStop(0.65, "rgba(0,0,0,0)"); x.fillStyle = rf; x.fillRect(0, 0, w, h);
        });
        var lit = K.mat("cf-lit", { color: 0x120c06, emissive: 0xffffff, emissiveMap: glassTex, emissiveIntensity: 1.35, roughness: 0.15, metalness: 0.1 });
        var dark = K.mat("cf-win", { color: 0x0c0d10, roughness: 0.55, metalness: 0.2 });
        var seg = function (x0, x1, y0, y1, z) { var m = K.box(x1 - x0, y1 - y0, 0.8, lime, (x0 + x1) / 2, y0, z - 0.4, 0, g); m.geometry = K.uvBox(m.geometry, 1.6); };
        seg(-w / 2, -4.2, 0, h, 0); seg(4.2, w / 2, 0, h, 0); seg(-4.2, 4.2, 4.6, h, 0);
        var rec = K.box(8.4, 4.6, 0.3, lime, 0, 0, -1.6, 0, g); rec.geometry = K.uvBox(rec.geometry, 1.6);
        K.box(8.4, 0.25, 1.6, lime, 0, 4.35, -0.8, 0, g);
        [-1, 1].forEach(function (s) { K.box(0.3, 4.6, 1.5, lime, s * 4.05, 0, -0.75, 0, g); });
        [-2.1, 2.1].forEach(function (cx) {
          K.box(3.2, 3.5, 0.12, bronze, cx, 0, -1.4, 0, g);
          [-0.76, 0.76].forEach(function (dx) { K.box(1.22, 2.8, 0.03, lit, cx + dx, 0.18, -1.33, 0, g); });
          K.box(3.0, 0.5, 0.03, lit, cx, 3.0, -1.33, 0, g);
        });
        for (var px = -w / 2 + 1.5; px <= w / 2 - 1.4; px += 3.4) { if (Math.abs(px) < 5) continue; K.box(0.7, h - 1.2, 0.35, lime, px, 0, 0.17, 0, g); }
        for (var wx = -w / 2 + 3.2; wx < w / 2 - 2; wx += 3.4) { if (Math.abs(wx) < 5.5) continue; K.box(1.5, 4.2, 0.05, dark, wx, 6.2, 0.03, 0, g); K.box(1.5, 3.0, 0.05, dark, wx, 0.9, 0.03, 0, g); }
        K.box(w + 0.8, 0.8, 1.2, lime, 0, h - 0.4, 0, 0, g);
        g.userData.keepOrigin = true;
        g.userData.doors = [0, 1.8, -1.3];
        return g;
      }
    });

    /* A ONE STOREY BRICK OFFICE, `w` by `d` m and 4.2 m high, buff brick, its south east corner a
     * room glazed floor to ceiling on two faces, `room` m square, lit warm from a pendant. The frame
     * furnishes the room. Foot at y = 0, front +z. userData.room is the room's floor centre. */
    K.define("brick_office", {
      size: [18, 4.4, 10],
      options: { w: 18, d: 10, room: 6.5, seed: 8 },
      note: "An illustrative one storey buff brick office facing +z with a corner room glazed floor to ceiling on its south and east faces, lit by a pendant; userData.room is the room's floor centre.",
      make: function (o, r) {
        var g = new THREE.Group(), w = o.w, d = o.d, H = 4.2, R = o.room;
        var brick = K.mat("bo-brick", { color: 0xd8c3a0, map: K.tex("brick"), roughness: 0.9 });
        var trim = K.mat("bo-trim", { color: 0x2a2a2c, metalness: 0.4, roughness: 0.5 });
        var inner = K.mat("bo-inner", { color: 0x8a7f72, roughness: 0.9 });
        var floor = K.mat("bo-floor", { color: 0x5a4c3e, roughness: 0.8 });
        var glass = K.mat("bo-glass", { color: 0x9fb0b8, roughness: 0.05, metalness: 0, transparent: true, opacity: 0.12, clearcoat: 1, envMapIntensity: 1.2 }, true);
        var wall = function (W, Hh, D, x, y, z) { var m = K.box(W, Hh, D, brick, x, y, z, 0, g); m.geometry = K.uvBox(m.geometry, 1.0); return m; };
        var x0 = -w / 2, x1 = w / 2, z0 = -d / 2, z1 = d / 2;
        wall(w - R, H, 0.3, x0 + (w - R) / 2, 0, z1 - 0.15);
        wall(0.3, H, d - R, x1 - 0.15, 0, z0 + (d - R) / 2);
        wall(w, H, 0.3, 0, 0, z0 + 0.15);
        wall(0.3, H, d, x0 + 0.15, 0, 0);
        wall(R, 0.7, 0.3, x1 - R / 2, H - 0.7, z1 - 0.15);
        wall(0.3, 0.7, R, x1 - 0.15, H - 0.7, z1 - R / 2);
        K.box(w + 0.4, 0.5, d + 0.4, brick, 0, H, 0, 0, g);
        K.box(w + 0.5, 0.08, d + 0.5, trim, 0, H + 0.5, 0, 0, g);
        var gs = K.box(R - 0.3, H - 0.75, 0.02, glass, x1 - R / 2 - 0.15, 0.05, z1 - 0.15, 0, g);
        var ge = K.box(0.02, H - 0.75, R - 0.3, glass, x1 - 0.15, 0.05, z1 - R / 2 - 0.15, 0, g);
        for (var k = 0; k <= 3; k++) { K.box(0.06, H - 0.7, 0.08, trim, x1 - 0.15 - k * (R - 0.15) / 3, 0, z1 - 0.15, 0, g); K.box(0.08, H - 0.7, 0.06, trim, x1 - 0.15, 0, z1 - 0.15 - k * (R - 0.15) / 3, 0, g); }
        K.box(R, 0.02, R, floor, x1 - R / 2, 0.02, z1 - R / 2, 0, g);
        K.box(0.2, H - 0.75, R, inner, x1 - R - 0.1, 0, z1 - R / 2, 0, g);
        K.box(R, H - 0.75, 0.2, inner, x1 - R / 2, 0, z1 - R - 0.1, 0, g);
        K.box(R, 0.05, R, K.mat("bo-ceil", { color: 0x6e665c, roughness: 0.9 }), x1 - R / 2, H - 0.75, z1 - R / 2, 0, g);
        var pend = K.cyl(0.35, 0.35, 0.08, K.finish.lamp(0xffd9a0, 2.4), x1 - R / 2, H - 1.6, z1 - R / 2, 24, g);
        K.bar([x1 - R / 2, H - 1.52, z1 - R / 2], [x1 - R / 2, H - 0.75, z1 - R / 2], 0.006, trim, 4, g);
        var pl = new THREE.PointLight(0xffd8a6, 26, 9, 1.6); pl.position.set(x1 - R / 2, H - 1.7, z1 - R / 2); g.add(pl);
        g.userData.keepOrigin = true;
        g.userData.room = [x1 - R / 2, 0, z1 - R / 2];
        g.userData.pendant = pl;
        return g;
      }
    });

    /* THE LECTERN RAIL: a walnut bar carrying `segments` brushed brass segments, the last `lit` of them
     * printed in the accent, unlit. Runs along x, centred. */
    K.define("lectern_rail", {
      size: [0.62, 0.03, 0.04],
      options: { segments: 1, lit: 0, length: 0.6, seed: 1 },
      note: "A lectern timer rail, drawn to illustrate: a walnut bar with `segments` brass segments, the last `lit` in the deck accent.",
      make: function (o, r) {
        var g = new THREE.Group(), L = o.length, n = o.segments, s = L / n;
        K.box(L + 0.03, 0.02, 0.04, K.mat("lr-wal", { color: 0x3a2618, roughness: 0.6 }), 0, 0, 0, 0.004, g);
        var brass = new THREE.MeshBasicMaterial({ color: new THREE.Color(0x9a7a4a), toneMapped: false, fog: false });   /* one hue at one intensity on every segment, like the accent ones, never a ramp */
        for (var i = 0; i < n; i++) {
          var lit = i >= n - o.lit;
          K.box(s * 0.82, 0.008, 0.026, lit ? N.accentMat(THREE) : brass, -L / 2 + s * (i + 0.5), 0.02, 0, 0, g);
        }
        return g;
      }
    });

    /* A PAGE OF THE RULES, a letter sheet lying flat with paper tooth. The rule's words are DOM, set on
     * this page's projected corners by N.quad. userData.corners are its four corners in the model frame. */
    K.define("rule_page", {
      size: [0.216, 0.002, 0.279],
      options: { seed: 1 },
      note: "A single letter page of a rule book lying flat, grey bars above and below a clear band where the frame sets the rule's words in DOM.",
      make: function (o, r) {
        var g = new THREE.Group(), W = 0.216, D = 0.279;
        K.box(W, 0.0008, D, K.mat("rp-edge", { color: 0xd9cfb9, roughness: 0.95 }), 0, 0, 0, 0, g);
        var p = new THREE.Mesh(new THREE.PlaneGeometry(W, D), K.mat("rp-face", { color: 0xffffff, roughness: 0.9, map: N.ruleTex(THREE) }));
        p.rotation.x = -Math.PI / 2; p.position.y = 0.0009; g.add(p);
        g.userData.keepOrigin = true;
        g.userData.corners = [[-W / 2, 0.001, -D / 2], [W / 2, 0.001, -D / 2], [W / 2, 0.001, D / 2], [-W / 2, 0.001, D / 2]];
        return g;
      }
    });
  };

  /* DOM TYPE ON A PROJECTED QUAD: a CSS matrix3d homography taking an element's own w x h box onto four
   * screen points (top left, top right, bottom right, bottom left), so a page's words stay vector type. */
  N.quad = function (el, w, h, P) {
    function solve(A, b) { var n = b.length; for (var i = 0; i < n; i++) { var mx = i; for (var k = i + 1; k < n; k++) if (Math.abs(A[k][i]) > Math.abs(A[mx][i])) mx = k; var t = A[i]; A[i] = A[mx]; A[mx] = t; var tb = b[i]; b[i] = b[mx]; b[mx] = tb; for (var k2 = i + 1; k2 < n; k2++) { var f = A[k2][i] / A[i][i]; for (var j = i; j < n; j++) A[k2][j] -= f * A[i][j]; b[k2] -= f * b[i]; } } var x = new Array(n); for (var i2 = n - 1; i2 >= 0; i2--) { var s = b[i2]; for (var j2 = i2 + 1; j2 < n; j2++) s -= A[i2][j2] * x[j2]; x[i2] = s / A[i2][i2]; } return x; }
    var src = [[0, 0], [w, 0], [w, h], [0, h]], A = [], b = [];
    for (var i = 0; i < 4; i++) {
      var x = src[i][0], y = src[i][1], u = P[i][0], v = P[i][1];
      A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.push(u);
      A.push([0, 0, 0, x, y, 1, -v * x, -v * y]); b.push(v);
    }
    var hm = solve(A, b);
    var m = [hm[0], hm[3], 0, hm[6], hm[1], hm[4], 0, hm[7], 0, 0, 1, 0, hm[2], hm[5], 0, 1];
    el.style.position = "absolute"; el.style.left = "0px"; el.style.top = "0px"; el.style.width = w + "px"; el.style.height = h + "px";
    el.style.transformOrigin = "0 0"; el.style.transform = "matrix3d(" + m.map(function (v) { return +v.toFixed(8); }).join(",") + ")";
  };

  N.keepAlpha = function (m) {
    var T = N.T;
    m.blending = T.CustomBlending; m.blendEquation = T.AddEquation;
    if (m.userData && m.userData.additive) { m.blendSrc = T.SrcAlphaFactor; m.blendDst = T.OneFactor; }
    else { m.blendSrc = T.SrcAlphaFactor; m.blendDst = T.OneMinusSrcAlphaFactor; }
    m.blendEquationAlpha = T.AddEquation; m.blendSrcAlpha = T.OneFactor; m.blendDstAlpha = T.OneFactor;
    return m;
  };
  /* THE PLAZA, matte: a ground that does not mirror the seam at a grazing camera */
  N.matte = function (gnd, k) { (Array.isArray(gnd) ? gnd : [gnd]).forEach(function (g) { (g.traverse ? g : { traverse: function (f) { f(g); } }).traverse(function (m) { if (m.material) { m.material.envMapIntensity = k == null ? 0.08 : k; m.material.roughness = 1; m.material.needsUpdate = true; } }); }); return gnd; };
  /* THE PLAZA PAD: a dark worn concrete slab the stair stands on. At a grazing camera TXT.ground fades into
   * the horizon's colour by design, which here is the seam, so the near plaza is this pad and the ground
   * beyond it keeps the engine's fade. */
  N.pad = function (THREE, R, w, d, x, z, rot) {
    var t = N.canvasTex(THREE, "pad", 512, 512, function (c, W, H) { var r = lcg(12); c.fillStyle = "#3a3633"; c.fillRect(0, 0, W, H); for (var i = 0; i < 9000; i++) { c.fillStyle = "rgba(" + (r() < 0.5 ? "20,18,17," : "90,84,78,") + (0.08 + r() * 0.12).toFixed(2) + ")"; c.fillRect(r() * W, r() * H, 1 + r() * 3, 1 + r() * 3); } c.strokeStyle = "rgba(15,14,13,0.6)"; c.lineWidth = 3; for (var k = 0; k <= 4; k++) { c.beginPath(); c.moveTo(k * W / 4, 0); c.lineTo(k * W / 4, H); c.stroke(); c.beginPath(); c.moveTo(0, k * H / 4); c.lineTo(W, k * H / 4); c.stroke(); } }, true);
    t.repeat.set(w / 6, d / 6);
    var m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshLambertMaterial({ color: 0x8a837c, map: t }));
    m.rotation.x = -Math.PI / 2; m.position.set(x || 0, 0.004, z || 0); if (rot) m.rotation.z = rot; m.receiveShadow = true; R.scene.add(m);
    return m;
  };
  /* FAR LIT WINDOWS on dark land: a scatter of small warm points low on the horizon, so a frame that looks
   * out from the court sees a county at night rather than a skyline anybody could name */
  N.windows = function (THREE, R, center, dirAz, o) {
    o = o || {}; var r = lcg(o.seed || 9), g = new THREE.Group(), n = o.count || 160;
    var mat = new THREE.MeshBasicMaterial({ color: 0xffc27a, toneMapped: true, fog: false });
    var geo = new THREE.BoxGeometry(1, 1, 1);
    for (var i = 0; i < n; i++) {
      var d = (o.near || 500) + Math.pow(r(), 0.7) * ((o.far || 2600) - (o.near || 500)), a = dirAz + (r() - 0.5) * (o.spread || 1.4);
      var m = new THREE.Mesh(geo, mat); var sz = 1.2 + r() * 2.4;
      m.scale.set(sz, sz * (0.5 + r() * 0.6), sz); m.position.set(center[0] + Math.sin(a) * d, 0.5 + r() * 3, center[2] + Math.cos(a) * d); g.add(m);
    }
    R.scene.add(g); return g;
  };
  /* A COURTROOM CARPET over the well, dark wool with a faint weave, so the floor a wide lens takes in
   * stays low in value and carries tooth rather than a bright tile field */
  N.carpet = function (THREE, R, w, d, x, z) {
    var t = N.canvasTex(THREE, "carpet", 256, 256, function (c, W, H) { var r = lcg(31); c.fillStyle = "#3a2c30"; c.fillRect(0, 0, W, H); for (var i = 0; i < 9000; i++) { c.fillStyle = "rgba(" + (r() < 0.5 ? "96,70,76," : "14,10,12,") + (0.3 + r() * 0.4).toFixed(2) + ")"; c.fillRect(r() * W, r() * H, 1, 1 + r() * 2); } c.strokeStyle = "rgba(120,92,60,0.5)"; c.lineWidth = 6; c.strokeRect(10, 10, W - 20, H - 20); }, true);
    t.repeat.set(w / 1.5, d / 1.5);
    var m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshLambertMaterial({ color: 0xffffff, map: t }));
    m.rotation.x = -Math.PI / 2; m.position.set(x || 0, 0.006, z || 0); m.receiveShadow = true; R.scene.add(m); return m;
  };
  /* WALNUT PANELING: raised panels with stiles and rails and a grain, for the wall behind a bench or a
   * law office's back wall, so a room's largest surface carries joinery rather than flat paint */
  N.paneling = function (THREE, K, R, w, h, x, y, z, ry, o) {
    o = o || {}; var g = new THREE.Group(), pw = o.panel || 1.2, ph = h / (o.rows || 2);
    var wood = K.mat("pn-wood", { color: o.color || 0x5a3a24, map: K.tex("wood"), roughness: 0.62 });
    var dark = K.mat("pn-dark", { color: o.dark || 0x2a1a10, map: K.tex("wood"), roughness: 0.7 });
    var back = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.03), dark); back.position.set(0, h / 2, 0); back.receiveShadow = true; g.add(back);
    var n = Math.max(1, Math.round(w / pw)), cw = w / n;
    for (var i = 0; i < n; i++) for (var j = 0; j < (o.rows || 2); j++) {
      var p = TXT_round(THREE, cw - 0.16, ph - 0.16, 0.035, wood); p.position.set(-w / 2 + cw * (i + 0.5), ph * (j + 0.5), 0.03); g.add(p);
    }
    var cap = new THREE.Mesh(new THREE.BoxGeometry(w, 0.08, 0.08), dark); cap.position.set(0, h, 0.03); g.add(cap);
    g.position.set(x, y || 0, z); g.rotation.y = ry || 0; g.traverse(function (m) { if (m.isMesh) { m.castShadow = false; m.receiveShadow = true; } }); R.scene.add(g); return g;
  };
  function TXT_round(THREE, w, h, d, mat) { var m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.geometry = N.K ? N.K.uvBox(m.geometry, 1.2) : m.geometry; return m; }
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
    var ink = N.INK, dek = "#D8D0C2", halo = "rgba(3,4,8,0.6)", halo2 = "rgba(3,4,8,0.45)", acc = "#" + ("000000" + N.ACCENT.toString(16)).slice(-6).toUpperCase();
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
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D8D0C2" });
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
