/* deck/2026-10-18-brush.js — the chassis for the 2026-10-18 deck: USDA's Kerrville laboratory built AI
 * models that pick where, when and how many sterile flies are released against New World screwworm,
 * while its drones fly over Texas herds and the state counts the premises the fly has reached
 * (tx-2026-0218).
 *
 * THE WORLD. lastLight, the house register: the sun just down, a near black sky, one warm seam low on
 * the key's side, each subject in a pool of light with the brush behind it gone dark. A rancher checks
 * stock at this hour, and the stage pool is the deck's argument, light on the place the response is
 * sent.
 *
 * THE LIGHT is azimuth -58, elevation 8. +x is east and +z is south, and az runs from +z toward +x,
 * so the key sits low to the south west of every subject, at (sin az, ., cos az): every lit face is
 * a south west face and every cast runs long to the north east. A frame that looks into the seam
 * looks south west. A
 * material relief (txbench.js) reads the same declaration from the top of its frame: the key comes
 * low from the upper left and every cast runs down and to the right.
 *
 * THE MATERIAL VOCABULARY. Red sandy loam on the ground, caliche on the roads, galvanized steel with
 * spangle for every windmill, tank, gate, wire and trap, waxed corrugated board for the release
 * boxes, mill aluminium for the trailer, Hill Country limestone on the stone frame, mesquite bark and
 * grey green leaf, Hereford red at silhouette distance. THE ACCENT is bluebonnet #4E5FA8 and means
 * one thing, what the response sends into the country: the pins (2), the trap's lid (4), the release
 * boxes' tape (5), the drone's lamp (7). The kit windmill's blue tail vane is repainted galvanized by
 * N.degalv so it never reads as the accent.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `screwworm_fly`, `fly_trap`,
 * `release_aircraft`, `release_box`, `survey_drone` and `stock_trailer`. Each is built in the kit's
 * conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 * Every one is drawn to illustrate and to no maker's or agency's design.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way
 * type is seated. Every frame composes its own picture, and the figures a frame draws are written in
 * that frame's own code where figure_bearing.py reads them. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("brush.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "brush",
    light: { az: -58, el: 8 },
    sky: "lastLight",
    ground: "#08060F",
    material: "#9AA0A3",
    accent: "#4E5FA8",
    grade: {
      exposure: 0,
      saturation: 1.03,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.002, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.96, strength: 0.05, radius: 8 },
      grain: { amount: 0.018, size: 2, seed: 20261018 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261018;
  N.ACCENT = 0x4e5fa8;   /* bluebonnet, brand.yaml's soft blue, the one cool hue in a warm brush palette */
  N.INK = "#ECE6DA";
  N.LOAM = 0x7a5236;
  N.LEAF = 0x6e7a5a;

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  N.canvasTex = function (THREE, key, w, h, paint, repeat) {
    N._tex = N._tex || {};
    if (N._tex[key]) return N._tex[key];
    var c = document.createElement("canvas"); c.width = w; c.height = h; paint(c.getContext("2d"), w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
    N._tex[key] = t; return t;
  };

  N.accentMat = function (THREE, glow) {
    var k = "_acc" + (glow || 0);
    if (N[k]) return N[k];
    N[k] = new THREE.MeshStandardMaterial({ color: new THREE.Color(N.ACCENT), roughness: 0.35, metalness: 0.1,
      emissive: new THREE.Color(N.ACCENT), emissiveIntensity: glow == null ? 0.35 : glow });
    return N[k];
  };

  /* THE KIT WINDMILL'S TAIL VANE is painted a saturated blue, which in this deck would read as the
   * accent. Any blue paint on a model passed here becomes weathered galvanized. */
  N.degalv = function (THREE, obj) {
    /* half metal and rough, so a blade facing the navy sky does not mirror it back as the accent */
    var galv = new THREE.MeshStandardMaterial({ color: 0x8f9396, metalness: 0.45, roughness: 0.62 });
    obj.traverse(function (m) {
      if (!m.isMesh || !m.material || !m.material.color) return;
      var c = m.material.color, hsl = {}; c.getHSL(hsl);
      if (hsl.h > 0.5 && hsl.h < 0.78 && hsl.s > 0.08) m.material = galv;
      else if (m.material.metalness > 0.6) m.material = galv;
    });
    return obj;
  };

  /* THE FLY'S THORAX: a metallic blue green field with three dark longitudinal stripes, and a faint
   * cross banding on the abdomen. Painted once and wrapped on the ellipsoids' UVs. */
  N.thoraxTex = function (THREE) {
    return N.canvasTex(THREE, "thorax", 512, 256, function (x, w, h) {
      var g = x.createLinearGradient(0, 0, 0, h);
      g.addColorStop(0, "#1f5a58"); g.addColorStop(0.5, "#2c7a70"); g.addColorStop(1, "#1a4c4a");
      x.fillStyle = g; x.fillRect(0, 0, w, h);
      [0.22, 0.5, 0.78].forEach(function (f) { x.fillStyle = "rgba(6,12,14,0.85)"; x.fillRect(f * w - w * 0.035, 0, w * 0.07, h); });
      var r = lcg(11);
      for (var i = 0; i < 900; i++) { x.fillStyle = "rgba(0,0,0," + (0.15 + r() * 0.25).toFixed(2) + ")"; x.fillRect(r() * w, r() * h, 1.5, 1.5); }
    });
  };
  N.eyeTex = function (THREE) {
    return N.canvasTex(THREE, "eye", 256, 256, function (x, w, h) {
      x.fillStyle = "#a8341c"; x.fillRect(0, 0, w, h);
      for (var j = 0; j < 22; j++) for (var i = 0; i < 26; i++) {
        var cx0 = i * 10 + (j % 2 ? 5 : 0), cy0 = j * 12;
        x.beginPath(); x.arc(cx0, cy0, 4.2, 0, Math.PI * 2); x.fillStyle = (i + j) % 3 ? "#c4482a" : "#b23e22"; x.fill();
      }
    });
  };
  N.wingTex = function (THREE) {
    return N.canvasTex(THREE, "wing", 512, 256, function (x, w, h) {
      x.clearRect(0, 0, w, h);
      x.fillStyle = "rgba(210,220,225,0.16)"; x.beginPath(); x.ellipse(w * 0.5, h * 0.5, w * 0.49, h * 0.42, 0, 0, Math.PI * 2); x.fill();
      x.strokeStyle = "rgba(40,34,30,0.9)"; x.lineWidth = 3;
      [[0.04, 0.5, 0.97, 0.36], [0.04, 0.5, 0.95, 0.5], [0.04, 0.52, 0.9, 0.68], [0.1, 0.55, 0.7, 0.82], [0.2, 0.42, 0.85, 0.2]].forEach(function (v) {
        x.beginPath(); x.moveTo(v[0] * w, v[1] * h); x.quadraticCurveTo(w * 0.5, (v[1] + v[3]) * 0.5 * h, v[2] * w, v[3] * h); x.stroke();
      });
      x.lineWidth = 2;
      [[0.45, 0.4, 0.5, 0.62], [0.68, 0.38, 0.72, 0.6]].forEach(function (v) { x.beginPath(); x.moveTo(v[0] * w, v[1] * h); x.lineTo(v[2] * w, v[3] * h); x.stroke(); });
      x.strokeStyle = "rgba(40,34,30,0.7)"; x.lineWidth = 2.5; x.beginPath(); x.ellipse(w * 0.5, h * 0.5, w * 0.49, h * 0.42, 0, 0, Math.PI * 2); x.stroke();
    });
  };
  N.boardTex = function (THREE) {
    return N.canvasTex(THREE, "board", 256, 256, function (x, w, h) {
      x.fillStyle = "#b39a76"; x.fillRect(0, 0, w, h);
      var r = lcg(5);
      for (var i = 0; i < 40; i++) { x.fillStyle = "rgba(90,70,45," + (0.05 + r() * 0.08).toFixed(2) + ")"; x.fillRect(0, r() * h, w, 2 + r() * 4); }
      for (var j = 0; j < 500; j++) { x.fillStyle = "rgba(60,45,30," + (r() * 0.12).toFixed(2) + ")"; x.fillRect(r() * w, r() * h, 2, 2); }
    }, true);
  };

  N.installKit = function (K, THREE, TXT) {
    if (K.registry.screwworm_fly) return;
    var galv = K.finish.galvanized();

    /* THE SCREWWORM FLY, at true size, head on +z. About 9.5 mm long: a head carried by two orange
     * red compound eyes, a metallic blue green thorax with three dark stripes, a rounded abdomen,
     * two veined wings folded back over the abdomen at a spread, six jointed legs and short dark
     * bristles. `legs` is the height of the feet below the thorax centre, so a frame can seat it on
     * a wire. Drawn to illustrate from no specimen. */
    K.define("screwworm_fly", {
      size: [0.012, 0.006, 0.011],
      options: { spread: 0.42, seed: 3 },
      note: "An illustrative New World screwworm fly at true size, about 9.5 mm: compound eyes, a striped metallic blue green thorax, veined transmissive wings, six legs, bristles. Feet at y 0.",
      make: function (o, r) {
        var g = new THREE.Group(), S = 0.001;
        var body = K.mat("sw-body", { color: 0xffffff, map: N.thoraxTex(THREE), metalness: 0.75, roughness: 0.28,
          clearcoat: 1, clearcoatRoughness: 0.12, iridescence: 0.5, iridescenceIOR: 1.4 }, true);
        var dark = K.mat("sw-dark", { color: 0x0c1112, metalness: 0.4, roughness: 0.45 });
        var eye = K.mat("sw-eye", { color: 0xffffff, map: N.eyeTex(THREE), roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05 }, true);
        var face = K.mat("sw-face", { color: 0xc9a46a, roughness: 0.55 });
        var wing = new THREE.MeshPhysicalMaterial({ map: N.wingTex(THREE), transparent: true, side: THREE.DoubleSide,
          roughness: 0.15, metalness: 0.0, transmission: 0.0, opacity: 1, depthWrite: false, iridescence: 0.6,
          iridescenceIOR: 1.3, clearcoat: 0.6 });
        var y0 = 2.6 * S;
        function ell(rx, ry, rz, mat, x, y, z) { var m = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), mat); m.scale.set(rx, ry, rz); m.position.set(x, y, z); g.add(m); return m; }
        ell(1.55 * S, 1.45 * S, 1.9 * S, body, 0, y0 + 0.2 * S, 0.4 * S);                    /* thorax */
        ell(1.6 * S, 1.3 * S, 2.3 * S, body, 0, y0 - 0.1 * S, -2.9 * S).rotation.x = -0.12;   /* abdomen */
        ell(1.5 * S, 1.25 * S, 0.9 * S, face, 0, y0 + 0.1 * S, 2.65 * S);                     /* head */
        [-1, 1].forEach(function (sx) { var e = ell(0.95 * S, 1.15 * S, 0.8 * S, eye, sx * 0.85 * S, y0 + 0.35 * S, 2.95 * S); e.rotation.y = sx * 0.35; });
        /* wings, from the thorax's shoulders back over the abdomen, opened by `spread` */
        [-1, 1].forEach(function (sx) {
          var wg = new THREE.Mesh(new THREE.PlaneGeometry(6.4 * S, 2.6 * S), wing);
          var piv = new THREE.Group(); piv.position.set(sx * 0.9 * S, y0 + 1.25 * S, 1.0 * S);
          wg.position.set(sx * 3.0 * S, 0, 0); wg.rotation.x = -Math.PI / 2; piv.add(wg);
          piv.rotation.y = sx * (Math.PI / 2 + o.spread); piv.rotation.z = sx * 0.12; g.add(piv);
        });
        /* legs: three pairs, femur up and out, tibia down to the foot at y 0 */
        var legMat = dark;
        [[1.6, 2.2], [0.3, 2.8], [-1.0, 2.6]].forEach(function (p, i) {
          [-1, 1].forEach(function (sx) {
            var hip = [sx * 1.0 * S, y0 - 0.6 * S, p[0] * S];
            var knee = [sx * p[1] * S, y0 + 0.9 * S, (p[0] + (i === 0 ? 1.2 : i === 2 ? -1.4 : 0)) * S];
            var foot = [sx * (p[1] + 0.8) * S, 0.05 * S, (p[0] + (i === 0 ? 2.2 : i === 2 ? -2.6 : 0.2)) * S];
            K.bar(hip, knee, 0.16 * S, legMat, 6, g); K.bar(knee, foot, 0.12 * S, legMat, 6, g);
          });
        });
        /* bristles on the thorax and abdomen */
        var br = new THREE.CylinderGeometry(0.03 * S, 0.06 * S, 0.7 * S, 4), list = [];
        for (var i = 0; i < 140; i++) {
          var th = r() * Math.PI * 2, ph = r() * Math.PI * 0.5, onAb = i % 2;
          var rx = onAb ? 1.6 : 1.55, rz = onAb ? 2.3 : 1.9, cz = onAb ? -2.9 : 0.4;
          list.push([Math.cos(th) * Math.sin(ph) * rx * S, y0 + Math.cos(ph) * 1.4 * S, cz * S + Math.sin(th) * Math.sin(ph) * rz * S, r() * 3, 1]);
        }
        K.instances(br, dark, list, g);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A FLY TRAP, drawn to no agency's design: a clear bait canister 0.28 m tall under a funnel lid
     * in the accent, hung on a wire hook. Origin at the hook's top, so a frame hangs it on a post. */
    K.define("fly_trap", {
      size: [0.2, 0.42, 0.2],
      anchor: "base",
      options: { seed: 1 },
      note: "An illustrative screwworm fly trap: a clear bait canister under a bluebonnet funnel lid on a wire hook.",
      make: function (o, r) {
        var g = new THREE.Group();
        var clear = K.mat("trap-clear", { color: 0xcfd8d6, roughness: 0.08, metalness: 0, transmission: 0.6, thickness: 0.004, transparent: true, opacity: 0.55, clearcoat: 1 }, true);
        var bait = K.mat("trap-bait", { color: 0x5a3a1c, roughness: 0.6 });
        var lid = N.accentMat(THREE, 0.25);
        K.cyl(0.075, 0.075, 0.26, clear, 0, 0.02, 0, 32, g);
        K.cyl(0.07, 0.07, 0.06, bait, 0, 0.025, 0, 24, g);
        K.cyl(0.03, 0.095, 0.07, lid, 0, 0.28, 0, 32, g);
        K.cyl(0.095, 0.095, 0.015, lid, 0, 0.275, 0, 32, g);
        K.bar([0, 0.35, 0], [0, 0.42, 0], 0.003, galv, 6, g);
        K.bar([0, 0.42, 0], [0, 0.42, -0.06], 0.003, galv, 6, g);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A RELEASE AIRCRAFT, a high wing single drawn to no maker's design: 8.3 m long, 11 m span,
     * fixed gear, wing struts, a prop disc. Seen only as a silhouette against the seam. */
    K.define("release_aircraft", {
      size: [11, 2.7, 8.3],
      options: { seed: 1 },
      note: "An illustrative high wing single engine aircraft, 8.3 m long, 11 m span, for a silhouette against the sky.",
      make: function (o, r) {
        var g = new THREE.Group();
        var paint = K.mat("ac-paint", { color: 0xd8d4cc, roughness: 0.4, metalness: 0.2 });
        var prof = [[0, -4.2], [0.18, -4.0], [0.42, -3.0], [0.62, -1.0], [0.66, 0.6], [0.6, 2.4], [0.45, 3.4], [0.2, 3.9], [0, 4.1]];
        var fus = TXT.lathe(prof.map(function (p) { return [p[0], p[1]]; }), paint, { segments: 24 });
        fus.rotation.x = Math.PI / 2; fus.position.y = 1.45; g.add(fus);
        var wingM = TXT.roundedBox(11, 0.16, 1.6, 0.06, paint); wingM.position.set(0, 2.25, 0.8); g.add(wingM);
        [-1, 1].forEach(function (sx) { K.bar([sx * 0.55, 1.1, 0.8], [sx * 3.2, 2.2, 0.8], 0.04, paint, 6, g); K.bar([0, 0.45, 1.6], [sx * 1.1, 0.0, 1.5], 0.04, paint, 6, g); K.cyl(0.28, 0.28, 0.14, K.finish.rubber(), sx * 1.1, -0.2, 1.5, 16, g).rotation.z = Math.PI / 2; });
        var tail = TXT.extrude([[0, 0], [1.6, 0], [1.9, 1.7], [1.2, 1.7]], 0.08, paint); tail.rotation.y = Math.PI / 2; tail.position.set(0.04, 1.6, -3.7); g.add(tail);
        var hs = TXT.roundedBox(3.4, 0.08, 0.9, 0.03, paint); hs.position.set(0, 1.62, -3.6); g.add(hs);
        var prop = new THREE.Mesh(new THREE.CircleGeometry(0.95, 32), K.mat("ac-prop", { color: 0x111111, transparent: true, opacity: 0.35, roughness: 0.5 }));
        prop.position.set(0, 1.45, 4.15); g.add(prop);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; } });
        return g;
      }
    });

    /* A RELEASE BOX, the deck's unit of a million sterile flies a week: a waxed corrugated carton
     * 0.60 x 0.45 x 0.45 m with a taped seam and one band in the accent. The size is a unit of the
     * drawing, not any program's packaging. */
    K.define("release_box", {
      size: [0.6, 0.47, 0.45],
      options: { seed: 1 },
      note: "An illustrative waxed corrugated carton, 0.60 x 0.45 x 0.45 m: bevelled corrugated edges, a centre flap seam taped across, a wax sheen and a bluebonnet band.",
      make: function (o, r) {
        var g = new THREE.Group();
        var tint = 0.92 + r() * 0.12;
        var board = K.mat("box-board" + Math.round(tint * 20), { color: new THREE.Color(0.6 * tint, 0.45 * tint, 0.28 * tint), roughness: 0.72, clearcoat: 0.22, clearcoatRoughness: 0.5 }, true);
        var edge = K.mat("box-edge", { color: 0x6e5636, roughness: 0.8 });
        var tape = K.mat("box-tape", { color: 0xd9cba6, roughness: 0.3, clearcoat: 0.6 }, true);
        K.box(0.6, 0.45, 0.45, board, 0, 0, 0, 0.03, g);
        /* the top flaps meet on a seam across the box, a dark corrugated line under the tape */
        K.box(0.6, 0.006, 0.012, edge, 0, 0.447, 0, 0, g);
        K.box(0.62, 0.008, 0.07, tape, 0, 0.449, 0, 0.002, g);
        /* the corrugated edges show on the bevel as a darker lip */
        [-1, 1].forEach(function (sx) { K.box(0.006, 0.43, 0.43, edge, sx * 0.299, 0.01, 0, 0, g); });
        K.box(0.045, 0.46, 0.46, N.accentMat(THREE, 0.45), 0.17, -0.003, 0, 0.004, g);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A SURVEY DRONE, a quadcopter drawn to no maker's design: 1.1 m across the rotors, a body
     * 0.34 x 0.13 x 0.24 m, carbon arms, blurred rotor discs, a gimbal ball, T skids and a lamp in
     * the accent. */
    K.define("survey_drone", {
      size: [1.1, 0.42, 1.1],
      options: { seed: 1 },
      note: "An illustrative survey quadcopter, 1.1 m across, with a gimbal camera and a bluebonnet lamp.",
      make: function (o, r) {
        var g = new THREE.Group();
        var carbon = K.mat("dr-carbon", { color: 0x15171a, roughness: 0.35, metalness: 0.3 });
        var shell = K.mat("dr-shell", { color: 0x2a2d31, roughness: 0.3, metalness: 0.2, clearcoat: 0.7 }, true);
        var disc = K.mat("dr-disc", { color: 0x0e0f10, transparent: true, opacity: 0.32, roughness: 0.5 });
        var body = TXT.roundedBox(0.34, 0.13, 0.24, 0.03, shell); body.position.y = 0.3; g.add(body);
        [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (p) {
          var tip = [p[0] * 0.39, 0.33, p[1] * 0.39];
          K.bar([p[0] * 0.1, 0.32, p[1] * 0.08], tip, 0.018, carbon, 8, g);
          K.cyl(0.035, 0.035, 0.06, carbon, tip[0], 0.32, tip[2], 16, g);
          var d = new THREE.Mesh(new THREE.CircleGeometry(0.265, 40), disc); d.rotation.x = -Math.PI / 2; d.position.set(tip[0], 0.39, tip[2]); g.add(d);
        });
        var ball = new THREE.Mesh(new THREE.SphereGeometry(0.045, 24, 16), shell); ball.position.set(0, 0.2, 0.1); g.add(ball);
        var lens = new THREE.Mesh(new THREE.CircleGeometry(0.02, 20), K.finish.glass(0x101820)); lens.position.set(0, 0.2, 0.146); g.add(lens);
        [-1, 1].forEach(function (sx) { K.bar([sx * 0.1, 0.24, 0], [sx * 0.14, 0.02, 0], 0.008, carbon, 6, g); K.bar([sx * 0.14, 0.02, -0.12], [sx * 0.14, 0.02, 0.12], 0.008, carbon, 6, g); });
        var lamp = new THREE.Mesh(new THREE.SphereGeometry(0.022, 16, 12), N.accentMat(THREE, 3.0)); lamp.position.set(0, 0.24, -0.12); g.add(lamp);
        g.userData.lamp = lamp;
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; } });
        return g;
      }
    });

    /* A GOOSENECK STOCK TRAILER, drawn to no maker's design: a 7.3 m bed, 2.1 m wide, 2.0 m inside
     * height, mill aluminium sides of horizontal slats with 0.10 m openings, a gooseneck over the
     * hitch, tandem axles, a rear swing gate. `gate` 0 shut, 1 open. Front (the gooseneck) on +z. */
    K.define("stock_trailer", {
      size: [2.3, 2.9, 9.6],
      options: { gate: 0, seed: 1 },
      note: "An illustrative gooseneck aluminium stock trailer, 7.3 m bed, slatted sides, tandem axles, rear swing gate.",
      make: function (o, r) {
        var g = new THREE.Group();
        var alu = K.mat("st-alu", { color: 0xb9bcbd, metalness: 0.75, roughness: 0.38 });
        var frame = K.mat("st-frame", { color: 0x2a2b2c, metalness: 0.5, roughness: 0.6 });
        var floorM = K.mat("st-floor", { color: 0x3a3632, roughness: 0.9 });
        var L = 7.3, Wd = 2.1, H = 2.0, base = 0.62, zb = -L / 2;
        K.box(Wd + 0.1, 0.12, L, frame, 0, base - 0.12, 0, 0, g);
        K.box(Wd, 0.04, L, floorM, 0, base, 0, 0, g);
        /* side slats: solid lower skirt, then slats with 0.10 m openings to the top rail */
        [-1, 1].forEach(function (sx) {
          var x = sx * Wd / 2;
          K.box(0.03, 0.55, L, alu, x, base, 0, 0, g);
          for (var y = base + 0.65; y < base + H - 0.1; y += 0.22) K.box(0.03, 0.12, L, alu, x, y, 0, 0.01, g);
          K.box(0.05, 0.08, L, alu, x, base + H - 0.08, 0, 0.015, g);
          for (var z = zb; z <= L / 2 + 0.01; z += L / 6) K.box(0.06, H, 0.06, alu, x, base, z, 0, g);
          /* fenders and tandem wheels */
          K.box(0.3, 0.06, 1.9, alu, sx * (Wd / 2 + 0.12), base - 0.02, zb + 1.8, 0.02, g);
          [zb + 1.35, zb + 2.25].forEach(function (zw) {
            var t = K.cyl(0.37, 0.37, 0.24, K.finish.rubber(), sx * (Wd / 2 - 0.05), 0, zw, 28, g); t.rotation.z = Math.PI / 2; t.position.y = 0.37;
            var hub = K.cyl(0.18, 0.18, 0.25, alu, sx * (Wd / 2 - 0.05), 0, zw, 20, g); hub.rotation.z = Math.PI / 2; hub.position.y = 0.37;
          });
        });
        /* roof rails and the front nose */
        for (var k = 0; k < 4; k++) K.box(Wd, 0.04, 0.06, alu, 0, base + H, zb + 0.4 + k * 2.1, 0, g);
        K.box(Wd, H, 0.04, alu, 0, base, L / 2, 0.01, g);
        /* the gooseneck: a raised deck over the hitch */
        K.box(Wd, 0.9, 1.7, alu, 0, base + H - 0.9, L / 2 + 0.85, 0.03, g);
        K.box(0.22, 0.9, 0.22, frame, 0, base + H - 1.8, L / 2 + 1.5, 0, g);
        /* the rear swing gate */
        var gate = new THREE.Group(); gate.position.set(-Wd / 2, 0, zb);
        for (var yg = base + 0.1; yg < base + H - 0.1; yg += 0.22) K.box(Wd, 0.12, 0.03, alu, Wd / 2, yg, 0, 0.01, gate);
        K.box(0.06, H, 0.06, alu, 0.03, base, 0, 0, gate); K.box(0.06, H, 0.06, alu, Wd - 0.03, base, 0, 0, gate);
        gate.rotation.y = -(o.gate || 0) * Math.PI * 0.55; g.add(gate);
        /* amber clearance lamps along the top rails */
        var amber = K.finish.lamp(0xffa040, 4.0);
        [-1, 1].forEach(function (sx) { [zb + 0.3, 0, L / 2 - 0.3].forEach(function (z) { K.box(0.03, 0.05, 0.1, amber, sx * (Wd / 2 + 0.03), base + H - 0.16, z, 0, g); }); });
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });
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
  /* Linear albedo per material id, with tooth so no surface is a flat fill. The flats stay dark,
   * so under the el 8 key only the walls facing it and the specular go bright. */
  N.M = { VOID: 0, PLATE: 1, RIM: 2, LOAM: 3, PIN: 4, RIVER: 5, STONE: 6, CUT: 7, BASALT: 8 };
  var BASE = {
    0: [0.004, 0.0035, 0.007],
    1: [0.075, 0.060, 0.045],
    2: [0.30, 0.31, 0.32],
    3: [0.20, 0.075, 0.035],
    4: [0.075, 0.094, 0.39],
    5: [0.010, 0.012, 0.016],
    6: [0.20, 0.18, 0.15],
    7: [0.11, 0.095, 0.075],
    8: [0.018, 0.016, 0.020]
  };
  N.SPEC = { 2: [0.55, 38], 4: [0.6, 60], 5: [0.7, 80], 6: [0.12, 10], 7: [0.08, 8], 1: [0.08, 10], 3: [0.12, 14] };
  N.albedo = function (X, Y, m) {
    var b = BASE[m] || BASE[0], n = global.TX && TX.simplex2 ? TX.simplex2(X * 0.07, Y * 0.07) * 0.5 + TX.simplex2(X * 0.31, Y * 0.31) * 0.25 : 0;
    var k = 1 + 0.18 * n;
    return [b[0] * k, b[1] * k, b[2] * k];
  };

  global.CH = N;
})(this);
