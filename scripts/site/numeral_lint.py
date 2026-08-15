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

    THE CHECK IS PER NUMERAL TOKEN, NEVER PER SUBSTRING. This is the whole correctness of
    the gate and the first version got it wrong in a way that disabled it completely. That
    version deleted every authorised string from the text and reported whatever digits
    survived. Authorise the single digits 0 through 9, which any real page does the moment
    it prints a day of the month or a count of four, and `8,927` is deleted one character
    at a time by four separate authorisations that have nothing to do with it. Nothing
    survives, so nothing is ever reported. **Every numeral on the site dissolved from the
    inside and the build stayed green.** Tokenise first, then ask of each whole token
    whether the build computed THAT number.

    A COMPUTED PHRASE IS STILL CONSUMED WHOLE, FIRST. "4pm to 5pm" is one computed label
    and tokenising it would authorise a bare 4 and a bare 5 anywhere on the page. A phrase
    is an authorised string carrying a character outside `[0-9,.]`, which is exactly the
    condition that makes it impossible for a phrase to sit inside a numeral token and
    split one the way the old scheme did.

    SVG GEOMETRY IS STRIPPED. Those coordinates are computed from the data by definition,
    there are hundreds per chart, and none is a figure a reader reads. Authorising them
    individually would bury a real violation inside a wall of noise.

    MARKUP IS STRIPPED. A viewBox, a width, a colour hex and a date in an attribute are not
    reader copy. Only what a person actually reads is checked.

