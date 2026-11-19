/* deck/2026-11-18-landbench-bespoke.js, the SPINE for the November 18th, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * a UT Dallas team paired satellite readings of eight air pollutants with CDC cancer prevalence across all 254 Texas counties
 * and used machine learning, and says the result is an association between places, never a diagnosis of a person
 * (tx-2026-0251).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the EXPLAINER tone, bespoke:true, the tone's grade and the accent. Each
 * frame picks its own world (TXT.sky(R, world)), turns its own key (TXT.deckRig(..., { light })) and places its own type,
 * seated with CH.seat. It mounts the type faces and the furniture (CH.start), and hands a frame the helpers below. There is
 * no drawFrame.
 *
 * THE ACCENT. Dusk gold #E0956A (brand.yaml) means ONE thing: WHAT THE SATELLITE READ, the air as measured. The air sheet
 * over the state, the swath, the column of air, the air blocks over three grounds, the edge of one reading, the block to
 * check first. Never the ground monitor, never the model's fit, never cancer, never decoration.
 *
 * EAST IS ALWAYS FRAME RIGHT on every frame with geography.
 *
 * THE MODELS. The kit holds the land, the trees, the houses, the vehicles and the people (pine, mesquite, live_oak,
 * hill_country_terrain, mesa, lath_stake, chain_link_fence, pickup, person, ranch_house). The chassis builds the two things
 * the kit lacks, in the kit's conventions (metres, y up, origin on the ground or the body centre, front on +z) so Phase 17
 * can queue the lift: survey_satellite (illustrative, silver and graphite foil, never gold, no logo, no flag, no agency
 * mark) and air_monitor_shelter (a fibreglass shelter on a pad with an inlet mast and a met mast). Every count a frame draws
 * is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("landbench.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "landbench", look: "v2", tone: "explainer", bespoke: true,
    light: { az: -45, el: 34 },
    sky: { preset: "v2explainer" },
    ground: "#e4d8c3",
    material: "#ede6d6",
    accent: "#e0956a",
    grade: TXLOOK.grade("explainer")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261118; N.TONE = "explainer"; N.P = TXLOOK.palette("explainer"); N.INK = N.P.ink;
  N.ACCENT = 0xe0956a;        /* dusk gold: what the satellite read, and nothing else */
  N.GOLD = N.ACCENT;
  /* a seeded canvas texture, so every surface carries tooth in its albedo and never in its height */
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };


  /* THE TWO MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.survey_satellite) return;
    /* silver and graphite foil with a crinkle in its albedo and roughness, never gold, so it never borrows the accent */
    var foilTex = function (base, seed) {
      return N.canvasTex(THREE, 512, 512, function (c, w, h) {
        var r = N.rng(seed); c.fillStyle = base; c.fillRect(0, 0, w, h);
        for (var i = 0; i < 1400; i++) { var x = r() * w, y = r() * h, s = 6 + r() * 34, a = r() * Math.PI;
          c.save(); c.translate(x, y); c.rotate(a); c.fillStyle = "rgba(" + (r() < 0.5 ? "255,255,255," : "20,24,40,") + (0.05 + r() * 0.12).toFixed(3) + ")";
          c.beginPath(); c.moveTo(-s, 0); c.lineTo(0, -s * 0.35); c.lineTo(s * 0.8, s * 0.1); c.lineTo(0, s * 0.4); c.closePath(); c.fill(); c.restore(); }
      });
    };
    var silverM = function () { return K.mat('lb_foil_silver', { color: 0xdfe3ea, metalness: 0.95, roughness: 0.28, map: foilTex("#cfd5de", 3), roughnessMap: foilTex("#8a8a8a", 5) }, true); };
    var graphM = function () { return K.mat('lb_foil_graphite', { color: 0x4a4f5c, metalness: 0.85, roughness: 0.38, map: foilTex("#5a6070", 7) }, true); };
    var frameM = function () { return K.mat('lb_frame', { color: 0xb8bec8, metalness: 1, roughness: 0.3 }); };
    var blackM = function () { return K.mat('lb_black', { color: 0x15171f, metalness: 0.2, roughness: 0.6 }); };
    var cellTex = N.canvasTex(THREE, 512, 256, function (c, w, h) {
      c.fillStyle = "#16245a"; c.fillRect(0, 0, w, h);
      for (var y = 0; y < h; y += 32) for (var x = 0; x < w; x += 32) {
        var g = c.createLinearGradient(x, y, x + 30, y + 30); g.addColorStop(0, "#2c4aa8"); g.addColorStop(1, "#1a2d74");
        c.fillStyle = g; c.fillRect(x + 1.5, y + 1.5, 29, 29); c.fillStyle = "rgba(200,215,255,0.18)"; c.fillRect(x + 1.5, y + 15, 29, 0.8); }
    });
    var cellM = function () { return K.mat('lb_cells', { color: 0xffffff, metalness: 0.55, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05, map: cellTex }, true); };
    K.define('survey_satellite', {
      size: [9.4, 2.4],
      options: { wing: 7, yaw: 0.35 },
      note: 'Illustrative earth observation satellite drawn to no agency design. Origin at the bus centre, nadir on -y, the wing along +x. Bus 2.0 x 2.1 x 3.0 m in silver foil with graphite foil panels, a 0.9 x 0.7 x 1.1 m nadir instrument with a 0.4 m baffled aperture, a star tracker pair, a 0.5 m antenna dish, a yoke and one cell wing. No logo, flag or mark. Never gold. Options wing (solar wing span in metres) and yaw (wing tilt in radians).',
      make: function (o) {
        o = o || {}; var g = new THREE.Group(), span = o.wing || 7;
        var bus = TXT.roundedBox ? TXT.roundedBox(2.0, 2.1, 3.0, 0.06, silverM()) : new THREE.Mesh(new THREE.BoxGeometry(2.0, 2.1, 3.0), silverM());
        g.add(bus);
        [[1.005, 0, 0, 0, Math.PI / 2], [-1.005, 0, 0, 0, -Math.PI / 2]].forEach(function (p) { var pn = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 1.5), graphM()); pn.position.set(p[0], p[1], p[2]); pn.rotation.y = p[4]; g.add(pn); });
        for (var s = -1; s <= 1; s += 2) for (var t = -1; t <= 1; t += 2) { var e = K.box(0.04, 2.14, 0.04, frameM(), 1.0 * s, (0) - (2.14) / 2, 1.5 * t, 0, g); }
        var inst = TXT.roundedBox ? TXT.roundedBox(0.9, 1.1, 0.7, 0.05, graphM()) : new THREE.Mesh(new THREE.BoxGeometry(0.9, 1.1, 0.7), graphM());
        inst.position.set(0, -1.6, 0.4); g.add(inst);
        var baffle = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.26, 0.5, 40, 1, true), blackM()); baffle.material.side = THREE.DoubleSide; baffle.position.set(0, -2.3, 0.4); g.add(baffle);
        var lip = new THREE.Mesh(new THREE.TorusGeometry(0.26, 0.025, 10, 40), frameM()); lip.rotation.x = Math.PI / 2; lip.position.set(0, -2.55, 0.4); g.add(lip);
        [-0.35, 0.35].forEach(function (x) { var st = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.32, 24), blackM()); st.position.set(x, 1.2, -1.1); st.rotation.x = -0.5; g.add(st);
          var hood = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.12, 0.2, 24, 1, true), frameM()); hood.material.side = THREE.DoubleSide; hood.position.set(x, 1.36, -1.2); hood.rotation.x = -0.5; g.add(hood); });
        var dish = new THREE.Mesh(new THREE.SphereGeometry(0.28, 32, 12, 0, Math.PI * 2, 0, 0.9), frameM()); dish.material.side = THREE.DoubleSide; dish.rotation.x = Math.PI; dish.position.set(-0.55, -1.25, -1.1); g.add(dish);
        K.cyl(0.02, 0.02, 0.35, frameM(), -0.55, (-1.2) - (0.35) / 2, -1.1, 8, g);
        var yoke = K.cyl(0.05, 0.05, 1.2, frameM(), 1.6, (0) - (1.2) / 2, 0, 16, g); yoke.rotation.z = Math.PI / 2;
        var wing = new THREE.Group(); wing.position.set(2.2, 0, 0); wing.rotation.x = o.yaw || 0.35; g.add(wing);
        var np = 3, pw = span / np;
        for (var k = 0; k < np; k++) { var p = new THREE.Mesh(new THREE.BoxGeometry(pw - 0.06, 0.035, 2.0), cellM()); p.userData.txBevel = false; p.position.set(pw * k + pw / 2, 0, 0); wing.add(p); var rail = new THREE.Mesh(new THREE.BoxGeometry(pw - 0.02, 0.05, 0.05), frameM()); rail.position.set(pw * k + pw / 2, 0, 1.02); wing.add(rail); var rail2 = rail.clone(); rail2.position.z = -1.02; wing.add(rail2); }
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; if (m.geometry && m.geometry.parameters && m.geometry.parameters.depth !== undefined) { var q = m.geometry.parameters; if (Math.min(q.width, q.height, q.depth) < 0.3) m.userData.txBevel = false; } } });
        return g;
      }
    });
    var glassFibreM = function () { return K.mat('lb_fibreglass', { color: 0xf2f1ec, roughness: 0.55, metalness: 0, clearcoat: 0.25, clearcoatRoughness: 0.5 }); };
    var galvM = function () { return K.mat('lb_galv', { color: 0xb9bec4, metalness: 0.9, roughness: 0.42 }); };
    var concM = function () { return K.mat('lb_pad', { color: 0xcfc8bb, roughness: 0.92 }); };
    var hvacM = function () { return K.mat('lb_hvac', { color: 0xd8dad6, metalness: 0.3, roughness: 0.5 }); };
    K.define('air_monitor_shelter', {
      size: [4.0, 10.4],
      options: { mast: 10 },
      note: 'An air quality monitoring shelter on its pad. Origin on the ground at the pad centre, front (door) on +z. A 3.0 x 2.4 x 2.6 m insulated fibreglass shelter with rounded edges on a 4.0 x 3.5 x 0.15 m concrete pad, a door with kick plate and step on +z, a wall HVAC unit on -x, a 2 m stainless sample inlet mast with rain cap on the roof, and a galvanized met mast with cup anemometer and vane at the +x corner. Fence it with the kit chain_link_fence. Option mast (met mast height in metres).',
      make: function (o) {
        o = o || {}; var g = new THREE.Group(), mh = o.mast || 10;
        K.box(4.0, 0.15, 3.5, concM(), 0, (0.075) - (0.15) / 2, 0, 0, g);
        var body = TXT.roundedBox ? TXT.roundedBox(3.0, 2.4, 2.6, 0.12, glassFibreM()) : new THREE.Mesh(new THREE.BoxGeometry(3.0, 2.4, 2.6), glassFibreM());
        body.position.set(0, 0.15 + 1.2, 0); g.add(body);
        K.box(3.1, 0.06, 2.7, galvM(), 0, (2.6) - (0.06) / 2, 0, 0, g);
        K.box(0.9, 1.95, 0.04, hvacM(), 0.6, (1.15) - (1.95) / 2, 1.31, 0, g);
        K.box(0.9, 0.25, 0.045, galvM(), 0.6, (0.3) - (0.25) / 2, 1.33, 0, g);
        K.box(0.05, 0.05, 0.06, galvM(), 0.98, (1.15) - (0.05) / 2, 1.35, 0, g);
        K.box(1.0, 0.18, 0.4, concM(), 0.6, (0.09) - (0.18) / 2, 1.95, 0, g);
        K.box(0.2, 0.6, 0.8, hvacM(), -1.62, (1.6) - (0.6) / 2, 0, 0, g);
        for (var v = 0; v < 6; v++) K.box(0.01, 0.5, 0.02, galvM(), -1.73, (1.6) - (0.5) / 2, -0.3 + v * 0.12, 0, g);
        var inlet = K.cyl(0.03, 0.03, 2.0, galvM(), -0.6, (2.6 + 1.0) - (2.0) / 2, -0.4, 16, g);
        var cap = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.06, 0.12, 24), galvM()); cap.position.set(-0.6, 3.65, -0.4); g.add(cap);
        K.cyl(0.03, 0.03, 0.8, galvM(), 0.4, (2.6 + 0.4) - (0.8) / 2, -0.6, 12, g);
        var mx = 1.8, mz = -1.4; K.cyl(0.04, 0.05, mh, galvM(), mx, (mh / 2) - (mh) / 2, mz, 12, g);
        var arm = K.box(1.0, 0.03, 0.03, galvM(), mx + 0.5, (mh - 0.3) - (0.03) / 2, mz, 0, g);
        for (var c = 0; c < 3; c++) { var a = c * Math.PI * 2 / 3; var cup = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 8, 0, Math.PI), galvM()); cup.position.set(mx + 1.0 + Math.cos(a) * 0.12, mh - 0.1, mz + Math.sin(a) * 0.12); cup.rotation.y = -a; g.add(cup); }
        K.cyl(0.01, 0.01, 0.25, galvM(), mx + 1.0, (mh - 0.2) - (0.25) / 2, mz, 8, g);
        K.box(0.35, 0.12, 0.01, galvM(), mx, (mh + 0.15) - (0.12) / 2, mz, 0, g);
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; if (m.geometry && m.geometry.parameters && m.geometry.parameters.depth !== undefined) { var q = m.geometry.parameters; if (Math.min(q.width, q.height, q.depth) < 0.3) m.userData.txBevel = false; } } });
        return g;
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
