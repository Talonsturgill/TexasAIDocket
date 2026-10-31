/* deck/2026-10-31-roadpaint.js — the chassis for the 2026-10-31 deck: League City's November 3rd vote on its police
 * department's fixed Flock plate reader cameras, and the council's own record behind it (tx-2026-0048).
 *
 * THE VISUAL ARGUMENT. Road paint. Proposition A defines the cameras by where they stand, "fixed locations on public
 * roadways", so every count in the record is laid in the material of a public road: white thermoplastic marking a few
 * millimetres proud of Gulf Coast asphalt. One stripe, one crosswalk bar, one raised marker or one cut groove is one
 * counted thing, read from figures.json in each frame's own code. Worn paint is old and fresh paint is new. The deck
 * never shows a camera.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky, one warm seam low in the west, the paint in
 * a pool of light and the road beyond it gone dark.
 *
 * THE LIGHT is azimuth -64, elevation 14. +x is east and +z is south. A camera looking north (-z) has the key on its
 * LEFT, every lit edge of paint is on the left, and every cast runs long to the right. TXBENCH reliefs read the same
 * declaration: raked from the upper left, casting to the lower right. Fourteen degrees is the rake a relief needs to
 * keep its casts.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `thermo_bar` (a thermoplastic marking bar, 4 mm proud,
 * chamfered, fresh or worn), `continental_crosswalk` (n bars at one pitch), `curb_ramp_warning` (a terracotta detectable
 * warning panel of truncated domes), `raised_marker` (a ceramic raised pavement marker with two prismatic faces) and
 * `gutter_rule` (a concrete gutter pan cut with a saw cut ruler, with inlaid bars). All drawn to illustrate, to no
 * maker's design, in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the
 * lift.
 *
 * THE ACCENT is dusk_ember, #B4664F, and it means ONE thing: the public. The terracotta at the kerb where the public stands,
 * the voter's own jacket, the start of the hours a no would set running, and League City and its two counties on the map.
 * The material is held redder than the token because the warm key shifts it toward yellow in the render.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated. Every
 * frame composes its own picture, and every count a frame draws is read from figures.json in that frame's own code. The
 * chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("roadpaint.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "roadpaint",
    light: { az: -64, el: 14 },
    sky: "lastLight",
    ground: "#09080C",
    material: "#E6E1D6",
    accent: "#B4664F",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.12, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261031 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261031;
  N.ACCENT = 0xb4664f;   /* dusk_ember, brand.yaml's token, and it means ONE thing: the terracotta at the kerb */
  N.INK = "#ECE8DF";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */
  function noiseTex(THREE, seed, lo, hi, n, sz) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "rgb(128,128,128)"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < n; i++) { var v = Math.floor(lo + r() * (hi - lo)); x.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; x.fillRect(r() * 256, r() * 256, sz, sz); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  /* PAINT ALBEDO: bead white with the asphalt's aggregate showing through in pits; worn paint shows far more of it */
  function paintTex(THREE, seed, base, pits, pitA) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = base; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < pits; i++) { var a = pitA * (0.4 + 0.6 * r()); x.fillStyle = "rgba(24,24,26," + a + ")"; var s = 0.8 + r() * 2.6; x.fillRect(r() * 256, r() * 256, s, s * (0.6 + r())); }
    for (var k = 0; k < 900; k++) { x.fillStyle = "rgba(255,255,250," + (0.15 + r() * 0.3) + ")"; x.fillRect(r() * 256, r() * 256, 0.8, 0.8); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  N.mats = function (THREE, K) {
    if (N._M) return N._M;
    var beads = noiseTex(THREE, 7, 100, 170, 12000, 1.2);
    var tooth = noiseTex(THREE, 11, 104, 156, 9000, 1.6);
    var fresh = paintTex(THREE, 3, "#e9e5dc", 700, 0.55), worn = paintTex(THREE, 5, "#a9a69f", 5200, 0.85);
    fresh.repeat.set(2, 2); worn.repeat.set(2, 2);
    N._M = {
      /* thermoplastic: matte with a fine bead glint, a clearcoat standing in for the glass beads' retroreflection */
      fresh: new THREE.MeshPhysicalMaterial({ map: fresh, roughness: 0.55, clearcoat: 0.12, clearcoatRoughness: 0.5, bumpMap: beads, bumpScale: 0.5, emissive: 0x3d3b36, emissiveIntensity: 0.45 }),
      worn: new THREE.MeshStandardMaterial({ map: worn, roughness: 0.78, bumpMap: tooth, bumpScale: 0.6 }),
      /* the deck's one accent: terracotta polymer, matte, held near #B4664F in the render */
      terracotta: new THREE.MeshStandardMaterial({ color: 0xc8424c, roughness: 0.62, bumpMap: tooth, bumpScale: 0.3, emissive: 0x6a1a1e, emissiveIntensity: 0.7 }),
      terracottaPaint: new THREE.MeshPhysicalMaterial({ color: 0xc8424c, roughness: 0.5, clearcoat: 0.2, clearcoatRoughness: 0.4, bumpMap: beads, bumpScale: 0.4, emissive: 0x7a2024, emissiveIntensity: 0.8 }),
      concrete: new THREE.MeshStandardMaterial({ color: 0x8a8984, roughness: 0.9, bumpMap: tooth, bumpScale: 0.7 }),
      cut: new THREE.MeshStandardMaterial({ color: 0x1a1918, roughness: 0.95 }),
      ceramic: new THREE.MeshPhysicalMaterial({ color: 0xe8e6e0, roughness: 0.32, clearcoat: 0.6, clearcoatRoughness: 0.2 }),
      prismWhite: new THREE.MeshPhysicalMaterial({ color: 0xf2f4f6, roughness: 0.08, metalness: 0.2, clearcoat: 1, clearcoatRoughness: 0.05, emissive: 0x2a2c30, emissiveIntensity: 0.4 }),
      prismAmber: new THREE.MeshPhysicalMaterial({ color: 0xffa21e, roughness: 0.08, metalness: 0.1, clearcoat: 1, clearcoatRoughness: 0.05, emissive: 0x6a3200, emissiveIntensity: 0.55 }),
      amberBody: new THREE.MeshPhysicalMaterial({ color: 0xe0921e, roughness: 0.3, clearcoat: 0.6, clearcoatRoughness: 0.2 }),
      asphaltSlab: new THREE.MeshStandardMaterial({ color: 0x1d1d20, roughness: 0.92, bumpMap: tooth, bumpScale: 0.9 }),
      kerb: new THREE.MeshStandardMaterial({ color: 0x77766f, roughness: 0.9, bumpMap: tooth, bumpScale: 0.7 })
    };
    return N._M;
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.thermo_bar) return;
    var M = N.mats(THREE, K);
    function shade(o) { o.traverse(function (c) { if (c.isMesh) { c.castShadow = c.receiveShadow = true; } }); return o; }
    var PAINT_T = 0.007;
    N.PAINT_T = PAINT_T;

    /* ONE THERMOPLASTIC BAR: w across x, l along z, 4 mm proud, its long edges chamfered so the key draws a lit line down
     * the lit edge and the far edge casts. wear 'fresh' | 'worn' | 'terracotta'. Drawn to illustrate. */
    K.define("thermo_bar", {
      size: [0.6, PAINT_T, 3.0],
      options: { w: 0.6, l: 3.0, t: PAINT_T, wear: "fresh" },
      note: "A thermoplastic road marking bar w x l, t thick (default 7 mm, a heavy profile marking), chamfered. wear fresh|worn|terracotta.",
      make: function (o) {
        var mat = o.wear === "worn" ? M.worn : o.wear === "terracotta" ? M.terracottaPaint : M.fresh;
        var t = o.t || PAINT_T, c = Math.min(t * 0.5, 0.003);
        var sh = new THREE.Shape(); sh.moveTo(-o.w / 2, 0); sh.lineTo(o.w / 2, 0); sh.lineTo(o.w / 2 - c, t); sh.lineTo(-o.w / 2 + c, t); sh.lineTo(-o.w / 2, 0);
        var geo = new THREE.ExtrudeGeometry(sh, { depth: o.l, bevelEnabled: false });
        geo.translate(0, 0, -o.l / 2); K.uvBox(geo, 0.5);
        var m = new THREE.Mesh(geo, mat); var g = new THREE.Group(); g.add(m); return shade(g);
      }
    });
    /* A CONTINENTAL CROSSWALK: n bars across x at one pitch, each bar l along z. `bare` lists bar indices drawn as a
     * saw cut outline with no paint, `wear` sets the finish of every painted bar. userData.bars holds each bar's centre. */
    K.define("continental_crosswalk", {
      size: [8.4, PAINT_T, 3.0],
      options: { n: 8, w: 0.6, gap: 0.6, l: 3.0, wear: "fresh", bare: [] },
      note: "n thermoplastic bars at one pitch across x, each l long on z. wear fresh|worn, bare (indices drawn as an unpainted saw cut outline).",
      make: function (o) {
        var g = new THREE.Group(), pitch = o.w + o.gap, x0 = -(o.n - 1) * pitch / 2, bars = [];
        for (var i = 0; i < o.n; i++) {
          var x = x0 + i * pitch; bars.push([x, 0]);
          if ((o.bare || []).indexOf(i) >= 0) {
            /* the saw cut: a 20 mm kerf round the bar's footprint, its two walls standing as thin raised lips of torn asphalt so the key lights one wall and shadows the other */
            [[x - o.w / 2, 0.02, o.l + 0.02], [x + o.w / 2, 0.02, o.l + 0.02]].forEach(function (s) { var m = new THREE.Mesh(new THREE.BoxGeometry(s[1], 0.003, s[2]), M.cut); m.position.set(s[0], 0.0008, 0); g.add(m); [-1, 1].forEach(function (sd) { var lip = new THREE.Mesh(new THREE.BoxGeometry(0.008, 0.005, s[2]), M.worn); lip.position.set(s[0] + sd * 0.014, 0.0025, 0); g.add(lip); }); });
            [-o.l / 2, o.l / 2].forEach(function (z) { var m = new THREE.Mesh(new THREE.BoxGeometry(o.w, 0.003, 0.02), M.cut); m.position.set(x, 0.0008, z); g.add(m); [-1, 1].forEach(function (sd) { var lip = new THREE.Mesh(new THREE.BoxGeometry(o.w, 0.005, 0.008), M.worn); lip.position.set(x, 0.0025, z + sd * 0.014); g.add(lip); }); });
            continue;
          }
          var b = K.make("thermo_bar", { w: o.w, l: o.l, wear: o.wear }); b.position.set(x, 0, 0); g.add(b);
        }
        g.userData.bars = bars; return shade(g);
      }
    });
    /* A DETECTABLE WARNING PANEL: a terracotta polymer panel w x d, 6 mm thick, cast with truncated domes 5 mm tall on a
     * 60 mm pitch, set flush at a kerb ramp. The deck's one accent. Drawn to illustrate. */
    K.define("curb_ramp_warning", {
      size: [1.22, 0.011, 0.61],
      options: { w: 1.22, d: 0.61, pitch: 0.06 },
      note: "A terracotta detectable warning panel of truncated domes, w x d (m), dome pitch.",
      make: function (o) {
        var g = new THREE.Group();
        var base = TXT.roundedBox(o.w, 0.006, o.d, 0.002, M.terracotta); base.position.y = 0.003; g.add(base);
        var dome = new THREE.CylinderGeometry(0.0115, 0.0175, 0.005, 20), list = [];
        var nx = Math.floor(o.w / o.pitch), nz = Math.floor(o.d / o.pitch);
        for (var i = 0; i < nx; i++) for (var j = 0; j < nz; j++) list.push([(i - (nx - 1) / 2) * o.pitch, 0.0085, (j - (nz - 1) / 2) * o.pitch, 0, 1]);
        K.instances(dome, M.terracotta, list, g);
        return shade(g);
      }
    });
    /* A RAISED PAVEMENT MARKER: a ceramic or polymer wedge 100 x 100 mm, 18 mm tall, its two faces sloped 30 degrees and
     * carrying a prismatic reflector that catches a low key as a bright tile. color white | amber. */
    K.define("raised_marker", {
      size: [0.1, 0.018, 0.1],
      options: { color: "white" },
      note: "A raised pavement marker 0.10 x 0.018 x 0.10 m with two prismatic faces. color white|amber.",
      make: function (o) {
        var g = new THREE.Group(), body = o.color === "amber" ? M.amberBody : M.ceramic, prism = o.color === "amber" ? M.prismAmber : M.prismWhite;
        var s = 0.05, h = 0.018, top = 0.022;
        var sh = new THREE.Shape(); sh.moveTo(-s, 0); sh.lineTo(-top, h); sh.lineTo(top, h); sh.lineTo(s, 0); sh.lineTo(-s, 0);
        var geo = new THREE.ExtrudeGeometry(sh, { depth: 0.1, bevelEnabled: true, bevelThickness: 0.002, bevelSize: 0.002, bevelSegments: 2 });
        geo.translate(0, 0, -0.05); var m = new THREE.Mesh(geo, body); g.add(m);
        var a = Math.atan2(h, s - top), L = Math.hypot(h, s - top) * 0.82;
        [-1, 1].forEach(function (sd) {
          var p = new THREE.Mesh(new THREE.BoxGeometry(L, 0.0016, 0.07), prism);
          p.position.set(sd * (s + top) / 2, h / 2 + 0.0012, 0); p.rotation.z = sd * a; g.add(p);
        });
        return shade(g);
      }
    });
    /* A GUTTER RULE: a salt grey concrete gutter pan len long (x) and d deep (z), cut with a saw cut tick at every unit
     * and a longer cut every 5, and thermoplastic bars inlaid against it from one origin at `unit` metres per count.
     * bars is a list of counts, laid one above another on z. userData.origin, userData.unit, userData.ends hold where
     * every bar ends, in the model's own frame, so a frame can land a leader on it. */
    K.define("gutter_rule", {
      size: [6, 0.12, 0.9],
      options: { len: 6, d: 0.9, unit: 0.07, bars: [], ticks: 0, barW: 0.12 },
      note: "A concrete gutter pan len x d with a saw cut tick ruler and inlaid thermoplastic bars. unit (m per count), bars (counts), ticks (how many unit ticks), barW.",
      make: function (o) {
        var g = new THREE.Group(), x0 = -o.len / 2 + 0.25, ends = [];
        var pan = TXT.roundedBox(o.len, 0.12, o.d, 0.012, M.concrete); K.uvBox(pan.geometry, 0.6); pan.position.y = 0.06; g.add(pan);
        var nt = o.ticks || 0, zt = o.d / 2 - 0.09;
        for (var k = 0; k <= nt; k++) {
          var major = k % 5 === 0, tl = major ? 0.13 : 0.06;
          var cut = new THREE.Mesh(new THREE.BoxGeometry(0.006, 0.004, tl), M.cut); cut.position.set(x0 + k * o.unit, 0.1195, zt - tl / 2 + 0.03); g.add(cut);
        }
        (o.bars || []).forEach(function (n, i) {
          var L = n * o.unit, z = -o.d / 2 + 0.16 + i * (o.barW + 0.14);
          var b = K.make("thermo_bar", { w: o.barW, l: L, t: 0.005, wear: "fresh" }); b.rotation.y = Math.PI / 2; b.position.set(x0 + L / 2, 0.12, z); g.add(b);
          ends.push([x0 + L, 0.125, z]);
        });
        var stop = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.006, o.d - 0.12), M.cut); stop.position.set(x0, 0.12, 0); g.add(stop);
        g.userData.origin = [x0, 0.12, 0]; g.userData.unit = o.unit; g.userData.ends = ends;
        return shade(g);
      }
    });
  };
  N.glowTex = function (THREE) {
    if (N._glow) return N._glow;
    var c = document.createElement("canvas"); c.width = c.height = 64; var g = c.getContext("2d");
    var gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.18, "rgba(255,255,255,0.6)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); N._glow = new THREE.CanvasTexture(c); return N._glow;
  };
  N.noShadows = function (R) { R.scene.traverse(function (o) { if (o.userData && o.userData.noShadow) { o.castShadow = false; o.receiveShadow = false; } }); };
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
  /* THE KEY is the last light, low and warm, and the world's cool rim is held low so a shadow side
   * of weathering steel stays warm dark rather than the navy of the sky */
  N.rigSpec = function (W, size, map) {
    var rim = Object.assign({}, W.rig.rim, { i: (W.rig.rim.i || 0.8) * 0.45 });
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
  N.shadeLow = function (cx, o) {
    o = o || {};
    var top = o.from, a = Math.min(0.5, o.a == null ? 0.35 : o.a), fade = o.fade || 200;
    var g = cx.createLinearGradient(0, top - fade, 0, N.H);
    g.addColorStop(0, "rgba(6,5,10,0)"); g.addColorStop(fade / (N.H - top + fade), "rgba(6,5,10," + a + ")"); g.addColorStop(1, "rgba(6,5,10," + a + ")");
    cx.fillStyle = g; cx.fillRect(0, top - fade, N.W, N.H - top + fade);
  };
  N.unacne = function (R, nb) { R.scene.traverse(function (l) { if (l.isDirectionalLight && l.castShadow) { l.shadow.normalBias = nb == null ? 0.04 : nb; l.shadow.bias = -0.0004; } }); return R; };
  /* THE SKY'S OWN LIGHT, held down: the navy dome lights every shadow face blue through the image
   * based light, so a frame calls this after TXT.sky to keep shadows warm dark */
  N.warm = function (R, k) {
    R.scene.environmentIntensity = k == null ? 0.3 : k;
    /* THE GROUND'S BOUNCE. The key's pool on caliche throws warm light back up into every shadow face;
     * without it no. 57's stringers and pier sides crushed to L* 0 and read as cut-outs */
    if (!R._bounce) { R._bounce = new N.T.HemisphereLight(0x161a24, 0x4a4743, N.BOUNCE); R.scene.add(R._bounce); }
    return R;
  };
  N.BOUNCE = 0.6;
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
  /* A RESERVE under one line of type: a feathered dark patch, darken only */
  N.knock = function (cx, els, a) {
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
    u.setAttribute("stroke", "#07070C"); u.setAttribute("stroke-width", "5"); u.setAttribute("stroke-opacity", "0.6"); svg.appendChild(u);
    var l = document.createElementNS("http://www.w3.org/2000/svg", "line");
    l.setAttribute("x1", from[0]); l.setAttribute("y1", from[1]); l.setAttribute("x2", to[0]); l.setAttribute("y2", to[1]);
    l.setAttribute("stroke", N.INK); l.setAttribute("stroke-width", "2"); l.setAttribute("stroke-opacity", "0.85"); svg.appendChild(l);
    var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", to[0]); c.setAttribute("cy", to[1]); c.setAttribute("r", "5"); c.setAttribute("fill", N.INK); svg.appendChild(c);
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#D6D0C4", halo = "rgba(4,3,8,0.6)", halo2 = "rgba(4,3,8,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#07070C; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      "/* Manrope and Fraunces contextual alternates curl a straight apostrophe after some letters (no. 61, no. 62), so calt is off on every line of type */",
      ".hook, .dek, .lab, .kick, .count, .src { font-feature-settings:\"calt\" 0; }",
      ".hook, .dek, .kick, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }",
      /* the footer lines carry a tight halo only: a 14 px blur read as a smudge on a lit ground */
      ".tx-site, .src { text-shadow:0 0 2px " + halo + ", 0 1px 4px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D6D0C4" });
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
    return document.getElementById("art").getContext("2d");
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
  /* a DOM label pinned to a world point, nudged by (dx, dy) */
  N.pin = function (THREE, R, id, p, dx, dy) {
    var q = N.project(THREE, R, p), el = document.getElementById(id);
    if (!el) return q;
    el.style.left = Math.round(q[0] + (dx || 0)) + "px"; el.style.top = Math.round(q[1] + (dy || 0)) + "px";
    return q;
  };




  global.CH = N;
})(this);
