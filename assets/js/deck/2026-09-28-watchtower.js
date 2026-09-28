/* deck/2026-09-28-watchtower.js — the chassis for the 2026-09-28 deck: the AI smoke cameras that
 * Southwestern Public Service, the Xcel Energy utility for most of the Texas Panhandle, runs with
 * Pano AI, the PUCT order that told it to report the number of AI camera fire detections, and the
 * first annual report that answered that line with a count of cameras (tx-2026-0192, tx-2026-0191).
 *
 * THE WORLD. A Panhandle red flag afternoon under a dry front. stormFront, tuned once so the haze
 * is a neutral dust grey rather than rain blue or peach: a bruised deck of cloud to the north and
 * one low shaft of sun from the west-southwest raking across cured straw grass. The world table's
 * line for stormFront is risk, a warning, a deadline. The key never moves: every cast runs to the
 * right and slightly toward the lens, and every lit face is on the left.
 *
 * THE HERO OBJECT. One wildfire camera station, the kit model this file adds
 * (wildfire_camera_station): a tapered galvanized monopole on a concrete pier, a crossarm with two
 * pan and tilt camera heads in white sunshielded housings, an equipment enclosure, a panel antenna
 * and a lightning rod. Its part option 'head' makes one loose head on its turntable, which is how
 * the deck counts cameras. It is DRAWN. It stands for the kind of site the utility's own plan
 * describes and is no one's station.
 *
 * THE ACCENT. comal #2A7A9E, the state's question. It marks the line the state asked to be filled
 * and nothing else: a rule beside a line on a page, flagging on a bare rail, the spine tab of a
 * filed plan. It never touches a camera, a pole, the grass or the sky, and it is cool so it can
 * never read as flame.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the kit
 * additions and the deck's materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("watchtower.js needs txdeck.js loaded first");

  /* ONE DECLARATION. The key is the low sun under the cloud deck at az -68 (clockwise from +Z
   * toward +X, so west of south as a frame looks toward -z), el 10, inside stormFront's 6 to 16.
   * A camera looking north (toward -z) has the sun on its left rear: lit faces on the left, casts
   * to the right. The haze is pulled to a neutral dust grey because a warm buff haze under a blue
   * zenith grades a frame mauve (2026-09-26). */
  TXDECK.declare({
    world: "watchtower",
    light: { az: -68, el: 10 },
    sky: { preset: "stormFront", haze: 0x9e9a92, clouds: 1.4, fogDensity: 0.0028, envIntensity: 0.75 },   /* round 2: the preset's haze closed the plain at 150 m into a white wall, and its dim sky light left every white housing taupe */
    ground: "#15171C",
    material: "#A9AEB0",
    accent: "#2A7A9E",
    grade: {
      exposure: 0.0,
      saturation: 0.98,
      contrast: 1.06,
      filmic: true,
      lift: [0.01, 0.01, 0.012],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.18, radius: 12 },
      grain: { amount: 0.013, size: 2, seed: 20260928 },
      aberration: 0,
      dither: true,
      sharpen: 0.16
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20260928;
  N.ACCENT = 0x2a7a9e;
  N.STRAW = 0x9c8a5c;           /* cured shortgrass, the ground colour the straw tufts stand in */

  /* THE KIT ADDITIONS: wildfire_camera_station and pipe_rail_fence. The kit has poles, towers,
   * lines and ranch gates and no detection camera and no oilfield pipe fence, and this deck
   * stands on both. Built under the conventions in the header of assets/js/txkit.js (metres, y
   * up, a mast anchored at its foot, front on +z, K.mat materials, bevelled manufactured edges)
   * so Phase 17 can lift them into assets/js/kit/ unchanged.
   *
   * wildfire_camera_station, WHAT IT IS, and only what the record says of it. The utility's plan
   * describes each location as "equipped with two physical cameras that rotate to detect smoke"
   * on a high vantage point. So: a tapered galvanized steel monopole on a concrete pier, a welded
   * crossarm near the top carrying two pan and tilt heads, each a sunshielded housing on a
   * turntable, a grey equipment enclosure at chest height with conduit up the mast, a small panel
   * antenna and a lightning rod. Nothing on it is a brand.
   *
   * OPTIONS. part ('station' | 'head'), height (m, 6 to 30, default 12), pan ([yaw, yaw] radians
   * about the mast, 0 faces +z; a single number for part 'head'), tilt ([pitch, pitch]), arm
   * (crossarm half span, m), enclosure, antenna, finish ('galvanized' | 'weathered'), lens (hex),
   * lensGlow (0..1).
   *
   * userData: lenses ([{x, y, z}] each window's centre in the model's own frame), heads ([{x, y, z}]
   * each turntable's centre), top, enclosure, dims ({H, arm}). */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.wildfire_camera_station) return;

    function mats(o) {
      var weathered = o.finish === 'weathered';
      return {
        galv: K.mat('cam-galv|' + o.finish, { color: weathered ? 0x8d8f89 : 0xb3b7b7, roughness: weathered ? 0.62 : 0.5, metalness: 0.5 }),   /* half metal: fully metallic steel mirrored the straw and read as brass under the grade (round 1) */
        galvDark: K.mat('cam-galvdark', { color: 0x6d7173, roughness: 0.5, metalness: 0.8 }),
        housing: K.mat('cam-housing', { color: 0xe7e6e1, roughness: 0.38, metalness: 0.05 }),
        shield: K.mat('cam-shield', { color: 0xf1f0ec, roughness: 0.32, metalness: 0.05, side: THREE.DoubleSide }),
        black: K.mat('cam-black', { color: 0x1d1f21, roughness: 0.55, metalness: 0.2 }),
        glass: new THREE.MeshPhysicalMaterial({ color: o.lens, roughness: 0.05, metalness: 0.0, clearcoat: 1, clearcoatRoughness: 0.03,
                                                emissive: o.lens, emissiveIntensity: +o.lensGlow || 0 }),
        box: K.mat('cam-enclosure', { color: 0xb9bcb8, roughness: 0.5, metalness: 0.3 }),
        conc: K.mat('cam-pier', { color: 0xffffff, map: K.tex('concrete'), roughness: 0.94 }),
        conduit: K.mat('cam-conduit', { color: 0x9c9fa0, roughness: 0.45, metalness: 0.7 })
      };
    }

    /* one pan and tilt head standing on y = 0 of its own group: a turntable drum, a U yoke, and
     * between its arms a cylindrical housing with a sunshield hood over it and a glass window at
     * the front. The housing's front is the group's +z, turned by pan about y and by tilt about x. */
    function head(M, pan, tilt) {
      var h = new THREE.Group(); h.rotation.y = pan || 0;
      /* A BOXED PTZ HEAD (round 1, 2026-09-28): a round barrel with a round dark face read as a
       * floodlight at feed size, so the housing is a rectangular white box under a flat sunshield
       * with a small dark rectangular window, the silhouette a reader knows as a camera. */
      K.cyl(0.07, 0.085, 0.12, M.housing, 0, 0, 0, 20, h);   /* the turntable and yoke in the housing's white, so the head reads as one seated unit (panel round 1) */
      [-1, 1].forEach(function (t) {
        var yoke = TXT.roundedBox(0.03, 0.2, 0.09, 0.008, M.housing); yoke.position.set(t * 0.12, 0.22, 0); h.add(yoke);
      });
      var base = TXT.roundedBox(0.28, 0.025, 0.1, 0.006, M.housing); base.position.set(0, 0.125, 0); h.add(base);   /* the yoke's base plate on the turntable, so the head sits on it and doesn't float (panel round 2) */
      var tg = new THREE.Group(); tg.position.set(0, 0.33, 0); tg.rotation.x = -(tilt || 0); h.add(tg);
      var body = TXT.roundedBox(0.2, 0.15, 0.42, 0.02, M.housing); tg.add(body);
      var shield = TXT.roundedBox(0.25, 0.018, 0.52, 0.008, M.shield); shield.position.set(0, 0.092, 0.04); tg.add(shield);
      var bez = TXT.roundedBox(0.15, 0.095, 0.012, 0.006, M.black); bez.position.set(0, -0.005, 0.212); tg.add(bez);
      var win = new THREE.Mesh(new THREE.PlaneGeometry(0.12, 0.07), M.glass); win.position.set(0, -0.005, 0.2195); tg.add(win);
      var back = TXT.roundedBox(0.16, 0.11, 0.02, 0.008, M.galvDark); back.position.set(0, 0, -0.215); tg.add(back);
      return h;
    }

    K.define('wildfire_camera_station', {
      anchor: 'base',
      size: [2.2, 13.2, 1.6],
      options: { part: 'station', height: 12, pan: [0.6, -2.5], tilt: [-0.08, -0.08], arm: 0.78, enclosure: true, antenna: true,
                 finish: 'galvanized', lens: 0x1a2228, lensGlow: 0 },
      note: 'Options: part station|head, height m (6 to 30), pan [yaw, yaw] radians for the two heads (0 faces +z; one number for part head), tilt [pitch, pitch], arm (crossarm half span m), enclosure bool, antenna bool, finish galvanized|weathered, lens hex, lensGlow 0..1. A wildfire detection station: a tapered galvanized monopole on a concrete pier, a crossarm with two pan and tilt camera heads in sunshielded housings, an equipment enclosure with conduit up the mast, a panel antenna and a lightning rod. part head returns one loose head on its turntable. userData.lenses, .heads, .top, .enclosure, .dims.',
      make: function (o, r) {
        var M = mats(o), g = new THREE.Group();
        if (o.part === 'head') {
          var p = Array.isArray(o.pan) ? o.pan[0] : o.pan, t = Array.isArray(o.tilt) ? o.tilt[0] : o.tilt;
          var hh = head(M, p, t); g.add(hh);
          g.userData.lenses = [{ x: Math.sin(p || 0) * 0.2, y: 0.34, z: Math.cos(p || 0) * 0.2 }];
          g.userData.heads = [{ x: 0, y: 0, z: 0 }];
          g.userData.keepOrigin = true;
          return g;
        }
        var H = Math.max(6, Math.min(30, +o.height || 12)), arm = +o.arm || 0.78;
        /* the pier: a cast pier standing 0.35 m proud of grade, a base plate, four anchor bolts */
        K.cyl(0.46, 0.5, 0.35, M.conc, 0, 0, 0, 28, g);
        var plate = TXT.roundedBox(0.62, 0.035, 0.62, 0.01, M.galvDark); plate.position.set(0, 0.3675, 0); g.add(plate);
        [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (s) {
          K.cyl(0.016, 0.016, 0.12, M.galvDark, s[0] * 0.24, 0.35, s[1] * 0.24, 8, g);
          K.cyl(0.03, 0.03, 0.03, M.galvDark, s[0] * 0.24, 0.39, s[1] * 0.24, 6, g);
        });
        /* the mast: a tapered 12 sided pole shipped in three parts, a base collar, a hand hole */
        var y0 = 0.387, rb = 0.2, rt = 0.11;
        var mast = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, H - y0, 12, 1), M.galv);
        mast.position.set(0, y0 + (H - y0) / 2, 0); g.add(mast);
        K.cyl(rb + 0.03, rb + 0.035, 0.22, M.galv, 0, y0, 0, 12, g);
        var hh2 = TXT.roundedBox(0.12, 0.26, 0.02, 0.01, M.galvDark); hh2.position.set(0, 0.95, rb - 0.01); g.add(hh2);
        [0.36, 0.7].forEach(function (f) {
          var y = y0 + (H - y0) * f, rr = rb + (rt - rb) * f;
          K.cyl(rr + 0.045, rr + 0.045, 0.03, M.galvDark, 0, y, 0, 12, g);
          for (var k = 0; k < 8; k++) { var a = k / 8 * Math.PI * 2; K.cyl(0.012, 0.012, 0.05, M.galvDark, Math.cos(a) * (rr + 0.03), y - 0.01, Math.sin(a) * (rr + 0.03), 6, g); }
        });
        K.cyl(rt + 0.02, rt + 0.02, 0.04, M.galvDark, 0, H - 0.02, 0, 12, g);
        K.bar([0, H, 0], [0, H + 0.95, 0], 0.009, M.galv, 6, g);
        K.cyl(0.02, 0.02, 0.04, M.galv, 0, H + 0.93, 0, 8, g);
        /* the crossarm, with a gusset each side and a platform plate at each end */
        var ya = H - 0.45;
        var armM = TXT.roundedBox(arm * 2 + 0.16, 0.1, 0.1, 0.012, M.galv); armM.position.set(0, ya, 0); g.add(armM);
        var lenses = [], heads = [];
        [-1, 1].forEach(function (s, i) {
          K.bar([s * 0.1, ya - 0.34, 0], [s * 0.42, ya - 0.04, 0], 0.018, M.galv, 6, g);
          K.cyl(0.11, 0.11, 0.018, M.galvDark, s * arm, ya + 0.05, 0, 20, g);
          var pan = (o.pan && o.pan[i] != null) ? o.pan[i] : 0, tilt = (o.tilt && o.tilt[i] != null) ? o.tilt[i] : 0;
          var hd = head(M, pan, tilt); hd.position.set(s * arm, ya + 0.068, 0); g.add(hd);
          lenses.push({ x: s * arm + Math.sin(pan) * 0.2, y: ya + 0.068 + 0.34, z: Math.cos(pan) * 0.2 });
          heads.push({ x: s * arm, y: ya + 0.068, z: 0 });
        });
        /* the enclosure on unistrut at chest height on the +z face, conduit up to the arm */
        var ye = 1.35, ze = rb + 0.02;
        if (o.enclosure !== false) {
          [ye - 0.05, ye + 0.62].forEach(function (y) { var s2 = TXT.roundedBox(0.62, 0.042, 0.042, 0.006, M.galvDark); s2.position.set(0, y, ze + 0.02); g.add(s2); });
          var bx = TXT.roundedBox(0.52, 0.68, 0.26, 0.02, M.box); bx.position.set(0, ye + 0.3, ze + 0.17); g.add(bx);
          var door = TXT.roundedBox(0.48, 0.64, 0.012, 0.01, M.box); door.position.set(0, ye + 0.3, ze + 0.306); g.add(door);
          var drip = TXT.roundedBox(0.58, 0.02, 0.3, 0.006, M.box); drip.position.set(0, ye + 0.66, ze + 0.17); g.add(drip);
          K.bar([0.19, ye + 0.22, ze + 0.32], [0.19, ye + 0.4, ze + 0.32], 0.012, M.black, 8, g);
          K.bar([0.12, ye + 0.64, ze + 0.12], [0.12, ya - 0.1, rt + 0.03], 0.017, M.conduit, 8, g);
          K.bar([-0.12, ye - 0.02, ze + 0.12], [-0.12, 0.36, ze + 0.12], 0.017, M.conduit, 8, g);
          for (var yy = ye + 1.2; yy < ya - 0.3; yy += 1.4) {
            var rr2 = rb + (rt - rb) * (yy - y0) / (H - y0);
            var strap = new THREE.Mesh(new THREE.TorusGeometry(rr2 + 0.012, 0.006, 6, 24), M.conduit); strap.rotation.x = Math.PI / 2; strap.position.y = yy; g.add(strap);
          }
        }
        if (o.antenna !== false) {
          var yA = ya - 1.4, rA = rb + (rt - rb) * (yA - y0) / (H - y0);
          K.bar([0, yA, 0], [0, yA, -(rA + 0.3)], 0.022, M.galv, 8, g);
          var pan2 = TXT.roundedBox(0.26, 0.42, 0.07, 0.02, M.housing); pan2.position.set(0, yA, -(rA + 0.36)); g.add(pan2);
          K.bar([0, yA - 0.2, -(rA + 0.36)], [0, yA - 0.6, -(rA + 0.05)], 0.008, M.black, 6, g);
        }
        g.userData.lenses = lenses; g.userData.heads = heads;
        g.userData.top = { x: 0, y: H, z: 0 };
        g.userData.enclosure = { x: 0, y: ye + 0.3, z: ze + 0.31 };
        g.userData.dims = { H: H, arm: arm };
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* pipe_rail_fence: the oilfield pipe fence of every Panhandle lease and ranch headquarters.
     * 0.114 m (4.5 in) pipe posts with welded domed caps at a spacing along x, and 0.073 m
     * (2 7/8 in) rails welded to their faces at given heights. Origin at the run's centre on the
     * ground, the run along x, front on +z. OPTIONS length, spacing, rails ([heights]), post (post
     * height above grade), color (paint hex, null for bare weathered pipe), flags ([post indices]
     * that carry a knot of survey flagging), flag (flag hex), flagAt (the height the knot is tied at, null for just under the cap).
     * userData: posts ([{x, y}] each post top), rails ([{y, z}] each rail's centre line). */
    K.define('pipe_rail_fence', {
      size: [20, 1.7, 0.2],
      options: { length: 20, spacing: 2.4, rails: [1.5, 0.9], post: 1.65, color: null, flags: [], flag: 0xff6a13, flagAt: null },
      note: 'Oilfield pipe fence: 4.5 in pipe posts with domed caps, 2 7/8 in rails welded to the post faces. Options length m, spacing m, rails [heights m], post (height m), color (paint hex or null for bare weathered pipe), flags [post indices] carrying survey flagging, flag hex, flagAt (knot height m). userData.posts, .rails.',
      make: function (o, r) {
        var g = new THREE.Group(), L = +o.length || 20, sp = +o.spacing || 2.4;
        var pipe = o.color != null ? K.mat('prf-paint|' + o.color, { color: o.color, roughness: 0.55, metalness: 0.4 })
                                   : K.mat('prf-pipe', { color: 0xa2a6a5, roughness: 0.55, metalness: 0.45 });   /* dull galvanized, so a rail reads as a lit line over the grass (round 1) */
        var n = Math.max(2, Math.round(L / sp) + 1), dx = L / (n - 1), posts = [];
        for (var i = 0; i < n; i++) {
          var x = -L / 2 + i * dx, ph = +o.post || 1.65;
          K.cyl(0.057, 0.057, ph, pipe, x, 0, 0, 14, g);
          var dome = new THREE.Mesh(new THREE.SphereGeometry(0.06, 14, 6, 0, Math.PI * 2, 0, Math.PI / 2), pipe); dome.position.set(x, ph, 0); g.add(dome);
          posts.push({ x: x, y: ph });
        }
        var rails = [];
        (o.rails || []).forEach(function (h) {
          K.bar([-L / 2 - 0.06, h, 0.09], [L / 2 + 0.06, h, 0.09], 0.0365, pipe, 12, g);
          rails.push({ y: h, z: 0.09 });
        });
        (o.flags || []).forEach(function (pi) {
          var p = posts[pi]; if (!p) return;
          var fm = K.mat('prf-flag|' + o.flag, { color: o.flag, roughness: 0.7, side: THREE.DoubleSide });
          var ky = o.flagAt != null ? +o.flagAt : p.y - 0.12;
          var knot = new THREE.Mesh(new THREE.TorusGeometry(0.066, 0.012, 6, 16), fm); knot.rotation.x = Math.PI / 2; knot.position.set(p.x, ky, 0); g.add(knot);
          for (var k = 0; k < 2; k++) {
            var tail = new THREE.Mesh(new THREE.PlaneGeometry(0.03, 0.34), fm);
            tail.position.set(p.x + 0.04 + k * 0.025, ky - 0.18, 0.06); tail.rotation.set(0.1, 0.4 + k * 0.5, 0.18 - k * 0.3); g.add(tail);
          }
        });
        g.userData.posts = posts; g.userData.rails = rails;
        return g;
      }
    });
  };

  /* THE HERO, made the same way on every frame. */
  N.station = function (K, o) {
    o = o || {};
    return K.make('wildfire_camera_station', Object.assign({ seed: 3, height: 12 }, o));
  };

  /* THE PASTURE'S TUFTS: cured shortgrass bunchgrass kept off any rectangles in world metres a
   * frame names. The frame lays its own TXT.ground first, in WATCH.STRAW, so the ground is in the
   * frame's source where depth_floor reads it. Call AFTER TXT.frame, because scatter thins with
   * distance from wherever the camera is at the call. */
  N.grass = function (TXT, R, o) {
    o = o || {};
    TXT.scatter(R, { kind: 'grass', count: o.count || 16000, area: o.area || [-120, -220, 120, 40], avoid: o.avoid || [], seed: (o.seed || 11) + 1, scale: o.scale || [0.7, 1.35] });
    if (o.scrub) TXT.scatter(R, { kind: 'scrub', count: o.scrub, area: o.scrubArea || o.area || [-300, -900, 300, -60], avoid: o.avoid || [], seed: (o.seed || 11) + 2, scale: [0.6, 1.1] });
  };

  /* THE FAR COUNTRY: the caprock escarpment and its red breaks, several kilometres out, where
   * TXT.sky's haze carries the distance. The ground must be large enough to pass under it. */
  N.caprock = function (K, TXT, R, o) {
    o = o || {};
    var me = K.make('mesa', { seed: o.seed || 2, kind: 'mesa', width: o.width || 1400, height: o.height || 80, scrub: o.scrub != null ? o.scrub : 0 });
    me.position.set(o.x != null ? o.x : 600, 0, o.z != null ? o.z : -3200); me.rotation.y = o.ry || 0.2;
    TXT.add(R, me);
    return me;
  };

  /* A PAGE, as a texture the size of a letter sheet at 8 px per mm: hairline entries for the
   * lines nobody reads, and the room for the DOM lines a frame registers onto it. entries is a
   * list of {kind: 'rule'|'gap'|'heading', w} drawn top to bottom. The type a reader reads is
   * DOM, set by the frame over the projected page, never painted here. */
  N.pageTexture = function (THREE, entries, o) {
    o = o || {};
    var W = 1728, H = 2232, c = document.createElement('canvas'); c.width = W; c.height = H;
    var x = c.getContext('2d');
    x.fillStyle = o.paper || '#f2f0ea'; x.fillRect(0, 0, W, H);
    var g = x.createLinearGradient(0, 0, W, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(60,50,40,0.06)');
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    var y = o.top || 200, lm = o.left || 200;
    (entries || []).forEach(function (e) {
      if (e.kind === 'gap') { y += e.h || 60; return; }
      if (e.kind === 'heading') { x.fillStyle = 'rgba(40,40,44,0.72)'; x.fillRect(lm, y, (W - 2 * lm) * (e.w || 0.5), 26); y += e.h || 70; return; }
      x.fillStyle = 'rgba(46,46,50,' + (e.a || 0.62) + ')'; x.fillRect(lm + (e.indent || 0), y, (W - 2 * lm - (e.indent || 0)) * (e.w || 1), e.t || 12); y += e.h || 44;
    });
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
    return t;
  };


  /* ATMOSPHERE TOWARD THE TYPE. Light dims toward type rather than being removed from around it
   * (ILLUSTRATION_SYSTEM, THE FIRST CHASSIS DECK). Two full-width vertical washes, never a box and
   * never over 0.45 alpha, so deck_chassis reads them as atmosphere and not as a plate: the storm
   * deck deepened from the top of the frame to just below the dek, where the brighter band under
   * the cloud would otherwise sit behind the last lines of type, and the near ground deepened under
   * the bottom furniture, where grass blades close to the lens would otherwise run through it. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector('.dek'), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    var top = o.a == null ? 0.38 : Math.min(0.45, o.a);
    if (bottom != null && top > 0) {
      var g = cx.createLinearGradient(0, 0, 0, bottom + (o.fade || 170));
      g.addColorStop(0, 'rgba(10,11,14,' + (top * 0.55) + ')');
      g.addColorStop(Math.max(0.05, bottom / (bottom + (o.fade || 170))), 'rgba(10,11,14,' + top + ')');
      g.addColorStop(1, 'rgba(10,11,14,0)');
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + (o.fade || 170));
    }
    var fa = o.floor == null ? 0.42 : Math.min(0.45, o.floor);
    if (fa > 0) {
      var y0 = N.H - (o.floorH || 190);
      var h = cx.createLinearGradient(0, y0, 0, N.H);
      for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); h.addColorStop(t, 'rgba(10,11,14,' + (fa * e).toFixed(4) + ')'); }   /* smoothstep, so the wash has no knee to read as a rule */
      cx.fillStyle = h; cx.fillRect(0, y0, N.W, N.H - y0);
    }
  };


  /* KNOCK THE EDGE OUT BEHIND A LINE OF TYPE, without removing its light. A rendered frame can't
   * consult a reserve mask as it draws, so a rail, a horizon or a grass blade that happens to run
   * through a label's glyph band reads as a strikethrough. This blurs the art under each named
   * element's line boxes, feathered wide, so the edge dissolves while the tone under the type stays
   * what the render made it: no plate, no hole, no change in value. */
  N.soften = function (cx, selectors, o) {
    o = o || {};
    var blur = o.blur || 9, pad = o.pad == null ? 16 : o.pad, feather = o.feather || 64;
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

  /* A world point to frame CSS px, through the frame's own camera, for leaders and registered
   * page lines that land on what they name. */
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

  global.WATCH = N;
})(this);
