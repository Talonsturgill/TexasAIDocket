#!/usr/bin/env python3
"""render.py — deterministic slide renderer for Texas AI Docket LinkedIn carousels.

Renders per-slide HTML files to exact-size PNGs via headless Chromium
(pre-installed in the cloud environment), and extracts an objective in-page
QA report (console/page errors, missing fonts, text-node geometry, clipped
or offscreen text) that downstream gates consume.

Conventions the slide HTML must follow (see SKILL.md for the full contract):
  - One file per slide, named  slide-01.html, slide-02.html, ...
  - Canvas is the viewport: design for exactly 1080x1350 CSS px (4:5).
  - Reference committed assets with the @@ASSETS@@ token, e.g.
      <link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
      <script src="@@ASSETS@@/js/noise.js"></script>
      fetch("@@ASSETS@@/geo/tx-counties.topo.json")
    The renderer resolves the token to an absolute file:// path.
  - NO external URLs (no CDNs, no Google Fonts, no http(s) at all).
  - If artwork draws asynchronously (canvas animation frames, fetched
    geodata), set  window.renderReady = new Promise(...)  and resolve it
    when the final frame is painted. The renderer awaits it (30s cap).

Usage:
  python .claude/skills/carousel-engine/render.py \
      --slides-dir out/run/slides --out-dir out/run/render [--scale 2] [--only 2,5]

Exit codes: 0 = all slides rendered (warnings possible; read the report),
            1 = at least one slide hard-failed (JS error, timeout, missing PNG).
Writes: <out-dir>/slide-XX.png + <out-dir>/render_report.json
"""

import argparse
import glob
import json
import re
import shutil
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# How many characters of each text node the report stores. See the report header note.
TEXT_WINDOW = 320

REPO_ROOT = Path(__file__).resolve().parents[3]
ASSETS_DIR = REPO_ROOT / "assets"

CHROMIUM_ARGS = [
    "--allow-file-access-from-files",   # lets slides fetch() committed geodata
    "--hide-scrollbars",
    "--force-color-profile=srgb",
    "--disable-lcd-text",               # subpixel AA looks wrong in screenshots
    "--font-render-hinting=none",       # fixes headless kerning/letter-spacing bugs
    "--enable-unsafe-swiftshader",      # software WebGL (experimental; probe before relying on it)
]

# Instrument canvas text BEFORE any slide script runs (add_init_script runs
# before all page scripts). Canvas fillText/strokeText ink is a raster bitmap:
# invisible to render.py's DOM walk, to copy_sync_check, to the LinkedIn ranker,
# and to accessibility, and it pixelates in the vector PDF. We record every
# non-empty text call so qa.py can WARN when a slide draws MEANINGFUL text on
# canvas (2026-07-19: S7 loop labels + S8 annotations were cx.fillText and had
# to be converted to DOM by hand; no gate saw the unauthored ones). The wrapper
# only observes and forwards; it never alters the drawn frame.
CANVAS_TEXT_HOOK_JS = """
(() => {
  try {
    window.__akCanvasText = [];
    const proto = window.CanvasRenderingContext2D && window.CanvasRenderingContext2D.prototype;
    if (!proto) return;
    for (const fn of ['fillText', 'strokeText']) {
      const orig = proto[fn];
      if (typeof orig !== 'function') continue;
      proto[fn] = function (text) {
        try {
          const s = (text == null ? '' : String(text));
          if (s.trim().length && window.__akCanvasText.length < 500) {
            window.__akCanvasText.push({ text: s.slice(0, __TEXT_WINDOW__), fn: fn, font: this.font || '' });
          }
        } catch (e) {}
        return orig.apply(this, arguments);
      };
    }
  } catch (e) {}
})();
"""

