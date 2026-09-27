/* deck/2026-09-27-nightrent.js — the chassis for the 2026-09-27 deck: the Justice Department's
 * proposed final judgment against Pinnacle Property Management Services, the Frisco apartment
 * manager that licensed RealPage's AI Revenue Management and YieldStar (tx-2026-0189).
 *
 * THE WORLD. A Texas garden apartment lot at two in the morning. The complaint's verbs are
 * "every night" and "generated daily" (c25, c26), and the world table's line for nightSodium is
 * what runs all night, what is not seen. The declared light is the city's sodium glow low in the
 * south behind the buildings, so a camera standing in a lot and looking at a front facade sees
 * the roofline against the amber glow and the facade lit by what is IN the lot: the pole lamps,
 * the breezeway wall packs and the few windows still lit. The key never moves.
 *
 * THE HERO OBJECT. One Texas garden walk-up, the kit model this file adds (garden_apartment),
 * the same building on every frame: brick ground floor, lap siding above, a gable ridge, five
 * breezeway cores whose wall packs are the deck's motif, and a leasing office at the west end.
 * It is DRAWN. It stands for a kind of building and is no one's property, and no frame says
 * otherwise.
 *
 * THE ACCENT. #7FB2D9, the one cool light in a sodium deck: a screen at night. The leasing
 * office's monitor where the complaint says a price arrives every night, and on the last frame
 * a resident's laptop. Nothing else wears it.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the kit
 * addition and the deck's materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("nightrent.js needs txdeck.js loaded first");

  /* ONE DECLARATION. The key is the sodium glow of the city low in the south-south-west, az 196
   * (clockwise from +Z toward +X), el 26, inside nightSodium's lamp range of 20 to 60. The
   * buildings' fronts face +z, so the key is BEHIND every front facade a lot camera looks at:
   * the roof ridge and the eave take a warm rim, casts run toward the camera, and the facade is
   * lit by the lot's own lamps. The preset's haze and glow are pulled down so the zenith stays
   * black and the glow sits on the horizon, never across the whole sky. */
  TXDECK.declare({
    world: "nightrent",
    light: { az: 196, el: 26 },
    sky: { preset: "nightSodium", haze: 0x3b2c22, glow: 0.3, horizonGlow: 0.55, fogDensity: 0.0042,
      rig: { key: { color: 0xffb46a, i: 1.3, radius: 8 }, rim: { color: 0x6f8fd8, i: 0.5, pos: [-8, 6, -8] },
             fill: { color: 0x2c3a60, i: 0.35, pos: [-4, 4, 9] }, ambient: { color: 0x1c2233, i: 0.18 } } },
    ground: "#171310",
    material: "#B89A76",
    accent: "#7FB2D9",
    grade: {
      exposure: 0.0,
      saturation: 1.0,
      contrast: 1.05,
      filmic: true,
      lift: [0.008, 0.008, 0.012],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.24,
      bloom: { threshold: 0.8, strength: 0.3, radius: 14 },
      grain: { amount: 0.014, size: 2, seed: 20260927 },
      aberration: 0,
      dither: true,
      sharpen: 0.16
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20260927;
  N.ACCENT = 0x7fb2d9;
  N.SODIUM = 0xffb25a;
  /* THE KIT ADDITION: garden_apartment. The kit has houses and no apartment building, and this
   * deck's whole subject is one. Built under the conventions in the header of assets/js/txkit.js
   * (metres, y up, origin centred on the footprint at the ground, front on +z, K.tex textures
   * mapped in metres through K.uvBox, merged by material) so Phase 17 can lift it into
   * assets/js/kit/ unchanged.
   *
   * WHAT IT IS. The Texas garden walk-up of every suburban submarket since the 1980s: three
   * storeys at 3.05 m floor to floor, a brick ground floor and lap siding above, a 6 in 12 gable
   * roof in dark shingle with its ridge along the building, a balcony and a sliding door on every
   * bay with a window beside it, and open breezeway stair cores through the depth of the building,
   * each with concrete treads on steel stringers, landings, a pipe rail and a wall pack lamp.
   * Condensers on pads along the back, gutters and downspouts, a leasing office storefront in the
   * ground floor of the west end bay.
   *
   * OPTIONS. cores (breezeways, 1 to 6), groupBays (bays between cores, 1 to 4), floors (2 to 4),
   * brick, siding, trim, roof, lampsOn (true, false, or one boolean per core), lit (a share 0 to 1
   * of the front units whose windows glow, by seed) or litUnits ([[bay, floor]...], bay counted
   * left to right across the front), glow (a lit window's colour), office ('west' or false),
   * officeGlow (the colour the storefront's room gives off), lampLights (true adds one real point
   * light per lit core, for frames that need the breezeway to throw light).
   *
   * userData: units (each front unit's slider centre {bay, floor, x, y, z, lit}), cores ({x, lampOn}),
   * dims ({L, D, eave, ridge, floorH, y0}), office ({x, y, z} the storefront's centre) or null. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.garden_apartment) return;
    var V3 = THREE.Vector3;

    function Bucket() {
      var parts = new Map();
      return {
        add: function (m, g) { if (!parts.has(m)) parts.set(m, []); parts.get(m).push(g); return g; },
        flush: function (group) {
          parts.forEach(function (list, m) {
            var meshes = list.map(function (g) {
              if (!g.attributes.uv) g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(g.attributes.position.count * 2), 2));
              if (!g.attributes.normal) g.computeVertexNormals();
              return new THREE.Mesh(g);
            });
            var mesh = K.merge(meshes, m);
            if (m.transparent) mesh.renderOrder = 2;
            if (m.emissiveIntensity > 0 && m.color && m.color.getHex() === 0) mesh.castShadow = false;
            group.add(mesh);
          });
          parts.clear();
          return group;
        }
      };
    }
    function box(B, m, w, h, d, x, y0, z, uvm) {
      var g = new THREE.BoxGeometry(w, h, d);
      g.translate(x, y0 + h / 2, z);
      if (uvm) K.uvBox(g, uvm);
      return B.add(m, g);
    }
    function bar(B, m, a, b, r) {
      var A = new V3(a[0], a[1], a[2]), C = new V3(b[0], b[1], b[2]), len = A.distanceTo(C);
      var g = new THREE.CylinderGeometry(r, r, len, 8);
      g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new V3(0, 1, 0), C.clone().sub(A).normalize()));
      var mid = A.clone().add(C).multiplyScalar(0.5); g.translate(mid.x, mid.y, mid.z);
      return B.add(m, g);
    }
    /* a wall in the x/y plane, outer face at z = zf facing +z (or -z when back), x0..x1, base y0,
     * height H, thickness t, with rectangular openings cut through it as real reveals */
    function wall(B, m, uvm, x0, x1, y0, H, zf, t, ops, back) {
      var zc = back ? zf + t / 2 : zf - t / 2, cuts = [x0, x1];
      ops.forEach(function (o) { cuts.push(Math.max(x0, Math.min(x1, o.x0)), Math.max(x0, Math.min(x1, o.x1))); });
      cuts.sort(function (a, b) { return a - b; });
      for (var i = 0; i < cuts.length - 1; i++) {
        var u0 = cuts[i], u1 = cuts[i + 1];
        if (u1 - u0 < 1e-3) continue;
        var mid = (u0 + u1) / 2;
        var holes = ops.filter(function (o) { return o.x0 < mid && o.x1 > mid; }).sort(function (a, b) { return a.y0 - b.y0; });
        var y = y0;
        holes.forEach(function (h) { if (h.y0 - y > 1e-3) box(B, m, u1 - u0, h.y0 - y, t, mid, y, zc, uvm); y = Math.max(y, h.y1); });
        if (y0 + H - y > 1e-3) box(B, m, u1 - u0, y0 + H - y, t, mid, y, zc, uvm);
      }
    }
    /* the room behind a lit window: a warm wash, darker toward the edges, with blinds or a
     * curtain, so a lit window reads as a room and not a lamp */
    var ROOMTEX = new Map();
    function roomTex(kind) {
      if (ROOMTEX.has(kind)) return ROOMTEX.get(kind);
      var c = document.createElement('canvas'); c.width = 128; c.height = 128;
      var x = c.getContext('2d'), g = x.createRadialGradient(64, 58, 6, 64, 64, 96);
      if (kind === 'office') { g.addColorStop(0, '#ffffff'); g.addColorStop(0.35, '#9aa3ab'); g.addColorStop(1, '#1c2024'); }
      else if (kind === 'blinds') { g.addColorStop(0, '#fff1d6'); g.addColorStop(0.55, '#e9b777'); g.addColorStop(1, '#6a4526'); }
      else { g.addColorStop(0, '#ffe7c2'); g.addColorStop(0.6, '#d49a5c'); g.addColorStop(1, '#4d311c'); }
      x.fillStyle = g; x.fillRect(0, 0, 128, 128);
      if (kind === 'blinds') for (var i = 0; i < 128; i += 6) { x.fillStyle = 'rgba(40,24,10,0.28)'; x.fillRect(0, i, 128, 1.4); }
      if (kind === 'curtain') { x.fillStyle = 'rgba(60,34,16,0.55)'; x.fillRect(0, 0, 22, 128); x.fillRect(106, 0, 22, 128); }
      if (kind === 'office') { x.fillStyle = 'rgba(0,0,0,0.7)'; x.fillRect(0, 88, 128, 40); }
      var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
      ROOMTEX.set(kind, t);
      return t;
    }

    K.define('garden_apartment', {
      size: [74, 13.1, 16.1],
      options: { cores: 2, groupBays: 2, floors: 3, brick: null, siding: null, trim: 0xe9e5da, roof: 0x3b3936,
                 lampsOn: true, lit: 0.3, litUnits: null, glow: 0xffc27a, office: false, officeGlow: 0x7fb2d9, lampLights: false },
      note: 'Options: cores (breezeways 1 to 6), groupBays (bays between cores), floors (2 to 4), brick, siding, trim, roof, lampsOn (true|false|[per core]), lit (share of front units lit, by seed) or litUnits [[bay, floor]...], glow, office ("west"|false), officeGlow, lampLights. A Texas garden walk-up: brick ground floor, lap siding above, a 6/12 gable roof, a balcony and slider on every bay, open breezeway stair cores with wall packs, condensers at the back. userData.units, .cores, .dims, .office.',
      make: function (o, r) {
        var grp = new THREE.Group(), B = Bucket();
        var cores = Math.max(1, Math.min(6, o.cores | 0)), gb = Math.max(1, Math.min(4, o.groupBays | 0));
        var floors = Math.max(2, Math.min(4, o.floors | 0));
        var UW = 7.6, FH = 3.05, D = 13.2, T = 0.3, BW = 3.8, Y0 = 0.25;
        var nBays = (cores + 1) * gb, L = nBays * UW + cores * BW, x0 = -L / 2, zF = D / 2, zB = -D / 2, Htot = floors * FH;
        var pick = function (a) { return a[Math.floor(r() * a.length)]; };
        var brickC = o.brick != null ? o.brick : pick(['#8f5a44', '#9b6a52', '#7d4e3c', '#a7775c', '#b99c7c', '#c2a27e']);
        var sidingC = o.siding != null ? o.siding : pick(['#c9c3b3', '#b8b9ad', '#d2cbbb', '#a9afab', '#c7bba4']);
        var hexs = function (c) { return typeof c === 'string' ? c : '#' + (c >>> 0).toString(16).padStart(6, '0'); };
        var bT = K.tex('brick', { color: hexs(brickC) }), sT = K.tex('siding', { color: hexs(sidingC) }), shT = K.tex('shingle', { color: hexs(o.roof) });
        var bm = bT.userData.metres, sm = sT.userData.metres;
        var bM = K.mat('apt-brick|' + brickC, { color: 0xffffff, map: bT, roughness: 0.92, bumpMap: bT, bumpScale: 1.4 });
        var sM = K.mat('apt-siding|' + sidingC, { color: 0xffffff, map: sT, roughness: 0.8, bumpMap: sT, bumpScale: 0.8 });
        var roofM = K.mat('apt-roof|' + o.roof, { color: 0xffffff, map: shT, roughness: 0.95, bumpMap: shT, bumpScale: 1.6, side: THREE.DoubleSide });
        var trimM = K.mat('apt-trim|' + o.trim, { color: o.trim, roughness: 0.55 });
        var slabM = K.mat('apt-slab', { color: 0xffffff, map: K.tex('concrete'), roughness: 0.93 });
        var railM = K.mat('apt-rail', { color: 0x222426, roughness: 0.45, metalness: 0.55 });
        var frameM = K.mat('apt-frame', { color: 0x3a3029, roughness: 0.5, metalness: 0.3 });     /* dark bronze */
        var soffitM = K.mat('apt-soffit', { color: 0xd8d2c4, roughness: 0.8 });
        var coreWallM = K.mat('apt-corewall', { color: 0x6d675e, roughness: 0.85 });
        var coreSideM = K.mat('apt-coreside|' + sidingC, { color: 0x857f76, map: sT, roughness: 0.85, bumpMap: sT, bumpScale: 0.8 });
        var darkPane = K.finish.glass(0x18212a);
        var mkLit = function (kind, c, i) { return new THREE.MeshStandardMaterial({ color: 0x000000, emissive: c, emissiveIntensity: i, emissiveMap: roomTex(kind), roughness: 0.2 }); };
        var litMats = { blinds: mkLit('blinds', o.glow, 1.3), curtain: mkLit('curtain', o.glow, 1.1) };
        var dimRoom = K.mat('apt-dim', { color: 0x101316, roughness: 0.9 });
        var lampsOn = function (c) { return Array.isArray(o.lampsOn) ? !!o.lampsOn[c] : !!o.lampsOn; };

        /* bay and core x positions along the front, left to right */
        var bayX = [], coreX = [], x = x0;
        for (var g = 0; g <= cores; g++) {
          for (var b = 0; b < gb; b++) { bayX.push(x + UW / 2); x += UW; }
          if (g < cores) { coreX.push(x + BW / 2); x += BW; }
        }
        var officeBay = o.office === 'west' ? 0 : -1;
        var litSet = {};
        if (Array.isArray(o.litUnits)) o.litUnits.forEach(function (u) { litSet[u[0] + ':' + u[1]] = true; });
        else for (var b0 = 0; b0 < nBays; b0++) for (var f0 = 0; f0 < floors; f0++) if (r() < o.lit) litSet[b0 + ':' + f0] = true;

        box(B, slabM, L + 0.3, Y0, D + 0.3, 0, 0, 0, 3.0);
        var units = [], office = null;

        /* the runs of wall between cores, front and back */
        var runs = [];
        for (var g2 = 0; g2 <= cores; g2++) {
          var a = g2 === 0 ? x0 : coreX[g2 - 1] + BW / 2, e = g2 === cores ? x0 + L : coreX[g2] - BW / 2;
          runs.push([a, e, g2 * gb]);
        }
        [false, true].forEach(function (back) {
          var zf = back ? zB : zF, sgn = back ? -1 : 1;
          for (var f = 0; f < floors; f++) {
            var yb = Y0 + f * FH, mat = f === 0 ? bM : sM, uvm = f === 0 ? bm : sm;
            runs.forEach(function (run) {
              var ops = [];
              for (var k = 0; k < gb; k++) {
                var bi = run[2] + k, cx = bayX[bi], flip = (bi % 2) ? -1 : 1;
                if (!back && f === 0 && bi === officeBay) {
                  ops.push({ x0: cx - 3.1, x1: cx + 3.1, y0: yb + 0.05, y1: yb + 2.6, kind: 'store', cx: cx, bi: bi });
                } else if (!back) {
                  ops.push({ x0: cx - flip * 1.25 - 1.15, x1: cx - flip * 1.25 + 1.15, y0: yb + 0.02, y1: yb + 2.12, kind: 'door', cx: cx - flip * 1.25, bi: bi });
                  ops.push({ x0: cx + flip * 2.1 - 0.7, x1: cx + flip * 2.1 + 0.7, y0: yb + 0.9, y1: yb + 2.3, kind: 'win', cx: cx + flip * 2.1, bi: bi });
                } else {
                  ops.push({ x0: cx - 0.6, x1: cx + 0.6, y0: yb + 1.0, y1: yb + 2.2, kind: 'win', cx: cx, bi: bi, backwin: true });
                  ops.push({ x0: cx + flip * 2.4 - 0.45, x1: cx + flip * 2.4 + 0.45, y0: yb + 1.3, y1: yb + 2.2, kind: 'win', cx: cx + flip * 2.4, bi: bi, backwin: true });
                }
              }
              wall(B, mat, uvm, run[0], run[1], yb, FH, zf, T, ops, back);
              box(B, trimM, run[1] - run[0] + 0.02, 0.18, 0.05, (run[0] + run[1]) / 2, yb + FH - 0.18, zf + sgn * 0.025);
              ops.forEach(function (op) {
                var lit = !back && !!litSet[op.bi + ':' + f];
                var w = op.x1 - op.x0, h = op.y1 - op.y0, cy = (op.y0 + op.y1) / 2;
                var room = new THREE.PlaneGeometry(w - 0.04, h - 0.04); if (back) room.rotateY(Math.PI);
                room.translate(op.cx, cy, zf - sgn * (T + 0.25));
                var rm = dimRoom;
                if (op.kind === 'store') rm = mkLit('office', o.officeGlow, 1.6);
                else if (lit) rm = op.kind === 'door' ? litMats.curtain : litMats.blinds;
                B.add(rm, room);
                /* the reveal's back returns, so a lit room has a lit box and not a card */
                if (rm !== dimRoom) {
                  var side = new THREE.PlaneGeometry(0.27, h - 0.04); side.rotateY(Math.PI / 2);
                  var sl = side.clone(); sl.translate(op.x0 + 0.02, cy, zf - sgn * (T + 0.12)); B.add(dimRoom, sl);
                  var sr = side.clone(); sr.rotateY(Math.PI); sr.translate(op.x1 - 0.02, cy, zf - sgn * (T + 0.12)); B.add(dimRoom, sr);
                }
                var gl = new THREE.PlaneGeometry(w - 0.08, h - 0.08); if (back) gl.rotateY(Math.PI);
                gl.translate(op.cx, cy, zf - sgn * (T - 0.1));
                if (rm === dimRoom) B.add(darkPane, gl);
                var fz = zf - sgn * (T - 0.13);
                box(B, frameM, w, 0.05, 0.06, op.cx, op.y0, fz); box(B, frameM, w, 0.05, 0.06, op.cx, op.y1 - 0.05, fz);
                box(B, frameM, 0.05, h, 0.06, op.x0 + 0.025, op.y0, fz); box(B, frameM, 0.05, h, 0.06, op.x1 - 0.025, op.y0, fz);
                if (op.kind === 'store') { for (var mu = 1; mu < 4; mu++) box(B, frameM, 0.05, h, 0.06, op.x0 + w * mu / 4, op.y0, fz); box(B, frameM, w, 0.05, 0.06, op.cx, op.y0 + 2.05, fz); }
                else box(B, frameM, 0.04, h, 0.06, op.cx, op.y0, fz + sgn * 0.01);
                if (op.kind === 'win') box(B, trimM, w + 0.16, 0.06, 0.12, op.cx, op.y0 - 0.06, zf + sgn * 0.04);
                if (op.kind === 'door') units.push({ bay: op.bi, floor: f, x: op.cx, y: cy, z: zf, lit: lit });
                if (op.kind === 'store') office = { x: op.cx, y: cy, z: zf, w: w, h: h };
              });
            });
          }
        });
        /* the leasing office's awning: standing seam on two steel brackets */
        if (office) {
          var awM = K.mat('apt-awning', { color: 0x2c2f31, roughness: 0.4, metalness: 0.6 });
          box(B, awM, office.w + 0.8, 0.08, 1.4, office.x, Y0 + 2.85, zF + 0.7);
          for (var sn = 0; sn < 16; sn++) box(B, awM, 0.02, 0.04, 1.4, office.x - (office.w + 0.8) / 2 + (sn + 0.5) * (office.w + 0.8) / 16, Y0 + 2.93, zF + 0.7);
        }
        /* balconies on the front: a concrete slab on the upper floors, a patio on the ground, each
         * with a steel picket rail, and a siding privacy wing between neighbours */
        for (var f2 = 0; f2 < floors; f2++) {
          var yb2 = Y0 + f2 * FH;
          for (var bb = 0; bb < nBays; bb++) {
            if (f2 === 0 && bb === officeBay) continue;
            var flip2 = (bb % 2) ? -1 : 1, bxC = bayX[bb] - flip2 * 1.25, BWd = 3.2, BD = 1.7;
            if (f2 > 0) box(B, slabM, BWd, 0.16, BD, bxC, yb2 - 0.16, zF + BD / 2, 3.0);
            else box(B, slabM, BWd + 0.4, 0.1, BD + 0.3, bxC, Y0 - 0.06, zF + (BD + 0.3) / 2, 3.0);
            var ry = yb2 + 1.07, xa = bxC - BWd / 2 + 0.05, xb = bxC + BWd / 2 - 0.05, zo = zF + BD - 0.05;
            bar(B, railM, [xa, ry, zo], [xb, ry, zo], 0.028);
            bar(B, railM, [xa, ry, zF + 0.02], [xa, ry, zo], 0.028); bar(B, railM, [xb, ry, zF + 0.02], [xb, ry, zo], 0.028);
            bar(B, railM, [xa, yb2 + 0.12, zo], [xb, yb2 + 0.12, zo], 0.018);
            for (var p = 0; p <= 22; p++) { var px = xa + (xb - xa) * p / 22; bar(B, railM, [px, yb2 + 0.12, zo], [px, ry, zo], 0.009); }
            for (var p2 = 1; p2 < 10; p2++) { var pz = zF + (zo - zF) * p2 / 10;
              bar(B, railM, [xa, yb2 + 0.12, pz], [xa, ry, pz], 0.009); bar(B, railM, [xb, yb2 + 0.12, pz], [xb, ry, pz], 0.009); }
          }
        }
        /* the gable ends, brick on the ground floor, siding above, a small window per floor */
        [[x0, -1], [x0 + L, 1]].forEach(function (en) {
          box(B, bM, T, FH, D, en[0] - en[1] * T / 2, Y0, 0, bm);
          box(B, sM, T, Htot - FH, D, en[0] - en[1] * T / 2, Y0 + FH, 0, sm);
          for (var f3 = 0; f3 < floors; f3++) {
            var wg = new THREE.PlaneGeometry(1.0, 1.2); wg.rotateY(en[1] * Math.PI / 2);
            wg.translate(en[0] + en[1] * 0.01, Y0 + f3 * FH + 1.55, 2.2); B.add(darkPane, wg);
            box(B, frameM, 0.05, 1.3, 1.1, en[0] + en[1] * 0.02, Y0 + f3 * FH + 0.9, 2.2);
          }
        });
        /* the breezeway cores */
        var cores_ = [], doorM = K.mat('apt-door', { color: 0x4a3a2e, roughness: 0.6 });
        var packOn = K.finish.lamp(0xffb868, 3.4), packOff = K.mat('apt-pack-off', { color: 0x3a3632, roughness: 0.5, metalness: 0.3 });
        coreX.forEach(function (cx, ci) {
          var on = lampsOn(ci), xl = cx - BW / 2, xr = cx + BW / 2;
          cores_.push({ x: cx, lampOn: on });
          [[xl, 1], [xr, -1]].forEach(function (s) {
            box(B, coreSideM, T, Htot, D, s[0] + s[1] * T / 2, Y0, 0, sm);
            for (var f4 = 0; f4 < floors; f4++) {
              box(B, doorM, 0.05, 2.05, 0.95, s[0] + s[1] * (T + 0.02), Y0 + f4 * FH, -2.4);
              box(B, frameM, 0.06, 2.12, 1.08, s[0] + s[1] * (T + 0.01), Y0 + f4 * FH, -2.4);
            }
          });
          box(B, coreWallM, BW, Htot, 0.12, cx, Y0, zB + 0.06, sm);
          for (var f5 = 0; f5 < floors; f5++) {
            var yl = Y0 + f5 * FH;
            if (f5 > 0) {
              box(B, slabM, BW - 0.6, 0.18, 3.4, cx, yl - 0.18, -3.9, 3.0);
              box(B, soffitM, BW - 0.6, 0.02, 3.4, cx, yl - 0.2, -3.9);
              bar(B, railM, [xl + 0.3, yl + 1.0, -2.2], [xr - 0.3, yl + 1.0, -2.2], 0.024);
              for (var p3 = 0; p3 <= 10; p3++) { var qx = xl + 0.3 + (BW - 0.6) * p3 / 10; bar(B, railM, [qx, yl, -2.2], [qx, yl + 1.0, -2.2], 0.009); }
            }
            box(B, on ? packOn : packOff, 0.08, 0.3, 0.22, xl + T + 0.04, yl + 2.2, zF - 0.9);
            box(B, on ? packOn : packOff, 0.22, 0.3, 0.1, xl + T + 0.06, yl + 2.0, -1.0);
            box(B, on ? packOn : packOff, 0.22, 0.3, 0.1, xl + T + 0.06, yl + 2.0, -4.6);
          }
          /* the stair: a flight up from the front, a landing, a flight back, per floor */
          for (var f6 = 0; f6 < floors - 1; f6++) {
            var ys = Y0 + f6 * FH, n = 16, rise = FH / n, run = 0.27, half = (BW - 0.7) / 2;
            var up = f6 % 2 === 0, xs = up ? xl + 0.35 : xr - 0.35 - half;
            var zStart = up ? zF - 0.2 : -5.6 + 0.1, dir = up ? -1 : 1;
            for (var s2 = 0; s2 < n; s2++) {
              var zt = zStart + dir * (s2 + 0.5) * run;
              box(B, slabM, half, 0.05, run + 0.02, xs + half / 2, ys + (s2 + 1) * rise - 0.05, zt);
            }
            var za = zStart, zb = zStart + dir * n * run;
            [xs + 0.06, xs + half - 0.06].forEach(function (sx) { bar(B, railM, [sx, ys, za], [sx, ys + FH, zb], 0.05); });
            bar(B, railM, [xs + (up ? half : 0), ys + 1.0, za], [xs + (up ? half : 0), ys + FH + 1.0, zb], 0.022);
          }
          box(B, soffitM, BW, 0.1, D, cx, Y0 + Htot - 0.1, 0);
          if (on && o.lampLights) {
            for (var lf = 0; lf < floors; lf++) { var pl = new THREE.PointLight(0xffb05a, 4, 7, 2); pl.position.set(cx - 0.6, Y0 + lf * FH + 2.2, zF - 1.4); pl.castShadow = false; grp.add(pl); }
          }
        });
        /* the gable roof, 6 in 12, ridge along x, eaves 0.6 m out, rakes 0.4 m */
        var ov = 0.6, rk = 0.4, ye = Y0 + Htot + 0.05, xa2 = x0 - rk, xb2 = x0 + L + rk, za2 = zB - ov, zb2 = zF + ov;
        var yr = ye + (zb2 - za2) / 2 * 0.5, zc = 0;
        (function () {
          var P = [], UV = [], m = shT.userData.metres;
          var quad = function (p) {
            var a = new V3(p[0][0], p[0][1], p[0][2]), b = new V3(p[1][0], p[1][1], p[1][2]), c = new V3(p[3][0], p[3][1], p[3][2]);
            var u = b.clone().sub(a).normalize(), v = c.clone().sub(a).normalize();
            [[0, 1, 2], [0, 2, 3]].forEach(function (t) { t.forEach(function (i) { var q = p[i]; P.push(q[0], q[1], q[2]);
              var d = new V3(q[0], q[1], q[2]).sub(a); UV.push(d.dot(u) / m, d.dot(v) / m); }); });
          };
          quad([[xa2, ye, zb2], [xb2, ye, zb2], [xb2, yr, zc], [xa2, yr, zc]]);
          quad([[xb2, ye, za2], [xa2, ye, za2], [xa2, yr, zc], [xb2, yr, zc]]);
          var geo = new THREE.BufferGeometry();
          geo.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(UV, 2));
          geo.computeVertexNormals(); B.add(roofM, geo);
          /* the gable triangles above the end walls, in siding */
          [x0, x0 + L].forEach(function (gx, gi) {
            var tri = new THREE.BufferGeometry(), s = gi ? 1 : -1;
            var pts = [[gx, ye, zB], [gx, ye, zF], [gx, yr - 0.1, 0]];
            if (!gi) pts = [pts[1], pts[0], pts[2]];
            var flat = []; pts.forEach(function (q) { flat.push(q[0], q[1], q[2]); });
            tri.setAttribute('position', new THREE.Float32BufferAttribute(flat, 3));
            tri.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, D / sm, 0, D / 2 / sm, (yr - ye) / sm], 2));
            tri.computeVertexNormals(); B.add(sM, tri);
            var vent = new THREE.PlaneGeometry(1.0, 0.6); vent.rotateY(s * Math.PI / 2); vent.translate(gx + s * 0.02, ye + 1.0, 0); B.add(frameM, vent);
          });
        })();
        box(B, trimM, xb2 - xa2, 0.24, 0.06, 0, ye - 0.2, zb2); box(B, trimM, xb2 - xa2, 0.24, 0.06, 0, ye - 0.2, za2);
        box(B, soffitM, xb2 - xa2, 0.02, ov, 0, ye - 0.02, zF + ov / 2); box(B, soffitM, xb2 - xa2, 0.02, ov, 0, ye - 0.02, zB - ov / 2);
        box(B, K.mat('apt-ridge|' + o.roof, { color: o.roof, roughness: 0.9 }), xb2 - xa2, 0.08, 0.34, 0, yr - 0.03, 0);
        [xa2 + 0.3, xb2 - 0.3].concat(coreX.map(function (c) { return c - BW / 2 - 0.15; })).forEach(function (dx) {
          box(B, trimM, 0.08, ye - 0.05, 0.08, dx, 0, zF + 0.08); box(B, trimM, 0.08, ye - 0.05, 0.08, dx, 0, zB - 0.08);
        });
        /* condensers on pads along the back */
        var cM = K.mat('apt-cond', { color: 0xb9bcbd, roughness: 0.5, metalness: 0.4 }), grille = K.mat('apt-grille', { color: 0x2b2d2f, roughness: 0.7 });
        bayX.forEach(function (bxp) {
          for (var q = 0; q < floors; q++) {
            var cxp = bxp - 1.2 + q * 1.1;
            box(B, slabM, 0.95, 0.1, 0.95, cxp, 0, zB - 1.1, 3.0); box(B, cM, 0.8, 0.8, 0.8, cxp, 0.1, zB - 1.1); box(B, grille, 0.62, 0.02, 0.62, cxp, 0.9, zB - 1.1);
          }
        });
        B.flush(grp);
        grp.userData.units = units; grp.userData.cores = cores_; grp.userData.office = office;
        grp.userData.dims = { L: L, D: D, eave: ye, ridge: yr, floorH: FH, y0: Y0, bays: bayX.slice() };
        return grp;
      }
    });
  };

  /* THE HERO, as every frame makes it. One call so the building is the same building. */
  N.hero = function (K, o) {
    return K.make("garden_apartment", Object.assign({ seed: 5, cores: 5, groupBays: 2, floors: 3, brick: "#9b6a52", siding: "#c7bba4",
      lit: 0, office: "west", officeGlow: N.ACCENT, lampLights: true }, o || {}));
  };

  /* A LOT LAMP: the kit's streetlight with a real sodium light under its head. The kit pole has
   * its foot at the origin and the arm over +x; the head sits reach metres out. */
  N.lotLamp = function (THREE, TXT, K, R, x, z, o) {
    o = o || {};
    var h = o.height || 9, reach = o.reach || 2.4, ry = o.ry || 0;
    var l = K.make("streetlight", { height: h, reach: reach, seed: o.seed || 31 });
    l.position.set(x, o.y || 0, z); l.rotation.y = ry; TXT.add(R, l);
    var hx = x + Math.cos(ry) * reach, hz = z - Math.sin(ry) * reach;
    var pl = new THREE.PointLight(N.SODIUM, o.i != null ? o.i : 110, o.range || 30, 2);
    pl.position.set(hx, (o.y || 0) + h - 0.35, hz); R.scene.add(pl);
    return l;
  };

  /* PARKING: painted stall lines and a concrete curb, true size (2.74 m stalls, 5.5 m deep). */
  N.stalls = function (THREE, TXT, R, x0, z0, n, o) {
    o = o || {};
    var paint = new THREE.MeshStandardMaterial({ color: 0xcfcac0, roughness: 0.7 });
    var g = new THREE.Group(), W = o.w || 2.74, Dp = o.d || 5.5, dir = o.dir || 1;
    for (var i = 0; i <= n; i++) {
      var m = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.012, Dp), paint);
      m.position.set(x0 + i * W, (o.y || 0) + 0.006, z0 + dir * Dp / 2); m.receiveShadow = true; g.add(m);
    }
    if (o.curb !== false) {
      var cm = new THREE.MeshStandardMaterial({ color: 0x8e887d, roughness: 0.9 });
      var c = TXT.roundedBox(n * W + 0.3, 0.15, 0.3, 0.03, cm);
      c.position.set(x0 + n * W / 2, (o.y || 0) + 0.075, z0 + dir * (Dp + 0.2)); g.add(c);
    }
    R.scene.add(g);
    return g;
  };

  /* A world point to frame CSS px, through the frame's own camera, for leaders that land on
   * what they name. */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };

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
  /* Refuses a black render, paints it onto the frame's art canvas, hands the context back for
   * TXDECK.finish, which every frame calls itself, last. */
  N.develop = function (shot, glCanvas) {
    if (!shot || !shot.ok) throw new Error("the GPU frame came back black: " + JSON.stringify(shot));
    var cx = document.getElementById("art").getContext("2d");
    cx.scale(2, 2);
    cx.drawImage(glCanvas, 0, 0, N.W, N.H);
    return cx;
  };

  global.NIGHTRENT = N;
})(this);
