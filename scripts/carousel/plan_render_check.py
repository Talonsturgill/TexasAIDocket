#!/usr/bin/env python3
"""plan_render_check.py — the plan has to describe the frame that shipped.

WHY THIS EXISTS. Three runs, roughly fifteen incidents, one mechanism.

`dossier_check.py` proves a plan EXISTS and is well formed. It says so in its own docstring:
it validates FORMAT, never CORRESPONDENCE. A pixel critic then grades each frame against that
plan. So a plan that was never executed, or that went stale after a rewrite, passes every
review that comes after it, and the only reader who ever notices is a scorer at the ship gate
with no budget left to rebuild a slide.

WHAT SHIPPED THROUGH THAT HOLE

  2026-08-16  slide 2   the declared palette was never drawn. The state fill was not the oak
                        the plan named, so at feed size the silhouette was a stain.
  2026-08-16  slide 8   the declared focal, a ground line, was an unstroked colour change, and
                        its lit cut face and depth scale were never drawn at all.
  2026-08-16  s4 and s6 two acceptance items were satisfiable by rendering NOTHING.
  2026-08-18  slide 5   all five acceptance items passed while the frame read as a Gantt chart
                        that contradicted its own caption.
  2026-08-18  slide 9   printed a word its own first acceptance item forbids.
  2026-08-19  slide 5   THE WORST ONE. The dossier says the words that differ between the two
                        wordings are marked in pecos. Five scoring passes shipped uniform ink,
                        on the frame the whole deck turns on.
  2026-08-19  slide 3   the dossier demanded at least two empty swatches. The frame shipped
                        three NAMED categories, and the categories were fabricated.
  2026-08-19  slide 2   the dossier states the rate holds at 46 pixels per day, measured. Both
                        bars shipped 9px short, encoding 3.80 and 15.80 days.
  2026-08-19  slide 7   the dossier's hook and dek never shipped in any form.

THE FIFTH KIND, ADDED 2026-08-21, AND THE DEFECT IS THE WHOLE ARGUMENT FOR IT

`build_slides.py` refused that run's build. `_footer_fit` did its job exactly, naming a slide 9
byline 72px too wide for its frame, and it printed that to a stream the caller had suppressed
with `>/dev/null 2>&1` and never read the exit code of. The PREVIOUS build's HTML was still in
`out/<date>/slides/`, so the renderer rendered it, every gate in the suite passed on it, and
three scoring judges graded a deck that had never been built. Two repairs the run believed it
had shipped existed only in `storyboard.md`.

This file passed too, because none of the four kinds above reads the words. It compared
palettes and acceptance items on a frame whose display copy was a day stale.

  DECLARED    every string the dossier's `type:` block declares must be on the frame. `hook`
              and `dek` FAIL, because those are the deck's assertions and the reader's first
              two lines. Everything else the block declares WARNS, because that is furniture
              and a byline, where the difference is usually one character of punctuation that
              was repaired on the frame and not back in the plan.

Replayed across every deck this project has shipped it is silent on 2026-08-20 and 2026-08-21,
and it names real drift on two older ones: 2026-08-19 slide 3 planned "No provider was to be
told by the 7th" and shipped "No service provider was to be told by the 7th", and slide 6
planned "the sector's membership body" and shipped "the Data Center Coalition".

WHAT THIS CHECKS, AND WHAT IT DELIBERATELY DOES NOT

A machine cannot read a frame and say whether it is good. It CAN read a plan, pull out the
assertions that are about something countable, and go and look. Four kinds, chosen because
they are the four that actually broke:

  PALETTE     `art.palette` names colour tokens in prose. The storyboard defines those tokens
              as hex once. Every token a slide's palette NAMES must appear in that slide's
              rendered source. This is the 2026-08-16 slide 2 and 2026-08-19 slide 5 defect,
              and it is the cheapest true statement in the whole dossier to verify.

  REQUIRED    an acceptance item that says a frame READS or CARRIES a quoted string. The
              string has to be in the rendered text.

  FORBIDDEN   an acceptance item that says a quoted string appears NOWHERE. It has to be
              absent from the rendered text.

  COVERAGE    a slide whose entire acceptance list contains nothing checkable. This is the
              2026-08-16 and 2026-08-18 defect in its general form: a list of items that no
              render could ever fail is not a test, it is a description. This WARNS rather
              than fails, because plenty of true acceptance items are genuinely about
              judgement and should stay prose.

THE HONEST LIMIT, stated because a gate that oversells itself is worse than no gate. This
proves a declared colour was used SOMEWHERE on the frame, not that it was used on the right
element. Slide 5's pecos could satisfy this by tinting one hairline. It closes the distance
between "the plan said pecos and the frame has no pecos in it at all", which is what actually
shipped five times, and it does not close the distance to "marked correctly".

THE HONEST LIMIT ON `DECLARED`, which is a different one and is worth its own paragraph. It can
only compare a string the PLAN declares. The 2026-08-21 defect had two halves and this catches
one of them: slide 4's dek is declared under `type:` and slide 9's source line is not declared
anywhere, so a source line that names the wrong body is still invisible here. The coverage
count is printed on success for that reason, and a deck whose dossiers declare no display
string at all FAILS rather than reporting clean, because a comparison that compared nothing is
the shape `sources_block` shipped for a whole run behind an exit code of 0.

    plan_render_check.py --date 2026-08-19
    plan_render_check.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# A `name #RRGGBB` pair anywhere in the storyboard. One definition, read never typed.
#
# THE 2026-08-28 DEFECT, AND IT IS THIS FILE'S OWN SHAPE OF GATE_LESSONS 35. The name pattern
# read `[a-z][a-z ]*?`, which allows lower case letters and spaces and nothing else. Every
# palette token this project has ever declared with an underscore was therefore unmatchable:
# `sky_predawn`, `rim_light`, `caliche_cap`, `satin_spar`, `ledge_shadow`. The declared-colour
# check below reported "the storyboard defines no `name #HEX` palette" and did not run, all run,
# on a nine frame deck whose plan named a colour per frame.
#
# The underscore was only half of it, and the half that would have left the gate asleep. Measured
# across all ten shipped storyboards, EIGHT declare their palette as a markdown table,
# `| \x60token\x60 | \x60#HEX\x60 | source |`, which carries no `name #HEX` pair in one backtick
# span at all. Two decks carry the inline form. One carries indented plain pairs, written by a
# run that had noticed the gate saying nothing and tried to feed it. Fixing only the character
# class would have taken the parser from zero decks to two.
#
# So the rule against writing a checker from your idea of the rendered form applies to a plan as
# much as to a page: get the form from the artifact. Three shapes, each measured on real
# storyboards, and the two loose ones are read ONLY inside a section whose heading names the
# palette, because a hex quoted in body prose ("525.5 is set in `#B4903F`") would otherwise
# invent a palette token called `in`.
PALETTE_DEF = re.compile(r"`([a-z][a-z_ ]*?) (#[0-9A-Fa-f]{6})`")

# `| `token` | `#HEX` | ...`. The token cell and the FIRST hex cell after it, and no further,
# because 2026-08-27's palette table carries a second hex inside one row's prose cell
# ("Declared `#D7677E` until round four") and taking the last one invents a token named
# `declared`.
PALETTE_ROW = re.compile(
    r"^\s*\|\s*`?([A-Za-z][A-Za-z0-9_ ]*?)`?\s*\|\s*`?(#[0-9A-Fa-f]{6})`?\s*[|\s]", re.M)

# An indented or bare `token #HEX` on a line of its own, which is what the 2026-08-28 storyboard
# wrote under the heading "Declared as plain pairs so the colour check can read them".
PALETTE_PLAIN = re.compile(r"^[ \t]*([A-Za-z][A-Za-z0-9_]*)[ \t]+(#[0-9A-Fa-f]{6})[ \t]*$", re.M)

# THE FIFTH SHAPE: A MEASURED COLUMN TABLE, and it cost the whole palette check on 2026-09-16.
#
# That deck measured its palette against the last eight decks before choosing it, and wrote the
# arithmetic into the table beside each colour:
#
#     bond       #BBC0C6  L* 76   the copy stock and the deck's most common value   dE 10.59
#     bond       L* 76   #BBC0C6   the copy stock and the deck's most common value  dE 10.59
#
# Both orders shipped in one run, because the columns were reordered mid run. `PALETTE_PLAIN`
# anchors the hex at the end of the line, so neither form matched, `palette_map` read ZERO tokens,
# and the declared-colour check did not run at all on a nine frame deck whose plan names colours
# per frame. This file's own comment above records the same fault in 2026-08-28's words and in
# 2026-08-30's, which makes today the third time the parser met a form nobody had shown it.
#
# So the column layout is read rather than the column ORDER: an indented row, a single word token,
# an optional stated `L* <n>` on either side of the hex, a BARE hex, and any description after it.
# Indentation and a bare hex are what keep it off running prose: the paragraph under that table
# reads "Flag red `#BF0A30` is UNSPENT", which is unindented and backticked, and reading it would
# invent a token called `red` for a colour the deck says it did not spend.
PALETTE_COLUMNS = re.compile(
    r"^[ \t]+([A-Za-z][A-Za-z0-9_]*)[ \t]+(?:L\*[ \t]*-?\d+(?:\.\d+)?[ \t]+)?"
    r"(#[0-9A-Fa-f]{6})(?:[ \t]+\S.*)?$", re.M)

# `field #333D45 the ground, far #768C9C, mid #B0C8D6` inside a dossier's `palette: >` prose.
# Scoped to that field alone, so a hex quoted anywhere else in a dossier cannot become a token.
PALETTE_PROSE = re.compile(r"\b([a-z][a-z0-9_]*)[ \t]+(#[0-9A-Fa-f]{6})")

# A markdown heading, used to find the palette section the two loose shapes are scoped to.
HEADING = re.compile(r"^(#{1,6})[ \t]+(.*)$", re.M)

# A QUOTED STRING, AND AN APOSTROPHE IS NOT ONE. 2026-08-26.
#
# The first draft wrote the delimiters as `["\']...["\']`, which accepts a `"` opened and a `'`
# closed, and lets a POSSESSIVE open a quote. Slide 7's acceptance line reading "all four title
# cells carry their applicant\'s name, because the county\'s own matter titles hold four" was
# therefore read as requiring the frame to print the string `s name, because the county`, and the
# gate failed a correct frame over a plan sentence that quotes nothing at all.
#
# Two rules fix the class. The marks must MATCH, via a backreference. And a mark glued to a word
# character on the inside is punctuation in a word, never a delimiter: `\w'` cannot open and `'\w`
# cannot close. Double quotes are unaffected, which is what every real quoted acceptance item
# here uses.
_Q = r"(?<!\w)([\"'])([^\"']{3,60})\1(?!\w)"

# An acceptance item asserting a string is present. Group 2 is what must be rendered.
REQUIRED_STR = re.compile(
    r"\b(?:read(?:s|ing)?|carr(?:y|ies|ying)|say(?:s|ing)?|print(?:s|ing)?|set)\b[^\"']{0,40}"
    + _Q, re.I)

# An acceptance item asserting a string is absent. TWO orders, because acceptance lines are
# written both ways and the first draft of this file only matched one of them:
#   "no legend label names 'base load'"        negation BEFORE the quote
#   "the phrase 'flag red' appears nowhere"    negation AFTER it
FORBIDDEN_BEFORE = re.compile(
    r"\b(?:no|never|nowhere|not)\b[^\"']{0,60}" + _Q, re.I)
FORBIDDEN_AFTER = re.compile(
    _Q + r"[^\"']{0,40}"
    r"\b(?:appears? nowhere|appears? on no|is absent|does not appear|never appears|"
    r"appears nowhere)\b", re.I)


def forbidden_needles(item: str) -> list:
    seen = []
    for rx in (FORBIDDEN_BEFORE, FORBIDDEN_AFTER):
        for m in rx.finditer(item):
            v = m.group(2).strip()
            if len(v.split()) >= 2 and v not in seen:
                seen.append(v)
    return seen

# Words that mean the item is about judgement rather than about a countable thing.
PROSE_ONLY = ("read as", "reads as", "feel", "judged", "at thumb", "by eye", "looks")


# ---------------------------------------------------------------------------------------------
# THE FIFTH KIND: A FRAME'S OWN DECLARED MEDIAN L* BAND (2026-09-16, carousel no. 26)
#
# THE DEFECT. That run's storyboard wrote a median L* band into every one of its nine dossiers'
# acceptance lists, at the size a reader receives: `the frame's median L* at 432px is between 36
# and 52`. The run then MEASURED all nine medians, wrote them to `measured_arc.json` beside the
# storyboard, and never compared the two. FIVE OF NINE frames were outside their own declared
# band, three of them by more than twenty points, while the storyboard still asserted every frame
# was inside its range. The first panel came back under the ship bar on all three lenses and the
# craft judge's one sentence fix was, in its own words, to make the pixel phase compare
# `measured_arc.json` against each dossier's own band and re-render on any frame that misses.
#
# Two gates were in the room and neither could see it, each correctly.
#
#   this file          counted every one of those nine items as PROSE. Its report line for that
#                      deck read `0 of 55 acceptance items carry a machine-checkable assertion`,
#                      which was true of what it could check and false of what the plan wrote:
#                      nine of the fifty five were arithmetic with a number on both sides.
#   panel_ready        compares the DECK MEDIAN against the deck's planned arc, deliberately, and
#                      its own comment says why a per frame rule keyed on a point target would
#                      fire on every deck. This deck's median was 45.9 against a plan of 44, so
#                      it passed while five frames sat outside their own bands.
#
# WHY A BAND IS DIFFERENT FROM A POINT TARGET, and it is the whole argument for checking per
# frame here while `panel_ready` keeps checking per deck. `arc_verdict`'s tolerance is one Munsell
# step, a number that file had to justify from outside this project because a plan states a target
# and not how far off is acceptable. A BAND IS THE PLAN'S OWN TOLERANCE. `between 36 and 52` is
# the dossier saying, before anything was drawn, which measurements it would accept. So this
# types in no threshold at all: it fails a frame only against the range that frame's own author
# wrote, which is the same contract as every other acceptance item in this file.
#
# THE SIZE IS READ FROM THE ITEM AND NEVER ASSUMED. A median moves with the resampling, so a band
# with no stated measurement size is a band that cannot be settled, and this reports that as
# UNCHECKABLE rather than picking a size and reporting a verdict. Two forms are read, both taken
# off real shipped storyboards rather than invented here:
#
#   `at 432px`                 2026-09-10 and 2026-09-16. Height follows the frame's own aspect.
#   `on the 270 by 338 grid`   2026-09-08. Both numbers are the plan's, so both are used.
#
# THE SUBJECT MUST BE THE FRAME. Acceptance items legitimately state the median of a REGION, and
# five shipped decks do: `the punch column's median L* is at least 10 below the rail face median`,
# `all four castors carry a contact shadow whose median L* differs from the floor beside it by 4
# or more`. Reading one of those as the frame's band would invent a number the plan does not
# contain, which is GATE_LESSONS 27 and is the most convincing shape a false failure takes. This
# is `panel_ready.FRAME_MEDIAN`'s rule, arrived at there for the same reason, so the qualifier is
# required and nothing else is read.
FRAME_MEDIAN_SUBJECT = re.compile(r"\b(?:the|this)\s+frame(?:'s)?\s+median\s+L\*", re.I)

# Where the assertion about the frame's own median stops and the sentence goes on to say
# something else. Every one of these was taken off a real acceptance item: `is 45 or higher,
# which is at least 18 above the deck median` (2026-09-10), `is above 80 and it is the only frame
# in the deck above 60` (2026-09-04), `measures 50.5 in measurements.json. NOT MET` (2026-09-11).
# `and` alone is NOT a break, because `between 36 and 52` is one assertion.
_CLAUSE_END = re.compile(r",|\bwhich\b|\bbecause\b|\band it\b|\bso the\b|\.\s", re.I)

_AT_PX = re.compile(r"\bat\s+(\d{2,4})\s*px\b", re.I)
_ON_GRID = re.compile(r"\bon the\s+(\d{2,4})\s+by\s+(\d{2,4})\s+grid\b", re.I)

_N = r"(\d+(?:\.\d+)?)"
_BETWEEN = re.compile(rf"\bbetween\s+{_N}\s+and\s+{_N}", re.I)
_PLUS_MINUS = re.compile(rf"{_N}\s*(?:plus or minus|\+/-)\s*{_N}", re.I)
# Inclusive and strict are kept apart rather than folded together. `60 or higher` admits exactly
# 60 and `above 60` does not, and a gate that quietly widened the second into the first would be
# loosening a bound its author chose, on the frame where it matters least and the day it matters
# most.
_LO_INCL = re.compile(rf"(?:\bat least\s+{_N}|{_N}\s+or (?:higher|more|greater))", re.I)
_LO_STRICT = re.compile(rf"\b(?:above|over|higher than|greater than)\s+{_N}", re.I)
_HI_INCL = re.compile(rf"(?:\bat most\s+{_N}|{_N}\s+or (?:lower|less|darker))", re.I)
_HI_STRICT = re.compile(rf"\b(?:below|under|lower than|darker than)\s+{_N}", re.I)


def band_clause(item: str) -> str | None:
    """The stretch of an acceptance item that is about the FRAME's own median, or None."""
    m = FRAME_MEDIAN_SUBJECT.search(item)
    if not m:
        return None
    tail = item[m.end():]
    cut = _CLAUSE_END.search(tail)
    return tail[:cut.start()] if cut else tail


