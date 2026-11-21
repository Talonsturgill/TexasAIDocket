/* deck/2026-11-20-truetrack-bespoke.js, the SPINE for the November 20th, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * East Texas A&M researchers in Commerce tested AI that flags a drone fed false GPS, reading only the drone's own motion
 * (how fast, which way, over how much time) and no GPS readings, on 96 recorded flights (tx-2026-0253).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the deck's TONE, bespoke:true, the tone's grade and the accent. Each
 * frame picks its own world (TXT.sky(R, world)), turns its own key (TXT.deckRig(..., { light })) and places its own type,
 * seated with CH.seat. It mounts the type faces and the furniture (CH.start), and hands a frame the helpers below. There is
 * no drawFrame.
 *
 * THE ACCENT. Amber #FF9F1C, the people tone's own accent, means ONE thing: MOTION THE DRONE ITSELF MEASURED,
 * the honest signal the check reads (how fast, which way, over how much time). The flown path, the three motion arrows, the
 * edge of the window over ten readings. Never the reported GPS position, which is frosted periwinkle glass and casts no
 * shadow (the deck's SHADOW RULE), never decoration, never a person.
 *
 * THE MODELS. The kit holds the land, the trees, the people, the vehicles and a fixed wing vtol_drone. The chassis builds
 * what the kit lacks, in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the
 * lift: survey_quad (an illustrative survey quadcopter to no maker's design, with a ghost mode in frosted glass that casts no
 * shadow, folded props and an open shell) and flight_board (its flight controller with the motion sensor chip). Every drone drawn is drawn to illustrate.
 * Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("truetrack.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "truetrack", look: "v2", tone: "people", bespoke: true,
    light: { az: -45, el: 35 },
    sky: { preset: "v2people" },
    ground: "#e4d8c3",
    material: "#e4d8c3",
    accent: "#ff9f1c",
    grade: TXLOOK.grade("people")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261120; N.TONE = "people"; N.P = TXLOOK.palette("people"); N.INK = N.P.ink;
  N.ACCENT = 0xff9f1c;        /* amber: motion the drone itself measured, and nothing else */
  N.GHOST = 0x9fb2ff;         /* frosted periwinkle glass: the position the false signal reports */
  N.GOLD = N.ACCENT;
  /* a seeded canvas texture, so every surface carries tooth in its albedo and never in its height */
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };



  N.glassMat = function (K, tint) {
    return K.mat("tt-glass" + (tint || ""), { color: tint || 0xf4f8ff, metalness: 0, roughness: 0.04, transmission: 0.95, ior: 1.47, thickness: 0.002,
      transparent: true, opacity: 1, clearcoat: 1, clearcoatRoughness: 0.03, specularIntensity: 1, envMapIntensity: 1.4, side: N.T.DoubleSide }, true);
  };
  N.goldMat = function (K, glow) { return K.mat("tt-gold" + (glow || 0), { color: N.ACCENT, metalness: 0.35, roughness: 0.32, emissive: N.ACCENT, emissiveIntensity: Math.min(0.7, glow || 0.12), clearcoat: 0.6 }, true); };

  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.survey_quad) return;
    N.T = THREE;
    var shadowAll = function (g) { g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return g; };
    var rbox = function (w, h, d, r, mat) { return TXT.roundedBox ? TXT.roundedBox(w, h, d, r, mat) : new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); };
    /* A SURVEY QUADCOPTER, drawn to no maker's design. Origin on the ground under the body centre, front (camera) on +z,
     * y up. About 0.70 m motor to motor across the diagonal, a moulded shell 0.30 x 0.11 x 0.22 m with a top battery
     * hatch, four folding carbon arms with motor bells, two blade props per motor (or a soft disc when spinning), a
     * three axis gimbal with a camera, two landing legs per side with rubber feet, front LEDs and a rear status lamp.
     * Options: spin (0 still blades, 1 blurred discs), shell (hex body colour), lamp (hex rear lamp, default the accent),
     * legs (true), lift (metres the body hovers above origin, 0 sits on its feet), arm (0.35 half diagonal in metres). */
    K.define("survey_quad", {
      size: [0.86, 0.26, 0.86],
      options: { spin: 0, shell: 0xe9ecef, lamp: null, legs: true, lift: 0, arm: 0.35, ghost: false, props: 'still', open: false },
      note: "An illustrative survey quadcopter, about 0.70 m motor to motor, moulded shell, carbon arms, gimbal camera, landing legs, GPS puck on a mast. Origin on the ground under the body, front on +z. props 'still' | 'spin' | 'folded'; lift raises it; open:true removes the top shell and shows the flight_board; ghost:true renders the whole aircraft in frosted periwinkle glass that casts NO shadow (the reported position); lamp colours the rear lamp.",
      make: function (o) {
        o = Object.assign({ spin: 0, shell: 0xe9ecef, lamp: null, legs: true, lift: 0, arm: 0.35, ghost: false, props: 'still', open: false }, o || {});
        if (o.props === 'spin') o.spin = 1;
        var g = new THREE.Group(), body = new THREE.Group(); g.add(body);
        var legH = o.legs ? 0.13 : 0.06; body.position.y = legH + o.lift;
        var shell = K.mat("q-shell-" + o.shell, { color: o.shell, roughness: 0.32, metalness: 0.05, clearcoat: 0.8, clearcoatRoughness: 0.18 }, true);
        var trim = K.mat("q-trim", { color: 0x2b2f36, roughness: 0.45, metalness: 0.2, clearcoat: 0.3 }, true);
        var carbonTex = N.canvasTex(THREE, 256, 256, function (x, w, h) {
          x.fillStyle = "#1c1f24"; x.fillRect(0, 0, w, h);
          for (var j = 0; j < h; j += 8) for (var i = 0; i < w; i += 8) { x.fillStyle = ((i + j) / 8) % 2 ? "#262a31" : "#16181c"; x.fillRect(i, j, 8, 8); }
        }, [4, 1]);
        var carbon = K.mat("q-carbon", { color: 0xffffff, map: carbonTex, roughness: 0.3, metalness: 0.35, clearcoat: 0.9, clearcoatRoughness: 0.12 }, true);
        var metal = K.mat("q-bell", { color: 0x9aa2ad, roughness: 0.25, metalness: 1 });
        var dark = K.mat("q-dark", { color: 0x111318, roughness: 0.5, metalness: 0.3 });
        var rubber = K.mat("q-rubber", { color: 0x1a1a1c, roughness: 0.9, metalness: 0 });
        /* the shell: a rounded lower tub, a domed upper shell, a battery hatch with a seam and a grip */
        var tub = rbox(0.30, 0.06, 0.22, 0.025, trim); tub.position.y = 0.03; body.add(tub);
        var top = rbox(0.28, 0.06, 0.20, 0.03, shell); top.position.y = 0.085; body.add(top);
        var hatch = rbox(0.17, 0.012, 0.11, 0.008, shell); hatch.position.set(0, 0.118, -0.02); body.add(hatch);
        var seam = rbox(0.172, 0.004, 0.112, 0.004, dark); seam.position.set(0, 0.112, -0.02); body.add(seam);
        var grip = rbox(0.05, 0.008, 0.02, 0.004, dark); grip.position.set(0, 0.126, -0.06); body.add(grip);
        /* nose sensors: two dark stereo windows and front LEDs */
        [-1, 1].forEach(function (s) {
          var win = new THREE.Mesh(new THREE.CircleGeometry(0.012, 20), K.finish.glass(0x0b0f18)); win.position.set(s * 0.05, 0.075, 0.1105); body.add(win);
          var led = new THREE.Mesh(new THREE.SphereGeometry(0.006, 12, 8), new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff4e0, emissiveIntensity: 2.2 })); led.position.set(s * 0.12, 0.03, 0.105); body.add(led);
        });
        /* arms, motors and props */
        var a = o.arm;
        [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(function (p, k) {
          var tip = [p[0] * a * 0.7071, 0.07, p[1] * a * 0.7071];
          K.bar([p[0] * 0.11, 0.07, p[1] * 0.07], tip, 0.014, carbon, 10, body);
          var mount = K.cyl(0.03, 0.034, 0.025, trim, tip[0], 0.06, tip[2], 20, body);
          var bell = K.cyl(0.026, 0.026, 0.03, metal, tip[0], 0.085, tip[2], 24, body);
          var cap = K.cyl(0.008, 0.008, 0.012, dark, tip[0], 0.106, tip[2], 12, body);
          var hubY = 0.112;
          if (o.spin > 0.5) {
            var dm = new THREE.MeshPhysicalMaterial({ color: 0x20242a, transparent: true, opacity: 0.22, roughness: 0.4, depthWrite: false, side: THREE.DoubleSide });
            var disc = new THREE.Mesh(new THREE.RingGeometry(0.012, 0.19, 48), dm); disc.rotation.x = -Math.PI / 2; disc.position.set(tip[0], hubY, tip[2]); disc.castShadow = false; body.add(disc);
            var rim = new THREE.Mesh(new THREE.RingGeometry(0.175, 0.19, 64), new THREE.MeshBasicMaterial({ color: 0x3a3f48, transparent: true, opacity: 0.25, depthWrite: false, side: THREE.DoubleSide })); rim.rotation.x = -Math.PI / 2; rim.position.set(tip[0], hubY + 0.001, tip[2]); body.add(rim);
          } else if (o.props === 'folded') {
            for (var b2 = 0; b2 < 2; b2++) { var bl = rbox(0.18, 0.004, 0.028, 0.002, dark); var pv = new THREE.Group(); pv.position.set(tip[0], hubY, tip[2]);
              pv.rotation.y = Math.atan2(-tip[2], tip[0]) + Math.PI + (b2 ? 0.08 : -0.08); bl.position.x = 0.09; pv.add(bl); body.add(pv); }
          } else {
            var ang = k * 0.9 + 0.3;
            for (var b = 0; b < 2; b++) {
              var blade = rbox(0.18, 0.004, 0.028, 0.002, dark); var piv = new THREE.Group(); piv.position.set(tip[0], hubY, tip[2]); piv.rotation.y = ang + b * Math.PI;
              blade.position.x = 0.09; blade.rotation.x = (p[0] * p[1] > 0 ? 1 : -1) * 0.12; piv.add(blade); body.add(piv);
            }
          }
          /* landing legs under the front and rear arms */
          if (o.legs && p[1] > 0 || o.legs && p[1] < 0) {
            var lx = p[0] * 0.10, lz = p[1] * 0.08;
            K.bar([lx, 0.0, lz], [lx * 1.5, -legH + 0.01, lz * 1.4], 0.008, carbon, 8, body);
            var foot = new THREE.Mesh(new THREE.SphereGeometry(0.013, 12, 8), rubber); foot.position.set(lx * 1.5, -legH + 0.012, lz * 1.4); body.add(foot);
          }
        });
        /* GPS puck on a short mast at the rear: the receiver spoofing lies to */
        K.cyl(0.006, 0.006, 0.06, carbon, 0, 0.115, -0.07, 10, body);
        var puck = K.cyl(0.035, 0.038, 0.016, shell, 0, 0.175, -0.07, 28, body);
        var dome = new THREE.Mesh(new THREE.SphereGeometry(0.034, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), shell); dome.scale.y = 0.35; dome.position.set(0, 0.19, -0.07); body.add(dome);
        g.userData.gps = puck;
        if (o.open) { top.visible = false; hatch.visible = false; seam.visible = false; grip.visible = false;
          var fb = K.make('flight_board', {}); fb.scale.setScalar(1.6); fb.position.set(0, 0.062, 0.0); body.add(fb); g.userData.board = fb; }
        var yoke = rbox(0.05, 0.03, 0.03, 0.008, trim); yoke.position.set(0, -0.01, 0.075); body.add(yoke);
        var cam = rbox(0.055, 0.048, 0.05, 0.012, dark); cam.position.set(0, -0.045, 0.085); body.add(cam);
        var lensRing = K.cyl(0.018, 0.018, 0.012, metal, 0, -0.045, 0.114, 24, body); lensRing.rotation.x = Math.PI / 2;
        var lens = new THREE.Mesh(new THREE.CircleGeometry(0.014, 24), K.finish.glass(0x0a1020)); lens.position.set(0, -0.045, 0.1205); body.add(lens);
        /* rear status lamp, neutral white by default so the accent keeps its one meaning */
        var lamp = new THREE.Mesh(new THREE.SphereGeometry(0.008, 14, 10), new THREE.MeshStandardMaterial({ color: o.lamp || 0xfff4e0, emissive: o.lamp || 0xfff4e0, emissiveIntensity: 2.2 }));
        lamp.position.set(0, 0.06, -0.112); body.add(lamp);
        g.userData.lamp = lamp; g.userData.body = body; g.userData.camera = cam;
        if (o.ghost) {
          var gm = new THREE.MeshPhysicalMaterial({ name: 'ghost-frosted-glass', color: N.GHOST, metalness: 0, roughness: 0.35, transmission: 0.6, thickness: 0.02, ior: 1.45, transparent: true, opacity: 0.85, clearcoat: 1, clearcoatRoughness: 0.2, emissive: N.GHOST, emissiveIntensity: 0.08 });
          g.traverse(function (m) { if (m.isMesh) { m.material = gm; m.castShadow = false; m.receiveShadow = false; } });
          g.userData.ghost = true; return g;
        }
        return shadowAll(g);
      }
    });

    /* THE FLIGHT CONTROLLER, drawn to no maker's design: a 36 x 36 mm board, green black solder mask, gold pads, a 3 x 3 x 1 mm
     * motion sensor chip at the centre (userData.imu), a processor, capacitors, header pins and four mounting holes. Origin at
     * the board's bottom centre, y up. Real size in metres; a macro frame scales its camera, not the model. */
    K.define("flight_board", {
      size: [0.036, 0.006, 0.036],
      options: { seed: 3 },
      note: "An illustrative 36 mm flight controller board with a motion sensor chip at the centre (userData.imu), processor, passives, header and mounting holes.",
      make: function (o) {
        o = o || {}; var g = new THREE.Group(), r = N.rng(o.seed || 3);
        var maskTex = N.canvasTex(THREE, 512, 512, function (x, w, h) {
          x.fillStyle = "#123a2c"; x.fillRect(0, 0, w, h);
          x.strokeStyle = "rgba(60,140,100,0.55)"; x.lineWidth = 3;
          for (var i = 0; i < 60; i++) { var x0 = r() * w, y0 = r() * h; x.beginPath(); x.moveTo(x0, y0); var hz = r() < 0.5; x.lineTo(hz ? x0 + (r() - 0.5) * 220 : x0, hz ? y0 : y0 + (r() - 0.5) * 220); x.lineTo(x0 + (r() - 0.5) * 60, y0 + (r() - 0.5) * 60); x.stroke(); }
          x.fillStyle = "#d8b25a"; for (var j = 0; j < 140; j++) { x.fillRect(r() * w, r() * h, 8, 5); }
          ["#d8b25a"].forEach(function () { [[40, 40], [472, 40], [40, 472], [472, 472]].forEach(function (p) { x.beginPath(); x.arc(p[0], p[1], 26, 0, 7); x.fill(); x.fillStyle = "#0b0d10"; x.beginPath(); x.arc(p[0], p[1], 14, 0, 7); x.fill(); x.fillStyle = "#d8b25a"; }); });
        });
        var pcb = K.mat("fb-mask", { color: 0xffffff, map: maskTex, roughness: 0.38, metalness: 0.05, clearcoat: 0.7, clearcoatRoughness: 0.2 }, true);
        var chipM = K.mat("fb-chip", { color: 0x16171b, roughness: 0.42, metalness: 0.1 });
        var silver = K.mat("fb-solder", { color: 0xc9ccd2, roughness: 0.22, metalness: 1 });
        var gold = K.mat("fb-gold", { color: 0xd8b25a, roughness: 0.25, metalness: 1 });
        var capM = K.mat("fb-cap", { color: 0xa88a5a, roughness: 0.5 });
        var board = rbox(0.036, 0.0016, 0.036, 0.0015, pcb); board.position.y = 0.0008; g.add(board);
        var imu = rbox(0.003, 0.001, 0.003, 0.0003, chipM); imu.position.set(0, 0.0021, 0); g.add(imu);
        var imuPad = rbox(0.0042, 0.0002, 0.0042, 0.0001, gold); imuPad.position.set(0, 0.0017, 0); g.add(imuPad);
        var mcu = rbox(0.009, 0.0012, 0.009, 0.0004, chipM); mcu.position.set(-0.009, 0.0022, 0.008); g.add(mcu);
        for (var k = 0; k < 9; k++) { [-1, 1].forEach(function (s) { var pin = rbox(0.0006, 0.0003, 0.0012, 0.0001, silver); pin.position.set(-0.009 + (k - 4) * 0.0009, 0.0018, 0.008 + s * 0.0052); g.add(pin); }); }
        for (var c = 0; c < 14; c++) { var cap = rbox(0.0016, 0.0008, 0.0008, 0.0002, capM); cap.position.set((r() - 0.5) * 0.028, 0.002, (r() - 0.5) * 0.028); if (Math.abs(cap.position.x) < 0.004 && Math.abs(cap.position.z) < 0.004) cap.position.x += 0.008; g.add(cap); }
        var hdr = rbox(0.014, 0.0025, 0.0025, 0.0003, chipM); hdr.position.set(0.006, 0.0029, -0.014); g.add(hdr);
        for (var p = 0; p < 6; p++) { var pn = K.cyl(0.0003, 0.0003, 0.004, gold, 0.0005 + p * 0.0023, 0.0016, -0.014, 6, g); }
        g.userData.imu = imu;
        return shadowAll(g);
      }
    });
  };
  N.studioOpts = function (o) { o = o || {}; return { tone: N.TONE, w: (o.w || 4.2) * 1.6, d: (o.d || 3.2) * 1.4, h: 3.2, radius: 0.9, env: 0.95, hemi: 0.7 }; };
  N.roomOpts = function (o) {
    o = o || {};
    return { w: o.w || 4.2, d: o.d || 3.2, h: 3.0, floor: "concrete", wall: o.wall || 0x16161b, window: null, ceiling: o.ceiling !== false, light: o.light == null ? 0.12 : o.light };
  };
  /* a parallel camera `span` metres wide, for a frame that compares lengths and must not foreshorten them */
  N.ortho = function (THREE, R, span) { var w = span / 2, h = w * N.H / N.W; R.camera = new THREE.OrthographicCamera(-w, w, h, -h, 0.01, 40); return R.camera; };
  /* an SVG leader from a label's anchor to a world point, registered for qa's leader check */
  N.leader = function (THREE, R, from, world, what) {
    var at = N.project(THREE, R, world), s = N.svg(), l = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    l.setAttribute("points", from[0] + "," + from[1] + " " + at[0] + "," + at[1]); l.setAttribute("fill", "none"); l.setAttribute("stroke", N.P.ink); l.setAttribute("stroke-width", "3"); l.setAttribute("stroke-linecap", "round");
    s.appendChild(l); (window.__txLeaders = window.__txLeaders || []).push({ target: what, at: at, to: at }); return at;
  };
  /* A CAMERA BEARING FROM THE SUN: the horizontal direction `deg` degrees clockwise (to the right) of the sun's own
   * bearing, so a frame can put the warm seam at its left edge by looking a little right of the sun. */
  N.bearing = function (TXT, deg) {
    var sd = TXT.sunDir(), hx = sd.x, hz = sd.z, n = Math.hypot(hx, hz) || 1; hx /= n; hz /= n;
    var a = -deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
    return [hx * c - hz * s, hz * c + hx * s];
  };
  N.dress = function (cx, o) { o = o || {}; if (TXLOOK.active()) { TXLOOK.footWash(cx, { a: 0.42, height: 230 }); N.typeDark(cx, o); return cx; } N.post(cx, { a: 0.3, veil: 0.35, veilH: 240 }); N.footWash(cx, { a: o.foot || 0.6 }); N.typeDark(cx, { fade: o.fade == null ? 120 : o.fade, pad: o.pad, a: 0.6 }); return cx; };
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

  /* THE FLOOD ITSELF: a spot hung on the declared key's bearing, for a frame whose subject sits too low or too small for
   * the directional key to model it; it never comes from another side. */
  N.flood = function (THREE, R, from, at, o) {
    o = o || {};
    var sp = new THREE.SpotLight(o.color || 0xf0f3ff, o.i == null ? 40 : o.i, o.reach || 8, o.angle || 0.4, o.penumbra == null ? 0.55 : o.penumbra, 2);
    sp.position.set(from[0], from[1], from[2]); sp.target.position.set(at[0], at[1], at[2]);
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0006; sp.shadow.normalBias = 0.01;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
  };
  /* THE LAB GOES DARK: the studio environment lifts the walls to grey, so a frame calls this after the rig. */
  N.darkRoom = function (R, o) {
    o = o || {};
    /* LOOK V2: no dark room. The studio keeps its environment; a frame's call trims the env a touch at most. */
    if (TXLOOK.active()) { if ('environmentIntensity' in R.scene) R.scene.environmentIntensity = Math.max(0.75, R.scene.environmentIntensity || 0.9); return R; }
    R.scene.environmentIntensity = o.env == null ? 0.12 : o.env;
    R.scene.traverse(function (l) { if (!l.isLight) return; if (l.isHemisphereLight || l.isAmbientLight) l.intensity *= (o.amb == null ? 0.35 : o.amb);
      else if (l.isDirectionalLight && !l.castShadow) l.intensity *= (o.fill == null ? 0.4 : o.fill); });
    return R;
  };

  /* THE TYPE BAND GOES TO THE DARK, darken only: a near black gradient from the top of the frame to just under the dek,
   * so the room's far edges behind the type sink rather than strike through it. */
  N.typeDark = function (cx, o) {
    o = o || {};
    if (TXLOOK.active()) return TXLOOK.typeWash(cx, { a: 0.5, fade: Math.max(200, o.fade || 0), pad: o.pad });
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


  /* ---- frame helpers, carried from the 2026-11-13 and 2026-11-08 chassis ---------------------------------- */
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
    ].join("\n") + "\n" + TXLOOK.css(N.TONE);
  };
  /* the bespoke type seat: a soft tint in the tone's deep hue around wherever this frame put its type */
  N.seat = function (cx, o) { return TXLOOK.typeSeat(cx, Object.assign({ tone: N.TONE }, o || {})); };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) { d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px"; });
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS(); document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: N.P.dek });
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
    var a = Math.min(0.5, o.a == null ? 0.3 : o.a), c = N.lowRGB();
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
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(" + N.lowRGB() + "," + (Math.min(0.5, o.veil == null ? 0.3 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
  };
  /* a darken-only wash under the footer, so the site line and the claim ids sit on a dark field and no edge strikes them */
  N.footWash = function (cx, o) {
    o = o || {};
    [[o.x == null ? 850 : o.x, 1300, o.r || 460], [180, 1300, 300]].forEach(function (c) {
      var g = cx.createRadialGradient(c[0], c[1], 20, c[0], c[1], c[2]);
      var lc = N.lowRGB(), fa = (o.a || 0.72) * 0.6; g.addColorStop(0, "rgba(" + lc + "," + fa + ")"); g.addColorStop(0.55, "rgba(" + lc + "," + (fa * 0.6) + ")"); g.addColorStop(1, "rgba(" + lc + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, N.H);
    });
  };
  N.lowRGB = function () { var h = N.P.low.replace("#", ""); return [0, 2, 4].map(function (i) { return parseInt(h.slice(i, i + 2), 16); }).join(","); };
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
