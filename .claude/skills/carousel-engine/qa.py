#!/usr/bin/env python3
"""qa.py — machine QA over rendered slides. The objective half of the review
loop; the subjective half is the pixel-critic agents reading the PNGs.

Checks per slide (consuming render_report.json + the PNGs):
  - PNG exists, exact expected pixel size
  - not blank / not near-uniform (dead render detector)
  - TEXT COLLISIONS: no two text elements' line boxes may overprint
    (FAIL when both are primary text, WARN when either is decorative).
    Added 2026-07-08 after a body-copy-over-bar-label collision passed
    every other gate and had to be caught by the scorer's eyes.
  - BUSY ART UNDER TEXT (WARN only): samples the PNG under each primary text
    line box, masks the glyph ink, and warns when the background carries
    high-contrast structured edges (a canvas/bitmap arc or texture the DOM
    collision gate cannot see). Added 2026-07-10 after canvas flightpath/orbit
    arcs crossed body copy and a headline and machine QA passed both.
  - LABEL CROSSED BY ART (FAIL): samples a thin ring around each non-decorative
    label's glyph ink and FAILS when ink of the GLYPHS' OWN VALUE touches the
    letterforms across the label (a rule, scored outline or groove edge struck
    through the text). Knockout plates and halos leave that ring clean.
    Added 2026-07-25 after four slides shipped art-band labels crossed by
    canvas-drawn geometry through two scoring cycles of PASS with zero warns.
  - TEXT STRUCK BY A DRAWN RULE (FAIL): consumes render.py's drawn-geometry
    probe (every border side, outline, painted empty box and SVG line/rect edge)
    and FAILS when a strip thinner than one em of the struck type runs through
    the GLYPH BAND of a non-decorative text line and measures 3.0:1 or better
    against the paper beside it (WCAG 1.4.11's non-text floor, measured off the
    PNG). Added 2026-08-18 after slide 09's table ran its 2px bottom rule
    through the middle of the closing footnote and machine QA reported PASS with
    zero fails and zero warns: text_collisions() compares TEXT to TEXT, the
    occlusion probe compares text to OPAQUE ELEMENT BOXES four or more px in
    both dimensions, and a border is neither. Paint order is not consulted; a
    dark hairline across a word is a strikethrough whichever painted last.
  - TEXT UNDER AN OPAQUE PLATE (FAIL): consumes render.py's occlusion probe
    (paint-order-confirmed intersections of each line box with foreign opaque
    element boxes) and FAILS when a plate covers >=20x6px of a non-decorative
    line box. Added 2026-07-26 after an opaque DEAD plate over the bottom third
    of a subtitle and a note column run under a callout plate produced two
    consecutive hard fails while machine QA reported PASS, 0 fails, 0 warns:
    text_collisions() only compares GLYPH LINE BOXES, and a padded plate's
    background is not one.
  - FRAME BALANCE / DEAD LOWER ZONE (FAIL): compares the bottom third's
    craft-density against the slide's own frame average and FAILS a top-loaded
    composition (<55%). Added 2026-07-26 after the SIXTH consecutive scorer
    note naming "dead lower zones" as the series' artwork-craft ceiling. Every
    earlier gate here judges legibility; nothing measured composition, so the
    only reviewer who saw this was the scorer, at the ship gate, too late to
    rebuild slides -- which is why it became a note six times instead of a fix.
    data-breather on <body> demotes it to WARN (and the dossier gate checks the
    storyboard actually declared that slide a breather).
  - DECLARED CONTACT SHADOW DOES NOT READ (FAIL): opt-in. A slide may name, on
    <body data-contacts>, the region its contact shadow occupies and the ground
    that shadow is supposed to darken; this measures both at feed scale in
    CIELAB and FAILs below 4.0 L* of separation, WARNs below 8.0. Added
    2026-08-05 after run No.26 made the contact corollary its declared attack,
    built the shadow exactly as specified in #1A0F08 at alpha 0.55, laid it on
    a table already near #0B0906 for a 1.2 L* composite, and shipped an object
    four pixel critics said was floating while machine QA reported 0 fails. A
    shadow is a subtraction and needs something to subtract from; nothing here
    had ever asked whether a declared depth cue survived compositing.
  - LEADER LANDS ON NOTHING (FAIL): opt-in. A slide declares each drafting
    leader in window.__akLeaders as {target, at:[x,y], to:[x,y]} -- the feature's
    own coordinates and where the leader ends -- and this FAILs when the two are
    more than LEADER_LAND_PX apart. Added 2026-08-07 after run No.28's slide 06
    shipped two detail-circle leaders pointing at void through two pixel critics,
    a flow critic and the first scoring cycle: their tails were fixed pixel
    deltas from each circle's own center, so the target was never named anywhere
    and no reviewer could tell a leader reaching something small from one
    reaching nothing. A pixel test cannot answer it (the landing tick puts ink at
    the terminus); declared arithmetic can.
  - UNSEEDED RANDOMNESS (FAIL): consumes render.py's determinism source scan
    and FAILS a slide whose inline script calls Math.random() or the crypto
    random APIs instead of the seeded TX.rng(seed) / TX.reseed(seed) the slide
    contract requires; clock reads (Date.now, new Date(), performance.now) are
    a WARN. Added 2026-08-01 after a stipple field shipped on Math.random()
    through five render rounds on a deck about a public record, caught by a
    human running grep. Every other check here reads one screenshot, so an
    irreproducible slide is invisible to all of them.
  - CANVAS RASTER TEXT (WARN only): warns when a slide draws meaningful text
    (>=4 alphabetic chars) via canvas fillText/strokeText, which ships as a
    bitmap in the vector PDF and is invisible to the ranker/copy_sync/a11y.
    Added 2026-07-19 after S7/S8 canvas labels had to be converted to DOM by hand.
  - approximate contrast of every non-decorative text node vs its local
    background (WCAG-style luminance ratio; estimate, so thresholds are
    conservative: <2.0 on primary text = FAIL, <3.5 = WARN)
  - text nodes inside the safe zone (default 80px margins at 1080x1350;
    slides may bleed decorative art, not primary text)
  - forwards render_report warnings (offscreen/clipped/tiny text, missing
    fonts, console errors)

Usage:
  python .claude/skills/carousel-engine/qa.py --render-dir out/run/render
  python .claude/skills/carousel-engine/qa.py --self-test
Exit codes: 0 pass (warnings allowed), 1 any FAIL, 2 the checker could not run.
Writes <render-dir>/machine_qa.json
"""

import argparse
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

SAFE_MARGIN = 80  # px at 1080-wide design size


def rel_luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(x) for x in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def parse_css_color(s):
    m = re.match(r"rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)", s or "")
    if not m:
        return None
    return tuple(float(m.group(i)) for i in (1, 2, 3))


def contrast_estimate(img_arr, node, scale):
    """Estimate contrast between text color and its local background.

    The bbox contains both text and background pixels; the background is
    estimated as the median of the pixels most different from the text color
    (text coverage in a bbox is typically well under half).
    """
    color = parse_css_color(node.get("color"))
    if color is None:
        return None
    x, y = int(node["x"] * scale), int(node["y"] * scale)
    w, h = int(node["w"] * scale), int(node["h"] * scale)
    H, W = img_arr.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 - x0 < 4 or y1 - y0 < 4:
        return None
    crop = img_arr[y0:y1, x0:x1].reshape(-1, img_arr.shape[2])[:, :3].astype(float)
    if len(crop) > 20000:
        crop = crop[:: len(crop) // 20000]
    dist = np.abs(crop - np.array(color)).sum(axis=1)
    bg = np.median(crop[dist > np.percentile(dist, 55)], axis=0) if (dist > np.percentile(dist, 55)).any() else np.median(crop, axis=0)
    lt, lb = rel_luminance(color), rel_luminance(bg)
    lo, hi = min(lt, lb), max(lt, lb)
    return (hi + 0.05) / (lo + 0.05)


WORST_CELL_PX = 64      # device-px width of the cell the worst-point walk samples
WORST_MIN_INK = 0.04    # a cell needs this much glyph ink before it is judged
WORST_MIN_BG = 200      # a cell needs this many background pixels to estimate one
WORST_FAIL = 3.0        # worst-cell ratio on primary text that is a FAIL
WORST_WARN = 4.5        # the rubric's own hard-fail line, reported as a WARN below it


def contrast_worst_cell(img_arr, node, scale):
    """Contrast at the WORST POINT of a text node, not averaged over its bbox.

    Added 2026-07-31. contrast_estimate() takes ONE background value, the median
    of the non-ink pixels across the whole bounding box. On a flat ground that is
    right. On a GRADED ground it is the thing that hides the defect: a line set
    across an engraved sheet that runs from dark at one end to lit at the other
    averages to a comfortable ratio while its lit end is unreadable. The rubric's
    hard-fail rule says "below 4.5:1 AT WORST POINT" and the machine gate was
    measuring a mean, so for three runs (2026-07-25, 2026-07-29, 2026-07-31) the
    only reader who caught it was the scorer, at the ship gate, where a fix costs
    a whole revision cycle and caps the score at 6.9.

    Walks each line box in WORST_CELL_PX-wide cells, estimates the background
    from that CELL's own non-ink pixels, and returns the minimum ratio over every
    cell carrying real glyph ink, or None if nothing was measurable. Tightens the
    existing check; it never raises a ratio the old one reported.
    """
    color = parse_css_color(node.get("color"))
    if color is None:
        return None
    lines = node.get("lines") or [[node["x"], node["y"], node["w"], node["h"]]]
    H, W = img_arr.shape[:2]
    lt = rel_luminance(color)
    worst = None
    for bx, by, bw, bh in lines:
        y0, y1 = max(0, int(by * scale)), min(H, int((by + bh) * scale))
        if y1 - y0 < 8:
            continue
        gx0, gx1 = max(0, int(bx * scale)), min(W, int((bx + bw) * scale))
        for cx0 in range(gx0, gx1, WORST_CELL_PX):
            cx1 = min(cx0 + WORST_CELL_PX, gx1)
            if cx1 - cx0 < 16:
                continue
            cell = img_arr[y0:y1, cx0:cx1, :3].astype(float)
            ink = np.abs(cell - np.array(color)).sum(axis=2) < BUSY_INK_DIST
            if ink.mean() < WORST_MIN_INK or ink.mean() > 0.75:
                continue
            bgm = ~_dilate(ink, BUSY_DILATE)
            if int(bgm.sum()) < WORST_MIN_BG:
                continue
            bg = np.median(cell[bgm], axis=0)
            lb = rel_luminance(bg)
            lo, hi = min(lt, lb), max(lt, lb)
            r = (hi + 0.05) / (lo + 0.05)
            worst = r if worst is None else min(worst, r)
    return worst


BUSY_INK_DIST = 90      # sum-abs RGB distance under which a pixel counts as glyph ink
BUSY_EDGE_LUM = 28      # luminance step (0..255) that counts as a "structured edge"
BUSY_DILATE = 2         # px to grow the ink mask by, to exclude anti-aliased glyph edges
BUSY_WARN = 0.03        # background edge-density above which we point the critics at the box


def _dilate(mask, k):
    m = mask.copy()
    for _ in range(k):
        n = m.copy()
        n[:-1] |= m[1:]; n[1:] |= m[:-1]
        n[:, :-1] |= m[:, 1:]; n[:, 1:] |= m[:, :-1]
        m = n
    return m


def busy_art_under_text(img_arr, node, scale):
    """WARN-level tripwire for canvas/bitmap art crossing a DOM text line box.

    text_collisions() only sees DOM/SVG text vs DOM/SVG text; canvas ink is a
    bitmap invisible to render.py's DOM walk, so structured art drawn UNDER a
    text line passes every objective gate (2026-07-10: an S3 flightpath arc
    crossed two body lines and an S4 orbit arc crossed the headline, and
    machine_qa PASSED both -- only the pixel critics caught them). This samples
    the PNG under each of a node's text line boxes, masks off the glyph ink
    (plus a 2px dilation for anti-aliased edges), and measures the fraction of
    remaining BACKGROUND pixel pairs that straddle a high-contrast luminance
    step. A solid or smooth-gradient background scores ~0; an arc, stroke, or
    dense texture crossing the text scores high. Returns the worst background
    edge density over the node's line boxes (0..1), or None if unmeasurable.
    Never a FAIL and never a threshold on legibility itself: it only points the
    pixel critics at a box to judge by eye.
    """
    color = parse_css_color(node.get("color"))
    if color is None:
        return None
    lines = node.get("lines") or [[node["x"], node["y"], node["w"], node["h"]]]
    H, W = img_arr.shape[:2]
    worst = None
    for bx, by, bw, bh in lines:
        x0, y0 = max(0, int(bx * scale)), max(0, int(by * scale))
        x1, y1 = min(W, int((bx + bw) * scale)), min(H, int((by + bh) * scale))
        if x1 - x0 < 8 or y1 - y0 < 8:
            continue
        crop = img_arr[y0:y1, x0:x1, :3].astype(float)
        lum = 0.2126 * crop[..., 0] + 0.7152 * crop[..., 1] + 0.0722 * crop[..., 2]
        ink = np.abs(crop - np.array(color)).sum(axis=2) < BUSY_INK_DIST
        if ink.mean() > 0.75:
            continue  # box is almost all ink colour (solid plate); nothing to read under
        bg = ~_dilate(ink, BUSY_DILATE)
        hd = np.abs(lum[:, 1:] - lum[:, :-1]); hb = bg[:, 1:] & bg[:, :-1]
        vd = np.abs(lum[1:, :] - lum[:-1, :]); vb = bg[1:, :] & bg[:-1, :]
        tot = int(hb.sum()) + int(vb.sum())
        if tot < 50:
            continue
        edges = int(((hd > BUSY_EDGE_LUM) & hb).sum()) + int(((vd > BUSY_EDGE_LUM) & vb).sum())
        d = edges / tot
        worst = d if worst is None else max(worst, d)
    return worst


GLYPH_RING_IN = 2       # px of anti-aliased glyph edge skipped before the ring starts
GLYPH_RING_OUT = 5      # px outer radius of the ring sampled around the glyphs
GLYPH_MIN_SPAN = 20     # min |paper - ink| luminance span to reason about at all
GLYPH_SAME_FRAC = 0.5   # ring pixel counts as foreign ink when it is this much closer to ink than paper
GLYPH_WARN = 0.02       # contaminated ring fraction that points the critics at the label
GLYPH_FAIL = 0.07       # contaminated ring fraction that, WITH extent, is a crossed label
GLYPH_FAIL_EXTENT = 0.30  # fraction of the label's columns (or rows) the contamination spans


def glyph_ink_contamination(img_arr, node, scale):
    """FAIL-grade detector for a label CROSSED by canvas/SVG geometry.

    Added 2026-07-25. busy_art_under_text() only WARNs, and only looked at
    primary text (>= 30px), so the art-band mono labels of run 2026-07-25 (24px)
    were never sampled at all: groove edges, scored slot outlines and leader
    rules ran straight through four slides' label glyphs and qa.py reported PASS
    with zero warns across TWO scoring cycles (two hard fails, score capped 6.9).

    Measures the DEFENSE rather than the busyness, which is what separates the
    defect from legitimate art-band typography: sample a thin ring around the
    glyph ink (skipping GLYPH_RING_IN px of anti-aliasing) and count ring pixels
    whose luminance is closer to the GLYPH's own value than to the local paper
    value. A knockout plate, a halo, or any deliberate contrast reserve leaves
    that ring clean (a halo is the OPPOSITE value, so it never trips). A rule,
    outline or groove edge crossing the letterforms puts ink of the glyph's own
    value directly against them, all the way across the label.

    Returns (frac, extent) where frac is the contaminated share of the ring and
    extent is the larger of the column/row span of that contamination (a rule
    crossing a label contaminates nearly every column; a single incidental blob
    contaminates few), or None when unmeasurable.
    """
    color = parse_css_color(node.get("color"))
    if color is None:
        return None
    ink_lum = 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]
    lines = node.get("lines") or [[node["x"], node["y"], node["w"], node["h"]]]
    H, W = img_arr.shape[:2]
    worst = None
    for bx, by, bw, bh in lines:
        # pad the box so the ring is measurable at the glyph extremes
        x0, y0 = max(0, int(bx * scale) - 3), max(0, int(by * scale) - 3)
        x1, y1 = min(W, int((bx + bw) * scale) + 3), min(H, int((by + bh) * scale) + 3)
        if x1 - x0 < 8 or y1 - y0 < 8:
            continue
        crop = img_arr[y0:y1, x0:x1, :3].astype(float)
        lum = 0.2126 * crop[..., 0] + 0.7152 * crop[..., 1] + 0.0722 * crop[..., 2]
        ink = np.abs(crop - np.array(color)).sum(axis=2) < BUSY_INK_DIST
        if ink.mean() > 0.75 or ink.sum() < 20:
            continue  # solid plate of the ink colour, or no glyph ink found
        near = _dilate(ink, GLYPH_RING_IN)
        far = _dilate(ink, GLYPH_RING_OUT)
        ring = far & ~near
        if int(ring.sum()) < 40:
            continue
        outer = ~far
        paper = float(np.median(lum[outer])) if int(outer.sum()) > 40 else float(np.median(lum[ring]))
        span = abs(paper - ink_lum)
        if span < GLYPH_MIN_SPAN:
            continue  # ink and ground are near-equal; the contrast gate owns this
        cont = np.abs(lum[ring] - ink_lum) < GLYPH_SAME_FRAC * span
        frac = float(cont.mean())
        cmask = np.zeros_like(ring)
        cmask[ring] = cont
        extent = max(float(cmask.any(axis=0).mean()), float(cmask.any(axis=1).mean()))
        if worst is None or frac > worst[0]:
            worst = (frac, extent)
    return worst