def parse_band(item: str) -> dict | None:
    """`{lo, hi, lo_strict, hi_strict, size, clause}` for an item that states a frame band.

    `None` when the item is not about the frame's own median at all. A dict with `size: None`
    when the band reads but the plan never said at what size to measure it, and a dict with
    `lo` and `hi` both None when the subject is there and no band could be read. Those two are
    the THIRD STATE, and they are reported rather than folded into the prose count, because an
    unread declaration and an item that declares nothing print the same line otherwise. That is
    the defect `panel_ready.unreadable_plan` exists for, one gate over.
    """
    clause = band_clause(item)
    if clause is None:
        return None
    size = None
    grid = _ON_GRID.search(clause)
    px = _AT_PX.search(clause)
    if grid:
        size = (int(grid.group(1)), int(grid.group(2)))
        clause = clause[:grid.start()] + " " + clause[grid.end():]
    elif px:
        size = (int(px.group(1)), None)
        clause = clause[:px.start()] + " " + clause[px.end():]
    out = {"lo": None, "hi": None, "lo_strict": False, "hi_strict": False,
           "size": size, "clause": clause.strip()}
    if (m := _BETWEEN.search(clause)):
        out["lo"], out["hi"] = float(m.group(1)), float(m.group(2))
        return out
    if (m := _PLUS_MINUS.search(clause)):
        mid, tol = float(m.group(1)), float(m.group(2))
        out["lo"], out["hi"] = mid - tol, mid + tol
        return out
    if (m := _LO_INCL.search(clause)):
        out["lo"] = float(m.group(1) or m.group(2))
    elif (m := _LO_STRICT.search(clause)):
        out["lo"], out["lo_strict"] = float(m.group(1)), True
    if (m := _HI_INCL.search(clause)):
        out["hi"] = float(m.group(1) or m.group(2))
    elif (m := _HI_STRICT.search(clause)):
        out["hi"], out["hi_strict"] = float(m.group(1)), True
    return out


def band_text(b: dict) -> str:
    lo = "-" if b["lo"] is None else f"{'over ' if b['lo_strict'] else ''}{b['lo']:g}"
    hi = "-" if b["hi"] is None else f"{'under ' if b['hi_strict'] else ''}{b['hi']:g}"
    return f"{lo} to {hi}"


def in_band(measured: float, b: dict) -> bool:
    if b["lo"] is not None and (measured <= b["lo"] if b["lo_strict"] else measured < b["lo"]):
        return False
    if b["hi"] is not None and (measured >= b["hi"] if b["hi_strict"] else measured > b["hi"]):
        return False
    return True


def median_lstar(path: Path, size: tuple) -> float:
    """The median CIE L* of one frame, resampled to `size` first.

    ONE IMPLEMENTATION OF THIS MEASUREMENT, and `panel_ready.measured_arc` calls this rather than
    keeping a second. Two tokenisers for one numeral is written up in GATE_LESSONS 34 as the
    defect under the defect, and a median computed two ways would be the same fault on the figure
    this project's whole value arc is argued in.

    `size` is `(width, height)`, or `(width, None)` to take the height from the frame's own
    aspect, which is what `at 432px` means on a 1080 by 1350 canvas.
    """
    from PIL import Image
    import numpy as np
    im = Image.open(path).convert("RGB")
    w, h = size
    if h is None:
        h = round(w * im.size[1] / im.size[0])
    a = np.asarray(im.resize((w, h), Image.LANCZOS), dtype=float) / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    Y = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    L = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
    return round(float(np.median(L)), 1)


# WHERE A FRAME'S PIXELS LIVE, in the three places this repo actually puts them. A run in flight
# writes `out/<date>/render/slide-0N.png`; a shipped run under `runs/carousel/<date>/` carries
# `slide-0N.webp` at the top of the directory, and 2026-09-03 carries one PNG among its webps.
# The thumbnails are deliberately NOT on this list: they are already resampled, and measuring a
# band at 432 px off a thumbnail would be measuring somebody else's resize.
def frame_image(slides_dir: Path, n: int) -> Path | None:
    root = slides_dir.parent
    for p in (root / "render" / f"slide-{n:02d}.png",
              root / f"slide-{n:02d}.png",
              root / f"slide-{n:02d}.webp"):
        if p.exists():
            return p
    return None


# THE LIBRARY A DOSSIER NAMES MUST BE IN THE SLIDE. 2026-08-26.
#
# Round 10's craft judge read slide 1's dossier, which declared "Zdog scene, rounded extrusion
# with a real depth axis" and argued for it at length on the ground that "Zdog has never shipped
# on this product", then opened slide-01.html and found it loads noise.js and nothing else and
# builds the whole case out of axis-aligned fillRects. No Zdog, no depth axis, no three quarter
# camera. It had stood for three rounds and every gate was green, because the one artifact a
# craft judge grades a frame against is the one artifact nothing checked.
#
# This is cheap and certain: a dossier that names a drawing library by name is making a claim
# about the slide's own <script> tags, and those are readable. Named narrowly, one entry per
# library this engine can actually load, so the check cannot widen into taste.
LIBRARIES = {
    "zdog": "zdog",
    "d3": "d3",
    "topojson": "topojson",
    "three.js": "three",
    "threejs": "three",
    "taichi": "taichi",
    "matter": "matter",
    "rough": "rough",
}


def declared_libraries(body: str) -> list:
    """Library names a dossier's art block claims, lowercased.

    ONLY the `technique` field, which is the DECLARATION. The rationale beside it is discussion,
    and reading it turned this gate's own repair into a new finding: the corrected slide 1 block
    explains that the frame draws "no Zdog, no depth axis and no three quarter view", and a gate
    reading that prose recorded a claim to both Zdog and three.js. Prose about what did not ship
    is not a claim that it did.

    `technique` is written as a one line quoted scalar and `section()` only reads block scalars,
    so both forms are read here.
    """
    m = re.search(r'^\s*technique:\s*"([^"]*)"', body, re.M)
    low = ((m.group(1) if m else "") + " " + section(body, "technique")).lower()
    return sorted({k for k in LIBRARIES if re.search(rf"(?<![a-z.]){re.escape(k)}(?![a-z])", low)})


def slide_sources(html: str) -> str:
    """Every src the slide loads, plus its inline script, as one lowercased haystack."""
    return " ".join(re.findall(r"<script[^>]*>", html, re.I)).lower() + " " + html.lower()


