/* deck/2026-09-26-fortyfive.js — the chassis for the 2026-09-26 deck, driverless Class 8 freight
 * on Interstate 45 between Dallas and Houston and the state authorization it runs under
 * (tx-2026-0188).
 *
 * THE HERO OBJECT. One Class 8 sleeper tractor with a 53 ft van, the kit's `semi_truck`, carrying
 * the thing the kit does not have: an autonomy sensor kit (a pod on each mirror arm and a roof bar
 * with a spinning lidar), a cab you can see into with the driver's seat, the wheel and the dash in
 * it, and lamps that are actually lit. The sensor kit and the open cab are ILLUSTRATIVE. None of
 * the three companies' releases gives a drawing a reader can check a silhouette against, so the
 * shapes follow the general arrangement of a long-haul autonomy retrofit and nothing here claims
 * to be any one company's hardware. A frame that shows it close says so.
 *
 * THE SEAT IS THE STORY. The wheel is there and nobody's hands are on it. The accent is worn by
 * the lidar band alone, the one part of the truck that is doing the driving.
 *
 * WHAT THIS FILE IS NOT. A frame. It declares the deck's one light and world, installs the kit
 * additions and the deck materials, and hands a frame primitives. Each frame sets up its own
 * renderer, camera, sky, ground and composition in its own source.
 */
