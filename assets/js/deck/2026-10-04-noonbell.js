/* deck/2026-10-04-noonbell.js — the chassis for the 2026-10-04 deck: emails obtained by The Texas
 * Tribune and ProPublica show Texas Education Agency staff helped connect Alpha School's AI learning
 * platform, now often called TimeBack, with public school districts, and Houston, Fort Davis and
 * Aldine launched pilots (tx-2026-0200).
 *
 * THE WORLD. A Texas school day at noon: highNoon, tuned once here. The sky is bleached toward a
 * pale caliche horizon and the haze carries a little dust, so a campus a few hundred metres off
 * goes soft the way a West Texas noon does. Shadows are short and black. The calm value for type
 * is the pale sky above the roofline, and type is dark.
 *
 * DIRECTIONS. +x is east and -z is north, so +z is south. The light is declared at az 10, el 58:
 * the sun high in the south, a touch west of the meridian. az runs clockwise from +z toward +x,
 * so the key sits at (sin 10, ., cos 10). A building whose face looks south (+z) is lit full on
 * and its shadow falls short behind it to the north. A camera looking north sees sunlit faces.
 *
 * THE HERO OBJECT. One school wall clock, `school_clock`, a kit addition below: 0.36 m across, a
 * black moulded case with a domed lens, a white face with minute ticks and twelve hour bars and no
 * numerals, black hands, and the deck's figure drawn on the face: a sector two hours wide in the
 * accent, the hours Alpha's full model gives the AI to teach basic subjects each day (c34). It is
 * the same clock on every frame. The frame sets the time on its hands and whether the sector shows.
 * On a campus facade the same clock is mounted large over the entry in a cast stone surround.
 *
 * THE ACCENT. #C2477A, "the two hour block": only ever the sector on the clock's face, and the
 * units a count frame marks as a pilot. Never a sky, a building, a person's clothing or a light.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the kit
 * additions and the deck's materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("noonbell.js needs txdeck.js loaded first");

  TXDECK.declare({
    world: "noonbell",
    light: { az: 10, el: 58 },
    sky: { preset: "highNoon", horizon: 0xdfe3e0, haze: 0xe6e2d6, fogDensity: 0.0022, clouds: 0.3 },
    ground: "#E7E3DA",
    material: "#C49460",
    accent: "#C2477A",
    grade: {
      exposure: -0.06,
      saturation: 1.03,
      contrast: 1.07,
      filmic: true,
      lift: [0.004, 0.004, 0.006],
      gain: [1.005, 1.0, 0.99],
      vignette: 0.16,
      bloom: { threshold: 0.88, strength: 0.14, radius: 12 },
      grain: { amount: 0.011, size: 2, seed: 20261004 },
      aberration: 0,
      dither: true,
      sharpen: 0.16
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20261004;
  N.ACCENT = 0xc2477a;
  N.INK = "#15171C";

  /* ---------------------------------------------------------------- textures */
  N.tex = {};
  function canvasTex(THREE, name, w, h, draw, rep) {
    if (N.tex[name]) return N.tex[name];
    var c = document.createElement("canvas"); c.width = w; c.height = h;
    draw(c.getContext("2d"), w, h);
    var t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    if (rep) t.repeat.set(rep[0], rep[1]);
    N.tex[name] = t; return t;
  }
  function lcg(seed) { var s = seed >>> 0 || 1; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  N.lcg = lcg;

  /* the clock's face: a warm white with the faint tooth of printed card, a soft grey ring where
   * the lens meets the case, and a little dust settled toward the bottom. No numerals: a figure
   * here is drawn, never typed into a texture. */
  N.faceTex = function (THREE) {
    return canvasTex(THREE, "face", 512, 512, function (x, w, h) {
      var r = lcg(404);
      x.fillStyle = "#f3f1ea"; x.fillRect(0, 0, w, h);
      for (var i = 0; i < 5000; i++) { x.fillStyle = r() < 0.5 ? "rgba(255,255,255,0.18)" : "rgba(120,110,95,0.07)"; x.fillRect(r() * w, r() * h, 1, 1); }
      var g = x.createRadialGradient(w / 2, h / 2, w * 0.36, w / 2, h / 2, w * 0.5);
      g.addColorStop(0, "rgba(90,90,90,0)"); g.addColorStop(1, "rgba(70,68,64,0.22)");
      x.fillStyle = g; x.fillRect(0, 0, w, h);
      var d = x.createLinearGradient(0, h * 0.55, 0, h);
      d.addColorStop(0, "rgba(140,128,104,0)"); d.addColorStop(1, "rgba(140,128,104,0.12)");
      x.fillStyle = d; x.fillRect(0, 0, w, h);
    }, [1, 1]);
  };
  /* steel locker paint, baked enamel with scuffs at knee height and a dark seam every door */
  N.lockerTex = function (THREE) {
    return canvasTex(THREE, "locker", 256, 512, function (x, w, h) {
      var r = lcg(77);
      x.fillStyle = "#8d969c"; x.fillRect(0, 0, w, h);
      for (var i = 0; i < 1600; i++) { x.fillStyle = r() < 0.5 ? "rgba(255,255,255,0.05)" : "rgba(30,34,38,0.06)"; x.fillRect(r() * w, r() * h, 1 + r() * 2, 1); }
      for (var s = 0; s < 40; s++) { x.strokeStyle = "rgba(40,42,44," + (0.06 + r() * 0.12) + ")"; x.lineWidth = 1 + r() * 2; var y = h * (0.62 + r() * 0.3), xx = r() * w; x.beginPath(); x.moveTo(xx, y); x.lineTo(xx + 10 + r() * 40, y + (r() - 0.5) * 6); x.stroke(); }
    }, [1, 1]);
  };

  /* ---------------------------------------------------------------- materials */
  N.mats = function (K, THREE, TXT) {
    if (N._m) return N._m;
    N._m = {
      caseBlack: K.mat("nb-case", { color: 0x17181a, roughness: 0.42, metalness: 0.1 }),
      caseRim: K.mat("nb-rim", { color: 0x2a2c2f, roughness: 0.3, metalness: 0.55 }),
      face: K.mat("nb-face", { color: 0xffffff, roughness: 0.62, metalness: 0, map: N.faceTex(THREE) }),
      ink: K.mat("nb-ink", { color: 0x121314, roughness: 0.5, metalness: 0.05 }),
      hub: K.mat("nb-hub", { color: 0x0d0d0e, roughness: 0.3, metalness: 0.6 }),
      sector: K.mat("nb-sector", { color: 0xc2477a, roughness: 0.55, metalness: 0, emissive: 0x6a1838, emissiveIntensity: 0.35 }),
      lens: K.mat("nb-lens", { color: 0xffffff, roughness: 0.04, metalness: 0, transparent: true, opacity: 0.12 }, true),
      castStone: K.mat("nb-cast", { color: 0xddd3bd, roughness: 0.88, metalness: 0 }),
      locker: K.mat("nb-locker", { color: 0xffffff, roughness: 0.48, metalness: 0.45, map: N.lockerTex(THREE) }),
      lockerDark: K.mat("nb-lockerin", { color: 0x2a2d30, roughness: 0.8, metalness: 0.2 }),
      lockerAccent: K.mat("nb-lockeracc", { color: 0xc2477a, roughness: 0.5, metalness: 0.3, emissive: 0x5a1430, emissiveIntensity: 0.25 }),
      base: K.mat("nb-base", { color: 0x2c2e30, roughness: 0.7, metalness: 0.1 })
    };
    return N._m;
  };

  /* ---------------------------------------------------------------- the kit additions */
  N.installKit = function (K, THREE, TXT) {
    if (K.registry && K.registry.school_clock) return;
    var M = N.mats(K, THREE, TXT);

    /* school_clock — a 14 in school wall clock. Origin at the centre of its BACK, face toward +z,
     * so a frame sets it on a wall by placing that point on the wall's surface.
     * options:
     *   d        face diameter in metres (0.36 classroom; 1.0 on a facade)
     *   hour     0..12, minute 0..60: the time the hands show
     *   sector   null | [startHour, hours]: the accent sector on the face, the deck's figure
     *   surround true puts it in a square cast stone surround, for a facade
     */
    K.define("school_clock", {
      size: [0.4, 0.4, 0.07],
      options: { d: 0.36, hour: 12, minute: 0, sector: null, surround: false, seed: 1 },
      note: "A school wall clock (0.36 m face by default, 1.0 m on a facade): black moulded case, domed lens, white face with minute ticks and hour bars and no numerals, black hands set by hour and minute, and an optional accent sector [startHour, hours]. Origin at the centre of its back, face toward +z.",
      make: function (o) {
        var g = new THREE.Group(), R = o.d / 2, depth = Math.max(0.045, o.d * 0.14);
        /* the case: a shallow drum whose front is the face's plane, and a rolled rim standing proud
         * of the face, so the face sits in the case like a dish rather than behind it */
        var fz = depth * 0.62;
        var drum = new THREE.Mesh(new THREE.CylinderGeometry(R * 1.1, R * 1.12, fz, 72), M.caseBlack);
        drum.rotation.x = Math.PI / 2; drum.position.z = fz / 2; drum.castShadow = true; drum.receiveShadow = true; g.add(drum);
        var rim = new THREE.Mesh(new THREE.TorusGeometry(R * 1.05, R * 0.06, 14, 96), M.caseRim);
        rim.position.z = fz + R * 0.02; rim.castShadow = true; g.add(rim);
        var face = new THREE.Mesh(new THREE.CircleGeometry(R, 96), M.face); face.position.z = fz + 0.0005; face.receiveShadow = false; g.add(face);
        /* the figure: an accent sector, clockwise from startHour, on the face under the ticks */
        if (o.sector) {
          var a0 = Math.PI / 2 - o.sector[0] / 12 * Math.PI * 2, sweep = o.sector[1] / 12 * Math.PI * 2;
          var sg = new THREE.RingGeometry(R * 0.2, R * 0.86, 64, 1, a0 - sweep, sweep);
          var sm = new THREE.Mesh(sg, M.sector); sm.position.z = fz + 0.0008; g.add(sm);
        }
        /* minute ticks and hour bars, raised a hair off the face */
        for (var i = 0; i < 60; i++) {
          var hr = i % 5 === 0, len = hr ? R * 0.15 : R * 0.05, wid = hr ? R * 0.035 : R * 0.012;
          var t = new THREE.Mesh(new THREE.BoxGeometry(wid, len, 0.0012), M.ink);
          var ang = i / 60 * Math.PI * 2, rr = R * 0.93 - len / 2;
          t.position.set(Math.sin(ang) * rr, Math.cos(ang) * rr, fz + 0.0012); t.rotation.z = -ang; g.add(t);
        }
        /* the hands: hour, minute and a slim sweep hand, on a hub */
        function hand(len, wid, ang, z, mat, tail) {
          var h = new THREE.Mesh(new THREE.BoxGeometry(wid, len + tail, 0.0018), mat);
          h.geometry.translate(0, (len - tail) / 2, 0);
          h.rotation.z = -ang; h.position.z = z; h.castShadow = true; g.add(h); return h;
        }
        var mAng = o.minute / 60 * Math.PI * 2, hAng = ((o.hour % 12) + o.minute / 60) / 12 * Math.PI * 2;
        hand(R * 0.55, R * 0.07, hAng, fz + 0.006, M.ink, R * 0.12);
        hand(R * 0.82, R * 0.045, mAng, fz + 0.009, M.ink, R * 0.14);
        hand(R * 0.86, R * 0.012, mAng + 0.9, fz + 0.012, M.ink, R * 0.2);
        var hub = new THREE.Mesh(new THREE.CylinderGeometry(R * 0.05, R * 0.05, 0.008, 24), M.hub); hub.rotation.x = Math.PI / 2; hub.position.z = fz + 0.013; g.add(hub);
        /* the domed lens */
        var lens = new THREE.Mesh(new THREE.SphereGeometry(R * 1.02, 48, 12, 0, Math.PI * 2, 0, 0.32), M.lens);
        lens.rotation.x = Math.PI / 2; lens.position.z = fz + R * 0.06 - R * 1.02 * Math.cos(0.32); g.add(lens);
        if (o.surround) {
          var s = o.d * 1.5;
          var plate = TXT.roundedBox(s, s, 0.12, 0.03, M.castStone); plate.position.z = -0.06; plate.castShadow = true; plate.receiveShadow = true; g.add(plate);
        }
        return g;
      }
    });

    /* locker_bank — a bank of full height steel lockers, each 0.305 m wide (12 in), 1.83 m tall
     * on a 0.1 m base, 0.38 m deep, facing +z, origin at the footprint centre on the floor.
     * options: count, open (a list of door indices that stand open, swung toward +x),
     *          accent (a list of door indices whose number plate carries the accent) */
    K.define("locker_bank", {
      size: [3.05, 1.93, 0.38],
      options: { count: 10, open: [], accent: [], seed: 1 },
      note: "A bank of full height steel school lockers, 0.305 m wide each, 1.83 m on a 0.1 m base, 0.38 m deep, facing +z. count, open (door indices standing open), accent (door indices whose plate is the accent).",
      make: function (o) {
        var g = new THREE.Group(), w = 0.305, H = 1.83, D = 0.38, n = o.count, W = n * w;
        K.box(W, 0.1, D - 0.04, M.base, 0, 0, -0.02, 0, g);
        K.box(W, H, 0.02, M.lockerDark, 0, 0.1, -D / 2 + 0.01, 0, g);
        K.box(W + 0.02, 0.03, D, M.locker, 0, 0.1 + H, 0, 0.005, g);
        var openSet = {}, accSet = {};
        (o.open || []).forEach(function (k) { openSet[k] = 1; });
        (o.accent || []).forEach(function (k) { accSet[k] = 1; });
        for (var i = 0; i < n; i++) {
          var x = -W / 2 + w * (i + 0.5);
          K.box(0.012, H, D, M.locker, x - w / 2 + 0.006, 0.1, 0, 0, g);
          var door = new THREE.Group();
          var leaf = K.box(w - 0.012, H - 0.02, 0.016, M.locker, (w - 0.012) / 2, 0, 0, 0.003, door);
          for (var v = 0; v < 3; v++) K.box(0.16, 0.012, 0.006, M.lockerDark, (w - 0.012) / 2, 0.12 + v * 0.03, 0.01, 0, door);
          for (var v2 = 0; v2 < 3; v2++) K.box(0.16, 0.012, 0.006, M.lockerDark, (w - 0.012) / 2, H - 0.22 + v2 * 0.03, 0.01, 0, door);
          K.box(0.03, 0.12, 0.02, M.hub, w - 0.06, H * 0.5, 0.012, 0.004, door);
          K.box(0.07, 0.03, 0.004, accSet[i] ? M.lockerAccent : M.castStone, (w - 0.012) / 2, H - 0.32, 0.011, 0, door);
          door.position.set(x - w / 2 + 0.006, 0.11, D / 2 - 0.008);
          if (openSet[i]) door.rotation.y = -1.25;
          g.add(door);
        }
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });
  };

  /* A CLOCK ON A FACADE: the kit school's entry vestibule carries a blank cast stone name panel
   * 4.6 m up on its south face. The deck's clock hangs in front of it, centred, in its surround.
   * The kit school: length 57 (default 56), depth 14, the vestibule centred at x = -L/2 + 13,
   * its outer face at z = 14/2 + 3.2. Returns the clock. */
  N.facadeClock = function (K, school, o) {
    o = o || {};
    var L = o.length || 57, ex = -L / 2 + 13;
    var c = K.make("school_clock", { d: o.d || 1.0, hour: o.hour == null ? 12 : o.hour, minute: o.minute || 0, sector: o.sector || null, surround: true, seed: 3 });
    c.position.set(ex, 5.15, 7 + 3.2 + 0.13);
    school.add(c);
    return c;
  };

  /* ---------------------------------------------------------------- the frame shell */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };
  N.rigSpec = function (W, size, map) {
    return Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { shadowSize: size || 30, mapSize: map || 2048, radius: 4 }) });
  };
  N.rigOpts = function (target, o) {
    o = o || {};
    return { target: target, distance: o.distance || 90, shadowFar: o.shadowFar || 220, normalBias: o.normalBias == null ? 0.02 : o.normalBias };
  };

  /* THE SKY BAND THE TYPE STANDS IN. At noon the type is dark, so the band is a pale wash that
   * lifts the sky behind the hook, never over 0.45 alpha. */
  N.atmosphere = function (cx, o) {
    o = o || {};
    var dek = document.querySelector(".dek"), bottom = o.to;
    if (bottom == null && dek) { var b = dek.getBoundingClientRect(); bottom = b.top + b.height; }
    if (bottom != null) bottom += o.pad == null ? 70 : o.pad;
    var a = o.a == null ? 0.2 : Math.min(0.45, o.a), c = o.rgb || "244,242,236";
    if (bottom != null && a > 0) {
      var fade = o.fade || 160, g = cx.createLinearGradient(0, 0, 0, bottom + fade);
      g.addColorStop(0, "rgba(" + c + "," + (a * 0.85) + ")");
      g.addColorStop(Math.max(0.05, bottom / (bottom + fade)), "rgba(" + c + "," + a + ")");
      g.addColorStop(1, "rgba(" + c + ",0)");
      cx.fillStyle = g; cx.fillRect(0, 0, N.W, bottom + fade);
    }
  };
  /* KNOCK THE EDGE OUT BEHIND A LINE OF TYPE, without removing its light. */
  N.soften = function (cx, selectors, o) {
    o = o || {};
    var blur = o.blur || 12, pad = o.pad == null ? 18 : o.pad, feather = o.feather || 70;
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
   * last. A pale band under the footer, never a box and never over 0.45. */
  N.post = function (cx, o) {
    o = o || {};
    N.atmosphere(cx, { a: o.a == null ? 0.18 : o.a, to: o.to, fade: o.fade, rgb: o.rgb, pad: o.pad });
    N.soften(cx, o.type || [".kick", ".hook", ".dek"], { blur: o.typeBlur || 8, pad: 8, feather: o.typeFeather || 26 });
    N.soften(cx, [".tx-site", ".src"], { blur: o.siteBlur || 9, pad: 14, feather: 40 });
    var y0 = N.H - (o.veilH || 200), v = cx.createLinearGradient(0, y0, 0, N.H), rgb = o.veilRgb || "238,236,230";
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(" + rgb + "," + (Math.min(0.45, o.veil == null ? 0.26 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    N.dither(cx);
  };
  N.dither = function (cx) {
    var c = cx.canvas, id = cx.getImageData(0, 0, c.width, c.height), d = id.data, s = 1234567;
    function rnd() { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    for (var i = 0; i < d.length; i += 4) { var n = (rnd() + rnd() - 1) * 1.2; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
    cx.putImageData(id, 0, 0);
  };

  /* THE SHELL EVERY FRAME SHARES: the type styles, the furniture, the fit of the hook. Dark type at
   * noon, with a pale halo rather than a shadow. A frame on a dark ground (a room facing away from
   * its window) passes { light: true } and the type turns light. */
  N.CSS = function (light) {
    var ink = light ? "#F5F2EB" : N.INK, dek = light ? "#ECE8E0" : "#1D2026", halo = light ? "rgba(10,12,16,0.55)" : "rgba(246,244,238,0.7)", halo2 = light ? "rgba(10,12,16,0.42)" : "rgba(246,244,238,0.55)";
    return [
      "* { margin:0; padding:0; box-sizing:border-box; }",
      "html, body { width:1080px; height:1350px; overflow:hidden; background:#E7E3DA; }",
      'body { position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }',
      "canvas#art { position:absolute; left:0; top:0; width:1080px; height:1350px; }",
      '.hook { position:absolute; left:80px; top:150px; width:900px; font-family:"Fraunces", serif; font-weight:800; line-height:0.98; letter-spacing:-0.012em; color:' + ink + '; font-variation-settings:"opsz" 144; z-index:10; }',
      ".dek { position:absolute; left:82px; width:820px; font-size:31px; font-weight:600; line-height:1.38; color:" + dek + "; z-index:10; }",
      '.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.07em; line-height:1.5; color:' + ink + '; white-space:nowrap; z-index:20; }',
      '.lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; font-weight:500; letter-spacing:0.06em; color:' + ink + '; white-space:nowrap; z-index:12; }',
      ".hook, .dek, .tx-site, .kick, .src, .cap, .lab, .count { text-shadow:0 0 2px " + halo + ", 0 1px 12px " + halo2 + "; }"
    ].join("\n");
  };
  N.start = function (o) {
    var st = document.createElement("style"); st.textContent = N.CSS(!!o.light);
    document.head.insertBefore(st, document.head.firstChild);
    TXLAYOUT.mount(document.body, { kicker: o.kicker, counter: o.counter, src: o.src, ink: o.light ? "#ECE8E0" : "#1D2026" });
    TX.fitText(document.getElementById("hook"), o.fit || { min: 96, max: 128, maxLines: 2 });
    N.follow();
  };
  N.boot = async function (THREE, bench, initKit, o) {
    N.T = THREE;
    await document.fonts.ready;
    N.start(o);
    var TXT = typeof bench === "function" ? bench(THREE) : bench, K = initKit(THREE, TXT);
    N.installKit(K, THREE, TXT);
    return { TXT: TXT, K: K, gl: N.glCanvas(), W: TXT.deckWorld() };
  };
  N.stage = function (TXT, gl, W, o) {
    o = o || {};
    return TXT.setup(gl, { w: N.W, h: N.H, fog: [W.haze, o.fog == null ? W.fogDensity : o.fog], exposure: W.exposure * (o.exposure || 1),
                           tone: W.tone, fov: o.fov || 30, near: o.near || 0.05, far: o.far || 12000 });
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

  global.NB = N;
})(this);
