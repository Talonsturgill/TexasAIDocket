/* deck/2026-10-24-apron.js — the chassis for the 2026-10-24 deck: Tesla's update for the third quarter of 2026 lists
 * its Texas rows of installed capacity as Production, and the Texas row for Optimus, its humanoid robot, as
 * Construction with no figure (tx-2026-0230).
 *
 * THE VISUAL ARGUMENT. The table walked as a plant at night. Five bay doors stand in a tilt up wall in the order of
 * the table's Texas rows. Every bay whose row reads Production has its high bay lamps lit over its line. The Optimus
 * bay, whose row reads Construction, is a dark slab of anchor bolts, taped empty pads and crated tools under two work
 * lamps, with its high bay lamps present and off. The plan is the table's order, never the site's.
 *
 * THE WORLD. floodlit, a STAGED world: a black sky and one cold LED flood on a far mast. A plant runs on its own light
 * at night, so the only other light in any frame is the bays' own, and that light is the variable the deck reads.
 *
 * THE LIGHT is azimuth -58, elevation 25. +x is east and +z is south, az runs from +z toward -x for a negative value,
 * so the flood stands low in the south west of every subject: a camera on +z looking -z has the key in front and to
 * its LEFT, every jamb and bolt has its lit edge on the left, and every cast runs long to the right and away. A
 * material relief reads it from the upper left of its frame and every cast runs down and to the right.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `plant_wall` (a tilt up wall of bays with vertical
 * lift door openings, each bay lit or dark), `line_carrier` (a steel skillet on a floor track), `bollard`,
 * `anchor_bolt_set`, `tool_crate`, `tripod_work_lamp`, `megapack_unit` (an illustrative battery enclosure),
 * `steel_frame` (an unclad primed steel frame) and `covered_pod` (a two seat car under a fitted cover). Each is built
 * in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is bluebonnet, #4E5FA8, and it means ONE thing: planned or under construction, not yet installed.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 * Every frame composes its own picture, and every count a frame draws is read from figures.json in that frame's own
 * code where figure_bearing.py reads it. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("apron.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "apron",
    light: { az: -58, el: 25 },
    sky: "floodlit",
    ground: "#08060F",
    material: "#CFC8BA",
    accent: "#4E5FA8",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.06,
      filmic: true,
      lift: [0.002, 0.003, 0.006],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.2,
      bloom: { threshold: 0.86, strength: 0.12, radius: 10 },
      grain: { amount: 0.016, size: 2, seed: 20261024 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261024;
  N.ACCENT = 0x4e5fa8;   /* bluebonnet, brand.yaml's, and it means ONE thing: planned or under construction */
  N.INK = "#ECE8DF";
  /* THE PLANT'S ONE BAY, in metres, on every frame that shows the wall */
  N.BAY = { w: 16, h: 13, door: 10, doorH: 8, depth: 30 };
  N.LAMP_WARM = 0xffd29c;   /* 3500K high bay light */

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */
  function stripes(THREE, n, a, b, vertical, size) {
    var c = document.createElement("canvas"); c.width = c.height = size || 256; var x = c.getContext("2d");
    x.fillStyle = a; x.fillRect(0, 0, c.width, c.height); x.fillStyle = b;
    var step = c.width / n;
    for (var i = 0; i < n; i++) { if (vertical) x.fillRect(i * step, 0, step * 0.42, c.height); else x.fillRect(0, i * step, c.width, step * 0.42); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  N.mats = function (THREE, K) {
    if (N._m) return N._m;
    var conc = K.tex("concrete").clone(); conc.needsUpdate = true;
    var m = {
      /* tilt up chalk aggregate panels, the map carries the tone, held below the pale band */
      panel: new THREE.MeshStandardMaterial({ color: 0xc8c3ba, roughness: 0.93, metalness: 0, map: conc }),
      reveal: new THREE.MeshStandardMaterial({ color: 0x24221f, roughness: 0.9 }),
      galv: K.finish.galvanized(),
      galvDark: K.mat("apron_galv_dark", { color: 0x7d8186, metalness: 0.7, roughness: 0.5 }),
      floor: new THREE.MeshStandardMaterial({ color: 0x6d6a64, roughness: 0.55, metalness: 0.02, map: conc }),
      backWall: new THREE.MeshStandardMaterial({ color: 0x1a1917, roughness: 0.95 }),
      roof: new THREE.MeshStandardMaterial({ color: 0x1d1c1b, roughness: 0.9, side: THREE.DoubleSide }),
      lampOn: new THREE.MeshStandardMaterial({ color: 0x222222, emissive: N.LAMP_WARM, emissiveIntensity: 2.4, roughness: 0.4 }),
      lampOff: new THREE.MeshStandardMaterial({ color: 0x3a3c3f, metalness: 0.6, roughness: 0.45 }),
      lampLens: new THREE.MeshStandardMaterial({ color: 0x5a5d60, metalness: 0.1, roughness: 0.2 }),
      steel: K.mat("apron_steel", { color: 0x5b5f63, metalness: 0.75, roughness: 0.42 }),
      rail: K.mat("apron_rail", { color: 0xb8bcc0, metalness: 0.95, roughness: 0.22 }),
      primer: K.mat("apron_primer", { color: 0x8c4630, metalness: 0.2, roughness: 0.5 }),
      ply: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85, map: K.tex("wood") }),
      strap: K.mat("apron_strap", { color: 0x2f3236, metalness: 0.8, roughness: 0.35 }),
      fabric: K.mat("apron_fabric", { color: 0x4f5154, roughness: 0.95, metalness: 0, side: THREE.DoubleSide }),
      tyre: K.finish.rubber(),
      rim: K.mat("apron_rim", { color: 0x55595d, metalness: 0.8, roughness: 0.35 }),
      white: new THREE.MeshStandardMaterial({ color: 0xc9c9c4, roughness: 0.55, metalness: 0.1, map: stripes(THREE, 26, "#d8d8d3", "#a7a7a2", false) }),
      plinth: K.mat("apron_plinth", { color: 0x55575a, roughness: 0.8 }),
      tape: new THREE.MeshBasicMaterial({ color: new THREE.Color(N.ACCENT), toneMapped: false, fog: false }),   /* the accent holds its hue at any distance */
      grout: K.mat("apron_grout", { color: 0x8a8781, roughness: 0.96 }),
      thread: new THREE.MeshStandardMaterial({ color: 0xc9cdd1, metalness: 0.55, roughness: 0.38, bumpMap: stripes(THREE, 40, "#ffffff", "#000000", false, 128), bumpScale: 0.6 }),
      workLamp: new THREE.MeshStandardMaterial({ color: 0x111111, emissive: 0xfff1d8, emissiveIntensity: 3.2 }),
      lampBody: K.mat("apron_lampbody", { color: 0x55595f, metalness: 0.7, roughness: 0.45 }),   /* graphite: a pastel yellow mast read as a toy */
      lane: new THREE.MeshStandardMaterial({ color: 0x9f9a7c, roughness: 0.7 }),
      freshSlab: new THREE.MeshStandardMaterial({ color: 0x3a3834, roughness: 0.92, map: conc }),
      leaf: K.mat("apron_leaf", { color: 0x3a3d41, metalness: 0.45, roughness: 0.6 }),
      film: new THREE.MeshPhysicalMaterial({ color: 0x77736c, roughness: 0.6, metalness: 0, clearcoat: 0.25, clearcoatRoughness: 0.6 })
    };
    m.white.map.repeat.set(1, 3);
    N._m = m;
    return m;
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.plant_wall) return;
    var M = N.mats(THREE, K);
    function box(w, h, d, mat, x, y, z, parent, r) {
      var b = r ? TXT.roundedBox(w, h, d, r, mat) : new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
      b.position.set(x, y, z); b.castShadow = b.receiveShadow = true; if (parent) parent.add(b); return b;
    }
    N.box = box;
    function uvb(mesh, m) { K.uvBox(mesh.geometry, m || 3); return mesh; }

    /* A VERTICAL LIFT DOOR BAY: a 24 m wide stretch of tilt up wall, 13 m tall, front face on z 0, a 10 by 8 m door
     * opening at its centre with galvanized jambs and the raised leaf's bottom rail in the header, and behind it a
     * 30 m deep bay with a sealed floor, a back wall, a roof, and three rows of high bay lamps lit or off. */
    K.define("plant_bay", {
      size: [24, 13, 30],
      options: { lit: true, leaf: 1, lamps: true, panels: 4 },
      note: "One bay of a tilt up plant wall with a vertical lift door opening and the bay behind it, its high bay lamps lit or off. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), B = N.BAY, w = B.w, h = B.h, dw = B.door, dh = B.doorH, t = 0.3, D = B.depth;
        var pier = (w - dw) / 2;
        uvb(box(pier, h, t, M.panel, -w / 2 + pier / 2, h / 2, -t / 2, g));
        uvb(box(pier, h, t, M.panel, w / 2 - pier / 2, h / 2, -t / 2, g));
        uvb(box(dw, h - dh, t, M.panel, 0, dh + (h - dh) / 2, -t / 2, g));
        /* panel reveals: dark joints between the tilt up panels, vertical and one horizontal */
        [-w / 2 + pier / 2, w / 2 - pier / 2].forEach(function (cx) { box(0.04, h, 0.02, M.reveal, cx, h / 2, 0.006, g); });
        box(dw, 0.04, 0.02, M.reveal, 0, dh + 1.6, 0.006, g);
        /* the parapet's galvanized coping */
        box(w, 0.12, t + 0.12, M.galv, 0, h + 0.06, -t / 2, g, 0.02);
        /* the jambs and head, galvanized steel angles */
        [-1, 1].forEach(function (s) { box(0.28, dh, 0.42, M.galv, s * (dw / 2 + 0.14), dh / 2, -0.05, g, 0.03); box(0.12, dh, 0.12, M.galvDark, s * (dw / 2 - 0.06), dh / 2, -0.32, g); });
        box(dw + 0.56, 0.3, 0.42, M.galv, 0, dh + 0.15, -0.05, g, 0.03);
        /* the raised leaf's bottom rail, just showing below the header */
        box(dw - 0.1, 0.22 * o.leaf, 0.16, M.galvDark, 0, dh - 0.11 * o.leaf, -0.42, g, 0.02);
        if (!o.lit) {
          /* a construction bay keeps its leaf part way down: ribbed steel panel from the header to `leafDown` */
          var ld = N.LEAF_DOWN, leaf = box(dw - 0.1, dh - ld, 0.1, M.leaf, 0, ld + (dh - ld) / 2, -0.5, g);
          for (var r2 = 0; r2 < 8; r2++) box(dw - 0.1, 0.04, 0.03, M.galvDark, 0, ld + 0.1 + r2 * (dh - ld - 0.2) / 7, -0.43, g);
          box(dw - 0.1, 0.14, 0.14, M.galvDark, 0, ld + 0.07, -0.45, g, 0.02);
        }
        /* the bay: floor, back wall, side walls, roof */
        var fl = new THREE.Mesh(new THREE.PlaneGeometry(w - 0.4, D), o.lit ? M.floor : M.freshSlab); fl.rotation.x = -Math.PI / 2; fl.position.set(0, 0.012, -t - D / 2); fl.receiveShadow = true; uvb(fl, 3); g.add(fl);
        box(w, h, 0.3, M.backWall, 0, h / 2, -t - D, g);
        [-1, 1].forEach(function (s) { box(0.3, h, D, M.backWall, s * (w / 2 - 0.15), h / 2, -t - D / 2, g); });
        var roof = box(w - 0.02, 0.3, D, M.roof, 0, h - 0.6, -t - D / 2 - 0.01, g); roof.castShadow = true;
        /* the high bay lamp rows, lit or off: three rows of five fixtures at 11 m */
        var lamps = new THREE.Group(); g.add(lamps);
        for (var r = -1; r <= 1; r++) for (var k = 0; k < 5; k++) {
          var lx = r * 4.6, lz = -t - 3 - k * 5.6, ly = N.LAMP_Y;
          var housing = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.55, 0.32, 20), M.lampOff); housing.position.set(lx, ly + 0.18, lz); housing.castShadow = true; lamps.add(housing);
          var lens = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.04, 20), o.lit && o.lamps ? M.lampOn : M.lampLens); lens.position.set(lx, ly, lz); lamps.add(lens);
          var rod = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, h - 0.6 - ly, 6), M.lampOff); rod.position.set(lx, (h - 0.6 + ly) / 2, lz); lamps.add(rod);
        }
        if (o.lit && o.lamps) {
          /* the bay's own light: warm, shadowless, pooled on the line so the back wall stays dark */
          [-5, -14, -23].forEach(function (z) {
            var sp = new THREE.SpotLight(N.LAMP_WARM, N.BAY_LIGHT, 22, 0.8, 0.7, 2); sp.position.set(0, N.LAMP_Y - 0.3, z); sp.castShadow = false;
            sp.target.position.set(0, 0, z - 1.5); g.add(sp); g.add(sp.target);
          });
          var glow = new THREE.PointLight(N.LAMP_WARM, N.BAY_GLOW, 34, 2); glow.position.set(0, 7, -12); glow.castShadow = false; g.add(glow);
        }
        g.userData.keepOrigin = true; g.userData.door = { w: dw, h: dh }; g.userData.depth = D; g.userData.lamps = lamps;
        return g;
      }
    });

    /* A PLANT WALL: `bays` bays side by side along +x from the origin, each lit or dark per `lit`. userData.doors gives
     * each door's centre x. The wall face is z 0, the bays run to -z. */
    K.define("plant_wall", {
      size: [120, 13, 30],
      options: { lit: [true, true, true, true, false], furnish: true },
      note: "A tilt up plant wall of vertical lift door bays, each bay lit or dark. Drawn to illustrate, the bays in the order of a table, not a site.",
      make: function (o) {
        var g = new THREE.Group(), doors = [];
        o.lit.forEach(function (on, i) {
          var b = K.make("plant_bay", { lit: on }); b.position.set(N.BAY.w / 2 + i * N.BAY.w, 0, 0); g.add(b);
          if (!on && o.furnish) N.furnish(K, b);
          doors.push({ x: N.BAY.w / 2 + i * N.BAY.w, lit: on, bay: b });
        });
        g.userData.keepOrigin = true; g.userData.doors = doors;
        return g;
      }
    });

    /* A LINE CARRIER: a steel skillet 6.0 by 2.8 m, 0.45 m high, on two floor rails, lifting pads on top. userData.seat
     * is the height a body sits at. */
    K.define("line_carrier", {
      size: [2.8, 0.45, 6.0],
      options: { rails: 8 },
      note: "A steel assembly line skillet on a floor track, with lifting pads. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group();
        box(2.8, 0.18, 6.0, M.steel, 0, 0.3, 0, g, 0.03);
        [-1, 1].forEach(function (s) { box(0.16, 0.22, 6.0, M.steel, s * 1.25, 0.14, 0, g, 0.02); box(0.07, 0.03, Math.min(o.rails, 6.0), M.rail, s * 0.9, 0.015, 0, g); });
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (p) { box(0.3, 0.1, 0.3, M.galvDark, p[0] * 0.75, 0.44, p[1] * 1.6, g, 0.02); });
        g.userData.keepOrigin = true; g.userData.seat = 0.49;
        return g;
      }
    });

    /* A BOLLARD: a galvanized steel pipe filled with concrete, 1.1 m tall, with a domed cap. */
    K.define("bollard", {
      size: [0.3, 1.2, 0.3],
      options: {},
      note: "A concrete filled galvanized pipe bollard. Drawn to illustrate.",
      make: function () {
        var g = new THREE.Group();
        var p = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 1.1, 24), M.galv); p.position.y = 0.55; p.castShadow = p.receiveShadow = true; g.add(p);
        var cap = new THREE.Mesh(new THREE.SphereGeometry(0.14, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), M.grout); cap.position.y = 1.1; cap.castShadow = true; g.add(cap);
        g.userData.keepOrigin = true; return g;
      }
    });

    /* AN ANCHOR BOLT SET: four threaded galvanized rods `proud` above a sealed slab on a square, each with a plate
     * washer and a hex nut, set in a pale grout pocket. The slab is the floor the frame provides. */
    K.define("anchor_bolt_set", {
      size: [0.8, 0.32, 0.8],
      options: { square: 0.5, proud: 0.3, rod: 0.017 },
      note: "Four threaded anchor rods with plate washers and hex nuts in a grout pocket, waiting for a machine base. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), s = o.square / 2;
        var pocket = TXT.roundedBox(o.square + 0.34, 0.05, o.square + 0.34, 0.02, M.grout); pocket.position.y = 0.025; pocket.castShadow = true; pocket.receiveShadow = true; g.add(pocket);
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (p) {
          var x = p[0] * s, z = p[1] * s;
          var rod = new THREE.Mesh(new THREE.CylinderGeometry(o.rod, o.rod, o.proud, 16), M.thread); rod.position.set(x, o.proud / 2 + 0.02, z); rod.castShadow = rod.receiveShadow = true; g.add(rod);
          var washer = TXT.roundedBox(0.09, 0.01, 0.09, 0.003, M.galv); washer.position.set(x, 0.056, z); washer.castShadow = washer.receiveShadow = true; g.add(washer);
          var nut = new THREE.Mesh(new THREE.CylinderGeometry(o.rod * 2, o.rod * 2, 0.034, 6), M.galv); nut.position.set(x, 0.078, z); nut.rotation.y = 0.3 * p[0]; nut.castShadow = nut.receiveShadow = true; g.add(nut);
          var top = new THREE.Mesh(new THREE.CylinderGeometry(o.rod * 2, o.rod * 2, 0.03, 6), M.galv); top.position.set(x, o.proud - 0.04, z); top.castShadow = true; g.add(top);
        });
        g.userData.keepOrigin = true; return g;
      }
    });

    /* A TOOL CRATE: a plywood crate on three skids with steel strapping and a blank stencil panel, `open` takes the
     * front face off to show a machine wrapped in film. */
    K.define("tool_crate", {
      size: [2.4, 1.9, 1.8],
      options: { w: 2.4, h: 1.7, d: 1.8, open: false },
      note: "A plywood shipping crate for a machine tool on skids, strapped, its stencil panel blank. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), w = o.w, h = o.h, d = o.d, y0 = 0.16;
        [-1, 0, 1].forEach(function (s) { box(0.12, 0.16, d + 0.1, M.ply, s * (w / 2 - 0.15), 0.08, 0, g); });
        var shell = [
          [w, 0.02, d, 0, y0 + h, 0], [w, h, 0.02, 0, y0 + h / 2, -d / 2], [0.02, h, d, -w / 2, y0 + h / 2, 0], [0.02, h, d, w / 2, y0 + h / 2, 0], [w, 0.02, d, 0, y0, 0]
        ];
        if (!o.open) shell.push([w, h, 0.02, 0, y0 + h / 2, d / 2]);
        shell.forEach(function (p) { var b = box(p[0], p[1], p[2], M.ply, p[3], p[4], p[5], g); uvb(b, 1.2); });
        /* cleats along the edges */
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (p) { box(0.1, h, 0.1, M.ply, p[0] * (w / 2 - 0.04), y0 + h / 2, p[1] * (d / 2 - 0.04), g); });
        /* two steel straps round the crate */
        [-0.6, 0.6].forEach(function (x) { box(0.05, 0.012, d + 0.06, M.strap, x * w / 2, y0 + h + 0.016, 0, g); [-1, 1].forEach(function (s) { box(0.05, h, 0.012, M.strap, x * w / 2, y0 + h / 2, s * (d / 2 + 0.016), g); }); });
        if (!o.open) box(0.9, 0.5, 0.01, M.grout, 0, y0 + h * 0.62, d / 2 + 0.016, g);
        else { var mach = box(w * 0.7, h * 0.8, d * 0.6, M.film, 0, y0 + 0.02 + h * 0.4, 0, g, 0.12); mach.castShadow = true; }
        g.userData.keepOrigin = true; return g;
      }
    });

    /* A TRIPOD WORK LAMP: three splayed legs, a 1.8 m mast in yellow, an LED head facing +z that glows, and a small
     * warm shadowless light so its pool is real. */
    K.define("tripod_work_lamp", {
      size: [0.9, 1.95, 0.9],
      options: { aim: -0.35, light: 1, shadow: false },
      note: "A tripod LED work lamp on a yellow mast with its cord on the floor. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), top = [0, 0.7, 0];
        for (var i = 0; i < 3; i++) { var a = i * Math.PI * 2 / 3 + 0.4; var foot = [Math.cos(a) * 0.45, 0.01, Math.sin(a) * 0.45]; var leg = K.bar(foot, top, 0.014, M.lampBody); leg.castShadow = true; g.add(leg); }
        var mast = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.025, 1.2, 10), M.lampBody); mast.position.y = 1.3; mast.castShadow = true; g.add(mast);
        var head = new THREE.Group(); head.position.set(0, 1.92, 0); head.rotation.x = o.aim; g.add(head);
        var hb = TXT.roundedBox(0.34, 0.26, 0.1, 0.02, M.strap); hb.castShadow = true; head.add(hb);
        var face = new THREE.Mesh(new THREE.PlaneGeometry(0.28, 0.2), M.workLamp); face.position.z = 0.052; head.add(face);
        [-1, 1].forEach(function (s) { var fin = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.012, 0.06), M.strap); fin.position.set(0, s * 0.09, -0.07); head.add(fin); });
        if (o.light) {
          var pl = new THREE.PointLight(0xfff0d6, N.WORK_LIGHT * o.light, 9, 2); pl.position.set(0, 1.85, 0.25); pl.castShadow = !!o.shadow;
          if (o.shadow) { pl.shadow.mapSize.set(2048, 2048); pl.shadow.radius = 2; pl.shadow.bias = -0.0005; pl.shadow.camera.near = 0.05; pl.shadow.camera.far = 10; }
          g.add(pl);
        }
        var cord = K.cable([0, 0.9, 0], [0.9, 0.012, 1.2], 0.25, 0.008, M.strap); g.add(cord);
        g.userData.keepOrigin = true; return g;
      }
    });

    /* A BATTERY ENCLOSURE, illustrative and unmarked: a 7.2 by 1.6 m white louvred steel cabinet 2.5 m tall on a grey
     * plinth, door seams and a roof cap. Its long side faces +z. */
    K.define("megapack_unit", {
      size: [7.2, 2.7, 1.7],
      options: {},
      note: "An illustrative utility battery enclosure, white louvred steel on a plinth, no maker's design or mark.",
      make: function () {
        var g = new THREE.Group();
        box(7.3, 0.18, 1.75, M.plinth, 0, 0.09, 0, g, 0.02);
        var body = box(7.2, 2.4, 1.6, M.white, 0, 0.18 + 1.2, 0, g, 0.04); K.uvBox(body.geometry, 1.2);
        box(7.3, 0.08, 1.7, M.plinth, 0, 2.62, 0, g, 0.02);
        for (var i = 1; i < 6; i++) box(0.025, 2.2, 0.02, M.reveal, -3.6 + i * 1.2, 1.38, 0.81, g);
        [-1, 1].forEach(function (s) { box(0.04, 0.3, 0.04, M.plinth, s * 3.2, 1.4, 0.82, g); });
        g.userData.keepOrigin = true; return g;
      }
    });

    /* AN UNCLAD STEEL FRAME in red oxide primer: W section columns on a `bay` metre grid, `cols` by `rows`, rising
     * `height` to open web joists, rod X bracing in the end bays, base plates on a slab the frame provides. */
    K.define("steel_frame", {
      size: [27, 14.5, 18],
      options: { cols: 4, rows: 3, bay: 9, height: 14 },
      note: "An unclad structural steel frame in red oxide primer, W columns, open web joists and rod bracing. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), H = o.height, B = o.bay, W0 = -(o.cols - 1) * B / 2, Z0 = -(o.rows - 1) * B / 2;
        function column(x, z) {
          var c = new THREE.Group(); c.position.set(x, 0, z);
          box(0.36, H, 0.025, M.primer, 0, H / 2, 0.18, c); box(0.36, H, 0.025, M.primer, 0, H / 2, -0.18, c); box(0.018, H, 0.34, M.primer, 0, H / 2, 0, c);
          box(0.6, 0.03, 0.6, M.galv, 0, 0.015, 0, c);
          g.add(c);
        }
        for (var i = 0; i < o.cols; i++) for (var j = 0; j < o.rows; j++) column(W0 + i * B, Z0 + j * B);
        /* joists along x on each row line: top and bottom chords with diagonals */
        for (var r = 0; r < o.rows; r++) {
          var z = Z0 + r * B, L = (o.cols - 1) * B;
          box(L, 0.12, 0.14, M.primer, 0, H - 0.06, z, g); box(L, 0.1, 0.12, M.primer, 0, H - 1.1, z, g);
          for (var k = 0; k < (o.cols - 1) * 6; k++) {
            var xa = W0 + k * B / 6, xb = xa + B / 6, up = k % 2 === 0;
            var d = K.bar([xa, up ? H - 1.1 : H - 0.06, z], [xb, up ? H - 0.06 : H - 1.1, z], 0.025, M.primer); d.castShadow = true; g.add(d);
          }
        }
        /* girders along z at each column line */
        for (var c2 = 0; c2 < o.cols; c2++) box(0.14, 0.5, (o.rows - 1) * B, M.primer, W0 + c2 * B, H - 0.3, 0, g);
        /* girts, cold formed channels between the columns at 4.5 and 9 m on the front line and both sides */
        [4.5, 9].forEach(function (gy) {
          var zf = Z0 + (o.rows - 1) * B; box((o.cols - 1) * B, 0.2, 0.06, M.primer, 0, gy, zf + 0.22, g);
          [W0, W0 + (o.cols - 1) * B].forEach(function (xs) { box(0.06, 0.2, (o.rows - 1) * B, M.primer, xs + (xs < 0 ? -0.22 : 0.22), gy, 0, g); });
        });
        /* rod X bracing in the two end bays of the front line */
        [[0, 1], [o.cols - 2, o.cols - 1]].forEach(function (p) {
          var xa = W0 + p[0] * B, xb = W0 + p[1] * B, zf = Z0 + (o.rows - 1) * B;
          var a = K.bar([xa, 0.4, zf], [xb, H - 1.2, zf], 0.03, M.galvDark), b = K.bar([xb, 0.4, zf], [xa, H - 1.2, zf], 0.03, M.galvDark);
          a.castShadow = b.castShadow = true; g.add(a, b);
        });
        g.userData.keepOrigin = true; g.userData.columns = { x0: W0, z0: Z0, bay: B, cols: o.cols, rows: o.rows };
        return g;
      }
    });

    /* A COVERED POD: a two seat car under a fitted grey fabric cover, 4.2 by 1.95 m and 1.45 m tall, a hem with folds
     * just above the wheels, the four wheels showing. Length runs along z, the nose on +z. No maker's design. */
    K.define("covered_pod", {
      size: [2.0, 1.5, 4.3],
      options: {},
      note: "A two seat car under a fitted grey fabric cover: one continuous lofted cloth from roof to a hem of folds just above the tyres, nothing of the car beneath showing through but its mass. No glass, mirror, seam, plate or maker's design. Drawn to illustrate.",
      make: function () {
        var g = new THREE.Group(), L = 4.2, Wd = 1.94, base = 0.4;
        /* THE CLOTH: a box of segments pushed out to a rounded superellipsoid, then given the car's side profile, a
         * short low nose, one swept cabin and a short tail, the way a cover lies over a small two seat body */
        var geo = new THREE.BoxGeometry(2, 2, 2, 40, 18, 80), pos = geo.attributes.position, v = new THREE.Vector3();
        var top = function (t) { return 0.92 + 0.5 * Math.exp(-Math.pow((t + 0.08) / 0.5, 2)) - 0.1 * Math.max(0, t - 0.55); };
        for (var i = 0; i < pos.count; i++) {
          v.fromBufferAttribute(pos, i);
          var n = Math.pow(Math.pow(Math.abs(v.x), 4) + Math.pow(Math.abs(v.y), 4) + Math.pow(Math.abs(v.z), 4), 0.25);
          var x = v.x / n, y = v.y / n, z = v.z / n;
          var up = (y + 1) / 2, H = top(z);
          var X = x * Wd / 2 * (1 - 0.2 * Math.pow(Math.max(0, up - 0.45), 1.4)), Y = base + up * (H - base), Z = z * L / 2;
          /* tension wrinkles where the cloth pulls over the shoulders, a few millimetres, never a pattern a reader sees */
          var w = 0.006 * Math.sin(Z * 9 + X * 3) * Math.sin(Y * 11) * up;
          pos.setXYZ(i, X + Math.sign(X) * w, Y, Z);
        }
        geo.computeVertexNormals();
        var shell = new THREE.Mesh(geo, M.fabric); g.add(shell);
        /* four tyres, showing below the hem */
        [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(function (p) {
          var t = new THREE.Mesh(new THREE.CylinderGeometry(0.33, 0.33, 0.22, 32), M.tyre); t.rotation.z = Math.PI / 2; t.position.set(p[0] * (Wd / 2 - 0.2), 0.33, p[1] * 1.32); g.add(t);
        });
        /* THE HEM: the cloth's loose lower edge, a superellipse in plan just outside the shell, falling in folds to
         * a quarter metre above the floor */
        var hx = Wd / 2 * 1.015, hz = L / 2 * 1.01;
        var hem = new THREE.CylinderGeometry(1, 1, 0.3, 240, 6, true), hp = hem.attributes.position;
        for (var k = 0; k < hp.count; k++) {
          v.fromBufferAttribute(hp, k);
          var th = Math.atan2(v.z, v.x), c = Math.cos(th), sn = Math.sin(th), drop = (0.15 - v.y) / 0.3;
          var fold = 1 + (0.004 + 0.02 * drop) * (0.6 * Math.sin(th * 23 + 1.3 * Math.sin(th * 4)) + 0.4 * Math.sin(th * 41 + 0.5));
          var hxx = hx * Math.sign(c) * Math.pow(Math.abs(c), 0.5) * fold, hzz = hz * Math.sign(sn) * Math.pow(Math.abs(sn), 0.5) * fold;
          hp.setXYZ(k, hxx, v.y - drop * drop * 0.012 * (1 + Math.sin(th * 23 + 1.3 * Math.sin(th * 4))), hzz);
        }
        hem.computeVertexNormals();
        var skirt = new THREE.Mesh(hem, M.fabric); skirt.position.y = 0.36; g.add(skirt);
        g.traverse(function (m) { if (m.isMesh) m.castShadow = m.receiveShadow = true; });
        g.userData.keepOrigin = true; return g;
      }
    });
  };

  /* A CONSTRUCTION BAY'S FLOOR, in the bay's own frame (door at z 0, the bay running to -z): bolt groups where machine
   * bases will stand, a taped empty pad, a crate. The same set on every frame that looks into the dark bay. */
  N.furnish = function (K, bay) {
    var y = 0.014;
    [[-2.2, -4.2], [1.8, -3.4], [-1.4, -8.0], [2.6, -7.4]].forEach(function (p, i) { var b = K.make("anchor_bolt_set", { square: 0.5, proud: 0.32 }); b.position.set(p[0], y, p[1]); b.rotation.y = 0.05 * i; bay.add(b); });
    var pad = K.make("machine_pad", { tape: N.ACCENT, tapeLit: true, cordTop: N.LAMP_Y }); pad.position.set(0.4, y, -12.5); bay.add(pad);
    var cr = K.make("tool_crate", { open: false }); cr.position.set(-4.6, 0, -14); cr.rotation.y = 0.2; bay.add(cr);
    var cr2 = K.make("tool_crate", { open: true }); cr2.position.set(4.4, 0, -16.5); cr2.rotation.y = -0.15 + Math.PI; bay.add(cr2);
    return bay;
  };

  /* A TAPED OUTLINE on a slab, w by d metres, tape `tw` wide, in bluebonnet held outside the tone curve: where a
   * machine is planned and not yet installed. Origin at its centre on the slab. */
  N.tapeRect = function (THREE, K, w, d, tw) {
    var g = new THREE.Group(), M = N.mats(THREE, K);
    [[w, tw, 0, -d / 2 + tw / 2], [w, tw, 0, d / 2 - tw / 2], [tw, d - 2 * tw, -w / 2 + tw / 2, 0], [tw, d - 2 * tw, w / 2 - tw / 2, 0]].forEach(function (t) {
      var m = new THREE.Mesh(new THREE.BoxGeometry(t[0], 0.004, t[1]), M.tape); m.position.set(t[2], 0.004, t[3]); m.userData.txWear = false; g.add(m);
    });
    return g;
  };
  N.BAY_LIGHT = 5200;
  N.WORK_LIGHT = 150;
  N.BAY_GLOW = 1400;
  N.LAMP_Y = 7.3;
  N.LEAF_DOWN = 4.6;

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
      ".hook, .dek, .kick, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }",
      /* the footer lines carry a tight halo only: a 14 px blur read as a smudge on a lit apron */
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



  /* ---- the relief bench: the apron and a steel plate in plan ------------------------------- */
  /* Linear albedo per material id, with tooth in the albedo rather than the height so a low key never turns noise
   * into a leopard print. Everything outside the subject stays near black. */
  N.M = { VOID: 0, SLAB: 1, CHANNEL: 2, RAIL: 3, STOP: 4, PLATE: 5, ALU: 6, IRON: 7, TAPE: 8, JOINT: 9 };
  var BASE = {
    0: [0.004, 0.004, 0.006],
    1: [0.055, 0.053, 0.050],   /* sealed concrete apron, dark */
    2: [0.012, 0.012, 0.013],   /* the channel floor, black */
    3: [0.55, 0.56, 0.58],      /* crowned steel rail */
    4: [0.30, 0.31, 0.32],      /* galvanized stop block */
    5: [0.020, 0.020, 0.022],   /* blackened steel plate */
    6: [0.30, 0.31, 0.33],      /* anodised aluminium fins */
    7: [0.045, 0.043, 0.042],   /* cast iron */
    8: [0.085, 0.13, 0.52],     /* bluebonnet tape, linear, set so it grades to the accent */
    9: [0.010, 0.010, 0.010]    /* a saw cut joint */
  };
  N.SPEC = { 1: [0.10, 14], 2: [0.02, 4], 3: [0.75, 60], 4: [0.45, 30], 5: [0.12, 16], 6: [0.40, 26], 7: [0.10, 8], 8: [0.20, 14] };
  N.albedo = function (X, Y, m) {
    var b = BASE[m] || BASE[0], n = global.TX && TX.simplex2 ? TX.simplex2(X * 0.07, Y * 0.07) * 0.5 + TX.simplex2(X * 0.37, Y * 0.37) * 0.3 : 0;
    var k = 1 + (m === 1 ? 0.75 : (m === 5 ? 0.6 : 0.08)) * n;
    if ((m === 1 || m === 5) && global.TX) { var f = TX.simplex2(X * 1.9, Y * 1.9); k += f > 0.6 ? 0.45 : (f < -0.7 ? -0.3 : 0); }
    return [b[0] * k, b[1] * k, b[2] * k];
  };

  global.CH = N;
})(this);
