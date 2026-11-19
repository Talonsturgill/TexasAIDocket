/* deck/2026-11-17-scorebench-bespoke.js, the SPINE for the November 17th, 2026 carousel (BESPOKE run, knowledge/carousel/BESPOKE.md):
 * the Texas Education Agency's automated scoring engine reads every written STAAR answer first, and districts asked 64,489
 * times this spring for a person to read one again (tx-2026-0194).
 *
 * THE SPINE AND NOTHING ELSE. It declares look v2, the WATCH tone, bespoke:true, the tone's grade and the accent. Each
 * frame picks its own world (TXT.sky(R, world)), turns its own key (TXT.deckRig(..., { light })) and places its own type,
 * seated with CH.seat. It mounts the type faces and the furniture (CH.start), and hands a frame the helpers below. There is
 * no drawFrame.
 *
 * THE ACCENT. Dusk gold #E0956A (brand.yaml) means ONE thing: A PERSON'S SCORE. The page that goes on to a person, the
 * lamp a person reads by, the tabs of human scored cards, a gilt raised page, a raised tile, the route back to a person.
 * Never the machine, never a count of requests, never decoration. Studio and room floors are kept violet rose so the gold
 * never fights the watch tone's coral.
 *
 * THE MODELS. The kit holds the rooms, furniture and people. The chassis builds the four things the kit lacks, in the kit's
 * conventions so Phase 17 can queue the lift: scoring_engine (sealed, no screen, no logo, no eye), response_sheet (greeked
 * TYPED lines, because STAAR is answered online, never handwriting, never legible), card_cabinet, and paper_column (one
 * modelled 0.1 mm sheet per request, drawn to illustrate). Every count a frame draws is read from window.FIG in that frame's
 * own code. The chassis types no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("scorebench.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "scorebench", look: "v2", tone: "watch", bespoke: true,
    light: { az: -40, el: 14 },
    sky: { preset: "v2watch" },
    ground: "#c98a9a",
    material: "#f3ead9",
    accent: "#e0956a",
    grade: TXLOOK.grade("watch")
  });

  var N = {};
  N.KEY_SCALE = 1;
  N.W = 1080; N.H = 1350; N.SEED = 20261117; N.TONE = "watch"; N.P = TXLOOK.palette("watch"); N.INK = N.P.ink;
  N.ACCENT = 0xe0956a;        /* dusk gold: a person's score, and nothing else */
  N.GOLD = N.ACCENT;
  /* a seeded canvas texture, so every surface carries tooth in its albedo and never in its height */
  N.canvasTex = function (THREE, w, h, paint, repeat) {
    var c = document.createElement("canvas"); c.width = w; c.height = h; var g = c.getContext("2d"); paint(g, w, h);
    var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
    return t;
  };
  N.rng = function (seed) { var t = seed >>> 0; return function () { t = (t + 0x6D2B79F5) >>> 0; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; };


  /* THE FOUR MODELS THE KIT LACKS. A frame calls nothing: CH.boot installs them. */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.scoring_engine) return;
    var violetM = function () { return K.mat('sb_violet', { color: 0x4a3f86, metalness: 0.75, roughness: 0.34, clearcoat: 0.3, clearcoatRoughness: 0.3 }, true); };
    var darkM = function () { return K.mat('sb_dark', { color: 0x2b2452, metalness: 0.6, roughness: 0.45 }); };
    var smokeM = function (o) { return K.mat('sb_smoke' + (o ? 'c' : ''), { color: 0x3a3070, metalness: 0.1, roughness: 0.05, transmission: o ? 0.75 : 0.35, transparent: true, opacity: o ? 0.35 : 0.85, clearcoat: 1, clearcoatRoughness: 0.02, envMapIntensity: 1.6 }, true); };
    var rubberM = function () { return K.mat('sb_rubber', { color: 0x1d1a2a, roughness: 0.7 }); };
    var scanM = function () { return K.mat('sb_scan', { color: 0x111111, emissive: 0xcfc6ff, emissiveIntensity: 3.2 }); };
    var goldM = function () { return K.mat('sb_gold', { color: N.ACCENT, metalness: 0.7, roughness: 0.32, clearcoat: 0.5, clearcoatRoughness: 0.2 }, true); };
    var paperTex = N.canvasTex(THREE, 512, 662, function (c, w, h) {
      var r = N.rng(17); c.fillStyle = "#f3ead9"; c.fillRect(0, 0, w, h);
      for (var i = 0; i < 2600; i++) { c.fillStyle = "rgba(120,100,80," + (r() * 0.05).toFixed(3) + ")"; c.fillRect(r() * w, r() * h, 1 + r() * 2, 1); }
      /* greeked TYPED lines, never handwriting, never legible: even ragged right blocks of short bars */
      c.fillStyle = "rgba(48,44,70,0.62)"; var y = 120;
      while (y < h - 50) { var x = 46, end = w - 46 - r() * 70; while (x < end) { var ww = 8 + r() * 34; if (x + ww > end) break; c.fillRect(x, y, ww, 6); x += ww + 7; } y += r() < 0.12 ? 34 : 20; }
      c.strokeStyle = "rgba(60,52,110,0.7)"; c.lineWidth = 3; c.strokeRect(w - 128, 28, 92, 64);   /* the empty score box */
    });
    var paperM = function () { return K.mat('sb_paper', { color: 0xffffff, roughness: 0.86, metalness: 0, map: paperTex }); };
    var edgeM = function () { return K.mat('sb_edge', { color: 0xeee3cf, roughness: 0.9 }); };

    /* A RESPONSE SHEET. Letter paper, 0.216 x 0.279 m, lying flat (y up), long side along z, with greeked typed lines and a
     * score box at the top right. state 'blank' | 'routed' | 'gold' sets the score box; gilt:true gilds its edges. curl lifts
     * the far edge. It is an illustrative unit for one written answer, never a real student's work. */
    K.define("response_sheet", { size: [0.216, 0.0006, 0.279], options: { state: "blank", gilt: false, curl: 0, thick: 0.0006 },
      note: "One letter sheet lying flat, typed greeked lines, a score box top right. state blank|routed|gold, gilt edges, curl. An illustrative unit for one written answer.",
      make: function (o) {
        var g = new THREE.Group(), W = 0.216, D = 0.279, t = o.thick || 0.0006;
        var geo = new THREE.BoxGeometry(W, t, D, 1, 1, o.curl ? 12 : 1);
        if (o.curl) { var p = geo.attributes.position; for (var i = 0; i < p.count; i++) { var z = p.getZ(i), k = (z / D + 0.5); p.setY(i, p.getY(i) + o.curl * 0.06 * k * k); } geo.computeVertexNormals(); }
        var mats = [o.gilt ? goldM() : edgeM(), o.gilt ? goldM() : edgeM(), paperM(), edgeM(), o.gilt ? goldM() : edgeM(), o.gilt ? goldM() : edgeM()];
        var m = new THREE.Mesh(geo, mats); m.position.y = t / 2; m.castShadow = true; m.receiveShadow = true; g.add(m);
        if (o.state === "routed" || o.state === "gold") {
          var mark = new THREE.Mesh(new THREE.PlaneGeometry(0.034, 0.024), o.state === "gold" ? goldM() : K.mat('sb_tick', { color: 0x111111, emissive: 0xcfc6ff, emissiveIntensity: 1.4 }));
          mark.rotation.x = -Math.PI / 2; mark.position.set(W / 2 - 0.035, t + 0.0004, -D / 2 + 0.024); g.add(mark);
        }
        return g;
      } });

    /* A SCORING ENGINE. A sealed sheet fed reader, 1.6 m long (x), 0.95 m tall, 0.7 m deep (z), on a plinth. Graphite violet
     * anodised housing with rounded edges, a smoked glass read window across the top with an emissive lilac scan bar, an
     * infeed tray at -x, two rubber feed rollers in the throat, an outfeed tray at +x and a diverter with a chute rising to
     * +x (userData.chuteStart, chuteEnd). cutaway:true makes the housing smoked glass so the paper path shows. No screen, no
     * logo, no eye shaped light. The chute may be gold (chuteGold) where a frame shows a person's score. */
    K.define("scoring_engine", { size: [1.6, 0.95, 0.7], options: { cutaway: false, chute: true, chuteGold: false, chuteLen: 1.1, scan: true },
      note: "A sealed graphite violet sheet reader 1.6 x 0.95 x 0.7 m, smoked read window with a lilac scan bar, infeed at -x, outfeed and diverter chute at +x. cutaway shows the paper path. userData.feedY, chuteStart, chuteEnd.",
      make: function (o) {
        var g = new THREE.Group(), V = o.cutaway ? smokeM(true) : violetM(), Dk = darkM();
        K.box(1.5, 0.12, 0.62, Dk, 0, 0, 0, 0.02, g);                                       /* plinth */
        K.box(1.6, 0.55, 0.7, V, 0, 0.12, 0, 0.05, g);                                       /* housing body */
        K.box(1.3, 0.2, 0.6, V, 0.05, 0.67, 0, 0.05, g);                                     /* crown over the read path */
        var win = K.box(0.7, 0.03, 0.42, smokeM(false), 0.05, 0.87, 0, 0.01, g);            /* smoked read window */
        if (o.scan) { var sc = K.box(0.04, 0.012, 0.44, scanM(), 0.05, 0.9, 0, 0.004, g); }
        K.box(0.4, 0.02, 0.36, Dk, -0.98, 0.6, 0, 0.006, g);                                 /* infeed tray */
        K.box(0.02, 0.06, 0.36, Dk, -1.17, 0.6, 0, 0.004, g);
        [-0.02, 0.02].forEach(function (dy) { var r = K.cyl(0.02, 0.02, 0.5, rubberM(), -0.8, 0.66 + dy, 0, 24, g); r.rotation.x = Math.PI / 2; });
        K.box(0.38, 0.02, 0.36, Dk, 0.98, 0.4, 0, 0.006, g);                                 /* outfeed tray */
        K.box(0.02, 0.07, 0.36, Dk, 1.17, 0.4, 0, 0.004, g);
        g.userData.feedY = 0.62; g.userData.outY = 0.42;
        if (o.cutaway) {                                                                     /* the paper path inside */
          K.box(1.3, 0.008, 0.4, Dk, 0, 0.62, 0, 0.002, g);
          var dv = K.box(0.18, 0.01, 0.36, goldM(), 0.72, 0.5, 0, 0.003, g); dv.rotation.z = 0.35;
        }
        if (o.chute) {
          var L = o.chuteLen, cm = o.chuteGold ? goldM() : Dk, ch = new THREE.Group(); ch.position.set(0.8, 0.5, 0); ch.rotation.z = 0.42; g.add(ch);
          K.box(L, 0.012, 0.3, cm, L / 2, 0, 0, 0.003, ch); K.box(L, 0.04, 0.012, cm, L / 2, 0, 0.15, 0.002, ch); K.box(L, 0.04, 0.012, cm, L / 2, 0, -0.15, 0.002, ch);
          g.userData.chuteStart = [0.8, 0.5, 0]; g.userData.chuteEnd = [0.8 + L * Math.cos(0.42), 0.5 + L * Math.sin(0.42), 0]; g.userData.chuteAngle = 0.42;
        }
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      } });

    /* A CARD CABINET. Powder coated violet steel, 0.52 w x 0.42 h x 0.48 d m, two by two drawer bays with label holders and
     * a lock cylinder, on a kick base. open names the bay (0 to 3) pulled out by `pull` metres; the frame puts a kit
     * index_card_drawer in it. userData.drawerAt is the open drawer's floor centre. */
    K.define("card_cabinet", { size: [0.52, 0.42, 0.48], options: { open: 2, pull: 0.32 },
      note: "A powder coated steel card cabinet 0.52 x 0.42 x 0.48 m, four drawer bays, label holders, a lock. open bay pulled by pull m. userData.drawerAt, drawerW, drawerD for a kit index_card_drawer.",
      make: function (o) {
        var g = new THREE.Group(), S = K.mat('sb_cab', { color: 0x5a4f9a, metalness: 0.4, roughness: 0.5 }), Ch = K.finish.chrome();
        K.box(0.5, 0.03, 0.44, darkM(), 0, 0, 0, 0.004, g);                                  /* kick base */
        var bw = 0.25, bh = 0.19;
        K.box(0.52, 0.42, 0.02, S, 0, 0.03, -0.23, 0.006, g); K.box(0.02, 0.42, 0.48, S, -0.25, 0.03, 0, 0.004, g); K.box(0.02, 0.42, 0.48, S, 0.25, 0.03, 0, 0.004, g);
        K.box(0.52, 0.02, 0.48, S, 0, 0.43, 0, 0.006, g);
        for (var i = 0; i < 4; i++) {
          var cx = i % 2 ? bw / 2 : -bw / 2, cy = 0.04 + (i < 2 ? bh + 0.01 : 0), pull = i === o.open ? o.pull : 0;
          K.box(bw - 0.01, bh - 0.01, 0.02, S, cx, cy, 0.23 + pull, 0.006, g);              /* drawer front */
          K.box(0.08, 0.03, 0.006, Ch, cx, cy + bh * 0.62, 0.243 + pull, 0.002, g);         /* label holder */
          K.box(0.06, 0.012, 0.012, Ch, cx, cy + bh * 0.35, 0.248 + pull, 0.004, g);        /* pull */
          if (i === o.open) { g.userData.drawerAt = [cx, cy + 0.01, 0.23 + pull - 0.21]; g.userData.drawerW = bw - 0.03; g.userData.drawerD = 0.42; }
        }
        var lk = K.cyl(0.008, 0.008, 0.01, Ch, 0, 0.405, 0.24, 20, g); lk.rotation.x = Math.PI / 2;
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      } });

    /* A PAPER COLUMN. A stack of `count` letter sheets at `sheet` metres each (0.0001 by default, a modelled thickness used
     * only for the drawing), so its height is count x sheet. A kraft ream band wraps every `ream` sheets, each ream turns
     * a seeded fraction of a degree and slides a millimetre or two, and the top `loose` sheets curl. color tints the paper
     * (gold for raised scores). It stands on y=0, footprint centred. userData.height. */
    K.define("paper_column", { size: [0.216, 1, 0.279], options: { count: 500, sheet: 0.0001, ream: 500, seed: 7, color: null, loose: 8, bands: true },
      note: "A stack of count letter sheets at sheet m each (modelled 0.1 mm), kraft band every ream sheets, seeded per ream skew, curled loose top sheets. userData.height = count x sheet.",
      make: function (o) {
        var g = new THREE.Group(), r = K.rng(o.seed), H = o.count * o.sheet, rh = o.ream * o.sheet, n = Math.ceil(o.count / o.ream);
        var pc = o.color != null ? o.color : 0xf1e7d4;
        var side = N.canvasTex(THREE, 64, 512, function (c, w, h) { c.fillStyle = "#" + pc.toString(16).padStart(6, "0"); c.fillRect(0, 0, w, h); for (var y = 0; y < h; y += 2) { c.fillStyle = "rgba(90,70,60," + (0.04 + Math.random() * 0.06).toFixed(3) + ")"; c.fillRect(0, y, w, 1); } }, [1, Math.max(1, rh / 0.02)]);
        var sideM = K.mat('sb_col_' + pc, { color: 0xffffff, roughness: 0.88, map: side });
        var topM = K.mat('sb_coltop_' + pc, { color: pc, roughness: 0.85 });
        var kraftM = K.mat('sb_kraft', { color: 0xa8794f, roughness: 0.9 });
        var y = 0;
        for (var i = 0; i < n; i++) {
          var cnt = Math.min(o.ream, o.count - i * o.ream), h = cnt * o.sheet, ream = new THREE.Group();
          ream.position.set((r() - 0.5) * 0.004, y, (r() - 0.5) * 0.004); ream.rotation.y = (r() - 0.5) * 0.026; g.add(ream);
          var m = new THREE.Mesh(new THREE.BoxGeometry(0.216, h, 0.279), [sideM, sideM, topM, topM, sideM, sideM]); m.position.y = h / 2; m.castShadow = true; m.receiveShadow = true; ream.add(m);
          if (o.bands && cnt === o.ream && h > 0.012) { var b = new THREE.Mesh(new THREE.BoxGeometry(0.2185, Math.min(0.05, h * 0.9), 0.2815), kraftM); b.position.y = h * 0.5; b.castShadow = true; ream.add(b); }
          y += h;
        }
        for (var j = 0; j < o.loose; j++) { var s = K.make("response_sheet", { curl: 0.3 + r() * 0.8, thick: 0.0004 }); s.children[0].material = s.children[0].material.map(function () { return topM; }); s.position.set((r() - 0.5) * 0.02, y + j * 0.0006, (r() - 0.5) * 0.02); s.rotation.y = (r() - 0.5) * 0.3; g.add(s); }
        g.userData.height = H; return g;
      } });
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
