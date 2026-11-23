/* deck/2026-11-22-fairtest-bespoke.js, the SPINE for the November 22nd, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * the Dell Medical School and IC² Institute AI Learning Lab at UT Austin, where 80 clinicians meet actors playing patients,
 * half with Claude and half with UpToDate's AI switched off, and researchers watch how each group reasons (tx-2026-0257).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the deck's TONE (explainer), bespoke:true, the tone's grade and the accent.
 * Each frame picks its own world (TXT.sky(R, world) or TXT.studio / TXT.interior), turns its own key
 * (TXT.deckRig(..., { light })) and places its own type, seated with CH.seat. It mounts the type faces and the furniture
 * (CH.start), and hands a frame the helpers below. There is no drawFrame.
 *
 * THE ACCENT. Cyan #22d3ee, the explainer tone's own accent, means ONE thing: THE TOOL WITHIN REACH, the one thing the
 * study's design lets differ. Where both arms are in frame it is a PAIR at equal intensity (CH.TOOL_GLOW), never one brighter.
 * It never marks a result, a person, or a group as better. NO RESULTS EXIST and no frame implies one.
 *
 * THE MODELS. The kit holds people, desks, chairs, laptops, monitors, a clinical workstation cart and student desks. The
 * chassis builds what the kit lacks, in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17
 * can queue the lift: exam_table (a padded clinic exam table with raised back, drawer base, step and paper roll),
 * stethoscope (binaurals, tubing, chest piece; coiled, draped or hung), timing_rail (an anodised rail with brass graduations
 * and a knurled carriage), handoff_tray (a track with a sliding shuttle pan), output_slip (a printed slip with greeked lines,
 * optional annotation marks) and paper_roll (a mounted roll of exam paper unrolled to a given length). Everything drawn is
 * drawn to illustrate: no real room, no product interface, no logo, no legible screen.
 * Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("fairtest.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "fairtest", look: "v2", tone: "explainer", bespoke: true,
    light: { az: -40, el: 34 },
    sky: { preset: "v2explainer" },
    ground: "#f0b884",
    material: "#ede6d6",
    accent: "#22d3ee",
    grade: TXLOOK.grade("explainer")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261122; N.TONE = "explainer"; N.P = TXLOOK.palette("explainer"); N.INK = N.P.ink;
  N.ACCENT = 0x22d3ee;        /* cyan: the tool within reach, and nothing else */
  N.TOOL_GLOW = { color: 0x22d3ee, intensity: 1.6 };   /* every lit tool reads this, so a pair is equal in code */
  N.LIMESTONE = 0xede6d6; N.CALICHE = 0xe4d8c3; N.VINYL = 0x4e5fa8; N.OAK = 0xc89b6a; N.SHADE = 0x2a1e78;
  N.BRASS = 0xc9a24a; N.INDIGO_AL = 0x2e3a8c; N.PAPER = 0xf7f3ea;
  N.GOLD = N.ACCENT;
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };
  N.glassMat = function (K, tint) {
    return K.mat("ft-glass" + (tint || ""), { color: tint || 0xeaf6ff, metalness: 0, roughness: 0.05, transmission: 0.9, ior: 1.47, thickness: 0.006,
      transparent: true, opacity: 1, clearcoat: 1, clearcoatRoughness: 0.03, specularIntensity: 1, envMapIntensity: 1.4, side: N.T.DoubleSide }, true);
  };
  /* the tool's glow, one material, so every lit tool in a frame is the same light */
  N.toolMat = function (K) { return K.mat("ft-tool", { color: 0x061820, emissive: N.TOOL_GLOW.color, emissiveIntensity: N.TOOL_GLOW.intensity, roughness: 0.2 }); };
  N.goldMat = N.toolMat;
  /* greeked lines on paper, never legible: short bars at a pitch, broken into words by the seed */
  N.paperTex = function (THREE, seed, lines, marks) {
    var r = N.rng(seed || 7);
    return N.canvasTex(THREE, 512, 340, function (g, w, h) {
      g.fillStyle = "#f7f3ea"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 2600; i++) { g.fillStyle = "rgba(120,110,90," + (r() * 0.05).toFixed(3) + ")"; g.fillRect(r() * w, r() * h, 1.2, 1.2); }
      var n = lines || 9;
      for (var L = 0; L < n; L++) {
        var y = 40 + L * (h - 70) / n, x = 34, end = w - 34 - (L === n - 1 ? 180 : r() * 40);
        while (x < end) { var ww = 14 + r() * 46; g.fillStyle = "rgba(60,64,92,0.42)"; g.fillRect(x, y, Math.min(ww, end - x), 5); x += ww + 8 + r() * 6; }
      }
      if (marks) {
        g.strokeStyle = "#0ea5c4"; g.lineWidth = 5; g.lineCap = "round";
        [[2, 0.2, 0.62], [5, 0.35, 0.8], [7, 0.12, 0.5]].forEach(function (m) { var y = 40 + m[0] * (h - 70) / n + 12; g.beginPath(); g.moveTo(w * m[1], y); g.lineTo(w * m[2], y + 1); g.stroke(); });
        g.beginPath(); g.moveTo(w - 26, 60); g.lineTo(w - 26, 150); g.stroke();
        g.beginPath(); g.arc(w - 40, 230, 14, Math.PI * 1.1, Math.PI * 2.6); g.stroke();
      }
    });
  };

  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.exam_table) return;
    N.T = THREE;
    var shadowAll = function (g) { g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return g; };
    var steel = function () { return K.mat("ft-steel", { color: 0xd6dbe0, metalness: 0.9, roughness: 0.32 }); };
    var vinyl = function (c) { return K.mat("ft-vinyl" + (c || ""), { color: c || N.VINYL, roughness: 0.42, clearcoat: 0.6, clearcoatRoughness: 0.35, sheen: 0.3 }, true); };

    /* EXAM TABLE. 1.85 x 0.84 x 0.70 m. A padded vinyl top 0.08 m thick on a cabinet base 0.62 m tall with two drawers and steel
     * pulls, a pull out step at 0.30 m on the foot end (+x), a back section hinged at the head end (-x) raised `back` degrees,
     * a 0.53 m paper roll on a dowel at the head and one paper sheet running the length. Front (drawers) on +z. */
    K.define("exam_table", {
      size: [1.95, 1.2, 0.72],
      options: { back: 38, vinyl: null, cabinet: 0xe8ecef, paper: true, step: true },
      note: "Padded clinic exam table, illustrative and unmarked: vinyl top 1.85 x 0.70 m at 0.70 m, raised back section, two drawer cabinet base, pull out step, paper roll at the head and a paper sheet. Front (drawers) on +z, head at -x. userData.seat is the seat top height.",
      make: function (o) {
        o = Object.assign({ back: 38, vinyl: null, cabinet: 0xe8ecef, paper: true, step: true }, o || {});
        var g = new THREE.Group(), cab = K.mat("ft-cab" + o.cabinet, { color: o.cabinet, roughness: 0.38, metalness: 0.05, clearcoat: 0.3 }, true), V = vinyl(o.vinyl);
        var kick = K.mat("ft-kick", { color: 0x2b2f3a, roughness: 0.7 });
        K.box(1.5, 0.06, 0.56, kick, 0.05, 0, 0, 0.01, g);
        K.box(1.6, 0.56, 0.62, cab, 0.05, 0.06, 0, 0.025, g);
        [0.22, 0.42].forEach(function (y) {
          K.box(0.62, 0.17, 0.012, cab, -0.32, y - 0.085, 0.312, 0.008, g);
          K.box(0.62, 0.17, 0.012, cab, 0.42, y - 0.085, 0.312, 0.008, g);
          K.bar([-0.44, y + 0.0, 0.33], [-0.2, y + 0.0, 0.33], 0.007, steel(), 10, g);
          K.bar([0.3, y + 0.0, 0.33], [0.54, y + 0.0, 0.33], 0.007, steel(), 10, g);
        });
        if (o.step) { K.box(0.36, 0.035, 0.42, cab, 0.98, 0.28, 0, 0.012, g); K.box(0.34, 0.012, 0.4, kick, 0.98, 0.315, 0, 0.005, g); }
        var seatY = 0.62;
        K.box(1.2, 0.08, 0.7, V, 0.32, seatY, 0, 0.03, g);
        var hinge = new THREE.Group(); hinge.position.set(-0.28, seatY + 0.04, 0); g.add(hinge);
        var backPad = K.box(0.62, 0.08, 0.7, V, -0.31, -0.04, 0, 0.03, hinge); hinge.rotation.z = -o.back * Math.PI / 180;
        if (o.paper) {
          var P = K.mat("ft-exampaper", { color: 0xfbfaf6, roughness: 0.88, sheen: 0.2 }, true);
          K.box(1.2, 0.002, 0.53, P, 0.32, seatY + 0.081, 0, 0, g);
          K.box(0.62, 0.002, 0.53, P, -0.31, 0.041, 0, 0, hinge);
          var roll = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.55, 28), P); roll.rotation.x = Math.PI / 2;
          roll.position.set(-0.64, 0.07, 0); hinge.add(roll);
          K.bar([-0.64, 0.07, -0.3], [-0.64, 0.07, 0.3], 0.008, steel(), 8, hinge);
        }
        g.userData.seat = seatY + 0.08;
        return shadowAll(g);
      }
    });

    /* STETHOSCOPE. Chrome binaurals in a Y about 0.15 m, soft ear tips, tubing 12 mm across, a steel chest piece 45 mm across.
     * pose 'coiled' (lying flat, origin on the surface, about 0.22 m across), 'hung' (hanging from a hook at origin, about
     * 0.45 m tall, for a pegboard), tubing colour from `tube`. Front on +z. */
    K.define("stethoscope", {
      size: [0.24, 0.05, 0.24],
      options: { pose: "coiled", tube: 0x2a7f86, seed: 1 },
      note: "Stethoscope at true scale: chrome binaurals, ear tips, coloured tubing, polished steel chest piece. pose 'coiled' lies flat on a surface; pose 'hung' hangs from a hook at its origin (y negative). tube sets the tubing colour.",
      make: function (o) {
        o = Object.assign({ pose: "coiled", tube: 0x2a7f86, seed: 1 }, o || {});
        var g = new THREE.Group(), r = N.rng(77 + (o.seed || 0) * 13);
        var T = K.mat("ft-tube" + o.tube, { color: o.tube, roughness: 0.48, clearcoat: 0.5, clearcoatRoughness: 0.3 }, true), C = K.finish.chrome(), S = steel();
        var tubeAlong = function (pts, rad) { var c = new THREE.CatmullRomCurve3(pts.map(function (p) { return new THREE.Vector3(p[0], p[1], p[2]); })); var m = new THREE.Mesh(new THREE.TubeGeometry(c, 96, rad, 10, false), T); g.add(m); return c; };
        var chest = function (p, flat) {
          var cp = new THREE.Group(); cp.position.set(p[0], p[1], p[2]); g.add(cp);
          var d = new THREE.Mesh(new THREE.CylinderGeometry(0.0225, 0.0225, 0.012, 36), S); cp.add(d);
          var rim = new THREE.Mesh(new THREE.TorusGeometry(0.0225, 0.0025, 10, 36), C); rim.rotation.x = Math.PI / 2; rim.position.y = 0.006; cp.add(rim);
          var stem = new THREE.Mesh(new THREE.CylinderGeometry(0.005, 0.006, 0.03, 12), C); stem.position.set(0, 0.006, -0.03); stem.rotation.x = Math.PI / 2; cp.add(stem);
          if (!flat) cp.rotation.x = Math.PI / 2;
          return cp;
        };
        if (o.pose === "hung") {
          /* hanging from the hook: binaurals over the hook at the top, tubing falling in a loop, chest piece at the bottom */
          var L = [-0.035, 0, 0], R2 = [0.035, 0, 0];
          [L, R2].forEach(function (s, i) { K.bar([s[0] * 0.4, -0.02, 0.01], [s[0], -0.12, 0.012], 0.0032, C, 8, g); var tip = new THREE.Mesh(new THREE.SphereGeometry(0.008, 12, 10), K.mat("ft-tip", { color: 0x1b1c22, roughness: 0.6 })); tip.position.set(s[0] * 0.4, -0.016, 0.012); g.add(tip); });
          var sway = (r() - 0.5) * 0.04;
          tubeAlong([[0, -0.12, 0.014], [0.012 + sway, -0.2, 0.02], [0.05 + sway, -0.3, 0.025], [0.02 + sway, -0.4, 0.028], [-0.03 + sway, -0.35, 0.03], [-0.025 + sway, -0.26, 0.03], [0.0 + sway, -0.31, 0.032]], 0.006);
          K.bar([-0.035, -0.12, 0.012], [0.035, -0.12, 0.012], 0.004, C, 8, g);
          chest([0.0 + sway, -0.335, 0.045], false);
        } else {
          /* coiled flat on a surface */
          var pts = [], turns = 1.6, n = 40;
          for (var i = 0; i <= n; i++) { var t = i / n, a = t * turns * Math.PI * 2 + r() * 0.2, rad = 0.095 - t * 0.04; pts.push([Math.cos(a) * rad, 0.006 + t * 0.006, Math.sin(a) * rad]); }
          tubeAlong(pts, 0.006);
          var e = pts[pts.length - 1];
          K.bar([e[0], 0.012, e[2]], [e[0] - 0.05, 0.01, e[2] + 0.07], 0.003, C, 8, g);
          K.bar([e[0], 0.012, e[2]], [e[0] + 0.03, 0.01, e[2] + 0.08], 0.003, C, 8, g);
          chest([pts[0][0] + 0.03, 0.006, pts[0][2] + 0.01], true);
        }
        return shadowAll(g);
      }
    });

    /* TIMING RAIL. An anodised extrusion `length` m long (x axis, from the near zero stop at x=0 toward +x), 0.04 x 0.06 m, brass
     * graduation ridges every `pitch` m with NO numerals, rubber end stops, and a knurled brass carriage 0.08 m long at `at` m
     * from the zero stop (0 = parked hard against it). Origin at the zero stop on the surface. */
    K.define("timing_rail", {
      size: [1.2, 0.08, 0.06],
      options: { length: 1.2, pitch: 0.05, at: 0 },
      note: "Illustrative timing rail: anodised indigo aluminium extrusion, brass graduation ridges with no numerals, rubber end stops, knurled brass carriage at `at` metres from the zero stop. Origin at the zero stop, rail along +x.",
      make: function (o) {
        o = Object.assign({ length: 1.2, pitch: 0.05, at: 0 }, o || {});
        var g = new THREE.Group(), A = K.mat("ft-anod", { color: N.INDIGO_AL, metalness: 0.85, roughness: 0.34 }), B = K.mat("ft-brass", { color: N.BRASS, metalness: 1, roughness: 0.28 }), Rb = K.finish.rubber();
        K.box(o.length, 0.04, 0.06, A, o.length / 2, 0, 0, 0.004, g);
        K.box(o.length - 0.02, 0.006, 0.014, K.mat("ft-slot", { color: 0x141a3a, roughness: 0.6 }), o.length / 2, 0.037, 0, 0.002, g);
        for (var x = o.pitch; x < o.length - 0.02; x += o.pitch) { var major = Math.abs(x / (o.pitch * 4) - Math.round(x / (o.pitch * 4))) < 1e-6; K.box(0.003, 0.004, major ? 0.024 : 0.014, B, x, 0.04, 0.03 - (major ? 0.012 : 0.007), 0.001, g); }
        K.box(0.02, 0.055, 0.07, Rb, -0.01, 0, 0, 0.006, g); K.box(0.02, 0.055, 0.07, Rb, o.length + 0.01, 0, 0, 0.006, g);
        var car = new THREE.Group(); car.position.set(o.at + 0.04, 0.04, 0); g.add(car);
        K.box(0.08, 0.026, 0.07, B, 0, 0, 0, 0.004, car);
        var knob = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.03, 40), B); knob.position.set(0, 0.04, 0); car.add(knob);
        for (var k = 0; k < 24; k++) { var a = k / 24 * Math.PI * 2; var ridge = new THREE.Mesh(new THREE.BoxGeometry(0.002, 0.028, 0.003), B); ridge.position.set(Math.cos(a) * 0.0165, 0.04, Math.sin(a) * 0.0165); ridge.rotation.y = -a; car.add(ridge); }
        g.userData.carriage = car;
        return shadowAll(g);
      }
    });

    /* HANDOFF TRAY. A track 0.34 m long along z (clinician's side at +z, tool's side at -z), an anodised indigo channel with a
     * brass pan 0.12 m square on a sliding shuttle at `at` (0 = parked on the clinician's side, 1 = on the tool's side), and a
     * second brass pan fixed at the far end. `filled` puts a paper card in the shuttle pan. Origin on the surface. */
    K.define("handoff_tray", {
      size: [0.14, 0.04, 0.4],
      options: { at: 0, filled: false },
      note: "Illustrative handoff tray: anodised indigo track along z, a brass shuttle pan that slides from the clinician's side (+z, at 0) to the tool's side (-z, at 1), a fixed empty pan at the far end. Origin on the surface.",
      make: function (o) {
        o = Object.assign({ at: 0, filled: false }, o || {});
        var g = new THREE.Group(), A = K.mat("ft-anod", { color: N.INDIGO_AL, metalness: 0.85, roughness: 0.34 }), B = K.mat("ft-brass", { color: N.BRASS, metalness: 1, roughness: 0.28 });
        K.box(0.06, 0.012, 0.4, A, 0, 0, 0, 0.003, g);
        K.box(0.008, 0.01, 0.4, A, -0.026, 0.012, 0, 0.002, g); K.box(0.008, 0.01, 0.4, A, 0.026, 0.012, 0, 0.002, g);
        var pan = function (z, parent) {
          var p = new THREE.Group(); p.position.set(0, 0.014, z); parent.add(p);
          K.box(0.12, 0.004, 0.12, B, 0, 0, 0, 0.002, p);
          [[0, 0.06], [0, -0.06]].forEach(function (q) { K.box(0.12, 0.016, 0.004, B, 0, 0.004, q[1], 0.0015, p); });
          [[0.06, 0], [-0.06, 0]].forEach(function (q) { K.box(0.004, 0.016, 0.12, B, q[0], 0.004, 0, 0.0015, p); });
          return p;
        };
        var sp = pan(0.13 - o.at * 0.26, g);
        if (o.filled) K.box(0.09, 0.003, 0.07, K.mat("ft-card", { color: N.PAPER, roughness: 0.9 }), 0, 0.005, 0, 0, sp);
        g.userData.shuttle = sp;
        return shadowAll(g);
      }
    });

    /* OUTPUT SLIP. A printed slip 0.216 x 0.14 m, 0.25 mm, with greeked lines that never read, an optional `annotated` layer of
     * raised cyan marks (0.6 mm proud, as ink ridges), and a slight curl. Origin at its centre on the surface. */
    K.define("output_slip", {
      size: [0.216, 0.004, 0.14],
      options: { annotated: false, seed: 3, curl: 0.004 },
      note: "Printed slip with greeked, illegible lines; annotated:true adds raised cyan annotation marks. Lies flat, origin at its centre on the surface.",
      make: function (o) {
        o = Object.assign({ annotated: false, seed: 3, curl: 0.004 }, o || {});
        var g = new THREE.Group(), geo = new THREE.PlaneGeometry(0.216, 0.14, 24, 12);
        var pos = geo.attributes.position; for (var i = 0; i < pos.count; i++) { var x = pos.getX(i); pos.setZ(i, o.curl * Math.pow(Math.abs(x) / 0.108, 3)); } geo.computeVertexNormals();
        var m = new THREE.Mesh(geo, K.mat("ft-slip" + o.seed + (o.annotated ? "a" : ""), { color: 0xffffff, roughness: 0.92, map: N.paperTex(THREE, o.seed, 9, o.annotated) }));
        m.rotation.x = -Math.PI / 2; m.position.y = 0.0004; g.add(m);
        return shadowAll(g);
      }
    });

    /* PAPER ROLL. A wall or counter mounted roll of exam paper 0.53 m wide (along z) on a steel bracket, its sheet unrolled
     * `length` metres along +x across the surface, with perforation ticks every `tick` metres. Origin at the roll's foot on
     * the surface. */
    K.define("paper_roll", {
      size: [0.6, 0.16, 0.6],
      options: { length: 1, tick: 0.2 },
      note: "Exam paper roll 0.53 m wide on a steel bracket, its sheet unrolled `length` metres along +x with perforation ticks every `tick` metres. Origin at the roll's foot on the surface.",
      make: function (o) {
        o = Object.assign({ length: 1, tick: 0.2 }, o || {});
        var g = new THREE.Group(), P = K.mat("ft-exampaper", { color: 0xfbfaf6, roughness: 0.88, sheen: 0.2 }, true), S = steel();
        var roll = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.53, 32), P); roll.rotation.x = Math.PI / 2; roll.position.set(0, 0.075, 0); g.add(roll);
        var core = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.56, 16), K.mat("ft-core", { color: 0xb08a5a, roughness: 0.8 })); core.rotation.x = Math.PI / 2; core.position.set(0, 0.075, 0); g.add(core);
        [-0.29, 0.29].forEach(function (z) { K.box(0.03, 0.09, 0.012, S, 0, 0, z, 0.004, g); });
        K.box(o.length, 0.0015, 0.53, P, 0.06 + o.length / 2, 0, 0, 0, g);
        var perf = K.mat("ft-perf", { color: 0x9aa3b8, roughness: 0.8 });
        for (var x = o.tick; x < o.length - 1e-6; x += o.tick) K.box(0.003, 0.0006, 0.5, perf, 0.06 + x, 0.0015, 0, 0, g);
        g.userData.end = 0.06 + o.length;
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