IN_PAGE_QA_JS = """
() => {
  const W = window.innerWidth, H = window.innerHeight;
  const out = { text_nodes: [], overflow_warnings: [], fonts_missing: [], body_overflow: false };
  const de = document.documentElement, b = document.body;
  // data-breather on <body> declares this slide a deliberate rest beat, which
  // demotes qa.py's frame-balance FAIL to a WARN. Not a free pass: the dossier
  // gate cross-checks that the storyboard actually declared this slide a
  // breather, so the attribute can only ratify a plan, never invent one.
  out.breather = !!(b && b.hasAttribute("data-breather"));
  if (de.scrollWidth > W + 1 || de.scrollHeight > H + 1 ||
      (b && (b.scrollWidth > W + 1 || b.scrollHeight > H + 1))) {
    out.body_overflow = true;
  }
  const seenFam = new Set();
  const recorded = new Map();   // element -> index in out.text_nodes (for ancestry)
  const walk = document.createTreeWalker(document.body || de, NodeFilter.SHOW_ELEMENT);
  let el;
  while ((el = walk.nextNode())) {
    const hasText = Array.from(el.childNodes).some(
      n => n.nodeType === 3 && n.textContent.trim().length > 0);
    if (!hasText) continue;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity) === 0) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    // 320, NOT 80. `aggregate_check` scans this report for computed figures, and at 80 it
    // structurally could not see past the 80th character of any sentence. The 2026-08-19
    // deck is the proof: slide 1 stored as "...how every large load was class", so the
    // phrase "That date passed 12 days ago" was invisible to the gate that exists to catch
    // an invented number. The scorer found it, no gate could have. `copy_sync` truncates
    // authored strings to the same window before comparing, so widening only widens what
    // both can see.
    const txt = el.textContent.trim().replace(/\\s+/g, " ").slice(0, __TEXT_WINDOW__);
    const fs = parseFloat(cs.fontSize);
    const fam = cs.fontFamily.split(",")[0].trim().replace(/["']/g, "");
    // For SVG text the ink is `fill`, not CSS `color`; the fill attribute or
    // computed fill is the real text color the contrast check must use.
    const isSvgText = el.namespaceURI === "http://www.w3.org/2000/svg";
    const inkColor = isSvgText ? (cs.fill || cs.getPropertyValue("fill") || cs.color) : cs.color;
    // Per-line rects of the element's DIRECT text nodes: the collision gate
    // compares line boxes, not block bboxes (block bboxes overlap on
    // whitespace and false-positive). SVG text keeps its bbox (single-line
    // labels; Range rects are unreliable in SVG).
    let lines = [];
    if (!isSvgText) {
      try {
        const range = document.createRange();
        for (const n of el.childNodes) {
          if (n.nodeType === 3 && n.textContent.trim().length > 0) {
            range.selectNodeContents(n);
            for (const lr of range.getClientRects()) {
              if (lr.width > 1 && lr.height > 1)
                lines.push([Math.round(lr.x), Math.round(lr.y),
                            Math.round(lr.width), Math.round(lr.height)]);
            }
          }
        }
      } catch (e) {}
    }
    if (!lines.length) lines = [[Math.round(r.x), Math.round(r.y),
                                 Math.round(r.width), Math.round(r.height)]];
    // recorded ancestors, so nested text elements are never compared
    const anc = [];
    for (let p = el.parentElement; p; p = p.parentElement) {
      if (recorded.has(p)) anc.push(recorded.get(p));
    }
    const node = {
      text: txt,
      x: Math.round(r.x), y: Math.round(r.y),
      w: Math.round(r.width), h: Math.round(r.height),
      font_px: Math.round(fs * 10) / 10,
      weight: cs.fontWeight,
      family: fam,
      color: inkColor,
      decorative: el.hasAttribute("data-decorative") ||
                  (el.closest && !!el.closest("[data-decorative]")),
      overlap_ok: el.hasAttribute("data-overlap-ok") ||
                  (el.closest && !!el.closest("[data-overlap-ok]")),
      lines: lines,
      anc: anc
    };
    recorded.set(el, out.text_nodes.length);
    out.text_nodes.push(node);
    if (!node.decorative) {
      if (r.x < -1 || r.y < -1 || r.right > W + 1 || r.bottom > H + 1) {
        out.overflow_warnings.push({ kind: "offscreen", text: txt,
          detail: `bbox ${Math.round(r.x)},${Math.round(r.y)} ${Math.round(r.width)}x${Math.round(r.height)} vs ${W}x${H}` });
      }
      if (el.scrollWidth > el.clientWidth + 2 && ["hidden","clip"].includes(cs.overflowX)) {
        out.overflow_warnings.push({ kind: "clipped-x", text: txt,
          detail: `scrollWidth ${el.scrollWidth} > clientWidth ${el.clientWidth}` });
      }
      if (el.scrollHeight > el.clientHeight + 2 && ["hidden","clip"].includes(cs.overflowY)) {
        out.overflow_warnings.push({ kind: "clipped-y", text: txt,
          detail: `scrollHeight ${el.scrollHeight} > clientHeight ${el.clientHeight}` });
      }
      if (fs < 24) {
        out.overflow_warnings.push({ kind: "tiny-text", text: txt,
          detail: `font-size ${fs}px < 24px mobile floor (mark data-decorative if intentional)` });
      }
    }
    // Probe the FACE ACTUALLY USED: include the computed font-style so an
    // italic-only display face (e.g. Instrument Serif italic, the SOFT voice)
    // is checked against its italic @font-face instead of a hardcoded
    // upright-400 that false-FAILs even when the used face is loaded
    // (2026-07-13 fix; the upright probe had forced hidden offscreen
    // upright-loader spans as a hack). Normalize "oblique 14deg" -> "oblique"
    // to keep the shorthand parseable, and key seenFam on style too so upright
    // AND italic of one family are each probed rather than deduped together.
    const styl = /^(italic|oblique)/.test(cs.fontStyle) ? cs.fontStyle.split(" ")[0] : "normal";
    const fkey = fam + "|" + cs.fontWeight + "|" + styl;
    if (!["serif","sans-serif","monospace","system-ui","cursive","fantasy"].includes(fam) &&
        !seenFam.has(fkey)) {
      seenFam.add(fkey);
      let spec = styl + " " + cs.fontWeight + " 32px \\"" + fam + "\\"";
      try {
        if (!document.fonts.check(spec)) out.fonts_missing.push({ family: fam, weight: cs.fontWeight, style: styl });
      } catch (e) {}
    }
  }
  /* TEXT OCCLUDED BY AN OPAQUE PLATE (2026-07-26). qa.py's text_collisions()
     compares GLYPH LINE BOXES only, so an opaque element's BACKGROUND is
     invisible to it: a padded plate can paint over the bottom third of a
     subtitle while every line-box pair stays under the 30% overlap ratio.
     That is exactly how the 2026-07-26 S06 and S02 hard fails (a DEAD plate
     over a subtitle; a note column run 62px past a callout plate) shipped
     past machine QA reporting zero fails and zero warns, twice.

     For each recorded text node, intersect its line boxes with every OPAQUE
     element box that is neither an ancestor nor a descendant of it, then
     confirm PAINT ORDER with elementFromPoint (a temporary
     pointer-events:auto sheet lets the hit test see decorative layers;
     pointer-events never affects pixels, and the sheet is removed before the
     screenshot). If the text paints ABOVE the plate the hit test returns the
     text and nothing is reported, so knockout plates and chips-on-plates stay
     legal. Deliberately conservative: canvas/SVG ink, blended layers, sub-0.9
     alpha and full-bleed ground planes are NOT treated as occluders, so the
     check only speaks when something opaque provably covers type. */
  const _alpha = (col) => {
    const m = /rgba?\(([^)]+)\)/.exec(col || "");
    if (!m) return 0;
    const p = m[1].split(",").map(parseFloat);
    return p.length > 3 ? p[3] : 1;
  };
  const peSheet = document.createElement("style");
  peSheet.textContent = "*{pointer-events:auto !important}";
  (document.head || de).appendChild(peSheet);
  try {
    const solids = [];
    for (const e of document.querySelectorAll("body *")) {
      if (e.namespaceURI === "http://www.w3.org/2000/svg") continue;
      const t = e.tagName;
      if (t === "CANVAS" || t === "SVG" || t === "SCRIPT" || t === "STYLE") continue;
      const cs3 = getComputedStyle(e);
      if (cs3.display === "none" || cs3.visibility === "hidden") continue;
      if (parseFloat(cs3.opacity) < 0.9) continue;
      if (cs3.mixBlendMode && cs3.mixBlendMode !== "normal") continue;
      const solid = _alpha(cs3.backgroundColor) >= 0.9 ||
                    (cs3.backgroundImage && cs3.backgroundImage !== "none") ||
                    t === "IMG";
      if (!solid) continue;
      const rr = e.getBoundingClientRect();
      if (rr.width < 4 || rr.height < 4) continue;
      if (rr.width >= W - 1 && rr.height >= H - 1) continue;  // full-bleed ground plane
      solids.push([e, rr]);
    }
    for (const [tel, idx] of recorded) {
      const tn = out.text_nodes[idx];
      let worst = null;
      for (const [se, sr] of solids) {
        if (se === tel || se.contains(tel) || tel.contains(se)) continue;
        for (const ln of tn.lines) {
          const ix = Math.min(ln[0] + ln[2], sr.right) - Math.max(ln[0], sr.left);
          const iy = Math.min(ln[1] + ln[3], sr.bottom) - Math.max(ln[1], sr.top);
          if (ix < 2 || iy < 2) continue;
          if (worst && ix * iy <= worst._px) continue;
          const x0 = Math.max(ln[0], sr.left), y0 = Math.max(ln[1], sr.top);
          let hits = 0, tries = 0;
          for (const fx of [0.2, 0.5, 0.8]) for (const fy of [0.3, 0.7]) {
            tries++;
            // elementsFromPoint returns the whole stack, TOPMOST FIRST. Compare
            // the plate's depth against the text's: a full-frame grain/edge
            // overlay sits above both and must not decide the answer, which
            // singular elementFromPoint would let it do.
            const stack = document.elementsFromPoint(x0 + ix * fx, y0 + iy * fy);
            let si = -1, ti = -1;
            for (let k = 0; k < stack.length; k++) {
              const nd = stack[k];
              if (si < 0 && (nd === se || se.contains(nd))) si = k;
              if (ti < 0 && (nd === tel || tel.contains(nd))) ti = k;
            }
            if (si >= 0 && (ti < 0 || si < ti)) hits++;
          }
          if (hits * 2 < tries) continue;   // the text paints above the plate: legible
          worst = {
            _px: ix * iy, w: Math.round(ix), h: Math.round(iy),
            frac: Math.round(1000 * (ix * iy) / Math.max(1, ln[2] * ln[3])) / 1000,
            by: (se.getAttribute("class") || se.id || se.tagName).slice(0, 40),
            by_text: (se.textContent || "").trim().replace(/\s+/g, " ").slice(0, 40)
          };
        }
      }
      if (worst) { delete worst._px; tn.occluded = worst; }
    }
  } catch (e) {
    // never fail the render over the probe itself; surface it as a console
    // error, which render.py records and qa.py reports as a WARN.
    try { console.error("text-occlusion probe threw: " + e); } catch (e2) {}
  } finally {
    peSheet.remove();
  }
  /* SVG KNOCKOUT PLATES (2026-07-29). A <rect> painted before a <text> in the
     same <svg>, overlapping it, is that label's knockout plate, and the label
     must sit fully inside it. NOTHING in this file could see that before: SVG
     text has no line boxes (the Range path above is DOM-only), the plate is a
     SIBLING rather than an ancestor, and the occlusion probe hit-tests DOM
     text only. Run 2026-07-29 shipped six labels hanging off their own plates
     through two scoring cycles with machine_qa reporting 0 fails, including a
     chip border rule drawn straight through the 'T' of 'PERMITS'. The root
     cause is arithmetic: JetBrains Mono at 24px with 0.10em tracking advances
     16.8px per character, and the plate widths were hand-sized at roughly 14.
     Measure containment here; qa.py grades it. */
  out.svg_plates = [];
  for (const sv of document.querySelectorAll('svg')) {
    const kids = Array.from(sv.querySelectorAll('text, rect'));
    for (let i = 0; i < kids.length; i++) {
      const t = kids[i];
      if (t.tagName.toLowerCase() !== 'text') continue;
      if (!t.textContent.trim()) continue;
      const tb = t.getBoundingClientRect();
      if (tb.width < 1 || tb.height < 1) continue;
      let plate = null;
      for (let j = 0; j < i; j++) {
        const r = kids[j];
        if (r.tagName.toLowerCase() !== 'rect') continue;
        const rb = r.getBoundingClientRect();
        if (rb.width < 1 || rb.height < 1) continue;
        if (tb.left < rb.right && tb.right > rb.left &&
            tb.top < rb.bottom && tb.bottom > rb.top) plate = rb;
      }
      /* The mirror case, and the one that bit this run twice: a rect painted
         AFTER the text, overlapping it, is painting OVER the label. SVG has no
         z-index, only document order, so a plate appended for the block below
         silently eats the descender of the line above. The DOM occlusion probe
         cannot see it (elementsFromPoint reports the <svg>, not the <rect>). */
      let covered = null;
      for (let j = i + 1; j < kids.length; j++) {
        const r = kids[j];
        if (r.tagName.toLowerCase() !== 'rect') continue;
        const f = (r.getAttribute('fill') || '').trim();
        if (!f || f === 'none') continue;
        const m = f.match(/rgba?\(([^)]+)\)/);
        const alpha = m ? (parseFloat(m[1].split(',')[3]) || 1) : 1;
        if (alpha * (parseFloat(r.getAttribute('fill-opacity')) || 1) < 0.5) continue;
        const rb = r.getBoundingClientRect();
        const ox = Math.min(tb.right, rb.right) - Math.max(tb.left, rb.left);
        const oy = Math.min(tb.bottom, rb.bottom) - Math.max(tb.top, rb.top);
        if (ox > 1 && oy > 1) {
          const area = ox * oy;
          if (!covered || area > covered.area) covered = { area: area, w: Math.round(ox), h: Math.round(oy) };
        }
      }
      /* And the third way to bury an SVG label: a DOM element painted above
         the whole <svg>. The furniture layer is one positioned element, so a
         knockout-plated body div declared after it in the document eats any
         guard line it happens to overlap, with no SVG-level evidence at all.
         Ask the compositor what is actually on top of the label's own box. */
      let domHit = 0, domN = 0;
      const cy = (tb.top + tb.bottom) / 2;
      if (cy >= 0 && cy <= H) {
        for (let s = 0; s <= 10; s++) {
          const px = tb.left + (tb.width * s) / 10;
          if (px < 0 || px > W) continue;
          domN++;
          for (const e of document.elementsFromPoint(px, cy)) {
            if (e === sv || e.contains(sv)) break;
            if (e === t || sv.contains(e)) continue;
            const bg = getComputedStyle(e).backgroundColor || '';
            const mm = bg.match(/rgba?\(([^)]+)\)/);
            const a2 = mm ? (parseFloat(mm[1].split(',')[3]) || 1) : 0;
            if (a2 >= 0.5) { domHit++; break; }
          }
        }
      }
      const domFrac = domN ? domHit / domN : 0;
      if (covered || domFrac > 0.15) {
        out.svg_plates.push({
          text: t.textContent.trim().slice(0, 60),
          covered_px: covered ? [covered.w, covered.h] : null,
          dom_cover_frac: Math.round(domFrac * 100) / 100,
          overrun_px: 0, over: { left: 0, right: 0, top: 0, bottom: 0 },
          decorative: t.hasAttribute('data-decorative'),
          overlap_ok: t.hasAttribute('data-overlap-ok')
        });
      }
      if (!plate) continue;
      const over = {
        left: Math.round(plate.left - tb.left), right: Math.round(tb.right - plate.right),
        top: Math.round(plate.top - tb.top), bottom: Math.round(tb.bottom - plate.bottom)
      };
      const worst = Math.max(over.left, over.right, over.top, over.bottom);
      if (worst > 0) {
        out.svg_plates.push({
          text: t.textContent.trim().slice(0, 60), overrun_px: worst, over: over,
          decorative: t.hasAttribute('data-decorative'),
          overlap_ok: t.hasAttribute('data-overlap-ok')
        });
      }
    }
  }

  /* DRAWN RULES (2026-08-18). The geometry half of qa.py's strikethrough gate.
     Everything above this block sees TEXT (line boxes) or OPAQUE BOXES (the
     occlusion probe, which requires a filled background >= 4px in BOTH
     dimensions and confirms paint order). A one or two pixel BORDER is neither,
     so on 2026-08-18 slide 09's table ran its 2px `tr.last td` bottom rule
     from x=84 to x=996 at y=1216, straight through the glyph band of a footnote
     line box at [84,1204,691,31], and machine QA reported zero fails and zero
     warns. At 432px feed width that rule reads as a strikethrough through the
     sentence. The scorer caught it by reading these coordinates out of this
     file, which is the whole argument for measuring them here.

     What is emitted is STRIPS, in viewport (design) px, with no judgement:

       kind "border"  one strip per visible side of any element's border box
       kind "outline" the same for a CSS outline, offset included
       kind "fill"    an element that is ITSELF drawn geometry: a painted box
                      with no text anywhere inside it (an <hr>, a divider div,
                      a ruled empty field). A plate BEHIND type contains that
                      type and is excluded here, which is right: the occlusion
                      probe above owns plates and this owns rules.
       kind "svg"     an SVG <line> or <rect>'s side strips. A <path> is not
                      emitted: its bounding box is not the shape it draws, and
                      a box that is not the geometry would be a gate reporting
                      a figure the slide does not contain (GATE_LESSONS 15).

     `skip` carries the indices of every text node this strip is the box of, or
     an ancestor or descendant of, so qa.py never reports an element's own
     underline or a card's border against text inside the card. That is the same
     conservative ownership rule the occlusion probe uses.

     NO VISIBILITY THRESHOLD IS APPLIED HERE, deliberately. Whether a hairline
     at alpha 0.45 reads as a strikethrough is a question about the pixels a
     reader receives, not about a declared alpha, so qa.py measures it off the
     PNG against WCAG 1.4.11's 3.0:1 non-text floor. Emitting everything and
     judging on measurement is what keeps this from being a typed number.
     PAINT ORDER IS ALSO NOT CONSULTED, and that is not an oversight: the
     2026-08-18 rule was painted BENEATH the footnote (the div comes after the
     table in document order) and still read as a strikethrough, because a dark
     hairline crossing a word is a strikethrough whichever of the two was
     rasterised last. */
  out.rules = [];
  try {
    const _skipFor = (el) => {
      const s = [];
      for (const [tel, idx] of recorded) {
        if (tel === el || el.contains(tel) || tel.contains(el)) s.push(idx);
      }
      return s;
    };
    const _name = (e) =>
      ((e.getAttribute && e.getAttribute("class")) || e.id || e.tagName || "?")
        .toString().slice(0, 40);
    const push = (el, kind, x, y, w, h, color) => {
      if (out.rules.length >= 600) return;
      if (!(w > 0.5 && h > 0.5)) return;
      if (x + w < 0 || y + h < 0 || x > W || y > H) return;
      out.rules.push({
        kind: kind, x: Math.round(x * 10) / 10, y: Math.round(y * 10) / 10,
        w: Math.round(w * 10) / 10, h: Math.round(h * 10) / 10,
        by: _name(el), color: color || "",
        decorative: !!(el.hasAttribute && (el.hasAttribute("data-decorative") ||
                       (el.closest && el.closest("[data-decorative]")))),
        skip: _skipFor(el)
      });
    };
    for (const e of document.querySelectorAll("body *")) {
      const tg = (e.tagName || "").toUpperCase();
      if (tg === "SCRIPT" || tg === "STYLE" || tg === "CANVAS") continue;
      const cs4 = getComputedStyle(e);
      if (cs4.display === "none" || cs4.visibility === "hidden") continue;
      if (parseFloat(cs4.opacity) === 0) continue;
      const isSvg = e.namespaceURI === "http://www.w3.org/2000/svg";
      const r4 = e.getBoundingClientRect();
      if (isSvg) {
        const lt = tg.toLowerCase();
        if (lt !== "line" && lt !== "rect") continue;
        const sw = parseFloat(cs4.strokeWidth || "0") || 0;
        const stroked = sw > 0 && (cs4.stroke || "") !== "none" && (cs4.stroke || "") !== "";
        if (lt === "line") {
          if (!stroked) continue;
          push(e, "svg", r4.left, r4.top, Math.max(r4.width, sw), Math.max(r4.height, sw),
               cs4.stroke);
        } else {
          if (stroked) {
            push(e, "svg", r4.left, r4.top, r4.width, sw, cs4.stroke);
            push(e, "svg", r4.left, r4.bottom - sw, r4.width, sw, cs4.stroke);
            push(e, "svg", r4.left, r4.top, sw, r4.height, cs4.stroke);
            push(e, "svg", r4.right - sw, r4.top, sw, r4.height, cs4.stroke);
          }
          const fl = (cs4.fill || "").trim();
          if (fl && fl !== "none" && !e.textContent.trim()) {
            push(e, "fill", r4.left, r4.top, r4.width, r4.height, fl);
          }
        }
        continue;
      }
      const side = (p) => {
        const st = cs4.getPropertyValue("border-" + p + "-style");
        if (!st || st === "none" || st === "hidden") return 0;
        return parseFloat(cs4.getPropertyValue("border-" + p + "-width")) || 0;
      };
      const bt = side("top"), bb = side("bottom"), bl = side("left"), br = side("right");
      if (bt) push(e, "border", r4.left, r4.top, r4.width, bt,
                   cs4.getPropertyValue("border-top-color"));
      if (bb) push(e, "border", r4.left, r4.bottom - bb, r4.width, bb,
                   cs4.getPropertyValue("border-bottom-color"));
      if (bl) push(e, "border", r4.left, r4.top, bl, r4.height,
                   cs4.getPropertyValue("border-left-color"));
      if (br) push(e, "border", r4.right - br, r4.top, br, r4.height,
                   cs4.getPropertyValue("border-right-color"));
      const ow = parseFloat(cs4.outlineWidth) || 0;
      if (ow > 0 && cs4.outlineStyle && cs4.outlineStyle !== "none") {
        const off = parseFloat(cs4.outlineOffset) || 0;
        const ox = r4.left - off - ow, oy = r4.top - off - ow;
        const oW = r4.width + 2 * (off + ow), oH = r4.height + 2 * (off + ow);
        push(e, "outline", ox, oy, oW, ow, cs4.outlineColor);
        push(e, "outline", ox, oy + oH - ow, oW, ow, cs4.outlineColor);
        push(e, "outline", ox, oy, ow, oH, cs4.outlineColor);
        push(e, "outline", ox + oW - ow, oy, ow, oH, cs4.outlineColor);
      }
      /* An element that is ITSELF a drawn mark: painted, and holding no words.
         A plate behind type holds that type and is not this. */
      if (!e.textContent.trim()) {
        const painted = _alpha(cs4.backgroundColor) > 0 ||
                        (cs4.backgroundImage && cs4.backgroundImage !== "none");
        if (painted && !(r4.width >= W - 1 && r4.height >= H - 1)) {
          push(e, "fill", r4.left, r4.top, r4.width, r4.height, cs4.backgroundColor);
        }
      }
    }
  } catch (e) {
    try { console.error("drawn-rules probe threw: " + e); } catch (e2) {}
  }

  /* DECLARED ENCODINGS (2026-07-29). A slide may state, in machine-readable
     form, what its artwork is supposed to SAY without words:

       <body data-encodes='[{"claim":"material change at hour 7",
                             "reads":"differ",
                             "a":[[732,1052,82,98]], "b":[[736,500,74,540]]}]'>

     `reads` is REQUIRED as of 2026-08-08 and is one of "differ" (the two
     regions must be tellable apart) or "same" (an absence or sameness claim).
     qa.py FAILS a declaration that omits it, and FAILS a "differ" whose two
     regions are under 4.0 dE apart at feed scale. Run No.29 authored two probe
     rectangles from the storyboard's camera arithmetic instead of measuring
     them off a render; they landed on empty water 300px from the aperture,
     reported dE 0.9, and gated nothing. MEASURE THE RECTS OFF THE PNG.

     Every gate before this one judged LEGIBILITY. Nothing judged whether the
     picture carried its own argument, so the only reviewer who ever saw a
     failed encoding was the scorer, at the ship gate, too late to rebuild the
     art. Artwork craft was the weakest criterion in 16 of the first 19 runs.

     Two things are measured, because calibration showed one is not enough.
     Run 2026-07-29's hero declared steel below hour 7 and brass above, and
     the scorer said it read as one uniform amber extrusion. It did not fail
     on colour: where the steel is visible it sits 43 dE from the brass, so a
     pure separability check PASSES the defect it was built to catch. What
     actually failed is PROMINENCE: a knockout plate and the base shadow left
     only 29 percent of the declared steel section as visible art, so the
     material change read as a glassy plinth rather than as half the object.
     Hence art_visible_frac, sampled with elementsFromPoint per region. */
  out.encodings = [];
  try {
    const decl = (document.body && document.body.dataset.encodes) || "";
    const specs = decl ? JSON.parse(decl) : [];
    const rectsOf = (v) => {
      if (typeof v === "string") {
        return Array.from(document.querySelectorAll(v)).map(e => {
          const r = e.getBoundingClientRect();
          return [r.x, r.y, r.width, r.height];
        });
      }
      return (Array.isArray(v) && Array.isArray(v[0])) ? v : [v];
    };
    const visibleFrac = (rects) => {
      let hit = 0, n = 0;
      for (const [rx, ry, rw, rh] of rects) {
        const cols = Math.max(3, Math.min(24, Math.round(rw / 8)));
        const rows = Math.max(3, Math.min(24, Math.round(rh / 8)));
        for (let i = 0; i < cols; i++) {
          for (let j = 0; j < rows; j++) {
            const px = rx + (rw * (i + 0.5)) / cols;
            const py = ry + (rh * (j + 0.5)) / rows;
            if (px < 0 || px > W || py < 0 || py > H) continue;
            n++;
            const stack = document.elementsFromPoint(px, py);
            let blocked = false;
            for (const e of stack) {
              const tag = e.tagName.toLowerCase();
              if (tag === "canvas" || tag === "svg" || tag === "body" || tag === "html") break;
              if (e.namespaceURI === "http://www.w3.org/2000/svg") {
                // art drawn as SVG shapes is still the artwork, but an opaque
                // knockout rect is furniture
                const f = (e.getAttribute("fill") || "").trim();
                const m = f.match(/rgba?\(([^)]+)\)/);
                const al = m ? (parseFloat(m[1].split(",")[3]) || 1) : (f && f !== "none" ? 1 : 0);
                if (al >= 0.5 && tag === "rect") { blocked = true; break; }
                continue;
              }
              const bg = getComputedStyle(e).backgroundColor || "";
              const mm = bg.match(/rgba?\(([^)]+)\)/);
              const a2 = mm ? (parseFloat(mm[1].split(",")[3]) || 1) : 0;
              if (a2 >= 0.5) { blocked = true; break; }
            }
            if (!blocked) hit++;
          }
        }
      }
      return n ? hit / n : 0;
    };
    for (const sp of specs) {
      const ra = rectsOf(sp.a), rb = rectsOf(sp.b);
      out.encodings.push({
        claim: String(sp.claim || "").slice(0, 90),
        reads: sp.reads || "any",
        a: ra.map(r => r.map(Math.round)), b: rb.map(r => r.map(Math.round)),
        a_visible_frac: Math.round(visibleFrac(ra) * 100) / 100,
        b_visible_frac: Math.round(visibleFrac(rb) * 100) / 100
      });
    }
  } catch (e) {
    out.encodings.push({ error: String(e).slice(0, 140) });
  }

  /* DECLARED CONTACT SHADOWS (2026-08-05). A shadow is a SUBTRACTION and it
     needs something to subtract FROM. Run No.26 declared the contact corollary
     as its attack, built the two-part shadow exactly as specified in #1A0F08
     at alpha 0.55, and laid it on a table already rendering near #0B0906. The
     composite is a 1.2 L* change. FOUR pixel critics independently returned
     contact_edge_reads: no, the scorer called three of nine slides
     "floating-adjacent", and qa.py passed the deck with zero fails, because
     every gate in it judges legibility, collision or balance and none of them
     asks whether a declared depth cue survived compositing.

     A slide states, in machine-readable form, where its contact shadow is and
     what ground it is supposed to darken:

       <body data-contacts='[{"what":"the shut block on the table",
                              "shadow":[[236,1178,608,26]],
                              "ground":[[236,1246,608,26]]}]'>

     Rects are [x,y,w,h] in design px, a list of rects or a single rect, or a
     CSS selector resolved by getBoundingClientRect (same grammar as
     data-encodes). qa.py measures median L* of each region at feed scale and
     FAILs when the shadow is not meaningfully darker than its own ground.

     Unlike the encoding probe there is no elementsFromPoint pass here: a
     contact shadow is CANVAS PAINT, so occlusion by type is a legitimate
     composition and the only question is what the pixels do. */
  out.contacts = [];
  try {
    const cdecl = (document.body && document.body.dataset.contacts) || "";
    const cspecs = cdecl ? JSON.parse(cdecl) : [];
    const rectsOf2 = (v) => {
      if (typeof v === "string") {
        return Array.from(document.querySelectorAll(v)).map(e => {
          const r = e.getBoundingClientRect();
          return [r.x, r.y, r.width, r.height];
        });
      }
      return (Array.isArray(v) && Array.isArray(v[0])) ? v : [v];
    };
    for (const sp of cspecs) {
      out.contacts.push({
        what: String(sp.what || "").slice(0, 90),
        shadow: rectsOf2(sp.shadow).map(r => r.map(Math.round)),
        ground: rectsOf2(sp.ground).map(r => r.map(Math.round))
      });
    }
  } catch (e) {
    out.contacts.push({ error: String(e).slice(0, 140) });
  }

  /* CANVAS TELEMETRY (2026-07-11, the rendered-3D gates): per visible canvas,
     backing resolution vs CSS size (silent-1x detector) and a downsampled
     pixel sample (dead/black-frame detector: a GL context that failed or
     never painted screenshots as uniform ink). GL canvases need
     preserveDrawingBuffer (akthree sets it) for drawImage sampling; when
     sampling fails we report sample_ok:false rather than guessing. */
  out.canvases = [];
  for (const cv of document.querySelectorAll('canvas')) {
    const cs2 = getComputedStyle(cv);
    if (cs2.display === 'none' || cs2.visibility === 'hidden') continue;
    const r2 = cv.getBoundingClientRect();
    if (r2.width < 8 || r2.height < 8) continue;
    const entry = {
      x: Math.round(r2.x), y: Math.round(r2.y),
      w: Math.round(r2.width), h: Math.round(r2.height),
      bw: cv.width, bh: cv.height,
      area_frac: Math.round(1000 * Math.min(1,
        (Math.min(r2.width, W) * Math.min(r2.height, H)) / (W * H))) / 1000,
      backing_ratio: Math.round(100 * Math.min(cv.width / Math.max(1, r2.width),
                                               cv.height / Math.max(1, r2.height))) / 100,
      sample_ok: false, mean: -1, variance: -1
    };
    try {
      const sw = 48, sh = Math.max(8, Math.round(48 * r2.height / r2.width));
      const t = document.createElement('canvas');
      t.width = sw; t.height = sh;
      const tc = t.getContext('2d', { willReadFrequently: true });
      tc.drawImage(cv, 0, 0, sw, sh);
      const px = tc.getImageData(0, 0, sw, sh).data;
      let sum = 0, sum2 = 0, n = sw * sh;
      for (let i = 0; i < px.length; i += 4) {
        const v = (px[i] + px[i + 1] + px[i + 2]) / 3;
        sum += v; sum2 += v * v;
      }
      entry.mean = Math.round(sum / n * 10) / 10;
      entry.variance = Math.round((sum2 / n - (sum / n) * (sum / n)) * 10) / 10;
      entry.sample_ok = true;
    } catch (e) {}
    out.canvases.push(entry);
  }
  /* CANVAS TEXT (2026-07-19): deduped list of strings drawn via fillText/
     strokeText, captured by the add_init_script hook before slide scripts ran.
     qa.py WARNs on the meaningful ones (raster text ships in the vector PDF and
     is invisible to the ranker/copy_sync/a11y). Only present if the hook ran. */
  out.canvas_text = [];
  try {
    const seen = new Set();
    for (const e of (window.__akCanvasText || [])) {
      if (seen.has(e.text)) continue;
      seen.add(e.text);
      out.canvas_text.push(e);
    }
  } catch (e) {}
  /* ANNOTATION LEADERS (2026-08-07). A leader line that stops in open field
     looks exactly like a leader reaching something small, which is why run
     No.28's slide 06 shipped two detail-circle leaders pointing at void through
     TWO pixel critics and a flow critic: the tails were fixed pixel deltas from
     each circle's own center (tail:[-70,-70,-150,-150]), so no reviewer and no
     gate could tell what they were supposed to arrive at. Pixels cannot answer
     it either (the leader's own landing tick puts ink at the terminus), so the
     slide DECLARES the arithmetic instead: for every drafting leader, where it
     ends and where the feature it points at actually is. qa.py then checks the
     two agree. Opt-in by construction -- a slide with no leaders declares
     nothing -- but SKILL.md makes the declaration part of the slide contract
     for any leader, callout or detail-circle annotation.

       window.__akLeaders = [{ target: '2024 sliver dimension line',
                               at: [BX + 2, 838],       // the FEATURE's own coords
                               to: [BX + 2, 838] }];    // where the leader ends
  */
  out.leaders = [];
  try {
    const pt = (v) => Array.isArray(v) && v.length === 2 &&
      v.every((n) => typeof n === "number" && isFinite(n))
        ? [Math.round(v[0] * 10) / 10, Math.round(v[1] * 10) / 10] : null;
    for (const e of (Array.isArray(window.__akLeaders) ? window.__akLeaders : []).slice(0, 60)) {
      out.leaders.push({
        target: (e && typeof e.target === "string" && e.target.trim())
          ? e.target.trim().slice(0, 90) : null,
        to: pt(e && e.to),
        at: pt(e && e.at)
      });
    }
  } catch (e) {}
  return out;
}
"""


