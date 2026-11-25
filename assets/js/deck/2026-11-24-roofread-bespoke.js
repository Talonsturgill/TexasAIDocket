/* deck/2026-11-24-roofread-bespoke.js, the SPINE for the November 24th, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * Texas A&M's CLARKE, an AI tool that turns drone imagery into building and road damage assessments, reviewed by a trained
 * operator, standard procedure for Florida's state drone team (tx-2026-0258).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the deck's TONE (wonder), bespoke:true, the tone's grade and the accent.
 * Each frame picks its own world (TXT.sky(R, world) or TXT.studio / TXT.interior), turns its own key
 * (TXT.deckRig(..., { light })) and places its own type, seated with CH.seat. It mounts the type faces and the furniture
 * (CH.start), and hands a frame the helpers below. There is no drawFrame.
 *
 * THE ACCENT. Wonder gold #ffcc00 means ONE thing: THE WAY THROUGH, the route around damaged roads (c7, c21). It is never
 * on a roof, a person, a rim or type. CH.route builds it.
 *
 * THE COLOR CODE is not the accent. CH.RAMP is three cool steps from the wonder family (ice, cerulean, cobalt violet), no
 * red, no legend, no class name, drawn to illustrate. CH.rim draws a footprint rim HOLLOW (before the review frame) or
 * FILLED (after it), so the human check (c19) is geometry.
 *
 * THE NEIGHBOURHOOD. CH.lots(n, seed) lays out n seeded Gulf Coast lots on curved streets, deterministic, never Math.random.
 * CH.carpet instances walls, hip roofs and rims for them. Every frame that draws the neighbourhood reads n from window.FIG.
 *
 * THE MODELS THE KIT LACKS, built in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17
 * can queue the lift: survey_quad (from the November 21st chassis), downed_oak (a kit live_oak on its side with a torn
 * gumbo root plate), rescue_helmet, ortho_plate (an anodised plate carrying a drawn aerial patch) and plate_rack (a steel
 * cradle of n plates). CH.roofDamage builds stripped OSB decking with nail rows and a tarp to lay on a roof plane.
 * Everything drawn is drawn to illustrate: no real town, no product interface, no logo, no legible screen.
 * Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("roofread.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "roofread", look: "v2", tone: "wonder", bespoke: true,
    light: { az: -55, el: 24 },
    sky: { preset: "v2wonder" },
    ground: "#3f7d3a",
    material: "#efe6d2",
    accent: "#ffcc00",
    grade: TXLOOK.grade("wonder")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261124; N.TONE = "wonder"; N.P = TXLOOK.palette("wonder"); N.INK = N.P.ink;
  N.ACCENT = 0xffcc00;        /* gold: the way through, and nothing else */
  N.GOLD = N.ACCENT;
  N.RAMP = [0xbfe6ff, 0x4aa3f0, 0x5b4fd0];   /* ice, cerulean, cobalt violet: the judged roof code, drawn to illustrate */
  N.GUMBO = 0x8a5a3c; N.LAWN = 0x3f7d3a; N.SHELL = 0xefe6d2; N.DECK = 0xc79a62; N.TARP = 0x2f6fd6; N.BRICK = 0x9a5a3c;
  N.SHINGLE = [0x3b3a3f, 0x5a4a44, 0x6e5a4c, 0x4a4f58, 0x7a6a5e]; N.LIMESTONE = 0xe9dfc8; N.SHADE = 0x24206a;
  N.CALICHE = 0xe4d8c3; N.VINYL = 0x4e5fa8; N.OAK = 0xc89b6a; N.BRASS = 0xc9a24a; N.PAPER = 0xf7f3ea; N.INDIGO_AL = 0x2e3a8c;
  N.GHOST = 0xb8c4ff;
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };
  N.glassMat = function (K, tint) {
    return K.mat("ft-glass" + (tint || ""), { color: tint || 0xeaf6ff, metalness: 0, roughness: 0.05, transmission: 0.9, ior: 1.47, thickness: 0.006,
      transparent: true, opacity: 1, clearcoat: 1, clearcoatRoughness: 0.03, specularIntensity: 1, envMapIntensity: 1.4, side: N.T.DoubleSide }, true);
  };
  /* the tool's glow, one material, so every lit tool in a frame is the same light */
  /* greeked lines on paper, never legible: short bars at a pitch, broken into words by the seed */
  N.paperTex = function (THREE, seed, lines, marks) {
    var r = N.rng(seed || 7);
    return N.canvasTex(THREE, 512, 340, function (g, w, h) {
      g.fillStyle = "#f7f3ea"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 2600; i++) { g.fillStyle = "rgba(120,110,90," + (r() * 0.05).toFixed(3) + ")"; g.fillRect(r() * w, r() * h, 1.2, 1.2); }
      var n = lines || 9;
      for (var L = 0; L < n; L++) {
        var y = 40 + L * (h - 70) / n, x = 34, end = w - 34 - (L === n - 1 ? 180 : r() * 40);
        while (x < end) { var ww = 14 + r() * 46; g.fillStyle = "rgba(60,64,92,0.42)"; g.fillRect(x, y, Math.min(ww, end - x), 5); x += ww + 8 + r() * 6; }
      }
      if (marks) {
        g.strokeStyle = "#0ea5c4"; g.lineWidth = 5; g.lineCap = "round";
        [[2, 0.2, 0.62], [5, 0.35, 0.8], [7, 0.12, 0.5]].forEach(function (m) { var y = 40 + m[0] * (h - 70) / n + 12; g.beginPath(); g.moveTo(w * m[1], y); g.lineTo(w * m[2], y + 1); g.stroke(); });
        g.beginPath(); g.moveTo(w - 26, 60); g.lineTo(w - 26, 150); g.stroke();
        g.beginPath(); g.arc(w - 40, 230, 14, Math.PI * 1.1, Math.PI * 2.6); g.stroke();
      }
    });
  };

  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */

  /* THE NEIGHBOURHOOD LAYOUT. n lots on gently curved streets, seeded. Each lot: x, z (house centre, metres), ry (house yaw),
   * w, d (footprint), step (0..2, the judged ramp step), damaged, tarp, roof (shingle index), hip. Streets run along x and
   * bow with z; houses face the nearer street. Returned with .streets (centrelines as [[x,z],...] arrays) and .span. */
  N.lots = function (n, seed, o) {
    o = o || {};
    var r = N.rng(seed || N.SEED), cols = o.cols || Math.ceil(Math.sqrt(n * 2.2)), lotW = o.lotW || 20, lotD = o.lotD || 36, road = o.road || 9;
    var rows = Math.ceil(n / cols), out = [], streets = [];
    var bow = function (x, row) { return Math.sin(x / 140 + row * 0.7) * 9 + Math.sin(x / 61 + row) * 2.5; };
    for (var row = 0; row < rows; row++) {
      var pair = Math.floor(row / 2), side = row % 2 ? 1 : -1;
      var sz = pair * (2 * lotD + road);
      if (row % 2 === 0) { var line = []; for (var sx = -cols * lotW / 2 - 40; sx <= cols * lotW / 2 + 40; sx += 10) line.push([sx, sz + bow(sx, pair)]); streets.push(line); }
      for (var c = 0; c < cols && out.length < n; c++) {
        var x = (c - (cols - 1) / 2) * lotW + (r() - 0.5) * 2.4;
        var z = sz + bow(x, pair) + side * (road / 2 + lotD * 0.42);
        var w = 13 + r() * 4, d = 10 + r() * 3, dmg = r() < (o.damage == null ? 0.32 : o.damage);
        out.push({ x: x, z: z, ry: (side > 0 ? Math.PI : 0) + (r() - 0.5) * 0.06, w: w, d: d, step: Math.floor(r() * 3), damaged: dmg,
          tarp: dmg && r() < 0.5, roof: Math.floor(r() * N.SHINGLE.length), hip: r() < 0.6, tree: r() < 0.55, treeX: (r() - 0.5) * 12, treeZ: (r() - 0.5) * 8 });
      }
    }
    out.streets = streets; out.span = [cols * lotW, rows / 2 * (2 * lotD + road)];
    return out;
  };

  /* hip or gable roof geometry over a unit footprint (1 x 1, base at y 0, height h), for instancing */
  N.roofGeo = function (THREE, hip, h) {
    var g = new THREE.BufferGeometry(), x = 0.5, z = 0.5, rx = hip ? 0.22 : 0.5, y = h, v;
    if (hip) v = [-x,0,z, x,0,z, rx,y,0, -x,0,z, rx,y,0, -rx,y,0,  x,0,-z, -x,0,-z, -rx,y,0, x,0,-z, -rx,y,0, rx,y,0,  x,0,z, x,0,-z, rx,y,0,  -x,0,-z, -x,0,z, -rx,y,0];
    else v = [-x,0,z, x,0,z, x,y,0, -x,0,z, x,y,0, -x,y,0,  x,0,-z, -x,0,-z, -x,y,0, x,0,-z, -x,y,0, x,y,0,  x,0,z, x,0,-z, x,y,0,  -x,0,-z, -x,0,z, -x,y,0];
    g.setAttribute("position", new THREE.Float32BufferAttribute(v, 3)); g.computeVertexNormals(); return g;
  };

  /* THE CARPET. Instanced walls, roofs and (optionally) rims for a list of lots, split into shingle colour batches so the
   * roofs vary. o.rims: "hollow" | "filled" | null. o.skip(lot, i): leave a lot out (where a frame places a full kit house).
   * o.damage: tint damaged roofs to decking. Returns a Group; group.userData.count is the number of roofs drawn. */
  N.carpet = function (THREE, K, lots, o) {
    o = o || {};
    var G = new THREE.Group(), wallGeo = new THREE.BoxGeometry(1, 1, 1); wallGeo.translate(0, 0.5, 0);
    var roofs = [N.roofGeo(THREE, true, 1), N.roofGeo(THREE, false, 1)], count = 0;
    var walls = K.mat("rr-wall", { color: 0xd9cbb2, roughness: 0.85 }), brick = K.mat("rr-brick", { color: N.BRICK, roughness: 0.9 });
    var batches = {};
    var M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(), p = new THREE.Vector3();
    lots.forEach(function (L, i) {
      if (o.skip && o.skip(L, i)) return;
      count++;
      var wh = o.wallH || 3.0, rh = o.roofH || 2.4;
      var wk = (L.roof % 2 ? "b" : "w"); (batches["wall" + wk] = batches["wall" + wk] || []).push([L.x, 0, L.z, L.ry, L.w, wh, L.d]);
      var rk = "roof" + (L.hip ? 0 : 1) + "_" + (o.damage && L.damaged ? (L.tarp ? "tarp" : "deck") : L.roof);
      (batches[rk] = batches[rk] || []).push([L.x, wh, L.z, L.ry, L.w * 1.08, rh, L.d * 1.12]);
    });
    Object.keys(batches).forEach(function (k) {
      var list = batches[k], geo, mat;
      if (k.indexOf("wall") === 0) { geo = wallGeo; mat = k === "wallb" ? brick : walls; }
      else { var parts = k.split("_"); geo = roofs[+parts[0].slice(4)];
        var c = parts[1] === "tarp" ? N.TARP : parts[1] === "deck" ? N.DECK : N.SHINGLE[+parts[1]];
        mat = K.mat("rr-roof-" + parts[1], { color: c, roughness: parts[1] === "tarp" ? 0.45 : 0.82, clearcoat: parts[1] === "tarp" ? 0.4 : 0 }, true); }
      var im = new THREE.InstancedMesh(geo, mat, list.length);
      list.forEach(function (it, j) { e.set(0, it[3], 0); q.setFromEuler(e); s.set(it[4], it[5], it[6]); p.set(it[0], it[1], it[2]); M.compose(p, q, s); im.setMatrixAt(j, M); });
      im.instanceMatrix.needsUpdate = true; im.castShadow = true; im.receiveShadow = true; G.add(im);
    });
    if (o.rims) G.add(N.rims(THREE, K, lots, { filled: o.rims === "filled", skip: o.skip, y: (o.wallH || 3.0) + 0.05, lift: o.rimLift }));
    G.userData.count = count;
    return G;
  };

  /* FOOTPRINT RIMS for many lots, instanced per ramp step. hollow: a 0.25 m wide frame 0.12 m tall around the footprint at
   * eave height; filled: a 4 cm plate lying over the roof. Colour from CH.RAMP[step]. Never red, never the accent. */
  N.rims = function (THREE, K, lots, o) {
    o = o || {};
    var G = new THREE.Group(), y = o.y == null ? 3.05 : o.y;
    var frame = function () {
      var sh = new THREE.Shape([new THREE.Vector2(-0.5, -0.5), new THREE.Vector2(0.5, -0.5), new THREE.Vector2(0.5, 0.5), new THREE.Vector2(-0.5, 0.5)]);
      var hole = new THREE.Path([new THREE.Vector2(-0.47, -0.47), new THREE.Vector2(-0.47, 0.47), new THREE.Vector2(0.47, 0.47), new THREE.Vector2(0.47, -0.47)]);
      sh.holes.push(hole); var g = new THREE.ExtrudeGeometry(sh, { depth: 1, bevelEnabled: false }); g.rotateX(-Math.PI / 2); return g;
    };
    var geo = o.filled ? new THREE.BoxGeometry(1, 1, 1).translate(0, 0.5, 0) : frame();
    [0, 1, 2].forEach(function (st) {
      var list = lots.filter(function (L, i) { return L.step === st && !(o.skip && o.skip(L, i)); });
      if (!list.length) return;
      var mat = K.mat("rr-rim-" + st + (o.filled ? "f" : "h"), { color: N.RAMP[st], emissive: N.RAMP[st], emissiveIntensity: o.filled ? 0.35 : 0.55, roughness: 0.4, transparent: !!o.filled, opacity: o.filled ? 0.82 : 1 }, true);
      var im = new THREE.InstancedMesh(geo, mat, list.length), M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(), p = new THREE.Vector3();
      list.forEach(function (L, j) { e.set(0, L.ry, 0); q.setFromEuler(e);
        if (o.filled) { s.set(L.w * 1.1, 0.04, L.d * 1.14); p.set(L.x, y + (o.lift == null ? 2.5 : o.lift), L.z); }
        else { s.set(L.w * 1.16, 0.14, L.d * 1.2); p.set(L.x, y, L.z); }
        M.compose(p, q, s); im.setMatrixAt(j, M); });
      im.instanceMatrix.needsUpdate = true; im.castShadow = false; im.receiveShadow = false; G.add(im);
    });
    return G;
  };

  /* ONE RIM around one footprint, for a frame's hero house: w, d metres, step 0..2, filled bool, y eave height */
  N.rim = function (THREE, K, w, d, step, filled, y) {
    var g = N.rims(THREE, K, [{ x: 0, z: 0, ry: 0, w: w / 1.1, d: d / 1.12, step: step || 1 }], { filled: filled, y: y == null ? 3.05 : y, lift: 0 });
    return g;
  };

  /* THE WAY THROUGH. A gold tube along a polyline of [x, y, z] points, radius r, lifted lift metres. Albedo led with a small
   * emissive so it holds its hue at feed size. The accent's one meaning. */
  N.route = function (THREE, K, pts, o) {
    o = o || {};
    var v = pts.map(function (p) { return new THREE.Vector3(p[0], (p[1] || 0) + (o.lift == null ? 0.4 : o.lift), p[2]); });
    var curve = new THREE.CatmullRomCurve3(v, false, "centripetal", 0.3);
    var mat = K.mat("rr-route", { color: N.ACCENT, emissive: N.ACCENT, emissiveIntensity: o.glow == null ? 0.6 : o.glow, roughness: 0.35, clearcoat: 0.5 }, true);
    var m = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(64, pts.length * 24), o.r || 0.35, 12, false), mat);
    m.castShadow = true; m.userData.accent = true; return m;
  };

  /* ROOF DAMAGE to lay on a roof plane: a w x d patch of OSB decking with nail rows and torn shingle edges, and an optional
   * tarp of tw x td with sandbag lumps. Lies in its own XZ plane at y 0, front +z; a frame tilts it to the roof pitch. */
  N.roofDamage = function (THREE, K, o) {
    o = Object.assign({ w: 4.5, d: 3.2, tarp: true, tw: 4, td: 3, seed: 5 }, o || {});
    var G = new THREE.Group(), r = N.rng(o.seed);
    var deckTex = N.canvasTex(THREE, 512, 384, function (g, w, h) {
      g.fillStyle = "#c79a62"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 3800; i++) { var a = r(); g.fillStyle = "rgba(" + (a < 0.5 ? "120,80,40," : "235,205,150,") + (0.08 + r() * 0.18).toFixed(2) + ")"; g.fillRect(r() * w, r() * h, 2 + r() * 14, 1 + r() * 4); }
      g.strokeStyle = "rgba(80,52,28,0.55)"; g.lineWidth = 3; for (var sx = 0; sx < w; sx += w / 3) { g.beginPath(); g.moveTo(sx, 0); g.lineTo(sx, h); g.stroke(); }
      g.fillStyle = "rgba(60,60,70,0.85)"; for (var row = 0; row < h; row += 22) for (var c = 8; c < w; c += 30) g.fillRect(c, row + 6, 3, 3);
    });
    var deck = new THREE.Mesh(new THREE.PlaneGeometry(o.w, o.d), K.mat("rr-deck-" + o.seed, { color: 0xffffff, map: deckTex, roughness: 0.9 }, true));
    deck.rotation.x = -Math.PI / 2; deck.position.y = 0.01; deck.receiveShadow = true; G.add(deck);
    var shg = K.mat("rr-torn", { color: 0x3b3a3f, roughness: 0.85 });
    for (var t = 0; t < 14; t++) { var tab = K.box(0.34 + r() * 0.3, 0.025, 0.3, shg, -o.w / 2 + r() * o.w, 0.0, (r() < 0.5 ? -1 : 1) * (o.d / 2 + 0.05), 0, G); tab.rotation.y = (r() - 0.5) * 0.5; tab.rotation.x = (r() - 0.5) * 0.4; tab.castShadow = true; }
    if (o.tarp) {
      var tg = new THREE.PlaneGeometry(o.tw, o.td, 24, 18), pos = tg.attributes.position;
      for (var k = 0; k < pos.count; k++) { var px = pos.getX(k), py = pos.getY(k); pos.setZ(k, 0.06 * Math.sin(px * 3.1 + py * 1.7) + 0.05 * Math.sin(py * 4.3)); }
      tg.computeVertexNormals();
      var tarp = new THREE.Mesh(tg, K.mat("rr-tarp", { color: N.TARP, roughness: 0.45, clearcoat: 0.5, sheen: 0.4, side: THREE.DoubleSide }, true));
      tarp.rotation.x = -Math.PI / 2; tarp.position.set(o.w * 0.28, 0.05, -o.d * 0.1); tarp.castShadow = true; tarp.receiveShadow = true; G.add(tarp);
      var bag = K.mat("rr-bag", { color: 0x8b7a5a, roughness: 0.95 });
      [[-0.45, -0.4], [0.45, -0.4], [-0.45, 0.4], [0.45, 0.4], [0, -0.45]].forEach(function (b) {
        var m = new THREE.Mesh(new THREE.SphereGeometry(0.22, 14, 10), bag); m.scale.set(1.4, 0.5, 0.9); m.position.set(tarp.position.x + b[0] * o.tw, 0.12, tarp.position.z + b[1] * o.td); m.castShadow = true; G.add(m); });
    }
    return G;
  };

  /* an aerial patch painted to a canvas: lots, roofs, lawns, a curved street, oaks. Never a real place. */
  N.aerialTex = function (THREE, seed, o) {
    o = o || {};
    var r = N.rng(seed || 3);
    return N.canvasTex(THREE, 512, 512, function (g, w, h) {
      g.fillStyle = "#3f7d3a"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 900; i++) { g.fillStyle = "rgba(" + (40 + r() * 40 | 0) + "," + (100 + r() * 50 | 0) + "," + (40 + r() * 30 | 0) + ",0.35)"; g.fillRect(r() * w, r() * h, 6, 6); }
      var yy = h * (0.3 + r() * 0.4); g.strokeStyle = "#e9e1cf"; g.lineWidth = 26; g.beginPath(); g.moveTo(-20, yy); g.bezierCurveTo(w * 0.3, yy - 40 + r() * 80, w * 0.7, yy - 40 + r() * 80, w + 20, yy + (r() - 0.5) * 60); g.stroke();
      var cols = ["#3b3a3f", "#5a4a44", "#6e5a4c", "#4a4f58", "#7a6a5e", "#c79a62", "#2f6fd6"];
      for (var k = 0; k < 26; k++) { var x = r() * w, y = r() * h; if (Math.abs(y - yy) < 30) continue; g.save(); g.translate(x, y); g.rotate((r() - 0.5) * 0.3);
        g.fillStyle = cols[Math.floor(r() * (r() < 0.2 ? 7 : 5))]; g.fillRect(-18, -13, 36, 26); g.fillStyle = "rgba(255,255,255,0.15)"; g.fillRect(-18, -13, 36, 3); g.restore(); }
      for (var t = 0; t < 30; t++) { g.fillStyle = "rgba(25,60,28,0.85)"; g.beginPath(); g.arc(r() * w, r() * h, 6 + r() * 9, 0, 7); g.fill(); }
    });
  };

  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.downed_oak) return;
    N.T = THREE;
    var shadowAll = function (g) { g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return g; };
    var rbox = function (w, h, d, r, mat) { return TXT.roundedBox ? TXT.roundedBox(w, h, d, r, mat) : new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); };
    K.define("survey_quad", {
      size: [0.86, 0.26, 0.86],
      options: { spin: 0, shell: 0xe9ecef, lamp: null, legs: true, lift: 0, arm: 0.35, ghost: false, props: 'still', open: false },
      note: "An illustrative survey quadcopter, about 0.70 m motor to motor, moulded shell, carbon arms, gimbal camera, landing legs, GPS puck on a mast. Origin on the ground under the body, front on +z. props 'still' | 'spin' | 'folded'; lift raises it; open:true removes the top shell and shows the flight_board; ghost:true renders the whole aircraft in frosted periwinkle glass that casts NO shadow (the reported position); lamp colours the rear lamp.",
      make: function (o) {
        o = Object.assign({ spin: 0, shell: 0xe9ecef, lamp: null, legs: true, lift: 0, arm: 0.35, ghost: false, props: 'still', open: false }, o || {});
        if (o.props === 'spin') o.spin = 1;
        var g = new THREE.Group(), body = new THREE.Group(); g.add(body);
        var legH = o.legs ? 0.13 : 0.06; body.position.y = legH + o.lift;
        var shell = K.mat("q-shell-" + o.shell, { color: o.shell, roughness: 0.32, metalness: 0.05, clearcoat: 0.8, clearcoatRoughness: 0.18 }, true);
        var trim = K.mat("q-trim", { color: 0x2b2f36, roughness: 0.45, metalness: 0.2, clearcoat: 0.3 }, true);
        var carbonTex = N.canvasTex(THREE, 256, 256, function (x, w, h) {
          x.fillStyle = "#1c1f24"; x.fillRect(0, 0, w, h);
          for (var j = 0; j < h; j += 8) for (var i = 0; i < w; i += 8) { x.fillStyle = ((i + j) / 8) % 2 ? "#262a31" : "#16181c"; x.fillRect(i, j, 8, 8); }
        }, [4, 1]);
        var carbon = K.mat("q-carbon", { color: 0xffffff, map: carbonTex, roughness: 0.3, metalness: 0.35, clearcoat: 0.9, clearcoatRoughness: 0.12 }, true);
        var metal = K.mat("q-bell", { color: 0x9aa2ad, roughness: 0.25, metalness: 1 });
        var dark = K.mat("q-dark", { color: 0x111318, roughness: 0.5, metalness: 0.3 });
        var rubber = K.mat("q-rubber", { color: 0x1a1a1c, roughness: 0.9, metalness: 0 });
        /* the shell: a rounded lower tub, a domed upper shell, a battery hatch with a seam and a grip */
        var tub = rbox(0.30, 0.06, 0.22, 0.025, trim); tub.position.y = 0.03; body.add(tub);
        var top = rbox(0.28, 0.06, 0.20, 0.03, shell); top.position.y = 0.085; body.add(top);
        var hatch = rbox(0.17, 0.012, 0.11, 0.008, shell); hatch.position.set(0, 0.118, -0.02); body.add(hatch);
        var seam = rbox(0.172, 0.004, 0.112, 0.004, dark); seam.position.set(0, 0.112, -0.02); body.add(seam);
        var grip = rbox(0.05, 0.008, 0.02, 0.004, dark); grip.position.set(0, 0.126, -0.06); body.add(grip);
        /* nose sensors: two dark stereo windows and front LEDs */
        [-1, 1].forEach(function (s) {
          var win = new THREE.Mesh(new THREE.CircleGeometry(0.012, 20), K.finish.glass(0x0b0f18)); win.position.set(s * 0.05, 0.075, 0.1105); body.add(win);
          var led = new THREE.Mesh(new THREE.SphereGeometry(0.006, 12, 8), new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff4e0, emissiveIntensity: 2.2 })); led.position.set(s * 0.12, 0.03, 0.105); body.add(led);
        });
        /* arms, motors and props */
        var a = o.arm;
        [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (p, k) {
          var tip = [p[0] * a * 0.7071, 0.07, p[1] * a * 0.7071];
          K.bar([p[0] * 0.11, 0.07, p[1] * 0.07], tip, 0.014, carbon, 10, body);
          var mount = K.cyl(0.03, 0.034, 0.025, trim, tip[0], 0.06, tip[2], 20, body);
          var bell = K.cyl(0.026, 0.026, 0.03, metal, tip[0], 0.085, tip[2], 24, body);
          var cap = K.cyl(0.008, 0.008, 0.012, dark, tip[0], 0.106, tip[2], 12, body);
          var hubY = 0.112;
          if (o.spin > 0.5) {
            var dm = new THREE.MeshPhysicalMaterial({ color: 0x20242a, transparent: true, opacity: 0.22, roughness: 0.4, depthWrite: false, side: THREE.DoubleSide });
            var disc = new THREE.Mesh(new THREE.RingGeometry(0.012, 0.19, 48), dm); disc.rotation.x = -Math.PI / 2; disc.position.set(tip[0], hubY, tip[2]); disc.castShadow = false; body.add(disc);
            var rim = new THREE.Mesh(new THREE.RingGeometry(0.175, 0.19, 64), new THREE.MeshBasicMaterial({ color: 0x3a3f48, transparent: true, opacity: 0.25, depthWrite: false, side: THREE.DoubleSide })); rim.rotation.x = -Math.PI / 2; rim.position.set(tip[0], hubY + 0.001, tip[2]); body.add(rim);
          } else if (o.props === 'folded') {
            for (var b2 = 0; b2 < 2; b2++) { var bl = rbox(0.18, 0.004, 0.028, 0.002, dark); var pv = new THREE.Group(); pv.position.set(tip[0], hubY, tip[2]);
              pv.rotation.y = Math.atan2(-tip[2], tip[0]) + Math.PI + (b2 ? 0.08 : -0.08); bl.position.x = 0.09; pv.add(bl); body.add(pv); }
          } else {
            var ang = k * 0.9 + 0.3;
            for (var b = 0; b < 2; b++) {
              var blade = rbox(0.18, 0.004, 0.028, 0.002, dark); var piv = new THREE.Group(); piv.position.set(tip[0], hubY, tip[2]); piv.rotation.y = ang + b * Math.PI;
              blade.position.x = 0.09; blade.rotation.x = (p[0] * p[1] > 0 ? 1 : -1) * 0.12; piv.add(blade); body.add(piv);
            }
          }
          /* landing legs under the front and rear arms */
          if (o.legs && p[1] > 0 || o.legs && p[1] < 0) {
            var lx = p[0] * 0.10, lz = p[1] * 0.08;
            K.bar([lx, 0.0, lz], [lx * 1.5, -legH + 0.01, lz * 1.4], 0.008, carbon, 8, body);
            var foot = new THREE.Mesh(new THREE.SphereGeometry(0.013, 12, 8), rubber); foot.position.set(lx * 1.5, -legH + 0.012, lz * 1.4); body.add(foot);
          }
        });
        /* GPS puck on a short mast at the rear: the receiver spoofing lies to */
        K.cyl(0.006, 0.006, 0.06, carbon, 0, 0.115, -0.07, 10, body);
        var puck = K.cyl(0.035, 0.038, 0.016, shell, 0, 0.175, -0.07, 28, body);
        var dome = new THREE.Mesh(new THREE.SphereGeometry(0.034, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), shell); dome.scale.y = 0.35; dome.position.set(0, 0.19, -0.07); body.add(dome);
        g.userData.gps = puck;
        if (o.open) { top.visible = false; hatch.visible = false; seam.visible = false; grip.visible = false;
          var fb = K.make('flight_board', {}); fb.scale.setScalar(1.6); fb.position.set(0, 0.062, 0.0); body.add(fb); g.userData.board = fb; }
        var yoke = rbox(0.05, 0.03, 0.03, 0.008, trim); yoke.position.set(0, -0.01, 0.075); body.add(yoke);
        var cam = rbox(0.055, 0.048, 0.05, 0.012, dark); cam.position.set(0, -0.045, 0.085); body.add(cam);
        var lensRing = K.cyl(0.018, 0.018, 0.012, metal, 0, -0.045, 0.114, 24, body); lensRing.rotation.x = Math.PI / 2;
        var lens = new THREE.Mesh(new THREE.CircleGeometry(0.014, 24), K.finish.glass(0x0a1020)); lens.position.set(0, -0.045, 0.1205); body.add(lens);
        /* rear status lamp, neutral white by default so the accent keeps its one meaning */
        var lamp = new THREE.Mesh(new THREE.SphereGeometry(0.008, 14, 10), new THREE.MeshStandardMaterial({ color: o.lamp || 0xfff4e0, emissive: o.lamp || 0xfff4e0, emissiveIntensity: 2.2 }));
        lamp.position.set(0, 0.06, -0.112); body.add(lamp);
        g.userData.lamp = lamp; g.userData.body = body; g.userData.camera = cam;
        if (o.ghost) {
          var gm = new THREE.MeshPhysicalMaterial({ name: 'ghost-frosted-glass', color: N.GHOST, metalness: 0, roughness: 0.35, transmission: 0.6, thickness: 0.02, ior: 1.45, transparent: true, opacity: 0.85, clearcoat: 1, clearcoatRoughness: 0.2, emissive: N.GHOST, emissiveIntensity: 0.08 });
          g.traverse(function (m) { if (m.isMesh) { m.material = gm; m.castShadow = false; m.receiveShadow = false; } });
          g.userData.ghost = true; return g;
        }
        return shadowAll(g);
      }
    });

    /* A DOWNED LIVE OAK. A kit live_oak laid on its side along +x with its crown crushed against the ground, and a torn
     * gumbo root plate standing up at the trunk base. About 12 x 4 x 9 m. Options: seed (the oak), plate (root plate
     * diameter in metres, default 3.2), height (the oak's height before it fell, default 9). */
    K.define("downed_oak", {
      size: [12, 4, 9], options: { seed: 2, plate: 3.2, height: 9 },
      note: "A fallen live oak on its side along +x, crown on the ground, a torn gumbo clay root plate standing at the trunk base (-x). Drawn to illustrate.",
      make: function (o) {
        o = Object.assign({ seed: 2, plate: 3.2, height: 9 }, o || {});
        var g = new THREE.Group(), tree = K.make("live_oak", { seed: o.seed, height: o.height });
        var holder = new THREE.Group(); holder.add(tree); tree.position.y = -0.25; tree.scale.x = 0.32; /* the crown crushed flat against the ground once it lies on its side */ holder.rotation.z = -Math.PI / 2 + 0.08; holder.position.set(-o.height * 0.5 + 0.8, 1.0, 0); g.add(holder);
        var clay = K.mat("rr-gumbo", { color: N.GUMBO, roughness: 0.95 }), root = K.mat("rr-root", { color: 0x5b3f2a, roughness: 0.9 });
        var pg = new THREE.CylinderGeometry(o.plate / 2, o.plate / 2 * 0.86, 0.6, 28, 3), pos = pg.attributes.position, rr = N.rng(o.seed + 9);
        for (var i = 0; i < pos.count; i++) { var x = pos.getX(i), z = pos.getZ(i), rad = Math.hypot(x, z); if (rad > 0.2) { var k = 1 + (rr() - 0.5) * 0.22; pos.setX(i, x * k); pos.setZ(i, z * k); pos.setY(i, pos.getY(i) + (rr() - 0.5) * 0.15); } }
        pg.computeVertexNormals();
        var plate = new THREE.Mesh(pg, clay); plate.rotation.z = Math.PI / 2 - 0.12; plate.position.set(-o.height * 0.5 + 0.2, o.plate / 2 - 0.15, 0); g.add(plate);
        for (var r = 0; r < 16; r++) { var a = rr() * Math.PI * 2, rad2 = o.plate * (0.25 + rr() * 0.28);
          K.bar([plate.position.x - 0.2, plate.position.y + Math.sin(a) * rad2 * 0.6, Math.cos(a) * rad2 * 0.6], [plate.position.x - 0.5 - rr() * 0.6, plate.position.y + Math.sin(a) * rad2, Math.cos(a) * rad2], 0.03 + rr() * 0.05, root, 6, g); }
        var pit = new THREE.Mesh(new THREE.CircleGeometry(o.plate * 0.45, 24), K.mat("rr-pit", { color: 0x4a3020, roughness: 1 })); pit.rotation.x = -Math.PI / 2; pit.position.set(-o.height * 0.5 - o.plate * 0.35, 0.01, 0); g.add(pit);
        return shadowAll(g);
      }
    });

    /* A RESCUE HELMET. 0.30 x 0.22 x 0.25 m: a rounded shell with a brim, a ratchet band, a chin strap and a blank badge
     * recess on the front (+z). Options: color (shell hex, never red), seed. Origin under the brim, crown up. */
    K.define("rescue_helmet", {
      size: [0.30, 0.22, 0.25], options: { color: 0xf2f2ee, seed: 1 },
      note: "An illustrative rescue helmet: rounded shell, brim, ratchet band, chin strap, blank badge recess. Never red. Drawn to no maker's design.",
      make: function (o) {
        o = Object.assign({ color: 0xf2f2ee, seed: 1 }, o || {});
        var g = new THREE.Group(), shell = K.mat("rr-helm-" + o.color, { color: o.color, roughness: 0.28, clearcoat: 0.9, clearcoatRoughness: 0.12 }, true);
        var dark = K.mat("rr-helm-band", { color: 0x1d1f24, roughness: 0.6 });
        var dome = new THREE.Mesh(new THREE.SphereGeometry(0.13, 36, 18, 0, Math.PI * 2, 0, Math.PI / 2), shell); dome.scale.set(1, 1.15, 1.12); dome.position.y = 0.035; g.add(dome);
        var ridge = new THREE.Mesh(new THREE.TorusGeometry(0.13, 0.008, 8, 40, Math.PI), shell); ridge.rotation.y = Math.PI / 2; ridge.scale.set(1.12, 1.15, 1); ridge.position.y = 0.035; g.add(ridge);
        var brim = new THREE.Mesh(new THREE.CylinderGeometry(0.155, 0.16, 0.012, 40), shell); brim.scale.set(1, 1, 1.15); brim.position.y = 0.034; g.add(brim);
        var band = new THREE.Mesh(new THREE.CylinderGeometry(0.118, 0.118, 0.022, 32, 1, true), dark); band.position.y = 0.02; g.add(band);
        var badge = rbox(0.06, 0.04, 0.01, 0.006, K.mat("rr-helm-badge", { color: 0xd8d8d0, roughness: 0.5 })); badge.position.set(0, 0.075, 0.142); badge.rotation.x = -0.35; g.add(badge);
        K.bar([-0.1, 0.02, 0.02], [-0.06, -0.08, 0.05], 0.006, dark, 6, g); K.bar([0.1, 0.02, 0.02], [0.06, -0.08, 0.05], 0.006, dark, 6, g);
        return shadowAll(g);
      }
    });

    /* AN ORTHO PLATE. An anodised aluminium plate w x 0.003 x w m carrying a drawn aerial patch on its top face, 1 mm edge
     * round. Options: w (0.40), seed (the patch), tint (anodised edge hex). */
    K.define("ortho_plate", {
      size: [0.40, 0.003, 0.40], options: { w: 0.40, seed: 3, tint: 0x9fb4d8 },
      note: "An anodised plate carrying a drawn aerial neighbourhood patch on its top face. Drawn to illustrate, no real place.",
      make: function (o) {
        o = Object.assign({ w: 0.40, seed: 3, tint: 0x9fb4d8 }, o || {});
        var g = new THREE.Group(), edge = K.mat("rr-anod-" + o.tint, { color: o.tint, metalness: 0.85, roughness: 0.3 });
        var body = rbox(o.w, 0.003, o.w, 0.001, edge); body.position.y = 0.0015; g.add(body);
        var face = new THREE.Mesh(new THREE.PlaneGeometry(o.w * 0.96, o.w * 0.96), K.mat("rr-face-" + o.seed, { color: 0xffffff, map: N.aerialTex(THREE, o.seed), roughness: 0.4, clearcoat: 0.6 }, true));
        face.rotation.x = -Math.PI / 2; face.position.y = 0.0032; g.add(face);
        return shadowAll(g);
      }
    });

    /* A PLATE RACK. A powder coated steel cradle holding n ortho plates on edge at a pitch, running along x. Options: n,
     * pitch (0.008 m), w (plate width 0.40), lift (index of a plate removed from the rack, -1 none), color (cradle hex).
     * userData.slot(i) gives a plate's centre. */
    K.define("plate_rack", {
      size: [2.2, 0.46, 0.5], options: { n: 100, pitch: 0.008, w: 0.40, lift: -1, color: 0x2e3a8c },
      note: "A steel cradle of n anodised ortho plates standing on edge at a fixed pitch along x. n is read from a figure by the frame.",
      make: function (o) {
        o = Object.assign({ n: 100, pitch: 0.008, w: 0.40, lift: -1, color: 0x2e3a8c }, o || {});
        var g = new THREE.Group(), L = o.n * o.pitch + 0.08, steel = K.mat("rr-cradle-" + o.color, { color: o.color, roughness: 0.55, metalness: 0.4 });
        K.box(L, 0.03, o.w * 0.9, steel, 0, 0, 0, 0.006, g);
        [-1, 1].forEach(function (s) { K.box(L, 0.05, 0.02, steel, 0, 0.03, s * o.w * 0.45, 0.004, g); K.box(0.02, 0.12, o.w * 0.9, steel, s * L / 2, 0.03, 0, 0.004, g); });
        var edges = [0x9fb4d8, 0xb8c2d6, 0x8fa6cf, 0xa9b7e0], rr = N.rng(11), slots = [];
        for (var i = 0; i < o.n; i++) {
          var x = -L / 2 + 0.04 + i * o.pitch; slots.push([x, 0.03 + o.w / 2, 0]);
          if (i === o.lift) continue;
          var p = rbox(0.003, o.w, o.w * 0.92, 0.001, K.mat("rr-anod-" + edges[i % 4], { color: edges[i % 4], metalness: 0.85, roughness: 0.25 + rr() * 0.15 }));
          p.position.set(x, 0.03 + o.w / 2 + (rr() - 0.5) * 0.004, (rr() - 0.5) * 0.004); g.add(p);
        }
        g.userData.slot = function (i) { return slots[i]; }; g.userData.count = o.n - (o.lift >= 0 ? 1 : 0);
        return shadowAll(g);
      }
    });
  };
  N.studioOpts = function (o) { o = o || {}; return { tone: N.TONE, w: (o.w || 4.2) * 1.6, d: (o.d || 3.2) * 1.4, h: 3.2, radius: 0.9, env: 0.95, hemi: 0.7 }; };
  N.roomOpts = function (o) {
    o = o || {};
    return { w: o.w || 4.2, d: o.d || 3.2, h: 3.0, floor: "concrete", wall: o.wall || 0x16161b, window: null, ceiling: o.ceiling !== false, light: o.light == null ? 0.12 : o.light };
  };
  /* a parallel camera `span` metres wide, for a frame that compares lengths and must not foreshorten them */
  N.ortho = function (THREE, R, span) { var w = span / 2, h = w * N.H / N.W; R.camera = new THREE.OrthographicCamera(-w, w, h, -h, 0.01, 40); return R.camera; };
  /* an SVG leader from a label's anchor to a world point, registered for qa's leader check */
  N.leader = function (THREE, R, from, world, what) {
    var at = N.project(THREE, R, world), s = N.svg(), l = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    l.setAttribute("points", from[0] + "," + from[1] + " " + at[0] + "," + at[1]); l.setAttribute("fill", "none"); l.setAttribute("stroke", N.P.ink); l.setAttribute("stroke-width", "3"); l.setAttribute("stroke-linecap", "round");
    s.appendChild(l); (window.__txLeaders = window.__txLeaders || []).push({ target: what, at: at, to: at }); return at;
  };
  /* A CAMERA BEARING FROM THE SUN: the horizontal direction `deg` degrees clockwise (to the right) of the sun's own
   * bearing, so a frame can put the warm seam at its left edge by looking a little right of the sun. */
  N.bearing = function (TXT, deg) {
    var sd = TXT.sunDir(), hx = sd.x, hz = sd.z, n = Math.hypot(hx, hz) || 1; hx /= n; hz /= n;
    var a = -deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
    return [hx * c - hz * s, hz * c + hx * s];
  };
  N.dress = function (cx, o) { o = o || {}; if (TXLOOK.active()) { TXLOOK.footWash(cx, { a: 0.42, height: 230 }); N.typeDark(cx, o); return cx; } N.post(cx, { a: 0.3, veil: 0.35, veilH: 240 }); N.footWash(cx, { a: o.foot || 0.6 }); N.typeDark(cx, { fade: o.fade == null ? 120 : o.fade, pad: o.pad, a: 0.6 }); return cx; };
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
    /* LOOK V2: no dark room. The studio keeps its environment; a frame's call trims the env a touch at most. */
    if (TXLOOK.active()) { if ('environmentIntensity' in R.scene) R.scene.environmentIntensity = Math.max(0.75, R.scene.environmentIntensity || 0.9); return R; }
    R.scene.environmentIntensity = o.env == null ? 0.12 : o.env;
    R.scene.traverse(function (l) { if (!l.isLight) return; if (l.isHemisphereLight || l.isAmbientLight) l.intensity *= (o.amb == null ? 0.35 : o.amb);
      else if (l.isDirectionalLight && !l.castShadow) l.intensity *= (o.fill == null ? 0.4 : o.fill); });
    return R;
  };

  /* THE TYPE BAND GOES TO THE DARK, darken only: a near black gradient from the top of the frame to just under the dek,
   * so the room's far edges behind the type sink rather than strike through it. */
  N.typeDark = function (cx, o) {
    o = o || {};
    if (TXLOOK.active()) return TXLOOK.typeWash(cx, { a: 0.5, fade: Math.max(200, o.fade || 0), pad: o.pad });
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
    ].join("\n") + "\n" + TXLOOK.css(N.TONE);
  };
  /* the bespoke type seat: a soft tint in the tone's deep hue around wherever this frame put its type */
  N.seat = function (cx, o) { return TXLOOK.typeSeat(cx, Object.assign({ tone: N.TONE }, o || {})); };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) { d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px"; });
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS(); document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: N.P.dek });
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
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = N.lowRGB();
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
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(" + N.lowRGB() + "," + (Math.min(0.5, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
  };
  /* a darken-only wash under the footer, so the site line and the claim ids sit on a dark field and no edge strikes them */
  N.footWash = function (cx, o) {
    o = o || {};
    [[o.x == null ? 850 : o.x, 1300, o.r || 460], [180, 1300, 300]].forEach(function (c) {
      var g = cx.createRadialGradient(c[0], c[1], 20, c[0], c[1], c[2]);
      var lc = N.lowRGB(), fa = (o.a || 0.72) * 0.6; g.addColorStop(0, "rgba(" + lc + "," + fa + ")"); g.addColorStop(0.55, "rgba(" + lc + "," + (fa * 0.6) + ")"); g.addColorStop(1, "rgba(" + lc + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, N.H);
    });
  };
  N.lowRGB = function () { var h = N.P.low.replace("#", ""); return [0, 2, 4].map(function (i) { return parseInt(h.slice(i, i + 2), 16); }).join(","); };
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
