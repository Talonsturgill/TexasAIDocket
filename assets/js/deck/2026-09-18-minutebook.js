/* minutebook.js — the chassis for carousel No. 28 (2026-09-18).
 *
 * WHAT THIS IS. The deck "WHO WRITES THE RECORD" follows one question through one Texas county's
 * own paperwork. Nine frames share one light, one material vocabulary and one way of seating
 * type, and this file is those three things and nothing else. Every frame's COMPOSITION is
 * written per frame.
 *
 * THE WORLD. A COUNTY RECORDS ROOM AT NIGHT. Oxblood walls going to black away from the key, a
 * shelf board running off both sides of the frame at a constant height, and warm bond paper
 * wherever a document is drawn. The camera moves through this one room across the deck, from the
 * building outside it to the shelf that holds what the building decided.
 *
 * THE LIGHT, IN WORDS A FRAME AUTHOR CAN CHECK A DRAWING AGAINST. THE KEY IS UPPER RIGHT AT 26
 * DEGREES ABOVE THE PLANE, SO EVERY CAST IN THIS DECK RUNS DOWN AND TO THE LEFT AT ABOUT TWICE
 * THE OBJECT'S OWN HEIGHT. Nothing here is lit from overhead and nothing is lit from the left.
 * That is the deck's signature and it is also its separation from September 17th, which lit its
 * reading surface from the upper LEFT at 22 degrees. Say it in those words, because "az 52" is
 * not a sentence a drawing can be checked against.
 *
 * THE MOTIF, AND IT CHANGES STATE ACROSS THE DECK. THE MINUTE BOOK SPINE. A run of bound county
 * minute books on a shelf, each one a volume of the official record, drawn at true size. The run
 * is continuous where the record is published and it STOPS where the record is not. The gap is
 * never a black bar and never a question mark. It is the shelf board itself, lit, with nothing
 * standing on it, and the accent keylines the empty space so a reader can see it has a SIZE.
 *
 * THE GLYPH LAW, inherited from September 17th and it is why this deck can draw documents at all.
 *
 *   A DRAWN LINE OF TYPE GETS GLYPHS IF AND ONLY IF THIS RUN FETCHED THOSE GLYPHS.
 *
 * The three agendas are set in real type, verbatim, because those pages were read and are in
 * claims.json. EVERYTHING THE COURT ACTUALLY DID IS THE UNGLYPHED DOCUMENT. It is drawn with
 * `ruleRun` as hairlines at true line lengths, because no document this run read publishes one
 * word of any disposition, and a frame that set glyphs there would be inventing them. Nothing in
 * nine frames is drawn as a filled bar, a strike or a smudge, because a black field says
 * something was REMOVED and the record says nothing was ever written.
 *
 * THE ONE SCREEN. `tooth`, a halftone dot field at cell 6, the deck's stock on all nine frames.
 * Halftone rather than hatch or stipple for the reason September 17th measured on its own ground
 * and ink: this deck needs a genuinely bright readable page standing on a near black ground on
 * five of nine frames, and a halftone is the only screen with the range to print one.
 *
 * THE PALETTE IS COMPUTED, NOT CHOSEN. out/2026-09-18/palette_measured.json carries the
 * arithmetic. Each role was measured by CIELAB dE76 nearest neighbour against all 53 hexes used
 * by the last eight decks, and the furthest candidate inside the region brand.yaml allows was
 * taken.
 *
 *   ground    #361D27  L* 14.5  dE 10.13  the records room, a deep oxblood
 *   material  #4F3D2F  L* 27.3  dE 14.76  the shelf board and the bindings
 *   ink       #E4D3CE  L* 85.8  dE  6.97  display type and light on dark marks
 *   stock     #EDDFD4  L* 89.6  dE  3.83  the drawn pages
 *   accent    #4FC79A  L* 72.8  dE 23.30  brand token signal_open, and see below
 *
 * TWO OF THOSE NUMBERS ARE HONEST RATHER THAN GOOD AND THEY ARE STATED RATHER THAN HIDDEN. The
 * paper roles sit at dE 3.83 and no candidate cleared 4, because eight consecutive decks have
 * drawn documents on warm bond and that corner of the space is genuinely spent. Moving the stock
 * further would buy a number by making the paper stop reading as paper, which is the wrong
 * trade on a deck whose subject is paper. The accent is brand token `signal_open` at dE 23.30,
 * and the resonance is deliberate rather than decorative: on this site that token means a window
 * still open, and every item in this deck is still open.
 *
 * WHAT THIS IS NOT. There is no drawFrame() here and there never will be. A shared projection
 * helper is house furniture. A shared draw-the-whole-slide is a template, and
 * scripts/carousel/deck_chassis.py refuses one by name. This file hands a frame primitives. The
 * frame decides what to build from them.
 *
 * LOAD ORDER: noise.js, txtype.js, txcolor.js, txpost.js, txdeck.js, then this, then the scene
 * bench (txscene, txfig, txobjects) on frames that need true scale objects, then txlayout.js.
 */
