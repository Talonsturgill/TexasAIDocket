/* deck/2026-10-25-returnplate.js — the chassis for the 2026-10-25 deck: the water board's water use survey, which
 * the Texas Tribune's records say 233 of 334 data center facilities never submitted from 2020 through 2025, and
 * ERCOT's request of September 14th, 2026, which carries the board's questions in its Section C (tx-2026-0172).
 *
 * THE VISUAL ARGUMENT. One gray cast iron plate with one threaded bore for each facility in the Tribune's records.
 * A brass hex pipe plug seals each of the 101 that returned a survey at least once, and the 233 stay open. Under a
 * low key a plug catches the light and a bore swallows it, so the count reads as light before a word is read. The
 * plugs fill the bores in reading order from the plate's north row, and the order says nothing about which facility.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky, one warm seam low on the key's side, the
 * subject in a pool of light on caliche and the world behind it gone dark.
 *
 * THE LIGHT is azimuth -62, elevation 13. +x is east and +z is south, az runs from +z toward -x for a negative value,
 * so the last light stands low in the south west of every subject: a camera on +z looking -z has the key in front
 * and to its LEFT, every plug, flange and bushing has its lit edge on the left, and every cast runs long to the right
 * and away. A material relief reads it from the upper left of its frame and every cast runs down and to the right.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having neither: `return_plate` (the cast iron plate, its bores, thread
 * rings and brass plugs) and `ground_storage_tank` (a welded steel water tank on a concrete ringwall). Each is built
 * in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is dust, #C9B393, the brass of an answer returned, and it means that ONE thing.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 * Every frame composes its own picture, and every count a frame draws is read from figures.json in that frame's own
 * code where figure_bearing.py reads it. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("returnplate.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "returnplate",
    light: { az: -62, el: 13 },
    sky: "lastLight",
    ground: "#08060F",
    material: "#2B2C2E",
    accent: "#C9B393",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.9, strength: 0.08, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261025 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261025;
  N.ACCENT = 0xc9b393;   /* dust, brand.yaml's, and it means ONE thing: an answer returned */
  N.INK = "#ECE8DF";
  /* THE PLATE, in metres, on every frame that shows it: one bore per position at this pitch, rows of COLS */
  N.PLATE = { cols: 20, pitch: 0.075, bore: 0.03, depth: 0.045, thick: 0.075, margin: 0.06, band: 0.18 };

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */
  /* A SAND CAST GRAIN for the iron: fine speckle and a few larger pits in a bump map, so the plate's flat top reads
   * as a casting under the low key and never as a painted panel */
  function grain(THREE, size, seed) {
    var c = document.createElement("canvas"); c.width = c.height = size; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "#808080"; x.fillRect(0, 0, size, size);
    for (var i = 0; i < size * size * 0.18; i++) { var v = Math.floor(96 + r() * 64); x.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; x.fillRect(r() * size, r() * size, 1.3, 1.3); }
    for (var j = 0; j < 140; j++) { x.fillStyle = "rgba(40,40,40,0.5)"; x.beginPath(); x.arc(r() * size, r() * size, 0.8 + r() * 1.6, 0, 6.283); x.fill(); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  /* THE TANK'S COATING: desert tan with long vertical rust and dust streaks, darker toward the base */
  function coating(THREE, seed) {
    var c = document.createElement("canvas"); c.width = 512; c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "#ffffff"; x.fillRect(0, 0, 512, 256);
    for (var i = 0; i < 260; i++) { var a = 0.03 + r() * 0.08, w = 1 + r() * 4, px = r() * 512, len = 30 + r() * 200;
      var g = x.createLinearGradient(0, 0, 0, len); g.addColorStop(0, "rgba(90,70,50," + a + ")"); g.addColorStop(1, "rgba(90,70,50,0)");
      x.fillStyle = g; x.fillRect(px, r() * 60, w, len); }
    var t = new THREE.CanvasTexture(c); t.wrapS = THREE.RepeatWrapping; t.wrapT = THREE.ClampToEdgeWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
  }
  N.mats = function (THREE, K) {
    if (N._m) return N._m;
    var g = grain(THREE, 256, N.SEED); g.repeat.set(6, 6);
    var g2 = grain(THREE, 256, N.SEED + 9); g2.repeat.set(40, 40);   /* fine scratches on the brass */
    var m = {
      /* gray cast iron, rough and only partly metallic so it never mirrors the navy sky */
      iron: new THREE.MeshStandardMaterial({ color: 0x2e2f31, roughness: 0.9, metalness: 0.12, bumpMap: g, bumpScale: 1.2 }),
      ironDark: new THREE.MeshStandardMaterial({ color: 0x0b0b0c, roughness: 0.95, metalness: 0 }),
      thread: new THREE.MeshStandardMaterial({ color: 0x4a4b4e, roughness: 0.55, metalness: 0.5 }),
      /* brass, held at roughness 0.48 so the lastLight sky does not paint a navy accent into it */
      brass: new THREE.MeshStandardMaterial({ color: N.ACCENT, roughness: 0.34, metalness: 0.55 }),
      coat: new THREE.MeshStandardMaterial({ color: 0x8f8470, roughness: 0.8, metalness: 0.05, map: coating(THREE, N.SEED + 3) }),
      seam: new THREE.MeshStandardMaterial({ color: 0x5f5648, roughness: 0.85, metalness: 0.05 }),
      roof: new THREE.MeshStandardMaterial({ color: 0x7a7060, roughness: 0.82, metalness: 0.08 }),
      ring: K.finish.concrete(),
      galv: K.mat("rp_galv", { color: 0x8c9094, metalness: 0.6, roughness: 0.6 }),
      rail: K.mat("rp_rail", { color: 0x6f6a5c, metalness: 0.4, roughness: 0.6 })
    };
    N._m = m;
    return m;
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.return_plate) return;
    var M = N.mats(THREE, K);

    /* THE POSITIONS of a plate of `total` bores in rows of `cols`, row 0 the north row at -z, filled west to east.
     * Returns [x, z] in the plate's own frame, centred on its footprint, and the plate's width and depth. */
    N.plateLayout = function (total, cols) {
      var P = N.PLATE, rows = Math.ceil(total / cols);
      var w = cols * P.pitch + 2 * P.margin, d = rows * P.pitch + P.margin + P.band + P.margin * 0.5;
      var pts = [];
      for (var i = 0; i < total; i++) {
        var r = Math.floor(i / cols), c = i % cols;
        pts.push([-w / 2 + P.margin + (c + 0.5) * P.pitch, -d / 2 + P.margin + (r + 0.5) * P.pitch]);
      }
      return { pts: pts, w: w, d: d, rows: rows };
    };

    /* A RETURN PLATE: a gray cast iron slab `thick` deep with one blind threaded bore per position, the bores cut
     * through the top as real holes so the camera sees down into them, a dark floor at the bore's depth, three
     * thread rings inside each rim, a raised foundry band along the south (+z) edge, and a brass hex pipe plug in
     * each of the first `answered` positions. */
    K.define("return_plate", {
      size: [1.62, 0.1, 1.53],
      options: { total: 340, answered: 0, cols: 20, plugs: true },
      note: "A cast iron plate with one threaded bore per position and a brass hex pipe plug in each of the first `answered`. Drawn to illustrate.",
      make: function (o) {
        var P = N.PLATE, L = N.plateLayout(o.total, o.cols), w = L.w, d = L.d, g = new THREE.Group();
        /* the slab, its top face carrying every bore as a hole */
        var sh = new THREE.Shape(), r = 0.012;
        sh.moveTo(-w / 2 + r, -d / 2); sh.lineTo(w / 2 - r, -d / 2); sh.quadraticCurveTo(w / 2, -d / 2, w / 2, -d / 2 + r);
        sh.lineTo(w / 2, d / 2 - r); sh.quadraticCurveTo(w / 2, d / 2, w / 2 - r, d / 2); sh.lineTo(-w / 2 + r, d / 2);
        sh.quadraticCurveTo(-w / 2, d / 2, -w / 2, d / 2 - r); sh.lineTo(-w / 2, -d / 2 + r); sh.quadraticCurveTo(-w / 2, -d / 2, -w / 2 + r, -d / 2);
        L.pts.forEach(function (p) { var h = new THREE.Path(); h.absarc(p[0], -p[1], P.bore, 0, Math.PI * 2, true); sh.holes.push(h); });
        /* NO BEVEL ON THE HOLES: an extrude bevel opens a seam where each hole's path starts, which read as a notch at
         * three o'clock on every near bore. The rim's chamfer is its own turned ring instead. */
        var top = new THREE.ExtrudeGeometry(sh, { depth: P.depth, bevelEnabled: false, curveSegments: 64 });
        top.rotateX(-Math.PI / 2); top.translate(0, P.thick - P.depth, 0);
        K.uvBox(top, 0.4);
        var slab = new THREE.Mesh(top, M.iron); slab.castShadow = slab.receiveShadow = true; g.add(slab);
        /* the solid lower part of the casting under the bores */
        var base = K.box(w, P.thick - P.depth, d, M.iron, 0, 0, 0, 0.004, g); base.castShadow = base.receiveShadow = true;
        /* the bore floors, black */
        var floorGeo = new THREE.CircleGeometry(P.bore * 0.98, 48); floorGeo.rotateX(-Math.PI / 2);
        var floors = K.instances(floorGeo, M.ironDark, L.pts.map(function (p) { return [p[0], P.thick - P.depth + 0.001, p[1]]; }), g);
        floors.receiveShadow = true;
        /* THE THREAD: a turned sawtooth wall over the bore's top 15 mm, five crests 3 mm apart, so a near bore shows its
         * thread on the far wall where the key reaches it */
        var tp = [new THREE.Vector2(P.bore + 0.004, 0.0005), new THREE.Vector2(P.bore, -0.003)];
        for (var k = 0; k < 5; k++) { tp.push(new THREE.Vector2(P.bore - 0.0028, -0.0045 - k * 0.003)); tp.push(new THREE.Vector2(P.bore - 0.0002, -0.006 - k * 0.003)); }
        tp.push(new THREE.Vector2(P.bore - 0.0002, -0.02));
        var threadGeo = new THREE.LatheGeometry(tp, 64);
        var th = K.instances(threadGeo, M.thread, L.pts.slice(o.answered).map(function (p) { return [p[0], P.thick, p[1]]; }), g);
        th.castShadow = false; th.receiveShadow = true;
        /* the foundry band, a smooth raised strip along the south edge */
        var band = K.box(w - 2 * P.margin * 0.6, 0.008, P.band - 0.05, M.iron, 0, P.thick, d / 2 - P.band / 2 - 0.01, 0.003, g);
        band.castShadow = band.receiveShadow = true;
        /* THE PLUGS: a band of exposed thread above the face, a hex 57 mm across flats with chamfered arrises, a turned
         * boss and a shallow dome, instanced, and a dark contact ring where each meets the iron */
        if (o.plugs && o.answered > 0) {
          var hexR = 0.057 / Math.sqrt(3), list = L.pts.slice(0, o.answered);
          var hs = new THREE.Shape();
          for (var v = 0; v < 6; v++) { var an = v / 6 * Math.PI * 2 + Math.PI / 6, hx = Math.cos(an) * (hexR - 0.0015), hz = Math.sin(an) * (hexR - 0.0015); if (v) hs.lineTo(hx, hz); else hs.moveTo(hx, hz); }
          hs.closePath();
          var hex = new THREE.ExtrudeGeometry(hs, { depth: 0.011, bevelEnabled: true, bevelThickness: 0.0015, bevelSize: 0.0015, bevelSegments: 2 });
          hex.rotateX(-Math.PI / 2); hex.translate(0, 0.0075, 0);
          var bp = [];
          for (var k2 = 0; k2 < 3; k2++) { bp.push(new THREE.Vector2(0.0262, k2 * 0.002)); bp.push(new THREE.Vector2(0.0278, k2 * 0.002 + 0.001)); }
          bp.push(new THREE.Vector2(0.0262, 0.0062));
          var tband = new THREE.LatheGeometry(bp, 64);
          var boss = new THREE.CylinderGeometry(0.0235, 0.0255, 0.004, 64); boss.translate(0, 0.0215, 0);
          var dome = new THREE.SphereGeometry(0.0235, 64, 16, 0, Math.PI * 2, 0, Math.PI * 0.28); dome.translate(0, 0.0235 - 0.0235 * Math.cos(Math.PI * 0.28), 0);
          var shank = new THREE.CylinderGeometry(P.bore * 0.98, P.bore * 0.98, P.depth * 0.9, 32); shank.translate(0, -P.depth * 0.45, 0);
          [hex, tband, boss, dome, shank].forEach(function (geo, gi) {
            var im = K.instances(geo, M.brass, list.map(function (p, i) { return [p[0], P.thick, p[1], (i * 0.37) % (Math.PI / 3)]; }), g);
            im.castShadow = gi !== 4; im.receiveShadow = true;
          });
          var cring = new THREE.RingGeometry(0.026, 0.052, 48); cring.rotateX(-Math.PI / 2);
          var cmat = new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.45, depthWrite: false });
          K.instances(cring, cmat, list.map(function (p) { return [p[0], P.thick + 0.0004, p[1]]; }), g);
        }
        g.userData.layout = L;
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* A WELDED STEEL GROUND STORAGE TANK on a concrete ringwall: six shell courses with a seam at each, a cone roof at
     * a 1 in 12 pitch with radial seams and a centre vent, a spiral stair on the shell with its rail, and an overflow
     * pipe down the side. */
    K.define("ground_storage_tank", {
      size: [62, 17, 62],
      options: { diameter: 60, height: 13.4 },
      note: "A welded steel ground storage tank in a desert tan coating on a concrete ringwall. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), R = o.diameter / 2, H = o.height, ring = 0.6;
        var rw = K.cyl(R + 0.6, R + 0.7, ring, M.ring, 0, 0, 0, 96, g); K.uvBox(rw.geometry, 3); rw.castShadow = rw.receiveShadow = true;
        var shell = new THREE.Mesh(new THREE.CylinderGeometry(R, R, H, 128, 1, true), M.coat);
        shell.material.map.repeat.set(8, 1);
        shell.position.y = ring + H / 2; shell.castShadow = shell.receiveShadow = true; g.add(shell);
        var courses = Math.round(H / 2.4);
        for (var k = 1; k < courses; k++) {
          var s = new THREE.Mesh(new THREE.TorusGeometry(R + 0.012, 0.025, 4, 160), M.seam);
          s.rotation.x = Math.PI / 2; s.position.y = ring + k * H / courses; g.add(s);
        }
        var top = new THREE.Mesh(new THREE.TorusGeometry(R + 0.04, 0.09, 6, 160), M.seam); top.rotation.x = Math.PI / 2; top.position.y = ring + H; g.add(top);
        var rh = R / 12;
        var roof = new THREE.Mesh(new THREE.ConeGeometry(R + 0.25, rh, 128, 1, true), M.roof); roof.position.y = ring + H + rh / 2; roof.castShadow = roof.receiveShadow = true; g.add(roof);
        for (var a = 0; a < 48; a++) {
          var t = a / 48 * Math.PI * 2;
          K.bar([Math.cos(t) * 0.8, ring + H + rh - 0.06, Math.sin(t) * 0.8], [Math.cos(t) * (R + 0.2), ring + H + 0.02, Math.sin(t) * (R + 0.2)], 0.03, M.seam, 4, g);
        }
        K.cyl(0.6, 0.7, 1.0, M.galv, 0, ring + H + rh - 0.1, 0, 24, g);
        K.cyl(0.85, 0.85, 0.12, M.galv, 0, ring + H + rh + 0.9, 0, 24, g);
        /* the spiral stair: treads climbing a quarter turn up the shell from the south west, and its outer rail */
        var steps = Math.round(H / 0.2), a0 = Math.PI * 0.75, sweep = Math.PI * 0.45, railPts = [];
        for (var i = 0; i <= steps; i++) {
          var f = i / steps, ang = a0 + f * sweep, y = ring + f * H;
          var tr = K.box(1.0, 0.04, 0.28, M.rail, 0, y, 0, 0, g);
          tr.position.set(Math.cos(ang) * (R + 0.55), y + 0.02, Math.sin(ang) * (R + 0.55)); tr.rotation.y = -ang;
          tr.castShadow = true;
          railPts.push(new THREE.Vector3(Math.cos(ang) * (R + 1.05), y + 1.07, Math.sin(ang) * (R + 1.05)));
        }
        g.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(railPts), 120, 0.03, 5, false), M.rail));
        for (var q = 0; q <= steps; q += 6) { var p = railPts[q]; K.bar([p.x, p.y - 1.07, p.z], [p.x, p.y, p.z], 0.02, M.rail, 4, g); }
        /* the overflow pipe down the east side */
        K.bar([R + 0.3, ring + H - 0.4, 0], [R + 0.3, ring + 0.2, 0], 0.15, M.galv, 12, g);
        g.userData.keepOrigin = true;
        return g;
      }
    });
  };

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



  /* ---- the relief bench: the plate, the tanks, the bus bar and the attestation in plan ------- */
  /* Linear albedo per material id, with tooth in the albedo rather than the height so a low key never turns noise
   * into a leopard print. Everything outside the subject stays near black. */
  N.M = { VOID: 0, IRON: 1, BORE: 2, BRASS: 3, CALICHE: 4, THREAD: 5, COAT: 6, RING: 7, SOIL: 8, COPPER: 9,
          PORC: 10, STEEL: 11, PAPER: 12, BOLT: 13 };
  var BASE = {
    0: [0.004, 0.004, 0.006],
    1: [0.034, 0.035, 0.037],   /* gray cast iron */
    2: [0.003, 0.003, 0.003],   /* a bore's floor, black */
    3: [0.48, 0.38, 0.22],      /* brass, linear, set so it grades to the dust accent */
    4: [0.20, 0.17, 0.12],      /* caliche, dark where the pool falls off */
    5: [0.08, 0.08, 0.085],     /* a thread crest */
    6: [0.22, 0.19, 0.14],      /* the tank's desert tan coating */
    7: [0.16, 0.155, 0.145],    /* a concrete ringwall */
    8: [0.025, 0.021, 0.017],   /* graded dark soil */
    9: [0.42, 0.20, 0.10],      /* tinned copper, satin */
    10: [0.12, 0.065, 0.035],   /* brown glazed porcelain */
    11: [0.020, 0.021, 0.024],  /* dark steel */
    12: [0.50, 0.48, 0.43],     /* cotton bond */
    13: [0.10, 0.10, 0.10]      /* a bolt head */
  };
  N.SPEC = { 1: [0.10, 12], 3: [0.85, 60], 4: [0.04, 6], 5: [0.30, 24], 6: [0.08, 12], 7: [0.06, 8], 9: [0.55, 40],
             10: [0.6, 50], 11: [0.12, 16], 12: [0.05, 8], 13: [0.4, 30] };
  N.albedo = function (X, Y, m) {
    var b = BASE[m] || BASE[0], n = global.TX && TX.simplex2 ? TX.simplex2(X * 0.07, Y * 0.07) * 0.5 + TX.simplex2(X * 0.37, Y * 0.37) * 0.3 : 0;
    var k = 1 + ((m === 1 || m === 11) ? 0.6 : (m === 4 || m === 8 ? 0.5 : 0.08)) * n;
    if ((m === 1 || m === 11) && global.TX) { var f = TX.simplex2(X * 1.9, Y * 1.9); k += f > 0.62 ? 0.4 : (f < -0.7 ? -0.3 : 0); }
    return [b[0] * k, b[1] * k, b[2] * k];
  };

  global.CH = N;
})(this);
