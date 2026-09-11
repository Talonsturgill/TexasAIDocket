/* txlayout.js — the ten layout archetypes, the rotation rules, and the house furniture.
 *
 * WHY THIS EXISTS (2026-09-11). Twenty one decks used one skeleton on every frame: a kicker at
 * the top, a headline under it, a small drawing under that, a source line at the bottom. The
 * flow critic called it "the same page nine times" and the fix was never going to be a nicer
 * drawing in the same slot. A magazine spread and a poster differ by where the IMAGE goes and
 * how much of the page it takes, and that decision has to be made per frame, on purpose, from a
 * short list, with a rule that stops the same choice being made twice in a row.
 *
 * THE TABLE below is the only copy the browser has, and `scripts/carousel/layout_check.py`
 * carries a Python copy that its self-test asserts against this file, so the planner and the
 * gate can never disagree about what a name means.
 *
 * ARCHETYPES (the image is the primary image the dossier declares, in a 1080 x 1350 frame):
 *
 *   FULL_BLEED          the image fills the frame edge to edge. Type sits in a reserve, one
 *                       band top or bottom, never a box in the middle
 *   SPLIT_HORIZON       one straight horizontal cut. Image on one side, at least 55 percent of
 *                       the height. Type on the other, on a flat ground
 *   TYPE_AS_OBJECT      the headline IS the image. Carved, cast, stacked, extruded, poured.
 *                       At most one per deck, because twice is a trick
 *   OBJECT_AND_CAPTION  one object drawn large on a ground plane with a horizon, a short
 *                       caption beside or under it. The poster
 *   DIAGRAM             a drawing annotated with leader lines and labels in the mono face.
 *                       The image is the thing explained, the labels are the type
 *   GRID                repeated units at true scale, the isotype. A count the reader can
 *                       count. The units ARE the image
 *   DOCUMENT            a drawn page, form, screen, ledger or letter is the subject, with its
 *                       own typography inside it. Type on the page is image, not caption
 *   MAP                 cartography. Texas, a county, a corridor, a site plan. Places named
 *   CLOSE_CROP          the subject cropped by at least two frame edges, at detail scale. The
 *                       reader is inside the thing
 *   FIGURE_SCALE        a person at true scale beside the thing, so the thing has a size
 *
 * ROTATION over a nine frame deck:
 *   no archetype twice in a row, at least five distinct, TYPE_AS_OBJECT at most once, and
 *   FULL_BLEED plus CLOSE_CROP at least two between them so the deck has frames the reader
 *   is inside rather than looking at.
 *
 * USAGE, at plan time in Node (a run checks its own sequence before it draws anything):
 *
 *   node -e 'require("./assets/js/txlayout.js"); console.log(TXLAYOUT.check(["FULL_BLEED", ...]))'
 *
 * USAGE, in a slide: `TXLAYOUT.mount(document.body, { kicker, counter, src })` writes three of
 * the four pieces of house furniture (the mono kicker, the counter, the source line) in the
 * fixed positions, so a frame's bespoke code is only ever the image and the headline and the
 * furniture is never drawn wrong.
 *
 * THE SITE LINE IS NEVER MOUNTED HERE, AND THE REASON IS A GATE. `coherence_check.check_site_line`
 * reads each slide's HTML FILE with a regex for `class="tx-site"` and holds the string to
 * `config/brand.yaml`. An element this function creates exists only in the DOM after the script
 * runs, so a slide that relied on it would print the site line and fail the gate on every frame.
 * Every slide carries the static line the shipped decks carry:
 *
 *   <div class="tx-site" id="site">texasaidocket.com</div>
 *
 * with `.tx-site { position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono",
 * monospace; font-size:24px; letter-spacing:0.07em; }`, and mount() refuses a `site` option so
 * nobody finds this out from a red gate.
 */
