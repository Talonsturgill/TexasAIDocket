#!/usr/bin/env python3
"""craft_floor.py — no frame ships that nobody drew. Measured per slide, not per deck.

WHY THIS EXISTS. 2026-08-19.

Every gate in this suite before it was deck-level or claim-level. Not one looked at a SINGLE FRAME
and asked whether it was worth drawing. That is the hole a frame walked through seven times.

The measurement, off that run's own render report:

    slide-01   variance 3160.7      an August month sheet embossed into limestone
    slide-06   variance 2315.0      four terrazzo inlay bands
    slide-08   variance  674.8      a lit cell throwing a shaft onto a list
    slide-04   variance  533.1      a chart table under a lamp
    slide-05   variance  302.0      a survey sheet on the paper register
    slide-07   variance  223.1      a redaction field
    slide-03   variance  134.4      a Voronoi partition
    slide-02   variance   15.9      twenty six contour lines at five percent alpha

**Slide 2 was two hundred times flatter than slide 1 and broke no rule**, because no rule existed.
It was rebuilt three times over three scoring rounds and the number did not move, because each
rebuild fixed the type layer while the canvas stayed empty. A reviewer found it by hand at round 6.
`artwork_craft` carries 0.28, the heaviest weight in the rubric, and it never once reached the
rubric's own definition of acceptable across the whole run.

WHAT IT MEASURES, AND WHY TWO THINGS RATHER THAN ONE

**Variance alone is not craft.** A frame of pure noise scores high and is worthless, and a gate
that rewarded variance would teach runs to add texture instead of drawing. So this reads two
numbers that are already in the artifacts and asks them different questions:

- `canvases[].variance` from `render_report.json`. Does the frame have a real light and a real dark
  rather than one mid band? This is the rubric's own first question about artwork.
- the per-third craft-cell density `qa.py` computes. Is the detail budgeted across the frame, or is
  the whole drawing in one band with the rest empty?

A frame has to fail BOTH to be a hard fail. A frame that fails one is a warning, because a
deliberately quiet frame is a legitimate move and a gate that fires on a correct decision is a gate
somebody switches off. `coherence_check` carries the same reasoning about display type sizes.

WHERE THE FLOOR COMES FROM

Fitted on shipped work, not invented. The floor is a fraction of the deck's OWN median, so a dark
quiet deck is judged against itself rather than against a bright one, and a deck cannot pass by
being uniformly flat: the absolute floor catches that.

A DECK CAN DRAW EVERY FRAME AND WRITE NO CANVAS AT ALL (2026-09-03).

Deck no. 14 is entirely SVG. Nine frames, nine drawings, and `canvases` empty on every one of
them, so `variance_of` returned 0.0 nine times, the median was 0.0, and this gate divided by it
and raised ZeroDivisionError. A crash is not a verdict. It told the run nothing about the deck
and it would have told a later run nothing either.

The fix is not to exempt an SVG deck, which would hand every future deck a way to opt out of the
one gate that asks whether a frame was drawn. It is to ask the SAME QUESTION of a signal that
exists for SVG. `qa.py` computes the per-third craft-cell density on every frame whatever drew
it, so when a deck writes no canvas anywhere, the mean of those three bands becomes the measured
quantity and the relative floor works exactly as before, against the deck's own median.

What that costs, stated rather than hidden: band density answers "is there detail here" and not
"does this frame have a real light and a real dark", so on an SVG deck this gate is measuring the
weaker of the two questions it normally asks. The report says so on the line where it happens.

    craft_floor.py --date 2026-08-19
    craft_floor.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------------------------
# A FRAME THAT FETCHES AT RENDER TIME DRAWS NOTHING AND SAYS NOTHING (2026-09-23, carousel no. 32)
#
# THE DEFECT, measured against a shipped slide rather than reasoned about. A frame drew the state
# outline and the county mesh with
#
#     fetch("@@ASSETS@@/geo/tx-counties.topo.json")
#
# and the render harness opens a slide over the FILE PROTOCOL, where that promise rejects. The
# frame rendered in 384 ms, `render_report.json` recorded **zero errors and zero warnings**, and
# the canvas had nothing on it. A `.catch()` that logs, or an `await` inside a handler nobody
# awaits, is all it takes for the rejection to leave no trace anywhere a gate can read.
#
# WHY THIS BELONGS BESIDE THE VARIANCE FLOOR AND NOT IN A GATE OF ITS OWN. The floor above is the
# only thing in this suite that would ever notice, and it notices only the extreme case: a frame
# whose ENTIRE drawing came out of one fetch measures flat and fails here. A frame that draws its
# type, its furniture and its bench in code and gets only its GEOGRAPHY from a fetch measures
# perfectly healthy with the subject missing, which is the shape that shipped. So this catches the
# CAUSE and the floor below catches the one consequence it can see. GATE_LESSONS 43's chain.
#
# THE RULE IS ABOUT THE CALL, NOT THE URL, and that is deliberate. A slide may reference any
# committed asset it likes through `<script src>`, `<link href>` or an `<img>`: the harness
# resolves those to real file paths and the browser loads them, which is why every deck here runs
# ten of them. What no slide may do is ask the FETCH API to go and get something while it draws.
#
# **XMLHttpRequest IS NOT THIS, AND THAT IS A MEASUREMENT RATHER THAN A CONCESSION.** The first
# cut of this rule swept XHR too, on the reasonable-sounding grounds that a network call is a
# network call, and the replay over the shipped corpus turned it red on four decks that drew
# their maps perfectly. Carousel no. 25's frame 8 says why, in its own source, and it was right:
#
#     "XHR rather than fetch: Chromium refuses the Fetch API on a file:// URL whatever
#      --allow-file-access-from-files says, and that flag DOES cover XHR."
#
# So XHR is the WORKAROUND this project already found for this exact defect, four decks deep,
# and a gate that banned it would have refused the repair and left only the broken route. This
# is the shape CLAUDE.md warns about on the push defect: **a wrong explanation is worse than
# none, because the next session inherits it and stops looking.** The corpus is what caught it.
#
# `d3.json` and its siblings ARE this, because d3-fetch is the Fetch API with a parser bolted on.
# A dynamic `import()` is too, because a module graph over file:// is refused for the same
# origin reason. A STATIC `import x from "..."` is resolved by the loader the way `<script src>`
# is, so the lookbehind refuses the keyword form rather than the whole word.
#
# THE FIX THE RUN ALREADY FOUND, so the message can name it: pre-project the geometry into the
# slide at build time. Carousel no. 32 did exactly that for the outline, the county mesh and the
# place marks, with a script under its own `tmp/`, and the frame drew.
NETWORK_CALLS = [
    (re.compile(r"\bfetch\s*\("), "fetch()"),
    (re.compile(r"\bd3\s*\.\s*(?:json|csv|tsv|text|xml|buffer|image)\s*\("), "a d3 fetch loader"),
    (re.compile(r"(?<![.\w$])import\s*\("), "a dynamic import()"),
]


def strip_comments(src: str) -> str:
    """HTML, block and line comments out, so a slide may DESCRIBE the trap without tripping it.

    Carousel no. 32's frame 8 carries a comment reading `fetch("@@ASSETS@@/geo/...")` to explain
    why its geometry is inline. That comment is the repair being documented at the site of the
    defect, which is the habit this whole repo runs on, and a gate that punished it would teach
    the next run to delete the explanation.

    THE TRAP INSIDE THE STRIPPER, which is why the line-comment arm has a lookbehind and a
    self-test case: `https://example.com` contains `//` and a naive rule deletes the rest of the
    line, taking any real call after it with it. A stripper that eats the code is a gate that
    goes quiet, which is worse than one that never existed.
    """
    out = re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    out = re.sub(r"/\*.*?\*/", " ", out, flags=re.S)
    out = re.sub(r"(?m)(?<![:\w'\"/`])//[^\n]*$", " ", out)
    return out


def network_calls(slides_dir: Path) -> tuple[list, int]:
    """(findings, slides read). A finding per (file, kind, line)."""
    found, n = [], 0
    for f in sorted(slides_dir.glob("slide-*.html")):
        n += 1
        src = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
        for rx, kind in NETWORK_CALLS:
            for m in rx.finditer(src):
                line = src.count("\n", 0, m.start()) + 1
                frag = src[m.start():m.start() + 72].split("\n")[0].strip()
                found.append(
                    f"{f.name}:{line} calls {kind} while the frame draws: {frag!r}. The render "
                    f"harness opens a slide over file://, where Chromium REFUSES the Fetch API "
                    f"whatever --allow-file-access-from-files says, and a frame that swallows "
                    f"the rejection renders clean with nothing on it. On 2026-09-23 that was "
                    f"384 ms, zero errors, zero warnings and an empty canvas. PRE-PROJECT the "
                    f"data into the slide at build time and draw from the literal, which is what "
                    f"that run did for the outline, the county mesh and the place marks. XHR is "
                    f"the other route and that flag DOES cover it. A committed asset reached "
                    f"through <script src> or <link href> is fine and is not this")
    return found, n

# RELATIVE FLOOR. A frame carrying less than this fraction of its own deck's median tonal range is
# not the same kind of object as the frames around it. Fitted on the three decks shipped to
# 2026-08-19: within a deck the ratio of the weakest frame to the median ran 0.05 on the deck that
# had the defect and stayed above 0.30 on the frames nobody complained about.
RELATIVE = 0.18

# ABSOLUTE FLOOR, so a uniformly flat deck cannot pass by having a flat median. Slide 2 measured
# 15.9 and slide 3, the next weakest and merely thin rather than empty, measured 134.4.
ABSOLUTE = 60.0

# A frame whose craft sits in one band with the rest empty. qa.py already reports this per third.
BAND_MIN = 0.04


def slides(report: dict) -> list:
    return report.get("slides") or []


def variance_of(slide: dict) -> float:
    """The tonal range of the frame's art. 0 when a slide draws no canvas at all."""
    cvs = slide.get("canvases") or []
    if not cvs:
        return 0.0
    return max(float(c.get("variance") or 0.0) for c in cvs)


