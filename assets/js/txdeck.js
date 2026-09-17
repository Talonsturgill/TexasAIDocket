/* txdeck.js — the deck chassis base. ONE light, ONE material vocabulary, ONE way of seating
 * type, ONE grade, declared once and shared by all nine frames.
 *
 * WHY THIS EXISTS (2026-09-16, owner). The artwork was "not good enough", the slides "don't
 * really flow together", and each frame looked "like somebody went and threw some text boxes
 * on a page". Twenty six decks shipped that way. The measurements behind the diagnosis:
 *
 *   - txpost.js, the film grade, was loaded by 1 slide out of 205. The sibling product loads
 *     its own copy on 127 of 127. The finishing pass that separates drawn shapes from a
 *     graded still was in this repo the whole time and was never called.
 *   - txcolor.js, the OKLCH ramp builder, was loaded by 1 slide out of 205, against 118 of 127.
 *   - Every frame reached into a permanent bin of finished parts (txobjects, txfig) and placed
 *     them. A bin of finished parts assembled per frame is the definition of the clip art the
 *     judges kept naming. The sibling writes a NEW chassis per deck, named for that deck's
 *     world, and all nine frames draw from it.
 *   - The deck's own value track on 2026-09-16 was 77.8, 77.5, 51.0, 34.1, 45.9, 20.8, 77.5,
 *     43.5, 13.0. Frame 6 to frame 7 is a 57 point jump in one swipe. The scorer called that
 *     "a genuine value arc" and gave it credit, because nothing measured adjacency.
 *
 * WHAT THIS IS. The three invariants a deck cannot hold by good intentions, in one file that
 * every frame loads. A run writes its own chassis at `assets/js/deck/<date>-<world>.js`, that chassis
 * calls `TXDECK.declare` exactly once, and the nine frames then share a light, a ramp, a
 * reserve discipline and a grade BY CONSTRUCTION rather than by nine separate acts of care.
 *
 * WHAT THIS IS NOT. There is no drawFrame() here and there never will be, and a run's own
 * chassis may not add one. A shared projection helper is house furniture. A shared
 * drawTheWholeSlide is a template, and `scripts/carousel/deck_chassis.py` measures the
 * difference. This file hands a frame primitives. The frame decides what to build from them.
 *
 * LOAD ORDER, stated rather than discovered:
 *     noise.js, txcolor.js, txpost.js, txdeck.js, deck/<date>-<world>.js, then the frame's own code.
 * txdeck throws on load if txcolor or txpost is missing, because the failure it prevents is a
 * frame that renders ungraded and looks fine in isolation.
 *
 * THE CONTRACT A FRAME KEEPS, and each line is a gate:
 *     1. load the deck's chassis, the same one as the other eight
 *     2. draw the image before a line of type exists
 *     3. seat type in a RESERVE the art left, never on a plate
 *     4. call TXDECK.finish(cx) as the last thing that touches the art canvas
 */