# THE CLAIM SET, DECLARED IN FOUR PLACES AND COMPARED IN NONE. 2026-09-07, carousel no. 17.
#
# `SLIDE_DOSSIER_SPEC.md` line 19 defines the field in six words: `claims: [c4, c7]  # every
# factual string on this slide, by claim id`. Four separate artifacts then state that set.
#
#   the dossier's `claims:` list            what the plan says the frame stands on
#   the dossier's `numerals:` `value_from`  which of those claims a printed figure came from
#   `copy.json`'s per-slide `claims`        what the copy chamber wrote
#   the rendered claim strip                the citation a reader can actually see
#
# On 2026-09-07 an integrity judge found three frames whose strip disagreed with the dossier that
# declared it. Three were repaired, and the same judge came back the next round with two more,
# slide 3's labels and slide 8's numerals. That is the run's own most transferable lesson written
# in its record: A REPAIR SCOPED TO THE STRING A FINDING NAMES LEAVES THE CLASS OPEN. The same
# round, in the same shape, `compute.py` returned `len()` over a typed list under a docstring
# post mortem about returning `len()` over a typed list.
#
# Measured over the seventeen decks this project has shipped, before a line of this was written:
#   strip against plan   drift on 5 decks and 9 frames, and none on the deck that shipped today
#   copy against plan    drift on 8 decks and 12 frames, and none on the deck that shipped today
# Six of those copy-side frames print no strip at all, which is why the copy surface is read and
# not only the rendered one: printing the strip is a design choice a frame is free to decline,
# and `copy.json` exists for every deck this project has ever built.
CLAIMS_INLINE = re.compile(r"^claims:\s*\[([^\]]*)\]\s*$", re.M)
CLAIMS_BLOCK = re.compile(r"^claims:\s*\n((?:[ \t]+-[ \t].*\n)+)", re.M)
NUMERALS_BLOCK = re.compile(r"^numerals:\s*(?:\[\s*\]\s*$|\n((?:[ \t]+-[ \t].*\n)*))", re.M)
CLAIM_ID = re.compile(r"\bc\d+\b")

# A TEXT NODE THAT IS NOTHING BUT CLAIM IDS. The whole node, anchored, because a node reading
# "CLAIM c7. QUOTED VERBATIM." is a sentence about a claim rather than a citation strip, and a
# gate that reads it as one invents a frame that cites a single claim. The separators are the
# three this project's frames have actually used, measured: a space on fourteen decks, a middle
# dot on 2026-08-18, and a comma nowhere yet. A strip split across several nodes is one strip:
# 2026-08-19's slide 8 renders `c3`, `c19`, `c20` and `c21` as four nodes, so taking the first
# node alone would report a frame citing one claim where the reader sees four.
CLAIM_STRIP_NODE = re.compile(r"^c\d+(?:[\s,·]+c\d+)*$")


def _ids(text: str) -> list:
    """The claim ids in a string, in order, deduplicated."""
    out = []
    for cid in CLAIM_ID.findall(text or ""):
        if cid not in out:
            out.append(cid)
    return out


def dossier_claims(body: str) -> list:
    """The `claims:` list one dossier declares, inline or as a block.

    Every storyboard this project has shipped writes it inline, and the block form is read too
    because a selector that can only see the shape it was written against is GATE_LESSONS 39. A
    `claims:` key that parses to nothing is reported by the caller rather than read as absent.
    """
    m = CLAIMS_INLINE.search(body)
    if m:
        return _ids(m.group(1))
    m = CLAIMS_BLOCK.search(body)
    return _ids(m.group(1)) if m else []


def declares_claims(body: str) -> bool:
    """The dossier HAS a claims key, whether or not anything parsed out of it."""
    return bool(re.search(r"^claims:", body, re.M))


def numeral_claims(body: str) -> list:
    """The claim ids the dossier's `numerals:` block sources its figures from.

    `numerals: []` is a frame that prints no figure and is not a hole. The comment beside a
    `value_from` carries the value itself on most decks, so ids are taken from the whole entry.
    """
    m = NUMERALS_BLOCK.search(body)
    return _ids(m.group(1)) if (m and m.group(1)) else []


def rendered_claim_ids(nodes: list) -> list | None:
    """The claim ids the frame PRINTS as a citation strip, or None if it prints no strip.

    None and [] are different answers and must not share a return value. None is a frame that
    declines to cite, which is a design choice this gate does not get to overrule. [] would be a
    strip with nothing in it, which no frame can produce.
    """
    out = []
    for node in nodes:
        t = (node or "").strip()
        if t and CLAIM_STRIP_NODE.match(t):
            for cid in _ids(t):
                if cid not in out:
                    out.append(cid)
    return out or None


def copy_claims(copy: dict | None, n: int) -> list | None:
    """`copy.json`'s per-slide claim list for slide n, or None if that surface is absent.

    The key is read off the slide id the same way `absence_check.claims_of` reads it, so a deck
    keyed `S1` and a deck keyed `slide-1` are both found.
    """
    if not isinstance(copy, dict):
        return None
    for sid, s in (copy.get("slides") or {}).items():
        m = re.search(r"(\d+)", str(sid))
        if not m or int(m.group(1)) != n or not isinstance(s, dict):
            continue
        if "claims" not in s:
            return None
        return [str(x) for x in (s.get("claims") or [])]
    return None

def parse_dossiers(storyboard: str) -> dict:
    """Slide number to its YAML-ish block. Same fenced form dossier_check reads."""
    out = {}
    for n, body in re.findall(r"```yaml\s*\nslide:\s*(\d+)\s*\n(.*?)```", storyboard, re.S):
        out[int(n)] = body
    return out


# A BOLD LEAD LINE IS A HEADING THAT IS NOT SPELLED AS ONE, and 2026-09-16 is why this is here.
#
# `palette_sections` looked for a markdown heading naming the palette and every storyboard before
# that one carried one. That deck writes its whole art section as bold lead-ins instead
# (`**Palette, MEASURED rather than chosen by eye.**`, `**Camera and light.**`), so no section was
# found, the two loose shapes were never read, and the palette check reported "the storyboard
# defines no `name #HEX` palette" on a deck that declares seven.
#
# A gate that selects what to examine by an allowlist of FORMS sleeps on the form nobody thought
# of. GATE_LESSONS 39, and this is the third time in this one parser.
BOLD_LEAD = re.compile(r"^\*\*(.+?)\*\*", re.M)


def palette_sections(storyboard: str) -> list:
    """Every span running from an anchor that names the palette to the next anchor.

    Two anchors, both taken off real storyboards. A markdown heading, which is what every deck
    up to 2026-09-15 wrote, spanning to the next heading as high. A BOLD LEAD LINE, which is what
    2026-09-16 wrote, spanning to the next heading or the next bold lead, whichever comes first.

    The two loose declaration shapes are read inside these spans and nowhere else, so a hex
    quoted in body prose cannot become a token.
    """
    heads = [(m.start(), len(m.group(1)), m.group(2)) for m in HEADING.finditer(storyboard)]
    out = []
    for i, (pos, lvl, title) in enumerate(heads):
        if "palette" not in title.lower():
            continue
        end = len(storyboard)
        for pos2, lvl2, _t in heads[i + 1:]:
            if lvl2 <= lvl:
                end = pos2
                break
        out.append(storyboard[pos:end])
    leads = [(m.start(), m.group(1)) for m in BOLD_LEAD.finditer(storyboard)]
    for i, (pos, title) in enumerate(leads):
        if "palette" not in title.lower():
            continue
        end = min([p for p, _l, _t in heads if p > pos] + [p for p, _t in leads[i + 1:]]
                  + [len(storyboard)])
        out.append(storyboard[pos:end])
    return out


def palette_map(storyboard: str) -> dict:
    """Token name to hex, from the storyboard's own palette section.

    Read, never typed. A constant here would be a second copy of a fact that already has a
    home, which is the shape that put the wrong URL on three decks.

    A name carrying a space is dropped, as it always was. `\x60stock deep #DCCFB2\x60` on
    2026-08-20 is a second spelling of the `stock_deep` its own table already declares, and a
    multi word token cannot be word-matched in a palette sentence without matching each half.
    """
    out = {}
    for name, hexv in PALETTE_DEF.findall(storyboard):
        name = name.strip().lower()
        if " " not in name:
            out[name] = hexv.upper()
    for span in palette_sections(storyboard):
        for pat in (PALETTE_ROW, PALETTE_PLAIN, PALETTE_COLUMNS):
            for name, hexv in pat.findall(span):
                name = name.strip().lower()
                if " " not in name and name not in ("token", "hex", "colour", "color"):
                    out.setdefault(name, hexv.upper())
    # THE FOURTH SHAPE: `name #HEX` inside a dossier's own `palette: >` prose, which is what
    # 2026-08-30 wrote and what made this parser read ZERO tokens on that deck. Ten storyboards
    # had a `## Palette` heading, the eleventh put the same pairs where the spec asks for them
    # and the calibration assertion below caught the silence as a number. Read last, so a deck
    # that declares a token in BOTH places keeps the section's value.
    for body in parse_dossiers(storyboard).values():
        for name, hexv in PALETTE_PROSE.findall(section(body, "palette")):
            name = name.strip().lower()
            if " " not in name:
                out.setdefault(name, hexv.upper())
    return out


def rgb(hexv: str) -> tuple:
    """The three channels of a `#RRGGBB`."""
    h = hexv.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def drawn(hexv: str, html_upper: str) -> bool:
    """Is this colour anywhere in the frame's source, in ANY of the forms a frame writes it?

    A HEX LITERAL IS NOT THE ONLY WAY TO DRAW A COLOUR, and assuming it was made this check
    blind to exactly the decks it most needed to read. 2026-08-30 drew its three slabs as
    canvas gradients over `tint:'176,200,214'`, which is `#B0C8D6` to the pixel and is the
    colour its dossier declares. Ten earlier decks passed this check on hex literals alone, so
    the assumption held every time it was tested and was wrong the first time a deck computed
    its ramps instead of writing them.

    Reported as a miss, that would have been a false failure naming the plan as the liar. The
    frame was drawing precisely what it said it would.
    """
    if hexv.upper() in html_upper:
        return True
    r, g, b = rgb(hexv)
    # `rgb(176,200,214)`, `rgba(176, 200, 214, .4)` and a bare `'176,200,214'` gradient tint.
    return re.search(rf"(?<!\d){r}\s*,\s*{g}\s*,\s*{b}(?!\d)", html_upper) is not None


def section(body: str, key: str) -> str:
    """The prose under `key: >` in one dossier block."""
    m = re.search(rf"^  {re.escape(key)}:\s*>\s*\n((?:    .*\n)+)", body, re.M)
    return m.group(1) if m else ""


# A continuation line inside a block list: indented FURTHER than the `  - ` that opened the
# item, and not itself a new item. Four or more leading spaces, because `  - ` is two and every
# storyboard that has ever wrapped an item aligned the continuation under the opening quote.
_ACC_BLOCK = re.compile(r"^acceptance:[^\S\n]*\n((?:(?:  - |    +)\S.*\n)+)", re.M)


