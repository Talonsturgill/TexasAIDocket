/* deck/2026-11-03-scalelane.js — the chassis for the 2026-11-03 deck: Aurora Innovation's third quarter letter, filed
 * with the SEC on October 28th, 2026, on a driverless truck that now decides for itself at a weigh station and will
 * drive straight into customer sites in November, and on the same company's truck build six weeks behind plan
 * (tx-2026-0239).
 *
 * THE VISUAL ARGUMENT. Scale lane. The deck is built where the machine makes a call a driver used to make: a
 * weigh station on an interstate at night, one LED flood over the scale deck, the tractor with nobody in its seat.
 * What exists is lit and drawn in its own material, steel, concrete, a white tractor. What the letter says will
 * happen and has not is laid in primer rust. The company's own figures are drawn in steel at one scale.
 *
 * THE WORLD. floodlit, a STAGED world: a black sky, one cold flood high on one side, the subject in its pool and
 * the interstate behind it gone dark. It is what a weigh station and a guard gate are at night.
 *
 * THE LIGHT is azimuth 52, elevation 38. +x is east and +z is south. The flood stands high to the south east, so a
 * camera looking north (-z) has the key upper right, every lit edge is on the right and every cast runs to the
 * lower left. TXBENCH reliefs read the same declaration: raked from the upper right, casting to the lower left.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `truck_scale` (a weigh station's scale deck in steel
 * plate sections between concrete approaches, kerb rails and a load cell pit line), `scale_house` (the station's
 * booth with a lit window on the scale), `scale_signal` (the lamp head over the lane that tells a truck to cross
 * the scale or bypass it), `flood_pole` (a galvanized pole with an LED flood head) and `guard_gate` (a customer
 * site's guard booth, a striped boom arm and a card reader pedestal). Drawn to illustrate, to no station's and no
 * maker's design, in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue
 * the lift.
 *
 * THE ACCENT is rust, #8C5A3C, read as red oxide primer, the colour of steel before it is finished, and it means ONE
 * thing: something Aurora's letter says WILL happen and has not. The stop bar at November's gate, the expected
 * production stop on the rule, Charger's planned chord on the map, the 200 and the 1,000 stalls. It never touches a
 * truck that exists or a figure the letter reports. Lit and in its own material means it exists; rust means planned.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the station, the models and the way
 * type is seated. Every count a frame draws is read from figures.json in that frame's own code. The chassis types
 * no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("scalelane.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "scalelane",
    light: { az: 52, el: 38 },
    sky: "floodlit",
    ground: "#08090C",
    material: "#C9CDD2",
    accent: "#8C5A3C",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.08, filmic: true,
      lift: [0.002, 0.003, 0.006], gain: [1.0, 1.0, 1.0], vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.12, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261103 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080; N.H = 1350; N.SEED = 20261103; N.INK = "#ECEEF0";
  N.RUST = "#8C5A3C";   /* brand.yaml's rust, read as primer: what the letter says will happen and has not, and nothing else */
  /* THE STATION, in metres. The interstate runs along z (north is -z). The weigh station's ramp leaves the right
   * lane to the east, the scale lane runs north at x = 0 over the scale deck, the bypass lane runs beside it at
   * x = 5, and the scale house stands west of the deck. */
  N.STA = { scaleX: 0, bypassX: 5.2, deckZ: 0, deckLen: 21.3, deckW: 3.4, houseX: -6.8, houseZ: 2, signalZ: 26, floodX: 9, floodZ: 4 };
  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.truck_scale) return;
    function shade(o) { o.traverse(function (c) { if (c.isMesh) { c.castShadow = c.receiveShadow = true; } }); return o; }
    var M = {
      conc: function () { return K.finish.concrete(); },
      steel: K.mat("sl-deck", { color: 0x5c6167, metalness: 0.75, roughness: 0.48 }),
      steelDark: K.mat("sl-deckd", { color: 0x2f3337, metalness: 0.7, roughness: 0.55 }),
      yellow: K.mat("sl-yellow", { color: 0xd8a51c, roughness: 0.55, metalness: 0.1 }),
      black: K.mat("sl-black", { color: 0x141518, roughness: 0.6 }),
      white: K.mat("sl-white", { color: 0xe6e7e4, roughness: 0.5 }),
      red: K.mat("sl-red", { color: 0xa3201b, roughness: 0.5 }),
      galv: K.finish.galvanized(),
      glass: K.finish.glass(0x1d2a33),
      lamp: K.mat("sl-lamp", { color: 0x0b0d10, emissive: 0xf2f6ff, emissiveIntensity: 9 }),
      go: K.mat("sl-go", { color: 0x07120b, emissive: 0x62e08e, emissiveIntensity: 7 }),
      rust: K.mat("sl-rust", { color: 0x8c5a3c, roughness: 0.62, metalness: 0.05, emissive: 0x3a1c0e, emissiveIntensity: 0.35 }),
      amber: K.mat("sl-amber", { color: 0x3a2008, emissive: 0xffa43a, emissiveIntensity: 6, roughness: 0.25 }),
      dim: K.mat("sl-dim", { color: 0x15181b, emissive: 0x2a2f33, emissiveIntensity: 0.4, roughness: 0.3 }),
      warm: K.mat("sl-warm", { color: 0x111111, emissive: 0xffd9a8, emissiveIntensity: 3.0 })
    };

    /* A TRUCK SCALE: a weigh station's in-ground scale, about 21.3 m long and 3.4 m wide, in three steel deck
     * sections with a visible joint and a row of anti-skid plate texture, flush with concrete approach slabs at both
     * ends, yellow kerb rails along both edges so a tyre can't drop off, and a dark pit line round the deck where it
     * floats on its load cells. Origin at the deck's centre; the lane runs along z. */
    K.define("truck_scale", {
      size: [4.4, 0.32, 33.3],
      options: { sections: 3, approach: 6, wear: 0.5 },
      note: "An in-ground truck scale in steel deck sections between concrete approaches, kerb rails and a pit line.",
      make: function (o) {
        var G = new THREE.Group(), L = N.STA.deckLen, Wd = N.STA.deckW, n = o.sections || 3, ap = o.approach || 6;
        /* the plate texture: a raised diamond tread in the bump channel, rust at the joints in the map */
        var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(31);
        x.fillStyle = "#8a8f95"; x.fillRect(0, 0, 256, 256);
        for (var j = 0; j < 16; j++) for (var i = 0; i < 16; i++) { var cx0 = i * 16 + (j % 2) * 8, cy0 = j * 16; x.save(); x.translate(cx0 + 8, cy0 + 8); x.rotate(((i + j) % 2 ? 1 : -1) * 0.6); x.fillStyle = "rgba(200,205,210,0.55)"; x.fillRect(-5, -1.4, 10, 2.8); x.restore(); }
        for (var k = 0; k < 900; k++) { x.fillStyle = "rgba(" + (60 + r() * 40 | 0) + "," + (50 + r() * 30 | 0) + "," + (40 + r() * 20 | 0) + "," + (0.04 + r() * 0.08) + ")"; x.fillRect(r() * 256, r() * 256, 1 + r() * 4, 1 + r() * 4); }
        var tex = new THREE.CanvasTexture(c); tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.colorSpace = THREE.SRGBColorSpace; tex.repeat.set(Wd / 0.6, (L / n) / 0.6); tex.anisotropy = 8;
        var plate = K.mat("sl-plate", { color: 0xffffff, map: tex, bumpMap: tex, bumpScale: 0.6, metalness: 0.7, roughness: 0.5 });
        var secL = (L - (n - 1) * 0.03) / n;
        for (var s = 0; s < n; s++) {
          var z = -L / 2 + secL / 2 + s * (secL + 0.03);
          var deck = TXT.roundedBox(Wd, 0.12, secL, 0.02, plate); deck.position.set(0, 0.2, z); G.add(deck);
        }
        /* the pit line: a dark gap all round the deck where it floats free of the foundation */
        var pit = new THREE.Mesh(new THREE.BoxGeometry(Wd + 0.12, 0.2, L + 0.12), M.black); pit.position.set(0, 0.1, 0); G.add(pit);
        /* the foundation wall's top, a narrow concrete lip round the pit */
        [-1, 1].forEach(function (sx) { var lip = K.box(0.25, 0.24, L + 0.5, M.conc(), sx * (Wd / 2 + 0.185), 0, 0, 0.02); K.uvBox(lip.geometry, 3); G.add(lip); });
        /* the approaches: concrete slabs at grade with saw cut joints */
        [-1, 1].forEach(function (sz) {
          var a = K.box(Wd + 1.0, 0.24, ap, M.conc(), 0, 0, sz * (L / 2 + ap / 2 + 0.06), 0.02); K.uvBox(a.geometry, 3); G.add(a);
        });
        /* the kerb rails: yellow steel guards along both edges of the deck and approaches */
        [-1, 1].forEach(function (sx) {
          var rail = TXT.roundedBox(0.2, 0.28, L + ap * 1.2, 0.03, M.yellow); rail.position.set(sx * (Wd / 2 + 0.42), 0.38, 0); G.add(rail);
          for (var q = -3; q <= 3; q++) { var post = K.box(0.16, 0.24, 0.16, M.steelDark, sx * (Wd / 2 + 0.42), 0.2, q * (L / 6)); G.add(post); }
        });
        return shade(G);
      }
    });

    /* A SCALE HOUSE: the station's booth beside the deck, about 4.2 m by 3.2 m, a steel clad box on a raised
     * concrete plinth with a canopy, a wide window facing the scale lit warm from inside, and a door with steps. */
    K.define("scale_house", {
      size: [4.6, 3.9, 3.6],
      options: { lit: true },
      note: "A weigh station's scale house, steel clad, a lit window on its scale side, a canopy and steps.",
      make: function (o) {
        var G = new THREE.Group();
        var clad = K.mat("sl-clad", { color: 0xbfc3c2, roughness: 0.5, metalness: 0.35, map: K.tex("corrugated") });
        var plinth = K.box(4.4, 0.6, 3.4, K.finish.concrete(), 0, 0, 0, 0.03); K.uvBox(plinth.geometry, 3); G.add(plinth);
        var body = K.box(4.2, 2.7, 3.2, clad, 0, 0.6, 0, 0.04); K.uvBox(body.geometry, 1); G.add(body);
        var roof = K.box(4.6, 0.18, 3.6, M.steelDark, 0, 3.3, 0, 0.03); G.add(roof);
        /* the window on +x (the scale side): glass, a lit interior plane behind it, a frame */
        var win = K.box(0.05, 1.1, 2.4, M.black, 2.12, 1.7, 0); G.add(win);
        var glow = K.box(0.02, 1.0, 2.3, o.lit === false ? M.dim : M.warm, 2.15, 1.75, 0); G.add(glow);
        /* the lit window reads as light, not as dark glass: the warm plane sits at the glazing line, a faint reflective
         * sheet in front of it carries the flood's highlight without hiding the room */
        var gl = new THREE.Mesh(new THREE.PlaneGeometry(2.3, 1.0), K.mat("sl-sheen", { color: 0x0a0c0e, metalness: 0.9, roughness: 0.08, transparent: true, opacity: 0.18 })); gl.rotation.y = Math.PI / 2; gl.position.set(2.165, 2.25, 0); G.add(gl);
        [-1.2, 0, 1.2].forEach(function (z) { G.add(K.box(0.06, 1.14, 0.06, M.steelDark, 2.15, 1.68, z)); });
        G.add(K.box(0.06, 0.06, 2.46, M.steelDark, 2.15, 2.8, 0)); G.add(K.box(0.06, 0.06, 2.46, M.steelDark, 2.15, 1.68, 0));
        /* the door and steps on +z */
        G.add(K.box(0.9, 2.05, 0.05, M.steelDark, -1.1, 0.6, 1.62));
        for (var s = 0; s < 3; s++) G.add(K.box(1.1, 0.2, 0.32, K.finish.concrete(), -1.1, s * 0.2, 1.75 + (2 - s) * 0.3));
        /* a wall pack lamp over the door */
        G.add(K.box(0.3, 0.18, 0.12, M.lamp, -1.1, 2.85, 1.66));
        return shade(G);
      }
    });

    /* A SCALE SIGNAL: the lamp head on a cantilever over the lane, the light that tells a truck to cross the scale
     * or keep to the bypass. Two lamps in a hooded head; `state` lights the pale go lamp (the scale is open to this
     * truck), the red lamp, or neither. No words: the meaning is the lamp. Anchored at the pole's foot. */
    K.define("scale_signal", {
      size: [6.4, 6.6, 0.6],
      anchor: "base",
      options: { state: "cross", reach: 5.2 },
      note: "A cantilevered signal head over a weigh station lane: a hooded go lamp and a red lamp.",
      make: function (o) {
        var G = new THREE.Group(), reach = o.reach || 5.2, h = 6.0;
        G.add(K.cyl(0.11, 0.13, h, M.galv, 0, 0, 0, 16));
        G.add(K.box(0.5, 0.06, 0.5, M.galv, 0, 0, 0));
        K.bar([0, h - 0.3, 0], [reach, h - 0.3, 0], 0.07, M.galv, 12, G);
        K.bar([0, h - 1.4, 0], [reach * 0.55, h - 0.3, 0], 0.04, M.galv, 8, G);
        var head = new THREE.Group(); head.position.set(reach, h - 0.95, 0); G.add(head);
        head.add(TXT.roundedBox(0.46, 1.0, 0.36, 0.05, M.black));
        /* lamps on both faces, so the head shows its aspect to the lane it governs and to the scale house behind it */
        [1, -1].forEach(function (f) {
          [[0.22, o.state === "stop" ? K.mat("sl-redlit", { color: 0x220303, emissive: 0xff2a1e, emissiveIntensity: 7 }) : M.dim], [-0.22, o.state === "cross" ? M.go : M.dim]].forEach(function (L) {
            var lens = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.04, 24), L[1]); lens.rotation.x = Math.PI / 2; lens.position.set(0, L[0], f * 0.19); head.add(lens);
            var visor = K.box(0.36, 0.025, 0.2, M.black, 0, L[0] + 0.17, f * 0.29); head.add(visor);
          });
        });
        G.userData.lamp = [reach, h - 0.95 - 0.22, 0];
        return shade(G);
      }
    });

    /* A FLOOD POLE: a tapered galvanized pole about 12 m tall with a cross arm and two LED flood heads, the panel
     * faces lit. Anchored at the foot. */
    K.define("flood_pole", {
      size: [2.4, 12.4, 0.8],
      anchor: "base",
      options: { height: 12, heads: 2 },
      note: "A tapered galvanized pole with LED flood heads, the panel faces lit.",
      make: function (o) {
        var G = new THREE.Group(), h = o.height || 12;
        G.add(K.cyl(0.09, 0.16, h, M.galv, 0, 0, 0, 16));
        G.add(K.cyl(0.4, 0.45, 0.6, K.finish.concrete(), 0, 0, 0, 20));
        K.bar([-0.9, h, 0], [0.9, h, 0], 0.05, M.galv, 8, G);
        var nh = o.heads || 2;
        for (var i = 0; i < nh; i++) {
          var hx = nh === 1 ? 0 : -0.7 + 1.4 * i / (nh - 1), hd = new THREE.Group(); hd.position.set(hx, h - 0.1, 0.1); hd.rotation.x = 0.55; G.add(hd);
          hd.add(TXT.roundedBox(0.72, 0.14, 0.56, 0.02, M.steelDark));
          var face = new THREE.Mesh(new THREE.PlaneGeometry(0.64, 0.48), M.lamp); face.rotation.x = Math.PI / 2; face.position.set(0, -0.075, 0); hd.add(face);
          for (var f = 0; f < 7; f++) hd.add(K.box(0.66, 0.06, 0.014, M.steelDark, 0, 0.07, -0.24 + f * 0.08));
          (G.userData.heads = G.userData.heads || []).push([hx, h - 0.2, 0.1]);
        }
        return shade(G);
      }
    });

    /* A GUARD GATE: a customer site's security checkpoint. A guard booth about 2.4 by 1.8 m with glass on three sides,
     * a raised island with yellow bollards, a striped boom arm about 6.5 m across the lane on a drive cabinet, and a
     * card reader pedestal at cab height whose screen is lit. `boom` 0 is down (closed), 1 is up. Front (+z) faces the
     * arriving truck; the lane runs along z on +x of the booth. */
    K.define("guard_gate", {
      size: [9.6, 3.3, 3.0],
      options: { boom: 0, reader: "lit", stopBar: true },
      note: "A guard booth on an island, a striped boom arm on its cabinet, and a lit card reader pedestal.",
      make: function (o) {
        var G = new THREE.Group();
        var isl = K.box(2.9, 0.18, 6.0, K.finish.concrete(), 0, 0, 0, 0.04); K.uvBox(isl.geometry, 3); G.add(isl);
        [-2.8, 2.8].forEach(function (z) { G.add(K.cyl(0.11, 0.11, 1.0, M.yellow, 1.25, 0.18, z, 16)); });
        var booth = new THREE.Group(); booth.position.set(-0.2, 0.18, 0); G.add(booth);
        booth.add(K.box(2.0, 0.9, 1.7, K.mat("sl-booth", { color: 0x9da3a8, roughness: 0.45, metalness: 0.4 }), 0, 0, 0, 0.03));
        booth.add(K.box(2.0, 1.25, 1.7, M.glass, 0, 0.9, 0, 0.02));
        booth.add(K.box(1.9, 1.15, 1.6, M.warm, 0, 0.95, 0));
        booth.add(K.box(2.3, 0.2, 2.0, M.steelDark, 0, 2.15, 0, 0.03));
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (p) { booth.add(K.box(0.07, 1.25, 0.07, M.steelDark, p[0] * 0.97, 0.9, p[1] * 0.82)); });
        /* the drive cabinet and boom at the island's far end, the arm reaching across the lane on +x */
        var cab = K.box(0.36, 1.05, 0.4, M.yellow, 1.25, 0.18, -2.2, 0.03); G.add(cab);
        var arm = new THREE.Group(); arm.position.set(1.25, 1.12, -2.2); arm.rotation.z = (o.boom || 0) * Math.PI / 2.1; G.add(arm);
        var segs = 12, len = 6.4;
        for (var s = 0; s < segs; s++) { var seg = TXT.roundedBox(len / segs, 0.11, 0.09, 0.02, s % 2 ? M.red : M.white); seg.position.set(0.15 + (s + 0.5) * len / segs, 0, 0); arm.add(seg); }
        /* the card reader pedestal before the gate, at a cab's window height, its screen in the accent */
        var ped = new THREE.Group(); ped.position.set(1.25, 0.18, 1.3); G.add(ped);
        ped.add(K.cyl(0.07, 0.07, 1.8, M.steelDark, 0, 0, 0, 12));
        var hd = TXT.roundedBox(0.34, 0.46, 0.22, 0.04, M.black); hd.position.set(0.05, 2.0, 0); hd.rotation.y = 0.5; ped.add(hd);
        var scr = new THREE.Mesh(new THREE.PlaneGeometry(0.22, 0.16), o.reader === "lit" ? M.go : M.dim); scr.position.set(0.12, 2.06, 0.1); scr.rotation.y = 0.5 + Math.PI / 2 - Math.PI / 2; ped.add(scr);
        /* the stop bar across the lane before the gate, in primer: November's gate is a plan, not yet true */
        if (o.stopBar) { var sb = K.box(4.0, 0.012, 0.6, M.rust, 4.5, 0.0, 3.4); G.add(sb); }
        G.userData.reader = [1.37, 2.24, 1.4];
        return shade(G);
      }
    });

    /* A CAB BEACON: an amber warning beacon on a magnetic base, about 0.16 m across and 0.13 m tall, the kind a stopped
     * driverless truck shows in place of triangles set out on the shoulder. Lit or dark. */
    K.define("cab_beacon", {
      size: [0.19, 0.17, 0.19],
      options: { lit: true },
      note: "An amber dome warning beacon on a magnetic base, lit or dark.",
      make: function (o) {
        var G = new THREE.Group();
        G.add(K.cyl(0.095, 0.095, 0.035, M.black, 0, 0, 0, 28));
        G.add(K.cyl(0.08, 0.085, 0.03, M.steelDark, 0, 0.035, 0, 28));
        var dome = new THREE.Mesh(new THREE.SphereGeometry(0.075, 28, 16, 0, Math.PI * 2, 0, Math.PI / 2), o.lit === false ? M.dim : M.amber); dome.position.y = 0.065; dome.scale.y = 1.3; G.add(dome);
        var cage = new THREE.Mesh(new THREE.TorusGeometry(0.077, 0.004, 6, 28), M.black); cage.rotation.x = Math.PI / 2; cage.position.y = 0.1; G.add(cage);
        return shade(G);
      }
    });

    /* PAINTED STALLS: a yard's parking stripes, `rows` rows of `cols` stalls at `pitch` metres, each stall bounded by
     * side stripes `stripe` m wide and `len` m long and closed by a head line across its far end, thermoplastic 4 mm
     * proud. Stalls in the near corner block `block` [cols, rows] are bead white (trucks that exist); every other stall
     * is primer (trucks the letter says will exist). Rows run toward -z from the origin, columns toward +x. Instanced,
     * so a thousand stalls cost two draw calls per colour. */
    K.define("yard_stalls", {
      size: [60, 0.004, 30], anchor: "base",
      options: { rows: 20, cols: 50, pitch: 4.4, len: 14, aisle: 10, block: [10, 2], stripe: 0.3 },
      note: "Instanced yard stalls with side stripes and head lines, a near corner block in bead white and the rest in primer.",
      make: function (o) {
        var G = new THREE.Group(), sw = o.stripe || 0.3, side = new THREE.BoxGeometry(sw, 0.004, o.len), head = new THREE.BoxGeometry(o.pitch, 0.004, sw);
        var W = { s: [], h: [] }, P = { s: [], h: [] }, bc = o.block[0], br = o.block[1];
        for (var r = 0; r < o.rows; r++) for (var c = 0; c < o.cols; c++) {
          var white = r < br && c < bc, L = white ? W : P, z = -(r * (o.len + o.aisle) + o.len / 2), x = c * o.pitch;
          L.s.push([x, 0.002, z, 0, 1]); L.h.push([x + o.pitch / 2, 0.002, z - o.len / 2, 0, 1]);
          if (c === o.cols - 1 || (white && c === bc - 1)) L.s.push([x + o.pitch, 0.002, z, 0, 1]);
        }
        var paintW = K.mat("sl-bead", { color: 0xe8e6df, roughness: 0.45, emissive: 0x15140f, emissiveIntensity: 0.4 });
        var paintP = K.mat("sl-rustpaint", { color: 0x9a6243, roughness: 0.5, emissive: 0x5a2c16, emissiveIntensity: 0.9 });
        [[W, paintW], [P, paintP]].forEach(function (q) { if (q[0].s.length) K.instances(side, q[1], q[0].s, G); if (q[0].h.length) K.instances(head, q[1], q[0].h, G); });
        G.userData.keepOrigin = true;
        G.userData.stall = function (c, r) { return [c * o.pitch + o.pitch / 2, 0, -(r * (o.len + o.aisle) + o.len / 2)]; };
        return G;
      }
    });
  };

  /* ---- helpers every frame uses ----------------------------------------------------------- */
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
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { color: 0xfbf7f0, shadowSize: size || 14, mapSize: map || 2048 }) });
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
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".lab.ru { color:#C99474; }",
      ".hook, .dek, .lab, .kick, .count, .src { font-feature-settings:\"calt\" 0; }",
      ".hook, .dek, .kick, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }",
      ".tx-site, .src { text-shadow:0 0 2px " + halo + ", 0 1px 4px " + halo2 + "; }"
    ].join("\n");
  };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) { d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px"; });
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS(); document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D2D6DA" });
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
  /* THE TRACTOR'S HEADLAMPS, ON. The kit's lens material is shared, so lighting it lights every tractor in the frame,
   * which is right: every truck in this deck is running. Glows sit on the four round lamps (the kit's bezels at x
   * ±0.78 ±0.075, y 1.52 above the tractor's base, just behind the bumper's face), and one spot throws their light down
   * the lane ahead. The truck must face +z in its own frame. */
  N.lightsOn = function (THREE, R, K, truck, o) {
    o = o || {};
    var lens = K.mat("v-lens", { color: 0xe9eef2, metalness: 0.95, roughness: 0.08 });
    lens.emissive = new THREE.Color(0xfff1d8); lens.emissiveIntensity = o.lens == null ? 6 : o.lens;
    truck.updateMatrixWorld(true);
    var inv = new THREE.Matrix4().copy(truck.matrixWorld).invert(), bb = new THREE.Box3().setFromObject(truck).applyMatrix4(inv);
    var zf = bb.max.z - 0.14, y0 = bb.min.y, out = [];
    [-1, 1].forEach(function (s) {
      [-0.075, 0.075].forEach(function (dx) {
        var p = new THREE.Vector3(s * 0.78 + dx, y0 + 1.52, zf).applyMatrix4(truck.matrixWorld); out.push(p);
        var g = new THREE.Sprite(new THREE.SpriteMaterial({ map: N.glowTex(THREE), color: 0xfff0d6, transparent: true, opacity: o.glow == null ? 0.85 : o.glow, depthWrite: false, fog: false }));
        g.scale.set(o.size || 0.55, o.size || 0.55, 1); g.position.copy(p).add(new THREE.Vector3(0, 0, 0.12).applyQuaternion(truck.getWorldQuaternion(new THREE.Quaternion()))); R.scene.add(g);
      });
    });
    if (o.beam !== false) {
      var q = truck.getWorldQuaternion(new THREE.Quaternion()), fwd = new THREE.Vector3(0, 0, 1).applyQuaternion(q);
      var c = out[0].clone().add(out[3]).multiplyScalar(0.5);
      var sp = new THREE.SpotLight(0xfff0d6, o.beam || 60, 40, 0.5, 0.6, 1.6); sp.position.copy(c).add(fwd.clone().multiplyScalar(0.3));
      sp.target.position.copy(c).add(fwd.clone().multiplyScalar(14)).setY(0); R.scene.add(sp); R.scene.add(sp.target);
    }
    return out;
  };
  /* THE FLOOD, ON: a glow at each head of a flood_pole and one spot from its height onto a target, so the pool the
   * staged world makes has a source a reader can see. The pole must not be rotated. */
  N.floodOn = function (THREE, R, pole, target, o) {
    o = o || {}; pole.updateMatrixWorld(true);
    var heads = (pole.userData.heads || []).map(function (h) { return new THREE.Vector3(h[0], h[1], h[2]).applyMatrix4(pole.matrixWorld); });
    heads.forEach(function (p) { N.lampGlow(THREE, R, [p.x, p.y - 0.15, p.z], 0xf2f5ff, o.glow || 2.2, 0); });
    if (!heads.length) return null;
    var c = heads[0].clone(); if (heads.length > 1) c.add(heads[heads.length - 1]).multiplyScalar(0.5);
    var sp = new THREE.SpotLight(0xeef2ff, o.intensity || 900, o.distance || 90, o.angle || 0.6, 0.55, 1.6);
    sp.position.copy(c); sp.target.position.set(target[0], target[1], target[2]); R.scene.add(sp); R.scene.add(sp.target);
    return sp;
  };
  /* THE DARK BAND THE TYPE STANDS IN. Light type on the dark field, and the band only ever DARKENS. */
  N.shade = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 60 : o.pad;
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "5,6,10";
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
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(5,6,10," + (Math.min(0.5, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
  };
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