FB_DOWN = 6          # box-downsample factor: kills film grain, keeps structure
FB_CELL = 9          # downsampled px per grid cell (9*6 = 54 png px = 27 design px)
FB_LIVE = 8.0        # cell energy (0..255 luminance spread) at which a cell holds anything
FB_MODELED = 0.55    # tonal entropy at which that content is MODELED, not flat fill
FB_MARGIN = 3        # cells of the 80px safe-margin ring excluded from the bands
FB_FAIL = 0.60       # bottom-band craft density / frame craft density = top-loaded
FB_WARN = 0.80


FEED_W = 432          # the thumb width the doctrine's legibility test uses

# NO PASS/FAIL THRESHOLD ON WHETHER AN ENCODING *WORKS*, DELIBERATELY. See
# encoding_reads() for the calibration that killed the two obvious candidates.
# That block MEASURES and does not judge, and anyone adding a quality threshold
# must first show it separates a known-bad encoding from a known-good one on
# real renders.
#
# ENC_DIFFER_MIN_DE IS NOT THAT THRESHOLD. It answers a strictly narrower and
# purely mechanical question -- did the probe measure ANYTHING -- and it is only
# ever applied to a direction THE SLIDE ITSELF DECLARED. See the DIRECTION
# CONTRACT block in encoding_reads() for the fit.
ENC_DIFFER_MIN_DE = 4.0
ENC_READS_VALUES = ("differ", "same")


def _srgb_to_lab(a):
    """sRGB 0..255 -> CIELAB. Written out rather than imported: the engine's
    dependency surface is part of its reliability and slides stay offline."""
    a = a.astype(np.float64) / 255.0
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    t = (lin @ m.T) / np.array([0.95047, 1.0, 1.08883])
    d = 6.0 / 29.0
    f = np.where(t > d ** 3, np.cbrt(t), t / (3 * d * d) + 4.0 / 29.0)
    return np.stack([116 * f[..., 1] - 16,
                     500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], -1)


def _rank_auc(x, y):
    """Mann-Whitney AUC folded to 0.5..1. 0.5 = the two sets are one set."""
    allv = np.concatenate([x, y])
    order = np.argsort(allv, kind="mergesort")
    sv = allv[order]
    ranks = np.empty(len(allv), float)
    i = 0
    while i < len(sv):
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    n1 = len(x)
    u1 = ranks[:n1].sum() - n1 * (n1 + 1) / 2.0
    a = u1 / (n1 * len(y))
    return max(a, 1.0 - a)


def encoding_reads(img_arr, enc, design_w, design_h):
    """MEASURE a declared wordless encoding. Deliberately does not judge it.

    Built 2026-07-29 to close the standing artwork-craft weakness (lowest
    criterion in 16 of the first 19 runs) by testing whether a slide's art
    actually carries the argument it claims. Two candidate metrics were
    calibrated against real renders, using that run's own hero as the
    known-bad (the scorer: the column "reads as one uniform amber extrusion",
    its declared steel-below-brass-above material change did not survive) and
    slide 07's sodium-to-slate ownership boundary as the known-good (a turn
    the scorer and the flow critic both called the deck's best fusion beat).

    BOTH METRICS FAILED TO SEPARATE THEM, and in the worst direction:

      known-bad  S03 steel vs brass    dE 49.0  AUC 0.87  visible 58/83 pct
      known-good S07 sodium vs slate   dE 12.2  AUC 0.77  visible 54/53 pct

    Colour separability is HIGHER on the broken encoding than on the working
    one, because the steel really is a different colour where you can see it;
    it just reads as a glassy plinth rather than as half the object. And the
    occlusion fraction is LOWER on the working one, because a deliberate
    composition puts type over its own art. Any threshold drawn through these
    numbers passes the defect and fails the success.

    The real defect is semantic, about shape, proportion and context ("is this
    read as part of the object"), and none of that is a colour statistic. So
    this function returns numbers for the pixel critics and the scorer to read,
    and qa.py raises no FAIL from them. That is the honest state of the art
    here, and it is recorded so the next attempt starts from the evidence
    rather than from the same intuition. Making it a gate needs encoding
    declarations across the back catalogue so a threshold can be FITTED rather
    than guessed, which is a corpus exercise, not a slot at the end of a run.

    THE DIRECTION CONTRACT (2026-08-08). Everything above is still true about
    JUDGING an encoding, and none of it is being softened. What run No.29 proved
    is that a probe can fail one step earlier, before any semantics are in play:
    slides 05 and 06 declared the deck's central wordless claim, the two probe
    rectangles were computed from the STORYBOARD'S CAMERA ARITHMETIC instead of
    measured off a render, and they landed on empty water about 300 design px
    left of where the aperture actually drew. The declaration reported dE 0.9 /
    AUC 0.58, the deck's own build gate never gated anything, and the scorer
    caught it at the ship gate and made it the run's one_sentence_fix. The same
    failure had already happened once earlier in that run, on a probe pair that
    reported the DARK frame as brighter than the lit one.
    The light itself was fine: measured off the shipped pixels the aperture runs
    98.3 L* lit against 26.9 L* unlit. The rectangle was wrong.

    So a slide now says WHICH WAY its declaration should read, and that one word
    is checked:

      "reads":"differ"  the two regions must be tellable apart
      "reads":"same"    an absence or sameness claim; they should match

    A declaration with no `reads` is a FAIL, not a pass. It is the same rule
    caption_check.py applies to a missing --ledger and a missing brand.yaml: a
    check that cannot look is a failure, not a stale green. An encoding that
    states no direction is a number nobody can be wrong about, which is exactly
    what shipped. The repair is one word, and typing it is the point: you cannot
    write "differ" without going and looking at what the render actually did.
    Slides that declare no encoding at all are untouched; the contract stays
    opt-in.

    THE FLOOR IS FITTED, NOT GUESSED, over every data-encodes line in the
    shipped corpus (runs/*/machine_qa.json, 19 declarations across 7 runs):

      the DIFFER claims that worked        dE 12.1, 15.0, 15.7, 15.9, 20.8,
                                              23.7, 24.7, 25.3, 27.6, 31.9, 73.6
      the low cluster, all SAMENESS or
        ABSENCE claims where a small dE
        is the CORRECT answer              dE 0.4 'three ticks stand alone with
                                              nothing drawn between them',
                                              1.6, 2.2, 4.6 'three equal
                                              swellings on a bare plate', 4.9
      the known DEFECT, run No.29          dE 0.9 and dE 3.5, both probes off
                                              their own aperture

    4.0 sits under every confirmed working differ claim by a factor of three and
    over the run No.29 defect, and the low cluster is not in its way because
    those claims declare "same" and are not gated. Note what this floor
    deliberately does NOT do: the 2026-07-29 known-bad, the steel-below-brass
    column the scorer said read as one uniform extrusion, measured dE 49.0 and
    PASSES here, correctly, because this is not a judgment of whether the
    encoding works. The calibration above still stands; nothing here revisits it.
    No threshold is drawn for "same", because the corpus has no known-bad for
    that direction to fit one against, and guessing is what this docstring
    exists to prevent.

    Returns (verdict, detail) where verdict is "info", "warn" or "fail".
    """
    if enc.get("error"):
        return "warn", f"declaration did not parse ({enc['error']})"
    ra, rb = enc.get("a") or [], enc.get("b") or []
    if not ra or not rb:
        return "warn", "declaration names no regions"

    im = Image.fromarray(img_arr)
    s = FEED_W / float(design_w)
    feed = np.asarray(im.resize((FEED_W, max(1, int(round(design_h * s)))), Image.LANCZOS))

    def take(rects):
        out = []
        for r in rects:
            x, y, w, h = r
            x0, y0 = max(0, int(x * s)), max(0, int(y * s))
            x1 = min(feed.shape[1], int((x + w) * s))
            y1 = min(feed.shape[0], int((y + h) * s))
            if x1 > x0 and y1 > y0:
                out.append(feed[y0:y1, x0:x1].reshape(-1, 3))
        return np.concatenate(out) if out else np.zeros((0, 3))

    A, B = take(ra), take(rb)
    va = enc.get("a_visible_frac")
    vb = enc.get("b_visible_frac")
    # Visible AREA, not declared area: a region can be large and still unseen.
    area_a = len(A) * (va if va is not None else 1.0)
    area_b = len(B) * (vb if vb is not None else 1.0)

    bits = []
    if va is not None:
        bits.append(f"visible {va:.0%}/{vb:.0%}")
    bits.append(f"seen {int(area_a)}/{int(area_b)}px at {FEED_W}w")

    if len(A) < 12 or len(B) < 12:
        return "warn", "region too small to measure at feed scale, " + ", ".join(bits)

    la, lb = _srgb_to_lab(A), _srgb_to_lab(B)
    ma, mb = np.median(la, 0), np.median(lb, 0)
    axis = mb - ma
    n = float(np.linalg.norm(axis))
    auc = _rank_auc(la @ axis / n, lb @ axis / n) if n > 1e-9 else 0.5
    bits.insert(0, f"dE {n:.1f}, AUC {auc:.2f}")
    detail = f"'{enc.get('claim', '')}': " + ", ".join(bits)

    # THE DIRECTION CONTRACT. See the docstring for the fit and for why this is
    # not the quality threshold the calibration rejected.
    reads = str(enc.get("reads") or "").strip().lower()
    if reads not in ENC_READS_VALUES:
        said = "nothing" if not reads or reads == "any" else repr(enc.get("reads"))
        return "fail", (
            "the declaration says %s about which way it should read, so no "
            "check on it is possible and the number below is not evidence. Add "
            '"reads":"differ" (the two regions must be tellable apart) or '
            '"reads":"same" (an absence or sameness claim). Measured %s'
            % (said, detail))
    if reads == "differ" and n < ENC_DIFFER_MIN_DE:
        return "fail", (
            "%s. The slide declares reads:\"differ\" and the two regions are "
            "%.1f dE apart at %dpx wide, under the %.1f floor: at feed scale "
            "these are one population, so this probe is measuring the same "
            "thing twice. The usual cause is a region computed from the "
            "storyboard's camera arithmetic rather than MEASURED off a render. "
            "Open the PNG, find where the feature actually drew, and author the "
            "rects from that."
            % (detail, n, FEED_W, ENC_DIFFER_MIN_DE))

    return "info", detail