def launch_chromium(p):
    """Launch chromium, falling back to the pre-installed browser binary."""
    try:
        return p.chromium.launch(args=CHROMIUM_ARGS)
    except Exception:
        candidates = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
        candidates += ["/opt/pw-browsers/chromium/chrome-linux/chrome", "/opt/pw-browsers/chromium"]
        for c in candidates:
            if Path(c).exists():
                try:
                    return p.chromium.launch(executable_path=c, args=CHROMIUM_ARGS)
                except Exception:
                    continue
        raise RuntimeError("No launchable Chromium found (tried default + /opt/pw-browsers)")


# --- DETERMINISM SOURCE SCAN (2026-08-01) -----------------------------------
# SKILL.md's slide contract says "seed all noise (TX.reseed / TX.rng), derive
# the seed from the run date, same inputs must reproduce the same pixels", and
# nothing enforced it. On 2026-08-01 a stipple field shipped through five
# render rounds on Math.random() and was caught by a human running grep, on a
# deck whose subject was a public RECORD. An unseeded field cannot be
# re-rendered: a repair pass on slide 9 silently repaints every dot, so a pixel
# critic's note about one label stops describing the file it was written
# against, and the shipped PNG can never be reproduced from the committed HTML.
#
# The scan reads the slide SOURCE (this is a source-level contract, and the
# defect is invisible in a single screenshot), and only inside INLINE <script>
# blocks: vendored libraries under assets/js are loaded by src= and are not
# read, and a deck that PRINTS the string "Math.random" as body copy is DOM
# text, not script, so it never trips. Comments and their contents are stripped
# before matching.
#   HARD (qa.py FAIL): unseeded randomness. There is no legitimate use of it in
#     a slide; TX.rng(seed) is the drop-in replacement and takes one argument.
#   SOFT (qa.py WARN): clock reads. Usually a timing log, occasionally an
#     animation phase that does feed pixels; the author decides, the machine
#     just refuses to let it pass unseen.
NONDET_HARD = [
    ("Math.random()", re.compile(r"\bMath\s*\.\s*random\s*\(")),
    ("crypto.getRandomValues()", re.compile(r"\bcrypto\s*\.\s*getRandomValues\s*\(")),
    ("crypto.randomUUID()", re.compile(r"\bcrypto\s*\.\s*randomUUID\s*\(")),
]
NONDET_SOFT = [
    ("Date.now()", re.compile(r"\bDate\s*\.\s*now\s*\(")),
    ("new Date()", re.compile(r"\bnew\s+Date\s*\(\s*\)")),
    ("performance.now()", re.compile(r"\bperformance\s*\.\s*now\s*\(")),
]
SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.S | re.I)
JS_TYPE_OK = ("", "text/javascript", "application/javascript", "module")


