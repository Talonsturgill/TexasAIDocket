/* deck/2026-11-08-plate.js — the chassis for the 2026-11-08 deck: Texas A&M AgriLife's AlphaFold-Multimer screen of
 * the human mitochondrial proteome (tx-2026-0244). The team turned the structure tool into a yes or no classifier,
 * ran it on every pairing of 1123 proteins, and kept 2,895 of 630,003 pairs as likely.
 *
 * THE VISUAL ARGUMENT. The plate. The half matrix is a made object: a black anodised plate whose triangle holds one
 * cell per pair, so the triangle IS the screen. Brass marks a likely pair and nothing else. A space-filling teaching
 * model of two proteins is the question the plate answers. Every count a frame draws is read from figures.json in that
 * frame's own code. The chassis types no figure.
 *
 * THE WORLD. lastLight, a STAGED world, inside one dark lab: a black epoxy bench under one window on the left wall at
 * the day's last light. The key is azimuth -55, elevation 14: low on the upper left, so every lit edge faces left and
 * up and every cast runs to the lower right. The back wall stays in shadow. TXBENCH reliefs read the same declaration
 * and are raked from the frame's upper left.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `protein_pair` (a space-filling teaching model of two
 * protein chains, drawn to illustrate and never a real structure), `lab_bench` (a black epoxy bench top on steel
 * casework), `half_matrix_plate` (the anodised triangle with a stepped hypotenuse and a corner pocket), `pair_block`
 * (the brass block of every likely pair), `microtube` and `tube_rack`, `petri_plate` (a yeast plate, inverted, with
 * agar and colonies) and `culture_flask`. All in the kit's conventions (metres, y up, origin on the ground, front on
 * +z) so Phase 17 can queue the lift.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("plate.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "plate",
    light: { az: -55, el: 14 },
    sky: "lastLight",
    ground: "#0D0E10",
    material: "#141416",
    accent: "#C9B393",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.08, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.2,
      bloom: { threshold: 0.92, strength: 0.08, radius: 6 },
      grain: { amount: 0.014, size: 2, seed: 20261108 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  function K_RNG(seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; }
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261108; N.INK = "#EDE6D6";
  N.BRASS = 0xC9B393;      /* brand.yaml's dust as brass: a likely pair, and nothing else */

  /* ---- the relief materials, shared so the plate is one metal on every plan frame --------------- */
  N.ALB = {
    0: [0.011, 0.012, 0.015],   /* black anodise */
    1: [0.060, 0.064, 0.072],   /* satin milled aluminium */
    2: [2.3, 1.62, 0.66],      /* brass, bright enough that a flat top under a 14 degree key still reads as brass */
    3: [0.045, 0.034, 0.024],   /* blackened bronze */
    4: [0.20, 0.21, 0.22],      /* bead blasted steel */
    5: [0.006, 0.006, 0.008],   /* groove floor */
    6: [3.4, 2.5, 1.1]          /* a brass bevel catching the key */
  };
  N.SPEC = { 0: [0.25, 30], 1: [0.4, 14], 2: [0.55, 9], 3: [0.4, 8], 4: [0.2, 6], 5: [0.05, 4], 6: [0.6, 8] };
  /* tool marks in the albedo, never in the height: a fine stepover running across the plate */
  N.tooth = function (X, Y) { return 0.86 + 0.28 * (0.5 + 0.5 * TX.fbm2(X / 60, Y / 2.2, 2)); };
  N.albedo = function (X, Y, m) { var a = N.ALB[m] || N.ALB[0], k = (m === 1 || m === 0) ? N.tooth(X, Y) : 1; return [a[0] * k, a[1] * k, a[2] * k]; };
  N.reliefOpts = function (o) {
    return Object.assign({ scale: 2, albedo: N.albedo, spec: N.SPEC, ambient: 0.14, diffuse: 1.0, ao: 0.9, shadow: 0.9, softness: 4, castLength: 140, dither: true }, o);
  };

  /* ---- the kit models this deck builds ------------------------------------------------------ */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.protein_pair) return;
    var BONE = K.mat("pl-bone", { color: 0xd4ccbc, roughness: 0.62, metalness: 0.0 });
    var BRASS = K.mat("pl-brass", { color: 0xd8c690, metalness: 1.0, roughness: 0.44 });
    var BRONZE = K.mat("pl-bronze", { color: 0x3a2e22, metalness: 0.75, roughness: 0.46 });
    var EPOXY = K.mat("pl-epoxy", { color: 0x0d0e10, roughness: 0.42, metalness: 0.0 }, true);
    var CASE = K.mat("pl-case", { color: 0x2c3036, roughness: 0.55, metalness: 0.35 });
    var ANOD = K.mat("pl-anod", { color: 0x121316, roughness: 0.38, metalness: 0.65 });
    var SATIN = K.mat("pl-satin", { color: 0x3a3e44, roughness: 0.42, metalness: 0.85 });
    var SLATE = K.mat("pl-slate", { color: 0x4a5058, roughness: 0.6, metalness: 0.0 });
    var PP = new THREE.MeshPhysicalMaterial({ color: 0xdfe3e6, roughness: 0.3, metalness: 0, transparent: true, opacity: 0.8 });   /* milky polypropylene, cool white */
    var PS = new THREE.MeshPhysicalMaterial({ color: 0xe8ecef, roughness: 0.08, metalness: 0, transparent: true, opacity: 0.32, clearcoat: 1, clearcoatRoughness: 0.05, depthWrite: false });   /* clear polystyrene: transmission banded the lathed lids into wedges */
    var AGAR = new THREE.MeshPhysicalMaterial({ color: 0xb98a4c, roughness: 0.35, metalness: 0, sheen: 0.4, sheenColor: 0xe0a060 });
    var COLONY = K.mat("pl-colony", { color: 0xe4d8c3, roughness: 0.55 });
    var MEDIUM = new THREE.MeshPhysicalMaterial({ color: 0xb4583e, roughness: 0.2, transparent: true, opacity: 0.75 });
    var CAPW = K.mat("pl-cap", { color: 0x2a3a52, roughness: 0.45 });
    var TAPE = K.mat("pl-tape", { color: 0xe6dfcf, roughness: 0.8 });

    /* A FOLD: a seeded chain of residues, helices joined by loops, pulled into a compact globule around `c`. */
    function fold(seed, n, c) {
      var rnd = K.rng(seed), pts = [], C = new THREE.Vector3(c[0], c[1], c[2]), p = C.clone(), dir = new THREE.Vector3(1, 0, 0);
      while (pts.length < n) {
        var helix = rnd() < 0.6, L = helix ? 18 + Math.floor(rnd() * 14) : 6 + Math.floor(rnd() * 8);
        var axis = new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).normalize();
        var u = new THREE.Vector3().crossVectors(axis, new THREE.Vector3(0, 1, 0.3)).normalize(), v = new THREE.Vector3().crossVectors(axis, u);
        for (var i = 0; i < L && pts.length < n; i++) {
          var step;
          if (helix) { var a = i * 1.745, b = a - 1.745;
            step = axis.clone().multiplyScalar(0.15).add(u.clone().multiplyScalar((Math.cos(a) - Math.cos(b)) * 0.23)).add(v.clone().multiplyScalar((Math.sin(a) - Math.sin(b)) * 0.23)); }
          else { dir.add(new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).multiplyScalar(0.8)).normalize(); step = dir.clone().multiplyScalar(0.38); }
          var toC = C.clone().sub(p), dc = toC.length(); step.add(toC.multiplyScalar(dc > 1.6 ? 0.22 : 0.06));
          p = p.clone().add(step); pts.push(p);
        }
      }
      return pts;
    }
    /* each residue as three overlapping atom spheres, one instanced mesh per chain */
    function atoms(pts, mat, seed) {
      var g = new THREE.SphereGeometry(0.26, 36, 26), im = new THREE.InstancedMesh(g, mat, pts.length * 3), M = new THREE.Matrix4(), q = new THREE.Quaternion(), rnd = K.rng(seed), c = 0;
      pts.forEach(function (p) { for (var s = 0; s < 3; s++) { var o = new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).multiplyScalar(0.34), sc = 0.8 + rnd() * 0.5;
        M.compose(p.clone().add(o), q, new THREE.Vector3(sc, sc, sc)); im.setMatrixAt(c, M);
        var k = 0.9 + rnd() * 0.16; im.setColorAt(c++, new THREE.Color(k, k, k)); } });
      im.castShadow = true; im.receiveShadow = true; return im;
    }

    /* PROTEIN PAIR: a space-filling teaching model of two protein chains on a short black stand, drawn to illustrate.
     * state 'seated' docks the two globules face to face; 'apart' parts them along x by `gap` metres. `matA`/`matB`
     * pick each chain's material ('bone', 'brass' or 'bronze'). Origin on the bench under the stand. */
    K.define("protein_pair", {
      size: [0.26, 0.2, 0.16],
      options: { state: "seated", gap: 0.03, matA: "bone", matB: "brass", unit: 0.03, seedA: 7, seedB: 19, stand: true },
      note: "A space-filling teaching model of two protein chains, three atom spheres per residue on a seeded helix and loop fold; drawn to illustrate, never a real structure.",
      make: function (o) {
        var mats = { bone: BONE, brass: BRASS, bronze: BRONZE }, G = new THREE.Group(), U = o.unit || 0.03;
        var A = atoms(fold(o.seedA, 520, [-1.25, 0, 0]), mats[o.matA] || BONE, o.seedA);
        var B = atoms(fold(o.seedB, 440, [1.25, 0.1, 0.2]), mats[o.matB] || BRASS, o.seedB);
        var gA = new THREE.Group(), gB = new THREE.Group(); gA.add(A); gB.add(B);
        gA.scale.setScalar(U); gB.scale.setScalar(U);
        var base = o.stand ? 0.012 : 0;
        gA.position.set(o.state === "apart" ? -o.gap / 2 : 0, 0, 0); gB.position.set(o.state === "apart" ? o.gap / 2 : 0, 0, 0);
        /* SEATED ON THE STAND: each chain's lowest atom is measured and set down on the stand's top face, so the
         * model rests rather than hovers, and sinks a millimetre so the contact reads */
        [gA, gB].forEach(function (g) { g.updateMatrixWorld(true); var bb = new THREE.Box3().setFromObject(g); g.position.y = base - bb.min.y - 0.001; });
        G.add(gA); G.add(gB);
        if (o.stand) G.add(K.box(0.24, 0.012, 0.13, ANOD, 0, 0, 0, 0.002));
        /* the weight of the model where it rests: a soft dark core under the chains on whatever they stand on */
        var sc = document.createElement("canvas"); sc.width = sc.height = 128; var sg = sc.getContext("2d"), rg = sg.createRadialGradient(64, 64, 4, 64, 64, 62);
        rg.addColorStop(0, "rgba(0,0,0,0.92)"); rg.addColorStop(0.5, "rgba(0,0,0,0.55)"); rg.addColorStop(1, "rgba(0,0,0,0)"); sg.fillStyle = rg; sg.fillRect(0, 0, 128, 128);
        var dec = new THREE.Mesh(new THREE.PlaneGeometry(0.2, 0.12), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(sc), transparent: true, depthWrite: false }));
        dec.rotation.x = -Math.PI / 2; dec.position.y = base + 0.0006; dec.renderOrder = 2; G.add(dec);
        G.userData.chains = [gA, gB]; G.userData.keepOrigin = true; return G;
      }
    });

    /* LAB BENCH: a 25 mm black epoxy top on steel casework with drawer fronts, the front edge on +z. */
    K.define("lab_bench", {
      size: [2.4, 0.92, 0.76], anchor: "base",
      options: { w: 2.4, d: 0.76, h: 0.92 },
      note: "A laboratory bench, black epoxy top with a radiused edge on painted steel casework; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), w = o.w, d = o.d, h = o.h;
        var top = TXT.roundedBox(w, 0.025, d, 0.004, EPOXY); top.position.set(0, h - 0.0125, 0); G.add(top);
        G.add(K.box(w - 0.04, h - 0.11, d - 0.08, CASE, 0, 0.1, -0.02, 0.003));
        G.add(K.box(w - 0.06, 0.1, d - 0.14, K.mat("pl-plinth", { color: 0x111214, roughness: 0.8 }), 0, 0, -0.05));
        var n = Math.max(2, Math.round(w / 0.6));
        for (var i = 0; i < n; i++) { var x = -w / 2 + 0.04 + (i + 0.5) * (w - 0.08) / n;
          G.add(K.box((w - 0.08) / n - 0.012, 0.22, 0.012, CASE, x, h - 0.28, d / 2 - 0.05, 0.002));
          G.add(K.box(0.12, 0.012, 0.018, SATIN, x, h - 0.17, d / 2 - 0.04)); }
        top.receiveShadow = true; G.userData.topY = h; return G;
      }
    });

    /* HALF MATRIX PLATE: a right triangle of black anodised aluminium, legs of `cells` cells at `cell` metres, the
     * hypotenuse a stair of one cell per step, 9 mm base and a 3 mm satin terrace, a square pocket near the right angle
     * sized for the pair_block, graduations every `tick` cells along both legs. The right angle sits at the origin's
     * corner, legs along +x and -z. */
    K.define("half_matrix_plate", {
      size: [0.62, 0.012, 0.62],
      options: { cells: 1122, cell: 0.0005, tick: 100, pocket: true, pocketAt: [0.035, 0.035], pocketSide: 0.0272 },
      note: "The half matrix as a machined plate: a right triangle one cell per pair, a stepped hypotenuse, a corner pocket; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), n = o.cells, c = o.cell, L = n * c, M = 0.03;
        function tri(inset, steps) {
          var s = new THREE.Shape(); s.moveTo(-M, M); s.lineTo(L + M, M);
          /* the stair from the far end of the +x leg back to the far end of the -z leg */
          var k = Math.max(1, Math.round(n / steps));
          for (var i = n; i > 0; i -= k) { var x = i * c, y = -(n - i) * c; s.lineTo(x + inset, y - inset); s.lineTo(x - k * c + inset, y - inset); }
          s.lineTo(-M, -L - M); s.lineTo(-M, M); return s;
        }
        var base = new THREE.Mesh(new THREE.ExtrudeGeometry(tri(M, 280), { depth: 0.009, bevelEnabled: false }), ANOD);
        base.rotation.x = -Math.PI / 2; G.add(base);
        var ts = tri(0, 560);
        if (o.pocket) { var h = new THREE.Path(), px = o.pocketAt[0], pz = o.pocketAt[1], ps = o.pocketSide;
          h.moveTo(px, -pz); h.lineTo(px, -pz - ps); h.lineTo(px + ps, -pz - ps); h.lineTo(px + ps, -pz); h.lineTo(px, -pz); ts.holes.push(h); }
        var terr = new THREE.Mesh(new THREE.ExtrudeGeometry(ts, { depth: 0.003, bevelEnabled: true, bevelThickness: 0.0004, bevelSize: 0.0004, bevelSegments: 1 }), SATIN);
        terr.rotation.x = -Math.PI / 2; terr.position.y = 0.009; G.add(terr);
        var TICK = K.mat("pl-tick", { color: 0xb8bcc2, roughness: 0.3, metalness: 0.9 });
        for (var t = o.tick; t < n; t += o.tick) { var long = t % (o.tick * 5) === 0, len = long ? 0.018 : 0.01;
          G.add(K.box(0.0009, 0.0004, len, TICK, t * c, 0.0121, -M + len / 2 + 0.002));
          G.add(K.box(len, 0.0004, 0.0009, TICK, -M + len / 2 + 0.002, 0.0121, t * c)); }
        base.castShadow = terr.castShadow = true; base.receiveShadow = terr.receiveShadow = true;
        G.userData.L = L; G.userData.top = 0.0124; G.userData.keepOrigin = true; return G;
      }
    });

    /* PAIR BLOCK: the brass block of every likely pair, `cols` columns and `rows` full rows of `cell` metre cells and
     * a last row of `last`, `t` thick, the cells milled into its top as a texture. Origin under its centre. */
    K.define("pair_block", {
      size: [0.027, 0.006, 0.027],
      options: { cols: 54, rows: 53, last: 33, cell: 0.0005, t: 0.006, major: 0 },
      note: "A brass block milled with one cell per likely pair, laid out as near square as whole cells allow; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), c = o.cell, W = o.cols * c, D = (o.rows + 1) * c;
        /* the cells are finer than any camera here resolves, so the top carries a fine brushed finish rather than a
         * grid that would alias into a false coarse count */
        var cv = document.createElement("canvas"); cv.width = cv.height = 512; var g = cv.getContext("2d"), rr = K.rng(5);
        g.fillStyle = "#b0b0b0"; g.fillRect(0, 0, 512, 512);
        for (var i = 0; i < 2600; i++) { var yy = rr() * 512, a = 0.06 + rr() * 0.12; g.fillStyle = rr() < 0.5 ? "rgba(255,255,255," + a + ")" : "rgba(0,0,0," + a + ")"; g.fillRect(0, yy, 512, 0.6 + rr()); }
        var tex = new THREE.CanvasTexture(cv); tex.anisotropy = 8; tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(1, 10);
        var mat = K.mat("pl-brass-lap", { color: 0xc9a35a, metalness: 0.7, roughness: 0.34 });   /* a lapped top; a brushed texture aliased into streaks at every camera tried */
        /* ONE SOLID: the block's outline, full rows and the short last row together, extruded once with one bevel, so
         * the stepped corner where the last row ends is a cut in a single machined part and not two boxes butted */
        var D0 = -c / 2 - o.rows * c / 2, D1 = D0 + o.rows * c, sh = new THREE.Shape();
        sh.moveTo(-W / 2, D0); sh.lineTo(W / 2, D0); sh.lineTo(W / 2, D1); sh.lineTo(-W / 2 + o.last * c, D1);
        sh.lineTo(-W / 2 + o.last * c, D1 + c); sh.lineTo(-W / 2, D1 + c); sh.lineTo(-W / 2, D0);
        var bv = Math.min(0.0006, o.t / 8), geo = new THREE.ExtrudeGeometry(sh, { depth: o.t - 2 * bv, bevelEnabled: true, bevelThickness: bv, bevelSize: bv, bevelSegments: 2 });
        geo.rotateX(Math.PI / 2); geo.translate(0, o.t - bv, 0);
        var solid = new THREE.Mesh(geo, mat); G.add(solid);
        /* THE CELLS AS CUTS: one groove between every column and every row, real geometry so no texture aliases them
         * into a false coarse count. A groove is 0.07 mm wide in blackened bronze, sunk into the top face. With `major`,
         * every major-th groove is cut four times as wide, an index of whole blocks of cells that reads at feed size
         * where the single cells can't, the same ruling every hundred cells the plate carries on frame 3. */
        var gw = 0.00007, gt = o.t + 0.00002, ins = 0.0006, z0 = -c / 2 - o.rows * c / 2, z1 = z0 + o.rows * c;
        var cuts = [];
        for (var i = 1; i < o.cols; i++) { var x = -W / 2 + i * c, za = z0 + ins, zb = (i < o.last ? z1 + c : z1) - ins, len = zb - za;
          var w1 = o.major && i % o.major === 0 ? gw * 4 : gw, m1 = new THREE.Mesh(new THREE.BoxGeometry(w1, 0.00006, len), BRONZE); m1.position.set(x, gt - 0.00003, za + len / 2); cuts.push(m1); }
        for (var j = 1; j <= o.rows; j++) { var zz = z0 + j * c, xa = -W / 2 + ins, xb = W / 2 - ins;
          var w2 = o.major && j % o.major === 0 ? gw * 4 : gw, m2 = new THREE.Mesh(new THREE.BoxGeometry(xb - xa, 0.00006, w2), BRONZE); m2.position.set((xa + xb) / 2, gt - 0.00003, zz); cuts.push(m2); }
        G.add(K.merge(cuts, BRONZE));
        G.traverse(function (m) { if (m.isMesh) { m.castShadow = m.receiveShadow = true; } });
        G.userData.size = [W, o.t, D]; return G;
      }
    });

    /* MICROTUBE: a 1.5 mL polypropylene tube, 10.8 mm across and 39 mm tall, conical foot, snap cap and hinge loop. */
    K.define("microtube", {
      size: [0.0108, 0.044, 0.0108],
      options: { cap: true },
      note: "A 1.5 mL snap cap microtube in milky polypropylene; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group();
        var prof = [[0.0005, 0], [0.0018, 0.002], [0.0046, 0.017], [0.0052, 0.019], [0.0052, 0.0385], [0.0058, 0.039], [0.0058, 0.0402], [0.0049, 0.0402], [0.0047, 0.02]];
        G.add(new THREE.Mesh(new THREE.LatheGeometry(prof.map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 28), PP));
        if (o.cap) { G.add(K.cyl(0.0056, 0.0056, 0.0034, PP, 0, 0.0402, 0, 24));
          var loop = new THREE.Mesh(new THREE.TorusGeometry(0.0026, 0.0007, 8, 16, Math.PI), PP); loop.position.set(0, 0.0418, 0.0058); loop.rotation.y = Math.PI / 2; G.add(loop); }
        G.traverse(function (m) { if (m.isMesh) m.castShadow = true; });
        return G;
      }
    });
    /* TUBE RACK: a slate rack, `cols` by `rows` wells at 12.5 mm pitch, holding `count` tubes from the front row back. */
    K.define("tube_rack", {
      size: [0.24, 0.05, 0.075], anchor: "base",
      options: { cols: 17, rows: 5, count: 85, pitch: 0.0125 },
      note: "A slate polypropylene microtube rack holding tubes in aligned rows; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), p = o.pitch, W = o.cols * p + 0.012, D = o.rows * p + 0.012;
        G.add(K.box(W, 0.004, D, SLATE, 0, 0, 0, 0.001));
        var deck = K.box(W, 0.003, D, SLATE, 0, 0.026, 0, 0.001); G.add(deck);
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (s) { G.add(K.box(0.004, 0.026, 0.004, SLATE, s[0] * (W / 2 - 0.003), 0.003, s[1] * (D / 2 - 0.003))); });
        var k = 0;
        for (var r = o.rows - 1; r >= 0 && k < o.count; r--) for (var c = 0; c < o.cols && k < o.count; c++, k++) {
          var t = K.make("microtube", {}); t.position.set(-W / 2 + 0.006 + (c + 0.5) * p, 0.006, -D / 2 + 0.006 + (r + 0.5) * p); G.add(t); }
        G.userData.count = k; return G;
      }
    });

    /* PETRI PLATE: a 90 mm polystyrene dish, inverted as a lab stores it, 4 mm of amber agar with seeded cream colony
     * domes, a tape strip on the lid's rim. `stack` dishes one on another. Origin under the stack. */
    K.define("petri_plate", {
      size: [0.09, 0.015, 0.09],
      options: { stack: 1, colonies: 60, seed: 3, tape: true },
      note: "A 90 mm yeast plate, polystyrene base and lid, amber agar, cream colonies, stored inverted; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), rnd = K.rng(o.seed), H = 0.0148;
        for (var s = 0; s < o.stack; s++) {
          var P = new THREE.Group(); P.position.y = s * (H + 0.0004);
          /* inverted: the base (with its agar) on top, the lid below */
          var lid = new THREE.Mesh(new THREE.LatheGeometry([[0, 0], [0.0458, 0], [0.0462, 0.0008], [0.0462, 0.0095], [0.0452, 0.0095], [0.0452, 0.0012], [0, 0.0012]].map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 48), PS);
          P.add(lid);
          var base = new THREE.Mesh(new THREE.LatheGeometry([[0, H], [0.0438, H], [0.0442, H - 0.0006], [0.0442, 0.0018], [0.0434, 0.0018], [0.0434, H - 0.001], [0, H - 0.001]].map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 48), PS);
          P.add(base);
          var agar = K.cyl(0.0432, 0.0432, 0.004, AGAR, 0, H - 0.005, 0, 48); P.add(agar);
          var dome = new THREE.SphereGeometry(1, 12, 8, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), list = [];
          for (var i = 0; i < o.colonies; i++) { var r = Math.sqrt(rnd()) * 0.038, a = rnd() * 6.283, sz = 0.0006 + rnd() * 0.0018;
            var m = new THREE.Mesh(dome, COLONY); m.scale.set(sz, sz * 0.6, sz); m.position.set(Math.cos(a) * r, H - 0.005, Math.sin(a) * r); P.add(m); }
          if (o.tape) { var tp = new THREE.Mesh(new THREE.CylinderGeometry(0.0464, 0.0464, 0.006, 48, 1, true, 0.4, 1.6), TAPE); tp.position.y = 0.006; P.add(tp); }
          G.add(P);
        }
        G.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return G;
      }
    });

    /* CULTURE FLASK: a T75 flask lying flat, a canted neck and a vented cap, a shallow layer of medium. */
    K.define("culture_flask", {
      size: [0.18, 0.037, 0.08],
      options: { fill: 0.004 },
      note: "A T75 tissue culture flask lying flat with a shallow layer of medium and a vented cap; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group();
        var body = TXT.roundedBox(0.147, 0.037, 0.08, 0.004, PS); body.position.set(0, 0.0185, 0); G.add(body);
        var med = TXT.roundedBox(0.141, o.fill, 0.074, 0.002, MEDIUM); med.position.set(0, 0.0015 + o.fill / 2, 0); G.add(med);
        var neck = K.cyl(0.012, 0.014, 0.025, PS, 0, 0, 0, 24); neck.rotation.z = -Math.PI / 2 + 0.35; neck.position.set(0.0735, 0.022, 0); G.add(neck);
        var cap = K.cyl(0.016, 0.016, 0.02, CAPW, 0, 0, 0, 24); cap.rotation.z = -Math.PI / 2 + 0.35; cap.position.set(0.098, 0.031, 0); G.add(cap);
        G.traverse(function (m) { if (m.isMesh) m.castShadow = true; });
        return G;
      }
    });
  };

  /* ---- frame helpers, carried from the 2026-11-06 chassis ---------------------------------- */

  /* THE LAB: one dark room, a black epoxy bench run under one window on the left wall at last light. A frame calls
   * this once and stands its subject on the bench top at y = N.BENCH_H. */
  N.BENCH_H = 0.92;
  /* the room's one specification, so every frame's TXT.interior call builds the same lab; the frame calls
   * TXT.interior itself, because a room is the frame's own decision to stand somewhere */
  N.roomOpts = function (o) {
    o = o || {};
    return { w: o.w || 6, d: o.d || 7, h: 3.0, floor: "concrete", wall: o.wall || 0x1d2025, window: "left",
      windowW: o.windowW || 1.6, windowH: o.windowH || 1.1, windowColor: o.windowColor || 0xffb27a, windowI: o.windowI == null ? 0.4 : o.windowI,
      ceiling: true, light: o.light == null ? 0.12 : o.light };
  };

  /* THE WINDOW AT LAST LIGHT: the room's pane is a flat colour, so a frame dresses it once with the evening outside,
   * near black overhead going to a warm seam at the sill, a line of far trees in silhouette and steel mullions, so the
   * one source in the room reads as a window and not a lit panel. */
  N.dressWindow = function (THREE, TXT, room, o) {
    o = o || {};
    var cv = document.createElement("canvas"); cv.width = 640; cv.height = 440; var g = cv.getContext("2d"), rr = K_RNG(91);
    var sk = g.createLinearGradient(0, 0, 0, 440); sk.addColorStop(0, "#05060c"); sk.addColorStop(0.45, "#141826"); sk.addColorStop(0.78, "#5a3a26"); sk.addColorStop(0.9, "#c8834e"); sk.addColorStop(1, "#e3a066");
    g.fillStyle = sk; g.fillRect(0, 0, 640, 440);
    g.fillStyle = "#07070a"; g.beginPath(); g.moveTo(0, 440);
    for (var x = 0; x <= 640; x += 8) g.lineTo(x, 392 - 26 * Math.abs(Math.sin(x * 0.019 + 1.3)) - 18 * rr());
    g.lineTo(640, 440); g.closePath(); g.fill();
    var tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
    var MUL = new THREE.MeshStandardMaterial({ color: 0x141518, roughness: 0.6, metalness: 0.4 });
    room.traverse(function (m) {
      if (m.isMesh && m.geometry && m.geometry.type === "PlaneGeometry" && m.material && m.material.isMeshBasicMaterial) {
        m.material.map = tex; m.material.color.setRGB(o.i || 0.9, o.i || 0.9, o.i || 0.9); m.material.needsUpdate = true;
        m.geometry.computeBoundingBox(); var bb = m.geometry.boundingBox, w = bb.max.x - bb.min.x, h = bb.max.y - bb.min.y;
        var bars = [[w, 0.05, 0, h / 2], [w, 0.05, 0, -h / 2], [0.05, h, -w / 2, 0], [0.05, h, w / 2, 0], [0.035, h, 0, 0], [w, 0.03, 0, h * 0.12]];
        bars.forEach(function (b) { var bx = TXT.roundedBox(b[0], b[1], 0.04, 0.008, MUL); bx.position.set(b[2], b[3], 0.02); m.add(bx); });
      }
    });
    return tex;
  };

  /* THE ROOM GOES WARM AND DARK: the studio environment and the preset's cool rim lit the bone chain navy and the bench
   * lavender, against a warm window. A frame calls this after the rig and before the snapshot. */
  N.darkRoom = function (R, o) {
    o = o || {};
    R.scene.environmentIntensity = o.env == null ? 0.06 : o.env;
    R.scene.traverse(function (l) {
      if (!l.isLight) return;
      if (l.isHemisphereLight || l.isAmbientLight) l.intensity *= 0.25;
      else if (l.isDirectionalLight && !l.castShadow) { l.color.setHex(0xffc89a); l.intensity *= 0.35; }
    });
    return R;
  };
  /* THE WINDOW SLOT: a tall warm pane on the window wall, placed where the camera's ray through screen point (sx, sy)
   * meets that wall, so the last light stands directly behind the subject; a warm light at it rims what is in front. */
  N.slot = function (THREE, R, sx, sy, o) {
    o = o || {};
    R.camera.updateMatrixWorld(true);
    var d = new THREE.Vector3(sx / N.W * 2 - 1, 1 - sy / N.H * 2, 0.5).unproject(R.camera).sub(R.camera.position).normalize();
    var wx = o.wallX == null ? -2.98 : o.wallX, k = (wx - R.camera.position.x) / d.x, p = R.camera.position.clone().add(d.multiplyScalar(k));
    var cv = document.createElement("canvas"); cv.width = 64; cv.height = 256; var g = cv.getContext("2d");
    var gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, "#1a1410"); gr.addColorStop(0.55, "#8a4e2a"); gr.addColorStop(0.85, "#f0a464"); gr.addColorStop(1, "#ffd29a");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 256);
    var tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
    var pane = new THREE.Mesh(new THREE.PlaneGeometry(o.w || 0.16, o.h || 0.7), new THREE.MeshBasicMaterial({ map: tex, toneMapped: true, fog: false }));
    pane.userData.txWear = false;
    pane.material.color.multiplyScalar(o.i || 1.6);
    pane.position.set(wx + 0.01, p.y + (o.lift || 0.12), p.z); pane.rotation.y = Math.PI / 2; R.scene.add(pane);
    var MUL = new THREE.MeshStandardMaterial({ color: 0x0c0d0f, roughness: 0.6, metalness: 0.4 });
    [[0.02, (o.h || 0.7) + 0.04, 0, -((o.w || 0.16) / 2)], [0.02, (o.h || 0.7) + 0.04, 0, (o.w || 0.16) / 2], [0.02, 0.02, (o.h || 0.7) / 2, 0], [0.02, 0.02, -(o.h || 0.7) / 2, 0]].forEach(function (b, i) {
      var m = new THREE.Mesh(new THREE.BoxGeometry(0.03, i < 2 ? b[1] : 0.03, i < 2 ? 0.025 : (o.w || 0.16) + 0.04), MUL);
      m.position.set(wx + 0.02, pane.position.y + b[2], p.z + b[3]); R.scene.add(m); });
    var pl = new THREE.PointLight(o.color || 0xffb27a, o.light == null ? 1.4 : o.light, 3, 2); pl.position.set(wx + 0.25, pane.position.y - 0.1, p.z); R.scene.add(pl);
    return pane;
  };
  N.bench = function (TXT, R, K, o) {
    o = o || {};
    var bench = K.make("lab_bench", { w: o.w || 2.4, d: 0.76, h: N.BENCH_H });
    bench.position.set(o.x || 0, 0, o.z || 0); if (o.rotY) bench.rotation.y = o.rotY; TXT.add(R, bench); TXT.contact(R, bench);
    return bench;
  };
  N.flood = function (THREE, R, from, at, o) {
    o = o || {};
    var sp = new THREE.SpotLight(o.color || 0xf2f4ff, o.i == null ? 900 : o.i, o.reach || 40, o.angle || 0.5, o.penumbra == null ? 0.55 : o.penumbra, 2);
    sp.position.set(from[0], from[1], from[2]); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0006; sp.shadow.normalBias = 0.03;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
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


  /* ---- frame helpers, carried from the 2026-11-04 chassis ---------------------------------- */
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
      ".lab.brass { color:#D6C49E; }",
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
