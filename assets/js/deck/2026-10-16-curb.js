/* deck/2026-10-16-curb.js — the chassis for the 2026-10-16 deck: Waymo opens its San Antonio
 * robotaxi service to anyone with the app, San Antonio International Airport included, on October
 * 14th, 2026, while the federal recall for its flood behaviour still lists the remedy as under
 * development (tx-2026-0216).
 *
 * THE WORLD. nightSodium, tuned: a black sky, the city's glow low on one horizon, the key at LAMP
 * height. THE LIGHT is azimuth 40, elevation 34: the curb's overhead lamps stand to the south east
 * of the subject and high, so every lit face is a top or a south east face and every cast falls short
 * and to the north west. A robotaxi lives at the curb at night, under lamps, and the service is the
 * story, so the deck stands where a rider stands to hail one.
 *
 * DIRECTIONS. +x is east, +z is south. az runs from +z toward +x, so the key sits at
 * (sin az, ., cos az): with az 40 that is south south east of the subject and high.
 *
 * TWO PLACES, both drawn to illustrate. THE CURB: an airport departures curb, a concrete island under a
 * steel canopy, a glazed terminal wall lit from inside, bollards, wet asphalt. No real terminal is
 * claimed. THE CREEK: a limestone creek bank in north San Antonio after rain, live oaks and pecans,
 * brown water high in the channel. No crossing is named and no gauge stands in it.
 *
 * THE HERO OBJECT. One illustrative ROBOTAXI, built here as `robotaxi`: the kit's SUV body at 0.88
 * scale, 4.71 m long, white, under a roof housing that carries a cylindrical spinning sensor dome and
 * four perimeter sensor pods. It carries no logo and is drawn to no maker's design.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `robotaxi`, `terminal_curb`,
 * `standing_water`, `curb_bollard` (the deck's unit of one day) and `road_stud`. Each is built in the kit's conventions so Phase 17 can queue the lift.
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, written in the frame's code where figure_bearing.py
 * checks them against figures.json. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("curb.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "curb",
    light: { az: 40, el: 34 },
    sky: { preset: "nightSodium", haze: 0x0c1018, horizon: 0x111725, sun: 0x8a6440, horizonGlow: 0.12, glow: 0.12, stars: 0.5, fogDensity: 0.0025 },
    ground: "#07080C",
    material: "#E9ECEF",
    accent: "#2A7A9E",
    grade: {
      exposure: 0,
      saturation: 1.04,
      contrast: 1.08,
      filmic: true,
      lift: [0.002, 0.003, 0.006],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.24,
      bloom: { threshold: 0.97, strength: 0.04, radius: 8 },
      grain: { amount: 0.02, size: 2, seed: 20261016 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261016;
  N.ACCENT = 0x2a7a9e;   /* comal, brand.yaml's "the water itself", the blue green of the Edwards Aquifer water San
                              * Antonio stands on. It means ONE thing in this deck: the line where water meets the car or
                              * the record. Lit with a small emissive so it holds against the sodium key. */
  N.INK = "#ECE9E2";

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
  /* RIPPLES for standing water: a wrapped field of soft rings and streaks used as a bump map, so a
   * lamp's reflection on the water breaks into a lit smear rather than a mirror disc */
  N.rippleTex = function (THREE) {
    return N.canvasTex(THREE, "ripple", 512, 512, function (x, w, h) {
      var r = lcg(41); x.fillStyle = "#808080"; x.fillRect(0, 0, w, h);
      function at(fn) { for (var dx = -1; dx <= 1; dx++) for (var dy = -1; dy <= 1; dy++) fn(dx * w, dy * h); }
      for (var i = 0; i < 260; i++) { var cx0 = r() * w, cy0 = r() * h, rr = 6 + r() * 40, a = 0.05 + r() * 0.12; at(function (ox, oy) { x.strokeStyle = "rgba(" + (r() < 0.5 ? "255,255,255," : "0,0,0,") + a.toFixed(3) + ")"; x.lineWidth = 1 + r() * 2.5; x.beginPath(); x.ellipse(cx0 + ox, cy0 + oy, rr, rr * 0.55, 0, 0, Math.PI * 2); x.stroke(); }); }
      for (var j = 0; j < 900; j++) { x.fillStyle = "rgba(" + (r() < 0.5 ? "255,255,255," : "0,0,0,") + (0.04 + r() * 0.08).toFixed(3) + ")"; x.fillRect(r() * w, r() * h, 6 + r() * 30, 1 + r() * 1.5); }
    }, true);
  };
  /* THE TERMINAL'S LIT INTERIOR: a warm band of ceiling, a few columns and silhouetted queues, seen
   * through the glass, never a sign that could be read */
  N.lobbyTex = function (THREE) {
    return N.canvasTex(THREE, "lobby", 1024, 256, function (x, w, h) {
      var r = lcg(77), g = x.createLinearGradient(0, 0, 0, h);
      g.addColorStop(0, "#f3d9a8"); g.addColorStop(0.35, "#c79a62"); g.addColorStop(1, "#3a2a1c");
      x.fillStyle = g; x.fillRect(0, 0, w, h);
      for (var i = 0; i < 40; i++) { x.fillStyle = "rgba(255,240,210," + (0.25 + r() * 0.35).toFixed(2) + ")"; x.fillRect(r() * w, 8 + r() * 10, 40 + r() * 60, 5); }
      for (var c = 0; c < 9; c++) { x.fillStyle = "rgba(60,44,30,0.7)"; x.fillRect(c * w / 9 + 30, 30, 14, h - 30); }
      for (var p = 0; p < 70; p++) { var px = r() * w, ph = 46 + r() * 22; x.fillStyle = "rgba(30,22,18," + (0.55 + r() * 0.3).toFixed(2) + ")"; x.fillRect(px, h - ph - 20, 9 + r() * 5, ph); x.beginPath(); x.arc(px + 6, h - ph - 26, 7, 0, Math.PI * 2); x.fill(); }
    });
  };

  N.accentMat = function (THREE) {
    if (N._accentMat) return N._accentMat;
    N._accentMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(N.ACCENT), toneMapped: false, fog: false });
    return N._accentMat;
  };

  N.installKit = function (K, THREE, TXT) {
    if (K.registry.robotaxi) return;
    var gloss = K.mat("rt-gloss", { color: 0x0d0f12, roughness: 0.18, metalness: 0.2 });
    var dome = K.mat("rt-dome", { color: 0x0a0c10, roughness: 0.06, metalness: 0.1, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.6 }, true);
    var band = K.mat("rt-band", { color: 0x1c2026, roughness: 0.35, metalness: 0.6 });
    var white = K.mat("rt-white", { color: 0xeceef0, roughness: 0.32, metalness: 0.0, clearcoat: 0.8, clearcoatRoughness: 0.12 }, true);
    var lens = K.mat("rt-lens", { color: 0x050608, roughness: 0.04, metalness: 0.3 });

    /* THE ROBOTAXI, front on +z. An illustrative crossover on the kit SUV body at 0.88 scale (4.71 x
     * 1.81 x 1.67 m to the roof), painted white, with a roof housing 1.0 x 0.1 x 0.78 m carrying a
     * cylindrical sensor dome 0.34 m across and 0.3 m tall under a white cap, four perimeter pods at the
     * fender and quarter corners, and a front sensor bar in the grille. `dome` false omits the roof
     * stack. userData.dome is the dome's centre and userData.roofY the roof line, in the model frame. */
    K.define("robotaxi", {
      size: [2.12, 1.96, 4.71],
      options: { dome: true, seed: 4 },
      note: "An illustrative white robotaxi on the kit SUV body at 0.88 scale, 4.71 m: roof sensor housing with a cylindrical spinning sensor dome under a white cap, four perimeter sensor pods, a front sensor bar. No logo, drawn to no maker's design.",
      make: function (o, r) {
        var g = new THREE.Group();
        var body = K.make("suv", { rack: false, color: 0xeceef0, metallic: false, seed: o.seed });
        var s = 0.88, sy = 0.84; body.scale.set(s, sy, s); g.add(body);
        /* COATED GLASS. The kit SUV's dark glass prints as a black card at night, so the screen and side
         * panes take a coated glass that carries the world's lights, the treatment the kit's semi got on
         * 2026-10-05 (metalness stands in for the coating, kept under a mirror). */
        var coat = K.mat("rt-glass", { color: 0x5f6c75, metalness: 0.55, roughness: 0.05, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 2.4 }, true);
        body.traverse(function (m) { if (m.isMesh && m.material && m.material.color && m.material.color.getHex() === 0x1a232a) m.material = coat; });
        var roofY = 1.9 * sy, L = 5.35 * s, W = 2.06 * s;
        var stack = new THREE.Group();
        var base = TXT.roundedBox(1.0, 0.1, 0.78, 0.04, white); base.position.set(0, 0.05, 0); stack.add(base);
        var neck = K.cyl(0.12, 0.15, 0.08, gloss, 0, 0.1, 0, 28, stack);
        var dm = K.cyl(0.17, 0.17, 0.24, dome, 0, 0.18, 0, 40, stack);
        var ring = K.cyl(0.175, 0.175, 0.03, band, 0, 0.27, 0, 40, stack);
        var cap = K.cyl(0.19, 0.18, 0.06, white, 0, 0.42, 0, 40, stack);
        [-1, 1].forEach(function (sx) { var cam = TXT.roundedBox(0.1, 0.07, 0.12, 0.02, gloss); cam.position.set(sx * 0.42, 0.13, 0.28); stack.add(cam); var cl = new THREE.Mesh(new THREE.CircleGeometry(0.025, 20), lens); cl.position.set(sx * 0.42, 0.135, 0.341); stack.add(cl); });
        stack.position.set(0, roofY - 0.01, -0.25 * s); g.add(stack);
        /* the perimeter pods: a white shoulder on each front fender and rear quarter, a black glass face out */
        [[1, 1], [-1, 1], [1, -1], [-1, -1]].forEach(function (p) {
          var pod = new THREE.Group();
          var sh = TXT.roundedBox(0.16, 0.22, 0.2, 0.05, white); sh.position.set(0, 0.11, 0); pod.add(sh);
          var face = TXT.roundedBox(0.02, 0.15, 0.14, 0.01, gloss); face.position.set(p[0] * 0.085, 0.12, 0); pod.add(face);
          pod.position.set(p[0] * (W / 2 - 0.02), p[1] > 0 ? 1.16 * sy : 1.12 * sy, p[1] * (L / 2 - (p[1] > 0 ? 0.62 : 0.5)));
          g.add(pod);
        });
        var bar = TXT.roundedBox(0.7, 0.06, 0.05, 0.02, gloss); bar.position.set(0, 0.5 * sy, L / 2 + 0.02); g.add(bar);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        if (o.dome === false) g.remove(stack);
        g.userData.dome = [0, roofY + 0.27, -0.25 * s];
        g.userData.roofY = roofY;
        return g;
      }
    });

    /* AN AIRPORT DEPARTURES CURB, the road along x in front of +z. `length` m of curb: a concrete
     * island 4 m deep raised 0.15 m, a steel canopy at 7.2 m on round columns every 9 m, its soffit lit
     * by rows of downlights, a glazed terminal wall 6 m behind the island's back edge with mullions every
     * 1.5 m and a lit interior behind it, and steel bollards along the island's front edge. Drawn to
     * illustrate. userData.curbZ is the island's front edge, userData.islandY its top. */
    K.define("terminal_curb", {
      size: [60, 9, 16],
      options: { length: 60, canopy: null, canopyX: 0, bollards: true, downlights: true, seed: 2 },
      note: "An illustrative airport departures curb: raised concrete island, steel canopy on round columns with a lit soffit, a glazed terminal wall lit from inside, steel bollards. Road runs along x in front (+z).",
      make: function (o, r) {
        var g = new THREE.Group(), Lc = o.length || 60, Ca = o.canopy || Lc, Cx = o.canopyX || 0;
        var conc = K.mat("tc-conc", { color: 0xffffff, map: K.tex("concrete"), roughness: 0.9 });
        var steel = K.mat("tc-steel", { color: 0x6c7076, metalness: 0.7, roughness: 0.4 });
        var dark = K.mat("tc-dark", { color: 0x1a1c20, metalness: 0.5, roughness: 0.5 });
        var soffit = K.mat("tc-soffit", { color: 0x17181b, roughness: 0.85, metalness: 0.1 });
        var down = new THREE.MeshBasicMaterial({ color: 0xb8a586, toneMapped: true });
        var glassM = K.mat("tc-glass", { color: 0x0e1418, roughness: 0.05, metalness: 0.4, transparent: true, opacity: 0.55 }, true);
        var lobby = new THREE.MeshBasicMaterial({ color: 0xffffff, map: N.lobbyTex(THREE), toneMapped: true });
        /* island: front edge at z = 0 */
        var isl = new THREE.Mesh(new THREE.BoxGeometry(Lc, 0.15, 4), conc); isl.geometry = K.uvBox(isl.geometry, 2); isl.position.set(0, 0.075, -2); isl.receiveShadow = true; g.add(isl);
        var curbFace = new THREE.Mesh(new THREE.BoxGeometry(Lc, 0.16, 0.12), K.mat("tc-curb", { color: 0xd8d2c6, roughness: 0.8 })); curbFace.position.set(0, 0.08, 0.04); g.add(curbFace);
        /* walk between the island and the wall */
        var walk = new THREE.Mesh(new THREE.BoxGeometry(Lc, 0.15, 6), conc); walk.geometry = K.uvBox(walk.geometry, 2); walk.position.set(0, 0.075, -7); walk.receiveShadow = true; g.add(walk);
        /* columns and canopy */
        for (var x = Cx - Ca / 2 + 4.5; x <= Cx + Ca / 2 - 4; x += 9) { K.cyl(0.22, 0.22, 7.2, steel, x, 0.15, -1.2, 24, g); K.cyl(0.3, 0.3, 0.12, dark, x, 0.15, -1.2, 24, g); }
        var deck = new THREE.Mesh(new THREE.BoxGeometry(Ca, 0.5, 11), soffit); deck.position.set(Cx, 7.6, -4.5); deck.castShadow = true; g.add(deck);
        var fascia = TXT.roundedBox(Ca, 0.9, 0.3, 0.05, K.mat("tc-fascia", { color: 0x2c2824, metalness: 0.5, roughness: 0.55 })); fascia.position.set(Cx, 7.75, 1.0); g.add(fascia);
        if (o.downlights !== false) for (var dx = Cx - Ca / 2 + 2; dx < Cx + Ca / 2; dx += 3) for (var dz = 0; dz < 3; dz++) { var dl = new THREE.Mesh(new THREE.CircleGeometry(0.11, 16), down); dl.rotation.x = Math.PI / 2; dl.position.set(dx, 7.34, -0.5 - dz * 3.2); g.add(dl); }
        /* the terminal wall: mullions, glass, the lit lobby behind */
        var wallZ = -10.2;
        var lob = new THREE.Mesh(new THREE.PlaneGeometry(Ca, 6.2), lobby); lob.position.set(Cx, 3.3, wallZ - 1.4); g.add(lob);
        var gl = new THREE.Mesh(new THREE.PlaneGeometry(Ca, 6.6), glassM); gl.position.set(Cx, 3.45, wallZ); g.add(gl);
        for (var mx = Cx - Ca / 2; mx <= Cx + Ca / 2; mx += 1.5) K.box(0.06, 6.6, 0.16, dark, mx, 0.15, wallZ, 0.01, g);
        [0.15, 3.4, 6.75].forEach(function (y) { K.box(Ca, 0.12, 0.18, dark, Cx, y, wallZ, 0.01, g); });
        var head = new THREE.Mesh(new THREE.BoxGeometry(Ca, 1.4, 0.4), K.mat("tc-head", { color: 0x9a9890, roughness: 0.8 })); head.position.set(Cx, 7.5, wallZ); g.add(head);
        /* bollards on the island's front edge, every 1.5 m */
        if (o.bollards !== false) for (var bx = -Lc / 2 + 1; bx < Lc / 2; bx += 1.5) { K.cyl(0.11, 0.11, 0.95, steel, bx, 0.15, -0.35, 18, g); K.cyl(0.115, 0.115, 0.06, dark, bx, 0.92, -0.35, 18, g); }
        g.traverse(function (m) { if (m.isMesh && m.material !== down && m.material !== lobby) { m.castShadow = true; m.receiveShadow = true; } });
        g.userData.keepOrigin = true;
        g.userData.curbZ = 0.1; g.userData.islandY = 0.15; g.userData.wallZ = wallZ;
        return g;
      }
    });

    /* STANDING WATER, a sheet `w` x `d` m and `depth` m deep, brown and still, its surface broken by
     * the ripple bump so a lamp smears in it. Its top sits at y = depth. */
    K.define("standing_water", {
      size: [8, 0.2, 8],
      options: { w: 8, d: 8, depth: 0.2, color: 0x2a2418, seed: 1 },
      note: "A sheet of standing floodwater, w x d m and depth m deep, brown and still under a rippled clearcoat.",
      make: function (o, r) {
        var g = new THREE.Group();
        var rip = N.rippleTex(THREE); rip.repeat.set(o.w / 3, o.d / 3);
        var m = new THREE.MeshPhysicalMaterial({ color: o.color, roughness: 0.08, metalness: 0.0, clearcoat: 1, clearcoatRoughness: 0.05, bumpMap: rip, bumpScale: 0.6, transparent: true, opacity: 0.9, envMapIntensity: 1.4 });
        var top = new THREE.Mesh(new THREE.BoxGeometry(o.w, o.depth, o.d), m); top.position.y = o.depth / 2; top.receiveShadow = true; g.add(top);
        g.userData.txWear = false;
        return g;
      }
    });

    /* A CURB BOLLARD, the deck's unit of one day: a 0.219 m steel pipe standing 1.0 m on a cast base,
     * painted dark bronze, a domed cap, and a 0.06 m retroreflective band at 0.82 m. `band` 'white',
     * 'accent' (comal, lit) or 'dark' (an unlit day). */
    K.define("curb_bollard", {
      size: [0.3, 1.06, 0.3],
      options: { band: "white", seed: 1 },
      note: "A steel pipe curb bollard 0.219 m across and 1.0 m tall, dark bronze, domed cap, a reflective band at 0.82 m in white, comal accent or dark.",
      make: function (o, r) {
        var g = new THREE.Group();
        K.cyl(0.11, 0.11, 1.0, N.bollardMat(THREE, K, "pipe"), 0, 0, 0, 20, g);
        K.cyl(0.14, 0.15, 0.04, N.bollardMat(THREE, K, "base"), 0, 0, 0, 20, g);
        var cap = new THREE.Mesh(new THREE.SphereGeometry(0.11, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), N.bollardMat(THREE, K, "pipe")); cap.position.y = 1.0; g.add(cap);
        K.cyl(0.113, 0.113, 0.06, N.bollardMat(THREE, K, o.band), 0, 0.79, 0, 20, g);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A RAISED ROAD STUD, a domed reflector 0.1 x 0.02 x 0.1 m on the lane line, its two faces lit */
    K.define("road_stud", {
      size: [0.1, 0.022, 0.1],
      options: { seed: 1 },
      note: "A raised pavement marker 0.10 x 0.02 x 0.10 m, white body with a lit prismatic face each way.",
      make: function (o, r) {
        var g = new THREE.Group();
        var b = TXT.roundedBox(0.1, 0.02, 0.1, 0.008, K.mat("rs-body", { color: 0xd8d6d0, roughness: 0.6 })); b.position.y = 0.01; g.add(b);
        [-1, 1].forEach(function (sz) { var f = new THREE.Mesh(new THREE.PlaneGeometry(0.07, 0.012), new THREE.MeshBasicMaterial({ color: 0xfff2d8, toneMapped: true })); f.position.set(0, 0.011, sz * 0.051); if (sz < 0) f.rotation.y = Math.PI; g.add(f); });
        return g;
      }
    });
  };

  /* the bollard's materials, shared so a row of hundreds costs one material each */
  N.bollardMat = function (THREE, K, which) {
    N._bm = N._bm || {};
    if (N._bm[which]) return N._bm[which];
    var m;
    if (which === "pipe") m = K.mat("bl-pipe", { color: 0x3a3028, metalness: 0.55, roughness: 0.45 });
    else if (which === "base") m = K.mat("bl-base", { color: 0x26221e, metalness: 0.5, roughness: 0.6 });
    else if (which === "white") m = K.mat("bl-white", { color: 0xf2f0ea, roughness: 0.25, emissive: 0xfff4e0, emissiveIntensity: 0.55 });
    else if (which === "accent") m = K.mat("bl-acc", { color: N.ACCENT, roughness: 0.25, emissive: N.ACCENT, emissiveIntensity: 1.4 });
    else m = K.mat("bl-dark", { color: 0x141210, roughness: 0.7 });
    N._bm[which] = m; return m;
  };

  /* A ROW OF BOLLARDS AS INSTANCES: n posts from `start` along `dir` at `pitch` m, each band chosen by
   * `bandOf(i)` ('white', 'accent' or 'dark'). One InstancedMesh per part and band, so 233 posts are a
   * handful of draw calls. Returns the posts' positions. */
  N.bollards = function (THREE, R, K, n, start, dir, pitch, bandOf, parent) {
    var pos = [], groups = {}, geo = {
      pipe: new THREE.CylinderGeometry(0.11, 0.11, 1.0, 16), base: new THREE.CylinderGeometry(0.14, 0.15, 0.04, 16),
      cap: new THREE.SphereGeometry(0.11, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), band: new THREE.CylinderGeometry(0.113, 0.113, 0.06, 16)
    };
    for (var i = 0; i < n; i++) pos.push([start[0] + dir[0] * pitch * i, start[1] || 0, start[2] + dir[2] * pitch * i]);
    function inst(g, mat, list, y) {
      var im = new THREE.InstancedMesh(g, mat, list.length), M = new THREE.Matrix4();
      list.forEach(function (p, k) { M.makeTranslation(p[0], p[1] + y, p[2]); im.setMatrixAt(k, M); });
      im.castShadow = true; im.receiveShadow = true; im.instanceMatrix.needsUpdate = true;
      (parent || R.scene).add(im); return im;
    }
    inst(geo.pipe, N.bollardMat(THREE, K, "pipe"), pos, 0.5);
    inst(geo.base, N.bollardMat(THREE, K, "base"), pos, 0.02);
    inst(geo.cap, N.bollardMat(THREE, K, "pipe"), pos, 1.0);
    pos.forEach(function (p, i) { var b = bandOf ? bandOf(i) : "white"; (groups[b] = groups[b] || []).push(p); });
    Object.keys(groups).forEach(function (b) { inst(geo.band, N.bollardMat(THREE, K, b), groups[b], 0.82); });
    return pos;
  };

  /* THE ROBOTAXI AT A LOW LEVEL OF DETAIL, for a field of thousands: a white body block with a dark
   * glass band, a dark dome, four dark wheels, at the hero's own proportions. Places one per entry of
   * `spots` ([x, z, yaw]) as InstancedMeshes. */
  N.carField = function (THREE, R, K, spots, parent) {
    var M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), S = new THREE.Vector3(1, 1, 1), up = new THREE.Vector3(0, 1, 0);
    var white = K.mat("cf-white", { color: 0xeceef0, roughness: 0.32, metalness: 0.0 });
    var glass = K.mat("cf-glass", { color: 0x0b0d10, roughness: 0.1, metalness: 0.3 });
    var dark = K.mat("cf-dark", { color: 0x0e1012, roughness: 0.5 });
    var parts = [
      [new THREE.BoxGeometry(1.86, 0.55, 4.6), white, [0, 0.48, 0]],
      [new THREE.BoxGeometry(1.66, 0.42, 2.2), glass, [0, 1.0, -0.45]],
      [new THREE.BoxGeometry(1.6, 0.5, 0.06).rotateX(-0.5), glass, [0, 0.98, 0.78]],
      [new THREE.BoxGeometry(1.6, 0.06, 2.1), white, [0, 1.23, -0.45]],
      [new THREE.BoxGeometry(1.7, 0.28, 0.06), dark, [0, 0.55, 2.31]],
      [new THREE.CylinderGeometry(0.17, 0.17, 0.32, 12), dark, [0, 1.42, -0.45]],
      [new THREE.SphereGeometry(0.09, 10, 8), new THREE.MeshBasicMaterial({ color: 0xfff2d8, toneMapped: false }), [0, 1.62, -0.45]],
      [new THREE.CylinderGeometry(0.33, 0.33, 1.9, 12).rotateZ(Math.PI / 2), dark, [0, 0.33, 1.45]],
      [new THREE.CylinderGeometry(0.33, 0.33, 1.9, 12).rotateZ(Math.PI / 2), dark, [0, 0.33, -1.45]]
    ];
    parts.forEach(function (pt) {
      var im = new THREE.InstancedMesh(pt[0], pt[1], spots.length);
      spots.forEach(function (sp, k) {
        Q.setFromAxisAngle(up, sp[2] || 0);
        var off = new THREE.Vector3(pt[2][0], pt[2][1], pt[2][2]).applyQuaternion(Q);
        M4.compose(new THREE.Vector3(sp[0] + off.x, off.y, sp[1] + off.z), Q, S); im.setMatrixAt(k, M4);
      });
      im.castShadow = true; im.receiveShadow = true; im.instanceMatrix.needsUpdate = true;
      (parent || R.scene).add(im);
    });
  };

  /* DOM TYPE ON A PROJECTED QUAD: a CSS matrix3d homography taking an element's own w x h box onto four
   * screen points (top left, top right, bottom right, bottom left), so a page's words stay vector type. */
  N.quad = function (el, w, h, P) {
    function solve(A, b) { var n = b.length; for (var i = 0; i < n; i++) { var mx = i; for (var k = i + 1; k < n; k++) if (Math.abs(A[k][i]) > Math.abs(A[mx][i])) mx = k; var t = A[i]; A[i] = A[mx]; A[mx] = t; var tb = b[i]; b[i] = b[mx]; b[mx] = tb; for (var k2 = i + 1; k2 < n; k2++) { var f = A[k2][i] / A[i][i]; for (var j = i; j < n; j++) A[k2][j] -= f * A[i][j]; b[k2] -= f * b[i]; } } var x = new Array(n); for (var i2 = n - 1; i2 >= 0; i2--) { var s = b[i2]; for (var j2 = i2 + 1; j2 < n; j2++) s -= A[i2][j2] * x[j2]; x[i2] = s / A[i2][i2]; } return x; }
    var src = [[0, 0], [w, 0], [w, h], [0, h]], A = [], b = [];
    for (var i = 0; i < 4; i++) {
      var x = src[i][0], y = src[i][1], u = P[i][0], v = P[i][1];
      A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.push(u);
      A.push([0, 0, 0, x, y, 1, -v * x, -v * y]); b.push(v);
    }
    var hm = solve(A, b);
    var m = [hm[0], hm[3], 0, hm[6], hm[1], hm[4], 0, hm[7], 0, 0, 1, 0, hm[2], hm[5], 0, 1];
    el.style.position = "absolute"; el.style.left = "0px"; el.style.top = "0px"; el.style.width = w + "px"; el.style.height = h + "px";
    el.style.transformOrigin = "0 0"; el.style.transform = "matrix3d(" + m.map(function (v) { return +v.toFixed(8); }).join(",") + ")";
  };

  N.keepAlpha = function (m) {
    var T = N.T;
    m.blending = T.CustomBlending; m.blendEquation = T.AddEquation;
    if (m.userData && m.userData.additive) { m.blendSrc = T.SrcAlphaFactor; m.blendDst = T.OneFactor; }
    else { m.blendSrc = T.SrcAlphaFactor; m.blendDst = T.OneMinusSrcAlphaFactor; }
    m.blendEquationAlpha = T.AddEquation; m.blendSrcAlpha = T.OneFactor; m.blendDstAlpha = T.OneFactor;
    return m;
  };
  /* A MATTE GROUND, so wet asphalt reads by its puddles rather than by a mirror everywhere */
  N.matte = function (gnd, k) { (Array.isArray(gnd) ? gnd : [gnd]).forEach(function (g) { (g.traverse ? g : { traverse: function (f) { f(g); } }).traverse(function (m) { if (m.material) { m.material.envMapIntensity = k == null ? 0.08 : k; m.material.roughness = 1; m.material.needsUpdate = true; } }); }); return gnd; };
  /* THE PLAZA PAD: a dark worn concrete slab the stair stands on. At a grazing camera TXT.ground fades into
   * the horizon's colour by design, which here is the seam, so the near plaza is this pad and the ground
   * beyond it keeps the engine's fade. */
  N.pad = function (THREE, R, w, d, x, z, rot) {
    var t = N.canvasTex(THREE, "pad", 512, 512, function (c, W, H) { var r = lcg(12); c.fillStyle = "#3a3633"; c.fillRect(0, 0, W, H); for (var i = 0; i < 9000; i++) { c.fillStyle = "rgba(" + (r() < 0.5 ? "20,18,17," : "90,84,78,") + (0.08 + r() * 0.12).toFixed(2) + ")"; c.fillRect(r() * W, r() * H, 1 + r() * 3, 1 + r() * 3); } c.strokeStyle = "rgba(15,14,13,0.6)"; c.lineWidth = 3; for (var k = 0; k <= 4; k++) { c.beginPath(); c.moveTo(k * W / 4, 0); c.lineTo(k * W / 4, H); c.stroke(); c.beginPath(); c.moveTo(0, k * H / 4); c.lineTo(W, k * H / 4); c.stroke(); } }, true);
    t.repeat.set(w / 6, d / 6);
    var m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshLambertMaterial({ color: 0x8a837c, map: t }));
    m.rotation.x = -Math.PI / 2; m.position.set(x || 0, 0.004, z || 0); if (rot) m.rotation.z = rot; m.receiveShadow = true; R.scene.add(m);
    return m;
  };
  /* FAR LIT WINDOWS on dark land: a scatter of small warm points low on the horizon, so a frame that looks
   * out from the court sees a county at night rather than a skyline anybody could name */
  N.windows = function (THREE, R, center, dirAz, o) {
    o = o || {}; var r = lcg(o.seed || 9), g = new THREE.Group(), n = o.count || 160;
    var mat = new THREE.MeshBasicMaterial({ color: 0xffc27a, toneMapped: true, fog: false });
    var geo = new THREE.BoxGeometry(1, 1, 1);
    for (var i = 0; i < n; i++) {
      var d = (o.near || 500) + Math.pow(r(), 0.7) * ((o.far || 2600) - (o.near || 500)), a = dirAz + (r() - 0.5) * (o.spread || 1.4);
      var m = new THREE.Mesh(geo, mat); var sz = 1.2 + r() * 2.4;
      m.scale.set(sz, sz * (0.5 + r() * 0.6), sz); m.position.set(center[0] + Math.sin(a) * d, 0.5 + r() * 3, center[2] + Math.cos(a) * d); g.add(m);
    }
    R.scene.add(g); return g;
  };

  /* A WINDOW CUT INTO A TXT.interior BACK WALL. The engine's room carries a lit pane, not an opening, so
   * a frame that must see the street through its window removes the back wall (the room's first child)
   * and builds it again around an opening x0..x1, y0..y1, with a sill, a frame, faint glass and a set of
   * blinds whose slats let the deck's key through in stripes. Room local coordinates, back wall at z = -d/2. */
  N.cutWindow = function (THREE, K, room, o) {
    var w = o.w, d = o.d, h = o.h, t = 0.2, z = -d / 2;
    var wallMat = room.children[0].material;
    room.remove(room.children[0]);
    function piece(x0, x1, y0, y1) { var m = TXT_box(THREE, x1 - x0, y1 - y0, t, wallMat); m.position.set((x0 + x1) / 2, (y0 + y1) / 2, z); room.add(m); }
    piece(-w / 2 - t / 2, o.x0, 0, h); piece(o.x1, w / 2 + t / 2, 0, h); piece(o.x0, o.x1, 0, o.y0); piece(o.x0, o.x1, o.y1, h);
    var frame = K.mat("cw-frame", { color: 0x2a2826, roughness: 0.6, metalness: 0.3 });
    [[o.x0, o.x1, o.y0 - 0.04, o.y0], [o.x0, o.x1, o.y1, o.y1 + 0.04]].forEach(function (b) { var m = TXT_box(THREE, b[1] - b[0], b[3] - b[2], t + 0.04, frame); m.position.set((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, z); room.add(m); });
    [o.x0, o.x1, (o.x0 + o.x1) / 2].forEach(function (x) { var m = TXT_box(THREE, 0.05, o.y1 - o.y0, t + 0.04, frame); m.position.set(x, (o.y0 + o.y1) / 2, z); room.add(m); });
    var sill = TXT_box(THREE, o.x1 - o.x0 + 0.1, 0.03, 0.26, K.mat("cw-sill", { color: 0x8a8278, roughness: 0.7 })); sill.position.set((o.x0 + o.x1) / 2, o.y0 - 0.015, z + 0.1); room.add(sill);
    var slat = K.mat("cw-slat", { color: o.slat || 0xcfc8bc, roughness: 0.55, metalness: 0.1 });
    for (var y = o.y0 + 0.06; y < o.y1 - 0.02; y += o.pitch || 0.1) { var sl = TXT_box(THREE, o.x1 - o.x0 - 0.04, 0.004, 0.05, slat); sl.position.set((o.x0 + o.x1) / 2, y, z + 0.16); sl.rotation.x = o.tilt == null ? 0.9 : o.tilt; room.add(sl); }
    room.traverse(function (m) { if (m.isMesh) { m.receiveShadow = true; m.castShadow = m.material === slat || m.material === frame || m.material === wallMat; } });
    return room;
  };
  function TXT_box(THREE, w, h, d, mat) { return new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); }
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  /* a point on a kit model, in world space, from the model's own frame */
  /* a named part of a kit model, in world space, wherever K.make's recentring moved it */
  N.part = function (THREE, obj, name) {
    obj.updateMatrixWorld(true);
    var m = obj.getObjectByName(name); if (!m) throw new Error("no part named " + name);
    var b = new THREE.Box3().setFromObject(m), c = b.getCenter(new THREE.Vector3());
    return [c.x, c.y, c.z];
  };
  N.world = function (THREE, obj, p) {
    obj.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).applyMatrix4(obj.matrixWorld);
    return [v.x, v.y, v.z];
  };
  /* AIM SO A POINT LANDS WHERE THE LAYOUT WANTS IT: from a fixed camera position, solve the look target
   * so that `point` projects to screen (sx, sy). A close camera makes a hand-typed look target swing
   * hundreds of pixels per centimetre, which is what this replaces. Returns the look target. */
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
  /* THE KEY is the curb's lamps, a sodium and LED mix rather than pure low pressure sodium, so the white
   * clearcoat reads white with a warm lit face; the cool rim from the world's rig is raised so a car's
   * shadow side separates from the night */
  N.rigSpec = function (W, size, map) {
    var rim = Object.assign({}, W.rig.rim, { i: (W.rig.rim.i || 0.8) * 1.4 });
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { color: 0xffd6aa, shadowSize: size || 12, mapSize: map || 2048, radius: 5 }) });
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
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "5,6,9";
    if (bottom != null && a > 0) {
      var fade = o.fade || 180, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + a + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + (a * 0.85) + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  N.post = function (cx, o) {
    o = o || {};
    if (o.a !== 0) N.shade(cx, { a: o.a, to: o.to, fade: o.fade, pad: o.pad });
    var y0 = N.H - (o.veilH || 240), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(5,6,9," + (Math.min(0.5, o.veil == null ? 0.38 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    /* the footer row wash (TECHNIQUE_LIBRARY, 2026-10-15): full width, darken only, at full strength from
     * the top of the footer row to the foot, feathered above it over the depth of the margin below it */
    var f = document.querySelector(".tx-site");
    if (f && o.footWash) {
      var r = f.getBoundingClientRect(), feather = N.H - r.bottom, fa = Math.min(o.footWash, 0.55 - 0.01);
      var fw = cx.createLinearGradient(0, r.top - feather, 0, N.H);
      fw.addColorStop(0, "rgba(5,6,9,0)");
      fw.addColorStop(feather / (N.H - r.top + feather), "rgba(5,6,9," + fa + ")");
      fw.addColorStop(1, "rgba(5,6,9," + fa + ")");
      cx.fillStyle = fw; cx.fillRect(0, r.top - feather, N.W, N.H - r.top + feather);
    }
    N.dither(cx);
  };
  /* A RESERVE under one line of type: a feathered dark patch behind the element, so a horizon, a
   * water edge or a lit floor never runs through its glyphs. It only darkens, and only there. */
  N.knock = function (cx, els, a) {
    (els || []).forEach(function (el) {
      if (typeof el === "string") el = document.querySelector(el);
      if (!el) return;
      var r = el.getBoundingClientRect();
      cx.save(); cx.filter = "blur(12px)"; cx.fillStyle = "rgba(5,6,9," + (a == null ? 0.82 : a) + ")";
      cx.fillRect(r.left - 18, r.top - 10, r.width + 36, r.height + 20); cx.restore();
    });
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 2.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };
  /* a DOM leader from a label's edge to a projected point, ending short of the glyphs */
  N.leader = function (svg, from, to) {
    /* a dark under-stroke first, so the line holds where it crosses the white paint */
    var u = document.createElementNS("http://www.w3.org/2000/svg", "line");
    u.setAttribute("x1", from[0]); u.setAttribute("y1", from[1]); u.setAttribute("x2", to[0]); u.setAttribute("y2", to[1]);
    u.setAttribute("stroke", "#07080C"); u.setAttribute("stroke-width", "5"); u.setAttribute("stroke-opacity", "0.6"); svg.appendChild(u);
    var l = document.createElementNS("http://www.w3.org/2000/svg", "line");
    l.setAttribute("x1", from[0]); l.setAttribute("y1", from[1]); l.setAttribute("x2", to[0]); l.setAttribute("y2", to[1]);
    l.setAttribute("stroke", N.INK); l.setAttribute("stroke-width", "2"); l.setAttribute("stroke-opacity", "0.85"); svg.appendChild(l);
    var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", to[0]); c.setAttribute("cy", to[1]); c.setAttribute("r", "5"); c.setAttribute("fill", N.INK); svg.appendChild(c);
  };
  N.labelAt = function (id, p, dx, dy) {
    var s = N.project(N.T, N.R, p), el = document.getElementById(id);
    el.style.left = Math.round(s[0] + (dx || 0)) + "px"; el.style.top = Math.round(s[1] + (dy || 0)) + "px";
    return s;
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#D8D0C2", halo = "rgba(3,4,8,0.6)", halo2 = "rgba(3,4,8,0.45)", acc = "#" + ("000000" + N.ACCENT.toString(16)).slice(-6).toUpperCase();
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#07090B; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      '.lab.acc { color:' + acc + '; }',
      ".hook, .dek, .tx-site, .kick, .src, .cap, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D8D0C2" });
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

  global.CH = N;
})(this);