# CONTACT SHADOW READ THRESHOLDS, in CIELAB L* at feed scale (432px wide).
# FITTED, not guessed, from run No.26 (2026-08-05), the run that produced the
# defect this gate exists to catch:
#
#   known-bad, the shipped defect    #1A0F08 @ a0.55 over #0B0906 -> dL 1.24
#   known-bad, measured in the final renders of the three slides the scorer
#     still called "floating-adjacent" (S01, S06, S09): the whole ground band
#     below the object varies by 1.6 to 2.0 L* end to end, i.e. no dip at all
#   known-half-good, the mid-run repair (a warm ground pool at #2A2118 under
#     the object, then the same shadow) -> dL 4.3 measured in the reconstruction
#     under out/upgrade-2026-08-05/, and the scorer's verdict on it was
#     "half landed"
#   known-GOOD, measured in the shipped render of slide 04, whose bar-base
#     shadows the scorer and the pixel critics called convincing: dL 8.1 at
#     both bars (shadow L* 81.7 / 82.7 against paper at L* 89.8 / 90.7)
#
# So FAIL below 4.0 sits under everything that has ever read at all and above
# everything that measurably did not, and WARN below 8.0 lands one tenth of an
# L* under the studio's own known-good, which is where a comfort band belongs:
# the half-landed repair warns, the shadow that convinced does not. A JND for
# two large flat patches side by side
# is about 0.4 L*, so 4.0 is an order of magnitude over it: the margin pays
# for the LANCZOS downscale to feed width, the paper tooth and film grain the
# shadow is composited into, and the fact that a blurred shadow has no edge to
# help the eye. Raising these is a tightening and is fine; lowering them is
# the maintainer's call.
# A leader may stop a little short of the feature it points at -- the drafting
# gap is real practice -- but a gap is a few px, not a journey. 24 design px is
# 2.2% of the frame width, comfortably past any intentional gap and far inside
# run No.28's misses (300 and 240 px). Tolerance, not a threshold to tune down.
LEADER_LAND_PX = 24.0


def leader_lands(ld):
    """CHECK A DECLARED LEADER AGAINST ITS DECLARED TARGET (2026-08-07).

    Run No.28's slide 06 shipped two drafting detail circles whose leader lines
    ran out into empty void, through two pixel critics, a flow critic and the
    first scoring cycle. Nobody was careless: a leader stopping in void looks
    exactly like a leader reaching something small, and the tails were authored
    as fixed pixel deltas from each circle's OWN center
    (tail:[-70,-70,-150,-150]), so there was no place in the slide, the record
    or the pipeline where the target was ever named. There was nothing to check.

    A PIXEL test cannot answer this and was rejected rather than shipped weak:
    the leader's own landing tick puts ink at its terminus, so "is there ink
    where it ends" is always yes, and any corridor-masked variant of it would
    fire on legitimate art. What the machine CAN check is arithmetic the author
    supplies: where the leader ends, and where the feature it enlarges actually
    is. Two points, one distance. This is the same shape as the contact-shadow
    and encoding contracts -- opt-in, declared by the slide, failed only when
    the slide contradicts itself -- and the real work it does is in the
    authoring: you cannot write `at:` without going and finding the target's
    coordinates, which is exactly the step the defect skipped.

    Returns (verdict, detail): "fail" (the declaration disagrees with itself),
    "warn" (the declaration is unusable, an authoring error) or "ok".
    """
    name = ld.get("target")
    to, at = ld.get("to"), ld.get("at")
    if not name:
        return "warn", ("a leader was declared with no target name; every "
                        "leader names the feature it points at")
    if not to or not at:
        miss = "to" if not to else "at"
        return "warn", ("leader %r declares no numeric %r point (both `to`, "
                        "where the leader ends, and `at`, the target's own "
                        "coordinates, are required)" % (name, miss))
    d = math.hypot(to[0] - at[0], to[1] - at[1])
    if d > LEADER_LAND_PX:
        return "fail", ("the leader for %r ends at (%g,%g) but that feature is "
                        "declared at (%g,%g), %.0f design px away (tolerance "
                        "%.0f). Author the leader as a world-coordinate "
                        "polyline that terminates ON the target's coordinates, "
                        "not as an offset from the annotation's own center"
                        % (name, to[0], to[1], at[0], at[1], d, LEADER_LAND_PX))
    return "ok", "leader %r lands %.1fpx from its target" % (name, d)


CONTACT_FAIL_DL = 4.0
CONTACT_WARN_DL = 8.0


def contact_reads(img_arr, con, design_w, design_h):
    """MEASURE a declared contact shadow against the ground it claims to darken.

    Built 2026-08-05. Every other gate here judges legibility, collision or
    composition. Nothing asked whether a declared DEPTH CUE survived
    compositing, so the run that made the contact edge its whole declared
    attack shipped a shadow worth 1.2 L* on top of a near-black table, four
    pixel critics reported the object floating, and machine QA returned zero
    fails. A shadow is a subtraction; it needs something to subtract from.

    Unlike encoding_reads() this one DOES fail, and the reason it can is that
    the question is one-dimensional and the slide asked it itself. "Is this
    region darker than that region" needs no semantics, no shape reading and
    no taste. A FAIL here is the slide contradicting its own declaration.

    Returns (verdict, detail), verdict in "info" | "warn" | "fail".
    """
    if con.get("error"):
        return "warn", "declaration did not parse (%s)" % con["error"]
    rs, rg = con.get("shadow") or [], con.get("ground") or []
    if not rs or not rg:
        return "warn", "declaration names no shadow/ground region"

    im = Image.fromarray(img_arr)
    s = FEED_W / float(design_w)
    feed = np.asarray(im.resize((FEED_W, max(1, int(round(design_h * s)))), Image.LANCZOS))

    def take(rects):
        out = []
        for r in rects:
            x, y, w, h = r
            x0, y0 = max(0, int(x * s)), max(0, int(y * s))
            x1 = min(feed.shape[1], int((x + w) * s))
            y1 = min(feed.shape[0], int((y + h) * s))
            if x1 > x0 and y1 > y0:
                out.append(feed[y0:y1, x0:x1].reshape(-1, 3))
        return np.concatenate(out) if out else np.zeros((0, 3))

    S, G = take(rs), take(rg)
    what = con.get("what", "") or "contact shadow"
    if len(S) < 12 or len(G) < 12:
        return "warn", ("'%s': region too small to measure at feed scale "
                        "(%d/%d px at %dw)" % (what, len(S), len(G), FEED_W))

    ls = float(np.median(_srgb_to_lab(S)[..., 0]))
    lg = float(np.median(_srgb_to_lab(G)[..., 0]))
    d = lg - ls
    bits = "'%s': shadow L* %.1f vs ground L* %.1f, dL %.1f at %dw" % (
        what, ls, lg, d, FEED_W)

    if d < CONTACT_FAIL_DL:
        extra = ""
        if lg < 12.0:
            # The exact shape of the No.26 defect, named so the fix is obvious.
            extra = (" -- the ground is already near black (L* %.1f), so there "
                     "is nothing left to subtract; light the ground first "
                     "(a warm pool under the object), then cast the shadow"
                     % lg)
        return "fail", bits + (" -- below the %.1f L* floor, the object floats"
                               % CONTACT_FAIL_DL) + extra
    if d < CONTACT_WARN_DL:
        return "warn", bits + (" -- under the %.1f L* comfort band; it reads, "
                               "barely" % CONTACT_WARN_DL)
    return "info", bits