def bands_of(qa_slide: dict) -> list:
    """Craft-cell density per third, if machine QA recorded it.

    THE CONTRACT, and the bug it is written against. qa.py's frame_balance() computes these
    three numbers on every slide and, until 2026-08-19, formatted them into a warning string
    and discarded them. This function looked for them and always got nothing, so `bands` was
    always empty, `lopsided` was always False, and the `thin and (lopsided or not bands)`
    branch below made EVERY thin frame a hard fail. The WARN tier three lines under it, the
    one that lets a deliberately quiet frame through, was unreachable dead code from the day
    this file was written.

    The self-test below already asserted that tier worked, and passed, every time, because it
    built its own qa dict WITH the key. The logic was never wrong. The data never arrived and
    nothing compared the two files. So the assertion that matters now reads a REAL shipped
    machine_qa.json and checks the producer actually writes what this reads.

    Third time in this repo a consumer read a key its producer does not write, after
    gate_status and email_check both missed `weighted_score`.
    """
    for k in ("bands", "thirds", "craft_bands"):
        v = qa_slide.get(k)
        if isinstance(v, (list, tuple)) and len(v) == 3:
            return [float(x) for x in v]
    return []


def check(report: dict, qa: dict | None = None) -> tuple[list, list, dict]:
    """Fails, warns, and the measurement, so a reader sees the distribution rather than a verdict."""
    rows = []
    for s in slides(report):
        rows.append({"file": s.get("file") or s.get("png") or "?", "variance": variance_of(s)})
    if not rows:
        return (["craft_floor: the render report lists no slides"], [], {})

    qa_by = {}
    for s in (slides(qa) if qa else []):
        qa_by[s.get("file") or s.get("png") or "?"] = s

    # AN ALL SVG DECK WRITES NO CANVAS, and the question still has to be asked. See the header.
    # The band densities qa.py already computes are the substitute, and the units change with
    # them, so the absolute floor cannot come along.
    signal = "canvas variance"
    if not any(r["variance"] > 0 for r in rows):
        signal = "band density"
        for r in rows:
            b = bands_of(qa_by.get(r["file"], {}))
            r["variance"] = (sum(b) / len(b)) if b else 0.0

    vals = [r["variance"] for r in rows]
    median = statistics.median(vals)
    if median <= 0:
        return ([f"craft_floor: every frame measures zero on {signal} and on band density too, so "
                 f"nothing here was drawn or nothing was measured. Neither is a deck that ships"],
                [], {"median": 0.0, "floor": 0.0, "rows": rows, "signal": signal})
    rel_floor = median * RELATIVE
    floor = max(ABSOLUTE, rel_floor) if signal == "canvas variance" else rel_floor

    fails, warns = [], []
    for r in rows:
        thin = r["variance"] < floor
        bands = bands_of(qa_by.get(r["file"], {}))
        lopsided = bool(bands) and min(bands) < BAND_MIN
        r["thin"], r["lopsided"] = thin, lopsided
        if thin and (lopsided or not bands):
            fails.append(
                f"{r['file']}: {signal} {r['variance']:.4g} against a floor of {floor:.4g}. "
                f"This frame carries {r['variance'] / median * 100:.0f} percent of the deck's own "
                f"median tonal range, so it is not the same kind of object as the frames around it. "
                f"Draw it or cut it. Do not answer this by adding texture")
        elif thin:
            warns.append(f"{r['file']}: {signal} {r['variance']:.4g} against a floor of "
                         f"{floor:.4g}, but its detail is spread across the frame. A deliberately "
                         f"quiet frame is a legitimate move. Confirm it is one")
    return fails, warns, {"median": median, "floor": floor, "rows": rows, "signal": signal}


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            fails += 1

    def rep(vals):
        return {"slides": [{"file": f"slide-{i + 1:02d}.html",
                            "canvases": [{"variance": v}]} for i, v in enumerate(vals)]}

    # THE 2026-08-19 DECK, as it actually measured, to the tenth.
    REAL = [3160.7, 15.9, 134.4, 533.1, 302.0, 2315.0, 223.1, 674.8]
    f, w, m = check(rep(REAL))
    ok("the frame nobody drew is CAUGHT", any("slide-02" in x for x in f), str(f))
    ok("...and it is the only hard fail in that deck", len(f) == 1, str(f))
    ok("...and the message names the measurement and the floor",
       f and "15.9" in f[0] and "floor" in f[0], str(f))
    ok("...and it refuses the wrong fix by name",
       f and "adding texture" in f[0], str(f))
    ok("the frames a reviewer never complained about all pass",
       not any(n in x for n in ("slide-01", "slide-04", "slide-06", "slide-08") for x in f), str(f))

    # The rebuilt slide 2 measured 334.6 and must clear.
    fixed = list(REAL); fixed[1] = 334.6
    f2, _, _ = check(rep(fixed))
    ok("...and the same frame passes once it is actually drawn", f2 == [], str(f2))

    # A UNIFORMLY FLAT DECK MUST NOT PASS BY HAVING A FLAT MEDIAN. This is what the absolute
    # floor is for, and a relative-only rule would wave this through.
    f3, _, _ = check(rep([12.0, 11.0, 13.0, 10.0, 12.5, 11.5, 12.2, 10.8]))
    ok("a deck that is flat all the way through is CAUGHT, not normalised away", len(f3) == 8,
       str(len(f3)))

    # A slide that draws no canvas at all.
    f4, _, _ = check({"slides": [{"file": "a.html", "canvases": []},
                                 {"file": "b.html", "canvases": [{"variance": 900}]},
                                 {"file": "c.html", "canvases": [{"variance": 800}]}]})
    ok("a slide with no canvas at all is CAUGHT", any("a.html" in x for x in f4), str(f4))

    # A QUIET FRAME WITH ITS DETAIL SPREAD IS A WARNING, NOT A FAIL. A gate that fires on a
    # correct decision gets switched off, which is coherence_check's own stated reasoning.
    quiet = rep([3000, 100, 900, 800, 700, 600, 500, 400])
    qa_spread = {"slides": [{"file": "slide-02.html", "bands": [0.30, 0.28, 0.31]}]}
    f5, w5, _ = check(quiet, qa_spread)
    ok("a quiet frame whose detail is spread is a WARN rather than a FAIL",
       not any("slide-02" in x for x in f5) and any("slide-02" in x for x in w5), str((f5, w5)))
    qa_lop = {"slides": [{"file": "slide-02.html", "bands": [0.30, 0.0, 0.01]}]}
    f6, _, _ = check(quiet, qa_lop)
    ok("...and the same frame with its craft in one band IS a fail",
       any("slide-02" in x for x in f6), str(f6))

    # ---- A DECK THAT WRITES NO CANVAS AT ALL (2026-09-03) -------------------------------
    # Deck no. 14 was entirely SVG and this gate raised ZeroDivisionError on it. A crash tells a
    # run nothing, so the same question is now asked of the band densities qa.py records for
    # every frame whatever drew it. These four cases are the proof it still goes red.
    svg_rep = {"slides": [{"file": "s%d.html" % i, "canvases": []} for i in range(1, 6)]}
    svg_qa_ok = {"slides": [{"file": "s%d.html" % i, "bands": [0.30, 0.28, 0.31]}
                            for i in range(1, 6)]}
    f7, w7, m7 = check(svg_rep, svg_qa_ok)
    ok("an all SVG deck no longer crashes this gate", True)
    ok("...and a drawn one passes", f7 == [] and w7 == [], str((f7, w7)))
    ok("...measured on band density rather than on a canvas that is not there",
       m7.get("signal") == "band density", str(m7.get("signal")))

    svg_qa_empty = {"slides": [{"file": "s1.html", "bands": [0.0, 0.005, 0.0]}] +
                              [{"file": "s%d.html" % i, "bands": [0.30, 0.28, 0.31]}
                               for i in range(2, 6)]}
    f8, _, _ = check(svg_rep, svg_qa_empty)
    ok("...and an SVG frame nobody drew is STILL CAUGHT",
       any("s1.html" in x for x in f8), str(f8))

    f9, _, _ = check(svg_rep, {"slides": [{"file": "s%d.html" % i, "bands": [0.0, 0.0, 0.0]}
                                          for i in range(1, 6)]})
    ok("...and a deck where nothing was drawn or nothing was measured is an error",
       f9 != [] and "nothing" in f9[0], str(f9))

    ok("an empty report is an error rather than a pass", check({})[0] != [])
    ok("the floor is fitted, not typed into a slide's own file",
       0.0 < RELATIVE < 1.0 and ABSOLUTE > 0)
    ok("...and the measurement is returned so a reader sees the distribution",
       "rows" in m and len(m["rows"]) == 8 and "median" in m)

    # ---- THE PRODUCER WRITES WHAT THIS GATE READS (2026-08-19) --------------------------
    # THE ASSERTION THAT WOULD HAVE CAUGHT THE BUG. Every other case in this file builds its
    # own qa dict with the key already in it, which is exactly why they all passed for the
    # entire life of a dead WARN tier. This one reaches across to the PRODUCER and checks the
    # link itself, so removing the write in qa.py turns this file red.
    _qa_src = REPO_ROOT / ".claude" / "skills" / "carousel-engine" / "qa.py"
    if _qa_src.exists():
        _src = _qa_src.read_text(encoding="utf-8")
        _writes = any(f'res["{k}"]' in _src or f"res['{k}']" in _src
                      for k in ("bands", "thirds", "craft_bands"))
        ok("qa.py PERSISTS the per-third bands this gate reads",
           _writes,
           "qa.py assigns none of bands/thirds/craft_bands onto its slide record, so "
           "bands_of() always returns [] and the WARN tier is dead again")
    else:
        print("  note  qa.py not found, so the producer contract was not checked")

    # ---- A RENDER-TIME FETCH IS AN EMPTY FRAME (2026-09-23) -----------------------------
    #
    # THE DEFECT AS IT WAS MEASURED, verbatim. Written into a scratch slide under out/, never
    # /tmp, because this repo's scratch never leaves the working tree.
    import tempfile
    scratch = REPO_ROOT / "out" / "craft_floor"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        sd = Path(td)
        (sd / "slide-01.html").write_text(
            "<html><script>\n"
            'const topo = await fetch("@@ASSETS@@/geo/tx-counties.topo.json").then(r=>r.json());\n'
            "draw(topo);\n</script></html>", encoding="utf-8")
        hits, n = network_calls(sd)
        ok("the 2026-09-23 defect, verbatim, is CAUGHT", len(hits) == 1 and n == 1, str(hits))
        ok("...and the finding names the file, the line and the call",
           bool(hits) and "slide-01.html:2" in hits[0] and "fetch()" in hits[0], str(hits))
        ok("...and names the repair the run actually used",
           bool(hits) and "PRE-PROJECT" in hits[0], str(hits))

        # THE FORM A SLIDE IS ALLOWED TO USE. Every deck here loads ten committed assets through
        # <script src>, and a rule that swept those would fail every correct frame ever drawn.
        (sd / "slide-01.html").write_text(
            '<html><head><link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">\n'
            '<script src="@@ASSETS@@/js/txscene.js"></script></head>\n'
            '<body><img src="@@ASSETS@@/art/mark.png"></body></html>', encoding="utf-8")
        ok("a committed asset reached through src or href is not a render-time call",
           network_calls(sd)[0] == [], str(network_calls(sd)[0]))

        # THE COMMENT THAT DOCUMENTS THE TRAP MUST NOT TRIP IT, which is carousel no. 32's own
        # frame 8. Nor may the stripper eat live code: a protocol-relative or https URL carries
        # `//` and a naive line-comment rule deletes everything after it.
        (sd / "slide-01.html").write_text(
            "<html>\n<!-- never fetch() a committed asset here -->\n<script>\n"
            '/* `fetch("@@ASSETS@@/geo/tx.json")` is the pattern this frame refuses */\n'
            "// and neither does XMLHttpRequest\n"
            'const SRC = "https://texasaidocket.com/x";  // the site, for the footer\n'
            "</script></html>", encoding="utf-8")
        ok("a comment describing the trap does not trip it",
           network_calls(sd)[0] == [], str(network_calls(sd)[0]))
        (sd / "slide-01.html").write_text(
            "<html><script>\n"
            'const SITE = "https://texasaidocket.com/"; fetch(SITE + "d.json");\n'
            "</script></html>", encoding="utf-8")
        ok("...and a URL's own slashes do not hide a real call after them",
           len(network_calls(sd)[0]) == 1, str(network_calls(sd)[0]))

        # A STATIC MODULE IMPORT IS NOT A RUNTIME GET. Only the dynamic call form is.
        (sd / "slide-01.html").write_text(
            '<html><script type="module">\nimport {draw} from "@@ASSETS@@/js/txscene.js";\n'
            "draw();\n</script></html>", encoding="utf-8")
        ok("a static module import is not a render-time call",
           network_calls(sd)[0] == [], str(network_calls(sd)[0]))
        (sd / "slide-01.html").write_text(
            '<html><script type="module">\nconst m = await import("@@ASSETS@@/js/late.js");\n'
            "</script></html>", encoding="utf-8")
        ok("...and a dynamic import() is",
           len(network_calls(sd)[0]) == 1, str(network_calls(sd)[0]))

    # REPLAYED AGAINST THE REAL SHIPPED CORPUS, which is where the first cut of this rule was
    # found to be wrong. GATE_LESSONS 16: a fixture written by the author of a detector agrees
    # with the detector, and only real artifacts carry the shapes nobody thought to write down.
    #
    # TWO SHIPPED DECKS CARRY THE PATTERN AND THEY ARE NAMED RATHER THAN EXEMPTED. Both predate
    # the XHR discovery written into carousel no. 25's own frame 8, and the 27 decks after it are
    # clean. Naming them does two things at once: it proves the rule FIRES on real published
    # slide source rather than only on a fixture, and it means a THIRD deck growing one goes red
    # here. An exemption pattern would have done neither.
    _shipped = [p for p in sorted((REPO_ROOT / "runs" / "carousel").glob("*/slides"))
                if any(p.glob("slide-*.html"))]
    ok("shipped decks with slide source exist to replay this against", bool(_shipped),
       "runs/carousel/*/slides matched no slide HTML")
    _HISTORICAL = {"2026-08-16", "2026-08-18"}
    _scanned, _hit_decks = 0, set()
    for _sd in _shipped:
        _hits, _n = network_calls(_sd)
        _scanned += _n
        if _hits:
            _hit_decks.add(_sd.parent.name)
        elif _sd.parent.name in _HISTORICAL:
            ok(f"{_sd.parent.name} still carries the fetch this rule is written for", False,
               "the historical carrier came back clean, so the replay proves nothing")
    ok("every deck after the XHR discovery is clean under this rule",
       _hit_decks == _HISTORICAL,
       f"carriers found: {sorted(_hit_decks)}, expected {sorted(_HISTORICAL)}")
    ok("...over a corpus big enough for the pass to mean something", _scanned > 100,
       f"only {_scanned} shipped slide(s) were read")

    print("\ncraft_floor self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--render-dir")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.date or a.render_dir):
        ap.error("one of --date or --render-dir is required")
    d = Path(a.render_dir) if a.render_dir else REPO_ROOT / "out" / a.date / "render"
    rp = d / "render_report.json"
    if not rp.exists():
        print(f"craft_floor: {rp} does not exist", file=sys.stderr)
        return 2
    report = json.loads(rp.read_text(encoding="utf-8"))
    qp = d / "machine_qa.json"
    qa = json.loads(qp.read_text(encoding="utf-8")) if qp.exists() else None

    # THE SLIDE SOURCE, FOUND FROM THE RENDER DIRECTORY RATHER THAN ASKED FOR. A live run keeps
    # it at out/<date>/slides beside out/<date>/render, and `ship_images` archives a shipped deck
    # with render_report.json at the run root and slides/ under it. Both layouts are tried.
    #
    # A GATE THAT CANNOT RUN IS RED, NEVER GREEN. GATE_LESSONS 37: a skip and an unavailable
    # check are not the same event and must not share a report line. If no slide source can be
    # found, this says so and exits non-zero rather than printing a clean floor over a scan that
    # never happened.
    slides_dir = next((p for p in (d.parent / "slides", d / "slides", d) if
                       p.is_dir() and any(p.glob("slide-*.html"))), None)
    if slides_dir is None:
        print(f"craft_floor: no slide source found near {d}. The render-time fetch scan CANNOT "
              f"RUN, which is a failure and not a skip: a frame whose data never arrives renders "
              f"clean with nothing on it, and this is the only thing that reads for it.",
              file=sys.stderr)
        return 2
    fetches, n_scanned = network_calls(slides_dir)

    fails, warns, m = check(report, qa)
    for r in sorted(m.get("rows", []), key=lambda x: -x["variance"]):
        mark = "FAIL" if r.get("thin") and r in [x for x in m["rows"]] and any(
            r["file"] in f for f in fails) else ("warn" if r.get("thin") else "ok  ")
        print(f"  {mark}  {r['file']:<18} variance {r['variance']:>8.1f}")
    print(f"\n  deck median {m.get('median', 0):.1f}, floor {m.get('floor', 0):.1f}")
    for w in warns:
        print("  warn  " + w)
    if fetches:
        print(f"\ncraft_floor: {len(fetches)} render-time network call(s) in the slide source.",
              file=sys.stderr)
        for f in fetches:
            print("  " + f, file=sys.stderr)
    if fails:
        print("\ncraft_floor: a frame in this deck was not drawn.", file=sys.stderr)
        for f in fails:
            print("  " + f, file=sys.stderr)
    if fetches or fails:
        return 1
    print(f"craft floor: no render-time network call in {n_scanned} slide(s) of source")
    print("craft floor: clean, every frame carries a real light and a real dark")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
