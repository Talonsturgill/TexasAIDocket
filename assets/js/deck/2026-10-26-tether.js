/* deck/2026-10-26-tether.js — the chassis for the 2026-10-26 deck: Zipline's autonomous delivery drones over Round
 * Rock, flown from a hub in the city's extraterritorial jurisdiction, and the City of Round Rock's own page saying its
 * zoning ordinances do not specifically address drone delivery hubs (tx-2026-0232, context tx-2026-0186).
 *
 * THE VISUAL ARGUMENT. One delivery aircraft and the line it lowers. The aircraft holds in the air the city does not
 * govern, and the tether is the one thing that reaches down into the yards the city does. Height, distance and the
 * three mile reach are drawn at true scale from figures.json in each frame's own code.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky, one warm seam low on the key's side, the
 * subject in a pool of light and the world behind it gone dark.
 *
 * THE LIGHT is azimuth -55, elevation 8. +x is east and +z is south. The last light stands low in the south west: a
 * camera on +z looking -z has the key in front and to its LEFT, every lit edge is on the left, and every cast runs
 * long to the right and away. Looking up at the aircraft against the west, it is a silhouette with a warm rim.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `delivery_drone` (a fixed wing VTOL delivery aircraft
 * with four lift rotors on two booms, a pusher, a V tail and a tether winch), `delivery_pod` (the lowered package
 * pod) and `dock_tower` (a charging and launch tower). All are drawn to illustrate and to no maker's design, in the
 * kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is the pod's signal amber, #E0956A (dusk gold), and it means ONE thing: what comes down to the ground.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 * Every frame composes its own picture, and every quantity a frame draws is read from figures.json in that frame's
 * own code. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("tether.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "tether",
    light: { az: -55, el: 8 },
    sky: "lastLight",
    ground: "#08070D",
    material: "#D9DCDF",
    accent: "#E0956A",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.12, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261026 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261026;
  N.ACCENT = 0xe0956a;   /* dusk gold, brand.yaml's, and it means ONE thing: what comes down to the ground */
  N.INK = "#ECE8DF";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */
  /* A COMPOSITE SKIN: fine panel tooth in a bump map and faint grime streaks aft, so the airframe reads as a worked
   * aircraft and never as a white toy under the low key */
  function skin(THREE, seed) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "#808080"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < 9000; i++) { var v = Math.floor(116 + r() * 24); x.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; x.fillRect(r() * 256, r() * 256, 1.2, 1.2); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  /* the blade sweep, radial: clear at the hub, a soft band toward the tips, a thin bright rim at the tip path */
  /* a soft radial glow for a lamp, built once */
  N.glowTex = function (THREE) {
    if (N._glow) return N._glow;
    var c = document.createElement("canvas"); c.width = c.height = 64; var g = c.getContext("2d");
    var gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.18, "rgba(255,255,255,0.6)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); N._glow = new THREE.CanvasTexture(c); return N._glow;
  };
  N.blurTex = function (THREE) {
    if (N._blur) return N._blur;
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d");
    var g = x.createRadialGradient(128, 128, 6, 128, 128, 128);
    g.addColorStop(0, "rgba(255,255,255,0)"); g.addColorStop(0.45, "rgba(255,255,255,0.05)"); g.addColorStop(0.85, "rgba(255,255,255,0.22)");
    g.addColorStop(0.96, "rgba(255,255,255,0.45)"); g.addColorStop(1, "rgba(255,255,255,0)");
    x.fillStyle = g; x.fillRect(0, 0, 256, 256);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; N._blur = t; return t;
  };
  /* panel seams for the airframe: a few fine lines in a bump map, so the shell reads as assembled panels */
  function seams(THREE) {
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d");
    x.fillStyle = "#808080"; x.fillRect(0, 0, 512, 512); x.strokeStyle = "#5a5a5a"; x.lineWidth = 2;
    [96, 230, 300, 420].forEach(function (v) { x.beginPath(); x.moveTo(v, 0); x.lineTo(v, 512); x.stroke(); });
    [140, 380].forEach(function (v) { x.beginPath(); x.moveTo(0, v); x.lineTo(512, v); x.stroke(); });
    x.fillStyle = "#606060"; for (var i = 0; i < 40; i++) { x.beginPath(); x.arc(96 + (i % 2) * 6, 10 + i * 12.5, 1.4, 0, 6.3); x.fill(); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
  }
  N.mats = function (THREE, K) {
    if (N._m) return N._m;
    var b = skin(THREE, N.SEED); b.repeat.set(4, 4);
    var m = {
      shell: new THREE.MeshPhysicalMaterial({ color: 0xd8dbde, roughness: 0.42, metalness: 0.0, clearcoat: 0.6, clearcoatRoughness: 0.35, bumpMap: seams(THREE), bumpScale: 0.9 }),
      shellDark: new THREE.MeshStandardMaterial({ color: 0x2a2d31, roughness: 0.55, metalness: 0.1 }),
      carbon: new THREE.MeshStandardMaterial({ color: 0x15171a, roughness: 0.38, metalness: 0.25 }),
      motor: new THREE.MeshStandardMaterial({ color: 0x3a3d42, roughness: 0.3, metalness: 0.75 }),
      blade: new THREE.MeshStandardMaterial({ color: 0x101113, roughness: 0.45, metalness: 0.05, side: THREE.DoubleSide }),
      bladeSoft: new THREE.MeshStandardMaterial({ color: 0x2a2d31, roughness: 0.5, metalness: 0.05, side: THREE.DoubleSide, transparent: true, opacity: 0.35, depthWrite: false }),
      pod: new THREE.MeshPhysicalMaterial({ color: 0xe4e2dc, roughness: 0.36, metalness: 0.0, clearcoat: 0.5, clearcoatRoughness: 0.3 }),
      /* the accent is unlit, so it holds its own hex under the dusk key and under the grade, where a lit band went brown */
      hatch: new THREE.MeshStandardMaterial({ color: 0xeef0f2, roughness: 0.35, metalness: 0.05 }),
      /* the gold holds its own hex as emission and keeps a dim albedo under it, so the band still turns with the light and reads as paint */
      podBand: new THREE.MeshStandardMaterial({ color: new THREE.Color(N.ACCENT).multiplyScalar(0.3), roughness: 0.55, metalness: 0, emissive: N.ACCENT, emissiveIntensity: 0.9, toneMapped: false }),
      tether: new THREE.MeshStandardMaterial({ color: 0xc9c6bf, roughness: 0.5, metalness: 0.1 }),
      navRed: new THREE.MeshStandardMaterial({ color: 0xff2a1a, emissive: 0xff2a1a, emissiveIntensity: 3.2 }),
      navGreen: new THREE.MeshStandardMaterial({ color: 0x1aff6a, emissive: 0x1aff6a, emissiveIntensity: 3.0 }),
      strobe: new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 4.0 }),
      steel: K.mat("tt_steel", { color: 0x8a8e93, metalness: 0.65, roughness: 0.42 }),
      steelDark: K.mat("tt_steel_dark", { color: 0x3b3f44, metalness: 0.55, roughness: 0.5 }),
      concrete: K.finish.concrete()
    };
    N._m = m;
    return m;
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.delivery_drone) return;
    var M = N.mats(THREE, K);
    /* reverse every triangle's winding, for a mirrored non-indexed geometry */
    function flip(geo) {
      if (geo.index) geo = geo.toNonIndexed();
      ["position", "normal", "uv"].forEach(function (k) {
        var a = geo.attributes[k]; if (!a) return; var n = a.itemSize, arr = a.array, t;
        for (var i = 0; i < a.count; i += 3) for (var c = 0; c < n; c++) { t = arr[(i + 1) * n + c]; arr[(i + 1) * n + c] = arr[(i + 2) * n + c]; arr[(i + 2) * n + c] = t; }
        a.needsUpdate = true;
      });
      geo.computeVertexNormals(); return geo;
    }
    function mesh(geo, mat, x, y, z) { var o = new THREE.Mesh(geo, mat); o.position.set(x || 0, y || 0, z || 0); o.castShadow = o.receiveShadow = true; return o; }
    /* a two blade rotor of radius r, lying flat, its hub at the origin, `ang` its stopped angle */
    function rotor(r, ang, blur) {
      var g = new THREE.Group();
      g.add(mesh(new THREE.CylinderGeometry(0.035, 0.04, 0.05, 20), M.motor, 0, 0, 0));
      for (var k = 0; k < 2; k++) {
        var sh = new THREE.Shape(); sh.moveTo(0.03, -0.012); sh.quadraticCurveTo(r * 0.45, -0.034, r, -0.012); sh.lineTo(r, 0.01); sh.quadraticCurveTo(r * 0.5, 0.026, 0.03, 0.014); sh.lineTo(0.03, -0.012);
        var geo = new THREE.ExtrudeGeometry(sh, { depth: 0.006, bevelEnabled: false }); geo.rotateX(-Math.PI / 2); geo.rotateY(0.06);
        var bl = mesh(geo, blur ? M.bladeSoft : M.blade, 0, 0.02, 0); bl.rotation.y = ang + k * Math.PI; if (blur) bl.userData.noShadow = true; g.add(bl);
      }
      if (blur) { /* where the blades sweep: a radial gradient, densest near the tips, never a flat grey disc */
        var d = new THREE.Mesh(new THREE.RingGeometry(0.05, r, 64), new THREE.MeshBasicMaterial({ map: N.blurTex(THREE), color: 0xb8bec6, transparent: true, opacity: Math.min(1, blur * 1.6), side: THREE.DoubleSide, depthWrite: false }));
        d.rotation.x = -Math.PI / 2; d.position.y = 0.03; d.userData.noShadow = true; g.add(d);
      }
      return g;
    }
    /* THE DELIVERY DRONE. Front on +z. A lathe fuselage about 2.1 m long, a straight wing of `span` with rounded
     * tips, two carbon booms under the wing each carrying a lift rotor fore and aft, a pusher at the tail, a V tail,
     * nav lights at the wingtips and a strobe on top. `tether` lowers a line of that many metres from the belly winch
     * and userData.attach.pod is where its end hangs. Drawn to illustrate, to no maker's design. */
    K.define("delivery_drone", {
      size: [3.4, 0.6, 2.4],
      options: { span: 3.4, tether: 0, rotorAng: 0.4, blur: 0, lights: true, sag: 0, chute: true },
      note: "An illustrative fixed wing VTOL delivery drone: lathe fuselage, straight wing, two booms with four lift rotors, a pusher, a V tail, nav lights, an optional tether lowered from the belly. Drawn to illustrate, to no maker's design.",
      make: function (o) {
        var g = new THREE.Group(), Y = 0.32;
        /* fuselage, a lathe profile along z */
        var prof = [[0, -1.05], [0.04, -1.0], [0.08, -0.85], [0.12, -0.55], [0.15, -0.15], [0.16, 0.2], [0.155, 0.55], [0.13, 0.8], [0.08, 0.98], [0, 1.06]];
        var lg = new THREE.LatheGeometry(prof.map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 48);
        lg.rotateX(Math.PI / 2); lg.scale(1, 0.82, 1);
        g.add(mesh(lg, M.shell, 0, Y, 0));
        /* a dark sensor window under the nose, and a belly hatch where the winch sits */
        var win = mesh(new THREE.SphereGeometry(0.075, 24, 16), M.carbon, 0, Y - 0.1, 0.78); win.scale.set(1, 0.6, 1.4); g.add(win);
        var hatch = mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.02, 32), M.shellDark, 0, Y - 0.155, 0.05); g.add(hatch);
        /* the wing, an extruded airfoil along the span, tapered toward each tip, a touch of dihedral */
        var span = o.span, chord = 0.36;
        function airfoil(c) {
          var sh = new THREE.Shape(), t = 0.12 * c, n = 18;
          sh.moveTo(c * 0.5, 0);
          for (var i = 1; i <= n; i++) { var u = i / n, x = c * 0.5 - u * c; sh.lineTo(x, 0.6 * t * Math.sqrt(Math.max(0, 1 - Math.pow(2 * u - 1, 2))) * (u < 0.3 ? 1.15 : 1)); }
          for (var j = n - 1; j >= 1; j--) { var v = j / n, x2 = c * 0.5 - v * c; sh.lineTo(x2, -0.25 * t * Math.sqrt(Math.max(0, 1 - Math.pow(2 * v - 1, 2)))); }
          sh.lineTo(c * 0.5, 0); return sh;
        }
        [-1, 1].forEach(function (s) {
          var len = span / 2 - 0.12;
          var geo = new THREE.ExtrudeGeometry(airfoil(chord), { depth: len, steps: 8, bevelEnabled: true, bevelThickness: 0.006, bevelSize: 0.006, bevelSegments: 2 });
          var pos = geo.attributes.position; /* taper the chord toward the tip */
          for (var k = 0; k < pos.count; k++) { var zz = pos.getZ(k) / len, f = 1 - 0.32 * zz; pos.setX(k, pos.getX(k) * f); pos.setY(k, pos.getY(k) * f); }
          geo.computeVertexNormals();
          geo.rotateY(-Math.PI / 2); /* span runs along -x, leading edge toward +z */
          if (s > 0) { geo.scale(-1, 1, 1); flip(geo); }  /* the starboard wing is the port wing mirrored */
          var w = mesh(geo, M.shell, s * 0.1, Y + 0.12, 0.12); w.rotation.z = s * 0.035; g.add(w);
          var tip = mesh(new THREE.SphereGeometry(0.022, 16, 12), o.lights ? (s < 0 ? M.navRed : M.navGreen) : M.shellDark, s * (span / 2 - 0.0), Y + 0.12 + s * 0.035 * 0, 0.16);
          tip.scale.set(1.0, 0.8, 2.2); g.add(tip);
          /* the boom under each wing, fore to aft, and its two lift rotors */
          var bx = s * 0.62;
          /* a faired boom, a lathe that tapers to a point at both ends, faired into the wing's underside by a pylon */
          var bp = []; for (var q = 0; q <= 24; q++) { var u = q / 24, rad = 0.036 * Math.pow(Math.sin(Math.PI * Math.min(1, Math.max(0, (u * 1.08 - 0.04)))), 0.35); bp.push(new THREE.Vector2(Math.max(0.002, rad), -1.15 + 2.3 * u)); }
          var boomG = new THREE.LatheGeometry(bp, 20); boomG.rotateX(Math.PI / 2);
          var boom = mesh(boomG, M.carbon, bx, Y + 0.06, 0.05); g.add(boom);
          /* the pylon is a short airfoil fairing, chord fore and aft, so it reads as part of the wing and never as a block */
          var pg = new THREE.ExtrudeGeometry(airfoil(0.3), { depth: 0.075, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.004, bevelSegments: 2 });
          pg.rotateX(-Math.PI / 2); pg.rotateY(Math.PI / 2); pg.scale(1.6, 1, 1); pg.computeVertexNormals();
          var pyl = mesh(pg, M.shell, bx, Y + 0.06, 0.12); g.add(pyl);
          [0.95, -0.85].forEach(function (z, i) {
            /* the motor nacelle, a lathe with a domed spinner seat */
            var np = [[0, 0], [0.04, 0.005], [0.052, 0.04], [0.05, 0.1], [0.036, 0.13], [0.012, 0.145], [0, 0.148]].map(function (p) { return new THREE.Vector2(p[0], p[1]); });
            var pod = mesh(new THREE.LatheGeometry(np, 24), M.shellDark, bx, Y + 0.035, z); g.add(pod);
            var rr = rotor(0.4, o.rotorAng + (s > 0 ? 0.7 : 0) + i * 1.1, o.blur); rr.position.set(bx, Y + 0.185, z); g.add(rr);
          });
        });
        /* the V tail and the pusher */
        [-1, 1].forEach(function (s) {
          var fin = TXT.roundedBox(0.02, 0.26, 0.17, 0.008, M.shell); fin.castShadow = true;
          fin.position.set(s * 0.1, Y + 0.15, -0.92); fin.rotation.z = -s * 0.62; g.add(fin);
        });
        /* the pusher turns edge on to most cameras, so its sweep is only a faint streak and never a disc */
        var push = rotor(0.26, o.rotorAng * 2, o.blur ? 0.05 : 0); push.rotation.x = Math.PI / 2; push.position.set(0, Y, -1.1); g.add(push);
        if (o.lights) g.add(mesh(new THREE.SphereGeometry(0.02, 12, 8), M.strobe, 0, Y + 0.17, -0.2));
        /* each light carries a small glow, the way a night camera holds a lamp, so the lights read as lit at feed size */
        if (o.lights) [[-span / 2, Y + 0.12, 0.16, 0xff4a38], [span / 2, Y + 0.12, 0.16, 0x4cff8c], [0, Y + 0.19, -0.2, 0xffffff]].forEach(function (q) {
          var sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: N.glowTex(THREE), color: q[3], blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, transparent: true }));
          sp.position.set(q[0], q[1], q[2]); sp.scale.setScalar(0.13); sp.userData.noShadow = true; g.add(sp);
        });
        /* the dorsal parachute hatch, a seamed panel with two latches ahead of the wing */
        if (o.chute) {
          var hp = TXT.roundedBox(0.17, 0.014, 0.28, 0.004, M.hatch); hp.position.set(0, Y + 0.158, 0.48); hp.rotation.x = -0.12; g.add(hp);
          [-0.05, 0.05].forEach(function (lx) { g.add(mesh(new THREE.BoxGeometry(0.02, 0.01, 0.03), M.motor, lx, Y + 0.168, 0.36)); });
          g.userData.chute = [0, Y + 0.16, 0.48];
        }
        /* THE TETHER, a lit tube from the belly winch down to the pod's bail, with a slight sag if asked */
        var attach = { winch: [0, Y - 0.16, 0.05] };
        if (o.tether > 0) {
          var top = new THREE.Vector3(0, Y - 0.16, 0.05), bot = new THREE.Vector3(o.sag || 0, Y - 0.16 - o.tether, 0.05);
          var mid = top.clone().lerp(bot, 0.5); mid.x += (o.sag || 0) * 0.6;
          var curve = new THREE.CatmullRomCurve3([top, mid, bot]);
          var tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 160, 0.006, 8, false), M.tether); tube.castShadow = true; g.add(tube);
          attach.pod = [bot.x, bot.y, bot.z];
        }
        g.userData.attach = attach;
        return g;
      }
    });
    /* THE DELIVERY POD, the package that rides the tether down: a rounded capsule about 0.62 m tall with a bail on
     * top, and an amber band, the deck's one accent. Origin at its base. */
    K.define("delivery_pod", {
      size: [0.42, 0.66, 0.36],
      options: { band: true },
      note: "An illustrative lowered delivery pod with a bail and an amber band. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group();
        /* a smooth profile: a superellipse of half width 0.2 and half height 0.31, so the shoulders round off */
        var prof = [];
        for (var i = 0; i <= 40; i++) { var t = -Math.PI / 2 + Math.PI * i / 40, c = Math.cos(t), sn = Math.sin(t);
          prof.push(new THREE.Vector2(0.2 * Math.pow(Math.abs(c), 0.55), 0.31 + 0.31 * Math.sign(sn) * Math.pow(Math.abs(sn), 0.8))); }
        prof[0].x = 0; prof[40].x = 0;
        var lg = new THREE.LatheGeometry(prof, 64);
        var body = mesh(lg, M.pod, 0, 0, 0); body.scale.set(1, 1, 0.86); g.add(body);
        /* the band is a ring turned on the body's own profile, a hair proud of it, so it wraps the curve and takes the same light */
        if (o.band) { var bp = prof.filter(function (v) { return v.y > 0.25 && v.y < 0.42; }).map(function (v) { return new THREE.Vector2(v.x * 1.012 + 0.0015, v.y); });
          var band = mesh(new THREE.LatheGeometry(bp, 64), M.podBand, 0, 0, 0); band.scale.set(1, 1, 0.86); g.add(band); }
        /* no guide fins: at every distance this deck shows the pod, a fin read as a flat white card stuck to it */
        var bail = mesh(new THREE.TorusGeometry(0.04, 0.008, 8, 24, Math.PI), M.motor, 0, 0.62, 0); g.add(bail);
        return g;
      }
    });
    /* THE DOCK TOWER, where an aircraft launches, lands and charges: a steel column about `height` m on a concrete
     * pad with a cantilevered dock arm and a charging cradle, and a cabinet at its foot. Drawn to illustrate. */
    K.define("dock_tower", {
      size: [2.6, 6.4, 2.4],
      options: { height: 6, arm: 1.6, ring: true },
      note: "An illustrative drone dock tower: a galvanized lattice mast on a concrete pad, a trussed cantilever arm with a charging cradle, a cabinet, conduit and a ladder. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), h = o.height, w = 0.42, base = 0.2;
        g.add(K.box(2.0, base, 2.0, M.concrete, 0, 0, 0, 0.03));
        /* four angle legs and K bracing every 0.6 m, so the mast reads as a built thing at any distance */
        var leg = function (x, z) { var l = TXT.roundedBox(0.05, h, 0.05, 0.008, M.steel); l.position.set(x, base + h / 2, z); l.castShadow = l.receiveShadow = true; g.add(l); };
        [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(function (c) { leg(c[0] * w / 2, c[1] * w / 2); });
        var bays = Math.round(h / 0.6);
        for (var i = 0; i <= bays; i++) {
          var y = base + i * h / bays;
          [[0, -1, 0], [0, 1, 0], [-1, 0, 1], [1, 0, 1]].forEach(function (f) {
            var r = TXT.roundedBox(f[2] ? 0.03 : w, 0.03, f[2] ? w : 0.03, 0.006, M.steel); r.position.set(f[0] * w / 2, y, f[1] * w / 2); r.castShadow = true; g.add(r);
          });
          if (i < bays) {
            var dy = h / bays, diag = Math.sqrt(dy * dy + w * w), ang = Math.atan2(dy, w);
            [[0, -1, 0], [0, 1, 0], [-1, 0, 1], [1, 0, 1]].forEach(function (f, k) {
              var d = TXT.roundedBox(diag, 0.022, 0.022, 0.004, M.steel), sgn = (i + k) % 2 ? 1 : -1;
              if (f[2]) { d.rotation.y = Math.PI / 2; d.rotation.x = sgn * ang; d.position.set(f[0] * w / 2, y + dy / 2, 0); }
              else { d.rotation.z = sgn * ang; d.position.set(0, y + dy / 2, f[1] * w / 2); }
              d.castShadow = true; g.add(d);
            });
          }
        }
        /* the trussed arm, top and bottom chords with web members, reaching +z */
        var top = base + h;
        /* `reach` stops the trussed arm short of its tip, so a docked aircraft sits on a long cradle plate cantilevered
         * past the truss rather than inside it. Without it the plate is a short pad at the tip, under the chords. */
        var reach = o.reach != null ? o.reach : o.arm + 0.3;
        [top - 0.02, top - 0.32].forEach(function (yy) { var c = TXT.roundedBox(0.06, 0.06, reach, 0.01, M.steel); c.position.set(0, yy, reach / 2 - 0.1); c.castShadow = true; g.add(c); });
        for (var j = 0; j < 4; j++) { var wz = 0.25 + j * ((reach - 0.35) / 3), wm = TXT.roundedBox(0.03, 0.34, 0.03, 0.005, M.steel); wm.position.set(0, top - 0.17, wz); wm.rotation.x = (j % 2 ? 1 : -1) * 0.5; wm.castShadow = true; g.add(wm); }
        /* the charging cradle at the arm's tip, a dark plate with a dusk gold landing ring */
        var pz0 = o.reach != null ? reach - 0.25 : o.arm - 0.3, pz1 = o.arm + 0.3, pl = pz1 - pz0, pc = (pz0 + pz1) / 2;
        var cr = TXT.roundedBox(0.8, 0.07, pl, 0.02, M.steelDark); cr.position.set(0, top - 0.38, pc); cr.castShadow = cr.receiveShadow = true; g.add(cr);
        if (o.ring) { var ring = mesh(new THREE.TorusGeometry(0.26, 0.04, 10, 48), M.podBand, 0, top - 0.33, o.arm); ring.rotation.x = Math.PI / 2; g.add(ring); }
        /* the cradle plate's rim is banded in the same gold: this is where an order comes down to the ground first */
        if (o.ring) [[0, pz0, 0.8, 0.03], [0, pz1, 0.8, 0.03], [0.4, pc, 0.03, pl], [-0.4, pc, 0.03, pl]].forEach(function (q) { var b = TXT.roundedBox(q[2], 0.03, q[3], 0.008, M.podBand); b.position.set(q[0], top - 0.38, q[1]); g.add(b); });
        /* the cabinet, conduit up the mast and a caged ladder face */
        var cab = TXT.roundedBox(0.7, 1.3, 0.45, 0.03, M.steelDark); cab.position.set(0.7, base + 0.65, -0.1); cab.castShadow = cab.receiveShadow = true; g.add(cab);
        var cond = mesh(new THREE.CylinderGeometry(0.025, 0.025, h, 8), M.steelDark, w / 2 + 0.04, base + h / 2, 0); g.add(cond);
        for (var k = 0; k < Math.round(h / 0.3); k++) { var rung = TXT.roundedBox(0.3, 0.02, 0.02, 0.004, M.steel); rung.position.set(0, base + 0.3 + k * 0.3, -w / 2 - 0.12); g.add(rung); }
        var lamp = mesh(new THREE.SphereGeometry(0.045, 12, 8), M.navRed, 0, top + 0.06, 0); g.add(lamp);
        g.userData.attach = { cradle: [0, top - 0.3, o.arm] };
        return g;
      }
    });
    /* THE STREET GLOW, a town at night seen from the air: instanced lamp points on a jittered block grid of `pitch`
     * metres over `area` [x0, z0, x1, z1], skipping `avoid` rectangles, in sodium and LED whites. Emissive and never fogged
     * by the stage alone, so a lamp far off stays a point. Drawn to illustrate, the grid is no real street plan. */
    K.define("street_glow", {
      size: [2000, 0.4, 2000],
      options: { area: [-1000, -1000, 1000, 1000], pitch: 60, keep: 0.82, size: 2.2, avoid: [], block: 0, turn: 0, within: null },
      note: "Instanced emissive street lamp points on a jittered block grid, for a town at night from the air. Drawn to illustrate.",
      make: function (o, rng) {
        var g = new THREE.Group(), pts = [], a = o.area, r = lcg((o.seed || 1) * 977);
        var add = function (px, pz) { var skip = false;
          (o.avoid || []).forEach(function (v) { if (px > v[0] && px < v[2] && pz > v[1] && pz < v[3]) skip = true; });
          if (o.within && Math.hypot(px - o.within[0], pz - o.within[1]) > o.within[2]) skip = true;
          if (!skip) pts.push([px, pz, r()]); };
        if (o.block) {
          /* STREETS: lamps every `pitch` metres along a grid of streets `block` apart, turned by `turn`, so rows of
           * lamps converge in perspective the way a town does from the air; a few blocks go dark at random */
          var ct = Math.cos(o.turn || 0), st = Math.sin(o.turn || 0);
          for (var u = a[0]; u <= a[2]; u += o.block) for (var v = a[1]; v <= a[3]; v += o.pitch) {
            if (r() > o.keep) continue; var p1 = [u, v + (r() - 0.5) * 3], q1 = [v + (r() - 0.5) * 3, u];
            [p1, q1].forEach(function (pp) { add(pp[0] * ct - pp[1] * st, pp[0] * st + pp[1] * ct); });
          }
        } else {
          for (var x = a[0]; x <= a[2]; x += o.pitch) for (var z = a[1]; z <= a[3]; z += o.pitch) {
            if (r() > o.keep) continue;
            add(x + (r() - 0.5) * o.pitch * 0.5, z + (r() - 0.5) * o.pitch * 0.5);
          }
        }
        /* a lamp is a POINT of constant screen size, so one 3 km off is still a point and never an orb */
        [[0xffb35c, true], [0xfff1d8, false]].forEach(function (c) {
          var list = pts.filter(function (p) { return (p[2] < 0.7) === c[1]; }), arr = new Float32Array(list.length * 3);
          list.forEach(function (p, i) { arr[i * 3] = p[0]; arr[i * 3 + 1] = 4; arr[i * 3 + 2] = p[1]; });
          var geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(arr, 3));
          /* each lamp a soft glow with a hot core, so a street reads as lit rather than as hard square sprites */
          var pm = new THREE.PointsMaterial({ color: c[0], size: o.size * 2.8, map: N.glowTex(THREE), sizeAttenuation: false, fog: false, transparent: true, opacity: 1, depthWrite: false, blending: THREE.AdditiveBlending });
          var pt = new THREE.Points(geo, pm); pt.userData.txWear = false; g.add(pt);
        });
        g.userData.keepOrigin = true; g.userData.count = pts.length;
        return g;
      }
    });
    /* A SURVEY STAKE: a pine lath 0.05 by 0.025 by 0.9 m with a pointed foot driven 0.15 m, a painted top and a tail of
     * pink flagging ribbon. Origin at the ground. */
    K.define("survey_stake", {
      size: [0.3, 0.8, 0.05],
      options: { lean: 0, flag: true },
      note: "A pine survey lath with a painted top and pink flagging. Drawn to illustrate.",
      make: function (o, rng) {
        var g = new THREE.Group();
        var pine = K.mat("tt_pine", { color: 0xc8ab7c, roughness: 0.85 }), paint = K.mat("tt_stake_paint", { color: 0xe0dccf, roughness: 0.6 });
        var flagM = new THREE.MeshStandardMaterial({ color: 0xff4f8b, roughness: 0.7, side: THREE.DoubleSide });
        var lath = TXT.roundedBox(0.05, 0.75, 0.025, 0.004, pine); lath.position.y = 0.375; lath.castShadow = lath.receiveShadow = true; g.add(lath);
        var top = TXT.roundedBox(0.052, 0.08, 0.027, 0.004, paint); top.position.y = 0.71; top.castShadow = true; g.add(top);
        if (o.flag) {
          var fg = new THREE.PlaneGeometry(0.03, 0.32, 1, 8), pos = fg.attributes.position;
          for (var i = 0; i < pos.count; i++) { var yy = pos.getY(i); pos.setX(i, pos.getX(i) + Math.sin((yy + 0.16) * 9) * 0.02); pos.setZ(i, (0.16 - yy) * 0.25); }
          fg.computeVertexNormals();
          var f = new THREE.Mesh(fg, flagM); f.position.set(0.03, 0.56, 0.02); f.rotation.y = 0.6; f.castShadow = true; g.add(f);
        }
        g.rotation.z = o.lean || 0;
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
