/* nightapron.js — the chassis for carousel No. 32 (2026-09-22).
 *
 * WHAT THIS IS. The deck "GOOD FOR 24 HOURS" spends nine frames on one inspection apron under
 * one high mast lamp and argues that the barrier to driverless freight in Texas was never the
 * truck. It is a person walking around it, and what that person signs runs out. Nine frames
 * share one light, one stock and one way of seating type, and this file is those three things
 * and nothing else. Every frame's COMPOSITION is written per frame.
 *
 * THE WORLD. A CONCRETE INSPECTION APRON OFF A TEXAS HIGHWAY RIGHT OF WAY, AT NIGHT, UNDER ONE
 * HIGH MAST LAMP. A Class 8 tractor trailer at a true 17.0 by 4.1 m, an empty cab, a person at
 * 1.70 m with a clipboard, apron joints at 4 m centres, tyre scuff and grime. Nothing else is
 * in this world. There is no county, no highway shield, no station name and no coordinate on
 * any of nine frames, because the record names two states and nothing smaller, and a map would
 * have to put a dot somewhere the record has not been.
 *
 * THE KEY IS A FIXTURE AND NOT THE SUN, AND THAT IS THE DECK'S ONE STRUCTURAL IDEA.
 *
 * The obvious deck for a story about 24 hours runs the sun across nine frames. That deck cannot
 * be built here and the reason is in ILLUSTRATION_SYSTEM.md twice over. Nine frames of a moving
 * sun is nine lights, which is the exact fault THE CHASSIS LAW was written against, and a dusk
 * to noon to dusk swing is the non monotonic arc THE CONTINUITY MANDATE names as wrong. So the
 * key is nailed to a mast at one azimuth and one elevation for all nine frames, and the only
 * thing that changes across the deck is the AMBIENT, which drains. A lamp licenses that. A sun
 * does not.
 *
 * At el 46 a 4.1 m trailer throws about 3.96 m and a 1.70 m person throws about 1.64 m, so
 * every cast in the deck stays inside its own frame. That is deliberate. A low key would have
 * given longer and handsomer shadows and would have put the deck's own subject half off the
 * page on five frames out of nine.
 *
 * THE GROUND AND THE INK WERE MEASURED, NOT CHOSEN.
 *
 *   ground #17233F   L* 14.1, b* -19.5. Nearest of the last six shipped grounds is #18222B
 *                    from September 19th at dE76 13.74, against a floor of 10. The fallback a
 *                    director proposed, #0E2438, MEASURES 8.19 AND WOULD HAVE FAILED, which is
 *                    the whole argument for measuring a fallback before writing it down.
 *   ink    #CDD6DE   L* 85.2, and it is COOL on purpose. The last three decks shipped cream
 *                    (#E6DFCC, #DCD3B4, #D9DEC9). A fourth would have read as this product's
 *                    house paper rather than as this deck's material, and the material here is
 *                    galvanised steel and retroreflective sheeting, which are not cream.
 *   accent #E0956A   dusk_gold. dE76 33.87 from the nearest accent in the recent window.
 *
 * THE ACCENT IS NEVER A MATERIAL, and this is the deck's sharpest law. Nothing physical wears
 * dusk_gold. Not the truck, not the person, not the paper's type, not a location. It is the 24
 * marks and nothing else, which means anything wearing it is a MEASUREMENT rather than a thing.
 * That is what stops a band along a trailer rail reading as livery a reader might go looking
 * for.
 *
 * THE 24 MARKS ARE ALL HOLLOW OR ALL FILLED AND NEVER PART FILLED, and this one is an accuracy
 * rule wearing a design rule's clothes. A treatment proposed filling them progressively across
 * the nine frames as a reading position. A part filled band of 24 is a QUANTITY OF ELAPSED
 * HOURS asserted in geometry, the record does not say how many hours any inspection has run,
 * and no numeral lint reads a drawing. It is the compute-not-generate law broken in the one
 * place nothing is watching. So the ring is hollow on every frame that carries it except frame
 * 4, where it is filled once, at the moment the walk closes, and that single filled state is
 * the deck's only solid colour.
 *
 * THE FRAMES DRAW IN GREYS. Every scene is drawn into TXINK's offscreen twin in greys and the
 * print maps tone to ink on this deck's stock, so this file hands out a GREY SCALE rather than
 * a colour ramp. A frame that picks its own colours has left the deck. The one place real
 * colour is painted is `over`, after the screen has run, which is where the accent goes.
 */
