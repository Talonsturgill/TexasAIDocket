/* deck/2026-11-12-roster.js — the chassis for the 2026-11-12 deck: the Texas Department of Motor Vehicles' Company and
 * Vehicle Summary Report, data as of October 29th, 2026, lists 17 companies and 3,164 automated motor vehicles under the
 * authorization Senate Bill 2807 created (tx-2026-0188).
 *
 * THE VISUAL ARGUMENT. The roster, parked. One stand-in car for every ten listed vehicles (figures.json `unit`, rounded
 * half up, never fewer than one), parked in rows of ten bays, so a full row is a hundred listed vehicles. Three columns:
 * Waymo, Tesla Robotaxi, then a painted stripe, then the fifteen others in rank order, Avride's rows and fourteen rows
 * that never fill. The lot changes state through the deck (whole, split, thinned to its tail, one car out on the street,
 * seen from outside the fence). Every count is read from figures.json in the frame's own code. The chassis types none.
 * The stand-in is one neutral model in one paint, drawn to illustrate: no maker's likeness, livery or vehicle type.
 *
 * THE WORLD. lastLight, a STAGED world. The sun is just down to the west-southwest: the key is azimuth -55, elevation 10,
 * low on the frame's left, so every lit flank looks left and every car casts long to the right across the next bay.
 *
 * THE ACCENT. dusk_gold #E0956A means ONE thing: the line where the two largest names end and the other fifteen begin.
 * It is the painted stripe down that aisle and nothing else.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having neither: `wheel_stop` (a 1.83 m precast concrete curb stop with chamfers,
 * pin holes and chipped corners) and `fleet_lot` (the roster parked: stand-in kit crossovers instanced from one baked
 * model per material in rows of ten bays, with stall bars and wheel stops). Both in the kit's conventions (metres, y up,
 * origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("roster.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "roster",
    light: { az: -55, el: 10 },
    sky: { preset: "lastLight", haze: 0x0b0f15 },
    ground: "#16171B",
    material: "#C9C2B2",
    accent: "#E0956A",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.06, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.2,
      bloom: { threshold: 0.9, strength: 0.12, radius: 6 },
      grain: { amount: 0.014, size: 2, seed: 20261112 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261112; N.INK = "#EDE6D6";
  N.GOLD = 0xE0956A;      /* dusk_gold: where the two largest names end, and nothing else */
  N.PAINT = 0xB9B3A6;     /* the stand-in's one neutral paint, a weathered limestone grey */

  /* ---- THE LOT, as a pure function of the figures ----------------------------------------------------------------- */
  /* bays are 2.75 m wide and 5.5 m deep; rows of ten bays run along x; rows pair back to back with a 7.5 m aisle between
   * pairs; columns are 10 bays wide with an 8 m aisle between them. Returns every bay with its company, row and whether a
   * stand-in car is parked in it. `order` is the rank, `units` maps company to drawn units. */
  N.BAY = { w: 2.75, d: 5.5, aisle: 7.5, colGap: 8.0, per: 10 };
  N.lotPlan = function (order, units) {
    /* THE FIFTEEN ARE PACKED (art director, audition 1): the third column fills its bays continuously in rank order, so
     * its depth is u_rest over ten and the three lengths compare honestly from one front baseline. `dividers` marks every
     * bay boundary where one company ends and the next begins. */
    var B = N.BAY, colW = B.per * B.w, cols = [[order[0]], [order[1]], order.slice(2)], bays = [], rows = [], dividers = [];
    cols.forEach(function (list, ci) {
      var x0 = (ci - 1) * (colW + B.colGap) - colW / 2, seq = [];
      list.forEach(function (name) { for (var u = 0; u < units[name]; u++) seq.push(name); });
      var nRows = Math.ceil(seq.length / B.per);
      for (var r = 0; r < nRows; r++) {
        var pair = Math.floor(r / 2), side = r % 2, z = -(pair * (2 * B.d + B.aisle) + side * B.d + B.d / 2), face = side ? Math.PI : 0;
        var filled = Math.min(B.per, seq.length - r * B.per);
        rows.push({ col: ci, row: r, filled: filled, z: z, x0: x0, face: face, companies: seq.slice(r * B.per, r * B.per + filled) });
        for (var b = 0; b < B.per; b++) {
          var k = r * B.per + b, name = k < seq.length ? seq[k] : null;
          bays.push({ company: name, col: ci, row: r, x: x0 + (b + 0.5) * B.w, z: z, face: face, car: name !== null });
          if (ci === 2 && name !== null && b > 0 && seq[k - 1] !== name) dividers.push({ x: x0 + b * B.w, z: z, company: name });
        }
      }
    });
    var xs = bays.map(function (q) { return q.x; }), zs = bays.map(function (q) { return q.z; });
    return { bays: bays, rows: rows, cols: cols, dividers: dividers, minX: Math.min.apply(null, xs) - B.w, maxX: Math.max.apply(null, xs) + B.w,
      minZ: Math.min.apply(null, zs) - B.d, maxZ: Math.max.apply(null, zs) + B.d,
      stripeX: (colW / 2) + B.colGap / 2 };
  };

  /* THE GLASS CARRIES THE SEAM (art director, audition 2): a dark dome with the warm horizon band as the coated glass's own
   * environment, so every windshield shows the last light rather than a flat grey slab. Built once. */
  N.glassEnv = function (THREE) {
    if (N._genv) return N._genv;
    var c = document.createElement("canvas"); c.width = 1024; c.height = 512; var g = c.getContext("2d");
    var gr = g.createLinearGradient(0, 0, 0, 512);
    gr.addColorStop(0, "#04060a"); gr.addColorStop(0.36, "#0b1018"); gr.addColorStop(0.46, "#3a2a26"); gr.addColorStop(0.495, "#c8814c");
    gr.addColorStop(0.505, "#7a4a30"); gr.addColorStop(0.56, "#141416"); gr.addColorStop(1, "#08080a");
    g.fillStyle = gr; g.fillRect(0, 0, 1024, 512);
    var t = new THREE.CanvasTexture(c); t.mapping = THREE.EquirectangularReflectionMapping; t.colorSpace = THREE.SRGBColorSpace; N._genv = t; return t;
  };
  /* THE GOLD LANE IS WORN PAINT (art director, review 5): a wear map lets the asphalt show through so it reads as paint on
   * the ground, and a self light outside the tone curve holds its one hue on every frame it crosses, the deck's accent. */
  N.stripeMat = function (THREE) {
    if (N._smat) return N._smat;
    var c = document.createElement("canvas"); c.width = 64; c.height = 512; var g = c.getContext("2d"), img = g.createImageData(64, 512), d = img.data;
    for (var y = 0; y < 512; y++) for (var x = 0; x < 64; x++) {
      var n = 0.5 + 0.5 * TX.fbm2(x / 9, y / 9, 4), f = 0.5 + 0.5 * TX.fbm2(x / 2, y / 2, 2), k = n > 0.74 ? 0.55 : 0.94 + 0.06 * f;
      var i = (y * 64 + x) * 4; d[i] = 255 * k; d[i + 1] = 255 * k; d[i + 2] = 255 * k; d[i + 3] = 255; }
    g.putImageData(img, 0, 0); var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1, 40); t.colorSpace = THREE.SRGBColorSpace;
    N._smat = new THREE.MeshBasicMaterial({ color: N.GOLD, map: t, toneMapped: false, fog: false });
    N._smat.userData = { txWear: false }; return N._smat;
  };
  N.isGlass = function (m) { return m && m.clearcoat >= 0.9 && m.roughness < 0.1 && m.metalness < 0.5; };
  N.finishGlass = function (THREE, root) {
    root.traverse(function (o) { if (o.isMesh && N.isGlass(o.material)) { o.material.envMap = N.glassEnv(THREE); o.material.envMapIntensity = 1.8; o.material.needsUpdate = true; } });
  };

  /* ---- the kit models this deck builds ------------------------------------------------------------------------------ */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.wheel_stop) return;
    function concTex(seed) {
      var c = document.createElement("canvas"); c.width = c.height = 256; var g = c.getContext("2d"), img = g.createImageData(256, 256), d = img.data;
      for (var y = 0; y < 256; y++) for (var x = 0; x < 256; x++) {
        var n = 0.5 + 0.5 * TX.fbm2(x / 22 + seed, y / 22, 4), f = 0.5 + 0.5 * TX.fbm2(x / 3, y / 3, 2), v = 150 + 34 * (n - 0.5) + 26 * (f - 0.5);
        var i = (y * 256 + x) * 4; d[i] = v; d[i + 1] = v * 0.98; d[i + 2] = v * 0.94; d[i + 3] = 255; }
      g.putImageData(img, 0, 0); var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
    }
    var CT = concTex(3);
    var CONC = new THREE.MeshStandardMaterial({ color: 0xa8a399, map: CT, bumpMap: CT, bumpScale: 1.2, roughness: 0.92, metalness: 0 });
    var REBAR = K.mat("ro-rebar", { color: 0x4a3a2c, roughness: 0.7, metalness: 0.6 });

    /* WHEEL STOP: a 1.83 x 0.23 x 0.15 m precast curb stop, 20 mm chamfers on the top edges, two pin holes with rebar
     * stubs, one corner chipped by a seeded amount. Long axis on x. */
    K.define("wheel_stop", {
      size: [1.83, 0.15, 0.23],
      options: { seed: 1, chip: 0.5 },
      note: "A 1.83 m precast concrete parking curb stop with chamfered top edges, two pin holes with flush rebar stubs and a chipped corner.",
      make: function (o) {
        var G = new THREE.Group(), L = 1.83, H = 0.15, D = 0.23;
        var b = TXT.roundedBox(L, H, D, 0.02, CONC); b.position.y = H / 2; G.add(b);
        var rr = ((o.seed || 1) * 9301 + 49297) % 233280 / 233280;
        if (o.chip) { var ch = TXT.roundedBox(0.09 + 0.06 * rr, 0.06, 0.07, 0.01, K.mat("ro-dark", { color: 0x0c0d10, roughness: 1 })); ch.position.set((rr > 0.5 ? 1 : -1) * (L / 2 - 0.03), H - 0.02, D / 2 - 0.02); G.add(ch); }
        [-0.6, 0.6].forEach(function (x) { var p = new THREE.Mesh(new THREE.CylinderGeometry(0.0125, 0.0125, 0.012, 10), REBAR); p.position.set(x, H + 0.003, 0); G.add(p); });
        G.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return G;
      }
    });

    /* bake a group (identity) into one geometry per material, so a model can be instanced */
    function bake(group) {
      group.updateMatrixWorld(true); var by = new Map();
      group.traverse(function (m) {
        if (!m.isMesh || m.isInstancedMesh) return;
        var g = m.geometry.index ? m.geometry.toNonIndexed() : m.geometry.clone(); g.applyMatrix4(m.matrixWorld);
        ["position", "normal", "uv"].forEach(function (k) { if (!g.attributes[k] && k === "normal") g.computeVertexNormals(); });
        Object.keys(g.attributes).forEach(function (k) { if (["position", "normal", "uv"].indexOf(k) < 0) g.deleteAttribute(k); });
        if (!g.attributes.uv) g.setAttribute("uv", new THREE.BufferAttribute(new Float32Array(g.attributes.position.count * 2), 2));
        if (!by.has(m.material)) by.set(m.material, []); by.get(m.material).push(g);
      });
      var out = [];
      by.forEach(function (gs, mat) {
        var n = 0; gs.forEach(function (g) { n += g.attributes.position.count; });
        var P = new Float32Array(n * 3), Nn = new Float32Array(n * 3), U = new Float32Array(n * 2), o = 0;
        gs.forEach(function (g) { P.set(g.attributes.position.array, o * 3); Nn.set(g.attributes.normal.array, o * 3); U.set(g.attributes.uv.array, o * 2); o += g.attributes.position.count; });
        var geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(P, 3)); geo.setAttribute("normal", new THREE.BufferAttribute(Nn, 3)); geo.setAttribute("uv", new THREE.BufferAttribute(U, 2));
        geo.computeBoundingSphere(); out.push({ geo: geo, mat: mat });
      });
      return out;
    }
    N.bake = bake;
    function instance(parts, list, parent) {
      var M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), one = new THREE.Vector3(1, 1, 1);
      parts.forEach(function (pt) {
        var im = new THREE.InstancedMesh(pt.geo, pt.mat, list.length);
        list.forEach(function (p, i) { e.set(0, p[3] || 0, 0); q.setFromEuler(e); M.compose(new THREE.Vector3(p[0], p[1], p[2]), q, one); im.setMatrixAt(i, M); });
        im.instanceMatrix.needsUpdate = true; im.computeBoundingSphere(); im.castShadow = true; im.receiveShadow = true; parent.add(im);
      });
    }
    N.instance = instance;

    /* FLEET LOT: the roster parked. order: companies in rank; units: company -> drawn units. near: a list of bay indices
     * drawn as full kit models (seated with TXT.contact by the frame), the rest instanced. stalls/stops: bars and stops. */
    K.define("fleet_lot", {
      size: [91, 0.6, 160],
      options: { order: null, units: null, near: [], stalls: true, stops: true, paint: N.PAINT, stripe: true, omit: [], dividers: true },
      note: "The roster parked at one stand-in crossover per drawn unit, rows of ten bays in three columns, stall bars, wheel stops and a dusk_gold stripe after the second column. userData.plan carries every bay.",
      make: function (o) {
        var G = new THREE.Group(), plan = N.lotPlan(o.order, o.units), B = N.BAY; G.userData.plan = plan; G.userData.nearModels = [];
        var proto = K.make("crossover", { color: o.paint, metallic: false, sensors: true, seed: 75 });
        /* the coated glass takes the seam: a low roughness and a stronger environment, so the cabins are not flat grey */
        N.finishGlass(THREE, proto);
        var parts = bake(proto), cars = [], nearSet = {}; (o.near || []).forEach(function (i) { nearSet[i] = 1; });
        var omit = {}; (o.omit || []).forEach(function (i) { omit[i] = 1; });
        plan.bays.forEach(function (q, i) {
          if (!q.car || omit[i]) return;
          var jit = (((i * 7919) % 97) / 97 - 0.5);
          var zc = q.z + (q.face ? -1 : 1) * (0.15 + 0.12 * jit), rot = q.face + 0.03 * jit;
          if (nearSet[i]) { var m = K.make("crossover", { color: o.paint, metallic: false, sensors: true, seed: 75 }); N.finishGlass(THREE, m); m.position.set(q.x, 0, zc); m.rotation.y = rot; G.add(m); G.userData.nearModels.push(m); }
          else cars.push([q.x + 0.06 * jit, 0, zc, rot]);
        });
        if (cars.length) instance(parts, cars, G);
        if (o.stalls) {
          var bar = K.make("pavement_bar", { w: 0.1, l: B.d, wear: "worn" }), bp = bake(bar), lines = [];
          plan.rows.forEach(function (r) { for (var b = 0; b <= B.per; b++) lines.push([r.x0 + b * B.w, 0, r.z, 0]); });
          instance(bp, lines, G);
        }
        if (o.stops) {
          var st = bake(K.make("wheel_stop", { seed: 4 })), stops = [];
          plan.bays.forEach(function (q) { stops.push([q.x, 0, q.z + (q.face ? 1 : -1) * (B.d / 2 - 0.45), 0]); });
          instance(st, stops, G);
        }
        if (o.dividers && plan.dividers.length) {
          var dv = bake(K.make("pavement_bar", { w: 0.6, l: B.d, wear: "fresh", color: 0xF2EFE8 })), dl = [];
          /* fresh white paint with a faint self light, so a company's end reads white under a dusk sky rather than sky blue */
          var dvm = new THREE.MeshStandardMaterial({ color: 0xF2EFE8, roughness: 0.7, metalness: 0, emissive: 0xE8E4DA, emissiveIntensity: 0.55 });
          dv.forEach(function (pt) { pt.mat = dvm; });
          plan.dividers.forEach(function (d) { dl.push([d.x, 0.004, d.z, 0]); });
          instance(dv, dl, G);
        }
        if (o.stripe) {
          var len = plan.maxZ - plan.minZ, sb = K.make("pavement_bar", { w: 1.8, l: len, wear: "worn", color: N.GOLD });
          sb.position.set(plan.stripeX, 0, (plan.maxZ + plan.minZ) / 2); G.add(sb); G.userData.stripe = sb;
          /* the gold paint holds one hue in every light, so the deck's one accent reads as one colour on every frame it crosses */
          sb.traverse(function (m) { if (m.isMesh) { m.material = N.stripeMat(THREE); m.castShadow = false; } });
        }
        return G;
      }
    });
  };

  /* THE DECK'S DRESSING, once: the darken-only washes every frame lays before TXDECK.finish */
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

  /* THE HALL: one windowless machine hall with no ceiling, the flood hung high out of frame. A frame calls TXT.interior
   * itself with these options, because a room is the frame's own decision to stand somewhere. */
  N.roomOpts = function (o) {
    o = o || {};
    return { w: o.w || 16, d: o.d || 16, h: 4.2, floor: "concrete", wall: o.wall || 0x15171b, window: null, ceiling: false, light: o.light == null ? 0.08 : o.light };
  };
  /* the raised floor, placed so its walking surface is at FLOOR_H, with the hall's own floor as the slab under it */
  N.floor = function (TXT, R, K, o) {
    var f = K.make("raised_floor", o || {}); TXT.add(R, f); return f;
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
  /* THE HALL GOES COLD AND DARK: the studio environment lifts the walls to grey, so a frame calls this after the rig. */
  N.darkHall = function (R, o) {
    o = o || {};
    R.scene.environmentIntensity = o.env == null ? 0.08 : o.env;
    R.scene.traverse(function (l) { if (!l.isLight) return; if (l.isHemisphereLight || l.isAmbientLight) l.intensity *= (o.amb == null ? 0.35 : o.amb);
      else if (l.isDirectionalLight && !l.castShadow) l.intensity *= (o.fill == null ? 0.4 : o.fill); });   /* the preset's lavender fill lit the floor periwinkle; the hall keeps only a trace of it */
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


  /* ---- frame helpers, carried from the 2026-11-08 chassis ---------------------------------- */
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
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
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
