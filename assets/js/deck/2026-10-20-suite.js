/* deck/2026-10-20-suite.js — the chassis for the 2026-10-20 deck: Houston Methodist put four wall
 * cameras in each of the 15 rooms of Walter Tower's cardiothoracic suite, and its study ties them to
 * about 25 more cases a month while saying it can't prove the cameras caused it (tx-2026-0222).
 *
 * THE WORLD. floodlit, a staged world: a black field and one cold key from high on one side, the
 * light an operating room is lit by. Every spatial frame is an INTERIOR built by TXT.interior, dark
 * around the one source, the back wall in shadow. A material relief reads the same declaration from
 * the top of its frame.
 *
 * THE LIGHT is azimuth -40, elevation 40. +x is east and +z is south, az runs from +z toward +x, so
 * the key sits high to the south west of every subject: every lit face is a top or south west face
 * and every cast runs to the north east. A material relief reads it from the top of its frame: the
 * key comes from the upper left, high, and every cast runs down and to the right.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `or_table`, `surgical_light`,
 * `room_camera`, `anesthesia_station`, `back_table`, `service_boom`, `sterile_container` and `turnover_board`. Each is built in the kit's
 * conventions (metres, y up, origin on the ground or at a ceiling point for an anchored model, front
 * on +z) so Phase 17 can queue the lift. Every one is drawn to illustrate and to no maker's design.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way
 * type is seated. Every frame composes its own picture, and the figures a frame draws are written in
 * that frame's own code where figure_bearing.py reads them. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("suite.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "suite",
    light: { az: -40, el: 40 },
    sky: "floodlit",
    ground: "#08060F",
    material: "#C9CCCE",
    accent: "#E0956A",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.94, strength: 0.07, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261020 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261020;
  N.ACCENT = 0xe0956a;   /* dusk gold, brand.yaml's, and it means ONE thing: Walter Tower's estimated added cases */
  N.INK = "#ECE6DA";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  N.accentMat = function (THREE, glow) {
    var k = "_acc" + (glow || 0);
    if (N[k]) return N[k];
    N[k] = new THREE.MeshStandardMaterial({ color: new THREE.Color(N.ACCENT), roughness: 0.35, metalness: 0.1,
      emissive: new THREE.Color(N.ACCENT), emissiveIntensity: glow == null ? 0.35 : glow });
    return N[k];
  };