def acceptance_items(body: str) -> list:
    """Every acceptance item in one dossier, INCLUDING the ones that wrap.

    THE DEFECT THIS SHAPE EXISTS FOR. 2026-09-08, and it had been running since this gate was
    written. The block was taken with `^acceptance:\\s*\\n((?:  - .*\\n)+)`, whose repetition
    stops at the first line that does not begin with two spaces and a dash. An acceptance item
    long enough to wrap continues on an indented line, so THE BLOCK ENDED AT THE FIRST WRAPPED
    ITEM and every item after it in that slide's list was never read.

    Measured on the 2026-09-08 storyboard as it was first written, at commit 7a32b69e:
    **17 items read of 52 written.** The gate then reported `0 of 16 acceptance items carry a
    machine-checkable assertion`, which was true of what it could see and false of the plan,
    because the items that survive truncation are the SHORT ones and a short item is the one
    least likely to quote a string. Three frames were outside their own declared median L* and
    no gate said so, because every one of those declarations sits past a wrapped item.

    Its old `--self-test` passed throughout, because the fixture it tests against writes every
    item on one line. That is GATE_LESSONS 16 exactly: a fixture written by the author of the
    detector agrees with the detector.

    TWO PARSERS FOR ONE FORMAT WAS THE ROOT CAUSE, which is GATE_LESSONS 34. `dossier_check.py`
    reads the same blocks with `yaml.safe_load` and counted all 52 the whole time. So the YAML
    parse is the primary route here now and the regex is only the fallback for a block PyYAML
    refuses, which keeps this gate working on a malformed dossier rather than reporting it
    clean. The fallback is continuation aware, so both routes read the same list.
    """
    try:
        import yaml                                     # noqa: PLC0415 - optional, see below
        doc = yaml.safe_load(body)
        if isinstance(doc, dict) and isinstance(doc.get("acceptance"), list):
            return [str(x).strip() for x in doc["acceptance"] if str(x).strip()]
    except Exception:
        pass                                            # fall through to the text route
    m = _ACC_BLOCK.search(body)
    if not m:
        return []
    items: list[str] = []
    for ln in m.group(1).splitlines():
        if ln.strip().startswith("- "):
            items.append(ln.strip()[2:].strip())
        elif items:
            items[-1] += " " + ln.strip()
    return [re.sub(r'^"|"$', "", it).strip() for it in items if it.strip()]


def rendered_text(report: dict, n: int) -> str:
    for s in report.get("slides") or []:
        if f"{n:02d}" in str(s.get("file", "")):
            return " ".join(str(t.get("text", "")) for t in (s.get("text_nodes") or []))
    return ""


def rendered_nodes(report: dict, n: int) -> list:
    for s in report.get("slides") or []:
        if f"{n:02d}" in str(s.get("file", "")):
            return [str(t.get("text", "")) for t in (s.get("text_nodes") or []) if t.get("text")]
    return []


# The two keys whose drift is an assertion drifting. Everything else `type:` declares is
# furniture or a byline and warns. Named here rather than inferred, and the list is the FAIL
# severity only: every key the block declares is compared, so a dossier that invents a key name
# is examined rather than skipped. That is GATE_LESSONS 39, where `copy_sync_check` selected by
# an allowlist of key names and could not see twelve of one deck's nineteen keys.
ASSERTING_KEYS = ("hook", "dek")

# `key: "value"` and `key: ["a", "b"]` inside the `type:` block. Two spaces of indent, which is
# the form SLIDE_DOSSIER_SPEC.md prints and every dossier that has ever declared one has used.
# EITHER QUOTE, BECAUSE A `type:` BLOCK IS YAML AND YAML HAS TWO. 2026-09-12.
#
# This read only the double quoted form, so a single quoted `dek:` was not a declaration at all
# and the string never reached the render comparison. The 2026-09-12 storyboard writes all nine
# deks that way and the gate reported the deck clean on hooks and labels alone. Three earlier
# storyboards, 08-22, 08-25 and 08-27, each had one line go the same way unnoticed.
#
# WHY THE RUNS CHOSE SINGLE QUOTES, which is the part that makes this a parser gap rather than a
# storyboard mistake. A dek on this project routinely carries a verbatim fragment, and a fragment
# is set in double quotes. `dek: 'The agency defines it as "a combined index of ride quality and
# pavement surface distress."'` is the natural YAML for that and escaping it into the double
# quoted form would be worse writing for no gain.
#
# It is caught by the self-test that reads the NEWEST SHIPPED STORYBOARD rather than a fixture,
# which is the case immediately below the parser tests and the reason that case exists. The
# fixtures all spelled it the way the parser already read.
TYPE_SCALAR = re.compile(r"""^  ([a-z_][a-z_0-9]*):\s*(?:"(.*)"|'(.*)')\s*$""")
TYPE_LIST = re.compile(r'^  ([a-z_][a-z_0-9]*):\s*\[(.*)\]\s*$')


def squash(s: str) -> str:
    """Case folded with EVERY space removed, and the reason is measured rather than guessed.

    `render.py` joins a text node's child spans with no separator, so a hook broken across two
    spans for line control comes back from the render report as "August 7thcame and went." A
    substring test that collapses whitespace instead of removing it reports that correct frame
    as a missing hook. Replayed over the five shipped decks, collapsing produced 14 false
    failures on 2026-08-16 alone and removing produces none.
    """
    s = (s or "").replace('\\"', '"').replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", "", s).lower()


def declared_strings(body: str) -> list:
    """[(key, string)] the dossier's `type:` block says will be on the frame."""
    m = re.search(r"^type:\s*\n(.*?)(?=^\S|\Z)", body, re.S | re.M)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        sm = TYPE_SCALAR.match(line)
        if sm:
            # Group 2 is the double quoted body, group 3 the single quoted one. YAML escapes a
            # literal apostrophe inside single quotes by doubling it, and two shipped deks do
            # exactly that ("The university''s release"), so undo it or the rendered string
            # never matches.
            if sm.group(2) is not None:
                out.append((sm.group(1), sm.group(2)))
            else:
                out.append((sm.group(1), sm.group(3).replace("''", "'")))
            continue
        lm = TYPE_LIST.match(line)
        if lm:
            for v in re.findall(r'"([^"]*)"', lm.group(2)):
                out.append((lm.group(1), v))
    # A one or two character label is furniture a squash test cannot distinguish from noise.
    return [(k, v) for k, v in out if len(v.strip()) >= 3]


def nearest(needle: str, nodes: list) -> str:
    """The rendered string closest to what the plan declared, so the message names the drift.

    A failure reading "the plan says X and the frame does not print it" sends a run looking at
    nine frames. One reading "the frame prints Y instead" is one edit. This is diagnostic and
    decides nothing: the pass or fail was already settled by the exact test above it.
    """
    import difflib
    best, score = "", 0.0
    for node in nodes:
        r = difflib.SequenceMatcher(None, squash(needle), squash(node)).ratio()
        if r > score:
            best, score = node, r
    return best if score >= 0.5 else ""


