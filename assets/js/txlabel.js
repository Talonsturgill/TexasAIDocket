/* txlabel.js — knockout-plate canvas-label helper (no dependencies).
 *
 * WHY THIS EXISTS. Labels drawn straight onto a scene canvas with cx.fillText()
 * are a BITMAP with no DOM node behind them. Every gate that walks render.py's
 * DOM text nodes -- text collisions, contrast estimates, the busy-art tripwire --
 * is structurally blind to them. So a canvas label can sit at 1.5:1 over a warm
 * ochre band, or two canvas labels can overprint into a single unreadable word,
 * and machine QA passes the deck with zero fails while a human reads it as
 * broken at a glance.
 *
 * The fix is not a brighter fill. It is an opaque chip drawn behind the label,
 * sized from the MEASURED string rather than a guessed constant. This is that
 * fix, committed once as reusable machinery so a cutaway, section or map deck
 * reaches for it instead of rediscovering the trap.
 *
 * The pixel-reading gates added later (art crossing glyphs) do see canvas ink,
 * so a bare canvas label now fails rather than passing silently. Use a plate
 * anyway: passing a gate by being caught by it is not the same as being legible.
 *
 * The guarantee: because the plate is an OPAQUE fill drawn under the glyphs,
 * the label's contrast is a function of (text colour, plate colour) ONLY,
 * independent of whatever art sits beneath. autoPlate (default) picks a
 * near-black or near-white plate from the text colour's luminance so the
 * on-pixel contrast clears a legible floor over any strata. A canvas label
 * is still second-best to DOM/SVG text (which stays vector in the PDF and is
 * visible to the QA gates); prefer DOM text where the layout allows, and use
 * this only for labels that must be authored in canvas coordinates
 * (dimension callouts, in-scene tags pinned to a drawn feature).
 *
 * Usage (include AFTER noise.js so it augments the same TX object):
 *   <script src="@@ASSETS@@/js/noise.js"></script>
 *   <script src="@@ASSETS@@/js/aklabel.js"></script>
 *   ...
 *   const r = TX.canvasLabel(cx, 430, 760, "DEMAND, JANUARY PEAK",
 *                            { color: "#8FB4FF", align: "left" });
 *   // r = {x,y,w,h} of the plate; check TX.rectsOverlap(r, prev) to keep
 *   // stacked in-scene labels from colliding.
 *
 * Contract: canvasLabel saves/restores the context (never leaks font,
 * fillStyle, textAlign, textBaseline). x,y is the anchor of the FIRST line's
 * baseline, positioned by `align` (left|center|right). Multi-line: pass an
 * array of strings. Returns the plate rect in canvas coordinates.
 */
(function (global) {
  "use strict";

  var TX = global.TX || (global.TX = {});

  function _relLum(rgb) {
    function c(x) { x /= 255; return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }
    return 0.2126 * c(rgb[0]) + 0.7152 * c(rgb[1]) + 0.0722 * c(rgb[2]);
  }

  function _parseColor(s) {
    if (!s) return [244, 248, 255];
    s = String(s).trim();
    var m;
    if ((m = s.match(/^#([0-9a-f])([0-9a-f])([0-9a-f])$/i)))
      return [parseInt(m[1] + m[1], 16), parseInt(m[2] + m[2], 16), parseInt(m[3] + m[3], 16)];
    if ((m = s.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i)))
      return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)];
    if ((m = s.match(/rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)/i)))
      return [parseFloat(m[1]), parseFloat(m[2]), parseFloat(m[3])];
    return [244, 248, 255];
  }

  function _roundRect(cx, x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    cx.beginPath();
    cx.moveTo(x + r, y);
    cx.arcTo(x + w, y, x + w, y + h, r);
    cx.arcTo(x + w, y + h, x, y + h, r);
    cx.arcTo(x, y + h, x, y, r);
    cx.arcTo(x, y, x + w, y, r);
    cx.closePath();
  }

  // Contrast ratio between two 0..255 rgb triples (WCAG-style).
  function contrast(a, b) {
    var la = _relLum(_parseColor(a)), lb = _relLum(_parseColor(b));
    var hi = Math.max(la, lb), lo = Math.min(la, lb);
    return (hi + 0.05) / (lo + 0.05);
  }

  function rectsOverlap(a, b, pad) {
    pad = pad || 0;
    return !(a.x + a.w + pad <= b.x || b.x + b.w + pad <= a.x ||
             a.y + a.h + pad <= b.y || b.y + b.h + pad <= a.y);
  }

  function canvasLabel(cx, x, y, text, opts) {
    opts = opts || {};
    var font = opts.font || "20px 'JetBrains Mono'";
    var color = opts.color || "#F4F8FF";
    var align = opts.align || "left";        // plate + text anchor
    var padX = opts.padX != null ? opts.padX : 11;
    var padY = opts.padY != null ? opts.padY : 7;
    var radius = opts.radius != null ? opts.radius : 5;
    var alpha = opts.plateAlpha != null ? opts.plateAlpha : 0.86;

    cx.save();
    cx.font = font;

    var lines = Array.isArray(text) ? text : [text];
    var tw = 0, i;
    for (i = 0; i < lines.length; i++) tw = Math.max(tw, cx.measureText(lines[i]).width);

    // Height from real glyph metrics, falling back to the font's px size.
    var sizePx = parseFloat(font) || 20;
    var mm = cx.measureText("Mg");
    var asc = mm.actualBoundingBoxAscent || sizePx * 0.74;
    var desc = mm.actualBoundingBoxDescent || sizePx * 0.24;
    var lh = opts.lineH || (asc + desc) * 1.4;
    var textH = asc + desc + (lines.length - 1) * lh;

    // Plate colour: caller override, else auto (opposite end of the luminance
    // range from the text) so the label always clears a legible floor.
    var plate;
    if (opts.plate) plate = _parseColor(opts.plate);
    else plate = _relLum(_parseColor(color)) >= 0.4 ? [4, 9, 17] : [238, 244, 252];

    var w = tw + padX * 2, h = textH + padY * 2;
    var px = align === "center" ? x - w / 2 : align === "right" ? x - w : x;
    var py = y - asc - padY;

    _roundRect(cx, px, py, w, h, radius);
    cx.fillStyle = "rgba(" + plate[0] + "," + plate[1] + "," + plate[2] + "," + alpha + ")";
    cx.fill();
    if (opts.border) {
      cx.lineWidth = opts.borderWidth || 1;
      cx.strokeStyle = opts.border;
      cx.stroke();
    }

    cx.fillStyle = color;
    cx.textBaseline = "alphabetic";
    var tx;
    if (align === "center") { cx.textAlign = "center"; tx = x; }
    else if (align === "right") { cx.textAlign = "right"; tx = px + w - padX; }
    else { cx.textAlign = "left"; tx = px + padX; }
    for (i = 0; i < lines.length; i++) cx.fillText(lines[i], tx, y + i * lh);

    cx.restore();
    return { x: px, y: py, w: w, h: h };
  }

  TX.canvasLabel = canvasLabel;
  TX.labelContrast = contrast;
  TX.rectsOverlap = rectsOverlap;
})(typeof window !== "undefined" ? window : globalThis);
