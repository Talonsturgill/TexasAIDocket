/* deck/2026-10-02-vials.js — the chassis for the 2026-10-02 deck: an AI tool flags BRSK1 for a
 * child in the Texome Project, a research network finds more families, and fruit flies do the
 * proving (tx-2026-0195).
 *
 * THE WORLD. A Houston laboratory window at golden hour, the camera turned INTO the low sun, so a
 * clear vial glows at its rim and the food and the plug hold a warm seam. goldenHour, tuned: the
 * haze pulled toward a Gulf coast gold and kept thin, the zenith left blue, because the doctrine's
 * named failure is a sky that mixes orange into blue and prints mauve. The key never moves.
 *
 * DIRECTIONS. +x is east, -z is north. The light is declared at az -78 (just north of due west)
 * and el 7, inside goldenHour's range. A camera looking west toward -x looks into the sun and gets
 * the vial lit from behind. A camera looking north gets the sun from its left and the shadows of
 * the sill falling east, to its right.
 *
 * THE HERO OBJECT. fly_vial, the kit addition below: a clear polystyrene culture vial, a band of
 * cornmeal food at its foot, a cellulose plug at its mouth, pupae on its wall and adult flies, at
 * the size such a vial is. Its STATE carries the argument: the flies climb, the flies are down on
 * the food (the gene disabled), the flies climb again (the human gene), the flies climb part way
 * (a patient's variant). No frame prints a dimension of it, and no state draws a measurement the
 * record does not give: a climb height is a picture of "largely" and "partially", never a number.
 *
 * THE ACCENT. #4FC79A, signal_open in config/brand.yaml: the one highlighted row where the tool
 * pointed, and the tape on the vial that holds that gene. It is never the sky and never a fly.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the kit
 * additions and the deck's materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("vials.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "vials",
    light: { az: -78, el: 12 },
    sky: { preset: "goldenHour", fogDensity: 0.0012, clouds: 0.22, haze: 0xf0bf86, horizonGlow: 1.45 },
    ground: "#20232B",
    material: "#D9D2C2",
    accent: "#4FC79A",
    grade: {
      exposure: 0.0,
      saturation: 1.02,
      contrast: 1.05,
      filmic: true,
      lift: [0.008, 0.007, 0.010],
      gain: [1.0, 0.99, 0.97],
      vignette: 0.2,
      bloom: { threshold: 0.8, strength: 0.18, radius: 14 },
      grain: { amount: 0.011, size: 2, seed: 20261002 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261002;
  N.ACCENT = 0x4fc79a;
  N.SILL_Y = 18;            /* the laboratory floor's window sill stands 18 m over the street */

  /* THE KIT ADDITIONS, built once here and lifted into assets/js/kit/ by the retro the same day.
   * Conventions of txkit.js: metres, y up, origin on the ground at the footprint centre, front
   * toward +z, materials through K.mat.
   *
   * fly_vial STATES:
   *   climbing  adults spread up the wall to near the plug, the healthy picture
   *   down      adults on the food surface and the low wall, a few on their backs: the gene disabled
   *   partial   adults on the lower half of the wall only: a patient's variant, restored in part
   *   empty     food and plug and no adults, a fresh vial
   */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.fly_vial) return;
    var R_OUT = 0.0125, H = 0.095, WALL = 0.0009, FOOD = 0.021;

    /* cornmeal: a granular mid tone, light grains and dark husk flecks, so the food has a body */
    var MEAL = null;
    function meal() {
      if (MEAL) return MEAL;
      var c = document.createElement('canvas'); c.width = c.height = 256; var x = c.getContext('2d'), r = K.rng(911);
      x.fillStyle = '#c9c2b4'; x.fillRect(0, 0, 256, 256);
      for (var i = 0; i < 5200; i++) { var v = r(); x.fillStyle = v < 0.45 ? 'rgba(255,248,230,0.55)' : v < 0.8 ? 'rgba(120,96,64,0.45)' : 'rgba(70,48,28,0.6)'; var sz = 1 + r() * 2.4; x.fillRect(r() * 256, r() * 256, sz, sz); }
      MEAL = new THREE.CanvasTexture(c); MEAL.wrapS = MEAL.wrapT = THREE.RepeatWrapping; MEAL.repeat.set(5, 1.4); MEAL.colorSpace = THREE.SRGBColorSpace;
      return MEAL;
    }
    function M() {
      return {
        glass: K.mat('fv-glass4', { color: 0xf6f9fb, roughness: 0.04, metalness: 0, transparent: true, opacity: 0.17, envMapIntensity: 1.3, clearcoat: 1, clearcoatRoughness: 0.03, specularIntensity: 1, side: THREE.DoubleSide, depthWrite: false }, true),
        rim: K.mat('fv-rim', { color: 0xe8eef2, roughness: 0.08, metalness: 0, transmission: 0.7, thickness: 0.003, ior: 1.59, transparent: true }, true),
        food: K.mat('fv-food3', { color: 0xc89a55, roughness: 0.86, metalness: 0, emissive: 0x6a3a10, emissiveIntensity: 0.06, map: meal() }),
        foodTop: K.mat('fv-foodtop', { color: 0x8d5f22, roughness: 0.75, metalness: 0 }),
        yeast: K.mat('fv-yeast', { color: 0xe9dcc0, roughness: 0.9 }),
        plug: K.mat('fv-plug2', { color: 0xece4d2, roughness: 1, metalness: 0, emissive: 0xf3d9a8, emissiveIntensity: 0.06 }),
        pupa: K.mat('fv-pupa3', { color: 0xb38d58, roughness: 0.55 }),
        body: K.mat('fv-body3', { color: 0x5a4126, roughness: 0.4 }),
        leg: K.mat('fv-leg', { color: 0x2a1d12, roughness: 0.6 }),
        abdo: K.mat('fv-abdo2', { color: 0x2c1f14, roughness: 0.4 }),
        eye: K.mat('fv-eye', { color: 0x9e1b14, roughness: 0.35, metalness: 0.1 }),
        wing: K.mat('fv-wing3', { color: 0xb9c2c9, roughness: 0.25, metalness: 0, transparent: true, opacity: 0.78, side: THREE.DoubleSide, depthWrite: false }),
        tape: K.mat('fv-tape', { color: 0xf1efe8, roughness: 0.8 }),
        accent: K.mat('fv-accent5', { color: 0x14503a, emissive: 0x2fd896, emissiveIntensity: 0.85, roughness: 0.55 }),
        ink: K.mat('fv-ink', { color: 0x1f2a3a, roughness: 0.7 })
      };
    }

    /* one adult fly, about 2.5 mm, head toward +y, back toward +z (away from the surface it stands
     * on): thorax, abdomen, head, two red eyes and two folded wings. */
    function fly(MM, rng, onBack) {
      var f = new THREE.Group(), sp = function (r, sx, sy, sz, m, x, y, z) {
        var s = new THREE.Mesh(new THREE.SphereGeometry(r, 10, 8), m); s.scale.set(sx, sy, sz); s.position.set(x, y, z); s.castShadow = true; f.add(s); return s;
      };
      sp(0.00042, 1, 1.25, 0.95, MM.body, 0, 0.0002, 0.0004);
      sp(0.0005, 1.12, 1.4, 0.95, MM.abdo, 0, -0.00075, 0.00036);
      sp(0.00032, 1.15, 0.9, 1, MM.body, 0, 0.00078, 0.00038);
      sp(0.00024, 0.9, 1.1, 0.9, MM.eye, 0.00027, 0.00084, 0.00044);
      sp(0.00024, 0.9, 1.1, 0.9, MM.eye, -0.00027, 0.00084, 0.00044);
      [-1, 1].forEach(function (s) {
        /* the wings folded flat over the abdomen, a little apart at the tips, as a resting fly holds them */
        var wg = new THREE.Mesh(new THREE.CircleGeometry(0.00075, 18), MM.wing);
        wg.scale.set(0.5, 1.4, 1); wg.position.set(s * 0.0002, -0.00072, 0.00086); wg.rotation.z = s * 0.14; f.add(wg);
      });
      /* six legs under the thorax, out to the sides, so a fly on its back reads as one */
      for (var l = 0; l < 6; l++) {
        var side = l < 3 ? -1 : 1, k = l % 3, lg = new THREE.Mesh(new THREE.CylinderGeometry(0.00006, 0.00004, 0.0008, 5), MM.leg);
        lg.position.set(side * 0.0004, 0.0003 - k * 0.00032, 0.0001); lg.rotation.z = side * (1.05 + (k - 1) * 0.35); lg.rotation.x = 0.5; f.add(lg);
      }
      if (onBack) f.rotation.y = Math.PI;
      return f;
    }

    K.define('fly_vial', {
      size: [0.026, 0.11, 0.026],
      options: { state: 'climbing', flies: 18, pupae: 4, plug: true, tape: false, tapeYaw: 0, tapeArc: 3.84, climbTop: 0.42, droplets: 0, flyScale: 1.6, seed: 1 },
      note: 'A clear polystyrene fruit fly culture vial (25 mm across, 95 mm tall) with cornmeal food at its foot, a cellulose plug, pupae on the wall and adult flies about 2.5 mm long. state climbing \\ down \\ partial \\ empty sets where the adults are. tape true wraps a strip of the accent tape at the shoulder. Front +z.',
      make: function (o) {
        var MM = M(), g = new THREE.Group(), rng = K.rng(+o.seed || 1);
        var rin = R_OUT - WALL;
        /* the vial: a lathe of the wall with a rounded foot and a lip at the mouth */
        var prof = [[0.0001, 0], [R_OUT - 0.0015, 0], [R_OUT - 0.0004, 0.0003], [R_OUT, 0.0015], [R_OUT, H - 0.001], [R_OUT + 0.0004, H - 0.0006], [R_OUT + 0.0004, H], [rin, H], [rin, 0.0018], [rin - 0.0012, 0.0011], [0.0001, 0.0011]];
        var wall = new THREE.Mesh(new THREE.LatheGeometry(prof.map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 48), MM.glass);
        wall.castShadow = true; wall.receiveShadow = false; g.add(wall);
        /* the food, its surface a shade darker and worked, a dusting of yeast on top */
        var food = new THREE.Mesh(new THREE.CylinderGeometry(rin - 0.0001, rin - 0.0001, FOOD - 0.0011, 64), MM.food);
        food.position.y = 0.0011 + (FOOD - 0.0011) / 2; food.receiveShadow = true; g.add(food);
        var top = new THREE.Mesh(new THREE.CircleGeometry(rin - 0.0001, 40), MM.foodTop);
        top.rotation.x = -Math.PI / 2; top.position.y = FOOD + 0.00005; top.receiveShadow = true; g.add(top);
        for (var y = 0; y < 26; y++) {
          var a = rng() * Math.PI * 2, rr = Math.sqrt(rng()) * (rin - 0.0012);
          var gr = new THREE.Mesh(new THREE.SphereGeometry(0.00028 + rng() * 0.0002, 6, 5), MM.yeast);
          gr.scale.y = 0.45; gr.position.set(Math.cos(a) * rr, FOOD + 0.0001, Math.sin(a) * rr); g.add(gr);
        }
        /* the plug, pushed in a third of its length, its top a little proud and fibrous */
        if (o.plug !== false) {
          var pl = new THREE.Mesh(new THREE.CylinderGeometry(rin * 1.01, rin * 0.99, 0.03, 64, 6), MM.plug);
          var pos = pl.geometry.attributes.position;
          for (var i = 0; i < pos.count; i++) {
            var px = pos.getX(i), pz = pos.getZ(i), d = Math.hypot(px, pz);
            if (d > 0.0001) { var k = 1 + (rng() - 0.5) * 0.02; pos.setX(i, px * k); pos.setZ(i, pz * k); }
          }
          pl.geometry.computeVertexNormals();
          pl.position.y = H - 0.008; pl.castShadow = true; g.add(pl);
          var cap = new THREE.Mesh(new THREE.SphereGeometry(rin * 1.02, 64, 16, 0, Math.PI * 2, 0, Math.PI / 2), MM.plug);
          cap.scale.y = 0.28; cap.position.y = H + 0.007; cap.castShadow = true; g.add(cap);
        }
        /* pupae on the wall a little above the food, as larvae climb to pupate */
        for (var p = 0; p < (+o.pupae || 0); p++) {
          var pa = rng() * Math.PI * 2, py = FOOD + 0.003 + rng() * 0.01;
          var pu = new THREE.Mesh(new THREE.CapsuleGeometry(0.00055, 0.0019, 4, 8), MM.pupa);
          pu.position.set(Math.cos(pa) * (rin - 0.00045), py, Math.sin(pa) * (rin - 0.00045));
          pu.rotation.z = (rng() - 0.5) * 0.6; g.add(pu);
        }
        /* condensation on the inside of the wall above the food, as a sealed vial carries in warm
         * light: small clear beads, denser low */
        var nd = o.droplets == null ? 0 : +o.droplets;
        if (nd) {
          var dm = K.mat('fv-drop', { color: 0xffffff, roughness: 0.05, metalness: 0, transparent: true, opacity: 0.55, envMapIntensity: 2.5 });
          var dg = new THREE.SphereGeometry(1, 8, 6, 0, Math.PI * 2, 0, Math.PI / 2); dg.rotateX(Math.PI / 2);
          var list = [];
          for (var q = 0; q < nd; q++) {
            var qa = rng() * Math.PI * 2, qy = FOOD + 0.002 + Math.pow(rng(), 1.6) * (H - FOOD - 0.02), rr2 = 0.0003 + Math.pow(rng(), 2) * 0.0006;
            list.push([Math.cos(qa) * (rin - 0.00005), qy, Math.sin(qa) * (rin - 0.00005), -qa + Math.PI / 2, rr2]);
          }
          var im = new THREE.InstancedMesh(dg, dm, list.length), mtx = new THREE.Matrix4(), qt = new THREE.Quaternion(), sc = new THREE.Vector3();
          list.forEach(function (d, k) {
            qt.setFromAxisAngle(new THREE.Vector3(0, 1, 0), d[3] + Math.PI);
            sc.set(d[4], d[4], d[4] * 0.5); mtx.compose(new THREE.Vector3(d[0], d[1], d[2]), qt, sc); im.setMatrixAt(k, mtx);
          });
          g.add(im);
        }
        /* the adults, by state */
        /* bands on the open wall between the food and the plug's foot, by state, so the state reads
         * as a POSITION at thumb size: climbing in the top 40 percent, partial in a band 45 to 65
         * percent down, down on the food with a few on their backs */
        var st = o.state || 'climbing', nF = st === 'empty' ? 0 : (+o.flies || 0), PLUGF = H - 0.023, OPEN = PLUGF - FOOD;
        var band = st === 'climbing' ? [PLUGF - OPEN * (+o.climbTop || 0.42), PLUGF - 0.003] : st === 'partial' ? [PLUGF - OPEN * 0.68, PLUGF - OPEN * 0.43] : [FOOD + 0.002, FOOD + 0.007];
        var pFood = st === 'down' ? 0.85 : st === 'partial' ? 0.08 : 0.0, fs = +o.flyScale || 1.6;
        for (var f = 0; f < nF; f++) {
          var fa = (o.front ? (rng() - 0.5) * 2.2 : rng() * Math.PI * 2) + Math.PI / 2, onFood = rng() < pFood;
          var ff = fly(MM, rng, st === 'down' && onFood && rng() < 0.35);
          ff.scale.setScalar(fs);
          if (onFood) {
            var fr = (0.35 + 0.65 * Math.sqrt(rng())) * (rin - 0.0018 * fs);
            ff.rotation.x = -Math.PI / 2; ff.rotation.z = rng() * Math.PI * 2;
            ff.position.set(Math.cos(fa) * fr, FOOD + 0.0004 * fs, Math.sin(fa) * fr);
          } else {
            var fy = band[0] + rng() * (band[1] - band[0]);
            ff.position.set(Math.cos(fa) * (rin - 0.0006 * fs), fy, Math.sin(fa) * (rin - 0.0006 * fs));
            ff.rotation.y = -fa - Math.PI / 2;
            ff.rotateZ((rng() - 0.5) * (st === 'climbing' ? 0.5 : 1.4));
          }
          g.add(ff);
        }
        /* the tape at the shoulder: a wrapped strip of the accent, as a bench marks one line */
        if (o.tape) {
          /* wrapped 220 degrees round the glass and centred on tapeYaw (0 faces +z), so both its ends
           * turn out of sight past the silhouette; over the plug, where it hides no fly */
          var ty = +o.tapeYaw || 0;
          var t = new THREE.Mesh(new THREE.CylinderGeometry(R_OUT + 0.00025, R_OUT + 0.00025, 0.008, 72, 1, true, ty - (+o.tapeArc || 3.84) / 2, +o.tapeArc || 3.84), MM.accent);
          t.position.y = H - 0.0125; g.add(t);
        }
        g.userData.mouth = { x: 0, y: H, z: 0 };
        g.userData.food = FOOD;
        return g;
      }
    });

    /* a vial tray: a grey cardboard flat with round wells, cols by rows at 30 mm pitch, the vials
     * standing in it. Front +z. */
    K.define('vial_tray', {
      size: [0.3, 0.012, 0.3],
      options: { cols: 10, rows: 1, pitch: 0.03 },
      note: 'A shallow cardboard vial flat, cols x rows wells at pitch metres, 12 mm deep. Vials stand sunk in it with their foot 6 mm above the bench.',
      make: function (o) {
        var g = new THREE.Group(), c = +o.cols || 10, r = +o.rows || 1, p = +o.pitch || 0.03;
        var card = K.mat('vt-card2', { color: 0xb08a5a, roughness: 0.95 });
        var b = TXT.roundedBox(c * p + 0.012, 0.012, r * p + 0.012, 0.002, card); b.position.y = 0.006; b.castShadow = true; b.receiveShadow = true; g.add(b);
        /* a dark well under each vial, so a vial reads as seated in the flat rather than on it */
        var well = K.mat('vt-well', { color: 0x2a2620, roughness: 1 });
        for (var i = 0; i < c; i++) for (var j = 0; j < r; j++) {
          var w = new THREE.Mesh(new THREE.CircleGeometry(0.0136, 28), well); w.rotation.x = -Math.PI / 2;
          w.position.set(-(c - 1) * p / 2 + i * p, 0.0122, -(r - 1) * p / 2 + j * p); g.add(w);
        }
        g.userData.well = function (i, j) { return [-(c - 1) * p / 2 + i * p, 0.006, -(r - 1) * p / 2 + j * p]; };
        return g;
      }
    });
  };

  /* THE SILL, the bench and the window every exterior frame stands at: a painted concrete sill
   * `w` metres wide and 0.32 deep at N.SILL_Y, its outer edge at z = 0, two aluminium mullions
   * either side, nothing overhead, so the sky is the sky. Returns the group. */
  N.sill = function (K, R, TXT, o) {
    o = o || {};
    var T = N.T, g = new T.Group(), w = o.w || 2.4, y = N.SILL_Y;
    var ct = K.tex('concrete'); ct.repeat.set(1, 1);
    var paint = K.mat('vl-sill3', { color: o.color || 0xe4d9c6, roughness: 0.72, map: ct, emissive: 0x3a2a18, emissiveIntensity: 0.35 });
    var alu = K.mat('vl-alu', { color: 0xaeb3b8, roughness: 0.35, metalness: 0.8 });
    var top = TXT.roundedBox(w, 0.04, 0.32, 0.006, paint); K.uvBox(top.geometry, 0.14); top.position.set(0, y - 0.02, 0.16); top.receiveShadow = true; top.castShadow = true; g.add(top);
    var face = new T.Mesh(new T.BoxGeometry(w, y - 0.04, 0.3), K.mat('vl-wall', { color: 0x8e8a83, roughness: 0.9 }));
    face.position.set(0, (y - 0.04) / 2, 0.18); face.receiveShadow = true; g.add(face);
    (o.mullions || [-0.95, 0.95]).forEach(function (x) {
      var m = TXT.roundedBox(0.06, 2.4, 0.09, 0.006, alu); m.position.set(x, y + 1.2, 0.02); m.castShadow = true; g.add(m);
    });
    var stool = TXT.roundedBox(w, 0.05, 0.08, 0.004, alu); stool.position.set(0, y + 0.01, 0.0); g.add(stool);
    TXT.add(R, g);
    return g;
  };

  /* THE STREET BELOW AND THE CITY BEYOND: a ground, a scatter of live oak and crape myrtle along a
   * medical district's streets, mid rise blocks, and the far skyline in haze. Every exterior frame
   * calls it, so the place is the same place on every frame. `look` is the direction the camera
   * faces, [dx, dz], so the near blocks stand where the camera can see them. */
  N.city = function (K, R, TXT, o) {
    o = o || {};
    var T = N.T, rng = K.rng(o.seed || 5);
    var sk = K.make('city_skyline', { city: 'houston', seed: o.skySeed || 3 });
    var d = o.skyDist || 5200, lk = o.look || [-1, 0], ln = Math.hypot(lk[0], lk[1]);
    sk.position.set(lk[0] / ln * d, 0, lk[1] / ln * d); sk.rotation.y = Math.atan2(-lk[0], -lk[1]); TXT.add(R, sk);
    /* the medical district between the sill and the skyline: kit hospital towers, never slabs */
    for (var i = 0; i < (o.blocks || 7); i++) {
      var dist = 420 + rng() * 1300, ang = Math.atan2(lk[1], lk[0]) + (rng() - 0.5) * 1.3;
      var hb = K.make('hospital', { seed: 60 + i });
      hb.position.set(Math.cos(ang) * dist, 0, Math.sin(ang) * dist); hb.rotation.y = Math.atan2(-Math.cos(ang), -Math.sin(ang)) + (rng() - 0.5) * 0.5; TXT.add(R, hb);
    }
    for (var t = 0; t < (o.trees || 40); t++) {
      var td = 160 + rng() * 260, ta = Math.atan2(lk[1], lk[0]) + (rng() - 0.5) * 1.9;
      var tr = K.make(rng() < 0.75 ? 'live_oak' : 'crape_myrtle', { seed: 30 + t, height: 9 + rng() * 6 });
      tr.position.set(Math.cos(ta) * td, 0, Math.sin(ta) * td); TXT.add(R, tr);
    }
  };

  /* THE ROOM INSIDE THE SAME BUILDING, for the four interior frames: a consult room with its
   * window on the west wall, so the deck's one low sun comes in from the camera's left exactly as it
   * falls on the coping outside. A desk under the window light, a chair, papers. Each frame places the
   * vial, the camera and whatever the frame is about. Returns the desk top height and the desk. */
  N.ROOM = { w: 5.2, d: 4.6, h: 2.9, floor: 'concrete', wall: 0x8f8371, window: null, ceiling: false, light: 1.0 };
  /* the frame calls TXT.interior(R, VL.ROOM) itself, so the room is in the frame's own code, then
   * this furnishes it */
  N.room = function (K, R, TXT, o) {
    o = o || {};
    /* the low sun through the west window: a warm spot from the window's own position, raking the
     * desk from the left as the declared key does outside. The wall stops the key itself, so this
     * stands in for the beam that comes through the glass, in the key's colour and direction. */
    /* THE WEST WINDOW, out of frame on the camera's left, and the low sun through it. The wall
     * itself casts nothing in TXT.interior, so an unseen occluder stands in its plane with the
     * window cut out of it and a cross of aluminium bars in the opening: the sun lays one bright
     * barred rectangle across the desk and the back wall, which is the window, seen by its light. */
    /* The room's own walls cast in TXT.interior, so the sun is a spot just inside the west wall,
     * and half a metre in front of it an unseen occluder carries the window's opening and its cross
     * of bars, scaled to that distance: the sun lays one bright barred rectangle across the desk,
     * which is the window, seen by its light. */
    var T = N.T, X = -1.9, sp = o.sunAt || [-2.4, 2.45, -0.3], tg = o.sunTo || [0.4, 0.78, -1.3];
    var tt = (X - sp[0]) / (tg[0] - sp[0]), wz = sp[2] + (tg[2] - sp[2]) * tt, wy = sp[1] + (tg[1] - sp[1]) * tt;
    var WW = o.winW || 0.42, WH = o.winH || 0.36;
    var occ = new T.Shape(); occ.moveTo(-2.3, 0); occ.lineTo(2.3, 0); occ.lineTo(2.3, 2.9); occ.lineTo(-2.3, 2.9); occ.lineTo(-2.3, 0);
    var hole = new T.Path(); hole.moveTo(wz - WW / 2, wy - WH / 2); hole.lineTo(wz - WW / 2, wy + WH / 2); hole.lineTo(wz + WW / 2, wy + WH / 2); hole.lineTo(wz + WW / 2, wy - WH / 2); hole.lineTo(wz - WW / 2, wy - WH / 2);
    occ.holes.push(hole);
    var om = new T.MeshBasicMaterial({ colorWrite: false, depthWrite: false, side: T.DoubleSide });
    var wallOcc = new T.Mesh(new T.ShapeGeometry(occ), om); wallOcc.rotation.y = Math.PI / 2; wallOcc.position.set(X, 0, 0);
    wallOcc.scale.x = -1; wallOcc.castShadow = o.occ !== false; R.scene.add(wallOcc);
    [[wy, 0.012, WH]].concat(o.hbar === false ? [] : [[wy + WH * 0.12, WW, 0.012]]).forEach(function (b) {
      var bar = new T.Mesh(new T.BoxGeometry(0.01, b[2], b[1]), om); bar.position.set(X, b[0], wz); bar.castShadow = true; R.scene.add(bar);
    });
    var sun = new T.SpotLight(0xffc98a, o.beam == null ? 70 : o.beam, 0, 0.6, 0.05, 2);
    sun.position.set(sp[0], sp[1], sp[2]); sun.target.position.set(tg[0], tg[1], tg[2]); sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048); sun.shadow.radius = 2; sun.shadow.bias = -0.0004; sun.shadow.camera.near = 0.1; R.scene.add(sun, sun.target);
    var bounce = new T.PointLight(0xffe6c8, 6, 7, 1.6); bounce.position.set(1.2, 2.2, 0.8); R.scene.add(bounce);
    var desk = K.make('desk', { seed: 3 });
    desk.position.set(o.deskX == null ? 0.2 : o.deskX, 0, o.deskZ == null ? -1.25 : o.deskZ); TXT.add(R, desk); TXT.contact(R, desk);
    var top = new N.T.Box3().setFromObject(desk).max.y;
    /* the walls take a hand trowelled plaster, and two filing cabinets stand at the back wall, so
     * the room has a surface rather than a colour */
    var wallM = K.mat('vl-plaster2', { color: 0x9a8d79, roughness: 0.95 });
    var right = new N.T.Mesh(new N.T.BoxGeometry(0.01, 2.9, 4.4), wallM); right.position.set(2.49, 1.45, 0); right.receiveShadow = true; R.scene.add(right);
    /* the desk's varnish takes no violet off the sky: a matte top */
    desk.traverse(function (m) { if (m.isMesh && m.material && m.material.isMeshStandardMaterial) { m.material = m.material.clone(); m.material.envMapIntensity = 0.35; m.material.roughness = Math.max(m.material.roughness, 0.62); } });
    if (o.cabinets !== false) (o.cabX || [1.55, 1.95]).forEach(function (x, i) { var fc = K.make('filing_cabinet', { seed: 8 + i }); fc.position.set(x, 0, -1.9); TXT.add(R, fc); TXT.contact(R, fc); });
    if (o.papers !== false) {
      var pp = K.make('document_stack', { seed: 5 }); pp.position.set(desk.position.x - 0.48, top, desk.position.z - 0.08); pp.rotation.y = 0.15; TXT.add(R, pp);
    }
    if (o.chair !== false) {
      var ch = K.make('office_chair', { seed: 4 }); ch.position.set(desk.position.x + (o.chairX || 0.1), 0, desk.position.z + (o.chairZ || 0.85)); ch.rotation.y = Math.PI + (o.chairYaw || 0.2); TXT.add(R, ch); TXT.contact(R, ch);
    }
    return { top: top, desk: desk };
  };

  /* A SCREEN THE FRAME DRAWS. The kit monitor's own display carries no chosen content, so a frame
   * that has something to show switches it off and lays its own canvas over the glass, here, at the
   * kit's own screen geometry. */
  N.screen = function (THREE, mon, canvas, inches, glow) {
    var diag = (inches || 27) * 0.0254, sw = diag * 16 / Math.hypot(16, 9), sh = diag * 9 / Math.hypot(16, 9);
    var tex = new THREE.CanvasTexture(canvas); tex.colorSpace = THREE.SRGBColorSpace;
    var m = new THREE.MeshStandardMaterial({ color: 0x000000, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: glow || 0.9, roughness: 0.25 });
    var pl = new THREE.Mesh(new THREE.PlaneGeometry(sw, sh), m);
    pl.position.set(0, -(sh + 0.03) / 2 + 0.026 + sh / 2, 0.0068);
    var head = null;
    mon.traverse(function (c) { if (!head && c.isGroup && Math.abs(c.rotation.x + 0.06) < 0.001) head = c; });
    if (!head) throw new Error('VL.screen: the monitor head was not found');
    head.add(pl);
    N.lastScreen = pl;
    return pl;
  };

  /* THE HERO, the same call on every frame. */
  N.vial = function (K, o) {
    o = o || {};
    return K.make('fly_vial', { state: o.state || 'climbing', flies: o.flies == null ? 18 : o.flies, pupae: o.pupae == null ? 4 : o.pupae, tape: !!o.tape, tapeYaw: o.tapeYaw || 0, tapeArc: o.tapeArc || 3.84, climbTop: o.climbTop || 0.42, front: !!o.front, flyScale: o.flyScale || 1.6, seed: o.seed || 1, droplets: o.droplets == null ? 0 : o.droplets });
  };

  /* A world point to frame CSS px, through the frame's own camera. */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };

  /* THE MACRO RIG. A vial is ten centimetres tall and the sun is the deck's key, so the shadow
   * camera is shrunk to the bench around the target, or a 2048 map spreads over 18 m and the vial
   * casts nothing. Colour and intensity stay the world's. */
  N.rigSpec = function (W, size) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 0.35, mapSize: 2048, radius: 4 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 3, shadowFar: o.shadowFar || 8, normalBias: o.normalBias == null ? 0.0006 : o.normalBias };
  };

  /* THE BLUR THE LENS GIVES. A macro lens at this distance holds a few millimetres in focus and
   * melts the city, so everything beyond the sill is softened in 2D after the snapshot, by a band
   * the frame names in CSS px. A grade on a render, never a screen. */
  N.lensBlur = function (cx, y0, y1, px, keep) {
    var art = cx.canvas, src = document.createElement('canvas'); src.width = art.width; src.height = art.height;
    var sx = src.getContext('2d'); sx.filter = 'blur(' + (px * 2) + 'px)'; sx.drawImage(art, 0, 0); sx.filter = 'none';
    var mask = document.createElement('canvas'); mask.width = art.width; mask.height = art.height;
    var mx = mask.getContext('2d'), gr = mx.createLinearGradient(0, y0 * 2, 0, y1 * 2);
    gr.addColorStop(0, 'rgba(0,0,0,1)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
    mx.fillStyle = gr; mx.fillRect(0, 0, mask.width, mask.height);
    /* the subject stays sharp: each keep rect [x, y, w, h] in CSS px is cut out of the blur with a
     * feathered edge, because the plane of focus is the vial and never the city behind it */
    (keep || []).forEach(function (k) {
      mx.save(); mx.globalCompositeOperation = 'destination-out'; mx.filter = 'blur(' + (k[4] || 10) + 'px)';
      mx.fillStyle = '#000'; mx.fillRect(k[0] * 2, k[1] * 2, k[2] * 2, k[3] * 2); mx.restore();
    });
    sx.globalCompositeOperation = 'destination-in'; sx.drawImage(mask, 0, 0);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.drawImage(src, 0, 0); cx.restore();
  };

  /* THE SKY BAND THE TYPE STANDS IN, never over 0.45 alpha, darkening a little behind light type. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector('.dek'), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    /* the band holds its full weight past the last line of type, so no line sits on the turn of the fade */
    if (bottom != null) bottom += o.pad == null ? 80 : o.pad;
    var a = o.a == null ? 0.22 : Math.min(0.45, o.a), c = o.rgb || '24,22,30';
    if (bottom != null && a > 0) {
      var fade = o.fade || 180, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, 'rgba(' + c + ',' + (a * 0.8) + ')');
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), 'rgba(' + c + ',' + a + ')');
      g.addColorStop(1, 'rgba(' + c + ',0)');
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

  /* THE POST STEPS every frame takes before its grade. The frame still calls TXDECK.finish itself,
   * last. A dark band under the footer, never a box and never over 0.45. */
  N.post = function (cx, o) {
    o = o || {};
    N.atmosphere(cx, { a: o.a == null ? 0.2 : o.a, to: o.to, fade: o.fade, rgb: o.rgb, pad: o.pad });
    N.soften(cx, o.type || ['.kick', '.hook', '.dek'], { blur: o.typeBlur || 8, pad: 8, feather: o.typeFeather || 26 });
    N.soften(cx, ['.tx-site', '.src'], { blur: o.siteBlur || 9, pad: 14, feather: 40 });
    var y0 = N.H - (o.veilH || 220), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, 'rgba(14,12,16,' + (Math.min(0.45, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ')'); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };

  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) {
      var n = (rnd() + rnd() - 1) * 1.2;
      d[i] += n; d[i + 1] += n; d[i + 2] += n;
    }
    cx.putImageData(id, 0, 0);
  };

  /* THE SHELL EVERY FRAME SHARES: the type styles, the furniture, the fit of the hook. */
  N.CSS = [
    '* { margin:0; padding:0; box-sizing:border-box; }',
    'html, body { width:1080px; height:1350px; overflow:hidden; background:#20232B; }',
    'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
    'canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }',
    '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:800; line-height:0.98; letter-spacing:-0.01em; color:#FBF7EF; font-variation-settings:"opsz" 144; z-index:10; }',
    '.dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:#F4F0E8; z-index:10; }',
    '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:#EFEBE4; white-space:nowrap; z-index:20; }',
    '.hook, .dek, .tx-site, .kick, .src, .cap, .lab { text-shadow:0 0 2px rgba(20,14,10,0.5), 0 1px 12px rgba(20,14,10,0.4); }'
  ].join('\n');
  N.start = function (o) {
    var st = document.createElement('style'); st.textContent = N.CSS;
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: '#EFEBE4' });
    TX.fitText(document.getElementById('hook'), o.fit || { min: 96, max: 128, maxLines: 2 });
    N.follow();
  };
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE;
    await document.fonts.ready;
    N.start(o);
    var TXT = typeof bench === 'function' ? bench(THREE) : bench, K = initKit(THREE, TXT);
    N.installKit(K, THREE, TXT);
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
  };
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    return TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 30, near: o.near || 0.005, far: o.far || 12000 });
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

  global.VL = N;
})(this);
