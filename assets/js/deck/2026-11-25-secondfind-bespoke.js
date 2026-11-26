/* deck/2026-11-25-secondfind-bespoke.js, the SPINE for the November 25th, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * UTMB Health's AI reads radiology reports and flags lung nodules for a patient navigator, and roughly two thirds of the
 * nodules the program found came from patients who were not having lung cancer screening (tx-2026-0260).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the deck's TONE (people), bespoke:true, the tone's grade and the accent.
 * Each frame picks its own world (TXT.sky(R, world) or TXT.studio / TXT.interior), turns its own key
 * (TXT.deckRig(..., { light })) and places its own type, seated with CH.seat. It mounts the type faces and the furniture
 * (CH.start), and hands a frame the helpers below. There is no drawFrame.
 *
 * THE ACCENT. Gold #ffc83d means ONE thing: A NODULE FLAGGED FOR A PERSON (the bead, a flag tab, a raised flagged line).
 * Never on type, never decoration, never red.
 * THE MATERIAL CODE. Periwinkle (CH.OTHER) means a scan ordered for something else. Frosted white (CH.SCREEN) means a
 * screening exam. Held on every frame that draws either.
 *
 * THE MODELS the kit lacks, in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can
 * queue the lift: glass_lung (paired lobes in lilac glass with frosted bronchi), scan_slab (a rounded acrylic scan field),
 * nodule_bead (the gold bead), manila_folder and chart_cart, age_rule (a steel rule with decade ticks, an enamel block and
 * a bead groove), ct_gantry (ring housing, bore, couch), card_rack, oak_counter and reading_bridge. Everything drawn is
 * drawn to illustrate: no real CT image, no product interface, no logo, no legible screen, no likeness.
 * Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("secondfind.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "secondfind", look: "v2", tone: "people", bespoke: true,
    light: { az: -38, el: 32 },
    sky: { preset: "v2people" },
    ground: "#ff9f62",
    material: "#efe6d8",
    accent: "#ffc83d",
    grade: TXLOOK.grade("people")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261125; N.TONE = "people"; N.P = TXLOOK.palette("people"); N.INK = N.P.ink;
  N.ACCENT = 0xffc83d;        /* gold: a nodule flagged for a person, and nothing else */
  N.OTHER = 0x8c9cf0;         /* periwinkle: a scan ordered for something else */
  N.SCREEN = 0xf4f1ff;        /* frosted white: a screening exam */
  N.LILAC = 0xd9c8ff; N.PLUM = 0x4a2a6e; N.OAK = 0xc89b6a; N.MANILA = 0xe9c98e; N.LIMESTONE = 0xe8dcc4; N.PAPER = 0xf7f1e4;
  N.STEEL = 0xd6dbe0; N.SHELL = 0xf4f2ee;
  N.GOLD = N.ACCENT;
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };
  /* lilac lung glass: transmission with a coloured attenuation, so it never reads as grey murk */
  N.glassMat = function (K, tint, att) {
    return K.mat("sf-glass" + (tint || "") + (att || ""), { color: tint || N.LILAC, metalness: 0, roughness: 0.06, transmission: 0.92, ior: 1.45, thickness: 0.05,
      attenuationColor: att || 0xb79cff, attenuationDistance: 0.25, transparent: true, opacity: 1, clearcoat: 1, clearcoatRoughness: 0.04,
      specularIntensity: 1, envMapIntensity: 1.5, side: N.T.DoubleSide }, true);
  };
  /* scan acrylic: OTHER (periwinkle) or SCREEN (frosted white) */
  N.acrylicMat = function (K, kind) {
    var screen = kind === "screen";
    return K.mat("sf-acryl-" + (screen ? "s" : "o"), { color: screen ? N.SCREEN : N.OTHER, metalness: 0, roughness: screen ? 0.42 : 0.12,
      transmission: screen ? 0.55 : 0.82, ior: 1.49, thickness: 0.02, attenuationColor: screen ? 0xffffff : 0x6f7fe8, attenuationDistance: 0.12,
      transparent: true, clearcoat: 1, clearcoatRoughness: 0.08, envMapIntensity: 1.3, side: N.T.DoubleSide }, true);
  };
  /* the flag's gold, albedo first with a little emissive (no. 41 read pink at 1.05) */
  N.goldMat = function (K) { return K.mat("sf-gold", { color: N.ACCENT, metalness: 0.75, roughness: 0.22, emissive: N.ACCENT, emissiveIntensity: 0.18, clearcoat: 0.6 }, true); };
  N.toolMat = function (K) { return K.mat("sf-cyan", { color: 0x061820, emissive: 0x22d3ee, emissiveIntensity: 1.2, roughness: 0.2 }); };
  /* greeked lines on paper, never legible */
  N.paperTex = function (THREE, seed, lines, flagLine) {
    var r = N.rng(seed || 7);
    return N.canvasTex(THREE, 512, 660, function (g, w, h) {
      g.fillStyle = "#f7f1e4"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 3000; i++) { g.fillStyle = "rgba(120,100,80," + (r() * 0.05).toFixed(3) + ")"; g.fillRect(r() * w, r() * h, 1.2, 1.2); }
      var n = lines || 18;
      for (var L = 0; L < n; L++) {
        var y = 50 + L * (h - 90) / n, x = 40, end = w - 40 - (L % 5 === 4 ? 200 : r() * 50);
        while (x < end) { var ww = 12 + r() * 50; g.fillStyle = L === flagLine ? "rgba(255,200,61,0.95)" : "rgba(74,42,110,0.5)"; g.fillRect(x, y, Math.min(ww, end - x), 7); x += ww + 9 + r() * 6; }
      }
    });
  };

  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.glass_lung) return;
    N.T = THREE;
    var shadowAll = function (g) { g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return g; };
    var steel = function () { return K.mat("sf-steel", { color: N.STEEL, metalness: 0.9, roughness: 0.3 }); };
    var oak = function () { return K.mat("sf-oak", { color: N.OAK, roughness: 0.55, clearcoat: 0.25, clearcoatRoughness: 0.5 }, true); };

    /* GLASS LUNG. 0.28 x 0.30 x 0.14 m. Two lobed lungs from deformed spheres (flattened on the medial face, tapered to the
     * apex, the left lung notched for the heart), a trachea and two main bronchi in frosted resin with branch stubs.
     * Origin at the base centre on the ground, front on +z. userData.lobes holds the two lung meshes; userData.anchor(side, u, v)
     * returns a point inside a lung (side -1 right lung on -x, +1 left lung) for a bead. */
    K.define("glass_lung", {
      size: [0.28, 0.30, 0.14],
      options: { tint: null, att: null, scale: 1, bronchi: true },
      note: "Teaching model lungs in lilac glass, drawn to illustrate: two lobed lungs, frosted trachea and bronchi. userData.anchor(side,u,v) gives a point inside a lung for a bead.",
      make: function (o) {
        o = Object.assign({ tint: null, att: null, scale: 1, bronchi: true }, o || {});
        var g = new THREE.Group(), G = N.glassMat(K, o.tint, o.att), lobes = [];
        var resin = K.mat("sf-resin", { color: 0xf3ecff, roughness: 0.38, transmission: 0.4, thickness: 0.01, transparent: true, clearcoat: 0.8 }, true);
        [-1, 1].forEach(function (side) {
          var geo = new THREE.SphereGeometry(1, 64, 48), p = geo.attributes.position, v = new THREE.Vector3();
          for (var i = 0; i < p.count; i++) {
            v.fromBufferAttribute(p, i);
            var y = (v.y + 1) / 2;                                   /* 0 base, 1 apex */
            var taper = 0.55 + 0.45 * Math.sin(Math.min(1, y * 1.15) * Math.PI * 0.62 + 0.25);
            var x = v.x * 0.062 * taper, z = v.z * 0.062 * taper * 1.05, yy = y * 0.27;
            if (v.x * side < 0) x *= 0.45;                            /* flattened medial face */
            if (side > 0 && v.x < 0 && y < 0.55 && v.z > -0.2) x *= 0.6; /* cardiac notch */
            if (y < 0.12) { var b = y / 0.12; x *= 0.75 + 0.25 * b; z *= 0.75 + 0.25 * b; } /* diaphragm dome underside */
            p.setXYZ(i, x + side * 0.072, yy + 0.01, z);
          }
          geo.computeVertexNormals();
          var m = new THREE.Mesh(geo, G); g.add(m); lobes.push(m);
        });
        if (o.bronchi) {
          var pts = function (a) { return new THREE.CatmullRomCurve3(a.map(function (q) { return new THREE.Vector3(q[0], q[1], q[2]); })); };
          g.add(new THREE.Mesh(new THREE.TubeGeometry(pts([[0, 0.34, 0], [0, 0.27, 0.005], [0, 0.22, 0.008]]), 24, 0.011, 12, false), resin));
          [-1, 1].forEach(function (s) {
            g.add(new THREE.Mesh(new THREE.TubeGeometry(pts([[0, 0.22, 0.008], [s * 0.03, 0.19, 0.01], [s * 0.06, 0.15, 0.012]]), 24, 0.0075, 10, false), resin));
            g.add(new THREE.Mesh(new THREE.TubeGeometry(pts([[s * 0.06, 0.15, 0.012], [s * 0.075, 0.11, 0.02], [s * 0.08, 0.07, 0.025]]), 16, 0.0045, 8, false), resin));
            g.add(new THREE.Mesh(new THREE.TubeGeometry(pts([[s * 0.06, 0.15, 0.012], [s * 0.085, 0.17, 0.0], [s * 0.095, 0.2, -0.01]]), 16, 0.0045, 8, false), resin));
          });
        }
        g.scale.setScalar(o.scale);
        g.userData.lobes = lobes;
        g.userData.anchor = function (side, u, v) { return new THREE.Vector3(side * 0.08 * o.scale, (0.03 + u * 0.22) * o.scale, (v || 0) * 0.03 * o.scale); };
        return shadowAll(g);
      }
    });

    /* SCAN SLAB. A rounded acrylic field w x h x d (default 0.42 x 0.10 x 0.30 m), kind 'other' (periwinkle) or 'screen'
     * (frosted white), with faint engraved scan lines across its top. Origin at the base centre. */
    K.define("scan_slab", {
      size: [0.42, 0.10, 0.30],
      options: { w: 0.42, h: 0.10, d: 0.30, kind: "other", lines: 14 },
      note: "A scan field as a slab of tinted acrylic, drawn to illustrate: kind 'other' periwinkle means a scan ordered for something else, 'screen' frosted white means a screening exam.",
      make: function (o) {
        o = Object.assign({ w: 0.42, h: 0.10, d: 0.30, kind: "other", lines: 14 }, o || {});
        var g = new THREE.Group(), A = N.acrylicMat(K, o.kind);
        K.box(o.w, o.h, o.d, A, 0, 0, 0, Math.min(0.008, o.h / 4), g);
        var L = K.mat("sf-scanline-" + o.kind, { color: o.kind === "screen" ? 0xffffff : 0xc9d0ff, roughness: 0.3, emissive: o.kind === "screen" ? 0x9a9ab8 : 0x5866d8, emissiveIntensity: 0.25, transparent: true, opacity: 0.55 });
        for (var i = 1; i < o.lines; i++) K.box(o.w * 0.94, 0.0008, 0.0016, L, 0, o.h + 0.0002, -o.d / 2 + i * o.d / o.lines, 0, g);
        return shadowAll(g);
      }
    });

    /* NODULE BEAD. A gold bead of radius r (default 7 mm), origin at its centre. */
    K.define("nodule_bead", {
      size: [0.014, 0.014, 0.014],
      options: { r: 0.007 },
      note: "The gold bead that stands for a nodule flagged for a person, drawn to illustrate and far larger than scale when a frame needs it to read.",
      make: function (o) {
        o = Object.assign({ r: 0.007 }, o || {});
        var g = new THREE.Group(), m = new THREE.Mesh(new THREE.SphereGeometry(o.r, 40, 28), N.goldMat(K)); g.add(m);
        return shadowAll(g);
      }
    });

    /* MANILA FOLDER. 0.31 x thick x 0.24 m lying flat, a tab on +z in `tab` hex (CH.OTHER or CH.SCREEN), optional dog ear.
     * CHART CART. A powder coated wire cart 0.9 x 1.0 x 0.5 m on four casters with two shelves; userData.top is the top
     * shelf height. */
    K.define("manila_folder", {
      size: [0.31, 0.02, 0.25],
      options: { thick: 0.02, tab: 0x8c9cf0, tabAt: 0, dog: false, seed: 1 },
      note: "A stuffed manila chart folder lying flat with a coloured tab on +z, drawn to illustrate.",
      make: function (o) {
        o = Object.assign({ thick: 0.02, tab: 0x8c9cf0, tabAt: 0, dog: false, seed: 1 }, o || {});
        var g = new THREE.Group(), M = K.mat("sf-manila", { color: N.MANILA, roughness: 0.82, sheen: 0.25 }, true), Pp = K.mat("sf-sheets", { color: N.PAPER, roughness: 0.9 }, true);
        var r = N.rng(31 + o.seed * 7);
        K.box(0.31, 0.0015, 0.24, M, 0, 0, 0, 0, g);
        var sheets = K.box(0.296, o.thick - 0.003, 0.228, Pp, (r() - 0.5) * 0.006, 0.0015, (r() - 0.5) * 0.006, 0.001, g);
        var top = K.box(0.31, 0.0015, 0.24, M, (r() - 0.5) * 0.004, o.thick - 0.0015, 0, 0, g);
        top.rotation.z = (r() - 0.5) * 0.02;
        var T = K.mat("sf-tab" + o.tab, { color: o.tab, roughness: 0.5, clearcoat: 0.4 }, true);
        K.box(0.06, 0.0018, 0.02, T, -0.1 + o.tabAt * 0.1, o.thick - 0.0015, 0.128, 0.001, g);
        if (o.dog) { var d = K.box(0.03, 0.0015, 0.03, M, 0.14, o.thick + 0.004, 0.105, 0, g); d.rotation.set(0.5, 0, -0.4); }
        return shadowAll(g);
      }
    });
    K.define("chart_cart", {
      size: [0.9, 1.0, 0.5],
      options: { color: 0x5a63a8 },
      note: "A powder coated wire records cart with two shelves on four twin wheel casters. userData.top is the top shelf height.",
      make: function (o) {
        o = Object.assign({ color: 0x5a63a8 }, o || {});
        var g = new THREE.Group(), C = K.mat("sf-cart" + o.color, { color: o.color, metalness: 0.4, roughness: 0.45, clearcoat: 0.4 }, true), R = K.mat("sf-rubber", { color: 0x1d1b26, roughness: 0.85 });
        [[-0.42, -0.22], [0.42, -0.22], [-0.42, 0.22], [0.42, 0.22]].forEach(function (c) {
          K.bar([c[0], 0.12, c[1]], [c[0], 0.98, c[1]], 0.012, C, 10, g);
          var w = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.03, 20), R); w.rotation.x = Math.PI / 2; w.position.set(c[0], 0.045, c[1] + 0.018); g.add(w);
          var w2 = w.clone(); w2.position.z -= 0.036; g.add(w2);
          K.box(0.05, 0.03, 0.05, C, c[0], 0.09, c[1], 0.005, g);
        });
        [0.22, 0.62].forEach(function (y) {
          K.box(0.88, 0.012, 0.48, C, 0, y, 0, 0.004, g);
          for (var x = -0.4; x <= 0.401; x += 0.05) K.bar([x, y + 0.012, -0.24], [x, y + 0.012, 0.24], 0.0035, C, 6, g);
        });
        K.bar([-0.45, 0.98, -0.24], [-0.45, 0.98, 0.24], 0.014, C, 10, g); K.bar([0.45, 0.98, -0.24], [0.45, 0.98, 0.24], 0.014, C, 10, g);
        g.userData.top = 0.634;
        return shadowAll(g);
      }
    });

    /* AGE RULE. A brushed steel rule `length` m long (default 1.0), 0.04 m wide, 6 mm thick, lying on +x, with engraved ticks
     * every `step` units over `span` units, an engraved groove down its centre, a frosted white enamel block from `from` to `to`
     * (in the rule's units) and userData.at(u) giving the world x of unit u. Origin at the rule's centre on the ground. */
    K.define("age_rule", {
      size: [1.0, 0.006, 0.04],
      options: { length: 1.0, span: 90, step: 10, from: null, to: null },
      note: "A brushed steel rule with engraved ticks, a centre groove and an optional frosted white enamel block, drawn to illustrate. userData.at(u) maps a unit to x.",
      make: function (o) {
        o = Object.assign({ length: 1.0, span: 90, step: 10, from: null, to: null }, o || {});
        var g = new THREE.Group(), S = K.mat("sf-rulesteel", { color: 0xcfd6de, metalness: 0.95, roughness: 0.26 }), E = K.mat("sf-engrave", { color: 0x3a3550, metalness: 0.6, roughness: 0.6 });
        var L = o.length, at = function (u) { return -L / 2 + 0.02 + (L - 0.04) * u / o.span; };
        K.box(L, 0.006, 0.04, S, 0, 0, 0, 0.0015, g);
        K.box(L - 0.02, 0.0008, 0.004, E, 0, 0.0056, 0, 0, g);
        for (var u = 0; u <= o.span + 1e-6; u += o.step) K.box(0.0016, 0.0008, u % (o.step * 5) === 0 ? 0.03 : 0.018, E, at(u), 0.0056, -0.005, 0, g);
        for (var u2 = 0; u2 <= o.span + 1e-6; u2 += o.step / 2) K.box(0.0011, 0.0007, 0.009, E, at(u2), 0.0057, -0.0145, 0, g);
        if (o.from != null && o.to != null) {
          var En = K.mat("sf-enamel", { color: N.SCREEN, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05, sheen: 0.3 }, true);
          K.box(at(o.to) - at(o.from), 0.004, 0.026, En, (at(o.to) + at(o.from)) / 2, 0.006, 0.004, 0.0015, g);
        }
        g.userData.at = at;
        return shadowAll(g);
      }
    });

    /* CT GANTRY. A ring housing 2.0 x 1.95 x 0.9 m with a 0.78 m bore centred at 1.05 m, a rounded satin white shell with panel
     * seams, vents and a trim band in `trim` hex, on a plinth; a couch 2.3 m long, top at 0.9 m, on a pedestal, extended
     * `extend` m toward +z with a folded pillow. Front (couch side) on +z. */
    K.define("ct_gantry", {
      size: [2.0, 1.95, 3.2],
      options: { trim: 0x8c9cf0, extend: 0.9, pillow: true },
      note: "An unmarked CT scanner, drawn to illustrate: rounded ring housing with bore, seams, vents and a trim band, and an extended patient couch with a pillow. Front on +z.",
      make: function (o) {
        o = Object.assign({ trim: 0x8c9cf0, extend: 0.9, pillow: true }, o || {});
        var g = new THREE.Group(), W = K.mat("sf-shell", { color: N.SHELL, roughness: 0.32, clearcoat: 0.7, clearcoatRoughness: 0.2 }, true);
        var Sm = K.mat("sf-seam", { color: 0x9d98ad, roughness: 0.6 }), Tr = K.mat("sf-trim" + o.trim, { color: o.trim, roughness: 0.35, clearcoat: 0.5 }, true);
        var Bo = K.mat("sf-bore", { color: 0xdedbe6, roughness: 0.45 }), D = K.mat("sf-dark", { color: 0x2a2440, roughness: 0.7 });
        var cy = 1.05, R0 = 0.39, R1 = 0.97, dep = 0.86;
        var sh = new THREE.Shape(); sh.absarc(0, 0, R1, 0, Math.PI * 2, false);
        var hole = new THREE.Path(); hole.absarc(0, 0, R0, 0, Math.PI * 2, true); sh.holes.push(hole);
        var ring = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: dep, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.05, bevelSegments: 6, curveSegments: 96 }), W);
        ring.position.set(0, cy, -dep / 2); g.add(ring);
        K.box(1.6, cy - 0.5, dep * 0.9, W, 0, 0, 0, 0.05, g);
        var band = new THREE.Mesh(new THREE.TorusGeometry((R0 + R1) / 2 + 0.18, 0.018, 12, 120), Tr); band.position.set(0, cy, dep / 2 + 0.065); g.add(band);
        var seam = new THREE.Mesh(new THREE.TorusGeometry(R0 + 0.12, 0.004, 8, 120), Sm); seam.position.set(0, cy, dep / 2 + 0.064); g.add(seam);
        var tun = new THREE.Mesh(new THREE.CylinderGeometry(R0 - 0.01, R0 - 0.01, dep + 0.1, 64, 1, true), Bo); tun.rotation.x = Math.PI / 2; tun.position.set(0, cy, 0); tun.material.side = THREE.BackSide; g.add(tun);
        for (var i = 0; i < 9; i++) K.box(0.16, 0.006, 0.02, D, 0.62, cy - 0.35 + i * 0.03, dep / 2 + 0.05, 0.002, g);
        K.box(1.7, 0.06, dep + 0.1, K.mat("sf-plinth", { color: 0x8b86a6, roughness: 0.6 }), 0, 0, 0, 0.02, g);
        /* couch */
        var cz = dep / 2 + 0.95 + o.extend * 0.5;
        K.box(0.42, 0.6, 0.9, W, 0, 0, dep / 2 + 1.1, 0.04, g);
        K.box(0.5, 0.08, 2.3, W, 0, 0.6, cz - 0.3, 0.035, g);
        var pad = K.mat("sf-pad", { color: 0x5a63a8, roughness: 0.5, clearcoat: 0.4, sheen: 0.3 }, true);
        K.box(0.44, 0.05, 2.2, pad, 0, 0.68, cz - 0.3, 0.02, g);
        K.bar([-0.26, 0.66, cz - 1.3], [-0.26, 0.66, cz + 0.7], 0.008, steel(), 8, g); K.bar([0.26, 0.66, cz - 1.3], [0.26, 0.66, cz + 0.7], 0.008, steel(), 8, g);
        if (o.pillow) { var pl = K.mat("sf-pillow", { color: 0xf2eefa, roughness: 0.85, sheen: 0.4 }, true); K.box(0.36, 0.08, 0.26, pl, 0, 0.73, cz - 1.1, 0.035, g); }
        g.userData.couchTop = 0.73; g.userData.boreY = cy;
        return shadowAll(g);
      }
    });

    /* CARD RACK. An oak desk rack 0.30 x 0.10 x 0.12 m with `slots` slots (default 9) and userData.slot(i) the centre of slot i. */
    K.define("card_rack", {
      size: [0.30, 0.10, 0.12],
      options: { slots: 9 },
      note: "An oak desk rack with upright slots for cards, drawn to illustrate. userData.slot(i) gives a slot centre.",
      make: function (o) {
        o = Object.assign({ slots: 9 }, o || {});
        var g = new THREE.Group(), O = oak(), n = o.slots, w = 0.30;
        K.box(w, 0.02, 0.12, O, 0, 0, 0, 0.004, g);
        for (var i = 0; i <= n; i++) K.box(0.004, 0.06, 0.11, O, -w / 2 + 0.01 + i * (w - 0.02) / n, 0.02, 0, 0.001, g);
        g.userData.slot = function (i) { return new THREE.Vector3(-w / 2 + 0.01 + (i + 0.5) * (w - 0.02) / n, 0.02, 0); };
        return shadowAll(g);
      }
    });

    /* OAK COUNTER. 3.6 x 0.92 x 0.9 m by default, rounded top edge, drawer fronts on +z, a toe kick. userData.top is its height. */
    K.define("oak_counter", {
      size: [3.6, 0.92, 0.9],
      options: { w: 3.6, d: 0.9, drawers: 6 },
      note: "A continuous quarter sawn oak work counter with a rounded top edge, drawer fronts and a toe kick, drawn to illustrate.",
      make: function (o) {
        o = Object.assign({ w: 3.6, d: 0.9, drawers: 6 }, o || {});
        var g = new THREE.Group(), O = oak(), K2 = K.mat("sf-kick", { color: 0x3b2a4e, roughness: 0.7 });
        K.box(o.w - 0.08, 0.1, o.d - 0.08, K2, 0, 0, -0.03, 0.01, g);
        K.box(o.w - 0.02, 0.76, o.d - 0.04, O, 0, 0.1, 0, 0.012, g);
        K.box(o.w, 0.05, o.d, O, 0, 0.87, 0, 0.02, g);
        for (var i = 0; i < o.drawers; i++) {
          var x = -o.w / 2 + (i + 0.5) * o.w / o.drawers;
          K.box(o.w / o.drawers - 0.03, 0.2, 0.01, O, x, 0.62, o.d / 2 - 0.015, 0.004, g);
          K.bar([x - 0.08, 0.72, o.d / 2 + 0.004], [x + 0.08, 0.72, o.d / 2 + 0.004], 0.006, steel(), 8, g);
        }
        g.userData.top = 0.92;
        return shadowAll(g);
      }
    });

    /* READING BRIDGE. A brushed steel bridge 0.5 x 0.14 x 0.24 m that straddles a card drawer, a thin cyan emissive strip on
     * its underside. Front on +z. */
    K.define("reading_bridge", {
      size: [0.5, 0.14, 0.24],
      options: { glow: 1.2 },
      note: "A small brushed steel bridge with a cyan reading strip, drawn to illustrate the software's station; no screen, no logo.",
      make: function (o) {
        o = Object.assign({ glow: 1.2 }, o || {});
        var g = new THREE.Group(), S = steel(), C = K.mat("sf-strip" + o.glow, { color: 0x061820, emissive: 0x22d3ee, emissiveIntensity: o.glow, roughness: 0.2 });
        K.box(0.03, 0.12, 0.22, S, -0.235, 0, 0, 0.006, g); K.box(0.03, 0.12, 0.22, S, 0.235, 0, 0, 0.006, g);
        K.box(0.5, 0.025, 0.24, S, 0, 0.12, 0, 0.008, g);
        K.box(0.44, 0.006, 0.02, C, 0, 0.113, 0.03, 0.002, g);
        return shadowAll(g);
      }
    });
  };
  N.studioOpts = function (o) { o = o || {}; return { tone: N.TONE, w: (o.w || 4.2) * 1.6, d: (o.d || 3.2) * 1.4, h: 3.2, radius: 0.9, env: 0.95, hemi: 0.7 }; };
  N.roomOpts = function (o) {
    o = o || {};
    return { w: o.w || 4.2, d: o.d || 3.2, h: 3.0, floor: "concrete", wall: o.wall || 0x16161b, window: null, ceiling: o.ceiling !== false, light: o.light == null ? 0.12 : o.light };
  };
  /* a parallel camera `span` metres wide, for a frame that compares lengths and must not foreshorten them */
  N.ortho = function (THREE, R, span) { var w = span / 2, h = w * N.H / N.W; R.camera = new THREE.OrthographicCamera(-w, w, h, -h, 0.01, 40); return R.camera; };
  /* an SVG leader from a label's anchor to a world point, registered for qa's leader check */
  N.leader = function (THREE, R, from, world, what) {
    var at = N.project(THREE, R, world), s = N.svg(), l = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    l.setAttribute("points", from[0] + "," + from[1] + " " + at[0] + "," + at[1]); l.setAttribute("fill", "none"); l.setAttribute("stroke", N.P.ink); l.setAttribute("stroke-width", "3"); l.setAttribute("stroke-linecap", "round");
    s.appendChild(l); (window.__txLeaders = window.__txLeaders || []).push({ target: what, at: at, to: at }); return at;
  };
  /* A CAMERA BEARING FROM THE SUN: the horizontal direction `deg` degrees clockwise (to the right) of the sun's own
   * bearing, so a frame can put the warm seam at its left edge by looking a little right of the sun. */
  N.bearing = function (TXT, deg) {
    var sd = TXT.sunDir(), hx = sd.x, hz = sd.z, n = Math.hypot(hx, hz) || 1; hx /= n; hz /= n;
    var a = -deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
    return [hx * c - hz * s, hz * c + hx * s];
  };
  N.dress = function (cx, o) { o = o || {}; if (TXLOOK.active()) { TXLOOK.footWash(cx, { a: 0.42, height: 230 }); N.typeDark(cx, o); return cx; } N.post(cx, { a: 0.3, veil: 0.35, veilH: 240 }); N.footWash(cx, { a: o.foot || 0.6 }); N.typeDark(cx, { fade: o.fade == null ? 120 : o.fade, pad: o.pad, a: 0.6 }); return cx; };
  /* the deck's rig, read from the chassis declaration, with its acne bias */
  N.rig = function (TXT, R, W, size, target, o) { o = o || {}; TXT.deckRig(R, N.rigSpec(W, size, o.map || 2048), N.rigOpts(target, o)); return N.unacne(R, o.normalBias == null ? 0.02 : o.normalBias); };

  /* THE KEY'S POOL: the declared low key, concentrated where the subject stands. A spot with no falloff, hung on the key's
   * own bearing far enough out that its casts run parallel to the sun's, so it never reads as a second light. */
  N.pool = function (THREE, TXT, R, at, o) {
    o = o || {};
    var r = o.radius || 6, d = r * 7, sd = TXT.sunDir();
    var sp = new THREE.SpotLight(o.color || 0xffc890, o.i == null ? 3 : o.i, 0, Math.atan(r / d), o.penumbra == null ? 0.65 : o.penumbra, 0);
    sp.position.set(at[0] + sd.x * d, at[1] + sd.y * d + (o.lift || 0), at[2] + sd.z * d); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0005; sp.shadow.normalBias = o.normalBias == null ? 0.02 : o.normalBias;
    sp.shadow.camera.near = Math.max(0.1, d * 0.5); sp.shadow.camera.far = d * 1.6;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
  };

  /* THE FLOOD ITSELF: a spot hung on the declared key's bearing, for a frame whose subject sits too low or too small for
   * the directional key to model it; it never comes from another side. */
  N.flood = function (THREE, R, from, at, o) {
    o = o || {};
    var sp = new THREE.SpotLight(o.color || 0xf0f3ff, o.i == null ? 40 : o.i, o.reach || 8, o.angle || 0.4, o.penumbra == null ? 0.55 : o.penumbra, 2);
    sp.position.set(from[0], from[1], from[2]); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0006; sp.shadow.normalBias = 0.01;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
  };
  /* THE LAB GOES DARK: the studio environment lifts the walls to grey, so a frame calls this after the rig. */
  N.darkRoom = function (R, o) {
    o = o || {};
    /* LOOK V2: no dark room. The studio keeps its environment; a frame's call trims the env a touch at most. */
    if (TXLOOK.active()) { if ('environmentIntensity' in R.scene) R.scene.environmentIntensity = Math.max(0.75, R.scene.environmentIntensity || 0.9); return R; }
    R.scene.environmentIntensity = o.env == null ? 0.12 : o.env;
    R.scene.traverse(function (l) { if (!l.isLight) return; if (l.isHemisphereLight || l.isAmbientLight) l.intensity *= (o.amb == null ? 0.35 : o.amb);
      else if (l.isDirectionalLight && !l.castShadow) l.intensity *= (o.fill == null ? 0.4 : o.fill); });
    return R;
  };

  /* THE TYPE BAND GOES TO THE DARK, darken only: a near black gradient from the top of the frame to just under the dek,
   * so the room's far edges behind the type sink rather than strike through it. */
  N.typeDark = function (cx, o) {
    o = o || {};
    if (TXLOOK.active()) return TXLOOK.typeWash(cx, { a: 0.5, fade: Math.max(200, o.fade || 0), pad: o.pad });
    var dek = document.querySelector(".dek"), b = dek ? dek.getBoundingClientRect() : { top: 400, height: 200 };
    var y1 = b.top + b.height + (o.pad == null ? 20 : o.pad), f = o.fade == null ? 90 : o.fade, a = o.a || 0.84;
    var g = cx.createLinearGradient(0, 0, 0, y1 + f); g.addColorStop(0, "rgba(4,5,8," + a + ")"); g.addColorStop(y1 / (y1 + f), "rgba(4,5,8," + (a * 0.9) + ")"); g.addColorStop(1, "rgba(4,5,8,0)");
    if (o.x1 == null) { cx.fillStyle = g; cx.fillRect(0, 0, N.W, y1 + f); return; }
    /* a column only, feathered on its right edge over `xf` px, so no seam is drawn down the frame */
    var c = document.createElement("canvas"); c.width = N.W * 2; c.height = N.H * 2; var k = c.getContext("2d"); k.scale(2, 2);
    k.fillStyle = g; k.fillRect(0, 0, N.W, y1 + f);
    var xf = o.xf || 220, m = k.createLinearGradient(o.x1 - xf, 0, o.x1, 0); m.addColorStop(0, "rgba(0,0,0,1)"); m.addColorStop(1, "rgba(0,0,0,0)");
    k.globalCompositeOperation = "destination-in"; k.fillStyle = m; k.fillRect(0, 0, N.W, N.H);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.drawImage(c, 0, 0); cx.restore();
  };

  /* a DOM label set beside a point in design px, so a leader's `at` and the label share one coordinate */
  N.pinLabel = function (id, at, off) { var el = document.getElementById(id); if (!el) return; el.style.left = Math.round(at[0] + (off ? off[0] : 0)) + "px"; el.style.top = Math.round(at[1] + (off ? off[1] : 0)) + "px"; return el; };

  /* a far lamp placed through the camera: the world point `dist` metres along the ray through screen (sx, sy) */
  N.lampAt = function (THREE, R, sx, sy, dist, size) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(sx / N.W * 2 - 1, 1 - sy / N.H * 2, 0.5).unproject(R.camera).sub(R.camera.position).normalize().multiplyScalar(dist).add(R.camera.position);
    return N.lampGlow(THREE, R, [v.x, v.y, v.z], 0xeef2ff, size || 0.9, 0);
  };


  /* ---- frame helpers, carried from the 2026-11-13 and 2026-11-08 chassis ---------------------------------- */
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.project = function (THREE, R, p) { R.camera.updateMatrixWorld(true); var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera); return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H]; };
  N.aim = function (THREE, R, TXT, from, point, sx, sy, fov) {
    var look = point.slice(), cam = R.camera;
    for (var it = 0; it < 40; it++) {
      TXT.frame(R, { fov: fov, from: from, look: look });
      var q = N.project(THREE, R, point), ex = q[0] - sx, ey = q[1] - sy;
      if (Math.abs(ex) < 0.5 && Math.abs(ey) < 0.5) break;
      cam.updateMatrixWorld(true);
      var right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0), up = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 1);
      var d = new THREE.Vector3(look[0] - from[0], look[1] - from[1], look[2] - from[2]).length(), k = 2 * d * Math.tan(fov * Math.PI / 360) / N.H;
      look = [look[0] + right.x * ex * k - up.x * ey * k, look[1] + right.y * ex * k - up.y * ey * k, look[2] + right.z * ex * k - up.z * ey * k];
    }
    return look;
  };
  N.rigSpec = function (W, size, map) {
    var rim = Object.assign({}, W.rig.rim, { i: (W.rig.rim.i || 0.8) * 0.6 });
    /* the flood is a 5000K LED, near neutral: the preset's faint lavender is warmed a step so white paint reads white */
    /* the key is the window's last light; a frame may scale it through N.KEY_SCALE */
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { i: (W.rig.key.i || 3) * (N.KEY_SCALE || 1), shadowSize: size || 14, mapSize: map || 2048 }) });
  };
  N.rigOpts = function (target, o) { o = o || {}; return { target: target, distance: o.distance || 40, shadowFar: o.shadowFar || 120, normalBias: o.normalBias == null ? 0.02 : o.normalBias }; };
  N.unacne = function (R, nb) { R.scene.traverse(function (l) { if (l.isDirectionalLight && l.castShadow) { l.shadow.normalBias = nb == null ? 0.04 : nb; l.shadow.bias = -0.0004; } }); return R; };
  N.BOUNCE = 0.5;
  N.warm = function (R, k) {
    R.scene.environmentIntensity = k == null ? 0.3 : k;
    if (!R._bounce) { R._bounce = new N.T.HemisphereLight(0x141a26, 0x3c3e42, N.BOUNCE); R.scene.add(R._bounce); }
    return R;
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#D2D6DA", halo = "rgba(3,4,8,0.62)", halo2 = "rgba(3,4,8,0.46)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#06070B; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; color:' + ink + '; font-variation-settings:"opsz" 144; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:34px; font-weight:500; letter-spacing:0.04em; line-height:1.2; text-align:center; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".lab.cyan { color:#8FE0F0; }",
      ".hook, .dek, .lab, .kick, .count, .src { font-feature-settings:\"calt\" 0; }",
      ".hook, .dek, .kick, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }",
      ".tx-site, .src { text-shadow:0 0 2px " + halo + ", 0 1px 4px " + halo2 + "; }"
    ].join("\n") + "\n" + TXLOOK.css(N.TONE);
  };
  /* the bespoke type seat: a soft tint in the tone's deep hue around wherever this frame put its type */
  N.seat = function (cx, o) { return TXLOOK.typeSeat(cx, Object.assign({ tone: N.TONE }, o || {})); };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) { d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px"; });
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS(); document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: N.P.dek });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 80, max: 104, maxLines: 2 });
    N.follow();
  };
  N.glCanvas = function () { var c = document.createElement("canvas"); c.width = N.W * 2; c.height = N.H * 2; return c; };
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE; await document.fonts.ready; N.start(o);
    var TXT = typeof bench === "function" ? bench(THREE) : bench, K = initKit(THREE, TXT);
    N.K = K; N.TXT = TXT; N.installKit(K, THREE, TXT);
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
  };
  N.bootFlat = async function (o) { await document.fonts.ready; N.start(o); return document.getElementById("art").getContext("2d"); };
  N.EXPOSURE = 1.0;
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    N.R = TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * N.EXPOSURE * (o.exposure || 1), tone: W.tone, fov: o.fov || 32, near: o.near || 0.05, far: o.far || 6000 });
    return N.R;
  };
  N.develop = function (shot, glCanvas) {
    if (!shot || !shot.ok) throw new Error("the GPU frame came back black: " + JSON.stringify(shot));
    var cx = document.getElementById("art").getContext("2d"); cx.scale(2, 2); cx.drawImage(glCanvas, 0, 0, N.W, N.H); return cx;
  };
  N.pin = function (THREE, R, id, p, dx, dy) {
    var q = N.project(THREE, R, p), el = document.getElementById(id); if (!el) return q;
    el.style.left = Math.round(q[0] + (dx || 0)) + "px"; el.style.top = Math.round(q[1] + (dy || 0)) + "px"; return q;
  };
  N.glowTex = function (THREE) {
    if (N._glow) return N._glow;
    var c = document.createElement("canvas"); c.width = c.height = 64; var g = c.getContext("2d");
    var gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.18, "rgba(255,255,255,0.6)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); N._glow = new THREE.CanvasTexture(c); return N._glow;
  };
  /* a glow sprite and a small point light at a lamp, so a lit lens reads at feed size and lights what is near it */
  N.lampGlow = function (THREE, R, p, color, size, light) {
    var g = new THREE.Sprite(new THREE.SpriteMaterial({ map: N.glowTex(THREE), color: color, transparent: true, opacity: 0.9, depthWrite: false, fog: false }));
    g.scale.set(size || 0.9, size || 0.9, 1); g.position.set(p[0], p[1], p[2]); R.scene.add(g);
    if (light) { var pl = new THREE.PointLight(color, light, 8, 2); pl.position.set(p[0], p[1], p[2] + 0.3); R.scene.add(pl); }
    return g;
  };
  N.shade = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 60 : o.pad;
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = N.lowRGB();
    if (bottom != null && a > 0) {
      var fade = o.fade || 180, gr = cx.createLinearGradient(0, 0, 0, bottom + fade);
      gr.addColorStop(0, "rgba(" + c + "," + a + ")"); gr.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + (a * 0.85) + ")"); gr.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = gr; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  N.post = function (cx, o) {
    o = o || {};
    if (o.a !== 0) N.shade(cx, { a: o.a, to: o.to, fade: o.fade, pad: o.pad });
    var y0 = N.H - (o.veilH || 240), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(" + N.lowRGB() + "," + (Math.min(0.5, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
  };
  /* a darken-only wash under the footer, so the site line and the claim ids sit on a dark field and no edge strikes them */
  N.footWash = function (cx, o) {
    o = o || {};
    [[o.x == null ? 850 : o.x, 1300, o.r || 460], [180, 1300, 300]].forEach(function (c) {
      var g = cx.createRadialGradient(c[0], c[1], 20, c[0], c[1], c[2]);
      var lc = N.lowRGB(), fa = (o.a || 0.72) * 0.6; g.addColorStop(0, "rgba(" + lc + "," + fa + ")"); g.addColorStop(0.55, "rgba(" + lc + "," + (fa * 0.6) + ")"); g.addColorStop(1, "rgba(" + lc + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, N.H);
    });
  };
  N.lowRGB = function () { var h = N.P.low.replace("#", ""); return [0, 2, 4].map(function (i) { return parseInt(h.slice(i, i + 2), 16); }).join(","); };
  N.svg = function () {
    var s = document.getElementById("over");
    if (!s) { s = document.createElementNS("http://www.w3.org/2000/svg", "svg"); s.id = "over"; s.setAttribute("width", N.W); s.setAttribute("height", N.H);
      s.setAttribute("style", "position:absolute;left:0;top:0;z-index:8;pointer-events:none"); document.body.appendChild(s); }
    return s;
  };
  N.rectOf = function (THREE, R, obj, m) {
    obj.updateMatrixWorld(true); var bb = new THREE.Box3().setFromObject(obj), xs = [], ys = [];
    [bb.min.x, bb.max.x].forEach(function (x) { [bb.min.y, bb.max.y].forEach(function (y) { [bb.min.z, bb.max.z].forEach(function (z) { var q = N.project(THREE, R, [x, y, z]); xs.push(q[0]); ys.push(q[1]); }); }); });
    m = m == null ? 18 : m;
    var x0 = Math.min.apply(null, xs) - m, y0 = Math.min.apply(null, ys) - m, x1 = Math.max.apply(null, xs) + m, y1 = Math.max.apply(null, ys) + m;
    return [x0, y0, x1 - x0, y1 - y0];
  };
  global.CH = N;
})(this);