/* draft of the operating suite kit models, to be folded into the deck chassis */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.or_table) return;
    var steel = function () { return K.mat("or_steel", { color: 0xc9ccce, metalness: 0.85, roughness: 0.32 }); };
    var satin = function () { return K.mat("or_satin", { color: 0xb8bcbf, metalness: 0.7, roughness: 0.45 }); };
    var paint = function (c) { return K.mat("or_paint_" + c.toString(16), { color: c, metalness: 0.05, roughness: 0.55 }); };
    var pad = function () { return K.mat("or_pad", { color: 0x1c1f24, metalness: 0, roughness: 0.62 }); };
    var rubber = function () { return K.mat("or_rubber", { color: 0x141518, metalness: 0, roughness: 0.85 }); };
    var glassM = function () { return K.mat("or_glass", { color: 0x0b0d10, metalness: 0.1, roughness: 0.05 }, true); };

    /* A RIGID STERILIZATION CONTAINER, the box a set of surgical instruments goes to the room in, at true
     * size: 0.28 m wide, 0.15 m high, 0.58 m long, long axis on z, its END on +z. An anodised aluminium
     * body with rounded corners, a ribbed stainless lid with two filter plates, a fold down handle and
     * two latches on each end, a card holder and a tamper lock on the front end. `lock` is steel or gold, and a
     * gold container is anodised dusk gold all over, the way sets are colour coded by their anodised bodies.
     * `detail: 'low'` drops the ribs and filters for a wall of hundreds. Drawn to no maker's design. */
    K.define("sterile_container", {
      size: [0.3, 0.17, 0.62],
      options: { lock: "steel", detail: "full", body: 0x5d6f7c },
      note: "Rigid sterilization container: anodised body, ribbed stainless lid, filters, handles, latches, card holder, tamper lock (steel|gold). End on +z.",
      make: function (o, rng) {
        var g = new THREE.Group(), W = 0.28, Hh = 0.15, L = 0.58, full = o.detail !== "low";
        /* brushed anodised aluminium, so the key lays a specular band along the rounded top edge */
        var bodyM = o.lock === "gold" ? K.mat("cont_body_gold", { color: N.ACCENT, metalness: 0.4, roughness: 0.36, emissive: N.ACCENT, emissiveIntensity: 0.16 }) : K.mat("cont_body_" + o.body.toString(16), { color: o.body, metalness: 0.62, roughness: 0.4 });
        var lidM = K.mat("cont_lid", { color: 0xc4c9cc, metalness: 0.9, roughness: 0.3 });
        var blk = K.mat("cont_black", { color: 0x16181b, metalness: 0.1, roughness: 0.55 });
        var wire = K.mat("cont_wire", { color: 0xb8bdc0, metalness: 0.95, roughness: 0.25 });
        /* the gold container's tag is white moulded plastic so it reads against the anodised body */
        var lockM = o.lock === "gold" ? K.mat("cont_tag_white", { color: 0xe9e5da, roughness: 0.6 }) : K.mat("cont_lockst", { color: 0xaeb3b6, metalness: 0.8, roughness: 0.35 });
        var seg = full ? { segments: 6 } : undefined;
        var body = TXT.roundedBox(W, Hh - 0.022, L, 0.018, bodyM, seg); body.position.set(0, (Hh - 0.022) / 2, 0); g.add(body);
        /* the lid sits flush on a dark gasket line, its own pressed stainless rim */
        var gasket = TXT.roundedBox(W - 0.004, 0.004, L - 0.004, 0.002, blk); gasket.position.set(0, Hh - 0.02, 0); g.add(gasket);
        var lid = TXT.roundedBox(W + 0.002, 0.02, L + 0.002, 0.007, lidM, seg); lid.position.set(0, Hh - 0.008, 0); g.add(lid);
        if (full) {
          for (var r = 0; r < 9; r++) { var rib = TXT.roundedBox(W - 0.05, 0.005, 0.01, 0.0025, lidM); rib.position.set(0, Hh + 0.003, -L / 2 + 0.05 + r * 0.06); g.add(rib); }
          /* two perforated filter retention plates */
          var holeM = K.mat("cont_hole", { color: 0x1a1d20, roughness: 0.8 });
          [-0.14, 0.14].forEach(function (z) {
            var f = new THREE.Mesh(new THREE.CylinderGeometry(0.058, 0.058, 0.008, 40), K.mat("cont_filter", { color: 0xa9b0b4, metalness: 0.75, roughness: 0.42 })); f.position.set(0, Hh + 0.007, z); g.add(f);
            for (var ring = 1; ring <= 3; ring++) { var n = ring * 7; for (var k = 0; k < n; k++) { var an = k / n * Math.PI * 2, rr = ring * 0.014;
              var h = new THREE.Mesh(new THREE.CylinderGeometry(0.0032, 0.0032, 0.002, 8), holeM); h.position.set(Math.cos(an) * rr, Hh + 0.0115, z + Math.sin(an) * rr); g.add(h); } }
          });
        }
        [-1, 1].forEach(function (end) {
          var z = end * (L / 2 + 0.002);
          /* a fold-down wire bail on each short end, hung from two pivot blocks */
          [-0.085, 0.085].forEach(function (x) { var pv = TXT.roundedBox(0.018, 0.022, 0.014, 0.004, lidM); pv.position.set(x, 0.1, z + end * 0.007); g.add(pv);
            g.add(K.bar([x, 0.1, z + end * 0.014], [x * 0.92, 0.052, z + end * 0.02], 0.0032, wire, 8)); });
          g.add(K.bar([-0.078, 0.052, z + end * 0.02], [0.078, 0.052, z + end * 0.02], 0.0035, wire, 8));
          /* two over-centre latches clamping lid to body */
          [-0.1, 0.1].forEach(function (x) { var lt = TXT.roundedBox(0.03, 0.042, 0.008, 0.004, lidM); lt.position.set(x, Hh - 0.03, z + end * 0.004); g.add(lt);
            var lb = TXT.roundedBox(0.022, 0.006, 0.01, 0.002, blk); lb.position.set(x, Hh - 0.05, z + end * 0.006); g.add(lb); });
        });
        /* the card holder, its card ruled with engraved lines */
        var card = TXT.roundedBox(0.075, 0.038, 0.004, 0.002, K.mat("cont_card", { color: 0xd9d6cc, roughness: 0.85 })); card.position.set(-0.03, 0.035, L / 2 + 0.0068); g.add(card);
        if (full) for (var li = 0; li < 3; li++) { var ln = K.box(0.058 - li * 0.012, 0.0022, 0.001, blk, -0.035 + li * 0.006, 0.045 - li * 0.009, L / 2 + 0.0092); g.add(ln); }
        var rim = TXT.roundedBox(0.083, 0.046, 0.003, 0.002, lidM); rim.position.set(-0.03, 0.035, L / 2 + 0.0032); g.add(rim);
        /* the tamper tag, a separate moulded tag hung on a thin loop through the right latch */
        var tg = TXT.roundedBox(0.024, 0.032, 0.004, 0.006, lockM); tg.position.set(0.1, Hh - 0.083, L / 2 + 0.016); tg.rotation.z = 0.12; g.add(tg);
        var loop = new THREE.Mesh(new THREE.TorusGeometry(0.008, 0.0016, 8, 18), lockM); loop.position.set(0.1, Hh - 0.062, L / 2 + 0.014); loop.rotation.y = Math.PI / 2; g.add(loop);
        var lock = tg;
        g.userData.lockMesh = lock;
        return g;
      }
    });

    /* A TURNOVER BOARD: a wall whiteboard 1.5 m by 1.0 m in an aluminium frame with a pen tray, ruled
     * into six lanes, carrying magnetic case blocks in four muted colours and no legible text. Its back
     * sits on the wall at z = 0, the face on +z, origin at the board's centre. */
    K.define("turnover_board", {
      size: [1.54, 1.04, 0.07],
      options: { w: 1.5, h: 1.0, seed: 7, lanes: 6 },
      note: "Wall whiteboard with ruled lanes and magnetic case blocks, no text. Origin at the face centre on the wall plane, face on +z.",
      make: function (o, rng) {
        var g = new THREE.Group(), bw = o.w, bh = o.h;
        var frameM = K.mat("tb_frame", { color: 0xaab0b2, metalness: 0.7, roughness: 0.35 });
        var faceM = K.mat("tb_face", { color: 0xd9dcd8, roughness: 0.18, metalness: 0 });
        var board = TXT.roundedBox(bw, bh, 0.02, 0.008, faceM); board.position.set(0, 0, 0.02); g.add(board);
        [bh / 2, -bh / 2].forEach(function (dy) { var r = TXT.roundedBox(bw + 0.04, 0.025, 0.035, 0.008, frameM); r.position.set(0, dy, 0.025); g.add(r); });
        [-bw / 2, bw / 2].forEach(function (dx) { var r = TXT.roundedBox(0.025, bh + 0.04, 0.035, 0.008, frameM); r.position.set(dx, 0, 0.025); g.add(r); });
        var tray = TXT.roundedBox(bw * 0.8, 0.03, 0.06, 0.01, frameM); tray.position.set(0, -bh / 2 - 0.03, 0.045); g.add(tray);
        var lineM = K.mat("tb_line", { color: 0x3a3f44, roughness: 0.6 });
        for (var k = 1; k < o.lanes; k++) { var l = K.box(bw - 0.08, 0.006, 0.002, lineM, 0, -bh / 2 + k * bh / o.lanes - 0.003, 0.031); g.add(l); }
        var cols = [0x6d8fa3, 0x8a9a8e, 0x9c8a74, 0x6f7f9a], sv = o.seed;
        for (var k2 = 0; k2 < o.lanes - 1; k2++) { var x0 = -bw / 2 + 0.06;
          for (var j = 0; j < 4; j++) { sv = (sv * 1103515245 + 12345) % 2147483648; var w = 0.14 + (sv % 1000) / 1000 * 0.18; if (x0 + w > bw / 2 - 0.05) break;
            var blk = TXT.roundedBox(w, bh / o.lanes - 0.05, 0.012, 0.004, K.mat("tb_blk_" + ((k2 + j) % 4), { color: cols[(k2 + j) % 4], roughness: 0.5 }));
            blk.position.set(x0 + w / 2, -bh / 2 + (k2 + 0.5) * bh / o.lanes + 0.003, 0.04); g.add(blk); x0 += w + 0.05; } }
        /* the back stays on the wall plane, so the kit must not re-centre the footprint */
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* AN OPERATING TABLE at true size: a pedestal column on a wide base, a tabletop of four
     * articulated sections 2.05 m long at a working height of 0.86 m, a black radiolucent pad,
     * stainless side rails and a hand control on its cord. Drawn to illustrate, no maker's design. */
    K.define("or_table", {
      size: [1.5, 1.0, 2.1],
      options: { height: 0.86, tilt: 0, sheet: false, sheetColor: 0xb9c2c4, blanket: 0x3f5f78 },
      note: "Operating table: base, column, four section top, pad, rails, hand control. Front (head) on +z.",
      make: function (o, rng) {
        var g = new THREE.Group(), H = o.height;
        var base = TXT.roundedBox(0.56, 0.12, 0.9, 0.03, paint(0xd9d8d2)); base.position.set(0, 0.06, -0.15); g.add(base);
        var col = TXT.roundedBox(0.3, H - 0.24, 0.42, 0.04, paint(0xd9d8d2)); col.position.set(0, 0.12 + (H - 0.24) / 2, -0.15); g.add(col);
        var bellow = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.08, 24), rubber()); bellow.position.set(0, H - 0.16, -0.15); g.add(bellow);
        var frame = TXT.roundedBox(0.5, 0.06, 2.0, 0.015, satin()); frame.position.set(0, H - 0.09, 0); g.add(frame);
        /* four pad sections with seams, head, back, seat, legs */
        var secs = [[0.86, 0.36], [0.34, 0.62], [-0.18, 0.42], [-0.72, 0.64]];
        secs.forEach(function (s, i) {
          var p = TXT.roundedBox(0.5, 0.075, s[1] - 0.012, 0.03, pad()); p.position.set(0, H - 0.0225, s[0] - 0.02); g.add(p);
        });
        [-1, 1].forEach(function (sx) {
          var rail = TXT.roundedBox(0.012, 0.035, 1.9, 0.004, steel()); rail.position.set(sx * 0.262, H - 0.075, 0); g.add(rail);
          [-0.8, 0, 0.8].forEach(function (z) { var b = K.box(0.03, 0.04, 0.03, satin(), sx * 0.255, H - 0.095, z); g.add(b); });
        });
        if (o.sheet) {
          /* a fitted sheet: a top that follows the four sections and two skirts that hang over the side rails,
           * with soft lengthwise creases so it reads as cloth rather than a plate */
          var sm = K.mat("or_sheet_" + o.sheetColor.toString(16), { color: o.sheetColor, metalness: 0, roughness: 0.93 });
          var tg = new THREE.PlaneGeometry(0.58, 1.98, 24, 60), tp = tg.attributes.position;
          for (var v = 0; v < tp.count; v++) { var x = tp.getX(v), y = tp.getY(v);
            var crease = 0.003 * (1 + Math.sin(y * 9.0 + Math.sin(x * 21) * 1.4)) * (1 - Math.abs(x) / 0.29);
            var drop = Math.max(0, Math.abs(x) - 0.25) * 0.9;
            tp.setZ(v, crease - drop * drop * 2.5); }
          tg.computeVertexNormals();
          var top = new THREE.Mesh(tg, sm); top.rotation.x = -Math.PI / 2; top.position.set(0, H + 0.03, -0.02); g.add(top);
          [-1, 1].forEach(function (sx) {
            var skirt = TXT.roundedBox(0.008, 0.14, 1.9, 0.003, sm); skirt.position.set(sx * 0.292, H - 0.05, -0.02); skirt.rotation.z = sx * 0.06; g.add(skirt); });
          var pil = TXT.roundedBox(0.4, 0.08, 0.3, 0.035, sm); pil.position.set(0, H + 0.06, 0.82); g.add(pil);
          var fold = TXT.roundedBox(0.5, 0.05, 0.22, 0.02, K.mat("or_blanket", { color: o.blanket || 0x3f5f78, roughness: 0.95 })); fold.position.set(0, H + 0.045, -0.82); g.add(fold);
        }
        /* arm boards out from the back section, and a safety strap across the seat */
        [-1, 1].forEach(function (sx) {
          var ab = TXT.roundedBox(0.66, 0.05, 0.15, 0.02, pad()); ab.position.set(sx * 0.58, H - 0.01, 0.42); ab.rotation.y = sx * 0.12; g.add(ab);
          var ac = K.box(0.08, 0.03, 0.06, satin(), sx * 0.27, H - 0.06, 0.42); g.add(ac); });
        var strap = TXT.roundedBox(0.6, 0.012, 0.07, 0.004, K.mat("or_strap", { color: 0x26292d, roughness: 0.8 })); strap.position.set(0, H + 0.03, -0.25); g.add(strap);
        var hc = TXT.roundedBox(0.07, 0.16, 0.03, 0.01, paint(0xe6e4de)); hc.position.set(0.3, H - 0.25, 0.55); hc.rotation.z = 0.15; g.add(hc);
        return g;
      }
    });

    /* A SURGICAL LIGHT on its ceiling mount, anchored at the ceiling: a drop tube, a pivot, two
     * spring arms and two lamp heads 0.68 m across, each a satin white shell holding a ring of
     * LED lens cells and a sterile handle at its centre. The cells glow with `lit`. */
    K.define("surgical_light", {
      size: [2.4, 1.4, 1.2],
      anchor: "base",
      options: { ceiling: 3.05, heads: 2, lit: 1.0, spread: 1.0, drop: 0.45 },
      note: "Ceiling surgical light: drop tube, two arms, two LED heads with handles. Origin at the ceiling point, heads hang below.",
      make: function (o, rng) {
        var g = new THREE.Group(), C = o.ceiling;
        var shellM = paint(0xe9e8e3), armM = paint(0xd6d6d1);
        var cellM = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xf2f6ff).multiplyScalar(0.25 + 2.4 * o.lit), toneMapped: true });
        var ring = new THREE.MeshStandardMaterial({ color: 0x9aa0a6, metalness: 0.6, roughness: 0.3 });
        var cap = TXT.roundedBox(0.34, 0.06, 0.34, 0.02, armM); cap.position.set(0, C - 0.03, 0); g.add(cap);
        var tube = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, o.drop, 20), armM); tube.position.set(0, C - 0.06 - o.drop / 2, 0); g.add(tube);
        var py = C - 0.06 - o.drop;
        var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.12, 24), armM); hub.position.set(0, py, 0); g.add(hub);
        for (var h = 0; h < o.heads; h++) {
          var ang = (h === 0 ? 0.35 : 2.6) , L = 0.85 * o.spread;
          var ax = Math.cos(ang) * L, az = Math.sin(ang) * L;
          var arm = TXT.roundedBox(L, 0.07, 0.09, 0.03, armM); arm.position.set(ax / 2, py - 0.02, az / 2); arm.rotation.y = -ang; g.add(arm);
          var elbow = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.1, 20), armM); elbow.position.set(ax, py - 0.04, az); g.add(elbow);
          var drop2 = TXT.roundedBox(0.06, 0.32, 0.06, 0.02, armM); drop2.position.set(ax, py - 0.24, az); g.add(drop2);
          var yoke = TXT.roundedBox(0.5, 0.05, 0.06, 0.02, armM); yoke.position.set(ax, py - 0.42, az); yoke.rotation.y = -ang; g.add(yoke);
          var head = new THREE.Group();
          var shell = new THREE.Mesh(new THREE.SphereGeometry(0.36, 40, 16, 0, Math.PI * 2, 0, Math.PI * 0.42), shellM);
          shell.scale.set(1, 0.42, 1); head.add(shell);
          var face = new THREE.Mesh(new THREE.CircleGeometry(0.335, 48), ring); face.rotation.x = Math.PI / 2; face.position.y = 0.0; head.add(face);
          /* the LED cells: rings of small lenses on the face */
          var cellG = new THREE.SphereGeometry(0.028, 14, 8, 0, Math.PI * 2, 0, Math.PI / 2);
          var rings = [[0.075, 6], [0.15, 12], [0.225, 18], [0.295, 24]];
          rings.forEach(function (r) { for (var i = 0; i < r[1]; i++) { var a = i / r[1] * Math.PI * 2 + r[0]; var c = new THREE.Mesh(cellG, cellM); c.rotation.x = Math.PI; c.position.set(Math.cos(a) * r[0], -0.002, Math.sin(a) * r[0]); head.add(c); } });
          var handle = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.035, 0.16, 16), paint(0xbfc3c6)); handle.position.y = -0.09; head.add(handle);
          var lip = new THREE.Mesh(new THREE.TorusGeometry(0.345, 0.018, 10, 48), shellM); lip.rotation.x = Math.PI / 2; head.add(lip);
          head.position.set(ax, py - 0.5, az); head.rotation.z = (h === 0 ? 0.28 : -0.22); head.rotation.x = (h === 0 ? -0.12 : 0.18);
          head.userData.lamp = true; g.add(head);
        }
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* A ROOM CAMERA, wall mounted near the ceiling: a short bracket, a pan and tilt yoke and a
     * fixed housing with a coated lens and a small status lamp. One of the four that watch each
     * room. Facing +z (the lens looks along +z, tilted down by `tilt`). Origin at the wall plate. */
    K.define("room_camera", {
      size: [0.16, 0.2, 0.42],
      anchor: "base",
      options: { tilt: 0.45, pan: 0, lamp: 1.0, lampColor: 0xdfe8f2, housing: 0x2a2d31 },
      note: "Wall camera: plate, knuckle arm, rounded housing with a sunshield hood, coated lens in a bezel ringed by IR emitters, a cable gland and cable, a status lamp. Origin at the wall plate centre, lens along +z. `pan` turns the arm and head on the knuckle while the plate stays flush to the wall.",
      make: function (o, rng) {
        var g = new THREE.Group();
        var hm = K.mat("rc_housing_" + o.housing.toString(16), { color: o.housing, metalness: 0.35, roughness: 0.38, clearcoat: 0.5, clearcoatRoughness: 0.25 }, true);
        var pm = K.mat("rc_mount", { color: 0xcfd0cc, metalness: 0.4, roughness: 0.45 });
        var dk = K.mat("rc_dark", { color: 0x0c0d0f, metalness: 0.5, roughness: 0.3 });
        var plate = TXT.roundedBox(0.11, 0.16, 0.018, 0.006, pm); plate.position.set(0, 0, 0.009); g.add(plate);
        [[-0.035, 0.055], [0.035, 0.055], [-0.035, -0.055], [0.035, -0.055]].forEach(function (q) { var sc = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.006, 12), K.mat("rc_screw", { color: 0x8a8d90, metalness: 0.9, roughness: 0.3 })); sc.rotation.x = Math.PI / 2; sc.position.set(q[0], q[1], 0.02); g.add(sc); });
        /* the arm, head, cable and its boss turn together on the plate; the plate stays flush to the wall */
        var panG = new THREE.Group(); panG.rotation.y = o.pan; g.add(panG);
        var arm = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.024, 0.12, 40), pm); arm.rotation.x = Math.PI / 2; arm.position.set(0, 0, 0.078); panG.add(arm);
        var knuckle = new THREE.Mesh(new THREE.SphereGeometry(0.032, 48, 32), pm); knuckle.position.set(0, 0, 0.145); panG.add(knuckle);
        var tiltG = new THREE.Group(); tiltG.position.set(0, 0.012, 0.15); tiltG.rotation.x = o.tilt; panG.add(tiltG);
        /* the housing: a rounded body, a hood that overhangs the front, a bezel ringed by emitters */
        var body = TXT.roundedBox(0.1, 0.09, 0.24, 0.035, hm); body.position.set(0, 0.03, 0.09); tiltG.add(body);
        var hood = TXT.roundedBox(0.124, 0.014, 0.27, 0.006, hm); hood.position.set(0, 0.082, 0.11); tiltG.add(hood);
        [-1, 1].forEach(function (sx) { var cheek = TXT.roundedBox(0.006, 0.03, 0.09, 0.003, hm); cheek.position.set(sx * 0.059, 0.068, 0.2); tiltG.add(cheek); });
        var face = new THREE.Mesh(new THREE.CylinderGeometry(0.042, 0.042, 0.008, 40), dk); face.rotation.x = Math.PI / 2; face.position.set(0, 0.03, 0.212); tiltG.add(face);
        var bezel = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.005, 12, 40), K.mat("rc_bezel", { color: 0x3a3d41, metalness: 0.85, roughness: 0.22 })); bezel.position.set(0, 0.03, 0.217); tiltG.add(bezel);
        var lens = new THREE.Mesh(new THREE.SphereGeometry(0.026, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), K.mat("rc_lens", { color: 0x05070c, metalness: 0.2, roughness: 0.02, clearcoat: 1, clearcoatRoughness: 0.02, iridescence: 0.7, iridescenceIOR: 1.5 }, true));
        lens.rotation.x = Math.PI / 2; lens.position.set(0, 0.03, 0.214); tiltG.add(lens);
        var irm = K.mat("rc_ir", { color: 0x2a1418, metalness: 0.2, roughness: 0.15 });
        for (var i = 0; i < 8; i++) { var a = i / 8 * Math.PI * 2; var ir = new THREE.Mesh(new THREE.SphereGeometry(0.0045, 10, 8), irm); ir.position.set(Math.cos(a) * 0.037, 0.03 + Math.sin(a) * 0.037, 0.214); tiltG.add(ir); }
        var gland = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.014, 0.025, 14), dk); gland.rotation.x = Math.PI / 2; gland.position.set(0, 0.0, -0.035); tiltG.add(gland);
        /* the cable leaves the gland at the housing's rear and drops in a smooth loop to a round boss on the plate */
        var boss = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.015, 0.016, 32), dk); boss.rotation.x = Math.PI / 2; boss.position.set(0.0, -0.05, 0.026); panG.add(boss);
        var cA = new THREE.Vector3(0, 0, -0.047).applyEuler(new THREE.Euler(o.tilt, 0, 0)).add(new THREE.Vector3(0, 0.012, 0.15));
        var cable = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([cA, new THREE.Vector3(0, cA.y - 0.035, cA.z - 0.012), new THREE.Vector3(0, -0.06, 0.07), new THREE.Vector3(0, -0.05, 0.034)]), 48, 0.0055, 24), dk);
        panG.add(cable);
        var lm = new THREE.MeshBasicMaterial({ color: new THREE.Color(o.lampColor).multiplyScalar(0.4 + 2.2 * o.lamp) });
        var lamp = new THREE.Mesh(new THREE.SphereGeometry(0.0045, 10, 8), lm); lamp.position.set(0.034, 0.064, 0.205); tiltG.add(lamp);
        g.userData.keepOrigin = true; g.userData.lens = lens; g.userData.lamp = lamp;
        return g;
      }
    });

    /* AN ANESTHESIA WORKSTATION on casters: a painted cart with drawers, a work shelf, a gas
     * column with flow tubes, two vaporizers, a ventilator bellows in a clear dome, and a monitor
     * on an arm. Front on +z. */
    K.define("anesthesia_station", {
      size: [0.85, 1.9, 0.8],
      options: { screen: 0.9, body: 0xdedcd5 },
      note: "Anesthesia workstation: cart, drawers, shelf, gas column, vaporizers, bellows dome, monitor on an arm.",
      make: function (o, rng) {
        var g = new THREE.Group(), bm = paint(o.body), dk = paint(0x3a3d42);
        var cart = TXT.roundedBox(0.78, 0.82, 0.7, 0.03, bm); cart.position.set(0, 0.12 + 0.41, 0); g.add(cart);
        for (var i = 0; i < 3; i++) { var d = TXT.roundedBox(0.7, 0.2, 0.02, 0.01, paint(0xcfcdc5)); d.position.set(0, 0.24 + i * 0.25, 0.355); g.add(d); var pl = K.box(0.24, 0.02, 0.02, steel(), 0, 0.3 + i * 0.25, 0.37); g.add(pl); }
        [[-0.33, -0.28], [0.33, -0.28], [-0.33, 0.28], [0.33, 0.28]].forEach(function (c) { var w = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.04, 16), rubber()); w.rotation.z = Math.PI / 2; w.position.set(c[0], 0.05, c[1]); g.add(w); var st = K.box(0.04, 0.08, 0.04, satin(), c[0], 0.08, c[1]); g.add(st); });
        var shelf = TXT.roundedBox(0.84, 0.04, 0.6, 0.015, paint(0x2b2e33)); shelf.position.set(0, 0.97, 0.05); g.add(shelf);
        var colm = TXT.roundedBox(0.78, 0.62, 0.32, 0.03, bm); colm.position.set(0, 1.3, -0.17); g.add(colm);
        for (var t = 0; t < 4; t++) { var tb = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.26, 12), glassM()); tb.position.set(-0.28 + t * 0.05, 1.33, -0.0); g.add(tb); var fl = new THREE.Mesh(new THREE.SphereGeometry(0.012, 8, 6), steel()); fl.position.set(-0.28 + t * 0.05, 1.26 + rng() * 0.1, 0.0); g.add(fl); }
        [0.1, 0.27].forEach(function (x, j) { var v = TXT.roundedBox(0.12, 0.24, 0.13, 0.02, paint(j ? 0xd8b04a : 0x6a4f8f)); v.position.set(x, 1.12, 0.02); g.add(v); });
        var dome = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.28, 24, 1, true), K.mat("or_dome", { color: 0xcfe0e6, metalness: 0, roughness: 0.08, transmission: 0.6, transparent: true, opacity: 0.5 }, true));
        dome.position.set(0.36, 1.1, 0.24); g.add(dome);
        var arm = TXT.roundedBox(0.05, 0.05, 0.4, 0.015, dk); arm.position.set(0, 1.68, 0.02); g.add(arm);
        var mon = TXT.roundedBox(0.5, 0.36, 0.06, 0.02, dk); mon.position.set(0, 1.74, 0.24); mon.rotation.x = -0.12; g.add(mon);
        var scr = new THREE.Mesh(new THREE.PlaneGeometry(0.44, 0.3), new THREE.MeshBasicMaterial({ color: new THREE.Color(0x10331f).multiplyScalar(1 + o.screen) }));
        scr.position.set(0, 1.74, 0.272); scr.rotation.x = -0.12; g.add(scr);
        return g;
      }
    });

    /* AN INSTRUMENT BACK TABLE: a stainless table 1.5 by 0.75 m at 0.9 m, with an undershelf.
     * `draped` covers it in a sterile wrap and lays instrument trays on it. */
    K.define("back_table", {
      size: [1.5, 0.95, 0.75],
      options: { draped: false, drape: 0x4f7e8c },
      note: "Stainless back table with undershelf, optionally draped with trays.",
      make: function (o, rng) {
        var g = new THREE.Group();
        var top = TXT.roundedBox(1.5, 0.03, 0.75, 0.01, steel()); top.position.set(0, 0.885, 0); g.add(top);
        var sh = TXT.roundedBox(1.42, 0.02, 0.67, 0.008, satin()); sh.position.set(0, 0.25, 0); g.add(sh);
        [[-0.71, -0.33], [0.71, -0.33], [-0.71, 0.33], [0.71, 0.33]].forEach(function (c) { var l = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.84, 12), steel()); l.position.set(c[0], 0.45, c[1]); g.add(l); var w = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.03, 14), rubber()); w.rotation.z = Math.PI / 2; w.position.set(c[0], 0.035, c[1]); g.add(w); });
        if (o.draped) {
          var dm = K.mat("or_drape_" + o.drape.toString(16), { color: o.drape, metalness: 0, roughness: 0.92 });
          var dr = TXT.roundedBox(1.56, 0.01, 0.8, 0.004, dm); dr.position.set(0, 0.905, 0); g.add(dr);
          var sk = TXT.roundedBox(1.56, 0.32, 0.01, 0.004, dm); sk.position.set(0, 0.75, 0.4); g.add(sk);
          for (var i = 0; i < 3; i++) { var tr = TXT.roundedBox(0.42, 0.05, 0.3, 0.01, steel()); tr.position.set(-0.5 + i * 0.5, 0.935, -0.05 + (i % 2) * 0.1); g.add(tr); }
        }
        return g;
      }
    });

    /* A CEILING SERVICE BOOM: a column from the ceiling with two shelves, gas outlets and a
     * monitor. Anchored at the ceiling point. */
    K.define("service_boom", {
      size: [1.0, 1.9, 0.6],
      anchor: "base",
      options: { ceiling: 3.05, reach: 0.9, screen: 0.8 },
      note: "Ceiling equipment boom: arm, column, shelves, outlets, a monitor. Origin at the ceiling point.",
      make: function (o, rng) {
        var g = new THREE.Group(), C = o.ceiling, m = paint(0xd4d3cd), dk = paint(0x2f3236);
        var cap = TXT.roundedBox(0.3, 0.06, 0.3, 0.02, m); cap.position.set(0, C - 0.03, 0); g.add(cap);
        var arm = TXT.roundedBox(o.reach, 0.12, 0.16, 0.03, m); arm.position.set(o.reach / 2, C - 0.18, 0); g.add(arm);
        var col = TXT.roundedBox(0.3, 1.2, 0.26, 0.03, m); col.position.set(o.reach, C - 0.24 - 0.6, 0); g.add(col);
        [C - 1.0, C - 1.38].forEach(function (y) { var s = TXT.roundedBox(0.6, 0.03, 0.45, 0.01, satin()); s.position.set(o.reach, y, 0.05); g.add(s); });
        for (var i = 0; i < 6; i++) { var out = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.02, 12), paint([0x2a7a3a, 0x2c4f9a, 0xe7e5e0][i % 3])); out.rotation.x = Math.PI / 2; out.position.set(o.reach - 0.09 + (i % 3) * 0.09, C - 0.5 - Math.floor(i / 3) * 0.09, 0.14); g.add(out); }
        var mon = TXT.roundedBox(0.56, 0.36, 0.05, 0.02, dk); mon.position.set(o.reach, C - 0.82, 0.2); g.add(mon);
        var scr = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.3), new THREE.MeshBasicMaterial({ color: new THREE.Color(0x0f2236).multiplyScalar(1 + o.screen) }));
        scr.position.set(o.reach, C - 0.82, 0.226); g.add(scr);
        g.userData.keepOrigin = true;
        return g;
      }
    });
  };

  /* GLAZED WALL TILE, the surface of an operating room wall: 0.15 m square surgical green glazed tiles with
   * pale grout, each tile a slightly different glaze, so the cold key leaves a glint on some and not others.
   * A canvas map in metres and a roughness map that keeps the grout matte. */
  N.tileTex = function (THREE) {
    if (N._tile) return N._tile;
    var n = 1024, c = document.createElement("canvas"); c.width = c.height = n; var x = c.getContext("2d");
    var rc = document.createElement("canvas"); rc.width = rc.height = n; var rx = rc.getContext("2d");
    var t = n / 8, r = lcg(31);
    x.fillStyle = "#5c6560"; x.fillRect(0, 0, n, n); rx.fillStyle = "#e6e6e6"; rx.fillRect(0, 0, n, n);
    for (var j = 0; j < 8; j++) for (var i = 0; i < 8; i++) {
      var k = 0.88 + r() * 0.2, g = Math.round(84 * k), gg = Math.round(112 * k), b = Math.round(104 * k);
      x.fillStyle = "rgb(" + g + "," + gg + "," + b + ")"; x.fillRect(i * t + 2, j * t + 2, t - 4, t - 4);
      var gl = Math.round(40 + r() * 50); rx.fillStyle = "rgb(" + gl + "," + gl + "," + gl + ")"; rx.fillRect(i * t + 3, j * t + 3, t - 6, t - 6);
    }
    var map = new THREE.CanvasTexture(c); map.colorSpace = THREE.SRGBColorSpace; map.wrapS = map.wrapT = THREE.RepeatWrapping; map.anisotropy = 8;
    var rough = new THREE.CanvasTexture(rc); rough.wrapS = rough.wrapT = THREE.RepeatWrapping;
    N._tile = { map: map, rough: rough, metres: 1.2 };
    return N._tile;
  };
  /* a tiled panel standing on the floor against a wall: centre x, z, width, height, yaw (0 faces +z) */
  N.tileWall = function (THREE, R, o) {
    var T = N.tileTex(THREE), mapA = T.map.clone(), roughA = T.rough.clone();
    [mapA, roughA].forEach(function (m) { m.needsUpdate = true; m.repeat.set(o.w / T.metres, o.h / T.metres); });
    var mat = new THREE.MeshStandardMaterial({ color: o.tint || 0x6f7f79, map: mapA, roughnessMap: roughA, roughness: 1, metalness: 0 });
    var m = new THREE.Mesh(new THREE.PlaneGeometry(o.w, o.h), mat);
    m.position.set(o.x, o.h / 2 + (o.y || 0), o.z); m.rotation.y = o.yaw || 0; m.receiveShadow = true; m.userData.txWear = false;
    R.scene.add(m); return m;
  };

  /* A BOUFFANT SCRUB CAP on a kit person, found at the top of the head: the meshes whose tops reach within
   * 4 cm of the figure's crown are the head and hair, and the cap is a gathered dome over them in the scrubs' cloth. */
  N.scrubCap = function (THREE, person, color) {
    person.updateMatrixWorld(true);
    var all = new THREE.Box3().setFromObject(person), top = all.max.y, head = new THREE.Box3(), any = false;
    person.traverse(function (m) { if (!m.isMesh) return; var b = new THREE.Box3().setFromObject(m); if (b.max.y > top - 0.04 && b.max.y - b.min.y < 0.5) { head.union(b); any = true; } });
    if (!any) return null;
    var c = head.getCenter(new THREE.Vector3()), sz = head.getSize(new THREE.Vector3());
    var g = new THREE.SphereGeometry(1, 40, 24, 0, Math.PI * 2, 0, Math.PI * 0.62), pos = g.attributes.position;
    for (var i = 0; i < pos.count; i++) { var y = pos.getY(i), a = Math.atan2(pos.getZ(i), pos.getX(i)); var k = 1 + 0.035 * Math.sin(a * 11) * (1 - y); pos.setXYZ(i, pos.getX(i) * k, y, pos.getZ(i) * k); }
    g.computeVertexNormals();
    var cap = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: color || 0x5d8aa0, roughness: 0.95 }));
    var r = 0.118;
    var inv = new THREE.Matrix4().copy(person.matrixWorld).invert();
    var local = new THREE.Vector3(c.x, top - r * 0.62, c.z).applyMatrix4(inv);
    cap.position.copy(local); cap.scale.set(r, r * 0.9, r); cap.castShadow = true; person.add(cap);
    return cap;
  };

  /* AN INSTANCED COPY OF ONE KIT MODEL, for a wall of hundreds: every mesh in the baked model becomes one
   * InstancedMesh carrying its own local transform, placed at each [x, y, z, yaw] of `list`. Returns a
   * Group, so TXT.add, TXT.contact and TXT.stage take it like any model. */
  /* a wall camera with its plate flush on a wall whose face looks along wallYaw, its head panned to look at a point */
  N.wallCamera = function (K, at, wallYaw, look, o) {
    var want = Math.atan2(look[0] - at[0], look[2] - at[2]), pan = want - wallYaw;
    pan = Math.atan2(Math.sin(pan), Math.cos(pan));
    var c = K.make('room_camera', Object.assign({}, o || {}, { pan: pan }));
    c.position.set(at[0], at[1], at[2]); c.rotation.y = wallYaw; return c;
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
  /* Linear albedo per material id, with tooth so no surface is a flat fill. The flats stay dark, so under the
   * el 40 key only the faces turned to it and the specular go bright. The operating suite's own materials. */
  N.M = { VOID: 0, VINYL: 1, TAPE: 2, STEEL: 3, GOLD: 4, RUBBER: 5, TOWEL: 6, PAPER: 7, CARD: 8, GLOSS: 9, BRUSHED: 10 };
  var BASE = {
    0: [0.004, 0.0045, 0.006],
    1: [0.018, 0.022, 0.021],
    2: [0.30, 0.30, 0.27],
    3: [0.36, 0.38, 0.39],
    4: [0.88, 0.32, 0.12],
    5: [0.020, 0.020, 0.024],
    6: [0.012, 0.030, 0.028],
    7: [0.50, 0.49, 0.45],
    8: [0.16, 0.165, 0.16],
    9: [0.012, 0.013, 0.016],
    10: [0.22, 0.23, 0.235]
  };
  N.SPEC = { 2: [0.08, 8], 3: [0.75, 70], 4: [0.55, 40], 5: [0.1, 10], 6: [0.02, 4], 7: [0.04, 6], 8: [0.06, 8], 9: [0.7, 80], 10: [0.45, 30], 1: [0.12, 18] };
  N.albedo = function (X, Y, m) {
    var b = BASE[m] || BASE[0], n = global.TX && TX.simplex2 ? TX.simplex2(X * 0.07, Y * 0.07) * 0.5 + TX.simplex2(X * 0.31, Y * 0.31) * 0.25 : 0;
    var k = 1 + 0.14 * n;
    if (m === 1) { var sp = global.TX && TX.simplex2 ? TX.simplex2(X * 1.3, Y * 1.3) : 0; k += sp > 0.62 ? 0.45 : sp < -0.6 ? -0.2 : 0; }
    return [b[0] * k, b[1] * k, b[2] * k];
  };

  global.CH = N;
})(this);
