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
    light: { az: -78, el: 7 },
    sky: { preset: "goldenHour", fogDensity: 0.0012, clouds: 0.22 },
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

    function M() {
      return {
        glass: K.mat('fv-glass3', { color: 0xf6f9fb, roughness: 0.02, metalness: 0, transparent: true, opacity: 0.26, envMapIntensity: 3.2, clearcoat: 1, clearcoatRoughness: 0.03, specularIntensity: 1, side: THREE.DoubleSide, depthWrite: false }, true),
        rim: K.mat('fv-rim', { color: 0xe8eef2, roughness: 0.08, metalness: 0, transmission: 0.7, thickness: 0.003, ior: 1.59, transparent: true }, true),
        food: K.mat('fv-food2', { color: 0xb8853a, roughness: 0.86, metalness: 0, emissive: 0x6a3a10, emissiveIntensity: 0.08 }),
        foodTop: K.mat('fv-foodtop', { color: 0x8d5f22, roughness: 0.75, metalness: 0 }),
        yeast: K.mat('fv-yeast', { color: 0xe9dcc0, roughness: 0.9 }),
        plug: K.mat('fv-plug2', { color: 0xece4d2, roughness: 1, metalness: 0, emissive: 0xf3d9a8, emissiveIntensity: 0.06 }),
        pupa: K.mat('fv-pupa2', { color: 0x4e2f16, roughness: 0.5 }),
        body: K.mat('fv-body2', { color: 0x7a5a36, roughness: 0.45 }),
        abdo: K.mat('fv-abdo', { color: 0x4a3420, roughness: 0.45 }),
        eye: K.mat('fv-eye', { color: 0x9e1b14, roughness: 0.35, metalness: 0.1 }),
        wing: K.mat('fv-wing2', { color: 0xeef2f5, roughness: 0.15, metalness: 0, transparent: true, opacity: 0.6, side: THREE.DoubleSide, depthWrite: false }),
        tape: K.mat('fv-tape', { color: 0xf1efe8, roughness: 0.8 }),
        accent: K.mat('fv-accent', { color: N.ACCENT, roughness: 0.6 }),
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
      sp(0.00048, 1, 1.9, 0.9, MM.abdo, 0, -0.00085, 0.00036);
      sp(0.00032, 1.15, 0.9, 1, MM.body, 0, 0.00078, 0.00038);
      sp(0.00024, 0.9, 1.1, 0.9, MM.eye, 0.00027, 0.00084, 0.00044);
      sp(0.00024, 0.9, 1.1, 0.9, MM.eye, -0.00027, 0.00084, 0.00044);
      [-1, 1].forEach(function (s) {
        var wg = new THREE.Mesh(new THREE.CircleGeometry(0.00075, 14), MM.wing);
        wg.scale.set(0.6, 1.45, 1); wg.position.set(s * 0.00042, -0.0008, 0.00088); wg.rotation.z = s * 0.38; wg.rotation.x = -0.12; f.add(wg);
      });
      if (onBack) f.rotation.y = Math.PI;
      return f;
    }

    K.define('fly_vial', {
      size: [0.026, 0.11, 0.026],
      options: { state: 'climbing', flies: 18, pupae: 9, plug: true, tape: false, seed: 1 },
      note: 'A clear polystyrene fruit fly culture vial (25 mm across, 95 mm tall) with cornmeal food at its foot, a cellulose plug, pupae on the wall and adult flies about 2.5 mm long. state climbing \\ down \\ partial \\ empty sets where the adults are. tape true wraps a strip of the accent tape at the shoulder. Front +z.',
      make: function (o) {
        var MM = M(), g = new THREE.Group(), rng = K.rng(+o.seed || 1);
        var rin = R_OUT - WALL;
        /* the vial: a lathe of the wall with a rounded foot and a lip at the mouth */
        var prof = [[0.0001, 0], [R_OUT - 0.0015, 0], [R_OUT - 0.0004, 0.0003], [R_OUT, 0.0015], [R_OUT, H - 0.001], [R_OUT + 0.0004, H - 0.0006], [R_OUT + 0.0004, H], [rin, H], [rin, 0.0018], [rin - 0.0012, 0.0011], [0.0001, 0.0011]];
        var wall = new THREE.Mesh(new THREE.LatheGeometry(prof.map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 48), MM.glass);
        wall.castShadow = true; wall.receiveShadow = false; g.add(wall);
        /* the food, its surface a shade darker and worked, a dusting of yeast on top */
        var food = new THREE.Mesh(new THREE.CylinderGeometry(rin - 0.0001, rin - 0.0001, FOOD - 0.0011, 40), MM.food);
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
          var pl = new THREE.Mesh(new THREE.CylinderGeometry(rin * 1.01, rin * 0.99, 0.03, 28, 6), MM.plug);
          var pos = pl.geometry.attributes.position;
          for (var i = 0; i < pos.count; i++) {
            var px = pos.getX(i), pz = pos.getZ(i), d = Math.hypot(px, pz);
            if (d > 0.0001) { var k = 1 + (rng() - 0.5) * 0.05; pos.setX(i, px * k); pos.setZ(i, pz * k); }
          }
          pl.geometry.computeVertexNormals();
          pl.position.y = H - 0.008; pl.castShadow = true; g.add(pl);
          var cap = new THREE.Mesh(new THREE.SphereGeometry(rin * 1.02, 24, 10, 0, Math.PI * 2, 0, Math.PI / 2), MM.plug);
          cap.scale.y = 0.28; cap.position.y = H + 0.007; cap.castShadow = true; g.add(cap);
        }
        /* pupae on the wall a little above the food, as larvae climb to pupate */
        for (var p = 0; p < (+o.pupae || 0); p++) {
          var pa = rng() * Math.PI * 2, py = FOOD + 0.006 + rng() * 0.022;
          var pu = new THREE.Mesh(new THREE.CapsuleGeometry(0.00055, 0.0019, 4, 8), MM.pupa);
          pu.position.set(Math.cos(pa) * (rin - 0.00045), py, Math.sin(pa) * (rin - 0.00045));
          pu.rotation.z = (rng() - 0.5) * 0.6; g.add(pu);
        }
        /* the adults, by state */
        var st = o.state || 'climbing', nF = st === 'empty' ? 0 : (+o.flies || 0);
        var hi = st === 'climbing' ? H - 0.018 : st === 'partial' ? FOOD + 0.03 : FOOD + 0.006;
        for (var f = 0; f < nF; f++) {
          var fa = rng() * Math.PI * 2, onFood = st === 'down' ? rng() < 0.7 : st === 'partial' ? rng() < 0.25 : rng() < 0.08;
          var ff = fly(MM, rng, st === 'down' && rng() < 0.3);
          if (onFood) {
            var fr = Math.sqrt(rng()) * (rin - 0.0018);
            ff.rotation.x = -Math.PI / 2; ff.rotation.z = rng() * Math.PI * 2;
            ff.position.set(Math.cos(fa) * fr, FOOD + 0.0004, Math.sin(fa) * fr);
          } else {
            var fy = FOOD + 0.004 + rng() * (hi - FOOD - 0.004);
            ff.position.set(Math.cos(fa) * (rin - 0.0006), fy, Math.sin(fa) * (rin - 0.0006));
            ff.rotation.y = Math.atan2(-Math.cos(fa), -Math.sin(fa)) + Math.PI / 2;
            ff.rotation.y = -fa - Math.PI / 2;
            ff.rotateZ((rng() - 0.5) * (st === 'climbing' ? 0.5 : 1.4));
          }
          g.add(ff);
        }
        /* the tape at the shoulder: a wrapped strip of the accent, as a bench marks one line */
        if (o.tape) {
          var t = new THREE.Mesh(new THREE.CylinderGeometry(R_OUT + 0.00025, R_OUT + 0.00025, 0.009, 40, 1, true, -0.9, 1.8), MM.accent);
          t.position.y = H - 0.03; g.add(t);
        }
        g.userData.mouth = { x: 0, y: H, z: 0 };
        g.userData.food = FOOD;
        return g;
      }
    });

    /* a vial tray: a grey cardboard flat with round wells, cols by rows at 30 mm pitch, the vials
     * standing in it. Front +z. */
    K.define('vial_tray', {
      size: [0.3, 0.03, 0.3],
      options: { cols: 10, rows: 1, pitch: 0.03 },
      note: 'A cardboard vial flat, cols x rows wells at pitch metres, 3 cm deep. Vials stand in it with their foot 1 cm above the bench.',
      make: function (o) {
        var g = new THREE.Group(), c = +o.cols || 10, r = +o.rows || 1, p = +o.pitch || 0.03;
        var card = K.mat('vt-card', { color: 0x8c877c, roughness: 0.95 });
        var b = TXT.roundedBox(c * p + 0.01, 0.03, r * p + 0.01, 0.002, card); b.position.y = 0.015; b.castShadow = true; b.receiveShadow = true; g.add(b);
        g.userData.well = function (i, j) { return [-(c - 1) * p / 2 + i * p, 0.01, -(r - 1) * p / 2 + j * p]; };
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
    var paint = K.mat('vl-sill', { color: o.color || 0xc9c4ba, roughness: 0.62 });
    var alu = K.mat('vl-alu', { color: 0xaeb3b8, roughness: 0.35, metalness: 0.8 });
    var top = TXT.roundedBox(w, 0.04, 0.32, 0.006, paint); top.position.set(0, y - 0.02, 0.16); top.receiveShadow = true; top.castShadow = true; g.add(top);
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
      var td = 40 + rng() * 260, ta = Math.atan2(lk[1], lk[0]) + (rng() - 0.5) * 1.9;
      var tr = K.make(rng() < 0.75 ? 'live_oak' : 'crape_myrtle', { seed: 30 + t, height: 9 + rng() * 6 });
      tr.position.set(Math.cos(ta) * td, 0, Math.sin(ta) * td); TXT.add(R, tr);
    }
  };

  /* THE HERO, the same call on every frame. */
  N.vial = function (K, o) {
    o = o || {};
    return K.make('fly_vial', { state: o.state || 'climbing', flies: o.flies == null ? 18 : o.flies, pupae: o.pupae == null ? 9 : o.pupae, tape: !!o.tape, seed: o.seed || 1 });
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
    N.atmosphere(cx, { a: o.a == null ? 0.2 : o.a, to: o.to, fade: o.fade, rgb: o.rgb });
    N.soften(cx, o.type || ['.kick', '.hook', '.dek'], { blur: o.typeBlur || 8, pad: 8, feather: o.typeFeather || 26 });
    N.soften(cx, ['.tx-site', '.src'], { blur: 9, pad: 14, feather: 40 });
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
