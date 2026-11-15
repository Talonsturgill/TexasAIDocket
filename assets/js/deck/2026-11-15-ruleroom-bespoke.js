/* deck/2026-11-15-ruleroom-bespoke.js, the SPINE for carousel no. 78 (BESPOKE run, knowledge/carousel/BESPOKE.md): Texas
 * 2036's November 10th, 2026 preview of its report on AI in Texas schools (tx-2026-0248). Texas school and district leaders
 * reported AI in classrooms far more often than they reported a written policy for it, and the group counts Texas outside the
 * states with statewide AI guidance for schools.
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the PEOPLE tone, bespoke:true, the tone's grade and the accent. Each frame
 * picks its own world (TXT.sky(R, world)), turns its own key (TXT.deckRig(..., { light })) and places its own type, seated with
 * CH.seat. It mounts the type faces and the furniture (CH.start), and hands a frame the helpers below. There is no drawFrame.
 *
 * THE ACCENT. The people tone's amber #ff9f1c means ONE thing: a WRITTEN RULE, a district policy or statewide guidance. A
 * frame lights in amber only the policies, binders, stamps or guidance a claim counts, and nothing else on any frame.
 *
 * THE MODELS. The kit holds the rooms and people (student_desk, student_desk_rows, classroom_window, school, school_bus,
 * laptop, desk, hearing_dais, podium, public_seating, person). The chassis builds the written rules the kit lacks, in the
 * kit's conventions so Phase 17 can queue the lift: ring_binder, pocket_folder, policy_sheet, cubby_wall and shelf_run.
 * Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("ruleroom.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "ruleroom", look: "v2", tone: "people", bespoke: true,
    light: { az: -40, el: 26 },
    sky: { preset: "v2people" },
    ground: "#ff9f62",
    material: "#ffdcb0",
    accent: "#ff9f1c",
    grade: TXLOOK.grade("people")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261115; N.TONE = "people"; N.P = TXLOOK.palette("people"); N.INK = N.P.ink;
  N.ACCENT = 0xff9f1c;        /* the people tone's amber: a WRITTEN RULE (a district policy or state guidance), and nothing else */
  N.GOLD = N.ACCENT;

  /* a seeded canvas texture, so every surface carries tooth in its albedo and never in its height */
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };


  /* LOOK V2: the studio sweep in place of the dark lab. A frame calls TXT.studio(R, CH.studioOpts({ w, d })) where it called
   * TXT.interior(R, CH.roomOpts({ w, d })), same footprint arguments. */
  /* THE WRITTEN RULES, built here because the kit lacks them. A frame calls nothing: CH.boot installs them. */
  N.AMBER = 0xff9f1c;   /* the accent as a material colour: a written rule */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.ring_binder) return;
    var amberM = function () { return K.mat('rr_amber', { color: N.AMBER, roughness: 0.42, metalness: 0, clearcoat: 0.6, clearcoatRoughness: 0.3 }, true); };
    var paperM = function (c) { return K.mat('rr_paper' + (c || ''), { color: c || 0xfbf6ec, roughness: 0.9, metalness: 0, sheen: 0.6, sheenRoughness: 0.6, sheenColor: 0xf0e2c8 }, true); };
    var vinylM = function (c) { return K.mat('rr_vinyl' + c, { color: c, roughness: 0.48, metalness: 0, clearcoat: 0.35, clearcoatRoughness: 0.4 }, true); };
    var steelM = function () { return K.mat('rr_ring', { color: 0xd9dde2, metalness: 1, roughness: 0.18 }); };
    var oakM = function () { return K.mat('rr_oak', { color: 0xffffff, roughness: 0.62, map: K.tex('wood', { color: '#c9935e' }) }); };

    /* A 3 RING BINDER standing on its bottom edge, spine toward +z: two vinyl over board covers with rounded corners,
     * a rounded spine, a clear spine pocket (blank), a steel D ring mechanism. open (degrees) swings the front cover
     * about the spine; leaves is how many sheets ride the rings. amber paints the cover in the accent: a written rule. */
    K.define("ring_binder", { size: [0.06, 0.30, 0.29], options: { open: 0, leaves: 0, amber: false, color: 0x5a6fd0, pocket: true },
      note: "A 1.5 in 3 ring binder, 0.29 x 0.30 m covers, spine on +z, standing on its bottom edge. open swings the front cover (degrees), leaves rides that many blank sheets on the rings, amber paints it in the deck's accent (a written rule only).",
      make: function (o) {
        var g = new THREE.Group(), W = 0.06, H = 0.30, D = 0.29, t = 0.004, M = o.amber ? amberM() : vinylM(o.color);
        K.box(t, H, D, M, -W / 2 + t / 2, 0, -0.0, 0.0015, g);                       /* back cover */
        var spine = TXT.roundedBox(W, H, 0.006, 0.0028, M); spine.position.set(0, H / 2, D / 2 - 0.003); g.add(spine);
        if (o.pocket) { var pk = new THREE.Mesh(new THREE.PlaneGeometry(W * 0.72, H * 0.78), K.finish.glass(0xdfe8f0)); pk.position.set(0, H / 2, D / 2 + 0.0006); g.add(pk);
          var card = new THREE.Mesh(new THREE.PlaneGeometry(W * 0.62, H * 0.7), paperM()); card.position.set(0, H / 2, D / 2 + 0.0003); g.add(card); }
        var hinge = new THREE.Group(); hinge.position.set(W / 2 - t / 2, 0, D / 2 - 0.006); g.add(hinge);
        var front = K.box(t, H, D - 0.006, M, 0, 0, -(D - 0.006) / 2, 0.0015, hinge); hinge.rotation.y = -(o.open || 0) * Math.PI / 180;
        /* the D rings on a plated base strip, on the back cover's inner face */
        var base = K.box(0.004, 0.27, 0.03, steelM(), -W / 2 + t + 0.002, 0.015, D / 2 - 0.03, 0.001, g);
        [0.06, 0.15, 0.24].forEach(function (y) { var r = new THREE.Mesh(new THREE.TorusGeometry(0.018, 0.0016, 8, 28, Math.PI * 1.25), steelM());
          r.rotation.y = Math.PI / 2; r.position.set(-W / 2 + t + 0.004, y, D / 2 - 0.032); g.add(r); });
        for (var i = 0; i < (o.leaves || 0); i++) K.box(0.0002, 0.279, 0.215, paperM(), -W / 2 + t + 0.006 + i * 0.0006, 0.01, D / 2 - 0.13, 0, g);
        return g;
      } });

    /* A POCKET FOLDER lying flat, slightly curled at the free edge. amber marks a written policy. */
    K.define("pocket_folder", { size: [0.24, 0.012, 0.31], options: { amber: true, color: 0x6b7fd8, sheets: 3 },
      note: "A letter pocket folder lying flat on a desk, 0.24 x 0.31 m, front on +z, with sheets inside and a soft curl at the open edge. amber marks a written policy (the accent).",
      make: function (o) {
        var g = new THREE.Group(), M = o.amber ? amberM() : vinylM(o.color);
        var geo = new THREE.BoxGeometry(0.24, 0.0012, 0.31, 12, 1, 1), pos = geo.attributes.position;
        for (var i = 0; i < pos.count; i++) { var x = pos.getX(i); pos.setY(i, pos.getY(i) + Math.pow(Math.max(0, x / 0.12), 3) * 0.006); }
        geo.computeVertexNormals();
        var back = new THREE.Mesh(geo, M); back.position.y = 0.0006; g.add(back);
        for (var k = 0; k < (o.sheets || 0); k++) K.box(0.214, 0.0002, 0.278, paperM(), -0.004 + k * 0.002, 0.0013 + k * 0.0003, -0.006 - k * 0.002, 0, g);
        var front = new THREE.Mesh(geo, M); front.position.set(0.002, 0.0042, 0.0); front.scale.set(0.98, 1, 0.985); g.add(front);
        var pocket = K.box(0.226, 0.0014, 0.11, M, 0.004, 0.005, 0.09, 0.0006, g);
        return g;
      } });

    /* ONE SHEET standing or lying: a letter page. amber gives it the accent edge band (a written policy). */
    K.define("policy_sheet", { size: [0.216, 0.0003, 0.279], options: { amber: true, curl: 0.004 },
      note: "A letter sheet lying flat (front +z) with a soft curl; amber puts the accent on its whole face, a written policy only.",
      make: function (o) {
        var g = new THREE.Group(), geo = new THREE.PlaneGeometry(0.216, 0.279, 6, 8); geo.rotateX(-Math.PI / 2);
        var pos = geo.attributes.position; for (var i = 0; i < pos.count; i++) { var z = pos.getZ(i); pos.setY(i, Math.pow(Math.abs(z) / 0.14, 2) * (o.curl || 0)); }
        geo.computeVertexNormals();
        var m = new THREE.Mesh(geo, o.amber ? amberM() : paperM()); m.material.side = THREE.DoubleSide; m.position.y = 0.0004; g.add(m);
        return g;
      } });

    /* A STAFF MAILBOX WALL: cols x rows open cubbies in oak with label rails, on a plinth. userData.cell(c, r) gives a
     * cubby's centre (world, base of the cubby) so a frame can place a sheet in it. */
    K.define("cubby_wall", { size: [3.1, 1.32, 0.32], options: { cols: 10, rows: 10, cell: [0.3, 0.11, 0.3], plinth: 0.1 },
      note: "A school staff mailbox wall of cols x rows open oak cubbies (0.30 x 0.11 x 0.30 m each) with label rails, front +z. userData.cell(c, r) is a cubby floor's centre; userData.count is cols x rows.",
      make: function (o) {
        var g = new THREE.Group(), c = o.cols, r = o.rows, cw = o.cell[0], ch = o.cell[1], cd = o.cell[2], t = 0.012, P = o.plinth;
        var W = c * cw + t, H = r * ch + t, oak = oakM();
        K.box(W + 0.04, P, cd + 0.03, K.finish.steelPaint(0x6a4e8a), 0, 0, 0, 0.004, g);
        K.box(W, H, t, oak, 0, P, -cd / 2 + t / 2, 0, g);
        for (var i = 0; i <= c; i++) K.box(t, H, cd, oak, -W / 2 + t / 2 + i * cw, P, 0, 0.002, g);
        for (var j = 0; j <= r; j++) K.box(W, t, cd, oak, 0, P + j * ch, 0, 0.002, g);
        var rail = K.mat('rr_rail', { color: 0xc8b08a, metalness: 0.6, roughness: 0.35 });
        for (var jj = 0; jj < r; jj++) K.box(W - 0.01, 0.012, 0.004, rail, 0, P + jj * ch + t, cd / 2 + 0.002, 0, g);
        g.userData.count = c * r;
        g.userData.cell = function (ci, ri) { return [-W / 2 + t / 2 + (ci + 0.5) * cw, P + ri * ch + t, 0]; };
        return g;
      } });

    /* A LIBRARY SHELF RUN: an oak plank shelf `length` long on steel standards with a back panel, binder slots at
     * `pitch`. userData.slot(i) is the centre of slot i on the shelf top, counted from +x end. */
    K.define("shelf_run", { size: [3.2, 0.42, 0.34], options: { length: 3.2, pitch: 0.066, depth: 0.32, back: true },
      note: "An oak library shelf `length` m long, 0.32 m deep, top at 0.4 m, on steel standards with a back panel, front +z. userData.slot(i) is slot i's centre on the shelf top from the +x end at `pitch` m; userData.slots is how many fit.",
      make: function (o) {
        var g = new THREE.Group(), L = o.length, D = o.depth, top = 0.4, oak = oakM();
        K.box(L, 0.028, D, oak, 0, top - 0.028, 0, 0.005, g);
        if (o.back) K.box(L, 0.42, 0.012, oak, 0, top - 0.028, -D / 2 + 0.006, 0.002, g);
        var st = K.finish.steelPaint(0x3c3a52); for (var x = -L / 2 + 0.06; x <= L / 2 - 0.05; x += Math.min(0.9, L - 0.12)) K.box(0.03, top - 0.028, 0.03, st, x, 0, -D / 2 + 0.04, 0.004, g);
        g.userData.slots = Math.floor((L - 0.04) / o.pitch);
        g.userData.slot = function (i) { return [L / 2 - 0.02 - (i + 0.5) * o.pitch, top, 0.0]; };
        return g;
      } });
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
