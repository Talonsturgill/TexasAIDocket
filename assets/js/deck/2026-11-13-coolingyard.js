/* deck/2026-11-13-coolingyard.js — the chassis for the 2026-11-13 deck: ERCOT's preliminary summary to the utility
 * commission of its data center state and community impact questionnaire (tx-2026-0072). 433 of 465 loads answered,
 * covering about 177 GW, and the largest share of unanswered questions was about cooling.
 *
 * THE VISUAL ARGUMENT. One West zone site at last light, drawn to illustrate and never a real place. The primer steel is
 * up, the power is staged as copper bus bar at one lamination per gigawatt, the cable trench is grated for the answered
 * share of its length, and the cooling pads beside the hall sit poured, bolted and empty inside an ember line. Every count
 * and length a frame draws is read from figures.json in that frame's own code. The chassis types no figure.
 *
 * THE WORLD. lastLight, STAGED. The sun is just down to the west. The key is azimuth -58, elevation 9: low on the LEFT, so
 * every lit face looks left and every cast runs long to the RIGHT. A cool rim from the back right edges the dark steel.
 * The yard is staged as one subject in a pool on caliche and the world behind it goes dark. TXBENCH reliefs read the same
 * declaration and are raked from the frame's left.
 *
 * THE ACCENT. dusk_ember #B4664F means ONE thing: LEFT BLANK. The layout line round an empty pad, the epoxy lining of the
 * trench's open stretch, the caps on an empty pad's conduit stubs. Copper is a material and never the accent.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them, in the kit's conventions (metres, y up, origin on the
 * ground at the footprint centre, front on +z) so Phase 17 can queue the lift: `equipment_pad` (a poured equipment pad
 * sized for the kit chiller, ember layout line, galvanized J bolts, capped conduit stubs), `bus_pack` (n copper
 * laminations on standoff insulators over oak dunnage), `cable_reel` (galvanized or timber flanged reel of black cable),
 * `cable_trench` (a precast cable trough on grade, grated for a share of its length, its open stretch lined in ember),
 * `plan_table` (plywood on two sawhorses) and `work_light` (a tripod LED work light).
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("coolingyard.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "coolingyard",
    light: { az: -58, el: 9 },
    sky: { preset: "lastLight", haze: 0x0b0d13 },
    ground: "#17150F",
    material: "#8E8A82",
    accent: "#B4664F",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.06, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.2,
      bloom: { threshold: 0.9, strength: 0.1, radius: 6 },
      grain: { amount: 0.014, size: 2, seed: 20261113 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261113; N.INK = "#EDE6D6";
  N.EMBER = 0xB4664F;     /* dusk_ember: left blank, and nothing else */
  N.PAD = { w: 14.5, d: 3.6, h: 0.25 };          /* an equipment pad sized for the kit chiller, 13.3 x 2.5 m */
  N.BAR = { t: 0.0127, sep: 0.001, face: 1.0, len: 6.0 };   /* one lamination per GW, a drawing scale; figures.json carries the widths */
  N.TRENCH = { w: 1.0, wall: 0.12, h: 0.42 };

  /* a seeded canvas texture, so every surface carries tooth in its albedo and never in its height */
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };

  /* bake a group's meshes into one InstancedMesh per mesh, so 245 reels cost a handful of draw calls */
  N.instanceGroup = function (THREE, proto, list) {
    var out = new THREE.Group(); proto.updateMatrixWorld(true);
    var m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), p = new THREE.Vector3();
    proto.traverse(function (mesh) {
      if (!mesh.isMesh) return;
      var geo = mesh.geometry.clone(); geo.applyMatrix4(mesh.matrixWorld);
      var im = new THREE.InstancedMesh(geo, mesh.material, list.length);
      list.forEach(function (e, i) { p.set(e[0], e[1], e[2]); q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), e[3] || 0); s.setScalar(e[4] || 1); m.compose(p, q, s); im.setMatrixAt(i, m); });
      im.castShadow = true; im.receiveShadow = true; im.instanceMatrix.needsUpdate = true; out.add(im);
    });
    return out;
  };

  /* A HOLE IN THE GROUND: the caliche discards its fragments over a rotated rectangle (centre, unit run direction,
   * half length and half width, in metres), so a trench sunk below grade shows through it flush at the surface. */
  N.cutGround = function (THREE, g, c, dir, hl, hw) {
    var m = g.material, prev = m.onBeforeCompile;
    m.onBeforeCompile = function (sh, r) {
      if (prev) prev(sh, r);
      sh.uniforms.uCut = { value: new THREE.Vector4(c[0], c[1], dir[0], dir[1]) };
      sh.uniforms.uCutH = { value: new THREE.Vector2(hl, hw) };
      sh.vertexShader = sh.vertexShader.replace("void main() {", "varying vec3 vTxCut;\nvoid main() {").replace("#include <project_vertex>", "#include <project_vertex>\nvTxCut = (modelMatrix * vec4(transformed, 1.0)).xyz;");
      sh.fragmentShader = sh.fragmentShader.replace("void main() {", "varying vec3 vTxCut;\nuniform vec4 uCut;\nuniform vec2 uCutH;\nvoid main() {\n  { vec2 d = vTxCut.xz - uCut.xy; float a = dot(d, uCut.zw); float b = dot(d, vec2(-uCut.w, uCut.z)); if (abs(a) < uCutH.x && abs(b) < uCutH.y) discard; }");
    };
    m.customProgramCacheKey = function () { return "txcut"; };
    m.needsUpdate = true;
  };

  /* A CAMERA BEARING FROM THE SUN: the horizontal direction `deg` degrees clockwise (to the right) of the sun's own
   * bearing, so a frame can put the warm seam at its left edge by looking a little right of the sun. */
  N.bearing = function (TXT, deg) {
    var sd = TXT.sunDir(), hx = sd.x, hz = sd.z, n = Math.hypot(hx, hz) || 1; hx /= n; hz /= n;
    var a = -deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
    return [hx * c - hz * s, hz * c + hx * s];
  };
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.equipment_pad) return;
    var R0 = N.rng(N.SEED);
    /* broom finished concrete: fine strokes across the pad in the albedo, blotches of cure and grime */
    var broom = N.canvasTex(THREE, 512, 512, function (g, w, h) {
      g.fillStyle = "#cfcdc8"; g.fillRect(0, 0, w, h); var r = N.rng(7);
      for (var i = 0; i < 2600; i++) { var y = r() * h, a = 0.03 + r() * 0.045; g.strokeStyle = r() < 0.5 ? "rgba(40,38,34," + a + ")" : "rgba(200,196,186," + a + ")"; g.lineWidth = 0.6 + r(); g.beginPath(); g.moveTo(r() * w, y); g.lineTo(r() * w, y + (r() - 0.5) * 3); g.stroke(); }
      for (var q = 0; q < 9000; q++) { g.fillStyle = r() < 0.5 ? "rgba(70,68,64,0.4)" : "rgba(240,238,232,0.35)"; g.fillRect(r() * w, r() * h, 0.6 + r() * 0.8, 0.6 + r() * 0.8); }
      
    }, [3, 1]);
    var CONC = new THREE.MeshStandardMaterial({ color: 0xbdbcb8, map: broom, roughness: 0.86, metalness: 0 });
    var CONCD = new THREE.MeshStandardMaterial({ color: 0x9a9995, map: broom, roughness: 0.9, metalness: 0 });
    var EMBER = new THREE.MeshStandardMaterial({ color: N.EMBER, roughness: 0.55, metalness: 0, emissive: N.EMBER, emissiveIntensity: 0.3 });
    var GALV = K.finish && K.finish.galvanized ? K.finish.galvanized() : new THREE.MeshStandardMaterial({ color: 0xa6abb0, roughness: 0.42, metalness: 0.9 });
    var PVC = new THREE.MeshStandardMaterial({ color: 0x5b5f63, roughness: 0.6, metalness: 0 });
    var mill = N.canvasTex(THREE, 256, 64, function (g, w, h) {
      g.fillStyle = "#b87350"; g.fillRect(0, 0, w, h); var r = N.rng(11);
      for (var i = 0; i < 500; i++) { g.fillStyle = r() < 0.5 ? "rgba(90,40,20,0.22)" : "rgba(240,190,150,0.2)"; g.fillRect(r() * w, r() * h, 6 + r() * 60, 0.6 + r()); }
    }, [3, 3]);
    var COPPER = new THREE.MeshStandardMaterial({ color: 0xc69a68, roughnessMap: mill, roughness: 0.36, metalness: 0.8 });   /* raw copper, its mill streaks in the roughness only */
    var COPPER2 = new THREE.MeshStandardMaterial({ color: 0xb08458, roughnessMap: mill, roughness: 0.4, metalness: 0.78 });   /* alternate laminations a shade duller, so the end face reads as many thin plates */
    var COPPERD = new THREE.MeshStandardMaterial({ color: 0x1e130e, roughness: 0.7, metalness: 0.2 });   /* the oxidised band every tenth bar, so the pack reads in tens */
    var EPOXY = new THREE.MeshStandardMaterial({ color: 0x6f747a, roughness: 0.5, metalness: 0 });
    var oakTex = N.canvasTex(THREE, 256, 64, function (g, w, h) {
      g.fillStyle = "#5c4630"; g.fillRect(0, 0, w, h); var r = N.rng(13);
      for (var i = 0; i < 90; i++) { g.strokeStyle = "rgba(30,20,12," + (0.1 + r() * 0.2) + ")"; g.lineWidth = 0.5 + r() * 1.5; var y = r() * h; g.beginPath(); g.moveTo(0, y); g.bezierCurveTo(w * 0.3, y + (r() - 0.5) * 6, w * 0.7, y + (r() - 0.5) * 6, w, y); g.stroke(); }
    });
    var OAK = new THREE.MeshStandardMaterial({ color: 0xa0886a, map: oakTex, roughness: 0.85, metalness: 0 });
    var pineTex = N.canvasTex(THREE, 256, 64, function (g, w, h) {
      g.fillStyle = "#a8824e"; g.fillRect(0, 0, w, h); var r = N.rng(17);
      for (var i = 0; i < 70; i++) { g.strokeStyle = "rgba(90,60,30," + (0.1 + r() * 0.25) + ")"; g.lineWidth = 0.6 + r() * 2; var y = r() * h; g.beginPath(); g.moveTo(0, y); g.lineTo(w, y + (r() - 0.5) * 4); g.stroke(); }
    });
    var PINE = new THREE.MeshStandardMaterial({ color: 0xc9a06a, map: pineTex, roughness: 0.8, metalness: 0 });
    var wraps = N.canvasTex(THREE, 64, 512, function (g, w, h) {
      g.fillStyle = "#121315"; g.fillRect(0, 0, w, h);
      for (var y = 0; y < h; y += 16) { var gr = g.createLinearGradient(0, y, 0, y + 16); gr.addColorStop(0, "#050506"); gr.addColorStop(0.45, "#2c2e33"); gr.addColorStop(1, "#050506"); g.fillStyle = gr; g.fillRect(0, y, w, 16); }
    });
    wraps.wrapS = wraps.wrapT = THREE.RepeatWrapping; wraps.repeat.set(1, 3);
    var CABLE = new THREE.MeshStandardMaterial({ color: 0xffffff, map: wraps, roughness: 0.55, metalness: 0 });
    var CABLEX = new THREE.MeshStandardMaterial({ color: 0x141518, roughness: 0.5, metalness: 0 });
    var gratingTex = N.canvasTex(THREE, 256, 256, function (g, w, h) {
      g.fillStyle = "#1b1c1e"; g.fillRect(0, 0, w, h);
      for (var x = 0; x < w; x += 16) { g.fillStyle = "#a9a49a"; g.fillRect(x, 0, 6, h); g.fillStyle = "#5e5a53"; g.fillRect(x + 5, 0, 1.5, h); }
      for (var y = 0; y < h; y += 64) { g.fillStyle = "#8d9297"; g.fillRect(0, y, w, 3); }
    });
    gratingTex.wrapS = gratingTex.wrapT = THREE.RepeatWrapping;

    function shadowAll(G) { G.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return G; }

    /* EQUIPMENT PAD: a poured pad for a cooling plant nobody has set. Ember layout line inset 0.25 m, J bolts in two rows at
     * the chiller's corners and along its length, conduit stubs capped in ember. Origin on the ground at the pad's centre. */
    K.define("equipment_pad", {
      size: [14.5, 0.55, 3.6],
      options: { w: 14.5, d: 3.6, h: 0.25, bolts: 6, stubs: 2, line: true, caps: true },
      note: "A poured equipment pad with nothing on it: broom finished concrete with a chamfer, an ember layout line, galvanized J bolts with nuts and washers, capped conduit stubs.",
      make: function (o) {
        var G = new THREE.Group(), w = o.w, d = o.d, h = o.h;
        var slab = TXT.roundedBox(w, h, d, 0.03, CONC); slab.position.set(0, h / 2, 0); G.add(slab);
        if (o.line) {
          var lw = 0.3, ins = 0.3, yy = h + 0.002;
          [[0, d / 2 - ins, w - 2 * ins, lw], [0, -d / 2 + ins, w - 2 * ins, lw], [w / 2 - ins, 0, lw, d - 2 * ins], [-w / 2 + ins, 0, lw, d - 2 * ins]].forEach(function (e) {
            var s = new THREE.Mesh(new THREE.BoxGeometry(e[2], 0.004, e[3]), EMBER); s.position.set(e[0], yy, e[1]); s.receiveShadow = true; G.add(s);
          });
        }
        /* saw-cut control joints across the slab every 2.4 m, the cut a pad actually carries */
        var JOINT = new THREE.MeshStandardMaterial({ color: 0x1a1816, roughness: 0.95 });
        for (var jx = -w / 2 + 2.4; jx < w / 2 - 1; jx += 2.4) { var jt = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.003, d - 0.06), JOINT); jt.position.set(jx, h + 0.0012, 0); jt.receiveShadow = true; G.add(jt); }
        var nb = o.bolts, bx0 = -w / 2 + 0.9, bx1 = w / 2 - 0.9;
        for (var i = 0; i < nb; i++) {
          var x = bx0 + (bx1 - bx0) * i / (nb - 1);
          [-1, 1].forEach(function (sz) {
            var z = sz * (d / 2 - 0.75);
            var rod = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.2, 12), GALV); rod.position.set(x, h + 0.1, z); G.add(rod);
            var nut = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.035, 6), GALV); nut.position.set(x, h + 0.04, z); G.add(nut);
            var wash = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.006, 16), GALV); wash.position.set(x, h + 0.0045, z); G.add(wash);
          });
        }
        for (var k = 0; k < o.stubs; k++) {
          var sx = -w / 2 + 2.2 + k * 0.32, sz = d / 2 - 1.4;
          var pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.22, 20), PVC); pipe.position.set(sx, h + 0.11, sz); G.add(pipe);
          if (o.caps) { var cap = new THREE.Mesh(new THREE.CylinderGeometry(0.052, 0.052, 0.05, 20), EMBER); cap.position.set(sx, h + 0.235, sz); G.add(cap); }
        }
        return shadowAll(G);
      }
    });

    /* BUS PACK: n copper laminations standing on edge, 12.7 mm thick with 1 mm separators, end faces on +z; every tenth bar
     * oxidised dark so the pack reads in tens; grey epoxy standoff insulators every 1.5 m on two oak dunnage beams. */
    K.define("bus_pack", {
      size: [2.43, 0.73, 6],
      options: { n: 10, face: 1.0, length: 6, every: 10 },
      note: "A pack of n copper bus laminations on edge on epoxy standoffs over oak dunnage; width n x 13.7 mm less one separator; every tenth bar darker.",
      make: function (o) {
        var G = new THREE.Group(), n = Math.max(1, Math.round(o.n)), pitch = N.BAR.t + N.BAR.sep, W = n * pitch - N.BAR.sep, L = o.length, F = o.face;
        var dunH = 0.15, insH = 0.12, y0 = dunH + insH;
        [-1, 1].forEach(function (s) { var d = TXT.roundedBox(W + 0.06, dunH, 0.15, 0.01, OAK); d.position.set(0, dunH / 2, s * L * 0.33); G.add(d); });
        var nIns = Math.max(2, Math.round(W / 0.35) + 1);
        [-1, 1].forEach(function (s) { for (var i = 0; i < nIns; i++) { var c = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.045, insH, 12), EPOXY); c.position.set(-W / 2 + W * (nIns === 1 ? 0.5 : i / (nIns - 1)), dunH + insH / 2, s * L * 0.33); G.add(c); } });
        var geo = new THREE.BoxGeometry(N.BAR.t, F, L), geoD = new THREE.BoxGeometry(N.BAR.t * 1.5, F, L + 0.002), lit = [], lit2 = [], dark = [];   /* the spacer every tenth bar drawn wider and 3 mm proud, so the tens read as bands at feed size */
        for (var b = 0; b < n; b++) { var x = -W / 2 + N.BAR.t / 2 + b * pitch; ((b + 1) % o.every === 0 ? dark : (b % 2 ? lit2 : lit)).push([x, y0 + F / 2, 0, 0, 1]); }
        /* the kit's bake collapses an InstancedMesh to its first instance, so the bars are separate meshes merged per material */
        function bars(list, mat, gg) { if (!list.length) return; var ms = list.map(function (e) { var m = new THREE.Mesh(gg || geo, mat); m.position.set(e[0], e[1], e[2]); m.updateMatrix(); return m; }); var mm = K.merge ? K.merge(ms, mat) : null; if (mm) G.add(mm); else ms.forEach(function (m) { G.add(m); }); }
        bars(lit, COPPER); bars(lit2, COPPER2); bars(dark, COPPERD, geoD);
        /* a bolted clamp across the pack near each end, tinned, so the pack reads as one assembly */
        [-1, 1].forEach(function (s) { var cl = TXT.roundedBox(W + 0.01, 0.03, 0.06, 0.006, GALV); cl.position.set(0, y0 + F + 0.015, s * (L / 2 - 0.4)); G.add(cl); var cl2 = cl.clone(); cl2.position.y = y0 - 0.015; G.add(cl2); });
        G.userData = { width: W, top: y0 + F, faceZ: L / 2 };
        return shadowAll(G);
      }
    });

    /* CABLE REEL: a flanged reel standing on edge, axis along x; galvanized flanges with eight radial ribs or pine flanges
     * with through bolts; wound black cable showing its wraps; an optional capped tail laid out along +z. */
    K.define("cable_reel", {
      size: [1.1, 1.6, 1.6],
      options: { flange: "steel", r: 0.8, width: 0.9, tail: 0, cap: false },
      note: "A cable reel on edge, axis along x: galvanized ribbed or pine flanges, a steel hub plate, wound black cable; tail metres of cable laid along +z with an optional ember cap.",
      make: function (o) {
        var G = new THREE.Group(), r = o.r, wd = o.width, t = 0.06, steel = o.flange !== "timber", FL = steel ? GALV : PINE;
        [-1, 1].forEach(function (s) {
          var f = new THREE.Mesh(new THREE.CylinderGeometry(r, r, t, 40), FL); f.rotation.z = Math.PI / 2; f.position.set(s * (wd / 2 + t / 2), r, 0); G.add(f);
          var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, t + 0.012, 20), GALV); hub.rotation.z = Math.PI / 2; hub.position.set(s * (wd / 2 + t / 2), r, 0); G.add(hub);
          if (steel) for (var k = 0; k < 8; k++) { var a = k * Math.PI / 4, rib = new THREE.Mesh(new THREE.BoxGeometry(0.02, r * 1.6, 0.04), GALV); rib.position.set(s * (wd / 2 + t + 0.01), r, 0); rib.rotation.x = a; G.add(rib); }
          else for (var k2 = 0; k2 < 8; k2++) { var a2 = k2 * Math.PI / 4, bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.02, 8), GALV); bolt.rotation.z = Math.PI / 2; bolt.position.set(s * (wd / 2 + t + 0.01), r + Math.cos(a2) * r * 0.55, Math.sin(a2) * r * 0.55); G.add(bolt); }
        });
        var wound = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.86, r * 0.86, wd, 40, 1, true), CABLE); wound.rotation.z = Math.PI / 2; wound.position.set(0, r, 0); G.add(wound);
        if (o.tail > 0) {
          var pts = [new THREE.Vector3(0, r * 1.6, 0.25), new THREE.Vector3(0.15, 0.4, r + 0.6), new THREE.Vector3(0.3, 0.07, r + 1.6), new THREE.Vector3(0.5, 0.06, r + o.tail)];
          var tube = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, 0.04, 12), CABLEX); G.add(tube);
          if (o.cap) { var cp = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.12, 16), EMBER); cp.rotation.x = Math.PI / 2; cp.position.set(0.5, 0.06, r + o.tail + 0.05); G.add(cp); }
        }
        return shadowAll(G);
      }
    });

    /* CABLE TRENCH: a precast cable trough on grade along x, curbs and walls in concrete, galvanized bar grating over the
     * first `covered` metres, the open stretch lined in ember epoxy. Origin at the trough's start, centred on its width. */
    K.define("cable_trench", {
      size: [24, 0.75, 2.16],
      options: { length: 24, covered: 20, width: 1.8, wall: 0.18, h: 0.75 },
      note: "A precast cable trough on grade, galvanized grating over the covered length, the open length lined in ember epoxy, starting at x = 0.",
      make: function (o) {
        var G = new THREE.Group(), L = o.length, c = Math.max(0, Math.min(L, o.covered)), w = o.width, t = o.wall, h = o.h;
        [-1, 1].forEach(function (s) { var wall = TXT.roundedBox(L, h, t, 0.015, CONCD); wall.position.set(L / 2, h / 2, s * (w / 2 + t / 2)); G.add(wall); });
        [0, L].forEach(function (ex) { var ew = TXT.roundedBox(t, h, w + 2 * t, 0.01, CONCD); ew.position.set(ex + (ex ? t / 2 : -t / 2), h / 2, 0); G.add(ew); });
        var floorC = new THREE.Mesh(new THREE.BoxGeometry(c, 0.06, w), CONCD); floorC.position.set(c / 2, 0.03, 0); G.add(floorC);
        if (L - c > 0) {
          var floorE = new THREE.Mesh(new THREE.BoxGeometry(L - c, 0.065, w), EMBER); floorE.position.set(c + (L - c) / 2, 0.033, 0); G.add(floorE);
          [-1, 1].forEach(function (s) { var lin = new THREE.Mesh(new THREE.BoxGeometry(L - c, h - 0.08, 0.008), EMBER); lin.position.set(c + (L - c) / 2, 0.065 + (h - 0.08) / 2, s * (w / 2 - 0.004)); G.add(lin); });
          var cab = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, L - c, 10), CABLEX); cab.rotation.z = Math.PI / 2; cab.position.set(c + (L - c) / 2, 0.11, -0.2); G.add(cab);
        }
        var panel = 1.0, np = Math.round(c / panel);
        for (var i = 0; i < np; i++) {
          var gt = gratingTex.clone(); gt.needsUpdate = true; gt.repeat.set(4, 1);
          var gm = new THREE.MeshStandardMaterial({ map: gt, roughness: 0.7, metalness: 0.4, color: 0xffffff });
          var g = new THREE.Mesh(new THREE.BoxGeometry(panel - 0.01, 0.03, w + 0.02), gm); g.position.set(i * panel + panel / 2, h - 0.015, 0); G.add(g);
        }
        G.userData = { length: L, covered: c };
        return shadowAll(G);
      }
    });

    /* PLAN TABLE: an 18 mm plywood top 2.4 x 0.9 m on two steel sawhorses, top at 0.95 m. */
    K.define("plan_table", {
      size: [2.4, 0.95, 0.9],
      options: {},
      note: "Plywood on two steel sawhorses, a site plan table.",
      make: function () {
        var G = new THREE.Group(), top = TXT.roundedBox(2.4, 0.018, 0.9, 0.004, PINE); top.position.set(0, 0.95, 0); G.add(top);
        [-0.85, 0.85].forEach(function (x) {
          var beam = TXT.roundedBox(0.06, 0.06, 0.8, 0.005, GALV); beam.position.set(x, 0.91, 0); G.add(beam);
          [-1, 1].forEach(function (s) { [-1, 1].forEach(function (u) { var leg = K.bar([x + s * 0.0, 0.9, u * 0.35], [x + s * 0.22, 0, u * 0.42], 0.016, GALV); if (leg) G.add(leg); }); });
        });
        return shadowAll(G);
      }
    });

    /* WORK LIGHT: a 1.8 m tripod with two LED heads; the frame adds the spot that the heads throw. */
    K.define("work_light", {
      size: [0.8, 1.9, 0.8],
      options: { lit: true },
      note: "A tripod LED work light, two heads on a T bar; emissive faces when lit.",
      make: function (o) {
        var G = new THREE.Group(), BLK = new THREE.MeshStandardMaterial({ color: 0x1a1b1d, roughness: 0.5, metalness: 0.5 });
        var LED = new THREE.MeshStandardMaterial({ color: 0xfff1d8, emissive: 0xfff1d8, emissiveIntensity: o.lit ? 7 : 0 });
        var mast = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.022, 1.7, 10), BLK); mast.position.set(0, 0.85, 0); G.add(mast);
        for (var k = 0; k < 3; k++) { var a = k * 2 * Math.PI / 3, leg = K.bar([0, 0.6, 0], [Math.cos(a) * 0.45, 0, Math.sin(a) * 0.45], 0.012, BLK); if (leg) G.add(leg); }
        var bar = TXT.roundedBox(0.7, 0.03, 0.03, 0.005, BLK); bar.position.set(0, 1.72, 0); G.add(bar);
        [-0.22, 0.22].forEach(function (x) { var hd = TXT.roundedBox(0.28, 0.2, 0.08, 0.01, BLK); hd.position.set(x, 1.82, 0.02); G.add(hd); var face = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.16, 0.005), LED); face.position.set(x, 1.82, 0.063); G.add(face); });
        return shadowAll(G);
      }
    });
  };

  N.dress = function (cx, o) { o = o || {}; N.post(cx, { a: 0.3, veil: 0.35, veilH: 240 }); N.footWash(cx, { a: o.foot || 0.6 }); N.typeDark(cx, { fade: o.fade == null ? 120 : o.fade, pad: o.pad, a: 0.6 }); return cx; };
  /* the deck's rig, read from the chassis declaration, with its acne bias */
  N.rig = function (TXT, R, W, size, target, o) { o = o || {}; TXT.deckRig(R, N.rigSpec(W, size, o.map || 2048), N.rigOpts(target, o)); return N.unacne(R, o.normalBias == null ? 0.02 : o.normalBias); };

  /* THE KEY'S POOL: the declared low key, concentrated where the subject stands. A spot with no falloff, hung on the key's
   * own bearing far enough out that its casts run parallel to the sun's, so it never reads as a second light. */
  N.pool = function (THREE, TXT, R, at, o) {
    o = o || {};
    var r = o.radius || 6, d = r * 7, sd = TXT.sunDir();
    var sp = new THREE.SpotLight(o.color || 0xffc890, o.i == null ? 3 : o.i, 0, Math.atan(r / d), o.penumbra == null ? 0.65 : o.penumbra, 0);
    sp.position.set(at[0] + sd.x * d, at[1] + sd.y * d + (o.lift || 0), at[2] + sd.z * d); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0005; sp.shadow.normalBias = o.normalBias == null ? 0.02 : o.normalBias;
    sp.shadow.camera.near = Math.max(0.1, d * 0.5); sp.shadow.camera.far = d * 1.6;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
  };

  /* THE HALL: one windowless machine hall with no ceiling, the flood hung high out of frame. A frame calls TXT.interior
   * itself with these options, because a room is the frame's own decision to stand somewhere. */
  N.roomOpts = function (o) {
    o = o || {};
    return { w: o.w || 16, d: o.d || 16, h: 4.2, floor: "concrete", wall: o.wall || 0x15171b, window: null, ceiling: false, light: o.light == null ? 0.08 : o.light };
  };
  /* the raised floor, placed so its walking surface is at FLOOR_H, with the hall's own floor as the slab under it */
  N.floor = function (TXT, R, K, o) {
    var f = K.make("raised_floor", o || {}); TXT.add(R, f); return f;
  };
  /* THE FLOOD ITSELF: a spot hung on the declared key's bearing, for a frame whose subject sits too low or too small for
   * the directional key to model it; it never comes from another side. */
  N.flood = function (THREE, R, from, at, o) {
    o = o || {};
    var sp = new THREE.SpotLight(o.color || 0xf0f3ff, o.i == null ? 40 : o.i, o.reach || 8, o.angle || 0.4, o.penumbra == null ? 0.55 : o.penumbra, 2);
    sp.position.set(from[0], from[1], from[2]); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0006; sp.shadow.normalBias = 0.01;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
  };
  /* THE HALL GOES COLD AND DARK: the studio environment lifts the walls to grey, so a frame calls this after the rig. */
  N.darkHall = function (R, o) {
    o = o || {};
    R.scene.environmentIntensity = o.env == null ? 0.08 : o.env;
    R.scene.traverse(function (l) { if (!l.isLight) return; if (l.isHemisphereLight || l.isAmbientLight) l.intensity *= (o.amb == null ? 0.35 : o.amb);
      else if (l.isDirectionalLight && !l.castShadow) l.intensity *= (o.fill == null ? 0.4 : o.fill); });   /* the preset's lavender fill lit the floor periwinkle; the hall keeps only a trace of it */
    return R;
  };

  /* THE TYPE BAND GOES TO THE DARK, darken only: a near black gradient from the top of the frame to just under the dek,
   * so the room's far edges behind the type sink rather than strike through it. */
  N.typeDark = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), b = dek ? dek.getBoundingClientRect() : { top: 400, height: 200 };
    var y1 = b.top + b.height + (o.pad == null ? 20 : o.pad), f = o.fade == null ? 90 : o.fade, a = o.a || 0.84;
    var g = cx.createLinearGradient(0, 0, 0, y1 + f); g.addColorStop(0, "rgba(4,5,8," + a + ")"); g.addColorStop(y1 / (y1 + f), "rgba(4,5,8," + (a * 0.9) + ")"); g.addColorStop(1, "rgba(4,5,8,0)");
    if (o.x1 == null) { cx.fillStyle = g; cx.fillRect(0, 0, N.W, y1 + f); return; }
    /* a column only, feathered on its right edge over `xf` px, so no seam is drawn down the frame */
    var c = document.createElement("canvas"); c.width = N.W * 2; c.height = N.H * 2; var k = c.getContext("2d"); k.scale(2, 2);
    k.fillStyle = g; k.fillRect(0, 0, N.W, y1 + f);
    var xf = o.xf || 220, m = k.createLinearGradient(o.x1 - xf, 0, o.x1, 0); m.addColorStop(0, "rgba(0,0,0,1)"); m.addColorStop(1, "rgba(0,0,0,0)");
    k.globalCompositeOperation = "destination-in"; k.fillStyle = m; k.fillRect(0, 0, N.W, N.H);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.drawImage(c, 0, 0); cx.restore();
  };

  /* a DOM label set beside a point in design px, so a leader's `at` and the label share one coordinate */
  N.pinLabel = function (id, at, off) { var el = document.getElementById(id); if (!el) return; el.style.left = Math.round(at[0] + (off ? off[0] : 0)) + "px"; el.style.top = Math.round(at[1] + (off ? off[1] : 0)) + "px"; return el; };

  /* a far lamp placed through the camera: the world point `dist` metres along the ray through screen (sx, sy) */
  N.lampAt = function (THREE, R, sx, sy, dist, size) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(sx / N.W * 2 - 1, 1 - sy / N.H * 2, 0.5).unproject(R.camera).sub(R.camera.position).normalize().multiplyScalar(dist).add(R.camera.position);
    return N.lampGlow(THREE, R, [v.x, v.y, v.z], 0xeef2ff, size || 0.9, 0);
  };


  /* ---- frame helpers, carried from the 2026-11-08 chassis ---------------------------------- */
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
    /* the key is the window's last light; a frame may scale it through N.KEY_SCALE */
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { i: (W.rig.key.i || 3) * (N.KEY_SCALE || 1), shadowSize: size || 14, mapSize: map || 2048 }) });
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
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:34px; font-weight:500; letter-spacing:0.04em; line-height:1.2; text-align:center; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".lab.cyan { color:#8FE0F0; }",
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
  /* a darken-only wash under the footer, so the site line and the claim ids sit on a dark field and no edge strikes them */
  N.footWash = function (cx, o) {
    o = o || {};
    [[o.x == null ? 850 : o.x, 1300, o.r || 460], [180, 1300, 300]].forEach(function (c) {
      var g = cx.createRadialGradient(c[0], c[1], 20, c[0], c[1], c[2]);
      g.addColorStop(0, "rgba(5,6,10," + (o.a || 0.72) + ")"); g.addColorStop(0.55, "rgba(5,6,10," + ((o.a || 0.72) * 0.6) + ")"); g.addColorStop(1, "rgba(5,6,10,0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, N.H);
    });
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
