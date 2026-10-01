/* deck/2026-10-01-plates.js — the chassis for the 2026-10-01 deck: Flock plate reader cameras
 * after the Governor ordered state agencies to pause funding for them, and each Texas town deciding
 * whether the camera on the pole stays on (tx-2026-0111, 0174, 0180, 0190, 0048).
 *
 * THE WORLD. A Texas roadside at blue hour. blueHour, tuned: a cobalt zenith, a clearer blue
 * horizon and an amber haze held thin, because the preset's blue horizon fogged toward its orange
 * haze printed the lower sky mauve on the probe frame (the doctrine's own named failure). The fog is
 * thinned for the same reason. In this world the declared light is the LAMP, a TxDOT cobra head,
 * and every exterior frame stands a kit streetlight where the light comes from (PL.lamp), so the
 * lamp's head and the shadows agree by construction. The cameras work "during the day and night"
 * (c25), and blue hour is the hinge between the two. The sky is one large softbox, so a 7 cm black
 * pole keeps its silhouette against it. The key never moves.
 *
 * DIRECTIONS. +x is east, -z is north. The light is declared at az -90 (clockwise from +z toward
 * +x, so due west) and el 34, the lamp's elevation over the subject. The seam and the lamp are on
 * the same side, west. Every road runs east and west along x, so a camera looking west down a road
 * looks into the seam and gets the pole as a dark T against it, and a camera looking north gets the
 * lamp from its left and the shadows falling east. Axis aligned on purpose: a scatter's avoid
 * rectangles are axis aligned, so a road along x keeps grass off the asphalt.
 *
 * THE HERO OBJECT. plate_reader, the kit addition below, drawn to Flock Safety's own published
 * Falcon specification. Its STATE is the deck's progress indicator: on, unbolted, stub, kept. It is
 * DRAWN at the size it is and no frame prints a dimension of it. PL.field stands any count of them
 * as instanced geometry, one unit per camera.
 *
 * THE ACCENT. #3E8F68, the green sheeting of a town limit sign (city_limit_sign below), where a
 * town's own say begins. It is only ever that sign, never the pole, never the sky.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the two kit
 * additions and the deck's materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("plates.js needs txdeck.js loaded first");

  /* ONE DECLARATION. In blueHour el is the lamp, az -90 (due west) el 34. */
  TXDECK.declare({
    world: "plates",
    light: { az: -90, el: 34 },
    sky: { preset: "blueHour", zenith: 0x0a1a40, horizon: 0x6f8cc4, haze: 0xe8a868, fogDensity: 0.0032, horizonGlow: 0.3, glow: 0.4, span: 0.5, clouds: 0.0, tone: 'agx' },
    ground: "#1A2133",
    material: "#16181B",
    accent: "#3E8F68",
    grade: {
      exposure: 0.0,
      saturation: 1.03,
      contrast: 1.06,
      filmic: true,
      lift: [0.006, 0.008, 0.016],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.18,
      bloom: { threshold: 0.82, strength: 0.16, radius: 12 },
      grain: { amount: 0.012, size: 2, seed: 20261001 },
      aberration: 0,
      dither: true,
      sharpen: 0.16
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261001;
  N.ACCENT = 0x3e8f68;
  N.CALICHE = 0x6e665c;     /* a caliche shoulder, grey warm, which the blue hour cools rather than tints mauve */
  N.VERGE = 0x6f7458;       /* a mown fall verge */
  N.LAMP = { az: -90, el: 34 };

  /* THE KIT ADDITION, plate_reader, built once here and lifted into assets/js/kit/civic.js by the
   * retro the same day. Conventions of txkit.js: metres, y up, anchored at the pole's foot on the
   * ground (anchor: 'base'), front (the lens) toward +z, materials through K.mat.
   *
   * Drawn to Flock Safety's own published specification for the Falcon (a village board packet,
   * Long Grove, Illinois, read 2026-10-01): a DOT breakaway pole of 6061 aluminum in black, 2.875 in
   * OD, 12 ft installed; dual solar panels 21.25 by 28 in each on the pole top; a camera body 8.75 by
   * 5 by 2.875 in on adjustable band clamps. None of these dimensions is a published figure of this
   * deck and no frame prints one. The kit carries them so the object is the size it is.
   *
   * STATES, because the story is the object's state:
   *   on       the lens glass clear, the IR ring faintly lit when ir > 0 (dusk and night)
   *   off      the same hardware, the ring dark, nothing else changes. A switched off camera looks
   *            like a switched on one, which is the point a frame can make with a caption, never
   *            with an invented light
   *   bagged   a black contractor bag over the camera head, tied at the clamp, as a city covers a
   *            camera it has stopped using
   *   removed  the camera and its clamps gone, the pole and panels standing, two clamp scars
   *   stub     the pole cut away: the breakaway base on its footing and four bolts, all that is
   *            left after a removal order is carried out
   */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.plate_reader && K.registry.city_limit_sign) return;
    var IN = 0.0254;

    function mats(o) {
      return {
        pole: K.mat('pr-pole', { color: 0x16181b, roughness: 0.42, metalness: 0.55 }),
        cast: K.mat('pr-cast', { color: 0x8d9094, roughness: 0.55, metalness: 0.7 }),
        conc: K.mat('pr-conc', { color: 0xa9a59c, roughness: 0.92, metalness: 0.0 }),
        bolt: K.mat('pr-bolt', { color: 0x6c6e70, roughness: 0.4, metalness: 0.85 }),
        frame: K.mat('pr-frame', { color: 0xb9bcc0, roughness: 0.35, metalness: 0.8 }),
        cell: K.mat('pr-cell', { color: 0x10151f, roughness: 0.18, metalness: 0.35 }),
        backsheet: K.mat('pr-back', { color: 0xd8d8d2, roughness: 0.7 }),
        housing: K.mat('pr-housing', { color: 0x202326, roughness: 0.5, metalness: 0.1 }),
        hood: K.mat('pr-hood', { color: 0x2a2d31, roughness: 0.45, metalness: 0.1 }),
        glass: K.mat('pr-glass', { color: 0x0b0f14, roughness: 0.06, metalness: 0.6 }),
        ir: K.mat('pr-ir-' + Math.round((+o.ir || 0) * 100), { color: 0x2a0d0d, emissive: 0xff2a1a, emissiveIntensity: (o.state === 'on' ? (+o.ir || 0) : 0) * 2.2, roughness: 0.3 }),
        clamp: K.mat('pr-clamp', { color: 0x9a9da1, roughness: 0.3, metalness: 0.9 }),
        bag: K.mat('pr-bag', { color: 0x111214, roughness: 0.42, metalness: 0.0 }),
        puck: K.mat('pr-puck', { color: 0xe4e4df, roughness: 0.55 }),
        scar: K.mat('pr-scar', { color: 0x3a3d40, roughness: 0.6, metalness: 0.4 })
      };
    }

    function rbx(w, h, d, r, m, x, y, z, parent) {
      var b = TXT.roundedBox(w, h, d, r, m); b.position.set(x, y, z); parent.add(b); return b;
    }

    /* one solar panel, face toward +z before its tilt: an aluminium frame, a dark cell field
     * divided into cells by thin silver busbars, a white backsheet behind */
    function panel(M, g, w, h) {
      var p = new THREE.Group();
      rbx(w, h, 0.035, 0.006, M.frame, 0, 0, 0, p);
      rbx(w - 0.03, h - 0.03, 0.004, 0.001, M.cell, 0, 0, 0.0185, p);
      rbx(w - 0.02, h - 0.02, 0.004, 0.001, M.backsheet, 0, 0, -0.0185, p);
      var cols = 4, rows = 6;
      for (var i = 1; i < cols; i++) rbx(0.003, h - 0.04, 0.002, 0.0005, M.frame, -w / 2 + i * w / cols, 0, 0.0215, p);
      for (var j = 1; j < rows; j++) rbx(w - 0.04, 0.003, 0.002, 0.0005, M.frame, 0, -h / 2 + j * h / rows, 0.0215, p);
      g.add(p);
      return p;
    }

    /* the camera head: a long body along +z under a sun hood, the lens and the IR ring on its
     * front face, two band clamps round the pole behind it */
    function head(M, o, g, y, r) {
      var c = new THREE.Group(), L = 8.75 * IN, Hh = 5 * IN, Wd = 2.875 * IN;
      rbx(Wd, Hh, L, 0.012, M.housing, 0, 0, 0, c);
      rbx(Wd + 0.016, 0.008, L + 0.05, 0.003, M.hood, 0, Hh / 2 + 0.006, 0.02, c);
      rbx(0.004, Hh * 0.55, L + 0.04, 0.001, M.hood, Wd / 2 + 0.006, Hh * 0.2, 0.018, c);
      rbx(0.004, Hh * 0.55, L + 0.04, 0.001, M.hood, -Wd / 2 - 0.006, Hh * 0.2, 0.018, c);
      var lens = new THREE.Mesh(new THREE.CylinderGeometry(0.019, 0.019, 0.006, 24), M.glass);
      lens.rotation.x = Math.PI / 2; lens.position.set(0, 0.012, L / 2 + 0.002); c.add(lens);
      var ring = new THREE.Mesh(new THREE.TorusGeometry(0.026, 0.0035, 8, 28), M.ir);
      ring.position.set(0, 0.012, L / 2 + 0.003); c.add(ring);
      rbx(Wd * 0.8, 0.016, 0.02, 0.004, M.housing, 0, -Hh / 2 - 0.006, -L / 2 + 0.03, c);
      c.rotation.order = 'YXZ';
      c.rotation.y = +o.yaw || 0; c.rotation.x = -(+o.tilt || 0);
      var arm = new THREE.Group();
      arm.position.set(0, y, 0); arm.rotation.y = +o.yaw || 0;
      /* the bracket from the clamps out to the body */
      rbx(0.03, 0.03, r + 0.09, 0.006, M.clamp, 0, -Hh / 2 - 0.02, (r + 0.09) / 2, arm);
      g.add(arm);
      c.position.set(Math.sin(+o.yaw || 0) * (r + 0.11), y, Math.cos(+o.yaw || 0) * (r + 0.11));
      g.add(c);
      return c;
    }

    K.define('plate_reader', {
      anchor: 'base',
      size: [1.25, 4.2, 0.9],
      options: { height: 12 * 0.3048, panels: 2, yaw: 0, tilt: 0.14, state: 'on', ir: 0, face: 0, footing: true },
      note: 'A solar powered automated license plate reader on its own pole, drawn to Flock Safety\'s published Falcon specification: a black 2.875 in DOT breakaway aluminum pole 12 ft tall on a cast breakaway base and a concrete footing, dual 21.25 x 28 in solar panels on the pole top tilted to the south (face), a camera body 8.75 x 5 x 2.875 in on band clamps under them aimed along +z (yaw, tilt down), an LTE puck. state on|off|bagged|removed|stub; ir 0..1 lights the IR ring when on. userData.lens, .top, .head.',
      make: function (o) {
        var M = mats(o), g = new THREE.Group();
        var H = +o.height || 3.66, r = 2.875 * IN / 2, st = o.state || 'on';
        /* the footing, flush with grade with a slight crown, and the breakaway base: a square cast
         * pedestal with four bolts, the pole socketed into it */
        if (st === 'stub') {
          /* what a removal leaves: a square pad proud of grade, four bolts, scuffed dirt round it */
          rbx(0.6, 0.05, 0.6, 0.01, M.conc, 0, 0.025, 0, g);
          [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (q) {
            K.cyl(0.0125, 0.0125, 0.08, M.bolt, q[0] * 0.18, 0.05, q[1] * 0.18, 10, g);
            K.cyl(0.022, 0.022, 0.018, M.bolt, q[0] * 0.18, 0.06, q[1] * 0.18, 6, g);
          });
          g.userData.top = { x: 0, y: 0.13, z: 0 }; g.userData.keepOrigin = true;
          return g;
        }
        if (o.footing !== false) K.cyl(0.24, 0.26, 0.06, M.conc, 0, -0.03, 0, 24, g);
        rbx(0.2, 0.012, 0.2, 0.004, M.cast, 0, 0.033, 0, g);
        var base = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.085, 0.2, 16), M.cast);
        base.position.set(0, 0.139, 0); g.add(base);
        [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (s) {
          K.cyl(0.009, 0.009, 0.05, M.bolt, s[0] * 0.072, 0.039, s[1] * 0.072, 8, g);
          K.cyl(0.015, 0.015, 0.012, M.bolt, s[0] * 0.072, 0.068, s[1] * 0.072, 6, g);
        });
        g.userData.top = { x: 0, y: 0.24, z: 0 };
        /* the pole */
        var pole = new THREE.Mesh(new THREE.CylinderGeometry(r, r, H - 0.22, 20, 1), M.pole);
        pole.position.set(0, 0.22 + (H - 0.22) / 2, 0); g.add(pole);
        K.cyl(r + 0.004, r + 0.004, 0.02, M.pole, 0, H - 0.01, 0, 20, g);
        /* the panels: a T bracket on the pole top, two panels side by side on east and west arms,
         * tilted 35 degrees up toward their face */
        var face = +o.face || 0, pw = 21.25 * IN, ph = 28 * IN, tilt = 0.61;
        var top = new THREE.Group(); top.position.set(0, H + 0.02, 0); top.rotation.y = face; g.add(top);
        rbx(0.05, 0.05, 0.05, 0.008, M.frame, 0, 0.02, 0, top);
        var n = +o.panels === 1 ? 1 : 2;
        for (var i = 0; i < n; i++) {
          var x = n === 1 ? 0 : (i === 0 ? -1 : 1) * (pw / 2 + 0.03);
          var p = panel(M, top, pw, ph);
          p.rotation.x = -(Math.PI / 2 - tilt);
          p.position.set(x, 0.05 + Math.sin(tilt) * 0.02 + ph / 2 * Math.cos(tilt) * 0.2, 0);
          K.bar([x * 0.2, 0.03, 0], [x, 0.05, 0], 0.012, M.frame, 8, top);
        }
        /* the LTE puck and the battery pack under the panels */
        K.bar([0, H + 0.04, 0], [0, H + 0.62, 0], 0.012, M.frame, 8, g);
        K.cyl(0.055, 0.06, 0.04, M.puck, 0, H + 0.62, 0, 20, g);
        g.userData.puck = { x: 0, y: H + 0.66, z: 0 };
        rbx(0.14, 0.24, 0.09, 0.012, M.housing, 0, H - 0.35, -(r + 0.045), g);
        rbx(0.15, 0.012, 0.1, 0.004, M.clamp, 0, H - 0.21, -(r + 0.045), g);
        rbx(0.15, 0.012, 0.1, 0.004, M.clamp, 0, H - 0.49, -(r + 0.045), g);
        /* the band clamps at camera height, and the camera itself unless it was taken down */
        var yc = H - 0.75;
        [yc - 0.06, yc + 0.06].forEach(function (y) {
          var band = new THREE.Mesh(new THREE.TorusGeometry(r + 0.004, 0.006, 6, 24), st === 'removed' ? M.scar : M.clamp);
          band.rotation.x = Math.PI / 2; band.position.y = y; g.add(band);
        });
        if (st !== 'removed') {
          var c = head(M, o, g, yc, r);
          if (st === 'bagged') {
            /* a contractor bag pulled over the head: a soft bulb longer than the body, sagging
             * below it, gathered at the clamp, and dented so it reads as film over a box */
            var bg = new THREE.SphereGeometry(1, 22, 16), pa = bg.attributes.position;
            for (var k = 0; k < pa.count; k++) {
              var bx = pa.getX(k), by = pa.getY(k), bz = pa.getZ(k);
              var sq = 0.75 + 0.25 * Math.abs(by);            /* squarer sides over the box */
              var dent = 1 + 0.06 * Math.sin(bx * 9 + bz * 5) * Math.cos(by * 7);
              pa.setXYZ(k, bx * sq * dent, by < 0 ? by * 1.25 : by, bz * dent);
            }
            bg.computeVertexNormals();
            var bag = new THREE.Mesh(bg, M.bag);
            bag.scale.set(0.07, 0.1, 0.16);
            bag.rotation.y = +o.yaw || 0;
            bag.position.copy(c.position); bag.position.y -= 0.015; g.add(bag);
            var tie = new THREE.Mesh(new THREE.TorusGeometry(r + 0.01, 0.007, 6, 20), M.bag);
            tie.rotation.x = Math.PI / 2; tie.position.y = yc - 0.11; g.add(tie);
          }
          g.userData.head = c;
          c.updateMatrixWorld(true);
          g.userData.lens = { x: c.position.x, y: c.position.y + 0.012, z: c.position.z };
        }
        g.userData.top = { x: 0, y: H + 0.4, z: 0 };
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* THE SECOND KIT ADDITION, city_limit_sign: a TxDOT style guide sign on two posts, green
     * retroreflective sheeting inside a white border, the legend left blank because no source
     * names the towns. Front (the face) toward +z, anchored at the ground between the posts. The
     * sheeting is the deck's one accent and is only ever this sign. */
    K.define('city_limit_sign', {
      size: [1.6, 2.4, 0.12],
      options: { w: 1.52, h: 0.76, bottom: 1.5, glow: 0.55 },
      note: 'A blank TxDOT style green guide sign (60 x 30 in by default) on two galvanized U channel posts, bottom at 1.5 m: a white border round green retroreflective sheeting, an aluminium back with two horizontal stiffeners. glow 0..1 lifts the sheeting as it returns a lamp or headlights. Front +z.',
      make: function (o) {
        var g = new THREE.Group(), w = +o.w || 1.52, h = +o.h || 0.76, b = o.bottom == null ? 1.5 : +o.bottom;
        var post = K.mat('cls-post', { color: 0x9a9fa3, roughness: 0.45, metalness: 0.8 });
        var back = K.mat('cls-back', { color: 0x8f9396, roughness: 0.5, metalness: 0.7 });
        var white = K.mat('cls-white', { color: 0xe9ece8, roughness: 0.4, emissive: 0xe9ece8, emissiveIntensity: 0.12 * (+o.glow || 0) });
        var green = K.mat('cls-green-' + Math.round((+o.glow || 0) * 100), { color: N.ACCENT, roughness: 0.35, emissive: N.ACCENT, emissiveIntensity: 0.9 * (+o.glow || 0) });
        [-w * 0.3, w * 0.3].forEach(function (x) {
          rbx(0.05, b + h - 0.04, 0.035, 0.004, post, x, (b + h - 0.04) / 2, -0.03, g);
        });
        rbx(w, h, 0.012, 0.01, back, 0, b + h / 2, 0, g);
        rbx(w - 0.006, h - 0.006, 0.004, 0.008, white, 0, b + h / 2, 0.008, g);
        rbx(w - 0.16, h - 0.16, 0.004, 0.025, green, 0, b + h / 2, 0.011, g);
        [b + h * 0.25, b + h * 0.75].forEach(function (y) { rbx(w * 0.9, 0.03, 0.02, 0.004, back, 0, y, -0.016, g); });
        g.userData.face = { x: 0, y: b + h / 2, z: 0.013 };
        return g;
      }
    });
  };

  /* THE LAMP THE LIGHT COMES FROM. A kit streetlight `d` metres from `at` toward the declared
   * light, its arm reaching back toward `at`, so the cobra head stands where the key says it is. */
  N.lampDir = function () {
    var a = N.LAMP.az * Math.PI / 180;
    return [Math.sin(a), Math.cos(a)];
  };
  N.lamp = function (K, R, TXT, at, d, o) {
    o = o || {};
    var dir = N.lampDir(), x = at[0] + dir[0] * d, z = at[1] + dir[1] * d;
    var s = K.make('streetlight', { height: o.height || 9.1, reach: o.reach || 2.4, finish: 'galvanized' });
    s.position.set(x, 0, z);
    s.rotation.y = Math.atan2(at[0] - x, at[1] - z);
    /* the cobra head's lens lit, a cool 4000K white, so the lamp reads as on */
    /* the cobra head's lens: the one material with a warm white emissive. Matched on the colour
     * itself, never on an exact hex, because colour management round trips the hex. */
    s.traverse(function (m) {
      var e = m.isMesh && m.material && m.material.emissive;
      if (e && e.r > 0.85 && e.g > 0.8 && e.b > 0.6 && m.material.emissiveIntensity < 1) {
        m.material = m.material.clone(); m.material.emissiveIntensity = o.lit == null ? 3.2 : o.lit;
      }
    });
    TXT.add(R, s); TXT.contact(R, s);
    /* and the light it gives: a 4000K pool under the head, no shadow of its own (the deck's one
     * shadow casting key is deckRig, which stands where this lamp is) */
    if (N.T && o.pool !== false) {
      var reach = o.reach || 2.4, hx = x + Math.sin(s.rotation.y) * reach, hz = z + Math.cos(s.rotation.y) * reach;
      var pl = new N.T.PointLight(0xfff0d8, o.pool || 70, 26, 2);
      pl.position.set(hx, (o.height || 9.1) - 0.4, hz); R.scene.add(pl);
    }
    return s;
  };


  /* SCENERY THE FRAMES SHARE, as primitives. Each frame decides where things go; these only save
   * it typing the same three lines for every tree, road and sign. */
  N.trees = function (K, R, TXT, list, o) {
    o = o || {};
    list.forEach(function (t) {
      var tr = K.make(t[2], { seed: t[3], height: t[4] }); tr.position.set(t[0], 0, t[1]);
      if (t[5] != null) tr.rotation.y = t[5];
      TXT.add(R, tr); if (o.contact !== false) TXT.contact(R, tr);
    });
  };
  N.road = function (K, R, TXT, at, o) {
    o = o || {};
    var rd = K.make('road', { length: o.length || 900, lanes: o.lanes || 2, sidewalk: !!o.sidewalk, parkway: o.parkway == null ? 1.6 : o.parkway });
    rd.position.set(at[0], 0, at[1]); if (o.rotY) rd.rotation.y = o.rotY; TXT.add(R, rd);
    return rd;
  };
  /* A RURAL TWO LANE ROAD with no curb: neutral blue black asphalt, white edge lines, a double
   * yellow centre and caliche gravel shoulders at grade. The kit road is a city street with curb
   * and gutter, which a ranch road never has. Along x, centred on `at`. */
  N.lane = function (K, R, TXT, at, o) {
    o = o || {};
    var T = N.T, g = new T.Group(), L = o.length || 900, rw = 7.2, sh = o.shoulder == null ? 2.4 : o.shoulder;
    function slab(m, w, h, z, y) { var b = new T.Mesh(new T.BoxGeometry(L, h, w), m); b.position.set(0, (y || 0) + h / 2, z); b.receiveShadow = true; g.add(b); }
    var asph = K.mat('pl-asphalt', { color: 0x2b2d31, roughness: 0.93 }), grav = K.mat('pl-shoulder', { color: o.gravel || 0x6a6359, roughness: 1 });
    var white = K.mat('pl-paint', { color: 0xd8d8d2, roughness: 0.6 }), yel = K.mat('pl-yellow', { color: 0xc99a2a, roughness: 0.6 });
    slab(asph, rw, 0.04, 0);
    slab(grav, sh, 0.02, rw / 2 + sh / 2); slab(grav, sh, 0.02, -(rw / 2 + sh / 2));
    slab(white, 0.15, 0.004, rw / 2 - 0.25, 0.04); slab(white, 0.15, 0.004, -(rw / 2 - 0.25), 0.04);
    slab(yel, 0.1, 0.004, 0.11, 0.04); slab(yel, 0.1, 0.004, -0.11, 0.04);
    g.position.set(at[0], 0, at[1]); if (o.rotY) g.rotation.y = o.rotY;
    TXT.add(R, g);
    return g;
  };
  N.sign = function (K, R, TXT, at, rotY, glow) {
    var sg = K.make('city_limit_sign', { glow: glow == null ? 0.8 : glow });
    sg.position.set(at[0], 0, at[1]); sg.rotation.y = rotY || 0; TXT.add(R, sg); TXT.contact(R, sg);
    return sg;
  };

  /* THE HERO, the same call on every frame. */
  N.pole = function (K, o) {
    o = o || {};
    return K.make('plate_reader', { state: o.state || 'on', yaw: o.yaw == null ? 0 : o.yaw, tilt: o.tilt == null ? 0.14 : o.tilt, face: o.face || 0, seed: o.seed || 1, footing: o.footing });
  };

  /* LOW DETAIL POLES AS INSTANCED GEOMETRY, one mesh per material, the unit drawn to the same
   * dimensions as the kit model: the pole, the base, two tilted panels, the camera body and its
   * bracket. */
  N.lodParts = function (THREE) {
    function merged(boxes) {
      var geos = boxes.map(function (b) {
        var gg = b[7] === 'cyl' ? new THREE.CylinderGeometry(b[0], b[0], b[1], 10) : new THREE.BoxGeometry(b[0], b[1], b[2]);
        if (b[6]) gg.applyMatrix4(new THREE.Matrix4().makeRotationX(b[6]));
        gg.translate(b[3], b[4], b[5]);
        return gg.index ? gg.toNonIndexed() : gg;
      });
      var total = 0; geos.forEach(function (gg) { total += gg.attributes.position.count; });
      var pos = new Float32Array(total * 3), nor = new Float32Array(total * 3), k = 0;
      geos.forEach(function (gg) { pos.set(gg.attributes.position.array, k * 3); nor.set(gg.attributes.normal.array, k * 3); k += gg.attributes.position.count; });
      var out = new THREE.BufferGeometry();
      out.setAttribute('position', new THREE.BufferAttribute(pos, 3)); out.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
      return out;
    }
    var IN = 0.0254, H = 12 * 0.3048, pw = 21.25 * IN, ph = 28 * IN, t = -(Math.PI / 2 - 0.61);
    return {
      pole: merged([[0.0365, H - 0.22, 0, 0, 0.22 + (H - 0.22) / 2, 0, 0, 'cyl'], [0.08, 0.2, 0, 0, 0.12, 0, 0, 'cyl'], [0.14, 0.24, 0.09, 0, H - 0.35, -0.08]]),
      panel: merged([[pw, ph, 0.035, -(pw / 2 + 0.03), H + 0.2, 0, t], [pw, ph, 0.035, (pw / 2 + 0.03), H + 0.2, 0, t]]),
      cam: merged([[0.073, 0.127, 0.222, 0, H - 0.75, 0.15], [0.03, 0.03, 0.12, 0, H - 0.83, 0.06]])
    };
  };

  /* A FIELD OF POLES. cols x rows at pitch [px, pz] from origin [x0, z0] (the near left pole),
   * rows running north (-z). count is exact. near(x, z, i) returning true puts a full kit model
   * there instead of an instance. Returns a group with userData.drawn, the number of poles placed,
   * which a frame asserts equals the figure it was given. */
  N.field = function (K, THREE, TXT, o) {
    o = o || {};
    var count = o.count | 0, cols = o.cols | 0, px = o.pitch ? o.pitch[0] : 6, pz = o.pitch ? o.pitch[1] : 6;
    if (!count || !cols) throw new Error('PL.field needs count and cols from the frame');
    var x0 = o.origin ? o.origin[0] : 0, z0 = o.origin ? o.origin[1] : 0;
    var g = new THREE.Group(), far = [], detailed = 0, drawn = 0;
    for (var i = 0; i < count; i++) {
      var c = i % cols, rw = Math.floor(i / cols), x = x0 + c * px, z = z0 - rw * pz;
      drawn++;
      if (o.near && o.near(x, z, i)) {
        var p = N.pole(K, { yaw: o.yaw || 0, face: o.face || 0 }); p.position.set(x, 0, z); g.add(p); detailed++;
      } else far.push([x, 0, z, o.rotY || 0, 1]);
    }
    if (far.length) {
      var P = N.lodParts(THREE);
      var mp = K.mat('pr-pole-lod', { color: 0x16181b, roughness: 0.45, metalness: 0.5 }),
          mg = K.mat('pr-panel-lod', { color: 0x1a2232, roughness: 0.12, metalness: 0.4 }),
          mc = K.mat('pr-cam-lod', { color: 0x202326, roughness: 0.5, metalness: 0.1 });
      [[P.pole, mp], [P.panel, mg], [P.cam, mc]].forEach(function (pm) {
        var im = K.instances(pm[0], pm[1], far, g); im.castShadow = o.castShadow !== false; im.receiveShadow = true;
      });
      /* a soft dark footprint under every instanced pole, so each one stands on the ground */
      var fc = document.createElement('canvas'); fc.width = fc.height = 64; var fx = fc.getContext('2d');
      var rg = fx.createRadialGradient(32, 32, 2, 32, 32, 31); rg.addColorStop(0, 'rgba(0,0,0,0.6)'); rg.addColorStop(1, 'rgba(0,0,0,0)'); fx.fillStyle = rg; fx.fillRect(0, 0, 64, 64);
      var ft = new THREE.CanvasTexture(fc), fg = new THREE.PlaneGeometry(0.6, 0.6); fg.rotateX(-Math.PI / 2); fg.translate(0, 0.02, 0);
      var fm = new THREE.MeshBasicMaterial({ map: ft, transparent: true, depthWrite: false, color: 0x000000, opacity: 0.85 });
      var fim = K.instances(fg, fm, far, g); fim.castShadow = false; fim.receiveShadow = false; fim.renderOrder = 1;
    }
    g.userData.drawn = drawn; g.userData.detailed = detailed;
    return g;
  };

  /* ONE LOT, ONE LENS, for the two frames that compare counts. Ranks of eleven at 2.6 m, 4 m
   * apart, filled from the near rank, left to right, so 32 and 165 stand on the same ground in
   * the same order and only the count differs. The first `near` ranks are the full kit model.
   * N.lotView is the one camera both frames use. */
  N.lot = function (K, THREE, TXT, R, count, o) {
    o = o || {};
    var files = 11, px = 2.6, pz = 4.0, near = o.near == null ? 2 : o.near, full = new THREE.Group(), far = [], drawn = 0;
    for (var i = 0; i < count; i++) {
      var c = i % files, r = Math.floor(i / files), x = -((files - 1) * px) / 2 + c * px, z = -r * pz;
      if (r < near) { var u = N.pole(K, { yaw: -Math.PI / 2, face: 0, seed: 40 + i }); u.position.set(x, 0, z); full.add(u); }
      else far.push([x, 0, z, 0, 1]);
      drawn++;
    }
    TXT.add(R, full);
    if (far.length) {
      var P = N.lodParts(THREE), g = new THREE.Group();
      [[P.pole, K.mat('pr-pole-lod', { color: 0x16181b, roughness: 0.45, metalness: 0.5 })],
       [P.panel, K.mat('pr-panel-lod', { color: 0x1a2232, roughness: 0.12, metalness: 0.4 })],
       [P.cam, K.mat('pr-cam-lod', { color: 0x202326, roughness: 0.5, metalness: 0.1 })]].forEach(function (pm) {
        var im = K.instances(pm[0], pm[1], far, g); im.castShadow = true; im.receiveShadow = true;
      });
      TXT.add(R, g);
    }
    return drawn;
  };
  N.lotView = function (TXT, R) { TXT.frame(R, { from: [0, 7, 30], look: [0, 2.5, -20] }); };

  /* THE SKY BAND THE TYPE STANDS IN. A light wash toward the type, never over 0.45 alpha. On a
   * blue hour sky the type is light, so the wash DARKENS a little behind it rather than lifting. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector('.dek'), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    var a = o.a == null ? 0.22 : Math.min(0.45, o.a);
    if (bottom != null && a > 0) {
      var fade = o.fade || 180, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, 'rgba(8,14,32,' + (a * 0.8) + ')');
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), 'rgba(8,14,32,' + a + ')');
      g.addColorStop(1, 'rgba(8,14,32,0)');
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

  /* THE POST STEPS every frame takes before its grade, in one place. The frame still calls
   * TXDECK.finish itself, last. A dark band under the footer, never a box and never over 0.45. */
  N.post = function (cx, o) {
    o = o || {};
    N.atmosphere(cx, { a: o.a == null ? 0.2 : o.a });
    N.soften(cx, o.type || ['.kick', '.hook', '.dek'], { blur: o.typeBlur || 8, pad: 8, feather: o.typeFeather || 26 });
    N.soften(cx, ['.tx-site', '.src'], { blur: 9, pad: 14, feather: 40 });
    var y0 = N.H - (o.veilH || 220), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, 'rgba(6,9,18,' + (Math.min(0.45, o.veil == null ? 0.32 : o.veil) * e).toFixed(4) + ')'); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };

  /* Triangular noise of about one level per channel breaks the 8 bit steps a soft wash makes on a
   * smooth sky. Seeded, so a re-render is identical. */
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) {
      var n = (rnd() + rnd() - 1) * 1.2;
      d[i] += n; d[i + 1] += n; d[i + 2] += n;
    }
    cx.putImageData(id, 0, 0);
  };

  /* A world point to frame CSS px, through the frame's own camera. */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };


  /* THE SHELL EVERY FRAME SHARES, kept here rather than typed into nine frames: the type styles,
   * the furniture, the fit of the hook and the stage. None of it draws anything. */
  N.CSS = [
    '* { margin:0; padding:0; box-sizing:border-box; }',
    'html, body { width:1080px; height:1350px; overflow:hidden; background:#1A2133; }',
    'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
    'canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }',
    '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:800; line-height:0.98; letter-spacing:-0.01em; color:#F2F1EC; font-variation-settings:"opsz" 144; z-index:10; }',
    '.dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:#EEF0F3; z-index:10; }',
    '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:#E6E7EA; white-space:nowrap; z-index:20; }',
    '.hook, .dek, .tx-site, .kick, .src, .cap, .lab { text-shadow:0 0 2px rgba(6,10,24,0.45), 0 1px 12px rgba(6,10,24,0.35); }'
  ].join('\n');
  N.start = function (o) {
    var st = document.createElement('style'); st.textContent = N.CSS;
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: '#E6E7EA' });
    TX.fitText(document.getElementById('hook'), o.fit || { min: 96, max: 128, maxLines: 2 });
    N.follow();
  };
  /* THE BOOT, once per frame: fonts, the shell, the engine and the kit with this deck's additions. */
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE;
    await document.fonts.ready;
    N.start(o);
    /* the frame binds the bench itself (const TXT = init(THREE)), so print_ban can follow the sky
     * and the kept snapshot to one context. A bare init function is still accepted. */
    var TXT = typeof bench === 'function' ? bench(THREE) : bench, K = initKit(THREE, TXT);
    N.installKit(K, THREE, TXT);
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
  };
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    return TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 40, near: o.near || 0.05, far: o.far || 5000 });
  };

  /* THE DECK'S SHELL, continued. */
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

  global.PL = N;
})(this);
