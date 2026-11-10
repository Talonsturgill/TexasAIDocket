/* deck/2026-11-10-tray.js — the chassis for the 2026-11-10 deck: the Texas Advanced Computing Center retires Frontera
 * after more than eight million jobs, and a UT Southwestern simulation that ran on 64 of its CPU nodes got almost the
 * same speed, in its researcher's words, on eight GPU nodes of Vista (tx-2026-0245).
 *
 * THE VISUAL ARGUMENT. The tray. One machined tray stands for one node, drawn to illustrate and never to size. The same
 * envelope is counted 64 times in brushed stainless for Frontera and eight times in black anodise for Vista, at one
 * scale, so the eight to one is a count a reader can make. No frame draws a speed. The membrane frames are drawn in the
 * same metals: steel heads, a graphite core, copper SNARE bundles. Every count a frame draws is read from figures.json in
 * that frame's own code. The chassis types no figure.
 *
 * THE WORLD. floodlit, a STAGED world, inside one windowless machine hall with no ceiling, the flood hung high and out
 * of frame. The key is azimuth -60, elevation 30: high on the upper left, so every lit edge faces left and up and every
 * cast runs to the lower right. The hall's walls stay in shadow. TXBENCH reliefs read the same declaration and are raked
 * from the frame's upper left.
 *
 * THE ACCENT. comal_lit #8FE0F0, the Comal spring's blue, means ONE thing: a Vista GPU node. Nothing on Frontera and
 * nothing on Horizon is cyan.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `compute_tray` (one node tray, cpu in brushed stainless
 * with an open state showing two copper heat sinks, or gpu in black anodise with a lit cyan strip, pullable on rails),
 * `tray_tower` (an open steel frame holding a stack of trays with light between them), `raised_floor` (graphite laminate
 * tiles with steel edges on pedestals over a dark plenum, any tiles liftable) and `equipment_crate` (a battened plywood
 * crate on a pallet). All in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can
 * queue the lift.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("tray.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "tray",
    light: { az: -60, el: 30 },
    sky: "floodlit",
    ground: "#1A1C20",
    material: "#9EA3A8",
    accent: "#8FE0F0",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.08, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.2,
      bloom: { threshold: 0.9, strength: 0.1, radius: 6 },
      grain: { amount: 0.014, size: 2, seed: 20261110 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  function K_RNG(seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; }
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261110; N.INK = "#EDE6D6";
  N.CYAN = 0x8FE0F0;      /* comal_lit: a Vista GPU node, and nothing else */

  /* ---- the relief materials, shared so every plan and section frame is one set of metals -------- */
  N.ALB = {
    0: [0.010, 0.011, 0.013],   /* graphite carrier */
    1: [0.17, 0.18, 0.195],     /* brushed stainless, dark enough that only its edges and sheen carry light */
    2: [0.62, 0.32, 0.17],      /* copper */
    3: [0.030, 0.034, 0.040],   /* black anodise */
    4: [0.62, 0.98, 1.06],      /* comal_lit strip: held under clipping so the hue survives the key */
    5: [0.006, 0.007, 0.009],   /* groove floor */
    6: [0.045, 0.048, 0.055]    /* graphite core, darker than the steel heads */
  };
  N.SPEC = { 0: [0.15, 20], 1: [0.9, 30], 2: [0.6, 24], 3: [0.9, 30], 4: [0.1, 6], 5: [0.05, 4], 6: [0.08, 8] };
  /* brushing in the albedo, never in the height: a fine grain running across the steel */
  N.tooth = function (X, Y) { return 0.86 + 0.28 * (0.5 + 0.5 * TX.fbm2(X / 70, Y / 1.8, 2)); };
  N.albedo = function (X, Y, m) { var a = N.ALB[m] || N.ALB[0], k = (m === 1 || m === 0 || m === 6) ? N.tooth(X, Y) : 1; return [a[0] * k, a[1] * k, a[2] * k]; };
  N.reliefOpts = function (o) {
    return Object.assign({ scale: 2, albedo: N.albedo, spec: N.SPEC, ambient: 0.13, diffuse: 1.0, ao: 0.9, shadow: 0.9, softness: 4, castLength: 150, dither: true }, o);
  };

  /* ---- the kit models this deck builds ------------------------------------------------------ */
  N.TRAY = { w: 0.44, h: 0.044, d: 0.70, pitch: 0.089 };   /* one tray, and the pitch a tower stacks them at */
  N.FLOOR_H = 0.45;                                          /* the raised floor's walking surface */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.compute_tray) return;
    var STEEL = K.mat("tr-steel", { color: 0xb4b9be, roughness: 0.34, metalness: 1.0 });
    var STEELD = K.mat("tr-steeld", { color: 0x5c6168, roughness: 0.45, metalness: 0.9 });
    var ANOD = K.mat("tr-anod", { color: 0x111317, roughness: 0.4, metalness: 0.7 });
    var BOARD = K.mat("tr-board", { color: 0x1b2420, roughness: 0.7, metalness: 0.1 });
    var COPPER = K.mat("tr-copper", { color: 0xc98a5a, roughness: 0.42, metalness: 0.85 });
    var FAN = K.mat("tr-fan", { color: 0x0c0d0f, roughness: 0.6, metalness: 0.0 });
    var DIMM = K.mat("tr-dimm", { color: 0x2a2d32, roughness: 0.5, metalness: 0.3 });
    var POST = K.mat("tr-post", { color: 0x3a3e44, roughness: 0.5, metalness: 0.8 });
    var CYAN = new THREE.MeshBasicMaterial({ color: N.CYAN, toneMapped: false });   /* unlit and outside the tone curve, so the strip renders comal_lit itself rather than a tone mapped white */
    CYAN.userData = { txWear: false };
    var DOT = new THREE.MeshStandardMaterial({ color: 0x0a0b0d, emissive: 0x000000, roughness: 0.6 });

    /* a perforated bezel: a canvas of holes, used as the bezel's albedo and roughness */
    function perfTex(dark) {
      var c = document.createElement("canvas"); c.width = 256; c.height = 32; var g = c.getContext("2d");
      g.fillStyle = dark ? "#1a1c20" : "#c4c8cc"; g.fillRect(0, 0, 256, 32);
      g.fillStyle = "#050506";
      for (var y = 5; y < 30; y += 6) for (var x = 4 + ((y / 6) % 2) * 3; x < 252; x += 6) { g.beginPath(); g.arc(x, y, 1.6, 0, 7); g.fill(); }
      var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
    }
    var PERF = new THREE.MeshStandardMaterial({ map: perfTex(false), roughness: 0.4, metalness: 0.9 });
    var PERFD = new THREE.MeshStandardMaterial({ map: perfTex(true), roughness: 0.45, metalness: 0.6 });

    /* COMPUTE TRAY: one node, drawn to illustrate and not to size. kind 'cpu' is brushed stainless; open shows the board
     * with `sinks` copper heat sinks, memory rows and a fan wall. kind 'gpu' is black anodise, closed, with a lit cyan
     * strip along the front edge (lit:false turns it dark). Origin on the ground under the tray, front on +z. */
    K.define("compute_tray", {
      size: [0.44, 0.06, 0.74],
      options: { kind: "cpu", open: false, lit: true, sinks: 2, fins: 13 },
      note: "One node tray, drawn to illustrate: rounded stainless or anodised body, perforated front bezel with two handles; cpu open shows copper heat sinks, memory and fans; gpu carries a lit cyan front strip.",
      make: function (o) {
        var G = new THREE.Group(), T = N.TRAY, gpu = o.kind === "gpu", BODY = gpu ? ANOD : STEEL;
        if (!o.open) {
          var body = TXT.roundedBox(T.w, T.h, T.d - 0.02, 0.004, BODY); body.position.set(0, T.h / 2, -0.01); G.add(body);
          /* a lid seam and a label recess on top, so the lid reads as a part */
          var seam = new THREE.Mesh(new THREE.BoxGeometry(T.w - 0.03, 0.0015, 0.004), gpu ? FAN : STEELD); seam.position.set(0, T.h + 0.0002, 0.08); G.add(seam);
        } else {
          var floor = TXT.roundedBox(T.w, 0.004, T.d - 0.02, 0.0015, BODY); floor.position.set(0, 0.002, -0.01); G.add(floor);
          [-1, 1].forEach(function (s) { var wall = TXT.roundedBox(0.003, T.h, T.d - 0.02, 0.001, BODY); wall.position.set(s * (T.w / 2 - 0.0015), T.h / 2, -0.01); G.add(wall);
            var lip = TXT.roundedBox(0.012, 0.003, T.d - 0.02, 0.001, BODY); lip.position.set(s * (T.w / 2 - 0.006), T.h, -0.01); G.add(lip); });
          var board = new THREE.Mesh(new THREE.BoxGeometry(T.w - 0.02, 0.002, T.d - 0.12), BOARD); board.position.set(0, 0.006, 0.0); G.add(board);
          var n = o.sinks || 2;
          for (var k = 0; k < n; k++) {
            var cx = (k - (n - 1) / 2) * 0.15, cz = 0.04;
            var base = TXT.roundedBox(0.09, 0.008, 0.09, 0.002, COPPER); base.position.set(cx, 0.011, cz); G.add(base);
            var nf = o.fins || 13;
            for (var f = 0; f < nf; f++) { var fin = new THREE.Mesh(new THREE.BoxGeometry(0.0012, 0.026, 0.088), COPPER); fin.position.set(cx - 0.042 + f * (0.084 / (nf - 1)), 0.028, cz); G.add(fin); }
            /* memory either side of each socket */
            [-1, 1].forEach(function (s) { for (var m = 0; m < 3; m++) { var dm = new THREE.Mesh(new THREE.BoxGeometry(0.0035, 0.03, 0.13), DIMM); dm.position.set(cx + s * (0.058 + m * 0.009), 0.022, cz); G.add(dm); } });
          }
          /* the fan wall at the back */
          for (var q = 0; q < 6; q++) { var fan = TXT.roundedBox(0.04, 0.038, 0.028, 0.003, FAN); fan.position.set(-0.17 + q * 0.068, 0.022, -0.24); G.add(fan);
            var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.03, 16), STEELD); hub.rotation.x = Math.PI / 2; hub.position.set(-0.17 + q * 0.068, 0.022, -0.24); G.add(hub); }
        }
        /* the front bezel, perforated, and two handles */
        var bez = new THREE.Mesh(new THREE.BoxGeometry(T.w, T.h, 0.012), gpu ? PERFD : PERF); bez.position.set(0, T.h / 2, T.d / 2 - 0.006); G.add(bez);
        [-1, 1].forEach(function (s) { var h = TXT.roundedBox(0.012, T.h * 0.7, 0.026, 0.004, gpu ? STEELD : STEEL); h.position.set(s * (T.w / 2 - 0.02), T.h / 2, T.d / 2 + 0.012); G.add(h); });
        if (gpu) {
          var strip = new THREE.Mesh(new THREE.BoxGeometry(T.w - 0.08, 0.014, 0.004), o.lit ? CYAN : DOT); strip.position.set(0, 0.012, T.d / 2 + 0.001); G.add(strip);   /* a light bar a third of the bezel tall, so it reads at feed size */
          if (o.lit) { var led = new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.004, 0.003), CYAN); led.position.set(T.w / 2 - 0.05, T.h - 0.01, T.d / 2 + 0.001); G.add(led); }
        } else {
          var dot = new THREE.Mesh(new THREE.BoxGeometry(0.006, 0.004, 0.003), DOT); dot.position.set(T.w / 2 - 0.05, T.h - 0.01, T.d / 2 + 0.001); G.add(dot);
        }
        G.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return G;
      }
    });

    /* TRAY TOWER: an open steel frame holding `count` trays at the tray pitch, light between them. pull (metres) draws
     * the top tray out toward +z on two slide rails. */
    K.define("tray_tower", {
      size: [0.5, 0.78, 0.74],
      options: { kind: "cpu", count: 8, lit: true, pull: 0, openTop: false },
      note: "An open four post frame holding a stack of compute_tray at a fixed pitch, drawn to illustrate one tray per node.",
      make: function (o) {
        var G = new THREE.Group(), T = N.TRAY, n = o.count || 8, H = n * T.pitch + 0.03;
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (c) { var p = TXT.roundedBox(0.018, H, 0.018, 0.003, POST); p.position.set(c[0] * (T.w / 2 + 0.014), H / 2, c[1] * (T.d / 2 - 0.02)); G.add(p); });
        /* a base frame and a top frame */
        [0.006, H - 0.006].forEach(function (y) { [-1, 1].forEach(function (s) { var r = TXT.roundedBox(T.w + 0.046, 0.012, 0.016, 0.003, POST); r.position.set(0, y, s * (T.d / 2 - 0.02)); G.add(r); }); });
        for (var i = 0; i < n; i++) {
          var y = 0.02 + i * T.pitch, top = i === n - 1;
          var t = K.make("compute_tray", { kind: o.kind, lit: o.lit, open: top && o.openTop });
          t.position.set(0, y, top && o.pull ? o.pull : 0); G.add(t);
          [-1, 1].forEach(function (s) { var rail = TXT.roundedBox(0.008, 0.012, T.d - 0.04, 0.002, STEELD); rail.position.set(s * (T.w / 2 + 0.006), y + 0.016, 0); G.add(rail);
            if (top && o.pull) { var ext = TXT.roundedBox(0.006, 0.01, o.pull + 0.1, 0.002, STEEL); ext.position.set(s * (T.w / 2 + 0.006), y + 0.016, T.d / 2 - 0.05 + o.pull / 2); G.add(ext); } });
        }
        G.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        G.userData.topY = H;
        return G;
      }
    });

    /* RAISED FLOOR: cols x rows tiles of `tile` metres with tops at FLOOR_H on pedestals over a dark plenum. `lift` lists
     * tile indices (row * cols + col) taken up, opening the plenum; `perf` lists perforated tiles. Origin under the centre. */
    K.define("raised_floor", {
      size: [8.4, 0.45, 7.2],
      options: { cols: 14, rows: 12, tile: 0.6, lift: [], perf: [] },
      note: "A data hall raised floor: graphite laminate tiles with steel edges at 0.45 m on pedestals, any tiles liftable to show the plenum.",
      make: function (o) {
        var G = new THREE.Group(), S = o.tile, C = o.cols, Rw = o.rows, Hf = N.FLOOR_H, lift = {}, perf = {};
        (o.lift || []).forEach(function (i) { lift[i] = 1; }); (o.perf || []).forEach(function (i) { perf[i] = 1; });
        /* high pressure laminate: a fine speckle, scuffs where carts roll and a darker rim of grime, in the albedo */
        var lc = document.createElement("canvas"); lc.width = lc.height = 256; var lg = lc.getContext("2d"), lr = K_RNG(733);
        lg.fillStyle = "#2a2d33"; lg.fillRect(0, 0, 256, 256);
        for (var q = 0; q < 2600; q++) { var v = 30 + (lr() * 34 | 0); lg.fillStyle = "rgba(" + v + "," + (v + 3) + "," + (v + 8) + ",0.55)"; lg.fillRect(lr() * 256, lr() * 256, 1 + lr() * 2, 1 + lr() * 2); }
        for (var q2 = 0; q2 < 14; q2++) { lg.strokeStyle = "rgba(10,11,13," + (0.25 + lr() * 0.35) + ")"; lg.lineWidth = 0.6 + lr() * 1.4; lg.beginPath(); var sx = lr() * 256, sy = lr() * 256; lg.moveTo(sx, sy); lg.lineTo(sx + (lr() - 0.5) * 120, sy + (lr() - 0.5) * 40); lg.stroke(); }
        var rim = lg.createRadialGradient(128, 128, 90, 128, 128, 182); rim.addColorStop(0, "rgba(0,0,0,0)"); rim.addColorStop(1, "rgba(0,0,0,0.45)"); lg.fillStyle = rim; lg.fillRect(0, 0, 256, 256);
        var ltex = new THREE.CanvasTexture(lc); ltex.colorSpace = THREE.SRGBColorSpace; ltex.anisotropy = 4;
        var LAM = new THREE.MeshStandardMaterial({ map: ltex, color: 0xffffff, roughness: 0.62, metalness: 0.05 });
        var EDGE = K.mat("tr-edge", { color: 0x6a6f76, roughness: 0.4, metalness: 0.9 });
        var PLEN = K.mat("tr-plen", { color: 0x08090b, roughness: 0.9, metalness: 0 });
        var PERFT = new THREE.MeshStandardMaterial({ map: (function () { var c = document.createElement("canvas"); c.width = c.height = 128; var g = c.getContext("2d"); g.fillStyle = "#2a2d32"; g.fillRect(0, 0, 128, 128); g.fillStyle = "#060607";
          for (var y = 6; y < 124; y += 8) for (var x = 6; x < 124; x += 8) { g.beginPath(); g.arc(x, y, 2.2, 0, 7); g.fill(); } var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })(), roughness: 0.55, metalness: 0.3 });
        var geo = TXT.roundedBox(S - 0.004, 0.03, S - 0.004, 0.003, LAM).geometry, egeo = new THREE.BoxGeometry(S, 0.006, S);
        var solid = [], holed = [];
        for (var r = 0; r < Rw; r++) for (var c = 0; c < C; c++) { var i = r * C + c; if (lift[i]) continue; (perf[i] ? holed : solid).push([(c - (C - 1) / 2) * S, (r - (Rw - 1) / 2) * S]); }
        function inst(list, mat, g, y) { if (!list.length) return; var im = new THREE.InstancedMesh(g, mat, list.length), M = new THREE.Matrix4();
          list.forEach(function (p, k) { M.makeTranslation(p[0], y, p[1]); im.setMatrixAt(k, M); }); im.castShadow = true; im.receiveShadow = true; G.add(im); }
        inst(solid, LAM, geo, Hf - 0.015); inst(holed, PERFT, geo, Hf - 0.015);
        inst(solid.concat(holed), EDGE, egeo, Hf - 0.033);
        /* the plenum and its pedestals, visible where tiles are up */
        var pl = new THREE.Mesh(new THREE.BoxGeometry(C * S, 0.02, Rw * S), PLEN); pl.position.set(0, 0.01, 0); pl.receiveShadow = true; G.add(pl);
        var ped = [];
        for (var rr = 0; rr <= Rw; rr++) for (var cc = 0; cc <= C; cc++) ped.push([(cc - C / 2) * S, (rr - Rw / 2) * S]);
        var pg = new THREE.CylinderGeometry(0.012, 0.012, Hf - 0.04, 10), pim = new THREE.InstancedMesh(pg, EDGE, ped.length), MM = new THREE.Matrix4();
        ped.forEach(function (p, k) { MM.makeTranslation(p[0], (Hf - 0.04) / 2, p[1]); pim.setMatrixAt(k, MM); }); pim.castShadow = true; G.add(pim);
        G.userData.tileAt = function (c, r) { return [(c - (C - 1) / 2) * S, Hf, (r - (Rw - 1) / 2) * S]; };
        G.userData.keepOrigin = true;
        return G;
      }
    });

    /* EQUIPMENT CRATE: a battened plywood crate on a hardwood pallet, closed. Origin on the ground, front on +z. */
    K.define("equipment_crate", {
      size: [1.2, 1.25, 1.0],
      options: { w: 1.2, h: 1.1, d: 1.0 },
      note: "A battened plywood shipping crate on a pallet, closed and unmarked.",
      make: function (o) {
        var G = new THREE.Group();
        var c = document.createElement("canvas"); c.width = 256; c.height = 256; var g = c.getContext("2d"), rr = K_RNG(311);
        g.fillStyle = "#9b7a55"; g.fillRect(0, 0, 256, 256);
        for (var i = 0; i < 90; i++) { g.strokeStyle = "rgba(" + (60 + rr() * 40 | 0) + "," + (40 + rr() * 25 | 0) + ",20," + (0.15 + rr() * 0.25) + ")"; g.lineWidth = 0.6 + rr() * 1.6; g.beginPath(); var y0 = rr() * 256; g.moveTo(0, y0); for (var x = 0; x <= 256; x += 16) g.lineTo(x, y0 + Math.sin(x * 0.03 + i) * 4 + rr() * 2); g.stroke(); }
        var tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
        var PLY = new THREE.MeshStandardMaterial({ map: tex, color: 0xffffff, roughness: 0.82, metalness: 0 });
        var BAT = K.mat("tr-batten", { color: 0x7a5c3c, roughness: 0.85, metalness: 0 });
        var PAL = K.mat("tr-pallet", { color: 0x6b5236, roughness: 0.9, metalness: 0 });
        var ph = 0.14;
        /* pallet: three runners and seven deck boards */
        [-1, 0, 1].forEach(function (s) { var b = TXT.roundedBox(0.09, 0.1, o.d, 0.004, PAL); b.position.set(s * (o.w / 2 - 0.08), 0.05, 0); G.add(b); });
        for (var k = 0; k < 7; k++) { var db = TXT.roundedBox(o.w, 0.022, 0.1, 0.003, PAL); db.position.set(0, 0.111, -o.d / 2 + 0.05 + k * (o.d - 0.1) / 6); G.add(db); }
        var box = TXT.roundedBox(o.w - 0.04, o.h, o.d - 0.04, 0.006, PLY); box.position.set(0, ph + o.h / 2, 0); G.add(box);
        /* battens round every face's edges and one across the middle */
        var W = o.w - 0.02, D = o.d - 0.02;
        [[W, 0.07, 0.025, 0, ph + 0.035, D / 2], [W, 0.07, 0.025, 0, ph + o.h - 0.035, D / 2], [W, 0.07, 0.025, 0, ph + o.h / 2, D / 2],
         [W, 0.07, 0.025, 0, ph + 0.035, -D / 2], [W, 0.07, 0.025, 0, ph + o.h - 0.035, -D / 2],
         [0.025, 0.07, D, W / 2, ph + 0.035, 0], [0.025, 0.07, D, W / 2, ph + o.h - 0.035, 0], [0.025, 0.07, D, -W / 2, ph + 0.035, 0], [0.025, 0.07, D, -W / 2, ph + o.h - 0.035, 0],
         [0.07, o.h, 0.025, W / 2 - 0.035, ph + o.h / 2, D / 2], [0.07, o.h, 0.025, -W / 2 + 0.035, ph + o.h / 2, D / 2]].forEach(function (b) {
          var m = TXT.roundedBox(b[0], b[1], b[2], 0.004, BAT); m.position.set(b[3], b[4], b[5]); G.add(m); });
        G.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return G;
      }
    });
  };

  /* THE HALL: one windowless machine hall with no ceiling, the flood hung high out of frame. A frame calls TXT.interior
   * itself with these options, because a room is the frame's own decision to stand somewhere. */
  N.roomOpts = function (o) {
    o = o || {};
    return { w: o.w || 16, d: o.d || 16, h: 4.2, floor: "concrete", wall: o.wall || 0x15171b, window: null, ceiling: false, light: o.light == null ? 0.08 : o.light };
  };
  /* the raised floor, placed so its walking surface is at FLOOR_H, with the hall's own floor as the slab under it */
  N.floor = function (TXT, R, K, o) {
    var f = K.make("raised_floor", o || {}); TXT.add(R, f); return f;
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
  /* THE HALL GOES COLD AND DARK: the studio environment lifts the walls to grey, so a frame calls this after the rig. */
  N.darkHall = function (R, o) {
    o = o || {};
    R.scene.environmentIntensity = o.env == null ? 0.08 : o.env;
    R.scene.traverse(function (l) { if (!l.isLight) return; if (l.isHemisphereLight || l.isAmbientLight) l.intensity *= (o.amb == null ? 0.35 : o.amb);
      else if (l.isDirectionalLight && !l.castShadow) l.intensity *= (o.fill == null ? 0.4 : o.fill); });   /* the preset's lavender fill lit the floor periwinkle; the hall keeps only a trace of it */
    return R;
  };

  /* THE TYPE BAND GOES TO THE DARK, darken only: a near black gradient from the top of the frame to just under the dek,
   * so the room's far edges behind the type sink rather than strike through it. */
  N.typeDark = function (cx, o) {
    o = o || {};
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


  /* ---- frame helpers, carried from the 2026-11-08 chassis ---------------------------------- */
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
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".lab.cyan { color:#8FE0F0; }",
      ".hook, .dek, .lab, .kick, .count, .src { font-feature-settings:\"calt\" 0; }",
      ".hook, .dek, .kick, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }",
      ".tx-site, .src { text-shadow:0 0 2px " + halo + ", 0 1px 4px " + halo2 + "; }"
    ].join("\n");
  };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) { d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px"; });
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS(); document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D2D6DA" });
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
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "5,6,10";
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
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(5,6,10," + (Math.min(0.5, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
  };
  /* a darken-only wash under the footer, so the site line and the claim ids sit on a dark field and no edge strikes them */
  N.footWash = function (cx, o) {
    o = o || {};
    [[o.x == null ? 850 : o.x, 1300, o.r || 460], [180, 1300, 300]].forEach(function (c) {
      var g = cx.createRadialGradient(c[0], c[1], 20, c[0], c[1], c[2]);
      g.addColorStop(0, "rgba(5,6,10," + (o.a || 0.72) + ")"); g.addColorStop(0.55, "rgba(5,6,10," + ((o.a || 0.72) * 0.6) + ")"); g.addColorStop(1, "rgba(5,6,10,0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, N.H);
    });
  };
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