def check(storyboard: str, slides_dir: Path, report: dict,
          copy: dict | None = None, claim_ids: set | None = None) -> tuple:
    """`copy` and `claim_ids` are optional so the three existing callers keep working.

    They are OPTIONAL, never silently absent: a run that passes neither is told in a warning that
    the claim-set comparison ran on fewer surfaces than exist, because the failure mode of this
    whole class of gate is that its empty case and its clean case print the same line.
    """
    fails, warns, stats = [], [], {"checkable": 0, "prose": 0, "slides": 0,
                                   "declared": 0, "silent_slides": []}
    pal = palette_map(storyboard)
    dossiers = parse_dossiers(storyboard)
    if not dossiers:
        return ([], ["plan_render_check: no fenced slide dossiers found, nothing compared"], stats)
    if not pal:
        warns.append("plan_render_check: the storyboard defines no `name #HEX` palette, so the "
                     "declared-colour check could not run")

    for n, body in sorted(dossiers.items()):
        stats["slides"] += 1
        html_p = slides_dir / f"slide-{n:02d}.html"
        html = html_p.read_text(encoding="utf-8").upper() if html_p.exists() else ""
        text = rendered_text(report, n)

        # ---- PALETTE: a colour the plan names must be somewhere on the frame ----------
        prose = section(body, "palette").lower()
        # THIS FRAME'S OWN DECLARATION WINS over the deck-wide map, and getting that backwards
        # turned one real question into twenty false ones. Where a storyboard declares its
        # palette per dossier, `field` is a different colour on frame 2 than on frame 7 and the
        # deck-wide map holds only the first. Checking every frame against that one value asks
        # whether frame 7 drew frame 1's grey, which no plan ever promised.
        #
        # And where a frame declares its OWN palette, that is the whole of its palette. The
        # deck-wide map otherwise leaks a token into every frame whose prose happens to use the
        # word: `lit` is declared by frames 5 and 8, and frames 1, 2, 4 and 6 all say "lit" of
        # a chamfer or a crest without claiming frame 8's particular blue. Four false failures
        # out of twelve, every one of them the gate reading a plan that says something else.
        local = {k.lower(): v.upper() for k, v in PALETTE_PROSE.findall(section(body, "palette"))}
        for token, hexv in (local or pal).items():
            if not re.search(rf"\b{re.escape(token)}\b", prose):
                continue
            if html and not drawn(hexv, html):
                fails.append(
                    f"slide {n}: the dossier's palette names {token} ({hexv}, "
                    f"rgb {','.join(str(c) for c in rgb(hexv))}) and the frame does not contain "
                    f"that colour anywhere, as a hex literal or as an rgb triplet. A declared "
                    f"colour that was never drawn is the 2026-08-19 slide 5 defect, where the "
                    f"plan said the differing words are marked in pecos and five passes shipped "
                    f"uniform ink")

        # ---- DECLARED: the words the plan says will be on the frame -------------------
        # THE 2026-08-21 DEFECT. A refused build left the previous build's HTML on disk, the
        # renderer rendered it, and the plan's repaired copy never reached a pixel.
        nodes = rendered_nodes(report, n)
        declared = declared_strings(body)
        if not declared:
            stats["silent_slides"].append(n)
        for key, want in declared:
            stats["declared"] += 1
            if not text:
                continue
            stats["compared"] = stats.get("compared", 0) + 1
            if squash(want) in squash(text):
                continue
            near = nearest(want, nodes)
            instead = f" The frame prints {near!r} in its place." if near else ""
            where = "FAIL" if key in ASSERTING_KEYS else "warn"
            msg = (f"slide {n}: the dossier declares {key} as {want!r} and the render does not "
                   f"carry that string.{instead} A plan the frame did not execute is what let a "
                   f"refused build ship stale HTML to three scoring judges on 2026-08-21")
            (fails if where == "FAIL" else warns).append(msg)

        # ---- CLAIMS: four declarations of one set -------------------------------------
        # See the block comment above CLAIMS_INLINE for the five frames this shipped past on
        # 2026-09-07 and the seventeen deck replay. The relation is EQUALITY rather than
        # containment, because the spec defines the list as every factual string on the slide:
        # a strip printing fewer ids than the plan declares is a frame under-citing a fact a
        # reader cannot trace, and one printing more is a plan that no longer describes the frame.
        planned = dossier_claims(body)
        if declares_claims(body) and not planned:
            warns.append(f"slide {n}: the dossier has a `claims:` key and no claim id parsed out "
                         f"of it, so this frame's claim set was compared against nothing")
        if planned:
            stats["claim_slides"] = stats.get("claim_slides", 0) + 1

            # The plan's own ids have to exist. `label_guard` asks this of the ids a frame
            # PRINTS, which is the other half and cannot see a plan-only id on an uncited frame.
            # A plan naming a claim that does not exist is GATE_LESSONS
            # entry 19 ("A reference is a dependency even when it is not a link").
            if claim_ids:
                unknown = [c for c in planned if c not in claim_ids]
                if unknown:
                    fails.append(
                        f"slide {n}: the dossier's claims list names {', '.join(unknown)} and "
                        f"claims.json holds no such claim. Prose or a plan that names a record is "
                        f"asserting that record exists")

            # A figure's source has to be one of the claims the slide stands on. This is the
            # second of the two the judge found in round 4, on slide 8.
            stray = [c for c in numeral_claims(body) if c not in planned]
            if stray:
                fails.append(
                    f"slide {n}: the dossier sources a numeral from {', '.join(stray)} and its "
                    f"own claims list does not carry {'them' if len(stray) > 1 else 'it'}. The "
                    f"figure on the frame and the claims behind the frame are one set")

            shown = rendered_claim_ids(nodes)
            declared_copy = copy_claims(copy, n)
            # ONE FINDING PER FRAME, naming every surface that disagrees. Two near identical
            # lines about one drift is the shape that taught a run to scroll past the tenth
            # warning. That is GATE_LESSONS
            # entry 16 ("Fixtures written by the author of the detector agree with it"),
            # and the strip and the copy list drift together on six of
            # the nine frames this replay names.
            off = []
            for label, other in (("the frame's claim strip", shown),
                                 ("copy.json's claim list", declared_copy)):
                if other is None:
                    continue
                stats["claims_compared"] = stats.get("claims_compared", 0) + 1
                missing = [c for c in planned if c not in other]
                extra = [c for c in other if c not in planned]
                if missing or extra:
                    off.append(f"{label} says {' '.join(other)}"
                               + (f", absent there {', '.join(missing)}" if missing else "")
                               + (f", absent from the plan {', '.join(extra)}" if extra else ""))
            if off:
                fails.append(
                    f"slide {n}: the dossier declares {' '.join(planned)} and " + "; ".join(off)
                    + ". Three frames drifted this way on 2026-09-07, were repaired, and the "
                      "same judge found two more in the next round")
            if shown is None:
                stats.setdefault("uncited_slides", []).append(n)
            if declared_copy is None:
                stats.setdefault("copyless_slides", []).append(n)

        # ---- THE DECLARED LIBRARY HAS TO BE IN THE SLIDE ------------------------------
        if html:
            hay = slide_sources(html)
            for lib in declared_libraries(body):
                token = LIBRARIES[lib]
                if not re.search(rf"(?<![a-z]){re.escape(token)}(?![a-z])", hay):
                    fails.append(
                        f"slide {n}: the dossier's art block names {lib} and slide-{n:02d}.html "
                        f"never loads it. A technique nobody executed is a plan a craft critic "
                        f"grades the frame against, and slide 1 carried a Zdog scene it never "
                        f"drew for three rounds with every gate green")

        # ---- ACCEPTANCE: the items that assert something countable --------------------
        checkable_here = 0
        for item in acceptance_items(body):
            low = item.lower()
            # THE FRAME'S OWN MEDIAN BAND, ASKED FIRST. Before the prose filter, deliberately: an
            # item carrying a number on both sides of a comparison is arithmetic whatever else
            # its sentence says, and a band that fell through into the prose count is the 2026-09-16
            # defect exactly.
            band = parse_band(item)
            if band is not None:
                if band["lo"] is None and band["hi"] is None:
                    warns.append(
                        f"slide {n}: an acceptance item states this frame's own median L* and no "
                        f"band could be read out of it ({band['clause']!r}), so it was checked "
                        f"against nothing. Write it as `the frame's median L* at 432px is between "
                        f"<lo> and <hi>`, or as `<n> or higher`, `<n> or lower`, or `<n> plus or "
                        f"minus <tol>`")
                    stats["prose"] += 1
                    continue
                if band["size"] is None:
                    warns.append(
                        f"slide {n}: an acceptance item declares a frame median band of "
                        f"{band_text(band)} and never says at what size to measure it, so it "
                        f"could not be settled. A median moves with the resampling. Write `at "
                        f"432px`, the size a reader receives, or `on the <w> by <h> grid`")
                    stats["prose"] += 1
                    continue
                png = frame_image(slides_dir, n)
                if png is None:
                    fails.append(
                        f"slide {n}: the dossier declares a frame median band of "
                        f"{band_text(band)} and no render of this frame could be found to measure "
                        f"it. A check that CANNOT run is not a check that passed. Looked for "
                        f"render/slide-{n:02d}.png, slide-{n:02d}.png and slide-{n:02d}.webp "
                        f"beside {slides_dir}")
                    stats["prose"] += 1
                    continue
                try:
                    got = median_lstar(png, band["size"])
                except Exception as exc:                             # noqa: BLE001
                    fails.append(
                        f"slide {n}: the dossier declares a frame median band of "
                        f"{band_text(band)} and it could not be measured: {exc}. Install Pillow "
                        f"and numpy. A gate that reports clean because it could not look is the "
                        f"shape this whole file exists to stop")
                    stats["prose"] += 1
                    continue
                w, h = band["size"]
                at = f"{w}px" if h is None else f"{w} by {h}"
                stats.setdefault("bands", []).append((n, got, band_text(band), at))
                checkable_here += 1
                stats["checkable"] += 1
                if not in_band(got, band):
                    fails.append(
                        f"slide {n}: the frame measures median L* {got:g} at {at} and its own "
                        f"dossier declared {band_text(band)}. The plan wrote the band before the "
                        f"frame was drawn, so this is the frame missing its plan rather than a "
                        f"threshold this gate chose. Redraw the frame or rewrite the band, and "
                        f"say in the run record which you did")
                continue
            if any(p in low for p in PROSE_ONLY):
                stats["prose"] += 1
                continue
            hit = False
            for needle in forbidden_needles(item):
                hit = True
                if text and needle.lower() in text.lower():
                    fails.append(
                        f"slide {n}: an acceptance item says {needle!r} appears nowhere on this "
                        f"frame, and the render prints it")
            if not hit:
                for m in REQUIRED_STR.finditer(item):
                    needle = m.group(2).strip()
                    if len(needle.split()) < 2:
                        continue
                    hit = True
                    if text and needle.lower() not in text.lower():
                        fails.append(
                            f"slide {n}: an acceptance item says the frame carries {needle!r} "
                            f"and the render does not print it")
            if hit:
                checkable_here += 1
                stats["checkable"] += 1
            else:
                stats["prose"] += 1
        if acceptance_items(body) and checkable_here == 0:
            stats.setdefault("blind_slides", []).append(n)

    # A COMPARISON THAT COMPARED NOTHING IS NOT A CLEAN COMPARISON. Both halves fail, and
    # neither is a warning, because the failure mode of this whole class of gate is that its
    # empty case and its clean case print the same line. 2026-08-18's dossiers carry no `type:`
    # block at all, so this gate would have reported that deck clean on a question it never
    # asked. SLIDE_DOSSIER_SPEC.md has required `type.hook` and `type.dek` since it was written.
    if stats["declared"] == 0:
        fails.append(
            "not one dossier in this storyboard declares a display string under `type:`, so "
            "nothing the reader will actually read was compared against the frames. "
            "knowledge/carousel/SLIDE_DOSSIER_SPEC.md requires `type.hook` and `type.dek`")
    elif not stats.get("compared"):
        fails.append(
            f"the storyboard declares {stats['declared']} display string(s) and the render "
            f"report carries no text for any slide, so none of them was compared. A render "
            f"report that describes no frames is a build that did not happen")
    elif stats["silent_slides"]:
        warns.append(
            f"slide(s) {', '.join(str(x) for x in stats['silent_slides'])} declare no display "
            f"string under `type:`, so their words were compared against nothing")

    # THE CLAIM SET'S OWN EMPTY CASE, and it takes the same treatment as the one above it. A deck
    # whose dossiers declare no claims at all has not passed this, it has not been asked.
    if stats["slides"] and not stats.get("claim_slides"):
        fails.append(
            "not one dossier in this storyboard declares a `claims:` list, so no frame's claim "
            "set was compared against anything. knowledge/carousel/SLIDE_DOSSIER_SPEC.md defines "
            "it as every factual string on the slide, by claim id")
    elif stats.get("claim_slides") and not stats.get("claims_compared"):
        warns.append(
            f"{stats['claim_slides']} dossier(s) declare a claims list and neither the render "
            f"report nor copy.json carries a claim set to compare it against, so the plan was "
            f"the only surface read")
    elif stats.get("uncited_slides") and len(stats["uncited_slides"]) == stats.get("claim_slides"):
        warns.append(
            "no frame in this deck prints a claim strip a reader can see. That is a design "
            "choice this gate does not overrule, and it means the citation half of the claim "
            "set was compared on copy.json alone")

    # COVERAGE, reported ONCE for the deck rather than once per frame. Eight identical warnings
    # is noise, and a warning a reader learns to scroll past protects nothing.
    total = stats["checkable"] + stats["prose"]
    if total and stats["checkable"] == 0:
        warns.append(
            f"not one of this deck's {total} acceptance items asserts anything a render could "
            f"contradict. They are written as prose about the frame rather than as claims about "
            f"it, so no gate could check them even in principle and the pixel critic is the only "
            f"reader they have. This is how 2026-08-18's slide 5 passed all five of its own items "
            f"while reading as a Gantt chart that contradicted its own caption. "
            f"knowledge/carousel/SLIDE_DOSSIER_SPEC.md says how to write a checkable one")
    elif stats.get("blind_slides"):
        warns.append(
            f"slide(s) {', '.join(str(x) for x in stats['blind_slides'])} carry no acceptance "
            f"item a render could contradict")
    return fails, warns, stats


