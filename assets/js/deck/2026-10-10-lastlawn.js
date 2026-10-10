/* deck/2026-10-10-lastlawn.js — the chassis for the 2026-10-10 deck: Austin Community College says it is
 * developing what it calls its first-ever AI policy under a five rule framework it calls TRUST, and has
 * opened it to a town hall on October 12th (tx-2026-0212).
 *
 * THE WORLD. lastLight, the house register: a near black sky with one warm seam low in the west. THE
 * LIGHT IS THE SUN'S OWN at the town hall's start, 6:30 p.m. Central Daylight Time on October 12th, over
 * the Travis County centroid in the committed gazetteer, computed in the run's compute.py from NOAA's
 * solar equations: elevation 6.4 degrees, bearing 257.7, which is engine azimuth -77.7. So the key is
 * low in the west south west, on camera LEFT whenever the camera looks north, every lit face is the west
 * face, and every cast runs long to the east north east.
 *
 * DIRECTIONS. +x is east, +z is south. az runs clockwise from +z toward +x, so the key sits at
 * (sin az, ., cos az): with az -77.7 that is west and a little south of the subject, and low.
 *
 * THE HERO OBJECT. The kit's `student_desk` with its kit `laptop`, and on its top one blank letter sheet
 * (`policy_sheet`, built here). The desk faces -z (the student sits on +z). Its STATE carries the deck: the
 * lid lit or shut, the seat empty or taken, and where it stands on the walk.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `paver_walk` (a walk of sawn limestone
 * pavers, one per day, with polished granite inlays on chosen days), `policy_sheet` (a blank letter sheet),
 * `paperback` (a paperback with a blank cover) and `wall_clock` (a classroom clock, hands set by angle).
 * Each is built in the kit's conventions so Phase 17 can lift it into assets/js/kit/ unchanged.
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, written in the frame's code where figure_bearing.py
 * checks them against figures.json. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("lastlawn.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "lastlawn",
    light: { az: -77.7, el: 6.4 },
    sky: { preset: "lastLight" },
    ground: "#0B0A10",
    material: "#C4AB88",
    accent: "#9A3B2A",
    grade: {
      exposure: 0,
      saturation: 1.04,
      contrast: 1.08,
      filmic: true,
      lift: [0.004, 0.003, 0.006],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.85, strength: 0.22, radius: 12 },
      grain: { amount: 0.02, size: 2, seed: 20261010 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261010;
  N.ACCENT = 0x9a3b2a;       /* Capitol granite, the deck's one accent: the event days inlaid in the walk */
  N.INK = "#EEEAE0";
  N.PAGE = 0xd8e2ea;         /* the lid's dim cool page */

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---------------------------------------------------------------- textures */
  /* SAWN AUSTIN LIMESTONE, one paver's face: a warm cream ground with shell grit, a few darker fossil
   * pocks, faint saw marks, and the edges worn darker where feet and soil meet it */
  N.stoneTex = function (THREE) {
    if (N._stone) return N._stone;
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(17);
    x.fillStyle = "#cfc3aa"; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 9000; i++) { var v = 150 + Math.floor(r() * 90); x.fillStyle = "rgba(" + v + "," + (v - 8) + "," + (v - 26) + "," + (0.2 + r() * 0.35).toFixed(2) + ")"; x.beginPath(); x.arc(r() * 512, r() * 512, 0.5 + r() * 1.6, 0, 7); x.fill(); }
    for (var j = 0; j < 60; j++) { x.fillStyle = "rgba(92,78,58," + (0.1 + r() * 0.18).toFixed(2) + ")"; x.beginPath(); x.ellipse(r() * 512, r() * 512, 2 + r() * 7, 1 + r() * 4, r() * 3, 0, 7); x.fill(); }
    for (var k = 0; k < 34; k++) { x.strokeStyle = "rgba(120,104,80," + (0.12 + r() * 0.12).toFixed(2) + ")"; x.lineWidth = 0.8; x.beginPath(); var y0 = r() * 512; x.moveTo(0, y0); x.lineTo(512, y0 + (r() - 0.5) * 6); x.stroke(); }
    var g = x.createRadialGradient(256, 256, 150, 256, 256, 380); g.addColorStop(0, "rgba(40,32,24,0)"); g.addColorStop(1, "rgba(40,32,24,0.55)"); x.fillStyle = g; x.fillRect(0, 0, 512, 512);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    N._stone = t; return t;
  };
  N.stoneBump = function (THREE) {
    if (N._sbump) return N._sbump;
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(19);
    x.fillStyle = "#808080"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < 5000; i++) { var v = 90 + Math.floor(r() * 80); x.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; x.fillRect(r() * 256, r() * 256, 1 + r() * 2, 1 + r() * 2); }
    for (var j = 0; j < 40; j++) { x.fillStyle = "rgba(40,40,40,0.6)"; x.beginPath(); x.arc(r() * 256, r() * 256, 1 + r() * 3, 0, 7); x.fill(); }
    var t = new THREE.CanvasTexture(c); N._sbump = t; return t;
  };
  N.graniteTex = function (THREE) {
    if (N._gran) return N._gran;
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(23);
    x.fillStyle = "#9a3b2a"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < 2600; i++) {
      var k = r(), col = k < 0.5 ? "rgba(132,48,34," : (k < 0.9 ? "rgba(176,74,54," : "rgba(110,52,42,");
      x.fillStyle = col + (0.2 + r() * 0.25).toFixed(2) + ")"; x.beginPath(); x.arc(r() * 256, r() * 256, 0.5 + r() * 1.2, 0, 7); x.fill();
    }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; N._gran = t; return t;
  };
  /* THE PAGE ON THE LID, a drawn page with no legible word: a header bar, grey text bars. The title a
   * frame needs legible is DOM type set on the lid's projected rect, never pixels on this texture. */
  N.pageTex = function (THREE, o) {
    o = o || {};
    var c = document.createElement("canvas"); c.width = 1184; c.height = 740; var x = c.getContext("2d"), r = lcg(o.seed || 7);
    x.fillStyle = "#e9eef2"; x.fillRect(0, 0, 1184, 740);
    x.fillStyle = "#d5dde3"; x.fillRect(0, 0, 1184, 46);
    if (!o.titleBlank) { x.fillStyle = "#c4ced6"; x.fillRect(140, 120, 904, 150); }
    for (var l = 0; l < 13; l++) { x.fillStyle = "#cfd7dd"; x.fillRect(140, 320 + l * 30, 760 + Math.floor(r() * 140), 11); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  };

  /* ---------------------------------------------------------------- the kit models this deck builds */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.paver_walk) return;
    var stone = K.mat("ll-stone", { color: 0xffffff, map: N.stoneTex(THREE), bumpMap: N.stoneBump(THREE), bumpScale: 1.4, roughness: 0.9, metalness: 0.0 });
    /* the event days' granite as printed: unlit at the deck's accent, so neither the pool nor the dark can shift it,
     * with a faint grain of its own so it reads as stone and not as paint */
    var gt = N.graniteTex(THREE);
    var gran = new THREE.MeshBasicMaterial({ color: 0xffffff, map: gt, toneMapped: false });
    K.define("paver_walk", {
      size: [1.0, 0.03, 15.5],
      options: { n: 14, pitch: 1.12, w: 1.0, d: 0.95, inlays: [], seed: 5 },
      note: "A walk of sawn limestone pavers laid along -z from the origin, paver i centred at z = -i * pitch, each w x d and 3 cm proud of the lawn with a 6 mm arris, a little turned and offset by seed so the row reads laid by hand. inlays lists the indices that carry a flush inset of polished sunset red granite, the paver less an 8 cm limestone border. userData.paver(i) gives a paver's top centre [x, y, z].",
      make: function (o, r) {
        var g = new THREE.Group(), tops = [];
        for (var i = 0; i < o.n; i++) {
          var dx = (r() - 0.5) * 0.06, dz = (r() - 0.5) * 0.04, rot = (r() - 0.5) * 0.03, h = 0.05 + r() * 0.008;
          var p = K.box(o.w, h, o.d, stone, dx, -0.012, -i * o.pitch + dz, 0.014, g); p.rotation.y = rot; p.userData.paver = true; h -= 0.012;
          tops.push([dx, h, -i * o.pitch + dz]);
          if (o.inlays.indexOf(i) >= 0) { var q = K.box(o.w - 0.16, 0.004, o.d - 0.16, gran, dx, h - 0.003, -i * o.pitch + dz, 0.0015, g); q.rotation.y = rot; }
        }
        g.userData.keepOrigin = true; g.userData.n = tops.length;
        g.userData.paver = function (i) { return tops[i].slice(); };
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = false; m.receiveShadow = true; } });
        return g;
      }
    });
    var paper = K.mat("ll-paper", { color: 0xf2efe6, roughness: 0.9, metalness: 0.0 });
    K.define("policy_sheet", {
      size: [0.216, 0.004, 0.279],
      options: { curl: 0.004, seed: 3 },
      note: "A blank US letter sheet, 0.216 x 0.279 m, lying flat with its far corner lifted by curl metres. Nothing is printed on it.",
      make: function (o) {
        var geo = new THREE.PlaneGeometry(0.216, 0.279, 8, 10); geo.rotateX(-Math.PI / 2);
        var pos = geo.attributes.position;
        for (var i = 0; i < pos.count; i++) { var u = (pos.getX(i) + 0.108) / 0.216, v = (0.1395 - pos.getZ(i)) / 0.279; pos.setY(i, 0.0006 + o.curl * Math.pow(u * v, 3)); }
        geo.computeVertexNormals();
        var m = new THREE.Mesh(geo, paper); m.receiveShadow = true; m.castShadow = true;
        var g = new THREE.Group(); g.add(m); return g;
      }
    });
    var cover = K.mat("ll-cover", { color: 0x56706a, roughness: 0.6, metalness: 0.0 });
    var block = K.mat("ll-block", { color: 0xe2d8c2, roughness: 0.95, metalness: 0.0 });
    K.define("paperback", {
      size: [0.108, 0.02, 0.175],
      options: { seed: 2 },
      note: "A closed paperback lying flat, 108 x 175 mm and 18 mm thick: a soft cover over a page block whose edges show on three sides. The cover is blank, with no title and no art.",
      make: function () {
        var g = new THREE.Group();
        K.box(0.106, 0.0165, 0.172, block, 0.001, 0.0008, 0, 0.001, g);
        K.box(0.108, 0.0008, 0.175, cover, 0, 0, 0, 0, g);
        K.box(0.108, 0.0008, 0.175, cover, 0, 0.0173, 0, 0, g);
        K.box(0.003, 0.0181, 0.175, cover, -0.0525, 0, 0, 0.001, g);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });
    var rim = K.mat("ll-rim", { color: 0x141416, roughness: 0.4, metalness: 0.2 });
    var face = K.mat("ll-face", { color: 0xe9e6dd, roughness: 0.6, metalness: 0.0 });
    var hand = K.mat("ll-hand", { color: 0x111113, roughness: 0.5, metalness: 0.1 });
    K.define("wall_clock", {
      size: [0.36, 0.36, 0.05],
      anchor: "base",
      options: { d: 0.36, minute: 0, hour: 0, seed: 1 },
      note: "A school wall clock facing +z, origin at the centre of its back face: a black rim, a white face, twelve ticks and no numerals. minute and hour are the hands' angles in degrees clockwise from twelve.",
      make: function (o) {
        var g = new THREE.Group(), R = o.d / 2;
        var rg = new THREE.Mesh(new THREE.CylinderGeometry(R, R, 0.05, 48), rim); rg.rotation.x = Math.PI / 2; rg.position.z = 0.025; g.add(rg);
        var f = new THREE.Mesh(new THREE.CircleGeometry(R * 0.9, 48), face); f.position.z = 0.0505; g.add(f);
        for (var t = 0; t < 12; t++) { var a = t * Math.PI / 6, tk = new THREE.Mesh(new THREE.PlaneGeometry(t % 3 ? 0.006 : 0.011, t % 3 ? 0.02 : 0.03), hand); tk.position.set(Math.sin(a) * R * 0.78, Math.cos(a) * R * 0.78, 0.051); tk.rotation.z = -a; g.add(tk); }
        function arm(len, wid, deg, z) { var m = new THREE.Mesh(new THREE.PlaneGeometry(wid, len), hand); m.geometry.translate(0, len / 2 - 0.012, 0); m.rotation.z = -deg * Math.PI / 180; m.position.z = z; g.add(m); }
        arm(R * 0.5, 0.014, o.hour, 0.052); arm(R * 0.72, 0.009, o.minute, 0.053);
        g.userData.keepOrigin = true;
        return g;
      }
    });
  };

  /* ---------------------------------------------------------------- the world, as calls */
  N.lawn = function (o) { o = o || {}; return N.TXT.ground(N.R, { surface: "lawn", size: o.size || 3000, tile: o.tile || 5, seed: o.seed || 3 }); };
  N.grass = function (area, o) { o = o || {}; return N.TXT.scatter(N.R, { kind: "grass", count: o.count || 5000, area: area, avoid: o.avoid, seed: o.seed || 9, scale: o.scale || [0.18, 0.36], colors: [0x3e4a2c, 0x34402a, 0x4a5232] }); };
  N.oak = function (x, z, o) { o = o || {}; var t = N.K.make("live_oak", Object.assign({ seed: 4 }, o)); t.position.set(x, 0, z); N.TXT.add(N.R, t); N.TXT.contact(N.R, t); return t; };
  N.walk = function (o) { o = o || {}; var w = N.K.make("paver_walk", Object.assign({ seed: 5 }, o)); N.TXT.add(N.R, w); return w; };
  /* THE HERO: the kit desk with its laptop lit and the blank sheet on the top, to the left of the laptop
   * and a little turned, its outer edge over the top's edge as a sheet on a small desk lies. */
  N.desk = function (o) {
    o = o || {};
    var d = N.K.make("student_desk", { seed: o.seed || 2, top: o.top == null ? 0x6f665a : o.top, laptop: o.laptop === undefined ? "doc" : o.laptop, open: o.open == null ? 110 : o.open, detail: o.detail || "full" });
    var lp = d.userData.laptop;
    if (lp && o.dim !== false) lp.traverse(function (m) { if (m.isMesh && m.geometry && m.geometry.parameters && m.geometry.parameters.width === 0.296) { m.material = m.material.clone(); if (m.material.color) m.material.color.multiplyScalar(o.screen == null ? 0.62 : o.screen); } });
    if (o.sheet !== false && lp) {
      var s = N.K.make("policy_sheet", { seed: 3 });
      s.position.set(lp.position.x - 0.255, lp.position.y + 0.0004, lp.position.z + 0.04); s.rotation.y = 0.16; d.add(s); d.userData.sheet = s;
    }
    return d;
  };
  /* a page of the drawn kind swapped onto the lid's display, dimmed to `bright` */
  N.page = function (desk, o) {
    o = o || {}; var T = N.T, lp = desk.userData.laptop, hit = null;
    lp.traverse(function (m) { if (m.isMesh && m.geometry && m.geometry.parameters && m.geometry.parameters.width === 0.296) hit = m; });
    if (!hit) throw new Error("no display on the laptop");
    var mat = new T.MeshBasicMaterial({ map: N.pageTex(T, o), toneMapped: true }); mat.color.setScalar(o.bright == null ? 0.7 : o.bright);
    hit.material = mat; return hit;
  };
  N.lidLight = function (desk, o) {
    o = o || {}; var T = N.T, lp = desk.userData.laptop; if (!lp) return null;
    desk.updateMatrixWorld(true);
    var p = new T.Vector3(0, 0.12, 0.14).applyMatrix4(lp.matrixWorld);
    var L = new T.PointLight(N.PAGE, (o.i || 0.6) * 10, o.range || 1.4, 2); L.position.copy(p); L.castShadow = false; N.R.scene.add(L); return L;
  };
  /* WHERE THE SEAT IS. K.make recentres a model's children on its bounds, and the desk publishes its
   * laptopAt and seatAt in its own unshifted frame, so the shift is read off the laptop it carries and
   * applied to the seat. Returns a world point after the desk is placed. */
  N.seat = function (desk) {
    var T = N.T, lp = desk.userData.laptop, a = desk.userData.laptopAt, st = desk.userData.seatAt;
    var dx = lp ? lp.position.x - a[0] : 0, dz = lp ? lp.position.z - (a[2] + 0.02) : 0;
    desk.updateMatrixWorld(true);
    return new T.Vector3(st[0] + dx, st[1], st[2] + dz).applyMatrix4(desk.matrixWorld);
  };
  /* the lid's display mesh, for a frame that needs its projected rect */
  N.display = function (desk) {
    var hit = null; desk.userData.laptop.traverse(function (m) { if (m.isMesh && m.geometry && m.geometry.parameters && m.geometry.parameters.width === 0.296) hit = m; });
    return hit;
  };
  /* the projected rect of a mesh's plane in frame px, [x0, y0, x1, y1] */
  N.rectOf = function (mesh) {
    var T = N.T, gp = mesh.geometry.parameters, w = gp.width / 2, h = gp.height / 2, xs = [], ys = [];
    mesh.updateMatrixWorld(true);
    [[-w, -h], [w, -h], [w, h], [-w, h]].forEach(function (c) { var v = new T.Vector3(c[0], c[1], 0).applyMatrix4(mesh.matrixWorld); var q = N.project(T, N.R, [v.x, v.y, v.z]); xs.push(q[0]); ys.push(q[1]); });
    return [Math.min.apply(null, xs), Math.min.apply(null, ys), Math.max.apply(null, xs), Math.max.apply(null, ys)];
  };
  /* a DOM leader from a label's edge to a projected point, ending short of the glyphs */
  N.leader = function (svg, from, to) {
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

  /* ---------------------------------------------------------------- the place, as primitives */
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 12, mapSize: map || 2048, radius: 5 }) });
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
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "6,5,9";
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
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(6,5,9," + (Math.min(0.5, o.veil == null ? 0.38 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 2.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#DCD6C8", halo = "rgba(3,4,8,0.6)", halo2 = "rgba(3,4,8,0.45)", acc = "#" + ("000000" + N.ACCENT.toString(16)).slice(-6).toUpperCase();
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#0B0A10; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; color:' + ink + '; white-space:nowrap; z-index:12; }',
      '.lab.acc { color:' + acc + '; }',
      ".hook, .dek, .tx-site, .kick, .src, .cap, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#DCD6C8" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 96, max: 128, maxLines: 2 });
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
