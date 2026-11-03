/* deck/2026-11-01-foundry.js — the chassis for the 2026-11-01 deck: Texas A&M's Aggie AI Foundry, a $2 million WoodNext
 * Foundation grant for a campus lab where computer controlled arms mix, melt and test new metal alloys (tx-2026-0229), set
 * beside the NSF Autonomous Robotic Metallurgist platform (tx-2026-0090) and PhaseForge (tx-2026-0122).
 *
 * THE VISUAL ARGUMENT. The metal still has to be melted. The software narrows the mixes and no tool can predict how an
 * alloy will behave, so every claim in the deck is carried by the thing the lab actually makes: an arc melted alloy button
 * on a water cooled copper hearth, and a tensile bar pulled until it breaks. One button is a drawing unit of money where a
 * frame counts money. A glowing button is metal being made. The deck never shows a screen with an answer on it.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky, one warm seam low on the key's side, the
 * hearth in a pool of light and everything past it gone dark. The rooms are TXT.interior, dark around one window.
 *
 * THE LIGHT is azimuth -60, elevation 14. +x is east and +z is south. A camera looking north (-z) has the key on its
 * LEFT, every lit edge is on the left, and every cast runs long to the right. TXBENCH reliefs read the same declaration:
 * raked from the upper left, casting to the lower right. Fourteen degrees is the rake a relief needs to keep its casts.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `copper_hearth` (a water cooled copper block with rows of
 * spherical pockets), `alloy_button` (an arc melted button, cool, hot or sectioned), `tensile_bar` (a flat dogbone test
 * specimen, whole or pulled to fracture), `crucible` (an alumina crucible) and `robot_arm` (a six axis arm with a
 * parallel gripper). All drawn to illustrate, to no maker's design, in the kit's conventions (metres, y up, origin on the
 * ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is bluebonnet, #4E5FA8, and it means ONE thing: this is the same alloy. A paint pen mark on the one button
 * the deck follows, on its cut section and on the grip of the bar pulled from it. Every warm hue belongs to copper and to
 * the glow of metal being made, which is the deck's light rather than its accent, so the accent is the one cool colour.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated. Every
 * frame composes its own picture, and every count a frame draws is read from figures.json in that frame's own code. The
 * chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("foundry.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "foundry",
    light: { az: -60, el: 14 },
    sky: "lastLight",
    ground: "#08080B",
    material: "#B87333",
    accent: "#4E5FA8",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.82, strength: 0.16, radius: 10 },
      grain: { amount: 0.016, size: 2, seed: 20261101 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261101;
  N.ACCENT = 0x4e5fa8;   /* bluebonnet, brand.yaml's token, and it means ONE thing: this is the same alloy */
  N.INK = "#ECE8DF";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */
  function noiseTex(THREE, seed, lo, hi, n, sz) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "rgb(128,128,128)"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < n; i++) { var v = Math.floor(lo + r() * (hi - lo)); x.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; x.fillRect(r() * 256, r() * 256, sz, sz); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  /* COPPER FACE MILL: a fly cutter leaves fine overlapping arcs a few millimetres apart, low in contrast, and the copper
   * carries them only in its roughness (about 0.2 to 0.3) and a faint relief, never in its colour. A full width linear grind
   * driven hard into the relief read as walnut veneer in the seventh audition, so the marks are arcs and they are quiet. */
  function grindTex(THREE, seed) {
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "rgb(214,214,214)"; x.fillRect(0, 0, 512, 512);
    var R0 = 900;
    for (var i = -40; i < 600; i += 3.2) {
      var v = r() < 0.5 ? 226 : 204; x.strokeStyle = "rgba(" + v + "," + v + "," + v + "," + (0.12 + r() * 0.12) + ")"; x.lineWidth = 0.8 + r() * 0.8;
      x.beginPath(); x.arc(i, 256 + R0, R0, Math.PI * 1.25, Math.PI * 1.75); x.stroke();
      x.beginPath(); x.arc(i - 512, 256 + R0, R0, Math.PI * 1.25, Math.PI * 1.75); x.stroke();
      x.beginPath(); x.arc(i + 512, 256 + R0, R0, Math.PI * 1.25, Math.PI * 1.75); x.stroke();
    }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 16; return t;
  }
  /* ARC MELTED ALLOY: a frozen ripple skin, darker in the folds, with a faint temper tint */
  function alloyTex(THREE, seed, base) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = base; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < 90; i++) { x.strokeStyle = "rgba(40,40,46," + (0.025 + r() * 0.05) + ")"; x.lineWidth = 3 + r() * 6; x.beginPath(); var cx0 = r() * 256, cy0 = r() * 256, rr = 8 + r() * 60; x.arc(cx0, cy0, rr, r() * 6, r() * 6 + 1.5 + r() * 2); x.stroke(); }
    for (var k = 0; k < 40; k++) { x.fillStyle = "rgba(" + (r() < 0.5 ? "150,120,190" : "200,160,90") + "," + (0.03 + r() * 0.05) + ")"; x.fillRect(r() * 256, r() * 256, 10 + r() * 30, 6 + r() * 20); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  /* EPOXY BENCH: black resin worn grey by years of samples, fine scratches running every way, rings where hot things sat */
  function benchTex(THREE, seed) {
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "#4a4c53"; x.fillRect(0, 0, 512, 512);
    for (var k = 0; k < 90; k++) { x.fillStyle = "rgba(" + (r() < 0.5 ? "70,72,78" : "12,12,14") + "," + (0.05 + r() * 0.12) + ")"; var s = 10 + r() * 60; x.beginPath(); x.ellipse(r() * 512, r() * 512, s, s * (0.4 + r() * 0.6), r() * 3, 0, 6.3); x.fill(); }
    for (var i = 0; i < 900; i++) { x.strokeStyle = "rgba(190,192,198," + (0.04 + r() * 0.1) + ")"; x.lineWidth = 0.5 + r() * 0.6; var a = r() * 6.3, l = 6 + r() * 60, x0 = r() * 512, y0 = r() * 512; x.beginPath(); x.moveTo(x0, y0); x.lineTo(x0 + Math.cos(a) * l, y0 + Math.sin(a) * l); x.stroke(); }
    for (var q = 0; q < 14; q++) { x.strokeStyle = "rgba(110,84,60," + (0.08 + r() * 0.1) + ")"; x.lineWidth = 2 + r() * 3; x.beginPath(); x.arc(r() * 512, r() * 512, 10 + r() * 30, 0, 6.3); x.stroke(); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; t.repeat.set(3, 1.5); return t;
  }
  N.mats = function (THREE, K) {
    if (N._M) return N._M;
    var tooth = noiseTex(THREE, 11, 104, 156, 9000, 1.6);
    var ripple = noiseTex(THREE, 17, 90, 170, 2600, 3.2);
    var cu = grindTex(THREE, 5); cu.repeat.set(1, 1);
    N._M = {
      copper: new THREE.MeshPhysicalMaterial({ color: 0xb87333, metalness: 1, roughness: 0.3, roughnessMap: cu, envMapIntensity: 1 }),
      copperDark: new THREE.MeshStandardMaterial({ color: 0x6e3e22, metalness: 0.85, roughness: 0.5, bumpMap: tooth, bumpScale: 0.3 }),
      alloy: new THREE.MeshPhysicalMaterial({ color: 0xc2c4c9, metalness: 0.7, roughness: 0.24, bumpMap: ripple, bumpScale: 0.45, clearcoat: 0.6, clearcoatRoughness: 0.12 }),
      alloyDark: new THREE.MeshPhysicalMaterial({ color: 0xa39c8e, metalness: 0.65, roughness: 0.3, bumpMap: ripple, bumpScale: 0.15, clearcoat: 0.5, clearcoatRoughness: 0.15 }),
      polished: new THREE.MeshPhysicalMaterial({ color: 0xd9dbe0, metalness: 1, roughness: 0.08, clearcoat: 0.3 }),
      /* the deck's one accent: metal being made, a button under the arc. Emissive held so the core reads gold, not white */
      hot: new THREE.MeshStandardMaterial({ color: 0x1a0a04, emissive: 0xff5a10, emissiveIntensity: 1.25, roughness: 0.45, metalness: 0.2, bumpMap: ripple, bumpScale: 0.9 }),
      hotCore: new THREE.MeshStandardMaterial({ color: 0x1a0a04, emissive: 0xffa040, emissiveIntensity: 1.5, roughness: 0.35 }),
      alumina: new THREE.MeshStandardMaterial({ color: 0xd8d2c6, roughness: 0.85, bumpMap: tooth, bumpScale: 0.6 }),
      steel: new THREE.MeshPhysicalMaterial({ color: 0xb8bcc2, metalness: 0.6, roughness: 0.36, bumpMap: tooth, bumpScale: 0.2 }),
      steelDark: new THREE.MeshStandardMaterial({ color: 0x2b2d31, metalness: 0.7, roughness: 0.45 }),
      armPaint: new THREE.MeshPhysicalMaterial({ color: 0xc9c7c1, metalness: 0.1, roughness: 0.42, clearcoat: 0.5, clearcoatRoughness: 0.3, bumpMap: tooth, bumpScale: 0.08 }),
      armJoint: new THREE.MeshStandardMaterial({ color: 0x1c1d21, metalness: 0.5, roughness: 0.5 }),
      rubber: new THREE.MeshStandardMaterial({ color: 0x141416, roughness: 0.8 }),
      benchTop: new THREE.MeshStandardMaterial({ map: benchTex(THREE, 23), color: 0xffffff, metalness: 0.1, roughness: 0.48, bumpMap: tooth, bumpScale: 0.5 }),
      hose: new THREE.MeshStandardMaterial({ color: 0x1b2a3a, roughness: 0.55 }),
      tungsten: new THREE.MeshPhysicalMaterial({ color: 0x9a9ca2, metalness: 1, roughness: 0.22 }),
      tray: new THREE.MeshPhysicalMaterial({ color: 0x4a4e57, metalness: 0.35, roughness: 0.55, bumpMap: tooth, bumpScale: 0.5 }),
      trayTop: new THREE.MeshPhysicalMaterial({ color: 0x5a5e68, metalness: 0.35, roughness: 0.55, bumpMap: tooth, bumpScale: 0.6 }),
      wellFloor: new THREE.MeshStandardMaterial({ color: 0x55585f, roughness: 0.55, metalness: 0.35 }),
      wellWall: new THREE.MeshStandardMaterial({ color: 0x6a6d74, roughness: 0.45, metalness: 0.4 }),
      paper: new THREE.MeshStandardMaterial({ color: 0x8a8477, roughness: 0.9 }),
      fracture: new THREE.MeshStandardMaterial({ color: 0x9a9890, roughness: 0.9, metalness: 0.3, bumpMap: ripple, bumpScale: 3.0 }),
      /* the accent: a bluebonnet paint pen mark, matte, held a touch brighter so the dark room does not crush it */
      mark: new THREE.MeshStandardMaterial({ color: 0x5a6cc0, roughness: 0.6, emissive: 0x24306a, emissiveIntensity: 0.6 })
    };
    return N._M;
  };

  /* THE HOT BUTTON: an emissive map hottest at the crown and cooling to a dull red at the foot, mapped in plan through
   * uvBox's top projection, so a glowing button reads as metal cooling from its edge rather than a lamp. */
  N.hotMat = function (THREE, d) {
    if (N._hot) return N._hot;
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
    g.addColorStop(0, "#ffd08a"); g.addColorStop(0.35, "#ff9a3c"); g.addColorStop(0.7, "#d8461a"); g.addColorStop(1, "#5a1206");
    x.fillStyle = g; x.fillRect(0, 0, 256, 256);
    
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
    t.repeat.set(1, 1); t.offset.set(0, 0);
    N._hot = new THREE.MeshStandardMaterial({ color: 0x120804, emissive: 0xffffff, emissiveMap: t, emissiveIntensity: 2.4, roughness: 0.5, metalness: 0.1, bumpMap: N._M.alloy.bumpMap, bumpScale: 0.9 });
    return N._hot;
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.copper_hearth) return;
    var M = N.mats(THREE, K);
    function shade(o) { o.traverse(function (c) { if (c.isMesh) { c.castShadow = c.receiveShadow = true; } }); return o; }

    /* A WATER COOLED COPPER HEARTH: a machined copper block w x d x h with rows x cols spherical pockets of radius pr, the
     * top a displaced plane so each pocket is a real dish that holds a button and takes the key on its far wall. Two
     * water fittings on the back face with hoses. userData.pockets holds each pocket's centre on the top face. */
    K.define("copper_hearth", {
      size: [0.36, 0.06, 0.24],
      options: { w: 0.36, d: 0.24, h: 0.06, rows: 2, cols: 3, pr: 0.024, depth: 0.007, hoses: true, seg: 560, fd: 0, fz: 0 },
      note: "Water cooled copper hearth for arc melting: rows x cols spherical pockets (radius pr, depth), hose fittings on -z. userData.pockets.",
      make: function (o) {
        /* fd, fz: the pocket field may be shallower than the block and sit off its centre, so one continuous block can run on
         * past its pockets (the cover runs it off the bottom of the frame) */
        var g = new THREE.Group(), pockets = [], pitchX = o.w / (o.cols + 0.6), pitchZ = (o.fd || o.d) / (o.rows + 0.6);
        for (var r = 0; r < o.rows; r++) for (var c = 0; c < o.cols; c++) pockets.push([(c - (o.cols - 1) / 2) * pitchX, o.h - o.depth, (r - (o.rows - 1) / 2) * pitchZ + (o.fz || 0)]);
        /* the top: a machined plate with a round hole per pocket, and a spherical bowl under each hole, so every pocket
         * is a recessed dish with a smooth rim rather than a stepped height field */
        var PT = Math.max(o.depth + 0.003, 0.01), shp = new THREE.Shape();
        shp.moveTo(-o.w / 2, -o.d / 2); shp.lineTo(o.w / 2, -o.d / 2); shp.lineTo(o.w / 2, o.d / 2); shp.lineTo(-o.w / 2, o.d / 2); shp.lineTo(-o.w / 2, -o.d / 2);
        pockets.forEach(function (q) { var hp = new THREE.Path(); hp.absarc(q[0], -q[2], o.pr, 0, Math.PI * 2, true); shp.holes.push(hp); });
        var plate = new THREE.ExtrudeGeometry(shp, { depth: PT, bevelEnabled: true, bevelThickness: 0.0012, bevelSize: 0.0012, bevelSegments: 2, curveSegments: 48 });
        plate.rotateX(-Math.PI / 2); plate.translate(0, o.h - PT, 0); K.uvBox(plate, 0.4);
        g.add(new THREE.Mesh(plate, M.copper));
        var Rs = (o.pr * o.pr + o.depth * o.depth) / (2 * o.depth), th = Math.asin(Math.min(1, o.pr / Rs));
        var bowl = new THREE.SphereGeometry(Rs, 56, 14, 0, Math.PI * 2, Math.PI - th, th); K.uvBox(bowl, 0.4);
        pockets.forEach(function (q) { var bm = new THREE.Mesh(bowl, M.copper); bm.material.side = THREE.DoubleSide; bm.position.set(q[0], o.h - o.depth + Rs, q[2]); g.add(bm); });
        var sideH = o.h - PT;
        var body = TXT.roundedBox(o.w, sideH, o.d, 0.004, M.copper); body.position.y = sideH / 2; g.add(body);
        /* a chamfer band at the top edge, darker copper, so the block reads as machined */
        var band = new THREE.Mesh(new THREE.BoxGeometry(o.w + 0.002, 0.003, o.d + 0.002), M.copperDark); band.position.y = o.h * 0.35; g.add(band);
        if (o.hoses) {
          [-1, 1].forEach(function (s) {
            var fit = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.03, 20), M.steel); fit.rotation.x = Math.PI / 2; fit.position.set(s * o.w * 0.3, o.h * 0.45, -o.d / 2 - 0.015); g.add(fit);
            var nut = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.011, 0.012, 6), M.steel); nut.rotation.x = Math.PI / 2; nut.position.set(s * o.w * 0.3, o.h * 0.45, -o.d / 2 - 0.006); g.add(nut);
            var curve = new THREE.CatmullRomCurve3([new THREE.Vector3(s * o.w * 0.3, o.h * 0.45, -o.d / 2 - 0.03), new THREE.Vector3(s * o.w * 0.34, o.h * 0.3, -o.d / 2 - 0.12), new THREE.Vector3(s * o.w * 0.5, 0.012, -o.d / 2 - 0.3), new THREE.Vector3(s * o.w * 0.8, 0.012, -o.d / 2 - 0.7)]);
            g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 48, 0.007, 10, false), M.hose));
          });
        }
        g.userData.pockets = pockets; g.userData.keepOrigin = true;
        return shade(g);
      }
    });

    /* AN ARC MELTED BUTTON: a squashed dome d across and h tall with a frozen ripple skin and a flattened foot where it sat
     * on the copper. state cool|hot|dark|section: hot glows dusk gold (metal being made); section is cut in half to show a
     * polished face. */
    K.define("alloy_button", {
      size: [0.034, 0.016, 0.034],
      options: { d: 0.034, h: 0.016, state: "cool", seed: 1 },
      note: "An arc melted alloy button: d across, h tall, rippled skin. state cool|hot|dark|section.",
      make: function (o) {
        var r = lcg(o.seed * 97 + 13), geo = new THREE.SphereGeometry(o.d / 2, 64, 20, 0, Math.PI * 2, 0, Math.PI / 2), p = geo.attributes.position;
        for (var k = 0; k < p.count; k++) {
          var x = p.getX(k), y = p.getY(k), z = p.getZ(k), rr = Math.hypot(x, z) / (o.d / 2), ang = Math.atan2(z, x);
          /* flattened crown, a slight belly, low concentric freeze ripples and a little lobing from the arc */
          var hy = y / (o.d / 2), lobe = 1 + 0.025 * Math.sin(ang * 3 + o.seed) + 0.012 * Math.sin(ang * 7 + o.seed * 2);
          var yy = o.h * Math.pow(Math.max(0, hy), 0.85) * (1 - 0.06 * Math.pow(1 - rr, 2)) + o.h * 0.018 * Math.sin(rr * 26 + o.seed) * rr;
          p.setX(k, x * lobe); p.setZ(k, z * lobe); p.setY(k, Math.max(0, yy));
        }
        geo.computeVertexNormals();
        { var uv = new Float32Array(p.count * 2); for (var u = 0; u < p.count; u++) { uv[u * 2] = p.getX(u) / o.d + 0.5; uv[u * 2 + 1] = p.getZ(u) / o.d + 0.5; } geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); }
        var mat = o.state === "hot" ? N.hotMat(THREE, o.d) : o.state === "dark" ? M.alloyDark : M.alloy;
        var g = new THREE.Group(), m = new THREE.Mesh(geo, mat);
        if (o.state === "section") {
          m.material = M.alloy;
          var cut = new THREE.Mesh(new THREE.CircleGeometry(o.d * 0.5, 48, 0, Math.PI), M.polished); cut.scale.set(1, o.h / (o.d * 0.5) * 1.02, 1); cut.position.z = 0.0001; g.add(cut);
          geo.clippingPlanes = null;
        }
        g.add(m);
        return shade(g);
      }
    });

    /* A ROUND TENSILE SPECIMEN: a lathe turned bar along x, grips of radius gr, a gauge of radius rr and length gl, fillets
     * between. pulled: true breaks it at mid gauge with a necked cup and cone, the two halves apart by gapW. */
    function roundBar(o) {
      var g = new THREE.Group(), L2 = o.L / 2, g2 = o.gl / 2, fl = o.fl || 0.008;
      function prof(x0, x1, side) {
        var pts = [], N2 = 90;
        for (var i = 0; i <= N2; i++) {
          var x = x0 + (x1 - x0) * i / N2, ax = Math.abs(x), r;
          if (ax <= g2) r = o.rr; else if (ax >= g2 + fl) r = o.gr; else { var u = (ax - g2) / fl; r = o.rr + (o.gr - o.rr) * (1 - Math.cos(u * Math.PI / 2)); }
          if (o.pulled) { var dn = Math.abs(x - (side < 0 ? x1 : x0)); if (dn < o.rr * 2.4) r *= 0.6 + 0.4 * Math.pow(dn / (o.rr * 2.4), 1.8); }
          pts.push(new THREE.Vector2(r, x));
        }
        pts.unshift(new THREE.Vector2(0.0001, pts[0].y)); pts.push(new THREE.Vector2(0.0001, pts[pts.length - 1].y));
        if (side > 0) pts.reverse();
        var geo = new THREE.LatheGeometry(side > 0 ? pts.reverse() : pts, 48); geo.rotateZ(-Math.PI / 2); K.uvBox(geo, 0.05);
        return geo;
      }
      var parts = o.pulled ? [[-L2, -o.gapW / 2, -1], [o.gapW / 2, L2, 1]] : [[-L2, L2, -1]];
      parts.forEach(function (pr) {
        var m = new THREE.Mesh(prof(pr[0], pr[1], pr[2]), M.steel); m.position.y = o.gr; g.add(m);
        if (o.pulled) {
          /* the fracture face: a rough fibrous disc with a raised shear lip, facing out of the break, lit when it faces the key */
          var fx = pr[2] < 0 ? pr[1] : pr[0], fr = o.rr * 0.66, fg = new THREE.CircleGeometry(fr, 40, 0, Math.PI * 2), fp = fg.attributes.position, rr2 = lcg(o.seed * 7 + (pr[2] < 0 ? 1 : 2));
          for (var q = 0; q < fp.count; q++) { var rx = Math.hypot(fp.getX(q), fp.getY(q)) / fr; fp.setZ(q, (rx > 0.82 ? 0.0009 : 0) + (rr2() - 0.5) * 0.0005 + (pr[2] < 0 ? -1 : 1) * 0.0006 * (1 - rx)); }
          fg.computeVertexNormals();
          var face = new THREE.Mesh(fg, M.fracture); face.material.side = THREE.DoubleSide; face.rotation.set(0, pr[2] < 0 ? Math.PI / 2 : -Math.PI / 2, 0); face.rotateX(-0.6); face.scale.set(1, 1.25, 1); face.position.set(fx, o.gr, 0); g.add(face);
        }
        /* the threaded grip end: rolled threads at a 1.5 mm pitch, one instanced ring each */
        var x0 = pr[2] < 0 ? -L2 + 0.002 : g2 + fl + 0.003, x1 = pr[2] < 0 ? -(g2 + fl + 0.003) : L2 - 0.002, pitch = 0.0013, n = Math.max(0, Math.floor((x1 - x0) / pitch));
        if (n > 0) {
          var pts3 = [], turns = n, segs = turns * 18;
          for (var hs = 0; hs <= segs; hs++) { var tt = hs / segs, an = tt * turns * Math.PI * 2; pts3.push(new THREE.Vector3(x0 + tt * (x1 - x0), o.gr + o.gr * 0.98 * Math.cos(an), o.gr * 0.98 * Math.sin(an))); }
          g.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts3), segs, o.gr * 0.11, 6, false), M.steel));
        }
      });
      return shade(g);
    }
    /* A TENSILE BAR: a flat dogbone specimen, grip ends gw wide, gauge section ww wide and gl long, t thick, its fillets
     * real arcs. pulled: true breaks it at the gauge's middle with a necked, cup and cone gap. Lies along x on the bench. */
    K.define("tensile_bar", {
      size: [0.1, 0.003, 0.02],
      options: { L: 0.1, gw: 0.02, ww: 0.006, gl: 0.032, t: 0.003, pulled: false, gapW: 0.004, seed: 1, round: false, gr: 0.0075, rr: 0.0045, fl: 0.008 },
      note: "A flat dogbone tensile specimen along x, t thick. pulled: true breaks it at mid gauge with a neck and a gap.",
      make: function (o) {
        function outline(x0, x1, neck) {
          var s = new THREE.Shape(), L2 = o.L / 2, g2 = o.gl / 2, f = (o.gw - o.ww) / 2, top = [];
          var N2 = 60;
          for (var i = 0; i <= N2; i++) {
            var x = -L2 + o.L * i / N2, ax = Math.abs(x), hw;
            if (ax <= g2) hw = o.ww / 2; else if (ax >= g2 + f * 1.6) hw = o.gw / 2;
            else { var u = (ax - g2) / (f * 1.6); hw = o.ww / 2 + f * (1 - Math.cos(u * Math.PI / 2)); }
            if (neck && Math.abs(x) < o.ww) hw *= 0.7 + 0.3 * (Math.abs(x) / o.ww);
            if (x >= x0 && x <= x1) top.push([x, hw]);
          }
          s.moveTo(top[0][0], -top[0][1]);
          top.forEach(function (q) { s.lineTo(q[0], -q[1]); });
          for (var j = top.length - 1; j >= 0; j--) s.lineTo(top[j][0], top[j][1]);
          return s;
        }
        if (o.round) return roundBar(o);
        var g = new THREE.Group(), ext = { depth: o.t, bevelEnabled: true, bevelThickness: 0.0003, bevelSize: 0.0003, bevelSegments: 1 };
        var parts = o.pulled ? [[-o.L / 2, -o.gapW / 2], [o.gapW / 2, o.L / 2]] : [[-o.L / 2, o.L / 2]];
        parts.forEach(function (pr, idx) {
          var geo = new THREE.ExtrudeGeometry(outline(pr[0], pr[1], o.pulled), ext); geo.rotateX(-Math.PI / 2); K.uvBox(geo, 0.05);
          var m = new THREE.Mesh(geo, M.steel); m.position.x = o.pulled ? (idx === 0 ? -o.gapW * 0.6 : o.gapW * 0.6) : 0; g.add(m);
          if (o.pulled) { var face = new THREE.Mesh(new THREE.BoxGeometry(0.0008, o.t * 0.9, o.ww * 0.62), M.alloyDark); face.position.set(idx === 0 ? -o.gapW * 1.1 : o.gapW * 1.1, o.t / 2, 0); g.add(face); }
        });
        return shade(g);
      }
    });

    /* AN ALUMINA CRUCIBLE: a lathe cup, r at the lip, h tall, wall thickness th. hot: the melt inside glows dusk gold. */
    K.define("crucible", {
      size: [0.06, 0.07, 0.06],
      options: { r: 0.03, h: 0.07, th: 0.004, hot: false, fill: 0.55 },
      note: "An alumina crucible: r at the lip, h tall. hot: true fills it with glowing melt to fill of its height.",
      make: function (o) {
        var rb = o.r * 0.72, pts = [new THREE.Vector2(0.0004, 0), new THREE.Vector2(rb, 0), new THREE.Vector2(rb + 0.002, 0.002), new THREE.Vector2(o.r, o.h), new THREE.Vector2(o.r - o.th, o.h), new THREE.Vector2(rb - o.th + 0.002, o.th + 0.002), new THREE.Vector2(0.0004, o.th)];
        var geo = new THREE.LatheGeometry(pts, 48); K.uvBox(geo, 0.05);
        var g = new THREE.Group(); g.add(new THREE.Mesh(geo, M.alumina));
        if (o.hot) {
          var fy = o.th + (o.h - o.th) * o.fill, fr = rb + (o.r - rb) * o.fill - o.th;
          var melt = new THREE.Mesh(new THREE.CircleGeometry(fr, 40), M.hotCore); melt.rotation.x = -Math.PI / 2; melt.position.y = fy; g.add(melt);
        }
        return shade(g);
      }
    });

    /* A SIX AXIS ARM: base, turret, shoulder, upper arm, elbow, forearm, wrist and a parallel gripper, reach about 1.1 m.
     * pose [turret, shoulder, elbow, wrist] radians. grip: an Object3D to place in the jaws, optional. Painted pale grey
     * with black joint housings, cable runs on the upper arm. userData.tip is the gripper's centre. */
    K.define("robot_arm", {
      size: [0.5, 1.4, 0.5],
      options: { pose: [0.4, -0.5, 1.4, 0.6], upper: 0.52, fore: 0.48, scale: 1 },
      note: "An illustrative six axis arm with a parallel gripper, to no maker's design. pose [turret, shoulder, elbow, wrist] radians.",
      make: function (o) {
        var g = new THREE.Group(), P = o.pose;
        var base = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.19, 0.08, 40), M.armJoint); base.position.y = 0.04; g.add(base);
        var plinth = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.16, 0.12, 40), M.armPaint); plinth.position.y = 0.14; g.add(plinth);
        var turret = new THREE.Group(); turret.position.y = 0.2; turret.rotation.y = P[0]; g.add(turret);
        var tb = TXT.roundedBox(0.22, 0.2, 0.24, 0.05, M.armPaint); tb.position.y = 0.1; turret.add(tb);
        var shoulder = new THREE.Group(); shoulder.position.set(0, 0.22, 0); shoulder.rotation.x = P[1]; turret.add(shoulder);
        var sj = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.26, 36), M.armJoint); sj.rotation.z = Math.PI / 2; shoulder.add(sj);
        var cap = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.272, 36), M.armPaint); cap.rotation.z = Math.PI / 2; shoulder.add(cap);
        var ua = TXT.roundedBox(0.15, o.upper, 0.17, 0.05, M.armPaint); ua.position.y = o.upper / 2; shoulder.add(ua);
        var cable = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, o.upper * 0.8, 10), M.armJoint); cable.position.set(0.09, o.upper / 2, -0.04); shoulder.add(cable);
        var elbow = new THREE.Group(); elbow.position.y = o.upper; elbow.rotation.x = P[2]; shoulder.add(elbow);
        var ej = new THREE.Mesh(new THREE.CylinderGeometry(0.078, 0.078, 0.2, 32), M.armJoint); ej.rotation.z = Math.PI / 2; elbow.add(ej);
        var ec = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.21, 32), M.armPaint); ec.rotation.z = Math.PI / 2; elbow.add(ec);
        var fa = TXT.roundedBox(0.11, o.fore, 0.12, 0.04, M.armPaint); fa.position.y = o.fore / 2; elbow.add(fa);
        var wrist = new THREE.Group(); wrist.position.y = o.fore; wrist.rotation.x = P[3]; elbow.add(wrist);
        var wj = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.12, 28), M.armJoint); wj.rotation.z = Math.PI / 2; wrist.add(wj);
        var fl = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.05, 0.07, 28), M.steel); fl.position.y = 0.06; wrist.add(fl);
        var gb = TXT.roundedBox(0.09, 0.04, 0.05, 0.01, M.steelDark); gb.position.y = 0.115; wrist.add(gb);
        [-1, 1].forEach(function (s) { var f = TXT.roundedBox(0.012, 0.06, 0.03, 0.003, M.steel); f.position.set(s * 0.022, 0.165, 0); wrist.add(f); });
        var tip = new THREE.Object3D(); tip.position.y = 0.18; wrist.add(tip);
        g.userData.tip = tip; g.userData.keepOrigin = true;
        if (o.scale !== 1) g.scale.setScalar(o.scale);
        return shade(g);
      }
    });
    /* A SAMPLE TRAY: a dark anodised aluminium plate w x d x h with n flat bottomed wells of radius wr and depth wd on a
     * pitch, in rows of cols, laid row by row from the near left corner. The top is a displaced plane so each well has a
     * lit wall and a shadowed wall. userData.wells holds each well's floor centre, in fill order. */
    K.define("sample_tray", {
      size: [0.36, 0.02, 0.09],
      options: { n: 20, cols: 10, pitch: 0.034, wr: 0.0145, wd: 0.006, h: 0.02, margin: 0.022, seg: 0 },
      note: "A dark anodised aluminium sample tray with n flat bottomed wells in rows of cols, filled from the near left. userData.wells.",
      make: function (o) {
        var rows = Math.ceil(o.n / o.cols), w = o.cols * o.pitch + 2 * o.margin - (o.pitch - 2 * o.wr), d = rows * o.pitch + 2 * o.margin - (o.pitch - 2 * o.wr);
        var wells = [], x0 = -w / 2 + o.margin + o.wr, z0 = d / 2 - o.margin - o.wr;
        for (var i = 0; i < o.n; i++) { var r = Math.floor(i / o.cols), c = i % o.cols; wells.push([x0 + c * o.pitch, o.h - o.wd, z0 - r * o.pitch]); }
        var g = new THREE.Group(), shape = new THREE.Shape();
        shape.moveTo(-w / 2, -d / 2); shape.lineTo(w / 2, -d / 2); shape.lineTo(w / 2, d / 2); shape.lineTo(-w / 2, d / 2); shape.lineTo(-w / 2, -d / 2);
        wells.forEach(function (q) { var h0 = new THREE.Path(); h0.absarc(q[0], -q[2], o.wr, 0, Math.PI * 2, true); shape.holes.push(h0); });
        var plate = new THREE.ExtrudeGeometry(shape, { depth: o.wd, bevelEnabled: true, bevelThickness: 0.0006, bevelSize: 0.0006, bevelSegments: 2, curveSegments: 28 });
        plate.rotateX(-Math.PI / 2); plate.translate(0, o.h - o.wd, 0); K.uvBox(plate, 0.2);
        g.add(new THREE.Mesh(plate, M.trayTop));
        var body = TXT.roundedBox(w, o.h - o.wd, d, 0.002, M.tray); body.position.y = (o.h - o.wd) / 2; g.add(body);
        var floor = new THREE.Mesh(new THREE.PlaneGeometry(w * 0.999, d * 0.999), M.wellFloor); floor.rotation.x = -Math.PI / 2; floor.position.y = o.h - o.wd + 0.0002; g.add(floor);
        /* each pocket's wall, an open cylinder so the window lights one side and shadows the other */
        var wall = new THREE.CylinderGeometry(o.wr, o.wr, o.wd, 28, 1, true), iw = new THREE.InstancedMesh(wall, M.wellWall, wells.length), m4 = new THREE.Matrix4();
        wells.forEach(function (q, k) { m4.makeTranslation(q[0], o.h - o.wd / 2, q[2]); iw.setMatrixAt(k, m4); }); iw.material.side = THREE.BackSide; g.add(iw);
        g.userData.wells = wells; g.userData.keepOrigin = true; g.userData.dims = [w, d];
        return shade(g);
      }
    });
    /* A HORIZONTAL TENSILE TESTER at bench scale: a ground steel bed on two rails, a fixed grip on the left and a pulling
     * grip on the right, each a bolted housing with a pair of serrated wedge jaws, a lead screw and a load cell can on the
     * right. span is the distance between the jaws' faces. Drawn to illustrate, to no maker's design. userData.jawL and
     * jawR are the jaw faces' centres, where a bar's grips sit. */
    K.define("tensile_tester", {
      size: [0.6, 0.12, 0.16],
      options: { span: 0.07, bedL: 0.6 },
      note: "An illustrative horizontal tensile tester: steel bed and rails, two bolted wedge grips span apart, lead screw, load cell.",
      make: function (o) {
        var g = new THREE.Group(), H = 0.03;
        var bed = TXT.roundedBox(o.bedL, H, 0.14, 0.004, M.steelDark); bed.position.y = H / 2; g.add(bed);
        [-1, 1].forEach(function (s2) { var rail = TXT.roundedBox(o.bedL * 0.96, 0.012, 0.018, 0.002, M.steel); rail.position.set(0, H + 0.006, s2 * 0.045); g.add(rail); });
        var screw = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.007, o.bedL * 0.9, 20), M.steel); screw.rotation.z = Math.PI / 2; screw.position.set(0, H + 0.012, 0); g.add(screw);
        for (var t = 0; t < 60; t++) { var th = new THREE.Mesh(new THREE.TorusGeometry(0.0072, 0.0012, 6, 16), M.steelDark); th.rotation.y = Math.PI / 2; th.position.set(-o.bedL * 0.42 + t * o.bedL * 0.014, H + 0.012, 0); g.add(th); }
        function grip(side) {
          var gg = new THREE.Group(), hx = side * (o.span / 2 + 0.045);
          var house = TXT.roundedBox(0.09, 0.075, 0.11, 0.006, M.armPaint); house.position.set(hx, H + 0.012 + 0.0375, 0); gg.add(house);
          var face = TXT.roundedBox(0.012, 0.05, 0.07, 0.002, M.steel); face.position.set(side * (o.span / 2 + 0.006), H + 0.012 + 0.04, 0); gg.add(face);
          [-1, 1].forEach(function (s3) {
            var jaw = TXT.roundedBox(0.03, 0.016, 0.022, 0.002, M.steel); jaw.position.set(side * (o.span / 2 + 0.016), H + 0.012 + 0.04 + s3 * 0.012, 0); gg.add(jaw);
            for (var k = 0; k < 7; k++) { var tooth = new THREE.Mesh(new THREE.BoxGeometry(0.0012, 0.002, 0.022), M.steelDark); tooth.position.set(side * (o.span / 2 + 0.004 + k * 0.004), H + 0.012 + 0.04 + s3 * 0.0045, 0); gg.add(tooth); }
          });
          [[-0.03, -0.035], [0.03, -0.035], [-0.03, 0.035], [0.03, 0.035]].forEach(function (b) { var bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.004, 6), M.steel); bolt.position.set(hx + b[0], H + 0.012 + 0.0755, b[1]); gg.add(bolt); });
          return gg;
        }
        g.add(grip(-1)); g.add(grip(1));
        var cell = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.05, 40), M.steel); cell.rotation.z = Math.PI / 2; cell.position.set(o.span / 2 + 0.12, H + 0.012 + 0.04, 0); g.add(cell);
        var cab = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(o.span / 2 + 0.14, H + 0.06, -0.02), new THREE.Vector3(o.span / 2 + 0.2, H + 0.09, -0.08), new THREE.Vector3(o.span / 2 + 0.24, H, -0.2)]), 24, 0.003, 8, false), M.rubber); g.add(cab);
        g.userData.jawY = H + 0.012 + 0.04; g.userData.keepOrigin = true;
        return shade(g);
      }
    });
    /* A STACK OF OFFPRINTS: n letter sheets in one block, each sheet a thin slab offset a hair so the edge shows lines,
     * a few sheets proud or short. Paper is held toward its shadow tone so a pale block does not lift the frame. */
    K.define("offprint_stack", {
      size: [0.216, 0.01, 0.279],
      options: { n: 100, t: 0.0001, w: 0.216, d: 0.279, seed: 1 },
      note: "A block of n letter sheets with a visible sheet edge. t is the sheet thickness in metres.",
      make: function (o) {
        var g = new THREE.Group(), r = lcg(o.seed * 31 + 7), geo = new THREE.BoxGeometry(o.w, o.t * 0.86, o.d), inst = new THREE.InstancedMesh(geo, M.paper, o.n), m4 = new THREE.Matrix4();
        for (var i = 0; i < o.n; i++) { m4.makeTranslation((r() - 0.5) * 0.0024, o.t * (i + 0.5), (r() - 0.5) * 0.0024); inst.setMatrixAt(i, m4); }
        inst.castShadow = inst.receiveShadow = true; g.add(inst);
        g.userData.top = o.t * o.n;
        return g;
      }
    });
    /* A STINGER: a copper water cooled torch body with a tungsten electrode ground to a point, hanging along -y from its
     * origin, so a frame places it by its tip. */
    K.define("electrode", {
      size: [0.03, 0.2, 0.03],
      options: { L: 0.2, tip: 0.012 },
      note: "An arc melting stinger: copper body, ceramic collar, tungsten electrode ground to a point, hanging from its origin.",
      make: function (o) {
        var g = new THREE.Group();
        var body = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.011, o.L, 32), M.copper); body.position.y = o.tip + 0.022 + o.L / 2; g.add(body);
        var collar = new THREE.Mesh(new THREE.CylinderGeometry(0.0058, 0.0098, 0.022, 32), M.steel); collar.position.y = o.tip + 0.011; g.add(collar);
        var rod = new THREE.Mesh(new THREE.CylinderGeometry(0.0016, 0.0016, o.tip, 16), M.tungsten); rod.position.y = o.tip / 2 + 0.002; g.add(rod);
        var pt = new THREE.Mesh(new THREE.ConeGeometry(0.0016, 0.004, 16), M.tungsten); pt.rotation.x = Math.PI; pt.position.y = 0.002; g.add(pt);
        g.userData.keepOrigin = true; return shade(g);
      }
    });
    /* A GRADUATED STEEL RULE standing on a foot, ticks ticks along its face. Drawn to illustrate a scale, never a reading. */
    K.define("steel_rule", {
      size: [0.03, 0.3, 0.02],
      options: { H: 0.3, ticks: 6 },
      note: "An upright satin steel rule on a cast foot with `ticks` engraved ticks evenly up its face.",
      make: function (o) {
        var g = new THREE.Group();
        var foot = TXT.roundedBox(0.06, 0.012, 0.05, 0.003, M.steelDark); foot.position.y = 0.006; g.add(foot);
        var bar = TXT.roundedBox(0.028, o.H, 0.004, 0.0008, M.steel); bar.position.y = 0.012 + o.H / 2; g.add(bar);
        for (var i = 1; i <= o.ticks; i++) { var t = new THREE.Mesh(new THREE.BoxGeometry(i % 2 === 0 ? 0.02 : 0.012, 0.0018, 0.0008), M.armJoint); t.position.set(-0.004, 0.012 + o.H * i / o.ticks - 0.004, 0.0022); g.add(t); }
        g.userData.keepOrigin = true; return shade(g);
      }
    });
  };

  /* ---- the frame plumbing, the same shape as the house chassis --------------------------- */
  N.glowTex = function (THREE) {
    var c = document.createElement("canvas"); c.width = c.height = 128; var x = c.getContext("2d"), g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
    g.addColorStop(0, "rgba(255,210,160,1)"); g.addColorStop(0.35, "rgba(224,149,106,0.55)"); g.addColorStop(1, "rgba(224,149,106,0)");
    x.fillStyle = g; x.fillRect(0, 0, 128, 128); var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  };
  /* THE COPPER'S OWN REFLECTION. A rasterised metal reflects only its environment, and the room's dark sky gave the
   * copper nothing to reflect, so it read as matte wood. This gives the copper (and only the copper) a dark studio with
   * ONE warm softbox placed where the camera's mirror ray off the top face lands, so the top carries one broad sweep.
   * dir is the direction of the softbox from the subject; the panel is sized by size, brightness by i. */
  N.copperEnv = function (THREE, R, dir, o) {
    o = o || {};
    var env = new THREE.Scene();
    env.add(new THREE.Mesh(new THREE.BoxGeometry(20, 14, 20), new THREE.MeshBasicMaterial({ color: 0x0a0a0d, side: THREE.BackSide })));
    var v = new THREE.Vector3(dir[0], dir[1], dir[2]).normalize().multiplyScalar(6);
    var box = new THREE.Mesh(new THREE.PlaneGeometry(o.w || 5, o.h || 3), new THREE.MeshBasicMaterial({ color: 0xffe2c0, side: THREE.DoubleSide }));
    box.material.color.multiplyScalar(o.i || 5); box.position.copy(v); box.lookAt(0, 0, 0); env.add(box);
    var fill = new THREE.Mesh(new THREE.PlaneGeometry(9, 2), new THREE.MeshBasicMaterial({ color: 0x3a2c22, side: THREE.DoubleSide }));
    fill.position.set(-v.x, 1.2, -v.z); fill.lookAt(0, 0, 0); env.add(fill);
    /* a low warm bounce in front and below, so a front face facing the camera is copper and not a black slab */
    var low = new THREE.Mesh(new THREE.PlaneGeometry(10, 3), new THREE.MeshBasicMaterial({ color: 0x6a4026, side: THREE.DoubleSide }));
    low.material.color.multiplyScalar(o.low == null ? 1.4 : o.low); low.position.set(0, -3.5, 5.5); low.lookAt(0, 0, 0); env.add(low);
    var pm = new THREE.PMREMGenerator(R.renderer), tex = pm.fromScene(env, 0.02).texture; pm.dispose();
    var M = N._M; [M.copper, M.copperDark].forEach(function (m) { if (m) { m.envMap = tex; m.envMapIntensity = o.k || 1; m.needsUpdate = true; } });
    return tex;
  };
  /* a point light for the glow of metal being made, so a hot button lights the copper around it */
  N.heat = function (THREE, R, p, i, dist) {
    var L = new THREE.PointLight(0xffa766, i == null ? 0.6 : i, dist || 0.5, 2); L.position.set(p[0], p[1], p[2]); L.castShadow = false; R.scene.add(L); return L;
  };
  /* THE LAB LAMP. At bench scale the declared key does not reach the bench through the room, so the room is lit by one
   * lamp hung ALONG THE DECLARED AZIMUTH, higher than the window key, so every cast still runs to the lower right. It is
   * the room's one source; the window is the seam behind it. */
  N.lamp = function (THREE, R, target, o) {
    o = o || {};
    var L = TXDECK.deck().light, a = L.az * Math.PI / 180, e = (o.el || 34) * Math.PI / 180, d = o.dist || 0.9;
    var sp = new THREE.SpotLight(0xffd6a8, o.i == null ? 6 : o.i, d * 3, o.angle || 0.42, 0.85, 1.6);
    sp.position.set(target[0] + d * Math.sin(a) * Math.cos(e), target[1] + d * Math.sin(e), target[2] + d * Math.cos(a) * Math.cos(e));
    sp.target.position.set(target[0], target[1], target[2]); R.scene.add(sp.target);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0002; sp.shadow.normalBias = 0.002; sp.shadow.radius = 4;
    sp.shadow.camera.near = 0.05; sp.shadow.camera.far = d * 3;
    R.scene.add(sp); return sp;
  };
  /* A BENCH SCALE CONTACT. TXT.contact marks the receiving surface at the scale of a yard, and on a bench a few
   * centimetres of footprint blacked the whole bench top, so a bench object takes this instead: a soft dark core sized
   * to its own footprint, laid on the surface it sits on. */
  N.contact = function (THREE, R, obj, o) {
    o = o || {};
    obj.updateMatrixWorld(true);
    var b = new THREE.Box3().setFromObject(obj), sz = b.getSize(new THREE.Vector3()), c = b.getCenter(new THREE.Vector3());
    if (!N._ctex) {
      var cv = document.createElement("canvas"); cv.width = cv.height = 128; var x = cv.getContext("2d"), g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
      g.addColorStop(0, "rgba(0,0,0,1)"); g.addColorStop(0.55, "rgba(0,0,0,0.55)"); g.addColorStop(1, "rgba(0,0,0,0)");
      x.fillStyle = g; x.fillRect(0, 0, 128, 128); N._ctex = new THREE.CanvasTexture(cv);
    }
    var pad = o.pad == null ? 1.25 : o.pad;
    var m = new THREE.Mesh(new THREE.PlaneGeometry(sz.x * pad, sz.z * pad), new THREE.MeshBasicMaterial({ map: N._ctex, transparent: true, opacity: o.opacity == null ? 0.75 : o.opacity, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }));
    m.rotation.x = -Math.PI / 2; m.position.set(c.x, (o.y != null ? o.y : b.min.y) + 0.0004, c.z); m.userData.noShadow = true; m.castShadow = m.receiveShadow = false;
    R.scene.add(m); return m;
  };
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.project = function (THREE, R, p) {
    var v = new THREE.Vector3(p[0], p[1], p[2]); v.project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  N.rigSpec = function (W, size, map) {
    var rim = Object.assign({}, W.rig.rim, { i: (W.rig.rim.i || 0.8) * 0.45 });
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { shadowSize: size || 2, mapSize: map || 2048 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 1.2, shadowFar: o.shadowFar || 2.6, normalBias: o.normalBias == null ? 0.004 : o.normalBias };
  };
  N.unacne = function (R, nb) { R.scene.traverse(function (l) { if (l.isDirectionalLight && l.castShadow) { l.shadow.normalBias = nb == null ? 0.004 : nb; l.shadow.bias = -0.0002; } }); return R; };
  N.warm = function (R, k) {
    R.scene.environmentIntensity = k == null ? 0.3 : k;
    if (!R._bounce) { R._bounce = new N.T.HemisphereLight(0x161a24, 0x4a3a30, N.BOUNCE); R.scene.add(R._bounce); }
    return R;
  };
  N.BOUNCE = 0.5;
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
  N.post = function (cx, o) {
    o = o || {};
    if (o.a !== 0) N.shade(cx, { a: o.a, to: o.to, fade: o.fade, pad: o.pad });
    var y0 = N.H - (o.veilH || 240), v = cx.createLinearGradient(0, y0, 0, N.H);
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(6,5,10," + (Math.min(0.5, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
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
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#08080B; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      "/* Manrope and Fraunces contextual alternates curl a straight apostrophe after some letters (no. 61, no. 62), so calt is off on every line of type */",
      ".hook, .dek, .lab, .kick, .count, .src { font-feature-settings:\"calt\" 0; }",
      ".hook, .dek, .kick, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }",
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
                           tone: W.tone, fov: o.fov || 32, near: o.near || 0.005, far: o.far || 400 });
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

  global.CH = N;
})(this);
