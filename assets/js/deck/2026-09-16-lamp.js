/* lamp.js — the desk lamp chassis, built for carousel No. 26R (2026-09-16).
 *
 * WHAT THIS IS. The deck "IT WAS BUILT TO NOT TELL YOU" is shot at one desk in Arlington after
 * dark. Nine frames share one lamp, one set of materials and one way of seating type, and this
 * file is those three things and nothing else. Every frame's COMPOSITION is written per frame.
 *
 * THE WORLD. A ruled sheet on a desk under a single lamp. The room beyond the pool is dark and
 * stays dark. The camera moves through that one space across the deck: inside the page, back to
 * the desk, out to the room, across to a second room with the same lamp moved, and down to the
 * page again. Nothing in the deck is lit by anything but this lamp.
 *
 * THE MOTIF. The answer line is EMPTY on all nine frames. The only mark the machine ever makes
 * is one short tick in the margin, and it changes state across the deck: one tick, then two
 * rooms' worth, then the two funders' marks, then nothing on the last frame. That is the
 * argument drawn rather than captioned.
 *
 * WHAT THIS IS NOT. There is no drawFrame() here and there never will be. A shared projection
 * helper is house furniture. A shared draw-the-whole-slide is a template, and
 * scripts/carousel/deck_chassis.py measures the difference. This file hands a frame primitives.
 * The frame decides what to build from them.
 *
 * LOAD ORDER: noise.js, txtype.js, txcolor.js, txpost.js, txdeck.js, then this.
 */
