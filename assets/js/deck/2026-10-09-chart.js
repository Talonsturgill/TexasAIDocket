/* deck/2026-10-09-chart.js — the chassis for the 2026-10-09 deck: UTMB says OpenEvidence, an AI that
 * answers clinical questions with citations, sits inside its electronic health record and that more
 * than half of its clinicians use it (tx-2026-0208).
 *
 * THE WORLD. floodlit, a pad at night under one cold LED flood: a black sky, the key high on camera
 * left at az -50 and el 40, so every lit face is the north west face and every cast runs to the south
 * east, short and crisp at the foot. It is the light a hospital's ambulance apron has at three in the
 * morning, and it is the colour of a screen, so the key on the cart and the light of the answer are
 * one family. Indoors the same flood comes through the window and the back wall stays in shadow.
 *
 * DIRECTIONS. +x is east, +z is south. az runs clockwise from +z toward +x, so the key sits at
 * (sin az, ., cos az), north west of the subject and high.
 *
 * THE HERO OBJECT. `workstation_cart`, the rolling clinical workstation a clinician pushes from room
 * to room: a five caster base, an oval mast with its battery, a grey work surface with a push bar, a
 * keyboard tray, a badge reader, a holstered scanner, and one 24 inch monitor on a swivel arm at a
 * standing eye. It is built in the kit's conventions so Phase 17 can lift it into assets/js/kit/
 * unchanged. It is ILLUSTRATIVE: no maker, no label, no legible screen. Its STATE carries the deck:
 * `yaw` is the monitor's swivel, 0 with the screen facing the push handle (the clinician, +z) and 180
 * with it facing whoever stands in front of the cart.
 *
 * THE KIT MODEL THIS DECK BUILDS, the kit having no clinical cart: `workstation_cart`, below.
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, written in the frame's code where figure_bearing.py
 * checks them against figures.json. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("chart.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "chart",
    light: { az: -50, el: 40 },
    sky: { preset: "floodlit", haze: 0x0e1220 },
    ground: "#0C0D11",
    material: "#D9DBD6",
    accent: "#E3A83B",
    grade: {
      exposure: 0,
      saturation: 1.03,
      contrast: 1.08,
      filmic: true,
      lift: [0.003, 0.004, 0.008],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.8, strength: 0.3, radius: 14 },
      grain: { amount: 0.02, size: 2, seed: 20261009 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261009;
  N.ACCENT = 0xe3a83b;       /* badge amber, the deck's one accent: what the record prints and a reader can point to */
  N.INK = "#EEF1F2";
  N.SCREEN = 0xdfeaf2;       /* a cool clinical white, the screen's own light */

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---------------------------------------------------------------- the screen */
  /* THE ANSWER ON THE SCREEN, painted once: a question in a bubble at the top, an answer of grey
   * text bars under it with small raised citation chips at the ends of its lines, and a list of
   * sources at the foot, each a chip and two grey bars. No word, no letter, no numeral is legible,
   * because the deck never shows a real product's UI. A cool clinical white page. */
  N.screenTex = function (THREE, o) {
    o = o || {}; var key = "scr" + (o.seed || 1) + (o.blank ? "b" : "");
    N._scr = N._scr || {}; if (N._scr[key]) return N._scr[key];
    var c = document.createElement("canvas"); c.width = 1280; c.height = 768; var x = c.getContext("2d"), r = lcg(o.seed || 5);
    x.fillStyle = "#f2f5f7"; x.fillRect(0, 0, 1280, 768);
    x.fillStyle = "#e3e8ec"; x.fillRect(0, 0, 1280, 54); x.fillStyle = "#c9d1d8"; x.fillRect(0, 54, 1280, 3);
    x.fillStyle = "#e9edf0"; x.fillRect(0, 57, 210, 711); x.fillStyle = "#d4dbe0"; x.fillRect(210, 57, 3, 711);
    for (var s = 0; s < 9; s++) { x.fillStyle = s === 2 ? "#b9c4cc" : "#d0d7dc"; x.fillRect(22, 92 + s * 58, 160 - (s * 17 % 60), 16); }
    if (!o.blank) {
      /* the question, right aligned in a soft bubble */
      x.fillStyle = "#d9e2e8"; rr(x, 640, 86, 580, 70, 18); x.fill();
      x.fillStyle = "#8a96a0"; x.fillRect(668, 108, 470, 11); x.fillRect(668, 128, 300, 11);
      /* the answer: lines of grey bars, each paragraph ending in a citation chip */
      var y = 192, paras = [5, 4, 5, 3];
      paras.forEach(function (n, pi) {
        for (var l = 0; l < n; l++) {
          var w = l === n - 1 ? 380 + r() * 300 : 860 + r() * 120;
          x.fillStyle = "#5b6670"; x.fillRect(250, y, w, 12);
          if (l === n - 1) { x.fillStyle = "#3d6f9e"; rr(x, 262 + w, y - 4, 30, 20, 6); x.fill(); if (pi % 2 === 0) { rr(x, 298 + w, y - 4, 30, 20, 6); x.fill(); } }
          y += 26;
        }
        y += 22;
      });
      /* the sources list */
      x.fillStyle = "#c9d1d8"; x.fillRect(250, y, 980, 2); y += 22;
      for (var k = 0; k < 4; k++) { x.fillStyle = "#3d6f9e"; rr(x, 250, y - 3, 30, 20, 6); x.fill(); x.fillStyle = "#6b7680"; x.fillRect(296, y, 520 + r() * 300, 11); x.fillStyle = "#a3adb5"; x.fillRect(296, y + 18, 360 + r() * 200, 9); y += 44; }
    }
    /* a faint glass falloff toward the corners */
    var g = x.createRadialGradient(640, 384, 200, 640, 384, 820); g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(1, "rgba(20,30,40,0.18)");
    x.fillStyle = g; x.fillRect(0, 0, 1280, 768);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    N._scr[key] = t; return t;
  };
  function rr(x, X, Y, w, h, r) { x.beginPath(); x.moveTo(X + r, Y); x.arcTo(X + w, Y, X + w, Y + h, r); x.arcTo(X + w, Y + h, X, Y + h, r); x.arcTo(X, Y + h, X, Y, r); x.arcTo(X, Y, X + w, Y, r); x.closePath(); }

  /* POWDER COAT: an off-white satin with the scuffs a cart picks up against door frames, lighter
   * rubbing on the edges, a few dark nicks and a faint grime toward the bottom of a part. */
  N.coatTex = function (THREE) {
    if (N._coat) return N._coat;
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(17);
    x.fillStyle = "#dcded9"; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 700; i++) { var v = r() < 0.5 ? "120,122,118" : "255,255,255"; x.fillStyle = "rgba(" + v + "," + (0.015 + r() * 0.025).toFixed(3) + ")"; x.fillRect(r() * 512, r() * 512, 4 + r() * 40, 2 + r() * 8); }
    x.lineWidth = 1.2; for (var k = 0; k < 70; k++) { var px = r() * 512, py = r() * 512, a = (r() - 0.5) * 0.6; x.strokeStyle = "rgba(90,92,88," + (0.12 + r() * 0.2).toFixed(2) + ")"; x.beginPath(); x.moveTo(px, py); x.lineTo(px + Math.cos(a) * (8 + r() * 40), py + Math.sin(a) * (8 + r() * 40)); x.stroke(); }
    for (var n = 0; n < 12; n++) { x.fillStyle = "rgba(60,60,58," + (0.12 + r() * 0.18).toFixed(2) + ")"; x.beginPath(); x.arc(r() * 512, r() * 512, 0.6 + r() * 1.2, 0, 7); x.fill(); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    N._coat = t; return t;
  };

  /* ---------------------------------------------------------------- the kit model this deck builds */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.workstation_cart) return;
    var coat = K.mat("ch-coat", { color: 0xffffff, map: N.coatTex(THREE), roughness: 0.46, metalness: 0.12 });
    var abs = K.mat("ch-abs", { color: 0x7c8084, roughness: 0.6, metalness: 0.02 });
    var absDark = K.mat("ch-absd", { color: 0x2a2c2f, roughness: 0.55, metalness: 0.02 });
    var housing = K.mat("ch-hous", { color: 0xc4c8cc, roughness: 0.38, metalness: 0.06 });   /* a medical grade monitor in a light grey housing, so its back reads against the night */
    var alu = K.mat("ch-alu", { color: 0xb9bdc1, roughness: 0.32, metalness: 0.85 });
    var castAlu = K.mat("ch-cast", { color: 0x9a9ea2, roughness: 0.5, metalness: 0.7 });
    var rubber = K.finish.rubber(), chrome = K.finish.chrome();
    var keyM = K.mat("ch-key", { color: 0x2e3033, roughness: 0.62, metalness: 0.02 });
    var bezel = K.mat("ch-bez", { color: 0x0b0c0d, roughness: 0.18, metalness: 0.1 });

    K.define("workstation_cart", {
      size: [0.66, 1.6, 0.7],
      options: { yaw: 0, height: 1.0, lit: true, screen: "answer", trayOut: 0.1, badge: "idle", seed: 1 },
      note: "Rolling clinical workstation, illustrative and unmarked: five caster cast aluminium star base, oval mast with a battery pack, a grey work surface (height m, default 1.0) with a front push bar, a keyboard tray (trayOut m), a badge reader (badge idle|ok), a holstered scanner and a wipes canister, and a 24 in monitor on a swivel arm. yaw is the monitor's swivel in degrees, 0 with the screen facing the push handle on +z, 180 facing -z. screen answer|blank|off; no legible text.",
      make: function (o, r) {
        var g = new THREE.Group(), H = o.height || 1.0;
        /* the base: a five spoke star on twin wheel casters */
        K.cyl(0.07, 0.08, 0.06, castAlu, 0, 0.075, 0, 28, g);
        for (var i = 0; i < 5; i++) {
          var a = i / 5 * Math.PI * 2 + 0.31, ex = Math.cos(a) * 0.29, ez = Math.sin(a) * 0.29;
          var sp = K.bar([0, 0.1, 0], [ex, 0.085, ez], 0.022, castAlu, 10, g); sp.scale.set(1.3, 1, 0.75);
          K.cyl(0.018, 0.018, 0.022, castAlu, ex, 0.07, ez, 16, g);                              /* the caster's swivel stem */
          var fork = K.box(0.034, 0.05, 0.06, absDark, ex, 0.035, ez, 0.006, g); fork.rotation.y = -a;
          [-1, 1].forEach(function (sd) {
            var w = new THREE.Mesh(new THREE.CylinderGeometry(0.048, 0.048, 0.02, 24), rubber);
            w.rotation.z = Math.PI / 2; w.rotation.y = -a + Math.PI / 2;
            w.position.set(ex + Math.cos(a + Math.PI / 2) * sd * 0.024, 0.048, ez + Math.sin(a + Math.PI / 2) * sd * 0.024); g.add(w);
            var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.022, 16), castAlu); hub.rotation.copy(w.rotation); hub.position.copy(w.position); g.add(hub);
          });
          if (i % 2 === 0) K.box(0.03, 0.008, 0.035, K.mat("ch-lock", { color: 0x3a3c3e, roughness: 0.5 }), ex, 0.094, ez, 0.003, g);   /* a lock pedal */
        }
        /* the mast: a lower gas spring sleeve and the oval column */
        var sleeve = K.cyl(0.055, 0.058, 0.44, coat, 0, 0.1, 0, 32, g); sleeve.scale.z = 0.72;
        var col = K.cyl(0.044, 0.044, H - 0.56, alu, 0, 0.52, 0, 32, g); col.scale.z = 0.7;
        /* the battery pack on the back of the mast, with its five segment level strip */
        K.box(0.26, 0.32, 0.11, coat, 0, 0.18, -0.105, 0.014, g);
        K.box(0.2, 0.012, 0.004, K.mat("ch-strip", { color: 0x111111, roughness: 0.4 }), 0, 0.44, -0.162, 0, g);
        for (var b = 0; b < 5; b++) K.box(0.032, 0.008, 0.003, K.finish.lamp(b < 4 ? 0x7dff9a : 0x222222, b < 4 ? 1.6 : 0.1), -0.075 + b * 0.0375, 0.442, -0.1635, 0, g);
        /* the power cord wound on two hooks behind the mast */
        K.box(0.02, 0.05, 0.03, absDark, -0.06, 0.62, -0.05, 0.004, g); K.box(0.02, 0.05, 0.03, absDark, 0.06, 0.62, -0.05, 0.004, g);
        for (var cw = 0; cw < 4; cw++) K.cable([-0.07, 0.66 - cw * 0.006, -0.065], [0.07, 0.66 - cw * 0.006, -0.065], 0.07 + cw * 0.012, 0.0045, absDark, g);
        /* the head: a drawer and keyboard tray under the work surface */
        K.box(0.44, 0.07, 0.36, coat, 0, H - 0.1, 0.02, 0.01, g);
        K.box(0.4, 0.008, 0.004, absDark, 0, H - 0.07, 0.202, 0, g);                                  /* the drawer pull recess */
        var trayZ = 0.05 + (o.trayOut || 0);
        K.box(0.56, 0.016, 0.3, abs, 0, H - 0.145, trayZ, 0.006, g);
        K.box(0.44, 0.018, 0.14, absDark, 0, H - 0.129, trayZ + 0.02, 0.006, g);
        var keyGeo = new THREE.BoxGeometry(0.0155, 0.007, 0.0155), list = [];
        for (var row = 0; row < 5; row++) for (var col2 = 0; col2 < 15; col2++) list.push([-0.2 + col2 * 0.0285 + (row % 2) * 0.006, H - 0.107, trayZ + 0.07 - row * 0.024, 0, 1]);
        var keys = K.instances(keyGeo, keyM, list, g); keys.castShadow = true;
        var mouse = new THREE.Mesh(new THREE.SphereGeometry(0.03, 20, 12), absDark); mouse.scale.set(0.95, 0.42, 1.6); mouse.position.set(0.245, H - 0.122, trayZ + 0.02); g.add(mouse);
        /* the work surface, a grey tray with a lip, and the push bar along its front */
        K.box(0.6, 0.032, 0.46, abs, 0, H - 0.032, 0, 0.012, g);
        K.box(0.6, 0.014, 0.012, abs, 0, H, -0.224, 0.005, g); K.box(0.012, 0.014, 0.44, abs, -0.294, H, 0, 0.005, g); K.box(0.012, 0.014, 0.44, abs, 0.294, H, 0, 0.005, g);
        K.bar([-0.27, H - 0.012, 0.29], [0.27, H - 0.012, 0.29], 0.0125, chrome, 18, g);
        K.bar([-0.25, H - 0.012, 0.29], [-0.25, H - 0.012, 0.225], 0.009, chrome, 12, g); K.bar([0.25, H - 0.012, 0.29], [0.25, H - 0.012, 0.225], 0.009, chrome, 12, g);
        /* the badge reader on the front right corner, its LED, and a badge on a reel */
        K.box(0.07, 0.024, 0.11, absDark, 0.22, H, 0.15, 0.008, g);
        K.box(0.008, 0.003, 0.008, K.finish.lamp(o.badge === "ok" ? 0x4dff7a : 0xffa63d, 2.2), 0.24, H + 0.024, 0.19, 0, g);
        /* the scanner in its holster on the right side, the wipes on the left */
        K.box(0.05, 0.12, 0.08, absDark, 0.33, H - 0.17, 0.02, 0.006, g);
        K.box(0.034, 0.14, 0.04, K.mat("ch-scan", { color: 0x3a3d40, roughness: 0.5 }), 0.335, H - 0.1, 0.02, 0.008, g);
        K.box(0.05, 0.05, 0.1, K.mat("ch-scan", { color: 0x3a3d40, roughness: 0.5 }), 0.335, H + 0.03, 0.04, 0.01, g);
        var wipes = K.cyl(0.04, 0.04, 0.17, K.mat("ch-wipe", { color: 0xe8ebec, roughness: 0.4 }), -0.335, H - 0.2, 0.0, 24, g);
        K.cyl(0.042, 0.042, 0.025, K.mat("ch-lid", { color: 0x7a8a9a, roughness: 0.4 }), -0.335, H - 0.03, 0.0, 24, g);
        K.box(0.03, 0.17, 0.09, coat, -0.31, H - 0.2, 0, 0.004, g);
        /* the monitor post at the back of the surface, the swivel and the screen */
        K.cyl(0.022, 0.022, 0.26, alu, 0, H, -0.16, 20, g);
        var head = new THREE.Group(); head.position.set(0, H + 0.26, -0.16); head.rotation.y = (o.yaw || 0) * Math.PI / 180; g.add(head);
        var knuckle = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.05, 20), alu); head.add(knuckle);
        var arm = K.box(0.04, 0.03, 0.12, alu, 0, -0.015, 0.06, 0.008, head); arm.position.y = 0;
        var sw = 0.531, sh = 0.299, mon = new THREE.Group(); mon.position.set(0, 0.17, 0.13); mon.rotation.x = -0.07; head.add(mon);
        mon.add(TXT.roundedBox(sw + 0.024, sh + 0.04, 0.022, 0.006, housing));
        var rear = TXT.roundedBox(sw * 0.66, sh * 0.7, 0.05, 0.022, housing); rear.position.z = -0.03; mon.add(rear);
        for (var v = 0; v < 9; v++) { var slot = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.004, 0.003), bezel); slot.position.set(-0.08, -0.06 + v * 0.012, -0.0565); mon.add(slot); var s2 = slot.clone(); s2.position.x = 0.08; mon.add(s2); }
        var vesa = TXT.roundedBox(0.11, 0.11, 0.03, 0.008, alu); vesa.position.set(0, 0, -0.06); mon.add(vesa);
        var bz = new THREE.Mesh(new THREE.PlaneGeometry(sw + 0.006, sh + 0.006), bezel); bz.position.set(0, 0.004, 0.0115); mon.add(bz);
        if (o.screen !== "off") {
          /* the screen lights only itself and takes no light: an unlit material, so a lamp in front of it
           * can never print a specular hotspot on the page (the probe of 2026-10-09 did) */
          var scrM = new THREE.MeshBasicMaterial({ map: N.screenTex(THREE, { blank: o.screen === "blank", seed: o.seed || 5 }), toneMapped: true, fog: false });
          scrM.color.setScalar(o.lit === false ? 0.04 : (o.glow || 1.0));
          var scr = new THREE.Mesh(new THREE.PlaneGeometry(sw, sh), scrM); scr.position.set(0, 0.006, 0.0118); scr.castShadow = false; mon.add(scr);
          scr.userData.txWear = false; scr.userData.screen = true;
          /* THE LEAK: a thin cool backlight just larger than the housing, set inside it, so a lit screen shows a rim of
           * light round the housing's edges from behind as well as a halo round the bezel from the front */
          if (o.lit !== false) {
            var lk = new THREE.Mesh(new THREE.PlaneGeometry(sw + 0.036, sh + 0.052), new THREE.MeshBasicMaterial({ color: new THREE.Color(0xdfeaf2).multiplyScalar(0.55 * (o.glow || 1.0)), side: THREE.DoubleSide, fog: false }));
            lk.position.set(0, 0.004, -0.004); lk.castShadow = false; lk.userData.txWear = false; mon.add(lk);
          }
        }
        var led = new THREE.Mesh(new THREE.CircleGeometry(0.0018, 12), K.finish.lamp(0xffffff, 1.4)); led.position.set(sw / 2 - 0.02, -sh / 2 - 0.008, 0.0118); mon.add(led);
        g.userData.screenAt = function () { var p = new THREE.Vector3(); mon.getWorldPosition(p); return [p.x, p.y, p.z]; };
        g.userData.monitor = mon;
        return g;
      }
    });
  };

  /* `galv_column`, a measured exhibit: a square hot dip galvanized steel tube standing on a bolted base
   * plate, `height` m tall, with a weld bead ring at each height in `welds` and `bands` clamp bands
   * spaced evenly between `bandFrom` and the top. Spangle in the zinc, a rust bloom and grime at the
   * plate. Used where a frame sets an amount as a length at one scale; the frame computes the height. */
  N.installColumn = function (K, THREE, TXT) {
    if (K.registry.galv_column) return;
    var zinc = K.mat("ch-zinc", { color: 0xffffff, map: N.zincTex(THREE), roughness: 0.38, metalness: 0.82 });
    var plateM = K.mat("ch-plate", { color: 0x8d9194, roughness: 0.55, metalness: 0.7 });
    var bead = K.mat("ch-bead", { color: 0x6f7376, roughness: 0.6, metalness: 0.6 });
    var bandM = K.mat("ch-band", { color: 0xb8bcbf, roughness: 0.3, metalness: 0.9 });
    K.define("galv_column", {
      size: [0.9, 4, 0.9],
      options: { height: 4, width: 0.45, welds: [], bands: 0, bandFrom: 0, seed: 1 },
      note: "A square galvanized steel tube on a bolted base plate, height m, width m, weld rings at `welds` heights, `bands` clamp bands spaced evenly from `bandFrom` to the top. A measured exhibit for a length at one scale.",
      make: function (o) {
        var g = new THREE.Group(), w = o.width || 0.45, h = o.height || 4;
        K.box(0.9, 0.025, 0.9, plateM, 0, 0, 0, 0.006, g);
        [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(function (p) { K.cyl(0.022, 0.022, 0.05, bead, p[0] * 0.36, 0.025, p[1] * 0.36, 12, g); });
        K.box(w, h - 0.025, w, zinc, 0, 0.025, 0, 0.012, g);
        K.box(w + 0.01, 0.012, w + 0.01, plateM, 0, h - 0.006, 0, 0.004, g);           /* the cap plate */
        (o.welds || []).forEach(function (y) { K.box(w + 0.03, 0.05, w + 0.03, bead, 0, y - 0.025, 0, 0.012, g); });
        var n = o.bands || 0;
        /* `bands` sleeves, each a clamp 0.3 m tall, centred in n equal spans from `bandFrom` to the cap, so a reader counts n objects */
        for (var i = 0; i < n; i++) { var y = o.bandFrom + (h - o.bandFrom) * (i + 0.5) / n; K.box(w + 0.05, 0.3, w + 0.05, bandM, 0, y - 0.15, 0, 0.012, g); for (var bb = 0; bb < 2; bb++) K.cyl(0.018, 0.018, 0.06, bead, (w / 2 + 0.03) * (bb ? 1 : -1), y - 0.03, 0, 10, g).rotation.set(0, 0, Math.PI / 2); }
        return g;
      }
    });
  };
  /* `precast_barrier`, the bench frames 4 and 5 set their figures on: a precast concrete parking barrier
   * lying along x on the apron, its front face (+z) cut by three cast channels running its length, each
   * exactly `length` m from userData.channel(i).x0, index 0 the top one. A cast tick on the face's lips at the
   * channels' start and at `tick` of their length (0.5 by default). Chipped arrises, the aggregate in the
   * face. A frame fills a channel with N.channelFill, which takes a length the frame computed. */
  N.installKerb = function (K, THREE, TXT) {
    if (K.registry.precast_barrier) return;
    var conc = K.mat("ch-conc", { color: 0xffffff, map: N.concTex(THREE), roughness: 0.86, metalness: 0.0 });
    var chan = K.mat("ch-chan", { color: 0x2c2d2b, roughness: 0.94, metalness: 0.0 });
    var tickM = K.mat("ch-tick", { color: 0x141514, roughness: 0.9, metalness: 0.0 });
    K.define("precast_barrier", {
      size: [4.4, 0.8, 0.5],
      options: { length: 4, height: 0.8, depth: 0.5, channel: 0.16, tick: 0.5, seed: 3 },
      note: "A precast concrete barrier lying along x, three cast channels along its front face (+z, index 0 the top one), each `length` m long from x = -length/2, a cast tick on the face at the start and at `tick` of the length. userData.channel(i) gives the channel's local start, bottom, depth centre and size.",
      make: function (o) {
        var g = new THREE.Group(), L = o.length || 4, Hk = o.height || 0.8, D = o.depth || 0.5;
        var Lt = L + 0.36, gh = o.channel || 0.16, gd = 0.06, n = 3, lip = (Hk - n * gh) / (n + 1);
        /* built centred on its own bounds, because K.make recentres a model's children on its bounding box and
         * a fill added afterwards would land off the cast tick by the offset (no. 47's first build drew the
         * solid 0.12 m past the half tick that way) */
        var x0 = -Lt / 2 + 0.06, xc = 0;
        var zf = D / 2 - gd / 2;                                           /* the depth centre of the face layer */
        K.box(Lt, Hk, D - gd, conc, xc, 0, -gd / 2, 0.02, g);                /* the body behind the channels */
        var ys = [];
        for (var k = 0; k <= n; k++) {
          var yb = k * (lip + gh);                                          /* the lips, from the foot up */
          K.box(Lt, lip, gd, conc, xc, yb, zf, 0.01, g);
          if (k < n) ys.unshift(yb + lip);                                  /* channel bottoms, top one first */
        }
        ys.forEach(function (y) {
          K.box(0.06, gh, gd, conc, x0 - 0.03, y, zf, 0.004, g);            /* the channel's closed start */
          var tail = Lt - L - 0.06; K.box(tail, gh, gd, conc, x0 + L + tail / 2, y, zf, 0.004, g);
          K.box(L, gh, 0.004, chan, x0 + L / 2, y, D / 2 - gd + 0.002, 0, g);   /* the channel's dark back */
        });
        [0, o.tick == null ? 0.5 : o.tick].forEach(function (t) {
          for (var k2 = 0; k2 <= n; k2++) K.box(0.016, lip - 0.02, 0.004, tickM, x0 + L * t, k2 * (lip + gh) + 0.01, D / 2 + 0.002, 0, g);
        });
        g.userData.channel = function (i) { return { x0: x0, y: ys[i], z: zf, h: gh, d: gd, length: L }; };
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });
  };
  /* FILL A CHANNEL from `from` to `to` m along it, `kind` amber (the record's accent, a cast resin) or
   * alu (a brushed aluminium bar standing proud of the face). `fade` m past `to` as one block whose alpha falls to nothing, open,
   * with no end cap, for a figure whose end is not published. */
  N.channelFill = function (kerb, i, from, to, o) {
    o = o || {};
    var THREE = N.T, K = N.K, c = kerb.userData.channel(i), g = new THREE.Group(), alu = o.kind === "alu";
    var mk = function (op) {
      return alu ? K.mat("ch-bar", { color: 0xe6e9ec, roughness: 0.3, metalness: 0.55 })
                 : new THREE.MeshBasicMaterial({ color: 0xE3A83B, toneMapped: false, transparent: op < 1, opacity: op, depthWrite: op >= 1 });   /* the record's accent as printed: unlit, so the flood can't bleach it */
    };
    var h = alu ? c.h - 0.03 : c.h - 0.008, d = alu ? c.d + 0.03 : c.d - 0.006, y = c.y + (c.h - h) / 2, z = c.z + (alu ? 0.015 : -0.002);
    K.box(to - from, h, d, mk(1), c.x0 + (from + to) / 2, y, z, alu ? 0.008 : 0.002, g);
    var f = o.fade || 0;
    if (f > 0) {
      /* the open end: one block whose alpha runs from the fill's own to nothing, smooth, no end cap */
      var fc = document.createElement("canvas"); fc.width = 256; fc.height = 4; var fx = fc.getContext("2d"), fg = fx.createLinearGradient(0, 0, 256, 0);
      for (var q = 0; q <= 10; q++) { var e = 0.72 * (1 - q / 10);   /* the fade starts a visible step below the solid, so the solid end reads exactly at `to` */ fg.addColorStop(q / 10, "rgb(" + Math.round(255 * e * e) + "," + Math.round(255 * e * e) + "," + Math.round(255 * e * e) + ")"); }
      fx.fillStyle = fg; fx.fillRect(0, 0, 256, 4);
      var fm = mk(0.99); fm.alphaMap = new THREE.CanvasTexture(fc); fm.transparent = true; fm.depthWrite = false;
      K.box(f, h, d, fm, c.x0 + to + f / 2, y, z, 0, g);
    }
    kerb.add(g); return g;
  };
  N.concTex = function (THREE) {
    if (N._conc) return N._conc;
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(41);
    x.fillStyle = "#8f908c"; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 4200; i++) { var v = 110 + Math.floor(r() * 90); x.fillStyle = "rgba(" + v + "," + v + "," + (v - 4) + "," + (0.25 + r() * 0.35).toFixed(2) + ")"; x.beginPath(); x.arc(r() * 512, r() * 512, 0.6 + r() * 2.2, 0, 7); x.fill(); }
    for (var j = 0; j < 40; j++) { x.fillStyle = "rgba(40,40,38," + (0.06 + r() * 0.1).toFixed(2) + ")"; x.beginPath(); x.arc(r() * 512, r() * 512, 2 + r() * 6, 0, 7); x.fill(); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(9, 2); t.anisotropy = 8;
    N._conc = t; return t;
  };
  N.zincTex = function (THREE) {
    if (N._zinc) return N._zinc;
    var c = document.createElement("canvas"); c.width = c.height = 512; var x = c.getContext("2d"), r = lcg(29);
    x.fillStyle = "#b9bdc0"; x.fillRect(0, 0, 512, 512);
    for (var i = 0; i < 260; i++) { var v = 150 + Math.floor(r() * 80); x.fillStyle = "rgba(" + v + "," + (v + 2) + "," + (v + 4) + ",0.35)"; x.beginPath(); var cx0 = r() * 512, cy0 = r() * 512, rad = 8 + r() * 30; for (var k = 0; k < 7; k++) { var a = k / 7 * Math.PI * 2; x.lineTo(cx0 + Math.cos(a) * rad * (0.7 + r() * 0.5), cy0 + Math.sin(a) * rad * (0.7 + r() * 0.5)); } x.fill(); }
    for (var j = 0; j < 30; j++) { x.fillStyle = "rgba(90,70,50," + (0.05 + r() * 0.08).toFixed(2) + ")"; x.fillRect(r() * 512, 420 + r() * 92, 2 + r() * 20, 2 + r() * 30); }
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    N._zinc = t; return t;
  };
  /* PLACE A DOM LABEL beside a world point: projects [x, y, z] through the frame's camera and sets the
   * element's left and top, offset by dx, dy px, so a label lands on the thing it names. */
  N.labelAt = function (id, p, dx, dy) {
    var s = N.project(N.T, N.R, p), el = document.getElementById(id);
    el.style.left = Math.round(s[0] + (dx || 0)) + "px"; el.style.top = Math.round(s[1] + (dy || 0)) + "px";
    return s;
  };

  /* ---------------------------------------------------------------- the place, as primitives */
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.cart = function (o) { return N.K.make("workstation_cart", Object.assign({ seed: 5 }, o || {})); };
  /* THE SCREEN'S OWN LIGHT. An emissive lights only itself, so a frame that wants the answer to fall
   * on a surface puts a soft, cool rect light at the screen, aimed the way the screen faces. */
  N.screenLight = function (cart, o) {
    o = o || {}; var T = N.T, mon = cart.userData.monitor; if (!mon) return null;
    var L = new T.PointLight(N.SCREEN, (o.i || 1.2) * 10, o.range || 3.2, 2);
    cart.updateMatrixWorld(true); var p = new T.Vector3(0, 0, 0.25).applyMatrix4(mon.matrixWorld);
    L.position.copy(p); L.castShadow = false; N.R.scene.add(L); return L;
  };
  /* THE FLOOD, the stage's pool made real: one cold LED flood on a pole, aimed at `target`, placed
   * along the declared key's azimuth so its casts agree with the deck's sun. */
  N.flood = function (target, o) {
    o = o || {}; var T = N.T, az = -50 * Math.PI / 180, el = (o.el || 50) * Math.PI / 180, d = o.dist || 9;
    var s = new T.SpotLight(o.color || 0xe8eef2, o.intensity || 900, o.range || 0, o.angle || 0.5, o.penumbra == null ? 0.7 : o.penumbra, 2);
    s.position.set(target[0] + Math.sin(az) * Math.cos(el) * d, target[1] + Math.sin(el) * d, target[2] + Math.cos(az) * Math.cos(el) * d);
    s.target.position.set(target[0], target[1] || 0, target[2]);
    s.castShadow = true; s.shadow.mapSize.set(2048, 2048); s.shadow.bias = -0.0003; s.shadow.normalBias = 0.02;
    N.R.scene.add(s); N.R.scene.add(s.target); return s;
  };
  /* THE COAST, the flat land around the apron: a big grass ground, with the concrete apron laid on it */
  N.coast = function (o) { o = o || {}; return N.TXT.ground(N.R, { surface: "grass", size: o.size || 12000, tile: o.tile || 6, seed: o.seed || 23, color: o.color || 0x4c5038 }); };
  N.apron = function (x, z, w, d, o) { o = o || {}; var g = N.TXT.ground(N.R, { surface: "concrete", size: Math.max(w, d), tile: o.tile || 4.5, seed: o.seed || 19, joints: true, y: 0.03 }); g.position.x = x; g.position.z = z; g.scale.set(w / Math.max(w, d), 1, d / Math.max(w, d)); return g; };
  N.grass = function (area, o) { o = o || {}; return N.TXT.scatter(N.R, { kind: "grass", count: o.count || 6000, area: area, avoid: o.avoid, seed: o.seed || 9, scale: o.scale || [0.25, 0.5], colors: [0x6e7048, 0x5a5c3c, 0x7d7a48] }); };
  /* THE REGION'S LIGHTS ON THE HORIZON: `n` small amber points across the flat land the camera looks
   * over, placed for the drawing on bearings inside the frame and at distances from `near` to `far`
   * metres. Each is sized to hold about the same few pixels whatever its distance, unfogged, so the
   * row reads as many places rather than one glow. Deterministic by seed. */
  N.clinicLights = function (from, look, n, o) {
    o = o || {}; var T = N.T, r = lcg(o.seed || 31), lists = [[], [], []], half = (o.spread || 16) * Math.PI / 180;
    var bearing = Math.atan2(look[0] - from[0], look[2] - from[2]), near = o.near || 900, far = o.far || 7000;
    for (var i = 0; i < n; i++) {
      /* evenly across the frame's width with a little jitter, so the row reads as many places and never as a dashed rule */
      var b = bearing + ((i + 0.5) / n - 0.5) * 2 * half + (r() - 0.5) * (1.6 * half / n), d = near + Math.pow(r(), 0.7) * (far - near);
      var k = r() < 0.25 ? 0 : (r() < 0.6 ? 1 : 2);
      lists[k].push([from[0] + Math.sin(b) * d, (o.y || 2) + r() * d * 0.0022, from[2] + Math.cos(b) * d, 0, d * (o.size || 0.0014) * (0.8 + r() * 0.5)]);
    }
    var glows = [1.5, 1.0, 0.62], out = [];
    lists.forEach(function (list, k) {
      if (!list.length) return;
      var mat = new T.MeshBasicMaterial({ color: new T.Color(N.ACCENT).multiplyScalar((o.glow || 1.1) * glows[k]), fog: false, toneMapped: false });
      var im = N.K.instances(new T.SphereGeometry(1, 10, 8), mat, list); im.castShadow = false; im.receiveShadow = false; im.userData.txWear = false;
      N.R.scene.add(im); out.push(im);
    });
    /* THE LAND LINE under them: a faint band of the coast's own dark, lit just enough to read as ground at the horizon */
    if (o.land !== false) {
      var lm = new T.Mesh(new T.PlaneGeometry(2 * far * Math.tan(half * 1.6), 1), new T.MeshBasicMaterial({ color: 0x1a1d24, fog: false, toneMapped: true }));
      lm.position.set(from[0] + Math.sin(bearing) * far * 0.98, 0.5, from[2] + Math.cos(bearing) * far * 0.98); lm.rotation.y = bearing + Math.PI; lm.scale.y = far * 0.004;
      N.R.scene.add(lm); out.push(lm);
    }
    out.points = lists[0].concat(lists[1], lists[2]);   /* every light's world position, so a frame can count the ones it shows */
    return out;
  };
  N.accentMat = function (THREE, glow) { return new THREE.MeshStandardMaterial({ color: N.ACCENT, emissive: N.ACCENT, emissiveIntensity: glow == null ? 0.25 : glow, roughness: 0.5, metalness: 0.05 }); };
  N.installAll = function () { N.installKit(N.K, N.T, N.TXT); };

  /* ---------------------------------------------------------------- the frame shell */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 12, mapSize: map || 2048, radius: 5 }) });
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
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = "5,6,10";
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
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(5,6,10," + (Math.min(0.5, o.veil == null ? 0.38 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 2.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#DDE2E4", halo = "rgba(3,4,8,0.6)", halo2 = "rgba(3,4,8,0.45)", acc = "#" + ("000000" + N.ACCENT.toString(16)).slice(-6).toUpperCase();
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#0C0D11; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; color:' + ink + '; white-space:nowrap; z-index:12; }',
      '.lab.acc { color:' + acc + '; }',
      ".hook, .dek, .tx-site, .kick, .src, .cap, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#DDE2E4" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 96, max: 128, maxLines: 2 });
    N.follow();
  };
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE;
    await document.fonts.ready;
    N.start(o);
    var TXT = typeof bench === "function" ? bench(THREE) : bench, K = initKit(THREE, TXT);
    N.K = K; N.TXT = TXT; N.installKit(K, THREE, TXT); N.installColumn(K, THREE, TXT); N.installKerb(K, THREE, TXT);
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
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

  global.CH = N;
})(this);