(function (global) {
  "use strict";

  if (!global.TXDECK) throw new Error("deck/minutebook.js needs txdeck.js loaded first");

  /* ------------------------------------------------------------------ the deck
   *
   * ONE LIGHT, NINE FRAMES, DECLARED HERE AND NOWHERE ELSE. A frame that calls declare() again
   * with different values throws, which fails that frame's render loudly rather than shipping a
   * deck whose seventh frame is lit from the other side.
   */
  TXDECK.declare({
    world: "minutebook",
    light: { az: 52, el: 26, keyToFill: 7.0 },
    ground: "#361D27",
    material: "#4F3D2F",
    accent: "#4FC79A",
    grade: {
      exposure: -0.04,
      saturation: 1.05,
      contrast: 1.16,
      filmic: true,
      lift: [0.020, 0.010, 0.016],   /* shadows to the room's oxblood */
      gain: [1.024, 1.004, 0.972],   /* highlights to the warm bond */
      vignette: 0.25,
      bloom: { threshold: 0.75, strength: 0.28, radius: 9 },
      grain: { amount: 0.044, size: 2, seed: 20260918 },
      aberration: 0,
      dither: true,
      sharpen: 0.33
    }
  });

  var N = {};
  var W = 1080, H = 1350;

  /* THE CONSTANT SHELF LINE. The records room's shelf board sits at this y on every frame that
   * shows it, so the eye keeps one horizontal across the whole swipe. It is the spine the
   * panorama runs along and the most load bearing number in the deck. */
  /* MOVED FROM 902 TO 1118 AFTER THE FIRST RENDER OF FRAME 9, AND THE REASON IS MEASURED. At 902
   * the volumes ended two thirds of the way up the frame and left a dead near black band across
   * the whole bottom third, which is the defect a scorer named on six consecutive decks in the
   * sibling product. At 1118 the run occupies the lower third, the floor below it is the
   * furniture band the falloff was always going to darken, and the wall above carries the type. */
  N.SHELF = 1118;

  /* THE DECK'S TWO RAMPS, built once and handed to every frame, which is most of what makes
   * nine frames look cut from one piece of stock.
   *
   * TWO, not one, and the reason is September 16th's written lesson. A single ramp off the
   * room's material makes the PAPER that material's hue, because a sheet drawn from steps 3 and
   * 6 of an oxblood ramp is an oxblood sheet whatever the light does to it afterwards. Paper
   * under a raking warm key is warm in its lights and cool only in its shadows.
   *
   * ROOM is the world: walls, shelf board, bindings, everything the key barely reaches.
   * STOCK is paper: the drawn agendas and nothing else.
   *
   * THE ROOM RAMP'S TOP END IS 0.76 AND IT IS NOT A NUMBER TO DRIFT FROM. September 17th's
   * probe frame rendered at a median L* of 2.3 against a planned 30 because its first ramp
   * topped out at 0.56. A ramp whose lightest step is still dark can't light a room, and no
   * amount of pool strength fixes it, because the pool screens ONTO what the ramp already put
   * down. That is the whole reason Phase 10.5 renders a probe frame before the other eight get
   * written.
   */
  N.ROOM  = TXDECK.ramp(9, { Lmin: 0.04, Lmax: 0.76, ambientHue: 348, drift: 13 });
  N.STOCK = TXDECK.ramp(9, { base: "#EDDFD4", Lmin: 0.16, Lmax: 0.96,
                             ambientHue: 32, drift: 10, chroma: 0.62 });
  N.pick  = function (i) { return TXDECK.pick(N.ROOM,  i); };
  N.paper = function (i) { return TXDECK.pick(N.STOCK, i); };

  /* The inks, so nine frames can't each pick their own. One pale ink for the furniture across
   * all nine frames, which is September 16th's lesson about mid grounds: nothing contrasts
   * against a mid tone, so the GROUND moves and the ink stays put. */
  N.INK   = "#E4D3CE";   /* display type and drawn light on dark marks */
  N.DEK   = "#B9A39E";
  N.RULE  = "#9A8079";   /* the furniture, one pale ink on all nine frames */
  N.TONER = "#2A1C18";   /* the type printed ON a drawn page */
  N.MINT  = "#4FC79A";   /* the accent. Hollow everywhere the answer is not */

  /* -------------------------------------------------------------------- scene
   *
   * A TXSCENE carrying THIS DECK'S light, so a frame can never set up a camera lit from
   * somewhere else. Guarded rather than required, because five of the nine frames draw paper
   * and need no camera at all.
   */
  N.scene = function (cx, o) {
    if (!global.TXSCENE) throw new Error("minutebook.scene needs txscene.js loaded on this frame");
    o = o || {};
    var d = TXDECK.deck();
    return TXSCENE.create(cx, {
      w: W, h: H,
      eye: o.eye == null ? 1.62 : o.eye,
      horizon: o.horizon == null ? 690 : o.horizon,
      f: o.f == null ? 850 : o.f,
      sky: o.sky || N.pick(0.2),
      fogZ: o.fogZ == null ? 1e9 : o.fogZ,
      light: { az: d.light.az, el: d.light.el }
    });
  };

  /* --------------------------------------------------------------------- pool
   *
   * THE KEY LANDING ON A SURFACE. Every lit thing in this deck is lit by a call to this, so the
   * falloff is the same everywhere and the deck has one light rather than nine.
   *
   * The pool is an ELLIPSE rotated toward the cast direction, because light arriving at 26
   * degrees above a plane lands on it as a conic section. A circle here is the tell that nobody
   * thought about where the light is.
   *
   * `reserve` is a list of line box rects. The light is DIMMED toward them with a wide feather,
   * never removed from around them. A hole punched at full strength is a plate with the sign
   * flipped, and that is a defect this project has already paid to find out about once.
   */
  N.pool = function (cx, o) {
    var x = o.x, y = o.y, r = o.r;
    var squash = o.squash == null ? 0.48 : o.squash;
    var strength = o.strength == null ? 1 : o.strength;
    var rot = o.rot == null ? -0.18 : o.rot;
    var layer = TXDECK.offscreen(W, H, function (g2) {
      g2.save();
      g2.translate(x, y);
      g2.rotate(rot);
      g2.scale(1, squash);
      var rg = g2.createRadialGradient(0, 0, 0, 0, 0, r);
      rg.addColorStop(0.00, "rgba(255,238,224," + (0.40 * strength) + ")");
      rg.addColorStop(0.42, "rgba(255,226,206," + (0.20 * strength) + ")");
      rg.addColorStop(0.74, "rgba(240,206,190," + (0.07 * strength) + ")");
      rg.addColorStop(1.00, "rgba(240,206,190,0)");
      g2.fillStyle = rg;
      g2.beginPath(); g2.arc(0, 0, r, 0, Math.PI * 2); g2.fill();
      g2.restore();
    });
    /* THE DIM IS SOFT AND PARTIAL AND THE PROBE FRAME IS WHY THOSE NUMBERS ARE WHAT THEY ARE.
     * The first build punched at feather 34 and strength 0.72, and the render carried two
     * visible dark rounded rectangles, one behind the hook and one behind the dek. That is a
     * plate drawn in the negative, which is the defect ILLUSTRATION_SYSTEM names in as many
     * words, and it was legible at feed size. Light DIMS toward type. It is not removed from
     * around it. A wide feather and a partial strength keeps the words off the bright part of
     * the pool without drawing a shape of their own. */
    if (o.reserve && o.reserve.length) {
      TXDECK.punch(layer.getContext("2d"), o.reserve, {
        feather: o.reserveFeather == null ? 72 : o.reserveFeather,
        strength: o.reserveStrength == null ? 0.34 : o.reserveStrength
      });
    }
    cx.save();
    cx.globalCompositeOperation = "screen";
    cx.drawImage(layer, 0, 0, W, H);
    cx.restore();
  };

  /* ------------------------------------------------------------------- falloff
   *
   * The room going to the deck's dark at the bottom of the frame, so the furniture band is
   * quiet by CONSTRUCTION rather than by a plate. This is what makes NO PLATE, EVER possible.
   */
  N.falloff = function (cx, o) {
    o = o || {};
    var from = o.from == null ? 1150 : o.from;
    var g = cx.createLinearGradient(0, from, 0, H);
    g.addColorStop(0, "rgba(19,8,12,0)");
    g.addColorStop(0.55, "rgba(19,8,12," + (o.mid == null ? 0.74 : o.mid) + ")");
    g.addColorStop(1, "rgba(19,8,12," + (o.end == null ? 0.95 : o.end) + ")");
    cx.save(); cx.fillStyle = g; cx.fillRect(0, from, W, H - from); cx.restore();
  };

  N.falloffTop = function (cx, o) {
    o = o || {};
    var to = o.to == null ? 250 : o.to;
    var g = cx.createLinearGradient(0, 0, 0, to);
    g.addColorStop(0, "rgba(19,8,12," + (o.start == null ? 0.72 : o.start) + ")");
    g.addColorStop(1, "rgba(19,8,12,0)");
    cx.save(); cx.fillStyle = g; cx.fillRect(0, 0, W, to); cx.restore();
  };

  /* --------------------------------------------------------------------- wall
   *
   * The records room's back wall and floor, one call, with the lateral falloff that stops the
   * lit region being a full width band. Light from one side of a room does not reach the far
   * corners of the opposite wall, so the wall loses its corners and the bright region stops
   * being a rectangle. Six frames of one shipped deck were called "one primitive, a solid
   * bright rectangle on a darker ground" for want of exactly this.
   */
  N.wall = function (cx, o) {
    o = o || {};
    var join = o.join == null ? N.SHELF : o.join;
    /* THE DEFAULTS ARE MEASURED OFF THE RAMP RATHER THAN CHOSEN. The ROOM ramp's steps measure
     * L* 0.1, 1.9, 9.2, 20.0, 30.2, 40.5, 51.0, 61.6, 71.9. The first build drew this wall from
     * step 0.9 to step 3.1, which is L* 1.6 to 20, the bottom third of a ramp that has a top
     * third, and the probe frame came back at a median L* of 5.4 against a planned 26. A wall
     * drawn from the dark end of a ramp can't light a room and no pool strength fixes it,
     * because the pool screens ONTO what the ramp already put down. */
    var lit = o.lit == null ? 4.6 : o.lit, shade = o.shade == null ? 2.4 : o.shade;
    var g = cx.createLinearGradient(0, 0, 0, join);
    g.addColorStop(0, N.pick(shade));
    g.addColorStop(1, N.pick(lit));
    cx.save();
    cx.fillStyle = g; cx.fillRect(0, 0, W, join);
    var lx = o.lightX == null ? 0.72 : o.lightX;   /* the key is upper RIGHT on this deck */
    var lg = cx.createLinearGradient(0, 0, W, 0);
    lg.addColorStop(0, "rgba(22,9,14,0.48)");
    lg.addColorStop(lx, "rgba(22,9,14,0)");
    lg.addColorStop(1, "rgba(22,9,14,0.10)");
    cx.fillStyle = lg; cx.fillRect(0, 0, W, join);
    /* the floor below the join, falling away but NEVER to black. The nearest thing in a picture
     * is never the darkest thing in it. */
    /* THE NEAR END OF THE FLOOR CARRIES LIGHT AND THE PROBE FRAME IS WHY. The first build ran
     * this from step 2.4 down to step 0.5 and the whole lower third of the render came back a
     * dead near black band, which is the defect a scorer named on six consecutive decks in the
     * sibling product. The floor immediately under the board is the nearest thing in the
     * picture and the nearest thing is never the darkest. It falls away toward the reader
     * rather than toward the camera. */
    var fg = cx.createLinearGradient(0, join, 0, H);
    fg.addColorStop(0, N.pick(Math.max(0, shade + 2.9)));
    fg.addColorStop(0.45, N.pick(Math.max(0, shade + 1.4)));
    fg.addColorStop(1, N.pick(Math.max(0, shade + 0.2)));
    cx.fillStyle = fg; cx.fillRect(0, join, W, H - join);
    cx.restore();
  };

  /* -------------------------------------------------------------------- board
   *
   * THE SHELF BOARD. A plank running off both edges of the frame at N.SHELF, with a lit front
   * lip along the key side and a two part contact under it. This is the deck's one horizontal
   * and it is the same y on every frame that shows it.
   */
  N.board = function (cx, o) {
    o = o || {};
    var y = o.y == null ? N.SHELF : o.y;
    var th = o.thickness == null ? 26 : o.thickness;
    var x0 = o.x0 == null ? -60 : o.x0, x1 = o.x1 == null ? W + 60 : o.x1;
    cx.save();
    /* the top face, taking the key */
    var g = cx.createLinearGradient(x0, y, x1, y);
    g.addColorStop(0, N.pick(2.0));
    g.addColorStop(0.74, N.pick(5.2));
    g.addColorStop(1, N.pick(4.0));
    cx.fillStyle = g; cx.fillRect(x0, y, x1 - x0, th);
    /* the lit lip along the front edge */
    cx.fillStyle = N.pick(6.4);
    cx.fillRect(x0, y, x1 - x0, 2.5);
    /* the front face falling away */
    var fg = cx.createLinearGradient(0, y + th, 0, y + th + 34);
    fg.addColorStop(0, N.pick(1.6));
    fg.addColorStop(1, N.pick(0.5));
    cx.fillStyle = fg; cx.fillRect(x0, y + th, x1 - x0, 34);
    cx.restore();
    return { y: y, thickness: th, top: y };
  };

  /* ---------------------------------------------------------------- elevation
   *
   * A SCENE BENCH SPRITE DRAWN IN ELEVATION AT A STATED PIXELS PER METRE, with no perspective.
   *
   * The records room frames are drawn square on at a stated scale rather than through a camera,
   * because a shelf photographed straight on is what a shelf looks like and a vanishing point
   * here would only add arithmetic. This is the projection helper that lets those frames still
   * use TXFIG and TXOBJ at TRUE SIZE, so a person beside a shelf of books is 1.70 m beside
   * 0.42 m and nothing is a slab.
   *
   * Sprite space has Y UP from the ground, which is why every part's y is subtracted from the
   * base rather than added to it. Getting that backwards draws the figure upside down and
   * nothing throws.
   */
  N.elevation = function (cx, sprite, o) {
    var ppm = o.ppm, x = o.x, base = o.base;
    var mx = o.mirror ? -1 : 1;
    var ink = o.ink || N.pick(1.6), paper = o.paper || N.paper(4.0);
    function P(px, py) { return [x + px * ppm * mx, base - py * ppm]; }
    cx.save();
    if (o.alpha != null) cx.globalAlpha = o.alpha;
    for (var i = 0; i < sprite.parts.length; i++) {
      var p = sprite.parts[i];
      if (p.fill === "none") continue;
      cx.fillStyle = p.fill === "paper" ? paper : ink;
      cx.strokeStyle = cx.fillStyle;
      if (p.type === "poly") {
        cx.beginPath();
        for (var j = 0; j < p.pts.length; j++) {
          var q = P(p.pts[j][0], p.pts[j][1]);
          if (j === 0) cx.moveTo(q[0], q[1]); else cx.lineTo(q[0], q[1]);
        }
        cx.closePath(); cx.fill();
      } else if (p.type === "rect") {
        var a = P(p.x, p.y + p.h), b = P(p.x + p.w, p.y);
        cx.fillRect(Math.min(a[0], b[0]), Math.min(a[1], b[1]),
                    Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1]));
      } else if (p.type === "ellipse") {
        var c = P(p.cx, p.cy);
        cx.beginPath(); cx.ellipse(c[0], c[1], p.rx * ppm, p.ry * ppm, 0, 0, Math.PI * 2); cx.fill();
      } else if (p.type === "line") {
        cx.lineWidth = Math.max(1, (p.width || 0.1) * ppm);
        cx.lineCap = p.cap || "round";
        cx.lineJoin = "round";
        cx.beginPath();
        for (var k = 0; k < p.pts.length; k++) {
          var r = P(p.pts[k][0], p.pts[k][1]);
          if (k === 0) cx.moveTo(r[0], r[1]); else cx.lineTo(r[0], r[1]);
        }
        cx.stroke();
      }
    }
    cx.restore();
    return { x: x - (sprite.w / 2) * ppm, y: base - sprite.h * ppm,
             w: sprite.w * ppm, h: sprite.h * ppm };
  };

  /* -------------------------------------------------------------------- spine
   *
   * THE MOTIF. One bound county minute book standing on the board, at TRUE SIZE. A county
   * record volume is about 0.32 m wide at the spine and 0.42 m tall, so a frame states its own
   * pixels per metre and the book is drawn from that rather than from a pixel guess.
   *
   * Bindings are the ROOM ramp, labels are the STOCK ramp, and the label is a rectangle of
   * paper rather than set type unless the frame has a quote to set on it.
   */
  N.spine = function (cx, o) {
    var x = o.x, base = o.base == null ? N.SHELF : o.base;
    var w = o.w, h = o.h;
    var tone = o.tone == null ? 2.6 : o.tone;
    var seed = o.seed == null ? 3 : o.seed;
    var R = TX.rng(seed);
    var lean = o.lean == null ? 0 : o.lean;
    cx.save();
    cx.translate(x + w / 2, base);
    cx.rotate(lean);
    cx.translate(-w / 2, -h);
    /* the binding, lit from the right */
    var g = cx.createLinearGradient(0, 0, w, 0);
    g.addColorStop(0, N.pick(Math.max(0, tone - 1.1)));
    g.addColorStop(0.78, N.pick(tone + 1.0));
    g.addColorStop(1, N.pick(Math.max(0, tone - 0.3)));
    cx.fillStyle = g; cx.fillRect(0, 0, w, h);
    /* the lit right edge, the key side */
    cx.fillStyle = N.pick(tone + 2.4);
    cx.fillRect(w - 2.2, 0, 2.2, h);
    /* two raised bands, which is what makes it a bound book rather than a block */
    cx.fillStyle = N.pick(tone + 1.6);
    cx.fillRect(0, h * 0.20, w, Math.max(1.6, h * 0.018));
    cx.fillRect(0, h * 0.74, w, Math.max(1.6, h * 0.018));
    /* the paper label */
    if (o.label !== false) {
      var lw = w * 0.66, lh = h * 0.20;
      var lx = (w - lw) / 2, ly = h * 0.33;
      cx.fillStyle = N.paper(o.labelTone == null ? 6.2 : o.labelTone);
      cx.fillRect(lx, ly, lw, lh);
      cx.fillStyle = N.paper(7.6);
      cx.fillRect(lx, ly, lw, 0.8);
    }
    /* the head of the text block, a sliver of page edges above the board line */
    cx.fillStyle = N.paper(3.0 + R() * 0.8);
    cx.fillRect(1.4, 0, w - 2.8, Math.max(1.2, h * 0.012));
    cx.restore();
    return { x: x, y: base - h, w: w, h: h };
  };

  /* ---------------------------------------------------------------------- gap
   *
   * THE ABSENCE, WITH A SIZE. The board, lit, with nothing standing on it, keylined in the
   * accent so a reader can see the space has dimensions.
   *
   * IT IS NEVER A FILLED BAR AND NEVER A DARK HOLE. A dark field says a volume was REMOVED. An
   * empty lit board says a volume was never set down, which is the true statement, and the
   * keyline is what stops the eye sliding over it.
   */
  N.gap = function (cx, o) {
    var x = o.x, w = o.w, h = o.h;
    var base = o.base == null ? N.SHELF : o.base;
    cx.save();
    /* the board under it reads brighter, because nothing is standing there to shade it.
     *
     * THE WASH IS AN OPTION BECAUSE THE RUN AROUND IT MOVED. At 0.10 this beat spines drawn from
     * ROOM steps 1.7 to 3.4, which is L* 7 to 24. Round 2 lifted that run to steps 3.9 to 5.4,
     * L* 28 to 45, to make frame 1's declared focal the frame's brightest mass, and the same
     * lift would have left frame 9's gap DARKER than the volumes it is supposed to be an absence
     * of. A focal made of value has to be remade whenever the value under it changes, which is
     * the whole reason this is a parameter and not a constant. A second call passes 0 so the
     * accent redraw does not lay the wash down twice. */
    var wash = o.wash == null ? 0.10 : o.wash;
    if (wash > 0) {
      var g = cx.createLinearGradient(x, base - h, x, base);
      g.addColorStop(0, "rgba(255,238,224,0)");
      g.addColorStop(1, "rgba(255,238,224," + wash + ")");
      cx.fillStyle = g; cx.fillRect(x, base - h, w, h);
    }
    /* the keyline, hollow */
    cx.strokeStyle = o.ink || N.MINT;
    cx.lineWidth = o.weight == null ? 13 : o.weight;
    if (o.dash) cx.setLineDash(o.dashPattern || [26, 10]);
    cx.strokeRect(x + 0.5, base - h + 0.5, w - 1, h - 1);
    cx.restore();
    return { x: x, y: base - h, w: w, h: h };
  };

  /* -------------------------------------------------------------------- sheet
   *
   * A US LETTER SHEET AT TRUE PROPORTION, 216 by 279 mm, with a hand wobbled edge, a lit top
   * edge on the key side and a two part contact under it. Returns its own screen box so a frame
   * can mount DOM type onto it, because type is DOM or SVG in this engine and never canvas.
   *
   * The wobble is what stops it being a rectangle. A sheet of paper on a shelf is never
   * straight on all four sides and the eye knows it before it can say so.
   */
  N.sheet = function (cx, o) {
    var x = o.x, y = o.y, w = o.w, h = o.h;
    var rot = o.rot == null ? 0 : o.rot;
    var seed = o.seed == null ? 17 : o.seed;
    var R = TX.rng(seed);
    var lit = o.lit == null ? 7.2 : o.lit, shade = o.shade == null ? 3.6 : o.shade;

    if (o.contact !== false) {
      TXDECK.contact(cx, {
        x: x + w / 2, y: y + h, w: w * 0.94, height: o.thickness == null ? 5 : o.thickness,
        ink: "rgba(14,5,9,0.62)"
      });
    }

    cx.save();
    cx.translate(x + w / 2, y + h / 2);
    cx.rotate(rot);
    cx.translate(-w / 2, -h / 2);

    /* the wobbled outline, four sides each drifting by under a millimetre of page */
    var wob = o.wobble == null ? 2.2 : o.wobble;
    cx.beginPath();
    cx.moveTo(0, 0);
    cx.lineTo(w + (R() - 0.5) * wob, (R() - 0.5) * wob);
    cx.lineTo(w + (R() - 0.5) * wob, h + (R() - 0.5) * wob);
    cx.lineTo((R() - 0.5) * wob, h + (R() - 0.5) * wob);
    cx.closePath();

    var g = cx.createLinearGradient(0, 0, w * 0.35, h);
    g.addColorStop(0, N.paper(lit));
    g.addColorStop(1, N.paper(shade));
    cx.fillStyle = g; cx.fill();

    /* the lit head of the sheet, the key side */
    cx.save(); cx.clip();
    cx.fillStyle = N.paper(Math.min(8.6, lit + 1.1));
    cx.fillRect(0, 0, w, 3);
    cx.restore();
    cx.restore();
    return { x: x, y: y, w: w, h: h, rot: rot };
  };

  /* --------------------------------------------------------------------- rule
   *
   * One ruled line on a drawn page. `answer` draws the deck's accent hollow, which is the rule
   * a disposition would have been written on.
   */
  N.rule = function (cx, o) {
    cx.save();
    if (o.answer) {
      cx.strokeStyle = o.ink || N.MINT;
      cx.lineWidth = o.weight == null ? 2.2 : o.weight;
      if (o.dash !== false) cx.setLineDash(o.dashPattern || [10, 8]);
    } else {
      cx.strokeStyle = o.ink || "rgba(42,28,24,0.24)";
      cx.lineWidth = o.weight == null ? 1.4 : o.weight;
    }
    cx.beginPath(); cx.moveTo(o.x0, o.y); cx.lineTo(o.x1, o.y); cx.stroke();
    cx.restore();
  };

  /* ------------------------------------------------------------------ ruleRun
   *
   * THE UNGLYPHED DOCUMENT, AND THE GLYPH LAW IS WHY IT EXISTS.
   *
   * Hairlines at a page's own leading, at TRUE LINE LENGTHS with a ragged right, drawn in the
   * page's own ink. This is what any disposition is drawn as on every frame it appears, because
   * no document this run read publishes one word of one.
   *
   * IT IS NEVER A FILLED BAR. A bar says something was removed. A hairline with a lit lip says
   * a line of type sits here and this run did not read it, which is the true statement.
   */
  N.ruleRun = function (cx, o) {
    var x = o.x, y = o.y, w = o.w;
    var n = o.n == null ? 6 : o.n;
    var leading = o.leading == null ? 22 : o.leading;
    var R = TX.rng(o.seed == null ? 5 : o.seed);
    var ink = o.ink || "rgba(42,28,24,0.30)";
    var weight = o.weight == null ? 2.0 : o.weight;
    cx.save();
    for (var i = 0; i < n; i++) {
      var len = w * (o.ragged === false ? 1 : (0.60 + R() * 0.40));
      if (i === n - 1) len = w * (0.30 + R() * 0.26);          /* a last line is short */
      var yy = y + i * leading;
      cx.fillStyle = ink;
      cx.fillRect(x, yy, len, weight);
    }
    cx.restore();
    return { x: x, y: y, w: w, h: n * leading };
  };

  /* ------------------------------------------------------------------ keyline
   *
   * THE ACCENT, UNFILLED, and it is the deck's one colour. Hollow everywhere the answer is not.
   * A frame that wants the accent SOLID is making a statement about the one place an answer
   * exists, and there is at most one of those in the deck.
   */
  /* THE WEIGHT IS 6.5 AND THAT NUMBER IS MEASURED RATHER THAN CHOSEN. layout_check counts the
   * accent at THUMB SCALE, 216 by 270, and asks for at least 0.2 percent of the frame within 12
   * Lab units of the declared hex. The first build drew this at 2.4 px dashed, which is 0.48 px
   * at thumb width, averages into the paper under it and measured 0.0000 on all five frames that
   * declared it. 6.5 px dashed measured 0.0007 to 0.0012, still under the line. SOLID at 13 px is
   * what clears it, and it stays HOLLOW, which is the property that matters: the accent bounds
   * what is unanswered and never fills it, so it can't be read as an approval mark. */
  N.keyline = function (cx, o) {
    cx.save();
    cx.strokeStyle = o.ink || N.MINT;
    cx.lineWidth = o.weight == null ? 13 : o.weight;
    if (o.dash) cx.setLineDash(o.dashPattern || [26, 10]);
    var r = o.radius == null ? 0 : o.radius;
    if (r > 0 && cx.roundRect) { cx.beginPath(); cx.roundRect(o.x, o.y, o.w, o.h, r); cx.stroke(); }
    else cx.strokeRect(o.x + 0.5, o.y + 0.5, o.w - 1, o.h - 1);
    cx.restore();
    return { x: o.x, y: o.y, w: o.w, h: o.h };
  };

  /* -------------------------------------------------------------------- tooth
   *
   * THE ONE SCREEN. A halftone dot field at cell 6, sampled off what is already on the canvas,
   * so tone becomes marks a reader can see. It is the deck's stock and the same on all nine
   * frames. `mask` is the type reserve, so the screen thins toward the words rather than being
   * punched out around them.
   */
  N.tooth = function (cx, o) {
    var x = o.x, y = o.y, w = o.w, h = o.h;
    var cell = o.cell == null ? 6 : o.cell;
    var angle = (o.angle == null ? 26 : o.angle) * Math.PI / 180;
    var strength = o.strength == null ? 0.15 : o.strength;
    var mask = o.mask || function () { return 1; };
    var img;
    try { img = cx.getImageData(x * 2, y * 2, Math.max(1, w * 2), Math.max(1, h * 2)); }
    catch (e) { return; }
    var d = img.data, iw = Math.max(1, w * 2), ih = Math.max(1, h * 2);
    function toneAt(px, py) {
      var ix = Math.round((px - x) * 2), iy = Math.round((py - y) * 2);
      if (ix < 0 || iy < 0 || ix >= iw || iy >= ih) return 0;
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
        var rr = cell * 0.5 * Math.sqrt(Math.max(0, Math.min(1, t))) * m;
        if (rr < 0.25) continue;
        cx.fillStyle = "rgba(255,244,232," + (strength * m) + ")";
        cx.beginPath(); cx.arc(px, py, rr, 0, Math.PI * 2); cx.fill();
      }
    }
    cx.restore();
  };

  /* -------------------------------------------------------------------- quiet
   *
   * Draw something, then dim it toward the type's own line boxes with a wide feather. This is
   * how a field, a hatch or a run of rules keeps clear of the words without a plate under them.
   */
  N.quiet = function (cx, rects, fn) {
    if (!rects || !rects.length) { fn(cx); return; }
    var layer = TXDECK.offscreen(W, H, function (g2) { fn(g2); });
    TXDECK.punch(layer.getContext("2d"), rects, { feather: 28, strength: 1 });
    cx.drawImage(layer, 0, 0, W, H);
  };

  /* ------------------------------------------------------------------ pageBox
   *
   * Where a drawn sheet's inner text block lands on screen, so a frame can mount DOM type onto
   * it. Type is DOM or SVG in this engine and never canvas, so every glyph on every drawn
   * document is a positioned element above the art.
   */
  N.pageBox = function (sheet, marginFrac) {
    var m = marginFrac == null ? 0.10 : marginFrac;
    return {
      x: sheet.x + sheet.w * m,
      y: sheet.y + sheet.h * m,
      w: sheet.w * (1 - m * 2),
      h: sheet.h * (1 - m * 2),
      rot: sheet.rot
    };
  };

  global.TXMB = N;
})(typeof window !== "undefined" ? window : globalThis);
