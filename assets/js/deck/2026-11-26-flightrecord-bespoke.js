/* deck/2026-11-26-flightrecord-bespoke.js, the SPINE for the November 26th, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * Texas Tech's IMMS and Fort Worth's AVX Defense Technologies built an AI enabled maintenance decision tool (FSUI) and an engine
 * life tracker (PSV) under the Army's FleetSpace program, and Texas Tech says both have been provided to the Army. Every result
 * the release reports is from testing (tx-2026-0263).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the deck's TONE (explainer), bespoke:true, the tone's grade and the accent.
 * Each frame picks its own world (TXT.sky(R, world) or TXT.studio / TXT.interior), turns its own key
 * (TXT.deckRig(..., { light })) and places its own type, seated with CH.seat. It mounts the type faces and the furniture
 * (CH.start), and hands a frame the helpers below. There is no drawFrame.
 *
 * THE ACCENT. Dusk gold #e0956a means ONE thing: WHAT THE SOFTWARE PUTS OUT (a flag on a part, a restored record cell, the
 * predicted phase mark). Never on a person, never on type, never decoration, never red.
 * THE MATERIAL CODE. Bead blasted titanium and heat tinted nickel alloy are the machine. Bare 6061 aluminium is the record.
 *
 * THE MODELS the kit lacks, in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the
 * lift: turboshaft_engine (an illustrative generic turboshaft drawn to no maker's design), engine_stand, blisk (a turbine disc
 * with twisted blades, one optionally flagged) and record_tray (a machined 10 by 10 socket tray with filled cells).
 * Everything drawn is drawn to illustrate: no aircraft type, no insignia, no tail number, no maker's mark, no legible screen.
 * Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("flightrecord.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "flightrecord", look: "v2", tone: "explainer", bespoke: true,
    light: { az: -40, el: 34 },
    sky: { preset: "v2explainer" },
    ground: "#ffc68a",
    material: "#c9d2dc",
    accent: "#e0956a",
    grade: TXLOOK.grade("explainer")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261126; N.TONE = "explainer"; N.P = TXLOOK.palette("explainer"); N.INK = N.P.ink;
  N.ACCENT = 0xe0956a;        /* dusk gold: what the software puts out, and nothing else */
  N.TITANIUM = 0x9aa6b4; N.INCONEL = 0x8a7f74; N.ALU = 0xd3d9df; N.ANODE = 0x2a3f8f; N.STAND = 0x3a4470; N.GRANITE = 0x26283a;
  N.STEEL = 0xc9ced4; N.RUBBER = 0x1c1c22;
  N.GOLD = N.ACCENT;
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };
  /* the accent, albedo first with a little emissive so it reads at feed size and never as pink */
  N.goldMat = function (K) { return K.mat("fr-gold", { color: N.ACCENT, metalness: 0.2, roughness: 0.34, emissive: N.ACCENT, emissiveIntensity: 0.12, clearcoat: 0.7, clearcoatRoughness: 0.15 }, true); };
  N.titaniumMat = function (K) { return K.mat("fr-ti", { color: N.TITANIUM, metalness: 0.88, roughness: 0.42 }, true); };
  N.aluMat = function (K) { return K.mat("fr-alu", { color: N.ALU, metalness: 0.9, roughness: 0.34 }, true); };
  /* heat tint along an axis: straw, bronze, peacock blue, a canvas gradient the lathe's v coordinate reads */
  N.heatTex = function (THREE) {
    if (N._heat) return N._heat;
    N._heat = N.canvasTex(THREE, 8, 256, function (g, w, h) {
      var gr = g.createLinearGradient(0, 0, 0, h);
      gr.addColorStop(0, "#b9a06a"); gr.addColorStop(0.35, "#a8743e"); gr.addColorStop(0.62, "#6b4a7a"); gr.addColorStop(0.85, "#3c6fa8"); gr.addColorStop(1, "#8d97a3");
      g.fillStyle = gr; g.fillRect(0, 0, w, h);
    });
    return N._heat;
  };
  N.heatMat = function (K, THREE) { return K.mat("fr-heat", { color: 0xffffff, map: N.heatTex(THREE), metalness: 0.85, roughness: 0.38 }, true); };

  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.turboshaft_engine) return;
    N.T = THREE;
    var shadowAll = function (g) { g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return g; };
    var steelPaint = function (c) { return K.mat("fr-steelp-" + c.toString(16), { color: c, metalness: 0.35, roughness: 0.5, clearcoat: 0.3 }, true); };
    var dark = function () { return K.mat("fr-dark", { color: 0x1d2236, metalness: 0.6, roughness: 0.5 }); };
    var lathe = function (prof, mat, seg) { var m = TXT.lathe(prof, mat, { segments: seg || 96 }); return m; };
    /* a ring of instanced bolts about the y axis at radius r, height y */
    var boltRing = function (parent, r, y, n, mat) {
      var geo = new THREE.CylinderGeometry(0.006, 0.006, 0.01, 6), list = [];
      geo.rotateZ(Math.PI / 2);
      for (var i = 0; i < n; i++) { var a = i / n * Math.PI * 2; list.push([Math.cos(a) * r, y, Math.sin(a) * r, -a]); }
      return K.instances(geo, mat, list, parent);
    };

    /* TURBOSHAFT ENGINE, illustrative, drawn to no maker's design. 1.20 m long on x, 0.56 m across at the combustor.
     * Built on a lathe about y, then laid on its side so the intake faces -x and the exhaust collector turns up at +x.
     * Options: panel (an access panel swung open on the compressor case), cutaway (a quarter of the turbine case removed,
     * showing a blisk), tag (a hang wire on the turbine flange; userData.tagAt is its world anchor before the frame moves
     * the engine), axisY (the shaft's height above the ground). userData.parts.turbine is the turbine case. */
    K.define("turboshaft_engine", {
      size: [1.3, 0.62, 0.6],
      options: { panel: false, cutaway: false, tag: false, axisY: 0.3 },
      note: "Illustrative generic turboshaft, drawn to no maker's design: bellmouth intake, ribbed compressor case, combustor, heat tinted turbine, exhaust collector, flanges with bolt rings, accessory gearbox, harness and fuel lines.",
      make: function (o, rnd) {
        var g = new THREE.Group(), core = new THREE.Group(); g.add(core);
        var ti = N.titaniumMat(K), heat = N.heatMat(K, THREE), alu = N.aluMat(K), bolt = K.mat("fr-bolt", { color: 0xd8dde2, metalness: 1, roughness: 0.25 });
        /* the profile in (radius, axial y), intake at y 0 */
        var prof = [[0.172, 0.13], [0.18, 0.06], [0.196, 0.016], [0.212, 0.004], [0.224, 0.016], [0.218, 0.045], [0.192, 0.075], [0.186, 0.1]];
        for (var s = 0; s < 6; s++) { var y = 0.12 + s * 0.055; prof.push([0.186 + s * 0.004, y], [0.198 + s * 0.004, y + 0.006], [0.198 + s * 0.004, y + 0.016], [0.186 + s * 0.004, y + 0.022]); }
        prof.push([0.214, 0.47], [0.236, 0.5], [0.244, 0.54], [0.246, 0.66], [0.238, 0.71], [0.236, 0.74]);
        var comp = lathe(prof, K.mat("fr-ti-ds", { color: N.TITANIUM, metalness: 0.88, roughness: 0.42, side: THREE.DoubleSide }, true)); core.add(comp);
        /* the intake: a dark throat, inlet guide vanes and a spinner, so the front reads as an engine and not a drum */
        var throat = K.mat("fr-throat", { color: 0x232846, metalness: 0.7, roughness: 0.45, side: THREE.DoubleSide });
        var thr = lathe([[0.171, 0.13], [0.171, 0.16], [0.0, 0.16]], throat); core.add(thr);
        var spin = lathe([[0.0, 0.0], [0.03, 0.02], [0.06, 0.06], [0.075, 0.1], [0.0, 0.1]], alu); core.add(spin);
        for (var v = 0; v < 22; v++) { var va = v / 22 * Math.PI * 2, vane = TXT.roundedBox(0.004, 0.05, 0.11, 0.0015, ti);
          vane.position.set(Math.cos(va) * 0.125, 0.085, Math.sin(va) * 0.125); vane.rotation.y = -va; vane.rotation.x = 0.35; core.add(vane); }
        /* the combustor: axial stiffening ribs, a fuel manifold ring and its nozzle bosses */
        for (var sr = 0; sr < 28; sr++) { var sa = sr / 28 * Math.PI * 2, rib = TXT.roundedBox(0.008, 0.16, 0.008, 0.002, ti);
          rib.position.set(Math.cos(sa) * 0.248, 0.6, Math.sin(sa) * 0.248); rib.rotation.y = -sa; core.add(rib); }
        var fuelMat = K.mat("fr-fuel", { color: 0xb8bec6, metalness: 0.9, roughness: 0.3 });
        var man = new THREE.Mesh(new THREE.TorusGeometry(0.262, 0.008, 12, 96), fuelMat); man.rotation.x = Math.PI / 2; man.position.y = 0.56; core.add(man);
        for (var nz = 0; nz < 12; nz++) { var na = nz / 12 * Math.PI * 2, boss = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.03, 12), alu);
          boss.position.set(Math.cos(na) * 0.258, 0.56, Math.sin(na) * 0.258); boss.rotation.z = Math.PI / 2; boss.rotation.y = -na; core.add(boss);
          var stub = K.bar([Math.cos(na) * 0.262, 0.56, Math.sin(na) * 0.262], [Math.cos(na) * 0.25, 0.585, Math.sin(na) * 0.25], 0.004, fuelMat, 8); core.add(stub); }
        /* turbine and exhaust in heat tint, open at the back over a dark centrebody */
        var tprof = [[0.236, 0.74], [0.228, 0.78], [0.222, 0.9], [0.218, 0.96], [0.214, 1.04], [0.21, 1.1], [0.2, 1.1], [0.204, 1.0]];
        var turb = lathe(tprof, K.mat("fr-heat-ds", { color: 0xffffff, map: N.heatTex(THREE), metalness: 0.85, roughness: 0.38, side: THREE.DoubleSide }, true)); core.add(turb);
        var cb = lathe([[0.0, 1.16], [0.03, 1.13], [0.08, 1.06], [0.11, 0.98], [0.12, 0.92]], K.mat("fr-cb", { color: 0x3b3550, metalness: 0.8, roughness: 0.4 })); core.add(cb);
        var soot = lathe([[0.199, 1.0], [0.199, 1.099]], K.mat("fr-soot", { color: 0x15151f, roughness: 0.9, side: THREE.BackSide })); core.add(soot);
        if (o.cutaway) {
          var bl = K.make("blisk", { blades: 31, diameter: 0.38, flag: -1 }); bl.position.y = 0.86; core.add(bl);
        }
        /* flanges with bolt rings at the joints */
        [[0.11, 0.2], [0.47, 0.222], [0.74, 0.246], [0.96, 0.226], [1.1, 0.214]].forEach(function (f) {
          var fl = lathe([[f[1] - 0.004, f[0] - 0.008], [f[1] + 0.012, f[0] - 0.008], [f[1] + 0.014, f[0]], [f[1] + 0.012, f[0] + 0.008], [f[1] - 0.004, f[0] + 0.008], [f[1] - 0.004, f[0] - 0.008]], alu); core.add(fl);
          boltRing(core, f[1] + 0.008, f[0], 36, bolt);
        });
        /* accessory gearbox under the front, harness and fuel lines hugging the case */
        var gb = TXT.roundedBox(0.2, 0.3, 0.16, 0.012, alu); gb.position.set(0, 0.26, -0.27); core.add(gb);
        for (var p = 0; p < 4; p++) { var pad = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.03, 24), ti); pad.rotation.x = Math.PI / 2; pad.position.set(-0.06 + p % 2 * 0.12, 0.17 + Math.floor(p / 2) * 0.16, -0.36); core.add(pad); }
        var hose = K.mat("fr-hose", { color: 0x2c3352, roughness: 0.55, metalness: 0.2 });
        var hug = function (pts, r, m) { core.add(TXT.tube(pts.map(function (q) { var a = q[0], rr = q[2]; return [Math.cos(a) * rr, q[1], Math.sin(a) * rr]; }), r, m, { segments: 80, radial: 10 })); };
        hug([[0.5, 0.13, 0.205], [0.52, 0.3, 0.214], [0.55, 0.46, 0.226], [0.6, 0.6, 0.262], [0.65, 0.76, 0.25], [0.7, 0.92, 0.236]], 0.008, hose);
        hug([[2.4, 0.15, 0.206], [2.38, 0.35, 0.216], [2.35, 0.5, 0.236], [2.3, 0.56, 0.285]], 0.01, fuelMat);
        hug([[1.2, 0.14, 0.203], [1.22, 0.3, 0.212], [1.25, 0.45, 0.222], [1.3, 0.6, 0.26], [1.35, 0.8, 0.245]], 0.006, K.mat("fr-wire", { color: 0x40486e, roughness: 0.5 }));
        for (var cl = 0; cl < 7; cl++) { var y = 0.18 + cl * 0.11; var clip = new THREE.Mesh(new THREE.TorusGeometry(0.012, 0.003, 6, 12), alu); clip.position.set(Math.cos(0.52) * 0.215, y, Math.sin(0.52) * 0.215); clip.rotation.y = -0.52; core.add(clip); }
        /* borescope port caps */
        [0.3, 0.62, 0.84].forEach(function (y, i) { var c = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.02, 16), alu); c.position.set(0.21 + i * 0.03, y, 0.04); c.rotation.z = Math.PI / 2; core.add(c); });
        if (o.panel) {
          var pnl = new THREE.Mesh(new THREE.CylinderGeometry(0.205, 0.205, 0.16, 48, 1, true, 0, 0.9), K.mat("fr-ti-ds", { color: N.TITANIUM, metalness: 0.88, roughness: 0.42, side: THREE.DoubleSide }));
          pnl.position.set(0.06, 0.26, 0.05); pnl.rotation.y = 1.2; core.add(pnl);
          var bladeRow = new THREE.Group(); for (var b = 0; b < 24; b++) { var bm = TXT.roundedBox(0.005, 0.03, 0.15, 0.002, ti); var a2 = b / 24 * Math.PI * 2; bm.position.set(Math.cos(a2) * 0.09, 0.0, Math.sin(a2) * 0.09); bm.rotation.y = -a2; bm.rotation.x = 0.4; bladeRow.add(bm); }
          bladeRow.position.y = 0.26; core.add(bladeRow);
        }
        /* lay it on its side: the lathe's y becomes +x, intake at -x */
        core.rotation.z = -Math.PI / 2; core.position.set(-0.6, o.axisY, 0);
        if (o.tag) {
          var tagAt = new THREE.Vector3(0.16, o.axisY - 0.26, 0.18);
          var wire = K.cable([0.16, o.axisY - 0.22, 0.2], [0.17, o.axisY - 0.34, 0.24], 0.01, 0.0015, bolt); g.add(wire);
          var tg = TXT.roundedBox(0.06, 0.1, 0.004, 0.006, N.goldMat(K)); tg.position.set(0.17, o.axisY - 0.39, 0.245); tg.rotation.y = 0.3; g.add(tg);
          g.userData.tagAt = tagAt;
        }
        g.userData.parts = { turbine: turb, core: core };
        g.userData.keepOrigin = true;
        return shadowAll(g);
      }
    });

    /* ENGINE STAND, 1.40 x 0.80 x 0.85 m painted square tube, two yoke saddles, four casters, a hook post at +x for a tag.
     * The saddles hold an engine whose axis is at height `axisY` (default 0.92); userData.axisY reports it. */
    K.define("engine_stand", {
      size: [1.4, 0.95, 0.85],
      options: { axisY: 0.92, color: 0x3a4470, hook: true },
      note: "Painted steel tube engine stand on casters with two yoke saddles and a hook post.",
      make: function (o, rnd) {
        var g = new THREE.Group(), pm = steelPaint(o.color), rub = K.mat("fr-rubber", { color: N.RUBBER, roughness: 0.75 }), z = 0.36, x = 0.62, t = 0.025, top = o.axisY - 0.24;
        var sq = function (a, b) { var A = new THREE.Vector3().fromArray(a), B = new THREE.Vector3().fromArray(b), L = A.distanceTo(B); var m = TXT.roundedBox(t * 2, L, t * 2, 0.004, pm); m.position.copy(A).add(B).multiplyScalar(0.5); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize()); g.add(m); };
        [-z, z].forEach(function (zz) { sq([-x, 0.12, zz], [x, 0.12, zz]); });
        [-x, x].forEach(function (xx) { sq([xx, 0.12, -z], [xx, 0.12, z]); });
        [-0.38, 0.38].forEach(function (xx) {
          sq([xx, 0.12, -z], [xx, top, -0.1]); sq([xx, 0.12, z], [xx, top, 0.1]);
          var sad = new THREE.Mesh(new THREE.TorusGeometry(0.25, 0.02, 10, 40, Math.PI * 0.8), pm); sad.rotation.y = Math.PI / 2; sad.rotation.x = 0; sad.position.set(xx, o.axisY, 0); sad.rotation.z = Math.PI + Math.PI * 0.1; g.add(sad);
          sq([xx, top, -0.1], [xx, top, 0.1]);
        });
        [[-x, -z], [-x, z], [x, -z], [x, z]].forEach(function (c) {
          var fork = TXT.roundedBox(0.05, 0.05, 0.05, 0.008, pm); fork.position.set(c[0], 0.085, c[1]); g.add(fork);
          var wh = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.035, 24), rub); wh.rotation.x = Math.PI / 2; wh.position.set(c[0], 0.045, c[1]); g.add(wh);
        });
        if (o.hook) { sq([x, 0.12, z], [x, 0.7, z]); var hk = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.005, 8, 20, Math.PI * 1.4), K.mat("fr-hook", { color: 0xd8dde2, metalness: 1, roughness: 0.3 })); hk.position.set(x, 0.72, z + 0.03); g.add(hk); g.userData.hookAt = new THREE.Vector3(x, 0.7, z + 0.05); }
        g.userData.axisY = o.axisY; g.userData.keepOrigin = true;
        return shadowAll(g);
      }
    });

    /* BLISK, a turbine disc, `diameter` m across, with `blades` twisted, leaned airfoil blades on a hub, lying in the x-z plane
     * (axis on y). flag: the index of the blade whose leading edge carries the accent line, -1 for none. userData.bladeAt(i)
     * returns blade i's tip centre. */
    K.define("blisk", {
      size: [0.4, 0.06, 0.4],
      options: { blades: 31, diameter: 0.38, flag: -1, heat: true },
      note: "Turbine disc with twisted, leaned airfoil blades on fir tree roots, heat tinted; one blade optionally flagged in the accent.",
      make: function (o, rnd) {
        var g = new THREE.Group(), R = o.diameter / 2, rh = R * 0.58, H = 0.045;
        var hubMat = K.mat("fr-hub", { color: 0xa79a86, metalness: 0.9, roughness: 0.32 }, true);
        var hub = lathe([[0.02, -0.03], [rh * 0.4, -0.03], [rh * 0.5, -0.012], [rh, -0.02], [rh, 0.02], [rh * 0.5, 0.012], [rh * 0.4, 0.03], [0.02, 0.03]], hubMat, 128); g.add(hub);
        var bore = new THREE.Mesh(new THREE.TorusGeometry(0.022, 0.006, 10, 32), K.mat("fr-bore", { color: 0x6e6a66, metalness: 1, roughness: 0.2 })); bore.rotation.x = Math.PI / 2; g.add(bore);
        /* one blade: a cambered airfoil extruded radially, twisted along its span */
        var foil = []; for (var i = 0; i <= 16; i++) { var t = i / 16; foil.push([(t - 0.5) * 0.034, Math.sin(t * Math.PI) * 0.007 + 0.0025]); }
        for (var j = 16; j >= 0; j--) { var t2 = j / 16; foil.push([(t2 - 0.5) * 0.034, Math.sin(t2 * Math.PI) * 0.003 - 0.0015]); }
        var span = R - rh;
        var bgeo = new THREE.ExtrudeGeometry(new THREE.Shape(foil.map(function (p) { return new THREE.Vector2(p[0], p[1]); })), { depth: span, steps: 10, bevelEnabled: false });
        var pos = bgeo.attributes.position;
        for (var k = 0; k < pos.count; k++) { var zz = pos.getZ(k), f = zz / span, tw = 0.95 + f * 0.5, cx = pos.getX(k), cy = pos.getY(k);
          pos.setXYZ(k, cx * Math.cos(tw) - cy * Math.sin(tw), cx * Math.sin(tw) + cy * Math.cos(tw), zz); }
        bgeo.computeVertexNormals();
        /* the blade lies with span on +z; stand it radially in the x-z plane */
        var bladeMat = o.heat ? N.heatMat(K, THREE) : N.titaniumMat(K), gold = N.goldMat(K), root = K.mat("fr-root", { color: 0x9a8f80, metalness: 0.9, roughness: 0.35 });
        var tips = [];
        for (var b = 0; b < o.blades; b++) {
          var a = b / o.blades * Math.PI * 2, piv = new THREE.Group(); piv.rotation.y = -a; g.add(piv);
          var bm = new THREE.Mesh(bgeo, bladeMat); bm.rotation.y = 0; bm.rotation.x = Math.PI / 2; bm.rotation.order = "YXZ";
          bm.position.set(0, 0, rh - 0.002); bm.rotation.set(0, 0, 0); bm.rotation.y = 0;
          var holder = new THREE.Group(); holder.position.set(0, 0, 0); holder.rotation.x = 0; holder.add(bm);
          bm.rotation.set(0.0, 0.0, 0.0); bm.position.set(0, 0, rh - 0.002);
          piv.add(holder);
          var rt = TXT.roundedBox(0.03, H * 0.7, 0.014, 0.002, root); rt.position.set(0, 0, rh - 0.004); piv.add(rt);
          if (b === o.flag) { var line = TXT.roundedBox(0.004, 0.006, span * 0.96, 0.0015, gold); line.position.set(-0.017, 0.004, rh + span * 0.5); piv.add(line); }
          tips.push(new THREE.Vector3(Math.sin(a) * R, 0, Math.cos(a) * R));
        }
        g.userData.bladeAt = function (i) { return tips[i]; };
        g.userData.keepOrigin = true;
        return shadowAll(g);
      }
    });

    /* RECORD TRAY, a machined 6061 tray `w` m square and 0.042 m tall with a `cols` by `rows` grid of square sockets 12 mm deep,
     * and `filled` rounded cubes in the accent standing 4 mm proud, filled row major from the near (+z) left corner. The
     * empty sockets show an indigo anodised floor. userData.cellAt(i) returns the centre of socket i's opening. */
    K.define("record_tray", {
      size: [0.42, 0.05, 0.42],
      options: { cols: 10, rows: 10, filled: 0, w: 0.42, fillMat: null },
      note: "Machined aluminium tray with a grid of square sockets, some filled with accent cubes, row major from the near left corner.",
      make: function (o, rnd) {
        var g = new THREE.Group(), alu = N.aluMat(K), w = o.w, hBase = 0.03, hWall = 0.012, pitch = (w - 0.03) / o.cols, sock = pitch * 0.8, wall = pitch - sock;
        var base = TXT.roundedBox(w, hBase, w, 0.006, alu); base.position.y = hBase / 2; g.add(base);
        var floor = K.mat("fr-anode", { color: N.ANODE, metalness: 0.6, roughness: 0.45 }, true);
        var fl = new THREE.Mesh(new THREE.BoxGeometry(w - 0.03, 0.002, w - 0.03), floor); fl.position.y = hBase + 0.0025; g.add(fl);
        var x0 = -w / 2 + 0.015, walls = [];
        for (var c = 0; c <= o.cols; c++) { var m = TXT.roundedBox(wall + (c === 0 || c === o.cols ? 0.015 : 0), hWall, w, 0.0015, alu); m.position.set(x0 + c * pitch + (c === 0 ? -0.0075 : c === o.cols ? 0.0075 : 0), hBase + hWall / 2, 0); g.add(m); }
        for (var r = 0; r <= o.rows; r++) { var m2 = TXT.roundedBox(w, hWall, wall + (r === 0 || r === o.rows ? 0.015 : 0), 0.0015, alu); m2.position.set(0, hBase + hWall / 2, x0 + r * pitch + (r === 0 ? -0.0075 : r === o.rows ? 0.0075 : 0)); g.add(m2); }
        var cells = [];
        for (var rr = 0; rr < o.rows; rr++) for (var cc = 0; cc < o.cols; cc++) {
          /* row major from the NEAR left corner: row 0 is the +z row */
          cells.push(new THREE.Vector3(x0 + (cc + 0.5) * pitch, hBase + hWall, -x0 - (rr + 0.5) * pitch));
        }
        var gm = o.fillMat || N.goldMat(K), cube = sock * 0.94, n = Math.max(0, Math.min(cells.length, o.filled | 0));
        for (var i = 0; i < n; i++) { var q = TXT.roundedBox(cube, hWall + 0.004, cube, 0.002, gm); q.position.set(cells[i].x, hBase + (hWall + 0.004) / 2, cells[i].z); g.add(q); }
        g.userData.cellAt = function (i) { return cells[i]; };
        g.userData.filled = n;
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
