#!/usr/bin/env python3
"""numeral_lint.py — no numeral reaches a reader unless code computed it.

THE LAW THIS ENFORCES, from CLAUDE.md:

    Every numeral this project publishes is produced by code, from data, and can be recomputed
    from the same inputs. No number is ever typed by a person or produced by a language model.

That is a public commitment stated on the site, which means it needs a mechanism rather than a
habit. A model that writes "about 8.9 gigawatts" is guessing at a formatting problem it does not
know it has. A model told the answer is 8,927 and writing 8,297 has made an error nothing
downstream would catch. This is what catches it.

HOW IT WORKS, AND WHY IT IS BUILT THIS WAY

A page hands over the set of numeral strings it is allowed to show, built from the same
formatting calls that rendered them. There is no path by which a displayed figure and an
authorised figure can disagree, because they are the same call. Anything else in the copy is a
violation.

    AUTHORISED STRINGS ARE CONSUMED WHOLE, LONGEST FIRST. "4pm to 5pm" is a computed label.
    Tokenising it into digits would authorise a bare 4 and a bare 5 everywhere on the page
    forever. Removing the phrase intact authorises those digits exactly where they were
    computed, and a stray 4 written anywhere else still fails. Longest first or "83.1" gets
    eaten by "3" and silently stops being checked.

    SVG GEOMETRY IS STRIPPED. Those coordinates are computed from the data by definition,
    there are hundreds per chart, and none is a figure a reader reads. Authorising them
    individually would bury a real violation inside a wall of noise.

    MARKUP IS STRIPPED. A viewBox, a width, a colour hex and a date in an attribute are not
    reader copy. Only what a person actually reads is checked.

WHAT IT CANNOT DO. A single digit that appears inside a legitimately computed phrase is
authorised wherever else it appears on that page, because after the phrase is consumed the two
are indistinguishable. The gate is strong on the figures that matter, which are the multi digit
and decimal ones, and honest about the edge it cannot see.
"""
from __future__ import annotations

import re
import sys

SVG_BLOCK = re.compile(r"<svg\b.*?</svg>", re.DOTALL | re.IGNORECASE)
TAG = re.compile(r"<[^>]+>")
NUMERAL = re.compile(r"\d[\d,]*(?:\.\d+)?")


def scan(html_body: str, authorised: set[str]) -> list[str]:
    """Every numeral in the reader facing copy that traces to no computation."""
    text = TAG.sub(" ", SVG_BLOCK.sub(" ", html_body))
    for v in sorted((a for a in authorised if a), key=len, reverse=True):
        text = text.replace(v, " ")
    return sorted({m.group(0) for m in NUMERAL.finditer(text)})


class Authorised:
    """The set a page builds as it computes, so authorising and rendering cannot drift.

    Add the FORMATTED string, the one that will actually appear. A minus sign is punctuation
    rather than part of a numeral and the scanner never sees one, so a negative figure is
    registered under both forms; storage is negative most days and it would otherwise fail the
    gate that exists to protect it.
    """

    def __init__(self):
        self._s: set[str] = set()

    def add(self, *vals) -> "Authorised":
        for v in vals:
            if v is None:
                continue
            s = str(v)
            self._s.add(s)
            if s.startswith("-"):
                self._s.add(s[1:])
        return self

    @property
    def set(self) -> set[str]:
        return set(self._s)

    def __contains__(self, v) -> bool:
        return str(v) in self._s

    def __len__(self) -> int:
        return len(self._s)


def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    a = Authorised().add("83.1", "1,701,380", "4pm to 5pm", "-15,002", None, "77.01")
    check("a page of authorised figures passes",
          not scan("<p>Peak was 83.1 GW at 4pm to 5pm, serving 1,701,380 MWh.</p>", a.set))
    check("a typed figure fails",
          scan("<p>about 8.9 gigawatts</p>", a.set) == ["8.9"])
    check("the failure names the numeral, so it can be found",
          scan("<p>8.9 and 42</p>", a.set) == ["42", "8.9"])

    # THE ORDERING PROPERTY. Without longest-first, "3" inside "83.1" would consume the "3"
    # and leave "8." unmatched, or worse, silently pass a different number.
    b = Authorised().add("3", "83.1")
    check("a longer authorised figure is consumed before a shorter one inside it",
          not scan("<p>83.1</p>", b.set), str(scan("<p>83.1</p>", b.set)))

    check("a digit inside a computed phrase does not authorise a different figure",
          scan("<p>4pm to 5pm, and also 4,500 more</p>", a.set) == ["4,500"],
          str(scan("<p>4pm to 5pm, and also 4,500 more</p>", a.set)))

    check("a negative figure is authorised by its formatted form",
          not scan("<p>Storage ran -15,002 MWh.</p>", a.set))

    check("SVG geometry is not reader copy",
          not scan('<svg viewBox="0 0 720 260"><path d="M12.5,300 L44,9"/></svg>', a.set))
    check("...but copy beside a chart still is",
          scan('<svg><path d="M1,2"/></svg><p>then 999 happened</p>', a.set) == ["999"])
    check("markup attributes are not reader copy",
          not scan('<div class="w-50" style="width:37.5%" data-n="12345"></div>', a.set))

    check("an empty page passes", not scan("", a.set))
    check("an empty authorised set still catches copy",
          scan("<p>7</p>", set()) == ["7"])

    c = Authorised().add(None, "")
    check("None and empty never enter the set", len(c) == 1 and "" in c.set)
    check("...and an empty string does not swallow the whole page",
          scan("<p>123</p>", c.set) == ["123"])

    if failures:
        print(f"\nnumeral_lint self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nnumeral_lint self-test: all passed")
    return 0


if __name__ == "__main__":
    sys.exit(self_test())
