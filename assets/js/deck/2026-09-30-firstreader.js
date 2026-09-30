/* deck/2026-09-30-firstreader.js — the chassis for the 2026-09-30 deck: the Texas Education
 * Agency's hybrid scoring of written STAAR answers, where an automated scoring engine reads every
 * English language written answer first and at least a quarter go on to two people
 * (tx-2026-0194).
 *
 * THE WORLD. A Texas ISD campus on a grey September morning. overcast, tuned toward a cool,
 * luminous lid and never toward cream: the zenith a blue grey, the horizon nearly white, the haze
 * a cool grey so a school wing 90 m out softens without going brown. The world table's line for
 * overcast is procedure, a filing, a waiting room, and this story is a procedure with no villain
 * and no verdict. Soft light also keeps a count countable, because a hard sun doubles every desk
 * with its shadow. The key never moves.
 *
 * DIRECTIONS. +x is east, -z is north. The light is declared at az -40 (south west of the zenith
 * track, clockwise from +z toward +x) and el 48, inside overcast's 35 to 60. The school wing stands
 * north of the practice field with its front, its walkway and its flagpole facing south (+z). A
 * camera looking north looks at the school with the key over its left shoulder, so the desks' south
 * faces take the light and the shadows fall softly north east.
 *
 * THE HERO OBJECT. One student combo chair desk, the kit model this file adds (student_desk): a
 * putty laminate top on a black bent tube frame joined to a charcoal seat shell, a wire book rack
 * under the seat, four glides. The student sits facing north (-z), so the seat is at +z and the top
 * at -z, and the kit laptop stands on the top with its screen facing the seat. Every Texan has sat
 * at one, and the deck uses it as one child's written answer. It is DRAWN at the size these desks
 * are and no frame prints a dimension of it. FR.field lays out any count of desks as instanced
 * geometry, so 27,200 can stand on one frame.
 *
 * THE ACCENT. bluebonnet #4E5FA8, a person reading an answer. It is only ever the shirt of a
 * reader or of the parent, and never a desk, a screen, the school or the sky.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the kit
 * addition and the deck's materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("firstreader.js needs txdeck.js loaded first");

  /* ONE DECLARATION. az -40, el 48 inside overcast's 35 to 60. */
  TXDECK.declare({
    world: "firstreader",
    light: { az: -40, el: 48 },
    sky: { preset: "overcast", zenith: 0x8d98a6, horizon: 0xe3e6e6, haze: 0xd2d6d8, fogDensity: 0.0032, envIntensity: 1.05, exposure: 1.02 },
    ground: "#D7D9DA",
    material: "#4A4D52",
    accent: "#4E5FA8",
    grade: {
      exposure: 0.0,
      saturation: 1.04,
      contrast: 1.07,
      filmic: true,
      lift: [0.004, 0.006, 0.01],
      gain: [0.99, 1.0, 1.01],
      vignette: 0.16,
      bloom: { threshold: 0.9, strength: 0.12, radius: 10 },
      grain: { amount: 0.011, size: 2, seed: 20260930 },
      aberration: 0,
      dither: true,
      sharpen: 0.18
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20260930;
  N.ACCENT = 0x4e5fa8;
  N.STRAW = 0x9d9a62;          /* late September bermuda on a practice field, half gone to straw */
  N.TOP = 0xc4ab88;            /* the putty oak laminate */
  N.SHELL = 0x464a50;          /* the charcoal seat shell almost every district buys */
  N.TUBE = 0x25282c;
  N.SCREEN = 0xdfe6ee;

  /* THE CAMPUS, one layout for every exterior frame so a camera anywhere sees the same place. The
   * school wing's centre is 92 m north of the desk of frames 1, 7 and 9, which stands at the
   * origin. The practice field runs south of the school. None of this is a real campus. */
  N.CAMPUS = { school: [6, 0, -92], oaks: [[-58, 0, -70, 2], [-44, 0, -84, 3], [70, 0, -76, 5], [84, 0, -60, 6], [52, 0, -95, 7]] };

  N.installKit = function (K, THREE, TXT) {
    if (K.registry.student_desk) return;

    function mats() {
      return {
        top: K.mat('sd-top', { color: N.TOP, roughness: 0.5, metalness: 0.0 }),
        edge: K.mat('sd-edge', { color: 0x1d1f22, roughness: 0.55 }),
        tube: K.mat('sd-tube', { color: N.TUBE, roughness: 0.38, metalness: 0.6 }),
        shell: K.mat('sd-shell', { color: N.SHELL, roughness: 0.62, metalness: 0.0 }),
        wire: K.mat('sd-wire', { color: 0x2e3135, roughness: 0.45, metalness: 0.65 }),
        glide: K.mat('sd-glide', { color: 0x9a9a92, roughness: 0.7 })
      };
    }

    /* THE STUDENT COMBO DESK. Metres, y up, origin at the footprint centre on the ground, the
     * seat on +z and the top on -z, the student facing -z. userData.laptopAt is where a laptop's
     * base centre sits on the top, and userData.seatAt the seat's centre. */
    K.define('student_desk', {
      size: [0.62, 0.86, 0.9],
      options: { hand: 'right', worn: 0.3 },
      note: 'Student combo chair desk: a putty laminate top (0.61 x 0.46 m at 0.74 m) with a dark T-mould edge, a bent black tube frame joining it to a charcoal moulded seat shell (seat at 0.44 m, back to 0.86 m), a wire book rack under the seat and four glides. The student faces -z. userData.laptopAt, .seatAt.',
      make: function (o, r) {
        var M = mats(), g = new THREE.Group(), s = o.hand === 'left' ? -1 : 1;
        /* the top, with its T-mould edge standing proud so the edge catches the lid of cloud */
        var top = TXT.roundedBox(0.6, 0.022, 0.45, 0.008, M.top); top.position.set(0.04 * s, 0.745, -0.2); g.add(top);
        var edge = TXT.roundedBox(0.615, 0.03, 0.465, 0.01, M.edge); edge.position.set(0.04 * s, 0.738, -0.2); g.add(edge);
        /* the seat shell: a pan with a lip, and a curved back on +z */
        var seat = TXT.roundedBox(0.4, 0.035, 0.38, 0.03, M.shell); seat.position.set(0, 0.44, 0.2); seat.rotation.x = -0.06; g.add(seat);
        var lip = TXT.roundedBox(0.4, 0.05, 0.03, 0.012, M.shell); lip.position.set(0, 0.45, 0.02); g.add(lip);
        /* the back: a moulded shell panel in three slightly turned segments so it reads as curved */
        var backP = TXT.roundedBox(0.4, 0.23, 0.028, 0.02, M.shell); backP.position.set(0, 0.73, 0.42); backP.rotation.x = 0.12; g.add(backP);
        K.bar([-0.12, 0.47, 0.37], [-0.14, 0.6, 0.41], 0.012, M.tube, 8, g);
        K.bar([0.12, 0.47, 0.37], [0.14, 0.6, 0.41], 0.012, M.tube, 8, g);
        /* the frame: two runners on the ground-side, four legs, the spine to the top on the writing side */
        var R = 0.011;
        [-0.19, 0.19].forEach(function (x) {
          K.bar([x, 0.03, 0.36], [x, 0.03, -0.38], R, M.tube, 8, g);       /* runner */
          K.bar([x, 0.03, 0.34], [x, 0.43, 0.3], R, M.tube, 8, g);         /* rear leg */
          K.bar([x, 0.03, 0.06], [x, 0.43, 0.08], R, M.tube, 8, g);        /* seat front leg */
          K.bar([x * 0.2, 0.43, 0.3], [x, 0.43, 0.3], R * 0.9, M.tube, 8, g);
        });
        K.bar([-0.19, 0.43, 0.08], [0.19, 0.43, 0.08], R * 0.9, M.tube, 8, g);
        K.bar([-0.19 * s, 0.03, -0.36], [-0.17 * s, 0.725, -0.34], R, M.tube, 8, g);   /* front post under the top */
        K.bar([0.19 * s, 0.03, -0.36], [0.2 * s, 0.725, -0.34], R, M.tube, 8, g);
        K.bar([0.19 * s, 0.43, 0.1], [0.2 * s, 0.725, -0.02], R * 1.2, M.tube, 8, g);  /* the spine on the writing side */
        K.bar([-0.17 * s, 0.725, -0.34], [0.2 * s, 0.725, -0.34], R * 0.9, M.tube, 8, g);
        K.bar([0.2 * s, 0.725, -0.34], [0.2 * s, 0.725, -0.02], R * 0.9, M.tube, 8, g);
        /* the book rack: a wire tray under the seat */
        for (var i = 0; i < 7; i++) K.bar([-0.17, 0.16, 0.06 + i * 0.045], [0.17, 0.16, 0.06 + i * 0.045], 0.003, M.wire, 5, g);
        [-0.17, 0.17].forEach(function (x) { K.bar([x, 0.16, 0.06], [x, 0.16, 0.33], 0.004, M.wire, 5, g); K.bar([x, 0.16, 0.06], [x, 0.03, 0.06], 0.004, M.wire, 5, g); });
        /* glides */
        [[-0.19, 0.35], [0.19, 0.35], [-0.19, -0.37], [0.19, -0.37]].forEach(function (p) { K.cyl(0.018, 0.02, 0.018, M.glide, p[0], 0, p[1], 10, g); });
        g.userData.laptopAt = [0.04 * s, 0.756, -0.2];
        g.userData.seatAt = [0, 0.46, 0.2];
        return g;
      }
    });
  };

  /* THE HERO, made the same way on every frame, with the kit laptop on its top. */
  N.desk = function (K, o) {
    o = o || {};
    var d = K.make('student_desk', { seed: o.seed || 7, hand: o.hand || 'right' });
    if (o.laptop !== false) {
      var lp = K.make('laptop', { open: o.open == null ? 108 : o.open, finish: 'space', screen: o.screen || 'doc' });
      var a = d.userData.laptopAt; lp.position.set(a[0], a[1], a[2] + 0.02); d.add(lp);
      d.userData.laptop = lp;
    }
    return d;
  };

  /* A READER, the bluebonnet shirt that means a person is reading an answer. */
  N.reader = function (K, o) {
    o = o || {};
    return K.make('person', { seed: o.seed || 3, role: o.role || 'resident', pose: o.pose || 'stand', shirt: o.accent === false ? (o.shirt || 0x8a8f96) : N.ACCENT, trousers: o.trousers || 0x2b2d33, hat: 'none', vest: false, detail: o.detail || 'full' });
  };

  /* LOW DETAIL DESKS AS INSTANCED GEOMETRY, one mesh per material, so a count in the tens of
   * thousands can stand on one frame. Each unit is the desk's silhouette at the same size: the top,
   * the seat and back, two leg pairs and a lit laptop lid. */
  N.lodParts = function (THREE, TXT) {
    function merged(boxes) {
      var geos = boxes.map(function (b) {
        var gg = new THREE.BoxGeometry(b[0], b[1], b[2]); gg.translate(b[3], b[4], b[5]);
        if (b[6]) { var m = new THREE.Matrix4().makeRotationX(b[6]); gg.applyMatrix4(m); }
        return gg.index ? gg.toNonIndexed() : gg;
      });
      var total = 0; geos.forEach(function (gg) { total += gg.attributes.position.count; });
      var pos = new Float32Array(total * 3), nor = new Float32Array(total * 3), o = 0;
      geos.forEach(function (gg) { pos.set(gg.attributes.position.array, o * 3); nor.set(gg.attributes.normal.array, o * 3); o += gg.attributes.position.count; });
      var out = new THREE.BufferGeometry();
      out.setAttribute('position', new THREE.BufferAttribute(pos, 3)); out.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
      return out;
    }
    return {
      top: merged([[0.6, 0.03, 0.45, 0.04, 0.74, -0.2]]),
      shell: merged([[0.4, 0.04, 0.38, 0, 0.44, 0.2], [0.4, 0.26, 0.03, 0, 0.71, 0.41]]),
      tube: merged([[0.024, 0.44, 0.024, -0.19, 0.22, 0.3], [0.024, 0.44, 0.024, 0.19, 0.22, 0.3], [0.024, 0.74, 0.024, -0.17, 0.37, -0.36], [0.024, 0.74, 0.024, 0.2, 0.37, -0.36], [0.024, 0.024, 0.74, -0.19, 0.03, 0], [0.024, 0.024, 0.74, 0.19, 0.03, 0]]),
      base: merged([[0.31, 0.014, 0.22, 0.04, 0.763, -0.18]]),
      lid: merged([[0.31, 0.21, 0.008, 0.04, 0.865, -0.29]])
    };
  };

  /* A FIELD OF DESKS. cols x rows at pitch [px, pz] from origin [x0, z0] (the near left desk),
   * rows running north (-z). count is exact: the last row is filled left to right until count is
   * reached. near(x, z) returning true puts a full detail desk there instead of an instance. Returns
   * { group, units:[[x,z]], drawn, detailed }. drawn is the number of desks placed, which a frame
   * asserts equals the figure it was given. */
  N.field = function (K, THREE, TXT, o) {
    o = o || {};
    var count = o.count | 0, cols = o.cols | 0, px = o.pitch ? o.pitch[0] : 1.2, pz = o.pitch ? o.pitch[1] : 1.2;
    if (!count || !cols) throw new Error('FR.field needs count and cols from the frame');
    var x0 = o.origin ? o.origin[0] : 0, z0 = o.origin ? o.origin[1] : 0;
    var g = new THREE.Group(), units = [], lists = { far: [] }, detailed = 0;
    for (var i = 0; i < count; i++) {
      var c = i % cols, rw = Math.floor(i / cols), x = x0 + c * px, z = z0 - rw * pz;
      units.push([x, z]);
      if (o.near && o.near(x, z, i)) {
        var d = N.desk(K, { seed: 11 + (i % 17), open: o.open, screen: o.screen }); d.position.set(x, 0, z); d.rotation.y = o.rotY || 0; g.add(d); detailed++;
      } else lists.far.push([x, 0, z, o.rotY || 0, 1]);
    }
    if (lists.far.length) {
      var P = N.lodParts(THREE, TXT);
      var mt = K.mat('sd-top-lod', { color: N.TOP, roughness: 0.55 }), ms = K.mat('sd-shell-lod', { color: N.SHELL, roughness: 0.65 }),
          mtu = K.mat('sd-tube-lod', { color: N.TUBE, roughness: 0.45, metalness: 0.5 }), mb = K.mat('sd-lap-lod', { color: 0x3b3e43, roughness: 0.55, metalness: 0.3 }),
          ml = K.mat('sd-lid-lod', { color: 0x3b3e43, roughness: 0.5, emissive: o.lidGlow ? N.SCREEN : 0x000000, emissiveIntensity: o.lidGlow ? 0.35 : 0 });
      [[P.top, mt], [P.shell, ms], [P.tube, mtu], [P.base, mb], [P.lid, ml]].forEach(function (pm) {
        var im = K.instances(pm[0], pm[1], lists.far, g); im.castShadow = o.castShadow !== false; im.receiveShadow = true;
      });
    }
    g.userData.units = units; g.userData.drawn = units.length; g.userData.detailed = detailed;
    return g;
  };

  /* THE CAMPUS AROUND A FRAME: the school wing, the oaks and the fence line, placed the same way
   * on every exterior frame. The frame lays its own TXT.ground first so the ground is in its own
   * source. */
  N.campus = function (K, THREE, TXT, R, o) {
    o = o || {};
    var S = N.CAMPUS, out = {};
    if (o.school !== false) {
      var sc = K.make('school', { length: 57, brick: '#c49460', seed: 4 }); sc.position.set(S.school[0], 0, S.school[2]); TXT.add(R, sc); TXT.contact(R, sc); out.school = sc;
    }
    if (o.oaks !== false) S.oaks.forEach(function (p) { var t = K.make('live_oak', { seed: p[3] }); t.position.set(p[0], 0, p[2]); TXT.add(R, t); TXT.contact(R, t); });
    if (o.fence) { var f = K.make('chain_link_fence', { length: o.fence.length || 60, height: 1.83 }); f.position.set(o.fence.at[0], 0, o.fence.at[2]); f.rotation.y = o.fence.rotY || 0; TXT.add(R, f); out.fence = f; }
    return out;
  };

  /* THE PRACTICE FIELD's grass, kept off rectangles a frame names. Call AFTER TXT.frame. */
  N.grass = function (TXT, R, o) {
    o = o || {};
    TXT.scatter(R, { kind: 'grass', count: o.count || 9000, area: o.area || [-30, -40, 30, 8], avoid: o.avoid || [], seed: o.seed || 17, scale: o.scale || [0.1, 0.2],
                     colors: [0x8e8a52, 0x9f9a5e, 0xa99f66, 0x7e8150] });
  };


  /* A HIGH SCHOOL FOOTBALL FIELD's markings on a plane: the field of play 91.44 m by 48.77 m (the
   * rule book's 100 yards by 160 feet) with end zones, a yard line every 4.572 m and hash marks,
   * painted white on a turf texture. No numerals are painted, so no number on the frame is typed.
   * centre [x, z], length along z. Returns the mesh and the field's corners. */
  N.footballField = function (THREE, TXT, R, o) {
    o = o || {};
    var L = 91.44, Wd = 48.77, EZ = 9.144, cx0 = o.center ? o.center[0] : 0, cz0 = o.center ? o.center[1] : 0;
    var PXM = 16, cw = Math.round((Wd + 8) * PXM), ch = Math.round((L + 2 * EZ + 8) * PXM);
    var c = document.createElement('canvas'); c.width = cw; c.height = ch; var x = c.getContext('2d');
    var rng = TX.rng(o.seed || 41);
    x.fillStyle = '#7f8a4c'; x.fillRect(0, 0, cw, ch);
    for (var i = 0; i < 26000; i++) { x.fillStyle = 'rgba(' + (90 + rng() * 60 | 0) + ',' + (100 + rng() * 50 | 0) + ',' + (50 + rng() * 30 | 0) + ',0.35)'; x.fillRect(rng() * cw, rng() * ch, 2, 2); }
    /* mowing stripes every five yards */
    for (var k = 0; k < 24; k++) { if (k % 2) continue; x.fillStyle = 'rgba(255,255,255,0.05)'; x.fillRect(0, (4 + k * 4.572) * PXM, cw, 4.572 * PXM); }
    x.fillStyle = 'rgba(244,244,236,0.92)';
    var ox = 4 * PXM, oz = 4 * PXM, lw = 0.1 * PXM;
    x.fillRect(ox, oz, Wd * PXM, lw * 1.2); x.fillRect(ox, oz + (L + 2 * EZ) * PXM - lw, Wd * PXM, lw * 1.2);
    x.fillRect(ox, oz, lw * 1.2, (L + 2 * EZ) * PXM); x.fillRect(ox + Wd * PXM - lw, oz, lw * 1.2, (L + 2 * EZ) * PXM);
    for (var yl = 0; yl <= 20; yl++) {
      var zz = oz + (EZ + yl * 4.572) * PXM; x.fillRect(ox, zz, Wd * PXM, lw);
      if (yl < 20) for (var h = 1; h < 5; h++) { var zh = zz + h * 0.9144 * PXM; x.fillRect(ox + 0.3 * PXM, zh, 0.6 * PXM, lw); x.fillRect(ox + (Wd - 0.9) * PXM, zh, 0.6 * PXM, lw); x.fillRect(ox + (Wd / 2 - 2.8) * PXM, zh, 0.6 * PXM, lw); x.fillRect(ox + (Wd / 2 + 2.2) * PXM, zh, 0.6 * PXM, lw); }
    }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    var m = new THREE.Mesh(new THREE.PlaneGeometry(Wd + 8, L + 2 * EZ + 8), new THREE.MeshStandardMaterial({ map: t, roughness: 0.95 }));
    m.rotation.x = -Math.PI / 2; m.position.set(cx0, 0.012, cz0); m.receiveShadow = true; R.scene.add(m);
    return { mesh: m, L: L, W: Wd, EZ: EZ, south: cz0 + L / 2, north: cz0 - L / 2, west: cx0 - Wd / 2, east: cx0 + Wd / 2 };
  };

  /* A HIGH SCHOOL GOAL POST, the single gooseneck kind: a padded post behind the end line, an arm
   * to a crossbar 3.05 m up, two uprights 5.64 m apart. Metres, origin at the post's foot. */
  N.goalPost = function (K, THREE, TXT) {
    var g = new THREE.Group(), y = K.mat('gp-yellow', { color: 0xd8b62a, roughness: 0.45, metalness: 0.35 }), pad = K.mat('gp-pad', { color: 0x23324f, roughness: 0.8 });
    K.cyl(0.11, 0.11, 3.05, y, 0, 0, 0, 16, g);
    K.cyl(0.2, 0.2, 1.8, pad, 0, 0, 0, 16, g);
    K.bar([0, 3.05, 0], [0, 3.05, -1.8], 0.09, y, 12, g);
    K.bar([-2.82, 3.05, -1.8], [2.82, 3.05, -1.8], 0.075, y, 12, g);
    [-2.82, 2.82].forEach(function (xx) { K.bar([xx, 3.05, -1.8], [xx, 9.1, -1.8], 0.055, y, 12, g); });
    return g;
  };

  /* A SCHOOL TRACK's straightaway: eight lanes of 1.22 m in rubber red brown with white lines,
   * running along -z from a start line at z0 for len metres. band [from, to] paints a band across
   * all lanes between those distances, in metres from the start. Returns the lane width total. */
  N.track = function (THREE, TXT, R, o) {
    o = o || {};
    var lanes = 8, lw = 1.22, Wd = lanes * lw, len = o.len || 100, x0 = o.x0 || 0, z0 = o.z0 || 0, over = o.over || 30;
    var PXM = 24, cw = Math.round(Wd * PXM), ch = Math.round((len + over) * PXM);
    var c = document.createElement('canvas'); c.width = cw; c.height = ch; var x = c.getContext('2d'), rng = TX.rng(o.seed || 43);
    x.fillStyle = '#8a4a3a'; x.fillRect(0, 0, cw, ch);
    for (var i = 0; i < 30000; i++) { x.fillStyle = 'rgba(' + (110 + rng() * 50 | 0) + ',' + (55 + rng() * 30 | 0) + ',' + (45 + rng() * 25 | 0) + ',0.4)'; x.fillRect(rng() * cw, rng() * ch, 2, 2); }
    x.fillStyle = 'rgba(240,238,230,0.95)';
    for (var l = 0; l <= lanes; l++) x.fillRect(Math.min(cw - 3, l * lw * PXM), 0, 0.05 * PXM, ch);
    var zs = function (d) { return ch - (over / 2 + d) * PXM; };
    x.fillRect(0, zs(0) - 0.05 * PXM, cw, 0.05 * PXM);
    x.fillRect(0, zs(len), cw, 0.05 * PXM);
    if (o.band) { x.fillStyle = o.bandColor || 'rgba(236,232,218,0.97)'; x.fillRect(0, zs(o.band[1]), cw, (o.band[1] - o.band[0]) * PXM); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    var m = new THREE.Mesh(new THREE.PlaneGeometry(Wd, len + over), new THREE.MeshStandardMaterial({ map: t, roughness: 0.9 }));
    m.rotation.x = -Math.PI / 2; m.position.set(x0 + Wd / 2, 0.015, z0 - len / 2); m.receiveShadow = true; R.scene.add(m);
    /* the kerb on the infield side */
    var kerb = TXT.roundedBox(0.08, 0.06, len + over, 0.01, new THREE.MeshStandardMaterial({ color: 0xd9d8d2, roughness: 0.6 }));
    kerb.position.set(x0 - 0.04, 0.03, z0 - len / 2); R.scene.add(kerb);
    return { width: Wd, lanes: lanes };
  };

  /* LIGHT TOWARD THE TYPE. On this deck the type is dark on a pale lid, so the wash LIFTS the
   * value under the type rather than darkening it: a full-width vertical wash, never a box and never
   * over 0.45 alpha, so deck_chassis reads it as atmosphere and not as a plate. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector('.dek'), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    var a = o.a == null ? 0.3 : Math.min(0.45, o.a);
    if (bottom != null && a > 0) {
      var fade = o.fade || 160, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, 'rgba(236,238,238,' + (a * 0.7) + ')');
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), 'rgba(236,238,238,' + a + ')');
      g.addColorStop(1, 'rgba(236,238,238,0)');
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };

  /* KNOCK THE EDGE OUT BEHIND A LINE OF TYPE, without removing its light. */
  N.soften = function (cx, selectors, o) {
    o = o || {};
    var blur = o.blur || 12, pad = o.pad == null ? 18 : o.pad, feather = o.feather || 70;
    var art = document.getElementById('art');
    var src = document.createElement('canvas'); src.width = art.width; src.height = art.height;
    var sx = src.getContext('2d'); sx.filter = 'blur(' + (blur * 2) + 'px)'; sx.drawImage(art, 0, 0);
    var mask = document.createElement('canvas'); mask.width = art.width; mask.height = art.height;
    var mx = mask.getContext('2d'); mx.filter = 'blur(' + feather + 'px)'; mx.fillStyle = '#000';
    (selectors || []).forEach(function (sel) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
        var r = el.getBoundingClientRect();
        mx.fillRect((r.left - pad) * 2, (r.top - pad) * 2, (r.width + 2 * pad) * 2, (r.height + 2 * pad) * 2);
      });
    });
    sx.filter = 'none'; sx.globalCompositeOperation = 'destination-in'; sx.drawImage(mask, 0, 0);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.drawImage(src, 0, 0); cx.restore();
  };


  /* THE POST STEPS every frame takes before its grade, in one place: light toward the type, then
   * knock the art's edges out behind the type and, harder, behind the footer lines. The frame still
   * calls TXDECK.finish itself, last. */
  N.post = function (cx, o) {
    o = o || {};
    N.atmosphere(cx, { a: o.a == null ? 0.22 : o.a });
    N.soften(cx, o.type || ['.kick', '.count', '.hook', '.dek']);
    N.soften(cx, ['.tx-site', '.src'], { blur: 24, pad: 26, feather: 60 });
  };

  /* A world point to frame CSS px, through the frame's own camera. */
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

  global.FR = N;
})(this);