(function (global) {
  "use strict";

  if (!global.TXC) throw new Error("txdeck.js needs txcolor.js loaded first");
  if (!global.TXPOST) throw new Error("txdeck.js needs txpost.js loaded first");

  var TXDECK = {};
  var DECL = null;

  /* ------------------------------------------------------------------ declare
   *
   * ONE DECLARATION PER DECK, AND IT LIVES IN THE CHASSIS FILE.
   *
   * Coherence is structural here rather than checked. There is exactly one file that declares
   * the light, so nine frames can't hold nine lights. A frame that calls declare() again with
   * different values THROWS, which fails that frame's render loudly, rather than shipping a
   * deck whose seventh frame is lit from the other side.
   *
   * Calling it twice with the SAME values is fine, because the chassis is loaded once per
   * frame and each frame re-executes it.
   */
  TXDECK.declare = function (d) {
    if (!d || typeof d !== "object") throw new Error("TXDECK.declare needs the deck object");
    var need = ["world", "light", "ground", "material", "accent", "grade"];
    for (var i = 0; i < need.length; i++) {
      if (d[need[i]] == null) throw new Error("TXDECK.declare is missing '" + need[i] + "'");
    }
    if (typeof d.light.az !== "number" || typeof d.light.el !== "number") {
      throw new Error("TXDECK.declare light needs numeric az and el");
    }
    var frozen = JSON.stringify(d);
    if (DECL && JSON.stringify(DECL) !== frozen) {
      throw new Error("TXDECK.declare called twice with different decks. One deck, one light, " +
                      "one grade. The chassis declares it and a frame may not override it.");
    }
    DECL = JSON.parse(frozen);
    if (global.document && document.body) TXDECK.stamp();
    return DECL;
  };

  TXDECK.deck = function () {
    if (!DECL) throw new Error("no deck declared. The chassis must call TXDECK.declare first.");
    return DECL;
  };

  /* The declaration, onto the body, so the gate reads what the browser actually ran rather
   * than what the source appears to say. Same shape as the contact and ink declarations. */
  TXDECK.stamp = function () {
    if (!global.document || !document.body) return;
    document.body.setAttribute("data-deck", JSON.stringify(TXDECK.deck()));
  };

  /* -------------------------------------------------------------------- light
   *
   * ONE LIGHT, NINE FRAMES, DECLARED ONCE.
   *
   * lightVec(az, el) = [cos(el)sin(az), -cos(el)cos(az), sin(el)] in SCREEN space with +y DOWN.
   * An azimuth of 76 and an elevation of 12 gives x = +0.949, y = -0.237, so the key is upper
   * right and every cast runs to the lower left. Say it in the chassis header in those words,
   * because "the light is upper right" is a sentence a frame author can check a drawing against
   * and "az 76" is not.
   */
  TXDECK.lightVec = function () {
    var L = TXDECK.deck().light;
    var a = L.az * Math.PI / 180, e = L.el * Math.PI / 180;
    return [Math.cos(e) * Math.sin(a), -Math.cos(e) * Math.cos(a), Math.sin(e)];
  };

  /* The unit direction a cast shadow runs on screen, which is the light's horizontal component
   * negated. Every shadow in the deck uses this and none of them guesses. */
  TXDECK.castDir = function () {
    var v = TXDECK.lightVec();
    var d = [-v[0], -v[1]];
    var m = Math.hypot(d[0], d[1]) || 1;
    return [d[0] / m, d[1] / m];
  };

  /* How long a cast runs for an object of height h, from the declared elevation. A shadow
   * length that is computed is a shadow that agrees with the eight other frames. */
  TXDECK.castLen = function (h) {
    var e = TXDECK.deck().light.el * Math.PI / 180;
    return h / Math.max(0.08, Math.tan(Math.max(0.02, e)));
  };

  /* --------------------------------------------------------------------- ramp
   *
   * The deck's material ramp, dark to light, built in OKLCH off the declared material so that
   * shadow drifts cool and light drifts warm by the numbers rather than by eye. Every frame
   * calls this and every frame gets the same steps, which is most of what makes nine frames
   * look like they were cut from one piece of stock.
   */
  TXDECK.ramp = function (steps, opts) {
    var d = TXDECK.deck();
    opts = opts || {};
    var keyHue = opts.keyHue != null ? opts.keyHue : TXC.hexToOklch(d.accent).H;
    return TXC.ramp(opts.base || d.material, {
      steps: steps || 7,
      Lmin: opts.Lmin != null ? opts.Lmin : 0.06,
      Lmax: opts.Lmax != null ? opts.Lmax : 0.82,
      keyHue: keyHue,
      ambientHue: opts.ambientHue != null ? opts.ambientHue : 268,
      chroma: opts.chroma != null ? opts.chroma : 1,
      drift: opts.drift != null ? opts.drift : 18
    });
  };

  /* A clamped picker, so a frame indexing past either end gets the end rather than undefined
   * and a black hole where a fill should be. */
  TXDECK.pick = function (ramp, i) {
    return ramp[Math.max(0, Math.min(ramp.length - 1, Math.round(i)))];
  };

  /* ------------------------------------------------------------- type seating
   *
   * NO PLATE, EVER. This is the whole answer to "text boxes thrown on a page".
   *
   * The 2026-09-16 deck put an opaque rect behind the headline on six frames of nine, and the
   * source comment beside one of them reads "the plate is the critic's own fix for the
   * placeholder-bar reading". A critic complained that the type sat badly and the repair was
   * more plate. A plate is what you reach for when the art underneath was drawn without
   * knowing where the type goes.
   *
   * So the art is told where the type goes BEFORE it draws. lineBoxes measures the real
   * rendered line boxes of the real fitted type, reserveMask turns them into a feathered
   * field the generators read, and every field, grain, hatch and stipple pass in the deck
   * multiplies its density by it. The type then sits in quiet the picture actually has.
   *
   * Measure AFTER document.fonts.ready and AFTER fitText, or the boxes are the wrong size.
   */
  TXDECK.lineBoxes = function (selector, pad) {
    pad = pad == null ? 16 : pad;
    var out = [];
    var nodes = document.querySelectorAll(selector);
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.hasAttribute("data-decorative")) continue;
      var range = document.createRange();
      range.selectNodeContents(el);
      var rects = range.getClientRects();
      for (var r = 0; r < rects.length; r++) {
        var b = rects[r];
        if (b.width < 2 || b.height < 2) continue;
        out.push([b.left - pad, b.top - pad, b.width + pad * 2, b.height + pad * 2]);
      }
      range.detach && range.detach();
    }
    return out;
  };

  /* fn(x, y) -> 0..1, where 0 is inside a type reserve and 1 is free picture. Feathered, so a
   * field fades out toward the type rather than stopping at a visible rectangle edge, which is
   * a plate drawn in the negative. */
  TXDECK.reserveMask = function (rects, feather) {
    feather = feather == null ? 28 : feather;
    if (!rects || !rects.length) return function () { return 1; };
    return function (x, y) {
      var worst = 1;
      for (var i = 0; i < rects.length; i++) {
        var r = rects[i];
        var dx = Math.max(r[0] - x, 0, x - (r[0] + r[2]));
        var dy = Math.max(r[1] - y, 0, y - (r[1] + r[3]));
        var d = Math.hypot(dx, dy);
        var k = d >= feather ? 1 : (d / feather);
        if (k < worst) worst = k;
        if (worst <= 0) return 0;
      }
      return worst;
    };
  };

  /* Knock the reserve out of an already drawn layer, for passes that can't consult a mask as
   * they go (an image blit, a filter result). destination-out with a feathered radial per rect
   * so the hole has no hard edge. */
  TXDECK.punch = function (ctx, rects, opts) {
    opts = opts || {};
    var feather = opts.feather == null ? 30 : opts.feather;
    var strength = opts.strength == null ? 1 : opts.strength;
    /* A BLURRED ROUNDED RECT PER BOX, NOT A RADIAL GRADIENT.
     *
     * The first build used a radial sized from the rect's diagonal, and it under-covered every
     * WIDE FLAT box, which is the shape a line of text actually is. A 200x30 site line got a
     * radial whose falloff began well inside its own ends, so the middle was punched and the
     * ends were not, and the QA harness correctly reported a ruled line striking the glyphs it
     * was supposed to have been cleared from. A hole for a line of type has to be the shape of
     * a line of type.
     */
    ctx.save();
    ctx.globalCompositeOperation = "destination-out";
    ctx.filter = "blur(" + feather * 0.5 + "px)";
    ctx.fillStyle = "rgba(0,0,0," + strength + ")";
    for (var i = 0; i < rects.length; i++) {
      var r = rects[i];
      var x = r[0] - feather * 0.4, y = r[1] - feather * 0.4;
      var w = r[2] + feather * 0.8, h = r[3] + feather * 0.8;
      var rad = Math.min(h / 2, 18);
      ctx.beginPath();
      if (ctx.roundRect) { ctx.roundRect(x, y, w, h, rad); }
      else {
        ctx.moveTo(x + rad, y);
        ctx.arcTo(x + w, y, x + w, y + h, rad);
        ctx.arcTo(x + w, y + h, x, y + h, rad);
        ctx.arcTo(x, y + h, x, y, rad);
        ctx.arcTo(x, y, x + w, y, rad);
      }
      ctx.fill();
    }
    ctx.restore();
  };

  /* ------------------------------------------------------------------ helpers */

  /* An offscreen canvas at frame scale, drawn into and handed back, for a layer that has to be
   * composited, blurred or masked as a whole. */
  TXDECK.offscreen = function (w, h, draw) {
    var c = document.createElement("canvas");
    var s = 2;
    c.width = w * s; c.height = h * s;
    var g = c.getContext("2d");
    g.scale(s, s);
    draw(g);
    return c;
  };

  /* ------------------------------------------------------------------ contact
   *
   * A TWO PART CONTACT SHADOW, along the declared cast direction.
   *
   * An object that does not touch the ground floats, and a deck of floating objects is the
   * "object in a void" the judges named. One tight dark contact where the object meets the
   * ground, one wide soft ambient around it. Both run down the deck's own cast direction, so
   * every object in all nine frames is lit by the same lamp.
   */
  TXDECK.contact = function (cx, o) {
    var d = TXDECK.castDir();
    var x = o.x, y = o.y, w = o.w, h = o.h == null ? w * 0.22 : o.h;
    var len = o.len == null ? TXDECK.castLen(o.height == null ? w * 0.6 : o.height) : o.len;
    var tint = o.tint || "0,0,0";

    cx.save();
    /* the wide ambient, first and softest */
    cx.filter = "blur(" + (o.ambientBlur == null ? 26 : o.ambientBlur) + "px)";
    cx.fillStyle = "rgba(" + tint + "," + (o.ambient == null ? 0.34 : o.ambient) + ")";
    cx.beginPath();
    cx.ellipse(x + d[0] * len * 0.28, y + d[1] * len * 0.28,
               w * 0.80, h * 1.30, 0, 0, Math.PI * 2);
    cx.fill();
    cx.restore();

    cx.save();
    /* the tight contact, last and darkest, right at the meeting line */
    cx.filter = "blur(" + (o.contactBlur == null ? 4 : o.contactBlur) + "px)";
    cx.fillStyle = "rgba(" + tint + "," + (o.contact == null ? 0.72 : o.contact) + ")";
    cx.beginPath();
    cx.ellipse(x + d[0] * 3, y + d[1] * 3, w * 0.42, h * 0.40, 0, 0, Math.PI * 2);
    cx.fill();
    cx.restore();

    return { dir: d, len: len };
  };

  /* ------------------------------------------------------------------- finish
   *
   * THE LAST THING THAT TOUCHES THE ART CANVAS, ON EVERY FRAME, WITH THE DECK'S ONE GRADE.
   *
   * This is the call that was missing from 204 of 205 shipped slides. It is one line, it takes
   * no arguments a frame has to invent, and `deck_chassis.py` fails the build for any frame
   * that skips it. DOM type sits above the canvas and is never graded, so the grade can be
   * strong without touching legibility.
   */
  TXDECK.finish = function (cx, opts) {
    var d = TXDECK.deck();
    opts = opts || {};
    var g = {};
    for (var k in d.grade) if (Object.prototype.hasOwnProperty.call(d.grade, k)) g[k] = d.grade[k];
    g.w = opts.w || 1080;
    g.h = opts.h || 1350;
    /* Per frame, ONLY the two knobs that are allowed to move: a hero may carry a touch more
     * bloom and a data frame may drop the aberration. Everything else is the deck's. */
    if (opts.bloom != null) g.bloom = opts.bloom;
    if (opts.aberration != null) g.aberration = opts.aberration;
    TXPOST.grade(cx, g);
    if (global.document && document.body) {
      document.body.setAttribute("data-deck-finish", "1");
      TXDECK.stamp();
    }
    return g;
  };

  /* The house grade for the Texas dusk register. A chassis may tune it, and whatever it sets
   * is what all nine frames get. These are the numbers, not a starting point to drift from. */
  TXDECK.DUSK_GRADE = {
    exposure: -0.05,
    saturation: 1.06,
    contrast: 1.14,
    filmic: true,
    lift: [0.014, 0.010, 0.022],     /* shadows to the cool violet of the panel token */
    gain: [1.028, 1.002, 0.968],     /* highlights to dusk gold */
    vignette: 0.22,
    bloom: { threshold: 0.74, strength: 0.30, radius: 9 },
    grain: { amount: 0.045, size: 2, seed: 20260916 },
    aberration: 0,
    dither: true,
    sharpen: 0.32
  };

  global.TXDECK = TXDECK;
})(typeof window !== "undefined" ? window : globalThis);
