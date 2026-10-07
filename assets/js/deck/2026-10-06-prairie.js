/* deck/2026-10-06-prairie.js — the chassis for the 2026-10-06 deck: Taylor City Council votes on
 * October 8th on a proposed development agreement for Taylor Technology Campus, a 664 acre data center
 * and on site power project east of town, and the city published what applies WITH the agreement and
 * what applies WITHOUT it (tx-2026-0203).
 *
 * THE WORLD. The Blackland Prairie east of Taylor at the last of an October day.
 * goldenHour, tuned once here: the haze warmed toward Blackland field dust, the sun low in the west
 * south west over town, at az -78 and el 7. The far field fades into the horizon's bright band, and a
 * stake standing on it reads as a silhouette. The calm values for type are the clear sky high above
 * the band and the dark worked clay near the camera.
 *
 * DIRECTIONS. +x is east and -z is north, so +z is south. az runs clockwise from +z toward +x, so the
 * key sits at (sin az, ., cos az). The site's SOUTH property line, the one FM 112 runs beside, lies on
 * z = 0 and the campus is north of it (negative z). A house on FM 112 stands at positive z.
 *
 * THE HERO OBJECT. A pine SURVEY LATH, driven so that exactly 6 feet stands above grade,
 * the height the terms set for the berm (c33), with two tails of survey pink flagging. It is on all nine
 * frames and its STATE is the argument: driven in rows at the distances the terms write down, pulled,
 * at the line beside a meter, beside a person, buried flush in a berm's crest, drowned in the fill,
 * multiplied once per reported signature, and alone at the close. The kit had no lath; it is built below
 * in the kit's conventions.
 *
 * THE KIT MODEL THIS DECK BUILDS. `earthen_berm`, installed below in the kit's own conventions so
 * Phase 17 can lift it into assets/js/kit/landscape.js unchanged. The kit had no berm, and no survey lath (below).
 *
 * THE FIGURES A FRAME DRAWS are the claims' own, in the units the city wrote them (feet, acres,
 * gallons, dBA), written in the frame's code where figure_bearing.py checks them against
 * figures.json, and converted here by exact definitions (N.ft, N.acre, N.gal). The chassis types no
 * figure of the story.
 * The halls' size is the kit's illustrative massing and is never a claim: no frame argues what the
 * berm hides or how tall a hall is (out/2026-10-06/tmp/probe/NOTES.md).
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("prairie.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "prairie",
    light: { az: -78, el: 7 },
    sky: { preset: "goldenHour", haze: 0xc9b393 },
    ground: "#1E1A16",
    material: "#C4A47A",
    accent: "#E05A8F",
    grade: {
      exposure: 0.0,
      saturation: 1.03,
      contrast: 1.05,
      filmic: true,
      lift: [0.008, 0.007, 0.010],
      gain: [1.05, 1.0, 0.93],
      vignette: 0.2,
      bloom: { threshold: 0.82, strength: 0.14, radius: 14 },
      grain: { amount: 0.012, size: 2, seed: 20261006 },
      aberration: 0,
      dither: true,
      sharpen: 0.14
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261006;
  N.ACCENT = 0xe05a8f;
  /* the flagging's own colour, set so that after the grade's warm gain (1.05, 1.0, 0.93) it prints as
   * the accent: each channel of #E05A8F divided by its gain */
  N.FLAG = 0xd55a9a;
  N.INK = "#F3EFE6";

  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* EXACT UNIT DEFINITIONS, the same three compute.py states */
  N.ft = function (f) { return f * 0.3048; };
  N.acre = function (a) { return a * 4046.8564224; };
  N.gal = function (g) { return g * 0.003785411784; };

  /* SURVEY_LATH, the deck's hero, in the kit's conventions (metres, y up, origin on the ground at the
   * foot, front +z) so Phase 17 can lift it into assets/js/kit/ unchanged. A pine survey lath, 1.5 by
   * 0.375 inch stock (38 x 9.5 mm), chisel pointed, driven so that `above` metres stand above grade,
   * with the grade's dirt ring at its foot, a hub beside it (2 by 2 inch, driven flush, a tack in its
   * top) and two tails of flagging tape knotted near the top. The deck drives every lath so that
   * exactly the berm height the terms set stands above grade: the frame passes N.ft(6).
   * state: 'driven' (default), 'pulled' (lying on the ground, point and mud on its lower third),
   * 'bundle' (n lath strapped, lying), 'buried' (only `above` shows, no flagging).
   * flagging: true | false. lean: radians off vertical. wind: 0..1, how far the tails stream. */
  N.installLath = function (K, THREE, TXT) {
    if (K.registry.survey_lath) return;
    var M = null;
    N.lathMats = function () { return mats(); };
    function mats() {
      if (M) return M;
      var c = document.createElement("canvas"); c.width = 64; c.height = 512;
      var x = c.getContext("2d"), r = lcg(4417);
      x.fillStyle = "#cdb083"; x.fillRect(0, 0, 64, 512);
      for (var i = 0; i < 26; i++) { x.strokeStyle = "rgba(120,86,48," + (0.08 + r() * 0.14).toFixed(2) + ")"; x.lineWidth = 0.6 + r() * 1.6; x.beginPath(); var x0 = r() * 64; x.moveTo(x0, 0); x.bezierCurveTo(x0 + (r() - 0.5) * 14, 170, x0 + (r() - 0.5) * 14, 340, x0 + (r() - 0.5) * 10, 512); x.stroke(); }
      for (var k = 0; k < 2; k++) { var ky = 80 + r() * 380; x.fillStyle = "rgba(92,60,30,0.55)"; x.beginPath(); x.ellipse(20 + r() * 24, ky, 4, 7, 0, 0, 6.28); x.fill(); }
      var t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
      M = {
        pine: new THREE.MeshStandardMaterial({ color: 0xffffff, map: t, roughness: 0.82, metalness: 0 }),
        mud: new THREE.MeshStandardMaterial({ color: 0x2c2620, roughness: 0.95, metalness: 0 }),
        hub: new THREE.MeshStandardMaterial({ color: 0xb7996c, map: t, roughness: 0.86, metalness: 0 }),
        tack: new THREE.MeshStandardMaterial({ color: 0x8c8f92, roughness: 0.35, metalness: 0.9 }),
        flag: new THREE.MeshStandardMaterial({ color: N.FLAG, roughness: 0.55, metalness: 0, side: THREE.DoubleSide, emissive: N.FLAG, emissiveIntensity: 0.7 }),
        strap: new THREE.MeshStandardMaterial({ color: 0x1d1f22, roughness: 0.6, metalness: 0.1 })
      };
      return M;
    }
    var W = 0.0381, T = 0.0095, L = 1.2192 * 1.75;          /* 1.5 x 0.375 in, a 7 ft blank */
    function lathMesh(len, mud) {
      var g = new THREE.Group(), m = mats(), pt = 0.09;
      var body = new THREE.Mesh(new THREE.BoxGeometry(W, len - pt, T), m.pine); body.position.y = pt + (len - pt) / 2; g.add(body);
      var cg = new THREE.CylinderGeometry(W * 0.5, 0.002, pt, 4, 1); cg.rotateY(Math.PI / 4); cg.scale(1, 1, T / W);
      var point = new THREE.Mesh(cg, mud ? m.mud : m.pine); point.position.y = pt / 2; g.add(point);
      if (mud) { var md = new THREE.Mesh(new THREE.BoxGeometry(W * 1.08, mud, T * 1.3), m.mud); md.position.y = pt + mud / 2; g.add(md); }
      return g;
    }
    function flagging(g, top, wind, r, tail) {
      var m = mats();
      for (var i = 0; i < 2; i++) {
        var len = (0.38 + r() * 0.12) * (tail || 1), seg = 8, geo = new THREE.PlaneGeometry(0.03, len, 1, seg);
        var p = geo.attributes.position;
        for (var j = 0; j < p.count; j++) {
          var y = p.getY(j), t = (len / 2 - y) / len;      /* 0 at the knot, 1 at the tail */
          p.setX(j, p.getX(j) + (wind * 0.75 * t * len) * (i ? 1 : 0.85) + Math.sin(t * 7 + i * 2) * 0.03 * t);
          p.setZ(j, Math.sin(t * 5 + i) * 0.04 * t);
          p.setY(j, y - (1 - wind * 0.7) * 0.0);
        }
        geo.translate(0, -len / 2, 0); geo.computeVertexNormals();
        var f = new THREE.Mesh(geo, m.flag);
        f.rotation.z = -(0.25 + wind * 1.05) * (i ? 1.05 : 0.9); f.rotation.y = i ? 0.5 : -0.35;
        f.position.set(i ? 0.012 : -0.012, top - 0.06 - i * 0.025, T * 0.6);
        f.userData.accent = true;
        g.add(f);
      }
      var knot = new THREE.Mesh(new THREE.BoxGeometry(W * 1.15, 0.026, T * 1.6), m.flag); knot.position.y = top - 0.06; g.add(knot);
    }
    K.define("survey_lath", {
      size: [0.2, 1.83, 0.2],
      anchor: "base",
      options: { above: 1.8288, state: "driven", flagging: true, lean: 0, wind: 0.45, hub: true, n: 25 },
      note: "Pine survey lath 38 x 9.5 mm, chisel point, driven so `above` m stands above grade, a dirt ring at its foot, a hub with a tack beside it and two tails of flagging. state driven | pulled | bundle | buried.",
      make: function (o, r) {
        var g = new THREE.Group(), m = mats();
        if (o.state === "pulled") {
          var l = lathMesh(L, 0.32); l.rotation.z = Math.PI / 2; l.rotation.y = (r() - 0.5) * 0.6; l.position.set(-L / 2, T / 2 + 0.004, 0); g.add(l);
          return g;
        }
        if (o.state === "bundle") {
          for (var i = 0; i < o.n; i++) { var b = lathMesh(L, 0); b.rotation.z = Math.PI / 2; b.position.set(-L / 2 + (r() - 0.5) * 0.02, T / 2 + Math.floor(i / 5) * T * 1.05, (i % 5) * W * 1.04 - W * 2); g.add(b); }
          for (var s = 0; s < 2; s++) { var st = new THREE.Mesh(new THREE.BoxGeometry(0.016, T * 5.6 + 0.004, W * 5.3), m.strap); st.position.set(-L * (0.25 + s * 0.5), T * 2.6, 0); g.add(st); }
          return g;
        }
        var buried = L - o.above;
        var lt = lathMesh(L, o.state === "buried" ? 0 : 0); lt.position.y = -buried; g.add(lt);
        var ring = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.11, 0.035, 10), m.mud); ring.position.y = 0.012; g.add(ring);
        if (o.hub && o.state !== "buried") {
          var hb = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.03, 0.045), m.hub); hb.position.set(0.14, 0.012, 0.05); g.add(hb);
          var tk = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.006, 8), m.tack); tk.position.set(0.14, 0.03, 0.05); g.add(tk);
        }
        if (o.flagging && o.state !== "buried") flagging(g, o.above, o.wind, r, o.tail);
        g.rotation.z = o.lean;
        g.userData.top = o.above;
        return g;
      }
    });
  };

  /* ---------------------------------------------------------------- the kit model this deck lacks */
  /* EARTHEN_BERM, built in the kit's conventions so Phase 17 can lift it into assets/js/kit/landscape.js
   * unchanged: metres, y up, origin at the footprint centre on the ground, the berm running along x,
   * its front face toward +z. A landscaped screening berm as a Texas site plan draws one: a
   * trapezoid in section with a rounded crest, side slopes about 3 to 1, a turf skin that goes from
   * mown green on the faces to October straw on the crest, and a soft toe that sinks into the ground.
   * `height` is the crest above grade (the claim's "at least 6 feet" is 1.83 m), `crest` the flat top,
   * `slope` run per unit rise, `length` along x, `wobble` the plan curve, `swale` a shallow ditch on
   * the back side. userData.heightAt(x, z) gives the surface height so a tree or a stake can sit on it. */
  N.installBerm = function (K, THREE, TXT) {
    if (K.registry.earthen_berm) return;
    var bumpTex = null;
    function bump() {
      if (bumpTex) return bumpTex;
      var c = document.createElement("canvas"); c.width = c.height = 256;
      var x = c.getContext("2d"), r = lcg(6061), img = x.createImageData(256, 256);
      for (var i = 0; i < img.data.length; i += 4) { var v = 110 + r() * 90; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
      x.putImageData(img, 0, 0);
      x.globalAlpha = 0.5; x.filter = "blur(1px)"; x.drawImage(c, 0, 0);
      bumpTex = new THREE.CanvasTexture(c); bumpTex.wrapS = bumpTex.wrapT = THREE.RepeatWrapping;
      return bumpTex;
    }
    K.define("earthen_berm", {
      size: [60, 1.83, 14],
      options: { length: 60, height: 1.83, crest: 2.4, slope: 3, wobble: 0.6, swale: true, turf: "october" },
      note: "Landscaped earthen screening berm along x: trapezoid section with a rounded crest, about 3:1 side slopes, turf from green faces to straw crest, a soft toe into the ground. height is the crest above grade (1.83 m is 6 ft). userData.heightAt(x, z) is the surface height.",
      make: function (o, r) {
        var L = o.length, H = o.height, cw = o.crest / 2, run = H * o.slope, half = cw + run;
        var nx = Math.max(24, Math.round(L / 1.5)), nz = 28;
        var g = new THREE.Group();
        var geo = new THREE.PlaneGeometry(L, half * 2 + 4, nx, nz); geo.rotateX(-Math.PI / 2);
        var p = geo.attributes.position, col = new Float32Array(p.count * 3);
        var ph1 = r() * 6.28, ph2 = r() * 6.28;
        function bend(x) { return o.wobble * Math.sin(x / L * 6.28 * 1.3 + ph1) + 0.35 * o.wobble * Math.sin(x / L * 6.28 * 3.1 + ph2); }
        function prof(d) {           /* height at distance d from the centre line */
          var a = Math.abs(d);
          if (a <= cw) return H - 0.06 * (a / Math.max(cw, 0.01)) * (a / Math.max(cw, 0.01));
          if (a >= half + 1.2) return o.swale && d < 0 && a < half + 2.0 ? -0.12 * Math.sin((a - half - 1.2) / 0.8 * Math.PI) : 0;
          var t = Math.min(1, (a - cw) / (run + 1.2));
          var s = t * t * (3 - 2 * t);              /* soft shoulder and soft toe */
          return (H - 0.06) * (1 - s);
        }
        function heightAt(x, z) { return Math.max(0, prof(z - bend(x)) * (1 + 0.04 * Math.sin(x * 0.31 + ph2))); }
        var cGreen = new THREE.Color(0x5d6b34), cStraw = new THREE.Color(0xa3925c), cSoil = new THREE.Color(0x6b5a44), tmp = new THREE.Color();
        for (var i = 0; i < p.count; i++) {
          var x = p.getX(i), z = p.getZ(i), y = heightAt(x, z);
          p.setY(i, y);
          var k = Math.min(1, y / H), n = (Math.sin(x * 1.7 + z * 2.3) + Math.sin(x * 0.53 - z * 1.1)) * 0.25 + (r() - 0.5) * 0.3;
          tmp.copy(cGreen).lerp(cStraw, Math.min(1, Math.max(0, 0.25 + k * 0.6 + n * 0.5)));
          if (y < 0.05) tmp.lerp(cSoil, 0.25);
          col[i * 3] = tmp.r; col[i * 3 + 1] = tmp.g; col[i * 3 + 2] = tmp.b;
        }
        geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
        geo.computeVertexNormals();
        var bt = bump().clone(); bt.needsUpdate = true; bt.repeat.set(L / 3, (half * 2 + 4) / 3);
        var mat = new THREE.MeshStandardMaterial({ color: 0xffffff, vertexColors: true, roughness: 0.96, metalness: 0, bumpMap: bt, bumpScale: 0.6 });
        var m = new THREE.Mesh(geo, mat); m.receiveShadow = true; m.castShadow = true;
        g.add(m);
        g.userData.heightAt = heightAt;
        g.userData.berm = { length: L, height: H, base: half * 2 };
        return g;
      }
    });
  };


  /* SOUND_LEVEL_METER, in the kit's conventions: a Class 1 sound level meter on a survey tripod, the
   * microphone in a grey foam windscreen at `height` (1.5 m is the usual measuring height), three
   * aluminium legs with steel shoes, a dark ABS body below the mic with no display text. */
  N.installMeter = function (K, THREE, TXT) {
    if (K.registry.sound_level_meter) return;
    K.define("sound_level_meter", {
      size: [1.0, 1.55, 1.0], anchor: "base",
      options: { height: 1.5, spread: 0.42 },
      note: "Class 1 sound level meter on a survey tripod, foam windscreen at height, no display text.",
      make: function (o, r) {
        var g = new THREE.Group();
        var al = new THREE.MeshStandardMaterial({ color: 0xb9bdc0, roughness: 0.38, metalness: 0.85 });
        var steel = new THREE.MeshStandardMaterial({ color: 0x3a3c3e, roughness: 0.5, metalness: 0.8 });
        var abs = new THREE.MeshStandardMaterial({ color: 0x24272a, roughness: 0.55, metalness: 0.05 });
        var foam = new THREE.MeshStandardMaterial({ color: 0x6f7173, roughness: 1.0, metalness: 0 });
        var head = o.height - 0.36;
        for (var i = 0; i < 3; i++) {
          var a = i * 2.094 + 0.3, fx = Math.sin(a) * o.spread, fz = Math.cos(a) * o.spread;
          K.bar([fx, 0.02, fz], [0, head, 0], 0.011, al, 8, g);
          K.bar([fx * 0.55, 0.32 * head, fz * 0.55], [0, 0.42 * head, 0], 0.005, steel, 6, g);
          var shoe = new THREE.Mesh(new THREE.ConeGeometry(0.012, 0.06, 8), steel); shoe.rotation.x = Math.PI; shoe.position.set(fx, 0.03, fz); g.add(shoe);
        }
        var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.05, 0.05, 16), steel); hub.position.y = head; g.add(hub);
        var col = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.12, 10), steel); col.position.y = head + 0.08; g.add(col);
        var body = TXT.roundedBox(0.075, 0.27, 0.04, 0.012, abs); body.position.y = head + 0.27; g.add(body);
        var neck = new THREE.Mesh(new THREE.CylinderGeometry(0.0065, 0.009, 0.06, 12), steel); neck.position.y = head + 0.43; g.add(neck);
        var ball = new THREE.Mesh(new THREE.SphereGeometry(0.045, 24, 18), foam); ball.position.y = o.height; g.add(ball);
        g.userData.mic = o.height;
        return g;
      }
    });
  };

  /* FILL_BASIN, a square basin cut `depth` metres into grade with banks at `slope` run per unit rise,
   * filled to just under grade, sized so its water holds `volume` cubic metres. The waterline side is
   * SOLVED here from the frustum's volume, V = h/3 (A1 + A2 + sqrt(A1 A2)), by bisection, so a frame
   * passes the volume and never a side. The water is a reflective plane that carries the sky; the
   * banks show only as a damp lip, because a basin full to grade hides its own sides. */
  N.basinSide = function (volume, depth, slope) {
    function vol(a) { var b = a - 2 * slope * depth; if (b <= 0) return 0; return depth / 3 * (a * a + b * b + a * b); }
    var lo = 2 * slope * depth, hi = 1000;
    for (var i = 0; i < 80; i++) { var m = (lo + hi) / 2; if (vol(m) < volume) lo = m; else hi = m; }
    return (lo + hi) / 2;
  };
  N.installBasin = function (K, THREE, TXT) {
    if (K.registry.fill_basin) return;
    K.define("fill_basin", {
      size: [57, 0.05, 57],
      options: { volume: 5962, depth: 1.8288, slope: 2, lip: 1.4, water: 0x1c2628 },
      note: "Square basin cut into grade, filled to grade, waterline side solved from volume, depth and bank slope.",
      make: function (o, r) {
        var g = new THREE.Group(), a = N.basinSide(o.volume, o.depth, o.slope);
        var rc = document.createElement("canvas"); rc.width = rc.height = 256; var rx = rc.getContext("2d"), rr = lcg(818), img = rx.createImageData(256, 256);
        for (var py = 0; py < 256; py++) for (var px = 0; px < 256; px++) { var k = (py * 256 + px) * 4, u = px / 256 * 6.2832, v = py / 256 * 6.2832, wv = (Math.sin(u * 9 + Math.sin(v * 3) * 2.2) * 0.5 + Math.sin(v * 13 + u * 2) * 0.35) * (0.55 + 0.45 * Math.sin(u * 2 + v * 3 + 1.3)) + Math.sin(u * 5 - v * 7) * 0.22 + (rr() - 0.5) * 0.4;
          /* every frequency a whole number of cycles across the tile, so the repeat carries no seam */
          img.data[k] = 128 + wv * 38; img.data[k + 1] = 128 + Math.cos(v * 11 + u * 2) * 30; img.data[k + 2] = 255; img.data[k + 3] = 255; }
        rx.putImageData(img, 0, 0); var nt = new THREE.CanvasTexture(rc); nt.wrapS = nt.wrapT = THREE.RepeatWrapping; nt.repeat.set(a / 7, a / 7);
        var water = new THREE.Mesh(new THREE.PlaneGeometry(a, a, 1, 1), new THREE.MeshPhysicalMaterial({ color: o.water, roughness: 0.06, metalness: 0.0, clearcoat: 1.0, clearcoatRoughness: 0.04, ior: 1.33, envMapIntensity: 1.25, normalMap: nt, normalScale: new THREE.Vector2(0.17, 0.17) }));
        water.rotation.x = -Math.PI / 2; water.position.y = 0.02; water.receiveShadow = true; water.userData.txWear = false; water.userData.noShadow = false;
        g.add(water);
        var damp = new THREE.MeshStandardMaterial({ color: 0x5a4838, roughness: 0.8, metalness: 0 });
        var L = o.lip;
        [[0, -(a + L) / 2, a + 2 * L, L], [0, (a + L) / 2, a + 2 * L, L], [-(a + L) / 2, 0, L, a], [(a + L) / 2, 0, L, a]].forEach(function (s) {
          var m = new THREE.Mesh(new THREE.PlaneGeometry(s[2], s[3]), damp); m.rotation.x = -Math.PI / 2; m.position.set(s[0], 0.012, s[1]); m.receiveShadow = true; g.add(m);
        });
        g.userData.side = a; g.userData.keepOrigin = true;
        return g;
      }
    });
  };

  /* N.lathField(K, THREE, list, o) stands a field of survey lath as two instanced meshes, the pine and
   * the flagging, one instance per [x, z] in `list`, every lath with `above` metres above grade. Built
   * from the kit lath's own materials and dimensions, so a field of 1,400 is the same object as the
   * one at the close, at a cost a frame can render. */
  N.lathField = function (K, THREE, list, o) {
    o = o || {};
    var above = o.above, sample = K.make("survey_lath", { above: above, seed: 9 }), pine = null, flag = null;
    sample.traverse(function (m) { if (m.isMesh && m.material && m.material.map && !pine) pine = m.material; if (m.isMesh && m.userData.accent && !flag) flag = m.material; });
    var g = new THREE.Group(), n = list.length, r = lcg(o.seed || 77);
    var bodyG = new THREE.BoxGeometry(0.0381, above, 0.0095); bodyG.translate(0, above / 2, 0);
    var flagG = new THREE.PlaneGeometry(0.03, 0.42, 1, 4); flagG.translate(0.0, -0.21, 0);
    var body = new THREE.InstancedMesh(bodyG, pine, n), tails = new THREE.InstancedMesh(flagG, flag, n * 2);
    var M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler(), S = new THREE.Vector3(1, 1, 1), P = new THREE.Vector3();
    for (var i = 0; i < n; i++) {
      var x = list[i][0], z = list[i][1], lean = (r() - 0.5) * 0.02;
      E.set(lean, r() * 3.1416, (r() - 0.5) * 0.02); Q.setFromEuler(E); P.set(x, 0, z); M4.compose(P, Q, S); body.setMatrixAt(i, M4);
      for (var k = 0; k < 2; k++) {
        E.set(0.2 * (r() - 0.5), -0.3 + k * 0.6, -(0.7 + (o.wind || 0.5) * 0.7) * (k ? 1.05 : 0.9)); Q.setFromEuler(E);
        P.set(x + (k ? 0.012 : -0.012), above - 0.06 - k * 0.025, z); M4.compose(P, Q, S); tails.setMatrixAt(i * 2 + k, M4);
      }
    }
    body.castShadow = true; body.receiveShadow = true; tails.castShadow = true;
    g.add(body); g.add(tails);
    g.userData.count = n;
    return g;
  };


  /* N.project puts a world point on the frame in CSS px, for a DOM label or a leader's end */
  N.project = function (THREE, R, p) {
    var v = new THREE.Vector3(p[0], p[1], p[2]); R.camera.updateMatrixWorld(); v.project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  N.unshadow = function (scene) { scene.traverse(function (m) { if (m.isMesh && m.userData.noShadow) { m.receiveShadow = false; m.castShadow = false; } }); };


  /* ---------------------------------------------------------------- the place, as primitives */
  /* The world's own furniture, which every exterior frame stands in: worked Houston Black clay, its
   * clods, October stubble, the south line's barbed wire, and the creek's tree line on the horizon.
   * Each is a primitive a frame places where its own composition wants it. None draws a frame. */
  N.CLAY = 0x6a5846;
  /* the bench the frame staged, remembered once by N.stage and N.boot so a primitive needs no plumbing */
  N.put = function (obj, contact) { N.TXT.add(N.R, obj); if (contact) N.TXT.contact(N.R, obj, contact === true ? undefined : contact); return obj; };
  N.clods = function (area, o) { o = o || {}; return N.TXT.scatter(N.R, { kind: "rock", count: o.count || 2400, area: area, seed: o.seed || 7, scale: o.scale || [0.025, 0.07], colors: [0x2c2620, 0x352d26, 0x40362c] }); };
  N.stubble = function (area, o) { o = o || {}; return N.TXT.scatter(N.R, { kind: "grass", count: o.count || 9000, area: area, avoid: o.avoid, seed: o.seed || 8, scale: o.scale || [0.12, 0.26], colors: [0xb3a27e, 0x9a8a66, 0x7d7656] }); };
  N.fenceLine = function (o) {
    o = o || {}; var out = [];
    (o.xs || [-210, 0, 210]).forEach(function (x, i) { var f = N.K.make("barbed_wire_fence", { length: o.length || 210, strands: 4, seed: (o.seed || 4) + i * 7 }); f.position.set(x, 0, o.z || 0); N.put(f); out.push(f); });
    return out;
  };
  N.treeLine = function (o) {
    o = o || {}; var n = o.n || 26, out = [];
    for (var i = 0; i < n; i++) {
      var t = N.K.make(i % (o.oakEvery || 3) ? "cedar_elm" : "live_oak", { seed: (o.seed || 40) + i, height: (o.height || 9) + (i * 7) % 5, spread: 11 + (i * 5) % 6 });
      t.position.set((o.x0 || -420) + i * (o.step || 34) + ((i * 17) % 13), 0, (o.z || -1150) - ((i * 29) % (o.jitter || 70)));
      N.put(t); out.push(t);
    }
    return out;
  };

  /* N.drape lifts every instance of a scatter onto a surface, `hAt(x, z)` metres above grade, so turf
   * tufts stand on a berm's face instead of buried inside it */
  N.drape = function (obj, hAt) {
    var T = N.T, M = new T.Matrix4(), P = new T.Vector3(), Q = new T.Quaternion(), S = new T.Vector3();
    obj.traverse(function (m) {
      if (!m.isInstancedMesh) return;
      for (var i = 0; i < m.count; i++) { m.getMatrixAt(i, M); M.decompose(P, Q, S); P.y += hAt(P.x, P.z); M.compose(P, Q, S); m.setMatrixAt(i, M); }
      m.instanceMatrix.needsUpdate = true; if (m.computeBoundingSphere) m.computeBoundingSphere();
    });
    return obj;
  };

  /* N.raked lays a raked strip of bare clay, lighter than the worked field around it, the way a staking
   * crew rakes the stubble off a line before it drives lath. [x0, z0, x1, z1] in metres. */
  N.raked = function (area, o) {
    o = o || {}; var T = N.T, w = Math.abs(area[2] - area[0]), d = Math.abs(area[3] - area[1]);
    var g = new T.PlaneGeometry(w, d, Math.max(1, Math.round(w / 4)), Math.max(1, Math.round(d / 4))), p = g.attributes.position, r = lcg(o.seed || 5);
    for (var i = 0; i < p.count; i++) p.setZ(i, (r() - 0.5) * 0.03);
    g.computeVertexNormals();
    var m = new T.Mesh(g, new T.MeshStandardMaterial({ color: o.color || 0x8c7a62, roughness: 1, metalness: 0 }));
    m.rotation.x = -Math.PI / 2; m.position.set((area[0] + area[2]) / 2, 0.012, (area[1] + area[3]) / 2);
    m.receiveShadow = true; m.userData.txWear = false;
    return m;
  };

  /* N.furrows lays a disked field's ridges, running north and south so the low west sun lights one
   * face of each and shades the other, and they converge toward the horizon like a real worked field.
   * One instanced prism, `pitch` metres apart, from x0 to x1, z0 to z1. */
  N.furrows = function (o) {
    o = o || {}; var T = N.T, pitch = o.pitch || 1.0, x0 = o.x0 == null ? -300 : o.x0, x1 = o.x1 == null ? 300 : o.x1;
    var z0 = o.z0 == null ? -2 : o.z0, z1 = o.z1 == null ? -600 : o.z1, len = Math.abs(z1 - z0), h = o.height || 0.13, w = o.width || 0.62;
    var shape = new T.Shape(); shape.moveTo(-w / 2, 0); shape.quadraticCurveTo(-w * 0.18, h * 1.05, 0, h); shape.quadraticCurveTo(w * 0.18, h * 1.05, w / 2, 0); shape.lineTo(-w / 2, 0);
    var geo = new T.ExtrudeGeometry(shape, { depth: 1, bevelEnabled: false, steps: 1, curveSegments: 4 });
    var mat = new T.MeshStandardMaterial({ color: o.color || 0x5f4f3f, roughness: 0.97, metalness: 0 });
    var n = Math.floor((x1 - x0) / pitch), mesh = new T.InstancedMesh(geo, mat, n), M4 = new T.Matrix4(), r = lcg(o.seed || 31);
    for (var i = 0; i < n; i++) {
      var x = x0 + i * pitch + (r() - 0.5) * pitch * 0.12, sh = 0.75 + r() * 0.5;
      M4.makeScale(1, sh, len); M4.setPosition(x, -0.02, Math.min(z0, z1));
      mesh.setMatrixAt(i, M4);
    }
    mesh.castShadow = true; mesh.receiveShadow = true; mesh.userData.txWear = false;
    return mesh;
  };

  /* N.flagStrength scales the flagging's own light for a frame exposed away from the deck's, so the
   * pink lands on the accent after the tone curve rather than drifting with the exposure */
  N.flagStrength = function (k) { var m = N.lathMats(); m.flag.emissiveIntensity = 0.7 * k; };
  N.rig = function (W, o) { return [N.rigSpec(W, o.size, 4096), N.rigOpts(o.target, { distance: o.distance, shadowFar: o.far })]; };
  N.installAll = function () { N.installLath(N.K, N.T, N.TXT); N.installBerm(N.K, N.T, N.TXT); N.installMeter(N.K, N.T, N.TXT); N.installBasin(N.K, N.T, N.TXT); };

  /* ---------------------------------------------------------------- the rig and the stage */
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 60, mapSize: map || 2048 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 120, shadowFar: o.shadowFar || 320, normalBias: o.normalBias == null ? 0.02 : o.normalBias };
  };
  /* THE DECK'S EXPOSURE, ONE NUMBER FOR ALL NINE, so the frames sit in one value band. Tuned on the
   * probe frame. */
  N.EXPOSURE = 1.0;
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    N.R = TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * N.EXPOSURE * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 34, near: o.near || 0.05, far: o.far || 12000 });
    return N.R;
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
    N.deband(cx);
    return cx;
  };
  /* N.deband. The GPU frame arrives in 8 bits, and a low sun's sky steps one level at a time into
   * rings the grade then sharpens. Where a pixel sits within `tol` levels of its neighbourhood mean
   * it is a smooth gradient, so it takes that mean plus a triangular dither. Anything with an edge,
   * a stake, a wire, a letter, differs from its mean by more and is left exactly as rendered. */
  N.deband = function (cx, o) {
    o = o || {}; var c = cx.canvas, w = c.width, h = c.height, rad = o.radius || 44, tol = o.tol || 2.8;
    var id = cx.getImageData(0, 0, w, h), d = id.data, n = w * h, a = new Float32Array(n), b = new Float32Array(n), s = 7654321;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var ch = 0; ch < 3; ch++) {
      for (var i = 0; i < n; i++) a[i] = d[i * 4 + ch];
      for (var y = 0; y < h; y++) { var row = y * w, acc = 0, cnt = 0;
        for (var x = -rad; x < w; x++) { if (x + rad < w) { acc += a[row + x + rad]; cnt++; } if (x - rad - 1 >= 0) { acc -= a[row + x - rad - 1]; cnt--; } if (x >= 0) b[row + x] = acc / cnt; } }
      for (var x2 = 0; x2 < w; x2++) { var acc2 = 0, cnt2 = 0;
        for (var y2 = -rad; y2 < h; y2++) { if (y2 + rad < h) { acc2 += b[(y2 + rad) * w + x2]; cnt2++; } if (y2 - rad - 1 >= 0) { acc2 -= b[(y2 - rad - 1) * w + x2]; cnt2--; } if (y2 >= 0) a[y2 * w + x2] = acc2 / cnt2; } }
      for (var j = 0; j < n; j++) { var v = d[j * 4 + ch], m = a[j]; if (Math.abs(v - m) < tol) d[j * 4 + ch] = m + (rnd() + rnd() - 1) * 1.6; }
    }
    cx.putImageData(id, 0, 0);
  };

  /* ---------------------------------------------------------------- the type's quiet */
  /* THE SKY BAND THE TYPE STANDS IN. Light type on a blue sky, so the band is a dark wash that
   * deepens the sky behind the hook and the dek, never over 0.45 alpha. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 60 : o.pad;
    var a = o.a == null ? 0.26 : Math.min(0.45, o.a), c = o.rgb || "16,14,22";
    if (bottom != null && a > 0) {
      var fade = o.fade || 170, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + a + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + (a * 0.9) + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  N.shade = function (cx, selectors, o) {
    o = o || {};
    var art = document.getElementById("art"), pad = o.pad == null ? 16 : o.pad;
    var mask = document.createElement("canvas"); mask.width = art.width; mask.height = art.height;
    var mx = mask.getContext("2d"); mx.filter = "blur(" + (o.feather || 40) + "px)"; mx.fillStyle = "rgb(14,10,8)";
    (selectors || []).forEach(function (sel) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
        var r = el.getBoundingClientRect(); mx.fillRect((r.left - pad) * 2, (r.top - pad) * 2, (r.width + 2 * pad) * 2, (r.height + 2 * pad) * 2);
      });
    });
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.globalAlpha = Math.min(0.35, o.alpha || 0.2); cx.drawImage(mask, 0, 0); cx.restore();
  };
  N.soften = function (cx, selectors, o) {
    o = o || {};
    var blur = o.blur || 10, pad = o.pad == null ? 16 : o.pad, feather = o.feather || 60;
    var art = document.getElementById("art");
    var src = document.createElement("canvas"); src.width = art.width; src.height = art.height;
    var sx = src.getContext("2d"); sx.filter = "blur(" + (blur * 2) + "px)"; sx.drawImage(art, 0, 0);
    var mask = document.createElement("canvas"); mask.width = art.width; mask.height = art.height;
    var mx = mask.getContext("2d"); mx.filter = "blur(" + feather + "px)"; mx.fillStyle = "#000";
    (selectors || []).forEach(function (sel) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
        var r = el.getBoundingClientRect();
        mx.fillRect((r.left - pad) * 2, (r.top - pad) * 2, (r.width + 2 * pad) * 2, (r.height + 2 * pad) * 2);
      });
    });
    sx.filter = "none"; sx.globalCompositeOperation = "destination-in"; sx.drawImage(mask, 0, 0);
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.drawImage(src, 0, 0); cx.restore();
  };
  /* THE POST STEPS every frame takes before its grade. The frame still calls TXDECK.finish itself,
   * last. A dark band under the footer, never a box and never over 0.45. */
  N.post = function (cx, o) {
    o = o || {};
    /* the fonts have landed by now, so fit the hook again and set the dek under it before anything
     * measures the type: a hook laid out in the fallback face wraps where the real face doesn't */
    TX.fitText(document.getElementById("hook"), N.fit || { min: 92, max: 128, maxLines: 2 }); N.follow();
    N.atmosphere(cx, { a: o.a, to: o.to, fade: o.fade, rgb: o.rgb, pad: o.pad });
    N.soften(cx, o.type || [".kick", ".hook", ".dek"], { blur: o.typeBlur || 16, pad: 12, feather: o.typeFeather || 30 });
    N.soften(cx, [".tx-site", ".src", ".count"], { blur: o.siteBlur || 14, pad: 16, feather: 60 });
    /* where a kicker lands on the brightest haze of the day, a feathered shade behind the furniture
     * alone, never a plate: no edge survives the feather */
    if (o.shade) N.shade(cx, [".kick", ".count"], { alpha: o.shade, pad: 8, feather: 26 });
    var y0 = N.H - (o.veilH || 240), v = cx.createLinearGradient(0, y0, 0, N.H), rgb = o.veilRgb || "14,10,8";
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(" + rgb + "," + (Math.min(0.45, o.veil == null ? 0.4 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 1.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };

  /* ---------------------------------------------------------------- the shell */
  /* THE SHELL EVERY FRAME SHARES: the type styles, the furniture, the fit of the hook. Light type on
   * a blue hour sky, with a dark halo rather than a plate. */
  N.CSS = function () {
    var ink = N.INK, dek = "#E6E3DC", halo = "rgba(14,10,8,0.6)", halo2 = "rgba(14,10,8,0.45)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#1E1A16; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; text-wrap:balance; font-family:"Fraunces", serif; font-weight:700; line-height:1.0; letter-spacing:-0.01em; color:' + ink + '; font-variation-settings:"opsz" 144; z-index:10; }',
      ".dek { position:absolute; left:82px; width:840px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:25px; font-weight:500; letter-spacing:0.06em; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".hook, .dek, .tx-site, .kick, .src, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 14px " + halo2 + "; }"
    ].join("\n");
  };
  N.follow = function () {
    var h = document.getElementById("hook");
    Array.prototype.forEach.call(document.querySelectorAll(".dek[data-follow]"), function (d) {
      d.style.top = (h.offsetTop + h.getBoundingClientRect().height + (+d.dataset.follow)) + "px";
    });
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS();
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: "#F3EFE6" });
    N.fit = o.fit; TX.fitText(document.getElementById("hook"), o.fit || { min: 92, max: 128, maxLines: 2 });
    N.follow();
  };
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE;
    await document.fonts.ready;
    N.start(o);
    var TXT = typeof bench === "function" ? bench(THREE) : bench, K = initKit(THREE, TXT);
    N.TXT = TXT; N.K = K;
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
  };

  global.TT = N;
})(this);