def _strip_js_comments(js: str) -> str:
    """Blank out // and /* */ comments, preserving length so offsets survive."""
    out = list(js)
    i, n = 0, len(js)
    while i < n:
        two = js[i:i + 2]
        if two == "//":
            j = js.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
        elif two == "/*":
            j = js.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if js[k] != "\n":
                    out[k] = " "
            i = j
        else:
            i += 1
    return "".join(out)


def scan_nondeterminism(html: str, name: str) -> list:
    """Report unseeded-randomness / clock reads in a slide's inline scripts."""
    hits = []
    for m in SCRIPT_RE.finditer(html):
        attrs, body = m.group(1), m.group(2)
        if re.search(r"\bsrc\s*=", attrs, re.I):
            continue                      # external file: vendored, not ours
        tm = re.search(r"""\btype\s*=\s*["']?([^"'\s>]*)""", attrs, re.I)
        if tm and tm.group(1).strip().lower() not in JS_TYPE_OK:
            continue                      # text/template, application/json, ...
        body_start = m.start(2)
        clean = _strip_js_comments(body)
        for tier, table in (("hard", NONDET_HARD), ("soft", NONDET_SOFT)):
            for api, rx in table:
                for hit in rx.finditer(clean):
                    off = body_start + hit.start()
                    line = html.count("\n", 0, off) + 1
                    src_line = html.splitlines()[line - 1].strip()
                    hits.append({"tier": tier, "api": api, "line": line,
                                 "snippet": src_line[:120]})
    hits.sort(key=lambda h: (h["line"], h["api"]))
    if hits:
        print(f"    [determinism] {name}: "
              + ", ".join(f"{h['api']} line {h['line']}" for h in hits))
    return hits


