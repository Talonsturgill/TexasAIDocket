/* deck/2026-11-06-rigfloor.js — the chassis for the 2026-11-06 deck: ExxonMobil's automated drilling rigs in the
 * Permian (tx-2026-0242). On its October 30th, 2026 call the company said three automated rigs are in operation and
 * that it expects about 25% of its Permian fleet next year and approximately half by 2028. Mechanical arms and robotic
 * systems now handle the heavy drill pipe that once put people on the rig floor.
 *
 * THE VISUAL ARGUMENT. The floor where people stood. A rig floor at night under its own floods, a robotic arm holding
 * a joint of pipe where a floor hand used to, and the pipe itself as the deck's measure. Every count a frame draws is
 * read from figures.json in that frame's own code. The chassis types no figure.
 *
 * THE WORLD. floodlit, a STAGED world: a black sky, a cold LED flood from high on one side, low rims. The key is
 * azimuth -60, elevation 26: one flood high on the left of a camera looking north, so every steel face toward the
 * reader takes a lit left edge and every cast runs right and away. TXBENCH reliefs read the same declaration and are
 * raked from the frame's upper left, across the grating bars and the joints, never along them.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `drill_pipe` (one joint, 5 in body, 6 5/8 in tool
 * joints, upsets, a hardband ring), `pipe_stand` (joints made up end to end), `pipe_robot` (a six axis arm on a
 * pedestal with a pipe gripper), `rig_mast` (a lattice mast with crown block, racking board and leg floods) and
 * `rig_floor` (the floor on its substructure, rotary and slips, rails, V door, catwalk and the driller's cabin). Drawn
 * to illustrate, to no maker's or operator's design, in the kit's conventions (metres, y up, origin on the ground,
 * front on +z) so Phase 17 can queue the lift.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("rigfloor.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "rigfloor",
    light: { az: -60, el: 26 },
    sky: "floodlit",
    ground: "#0A0B0E",
    material: "#5A5C60",
    accent: "#B4664F",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.08, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.22,
      bloom: { threshold: 0.93, strength: 0.08, radius: 6 },
      grain: { amount: 0.016, size: 2, seed: 20261106 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080; N.H = 1350; N.SEED = 20261106; N.INK = "#EEEAE3";
  N.EMBER = 0xB4664F;      /* brand.yaml's dusk_ember: pipe work handed to a machine, a painted band on a joint's box end, and nothing else */
  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.drill_pipe) return;
    var PIPE = K.mat("rf-pipe", { color: 0x3a3d41, metalness: 0.8, roughness: 0.38 });           /* mill scale, oiled */
    var JOINT = K.mat("rf-joint", { color: 0x8a8c8e, metalness: 0.9, roughness: 0.3 });           /* worn bright tool joint */
    var BAND = K.mat("rf-band", { color: 0x4a4744, metalness: 0.9, roughness: 0.5 });           /* hardbanding */
    var ARM = K.mat("rf-arm", { color: 0x8f918d, metalness: 0.12, roughness: 0.42 });             /* off white industrial paint */
    var ARMDK = K.mat("rf-armdk", { color: 0x2a2c30, metalness: 0.35, roughness: 0.5 });          /* motor housings, joints */
    var GRIP = K.mat("rf-grip", { color: 0x8a8d91, metalness: 0.82, roughness: 0.32 });
    var MAST = K.mat("rf-mast", { color: 0xa39c8c, metalness: 0.4, roughness: 0.58 });            /* faded cream mast paint */
    var DECK = K.mat("rf-deck", { color: 0x55585b, metalness: 0.65, roughness: 0.58 });
    var RAIL = K.mat("rf-rail", { color: 0xc4a43a, metalness: 0.25, roughness: 0.55 });           /* safety yellow, sun worn */
    var CAB = K.mat("rf-cab", { color: 0x8e9294, metalness: 0.4, roughness: 0.55 });
    var GLASS = K.finish.glass(0x1a2228);
    var LAMP = K.finish.lamp(0xeef2ff, 4.0);
    var CABLIT = K.finish.lamp(0xffd9a8, 2.2);

    function lathe(profile, mat, seg) {
      var pts = profile.map(function (p) { return new THREE.Vector2(p[0], p[1]); });
      var m = new THREE.Mesh(new THREE.LatheGeometry(pts, seg || 40), mat); return m;
    }

    /* DRILL PIPE: one joint, standing along +y from its pin at y = 0 to its box at the top. 5 in body (0.127 m OD),
     * 6 5/8 in tool joints (0.168 m), the upsets tapering into the body, a hardband ring on the box, thread shoulders.
     * `length` is the joint's length in metres; `lying: true` lays it along +z with its pin at z = 0. */
    K.define("drill_pipe", {
      size: [0.17, 9.4, 0.17],
      options: { length: 9.4, lying: false, band: null, bandH: 0.07, hardband: true, seed: 1 },
      note: "One joint of 5 in drill pipe: a threaded pin below its shoulder, 6 5/8 in tool joints, upsets into the body, a counterbored box at the top; band 'pin' or 'box' paints a raised ember ring bandH tall on that tool joint; drawn to illustrate.",
      make: function (o) {
        var L = o.length || 9.4, rb = 0.0635, rj = 0.084, TH = 0.11;
        /* the body and both tool joints as one lathe profile, from the pin shoulder at y = TH to the box face at L */
        var prof = [[0.064, TH], [rj, TH], [rj, TH + 0.25], [0.076, TH + 0.29], [rb + 0.004, TH + 0.42], [rb, TH + 0.48],
          [rb, L - 0.62], [rb + 0.004, L - 0.56], [0.074, L - 0.47], [rj, L - 0.44], [rj, L - 0.006], [rj - 0.004, L], [0.071, L], [0.069, L - 0.07], [0.055, L - 0.075]];
        var G = new THREE.Group(); G.add(lathe(prof, PIPE, 40));
        /* the pin: a tapered thread below the shoulder, its crests catching the light at a 10 mm pitch */
        var thr = [[0, 0], [0.046, 0]], n = Math.floor(TH / 0.01);
        for (var t = 0; t < n; t++) { var y0 = t * 0.01, r0 = 0.048 + (0.062 - 0.048) * (y0 / TH); thr.push([r0, y0 + 0.002], [r0 + 0.004, y0 + 0.005], [r0, y0 + 0.008]); }
        thr.push([0.062, TH], [0, TH]); G.add(lathe(thr, JOINT, 32));
        /* worn bright sleeves on both tool joints, a hardband ring on the box */
        G.add(K.cyl(rj + 0.0015, rj + 0.0015, 0.24, JOINT, 0, TH + 0.005, 0, 40));
        G.add(K.cyl(rj + 0.0015, rj + 0.0015, 0.40, JOINT, 0, L - 0.42, 0, 40));
        if (o.hardband) G.add(K.cyl(rj + 0.004, rj + 0.004, 0.05, BAND, 0, L - 0.30, 0, 40));
        /* the counterbore's dark mouth, so the box reads as a box from above */
        var mouth = new THREE.Mesh(new THREE.CircleGeometry(0.055, 28), K.mat("rf-bore", { color: 0x050506, roughness: 1 })); mouth.rotation.x = -Math.PI / 2; mouth.position.y = L - 0.07; G.add(mouth);
        /* the deck's one accent: a raised ember paint ring on the tool joint the machine handles */
        if (o.band) { var EMB = K.mat("rf-ember", { color: 0x9a4a34, metalness: 0.0, roughness: 0.92, envMapIntensity: 0.15 });
          var bh = o.bandH || 0.07, by = o.band === "box" ? L - 0.40 + (0.36 - bh) / 2 : TH + 0.06;
          G.add(K.cyl(rj + 0.006, rj + 0.006, bh, EMB, 0, by, 0, 40)); }
        if (o.lying) { var H = new THREE.Group(); G.rotation.x = Math.PI / 2; G.position.y = rj; H.add(G); H.userData.keepOrigin = true; return H; }
        G.userData.keepOrigin = true; return G;
      }
    });

    /* A STAND of `joints` joints made up end to end, pin down, standing on its lowest pin. */
    K.define("pipe_stand", {
      size: [0.17, 28.2, 0.17], anchor: "base",
      options: { joints: 3, length: 9.4, band: null, seed: 1 },
      note: "A stand of drill pipe, joints made up end to end; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), L = o.length || 9.4;
        for (var i = 0; i < (o.joints || 3); i++) { var j = K.make("drill_pipe", { length: L, seed: o.seed + i, band: o.band && i === 0 ? o.band : null }); j.position.y = i * (L - 0.02); G.add(j); }
        return G;
      }
    });

    /* AN INDUSTRIAL ARM on a pedestal, six axes, gripping a pipe. Drawn to illustrate, to no maker's design. Origin on
     * the floor under the pedestal; the arm reaches toward +z. Pose in degrees: yaw (about y), shoulder and elbow (in
     * the arm's plane, 0 = upper arm vertical, forearm horizontal forward), wrist pitch. `gripR` is the jaw radius. */
    K.define("pipe_robot", {
      size: [1.4, 3.6, 2.8],
      options: { yaw: 0, shoulder: 18, elbow: -12, wrist: 0, gripR: 0.085, pedestal: 0.9, seed: 1 },
      note: "A six axis industrial arm on a steel pedestal with a pipe gripper; drawn to illustrate, to no maker's design.",
      make: function (o) {
        var D = Math.PI / 180, G = new THREE.Group(), ph = o.pedestal == null ? 0.9 : o.pedestal;
        /* pedestal: a fabricated steel column on a bolted base plate, a top flange, stiffeners */
        G.add(K.box(0.9, 0.04, 0.9, DECK, 0, 0, 0, 0.01));
        for (var b = 0; b < 8; b++) { var a = b / 8 * Math.PI * 2; G.add(K.cyl(0.018, 0.018, 0.035, JOINT, Math.cos(a) * 0.38, 0.04, Math.sin(a) * 0.38, 8)); }
        G.add(K.box(0.52, ph - 0.1, 0.52, ARMDK, 0, 0.04, 0, 0.02));
        [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (s) { var st = K.box(s[0] ? 0.03 : 0.2, 0.28, s[1] ? 0.03 : 0.2, ARMDK, s[0] * 0.27, 0.04, s[1] * 0.27, 0.004); G.add(st); });
        G.add(K.cyl(0.36, 0.36, 0.06, ARMDK, 0, ph - 0.06, 0, 40));
        /* axis 1: the turret */
        var T = new THREE.Group(); T.position.y = ph; T.rotation.y = (o.yaw || 0) * D; G.add(T);
        T.add(K.cyl(0.33, 0.35, 0.34, ARM, 0, 0, 0, 40));
        T.add(K.cyl(0.2, 0.2, 0.08, ARMDK, 0, 0.34, 0, 32));
        var shoulderH = 0.62;
        var sh = new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.23, 0.5, 64), ARM); sh.rotation.z = Math.PI / 2; sh.position.set(0, shoulderH, 0); T.add(sh);
        var shCap = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.56, 64), ARMDK); shCap.rotation.z = Math.PI / 2; shCap.position.set(0, shoulderH, 0); T.add(shCap);
        T.add(K.box(0.42, 0.34, 0.46, ARM, 0, 0.3, -0.02, 0.06));
        /* motor on the turret's back */
        var mot = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.34, 48), ARMDK); mot.rotation.x = Math.PI / 2; mot.position.set(0.18, 0.5, -0.3); T.add(mot);
        /* axis 2: the upper arm */
        var U = new THREE.Group(); U.position.set(0, shoulderH, 0); U.rotation.x = -(o.shoulder || 0) * D; T.add(U);
        var upL = 1.25;
        U.add(K.box(0.3, upL, 0.24, ARM, 0, 0, 0, 0.07));
        U.add(K.box(0.32, 0.5, 0.05, ARMDK, 0, 0.32, -0.14, 0.01));   /* the cable cover */
        var el = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.4, 64), ARM); el.rotation.z = Math.PI / 2; el.position.set(0, upL, 0); U.add(el);
        var elc = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.44, 64), ARMDK); elc.rotation.z = Math.PI / 2; elc.position.set(0, upL, 0); U.add(elc);
        /* axis 3: the forearm, pointing forward (+z) at elbow 0 */
        var F = new THREE.Group(); F.position.set(0, upL, 0); F.rotation.x = -(o.elbow || 0) * D; U.add(F);
        var foL = 1.15;
        var fa = TXT.roundedBox(0.22, 0.24, foL, 0.06, ARM); fa.position.set(0, 0.02, foL / 2 - 0.05); F.add(fa);
        var fm = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.36, 48), ARMDK); fm.rotation.x = Math.PI / 2; fm.position.set(0, 0.06, -0.22); F.add(fm);
        F.add(K.box(0.24, 0.05, 0.6, ARMDK, 0, 0.13, 0.32, 0.01));
        /* axes 4 to 6: the wrist and the gripper */
        var Wr = new THREE.Group(); Wr.position.set(0, 0.02, foL); Wr.rotation.x = -(o.wrist || 0) * D; F.add(Wr);
        var wr = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.12, 0.2, 56), ARMDK); wr.rotation.x = Math.PI / 2; wr.position.z = 0.06; Wr.add(wr);
        var fl = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.04, 48), GRIP); fl.rotation.x = Math.PI / 2; fl.position.z = 0.18; Wr.add(fl);
        /* the gripper head: a cast body with a hydraulic cylinder on top, and two curved clamp jaws that close around
         * the pipe, each lined with three ridged die inserts, the pipe's centre at (0, 0, 0.5) in the wrist's frame */
        var body = TXT.roundedBox(0.36, 0.22, 0.24, 0.035, GRIP); body.position.z = 0.3; Wr.add(body);
        var cylB = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.34, 48), ARMDK); cylB.rotation.z = Math.PI / 2; cylB.position.set(0, 0.15, 0.3); Wr.add(cylB);
        var rod = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.46, 32), JOINT); rod.rotation.z = Math.PI / 2; rod.position.set(0, 0.15, 0.3); Wr.add(rod);
        /* bolt rings on the gripper body's two flanks, eight cap screws round each */
        [-1, 1].forEach(function (sx) { for (var bk = 0; bk < 8; bk++) { var ang = bk / 8 * Math.PI * 2, cs = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.012, 10), JOINT);
          cs.rotation.z = Math.PI / 2; cs.position.set(sx * 0.184, Math.cos(ang) * 0.065, 0.3 + Math.sin(ang) * 0.065); Wr.add(cs); } });
        for (var bo = 0; bo < 6; bo++) { var bt = K.cyl(0.011, 0.011, 0.012, JOINT, -0.15 + bo * 0.06, 0.11, 0.42, 6); bt.rotation.x = Math.PI / 2; Wr.add(bt); }
        var gr = o.gripR || 0.085, DIE = K.mat("rf-die", { color: 0x3b3d40, metalness: 0.92, roughness: 0.28 });
        [-1, 1].forEach(function (s2) {
          /* a jaw: a thick curved casting lathed round the pipe over 150 degrees, so the two jaws meet at a seam on the
           * front and back, each lined with dark die inserts at its lips and bolted through its back */
          var pc = s2 > 0 ? Math.PI / 2 : Math.PI * 1.5, span = 2.6, r0 = gr + 0.012, r1 = gr + 0.058;
          var jaw = new THREE.Mesh(new THREE.LatheGeometry([new THREE.Vector2(r0, -0.16), new THREE.Vector2(r1, -0.16), new THREE.Vector2(r1 + 0.008, -0.12),
            new THREE.Vector2(r1 + 0.008, 0.12), new THREE.Vector2(r1, 0.16), new THREE.Vector2(r0, 0.16), new THREE.Vector2(r0, -0.16)], 40, pc - span / 2, span), GRIP);
          jaw.material.side = THREE.DoubleSide; jaw.position.set(0, 0, 0.5); Wr.add(jaw);
          [pc - span / 2 + 0.06, pc + span / 2 - 0.06].forEach(function (ph) {
            var ins = K.box(0.012, 0.28, 0.03, DIE, 0, -0.14, 0, 0.002); ins.position.set(Math.sin(ph) * (gr + 0.006), 0, 0.5 + Math.cos(ph) * (gr + 0.006)); ins.rotation.y = ph; Wr.add(ins);
            for (var tt = 0; tt < 7; tt++) { var tooth = K.box(0.024, 0.012, 0.05, JOINT, 0, 0, 0, 0.002); tooth.position.set(Math.sin(ph) * (gr + 0.03), -0.135 + tt * 0.045, 0.5 + Math.cos(ph) * (gr + 0.03)); tooth.rotation.y = ph; Wr.add(tooth); }
          });
          [-0.08, 0.08].forEach(function (yy) { var hb = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.03, 32), JOINT); hb.rotation.z = Math.PI / 2; hb.position.set(s2 * (r1 + 0.02), yy, 0.5); Wr.add(hb); });
          var link = TXT.roundedBox(0.07, 0.26, 0.2, 0.02, GRIP); link.position.set(s2 * (gr + 0.09), 0, 0.37); Wr.add(link);
          /* the link plate's bolt pattern, three by two socket heads on its outer face, and a bolt ring round its pivot */
          for (var lb = 0; lb < 6; lb++) { var sb = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.012, 12), JOINT); sb.rotation.z = Math.PI / 2;
            sb.position.set(s2 * (gr + 0.126), -0.08 + (lb % 3) * 0.08, 0.32 + Math.floor(lb / 3) * 0.1); Wr.add(sb); }
          var pin = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.3, 32), JOINT); pin.position.set(s2 * (gr + 0.09), 0, 0.3); Wr.add(pin);
        });
        /* cable dress: a loom from the turret over the elbow to the wrist, clipped, so the arm reads as a working machine */
        var CABLE = K.mat("rf-cable", { color: 0x15161a, roughness: 0.7 });
        U.add(TXT.tube([[0.2, 0.1, -0.05], [0.24, 0.6, -0.16], [0.22, upL - 0.1, -0.12], [0.2, upL + 0.12, 0.05]], 0.03, CABLE, { segments: 24 }));
        F.add(TXT.tube([[0.15, 0.12, -0.1], [0.15, 0.17, 0.3], [0.14, 0.12, foL - 0.1]], 0.024, CABLE, { segments: 16 }));
        [[U, upL], [T, shoulderH]].forEach(function (pr) { for (var bi = 0; bi < 10; bi++) { var ba = bi / 10 * Math.PI * 2;
          var bolt = K.cyl(0.012, 0.012, 0.02, JOINT, 0.26, 0, 0, 6); bolt.rotation.z = Math.PI / 2; bolt.position.set(0.26, pr[1] + Math.cos(ba) * 0.13, Math.sin(ba) * 0.13); pr[0].add(bolt); } });
        /* a black and yellow hazard band on the pedestal, the one painted warning on the machine */
        G.add(K.box(0.54, 0.08, 0.54, RAIL, 0, ph - 0.24, 0, 0.005));
        G.userData.gripAt = function () { var v = new THREE.Vector3(0, 0, 0.5); Wr.updateWorldMatrix(true, false); return Wr.localToWorld(v); };
        G.userData.parts = { wrist: Wr, forearm: F, upper: U, turret: T };
        G.userData.keepOrigin = true;
        return G;
      }
    });

    /* THE MAST: a lattice derrick standing on the rig floor at its own origin, `h` tall, four legs tapering from `base`
     * to `top` wide, girts every `bay` metres, alternating diagonals, a crown block, a racking board with fingers at
     * `board` metres, and LED floods up the legs (`lamps`). Origin at the mast's foot centre on the floor. */
    K.define("rig_mast", {
      size: [9.6, 44, 9.6], anchor: "base",
      options: { h: 42, base: 9.0, top: 2.2, bay: 2.6, board: 26, lamps: 10, open: 5.2, seed: 1 },
      note: "A lattice drilling mast with crown block, racking board and leg floods; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), h = o.h, n = Math.round(h / o.bay);
        function half(y) { return (o.base + (o.top - o.base) * (y / h)) / 2; }
        var legs = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
        legs.forEach(function (s) { G.add(K.bar([s[0] * half(0), 0, s[1] * half(0)], [s[0] * half(h), h, s[1] * half(h)], 0.13, MAST, 4)); });
        for (var i = 0; i < n; i++) {
          var y0 = i * (h / n), y1 = (i + 1) * (h / n), a0 = half(y0), a1 = half(y1);
          if (y1 < (o.open || 0)) continue;   /* the bottom bay stays open, the way a floor crew walks through it */
          [[1, 1, 1, -1], [1, -1, -1, -1], [-1, -1, -1, 1], [-1, 1, 1, 1]].forEach(function (f, k) {
            G.add(K.bar([f[0] * a1, y1, f[1] * a1], [f[2] * a1, y1, f[3] * a1], 0.055, MAST, 4));
            var flip = (i + k) % 2 === 0;
            G.add(K.bar([f[0] * (flip ? a0 : a1), flip ? y0 : y1, f[1] * (flip ? a0 : a1)], [f[2] * (flip ? a1 : a0), flip ? y1 : y0, f[3] * (flip ? a1 : a0)], 0.045, MAST, 4));
          });
        }
        /* crown block and its sheaves */
        var cw = o.top + 0.8; G.add(K.box(cw, 0.5, cw, DECK, 0, h, 0, 0.04));
        for (var s = -2; s <= 2; s++) { var sv = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.12, 28), JOINT); sv.rotation.z = Math.PI / 2; sv.position.set(s * 0.18, h + 0.85, 0); G.add(sv); }
        G.add(K.box(cw + 0.4, 0.06, cw + 0.4, RAIL, 0, h + 0.5, 0, 0.01));
        /* racking board on the driller's side (+z): a platform and fingers */
        var bw = half(o.board) * 2 + 0.2;
        G.add(K.box(bw + 1.6, 0.08, 1.4, DECK, 0, o.board, -half(o.board) - 0.7, 0.01));
        for (var f = 0; f < 9; f++) G.add(K.box(0.07, 0.07, 2.0, DECK, -bw / 2 - 0.6 + f * ((bw + 1.2) / 8), o.board + 0.08, -half(o.board) - 1.6, 0.005));
        G.add(K.box(bw + 1.6, 0.9, 0.04, RAIL, 0, o.board + 0.08, -half(o.board) - 0.02, 0.005));
        /* floods up the legs, facing in and down */
        var lamps = [];
        for (var L = 0; L < o.lamps; L++) {
          var y = 4 + L * ((h - 6) / Math.max(1, o.lamps - 1)), sg = legs[L % 4], a = half(y) + 0.18;
          var hous = K.box(0.34, 0.24, 0.16, DECK, sg[0] * a, y, sg[1] * a, 0.02); G.add(hous);
          var lens = K.box(0.28, 0.18, 0.02, LAMP, sg[0] * a, y + 0.03, sg[1] * (a - 0.09), 0); G.add(lens);
          lamps.push([sg[0] * a, y + 0.12, sg[1] * (a - 0.1)]);
        }
        G.userData.lamps = lamps; G.userData.board = o.board; G.userData.half = half;
        return G;
      }
    });

    /* THE RIG FLOOR on its substructure: a box truss `subH` tall, a deck `w` by `d` of grating with a rotary table and
     * slips at the well centre, a mousehole, yellow handrails, a V door and catwalk ramp on +z, and the driller's
     * cabin (the doghouse) with lit glazing on -x. Origin at the substructure's foot centre; the well centre is at
     * (0, subH, 0). userData.floorY is the deck height. */
    K.define("rig_floor", {
      size: [14, 12, 16],
      options: { subH: 7.6, w: 11, d: 11, cabin: true, ramp: true, seed: 1 },
      note: "A drilling rig floor on its substructure with rotary, slips, handrails, V door, catwalk and driller's cabin; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), H = o.subH, w = o.w, d = o.d;
        /* substructure: boxes and braces */
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (s) { G.add(K.box(0.7, H - 0.5, 0.7, MAST, s[0] * (w / 2 - 0.5), 0, s[1] * (d / 2 - 0.5), 0.03)); });
        [-1, 1].forEach(function (s) {
          G.add(K.box(w, 0.6, 0.5, MAST, 0, H - 0.6, s * (d / 2 - 0.5), 0.03));
          G.add(K.box(0.5, 0.6, d, MAST, s * (w / 2 - 0.5), H - 0.6, 0, 0.03));
          G.add(K.box(w, 0.4, 0.6, MAST, 0, 0, s * (d / 2 - 0.5), 0.02));
          G.add(K.bar([-w / 2 + 0.5, 0.4, s * (d / 2 - 0.5)], [w / 2 - 0.5, H - 0.6, s * (d / 2 - 0.5)], 0.09, MAST, 8));
          G.add(K.bar([s * (w / 2 - 0.5), 0.4, -d / 2 + 0.5], [s * (w / 2 - 0.5), H - 0.6, d / 2 - 0.5], 0.09, MAST, 8));
        });
        /* deck plate and grating texture by strips */
        G.add(K.box(w, 0.14, d, DECK, 0, H - 0.04, 0, 0.02));
        for (var g = -w / 2 + 0.15; g < w / 2; g += 0.3) G.add(K.box(0.035, 0.02, d - 0.2, JOINT, g, H + 0.1, 0, 0));
        for (var g2 = -d / 2 + 0.6; g2 < d / 2; g2 += 1.2) G.add(K.box(w - 0.2, 0.024, 0.05, BAND, 0, H + 0.1, g2, 0));
        /* rotary table: a dark steel table with a bright worn rim, a square master bushing, and three slip segments
         * wrapped round the well, each a curved wedge with grooved die faces and a handle */
        G.add(K.cyl(0.98, 1.0, 0.24, DECK, 0, H + 0.08, 0, 56));
        G.add(K.cyl(0.97, 1.0, 0.05, JOINT, 0, H + 0.31, 0, 72));
        G.add(K.box(0.86, 0.06, 0.86, GRIP, 0, H + 0.33, 0, 0.02));
        var RIM = K.mat("rf-rim", { color: 0xb3b5b7, metalness: 0.55, roughness: 0.34 });
        G.add(K.cyl(0.62, 0.64, 0.035, RIM, 0, H + 0.39, 0, 72));
        for (var sl = 0; sl < 3; sl++) {
          var a0 = sl / 3 * Math.PI * 2 + 0.26, len = Math.PI * 2 / 3 - 0.52;
          var seg = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.22, 0.34, 24, 1, false, a0, len), GRIP); seg.position.y = H + 0.6; G.add(seg);
          for (var gv = 0; gv < 6; gv++) { var gr2 = 0.172 + (0.22 - 0.172) * (1 - (gv + 0.5) / 6);
            var groove = new THREE.Mesh(new THREE.CylinderGeometry(gr2 + 0.003, gr2 + 0.003, 0.012, 24, 1, true, a0 + 0.02, len - 0.04), K.mat("rf-groove", { color: 0x1d1e20, metalness: 0.6, roughness: 0.6 }));
            groove.material.side = THREE.DoubleSide; groove.position.y = H + 0.46 + gv * 0.05; G.add(groove); }
          var am = a0 + len / 2, hx = Math.sin(am), hz = Math.cos(am);
          G.add(K.bar([hx * 0.19, H + 0.77, hz * 0.19], [hx * 0.27, H + 0.86, hz * 0.27], 0.012, JOINT, 24));
        }
        G.add(K.cyl(0.12, 0.12, 0.06, DECK, 2.1, H + 0.1, 1.3, 20));   /* mousehole */
        /* handrails on three sides */
        function rail(a, b) { G.add(K.bar([a[0], H + 1.07, a[1]], [b[0], H + 1.07, b[1]], 0.025, RAIL, 8)); G.add(K.bar([a[0], H + 0.55, a[1]], [b[0], H + 0.55, b[1]], 0.02, RAIL, 8)); }
        rail([-w / 2 + 0.1, -d / 2 + 0.1], [w / 2 - 0.1, -d / 2 + 0.1]); rail([w / 2 - 0.1, -d / 2 + 0.1], [w / 2 - 0.1, d / 2 - 0.1]);
        rail([-w / 2 + 0.1, d / 2 - 0.1], [-1.4, d / 2 - 0.1]); rail([1.4, d / 2 - 0.1], [w / 2 - 0.1, d / 2 - 0.1]);
        for (var p = -w / 2 + 0.1; p <= w / 2; p += 1.8) { G.add(K.bar([p, H + 0.1, -d / 2 + 0.1], [p, H + 1.1, -d / 2 + 0.1], 0.025, RAIL, 8)); }
        /* V door and catwalk ramp */
        if (o.ramp) { var ramp = K.box(1.4, 0.12, 9.0, DECK, 0, 0, 0, 0.02); ramp.rotation.x = Math.atan2(H, 9.0) * -1 + 0; ramp.position.set(0, H / 2, d / 2 + 3.6); ramp.rotation.x = Math.atan2(H - 0.9, 8.4); G.add(ramp);
          G.add(K.box(1.6, 0.9, 12, DECK, 0, 0, d / 2 + 8.6, 0.03)); }
        /* the driller's cabin on -x: a steel box with lit glazing toward the well */
        if (o.cabin) {
          var cx = -w / 2 - 1.3;
          G.add(K.box(2.6, 2.6, 3.6, CAB, cx, H, -1.2, 0.05));
          var gl = K.box(0.03, 1.1, 2.8, CABLIT, cx + 1.31, H + 1.1, -1.2, 0); G.add(gl);
          var gl2 = K.box(0.04, 1.14, 2.84, GLASS, cx + 1.33, H + 1.09, -1.2, 0); G.add(gl2);
          G.add(K.box(2.8, 0.08, 3.8, DECK, cx, H + 2.6, -1.2, 0.01));
          G.add(K.box(2.6, 0.12, 3.4, DECK, cx, H - 0.12, -1.2, 0.01));
        }
        G.userData.floorY = H + 0.12; G.userData.keepOrigin = true;
        return G;
      }
    });
    /* THE RED ZONE GATE: a pipe swing gate `w` wide across an opening in the floor's handrail, 1.07 m tall, three
     * rails and a diagonal brace in sun worn safety yellow, hung on pin hinges from a post at -x, a chain latch at +x,
     * and a riveted sign plate with a rolled edge on the top rails, red with a white band. No lettering is drawn on
     * the plate: the words a frame needs are set in DOM. Origin on the floor at the opening's centre, front on +z. */
    K.define("red_zone_gate", {
      size: [2.0, 1.15, 0.2],
      options: { w: 1.8, open: 0, seed: 1 },
      note: "A safety yellow pipe swing gate with a riveted red sign plate and a chain latch; drawn to illustrate.",
      make: function (o) {
        var G = new THREE.Group(), w = o.w || 1.8;
        var SIGN = K.mat("rf-sign", { color: 0x9a2a24, metalness: 0.3, roughness: 0.5 });
        var WHITE = K.mat("rf-white", { color: 0xd9d6cf, metalness: 0.2, roughness: 0.55 });
        var CHAIN = K.mat("rf-chain", { color: 0x55575a, metalness: 0.9, roughness: 0.4 });
        [-w / 2 - 0.06, w / 2 + 0.06].forEach(function (x) { G.add(K.cyl(0.038, 0.038, 1.2, RAIL, x, 0, 0, 16)); G.add(K.cyl(0.05, 0.05, 0.03, RAIL, x, 1.2, 0, 16)); });
        var L = new THREE.Group(); L.position.x = -w / 2; L.rotation.y = -(o.open || 0); G.add(L);
        [0.12, 0.58, 1.04].forEach(function (y) { L.add(K.bar([0.02, y, 0], [w - 0.02, y, 0], 0.024, RAIL, 12)); });
        L.add(K.bar([0.02, 0.12, 0], [0.02, 1.04, 0], 0.024, RAIL, 12)); L.add(K.bar([w - 0.02, 0.12, 0], [w - 0.02, 1.04, 0], 0.024, RAIL, 12));
        L.add(K.bar([0.05, 0.14, 0], [w - 0.05, 1.02, 0], 0.02, RAIL, 10));
        [0.3, 0.86].forEach(function (y) { L.add(K.cyl(0.03, 0.03, 0.09, JOINT, -0.04, y - 0.045, 0, 10)); });
        var sw = Math.min(0.62, w * 0.4), sx = w * 0.28;
        var plate = TXT.roundedBox(sw, 0.34, 0.012, 0.01, SIGN); plate.position.set(sx, 0.81, 0.03); L.add(plate);
        var band = K.box(sw * 0.9, 0.07, 0.004, WHITE, sx, 0.84, 0.038, 0); L.add(band);
        [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(function (c) { L.add(K.cyl(0.008, 0.008, 0.006, JOINT, sx + c[0] * (sw / 2 - 0.03), 0.81 + 0.17 + c[1] * 0.14 - 0.003, 0.04, 8)); });
        for (var k = 0; k < 6; k++) { var lk = new THREE.Mesh(new THREE.TorusGeometry(0.018, 0.005, 6, 10), CHAIN); lk.position.set(w - 0.02 + 0.02 * k, 0.9 - 0.028 * k, 0.02); lk.rotation.y = k % 2 ? Math.PI / 2 : 0; L.add(lk); }
        G.userData.signAt = function () { var v = new THREE.Vector3(sx, 0.81 + 0.17, 0.04); L.updateWorldMatrix(true, false); return L.localToWorld(v); };
        G.userData.keepOrigin = true;
        return G;
      }
    });
  };

  /* THE RIG'S OWN FLOODS. A rig floor at night is lit by LED floods on the mast, so a frame on the floor adds one or
   * two of them as shadow casting spots: cold white, from high on the mast leg on the deck light's side, aimed at the
   * well. They light what the deck key can't reach from 30 m and they cast the way the key does, down and to the right. */
  N.flood = function (THREE, R, from, at, o) {
    o = o || {};
    var sp = new THREE.SpotLight(o.color || 0xf2f4ff, o.i == null ? 900 : o.i, o.reach || 40, o.angle || 0.5, o.penumbra == null ? 0.55 : o.penumbra, 2);
    sp.position.set(from[0], from[1], from[2]); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0006; sp.shadow.normalBias = 0.03;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
  };

  /* THE TYPE BAND GOES TO THE DARK, darken only: a near black gradient from the top of the frame to just under the dek,
   * so the far rails and the mast's girts behind the type sink rather than strike through it. */
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

  /* THE ARM REACHES WHAT IT HOLDS. Pose a pipe_robot so its gripper's centre lands on a world point with the jaws
   * vertical (a pipe standing in the derrick): yaw toward the target, then a coarse to fine search over shoulder and
   * elbow, the wrist set to keep the gripper level. Returns the miss in metres, which a frame can assert on. */
  N.reach = function (THREE, rob, target, o) {
    o = o || {};
    var D = Math.PI / 180, P = rob.userData.parts, inv = new THREE.Matrix4(), T = new THREE.Vector3(target[0], target[1], target[2]);
    rob.updateMatrixWorld(true); inv.copy(rob.matrixWorld).invert();
    var t = T.clone().applyMatrix4(inv);
    P.turret.rotation.y = Math.atan2(t.x, t.z);
    var best = [0, 0, 1e9, 1e9], ev = new THREE.Vector3();
    /* `low` asks for the pose that keeps the elbow lowest among those that land, so the arm reaches in level */
    function err(sh, el) { P.upper.rotation.x = -sh * D; P.forearm.rotation.x = -el * D; P.wrist.rotation.x = (sh + el) * D;
      rob.updateMatrixWorld(true); var e = rob.userData.gripAt().distanceTo(T);
      P.forearm.getWorldPosition(ev); return [e, e + (o.low ? Math.max(0, ev.y - T.y) * 0.02 : 0)]; }
    for (var sh = -60; sh <= 120; sh += 4) for (var el = -150; el <= 70; el += 4) { var e = err(sh, el); if (e[1] < best[3]) best = [sh, el, e[0], e[1]]; }
    for (var step = 2; step > 0.05; step /= 2) { var b0 = best.slice();
      for (var a = -2; a <= 2; a++) for (var b = -2; b <= 2; b++) { var e2 = err(b0[0] + a * step, b0[1] + b * step); if (e2[1] < best[3]) best = [b0[0] + a * step, b0[1] + b * step, e2[0], e2[1]]; } }
    return err(best[0], best[1])[0];
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
    /* the key is the rig's own LED flood, cold and high, held a step down so a floor it grazes never clips to white */
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { color: 0xeef2ff, i: (W.rig.key.i || 3) * (N.KEY_SCALE || 1), shadowSize: size || 14, mapSize: map || 2048 }) });
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
      ".lab.ru { color:#C99474; }",
      ".lab.gold { color:#D08A6F; }",
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
  /* THE TRACTOR'S HEADLAMPS, ON. The kit's lens material is shared, so lighting it lights every tractor in the frame,
   * which is right: every truck in this deck is running. Glows sit on the four round lamps (the kit's bezels at x
   * ±0.78 ±0.075, y 1.52 above the tractor's base, just behind the bumper's face), and one spot throws their light down
   * the lane ahead. The truck must face +z in its own frame. */
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
  global.CH = N;
})(this);
