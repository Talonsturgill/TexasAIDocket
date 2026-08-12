/* aktype.js — display-type fitting helper for slide code (no dependencies).
 *
 * Exists because of a recurring defect (runs through 2026-07-09): a large
 * Archivo/Unbounded display headline is set at a fixed font-size in a
 * container narrower than its longest line, so the headline SILENTLY wraps
 * one extra line down into the body/attribution block and machine_qa fails
 * it as a text-overprint. DESIGN_DOCTRINE section 2 prescribes a
 * "binary-search font-size" fit-to-box recipe, but every deck re-implemented
 * (or forgot) it. This is the one committed implementation.
 *
 * Note the frontier finding that motivated committing this (2026-07-09
 * typography scan): CSS `text-wrap: balance`/`pretty` only redistribute the
 * lines that naturally occur — per Chrome's own docs they give NO guarantee
 * that text stays within a line count and do NOT prevent overflow. Only a
 * measure-and-shrink pass guarantees "never more than N lines, never
 * overflow." That is what TX.fitText does. Binary search converges in ~8
 * probes (log2 of the size range), sub-millisecond.
 *
 * Usage (call INSIDE renderReady, AFTER fonts are ready so measurement uses
 * the real metrics):
 *
 *   <script src="@@ASSETS@@/js/aktype.js"></script>
 *   window.renderReady = new Promise(async (resolve) => {
 *     await document.fonts.ready;                       // REQUIRED before fitting
 *     TX.fitText(document.querySelector("h1"), { min: 44, max: 80, maxLines: 3 });
 *     resolve(true);
 *   });
 *
 * Contract: the element keeps its CSS width/height; fitText only lowers the
 * font-size (never above `max`) until the element renders in <= maxLines line
 * boxes AND does not overflow its box horizontally or (if the box has a fixed
 * height) vertically. It never enlarges past what fits, never throws, and if
 * even `min` cannot satisfy the constraint it clamps to `min` and sets
 * data-fit-overflow="1" on the element so a human/critic can see the box is
 * genuinely too small. Returns the fit report { size, lines, fit }.
 *
 * <br> line breaks are honored: a maxLines:3 headline authored with two <br>
 * is already 3 lines, so fitText only ever needs to shrink if a line ALSO
 * soft-wraps. This is exactly the run-2026-07-09 failure mode.
 */
