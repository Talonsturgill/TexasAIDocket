/* deck/2026-11-11-cityline.js — the chassis for the 2026-11-11 deck: SpaceX asks the City of Starbase for a Chapter 312
 * tax abatement and a Chapter 380 agreement on a gas-fired power plant and super-compute facility on an approximately
 * 444-acre tract in Cameron County that Brownsville de-annexed at SpaceX's request; the hearing is December 9th
 * (tx-2026-0246).
 *
 * THE VISUAL ARGUMENT. The line. A city limit is the one legal object a reader already knows as a physical thing: the
 * green sign on two posts and the lath and flagging that mark a line in the ground. The deck carries that line: the sign,
 * a square of the tract's area at true scale, the estimate stacked as blocks of the water ceiling, a pulled stake, a
 * flagged line to the horizon, the plant beyond it, the room where the public is heard, and the sign again at night.
 * Every count a frame draws is read from figures.json in that frame's own code. The chassis types no figure.
 *
 * THE WORLD. lastLight, a STAGED world. The sun is just down over Brownsville, to the west: the key is azimuth -68,
 * elevation 7, low on the frame's left, so every lit face looks left and every cast runs long to the right, east, onto
 * the tract. The warm seam lies on the city's side. The hearing room keeps the same key through its left window.
 *
 * THE ACCENT. signal_open #4FC79A, measured as rendered at #3FA07A, the green of a city limit sign, means ONE thing: a city limit as it stands now. The
 * sign face, the flagging on the line and the square's edge carry it. The blocks and the room carry none.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having neither: `survey_lath` (a pine survey stake with flagging,
 * standing or lying, with a clay foot), and `unit_block` (a 2 m precast concrete cube with chamfers, lifting loops and form
 * tie dimples). The road markers are the kit's own `pavement_marker`. All in the kit's conventions (metres, y
 * up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("cityline.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "cityline",
    light: { az: -68, el: 7 },
    sky: { preset: "lastLight", haze: 0x0b1016 },
    ground: "#3E352B",
    material: "#9C968A",
    accent: "#3FA07A",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.06, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.2,
      bloom: { threshold: 0.9, strength: 0.12, radius: 6 },
      grain: { amount: 0.014, size: 2, seed: 20261111 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261111; N.INK = "#EDE6D6";
  N.GREEN = 0x4FC79A;     /* signal_open: a city limit as it stands now, and nothing else */

  /* ---- the kit models this deck builds ------------------------------------------------------ */
  N.LATH = { h: 1.22, w: 0.038, t: 0.0095 };
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.survey_lath) return;
    var PINE = K.mat("cl-pine", { color: 0x9c8460, roughness: 0.82, metalness: 0.0 });
    var PINEO = K.mat("cl-pineo", { color: 0x7a6a52, roughness: 0.9, metalness: 0.0 });
    var CLAY = K.mat("cl-clay", { color: 0x2a231c, roughness: 0.95, metalness: 0.0 });
    var FLAG = K.mat("cl-flag", { color: N.GREEN, roughness: 0.35, metalness: 0.0, emissive: 0x3fa07a, emissiveIntensity: 0.55 });
    var FLAGOLD = K.mat("cl-flagold", { color: 0x8a8a74, roughness: 0.6, metalness: 0.0 });
    /* precast: aggregate and bug holes in the albedo and the bump, never in the geometry */
    function precastTex() {
      var c = document.createElement("canvas"); c.width = c.height = 512; var g = c.getContext("2d"), img = g.createImageData(512, 512), d = img.data;
      var rnd = (function (t) { return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; })(N.SEED);
      for (var y = 0; y < 512; y++) for (var x = 0; x < 512; x++) {
        var n = 0.5 + 0.5 * TX.fbm2(x / 38, y / 38, 4), f = 0.5 + 0.5 * TX.fbm2(x / 4, y / 4, 2), v = 196 + 40 * (n - 0.5) + 30 * (f - 0.5);
        var i = (y * 512 + x) * 4; d[i] = v; d[i + 1] = v * 0.98; d[i + 2] = v * 0.93; d[i + 3] = 255; }
      g.putImageData(img, 0, 0);
      for (var k = 0; k < 260; k++) { g.fillStyle = "rgba(40,36,32," + (0.18 + 0.3 * rnd()) + ")"; g.beginPath(); g.arc(rnd() * 512, rnd() * 512, 0.5 + rnd() * 1.1, 0, 7); g.fill(); }
      var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4; return t;
    }
    var PCT = precastTex();
    var CONC = new THREE.MeshStandardMaterial({ color: 0xf0ece4, map: PCT, bumpMap: PCT, bumpScale: 1.4, roughness: 0.9, metalness: 0.0 });
    var LOOP = K.mat("cl-loop", { color: 0x6a5a48, roughness: 0.6, metalness: 0.8 });
    var MBODY = K.mat("cl-mbody", { color: 0xe8e4d8, roughness: 0.5, metalness: 0.0 });
    var AMBER = new THREE.MeshStandardMaterial({ color: 0xe0a030, emissive: 0xe0a030, emissiveIntensity: 1.6, roughness: 0.3 });
    AMBER.userData = { txWear: false };

    /* a flagging tail: a thin ribbon bent by a seeded curve, hanging from a point */
    function ribbon(len, wid, droop, twist, mat) {
      var geo = new THREE.PlaneGeometry(wid, len, 1, 12); var p = geo.attributes.position;
      for (var i = 0; i < p.count; i++) { var y = p.getY(i), t = (len / 2 - y) / len; p.setZ(i, droop * t * t + Math.sin(t * 3.0 + twist) * 0.015); p.setX(i, p.getX(i) + Math.sin(t * 2.2 + twist) * 0.02); }
      geo.computeVertexNormals(); var m = new THREE.Mesh(geo, mat); m.material.side = THREE.DoubleSide; return m;
    }

    /* SURVEY LATH: a pine stake 1.22 x 0.038 x 0.0095 m with a 0.10 m pointed foot, flagging tied near the top.
     * lying: on its face on the ground, foot to +x. flag: 'green' | 'old' | 'none'. mud: the dark clay line on the foot. */
    K.define("survey_lath", {
      size: [0.038, 1.22, 0.0095],
      options: { flag: "green", lying: false, mud: 0.28, lean: 0, seed: 1, tails: 2, scale: 1 },
      note: "A pine survey lath with a pointed foot, dark wet clay on its foot and one or two flagging tails tied near the top; standing (driven 0.15 m) or lying on its face.",
      make: function (o) {
        var G = new THREE.Group(), L = N.LATH, sc = o.scale || 1, h = L.h * sc, w = L.w * sc, t = L.t * sc, foot = 0.10 * sc;
        var body = TXT.roundedBox(w, h - foot, t, 0.0015 * sc, PINE); body.position.y = foot + (h - foot) / 2; G.add(body);
        var sh = new THREE.Shape(); sh.moveTo(-w / 2, 0); sh.lineTo(w / 2, 0); sh.lineTo(0.004 * sc, -foot); sh.lineTo(-0.004 * sc, -foot); sh.lineTo(-w / 2, 0);
        var tip = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: t, bevelEnabled: false }), PINE); tip.position.set(0, foot, -t / 2); G.add(tip);
        if (o.mud) { var mud = TXT.roundedBox(w * 1.04, o.mud * sc, t * 1.15, 0.001 * sc, CLAY); mud.position.y = foot + o.mud * sc / 2 - 0.02 * sc; G.add(mud); var mt = tip.clone(); mt.material = CLAY; mt.scale.set(1.05, 1, 1.15); G.add(mt); }
        if (o.flag !== "none") {
          var fm = o.flag === "old" ? FLAGOLD : FLAG, n = o.tails || 2;
          var knot = TXT.roundedBox(w * 1.25, 0.03 * sc, t * 2.2, 0.004 * sc, fm); knot.position.y = h - 0.09 * sc; G.add(knot);
          for (var k = 0; k < n; k++) { var r = ribbon(0.55 * sc, 0.03 * sc, o.flag === "old" ? 0.02 : 0.12 * sc, (o.seed || 1) * 1.7 + k * 2.1, fm); r.position.set((k - 0.5) * 0.012 * sc, h - 0.09 * sc - 0.27 * sc, t + 0.002); r.rotation.y = 0.3 + k * 0.5; G.add(r); }
        }
        if (o.lying) { G.rotation.z = -Math.PI / 2; G.rotation.y = 0; G.position.y = t / 2 + 0.001; var outer = new THREE.Group(); outer.add(G); G.rotation.x = Math.PI / 2; outer.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return outer; }
        G.position.y = -0.15 * sc; if (o.lean) G.rotation.z = o.lean;
        var W = new THREE.Group(); W.add(G); W.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return W;
      }
    });

    /* UNIT BLOCK: a 2 m precast concrete cube, chamfered, two cast-in lifting loops on top, a faint grid of form tie
     * dimples on each side face. Drawn to illustrate a unit; never a real block. */
    K.define("unit_block", {
      size: [2.0, 2.06, 2.0],
      options: { s: 2.0, loops: true, seed: 1 },
      note: "A 2 m precast concrete cube with 40 mm chamfers, two steel lifting loops on top and form tie dimples on its sides.",
      make: function (o) {
        var G = new THREE.Group(), s = o.s || 2.0;
        /* each pour cures a shade apart: a seeded tone per block, so a stack reads as units and not one slab */
        var rr = ((o.seed || 1) * 9301 + 49297) % 233280 / 233280, tone = 0.86 + 0.24 * rr;
        var MAT = CONC.clone(); MAT.color = CONC.color.clone().multiplyScalar(tone); MAT.roughness = 0.82 + 0.12 * rr;
        var b = TXT.roundedBox(s, s, s, 0.06, MAT); b.position.y = s / 2; G.add(b);
        var dim = new THREE.CylinderGeometry(0.022, 0.022, 0.01, 12);
        [0, 1, 2, 3].forEach(function (f) { for (var i = 0; i < 2; i++) for (var j = 0; j < 2; j++) {
          var d = new THREE.Mesh(dim, CLAY), off = (i - 0.5) * s * 0.5, y = s * (0.3 + j * 0.4), ang = f * Math.PI / 2;
          d.rotation.x = Math.PI / 2; d.rotation.z = 0; var x = Math.sin(ang) * (s / 2 + 0.002), z = Math.cos(ang) * (s / 2 + 0.002);
          d.position.set(x + Math.cos(ang) * off, y, z - Math.sin(ang) * off); d.rotation.y = ang; G.add(d); } });
        if (o.loops !== false) [-1, 1].forEach(function (k) { var tor = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.022, 8, 16, Math.PI), LOOP); tor.position.set(k * s * 0.28, s, 0); G.add(tor); });
        G.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return G;
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

  /* THE TIDAL FLAT'S OWN FACE: salt pans, algal mat and the meanders of wind tidal channels, laid as albedo on a thin
   * plane just above the ground (polygon offset, never a second ground). `tile` is the metres one texture covers. */
  N.tidalFlat = function (THREE, TXT, R, o) {
    o = o || {};
    var size = o.size || 4000, tile = o.tile || 400, seed = o.seed || N.SEED, px = 1024, vein = o.veins == null ? 0.5 : o.veins, mot = o.mottle == null ? 1 : o.mottle;
    var c = document.createElement("canvas"); c.width = c.height = px; var g = c.getContext("2d"), img = g.createImageData(px, px), d = img.data;
    TX.reseed && TX.reseed(seed);
    for (var y = 0; y < px; y++) for (var x = 0; x < px; x++) {
      var u = x / px * 6, v = y / px * 6;
      var pan = 0.5 + 0.5 * TX.fbm2(u * 1.3 + 7, v * 1.3, 5);                       /* salt pans, pale */
      var mat = 0.5 + 0.5 * TX.fbm2(u * 3.1, v * 3.1 + 11, 4);                     /* algal mat, dark */
      var ch = Math.abs(TX.fbm2(u * 0.9 + 3, v * 0.9 - 5, 4));                      /* channel lines */
      var grit = vein ? 0 : 0.08 * (TX.fbm2(u * 60, v * 60, 2));                     /* fine grit where the veins are dropped */
      var k = 0.6 + mot * (0.85 * Math.max(0, pan - 0.5) - 0.5 * Math.max(0, mat - 0.52)) - (ch < 0.04 ? vein * (1 - ch / 0.04) : 0) + grit;
      var i = (y * px + x) * 4; d[i] = 189 * k; d[i + 1] = 182 * k; d[i + 2] = 164 * k; d[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(size / tile, size / tile); t.anisotropy = 8;
    var m = new THREE.MeshStandardMaterial({ map: t, roughness: 0.95, metalness: 0, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
    m.userData = { txWear: false };
    var pl = new THREE.Mesh(new THREE.PlaneGeometry(size, size), m); pl.rotation.x = -Math.PI / 2; pl.position.set(o.x || 0, o.y == null ? 0.004 : o.y, o.z || 0); pl.receiveShadow = true;
    R.scene.add(pl); return pl;
  };

  /* THE SKY IN FRAME: the flats are open, so an exterior frame calls these after TXT.frame */
  N.flats = function (TXT, R, o) {
    o = o || {};
    TXT.sky(R);
    TXT.ground(R, { surface: o.surface || "dirt", color: o.color == null ? 0x3e352b : o.color, size: o.size || 3000, seed: o.seed || 11 });
    return R;
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
