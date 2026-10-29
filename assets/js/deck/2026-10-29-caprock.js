/* deck/2026-10-29-caprock.js — the chassis for the 2026-10-29 deck: Soluna Holdings and Applied Digital's planned AI
 * data center, Dorothy 3, beside the Briscoe Wind Farm near Silverton in Briscoe County (tx-2026-0233).
 *
 * THE VISUAL ARGUMENT. One county road on the Caprock. The wind farm and its substation stand on the west side, the
 * pasture where Dorothy 3 is planned lies on the east side, and the road between them is the "directly across from" the
 * record states. The measure is the flanged wind tower section: one section stands for a fixed number of megawatts, a
 * drawing unit each frame reads from figures.json, so the load is measured in the wind's own parts.
 *
 * THE WORLD. lastLight, a STAGED world: the sun just down, a near black sky, one warm seam low on the key's side, the
 * subject in a pool of light and the world behind it gone dark.
 *
 * THE LIGHT is azimuth -78, elevation 10. +x is east and +z is south, the road runs north and south along x = 0. The last
 * light stands low in the west south west. A camera looking north (-z) has the key on its LEFT, every lit edge is on the
 * left, and every cast runs long to the right. A camera looking west sees the turbines against the warm seam.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `tower_section` (one flanged wind tower can, 4.3 m across
 * and 1.0 m tall), `section_stack` (n of them bolted into a column), `survey_stake` (a pine lath with flagging) and
 * `gate_lock` (a chain and padlock). All are drawn to illustrate, in the kit's conventions (metres, y up, origin on the
 * ground, front on +z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is mesquite, #6E7A5A, and it means ONE thing: what is planned for Dorothy 3.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way type is seated.
 * Every frame composes its own picture, and every quantity a frame draws is read from figures.json in that frame's own
 * code. The chassis types no figure of the story.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("caprock.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "caprock",
    light: { az: -78, el: 10 },
    sky: "lastLight",
    ground: "#08060F",
    material: "#DFE1DD",
    accent: "#6E7A5A",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.86, strength: 0.12, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261029 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261029;
  N.ACCENT = 0x6e7a5a;   /* mesquite, brand.yaml's deck token, and it means ONE thing: what is planned for Dorothy 3 */
  N.INK = "#ECE8DF";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */
  /* TOWER PAINT: a satin off white with faint roller tooth in a bump map, so a section reads as painted steel and
   * never as a white plastic tube under the low key */
  function tooth(THREE, seed) {
    var c = document.createElement("canvas"); c.width = c.height = 256; var x = c.getContext("2d"), r = lcg(seed);
    x.fillStyle = "#808080"; x.fillRect(0, 0, 256, 256);
    for (var i = 0; i < 7000; i++) { var v = Math.floor(118 + r() * 20); x.fillStyle = "rgb(" + v + "," + v + "," + v + ")"; x.fillRect(r() * 256, r() * 256, 1.4, 1.4); }
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t;
  }
  /* RED DUST, a vertical gradient map: the bottom of a section that stood in Caprock wind carries red bed dust */
  function dustMap(THREE) {
    var c = document.createElement("canvas"); c.width = 8; c.height = 256; var x = c.getContext("2d");
    var g = x.createLinearGradient(0, 0, 0, 256); g.addColorStop(0, "#ffffff"); g.addColorStop(0.7, "#f6efe8"); g.addColorStop(1, "#d6b7a2");
    x.fillStyle = g; x.fillRect(0, 0, 8, 256);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
  }
  N.mats = function (THREE, K) {
    if (N._m) return N._m;
    var b = tooth(THREE, N.SEED); b.repeat.set(6, 2);
    var m = {
      paint: new THREE.MeshPhysicalMaterial({ color: 0xdcded9, roughness: 0.46, metalness: 0.0, clearcoat: 0.25, clearcoatRoughness: 0.5, bumpMap: b, bumpScale: 0.6 }),
      paintDusty: new THREE.MeshPhysicalMaterial({ color: 0xdcded9, map: dustMap(THREE), roughness: 0.55, metalness: 0.0, bumpMap: b, bumpScale: 0.6 }),
      machined: new THREE.MeshStandardMaterial({ color: 0x9da2a6, roughness: 0.3, metalness: 0.85 }),
      galv: new THREE.MeshStandardMaterial({ color: 0xa3a8ab, roughness: 0.5, metalness: 0.55 }),
      galvLit: new THREE.MeshStandardMaterial({ color: 0xd3d7d9, roughness: 0.3, metalness: 0.4 }),
      bolt: new THREE.MeshStandardMaterial({ color: 0x55595d, roughness: 0.45, metalness: 0.7 }),
      /* the accent holds its own hex as emission with a dim albedo under it, so the rim still turns with the light and
       * reads as paint, and the tone curve can't grey it (queue tone-curve-greys-a-thin-accent) */
      rimPlan: new THREE.MeshStandardMaterial({ color: new THREE.Color(N.ACCENT).multiplyScalar(0.45), roughness: 0.5, metalness: 0, emissive: N.ACCENT, emissiveIntensity: 1.9, toneMapped: false }),
      pine: K.mat("cp_pine", { color: 0xb59a72, roughness: 0.86 }),
      flag: new THREE.MeshStandardMaterial({ color: new THREE.Color(N.ACCENT).multiplyScalar(0.5), roughness: 0.7, emissive: N.ACCENT, emissiveIntensity: 1.3, toneMapped: false, side: THREE.DoubleSide }),
      chain: new THREE.MeshStandardMaterial({ color: 0x6b6f72, roughness: 0.42, metalness: 0.8 }),
      brass: new THREE.MeshStandardMaterial({ color: 0x8a7444, roughness: 0.35, metalness: 0.85 })
    };
    N._m = m;
    return m;
  };

  /* ---- the kit models this deck builds ---------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.tower_section) return;
    var M = N.mats(THREE, K);
    var RAD = 2.15, H = 3.0, FL = 2.32, FT = 0.1;
    function shade(o) { o.traverse(function (c) { if (c.isMesh) { c.castShadow = c.receiveShadow = true; } }); return o; }

    /* ONE CAN OF A WIND TOWER: a rolled steel shell 3.0 m tall, so a stack of thirty stands at the kit turbine's own hub height, that TAPERS like a real tubular tower, narrowing by
     * TAPER metres of radius per metre of height (the kit wind_turbine's own rate, 2.15 m at the foot to 1.40 m at 88 m),
     * with one flush bolted flange at its foot that stands a few centimetres proud and catches the key as one lit line.
     * Options: r0 (radius at its foot), rim 'galv' (what exists) or 'plan' (the accent band painted on the flange's outer
     * face, what is planned), dusty (red dust at the foot), top (the top flange with its open bore), door (the tower's
     * base door and steel steps, so the column reads as a wind tower's own base). Drawn to illustrate. */
    var TAPER = (2.15 - 1.4) / 88;
    K.define("tower_section", {
      size: [FL * 2, H, FL * 2],
      options: { r0: RAD, rim: "galv", dusty: false, top: false, door: false, bolts: 40 },
      note: "One flanged wind tower can, 3.0 m tall, tapering at the kit turbine's rate, a drawing unit. r0, rim galv|plan, dusty, top, door.",
      make: function (o) {
        var g = new THREE.Group(), r0 = o.r0 || RAD, r1 = r0 - TAPER * H;
        var shell = new THREE.Mesh(new THREE.CylinderGeometry(r1, r0 - TAPER * FT, H - FT, 96, 1, true), o.dusty ? M.paintDusty : M.paint);
        shell.position.y = FT + (H - FT) / 2; g.add(shell);
        /* the foot flange, a bolted lip 9 cm proud of the shell with a chamfered top edge, so every section joint catches the key
         * as one lit tick with a shadow line under it, the way a tower's flanges read from the ground */
        var ro = r0 + 0.09;
        var prof = [[r0 - 0.1, 0], [ro, 0], [ro, FT - 0.02], [ro - 0.02, FT], [r0 - 0.1, FT]].map(function (p) { return new THREE.Vector2(p[0], p[1]); });
        /* a galvanized flange is lighter and less mirror-like than machined steel, so it catches the key as a lit tick */
        var fl = new THREE.Mesh(new THREE.LatheGeometry(prof, 128), o.rim === "plan" ? M.machined : M.galvLit); g.add(fl);
        if (o.rim === "plan") {
          /* a painted band on the shell just above the flange, flush, as a planned can would carry a mark */
          var bh = 0.6, rb = r0 - TAPER * (FT + bh / 2) + 0.004;
          var band = new THREE.Mesh(new THREE.CylinderGeometry(rb - TAPER * bh / 2, rb + TAPER * bh / 2, bh, 128, 1, true), M.rimPlan);
          band.position.y = FT + bh / 2; g.add(band);
        }
        /* bolt heads on the flange's top face */
        var nb = o.bolts || 40, bg = new THREE.CylinderGeometry(0.022, 0.022, 0.03, 6), list = [];
        for (var i = 0; i < nb; i++) { var a = i / nb * Math.PI * 2; list.push([Math.cos(a) * (r0 + 0.012), FT + 0.015, Math.sin(a) * (r0 + 0.012), -a, 1]); }
        K.instances(bg, M.bolt, list, g);
        if (o.door) {
          /* the tower's base door with a steel stair and landing, on the +z face, as the kit turbine draws it */
          var dz = r0 - 0.02;
          var frame = TXT.roundedBox(1.0, 0.9, 0.1, 0.03, M.paint); frame.position.set(0, 0.55, dz + 0.03); g.add(frame);
          var door = TXT.roundedBox(0.8, 0.8, 0.04, 0.02, K.mat("cp_door", { color: 0xb5b8b4, roughness: 0.45 })); door.position.set(0, 0.55, dz + 0.07); g.add(door);
        }
        if (o.top) {
          var tp = new THREE.Mesh(new THREE.LatheGeometry([[r1 - 0.1, 0], [r1 + 0.04, 0], [r1 + 0.04, FT], [r1 - 0.1, FT]].map(function (p) { return new THREE.Vector2(p[0], p[1]); }), 128), M.machined);
          tp.position.y = H - FT; g.add(tp);
          var bore = new THREE.Mesh(new THREE.CircleGeometry(r1 - 0.1, 64), new THREE.MeshStandardMaterial({ color: 0x0c0b0d, roughness: 0.9 }));
          bore.rotation.x = -Math.PI / 2; bore.position.y = H - 0.25; g.add(bore);
        }
        return shade(g);
      }
    });

    /* A COLUMN OF SECTIONS: n cans bolted flange to flange, each starting where the one below it ended so the column
     * tapers continuously, the foot carrying the base door and the top its open flange. Only the bottom two carry dust. */
    K.define("section_stack", {
      anchor: "base",
      size: [FL * 2, 45, FL * 2],
      options: { n: 15, rim: "galv", door: false },
      note: "n tower_sections bolted into a tapering column. n, rim galv|plan, door.",
      make: function (o) {
        var g = new THREE.Group(), n = Math.max(1, Math.round(o.n || 1));
        for (var i = 0; i < n; i++) {
          var s = K.make("tower_section", { r0: RAD - TAPER * H * i, rim: o.rim, dusty: i < 2, top: i === n - 1, door: o.door && i === 0 });
          s.position.y = i * H; g.add(s);
        }
        /* the door's steps stand on the ground in front of it */
        if (o.door) for (var k = 0; k < 2; k++) { var st = TXT.roundedBox(1.0, 0.04, 0.3, 0.01, K.mat("cp_galv_step", { color: 0x8d9296, metalness: 0.6, roughness: 0.5 })); st.position.set(0, 0.06 + k * 0.08, RAD + 0.35 - k * 0.2); st.castShadow = st.receiveShadow = true; g.add(st); }
        /* the concrete foundation pedestal the bottom can bolts to, a wind tower's own base rather than a silo's slab */
        var ped = new THREE.Mesh(new THREE.CylinderGeometry(RAD + 0.55, RAD + 0.75, 0.5, 64), K.mat("cp_pedestal", { color: 0x9a948a, roughness: 0.92 }));
        ped.position.y = -0.25; ped.castShadow = ped.receiveShadow = true; g.add(ped);
        for (var c = 0; c < g.children.length; c++) if (g.children[c] !== ped) g.children[c].position.y += 0.5;
        g.userData.height = n * H + 0.5;
        return g;
      }
    });

    /* A SURVEY LATH, pine, its top painted and a strip of flagging hung, both in the accent, 1.2 m tall. Drawn to illustrate. */
    K.define("survey_stake", {
      anchor: "base",
      size: [0.3, 1.2, 0.05],
      options: { lean: 0, flag: true },
      note: "A pine survey lath, 1.2 m, with flagging in the accent. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group();
        var lath = TXT.roundedBox(0.045, 1.2, 0.012, 0.003, M.pine); lath.position.y = 0.6; g.add(lath);
        var top = TXT.roundedBox(0.047, 0.26, 0.014, 0.003, M.rimPlan); top.position.y = 1.07; g.add(top);
        if (o.flag) {
          var fg = new THREE.PlaneGeometry(0.05, 0.6, 1, 12), pos = fg.attributes.position;
          for (var i = 0; i < pos.count; i++) { var yy = pos.getY(i); pos.setX(i, pos.getX(i) + Math.sin((yy + 0.3) * 7) * 0.03); pos.setZ(i, (0.3 - yy) * 0.3); }
          fg.computeVertexNormals();
          var f = new THREE.Mesh(fg, M.flag); f.position.set(0.04, 0.84, 0.02); f.rotation.y = 0.7; g.add(f);
        }
        g.rotation.z = o.lean || 0;
        return shade(g);
      }
    });

    /* A CHAIN AND PADLOCK at a gate seam: a short run of oval links hanging in a U, a brass bodied lock with a steel
     * shackle and an accent tag. Drawn to illustrate. */
    K.define("gate_lock", {
      anchor: "base",
      size: [0.3, 0.5, 0.1],
      options: { links: 9 },
      note: "A hanging chain with a padlock and an accent tag. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), n = o.links || 9, lg = new THREE.TorusGeometry(0.022, 0.006, 6, 14);
        for (var i = 0; i < n; i++) {
          var t = i / (n - 1), x = (t - 0.5) * 0.16, y = 0.42 - Math.sin(t * Math.PI) * 0.16;
          var l = new THREE.Mesh(lg, M.chain); l.scale.set(1, 1.6, 1); l.position.set(x, y, 0); l.rotation.y = i % 2 ? Math.PI / 2 : 0;
          l.rotation.z = (t - 0.5) * 1.6; g.add(l);
        }
        var body = TXT.roundedBox(0.06, 0.05, 0.026, 0.006, M.brass); body.position.set(0, 0.2, 0.01); g.add(body);
        var sh = new THREE.Mesh(new THREE.TorusGeometry(0.019, 0.0045, 6, 16, Math.PI), M.chain); sh.position.set(0, 0.226, 0.01); g.add(sh);
        var tag = TXT.roundedBox(0.03, 0.045, 0.002, 0.002, M.rimPlan); tag.position.set(0.01, 0.155, 0.02); tag.rotation.z = 0.2; g.add(tag);
        return shade(g);
      }
    });

    /* A TRANSFORMER'S RADIATOR BANK, close enough to crop: weathered galvanized fins hung on two headers, the tank wall
     * behind them with its stiffeners and lid flange, cooling fans beneath, on a concrete pad with its curb. The fins run
     * along z and the tank wall is on -x. Drawn at a plausible size for an autotransformer, no rating printed. */
    K.define("radiator_bank", {
      size: [3.4, 4.9, 4.8],
      options: { fins: 22, pitch: 0.11 },
      note: "A transformer radiator bank on its tank wall and pad. fins, pitch (m). Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), nF = o.fins || 22, pitch = o.pitch || 0.11, finW = 0.78, finH = 3.1, y0 = 1.25;
        var skin = M.galv.clone(); skin.color.set(0x9aa0a3); skin.metalness = 0.82; skin.roughness = 0.46; skin.map = dustMap(THREE);
        var conc = K.mat("cp_pad_conc", { color: 0x9c968c, roughness: 0.9 });
        var finG = new THREE.BoxGeometry(finW, finH, 0.014), list = [];
        for (var i = 0; i < nF; i++) list.push([0, y0 + finH / 2, (i - (nF - 1) / 2) * pitch, 0, 1]);
        K.instances(finG, skin, list, g);
        [y0 + 0.08, y0 + finH - 0.08].forEach(function (yy) { var h = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, nF * pitch + 0.2, 16), skin); h.rotation.x = Math.PI / 2; h.position.set(-finW / 2 - 0.12, yy, 0); g.add(h); });
        var tank = TXT.roundedBox(0.3, 4.4, 3.6, 0.04, skin); tank.position.set(-finW / 2 - 0.4, 0.45 + 2.2, 0); g.add(tank);
        for (var k = -3; k <= 3; k++) { var rib = new THREE.Mesh(new THREE.BoxGeometry(0.12, 4.2, 0.1), skin); rib.position.set(-finW / 2 - 0.2, 0.45 + 2.15, k * 0.55); g.add(rib); }
        var lid = TXT.roundedBox(0.5, 0.14, 3.8, 0.03, skin); lid.position.set(-finW / 2 - 0.4, 0.45 + 4.4, 0); g.add(lid);
        for (var f = 0; f < 2; f++) { var fan = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.3, 24, 1, true), M.bolt); fan.position.set(0, y0 - 0.35, (f - 0.5) * 1.2); g.add(fan); }
        var pad = TXT.roundedBox(3.4, 0.35, 4.8, 0.05, conc); pad.position.set(-0.6, 0.175, 0); g.add(pad);
        /* three porcelain bushings on the tank lid, so the bank reads as a transformer's */
        var porc = K.mat("cp_porcelain", { color: 0x6b4a36, roughness: 0.25, clearcoat: 0.8 });
        for (var b2 = -1; b2 <= 1; b2++) {
          var bush = new THREE.Group();
          for (var sk = 0; sk < 5; sk++) { var d = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.04, 18), porc); d.position.y = 0.08 + sk * 0.11; bush.add(d); }
          var core = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 0.66, 12), porc); core.position.y = 0.33; bush.add(core);
          bush.position.set(-finW / 2 - 0.15, 0.45 + 4.5, b2 * 0.9); g.add(bush);
        }
        return shade(g);
      }
    });

    /* A ROW OF LIT INTAKE BAYS for a data hall's long wall: n louvred bays across a given length, each a warm glowing
     * panel behind raked slats, and `lit` decides the glow, the bay at index i lit to min(1, max(0, lit - i)), so a
     * fractional count lights its last bay to its fraction. Faces +z. Drawn to illustrate. */
    K.define("intake_bays", {
      anchor: "base",
      size: [150, 7.6, 0.5],
      options: { n: 10, lit: 10, length: 150, height: 6.2, glow: 0.9 },
      note: "n louvred intake bays across length m, lit by count, a fractional last bay filled from the bottom like a gauge, warm spill in front. Faces +z. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), n = Math.max(1, Math.round(o.n)), L = o.length || 150, hB = o.height || 6.2, bw = L / n, wB = bw * 0.62;
        var slat = K.mat("cp_bay_slat", { color: 0x2a2c2e, roughness: 0.6, metalness: 0.4 }), slatG = new THREE.BoxGeometry(wB, 0.12, 0.28), centres = [];
        for (var i = 0; i < n; i++) {
          var k = Math.max(0, Math.min(1, o.lit - i)), cx = -L / 2 + (i + 0.5) * bw;
          var glow = new THREE.MeshStandardMaterial({ color: 0x1a1410, emissive: 0xff9448, emissiveIntensity: (o.glow || 0.9) * k, toneMapped: false });
          /* a part-lit bay fills from the bottom to its fraction like a gauge, the rest of it dark glass, so the
           * fraction reads at feed size where a uniform dimming would not */
          var hL = hB * (k > 0 && k < 1 ? k : 1), on = k > 0 ? 1 : 0;
          var p = new THREE.Mesh(new THREE.PlaneGeometry(wB, hL), on ? new THREE.MeshStandardMaterial({ color: 0x1a1410, emissive: 0xff9448, emissiveIntensity: (o.glow || 0.9), toneMapped: false }) : glow);
          p.position.set(cx, 1.4 + hL / 2, 0); g.add(p);
          if (hL < hB) { var dk = new THREE.Mesh(new THREE.PlaneGeometry(wB, hB - hL), glow); dk.material.emissiveIntensity = 0; dk.position.set(cx, 1.4 + hL + (hB - hL) / 2, 0); g.add(dk); }
          if (on) { var spill = new THREE.PointLight(0xff9a50, 6 * Math.max(k, 0.5), 14, 2); spill.position.set(cx, 1.6, 2.2); g.add(spill); }
          var list = [];
          for (var j = 0; j < 9; j++) list.push([cx, 1.4 + 0.35 + j * (hB - 0.7) / 8, 0.16, 0, 1]);
          var sl = K.instances(slatG, slat, list, g);
          centres.push([cx, 1.4 + hB / 2, 0]);
        }
        g.userData.bays = centres;
        g.userData.keepOrigin = true;
        return g;
      }
    });
  };

  N.glowTex = function (THREE) {
    if (N._glow) return N._glow;
    var c = document.createElement("canvas"); c.width = c.height = 64; var g = c.getContext("2d");
    var gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.18, "rgba(255,255,255,0.6)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); N._glow = new THREE.CanvasTexture(c); return N._glow;
  };
  N.noShadows = function (R) { R.scene.traverse(function (o) { if (o.userData && o.userData.noShadow) { o.castShadow = false; o.receiveShadow = false; } }); };
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
