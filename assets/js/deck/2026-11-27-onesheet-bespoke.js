/* deck/2026-11-27-onesheet-bespoke.js, the SPINE for the November 27th, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * the Texas Comptroller's proposed amendments to Rule 3.308, which would treat cloud computing, artificial intelligence and
 * quantum computing as hosted technology services outside the sales tax on data processing, and the comptroller's own
 * fiscal note estimate of what the state and local governments would stop collecting (tx-2026-0255).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the deck's TONE (watch), bespoke:true, the tone's grade and the accent.
 * Each frame picks its own world (TXT.sky(R, world) or TXT.studio / TXT.interior), turns its own key
 * (TXT.deckRig(..., { light })) and places its own type, seated with CH.seat. It mounts the type faces and the furniture
 * (CH.start), and hands a frame the helpers below. There is no drawFrame.
 *
 * THE ACCENT. Dusk gold #e0956a means ONE thing: THE WORDS OF THE PROPOSAL (a highlighted line on a Register page, the
 * highlighted paragraph, the tab on the last day card, the line of a reader's letter quoting the rule). Never on the paper
 * stacks, which carry the estimate's figures. Never on type, never decoration, never red.
 * THE MATERIAL CODE. Kraft wrapped reams with a rose band and cream sheet edges are the ESTIMATE, at one sheet of paper per
 * $1,000,000 (FIG.sheet_usd), 500 sheets to a ream, 0.1 mm a sheet. Cream Register paper with violet grey ink is the RULE.
 *
 * THE MODELS the kit lacks, in the kit's conventions (metres, y up, origin on the ground, front on +z) so Phase 17 can
 * queue the lift: paper_ream (one wrapped ream, or an opened block of n loose sheets), ream_stack (a stack holding exactly
 * n sheets as whole reams plus a loose block, its height n x 0.1 mm), register_page (a letter leaf with greeked two column
 * type, a highlight line and an optional curl and clip) and envelope (a #10 envelope with an open flap and a letter half
 * out). Everything drawn is drawn to illustrate: no legible text, no logo, no likeness.
 * Every count a frame draws is read from window.FIG in that frame's own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("onesheet.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "onesheet", look: "v2", tone: "watch", bespoke: true,
    light: { az: -42, el: 30 },
    sky: { preset: "v2watch" },
    ground: "#ff8a5a",
    material: "#f4ead8",
    accent: "#e0956a",
    grade: TXLOOK.grade("watch")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261127; N.TONE = "watch"; N.P = TXLOOK.palette("watch"); N.INK = N.P.ink;
  N.ACCENT = 0xe0956a;        /* dusk gold: the words of the proposal, and nothing else */
  N.KRAFT = 0xa98458; N.BAND = 0xb8707e; N.PAPER = 0xf4ead8; N.INKC = 0x4a3f6b; N.OAK = 0x9a6a42; N.RACK = 0x2a2350;
  N.STEEL = 0xc9ced4; N.WALNUT = 0x5e3b26;
  N.GOLD = N.ACCENT;
  N.SHEET_M = 0.0001;         /* one sheet of 20 lb bond, 0.1 mm, the stack's drawing rule */
  N.REAM = 500;
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };
  /* the accent as a wax highlighter: albedo first with a little emissive so it reads at feed size under a coral key */
  N.goldMat = function (K) { return K.mat("os-gold", { color: 0xd9803e, metalness: 0.1, roughness: 0.35, emissive: 0xe8913c, emissiveIntensity: 0.25, clearcoat: 0.6, clearcoatRoughness: 0.2 }, true); };
  N.rackMat = function (K) { return K.mat("os-rack", { color: N.RACK, metalness: 0.55, roughness: 0.45, envMapIntensity: 1.2 }, true); };
  /* greeked two column type on cream paper, never legible; hl is the index of the one highlighted line (accent), or -1 */
  N.pageTex = function (THREE, seed, hl, o) {
    o = o || {}; var r = N.rng(seed || 11);
    return N.canvasTex(THREE, 864, 1116, function (g, w, h) {
      g.fillStyle = "#f4ead8"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 9000; i++) { g.fillStyle = "rgba(110,90,70," + (r() * 0.05).toFixed(3) + ")"; g.fillRect(r() * w, r() * h, 1.3, 1.3); }
      g.fillStyle = "rgba(74,63,107,0.85)"; g.fillRect(60, 56, w - 120, 18); g.fillRect(60, 84, w - 120, 3);
      var colW = (w - 150) / 2, line = 0, rows = o.rows || 44;
      for (var c = 0; c < 2; c++) {
        var x0 = 60 + c * (colW + 30);
        for (var L = 0; L < rows; L++) {
          var y = 120 + L * (h - 170) / rows, end = x0 + colW - (L % 7 === 6 ? colW * 0.45 : r() * 30), x = x0 + (L % 7 === 0 ? 22 : 0);
          var isHl = line === hl;
          if (isHl) { g.fillStyle = "rgba(224,149,106,0.9)"; g.fillRect(x0 - 6, y - 7, colW + 12, 22); }
          while (x < end) { var ww = 10 + r() * 46; g.fillStyle = isHl ? "rgba(74,40,30,0.9)" : "rgba(74,63,107,0.62)"; g.fillRect(x, y, Math.min(ww, end - x), 8); x += ww + 8 + r() * 5; }
          line++;
        }
      }
    });
  };
  /* sheet edges seen side on: fine cream striations with a little grey, every so often a darker sheet */
  N.edgeTex = function (THREE, seed) {
    var r = N.rng(seed || 5);
    return N.canvasTex(THREE, 64, 1024, function (g, w, h) {
      for (var y = 0; y < h; y += 2) { var v = 232 + Math.floor(r() * 18) - (r() < 0.04 ? 30 : 0); g.fillStyle = "rgb(" + v + "," + (v - 6) + "," + (v - 18) + ")"; g.fillRect(0, y, w, 2); }
    }, [1, 1]);
  };
  /* kraft wrapper with a rose band and greeked band print, wrapping the four sides of a ream */
  N.kraftTex = function (THREE, seed) {
    var r = N.rng(seed || 3);
    return N.canvasTex(THREE, 512, 256, function (g, w, h) {
      g.fillStyle = "#9c6a3a"; g.fillRect(0, 0, w, h);
      for (var i = 0; i < 5000; i++) { var k = r(); g.fillStyle = k < 0.5 ? "rgba(90,60,30,0.08)" : "rgba(255,230,190,0.07)"; g.fillRect(r() * w, r() * h, 1 + r() * 3, 1); }
                  g.fillStyle = "rgba(70,40,20,0.25)"; for (var s = 0; s < 3; s++) g.fillRect(r() * w, 0, 2, h);
    }, [1, 1]);
  };

  /* THE MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.paper_ream) return;
    N.T = THREE;
    var shadowAll = function (g) { g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } }); return g; };
    var W = 0.216, D = 0.279;
    var paperMat = function () { return K.mat("os-paper", { color: 0xffffff, map: N.pageTex(THREE, 21, -1), roughness: 0.9 }); };
    var edgeMat = function () { return K.mat("os-edge", { color: 0xffffff, map: N.edgeTex(THREE, 5), roughness: 0.92 }); };
    var kraftMat = function () { return K.mat("os-kraft", { color: 0xffffff, map: N.kraftTex(THREE, 3), roughness: 0.78, clearcoat: 0.05 }, true); };
    var kraftTop = function () { return K.mat("os-kraft-top", { color: N.KRAFT, roughness: 0.82 }); };

    /* PAPER REAM. 0.216 x 0.050 x 0.279 m. sheets 500 (default) is a wrapped ream: a kraft wrapper with a rose band on the
     * four sides, folded end seams on the top and bottom faces. sheets under 500 is an opened block of exactly that many
     * sheets, n x 0.1 mm tall, cream edges striated, a top sheet of greeked type. Origin at the base centre. */
    K.define("paper_ream", {
      size: [W, 0.05, D],
      options: { sheets: 500, torn: false },
      note: "One ream of letter paper at true size (500 sheets, 50 mm), kraft wrapped with a rose band, or an opened block of n loose sheets n x 0.1 mm tall. The deck's drawing unit for money: one sheet stands for $1,000,000 of the estimate.",
      make: function (o) {
        o = Object.assign({ sheets: 500, torn: false }, o || {});
        var g = new THREE.Group(), n = Math.max(1, Math.min(500, Math.round(o.sheets))), h = n * N.SHEET_M;
        if (n >= 500) {
          var top = kraftTop();
          var body = TXT.roundedBox(W, h, D, 0.002, top); body.position.y = h / 2; g.add(body);
          var band = new THREE.Mesh(new THREE.BoxGeometry(W + 0.0008, h * 0.18, D + 0.0008), K.mat("os-band", { color: N.BAND, roughness: 0.6 }));
          band.position.y = h / 2; g.add(band);
          /* the folded end seams, a slightly proud flap on top and bottom */
          [h + 0.0004, -0.0001].forEach(function (y) {
            var flap = new THREE.Mesh(new THREE.BoxGeometry(W * 0.98, 0.0008, D * 0.36), top); flap.position.set(0, y, D * 0.31); g.add(flap);
            var flap2 = flap.clone(); flap2.position.z = -D * 0.31; g.add(flap2);
          });
          if (o.torn) {
            var paper = paperMat(), t = new THREE.Mesh(new THREE.BoxGeometry(W * 0.5, 0.0012, D * 0.42), paper); t.position.set(W * 0.18, h + 0.0008, -D * 0.18); g.add(t);
          }
        } else {
          var e = edgeMat(), p = paperMat();
          var blk = new THREE.Mesh(new THREE.BoxGeometry(W, h, D), [e, e, p, p, e, e]); blk.position.y = h / 2; g.add(blk);
        }
        g.userData.height = h;
        return shadowAll(g);
      }
    });

    /* REAM STACK. A stack holding EXACTLY o.sheets sheets: floor(sheets / 500) wrapped reams with a settle jitter, then an
     * opened block of the remainder on top. Height = sheets x 0.1 mm. userData.top is the top surface height,
     * userData.reams and userData.loose the split, so a frame can assert what it drew. */
    K.define("ream_stack", {
      size: [W, 0.2, D],
      options: { sheets: 1000, jitter: 0.002, seed: 1, tornTop: true },
      note: "A stack of paper holding exactly n sheets, whole reams plus a loose block, n x 0.1 mm tall. Read sheets from FIG.",
      make: function (o) {
        o = Object.assign({ sheets: 1000, jitter: 0.002, seed: 1, tornTop: true }, o || {});
        var g = new THREE.Group(), r = N.rng(o.seed * 977 + 13), n = Math.max(1, Math.floor(o.sheets));
        var reams = Math.floor(n / N.REAM), loose = n % N.REAM, y = 0;
        for (var i = 0; i < reams; i++) {
          var rm = K.make("paper_ream", { sheets: 500, torn: o.tornTop && loose === 0 && i === reams - 1 });
          rm.position.set((r() - 0.5) * 2 * o.jitter, y, (r() - 0.5) * 2 * o.jitter); rm.rotation.y = (r() - 0.5) * 0.03; g.add(rm); y += 500 * N.SHEET_M;
        }
        if (loose > 0) { var lb = K.make("paper_ream", { sheets: loose }); lb.position.set((r() - 0.5) * o.jitter, y, (r() - 0.5) * o.jitter); lb.rotation.y = (r() - 0.5) * 0.05; g.add(lb); y += loose * N.SHEET_M; }
        g.userData.top = y; g.userData.reams = reams; g.userData.loose = loose; g.userData.sheets = n; g.userData.keepOrigin = true;
        return shadowAll(g);
      }
    });

    /* REGISTER PAGE. A letter leaf 0.216 x 0.279 m, 0.3 mm thick, greeked two column type with one highlighted line
     * (hl, the accent, -1 for none), an optional curl (0 to 1, the free corner lifting) and a chrome binder clip at the top
     * edge. Lies flat on y = 0, top edge toward -z. */
    K.define("register_page", {
      size: [W, 0.012, D],
      options: { hl: 9, curl: 0.15, clip: false, seed: 11 },
      note: "A Texas Register page drawn to illustrate: greeked two column type, nothing legible, one dusk gold highlighted line.",
      make: function (o) {
        o = Object.assign({ hl: 9, curl: 0.15, clip: false, seed: 11 }, o || {});
        var g = new THREE.Group();
        var geo = new THREE.PlaneGeometry(W, D, 24, 32); geo.rotateX(-Math.PI / 2);
        var p = geo.attributes.position;
        for (var i = 0; i < p.count; i++) {
          var x = p.getX(i), z = p.getZ(i), u = (x + W / 2) / W, v = (z + D / 2) / D;
          var lift = o.curl * 0.03 * Math.pow(Math.max(0, u + v - 1.2) / 0.8, 2);
          p.setY(i, 0.0004 + lift + Math.sin(u * 9 + v * 5) * 0.0002);
        }
        geo.computeVertexNormals();
        var mat = K.mat("os-page-" + o.hl + "-" + o.seed, { color: 0xffffff, map: N.pageTex(THREE, o.seed, o.hl), roughness: 0.88, side: THREE.DoubleSide });
        var leaf = new THREE.Mesh(geo, mat); g.add(leaf);
        if (o.clip) {
          var chrome = K.mat("os-chrome", { color: 0xdfe3e8, metalness: 1, roughness: 0.18 });
          var c1 = TXT.roundedBox(0.032, 0.006, 0.016, 0.002, chrome); c1.position.set(0, 0.004, -D / 2 + 0.006); g.add(c1);
          [-1, 1].forEach(function (s) {
            var arm = new THREE.Mesh(new THREE.TorusGeometry(0.009, 0.0012, 8, 24, Math.PI), chrome);
            arm.position.set(s * 0.01, 0.008, -D / 2 - 0.004); arm.rotation.set(0, Math.PI / 2, 0); g.add(arm);
          });
        }
        g.userData.keepOrigin = true;
        return shadowAll(g);
      }
    });

    /* ENVELOPE. A #10 envelope 0.241 x 0.105 m, flap open (flap degrees), a letter leaf half out carrying one dusk gold line,
     * a blank stamp square and greeked address lines. Lies flat on y = 0, long side along x, flap toward -z. */
    K.define("envelope", {
      size: [0.241, 0.02, 0.105],
      options: { flap: 35, letter: 0.45, seed: 4 },
      note: "A #10 envelope with its flap open and a letter half out, one dusk gold line on the letter quoting the rule. Nothing legible.",
      make: function (o) {
        o = Object.assign({ flap: 35, letter: 0.45, seed: 4 }, o || {});
        var g = new THREE.Group(), EW = 0.241, ED = 0.105;
        var face = N.canvasTex(THREE, 960, 420, function (c, w, h) {
          c.fillStyle = "#f7f1e6"; c.fillRect(0, 0, w, h);
          c.fillStyle = "rgba(74,63,107,0.55)"; for (var L = 0; L < 3; L++) c.fillRect(w * 0.4, h * 0.45 + L * 34, w * (0.36 - L * 0.06), 12);
          c.strokeStyle = "rgba(74,63,107,0.45)"; c.lineWidth = 4; c.strokeRect(w - 150, 30, 110, 120);
        });
        var env = K.mat("os-env", { color: 0xffffff, map: face, roughness: 0.85 });
        var plain = K.mat("os-env-b", { color: 0xf3ecdf, roughness: 0.88 });
        var body = new THREE.Mesh(new THREE.BoxGeometry(EW, 0.0012, ED), [plain, plain, env, plain, plain, plain]); body.position.y = 0.0006; g.add(body);
        var flapShape = new THREE.Shape(); flapShape.moveTo(-EW / 2, 0); flapShape.lineTo(EW / 2, 0); flapShape.lineTo(0, ED * 0.45); flapShape.lineTo(-EW / 2, 0);
        var flap = new THREE.Mesh(new THREE.ShapeGeometry(flapShape), K.mat("os-env-f", { color: 0xefe7d8, roughness: 0.88, side: THREE.DoubleSide }));
        var hinge = new THREE.Group(); hinge.position.set(0, 0.0012, -ED / 2); hinge.add(flap); flap.rotation.x = -Math.PI / 2;
        hinge.rotation.x = -THREE.MathUtils.degToRad(180 - o.flap); g.add(hinge);
        var lt = N.canvasTex(THREE, 864, 600, function (c, w, h) {
          c.fillStyle = "#fbf6ec"; c.fillRect(0, 0, w, h); var r = N.rng(o.seed);
          for (var L = 0; L < 11; L++) { var y = 60 + L * 46, x = 60, end = w - 60 - r() * 120; if (L === 2) { c.fillStyle = "rgba(224,149,106,0.95)"; c.fillRect(50, y - 10, w - 100, 30); }
            while (x < end) { var ww = 14 + r() * 50; c.fillStyle = L === 2 ? "rgba(80,40,25,0.9)" : "rgba(74,63,107,0.55)"; c.fillRect(x, y, Math.min(ww, end - x), 10); x += ww + 10; } }
        });
        var letter = new THREE.Mesh(new THREE.BoxGeometry(EW * 0.92, 0.0006, ED * 1.3), [plain, plain, K.mat("os-letter", { color: 0xffffff, map: lt, roughness: 0.86 }), plain, plain, plain]);
        letter.position.set(0, 0.0016, -ED * o.letter); g.add(letter);
        g.userData.keepOrigin = true;
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