def run(date: str, quiet: bool = False) -> int:
    out = REPO_ROOT / "out" / date
    sb = out / "storyboard.md"
    rp = out / "render" / "render_report.json"
    if not sb.exists():
        print(f"plan_render_check: no storyboard at {sb}", file=sys.stderr)
        return 1
    report = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}
    cp, cl = out / "copy.json", out / "claims.json"
    copy = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else None
    ids = None
    if cl.exists():
        raw = json.loads(cl.read_text(encoding="utf-8"))
        ids = {str(c.get("id")) for c in (raw.get("claims") if isinstance(raw, dict) else raw)
               if isinstance(c, dict)}
    fails, warns, stats = check(sb.read_text(encoding="utf-8"), out / "slides", report, copy, ids)
    for w in warns:
        print(f"  warn  {w}", file=sys.stderr)
    if fails:
        print(f"\nplan_render_check: {len(fails)} frame(s) do not match their own plan\n",
              file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    if not quiet:
        total = stats["checkable"] + stats["prose"]
        # PRINTED ON SUCCESS AS WELL AS ON FAILURE. A run that measured nothing and a run whose
        # every frame is inside its band print the same line otherwise, which is the shape this
        # whole file's coverage count exists to refuse.
        for fn, got, band, at in stats.get("bands", []):
            print(f"  band  slide {fn}: median L* {got:g} at {at}, declared {band}")
        print(f"plan_render_check: {stats['slides']} slide(s), {stats['checkable']} of {total} "
              f"acceptance items carry a machine-checkable assertion, and every one holds. "
              f"{stats.get('compared', 0)} of {stats['declared']} declared display string(s) "
              f"were found on their own frame. "
              f"{stats.get('claims_compared', 0)} claim set comparison(s) over "
              f"{stats.get('claim_slides', 0)} frame(s) that declare one, and every set agrees")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    SB = """
Palette line: `tower #16151C` and `pecos #8E4B3A` and `paper #F6F1E4`.

```yaml
slide: 5
job: >
  the inversion
claims: [c1, c4]
composition:
  focal: >
    the marked words
art:
  palette: >
    paper ground with ink type. The words that differ between the two wordings are marked in
    pecos, which clears contrast on paper.
type:
  hook: "One office. The same day."
  dek: "Two wordings."
  labels: ["05 / 09", "PARALLAX"]
acceptance:
  - "the differing words are marked in pecos and nothing else on the frame is"
  - "the frame carries 'One office' as its display line"
  - "the phrase 'flag red' appears nowhere on the frame"
```
"""
    REPORT = {"slides": [{"file": "slide-05.html",
                          "text_nodes": [{"text": "One office. The same day."},
                                         {"text": "Two wordings."},
                                         {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        dd = Path(d)

        # THE REAL 2026-08-19 DEFECT. The plan says pecos, the frame has none.
        (dd / "slide-05.html").write_text(
            "<style>.q{color:#23202B}</style><div>One office. The same day. Two wordings.</div>",
            encoding="utf-8")
        f, w, s = check(SB, dd, REPORT)
        ok("a frame whose plan declares pecos and draws none is CAUGHT",
           any("pecos" in x and "does not contain" in x for x in f), str(f))

        # ...and the repaired frame passes.
        GOOD = ("<style>.d{color:#8E4B3A}.p{background:#F6F1E4}</style>"
                "<div>One office. The same day. Two wordings.</div>")
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(SB, dd, REPORT)
        ok("...and the same frame with pecos actually drawn passes", not f, str(f))
        ok("the checkable acceptance items were counted", s["checkable"] >= 1, str(s))

        # A REQUIRED string the render does not print.
        R2 = {"slides": [{"file": "slide-05.html",
                          "text_nodes": [{"text": "Something else entirely."}]}]}
        f, w, s = check(SB, dd, R2)
        ok("an acceptance item naming a string the frame does not print is CAUGHT",
           any("does not print it" in x for x in f), str(f))

        # A FORBIDDEN string the render does print. 2026-08-18 slide 9 shape.
        R3 = {"slides": [{"file": "slide-05.html",
                          "text_nodes": [{"text": "One office. The same day."},
                                         {"text": "Two wordings. it is flag red here"},
                                         {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(SB, dd, R3)
        ok("an acceptance item forbidding a string the frame prints is CAUGHT",
           any("appears nowhere" in x for x in f), str(f))

        # ---- THE WRAPPED ACCEPTANCE ITEM, 2026-09-08 ---------------------------------
        # Replays the truncation directly. The fixture above writes every item on one line,
        # which is exactly why this gate certified a third of every plan and stayed green.
        WRAP_SB = """
```yaml
slide: 5
job: >
  the inversion
type:
  hook: "One office. The same day."
  dek: "Two wordings."
acceptance:
  - "the differing words are marked in pecos and nothing else on the frame is, and the reason
     is that a second marked run turns a comparison into a list"
  - "the frame carries 'One office' as its display line"
  - "the frame median L* measures 38 plus or minus 4"
  - "the phrase 'flag red' appears nowhere on the frame"
```
"""
        body5 = parse_dossiers(WRAP_SB)[5]
        items = acceptance_items(body5)
        ok("every acceptance item is read when one of them WRAPS",
           len(items) == 4, f"read {len(items)}: {items}")
        ok("...and the wrapped item is joined rather than cut at the line break",
           items and items[0].endswith("turns a comparison into a list"), str(items[:1]))

        # THE OLD PARSER, kept here as the thing this replaced, so the replay is visible rather
        # than asserted. It stops at the first line that is not `  - `.
        old = re.search(r"^acceptance:\s*\n((?:  - .*\n)+)", body5, re.M)
        old_n = len([ln for ln in old.group(1).splitlines()
                     if ln.strip().startswith("- ")]) if old else 0
        ok("the parser this replaced would have read ONE of the four",
           old_n == 1, f"old parser read {old_n}")

        # ...and the three items past the wrap are actually CHECKED, not merely counted. The
        # forbidden-string item is the last of the four and it is the one truncation ate.
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(WRAP_SB, dd, R3)
        ok("an item PAST the wrap is enforced, not just parsed",
           any("appears nowhere" in x for x in f), str(f))

        # BOTH ROUTES READ THE SAME LIST, on the real shipped storyboards rather than on a
        # fixture. GATE_LESSONS 50: the synthetic half proves the logic, and only the half that
        # goes and reads the real artifact would have gone red on the day this broke. If PyYAML
        # is ever absent from a runner the fallback carries this gate, so the two must agree.
        boards = sorted((REPO_ROOT / "runs" / "carousel").glob("2*/storyboard.md"))
        drift, swept = [], 0
        for bp in boards:
            for n, body in parse_dossiers(bp.read_text(encoding="utf-8")).items():
                swept += 1
                m = _ACC_BLOCK.search(body)
                fb: list = []
                for ln in (m.group(1).splitlines() if m else []):
                    if ln.strip().startswith("- "):
                        fb.append(ln.strip()[2:].strip())
                    elif fb:
                        fb[-1] += " " + ln.strip()
                fb = [re.sub(r'^"|"$', "", it).strip() for it in fb if it.strip()]
                if len(fb) != len(acceptance_items(body)):
                    drift.append(f"{bp.parent.name} slide {n}: "
                                 f"yaml {len(acceptance_items(body))} vs text {len(fb)}")
        ok(f"the yaml route and the text fallback agree over {swept} shipped dossier(s)",
           not drift, "; ".join(drift[:4]))
        ok("...and there were shipped dossiers to sweep", swept > 0, str(swept))

        # ---- DECLARED, the 2026-08-21 defect and every way it can go wrong ------------
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")

        # THE DEFECT ITSELF. The plan carries a repaired hook and the frame is the stale build.
        STALE = {"slides": [{"file": "slide-05.html",
                             "text_nodes": [{"text": "One office. The same week."},
                                            {"text": "Two wordings."},
                                            {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}
        f, w, s = check(SB, dd, STALE)
        ok("a hook that lives only in the plan is CAUGHT",
           any("declares hook" in x for x in f), str(f))
        ok("...and the failure names what the frame printed instead",
           any("The same week." in x for x in f), str(f))

        # A DEK is an assertion and fails. A LABEL is furniture and warns, because the drift
        # there is a comma repaired on the frame and not in the plan, which is what 2026-08-21
        # slide 5's byline actually is.
        NODEK = {"slides": [{"file": "slide-05.html",
                             "text_nodes": [{"text": "One office. The same day."},
                                            {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}
        f, w, s = check(SB, dd, NODEK)
        ok("a dek that never reached the frame is CAUGHT",
           any("declares dek" in x for x in f), str(f))
        NOLABEL = {"slides": [{"file": "slide-05.html",
                               "text_nodes": [{"text": "One office. The same day."},
                                              {"text": "Two wordings."},
                                              {"text": "05 / 09"}, {"text": "ORTHOGRAPHIC"}]}]}
        f, w, s = check(SB, dd, NOLABEL)
        ok("a label that drifted WARNS rather than failing",
           not f and any("declares labels" in x for x in w), f"fails={f} warns={w}")

        # A HOOK BROKEN ACROSS TWO SPANS is what render.py actually returns, with no space at
        # the join. Measured on 2026-08-19 slide 1, which shipped correctly and reads
        # "August 7thcame and went." in the report. A gate that fails that is a gate nobody runs.
        SPLIT = {"slides": [{"file": "slide-05.html",
                             "text_nodes": [{"text": "One office.The same day."},
                                            {"text": "Two wordings."},
                                            {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}
        f, w, s = check(SB, dd, SPLIT)
        ok("...and a hook the renderer joined without a space still passes", not f, str(f))

        # THE EMPTY CASE IS NOT THE CLEAN CASE. 2026-08-18's dossiers declare no `type:` block.
        SB_NOTYPE = re.sub(r"type:\n(?:  .*\n)+", "", SB)
        f, w, s = check(SB_NOTYPE, dd, REPORT)
        ok("a storyboard that declares no display string at all FAILS",
           any("declares a display string" in x for x in f), str(f))
        f, w, s = check(SB, dd, {"slides": []})
        ok("...and declared strings with nothing rendered to compare them to FAILS",
           any("none of them was compared" in x for x in f), str(f))

        # COVERAGE: a slide whose whole list is unfalsifiable.
        SB2 = SB.replace('  - "the differing words are marked in pecos and nothing else on the frame is"\n', "") \
                .replace("""  - "the frame carries 'One office' as its display line"\n""", "") \
                .replace("""  - "the phrase 'flag red' appears nowhere on the frame"\n""",
                         '  - "the composition reads as balanced at thumb"\n')
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(SB2, dd, REPORT)
        ok("a deck whose acceptance list nothing could fail is WARNED",
           any("could contradict" in x for x in w), str(w))

    # AGAINST THE REAL ARTIFACT, not only against a fixture this file wrote. GATE_LESSONS 50:
    # a checker that classifies a thing must assert its classification against the thing. The
    # `type:` block is written by hand every run, so the day a storyboard spells it differently
    # this parser starts finding nothing and would otherwise report every deck clean forever.
    shipped = sorted((REPO_ROOT / "runs" / "carousel").glob("2*")) \
        if (REPO_ROOT / "runs" / "carousel").is_dir() else []
    newest = next((p for p in reversed(shipped) if (p / "storyboard.md").exists()), None)
    if newest is not None:
        ds = parse_dossiers((newest / "storyboard.md").read_text(encoding="utf-8"))
        keys = {k for b in ds.values() for k, _v in declared_strings(b)}
        ok(f"the newest shipped storyboard ({newest.name}) declares display strings this "
           f"parser can read", {"hook", "dek"} <= keys, f"found keys {sorted(keys)}")

    # The palette map is READ from the storyboard, never held as a constant here.
    ok("the palette is read from the storyboard rather than typed into this file",
       palette_map(SB) == {"tower": "#16151C", "pecos": "#8E4B3A", "paper": "#F6F1E4"},
       str(palette_map(SB)))

    # ---- THE 2026-09-12 DEFECT: A QUOTE STYLE THIS PROJECT WRITES AND THE PARSER COULD NOT READ.
    # Every string here is lifted off the 2026-09-12 storyboard, which wrote all nine of its deks
    # single quoted and had all nine silently skipped. Revert TYPE_SCALAR to the double quoted
    # form alone and the first three of these go red.
    _SQ = ("type:\n"
           "  hook: \"Somebody used to stand here.\"\n"
           "  dek: 'A rater measured the distress by hand on a sampled portion.'\n")
    ok("a SINGLE QUOTED display string is a declaration (2026-09-12, all nine deks)",
       dict(declared_strings(_SQ)).get("dek") == "A rater measured the distress by hand on a sampled portion.",
       str(declared_strings(_SQ)))
    ok("...and the double quoted form beside it still reads",
       dict(declared_strings(_SQ)).get("hook") == "Somebody used to stand here.")
    # THE REASON THE RUNS REACH FOR SINGLE QUOTES AT ALL. A dek carries a verbatim fragment and
    # a fragment is set in double quotes, so the outer quote has to be the other one.
    _EMB = ("type:\n"
            "  dek: 'The agency defines it as \"a combined index of ride quality.\"'\n")
    ok("...and an embedded double quoted fragment survives whole",
       dict(declared_strings(_EMB))["dek"] == 'The agency defines it as "a combined index of ride quality."',
       str(declared_strings(_EMB)))
    # YAML doubles an apostrophe to escape it inside single quotes, and two shipped deks do.
    _ESC = "type:\n  dek: 'The university''s release lists what prepared the data.'\n"
    ok("...and a doubled apostrophe comes back as one",
       dict(declared_strings(_ESC))["dek"] == "The university's release lists what prepared the data.",
       str(declared_strings(_ESC)))
    # AND IT STILL REFUSES WHAT IS NOT A DECLARATION, which is what stops the wider pattern from
    # turning prose into display strings.
    _NOTQ = "type:\n  dek: A rater measured the distress by hand.\n  hook: \"Somebody used to stand here.\"\n"
    ok("an UNQUOTED value is still not a declaration",
       [k for k, _ in declared_strings(_NOTQ)] == ["hook"], str(declared_strings(_NOTQ)))
    _MIX = "type:\n  dek: 'mismatched marks are not a string\"\n"
    ok("...and mismatched marks declare nothing", declared_strings(_MIX) == [], str(declared_strings(_MIX)))

    # ---- THE 2026-08-28 DEFECT: A TOKEN NAME THIS PROJECT WRITES AND THE PARSER COULD NOT READ.
    # Each of these three declaration shapes was taken off a real shipped storyboard. Revert the
    # character class or the two section-scoped shapes and the matching case goes red here.
    _UNDER = "Palette: `sky_predawn #1A1C33` and `rim_light #F2D9B4`."
    ok("an UNDERSCORED token in the inline form is read (2026-08-28, and every deck before it)",
       palette_map(_UNDER) == {"sky_predawn": "#1A1C33", "rim_light": "#F2D9B4"},
       str(palette_map(_UNDER)))
    _TABLE = ("## Palette, Armstrong County's own section\n\n"
              "| token | hex | source |\n|---|---|---|\n"
              "| `caliche_cap` | `#E4DCC6` | the Ogallala caprock |\n"
              "| `satin_spar` | `#F5F1E6` | gypsum veins. Declared `#F4F0E4` until round two |\n")
    ok("the MARKDOWN TABLE form eight of ten shipped storyboards use is read",
       palette_map(_TABLE) == {"caliche_cap": "#E4DCC6", "satin_spar": "#F5F1E6"},
       str(palette_map(_TABLE)))
    ok("...and a second hex inside a row's prose cell invents no token named `declared`",
       "declared" not in palette_map(_TABLE))
    _PLAIN = "## Palette\n\nDeclared as plain pairs:\n\n    ledge_shadow #241E22\n    ochre #B4903F\n"
    ok("the INDENTED PLAIN PAIR form is read",
       palette_map(_PLAIN) == {"ledge_shadow": "#241E22", "ochre": "#B4903F"},
       str(palette_map(_PLAIN)))

    # THE SCOPE, which is what keeps the two loose shapes from inventing tokens. A hex quoted in
    # body prose is not a declaration, and 2026-08-28's slide 6 acceptance line quotes one.
    _PROSE = ("## Palette\n\n| token | hex |\n|---|---|\n| `ochre` | `#B4903F` |\n\n"
              "## Slide 6\n\n| a | b |\n|---|---|\n| 525.5 is set in | `#B4903F` and no plate |\n")
    ok("a hex in a table OUTSIDE the palette section declares nothing",
       palette_map(_PROSE) == {"ochre": "#B4903F"}, str(palette_map(_PROSE)))

    # AND THE GATE ITSELF STILL GOES RED, through an underscored token, which is the whole point
    # of the parser fix. Without it this deck reports "the storyboard defines no palette".
    SB_U = SB.replace("`pecos #8E4B3A`", "`pecos_mark #8E4B3A`").replace(
        "marked in\n    pecos,", "marked in\n    pecos_mark,")
    with tempfile.TemporaryDirectory() as d2:
        dd2 = Path(d2)
        (dd2 / "slide-05.html").write_text(
            "<style>.q{color:#23202B}</style><div>One office. The same day. Two wordings.</div>",
            encoding="utf-8")
        f, w, s = check(SB_U, dd2, REPORT)
        ok("a frame whose plan declares an UNDERSCORED colour and draws none is CAUGHT",
           any("pecos_mark" in x and "does not contain" in x for x in f), str(f))
        ok("...and the declared-colour check is not reported as unable to run",
           not any("defines no `name #HEX` palette" in x for x in w), str(w))
        (dd2 / "slide-05.html").write_text(
            "<style>.d{color:#8E4B3A}.p{background:#F6F1E4}</style>"
            "<div>One office. The same day. Two wordings.</div>", encoding="utf-8")
        f, w, s = check(SB_U, dd2, REPORT)
        ok("...and the same frame with that colour drawn passes", not f, str(f))

    # ---- THE CLAIM SET, FOUR DECLARATIONS OF ONE THING (2026-09-07) --------------------
    #
    # Replays the two findings the integrity judge made in two consecutive rounds of carousel
    # no. 17: three frames whose strip disagreed with the dossier that declared it, and then,
    # after those three were repaired, slide 3's labels and slide 8's numerals doing the same.
    with tempfile.TemporaryDirectory() as d3:
        dd3 = Path(d3)
        (dd3 / "slide-05.html").write_text(GOOD, encoding="utf-8")
        NODES = [{"text": "One office. The same day."}, {"text": "Two wordings."},
                 {"text": "05 / 09"}, {"text": "PARALLAX"}]

        def rep(strip):
            return {"slides": [{"file": "slide-05.html",
                                "text_nodes": NODES + [{"text": t} for t in strip]}]}

        agree = rep(["c1 c4"])
        copy_ok = {"slides": {"S5": {"hook": "One office. The same day.",
                                     "claims": ["c1", "c4"]}}}
        f, w, s = check(SB, dd3, agree, copy_ok, {"c1", "c4", "c7"})
        ok("a frame whose plan, copy and strip name one set passes", not f, str(f))
        ok("...and both surfaces were actually compared, rather than skipped",
           s.get("claims_compared") == 2, str(s))

        f, _w, _s = check(SB, dd3, rep(["c1"]), copy_ok, None)
        ok("a claim strip that drops one of the plan's claims is CAUGHT",
           any("claim strip" in x and "absent there c4" in x for x in f), str(f))

        f, _w, _s = check(SB, dd3, rep(["c1 c4 c7"]), copy_ok, None)
        ok("...and a strip carrying a claim the plan never declared is CAUGHT too",
           any("absent from the plan c7" in x for x in f), str(f))

        f, _w, _s = check(SB, dd3, agree, {"slides": {"S5": {"claims": ["c1"]}}}, None)
        ok("copy.json's claim list drifting from the plan is CAUGHT",
           any("copy.json" in x and "absent there c4" in x for x in f), str(f))

        # ONE FINDING PER FRAME when both surfaces drift together, which is six of the nine
        # frames the seventeen deck replay names. Two lines about one drift is how a run learns
        # to scroll past the tenth warning.
        f, _w, _s = check(SB, dd3, rep(["c1"]), {"slides": {"S5": {"claims": ["c1"]}}}, None)
        ok("...and a drift on both surfaces is one finding naming both",
           len([x for x in f if "the dossier declares" in x]) == 1
           and all(k in f[0] for k in ("claim strip", "copy.json")), str(f))

        # A STRIP SPLIT ACROSS FOUR NODES IS ONE STRIP. 2026-08-19's slide 8 renders c3, c19,
        # c20 and c21 as four separate text nodes. Reading the first node alone would report
        # that correct frame as citing one claim, which is a gate inventing a failure.
        f, _w, _s = check(SB, dd3, rep(["c1", "c4"]), copy_ok, None)
        ok("a strip split across separate text nodes is read as one strip", not f, str(f))

        # AND A SENTENCE ABOUT A CLAIM IS NOT A STRIP. 2026-08-16's slide 3 prints
        # "THE PLANT IS ANNOUNCED. NOTHING IS BUILT.CLAIM c7. QUOTED VERBATIM."
        ok("a sentence naming a claim id is not a citation strip",
           rendered_claim_ids(["THE PLANT IS ANNOUNCED.CLAIM c7. QUOTED VERBATIM."]) is None)
        ok("...and a frame that prints no ids at all reports None, not an empty set",
           rendered_claim_ids(["One office."]) is None)

        # THE NUMERAL HALF, which is what the judge found on slide 8 the round AFTER the strips
        # were repaired. A figure sourced from a claim the slide does not stand on.
        SBN = SB.replace("claims: [c1, c4]",
                         "claims: [c1, c4]\nnumerals:\n  - value_from: c7     # seven years")
        f, _w, _s = check(SBN, dd3, agree, copy_ok, {"c1", "c4", "c7"})
        ok("a numeral sourced from a claim outside the slide's own list is CAUGHT",
           any("sources a numeral from c7" in x for x in f), str(f))
        SBN2 = SB.replace("claims: [c1, c4]",
                          "claims: [c1, c4]\nnumerals:\n  - value_from: c4     # seven years")
        f, _w, _s = check(SBN2, dd3, agree, copy_ok, {"c1", "c4"})
        ok("...and a numeral sourced from a claim the slide declares is clean", not f, str(f))
        SBN3 = SB.replace("claims: [c1, c4]", "claims: [c1, c4]\nnumerals: []")
        f, _w, _s = check(SBN3, dd3, agree, copy_ok, {"c1", "c4"})
        ok("...and `numerals: []`, a frame that prints no figure, is not a hole", not f, str(f))

        # THE PLAN'S OWN IDS HAVE TO EXIST. label_guard asks this of the ids a frame PRINTS and
        # cannot see a plan-only id on a frame that prints no strip.
        f, _w, _s = check(SB, dd3, agree, copy_ok, {"c1"})
        ok("a dossier citing a claim claims.json does not hold is CAUGHT",
           any("claims.json holds no such claim" in x for x in f), str(f))

        # THE EMPTY CASE FAILS, because a comparison that compared nothing prints the same line
        # as a clean one. Nothing in this suite has ever asked for the field the dossier spec
        # defines on its line 19.
        f, _w, _s = check(SB.replace("claims: [c1, c4]\n", ""), dd3, agree, copy_ok, None)
        ok("a storyboard whose dossiers declare no claims at all FAILS",
           any("declares a `claims:` list" in x for x in f), str(f))
        f, w, _s = check(SB.replace("claims: [c1, c4]", "claims: []"), dd3, agree, copy_ok, None)
        ok("...and a `claims:` key nothing parses out of is reported, never read as absent",
           any("compared against nothing" in x for x in w), str(w))

    # AGAINST THE SHIPPED ARTIFACTS, because a fixture written by the author of the detector
    # agrees with the detector. That is GATE_LESSONS
    # entry 16 ("Fixtures written by the author of the detector agree with it").
    # 2026-09-05's slide 1 declares `c18, c17` and
    # both its frame and its copy say `c18` alone, measured before this was written. 2026-09-07
    # is the deck that repaired five of these by hand and has to come back silent.
    for date, want in (("2026-09-05", True), ("2026-09-07", False)):
        p = REPO_ROOT / "runs" / "carousel" / date
        if not ((p / "storyboard.md").exists() and (p / "render_report.json").exists()):
            continue
        _copy = json.loads((p / "copy.json").read_text(encoding="utf-8")) \
            if (p / "copy.json").exists() else None
        f, _w, st = check((p / "storyboard.md").read_text(encoding="utf-8"), p / "slides",
                          json.loads((p / "render_report.json").read_text(encoding="utf-8")),
                          _copy, None)
        drift = [x for x in f if "the dossier declares" in x]
        ok(f"{date}: the claim sets {'drift' if want else 'agree'} on the shipped deck",
           bool(drift) == want, str(drift)[:200])
        ok(f"{date}: every frame's claim set was compared on both surfaces",
           st.get("claims_compared") == 2 * st.get("claim_slides", 0),
           f"compared={st.get('claims_compared')} slides={st.get('claim_slides')}")

    # CALIBRATION against every shipped storyboard, so a parser that stops reading the form
    # these runs write reports itself as a number rather than as silence. This is the assertion
    # that would have gone red on 2026-08-22, the first deck to declare a palette as a table.
    for p in sorted((REPO_ROOT / "runs" / "carousel").glob("2*")):
        if not (p / "storyboard.md").exists():
            continue
        pm = palette_map((p / "storyboard.md").read_text(encoding="utf-8"))
        ok(f"{p.name}: its declared palette is readable", len(pm) >= 5, f"read {sorted(pm)}")
    # THE DECLARED LIBRARY (2026-08-26). Slide 1 carried a Zdog scene it never drew, for three
    # rounds, with every gate green, because nothing read the dossier against the slide.
    _zdog = ('art:\n  technique: "Zdog scene, rounded extrusion with a real depth axis"\n'
             '  why_this_technique: >\n    Zdog builds it natively in vector.\n')
    ok("a dossier naming Zdog is seen to name it", declared_libraries(_zdog) == ["zdog"],
       str(declared_libraries(_zdog)))
    ok("...and a slide loading only noise.js does not satisfy it",
       "zdog" not in slide_sources('<script src="@@ASSETS@@/js/noise.js"></script>'))
    ok("...while a slide that loads it does",
       "zdog" in slide_sources('<script src="@@ASSETS@@/js/zdog.dist.js"></script>'))
    ok("a dossier naming no library declares none",
       declared_libraries('art:\n  technique: "flat elevation, axis aligned rects"\n') == [])
    ok("d3 and topojson are each their own claim",
       declared_libraries('art:\n  technique: "d3 geoAlbers over topojson counties"\n')
       == ["d3", "topojson"])
    ok("a word merely containing a library name is not a claim",
       declared_libraries('art:\n  technique: "three quarter camera on a threaded rod"\n') == [])

    # A POSSESSIVE IS NOT A QUOTE (2026-08-26). The loose delimiters failed a correct frame.
    _poss = ("all four title cells carry their applicant's name, because the county's own "
             "matter titles hold four")
    ok("a possessive apostrophe does not open a required string",
       not [m.group(2) for m in REQUIRED_STR.finditer(_poss)],
       str([m.group(2) for m in REQUIRED_STR.finditer(_poss)]))
    ok("...and a real single quoted needle is still read",
       [m.group(2) for m in REQUIRED_STR.finditer("the frame carries 'base load' at the foot")]
       == ["base load"])
    ok("...and a double quoted needle is still read",
       [m.group(2) for m in REQUIRED_STR.finditer('the frame reads "two public hearings" plainly')]
       == ["two public hearings"])
    ok("mismatched marks are not a quote",
       not [m.group(2) for m in REQUIRED_STR.finditer("""the frame carries "base load' here""")])
    ok("a possessive does not create a forbidden needle either",
       not forbidden_needles("no cell carries the county's own internal matter number"))
    ok("...while a real forbidden needle still fires",
       forbidden_needles("no legend label names 'base load'") == ["base load"])

    # ---- THE MEASURED COLUMN PALETTE, UNDER A BOLD LEAD (2026-09-16) -------------------
    #
    # THE DEFECT. Carousel no. 26 declared seven colours, measured each against the last eight
    # decks, and wrote them as an indented column table under `**Palette, MEASURED rather than
    # chosen by eye.**`. There is no markdown heading in that deck's art section, so
    # `palette_sections` found nothing, `palette_map` read zero tokens, and the declared-colour
    # half of this gate did not run on that deck at all. The run then REORDERED the columns mid
    # run, which is how both shapes below come to be real.
    _PAL = (
        "**Palette, MEASURED rather than chosen by eye.** The arithmetic is in the run.\n"
        "\n"
        "    bond       #BBC0C6  L* 76   the copy stock and the deck's most common value  dE 10.59\n"
        "    fed_blue   L* 14   #00205B   THE ACCENT, PMS 281 C, `flag_blue` in brand.yaml dE 24.32\n"
        "\n"
        "`fed_blue` is dark against a pale stock on purpose. Flag red `#BF0A30` is UNSPENT.\n"
        "\n"
        "**Camera and light.** A seated public eye at 1.10 m.\n")
    pm = palette_map(_PAL)
    ok("a bold lead line anchors a palette section, which is what 2026-09-16 wrote",
       pm.get("bond") == "#BBC0C6", str(pm))
    ok("...and the measured column table reads in EITHER column order",
       pm.get("fed_blue") == "#00205B", str(pm))
    ok("...and an unindented backticked hex in the paragraph below is not a token",
       "red" not in pm and "#BF0A30" not in pm.values(), str(pm))
    ok("...and the span stops at the next bold lead, so the camera paragraph is not palette",
       len(palette_sections(_PAL)) == 1
       and "Camera and light" not in palette_sections(_PAL)[0], str(palette_sections(_PAL)))
    ok("a storyboard with neither anchor still declares no palette rather than inventing one",
       palette_map("The ground is `#B4903F` in most frames.") == {})

    # ---- THE FRAME'S OWN MEDIAN BAND (2026-09-16, carousel no. 26) ----------------------
    #
    # THE DEFECT. Nine dossiers declared a median L* band at 432px, the run measured all nine
    # medians into `measured_arc.json`, nothing compared the two, and FIVE OF NINE frames shipped
    # to a scoring panel outside their own declared band while the storyboard asserted in prose
    # that every one was inside. The panel came back under the bar on all three lenses.
    #
    # THE PARSER FIRST, and the discrimination before the agreement. Every string below is taken
    # off a real shipped storyboard rather than written for this test, because a fixture written
    # by the author of the detector agrees with the detector (GATE_LESSONS 16).
    b = parse_band("the frame's median L* at 432px is between 36 and 52")
    ok("a between band reads, with its size", b and (b["lo"], b["hi"], b["size"]) == (36, 52, (432, None)), str(b))
    b = parse_band("the frame's median L* at 432px is 60 or higher")
    ok("an open-topped band reads", b and (b["lo"], b["hi"]) == (60, None), str(b))
    b = parse_band("the frame's median L* at 432px is 28 or lower")
    ok("an open-bottomed band reads", b and (b["lo"], b["hi"]) == (None, 28), str(b))
    b = parse_band("the frame median L* measures 34 plus or minus 8 on the 270 by 338 grid")
    ok("a plus or minus band reads on its own grid",
       b and (b["lo"], b["hi"], b["size"]) == (26, 42, (270, 338)), str(b))

    # THE TRAILING CLAUSE IS NOT PART OF THE BAND. Both of these shipped.
    b = parse_band("the frame's median L* at 432px is 45 or higher, which is at least 18 above "
                   "the deck median")
    ok("a band stops at the clause that starts talking about the deck",
       b and (b["lo"], b["hi"]) == (45, None), str(b))
    b = parse_band("this frame's median L* is above 80 and it is the only frame in the deck "
                   "above 60")
    ok("...and `and it is` ends the assertion, so 60 is not read as a ceiling",
       b and (b["lo"], b["hi"], b["lo_strict"]) == (80, None, True), str(b))

    # A REGION'S MEDIAN IS NOT THE FRAME'S. Every one of these is a real acceptance item, and
    # reading any of them as the frame's band would invent a number the plan does not contain.
    for region in (
            "the punch column's median L* is at least 10 below the rail face median at 432px wide",
            "all four castors carry a contact shadow whose median L* differs from the floor "
            "beside it by 4 or more",
            "the two regions' median L* differ by LESS than 2, measured at 432px",
            "a `rim_light` band at least 30 px tall runs unbroken across 60 percent or more of "
            "the horizon, and its median L* is at least 25 above the land beneath it",
            "the median L* of the chassis top faces is at least 15 below the median of their "
            "front faces"):
        ok(f"a region median is not read as the frame's ({region[:34]}...)",
           parse_band(region) is None, str(parse_band(region)))

    # INCLUSIVE AND STRICT ARE DIFFERENT BOUNDS, and folding one into the other would widen a
    # band its author chose.
    ok("`60 or higher` admits exactly 60",
       in_band(60.0, parse_band("the frame's median L* at 432px is 60 or higher")))
    ok("...and `above 60` does not",
       not in_band(60.0, parse_band("the frame's median L* at 432px is above 60")))

    # THE THIRD STATE. A declaration nobody could read must not print the same line as an item
    # that declares nothing. `panel_ready.unreadable_plan` is this same finding one gate over.
    b = parse_band("this frame's median L* is the highest of the nine, measured off the render")
    ok("a frame median sentence with no band in it is reported, not read as prose",
       b is not None and b["lo"] is None and b["hi"] is None, str(b))
    b = parse_band("the frame's median L* measures above 70")
    ok("...and a band with no stated measurement size is reported as unsettleable",
       b is not None and b["lo"] == 70 and b["size"] is None, str(b))

    # THE MEASUREMENT ITSELF, against a value that is not ours. sRGB 128 is a standard mid grey
    # and its CIE L* is 53.6 by the sRGB transfer function, and sRGB 64 is 27.1. If this ever
    # drifts, the instrument moved rather than the deck.
    with tempfile.TemporaryDirectory() as dband:
        bd = Path(dband) / "slides"
        bd.mkdir()
        try:
            from PIL import Image as _Im
            _Im.new("RGB", (1080, 1350), (128, 128, 128)).save(
                Path(dband) / "slide-01.png")
            _Im.new("RGB", (1080, 1350), (64, 64, 64)).save(Path(dband) / "slide-02.png")
            have_pil = True
        except Exception as exc:                                     # noqa: BLE001
            have_pil = False
            ok("Pillow is installed, because this gate measures pixels", False, str(exc))
        if have_pil:
            got = median_lstar(Path(dband) / "slide-01.png", (432, None))
            ok("a 50 percent sRGB grey measures L* 53.6", abs(got - 53.6) < 0.1, str(got))
            ok("...and sRGB 64 measures 27.1",
               abs(median_lstar(Path(dband) / "slide-02.png", (432, None)) - 27.1) < 0.1)
            ok("...and `at 432px` takes its height from the frame's own aspect",
               median_lstar(Path(dband) / "slide-01.png", (432, 540)) == got)

            BAND_SB = """
```yaml
slide: 1
type:
  hook: "A hook."
  dek: "A dek."
claims: [c1]
art:
  value_structure: >
    Every frame in this deck is inside its own range.
acceptance:
  - "the frame's median L* at 432px is between 24 and 36"
```
"""
            RPT = {"slides": [{"file": "slide-01.html",
                               "text_nodes": [{"text": "A hook."}, {"text": "A dek."},
                                              {"text": "c1"}]}]}
            f, w, s = check(BAND_SB, bd, RPT, None, {"c1"})
            ok("A FRAME OUTSIDE ITS OWN DECLARED BAND IS CAUGHT",
               any("measures median L* 53.6" in x and "24 to 36" in x for x in f), str(f))
            ok("...and the plan asserting every frame is inside its range does not save it",
               any("median L*" in x for x in f), str(f))
            ok("...and the item was counted as checkable rather than as prose",
               s["checkable"] >= 1 and s.get("bands"), str(s))

            inside = BAND_SB.replace("between 24 and 36", "between 44 and 60")
            f2, _w2, s2 = check(inside, bd, RPT, None, {"c1"})
            ok("...while the same frame inside its band is clean",
               not [x for x in f2 if "median L*" in x], str(f2))

            # A CHECK THAT CANNOT RUN IS NOT A CHECK THAT PASSED. GATE_LESSONS 37.
            empty = Path(dband) / "nopix"
            (empty / "slides").mkdir(parents=True)
            f3, _w3, _s3 = check(BAND_SB, empty / "slides", RPT, None, {"c1"})
            ok("a declared band with no render to measure it against FAILS",
               any("no render of this frame could be found" in x for x in f3), str(f3))

            nosize = BAND_SB.replace(" at 432px", "")
            f4, w4, s4 = check(nosize, bd, RPT, None, {"c1"})
            ok("a band with no stated size WARNS and is not counted checkable",
               any("never says at what size" in x for x in w4)
               and not [x for x in f4 if "median L*" in x] and not s4.get("bands"), str(w4))

    # AGAINST THE SHIPPED DECKS, because only a real artifact carries the shapes nobody thought
    # to write down. 2026-09-16 is the deck this was built for and every frame is inside its band
    # after the repair round; 2026-09-08 and 2026-09-10 declare bands in the two other forms.
    swept_bands, band_fails = 0, []
    for p in sorted((REPO_ROOT / "runs" / "carousel").glob("2*")):
        if not ((p / "storyboard.md").exists() and (p / "render_report.json").exists()):
            continue
        f, _w, st = check((p / "storyboard.md").read_text(encoding="utf-8"), p / "slides",
                          json.loads((p / "render_report.json").read_text(encoding="utf-8")))
        swept_bands += len(st.get("bands", []))
        band_fails += [f"{p.name}: {x}" for x in f if "median L*" in x]
    ok(f"every frame band in the shipped corpus holds ({swept_bands} measured)",
       not band_fails, "; ".join(band_fails[:3]))
    ok("...and there were bands to measure, so this is not asleep", swept_bands >= 10,
       str(swept_bands))

    # THE DISCRIMINATION ON REAL PIXELS, not only on a grey square. A shipped frame held to
    # another shipped frame's band has to be refused, or the comparison is measuring nothing.
    live = REPO_ROOT / "runs" / "carousel" / "2026-09-16"
    if (live / "slide-09.webp").exists():
        dark = median_lstar(live / "slide-09.webp", (432, None))
        ok("the deck's closing frame measures its own floor", 10 < dark < 16, str(dark))
        ok("...and holding it to frame 1's `60 or higher` is refused",
           not in_band(dark, parse_band("the frame's median L* at 432px is 60 or higher")))
        ok("...while its own `28 or lower` holds",
           in_band(dark, parse_band("the frame's median L* at 432px is 28 or lower")))

    ok("no hex literal for a brand colour is hardcoded in this module",
       not re.search(r"#(16151C|8E4B3A|D9CDB4|B98D46|4E6B62|EFE9DA)",
                     Path(__file__).read_text(encoding="utf-8").split("def self_test")[0], re.I))

    print("\nplan_render_check self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.date:
        ap.error("--date or --self-test")
    return run(a.date)


if __name__ == "__main__":
    raise SystemExit(main())
