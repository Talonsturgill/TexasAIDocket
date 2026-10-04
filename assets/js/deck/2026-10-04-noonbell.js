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
 * the sun high in the south, a touch east of it, where it stands at noon by the clock in Central Daylight Time. az runs clockwise from +z toward +x,
 * so the key sits at (sin 10, ., cos 10). A building whose face looks south (+z) is lit full on
 * and its shadow falls short behind it to the north. A camera looking north sees sunlit faces.
 *
 * THE HERO OBJECT. One Type C school bus, the kit's `school_bus`, unlettered, its stop arm out for a
 * no and folded for a yes, one bus per district wherever a frame counts districts (N.bus below).
 *
 * THE CLOCK. One school wall clock, `school_clock`, a kit addition below: 0.36 m across, a
 * black moulded case with a domed lens, a white face with minute ticks and twelve hour bars and no
 * numerals, black hands, and the deck's figure drawn on the face: a sector two hours wide in the
 * accent, the hours Alpha's full model gives the AI to teach basic subjects each day (c34). The frame
 * sets the time on its hands and whether the sector shows.
 *
 * THE ACCENT. #C2477A, "the platform": only ever the card in a pilot district's bus windshield,
 * the two hour sector on the clock's face, and the measured column for the one school with scores.
 * Never a sky, a building, a person's clothing or a light.
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

  /* ---------------------------------------------------------------- materials */
  N.mats = function (K, THREE, TXT) {
    if (N._m) return N._m;
    N._m = {
      caseBlack: K.mat("nb-case", { color: 0x17181a, roughness: 0.42, metalness: 0.1 }),
      caseRim: K.mat("nb-rim", { color: 0x2a2c2f, roughness: 0.3, metalness: 0.55 }),
      face: K.mat("nb-face", { color: 0xffffff, roughness: 0.62, metalness: 0, map: N.faceTex(THREE) }),
      ink: K.mat("nb-ink", { color: 0x121314, roughness: 0.5, metalness: 0.05 }),
      hub: K.mat("nb-hub", { color: 0x0d0d0e, roughness: 0.3, metalness: 0.6 }),
      sector: K.mat("nb-sector", { color: 0xc2477a, roughness: 0.55, metalness: 0, emissive: 0x6a1838, emissiveIntensity: 0.35, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }),
      lens: K.mat("nb-lens", { color: 0xffffff, roughness: 0.04, metalness: 0, transparent: true, opacity: 0.12 }, true),
      castStone: K.mat("nb-cast", { color: 0xddd3bd, roughness: 0.88, metalness: 0 }),
      card: K.mat("nb-card2", { color: 0x8e2a52, roughness: 0.85, metalness: 0, emissive: 0x2a0816, emissiveIntensity: 0.3, side: 2 }),
      glassBand: K.mat("nb-glassband", { color: 0x9fb4bd, roughness: 0.08, metalness: 0, transparent: true, opacity: 0.55 }, true),
      glassGhost: K.mat("nb-glassghost", { color: 0xe6eef0, roughness: 0.05, metalness: 0, transparent: true, opacity: 0.16 }, true),
      paper: K.mat("nb-paper", { color: 0xf4f1e9, roughness: 0.82, metalness: 0 }),
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
          var sm = new THREE.Mesh(sg, M.sector); sm.position.z = fz + 0.0012; g.add(sm);
        }
        /* minute ticks and hour bars, raised a hair off the face */
        for (var i = 0; i < 60; i++) {
          var hr = i % 5 === 0, len = hr ? R * 0.15 : R * 0.05, wid = hr ? R * 0.035 : R * 0.012;
          var t = new THREE.Mesh(new THREE.BoxGeometry(wid, len, 0.0012), M.ink);
          var ang = i / 60 * Math.PI * 2, rr = R * 0.93 - len / 2;
          t.position.set(Math.sin(ang) * rr, Math.cos(ang) * rr, fz + 0.0026); t.rotation.z = -ang; g.add(t);
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
        hand(R * 0.86, R * 0.012, mAng + 3.3, fz + 0.012, M.ink, R * 0.2);
        var hub = new THREE.Mesh(new THREE.CylinderGeometry(R * 0.05, R * 0.05, 0.008, 24), M.hub); hub.rotation.x = Math.PI / 2; hub.position.z = fz + 0.013; g.add(hub);
        /* the domed lens */
        var lens = new THREE.Mesh(new THREE.SphereGeometry(R * 1.02, 48, 12, 0, Math.PI * 2, 0, 0.32), M.lens);
        lens.rotation.x = Math.PI / 2; lens.position.z = fz + R * 0.06 - R * 1.02 * Math.cos(0.32); g.add(lens);
        if (o.surround) {
          var s = o.d * 1.5;
          var plate = TXT.roundedBox(s, s, 0.12, 0.03, M.castStone); plate.position.z = -0.06; plate.castShadow = true; plate.receiveShadow = true; plate.userData.keepCast = true; g.add(plate);
          /* ON ITS PLATE THE CLOCK CASTS NO MAPPED SHADOW. The shadow map at this scale drew the
           * case's shadow as a stippled ring (no. 42 pixel rounds 2 and 3), so the case's weight
           * is a soft painted falloff a hair off the plate, offset down and away from the sun. */
          g.userData.noCast = true;
          var sc2 = document.createElement("canvas"); sc2.width = sc2.height = 256; var sx = sc2.getContext("2d");
          var rg = sx.createRadialGradient(128, 128, 70, 128, 128, 128); rg.addColorStop(0, "rgba(0,0,0,1)"); rg.addColorStop(1, "rgba(0,0,0,0)");
          sx.fillStyle = rg; sx.fillRect(0, 0, 256, 256);
          var st = new THREE.CanvasTexture(sc2);
          var shade = new THREE.Mesh(new THREE.PlaneGeometry(R * 2.9, R * 2.9), new THREE.MeshBasicMaterial({ map: st, color: 0x2a2018, transparent: true, opacity: 0.42, depthWrite: false }));
          shade.position.set(-R * 0.1, -R * 0.16, 0.002); g.add(shade);
        }
        return g;
      }
    });

    /* measure_column — a column at one scale for a share of a hundred. Origin at the centre of its
     * base. options: h (metres, the drawn share), w (square section), kind 'solid' | 'glass' |
     * 'footprint' (a plate for a share of zero), finish 'stone' | 'accent'. The glass kind is a
     * band from y0 to h, for a claimed range. */
    K.define("measure_column", {
      size: [0.16, 1.0, 0.16],
      options: { h: 0.5, y0: 0, w: 0.16, kind: "solid", finish: "stone", seed: 1 },
      note: "A column at one scale: h metres tall on a square section w, solid (cast stone or the accent), glass (a band from y0 to h for a claimed range) or footprint (a plate for zero). Origin at the base centre.",
      make: function (o) {
        var g = new THREE.Group();
        if (o.kind === "footprint") {
          K.box(o.w + 0.02, 0.006, o.w + 0.02, M.castStone, 0, 0, 0, 0.002, g);
        } else if (o.kind === "glass") {
          /* a faint glass column from the table to y0, so the band reads as a height and not a
           * floating box, then the claimed range from y0 to h in a stronger tint */
          if (o.y0 > 0) { var ghost = new THREE.Mesh(new THREE.BoxGeometry(o.w * 0.98, o.y0, o.w * 0.98), M.glassGhost); ghost.position.y = o.y0 / 2; g.add(ghost);
            var ge = new THREE.LineSegments(new THREE.EdgesGeometry(ghost.geometry), new THREE.LineBasicMaterial({ color: 0x8a959c, transparent: true, opacity: 0.6 })); ge.position.copy(ghost.position); g.add(ge); }
          var band = new THREE.Mesh(new THREE.BoxGeometry(o.w, o.h - o.y0, o.w), M.glassBand);
          band.position.y = o.y0 + (o.h - o.y0) / 2; g.add(band);
          var edges = new THREE.LineSegments(new THREE.EdgesGeometry(band.geometry), new THREE.LineBasicMaterial({ color: 0x5a6670 }));
          edges.position.copy(band.position); g.add(edges);
          K.box(o.w + 0.02, 0.006, o.w + 0.02, M.castStone, 0, 0, 0, 0.002, g);
        } else {
          var c = TXT.roundedBox(o.w, o.h, o.w, 0.012, o.finish === "accent" ? M.sector : M.castStone);
          c.position.y = o.h / 2; g.add(c);
        }
        g.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        return g;
      }
    });

    /* letter_sheet — one US letter sheet (0.216 x 0.279 m) lying on a surface with a soft curl at
     * its far corners. Origin at its centre on the surface, long side along z. No type is drawn
     * into it: a frame sets type over it in the DOM. */
    K.define("letter_sheet", {
      size: [0.216, 0.004, 0.279],
      options: { curl: 0.006, seed: 1 },
      note: "A US letter sheet lying flat with a slight curl, 0.216 x 0.279 m, origin at its centre on the surface. Blank: type is DOM.",
      make: function (o) {
        var geo = new THREE.PlaneGeometry(0.216, 0.279, 16, 20), pos = geo.attributes.position;
        for (var i = 0; i < pos.count; i++) {
          var x = pos.getX(i), y = pos.getY(i), e = Math.max(0, (Math.abs(x) - 0.06) / 0.048) * Math.max(0, (y - 0.06) / 0.08);
          pos.setZ(i, o.curl * e * e + 0.0008);
        }
        geo.computeVertexNormals();
        var m = new THREE.Mesh(geo, M.paper); m.rotation.x = -Math.PI / 2; m.receiveShadow = true; m.castShadow = true;
        var g = new THREE.Group(); g.add(m); return g;
      }
    });
  };


  /* THE HERO. The kit's Type C school bus, unlettered, white roof, its stop arm out for a no and
   * folded for a yes. A pilot district's bus carries the accent placard, a 0.95 x 0.46 m card standing
   * in the lower windshield on the door side, the only accent on the bus. Front faces +z. */
  N.bus = function (K, o) {
    o = o || {};
    var THREE = N.T, b = K.make("school_bus", { seed: o.seed || 11, whiteRoof: true, stopArm: !!o.arm, district: null });
    if (o.card) {
      var M = N._m, card = new THREE.Mesh(new THREE.PlaneGeometry(0.95, 0.46), M.card);
      card.position.set(-0.42, 2.17, 4.0); card.rotation.x = -0.22; b.add(card);
    }
    b.traverse(function (m) { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
    return b;
  };

  /* A CLOCK ON A FACADE: the kit school's entry vestibule carries a blank cast stone name panel
   * 4.6 m up on its south face. The deck's clock hangs in front of it, centred, in its surround.
   * The kit school: length 57 (default 56), depth 14, the vestibule centred at x = -L/2 + 13,
   * its outer face at z = 14/2 + 3.2. Returns the clock. */
  N.facadeClock = function (K, school, o) {
    o = o || {};
    var L = o.length || 57, ex = -L / 2 + 13;
    var c = K.make("school_clock", { d: o.d || 1.0, hour: o.hour == null ? 12 : o.hour, minute: o.minute || 0, sector: o.sector || null, surround: true, seed: 3 });
    /* over the entry vestibule by default; o.x and o.z hang it elsewhere on the facade */
    c.position.set(o.x != null ? o.x : ex, o.y || 4.75, o.z != null ? o.z : 7 + 3.2 + 0.13);
    school.add(c);
    return c;
  };


  /* A ROOM IN THE DECK'S LIGHT. TXT.interior builds the walls and a lit window; the deck's rooms
   * are limestone and the window is on the back wall so the light has a source a reader sees.
   * A darker floor is laid a hair above the room's own, so the frame steps down from the noon
   * exteriors instead of bleaching. o: w, d, h, wall, floor (hex), windowX. The frame calls
   * TXT.interior itself with N.roomSpec(o), so the room it stands in is in its own source, and
   * hands the room here for the window and the floor. */
  N.roomSpec = function (o) {
    o = o || {};
    return { w: o.w || 12, d: o.d || 9, h: o.h || 6, floor: "concrete", wall: o.wall || 0xb9ae9b, window: null, light: o.light || 0.7 };
  };
  /* THE WALL IS LIMESTONE ASHLAR, the stone of a Texas public building: courses of sawn block in
   * the wall's own tone, each block a shade off its neighbours, with a recessed mortar joint. Drawn
   * once to a canvas at the wall's own size, so a course reads the same height in every room. */
  N.ashlar = function (mesh, o) {
    var T = N.T, w = o.w || 12, h = o.h || 6, ppm = Math.max(40, Math.min(150, Math.floor(3600 / Math.max(w, h))));
    var c = document.createElement("canvas"); c.width = Math.round(w * ppm); c.height = Math.round(h * ppm);
    var x = c.getContext("2d"), hx = o.wall || 0xb9ae9b, base = [(hx >> 16) & 255, (hx >> 8) & 255, hx & 255], s = 20261004;
    function rnd() { s = (Math.imul(s, 1103515245) + 12345) & 0x7fffffff; return s / 0x7fffffff; }
    /* the tone is the wall's own sRGB hex scaled, written to the canvas as sRGB */
    function tone(k) { return "rgb(" + base.map(function (v) { return Math.round(Math.min(255, v * k)); }).join(",") + ")"; }
    var ch = 0.45 * ppm, joint = Math.max(2, Math.round(0.018 * ppm));
    x.fillStyle = tone(0.8); x.fillRect(0, 0, c.width, c.height);
    for (var row = 0, y = c.height; y > -ch; row++, y -= ch) {
      var bx = -(row % 2) * 0.45 * ppm;
      while (bx < c.width) {
        var bw = (0.7 + rnd() * 0.5) * ppm;
        x.fillStyle = tone(0.93 + rnd() * 0.12); x.fillRect(bx + joint / 2, y - ch + joint / 2, bw - joint, ch - joint);
        for (var k = 0; k < 14; k++) { x.fillStyle = "rgba(60,48,36," + (rnd() * 0.02).toFixed(3) + ")"; x.beginPath(); x.arc(bx + rnd() * bw, y - rnd() * ch, (0.01 + rnd() * 0.05) * ppm, 0, 6.283); x.fill(); }
        bx += bw;
      }
    }
    var t = new T.CanvasTexture(c); t.colorSpace = T.SRGBColorSpace; t.anisotropy = 8;
    /* a face of the wall's own size a centimetre in front of it, so the block size is known */
    var face = new T.Mesh(new T.PlaneGeometry(w, h), new T.MeshStandardMaterial({ color: 0xffffff, map: t, roughness: 0.93, metalness: 0 }));
    face.position.set(0, h / 2, (o.z || 0) + 0.11); face.receiveShadow = true; face.castShadow = false;
    return face;
  };
  N.room = function (TXT, R, o, room) {
    o = o || {};
    if (room && o.ashlar !== false) R.scene.add(N.ashlar(null, { w: o.w || 12, h: o.h || 6, wall: o.wall, z: -(o.d || 9) / 2 }));
    var T = N.T, d = o.d || 9, ww = o.windowW || 2.6, wh = o.windowH || 2.2;
    /* the window, set where the frame wants it on the back wall: a lit pane in a dark frame with a sill */
    /* the pane shows the noon outside as the deck's own sky, blue at the head going to the bleached
     * horizon value at the sill, so the window reads as a source and never as a blank panel or a
     * painted view */
    if (o.window !== false) {
    var vc = document.createElement("canvas"); vc.width = 256; vc.height = 256; var vx = vc.getContext("2d");
    var sg = vx.createLinearGradient(0, 0, 0, 256); sg.addColorStop(0, "#b9cadb"); sg.addColorStop(0.7, "#e9ebe6"); sg.addColorStop(1, "#f4f1e8"); vx.fillStyle = sg; vx.fillRect(0, 0, 256, 256);
    var vt = new T.CanvasTexture(vc); vt.colorSpace = T.SRGBColorSpace;
    var pane = new T.Mesh(new T.PlaneGeometry(ww, wh), new T.MeshBasicMaterial({ map: vt, toneMapped: true }));
    pane.material.color.setScalar(o.windowI ? o.windowI / 2.4 * 1.15 : 1.15); pane.position.set(o.windowX || 0, o.windowY || 2.2, -d / 2 + 0.115); R.scene.add(pane);
    var fm = new T.MeshStandardMaterial({ color: 0x3a3632, roughness: 0.6, metalness: 0.3 });
    [[ww + 0.16, 0.08, 0, wh / 2 + 0.04], [ww + 0.16, 0.12, 0, -wh / 2 - 0.06], [0.08, wh, -ww / 2 - 0.04, 0], [0.08, wh, ww / 2 + 0.04, 0], [0.05, wh, 0, 0]].forEach(function (b) {
      var m = new T.Mesh(new T.BoxGeometry(b[0], b[1], 0.06), fm); m.position.set((o.windowX || 0) + b[2], (o.windowY || 2.2) + b[3], -d / 2 + 0.13); m.castShadow = true; R.scene.add(m);
    });
    }
    /* the floor: the concrete surface with its tooth and joints, in the frame's darker tone */
    TXT.ground(R, { surface: "concrete", color: o.floor || 0x6b6f73, size: 60, tile: o.tile || 2.5, y: 0.003, seed: o.seed });
    return room;
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
    N.soften(cx, [".tx-site", ".src"], { blur: o.siteBlur || 18, pad: 18, feather: 70 });
    var y0 = N.H - (o.veilH || 250), v = cx.createLinearGradient(0, y0, 0, N.H), rgb = o.veilRgb || "238,236,230";
    for (var k = 0; k <= 8; k++) { var t = k / 8, e = t * t * (3 - 2 * t); v.addColorStop(t, "rgba(" + rgb + "," + (Math.min(0.45, o.veil == null ? 0.45 : o.veil) * e).toFixed(4) + ")"); }
    cx.fillStyle = v; cx.fillRect(0, y0, N.W, N.H - y0);
    /* THE FOOTER ROW'S WASH, for a frame whose ground under the footer is asphalt or shadow: a
     * feathered band across the whole width, peaking on the footer's own line, so the citation
     * and the site line clear 4.5 without a plate behind either */
    if (o.footWash) {
      var f = document.querySelector(".tx-site"), sc = N.H / document.body.clientHeight, fr = f ? f.getBoundingClientRect() : null;
      var mid = fr ? (fr.top + fr.height / 2) * sc : N.H - 110, half = 70;
      var fw = cx.createLinearGradient(0, mid - half, 0, mid + half);
      [[0, 0], [0.3, 1], [0.7, 1], [1, 0]].forEach(function (p) { fw.addColorStop(p[0], "rgba(" + rgb + "," + (o.footWash * p[1]).toFixed(4) + ")"); });
      cx.fillStyle = fw; cx.fillRect(0, mid - half, N.W, half * 2);
    }
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
