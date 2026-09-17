/* nightdraft.js — the chassis for carousel No. 27 (2026-09-17).
 *
 * WHAT THIS IS. The deck "SOFTWARE WRITES THE FIRST DRAFT" follows one sentence from a machine
 * to a Texan, across one continuous reading surface at night. Nine frames share one light, one
 * material vocabulary and one way of seating type, and this file is those three things and
 * nothing else. Every frame's COMPOSITION is written per frame.
 *
 * THE WORLD. A reading surface with a squared front edge, running off both sides of every
 * frame, and one raking light from the upper left. The surface's MATERIAL changes at three
 * declared seams, clinic laminate to home oak to public counter enamel, and the camera height
 * changes with it, so the seams are chapters rather than accidents. The room beyond the light
 * is dark on all nine frames and stays dark. Nothing in this deck is lit from above.
 *
 * THE MOTIF. The EMPTY RULE. A ruled space with nothing set in it, marked by the accent, and it
 * changes state across the deck. Eight empty boxes beside eight search terms on frame 4. A field
 * table with its heads set and every cell blank on frame 5. Three duty holders outlined on frame
 * 7. A keyline that CLOSES on frame 8, around a list that is complete. And on frame 9 the accent
 * is FILLED for the only time in the deck, on a card carrying what a Texan can do. Hollow
 * everywhere the door is not, solid at the one place it is.
 *
 * THE GLYPH LAW, and it is the reason this deck can draw documents at all.
 *
 *   A DRAWN LINE OF TYPE GETS GLYPHS IF AND ONLY IF THIS RUN FETCHED THOSE GLYPHS.
 *
 * The release, the article and the statute are set in real type, verbatim, because those
 * documents were read and are in claims.json. THE PATIENT'S OWN MESSAGE IS THE ONE UNGLYPHED
 * DOCUMENT IN THE DECK. It is drawn with `ruleRun` as hairlines at true line lengths, because
 * no document this run read publishes one word of what such a draft says, and a frame that set
 * glyphs there would be inventing them. Nothing anywhere in nine frames is drawn as a filled
 * bar, a strike or a smudge, because a black field says something was REMOVED and the record
 * says nothing was ever written.
 *
 * THE ONE SCREEN. `tooth`, a halftone dot field at cell 6. It is the deck's stock and it is the
 * same on all nine frames. Cell 6 rather than anything else because it was MEASURED on this
 * deck's own ground and ink at feed scale rather than chosen: out/2026-09-17/screen_ceilings.json
 * prints a black field, a mid field and a white field through seven configurations, and halftone
 * at cell 6 runs 4.0 to 87.0 where hatch at cell 6 caps at 42.6 and stipple at cell 5 caps at
 * 25.2. This deck needs a genuinely bright readable page on a near black ground on five frames,
 * and a halftone is the only screen that can print one.
 *
 * WHAT THIS IS NOT. There is no drawFrame() here and there never will be. A shared projection
 * helper is house furniture. A shared draw-the-whole-slide is a template, and
 * scripts/carousel/deck_chassis.py refuses one by name. This file hands a frame primitives. The
 * frame decides what to build from them.
 *
 * LOAD ORDER: noise.js, txtype.js, txcolor.js, txpost.js, txdeck.js, then this.
 */
