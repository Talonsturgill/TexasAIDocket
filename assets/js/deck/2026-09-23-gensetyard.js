/* deck/2026-09-23-gensetyard.js — the chassis for carousel no. 32, REBUILT as a render.
 *
 * THE PRINT SCREEN IS DELETED (owner, 2026-09-23): "delete that fallback bullshit look, make it
 * impossible for me to have to tell u this again." The first build of this deck pushed all nine
 * frames through a line screen at cell 6, which is the faded look, and this file carried the
 * screen as house furniture. It carries none now. Every frame RENDERS the same object through
 * the GPU bench, `txthree.js`, under one rig whose key is read from the declaration below.
 *
 * THE HERO OBJECT. One containerised reciprocating natural gas generator set on its skid, in
 * metres: a 12.2 m enclosure, 2.9 m tall and 2.44 m deep, a louvred radiator end, a roof cooler,
 * a silencer and an exhaust stack, four access doors. It is the thing c16 and c17 describe, forty
 * of them behind a meter in West Texas, and it is modelled ONCE here so every frame shows the same
 * machine from a new camera or in a new state. That is the continuity device, and it is stronger
 * than any texture, because a reader recognises a thing before they recognise a surface.
 *
 * WHAT THIS FILE IS NOT. A frame. It builds the object, holds the palette and the rig, and exposes
 * small primitives. Each frame sets up its own renderer, camera, ground and light call, in its own
 * source, because that is where depth_floor reads staging and where the owner reads the work.
 *
 * NO PER UNIT RATING, anywhere. 76 MW over about 40 units is a division no document performs, so
 * nothing about this model's size claims an output.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("gensetyard.js needs txdeck.js loaded first");

  /* ONE DECLARATION. The light is a direction in the WORLD, read by TXT.deckRig on every frame,
   * so nine cameras see one lamp. az is clockwise from +Z toward +X, el is above the pad. */
  TXDECK.declare({
    world: "gensetyard",
    light: { az: -105, el: 27 },
    ground: "#0D1117",
    material: "#C9C4B6",
    accent: "#E0A33F",
    grade: {
      exposure: 0.02,
      saturation: 1.05,
      contrast: 1.10,
      filmic: true,
      /* shadows toward a cool night, highlights toward the sodium lamp. A render needs a grade,
       * never a screen: grain on a solid reads as film, a screen over it reads as the faded look */
      lift: [0.010, 0.012, 0.020],
      gain: [1.030, 1.004, 0.972],
      vignette: 0.20,
      bloom: { threshold: 0.82, strength: 0.16, radius: 10 },
      grain: { amount: 0.016, size: 2, seed: 20260923 },
      aberration: 0,
      dither: true,
      sharpen: 0.22
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20260923;

  /* The night the machine stands in. The DOM body background matches SKY so a frame's edges and
   * its type never sit on a colour the render did not make. */
  N.SKY_HEX = "#0D1117";
  N.SKY = 0x0d1117;
  N.ZENITH = 0x06080d;       /* the top of the dome, where the hook sits */
  N.HORIZON = 0x2a3345;      /* the glow at the edge of the pad, cool, never grey */
  N.FOG = 0x222a39;          /* fog is the horizon's own hue (DESIGN_DOCTRINE 4) */
  N.PAD = 0x4a443b;          /* caliche at night: warm, rough, dark */
  N.CONCRETE = 0x64625d;     /* the slab each set stands on */
  N.ACCENT = "#E0A33F";      /* the posted notice amber. THE STATE'S PAPER wears it, never a machine */

  /* THE RIG. Colour and intensity only: the key's DIRECTION comes from the declaration above
   * through TXT.deckRig, so no frame can hold a second copy of the light. A sodium discharge lamp
   * key, a cool sky rim, a low fill so the shadow side is dark but never black. */
  N.RIG = {
    key:  { color: 0xffe2c2, i: 2.5, radius: 4, shadowSize: 30 },
    rim:  { color: 0x8fb0e0, i: 1.5, pos: [8, 6, -14] },
    fill: { color: 0x40506e, i: 1.6, pos: [6, 3, 11] },
    ambient: { color: 0x1c2433, i: 1.0 }
  };

  /* The materials, made once per frame from the frame's own THREE. Painted steel for the box,
   * because industrial gensets ship painted, galvanised for the stack and silencer, dark steel for
   * the skid and louvres. */
  N.mats = function (TXT) {
    if (!TXT || !TXT.mat) throw new Error("YARD.mats takes the bench, TXT, so every surface is a TXT.mat material");
    var S = function (c, m, r) { return TXT.mat.clay(c, { metalness: m, roughness: r }); };
    return {
      paint:   S(0xc3c4c0, 0.12, 0.48),
      paintDk: S(0x9fa19e, 0.12, 0.55),
      door:    S(0xa8a9a5, 0.12, 0.40),
      skid:    S(0x2a2c30, 0.55, 0.50),
      louvre:  S(0x7a7d83, 0.30, 0.48),
      recess:  S(0x0c0d0f, 0.20, 0.90),
      galv:    S(0xb4b9bc, 0.72, 0.36),
      conc:    S(N.CONCRETE, 0.0, 0.90),
      seat:    S(0x2f3238, 0.05, 0.62),
      iron:    S(0x3f4448, 0.45, 0.55),
      handle:  S(0x1b1c1f, 0.6, 0.4)
    };
  };

  function box(THREE, w, h, d, mat, x, y, z) {
    var m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x || 0, y || 0, z || 0);
    return m;
  }

  /* THE HERO. Origin on the ground at the centre of the slab, long axis along X, the door side
   * facing +Z. o.lamp adds the one amber status lamp by the first door, and only frames that are
   * allowed the accent may ask for it. o.detail false drops the small parts for the far sets on a
   * frame that renders forty of them. */
  N.genset = function (THREE, M, o) {
    o = o || {};
    if (!M || !M.paint) throw new Error("YARD.genset(THREE, YARD.mats(TXT), opts)");
    var g = new THREE.Group();
    var detail = o.detail !== false;
    var L = 12.2, H = 2.9, D = 2.44, SK = 0.32, SLAB = 0.12;
    var base = SLAB + SK;

    g.add(box(THREE, L + 1.2, SLAB, D + 1.0, M.conc, 0, SLAB / 2, 0));            /* the slab */
    g.add(box(THREE, L + 0.4, SK, D + 0.26, M.skid, 0, SLAB + SK / 2, 0));        /* the skid */
    if (o.open) {
      /* THE BOX OPENED ON ITS DOOR SIDE: roof, back, both ends and the door side's two end bays,
       * with the middle 7.4 m standing open so the engine is seen. The doors are left off. */
      g.add(box(THREE, L, 0.06, D, M.paint, 0, base + H - 0.03, 0));
      g.add(box(THREE, L, H, 0.06, M.paint, 0, base + H / 2, -D / 2 + 0.03));
      g.add(box(THREE, 0.06, H, D, M.paint, -L / 2 + 0.03, base + H / 2, 0));
      g.add(box(THREE, 0.06, H, D, M.paint, L / 2 - 0.03, base + H / 2, 0));
      g.add(box(THREE, 2.4, H, 0.06, M.paint, -L / 2 + 1.2, base + H / 2, D / 2 - 0.03));
      g.add(box(THREE, 2.4, H, 0.06, M.paint, L / 2 - 1.2, base + H / 2, D / 2 - 0.03));
      g.add(box(THREE, L, 0.04, D, M.recess, 0, base + 0.02, 0));
      var eng = N.engine(THREE, M);
      eng.position.set(-0.4, base + 0.04, 0);
      g.add(eng);
    } else {
      g.add(box(THREE, L, H, D, M.paint, 0, base + H / 2, 0));                    /* the box */
    }
    g.add(box(THREE, L + 0.1, 0.07, D + 0.1, M.paintDk, 0, base + H + 0.035, 0)); /* drip edge */

    if (detail) {
      /* corner castings, so it reads as a made container and not a block */
      for (var cx = -1; cx <= 1; cx += 2) for (var cy = 0; cy <= 1; cy++) for (var cz = -1; cz <= 1; cz += 2) {
        g.add(box(THREE, 0.2, 0.18, 0.2, M.skid, cx * (L / 2 - 0.08), base + (cy ? H - 0.09 : 0.09), cz * (D / 2 - 0.08)));
      }
      /* the ribs every 1.22 m on both long faces: the light rakes across them and the form turns */
      for (var r = -4; r <= 4; r++) {
        var rx = r * 1.22;
        if (!o.open || Math.abs(rx) > 3.7) g.add(box(THREE, 0.07, H - 0.3, 0.05, M.paintDk, rx, base + H / 2, D / 2 + 0.025));
        g.add(box(THREE, 0.07, H - 0.3, 0.05, M.paintDk, rx, base + H / 2, -D / 2 - 0.025));
      }
      /* four access doors on the +Z face, each inset with a handle, unless the side is open */
      (o.open ? [] : [-4.25, -1.8, 0.65]).forEach(function (dx) {
        g.add(box(THREE, 1.12, 2.15, 0.035, M.door, dx, base + 0.22 + 1.075, D / 2 + 0.02));
        g.add(box(THREE, 0.05, 0.26, 0.06, M.handle, dx + 0.42, base + 1.25, D / 2 + 0.05));
      });
      /* the radiator end: a dark recess behind fourteen raked slats */
      g.add(box(THREE, 0.03, H - 0.5, D - 0.36, M.recess, L / 2 + 0.01, base + H / 2, 0));
      for (var s = 0; s < 14; s++) {
        var sl = box(THREE, 0.05, 0.13, D - 0.4, M.louvre, L / 2 + 0.05, base + 0.36 + s * 0.158, 0);
        sl.rotation.z = -0.6;
        g.add(sl);
      }
      /* an intake louvre panel on the door face near the radiator end */
      g.add(box(THREE, 1.6, 1.5, 0.03, M.recess, 4.4, base + 1.7, D / 2 + 0.018));
      for (var i = 0; i < 9; i++) {
        g.add(box(THREE, 1.5, 0.05, 0.07, M.louvre, 4.4, base + 1.05 + i * 0.16, D / 2 + 0.045));
      }
    }

    /* the roof cooler at the radiator end, with its fan grille */
    var roof = base + H + 0.07;
    g.add(box(THREE, 2.7, 0.85, D - 0.2, M.paint, 4.5, roof + 0.425, 0));
    if (detail) {
      g.add(box(THREE, 2.5, 0.03, D - 0.4, M.recess, 4.5, roof + 0.86, 0));
      for (var f = 0; f < 11; f++) g.add(box(THREE, 2.5, 0.05, 0.05, M.louvre, 4.5, roof + 0.885, -0.95 + f * 0.19));
    }

    /* the silencer, lying along the roof, and the exhaust stack rising out of it */
    var sil = new THREE.Mesh(new THREE.CylinderGeometry(0.44, 0.44, 2.6, 32), M.galv);
    sil.rotation.z = Math.PI / 2;
    sil.position.set(-2.8, roof + 0.62, 0);
    g.add(sil);
    [-3.8, -1.8].forEach(function (px) { g.add(box(THREE, 0.14, 0.4, 0.9, M.skid, px, roof + 0.2, 0)); });
    var stackH = o.stackH || 3.2;
    var stack = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.27, stackH, 28), M.galv);
    stack.position.set(-1.6, roof + 0.62 + stackH / 2, 0);
    g.add(stack);
    var cap = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.30, 0.07, 28), M.galv);
    cap.position.set(-1.6, roof + 0.62 + stackH + 0.06, 0);
    g.add(cap);

    if (o.lamp) {
      var lamp = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 0.05),
        new THREE.MeshStandardMaterial({ color: 0x1a0f05, emissive: 0xe0a33f, emissiveIntensity: 3.2 }));
      lamp.position.set(-5.2, base + 2.45, D / 2 + 0.05);
      g.add(lamp);
    }
    g.userData = { length: L, height: base + H, top: roof + 0.62 + stackH + 0.1, depth: D };
    return g;
  };

  /* A PERSON, 1.70 m, for scale. Coveralls and a white hard hat. Built from capsules so it has a
   * body rather than a silhouette, and lit by the same lamp as the machine it stands beside. */
  N.person = function (THREE, o) {
    o = o || {};
    var g = new THREE.Group();
    var cloth = new THREE.MeshStandardMaterial({ color: o.cloth || 0x2b3440, roughness: 0.8, metalness: 0 });
    var skin = new THREE.MeshStandardMaterial({ color: 0x9c7a62, roughness: 0.7, metalness: 0 });
    var hat = new THREE.MeshStandardMaterial({ color: 0xe9e6de, roughness: 0.35, metalness: 0.05 });
    function cap(r, len, mat, x, y, z) {
      var m = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 6, 14), mat);
      m.position.set(x, y, z); g.add(m); return m;
    }
    cap(0.075, 0.72, cloth, -0.1, 0.43, 0);        /* legs, to the hip at 0.86 */
    cap(0.075, 0.72, cloth, 0.1, 0.43, 0);
    cap(0.17, 0.42, cloth, 0, 1.13, 0);            /* torso, shoulders at about 1.45 */
    cap(0.06, 0.52, cloth, -0.25, 1.12, 0.02);     /* arms */
    cap(0.06, 0.52, cloth, 0.25, 1.12, 0.02);
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.105, 20, 16), skin);
    head.position.set(0, 1.56, 0); g.add(head);
    var hh = new THREE.Mesh(new THREE.SphereGeometry(0.125, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2), hat);
    hh.position.set(0, 1.6, 0); g.add(hh);
    g.userData = { height: 1.72 };
    return g;
  };

  /* THE SKY, as a dome in the scene rather than a gradient painted behind it, so the fog, the
   * horizon and the silhouettes all agree about where the light is. Zenith to horizon glow, with
   * a warm trace at the very edge where a town would be. Unlit, and outside the fog. */
  N.sky = function (THREE, R, o) {
    o = o || {};
    var RAD = o.radius || 150;   /* inside the camera's far plane of 200, or the dome is clipped away */
    /* THE GRADIENT IS A TEXTURE, read per pixel down the sphere's own latitude, because vertex
     * colours interpolate ring by ring and the first render showed every ring as a band. */
    var n = 1024, c = document.createElement("canvas");
    c.width = 4; c.height = n; /* four columns, each dithered on its own */
    var x = c.getContext("2d");
    var zen = new THREE.Color(o.zenith || N.ZENITH), hor = new THREE.Color(o.horizon || N.HORIZON);
    var warm = new THREE.Color(o.warm || 0x3a3431), col = new THREE.Color();
    var im = x.createImageData(4, n), Rn = TX.rng(N.SEED + 7);
    for (var j = 0; j < n; j++) {
      /* canvas row 0 is the TOP of the texture, which SphereGeometry maps to the north pole */
      var lat = 90 - (j + 0.5) / n * 180;              /* degrees above the horizon */
      var t = Math.max(0, Math.min(1, lat / (o.span || 38)));
      col.copy(hor).lerp(zen, Math.pow(t, 0.5));
      if (lat < 2.2) col.lerp(warm, Math.min(1, (2.2 - Math.max(lat, 0)) / 2.2) * 0.6);
      for (var i = 0; i < 4; i++) {
        var d = (Rn() - 0.5) * 2.5 / 255;               /* per pixel dither, so eight bits never band */
        var p = (j * 4 + i) * 4;
        im.data[p] = 255 * Math.max(0, col.r + d); im.data[p + 1] = 255 * Math.max(0, col.g + d);
        im.data[p + 2] = 255 * Math.max(0, col.b + d); im.data[p + 3] = 255;
      }
    }
    x.putImageData(im, 0, 0);
    var tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.LinearSRGBColorSpace;
    tex.magFilter = THREE.LinearFilter;
    var dome = new THREE.Mesh(new THREE.SphereGeometry(RAD, 64, 64),
      new THREE.MeshBasicMaterial({ map: tex, side: THREE.BackSide, fog: false, depthWrite: false, toneMapped: false }));
    dome.renderOrder = -1;
    /* CENTRED ON THE CAMERA, so no part of it falls past the far plane. Call it after TXT.frame. */
    dome.position.copy(R.camera.position);
    R.scene.add(dome);
    return dome;
  };

  /* THE PAD'S TOOTH, as a texture on the ground TXT.ground made, so the caliche has grain that
   * tightens with distance through the camera rather than being drawn to look like it does.
   * Deterministic: seeded value noise, never Math.random. */
  N.padMap = function (THREE, ground, o) {
    o = o || {};
    var n = 512, c = document.createElement("canvas");
    c.width = n; c.height = n;
    var x = c.getContext("2d"), im = x.createImageData(n, n), R = TX.rng(o.seed || N.SEED);
    var grid = [];
    for (var k = 0; k < 64 * 64; k++) grid.push(R());
    function vn(u, v) {
      var i = Math.floor(u), j = Math.floor(v), fu = u - i, fv = v - j;
      var g = function (a, b) { return grid[((b & 63) * 64) + (a & 63)]; };
      var s1 = g(i, j) + (g(i + 1, j) - g(i, j)) * fu, s2 = g(i, j + 1) + (g(i + 1, j + 1) - g(i, j + 1)) * fu;
      return s1 + (s2 - s1) * fv;
    }
    for (var yy = 0; yy < n; yy++) for (var xx = 0; xx < n; xx++) {
      var u = xx / n * 64, v = yy / n * 64;
      var val = 0.55 * vn(u / 8, v / 8) + 0.3 * vn(u / 2, v / 2) + 0.15 * vn(u, v);
      var fine = R();
      var L = 150 + (val - 0.5) * 44 + (fine - 0.5) * 22;
      var p = (yy * n + xx) * 4;
      im.data[p] = L; im.data[p + 1] = L * 0.96; im.data[p + 2] = L * 0.9; im.data[p + 3] = 255;
    }
    x.putImageData(im, 0, 0);
    var t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(o.repeat || 120, o.repeat || 120);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    ground.material.map = t;
    ground.material.color.set(o.tint || 0x6f685e);
    ground.material.needsUpdate = true;
    return t;
  };

  /* A YARD MAST. A galvanised pole with a lamp head, the frame's visible reason for its light.
   * The head is emissive, so the grade's bloom finds it; the light itself is the deck's key. */
  N.mast = function (THREE, M, o) {
    o = o || {};
    var g = new THREE.Group(), h = o.height || 16;
    var pole = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.2, h, 16), M.galv);
    pole.position.y = h / 2; g.add(pole);
    var arm = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.1, 0.1), M.galv);
    arm.position.set(0.7, h - 0.2, 0); g.add(arm);
    var lampMat = new THREE.MeshStandardMaterial({ color: 0x222222, emissive: 0xfff0d8, emissiveIntensity: 6 });
    [-0.1, 1.4].forEach(function (x) {
      var head = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.16, 0.42), M.skid);
      head.position.set(x, h - 0.32, 0); g.add(head);
      var lens = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.03, 0.34), lampMat);
      lens.position.set(x, h - 0.41, 0); g.add(lens);
    });
    return g;
  };

  /* THE STATE'S PAPER, in the accent exactly. Paper printed amber is a flat printed colour, so it
   * is unlit and outside the tone map: under the deck's warm key a lit amber drifts orange and
   * the accent a reader is meant to recognise across frames stops being one colour. Only paper
   * wears it, never a machine. */
  /* AND IT IS SOLVED THROUGH THE GRADE, not typed. TXDECK.finish runs a filmic curve, a warm gain
   * and a lift over the whole art canvas, so paper printed at #E0A33F came out of the first render
   * at about (233, 194, 40): a different colour, and layout_check found the accent on one frame
   * of four. The ink that lands on the accent AFTER the grade is found by running the deck's own
   * grade over a patch and correcting until it converges, once per page. If the grade changes,
   * the ink follows it, so the accent a reader sees is the declared one by construction. */
  var PAPER_IN = null;
  N.paperInk = function () {
    if (PAPER_IN) return PAPER_IN;
    var t = TX_hex(N.ACCENT), inp = t.slice();
    var c = document.createElement("canvas");
    c.width = 2160; c.height = 2700;
    for (var it = 0; it < 10; it++) {
      var x = c.getContext("2d");
      x.setTransform(1, 0, 0, 1, 0, 0);
      x.fillStyle = N.SKY_HEX; x.fillRect(0, 0, 2160, 2700);
      x.scale(2, 2);
      x.fillStyle = "rgb(" + inp.map(function (v) { return Math.round(Math.max(0, Math.min(255, v))); }).join(",") + ")";
      x.fillRect(390, 520, 300, 300);
      TXDECK.finish(x);
      var d = c.getContext("2d").getImageData(1040, 1290, 40, 40).data, s = [0, 0, 0];
      for (var i = 0; i < d.length; i += 4) { s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2]; }
      var got = s.map(function (v) { return v / (d.length / 4); });
      inp = inp.map(function (v, k) { return Math.max(0, Math.min(255, v + (t[k] - got[k]) * 0.9)); });
    }
    PAPER_IN = inp.map(Math.round);
    if (global.document && document.body) document.body.setAttribute("data-paper-ink", PAPER_IN.join(","));
    return PAPER_IN;
  };
  function TX_hex(h) { return [1, 3, 5].map(function (i) { return parseInt(h.slice(i, i + 2), 16); }); }

  N.paperMat = function (THREE) {
    var p = N.paperInk();
    var col = new THREE.Color().setRGB(p[0] / 255, p[1] / 255, p[2] / 255, THREE.SRGBColorSpace);
    return new THREE.MeshBasicMaterial({ color: col, toneMapped: false });
  };

  /* A thin rectangular marker tile, for frames that draw a count as physical units in one scale. */
  N.tile = function (THREE, w, h, d, mat) {
    return new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  };

  /* A world point to frame CSS pixels through the frame's own camera, so a DOM label or a page's
   * type lands on the thing it names by projection rather than by a typed coordinate. */
  N.project = function (THREE, R, p) {
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return { x: (v.x + 1) / 2 * N.W, y: (1 - v.y) / 2 * N.H };
  };

  /* A parallel camera for a frame that compares quantities, because perspective shrinks the far
   * end of a row and a reader would read the shrink as a smaller number. `span` is the frame's
   * width in metres. It replaces the bench's perspective camera and TXT.frame then aims it. */
  N.ortho = function (THREE, R, span) {
    var w = span / 2, h = w * N.H / N.W;
    R.camera = new THREE.OrthographicCamera(-w, w, h, -h, 0.1, 400);
    return R.camera;
  };

  /* A FOLDING CHAIR, for the hearing room. Steel frame, a moulded seat and back. */
  N.chair = function (THREE, M) {
    var g = new THREE.Group();
    g.add(box(THREE, 0.44, 0.035, 0.42, M.seat, 0, 0.46, 0));
    var back = box(THREE, 0.44, 0.30, 0.03, M.seat, 0, 0.78, -0.2);
    back.rotation.x = -0.1; g.add(back);
    [[-0.2, 0.19], [0.2, 0.19], [-0.2, -0.2], [0.2, -0.2]].forEach(function (q) {
      var leg = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, q[1] < 0 ? 0.92 : 0.46, 8), M.galv);
      leg.position.set(q[0], q[1] < 0 ? 0.46 : 0.23, q[1]); g.add(leg);
    });
    return g;
  };

  /* THE ENGINE, for the frame that opens the box. A sixteen cylinder vee on its base rails, the
   * alternator drum at the radiator end, exhaust manifolds along both banks. Proportioned to sit
   * inside the 12.2 m enclosure; no rating is implied by any of it. Origin on the skid deck. */
  N.engine = function (THREE, M) {
    var g = new THREE.Group();
    var iron = TXT_mat(M, "iron");
    g.add(box(THREE, 7.6, 0.18, 1.5, M.skid, 0, 0.09, 0));                   /* base rails */
    g.add(box(THREE, 5.0, 1.05, 1.15, iron, -1.2, 0.72, 0));                 /* crankcase */
    [-1, 1].forEach(function (bank) {
      for (var c = 0; c < 8; c++) {
        var head = box(THREE, 0.5, 0.42, 0.5, iron, -3.3 + c * 0.6, 1.5, bank * 0.52);
        head.rotation.x = bank * 0.52; g.add(head);
        var cover = box(THREE, 0.44, 0.1, 0.36, M.galv, -3.3 + c * 0.6, 1.76, bank * 0.66);
        cover.rotation.x = bank * 0.52; g.add(cover);
      }
      var man = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 4.9, 16), M.galv);
      man.rotation.z = Math.PI / 2; man.position.set(-1.2, 1.3, bank * 0.98); g.add(man);
    });
    var drum = new THREE.Mesh(new THREE.CylinderGeometry(0.78, 0.78, 1.7, 40), M.paintDk);
    drum.rotation.z = Math.PI / 2; drum.position.set(2.6, 0.98, 0); g.add(drum);
    var fly = new THREE.Mesh(new THREE.CylinderGeometry(0.66, 0.66, 0.36, 40), iron);
    fly.rotation.z = Math.PI / 2; fly.position.set(1.55, 0.9, 0); g.add(fly);
    var turbo = new THREE.Mesh(new THREE.TorusGeometry(0.26, 0.12, 12, 24), M.galv);
    turbo.position.set(-4.0, 1.7, 0); turbo.rotation.y = Math.PI / 2; g.add(turbo);
    return g;
  };
  function TXT_mat(M, k) { return M[k] || M.skid; }

  /* THE DECK'S SHELL, kept here rather than typed into nine frames. */
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
  /* Refuses a black render, then paints it onto the frame's art canvas and hands that back for
   * TXDECK.finish, which every frame calls itself, last. */
  N.develop = function (shot, glCanvas) {
    if (!shot || !shot.ok) throw new Error("the GPU frame came back black: " + JSON.stringify(shot));
    var cx = document.getElementById("art").getContext("2d");
    cx.scale(2, 2);
    cx.drawImage(glCanvas, 0, 0, N.W, N.H);
    return cx;
  };

  N.boxes = function (sel, pad) { return TXDECK.lineBoxes(sel, pad); };

  global.YARD = N;
})(this);
