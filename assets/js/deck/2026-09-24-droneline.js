/* deck/2026-09-24-droneline.js — the chassis for the 2026-09-24 deck, the FAA's draft
 * environmental assessment of Zipline's drone delivery over five Texas metros.
 *
 * THE HERO OBJECT. One delivery aircraft of the kind the draft describes, and the pod it lowers
 * on a line. The draft gives the aircraft's size (a wingspan, a length and a height, in feet) and
 * five propellers with the tail pair tilting between lift and forward flight. It gives no drawing
 * a reader can check a silhouette against, so the MODEL IS ILLUSTRATIVE: every dimension that is
 * a number comes in from figures.json, converted from the draft's feet by compute.py, and every
 * shape between those dimensions is drawn to illustrate. A frame says so where it shows the
 * aircraft close.
 *
 * THE LINE IS THE STORY. At a delivery the aircraft holds a hover at the draft's cruise height
 * and lowers the pod to the ground on a winch line, and the pod decides whether the spot will do.
 * So the line is drawn at the draft's height, converted to metres by code, on every frame that
 * shows it, and it is the one thing in this deck that wears the accent.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, builds the objects
 * and the materials, and hands a frame primitives. Each frame sets up its own renderer, camera,
 * sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("droneline.js needs txdeck.js loaded first");

  /* ONE DECLARATION. The light is the low sun over the west side of the street, at an elevation
   * inside goldenHour's range, so every cast in the deck runs east and every west face is lit.
   * az is clockwise from +Z toward +X, el is above the ground. */
  TXDECK.declare({
    world: "droneline",
    light: { az: -58, el: 9 },
    sky: "goldenHour",
    ground: "#131A24",
    material: "#D9DCD6",
    accent: "#8FE0F0",
    grade: {
      exposure: 0.0,
      saturation: 1.04,
      contrast: 1.07,
      filmic: true,
      lift: [0.008, 0.010, 0.018],
      gain: [1.025, 1.0, 0.975],
      vignette: 0.20,
      bloom: { threshold: 0.8, strength: 0.2, radius: 12 },
      grain: { amount: 0.014, size: 2, seed: 20260924 },
      aberration: 0,
      dither: true,
      sharpen: 0.2
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20260924;
  N.ACCENT = 0x8fe0f0;          /* comal_lit, config/brand.yaml: the lit line where water meets air */
  N.GROUND_HEX = "#131A24";

  /* ONE MATERIAL VOCABULARY. A white composite airframe, dark rotor blades, painted siding and
   * shingle on the houses, galvanised steel on the posts, and the accent on the line alone. */
  N.mats = function (TXT, THREE) {
    var S = function (c, m, r) { return TXT.mat.clay(c, { metalness: m, roughness: r }); };
    var line = new THREE.MeshBasicMaterial({ color: N.ACCENT, toneMapped: false });
    return {
      skin: TXT.mat.plastic(0xe9ebe6, { roughness: 0.34, metalness: 0.02 }),
      trim: S(0x2b3138, 0.1, 0.5),
      blade: S(0x1c2126, 0.2, 0.42),
      glass: TXT.mat.plastic(0x10161c, { roughness: 0.12, metalness: 0.3 }),
      pod: TXT.mat.plastic(0xdfe3de, { roughness: 0.4 }),
      podBand: S(0x39424b, 0.1, 0.5),
      line: line,
      siding: [S(0xb9b0a0, 0, 0.9), S(0x8f978e, 0, 0.9), S(0xc7b9a2, 0, 0.9), S(0x9aa3a8, 0, 0.9)],
      brick: S(0x8a5a44, 0, 0.92),
      roof: [S(0x3b3a38, 0, 0.8), S(0x4a4036, 0, 0.8), S(0x2f3438, 0, 0.8)],
      trimWhite: S(0xe6e2d8, 0, 0.7),
      window: TXT.mat.plastic(0x1b2530, { roughness: 0.1, metalness: 0.4 }),
      windowLit: TXT.mat.emissive(0xffc98a, 1.2),
      fence: S(0x7a5e45, 0, 0.9),
      galv: S(0x9aa2a6, 0.7, 0.4),
      concrete: S(0x9c978d, 0, 0.95),
      kiosk: S(0x2e353d, 0.3, 0.45),
      leaf: [S(0x3e4a2c, 0, 0.9), S(0x4b5632, 0, 0.9), S(0x36422a, 0, 0.9)],
      bark: S(0x3b3027, 0, 0.95),
      cloth: [S(0x3c4a5c, 0, 0.8), S(0x6b4d3a, 0, 0.8), S(0x51603f, 0, 0.8)],
      skinTone: S(0x9c7458, 0, 0.7),
      package: S(0xb58e5f, 0, 0.85)
    };
  };

  function box(THREE, w, h, d, mat, x, y, z) {
    var m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x || 0, y || 0, z || 0);
    return m;
  }

  /* A rotor: a hub and two blades, radius r, lying flat (lift) unless turned by the caller. */
  function rotor(THREE, M, r) {
    var g = new THREE.Group();
    var hub = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.09, r * 0.09, r * 0.08, 16), M.trim);
    g.add(hub);
    [0, Math.PI].forEach(function (a) {
      var b = new THREE.Mesh(new THREE.BoxGeometry(r * 0.95, r * 0.012, r * 0.1), M.blade);
      b.position.set(Math.cos(a) * r * 0.5, r * 0.02, Math.sin(a) * r * 0.5);
      b.rotation.y = -a; b.rotation.x = 0.12;
      g.add(b);
    });
    return g;
  }

  /* THE AIRCRAFT, nose toward -Z, wing along X, centred on its own centre of mass, y up.
   * o.span, o.length, o.height are METRES from figures.json. o.mode 'hover' tips the tail pair
   * up to lift, 'cruise' lays them back to push. o.bay true opens the pod bay. */
  N.zip = function (THREE, TXT, M, o) {
    o = o || {};
    var span = o.span, len = o.length, ht = o.height;
    if (!(span > 0 && len > 0 && ht > 0)) throw new Error("N.zip needs span, length and height in metres from figures.json");
    var g = new THREE.Group();
    /* the fuselage, a lathed teardrop along Z, its depth set by the draft's height */
    var R = ht * 0.36;
    var prof = [];
    for (var i = 0; i <= 24; i++) {
      var t = i / 24, y = (t - 0.5) * len;
      var r = R * Math.pow(Math.sin(Math.PI * Math.min(1, t * 1.15)), 0.62) * (t > 0.87 ? (1 - (t - 0.87) / 0.13) * 0.9 + 0.1 : 1);
      prof.push([Math.max(0.001, r), y]);
    }
    var fus = TXT.lathe(prof, M.skin, { segments: 48 });
    fus.rotation.x = Math.PI / 2; fus.scale.set(1, 1, 0.82);
    g.add(fus);
    /* a dark sensor window under the nose */
    var eye = new THREE.Mesh(new THREE.SphereGeometry(R * 0.32, 20, 12), M.glass);
    eye.position.set(0, -R * 0.55, -len * 0.36); eye.scale.set(1, 0.6, 1.3); g.add(eye);
    /* the wing: straight, thin, a rounded box, set a third of the way back */
    var chord = len * 0.13;
    var wing = TXT.roundedBox(span, ht * 0.05, chord, ht * 0.02, M.skin);
    wing.position.set(0, R * 0.55, -len * 0.06); g.add(wing);
    /* two booms under the wing carrying the lift rotors forward and the tilting pair aft */
    var boomX = span * 0.23, boomL = len * 0.78;
    [-1, 1].forEach(function (s) {
      var boom = TXT.roundedBox(ht * 0.06, ht * 0.06, boomL, ht * 0.025, M.skin);
      boom.position.set(s * boomX, R * 0.45, len * 0.02); g.add(boom);
      /* a lift rotor at the boom's nose */
      var ro = rotor(THREE, M, span * 0.13);
      ro.position.set(s * boomX, R * 0.45 + ht * 0.06, -boomL * 0.45); g.add(ro);
      /* the tail rotor, tilting 90 degrees between lift and forward flight */
      var tail = new THREE.Group();
      var nac = TXT.roundedBox(ht * 0.09, ht * 0.09, ht * 0.22, ht * 0.03, M.trim); tail.add(nac);
      var tr = rotor(THREE, M, span * 0.11); tr.position.set(0, ht * 0.08, 0); tail.add(tr);
      tail.position.set(s * boomX, R * 0.5, boomL * 0.5);
      tail.rotation.x = o.mode === 'cruise' ? Math.PI / 2 : 0;
      g.add(tail);
      /* a V tail fin at the boom's end */
      var fin = TXT.roundedBox(ht * 0.02, ht * 0.32, len * 0.09, ht * 0.01, M.skin);
      fin.position.set(s * boomX, R * 0.5 + ht * 0.2, boomL * 0.42); fin.rotation.z = s * 0.45; g.add(fin);
    });
    /* the fifth propeller: a lift rotor over the nose */
    var nose = rotor(THREE, M, span * 0.1);
    nose.position.set(0, R * 0.9, -len * 0.3); g.add(nose);
    /* the pod bay under the belly, a dark seam, open when the pod is out */
    var bay = TXT.roundedBox(R * 0.9, R * 0.12, len * 0.22, R * 0.05, o.bay ? M.glass : M.trim);
    bay.position.set(0, -R * 0.78, len * 0.04); g.add(bay);
    g.userData.bellyY = -R * 0.84;
    g.userData.bayZ = len * 0.04;
    return g;
  };

  /* THE POD, the delivery unit the draft calls a pod (and its noise study a droid), lowered on
   * the line. Illustrative size. o.package true shows the parcel held in its bay door. */
  N.pod = function (THREE, TXT, M, o) {
    o = o || {};
    var g = new THREE.Group();
    var body = TXT.lathe([[0.001, -0.22], [0.1, -0.2], [0.15, -0.1], [0.16, 0.05], [0.12, 0.18], [0.04, 0.24], [0.001, 0.245]], M.pod, { segments: 40 });
    g.add(body);
    var band = new THREE.Mesh(new THREE.CylinderGeometry(0.162, 0.162, 0.04, 40), M.podBand);
    band.position.y = 0.0; g.add(band);
    [0, 1, 2, 3].forEach(function (k) {
      var fin = TXT.roundedBox(0.012, 0.16, 0.12, 0.004, M.podBand);
      var a = k * Math.PI / 2;
      fin.position.set(Math.cos(a) * 0.15, 0.1, Math.sin(a) * 0.15); fin.rotation.y = -a; g.add(fin);
    });
    if (o.package) { var p = TXT.roundedBox(0.22, 0.14, 0.18, 0.01, M.package); p.position.set(0, -0.3, 0); g.add(p); }
    return g;
  };

  /* THE LINE, from the aircraft's belly to the pod, in the accent. A thin tube so it catches
   * light at any camera, radius exaggerated only as far as a 2x frame needs to resolve it. */
  N.line = function (THREE, M, from, to, radius) {
    var a = new THREE.Vector3(from[0], from[1], from[2]), b = new THREE.Vector3(to[0], to[1], to[2]);
    var L = a.distanceTo(b);
    var m = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, L, 8), M.line);
    m.position.copy(a).add(b).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
    m.castShadow = false;
    return m;
  };

  /* A ONE STOREY TEXAS RANCH HOUSE, w by d metres, gabled along x, on a slab. Seeded variety. */
  N.house = function (THREE, TXT, M, o) {
    o = o || {};
    var w = o.w || 16, d = o.d || 11, h = o.h || 2.9, k = (o.seed || 0);
    var g = new THREE.Group();
    var wall = (k % 3 === 0) ? M.brick : M.siding[k % M.siding.length];
    var slab = TXT.roundedBox(w + 0.3, 0.25, d + 0.3, 0.03, M.concrete); slab.position.y = 0.125; g.add(slab);
    var body = TXT.roundedBox(w, h, d, 0.04, wall); body.position.y = 0.25 + h / 2; g.add(body);
    /* the gable roof, an extruded triangle along x */
    var rise = o.rise || 2.1, over = 0.45;
    var roofShape = [[-(d / 2 + over), 0], [d / 2 + over, 0], [0, rise]];
    var roof = TXT.extrude(roofShape, w + over * 2, M.roof[k % M.roof.length], { bevel: false });
    roof.rotation.y = Math.PI / 2; roof.position.set(-(w / 2 + over), 0.25 + h, 0); g.add(roof);
    /* windows and a door on the +z face (the street side) */
    var nWin = Math.max(2, Math.floor(w / 4));
    for (var i = 0; i < nWin; i++) {
      var x = -w / 2 + (i + 0.7) * (w / (nWin + 0.4));
      var lit = o.lit && ((i + k) % 3 === 0);
      var win = box(THREE, 1.3, 1.25, 0.06, lit ? M.windowLit : M.window, x, 0.25 + 1.55, d / 2 + 0.02); g.add(win);
      var sill = box(THREE, 1.45, 0.08, 0.12, M.trimWhite, x, 0.25 + 0.9, d / 2 + 0.05); g.add(sill);
    }
    var door = box(THREE, 1.0, 2.1, 0.06, M.trim, w * 0.18, 0.25 + 1.05, d / 2 + 0.02); g.add(door);
    /* a garage door on the -x end of the street face */
    var gar = box(THREE, 4.8, 2.2, 0.06, M.trimWhite, -w / 2 + 3.0, 0.25 + 1.1, d / 2 + 0.03); g.add(gar);
    return g;
  };

  /* A LIVE OAK, a spreading crown of lumps on a short trunk. Height in metres. */
  N.oak = function (THREE, TXT, M, o) {
    o = o || {};
    var h = o.h || 8, s = o.seed || 1, g = new THREE.Group();
    var rnd = TXT.rng ? TXT.rng(s) : function () { s = (s * 16807) % 2147483647; return s / 2147483647; };
    var trunk = new THREE.Mesh(new THREE.CylinderGeometry(h * 0.04, h * 0.06, h * 0.45, 10), M.bark);
    trunk.position.y = h * 0.225; g.add(trunk);
    for (var i = 0; i < 9; i++) {
      var a = rnd() * Math.PI * 2, rr = h * (0.18 + rnd() * 0.3);
      var blob = new THREE.Mesh(new THREE.IcosahedronGeometry(h * (0.22 + rnd() * 0.12), 2), M.leaf[i % M.leaf.length]);
      blob.position.set(Math.cos(a) * rr, h * (0.55 + rnd() * 0.3), Math.sin(a) * rr);
      blob.scale.set(1.2, 0.7, 1.2); g.add(blob);
    }
    return g;
  };

  /* A PRIVACY FENCE RUN, from [x0,z0] to [x1,z1], 1.8 m of cedar pickets on posts. */
  N.fence = function (THREE, TXT, M, a, b, o) {
    o = o || {};
    var g = new THREE.Group(), h = o.h || 1.8;
    var dx = b[0] - a[0], dz = b[1] - a[1], L = Math.hypot(dx, dz);
    var panel = TXT.roundedBox(L, h, 0.04, 0.01, M.fence);
    panel.position.set((a[0] + b[0]) / 2, h / 2, (a[1] + b[1]) / 2);
    panel.rotation.y = -Math.atan2(dz, dx); g.add(panel);
    var n = Math.max(1, Math.round(L / 2.4));
    for (var i = 0; i <= n; i++) {
      var t = i / n, post = TXT.roundedBox(0.1, h + 0.1, 0.1, 0.01, M.fence);
      post.position.set(a[0] + dx * t, (h + 0.1) / 2, a[1] + dz * t + 0.04); g.add(post);
    }
    return g;
  };

  /* A PERSON, 1.7 m, standing, arms down. Illustrative, faceless, the size the frame needs. */
  N.person = function (THREE, M, o) {
    o = o || {};
    var g = new THREE.Group(), c = M.cloth[(o.seed || 0) % M.cloth.length];
    function cap(r, len, mat, x, y, z) { var m = new THREE.Mesh(new THREE.CapsuleGeometry(r, len, 6, 12), mat); m.position.set(x, y, z); return m; }
    g.add(cap(0.075, 0.72, M.trim, -0.1, 0.44, 0));
    g.add(cap(0.075, 0.72, M.trim, 0.1, 0.44, 0));
    g.add(cap(0.19, 0.42, c, 0, 1.12, 0));
    g.add(cap(0.05, 0.56, c, -0.25, 1.1, 0));
    g.add(cap(0.05, 0.56, c, 0.25, 1.1, 0));
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.105, 20, 14), M.skinTone); head.position.set(0, 1.58, 0); g.add(head);
    if (o.lookUp) head.rotation.x = -0.5;
    return g;
  };

  /* A DROPBOX, the draft's pickup kiosk: a column the pod descends into, on a pad. Illustrative. */
  N.dropbox = function (THREE, TXT, M) {
    var g = new THREE.Group();
    var pad = TXT.roundedBox(1.8, 0.15, 1.8, 0.02, M.concrete); pad.position.y = 0.075; g.add(pad);
    var col = TXT.roundedBox(0.9, 2.6, 0.9, 0.05, M.kiosk); col.position.y = 0.15 + 1.3; g.add(col);
    var mouth = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.3, 0.12, 32), M.trim); mouth.position.y = 0.15 + 2.66; g.add(mouth);
    var face = box(THREE, 0.6, 0.7, 0.04, M.trimWhite, 0, 1.3, 0.47); g.add(face);
    return g;
  };

  /* A CHARGER, the draft's docking tower: a mast with arms of docks. o.docks sets how many arms
   * are drawn, from figures.json when a frame says so. Illustrative. */
  N.charger = function (THREE, TXT, M, o) {
    o = o || {};
    var g = new THREE.Group(), docks = o.docks || 12, h = o.h || 7;
    var mast = TXT.roundedBox(0.5, h, 0.5, 0.05, M.galv); mast.position.y = h / 2; g.add(mast);
    var tiers = Math.ceil(docks / 4);
    for (var t = 0; t < tiers; t++) {
      for (var k = 0; k < 4 && t * 4 + k < docks; k++) {
        var a = k * Math.PI / 2 + t * 0.4, y = h - 0.6 - t * 1.4;
        var arm = TXT.roundedBox(2.2, 0.12, 0.16, 0.02, M.galv);
        arm.position.set(Math.cos(a) * 1.1, y, Math.sin(a) * 1.1); arm.rotation.y = -a; g.add(arm);
        var dock = TXT.roundedBox(0.5, 0.18, 0.5, 0.03, M.trim);
        dock.position.set(Math.cos(a) * 2.2, y - 0.1, Math.sin(a) * 2.2); g.add(dock);
      }
    }
    var base = TXT.roundedBox(1.6, 0.3, 1.6, 0.03, M.concrete); base.position.y = 0.15; g.add(base);
    return g;
  };

  /* THE DECK'S SHELL, kept here rather than typed into nine frames. */
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
  /* Refuses a black render, paints it onto the frame's art canvas, hands the context back for
   * TXDECK.finish, which every frame calls itself, last. */
  N.develop = function (shot, glCanvas) {
    if (!shot || !shot.ok) throw new Error("the GPU frame came back black: " + JSON.stringify(shot));
    var cx = document.getElementById("art").getContext("2d");
    cx.scale(2, 2);
    cx.drawImage(glCanvas, 0, 0, N.W, N.H);
    return cx;
  };

  global.LINE = N;
})(this);