(function (global) {
  "use strict";

  if (!global.TXDECK) throw new Error("deck/lamp.js needs txdeck.js loaded first");

  /* ------------------------------------------------------------------ the deck
   *
   * ONE LIGHT, NINE FRAMES, DECLARED HERE AND NOWHERE ELSE.
   *
   * az 64, el 26. THE LAMP IS UP AND TO THE RIGHT AND EVERY CAST RUNS DOWN AND TO THE LEFT.
   * Say it in those words because that is the sentence a frame author can check a drawing
   * against, where "az 64" is not.
   *
   * The ground is `night`, the material is `panel` and the accent is `dusk_gold`, all three
   * straight out of config/brand.yaml. The lamp IS the accent, which is why the accent appears
   * on every frame without ever being decoration: it is the light source.
   */
  TXDECK.declare({
    world: "lamp",
    light: { az: 64, el: 26, keyToFill: 7.0 },
    ground: "#08060F",          // night
    material: "#191530",        // panel
    accent: "#E0956A",          // dusk_gold, and it is the lamp itself
    grade: TXDECK.DUSK_GRADE
  });

  var L = {};
  var W = 1080, H = 1350;

  /* THE DECK'S TWO RAMPS, built once and handed to every frame, which is most of what makes
   * nine frames look cut from one piece of stock.
   *
   * TWO, not one, and the first build of this chassis had one and was wrong. A single ramp off
   * `panel` (#191530, a violet) made the PAPER violet, because a sheet drawn from steps 3 and 6
   * of a violet ramp is a violet sheet whatever the lamp does to it afterwards. Paper under a
   * tungsten lamp is warm and slightly green-grey in its shadows, not lavender.
   *
   * ROOM is the world: the desk, the walls, the furniture, everything the lamp barely reaches.
   * STOCK is paper: derived from `caliche` (#E4D8C3), which config/brand.yaml already calls
   * "body text on dark, and the raised surface on paper". One material, two jobs, which is the
   * note that palette carries about itself.
   */
  L.RAMP  = TXDECK.ramp(9, { Lmin: 0.04, Lmax: 0.62 });
  L.STOCK = TXDECK.ramp(9, { base: "#E4D8C3", Lmin: 0.17, Lmax: 0.93,
                             ambientHue: 96, drift: 10, chroma: 0.72 });
  L.pick  = function (i) { return TXDECK.pick(L.RAMP,  i); };
  L.paper = function (i) { return TXDECK.pick(L.STOCK, i); };

  /* --------------------------------------------------------------------- pool
   *
   * THE LAMP'S LIGHT ON A SURFACE. Every lit thing in this deck is lit by a call to this, so
   * the falloff is the same everywhere and the deck has one lamp rather than nine.
   *
   * A pool is an ellipse because the lamp is off to one side and light lands on a plane as a
   * conic section. A circle here is the tell that nobody thought about where the lamp is.
   */
  L.pool = function (cx, o) {
    var x = o.x, y = o.y, r = o.r, squash = o.squash == null ? 0.52 : o.squash;
    var strength = o.strength == null ? 1 : o.strength;

    function paint(g2) {
      g2.save();
      g2.translate(x, y);
      g2.rotate(o.rot || -0.12);
      g2.scale(1, squash);
      var g = g2.createRadialGradient(0, 0, r * 0.04, 0, 0, r);
      /* Four stops, not two. A two stop radial is the gradient a screen does when nobody
       * decided anything, and it is what the judges kept calling "an object in a void". */
      g.addColorStop(0.00, "rgba(255,226,186," + (0.95 * strength) + ")");
      g.addColorStop(0.16, "rgba(240,187,133," + (0.62 * strength) + ")");
      g.addColorStop(0.46, "rgba(178,122,88,"  + (0.26 * strength) + ")");
      g.addColorStop(0.74, "rgba(86,62,60,"    + (0.09 * strength) + ")");
      g.addColorStop(1.00, "rgba(8,6,15,0)");
      g2.fillStyle = g;
      g2.beginPath(); g2.arc(0, 0, r, 0, Math.PI * 2); g2.fill();
      g2.restore();
    }

    /* THE RESERVE IS PUNCHED OUT OF THE LIGHT, NOT PAINTED OVER IT.
     *
     * The first build of this deck measured the reserve, handed it to the desk grain, and then
     * let the pool wash straight across the headline. The QA harness caught it as a worst point
     * contrast of 1.6 on frame 1 against a 4.5 line, which is the correct answer: a reserve
     * that only some of the art respects is not a reserve.
     *
     * The pool is drawn into an offscreen, the type's rects are punched out of it with a
     * feathered destination-out, and the result is composited with `lighter`. The light then
     * simply does not fall where the words are, which is a lighting decision and not a plate.
     * A plate ADDS an opaque thing behind type. This REMOVES light from in front of it.
     */
    if (o.reserve && o.reserve.length) {
      var layer = TXDECK.offscreen(W, H, function (g2) {
        paint(g2);
        /* DITHER THE LAYER, and this line is the whole reason the reserve path exists as an
         * offscreen at all rather than being free.
         *
         * A radial gradient painted straight onto the frame is dithered once at the end by the
         * deck's grade. Painted into an OFFSCREEN and composited back, it is quantised to 8 bit
         * BEFORE the grade ever sees it, and a wide shallow falloff quantised to 8 bit has
         * visible steps in it. On frame 2 one of those steps ran horizontally through the line
         * "Context-Aware Conversational Tutors" and the QA harness reported the document's own
         * title as struck by a drawn rule. It was struck by a gradient band, which is worse,
         * because a rule is at least meant to be there. Bisecting the frame found it: with the
         * pool removed the frame passed clean.
         *
         * Ordered noise at plus or minus one level breaks the step up below the eye and below
         * the edge detector, for the cost of one pass over the layer. */
        var idata = g2.getImageData(0, 0, W * 2, H * 2);
        var px = idata.data;
        for (var q3 = 0; q3 < px.length; q3 += 4) {
          if (px[q3 + 3] === 0) continue;
          var n = ((q3 * 1103515245 + 12345) >> 8 & 3) - 1.5;
          px[q3] += n; px[q3 + 1] += n; px[q3 + 2] += n;
        }
        g2.putImageData(idata, 0, 0);
        /* SOFT AND PARTIAL, because a hard full strength hole in a light layer is a dark box,
         * and a dark box behind type is a plate however it was arrived at. The third build of
         * this deck punched at 0.92 with a 40 px feather and put a visible dark rounded rect
         * behind the site line on frame 3 and the footnote on frame 7. This file's own header
         * had already named that failure ("a plate drawn in the negative") and the code did it
         * anyway. Light DIMS toward the words. It is not removed from around them. */
        TXDECK.punch(g2, o.reserve, { feather: o.feather == null ? 96 : o.feather,
                                      strength: o.punch == null ? 0.50 : o.punch });
      });
      cx.save();
      cx.globalCompositeOperation = "lighter";
      cx.drawImage(layer, 0, 0, W, H);
      cx.restore();
      return;
    }

    cx.save();
    cx.globalCompositeOperation = "lighter";
    paint(cx);
    cx.restore();
  };

  /* --------------------------------------------------------------------- quiet
   *
   * Draw anything with the type's reserve punched out of it. For the passes that CAN'T consult
   * a mask as they go: a ruled line that would run through a quote, a bezel that would cross a
   * dek, a sheet edge that would strike the site line. The art stops at the words instead of
   * the words sitting on a box.
   */
  L.quiet = function (cx, reserve, draw, opts) {
    opts = opts || {};
    if (!reserve || !reserve.length) { draw(cx); return; }
    var layer = TXDECK.offscreen(W, H, function (g2) {
      draw(g2);
      TXDECK.punch(g2, reserve, { feather: opts.feather == null ? 26 : opts.feather,
                                  strength: opts.strength == null ? 1 : opts.strength });
    });
    cx.drawImage(layer, 0, 0, W, H);
  };

  /* --------------------------------------------------------------------- desk
   *
   * The desk plane, with grain that runs along it and dies as it leaves the pool. The grain is
   * multiplied by the type reserve so the field never fights a headline.
   */
  L.desk = function (cx, o) {
    var y0 = o.y, mask = o.mask || function () { return 1; };
    var g = cx.createLinearGradient(0, y0, 0, H);
    g.addColorStop(0, L.pick(2));
    g.addColorStop(1, L.pick(0));
    cx.fillStyle = g; cx.fillRect(0, y0, W, H - y0);

    /* the grain, 4200 short strokes along the desk's length, reserved around every line box */
    var R = TX.rng(o.seed || 41);
    for (var i = 0; i < 4200; i++) {
      var x = R() * W, y = y0 + R() * (H - y0);
      var k = mask(x, y);
      if (k < 0.5) continue;
      /* value falls with distance from the lamp, so the grain is a lighting cue and not noise */
      var d = Math.hypot(x - (o.lampX || 760), y - (o.lampY || y0 + 120)) / 900;
      var a = Math.max(0, 0.11 - d * 0.085) * k;
      if (a <= 0.002) continue;
      cx.fillStyle = (R() > 0.42 ? "rgba(226,190,150," : "rgba(4,3,8,") + a.toFixed(3) + ")";
      cx.fillRect(x, y, 5 + R() * 22, 0.9);
    }
  };

  /* -------------------------------------------------------------------- sheet
   *
   * A SHEET OF RULED PAPER, lying on the desk, lit by the pool rather than painted pale.
   *
   * The sheet is NEVER filled with a flat light grey. That is what made the first product's
   * frame 1 read as a white box: a pale fill on a dark ground is a plate whatever it is a
   * picture of. It is filled with the ramp and then the pool is drawn over it, so its value
   * comes from the light.
   */
  L.sheet = function (cx, o) {
    var x = o.x, y = o.y, w = o.w, h = o.h, rot = o.rot || 0;
    cx.save();
    cx.translate(x + w / 2, y + h / 2); cx.rotate(rot); cx.translate(-w / 2, -h / 2);

    TXDECK.contact(cx, { x: w / 2, y: h - 2, w: w * 0.92, h: h * 0.05, height: 6,
                         ambient: 0.40, contact: 0.60, ambientBlur: 22, contactBlur: 6 });

    /* The sheet's OWN value runs from mid to low across the page, and the LAMP is what lifts
     * the lit end. A sheet filled pale and then lit is a plate with a gradient on it. */
    var g = cx.createLinearGradient(0, 0, w * 0.5, h);
    g.addColorStop(0, L.paper(o.lit == null ? 5 : o.lit));
    g.addColorStop(1, L.paper(o.shade == null ? 1 : o.shade));
    cx.fillStyle = g; cx.fillRect(0, 0, w, h);

    /* the tooth of the stock, so a large fill is never flat at 100 percent */
    var R = TX.rng(o.seed || 7);
    for (var i = 0; i < 2600; i++) {
      var px = R() * w, py = R() * h;
      cx.fillStyle = R() > 0.5 ? "rgba(255,246,228,0.040)" : "rgba(38,30,22,0.070)";
      cx.fillRect(px, py, 1.6, 1.2);
    }
    cx.restore();
    return { x: x, y: y, w: w, h: h, rot: rot };
  };

  /* --------------------------------------------------------------------- rule
   *
   * One ruled line of the pad. `answer: true` is THE line the deck never fills, drawn heavier
   * so a reader's eye lands on it and finds nothing there.
   */
  L.rule = function (cx, o) {
    cx.save();
    cx.strokeStyle = o.answer ? "rgba(224,149,106,0.62)" : "rgba(58,52,44,0.26)";
    cx.lineWidth = o.answer ? 3.2 : 1.5;
    cx.beginPath(); cx.moveTo(o.x0, o.y); cx.lineTo(o.x1, o.y); cx.stroke();
    cx.restore();
  };

  /* ------------------------------------------------------------------ working
   *
   * A student's handwriting as TOKEN STROKES and never letterforms, so the frame prints no word
   * and no numeral that no source contains. The compute-not-generate law reaches the artwork:
   * a drawn glyph on a page is a published numeral if it is legible.
   */
  L.working = function (cx, o) {
    var R = TX.rng(o.seed || 101);
    cx.save();
    cx.strokeStyle = o.ink || "rgba(26,22,20,0.72)";
    cx.lineCap = "round";
    for (var i = 0; i < (o.lines || 7); i++) {
      var y = o.y + i * (o.step || 52);
      var x = o.x + R() * 18;
      var end = o.x + (o.min || 280) + R() * (o.jitter || 420);
      while (x < end) {
        var w = 9 + R() * 26;
        cx.lineWidth = (o.weight || 3.4) + R() * 1.8;
        cx.beginPath();
        cx.moveTo(x, y + (R() - 0.5) * 2.4);
        cx.bezierCurveTo(x + w * 0.35, y - 5 - R() * 4,
                         x + w * 0.65, y + 4 + R() * 4,
                         x + w,        y + (R() - 0.5) * 2.4);
        cx.stroke();
        x += w + 3 + R() * 6;
      }
    }
    cx.restore();
  };

  /* --------------------------------------------------------------------- tick
   *
   * THE MOTIF. The machine's entire contribution to a page, one short mark in the margin. It is
   * the accent at full strength and it is the only thing in the deck drawn in that colour that
   * is not the lamp, which is the point: the hint and the light are the same substance.
   */
  L.tick = function (cx, o) {
    var w = o.w == null ? 9 : o.w, h = o.h == null ? 46 : o.h;
    cx.save();
    cx.shadowColor = "rgba(224,149,106,0.85)";
    cx.shadowBlur = o.glow == null ? 26 : o.glow;
    cx.fillStyle = "#E0956A";
    cx.fillRect(o.x, o.y, w, h);
    cx.restore();
  };

  /* --------------------------------------------------------------------- room
   *
   * The dark beyond the pool. Atmospheric perspective toward the ground colour, so a shape
   * further from the lamp is not merely smaller, it is closer to the dark.
   */
  L.room = function (cx, o) {
    /* ATMOSPHERIC PERSPECTIVE, and the first build got the direction right and the AMOUNT
     * wrong: every row mixed so far toward the ground colour that the near row was already
     * within 3 L* of the wall and the room read as an empty black rectangle. A depth cue that
     * takes the nearest object to within noise of the background has not created depth, it has
     * deleted the subject. The near row now starts well clear of the wall and the falloff is
     * gentler, so the room still recedes and the reader can still see it recede.
     */
    var layers = o.layers || [];
    var n = Math.max(1, layers.length);
    var rim = o.rim == null ? "rgba(224,168,120,0.30)" : o.rim;
    for (var i = 0; i < layers.length; i++) {
      var t = i / n;
      cx.save();
      cx.fillStyle = TXC.mixOklab(L.pick(5), "#08060F", 0.20 + t * 0.52);
      cx.beginPath();
      layers[i](cx);
      cx.restore();
      /* A RIM on the key side of the two nearest rows. Without it a silhouette on a dark ground
       * is a hole, which is what "an object in a void" actually looks like.
       *
       * IT IS A CLIP AND NEVER A STROKE. The first build stroked the layer's whole path, which
       * outlines every rect on all four sides and turns a room of furniture into a wireframe
       * diagram of a room of furniture. That is the "diagram of a place" the judges named, drawn
       * by the very call that was meant to cure it. Clipping to the shapes and painting a thin
       * band along the top edge lights the surface the lamp can actually reach.
       */
      if (i < 3) {
        cx.save();
        cx.beginPath();
        layers[i](cx);
        cx.clip();
        cx.globalCompositeOperation = "lighter";
        cx.fillStyle = rim;
        for (var b = 0; b < 40; b++) {
          cx.globalAlpha = Math.max(0, (1 - b / 40)) * (0.5 - i * 0.14);
          cx.fillRect(0, 560 + i * 104 + b * 0.9, 1080, 1.2);
        }
        cx.restore();
      }
    }
  };

  /* -------------------------------------------------------------------- glow
   *
   * A screen's light, the one OTHER emitter the world allows and only in the second room,
   * because a police training terminal is a lit thing. Cool against the lamp's warm so the two
   * rooms read as different without the deck changing stock.
   */
  L.glow = function (cx, o) {
    cx.save();
    cx.globalCompositeOperation = "lighter";
    var g = cx.createRadialGradient(o.x, o.y, 2, o.x, o.y, o.r);
    g.addColorStop(0.0, "rgba(150,186,226,0.62)");
    g.addColorStop(0.35, "rgba(96,132,182,0.24)");
    g.addColorStop(1.0, "rgba(8,6,15,0)");
    cx.fillStyle = g;
    cx.beginPath(); cx.arc(o.x, o.y, o.r, 0, Math.PI * 2); cx.fill();
    cx.restore();
  };

  /* ---------------------------------------------------------------- falloff
   *
   * THE LAMP DYING BEFORE THE FRAME EDGE, and it exists for a composition reason with a
   * physical justification rather than the other way round.
   *
   * `TXLAYOUT.BANDS` gives the furniture the top and bottom 130 px, and says a primary image
   * may run under them ONLY WHERE IT IS KEPT QUIET. On the two room frames the foreground
   * page's hard left edge ran straight through the claim ids, so half of "c13 c33 TEXAS AI
   * DOCKET" sat on lit paper and half on dark desk, and the QA harness reported the edge
   * running through the letterforms. It was right.
   *
   * A scrim over the band would be a plate. This is the lamp: on the room frames the camera is
   * further back, the near edge of the desk is past the pool, and light falls off with
   * distance. Applying that falloff quiets the band, removes the edge, and is true to the
   * world rather than a repair laid on top of it.
   */
  L.falloff = function (cx, o) {
    o = o || {};
    var from = o.from == null ? 1140 : o.from;
    var to = o.to == null ? H : o.to;
    var g = cx.createLinearGradient(0, from, 0, to);
    g.addColorStop(0, "rgba(8,6,15,0)");
    g.addColorStop(0.55, "rgba(8,6,15," + (o.mid == null ? 0.72 : o.mid) + ")");
    g.addColorStop(1, "rgba(8,6,15," + (o.end == null ? 0.96 : o.end) + ")");
    cx.save();
    cx.fillStyle = g;
    cx.fillRect(0, from, W, to - from);
    cx.restore();
  };

  /* ------------------------------------------------------------------- shade
   *
   * The lamp's own shade and arm, drawn as a silhouette against its own light. It is the one
   * object that can appear at the frame edge on any frame and tell the reader where the light
   * comes from, which is the cheapest continuity device this deck has.
   */
  L.shade = function (cx, o) {
    var x = o.x, y = o.y, s = o.s == null ? 1 : o.s;
    cx.save();
    cx.translate(x, y); cx.rotate(o.rot || 0); cx.scale(s, s);
    cx.fillStyle = L.pick(1);
    cx.beginPath();
    cx.moveTo(-96, 0); cx.lineTo(96, 0); cx.lineTo(54, -78); cx.lineTo(-54, -78);
    cx.closePath(); cx.fill();
    /* the lit inner lip, the only part of the shade the lamp reaches */
    cx.fillStyle = "rgba(240,196,146,0.42)";
    cx.fillRect(-96, -5, 192, 5);
    cx.strokeStyle = L.pick(2); cx.lineWidth = 11;
    cx.beginPath(); cx.moveTo(0, -78); cx.lineTo(0, -150); cx.stroke();
    cx.restore();
  };

  global.TXLAMP = L;
})(typeof window !== "undefined" ? window : globalThis);
