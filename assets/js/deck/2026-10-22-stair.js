/* deck/2026-10-22-stair.js — the chassis for the 2026-10-22 deck: Texas A&M, with the University of
 * Texas at Austin and Purdue listed as the paper's institutions, continually trained four open
 * language models on junk and control posts from Twitter/X, and reasoning fell as the junk share
 * rose; the paper names thought skipping as the main failure and finds the repair partial
 * (tx-2026-0223).
 *
 * THE VISUAL ARGUMENT. Reasoning is a stair. Every score in the deck is the rise of a stair from the
 * ground at ONE scale, `N.S` metres per score point, so a falling score is lost height a reader can
 * stand under, and the brass datum on a sawn wall is where the base model stood. Junk is cast into the
 * treads as glass chip aggregate and control as limestone slivers. Thought skipping is treads gone.
 *
 * THE WORLD. lastLight, the house register and a STAGED world: the sun just down, a near black sky,
 * one low warm key, the stair standing in a pool of it on dark caliche and the field behind gone dark.
 * A stair is read by its nosing edges and the shadows under its treads, and a low raking key is the
 * one light that draws both.
 *
 * THE LIGHT is azimuth -58, elevation 10. +x is east and +z is south, az runs from +z toward +x, so
 * the key sits low in the south west of every subject: a camera on +z looking -z has the key low in
 * front and to its left, every nosing facing it is lit, and every cast runs long to the right and
 * away. A material relief reads it from the left of its frame, low, and every cast runs right.
 *
 * THE KIT MODELS THIS DECK BUILDS, the kit having none of them: `stair_flight` (an open stair of two
 * weathering steel stringers and exposed aggregate treads up to a sawn limestone landing on a pier,
 * any tread left out by index), `landing_pier` (a sawn limestone pier with an aggregate landing slab),
 * `datum_wall` (a coursed sawn limestone wall carrying a brass datum strip at a given height),
 * `tread_slab` (one loose cast tread, sawn short by a fraction) and `chalk_pad` (a concrete pad with a
 * chalk outline and nothing on it). Each is built in the kit's conventions (metres, y up, origin on
 * the ground, front on +z, a stair climbing toward -z) so Phase 17 can queue the lift.
 *
 * THE ACCENT is dusk gold, #E0956A, and it means ONE thing: the brass datum where the base model stood.
 *
 * WHAT THIS FILE IS NOT. There is no drawFrame. It hands a frame the world, the models and the way
 * type is seated. Every frame composes its own picture, and every score a frame draws is read from
 * figures.json in that frame's own code where figure_bearing.py reads it. The chassis types no figure
 * of the story. `N.S` is a drawing scale, the same on every frame, and no figure.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("stair.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "stair",
    light: { az: -58, el: 10 },
    sky: "lastLight",
    ground: "#08060F",
    material: "#B9AE98",
    accent: "#E0956A",
    grade: {
      exposure: 0,
      saturation: 1.0,
      contrast: 1.07,
      filmic: true,
      lift: [0.002, 0.003, 0.005],
      gain: [1.0, 1.0, 1.0],
      vignette: 0.22,
      bloom: { threshold: 0.9, strength: 0.08, radius: 8 },
      grain: { amount: 0.016, size: 2, seed: 20261022 },
      aberration: 0,
      dither: true,
      sharpen: 0.12
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261022;
  N.ACCENT = 0xe0956a;   /* dusk gold, brand.yaml's, and it means ONE thing: the base model's datum */
  N.INK = "#ECE6DA";
  /* THE DECK'S ONE SCALE: metres of rise per score point, on every stair in every frame */
  N.S = 0.06;
  N.RUN = 0.28;          /* a tread's going, metres */
  N.RISER = 0.18;        /* the riser a flight aims at, metres; the real one divides the rise evenly */
  N.WIDTH = 1.2;         /* a flight's clear width, metres */

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* ---- the materials of the world --------------------------------------------------------- */

  /* EXPOSED AGGREGATE, the tread's own surface: a buff cement matrix with pieces standing in it. `dose`
   * is the share of the pieces that are glass chips, the junk: short, bottle green or amber, glossy.
   * The rest are limestone slivers, the control: long, pale, matte. Albedo and roughness are painted
   * together, so a chip is dark and shines and a sliver is pale and does not. One tile is 0.4 m. */
  N.aggTex = function (THREE, dose, seed) {
    var key = "_agg" + Math.round(dose * 100) + "_" + (seed || 0);
    if (N[key]) return N[key];
    var S = 512, a = document.createElement("canvas"), r = document.createElement("canvas");
    a.width = a.height = r.width = r.height = S;
    var x = a.getContext("2d"), y = r.getContext("2d"), rnd = lcg(9100 + Math.round(dose * 100) * 7 + (seed || 0));
    x.fillStyle = "#8a8172"; x.fillRect(0, 0, S, S);
    y.fillStyle = "rgb(225,225,225)"; y.fillRect(0, 0, S, S);
    /* the matrix's own tooth: fine sand, light and dark, and a slow cloud so no tile reads flat */
    for (var c = 0; c < 26; c++) {
      var gx = rnd() * S, gy = rnd() * S, gr = 40 + rnd() * 120, gg = x.createRadialGradient(gx, gy, 0, gx, gy, gr);
      gg.addColorStop(0, rnd() < 0.5 ? "rgba(60,54,44,0.18)" : "rgba(180,170,150,0.14)"); gg.addColorStop(1, "rgba(0,0,0,0)");
      x.fillStyle = gg; x.fillRect(gx - gr, gy - gr, gr * 2, gr * 2);
    }
    for (var i = 0; i < 14000; i++) {
      var v = rnd(); x.fillStyle = v < 0.5 ? "rgba(52,46,38,0.45)" : "rgba(196,186,166,0.4)";
      x.fillRect(rnd() * S, rnd() * S, 1 + rnd() * 1.6, 1 + rnd() * 1.6);
    }
    var pieces = 120;
    for (var p = 0; p < pieces; p++) {
      var cx = rnd() * S, cy = rnd() * S, ang = rnd() * Math.PI;
      var glass = rnd() < dose;
      for (var ox = -S; ox <= S; ox += S) for (var oy = -S; oy <= S; oy += S) {
        var px = cx + ox, py = cy + oy;
        if (px < -60 || px > S + 60 || py < -60 || py > S + 60) continue;
        x.save(); y.save(); x.translate(px, py); y.translate(px, py); x.rotate(ang); y.rotate(ang);
        if (glass) {
          /* a broken bottle chip: dark body, a darker rim where it sinks into the matrix, one bright facet */
          var L = 9 + rnd() * 12, Wd = 6 + rnd() * 7, amber = rnd() < 0.3;
          x.fillStyle = "rgba(30,26,20,0.6)"; x.beginPath(); x.ellipse(0.8, 1, L / 2 + 1.5, Wd / 2 + 1.5, 0, 0, Math.PI * 2); x.fill();
          x.fillStyle = amber ? "#5a300c" : "#173320";
          x.beginPath(); x.moveTo(-L / 2, 0); x.lineTo(-L / 5, -Wd / 2); x.lineTo(L / 2, -Wd / 3); x.lineTo(L / 3, Wd / 2); x.lineTo(-L / 3, Wd / 2); x.closePath(); x.fill();
          x.fillStyle = amber ? "rgba(255,200,120,0.7)" : "rgba(170,235,190,0.6)"; x.fillRect(-L / 5, -Wd / 4, L / 2.6, 1.6);
          y.fillStyle = "rgb(18,18,18)"; y.beginPath(); y.ellipse(0, 0, L / 2, Wd / 2, 0, 0, Math.PI * 2); y.fill();
        } else {
          /* a limestone sliver, close in value to the matrix, told apart by its length and a shadowed lower edge */
          var L2 = 26 + rnd() * 30, W2 = 5 + rnd() * 5;
          x.fillStyle = "rgba(40,34,26,0.35)"; x.beginPath(); x.ellipse(0.8, 1.2, L2 / 2, W2 / 2 + 0.8, 0, 0, Math.PI * 2); x.fill();
          x.fillStyle = "rgb(" + (168 + rnd() * 20 | 0) + "," + (160 + rnd() * 18 | 0) + "," + (142 + rnd() * 16 | 0) + ")";
          x.beginPath(); x.ellipse(0, 0, L2 / 2, W2 / 2, 0, 0, Math.PI * 2); x.fill();
          y.fillStyle = "rgb(205,205,205)"; y.beginPath(); y.ellipse(0, 0, L2 / 2, W2 / 2, 0, 0, Math.PI * 2); y.fill();
        }
        x.restore(); y.restore();
      }
    }
    var mt = new THREE.CanvasTexture(a), rt = new THREE.CanvasTexture(r);
    [mt, rt].forEach(function (t) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; });
    mt.colorSpace = THREE.SRGBColorSpace;
    N[key] = { map: mt, rough: rt };
    return N[key];
  };
  N.aggMat = function (THREE, dose, seed) {
    var k = "_aggm" + Math.round(dose * 100) + "_" + (seed || 0);
    if (N[k]) return N[k];
    var t = N.aggTex(THREE, dose, seed);
    N[k] = new THREE.MeshPhysicalMaterial({ map: t.map, roughnessMap: t.rough, roughness: 1.0, metalness: 0,
      color: 0xb4ab9a, clearcoat: dose > 0 ? 0.25 * dose : 0, clearcoatRoughness: 0.35, specularIntensity: 0.9 });
    return N[k];
  };
  /* A PAINTED SURFACE, one tile `metres` square: a base colour, a slow cloud, fine speckle and, for sawn
   * stone, the horizontal striations a gang saw leaves; returned as a map and a bump map */
  N.surfTex = function (THREE, kind, base, seed) {
    var key = "_surf_" + kind + "_" + base + "_" + seed;
    if (N[key]) return N[key];
    var S = 512, c = document.createElement("canvas"), b = document.createElement("canvas");
    c.width = c.height = b.width = b.height = S;
    var x = c.getContext("2d"), y = b.getContext("2d"), rnd = lcg(seed * 977 + kind.length);
    x.fillStyle = base; x.fillRect(0, 0, S, S); y.fillStyle = "#808080"; y.fillRect(0, 0, S, S);
    for (var k = 0; k < (kind === "rust" ? 60 : 30); k++) {
      var gx = rnd() * S, gy = rnd() * S, gr = 20 + rnd() * (kind === "rust" ? 70 : 140), gg = x.createRadialGradient(gx, gy, 0, gx, gy, gr);
      var tone = kind === "rust" ? (rnd() < 0.5 ? "rgba(140,70,30,0.45)" : "rgba(30,18,12,0.45)") : (rnd() < 0.5 ? "rgba(70,62,50,0.22)" : "rgba(220,210,190,0.16)");
      gg.addColorStop(0, tone); gg.addColorStop(1, "rgba(0,0,0,0)"); x.fillStyle = gg;
      /* drawn at every wrapped copy, so a cloud crossing the tile's edge carries on across the seam
       * (no. 57's piers showed a hard rectangle where one was cut off) */
      for (var ox = -S; ox <= S; ox += S) for (var oy = -S; oy <= S; oy += S) {
        x.save(); x.translate(ox, oy); x.fillRect(gx - gr, gy - gr, gr * 2, gr * 2); x.restore();
      }
    }
    if (kind === "sawn") for (var r = 0; r < S; r += 2 + rnd() * 5) {
      var a = 0.04 + rnd() * 0.08; x.fillStyle = "rgba(40,34,26," + a + ")"; x.fillRect(0, r, S, 1);
      y.fillStyle = "rgba(0,0,0," + (a * 2) + ")"; y.fillRect(0, r, S, 1);
    }
    for (var i = 0; i < 16000; i++) {
      var v = rnd(), px = rnd() * S, py = rnd() * S, sz = 1 + rnd() * (kind === "rust" ? 2.5 : 1.5);
      x.fillStyle = v < 0.5 ? "rgba(25,20,15,0.35)" : (kind === "rust" ? "rgba(170,90,40,0.35)" : "rgba(225,215,195,0.3)"); x.fillRect(px, py, sz, sz);
      y.fillStyle = v < 0.5 ? "rgba(0,0,0,0.35)" : "rgba(255,255,255,0.3)"; y.fillRect(px, py, sz, sz);
    }
    var t = new THREE.CanvasTexture(c), bt = new THREE.CanvasTexture(b);
    [t, bt].forEach(function (q) { q.wrapS = q.wrapT = THREE.RepeatWrapping; q.anisotropy = 8; });
    t.colorSpace = THREE.SRGBColorSpace;
    N[key] = { map: t, bump: bt };
    return N[key];
  };
  /* SAWN LIMESTONE, held to a mid albedo so a lit face stays out of the pale band */
  N.limeMat = function (K, fresh) {
    var k = "_limem" + (fresh ? 1 : 0);
    if (N[k]) return N[k];
    var t = N.surfTex(K.THREE, "sawn", fresh ? "#c2b8a2" : "#8f8574", fresh ? 2 : 1);
    N[k] = new K.THREE.MeshStandardMaterial({ map: t.map, bumpMap: t.bump, bumpScale: 1.2, roughness: 0.88, metalness: 0 });
    return N[k];
  };
  N.steelMat = function (K) {
    if (N._steel) return N._steel;
    var t = N.surfTex(K.THREE, "rust", "#6a4028", 5);
    /* the shadow side of a weathering steel plate under a dusk sky still holds a warm rust value; without
     * this the stringers fell to L* 0 and split the flight into lit treads floating in the dark (no. 57) */
    N._steel = new K.THREE.MeshStandardMaterial({ map: t.map, bumpMap: t.bump, bumpScale: 1.6, roughness: 0.78, metalness: 0.15,
      emissive: 0x4a2a18, emissiveMap: t.map, emissiveIntensity: 0.9 });
    return N._steel;
  };
  N.brassMat = function (THREE) {
    if (N._brass) return N._brass;
    /* LIT BRASS. A metal the key draws a glint along, with the accent held in a low glow so the hue
     * survives the dusk at feed size. The first build was self-lit and the art director read it as a
     * painted stripe (no. 57, frames 3 and 9) */
    N._brass = new THREE.MeshStandardMaterial({ color: 0xc98a52, metalness: 0.9, roughness: 0.3, emissive: N.ACCENT, emissiveIntensity: 0.55, fog: false });
    return N._brass;
  };
  /* the brass datum's face is drawn in the accent itself, outside the tone curve, because a thin
   * accent through the curve reads as grey at 432 px (no. 56, frame 6) */
  N.accentMat = function (THREE) {
    if (N._acc) return N._acc;
    N._acc = new THREE.MeshBasicMaterial({ color: N.ACCENT, toneMapped: false, fog: false });
    return N._acc;
  };

  /* ---- the models --------------------------------------------------------------------------- */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry.stair_flight) return;

    /* A FLIGHT climbing toward -z from its foot at the origin to a landing `rise` metres up. The riser
     * divides the rise evenly near N.RISER. Steps 0..n-2 are treads at (i+1) risers, the nth level is
     * the landing's top, exactly `rise`. `missing` leaves treads out by index; `treads` builds only the
     * first k from the foot. A tread's top lands on its level exactly: the stringer flats sit one tread
     * thickness under it. userData: rise, n, riser, foot depth of the landing front (landingZ). */
    K.define("stair_flight", {
      size: [1.4, 3.4, 4.6],
      options: { rise: 3.0, width: 1.2, run: 0.28, riser: 0.18, dose: 1, missing: [], treads: null, landing: 1.0, pier: true, stringers: true, seed: 1, fresh: false },
      note: "Open stair: two weathering steel stringers with sawtooth tops, exposed aggregate treads with a nosing, a sawn limestone landing on a pier. Climbs toward -z. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), rise = o.rise, w = o.width, run = o.run;
        var n = Math.max(1, Math.round(rise / o.riser)), r = rise / n, tt = 0.05, t = 0.05, D = 0.3;
        var steel = N.steelMat(K), lime = N.limeMat(K, o.fresh), agg = N.aggMat(THREE, o.dose, o.seed);
        var missing = {}; (o.missing || []).forEach(function (i) { missing[i] = 1; });
        var nT = n - 1, built = o.treads == null ? nT : Math.min(nT, o.treads);
        /* the stringers, extruded sawtooth plates on both sides */
        if (o.stringers && n >= 2) {
          var sh = new THREE.Shape(); sh.moveTo(0, 0);
          for (var i = 0; i < nT; i++) { sh.lineTo(i * run, (i + 1) * r - tt); sh.lineTo((i + 1) * run, (i + 1) * r - tt); }
          var dEnd = nT * run, yEnd = nT * r - tt, pitch = Math.atan2(r, run), Dk = D / Math.cos(pitch);
          sh.lineTo(dEnd, Math.max(0, yEnd - Dk));
          var d0 = Math.max(0, dEnd - (yEnd - Dk) * run / r);
          sh.lineTo(d0, 0); sh.lineTo(0, 0);
          var geo = new THREE.ExtrudeGeometry(sh, { depth: t, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.004, bevelSegments: 1 });
          geo.rotateY(Math.PI / 2);
          [-1, 1].forEach(function (sg) {
            var m = new THREE.Mesh(geo, steel); m.position.x = sg * (w / 2 + t / 2) - t / 2; m.castShadow = m.receiveShadow = true; g.add(m);
            /* bolt heads where each tread seat is fixed, two to a step, on the outer face */
            for (var b = 0; b < nT; b++) {
              [0.25, 0.75].forEach(function (f) {
                var bh = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.012, 10), K.mat("st_bolt", { color: 0x2f2a26, metalness: 0.6, roughness: 0.5 }));
                bh.rotation.z = Math.PI / 2; bh.position.set(sg * (w / 2 + t + 0.004), (b + 1) * r - tt - 0.06, -(b + f) * run); g.add(bh);
              });
            }
          });
        }
        /* the treads, each a cast slab with a bullnose nosing proud of the riser line */
        var nos = 0.035;
        for (var k = 0; k < built; k++) {
          if (missing[k]) continue;
          var tr = TXT.roundedBox(w + 2 * t + 0.04, tt, run + nos, 0.012, agg);
          K.uvBox(tr.geometry, 0.4);
          tr.position.set(0, (k + 1) * r - tt / 2, -(k + 0.5) * run + nos / 2);
          tr.castShadow = tr.receiveShadow = true; g.add(tr);
        }
        /* the landing and its pier */
        var L = o.landing, zf = -nT * run;
        if (L > 0) {
          var slabT = Math.min(0.16, rise);
          var slab = TXT.roundedBox(w + 2 * t + 0.16, slabT, L, 0.014, agg); K.uvBox(slab.geometry, 0.4);
          slab.position.set(0, rise - slabT / 2, zf - L / 2 + nos); slab.castShadow = slab.receiveShadow = true; g.add(slab);
          if (o.pier && rise - slabT > 0.01) {
            var ph = rise - slabT, pier = TXT.roundedBox(w + 2 * t, ph, L - 0.12, 0.02, lime); K.uvBox(pier.geometry, 1.6);
            pier.position.set(0, ph / 2, zf - L / 2); pier.castShadow = pier.receiveShadow = true; g.add(pier);
          }
        }
        g.userData.keepOrigin = true;
        g.userData.rise = rise; g.userData.n = n; g.userData.riser = r; g.userData.landingZ = zf; g.userData.run = run;
        return g;
      }
    });

    /* A LANDING ON A PIER: a sawn limestone block `height` up with an aggregate slab on it, its front
     * edge on +z with a nosing. Origin at the footprint centre on the ground. */
    K.define("landing_pier", {
      size: [1.6, 3.0, 2.0],
      options: { height: 3.0, width: 1.5, depth: 2.0, dose: 0, seed: 1 },
      note: "A landing on a sawn limestone pier with an exposed aggregate slab top. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), h = o.height, sT = Math.min(0.16, h * 0.5);
        var pier = TXT.roundedBox(o.width, h - sT, o.depth - 0.1, 0.02, N.limeMat(K)); K.uvBox(pier.geometry, 1.6);
        pier.position.set(0, (h - sT) / 2, 0); pier.castShadow = pier.receiveShadow = true; g.add(pier);
        var slab = TXT.roundedBox(o.width + 0.1, sT, o.depth + 0.04, 0.014, N.aggMat(THREE, o.dose, o.seed)); K.uvBox(slab.geometry, 0.4);
        slab.position.set(0, h - sT / 2, 0.02); slab.castShadow = slab.receiveShadow = true; g.add(slab);
        g.userData.keepOrigin = true; g.userData.top = h;
        return g;
      }
    });

    /* A COURSED SAWN LIMESTONE WALL running along x, its face on +z, `height` tall, with a brass datum
     * strip set into the face at `datum` metres. Blocks are real geometry with joints, so the face has
     * the stone's own detail rather than a painted grid. */
    K.define("datum_wall", {
      size: [12, 5, 0.4],
      options: { length: 12, height: 5, datum: 4, thick: 0.4, course: 0.32, seed: 3, band: 0.12 },
      note: "Coursed sawn limestone wall with a brass datum strip inlaid at a given height. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), rnd = lcg(o.seed * 131 + 7);
        /* the wall stands behind the subject, so its stone is held darker than the stair's own */
        var wt = N.surfTex(THREE, "sawn", "#5e564a", 7), lime = new THREE.MeshStandardMaterial({ map: wt.map, bumpMap: wt.bump, bumpScale: 1.2, roughness: 0.9 });
        var rows = Math.ceil(o.height / o.course);
        var core = new THREE.Mesh(new THREE.BoxGeometry(o.length, o.height, o.thick - 0.04), K.mat("st_mortar", { color: 0x3a352e, roughness: 0.95 }));
        core.position.set(0, o.height / 2, -0.02); core.receiveShadow = true; g.add(core);
        var blocks = [];
        for (var j = 0; j < rows; j++) {
          var y0 = j * o.course, hh = Math.min(o.course, o.height - y0) - 0.012, x = -o.length / 2 - (j % 2) * 0.35;
          while (x < o.length / 2) {
            var bw = 0.55 + rnd() * 0.5, x1 = Math.min(o.length / 2, x + bw), x0 = Math.max(-o.length / 2, x);
            if (x1 - x0 > 0.05) {
              var bm = lime.clone(); bm.color = new THREE.Color().setScalar(0.8 + rnd() * 0.35);
              var b = TXT.roundedBox(x1 - x0 - 0.012, hh, 0.06, 0.012, bm);
              K.uvBox(b.geometry, 1.6);
              b.position.set((x0 + x1) / 2, y0 + hh / 2 + 0.006, o.thick / 2 - 0.02 + rnd() * 0.006);
              b.castShadow = b.receiveShadow = true; g.add(b); blocks.push(b);
            }
            x = x1;
          }
        }
        /* THE BRASS DATUM. Its lower edge is the datum, so the band rises from the line it marks and
         * never eats the distance under it (no. 57, frame 3). A metal carrying the accent in its own
         * glow, with a lit top bevel, and no second surface laid on its face: the coplanar accent
         * plane of the first build z-fought into a moire the critics read as a screen. */
        var bh = o.band, strip = TXT.roundedBox(o.length, bh, 0.05, Math.min(0.012, bh * 0.2), N.brassMat(THREE));
        strip.position.set(0, o.datum + bh / 2, o.thick / 2 + 0.035); strip.castShadow = true; g.add(strip);   /* 4 cm proud, so it casts a line */
        /* the lit top edge is drawn in the accent itself, outside the fog and the tone curve, because a
         * metal under dusk light alone fell to brown at 432 px and the deck lost its one colour */
        var lh = Math.max(0.02, bh * 0.35), lip = new THREE.Mesh(new THREE.BoxGeometry(o.length, lh, 0.036), N.accentMat(THREE));
        lip.position.set(0, o.datum + bh + lh / 2 - 0.002, o.thick / 2 + 0.035); g.add(lip);
        g.userData.keepOrigin = true; g.userData.datum = o.datum;
        return g;
      }
    });

    /* ONE LOOSE CAST TREAD lying flat, `length` the share of a full tread's width (a saw cut short) */
    K.define("tread_slab", {
      size: [1.4, 0.06, 0.32],
      options: { dose: 0, length: 1, width: 1.3, depth: 0.32, seed: 1, fresh: true },
      note: "One exposed aggregate tread lying flat, sawn short by a share of its length. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group(), L = o.width * o.length;
        var s = TXT.roundedBox(L, 0.06, o.depth, 0.012, N.aggMat(THREE, o.dose, o.seed)); K.uvBox(s.geometry, 0.4);
        s.position.set(0, 0.03, 0); s.castShadow = s.receiveShadow = true; g.add(s);
        if (o.length < 1) {
          /* the saw face: a paler, finer cut across the short end */
          var f = new THREE.Mesh(new THREE.PlaneGeometry(o.depth - 0.02, 0.05), K.mat("st_saw", { color: 0xc9bfa9, roughness: 0.7 }));
          f.rotation.y = Math.PI / 2; f.position.set(L / 2 + 0.0015, 0.03, 0); g.add(f);
        }
        g.userData.keepOrigin = true;
        return g;
      }
    });

    /* A CONCRETE PAD with a chalk outline on it and nothing else */
    K.define("chalk_pad", {
      size: [1.6, 0.05, 2.0],
      options: { width: 1.4, depth: 4.0, seed: 1 },
      note: "A poured concrete pad with a chalk outline of a stair's footprint and no stair. Drawn to illustrate.",
      make: function (o) {
        var g = new THREE.Group();
        var pad = TXT.roundedBox(o.width + 0.5, 0.05, o.depth + 0.5, 0.01, K.finish.concrete()); K.uvBox(pad.geometry, 3.0);
        pad.position.set(0, 0.025, 0); pad.receiveShadow = pad.castShadow = true; g.add(pad);
        var chalk = K.mat("st_chalk", { color: 0xe8e2d2, roughness: 0.95 }), cw = 0.07;
        [[0, -o.depth / 2, o.width, cw], [0, o.depth / 2, o.width, cw]].forEach(function (q) { var m = new THREE.Mesh(new THREE.BoxGeometry(q[2], 0.002, q[3]), chalk); m.position.set(q[0], 0.051, q[1]); g.add(m); });
        [[-o.width / 2, 0], [o.width / 2, 0]].forEach(function (q) { var m = new THREE.Mesh(new THREE.BoxGeometry(cw, 0.002, o.depth), chalk); m.position.set(q[0], 0.051, q[1]); g.add(m); });
        g.userData.keepOrigin = true;
        return g;
      }
    });
  };

  /* ---- placement and staging, the house furniture of the 2026-10-16 and 2026-10-21 chassis ---- */
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
    var rim = Object.assign({}, W.rig.rim, { i: (W.rig.rim.i || 0.8) * 0.3, color: 0xb9a48c });
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
    if (!R._bounce) { R._bounce = new N.T.HemisphereLight(0x1c1828, 0x7a5a3c, N.BOUNCE); R.scene.add(R._bounce); }
    return R;
  };
  N.BOUNCE = 1.1;
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
    u.setAttribute("stroke", "#08060F"); u.setAttribute("stroke-width", "5"); u.setAttribute("stroke-opacity", "0.6"); svg.appendChild(u);
    var l = document.createElementNS("http://www.w3.org/2000/svg", "line");
    l.setAttribute("x1", from[0]); l.setAttribute("y1", from[1]); l.setAttribute("x2", to[0]); l.setAttribute("y2", to[1]);
    l.setAttribute("stroke", N.INK); l.setAttribute("stroke-width", "2"); l.setAttribute("stroke-opacity", "0.85"); svg.appendChild(l);
    var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", to[0]); c.setAttribute("cy", to[1]); c.setAttribute("r", "5"); c.setAttribute("fill", N.INK); svg.appendChild(c);
  };
  N.CSS = function () {
    var ink = N.INK, dek = "#D8CFC0", halo = "rgba(4,3,8,0.6)", halo2 = "rgba(4,3,8,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#08060F; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:700; line-height:0.98; letter-spacing:0.004em; color:' + ink + '; font-variation-settings:"opsz" 144; word-spacing:0.05em; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; line-height:1.3; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".hook, .dek, .tx-site, .kick, .src, .count, .lab { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#D8CFC0" });
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

  /* ---- the relief bench: the tread's own surface at native size ---------------------------- */
  /* Linear albedo per material id, with tooth so no surface is a flat fill. The matrix stays dark so
   * under the low key only the pieces' lit edges and the glass's specular go bright. */
  N.M = { VOID: 0, MATRIX: 1, GLASS: 2, AMBER: 3, SLIVER: 4, BRASS: 5 };
  var BASE = {
    0: [0.006, 0.006, 0.008],
    1: [0.150, 0.125, 0.090],   /* buff cement, the cover's tread, held mid so the key warms it */
    2: [0.020, 0.060, 0.032],
    3: [0.120, 0.050, 0.012],
    4: [0.42, 0.39, 0.32],
    5: [0.55, 0.32, 0.15]
  };
  N.SPEC = { 1: [0.04, 6], 2: [2.6, 180], 3: [2.6, 180], 4: [0.04, 5], 5: [0.8, 40] };
  N.albedo = function (X, Y, m) {
    var b = BASE[m] || BASE[0], n = global.TX && TX.simplex2 ? TX.simplex2(X * 0.09, Y * 0.09) * 0.5 + TX.simplex2(X * 0.37, Y * 0.37) * 0.3 : 0;
    var k = 1 + (m === 1 ? 0.3 : (m === 4 ? 0.28 : 0.12)) * n;
    if (m === 1 && global.TX) { var sp = TX.simplex2(X * 1.9, Y * 1.9); k += sp > 0.6 ? 0.5 : (sp < -0.65 ? -0.35 : 0); }
    if (m === 4 && global.TX) { var sq = TX.simplex2(X * 1.3, Y * 1.3); k += sq > 0.55 ? 0.18 : (sq < -0.6 ? -0.15 : 0); }
    return [b[0] * k, b[1] * k, b[2] * k];
  };

  global.CH = N;
})(this);
