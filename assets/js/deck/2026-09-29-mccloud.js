/* deck/2026-09-29-mccloud.js — the chassis for the 2026-09-29 deck: El Paso Electric's McCloud
 * facility, 813 modular gas generators proposed for a data center Meta is building in northeast
 * El Paso County through Wurldwide LLC, and the proposal for decision in which two administrative
 * law judges recommend approval only if the utility's other customers are held harmless
 * (tx-2026-0193, PUCT Docket 59076).
 *
 * THE WORLD. The Chihuahuan desert on the east side of the Franklin Mountains at the end of a
 * September day. goldenHour, looked at INTO the sun: the sun sits low over the range in the west,
 * so every frame that faces west puts the burning seam behind the ridge and a cool rim on steel,
 * and every frame that faces east gets the warm faces and the long casts. The world table's line
 * for golden hour into the sun is scale, weight and consequence, which is what a plant built for
 * one customer is. The key never moves.
 *
 * DIRECTIONS. +x is east, -x is west, -z is north, +z is south. The light is declared at az -84
 * (a hair south of due west) and el 5. A frame looking west (toward -x) looks into the sun. The
 * Franklin ridge runs north to south about seven kilometres west of the yard.
 *
 * THE HERO OBJECT. One modular gas generator, the kit model this file adds (modular_gas_genset):
 * a sound attenuated enclosure on a steel skid, radiator louvres at the +x end, intake louvres
 * down both sides, a silencer and a short stack on the roof, and the gas train at the -x end. The
 * record gives its rating (450 kW) and says the units are enclosed and fed by a pipeline, installed
 * in groups of four or five on one step-up transformer. It gives no dimensions and no vendor
 * drawing, so the model is DRAWN at the size a unit of that rating plausibly is, and no frame
 * prints a dimension of it. padmount_transformer is the step-up the group shares, and
 * genset_block is one group of four or five on its pad. N.yard lays out a count of units as
 * instanced low detail geometry, so 813 can stand on one frame.
 *
 * THE ACCENT. capitol granite #9A3B2A, the costs the data center carries. It marks the fence spans
 * the data center pays for, a rule under the judges' own words, and the one customer on the cover,
 * and nothing else. It never touches a generator, the pipeline, the sky or the ridge. It replaced
 * bluebonnet on the first render, because a blue accent under a blue golden hour sky measures as
 * sky and the sky measured as accent.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the kit
 * additions and the deck's materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("mccloud.js needs txdeck.js loaded first");

  /* ONE DECLARATION. az -84 is a hair south of west (clockwise from +Z toward +X), el 5 inside
   * goldenHour's 4 to 14, the sun a few degrees over the range. The haze is pulled to a dust rose
   * rather than the preset's peach, because the desert throws its own tan into the air and a
   * peach haze over a blue zenith grades a frame mauve (2026-09-26). */
  TXDECK.declare({
    world: "mccloud",
    light: { az: -84, el: 9 },
    sky: { preset: "goldenHour", zenith: 0x1b4f8f, horizon: 0x86bdd0, haze: 0xf0c07e, span: 0.3, fogDensity: 0.00017, clouds: 0, envIntensity: 0.46 },
    ground: "#16181D",
    material: "#CFCAC0",
    accent: "#9A3B2A",
    grade: {
      exposure: 0.0,
      saturation: 1.0,
      contrast: 1.05,
      filmic: true,
      lift: [0.01, 0.01, 0.014],
      gain: [1.0, 0.99, 0.98],
      vignette: 0.22,
      bloom: { threshold: 0.84, strength: 0.2, radius: 12 },
      grain: { amount: 0.012, size: 2, seed: 20260929 },
      aberration: 0,
      dither: true,
      sharpen: 0.16
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20260929;
  N.ACCENT = 0x9a3b2a;
  N.DESERT = 0xdcc6a0;          /* the basin floor, caliche and sand under creosote */
  N.PAINT = 0xd4d0c6;           /* the enclosure paint, a warm light grey */

  /* THE KIT ADDITIONS: modular_gas_genset, padmount_transformer and genset_block. The kit has a
   * 12 m containerised diesel genset and no small natural gas module, no pad-mounted step-up and
   * no block of units on one transformer, and this deck stands on all three. Built under the
   * conventions in the header of assets/js/txkit.js (metres, y up, origin at the footprint centre
   * on the ground, front on +z, K.mat materials, bevelled manufactured edges) so Phase 17 can lift
   * them into assets/js/kit/ unchanged. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.modular_gas_genset) return;

    function mats(o) {
      return {
        paint: K.mat('mgg-paint|' + (o.color || N.PAINT), { color: o.color || N.PAINT, roughness: 0.52, metalness: 0.18 }),
        louvre: K.mat('mgg-louvre', { color: 0x5d6064, roughness: 0.6, metalness: 0.35 }),
        dark: K.mat('mgg-dark', { color: 0x17191c, roughness: 0.7, metalness: 0.2 }),
        skid: K.mat('mgg-skid', { color: 0x3c3f42, roughness: 0.55, metalness: 0.55 }),
        galv: K.finish.galvanized(),
        stack: K.mat('mgg-stack', { color: 0x6f6a64, roughness: 0.45, metalness: 0.7 }),
        yellow: K.mat('mgg-gasline', { color: 0xc9a227, roughness: 0.5, metalness: 0.3 }),
        conc: K.finish.concrete(),
        xfmr: K.mat('pmt-green|' + (o.xcolor || 0x5c6b58), { color: o.xcolor || 0x5c6b58, roughness: 0.5, metalness: 0.3 }),
        fin: K.mat('pmt-fin', { color: 0x4d5a4a, roughness: 0.55, metalness: 0.35 })
      };
    }

    /* a louvre panel: a dark recess with blades, on a face at +z (turned by the caller) */
    function louvres(parent, M, w, h, x, y, z, ry) {
      var g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry || 0; parent.add(g);
      var back = TXT.roundedBox(w, h, 0.03, 0.006, M.dark); back.position.set(0, h / 2, -0.01); g.add(back);
      var n = Math.max(3, Math.round(h / 0.09));
      for (var i = 0; i < n; i++) {
        var b = TXT.roundedBox(w - 0.04, 0.012, 0.07, 0.004, M.louvre);
        b.position.set(0, (i + 0.5) * h / n, 0.025); b.rotation.x = 0.55; g.add(b);
      }
      var fr = TXT.roundedBox(w + 0.06, 0.035, 0.05, 0.008, M.paint); fr.position.set(0, h + 0.015, 0.01); g.add(fr);
      var fb = TXT.roundedBox(w + 0.06, 0.035, 0.05, 0.008, M.paint); fb.position.set(0, -0.015, 0.01); g.add(fb);
      return g;
    }

    K.define('modular_gas_genset', {
      size: [6.6, 3.7, 2.5],
      options: { color: null, lod: 'high', stack: true, gas: true },
      note: 'Modular natural gas generator in a sound attenuated enclosure on a steel skid, the kind installed in groups of four or five on one step-up transformer: radiator louvres at +x, intake louvres down both sides, personnel doors on +z, a roof silencer and short stack, the gas train and its yellow line at -x. DRAWN at a plausible size for a unit of a few hundred kilowatts; no record gives its dimensions. lod "low" is one merged body for a yard. userData.stackTop, .gasInlet, .cableOut.',
      make: function (o, r) {
        var M = mats(o), g = new THREE.Group();
        var L = 6.1, Wd = 2.35, H = 2.55, sk = 0.22;
        /* the skid: two channel rails and cross members, standing proud of the pad */
        [-1, 1].forEach(function (s) { K.box(L + 0.2, sk, 0.18, M.skid, 0, 0, s * (Wd / 2 - 0.09), 0.01, g); });
        K.box(L, 0.06, Wd - 0.1, M.skid, 0, sk - 0.06, 0, 0, g);
        /* the enclosure */
        var body = TXT.roundedBox(L, H, Wd, 0.05, M.paint); body.position.set(0, sk + H / 2, 0); g.add(body);
        /* roof drip edge and seam ribs */
        var roof = TXT.roundedBox(L + 0.1, 0.06, Wd + 0.1, 0.02, M.paint); roof.position.set(0, sk + H + 0.03, 0); g.add(roof);
        if (o.lod !== 'low') {
          /* panel seams on the door side only, standing clear of the face so they never z-fight it */
          [-2.35, -0.95, 2.85].forEach(function (x) { var rib = TXT.roundedBox(0.05, H - 0.1, 0.03, 0.01, M.paint); rib.position.set(x, sk + H / 2, Wd / 2 + 0.03); g.add(rib); });
          /* radiator louvres on the +x end, the full face */
          louvres(g, M, Wd - 0.4, H - 0.5, L / 2 + 0.005, sk + 0.25, 0, Math.PI / 2);
          /* intake louvres on both long sides, toward the -x end */
          [1, -1].forEach(function (s) {
            louvres(g, M, 1.3, 1.2, -L / 2 + 1.1, sk + 1.0, s * (Wd / 2 + 0.01), s > 0 ? 0 : Math.PI);
            louvres(g, M, 1.3, 1.2, -L / 2 + 2.6, sk + 1.0, s * (Wd / 2 + 0.01), s > 0 ? 0 : Math.PI);
          });
          /* two personnel doors on +z with handles */
          [0.9, 2.1].forEach(function (x) {
            var d = TXT.roundedBox(0.95, 2.0, 0.02, 0.01, M.paint); d.position.set(x, sk + 1.08, Wd / 2 + 0.02); g.add(d);
            K.bar([x + 0.36, sk + 1.0, Wd / 2 + 0.05], [x + 0.36, sk + 1.25, Wd / 2 + 0.05], 0.012, M.dark, 6, g);
          });
          /* a data plate */
          var pl = TXT.roundedBox(0.34, 0.22, 0.01, 0.004, K.mat('mgg-plate', { color: 0xeeece6, roughness: 0.4 })); pl.position.set(-1.95, sk + 2.38, Wd / 2 + 0.03);   /* above the intake louvres, on solid panel */ g.add(pl);
        } else {
          /* one dark band for the louvres at the far end and down the side, so a far unit still reads as a machine */
          var band = TXT.roundedBox(0.02, H - 0.5, Wd - 0.4, 0.004, M.dark); band.position.set(L / 2 + 0.01, sk + H / 2, 0); g.add(band);
          [1, -1].forEach(function (s) { var b2 = TXT.roundedBox(2.8, 1.2, 0.02, 0.004, M.dark); b2.position.set(-L / 2 + 1.85, sk + 1.6, s * (Wd / 2 + 0.01)); g.add(b2); });
        }
        /* the roof silencer on saddles and the stack */
        var stackTop = null;
        if (o.stack !== false) {
          var sil = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 1.7, 20), M.stack); sil.rotation.z = Math.PI / 2; sil.position.set(-0.6, sk + H + 0.42, -0.3); g.add(sil);
          [-1.2, 0.0].forEach(function (x) { K.box(0.12, 0.2, 0.5, M.skid, x, sk + H + 0.06, -0.3, 0.01, g); });
          K.cyl(0.13, 0.13, 0.75, M.stack, 0.3, sk + H + 0.42, -0.3, 16, g);
          var lip = K.cyl(0.15, 0.13, 0.06, M.stack, 0.3, sk + H + 1.15, -0.3, 16, g);
          stackTop = { x: 0.3, y: sk + H + 1.21, z: -0.3 };
        }
        /* the gas train at -x: a yellow riser from the pad, a regulator and a valve */
        var gasInlet = { x: -L / 2 - 0.35, y: 0.0, z: 0.55 };
        if (o.gas !== false && o.lod !== 'low') {
          K.bar([-L / 2 - 0.35, 0.0, 0.55], [-L / 2 - 0.35, 0.9, 0.55], 0.05, M.yellow, 12, g);
          K.bar([-L / 2 - 0.35, 0.9, 0.55], [-L / 2 + 0.02, 0.9, 0.55], 0.05, M.yellow, 12, g);
          var reg = K.cyl(0.14, 0.14, 0.22, M.yellow, -L / 2 - 0.35, 0.55, 0.55, 16, g);
          var cap = K.cyl(0.18, 0.06, 0.12, M.dark, -L / 2 - 0.35, 0.77, 0.55, 16, g);
          /* the quarter turn valve handle on the riser */
          K.bar([-L / 2 - 0.35, 0.35, 0.55], [-L / 2 - 0.62, 0.35, 0.55], 0.018, M.dark, 8, g);
        }
        g.userData.stackTop = stackTop;
        g.userData.gasInlet = gasInlet;
        g.userData.cableOut = { x: L / 2 - 0.5, y: 0.0, z: -Wd / 2 };
        return g;
      }
    });

    K.define('padmount_transformer', {
      size: [2.6, 2.1, 2.3],
      options: { xcolor: null, fins: true },
      note: 'Pad mounted step-up transformer the units of one block share: a green steel tank on a concrete pad with radiator fins on both sides, a low voltage cabinet on +z and a high voltage cabinet on -z, a nameplate. DRAWN, no rating printed. userData.hvOut.',
      make: function (o, r) {
        var M = mats(o), g = new THREE.Group();
        K.box(2.8, 0.2, 2.5, M.conc, 0, 0, 0, 0.02, g);
        var tank = TXT.roundedBox(1.6, 1.5, 1.4, 0.04, M.xfmr); tank.position.set(0, 0.2 + 0.75, 0); g.add(tank);
        var lid = TXT.roundedBox(1.7, 0.06, 1.5, 0.02, M.xfmr); lid.position.set(0, 0.2 + 1.53, 0); g.add(lid);
        [0.7, -0.7].forEach(function (z) { var cab = TXT.roundedBox(1.5, 1.4, 0.45, 0.03, M.xfmr); cab.position.set(0, 0.2 + 0.7, z > 0 ? 0.92 : -0.92); g.add(cab); });
        if (o.fins !== false) {
          [-1, 1].forEach(function (s) {
            for (var i = 0; i < 9; i++) { var f = TXT.roundedBox(0.36, 1.2, 0.03, 0.006, M.fin); f.position.set(s * 0.98, 0.2 + 0.7, -0.52 + i * 0.13); g.add(f); }
          });
        }
        var np = TXT.roundedBox(0.3, 0.2, 0.01, 0.004, K.mat('pmt-plate', { color: 0xdcdad2, roughness: 0.4 })); np.position.set(0.3, 0.2 + 1.1, 1.15 + 0.005); g.add(np);
        K.cyl(0.05, 0.05, 0.35, K.finish.porcelain(), -0.3, 0.2 + 1.56, -0.4, 12, g);
        K.cyl(0.05, 0.05, 0.35, K.finish.porcelain(), 0.0, 0.2 + 1.56, -0.4, 12, g);
        K.cyl(0.05, 0.05, 0.35, K.finish.porcelain(), 0.3, 0.2 + 1.56, -0.4, 12, g);
        g.userData.hvOut = { x: 0, y: 1.9, z: -0.4 };
        return g;
      }
    });

    /* one block: n units (4 or 5) side by side along x, doors to +z, on a shared concrete pad,
     * the step-up transformer at the +x end of the row, conduit trench to it. */
    K.define('genset_block', {
      size: [22, 3.7, 6],
      options: { units: 5, lod: 'high', gap: 1.1 },
      note: 'One group of modular gas generators on a shared pad with the step-up transformer they share at the +x end, units 4 or 5 (the record says groups of four or five). Units stand side by side, long axis along z. userData.units ([{x,z}]), .transformer ({x,z}).',
      make: function (o, r) {
        var g = new THREE.Group(), n = Math.max(1, Math.min(6, o.units | 0 || 5)), gap = +o.gap || 1.1;
        var pitch = 2.35 + gap, span = (n - 1) * pitch, units = [];
        var M = mats(o);
        K.box(span + 2.35 + 6.2, 0.15, 7.2, M.conc, (6.2 - 0) / 2 - 0.5, 0, 0, 0.02, g);
        for (var i = 0; i < n; i++) {
          var u = K.make('modular_gas_genset', { seed: (o.seed || 1) * 13 + i, lod: o.lod });
          u.rotation.y = Math.PI / 2; u.position.set(-span / 2 + i * pitch, 0.15, 0); g.add(u);
          units.push({ x: -span / 2 + i * pitch, z: 0 });
        }
        var tx = K.make('padmount_transformer', { seed: 3 });
        tx.position.set(span / 2 + 4.2, 0.15, -1.2); g.add(tx);
        /* the conduit trench cover from the row to the transformer */
        K.box(span + 4.0, 0.04, 0.5, K.mat('mgg-trench', { color: 0x8c8a86, roughness: 0.9 }), 0.2, 0.15, -3.1, 0.01, g);
        g.userData.units = units;
        g.userData.transformer = { x: span / 2 + 4.2, z: -1.2 };
        return g;
      }
    });
  };

  /* THE YEAR FENCE: an oilfield pipe-rail fence of `spans` equal spans, one span per year of the
   * plant's estimated service life, whose top rails are painted the accent for the first `paid`
   * spans and left bare primer for the rest. The fence is the deck's measure of time, and the
   * number of spans and the number painted are figures from the record (figures.json), never
   * typed into a frame. `collarAt` puts a galvanised collar on the post that ends that span.
   * Origin at the fence's west end on the ground, the run along +x. Returns the group with
   * userData.posts ([{x, y}]) so a frame can land a leader on a post. */
  N.yearFence = function (K, THREE, TXT, o) {
    o = o || {};
    var spans = o.spans | 0, paid = o.paid | 0, sp = o.spacing || 1.8, ph = o.postH || 2.2, g = new THREE.Group(), posts = [];
    if (!spans) throw new Error('yearFence needs spans from figures.json');
    var pipe = K.mat('yf-pipe', { color: 0x9a9da0, roughness: 0.5, metalness: 0.55 });
    /* the paint is darker than the accent it has to read as, because the low sun lifts a lit face
     * well above its base colour (2026-09-29, the first render sampled vermilion on a #9A3B2A base) */
    var acc = K.mat('yf-acc2', { color: 0x6e2a20, roughness: 0.65, metalness: 0.05 });
    var primer = K.mat('yf-primer', { color: 0x8f8a80, roughness: 0.8, metalness: 0.05 });
    var galv = K.finish.galvanized();
    for (var i = 0; i <= spans; i++) {
      var x = i * sp;
      K.cyl(0.057, 0.057, ph, pipe, x, 0, 0, 14, g);
      var dome = new THREE.Mesh(new THREE.SphereGeometry(0.06, 14, 6, 0, Math.PI * 2, 0, Math.PI / 2), pipe); dome.position.set(x, ph, 0); g.add(dome);
      if (o.collarAt != null && i === (o.collarAt | 0)) K.cyl(0.085, 0.085, 0.16, galv, x, ph - 0.3, 0, 16, g);
      posts.push({ x: x, y: ph });
    }
    /* each span carries a sheet panel between the rails: the PANEL carries the paint, because a
     * pipe rail projects under a pixel at feed size once the fence is seen side on */
    var pT = ph - 0.25, pB = 0.45;
    for (var s = 0; s < spans; s++) {
      var x0 = s * sp, x1 = (s + 1) * sp;
      K.bar([x0 + 0.05, pT + 0.05, 0.0], [x1 - 0.05, pT + 0.05, 0.0], 0.05, pipe, 12, g);
      K.bar([x0 + 0.05, pB - 0.05, 0.0], [x1 - 0.05, pB - 0.05, 0.0], 0.045, pipe, 12, g);
      var pn = TXT.roundedBox(sp - 0.16, pT - pB, 0.03, 0.008, s < paid ? acc : primer);
      pn.position.set((x0 + x1) / 2, (pT + pB) / 2, 0.06); pn.castShadow = true; pn.receiveShadow = true; g.add(pn);
      /* three pressed ribs per panel, so a panel lit face on still shows its modelling */
      for (var rb = 1; rb <= 3; rb++) { var rib = TXT.roundedBox(0.05, pT - pB - 0.12, 0.025, 0.008, s < paid ? acc : primer); rib.position.set(x0 + (x1 - x0) * rb / 4, (pT + pB) / 2, 0.085); rib.castShadow = true; g.add(rib); }
    }
    g.userData.posts = posts; g.userData.spans = spans; g.userData.paid = paid; g.userData.panel = [pB, pT];
    return g;
  };

  /* THE SITE, one layout for every frame so a camera anywhere sees the same place. The pad is a
   * square whose area is the record's acreage (figures.json acres, converted in code at 4046.86 m2
   * per acre); the yard stands on it; the data hall stands immediately north of it; the year fence
   * runs north along the pad's west edge from its south-west corner. None of this is the site plan,
   * which the record does not give. */
  N.site = function (acres) {
    var side = Math.sqrt(acres * 4046.86);
    return { side: side, yard: [0, 0, 0], hall: [0, 0, -side / 2 - 70], fence: [-side / 2 - 4, 0, side / 2 - 8] };
  };
  N.pad = function (K, THREE, TXT, R, side) {
    /* graded caliche with the concrete texture's tooth, tiled in metres, so the pad is a surface and not a plate */
    var tex = K.tex('concrete').clone(); tex.needsUpdate = true; tex.repeat.set(side / 6, side / 6);
    var m = new THREE.Mesh(new THREE.PlaneGeometry(side, side), new THREE.MeshStandardMaterial({ color: 0xe6d6b8, map: tex, roughness: 0.95 }));
    m.rotation.x = -Math.PI / 2; m.position.y = 0.02; m.receiveShadow = true; TXT.add(R, m);
    return m;
  };

  /* THE HERO, made the same way on every frame. */
  N.unit = function (K, o) { return K.make('modular_gas_genset', Object.assign({ seed: 7 }, o || {})); };
  N.block = function (K, o) { return K.make('genset_block', Object.assign({ seed: 5, units: 5 }, o || {})); };

  /* A YARD OF UNITS AS INSTANCED LOW DETAIL GEOMETRY, so a count in the hundreds can stand on one
   * frame at the cost of a few draw calls. count is the exact number of units drawn, and the
   * layout is blocks of 5 (then 4 for the remainder that 5 does not divide), rows along x, each
   * block's transformer at its +x end, block rows marching in z. Returns {group, units:[[x,z]],
   * drawn}, where drawn is the number of unit instances placed, which a frame asserts equals the
   * count it was given. */
  N.yard = function (K, THREE, TXT, o) {
    o = o || {};
    var count = o.count | 0, per = o.per || 5, perRow = o.blocksPerRow || 8, pitch = 3.45, blockGap = o.blockGap || 5.5, rowGap = o.rowGap || 11;
    var blocks = [], left = count;
    /* blocks of five, and fours for the remainder: 5a + 4b = count with the fewest fours */
    var fours = 0; while ((count - 4 * fours) % 5 !== 0 && fours < 5) fours++;
    var fives = (count - 4 * fours) / 5;
    for (var i = 0; i < fives; i++) blocks.push(5);
    for (var j = 0; j < fours; j++) blocks.splice(Math.floor((j + 1) * blocks.length / (fours + 1)), 0, 4);
    var M = {
      paint: K.mat('mgg-paint|' + N.PAINT, { color: N.PAINT, roughness: 0.52, metalness: 0.18 }),
      dark: K.mat('mgg-dark', { color: 0x17191c, roughness: 0.7, metalness: 0.2 }),
      stack: K.mat('mgg-stack', { color: 0x6f6a64, roughness: 0.45, metalness: 0.7 }),
      xfmr: K.mat('pmt-green|yard', { color: 0x74846d, roughness: 0.6, metalness: 0.2 }),
      conc: K.finish.concrete()
    };
    var bodyG = new THREE.BoxGeometry(2.35, 2.55, 6.1); bodyG.translate(0, 0.22 + 1.275, 0);
    /* the radiator end as five slats with gaps between, so a far unit's end reads as louvres and not a black square (round 2) */
    var louvG = (function () { var parts = [], k; for (k = 0; k < 5; k++) { var b = new THREE.BoxGeometry(2.0, 0.22, 0.06); b.rotateX(0.5); b.translate(0, 0.22 + 0.62 + k * 0.36, 3.07); parts.push(b); }
      var pos = [], nor = []; parts.forEach(function (g) { var n = g.toNonIndexed(); pos.push.apply(pos, n.attributes.position.array); nor.push.apply(nor, n.attributes.normal.array); });
      var G = new THREE.BufferGeometry(); G.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); G.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3)); return G; })();
    /* the intake louvres as three dark bands, not one dark window, so a far unit reads as a machine and not a cabin (2026-09-29) */
    var sideG = new THREE.BoxGeometry(2.38, 0.16, 2.8); sideG.translate(0, 0.22 + 1.1, -1.3);
    var sideG2 = sideG.clone(); sideG2.translate(0, 0.36, 0); var sideG3 = sideG.clone(); sideG3.translate(0, 0.72, 0);
    var stackG = new THREE.CylinderGeometry(0.13, 0.13, 1.0, 10); stackG.translate(0.3, 0.22 + 2.55 + 0.5, -0.4);
    var silG = new THREE.CylinderGeometry(0.3, 0.3, 1.6, 12); silG.rotateX(Math.PI / 2); silG.translate(0.3, 0.22 + 2.55 + 0.34, 0.5);
    var xfG = new THREE.BoxGeometry(1.6, 1.7, 2.1); xfG.translate(0, 0.85, 0);
    var padG = new THREE.BoxGeometry(1, 0.15, 7.4); padG.translate(0, 0.075, 0);
    var U = [], X = [], P = [], units = [];
    var bx = 0, bz = 0, col = 0, rowW = 0, x0 = 0;
    blocks.forEach(function (n, bi) {
      var w = n * pitch + 4.0;
      for (var k = 0; k < n; k++) { var ux = x0 + k * pitch; U.push([ux, 0.15, bz, 0, 1]); units.push([ux, bz]); }
      X.push([x0 + n * pitch + 1.2, 0.15, bz - 1.4, 0, 1]);
      P.push([x0 + w / 2 - 1.6, 0, bz, 0, 1, w]);
      x0 += w + blockGap; col++;
      if (col >= perRow) { col = 0; x0 = 0; bz += rowGap; }
    });
    var grp = new THREE.Group();
    function inst(geo, mat, list, shadow) {
      var im = K.instances(geo, mat, list, grp); im.castShadow = shadow !== false; im.receiveShadow = true; return im;
    }
    /* THE DETAIL ZONE. o.detail = [x0, z0, x1, z1] in the yard's own centred coordinates: every
     * unit and transformer inside it is built as the full kit model instead of an instance, so a
     * camera standing at the yard's edge sees the hero at the lens and the count stays exact */
    var DU = [], DX = [], total = U.length;
    if (o.detail) {
      var d = o.detail, c0 = (function () { var a = Infinity, b = -Infinity, e = Infinity, f = -Infinity;
        units.forEach(function (u) { a = Math.min(a, u[0]); b = Math.max(b, u[0]); e = Math.min(e, u[1]); f = Math.max(f, u[1]); }); return [(a + b) / 2, (e + f) / 2]; })();
      var inBox = function (x, z) { x -= c0[0]; z -= c0[1]; return x > d[0] && x < d[2] && z > d[1] && z < d[3]; };
      U = U.filter(function (u) { if (inBox(u[0], u[2])) { DU.push(u); return false; } return true; });
      X = X.filter(function (x) { if (inBox(x[0], x[2])) { DX.push(x); return false; } return true; });
    }
    inst(bodyG, M.paint, U); inst(louvG, K.mat('mgg-louvre', { color: 0x5d6064, roughness: 0.6, metalness: 0.35 }), U, false);   /* a louvre grey, not a black square, on the end a camera faces */ inst(sideG, M.dark, U, false); inst(sideG2, M.dark, U, false); inst(sideG3, M.dark, U, false);
    inst(stackG, M.stack, U); inst(silG, M.stack, U);
    inst(xfG, M.xfmr, X);
    DU.forEach(function (u, i) { var m = K.make('modular_gas_genset', { seed: 40 + i }); m.rotation.y = -Math.PI / 2; m.position.set(u[0], 0.15, u[2]); grp.add(m); });
    DX.forEach(function (x, i) { var m = K.make('padmount_transformer', { seed: 3 }); m.rotation.y = -Math.PI / 2; m.position.set(x[0], 0.15, x[2]); grp.add(m); });
    var pads = new THREE.InstancedMesh(padG, M.conc, P.length), Mx = new THREE.Matrix4();
    P.forEach(function (p, i) { Mx.compose(new THREE.Vector3(p[0], 0, p[2]), new THREE.Quaternion(), new THREE.Vector3(p[5], 1, 1)); pads.setMatrixAt(i, Mx); });
    pads.receiveShadow = true; grp.add(pads);
    /* centre the yard on its own footprint so a frame can place it by its middle */
    var minx = Infinity, maxx = -Infinity, minz = Infinity, maxz = -Infinity;
    units.forEach(function (u) { minx = Math.min(minx, u[0]); maxx = Math.max(maxx, u[0]); minz = Math.min(minz, u[1]); maxz = Math.max(maxz, u[1]); });
    var cx = (minx + maxx) / 2, cz = (minz + maxz) / 2;
    grp.children.forEach(function (c) { c.position.x -= cx; c.position.z -= cz; });
    units = units.map(function (u) { return [u[0] - cx, u[1] - cz]; });
    grp.userData = { units: units, drawn: U.length + DU.length, detailed: DU.length, blocks: blocks.length, fours: fours, extent: [maxx - minx + 6.1, maxz - minz + 7.4] };
    return grp;
  };

  /* THE FRANKLIN RIDGE: a long ridged range seven or eight kilometres west, running north to
   * south, where TXT.sky's haze carries the distance. Built as a displaced strip whose crest is a
   * seeded ridged noise, faces falling steep to the east. It is DRAWN, the kind of range that
   * stands west of the site, and no frame names a peak or a height. */
  N.ridge = function (THREE, TXT, R, o) {
    o = o || {};
    var len = o.length || 26000, depth = o.depth || 2600, peak = o.peak || 430, seg = o.seg || 480, dseg = o.dseg || 90;
    var geo = new THREE.PlaneGeometry(depth, len, dseg, seg); geo.rotateX(-Math.PI / 2);
    var rng = TX.rng(o.seed || 29), ph = [rng() * 10, rng() * 10, rng() * 10];
    var pos = geo.attributes.position;
    for (var i = 0; i < pos.count; i++) {
      var x = pos.getX(i), z = pos.getZ(i);
      var t = (x + depth / 2) / depth;            /* 0 at the west foot, 1 at the east foot */
      var crest = 0.42 + 0.08 * Math.sin(z / 2600 + ph[0]);
      var prof = t < crest ? Math.pow(t / crest, 0.8) : Math.pow(Math.max(0, 1 - (t - crest) / (1 - crest)), 1.6);
      var n = 0.62 + 0.22 * Math.sin(z / 1900 + ph[1]) + 0.12 * Math.sin(z / 700 + ph[2]) + 0.05 * Math.sin(z / 230 + ph[0]);
      var along = Math.min(1, Math.min(z + len / 2, len / 2 - z) / 2500);
      var hh = peak * n * prof * Math.max(0.15, along);
      var rough = 0; for (var oc = 0, a = 1, f = 1; oc < 5; oc++, a *= 0.5, f *= 2.1) rough += a * (1 - Math.abs(TX.simplex2 ? TX.simplex2(x / 900 * f + ph[0], z / 900 * f + ph[1]) : Math.sin(x * f / 300 + z * f / 410)));
      var rk = o.rough != null ? o.rough : 1; hh = hh * (1 - 0.45 * rk + 0.45 * rk * rough / 1.9) + 60 * Math.pow(Math.max(0, TX.simplex2 ? TX.simplex2(z / 380 + ph[2], x / 380) : 0), 2) * prof;
      pos.setY(i, Math.max(0, hh));
    }
    geo.computeVertexNormals();
    var m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: o.color || 0x6a5648, roughness: 0.98, metalness: 0 }));
    m.position.set(o.x != null ? o.x : -5600, -2, o.z || 0);
    m.receiveShadow = true; m.castShadow = false;
    R.scene.add(m);
    return m;
  };

  /* THE DESERT FLOOR's plants and stones, kept off any rectangles in world metres a frame names.
   * The frame lays its own TXT.ground first, in MC.DESERT, so the ground is in the frame's source
   * where depth_floor reads it. Call AFTER TXT.frame. */
  N.desert = function (TXT, R, o) {
    o = o || {};
    TXT.scatter(R, { kind: 'scrub', count: o.scrub || 2600, area: o.area || [-400, -400, 400, 200], avoid: o.avoid || [], seed: (o.seed || 11) + 2, scale: o.scale || [0.1, 0.2],
                     colors: [0x5a5e3a, 0x676a41, 0x4f5535, 0x6f6c46] });
    TXT.scatter(R, { kind: 'rock', count: o.rock || 1400, area: o.area || [-400, -400, 400, 200], avoid: o.avoid || [], seed: (o.seed || 11) + 3, scale: [0.05, 0.16] });
    if (o.grass) TXT.scatter(R, { kind: 'grass', count: o.grass, area: o.grassArea || o.area || [-200, -200, 200, 100], avoid: o.avoid || [], seed: (o.seed || 11) + 4, scale: [0.4, 0.8],
                                  colors: [0xb7a07a, 0xa89272, 0xc2ad86] });
  };

  /* A PAGE, as a texture the size of a letter sheet at 8 px per mm: hairline entries for the
   * lines nobody reads, and the room for the DOM lines a frame registers onto it. */
  N.pageTexture = function (THREE, entries, o) {
    o = o || {};
    var W = 1728, H = 2232, c = document.createElement('canvas'); c.width = W; c.height = H;
    var x = c.getContext('2d');
    x.fillStyle = o.paper || '#f1efe9'; x.fillRect(0, 0, W, H);
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

  /* ATMOSPHERE TOWARD THE TYPE. Light dims toward type rather than being removed from around it.
   * Two full-width vertical washes, never a box and never over 0.45 alpha, so deck_chassis reads
   * them as atmosphere and not as a plate. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector('.dek'), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    var top = o.a == null ? 0.34 : Math.min(0.45, o.a);
    if (bottom != null && top > 0) {
      var g = cx.createLinearGradient(0, 0, 0, bottom + (o.fade || 170));
      g.addColorStop(0, 'rgba(10,11,16,' + (top * 0.6) + ')');
      g.addColorStop(Math.max(0.05, bottom / (bottom + (o.fade || 170))), 'rgba(10,11,16,' + top + ')');
      g.addColorStop(1, 'rgba(10,11,16,0)');
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + (o.fade || 170));
    }
    var fa = o.floor == null ? 0.4 : Math.min(0.45, o.floor);
    if (fa > 0) {
      var y0 = N.H - (o.floorH || 190);
      var h = cx.createLinearGradient(0, y0, 0, N.H);
      for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); h.addColorStop(t, 'rgba(10,11,16,' + (fa * e).toFixed(4) + ')'); }
      cx.fillStyle = h; cx.fillRect(0, y0, N.W, N.H - y0);
    }
  };

  /* KNOCK THE EDGE OUT BEHIND A LINE OF TYPE, without removing its light: blur the art under each
   * named element's line boxes, feathered wide, so the edge dissolves while the tone stays. */
  N.soften = function (cx, selectors, o) {
    o = o || {};
    var blur = o.blur || 13, pad = o.pad == null ? 20 : o.pad, feather = o.feather || 72;
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

  global.MC = N;
})(this);