def resolve_html(src: Path, resolved_dir: Path) -> Path:
    html = src.read_text()
    if re.search(r'src\s*=\s*["\']https?://|href\s*=\s*["\']https?://|url\(\s*["\']?https?://', html):
        raise ValueError(f"{src.name}: external http(s) reference found. Slides must be fully offline.")
    html = html.replace("@@ASSETS@@", ASSETS_DIR.as_uri())
    dst = resolved_dir / src.name
    dst.write_text(html)
    return dst


def render_slide(browser, path: Path, out_png: Path, width: int, height: int,
                 scale: float, timeout_ms: int) -> dict:
    rec = {"file": path.name, "png": out_png.name, "console_errors": [], "page_errors": [],
           "overflow_warnings": [], "fonts_missing": [], "text_nodes": [],
           "body_overflow": False, "canvas_text": [], "svg_plates": [],
           "rules": [], "encodings": [], "contacts": [], "nondeterminism": [],
           "render_ms": 0, "ok": False}
    t0 = time.time()
    page = browser.new_page(viewport={"width": width, "height": height},
                            device_scale_factor=scale)
    page.add_init_script(CANVAS_TEXT_HOOK_JS.replace("__TEXT_WINDOW__", str(TEXT_WINDOW)))
    page.on("console", lambda m: rec["console_errors"].append(m.text)
            if m.type in ("error",) else None)
    page.on("pageerror", lambda e: rec["page_errors"].append(str(e)))
    try:
        page.goto(path.as_uri(), wait_until="load", timeout=timeout_ms)
        page.evaluate("() => document.fonts.ready.then(() => true)")
        has_ready = page.evaluate("() => typeof window.renderReady !== 'undefined'")
        if has_ready:
            page.evaluate("() => Promise.race([window.renderReady, "
                          "new Promise((_, rej) => setTimeout(() => rej('renderReady timeout'), 30000))])")
        else:
            page.wait_for_timeout(400)
        qa = page.evaluate(IN_PAGE_QA_JS.replace("__TEXT_WINDOW__", str(TEXT_WINDOW)))
        rec.update({k: qa[k] for k in ("text_nodes", "overflow_warnings",
                                       "fonts_missing", "body_overflow", "canvases",
                                       "canvas_text", "breather", "svg_plates",
                                       "rules", "encodings", "contacts", "leaders")})
        page.screenshot(path=str(out_png), clip={"x": 0, "y": 0, "width": width, "height": height})
        rec["ok"] = out_png.exists() and out_png.stat().st_size > 10_000
        if not rec["ok"]:
            rec["page_errors"].append("screenshot missing or suspiciously small")
    except Exception as e:
        rec["page_errors"].append(f"render exception: {e}")
    finally:
        page.close()
    rec["render_ms"] = int((time.time() - t0) * 1000)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1350)
    ap.add_argument("--only", default="", help="comma-separated slide numbers to re-render, e.g. 2,5")
    ap.add_argument("--timeout", type=int, default=45000)
    args = ap.parse_args()

    slides_dir = Path(args.slides_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    resolved_dir = out_dir / ".resolved"
    resolved_dir.mkdir(exist_ok=True)

    slides = sorted(slides_dir.glob("slide-*.html"))
    if not slides:
        print(f"FAIL: no slide-*.html in {slides_dir}", file=sys.stderr)
        sys.exit(1)
    if args.only:
        keep = {int(x) for x in args.only.split(",")}
        slides = [s for s in slides
                  if int(re.search(r"slide-(\d+)", s.name).group(1)) in keep]

    report_path = out_dir / "render_report.json"
    prior = {}
    if report_path.exists():
        try:
            prior = {r["file"]: r for r in json.loads(report_path.read_text())["slides"]}
        except Exception:
            prior = {}

    results = []
    with sync_playwright() as p:
        browser = launch_chromium(p)
        for s in slides:
            resolved = resolve_html(s, resolved_dir)
            png = out_dir / (s.stem + ".png")
            rec = render_slide(browser, resolved, png, args.width, args.height,
                               args.scale, args.timeout)
            rec["nondeterminism"] = scan_nondeterminism(s.read_text(), s.name)
            status = "OK " if rec["ok"] and not rec["page_errors"] else "FAIL"
            warn = len(rec["overflow_warnings"])
            print(f"[{status}] {s.name} -> {png.name}  {rec['render_ms']}ms"
                  f"  warnings={warn}  errors={len(rec['page_errors'])}")
            prior[s.name] = rec
            results.append(rec)
        browser.close()
    shutil.rmtree(resolved_dir, ignore_errors=True)

    merged = [prior[k] for k in sorted(prior.keys())]
    report = {
        "canvas": {"width": args.width, "height": args.height, "scale": args.scale,
                   "px": [int(args.width * args.scale), int(args.height * args.scale)]},
        # THE REPORT DECLARES ITS OWN TEXT WINDOW, so a reader of it never has to assume one.
        # This value moved from 80 to 320 on 2026-08-19, and every report written before that is
        # truncated at 80. `copy_sync_check` truncates authored strings to the same figure before
        # comparing, so a consumer that assumes the current constant will mis-compare every
        # historical report and fail decks that were correct when they shipped. It did exactly
        # that on the 2026-08-16 deck within one CI run of the widening.
        "text_window": TEXT_WINDOW,
        "slides": merged,
    }
    report_path.write_text(json.dumps(report, indent=2))
    print(f"report -> {report_path}")

    hard_fail = any((not r["ok"]) or r["page_errors"] or r["body_overflow"] for r in results)
    if hard_fail:
        print("HARD FAIL: at least one slide has render errors or body overflow "
              "(see render_report.json)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
