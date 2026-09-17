#!/usr/bin/env python3
"""deck_chassis.py — prove the deck's nine frames were cut from ONE piece of stock.

WHY THIS EXISTS (2026-09-16, owner).

    "the artwork for the carousel post is just like, it's not good enough. it doesn't really
     flow together. all the slides don't really flow together. the artwork kind of just seems
     like it's like thrown on the page. I want each page to really seem like custom artwork,
     not just like somebody went and like threw some text boxes on a page."

Four things were measured under that sentence, and every one of them is a structural fact
rather than a matter of taste:

  1. THE GRADE WAS NEVER CALLED. `assets/js/txpost.js` is a full film grade, ported and
     working, and it was loaded by 1 shipped slide out of 205. The sibling product loads its
     own copy on 127 of 127. `txcolor.js`, the OKLCH ramp builder, ran 1 of 205 against 118 of
     127. The deck looked like flat vector fills because the pass that makes it not look like
     flat vector fills was sitting in the repo uncalled.

  2. THERE WAS NO DECK. Each frame reached into a permanent bin of finished parts and placed
     them, so the deck had uniform PARTS and no unity of WORLD. The sibling writes a new
     chassis per run, named for that deck's world, and all nine frames draw from it. Twenty six
     Texas decks had zero per run chassis between them.

  3. THE FRAMES DID NOT AGREE ABOUT THE LIGHT. Nothing said they had to, so nothing did.

  4. SIX FRAMES OF NINE PUT AN OPAQUE PLATE BEHIND THE HEADLINE. The source comment beside one
     of them reads "the plate is the critic's own fix for the placeholder bar reading", which is
     a critic saying the type sat badly and the repair being more plate. A plate is what a frame
     reaches for when the art under it was drawn without knowing where the type goes.

WHAT THIS CHECKS. Not whether a frame is beautiful, which is the scorer's job. Whether the nine
frames are ONE DECK, which is a property a machine can read off the source:

    chassis      all nine load txdeck.js and the SAME deck/<date>-<world>.js, and nothing else claims
                 to be a chassis
    declaration  the chassis calls TXDECK.declare exactly once, so nine frames cannot hold nine
                 lights. Coherence by construction rather than by nine acts of care
    finish       every frame calls TXDECK.finish as the last thing that touches the art canvas
    no template  the chassis exposes primitives, never a whole frame. A shared projection helper
                 is house furniture. A shared drawTheWholeSlide is a template
    no plate     no opaque rect behind display type
    reserve      nothing a TXDECK.lineBoxes call reserved is repositioned after it. The reserve
                 is live geometry, so an element that moves afterwards was never measured

EXIT CODES
    0  the nine frames are one deck
    1  a violation, or the checker was called wrongly
    2  the checker itself broke. Distinct so CI can tell "your deck is loose" from "the gate is
       unavailable"

RUN IT BY EXIT CODE, never by reading the last line.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# A chassis lives here and nowhere else. `assets/**` is `human` in ownership.yaml so that a run
# can never rewrite the house tools, and this one directory is carved out to `daily` so that a
# run CAN write its own world. That asymmetry is the whole point: the run may build a world, it
# may not edit the workshop.
CHASSIS_DIR = "assets/js/deck"

SCRIPT_RE = re.compile(r'<script[^>]+src="@@ASSETS@@/js/([^"]+)"', re.I)

# A chassis that draws a whole frame is a template wearing a chassis's name. These are the
# shapes that have meant "one drawing nine times" in this repo and in the sibling.
TEMPLATE_NAMES = (
    "drawslide", "drawframe", "renderslide", "renderframe", "buildslide",
    "buildframe", "drawscene", "composeframe", "layoutslide", "paintslide",
)

# AN OPAQUE FILL BEHIND DISPLAY TYPE, FOUND BY WHAT THE RULE DOES RATHER THAN BY ITS NAME.
#
# The first cut of this gate matched six class names plus an `rgba()` fallback, and a reviewer
# pointed out what that misses: `.hook { background: #08060F }` is a plate, an inline
# `style="background:#08060F"` is a plate, and neither carries one of the six names. A gate that
# recognises a defect by the name somebody happened to give it catches only the defects written
# by people who were not trying to get past it.
#
# So every CSS RULE is parsed, and a rule is a finding when its selector reaches display type and
# its background is opaque enough to read as a box. `data-decorative` and the deck's own
# furniture are not display type, and a wash is not a plate, so the alpha line stays.
CSS_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
BG_RE = re.compile(r"(?:^|;)\s*background(?:-color)?\s*:\s*([^;]+)", re.I)
INLINE_BG_RE = re.compile(r"style\s*=\s*[\"']([^\"']*background[^\"']*)[\"']", re.I)

# The selectors that carry a frame's own words. A plate behind the site line is a different
# (and smaller) sin than a plate behind the headline, and the furniture is excluded because
# TXLAYOUT owns its own treatment.
# TWO LISTS, because replacing the names with the behaviour lost a real catch. The first cut of
# this rewrite dropped the class names for a selector-reaches-display-type test, and the very
# defect the gate was built for, `.plate { background: rgba(9,10,15,0.97) }` on the 2026-09-16
# deck, stopped being found: `.plate` carries no display type of its own, it sits BEHIND some.
# The behaviour test catches what the names miss and the names catch what the behaviour misses,
# so both run.
DISPLAY_SEL = ("hook", "dek", "lab", "doc", "headline", "title", "quote", "big", "hed")

# A class whose whole job is to sit behind words. Its name is the confession.
PLATE_SEL = ("plate", "hookbox", "headbox", "titlebox", "textbox", "knockout", "backdrop",
             "textbg", "typebg", "scrim", "lozenge")

# Below this a fill is atmosphere. Measured against the six plates of the 2026-09-16 deck, whose
# lightest was 0.86, and against the wash frames of the reference build, whose heaviest was 0.22.
PLATE_ALPHA = 0.55


def slide_files(slides_dir: Path) -> list[Path]:
    return sorted(slides_dir.glob("slide-*.html"))


def scripts_of(html: str) -> list[str]:
    return SCRIPT_RE.findall(html)


# A CHASSIS FILENAME CARRIES ITS RUN'S DATE, and the reason is archive reproducibility
# (2026-09-16, review). A name derived from the world alone collides: a later deck about a desk
# lamp would overwrite `assets/js/deck/lamp.js`, and the archived slides under
# `runs/carousel/<earlier-date>/slides` still reference that exact path. `shipped_check.py`
# re-runs the gates against every deck this project has published, so the earlier run would be
# re-checked, and anyone reproducing it would render, against the LATER deck's world: a
# different light, a different ramp, a different grade. The date makes the path unique by
# construction, which is cheaper than a create-only rule somebody has to remember.
CHASSIS_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9_-]*)$")


def chassis_of(html: str) -> list[str]:
    """The deck chassis modules a frame loads, as bare file stems."""
    return [s.split("/", 1)[1][:-3] for s in scripts_of(html)
            if s.startswith("deck/") and s.endswith(".js")]


def _alpha_of(value: str) -> float:
    """How opaque a CSS colour is. A hex or a named colour is fully opaque."""
    v = value.strip().lower()
    m = re.match(r"rgba?\(([^)]*)\)", v)
    if m:
        parts = [x.strip() for x in m.group(1).replace("/", ",").split(",")]
        if len(parts) >= 4:
            try:
                a = parts[3]
                return float(a[:-1]) / 100 if a.endswith("%") else float(a)
            except ValueError:
                return 1.0
        return 1.0
    if v.startswith("#"):
        h = v[1:]
        if len(h) == 8:                       # #rrggbbaa
            try:
                return int(h[6:8], 16) / 255
            except ValueError:
                return 1.0
        if len(h) == 4:                       # #rgba
            try:
                return int(h[3] * 2, 16) / 255
            except ValueError:
                return 1.0
        return 1.0
    if v in ("transparent", "none", "inherit", "initial", "unset"):
        return 0.0
    if v.startswith(("linear-gradient", "radial-gradient", "var(")):
        # A gradient or a token can't be judged from the source. The RENDER gate is what sees
        # those, and saying so is better than a guess in either direction.
        return 0.0
    return 1.0                                 # a hex, a named colour, anything else opaque


def _reaches_display_type(selector: str) -> bool:
    sel = selector.lower()
    if any(("." + d) in sel or sel.strip().startswith(d) for d in DISPLAY_SEL):
        return True
    return any(("." + d) in sel or ("#" + d) in sel for d in PLATE_SEL)


def opaque_plates(html: str) -> list[str]:
    """Fills opaque enough to read as a box, on a selector that carries display type."""
    out = []
    for m in CSS_RULE_RE.finditer(html):
        selector, body = m.group(1), m.group(2)
        if "@" in selector or not _reaches_display_type(selector):
            continue
        for bg in BG_RE.finditer(body):
            value = bg.group(1)
            if _alpha_of(value) >= PLATE_ALPHA:
                out.append(f"{selector.strip().splitlines()[-1].strip()} {{ background: "
                           f"{value.strip()} }}")
    for m in INLINE_BG_RE.finditer(html):
        for bg in BG_RE.finditer(";" + m.group(1)):
            if _alpha_of(bg.group(1)) >= PLATE_ALPHA:
                out.append(f"inline style background: {bg.group(1).strip()}")
    return out


# Canvas calls that MUTATE the art. A frame that runs any of these after the grade has shipped
# artwork the grade never saw, which is the contract's whole point and not a technicality: the
# grade is what makes the deck one deck.
DRAW_AFTER_RE = re.compile(
    r"\b(?:fill|stroke|fillRect|strokeRect|clearRect|fillText|strokeText|drawImage|putImageData"
    r"|ellipse|arc|rect|beginPath|moveTo|lineTo|bezierCurveTo|quadraticCurveTo|createLinearGradient"
    r"|createRadialGradient)\s*\(")

# `TXDECK.finish(` with nothing commenting it out. Crude by design: a full JS parse is not worth
# it here, and a line whose finish call sits after `//` is the case that actually occurs.
FINISH_CALL_RE = re.compile(r"^(?P<before>[^\n]*?)TXDECK\.finish\s*\(", re.M)


def _executable_finish_lines(script: str) -> list[int]:
    """Character offsets of every TXDECK.finish call that is not commented out."""
    out = []
    for m in FINISH_CALL_RE.finditer(script):
        before = m.group("before")
        if "//" in before or "*" == before.strip()[:1]:
            continue
        out.append(m.end())
    return out


def _strip_block_comments(js: str) -> str:
    """Block comments blanked out, keeping length so offsets stay meaningful."""
    return re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), js, flags=re.S)


def finish_problems(name: str, html: str) -> list[str]:
    """The grade runs, it is executable, and NOTHING draws on the art canvas after it.

    WHY THIS IS NOT A SUBSTRING TEST (2026-09-16, review). The first cut asked whether the string
    `TXDECK.finish(` appeared anywhere in the file, which passes when the call sits in a comment
    and passes when a frame calls it and then keeps drawing. Both ship artwork the deck's grade
    never touched, which is exactly the defect the contract exists to prevent, and a gate that
    reports clean on the thing it was written to catch is worse than no gate.
    """
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S | re.I)
    body = _strip_block_comments("\n".join(scripts))

    calls = _executable_finish_lines(body)
    if not calls:
        if "TXDECK.finish(" in html:
            return [f"{name}: mentions TXDECK.finish only in a comment, so it ships ungraded. "
                    f"This is the call that was missing from 204 of 205 shipped slides"]
        return [f"{name}: never calls TXDECK.finish, so it ships ungraded. This is the call that "
                f"was missing from 204 of 205 shipped slides"]

    # After the LAST finish call, nothing may touch the art canvas again.
    tail = body[calls[-1]:]
    # the finish call's own argument list is not drawing
    tail = tail[tail.find(")") + 1:] if ")" in tail[:400] else tail
    drawn = sorted({m.group(0)[:-1].strip() for m in DRAW_AFTER_RE.finditer(tail)})
    if drawn:
        return [f"{name}: draws on the canvas AFTER TXDECK.finish ({', '.join(drawn[:4])}). The "
                f"grade is the last thing that touches the art canvas, so anything after it "
                f"ships ungraded on a frame that reports itself graded"]
    return []


# --------------------------------------------------------------------------- the type reserve
POSITION_RE = re.compile(
    r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*\.\s*style\s*\.\s*(left|top|right|bottom|transform)\s*=(?!=)")
BIND_RE = re.compile(
    r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*=\s*document\.(?:getElementById|querySelector)\("
    r"\s*[\"']([^\"']+)[\"']")
LINEBOXES_RE = re.compile(r"TXDECK\.lineBoxes\(\s*[\"']([^\"']*)[\"']")
ELEMENT_RE = re.compile(r"<[a-zA-Z][^>]*>")
ATTR_RE = re.compile(r"\b(id|class)\s*=\s*[\"']([^\"']*)[\"']")


def _code_only(html: str) -> str:
    """Inline script bodies with COMMENTS blanked and STRING BODIES KEPT, offsets preserved.

    `scene_bounds.strip_js` blanks strings too, which is right for reading numbers and wrong
    here: the selector a `lineBoxes` call names IS a string, and so is the id a binding reads.
    Blanking rather than deleting keeps the line numbers in the findings honest, and a `//`
    inside a string ("https://...") does not open a comment, which a regex would get wrong in
    the direction of a silent miss.
    """
    out = list(html)
    for i, c in enumerate(out):
        out[i] = "\n" if c == "\n" else " "
    for blk in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script\s*>", html, re.S | re.I):
        s, e = blk.start(1), blk.end(1)
        i, mode = s, None
        while i < e:
            c = html[i]
            if mode is None:
                if html.startswith("//", i):
                    mode, i = "line", i + 2
                    continue
                if html.startswith("/*", i):
                    mode, i = "block", i + 2
                    continue
                out[i] = c
                if c in "\"'`":
                    mode = c
                i += 1
            elif mode == "line":
                if c == "\n":
                    mode = None
                i += 1
            elif mode == "block":
                if html.startswith("*/", i):
                    mode, i = None, i + 2
                    continue
                i += 1
            else:
                out[i] = c
                if c == "\\":
                    out[i + 1] = html[i + 1] if i + 1 < e else " "
                    i += 2
                    continue
                if c == mode:
                    mode = None
                i += 1
    return "".join(out)


def _selectors_of(html: str) -> dict[str, set[str]]:
    """Every element's id, mapped to the selectors that reach it. `#card` AND `.card`.

    The whole reason this reads the markup instead of the script is that `.card` and `#card` are
    the same element only because one div carries both, and a checker that assumed the variable
    name equals the class name would be right on carousel no. 27 by luck and silent on the next
    deck that names its variable anything else.
    """
    out: dict[str, set[str]] = {}
    for tag in ELEMENT_RE.finditer(html):
        attrs = dict((m.group(1), m.group(2)) for m in ATTR_RE.finditer(tag.group(0)))
        eid = attrs.get("id")
        if not eid:
            continue
        sel = {"#" + eid}
        sel.update("." + c for c in (attrs.get("class") or "").split() if c)
        out[eid] = sel
    return out


def reserve_order_problems(name: str, html: str) -> list[str]:
    """THE TYPE RESERVE IS MEASURED AFTER THE TYPE IS PLACED, and nothing checked the order.

    THE DEFECT THIS EXISTS FOR (2026-09-17, carousel no. 27, frame 9)

    The deck's one screen ran its halftone straight under five lines of mono type on the accent
    card, against `txdeck.js`'s own oldest rule. A judge found it in round 4, the run added
    `.card` to the `lineBoxes` selector, reported it fixed, and A ROUND 5 JUDGE FOUND IT AGAIN
    by reading the source and the render together. The string was right and the pixels were
    unchanged, because the card is positioned twenty lines LATER:

        var boxes = TXDECK.lineBoxes(".hook, .dek, .card, .kick, .ctr, .src, .tx-site", 18);
        ...
        var card = document.getElementById("card");
        card.style.left = (CX0 + 26) + "px";
        card.style.top  = (CY0 + 24) + "px";

    `lineBoxes` measures LIVE geometry through `getClientRects`, so it reserved the card's
    STATIC coordinates and protected a region of the frame no type was ever in. Its own docstring
    says "Measure AFTER document.fonts.ready and AFTER fitText, or the boxes are the wrong size",
    which is the same rule one step short: an element that MOVES after the measurement is as
    unmeasured as one whose font had not loaded.

    A repair that changes a selector string and never moves a pixel is the exact shape this
    project keeps meeting, and the only thing that separates it from a real fix is a measurement.

    WHAT IT DOES NOT ASK. Whether the reserve was big enough, whether the selector names every
    type block, or whether the mask was used. Those are questions about the picture. This is one
    question about ORDER, which is a fact about the source and has a right answer.
    """
    code = _code_only(html)
    calls = list(LINEBOXES_RE.finditer(code))
    if not calls:
        return []
    reach = _selectors_of(html)
    bound: dict[str, set[str]] = {}
    for m in BIND_RE.finditer(code):
        target = m.group(2)
        if target.startswith("#") or not target.startswith("."):
            bound[m.group(1)] = reach.get(target.lstrip("#"), {target if target.startswith("#")
                                                               else "#" + target})
        else:
            bound[m.group(1)] = {target}
    out = []
    for call in calls:
        named = {s.strip() for s in call.group(1).split(",") if s.strip()}
        line_of_call = code.count("\n", 0, call.start()) + 1
        for move in POSITION_RE.finditer(code):
            if move.start() < call.end():
                continue
            hit = named & bound.get(move.group(1), set())
            if not hit:
                continue
            line = code.count("\n", 0, move.start()) + 1
            out.append(
                f"{name}: TXDECK.lineBoxes at line {line_of_call} reserves "
                f"{', '.join(sorted(hit))} and `{move.group(1)}.style.{move.group(2)}` moves that "
                f"element at line {line}. lineBoxes reads LIVE geometry, so the reserve was taken "
                f"at the element's static position and protects a region the type is not in. "
                f"Position, then measure")
    return sorted(set(out))


def check_deck(slides_dir: Path, repo_root: Path = REPO_ROOT) -> list[str]:
    """Every way the nine frames fail to be one deck. Empty means they are."""
    problems: list[str] = []
    files = slide_files(slides_dir)
    if not files:
        return [f"no slide-*.html in {slides_dir}"]

    seen_chassis: dict[str, list[str]] = {}

    for f in files:
        name = f.name
        html = f.read_text(encoding="utf-8", errors="replace")
        srcs = scripts_of(html)

        if "txdeck.js" not in srcs:
            problems.append(f"{name}: does not load txdeck.js, so it has no deck to belong to")

        ch = chassis_of(html)
        if not ch:
            problems.append(
                f"{name}: loads no deck chassis. A run writes one {CHASSIS_DIR}/<world>.js for "
                f"the deck and every frame loads it. Reaching into the permanent bin per frame "
                f"is what twenty six decks did and is what the owner called thrown on the page")
        elif len(ch) > 1:
            problems.append(f"{name}: loads {len(ch)} chassis modules {ch}. One deck, one world")
        else:
            seen_chassis.setdefault(ch[0], []).append(name)
            if not CHASSIS_NAME_RE.match(ch[0]):
                problems.append(
                    f"{name}: loads chassis '{ch[0]}', which is not <date>-<world>. A chassis "
                    f"named for its world alone collides with a later deck that picks the same "
                    f"world, and the archived slides of the earlier run point at that same path, "
                    f"so re-checking or reproducing it would render the later deck's light")

        problems.extend(finish_problems(name, html))
        problems.extend(reserve_order_problems(name, html))

        # A frame grading itself is a frame holding its own opinion about the deck's look.
        direct = [m for m in re.finditer(r"TXPOST\.grade\s*\(", html)]
        if direct:
            problems.append(
                f"{name}: calls TXPOST.grade directly {len(direct)}x. The grade is the deck's, "
                f"not the frame's. Call TXDECK.finish(cx)")

        if "TXDECK.declare(" in html:
            problems.append(
                f"{name}: declares a deck. Only the chassis declares. A frame that redeclares is "
                f"a frame holding its own light")

        plates = opaque_plates(html)
        if plates:
            problems.append(
                f"{name}: {len(plates)} opaque plate(s) behind type {plates[:2]}. Seat type in a "
                f"reserve the art left (TXDECK.lineBoxes + reserveMask), never on a plate")

    if len(seen_chassis) > 1:
        detail = "; ".join(f"{w}: {', '.join(v)}" for w, v in sorted(seen_chassis.items()))
        problems.append(
            f"the deck loads {len(seen_chassis)} different chassis modules ({detail}). "
            f"Nine frames, one world")

    for world in seen_chassis:
        problems.extend(check_chassis(repo_root / CHASSIS_DIR / f"{world}.js"))

    return problems


def check_chassis(path: Path) -> list[str]:
    """The chassis file itself: one declaration, primitives only."""
    problems: list[str] = []
    if not path.exists():
        return [f"chassis {path.relative_to(REPO_ROOT) if path.is_absolute() else path} "
                f"is loaded by the frames and does not exist"]

    src = path.read_text(encoding="utf-8", errors="replace")
    name = path.name

    declares = len(re.findall(r"TXDECK\.declare\s*\(", src))
    if declares == 0:
        problems.append(f"{name}: never calls TXDECK.declare. The chassis is what declares the "
                        f"deck's light, material, accent and grade")
    elif declares > 1:
        problems.append(f"{name}: calls TXDECK.declare {declares}x. One deck, one declaration")

    lowered = src.lower()
    for bad in TEMPLATE_NAMES:
        if re.search(r"\b" + re.escape(bad) + r"\s*[:=]\s*function|\bfunction\s+" + re.escape(bad) + r"\b",
                     lowered):
            problems.append(
                f"{name}: exposes '{bad}', which draws a whole frame. A shared projection helper "
                f"is house furniture. A shared whole frame is a template, and a template is the "
                f"defect this gate exists for")

    return problems


def report(problems: list[str], slides_dir: Path) -> int:
    if not problems:
        print(f"deck_chassis: ok, {len(slide_files(slides_dir))} frames are one deck")
        return 0
    print(f"deck_chassis: FAIL, {len(problems)} problem(s) in {slides_dir}\n", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    print("\n  knowledge/carousel/ILLUSTRATION_SYSTEM.md, 'THE DECK IS THE UNIT', is the standard.",
          file=sys.stderr)
    return 1


# --------------------------------------------------------------------------- self test

_GOOD_CHASSIS = """
(function (g) {
  TXDECK.declare({ world: "caprock", light: { az: 76, el: 12, keyToFill: 6 },
    ground: "#08060F", material: "#191530", accent: "#E0956A", grade: TXDECK.DUSK_GRADE });
  var C = {};
  C.mesa = function (cx, o) { /* a primitive, not a frame */ };
  g.TXCAPROCK = C;
})(window);
"""

_GOOD_SLIDE = """<!doctype html><html><body>
<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/deck/2026-09-16-caprock.js"></script>
<script>TXCAPROCK.mesa(cx, {}); TXDECK.finish(cx, { w: 1080, h: 1350 });</script>
</body></html>"""


def _write_deck(root: Path, slides: dict[str, str], chassis: dict[str, str]) -> Path:
    sd = root / "slides"
    sd.mkdir(parents=True, exist_ok=True)
    for n, body in slides.items():
        (sd / n).write_text(body, encoding="utf-8")
    cd = root / CHASSIS_DIR
    cd.mkdir(parents=True, exist_ok=True)
    for n, body in chassis.items():
        (cd / n).write_text(body, encoding="utf-8")
    return sd


def self_test() -> int:
    """Replays the 2026-09-16 deck's four defects and proves a clean deck passes."""
    fails = []

    ran: list[str] = []

    def case(label: str, slides: dict[str, str], chassis: dict[str, str],
             want_problem: str | None) -> None:
        ran.append(label)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sd = _write_deck(root, slides, chassis)
            got = check_deck(sd, repo_root=root)
            if want_problem is None:
                if got:
                    fails.append(f"{label}: expected clean, got {got}")
            else:
                if not any(want_problem in g for g in got):
                    fails.append(f"{label}: expected a problem mentioning {want_problem!r}, "
                                 f"got {got}")

    nine = {f"slide-0{i}.html": _GOOD_SLIDE for i in range(1, 10)}
    good_ch = {"2026-09-16-caprock.js": _GOOD_CHASSIS}

    case("a clean deck passes", nine, good_ch, None)

    # 1. the grade that 204 of 205 slides never called
    ungraded = dict(nine)
    ungraded["slide-04.html"] = _GOOD_SLIDE.replace("TXDECK.finish(cx, { w: 1080, h: 1350 });", "")
    case("a frame that skips the grade fails", ungraded, good_ch, "never calls TXDECK.finish")

    # 2. no chassis at all, which is every Texas deck to date
    nochassis = dict(nine)
    nochassis["slide-02.html"] = _GOOD_SLIDE.replace(
        '<script src="@@ASSETS@@/js/deck/2026-09-16-caprock.js"></script>', "")
    case("a frame with no chassis fails", nochassis, good_ch, "loads no deck chassis")

    # 3. two worlds in one deck
    split = dict(nine)
    split["slide-07.html"] = _GOOD_SLIDE.replace("deck/2026-09-16-caprock.js", "deck/2026-09-16-bayou.js")
    case("two chassis in one deck fails", split,
         {"2026-09-16-caprock.js": _GOOD_CHASSIS,
          "2026-09-16-bayou.js": _GOOD_CHASSIS.replace("caprock", "bayou")},
         "different chassis modules")

    # 4. the opaque plate behind the headline, six of nine on 2026-09-16
    plated = dict(nine)
    plated["slide-05.html"] = _GOOD_SLIDE.replace(
        "<body>", "<body><style>.plate{position:absolute;background:rgba(9,10,15,0.97)}</style>")
    case("an opaque plate behind type fails", plated, good_ch, "opaque plate")

    # a wash is not a plate
    washed = dict(nine)
    washed["slide-05.html"] = _GOOD_SLIDE.replace(
        "<body>", "<body><style>.veil{background:rgba(9,10,15,0.22)}</style>")
    case("a light wash is allowed", washed, good_ch, None)

    # a frame grading itself
    selfgrade = dict(nine)
    selfgrade["slide-03.html"] = _GOOD_SLIDE.replace(
        "TXDECK.finish(cx, { w: 1080, h: 1350 });",
        "TXPOST.grade(cx, { contrast: 2.0 }); TXDECK.finish(cx, { w: 1080, h: 1350 });")
    case("a frame grading itself fails", selfgrade, good_ch, "calls TXPOST.grade directly")

    # a chassis that draws whole frames is a template
    # 2b. THE FINISH CONTRACT, structurally (2026-09-16 review). A substring test passes on a
    # commented-out call and on a frame that grades and then keeps drawing, and both ship
    # artwork the grade never saw.
    commented = dict(nine)
    commented["slide-06.html"] = _GOOD_SLIDE.replace(
        "TXDECK.finish(cx, { w: 1080, h: 1350 });", "// TXDECK.finish(cx, { w: 1080, h: 1350 });")
    case("a finish call that is commented out fails", commented, good_ch, "only in a comment")

    blockc = dict(nine)
    blockc["slide-06.html"] = _GOOD_SLIDE.replace(
        "TXDECK.finish(cx, { w: 1080, h: 1350 });", "/* TXDECK.finish(cx, {}) one day */")
    case("a finish call inside a block comment fails", blockc, good_ch, "only in a comment")

    # 2c. THE TYPE RESERVE ORDER, replayed on carousel no. 27's frame 9 as it shipped. The card
    # carries `id="card" class="card"` and the selector names `.card`, so a checker that matched
    # the VARIABLE name against the selector would pass this and pass the buggy version too.
    # The variable is deliberately named something else here for exactly that reason.
    _CARD = ('<div class="card" id="card">FIVE LINES</div>\n'
             '<script>var boxes = TXDECK.lineBoxes(".hook, .card, .src", 18);\n'
             'var mask = TXDECK.reserveMask(boxes, 24);\n')
    moved = dict(nine)
    moved["slide-09.html"] = _GOOD_SLIDE.replace(
        "<script>TXCAPROCK", _CARD + "var el = document.getElementById('card');\n"
        "el.style.left = (CX0 + 26) + 'px';\nel.style.top = (CY0 + 24) + 'px';</script>\n"
        "<script>TXCAPROCK")
    case("an element the reserve names, repositioned after it, fails", moved, good_ch,
         "Position, then measure")

    ordered = dict(nine)
    ordered["slide-09.html"] = _GOOD_SLIDE.replace(
        "<script>TXCAPROCK",
        '<div class="card" id="card">FIVE LINES</div>\n'
        "<script>var el = document.getElementById('card');\n"
        "el.style.left = (CX0 + 26) + 'px';\nel.style.top = (CY0 + 24) + 'px';\n"
        'var boxes = TXDECK.lineBoxes(".hook, .card, .src", 18);\n'
        "var mask = TXDECK.reserveMask(boxes, 24);</script>\n<script>TXCAPROCK")
    case("...and the SAME frame with the two steps in the right order passes", ordered,
         good_ch, None)

    unnamed = dict(nine)
    unnamed["slide-09.html"] = _GOOD_SLIDE.replace(
        "<script>TXCAPROCK", _CARD.replace('".hook, .card, .src"', '".hook, .src"')
        + "var el = document.getElementById('card');\nel.style.left = '20px';</script>\n"
        "<script>TXCAPROCK")
    case("an element the reserve does NOT name may be moved freely", unnamed, good_ch, None)

    commentmove = dict(nine)
    commentmove["slide-09.html"] = _GOOD_SLIDE.replace(
        "<script>TXCAPROCK", _CARD + "var el = document.getElementById('card');\n"
        "// el.style.left = '20px';\nvar u = 'https://texasaidocket.com';</script>\n"
        "<script>TXCAPROCK")
    case("a commented move is not a move, and a // inside a URL does not hide a real one",
         commentmove, good_ch, None)

    drawafter = dict(nine)
    drawafter["slide-08.html"] = _GOOD_SLIDE.replace(
        "TXDECK.finish(cx, { w: 1080, h: 1350 });",
        "TXDECK.finish(cx, { w: 1080, h: 1350 }); cx.fillRect(0, 0, 80, 80);")
    case("drawing after the grade fails", drawafter, good_ch, "AFTER TXDECK.finish")

    # 4b. A PLATE FOUND BY BEHAVIOUR RATHER THAN BY ITS CLASS NAME
    hexplate = dict(nine)
    hexplate["slide-02.html"] = _GOOD_SLIDE.replace(
        "<body>", "<body><style>.hook{position:absolute;background:#08060F}</style>")
    case("an opaque HEX background on display type fails", hexplate, good_ch, "opaque plate")

    inlineplate = dict(nine)
    inlineplate["slide-02.html"] = _GOOD_SLIDE.replace(
        "<body>", '<body><h1 class="hook" style="background:#08060F">x</h1>')
    case("an inline opaque background fails", inlineplate, good_ch, "opaque plate")

    gradient = dict(nine)
    gradient["slide-02.html"] = _GOOD_SLIDE.replace(
        "<body>", "<body><style>.hook{background:linear-gradient(#000,#fff)}</style>")
    case("a gradient is left to the render gate, not guessed at", gradient, good_ch, None)

    case("a chassis that draws a whole frame fails", nine,
         {"2026-09-16-caprock.js": _GOOD_CHASSIS.replace("C.mesa = function", "C.drawSlide = function")},
         "which draws a whole frame")

    # a chassis that forgets to declare
    case("a chassis with no declaration fails", nine,
         {"2026-09-16-caprock.js": _GOOD_CHASSIS.replace("TXDECK.declare(", "noop(")},
         "never calls TXDECK.declare")

    if fails:
        print(f"deck_chassis --self-test: FAIL, {len(fails)} case(s)", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    # COUNTED, NEVER TYPED. This line read "16 cases" while nineteen ran, having been written
    # when sixteen did, so the one number the suite prints about itself was three behind and a
    # reader could not tell a case that had been added from one that had been deleted.
    print(f"deck_chassis --self-test: ok, {len(ran)} cases")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--slides-dir", help="the directory holding slide-*.html")
    ap.add_argument("--date", help="shorthand for runs/carousel/<date>/slides")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    if a.date and not a.slides_dir:
        a.slides_dir = str(REPO_ROOT / "runs" / "carousel" / a.date / "slides")
    if not a.slides_dir:
        print("deck_chassis: need --slides-dir or --date", file=sys.stderr)
        return 1

    sd = Path(a.slides_dir)
    if not sd.is_dir():
        print(f"deck_chassis: no such directory {sd}", file=sys.stderr)
        return 1

    problems = check_deck(sd)
    if a.json:
        print(json.dumps({"slides_dir": str(sd), "problems": problems,
                          "ok": not problems}, indent=1))
        return 1 if problems else 0
    return report(problems, sd)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                    # pragma: no cover
        print(f"deck_chassis: the gate itself broke: {exc}", file=sys.stderr)
        sys.exit(2)
