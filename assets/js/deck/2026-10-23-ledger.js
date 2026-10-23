/* deck/2026-10-23-ledger.js — the chassis for the 2026-10-23 deck: UT Southwestern Medical Center reported a study in
 * which language models picked which of two matched emergency patients to see first, and one stigmatizing line added
 * to a record sometimes moved a model away from the patient who later deteriorated (tx-2026-0228).
 *
 * THE VISUAL ARGUMENT. A patient record is a card at ONE measured size, 127 by 203 mm, and the one added line is a
 * strip of ember tape laid on it. Two matched cards stand in a pool of light, three sorting trays put the notched card
 * of the patient who later deteriorated in the front slot, and with the tape laid on, that card drops to the back slot.
 * A corner notch marks the patient who later deteriorated on every card in the deck.
 *
 * THE WORLD. lastLight, the house register and a STAGED world: the sun just down, a near black sky, one low warm key,
 * the still life standing on a dark Eagle Ford shale ledge in a pool of it and the field behind gone dark. A record is
 * read at hand distance under one light, and the dark around it is everything nobody is looking at.
 *
 * THE LIGHT is azimuth 62, elevation 14. +x is east and +z is south, az runs from +z toward +x, so the key sits low in
 * the south east of every subject: a camera on +z looking -z has the key low in front and to its RIGHT, every card face
 * turned toward it is lit, and every cast runs long to the left and away. A material relief reads it from the upper
 * right of its frame, low, and every cast runs down and to the left.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `record_card` (bone card stock with ruled lines, an
 * optional corner notch and an optional ember tape strip, laid flat or peeled), `card_holder` (a graphite steel two
 * slot holder), `sorting_tray` (a stepped two slot graphite steel rack), `wristband` (a closed white vinyl loop with a
 * nickel snap and an ember tab), `card_stack` (a stack of the card with a slid top pair), `card_drawer` (a graphite
 * steel index card drawer with a rod, upright cards, a tabbed divider and a leaning rank behind it) and `shale_ledge`
 * (an Eagle Ford shale slab with laminations). Each is built in the kit's conventions (metres, y up, origin on the
 * ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is dusk ember, #B4664F, and it means ONE thing: the added line.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 * Every frame composes its own picture, and every count a frame draws is read from figures.json in that frame's own
 * code where figure_bearing.py reads it. The chassis types no figure of the story. `N.CARD` is the card's size, the
 * same on every frame, and no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("ledger.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "ledger",
    light: { az: 62, el: 14 },
    sky: "lastLight",
    ground: "#07070C",
    material: "#D8D0BE",
    accent: "#B4664F",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.9, strength: 0.08, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261023 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261023;
  N.ACCENT = 0xb4664f;   /* dusk ember, brand.yaml's, and it means ONE thing: the added line */
  N.INK = "#ECE6DA";
  /* THE DECK'S ONE CARD: width, height and stock thickness in metres, on every card in every frame */
  N.CARD = { w: 0.127, h: 0.203, t: 0.0006 };
  /* the index card the drawer holds is the same stock, cut to 3 by 5 */
  N.INDEX = { w: 0.127, h: 0.076, t: 0.0006 };
  N.LEDGE_Y = 0.62;      /* the shale ledge's top, metres above the ground */

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */
  /* CARD STOCK: bone, with faint ruled lines and a header rule, nothing legible. One texture covers one card face. */
  N.cardTex = function (THREE, ruled) {
    var key = "_cardtex" + (ruled ? 1 : 0);
    if (N[key]) return N[key];
    var S = 512, c = document.createElement("canvas"), b = document.createElement("canvas");
    c.width = b.width = S; c.height = b.height = Math.round(S * N.CARD.h / N.CARD.w);
    var x = c.getContext("2d"), y = b.getContext("2d"), rnd = lcg(7301 + (ruled ? 1 : 0)), H = c.height;
    x.fillStyle = "#cfc6b2"; x.fillRect(0, 0, S, H); y.fillStyle = "#808080"; y.fillRect(0, 0, S, H);
    /* the stock's own tooth: a slow cloud and fine fibre speckle */
    for (var k = 0; k < 24; k++) {
      var gx = rnd() * S, gy = rnd() * H, gr = 30 + rnd() * 120, gg = x.createRadialGradient(gx, gy, 0, gx, gy, gr);
      gg.addColorStop(0, rnd() < 0.5 ? "rgba(120,104,80,0.05)" : "rgba(240,232,214,0.05)"); gg.addColorStop(1, "rgba(0,0,0,0)");
      x.fillStyle = gg; x.fillRect(gx - gr, gy - gr, gr * 2, gr * 2);
    }
    for (var i = 0; i < 9000; i++) {
      var v = rnd(); x.fillStyle = v < 0.5 ? "rgba(90,80,62,0.22)" : "rgba(250,244,230,0.22)";
      var px = rnd() * S, py = rnd() * H; x.fillRect(px, py, 1 + rnd() * 1.4, 1);
      y.fillStyle = v < 0.5 ? "rgba(0,0,0,0.25)" : "rgba(255,255,255,0.25)"; y.fillRect(px, py, 1, 1);
    }
    if (ruled) {
      /* a header band and ruled lines: printed rules a reader recognises as a form, with no words on them */
      x.fillStyle = "rgba(70,74,84,0.55)"; x.fillRect(S * 0.08, H * 0.07, S * 0.84, H * 0.012);
      x.fillStyle = "rgba(70,74,84,0.30)"; x.fillRect(S * 0.08, H * 0.10, S * 0.36, H * 0.03);
      for (var r = 0; r < 11; r++) {
        var ry = H * (0.2 + r * 0.068);
        x.fillStyle = "rgba(70,74,84,0.38)"; x.fillRect(S * 0.08, ry, S * 0.84, 2);
        /* grey stand-ins for handwriting on a few lines, abstract strokes, never letters */
        if (r % 3 !== 2) { x.fillStyle = "rgba(60,62,70,0.22)"; x.fillRect(S * 0.1, ry - 14, S * (0.25 + rnd() * 0.45), 9); }
      }
    }
    var t = new THREE.CanvasTexture(c), bt = new THREE.CanvasTexture(b);
    t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; bt.anisotropy = 8;
    N[key] = { map: t, bump: bt };
    return N[key];
  };
  N.cardMat = function (THREE, ruled) {
    var k = "_cardm" + (ruled ? 1 : 0);
    if (N[k]) return N[k];
    var t = N.cardTex(THREE, ruled);
    N[k] = new THREE.MeshStandardMaterial({ map: t.map, bumpMap: t.bump, bumpScale: 0.4, roughness: 0.86, metalness: 0, side: THREE.DoubleSide });
    return N[k];
  };
  /* the card's edge and back: plain stock, a touch darker */
  N.stockMat = function (THREE) {
    if (N._stock) return N._stock;
    N._stock = new THREE.MeshStandardMaterial({ color: 0xbdb39d, roughness: 0.9, metalness: 0 });
    return N._stock;
  };
  /* EMBER VINYL TAPE. The colour lives in the albedo with a low glow so the hue survives the dusk at feed size, and a
   * clearcoat gives its raised edge a glint (no. 41 read a strong emissive as pink) */
  N.tapeMat = function (THREE) {
    if (N._tape) return N._tape;
    N._tape = new THREE.MeshPhysicalMaterial({ color: 0x9c4a34, roughness: 0.36, metalness: 0, clearcoat: 0.8, clearcoatRoughness: 0.12,
      emissive: N.ACCENT, emissiveIntensity: 0.12, side: THREE.DoubleSide });
    return N._tape;
  };
  /* GRAPHITE STEEL, rough and barely metallic so it never mirrors the navy sky (no. 54's kit metal) */
  N.steelMat = function (THREE) {
    if (N._steel) return N._steel;
    N._steel = new THREE.MeshStandardMaterial({ color: 0x3a3c42, roughness: 0.55, metalness: 0.2 });
    return N._steel;
  };
  N.vinylMat = function (THREE) {
    if (N._vinyl) return N._vinyl;
    N._vinyl = new THREE.MeshStandardMaterial({ color: 0xd9d4c8, roughness: 0.48, metalness: 0, side: THREE.DoubleSide });
    return N._vinyl;
  };
  N.nickelMat = function (THREE) {
    if (N._nickel) return N._nickel;
    N._nickel = new THREE.MeshStandardMaterial({ color: 0x9a9ea3, roughness: 0.35, metalness: 0.6 });
    return N._nickel;
  };
  /* EAGLE FORD SHALE: near black with fine laminations, as a map and a bump map, one tile `metres` across */
  N.shaleTex = function (THREE) {
    if (N._shaletex) return N._shaletex;
    var S = 512, c = document.createElement("canvas"), b = document.createElement("canvas");
    c.width = c.height = b.width = b.height = S;
    var x = c.getContext("2d"), y = b.getContext("2d"), rnd = lcg(5501);
    x.fillStyle = "#2a2b2f"; x.fillRect(0, 0, S, S); y.fillStyle = "#808080"; y.fillRect(0, 0, S, S);
    for (var k = 0; k < 40; k++) {
      var gx = rnd() * S, gy = rnd() * S, gr = 30 + rnd() * 140, gg = x.createRadialGradient(gx, gy, 0, gx, gy, gr);
      gg.addColorStop(0, rnd() < 0.5 ? "rgba(10,10,12,0.35)" : "rgba(70,70,76,0.18)"); gg.addColorStop(1, "rgba(0,0,0,0)");
      x.fillStyle = gg;
      for (var ox = -S; ox <= S; ox += S) for (var oy = -S; oy <= S; oy += S) { x.save(); x.translate(ox, oy); x.fillRect(gx - gr, gy - gr, gr * 2, gr * 2); x.restore(); }
    }
    /* laminations: fine wavering bands across the tile */
    for (var r = 0; r < S; r += 3 + rnd() * 6) {
      var a = 0.05 + rnd() * 0.12, wob = rnd() * 6;
      x.strokeStyle = rnd() < 0.5 ? "rgba(8,8,10," + a + ")" : "rgba(90,90,96," + (a * 0.6) + ")"; x.lineWidth = 1 + rnd() * 1.5;
      x.beginPath(); for (var px = 0; px <= S; px += 16) x.lineTo(px, r + Math.sin(px * 0.02 + wob) * 2); x.stroke();
      y.strokeStyle = "rgba(0,0,0," + (a * 1.5) + ")"; y.beginPath(); for (var qx = 0; qx <= S; qx += 16) y.lineTo(qx, r + Math.sin(qx * 0.02 + wob) * 2); y.stroke();
    }
    for (var i = 0; i < 12000; i++) {
      var v = rnd(), sx = rnd() * S, sy = rnd() * S;
      x.fillStyle = v < 0.5 ? "rgba(0,0,0,0.35)" : "rgba(120,120,128,0.18)"; x.fillRect(sx, sy, 1 + rnd() * 1.5, 1 + rnd());
      y.fillStyle = v < 0.5 ? "rgba(0,0,0,0.35)" : "rgba(255,255,255,0.25)"; y.fillRect(sx, sy, 1, 1);
    }
    var t = new THREE.CanvasTexture(c), bt = new THREE.CanvasTexture(b);
    [t, bt].forEach(function (q) { q.wrapS = q.wrapT = THREE.RepeatWrapping; q.anisotropy = 8; });
    t.colorSpace = THREE.SRGBColorSpace;
    N._shaletex = { map: t, bump: bt };
    return N._shaletex;
  };
  N.shaleMat = function (K) {
    if (N._shale) return N._shale;
    var t = N.shaleTex(K.THREE);
    N._shale = new K.THREE.MeshStandardMaterial({ map: t.map, bumpMap: t.bump, bumpScale: 1.4, roughness: 0.82, metalness: 0 });
    return N._shale;
  };

  /* ---- the models --------------------------------------------------------------------------- */
  /* A card face as a flat shape in the XY plane, origin at its bottom centre, the top right corner cut by `notch`
   * metres when given, with UVs running 0..1 over the full card so the ruled texture lands the same on every card */
  N.cardShape = function (THREE, w, h, notch) {
    var s = new THREE.Shape(), r = 0.003;
    s.moveTo(-w / 2 + r, 0); s.lineTo(w / 2 - r, 0); s.quadraticCurveTo(w / 2, 0, w / 2, r);
    if (notch) { s.lineTo(w / 2, h - notch); s.lineTo(w / 2 - notch, h); }
    else { s.lineTo(w / 2, h - r); s.quadraticCurveTo(w / 2, h, w / 2 - r, h); }
    s.lineTo(-w / 2 + r, h); s.quadraticCurveTo(-w / 2, h, -w / 2, h - r); s.lineTo(-w / 2, r); s.quadraticCurveTo(-w / 2, 0, -w / 2 + r, 0);
    var g = new THREE.ShapeGeometry(s, 6), uv = g.attributes.uv, p = g.attributes.position;
    for (var i = 0; i < uv.count; i++) uv.setXY(i, (p.getX(i) + w / 2) / w, p.getY(i) / h);
    uv.needsUpdate = true;
    return g;
  };
  /* A RIBBON along a polyline in the XZ plane at height y0, `width` tall in y: the tape, flat or peeled */
  N.ribbon = function (THREE, pts, width) {
    var pos = [], idx = [], nrm = [], uvs = [], L = 0;
    for (var i = 0; i < pts.length; i++) {
      if (i) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      var a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
      var tx = b[0] - a[0], tz = b[1] - a[1], tl = Math.hypot(tx, tz) || 1, nx = tz / tl, nz = -tx / tl;
      pos.push(pts[i][0], -width / 2, pts[i][1], pts[i][0], width / 2, pts[i][1]);
      nrm.push(nx, 0, nz, nx, 0, nz); uvs.push(L, 0, L, 1);
      if (i) { var k = i * 2; idx.push(k - 2, k - 1, k, k - 1, k + 1, k); }
    }
    var g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute("normal", new THREE.Float32BufferAttribute(nrm, 3));
    g.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
    g.setIndex(idx);
    return g;
  };

  /* A TAPE STRIP WITH THICKNESS along a polyline in the XZ plane, `width` tall in y and `thick` deep: short rounded
   * segments joined end to end, so the strip has an edge the key can catch and a cast of its own (no. 58's audition
   * read a zero thickness ribbon as a printed bar) */
  N.tapeStrip = function (THREE, TXT, pts, width, thick) {
    var g = new THREE.Group(), mat = N.tapeMat(THREE);
    for (var i = 1; i < pts.length; i++) {
      var a = pts[i - 1], b = pts[i], dx = b[0] - a[0], dz = b[1] - a[1], L = Math.hypot(dx, dz);
      if (L < 1e-5) continue;
      var m = TXT.roundedBox(L + thick * 0.6, width, thick, Math.min(thick * 0.45, 0.0004), mat);
      m.position.set((a[0] + b[0]) / 2, 0, (a[1] + b[1]) / 2); m.rotation.y = -Math.atan2(dz, dx);
      m.castShadow = m.receiveShadow = true; g.add(m);
    }
    return g;
  };

  N.installKit = function (K, THREE, TXT) {
    if (K.registry.record_card) return;

    /* A RECORD CARD standing on its bottom edge, face on +z, origin at its bottom centre. `notch` cuts the top right
     * corner, the mark of the patient who later deteriorated. `tape` lays an ember strip across the face at
     * `tapeAt` of the height; `peel` lifts the strip's left end off in a curl, 0 flat to 1 the whole strip.
     * `index` cuts the card to 3 by 5 for the drawer. userData.tapeY is the strip's height on the card. */
    K.define("record_card", {
      size: [0.127, 0.203, 0.002],
      options: { notch: false, tape: false, tapeAt: 0.52, peel: 0, ruled: true, index: false, flag: null },
      note: "Bone record card stock with printed ruled lines and no legible words, an optional corner notch and an optional ember tape strip, flat or peeled. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), C = o.index ? N.INDEX : N.CARD, w = C.w, h = C.h, t = C.t, notch = o.notch ? (o.index ? 0.014 : 0.022) : 0;
        var geo = N.cardShape(THREE, w, h, notch);
        var front = new THREE.Mesh(geo, N.cardMat(THREE, o.ruled && !o.index)); front.position.z = t / 2; front.castShadow = front.receiveShadow = true; g.add(front);
        var back = new THREE.Mesh(geo, N.stockMat(THREE)); back.rotation.y = Math.PI; back.position.z = -t / 2; back.castShadow = back.receiveShadow = true; g.add(back);
        /* the card's edge, so a card seen end on still has a lit line along its top */
        var top = new THREE.Mesh(new THREE.BoxGeometry(w - (notch ? notch : 0.004), t, t), N.stockMat(THREE));
        top.position.set(-(notch ? notch / 2 : 0), h - t / 2, 0); g.add(top);
        if (o.tape) {
          var tw = o.index ? 0.009 : 0.012, ty = h * o.tapeAt, x0 = -w * 0.43, x1 = w * 0.43, L = x1 - x0, zf = t / 2 + 0.0005;
          var p = Math.max(0, Math.min(1, o.peel || 0)), xs = x0 + L * p, pts = [];
          if (p > 0) {
            /* the peeled end: a free length of tape leaving the card where it is still stuck and arcing out toward the
             * camera and back over the stuck part, so its lit inner face shows and its cast falls on the card */
            var Lf = L * p, Rr = Lf / 1.9, seg = 22;
            for (var k = seg; k >= 1; k--) {
              var a = (k / seg) * 1.9;
              pts.push([xs - Math.sin(a) * Rr, zf + (1 - Math.cos(a)) * Rr]);
            }
          }
          for (var j = 0; j <= 1; j++) pts.push([xs + (x1 - xs) * j, zf]);
          var rib = N.tapeStrip(THREE, TXT, pts, tw, 0.0007); rib.position.y = ty; g.add(rib);
          g.userData.tapeY = ty;
        }
        if (o.flag != null) {
          /* an ember flag folded over the card's top edge, standing above it, at `flag` of the width from the left */
          var fx = -w / 2 + 0.02 + (w - 0.04) * o.flag, fm = N.tapeMat(THREE);
          [-1, 1].forEach(function (sd) { var leg = TXT.roundedBox(0.016, 0.022, 0.0006, 0.0002, fm); leg.position.set(fx, h - 0.004, sd * (t / 2 + 0.0004)); leg.castShadow = true; g.add(leg); });
          var cap = TXT.roundedBox(0.016, 0.0008, t + 0.0016, 0.0003, fm); cap.position.set(fx, h + 0.0072, 0); g.add(cap);
          var up = TXT.roundedBox(0.016, 0.009, 0.0007, 0.0002, fm); up.position.set(fx, h + 0.003, 0); g.add(up);
        }
        g.userData.keepOrigin = true; g.userData.w = w; g.userData.h = h;
        return g;
      }
    });

    /* A TWO SLOT CARD HOLDER in graphite steel, cards standing side by side, each leaning back `lean` degrees.
     * userData.slots gives each slot's x. The cards are added by the frame. */
    K.define("card_holder", {
      size: [0.32, 0.03, 0.075],
      options: { width: 0.32, lean: 6 },
      note: "Graphite steel two slot desk card holder with folded lips. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), st = N.steelMat(THREE), W = o.width;
        var base = TXT.roundedBox(W, 0.014, 0.075, 0.004, st); base.position.y = 0.007; base.castShadow = base.receiveShadow = true; g.add(base);
        [-1, 1].forEach(function (sg) {
          var fr = TXT.roundedBox(W * 0.44, 0.026, 0.006, 0.002, st); fr.position.set(sg * W * 0.23, 0.026, 0.016); fr.castShadow = fr.receiveShadow = true; g.add(fr);
          var bk = TXT.roundedBox(W * 0.44, 0.04, 0.006, 0.002, st); bk.position.set(sg * W * 0.23, 0.033, -0.012); bk.castShadow = bk.receiveShadow = true; g.add(bk);
        });
        g.userData.keepOrigin = true; g.userData.slots = [-W * 0.23, W * 0.23]; g.userData.seat = { y: 0.014, z: 0.002 }; g.userData.lean = o.lean;
        return g;
      }
    });

    /* A STEPPED TWO SLOT SORTING TRAY in graphite steel, front on +z: the front slot low, the back slot on a step.
     * userData.slots.front and .back give each slot's seat {y, z}. */
    K.define("sorting_tray", {
      size: [0.18, 0.07, 0.17],
      options: { width: 0.18 },
      note: "Graphite steel stepped two slot sorting rack with folded lips, front slot low and back slot raised. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), st = N.steelMat(THREE), W = o.width;
        var plate = TXT.roundedBox(W, 0.004, 0.17, 0.0015, st); plate.position.y = 0.002; plate.castShadow = plate.receiveShadow = true; g.add(plate);
        var lipF = TXT.roundedBox(W, 0.03, 0.004, 0.0015, st); lipF.position.set(0, 0.015, 0.083); lipF.castShadow = lipF.receiveShadow = true; g.add(lipF);
        var step = TXT.roundedBox(W, 0.052, 0.09, 0.003, st); step.position.set(0, 0.026, -0.04); step.castShadow = step.receiveShadow = true; g.add(step);
        var lipB = TXT.roundedBox(W, 0.03, 0.004, 0.0015, st); lipB.position.set(0, 0.067, 0.002); lipB.castShadow = lipB.receiveShadow = true; g.add(lipB);
        var back = TXT.roundedBox(W, 0.11, 0.004, 0.0015, st); back.position.set(0, 0.055, -0.083); back.castShadow = back.receiveShadow = true; g.add(back);
        [-1, 1].forEach(function (sg) {
          var side = TXT.roundedBox(0.004, 0.11, 0.17, 0.0015, st); side.position.set(sg * (W / 2 - 0.002), 0.055, 0); side.castShadow = side.receiveShadow = true; g.add(side);
        });
        g.userData.keepOrigin = true;
        g.userData.slots = { front: { y: 0.004, z: 0.058 }, back: { y: 0.052, z: -0.03 } };
        return g;
      }
    });

    /* A CLOSED VINYL WRISTBAND standing on its edge, loop axis along z, a nickel snap at the top and an ember tab. */
    K.define("wristband", {
      size: [0.062, 0.062, 0.025],
      options: { r: 0.03, width: 0.025, tab: true },
      note: "Closed white vinyl patient wristband standing on edge, with a nickel snap and an ember tab. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), r = o.r, wd = o.width;
        var loop = new THREE.Mesh(new THREE.CylinderGeometry(r, r, wd, 48, 1, true), N.vinylMat(THREE));
        loop.rotation.x = Math.PI / 2; loop.position.y = r; loop.castShadow = loop.receiveShadow = true; g.add(loop);
        var inner = new THREE.Mesh(new THREE.CylinderGeometry(r - 0.0012, r - 0.0012, wd, 48, 1, true), N.vinylMat(THREE));
        inner.rotation.x = Math.PI / 2; inner.position.y = r; inner.receiveShadow = true; g.add(inner);
        var snap = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.003, 16), N.nickelMat(THREE));
        snap.position.set(0, 2 * r + 0.0012, 0.004); snap.castShadow = true; g.add(snap);
        if (o.tab) { var tab = TXT.roundedBox(0.014, 0.0016, wd * 0.7, 0.0006, N.tapeMat(THREE)); tab.position.set(-0.012, 2 * r - 0.002, 0); tab.rotation.z = 0.38; tab.castShadow = true; g.add(tab); }
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* A STACK OF THE CARD lying flat, `height` metres of stock, its edges striped as cards, with the top pair slid
     * forward on +z: one notched, one plain. */
    K.define("card_stack", {
      size: [0.13, 0.12, 0.21],
      options: { height: 0.12, slide: 0.04, seed: 1 },
      note: "A stack of record cards lying flat with striped card edges and its top pair slid forward. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), w = N.CARD.w, d = N.CARD.h, hgt = o.height, rnd = lcg(800 + o.seed);
        /* the stack in five slightly offset blocks, so its edge shows the lean of a real pile */
        var blocks = 5, bh = hgt / blocks;
        for (var b = 0; b < blocks; b++) {
          var blk = new THREE.Mesh(new THREE.BoxGeometry(w, bh, d), [N.edgeMat(THREE, 0), N.edgeMat(THREE, 0), N.stockMat(THREE), N.stockMat(THREE), N.edgeMat(THREE, 1), N.edgeMat(THREE, 1)]);
          blk.position.set((rnd() - 0.5) * 0.004, bh * (b + 0.5), (rnd() - 0.5) * 0.004); blk.rotation.y = (rnd() - 0.5) * 0.03;
          blk.castShadow = blk.receiveShadow = true; g.add(blk);
        }
        [[false, -0.006, 0], [true, 0.004, 1]].forEach(function (c) {
          var card = K.make("record_card", { notch: c[0] });
          card.rotation.x = -Math.PI / 2; card.position.set(c[1], hgt + 0.0008 + c[2] * 0.0008, d / 2 + o.slide * (c[2] ? 1 : 0.55)); card.rotation.z = (c[2] ? 0.04 : -0.03);
          g.add(card);
        });
        g.userData.keepOrigin = true; g.userData.top = hgt;
        return g;
      }
    });
    /* card edges seen from the side: fine lines, one per few cards, so a stack reads as paper and not as a block */
    N.edgeMat = function (THREE, k) {
      var key = "_edge" + k;
      if (N[key]) return N[key];
      var S = 256, c = document.createElement("canvas"); c.width = S; c.height = S;
      var x = c.getContext("2d"), rnd = lcg(611 + k);
      x.fillStyle = "#b8ad96"; x.fillRect(0, 0, S, S);
      for (var yy = 0; yy < S; yy += 2) { var v = rnd(); x.fillStyle = v < 0.5 ? "rgba(60,52,40," + (0.25 + rnd() * 0.3) + ")" : "rgba(240,232,214,0.2)"; x.fillRect(0, yy, S, 1); }
      var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1, 6);
      N[key] = new THREE.MeshStandardMaterial({ map: t, roughness: 0.92, metalness: 0 });
      return N[key];
    };

    /* AN INDEX CARD DRAWER in graphite steel, its length along z with the front on +z, holding `cards` upright index
     * cards on a rod, a tabbed divider `rank` cards from the back, and `rank` notched cards behind it carrying ember
     * flags and leaning back `lean` degrees. Every count is the frame's to pass. */
    K.define("card_drawer", {
      size: [0.15, 0.08, 0.46],
      options: { blocks: 10, per: 10, flagged: 1, length: 0.46 },
      note: "Graphite steel index card drawer with a rod, upright 3 by 5 cards in blocks separated by tabbed dividers and dark gaps, the last blocks' cards notched and flagged in ember. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), st = N.steelMat(THREE), Lz = o.length, iw = N.INDEX.w + 0.008, ht = 0.058, wall = 0.0018;
        var bot = TXT.roundedBox(iw + 2 * wall, wall, Lz, 0.001, st); bot.position.y = wall / 2; bot.castShadow = bot.receiveShadow = true; g.add(bot);
        [-1, 1].forEach(function (sg) {
          var sdw = TXT.roundedBox(wall, ht, Lz, 0.001, st); sdw.position.set(sg * (iw / 2 + wall / 2), ht / 2, 0); sdw.castShadow = sdw.receiveShadow = true; g.add(sdw);
          var lip = TXT.roundedBox(wall * 3, wall * 2, Lz, 0.0008, N.nickelMat(THREE)); lip.position.set(sg * (iw / 2 + wall / 2), ht, 0); g.add(lip);
        });
        var fr = TXT.roundedBox(iw + 2 * wall + 0.006, ht + 0.012, 0.004, 0.0015, st); fr.position.set(0, (ht + 0.012) / 2, Lz / 2); fr.castShadow = fr.receiveShadow = true; g.add(fr);
        var bk = TXT.roundedBox(iw + 2 * wall, ht, wall, 0.001, st); bk.position.set(0, ht / 2, -Lz / 2); bk.castShadow = bk.receiveShadow = true; g.add(bk);
        var pull = TXT.roundedBox(0.05, 0.008, 0.012, 0.003, N.nickelMat(THREE)); pull.position.set(0, ht * 0.55, Lz / 2 + 0.008); pull.castShadow = true; g.add(pull);
        var rod = new THREE.Mesh(new THREE.CylinderGeometry(0.0025, 0.0025, Lz, 10), N.nickelMat(THREE)); rod.rotation.x = Math.PI / 2; rod.position.y = 0.012; g.add(rod);
        /* ten blocks from the front: cards at a 2.6 mm pitch, a dark gap and a tabbed divider between blocks */
        var pitch = 0.0026, gapZ = 0.013, blockL = (o.per - 1) * pitch, used = o.blocks * blockL + (o.blocks - 1) * gapZ, z = used / 2, rnd = lcg(4410);
        var plain = o.blocks - o.flagged, n = plain * o.per;
        var im = new THREE.InstancedMesh(new THREE.BoxGeometry(N.INDEX.w, N.INDEX.h, N.INDEX.t), [N.stockMat(THREE), N.stockMat(THREE), N.stockMat(THREE), N.stockMat(THREE), N.cardMat(THREE, false), N.stockMat(THREE)], n);
        var m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), idx = 0;
        g.userData.blocks = [];
        for (var b = 0; b < o.blocks; b++) {
          var zb = z; g.userData.blocks.push(zb - blockL / 2);
          for (var c = 0; c < o.per; c++) {
            var zc = z - c * pitch;
            if (b < plain) {
              e.set(-0.06 + (rnd() - 0.5) * 0.04, (rnd() - 0.5) * 0.02, 0); q.setFromEuler(e);
              m4.compose(new THREE.Vector3((rnd() - 0.5) * 0.0015, N.INDEX.h / 2 + 0.002, zc), q, new THREE.Vector3(1, 1, 1)); im.setMatrixAt(idx++, m4);
            } else {
              var fc = K.make("record_card", { index: true, notch: true, flag: 0.12 + 0.76 * (c / Math.max(1, o.per - 1)) });
              fc.rotation.x = -0.06 + (rnd() - 0.5) * 0.04; fc.position.set((rnd() - 0.5) * 0.0015, 0.002, zc); g.add(fc);
            }
          }
          z -= blockL;
          if (b < o.blocks - 1) {
            /* the divider: steel, a little lower than the cards, with a nickel tab, in the middle of a dark gap */
            var dz = z - gapZ / 2, dv = TXT.roundedBox(N.INDEX.w + 0.004, N.INDEX.h - 0.02, 0.0012, 0.0006, st);
            dv.position.set(0, (N.INDEX.h - 0.02) / 2 + 0.002, dz); dv.castShadow = dv.receiveShadow = true; g.add(dv);
            var tb = TXT.roundedBox(0.026, 0.014, 0.0012, 0.0008, N.nickelMat(THREE)); tb.position.set(-0.045 + (b % 3) * 0.045, N.INDEX.h - 0.012, dz); g.add(tb);
            z -= gapZ;
          }
        }
        im.castShadow = im.receiveShadow = true; g.add(im);
        g.userData.keepOrigin = true; g.userData.height = ht; g.userData.lastBlockZ = z + blockL / 2;
        return g;
      }
    });

    /* AN EAGLE FORD SHALE LEDGE, a dark laminated slab with a top at `height`, its long side along x. */
    K.define("shale_ledge", {
      size: [2.4, 0.62, 1.6],
      options: { width: 2.4, height: 0.62, depth: 1.6 },
      note: "A dark laminated shale slab with sawn faces. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), m = TXT.roundedBox(o.width, o.height, o.depth, 0.012, N.shaleMat(K));
        K.uvBox(m.geometry, 0.5); m.position.y = o.height / 2; m.castShadow = m.receiveShadow = true; g.add(m);
        g.userData.keepOrigin = true; g.userData.top = o.height;
        return g;
      }
    });
  };

  /* ---- placement and staging, the house furniture of the 2026-10-16, 2026-10-21 and 2026-10-22 chassis ---- */
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
    if (!R._bounce) { R._bounce = new N.T.HemisphereLight(0x1c1828, 0x7a5a3c, N.BOUNCE); R.scene.add(R._bounce); }
    return R;
  };
  N.BOUNCE = 1.1;
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
    var ink = N.INK, dek = "#D8CFC0", halo = "rgba(4,3,8,0.6)", halo2 = "rgba(4,3,8,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#07070C; }",
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


  /* ---- the relief bench: one card's face at native size ------------------------------------ */
  /* Linear albedo per material id, with tooth so no surface is a flat fill. The shale stays near black so under the
   * low key only the card in the pool, the tape's raised edge and the debossed rules' lit lips go bright. */
  N.M = { VOID: 0, SHALE: 1, CARD: 2, TAPE: 3, RULE: 4, ROD: 5 };
  var BASE = {
    0: [0.004, 0.004, 0.006],
    1: [0.018, 0.018, 0.021],
    2: [0.40, 0.36, 0.29],      /* bone card stock, held under the pale band so the pool keeps it out of the mid tones */
    3: [0.36, 0.11, 0.06],      /* ember vinyl, linear */
    4: [0.12, 0.12, 0.14],      /* the printed rule in the deboss */
    5: [0.06, 0.06, 0.07]
  };
  N.SPEC = { 2: [0.05, 8], 3: [0.45, 28], 4: [0.03, 6], 5: [0.6, 40], 1: [0.08, 10] };
  N.albedo = function (X, Y, m) {
    var b = BASE[m] || BASE[0], n = global.TX && TX.simplex2 ? TX.simplex2(X * 0.08, Y * 0.08) * 0.5 + TX.simplex2(X * 0.41, Y * 0.41) * 0.3 : 0;
    var k = 1 + (m === 2 ? 0.16 : (m === 1 ? 0.5 : 0.08)) * n;
    if (m === 2 && global.TX) { var f = TX.simplex2(X * 2.3, Y * 2.3); k += f > 0.7 ? 0.08 : (f < -0.7 ? -0.08 : 0); }
    return [b[0] * k, b[1] * k, b[2] * k];
  };

  global.CH = N;
})(this);
