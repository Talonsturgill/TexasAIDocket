/* deck/2026-11-19-sortglass-bespoke.js, the SPINE for the November 19th, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * UT Arlington coordinates a $3.1 million USDA funded project to build an AI smart trap meant to tell wild New World
 * screwworm flies from sterile ones and females from males, keeping wild females and releasing the rest. The trap is not
 * built; a prototype is expected next spring (tx-2026-0252).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the WONDER tone, bespoke:true, the tone's grade and the accent. Each
 * frame picks its own world (TXT.sky(R, world)), turns its own key (TXT.deckRig(..., { light })) and places its own type,
 * seated with CH.seat. It mounts the type faces and the furniture (CH.start), and hands a frame the helpers below. There is
 * no drawFrame.
 *
 * THE ACCENT. Dusk gold #E0956A (brand.yaml) means ONE thing: THE FLY THE SORT KEEPS, the wild female and the report she
 * becomes. The keep branch of the glass, the wild female's shut lid, the keep chamber's band, the report pill on a phone.
 * Never today's traps, never the released flies, never decoration.
 *
 * THE MODELS. The kit holds the land, trees, fences, bales, tanks, lab ware and people. The chassis builds what the kit
 * lacks, in the kit's conventions (metres, y up, origin on the ground or the body's feet, front on +z) so Phase 17 can
 * queue the lift: blowfly (a generic bronze fly drawn to illustrate, no species detail claimed, no size claimed),
 * sort_glass (a borosilicate Y passage, the DECISION drawn as a shape, never a device: no camera, flap or circuit),
 * cell_block (a machined block of four glass topped cells), stone_plinth, beetle (a generic small insect), dead_end_jar
 * (a funnel into one jar with no second exit), bucket_trap (a generic one way bucket trap, to no agency design) and
 * smartphone. Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("sortglass.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "sortglass", look: "v2", tone: "wonder", bespoke: true,
    light: { az: -45, el: 35 },
    sky: { preset: "v2wonder" },
    ground: "#e4d8c3",
    material: "#e4d8c3",
    accent: "#e0956a",
    grade: TXLOOK.grade("wonder")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261119; N.TONE = "wonder"; N.P = TXLOOK.palette("wonder"); N.INK = N.P.ink;
  N.ACCENT = 0xe0956a;        /* dusk gold: the fly the sort keeps, and nothing else */
  N.GOLD = N.ACCENT;
  /* a seeded canvas texture, so every surface carries tooth in its albedo and never in its height */
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };



  /* THE FLY'S SKIN: a dark bronze field with a green sheen, faint cross banding. Generic, drawn to illustrate. */
  N.bodyTex = function (THREE) {
    return N._bodyTex || (N._bodyTex = N.canvasTex(THREE, 512, 256, function (x, w, h) {
      var g = x.createLinearGradient(0, 0, 0, h); g.addColorStop(0, "#3a3220"); g.addColorStop(0.5, "#5a4a2a"); g.addColorStop(1, "#2e2818");
      x.fillStyle = g; x.fillRect(0, 0, w, h);
      for (var k = 0; k < 6; k++) { x.fillStyle = "rgba(30,70,58," + (0.18 + 0.05 * k) + ")"; x.fillRect(0, (k / 6) * h, w, h / 14); }
      var r = N.rng(11); for (var i = 0; i < 1400; i++) { x.fillStyle = "rgba(0,0,0," + (0.12 + r() * 0.22).toFixed(2) + ")"; x.fillRect(r() * w, r() * h, 1.6, 1.6); }
    }));
  };
  N.eyeTex = function (THREE) {
    return N._eyeTex || (N._eyeTex = N.canvasTex(THREE, 256, 256, function (x, w, h) {
      x.fillStyle = "#6a2216"; x.fillRect(0, 0, w, h);
      for (var j = 0; j < 22; j++) for (var i = 0; i < 26; i++) { x.beginPath(); x.arc(i * 10 + (j % 2 ? 5 : 0), j * 12, 4.2, 0, Math.PI * 2); x.fillStyle = (i + j) % 3 ? "#8a3020" : "#7a2a1a"; x.fill(); }
    }));
  };
  N.wingTex = function (THREE) {
    return N._wingTex || (N._wingTex = N.canvasTex(THREE, 512, 256, function (x, w, h) {
      x.clearRect(0, 0, w, h);
      x.fillStyle = "rgba(210,220,225,0.18)"; x.beginPath(); x.ellipse(w * 0.5, h * 0.5, w * 0.49, h * 0.42, 0, 0, Math.PI * 2); x.fill();
      x.strokeStyle = "rgba(40,34,30,0.9)"; x.lineWidth = 3;
      [[0.04, 0.5, 0.97, 0.36], [0.04, 0.5, 0.95, 0.5], [0.04, 0.52, 0.9, 0.68], [0.1, 0.55, 0.7, 0.82], [0.2, 0.42, 0.85, 0.2]].forEach(function (v) {
        x.beginPath(); x.moveTo(v[0] * w, v[1] * h); x.quadraticCurveTo(w * 0.5, (v[1] + v[3]) * 0.5 * h, v[2] * w, v[3] * h); x.stroke(); });
      x.lineWidth = 2; [[0.45, 0.4, 0.5, 0.62], [0.68, 0.38, 0.72, 0.6]].forEach(function (v) { x.beginPath(); x.moveTo(v[0] * w, v[1] * h); x.lineTo(v[2] * w, v[3] * h); x.stroke(); });
      x.strokeStyle = "rgba(40,34,30,0.7)"; x.lineWidth = 2.5; x.beginPath(); x.ellipse(w * 0.5, h * 0.5, w * 0.49, h * 0.42, 0, 0, Math.PI * 2); x.stroke();
    }));
  };
  N.glassMat = function (K, tint) {
    return K.mat("sg-glass" + (tint || ""), { color: tint || 0xf4f8ff, metalness: 0, roughness: 0.04, transmission: 0.95, ior: 1.47, thickness: 0.002,
      transparent: true, opacity: 1, clearcoat: 1, clearcoatRoughness: 0.03, specularIntensity: 1, envMapIntensity: 1.4, side: N.T.DoubleSide }, true);
  };
  N.goldMat = function (K, glow) { return K.mat("sg-gold" + (glow || 0), { color: N.ACCENT, metalness: 0.35, roughness: 0.32, emissive: N.ACCENT, emissiveIntensity: Math.min(0.7, glow || 0.12), clearcoat: 0.6 }, true); };

  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.blowfly) return;
    N.T = THREE;
    var shadowAll = function (g) { g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return g; };
    var rbox = function (w, h, d, r, mat) { return TXT.roundedBox ? TXT.roundedBox(w, h, d, r, mat) : new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); };

    /* A GENERIC FLY, drawn to illustrate, head on +z, feet at y 0, about 10 mm long in model units. No species detail and
     * no size is claimed: a frame never places it beside a scale object it would measure against. */
    K.define("blowfly", {
      size: [0.012, 0.006, 0.011],
      options: { spread: 0.42, seed: 3, flying: 0 },
      note: "A generic bronze fly drawn to illustrate: faceted eyes, a bristled thorax, a banded abdomen, veined iridescent wings, six jointed legs. Feet at y 0, head on +z. flying 0 to 1 lifts the legs and opens the wings.",
      make: function (o, r) {
        o = o || {}; var g = new THREE.Group(), S = 0.001, fl = o.flying || 0;
        var body = K.mat("bf-body", { color: 0xffffff, map: N.bodyTex(THREE), metalness: 0.7, roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.12, iridescence: 0.55, iridescenceIOR: 1.4 }, true);
        var dark = K.mat("bf-dark", { color: 0x15120c, metalness: 0.35, roughness: 0.45 });
        var eye = K.mat("bf-eye", { color: 0xffffff, map: N.eyeTex(THREE), roughness: 0.16, clearcoat: 1, clearcoatRoughness: 0.04 }, true);
        var face = K.mat("bf-face", { color: 0x9c8460, roughness: 0.55 });
        var wing = new THREE.MeshPhysicalMaterial({ map: N.wingTex(THREE), transparent: true, side: THREE.DoubleSide, roughness: 0.15, metalness: 0, opacity: 1, depthWrite: false, iridescence: 0.6, iridescenceIOR: 1.3, clearcoat: 0.6 });
        var y0 = 2.6 * S;
        function ell(rx, ry, rz, mat, x, y, z) { var m = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 28), mat); m.scale.set(rx, ry, rz); m.position.set(x, y, z); g.add(m); return m; }
        ell(1.55 * S, 1.45 * S, 1.9 * S, body, 0, y0 + 0.2 * S, 0.4 * S);
        ell(1.6 * S, 1.3 * S, 2.3 * S, body, 0, y0 - 0.1 * S, -2.9 * S).rotation.x = -0.12;
        ell(1.5 * S, 1.25 * S, 0.9 * S, face, 0, y0 + 0.1 * S, 2.65 * S);
        [-1, 1].forEach(function (sx) { var e = ell(0.95 * S, 1.15 * S, 0.8 * S, eye, sx * 0.85 * S, y0 + 0.35 * S, 2.95 * S); e.rotation.y = sx * 0.35; });
        [-1, 1].forEach(function (sx) {
          var wg = new THREE.Mesh(new THREE.PlaneGeometry(6.4 * S, 2.6 * S), wing);
          var piv = new THREE.Group(); piv.position.set(sx * 0.9 * S, y0 + 1.25 * S, 1.0 * S);
          wg.position.set(sx * 3.0 * S, 0, 0); wg.rotation.x = -Math.PI / 2; piv.add(wg);
          piv.rotation.y = sx * (Math.PI / 2 + (o.spread || 0.42) + fl * 0.9); piv.rotation.z = sx * (0.12 + fl * 0.7); g.add(piv);
        });
        [[1.6, 2.2], [0.3, 2.8], [-1.0, 2.6]].forEach(function (p, i) {
          [-1, 1].forEach(function (sx) {
            var hip = [sx * 1.0 * S, y0 - 0.6 * S, p[0] * S];
            var knee = [sx * p[1] * S, y0 + (0.9 - fl * 0.9) * S, (p[0] + (i === 0 ? 1.2 : i === 2 ? -1.4 : 0)) * S];
            var foot = [sx * (p[1] + 0.8 - fl * 1.2) * S, (0.05 + fl * 1.6) * S, (p[0] + (i === 0 ? 2.2 : i === 2 ? -2.6 : 0.2)) * S];
            K.bar(hip, knee, 0.16 * S, dark, 6, g); K.bar(knee, foot, 0.12 * S, dark, 6, g);
          });
        });
        var br = new THREE.CylinderGeometry(0.03 * S, 0.06 * S, 0.7 * S, 4), list = [];
        for (var i = 0; i < 160; i++) { var th = r() * Math.PI * 2, ph = r() * Math.PI * 0.5, onAb = i % 2, rx = onAb ? 1.6 : 1.55, rz = onAb ? 2.3 : 1.9, cz = onAb ? -2.9 : 0.4;
          list.push([Math.cos(th) * Math.sin(ph) * rx * S, y0 + Math.cos(ph) * 1.4 * S, cz * S + Math.sin(th) * Math.sin(ph) * rz * S, r() * 3, 1]); }
        K.instances(br, dark, list, g);
        return shadowAll(g);
      }
    });

    /* A GENERIC SMALL BEETLE for "other insects", matte rust, about 8 mm, feet at y 0. */
    K.define("beetle", {
      size: [0.006, 0.004, 0.009],
      options: { seed: 2 },
      note: "A generic small beetle drawn to illustrate, matte rust elytra, six legs, feet at y 0, head on +z.",
      make: function (o, r) {
        var g = new THREE.Group(), S = 0.001;
        var shell = K.mat("bt-shell", { color: 0x8c5a3c, roughness: 0.42, clearcoat: 0.7, clearcoatRoughness: 0.2 }, true), dark = K.mat("bt-dark", { color: 0x1d1610, roughness: 0.5 });
        var m = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), shell); m.scale.set(2.6 * S, 1.6 * S, 3.6 * S); m.position.set(0, 2.0 * S, -0.4 * S); g.add(m);
        var hd = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), dark); hd.scale.set(1.3 * S, 1.0 * S, 1.1 * S); hd.position.set(0, 1.8 * S, 3.2 * S); g.add(hd);
        K.bar([0, 3.5 * S, -3.6 * S], [0, 3.62 * S, 2.6 * S], 0.08 * S, dark, 4, g);
        [-1.6, 0, 1.6].forEach(function (z) { [-1, 1].forEach(function (sx) { K.bar([sx * 1.8 * S, 1.4 * S, z * S], [sx * 3.4 * S, 1.6 * S, (z + 0.4) * S], 0.14 * S, dark, 5, g); K.bar([sx * 3.4 * S, 1.6 * S, (z + 0.4) * S], [sx * 4.0 * S, 0.05 * S, (z + 0.9) * S], 0.11 * S, dark, 5, g); }); });
        return shadowAll(g);
      }
    });

    /* THE SORT, drawn as a shape and never as a device: a borosilicate Y. The mouth at the top flares 0.06 m wide, the bore
     * is 0.02 m, it forks at 35 degrees into a KEEP branch ending in a capped chamber with a dusk gold band and a RELEASE
     * branch ending open. Origin at the foot of the stem, y up, the keep branch to -x, the release branch to +x. No camera,
     * flap, light or circuit. Options: height (m, default 0.30), band (true carries the gold band), keepOpen (false). */
    K.define("sort_glass", {
      size: [0.24, 0.30, 0.07],
      options: { height: 0.30, band: true },
      note: "An illustrative glass Y passage, the decision drawn as a shape: one flared mouth, a fork at 35 degrees, a capped KEEP chamber with a dusk gold band on -x, an open RELEASE branch on +x. Origin at the stem foot. Drawn to illustrate the decision, never the device.",
      make: function (o) {
        o = o || {}; var g = new THREE.Group(), s = (o.height || 0.30) / 0.30, glass = N.glassMat(K);
        var bore = 0.010 * s, wall = 0.0018 * s;
        var tube = function (a, b, rad) { var v = new THREE.Vector3(b[0] - a[0], b[1] - a[1], b[2] - a[2]), L = v.length();
          var m = new THREE.Mesh(new THREE.CylinderGeometry(rad, rad, L, 48, 1, true), glass); m.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2);
          m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v.normalize()); g.add(m); return m; };
        /* stem foot and mouth: the mouth is at the TOP, the fork below it, the branches below that, so flies enter from above */
        var fork = [0, 0.17 * s, 0], mouthY = 0.26 * s;
        var prof = []; for (var i = 0; i <= 24; i++) { var t = i / 24; prof.push(new THREE.Vector2(bore + wall + (0.03 * s - bore) * Math.pow(t, 2.2), mouthY + t * 0.04 * s)); }
        var mouth = new THREE.Mesh(new THREE.LatheGeometry(prof, 64), glass); g.add(mouth);
        var lip = new THREE.Mesh(new THREE.TorusGeometry(0.03 * s + wall, wall * 1.4, 12, 64), glass); lip.rotation.x = Math.PI / 2; lip.position.y = mouthY + 0.04 * s; g.add(lip);
        tube([0, mouthY, 0], fork, bore + wall);
        var a = 35 * Math.PI / 180, L = 0.14 * s;
        var keepEnd = [-Math.sin(a) * L, fork[1] - Math.cos(a) * L, 0], relEnd = [Math.sin(a) * L, fork[1] - Math.cos(a) * L, 0];
        tube(fork, keepEnd, bore + wall); tube(fork, relEnd, bore + wall);
        var knot = new THREE.Mesh(new THREE.SphereGeometry(bore + wall * 1.6, 32, 20), glass); knot.position.set(fork[0], fork[1], fork[2]); g.add(knot);
        /* the keep chamber, a capped bulb at the keep end */
        var ch = new THREE.Mesh(new THREE.SphereGeometry(0.026 * s, 48, 32), glass); ch.scale.set(1, 1.25, 1); ch.position.set(keepEnd[0], keepEnd[1] - 0.02 * s, 0); g.add(ch);
        var cap = new THREE.Mesh(new THREE.CylinderGeometry(0.012 * s, 0.014 * s, 0.012 * s, 32), K.mat("sg-cap", { color: 0xc9ccd2, metalness: 0.9, roughness: 0.28 })); cap.position.set(keepEnd[0], keepEnd[1] - 0.054 * s, 0); g.add(cap);
        if (o.band !== false) { var band = new THREE.Mesh(new THREE.TorusGeometry(0.0262 * s, 0.0026 * s, 14, 64), N.goldMat(K, 0.18)); band.position.set(keepEnd[0], keepEnd[1] - 0.02 * s, 0); band.rotation.x = Math.PI / 2; g.add(band); }
        /* the release end flares open */
        var rp = []; for (var j = 0; j <= 16; j++) { var u = j / 16; rp.push(new THREE.Vector2(bore + wall + 0.008 * s * u * u, -u * 0.02 * s)); }
        var flare = new THREE.Mesh(new THREE.LatheGeometry(rp, 48), glass); flare.position.set(relEnd[0], relEnd[1], 0);
        flare.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), new THREE.Vector3(Math.sin(a), -Math.cos(a), 0)); g.add(flare);
        /* a stand: a short steel rod and foot ring under the fork so it stands on a plinth */
        var steel = K.mat("sg-steel", { color: 0xb9bec6, metalness: 0.95, roughness: 0.25 });
        K.bar([0, 0, 0], [0, fork[1] - 0.004 * s, 0], 0.0025 * s, steel, 12, g);
        var foot = new THREE.Mesh(new THREE.CylinderGeometry(0.035 * s, 0.038 * s, 0.006 * s, 48), steel); foot.position.y = 0.003 * s; g.add(foot);
        g.userData.keep = [keepEnd[0], keepEnd[1] - 0.02 * s, 0]; g.userData.release = relEnd; g.userData.fork = fork; g.userData.mouth = [0, mouthY + 0.04 * s, 0];
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = m.material !== glass; m.receiveShadow = true; } });
        return g;
      }
    });

    /* A MACHINED BLOCK of four glass topped cells, 0.16 x 0.04 x 0.16 m, bead blasted top, brushed sides, rounded edges.
     * Options: cells (default 4, laid 2 x 2), shut (index of the one shut lid, its rim in dusk gold), open (lid angle). */
    K.define("cell_block", {
      size: [0.16, 0.04, 0.16],
      options: { cells: 4, shut: 0, open: 1.9 },
      note: "An illustrative aluminium block, 0.16 x 0.04 x 0.16 m, with four 0.05 m glass topped cells laid 2 x 2, hinged lids, one shut with a dusk gold rim. Origin at the base centre. userData.cells holds each cell's floor centre.",
      make: function (o) {
        o = o || {}; var g = new THREE.Group(), n = o.cells || 4, side = Math.round(Math.sqrt(n));
        if (side * side !== n) throw new Error("cell_block wants a square count, got " + n);
        var al = K.mat("cb-al", { color: 0xc8ccd2, metalness: 0.92, roughness: 0.42 }), alTop = K.mat("cb-altop", { color: 0xd8dce2, metalness: 0.85, roughness: 0.6 });
        var blk = rbox(0.16, 0.04, 0.16, 0.003, al); blk.position.y = 0.02; g.add(blk);
        var pitch = 0.16 / side, cells = [], glass = N.glassMat(K);
        for (var i = 0; i < n; i++) {
          var cx0 = -0.08 + pitch * (i % side + 0.5), cz0 = -0.08 + pitch * (Math.floor(i / side) + 0.5);
          var well = new THREE.Mesh(new THREE.CylinderGeometry(0.024, 0.024, 0.026, 48), K.mat("cb-well", { color: 0x2e2a36, roughness: 0.7 })); well.position.set(cx0, 0.028, cz0); g.add(well);
          var rimM = i === (o.shut || 0) ? N.goldMat(K, 0.15) : alTop;
          var rim = new THREE.Mesh(new THREE.TorusGeometry(0.0255, 0.0018, 10, 48), rimM); rim.rotation.x = Math.PI / 2; rim.position.set(cx0, 0.0405, cz0); g.add(rim);
          var hinge = new THREE.Group(); hinge.position.set(cx0, 0.041, cz0 - 0.026); g.add(hinge);
          var lid = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.002, 48), glass); lid.position.set(0, 0.001, 0.026); hinge.add(lid);
          var lidRim = new THREE.Mesh(new THREE.TorusGeometry(0.025, 0.0012, 8, 48), rimM); lidRim.rotation.x = Math.PI / 2; lidRim.position.set(0, 0.002, 0.026); hinge.add(lidRim);
          if (i !== (o.shut || 0)) hinge.rotation.x = -(o.open || 1.9);
          cells.push([cx0, 0.0155, cz0]);
        }
        g.userData.cells = cells;
        return shadowAll(g);
      }
    });

    /* A TURNED STONE PLINTH in honed caliche, worn and dusted at the edges. Options: r (radius, 0.1), h (height, 0.12). */
    K.define("stone_plinth", {
      size: [0.2, 0.12, 0.2],
      options: { r: 0.1, h: 0.12 },
      note: "A honed caliche stone plinth, origin at the base centre, with a chamfered top edge and a worn, dusted albedo.",
      make: function (o) {
        o = o || {}; var r0 = o.r || 0.1, h = o.h || 0.12, g = new THREE.Group();
        var tex = N.canvasTex(THREE, 512, 256, function (x, w, hh) { x.fillStyle = "#e4d8c3"; x.fillRect(0, 0, w, hh); var r = N.rng(7);
          for (var i = 0; i < 2600; i++) { x.fillStyle = "rgba(" + (r() < 0.5 ? "120,100,70," : "255,250,240,") + (0.05 + r() * 0.12).toFixed(3) + ")"; x.fillRect(r() * w, r() * hh, 1 + r() * 3, 1 + r() * 2); }
          var gr = x.createLinearGradient(0, 0, 0, hh); gr.addColorStop(0, "rgba(255,255,255,0)"); gr.addColorStop(1, "rgba(110,90,60,0.25)"); x.fillStyle = gr; x.fillRect(0, 0, w, hh); });
        var stone = K.mat("sp-stone", { color: 0xffffff, map: tex, roughness: 0.62, metalness: 0 }, true);
        var prof = [new THREE.Vector2(0, 0), new THREE.Vector2(r0 * 1.06, 0), new THREE.Vector2(r0 * 1.06, h * 0.08), new THREE.Vector2(r0, h * 0.12), new THREE.Vector2(r0, h * 0.94), new THREE.Vector2(r0 * 0.96, h), new THREE.Vector2(0, h)];
        g.add(new THREE.Mesh(new THREE.LatheGeometry(prof, 72), stone));
        return shadowAll(g);
      }
    });

    /* TODAY'S SINGLE EXIT: a glass funnel into one jar with no second opening, 0.12 m tall. Origin at the base centre. */
    K.define("dead_end_jar", {
      size: [0.09, 0.12, 0.09],
      options: { flies: 6 },
      note: "An illustrative glass funnel into one jar, one way in and no way out, 0.12 m tall, with a few dark specks of catch on the floor. Origin at the base centre.",
      make: function (o, r) {
        o = o || {}; var g = new THREE.Group(), glass = N.glassMat(K);
        g.add(new THREE.Mesh(new THREE.CylinderGeometry(0.042, 0.042, 0.09, 48, 1, true), glass)).position.y = 0.045;
        var base = new THREE.Mesh(new THREE.CylinderGeometry(0.043, 0.043, 0.004, 48), glass); base.position.y = 0.002; g.add(base);
        var fp = []; for (var i = 0; i <= 16; i++) { var t = i / 16; fp.push(new THREE.Vector2(0.006 + 0.036 * t, 0.06 + t * 0.03)); }
        var fun = new THREE.Mesh(new THREE.LatheGeometry(fp, 48), glass); g.add(fun);
        var lip = new THREE.Mesh(new THREE.TorusGeometry(0.043, 0.002, 8, 48), glass); lip.rotation.x = Math.PI / 2; lip.position.y = 0.09; g.add(lip);
        var speck = K.mat("dj-speck", { color: 0x1b160f, roughness: 0.6 });
        for (var k = 0; k < (o.flies || 6); k++) { var s = new THREE.Mesh(new THREE.SphereGeometry(0.0022, 8, 6), speck); var a = r() * 6.28, d = r() * 0.03; s.position.set(Math.cos(a) * d, 0.0055, Math.sin(a) * d); s.scale.set(1, 0.6, 1.7); g.add(s); }
        return shadowAll(g);
      }
    });

    /* A GENERIC ONE WAY BUCKET TRAP, drawn to no agency's design: a 0.25 m white polymer drum, a single funnel mouth in the
     * lid, a galvanized wire bail. Origin at the top of the bail, so a frame hangs it from a limb. Options: weather (0 to 1). */
    K.define("bucket_trap", {
      size: [0.24, 0.42, 0.24],
      options: { weather: 0.5 },
      note: "An illustrative one way bucket trap: a 0.25 m white polymer drum, one funnel mouth, a wire bail. Origin at the bail's top. Drawn to no agency design.",
      make: function (o) {
        o = o || {}; var g = new THREE.Group(), w = o.weather == null ? 0.5 : o.weather;
        var tex = N.canvasTex(THREE, 512, 256, function (x, ww, hh) { x.fillStyle = "#eeeae2"; x.fillRect(0, 0, ww, hh); var r = N.rng(13);
          for (var i = 0; i < 900 * w; i++) { x.fillStyle = "rgba(110,95,70," + (0.04 + r() * 0.1).toFixed(3) + ")"; x.fillRect(r() * ww, hh * (0.4 + 0.6 * r()), 1 + r() * 4, 1 + r() * 10); }
          var gr = x.createLinearGradient(0, 0, 0, hh); gr.addColorStop(0, "rgba(0,0,0,0)"); gr.addColorStop(1, "rgba(120,100,70," + (0.3 * w).toFixed(2) + ")"); x.fillStyle = gr; x.fillRect(0, 0, ww, hh); });
        var poly = K.mat("bk-poly", { color: 0xffffff, map: tex, roughness: 0.55, metalness: 0, clearcoat: 0.2 }, true), galv = K.finish && K.finish.galvanized ? K.finish.galvanized() : K.mat("bk-galv", { color: 0xb8bcc0, metalness: 0.9, roughness: 0.4 });
        var drum = new THREE.Mesh(new THREE.CylinderGeometry(0.115, 0.1, 0.26, 56), poly); drum.position.y = -0.42 + 0.13; g.add(drum);
        var lid = new THREE.Mesh(new THREE.CylinderGeometry(0.122, 0.122, 0.018, 56), poly); lid.position.y = -0.42 + 0.27; g.add(lid);
        var fp = []; for (var i = 0; i <= 14; i++) { var t = i / 14; fp.push(new THREE.Vector2(0.018 + 0.06 * t, -0.06 + t * 0.06)); }
        var fun = new THREE.Mesh(new THREE.LatheGeometry(fp, 48), K.mat("bk-fun", { color: 0x2a2f38, roughness: 0.5, side: THREE.DoubleSide })); fun.position.y = -0.42 + 0.28; g.add(fun);
        var curve = new THREE.CatmullRomCurve3([new THREE.Vector3(-0.122, -0.42 + 0.2, 0), new THREE.Vector3(-0.09, -0.06, 0), new THREE.Vector3(0, 0, 0), new THREE.Vector3(0.09, -0.06, 0), new THREE.Vector3(0.122, -0.42 + 0.2, 0)]);
        g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 48, 0.0025, 8, false), galv));
        return shadowAll(g);
      }
    });

    /* A SMARTPHONE, 0.072 x 0.150 x 0.008 m, glass front, aluminium frame, screen on +z. Origin at its centre. The screen
     * is a canvas the frame paints (o.screen, a function (ctx, w, h)); left dark when absent. */
    K.define("smartphone", {
      size: [0.072, 0.15, 0.008],
      options: {},
      note: "An illustrative smartphone, 0.072 x 0.150 x 0.008 m, aluminium frame, glass front, screen on +z painted by o.screen(ctx, w, h). Origin at its centre. No real app or brand.",
      make: function (o) {
        o = o || {}; var g = new THREE.Group();
        var al = K.mat("ph-al", { color: 0x9aa0a8, metalness: 0.95, roughness: 0.3 });
        g.add(rbox(0.072, 0.15, 0.008, 0.006, al));
        var c = document.createElement("canvas"); c.width = 540; c.height = 1140; var x = c.getContext("2d"); x.fillStyle = "#0b0d14"; x.fillRect(0, 0, 540, 1140);
        if (o.screen) o.screen(x, 540, 1140);
        var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
        var scr = new THREE.Mesh(new THREE.PlaneGeometry(0.066, 0.1395), new THREE.MeshPhysicalMaterial({ map: t, emissive: 0xffffff, emissiveMap: t, emissiveIntensity: 0.55, roughness: 0.05, clearcoat: 1, clearcoatRoughness: 0.02 }));
        scr.position.z = 0.0041; g.add(scr);
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
