/* firstlight.js — the chassis for carousel No. 29 (2026-09-19).
 *
 * WHAT THIS IS. The deck "THE CRIME WAS ALREADY IN THE WATER CODE" follows one September
 * morning down one Texas water line, from the instrument anybody can wade out to, to the one
 * nobody reads. Nine frames share one light, one stock and one way of seating type, and this
 * file is those three things and nothing else. Every frame's COMPOSITION is written per frame.
 *
 * THE WORLD. A HILL COUNTRY WATER SUPPLY RESERVOIR ON THE EDWARDS PLATEAU AND THE FORTY
 * MINUTES THAT FOLLOW IT DOWNSTREAM. First light, clear, no wind on the water yet. Limestone
 * ledges, ashe juniper on the far ridge, a galvanized windmill on the skyline, caliche dust on
 * every horizontal surface. It is DAYLIGHT and that is argued rather than defaulted: the last
 * six decks are dark interiors at night, and this story's subject is a thing a person stands
 * beside in the open. The stock stays dark. What changes across nine frames is how much lit
 * sky is in them.
 *
 * THE LIGHT, IN WORDS A FRAME AUTHOR CAN CHECK A DRAWING AGAINST. THE KEY IS LOW IN THE EAST
 * OFF THE CAMERA'S LEFT SHOULDER, AT 14 DEGREES ABOVE THE PLANE. So every lit face in this
 * deck is a LEFT face, every right face is the deck's dark side, and every cast runs RIGHT and
 * away at about four times the object's own height. A 1.7 m person throws about 6.8 m. If a
 * drawn object has a shadow shorter than itself, or no contact where it meets ground or water,
 * that frame is wrong and gets redrawn rather than tuned. Say it in those words, because
 * "az -68" is not a sentence a drawing can be checked against.
 *
 * THE MOTIF, AND IT CHANGES STATE ACROSS THE DECK. THE HELD WATER. One stock tank, seen five
 * times at five distances, and each time it is further from the reader and closer to the thing
 * that wants its number. On the pad beside a hall, then a few metres inside a fence a reader
 * can't cross, then as the line the answer travels along, then under a tower the state plan
 * needs a figure for, then small and far at the close with a date on it.
 *
 * THIS PARAGRAPH DESCRIBED A DIFFERENT DECK UNTIL ROUND 1 and a judge caught it by reading the
 * prose against the frames. It named a staff gauge, a pump, a brass register in a hole in the
 * ground and the state's own instrument shelter, none of which is drawn anywhere in these nine
 * frames. The functional `declare` below was correct the whole time and ran through all nine,
 * so nothing rendered wrong. What was wrong is that the one place a frame author goes to find
 * out what deck they are drawing was telling them about another one. CLAUDE.md says a wrong
 * measurement in a file is worse than none, because the next reader inherits it and stops
 * looking, and a wrong DESCRIPTION is the same defect wearing prose.
 *
 * THE ACCENT LAW, AND IT IS THE STRICTEST THING IN THIS FILE.
 *
 *   COMAL ONLY EVER LANDS ON WATER SOMEBODY HOLDS A NUMBER FOR.
 *
 * A gauged stock tank gets it, on frames 1, 2, 6 and 9. Frame 5 gets it on the route itself,
 * because the route IS that number moving between the three parties, and that is the one
 * extension of the law in the deck. Water nobody has counted does not, and neither does a
 * building whose water is the whole question, so frames 3, 4, 7 and 8 carry none at all. A
 * reader who swipes twice sees that the colour only turns up where somebody holds a figure.
 * It never touches sky, concrete or metal, because at L* 46 it is a mid value and would vanish
 * on a lit surface. #2A7A9E is `comal` in config/brand.yaml,
 * where its own comment reads "the water itself". It is not bluebonnet, which is a violet
 * flower spent two decks ago, and not signal_link, which on this project's own site means a
 * link out to a source and would be a lie on a slide.
 *
 * THE FRAMES DRAW IN GREYS. Every scene is drawn into TXINK's offscreen twin in greys and the
 * print maps tone to ink on the deck's stock. That is why this file hands out a GREY SCALE
 * rather than a colour ramp: a frame that picks its own colours has left the deck. The one
 * place real colour is painted is `over`, where the accent and the type reserve go, after the
 * screen has run.
 */
