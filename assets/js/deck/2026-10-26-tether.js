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
  N.mats = function (THREE, K) {
    if (N._m) return N._m;
    var b = skin(THREE, N.SEED); b.repeat.set(4, 4);
    var m = {
      shell: new THREE.MeshPhysicalMaterial({ color: 0xd8dbde, roughness: 0.42, metalness: 0.0, clearcoat: 0.6, clearcoatRoughness: 0.35, bumpMap: b, bumpScale: 0.35 }),
      shellDark: new THREE.MeshStandardMaterial({ color: 0x2a2d31, roughness: 0.55, metalness: 0.1 }),
      carbon: new THREE.MeshStandardMaterial({ color: 0x15171a, roughness: 0.38, metalness: 0.25 }),
      motor: new THREE.MeshStandardMaterial({ color: 0x3a3d42, roughness: 0.3, metalness: 0.75 }),
      blade: new THREE.MeshStandardMaterial({ color: 0x101113, roughness: 0.45, metalness: 0.05, side: THREE.DoubleSide }),
      pod: new THREE.MeshPhysicalMaterial({ color: 0xe4e2dc, roughness: 0.36, metalness: 0.0, clearcoat: 0.5, clearcoatRoughness: 0.3 }),
      podBand: new THREE.MeshStandardMaterial({ color: N.ACCENT, roughness: 0.45, metalness: 0.05, emissive: N.ACCENT, emissiveIntensity: 0.18 }),
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
        var bl = mesh(geo, M.blade, 0, 0.02, 0); bl.rotation.y = ang + k * Math.PI; g.add(bl);
      }
      if (blur) { /* a faint disc where the blades sweep, for an aircraft in flight */
        var d = new THREE.Mesh(new THREE.RingGeometry(0.05, r, 48), new THREE.MeshBasicMaterial({ color: 0x9aa3ad, transparent: true, opacity: blur * 0.5, side: THREE.DoubleSide, depthWrite: false }));
        d.rotation.x = -Math.PI / 2; d.position.y = 0.03; g.add(d);
      }
      return g;
    }
    /* THE DELIVERY DRONE. Front on +z. A lathe fuselage about 2.1 m long, a straight wing of `span` with rounded
     * tips, two carbon booms under the wing each carrying a lift rotor fore and aft, a pusher at the tail, a V tail,
     * nav lights at the wingtips and a strobe on top. `tether` lowers a line of that many metres from the belly winch
     * and userData.attach.pod is where its end hangs. Drawn to illustrate, to no maker's design. */
    K.define("delivery_drone", {
      size: [3.4, 0.6, 2.4],
      options: { span: 3.4, tether: 0, rotorAng: 0.4, blur: 0, lights: true, sag: 0 },
      note: "An illustrative fixed wing VTOL delivery drone: lathe fuselage, straight wing, two booms with four lift rotors, a pusher, a V tail, nav lights, an optional tether lowered from the belly. Drawn to illustrate, to no maker's design.",
      make: function (o) {
        var g = new THREE.Group(), Y = 0.32;
        /* fuselage, a lathe profile along z */
        var prof = [[0, -1.05], [0.06, -1.0], [0.11, -0.85], [0.16, -0.55], [0.19, -0.15], [0.2, 0.2], [0.185, 0.55], [0.15, 0.8], [0.09, 0.98], [0, 1.06]];
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
          var boom = mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.25, 16), M.carbon, bx, Y + 0.06, 0.05); boom.rotation.x = Math.PI / 2; g.add(boom);
          [0.95, -0.85].forEach(function (z, i) {
            var pod = mesh(new THREE.CylinderGeometry(0.05, 0.045, 0.12, 20), M.shellDark, bx, Y + 0.1, z); g.add(pod);
            var rr = rotor(0.4, o.rotorAng + (s > 0 ? 0.7 : 0) + i * 1.1, o.blur); rr.position.set(bx, Y + 0.17, z); g.add(rr);
          });
        });
        /* the V tail and the pusher */
        [-1, 1].forEach(function (s) {
          var fin = TXT.roundedBox(0.03, 0.34, 0.24, 0.012, M.shell); fin.castShadow = true;
          fin.position.set(s * 0.12, Y + 0.18, -0.9); fin.rotation.z = -s * 0.62; g.add(fin);
        });
        var push = rotor(0.26, o.rotorAng * 2, o.blur); push.rotation.x = Math.PI / 2; push.position.set(0, Y, -1.1); g.add(push);
        if (o.lights) g.add(mesh(new THREE.SphereGeometry(0.02, 12, 8), M.strobe, 0, Y + 0.17, -0.2));
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
     * top, two small guide fins and an amber band, the deck's one accent. Origin at its base. */
    K.define("delivery_pod", {
      size: [0.42, 0.66, 0.36],
      options: { band: true },
      note: "An illustrative lowered delivery pod with a bail, guide fins and an amber band. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group();
        /* a smooth profile: a superellipse of half width 0.2 and half height 0.31, so the shoulders round off */
        var prof = [];
        for (var i = 0; i <= 40; i++) { var t = -Math.PI / 2 + Math.PI * i / 40, c = Math.cos(t), sn = Math.sin(t);
          prof.push(new THREE.Vector2(0.2 * Math.pow(Math.abs(c), 0.55), 0.31 + 0.31 * Math.sign(sn) * Math.pow(Math.abs(sn), 0.8))); }
        prof[0].x = 0; prof[40].x = 0;
        var lg = new THREE.LatheGeometry(prof, 64);
        var body = mesh(lg, M.pod, 0, 0, 0); body.scale.set(1, 1, 0.86); g.add(body);
        if (o.band) { var band = mesh(new THREE.CylinderGeometry(0.203, 0.203, 0.05, 48, 1, true), M.podBand, 0, 0.33, 0); band.scale.set(1, 1, 0.86); g.add(band); }
        [-1, 1].forEach(function (s) { var f = TXT.roundedBox(0.012, 0.22, 0.12, 0.004, M.shellDark); f.position.set(s * 0.205, 0.22, 0); g.add(f); });
        var bail = mesh(new THREE.TorusGeometry(0.04, 0.008, 8, 24, Math.PI), M.motor, 0, 0.62, 0); g.add(bail);
        return g;
      }
    });
    /* THE DOCK TOWER, where an aircraft launches, lands and charges: a steel column about `height` m on a concrete
     * pad with a cantilevered dock arm and a charging cradle, and a cabinet at its foot. Drawn to illustrate. */
    K.define("dock_tower", {
      size: [2.6, 6.2, 1.8],
      options: { height: 6, arm: 1.6, docked: false },
      note: "An illustrative drone dock tower: a steel column on a concrete pad, a cantilever arm with a charging cradle, a cabinet at its foot. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), h = o.height;
        g.add(K.box(1.8, 0.2, 1.8, M.concrete, 0, 0, 0, 0.03));
        var col = TXT.roundedBox(0.32, h, 0.32, 0.03, M.steel); col.position.set(0, 0.2 + h / 2, 0); col.castShadow = col.receiveShadow = true; g.add(col);
        var arm = TXT.roundedBox(0.22, 0.18, o.arm, 0.02, M.steel); arm.position.set(0, 0.2 + h - 0.1, o.arm / 2); arm.castShadow = true; g.add(arm);
        var cradle = TXT.roundedBox(0.7, 0.06, 0.5, 0.02, M.steelDark); cradle.position.set(0, 0.2 + h - 0.24, o.arm - 0.1); cradle.castShadow = true; g.add(cradle);
        var cab = TXT.roundedBox(0.7, 1.3, 0.45, 0.03, M.steelDark); cab.position.set(0.55, 0.2 + 0.65, 0); cab.castShadow = cab.receiveShadow = true; g.add(cab);
        var lamp = mesh(new THREE.SphereGeometry(0.04, 12, 8), M.strobe, 0, 0.2 + h + 0.06, 0); g.add(lamp);
        g.userData.attach = { cradle: [0, 0.2 + h - 0.2, o.arm - 0.1] };
        return g;
      }
    });
  };

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