(function (global) {
  "use strict";

  if (!global.TXDECK) throw new Error("nightapron.js needs txdeck.js loaded first");

  /* ONE DECLARATION, AND IT IS THE ONLY ONE IN THE DECK. Nine frames can't hold nine lights. */
  TXDECK.declare({
    world: "nightapron",
    light: { az: -38, el: 46, keyToFill: 5.2 },
    ground: "#17233F",
    material: "#CDD6DE",
    accent: "#E0956A",
    grade: {
      exposure: 0.015,
      saturation: 0.98,
      contrast: 1.14,
      filmic: true,
      lift: [0.010, 0.014, 0.026],   /* shadows toward the apron's own night blue, not to grey */
      gain: [0.982, 0.996, 1.038],   /* highlights to a cold mast lamp rather than to daylight */
      vignette: 0.22,
      bloom: { threshold: 0.80, strength: 0.22, radius: 9 },
      /* GRAIN AT 0.014, CARRIED FORWARD FROM THE SEPTEMBER 19TH MEASUREMENT rather than the
       * house 0.044. That run measured its vector PDF at 68.7 MB against 6 to 14 MB for every
       * deck before it, tested three hypotheses, and found cutting per pixel noise and the
       * dither was worth 9 MB while a raised screen floor and a higher gamma were worth
       * nothing. It is the one knob known to move, and the size is DISCLOSED rather than
       * predicted. A number in this file that was guessed is worse than no number. */
      grain: { amount: 0.014, size: 3, seed: 20260922 },
      aberration: 0,
      dither: false,
      sharpen: 0.30
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;

  /* ------------------------------------------------------------------- stock */
  N.GROUND = "#17233F";   /* hot mix and night sky, the deck's paper */
  N.INK    = "#CDD6DE";   /* hot dip galvanised steel and retroreflective sheeting */
  N.ACCENT = "#E0956A";   /* dusk_gold. THE CLOCK, and nothing else wears it. THE DECLARED value */

  /* THE PAINTED ACCENT IS NOT THE DECLARED ACCENT, AND THE DIFFERENCE IS THE GRADE.
   *
   * TXDECK.finish is the last thing that touches the art canvas and this deck's grade lifts the
   * highlights toward a cold lamp: gain [0.982, 0.996, 1.038] pushes blue up and saturation sits
   * at 0.98. Paint #E0956A through that and what LANDS is #D2A57D, measured off the render,
   * which is about 12 Lab units from the declared hex. `layout_check` reads the accent off the
   * RENDER at thumb scale and counts pixels within 12 Lab of the declared colour, so a deck that
   * paints its own accent hex and then grades it reports an accent present on ZERO frames while
   * looking perfectly correct to a person.
   *
   * So the paint is pre-compensated by the inverse of the measured shift and the DECLARATION
   * stays put. The declared colour is the one checked for variety against the recent window and
   * it is what a reader sees. Changing the declaration to match the drift would have been fixing
   * the measurement rather than the product.
   */
  N.ACCENT_INK = "#EE8557";
  N.DEK    = "#9AA6B6";
  N.RULE   = "#7B8798";   /* the furniture, one pale ink on all nine frames */

  /* THE TWO MATERIALS OF THE PAPER FRAMES. `STOCK` is carbonless inspection form bond under a
   * mast lamp and it is deliberately NOT white: four cream sheets at full white made September
   * 18th's canvas mean strobe, and the judges converged on capping unscreened stock rather than
   * dimming it afterwards. `TONER` is the print on that stock. */
  N.STOCK = "#B9BEC4";
  N.TONER = "#141820";

  /* LINE, CELL 5, ANGLE 76, AND BOTH THE ANGLE AND THE GAMMA WERE DECIDED ON THE PROBE.
   *
   * A LINE SCREEN is the banknote and security print register, which is what a deck about a
   * signed record with a stated expiry wants. It is also the only one of the four screens
   * unspent in the last three decks: September 19th took halftone at cell 7, the 20th hatch at
   * cell 6, the 21st stipple at cell 5.
   *
   * WHY GAMMA STARTS AT 1.0 HERE AND STARTED AT 0.5 ON THE STIPPLE DECK, which is arithmetic
   * rather than a preference. `INK.screen`'s stipple lays `n = round(d * d * perCell)` dots, so
   * its ink coverage goes as luminance to the power 2 * gamma and September 21st needed gamma
   * 0.5 to make that linear. LINE sets `lineWidth = maxW * d` with `maxW = cell * 0.9`, so
   * coverage is ALREADY linear in d and a gamma of 1.0 is the linear setting. Copying the 0.5
   * across would have bent a scale that was straight.
   *
   * THE ANGLE IS 76 AND IT STARTED AT 12, WHICH IS THE DEFECT THIS LINE EXISTS FOR.
   * A line screen at 12 degrees lays its rules NEARLY HORIZONTAL at a 5 px pitch. Type is also
   * horizontal, so one of those rules runs the full width of every line of type that is not
   * sitting in a reserve, and qa.py reads a ruled line crossing a whole label as a strikethrough
   * and is right to. Frame 4's three diagram labels sit out in the art by definition, and all
   * three were struck. The doctrine's own answer, that type never sits on a screen, is not
   * available to a DIAGRAM whose labels have to be beside the thing they point at. So the SCREEN
   * turns instead: at 76 degrees the rules run nearly vertical and a glyph band can't be crossed
   * along its length. It also stops the whole family of moire risks against the apron joints,
   * the horizon and the trailer's own long edges, which are the deck's main horizontals.
   *
   * THAT IS A DERIVATION AND NOT A MEASUREMENT, so it is not trusted. Phase 10.5 prints all
   * nine steps of N.G as full width bands through this exact press and reads each band's L* off
   * the render BEFORE the value arc is committed, at 12 degrees and again at 76. September 21st's press ran BACKWARDS between
   * two steps and its deck was read as hairline wireframes over noise by five critics, with
   * nothing wrong with any frame's drawing. The stated fallback is halftone at cell 9, which is
   * the coarse end and is deliberately not September 19th's cell 7.
   */
  N.SCREEN = { mode: "line", cell: 5, angle: 76, gamma: 1.0, floor: 0.04 };
  N.EDGES  = { threshold: 18, width: 1.3, alpha: 0.80, dx: 1.2, dy: -0.9 };

  /* THE GREY SCALE THE TWIN IS DRAWN IN, dark to light. A frame reaches for these by name so
   * nine frames can't each invent their own tonal separation. The gap in the middle is
   * deliberate: nothing contrasts against a mid tone, so objects are separated ACROSS the hole
   * rather than inside it. `mid` is apron and terrain only, and a SUBJECT drawn at `mid`
   * against the ground is the defect that rule names. */
  N.G = {
    voidd:  "#000000",   /* the inside of a cab seen from outside, a wheel arch */
    deep:   "#0A0E18",   /* the deck's own shade, under a trailer, behind a tyre */
    dark:   "#161C2A",   /* a right face, the deck's dark side, away from the mast */
    shade:  "#252C3C",   /* apron in the lamp's falloff, the shaded half of a sheet */
    mid:    "#3C4454",   /* NOT for a subject against the ground. Apron and terrain only */
    stone:  "#5A6270",   /* lit concrete, a kerb face, a guardrail post in half light */
    metal:  "#848C98",   /* galvanised steel, a chalked trailer flank, a lit face */
    bright: "#B4BCC6",   /* a face taking the mast square on, bond in the light */
    glare:  "#DCE2EA"    /* the lamp square on retroreflective tape or a mirror arm. Sparingly */
  };

  /* One ramp off the deck's material, for the few marks painted in real colour in `over`.
   * TXDECK.pick TAKES AN INDEX, NOT A FRACTION. pick(ramp, 0.74), written by an author who
   * meant "74 percent up the ramp", returns step 1 of 9 and sinks the frame into the ground.
   * Write integer steps, 0 to 8, and read them as steps. */
  N.RAMP = TXDECK.ramp(9, { Lmin: 0.05, Lmax: 0.88, ambientHue: 232, drift: -10 });
  N.pick = function (i) { return TXDECK.pick(N.RAMP, i); };

  /* -------------------------------------------------------------------- scene
   *
   * THE CAMERA BELONGS TO THE FRAME AND THE LIGHT BELONGS TO THE DECK. This hands a frame the
   * camera options with the deck's declared light already in them, and the FRAME writes
   * `TXSCENE.create` itself where a reader can see which camera it stands in.
   *
   * That split is not stylistic. `depth_floor.py` binds on the literal `TXSCENE.create(` in a
   * FRAME's own source, deliberately, because a gate matching a bare method name once counted
   * 62 calls belonging to things that were not the bench and read nine genuinely staged frames
   * as zero.
   *
   * EVERY OPTION ON THE BENCH IS OPTIONAL AND A WRONG NAME IS SILENTLY A DEFAULT. `S.strip`
   * takes X, w, near, far, fill. `S.gridX` takes X extents in from/to and Z extents in
   * near/far; `S.gridZ` takes Z extents in from/to. They are NOT the same shape, and given each
   * other's arguments they draw off frame in silence. Read the signature in txscene.js before
   * the call, then look at the render.
   */
  N.cam = function (o) {
    if (!global.TXSCENE) throw new Error("nightapron.cam needs txscene.js on this frame");
    o = o || {};
    var d = TXDECK.deck();
    return {
      w: N.W, h: N.H,
      eye:     o.eye     == null ? 1.65 : o.eye,
      horizon: o.horizon == null ? 837  : o.horizon,
      f:       o.f       == null ? 900  : o.f,
      sky:     o.sky     || N.G.deep,
      fogZ:    o.fogZ    == null ? 1e9 : o.fogZ,
      light:   { az: d.light.az, el: d.light.el }
    };
  };

  /* -------------------------------------------------------------------- print
   *
   * THE DECK'S STOCK, HANDED TO A FRAME. A frame passes its own `draw` and its own `over` and
   * gets the deck's paper, ink, screen and contour.
   *
   * There is no drawFrame here and there never will be. A shared draw-the-whole-slide is a
   * template, `deck_chassis.py` refuses one by name, and the per frame composition is this
   * machine's whole strength. The chassis hands a frame the press. The frame decides what goes
   * through it.
   */
  N.print = function (cx, o) {
    if (!global.TXINK) throw new Error("nightapron.print needs txink.js on this frame");
    o = o || {};
    TXINK.print(cx, {
      ground: N.GROUND,
      ink: N.INK,
      fibre: 0.045,
      seed: o.seed == null ? 32 : o.seed,
      screen: o.screen || N.SCREEN,
      edges: o.edges || N.EDGES,
      draw: o.draw,
      over: o.over
    });
  };

  /* ------------------------------------------------------------------ the type
   *
   * ONE WAY OF SEATING TYPE, AND IT IS A RESERVE AND NEVER A PLATE. `deck_chassis.py` fails the
   * build on any fill over 0.55 alpha behind display type.
   */
  N.boxes = function (sel, pad) { return TXDECK.lineBoxes(sel, pad == null ? 20 : pad); };

  /* DIM THE GROUND TOWARD THE TYPE. On a DARK deck the type is light on dark, so the light is
   * DIMMED toward it, softly and with a wide feather. It is never REMOVED from around it: a
   * hole punched in a light layer is a plate with the sign flipped, and September 16th's build
   * printed a visible dark rounded rect behind its own site line doing exactly that. */
  N.quiet = function (c, boxes, alpha) {
    var A = alpha == null ? 0.40 : Math.min(0.52, alpha);
    var g = [parseInt(N.GROUND.slice(1, 3), 16),
             parseInt(N.GROUND.slice(3, 5), 16),
             parseInt(N.GROUND.slice(5, 7), 16)];
    c.save();
    for (var i = 0; i < boxes.length; i++) {
      var b = boxes[i], bx = b[0], by = b[1], bw = b[2], bh = b[3];
      var feY = bh * 1.6, feX = Math.max(40, bh * 1.2);
      /* A SMOOTH RAMP WITH NO PLATEAU, AND THE PLATEAU IS WHY THIS IS WRITTEN OUT LONGHAND.
       * The first cut ran four stops, 0 to A at 0.42, A to A across the middle, A to 0 at 1.00.
       * The alpha is constant between those inner stops, so the RATE of change jumps at each of
       * them, and TXINK's contour plate runs a Sobel over the twin and traced that jump as a
       * hairline rule. It landed about a quarter of a line height into the glyph band, so the QA
       * reported the deck's own type reserve as a strikethrough THROUGH THE LABEL IT WAS
       * PROTECTING, and moving the label moved the strike with it, which is the tell.
       * A sampled smoothstep has no step in its derivative anywhere, so there is nothing for an
       * edge detector to find. */
      var gy = c.createLinearGradient(0, by - feY, 0, by + bh + feY);
      for (var s = 0; s <= 24; s++) {
        var t = s / 24;
        var u = Math.abs(t - 0.5) * 2;                 /* 0 at the middle, 1 at either end */
        var k = 1 - u * u * (3 - 2 * u);               /* smoothstep, zero slope at both ends */
        gy.addColorStop(t, "rgba(" + g[0] + "," + g[1] + "," + g[2] + "," + (A * k).toFixed(4) + ")");
      }
      c.fillStyle = gy;
      c.fillRect(bx - feX, by - feY, bw + feX * 2, bh + feY * 2);
    }
    c.restore();
  };

  /* The furniture band's own reserve, from txink. */
  N.reserve = function (c, o) {
    o = o || {};
    TXINK.reserve(c, { ground: N.GROUND,
                       top: o.top == null ? 0 : o.top,
                       topSolid: o.topSolid == null ? 0 : o.topSolid,
                       bottom: o.bottom == null ? 0 : o.bottom,
                       bottomSolid: o.bottomSolid == null ? 0 : o.bottomSolid });
  };

  /* ------------------------------------------------------------- THE 24 MARKS
   *
   * THE DECK'S MOTIF, AS A PRIMITIVE THE FRAME COMPOSES WITH. The FRAME computes the path
   * through its own camera and hands it here as screen points. This divides that path into `n`
   * equal arc lengths and draws the marks. It knows nothing about where the path came from,
   * which is what keeps it a primitive rather than a drawFrame.
   *
   * `filled` IS A BOOLEAN AND NOT A COUNT, ON PURPOSE. There is no way to ask this function for
   * nine of twenty four, because a part filled run of 24 is an assertion about how many hours
   * an inspection has run and no source in this record measures that. The type refuses the
   * defect rather than a comment asking a frame not to commit it.
   *
   * It is also never a sector, never a sweep and never an arc that thickens. One hue at one
   * intensity at every mark. A ring of 24 segments is one bad drawing away from a dial with a
   * red zone on it, and a red zone is a verdict this project's data cannot carry.
   */
  N.ticks = function (c, o) {
    o = o || {};
    var pts = o.path || [];
    if (pts.length < 2) return null;
    var n = o.n == null ? 24 : o.n;
    var ink = o.ink || N.ACCENT_INK;
    var lw = o.width == null ? 4 : o.width;
    var cross = o.cross == null ? 11 : o.cross;

    /* cumulative arc length, so the marks are equal ALONG THE PATH rather than equal in x,
     * which is what makes them survive a perspective projection */
    var seg = [0];
    for (var i = 1; i < pts.length; i++) {
      seg.push(seg[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    }
    var total = seg[seg.length - 1];
    if (total <= 0) return null;

    function at(s) {
      for (var k = 1; k < seg.length; k++) {
        if (s <= seg[k]) {
          var t = (s - seg[k - 1]) / Math.max(1e-6, seg[k] - seg[k - 1]);
          var x = pts[k - 1][0] + (pts[k][0] - pts[k - 1][0]) * t;
          var y = pts[k - 1][1] + (pts[k][1] - pts[k - 1][1]) * t;
          var dx = pts[k][0] - pts[k - 1][0], dy = pts[k][1] - pts[k - 1][1];
          var m = Math.hypot(dx, dy) || 1;
          return [x, y, -dy / m, dx / m];        /* point plus unit normal */
        }
      }
      var last = pts[pts.length - 1], p2 = pts[pts.length - 2];
      var ddx = last[0] - p2[0], ddy = last[1] - p2[1], mm = Math.hypot(ddx, ddy) || 1;
      return [last[0], last[1], -ddy / mm, ddx / mm];
    }

    c.save();
    c.strokeStyle = ink;
    c.fillStyle = ink;
    c.lineCap = "butt";
    c.lineJoin = "miter";

    if (o.filled) {
      /* THE ONE FILLED STATE IN THE DECK. A constant width band along the path, drawn as a
       * polygon offset either side of it, so it is a PATH and not a sector. */
      var half = lw * 1.9;
      c.beginPath();
      var s, p;
      for (s = 0; s <= total; s += Math.max(2, total / 320)) {
        p = at(s); c.lineTo(p[0] + p[2] * half, p[1] + p[3] * half);
      }
      for (s = total; s >= 0; s -= Math.max(2, total / 320)) {
        p = at(s); c.lineTo(p[0] - p[2] * half, p[1] - p[3] * half);
      }
      c.closePath();
      c.fill();
      /* the divisions, cut OUT of the band in the ground so 24 stays countable */
      c.strokeStyle = o.cut || N.GROUND;
      c.lineWidth = Math.max(1.6, lw * 0.42);
      for (var d = 0; d <= n; d++) {
        var q = at(total * d / n);
        c.beginPath();
        c.moveTo(q[0] + q[2] * half, q[1] + q[3] * half);
        c.lineTo(q[0] - q[2] * half, q[1] - q[3] * half);
        c.stroke();
      }
    } else {
      /* HOLLOW. The run itself as a hairline, and a cross tick at every division. */
      c.lineWidth = Math.max(1.1, lw * 0.34);
      c.beginPath();
      c.moveTo(pts[0][0], pts[0][1]);
      for (var j = 1; j < pts.length; j++) c.lineTo(pts[j][0], pts[j][1]);
      c.stroke();
      c.lineWidth = lw;
      for (var e = 0; e <= n; e++) {
        var r = at(total * e / n);
        c.beginPath();
        c.moveTo(r[0] + r[2] * cross * 0.5, r[1] + r[3] * cross * 0.5);
        c.lineTo(r[0] - r[2] * cross * 0.5, r[1] - r[3] * cross * 0.5);
        c.stroke();
      }
    }
    c.restore();
    return { total: total, n: n, filled: !!o.filled };
  };

  /* ---------------------------------------------------------------- flat stock
   *
   * TYPE NEVER SITS ON A SCREEN, and a drawn page is where that rule gets broken, because the
   * page's own type is dark on light and the stock under it is the brightest thing in the frame,
   * which is exactly where a screen lays its heaviest marks. Frame 5's first render put eighteen
   * screen rules through eight lines of type and qa.py reported every one of them as a
   * strikethrough.
   *
   * This is laid in `over`, AFTER the screen has run, so the paper under the type is flat. It is
   * not a plate: a plate is an opaque rectangle put behind type to rescue art that was drawn
   * without knowing where the type goes. This is the page's own stock, and the page is the
   * subject.
   */
  N.stock = function (c, r, o) {
    o = o || {};
    var pad = o.pad == null ? 12 : o.pad;
    c.save();
    c.fillStyle = o.stock || N.STOCK;
    c.fillRect(r.x - pad, r.y - pad, r.w + pad * 2, r.h + pad * 2);
    c.restore();
    return { x: r.x - pad, y: r.y - pad, w: r.w + pad * 2, h: r.h + pad * 2 };
  };

  /* A two part contact shadow along the declared cast direction, so a thing sits ON the apron
   * rather than over it. */
  N.contact = function (cx, o) { return TXDECK.contact(cx, o); };

  /* A grey lifted or dropped by a factor, so one surface can take its own light without a frame
   * inventing a second palette. Clamped, because a factor over the top of the ramp is a blown
   * highlight the screen cannot print. */
  N.mixGrey = function (hex, k) {
    var c = [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
    var out = "#";
    for (var i = 0; i < 3; i++) {
      var v = Math.max(0, Math.min(255, Math.round(c[i] * k)));
      out += (v < 16 ? "0" : "") + v.toString(16);
    }
    return out;
  };

  global.TXNA = N;
})(typeof window !== "undefined" ? window : globalThis);