WHAT IT CANNOT DO. A figure that genuinely equals one the build computed passes wherever it
appears on that page, because the two are the same string and nothing distinguishes them. So a
count of 13 written into a sentence about something else passes on a page that legitimately
prints 13. That is a real edge and it is bounded by the value being right anyway.
"""
from __future__ import annotations

import html as _html
import re
import sys

SVG_BLOCK = re.compile(r"<svg\b.*?</svg>", re.DOTALL | re.IGNORECASE)

# SCRIPT AND STYLE ARE NOT READER COPY, and leaving them in made this gate unusable on
# any page that carries the shell.
#
# It went unnoticed because the gate had only ever been pointed at the grid watch and
# water watch page BODIES, which are fragments with no script in them. The first build
# that ran it across the whole site failed every single page on the `8` in
# `scrollY>8`, which is a threshold in a scroll handler and is not a published figure by
# any reading. A gate that fires on all 48 pages for a reason that is never the reader's
# problem is a gate somebody switches off, so the exemption is part of the scanner
# rather than 48 authorisations.
SCRIPT_BLOCK = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)

# A `<cite>` IS THE TITLE OF A WORK, AND A WORK'S TITLE IS NOT OUR FIGURE TO AUTHORISE.
#
# `house_style_check` already strips `<cite>` for exactly this reason: rewriting a source's own
# words to fit house style falsifies them. The same argument governs numerals. TCEQ really did
# name a notice "Cancelation of Public Meeting: Fermi Equipment Holdco, LLC, 183462, PSDTX1704",
# and the Texas Water Development Board really does meet at 1700 Congress Avenue. Those are
# identifiers inside quoted material, not measurements this build computed, and authorising
# them one by one would grow the allowlist by every permit number the record ever cites.
#
# The exemption is NARROW because `<cite>` is narrow: it marks a title and nothing else. A
# figure in our own sentence beside a citation is still read and still has to trace to data.
CITE_BLOCK = re.compile(r"<cite\b.*?</cite>", re.DOTALL | re.IGNORECASE)
TAG = re.compile(r"<[^>]+>")

# A NUMERAL TOKEN ENDS ON A DIGIT. `\d[\d,]*` swallows the comma in "In 2026, the" and
# hands back the token "2026,", which then matches no authorised value and fails a page
# for its own punctuation. The old scheme never noticed because it deleted "2026" as a
# substring and left the comma behind as debris.
NUMERAL = re.compile(r"\d(?:[\d,]*\d)?(?:\.\d+)?")

# A PHRASE is an authorised string carrying a character a numeral token cannot contain.
# That test is what stops a phrase from splitting a figure it merely overlaps.
_PHRASE_CHAR = re.compile(r"[^0-9,.]")


def scan(html_body: str, authorised: set[str]) -> list[str]:
    """Every numeral in the reader facing copy that traces to no computation."""
    # ENTITIES ARE DECODED, because the scanner has to read what the reader reads. An
    # apostrophe escaped as `&#x27;` is an apostrophe on screen and a stray 27 to a regex,
    # and the site footer carries two of them, so every page on the site reported a
    # phantom 27 that no reader could see. Decoded after the tags come out, so an escaped
    # `&lt;div&gt;` sitting in copy cannot turn itself back into markup and vanish.
    text = _html.unescape(TAG.sub(" ", CITE_BLOCK.sub(" ", SCRIPT_BLOCK.sub(" ", SVG_BLOCK.sub(" ", html_body)))))
    phrases = [a for a in authorised if a and _PHRASE_CHAR.search(a)]
    # A PHRASE IS REMOVED AT A TOKEN BOUNDARY, NEVER AS A BARE SUBSTRING.
    #
    # The comment above says longest-first is what stops a phrase splitting a figure it
    # merely overlaps, and that only holds when a longer authorised phrase covers the same
    # span. It did not here. The water watch page prints "Amarillo 42.0%", the set carried a
    # bare "0%" from an unrelated computation, and `str.replace` took the "0%" out of the
    # middle of the percentage and left "42." behind. The scanner then reported a stray 42
    # that no reader could see and no page had printed, on a figure that was correct.
    #
    # It stayed hidden because 42 happened to be authorised site wide by an unrelated docket
    # count, so the page passed. Growing the record from 13 items to 58 changed those counts,
    # the coincidence lapsed, and four phantom numerals appeared on a page nobody had touched.
    # A GATE THAT PASSES BY COLLISION IS NOT PASSING.
    #
    # The boundary is asserted on both sides: a phrase may not begin in the middle of a
    # number, and may not end immediately before more digits.
    for v in sorted(phrases, key=len, reverse=True):
        text = re.sub(r"(?<![0-9.,])" + re.escape(v) + r"(?![0-9])", " ", text)
    return sorted({m.group(0) for m in NUMERAL.finditer(text)
                   if m.group(0) not in authorised})


class Authorised:
    """The set a page builds as it computes, so authorising and rendering cannot drift.

    Add the FORMATTED string, the one that will actually appear. A minus sign is punctuation
    rather than part of a numeral and the scanner never sees one, so a negative figure is
    registered under both forms. Storage is negative most days and it would otherwise fail the
    gate that exists to protect it.

    AN INTEGER IS ALSO REGISTERED COMMA GROUPED, because a count and its thousands separated
    rendering are the same computed quantity and the choice between them is typography. This
    is the one widening the gate is entitled to, and it is safe only because the value on both
    sides came out of the same computation. It is not a licence to authorise a rounding, which
    is a different number and has to be computed as one.
    """

    def __init__(self):
        self._s: set[str] = set()

    def add(self, *vals) -> "Authorised":
        for v in vals:
            if v is None or isinstance(v, bool):
                continue
            s = str(v)
            self._s.add(s)
            if s.startswith("-"):
                self._s.add(s[1:])
            if isinstance(v, int):
                self._s.add(f"{v:,}")
                self._s.add(f"{abs(v):,}")
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

    # THE DEFECT THAT DISABLED THIS GATE ENTIRELY, replayed. Every real page authorises all
    # ten single digits within a few counts and dates. Under substring deletion that made
    # every multi digit figure on the site dissolve one character at a time, so the gate
    # could not fail on anything and forty-eight pages reported clean for two waves.
    every_digit = Authorised().add(*range(10))
    check("authorising every single digit does not dissolve a four digit figure",
          scan("<p>Roughly 8,927 megawatts.</p>", every_digit.set) == ["8,927"],
          str(scan("<p>Roughly 8,927 megawatts.</p>", every_digit.set)))
    check("...nor a decimal",
          scan("<p>about 8.9 gigawatts</p>", every_digit.set) == ["8.9"],
          str(scan("<p>about 8.9 gigawatts</p>", every_digit.set)))
    check("...and the digits it did authorise still pass",
          not scan("<p>7 rooms, 4 counties</p>", every_digit.set),
          str(scan("<p>7 rooms, 4 counties</p>", every_digit.set)))

    # THE TOKEN BOUNDARY. A numeral ends on a digit, so sentence punctuation is not part of
    # the figure. Substring deletion hid this by leaving the comma behind as debris.
    check("a trailing sentence comma is not part of the numeral",
          not scan("<p>In 2026, it opened.</p>", Authorised().add(2026).set),
          str(scan("<p>In 2026, it opened.</p>", Authorised().add(2026).set)))
    check("a full stop is not part of the numeral",
          not scan("<p>It was 8.</p>", Authorised().add(8).set))
    check("an integer is authorised comma grouped as well as bare",
          not scan("<p>8,927 and 8927</p>", Authorised().add(8927).set),
          str(scan("<p>8,927 and 8927</p>", Authorised().add(8927).set)))
    check("a near miss of an authorised figure still fails",
          scan("<p>8,297</p>", Authorised().add(8927).set) == ["8,297"])
    check("a longer figure containing an authorised one still fails",
          scan("<p>18,927</p>", Authorised().add(8927).set) == ["18,927"])
    check("True is not the number one",
          scan("<p>1</p>", Authorised().add(True).set) == ["1"])

    b = Authorised().add("3", "83.1")
    check("an authorised short figure does not authorise a longer one containing it",
          not scan("<p>83.1</p>", b.set), str(scan("<p>83.1</p>", b.set)))
    check("...and 3 inside 83.1 is not a licence for 133",
          scan("<p>133</p>", b.set) == ["133"], str(scan("<p>133</p>", b.set)))

    # THE WATER WATCH FAULT, kept as a case because it survived in the repository for as long
    # as an unrelated docket count happened to equal the phantom it produced.
    pct = Authorised()
    pct.add("0%", "6%", "42.0%", "76.6%")
    check("a short authorised phrase does not eat the middle of a longer figure",
          not scan("<p>Amarillo 42.0% and 76.6% of capacity</p>", pct.set),
          str(scan("<p>Amarillo 42.0% and 76.6% of capacity</p>", pct.set)))
    check("...and the same phrase standing alone is still authorised",
          not scan("<p>The residual is 0% today.</p>", pct.set),
          str(scan("<p>The residual is 0% today.</p>", pct.set)))
    check("...while an unauthorised percentage is still caught",
          scan("<p>Storage sits at 51.4% today.</p>", pct.set) == ["51.4"],
          str(scan("<p>Storage sits at 51.4% today.</p>", pct.set)))

    check("a digit inside a computed phrase does not authorise a different figure",
          scan("<p>4pm to 5pm, and also 4,500 more</p>", a.set) == ["4,500"],
          str(scan("<p>4pm to 5pm, and also 4,500 more</p>", a.set)))
    check("a phrase cannot split a figure it overlaps",
          scan("<p>4pm to 5pm and 483.19</p>", a.set) == ["483.19"],
          str(scan("<p>4pm to 5pm and 483.19</p>", a.set)))

    check("a negative figure is authorised by its formatted form",
          not scan("<p>Storage ran -15,002 MWh.</p>", a.set))

    check("SVG geometry is not reader copy",
          not scan('<svg viewBox="0 0 720 260"><path d="M12.5,300 L44,9"/></svg>', a.set))
    check("...but copy beside a chart still is",
          scan('<svg><path d="M1,2"/></svg><p>then 999 happened</p>', a.set) == ["999"])
    check("a script is not reader copy",
          not scan("<script>if(scrollY>8){go(42)}</script>", a.set))
    check("a style block is not reader copy",
          not scan("<style>.x{width:37px;margin:9em}</style>", a.set))
    check("...but copy after a script still is",
          scan("<script>var n=8</script><p>then 777 happened</p>", a.set) == ["777"])
    check("markup attributes are not reader copy",
          not scan('<div class="w-50" style="width:37.5%" data-n="12345"></div>', a.set))
    check("an escaped apostrophe is an apostrophe, not a 27",
          not scan("<p>Texas&#x27; grid</p>", set()),
          str(scan("<p>Texas&#x27; grid</p>", set())))
    check("...and a figure beside one is still read",
          scan("<p>Texas&#x27; 640 acres</p>", set()) == ["640"])
    check("an escaped tag in copy stays copy",
          scan("<p>&lt;div&gt; and 33</p>", set()) == ["33"],
          str(scan("<p>&lt;div&gt; and 33</p>", set())))

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
