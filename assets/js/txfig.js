/* txfig.js — people, at true scale, as pictograms. Builds TXSCENE sprites.
 *
 * WHY THIS EXISTS (2026-09-11). Twenty one decks shipped without a person in any of them, and
 * a deck about a school, a hearing room, a grid crew or a hospital ward read as a diagram of
 * the place with nobody in it. A figure does three things nothing else on a frame can do: it
 * gives every object beside it a size, it gives the reader somewhere to stand, and it turns
 * a statistic into a count of people. This file draws the figure in the register the rest of
 * the illustration system uses, thick round-capped strokes and one ellipse, so a person reads
 * at 54 px in a feed thumb and stays a person, never a doll, at 540.
 *
 * A figure is 1.70 m tall unless told otherwise. Proportions are the eight-head canon, which
 * is what makes a group of them read as adults rather than as toys. `height: 1.2` with
 * `child: true` gives a child the larger head a child has.
 *
 * USAGE
 *
 *   const f = TXFIG.figure({ pose: "walk", height: 1.7, hat: "hard", hold: "clipboard" });
 *   S.shadow(f, { X: 2, Z: 9 });           // TXSCENE places it, as any other sprite
 *   S.sprite(f, { X: 2, Z: 9, inks: inks });
 *
 *   TXFIG.crowd(12, { seed: 7 })           // twelve varied figures for a queue or a lot
 *   TXFIG.figure({ view: "front" })        // the isotype front view for counts and grids
 *
 * POSES (side view, facing +x, mirror with TXSCENE to face the other way):
 *   stand walk stride point wave raise phone carry sit crossed lean
 * Every pose is a set of joint angles, so a new one is a line in POSES and nothing else.
 */
