/* deck/2026-10-30-balance.js — the chassis for the 2026-10-30 deck: Plano City Council's citywide AI purchase,
 * ChatGPT Enterprise and the Darwin AI governance platform, on its October 12th consent agenda (tx-2026-0234).
 *
 * THE VISUAL ARGUMENT. One brass laboratory pillar balance and its slotted weights. One weight is a drawing unit of
 * unit_usd dollars from figures.json (the greatest common divisor of the item's four lines, which is the Microsoft line),
 * so every line of the purchase is a whole count of identical weights: polished brass for ChatGPT Enterprise, heat blued
 * steel for Darwin AI, nickel for Microsoft, and empty wells for the reserve. The beam tilts toward the heavier pan by a
 * drawing rule (TILT_PER_UNIT degrees per weight of difference), and the needle hangs from the beam, so the needle's
 * reading in graduations IS the difference in weights.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky, one warm seam low on the key's side, the
 * instrument in a pool of light on a chalk plinth and the plaza behind it gone dark.
 *
 * THE LIGHT is azimuth -58, elevation 13. +x is east and +z is south. A camera looking north (-z) has the key on its
 * LEFT, every lit edge is on the left, and every cast runs long to the right. TXBENCH reliefs read the same declaration:
 * lit from the upper left, casting to the lower right.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `slotted_weight` (a slotted brass, blued or nickel disc,
 * 68 mm across and 10 mm thick), `weight_stack` (n of them), `equal_arm_balance` (a pillar balance 0.66 m tall with a
 * 0.64 m beam, pans on three rods, a needle and a 39 graduation arc), `weight_case` (a fitted pecan case, shut) and
 * `chalk_plinth` (an Austin chalk block). All drawn to illustrate, in the kit's conventions (metres, y up, origin on the
 * ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is bluebonnet, #4E5FA8, and it means ONE thing: the heat blued steel of the Darwin AI weights, the watcher.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated. Every
 * frame composes its own picture, and every count a frame draws is read from figures.json in that frame's own code. The
 * chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("balance.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "balance",
    light: { az: -58, el: 13 },
    sky: "lastLight",
    ground: "#08070C",
    material: "#B08D57",
    accent: "#4E5FA8",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.12, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261030 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261030;
  N.ACCENT = 0x4e5fa8;   /* bluebonnet, brand.yaml's token, and it means ONE thing: the watcher's blued steel */
  N.INK = "#ECE8DF";
  /* THE DRAWING RULE for the beam: degrees of tilt per weight of difference between the pans. A drawing rule, never a
   * claim, and the deck calls the tilt a drawing wherever it is read. */
  N.TILT_PER_UNIT = 1.5;
  N.balanceState = function (left, right) { return (left - right) * N.TILT_PER_UNIT; };

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */
  function noiseTex(THREE, seed, lo, hi, n, sz) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "rgb(128,128,128)"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < n; i++) { var v = Math.floor(lo + r() * (hi - lo)); x.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; x.fillRect(r() * 256, r() * 256, sz, sz); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  /* PECAN GRAIN, a streaked albedo map: heartwood with darker growth lines */
  function grainTex(THREE, seed) {
    var c = document.createElement("canvas"); c.width = 512; c.height = 128; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "#6b4a32"; x.fillRect(0, 0, 512, 128);
    for (var i = 0; i < 160; i++) {
      var y = r() * 128, a = 0.05 + r() * 0.14; x.strokeStyle = "rgba(30,18,10," + a + ")"; x.lineWidth = 0.6 + r() * 1.8;
      x.beginPath(); x.moveTo(0, y); for (var k = 0; k <= 16; k++) x.lineTo(k * 32, y + Math.sin(k * 0.7 + i) * 2.2 * r()); x.stroke();
    }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
  }
  N.mats = function (THREE, K) {
    if (N._M) return N._M;
    var tooth = noiseTex(THREE, 7, 108, 150, 9000, 1.6);
    var chalkBump = noiseTex(THREE, 11, 70, 190, 14000, 2.2);
    N._M = {
      brass: new THREE.MeshPhysicalMaterial({ color: 0xc9a265, metalness: 1, roughness: 0.24, clearcoat: 0.2, clearcoatRoughness: 0.4, bumpMap: tooth, bumpScale: 0.25 }),
      brassDull: new THREE.MeshPhysicalMaterial({ color: 0x8f7344, metalness: 1, roughness: 0.42, bumpMap: tooth, bumpScale: 0.3 }),
      blued: new THREE.MeshPhysicalMaterial({ color: 0x4e5fa8, metalness: 0.9, roughness: 0.24, clearcoat: 0.45, clearcoatRoughness: 0.18, bumpMap: tooth, bumpScale: 0.2 }),
      nickel: new THREE.MeshPhysicalMaterial({ color: 0xa9adb0, metalness: 1, roughness: 0.26, bumpMap: tooth, bumpScale: 0.15 }),
      slot: new THREE.MeshStandardMaterial({ color: 0x0b0a0c, roughness: 0.8 }),
      pecan: new THREE.MeshStandardMaterial({ map: grainTex(THREE, 5), roughness: 0.55, bumpMap: tooth, bumpScale: 0.4 }),
      ebony: new THREE.MeshPhysicalMaterial({ color: 0x1a1210, roughness: 0.38, clearcoat: 0.5, clearcoatRoughness: 0.3 }),
      chalk: new THREE.MeshStandardMaterial({ color: 0xcfc8b6, roughness: 0.92, bumpMap: chalkBump, bumpScale: 1.6 }),
      felt: new THREE.MeshStandardMaterial({ color: 0x111014, roughness: 1 })
    };
    return N._M;
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.slotted_weight) return;
    var M = N.mats(THREE, K);
    function shade(o) { o.traverse(function (c) { if (c.isMesh) { c.castShadow = c.receiveShadow = true; } }); return o; }
    var WR = 0.034, WT = 0.010;
    N.WR = WR; N.WT = WT;
    function finishOf(f) { return f === "blued" ? M.blued : f === "nickel" ? M.nickel : M.brass; }

    /* ONE SLOTTED WEIGHT: a turned disc 68 mm across and 10 mm thick with a chamfer on both faces, a radial slot to the
     * centre bore so it can be slipped onto a hanger, and a knurled band round its edge that catches the key as a row of
     * tiny lit ticks. finish brass|blued|nickel. Drawn to illustrate. */
    K.define("slotted_weight", {
      size: [WR * 2, WT, WR * 2],
      options: { finish: "brass", yaw: 0 },
      note: "A slotted disc weight 68 mm by 10 mm, a drawing unit. finish brass|blued|nickel, yaw (radians) turns the slot.",
      make: function (o) {
        var g = new THREE.Group(), mat = finishOf(o.finish), c = 0.0018;
        var prof = [[0.006, 0], [WR - c, 0], [WR, c], [WR, WT - c], [WR - c, WT], [0.006, WT]].map(function (p) { return new THREE.Vector2(p[0], p[1]); });
        var body = new THREE.Mesh(new THREE.LatheGeometry(prof, 96), mat); g.add(body);
        /* the knurl: thin vertical ribs proud of the edge in a band, instanced */
        var rib = new THREE.BoxGeometry(0.0009, WT * 0.46, 0.0012), list = [];
        for (var i = 0; i < 120; i++) { var a = i / 120 * Math.PI * 2; list.push([Math.cos(a) * (WR + 0.0003), WT / 2, Math.sin(a) * (WR + 0.0003), -a, 1]); }
        K.instances(rib, mat, list, g);
        /* the slot, a dark radial cut from the bore to the rim on +z (yaw turns it) */
        var slot = new THREE.Mesh(new THREE.BoxGeometry(0.008, WT + 0.0004, WR), M.slot); slot.position.set(0, WT / 2, WR / 2); g.add(slot);
        var bore = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, WT + 0.0004, 24), M.slot); bore.position.y = WT / 2; g.add(bore);
        g.rotation.y = o.yaw || 0;
        return shade(g);
      }
    });

    /* A STACK of n weights, each turned a little so the slots stagger, each a hair off centre as stacked by hand */
    K.define("weight_stack", {
      anchor: "base",
      size: [WR * 2, WT * 19, WR * 2],
      options: { n: 10, finish: "brass", seed: 1 },
      note: "n slotted_weights stacked by hand, slots staggered. n, finish, seed.",
      make: function (o) {
        var g = new THREE.Group(), r = lcg(o.seed || 1);
        for (var i = 0; i < o.n; i++) {
          var w = K.make("slotted_weight", { finish: o.finish, yaw: r() * Math.PI * 2 });
          w.position.set((r() - 0.5) * 0.0016, i * WT, (r() - 0.5) * 0.0016); g.add(w);
        }
        return g;
      }
    });

    /* THE BALANCE: an equal arm pillar balance. An ebonized base on four levelling feet, a turned brass pillar, a brass
     * beam on a knife edge at PIVOT_Y, two stirrups each hanging a spun brass pan on three rods, a nickel needle fixed to
     * the beam pointing down, and a nickel silver arc on the pillar engraved with 39 graduations (no numerals) and a brass
     * index. left and right are weight counts in each pan, tilt (degrees) is N.balanceState(left, right) unless given,
     * index is the graduation the brass index marks. The pans always hang plumb. */
    var PIVOT_Y = 0.62, ARM = 0.32, ROD = 0.36, NEEDLE = 0.36, GRAD = 39;
    N.PIVOT_Y = PIVOT_Y; N.ARM = ARM; N.ROD = ROD; N.NEEDLE = NEEDLE;
    K.define("equal_arm_balance", {
      anchor: "base",
      size: [0.86, 0.66, 0.24],
      options: { left: 0, right: 0, leftFinish: "brass", rightFinish: "blued", tilt: null, index: null, seed: 63 },
      note: "A laboratory pillar balance 0.66 m tall, beam 0.64 m. left, right (weight counts), leftFinish, rightFinish, tilt (deg), index (graduation).",
      make: function (o) {
        var g = new THREE.Group();
        var tilt = (o.tilt == null ? N.balanceState(o.left, o.right) : o.tilt) * Math.PI / 180;
        /* base and feet */
        var base = TXT.roundedBox(0.30, 0.036, 0.20, 0.008, M.ebony); base.position.y = 0.012 + 0.018; g.add(base);
        [[-0.13, -0.08], [0.13, -0.08], [-0.13, 0.08], [0.13, 0.08]].forEach(function (p) {
          var f = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.013, 0.012, 24), M.brassDull); f.position.set(p[0], 0.006, p[1]); g.add(f);
        });
        /* the pillar, turned brass with rings */
        var pp = [[0.0, 0.048], [0.034, 0.048], [0.034, 0.056], [0.022, 0.066], [0.016, 0.09], [0.016, 0.50], [0.022, 0.51], [0.022, 0.525], [0.014, 0.535], [0.012, PIVOT_Y - 0.012], [0.0, PIVOT_Y - 0.012]];
        g.add(new THREE.Mesh(new THREE.LatheGeometry(pp.map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 64), M.brass));
        /* the arc scale on a bracket, below the beam, facing +z */
        var arcG = new THREE.Group(), ay = PIVOT_Y, R0 = NEEDLE - 0.03, R1 = NEEDLE - 0.005, span = (GRAD - 1) / 2 * N.TILT_PER_UNIT * Math.PI / 180 + 0.04;
        var arcShape = new THREE.Shape();
        arcShape.absarc(0, 0, R1, -Math.PI / 2 - span, -Math.PI / 2 + span, false);
        arcShape.absarc(0, 0, R0, -Math.PI / 2 + span, -Math.PI / 2 - span, true);
        var arcGeo = new THREE.ExtrudeGeometry(arcShape, { depth: 0.003, bevelEnabled: true, bevelThickness: 0.0008, bevelSize: 0.0008, bevelSegments: 2, curveSegments: 96 });
        var arc = new THREE.Mesh(arcGeo, M.nickel); arc.position.set(0, ay, 0.024); arcG.add(arc);
        var tick = new THREE.BoxGeometry(0.0011, 1, 0.0009), list = [];
        for (var k = 0; k < GRAD; k++) {
          var u = k - (GRAD - 1) / 2, a = -Math.PI / 2 + u * N.TILT_PER_UNIT * Math.PI / 180, len = (u % 5 === 0) ? 0.016 : 0.009;
          var rm = R1 - 0.002 - len / 2;
          list.push({ x: Math.cos(a) * rm, y: ay + Math.sin(a) * rm, a: a, len: len });
        }
        list.forEach(function (t) { var m = new THREE.Mesh(tick, M.slot); m.scale.y = t.len; m.position.set(t.x, t.y, 0.0285); m.rotation.z = t.a + Math.PI / 2; arcG.add(m); });
        if (o.index != null) {
          var ia = -Math.PI / 2 + o.index * N.TILT_PER_UNIT * Math.PI / 180;
          var tri = new THREE.Shape(); tri.moveTo(0, 0); tri.lineTo(-0.004, -0.009); tri.lineTo(0.004, -0.009); tri.lineTo(0, 0);
          var im = new THREE.Mesh(new THREE.ExtrudeGeometry(tri, { depth: 0.002, bevelEnabled: false }), M.brass);
          im.position.set(Math.cos(ia) * (R0 - 0.001), ay + Math.sin(ia) * (R0 - 0.001), 0.026); im.rotation.z = ia + Math.PI / 2; arcG.add(im);
          N.indexAt = [im.position.x, im.position.y, im.position.z];
        }
        var br = TXT.roundedBox(0.016, 0.05, 0.024, 0.003, M.brass); br.position.set(0, ay - R0 - 0.02, 0.012); arcG.add(br);
        g.add(arcG);
        /* the beam group, rotated about the knife edge */
        var beam = new THREE.Group(); beam.position.y = PIVOT_Y; beam.rotation.z = tilt; g.add(beam);
        var bar = TXT.roundedBox(ARM * 2 + 0.03, 0.026, 0.012, 0.004, M.brass); beam.add(bar);
        var boss = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.03, 48), M.brass); boss.rotation.x = Math.PI / 2; beam.add(boss);
        var ped = new THREE.Mesh(new THREE.ConeGeometry(0.012, 0.03, 32), M.brass); ped.position.y = 0.03; beam.add(ped);
        /* the needle, a tapered nickel blade hanging from the beam centre */
        var nShape = new THREE.Shape(); nShape.moveTo(-0.004, 0); nShape.lineTo(0.004, 0); nShape.lineTo(0.0006, -NEEDLE); nShape.lineTo(-0.0006, -NEEDLE); nShape.lineTo(-0.004, 0);
        var needle = new THREE.Mesh(new THREE.ExtrudeGeometry(nShape, { depth: 0.0016, bevelEnabled: false }), M.nickel); needle.position.z = 0.03; beam.add(needle);
        /* the ends: a stirrup at each, the pans hanging plumb from it */
        [[-1, o.left, o.leftFinish], [1, o.right, o.rightFinish]].forEach(function (s) {
          var ex = s[0] * ARM, endW = new THREE.Vector3(ex * Math.cos(tilt), PIVOT_Y + ex * Math.sin(tilt), 0);
          var hook = new THREE.Mesh(new THREE.TorusGeometry(0.009, 0.0025, 12, 24), M.brass); hook.position.copy(endW); hook.position.y -= 0.01; g.add(hook);
          var panY = endW.y - ROD, PR = 0.10;
          var panProf = [[0, 0], [PR * 0.8, 0.002], [PR, 0.012], [PR + 0.002, 0.016], [PR - 0.002, 0.016], [PR * 0.8, 0.006], [0, 0.004]];
          var pan = new THREE.Mesh(new THREE.LatheGeometry(panProf.map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 72), M.brass);
          pan.position.set(endW.x, panY, 0); g.add(pan);
          for (var k = 0; k < 3; k++) {
            var a = k / 3 * Math.PI * 2 + Math.PI / 6;
            K.bar([endW.x, endW.y - 0.016, 0], [endW.x + Math.cos(a) * PR * 0.96, panY + 0.014, Math.sin(a) * PR * 0.96], 0.0012, M.nickel, 8, g);
          }
          if (s[1] > 0) { var st = K.make("weight_stack", { n: s[1], finish: s[2], seed: (o.seed || 1) + s[0] * 7 }); st.position.set(endW.x, panY + 0.004, 0); g.add(st); }
        });
        g.userData.tilt = tilt;
        return shade(g);
      }
    });

    /* THE CASE, SHUT: a fitted pecan case with a lid, a brass latch and two brass hinges, 0.62 x 0.08 x 0.36 m */
    K.define("weight_case", {
      size: [0.62, 0.09, 0.36],
      options: { open: false },
      note: "A fitted pecan weight case, shut, 0.62 x 0.09 x 0.36 m, brass latch and hinges.",
      make: function (o) {
        var g = new THREE.Group();
        var b = TXT.roundedBox(0.62, 0.05, 0.36, 0.006, M.pecan); b.position.y = 0.025; g.add(b);
        var l = TXT.roundedBox(0.622, 0.036, 0.362, 0.008, M.pecan); l.position.y = 0.05 + 0.018 + 0.001; g.add(l);
        var seam = new THREE.Mesh(new THREE.BoxGeometry(0.624, 0.0016, 0.364), M.slot); seam.position.y = 0.0505; g.add(seam);
        var latch = TXT.roundedBox(0.05, 0.03, 0.008, 0.002, M.brass); latch.position.set(0, 0.05, 0.183); g.add(latch);
        var hasp = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.012, 16), M.brass); hasp.rotation.x = Math.PI / 2; hasp.position.set(0, 0.05, 0.19); g.add(hasp);
        [-0.2, 0.2].forEach(function (x) { var h = TXT.roundedBox(0.05, 0.016, 0.006, 0.002, M.brassDull); h.position.set(x, 0.05, -0.183); g.add(h); });
        return shade(g);
      }
    });

    /* THE PLINTH: an Austin chalk block with a bevelled top edge, w x h x d */
    K.define("chalk_plinth", {
      size: [0.9, 1.0, 0.6],
      options: { w: 0.9, h: 1.0, d: 0.6 },
      note: "An Austin chalk plinth block. w, h, d (m).",
      make: function (o) {
        var g = new THREE.Group(), w = o.w || 0.9, h = o.h || 1.0, d = o.d || 0.6;
        var m = TXT.roundedBox(w, h, d, 0.03, M.chalk); m.position.y = h / 2; g.add(m);
        return shade(g);
      }
    });
  };

  N.glowTex = function (THREE) {
    if (N._glow) return N._glow;
    var c = document.createElement("canvas"); c.width = c.height = 64; var g = c.getContext("2d");
    var gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.18, "rgba(255,255,255,0.6)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); N._glow = new THREE.CanvasTexture(c); return N._glow;
  };
  N.noShadows = function (R) { R.scene.traverse(function (o) { if (o.userData && o.userData.noShadow) { o.castShadow = false; o.receiveShadow = false; } }); };
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  /* AIM SO A POINT LANDS WHERE THE LAYOUT WANTS IT: from a fixed camera, solve the look target so
   * `point` projects to screen (sx, sy). Returns the look target. */
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
  /* THE KEY is the last light, low and warm, and the world's cool rim is held low so a shadow side
   * of weathering steel stays warm dark rather than the navy of the sky */
  N.rigSpec = function (W, size, map) {
    var rim = Object.assign({}, W.rig.rim, { i: (W.rig.rim.i || 0.8) * 0.45 });
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { shadowSize: size || 12, mapSize: map || 2048 }) });
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
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "6,5,10";
    if (bottom != null && a > 0) {
      var fade = o.fade || 180, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + a + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + (a * 0.85) + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  N.shadeLow = function (cx, o) {
    o = o || {};
    var top = o.from, a = Math.min(0.5, o.a == null ? 0.35 : o.a), fade = o.fade || 200;
    var g = cx.createLinearGradient(0, top - fade, 0, N.H);
    g.addColorStop(0, "rgba(6,5,10,0)"); g.addColorStop(fade / (N.H - top + fade), "rgba(6,5,10," + a + ")"); g.addColorStop(1, "rgba(6,5,10," + a + ")");
    cx.fillStyle = g; cx.fillRect(0, top - fade, N.W, N.H - top + fade);
  };
  N.unacne = function (R, nb) { R.scene.traverse(function (l) { if (l.isDirectionalLight && l.castShadow) { l.shadow.normalBias = nb == null ? 0.04 : nb; l.shadow.bias = -0.0004; } }); return R; };
  /* THE SKY'S OWN LIGHT, held down: the navy dome lights every shadow face blue through the image
   * based light, so a frame calls this after TXT.sky to keep shadows warm dark */
  N.warm = function (R, k) {
    R.scene.environmentIntensity = k == null ? 0.3 : k;
    /* THE GROUND'S BOUNCE. The key's pool on caliche throws warm light back up into every shadow face;
     * without it no. 57's stringers and pier sides crushed to L* 0 and read as cut-outs */
    if (!R._bounce) { R._bounce = new N.T.HemisphereLight(0x161a24, 0x4a4743, N.BOUNCE); R.scene.add(R._bounce); }
    return R;
  };
  N.BOUNCE = 0.6;
  N.post = function (cx, o) {
    o = o || {};
    if (o.a !== 0 && !o.low) N.shade(cx, { a: o.a, to: o.to, fade: o.fade, pad: o.pad });
    if (o.low) N.shadeLow(cx, o.low);
    var y0 = N.H - (o.veilH || 240), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(6,5,10," + (Math.min(0.5, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    var f = document.querySelector(".tx-site");
    if (f && o.footWash) {
      var r = f.getBoundingClientRect(), feather = N.H - r.bottom, fa = Math.min(o.footWash, 0.54);
      var fw = cx.createLinearGradient(0, r.top - feather, 0, N.H);
      fw.addColorStop(0, "rgba(6,5,10,0)");
      fw.addColorStop(feather / (N.H - r.top + feather), "rgba(6,5,10," + fa + ")");
      fw.addColorStop(1, "rgba(6,5,10," + fa + ")");
      cx.fillStyle = fw; cx.fillRect(0, r.top - feather, N.W, N.H - r.top + feather);
    }
  };
  /* A RESERVE under one line of type: a feathered dark patch, darken only */
  N.knock = function (cx, els, a) {
    (els || []).forEach(function (el) {
      if (typeof el === "string") el = document.querySelector(el);
      if (!el) return;
      var r = el.getBoundingClientRect(), off = 4000;
      cx.save(); cx.shadowColor = "rgba(6,5,10," + (a == null ? 0.5 : Math.min(0.54, a)) + ")"; cx.shadowBlur = 44; cx.shadowOffsetX = off * 2;
      cx.fillStyle = "#000"; cx.fillRect(r.left - 14 - off, r.top - 6, r.width + 28, r.height + 12); cx.restore();
    });
  };
  N.leader = function (svg, from, to) {
    var u = document.createElementNS("http://www.w3.org/2000/svg", "line");
    u.setAttribute("x1", from[0]); u.setAttribute("y1", from[1]); u.setAttribute("x2", to[0]); u.setAttribute("y2", to[1]);
    u.setAttribute("stroke", "#07070C"); u.setAttribute("stroke-width", "5"); u.setAttribute("stroke-opacity", "0.6"); svg.appendChild(u);
    var l = document.createElementNS("http://www.w3.org/2000/svg", "line");
    l.setAttribute("x1", from[0]); l.setAttribute("y1", from[1]); l.setAttribute("x2", to[0]); l.setAttribute("y2", to[1]);
    l.setAttribute("stroke", N.INK); l.setAttribute("stroke-width", "2"); l.setAttribute("stroke-opacity", "0.85"); svg.appendChild(l);
    var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", to[0]); c.setAttribute("cy", to[1]); c.setAttribute("r", "5"); c.setAttribute("fill", N.INK); svg.appendChild(c);
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#D6D0C4", halo = "rgba(4,3,8,0.6)", halo2 = "rgba(4,3,8,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#07070C; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      "/* Manrope and Fraunces contextual alternates curl a straight apostrophe after some letters (no. 61, no. 62), so calt is off on every line of type */",
      ".hook, .dek, .lab, .kick, .count, .src { font-feature-settings:\"calt\" 0; }",
      ".hook, .dek, .kick, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }",
      /* the footer lines carry a tight halo only: a 14 px blur read as a smudge on a lit ground */
      ".tx-site, .src { text-shadow:0 0 2px " + halo + ", 0 1px 4px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D6D0C4" });
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
  /* a relief frame boots the type alone, with no three.js world */
  N.bootFlat = async function (o) {
    await document.fonts.ready;
    N.start(o);
    return document.getElementById("art").getContext("2d");
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
  /* a DOM label pinned to a world point, nudged by (dx, dy) */
  N.pin = function (THREE, R, id, p, dx, dy) {
    var q = N.project(THREE, R, p), el = document.getElementById(id);
    if (!el) return q;
    el.style.left = Math.round(q[0] + (dx || 0)) + "px"; el.style.top = Math.round(q[1] + (dy || 0)) + "px";
    return q;
  };




  global.CH = N;
})(this);
