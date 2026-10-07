/* deck/2026-10-07-portalpha.js — the chassis for the 2026-10-07 deck: Saronic broke ground on Port
 * Alpha at the Port of Brownsville on September 30th, a shipyard it calls software defined, built to
 * make autonomous, autonomy-capable and manned ships, on 835 acres where Cameron County had approved a
 * 95% abatement in June (tx-2026-0204).
 *
 * THE WORLD. The Brownsville Ship Channel at midday in Gulf humidity. highNoon, tuned once here: the
 * haze pulled to a humid Gulf grey, the horizon softened, the sun high in the south south east at az 25
 * and el 58, so every cast runs north north west, short and dark. The water carries the sky, which is
 * why this world and no other: the probe in out/2026-10-07/tmp/probe/ put the same hull in four worlds
 * and only noon made the channel read as water and the hull as steel. Type is dark ink on the sky band.
 *
 * DIRECTIONS. +x is east, +z is south. az runs clockwise from +z toward +x, so the key sits at
 * (sin az, ., cos az), south and a little east. The yard bank's edge lies on z = 0 and the yard's land
 * stands N.BANK metres above the water to the north (negative z). The channel runs east and west and
 * is N.CHANNEL metres wide (illustrative); its far bank lies south at z = N.CHANNEL.
 *
 * THE LIGHT DECK CAP. 2026-09-30 sits in the eight run window at a deck median of 60.6, so this deck
 * must measure under 60. The probe measured 64.7 at the world's own exposure. N.EXPOSURE takes the
 * whole deck down together through the renderer's tone curve, never a multiply on the pixels.
 *
 * THE HERO OBJECT. `autonomous_vessel`, a windowless hull built in the kit's conventions so Phase 17
 * can lift it into assets/js/kit/ unchanged. It is ILLUSTRATIVE: 46 m long, 9.6 m in beam, 4.6 m deep,
 * drawn to the type, not to any Saronic design, and no frame prints a length. Nothing on it is sized
 * for a person: no window, no ladder, no lifeline, a toe rail only. Its STATE carries the deck: afloat,
 * close at the mast, broadside with its payload as one steel block, on keel blocks out of the water,
 * small at the bank of its site, and gone at the close.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having no vessel, no keel block and no bank:
 * `autonomous_vessel`, `keel_block_line` and `riprap_bank`, below.
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, written in the frame's code where figure_bearing.py
 * checks them against figures.json, and converted here by exact definitions (N.ft, N.acre). The chassis
 * types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("portalpha.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "portalpha",
    light: { az: 25, el: 58 },
    sky: { preset: "highNoon", horizon: 0xd6dde0, haze: 0xd3d8d4, fogDensity: 0.0019, clouds: 0.34 },
    ground: "#5E6266",
    material: "#6E757C",
    accent: "#4E5FA8",
    grade: {
      exposure: -0.04,
      saturation: 1.02,
      contrast: 1.07,
      filmic: true,
      lift: [0.004, 0.005, 0.007],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.16,
      bloom: { threshold: 0.9, strength: 0.12, radius: 12 },
      grain: { amount: 0.018, size: 2, seed: 20261007 },
      aberration: 0,
      dither: true,
      sharpen: 0.16
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261007;
  N.ACCENT = 0x4e5fa8;
  N.INK = "#15171C";
  N.BANK = 2.2;        /* the yard's land above the water, illustrative */
  N.CHANNEL = 180;     /* the channel's width, illustrative */
  N.FAR = 1.4;         /* the far bank above the water */

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* EXACT UNIT DEFINITIONS, the same two compute.py states */
  N.ft = function (f) { return f * 0.3048; };
  N.acre = function (a) { return a * 4046.8564224; };

  /* ---------------------------------------------------------------- textures */
  /* PLATE: haze grey plate with seams every few metres, weld lines, drain streaks, a black boot top at
   * the waterline and red antifouling below it. u runs along the hull in metres / 12, v from keel 0 to
   * deck 1. */
  N.plateTex = function (THREE, o) {
    var c = document.createElement("canvas"); c.width = 1024; c.height = 256; var x = c.getContext("2d"), r = lcg(o.seed || 9);
    x.fillStyle = o.paint || "#6e757c"; x.fillRect(0, 0, 1024, 256);
    for (var i = 0; i < 1600; i++) { x.fillStyle = "rgba(" + (r() < 0.5 ? "20,22,24" : "220,225,230") + "," + (0.02 + r() * 0.035).toFixed(3) + ")"; x.fillRect(r() * 1024, r() * 256, 2 + r() * 40, 1 + r() * 6); }
    x.strokeStyle = "rgba(25,27,30,0.42)"; x.lineWidth = 1.2;
    for (var k = 0; k < 1024; k += 1024 / (o.plates || 8)) { x.beginPath(); x.moveTo(k + (r() - 0.5) * 2, 0); x.lineTo(k, 256); x.stroke(); }
    for (var j = 40; j < 256; j += 52) { x.beginPath(); x.moveTo(0, j); x.lineTo(1024, j); x.stroke(); }
    for (var s = 0; s < 110; s++) { var sx = r() * 1024, sy = r() * 120; var g = x.createLinearGradient(sx, sy, sx, sy + 30 + r() * 60); g.addColorStop(0, "rgba(80,58,40,0.20)"); g.addColorStop(1, "rgba(80,58,40,0)"); x.fillStyle = g; x.fillRect(sx, sy, 1 + r() * 2, 30 + r() * 60); }
    var wl = o.waterline == null ? 0.5 : o.waterline, yw = 256 * (1 - wl);
    x.fillStyle = o.bottom || "#6a2f26"; x.fillRect(0, yw + 7, 1024, 256 - yw);
    for (var b = 0; b < 400; b++) { x.fillStyle = "rgba(40,36,30," + (0.05 + r() * 0.12).toFixed(2) + ")"; x.fillRect(r() * 1024, yw + 7 + r() * (256 - yw), 2 + r() * 30, 1 + r() * 4); }
    x.fillStyle = o.boot || "#15171a"; x.fillRect(0, yw - 14, 1024, 22);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = THREE.RepeatWrapping; t.wrapT = THREE.ClampToEdgeWrapping; t.anisotropy = 8; return t;
  };
  /* PANEL: the deckhouse's flat plate, welded panels a metre or two across with dark seams, a lighter
   * weld bead beside each, rust bleed and salt streaks running down from every seam and fitting */
  N.panelTex = function (THREE, paint) {
    if (N._panel) return N._panel;
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(53);
    x.fillStyle = paint || "#6e757c"; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 26; i++) { var px = Math.floor(r() * 4) * 128, py = Math.floor(r() * 4) * 128; x.fillStyle = "rgba(" + (r() < 0.5 ? "0,0,0" : "255,255,255") + "," + (0.04 + r() * 0.06).toFixed(3) + ")"; x.fillRect(px, py, 128, 128); }
    x.strokeStyle = "rgba(18,20,22,0.75)"; x.lineWidth = 3;
    for (var k = 0; k <= 512; k += 128) { x.beginPath(); x.moveTo(k, 0); x.lineTo(k, 512); x.stroke(); x.beginPath(); x.moveTo(0, k); x.lineTo(512, k); x.stroke(); }
    x.strokeStyle = "rgba(200,205,210,0.35)"; x.lineWidth = 1.5;
    for (var k2 = 4; k2 <= 512; k2 += 128) { x.beginPath(); x.moveTo(k2, 0); x.lineTo(k2, 512); x.stroke(); x.beginPath(); x.moveTo(0, k2); x.lineTo(512, k2); x.stroke(); }
    for (var s2 = 0; s2 < 140; s2++) { var sx = r() * 512, sy = Math.floor(r() * 4) * 128 + r() * 20, ln = 30 + r() * 110, g = x.createLinearGradient(sx, sy, sx, sy + ln);
      var rust = r() < 0.4; g.addColorStop(0, rust ? "rgba(110,62,38,0.45)" : "rgba(235,236,232,0.35)"); g.addColorStop(1, "rgba(0,0,0,0)"); x.fillStyle = g; x.fillRect(sx, sy, 1.5 + r() * 3, ln); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; t.repeat.set(1.5, 1); N._panel = t; return t;
  };
  /* WATER NORMALS: two octaves of seeded value noise, stretched along the wind, never a sine */
  N.waterNormal = function (THREE, seed) {
    var n = 512, c = document.createElement("canvas"); c.width = c.height = n; var x = c.getContext("2d"), img = x.createImageData(n, n), r = lcg(seed || 3);
    var G = 64, grid = []; for (var i = 0; i < (G + 1) * (G + 1); i++) grid.push(r());
    function vn(px, py, f) { var gx = px * f / n, gy = py * f / n, x0 = Math.floor(gx), y0 = Math.floor(gy), tx = gx - x0, ty = gy - y0; tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty);
      function g(a, b) { return grid[((b % f) * (G + 1) + (a % f)) % grid.length]; }
      return (g(x0, y0) * (1 - tx) + g(x0 + 1, y0) * tx) * (1 - ty) + (g(x0, y0 + 1) * (1 - tx) + g(x0 + 1, y0 + 1) * tx) * ty; }
    var h = new Float32Array(n * n);
    for (var py = 0; py < n; py++) for (var px = 0; px < n; px++) h[py * n + px] = vn(px, py * 2.2, 16) * 0.6 + vn(px, py * 2.2, 32) * 0.3 + vn(px, py, 64) * 0.1;
    for (var py2 = 0; py2 < n; py2++) for (var px2 = 0; px2 < n; px2++) {
      var dx = h[py2 * n + (px2 + 1) % n] - h[py2 * n + (px2 + n - 1) % n], dy = h[((py2 + 1) % n) * n + px2] - h[((py2 + n - 1) % n) * n + px2];
      var p = (py2 * n + px2) * 4; img.data[p] = 128 - dx * 300; img.data[p + 1] = 128 - dy * 300; img.data[p + 2] = 255; img.data[p + 3] = 255; }
    x.putImageData(img, 0, 0);
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  };
  /* STONE: a riprap face, irregular granite blocks with dark joints, as a map and a bump */
  N.stoneTex = function (THREE, seed) {
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(seed || 77);
    x.fillStyle = "#3c3a35"; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 260; i++) { var cx0 = r() * 512, cy0 = r() * 512, rad = 10 + r() * 26, v = 120 + Math.floor(r() * 60);
      x.fillStyle = "rgb(" + v + "," + (v - 4) + "," + (v - 12) + ")"; x.beginPath();
      for (var k = 0; k < 7; k++) { var a = k / 7 * 6.283 + r() * 0.5, rr = rad * (0.7 + r() * 0.4); x[k ? "lineTo" : "moveTo"](cx0 + Math.cos(a) * rr, cy0 + Math.sin(a) * rr * 0.8); }
      x.closePath(); x.fill(); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  };

  /* ---------------------------------------------------------------- the kit models this deck builds */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.autonomous_vessel) return;
    var plateCache = {};
    function plate(paint) { return plateCache[paint] || (plateCache[paint] = new THREE.MeshStandardMaterial({ color: 0xffffff, map: N.plateTex(THREE, { seed: 4, paint: paint }), roughness: 0.55, metalness: 0.3, side: THREE.DoubleSide })); }
    var deckM = new THREE.MeshStandardMaterial({ color: 0x3b4044, roughness: 0.82, metalness: 0.2, side: THREE.DoubleSide });
    var dark = new THREE.MeshStandardMaterial({ color: 0x24282c, roughness: 0.5, metalness: 0.45 });
    var lens = new THREE.MeshStandardMaterial({ color: 0x0b0d10, roughness: 0.08, metalness: 0.6 });
    var dome = new THREE.MeshStandardMaterial({ color: 0xd9dbd8, roughness: 0.45, metalness: 0 });
    var primer = new THREE.MeshStandardMaterial({ color: 0xa8553c, roughness: 0.72, metalness: 0.15 });

    /* the hull's lines: a hard chine hull, stations stern (u 0) to bow (u 1), each half section keel,
     * bilge, chine, deck edge; the bow closes to the stem and the keel rises in a forefoot */
    function station(L, B, D, u) {
      var bow = Math.max(0, (u - 0.4) / 0.6), hb = B / 2 * Math.pow(Math.max(0, 1 - Math.pow(bow, 1.7)), 0.62);
      var keel = D * 0.42 * Math.pow(bow, 2.4), top = D * (1 + 0.12 * Math.pow(u, 3));
      var dead = 0.18 + 0.32 * bow, chineY = keel + (top - keel) * (0.34 + 0.1 * bow), chineX = hb * 0.97;
      return [[0, keel], [hb * 0.62, keel + (chineY - keel) * dead * 1.2], [chineX, chineY], [hb * (1 + 0.025 * bow), top]];
    }
    function hullGeo(L, B, D) {
      var NS = 72, P = 4, pos = [], uvs = [], idx = [], deck = [], dIdx = [];
      for (var i = 0; i <= NS; i++) {
        var u = i / NS, z = -L / 2 + u * L, s = station(L, B, D, u);
        var rk = 3.2 * Math.pow(Math.max(0, (u - 0.7) / 0.3), 1.6);     /* the stem rakes forward with height */
        for (var side = -1; side <= 1; side += 2) for (var k = 0; k < P; k++) { var zk = z + rk * (s[k][1] / D); pos.push(side * s[k][0], s[k][1], zk); uvs.push((zk + L / 2) / 12, s[k][1] / D); }
        deck.push(-s[3][0], s[3][1], z + rk * (s[3][1] / D), s[3][0], s[3][1], z + rk * (s[3][1] / D));
      }
      var row = P * 2;
      for (var i2 = 0; i2 < NS; i2++) {
        for (var sd = 0; sd < 2; sd++) for (var k2 = 0; k2 < P - 1; k2++) { var a = i2 * row + sd * P + k2, b = a + 1, c = a + row, d = b + row; if (sd === 0) idx.push(a, c, b, b, c, d); else idx.push(a, b, c, b, d, c); }
        var e = i2 * 2; dIdx.push(e, e + 2, e + 1, e + 1, e + 2, e + 3);
      }
      var sides = new THREE.BufferGeometry(); sides.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); sides.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2)); sides.setIndex(idx);
      sides = sides.toNonIndexed(); sides.computeVertexNormals();
      var dg = new THREE.BufferGeometry(); dg.setAttribute("position", new THREE.Float32BufferAttribute(deck, 3)); dg.setIndex(dIdx); dg.computeVertexNormals();
      var s0 = station(L, B, D, 0), tr = [], tuv = [], ti = [];
      s0.forEach(function (p) { tr.push(-p[0], p[1], -L / 2); tuv.push(0.02, p[1] / D); }); s0.forEach(function (p) { tr.push(p[0], p[1], -L / 2); tuv.push(0.05, p[1] / D); });
      for (var t = 0; t < P - 1; t++) ti.push(t, t + 1, P + t, t + 1, P + t + 1, P + t);
      var tg = new THREE.BufferGeometry(); tg.setAttribute("position", new THREE.Float32BufferAttribute(tr, 3)); tg.setAttribute("uv", new THREE.Float32BufferAttribute(tuv, 2)); tg.setIndex(ti); tg.computeVertexNormals();
      return { sides: sides, deck: dg, transom: tg };
    }
    /* a faceted frustum, flat plate chamfered in on every face */
    function facet(w, h, d, taper, mat) {
      var g = new THREE.CylinderGeometry(Math.SQRT1_2 * (1 - taper), Math.SQRT1_2, h, 4, 1); g.rotateY(Math.PI / 4); g.scale(w, 1, d); g = g.toNonIndexed(); g.computeVertexNormals();
      var m = new THREE.Mesh(g, mat); m.castShadow = m.receiveShadow = true; return m;
    }
    /* WASH: a broken band of white where the hull meets still water, following the chine's half
     * breadth at the waterline, wider at the bow where the water piles up. Seeded, never a frill. */
    function washRing(L, B, D, draft, r) {
      var c = document.createElement("canvas"); c.width = 1024; c.height = 32; var x = c.getContext("2d");
      for (var i = 0; i < 3200; i++) { var px = r() * 1024, py = 4 + Math.pow(r(), 1.6) * 26; x.fillStyle = "rgba(238,240,238," + (0.18 + r() * 0.55).toFixed(2) + ")"; x.fillRect(px, py, 1 + r() * 10, 1 + r() * 2.5); }
      var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = THREE.RepeatWrapping; t.repeat.set(5, 1);
      var mat = new THREE.MeshStandardMaterial({ map: t, transparent: true, depthWrite: false, roughness: 0.9 });
      var NS = 90, pos = [], uv = [], idx = [];
      for (var side = -1; side <= 1; side += 2) {
        var base = pos.length / 3;
        for (var i2 = 0; i2 <= NS; i2++) { var u = i2 / NS, z = -L / 2 + u * L, st = station(L, B, D, u), hb = st[2][0];
          var inner = side * Math.max(0, hb - 0.1), outer = side * (hb + 0.8 + 1.4 * Math.pow(u, 5));
          pos.push(inner, 0.03, z, outer, 0.03, z); uv.push(u * 7, 1, u * 7, 0); }
        for (var j = 0; j < NS; j++) { var a = base + j * 2; if (side < 0) idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); else idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
      }
      var geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2)); geo.setIndex(idx); geo.computeVertexNormals();
      var m = new THREE.Mesh(geo, mat); m.renderOrder = 2; m.userData.txWear = false;
      /* THE SKIRT: the same foam standing on the hull's skin at the waterline. Seen from a bank a few
       * metres up, a flat ring foreshortens to nothing, so the line a reader sees is this band, densest
       * at the water and broken above it, climbing at the bow where the water piles up. */
      var c2 = document.createElement("canvas"); c2.width = 1024; c2.height = 64; var x2 = c2.getContext("2d");
      for (var k = 0; k < 5200; k++) { var qx = r() * 1024, qy = 63 - Math.pow(r(), 2.2) * 60; x2.fillStyle = "rgba(240,242,240," + (0.3 + r() * 0.6).toFixed(2) + ")"; x2.fillRect(qx, qy, 2 + r() * 14, 1 + r() * 3); }
      var t2 = new THREE.CanvasTexture(c2); t2.colorSpace = THREE.SRGBColorSpace; t2.wrapS = THREE.RepeatWrapping;
      var mat2 = new THREE.MeshStandardMaterial({ map: t2, transparent: true, depthWrite: false, roughness: 0.9, side: THREE.DoubleSide, emissive: 0xffffff, emissiveMap: t2, emissiveIntensity: 0.12 });
      var sp = [], su = [], si = [];
      for (var sd2 = -1; sd2 <= 1; sd2 += 2) { var b2 = sp.length / 3;
        for (var i3 = 0; i3 <= NS; i3++) { var u3 = i3 / NS, z3 = -L / 2 + u3 * L, hb3 = station(L, B, D, u3)[2][0] + 0.06, top = 0.3 + 0.9 * Math.pow(u3, 6);
          sp.push(sd2 * hb3, -0.05, z3, sd2 * hb3, top, z3); su.push(u3 * 9, 0, u3 * 9, 1); }
        for (var j3 = 0; j3 < NS; j3++) { var a3 = b2 + j3 * 2; si.push(a3, a3 + 2, a3 + 1, a3 + 1, a3 + 2, a3 + 3); } }
      var g2 = new THREE.BufferGeometry(); g2.setAttribute("position", new THREE.Float32BufferAttribute(sp, 3)); g2.setAttribute("uv", new THREE.Float32BufferAttribute(su, 2)); g2.setIndex(si); g2.computeVertexNormals();
      var skirt = new THREE.Mesh(g2, mat2); skirt.renderOrder = 3; skirt.userData.txWear = false;
      var w = new THREE.Group(); w.add(m); w.add(skirt); return w;
    }
    function keelBlock(parent, x, z, h, conc, timber) {
      K.box(1.4, h - 0.3, 0.9, conc, x, 0, z, 0.04, parent);
      K.box(1.5, 0.15, 1.0, timber, x, h - 0.3, z, 0.01, parent);
      K.box(1.5, 0.15, 1.0, timber, x, h - 0.15, z, 0.01, parent);
    }
    var conc = K.mat ? K.mat("pa-conc", { color: 0xb3ada2, map: K.tex("concrete"), roughness: 0.9 }) : new THREE.MeshStandardMaterial({ color: 0xb3ada2, roughness: 0.9 });
    var timber = K.mat("pa-timber", { color: 0x8a6d4c, map: K.tex("wood", { color: "#7f6345" }), roughness: 0.88 });

    K.define("autonomous_vessel", {
      size: [9.8, 14.6, 46],
      anchor: "base",
      options: { length: 46, beam: 9.6, depth: 4.6, draft: 2.3, state: "afloat", payload: 0, paint: "#9aa2aa", blocks: 1.4, mast: true },
      note: "An illustrative autonomous surface vessel, hard chine steel hull with a black boot top and red antifouling, a faceted windowless deckhouse, a faceted sensor mast (open array radar, radome, EO/IR ball, whips), a flush payload deck aft with a toe rail, two waterjets at the transom. Nothing on it is sized for a person. state afloat (origin at the waterline, keel at -draft) | blocks (on keel blocks `blocks` m high, origin on the ground). payload: edge in m of one primer steel block on the after deck, 0 for none. Front is +z.",
      make: function (o, r) {
        var L = o.length, B = o.beam, D = o.depth, root = new THREE.Group(), g = new THREE.Group(); root.add(g);
        var H = hullGeo(L, B, D), pm = plate(o.paint);
        [H.sides, H.transom].forEach(function (geo) { var m = new THREE.Mesh(geo, pm); m.castShadow = m.receiveShadow = true; g.add(m); });
        var dk = new THREE.Mesh(H.deck, deckM); dk.receiveShadow = true; g.add(dk);
        /* rubbing strake, a dark half round at the sheer, and a toe rail */
        var sm = station(L, B, D, 0.5)[3];
        [-1, 1].forEach(function (sd) {
          var pts = []; for (var i = 2; i <= 30; i++) { var u = i / 32, st = station(L, B, D, u)[3]; pts.push(new THREE.Vector3(sd * (st[0] + 0.05), st[1] - 0.45, -L / 2 + u * L)); }
          var tube = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 64, 0.14, 8, false), dark); tube.castShadow = true; g.add(tube);
          var rail = []; for (var j = 1; j <= 30; j++) { var u2 = j / 32, s2 = station(L, B, D, u2)[3]; rail.push(new THREE.Vector3(sd * (s2[0] - 0.08), s2[1] + 0.12, -L / 2 + u2 * L)); }
          var tr = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(rail), 64, 0.07, 6, false), pm); g.add(tr);
        });
        /* deckhouse forward of midships, mast on it */
        var hz = L * 0.12, hp = new THREE.MeshStandardMaterial({ color: 0xffffff, map: N.panelTex(THREE, o.paint), roughness: 0.6, metalness: 0.3 });
        var house = facet(6.6, 3.0, 8.8, 0.24, hp); house.position.set(0, D + 0.15 + 1.5, hz); g.add(house);
        var house2 = facet(4.4, 1.6, 5.2, 0.3, hp); house2.position.set(0, D + 0.15 + 3.0 + 0.8, hz - 0.6); g.add(house2);
        /* mast false leaves the sensor mast off, for a frame whose headline stands where it would rise */
        var mg = o.mast === false ? new THREE.Group() : g;
        var mast = facet(1.9, 6.0, 1.9, 0.55, hp); mast.position.set(0, D + 0.15 + 4.6 + 3.0, hz - 0.8); mg.add(mast);
        var mt = D + 0.15 + 4.6 + 6.0;
        var arr = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.42, 0.22), dark); arr.position.set(0, mt + 0.35, hz - 0.8); arr.castShadow = true; mg.add(arr);
        var ped = K.cyl(0.18, 0.22, 0.3, dark, 0, mt, hz - 0.8, 12, mg);
        var arm = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.34, 1.1), dark); arm.position.set(0, mt - 0.7, hz - 0.1); mg.add(arm);
        var rd = new THREE.Mesh(new THREE.SphereGeometry(0.55, 24, 16), dome); rd.position.set(0, mt - 0.25, hz + 0.45); rd.castShadow = true; mg.add(rd);
        var eo = new THREE.Mesh(new THREE.SphereGeometry(0.24, 20, 14), dark); eo.position.set(0, mt - 2.2, hz - 0.05); mg.add(eo);
        var ap = new THREE.Mesh(new THREE.CircleGeometry(0.09, 18), lens); ap.position.set(0, mt - 2.2, hz + 0.19); mg.add(ap);
        /* no whips: at a broadside crop they read as loose bars beside the mast */
        /* waterjets at the transom */
        [-1, 1].forEach(function (sd) { var j = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.48, 1.1, 18), dark); j.rotation.x = Math.PI / 2; j.position.set(sd * 1.6, D * 0.32, -L / 2 - 0.45); j.castShadow = true; g.add(j); });
        /* the payload: one steel block in primer on the after deck */
        if (o.payload > 0) { var e = o.payload, blk = TXT.roundedBox(e, e, e, 0.04, primer); blk.position.set(0, D + 0.12 + e / 2, -L * 0.2); blk.rotation.y = 0.44; blk.castShadow = blk.receiveShadow = true; g.add(blk); }
        if (o.state === "blocks") {
          g.position.y = o.blocks;
          for (var z = -L / 2 + 2; z < L / 2 - 6; z += 1.83) keelBlock(root, 0, z, o.blocks, conc, timber);
          for (var zb = -L / 2 + 6; zb < L / 2 - 12; zb += 9) [-1, 1].forEach(function (sd) { keelBlock(root, sd * B * 0.28, zb, o.blocks + station(L, B, D, (zb + L / 2) / L)[1][1], conc, timber); });
        } else {
          g.position.y = -o.draft;
          root.add(washRing(L, B, D, o.draft, r));
        }
        root.userData.draft = o.draft; root.userData.length = L;
        return root;
      }
    });

    /* KEEL_BLOCK_LINE: a line of keel blocks `length` m long along +z from the origin, concrete bases
     * with two timber caps, at `pitch` m, `h` m tall. */
    K.define("keel_block_line", {
      size: [1.5, 1.4, 60],
      anchor: "base",
      options: { length: 60, pitch: 1.83, h: 1.4 },
      note: "A line of keel blocks along +z from the origin, `length` m at `pitch` m, each a chamfered concrete base under two timber caps, `h` m tall.",
      make: function (o, r) {
        var g = new THREE.Group(), n = Math.floor(o.length / o.pitch) + 1;
        var base = new THREE.BoxGeometry(1.4, o.h - 0.3, 0.9), cap = new THREE.BoxGeometry(1.5, 0.15, 1.0), bl = [], cl = [];
        for (var i = 0; i < n; i++) { var z = i * o.pitch; bl.push([0, (o.h - 0.3) / 2, z, (r() - 0.5) * 0.04, 1]); cl.push([0, o.h - 0.225, z, (r() - 0.5) * 0.06, 1]); cl.push([0, o.h - 0.075, z, (r() - 0.5) * 0.06, 1]); }
        g.add(K.instances(base, conc, bl)); g.add(K.instances(cap, timber, cl));
        g.traverse(function (m) { if (m.isMesh || m.isInstancedMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* RIPRAP_BANK: a bank `length` m along x, its top edge on z = 0 at y = `top`, falling south to
     * `toe` m under the water at a run of `run` m, faced with granite riprap. */
    K.define("riprap_bank", {
      size: [200, 3.4, 5],
      anchor: "base",
      options: { length: 200, top: 2.2, toe: -1.2, run: 5, stones: 1 },
      note: "A ship channel bank faced in granite riprap: a sloped face from the land's edge at y top down to y toe under the water, a stone texture and instanced stones on its face. The top edge is on z = 0 and the water side is +z.",
      make: function (o, r) {
        var g = new THREE.Group(), t = N.stoneTex(THREE, 77); t.repeat.set(o.length / 6, 1);
        var face = new THREE.PlaneGeometry(o.length, Math.hypot(o.run, o.top - o.toe), Math.ceil(o.length / 2), 6);
        var m = new THREE.Mesh(face, new THREE.MeshStandardMaterial({ map: t, bumpMap: t, bumpScale: 0.35, roughness: 0.92, color: 0xffffff }));
        m.rotation.x = -Math.PI / 2 + Math.atan2(o.top - o.toe, o.run); m.position.set(0, (o.top + o.toe) / 2, o.run / 2); m.receiveShadow = true; g.add(m);
        if (o.stones) {
          var geo = new THREE.SphereGeometry(1, 14, 10), P = geo.attributes.position, rs = lcg(91);
          for (var vi = 0; vi < P.count; vi++) { var vx = P.getX(vi), vy = P.getY(vi), vz = P.getZ(vi), k = 0.82 + 0.3 * (Math.sin(vx * 3.1 + vz * 1.7) * 0.5 + Math.sin(vy * 4.3 - vx * 2.2) * 0.5) * 0.5 + rs() * 0.04; P.setXYZ(vi, vx * k * 1.15, vy * k * 0.7, vz * k); }
          geo.computeVertexNormals(); var list = [], mat = K.mat("pa-riprap", { color: 0x9d978a, roughness: 0.9, map: K.tex("concrete") });
          for (var i = 0; i < o.length * 3 * o.stones; i++) { var x = (r() - 0.5) * o.length, f = r(), y = o.top + (o.toe - o.top) * f, z = o.run * f; if (y < -0.4) continue;
            list.push([x, y + 0.1, z - 0.15, r() * 6.28, 0.25 + r() * 0.45]); }
          var inst = K.instances(geo, mat, list); inst.castShadow = true; inst.receiveShadow = true; g.add(inst);
        }
        return g;
      }
    });
  };

  /* ---------------------------------------------------------------- the place, as primitives */
  /* The world's own furniture: the channel's water, the two banks' land, the plan's ink on the ground.
   * Each is a primitive a frame places where its own composition wants it. None draws a frame. */
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  /* THE WATER is a TXT.ground plane, so it takes the grazing fade into the sky's horizon, with a glossy
   * finish and the seeded normal map. Tile `tile` m, ripple strength `ripple`. */
  N.water = function (o) {
    o = o || {}; var T = N.T, w = N.TXT.ground(N.R, { color: o.color || 0x2c3a33, roughness: o.roughness == null ? 0.1 : o.roughness, size: o.size || 12000, y: 0 });
    var nt = N.waterNormal(T, o.seed || 5), size = o.size || 12000; nt.repeat.set(size / (o.tile || 46), size / (o.tile || 46));
    w.material.normalMap = nt; w.material.normalScale = new T.Vector2(o.ripple || 0.16, o.ripple || 0.16); w.material.envMapIntensity = 1.0; w.material.needsUpdate = true;
    w.userData.txWear = false; return w;
  };
  /* LAND: a TXT.ground surface covering z from z0 to z1 at height y, as one square placed there */
  N.land = function (z0, z1, y, o) {
    o = o || {}; var size = o.size || 8000, g = N.TXT.ground(N.R, { surface: o.surface || "dirt", size: size, y: y, tile: o.tile || 6, seed: o.seed || 41, color: o.color || 0x8a7f6c, wear: o.wear });
    var zc = z1 < z0 ? z0 - size / 2 : z0 + size / 2; g.position.z = zc; g.position.x = o.x || 0; return g;
  };
  /* THE PLAN'S INK: a flat strip on the ground from a to b ([x, z]), `w` wide at height y, the accent in
   * its albedo and a small emissive so it holds its hue under the grade; `dash` metres on, `gap` off. */
  N.inkMat = function () { return N._ink || (N._ink = new N.T.MeshStandardMaterial({ color: 0x5b69a6, roughness: 0.9, metalness: 0, emissive: 0x4e5fa8, emissiveIntensity: 0.08 })); };
  N.strip = function (a, b, w, y, o) {
    o = o || {}; var T = N.T, dx = b[0] - a[0], dz = b[1] - a[1], len = Math.hypot(dx, dz), ang = Math.atan2(dx, dz), g = new T.Group();
    var on = o.dash || len, off = o.gap || 0, step = on + off;
    for (var s = 0; s < len; s += step) { var l = Math.min(on, len - s), m = new T.Mesh(new T.BoxGeometry(w, 0.04, l), o.mat || N.inkMat()); m.position.set(a[0] + Math.sin(ang) * (s + l / 2), y + 0.02, a[1] + Math.cos(ang) * (s + l / 2)); m.rotation.y = ang; m.receiveShadow = true; m.userData.txWear = false; g.add(m); }
    N.TXT.add(N.R, g); return g;
  };
  /* THE FAR BANK: land at N.FAR beyond the channel, a riprap face, palms and mesquite along it, scrub */
  N.farBank = function (o) {
    o = o || {}; var K = N.K, z = N.CHANNEL;
    N.land(z, z + 1, N.FAR, { surface: "grass", color: 0x8c8a62, seed: 52, tile: 7 });
    var bank = K.make("riprap_bank", { length: o.length || 3000, top: N.FAR, toe: -1.2, run: 4, stones: 0, seed: 9 }); bank.rotation.y = Math.PI; bank.position.set(o.x || 0, 0, z); N.TXT.add(N.R, bank);
    var r = lcg(o.seed || 31);
    for (var i = 0; i < (o.trees || 40); i++) { var t = K.make(r() < 0.45 ? "palm" : "mesquite", { seed: 200 + i }); t.position.set((o.x || 0) + (r() - 0.5) * (o.spread || 1800), N.FAR, z + 14 + r() * 120); N.TXT.add(N.R, t); }
  };
  /* THE NEAR BANK: the yard's land edge, a riprap face down into the water along z = 0 */
  N.yardBank = function (o) {
    o = o || {}; var K = N.K;
    N.land(0, -1, N.BANK, { surface: o.surface || "dirt", color: o.color || 0x8a7f6c, seed: o.seed || 41, tile: o.tile || 6 });
    var bank = K.make("riprap_bank", { length: o.length || 3000, top: N.BANK, toe: -1.2, run: 5, stones: o.stones == null ? 1 : o.stones, seed: 7 }); bank.position.set(o.x || 0, 0, 0); N.TXT.add(N.R, bank);
    return bank;
  };
  /* SCATTER ON THE LAND. TXT.scatter seeds at y 0 and this deck's land stands N.BANK above the water,
   * so every field is lifted onto the ground it belongs to, or it renders under it. */
  N.lift = function (obj, y) { if (obj) obj.position.y += y; return obj; };
  N.scrub = function (area, o) { o = o || {}; return N.lift(N.TXT.scatter(N.R, { kind: "scrub", count: o.count || 2600, area: area, avoid: o.avoid, seed: o.seed || 8, scale: o.scale || [0.5, 1.4], colors: [0x5f6a4e, 0x6e7458, 0x4f553a] }), o.y == null ? N.BANK : o.y); };
  N.grass = function (area, o) { o = o || {}; return N.lift(N.TXT.scatter(N.R, { kind: "grass", count: o.count || 6000, area: area, avoid: o.avoid, seed: o.seed || 9, scale: o.scale || [0.25, 0.5], colors: [0xa39a6b, 0x8f8a5c, 0xb3a77a] }), o.y == null ? N.BANK : o.y); };
  /* GRIT on a graded yard: small stones and clods near the camera, so a worked ground reads as worked */
  N.grit = function (area, o) { o = o || {}; return N.lift(N.TXT.scatter(N.R, { kind: "rock", count: o.count || 7000, area: area, avoid: o.avoid, seed: o.seed || 13, scale: o.scale || [0.04, 0.14], colors: [0x5a5248, 0x6d6457, 0x463f37] }), o.y == null ? N.BANK : o.y); };
  /* TYRE TRACKS across a graded yard: pairs of dark compacted bands, seeded curves of short strips */
  N.trackMat = function () { return N._trk || (N._trk = new N.T.MeshStandardMaterial({ color: 0x3e3832, roughness: 0.95 })); };
  N.tracks = function (n, area, o) {
    o = o || {}; var r = lcg(o.seed || 61), T = N.T;
    for (var k = 0; k < n; k++) { var x = area[0] + r() * (area[2] - area[0]), z = area[1] + r() * (area[3] - area[1]), a = r() * 6.28, len = 30 + r() * 60, bend = (r() - 0.5) * 0.03;
      for (var side = -1; side <= 1; side += 2) { var px = x + Math.cos(a) * side * 0.95, pz = z - Math.sin(a) * side * 0.95, aa = a;
        for (var t = 0; t < len; t += 2) { var nx = px + Math.sin(aa) * 2, nz = pz + Math.cos(aa) * 2; N.strip([px, pz], [nx, nz], 0.45, o.y == null ? N.BANK - 0.015 : o.y, { mat: N.trackMat() }); px = nx; pz = nz; aa += bend; } } }
  };
  /* KEEP THE TYPE CLEAR: after TXT.frame, hide every kit model named in `kinds` whose projected base
   * to top falls inside any of `rects` ([x0, y0, x1, y1] in CSS px of the 1080 x 1350 page). A far palm
   * standing in a headline is a letterform crossing, and moving the type is the costlier fix. */
  N.keepClear = function (THREE, R, rects, kinds) {
    kinds = kinds || ["palm", "mesquite"]; var hid = 0, box = new THREE.Box3();
    R.scene.traverse(function (o) { if (!o.userData || kinds.indexOf(o.userData.kit) < 0 || !o.visible) return;
      box.setFromObject(o); var a = N.project(THREE, R, [(box.min.x + box.max.x) / 2, box.min.y, (box.min.z + box.max.z) / 2]), b = N.project(THREE, R, [(box.min.x + box.max.x) / 2, box.max.y, (box.min.z + box.max.z) / 2]);
      var half = Math.max(6, Math.abs(N.project(THREE, R, [box.max.x, box.max.y, box.max.z])[0] - N.project(THREE, R, [box.min.x, box.max.y, box.min.z])[0]) / 2);
      for (var i = 0; i < rects.length; i++) { var q = rects[i]; if (a[0] + half > q[0] && a[0] - half < q[2] && Math.min(a[1], b[1]) < q[3] && Math.max(a[1], b[1]) > q[1]) { o.visible = false; hid++; break; } } });
    return hid;
  };
  N.vessel = function (o) { return N.K.make("autonomous_vessel", Object.assign({ seed: 3 }, o || {})); };
  N.installAll = function () { N.installKit(N.K, N.T, N.TXT); };

  /* ---------------------------------------------------------------- the frame shell */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 30, mapSize: map || 2048, radius: 4 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 90, shadowFar: o.shadowFar || 220, normalBias: o.normalBias == null ? 0.02 : o.normalBias };
  };

  /* THE SKY BAND THE TYPE STANDS IN. At noon the type is dark, so the band is a pale wash that
   * lifts the sky behind the hook, never over 0.45 alpha. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 70 : o.pad;
    var a = o.a == null ? 0.2 : Math.min(0.45, o.a), c = o.rgb || "244,242,236";
    if (bottom != null && a > 0) {
      var fade = o.fade || 160, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + (a * 0.85) + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + a + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  /* KNOCK THE EDGE OUT BEHIND A LINE OF TYPE, without removing its light. */
  N.soften = function (cx, selectors, o) {
    o = o || {};
    var blur = o.blur || 12, pad = o.pad == null ? 18 : o.pad, feather = o.feather || 70;
    var art = document.getElementById("art");
    var src = document.createElement("canvas"); src.width = art.width; src.height = art.height;
    var sx = src.getContext("2d"); sx.filter = "blur(" + (blur * 2) + "px)"; sx.drawImage(art, 0, 0);
    var mask = document.createElement("canvas"); mask.width = art.width; mask.height = art.height;
    var mx = mask.getContext("2d"); mx.filter = "blur(" + feather + "px)"; mx.fillStyle = "#000";
    (selectors || []).forEach(function (sel) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
        var r = el.getBoundingClientRect();
        mx.fillRect((r.left - pad) * 2, (r.top - pad) * 2, (r.width + 2 * pad) * 2, (r.height + 2 * pad) * 2);
      });
    });
    sx.filter = "none"; sx.globalCompositeOperation = "destination-in"; sx.drawImage(mask, 0, 0);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.drawImage(src, 0, 0); cx.restore();
  };
  /* THE POST STEPS every frame takes before its grade. The frame still calls TXDECK.finish itself,
   * last. A pale band under the footer, never a box and never over 0.45. */
  N.post = function (cx, o) {
    o = o || {};
    /* the type band lifts by the same step the exposure took away, so dark type keeps 4.5 */
    N.atmosphere(cx, { a: Math.min(0.5, (o.a == null ? 0.18 : o.a) + 0.24), to: o.to, fade: o.fade, rgb: o.rgb, pad: o.pad });
    N.soften(cx, o.type || [".kick", ".hook", ".dek"], { blur: o.typeBlur || 3, pad: 8, feather: o.typeFeather || 22 });
    N.soften(cx, [".tx-site", ".src"], { blur: o.siteBlur || 18, pad: 18, feather: 70 });
    var y0 = N.H - (o.veilH || 250), v = cx.createLinearGradient(0, y0, 0, N.H), rgb = o.veilRgb || "238,236,230";
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(" + rgb + "," + (Math.min(0.45, o.veil == null ? 0.28 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    /* THE FOOTER ROW'S WASH, for a frame whose ground under the footer is asphalt or shadow: a
     * feathered band across the whole width, peaking on the footer's own line, so the citation
     * and the site line clear 4.5 without a plate behind either */
    if (o.footWash) {
      var f = document.querySelector(".tx-site"), sc = N.H / document.body.clientHeight, fr = f ? f.getBoundingClientRect() : null;
      var mid = fr ? (fr.top + fr.height / 2) * sc : N.H - 110, half = 70;
      var fw = cx.createLinearGradient(0, mid - half, 0, mid + half);
      [[0, 0], [0.3, 1], [0.7, 1], [1, 0]].forEach(function (p) { fw.addColorStop(p[0], "rgba(" + rgb + "," + (o.footWash * p[1]).toFixed(4) + ")"); });
      cx.fillStyle = fw; cx.fillRect(0, mid - half, N.W, half * 2);
    }
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 2.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };

  /* THE SHELL EVERY FRAME SHARES: the type styles, the furniture, the fit of the hook. Dark type at
   * noon, with a pale halo rather than a shadow. A frame on a dark ground (a room facing away from
   * its window) passes { light: true } and the type turns light. */
  N.CSS = function (light) {
    var ink = light ? "#F5F2EB" : N.INK, dek = light ? "#ECE8E0" : "#1D2026", halo = light ? "rgba(10,12,16,0.55)" : "rgba(246,244,238,0.7)", halo2 = light ? "rgba(10,12,16,0.42)" : "rgba(246,244,238,0.55)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#5E6266; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".hook, .dek, .tx-site, .kick, .src, .cap, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 12px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS(!!o.light);
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: o.light ? "#ECE8E0" : "#1D2026" });
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
  /* THE DECK'S EXPOSURE, ONE NUMBER FOR ALL NINE. brand.yaml allows a light deck once per eight
   * runs and no. 38 on September 30th was one, measured at L* 60.6. At the round cap this deck
   * measured L* 68.0, so every frame is exposed down together to hold the deck median under the
   * ledger's 60 line, through the renderer's own tone curve rather than a multiply on the pixels. */
  N.EXPOSURE = 0.46;  /* tuned on the probe frame, then lowered after the flow critic asked for a true dark, so the deck sits well under the light deck cap */
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    N.R = TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * N.EXPOSURE * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 30, near: o.near || 0.05, far: o.far || 12000 });
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
    /* NO DEBAND ON THIS DECK. The pass was written for a low golden sun's ringed sky and it flattens
     * any texture within its tolerance of the local mean, which at noon is the ground's whole tooth.
     * A noon sky steps far less, and the grade's grain and N.dither break what steps remain. */
    return cx;
  };

  /* N.deband. The GPU frame arrives in 8 bits, and a low sun's sky steps one level at a time into
   * rings the grade then sharpens. Where a pixel sits within `tol` levels of its neighbourhood mean
   * it is a smooth gradient, so it takes that mean plus a triangular dither. Anything with an edge,
   * a stake, a wire, a letter, differs from its mean by more and is left exactly as rendered. */
  N.deband = function (cx, o) {
    o = o || {}; var c = cx.canvas, w = c.width, h = c.height, rad = o.radius || 44, tol = o.tol || 2.8;
    var id = cx.getImageData(0, 0, w, h), d = id.data, n = w * h, a = new Float32Array(n), b = new Float32Array(n), s = 7654321;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var ch = 0; ch < 3; ch++) {
      for (var i = 0; i < n; i++) a[i] = d[i * 4 + ch];
      for (var y = 0; y < h; y++) { var row = y * w, acc = 0, cnt = 0;
        for (var x = -rad; x < w; x++) { if (x + rad < w) { acc += a[row + x + rad]; cnt++; } if (x - rad - 1 >= 0) { acc -= a[row + x - rad - 1]; cnt--; } if (x >= 0) b[row + x] = acc / cnt; } }
      for (var x2 = 0; x2 < w; x2++) { var acc2 = 0, cnt2 = 0;
        for (var y2 = -rad; y2 < h; y2++) { if (y2 + rad < h) { acc2 += b[(y2 + rad) * w + x2]; cnt2++; } if (y2 - rad - 1 >= 0) { acc2 -= b[(y2 - rad - 1) * w + x2]; cnt2--; } if (y2 >= 0) a[y2 * w + x2] = acc2 / cnt2; } }
      for (var j = 0; j < n; j++) { var v = d[j * 4 + ch], m = a[j]; if (Math.abs(v - m) < tol) d[j * 4 + ch] = m + (rnd() + rnd() - 1) * 1.6; }
    }
    cx.putImageData(id, 0, 0);
  };


  global.PA = N;
})(this);
