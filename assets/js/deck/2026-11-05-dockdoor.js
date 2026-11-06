/* deck/2026-11-05-dockdoor.js — the chassis for the 2026-11-05 deck: Applied Optoelectronics' third quarter results,
 * filed with the SEC on November 5th, 2026, saying its 2027 US capacity expansion will take longer because obtaining
 * the electrical power it needs is taking longer than expected (tx-2026-0241).
 *
 * THE VISUAL ARGUMENT. The waiting building. A new manufacturing bay taped out for machines and lit only by the last
 * of the day through its open dock door, because power is the one thing it waits for. The company's own targets are
 * taped on that floor at one scale, one machine pad per 50,000 pieces a month (figures.json pad_unit, never printed):
 * one pad lit on the cover, ten on frame 5 for the end of 2026, all twenty on the close for the end of 2027.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky with one warm seam low on the key's side.
 * Inside the bay there is no light of its own. The door faces the key, so the seam through the opening is the only
 * light, and the floor takes it as a long wedge. Outside, the subject stands in a pool and the world behind goes dark.
 *
 * THE LIGHT is azimuth -55, elevation 6, the deck's one key. CH.bay() turns the bay so its door wall faces that key:
 * in the bay's own frame the door is at -z, the camera looks toward -z, and every cast runs toward the camera. TXBENCH
 * reliefs read the same declaration, raked low.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `dock_door` (a rolled steel dock door opening with
 * guide tracks, a coil drum housing, the raised curtain's bottom slats, rubber bumpers and jamb seals), `osfp_module`
 * (an OSFP class optical transceiver, 0.108 m long, bead blasted shell, finned black lid, pull tab and gold edge
 * fingers), `survey_stake` (a wood lath with flagging and a nail for the string line) and `conduit_stub` (a capped grey
 * PVC conduit stub in a concrete collar). Drawn to illustrate, to no maker's or site's design, in the kit's conventions
 * (metres, y up, origin on the ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is dusk_gold, #E0956A, and it means ONE thing: a capacity target the company states, as gold floor tape
 * on a machine pad and as the string line along the staked lease. Nothing else wears it.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models, the bay and the way type is
 * seated. Every count a frame draws is read from figures.json in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("dockdoor.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "dockdoor",
    light: { az: -55, el: 6 },
    sky: "lastLight",
    ground: "#0A0A0C",
    material: "#5F5A52",
    accent: "#E0956A",
    grade: {
      exposure: 0, saturation: 1.0, contrast: 1.08, filmic: true,
      lift: [0.002, 0.002, 0.004], gain: [1.0, 1.0, 1.0], vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.14, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261105 },
      aberration: 0, dither: true, sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080; N.H = 1350; N.SEED = 20261105; N.INK = "#EEEAE3";
  N.GOLD = 0xE0956A;       /* brand.yaml's dusk_gold: a stated capacity target, and nothing else */
  N.GREY_TAPE = 0x8d8f8c;  /* a pad not yet counted */
  N.GREY_LIT = 0x5c5e5c;   /* the same grey held outside the tone curve, so an uncounted pad in the dark still reads as a pad */
  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.dock_door) return;
    function shade(o) { o.traverse(function (c) { if (c.isMesh) { c.castShadow = c.receiveShadow = true; } }); return o; }
    var PAINT = K.mat("dd-paint", { color: 0x3b4046, metalness: 0.55, roughness: 0.48 });
    var RUBBER = K.mat("dd-rubber", { color: 0x111214, roughness: 0.92, metalness: 0 });
    var GALV = K.mat("dd-galv", { color: 0x9ea3a6, metalness: 0.85, roughness: 0.42 });

    /* A DOCK DOOR: a rolled steel door opening `w` wide and `h` tall in a wall whose inside face is z = 0, the wall
     * running back to -z. The curtain is raised: its bottom bar and two slats show under the coil drum housing at the
     * head. Guide tracks stand proud of the inside face on both jambs, seals line the jambs, and two rubber bumpers
     * sit at dock height on the outside face. No wall is built here; the frame builds the wall around the opening. */
    K.define("dock_door", {
      size: [5.0, 5.7, 0.9],
      options: { w: 4.3, h: 4.6, slats: 3, seed: 1 },
      note: "A rolled steel dock door opening with guide tracks, coil drum housing, raised curtain bottom slats, jamb seals and rubber bumpers; the wall is the frame's.",
      make: function (o) {
        var G = new THREE.Group(), w = o.w || 4.3, h = o.h || 4.6;
        /* guide tracks: steel channels proud of the inside face */
        [-1, 1].forEach(function (s) {
          var tr = K.box(0.13, h + 0.35, 0.11, PAINT, s * (w / 2 + 0.065), 0, 0.055, 0.008); G.add(tr);
          var lip = K.box(0.03, h + 0.35, 0.05, PAINT, s * (w / 2 + 0.005), 0, 0.12, 0.004); G.add(lip);
          var seal = K.box(0.05, h, 0.05, RUBBER, s * (w / 2 - 0.02), 0, -0.05, 0.01); G.add(seal);
          /* bumpers on the outside face at dock height */
          var bp = K.box(0.26, 0.5, 0.12, RUBBER, s * (w / 2 - 0.55), 0.55, -0.27, 0.02); G.add(bp);
          [0.62, 0.92].forEach(function (y) { var b = K.cyl(0.012, 0.012, 0.03, GALV, 0, 0, 0, 10); b.rotation.x = Math.PI / 2; b.position.set(s * (w / 2 - 0.55), y, -0.34); G.add(b); });
        });
        /* coil drum housing at the head, inside */
        var hood = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, w + 0.5, 28, 1, false, 0, Math.PI * 1.25), PAINT);
        hood.rotation.z = Math.PI / 2; hood.position.set(0, h + 0.42, 0.36); G.add(hood);
        var cap = [-1, 1].map(function (s) { var c = K.cyl(0.36, 0.36, 0.03, PAINT, 0, 0, 0, 28); c.rotation.z = Math.PI / 2; c.position.set(s * (w / 2 + 0.26), h + 0.42, 0.36); G.add(c); return c; });
        /* the raised curtain's bottom slats and bar, showing under the head */
        var ns = Math.max(1, o.slats || 3), slH = 0.085;
        for (var i = 0; i < ns; i++) {
          var sl = K.box(w + 0.1, slH - 0.008, 0.035, PAINT, 0, h - (i + 1) * slH, 0.0, 0.006); G.add(sl);
        }
        var bar = K.box(w + 0.1, 0.06, 0.06, GALV, 0, h - ns * slH - 0.06, 0.0, 0.008); G.add(bar);
        var astr = K.box(w + 0.1, 0.03, 0.07, RUBBER, 0, h - ns * slH - 0.09, 0.0, 0.008); G.add(astr);
        /* the dock leveller lip at the sill, a steel plate flush with the floor */
        var lev = K.box(w - 0.2, 0.02, 0.6, K.mat("dd-tread", { color: 0x2c2f33, metalness: 0.6, roughness: 0.5 }), 0, 0, 0.3, 0.004); G.add(lev);
        G.userData.opening = { w: w, h: h };
        return shade(G);
      }
    });

    /* AN OSFP CLASS OPTICAL TRANSCEIVER, 0.1078 m long (along z, the optical end at +z), 0.0225 m wide, 0.013 m
     * tall. A bead blasted aluminium lower shell, a black anodised finned lid with fins running its length, two
     * receptacle mouths at the optical end, a black polymer pull tab trailing from it, and a PCB tongue at the host
     * end with gold edge fingers on its top face. Drawn to illustrate, to no maker's design. */
    K.define("osfp_module", {
      size: [0.0225, 0.0135, 0.155],
      options: { tab: true, seed: 1 },
      note: "An OSFP class optical transceiver, bead blasted shell, finned black lid, receptacle mouths, pull tab and gold edge fingers.",
      make: function (o) {
        var G = new THREE.Group(), L = 0.1078, Wd = 0.0225, Hs = 0.0072;
        var ALU = K.mat("osfp-alu", { color: 0xb9bdc1, metalness: 1.0, roughness: 0.46 });
        var ANOD = K.mat("osfp-anod", { color: 0x17181b, metalness: 0.7, roughness: 0.34 });
        var GOLDM = K.mat("osfp-gold", { color: 0xd7b46a, metalness: 1.0, roughness: 0.22 });
        var PCB = K.mat("osfp-pcb", { color: 0x0f3a2a, metalness: 0.1, roughness: 0.5 });
        var TAB = K.mat("osfp-tab", { color: 0x141516, metalness: 0.0, roughness: 0.62 });
        var HOLE = K.mat("osfp-hole", { color: 0x050506, metalness: 0, roughness: 0.9 });
        var shell = TXT.roundedBox(Wd, Hs, L, 0.0009, ALU); shell.position.set(0, Hs / 2, 0); G.add(shell);
        /* the lid: a base plate and fins along the length */
        var lidT = 0.0016, lid = TXT.roundedBox(Wd - 0.0006, lidT, L * 0.82, 0.0005, ANOD); lid.position.set(0, Hs + lidT / 2, -L * 0.04); G.add(lid);
        var nf = 13, fh = 0.0042, ft = 0.00062, pitch = (Wd - 0.002) / (nf - 1);
        var finGeo = TXT.roundedBox(ft, fh, L * 0.8, 0.00025);
        for (var i = 0; i < nf; i++) { var f = new THREE.Mesh(finGeo, ANOD); f.position.set(-Wd / 2 + 0.001 + i * pitch, Hs + lidT + fh / 2, -L * 0.04); G.add(f); }
        /* the optical end: a bezel with two receptacle mouths */
        var bez = TXT.roundedBox(Wd, Hs + 0.0006, 0.004, 0.0007, ALU); bez.position.set(0, (Hs + 0.0006) / 2, L / 2 - 0.002); G.add(bez);
        [-1, 1].forEach(function (s) { var hl = TXT.roundedBox(0.0068, 0.0042, 0.0012, 0.0006, HOLE); hl.position.set(s * 0.0052, Hs * 0.5, L / 2 + 0.0001); G.add(hl); });
        /* the pull tab: a strap from the bezel, curving down to the bench, a loop at its end */
        if (o.tab !== false) {
          var pts = [], n = 18;
          for (var k = 0; k <= n; k++) { var t = k / n; pts.push(new THREE.Vector3(0, Hs * 0.62 - 0.0055 * t * t, L / 2 + 0.002 + 0.044 * t)); }
          var curve = new THREE.CatmullRomCurve3(pts);
          var strapShape = new THREE.Shape(); strapShape.moveTo(-0.0058, -0.0007); strapShape.lineTo(0.0058, -0.0007); strapShape.lineTo(0.0058, 0.0007); strapShape.lineTo(-0.0058, 0.0007); strapShape.lineTo(-0.0058, -0.0007);
          var strap = new THREE.Mesh(new THREE.ExtrudeGeometry(strapShape, { steps: 24, bevelEnabled: false, extrudePath: curve }), TAB); G.add(strap);
          var loop = new THREE.Mesh(new THREE.TorusGeometry(0.0062, 0.0014, 10, 28), TAB); loop.rotation.x = Math.PI / 2; loop.position.set(0, Hs * 0.62 - 0.0055 + 0.0006, L / 2 + 0.002 + 0.044 + 0.005); loop.scale.set(1, 1.25, 1); G.add(loop);
        }
        /* the host end: the PCB tongue and its gold fingers */
        var tongue = TXT.roundedBox(Wd - 0.003, 0.0011, 0.0075, 0.0003, PCB); tongue.position.set(0, Hs * 0.42, -L / 2 - 0.0035); G.add(tongue);
        var fg = new THREE.BoxGeometry(0.00042, 0.0002, 0.0042), nfg = 26, fp = (Wd - 0.0055) / (nfg - 1);
        for (var j = 0; j < nfg; j++) { var g = new THREE.Mesh(fg, GOLDM); g.position.set(-Wd / 2 + 0.00275 + j * fp, Hs * 0.42 + 0.00065, -L / 2 - 0.0042); G.add(g); }
        G.userData.length = L;
        return shade(G);
      }
    });

    /* A SURVEY STAKE: a pine lath 0.038 x 0.012 m, 0.62 m out of the ground with a pointed foot below, a nail near
     * the top for the string line, and flagging tape tied below the top when `flag` is set. */
    K.define("survey_stake", {
      size: [0.06, 0.64, 0.03],
      options: { flag: false, lean: 0, seed: 1 },
      note: "A wood survey lath with a string nail and optional flagging tape.",
      make: function (o) {
        var G = new THREE.Group(), r = lcg(o.seed || 1), H = 0.62;
        var WOOD = K.mat("ss-wood", { color: 0xcdb48c, roughness: 0.82, metalness: 0 });
        var lath = TXT.roundedBox(0.038, H, 0.012, 0.002, WOOD); lath.position.set(0, H / 2, 0); G.add(lath);
        var top = TXT.roundedBox(0.04, 0.012, 0.014, 0.002, K.mat("ss-wood-end", { color: 0xb59a72, roughness: 0.85 })); top.position.set(0, H + 0.004, 0); G.add(top);
        var nail = K.cyl(0.0022, 0.0022, 0.03, GALV, 0, 0, 0, 8); nail.rotation.x = Math.PI / 2; nail.position.set(0, H - 0.09, 0.016); G.add(nail);
        if (o.flag) {
          var FLAG = K.mat("ss-flag", { color: 0xe2571e, roughness: 0.7, side: THREE.DoubleSide });
          for (var k = 0; k < 2; k++) {
            var len = 0.24 + r() * 0.06, pts = [];
            for (var i = 0; i <= 10; i++) { var t = i / 10; pts.push(new THREE.Vector3((k ? 1 : -1) * (0.012 + 0.05 * t), H - 0.05 - len * t * t * 0.9, 0.008 + 0.01 * Math.sin(t * 3 + k))); }
            var tape = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 16, 0.006, 3, false), FLAG);
            tape.scale.set(1, 1, 0.35); G.add(tape);
          }
          var knot = K.box(0.044, 0.02, 0.018, FLAG, 0, H - 0.07, 0, 0.003); G.add(knot);
        }
        G.rotation.z = (o.lean || 0) * (r() - 0.5);
        G.userData.nailY = H - 0.09;
        return shade(G);
      }
    });

    /* A CAPPED CONDUIT STUB: grey schedule 40 PVC, 0.1 m across, 0.42 m out of a concrete collar, a slip cap on top,
     * with nothing in it. */
    K.define("conduit_stub", {
      size: [0.24, 0.48, 0.24],
      options: { height: 0.42, seed: 1 },
      note: "A capped grey PVC conduit stub in a concrete collar, empty.",
      make: function (o) {
        var G = new THREE.Group(), h = o.height || 0.42;
        var PVC = K.mat("cs-pvc", { color: 0x8e9294, roughness: 0.55, metalness: 0 });
        var collar = K.cyl(0.11, 0.12, 0.05, K.finish.concrete(), 0, 0, 0, 24); G.add(collar);
        var pipe = K.cyl(0.05, 0.05, h, PVC, 0, 0.04, 0, 24); G.add(pipe);
        var capm = K.cyl(0.056, 0.056, 0.055, PVC, 0, 0.04 + h - 0.03, 0, 24); G.add(capm);
        var band = K.cyl(0.0565, 0.0565, 0.006, K.mat("cs-band", { color: 0x6c7072, roughness: 0.6 }), 0, 0.04 + h - 0.03, 0, 24); G.add(band);
        return shade(G);
      }
    });
  };

  /* ---- THE BAY: the deck's one interior, the building that waits on power ------------------
   * CH.bay(THREE, R, TXT, K, { pads, gold, tapeLit }) builds it in a group turned so its dock door faces the
   * declared key: in the group's own frame the door wall is at z = -D/2, the room runs toward +z, and the camera
   * stands on the +z side looking toward -z. Returns { G, pads, door, D, Wd, Hh, toWorld(p) }.
   * `pads` is the pad count (figures.json), laid in rows of five from the door; the first `gold` pads from the door
   * wear the accent tape, or the pads `isGold(i, col, row)` names. The low key through the door lights a stripe
   * down the middle column (col 2), so a lit pad is chosen by where it stands. The red oxide columns stand between the rows. */
  N.BAY = { Wd: 30, D: 46, Hh: 9.6 };
  N.KEY_SCALE = 1;
  /* the room's options, so a frame lays the bay's floor and walls with its own TXT.interior call and hands the
   * room to CH.bay: an epoxy floor with no saw joints, dark tilt wall, a ceiling, no window (the door is the window) */
  N.bayRoom = function (o) { o = o || {}; return { w: N.BAY.Wd, d: N.BAY.D, h: N.BAY.Hh, floor: "concrete", joints: false, wall: 0x2b2926, window: null, ceiling: true, light: o.light == null ? 0.24 : o.light }; };
  N.tapeGold = function (THREE) { return N._tg || (N._tg = new THREE.MeshStandardMaterial({ color: 0xd2682a, emissive: 0xd06a28, emissiveIntensity: 0.5, roughness: 0.92, metalness: 0.0 })); };
  N.tapeGrey = function (THREE) { return N._tq || (N._tq = new THREE.MeshStandardMaterial({ color: 0x5a5c5a, emissive: 0x2e302e, emissiveIntensity: 0.3, roughness: 0.5, metalness: 0.02 })); };
  /* THE DOOR'S SPILL: the sky through the opening lays a warm wedge on the floor from any viewpoint, a wide soft spot at
   * the door head aimed down the bay's axis, casting, in the seam's hue. It stands for the sky light the opening admits,
   * so it only ever sits AT the door. */
  N.doorSpill = function (THREE, R, B, o) {
    o = o || {};
    var sp = new THREE.SpotLight(0xffb57c, o.i || 160, o.reach || 48, o.angle || 0.42, 0.75, 1.6);
    sp.position.fromArray(B.toWorld([0, 4.2, -B.D / 2 - 1.2])); sp.target.position.fromArray(B.toWorld([0, 0, -B.D / 2 + (o.at || 16)]));
    sp.castShadow = true; sp.shadow.mapSize.set(2048, 2048); sp.shadow.bias = -0.0004; sp.shadow.normalBias = 0.02;
    R.scene.add(sp); R.scene.add(sp.target); return sp;
  };
  N.bayYaw = function (THREE, TXT) {
    var s = TXT.sunDir(); return Math.atan2(-s.x, -s.z);
  };
  N.bay = function (THREE, R, TXT, K, o) {
    o = o || {};
    var Wd = N.BAY.Wd, D = N.BAY.D, Hh = N.BAY.Hh;
    var room = o.room || TXT.interior(R, N.bayRoom(o));
    var G = new THREE.Group(); G.rotation.y = N.bayYaw(THREE, TXT); R.scene.add(G);
    G.add(room);
    /* the back wall with the dock door opening, built to cast so only the doorway lets the seam in */
    room.children.slice().forEach(function (m) { if (m.isMesh && Math.abs(m.position.z + D / 2) < 0.01 && Math.abs(m.position.x) < 0.01 && Math.abs(m.position.y - Hh / 2) < 0.01) room.remove(m); });
    var wallM = new THREE.MeshStandardMaterial({ color: 0x2b2926, roughness: 0.93, metalness: 0 });
    var dw = 4.3, dh = 4.6, t = 0.25, dx = o.doorX || 0;
    function wall(w, h, x, y) { var m = TXT.roundedBox(w, h, t, 0.02, wallM); m.position.set(x, y, -D / 2); m.castShadow = true; m.receiveShadow = true; G.add(m); return m; }
    var lw = (Wd / 2 + dx) - dw / 2, rw = (Wd / 2 - dx) - dw / 2;
    wall(lw, Hh, -Wd / 2 + lw / 2, Hh / 2);
    wall(rw, Hh, Wd / 2 - rw / 2, Hh / 2);
    wall(dw, Hh - dh, dx, dh + (Hh - dh) / 2);
    var door = K.make("dock_door", { w: dw, h: dh }); door.position.set(dx, 0, -D / 2 + t / 2); G.add(door);
    /* the roof steel and columns, red oxide primer */
    /* two lines of columns at x = -7.5 and +7.5, just outside the pad grid, so no column ever stands between a lens on the
     * bay's axis and a pad; joistBays 0 on a frame whose roof sits behind the type */
    var frame = K.make("structural_frame", { cols: 2, rows: 4, bay: 15, height: Hh - 0.2, girts: [], bracing: false, primer: 0x8c4630, joistBays: o.joists === false ? 0 : null });
    frame.position.set(0, 0, 0.6); G.add(frame);
    /* the pads: rows of five, the first `gold` from the door gold, the rest grey */
    var n = o.pads || 0, gold = o.gold || 0, pads = [];
    /* the pad grid: kit machine_pads at 0.62 scale, a 2.0 by 2.2 m bench bay, five to a row at 3.0 m by 3.4 m, so all
     * twenty sit whole inside one lens; the middle column (col 2, x = 0) lies in the door's stripe */
    var cols = 5, px = 3.0, pz = 3.4, z0 = -D / 2 + 8.0, PS = 0.62;
    for (var i = 0; i < n; i++) {
      var c = i % cols, rr = Math.floor(i / cols), isGold = o.isGold ? !!o.isGold(i, c, rr) : i < gold;
      var pad = K.make("machine_pad", { tape: isGold ? N.GOLD : (o.greyLit ? N.GREY_LIT : N.GREY_TAPE), tapeLit: isGold ? o.tapeLit !== false : !!o.greyLit, cordTop: Hh - 0.4 });
      pad.scale.setScalar(PS); pad.position.set((c - (cols - 1) / 2) * px, 0, z0 + rr * pz); pad.userData.gold = isGold; G.add(pad); pads.push(pad);
      /* the tape as a lit material with a little glow of its own: it brightens in the door light and still counts outside it */
      pad.children.slice().forEach(function (m) { if (m.isMesh && Math.abs(m.position.y - 0.005) < 0.0005) pad.remove(m); });
      /* floor tape about 0.11 m wide in the world, the width a layout crew lays, so the outline holds at feed size */
      (function (pad, mat) {
        var bw = 3.2, bd = 3.6, tw = 0.11 / PS, th = 0.006 / PS;
        [[bw, tw, 0, -bd / 2 + tw / 2], [bw, tw, 0, bd / 2 - tw / 2], [tw, bd - 2 * tw, -bw / 2 + tw / 2, 0], [tw, bd - 2 * tw, bw / 2 - tw / 2, 0]].forEach(function (t) {
          var m = TXT.roundedBox(t[0], th, t[1], th * 0.45, mat); m.position.set(t[2], th / 2 + 0.003, t[3]); m.receiveShadow = true; m.userData.txWear = false; pad.add(m);
        });
      })(pad, isGold ? N.tapeGold(THREE) : N.tapeGrey(THREE));
      if (o.cords === false) pad.children.slice().forEach(function (m) { if (m.position.y > 1.5) pad.remove(m); });
    }
    /* the epoxy: the room's floor made glossy dark slate so the door's light lies on it as a sheen */
    R.scene.traverse(function (m) { if (m.isMesh && m.geometry && m.geometry.type === "PlaneGeometry" && m.material && m.material.map && m.geometry.parameters.width >= Wd * 2) { m.material = m.material.clone(); m.material.color.set(0x55585b); m.material.roughness = 0.52; m.material.metalness = 0.05; m.material.bumpMap = null; m.material.normalMap = null; m.material.bumpScale = 0; m.material.needsUpdate = true; } });
    G.updateMatrixWorld(true);
    return { G: G, room: room, pads: pads, door: door, frame: frame, D: D, Wd: Wd, Hh: Hh,
      toWorld: function (p) { return new THREE.Vector3(p[0], p[1], p[2]).applyMatrix4(G.matrixWorld).toArray(); } };
  };
  /* the sun's light through the door, kept to the deck's one key: the rig at the bay with a shadow box the room's size */
  /* inside an unpowered bay the preset's rim and fill are sky light on walls no window reaches: turned down after a
   * frame's TXT.deckRig call, the key left as it is */
  N.bayFill = function (R, keep) {
    R.scene.traverse(function (l) { if (l.isLight && !l.castShadow && !l.isAmbientLight && !l.isHemisphereLight && l.userData.txRole !== "key") { l.intensity *= keep == null ? 0.25 : keep; } });
  };
  N.bayRig = function (TXT, R, W, target, o) {
    o = o || {};
    TXT.deckRig(R, N.rigSpec(W, o.size || 70, 4096), N.rigOpts(target || [0, 0, 0], { distance: o.distance || 90, shadowFar: o.far || 200, normalBias: 0.03 }));
    N.unacne(R, 0.03);
    /* the preset's rim and fill are sky light; inside an unpowered bay they would light walls no window reaches */
    R.scene.traverse(function (l) { if (l.isLight && !l.castShadow && !l.isAmbientLight && !l.isHemisphereLight && l.userData.txRole !== "key") { l.intensity *= o.fillKeep == null ? 0.25 : o.fillKeep; } });
  };

  /* ---- frame helpers, carried from the 2026-11-04 chassis ---------------------------------- */
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
    /* the key is the seam's warm light, and held a step down so a floor it grazes never clips to white */
    return Object.assign({}, W.rig, { rim: rim, key: Object.assign({}, W.rig.key, { color: 0xffc596, i: (W.rig.key.i || 3) * (N.KEY_SCALE || 1), shadowSize: size || 14, mapSize: map || 2048 }) });
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
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".lab.ru { color:#C99474; }",
      ".lab.gold { color:#E0956A; }",
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
  /* THE TRACTOR'S HEADLAMPS, ON. The kit's lens material is shared, so lighting it lights every tractor in the frame,
   * which is right: every truck in this deck is running. Glows sit on the four round lamps (the kit's bezels at x
   * ±0.78 ±0.075, y 1.52 above the tractor's base, just behind the bumper's face), and one spot throws their light down
   * the lane ahead. The truck must face +z in its own frame. */
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
  global.CH = N;
})(this);