def _box_down(a, k):
    h, w = a.shape[:2]
    h -= h % k
    w -= w % k
    return a[:h, :w].reshape(h // k, k, w // k, k, -1).mean(axis=(1, 3))


def frame_balance(img_arr):
    """Detect a TOP-LOADED composition -- the 'dead lower zone' that has capped
    artwork craft at 6-7 for six consecutive runs (ledger entries 10, 11, 13,
    14, 15, 16, 18).

    Added 2026-07-26 after the sixth consecutive scorer note naming the same
    defect. The root cause was never a missing pair of eyes, it was
    DESIGN_DOCTRINE 1's "at least one generous quiet zone per slide": an
    unbounded, unplaced licence that the directors room kept spending on the
    frame's bottom band, because that is the cheapest place to put it. The
    dossier then legitimized the empty bottom, and the pixel critics grade each
    slide against its own dossier, so the only reviewer who ever saw the defect
    was the scorer -- at the ship gate, with no budget left to rebuild slides.
    Every run it therefore became a FIELD_NOTES sentence instead of a fix.

    TWO defects share the name, and separating them is what took this from a
    note to a gate. (1) The bottom band is EMPTY (2026-07-17 S09 and
    2026-07-20 S03 both ship a bottom 40% with nothing in it; neither was ever
    named, which is its own evidence about relying on eyes). (2) The bottom
    band is OCCUPIED BUT FLAT -- grey label plates and hairlines floating on
    bare ground, which is what 2026-07-26's S05 and S08 actually are. A plain
    occupancy measure sees only (1): across the 45 scorer-labeled slides the
    dead ones' whole-frame occupancy (median 0.505) is indistinguishable from
    the rest (0.537), because every slide has quiet margins and a flat plate
    counts as "occupied".

    So a cell only counts when it carries MODELED tone. Box-downsample the PNG
    6x (film grain is high-frequency and would otherwise read as craft
    everywhere), then per 27px design cell take the robust luminance spread and
    peak local gradient (does it hold anything at all) AND the normalized
    entropy of its tonal histogram (is that content modeled or flat). A flat
    plate is bimodal and scores ~0.2; graded, textured, lit or rendered art
    scores 0.7+. Drop the safe-margin ring, then compare the bottom third's
    craft density against the slide's OWN frame average.

    Deliberately RELATIVE. An absolute craft floor was tested and rejected: it
    fails 48-60% of every slide the series has ever shipped, which makes it a
    taste judgment the machine has no business making unilaterally, and the
    doctrine's own position is that flat is a legitimate choice. The ratio
    asks only the question the scorers kept asking, which is whether the slide
    spends its craft up top and coasts. Content spread through the frame
    scores ~1.0 at any density.

    Returns (ratio, bands) or None if unmeasurable.
    """
    d = _box_down(img_arr.astype(np.float32), FB_DOWN)
    lum = 0.2126 * d[..., 0] + 0.7152 * d[..., 1] + 0.0722 * d[..., 2]
    rows, cols = lum.shape[0] // FB_CELL, lum.shape[1] // FB_CELL
    if rows < 3 * FB_MARGIN + 6 or cols < 2 * FB_MARGIN + 2:
        return None
    lum = lum[:rows * FB_CELL, :cols * FB_CELL]
    cells = lum.reshape(rows, FB_CELL, cols, FB_CELL).transpose(0, 2, 1, 3)
    cells = cells.reshape(rows, cols, FB_CELL * FB_CELL)
    # robust spread (p90-p10) ignores a lone anti-aliased pixel; the gradient
    # term keeps a single hard edge through an otherwise flat cell counted.
    spread = np.percentile(cells, 90, axis=2) - np.percentile(cells, 10, axis=2)
    gx, gy = np.abs(np.diff(lum, axis=1)), np.abs(np.diff(lum, axis=0))
    g = np.zeros_like(lum)
    g[:, :-1] += gx; g[:, 1:] += gx; g[:-1, :] += gy; g[1:, :] += gy
    gc = g.reshape(rows, FB_CELL, cols, FB_CELL).transpose(0, 2, 1, 3).reshape(rows, cols, -1)
    live = np.maximum(spread, np.percentile(gc, 98, axis=2)) >= FB_LIVE

    # modeled-tone test: normalized entropy of each cell's luminance histogram
    bins = 12
    rng = cells.max(axis=2) - cells.min(axis=2)
    q = np.clip((cells - cells.min(axis=2, keepdims=True)) /
                np.maximum(rng[..., None], 1e-6) * (bins - 1), 0, bins - 1).astype(np.int8)
    ent = np.zeros(q.shape[:2], dtype=np.float32)
    for b in range(bins):
        p = (q == b).sum(axis=2) / q.shape[2]
        ent -= np.where(p > 0, p * np.log2(np.maximum(p, 1e-12)), 0)
    ent = np.where(rng >= 2.0, ent / np.log2(bins), 0.0)

    craft = live & (ent >= FB_MODELED)
    inner = craft[FB_MARGIN:rows - FB_MARGIN, FB_MARGIN:cols - FB_MARGIN]
    band = inner.shape[0] // 3
    if band < 2:
        return None
    occ = float(inner.mean())
    if occ < 1e-6:
        return None  # the near-uniform gate above owns a truly blank frame
    bands = [float(inner[:band].mean()), float(inner[band:2 * band].mean()),
             float(inner[2 * band:].mean())]
    return bands[2] / occ, bands


# TEXT STRUCK BY A DRAWN RULE (2026-08-18). See rule_strikes().
#
# WCAG 2.1 SC 1.4.11 Non-text Contrast. A rule only reads as a strikethrough if
# a reader can see it, and the published floor for "visual information required
# to identify graphical objects" is 3.0:1 against adjacent colour. This is that
# standard, used as written; it is not a number measured off this corpus, so it
# cannot ratchet. Below it, a hairline is the decoration GATE_LESSONS 7 says a
# divider is allowed to be, and this gate says nothing about it.
RULE_VISIBLE_RATIO = 3.0
# A RULE THROUGH A WORD DOES NOT NEED TO BE A VISIBLE GRAPHIC TO RUIN THE WORD.
#
# 2026-08-26. Frame 9 shipped a separator at rgba(58,52,42,0.30) over #F2EEE4 running through
# "with a state body.", plainly visible in the render, and this file passed the frame with zero
# fails. The rule measured about 1.6:1 against the paper, under RULE_VISIBLE_RATIO, and was
# skipped as "a quiet divider; WCAG 1.4.11 asks nothing of it".
#
# That reasoning is right for a divider sitting in the leading and wrong for one crossing a glyph
# band, because the eye judges an in-band rule against the LETTERFORMS it crosses rather than
# against the paper beside it. So the two cases get two floors: a divider in the leading still has
# to clear 3.0 before this file says anything about it, and a rule through the words has to clear
# only enough to be distinguishable from the paper at all.
RULE_STRIKE_RATIO = 1.25
# ...AND IT HAS TO CROSS THE MIDDLE OF THE LETTERS, not the line box.
#
# The first cut of the lower floor fired on two things that are not strikethroughs: frame 3's
# seating channel, which runs at the letters' FEET by design and is the whole reason that board
# reads as a letterboard, and the top edge of frame 9's own notice sheet, which grazes the hook's
# ascender line. Both sit inside the middle `em` of a line box, because a line box at 1.4 leading
# is half again as tall as its em.
#
# A strikethrough is a rule through the x-height. This is the fraction of the em, centred on the
# line's optical centre, that a rule has to cross before this file calls it one.
RULE_STRIKE_BAND = 0.45
RULE_SAMPLE_MIN = 24   # device px of clean strip needed before a colour is claimed

OCC_FAIL_W = 20     # px of a line box's WIDTH an opaque plate must cover to FAIL
OCC_FAIL_H = 6       # px of its HEIGHT (a quarter of the 24px mono floor)
OCC_WARN_W = 12      # the tripwire band below the FAIL, for the critics' eyes
OCC_WARN_H = 4


# --------------------------------------------------------------------------- standing furniture
#
# THE DEFECT (2026-08-29, deck no. 11, and all three judges opened with it).
#
# The cover's foot is one flex row: an eyebrow, a cite line, the site address and the progress
# counter, inside a 920px measure. Round 3 added one more claim id to the cite. The row went past
# its measure, the flex line broke, and the cover printed the canonical URL as
# "texasaidocket.com01 /" with "09" alone on a second line, on three frames.
#
# NOTHING COULD SEE IT. coherence_check.check_site_line reads the span's TEXT, finds
# `texasaidocket.com`, and passes, which is correct and is the whole of GATE_LESSONS' recurring
# sentence: a checker sees what it reads and the product is what a reader receives. The DOM was
# right. The pixels were wrong. CLAUDE.md's public URL section is specifically about that string
# and the gate written for it is blind to the one way it can be rendered wrong.
#
# The run's repair was a per-frame assertion pasted into all nine slides, measuring the foot's own
# client rects. That is the right measurement in the wrong place: it works for one deck and every
# future deck has to remember to paste it.
#
# WHAT IS ASSERTED HERE, AND WHY IT NEEDS NO THRESHOLD.
#
# The deck's STANDING FURNITURE is the text that appears on every frame: the wordmark, the site
# address, the progress counter. `coherence_check` already calls that the frame that does not
# vary. So the assertion is a comparison rather than an absolute, which is entry 10's rule for
# exactly this situation: where two renderings are meant to agree, compare them instead of holding
# each to a number somebody typed.
#
#     A piece of standing furniture lays out on the SAME NUMBER OF LINES on every frame.
#
# Six frames gave the counter one line and three gave it two. That is the finding, and it needs no
# opinion about how many lines a counter ought to have.
#
# MEASURED on all ten decks shipped before this one, 86 frames: every standing item is one line on
# every frame of its deck. Zero false positives. It also cannot fire on a deck whose repeated
# furniture is legitimately two lines, because two lines everywhere is agreement.
#
# THE BLIND SPOT, stated rather than implied. If a row breaks on EVERY frame the counts agree and
# this says nothing. Catching that would need a number for how many lines furniture may have, and
# a typed number is what this project's own law forbids. The frame-level assertion the run wrote,
# which measures the row against its own container, is the honest way to close it, and it belongs
# in the frame contract rather than here.
_COUNTER_TEXT = re.compile(r"^\d{1,3}\s*/\s*\d{1,3}$")


def _furniture_key(text):
    """One key for a piece of standing furniture, whatever it says on this frame.

    The progress counter reads 01 / 09 on one frame and 02 / 09 on the next. Those are the same
    object and a comparison keyed on the literal string would never find it on any frame twice.
    Everything else is keyed on itself.
    """
    t = " ".join(str(text).split())
    return "NN / NN" if _COUNTER_TEXT.match(t) else t


def standing_furniture(report):
    """{furniture text: {slide file: line count}} for text that stands on EVERY frame.

    Returns ({}, reason) when the report cannot answer, which is not the same event as finding
    nothing wrong and must not print the same colour. GATE_LESSONS 37.
    """
    slides = report.get("slides") or []
    if len(slides) < 2:
        return {}, "a deck of one frame has no frames to compare"
    per = []
    for rec in slides:
        seen = {}
        for nd in rec.get("text_nodes") or []:
            t = _furniture_key(nd.get("text", ""))
            if not t:
                continue
            lines = nd.get("lines")
            if lines is None:
                return {}, "this render report predates per-node line boxes, so nothing was compared"
            seen[t] = max(seen.get(t, 0), len(lines) or 1)
        per.append((rec.get("file", "?"), seen))
    common = set.intersection(*[set(s) for _, s in per]) if per else set()
    return {t: {f: s[t] for f, s in per} for t in sorted(common)}, ""


def furniture_breaks(report):
    """[(slide file, message)] for standing furniture that wraps on some frames and not others."""
    table, why = standing_furniture(report)
    out = []
    for text, per_file in table.items():
        counts = set(per_file.values())
        if len(counts) < 2:
            continue
        least = min(counts)
        for f, n in per_file.items():
            if n == least:
                continue
            good = sorted(x for x, c in per_file.items() if c == least)
            out.append((f, (
                f"standing furniture wrapped: '{text}' lays out on {n} lines here and on "
                f"{least} on {len(good)} other frame(s) ({', '.join(good[:4])}"
                f"{'...' if len(good) > 4 else ''}). The row it sits in ran past its measure and "
                f"the line broke. A checker reading DOM text cannot see this: on 2026-08-29 the "
                f"cover printed 'texasaidocket.com01 /' with the counter on a second line while "
                f"coherence_check read the span and passed. Shorten the row or give it more "
                f"measure; never let the frame decide by wrapping")))
    return out, why


def text_collisions(nodes, min_overlap=0.30, min_px=8):
    """Detect text-on-text overprint between distinct elements.

    Compares per-LINE boxes (render.py extracts them; falls back to the
    element bbox), skips DOM ancestor/descendant pairs, and counts a
    collision when the intersection covers >= min_overlap of the smaller
    line box in both dimensions beyond min_px. Returns
    [(i, j, overlap_ratio)] with i < j indexing `nodes`.
    """
    found = []
    for i in range(len(nodes)):
        a = nodes[i]
        a_lines = a.get("lines") or [[a["x"], a["y"], a["w"], a["h"]]]
        a_anc = set(a.get("anc") or [])
        for j in range(i + 1, len(nodes)):
            b = nodes[j]
            if i in (b.get("anc") or []) or j in a_anc:
                continue  # nested elements share ink legitimately
            b_lines = b.get("lines") or [[b["x"], b["y"], b["w"], b["h"]]]
            worst = 0.0
            for ax, ay, aw, ah in a_lines:
                for bx, by, bw, bh in b_lines:
                    ix = min(ax + aw, bx + bw) - max(ax, bx)
                    iy = min(ay + ah, by + bh) - max(ay, by)
                    if ix < min_px or iy < min_px:
                        continue
                    smaller = min(aw * ah, bw * bh)
                    if smaller <= 0:
                        continue
                    worst = max(worst, (ix * iy) / smaller)
            if worst >= min_overlap:
                found.append((i, j, worst))
    return found


def _text_mask(nodes, shape, scale):
    """Device-pixel mask of every text line box on the slide, dilated 2px.

    Used to keep glyph ink out of the colour samples taken for a drawn rule and
    for the paper beside it. A median over a region that includes letterforms is
    a median of the wrong population, which is the mistake GATE_LESSONS 26 is
    about: do not measure a thing through something else that is sitting on it.
    """
    m = np.zeros(shape[:2], dtype=bool)
    for n in nodes:
        for bx, by, bw, bh in (n.get("lines") or [[n["x"], n["y"], n["w"], n["h"]]]):
            x0 = max(0, int(bx * scale) - 2)
            y0 = max(0, int(by * scale) - 2)
            x1 = min(shape[1], int(math.ceil((bx + bw) * scale)) + 2)
            y1 = min(shape[0], int(math.ceil((by + bh) * scale)) + 2)
            if x1 > x0 and y1 > y0:
                m[y0:y1, x0:x1] = True
    return m


def _clean_median(img_arr, tmask, x0, y0, x1, y1):
    H, W = img_arr.shape[:2]
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(W, int(x1)), min(H, int(y1))
    if x1 <= x0 or y1 <= y0:
        return None, 0
    sub = img_arr[y0:y1, x0:x1, :3]
    keep = ~tmask[y0:y1, x0:x1]
    n = int(keep.sum())
    if n < RULE_SAMPLE_MIN:
        return None, n
    return np.median(sub[keep].astype(float), axis=0), n


def strip_visibility(img_arr, tmask, r, scale, reach):
    """MEASURE, off the PNG, whether a drawn strip reads against its own ground.

    Returns (ratio, ink_rgb, paper_rgb) or None when the paper beside the strip
    cannot be found within `reach` device px. Nothing is inferred from the
    declared CSS colour: an rgba hairline, a blend mode and a grain overlay all
    change what the reader receives, and only the composited pixel knows.

    TWO THINGS THIS GETS RIGHT THAT THE FIRST DRAFT GOT WRONG, both found by
    replaying the 2026-08-18 defect rather than by reasoning about it.

    The ink is the strip's WORST (most contrasting) SCAN LINE, not the median
    over the strip. A 2 design px border occupies 4 device rows at scale 2 and
    paints about two of them, so a median over the whole strip reads halfway
    between the rule and the paper: the real rule measured 2.6:1 that way and
    7.6:1 correctly, and 2.6 is under the floor, so averaging would have passed
    the defect this gate exists for. This is the same correction
    contrast_worst_cell() made for text in 2026-07-31.

    The ink sample does NOT mask off text and the paper sample DOES. A rule
    spans its own scan line and glyphs cross it at a few x positions, so the
    row median is the rule; a band of paper inside a line box is mostly
    letterforms, so it has to be masked, and then looked for further out when
    the rule runs the whole width of the type.
    """
    sx0, sy0 = int(r["x"] * scale), int(r["y"] * scale)
    sx1 = int(math.ceil((r["x"] + r["w"]) * scale))
    sy1 = int(math.ceil((r["y"] + r["h"]) * scale))
    H, W = img_arr.shape[:2]
    sx0, sy0 = max(0, sx0), max(0, sy0)
    sx1, sy1 = min(W, sx1), min(H, sy1)
    if sx1 <= sx0 or sy1 <= sy0:
        return None
    horiz = r["w"] >= r["h"]
    t = max(1, (sy1 - sy0) if horiz else (sx1 - sx0))

    # paper first: widen away from the strip in steps of its own thickness
    paper = None
    step = t
    while step <= max(reach, t):
        if horiz:
            a, na = _clean_median(img_arr, tmask, sx0, sy0 - t - step, sx1, sy0 - t)
            b, nb = _clean_median(img_arr, tmask, sx0, sy1 + t, sx1, sy1 + t + step)
        else:
            a, na = _clean_median(img_arr, tmask, sx0 - t - step, sy0, sx0 - t, sy1)
            b, nb = _clean_median(img_arr, tmask, sx1 + t, sy0, sx1 + t + step, sy1)
        sides = [(v, c) for v, c in ((a, na), (b, nb)) if v is not None]
        if sides:
            paper = sum(v * c for v, c in sides) / sum(c for _, c in sides)
            break
        step *= 2
    if paper is None:
        return None
    lp = rel_luminance(paper)

    best = None
    for k in (range(sy0, sy1) if horiz else range(sx0, sx1)):
        line = img_arr[k:k + 1, sx0:sx1, :3] if horiz else img_arr[sy0:sy1, k:k + 1, :3]
        if line.size == 0:
            continue
        ink = np.median(line.reshape(-1, 3).astype(float), axis=0)
        li = rel_luminance(ink)
        lo, hi = min(li, lp), max(li, lp)
        ratio = (hi + 0.05) / (lo + 0.05)
        if best is None or ratio > best[0]:
            best = (ratio, ink, paper)
    return best


def canvas_rules(nodes, img_arr, scale):
    """FIND THE RULES THE DOM CANNOT DECLARE, so rule_strikes can judge them.

    THE DEFECT. rule_strikes was built in 2026-08-18 for a table border struck through a
    footnote, and it reads `rules` out of render_report.json, which is a DOM walk. On
    2026-08-19 slide 5 a canvas-drawn SHEET EDGE ran through the last line of a paragraph,
    twice, and the new gate never saw it, because a canvas edge is not a DOM element.

    Every fix in this file so far has enumerated one more kind of thing that can cross a word:
    text vs text, then opaque plates, then DOM rules. The class is ANYTHING DRAWN, and canvas
    is the half the DOM cannot describe. So this does not add a fourth special case. It
    recovers candidate strips FROM THE PIXELS and hands them to the existing judge, which
    already knows about em bands, plates, corner clips and WCAG 1.4.11.

    HOW A RULE IS TOLD FROM LETTERFORMS, which is the whole problem.

    Both are dark pixels inside a line box. The difference is CONTINUITY: glyphs give short
    runs broken by counters and side bearings, and a rule gives one unbroken run. So a row
    counts only when its longest CONTIGUOUS off-paper run reaches one em, which is the same
    unit rule_strikes already uses for "a character struck rather than a corner clipped", and
    it scales with the type instead of being typed here.

    Rows are merged into strips, and a strip at or over one em thick is dropped: that is a
    plate, and the occlusion probe owns plates. Everything surviving goes to rule_strikes,
    which measures it against the paper and stays silent under 3.0:1.
    """
    out = []
    if img_arr is None:
        return out
    h_px, w_px = img_arr.shape[0], img_arr.shape[1]
    grey = (0.2126 * img_arr[:, :, 0] + 0.7152 * img_arr[:, :, 1]
            + 0.0722 * img_arr[:, :, 2]) if img_arr.ndim == 3 else img_arr.astype(float)
    for n in nodes or []:
        if n.get("decorative"):
            continue
        em = float(n.get("font_px") or 0)
        if em <= 0:
            continue
        for bx, by, bw, bh in (n.get("lines") or [[n.get("x"), n.get("y"), n.get("w"), n.get("h")]]):
            try:
                bx, by, bw, bh = float(bx), float(by), float(bw), float(bh)
            except (TypeError, ValueError):
                continue
            if bw <= 0 or bh <= 0:
                continue
            cy = by + bh / 2.0
            b0, b1 = max(by, cy - em / 2.0), min(by + bh, cy + em / 2.0)
            y0, y1 = int(b0 * scale), int(b1 * scale)
            x0, x1 = int(bx * scale), int((bx + bw) * scale)
            y0, y1 = max(0, y0), min(h_px, y1)
            x0, x1 = max(0, x0), min(w_px, x1)
            if y1 - y0 < 2 or x1 - x0 < 4:
                continue
            need = max(4, int(em * scale))          # one em of unbroken run
            band = grey[y0:y1, x0:x1]
            paper = float(np.median(band))
            rows = []
            for r in range(band.shape[0]):
                off = np.abs(band[r] - paper) > 28.0   # clearly not the paper
                if not off.any():
                    continue
                best = run = 0
                for v in off:
                    run = run + 1 if v else 0
                    if run > best:
                        best = run
                if best >= need:
                    rows.append(r)
            # merge contiguous rows into strips
            for grp in _groups(rows):
                ry0, ry1 = grp[0], grp[-1] + 1
                th = (ry1 - ry0) / float(scale)
                if th <= 0 or th >= em:
                    continue                          # a plate, not a rule
                out.append({"x": bx, "y": (y0 + ry0) / float(scale),
                            "w": bw, "h": th,
                            "kind": "canvas edge", "by": "pixels"})
    return out


def _groups(idx):
    """Contiguous runs of row indices."""
    grp, out = [], []
    for i in idx:
        if grp and i == grp[-1] + 1:
            grp.append(i)
        else:
            if grp:
                out.append(grp)
            grp = [i]
    if grp:
        out.append(grp)
    return out


def rule_strikes(nodes, rules, img_arr, scale):
    """TEXT STRUCK BY A DRAWN RULE (2026-08-18). The class of collision every
    other gate in this file is structurally unable to see.

    THE DEFECT THIS EXISTS FOR. Run No.2's slide 09 closed the deck with a field
    table over a footnote. The table's `tr.last td { border-bottom: 2px }` drew a
    rule from x=84 to x=996 at y=1215, and the footnote's first line box was
    [84,1204,691,31] with a 24px face, so a dark 2px rule ran through the middle
    of the sentence and read as a STRIKETHROUGH at 432px feed width. qa.py
    reported zero fails and zero warns on that slide. The scorer found it by
    reading render_report.json's coordinates by hand, at the ship gate.

    WHY NOTHING HERE COULD SEE IT, which is the part that generalises:

      text_collisions()          compares TEXT line boxes against TEXT line
                                 boxes. A border is not text.
      the occlusion probe        compares line boxes against OPAQUE ELEMENT
                                 BOXES, and requires >= 4px in both dimensions
                                 plus a confirmed paint order. A 2px border is
                                 not an element box, and this one painted BELOW
                                 the footnote anyway.
      glyph_ink_contamination()  reads pixels and would have had a chance, but
                                 it fires on ink of the GLYPHS' OWN VALUE, and
                                 the rule (#2C3A34) and the footnote (#4A4436)
                                 are different values on the same sheet.
      busy_art_under_text()      measures edge DENSITY, and one clean straight
                                 rule through a line is the lowest-density
                                 structure there is.

    So the whole family -- a table rule, a CSS border, an <hr>, a divider div,
    an SVG line -- shipped invisibly. render.py now emits every such strip as
    geometry; this grades them.

    THE TEST, and every quantity in it is the type's own or an external standard.

      the glyph band   the em box, centred in the measured line box. That is
                       CSS's own content area for an inline box, so it is
                       derived from the node's font-size and its rendered line
                       box rather than typed. Half-leading falls outside it,
                       which is what separates a rule THROUGH a word from a
                       rule sitting in the gap under it.
      is it a rule     the strip's thickness must be under one em of the struck
                       type. At one em or more the thing is a plate, and the
                       occlusion probe owns plates. One em is the type's own
                       unit and scales with the slide.
      how much crossed a horizontal rule must cross at least one em of the line
                       (one character struck, not a corner clipped). A vertical
                       rule must sit at least one em inside BOTH ends of the
                       line box, because a column divider brushing the end of a
                       line box is ordinary and legitimate and a vertical rule
                       standing inside a run of words is not.
      can it be seen   WCAG 1.4.11's 3.0:1 non-text contrast floor, measured off
                       the PNG between the strip and the paper beside it. Under
                       that it is the hairline divider GATE_LESSONS 7 says is
                       allowed to be quiet, and this says nothing about it.

    PAINT ORDER IS NOT CONSULTED. The rule that shipped was painted UNDER the
    footnote and read as a strikethrough regardless, because a dark hairline
    across a word is a strikethrough whichever was rasterised last.

    Returns a list of (severity, message) with severity "fail" or "warn".
    """
    out = []
    if not rules or not nodes:
        return out
    tmask = _text_mask(nodes, img_arr.shape, scale)
    seen = set()
    for i, n in enumerate(nodes):
        if n.get("decorative"):
            continue
        em = float(n.get("font_px") or 0)
        if em <= 0:
            continue
        lines = n.get("lines") or [[n["x"], n["y"], n["w"], n["h"]]]
        for bx, by, bw, bh in lines:
            cy = by + bh / 2.0
            band0, band1 = max(by, cy - em / 2.0), min(by + bh, cy + em / 2.0)
            half = em * RULE_STRIKE_BAND / 2.0
            strike0, strike1 = max(by, cy - half), min(by + bh, cy + half)
            for r in rules:
                if i in (r.get("skip") or []):
                    continue
                rw, rh = float(r["w"]), float(r["h"])
                if min(rw, rh) <= 0 or min(rw, rh) >= em:
                    continue          # a plate, not a rule: the occlusion probe owns it
                rx, ry = float(r["x"]), float(r["y"])
                ix = min(bx + bw, rx + rw) - max(bx, rx)
                if ix <= 0 or min(by + bh, ry + rh) - max(by, ry) <= 0:
                    continue
                if rw >= rh:
                    if ix < em:
                        continue      # a corner clipped, not a character struck
                else:
                    cxr = rx + rw / 2.0
                    if cxr - bx < em or (bx + bw) - cxr < em:
                        continue      # a divider brushing the end of a line box
                in_band = min(band1, ry + rh) - max(band0, ry) > 0
                in_strike = min(strike1, ry + rh) - max(strike0, ry) > 0
                key = (i, round(rx), round(ry), round(rw), round(rh))
                if key in seen:
                    continue
                seen.add(key)
                # look for the paper up to one em away from the rule: further
                # than that is a different part of the picture, not its ground.
                vis = strip_visibility(img_arr, tmask, r, scale, em * scale)
                where = ("%s .%s at %g,%g %gx%g"
                         % (r.get("kind", "rule"), r.get("by", "?"), rx, ry, rw, rh))
                if vis is None:
                    if in_band:
                        out.append(("warn",
                                    "a drawn rule crosses the glyph band of '%s' (%s) and "
                                    "COULD NOT BE MEASURED: too little of the strip is clear "
                                    "of type to read its colour against the paper. Judge it "
                                    "by eye rather than reading this as a pass"
                                    % (n["text"][:40], where)))
                    continue
                ratio, _ink, _paper = vis
                if ratio < (RULE_STRIKE_RATIO if in_strike else RULE_VISIBLE_RATIO):
                    continue          # a quiet divider; WCAG 1.4.11 asks nothing of it
                if in_band and not (in_strike or ratio >= RULE_VISIBLE_RATIO):
                    continue          # inside the line box, clear of the letters, and quiet
                if in_band:
                    out.append((
                        "warn" if n.get("overlap_ok") else "fail",
                        "text struck by a drawn rule: '%s' has a %s running through its "
                        "glyph band (%.0fpx of the line, %.1f:1 against the paper beside "
                        "it). At feed width that reads as a strikethrough. Move the type, "
                        "move the rule, or knock the rule out behind the line"
                        % (n["text"][:40], where, ix, ratio)
                        + (" [marked data-overlap-ok]" if n.get("overlap_ok") else "")))
                else:
                    out.append((
                        "warn",
                        "a drawn rule sits inside the line box of '%s' (%s, %.1f:1) but "
                        "clear of the glyph band -- it is in the leading, so one reflow "
                        "of this copy puts it through the words"
                        % (n["text"][:40], where, ratio)))
    return out


def rules_missing_warning(rec):
    """A slide record with no `rules` key was written by a render.py that had no
    drawn-geometry probe, so the strikethrough gate CANNOT RUN on it.

    GATE_LESSONS 19: a skip and an unavailable check are not the same event and
    must not share a report line. This one says so out loud rather than letting
    a slide nothing looked at read as a slide nothing found.
    """
    if "rules" in rec:
        return None
    return ("drawn-rule geometry is missing from this slide's render record, so "
            "the strikethrough gate COULD NOT RUN -- re-render with the current "
            "render.py rather than reading this slide as clean")


TESTDATA = Path(__file__).resolve().parent / "testdata"


def self_test():
    """Replay the 2026-08-18 strikethrough against REAL CAPTURED RENDERS.

    Three of the four cases are chromium renders of the same slide, cropped and
    re-based, with the browser's own coordinates: the slide as it first
    rendered (the defect), the slide as it shipped (the repair), and the defect
    geometry with the loud rule swapped for the table's ordinary quiet hairline.
    GATE_LESSONS 15 is why they are renders and not hand-written dicts, and the
    third one is why they are three: it holds the geometry constant and changes
    only what a reader can see, so it is the case that would go red if the WCAG
    floor were quietly removed.
    """
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def load(name):
        d = json.loads((TESTDATA / f"strike_2026-08-18_{name}.json").read_text())
        arr = np.asarray(Image.open(TESTDATA / d["image"]).convert("RGB"))
        return d, arr

    def run(d, arr, nodes=None):
        return rule_strikes(nodes if nodes is not None else d["text_nodes"],
                            d["rules"], arr, d["scale"])

    # 1. THE DEFECT. qa.py reported this slide PASS, 0 fails, 0 warns.
    d, arr = load("defect")
    f = run(d, arr)
    fails = [m for s, m in f if s == "fail"]
    ok("the 2026-08-18 strikethrough is CAUGHT", len(fails) >= 1, str(f))
    ok("...and it names the struck text", any("Checked five days" in m for m in fails),
       str(fails))
    ok("...and it names the rule that struck it",
       any("border .k" in m or "border .v" in m for m in fails), str(fails))

    # 2. THE REPAIR. Same table, same 2px rule, moved clear of the footnote. A
    #    gate that cannot go green on the repair is measuring something else.
    dr, ar = load("repaired")
    ok("the shipped repair is clean", run(dr, ar) == [], str(run(dr, ar)))
    ok("...and the repair fixture still carries the rule that struck",
       any(r["h"] == 2 for r in dr["rules"]), str(dr["rules"]))

    # 3. THE DISCRIMINATION, AND IT MOVED ON 2026-08-26. Identical crossing, quiet
    #    1px hairline instead of the 2px near-black rule.
    #
    #    This case used to assert that a 1.6:1 hairline through the x-height is NOT
    #    a strike, on the reasoning that WCAG 1.4.11's 3.0:1 non-text floor asks
    #    nothing of it. THE RENDER REFUTED THAT. On 2026-08-26 frame 9 of
    #    carousel no. 7 shipped a separator at rgba(58,52,42,0.30) over #F2EEE4,
    #    measured 1.6:1, running through "with a state body." It is plainly visible
    #    in out/2026-08-25/render/slide-09.png at that revision and this file passed
    #    the frame with zero fails.
    #
    #    WCAG 1.4.11 asks whether a graphic is perceivable enough to CARRY
    #    INFORMATION. That is not the question a strikethrough poses. The eye judges
    #    an in-band rule against the LETTERFORMS it crosses, not against the paper
    #    beside it, so the floor for the strike case is now RULE_STRIKE_RATIO and the
    #    discrimination that does the real work is GEOMETRIC: a strike has to cross
    #    the middle RULE_STRIKE_BAND of the em, which is the x-height, rather than
    #    anywhere in a line box that is half again as tall as its type.
    #
    #    Reversing a self test's expectation is the move this repo names as a run
    #    editing its own checker so its copy passes. It is written out here with the
    #    render that forced it, so the next reader can judge the reversal rather than
    #    inherit it.
    dq, aq = load("quiet")
    q = run(dq, aq)
    ok("a quiet hairline through the x-height IS a strike, since 2026-08-26",
       any(s == "fail" for s, _ in q), str(q))
    ok("...and the quiet fixture really does cross the glyph band",
       any(abs(r["y"] - 86.5) < 0.6 for r in dq["rules"]), str(dq["rules"]))
    #    ...and the geometric half of the discrimination, which is what stops the
    #    lower floor firing on frame 3's seating channel at the letters' feet.
    below = [dict(n) for n in dq["text_nodes"]]
    for n in below:
        if n["text"].startswith("Checked"):
            n["lines"] = [[lx, ly - 11, lw, lh] for lx, ly, lw, lh in n["lines"]]
    qb = run(dq, aq, below)
    ok("...and the same quiet hairline at the letters' FEET is not a strike",
       not [m for sv, m in qb if sv == "fail"], str(qb))

    # 4. THE GLYPH BAND IS THE LINE, NOT THE LINE BOX. Take the defect's real
    #    pixels and slide the footnote's line box down 12px, which puts the same
    #    rule in the LEADING above the type instead of through it. The rule's
    #    own pixels are untouched, so the visibility measurement is unchanged
    #    and only the band test moves.
    shifted = [dict(n) for n in d["text_nodes"]]
    for n in shifted:
        if n["text"].startswith("Checked"):
            n["lines"] = [[lx, ly + 12, lw, lh] for lx, ly, lw, lh in n["lines"]]
    s = run(d, arr, shifted)
    ok("a rule in the leading is a WARN, not a FAIL",
       not [m for sv, m in s if sv == "fail"] and
       any("in the leading" in m for _, m in s), str(s))

    # 5. THE AUTHOR'S ESCAPE HATCH, which every other gate in this file honours.
    marked = [dict(n) for n in d["text_nodes"]]
    for n in marked:
        if n["text"].startswith("Checked"):
            n["overlap_ok"] = True
    m = run(d, arr, marked)
    ok("data-overlap-ok demotes the strike to a WARN",
       not [x for sv, x in m if sv == "fail"] and
       any("data-overlap-ok" in x for _, x in m), str(m))

    # 6. AN UNAVAILABLE CHECK IS NOT A SKIP (GATE_LESSONS 19).
    ok("a render record with no geometry reports that it could not run",
       rules_missing_warning({"file": "slide-01.html"}) is not None)
    ok("...and a record that has it does not",
       rules_missing_warning({"file": "slide-01.html", "rules": []}) is None)

    # 7. THE GATE MUST BE WIRED TO THE RUN, not just to this function.
    #    GATE_LESSONS 13: a self-test is not wiring, and a MENTION is not a
    #    reference. The first draft of this case grepped the source for a call
    #    to rule_strikes and stayed green when the call was neutered to
    #    `[] and rule_strikes(...)`, which is the same fault the port audit
    #    shipped. So it runs the real entry point end to end instead: a render
    #    dir built from the defect fixture, through argparse, the slide loop and
    #    the exit code a run reads.
    with tempfile.TemporaryDirectory() as td:
        rd = Path(td)
        Image.fromarray(arr).save(rd / "slide-09.png")
        h, w = arr.shape[:2]
        rec = {k: v for k, v in d.items() if k in ("text_nodes", "rules")}
        rec.update({"file": "slide-09.html", "png": "slide-09.png"})
        (rd / "render_report.json").write_text(json.dumps({
            "canvas": {"width": int(w / d["scale"]), "height": int(h / d["scale"]),
                       "scale": d["scale"], "px": [w, h]},
            "slides": [rec]}))
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                            "--render-dir", str(rd)],
                           capture_output=True, text=True)
        ok("the real entry point exits 1 on the defect", p.returncode == 1,
           p.stdout[-400:] + p.stderr[-200:])
        ok("...reporting it as a FAIL, not a warn",
           "FAIL: text struck by a drawn rule" in p.stdout, p.stdout[-600:])

    # ---- CANVAS EDGES CROSSING TEXT (2026-08-19) ---------------------------------------
    # rule_strikes is judged against three real captured renders above. What is new here is
    # the DETECTOR that finds strips the DOM never declared, so these cases test continuity:
    # a rule is one unbroken run, letterforms are short runs with gaps between them.
    def _band(with_rule, glyphs=True, thick=1):
        a = np.full((80, 400, 3), 235, dtype=np.uint8)      # paper
        if glyphs:                                          # short runs, like letters
            for x in range(10, 390, 17):
                a[34:46, x:x + 9] = 40
        if with_rule:                                       # one unbroken run
            a[39:39 + thick, 5:395] = 40
        return a

    node = [{"text": "a line of set type", "font_px": 20, "decorative": False,
             "lines": [[5, 15, 190, 20]], "x": 5, "y": 15, "w": 190, "h": 20}]

    got = canvas_rules(node, _band(True), 2)
    ok("a canvas edge running unbroken through the glyph band is DETECTED", len(got) >= 1, str(got))
    got = canvas_rules(node, _band(False), 2)
    ok("...and letterforms alone are NOT read as a rule", not got, str(got))
    # A PLATE IS NOT A RULE, and the drop happens in rule_strikes rather than here. Asserted
    # through the judge instead of the detector, because that is where the boundary lives: a
    # strip at or over one em is a plate and the occlusion probe owns it. Worth stating that
    # this detector is NOT reliable when a plate fills the glyph band, since the band's median
    # then IS the plate and "off paper" inverts. That case is the occlusion probe's by design.
    fat = [{"x": 5, "y": 15, "w": 190, "h": 20, "kind": "plate", "by": "test"}]
    ok("a strip one em thick or more is dropped as a plate, not reported as a rule",
       not rule_strikes(node, fat, _band(True), 2), str(rule_strikes(node, fat, _band(True), 2)))
    got = canvas_rules([dict(node[0], decorative=True)], _band(True), 2)
    ok("a decorative node is not judged", not got, str(got))

    # THE REAL FRAME, when its PNG is on disk. 2026-08-19 slide 5 ships faint register lines
    # from the paper sheet straight through the last line of a paragraph, and machine QA
    # reported zero fails and zero warns on that slide before this detector existed.
    _root = Path(__file__).resolve().parents[3]
    _s5 = _root / "out" / "2026-08-19" / "render" / "slide-05.png"
    _rp = _root / "out" / "2026-08-19" / "render" / "render_report.json"
    if _s5.exists() and _rp.exists():
        _rep = json.loads(_rp.read_text(encoding="utf-8"))
        _rec = next((s for s in _rep.get("slides", []) if "05" in str(s.get("file", ""))), None)
        if _rec:
            _arr = np.asarray(Image.open(_s5).convert("RGB"))
            _sc = _arr.shape[1] / 1080.0
            _found = canvas_rules(_rec.get("text_nodes", []), _arr, _sc)
            ok("the real slide 5 register lines are found on the shipped render",
               len(_found) >= 1, f"found {len(_found)}")

    # ---------------------------------------------------------------- STANDING FURNITURE
    #
    # The 2026-08-29 foot wrap, replayed against REAL COMMITTED RENDER REPORTS rather than a
    # hand-written fixture, for entry 16's reason: a fixture written beside a detector agrees
    # with it, and only a real artifact carries the shapes nobody thought to write down.
    #
    # A MISSING CORPUS IS A FAILURE HERE, NOT A SKIP. Entry 37.
    _decks = sorted((_root / "runs" / "carousel").glob("*/render_report.json"))
    ok("committed render reports are present to calibrate the furniture check against",
       len(_decks) >= 8, f"found {len(_decks)}")
    _clean, _items = 0, 0
    for _p in _decks:
        _rep = json.loads(_p.read_text(encoding="utf-8"))
        _br, _why = furniture_breaks(_rep)
        _tab, _ = standing_furniture(_rep)
        _items += len(_tab)
        if not _br and not _why:
            _clean += 1
        else:
            ok(f"{_p.parent.name}: standing furniture agrees across the deck", False,
               str(_br or _why)[:200])
    ok("every shipped deck's standing furniture agrees across its own frames",
       _clean == len(_decks), f"{_clean} of {len(_decks)}")
    ok("...and the comparison had furniture to compare rather than passing on an empty set",
       _items >= len(_decks), str(_items))

    # THE DEFECT, injected into a real report: the progress counter takes a second line on three
    # frames and one line on the rest, which is exactly what the flex row did on 2026-08-29.
    _base = json.loads(_decks[-1].read_text(encoding="utf-8"))
    _hit = 0
    for _rec in _base["slides"][:3]:
        for _nd in _rec.get("text_nodes") or []:
            if _COUNTER_TEXT.match(" ".join(str(_nd.get("text", "")).split())):
                _ln = _nd.get("lines") or [[_nd["x"], _nd["y"], _nd["w"], _nd["h"]]]
                _nd["lines"] = [list(_ln[0]), [80, _ln[0][1] + 31, 40, 31]]
                _hit += 1
    ok("the counter was found on the fixture, so the injection reached the code under test",
       _hit == 3, f"mutated {_hit} node(s)")
    _br, _ = furniture_breaks(_base)
    ok("a counter that wraps on three frames and not the rest is CAUGHT", len(_br) == 3, str(_br))
    ok("...and it names the frames that disagree",
       len({f for f, _ in _br}) == 3, str(sorted(f for f, _ in _br)))
    ok("...and the message says the row ran past its measure",
       bool(_br) and "ran past its measure" in _br[0][1], str(_br[:1]))

    # AGREEMENT IS AGREEMENT, in both directions. Two lines on EVERY frame is a deck whose
    # furniture is two lines, and this check has no opinion about that. Stated in the header as
    # the blind spot; asserted here so nobody later mistakes it for a bug and adds a threshold.
    _all = json.loads(_decks[-1].read_text(encoding="utf-8"))
    for _rec in _all["slides"]:
        for _nd in _rec.get("text_nodes") or []:
            if _COUNTER_TEXT.match(" ".join(str(_nd.get("text", "")).split())):
                _ln = _nd.get("lines") or [[_nd["x"], _nd["y"], _nd["w"], _nd["h"]]]
                _nd["lines"] = [list(_ln[0]), [80, _ln[0][1] + 31, 40, 31]]
    ok("furniture that is two lines on EVERY frame is agreement, which is the stated blind spot",
       furniture_breaks(_all)[0] == [], str(furniture_breaks(_all)[0]))

    # A report with no line boxes cannot answer, and that is not the same event as finding
    # nothing. It has to say so rather than print the colour of a clean run.
    _old = {"slides": [{"file": "slide-01.html", "text_nodes": [{"text": "TEXAS AI DOCKET"}]},
                       {"file": "slide-02.html", "text_nodes": [{"text": "TEXAS AI DOCKET"}]}]}
    ok("a report with no per-node line boxes reports that it could not compare",
       furniture_breaks(_old) == ([], "this render report predates per-node line boxes, "
                                      "so nothing was compared"), str(furniture_breaks(_old)))

    # The counter reads a different string on every frame and is one object. A comparison keyed
    # on the literal text would never see it twice and the check would cover nothing.
    ok("the progress counter is one piece of furniture across the deck",
       _furniture_key("01 / 09") == _furniture_key("07 / 09") == "NN / NN")
    ok("...and ordinary copy is keyed on itself",
       _furniture_key("  TEXAS  AI DOCKET ") == "TEXAS AI DOCKET")

    if failures:
        print(f"\nqa self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nqa self-test: all passed (3 real renders of slide-09.html, "
          "2026-08-18, replayed)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-dir")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--safe-margin", type=int, default=SAFE_MARGIN)
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if not args.render_dir:
        print("qa.py: pass --render-dir or --self-test", file=sys.stderr)
        sys.exit(2)

    rdir = Path(args.render_dir)
    report = json.loads((rdir / "render_report.json").read_text())
    scale = report["canvas"]["scale"]
    exp_w, exp_h = report["canvas"]["px"]
    design_w, design_h = report["canvas"]["width"], report["canvas"]["height"]

    out = {"slides": [], "fails": 0, "warns": 0}

    # STANDING FURNITURE, measured across the deck rather than within a frame. This is the one
    # check here whose subject is the deck, so it is computed once and attributed to the frames
    # that disagree with the rest. See standing_furniture() for the 2026-08-29 defect.
    fbreaks, fwhy = furniture_breaks(report)
    by_file = {}
    for f, msg in fbreaks:
        by_file.setdefault(f, []).append(msg)
    if fwhy:
        print(f"qa: standing furniture NOT compared: {fwhy}", file=sys.stderr)

    for rec in report["slides"]:
        res = {"file": rec["file"], "fails": [], "warns": []}
        res["fails"].extend(by_file.get(rec["file"], []))
        png = rdir / rec["png"]
        if not png.exists():
            res["fails"].append("png missing")
            out["slides"].append(res)
            continue
        im = Image.open(png).convert("RGB")
        if im.size != (exp_w, exp_h):
            res["fails"].append(f"size {im.size} != expected {(exp_w, exp_h)}")
        arr = np.asarray(im)
        if float(arr.std()) < 6.0:
            res["fails"].append(f"near-uniform image (std {arr.std():.1f}) — dead or empty render")

        # DETERMINISM (2026-08-01). render.py scans the slide SOURCE; this is
        # the judgement. Unseeded randomness is a FAIL because it makes the
        # slide unreproducible: a repair pass repaints the field, so the render
        # a pixel critic reviewed is not the render that ships, and the shipped
        # PNG cannot be rebuilt from the committed HTML. TX.rng(seed) is the
        # one-argument replacement. Clock reads are a WARN: usually a timing
        # log, occasionally an animation phase that does feed pixels.
        for nd in rec.get("nondeterminism", []):
            where = f"line {nd['line']}: {nd['snippet']}"
            if nd["tier"] == "hard":
                res["fails"].append(
                    f"unseeded randomness: {nd['api']} in this slide's inline "
                    f"script ({where}) -- the slide contract requires seeded "
                    f"noise (TX.rng(seed) / TX.reseed(seed), seed from the run "
                    f"date) so the same source reproduces the same pixels")
            else:
                res["warns"].append(
                    f"clock read in slide script: {nd['api']} ({where}) -- if it "
                    f"feeds the artwork the slide is not reproducible; pin it to "
                    f"a constant or a seeded value")

        # FRAME BALANCE / DEAD LOWER ZONE (2026-07-26). The series' longest-
        # running craft defect, and the first gate here that judges COMPOSITION
        # rather than legibility. See frame_balance() for why the measurement is
        # a distribution and not a density. Calibrated on all 162 shipped
        # full-size slides: the FAIL tier fires on 10% of them and every slide
        # it fires on is one the scorers named, or (2026-07-17 S09,
        # 2026-07-20 S03, both bottom-40%-empty) one they should have.
        fb = frame_balance(arr)
        if fb is not None:
            ratio, bands = fb
            # PERSIST THE MEASUREMENT, not only the sentence about it.
            #
            # These three numbers were computed here and then thrown away into a message
            # string. scripts/carousel/craft_floor.py reads a per-third band density to decide
            # whether a THIN frame is a deliberate quiet frame (warn) or a frame nobody drew
            # (fail), and it looked for exactly these keys and found nothing, on every run,
            # because nothing ever wrote them. Its WARN tier was unreachable dead code and
            # every thin frame was a hard fail on a test that never ran.
            #
            # Third time in this repo that a consumer read a key its producer does not write,
            # after gate_status and email_check both missed `weighted_score`. The shape is
            # always the same: two files agreeing about a name in one direction only.
            res["bands"] = [round(b, 4) for b in bands]
            res["band_ratio"] = round(ratio, 4)
            if ratio < FB_WARN:
                where = f"top {bands[0]:.0%} / mid {bands[1]:.0%} / bottom {bands[2]:.0%} of cells carrying craft"
                msg = (f"top-loaded composition: the bottom third carries {ratio:.0%} of "
                       f"this slide's own average craft density ({where}) -- the dead "
                       f"lower zone. Extend the anchor, run the annotation furniture "
                       f"down, or move the mass; do not answer it with a bigger quiet zone")
                if ratio < FB_FAIL and not rec.get("breather"):
                    res["fails"].append(msg)
                elif rec.get("breather"):
                    res["warns"].append(msg + " [data-breather]")
                else:
                    res["warns"].append(msg)

        # CANVAS HEALTH (2026-07-11, the rendered-3D gates). Two failure modes
        # the DOM/text gates cannot see, both from the GPU-bench research:
        # (1) DEAD CANVAS: a large visible canvas whose pixels are near-uniform
        #     = a WebGL context that failed/never painted (screenshots as flat
        #     ink) or an art draw that silently threw. FAIL: no slide ships a
        #     dead art layer. A canvas that COULD NOT be sampled (no
        #     preserveDrawingBuffer) on a slide whose full-frame std is healthy
        #     only WARNs (the whole-image gate above still backstops it).
        # (2) LOW-RES BACKING: the slide contract requires 2x backing
        #     (canvas.width = cssW*2); a big canvas below 1.5x ships visibly
        #     blurry in the PDF (the three.js setSize-order trap). FAIL >=1/4
        #     of the slide below 1.5x; WARN 1.5x-1.9x.
        for cvi in rec.get("canvases", []):
            if cvi.get("area_frac", 0) < 0.25:
                continue
            tag = f"canvas {cvi['w']}x{cvi['h']}@({cvi['x']},{cvi['y']})"
            br = cvi.get("backing_ratio", 2)
            if br < 1.5:
                res["fails"].append(
                    f"low-res canvas backing ({br}x < 1.5x) on {tag} — 2x contract; ships blurry")
            elif br < 1.9:
                res["warns"].append(
                    f"canvas backing {br}x < 2x on {tag} (contract is 2x)")
            if cvi.get("sample_ok"):
                if cvi.get("variance", -1) >= 0 and cvi["variance"] < 3.0:
                    res["fails"].append(
                        f"dead canvas (pixel variance {cvi['variance']}) on {tag} — "
                        "failed GL context or empty art layer")
            else:
                res["warns"].append(
                    f"unsampleable canvas on {tag} (GL without preserveDrawingBuffer?) — "
                    "verify visually; akthree sets preserveDrawingBuffer for the gate")

        # CANVAS RASTER TEXT (2026-07-19, WARN only). Text drawn via canvas
        # fillText/strokeText is a raster bitmap: invisible to render.py's DOM
        # walk, to copy_sync_check (unless the string is an authored copy.json
        # record), to the LinkedIn ranker, and to accessibility, and it pixelates
        # in the vector PDF. render.py's init-script hook captured every drawn
        # string; warn on the MEANINGFUL ones (>= 4 alphabetic chars, so axis
        # ticks / short unit labels / numbers do not trip it), pointing the
        # author to move real labels to DOM/SVG. Never a FAIL: txlabel-style
        # in-scene labels are legitimate, but the raster-text cost is worth a
        # visible note. (2026-07-19: S7 loop labels + S8 annotations were
        # cx.fillText and only caught by hand.)
        seen_ct = set()
        for ct in rec.get("canvas_text", []):
            s = (ct.get("text") or "").strip()
            if s in seen_ct:
                continue
            seen_ct.add(s)
            if sum(c.isalpha() for c in s) >= 4:
                res["warns"].append(
                    f"canvas raster text '{s[:40]}' drawn via {ct.get('fn', 'fillText')} "
                    "-- ships as a bitmap in the vector PDF (invisible to the LinkedIn "
                    "ranker, copy_sync, and accessibility); move meaningful labels to DOM/SVG")

        for e in rec.get("page_errors", []):
            res["fails"].append(f"page error: {e}")
        for e in rec.get("console_errors", []):
            res["warns"].append(f"console error: {e}")
        for f in rec.get("fonts_missing", []):
            sty = f.get("style", "normal")
            styd = "" if sty in ("normal", None) else f" {sty}"
            res["fails"].append(f"font not loaded: {f['family']} w{f['weight']}{styd}")
        if rec.get("body_overflow"):
            res["fails"].append("body overflow (page scrolls beyond canvas)")
        for wr in rec.get("overflow_warnings", []):
            level = res["warns"] if wr["kind"] == "tiny-text" else res["fails"]
            level.append(f"{wr['kind']}: '{wr['text'][:50]}' ({wr['detail']})")

        # DECLARED ENCODING DOES NOT READ (2026-07-29). Opt-in: a slide that
        # declares nothing is not judged here, so this can never block a deck
        # that has not adopted the contract.
        for enc in rec.get("encodings", []):
            verdict, detail = encoding_reads(arr, enc, design_w, design_h)
            if verdict == "fail":
                # THE DIRECTION CONTRACT (2026-08-08). Still not a judgment of
                # whether the encoding WORKS -- no threshold through those
                # numbers survived calibration and none has been added. This
                # fails only when the declaration cannot be checked at all, or
                # when the slide contradicts the direction it declared itself.
                res["fails"].append(f"encoding declaration is not evidence: {detail}")
            elif verdict == "warn":
                # Only an AUTHORING error warns: a declaration that does not
                # parse or names a region nobody can measure.
                res["warns"].append(f"encoding declaration unusable: {detail}")
            else:
                res.setdefault("encodings", []).append(detail)

        # DECLARED CONTACT SHADOW DOES NOT READ (2026-08-05). Opt-in like the
        # encoding contract, so a deck that declares nothing is not judged
        # here. When a slide DOES declare one, the measurement is a hard gate.
        for con in rec.get("contacts", []):
            verdict, detail = contact_reads(arr, con, design_w, design_h)
            if verdict == "fail":
                res["fails"].append("contact shadow does not read: " + detail)
            elif verdict == "warn":
                res["warns"].append("contact shadow: " + detail)
            else:
                res.setdefault("contacts", []).append(detail)

        # LEADER LANDS ON NOTHING (2026-08-07). Opt-in, and pure arithmetic on
        # two declared points, so it cannot false-positive on an undeclared
        # slide or on art it cannot understand. See LEADER_LAND_PX for why the
        # measurement is a declaration and not a pixel test.
        for ld in rec.get("leaders", []):
            verdict, detail = leader_lands(ld)
            if verdict == "fail":
                res["fails"].append("leader lands on nothing: " + detail)
            elif verdict == "warn":
                res["warns"].append("leader declaration unusable: " + detail)
            else:
                res.setdefault("leaders", []).append(detail)

        # SVG LABEL OFF ITS OWN PLATE (2026-07-29). render.py measures every
        # SVG <text> against the <rect> painted under it. A label that spills
        # past its knockout is not a style choice: the plate exists precisely
        # because the artwork behind it cannot carry type, so every pixel that
        # escapes lands on unreadable ground, and a chip's border rule ends up
        # drawn through a letterform. 2px of tolerance absorbs subpixel bbox
        # rounding; anything past that is the arithmetic being wrong.
        for sp in rec.get("svg_plates", []):
            cov = sp.get("covered_px")
            dom = sp.get("dom_cover_frac") or 0
            if (cov and cov[0] > 4 and cov[1] > 2) or dom > 0.15:
                what = (f"a {cov[0]}x{cov[1]}px opaque rect" if cov
                        else f"an opaque DOM block over {dom:.0%} of its width")
                msg = (f"svg label painted over: '{sp['text'][:40]}' has "
                       f"{what} drawn on top of it")
                if sp.get("overlap_ok"):
                    res["warns"].append(msg + " [marked data-overlap-ok]")
                elif sp.get("decorative"):
                    res["warns"].append(msg + " [decorative]")
                else:
                    res["fails"].append(msg)
            if sp["overrun_px"] <= 2:
                continue
            o = sp["over"]
            sides = ", ".join(f"{k} {v}px" for k, v in o.items() if v > 2)
            msg = (f"svg label off its plate: '{sp['text'][:40]}' spills {sides}"
                   f" (worst {sp['overrun_px']}px)")
            if sp.get("overlap_ok"):
                res["warns"].append(msg + " [marked data-overlap-ok]")
            elif sp.get("decorative"):
                res["warns"].append(msg + " [decorative]")
            else:
                res["fails"].append(msg)

        # TEXT STRUCK BY A DRAWN RULE (2026-08-18). See rule_strikes() for the
        # defect and for why every other gate here was blind to it. The absence
        # of the key is NOT a skip: a render_report written by an older
        # render.py carries no geometry, so the check cannot run, and
        # GATE_LESSONS 19 is the whole reason that says so out loud instead of
        # passing quietly.
        _missing = rules_missing_warning(rec)
        if _missing:
            res["warns"].append(_missing)
        else:
            # DECLARED rules plus the ones recovered from pixels. A canvas edge is not a
            # DOM element, and one ran through a paragraph twice on 2026-08-19 slide 5 while
            # this gate, built for exactly that collision, saw nothing.
            _nodes = rec.get("text_nodes", [])
            _rules = list(rec["rules"] or []) + canvas_rules(_nodes, arr, scale)
            for sev, msg in rule_strikes(_nodes, _rules,
                                         arr, scale):
                (res["fails"] if sev == "fail" else res["warns"]).append(msg)

        # text-on-text overprint (the class of defect no other gate sees).
        # data-overlap-ok marks DELIBERATE layering (e.g., a chip on an
        # opaque plate crossing a display line box): demoted to WARN so the
        # pixel critics still judge it.
        tnodes = rec.get("text_nodes", [])
        for i, j, ratio in text_collisions(tnodes):
            a, b = tnodes[i], tnodes[j]
            msg = (f"text collision ({ratio:.0%} overprint): "
                   f"'{a['text'][:36]}' x '{b['text'][:36]}' "
                   f"near {max(a['x'], b['x'])},{max(a['y'], b['y'])}")
            if a.get("overlap_ok") or b.get("overlap_ok"):
                res["warns"].append(msg + " [marked data-overlap-ok]")
            elif a.get("decorative") or b.get("decorative"):
                res["warns"].append(msg + " [decorative involved]")
            else:
                res["fails"].append(msg)

        for node in rec.get("text_nodes", []):
            if node.get("decorative"):
                continue
            primary = node["font_px"] >= 30
            if (node["x"] < args.safe_margin - 8 or node["y"] < args.safe_margin - 8 or
                    node["x"] + node["w"] > design_w - args.safe_margin + 8 or
                    node["y"] + node["h"] > design_h - args.safe_margin + 8):
                res["warns"].append(
                    f"outside safe zone: '{node['text'][:40]}' at {node['x']},{node['y']} "
                    f"{node['w']}x{node['h']} (margin {args.safe_margin}px)")
            # TEXT UNDER AN OPAQUE PLATE (2026-07-26). render.py's occlusion
            # probe reports the largest patch of a line box that a foreign
            # OPAQUE element provably paints over (paint order confirmed with
            # elementsFromPoint). text_collisions() cannot see this: it
            # compares glyph line boxes, and a padded plate's BACKGROUND is
            # not a line box, so the 2026-07-26 S06 DEAD plate covering the
            # bottom third of a subtitle scored 0.21 against the 0.30 overlap
            # ratio and shipped through two scoring cycles of PASS. Covered
            # type is never a style choice; data-overlap-ok demotes it to WARN
            # so a deliberate layering stays the author's call.
            occ = node.get("occluded")
            if occ:
                ow, oh = occ.get("w", 0), occ.get("h", 0)
                if ow >= OCC_FAIL_W and oh >= OCC_FAIL_H:
                    msg = (f"text under an opaque plate: '{node['text'][:40]}' has a "
                           f"{ow}x{oh}px patch ({occ.get('frac', 0):.0%} of the line box) "
                           f"painted over by .{occ.get('by', '?')}"
                           + (f" '{occ['by_text'][:24]}'" if occ.get("by_text") else "")
                           + " -- move the plate, move the type, or knock the plate out")
                    if node.get("overlap_ok"):
                        res["warns"].append(msg + " [marked data-overlap-ok]")
                    else:
                        res["fails"].append(msg)
                elif ow >= OCC_WARN_W and oh >= OCC_WARN_H:
                    res["warns"].append(
                        f"opaque plate grazing text: '{node['text'][:40]}' has a "
                        f"{ow}x{oh}px patch covered by .{occ.get('by', '?')} -- "
                        f"pixel critic verify no glyph is cut")

            ratio = contrast_estimate(arr, node, scale)
            if ratio is not None:
                if primary and ratio < 2.0:
                    res["fails"].append(f"contrast ~{ratio:.1f} on '{node['text'][:40]}' (est.)")
                elif ratio < 3.5:
                    res["warns"].append(f"low contrast ~{ratio:.1f} on '{node['text'][:40]}' (est.)")
            # WORST-POINT contrast (2026-07-31). The line above averages the
            # background over the whole box, which passes a line whose lit end is
            # unreadable. This measures the rubric's actual rule.
            wc = contrast_worst_cell(arr, node, scale)
            if wc is not None and (ratio is None or wc < ratio - 0.15):
                if primary and wc < WORST_FAIL:
                    res["fails"].append(
                        f"contrast {wc:.1f} at WORST POINT on '{node['text'][:40]}' "
                        f"(box mean reads {ratio:.1f}) -- the ground under this line "
                        f"is graded; give it a reserve or move it")
                elif wc < WORST_WARN:
                    res["warns"].append(
                        f"worst-point contrast {wc:.1f} on '{node['text'][:40]}' "
                        f"(box mean {ratio:.1f}) -- below the rubric's 4.5 line "
                        f"somewhere along the run of the text")
            # canvas/bitmap-under-text tripwire (WARN only): the DOM collision
            # gate cannot see canvas ink, so busy art crossing a text line box
            # is otherwise invisible to the machine (2026-07-10 S3/S4 arcs).
            # 2026-07-25: no longer restricted to primary (>=30px) text. The
            # art-band mono labels that shipped crossed by canvas geometry were
            # 24px, so the size filter meant the only gate that could have seen
            # them never even sampled their boxes.
            busy = busy_art_under_text(arr, node, scale)
            if busy is not None and busy >= BUSY_WARN:
                res["warns"].append(
                    f"busy art under text (bg edge density {busy:.2f}) beneath "
                    f"'{node['text'][:40]}' -- canvas/bitmap may be crossing a "
                    f"text line box; pixel critic verify legibility")

            # LABEL CROSSED BY ART (2026-07-25). The FAIL tier the run of
            # 2026-07-25 needed: foreign ink of the glyphs' own value touching
            # the letterforms across the label = a rule/outline/groove edge
            # struck through the text, whatever layer drew it. A knockout plate
            # or a halo leaves the ring clean, so protected art-band type never
            # trips. data-decorative text is out of scope (skipped above) and
            # data-overlap-ok demotes the FAIL to a WARN, so a deliberate
            # layering stays the author's call.
            gi = glyph_ink_contamination(arr, node, scale)
            if gi is not None:
                gfrac, gext = gi
                if gfrac >= GLYPH_FAIL and gext >= GLYPH_FAIL_EXTENT:
                    msg = (f"label crossed by art ({gfrac:.0%} of the ring around "
                           f"'{node['text'][:40]}' is ink of the glyphs' own value, "
                           f"spanning {gext:.0%} of the label) -- a rule, outline or "
                           f"edge is running through the letterforms; put the label on "
                           f"a knockout plate, halo it, or move the geometry")
                    if node.get("overlap_ok"):
                        res["warns"].append(msg + " [marked data-overlap-ok]")
                    else:
                        res["fails"].append(msg)
                elif gfrac >= GLYPH_WARN:
                    res["warns"].append(
                        f"art touching glyphs ({gfrac:.0%} of the ring around "
                        f"'{node['text'][:40]}', spanning {gext:.0%}) -- pixel critic "
                        f"verify the label is not crossed")

        out["fails"] += len(res["fails"])
        out["warns"] += len(res["warns"])
        out["slides"].append(res)

    out["verdict"] = "FAIL" if out["fails"] else ("WARN" if out["warns"] else "PASS")
    (rdir / "machine_qa.json").write_text(json.dumps(out, indent=2))
    for s in out["slides"]:
        flag = "FAIL" if s["fails"] else ("warn" if s["warns"] else "ok  ")
        print(f"[{flag}] {s['file']}  fails={len(s['fails'])} warns={len(s['warns'])}")
        for f in s["fails"]:
            print(f"    FAIL: {f}")
        for w in s["warns"][:6]:
            print(f"    warn: {w}")
    print(f"verdict: {out['verdict']}  (report -> {rdir / 'machine_qa.json'})")
    sys.exit(1 if out["fails"] else 0)


if __name__ == "__main__":
    main()