(function (global) {
  "use strict";

  var ARCHETYPES = ["FULL_BLEED", "SPLIT_HORIZON", "TYPE_AS_OBJECT", "OBJECT_AND_CAPTION", "DIAGRAM", "GRID", "DOCUMENT", "MAP", "CLOSE_CROP", "FIGURE_SCALE"];
  var ROTATION = {"max_consecutive": 1, "min_distinct": 5, "max_type_as_object": 1, "min_full_bleed_or_close_crop": 2, "min_primary_area": 0.30, "min_bleed_frames": 4};

  // The house furniture. Positions and sizes are the ones every shipped deck has used and the
  // coherence gate reads, so they are not options.
  var FURNITURE = {
    kicker: { left: 80, top: 80, size: 24, tracking: 0.09, maxWidth: 760 },
    counter: { right: 80, top: 80, size: 24, tracking: 0.09 },
    src: { left: 80, bottom: 80, size: 24, tracking: 0.07 },
    site: { right: 80, bottom: 80, size: 24, tracking: 0.07 }
  };
  // The furniture bands: the strips of frame the kicker, counter, source and site lines own.
  // A primary image may run under them only where it is kept quiet (see TXINK.reserve).
  var BANDS = { top: 130, bottom: 130 };

  function check(seq) {
    var problems = [];
    if (!seq || !seq.length) return ["no sequence"];
    for (var i = 0; i < seq.length; i++) {
      if (ARCHETYPES.indexOf(seq[i]) < 0) problems.push("frame " + (i + 1) + ": '" + seq[i] + "' is not an archetype");
      if (i > 0 && seq[i] === seq[i - 1]) problems.push("frames " + i + " and " + (i + 1) + " repeat " + seq[i]);
    }
    var distinct = {};
    seq.forEach(function (a) { distinct[a] = 1; });
    if (Object.keys(distinct).length < ROTATION.min_distinct && seq.length >= 6)
      problems.push("only " + Object.keys(distinct).length + " distinct archetypes; the rule is at least " + ROTATION.min_distinct);
    var tao = seq.filter(function (a) { return a === "TYPE_AS_OBJECT"; }).length;
    if (tao > ROTATION.max_type_as_object) problems.push("TYPE_AS_OBJECT " + tao + " times; at most " + ROTATION.max_type_as_object);
    var inside = seq.filter(function (a) { return a === "FULL_BLEED" || a === "CLOSE_CROP"; }).length;
    if (inside < ROTATION.min_full_bleed_or_close_crop && seq.length >= 6)
      problems.push("FULL_BLEED and CLOSE_CROP " + inside + " between them; at least " + ROTATION.min_full_bleed_or_close_crop);
    return problems;
  }

  // Writes the furniture into a slide. Colours are the caller's, because a dark frame and a
  // paper frame print them in different inks. Returns the four elements.
  function mount(root, o) {
    o = o || {};
    var ink = o.ink || "#1B1830";
    var mk = function (cls, text, pos) {
      var d = root.ownerDocument.createElement("div");
      d.className = cls;
      d.textContent = text;
      var s = d.style;
      s.position = "absolute"; s.fontFamily = '"JetBrains Mono", monospace'; s.fontSize = pos.size + "px";
      s.letterSpacing = pos.tracking + "em"; s.color = ink; s.lineHeight = "1.5"; s.whiteSpace = "nowrap";
      s.textTransform = cls === "kick" ? "uppercase" : "none";
      if (pos.maxWidth) { s.maxWidth = pos.maxWidth + "px"; s.whiteSpace = "normal"; }
      if (pos.left != null) s.left = pos.left + "px";
      if (pos.right != null) s.right = pos.right + "px";
      if (pos.top != null) s.top = pos.top + "px";
      if (pos.bottom != null) s.bottom = pos.bottom + "px";
      s.zIndex = o.z == null ? 20 : o.z;
      root.appendChild(d);
      return d;
    };
    var out = {};
    if (o.kicker) {
      out.kicker = mk("kick", o.kicker, FURNITURE.kicker);
      if (o.kicker2) { var b = root.ownerDocument.createElement("b"); b.style.display = "block"; b.style.fontWeight = "500"; b.style.color = o.ink2 || ink; b.textContent = o.kicker2; out.kicker.appendChild(b); }
    }
    if (o.counter) out.counter = mk("count", o.counter, FURNITURE.counter);
    if (o.src) out.src = mk("src", o.src, FURNITURE.src);
    if (o.site) throw new Error("TXLAYOUT.mount: the site line is static HTML, never mounted. coherence_check reads it from the file. Put <div class=\"tx-site\" id=\"site\">texasaidocket.com</div> in the slide.");
    return out;
  }

  // Where a type reserve goes for a given archetype, as a rect in frame px, so the primary
  // image can be planned to fill everything else.
  function reserve(arch, o) {
    o = o || {};
    var W = 1080, H = 1350, pad = 80;
    switch (arch) {
      case "FULL_BLEED": return o.top ? { x: 0, y: 0, w: W, h: 470 } : { x: 0, y: H - 520, w: W, h: 520 };
      case "SPLIT_HORIZON": return o.top ? { x: 0, y: 0, w: W, h: Math.round(H * 0.42) } : { x: 0, y: Math.round(H * 0.58), w: W, h: Math.round(H * 0.42) };
      case "OBJECT_AND_CAPTION": return { x: pad, y: H - 400, w: W - 2 * pad, h: 320 };
      case "FIGURE_SCALE": return { x: pad, y: 150, w: 620, h: 360 };
      case "CLOSE_CROP": return o.top ? { x: 0, y: 0, w: W, h: 430 } : { x: 0, y: H - 470, w: W, h: 470 };
      case "MAP": return { x: pad, y: H - 420, w: W - 2 * pad, h: 340 };
      case "GRID": return { x: pad, y: 150, w: W - 2 * pad, h: 300 };
      case "DIAGRAM": return { x: pad, y: 150, w: W - 2 * pad, h: 260 };
      case "DOCUMENT": return { x: pad, y: 150, w: W - 2 * pad, h: 230 };
      case "TYPE_AS_OBJECT": return { x: pad, y: H - 320, w: W - 2 * pad, h: 240 };
    }
    return { x: pad, y: 150, w: W - 2 * pad, h: 360 };
  }

  global.TXLAYOUT = { ARCHETYPES: ARCHETYPES, ROTATION: ROTATION, FURNITURE: FURNITURE, BANDS: BANDS, check: check, mount: mount, reserve: reserve };
})(typeof window !== "undefined" ? window : globalThis);