(function (global) {
  "use strict";
  if (!global.TXDECK) throw new Error("fortyfive.js needs txdeck.js loaded first");

  /* ONE DECLARATION. Blue hour on the interstate: the sun just under the western horizon, an
   * amber seam low in the west, and the declared light is the high-mast and cab lamps' key, up and
   * to the west of the road, inside blueHour's lamp range of 25 to 45 degrees. az is clockwise
   * from +Z toward +X. Every cast in the deck runs east and away. */
  TXDECK.declare({
    world: "fortyfive",
    light: { az: -70, el: 32 },
    sky: "blueHour",
    ground: "#0E131B",
    material: "#DADDE0",
    accent: "#4FC79A",
    grade: {
      exposure: 0.0,
      saturation: 1.03,
      contrast: 1.06,
      filmic: true,
      lift: [0.006, 0.009, 0.016],
      gain: [1.02, 1.0, 0.985],
      vignette: 0.22,
      bloom: { threshold: 0.82, strength: 0.28, radius: 14 },
      grain: { amount: 0.013, size: 2, seed: 20260926 },
      aberration: 0,
      dither: true,
      sharpen: 0.18
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20260926;
  N.ACCENT = 0x4fc79a;          /* signal_open, config/brand.yaml: the one part that is driving */
  N.GROUND_HEX = "#0E131B";

  /* ONE MATERIAL VOCABULARY. Painted tractor steel, a white van, chrome, black sensor housings,
   * warm cab light, and the accent on the lidar band alone. */
  N.mats = function (TXT, THREE) {
    var S = function (c, m, r) { return TXT.mat.clay(c, { metalness: m, roughness: r }); };
    return {
      housing: TXT.mat.plastic(0x15181c, { roughness: 0.38, metalness: 0.15 }),
      housingEdge: S(0x2a2f35, 0.3, 0.42),
      lens: TXT.mat.plastic(0x0a0e12, { roughness: 0.06, metalness: 0.5 }),
      band: TXT.mat.emissive(N.ACCENT, 2.2),
      arm: S(0x3a3f44, 0.6, 0.35),
      seat: S(0x2b2d31, 0.0, 0.8),
      seatStitch: S(0x3c3f44, 0.0, 0.7),
      dash: S(0x1e2024, 0.1, 0.6),
      wheel: S(0x17191c, 0.1, 0.5),
      screen: TXT.mat.emissive(0x9fc9e0, 0.9),
      cabGlow: TXT.mat.emissive(0xffd29a, 1.1),
      headLamp: TXT.mat.emissive(0xfff2dc, 5.0),
      tailLamp: TXT.mat.emissive(0xff3a2a, 3.0),
      markerLamp: TXT.mat.emissive(0xffa53a, 3.5),
      glass: new THREE.MeshPhysicalMaterial({ color: 0x9fb2bf, roughness: 0.04, metalness: 0.0,
        transparent: true, opacity: 0.12, depthWrite: false })
    };
  };

  /* THE TRUCK. The kit's semi_truck with the deck's additions. Faces +z like every kit model.
   * The kit centres the coupled footprint on the origin, so the cab's own coordinates are read
   * back from the built model rather than typed: userData.size is measured by K.make, and the
   * tractor's front is at +size[2]/2. o.lit lights the lamps; o.lidar false leaves the sensor kit off (a conventional truck). */
  N.truck = function (THREE, TXT, K, M, o) {
    o = o || {};
    var t = K.make("semi_truck", { seed: o.seed || 3, color: o.color != null ? o.color : 0xdfe2e4,
      trailer: o.trailer !== false, trailerColor: o.trailerColor != null ? o.trailerColor : 0xecedea });
    var front = t.userData.size[2] / 2;           /* local z of the front bumper after centring */
    var zc = function (kitZ) { return front - 0.25 + kitZ; };   /* kit-local z to model z */
    var hw = 1.22;

    if (o.lidar !== false) {
      var kit = new THREE.Group();
      /* a pod on each mirror arm, forward of the doors: a black housing with a lens face and a
       * thin accent band where its lidar sits */
      [1, -1].forEach(function (s) {
        var arm = TXT.roundedBox(0.34, 0.05, 0.06, 0.015, M.arm); arm.position.set(s * (hw + 0.17), 2.55, zc(-1.95)); kit.add(arm);
        var pod = TXT.roundedBox(0.2, 0.42, 0.26, 0.05, M.housing); pod.position.set(s * (hw + 0.36), 2.5, zc(-1.95)); kit.add(pod);
        var lens = new THREE.Mesh(new THREE.PlaneGeometry(0.14, 0.2), M.lens); lens.position.set(s * (hw + 0.36), 2.52, zc(-1.95) + 0.131); kit.add(lens);
        var band = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.03, 32), M.band); band.position.set(s * (hw + 0.36), 2.26, zc(-1.95)); kit.add(band);
        var cap = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.07, 32), M.housing); cap.position.set(s * (hw + 0.36), 2.21, zc(-1.95)); kit.add(cap);
      });
      /* the roof bar over the windshield, cameras along it, and the puck in the middle */
      var bar = TXT.roundedBox(2.1, 0.14, 0.34, 0.05, M.housing); bar.position.set(0, 3.22, zc(-2.4)); kit.add(bar);
      for (var i = -3; i <= 3; i++) {
        if (i === 0) continue;
        var cam = new THREE.Mesh(new THREE.PlaneGeometry(0.1, 0.07), M.lens); cam.position.set(i * 0.28, 3.22, zc(-2.4) + 0.171); kit.add(cam);
      }
      var puckBase = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.15, 0.08, 40), M.housingEdge); puckBase.position.set(0, 3.33, zc(-2.4)); kit.add(puckBase);
      var puckBand = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.05, 40), M.band); puckBand.position.set(0, 3.395, zc(-2.4)); kit.add(puckBand);
      var puckCap = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.12, 0.07, 40), M.housing); puckCap.position.set(0, 3.455, zc(-2.4)); kit.add(puckCap);
      t.add(kit);
    }

    if (o.lit) {
      /* headlamps: bright discs over the kit's lamp bodies, and two real spot lights down the road */
      [0.84, -0.84].forEach(function (x) {
        var hl = new THREE.Mesh(new THREE.CircleGeometry(0.085, 24), M.headLamp); hl.position.set(x, 1.5, front + 0.03); t.add(hl);
        var sp = new THREE.SpotLight(0xfff0d8, o.beam != null ? o.beam : 60, 90, 0.42, 0.55, 1.6);
        sp.position.set(x, 1.5, front + 0.1); sp.target.position.set(x * 1.6, 0, front + 40); sp.castShadow = false;
        t.add(sp); t.add(sp.target);
      });
      /* amber cab markers over the roof, and the van's tails at the back */
      for (var k = -2; k <= 2; k++) { var mk = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.04, 0.05), M.markerLamp); mk.position.set(k * 0.25, 3.17, zc(-2.6)); t.add(mk); }
      var backZ = -t.userData.size[2] / 2 - 0.02;
      [0.95, -0.95].forEach(function (x) { var tl = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.2, 0.04), M.tailLamp); tl.position.set(x, 1.1, backZ); t.add(tl); });
    }
    t.userData.front = front;
    return t;
  };

  /* THE CAB, AS A SET. The kit's tractor is a solid body, so its glass can't show a seat behind
   * it. For the frames that stand inside the cab this builds the cab itself at true size around
   * the origin: the floor at y 0, the windshield across -z (the truck drives toward -z here), the
   * driver's seat on +x and the passenger seat on -x, the dash, the wheel on its column, the
   * A pillars, the roof, the door with its window, and the bunk curtain behind. Open to the road
   * through the windshield and the side glass, so a frame standing in here still stands in the
   * deck's world and its sky. Dimensions are a Class 8 sleeper's general interior, illustrative.
   * o.observer puts a seated person on the passenger side with hands in the lap. */
  N.cab = function (THREE, TXT, K, M, o) {
    o = o || {};
    var g = new THREE.Group();
    var W = 2.3, H = 1.9, D = 2.2, zf = -1.0;            /* width, floor to roof, depth, windshield base z */
    var trim = TXT.mat.clay(0x2e3136, { metalness: 0.05, roughness: 0.75 });
    var head = TXT.mat.clay(0x8f8a82, { metalness: 0, roughness: 0.9 });
    var floor = TXT.roundedBox(W, 0.06, D, 0.01, TXT.mat.clay(0x1c1d20, { roughness: 0.95 })); floor.position.set(0, -0.03, zf + D / 2 - 0.2); g.add(floor);
    var roof = TXT.roundedBox(W, 0.06, D + 0.3, 0.02, head); roof.position.set(0, H, zf + D / 2 - 0.35); g.add(roof);
    /* the windshield frame: a lower cowl, a header, a centre post and the A pillars, leaning back */
    var lean = 0.32;
    var cowl = TXT.roundedBox(W, 0.1, 0.12, 0.02, trim); cowl.position.set(0, 1.0, zf); g.add(cowl);
    var header = TXT.roundedBox(W, 0.14, 0.14, 0.02, trim); header.position.set(0, H - 0.07, zf + 0.3); g.add(header);
    [-1, 0, 1].forEach(function (s) {
      var post = TXT.roundedBox(s === 0 ? 0.07 : 0.14, 0.95, 0.1, 0.02, trim);
      post.position.set(s * (W / 2 - 0.07), 1.47, zf + 0.15); post.rotation.x = lean; g.add(post);
    });
    /* doors: a panel below the belt line and a pillar behind the window */
    [1, -1].forEach(function (s) {
      var door = TXT.roundedBox(0.08, 1.0, 1.25, 0.02, trim); door.position.set(s * (W / 2), 0.5, zf + 0.75); g.add(door);
      var bpil = TXT.roundedBox(0.1, H - 1.0, 0.12, 0.02, trim); bpil.position.set(s * (W / 2), 1.0 + (H - 1.0) / 2, zf + 1.4); g.add(bpil);
      var rear = TXT.roundedBox(0.08, H, 0.9, 0.02, head); rear.position.set(s * (W / 2), H / 2, zf + 1.9); g.add(rear);
    });
    /* the bunk curtain behind the seats, a soft dark fold */
    var curtain = TXT.roundedBox(W, H, 0.05, 0.02, TXT.mat.clay(0x24262a, { roughness: 1 })); curtain.position.set(0, H / 2, zf + 2.3); g.add(curtain);
    /* the dash, a wide shelf under the glass, with the instrument cluster in front of the wheel */
    var dash = TXT.roundedBox(W - 0.1, 0.34, 0.55, 0.06, M.dash); dash.position.set(0, 0.86, zf + 0.3); g.add(dash);
    var cluster = TXT.roundedBox(0.5, 0.2, 0.12, 0.03, M.dash); cluster.position.set(0.55, 1.06, zf + 0.5); g.add(cluster);
    var gauge = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.12), M.screen); gauge.position.set(0.55, 1.07, zf + 0.565); g.add(gauge);
    var mid = new THREE.Mesh(new THREE.PlaneGeometry(0.26, 0.16), M.screen); mid.position.set(0.0, 1.0, zf + 0.58); mid.rotation.x = -0.35; g.add(mid);
    /* seats, driver on +x */
    var mkSeat = function (x) {
      var s = new THREE.Group();
      var cushion = TXT.roundedBox(0.54, 0.16, 0.52, 0.06, M.seat); cushion.position.set(0, 0.5, 0); s.add(cushion);
      var back = TXT.roundedBox(0.54, 0.78, 0.14, 0.06, M.seat); back.position.set(0, 0.94, 0.28); back.rotation.x = 0.16; s.add(back);
      var hr = TXT.roundedBox(0.32, 0.22, 0.12, 0.05, M.seatStitch); hr.position.set(0, 1.44, 0.35); s.add(hr);
      var ped = TXT.roundedBox(0.24, 0.42, 0.28, 0.03, M.dash); ped.position.set(0, 0.21, 0); s.add(ped);
      s.position.set(x, 0, zf + 1.2);
      return s;
    };
    g.add(mkSeat(0.55)); g.add(mkSeat(-0.55));
    /* the wheel on its column, raked toward the seat */
    var col = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.05, 0.55, 14), M.wheel);
    col.position.set(0.55, 0.98, zf + 0.62); col.rotation.x = -0.95; g.add(col);
    var wheel = new THREE.Mesh(new THREE.TorusGeometry(0.25, 0.026, 14, 56), M.wheel);
    wheel.position.set(0.55, 1.12, zf + 0.82); wheel.rotation.x = 0.62; g.add(wheel);
    [0, 2.1, 4.2].forEach(function (a) {
      var sp = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.03, 0.02), M.wheel);
      sp.position.copy(wheel.position); sp.rotation.set(0.62, 0, a); sp.translateX(0.11); g.add(sp);
    });
    var hub = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.05, 20), M.wheel); hub.position.copy(wheel.position); hub.rotation.x = 0.62 + Math.PI / 2; g.add(hub);
    /* pedals under the wheel, nobody's feet on them */
    [0.45, 0.62].forEach(function (x) { var p = TXT.roundedBox(0.08, 0.02, 0.2, 0.01, M.arm); p.position.set(x, 0.2, zf + 0.55); p.rotation.x = -0.5; g.add(p); });
    /* a dim warm dome over the seats */
    var dome = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.02, 0.14), M.cabGlow); dome.position.set(0, H - 0.04, zf + 1.3); g.add(dome);
    var pl = new THREE.PointLight(0xffc98a, o.dome != null ? o.dome : 2.2, 4.0, 2); pl.position.set(0, H - 0.2, zf + 1.4); g.add(pl);
    if (o.observer && K) {
      var p = K.make('person', { seed: o.observerSeed || 4, pose: 'stand', role: 'worker', hat: 'none' });
      /* the kit person stands; a seated observer is posed by lowering it so the hips meet the
       * cushion and hiding the legs in the footwell shadow is left to the camera */
      p.position.set(-0.55, 0.52 - 0.9, zf + 1.18); p.rotation.y = Math.PI; g.add(p);
    }
    g.userData.wheel = [0.55, 1.12, zf + 0.82];
    g.userData.seat = [0.55, 0.6, zf + 1.2];
    g.userData.windshield = zf;
    return g;
  };

  /* A world point to frame CSS px, through the frame's own camera, for leaders and labels that
   * have to land on what they name. */
  N.project = function (THREE, R, p) {
    R.camera.updateMatrixWorld(true);
    var v = new THREE.Vector3(p[0], p[1], p[2]).project(R.camera);
    return [(v.x + 1) / 2 * N.W, (1 - v.y) / 2 * N.H];
  };

  /* THE DECK'S SHELL, kept here rather than typed into nine frames. */
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
  /* Refuses a black render, paints it onto the frame's art canvas, hands the context back for
   * TXDECK.finish, which every frame calls itself, last. */
  N.develop = function (shot, glCanvas) {
    if (!shot || !shot.ok) throw new Error("the GPU frame came back black: " + JSON.stringify(shot));
    var cx = document.getElementById("art").getContext("2d");
    cx.scale(2, 2);
    cx.drawImage(glCanvas, 0, 0, N.W, N.H);
    return cx;
  };

  global.FORTYFIVE = N;
})(this);
