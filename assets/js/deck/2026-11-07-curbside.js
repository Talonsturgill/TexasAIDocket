/* deck/2026-11-07-curbside.js — the chassis for the 2026-11-07 deck: Dallas's AI enabled cameras on its sanitation brush
 * trucks (tx-2026-0179). The city's December 2025 briefing says the cameras face sideways from the truck, photograph
 * parcels from the public right of way, and that there is a human in the loop for all actions. The Dallas Morning
 * News counted more than 20,000 code concerns photographed in four months and 57 citations at 34 properties.
 *
 * THE VISUAL ARGUMENT. One parcel, and the paper a camera hands to people. A brick ranch house on a Dallas street at
 * the end of the route, seen from the truck's side camera, then by the analyst, at its mailbox, by the code officer at
 * its curb, and finally by its own resident. The counts are drawn at one paper scale, one letter sheet per item at 0.1
 * mm, so more than 20,000 photographed concerns stand as a column taller than a person and 57 citations are a sheaf a
 * thumb covers. A sheet is a drawing unit and never a claim that anything was printed. Every count a frame draws is
 * read from figures.json in that frame's own code. The chassis types no figure.
 *
 * THE WORLD. lastLight, the house register and a STAGED world: the sun just down, a near black sky, one warm seam low
 * on the key's side. The key is azimuth -50, elevation 9: low and warm from the camera's left front quarter of a camera
 * looking north, so every face toward the reader takes the light from the reader's side and every cast runs back and to
 * the right, long. The rim is the world's cool rim from behind right, drawing each contour on the dark field. Rooms
 * take the same key through a window on the left.
 *
 * THE MATERIALS. Red-brown Dallas brick, sanitation white steel with road film, bead blasted cast aluminium on the
 * camera, bond paper (#ECE6D8) banded in kraft (#A8875C), the southern Dallas share banded in Blackland clay kraft
 * (#3A2E26), concrete curb and walk, a winter lawn over black clay. The accent is bluebonnet #4E5FA8 and it means ONE
 * thing: what the software flagged, carried on paper by a person. The flag box, the notice band, the citation cover.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `camera_pod` (a side facing roadway camera in a finned
 * cast housing with a sun hood, on an L bracket), `body_flank` (a section of a brush truck's dump body side: stake ribs,
 * top rail, rub rail, marker lamp, on its frame rail), `brush_pile` (curbside limbs), `tire` (a passenger tire, lying or
 * standing), `paper_column` (letter sheets in banded bundles of 500 at 0.1 mm a sheet, misregistered, a divider card
 * and a second band colour below a stated sheet count), `letter_tray`, `notice` (a #10 envelope or an open letter
 * sheet with the accent band and an unscannable code panel), `clipboard` (with a sheaf of a stated sheet count) and
 * `plan_folder` (pressboard with a blank date tab). Drawn to illustrate, to no maker's or city's design, in the kit's
 * conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("curbside.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "curbside",
    light: { az: -50, el: 9 },
    sky: "lastLight",
    ground: "#0B0C10",
    material: "#8C5A3C",
    accent: "#4E5FA8",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.06, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.24,
      bloom: { threshold: 0.92, strength: 0.07, radius: 6 },
      grain: { amount: 0.016, size: 2, seed: 20261107 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080; N.H = 1350; N.SEED = 20261107; N.INK = "#EEEAE3";
  N.ACCENT = 0x4E5FA8;       /* brand.yaml's bluebonnet: what the software flagged, carried on paper by a person */
  N.SHEET = 0.0001;          /* one letter sheet, 0.1 mm, the deck's one paper scale (a drawing unit) */
  N.LETTER = [0.2159, 0.2794];
  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.camera_pod) return;
    /* BEAD BLAST AND ROAD FILM, painted in the albedo: a fine speckle on the cast housing, and on the white body a
     * film of road grime in vertical streaks, heavier toward the bottom, with a few drip runs under the top rail. */
    function canvasTex(w, h, paint, rep) { var c = document.createElement("canvas"); c.width = w; c.height = h; paint(c.getContext("2d"), w, h, lcg(rep * 131 + 7));
      var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.repeat.set(rep, rep); return t; }
    var SPECK = canvasTex(256, 256, function (g, w, h, rr) { g.fillStyle = "#b8bbbe"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 26000; i++) { var v = 160 + Math.floor(rr() * 70); g.fillStyle = "rgba(" + v + "," + v + "," + (v + 3) + ",0.45)"; g.fillRect(rr() * w, rr() * h, 1, 1); } }, 6);
    var FILM = canvasTex(512, 512, function (g, w, h, rr) { var gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, "#ebe9e3"); gr.addColorStop(0.7, "#dedbd3"); gr.addColorStop(1, "#c9c4b8"); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      for (var j = 0; j < 60000; j++) { var v = rr(); g.fillStyle = v < 0.5 ? "rgba(90,84,72," + (0.03 + rr() * 0.07) + ")" : "rgba(255,255,250," + (0.03 + rr() * 0.06) + ")"; g.fillRect(rr() * w, rr() * h, 1, 1); }
      g.filter = "blur(0.6px)"; for (var i = 0; i < 90; i++) { var x = rr() * w, y0 = h * (0.68 + rr() * 0.2), len = 12 + rr() * h * 0.14; g.fillStyle = "rgba(96,86,70," + (0.08 + rr() * 0.1) + ")"; g.fillRect(x, y0, 1 + rr() * 1.5, len); } g.filter = "none"; }, 2);
    var ALU = K.mat("cs-alu", { color: 0xd2d5d8, metalness: 0.85, roughness: 0.4, map: SPECK });   /* bead blasted cast aluminium */
    var ALUS = K.mat("cs-alus", { color: 0xa9adb1, metalness: 0.88, roughness: 0.36 });               /* the same casting, small parts, no map */
    var ALUDK = K.mat("cs-aludk", { color: 0x3a3c40, metalness: 0.6, roughness: 0.5 });          /* anodised hood, dark */
    var GLASS = K.finish.glass(0x0d1418);
    var LENS = K.mat("cs-lens", { color: 0x0a0c10, metalness: 0.2, roughness: 0.08 }, true);
    var CABLE = K.mat("cs-cable", { color: 0x16171a, roughness: 0.7 });
    var BOLT = K.mat("cs-bolt", { color: 0xb8bcc0, metalness: 0.95, roughness: 0.28 });
    var WHITE = K.mat("cs-white", { color: 0xf0eee8, metalness: 0.15, roughness: 0.5, map: FILM }); /* sanitation white, sun worn, road film */
    var FRAME = K.mat("cs-frame", { color: 0x1c1d20, metalness: 0.5, roughness: 0.6 });
    var AMBER = K.finish.lamp(0xffa040, 1.6);
    var RUBBER = K.finish.rubber();
    var BARK = K.tex("bark");
    var WOOD = K.mat("cs-limb", { color: 0x8a7a68, roughness: 0.92, map: BARK });
    var WOOD2 = K.mat("cs-limb2", { color: 0xa08a70, roughness: 0.9, map: BARK });
    var LEAF = K.mat("cs-leaf", { color: 0x4a4a2a, roughness: 0.8 });
    /* SHEET EDGES. One tile covers one bundle's 50 mm: fine horizontal streaks at about 1.2 mm, each a little lighter or
     * darker than the next, the way a ream's cut edge reads, with a soft shadow line where one bundle meets the next.
     * Painted in the albedo only; the bundle's height stays a plain box with a soft edge. */
    var edgeTex = (function () {
      var c = document.createElement("canvas"); c.width = 64; c.height = 512; var g = c.getContext("2d"), rr = lcg(511);
      g.fillStyle = "#ece6d8"; g.fillRect(0, 0, 64, 512);
      for (var y = 0; y < 512; y += 3) { var v = 222 + Math.floor((rr() - 0.5) * 34); g.fillStyle = "rgb(" + v + "," + (v - 6) + "," + (v - 18) + ")"; g.fillRect(0, y, 64, 1 + (rr() < 0.3 ? 1 : 0)); }
      var gr = g.createLinearGradient(0, 0, 0, 26); gr.addColorStop(0, "rgba(60,50,40,0.55)"); gr.addColorStop(1, "rgba(60,50,40,0)"); g.fillStyle = gr; g.fillRect(0, 0, 64, 26);
      var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
    })();
    var PAPER = K.mat("cs-paper", { color: 0xffffff, roughness: 0.86, map: edgeTex });
    var PAPER2 = K.mat("cs-paper2", { color: 0xf4efe6, roughness: 0.88, map: edgeTex });
    var SHEETM = K.mat("cs-sheet", { color: 0xeee8da, roughness: 0.85, side: THREE.DoubleSide });
    var KRAFT = K.mat("cs-kraft", { color: 0xa8875c, roughness: 0.9 });
    var CLAY = K.mat("cs-clay", { color: 0x3a2e26, roughness: 0.9 });
    var PRESS = K.mat("cs-press", { color: 0xbfb3a0, roughness: 0.82 });
    var MANILA = K.mat("cs-manila", { color: 0xc9b07c, roughness: 0.86 });
    /* THE ACCENT HOLDS ITS HEX. A warm low key shifts a blue albedo toward grey, so the accent carries most of its
     * colour as emission at the deck hex and stays within the layout gate's 12 Lab window in any pool. */
    var ACC = K.mat("cs-accent", { color: 0x101830, roughness: 0.7, emissive: 0x4E5FA8, emissiveIntensity: 1.0 });
    var MESH = K.mat("cs-mesh", { color: 0x141518, metalness: 0.6, roughness: 0.45 });
    var BOARD = K.mat("cs-board", { color: 0x7a5a3a, roughness: 0.8 });
    var INK = K.mat("cs-ink", { color: 0x2a2a2e, roughness: 0.7 });

    /* CAMERA POD: a side facing roadway camera. The housing is 0.24 wide, 0.18 tall, 0.30 deep with eight cooling fins
     * on top, a sun hood over the port, a flat port glass with the lens behind it, a cable gland and conduit at the
     * back, on an L bracket bolted to whatever it is mounted on. Its lens looks along +z; the bracket foot is at -z. */
    K.define("camera_pod", {
      size: [0.3, 0.32, 0.44],
      options: { seed: 1, bracket: true },
      note: "A side facing roadway camera in a finned cast housing with a sun hood and a flat port, on an L bracket; the lens looks along +z; drawn to illustrate, to no maker's design.",
      make: function (o) {
        var G = new THREE.Group(), y0 = 0.1;
        K.uvBox(K.box(0.24, 0.18, 0.30, ALU, 0, y0, 0, 0.04, G).geometry, 0.3);
        /* the gasket seam between the body and its rear cap, a dark band set in 2 mm */
        K.box(0.236, 0.176, 0.012, ALUDK, 0, y0 + 0.002, -0.105, 0.036, G);
        for (var i = 0; i < 8; i++) K.box(0.012, 0.03, 0.24, ALUS, -0.063 + i * 0.018, y0 + 0.172, -0.02, 0.005, G);
        /* the sun hood: a top plate with a turned down front lip and two cheeks reaching past the port */
        K.box(0.27, 0.012, 0.36, ALUDK, 0, y0 + 0.212, 0.04, 0.005, G);
        K.box(0.27, 0.035, 0.012, ALUDK, 0, y0 + 0.18, 0.215, 0.004, G);
        /* cast detail on both flanks: a raised rib band, a blank recessed nameplate with four rivets, and vent slots */
        [-1, 1].forEach(function (sd) {
          var xs = sd * 0.121;
          K.box(0.006, 0.014, 0.25, ALUS, xs + sd * 0.002, y0 + 0.125, -0.01, 0.003, G);
          K.box(0.004, 0.05, 0.09, ALUDK, xs + sd * 0.001, y0 + 0.045, -0.04, 0.002, G);
          [[-0.08, 0.052], [0.0, 0.052], [-0.08, 0.088], [0.0, 0.088]].forEach(function (q) {
            var rv = new THREE.Mesh(new THREE.SphereGeometry(0.0035, 10, 8), BOLT); rv.position.set(xs + sd * 0.004, y0 + q[1] - 0.002, q[0]); G.add(rv); });
          for (var v = 0; v < 5; v++) K.box(0.004, 0.006, 0.05, FRAME, xs + sd * 0.001, y0 + 0.02 + v * 0.016, 0.085, 0.001, G);
        });
        /* the port bezel, the glass, and the lens barrel seen through it */
        var bz = new THREE.Mesh(new THREE.TorusGeometry(0.052, 0.009, 12, 40), ALUDK); bz.position.set(0, y0 + 0.09, 0.152); G.add(bz);
        var gl = new THREE.Mesh(new THREE.CircleGeometry(0.05, 40), GLASS); gl.position.set(0, y0 + 0.09, 0.153); G.add(gl);
        /* the port glass catching the sky: a soft crescent of reflected light across its upper left */
        var refl = new THREE.Mesh(new THREE.RingGeometry(0.028, 0.044, 32, 1, 1.9, 1.5), K.mat("cs-refl", { color: 0x8a96b0, emissive: 0x5a6680, emissiveIntensity: 0.5, roughness: 0.1, transparent: true, opacity: 0.55 })); refl.position.set(0, y0 + 0.09, 0.1535); G.add(refl);
        var ln = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.034, 0.04, 32), LENS); ln.rotation.x = Math.PI / 2; ln.position.set(0, y0 + 0.09, 0.13); G.add(ln);
        /* four bolts on the face, a status lamp, the gland and conduit at the back */
        [[-0.095, 0.03], [0.095, 0.03], [-0.095, 0.15], [0.095, 0.15]].forEach(function (b) {
          var h = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.006, 12), BOLT); h.rotation.x = Math.PI / 2; h.position.set(b[0], y0 + b[1], 0.151); G.add(h); });
        var gland = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.016, 0.03, 16), FRAME); gland.rotation.x = Math.PI / 2; gland.position.set(0.06, y0 + 0.05, -0.16); G.add(gland);
        TXT.tube([[0.06, y0 + 0.05, -0.17], [0.06, y0 + 0.04, -0.22], [0.08, y0 - 0.06, -0.24], [0.1, -0.25, -0.24]], 0.007, CABLE, {}).traverse(function (m) { if (m.isMesh) G.add(m.clone()); });
        if (o.bracket !== false) {
          K.box(0.14, 0.012, 0.16, FRAME, 0, y0 - 0.012, -0.06, 0.003, G);
          K.box(0.14, 0.22, 0.012, FRAME, 0, y0 - 0.21, -0.145, 0.003, G);
          [[-0.045, -0.06], [0.045, -0.06], [-0.045, -0.17], [0.045, -0.17]].forEach(function (b) {
            var h = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.01, 6), BOLT); h.rotation.x = Math.PI / 2; h.position.set(b[0], y0 + b[1], -0.153); G.add(h); });
        }
        G.userData.lensAt = [0, y0 + 0.09, 0.153];
        return G;
      }
    });

    /* BODY FLANK: a section of a brush truck's dump body side, `length` long along x and its outer face toward +z, on its
     * frame rail. Stake ribs every 0.6 m, a top rail, a rub rail at the floor line, an amber marker lamp, a step and,
     * if asked, the rear dual wheels. The body floor is at 1.1 m and its top rail at 2.7 m. */
    K.define("body_flank", {
      size: [4.2, 2.8, 0.4],
      options: { length: 4.2, wheels: true, seed: 1 },
      note: "A section of a sanitation brush truck's dump body side on its frame rail: sheet steel with stake ribs every 0.6 m, top and rub rails, an amber marker, optional rear duals; face toward +z; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), L = o.length || 4.2, fl = 1.1, top = 2.7, H = top - fl;
        K.uvBox(K.box(L, H, 0.04, WHITE, 0, fl, 0, 0.01, G).geometry, 0.8);
        var POST = K.mat("cs-post", { color: 0xd9d6ce, metalness: 0.15, roughness: 0.5 });
        for (var x = -L / 2 + 0.3; x <= L / 2 - 0.25; x += 0.6) K.box(0.07, H - 0.06, 0.07, POST, x, fl + 0.02, 0.05, 0.014, G);
        K.box(L + 0.06, 0.09, 0.12, POST, 0, top - 0.02, 0.03, 0.02, G);
        K.box(L + 0.06, 0.12, 0.13, POST, 0, fl - 0.04, 0.035, 0.02, G);
        K.box(L, 0.22, 0.32, FRAME, 0, fl - 0.34, -0.12, 0.02, G);
        /* panel seams: the body side is two sheets, a horizontal lap seam at mid height */
        K.box(L, 0.012, 0.008, FRAME, 0, fl + H * 0.48, 0.022, 0.002, G);
        /* conspicuity tape along the rub rail, alternating red and white, the plainest sign this is a truck */
        for (var tx = -L / 2 + 0.05; tx < L / 2 - 0.3; tx += 0.6) {
          K.box(0.3, 0.05, 0.005, K.mat("cs-tapeR", { color: 0xb02020, roughness: 0.35, emissive: 0x300808, emissiveIntensity: 0.4 }), tx + 0.15, fl - 0.02, 0.1, 0, G);
          K.box(0.3, 0.05, 0.005, K.mat("cs-tapeW", { color: 0xe8e8e2, roughness: 0.3, emissive: 0x303030, emissiveIntensity: 0.4 }), tx + 0.45, fl - 0.02, 0.1, 0, G);
        }
        /* the same tape run along the top of the body, under the rail, where a camera on the rail sits over it */
        for (var ux = -L / 2; ux < L / 2 - 0.3; ux += 0.6) {
          K.box(0.3, 0.05, 0.005, K.mat("cs-tapeR", { color: 0xb02020, roughness: 0.35, emissive: 0x300808, emissiveIntensity: 0.4 }), ux + 0.15, top - 0.16, 0.03, 0, G);
          K.box(0.3, 0.05, 0.005, K.mat("cs-tapeW", { color: 0xe8e8e2, roughness: 0.3, emissive: 0x303030, emissiveIntensity: 0.4 }), ux + 0.45, top - 0.16, 0.03, 0, G);
        }
        var mk = K.box(0.1, 0.05, 0.03, AMBER, -L / 2 + 0.55, fl + 0.35, 0.1, 0.01, G);
        K.box(0.5, 0.04, 0.24, MESH, -L / 2 + 0.5, 0.55, 0.12, 0.01, G);
        if (o.wheels) {
          [L / 2 - 1.2].forEach(function (zx) {
            for (var k = 0; k < 2; k++) {
              var t = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 0.28, 40), RUBBER); t.rotation.x = Math.PI / 2; t.position.set(zx, 0.52, -0.05 - k * 0.3); G.add(t);
            }
            var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.02, 32), K.finish.galvanized()); hub.rotation.x = Math.PI / 2; hub.position.set(zx, 0.52, 0.1); G.add(hub);
            for (var b = 0; b < 10; b++) { var a = b / 10 * Math.PI * 2, nut = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.03, 6), BOLT); nut.rotation.x = Math.PI / 2; nut.position.set(zx + Math.cos(a) * 0.17, 0.52 + Math.sin(a) * 0.17, 0.115); G.add(nut); }
            K.box(1.3, 0.04, 0.5, FRAME, zx, 1.07, 0.0, 0.01, G);
            /* the wheel arch: a dark fender lip over the duals, and a mud flap behind them */
            var arch = new THREE.Mesh(new THREE.TorusGeometry(0.64, 0.035, 10, 32, Math.PI), FRAME); arch.position.set(zx, 0.52, 0.12); G.add(arch);
            K.box(0.5, 0.55, 0.012, RUBBER, zx + 0.95, 0.12, 0.05, 0.006, G);
          });
        }
        G.userData.topRail = top; G.userData.floor = fl;
        return G;
      }
    });

    /* BRUSH PILE: curbside limbs about `l` long, `w` deep and `h` tall, seeded tapered branches lying roughly along x
     * with forks and a few leaf clusters. */
    K.define("brush_pile", {
      size: [3.0, 1.1, 1.2],
      options: { l: 3.0, w: 1.2, h: 1.1, limbs: 26, seed: 3 },
      note: "A curbside pile of cut limbs, seeded tapered branches along x with forks and leaf clusters; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), r = lcg(o.seed || 3), L = o.l, Wd = o.w, Hh = o.h;
        /* each limb is a bent tube from a cut butt end, yawed up to 50 degrees off the pile's axis, with two or three
         * forks and a spray of twigs; the pile mounds toward its middle and settles at its ends */
        function limb(p0, dir, len, rad, depth) {
          var pts = [p0], p = p0.slice(), d = dir.slice();
          for (var k = 1; k <= 4; k++) {
            d = [d[0] + (r() - 0.5) * 0.35, d[1] + (r() - 0.5) * 0.25 - 0.04, d[2] + (r() - 0.5) * 0.35];
            var n = Math.hypot(d[0], d[1], d[2]); d = [d[0] / n, d[1] / n, d[2] / n];
            p = [p[0] + d[0] * len / 4, Math.max(rad, p[1] + d[1] * len / 4), p[2] + d[2] * len / 4]; pts.push(p);
          }
          var m = TXT.tube(pts, rad, depth ? WOOD : (r() < 0.5 ? WOOD : WOOD2), {}); m.traverse(function (q) { if (q.isMesh) { q.castShadow = true; q.receiveShadow = true; } }); G.add(m);
          if (!depth) { var cut = new THREE.Mesh(new THREE.CircleGeometry(rad * 0.95, 14), K.mat("cs-cut", { color: 0xb59a74, roughness: 0.85 }));
            cut.position.set(p0[0], p0[1], p0[2]); cut.lookAt(p0[0] - dir[0], p0[1] - dir[1], p0[2] - dir[2]); G.add(cut); }
          if (depth < 2) for (var f = 0; f < (depth ? 2 : 3); f++) {
            var at = pts[1 + Math.floor(r() * 3)], yaw = (r() - 0.5) * 1.8;
            var fd = [dir[0] * Math.cos(yaw) - dir[2] * Math.sin(yaw), 0.25 + r() * 0.4, dir[0] * Math.sin(yaw) + dir[2] * Math.cos(yaw)];
            limb(at, fd, len * (0.35 + r() * 0.25), rad * 0.5, depth + 1);
          }
          if (false && depth === 2) { var lc = new THREE.Mesh(new THREE.IcosahedronGeometry(0.1 + r() * 0.08, 1), LEAF); lc.scale.set(1.3, 0.55, 1); lc.position.set(p[0], p[1], p[2]); G.add(lc); }
        }
        for (var i = 0; i < o.limbs; i++) {
          var u = (r() - 0.5) * L * 0.7, mound = 1 - Math.pow(Math.abs(u) / (L * 0.5), 2);
          var y = 0.04 + Hh * mound * r() * 0.85, z = (r() - 0.5) * Wd;
          var yaw = (r() - 0.5) * 1.6, sgn = r() < 0.5 ? 1 : -1;
          var dir = [sgn * Math.cos(yaw), (r() - 0.6) * 0.3, Math.sin(yaw)];
          limb([u - dir[0] * L * 0.3, y, z - dir[2] * 0.3], dir, L * (0.45 + r() * 0.35), 0.016 + r() * 0.04, 0);
        }
        return G;
      }
    });

    /* TIRE: a passenger tire, 0.66 m across and 0.22 wide, with tread grooves and a sidewall bead; `lying` lays it flat. */
    K.define("tire", {
      size: [0.66, 0.66, 0.22],
      options: { lying: false, seed: 1 },
      note: "A worn passenger tire, 0.66 m diameter, tread grooves and a bead; lying lays it flat; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), T = new THREE.Group();
        var body = new THREE.Mesh(new THREE.TorusGeometry(0.25, 0.085, 18, 48), RUBBER); body.scale.set(1, 1, 1.25); T.add(body);
        for (var g = 0; g < 3; g++) { var gr = new THREE.Mesh(new THREE.TorusGeometry(0.334, 0.006, 6, 64), K.mat("cs-groove", { color: 0x050506, roughness: 0.95 })); gr.position.z = -0.06 + g * 0.06; T.add(gr); }
        if (o.lying) { T.rotation.x = Math.PI / 2; T.position.y = 0.11; } else { T.position.y = 0.335; }
        G.add(T); return G;
      }
    });

    /* PAPER COLUMN: `sheets` letter sheets at 0.1 mm stacked in bundles of 500 (50 mm each), each bundle misregistered by
     * a seeded few millimetres and a degree or two, a kraft band round each, the band switched to Blackland clay kraft
     * below `darkBelow` sheets, a pressboard divider card at `divider` sheets, and the top bundle broken open with loose
     * sheets lifting. Sheet edge striation is in the paper's albedo, never its height. */
    K.define("paper_column", {
      size: [0.24, 2.0, 0.3],
      options: { sheets: 20000, bundle: 500, darkBelow: 0, divider: 0, open: true, seed: 7 },
      note: "Letter sheets at 0.1 mm a sheet in banded bundles of 500, misregistered; darkBelow switches the band colour below that sheet count; divider stands a card proud at that count; a drawing unit, never a claim that paper exists.",
      make: function (o) {
        var G = new THREE.Group(), r = lcg(o.seed || 7), bh = o.bundle * N.SHEET, n = Math.floor(o.sheets / o.bundle), rest = o.sheets - n * o.bundle;
        var Wd = N.LETTER[0], Dp = N.LETTER[1];
        for (var i = 0; i < n; i++) {
          var y = i * bh, top = (i === n - 1) && o.open, h = top ? bh * 0.55 : bh;
          var B = new THREE.Group(); B.position.set((r() - 0.5) * 0.006, y, (r() - 0.5) * 0.006); B.rotation.y = (r() - 0.5) * 0.045;
          var m = K.box(Wd, h - 0.0008, Dp, i % 3 ? PAPER : PAPER2, 0, 0.0004, 0, 0.004, B);
          var mesh = m && m.isMesh ? m : B.children[B.children.length - 1]; if (mesh && mesh.geometry) { K.uvBox(mesh.geometry, bh); mesh.geometry.translate(0, 0, 0); }
          var dark = o.darkBelow && (i + 1) * o.bundle <= o.darkBelow;
          /* the band wraps the bundle's middle, 16 mm tall, standing 1.5 mm proud all round */
          K.box(Wd + 0.003, 0.016, Dp + 0.003, dark ? CLAY : KRAFT, 0, h / 2 - 0.008, 0, 0.0015, B);
          G.add(B);
        }
        var topY = (n - 1) * bh + (o.open ? bh * 0.55 : bh);
        if (rest > 0) { K.box(Wd, rest * N.SHEET, Dp, PAPER, 0, topY, 0, 0.002, G); topY += rest * N.SHEET; }
        /* THE BROKEN TOP: the last bundle's band cut, its sheets spilling in a fan off the top, each a little curled */
        if (o.open) for (var s2 = 0; s2 < 14; s2++) {
          var sh = new THREE.Mesh(new THREE.PlaneGeometry(Wd, Dp, 6, 6), SHEETM);
          var curl = 0.004 + r() * 0.012, p = sh.geometry.attributes.position;
          for (var k = 0; k < p.count; k++) { var u = (p.getX(k) + Wd / 2) / Wd; p.setZ(k, curl * u * u); }
          p.needsUpdate = true; sh.geometry.computeVertexNormals();
          var fan = (s2 / 13 - 0.5) * 1.1 + (r() - 0.5) * 0.15;
          sh.rotation.order = "YXZ"; sh.rotation.set(-Math.PI / 2 + 0.55 + r() * 0.45, fan + Math.PI, 0);
          sh.position.set(Math.sin(fan) * 0.05, topY + 0.002 + s2 * 0.0035, Math.cos(fan) * 0.02 - 0.01); sh.castShadow = true; sh.receiveShadow = true; G.add(sh);
        }
        if (o.divider) K.box(Wd + 0.14, 0.014, Dp + 0.12, K.mat("cs-card", { color: 0xe4dac6, roughness: 0.55 }), 0.05, o.divider * N.SHEET - 0.007, 0.04, 0.002, G);
        G.userData.top = topY;
        return G;
      }
    });

    /* LETTER TRAY: a black steel mesh desk tray 0.26 x 0.07 x 0.35 m, holding `holds`: null, 'notice' or 'folder'. */
    K.define("letter_tray", {
      size: [0.27, 0.08, 0.36],
      options: { holds: null, seed: 1 },
      note: "A black steel mesh letter tray; holds null, 'notice' (an envelope with the accent band) or 'folder' (a manila case folder).",
      make: function (o) {
        var G = new THREE.Group();
        K.box(0.26, 0.004, 0.35, MESH, 0, 0, 0, 0.001, G);
        K.box(0.004, 0.05, 0.35, MESH, -0.128, 0, 0, 0.001, G); K.box(0.004, 0.05, 0.35, MESH, 0.128, 0, 0, 0.001, G);
        K.box(0.26, 0.05, 0.004, MESH, 0, 0, -0.173, 0.001, G); K.box(0.26, 0.02, 0.004, MESH, 0, 0, 0.173, 0.001, G);
        for (var i = 0; i < 9; i++) K.box(0.002, 0.003, 0.33, MESH, -0.112 + i * 0.028, 0.004, 0, 0, G);   /* the floor wires, low, so what the tray holds shows */
        if (o.holds === "notice") { G.add(K.make("notice", { kind: "envelope" })); G.children[G.children.length - 1].position.y = 0.006; }
        if (o.holds === "folder") { K.box(0.24, 0.004, 0.31, MANILA, 0, 0.006, 0, 0.0008, G); K.box(0.08, 0.004, 0.02, MANILA, -0.06, 0.006, -0.162, 0.0008, G);
          K.box(0.23, 0.006, 0.3, PAPER, 0.004, 0.009, 0.002, 0.0008, G); K.box(0.24, 0.002, 0.31, MANILA, 0, 0.015, 0, 0.0006, G); }
        return G;
      }
    });

    /* NOTICE: kind 'envelope' is a #10 envelope 0.241 x 0.105 lying flat with a 12 mm accent band across one end; kind
     * 'sheet' is an open letter sheet with an accent band at the top, greeked lines and a 30 mm code panel whose three
     * finder squares carry no data, so nothing can be scanned. Lies in x-z, face up (+y); `standing` stands it on its
     * long edge facing +z. */
    K.define("notice", {
      size: [0.22, 0.003, 0.28],
      options: { kind: "sheet", standing: false, seed: 1 },
      note: "A courtesy notice: 'envelope' (#10, accent band) or 'sheet' (letter, accent band, greeked lines, an unscannable code panel); drawn to illustrate, carries no real text or code.",
      make: function (o) {
        var G = new THREE.Group(), T = new THREE.Group();
        if (o.kind === "envelope") {
          K.box(0.241, 0.002, 0.105, PAPER, 0, 0, 0, 0.0006, T);
          K.box(0.241, 0.0004, 0.06, ACC, 0, 0.002, -0.0225, 0, T);
          K.box(0.08, 0.0004, 0.02, INK, 0.03, 0.002, 0.03, 0, T);
        } else {
          K.box(N.LETTER[0], 0.0006, N.LETTER[1], PAPER, 0, 0, 0, 0, T);
          K.box(N.LETTER[0], 0.0004, 0.05, ACC, 0, 0.0006, -N.LETTER[1] / 2 + 0.025, 0, T);
          for (var l = 0; l < 9; l++) K.box(0.15 - (l % 3) * 0.02, 0.0003, 0.0035, INK, -0.02 - (l % 3) * 0.01, 0.0006, -0.07 + l * 0.016, 0, T);
          var qx = 0.06, qz = 0.095; K.box(0.034, 0.0004, 0.034, PAPER2, qx, 0.0007, qz, 0, T);
          [[-1, -1], [1, -1], [-1, 1]].forEach(function (f) { K.box(0.009, 0.0004, 0.009, ACC, qx + f[0] * 0.011, 0.0009, qz + f[1] * 0.011, 0, T); });
        }
        if (o.standing) { T.rotation.x = Math.PI / 2; T.position.y = (o.kind === "envelope" ? 0.105 : N.LETTER[1]) / 2; }
        G.add(T); return G;
      }
    });

    /* CLIPBOARD: hardboard 0.23 x 0.32 with a steel clip, carrying `sheets` letter sheets at 0.1 mm under an accent
     * cover; it lies in x-z face up. */
    K.define("clipboard", {
      size: [0.23, 0.02, 0.32],
      options: { sheets: 57, board: true, seed: 1 },
      note: "A clipboard (board:false is the sheaf alone under its cover, a clip at one corner) carrying a sheaf of `sheets` letter sheets at 0.1 mm under an accent cover; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), th = Math.max(0.0006, o.sheets * N.SHEET);
        var b0 = o.board === false ? 0 : 0.004;
        if (b0) K.box(0.23, 0.004, 0.32, BOARD, 0, 0, 0, 0.002, G);
        K.box(N.LETTER[0] - 0.002, th, N.LETTER[1], SHEETM, 0, b0, 0.012, 0.0004, G);
        if (b0) K.box(N.LETTER[0], 0.0008, N.LETTER[1], ACC, 0, b0 + th, 0.012, 0.0003, G);
        else { K.box(N.LETTER[0], 0.0006, N.LETTER[1], PAPER2, 0, b0 + th, 0.012, 0, G);
          K.box(N.LETTER[0], 0.0006, 0.06, ACC, 0, b0 + th + 0.0003, 0.012 - N.LETTER[1] / 2 + 0.03, 0, G);
          for (var ln = 0; ln < 8; ln++) K.box(0.15 - (ln % 3) * 0.02, 0.0003, 0.004, INK, -0.02, b0 + th + 0.0006, -0.06 + ln * 0.018, 0, G); }
        if (b0) K.box(0.11, 0.014, 0.035, BOLT, 0, b0 + th, -0.14, 0.004, G); else K.box(0.012, 0.004, 0.03, BOLT, -0.08, b0 + th, -0.13, 0.001, G);
        G.userData.sheaf = th;
        return G;
      }
    });

    /* PLAN FOLDER: a pressboard folder 0.24 x 0.31 x 0.012 m with a raised date tab left blank. */
    K.define("plan_folder", {
      size: [0.24, 0.012, 0.33],
      options: { seed: 1 },
      note: "A pressboard folder with a raised date tab left blank, for a plan with no date; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group();
        K.box(0.24, 0.004, 0.31, PRESS, 0, 0, 0, 0.001, G);
        K.box(0.232, 0.006, 0.302, PAPER2, 0.002, 0.004, 0.002, 0.0008, G);
        K.box(0.24, 0.003, 0.31, PRESS, 0, 0.01, 0, 0.001, G);
        K.box(0.07, 0.003, 0.022, PAPER, 0.06, 0.01, -0.166, 0.001, G);
        return G;
      }
    });
  };

  /* ONE VEST ACROSS THE DECK. The kit seeds a hi vis colour per pose, so the same officer would change vests between
   * frames 5 and 6; this sets every hi vis cloth on a person to the deck's lime. */
  N.vest = function (person, hex) {
    var HV = [0xc8f02a, 0xf06a1c, 0xd4f230];
    person.traverse(function (m) { if (m.isMesh && m.material && m.material.color && HV.indexOf(m.material.color.getHex()) >= 0) { m.material = m.material.clone(); m.material.color.setHex(hex || 0xc8f02a); } });
    return person;
  };

  /* ---- frame helpers, carried from the 2026-11-06 chassis ---------------------------------- */
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
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { i: (W.rig.key.i || 3) * (N.KEY_SCALE || 1), shadowSize: size || 14, mapSize: map || 2048 }) });
  };
  N.rigOpts = function (target, o) { o = o || {}; return { target: target, distance: o.distance || 40, shadowFar: o.shadowFar || 120, normalBias: o.normalBias == null ? 0.02 : o.normalBias }; };
  N.unacne = function (R, nb) { R.scene.traverse(function (l) { if (l.isDirectionalLight && l.castShadow) { l.shadow.normalBias = nb == null ? 0.04 : nb; l.shadow.bias = -0.0004; } }); return R; };
  /* a warm practical (a porch lamp, a desk lamp, a monitor's spill) that lights what is near it and casts */
  N.lamp = function (THREE, R, at, o) {
    o = o || {};
    var pl = new THREE.PointLight(o.color || 0xffc890, o.i == null ? 4 : o.i, o.reach || 8, 2);
    pl.position.set(at[0], at[1], at[2]); pl.castShadow = !!o.shadow; if (o.shadow) { pl.shadow.mapSize.set(1024, 1024); pl.shadow.bias = -0.0008; }
    R.scene.add(pl); return pl;
  };
  N.spot = function (THREE, R, from, at, o) {
    o = o || {};
    var sp = new THREE.SpotLight(o.color || 0xffd6a8, o.i == null ? 60 : o.i, o.reach || 30, o.angle || 0.5, o.penumbra == null ? 0.6 : o.penumbra, 2);
    sp.position.set(from[0], from[1], from[2]); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0006; sp.shadow.normalBias = 0.02;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
  };
  /* THE TYPE BAND GOES TO THE DARK, darken only, as a column or full width, feathered so no seam is drawn */
  N.typeDark = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), b = dek ? dek.getBoundingClientRect() : { top: 400, height: 200 };
    var y1 = b.top + b.height + (o.pad == null ? 20 : o.pad), f = o.fade == null ? 90 : o.fade, a = o.a || 0.8;
    var g = cx.createLinearGradient(0, 0, 0, y1 + f); g.addColorStop(0, "rgba(4,5,8," + a + ")"); g.addColorStop(y1 / (y1 + f), "rgba(4,5,8," + (a * 0.9) + ")"); g.addColorStop(1, "rgba(4,5,8,0)");
    if (o.x1 == null) { cx.fillStyle = g; cx.fillRect(0, 0, N.W, y1 + f); return; }
    var c = document.createElement("canvas"); c.width = N.W * 2; c.height = N.H * 2; var k = c.getContext("2d"); k.scale(2, 2);
    k.fillStyle = g; k.fillRect(0, 0, N.W, y1 + f);
    var xf = o.xf || 220, m = k.createLinearGradient(o.x1 - xf, 0, o.x1, 0); m.addColorStop(0, "rgba(0,0,0,1)"); m.addColorStop(1, "rgba(0,0,0,0)");
    k.globalCompositeOperation = "destination-in"; k.fillStyle = m; k.fillRect(0, 0, N.W, N.H);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.drawImage(c, 0, 0); cx.restore();
  };
  N.pinLabel = function (id, at, off) { var el = document.getElementById(id); if (!el) return; el.style.left = Math.round(at[0] + (off ? off[0] : 0)) + "px"; el.style.top = Math.round(at[1] + (off ? off[1] : 0)) + "px"; return el; };
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
      ".lab.acc { color:#9AA8E0; }",
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
  /* a cream hairline leader from a label to what it names, ending in a dot, drawn on the art canvas */
  N.lead = function (cx, a, b, col) { cx.save(); cx.strokeStyle = col || "rgba(240,236,228,0.92)"; cx.fillStyle = cx.strokeStyle; cx.lineWidth = 2;
    cx.beginPath(); cx.moveTo(a[0], a[1]); cx.lineTo(b[0], b[1]); cx.stroke(); cx.beginPath(); cx.arc(b[0], b[1], 5, 0, 7); cx.fill(); cx.restore(); };
  global.CH = N;
})(this);
