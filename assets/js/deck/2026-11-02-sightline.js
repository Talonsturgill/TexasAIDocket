/* deck/2026-11-02-sightline.js — the chassis for the 2026-11-02 deck: San Antonio's automated count of
 * unrestrained dogs, a phone on a car window running object detection, and the human review behind it
 * (tx-2026-0236).
 *
 * THE VISUAL ARGUMENT. Sight line. The deck is built from where the survey's camera sits: a phone clipped to a
 * car window on a San Antonio street at last light. A thin dusk gold box of four corners is what the machine
 * draws around a dog, and each corner is one of the review's four checks. The box changes state across the deck
 * and leaves it at frame 6, where the record takes over in caliche on black clay: the 32 study areas, the same
 * places as 2019, and the field window, all as measured reliefs.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky, one warm seam low in the west, the
 * dog in a pool of light and the street behind it gone dark.
 *
 * THE LIGHT is azimuth -58, elevation 12. +x is east and +z is south. A camera looking north (-z) has the key on
 * its LEFT, every lit edge is on the left, and every cast runs long to the right. TXBENCH reliefs read the same
 * declaration: raked from the upper left, casting to the lower right.
 *
 * THE BLOCK. One street, built from N.BLOCK's fixed coordinates by every street frame: the road along x centred on
 * z = 0, the north kerb, the parkway, the sidewalk, a chain link fence, a limestone ranch house, a driveway, a live
 * oak and a streetlight. The survey car drives east in the south lane with the phone on its north (left rear) window, so the
 * lens looks north across the road to the parkway. Every frame stands somewhere on this one street.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having neither: `street_dog` (one smooth signed distance body meshed by
 * K.sdfMesh, angulated, with fur normals and a sheen) and `window_phone` (a handset in a clamp over the top edge of a
 * car's door glass). Drawn to illustrate, to no breed and no maker's design, in the kit's conventions (metres, y up,
 * origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is dusk_gold, #E0956A, and it means ONE thing: the machine's detection. The box around a dog, the sight
 * lines from the lens, the box on the reviewer's screen, and the chamfer of the 2026 plugs.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the block, the models and the way type
 * is seated. Every frame composes its own picture, and every count a frame draws is read from figures.json in that
 * frame's own code. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("sightline.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "sightline",
    light: { az: -58, el: 12 },
    sky: "lastLight",
    ground: "#09080C",
    material: "#E3DCCD",
    accent: "#E0956A",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.07, filmic: true,
      lift: [0.002, 0.003, 0.005], gain: [1.0, 1.0, 1.0], vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.12, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261102 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080; N.H = 1350; N.SEED = 20261102; N.INK = "#ECE8DF";
  N.GOLD = "#E0956A";   /* dusk_gold, brand.yaml's token: the machine's detection and nothing else */
  /* THE BLOCK, in metres. The kit road (2 lanes, parkway 1.2, sidewalk 1.5) puts the north kerb face at z -4.28,
   * the parkway from -4.36 to -5.56 and the sidewalk from -5.56 to -7.06. */
  N.BLOCK = {
    roadLen: 120, parkway: [-4.36, -5.56], sidewalk: [-5.56, -7.06], fenceZ: -8.2,
    house: [0, -19.5], driveX: 7.5, oak: [-8.5, -12], light: [-5.6, -5.0],
    car: [0, 1.8], lensY: 1.15, lensZ: 0.66, across: -19.5
  };
  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* FUR: a normal map of short strokes running along one axis, so a key raking the body draws a coat
   * rather than a plastic sheen. The strokes run along u, which the dog's geometry lays nose to tail. */
  function furTex(THREE, seed, base, dark, n) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = base; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < n; i++) {
      var px = r() * 256, py = r() * 256, L = 3 + r() * 7, a = 0.08 + r() * 0.22, d = r() < 0.5;
      x.strokeStyle = d ? "rgba(" + dark + "," + a + ")" : "rgba(255,246,230," + a * 0.6 + ")";
      x.lineWidth = 0.6 + r() * 0.8; x.beginPath(); x.moveTo(px, py); x.lineTo(px + L, py + (r() - 0.5) * 1.6); x.stroke();
    }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  function bumpTex(THREE, seed, n) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "rgb(128,128,128)"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < n; i++) { var v = Math.floor(70 + r() * 120), px = r() * 256, py = r() * 256, L = 2 + r() * 6;
      x.strokeStyle = "rgb(" + v + "," + v + "," + v + ")"; x.lineWidth = 0.7 + r(); x.beginPath(); x.moveTo(px, py); x.lineTo(px + L, py + (r() - 0.5)); x.stroke(); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  N.coat = function (THREE, key, base, dark, sheenK) {
    N._coats = N._coats || {};
    if (N._coats[key]) return N._coats[key];
    var map = furTex(THREE, key.length * 97 + 5, base, dark, 9000); map.repeat.set(6, 6);
    var bump = bumpTex(THREE, key.length * 31 + 7, 9000); bump.repeat.set(7, 7);
    N._coats[key] = new THREE.MeshPhysicalMaterial({ map: map, bumpMap: bump, bumpScale: 0.7, roughness: 0.88, metalness: 0, sheen: sheenK == null ? 0.55 : sheenK, sheenRoughness: 0.5, sheenColor: new THREE.Color(0xffe2bf) });
    return N._coats[key];
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.street_dog) return;
    function shade(o) { o.traverse(function (c) { if (c.isMesh) { c.castShadow = c.receiveShadow = true; } }); return o; }
    var V = function (x, y, z) { return new THREE.Vector3(x, y, z); };
    /* A smooth limb or trunk: a tube along a curve whose radius follows a profile, capped round at both ends. */
    function limb(pts, radii, mat, seg) {
      var curve = new THREE.CatmullRomCurve3(pts.map(function (p) { return V(p[0], p[1], p[2]); }));
      var n = seg || 24, rs = 12, geo = new THREE.TubeGeometry(curve, n, 1, rs, false);
      var pos = geo.attributes.position, tmp = new THREE.Vector3();
      for (var i = 0; i <= n; i++) {
        var t = i / n, rr = sampleR(radii, t), c = curve.getPointAt(t);
        for (var j = 0; j <= rs; j++) { var k = i * (rs + 1) + j; tmp.fromBufferAttribute(pos, k).sub(c).multiplyScalar(rr).add(c); pos.setXYZ(k, tmp.x, tmp.y, tmp.z); }
      }
      geo.computeVertexNormals();
      var g = new THREE.Group(); g.add(new THREE.Mesh(geo, mat));
      [0, 1].forEach(function (e) { var s = new THREE.Mesh(new THREE.SphereGeometry(sampleR(radii, e), 16, 12), mat); s.position.copy(curve.getPointAt(e)); g.add(s); });
      return g;
    }
    function sampleR(r, t) { var f = t * (r.length - 1), i = Math.min(r.length - 2, Math.floor(f)), u = f - i; return r[i] * (1 - u) + r[i + 1] * u; }

    /* A STREET DOG, true scale (shoulder 0.52 m at the default), drawn to illustrate and to no breed. Front on +z.
     * ONE SMOOTH BODY: ribcage, loin, pelvis, neck, skull, muzzle and four angulated legs are blended into one
     * signed distance field with a smooth minimum and meshed by K.sdfMesh, the way the kit's cattle are, so there
     * is no seam where a limb meets the trunk. The hock is the tell that keeps it from reading as a toy.
     * build 'lean' tucks the belly up, narrows the waist and shows the ribs as shallow grooves; 'full' a deeper
     * barrel. pose 'wary' drops the head below the topline, lays the ears back and tucks the tail; 'easy' carries
     * the head up and the tail raised; 'step' is easy with the near forepaw lifted. coat tan|black|brindle|cream. */
    function sdRC(px, py, pz, a, b, r1, r2) {
      var bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2], l2 = bx * bx + by * by + bz * bz, rr = r1 - r2, a2 = l2 - rr * rr, il2 = 1 / l2;
      var ax = px - a[0], ay = py - a[1], az = pz - a[2], y = ax * bx + ay * by + az * bz, z = y - l2;
      var xx = ax * l2 - bx * y, xy = ay * l2 - by * y, xz = az * l2 - bz * y, x2 = xx * xx + xy * xy + xz * xz, y2 = y * y * l2, z2 = z * z * l2;
      var k = Math.sign(rr) * rr * rr * x2;
      if (Math.sign(z) * a2 * z2 > k) return Math.sqrt(x2 + z2) * il2 - r2;
      if (Math.sign(y) * a2 * y2 < k) return Math.sqrt(x2 + y2) * il2 - r1;
      return (Math.sqrt(x2 * a2 * il2) + y * rr) * il2 - r1;
    }
    function sdE(px, py, pz, c, r) {
      var x = (px - c[0]) / r[0], y = (py - c[1]) / r[1], z = (pz - c[2]) / r[2], k0 = Math.sqrt(x * x + y * y + z * z);
      var x2 = x / r[0], y2 = y / r[1], z2 = z / r[2], k1 = Math.sqrt(x2 * x2 + y2 * y2 + z2 * z2);
      return k1 < 1e-9 ? -Math.min(r[0], r[1], r[2]) : k0 * (k0 - 1) / k1;
    }
    function smin(a, b, k) { var h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; }
    N.dogField = function (o) {
      var lean = o.build === "lean", wary = o.pose === "wary", step = o.pose === "step";
      var P = [];   /* primitives: ['e', c, r] or ['c', a, b, r1, r2] */
      var E = function (c, r) { P.push(["e", c, r]); }, Cn = function (a2, b2, r1, r2) { P.push(["c", a2, b2, r1, r2]); };
      /* the trunk */
      E([0, 0.40, 0.12], lean ? [0.086, 0.12, 0.19] : [0.116, 0.142, 0.205]);
      Cn([0, lean ? 0.44 : 0.415, 0.0], [0, 0.44, -0.16], lean ? 0.058 : 0.1, lean ? 0.068 : 0.092);
      E([0, 0.435, -0.19], lean ? [0.072, 0.086, 0.1] : [0.094, 0.1, 0.115]);
      /* neck and head */
      var hy = wary ? 0.39 : 0.64, hz = wary ? 0.44 : 0.38;
      Cn([0, 0.46, 0.22], [0, hy - 0.025, hz - 0.035], lean ? 0.068 : 0.078, 0.052);
      E([0, hy, hz], [0.056, 0.058, 0.068]);
      E([0, hy - 0.02, hz + 0.03], [0.05, 0.04, 0.05]);
      var my = wary ? -0.03 : -0.018;
      Cn([0, hy - 0.012, hz + 0.035], [0, hy + my, hz + 0.135], 0.038, 0.022);
      Cn([0, hy - 0.035, hz + 0.03], [0, hy + my - 0.022, hz + 0.115], 0.026, 0.014);
      /* ears: thick round cones blended into the skull, pricked on an easy dog and laid back on a wary one */
      var ears = [];
      [-1, 1].forEach(function (k) {
        var base = [k * 0.036, hy + 0.04, hz - 0.015];
        var tip = wary ? [k * 0.062, hy + 0.055, hz - 0.1] : [k * 0.052, hy + 0.115, hz - 0.03];
        Cn(base, tip, 0.024, 0.006);
        ears.push([base, tip, k]);
      });
      /* forelegs: shoulder to elbow tucked back, a straight forearm, the pastern sloping forward to the paw */
      [-1, 1].forEach(function (k) {
        var fx = k * 0.062, lift = step && k > 0;
        var el = [fx, 0.29, 0.13], wr = lift ? [fx, 0.17, 0.26] : [fx * 0.95, 0.075, 0.155], pw = lift ? [fx, 0.14, 0.3] : [fx * 0.95, 0.024, 0.18];
        Cn([fx, 0.42, 0.17], el, 0.05, 0.036);
        Cn(el, wr, 0.03, 0.019);
        Cn(wr, pw, 0.018, 0.02);
        var pc = lift ? [fx, 0.13, 0.31] : [fx * 0.95, 0.018, 0.19]; E(pc, [0.022, 0.016, 0.028]); [-1.5, -0.5, 0.5, 1.5].forEach(function (t) { E([pc[0] + t * 0.0105, pc[1] - 0.002, pc[2] + 0.022 - Math.abs(t) * 0.004], [0.0075, 0.009, 0.01]); });
        /* hind legs: the thigh's muscle, the stifle forward, the gaskin down and back to the hock, then the
         * hock to the paw nearly upright. A wary dog crouches: the stifle bends further. */
        var hx = k * 0.07, cr = wary ? 0.03 : 0;
        E([hx, 0.36 - cr * 0.5, -0.16], [0.048, 0.088, 0.078]);
        var st = [hx, 0.25 - cr, -0.1 + cr], hk = [hx * 0.95, 0.12 - cr * 0.3, -0.25], hp = [hx * 0.95, 0.024, -0.225];
        Cn([hx, 0.36 - cr * 0.5, -0.15], st, 0.05, 0.035);
        Cn(st, hk, 0.03, 0.02);
        Cn(hk, hp, 0.019, 0.019);
        E([hx * 0.95, 0.018, -0.21], [0.021, 0.016, 0.026]); [-1.5, -0.5, 0.5, 1.5].forEach(function (t) { E([hx * 0.95 + t * 0.0100, 0.016, -0.19 - Math.abs(t) * 0.004], [0.0072, 0.009, 0.0095]); });
      });
      /* tail */
      var T = wary ? [[0, 0.43, -0.29], [0, 0.35, -0.315], [0, 0.26, -0.29], [0, 0.19, -0.24], [0, 0.15, -0.19]] : [[0, 0.46, -0.28], [0, 0.54, -0.345], [0, 0.62, -0.365], [0, 0.69, -0.345], [0, 0.73, -0.31]];
      var TR = [0.03, 0.024, 0.017, 0.011, 0.004];
      /* one smooth curve through the tail's points, cut into many short cones whose radii taper evenly, so no step shows */
      var tc = new THREE.CatmullRomCurve3(T.map(function (q) { return new THREE.Vector3(q[0], q[1], q[2]); })), NS = 14;
      for (var i = 0; i < NS; i++) {
        var a0 = tc.getPointAt(i / NS), a1 = tc.getPointAt((i + 1) / NS);
        Cn([a0.x, a0.y, a0.z], [a1.x, a1.y, a1.z], 0.03 - 0.026 * (i / NS), 0.03 - 0.026 * ((i + 1) / NS));
      }
      var K2 = 0.028;
      var f = function (x, y, z) {
        var d = 1e9;
        for (var j = 0; j < P.length; j++) {
          var q = P[j], dj = q[0] === "e" ? sdE(x, y, z, q[1], q[2]) : sdRC(x, y, z, q[1], q[2], q[3], q[4]);
          d = j === 0 ? dj : smin(d, dj, K2);
        }
        /* a lean dog's ribs: shallow grooves across the barrel's flanks, never sores or bone */
        /* the inner cup of each ear, carved from the face side; eye sockets carved where the eyes sit */
        for (var e = 0; e < ears.length; e++) {
          var E2 = ears[e], cxp = [E2[0][0] * 0.8 + E2[1][0] * 0.2 + E2[2] * -0.004, E2[0][1] * 0.45 + E2[1][1] * 0.55, E2[0][2] * 0.45 + E2[1][2] * 0.55 + 0.012];
          var cup = sdE(x, y, z, cxp, [0.011, 0.03, 0.009]);
          d = Math.max(d, -cup + 0.0005 * 0);
        }
        [-1, 1].forEach(function (k) { var so = sdE(x, y, z, [k * 0.034, hy + 0.018, hz + 0.058], [0.013, 0.009, 0.01]); d = Math.max(d, -so); });
        if (lean && z > -0.02 && z < 0.24 && y > 0.3 && y < 0.5 && Math.abs(x) > 0.05) {
          var g = Math.cos((z - 0.02) / 0.034 * Math.PI * 2);
          d += 0.0006 * Math.max(0, g);
        }
        return d;
      };
      return { f: f, head: [0, hy, hz], muzzle: [0, hy + my, hz + 0.135], tail: T };
    };
    N.dogUV = { region: function () { return 0; }, uv: function (x, y, z, r, t) { t[0] = z * 2.2; t[1] = y * 2.2 + x * 1.1; t[2] = 0; } };
    /* A PHONE ON A CAR WINDOW: a handset (71.5 x 146.7 x 8.3 mm) in a spring cradle with rubber jaws, on a short arm
     * to a hooked clamp whose padded U sits over the top edge of the door glass. Origin at the glass edge, the
     * glass in the x y plane; the camera island faces +z (out of the car). userData.lens is the lens centre. */
    K.define("window_phone", {
      size: [0.09, 0.2, 0.05],
      options: { landscape: false, glass: 0.005 },
      note: "A smartphone in a clamp mount over the top edge of a car window. Origin on the glass edge, lens facing +z. userData.lens.",
      make: function (o) {
        var g = new THREE.Group();
        var alu = new THREE.MeshPhysicalMaterial({ color: 0x8e9196, metalness: 0.85, roughness: 0.32, clearcoat: 0.3 });
        var back = new THREE.MeshPhysicalMaterial({ color: 0x1b1d21, metalness: 0.1, roughness: 0.28, clearcoat: 0.9, clearcoatRoughness: 0.1 });
        var rubber = new THREE.MeshStandardMaterial({ color: 0x111112, roughness: 0.85 });
        var lensG = new THREE.MeshPhysicalMaterial({ color: 0x05060a, metalness: 0.2, roughness: 0.05, clearcoat: 1, clearcoatRoughness: 0.02 });
        var chrome = new THREE.MeshPhysicalMaterial({ color: 0xd8dadd, metalness: 1, roughness: 0.18 });
        var w = 0.0715, h = 0.1467, t = 0.0083, gt = o.glass || 0.005;
        /* clamp: a U over the glass edge */
        var cl = TXT.roundedBox(0.03, 0.012, gt + 0.012, 0.003, rubber); cl.position.set(0, 0.006, 0); g.add(cl);
        [-1, 1].forEach(function (k) { var j = TXT.roundedBox(0.028, 0.04, 0.005, 0.002, rubber); j.position.set(0, -0.016, k * (gt / 2 + 0.0035)); g.add(j); });
        /* arm and ball */
        var arm = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.007, 0.05, 18), alu); arm.position.set(0, 0.035, 0.008); g.add(arm);
        var ball = new THREE.Mesh(new THREE.SphereGeometry(0.009, 18, 14), alu); ball.position.set(0, 0.062, 0.012); g.add(ball);
        /* cradle and jaws */
        var py = 0.062 + h / 2 - 0.02, pz = 0.022;
        var cr = TXT.roundedBox(w * 0.6, 0.02, 0.012, 0.004, rubber); cr.position.set(0, 0.065, pz - 0.006); g.add(cr);
        [-1, 1].forEach(function (k) { var jw = TXT.roundedBox(0.008, 0.045, 0.016, 0.003, rubber); jw.position.set(k * (w / 2 + 0.003), py, pz - 0.002); g.add(jw); });
        /* the handset: aluminium band, glass back with the camera island facing out */
        var band = TXT.roundedBox(w, h, t, 0.008, alu); band.position.set(0, py, pz); g.add(band);
        var bk = TXT.roundedBox(w - 0.002, h - 0.002, 0.001, 0.008, back); bk.position.set(0, py, pz + t / 2); g.add(bk);
        var isl = TXT.roundedBox(0.036, 0.036, 0.0025, 0.007, back); isl.position.set(-w / 2 + 0.024, py + h / 2 - 0.024, pz + t / 2 + 0.0015); g.add(isl);
        var lens = [];
        [[-0.008, 0.008], [-0.008, -0.008], [0.008, 0]].forEach(function (q, i) {
          var cx = -w / 2 + 0.024 + q[0], cy = py + h / 2 - 0.024 + q[1], r = i === 2 ? 0.0045 : 0.0062;
          var ring = new THREE.Mesh(new THREE.CylinderGeometry(r + 0.0012, r + 0.0012, 0.0016, 28), chrome); ring.rotation.x = Math.PI / 2; ring.position.set(cx, cy, pz + t / 2 + 0.0035); g.add(ring);
          var gl = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 0.0018, 28), lensG); gl.rotation.x = Math.PI / 2; gl.position.set(cx, cy, pz + t / 2 + 0.0038); g.add(gl);
          lens.push([cx, cy, pz + t / 2 + 0.004]);
        });
        g.userData.lens = lens[0];
        g.userData.keepOrigin = true;
        return shade(g);
      }
    });
    K.define("street_dog", {
      size: [0.3, 0.75, 1.0],
      options: { build: "full", pose: "easy", coat: "tan", shoulder: 0.52, detail: 0.008, seed: 1 },
      note: "A medium street dog at true scale, to no breed, one smooth SDF body. build lean|full, pose wary|easy|step, coat tan|black|brindle|cream, shoulder m, detail mesh cell m.",
      make: function (o) {
        var coats = { tan: ["#a07a4f", "46,26,12", 0.55], black: ["#1c1918", "4,3,3", 0.18], brown: ["#6a4a30", "22,14,8", 0.42], brindle: ["#6b5038", "24,16,10", 0.4], cream: ["#cdb898", "70,50,30", 0.55] };
        var cc = coats[o.coat] || coats.tan, mat = N.coat(THREE, "dog_" + o.coat, cc[0], cc[1], cc[2]);
        var dark = new THREE.MeshPhysicalMaterial({ color: 0x0b0908, roughness: 0.25, clearcoat: 0.8 });
        var F = N.dogField(o), g = new THREE.Group();
        var geo = K.sdfMesh(F.f, [-0.14, 0, -0.42, 0.14, 0.8, 0.64], o.detail || 0.008, N.dogUV);
        g.add(new THREE.Mesh(geo, mat));
        var hy = F.head[1], hz = F.head[2], wary = o.pose === "wary";
        var nose = new THREE.Mesh(new THREE.SphereGeometry(0.017, 18, 14), dark); nose.scale.set(1.3, 0.9, 0.85); nose.position.set(0, F.muzzle[1] + 0.006, F.muzzle[2] + 0.016); g.add(nose);
        var iris = new THREE.MeshPhysicalMaterial({ color: 0x2a1a0e, roughness: 0.15, clearcoat: 1, clearcoatRoughness: 0.05 });
        [-1, 1].forEach(function (k) {
          var eye = new THREE.Mesh(new THREE.SphereGeometry(0.0085, 14, 10), iris); eye.scale.set(1.2, 0.75, 0.8); eye.position.set(k * 0.033, hy + 0.018, hz + 0.054); g.add(eye);
        });
        g.scale.setScalar((o.shoulder || 0.52) / 0.52);
        return shade(g);
      }
    });
  };

  /* ---- the frame plumbing (house furniture, no picture) ------------------------------------ */
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
    var rim = Object.assign({}, W.rig.rim, { i: (W.rig.rim.i || 0.8) * 0.45 });
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { shadowSize: size || 12, mapSize: map || 2048 }) });
  };
  N.rigOpts = function (target, o) { o = o || {}; return { target: target, distance: o.distance || 40, shadowFar: o.shadowFar || 120, normalBias: o.normalBias == null ? 0.02 : o.normalBias }; };
  N.unacne = function (R, nb) { R.scene.traverse(function (l) { if (l.isDirectionalLight && l.castShadow) { l.shadow.normalBias = nb == null ? 0.04 : nb; l.shadow.bias = -0.0004; } }); return R; };
  N.BOUNCE = 0.6;
  N.warm = function (R, k) {
    R.scene.environmentIntensity = k == null ? 0.3 : k;
    if (!R._bounce) { R._bounce = new N.T.HemisphereLight(0x161a24, 0x4a4743, N.BOUNCE); R.scene.add(R._bounce); }
    return R;
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#D6D0C4", halo = "rgba(4,3,8,0.6)", halo2 = "rgba(4,3,8,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#07070C; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; color:' + ink + '; font-variation-settings:"opsz" 144; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".hook, .dek, .lab, .kick, .count, .src { font-feature-settings:\"calt\" 0; }",
      ".hook, .dek, .kick, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }",
      ".tx-site, .src { text-shadow:0 0 2px " + halo + ", 0 1px 4px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS(); document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D6D0C4" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 80, max: 104, maxLines: 2 });
    N.follow();
  };
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
    N.R = TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * N.EXPOSURE * (o.exposure || 1), tone: W.tone, fov: o.fov || 32, near: o.near || 0.02, far: o.far || 8000 });
    return N.R;
  };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) { d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px"; });
  };
  N.glCanvas = function () { var c = document.createElement("canvas"); c.width = N.W * 2; c.height = N.H * 2; return c; };
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
  /* THE DARK BAND THE TYPE STANDS IN. Light type on the dark field, and the band only ever DARKENS. */
  N.shade = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 60 : o.pad;
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "6,5,10";
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
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(6,5,10," + (Math.min(0.5, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
  };
  /* THE DETECTION BOX: four gold corner marks around a screen rect, drawn as SVG over the art. The corner count is
   * the frame's own figure, passed in; the chassis draws what it is handed. Returns the svg. */
  N.svg = function () {
    var s = document.getElementById("over");
    if (!s) { s = document.createElementNS("http://www.w3.org/2000/svg", "svg"); s.id = "over"; s.setAttribute("width", N.W); s.setAttribute("height", N.H);
      s.setAttribute("style", "position:absolute;left:0;top:0;z-index:8;pointer-events:none"); document.body.appendChild(s); }
    return s;
  };
  N.box = function (rect, corners, o) {
    o = o || {}; var s = N.svg(), x = rect[0], y = rect[1], w = rect[2], h = rect[3], L = o.arm || Math.min(w, h) * 0.22, sw = o.width || 3.5;
    var pts = [[x, y, 1, 1], [x + w, y, -1, 1], [x + w, y + h, -1, -1], [x, y + h, 1, -1]].slice(0, corners);
    pts.forEach(function (q) {
      var d = "M" + (q[0] + q[2] * L) + " " + q[1] + " L" + q[0] + " " + q[1] + " L" + q[0] + " " + (q[1] + q[3] * L);
      [["#07070C", sw + 3, 0.55], [N.GOLD, sw, 1]].forEach(function (st) {
        var p = document.createElementNS("http://www.w3.org/2000/svg", "path"); p.setAttribute("d", d); p.setAttribute("fill", "none");
        p.setAttribute("stroke", st[0]); p.setAttribute("stroke-width", st[1]); p.setAttribute("stroke-opacity", st[2]); p.setAttribute("stroke-linecap", "square"); s.appendChild(p);
      });
    });
    return pts;
  };
  /* the screen rect of an object's world bounding box, with a margin in px */
  N.rectOf = function (THREE, R, obj, m) {
    obj.updateMatrixWorld(true); var bb = new THREE.Box3().setFromObject(obj), xs = [], ys = [];
    [bb.min.x, bb.max.x].forEach(function (x) { [bb.min.y, bb.max.y].forEach(function (y) { [bb.min.z, bb.max.z].forEach(function (z) { var q = N.project(THREE, R, [x, y, z]); xs.push(q[0]); ys.push(q[1]); }); }); });
    m = m == null ? 18 : m;
    var x0 = Math.min.apply(null, xs) - m, y0 = Math.min.apply(null, ys) - m, x1 = Math.max.apply(null, xs) + m, y1 = Math.max.apply(null, ys) + m;
    return [x0, y0, x1 - x0, y1 - y0];
  };
  /* THE BLOCK'S STANDING THINGS, at N.BLOCK's coordinates; a frame asks for what it shows. */
  N.street = function (K, TXT, R, want) {
    var B = N.BLOCK, out = {};
    if (want.road) { var rd = K.make("road", { length: B.roadLen, lanes: 2, sidewalk: true, parkway: 1.2 }); TXT.add(R, rd); out.road = rd; }
    if (want.parkway) { var y = K.make("yard", { size: [B.roadLen, 1.18], dryness: 0.78, edge: true }); y.position.set(0, 0.2, (B.parkway[0] + B.parkway[1]) / 2); TXT.add(R, y); out.parkway = y; }
    if (want.fence) { var f = K.make("chain_link_fence", { length: want.fenceLen || 40, height: 1.22, color: "galvanized" }); f.position.set(want.fenceX || 0, 0.2, B.fenceZ); TXT.add(R, f); TXT.contact(R, f); out.fence = f; }
    if (want.yard) { var yd = K.make("yard", { size: [want.fenceLen || 40, 10], dryness: 0.7 }); yd.position.set(want.fenceX || 0, 0.2, B.fenceZ - 5.2); TXT.add(R, yd); out.yard = yd; }
    if (want.house) { var h = K.make("ranch_house", { material: "limestone", seed: 3, garage: "right", chimney: true }); h.position.set(B.house[0], 0.2, B.house[1]); TXT.add(R, h); TXT.contact(R, h); out.house = h; }
    if (want.oak) { var t = K.make("live_oak", { seed: 2 }); t.position.set(B.oak[0], 0.2, B.oak[1]); TXT.add(R, t); TXT.contact(R, t); out.oak = t; }
    if (want.light) { var l = K.make("streetlight", {}); l.position.set(B.light[0], 0.2, B.light[1]); TXT.add(R, l); out.light = l; }
    return out;
  };
  global.CH = N;
})(this);
