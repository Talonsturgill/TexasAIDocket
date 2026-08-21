#!/usr/bin/env python3
"""css_tokens.py — every custom property the stylesheets use is one they define.

WHY THIS EXISTS

CSS fails SILENTLY and it fails INVISIBLY. `stroke: var(--signal-link)` where the token is
actually `--sig-link` is not an error, it is a declaration the browser discards, and the element
simply renders with its initial value. A stroke goes to none. A fill goes to black. Nothing is
logged, no build step complains, and the page looks like a page that was designed that way.

It has cost this project three times, each the same shape: a stylesheet written from memory of a
token name rather than from the file that defines it. The last one drew forty four filaments of
a network diagram with no stroke at all, on a page whose whole subject is the filaments, and
every gate in the suite was green over it.

    A NAME THAT IS NOT DEFINED IS NOT A COLOUR. It is a missing declaration wearing one.

WHAT IT CHECKS

Every `var(--x)` in the built stylesheets resolves to a `--x:` definition somewhere in the
built stylesheets, or carries its own fallback. A fallback is an explicit decision and passes,
because `var(--x, #fff)` renders something the author chose either way.

The two halves are read from the SAME built output rather than from the source that wrote it,
so a token defined only in a sheet the page never loads is still reported.

A TOKEN SET ON THE ELEMENT COUNTS. The queue chart writes `style="--h:41.20%"` on each bar and
the sheet reads it back, which is a real definition living in the markup rather than the
stylesheet. A gate that reported that as missing would be reporting a correct product as a
violation, and that is how a gate gets switched off. So the built HTML is read for definitions
too, in the same pass.

    css_tokens.py                 # check docs/
    css_tokens.py --self-test     # hermetic
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

# A definition. `--x:` at the head of a declaration, which is the only place one can appear.
DEFINE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")
# A use. The fallback is everything after the first comma, and its presence is what excuses it.
USE = re.compile(r"\bvar\(\s*(--[A-Za-z0-9_-]+)\s*(,)?")


def defined(css: str) -> set[str]:
    """Names this stylesheet defines. A `var()` use also matches DEFINE inside the fallback of
    something like `var(--a, var(--b))`, so uses are cut out before the definitions are read."""
    return set(DEFINE.findall(USE.sub("var(", css)))


def used(css: str) -> list[tuple[str, bool]]:
    return [(m.group(1), bool(m.group(2))) for m in USE.finditer(css)]


def problems(sheets: dict[str, str], inline: set[str] | None = None) -> list[str]:
    have: set[str] = set(inline or ())
    for css in sheets.values():
        have |= defined(css)
    out = []
    for name, css in sorted(sheets.items()):
        seen = set()
        for token, fallback in used(css):
            if token in have or fallback or token in seen:
                continue
            seen.add(token)
            out.append(f"{name} uses {token}, which nothing defines and which has no fallback")
    return out


INLINE = re.compile(r'\bstyle="([^"]*)"|<style\b[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)


def sheets_in(docs: Path) -> dict[str, str]:
    return {str(p.relative_to(docs)): p.read_text(encoding="utf-8")
            for p in sorted(docs.rglob("*.css"))}


def inline_in(docs: Path) -> set[str]:
    """Custom properties the built pages set on elements or in a page level <style>."""
    out: set[str] = set()
    for p in sorted(docs.rglob("*.html")):
        for m in INLINE.finditer(p.read_text(encoding="utf-8")):
            out |= defined(m.group(1) or m.group(2) or "")
    return out


def self_test() -> int:
    checks = []

    def ok(name, cond, extra=""):
        checks.append(bool(cond))
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}{'' if cond else '  ' + str(extra)}")

    base = ":root { --night:#08060F; --sig-link:#7FB2D9; }"

    ok("a defined token passes",
       problems({"a.css": base + " .x { color:var(--night); }"}) == [])
    # The defect, replayed. Three letters different and the declaration is thrown away.
    ok("a token nothing defines fails",
       problems({"a.css": base + " .x { stroke:var(--signal-link); }"}) != [])
    ok("...and the report names the token",
       "--signal-link" in " ".join(
           problems({"a.css": base + " .x { stroke:var(--signal-link); }"})))
    ok("a fallback is an explicit decision and passes",
       problems({"a.css": base + " .x { stroke:var(--signal-link, #7FB2D9); }"}) == [])
    ok("a token defined in another sheet on the same site passes",
       problems({"a.css": base, "b.css": ".x { color:var(--sig-link); }"}) == [])
    # `var(--a, var(--b))` puts a USE inside a fallback, and the inner name is the one that has
    # to resolve. Reading definitions naively would mistake that inner `var(` for a definition
    # of `--b` and wave the whole chain through, which is the one shape where a fallback does
    # not save the declaration: if `--b` is undefined too, the property is still discarded.
    nested = ".x { color:var(--one, var(--two)); }"
    ok("a use inside a fallback is a use, not a definition",
       [p for p in problems({"a.css": nested}) if "--two" in p], problems({"a.css": nested}))
    ok("...and it passes once the inner token is defined",
       problems({"a.css": ":root{--two:#fff;}" + nested}) == [],
       problems({"a.css": ":root{--two:#fff;}" + nested}))
    ok("one report per token per sheet, not one per use",
       len(problems({"a.css": ".x{color:var(--z);} .y{color:var(--z);} .w{color:var(--z);}"})) == 1)
    ok("a sheet with no custom properties at all passes",
       problems({"a.css": ".x { color:#fff; }"}) == [])
    # The queue chart's bar height, set per element in the markup. Reporting it would be
    # reporting a correct product as a violation.
    ok("a token set inline on an element counts as defined",
       problems({"a.css": ".qb { height:var(--h); }"}, {"--h"}) == [])
    ok("...and without that markup it is still reported",
       problems({"a.css": ".qb { height:var(--h); }"}) != [])

    passed = sum(checks)
    print(f"\ncss_tokens self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--docs", default=str(DOCS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    docs = Path(a.docs)
    if not docs.exists():
        print("css_tokens: no docs/ built yet, nothing to check")
        return 0
    sheets = sheets_in(docs)
    if not sheets:
        print("css_tokens: no stylesheet in docs/, which is itself wrong", file=sys.stderr)
        return 1
    found = problems(sheets, inline_in(docs))
    if not found:
        n = sum(len(defined(c)) for c in sheets.values())
        print(f"css tokens: every var() resolves across {len(sheets)} sheet(s), {n} defined")
        return 0
    print(f"css_tokens: {len(found)} unresolved custom propert(ies)\n", file=sys.stderr)
    for p in found:
        print(f"  - {p}", file=sys.stderr)
    print("\n  A var() with no definition and no fallback is a declaration the browser throws\n"
          "  away. The element renders with its initial value and nothing reports it.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