(function (global) {
  "use strict";

  var SC = global.TXSCENE;
  if (!SC) throw new Error("txfig.js needs txscene.js loaded first");

  // Joint angles in degrees. Arms: upper from straight down, positive forward; fore is the
  // elbow flex, positive bends the hand forward. Legs: thigh from straight down, positive
  // forward; shin is the knee flex, positive swings the foot back. [L, R] each.
  var POSES = {
    stand:   { arm: [[-5, 8], [9, 16]],      leg: [[7, 0], [-6, 0]] },
    walk:    { arm: [[-24, 18], [26, 32]],   leg: [[24, 8], [-18, 38]] },
    stride:  { arm: [[-40, 30], [42, 50]],   leg: [[36, 12], [-30, 55]] },
    point:   { arm: [[-4, 8], [92, 0]],      leg: [[7, 0], [-6, 0]] },
    wave:    { arm: [[-4, 8], [158, -28]],   leg: [[7, 0], [-6, 0]] },
    raise:   { arm: [[-4, 8], [172, 6]],     leg: [[7, 0], [-6, 0]] },
    phone:   { arm: [[-4, 8], [14, 142]],    leg: [[7, 0], [-6, 0]] },
    carry:   { arm: [[38, 74], [42, 70]],    leg: [[8, 0], [-7, 0]] },
    crossed: { arm: [[22, 108], [26, 104]],  leg: [[7, 0], [-6, 0]] },
    lean:    { arm: [[-10, 12], [-26, 96]],  leg: [[12, 0], [-14, 0]], tilt: -8 },
    sit:     { arm: [[34, 62], [36, 60]],    leg: [[90, 90], [90, 90]], sit: true }
  };

  function rad(d) { return d * Math.PI / 180; }

  // A limb as one polyline, root at (x0, y0), two segments of lengths l1 and l2.
  function limb(x0, y0, l1, a1, l2, flex, width, fill) {
    var a = rad(a1);
    var kx = x0 + l1 * Math.sin(a), ky = y0 - l1 * Math.cos(a);
    var b = rad(a1 - flex);
    var ex = kx + l2 * Math.sin(b), ey = ky - l2 * Math.cos(b);
    return { part: { type: "line", pts: [[x0, y0], [kx, ky], [ex, ey]], width: width, fill: fill }, end: [ex, ey], knee: [kx, ky] };
  }
  function armLimb(x0, y0, l1, a1, l2, flex, width, fill) {
    // an arm bends the other way: the elbow flex brings the hand forward
    var a = rad(a1);
    var kx = x0 + l1 * Math.sin(a), ky = y0 - l1 * Math.cos(a);
    var b = rad(a1 + flex);
    var ex = kx + l2 * Math.sin(b), ey = ky - l2 * Math.cos(b);
    return { part: { type: "line", pts: [[x0, y0], [kx, ky], [ex, ey]], width: width, fill: fill }, end: [ex, ey], dir: b };
  }

  function figure(o) {
    o = o || {};
    var H = o.height || 1.7;
    var child = !!o.child;
    var pose = POSES[o.pose || "stand"] || POSES.stand;
    var fill = o.fill || "ink";
    var view = o.view || "side";
    var parts = [];

    var headR = (child ? 0.075 : 0.061) * H;
    var shoulderY = (child ? 0.78 : 0.82) * H;
    var hipY = (child ? 0.50 : 0.52) * H;
    var kneeL = (child ? 0.22 : 0.24) * H, shinL = (child ? 0.21 : 0.24) * H;
    var upperL = 0.17 * H, foreL = 0.15 * H;
    var legW = 0.076 * H, armW = 0.064 * H;
    var torsoW = (o.build === "broad" ? 0.30 : 0.26) * H;
    var lift = 0;           // raises the whole skeleton when seated
    var seat = o.seat == null ? 0.45 : o.seat;

    if (view === "front") return front(o, H, headR, fill, child);

    if (pose.sit) {
      lift = seat - 0.02;
      hipY = lift + 0.06 * H; shoulderY = hipY + 0.30 * H;
    }

    // legs first, so the torso covers the hip joint
    var legs = [];
    for (var i = 0; i < 2; i++) {
      var la = pose.leg[i];
      var hx = (i === 0 ? -0.055 : 0.055) * H;
      var L;
      if (pose.sit) {
        // thigh forward along the seat, shin down to the floor
        var kx = hx + kneeL, ky = hipY;
        var fy = 0.03 * H;
        L = { part: { type: "line", pts: [[hx, hipY], [kx, ky], [kx + 0.02 * H, fy]], width: legW, fill: fill }, end: [kx + 0.02 * H, fy] };
      } else {
        L = limb(hx, hipY, kneeL, la[0], shinL, la[1], legW, fill);
      }
      legs.push(L);
      parts.push(L.part);
      // the shoe: a short stroke forward from the ankle
      var ang = pose.sit ? 0 : rad(la[0] - la[1]);
      var footY = Math.max(0.025 * H, L.end[1] - 0.02 * H);
      parts.push({ type: "line", pts: [[L.end[0] - 0.02 * H, footY], [L.end[0] + 0.10 * H * Math.cos(ang) + 0.02 * H, footY]], width: 0.05 * H, fill: fill });
    }

    // torso: a tapered plate with rounded shoulders
    var tilt = rad(pose.tilt || 0);
    var sx = Math.sin(tilt) * (shoulderY - hipY);
    parts.push({ type: "poly", pts: [[-0.085 * H, hipY - 0.03 * H], [0.085 * H, hipY - 0.03 * H],
                 [sx + torsoW / 2 - 0.02 * H, shoulderY], [sx - torsoW / 2 + 0.02 * H, shoulderY]], fill: fill });
    parts.push({ type: "line", pts: [[sx - torsoW / 2 + 0.035 * H, shoulderY], [sx + torsoW / 2 - 0.035 * H, shoulderY]], width: 0.07 * H, fill: fill });
    // neck and head
    var neckTop = shoulderY + 0.06 * H;
    parts.push({ type: "line", pts: [[sx, shoulderY], [sx * 1.15, neckTop]], width: 0.055 * H, fill: fill });
    var headCx = sx * 1.2 + 0.006 * H, headCy = neckTop + headR * 0.95;
    parts.push({ type: "ellipse", cx: headCx, cy: headCy, rx: headR * 0.92, ry: headR, fill: fill });

    // arms, far arm first so the near one reads on top
    var arms = [];
    var order = [0, 1];
    for (var j = 0; j < 2; j++) {
      var k = order[j], aa = pose.arm[k];
      var ax = sx + (k === 0 ? -0.06 : 0.06) * H;
      var A = armLimb(ax, shoulderY - 0.01 * H, upperL, aa[0], foreL, aa[1], armW, fill);
      arms.push(A);
      parts.push(A.part);
    }

    // hats, in the register of the trade rather than of the tourist shop
    if (o.hat === "hard") {
      parts.push({ type: "ellipse", cx: headCx, cy: headCy + headR * 0.55, rx: headR * 1.0, ry: headR * 0.62, fill: o.hatFill || "accent", noShadow: true });
      parts.push({ type: "rect", x: headCx - headR * 1.25, y: headCy + headR * 0.42, w: headR * 2.5, h: headR * 0.16, fill: o.hatFill || "accent", noShadow: true });
    } else if (o.hat === "brim") {
      parts.push({ type: "rect", x: headCx - headR * 0.75, y: headCy + headR * 0.72, w: headR * 1.5, h: headR * 0.55, r: headR * 0.2, fill: fill });
      parts.push({ type: "rect", x: headCx - headR * 1.65, y: headCy + headR * 0.62, w: headR * 3.3, h: headR * 0.14, fill: fill });
    } else if (o.hat === "cap") {
      parts.push({ type: "ellipse", cx: headCx, cy: headCy + headR * 0.45, rx: headR * 0.95, ry: headR * 0.6, fill: fill });
      parts.push({ type: "rect", x: headCx, y: headCy + headR * 0.55, w: headR * 1.6, h: headR * 0.14, fill: fill });
    }

    // things in the near hand
    var hand = arms[1].end;
    if (o.hold === "briefcase") {
      parts.push({ type: "rect", x: hand[0] - 0.02 * H, y: hand[1] - 0.24 * H, w: 0.24 * H, h: 0.18 * H, r: 0.01 * H, fill: fill });
      parts.push({ type: "rect", x: hand[0] + 0.04 * H, y: hand[1] - 0.20 * H, w: 0.12 * H, h: 0.10 * H, fill: "paper", noShadow: true });
    } else if (o.hold === "box") {
      var hx2 = arms[0].end[0], hy2 = arms[0].end[1];
      parts.push({ type: "rect", x: hx2 - 0.02 * H, y: hy2 - 0.05 * H, w: 0.30 * H, h: 0.24 * H, fill: fill });
      parts.push({ type: "rect", x: hx2 + 0.02 * H, y: hy2 + 0.06 * H, w: 0.22 * H, h: 0.02 * H, fill: "paper", noShadow: true });
    } else if (o.hold === "placard") {
      parts.push({ type: "line", pts: [[hand[0], hand[1]], [hand[0] + 0.02 * H, hand[1] + 0.34 * H]], width: 0.025 * H, fill: fill });
      parts.push({ type: "rect", x: hand[0] - 0.20 * H, y: hand[1] + 0.34 * H, w: 0.44 * H, h: 0.30 * H, fill: "paper", stroke: true, strokePx: 2 });
    } else if (o.hold === "clipboard") {
      parts.push({ type: "rect", x: hand[0] - 0.02 * H, y: hand[1] - 0.10 * H, w: 0.16 * H, h: 0.22 * H, fill: "paper", stroke: true, strokePx: 2 });
      parts.push({ type: "rect", x: hand[0] + 0.01 * H, y: hand[1] - 0.06 * H, w: 0.10 * H, h: 0.015 * H, fill: fill, noShadow: true });
      parts.push({ type: "rect", x: hand[0] + 0.01 * H, y: hand[1] - 0.01 * H, w: 0.10 * H, h: 0.015 * H, fill: fill, noShadow: true });
    } else if (o.hold === "phone") {
      parts.push({ type: "rect", x: hand[0] - 0.01 * H, y: hand[1] - 0.02 * H, w: 0.045 * H, h: 0.09 * H, r: 0.006 * H, fill: "paper", noShadow: true });
    } else if (o.hold === "bag") {
      parts.push({ type: "line", pts: [[hand[0], hand[1]], [hand[0] + 0.01 * H, hand[1] - 0.08 * H]], width: 0.02 * H, fill: fill });
      parts.push({ type: "rect", x: hand[0] - 0.08 * H, y: hand[1] - 0.30 * H, w: 0.18 * H, h: 0.22 * H, r: 0.02 * H, fill: fill });
    }

    var s = SC.sprite(parts, { kind: "figure", pose: o.pose || "stand", height: H });
    s.hand = hand;
    s.head = [headCx, headCy];
    return s;
  }

  // The isotype front view: symmetric, no pose, the unit of a count.
  function front(o, H, headR, fill, child) {
    var parts = [];
    var shoulderY = 0.80 * H, hipY = 0.50 * H;
    var torsoW = (o.build === "broad" ? 0.34 : 0.30) * H;
    // legs
    parts.push({ type: "line", pts: [[-0.055 * H, hipY], [-0.06 * H, 0.04 * H]], width: 0.10 * H, fill: fill });
    parts.push({ type: "line", pts: [[0.055 * H, hipY], [0.06 * H, 0.04 * H]], width: 0.10 * H, fill: fill });
    // torso with rounded shoulders
    parts.push({ type: "poly", pts: [[-0.11 * H, hipY - 0.03 * H], [0.11 * H, hipY - 0.03 * H], [torsoW / 2, shoulderY], [-torsoW / 2, shoulderY]], fill: fill });
    parts.push({ type: "line", pts: [[-torsoW / 2 + 0.04 * H, shoulderY], [torsoW / 2 - 0.04 * H, shoulderY]], width: 0.08 * H, fill: fill });
    // arms at the sides, slightly out
    parts.push({ type: "line", pts: [[-torsoW / 2 + 0.01 * H, shoulderY - 0.02 * H], [-torsoW / 2 - 0.03 * H, 0.50 * H]], width: 0.065 * H, fill: fill });
    parts.push({ type: "line", pts: [[torsoW / 2 - 0.01 * H, shoulderY - 0.02 * H], [torsoW / 2 + 0.03 * H, 0.50 * H]], width: 0.065 * H, fill: fill });
    // neck and head
    parts.push({ type: "line", pts: [[0, shoulderY], [0, shoulderY + 0.06 * H]], width: 0.06 * H, fill: fill });
    var headCy = shoulderY + 0.06 * H + headR * 0.95;
    parts.push({ type: "ellipse", cx: 0, cy: headCy, rx: headR * 0.92, ry: headR, fill: fill });
    if (o.hat === "hard") {
      parts.push({ type: "ellipse", cx: 0, cy: headCy + headR * 0.55, rx: headR * 1.0, ry: headR * 0.62, fill: o.hatFill || "accent", noShadow: true });
    }
    var s = SC.sprite(parts, { kind: "figure", pose: "front", height: H });
    s.head = [0, headCy];
    return s;
  }

  // A deterministic small rng so a crowd is the same crowd every render.
  function rng(seed) {
    var t = (seed >>> 0) || 1;
    return function () { t += 0x6D2B79F5; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; };
  }

  // n varied figures, for queues, lots, audiences. Each entry carries a lateral jitter and a
  // mirror flag so `S.sprite(e.sprite, {X: base + e.dx, Z, mirror: e.mirror})` places a crowd.
  function crowd(n, o) {
    o = o || {};
    var r = rng(o.seed || 1);
    var poses = o.poses || ["stand", "walk", "stand", "phone", "crossed", "stride", "stand", "carry"];
    var out = [];
    for (var i = 0; i < n; i++) {
      var child = o.children ? r() < 0.25 : false;
      out.push({
        sprite: figure({ pose: poses[Math.floor(r() * poses.length)], height: child ? 1.1 + r() * 0.3 : 1.55 + r() * 0.3,
                         child: child, build: r() < 0.3 ? "broad" : "normal",
                         hat: o.hats ? o.hats[Math.floor(r() * o.hats.length)] : undefined,
                         hold: o.holds ? o.holds[Math.floor(r() * o.holds.length)] : undefined }),
        dx: (r() - 0.5) * (o.jitter == null ? 0.6 : o.jitter),
        mirror: r() < 0.5
      });
    }
    return out;
  }

  global.TXFIG = { figure: figure, crowd: crowd, POSES: POSES, rng: rng };
})(typeof window !== "undefined" ? window : globalThis);
