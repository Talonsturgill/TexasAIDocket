/* deck/2026-11-23-samewires-bespoke.js, the SPINE for the November 23rd, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * Riot Platforms leases its whole Corsicana bitcoin mining campus in Navarro County to an AI lab for 15 years, 910 MW of
 * critical IT capacity on 332 acres, delivered in 40 blocks over three phases (tx-2026-0258).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the deck's TONE (watch), bespoke:true, the tone's grade and the accent.
 * Each frame picks its own world (TXT.sky(R, world) or TXT.studio / TXT.interior), turns its own key
 * (TXT.deckRig(..., { light })) and places its own type, seated with CH.seat. It mounts the type faces and the furniture
 * (CH.start), and hands a frame the helpers below. There is no drawFrame.
 *
 * THE ACCENT. Dusk gold #E0956A means ONE thing: SCHEDULED FOR THE LAB, NOT YET BUILT. It is the tape on an empty pad,
 * the flagging on a stake and a date pill. It never touches a miner container, Riot's gear, the parcel or the lock.
 * CH.schedMat(K) is the one gold tape material, emissive so it holds its hue under the coral key.
 *
 * THE TWO MATERIALS. What exists today (clay, line, transformers, miner containers, paper) is solid, weathered and lit.
 * What is only scheduled is gold tape on empty ground. NOTHING IS BUILT FOR THE TENANT and no frame draws compute on a pad.
 *
 * THE MODELS. The kit holds power_line, transformers, shipping_container, machine_pad, desk and person. The chassis
 * builds what the kit lacks, in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can
 * queue the lift: powered_pad, miner_container, trench_section, switchgear_handle, lockout_hasp, bound_lease.
 * Everything is drawn to illustrate: no real campus, no maker's design, no logo, no legible text, no glyph in a texture.
 * Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("samewires.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "samewires", look: "v2", tone: "watch", bespoke: true,
    light: { az: -55, el: 14 },
    sky: { preset: "v2watch" },
    ground: "#4a2f3a",
    material: "#e4d8c3",
    accent: "#e0956a",
    grade: TXLOOK.grade("watch")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261123; N.TONE = "watch"; N.P = TXLOOK.palette("watch"); N.INK = N.P.ink;
  N.ACCENT = 0xe0956a;        /* dusk gold: scheduled for the lab, and nothing else */
  N.SCHED_GLOW = { color: 0xe0956a, intensity: 1.35 };
  N.CLAY = 0x4a2f3a; N.DUST = 0xc9b393; N.STRAW = 0xc7a15a; N.ZINC = 0xa9b2b6; N.TANK = 0x6f8a78; N.CALICHE = 0xe4d8c3;
  N.SHADE = 0x2a1a4a; N.COPPER = 0xb8693e; N.CONCRETE = 0xcfc6b8; N.PAPER = 0xf1eadb; N.WALNUT = 0x5a3a28;
  N.GOLD = N.ACCENT;
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };
  /* the scheduled gold, one material, so every taped pad and flag in a frame is the same light */
  N.schedMat = function (K) { return K.mat("sw-sched", { color: 0x3a1c10, emissive: N.SCHED_GLOW.color, emissiveIntensity: N.SCHED_GLOW.intensity, roughness: 0.55 }); };
  N.toolMat = N.schedMat; N.goldMat = N.schedMat;
  /* broom finished concrete: a pale tint with fine parallel broom strokes and a few stains, no glyph */
  N.broomTex = function (THREE, seed) {
    var r = N.rng(seed || 11);
    return N.canvasTex(THREE, 512, 512, function (g, w, h) {
      g.fillStyle = "#cfc6b8"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 900; i++) { var y = r() * h; g.strokeStyle = "rgba(90,80,70," + (0.03 + r() * 0.05).toFixed(3) + ")"; g.lineWidth = 0.6 + r(); g.beginPath(); g.moveTo(0, y); g.lineTo(w, y + (r() - 0.5) * 6); g.stroke(); }
      for (var k = 0; k < 14; k++) { var gr = g.createRadialGradient(r() * w, r() * h, 2, r() * w, r() * h, 30 + r() * 70); gr.addColorStop(0, "rgba(74,47,58,0.10)"); gr.addColorStop(1, "rgba(74,47,58,0)"); g.fillStyle = gr; g.fillRect(0, 0, w, h); }
    }, [1, 1]);
  };
  /* cracked vertisol clay: plum umber with a polygon crack net and dust in the cracks, never near black */
  N.clayTex = function (THREE, seed, repeat) {
    var r = N.rng(seed || 23);
    return N.canvasTex(THREE, 1024, 1024, function (g, w, h) {
      g.fillStyle = "#5a3a46"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 9000; i++) { g.fillStyle = "rgba(" + (r() < 0.5 ? "120,86,96" : "60,38,50") + "," + (r() * 0.25).toFixed(3) + ")"; g.fillRect(r() * w, r() * h, 2, 2); }
      g.strokeStyle = "rgba(201,179,147,0.55)"; g.lineWidth = 2.2;
      var pts = []; for (var p = 0; p < 70; p++) pts.push([r() * w, r() * h]);
      pts.forEach(function (a) { var near = pts.map(function (b) { return [b, Math.hypot(a[0] - b[0], a[1] - b[1])]; }).sort(function (x, y) { return x[1] - y[1]; }).slice(1, 4);
        near.forEach(function (n) { g.beginPath(); g.moveTo(a[0], a[1]); var mx = (a[0] + n[0][0]) / 2 + (r() - 0.5) * 18, my = (a[1] + n[0][1]) / 2 + (r() - 0.5) * 18; g.quadraticCurveTo(mx, my, n[0][0], n[0][1]); g.stroke(); }); });
    }, repeat || [4, 4]);
  };
  /* greeked lines on paper, never legible: short bars at a pitch */
  N.paperTex = function (THREE, seed, lines) {
    var r = N.rng(seed || 7);
    return N.canvasTex(THREE, 512, 680, function (g, w, h) {
      g.fillStyle = "#f1eadb"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 2600; i++) { g.fillStyle = "rgba(120,110,90," + (r() * 0.05).toFixed(3) + ")"; g.fillRect(r() * w, r() * h, 1.2, 1.2); }
      var n = lines || 22;
      for (var L = 0; L < n; L++) { var y = 50 + L * (h - 90) / n, x = 40, end = w - 40 - r() * 60; while (x < end) { var ww = 14 + r() * 46; g.fillStyle = "rgba(40,44,80,0.36)"; g.fillRect(x, y, Math.min(ww, end - x), 5); x += ww + 8 + r() * 6; } }
    });
  };

  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.powered_pad) return;
    N.T = THREE;
    var shadowAll = function (g) { g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return g; };
    var galv = function () { return K.finish.galvanized(); };
    var conc = function () { return K.mat("sw-conc", { color: 0xffffff, map: N.broomTex(THREE, 11), roughness: 0.9 }, true); };

    /* POWERED PAD. A broom finished slab `w` x `d` m, `h` m proud, chamfered, with a rank of capped conduit stubs along its
     * -z edge, an optional coiled drop cord with a twist lock end and amber indicator, and the empty tenant footprint taped
     * in gold (tape:true) or plain (tape:false). Nothing stands on it, ever. Origin at the slab's centre on the ground. */
    K.define("powered_pad", {
      size: [24, 0.35, 12],
      options: { w: 24, d: 12, h: 0.3, tape: true, stubs: 8, cord: true, lod: "near" },
      note: "Empty powered pad, illustrative: broom finished slab with chamfer, conduit stubs on the -z edge, drop cord with lit amber indicator, the tenant footprint taped in the scheduled gold (CH.schedMat). Nothing stands on it. userData.top is the slab top height; userData.corner is the +x +z corner on top.",
      make: function (o) {
        var g = new THREE.Group(), C = conc(), near = o.lod !== "far";
        K.box(o.w, o.h, o.d, C, 0, 0, 0, near ? Math.min(0.06, o.h * 0.3) : 0, g);
        if (o.tape) {
          var T = N.schedMat(K), tw = Math.max(0.1, o.w * 0.006), inset = Math.min(o.w, o.d) * 0.12, y = o.h + 0.003;
          var iw = o.w - 2 * inset, id = o.d - 2 * inset;
          K.box(iw, 0.004, tw, T, 0, y, -id / 2, 0, g); K.box(iw, 0.004, tw, T, 0, y, id / 2, 0, g);
          K.box(tw, 0.004, id, T, -iw / 2, y, 0, 0, g); K.box(tw, 0.004, id, T, iw / 2, y, 0, 0, g);
          if (near) { var lift = K.box(0.5, 0.004, tw, T, iw / 2 - 0.25, y + 0.01, id / 2, 0, g); lift.rotation.z = 0.06; }
        }
        if (near) {
          var cap = K.mat("sw-stubcap", { color: 0x7d8c86, roughness: 0.5, metalness: 0.3 }), G = galv();
          for (var i = 0; i < o.stubs; i++) { var x = -o.w * 0.35 + i * (o.w * 0.7) / Math.max(1, o.stubs - 1); K.cyl(0.055, 0.055, 0.55, G, x, o.h, -o.d / 2 + 0.35, 18, g); K.cyl(0.07, 0.07, 0.05, cap, x, o.h + 0.55, -o.d / 2 + 0.35, 18, g); }
          if (o.cord) {
            var R = K.finish.rubber(), pts = [], cx0 = -o.w * 0.35, cz0 = -o.d / 2 + 0.35;
            for (var k = 0; k <= 60; k++) { var a = k / 60 * Math.PI * 5, rr = 0.25 + k * 0.006; pts.push(new THREE.Vector3(cx0 + 0.6 + Math.cos(a) * rr, o.h + 0.03 + (k > 50 ? (k - 50) * 0.003 : 0), cz0 + 1.0 + Math.sin(a) * rr)); }
            pts.unshift(new THREE.Vector3(cx0, o.h + 0.55, cz0));
            g.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 220, 0.022, 10, false), R));
            var end = pts[pts.length - 1]; var plug = K.cyl(0.05, 0.05, 0.12, K.mat("sw-plug", { color: 0xd8c25a, roughness: 0.5 }), end.x, end.y - 0.05, end.z, 18, g); plug.rotation.z = Math.PI / 2;
            K.mesh(new THREE.SphereGeometry(0.014, 12, 10), K.finish.lamp(0xffa53a, 4), end.x + 0.07, end.y + 0.02, end.z, g);
          }
        }
        g.userData.top = o.h; g.userData.corner = [o.w / 2, o.h, o.d / 2];
        return shadowAll(g);
      }
    });

    /* MINER CONTAINER. 12.19 x 2.9 x 2.44 m, drawn to illustrate and to no maker's design: a corrugated high cube body, a fan
     * wall on +z of 2 rows of `fans` guarded axial fans with a warm exhaust glow, an intake louvre on -z, a cable gland box at
     * +x, on two concrete sleepers 0.3 m tall. No count of miners anywhere. */
    K.define("miner_container", {
      size: [12.19, 2.9, 2.44],
      options: { color: 0x7d8a8f, fans: 8, glow: 0.8, rust: 0.2 },
      note: "Containerised bitcoin miner block, illustrative: high cube container body on sleepers, guarded fan wall on +z with warm exhaust glow, intake louvre on -z, cable gland box at +x. glow 0..1.",
      make: function (o) {
        var g = new THREE.Group(), sl = K.mat("sw-sleeper", { color: 0xb9b0a2, roughness: 0.95 });
        K.box(0.5, 0.3, 2.6, sl, -4.8, 0, 0, 0.03, g); K.box(0.5, 0.3, 2.6, sl, 4.8, 0, 0, 0.03, g);
        var body = K.make("shipping_container", { color: o.color, highCube: true, rust: o.rust }); body.rotation.y = Math.PI / 2; body.position.y = 0.3; g.add(body);
        /* NO GLYPH IN A TEXTURE: the kit container strokes an owner code, a serial and a weight table into its paint maps.
         * Every mapped paint is swapped for a plain weathered paint; the corrugation is geometry and stays. */
        var plain = K.mat("sw-minerpaint" + o.color, { color: o.color, roughness: 0.5, metalness: 0.15 }, true);
        body.traverse(function (m) { if (m.isMesh && m.material && m.material.map) { var keep = m.material; m.material = plain.clone(); m.material.roughness = keep.roughness; } });
        var bb = new THREE.Box3().setFromObject(body), zf = bb.max.z + 0.005, top = bb.max.y;
        var guard = K.mat("sw-guard", { color: 0x16161a, metalness: 0.6, roughness: 0.4 }), hub = K.mat("sw-hub", { color: 0x2a2a30, metalness: 0.5, roughness: 0.5 });
        var glow = K.mat("sw-exhaust" + o.glow, { color: 0x121116, emissive: 0xc8404e, emissiveIntensity: 0.28 * o.glow, roughness: 0.8 }, true);
        var blade = K.mat("sw-blade", { color: 0x3a3d44, metalness: 0.5, roughness: 0.45 });
        var span = 10.6, n = o.fans, d = 0.9;
        for (var row = 0; row < 2; row++) for (var i = 0; i < n; i++) {
          var x = -span / 2 + d / 2 + i * (span - d) / (n - 1), y = 0.3 + 0.78 + row * 1.0;
          var disk = new THREE.Mesh(new THREE.CircleGeometry(0.4, 32), glow); disk.position.set(x, y, zf - 0.002); g.add(disk);
          var ring = new THREE.Mesh(new THREE.TorusGeometry(0.41, 0.024, 8, 36), guard); ring.position.set(x, y, zf + 0.02); g.add(ring);
          for (var s = 0; s < 3; s++) { var bar = K.bar([x - 0.38, y + (s - 1) * 0.18, zf + 0.03], [x + 0.38, y + (s - 1) * 0.18, zf + 0.03], 0.008, guard, 6, g); }
          K.bar([x, y - 0.38, zf + 0.03], [x, y + 0.38, zf + 0.03], 0.008, guard, 6, g);
          K.mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.04, 14), hub, x, y, zf + 0.02, g).rotation.x = Math.PI / 2;
          for (var bl = 0; bl < 5; bl++) { var bm = K.box(0.3, 0.09, 0.012, blade, 0, 0, 0, 0.004); bm.geometry.translate(0.17, -0.045, 0); bm.position.set(x, y, zf + 0.01); bm.rotation.set(0.3, 0, bl * Math.PI * 2 / 5 + i); g.add(bm); }
        }
        var lv = K.mat("sw-louvre", { color: 0x5c676b, metalness: 0.5, roughness: 0.5 });
        for (var j = 0; j < 14; j++) K.box(8.0, 0.04, 0.06, lv, 0, 0.6 + j * 0.13, bb.min.z - 0.03, 0, g);
        K.box(0.5, 0.7, 0.35, galv(), bb.max.x + 0.18, 1.0, 0.6, 0.02, g);
        K.bar([bb.max.x + 0.3, 1.0, 0.6], [bb.max.x + 0.3, 0.0, 0.6], 0.04, K.finish.rubber(), 8, g);
        g.userData.top = top;
        return shadowAll(g);
      }
    });

    /* TRENCH SECTION. A cut block of cracked vertisol clay `w` x `h` x `d` m with dust in the cracks, a duct bank of `ducts`
     * PVC conduits in red-dyed concrete encasement 0.8 m down, and `branches` cable runs leaving its +x face. Origin at the
     * top centre of the block (the ground surface). */
    K.define("trench_section", {
      size: [14, 2, 3],
      options: { w: 14, h: 2, d: 3, ducts: 6, branches: 1 },
      note: "Cut section of Blackland clay with a red concrete duct bank, illustrative. Origin at the ground surface centre; the block hangs below y 0. branches sets how many conduit runs leave the +x face.",
      anchor: "base",
      make: function (o) {
        var g = new THREE.Group(), clay = K.mat("sw-claycut", { color: 0xffffff, map: N.clayTex(THREE, 31, [2, 1]), roughness: 0.97 }, true);
        var strata = [0x6a4654, 0x5a3a46, 0x4f3340, 0x6b5148];
        strata.forEach(function (c, i) { K.box(o.w, o.h / 4, o.d, i === 0 ? clay : K.mat("sw-strata" + i, { color: c, roughness: 0.97 }), 0, -o.h + i * o.h / 4, 0, 0, g); });
        var enc = K.mat("sw-redconc", { color: 0xa3473a, roughness: 0.88 }), pvc = K.mat("sw-pvc", { color: 0x8a8e93, roughness: 0.6 });
        K.box(o.w + 0.02, 0.6, 0.9, enc, 0, -1.1, 0, 0.02, g);
        for (var i = 0; i < o.ducts; i++) { var cx = (i % 3 - 1) * 0.26, cy = -1.0 + Math.floor(i / 3) * 0.26; var p = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, o.w + 0.04, 18), pvc); p.rotation.z = Math.PI / 2; p.position.set(0, cy + 0.12, cx); g.add(p); var cu = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, o.w + 0.06, 14), K.mat("sw-cu", { color: N.COPPER, metalness: 0.9, roughness: 0.3 })); cu.rotation.z = Math.PI / 2; cu.position.copy(p.position); g.add(cu); }
        for (var b = 0; b < o.branches; b++) { var z = (b - (o.branches - 1) / 2) * 0.9; K.bar([o.w / 2, -0.85, 0], [o.w / 2 + 2.5, -0.85, z * 2.2], 0.08, pvc, 14, g); }
        return shadowAll(g);
      }
    });

    /* SWITCHGEAR HANDLE. A medium voltage switchgear front section 0.8 x 2.3 m in powder coat with an inset nameplate panel
     * left blank, a cast lever 0.28 m on a rotary boss at 1.25 m, worn bare at the grip. Front on +z. userData.boss is the boss
     * centre. */
    K.define("switchgear_handle", {
      size: [0.8, 2.3, 0.6],
      options: { color: 0x9aa4ad, angle: -30 },
      note: "Medium voltage switchgear panel section with an operating lever on a rotary boss, illustrative and unmarked. userData.boss is the boss centre; angle is the lever angle in degrees.",
      anchor: "base",
      make: function (o) {
        var g = new THREE.Group(), pc = K.mat("sw-powder" + o.color, { color: o.color, roughness: 0.62, metalness: 0.15, clearcoat: 0.2 }, true);
        K.box(0.8, 2.3, 0.6, pc, 0, 0, 0, 0.012, g);
        K.box(0.7, 0.9, 0.01, K.mat("sw-panelin", { color: 0x8a949c, roughness: 0.55, metalness: 0.2 }), 0, 1.35, 0.302, 0.004, g);
        K.box(0.22, 0.08, 0.006, K.mat("sw-plate", { color: 0xd8d4c8, roughness: 0.4, metalness: 0.4 }), 0, 1.95, 0.31, 0.002, g);
        for (var i = 0; i < 6; i++) K.box(0.6, 0.012, 0.02, K.mat("sw-vent", { color: 0x50585f, roughness: 0.6 }), 0, 0.25 + i * 0.05, 0.302, 0, g);
        var by = 1.25, bz = 0.31, steel = K.mat("sw-cast", { color: 0x2b2f36, roughness: 0.35, metalness: 0.8 });
        var boss = K.cyl(0.07, 0.08, 0.06, steel, 0, 0, 0, 32); boss.rotation.x = Math.PI / 2; boss.position.set(0, by, bz + 0.03); g.add(boss);
        var lever = new THREE.Group(); lever.position.set(0, by, bz + 0.07); lever.rotation.z = o.angle * Math.PI / 180; g.add(lever);
        K.box(0.28, 0.045, 0.035, steel, 0.13, -0.022, 0, 0.012, lever);
        K.box(0.09, 0.05, 0.04, K.mat("sw-grip", { color: 0x8c8f92, roughness: 0.25, metalness: 0.95 }), 0.25, -0.025, 0, 0.015, lever);
        K.box(0.035, 0.11, 0.008, steel, 0.02, -0.1, 0.02, 0.004, lever);
        g.userData.boss = [0, by, bz + 0.07]; g.userData.keepOrigin = true;
        return shadowAll(g);
      }
    });

    /* LOCKOUT HASP. Steel scissor hasp jaws 0.04 x 0.115 m with six 10 mm holes, `locks` hardened padlocks 0.04 x 0.065 m
     * with chrome shackles in the first holes, and an optional blank card tag 0.075 x 0.145 m on a tie. Origin at the jaw ring. */
    K.define("lockout_hasp", {
      size: [0.12, 0.2, 0.03],
      options: { locks: 1, tag: true },
      note: "Lockout hasp with six holes, padlocks in the first `locks` holes, blank tag. Illustrative, unmarked.",
      anchor: "base",
      make: function (o) {
        var g = new THREE.Group(), st = K.mat("sw-hasp", { color: 0xc7ccd0, roughness: 0.3, metalness: 0.95 }), red = K.mat("sw-haspvinyl", { color: 0x2c3e66, roughness: 0.5 });
        var ring = new THREE.Mesh(new THREE.TorusGeometry(0.018, 0.004, 10, 24), st); g.add(ring);
        K.box(0.04, 0.115, 0.006, st, 0, -0.13, 0, 0.003, g);
        K.box(0.034, 0.03, 0.012, red, 0, -0.03, 0, 0.004, g);
        var holes = []; for (var i = 0; i < 6; i++) { var hx = (i % 2 ? 0.01 : -0.01), hy = -0.06 - Math.floor(i / 2) * 0.022; holes.push([hx, hy]); var h = new THREE.Mesh(new THREE.CircleGeometry(0.005, 14), K.mat("sw-hole", { color: 0x111216, roughness: 1 })); h.position.set(hx, hy, 0.0035); g.add(h); }
        var body = K.mat("sw-padlock", { color: 0xd8a33a, roughness: 0.4, metalness: 0.6 });
        for (var L = 0; L < o.locks; L++) { var p = holes[L]; var sh = new THREE.Mesh(new THREE.TorusGeometry(0.012, 0.0035, 10, 24, Math.PI), K.finish.chrome()); sh.position.set(p[0], p[1] - 0.004, 0.012); sh.rotation.z = Math.PI; g.add(sh); K.box(0.04, 0.05, 0.022, K.mat("sw-lockbody", { color: 0x2f3b55, roughness: 0.35, metalness: 0.5 }), p[0], p[1] - 0.07, 0.012, 0.006, g); }
        if (o.tag) { var tg = K.box(0.075, 0.145, 0.002, K.mat("sw-tag", { color: 0xf3efe4, roughness: 0.85 }), 0.05, -0.3, 0.02, 0.003, g); tg.rotation.z = 0.25; K.bar([0, -0.13, 0.01], [0.04, -0.23, 0.02], 0.0015, K.mat("sw-tie", { color: 0xe8e2d0, roughness: 0.6 }), 6, g); }
        g.userData.keepOrigin = true;
        return shadowAll(g);
      }
    });

    /* BOUND LEASE. A closed bound document `w` x `t` x `d` m with a blank cloth cover and screw posts, `years` straw tabs along
     * its fore edge (+z) at one pitch and `options` darker tabs each `optLen` times the year pitch long. No text anywhere. */
    K.define("bound_lease", {
      size: [0.24, 0.04, 0.31],
      options: { w: 0.24, t: 0.04, d: 0.31, years: 0, opts: 0, optLen: 1 },
      note: "Closed bound lease with blank cover and fore edge tabs, illustrative. years straw tabs, opts darker tabs each optLen year pitches long, all read from FIG by the frame. userData.tabs is the tab count drawn.",
      make: function (o) {
        var g = new THREE.Group(), cloth = K.mat("sw-cloth", { color: 0x2f3a5c, roughness: 0.8, sheen: 0.4 }, true), pages = K.mat("sw-pages", { color: 0xefe7d6, roughness: 0.9 });
        K.box(o.w, 0.004, o.d, cloth, 0, 0, 0, 0.002, g); K.box(o.w - 0.01, o.t - 0.008, o.d - 0.012, pages, 0.003, 0.004, 0, 0.001, g); K.box(o.w, 0.004, o.d, cloth, 0, o.t - 0.004, 0, 0.002, g);
        K.box(0.018, o.t, o.d, cloth, -o.w / 2 + 0.009, 0, 0, 0.004, g);
        [-0.1, 0, 0.1].forEach(function (z) { K.cyl(0.006, 0.006, o.t + 0.003, K.finish.chrome(), -o.w / 2 + 0.03, 0, z, 16, g); });
        var straw = K.mat("sw-tabstraw", { color: N.STRAW, roughness: 0.6 }), mesq = K.mat("sw-tabmesq", { color: 0x6e7a5a, roughness: 0.6 });
        var total = o.years + o.opts * o.optLen, pitch = (o.w - 0.04) / Math.max(1, total), x = -o.w / 2 + 0.03, n = 0;
        for (var i = 0; i < o.years; i++) { K.box(pitch * 0.82, 0.003, 0.02, straw, x + pitch / 2, 0.006 + (i % 3) * 0.009, o.d / 2 + 0.008, 0.001, g); x += pitch; n++; }
        for (var j = 0; j < o.opts; j++) { K.box(pitch * o.optLen * 0.9, 0.003, 0.02, mesq, x + pitch * o.optLen / 2, 0.012 + (j % 2) * 0.012, o.d / 2 + 0.008, 0.001, g); x += pitch * o.optLen; n++; }
        g.userData.tabs = n;
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