(function (global) {
  "use strict";

  var TX = global.TX || (global.TX = {});

  // Count the rendered line boxes of an element (across its text nodes, nested
  // spans and <br>) and whether any line exceeds the element's content box.
  function measure(el) {
    var range = document.createRange();
    range.selectNodeContents(el);
    var rects = range.getClientRects();
    var tops = {};
    var n = 0;
    for (var i = 0; i < rects.length; i++) {
      var r = rects[i];
      if (r.width > 1 && r.height > 1) {
        var key = Math.round(r.top);
        if (!(key in tops)) { tops[key] = 1; n++; }
      }
    }
    // scrollWidth/scrollHeight vs client* is the canonical overflow probe.
    var overflowX = el.scrollWidth > el.clientWidth + 1;
    var overflowY = el.scrollHeight > el.clientHeight + 1;
    return { lines: n || 1, overflowX: overflowX, overflowY: overflowY };
  }

  /* Binary-search the largest font-size in [min, max] (px, resolved to 0.5px)
   * at which `el` fits `maxLines` line boxes with no horizontal overflow.
   * `respectHeight` (default: only when the element has a fixed/clipped height)
   * also forbids vertical overflow. Mutates el.style.fontSize; returns a report. */
  function fitText(el, opts) {
    if (!el) return { size: 0, lines: 0, fit: false };
    opts = opts || {};
    var min = opts.min != null ? opts.min : 24;
    var max = opts.max != null ? opts.max : 120;
    var maxLines = opts.maxLines != null ? opts.maxLines : 3;
    // Only enforce vertical overflow when the author gave the box a real
    // height cap (fixed height + hidden/clip overflow); otherwise height is
    // author-intended to grow and line count is the true constraint.
    var cs = getComputedStyle(el);
    var respectHeight = opts.respectHeight != null ? opts.respectHeight
      : (["hidden", "clip"].indexOf(cs.overflowY) !== -1);

    function fitsAt(px) {
      el.style.fontSize = px + "px";
      var m = measure(el);
      var ok = m.lines <= maxLines && !m.overflowX && (!respectHeight || !m.overflowY);
      return ok;
    }

    var lo = min, hi = max, best = null;
    // 0.5px resolution: ~8 iterations over a 40px range.
    for (var it = 0; it < 24 && hi - lo > 0.5; it++) {
      var mid = Math.round(((lo + hi) / 2) * 2) / 2;
      if (fitsAt(mid)) { best = mid; lo = mid; } else { hi = mid; }
    }
    if (best == null) {
      // Even the smallest tested size overflowed; check min explicitly.
      if (fitsAt(min)) { best = min; }
      else { best = min; el.style.fontSize = min + "px"; el.setAttribute("data-fit-overflow", "1"); }
    } else {
      el.style.fontSize = best + "px";
    }
    var fm = measure(el);
    return { size: best, lines: fm.lines, fit: !el.hasAttribute("data-fit-overflow") };
  }

  /* ---------------------------------------------------------------------
   * TX.svgPlate: size a knockout plate FROM the label instead of guessing.
   *
   * Why this exists (run 2026-07-29). Six mono labels shipped off their own
   * knockout plates across slides 04, 05 and 07, one of them sitting entirely
   * off its plate and one with the chip's border rule drawn through the "T" of
   * PERMITS. The scorer capped the deck at 6.9 of record on that single hard
   * fail. The cause was arithmetic, not taste: JetBrains Mono at 24px with
   * 0.10em tracking advances 16.8px per character and every plate had been
   * hand-sized at roughly 14, in the authoring shape
   *
   *     el('rect', { x: 580, y: y, width: 420, height: 48, ... });
   *     mono(594, y + 32, 'ABOUT 10% OF TX PERMITS', 24, '#F4F8FF');
   *
   * two independent hand-typed numbers that have to agree, and that stop
   * agreeing the moment anyone edits the string. Revision #3 of that run's
   * repair created a fresh instance by lengthening a legend without resizing
   * its chip. qa.py now DETECTS the mismatch (the 2026-07-29 svg_plates gate).
   * This makes it UNREACHABLE: measure the laid-out text, then build the rect.
   *
   * Measurement notes, from the 2026-07-29 typography scan:
   *  - getBBox() is the right primitive, not getComputedTextLength(): the
   *    latter returns only the horizontal ADVANCE (glyph widths plus
   *    letter-spacing and word-spacing, ignoring x adjustments), so it gives
   *    no height and no anchor-correct origin. getBBox gives the laid-out box
   *    in the element's own user space, which is what a plate must contain.
   *    https://developer.mozilla.org/en-US/docs/Web/API/SVGTextContentElement
   *  - getBBox EXCLUDES stroke, so a stroked/haloed label needs half its
   *    stroke-width added back. This helper does that.
   *  - Headless Chrome measures SVG text differently from desktop Chrome
   *    (puppeteer#814). Irrelevant here by construction: the same browser
   *    measures the label and screenshots the slide, and qa.py grades the
   *    screenshot's own geometry, so the plate is correct in the only
   *    rendering that ships.
   *  - Leading/trailing whitespace in the text content corrupts the box in
   *    every engine, so it is reported (console.error becomes a qa.py WARN).
   *
   * Usage (inside renderReady, AFTER `await document.fonts.ready`, and after
   * the <text> is in the document; a plate sized against fallback metrics is
   * the same bug in a new costume):
   *
   *   const t = mono(594, y + 32, 'ABOUT 10% OF TX PERMITS', 24, '#F4F8FF');
   *   TX.svgPlate(t, { padX: 14, padY: 12, fill: 'rgba(13,9,6,0.94)',
   *                    stroke: 'rgba(138,147,155,0.85)', strokeWidth: 1.25 });
   *
   * The rect is inserted as the text's IMMEDIATELY PRECEDING SIBLING, which is
   * both the correct SVG paint order (no z-index in SVG, document order is the
   * stack) and exactly the shape render.py's plate probe looks for. It also
   * carries data-plate="1" so a future gate can identify plates by declaration
   * rather than by the last-overlapping-preceding-rect heuristic.
   *
   * Throws a named TypeError on misuse (a page error is a render.py hard fail,
   * which is the correct loudness for "your plate was never built").
   * Returns the <rect>.
   */
  var SVGNS = "http://www.w3.org/2000/svg";

  function pad2(v, dflt) {
    if (v == null) return [dflt, dflt];
    if (Array.isArray(v)) return [num(v[0], dflt), num(v[1], dflt)];
    return [num(v, dflt), num(v, dflt)];
  }

  function num(v, dflt) {
    var n = parseFloat(v);
    return isFinite(n) ? n : dflt;
  }

  function svgPlate(textEl, opts) {
    opts = opts || {};
    if (!textEl || !textEl.tagName || textEl.tagName.toLowerCase() !== "text") {
      throw new TypeError("TX.svgPlate: first argument must be an SVG <text> element, got " +
        (textEl && textEl.tagName ? textEl.tagName : String(textEl)));
    }
    if (!textEl.parentNode) {
      throw new TypeError("TX.svgPlate: the <text> is not in the document yet, so it has no laid-out box. Append it first, then plate it.");
    }
    var raw = textEl.textContent || "";
    if (!raw.trim()) {
      throw new TypeError("TX.svgPlate: the <text> is empty, so there is nothing to measure.");
    }
    if (raw !== raw.trim()) {
      // Known cross-engine defect: leading/trailing whitespace skews the box.
      console.error("TX.svgPlate: text content has leading or trailing whitespace ('" +
        raw.slice(0, 40) + "'), which measures wrong in every engine. Trim it.");
    }
    // getBBox ignores stroke; a haloed label paints half its stroke outside.
    var cs = null;
    try { cs = getComputedStyle(textEl); } catch (e) { cs = null; }

    // NO runtime font-readiness guard here, deliberately. Two were tried on
    // 2026-07-29 and both cried wolf on correct usage: document.fonts.status
    // flips back to "loading" whenever any face begins fetching, including one
    // this very label just triggered (3 of 4 correct calls warned), and
    // document.fonts.check() returned false for a loaded, rendering face
    // (4 of 4 warned). A guard that cannot tell correct usage from incorrect
    // usage only teaches authors to ignore QA warnings.
    //
    // The real protection is downstream and objective: qa.py's svg_plates gate
    // measures the SHIPPED render, so a plate sized from fallback metrics shows
    // up as a containment failure on the actual pixels. Await
    // document.fonts.ready before plating because the doc comment says so, and
    // the gate will catch you if you do not.

    var b = textEl.getBBox();
    if (!(b.width > 0.5) || !(b.height > 0.5)) {
      throw new TypeError("TX.svgPlate: measured a zero box for '" + raw.slice(0, 40) +
        "' (hidden, display:none, or not yet laid out).");
    }

    var sw = 0;
    if (cs && cs.stroke && cs.stroke !== "none") sw = num(cs.strokeWidth, 0) / 2;

    var px = pad2(opts.padX, 14);
    var py = pad2(opts.padY, 10);
    var x = b.x - px[0] - sw;
    var y = b.y - py[0] - sw;
    var w = b.width + px[0] + px[1] + sw * 2;
    var h = b.height + py[0] + py[1] + sw * 2;

    // A minimum size grows the plate symmetrically, so a right- or
    // middle-anchored label stays centred on its own plate.
    var minW = num(opts.minWidth, 0), minH = num(opts.minHeight, 0);
    if (minW > w) { x -= (minW - w) / 2; w = minW; }
    if (minH > h) { y -= (minH - h) / 2; h = minH; }

    var rect = document.createElementNS(SVGNS, "rect");
    rect.setAttribute("x", round2(x));
    rect.setAttribute("y", round2(y));
    rect.setAttribute("width", round2(w));
    rect.setAttribute("height", round2(h));
    rect.setAttribute("fill", opts.fill != null ? opts.fill : "rgba(13,9,6,0.94)");
    if (opts.stroke) {
      rect.setAttribute("stroke", opts.stroke);
      rect.setAttribute("stroke-width", opts.strokeWidth != null ? opts.strokeWidth : 1.25);
      if (opts.strokeDasharray) rect.setAttribute("stroke-dasharray", opts.strokeDasharray);
    }
    if (opts.rx != null) rect.setAttribute("rx", opts.rx);
    if (opts.opacity != null) rect.setAttribute("opacity", opts.opacity);
    if (opts.className) rect.setAttribute("class", opts.className);
    // Same coordinate frame as the label it backs.
    if (textEl.hasAttribute("transform")) {
      rect.setAttribute("transform", textEl.getAttribute("transform"));
    }
    rect.setAttribute("data-plate", "1");
    if (opts.attrs) {
      for (var k in opts.attrs) {
        if (Object.prototype.hasOwnProperty.call(opts.attrs, k)) rect.setAttribute(k, opts.attrs[k]);
      }
    }

    textEl.parentNode.insertBefore(rect, textEl);
    return rect;
  }

  function round2(v) { return Math.round(v * 100) / 100; }

  /* Plate a whole set at once: a CSS selector (queried document-wide or under
   * `root`), a NodeList, or an array of <text> elements. Returns the rects. */
  function svgPlateAll(sel, opts, root) {
    var nodes;
    if (typeof sel === "string") nodes = (root || document).querySelectorAll(sel);
    else if (sel && sel.length != null) nodes = sel;
    else if (sel) nodes = [sel];
    else nodes = [];
    var out = [];
    for (var i = 0; i < nodes.length; i++) out.push(svgPlate(nodes[i], opts));
    return out;
  }

  TX.fitText = fitText;
  TX.measureLines = measure;
  TX.svgPlate = svgPlate;
  TX.svgPlateAll = svgPlateAll;
})(typeof window !== "undefined" ? window : globalThis);
