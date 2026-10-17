/* deck/2026-10-17-section.js — the chassis for the 2026-10-17 deck: MD Anderson's AI model SPACER,
 * which reads gene activity mapped across intact tumor tissue to infer why T cells gather in some
 * regions and avoid others, and points at mucin as a physical barrier that may keep them out
 * (tx-2026-0217).
 *
 * THE WORLD. A tissue section cut thin and laid on a glass slide, rendered as a material relief
 * (txbench.js) under ONE raking key. Plan view, orthographic, height in CSS px out of the glass.
 * Nothing here is a real patient's tissue. Every section, nest, wall and cell is drawn to
 * illustrate, at a scale the frame states.
 *
 * THE LIGHT is azimuth 300, elevation 16: the key comes low from the upper left, so every lit face
 * is an upper left face and every cast runs down and to the right. A low key is what makes a
 * section a few cells thick read as a landscape with walls and beads in it.
 *
 * THE MATERIAL VOCABULARY, one id per material on every frame:
 *   0 GLASS   the slide and the dark field around the section, near black
 *   1 STROMA  the connective tissue between nests, dark plum fibre
 *   2 TUMOR   the nest, a cobble of cells with a nucleus dimple each, oxblood
 *   3 MUCIN   the sugar coat, smooth and glossy, a pale cool grey with a hard specular
 *   4 TCELL   a T cell, a round bead in dusk ember, the deck's one accent and nothing else wears it
 *   5 SPOT    a measured spot of the gene map, a shallow well in graphite
 *   6 STEEL   a scale bar or a measured ruler, worn steel
 *   7 LABEL   the slide's frosted label end, a matte pale glass
 *   8 SLIDE   the slide's own glass, near black with a green cast and a hard specular on its bevel
 *   9 STAGE   a microscope stage, black anodised metal with a brushed sheen
 *  10 BEVEL   a slide's ground glass edge, a pale green that catches the key on the faces turned to it
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame here. It hands a frame fields, cells, beads and the
 * one relief call with the deck's light and materials. Every frame builds its own geometry, and the
 * figures a frame draws are written in that frame's own code where figure_bearing.py reads them.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK || !global.TXBENCH) throw new Error("section.js needs txdeck.js and txbench.js loaded first");

  TXDECK.declare({
    world: "section",
    light: { az: 300, el: 16 },
    ground: "#05040A",
    material: "#3A1424",
    accent: "#B4664F",
    grade: { filmic: false, exposure: 0, saturation: 1.0, contrast: 1.06, aberration: 0,
             grain: { amount: 0.007, size: 1, seed: 20261017 }, vignette: 0.12 }
  });

  var N = {};
  N.W = 1080; N.H = 1350; N.SC = 2;
  N.GLASS = 0; N.STROMA = 1; N.TUMOR = 2; N.MUCIN = 3; N.TCELL = 4; N.SPOT = 5; N.STEEL = 6; N.LABEL = 7; N.SLIDE = 8; N.STAGE = 9; N.BEVEL = 10;

  /* linear albedo per material, with a little tooth so no surface is a flat fill */
  var BASE = {
    0: [0.004, 0.0035, 0.008],
    1: [0.085, 0.022, 0.050],
    2: [0.150, 0.028, 0.045],
    3: [0.28, 0.34, 0.44],
    4: [0.74, 0.20, 0.11],
    5: [0.050, 0.048, 0.055],
    6: [0.13, 0.13, 0.14],
    7: [0.50, 0.49, 0.47],
    8: [0.032, 0.024, 0.030],
    9: [0.026, 0.015, 0.022],
    10: [0.21, 0.17, 0.16]
  };
  N.albedo = function (X, Y, m) {
    var b = BASE[m] || BASE[0];
    var tooth = 0.93 + 0.07 * TX.simplex2(X * 0.21, Y * 0.21);
    return [b[0] * tooth, b[1] * tooth, b[2] * tooth];
  };
  N.spec = { 1: [0.06, 20], 2: [0.14, 34], 3: [2.4, 170], 4: [0.55, 60], 5: [0.08, 25], 6: [2.4, 220], 7: [0.04, 12], 8: [1.0, 160], 9: [0.45, 40], 10: [1.6, 90] };

  /* A FIELD: evaluate fn(X, Y) -> [height, material] once per device pixel into two buffers, then
   * hand txbench a lookup. Evaluating twice (once for height, once for material) doubles the cost
   * of every frame and gets nothing for it. */
  N.field = function (fn) {
    var W = N.W * N.SC, H = N.H * N.SC, hb = new Float32Array(W * H), mb = new Uint8Array(W * H);
    for (var j = 0; j < H; j++) for (var i = 0; i < W; i++) {
      var o = fn((i + 0.5) / N.SC, (j + 0.5) / N.SC), k = j * W + i;
      hb[k] = o[0]; mb[k] = o[1];
    }
    function idx(X, Y) {
      var i = Math.min(W - 1, Math.max(0, Math.floor(X * N.SC))), j = Math.min(H - 1, Math.max(0, Math.floor(Y * N.SC)));
      return j * W + i;
    }
    return { height: function (X, Y) { return hb[idx(X, Y)]; }, material: function (X, Y) { return mb[idx(X, Y)]; } };
  };

  /* CELLS: a jittered grid Voronoi of a given cell size. Returns [d1, d2, sx, sy, id] for a point:
   * the distance to the nearest seed, to the second, the nearest seed and a stable integer id. */
  N.cells = function (size, seed) {
    var cache = new Map(), s0 = seed || 1;
    function hash(i, j, k) { var h = Math.sin(i * 127.1 + j * 311.7 + k * 74.7 + s0 * 19.19) * 43758.5453; return h - Math.floor(h); }
    function at(i, j) {
      var key = i * 65536 + j, s = cache.get(key);
      if (!s) { s = [(i + 0.02 + 0.96 * hash(i, j, 1)) * size, (j + 0.02 + 0.96 * hash(i, j, 2)) * size, hash(i, j, 3)]; cache.set(key, s); }
      return s;
    }
    return function (X, Y) {
      var i = Math.floor(X / size), j = Math.floor(Y / size), d1 = 1e9, d2 = 1e9, b = null;
      for (var a = -1; a <= 1; a++) for (var c = -1; c <= 1; c++) {
        var s = at(i + a, j + c), d = Math.hypot(X - s[0], Y - s[1]);
        if (d < d1) { d2 = d1; d1 = d; b = s; } else if (d < d2) d2 = d;
      }
      return [d1, d2, b[0], b[1], b[2]];
    };
  };

  /* BEADS: round raised cells (a T cell, a spot) in a spatial hash, so a frame can carry hundreds.
   * Each bead is [x, y, r]. Returns the bead's dome height at a point, or -1 outside every bead. */
  N.beads = function (list, cell) {
    cell = cell || 32;
    var map = new Map();
    list.forEach(function (b) {
      var k = Math.floor(b[0] / cell) * 65536 + Math.floor(b[1] / cell);
      if (!map.has(k)) map.set(k, []);
      map.get(k).push(b);
    });
    return function (X, Y) {
      var gi = Math.floor(X / cell), gj = Math.floor(Y / cell), best = -1;
      for (var a = -1; a <= 1; a++) for (var c = -1; c <= 1; c++) {
        var L = map.get((gi + a) * 65536 + gj + c);
        if (!L) continue;
        for (var n = 0; n < L.length; n++) {
          var b = L[n], d = Math.hypot(X - b[0], Y - b[1]);
          if (d < b[2]) { var h = Math.sqrt(1 - (d / b[2]) * (d / b[2])) * b[2] * 0.95; if (h > best) best = h; }
        }
      }
      return best;
    };
  };

  /* STROMA: wavy fibre bundles with open lacunae, dark plum. The fibre runs along a slow field so it
   * reads as tissue rather than as corduroy. */
  N.stroma = function (X, Y, k) {
    k = k || 1;
    var w = TX.fbm2(X * 0.006 * k, Y * 0.006 * k, 3);
    var f = Math.sin((X * 0.55 + Y * 0.83) * 0.30 * k + 5.0 * w);
    var gap = TX.fbm2(X * 0.018 * k + 11, Y * 0.018 * k + 3, 3);
    /* the lacunae: the fibre falls away into each open space over a few px, so a hole has a wall to it */
    var t = Math.max(0, Math.min(1, (gap + 0.36) / 0.12)), sm = t * t * (3 - 2 * t);
    if (sm <= 0) return [0, 0];
    return [(2.4 + 1.1 * f + 1.6 * Math.max(0, gap)) * sm, sm < 0.5 ? 0 : 1];
  };

  /* THE COAT'S CROSS-SECTION: a smooth dome that rises from the ground it meets on each side, peaks a
   * little toward the side facing the key, and carries only long, low ripples along its length. u runs
   * 0 at the outer foot to 1 at the inner foot; lo and hi are the heights of the ground at each foot. */
  N.dome = function (u, lo, hi, peak, lean) {
    lean = lean == null ? 0.42 : lean;
    var v = u < lean ? 0.5 * u / lean : 0.5 + 0.5 * (u - lean) / (1 - lean);   // the crest sits at u = lean
    var b = Math.sin(Math.PI * Math.max(0, Math.min(1, v)));
    var base = lo + (hi - lo) * (u * u * (3 - 2 * u));
    return base + (peak - Math.max(lo, hi)) * Math.pow(b, 1.4);
  };

  /* THE RELIEF OPTIONS, with the deck's light (txbench reads it from the declaration), materials and
   * finish. Every frame makes the TXBENCH.relief call itself, passing its field through this, so the gates
   * that read a frame's own code see the relief it renders. */
  N.opts = function (fld, o) {
    o = o || {};
    return {
      x: 0, y: 0, w: N.W, h: N.H, scale: N.SC,
      height: fld.height, material: fld.material, albedo: N.albedo, spec: N.spec,
      ambient: o.ambient == null ? 0.12 : o.ambient, diffuse: o.diffuse == null ? 1.65 : o.diffuse,
      keyMask: o.pool ? N.pool(o.pool) : undefined,
      ao: 0.9, shadow: 0.9, softness: o.softness || 5, castLength: o.castLength || 90,
      visBlur: o.visBlur || 0, visSharp: o.visSharp, dither: true
    };
  };

  /* A POOL OF KEY LIGHT: the key gated by a soft ellipse, full inside and falling to a floor outside, so a
   * frame is lit where its subject is and the rest of the bench goes dark. o = {x, y, r, floor}. */
  N.pool = function (o) {
    var fl = o.floor == null ? 0.25 : o.floor;
    return function (X, Y) {
      var d = Math.hypot((X - o.x) / (o.rx || o.r), (Y - o.y) / (o.ry || o.r));
      var t = Math.max(0, Math.min(1, (d - 0.55) / 0.6)), sm = t * t * (3 - 2 * t);
      return 1 - (1 - fl) * sm;
    };
  };
  /* THE SEAM where the art begins under the type: a darken-only fade over its top so the bench never stops
   * at a ruled line. */
  N.seam = function (cx, y, h) {
    h = h || 90;
    var g = cx.createLinearGradient(0, y - 60, 0, y + h);   // feathered both ways, so it never ends in a step
    g.addColorStop(0, "rgba(4,3,8,0)"); g.addColorStop(60 / (h + 60), "rgba(4,3,8,0.32)"); g.addColorStop(1, "rgba(4,3,8,0)");
    cx.fillStyle = g; cx.fillRect(0, y - 60, N.W, h + 60);
  };
  /* A RESERVE under one line of type: a feathered dark patch behind the element, so a wall's edge or a
   * row of cells never runs through its glyphs. It only darkens, and only there. */
  N.knock = function (cx, sel, a) {
    var el = document.querySelector(sel);
    if (!el) return;
    var r = el.getBoundingClientRect();
    cx.save(); cx.filter = "blur(14px)"; cx.fillStyle = "rgba(4,3,8," + Math.min(0.5, a == null ? 0.5 : a) + ")";
    cx.fillRect(r.left - 22, r.top - 12, r.width + 44, r.height + 24); cx.restore();
  };

  /* -------------------------------------------------------------- type seating */
  N.INK = "#ECE6DC";
  N.CSS = function () {
    var ink = N.INK, dek = "#D6CEC4", halo = "rgba(3,2,6,0.65)", halo2 = "rgba(3,2,6,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#05040A; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:1.06; letter-spacing:0.004em; text-wrap:balance; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:840px; font-size:31px; font-weight:600; line-height:1.38; text-wrap:pretty; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.05em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      '.lab.acc { color:#E0A08A; }',
      '.lab.big { font-size:56px; font-weight:700; letter-spacing:0; }',
      ".hook, .dek, .tx-site, .kick, .src, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = async function (o) {
    await document.fonts.ready;
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D6CEC4" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 72, max: 100, maxLines: 2 });
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) {
      d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px";
    });
    /* yield once so the page's load event fires before the field is computed */
    await new Promise(function (r) { setTimeout(r, 0); });
    TX.reseed(o.seed || 20261017);
    var c = document.getElementById("art"); c.width = N.W * N.SC; c.height = N.H * N.SC;
    var cx = c.getContext("2d"); cx.scale(N.SC, N.SC);
    return cx;
  };
  /* The bottom of the type block, so a frame keeps its section below it. */
  N.typeBottom = function (pad) {
    var dek = document.querySelector(".dek"), h = document.getElementById("hook"), el = dek || h;
    var b = el.getBoundingClientRect();
    return b.top + b.height + (pad == null ? 40 : pad);
  };
  /* THE DARK BAND THE TYPE STANDS IN, and a foot wash under the site line. Both only darken, and
   * neither exceeds 0.5. */
  N.post = function (cx, o) {
    o = o || {};
    var bottom = o.to == null ? N.typeBottom(60) : o.to, a = Math.min(0.5, o.a == null ? 0.0 : o.a);
    if (a > 0) {
      var fade = o.fade || 160, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(4,3,8," + a + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(4,3,8," + (a * 0.85) + ")");
      g.addColorStop(1, "rgba(4,3,8,0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
    var f = document.querySelector(".tx-site");
    if (f && o.footWash) {
      var r = f.getBoundingClientRect(), feather = N.H - r.bottom, fa = Math.min(o.footWash, 0.5);
      var fw = cx.createLinearGradient(0, r.top - feather, 0, N.H);
      fw.addColorStop(0, "rgba(4,3,8,0)");
      fw.addColorStop(feather / (N.H - r.top + feather), "rgba(4,3,8," + fa + ")");
      fw.addColorStop(1, "rgba(4,3,8," + fa + ")");
      cx.fillStyle = fw; cx.fillRect(0, r.top - feather, N.W, N.H - r.top + feather);
    }
  };
  /* LIGHT FROM BELOW, for a frame where a lamp shines up through glass: a warm transmitted glow laid over
   * the rendered relief inside a circle, screened so dark tissue there reads backlit rather than painted. */
  N.transmit = function (cx, x, y, r, o) {
    o = o || {};
    cx.save();
    cx.beginPath(); cx.arc(x, y, r, 0, Math.PI * 2); cx.clip();
    cx.globalCompositeOperation = "screen";
    var g = cx.createRadialGradient(x - r * 0.12, y - r * 0.1, r * 0.05, x, y, r);
    g.addColorStop(0, "rgba(255,236,214," + (o.peak == null ? 0.78 : o.peak) + ")");
    g.addColorStop(0.7, "rgba(214,176,150," + (o.mid == null ? 0.42 : o.mid) + ")");
    g.addColorStop(1, "rgba(120,80,70,0.10)");
    cx.fillStyle = g; cx.fillRect(x - r, y - r, r * 2, r * 2);
    cx.restore();
  };
  /* a DOM leader from a label to the point it names, ending short of the glyphs */
  N.leader = function (svg, from, to) {
    var NS = "http://www.w3.org/2000/svg";
    var u = document.createElementNS(NS, "line");
    u.setAttribute("x1", from[0]); u.setAttribute("y1", from[1]); u.setAttribute("x2", to[0]); u.setAttribute("y2", to[1]);
    u.setAttribute("stroke", "#05040A"); u.setAttribute("stroke-width", "5"); u.setAttribute("stroke-opacity", "0.6"); svg.appendChild(u);
    var l = document.createElementNS(NS, "line");
    l.setAttribute("x1", from[0]); l.setAttribute("y1", from[1]); l.setAttribute("x2", to[0]); l.setAttribute("y2", to[1]);
    l.setAttribute("stroke", N.INK); l.setAttribute("stroke-width", "2"); l.setAttribute("stroke-opacity", "0.85"); svg.appendChild(l);
    var c = document.createElementNS(NS, "circle");
    c.setAttribute("cx", to[0]); c.setAttribute("cy", to[1]); c.setAttribute("r", "5"); c.setAttribute("fill", N.INK); svg.appendChild(c);
  };

  global.SEC = N;
})(this);
