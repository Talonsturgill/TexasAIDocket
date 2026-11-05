/* deck/2026-11-04-wellpad.js — the chassis for the 2026-11-04 deck: Permian Resources' third quarter results, filed
 * with the SEC on November 4th, 2026, saying its production team has deployed an AI-powered artificial lift
 * monitoring system and that it feeds its subsurface data into large language models (tx-2026-0240).
 *
 * THE VISUAL ARGUMENT. The watched stroke. One Permian pump jack recurs as the subject and its crank advances 40
 * degrees a frame, so the deck is one stroke left open at the close. The AI is never drawn as a device, because the
 * record names none. What is watched, the stroke and its rod, carries the argument, and every figure the release
 * prints gets its own oilfield object at true scale.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down in the west south west, a near black sky with one warm seam
 * low on the key's side, the subject in its pool on a caliche pad and the basin behind it gone dark.
 *
 * THE LIGHT is azimuth -70, elevation 6. +x is east and +z is south, so the sun stands low in the west south west. A
 * camera looking west has the key behind its subject: every lit edge is a rim on the subject's top and right, and
 * every cast runs toward the camera and a little to the right. TXBENCH reliefs read the same declaration, raked low.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `release_page` (a printed letter sheet with ruled
 * text lines in its albedo, pencil brackets and a curled corner), `strata_block` (a cutaway block of ground with
 * banded rock on its cut faces), `pipe_column` (drill pipe joints with tool joint upsets stacked on end to a height),
 * `gauge_board` (a float gauge board for a stock tank with a sliding target) and `gauge_tape` (a gauger's steel tape
 * with graduations, brass tags and a plumb bob). Drawn to illustrate, to no maker's or operator's design, in the
 * kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is dusk_gold, #E0956A, and it means ONE thing: a figure the release or the record prints. The plate at
 * the pipe column's foot, the gauge target, the brass tags on the cast iron and on the tape. The jack never wears it.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 * Every count a frame draws is read from figures.json in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("wellpad.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "wellpad",
    light: { az: -70, el: 6 },
    sky: "lastLight",
    ground: "#0A0A0C",
    material: "#B9A68A",
    accent: "#E0956A",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.08, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.14, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261104 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080; N.H = 1350; N.SEED = 20261104; N.INK = "#EEEAE3";
  N.GOLD = "#E0956A";   /* brand.yaml's dusk_gold: a figure the release or the record prints, and nothing else */
  N.JACK = { color: 0x4a4b45, head: 0x2a2b28, seed: 11 };   /* the one jack every frame shows */
  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;
  N.ft2m = function (ft) { return ft * 0.3048; };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.release_page) return;
    function shade(o) { o.traverse(function (c) { if (c.isMesh) { c.castShadow = c.receiveShadow = true; } }); return o; }
    var GOLD = K.mat("wp-gold", { color: 0xc9894f, metalness: 0.75, roughness: 0.32, emissive: 0x3a1c08, emissiveIntensity: 0.35 });
    N.goldMat = GOLD;
    var STEEL = K.mat("wp-steel", { color: 0x8b8f93, metalness: 0.8, roughness: 0.38 });
    var DARK = K.mat("wp-dark", { color: 0x16171a, roughness: 0.7, metalness: 0.2 });

    /* A RELEASE PAGE: a US letter sheet, 0.216 m by 0.279 m, lying flat, its far right corner curled up about 2 cm.
     * The text is never type: ruled grey lines in the albedo stand for paragraphs, and `brackets` pencil brackets
     * mark the passages the frame names. A steel binder clip holds the near edge. */
    K.define("release_page", {
      size: [0.24, 0.03, 0.29],
      options: { brackets: 2, curl: 0.02, seed: 3 },
      note: "A printed letter sheet with ruled text lines in its albedo, pencil brackets on the margin, a curled corner and a binder clip.",
      make: function (o) {
        var G = new THREE.Group(), w = 0.216, d = 0.279, r = lcg(o.seed || 3), nb = Math.max(0, Math.round(o.brackets == null ? 2 : o.brackets));
        var c = document.createElement("canvas"); c.width = 864; c.height = 1116; var x = c.getContext("2d");
        x.fillStyle = "#f2efe8"; x.fillRect(0, 0, 864, 1116);
        for (var k = 0; k < 4000; k++) { x.fillStyle = "rgba(120,110,90," + (r() * 0.05) + ")"; x.fillRect(r() * 864, r() * 1116, 2, 2); }
        x.fillStyle = "#3a3d42"; x.fillRect(90, 80, 380, 26);                       /* the masthead block */
        x.fillStyle = "#8b8e92"; x.fillRect(90, 122, 240, 12);
        var y = 190, para = 0, marks = [];
        while (y < 1040) {
          var lines = 3 + Math.floor(r() * 4), y0 = y;
          for (var l = 0; l < lines && y < 1040; l++) { var len = l === lines - 1 ? 260 + r() * 300 : 640 + r() * 40; x.fillStyle = "#9a9da1"; x.fillRect(110, y, len, 11); y += 26; }
          marks.push([y0 - 6, y - 14]); y += 22; para++;
        }
        /* the brackets go on two middle paragraphs, a graphite stroke in the left margin */
        var pick = nb === 2 ? [2, 4] : nb === 1 ? [3] : [];
        x.strokeStyle = "#2b2b2d"; x.lineWidth = 6; x.lineCap = "round";
        pick.forEach(function (i) { var m = marks[Math.min(i, marks.length - 1)]; x.beginPath(); x.moveTo(84, m[0]); x.lineTo(66, m[0]); x.lineTo(66, m[1]); x.lineTo(84, m[1]); x.stroke(); });
        var tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
        var g = new THREE.PlaneGeometry(w, d, 24, 30); g.rotateX(-Math.PI / 2);
        var p = g.attributes.position, cu = o.curl == null ? 0.02 : o.curl;
        for (var i = 0; i < p.count; i++) { var px = p.getX(i), pz = p.getZ(i); var u = (px + w / 2) / w, v = (d / 2 - pz) / d; var t = Math.max(0, u + v - 1.45) / 0.55; p.setY(i, 0.0015 + cu * t * t); }
        g.computeVertexNormals();
        var sheet = new THREE.Mesh(g, K.mat("wp-paper", { color: 0xffffff, map: tex, roughness: 0.92, metalness: 0, side: THREE.DoubleSide })); G.add(sheet);
        /* the binder clip on the near edge */
        var clip = TXT.roundedBox(0.05, 0.012, 0.022, 0.003, K.mat("wp-clip", { color: 0x111214, metalness: 0.6, roughness: 0.35 })); clip.position.set(-0.03, 0.007, d / 2 - 0.008); G.add(clip);
        [-1, 1].forEach(function (s) { var a = new THREE.Mesh(new THREE.TorusGeometry(0.012, 0.0012, 6, 16, Math.PI), STEEL); a.position.set(-0.03 + s * 0.016, 0.014, d / 2 - 0.002); a.rotation.y = Math.PI / 2; G.add(a); });
        G.userData.brackets = pick.length;
        return shade(G);
      }
    });

    /* A STRATA BLOCK: a cutaway block of ground standing on the ground like a model on a table, `h` tall, its top the
     * pad. The front (+z) and right (+x) faces carry the bands in their albedo and bump: caliche, red bed, grey shale,
     * dark carbonate. The bands are drawn to illustrate and are not to scale. userData.top is the top's height. */
    K.define("strata_block", {
      size: [30, 12, 14],
      options: { w: 30, h: 12, d: 14, seed: 5 },
      note: "A cutaway block of ground with banded rock in the albedo and bump of its cut faces, its top a caliche pad.",
      make: function (o) {
        var G = new THREE.Group(), W = o.w || 30, H = o.h || 12, D = o.d || 14, r = lcg(o.seed || 5);
        var bands = [[0.07, [214, 196, 160]], [0.16, [140, 82, 52]], [0.10, [112, 66, 44]], [0.22, [92, 92, 90]], [0.14, [70, 72, 74]], [0.31, [44, 42, 44]]];
        function face(pxW) {
          var c = document.createElement("canvas"); c.width = pxW; c.height = 1024; var x = c.getContext("2d"), y = 0;
          var b = document.createElement("canvas"); b.width = pxW; b.height = 1024; var bx = b.getContext("2d");
          bands.forEach(function (bd, i) {
            var hh = bd[0] * 1024, col = bd[1];
            for (var yy = 0; yy < hh; yy++) {
              var j = 0.9 + 0.12 * Math.sin((y + yy) * 0.21 + i) + 0.06 * (r() - 0.5);
              x.fillStyle = "rgb(" + (col[0] * j | 0) + "," + (col[1] * j | 0) + "," + (col[2] * j | 0) + ")"; x.fillRect(0, y + yy, pxW, 1);
              var bump = 120 + 60 * Math.sin((y + yy) * 0.35 + i * 2) + 30 * (r() - 0.5); bx.fillStyle = "rgb(" + (bump | 0) + "," + (bump | 0) + "," + (bump | 0) + ")"; bx.fillRect(0, y + yy, pxW, 1);
            }
            x.fillStyle = "rgba(10,8,6,0.55)"; x.fillRect(0, y + hh - 2, pxW, 3); y += hh;
          });
          for (var k = 0; k < pxW * 3; k++) { var gx = r() * pxW, gy = r() * 1024, s = 1 + r() * 4; x.fillStyle = "rgba(" + (r() < 0.5 ? "20,16,12" : "230,220,200") + "," + (r() * 0.18) + ")"; x.fillRect(gx, gy, s, s * 0.6); bx.fillStyle = "rgba(255,255,255," + (r() * 0.2) + ")"; bx.fillRect(gx, gy, s, s * 0.6); }
          var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; var bt = new THREE.CanvasTexture(b);
          return K.mat("wp-strata-" + pxW, { color: 0xffffff, map: t, bumpMap: bt, bumpScale: 2.0, roughness: 0.92, metalness: 0 });
        }
        var front = face(2048), side = face(1024), top = K.mat("wp-cal", { color: 0xcbbb98, roughness: 0.95 }), dark = DARK;
        var geo = new THREE.BoxGeometry(W, H, D);
        var mesh = new THREE.Mesh(geo, [side, dark, top, dark, front, dark]);   /* +x, -x, +y, -y, +z, -z */
        mesh.position.set(0, H / 2, 0); G.add(mesh);
        G.userData.top = H;
        G.userData.bandAt = function (f) { var acc = 0; for (var i = 0; i < bands.length; i++) { if (f <= acc + bands[i][0]) return i; acc += bands[i][0]; } return bands.length - 1; };
        return shade(G);
      }
    });

    /* A PIPE COLUMN: range 2 drill pipe stood on end, joints of 9.45 m, 5 in body (0.127 m), tool joints of 0.168 m
     * with a box of 0.43 m and a pin shoulder of 0.30 m, each box carrying a bright hardband ring. Stacked to `height`
     * metres from a steel base plate. userData.top is the column's height. */
    K.define("pipe_column", {
      size: [0.6, 34.3, 0.6],
      options: { height: 34.29, joint: 9.45 },
      note: "Drill pipe joints with tool joint upsets and hardband rings stacked on end to a height, on a steel base plate.",
      make: function (o) {
        var G = new THREE.Group(), Ht = +o.height || 34.29, J = +o.joint || 9.45;
        var body = K.mat("wp-mill", { color: 0x2a2f36, metalness: 0.85, roughness: 0.42 });
        var tj = K.mat("wp-tj", { color: 0x6e7378, metalness: 0.9, roughness: 0.3 });
        var hb = K.mat("wp-hb", { color: 0xc8ccd0, metalness: 0.95, roughness: 0.18 });
        var base = K.box(0.6, 0.06, 0.6, K.mat("wp-plate", { color: 0x3b3c3e, metalness: 0.6, roughness: 0.55 }), 0, 0, 0, 0.01, G);
        var y = 0.06;
        while (y < Ht - 0.05) {
          var seg = Math.min(J, Ht - y);
          K.cyl(0.084, 0.084, Math.min(0.30, seg), tj, 0, y, 0, 24, G);                          /* pin shoulder */
          if (seg > 0.8) K.cyl(0.0635, 0.0635, seg - 0.73, body, 0, y + 0.30, 0, 20, G);           /* body */
          if (seg > 0.73) { K.cyl(0.084, 0.084, 0.43, tj, 0, y + seg - 0.43, 0, 24, G); K.cyl(0.0855, 0.0855, 0.06, hb, 0, y + seg - 0.30, 0, 24, G); }
          y += seg;
        }
        G.userData.top = Ht;
        return shade(G);
      }
    });

    /* A GAUGE BOARD: a float gauge for a stock tank, `height` m tall on the shell, a 0.25 m painted board with a
     * scale every tenth in its albedo, a T track, a target that slides to `level` (0 bottom to 1 top) and a cable
     * running up to a sheave on the roof. Origin at the board's foot, the board's face on +z. */
    K.define("gauge_board", {
      size: [0.3, 6, 0.1],
      options: { height: 5.6, level: 0.5 },
      note: "A stock tank float gauge board with a scale, a track, a sliding target and a cable over a roof sheave.",
      make: function (o) {
        var G = new THREE.Group(), Hb = +o.height || 5.6, lv = Math.max(0, Math.min(1, o.level == null ? 0.5 : +o.level));
        var c = document.createElement("canvas"); c.width = 64; c.height = 1024; var x = c.getContext("2d");
        x.fillStyle = "#d8d3c6"; x.fillRect(0, 0, 64, 1024);
        x.fillStyle = "#1c1d1f"; for (var k = 0; k <= 50; k++) { var yy = 1024 - k * (1024 / 50); x.fillRect(k % 5 ? 40 : 14, yy - 2, 64, k % 5 ? 3 : 5); }
        var tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
        var board = K.box(0.25, Hb, 0.025, K.mat("wp-board", { color: 0xffffff, map: tex, roughness: 0.7 }), 0, 0, 0, 0.004, G);
        var track = K.box(0.03, Hb, 0.04, STEEL, 0.15, 0, 0.0, 0.004, G);
        var ty = 0.05 + lv * (Hb - 0.1);
        var target = TXT.roundedBox(0.36, 0.14, 0.06, 0.01, GOLD); target.position.set(0.05, ty, 0.04); G.add(target);
        var cable = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, Hb - ty + 0.3, 6), STEEL); cable.position.set(0.15, ty + (Hb - ty + 0.3) / 2, 0.03); G.add(cable);
        var sheave = new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.015, 8, 20), STEEL); sheave.position.set(0.15, Hb + 0.3, 0.0); sheave.rotation.y = Math.PI / 2; G.add(sheave);
        G.userData.targetY = ty; G.userData.level = lv;
        return shade(G);
      }
    });

    /* A GAUGE TAPE: a gauger's steel tape, 13 mm wide, laid over a rail of radius `railR` at height `railY`, running
     * `span` m along +x on the rail's top, falling away at both ends in a shallow curve. `marks` graduations are
     * painted between the two brass tags, a longer one every `week`th. A brass plumb bob hangs from the -x end.
     * Origin under the span's middle on the ground. userData.tags holds the two tags' world positions in its frame. */
    K.define("gauge_tape", {
      size: [1.6, 1.6, 0.05],
      options: { span: 1.2, marks: 100, week: 7, railY: 1.5, railR: 0.037, drop: 0.32, width: 0.013 },
      note: "A gauger's steel tape with painted graduations and brass end tags, laid over a pipe rail, a brass plumb bob hanging from one end.",
      make: function (o) {
        var G = new THREE.Group(), S = +o.span || 1.2, M = Math.max(1, Math.round(+o.marks || 100)), wk = Math.max(2, Math.round(+o.week || 7));
        var ry = (o.railY == null ? 1.5 : +o.railY) + (o.railR == null ? 0.037 : +o.railR) + 0.0006, drop = +o.drop || 0.32, Wt = +o.width || 0.013;
        var hang = 0.18, pts = [];
        /* the path: hang down at -x, over the rail top for the span, hang down at +x */
        for (var i = 0; i <= 20; i++) { var t = i / 20; pts.push([-S / 2 - hang * (1 - t), ry - drop * Math.pow(1 - t, 2), 0]); }
        for (var j = 1; j <= 60; j++) { var u = j / 60; pts.push([-S / 2 + S * u, ry, 0]); }
        for (var k = 1; k <= 20; k++) { var t2 = k / 20; pts.push([S / 2 + hang * t2, ry - drop * t2 * t2, 0]); }
        var lens = [0]; for (var q = 1; q < pts.length; q++) lens.push(lens[q - 1] + Math.hypot(pts[q][0] - pts[q - 1][0], pts[q][1] - pts[q - 1][1]));
        var Ltot = lens[lens.length - 1], u0 = lens[20] / Ltot, u1 = lens[80] / Ltot;
        var c = document.createElement("canvas"); c.width = 4096; c.height = 64; var x = c.getContext("2d");
        x.fillStyle = "#e9e6dc"; x.fillRect(0, 0, 4096, 64);
        x.fillStyle = "#121314";
        for (var m = 0; m <= M; m++) { var px = (u0 + (u1 - u0) * m / M) * 4096; var long = m % wk === 0; x.fillRect(px - (long ? 2.5 : 1.5), 0, long ? 5 : 3, long ? 46 : 26); }
        var tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 16;
        var pos = [], uv = [], idx = [];
        for (var a = 0; a < pts.length; a++) {
          var uu = lens[a] / Ltot; pos.push(pts[a][0], pts[a][1], -Wt / 2, pts[a][0], pts[a][1], Wt / 2); uv.push(uu, 1, uu, 0);
          if (a) { var b0 = (a - 1) * 2; idx.push(b0, b0 + 2, b0 + 1, b0 + 1, b0 + 2, b0 + 3); }
        }
        var g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals();
        var tape = new THREE.Mesh(g, K.mat("wp-tape", { color: 0xffffff, map: tex, metalness: 0.55, roughness: 0.32, side: THREE.DoubleSide })); G.add(tape);
        var tags = [];
        [20, 80].forEach(function (ai) { var p = pts[ai]; var tg = TXT.roundedBox(0.03, 0.006, 0.022, 0.002, GOLD); tg.position.set(p[0], p[1] + 0.003, 0); G.add(tg); tags.push([p[0], p[1] + 0.006, 0]); });
        var end = pts[0], bob = TXT.lathe([[0, 0], [0.018, 0.02], [0.022, 0.05], [0.012, 0.09], [0.004, 0.1], [0, 0.1]], K.mat("wp-brass", { color: 0xb8893c, metalness: 0.85, roughness: 0.3 }));
        bob.rotation.x = Math.PI; bob.position.set(end[0], end[1], 0); G.add(bob);
        G.userData.tags = tags; G.userData.marks = M;
        return shade(G);
      }
    });
  };

  /* ---- helpers every frame uses ----------------------------------------------------------- */
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
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { color: 0xfbf7f0, shadowSize: size || 14, mapSize: map || 2048 }) });
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
  N.lightsOn = function (THREE, R, K, truck, o) {
    o = o || {};
    var lens = K.mat("v-lens", { color: 0xe9eef2, metalness: 0.95, roughness: 0.08 });
    lens.emissive = new THREE.Color(0xfff1d8); lens.emissiveIntensity = o.lens == null ? 6 : o.lens;
    truck.updateMatrixWorld(true);
    var inv = new THREE.Matrix4().copy(truck.matrixWorld).invert(), bb = new THREE.Box3().setFromObject(truck).applyMatrix4(inv);
    var zf = bb.max.z - 0.14, y0 = bb.min.y, out = [];
    [-1, 1].forEach(function (s) {
      [-0.075, 0.075].forEach(function (dx) {
        var p = new THREE.Vector3(s * 0.78 + dx, y0 + 1.52, zf).applyMatrix4(truck.matrixWorld); out.push(p);
        var g = new THREE.Sprite(new THREE.SpriteMaterial({ map: N.glowTex(THREE), color: 0xfff0d6, transparent: true, opacity: o.glow == null ? 0.85 : o.glow, depthWrite: false, fog: false }));
        g.scale.set(o.size || 0.55, o.size || 0.55, 1); g.position.copy(p).add(new THREE.Vector3(0, 0, 0.12).applyQuaternion(truck.getWorldQuaternion(new THREE.Quaternion()))); R.scene.add(g);
      });
    });
    if (o.beam !== false) {
      var q = truck.getWorldQuaternion(new THREE.Quaternion()), fwd = new THREE.Vector3(0, 0, 1).applyQuaternion(q);
      var c = out[0].clone().add(out[3]).multiplyScalar(0.5);
      var sp = new THREE.SpotLight(0xfff0d6, o.beam || 60, 40, 0.5, 0.6, 1.6); sp.position.copy(c).add(fwd.clone().multiplyScalar(0.3));
      sp.target.position.copy(c).add(fwd.clone().multiplyScalar(14)).setY(0); R.scene.add(sp); R.scene.add(sp.target);
    }
    return out;
  };
  /* THE FLOOD, ON: a glow at each head of a flood_pole and one spot from its height onto a target, so the pool the
   * staged world makes has a source a reader can see. The pole must not be rotated. */
  N.floodOn = function (THREE, R, pole, target, o) {
    o = o || {}; pole.updateMatrixWorld(true);
    var heads = (pole.userData.heads || []).map(function (h) { return new THREE.Vector3(h[0], h[1], h[2]).applyMatrix4(pole.matrixWorld); });
    heads.forEach(function (p) { N.lampGlow(THREE, R, [p.x, p.y - 0.15, p.z], 0xf2f5ff, o.glow || 2.2, 0); });
    if (!heads.length) return null;
    var c = heads[0].clone(); if (heads.length > 1) c.add(heads[heads.length - 1]).multiplyScalar(0.5);
    var sp = new THREE.SpotLight(0xeef2ff, o.intensity || 900, o.distance || 90, o.angle || 0.6, 0.55, 1.6);
    sp.position.copy(c); sp.target.position.set(target[0], target[1], target[2]); R.scene.add(sp); R.scene.add(sp.target);
    return sp;
  };
  /* THE DARK BAND THE TYPE STANDS IN. Light type on the dark field, and the band only ever DARKENS. */
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
