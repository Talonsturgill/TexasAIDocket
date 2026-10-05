/* deck/2026-10-05-wards.js — the chassis for the 2026-10-05 deck: UT REAL Health AI, the UT
 * System's health care AI laboratory, funded 12 pilot projects out of 120 submissions, and one of
 * them, the no-show project, states what it already saved (tx-2026-0201).
 *
 * THE WORLD. A Texas hospital at blue hour on the humid coast. blueHour, tuned once here: a grey blue
 * Gulf haze, a little more fog for the wet air, clouds off, and the engine's own horizon glow kept
 * (it turns yellow-white as it rises since 2026-10-03, so no. 39's suppression is not needed). The
 * sky is deep blue above the roofline and the type is light on it.
 *
 * DIRECTIONS. +x is east and -z is north, so +z is south. In blueHour the declared light is the
 * LAMP: the lot's LED heads and the porte-cochere soffit, at az -60, el 32. az runs clockwise from
 * +z toward +x, so the key sits at (sin -60, ., cos -60), to the south-west and low. A face looking
 * south (+z) takes it, and casts run to the north-east, away from the camera's right shoulder when
 * the camera looks north at the hospital's front.
 *
 * THE HERO OBJECT. The kit `hospital` at ten floors, the kit's cap, with a BAY SKIN this file lays in
 * the tower's south ribbon glass: 10 floors of 12 bays, one emissive pane per bay, 120 in all, one
 * per submission (figures.json `submissions`, `bays_per_floor`). The stair core stands proud of the
 * middle of the face, so the bays sit six to each side of it. A pane is a lit room card just proud of
 * the tinted glass and behind the mullions, never behind the wall face (no. 36), its roughness varied
 * by seed so no two reflect the same sky (the craft refresh).
 *
 * THE ACCENT. #E0956A, dusk_gold, "a funded pilot". Only ever a gold bay in the skin, or a screen
 * that is a pilot's tool. Never a sky, a lamp, a person or a car. Its albedo sits near the hex and
 * its emissive stays at or under 0.72 (no. 41's ember read pink at 1.05).
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the bay skin
 * and the deck's materials, and hands a frame primitives. Each frame sets up its own renderer,
 * camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("wards.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "wards",
    light: { az: -60, el: 32 },
    sky: { preset: "blueHour", haze: 0x5a6c80, fogDensity: 0.0042, clouds: 0.0 },
    ground: "#16202A",
    material: "#A9A397",
    accent: "#E0956A",
    grade: {
      exposure: 0.0,
      saturation: 1.02,
      contrast: 1.05,
      filmic: true,
      lift: [0.006, 0.008, 0.014],
      gain: [1.0, 1.0, 1.01],
      vignette: 0.2,
      bloom: { threshold: 0.8, strength: 0.18, radius: 14 },
      grain: { amount: 0.012, size: 2, seed: 20261005 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261005;
  N.ACCENT = 0xe0956a;
  N.INK = "#F3F1EC";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---------------------------------------------------------------- materials */
  N.mats = function (K, THREE) {
    if (N._m) return N._m;
    var m = {};
    /* the cool corridor white, six strengths and six glass roughnesses, so a face of 120 rooms
     * reads as rooms rather than as one sheet */
    m.base = [];
    for (var i = 0; i < 6; i++) {
      m.base.push(new THREE.MeshStandardMaterial({
        color: 0x10161b, roughness: 0.05 + i * 0.03, metalness: 0.0,
        emissive: 0xdce6e2, emissiveIntensity: 0.1 + i * 0.035
      }));
    }
    /* a dark bay, the room with its lights off, for the few a frame wants quiet */
    m.dark = new THREE.MeshStandardMaterial({ color: 0x0c1116, roughness: 0.08, metalness: 0.0, emissive: 0x1c2630, emissiveIntensity: 0.4 });
    /* the funded pilot's light */
    m.gold = new THREE.MeshStandardMaterial({ color: N.ACCENT, roughness: 0.12, metalness: 0.0, emissive: N.ACCENT, emissiveIntensity: 0.68 });
    /* a screen that is a pilot's tool, for the interiors */
    m.screen = new THREE.MeshStandardMaterial({ color: 0x2a1a10, roughness: 0.35, metalness: 0.0, emissive: N.ACCENT, emissiveIntensity: 0.62 });
    m.precast = new THREE.MeshStandardMaterial({ color: 0xa9a397, roughness: 0.85, metalness: 0.0 });
    N._m = m;
    return m;
  };

  /* ---------------------------------------------------------------- the hero */
  /* THE KIT HOSPITAL'S OWN NUMBERS, read from kit/civic.js rather than guessed. The podium is 9.6 m
   * on a 0.15 m slab, the tower stands on it at T0 with floors 4.0 m apart, its south ribbon runs
   * x -16.4 to 16.4 at y T0 + 1.0 + 4k and 1.9 m tall, its glass at the face plus 0.02 to 0.06 m and
   * its mullions to 0.16 m proud. The tower is 17 m deep and centred at z -4 before the kit re-centres
   * the footprint, which shifts every child by the same amount, so the shift is read back off the
   * first child rather than assumed. */
  var T0 = 9.75, FH = 4.0, TD = 17, TZ = -4, RIB_Y = 1.0, RIB_H = 1.9, CORE_HALF = 3.25, RIB_HALF = 16.4;
  N.FLOORS = 10;
  N.BAYS = 12;

  N.hospital = function (K, THREE, o) {
    o = o || {};
    var g = K.make("hospital", { floors: N.FLOORS, seed: o.seed || 5 });
    var off = g.children.length ? g.children[0].position.clone() : new THREE.Vector3();
    var M = N.mats(K, THREE);
    /* the kit's red emergency panel is the one red near the frame, and red sits in flag red's
     * window, so it is repainted to the deck's precast with its lamp kept */
    g.traverse(function (c) {
      if (!c.isMesh || !c.material) return;
      var mt = c.material;
      if (mt.color && mt.color.getHex && mt.color.getHex() === 0xb3121b) { c.material = M.precast; }
    });
    g.userData.off = off;
    return g;
  };

  /* bayAt(floor, bay) -> the pane's centre in the hospital's own frame. floor 0 is the lowest tower
   * floor, bay 0 the west-most. Six bays sit west of the stair core and six east of it. */
  N.bayAt = function (g, floor, bay) {
    var off = g.userData.off, side = bay < 6 ? -1 : 1, j = bay < 6 ? bay : bay - 6;
    var span = RIB_HALF - CORE_HALF, w = span / 6;
    var x = side < 0 ? -RIB_HALF + (j + 0.5) * w : CORE_HALF + (j + 0.5) * w;
    var y = T0 + RIB_Y + floor * FH + RIB_H / 2;
    var z = TZ + TD / 2 + 0.075;
    return { x: x + off.x, y: y, z: z + off.z, w: w - 0.18, h: RIB_H - 0.22 };
  };

  /* N.skin(g, state) lays the 120 panes. state(floor, bay) returns 'gold', 'dark' or a number 0..5
   * for a base strength; omitted, every pane is a seeded base. Returns the skin group, already
   * added to the hospital. The pane count is N.FLOORS x N.BAYS and nothing else sets it. */
  N.skin = function (K, THREE, g, state, seed) {
    var M = N.mats(K, THREE), r = lcg(seed || N.SEED), grp = new THREE.Group(), geos = {};
    for (var f = 0; f < N.FLOORS; f++) {
      for (var b = 0; b < N.BAYS; b++) {
        var p = N.bayAt(g, f, b), s = state ? state(f, b) : null, mat;
        var pick = Math.floor(r() * 6);
        if (s === "gold") mat = M.gold;
        else if (s === "dark") mat = M.dark;
        else mat = M.base[typeof s === "number" ? s : pick];
        var key = p.w.toFixed(3) + "x" + p.h.toFixed(3);
        if (!geos[key]) geos[key] = new THREE.PlaneGeometry(p.w, p.h);
        var mesh = new THREE.Mesh(geos[key], mat);
        mesh.position.set(p.x, p.y, p.z);
        mesh.userData.bay = [f, b, s || "base"];
        grp.add(mesh);
      }
    }
    grp.userData.panes = N.FLOORS * N.BAYS;
    g.add(grp);
    return grp;
  };

  /* the deck's gold block: floors 6 and 7 (the seventh and eighth), the six bays west of the core */
  N.goldBlock = function (f, b) { return (f === 6 || f === 7) && b < 6; };

  /* N.lamp stands a kit streetlight, lights its head, and gives it a 4000K pool on the ground. The
   * pool casts no shadow of its own: the deck's one shadow casting key is deckRig, which stands
   * where the lot's lamps are. */
  N.lamp = function (R, K, TXT, x, z, rotY, o) {
    o = o || {};
    var s = K.make("streetlight", { height: o.height || 9.1 });
    s.rotation.y = rotY || 0; s.position.set(x, 0, z);
    s.traverse(function (m) {
      var e = m.isMesh && m.material && m.material.emissive;
      if (e && e.r > 0.85 && e.g > 0.8 && e.b > 0.6 && m.material.emissiveIntensity < 1) {
        m.material = m.material.clone(); m.material.emissiveIntensity = o.lit == null ? 3.0 : o.lit;
      }
    });
    TXT.add(R, s); TXT.contact(R, s);
    if (o.pool !== false) {
      var reach = o.reach || 2.4, hx = x + Math.sin(s.rotation.y) * reach, hz = z + Math.cos(s.rotation.y) * reach;
      var pl = new N.T.PointLight(0xfff0d8, o.pool || 60, o.range || 24, 2);
      pl.position.set(hx, (o.height || 9.1) - 0.4, hz); R.scene.add(pl);
    }
    return s;
  };

  /* ---------------------------------------------------------------- the rig and the stage */
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 60, mapSize: map || 2048 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 120, shadowFar: o.shadowFar || 320, normalBias: o.normalBias == null ? 0.02 : o.normalBias };
  };
  /* THE DECK'S EXPOSURE, ONE NUMBER FOR ALL NINE, so the frames sit in one value band. Tuned on the
   * probe frame. */
  N.EXPOSURE = 1.0;
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    return TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * N.EXPOSURE * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 34, near: o.near || 0.05, far: o.far || 12000 });
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

  /* ---------------------------------------------------------------- the type's quiet */
  /* THE SKY BAND THE TYPE STANDS IN. Light type on a blue sky, so the band is a dark wash that
   * deepens the sky behind the hook and the dek, never over 0.45 alpha. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 60 : o.pad;
    var a = o.a == null ? 0.26 : Math.min(0.45, o.a), c = o.rgb || "8,14,26";
    if (bottom != null && a > 0) {
      var fade = o.fade || 170, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + a + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + (a * 0.9) + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  N.soften = function (cx, selectors, o) {
    o = o || {};
    var blur = o.blur || 10, pad = o.pad == null ? 16 : o.pad, feather = o.feather || 60;
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
   * last. A dark band under the footer, never a box and never over 0.45. */
  N.post = function (cx, o) {
    o = o || {};
    N.atmosphere(cx, { a: o.a, to: o.to, fade: o.fade, rgb: o.rgb, pad: o.pad });
    N.soften(cx, o.type || [".kick", ".hook", ".dek"], { blur: o.typeBlur || 7, pad: 8, feather: o.typeFeather || 24 });
    N.soften(cx, [".tx-site", ".src", ".count"], { blur: o.siteBlur || 14, pad: 16, feather: 60 });
    var y0 = N.H - (o.veilH || 240), v = cx.createLinearGradient(0, y0, 0, N.H), rgb = o.veilRgb || "8,12,20";
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(" + rgb + "," + (Math.min(0.45, o.veil == null ? 0.4 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 1.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };

  /* ---------------------------------------------------------------- the shell */
  /* THE SHELL EVERY FRAME SHARES: the type styles, the furniture, the fit of the hook. Light type on
   * a blue hour sky, with a dark halo rather than a plate. */
  N.CSS = function () {
    var ink = N.INK, dek = "#E6E3DC", halo = "rgba(6,10,18,0.6)", halo2 = "rgba(6,10,18,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#16202A; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:1.0; letter-spacing:-0.01em; color:' + ink + '; font-variation-settings:"opsz" 144; z-index:10; }',
      ".dek { position:absolute; left:82px; width:840px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:25px; font-weight:500; letter-spacing:0.06em; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".hook, .dek, .tx-site, .kick, .src, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) {
      d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px";
    });
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#E6E3DC" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 92, max: 128, maxLines: 2 });
    N.follow();
  };
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE;
    await document.fonts.ready;
    N.start(o);
    var TXT = typeof bench === "function" ? bench(THREE) : bench, K = initKit(THREE, TXT);
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
  };

  global.WD = N;
})(this);
