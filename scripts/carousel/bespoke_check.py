#!/usr/bin/env python3
"""bespoke_check.py — prove the deck is nine drawings and not one drawing nine times.

THE FAILURE THIS MEASURES

"The engine is a harness, not a template" is a sentence every run agrees with and some runs
break anyway, because breaking it does not look like breaking it. A run writes one good drawing
function, calls it nine times with different arguments, and produces a deck that renders
cleanly, passes every legibility gate, reads as consistent, and is boring in a way no individual
slide can be blamed for. The storyboard will even justify it as a visual system.

So the outcome gets measured rather than the method. Generating slide HTML is fine. Nine frames
sharing one drawing function is not, and only a similarity number can tell those apart.

HOW IT MEASURES

Each slide's art code is normalised, then every pair is compared with a token-level similarity.
What is compared is the DRAWING, not the document: markup skeleton, brand tokens, the font link,
the counter furniture and the asset paths are identical across a deck by design, and leaving
them in would put a floor under every score high enough to hide the thing being looked for.

    normalise   strip comments, string literals, numbers, whitespace, and the boilerplate
                every slide shares. What survives is the shape of the drawing.
    compare     token multiset cosine over every unordered pair.
    report      the MEDIAN pairwise similarity, plus the worst pair by name.

THE THRESHOLDS ARE FITTED, NOT GUESSED. They come from measuring two real decks:

    bespoke reference      0.049 median pairwise
    known-bad template     0.940 median pairwise

Two decks is a thin corpus, which is why the fail line sits at 0.55, far from both, rather than
tucked next to the bad one. A number in the middle is a run that should look at its own deck,
not a run this file gets to convict. WARN from 0.35.

    bespoke_check.py --slides-dir out/<run>/slides
    bespoke_check.py --self-test
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

FAIL_AT = 0.55
WARN_AT = 0.35

# Everything a deck shares on purpose. Left in, these put a floor under every pair.
BOILERPLATE = re.compile(
    r"<!doctype[^>]*>|</?html[^>]*>|</?head[^>]*>|</?body[^>]*>|</?meta[^>]*>|"
    r"@@ASSETS@@[^\"')]*|<link[^>]*>|<script[^>]*src=[^>]*></script>|"
    r"box-sizing|margin\s*:\s*0|padding\s*:\s*0|overflow\s*:\s*hidden|"
    r"width\s*:\s*1080px|height\s*:\s*1350px|position\s*:\s*absolute|inset\s*:\s*0|"
    # Pure containers, which every slide has and which say nothing about the drawing.
    # canvas, svg, table and img are deliberately NOT here: choosing one over another IS
    # a difference in technique, and that is the thing being measured.
    r"</?script[^>]*>|</?style[^>]*>|</?div[^>]*>|</?span[^>]*>|</?p[^>]*>|</?br[^>]*>|"
    r"</?section[^>]*>|</?main[^>]*>|</?header[^>]*>|</?footer[^>]*>|"
    # IDIOMS THE SLIDE CONTRACT REQUIRES. Every canvas slide sets a 2x backing store, seeds
    # its noise, and gates the screenshot, because SKILL.md makes all three mandatory. Two
    # slides obeying the same required contract is not evidence of a template, and leaving
    # these in put the demo deck's two canvas slides at 0.76 against each other on nothing
    # but compliance. Stripped for the same reason box-sizing is.
    r"getcontext\s*\(|\.width\s*=[^;]*\*\s*SC|\.height\s*=[^;]*\*\s*SC|"
    r"\.style\.width|\.style\.height|\bcx\.scale\s*\(|\bconst\s+SC\b|"
    r"TX\.reseed\s*\(|TX\.rng\s*\(|document\.body\.dataset\.ready|"
    r"window\.renderReady|document\.getElementById\s*\(",
    re.IGNORECASE)
COMMENT = re.compile(r"<!--.*?-->|/\*.*?\*/|//[^\n]*", re.DOTALL)
STRING = re.compile(r"\"[^\"]*\"|'[^']*'")
NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")

# THE STANDING MASTHEAD, added to every slide of every deck on 2026-08-19.
#
# The coherence upgrade that run made the wordmark, the star, the kicker, the site line and the
# NN / NN counter identical on all eight frames, which is the whole point of them: they are what
# makes eight drawings read as one publication. This gate then scored that consistency as
# sameness. Measured on the 2026-08-19 deck, the closest pair shared 50 tokens and exactly ONE of
# them was a drawing call. The other 49 were the masthead's markup, its class names and its text.
# The deck failed at 0.5508 against a 0.55 line on furniture alone.
#
# That is the same fault the FURNITURE set above was written for, one layer up. FURNITURE is a
# vocabulary of CSS and JS keywords, so it could never have caught markup the deck introduced
# afterwards. Anything carrying a `tx-` class is standing furniture by construction, so it is
# removed here with its subtree, along with the CSS rules that style it.
MASTHEAD_CSS = re.compile(r"\.tx-[A-Za-z0-9_-]+\s*\{[^}]*\}")
MASTHEAD_OPEN = re.compile(r"<([A-Za-z][A-Za-z0-9]*)\b[^>]*\bclass\s*=\s*[\"'][^\"']*\btx-")
VOID = {"br", "img", "input", "hr", "meta", "link", "source", "use", "path", "polygon", "circle"}


def strip_masthead(html: str) -> str:
    """Remove every element carrying a `tx-` class, subtree and all, plus its CSS rules.

    Written as a scanner rather than a regex because the masthead nests: the frame container
    holds the wordmark, the star, the kicker, the site line and the counter, and a non-greedy
    regex closes on the first inner `</div>` and leaves the rest of the block behind, which is
    the failure mode that made this look fixed while four of five tokens survived.
    """
    out = html
    while True:
        m = MASTHEAD_OPEN.search(out)
        if not m:
            break
        tag = m.group(1).lower()
        gt = out.find(">", m.end())
        if gt < 0:
            break
        if tag in VOID or out[gt - 1] == "/":
            out = out[:m.start()] + " " + out[gt + 1:]
            continue
        depth, i = 1, gt + 1
        open_re = re.compile(rf"<(/?){re.escape(tag)}\b", re.IGNORECASE)
        while depth and i < len(out):
            nxt = open_re.search(out, i)
            if not nxt:
                i = len(out)
                break
            depth += -1 if nxt.group(1) else 1
            i = out.find(">", nxt.end())
            i = len(out) if i < 0 else i + 1
        out = out[:m.start()] + " " + out[i:]
    return MASTHEAD_CSS.sub(" ", out)

# THE TYPE FURNITURE IS SUPPOSED TO BE THE SAME. A deck has one kicker style, one headline
# style, one footer, and that consistency is the visual system working rather than a template
# failing. Counting it as similarity buries the signal: measured on the demo deck, the single
# token "px" contributed more to the closest pair's score than every drawing call combined.
#
# Kept, deliberately: gradient, filter, transform, blend, shadow, clip and mask. Those are
# art done in CSS, and a slide that draws with them is making a choice this gate should see.
FURNITURE = {
    "px", "rem", "em", "deg", "vh", "vw", "ch", "fr", "pt", "s", "ms",
    "font", "family", "size", "weight", "style", "color", "background", "border", "radius",
    "margin", "padding", "top", "bottom", "left", "right", "width", "height", "display",
    "flex", "grid", "gap", "align", "justify", "content", "items", "direction", "wrap",
    "line", "letter", "spacing", "text", "transform", "uppercase", "lowercase", "decoration",
    "variation", "settings", "variant", "numeric", "tabular", "serif", "sans", "monospace",
    "rgba", "rgb", "solid", "dashed", "none", "auto", "center", "baseline", "block", "inline",
    "absolute", "relative", "fixed", "sticky", "hidden", "visible", "opacity", "z", "index",
    "class", "id", "html", "body", "canvas", "viewbox", "xmlns", "aria", "role", "data",
    "const", "let", "var", "function", "return", "for", "of", "in", "if", "else", "new",
    "await", "async", "true", "false", "null", "undefined", "this", "document", "window",
    "math", "max", "min", "abs", "floor", "round", "length", "push", "map", "filter",
}


def _informative(tok: str) -> bool:
    """A token that says something about the DRAWING.

    Single characters are loop variables. Furniture is layout and type vocabulary every slide
    shares by design. What is left is the technique.
    """
    return len(tok) > 1 and tok not in FURNITURE


def normalise(html: str) -> Counter:
    """The shape of the drawing, with everything shared or incidental removed."""
    s = COMMENT.sub(" ", html)
    s = strip_masthead(s)
    s = BOILERPLATE.sub(" ", s)
    s = STRING.sub(" ", s)
    s = NUMBER.sub(" ", s)
    return Counter(t for t in TOKEN.findall(s.lower()) if _informative(t))


def similarity(a: Counter, b: Counter) -> float:
    """Cosine over token multisets. 1.0 is the same drawing, 0.0 shares no vocabulary."""
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return round(dot / (na * nb), 4) if na and nb else 0.0


def measure(slides: dict[str, str]) -> dict:
    names = sorted(slides)
    vecs = {n: normalise(slides[n]) for n in names}
    pairs = []
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            pairs.append((similarity(vecs[x], vecs[y]), x, y))
    if not pairs:
        return {"slides": len(names), "pairs": 0, "median": 0.0, "worst": None, "verdict": "ok"}
    pairs.sort()
    sims = [p[0] for p in pairs]
    mid = len(sims) // 2
    median = sims[mid] if len(sims) % 2 else round((sims[mid - 1] + sims[mid]) / 2, 4)
    worst = pairs[-1]
    verdict = "fail" if median >= FAIL_AT else "warn" if median >= WARN_AT else "ok"
    return {"slides": len(names), "pairs": len(pairs), "median": median,
            "worst": {"similarity": worst[0], "a": worst[1], "b": worst[2]},
            "verdict": verdict}


def report(m: dict) -> int:
    print(f"bespoke_check: {m['slides']} slide(s), {m['pairs']} pair(s), "
          f"median pairwise similarity {m['median']}")
    if m["worst"]:
        w = m["worst"]
        print(f"  closest pair: {w['a']} and {w['b']} at {w['similarity']}")
    if m["verdict"] == "fail":
        print(f"\nbespoke_check: FAIL at or above {FAIL_AT}. This deck is one drawing repeated.\n"
              f"  The fix is not different arguments to the same function. It is a different\n"
              f"  drawing: a different technique, a different structure, a different way of\n"
              f"  seeing the subject. A visual system is a reason, not an excuse.",
              file=sys.stderr)
        return 1
    if m["verdict"] == "warn":
        print(f"  WARN at or above {WARN_AT}: look at the deck yourself. Shared vocabulary is "
              f"not automatically repetition, and this number cannot tell the difference.")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    SHELL = ('<!doctype html><html><head><meta charset="utf-8">'
             '<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">'
             '<style>*{margin:0;padding:0;box-sizing:border-box}'
             'html,body{width:1080px;height:1350px;overflow:hidden}</style></head><body>')

    # A TEMPLATED DECK: one drawing function, different arguments.
    tmpl = {f"slide-{i:02d}.html": SHELL + f'''
      <canvas id="c"></canvas><script>
      function drawPanel(cx, hue, label, count) {{
        const grad = cx.createLinearGradient(0, 0, 0, 1350);
        grad.addColorStop(0, hue); cx.fillStyle = grad; cx.fillRect(0, 0, 1080, 1350);
        for (let i = 0; i < count; i++) {{ cx.beginPath(); cx.arc(i, i, 4, 0, 7); cx.fill(); }}
        cx.fillText(label, 96, 1200);
      }}
      drawPanel(document.getElementById("c").getContext("2d"), "#{i}{i}{i}", "panel", {i * 10});
      </script></body></html>''' for i in range(1, 10)}

    # A BESPOKE DECK: genuinely different techniques per slide.
    bespoke = {
        "slide-01.html": SHELL + '''<svg><defs><filter id="f"><feTurbulence
            baseFrequency="0.01" numOctaves="4"/><feDisplacementMap scale="140"/>
            </filter></defs><ellipse filter="url(#f)"/></svg></body></html>''',
        "slide-02.html": SHELL + '''<script src="@@ASSETS@@/js/d3.v7.min.js"></script>
            <script>const proj = TXGeo.texasProjection(state, extent);
            svg.append("path").attr("d", d3.geoPath(proj)(counties));</script></body></html>''',
        "slide-03.html": SHELL + '''<script>const R = TX.rng(1); for (const band of bands) {
            let x = R(); const th = TX.fbm2(x, y); ctx.lineTo(Math.cos(th), Math.sin(th)); }
            </script></body></html>''',
        "slide-04.html": SHELL + '''<script>const cam = TX3D.camera({pos: [0, 9, 27]});
            const terrain = TX3D.heightfield({y: land, color: shade});
            TX3D.render(ctx, cam, terrain.faces, {fog: haze});</script></body></html>''',
        "slide-05.html": SHELL + '''<table class="figures"><thead><tr><th>Fuel</th></tr></thead>
            <tbody><tr><td>Natural Gas</td></tr></tbody></table></body></html>''',
    }

    mt, mb = measure(tmpl), measure(bespoke)
    ok("a templated deck scores high", mt["median"] >= FAIL_AT, str(mt["median"]))
    ok("a bespoke deck scores low", mb["median"] < WARN_AT, str(mb["median"]))
    ok("the two are far apart, not adjacent", mt["median"] - mb["median"] > 0.4,
       f"{mb['median']} vs {mt['median']}")
    ok("the templated deck FAILS", mt["verdict"] == "fail")
    ok("the bespoke deck passes", mb["verdict"] == "ok")
    ok("the closest pair is named, so it can be looked at",
       mt["worst"] and mt["worst"]["a"] != mt["worst"]["b"])

    # THE BOILERPLATE STRIP IS WHAT MAKES THE NUMBER MEAN ANYTHING.
    raw = {k: v for k, v in bespoke.items()}
    stripped_med = measure(raw)["median"]
    unstripped = []
    names = sorted(raw)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            ca = Counter(TOKEN.findall(raw[x].lower()))
            cb = Counter(TOKEN.findall(raw[y].lower()))
            unstripped.append(similarity(ca, cb))
    unstripped.sort()
    raw_med = unstripped[len(unstripped) // 2]
    ok("stripping the shared shell lowers a bespoke deck's score",
       stripped_med < raw_med, f"stripped {stripped_med} vs raw {raw_med}")
    ok("...which is the point: unstripped, a bespoke deck would score like a template",
       raw_med > stripped_med + 0.15, f"{raw_med} vs {stripped_med}")

    ok("numbers do not count as difference",
       similarity(normalise("<script>drawPanel(cx, 1, 2, 3)</script>"),
                  normalise("<script>drawPanel(cx, 9, 8, 7)</script>")) == 1.0,
       "different arguments to the same call are the same drawing")
    ok("string literals do not count as difference",
       similarity(normalise('<script>drawPanel(cx, "permian")</script>'),
                  normalise('<script>drawPanel(cx, "panhandle")</script>')) == 1.0)
    ok("a loop variable is not a technique",
       not _informative("i") and not _informative("x") and _informative("heightfield"))
    ok("a CSS property every slide sets is not a technique",
       not _informative("letter") and not _informative("spacing"))
    ok("art done in CSS still counts as a technique",
       _informative("gradient") and _informative("feturbulence") and _informative("blend"))
    ok("a different technique does count",
       similarity(normalise("<canvas></canvas><script>const cam = TX3D.camera(opts); "
                            "TX3D.render(ctx, cam, terrain.faces, fog);</script>"),
                  normalise("<svg></svg><script>const proj = TXGeo.texasProjection(state); "
                            "svg.append(path).attr(d, d3.geoPath(proj)(counties));</script>"))
       < 0.3,
       str(similarity(normalise("<canvas></canvas><script>const cam = TX3D.camera(opts); "
                                "TX3D.render(ctx, cam, terrain.faces, fog);</script>"),
                      normalise("<svg></svg><script>const proj = TXGeo.texasProjection(state); "
                                "svg.append(path).attr(d, d3.geoPath(proj)(counties));"
                                "</script>"))))
    ok("a container tag is not evidence of similarity",
       similarity(normalise("<script></script>"), normalise("<script></script>")) == 0.0,
       "two empty scripts share no drawing")

    ok("one slide is not a comparison", measure({"a.html": SHELL})["pairs"] == 0)
    ok("no slides is not a crash", measure({})["verdict"] == "ok")
    ok("an empty slide scores zero rather than dividing by zero",
       similarity(Counter(), Counter({"a": 1})) == 0.0)

    ok("the fail line sits well clear of both fitted decks",
       mb["median"] < WARN_AT < FAIL_AT < mt["median"],
       f"{mb['median']} < {WARN_AT} < {FAIL_AT} < {mt['median']}")

    # THE 2026-08-19 DEFECT, replayed. Two slides that draw nothing alike, each carrying the
    # standing masthead the coherence upgrade put on every frame.
    MAST = ('<style>.tx-frame{position:absolute;inset:0}.tx-wordmark{font-size:25px;'
            'letter-spacing:.16em}.tx-counter{font-variant-numeric:tabular-nums}</style>'
            '<div class="tx-frame" data-decorative>'
            '<svg class="tx-star" viewBox="0 0 26 26"><polygon points="1,2"/></svg>'
            '<div class="tx-wordmark">TEXAS AI DOCKET</div>'
            '<div class="tx-kicker">ERCOT MARKET NOTICE</div>'
            '<div class="tx-site">texasaidocket.com</div>'
            '<div class="tx-counter">03 / 08</div></div>')
    art_a = '<script>stoneGround(); embossMonthSheet(cellW, deadline); rakingShadow();</script>'
    art_b = '<script>voronoiPartition(seeds); neatline(); hatchCell(idx);</script>'
    bare = similarity(normalise(art_a), normalise(art_b))
    with_mast = similarity(normalise(art_a + MAST), normalise(art_b + MAST))
    ok("the standing masthead does not put a floor under an unrelated pair",
       with_mast <= bare + 0.02, f"bare {bare:.4f} against {with_mast:.4f} with the masthead")
    ok("...and the frame is removed with its subtree, not up to the first close tag",
       "wordmark" not in strip_masthead(MAST) and "counter" not in strip_masthead(MAST)
       and "DOCKET" not in strip_masthead(MAST), strip_masthead(MAST))
    ok("...and its css rules go with it", "letter-spacing" not in strip_masthead(MAST),
       strip_masthead(MAST))
    ok("a slide with no masthead is untouched",
       strip_masthead(art_a) == art_a)
    ok("...so a deck that never carried one measures exactly as it did before",
       normalise(art_b) == normalise(strip_masthead(art_b)))
    # The drawing must still be visible through the strip, or this traded one blindness for another.
    ok("two slides that DO share a drawing still score high through the masthead",
       similarity(normalise(art_a + MAST), normalise(art_a + MAST)) == 1.0)

    if failures:
        print(f"\nbespoke_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nbespoke_check self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--slides-dir")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.slides_dir:
        ap.print_help()
        return 0

    d = Path(a.slides_dir)
    slides = {p.name: p.read_text(encoding="utf-8") for p in sorted(d.glob("slide-*.html"))}
    if not slides:
        print(f"bespoke_check: no slides in {d}", file=sys.stderr)
        return 1
    return report(measure(slides))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"bespoke_check: broke: {exc}", file=sys.stderr)
        sys.exit(1)