(function (global) {
  "use strict";

  if (!global.TXDECK) throw new Error("deck/nightdraft.js needs txdeck.js loaded first");

  /* ------------------------------------------------------------------ the deck
   *
   * ONE LIGHT, NINE FRAMES, DECLARED HERE AND NOWHERE ELSE.
   *
   * az -28, el 22. THE LIGHT COMES FROM THE UPPER LEFT AT 22 DEGREES ABOVE THE SURFACE, SO
   * EVERY OBJECT LAYS ITS CAST DOWN AND TO THE RIGHT AT ABOUT 2.5 TIMES ITS OWN HEIGHT, AND
   * NOTHING IN THIS DECK IS LIT FROM ABOVE. That last clause is the deck's signature and it is
   * also its separation from the hospital deck of September 13th, which lit its rooms from
   * overhead fixtures at standing eye. Say it in those words, because that is the sentence a
   * frame author can check a drawing against, where "az -28" is not.
   *
   * THE PALETTE IS COMPUTED, NOT CHOSEN. out/2026-09-17/palette_measured.json carries the
   * arithmetic. Each role was searched for the point furthest from the 59 hexes of the last
   * eight decks INSIDE the region brand.yaml allows, which is a low chroma ceiling on everything
   * but the accent, because this product's decks are paper and ink and one colour. The line is
   * dE 10.09, the 10th percentile of 20,000 random colours' nearest neighbour in that window.
   *
   *   ground      #051F21  L* 10.0   dE  8.51   the unlit room, a cool dark
   *   material    #0E2B31  L* 15.6            the mid the ROOM ramp is built from
   *   accent      #EFA31D  L* 72.7   dE 39.95   standby amber, and see the accent law above
   *
   * The ground sits UNDER the line and that is stated rather than hidden. Eight decks each
   * carry one near black ground, so that corner of the space is spent and no dark deck clears a
   * p10 line against it. What this deck carries instead is four roles clear of the line and an
   * accent at dE 39.95.
   */
  TXDECK.declare({
    world: "nightdraft",
    light: { az: -28, el: 22, keyToFill: 6.5 },
    ground: "#051F21",
    material: "#0E2B31",
    accent: "#EFA31D",
    grade: {
      exposure: -0.04,
      saturation: 1.05,
      contrast: 1.15,
      filmic: true,
      lift: [0.008, 0.018, 0.020],   /* shadows to the room's cool teal */
      gain: [1.030, 1.004, 0.964],   /* highlights to the standby amber */
      vignette: 0.24,
      bloom: { threshold: 0.76, strength: 0.26, radius: 9 },
      grain: { amount: 0.042, size: 2, seed: 20260917 },
      aberration: 0,
      dither: true,
      sharpen: 0.34
    }
  });

  var N = {};
  var W = 1080, H = 1350;

  /* THE CONSTANT FRONT EDGE. The reading surface's own near edge sits at this y on every one of
   * the nine frames, so the eye keeps one horizontal across the whole swipe. It is the spine
   * the panorama runs along and the single most load bearing number in the deck. */
  N.EDGE = 1096;

  /* THE DECK'S TWO RAMPS, built once and handed to every frame, which is most of what makes
   * nine frames look cut from one piece of stock.
   *
   * TWO, not one, and the reason is the lamp deck's own written lesson. A single ramp off the
   * room's material makes the PAPER that material's hue, because a sheet drawn from steps 3 and
   * 6 of a teal ramp is a teal sheet whatever the light does to it afterwards. Paper under a
   * raking warm light is warm in its lights and cool only in its shadows.
   *
   * ROOM is the world: the surfaces, the furniture, everything the light barely reaches.
   * STOCK is paper: the four drawn documents and nothing else.
   */
  /* THE ROOM RAMP'S TOP END IS 0.78 AND THE FIRST BUILD HAD 0.56, WHICH WAS WRONG BY
   * MEASUREMENT RATHER THAN BY EYE. The probe frame this chassis was built against rendered at
   * a median L* of 2.3 against a planned 30, because every surface in the frame was drawn from
   * the bottom third of a ramp that had no top third. A ramp whose lightest step is still dark
   * cannot light a room, and no amount of pool strength fixes it, because the pool screens ONTO
   * what the ramp already put down. This is the whole reason Phase 10.5 renders one probe frame
   * before the other eight get written. */
  N.ROOM  = TXDECK.ramp(9, { Lmin: 0.03, Lmax: 0.78, ambientHue: 205, drift: 14 });
  N.STOCK = TXDECK.ramp(9, { base: "#BFCBBD", Lmin: 0.15, Lmax: 0.95,
                             ambientHue: 150, drift: 11, chroma: 0.66 });
  N.pick  = function (i) { return TXDECK.pick(N.ROOM,  i); };
  N.paper = function (i) { return TXDECK.pick(N.STOCK, i); };

  /* The inks, so nine frames cannot each pick their own. */
  N.INK   = "#C8DDD7";   /* display type and drawn light-on-dark marks */
  N.DEK   = "#8CADA7";
  N.RULE  = "#6A929A";   /* the furniture, one pale ink on all nine frames */
  N.TONER = "#272310";   /* the type printed ON a drawn page */
  N.AMBER = "#EFA31D";

  /* ------------------------------------------------------------------- pool
   *
   * THE LIGHT LANDING ON A SURFACE. Every lit thing in this deck is lit by a call to this, so
   * the falloff is the same everywhere and the deck has one light rather than nine.
   *
   * The pool is an ELLIPSE rotated toward the cast direction, because light from 22 degrees
   * above a plane lands on it as a conic section. A circle here is the tell that nobody thought
   * about where the light is.
   *
   * `reserve` is a list of line box rects. The light is DIMMED toward them with a wide feather,
   * never removed from around them: a hole punched at full strength is a plate with the sign
   * flipped, which is the defect the lamp deck paid for finding out.
   */
  N.pool = function (cx, o) {
    var x = o.x, y = o.y, r = o.r;
    var squash = o.squash == null ? 0.46 : o.squash;
    var strength = o.strength == null ? 1 : o.strength;
    var layer = TXDECK.offscreen(W, H, function (g2) {
      g2.save();
      g2.translate(x, y);
      g2.rotate(o.rot == null ? 0.16 : o.rot);
      g2.scale(1, squash);
      var g = g2.createRadialGradient(0, 0, r * 0.05, 0, 0, r);
      /* Four stops, not two. A two stop radial is the gradient a screen does when nobody
       * decided anything, and it reads as one. */
      g.addColorStop(0.00, "rgba(236,247,242," + (0.82 * strength) + ")");
      g.addColorStop(0.26, "rgba(206,228,224," + (0.54 * strength) + ")");
      g.addColorStop(0.58, "rgba(140,173,167," + (0.24 * strength) + ")");
      g.addColorStop(1.00, "rgba(5,31,33,0)");
      g2.fillStyle = g;
      g2.beginPath(); g2.arc(0, 0, r, 0, Math.PI * 2); g2.fill();
      g2.restore();
    });
    if (o.reserve && o.reserve.length) {
      TXDECK.punch(layer.getContext("2d"), o.reserve, { feather: 64, strength: 0.72 });
    }
    cx.save();
    cx.globalCompositeOperation = "screen";
    cx.drawImage(layer, 0, 0, W, H);
    cx.restore();
  };

  /* ---------------------------------------------------------------- falloff
   *
   * The light dying toward an edge, which is what lets the furniture band read without a
   * reserve rectangle being laid over the art. The scene keeps its own quiet.
   */
  N.falloff = function (cx, o) {
    var from = o.from == null ? 1150 : o.from;
    var to = o.to == null ? H : o.to;
    var end = o.end == null ? 0.94 : o.end;
    var g = cx.createLinearGradient(0, from, 0, to);
    g.addColorStop(0, "rgba(5,31,33,0)");
    g.addColorStop(1, "rgba(5,31,33," + end + ")");
    cx.save(); cx.fillStyle = g; cx.fillRect(0, from, W, to - from); cx.restore();
  };

  /* The same, from the top, for the kicker band. */
  N.falloffTop = function (cx, o) {
    o = o || {};
    var to = o.to == null ? 210 : o.to;
    var end = o.end == null ? 0.90 : o.end;
    var g = cx.createLinearGradient(0, 0, 0, to);
    g.addColorStop(0, "rgba(5,31,33," + end + ")");
    g.addColorStop(1, "rgba(5,31,33,0)");
    cx.save(); cx.fillStyle = g; cx.fillRect(0, 0, W, to); cx.restore();
  };

  /* ---------------------------------------------------------------- surface
   *
   * A READING SURFACE WITH A SQUARED FRONT EDGE AND A LIT LIP. The deck's spine.
   *
   * `edge` defaults to N.EDGE so a frame has to go out of its way to break the panorama. The
   * lip is 3 px of the material's own light, which is what a squared edge does under a raking
   * key and is also what stops the surface reading as a flat rectangle of colour.
   */
  N.surface = function (cx, o) {
    o = o || {};
    var edge = o.edge == null ? N.EDGE : o.edge;
    var top = o.top == null ? 0 : o.top;
    var lit = o.lit == null ? 3 : o.lit, shade = o.shade == null ? 1 : o.shade;
    var g = cx.createLinearGradient(0, top, 0, edge);
    g.addColorStop(0, N.pick(shade));
    g.addColorStop(1, N.pick(lit));
    cx.save();
    cx.fillStyle = g; cx.fillRect(0, top, W, edge - top);
    /* the lit lip along the squared edge */
    cx.fillStyle = N.pick(lit + 2.2);
    cx.fillRect(0, edge - 3, W, 3);
    /* THE FACE BELOW THE EDGE, falling away from the light but NEVER to black.
     * The probe frame put 19 percent of the frame at L* 3 here, which with the unlit room above
     * made the frame bimodal: 60 percent near black and 40 percent lit, median 4 against a
     * planned 30. A surface the reader is leaning over is the nearest thing in the picture and
     * the nearest thing is never the darkest. It carries the light it is closest to. */
    var fg = cx.createLinearGradient(0, edge, 0, H);
    fg.addColorStop(0, N.pick(Math.max(0, shade + 0.4)));
    fg.addColorStop(1, N.pick(Math.max(0, shade - 0.7)));
    cx.fillStyle = fg;
    cx.fillRect(0, edge, W, H - edge);
    cx.restore();
  };

  /* ------------------------------------------------------------------ sheet
   *
   * A US LETTER SHEET AT TRUE SIZE, 216 by 279 mm, with a hand wobbled edge, a lit top edge and
   * a two part contact under it. Returns its own screen box so a frame can mount DOM type onto
   * it, because type is DOM or SVG in this engine and never canvas.
   *
   * The wobble is what stops it being a rectangle. A sheet of paper on a table is never
   * straight on all four sides and the eye knows it before it can say so.
   */
  N.sheet = function (cx, o) {
    var x = o.x, y = o.y, w = o.w, h = o.h;
    var rot = o.rot == null ? 0 : o.rot;
    var seed = o.seed == null ? 17 : o.seed;
    var R = TX.rng(seed);
    var lit = o.lit == null ? 7 : o.lit, shade = o.shade == null ? 3.4 : o.shade;

    cx.save();
    cx.translate(x + w / 2, y + h / 2);
    cx.rotate(rot);
    cx.translate(-w / 2, -h / 2);

    /* THE TWO PART CONTACT, AT THE MEETING LINE AND NOT AT A CORNER.
     * TXDECK.contact takes the CENTRE of the contact ellipse, so it is handed the middle of the
     * sheet's near edge with the sheet's own thickness. Handing it the rect's origin puts the
     * shadow off the top left corner, which is a sheet floating over its own shadow. */
    TXDECK.contact(cx, { x: w / 2, y: h, w: w * 0.92, h: (o.thick == null ? 4 : o.thick) * 1.6,
                         height: o.thick == null ? 4 : o.thick });

    /* the sheet, wobbled */
    cx.beginPath();
    var steps = 26;
    function edgePt(px, py) { return [px + (R() - 0.5) * 2.2, py + (R() - 0.5) * 2.2]; }
    var p = edgePt(0, 0); cx.moveTo(p[0], p[1]);
    for (var i = 1; i <= steps; i++) { p = edgePt(w * i / steps, 0); cx.lineTo(p[0], p[1]); }
    for (i = 1; i <= steps; i++) { p = edgePt(w, h * i / steps); cx.lineTo(p[0], p[1]); }
    for (i = 1; i <= steps; i++) { p = edgePt(w - w * i / steps, h); cx.lineTo(p[0], p[1]); }
    for (i = 1; i <= steps; i++) { p = edgePt(0, h - h * i / steps); cx.lineTo(p[0], p[1]); }
    cx.closePath();
    var g = cx.createLinearGradient(0, 0, w * 0.55, h);
    g.addColorStop(0, N.paper(lit));
    g.addColorStop(1, N.paper(shade));
    cx.fillStyle = g; cx.fill();

    /* the lit top edge, which is what gives the sheet thickness under a raking key */
    cx.save(); cx.clip();
    cx.fillStyle = N.paper(Math.min(8, lit + 1.4));
    cx.fillRect(0, 0, w, 2.4);
    cx.restore();

    cx.restore();
    return { x: x, y: y, w: w, h: h, rot: rot };
  };

  /* ------------------------------------------------------------------- tooth
   *
   * THE DECK'S ONE SCREEN. A halftone dot field at cell 6, laid over a region and modulated by
   * the tone already under it, so a light passage carries big dots and a dark one carries small
   * ones. This is the deck's stock and it is identical on all nine frames.
   *
   * `mask` is the type reserve. The screen NEVER runs under type, which is the oldest rule in
   * the print register, and the mask is how that is kept without a rectangle.
   */
  N.tooth = function (cx, o) {
    var x = o.x, y = o.y, w = o.w, h = o.h;
    var cell = o.cell == null ? 6 : o.cell;
    var angle = (o.angle == null ? 22 : o.angle) * Math.PI / 180;
    var strength = o.strength == null ? 0.16 : o.strength;
    var mask = o.mask || function () { return 1; };
    var img;
    try { img = cx.getImageData(x * 2, y * 2, Math.max(1, w * 2), Math.max(1, h * 2)); }
    catch (e) { return; }
    var d = img.data, iw = Math.max(1, w * 2);
    function toneAt(px, py) {
      var ix = Math.round((px - x) * 2), iy = Math.round((py - y) * 2);
      if (ix < 0 || iy < 0 || ix >= iw || iy >= Math.max(1, h * 2)) return 0;
      var k = (iy * iw + ix) * 4;
      return (0.2126 * d[k] + 0.7152 * d[k + 1] + 0.0722 * d[k + 2]) / 255;
    }
    cx.save();
    cx.beginPath(); cx.rect(x, y, w, h); cx.clip();
    cx.globalCompositeOperation = "overlay";
    var cos = Math.cos(angle), sin = Math.sin(angle);
    var diag = Math.hypot(w, h);
    for (var u = -diag; u < diag; u += cell) {
      for (var v = -diag; v < diag; v += cell) {
        var px = x + w / 2 + u * cos - v * sin;
        var py = y + h / 2 + u * sin + v * cos;
        if (px < x - cell || px > x + w + cell || py < y - cell || py > y + h + cell) continue;
        var t = toneAt(px, py);
        var m = mask(px, py);
        if (m <= 0.02) continue;
        var r = cell * 0.5 * Math.sqrt(Math.max(0, Math.min(1, t))) * m;
        if (r < 0.25) continue;
        cx.fillStyle = "rgba(255,255,255," + (strength * m) + ")";
        cx.beginPath(); cx.arc(px, py, r, 0, Math.PI * 2); cx.fill();
      }
    }
    cx.restore();
  };

  /* ---------------------------------------------------------------- ruleRun
   *
   * THE UNGLYPHED MESSAGE, AND THE GLYPH LAW IS WHY IT EXISTS.
   *
   * Hairlines at a page's own leading, at TRUE LINE LENGTHS with a ragged right, drawn in the
   * page's own light. This is what the patient's note is drawn as on every frame it appears,
   * because no document this run read publishes one word of it.
   *
   * IT IS NEVER A FILLED BAR. A bar says something was removed. A hairline with a lit lip says
   * a line of type sits here and this run did not read it, which is the true statement.
   */
  N.ruleRun = function (cx, o) {
    var x = o.x, y = o.y, w = o.w;
    var n = o.n == null ? 6 : o.n;
    var leading = o.leading == null ? 22 : o.leading;
    var seed = o.seed == null ? 5 : o.seed;
    var R = TX.rng(seed);
    var ink = o.ink || N.paper(2.2);
    var weight = o.weight == null ? 2.0 : o.weight;
    cx.save();
    for (var i = 0; i < n; i++) {
      var len = w * (o.ragged === false ? 1 : (0.62 + R() * 0.38));
      if (i === n - 1) len = w * (0.34 + R() * 0.24);          /* a last line is short */
      var yy = y + i * leading;
      cx.fillStyle = ink;
      cx.fillRect(x, yy, len, weight);
      /* the lit lip, so the line reads as set type catching the key rather than as a rule */
      cx.fillStyle = o.lip || N.paper(5.6);
      cx.fillRect(x, yy - 0.7, len, 0.7);
    }
    cx.restore();
    return { x: x, y: y, w: w, h: n * leading };
  };

  /* ---------------------------------------------------------------- keyline
   *
   * THE ACCENT, UNFILLED. A 2 px stroke around an empty rule, and it is the deck's motif.
   * Hollow everywhere the door is not.
   */
  N.keyline = function (cx, o) {
    cx.save();
    cx.strokeStyle = N.AMBER;
    cx.lineWidth = o.weight == null ? 2 : o.weight;
    cx.globalAlpha = o.alpha == null ? 0.92 : o.alpha;
    var r = o.radius == null ? 2 : o.radius;
    cx.beginPath();
    if (cx.roundRect) cx.roundRect(o.x, o.y, o.w, o.h, r);
    else cx.rect(o.x, o.y, o.w, o.h);
    cx.stroke();
    cx.restore();
  };

  /* --------------------------------------------------------------- fillCard
   *
   * THE ACCENT, FILLED. This exists so it can be called EXACTLY ONCE in the deck, on frame 9,
   * at the one place a reader has somewhere to go. If a second frame calls it the motif is
   * gone and the deck is making a claim it did not intend.
   */
  N.fillCard = function (cx, o) {
    cx.save();
    cx.fillStyle = N.AMBER;
    cx.globalAlpha = o.alpha == null ? 0.95 : o.alpha;
    var r = o.radius == null ? 3 : o.radius;
    cx.beginPath();
    if (cx.roundRect) cx.roundRect(o.x, o.y, o.w, o.h, r);
    else cx.rect(o.x, o.y, o.w, o.h);
    cx.fill();
    cx.restore();
  };

  /* ------------------------------------------------------------------ panel
   *
   * AN EMISSIVE RECTANGLE, the one other emitter this world allows. It MAY NEVER GLOW WITHOUT
   * CONTENT: a lit rectangle with nothing on it is the placeholder bar this whole system was
   * rebuilt to stop drawing, so the caller passes `content` and this refuses without it.
   */
  N.panel = function (cx, o) {
    if (typeof o.content !== "function") {
      throw new Error("nightdraft.panel: a lit panel with no content is a placeholder bar");
    }
    var x = o.x, y = o.y, w = o.w, h = o.h;
    cx.save();
    /* the bezel, which is object rather than light */
    cx.fillStyle = N.pick(2.2);
    cx.fillRect(x - 7, y - 7, w + 14, h + 14);
    cx.fillStyle = N.pick(4.4);
    cx.fillRect(x - 7, y - 7, w + 14, 2);
    /* the glass */
    var g = cx.createLinearGradient(x, y, x + w * 0.4, y + h);
    g.addColorStop(0, N.paper(3.0));
    g.addColorStop(1, N.paper(1.2));
    cx.fillStyle = g; cx.fillRect(x, y, w, h);
    cx.save(); cx.beginPath(); cx.rect(x, y, w, h); cx.clip();
    o.content(cx, { x: x, y: y, w: w, h: h });
    cx.restore();
    cx.restore();
    return { x: x, y: y, w: w, h: h };
  };

  /* ------------------------------------------------------------------ quiet
   *
   * Draw marks with the type's reserve honoured. Anything drawn inside the callback is clipped
   * away from the type's own line boxes with a feather, so a rule can never run through a
   * glyph, which qa.py reads as a strikethrough and is right to.
   */
  N.quiet = function (cx, rects, fn) {
    if (!rects || !rects.length) { fn(cx); return; }
    var layer = TXDECK.offscreen(W, H, function (g2) { fn(g2); });
    TXDECK.punch(layer.getContext("2d"), rects, { feather: 26, strength: 1 });
    cx.drawImage(layer, 0, 0, W, H);
  };

  /* ---------------------------------------------------------------- pageBox
   *
   * Where a drawn sheet's inner text block lands on screen, so a frame can mount DOM type onto
   * it. Type is DOM or SVG in this engine and never canvas, so every glyph on every drawn
   * document is a positioned element above the art.
   */
  N.pageBox = function (sheet, marginFrac) {
    var m = marginFrac == null ? 0.11 : marginFrac;
    return {
      x: sheet.x + sheet.w * m,
      y: sheet.y + sheet.h * m,
      w: sheet.w * (1 - m * 2),
      h: sheet.h * (1 - m * 2),
      rot: sheet.rot
    };
  };

  global.TXND = N;
})(typeof window !== "undefined" ? window : globalThis);
