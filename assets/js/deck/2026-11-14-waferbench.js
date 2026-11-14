/* deck/2026-11-14-waferbench.js — the chassis for the 2026-11-14 deck: the Texas Semiconductor Innovation Fund's award of
 * over $19 million to Texas Tech for an AI computing cluster in Lubbock (tx-2026-0247), beside the fund's January award of
 * $12 million toward a clean room the university matched and its May award of roughly $4.5 million.
 *
 * THE VISUAL ARGUMENT. One wafer stands for $1 million (figures.json usd_m_per_wafer, a drawing unit). The awards are boats
 * of wafers on one black lab bench at one pitch. An exact award is a boat capped at both ends. Roughly is whole wafers and a
 * cleaved one. Over is a boat with no far end wall. Every count a frame draws is read from figures.json in that frame's own
 * code. The chassis types no figure.
 *
 * THE WORLD. floodlit, STAGED, and indoors. One cold LED flood hangs high on the LEFT, azimuth -58 and elevation 28, so every
 * lit face looks left and up and every cast runs down and to the RIGHT across the bench. The lab is dark around that one
 * source. A warm strip low on the back wall sits behind the clear quartz and the mirror wafers, because glass on a dark field
 * shows nothing unless something lit stands behind it. TXBENCH reliefs read the same declaration.
 *
 * THE ACCENT. dusk_gold #E0956A means ONE thing: the November award. The strip behind the November boat, the city pad that
 * receives it, the unjoined islands of the layer the cluster is for, and the one stamped field on the nameplate.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them, in the kit's conventions (metres, y up, origin on the ground
 * at the footprint centre, front on +z) so Phase 17 can queue the lift: `wafer` (a 200 mm polished silicon wafer with an
 * edge bevel and an orientation notch, whole or cleaved in half along a straight edge), `wafer_boat` (four rods and slotted
 * end walls in clear fused quartz or matte silicon carbide, capped at both ends or at the near end only) and `lab_bench`
 * (a black epoxy resin top with a rounded nosing on a steel frame).
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("waferbench.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "waferbench",
    light: { az: -58, el: 28 },
    sky: { preset: "floodlit" },
    ground: "#0E0E11",
    material: "#6E6A78",
    accent: "#E0956A",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.06, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.2,
      bloom: { threshold: 0.88, strength: 0.12, radius: 6 },
      grain: { amount: 0.014, size: 2, seed: 20261114 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261114; N.INK = "#EDE6D6";
  N.GOLD = 0xE0956A;          /* dusk_gold: the November award, and nothing else */
  N.BENCH_H = 0.9;            /* the bench top's height above the floor, metres */
  N.WAFER = { d: 0.2, t: 0.000725 };   /* figures.json wafer_mm carries the diameter a frame checks against */

  /* a seeded canvas texture, so every surface carries tooth in its albedo and never in its height */
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };


  /* THE THREE MODELS. A frame calls N.installKit once after initKit, then K.make('wafer'), K.make('wafer_boat') and
   * K.make('lab_bench') like any kit model. */
  N.mats = function (THREE) {
    if (N._m) return N._m;
    var scr = N.canvasTex(THREE, 1024, 512, function (g, w, h) {
      g.fillStyle = "#808080"; g.fillRect(0, 0, w, h); var r = N.rng(21);
      for (var i = 0; i < 2600; i++) { var x = r() * w, y = r() * h, a = r() * Math.PI, l = 4 + r() * 70;
        g.strokeStyle = "rgba(" + (r() < 0.5 ? "40,40,40" : "200,200,200") + "," + (0.05 + r() * 0.12) + ")"; g.lineWidth = 0.4 + r() * 0.8;
        g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l * 0.2); g.stroke(); }
    }, [2, 1]);
    /* THE FILM ON THE FACE: one soft colour sweep across the polish where the grown film's thickness drifts, and a faint haze.
     * Albedo only, mapped to the wafer's own metres. */
    var sil = N.canvasTex(THREE, 512, 512, function (g, w, h) {
      var gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, "#c3bfd2"); gr.addColorStop(0.55, "#b5b8c6"); gr.addColorStop(1, "#aab3be"); g.fillStyle = gr; g.fillRect(0, 0, w, h);
      var r = N.rng(31); for (var q = 0; q < 900; q++) { g.fillStyle = "rgba(" + (r() < 0.5 ? "120,115,140" : "215,220,230") + ",0.2)"; g.beginPath(); g.arc(r() * w, r() * h, 3 + r() * 18, 0, Math.PI * 2); g.fill(); }
    });
    sil.repeat.set(5, 5); sil.offset.set(0.5, 0.5); sil.wrapS = sil.wrapT = THREE.ClampToEdgeWrapping;
    N._m = {
      silicon: new THREE.MeshPhysicalMaterial({ color: 0x9aa1b4, map: sil, roughnessMap: sil, metalness: 0.9, roughness: 0.16, clearcoat: 1, clearcoatRoughness: 0.02,
        iridescence: 0.18, iridescenceIOR: 1.8, iridescenceThicknessRange: [300, 520] }),
      bevel: new THREE.MeshStandardMaterial({ color: 0xe8ecf4, metalness: 0.9, roughness: 0.18 }),
      cleave: new THREE.MeshStandardMaterial({ color: 0x5d5a66, metalness: 0.5, roughness: 0.32 }),
      quartz: new THREE.MeshPhysicalMaterial({ color: 0xd8eef5, metalness: 0, roughness: 0.04, transparent: true, opacity: 0.32, depthWrite: false,
        clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 2.2, specularIntensity: 1, ior: 1.46 }),
      sic: new THREE.MeshStandardMaterial({ color: 0x2c2c31, metalness: 0.15, roughness: 0.52 }),
      epoxy: new THREE.MeshPhysicalMaterial({ color: 0x2a282e, map: scr, roughness: 0.3, roughnessMap: scr, metalness: 0, clearcoat: 0.5, clearcoatRoughness: 0.25 }),
      steel: new THREE.MeshStandardMaterial({ color: 0x3a3c40, metalness: 0.6, roughness: 0.45 }),
      gold: new THREE.MeshBasicMaterial({ color: N.GOLD, toneMapped: false, fog: false })
    };
    return N._m;
  };
  /* a wafer's outline in its own plane: a circle of radius r with a 3 mm orientation notch at the bottom, or the half above a
   * straight cleave through the centre when `half`, keeping the lower half */
  N.waferShape = function (THREE, r, half) {
    var s = new THREE.Shape(), n = 160, i, a;
    if (half) {
      s.moveTo(-r, 0);
      for (i = 1; i <= n; i++) { a = Math.PI + Math.PI * i / n; s.lineTo(Math.cos(a) * r, Math.sin(a) * r); }
      s.lineTo(-r, 0); return s;   /* the LOWER half, so it rests on the rods with its straight cleave on top */
    }
    var na = 0.016;   /* the notch, about 3 mm across at the rim */
    s.moveTo(Math.cos(-Math.PI / 2 + na) * r, Math.sin(-Math.PI / 2 + na) * r);
    for (i = 1; i <= n; i++) { a = -Math.PI / 2 + na + (2 * Math.PI - 2 * na) * i / n; s.lineTo(Math.cos(a) * r, Math.sin(a) * r); }
    s.lineTo(0, -r + 0.003); s.closePath(); return s;
  };
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.wafer_boat) return;
    var M = N.mats(THREE);
    K.define("wafer", { size: [0.2, 0.2, 0.001], options: { d: 0.2, half: false }, note: "A 200 mm polished silicon wafer standing on edge, its face toward +z, origin at the bottom of the rim; half cleaves it straight through the centre and keeps the lower half, its raw cleave on top.",
      make: function (o) {
        var r = (o.d || N.WAFER.d) / 2, t = N.WAFER.t, g = new THREE.Group();
        var geo = new THREE.ExtrudeGeometry(N.waferShape(THREE, r, o.half), { depth: t, bevelEnabled: true, bevelThickness: 0.00012, bevelSize: 0.00025, bevelSegments: 2, curveSegments: 160 });
        geo.translate(0, 0, -t / 2);
        var m = new THREE.Mesh(geo, [M.silicon, o.half ? M.cleave : M.silicon]); m.castShadow = true; m.receiveShadow = true;
        m.position.y = r; g.add(m);
        if (o.half) { var arc = new THREE.Mesh(new THREE.TorusGeometry(r - 0.0002, 0.00042, 6, 80, Math.PI), M.bevel); arc.rotation.z = Math.PI; arc.position.y = r; g.add(arc);
          var lip = new THREE.Mesh(new THREE.BoxGeometry(2 * r, 0.0009, N.WAFER.t * 1.3), M.bevel); lip.position.y = r; g.add(lip); }
        if (o.half) {
          /* the raw cleave face: a strip of fine steps along the straight edge, darker and rougher than the polish */
          for (var k = 0; k < 7; k++) { var s = new THREE.Mesh(new THREE.BoxGeometry(2 * r * (0.92 - k * 0.11), 0.0006, t * 1.15), M.cleave);
            s.position.set((k % 2 ? 1 : -1) * r * 0.02 * k, r - 0.0003 - k * 0.00005, 0); s.castShadow = true; g.add(s); }
        }
        return g;
      } });
    K.define("wafer_boat", { size: [0.24, 0.13, 0.4], options: { count: 19, pitch: 0.016, material: "quartz", ends: "both", wafers: true, half: false, tail: 0.04, empty: 0 },
      note: "A wafer boat along z: four slotted rods and end walls with a wafer cut-out, in clear fused quartz or matte silicon carbide. count wafers at pitch metres, the first slot at the near end (+z). ends 'both' caps both ends, 'near' leaves the far end open with the rods running on by tail metres. half makes the last wafer a cleaved half. empty adds that many unfilled slots after the last wafer. userData.slotZ(i) gives a slot's z.",
      make: function (o) {
        var n = o.count, p = o.pitch || 0.016, mat = o.material === "sic" ? M.sic : M.quartz, g = new THREE.Group();
        var margin = 0.022, wall = 0.006, len = (n - 1 + (o.empty || 0)) * p + 2 * margin + (o.ends === "near" ? (o.tail || 0.04) : 0);
        var z0 = len / 2 - margin;             /* slot 0, nearest the camera end (+z) */
        var rods = [[-0.06, 0.03, 0.0065], [0.06, 0.03, 0.0065], [-0.094, 0.088, 0.006], [0.094, 0.088, 0.006]];
        rods.forEach(function (q) {
          var rod = new THREE.Mesh(new THREE.CylinderGeometry(q[2], q[2], len, 20), mat); rod.rotation.x = Math.PI / 2; rod.position.set(q[0], q[1], 0);
          rod.castShadow = true; rod.receiveShadow = true; g.add(rod);
        });
        function endWall(z) {
          var s = new THREE.Shape(); s.moveTo(-0.12, 0); s.lineTo(0.12, 0); s.lineTo(0.12, 0.13); s.lineTo(0.095, 0.13);
          var c = 0.112, r = 0.102; s.absarc(0, c, r, 0, -Math.PI, true); s.lineTo(-0.12, 0.13); s.closePath();
          /* the arc dips into the wall so a wafer reads seated through the cut-out */
          var geo = new THREE.ExtrudeGeometry(s, { depth: wall, bevelEnabled: true, bevelThickness: 0.0008, bevelSize: 0.0008, bevelSegments: 2, curveSegments: 48 });
          var m = new THREE.Mesh(geo, mat); m.position.set(0, 0, z - wall / 2); m.castShadow = true; m.receiveShadow = true; g.add(m);
          [-0.1, 0.1].forEach(function (x) { var f = K.box(0.03, 0.008, 0.02, mat, x, -0.008, z, 0.002); g.add(f); });
        }
        endWall(len / 2);
        if (o.ends !== "near") endWall(-len / 2);
        var wy = 0.03 + Math.sqrt(Math.pow(0.1 + 0.0065, 2) - 0.06 * 0.06) - 0.1;   /* the wafer's rim rests on the two bottom rods */
        g.userData.slotZ = function (i) { return z0 - i * p; };
        if (o.wafers !== false) for (var i = 0; i < n; i++) {
          var last = o.half && i === n - 1, w = K.make("wafer", { half: last, seed: i });
          w.position.set(0, wy, z0 - i * p); g.add(w);
        }
        g.position.y = 0.008;
        var outer = new THREE.Group(); outer.add(g); outer.userData.slotZ = g.userData.slotZ; outer.userData.len = len; outer.userData.z0 = z0;
        return outer;
      } });
    K.define("lab_bench", { size: [1.8, 0.9, 0.76], options: { w: 1.8, d: 0.76, h: 0.9 },
      note: "A lab bench, origin on the floor at its footprint centre: a 25 mm black epoxy resin top with a rounded nosing and fine scratches in its roughness, on a steel C frame. userData.top is the top's height.",
      make: function (o) {
        var w = o.w || 1.8, d = o.d || 0.76, h = o.h || N.BENCH_H, g = new THREE.Group();
        var top = TXT.roundedBox(w, 0.025, d, 0.006, M.epoxy); top.position.set(0, h - 0.0125, 0); top.castShadow = true; top.receiveShadow = true; g.add(top);
        [[-w / 2 + 0.06, 1], [w / 2 - 0.06, 1]].forEach(function (q) {
          g.add(K.box(0.05, h - 0.025, 0.05, M.steel, q[0], 0, d / 2 - 0.08, 0.004));
          g.add(K.box(0.05, h - 0.025, 0.05, M.steel, q[0], 0, -d / 2 + 0.08, 0.004));
          g.add(K.box(0.05, 0.05, d - 0.16, M.steel, q[0], h - 0.1, 0, 0.004));
        });
        g.add(K.box(w - 0.12, 0.06, 0.04, M.steel, 0, h - 0.09, d / 2 - 0.06, 0.004));
        g.userData.top = h; g.userData.keepOrigin = true; return g;
      } });
  };

  /* THE LAB: a dark room a few metres across with the bench against its back wall and the warm strip low on that wall,
   * behind where the boats stand. A frame calls TXT.interior itself through these options. */
  N.roomOpts = function (o) {
    o = o || {};
    return { w: o.w || 4.2, d: o.d || 3.2, h: 3.0, floor: "concrete", wall: o.wall || 0x16161b, window: null, ceiling: o.ceiling !== false, light: o.light == null ? 0.12 : o.light };
  };
  /* THE MIRROR'S WORLD: an environment map for the polished materials only (silicon, quartz), so a wafer face reflects the
   * flood's softbox high on the key's side and the warm strip low behind, while the room's walls stay dark. Same light as
   * the declared key: the softbox sits on azimuth -58 and elevation 28. */
  N.labEnv = function (THREE, R, o) {
    o = o || {};
    if (N._env && N._envR === R && !o.low && !o.auto) return N._env;
    var env = new THREE.Scene();
    env.add(new THREE.Mesh(new THREE.BoxGeometry(20, 12, 20), new THREE.MeshBasicMaterial({ color: 0x050608, side: THREE.BackSide })));
    function panel(w, h, c, i, pos) { var p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: c, side: THREE.DoubleSide }));
      p.material.color.multiplyScalar(i); p.position.set(pos[0], pos[1], pos[2]); p.lookAt(0, 0, 0); env.add(p); return p; }
    var az = -58 * Math.PI / 180, el = 28 * Math.PI / 180, d = 7;
    panel(4.5, 3, 0xeef2ff, o.soft || 5, [Math.sin(az) * Math.cos(el) * d, Math.sin(el) * d, Math.cos(az) * Math.cos(el) * d]);
    panel(16, 0.2, N.GOLD, (o.warm || 3.2) * 0.6, [0, 0.4, -8]);
    panel(0.3, 10, 0xdfe5f2, 1.4, [-8, 0.5, -2]);
    panel(5, 2, 0x6f86b8, o.cool || 0.6, [7, 2, 2]);
    panel(14, 0.5, 0xdfe5f2, o.bounce || 2.6, [-3, -2.6, -7]);   /* a narrow cool band low behind: the flood off the bench edge */
    panel(14, 0.1, N.GOLD, (o.warm || 3.2) * 0.5, [-3, -1.3, -7.2]);
    if (o.low) { panel(8, 2.2, 0xdfe5f2, o.low, [-1.4, -3.4, -6]); panel(8, 0.12, N.GOLD, 2.0, [-1.4, -2.2, -6.1]); }
    if (o.auto) {
      /* THE PANEL THE FACES SEE: the camera's ray off a wafer face (normal along x, toward the camera's side) mirrored into
       * the environment, with a soft cool panel there and a thin warm band above it, so each frame's faces carry a band */
      var c = R.camera.position, t = R._txLook || [0, 0, 0], dx = t[0] - c.x, dy = t[1] - c.y, dz = t[2] - c.z, L = Math.hypot(dx, dy, dz);
      dx /= L; dy /= L; dz /= L; var rx = -dx, ry = dy, rz = dz;   /* reflect off a face whose normal is along x */
      for (var b = -2; b <= 2; b++) panel(6, 0.32, 0xdfe5f2, o.auto * (1 - Math.abs(b) * 0.18), [rx * 7, ry * 7 + b * 0.62, rz * 7]);   /* light strips, as a lab ceiling reflects in a polished wafer */
      panel(6, 0.14, N.GOLD, 1.6, [rx * 7, ry * 7 + 1.5, rz * 7]);
    }   /* the warm strip, a sharp band */
    panel(14, 0.12, 0xdfe5f2, 2.0, [-3, -0.4, -7.2]);
    var pm = new THREE.PMREMGenerator(R.renderer), tex = pm.fromScene(env, 0.02).texture; pm.dispose();
    var M = N.mats(THREE);
    [M.silicon, M.quartz, M.cleave].forEach(function (m) { m.envMap = tex; m.envMapIntensity = o.intensity || 0.85; m.needsUpdate = true; });
    N._env = tex; N._envR = R; return tex;
  };
  /* a parallel camera `span` metres wide, for a frame that compares lengths and must not foreshorten them */
  N.ortho = function (THREE, R, span) { var w = span / 2, h = w * N.H / N.W; R.camera = new THREE.OrthographicCamera(-w, w, h, -h, 0.01, 40); return R.camera; };
  /* an SVG leader from a label's anchor to a world point, registered for qa's leader check */
  N.leader = function (THREE, R, from, world, what) {
    var at = N.project(THREE, R, world), s = N.svg(), l = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    l.setAttribute("points", from[0] + "," + from[1] + " " + at[0] + "," + at[1]); l.setAttribute("fill", "none"); l.setAttribute("stroke", "#D2D6DA"); l.setAttribute("stroke-width", "2");
    s.appendChild(l); (window.__txLeaders = window.__txLeaders || []).push({ target: what, at: at, to: at }); return at;
  };
  /* the side strip: a lit vertical band on the room's left wall at bench height, facing +x, so wafer faces turned to the
   * left reflect it toward a camera standing front left */
  N.sideStrip = function (THREE, R, x, z0, z1, y, hgt) {
    var m = new THREE.Mesh(new THREE.PlaneGeometry(z1 - z0, hgt || 0.05), N.mats(THREE).gold);
    m.rotation.y = Math.PI / 2; m.position.set(x, y, (z0 + z1) / 2); R.scene.add(m); return m;
  };
  /* the strip: a lit band on the back wall, x from x0 to x1 at height y, so it reflects in the mirror faces */
  N.strip = function (THREE, R, x0, x1, y, z, hgt) {
    var m = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, hgt || 0.035), N.mats(THREE).gold);
    m.position.set((x0 + x1) / 2, y, z); R.scene.add(m);
    var glow = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0 + 0.1, (hgt || 0.035) * 6), new THREE.MeshBasicMaterial({ color: N.GOLD, transparent: true, opacity: 0.12, toneMapped: false, fog: false, depthWrite: false }));
    glow.position.set((x0 + x1) / 2, y, z - 0.001); R.scene.add(glow);
    return m;
  };

  /* A CAMERA BEARING FROM THE SUN: the horizontal direction `deg` degrees clockwise (to the right) of the sun's own
   * bearing, so a frame can put the warm seam at its left edge by looking a little right of the sun. */
  N.bearing = function (TXT, deg) {
    var sd = TXT.sunDir(), hx = sd.x, hz = sd.z, n = Math.hypot(hx, hz) || 1; hx /= n; hz /= n;
    var a = -deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
    return [hx * c - hz * s, hz * c + hx * s];
  };
  N.dress = function (cx, o) { o = o || {}; N.post(cx, { a: 0.3, veil: 0.35, veilH: 240 }); N.footWash(cx, { a: o.foot || 0.6 }); N.typeDark(cx, { fade: o.fade == null ? 120 : o.fade, pad: o.pad, a: 0.6 }); return cx; };
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
    R.scene.environmentIntensity = o.env == null ? 0.12 : o.env;
    R.scene.traverse(function (l) { if (!l.isLight) return; if (l.isHemisphereLight || l.isAmbientLight) l.intensity *= (o.amb == null ? 0.35 : o.amb);
      else if (l.isDirectionalLight && !l.castShadow) l.intensity *= (o.fill == null ? 0.4 : o.fill); });
    return R;
  };

  /* THE TYPE BAND GOES TO THE DARK, darken only: a near black gradient from the top of the frame to just under the dek,
   * so the room's far edges behind the type sink rather than strike through it. */
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
})(this);
