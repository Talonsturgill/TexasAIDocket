/* deck/2026-10-28-route.js — the chassis for the 2026-10-28 deck: the City of Dallas's computer vision cameras on
 * its Sanitation brush trucks (City Detect), told through the city's own October 19th, 2026 briefing to the Quality of
 * Life, Arts, and Culture Committee (tx-2026-0179).
 *
 * THE VISUAL ARGUMENT. One brush truck on its routine route, and what happens after its camera looks. The city counts
 * each step a person took after an observation, from 5,318 observations reviewed down to 101 formal enforcement, and
 * lists an accuracy measure as a next step. Every count a frame draws is read from figures.json in that frame's own code.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky, one warm seam low on the key's side, the
 * subject in a pool of light and the block behind it gone dark.
 *
 * THE LIGHT is azimuth -125, elevation 12, the last light low in the west north west. +x is east and +z is south. A
 * camera on the west side of the street looking east has the key behind its left shoulder: every lit edge faces the
 * camera's left and every cast runs long to the right and away. On a relief the key comes from the lower left and every
 * cast runs up and to the right.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `brush_truck` (a medium duty conventional cab on a
 * tandem chassis with an open steel brush body, a knuckle boom grapple loader behind the cab and two camera pods on the
 * body's front corners), `camera_pod` (the pod alone, for a close), `count_token` (one cast marker standing for one
 * item of a count) and `notice_letter` (a folded city letter). All are drawn to illustrate and to no maker's design, in
 * the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is the camera's own cold signal, #7CC6D6, and it means ONE thing: a computer vision observation, which the
 * city says is not a confirmed violation. Nothing a person decided ever carries it.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 * Every frame composes its own picture, and every quantity a frame draws is read from figures.json in that frame's
 * own code. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("route.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "route",
    light: { az: -125, el: 12 },
    sky: "lastLight",
    ground: "#08070C",
    material: "#E4E2DC",
    accent: "#7CC6D6",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.12, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261028 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261028;
  N.ACCENT = 0x7cc6d6;   /* the camera's signal, and it means ONE thing: a computer vision observation */
  N.INK = "#ECE8DF";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* a soft radial glow for a lamp, built once */
  N.glowTex = function (THREE) {
    if (N._glow) return N._glow;
    var c = document.createElement("canvas"); c.width = c.height = 64; var g = c.getContext("2d");
    var gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.18, "rgba(255,255,255,0.6)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); N._glow = new THREE.CanvasTexture(c); return N._glow;
  };

  /* ---- the materials of the world --------------------------------------------------------- */
  /* WORKED STEEL: a brush body takes limbs and stumps every day, so its plate carries dents and scuffs in a bump
   * map and streaks of rust bloom at the seams in its albedo */
  function workedSteel(THREE, seed, base) {
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = base; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 2600; i++) { var v = Math.floor(r() * 40); x.fillStyle = "rgba(" + (20 + v) + "," + (18 + v) + "," + (16 + v) + "," + (0.05 + r() * 0.1) + ")"; x.fillRect(r() * 512, r() * 512, 1 + r() * 3, 1 + r() * 2); }
    for (var k = 0; k < 90; k++) { var sx = r() * 512, sy = r() * 512, len = 30 + r() * 160;
      var g = x.createLinearGradient(sx, sy, sx, sy + len); g.addColorStop(0, "rgba(110,62,32,0.6)"); g.addColorStop(1, "rgba(96,58,34,0)");
      x.fillStyle = g; x.fillRect(sx, sy, 2 + r() * 4, len); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
  }
  function dentBump(THREE, seed) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "#808080"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < 60; i++) { var gx = r() * 256, gy = r() * 256, rr = 4 + r() * 18, g = x.createRadialGradient(gx, gy, 0, gx, gy, rr);
      g.addColorStop(0, "rgba(40,40,40,0.5)"); g.addColorStop(1, "rgba(128,128,128,0)"); x.fillStyle = g; x.beginPath(); x.arc(gx, gy, rr, 0, 6.3); x.fill(); }
    for (var j = 0; j < 220; j++) { x.strokeStyle = "rgba(" + (r() < 0.5 ? "200,200,200" : "60,60,60") + ",0.4)"; x.lineWidth = 1; x.beginPath(); var ax = r() * 256, ay = r() * 256; x.moveTo(ax, ay); x.lineTo(ax + (r() - 0.5) * 30, ay + (r() - 0.5) * 6); x.stroke(); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
  }
  /* a tyre's tread and sidewall lettering-free ribs, as a bump map wrapped round the lathe */
  function treadBump(THREE) {
    var c = document.createElement("canvas"); c.width = 512; c.height = 64; var x = c.getContext("2d");
    x.fillStyle = "#808080"; x.fillRect(0, 0, 512, 64); x.fillStyle = "#3a3a3a";
    for (var i = 0; i < 64; i++) { x.fillRect(i * 8, 18, 3, 28); x.fillRect(i * 8 + 4, 6, 2, 12); x.fillRect(i * 8 + 4, 46, 2, 12); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
  }
  N.mats = function (THREE, K) {
    if (N._m) return N._m;
    var body = workedSteel(THREE, N.SEED, "#3a3b3d"); body.repeat.set(2, 1);
    var bump = dentBump(THREE, N.SEED + 1); bump.repeat.set(3, 2);
    var m = {
      paint: new THREE.MeshPhysicalMaterial({ color: 0xe6e5df, roughness: 0.38, metalness: 0.0, clearcoat: 0.7, clearcoatRoughness: 0.28 }),
      paintDirty: new THREE.MeshPhysicalMaterial({ color: 0xcfcdc5, roughness: 0.5, metalness: 0.0, clearcoat: 0.4, clearcoatRoughness: 0.4 }),
      bodySteel: new THREE.MeshStandardMaterial({ color: 0xffffff, map: body, bumpMap: bump, bumpScale: 2.6, roughness: 0.62, metalness: 0.35 }),
      frame: new THREE.MeshStandardMaterial({ color: 0x141517, roughness: 0.55, metalness: 0.4 }),
      chrome: new THREE.MeshStandardMaterial({ color: 0xd8dbe0, roughness: 0.14, metalness: 1.0 }),
      satin: new THREE.MeshStandardMaterial({ color: 0x8a8d91, roughness: 0.35, metalness: 0.85 }),
      glass: new THREE.MeshPhysicalMaterial({ color: 0x1a2330, roughness: 0.04, metalness: 0.55, envMapIntensity: 2.2, clearcoat: 1.0, clearcoatRoughness: 0.05, reflectivity: 0.6 }),
      glassSide: new THREE.MeshPhysicalMaterial({ color: 0x1a2330, roughness: 0.04, metalness: 0.55, envMapIntensity: 2.2, clearcoat: 1.0, clearcoatRoughness: 0.05, side: THREE.DoubleSide }),
      rubber: new THREE.MeshStandardMaterial({ color: 0x18181a, roughness: 0.82, metalness: 0.0, bumpMap: treadBump(THREE), bumpScale: 2.0 }),
      wheel: new THREE.MeshStandardMaterial({ color: 0xb9bbbd, roughness: 0.42, metalness: 0.7 }),
      hydraulic: new THREE.MeshStandardMaterial({ color: 0xd7d9dc, roughness: 0.12, metalness: 1.0 }),
      boom: new THREE.MeshPhysicalMaterial({ color: 0x2c4b6e, roughness: 0.45, metalness: 0.15, clearcoat: 0.4, clearcoatRoughness: 0.4 }),
      amber: new THREE.MeshStandardMaterial({ color: 0xffa23a, emissive: 0xff8a1a, emissiveIntensity: 1.6, roughness: 0.3 }),
      amberOff: new THREE.MeshStandardMaterial({ color: 0x8a4a12, roughness: 0.35, metalness: 0.1, transparent: true, opacity: 0.92 }),
      tail: new THREE.MeshStandardMaterial({ color: 0x5a0a08, emissive: 0xc0140c, emissiveIntensity: 1.2, roughness: 0.3 }),
      head: new THREE.MeshStandardMaterial({ color: 0xf2f0e8, emissive: 0xfff2d8, emissiveIntensity: 1.4, roughness: 0.2 }),
      podShell: new THREE.MeshPhysicalMaterial({ color: 0x1c1e21, roughness: 0.35, metalness: 0.3, clearcoat: 0.6, clearcoatRoughness: 0.3 }),
      lens: new THREE.MeshPhysicalMaterial({ color: 0x050608, roughness: 0.02, metalness: 0.6, clearcoat: 1.0, clearcoatRoughness: 0.02 }),
      /* the main lens's coating holds the accent: the camera's cold colour, the one the deck reserves for what it sees */
      lensCoat: new THREE.MeshPhysicalMaterial({ color: 0x0a1418, emissive: N.ACCENT, emissiveIntensity: 1.0, toneMapped: false, roughness: 0.05, metalness: 0.2, clearcoat: 1.0, clearcoatRoughness: 0.02 }),
      /* the accent is emission at its own hex, so it holds under the dusk key and the grade */
      signal: new THREE.MeshStandardMaterial({ color: new THREE.Color(N.ACCENT).multiplyScalar(0.3), emissive: N.ACCENT, emissiveIntensity: 1.4, toneMapped: false, roughness: 0.4 }),
      bark: new THREE.MeshStandardMaterial({ color: 0x4a3b2c, roughness: 0.92 }),
      barkPale: new THREE.MeshStandardMaterial({ color: 0x7a6650, roughness: 0.9 }),
      leaf: new THREE.MeshStandardMaterial({ color: 0x46552a, roughness: 0.85, side: THREE.DoubleSide }),
      leafDry: new THREE.MeshStandardMaterial({ color: 0x5a4a2a, roughness: 0.9, side: THREE.DoubleSide }),
      paper: new THREE.MeshStandardMaterial({ color: 0xece8de, roughness: 0.92, side: THREE.DoubleSide }),
      tokenCast: new THREE.MeshStandardMaterial({ color: 0x9c9fa3, roughness: 0.38, metalness: 0.85 }),
      tokenWarm: new THREE.MeshStandardMaterial({ color: 0xcdb48a, roughness: 0.34, metalness: 0.9 })
    };
    N._m = m;
    return m;
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.brush_truck) return;
    var M = N.mats(THREE, K);
    function mesh(geo, mat, x, y, z) { var o = new THREE.Mesh(geo, mat); o.position.set(x || 0, y || 0, z || 0); o.castShadow = o.receiveShadow = true; return o; }
    function rb(w, h, d, r, mat, x, y, z) { var b = TXT.roundedBox(w, h, d, r, mat); b.position.set(x || 0, y || 0, z || 0); b.castShadow = b.receiveShadow = true; return b; }
    /* a side profile in (z, y), extruded across x by `w` and centred, with rounded edges: the body shop's way */
    function side(pts, w, bevel, mat) {
      var sh = new THREE.Shape(); sh.moveTo(pts[0][0], pts[0][1]);
      for (var i = 1; i < pts.length; i++) {
        var p = pts[i];
        if (p.length === 4) sh.quadraticCurveTo(p[0], p[1], p[2], p[3]); else sh.lineTo(p[0], p[1]);
      }
      sh.lineTo(pts[0][0], pts[0][1]);
      var g = new THREE.ExtrudeGeometry(sh, { depth: w - 2 * bevel, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 3, curveSegments: 10 });
      g.translate(0, 0, -(w - 2 * bevel) / 2); g.rotateY(-Math.PI / 2); g.computeVertexNormals();
      return mesh(g, mat);
    }
    /* A TRUCK WHEEL. A lathe tyre with a rounded shoulder and a tread bump, a steel disc with eight hand holes and a
     * hub with studs. `dual` stacks an inner wheel the way a rear axle carries two. Axis along x. */
    function wheel(R, w, dual) {
      var g = new THREE.Group(), prof = [];
      var ri = R * 0.58;
      prof.push(new THREE.Vector2(ri, -w / 2));
      for (var i = 0; i <= 10; i++) { var a = -Math.PI / 2 + Math.PI * i / 10; prof.push(new THREE.Vector2(R - 0.06 + 0.06 * Math.cos(a), (w / 2 - 0.05) * Math.sin(a) * 1.02)); }
      prof.push(new THREE.Vector2(ri, w / 2));
      var tg = new THREE.LatheGeometry(prof, 48); tg.rotateZ(Math.PI / 2);
      var copies = dual ? [-(w * 0.52), w * 0.52] : [0];
      copies.forEach(function (off) {
        var t = mesh(tg, M.rubber, off, 0, 0); g.add(t);
        var disc = mesh(new THREE.CylinderGeometry(ri * 0.98, ri * 0.98, w * 0.7, 40), M.wheel, off, 0, 0); disc.rotation.z = Math.PI / 2; g.add(disc);
      });
      var outer = dual ? w * 0.52 + w * 0.36 : w * 0.36;
      var face = mesh(new THREE.CylinderGeometry(ri * 0.9, ri * 0.94, 0.02, 40), M.wheel, outer, 0, 0); face.rotation.z = Math.PI / 2; g.add(face);
      for (var h = 0; h < 8; h++) { var a2 = h / 8 * Math.PI * 2; var hole = mesh(new THREE.CylinderGeometry(ri * 0.13, ri * 0.13, 0.022, 14), M.frame, outer + 0.003, Math.sin(a2) * ri * 0.6, Math.cos(a2) * ri * 0.6); hole.rotation.z = Math.PI / 2; g.add(hole); }
      var hub = mesh(new THREE.CylinderGeometry(ri * 0.34, ri * 0.4, 0.12, 24), M.satin, outer + 0.05, 0, 0); hub.rotation.z = Math.PI / 2; g.add(hub);
      for (var s = 0; s < 10; s++) { var a3 = s / 10 * Math.PI * 2; var stud = mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.05, 8), M.chrome, outer + 0.03, Math.sin(a3) * ri * 0.42, Math.cos(a3) * ri * 0.42); stud.rotation.z = Math.PI / 2; g.add(stud); }
      return g;
    }
    /* THE CAMERA POD. A weatherproof housing about 0.34 m long on a short swivel bracket: a rounded dark shell, a sun
     * visor over a recessed lens, a second smaller lens below it, and one status lamp in the deck's accent. Front of
     * the lens on +z. Origin at the bracket foot. */
    K.define("camera_pod", {
      size: [0.2, 0.32, 0.36],
      options: { lit: true, tilt: 0.12 },
      note: "An illustrative vehicle mounted computer vision camera pod: a dark weatherproof housing, visor, two lenses and a status lamp on a swivel bracket. Drawn to illustrate, to no maker's design.",
      make: function (o) {
        var g = new THREE.Group();
        g.add(mesh(new THREE.CylinderGeometry(0.022, 0.03, 0.12, 14), M.satin, 0, 0.06, 0));
        g.add(rb(0.09, 0.03, 0.09, 0.008, M.frame, 0, 0.012, 0));
        var head = new THREE.Group(); head.position.y = 0.2; head.rotation.x = o.tilt; g.add(head);
        head.add(rb(0.17, 0.14, 0.32, 0.035, M.podShell, 0, 0, 0));
        var vis = rb(0.19, 0.012, 0.12, 0.005, M.podShell, 0, 0.078, 0.17); vis.rotation.x = -0.08; head.add(vis);
        var bezel = mesh(new THREE.CylinderGeometry(0.052, 0.056, 0.03, 32), M.frame, 0, 0.012, 0.165); bezel.rotation.x = Math.PI / 2; head.add(bezel);
        var lens = mesh(new THREE.SphereGeometry(0.042, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), M.lensCoat, 0, 0.012, 0.172); lens.rotation.x = Math.PI / 2; lens.scale.set(1, 0.5, 1); head.add(lens);
        var lens2 = mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.02, 20), M.lens, 0.045, -0.042, 0.163); lens2.rotation.x = Math.PI / 2; head.add(lens2);
        if (o.lit) {
          var led = mesh(new THREE.SphereGeometry(0.008, 10, 8), M.signal, -0.05, -0.045, 0.162); head.add(led);
          var sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: N.glowTex(THREE), color: N.ACCENT, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, transparent: true }));
          sp.position.set(-0.05, -0.045, 0.17); sp.scale.setScalar(0.12); sp.userData.noShadow = true; head.add(sp);
        }
        g.userData.lens = [0, 0.2, 0.17];
        return g;
      }
    });
    /* THE BRUSH TRUCK. A medium duty conventional cab on a tandem axle chassis, about 9.4 m long: a sloped hood with a
     * chrome grille, a two door cab with a dark windshield and side glass, an exhaust stack, a knuckle boom grapple
     * loader on a pedestal behind the cab folded over an open steel brush body with ribbed sides and a raised front
     * bulkhead, and two camera pods on the body's front corners turned to the curb. `load` 0..1 fills the body with
     * cut limbs. `boom` 0 is folded and 1 reaches out over the curb. Front on +z. Drawn to illustrate. */
    K.define("brush_truck", {
      size: [2.6, 3.9, 9.4],
      options: { load: 0.6, boom: 0, beacon: true, lights: true, pods: true, podsLit: true, side: 1 },
      note: "An illustrative municipal brush collection truck: conventional cab, tandem chassis, open steel brush body, knuckle boom grapple loader behind the cab, two camera pods on the body's front corners. Drawn to illustrate, to no maker's design.",
      make: function (o) {
        var g = new THREE.Group(), W = 2.44, hw = W / 2, R = 0.52, zf = 4.7, zFrontAxle = 3.45;
        /* the frame rails and the bumper */
        g.add(rb(0.92, 0.26, 9.0, 0.02, M.frame, 0, 0.78, 0.15));
        g.add(rb(2.46, 0.3, 0.28, 0.05, M.satin, 0, 0.72, zf - 0.02));
        /* the hood: a side profile with the front wheel arch cut, sloping to the grille */
        var hood = [[2.55, 0.98], [zFrontAxle - 0.66, 0.98]];
        for (var ha = 0; ha <= 16; ha++) { var an = Math.PI - Math.PI * ha / 16; hood.push([zFrontAxle + 0.66 * Math.cos(an), 0.98 + 0.66 * Math.sin(an) * 0.95]); }
        hood = hood.concat([[zf - 0.1, 0.98], [zf - 0.02, 1.08], [zf, 1.62], [zf - 0.02, 1.76, zf - 0.22, 1.8], [3.4, 1.9], [2.55, 2.04]]);
        g.add(side(hood, 2.12, 0.08, M.paint));
        /* the fender skirts over the front wheels, black composite */
        [-1, 1].forEach(function (s) {
          var well = new THREE.Mesh(new THREE.CylinderGeometry(0.64, 0.64, 0.5, 28, 1, true, 0, Math.PI), new THREE.MeshStandardMaterial({ color: 0x0c0c0d, roughness: 0.9, side: THREE.DoubleSide }));
          well.rotation.z = Math.PI / 2; well.rotation.y = Math.PI / 2; well.scale.set(1, 1, 0.95); well.position.set(s * 0.82, 0.98, zFrontAxle); g.add(well);
          var lip = new THREE.Mesh(new THREE.TorusGeometry(0.665, 0.022, 8, 32, Math.PI), M.frame); lip.scale.set(1, 0.95, 1); lip.position.set(s * 1.065, 0.98, zFrontAxle); lip.rotation.y = Math.PI / 2; g.add(lip);
        });
        /* the grille, chrome surround with dark slots, and the headlamps either side */
        /* the hood's bevel stands 8 cm proud of its profile, so the grille and lamps sit on that face, not inside it */
        var zg = zf + 0.09;
        g.add(rb(1.05, 0.72, 0.06, 0.04, M.chrome, 0, 1.42, zg));
        g.add(rb(0.95, 0.62, 0.04, 0.02, M.frame, 0, 1.42, zg + 0.02));
        for (var gs = 0; gs < 7; gs++) g.add(rb(0.93, 0.022, 0.03, 0.006, M.chrome, 0, 1.17 + gs * 0.085, zg + 0.04));
        [-1, 1].forEach(function (s) {
          g.add(rb(0.4, 0.26, 0.12, 0.05, M.chrome, s * 0.8, 1.38, zg));
          g.add(rb(0.34, 0.2, 0.06, 0.04, o.lights ? M.head : M.glass, s * 0.8, 1.38, zg + 0.05));
          g.add(rb(0.14, 0.08, 0.06, 0.02, M.amber, s * 0.8, 1.18, zg));
          g.add(rb(0.08, 0.1, 0.12, 0.02, M.frame, s * 0.55, 0.62, zf + 0.12));
        });
        g.add(rb(2.5, 0.06, 0.3, 0.02, M.chrome, 0, 0.87, zf - 0.02));
        /* the cab: a profile with the door's rake, roof at 3.0 m */
        g.add(side([[0.75, 1.05], [2.6, 1.05], [2.6, 2.02], [2.32, 2.9], [2.25, 3.0, 2.1, 3.0], [0.85, 3.0], [0.75, 3.0, 0.75, 2.9]], W, 0.1, M.paint));
        /* the windshield and side glass, set a hair proud of the body */
        var ws = side([[2.62, 2.06], [2.36, 2.84], [2.3, 2.84], [2.57, 2.04]], W - 0.24, 0.02, M.glass); g.add(ws);
        [-1, 1].forEach(function (s) {
          var sg = new THREE.Shape(); sg.moveTo(2.44, 2.08); sg.lineTo(2.25, 2.78); sg.lineTo(1.05, 2.78); sg.lineTo(1.05, 2.08); sg.lineTo(2.44, 2.08);
          var geo = new THREE.ShapeGeometry(sg); geo.rotateY(-Math.PI / 2);
          var pane = mesh(geo, M.glassSide, s * (hw + 0.012), 0, 0); g.add(pane);
          /* the glass framed in black rubber, an A pillar band and a drip rail, so the cab reads as a pressed cab */
          g.add(rb(0.03, 0.06, 1.42, 0.01, M.frame, s * (hw + 0.016), 2.1, 1.74));
          g.add(rb(0.03, 0.05, 1.2, 0.01, M.frame, s * (hw + 0.016), 2.8, 1.65));
          var ap = rb(0.04, 0.78, 0.07, 0.01, M.frame, s * (hw + 0.016), 2.44, 2.36); ap.rotation.x = -0.34; g.add(ap);
          g.add(rb(0.04, 0.7, 0.06, 0.01, M.frame, s * (hw + 0.016), 2.43, 1.05));
          g.add(rb(0.03, 0.03, 1.55, 0.008, M.satin, s * (hw + 0.02), 2.97, 1.62));
          /* the hood's side louvres and the cowl seam */
          for (var lv = 0; lv < 6; lv++) g.add(rb(0.02, 0.025, 0.42, 0.006, M.frame, s * 1.07, 1.45 + lv * 0.06, 3.55));
          g.add(rb(0.015, 0.92, 0.015, 0.004, M.frame, s * 1.065, 1.5, 2.62));
          /* door seam and handle, mirror on a tube arm */
          g.add(rb(0.012, 0.86, 0.012, 0.004, M.frame, s * (hw + 0.006), 1.6, 1.0));
          g.add(rb(0.03, 0.04, 0.16, 0.01, M.satin, s * (hw + 0.02), 1.95, 1.3));
          g.add(rb(0.07, 0.44, 0.22, 0.03, M.frame, s * (hw + 0.3), 2.42, 2.42));
          g.add(rb(0.075, 0.38, 0.17, 0.02, M.glass, s * (hw + 0.3), 2.42, 2.3));
          g.add(rb(0.32, 0.025, 0.025, 0.008, M.satin, s * (hw + 0.15), 2.6, 2.42));
          g.add(rb(0.32, 0.025, 0.025, 0.008, M.satin, s * (hw + 0.15), 2.24, 2.42));
          g.add(rb(0.03, 0.62, 0.03, 0.01, M.chrome, s * (hw + 0.03), 1.75, 0.85));
          /* the step and the fuel tank under the door */
          g.add(rb(0.34, 0.04, 0.5, 0.01, M.satin, s * (hw - 0.05), 0.72, 1.55));
          var tank = mesh(new THREE.CylinderGeometry(0.3, 0.3, 1.1, 28), M.chrome, s * 0.92, 0.82, 0.55); tank.rotation.x = Math.PI / 2; g.add(tank);
        });
        /* roof: amber beacon bar and the exhaust stack behind the cab */
        if (o.beacon) { g.add(rb(1.1, 0.1, 0.24, 0.04, M.frame, 0, 3.05, 1.5)); g.add(rb(0.98, 0.09, 0.2, 0.04, M.amberOff, 0, 3.14, 1.5)); }
        for (var cm = -2; cm <= 2; cm++) g.add(rb(0.09, 0.04, 0.05, 0.01, M.amber, cm * 0.25, 3.02, 2.12));
        var stack = mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.3, 18), M.chrome, -hw + 0.18, 2.2, 0.62); g.add(stack);
        /* THE LOADER. A pedestal column behind the cab, the inner boom raised and the outer boom folded back over the body,
         * the grapple's two curved tines hanging into the load. Painted city blue, chrome rams. */
        var ped = mesh(new THREE.CylinderGeometry(0.26, 0.32, 0.5, 24), M.frame, 0.35, 1.2, 0.4); g.add(ped);
        var col = rb(0.36, 2.2, 0.36, 0.05, M.boom, 0.35, 2.4, 0.4); g.add(col);
        var k = Math.max(0, Math.min(1, o.boom || 0));
        var inner = new THREE.Group(); inner.position.set(0.35, 3.4, 0.4); inner.rotation.x = 0.06 + 0.5 * k; inner.rotation.y = k * 1.3; g.add(inner);
        var ib = rb(0.28, 0.32, 2.5, 0.05, M.boom, 0, 0, -1.15); inner.add(ib);
        var ram = mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.3, 14), M.hydraulic, 0, -0.3, -0.7); ram.rotation.x = Math.PI / 2 - 0.12; inner.add(ram);
        [-0.1, 0.1].forEach(function (hx) { var hp = [new THREE.Vector3(hx, 0.17, 0.2), new THREE.Vector3(hx, 0.2, -1.2), new THREE.Vector3(hx, 0.17, -2.3)];
          var hose = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(hp), 20, 0.018, 6, false), M.rubber); hose.castShadow = true; inner.add(hose); });
        var elbow = new THREE.Group(); elbow.position.set(0, 0, -2.4); inner.add(elbow);
        var kn = mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.4, 20), M.boom, 0, 0, 0); kn.rotation.z = Math.PI / 2; elbow.add(kn);
        var outer = new THREE.Group(); outer.rotation.x = -0.95 + 0.5 * k; elbow.add(outer);
        outer.add(rb(0.24, 0.26, 2.4, 0.05, M.boom, 0, 0, -1.15));
        var grap = new THREE.Group(); grap.position.set(0, 0, -2.4); outer.add(grap);
        var lev = new THREE.Group(); lev.rotation.x = -(outer.rotation.x + inner.rotation.x); grap.add(lev);
        lev.add(rb(0.22, 0.3, 0.22, 0.03, M.frame, 0, -0.15, 0));
        /* the rotator and a four tine clamshell grapple hanging open below it, each tine a curved tapered bar */
        lev.add(mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.18, 16), M.hydraulic, 0, -0.36, 0));
        lev.add(rb(0.5, 0.12, 0.2, 0.03, M.frame, 0, -0.5, 0));
        [-1, 1].forEach(function (s) { [-0.13, 0.13].forEach(function (zz) {
          var pts = []; for (var ti = 0; ti <= 10; ti++) { var a = ti / 10; pts.push(new THREE.Vector3(s * (0.12 + 0.62 * Math.sin(a * 2.3)), -0.5 - 0.66 * a, zz)); }
          var tg = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 24, 0.035, 8, false);
          var tine = new THREE.Mesh(tg, M.frame); tine.castShadow = true; lev.add(tine);
        }); });
        /* THE BODY. An open steel box, floor at 1.15, sides to 3.15, with vertical ribs, a top rail, a raised front
         * bulkhead with a cab shield, a barn door tailgate and rub rails. Worked steel, dented and rust streaked. */
        var bz0 = 0.0, bz1 = -4.65, by0 = 1.12, by1 = 3.1, bl = bz0 - bz1, bc = (bz0 + bz1) / 2;
        g.add(rb(W, 0.12, bl, 0.02, M.bodySteel, 0, by0, bc));
        [-1, 1].forEach(function (s) {
          g.add(rb(0.05, by1 - by0, bl, 0.01, M.bodySteel, s * (hw - 0.025), (by0 + by1) / 2, bc));
          g.add(rb(0.1, 0.1, bl + 0.04, 0.02, M.bodySteel, s * hw, by1, bc));
          g.add(rb(0.12, 0.12, bl, 0.02, M.frame, s * hw, by0 - 0.02, bc));
          for (var ri = 0; ri <= 7; ri++) { var rz = bz0 - 0.1 - ri * (bl - 0.2) / 7; g.add(rb(0.07, by1 - by0, 0.08, 0.015, M.bodySteel, s * (hw + 0.02), (by0 + by1) / 2, rz)); }
          /* the rear wheel fenders, black, over the tandem */
          g.add(rb(0.62, 0.05, 2.5, 0.02, M.frame, s * (hw - 0.31), by0 - 0.12, -3.25));
          /* tail and marker lamps */
          g.add(rb(0.18, 0.12, 0.05, 0.02, M.tail, s * (hw - 0.15), 0.98, bz1 - 0.05));
          g.add(rb(0.06, 0.04, 0.04, 0.01, M.amber, s * (hw + 0.05), by1 - 0.1, bz0 - 0.2));
        });
        g.add(rb(W, by1 - by0 + 0.5, 0.08, 0.02, M.bodySteel, 0, (by0 + by1 + 0.5) / 2, bz0));
        g.add(rb(W, 0.1, 0.5, 0.02, M.bodySteel, 0, by1 + 0.5, bz0 + 0.2));
        g.add(rb(W, by1 - by0, 0.07, 0.01, M.bodySteel, 0, (by0 + by1) / 2, bz1));
        g.add(rb(0.06, by1 - by0, 0.1, 0.01, M.frame, 0, (by0 + by1) / 2, bz1 - 0.05));
        [-0.8, -0.4, 0.4, 0.8].forEach(function (rx) { g.add(rb(0.07, by1 - by0, 0.07, 0.012, M.bodySteel, rx, (by0 + by1) / 2, bz1 - 0.06)); });
        [by0 + 0.6, by0 + 1.3].forEach(function (yy) { g.add(rb(W - 0.1, 0.06, 0.06, 0.012, M.bodySteel, 0, yy, bz1 - 0.07)); });
        g.add(rb(0.06, 0.06, W * 0.9, 0.01, M.satin, 0, by1 - 0.15, bz1 - 0.1)); g.children[g.children.length - 1].rotation.y = Math.PI / 2;
        g.add(rb(2.3, 0.16, 0.12, 0.02, M.frame, 0, 0.66, bz1 - 0.1));
        g.add(rb(0.3, 0.06, 0.02, 0.005, M.head, 0, 0.82, bz1 - 0.17));
        [by0 + 0.3, by1 - 0.3].forEach(function (yy) { [-1, 1].forEach(function (s) { g.add(rb(0.16, 0.12, 0.06, 0.01, M.frame, s * (hw - 0.12), yy, bz1 - 0.06)); }); });
        /* THE LOAD. Cut limbs and brush heaped in the body, seeded, crowns of leaves among them */
        if (o.load > 0) {
          var r = lcg(N.SEED + 7), n = Math.round(170 * o.load), topY = by0 + (by1 - by0) * Math.min(1.15, 0.55 + o.load * 0.6);
          /* every limb is the chassis cut_limb, barked and bent with ringed pale ends, its butt toward the tailgate */
          var limbs = [];
          for (var li = 0; li < n; li++) {
            var len = 0.8 + r() * 2.2, rad = 0.03 + r() * 0.07, y = by0 + 0.2 + Math.sqrt(r()) * (topY - by0 - 0.2);
            var lz = bz1 + 0.3 + r() * Math.max(0.01, bl - 0.6 - len);
            var limb = K.make("cut_limb", { length: len, radius: rad, taper: 0.45, seed: 1 + (li % 9), stubs: len > 1.4 });
            limb.position.set((r() - 0.5) * (W - 0.6), y - rad, lz); limb.rotation.set(0, -Math.PI / 2 + (r() - 0.5) * 0.7, (r() - 0.5) * 0.5);
            limb.updateMatrix(); g.add(limb); limbs.push([limb, len, rad]);
          }
          /* leaves as small cards seated on the limbs' own surfaces, in clumps, never hanging in the air */
          var card = new THREE.PlaneGeometry(0.022, 0.034); card.translate(0, 0.015, 0);
          [M.leafDry, M.leaf].forEach(function (lm) {
            var cnt = Math.round(420 * o.load), inst = new THREE.InstancedMesh(card, lm, cnt), dm = new THREE.Object3D(), pt = new THREE.Vector3();
            for (var q = 0; q < cnt; q++) {
              var L = limbs[Math.floor(r() * limbs.length)], a = r() * 6.3, t = 0.35 + r() * 0.65;
              pt.set(t * L[1], L[2] * (1 + Math.sin(a) * 0.95), L[2] * Math.cos(a) * 0.95).applyMatrix4(L[0].matrix);
              dm.position.copy(pt); dm.rotation.set(r() * 6.3, r() * 6.3, r() * 6.3); dm.scale.setScalar(0.7 + r() * 0.7); dm.updateMatrix(); inst.setMatrixAt(q, dm.matrix);
            }
            inst.castShadow = inst.receiveShadow = true; g.add(inst);
          });
        }
        /* THE CAMERAS: one pod on each front corner of the body, on a bracket off the top rail, turned out to the side */
        var pods = [];
        if (o.pods) [-1, 1].forEach(function (s) {
          var p = K.make("camera_pod", { lit: o.podsLit, tilt: 0.18 }); p.scale.setScalar(o.podScale || 1.4);
          p.position.set(s * (hw + 0.02), by1 + 0.05, bz0 - 0.35); p.rotation.y = s * Math.PI / 2; g.add(p);
          pods.push([s * (hw + 0.2), by1 + 0.25, bz0 - 0.35]);
        });
        /* the wheels: steer axle and tandem duals */
        [-1, 1].forEach(function (s) {
          var wf = wheel(R, 0.3, false); wf.position.set(s * 1.0, R, zFrontAxle); if (s < 0) wf.rotation.y = Math.PI; g.add(wf);
          [-2.7, -3.95].forEach(function (z) { var wr = wheel(R, 0.28, true); wr.position.set(s * 0.95, R, z); if (s < 0) wr.rotation.y = Math.PI; g.add(wr); });
        });
        /* axle housings and the mud flaps behind the tandem */
        [zFrontAxle, -2.7, -3.95].forEach(function (z) { var ax = mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.8, 12), M.frame, 0, R, z); ax.rotation.z = Math.PI / 2; g.add(ax); });
        [-1, 1].forEach(function (s) { g.add(rb(0.5, 0.55, 0.02, 0.005, M.rubber, s * 0.95, 0.42, -4.6)); });
        g.userData.attach = { pods: pods, cab: [0, 2.4, 1.8], body: [0, by1, bc], grapple: [0.35, 2.4, -2.2] };
        return g;
      }
    });
    /* A BRUSH WINDROW at the curb, the way a resident sets out a monthly pickup: cut cedar elm limbs laid roughly along
     * its length in a half ellipse section `height` high and `depth` deep, with clumps of small leaves and pale cut
     * ends. `length` comes from the frame's figures. Instanced, seeded. Origin at the centre of its footprint, length
     * along x. */
    K.define("brush_pile", {
      size: [4, 1.2, 2],
      options: { length: 4, height: 1.2, depth: 2.0, density: 1, seed: 3 },
      note: "An illustrative curbside brush windrow of cut limbs and leaf clumps in a half ellipse section. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), r = lcg((o.seed || 3) * 7919), L = o.length, Hh = o.height, Dd = o.depth;
        var limbG = new THREE.CylinderGeometry(0.6, 1, 1, 7, 1); limbG.rotateZ(Math.PI / 2);
        var nL = Math.round(70 * L * o.density), dm = new THREE.Object3D();
        var dark = new THREE.InstancedMesh(limbG, M.bark, nL), pale = new THREE.InstancedMesh(limbG, M.barkPale, Math.round(nL * 0.3));
        var ends = new THREE.InstancedMesh(new THREE.CircleGeometry(1, 10), new THREE.MeshStandardMaterial({ color: 0xc9a979, roughness: 0.8, side: THREE.DoubleSide }), nL);
        var put = function (inst, k) {
          var u = (r() - 0.5) * 2, v = Math.sqrt(Math.max(0, 1 - u * u)), len = 0.6 + r() * 1.8, rad = 0.015 + Math.pow(r(), 2) * 0.06;
          var x = (r() - 0.5) * (L - len * 0.6), z = u * Dd / 2 * 0.95, y = r() * v * Hh;
          dm.position.set(x, y + rad, z); dm.rotation.set((r() - 0.5) * 0.6, (r() - 0.5) * 0.9, (r() - 0.5) * 0.5 + (y > Hh * 0.5 ? 0.2 : 0));
          dm.scale.set(len, rad, rad); dm.updateMatrix(); inst.setMatrixAt(k, dm.matrix);
          return [x, y + rad, z, len, rad, dm.rotation.y];
        };
        for (var i = 0; i < nL; i++) {
          var q = put(dark, i);
          dm.position.set(q[0] + Math.cos(q[5]) * q[3] / 2, q[1], q[2] - Math.sin(q[5]) * q[3] / 2); dm.rotation.set(0, q[5] + Math.PI / 2, 0); dm.scale.setScalar(q[4] * 0.95); dm.updateMatrix(); ends.setMatrixAt(i, dm.matrix);
        }
        for (var j = 0; j < pale.count; j++) put(pale, j);
        [dark, pale, ends].forEach(function (m) { m.castShadow = m.receiveShadow = true; g.add(m); });
        var card = new THREE.PlaneGeometry(0.035, 0.055); card.translate(0, 0.025, 0);
        [M.leafDry, M.leaf].forEach(function (lm) {
          var cnt = Math.round(2600 * L * o.density), inst = new THREE.InstancedMesh(card, lm, cnt);
          for (var k = 0; k < cnt; k++) {
            if (k % 60 === 0) { var u2 = (r() - 0.5) * 2, v2 = Math.sqrt(Math.max(0, 1 - u2 * u2)); var cc = [(r() - 0.5) * L * 0.9, Math.max(0.05, (0.5 + 0.5 * Math.sqrt(r())) * v2 * Hh), u2 * Dd / 2 * 0.9]; }
            dm.position.set(cc[0] + (r() - 0.5) * 0.45, cc[1] + (r() - 0.5) * 0.25, cc[2] + (r() - 0.5) * 0.45);
            dm.rotation.set(r() * 6.3, r() * 6.3, r() * 6.3); dm.scale.setScalar(0.7 + r() * 0.8); dm.updateMatrix(); inst.setMatrixAt(k, dm.matrix);
          }
          inst.castShadow = inst.receiveShadow = true; g.add(inst);
        });
        return g;
      }
    });
    /* BARK AND END GRAIN for a cut cedar elm limb: furrows run ALONG the limb (the texture's v axis), broken and seeded;
     * the end grain is pale wood with growth rings, a darker heart and a bark rim */
    var barkTexMemo = {};
    function barkTex(seed) { if (!barkTexMemo[seed]) barkTexMemo[seed] = barkTexMake(seed); return barkTexMemo[seed].clone(); }
    function barkTexMake(seed) {
      var c = document.createElement("canvas"); c.width = 256; c.height = 512; var x = c.getContext("2d"), r = lcg(seed);
      x.fillStyle = "#6a5541"; x.fillRect(0, 0, 256, 512);
      for (var i = 0; i < 70; i++) { var u = r() * 256, w = 2 + r() * 7, y0 = r() * 512, len = 80 + r() * 420;
        x.fillStyle = "rgba(" + (r() < 0.5 ? "38,29,21" : "128,108,86") + "," + (0.35 + r() * 0.45) + ")"; x.fillRect(u, y0, w, len); x.fillRect(u, y0 - 512, w, len); }
      for (var j = 0; j < 400; j++) { x.fillStyle = "rgba(20,16,12," + (0.2 + r() * 0.3) + ")"; x.fillRect(r() * 256, r() * 512, 1 + r() * 2, 4 + r() * 14); }
      var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
    }
    var barkBumpMemo = {};
    function barkBump(seed) { if (!barkBumpMemo[seed]) barkBumpMemo[seed] = barkBumpMake(seed); return barkBumpMemo[seed].clone(); }
    function barkBumpMake(seed) {
      var c = document.createElement("canvas"); c.width = 256; c.height = 512; var x = c.getContext("2d"), r = lcg(seed + 3);
      x.fillStyle = "#808080"; x.fillRect(0, 0, 256, 512);
      for (var i = 0; i < 90; i++) { var u = r() * 256, w = 2 + r() * 6, y0 = r() * 512, len = 60 + r() * 400; x.fillStyle = "rgba(30,30,30," + (0.5 + r() * 0.4) + ")"; x.fillRect(u, y0, w, len); x.fillRect(u, y0 - 512, w, len); }
      var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
    }
    var grainTexMemo = {};
    function grainTex(seed) { if (!grainTexMemo[seed]) grainTexMemo[seed] = grainTexMake(seed); return grainTexMemo[seed].clone(); }
    function grainTexMake(seed) {
      var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed + 9);
      x.fillStyle = "#d8bd92"; x.fillRect(0, 0, 256, 256);
      var cxx = 128 + (r() - 0.5) * 24, cyy = 128 + (r() - 0.5) * 24;
      for (var k = 1; k < 30; k++) { x.strokeStyle = "rgba(" + (120 + r() * 30) + "," + (88 + r() * 20) + ",52," + (0.35 + r() * 0.3) + ")"; x.lineWidth = 1 + r() * 1.5;
        x.beginPath(); x.ellipse(cxx, cyy, k * 4.2 + r() * 1.5, k * 4.0 + r() * 1.5, r(), 0, 6.3); x.stroke(); }
      var gr = x.createRadialGradient(cxx, cyy, 0, cxx, cyy, 30); gr.addColorStop(0, "rgba(120,80,44,0.7)"); gr.addColorStop(1, "rgba(120,80,44,0)"); x.fillStyle = gr; x.fillRect(0, 0, 256, 256);
      x.strokeStyle = "#3a2c20"; x.lineWidth = 14; x.beginPath(); x.arc(128, 128, 124, 0, 6.3); x.stroke();
      for (var s = 0; s < 6; s++) { x.strokeStyle = "rgba(90,60,36,0.5)"; x.lineWidth = 1; x.beginPath(); var a = r() * 6.3; x.moveTo(cxx, cyy); x.lineTo(cxx + Math.cos(a) * 110, cyy + Math.sin(a) * 110); x.stroke(); }
      var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
    }
    /* A CUT LIMB: a cedar elm limb `length` m long, `radius` at the butt tapering by `taper`, with a slight seeded bend,
     * longitudinal bark, two saw cut ends showing ringed end grain, and a few twig stubs. Lies along +x from its butt
     * at the origin, resting on y = 0. */
    K.define("cut_limb", {
      size: [2, 0.24, 0.24],
      options: { length: 2, radius: 0.11, taper: 0.3, seed: 1, stubs: true },
      note: "An illustrative cut cedar elm limb with longitudinal bark, ringed end grain at both saw cuts and twig stubs. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), L = Math.max(0.01, o.length), r0 = o.radius, r1 = r0 * (1 - o.taper * Math.min(1, L / 6)), rr = lcg(o.seed * 131);
        var seg = Math.max(2, Math.round(L * 6));
        var geo = new THREE.CylinderGeometry(r1, r0, L, 28, seg, true); geo.rotateZ(-Math.PI / 2); geo.translate(L / 2, 0, 0);
        var pos = geo.attributes.position, bendA = (rr() - 0.5) * 0.06, bendB = (rr() - 0.5) * 0.05;
        for (var i = 0; i < pos.count; i++) { var px = pos.getX(i), u = px / L; pos.setY(i, pos.getY(i) + bendA * Math.sin(u * Math.PI) * Math.min(1, L / 3)); pos.setZ(i, pos.getZ(i) + bendB * Math.sin(u * Math.PI * 1.3) * Math.min(1, L / 3)); }
        geo.computeVertexNormals();
        var bt = barkTex(o.seed), bb = barkBump(o.seed); bt.repeat.set(2, Math.max(0.2, L / 0.9)); bb.repeat.copy(bt.repeat);
        var bark = new THREE.MeshStandardMaterial({ map: bt, bumpMap: bb, bumpScale: 3.5, roughness: 0.92 });
        var body = mesh(geo, bark, 0, r0, 0); g.add(body);
        var gm = new THREE.MeshStandardMaterial({ map: grainTex(o.seed), roughness: 0.78 });
        [[0, r0, -1], [L, r1, 1]].forEach(function (e) {
          var cap = mesh(new THREE.CircleGeometry(e[1] * 1.0, 32), gm, e[0], r0 + (e[2] > 0 ? bendA * 0 : 0), 0); cap.rotation.y = e[2] * Math.PI / 2; g.add(cap);
        });
        if (o.stubs && L > 0.5) for (var s = 0; s < Math.floor(L / 1.4); s++) {
          var sx = 0.3 + rr() * (L - 0.6), sr = 0.015 + rr() * 0.02, sl = 0.08 + rr() * 0.14, sa = rr() * 6.3;
          var st = mesh(new THREE.CylinderGeometry(sr * 0.7, sr, sl, 8), bark, sx, r0 + Math.sin(sa) * r0 * 0.9, Math.cos(sa) * r0 * 0.9); st.rotation.x = sa - Math.PI / 2; st.rotation.z = -0.5; g.add(st);
          var sc = mesh(new THREE.CircleGeometry(sr * 0.7, 10), gm, 0, 0, 0); st.add(sc); sc.position.y = sl / 2 + 0.001; sc.rotation.x = -Math.PI / 2;
        }
        g.userData.keepOrigin = true; /* the butt stays at the origin, so every limb starts on one line */
        return g;
      }
    });
    /* A CANTILEVER RACK as a city yard keeps for long stock: galvanized upright columns on base plates with `rows` arms
     * projecting forward (+z), `pitch` m apart, the lowest at `y0`. userData.arms[k] is the top centre of arm k (k = 0 is
     * the top arm) at the first upright. Uprights at x = 0 and x = `span`. */
    K.define("limb_rack", {
      size: [6, 4, 1.2],
      options: { rows: 6, pitch: 0.58, y0: 0.42, span: 5.2, reach: 0.75 },
      note: "An illustrative galvanized cantilever rack with arms for long stock. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), H = o.y0 + (o.rows - 1) * o.pitch + 0.45, galv = K.finish.galvanized(), arms = [];
        [0, o.span].forEach(function (ux) {
          g.add(rb(0.2, H, 0.16, 0.02, galv, ux, H / 2, -0.12));
          g.add(rb(0.05, H, 0.2, 0.01, galv, ux - 0.11, H / 2, -0.12));
          g.add(rb(0.05, H, 0.2, 0.01, galv, ux + 0.11, H / 2, -0.12));
          g.add(rb(0.5, 0.03, 1.4, 0.01, galv, ux, 0.015, 0.2));
          var brace = rb(0.12, 0.12, 1.3, 0.02, galv, ux, 0.08, 0.35); g.add(brace);
          for (var k = 0; k < o.rows; k++) {
            var y = o.y0 + (o.rows - 1 - k) * o.pitch;
            var arm = rb(0.09, 0.1, o.reach, 0.015, galv, ux, y, -0.04 + o.reach / 2); arm.rotation.x = -0.035; g.add(arm);
            g.add(rb(0.09, 0.06, 0.04, 0.01, galv, ux, y + 0.06, -0.04 + o.reach - 0.02));
            if (ux === 0) arms.push([ux, y + 0.05, 0.3]);
          }
        });
        g.userData.arms = arms; g.userData.height = H; g.userData.keepOrigin = true; /* arms[] are published coordinates */
        return g;
      }
    });
    /* A COUNT TOKEN. One cast metal marker standing for one item of a count: a short hexagonal stud 30 mm across with a
     * chamfered top, so thousands of them read as a field of made things and one alone reads as an object. `warm`
     * gives the brass of an outcome a person decided. Origin at its base. */
    K.define("count_token", {
      size: [0.03, 0.018, 0.026],
      options: { warm: false, h: 0.018 },
      note: "An illustrative cast count marker, hexagonal with a chamfered top. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group();
        var geo = new THREE.CylinderGeometry(0.013, 0.015, o.h, 6); geo.translate(0, o.h / 2, 0);
        g.add(mesh(geo, o.warm ? M.tokenWarm : M.tokenCast));
        return g;
      }
    });
    /* THE NOTICE LETTER. A letter sheet 0.216 by 0.279 m folded in three and half opened, with grey ruled lines for
     * text that a reader can't read and a blank letterhead band. Origin at its centre, lying on +y. */
    K.define("notice_letter", {
      size: [0.216, 0.03, 0.279],
      options: { open: 0.6, deadline: false },
      note: "An illustrative folded city letter with unreadable ruled text. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group();
        var c = document.createElement("canvas"); c.width = 432; c.height = 558; var x = c.getContext("2d");
        x.fillStyle = "#ece8de"; x.fillRect(0, 0, 432, 558);
        x.fillStyle = "#c9c4b8"; x.fillRect(36, 36, 140, 22);
        x.fillStyle = "#9e998e"; for (var i = 0; i < 22; i++) { var w = 300 + ((i * 37) % 60); if (i % 6 === 5) continue; x.fillRect(36, 100 + i * 18, i % 6 === 4 ? w * 0.5 : w, 5); }
        if (o.deadline) { x.strokeStyle = "#6a2a22"; x.lineWidth = 4; x.strokeRect(220, 30, 176, 54); }
        var tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
        var mat = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.9, side: THREE.DoubleSide });
        var th = 0.279 / 3, a = o.open;
        [0, 1, 2].forEach(function (k) {
          var geo = new THREE.PlaneGeometry(0.216, th); var uv = geo.attributes.uv;
          for (var j = 0; j < uv.count; j++) uv.setY(j, (2 - k) / 3 + uv.getY(j) / 3);
          var p = new THREE.Mesh(geo, mat); p.castShadow = p.receiveShadow = true;
          var pivot = new THREE.Group();
          if (k === 1) { p.rotation.x = -Math.PI / 2; pivot.add(p); }
          else { var sgn = k === 0 ? -1 : 1; pivot.position.z = sgn * th / 2; pivot.rotation.x = sgn * (1 - a) * 1.4; p.position.z = sgn * th / 2; p.rotation.x = -Math.PI / 2; var inner = new THREE.Group(); inner.add(p); pivot.add(inner); }
          pivot.position.y = 0.002; g.add(pivot);
        });
        return g;
      }
    });
  };

  /* after TXT.add: rotor blur discs and other marked meshes cast no shadow */
  N.noShadows = function (R) { R.scene.traverse(function (o) { if (o.userData && o.userData.noShadow) { o.castShadow = false; o.receiveShadow = false; } }); };
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
      /* the footer lines carry a tight halo only: a 14 px blur read as a smudge on a lit ground */
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




  global.CH = N;
})(this);
