/* deck/2026-10-03-norther.js — the chassis for the 2026-10-03 deck: Kodiak AI names Interstate 45
 * from Dallas to Houston as its first driverless truck lane, and says the safety observer comes
 * out only after it closes its safety case, which its own measure put at 93 of 100 at the end of
 * August (tx-2026-0198).
 *
 * THE WORLD. The Lancaster end of Interstate 45 on an October morning, a norther lying to the
 * northwest: stormFront, tuned once here. The haze is pulled from the preset's West Texas dust to a
 * Blackland green grey and thinned, so the world reads past a kilometre. The front stays behind the
 * truck. Nothing in it is rain or lightning.
 *
 * DIRECTIONS. +x is east and -z is north. The light is declared at az 68, el 11: the sun low in the
 * east southeast. az runs clockwise from +z toward +x, so the key sits at (sin 68, ., cos 68).
 * At the hub the van's rear faces east, so the low sun shines into its open doors. On the highway
 * the truck runs south toward +z, so its driver side (+x, east) faces the sun.
 *
 * THE HERO OBJECT. One Class 8 tractor (the kit's semi_truck, sensors full, no trailer) and one 53 ft
 * dry van, `dry_van`, the kit addition below: a white plate van whose interior is divided into 100
 * places, 50 rows of 0.318 m by 2 files, loaded from the nose one carton stack per place. Its swing
 * doors fold flat against its sides. The load is a DRAWING of Kodiak's own readiness measure, one
 * stack per percentage point, and the frames that show it say so. It is never a claim about what any
 * Kodiak trailer carries.
 *
 * THE ACCENT. #B4664F, dusk_ember in config/brand.yaml: the pair of decking beams across the load
 * face, and frame 5's AUG 93 label. Never a carton, never the ground, never a light.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the kit
 * additions and the deck's materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("norther.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "norther",
    light: { az: 68, el: 11 },
    sky: { preset: "stormFront", haze: 0x8c9088, fogDensity: 0.0026, clouds: 1.0 },
    ground: "#1C2027",
    material: "#DADDE0",
    accent: "#B4664F",
    grade: {
      exposure: 0.0,
      saturation: 1.02,
      contrast: 1.06,
      filmic: true,
      lift: [0.007, 0.008, 0.011],
      gain: [1.01, 1.0, 0.985],
      vignette: 0.2,
      bloom: { threshold: 0.82, strength: 0.2, radius: 14 },
      grain: { amount: 0.012, size: 2, seed: 20261003 },
      aberration: 0,
      dither: true,
      sharpen: 0.16
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261003;
  N.ACCENT = 0xb4664f;

  /* THE VAN'S DIMENSIONS, metres. A 53 ft plate van: 16.15 long, 2.59 wide, 4.10 tall, floor at
   * 1.24. The interior is 15.9 long, the 100 places are 50 rows of 0.318 by 2 files of 1.245. */
  var V = N.VAN = { L: 16.15, W: 2.59, H: 4.1, FL: 1.24, FT: 0.06, IL: 15.9, IW: 2.49, ROWS: 50, ROW: 0.318 };
  V.FLOOR_TOP = V.FL + V.FT;
  V.Z_NOSE_IN = V.L / 2 - 0.12;                 /* the interior's front wall, local z */
  V.Z_DOOR = -V.L / 2;                          /* the rear opening's plane */
  /* where the load face stands after n places, loaded from the nose: interior length x n / 100 */
  N.faceZ = function (n) { return V.Z_NOSE_IN - V.IL * n / 100; };

  /* THE TRACTOR AND THE VAN, coupled the way the kit couples its own trailer: the kit tractor's
   * front bumper at its local z 0 before it centres itself, and the van's nose at -5.1 from it. */
  N.TRACTOR_SHIFT = 3.825;                      /* semi_truck trailer:false centres by this */
  N.VAN_FROM_TRACTOR = -(5.1 - N.TRACTOR_SHIFT) - V.L / 2;

  /* ---------------------------------------------------------------- textures */
  N.tex = {};
  function canvasTex(THREE, name, w, h, draw, rep) {
    if (N.tex[name]) return N.tex[name];
    var c = document.createElement("canvas"); c.width = w; c.height = h;
    draw(c.getContext("2d"), w, h);
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (rep) t.repeat.set(rep[0], rep[1]);
    N.tex[name] = t; return t;
  }
  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }

  /* laminated oak trailer floor: strips 0.25 m wide along the van's length, a shade apart, nail
   * lines across them and two dark wheel tracks worn in by pallet jacks */
  N.oakTex = function (THREE) {
    return canvasTex(THREE, "oak", 512, 1024, function (x, w, h) {
      var r = lcg(77), strips = 8;
      for (var i = 0; i < strips; i++) {
        var base = 150 + Math.floor(r() * 26), x0 = i * w / strips;
        x.fillStyle = "rgb(" + base + "," + Math.floor(base * 0.74) + "," + Math.floor(base * 0.5) + ")";
        x.fillRect(x0, 0, w / strips, h);
        for (var g = 0; g < 70; g++) {
          x.strokeStyle = "rgba(60,36,18," + (0.06 + r() * 0.1) + ")"; x.lineWidth = 0.6 + r() * 1.4;
          var gx = x0 + r() * w / strips; x.beginPath(); x.moveTo(gx, 0); x.bezierCurveTo(gx + 4 * (r() - 0.5), h * 0.3, gx + 6 * (r() - 0.5), h * 0.7, gx + 3 * (r() - 0.5), h); x.stroke();
        }
        x.fillStyle = "rgba(30,18,10,0.55)"; x.fillRect(x0, 0, 2, h);
      }
      for (var n = 0; n < 40; n++) { var ny = r() * h; x.fillStyle = "rgba(25,20,18,0.5)"; for (var k = 0; k < strips; k++) x.fillRect(k * w / strips + 14 + r() * 30, ny, 3, 3); }
      [0.3, 0.7].forEach(function (f) {
        var g2 = x.createLinearGradient(w * f - 40, 0, w * f + 40, 0);
        g2.addColorStop(0, "rgba(20,14,10,0)"); g2.addColorStop(0.5, "rgba(20,14,10,0.32)"); g2.addColorStop(1, "rgba(20,14,10,0)");
        x.fillStyle = g2; x.fillRect(w * f - 40, 0, 80, h);
      });
    }, [1, 4]);
  };
  /* kraft corrugated board: a warm mid tone, faint flute lines and fibre flecks */
  N.kraftTex = function (THREE) {
    return canvasTex(THREE, "kraft", 256, 256, function (x, w, h) {
      var r = lcg(311);
      x.fillStyle = "#b39468"; x.fillRect(0, 0, w, h);
      for (var i = 0; i < 2600; i++) { var v = r(); x.fillStyle = v < 0.5 ? "rgba(255,240,210,0.16)" : "rgba(90,62,34,0.18)"; x.fillRect(r() * w, r() * h, 1 + r() * 2, 1); }
      for (var y = 0; y < h; y += 5) { x.fillStyle = "rgba(80,56,30,0.07)"; x.fillRect(0, y, w, 1); }
      for (var s = 0; s < 6; s++) { x.fillStyle = "rgba(70,48,26," + (0.05 + r() * 0.08) + ")"; x.fillRect(r() * w, r() * h, 20 + r() * 60, 3 + r() * 10); }
    }, [1, 1]);
  };
  /* white scuff liner: a plywood liner painted white, scuffed grey at forklift height */
  N.linerTex = function (THREE) {
    return canvasTex(THREE, "liner", 512, 256, function (x, w, h) {
      var r = lcg(91);
      x.fillStyle = "#e4e1da"; x.fillRect(0, 0, w, h);
      for (var i = 0; i < 260; i++) { x.strokeStyle = "rgba(70,66,60," + (0.05 + r() * 0.12) + ")"; x.lineWidth = 1 + r() * 2; var y = h * (0.45 + r() * 0.5), xx = r() * w; x.beginPath(); x.moveTo(xx, y); x.lineTo(xx + 20 + r() * 80, y + (r() - 0.5) * 6); x.stroke(); }
      for (var p = 0; p < w; p += 64) { x.fillStyle = "rgba(60,58,54,0.25)"; x.fillRect(p, 0, 2, h); }
    }, [8, 1]);
  };

  /* ---------------------------------------------------------------- materials */
  N.mats = function (K, THREE, TXT) {
    if (N._m) return N._m;
    N._m = {
      skin: K.mat("nt-skin", { color: 0xe9e6df, roughness: 0.48, metalness: 0.08 }),
      skinIn: K.mat("nt-skinin", { color: 0xd8d4cc, roughness: 0.7, metalness: 0.0 }),
      post: K.mat("nt-post", { color: 0xc6c9cc, roughness: 0.34, metalness: 0.65 }),
      alu: K.mat("nt-alu", { color: 0xb9bcbf, roughness: 0.38, metalness: 0.75 }),
      frame: K.mat("nt-frame", { color: 0x202224, roughness: 0.6, metalness: 0.4 }),
      rubber: K.mat("nt-rubber", { color: 0x141414, roughness: 0.92, metalness: 0 }),
      rim: K.mat("nt-rim", { color: 0xcfd2d4, roughness: 0.25, metalness: 0.9 }),
      chrome: K.mat("nt-chrome", { color: 0xe8eaec, roughness: 0.12, metalness: 1.0 }),
      oak: K.mat("nt-oak", { color: 0xffffff, roughness: 0.62, metalness: 0, map: N.oakTex(THREE) }),
      liner: K.mat("nt-liner", { color: 0xffffff, roughness: 0.85, metalness: 0, map: N.linerTex(THREE) }),
      track: K.mat("nt-etrack", { color: 0x8f9396, roughness: 0.4, metalness: 0.8 }),
      kraft: K.mat("nt-kraft", { color: 0xffffff, roughness: 0.93, metalness: 0, map: N.kraftTex(THREE) }),
      tape: K.mat("nt-tape", { color: 0xcdb48a, roughness: 0.55, metalness: 0 }),
      beam: K.mat("nt-beam3", { color: 0x4a2a22, roughness: 0.8, metalness: 0.0, emissive: 0xb4664f, emissiveIntensity: 0.72 }),
      pad: K.mat("nt-pad", { color: 0x0e0e0e, roughness: 0.9 }),
      floorTape: K.mat("nt-ftape", { color: 0xe8dcc6, roughness: 0.6, emissive: 0x3a3428, emissiveIntensity: 0.6 }),
      tail: K.mat("nt-tail", { color: 0x3a1a14, roughness: 0.45, emissive: 0x1a0804, emissiveIntensity: 0.15 }),
      amber: K.mat("nt-amber", { color: 0xd98a1c, roughness: 0.3, emissive: 0x6a3a06, emissiveIntensity: 0.5 }),
      reflector: K.mat("nt-rpm", { color: 0xf2b23a, roughness: 0.2, metalness: 0.2, emissive: 0xffb43a, emissiveIntensity: 1.6 }),
      rpmBody: K.mat("nt-rpmbody", { color: 0xe8e2cc, roughness: 0.6 })
    };
    return N._m;
  };

  /* ---------------------------------------------------------------- the kit additions */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.dry_van) return;
    var M = N.mats(K, THREE, TXT);

    /* a dual wheel set on one side of one axle: two tyres, rims and a hub, axis along x */
    function duals(g, x, z, side) {
      var R = 0.52, Wt = 0.28;
      for (var k = 0; k < 2; k++) {
        var tx = x + side * (k * 0.31);
        var tyre = new THREE.Mesh(new THREE.CylinderGeometry(R, R, Wt, 40), M.rubber); tyre.rotation.z = Math.PI / 2; tyre.position.set(tx, R, z); tyre.castShadow = true; g.add(tyre);
        var sw = new THREE.Mesh(new THREE.TorusGeometry(R - 0.06, 0.05, 8, 40), M.rubber); sw.rotation.y = Math.PI / 2; sw.position.set(tx + side * Wt / 2, R, z); g.add(sw);
        if (k === 1) {
          var rim = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.02, 32), M.rim); rim.rotation.z = Math.PI / 2; rim.position.set(tx + side * (Wt / 2 + 0.005), R, z); g.add(rim);
          var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.13, 0.12, 20), M.rim); hub.rotation.z = Math.PI / 2; hub.position.set(tx + side * (Wt / 2 + 0.05), R, z); g.add(hub);
        }
      }
    }

    /* dry_van — a 53 ft plate van. Origin on the ground at the centre of its footprint, nose to +z.
     * options:
     *   doors     'open' (swung flat against the sides) | 'closed'
     *   roof      true | false (lifted off, for a count from above)
     *   nearWall  null | 'left' (+x) | 'right' (-x), a side taken off to see the load in section
     *   load      0..100, places filled from the nose, one carton stack each
     *   bar       true puts the decking beams at the load face
     *   tapes     [values], pale floor tapes where the face stood at those values
     */
    K.define("dry_van", {
      size: [V.W, V.H, V.L],
      options: { doors: "closed", swing: 0.42, roof: true, nearWall: null, load: 0, bar: false, tapes: [], seed: 1 },
      note: "A 53 ft dry van (16.15 x 2.59 x 4.1 m, floor at 1.24 m), its interior divided into 100 places of 0.318 m by 1.245 m, loaded from the nose one carton stack per place. doors open|closed, roof, nearWall left|right, load 0 to 100, bar, tapes. Nose to +z.",
      make: function (o) {
        var g = new THREE.Group(), hw = V.W / 2, L = V.L, FL = V.FL, H = V.H, zc = 0;
        var wallT = 0.03, inW = V.IW, iy0 = V.FLOOR_TOP, iy1 = H - 0.1;
        /* floor, under frame and crossmembers */
        K.box(inW + 0.06, V.FT, L - 0.05, M.oak, 0, FL, zc, 0.004, g);
        K.box(1.0, 0.28, L - 1.2, M.frame, 0, FL - 0.28, zc, 0.02, g);
        for (var cz = -L / 2 + 0.5; cz < L / 2 - 0.4; cz += 0.6) K.box(2.4, 0.1, 0.07, M.frame, 0, FL - 0.11, cz, 0, g);
        for (var s = -1; s <= 1; s += 2) K.box(0.06, 0.16, L, M.alu, s * (hw - 0.02), FL - 0.06, zc, 0.01, g);   /* bottom rails */
        /* walls: outer skin, posts, inner liner, E-track */
        [["left", 1], ["right", -1]].forEach(function (pair) {
          var side = pair[0], sx = pair[1];
          if (o.nearWall === side) {
            /* the cut: the van's own aluminium top and bottom rails stay, the skin is gone */
            K.box(0.06, 0.08, L, M.alu, sx * (hw - 0.02), H - 0.1, zc, 0.01, g);
            return;
          }
          K.box(wallT, H - FL - 0.04, L, M.skin, sx * (hw - wallT / 2), FL + 0.02, zc, 0.004, g);
          var posts = [];
          for (var pz = L / 2 - 0.6; pz > -L / 2 + 0.4; pz -= 1.22) posts.push(K.box(0.012, H - FL - 0.3, 0.05, M.post, sx * (hw + 0.004), FL + 0.15, pz));
          g.add(K.merge(posts, M.post));
          K.box(0.04, 0.06, L, M.post, sx * (hw + 0.004), H - 0.08, zc, 0.01, g);
          /* inside: liner to 1.2 m above the floor, bare skin above it, two rows of E-track */
          K.box(0.012, 1.2, V.IL, M.liner, sx * (inW / 2 + 0.006), iy0, zc - 0.05, 0, g);
          [1.2, 2.1].forEach(function (ty) { K.box(0.008, 0.12, V.IL, M.track, sx * (inW / 2 - 0.004), iy0 + ty - 0.06, zc - 0.05, 0, g); });
          /* amber side markers */
          for (var mz = L / 2 - 1.5; mz > -L / 2 + 1; mz -= 3) K.box(0.04, 0.05, 0.08, M.amber, sx * (hw + 0.02), FL + 0.18, mz, 0.01, g);
        });
        /* roof and roof bows */
        if (o.roof !== false) {
          K.box(V.W, 0.05, L, M.skin, 0, H - 0.05, zc, 0.02, g);
          for (var bz = L / 2 - 0.4; bz > -L / 2 + 0.3; bz -= 0.6) K.box(inW, 0.04, 0.05, M.skinIn, 0, H - 0.1, bz, 0, g);
        } else {
          K.box(V.W, 0.05, 0.12, M.alu, 0, H - 0.06, L / 2 - 0.06, 0.01, g);
        }
        /* nose wall */
        K.box(V.W, H - FL, 0.12, M.skin, 0, FL, L / 2 - 0.06, 0.01, g);
        /* rear frame: header, sill, corner posts */
        var rz = -L / 2;
        K.box(V.W, 0.22, 0.14, M.alu, 0, H - 0.22, rz + 0.07, 0.01, g);
        K.box(V.W, 0.14, 0.16, M.alu, 0, FL - 0.06, rz + 0.08, 0.01, g);
        for (s = -1; s <= 1; s += 2) K.box(0.12, H - FL, 0.14, M.alu, s * (hw - 0.06), FL, rz + 0.07, 0.01, g);
        /* two swing doors, each hinged on its outer edge */
        var dw = (V.W - 0.08) / 2, dh = H - FL - 0.3;
        [1, -1].forEach(function (sx) {
          /* a side taken off for a section takes its door with it, or the door folded flat against
           * that side would hide exactly the places the section is drawn to show */
          if ((o.nearWall === "left" && sx > 0) || (o.nearWall === "right" && sx < 0)) return;
          var pivot = new THREE.Group(); pivot.position.set(sx * (hw + 0.02), FL + 0.08, rz - 0.03);
          var door = new THREE.Group();
          K.box(dw, dh, 0.045, M.skin, -sx * dw / 2, 0, 0, 0.01, door);                                  /* outer face toward -z */
          var inner = K.box(dw - 0.08, dh - 0.12, 0.01, M.liner, -sx * dw / 2, 0.06, 0.028, 0, door);  /* inner face */
          [0.32, 0.9].forEach(function (f) {
            var x = -sx * dw * f;
            K.box(0.03, dh - 0.1, 0.03, M.chrome, x, 0.05, -0.04, 0.01, door);                          /* lock rod */
            [0.12, dh - 0.2].forEach(function (y) { K.box(0.09, 0.07, 0.05, M.post, x, y, -0.045, 0.01, door); });  /* cam keepers */
            K.box(0.14, 0.04, 0.05, M.post, x + sx * 0.05, dh * 0.42, -0.06, 0.01, door);               /* handle */
          });
          [0.15, dh * 0.38, dh * 0.62, dh - 0.25].forEach(function (y) { K.box(0.16, 0.1, 0.05, M.post, -sx * 0.06, y, -0.035, 0.01, door); });  /* hinges */
          pivot.add(door);
          if (o.doors === "open") { var sw = (o.swing == null ? 0.42 : o.swing) * Math.PI; pivot.rotation.y = sx > 0 ? sw : -sw; }
          g.add(pivot);
        });
        /* tail lamps, ICC bumper, mud flaps, landing gear, tandem */
        for (s = -1; s <= 1; s += 2) {
          K.box(0.14, 0.2, 0.05, M.tail, s * (hw - 0.25), FL - 0.25, rz - 0.04, 0.01, g);
          K.box(0.5, 0.6, 0.02, M.rubber, s * 0.82, 0.18, rz + 1.25, 0, g);
          K.box(0.1, FL - 0.1, 0.1, M.frame, s * 0.75, 0.1, L / 2 - 3.6, 0.01, g);
          K.box(0.3, 0.05, 0.3, M.frame, s * 0.75, 0.05, L / 2 - 3.6, 0.01, g);
        }
        K.box(2.3, 0.14, 0.12, M.frame, 0, 0.46, rz + 0.2, 0.02, g);
        for (s = -1; s <= 1; s += 2) K.box(0.1, 0.62, 0.1, M.frame, s * 0.7, 0.5, rz + 0.3, 0.01, g);
        [rz + 1.9, rz + 3.12].forEach(function (az) { duals(g, 0.82, az, 1); duals(g, -0.82, az, -1); K.box(1.7, 0.12, 0.12, M.frame, 0, 0.52, az, 0, g); });
        /* the load: n stacks of four kraft cartons from the nose, two files, row by row */
        var n = Math.max(0, Math.min(100, Math.round(o.load || 0)));
        if (n > 0) g.add(N.stacks(K, THREE, n, o.seed || 1));
        if (o.bar) g.add(N.beams(K, THREE, n));
        /* the tapes: where the load face stood at earlier values. The floor there is under stacks now,
         * so each is a pale band round both bottom rails and a strip up the far wall above the load. */
        (o.tapes || []).forEach(function (t) {
          var tz = N.faceZ(t);
          [1, -1].forEach(function (sx) { K.box(0.08, 0.5, 0.22, M.floorTape, sx * (hw - 0.02), FL - 0.18, tz, 0.005, g); });
          K.box(0.012, iy1 - iy0 - 2.42, 0.1, M.floorTape, -(inW / 2 - 0.02), iy0 + 2.42, tz, 0, g);
        });
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        g.userData.faceZ = N.faceZ(n);
        return g;
      }
    });

    /* delineator — a roadside delineator post as Texas highways set them along the shoulder: a white
     * flexible post 1.2 m tall with an amber retroreflective panel at its head, facing +z. */
    K.define("delineator", {
      size: [0.1, 1.25, 0.1],
      options: { seed: 1 },
      note: "A roadside delineator post, a white flexible post 1.2 m tall with an amber retroreflective panel at its head facing +z, its base driven into the shoulder.",
      make: function () {
        var g = new THREE.Group();
        K.box(0.085, 1.2, 0.03, M.rpmBody, 0, 0, 0, 0.012, g);
        K.box(0.085, 0.22, 0.008, M.reflector, 0, 0.95, 0.02, 0, g);
        K.box(0.12, 0.04, 0.06, M.frame, 0, 0, 0, 0, g);
        return g;
      }
    });

    /* raised_pavement_marker — a retroreflective lane marker, 10 cm square, its amber face toward
     * the oncoming traffic (+z faces the lens of a truck running toward -z... a frame turns it). */
    K.define("raised_pavement_marker", {
      size: [0.1, 0.02, 0.1],
      options: { seed: 1 },
      note: "A raised retroreflective pavement marker, 10 x 10 cm and 2 cm proud, its reflective face toward +z.",
      make: function () {
        var g = new THREE.Group();
        K.box(0.1, 0.018, 0.1, M.rpmBody, 0, 0, 0, 0.006, g);
        var f = K.box(0.08, 0.012, 0.01, M.reflector, 0, 0.003, 0.048, 0, g);
        return g;
      }
    });
  };

  /* THE STACKS, one per place, as two instanced meshes (cartons and their tape), seeded so the
   * same frame renders the same lean every time. Place p (1..n) is row floor((p-1)/2), file
   * (p-1) % 2: the left file of a row loads before the right. */
  N.stacks = function (K, THREE, n, seed) {
    var M = N._m, r = lcg(4000 + seed), g = new THREE.Group();
    var per = 4, cw = 1.18, ch = 0.585, cd = 0.29;
    var geo = new THREE.BoxGeometry(cw, ch, cd);
    var tapeGeoF = new THREE.BoxGeometry(0.08, ch * 0.96, 0.004), tapeGeoT = new THREE.BoxGeometry(0.08, 0.004, cd * 0.98);
    var cart = new THREE.InstancedMesh(geo, M.kraft, n * per);
    var tapes = new THREE.InstancedMesh(tapeGeoF, M.tape, n * per);
    var tops = new THREE.InstancedMesh(tapeGeoT, M.tape, n);
    var m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), p = new THREE.Vector3(), sc = new THREE.Vector3(1, 1, 1);
    var col = new THREE.Color();
    for (var i = 0; i < n; i++) {
      var row = Math.floor(i / 2), file = i % 2;
      var x = (file === 0 ? 1 : -1) * 0.623, z = V.Z_NOSE_IN - V.ROW * (row + 0.5);
      for (var k = 0; k < per; k++) {
        var lean = (r() - 0.5) * 0.02, yaw = (r() - 0.5) * 0.03;
        e.set(0, yaw, lean); q.setFromEuler(e);
        var y = V.FLOOR_TOP + ch * (k + 0.5) + 0.002 * k;
        p.set(x + (r() - 0.5) * 0.02, y, z + (r() - 0.5) * 0.012);
        sc.set(0.98 + r() * 0.03, 1, 0.97 + r() * 0.04);
        m4.compose(p, q, sc); cart.setMatrixAt(i * per + k, m4);
        var shade = 0.82 + r() * 0.24; col.setRGB(shade, shade * (0.97 + r() * 0.05), shade * (0.93 + r() * 0.08)); cart.setColorAt(i * per + k, col);
        /* the tape strip on the face toward the doors */
        var tp = new THREE.Vector3(p.x + (r() - 0.5) * 0.1, p.y, p.z - cd / 2 - 0.002);
        m4.compose(tp, q, new THREE.Vector3(1, 1, 1)); tapes.setMatrixAt(i * per + k, m4);
        if (k === per - 1) { m4.compose(new THREE.Vector3(p.x, p.y + ch / 2 + 0.002, p.z), q, new THREE.Vector3(1, 1, 1)); tops.setMatrixAt(i, m4); }
      }
    }
    [cart, tapes, tops].forEach(function (im) { im.castShadow = true; im.receiveShadow = true; im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true; g.add(im); });
    return g;
  };

  /* THE DECKING BEAMS across the load face, the accent: two square tubes at 0.9 and 1.8 m above the
   * floor with black rubber end pads against the E-track, set just behind the last full row of the
   * left file. */
  N.beams = function (K, THREE, n) {
    var M = N._m, g = new THREE.Group(), rows = Math.ceil(n / 2), z = V.Z_NOSE_IN - V.ROW * rows - 0.05;
    [0.9, 1.8].forEach(function (h) {
      K.box(V.IW - 0.12, 0.14, 0.12, M.beam, 0, V.FLOOR_TOP + h, z, 0.014, g);
      [1, -1].forEach(function (sx) { K.box(0.05, 0.12, 0.1, M.pad, sx * (V.IW / 2 - 0.045), V.FLOOR_TOP + h - 0.02, z, 0.01, g); });
    });
    return g;
  };

  /* THE RIG: the kit tractor and the chassis's van, coupled, nose to +z. Returns the group and the
   * van, so a frame can read the van's own load face. */
  N.rig = function (K, o) {
    o = o || {};
    var g = new N.T.Group();
    var tr = K.make("semi_truck", { seed: 41, sensors: "full", trailer: false, color: 0xedeae3, lettering: null });
    g.add(tr);
    var van = K.make("dry_van", Object.assign({ seed: 3 }, o.van || {}));
    van.position.z = N.VAN_FROM_TRACTOR; g.add(van);
    if (o.lights) {
      var head = new N.T.MeshStandardMaterial({ color: 0xfff4dc, emissive: 0xfff0d0, emissiveIntensity: 6 });
      [1, -1].forEach(function (sx) {
        var l = new N.T.Mesh(new N.T.CircleGeometry(0.11, 24), head); l.position.set(sx * 0.84, 1.5, N.TRACTOR_SHIFT + 0.03); g.add(l);
      });
    }
    g.userData.van = van; g.userData.tractor = tr;
    return g;
  };

  /* THE RIG AT THE HUB: nose west, the van's rear to the low east sun, the van's centre on the
   * origin, standing on its contact. Local van z maps to world x. */
  N.hubRig = function (K, R, TXT, van) {
    var rig = N.rig(K, { van: van });
    rig.rotation.y = -Math.PI / 2; rig.position.x = N.VAN_FROM_TRACTOR;
    TXT.add(R, rig); TXT.contact(R, rig, { opacity: 0.75 });
    return rig;
  };

  /* ---------------------------------------------------------------- places */
  N.COURT = { surface: "concrete", size: 300, tile: 6, seed: 23, joints: true };
  /* the Blackland beyond the court's edge, a hand's breadth below it so the slab stands on it */
  N.CLAY = { surface: "dirt", size: 6000, tile: 5, seed: 19, color: 0x4a4034, y: -0.03 };
  N.SOIL = { surface: "dirt", size: 6000, tile: 5, seed: 17, color: 0x3a352e };

  /* THE HUB: a jointed concrete truck court, the kit warehouse hazed behind, the prairie's grass
   * beyond the court's edge, kept off the type with avoid rectangles. */
  N.hub = function (K, R, TXT, o) {
    o = o || {};
    /* the frame lays the court itself, TXT.ground(R, NR.COURT), so its ground is in its own code */
    TXT.ground(R, N.CLAY);   /* the Blackland past the court's edge */
    var wh = K.make("warehouse", { seed: 5, docks: true, trucks: 3 });
    var wp = o.warehouse || [-150, -120];
    wh.position.set(wp[0], 0, wp[1]); wh.rotation.y = o.whYaw || 0.35; TXT.add(R, wh);
    TXT.scatter(R, { kind: "grass", count: o.grass || 9000, area: o.grassArea || [-400, -400, 400, 400], avoid: (o.avoid || []).concat([[-60, -50, 60, 50]]), seed: 31, scale: 1.1 });
  };

  /* SOMETHING IN THE YARD BEYOND: a closed van parked on the court and a pickup, at true scale. */
  N.yard = function (K, R, TXT, list) {
    (list || []).forEach(function (it) {
      var m = it.kind === "van" ? K.make("dry_van", { seed: it.seed || 9, doors: "closed" }) : K.make(it.kind, Object.assign({ seed: it.seed || 2 }, it.opts || {}));
      m.position.set(it.at[0], 0, it.at[1]); m.rotation.y = it.yaw || 0; TXT.add(R, m); TXT.contact(R, m, { opacity: 0.6 });
    });
  };

  /* THE ROAD: a run of the kit highway along z, Blackland ground, fields and fencerows. */
  N.road = function (K, R, TXT, o) {
    o = o || {};
    var seg = o.seg || 200, n = o.segs || 3, z0 = o.z0 == null ? -seg : o.z0;
    /* the frame lays the Blackland ground itself, TXT.ground(R, NR.SOIL) */
    for (var i = 0; i < n; i++) {
      /* the pavement at ground level, so a truck placed at y 0 stands on it */
      var hw = K.make("highway", { seed: 7 + i, length: seg, lanes: 2, surface: "concrete", gantry: false, overpass: false, embank: o.embank == null ? 0 : o.embank, ground: 0x4a4636 });
      /* RURAL I-45 BETWEEN DALLAS AND HOUSTON RUNS ON A GRASSED MEDIAN over long stretches, so a
       * frame may take the kit's F-shape barrier out: every piece of it is under 0.8 m wide and
       * centred on the median line. */
      if (o.barrier === false) {
        var box = new N.T.Box3(), size = new N.T.Vector3(), ctr = new N.T.Vector3();
        hw.children.forEach(function (c) {
          box.setFromObject(c); box.getSize(size); box.getCenter(ctr);
          if (size.x < 0.8 && Math.abs(ctr.x) < 0.3) c.visible = false;
        });
      }
      hw.position.set(0, 0, z0 + i * seg); TXT.add(R, hw);
    }
  };

  /* ---------------------------------------------------------------- the frame shell */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  /* THE RIG FOR A TRUCK: the world's own key, its shadow camera widened to cover a 22 m truck */
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 16, mapSize: map || 2048, radius: 6 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 60, shadowFar: o.shadowFar || 160, normalBias: o.normalBias == null ? 0.02 : o.normalBias };
  };

  /* THE SKY BAND THE TYPE STANDS IN, never over 0.45 alpha. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 80 : o.pad;
    var a = o.a == null ? 0.22 : Math.min(0.45, o.a), c = o.rgb || "22,24,30";
    if (bottom != null && a > 0) {
      var fade = o.fade || 180, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + (a * 0.8) + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + a + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  /* KNOCK THE EDGE OUT BEHIND A LINE OF TYPE, without removing its light. */
  N.soften = function (cx, selectors, o) {
    o = o || {};
    var blur = o.blur || 12, pad = o.pad == null ? 18 : o.pad, feather = o.feather || 70;
    var art = document.getElementById("art");
    var src = document.createElement("canvas"); src.width = art.width; src.height = art.height;
    var sx = src.getContext("2d"); sx.filter = "blur(" + (blur * 2) + "px)"; sx.drawImage(art, 0, 0);
    var mask = document.createElement("canvas"); mask.width = art.width; mask.height = art.height;
    var mx = mask.getContext("2d"); mx.filter = "blur(" + feather + "px)"; mx.fillStyle = "#000";
    (selectors || []).forEach(function (sel) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
        var r = el.getBoundingClientRect();
        mx.fillRect((r.left - pad) * 2, (r.top - pad) * 2, (r.width + 2 * pad) * 2, (r.height + 2 * pad) * 2);
      });
    });
    sx.filter = "none"; sx.globalCompositeOperation = "destination-in"; sx.drawImage(mask, 0, 0);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.drawImage(src, 0, 0); cx.restore();
  };
  /* THE POST STEPS every frame takes before its grade. The frame still calls TXDECK.finish itself,
   * last. A dark band under the footer, never a box and never over 0.45. */
  N.post = function (cx, o) {
    o = o || {};
    N.atmosphere(cx, { a: o.a == null ? 0.2 : o.a, to: o.to, fade: o.fade, rgb: o.rgb, pad: o.pad });
    N.soften(cx, o.type || [".kick", ".hook", ".dek"], { blur: o.typeBlur || 8, pad: 8, feather: o.typeFeather || 26 });
    N.soften(cx, [".tx-site", ".src"], { blur: o.siteBlur || 9, pad: 14, feather: 40 });
    var y0 = N.H - (o.veilH || 220), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(14,14,18," + (Math.min(0.45, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 1.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };

  /* THE SHELL EVERY FRAME SHARES: the type styles, the furniture, the fit of the hook. */
  N.CSS = [
    "* { margin:0; padding:0; box-sizing:border-box; }",
    "html, body { width:1080px; height:1350px; overflow:hidden; background:#1C2027; }",
    'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
    "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
    '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:800; line-height:0.98; letter-spacing:-0.01em; color:#F7F3EC; font-variation-settings:"opsz" 144; z-index:10; }',
    ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:#EEE9E1; z-index:10; }",
    '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:#E8E3DA; white-space:nowrap; z-index:20; }',
    '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; color:#E8E3DA; white-space:nowrap; z-index:12; }',
    ".hook, .dek, .tx-site, .kick, .src, .cap, .lab { text-shadow:0 0 2px rgba(10,12,16,0.55), 0 1px 12px rgba(10,12,16,0.45); }"
  ].join("\n");
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS;
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#E8E3DA" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 96, max: 128, maxLines: 2 });
    N.follow();
  };
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE;
    await document.fonts.ready;
    N.start(o);
    var TXT = typeof bench === "function" ? bench(THREE) : bench, K = initKit(THREE, TXT);
    N.installKit(K, THREE, TXT);
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
  };
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    return TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 30, near: o.near || 0.05, far: o.far || 12000 });
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

  global.NR = N;
})(this);