(function (global) {
  "use strict";

  if (!global.TXDECK) throw new Error("firstlight.js needs txdeck.js loaded first");

  /* ONE DECLARATION, AND IT IS THE ONLY ONE IN THE DECK. Nine frames can't hold nine lights. */
  TXDECK.declare({
    world: "firstlight",
    light: { az: -68, el: 14, keyToFill: 6.0 },
    ground: "#18222B",
    material: "#8A9299",
    accent: "#2A7A9E",
    grade: {
      exposure: -0.02,
      saturation: 1.04,
      contrast: 1.15,
      filmic: true,
      lift: [0.012, 0.016, 0.024],   /* shadows to the limestone's blue */
      gain: [1.030, 1.010, 0.974],   /* highlights to first light */
      vignette: 0.20,
      bloom: { threshold: 0.78, strength: 0.26, radius: 9 },
      /* GRAIN AT 0.012 RATHER THAN THE HOUSE 0.044, AND THE REASON IS A MEASUREMENT.
       * This is the first deck to run TXINK.print's full halftone across the whole of all nine
       * frames, and its vector PDF came out at 68.7 MB against 6 to 14 MB for every deck before
       * it. Three hypotheses were measured. A coarser screen cell was worth 5 MB, a raised
       * screen floor and a higher gamma were worth nothing at all, and CUTTING THE FILM GRAIN
       * AND THE DITHER WAS WORTH 9 MB. Per-pixel noise over a frame that is already maximum
       * entropy is the one knob that moved, so it is the one that was turned.
       * It does not get the file inside the 2 to 25 MB target. What remains is the halftone
       * itself and it is the deck's register, so the size is DISCLOSED rather than cured, and
       * the diagnosis is in the upgrade backlog for somebody with a render-side fix. */
      grain: { amount: 0.012, size: 3, seed: 20260919 },
      aberration: 0,
      dither: false,
      sharpen: 0.34
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;

  /* ------------------------------------------------------------------- stock
   *
   * The paper and the ink, once, for all nine frames. A screen is the deck's STOCK and
   * changing stock between frames is a different print job rather than variety.
   *
   * #18222B is the shaded face of an Edwards limestone ledge at the waterline before the sun
   * clears the far ridge. It is bluer and two stops lighter than the dark teal spent on
   * September 17th and carries none of the warm neutral spent on the 13th.
   *
   * #E6DFCC is the calcium rim a reservoir leaves on rock and on a galvanized standpipe. One
   * shade cooler than house limestone so it sits on a blue-grey stock rather than fighting it.
   */
  N.GROUND = "#18222B";
  N.INK    = "#E6DFCC";
  N.ACCENT = "#2A7A9E";   /* comal, the water itself */
  N.LIT    = "#8FE0F0";   /* comal_lit, the surface where water meets air. Used once at most */
  N.DEK    = "#B4B4A6";
  N.RULE   = "#9C9C90";   /* the furniture, one pale ink on all nine frames */
  N.TONER  = "#22303A";   /* type printed ON a drawn page, and only there */

  /* HALFTONE, CELL 7, ON ALL NINE, AND THE SCREEN WAS CHOSEN BY ARITHMETIC RATHER THAN TASTE.
   *
   * Stipple is the register this world wants. Limestone, caliche dust, galvanized steel and a
   * water surface are all grain, and the field guide plate is the obvious answer. It is the
   * wrong answer here and the reason is measured rather than argued.
   *
   * A SCREEN'S WHITE FIELD CEILING BOUNDS A FRAME'S MEDIAN. On 2026-09-15 the ceilings were
   * measured on a dark ground at L* 26.7 for stipple c5, 45.5 for hatch and 82.7 for halftone
   * c6. This deck's argument is that the light ARRIVES across nine frames, so its closing
   * frames have to reach the forties. A stipple deck physically can't print them, and no amount
   * of drawing brighter fixes a miss the press can't make. Carousel no. 25 paid for that once.
   *
   * So the stock is halftone, one cell for the deck, and the probe frame in Phase 10.5 prints a
   * white field through THIS configuration and records the ceiling BEFORE the value arc is
   * committed. The arc is written against the press. The press is never chased to the arc. */
  N.SCREEN = { mode: "halftone", cell: 7, angle: 22, gamma: 1.16, floor: 0.04 };
  N.EDGES  = { threshold: 18, width: 1.3, alpha: 0.78, dx: 1.1, dy: -0.6 };

  /* THE GREY SCALE THE TWIN IS DRAWN IN, dark to light. A frame reaches for these by name so
   * nine frames can't each invent their own tonal separation. The gaps are deliberate: the
   * September 16th lesson is that nothing contrasts against a mid tone, so there is a hole in
   * the middle of this scale and objects are separated across it rather than inside it. */
  N.G = {
    void:   "#000000",   /* the deepest dark. A vault's right wall, a ceiling */
    deep:   "#111820",   /* shadowed rock, the underside of things */
    dark:   "#232B33",   /* a dark side facing away from the key */
    shade:  "#3A424A",   /* ground plane in shadow, water in shadow */
    mid:    "#5A6068",   /* NOT for a subject against the ground. Terrain only */
    stone:  "#7C8088",   /* limestone, concrete, the lit ground plane */
    metal:  "#A6A8AC",   /* galvanized steel, a lit flank */
    bright: "#D2D2CE",   /* a lit face taking the key square on */
    glare:  "#F2F2EE"    /* the water's lit band and the sky at the horizon. Sparingly */
  };

  /* --------------------------------------------------------------------- ramp
   *
   * One ramp, off the deck's material, for the few marks painted in real colour in `over`.
   * The print path does not use it and most frames never call it.
   */
  N.RAMP = TXDECK.ramp(9, { Lmin: 0.06, Lmax: 0.82, ambientHue: 232, drift: 12 });
  N.pick = function (i) { return TXDECK.pick(N.RAMP, i); };

  /* -------------------------------------------------------------------- scene
   *
   * A TXSCENE carrying THIS DECK'S light, so a frame can't set up a camera lit from anywhere
   * else. Standing eye is 1.65 m and that is the deck's default, because a person standing at
   * the water is the reader's position in this story.
   */
  N.scene = function (a, o) {
    if (!global.TXSCENE) throw new Error("firstlight.scene needs txscene.js on this frame");
    o = o || {};
    var d = TXDECK.deck();
    return TXSCENE.create(a, {
      w: N.W, h: N.H,
      eye:     o.eye     == null ? 1.65 : o.eye,
      horizon: o.horizon == null ? 608  : o.horizon,
      f:       o.f       == null ? 820  : o.f,
      sky:     o.sky     || N.G.void,
      fogZ:    o.fogZ    == null ? 1e9 : o.fogZ,
      light:   { az: d.light.az, el: d.light.el }
    });
  };

  /* -------------------------------------------------------------------- print
   *
   * THE DECK'S STOCK, HANDED TO A FRAME. A frame passes its own `draw` and its own `over` and
   * gets the deck's paper, ink, screen and contour. This is house furniture in the sense the
   * chassis law means: it hands a frame the press, it does not decide what goes through it.
   */
  N.print = function (cx, o) {
    if (!global.TXINK) throw new Error("firstlight.print needs txink.js on this frame");
    TXINK.print(cx, {
      ground: N.GROUND,
      ink:    N.INK,
      fibre:  0.05,
      seed:   o.seed == null ? 19 : o.seed,
      screen: N.SCREEN,
      edges:  N.EDGES,
      draw:   o.draw,
      over:   o.over
    });
  };

  /* ---------------------------------------------------------------------- sky
   *
   * THE LIT SKY ABOVE THE HORIZON, drawn into the twin in greys. This is the deck's value arc
   * made of one thing: the amount of light in the sky rises monotonically across nine frames
   * and nothing else about the stock moves. `t` runs 0 at first light to 1 at full morning.
   *
   * THE LIGHT IS PUSHED INTO THE LAST FIFTH OF THE GRADIENT, AND THAT IS MEASURED RATHER THAN
   * STYLED. The first cut ran a smooth ramp from the top of the frame to the horizon, and the
   * probe render came back with the headline, the date and the dek all struck by the screen's
   * own dots, the date at a contrast of 1.4 against a floor of 4.5. The type was sitting on a
   * lit, screened sky, which is the oldest rule in this system said backwards.
   *
   * At first light the glow is a BAND at the horizon and the zenith is still night, so the
   * physically true gradient is also the one that leaves the upper frame dark enough to set
   * type on. The reserve is the scene's own construction rather than a hole punched in a light,
   * which is what the header of this file promised and what the first cut did not deliver. */
  N.sky = function (a, S, t) {
    var yh = S.groundY(1e6);
    var g = a.createLinearGradient(0, 0, 0, yh);
    var lo = 0.010 + 0.020 * t;   /* the zenith, still night even at full morning */
    var mid = 0.030 + 0.075 * t;
    var hi = 0.34 + 0.56 * t;     /* the band at the horizon, and it is only a band */
    g.addColorStop(0.00, "rgba(255,255,255," + lo.toFixed(3) + ")");
    g.addColorStop(0.74, "rgba(255,255,255," + mid.toFixed(3) + ")");
    g.addColorStop(0.90, "rgba(255,255,255," + (mid + (hi - mid) * 0.26).toFixed(3) + ")");
    g.addColorStop(1.00, "rgba(255,255,255," + hi.toFixed(3) + ")");
    a.fillStyle = N.G.void;
    a.fillRect(0, 0, N.W, yh);
    a.fillStyle = g;
    a.fillRect(0, 0, N.W, yh);
    return yh;
  };

  /* -------------------------------------------------------------------- water
   *
   * A WATER PLANE IN GREYS, with the key's specular band running off the left where the sun
   * is. Returns the horizon y so a frame can hang things on it.
   */
  N.water = function (a, S, o) {
    o = o || {};
    var yh = S.groundY(1e6);
    var yb = o.bottom == null ? N.H : o.bottom;
    a.fillStyle = o.fill || N.G.shade;
    a.fillRect(0, yh, N.W, yb - yh);
    /* the lit band, wide at the horizon and narrowing toward the camera, off the left */
    var band = a.createLinearGradient(0, yh, N.W * 0.78, yh + (yb - yh) * 0.55);
    band.addColorStop(0.00, "rgba(255,255,255," + (o.glare == null ? 0.34 : o.glare) + ")");
    band.addColorStop(0.55, "rgba(255,255,255,0.09)");
    band.addColorStop(1.00, "rgba(255,255,255,0)");
    a.fillStyle = band;
    a.fillRect(0, yh, N.W, yb - yh);
    return yh;
  };

  /* ------------------------------------------------------------------- ripple
   *
   * Horizontal broken rules on a water plane, denser near the camera, seeded. A water surface
   * with no marks on it reads as a floor.
   */
  N.ripple = function (a, yh, yb, seed, ink) {
    var R = TX.rng(seed == null ? 919 : seed);
    a.save();
    a.strokeStyle = ink || "rgba(255,255,255,0.16)";
    for (var y = yh + 6; y < yb; y += 4 + (y - yh) * 0.035) {
      var w = 40 + (y - yh) * 1.6;
      var x = R() * N.W;
      a.lineWidth = 0.8 + (y - yh) * 0.004;
      for (var k = 0; k < 3; k++) {
        a.beginPath();
        a.moveTo(x, y);
        a.lineTo(x + w * (0.4 + R() * 0.8), y);
        a.stroke();
        x = (x + w * 1.7 + R() * 180) % N.W;
      }
    }
    a.restore();
  };

  /* ------------------------------------------------------------------ reserve
   *
   * THE FURNITURE BAND, faded to paper so type never sits on a screen. This is the deck's
   * reserve and a frame passes only how deep it goes. A frame whose scene already keeps its
   * type zone dark by construction passes `bottom: 0` and uses nothing.
   */
  N.reserve = function (c, o) {
    o = o || {};
    TXINK.reserve(c, {
      ground: N.GROUND,
      top: o.top == null ? 0 : o.top,
      topSolid: o.topSolid == null ? 0 : o.topSolid,
      bottom: o.bottom == null ? 200 : o.bottom,
      bottomSolid: o.bottomSolid == null ? 130 : o.bottomSolid
    });
  };

  /* ------------------------------------------------------------------- casts
   *
   * How long a cast runs, from the deck's own elevation, so no frame guesses. At 14 degrees
   * this returns about 4.0 times the height, which is the number the header states in words.
   */
  N.cast = function (metres) { return TXDECK.castLen(metres); };
  N.castDir = function () { return TXDECK.castDir(); };

  global.TXFL = N;
})(this);
