/* deck/2026-10-21-cell.js — the chassis for the 2026-10-21 deck: Lockheed Martin is bringing Hadrian's
 * highly automated 24 machine machining cell into its Grand Prairie missile parts plant, run by
 * Lockheed's own workforce and expected to be operational in early 2027, while the release never says
 * what the AI Hadrian describes does inside this cell (tx-2026-0225).
 *
 * THE WORLD. lastLight, the house register and a STAGED world: the sun just down, a near black sky,
 * one low warm key entering through the plant's west doors and windows, every subject standing in a
 * pool of it and the plant behind it gone dark. Machined aluminium only reads under a raking key, and a
 * low sun through a west door at shift change is the one light that rakes every machined face.
 *
 * THE LIGHT is azimuth -64, elevation 9. +x is east and +z is south, az runs from +z toward +x, so the
 * key sits low in the west south west of every subject: every lit face is a west or south face, every
 * cast runs long to the east north east. A material relief reads it from the left of its frame, low:
 * the key comes from the left and a little below the top, and every cast runs long to the right.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `housing_part` (an illustrative pocketed
 * aluminium housing, raw or finished), `machine_vise`, `machining_centre` (a vertical machining centre
 * with sliding doors, spindle, tool drum, pendant and stack light, full or low detail) and
 * `machine_bay` (an empty bay on the floor: an epoxy pad, a taped outline, levelling plates and a drop
 * cord). Each is built in the kit's conventions (metres, y up, origin on the ground, front on +z) so
 * Phase 17 can queue the lift. Every one is drawn to illustrate and to no maker's design. No missile and
 * no company mark is drawn anywhere in this deck.
 *
 * THE ACCENT is comal lit, #8FE0F0, and it means ONE thing: Hadrian's cell, which is not running yet.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way
 * type is seated. Every frame composes its own picture, and the figures a frame draws are written in
 * that frame's own code where figure_bearing.py reads them. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("cell.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "cell",
    light: { az: -64, el: 9 },
    sky: "lastLight",
    ground: "#08060F",
    material: "#C9CDD1",
    accent: "#8FE0F0",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.9, strength: 0.08, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261021 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261021;
  N.ACCENT = 0x8fe0f0;   /* comal lit, brand.yaml's, and it means ONE thing: Hadrian's cell */
  N.INK = "#ECE6DA";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  N.accentMat = function (THREE, glow) {
    var k = "_acc" + (glow || 0);
    if (N[k]) return N[k];
    N[k] = new THREE.MeshStandardMaterial({ color: new THREE.Color(N.ACCENT), roughness: 0.45, metalness: 0.0,
      emissive: new THREE.Color(N.ACCENT), emissiveIntensity: glow == null ? 0.4 : glow });
    return N[k];
  };

  /* THE PART, in plan, the one shape every frame draws. An illustrative pocketed housing 0.12 m wide
   * (x) and 0.08 m deep (z), its top 0.03 m up: a base, an outer wall 6 mm thick, a 6 mm rib across
   * its middle making two pockets, four counterbored holes in the corners. `N.partPlan(u, v)` takes u
   * across and v down the part, each 0 to 1, and returns { h, kind } with h from 0 (pocket floor) to 1
   * (top face), so a relief draws the same part the 3D frames build. kind is 'top', 'floor', 'wall' or
   * 'hole'. */
  N.PART = { w: 0.12, d: 0.08, h: 0.03, floor: 0.012, wall: 0.006, hole: 0.0045, cb: 0.0075 };
  N.partPlan = function (u, v) {
    var P = N.PART, x = u * P.w, z = v * P.d, t = P.wall;
    var hx = [0.012, P.w - 0.012], hz = [0.012, P.d - 0.012];
    for (var i = 0; i < 2; i++) for (var j = 0; j < 2; j++) {
      var r = Math.hypot(x - hx[i], z - hz[j]);
      if (r < P.hole * 0.5) return { h: 0.0, kind: "hole" };
      if (r < P.cb * 0.5) return { h: 0.75, kind: "floor" };
    }
    var inOuter = x > t && x < P.w - t && z > t && z < P.d - t;
    var onRib = Math.abs(x - P.w / 2) < t / 2;
    if (inOuter && !onRib && x > 0.018 && x < P.w - 0.018) return { h: P.floor / P.h, kind: "floor" };
    if (inOuter && !onRib) return { h: 1, kind: "top" };
    return { h: 1, kind: "top" };
  };

  N.installKit = function (K, THREE, TXT) {
    if (K.registry.machining_centre) return;
    var alu = function (aniso) {
      return K.mat("mc_alu_" + (aniso ? 1 : 0), { color: 0x98a2ac, metalness: 0.9, roughness: 0.32, anisotropy: aniso ? 0.7 : 0, clearcoat: 0.15, clearcoatRoughness: 0.25 }, true);
    };
    var aluRaw = function () { return K.mat("mc_alu_raw", { color: 0xb9bdc0, metalness: 0.95, roughness: 0.48 }); };
    var paint = function () { return K.mat("mc_paint", { color: 0x35383d, metalness: 0.25, roughness: 0.5 }); };
    var paintPale = function () { return K.mat("mc_paint_pale", { color: 0x8c9092, metalness: 0.2, roughness: 0.48 }); };
    var plinth = function () { return K.mat("mc_plinth", { color: 0x17181b, metalness: 0.15, roughness: 0.6 }); };
    var steel = function () { return K.mat("mc_steel", { color: 0xaeb3b7, metalness: 0.9, roughness: 0.3, anisotropy: 0.5 }, true); };
    var iron = function () { return K.mat("mc_iron", { color: 0x4a4d50, metalness: 0.85, roughness: 0.42 }); };
    var black = function () { return K.mat("mc_black", { color: 0x111214, metalness: 0.1, roughness: 0.55 }); };
    var rubber = function () { return K.mat("mc_rubber", { color: 0x0e0f10, metalness: 0, roughness: 0.85 }); };
    var glass = function (lit) {
      return lit ? K.mat("mc_glass_lit", { color: 0x1d2629, metalness: 0.1, roughness: 0.08, emissive: 0x9fb3b8, emissiveIntensity: 0.22 })
                 : K.mat("mc_glass", { color: 0x0a0d0f, metalness: 0.2, roughness: 0.06 });
    };
    var carbide = function () { return K.mat("mc_carbide", { color: 0x70757a, metalness: 0.9, roughness: 0.32 }); };
    var hose = function () { return K.mat("mc_hose", { color: 0x40566a, metalness: 0.05, roughness: 0.4 }); };

    /* THE PART: an illustrative pocketed aluminium housing, 0.12 x 0.03 x 0.08 m, built wall by wall so
     * its two pockets are real openings that hold a shadow. state 'finished' is bright anisotropic
     * 6061 with chamfered edges, 'raw' is a sawn billet 0.13 x 0.035 x 0.09 m with a dull face. */
    K.define("housing_part", {
      size: [0.13, 0.035, 0.09],
      options: { state: "finished" },
      note: "Illustrative pocketed aluminium housing (finished) or its sawn billet (raw). Drawn to illustrate, no program's design.",
      make: function (o) {
        var g = new THREE.Group(), P = N.PART;
        if (o.state === "raw") {
          var b = TXT.roundedBox(0.13, 0.035, 0.09, 0.0015, aluRaw()); b.position.y = 0.0175; g.add(b);
          /* bandsaw marks across the two sawn faces, fine dark lines */
          var sm = K.mat("mc_saw", { color: 0x7c8084, metalness: 0.9, roughness: 0.6 });
          for (var i = 0; i < 14; i++) { var l = K.box(0.0006, 0.034, 0.0006, sm, -0.0651, 0.0005, -0.042 + i * 0.0065); g.add(l); var l2 = l.clone(); l2.position.x = 0.0651; g.add(l2); }
          return g;
        }
        /* ONE SOLID BILLET WITH TWO BLIND POCKETS: the outline extruded the part's full height with the two
         * pockets as holes through it and a small chamfer on every edge, then a milled floor set into each
         * pocket at the floor depth, so there is no seam and the pockets hold their own shadow */
        var A = alu(true), t = P.wall, fl = P.floor;
        var hw = P.w / 2, hd = P.d / 2, pr = 0.004;
        function rrect(x0, y0, x1, y1, r) {
          var sh = new THREE.Shape();
          sh.moveTo(x0 + r, y0); sh.lineTo(x1 - r, y0); sh.quadraticCurveTo(x1, y0, x1, y0 + r); sh.lineTo(x1, y1 - r);
          sh.quadraticCurveTo(x1, y1, x1 - r, y1); sh.lineTo(x0 + r, y1); sh.quadraticCurveTo(x0, y1, x0, y1 - r); sh.lineTo(x0, y0 + r);
          sh.quadraticCurveTo(x0, y0, x0 + r, y0); return sh;
        }
        var outline = rrect(-hw, -hd, hw, hd, 0.003);
        var pockets = [[-hw + t, -hd + t, -t / 2, hd - t], [t / 2, -hd + t, hw - t, hd - t]];
        pockets.forEach(function (q) { var hole = rrect(q[0], q[1], q[2], q[3], pr); outline.holes.push(new THREE.Path(hole.getPoints(12))); });
        var geo = new THREE.ExtrudeGeometry(outline, { depth: P.h - 0.001, bevelEnabled: true, bevelThickness: 0.0008, bevelSize: 0.0008, bevelSegments: 2, curveSegments: 12 });
        geo.rotateX(-Math.PI / 2); geo.translate(0, 0.0008, 0);
        var body = new THREE.Mesh(geo, A); g.add(body);
        var floorM = K.mat("mc_alu_floor", { color: 0x8f969c, metalness: 0.75, roughness: 0.45 });
        var hole = K.mat("mc_hole", { color: 0x08090a, roughness: 0.9 });
        pockets.forEach(function (q) {
          var f = K.box(q[2] - q[0] - 0.0004, fl, q[3] - q[1] - 0.0004, floorM, (q[0] + q[2]) / 2, 0, (q[1] + q[3]) / 2); g.add(f);
          /* a counterbored bolt hole in each pocket floor */
          var cxh = (q[0] + q[2]) / 2, czh = (q[1] + q[3]) / 2;
          var cb = new THREE.Mesh(new THREE.CylinderGeometry(0.0055, 0.0055, 0.0008, 24), K.mat("mc_alu_cb", { color: 0x9da3a8, metalness: 0.8, roughness: 0.4 })); cb.position.set(cxh, fl + 0.0001, czh); g.add(cb);
          var bore = new THREE.Mesh(new THREE.CylinderGeometry(0.003, 0.003, 0.001, 16), hole); bore.position.set(cxh, fl + 0.0004, czh); g.add(bore);
        });
        /* four tapped holes on the top face, one in each corner */
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (sg) {
          var th = new THREE.Mesh(new THREE.CylinderGeometry(0.0018, 0.0018, 0.0012, 12), hole);
          th.position.set(sg[0] * (hw - t / 2 - 0.0005), P.h + 0.0002, sg[1] * (hd - t / 2 - 0.0005)); g.add(th);
        });
        return g;
      }
    });

    /* A MACHINE VISE, 0.15 m jaws, 0.40 m long on +z, its jaws open by `open` metres around a part. */
    K.define("machine_vise", {
      size: [0.17, 0.12, 0.42],
      options: { open: 0.08 },
      note: "Precision machine vise: cast body, fixed and moving hardened jaws, screw, handle. Jaws across x, screw on +z.",
      make: function (o) {
        /* a real vise: the fixed jaw is the body's raised far end, the moving jaw rides the bed toward it, and
         * the screw runs from the moving jaw through the end housing to a crank handle. The jaw gap is centred
         * on the origin, so the part placed there sits between the two hardened plates */
        var g = new THREE.Group(), I = iron(), S = steel(), B = black();
        var JP = K.mat("mc_jawplate", { color: 0x8a8f93, metalness: 0.85, roughness: 0.38 });
        var JB = K.mat("mc_jawbody", { color: 0x6f7478, metalness: 0.8, roughness: 0.5 });
        var h0 = o.open / 2, zF = -h0 - 0.09, zE = h0 + 0.15;
        var body = TXT.roundedBox(0.15, 0.06, zE - zF, 0.006, I); body.position.set(0, 0.03, (zF + zE) / 2); g.add(body);
        var bed = TXT.roundedBox(0.11, 0.006, zE - h0 - 0.08, 0.002, K.mat("mc_vise_bed", { color: 0x3e4246, metalness: 0.8, roughness: 0.5 })); bed.position.set(0, 0.063, (h0 + 0.07 + zE - 0.02) / 2); g.add(bed);
        var fixedJ = TXT.roundedBox(0.15, 0.055, 0.09, 0.0012, JB); fixedJ.position.set(0, 0.0875, -h0 - 0.045); g.add(fixedJ);
        var movJ = TXT.roundedBox(0.15, 0.05, 0.06, 0.0012, JB); movJ.position.set(0, 0.085, h0 + 0.03); g.add(movJ);
        [-1, 1].forEach(function (sg) { var jaw = TXT.roundedBox(0.148, 0.04, 0.008, 0.001, JP); jaw.position.set(0, 0.09, sg * (h0 - 0.0035)); g.add(jaw);
          for (var k = 0; k < 6; k++) { var sr = K.box(0.148, 0.0012, 0.0012, B, 0, 0.074 + k * 0.006, sg * (h0 - 0.0078)); g.add(sr); }
          /* two socket cap screws holding each hardened plate to its jaw, on the plate's top edge */
          [-0.05, 0.05].forEach(function (x) { var cs = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.003, 16), B); cs.position.set(x, 0.1115, sg * (h0 - 0.0035)); g.add(cs); }); });
        var endH = TXT.roundedBox(0.12, 0.07, 0.03, 0.006, I); endH.position.set(0, 0.035, zE - 0.015); g.add(endH);
        var screw = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.011, zE - h0 - 0.06, 20), S); screw.rotation.x = Math.PI / 2; screw.position.set(0, 0.045, (h0 + 0.06 + zE) / 2); g.add(screw);
        for (var t = 0; t < 12; t++) { var th = new THREE.Mesh(new THREE.TorusGeometry(0.011, 0.0015, 6, 16), S); th.position.set(0, 0.045, h0 + 0.07 + t * (zE - h0 - 0.08) / 12); g.add(th); }
        var hex = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.022, 6), S); hex.rotation.x = Math.PI / 2; hex.position.set(0, 0.045, zE + 0.011); g.add(hex);
        g.add(K.bar([-0.12, 0.045, zE + 0.03], [0.12, 0.045, zE + 0.03], 0.0065, B, 12));
        [-0.12, 0.12].forEach(function (x) { var knob = new THREE.Mesh(new THREE.SphereGeometry(0.012, 14, 10), B); knob.position.set(x, 0.045, zE + 0.03); g.add(knob); });
        /* the jaws stay centred on the origin, so a part placed there is clamped by both plates */
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* THE MACHINING CENTRE: an illustrative vertical machining centre, 2.60 m wide, 2.70 m tall to its
     * roof and 2.35 m deep, front on +z. Graphite enclosure over a charcoal plinth with a kick recess, a
     * pale fascia band, bi-parting sliding doors over a 1.10 x 0.95 m opening each leaf with a
     * laminated window in a black gasket and a bar handle, a cast iron T-slot table with way covers, a
     * vise holding the part, a spindle head on its column with a holder and an end mill, coolant hoses,
     * a work light bar, a side tool drum under a hood, a control pendant on a swing arm at the front
     * right, a chip conveyor to a cart at the rear and a three segment stack light. Options:
     *   door 0 (shut) to 1 (open), part 'finished'|'raw'|null, workLight, lamp 'off'|'warm'|'accent',
     *   screen 'off'|'on', chips, lod 'full'|'low'. Drawn to illustrate, to no maker's design. */
    K.define("machining_centre", {
      size: [3.3, 3.05, 2.9],
      options: { door: 0, part: "finished", workLight: false, lamp: "off", screen: "off", chips: false, lod: "full", zUp: 0 },
      note: "Vertical machining centre: enclosure, sliding windowed doors, table, vise and part, spindle, tool drum, pendant, stack light, chip cart. Front on +z.",
      make: function (o, rng) {
        var g = new THREE.Group(), full = o.lod !== "low";
        var W = 2.6, H = 2.7, D = 2.35, z0 = D / 2, OW = 1.1, OY0 = 0.95, OY1 = 1.9;
        var Pm = paint(), PP = paintPale(), PL = plinth(), S = steel(), I = iron(), B = black(), R = rubber();
        /* plinth with a kick recess */
        var pl = TXT.roundedBox(W - 0.06, 0.32, D - 0.06, 0.02, PL); pl.position.set(0, 0.16, -0.03); g.add(pl);
        var kick = K.box(W - 0.3, 0.1, 0.02, B, 0, 0.02, z0 - 0.05); g.add(kick);
        /* body: lower block, then the upper shell around the opening */
        var lower = TXT.roundedBox(W, OY0 - 0.32, D, 0.03, Pm); lower.position.set(0, 0.32 + (OY0 - 0.32) / 2, 0); g.add(lower);
        var back = TXT.roundedBox(W, H - OY0, D - 0.64, 0.03, Pm); back.position.set(0, OY0 + (H - OY0) / 2, -0.32); g.add(back);
        var sideW = (W - OW) / 2;
        [-1, 1].forEach(function (s) { var p = TXT.roundedBox(sideW, H - OY0, 0.5, 0.03, Pm); p.position.set(s * (OW / 2 + sideW / 2), OY0 + (H - OY0) / 2, z0 - 0.25); g.add(p); });
        var head = TXT.roundedBox(OW, H - OY1, 0.5, 0.03, Pm); head.position.set(0, OY1 + (H - OY1) / 2, z0 - 0.25); g.add(head);
        /* the pale fascia band and the roof cap, the edges the low key finds */
        var fas = TXT.roundedBox(W + 0.01, 0.12, 0.04, 0.01, PP); fas.position.set(0, H - 0.16, z0 + 0.005); g.add(fas);
        var roof = TXT.roundedBox(W + 0.04, 0.05, D + 0.04, 0.015, Pm); roof.position.set(0, H + 0.02, 0); g.add(roof);
        /* panel seams on the sides, 3 mm dark grooves */
        if (full) [-1, 1].forEach(function (s) { for (var k = 1; k < 4; k++) { var sm = K.box(0.004, H - 0.4, 0.006, B, s * (W / 2 + 0.001), 0.34, -D / 2 + k * D / 4); g.add(sm); } });
        /* the opening: a stainless jamb and a sloped splash lip */
        var jm = S;
        [[OW + 0.08, 0.04, 0, OY1 + 0.02], [OW + 0.08, 0.04, 0, OY0 - 0.02]].forEach(function (b) { var m = TXT.roundedBox(b[0], b[1], 0.06, 0.01, jm); m.position.set(b[2], b[3], z0 + 0.012); g.add(m); });
        [-1, 1].forEach(function (s) { var m = TXT.roundedBox(0.04, OY1 - OY0 + 0.08, 0.06, 0.01, jm); m.position.set(s * (OW / 2 + 0.02), (OY0 + OY1) / 2, z0 + 0.012); g.add(m); });
        /* the inside: a dark stainless envelope */
        var inner = K.mat("mc_inner", { color: 0x08090a, metalness: 0.2, roughness: 0.85 });
        var bk = K.box(OW, OY1 - OY0, 0.02, inner, 0, OY0, z0 - 0.62); g.add(bk);
        [-1, 1].forEach(function (s) { var sd = K.box(0.02, OY1 - OY0, 0.6, inner, s * OW / 2, OY0, z0 - 0.31); g.add(sd); });
        var top = K.box(OW, 0.02, 0.6, inner, 0, OY1 - 0.02, z0 - 0.31); g.add(top);
        var sill = K.box(OW, 0.02, 0.6, inner, 0, OY0 - 0.02, z0 - 0.31); g.add(sill);
        /* the table, its T-slots and way covers, and the vise with the part */
        var tY = OY0 + 0.06;
        var table = TXT.roundedBox(0.9, 0.08, 0.42, 0.006, I); table.position.set(0, tY - 0.04, z0 - 0.33); g.add(table);
        if (full) for (var ts = -2; ts <= 2; ts++) { var slot = K.box(0.9, 0.003, 0.018, B, 0, tY - 0.0015, z0 - 0.33 + ts * 0.08); g.add(slot); }
        if (full) for (var wc = 0; wc < 4; wc++) { var cov = TXT.roundedBox(0.1, 0.012, 0.42, 0.003, S); cov.position.set(-0.5 - wc * 0.012, tY - 0.06 + wc * 0.004, z0 - 0.33); g.add(cov); var cov2 = cov.clone(); cov2.position.x = 0.5 + wc * 0.012; g.add(cov2); }
        if (o.part || full) {
          var vise = K.make("machine_vise", { open: o.part === "raw" ? 0.105 : N.PART.d + 0.015 }); vise.position.set(0, tY, z0 - 0.34); vise.rotation.y = Math.PI / 2; g.add(vise);
          if (o.part) { var part = K.make("housing_part", { state: o.part }); part.position.set(0, tY + 0.09, z0 - 0.34); part.rotation.y = Math.PI / 2; g.add(part); g.userData.part = part; }
        }
        /* the spindle head on its column, a holder and an end mill held clear of the part */
        /* `zUp` retracts the spindle along Z, head, holder and tool together, the way a machine clears the part */
        var zu = o.zUp || 0;
        var col = TXT.roundedBox(0.36, 0.5, 0.36, 0.02, Pm); col.position.set(0, OY1 - 0.2 + zu, z0 - 0.48); g.add(col);
        var hd = TXT.roundedBox(0.3, 0.26, 0.34, 0.02, Pm); hd.position.set(0, OY1 - 0.32 + zu, z0 - 0.36); g.add(hd);
        if (full) { var seamH = K.box(0.302, 0.006, 0.342, B, 0, OY1 - 0.34 + zu, z0 - 0.36); g.add(seamH);
}
        var nose = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.075, 0.06, 32), S); nose.position.set(0, OY1 - 0.48 + zu, z0 - 0.34); g.add(nose);
        var hold = TXT.lathe([[0, 0], [0.045, 0], [0.045, 0.02], [0.03, 0.025], [0.022, 0.07], [0.02, 0.1], [0, 0.1]], S); hold.rotation.x = Math.PI; hold.position.set(0, OY1 - 0.51 + zu, z0 - 0.34); g.add(hold);
        var mill = new THREE.Mesh(new THREE.CylinderGeometry(0.0062, 0.0062, 0.075, 16), carbide()); mill.position.set(0, OY1 - 0.65 + zu, z0 - 0.34); g.add(mill);
        if (full) { var fl2 = K.mat("mc_flute", { color: 0x1b1c1e, metalness: 0.6, roughness: 0.4 });
          for (var fk = 0; fk < 3; fk++) { var hp = []; for (var q2 = 0; q2 <= 24; q2++) { var tq = q2 / 24, an2 = fk * 2.094 + tq * 3.6;
            hp.push([Math.cos(an2) * 0.0062, OY1 - 0.6875 + zu + tq * 0.045, z0 - 0.34 + Math.sin(an2) * 0.0062]); }
            g.add(TXT.tube(hp, 0.0014, fl2)); } }
        if (full) {
          /* two segmented coolant hoses aimed at the tool */
          var hm = hose();
          [-1, 1].forEach(function (s) {
            var pts = []; for (var k = 0; k <= 8; k++) { var t = k / 8; pts.push([s * (0.12 - 0.07 * t), OY1 - 0.4 + zu - 0.18 * t, z0 - 0.28 - 0.04 * Math.sin(t * 3)]); }
            g.add(TXT.tube(pts, 0.009, hm));
            for (var sk = 1; sk < pts.length; sk++) { var ring = new THREE.Mesh(new THREE.TorusGeometry(0.0093, 0.0016, 6, 14), hm); ring.position.set(pts[sk][0], pts[sk][1], pts[sk][2]); ring.rotation.x = Math.PI / 2; g.add(ring); }
            var last = pts[pts.length - 1], noz = new THREE.Mesh(new THREE.CylinderGeometry(0.003, 0.008, 0.022, 12), K.mat("mc_nozzle", { color: 0x2a2c2f, roughness: 0.4 })); noz.position.set(last[0], last[1] - 0.008, last[2]); g.add(noz);
          });
          /* the work light bar in the upper back corner */
          var wl = K.box(0.6, 0.035, 0.04, o.workLight ? K.mat("mc_wl_on", { color: 0x111111, emissive: 0xf1e7d6, emissiveIntensity: 2.2 }) : K.mat("mc_wl_off", { color: 0x2b2d2f, roughness: 0.3 }), -0.2, OY1 - 0.08, z0 - 0.58); g.add(wl);
          if (o.chips) {
            var chipM = K.mat("mc_chip", { color: 0xc8ccd0, metalness: 1, roughness: 0.3 });
            for (var c = 0; c < 60; c++) {
              var cx = (rng() - 0.5) * 0.7, cz = z0 - 0.33 + (rng() - 0.5) * 0.3;
              var curl = new THREE.Mesh(new THREE.TorusGeometry(0.006 + rng() * 0.004, 0.0012, 4, 10, Math.PI * (1 + rng())), chipM);
              curl.position.set(cx, tY + 0.002, cz); curl.rotation.set(Math.PI / 2 + (rng() - 0.5), rng() * 6, 0); g.add(curl);
            }
          }
        }
        /* the doors, two leaves, sliding apart by `door` */
        var leafW = 0.6, leafH = 1.06, slide = o.door * 0.6;
        [-1, 1].forEach(function (s) {
          var lx = s * (leafW / 2 + slide), leaf = new THREE.Group();
          var fr = TXT.roundedBox(leafW, leafH, 0.04, 0.01, Pm); leaf.add(fr);
          var gas = TXT.roundedBox(0.44, 0.59, 0.044, 0.01, R); gas.position.set(0, 0.12, 0); leaf.add(gas);
          var gl = K.box(0.4, 0.55, 0.046, glass(o.workLight), 0, 0.12 - 0.275, 0); leaf.add(gl);
          if (full) for (var sc = 0; sc < 6; sc++) { var scr = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.006, 8), S); scr.rotation.x = Math.PI / 2; scr.position.set(-0.21 + sc * 0.084, 0.42, 0.024); leaf.add(scr); var scr2 = scr.clone(); scr2.position.y = -0.18; leaf.add(scr2); }
          var hdl = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.013, 0.32, 16), S); hdl.position.set(-s * 0.24, -0.15, 0.06); leaf.add(hdl);
          [-0.14, 0.14].forEach(function (dy) { var so = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.05, 10), S); so.rotation.x = Math.PI / 2; so.position.set(-s * 0.24, -0.15 + dy, 0.035); leaf.add(so); });
          leaf.position.set(lx, (OY0 + OY1) / 2 + 0.02, z0 + 0.06); g.add(leaf);
        });
        var rail = TXT.roundedBox(W - 0.2, 0.05, 0.05, 0.01, S); rail.position.set(0, OY1 + 0.1, z0 + 0.06); g.add(rail);
        /* the side tool drum under its hood on -x */
        var hood = TXT.roundedBox(0.3, 0.95, 0.95, 0.03, Pm); hood.position.set(-W / 2 - 0.15, 1.65, -0.2); g.add(hood);
        if (full) { var win = K.box(0.02, 0.36, 0.42, glass(false), -W / 2 - 0.3, 1.5, -0.2); g.add(win); }
        /* the control pendant on a swing arm at the front right */
        var px = W / 2 + 0.18, py = 1.45, pz = z0 + 0.35;
        g.add(TXT.tube([[W / 2 - 0.05, H - 0.4, z0 - 0.1], [W / 2 + 0.12, H - 0.4, z0 + 0.1], [px, H - 0.4, pz - 0.05], [px, py + 0.32, pz - 0.05]], 0.035, Pm));
        var knuck = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.08, 20), PP); knuck.position.set(W / 2 + 0.12, H - 0.4, z0 + 0.1); g.add(knuck);
        var pend = new THREE.Group();
        var ph = TXT.roundedBox(0.46, 0.6, 0.11, 0.025, PP); pend.add(ph);
        var bez = TXT.roundedBox(0.38, 0.25, 0.012, 0.008, B); bez.position.set(0, 0.13, 0.058); pend.add(bez);
        var scrM = o.screen === "on" ? K.mat("mc_scr_on", { color: 0x0a1214, emissive: 0x6d8f98, emissiveIntensity: 0.5, roughness: 0.05 }) :
          K.mat("mc_scr_off", { color: 0x050607, metalness: 0.3, roughness: 0.04 }, false);
        var scr = K.box(0.34, 0.21, 0.004, scrM, 0, 0.13 - 0.105, 0.064); pend.add(scr);
        if (full) {
          var keyM = K.mat("mc_key", { color: 0x2a2c30, roughness: 0.45 }), keyL = K.mat("mc_keyl", { color: 0x8a8e92, roughness: 0.45 });
          for (var r = 0; r < 4; r++) for (var c2 = 0; c2 < 9; c2++) {
            var kk = TXT.roundedBox(0.03, 0.022, 0.012, 0.004, (r === 0 && c2 > 6) ? keyL : keyM); kk.position.set(-0.17 + c2 * 0.042, -0.07 - r * 0.033, 0.06); pend.add(kk);
          }
          var knob = new THREE.Mesh(new THREE.CylinderGeometry(0.024, 0.026, 0.026, 28), B); knob.rotation.x = Math.PI / 2; knob.position.set(0.15, -0.24, 0.067); pend.add(knob);
          var mpg = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.02, 40), S); mpg.rotation.x = Math.PI / 2; mpg.position.set(-0.13, -0.24, 0.064); pend.add(mpg);
        }
        pend.position.set(px, py, pz); pend.rotation.y = -0.35; g.add(pend); g.userData.pendant = pend;
        /* the stack light on the roof's rear right corner */
        var pole = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.2, 10), S); pole.position.set(W / 2 - 0.2, H + 0.14, -D / 2 + 0.2); g.add(pole);
        var lens = [K.mat("mc_lens_g", { color: 0x16301e, roughness: 0.3 }), K.mat("mc_lens_y", { color: 0x3a3214, roughness: 0.3 })];
        for (var sg = 0; sg < 3; sg++) {
          var top3 = sg === 2, lm = top3 ? (o.lamp === "accent" ? N.accentMat(THREE, 1.4) : o.lamp === "warm" ? K.mat("mc_lens_w", { color: 0x332211, emissive: 0xf1e7d6, emissiveIntensity: 1.2 }) : K.mat("mc_lens_off", { color: 0x2c3436, roughness: 0.3 })) : lens[sg];
          var seg = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.06, 24), lm); seg.position.set(W / 2 - 0.2, H + 0.27 + sg * 0.065, -D / 2 + 0.2); g.add(seg);
        }
        var cap = new THREE.Mesh(new THREE.SphereGeometry(0.035, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), PL); cap.position.set(W / 2 - 0.2, H + 0.43, -D / 2 + 0.2); g.add(cap);
        if (full) {
          /* the chip conveyor out of the rear right to a tilt cart, and the coolant tank */
          var cv = TXT.roundedBox(0.4, 0.18, 1.4, 0.02, Pm); cv.position.set(W / 2 - 0.45, 0.85, -D / 2 - 0.45); cv.rotation.x = -0.7; g.add(cv);
          var cart = TXT.roundedBox(0.6, 0.5, 0.6, 0.03, K.mat("mc_cart", { color: 0x2b2e31, metalness: 0.4, roughness: 0.55 })); cart.position.set(W / 2 - 0.45, 0.37, -D / 2 - 0.95); g.add(cart);
          var tank = TXT.roundedBox(1.2, 0.5, 0.4, 0.02, Pm); tank.position.set(-0.4, 0.25, -D / 2 - 0.2); g.add(tank);
        }
        g.userData.opening = { y0: OY0, y1: OY1, w: OW, z: z0 };
        /* the enclosure's centre stays the origin, so a frame can address the door, the vise and the
         * pendant in the model's own coordinates; the drum hood and pendant overhang either side */
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* AN EMPTY MACHINE BAY on the floor, 3.2 x 3.6 m: a glossy epoxy pad 3 mm proud, an outline of
     * 0.10 m floor tape in the accent with corner marks, four steel levelling plates with anchor bolts,
     * a capped conduit stub, and a drop cord hanging from `cordTop` metres to 1.9 m. The cell's bays,
     * drawn as a plan drawn as a plan: what is not there yet. */
    K.define("machine_bay", {
      size: [3.2, 6, 3.6],
      options: { cordTop: 6, tape: "accent" },
      note: "An empty machine bay: epoxy pad, accent tape outline, levelling plates, conduit stub, drop cord. Origin at the pad centre.",
      make: function (o) {
        var g = new THREE.Group(), bw = 3.2, bd = 3.6, tw = 0.1;
        /* the pad's tooth is the kit's concrete map, repeated at its own metres under a satin coat */
        if (!N._padTex) { N._padTex = K.tex("concrete").clone(); var mtr = N._padTex.userData.metres || 3; N._padTex.repeat.set(bw / mtr, bd / mtr); N._padTex.needsUpdate = true; }
        var pad = new THREE.Mesh(new THREE.PlaneGeometry(bw, bd), K.mat("bay_epoxy", { color: 0x4a5158, metalness: 0.05, roughness: 0.16, map: N._padTex }));
        pad.rotation.x = -Math.PI / 2; pad.position.y = 0.003; pad.userData.txWear = false; pad.receiveShadow = true; g.add(pad);
        var TM = o.tape === "accent" ? N.accentMat(THREE, 0.22) : K.mat("bay_tape_w", { color: 0xd8d8d2, roughness: 0.7 });
        /* the tape is a strip with a body: 2 mm proud with a rounded edge, so the low key draws a line along it */
        [[bw, tw, 0, -bd / 2 + tw / 2], [bw, tw, 0, bd / 2 - tw / 2], [tw, bd - 2 * tw, -bw / 2 + tw / 2, 0], [tw, bd - 2 * tw, bw / 2 - tw / 2, 0]].forEach(function (t) {
          var m = TXT.roundedBox(t[0], 0.004, t[1], 0.0018, TM); m.position.set(t[2], 0.005, t[3]); m.userData.txWear = false; g.add(m);
        });
        var S = steel();
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (s) {
          var p = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.015, 24), S); p.position.set(s[0] * (bw / 2 - 0.45), 0.0105, s[1] * (bd / 2 - 0.5)); g.add(p);
          var bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.05, 10), S); bolt.position.set(s[0] * (bw / 2 - 0.45), 0.04, s[1] * (bd / 2 - 0.5)); g.add(bolt);
        });
        var stub = new THREE.Mesh(new THREE.CylinderGeometry(0.027, 0.027, 0.12, 14), K.mat("bay_emt", { color: 0x8a8f93, metalness: 0.85, roughness: 0.35 })); stub.position.set(bw / 2 - 0.3, 0.06, -bd / 2 + 0.35); g.add(stub);
        var cord = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, o.cordTop - 1.9, 8), K.mat("bay_cord", { color: 0x141516, roughness: 0.6 })); cord.position.set(bw / 2 - 0.3, 1.9 + (o.cordTop - 1.9) / 2, -bd / 2 + 0.35); g.add(cord);
        var plug = TXT.roundedBox(0.06, 0.12, 0.06, 0.01, K.mat("bay_plug", { color: 0x2b2b2b, roughness: 0.5 })); plug.position.set(bw / 2 - 0.3, 1.86, -bd / 2 + 0.35); g.add(plug);
        g.userData.keepOrigin = true;
        return g;
      }
    });
  };

  N.instanceModel = function (THREE, model, list) {
    var grp = new THREE.Group(), M = new THREE.Matrix4(), P = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), one = new THREE.Vector3(1, 1, 1), v = new THREE.Vector3();
    model.updateMatrixWorld(true);
    model.traverse(function (m) {
      if (!m.isMesh) return;
      var g = m.geometry.clone(); g.applyMatrix4(m.matrixWorld);
      var im = new THREE.InstancedMesh(g, m.material, list.length);
      list.forEach(function (it, i) { e.set(0, it[3] || 0, 0); q.setFromEuler(e); v.set(it[0], it[1], it[2]); P.compose(v, q, one); im.setMatrixAt(i, P);
        /* an optional per-unit value, so a wall of one model reads as many objects rather than one tiled texture */
        if (it[4] != null) im.setColorAt(i, new THREE.Color(it[4], it[4], it[4])); });
      if (im.instanceColor) im.instanceColor.needsUpdate = true;
      im.instanceMatrix.needsUpdate = true; im.castShadow = true; im.receiveShadow = true; im.frustumCulled = false;
      grp.add(im);
    });
    return grp;
  };

  /* ---- placement and staging, the 2026-10-16 chassis's helpers kept as house furniture ---- */
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
  /* THE KEY is the last light, low and warm, and the world's cool rim is raised a little so a
   * silhouette's shadow side separates from the dark */
  N.rigSpec = function (W, size, map) {
    /* the world's cool rim is held low: at full strength it turned every shadow side of galvanized
     * steel and kit hide bluebonnet blue, the deck's accent, on frames that must carry none (audition
     * review, 2026-10-18) */
    var rim = Object.assign({}, W.rig.rim, { i: (W.rig.rim.i || 0.8) * 0.3, color: 0xb9a48c });
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
  /* the same band from the bottom up, for a frame whose type sits low */
  N.shadeLow = function (cx, o) {
    o = o || {};
    var top = o.from, a = Math.min(0.5, o.a == null ? 0.35 : o.a), fade = o.fade || 200;
    var g = cx.createLinearGradient(0, top - fade, 0, N.H);
    g.addColorStop(0, "rgba(6,5,10,0)"); g.addColorStop(fade / (N.H - top + fade), "rgba(6,5,10," + a + ")"); g.addColorStop(1, "rgba(6,5,10," + a + ")");
    cx.fillStyle = g; cx.fillRect(0, top - fade, N.W, N.H - top + fade);
  };
  /* THE SKY'S OWN LIGHT, held down: the navy dome lights every shadow face blue through the image
   * based light, so a frame calls this after TXT.sky to keep shadows warm dark rather than accent blue */
  N.unacne = function (R, nb) { R.scene.traverse(function (l) { if (l.isDirectionalLight && l.castShadow) { l.shadow.normalBias = nb == null ? 0.04 : nb; l.shadow.bias = -0.0004; } }); return R; };
  N.warm = function (R, k) { R.scene.environmentIntensity = k == null ? 0.3 : k; if (R.scene.environment && R.scene.environmentRotation) {} return R; };
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
  /* A RESERVE under one line of type: a feathered dark patch, darken only. */
  N.knock = function (cx, els, a) {
    /* the patch is drawn as a blurred shadow cast from a rectangle far off canvas, because the canvas
     * filter is not honoured by the renderer and a plain fill prints as a hard box */
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
    u.setAttribute("stroke", "#08060F"); u.setAttribute("stroke-width", "5"); u.setAttribute("stroke-opacity", "0.6"); svg.appendChild(u);
    var l = document.createElementNS("http://www.w3.org/2000/svg", "line");
    l.setAttribute("x1", from[0]); l.setAttribute("y1", from[1]); l.setAttribute("x2", to[0]); l.setAttribute("y2", to[1]);
    l.setAttribute("stroke", N.INK); l.setAttribute("stroke-width", "2"); l.setAttribute("stroke-opacity", "0.85"); svg.appendChild(l);
    var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", to[0]); c.setAttribute("cy", to[1]); c.setAttribute("r", "5"); c.setAttribute("fill", N.INK); svg.appendChild(c);
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#D8CFC0", halo = "rgba(4,3,8,0.6)", halo2 = "rgba(4,3,8,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#08060F; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".hook, .dek, .tx-site, .kick, .src, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D8CFC0" });
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
    var cx = document.getElementById("art").getContext("2d");
    return cx;
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


  /* ---- the relief bench: one material vocabulary for the plan frames ---------------------- */
  /* Linear albedo per material id, with tooth so no surface is a flat fill. The flats stay dark, so under
   * the low el 9 key only the edges turned to it and the specular go bright. The machine shop's own
   * materials: epoxy and slab, a fresh pour, carpet tile, enclosure paint, 6061, foam, the accent tape,
   * steel, granite, the cyanotype sheet and its white line. */
  N.M = { VOID: 0, EPOXY: 1, SLAB: 2, POUR: 3, CARPET: 4, PAINT: 5, ALU: 6, FOAM: 7, TAPE: 8, STEEL: 9, GRANITE: 10, CYAN: 11, INK: 12, FLOOR: 13, LAMP: 14 };
  var BASE = {
    0: [0.004, 0.0045, 0.006],
    1: [0.016, 0.019, 0.021],
    2: [0.10, 0.10, 0.098],
    3: [0.20, 0.20, 0.19],
    4: [0.022, 0.022, 0.026],
    5: [0.11, 0.115, 0.12],
    6: [0.62, 0.64, 0.66],
    7: [0.016, 0.016, 0.018],
    8: [0.27, 0.75, 0.87],
    9: [0.30, 0.31, 0.32],
    10: [0.010, 0.010, 0.011],
    11: [0.016, 0.040, 0.095],
    12: [0.70, 0.76, 0.80],
    13: [0.45, 0.47, 0.50],
    14: [0.022, 0.026, 0.028]
  };
  N.SPEC = { 1: [0.5, 60], 2: [0.06, 8], 3: [0.08, 8], 5: [0.25, 24], 6: [0.9, 34], 7: [0.02, 3], 8: [0.15, 14], 9: [0.6, 30], 10: [0.35, 24], 11: [0.04, 5], 12: [0.05, 6], 13: [0.7, 28], 14: [0.5, 30] };
  N.albedo = function (X, Y, m) {
    var b = BASE[m] || BASE[0], n = global.TX && TX.simplex2 ? TX.simplex2(X * 0.07, Y * 0.07) * 0.5 + TX.simplex2(X * 0.31, Y * 0.31) * 0.25 : 0;
    var k = 1 + ((m === 1 || m === 2 || m === 3 || m === 5) ? 0.03 : 0.14) * n;
    if (m === 10 && global.TX) { var sp = TX.simplex2(X * 1.7, Y * 1.7); k += sp > 0.7 ? 1.6 : 0; }
    if (m === 6 && global.TX) k += 0.08 * TX.simplex2(X * 0.04, Y * 2.2);
    return [b[0] * k, b[1] * k, b[2] * k];
  };

  global.CH = N;
})(this);
