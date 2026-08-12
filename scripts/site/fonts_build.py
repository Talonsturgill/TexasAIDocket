#!/usr/bin/env python3
"""fonts_build.py — the three brand faces, subset and packed for the web.

WHY THIS EXISTS

`config/brand.yaml` names Fraunces, Manrope and JetBrains Mono, `theme.py` writes them into
every font stack, and `assets/fonts/` holds all three as committed TrueType. None of that put a
font in front of a reader. Nothing served them, no `@font-face` rule existed, and every visitor
fell back to Georgia, system-ui and whatever monospace their machine happened to have. The
config said one thing and the page did another, which is the failure this whole port is built to
catch, arriving in the one place the port audit was not looking: an asset rather than a script.

WHY THE OUTPUT IS COMMITTED AND NOT BUILT ON EVERY BUILD

`docs/` has to be byte-identical to a rebuild, which is the guarantee that the published site is
exactly what the ledgers produce. Subsetting is not byte-stable across `fonttools` versions, so
running it inside the site build would make that guarantee depend on a pinned compression
library. Instead the web fonts are generated ONCE by this script, committed under
`assets/fonts/web/`, and COPIED verbatim by the site build. Copying is deterministic. This is the
same discipline `assets/geo/tx-places.json` is held to.

WHY THE ATTRIBUTION IS READ AND NOT TYPED

All three faces are SIL Open Font License 1.1, and the repository is public, so the licence and
its copyright line have to ship beside the fonts. Both are recorded in each font's own `name`
table, so this script READS them out of the binary. A copyright line typed from memory is a
number typed by a person, in the sense CLAUDE.md means it: unverifiable, and wrong in a way
nothing downstream would catch.

    fonts_build.py                  regenerate assets/fonts/web/ (needs fonttools + brotli)
    fonts_build.py --manifest       print what is committed, no dependencies needed
    fonts_build.py --self-test      check the committed output is present and consistent
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "assets" / "fonts"
WEB = SRC / "web"
MANIFEST = WEB / "manifest.json"

# The three faces the SITE uses. `assets/fonts/` carries eight, because the carousel draws on a
# wider library per deck, but a website that ships eight families ships none of them well.
FACES = [
    # (source file, web basename, CSS family, weight range, style, axis limits)
    #
    # AXES ARE PINNED TO WHAT THE SITE ACTUALLY USES, which is most of the saving. Fraunces
    # ships four axes and the site varies one. `opsz` is Fraunces' optical size, and pinning it
    # to 40 is a design decision rather than a size decision: this face is used for headings
    # only, and a display optical size is what a heading wants. `SOFT` and `WONK` are the
    # family's playful axes and are pinned to their defaults, because a docket is not the place.
    # Carrying all four unpinned cost 145 KB for a face used on four selectors.
    ("Fraunces-Var.ttf", "fraunces", "Fraunces", "400 700", "normal",
     {"wght": (400, 700), "opsz": 40, "SOFT": 0, "WONK": 0}),
    ("Manrope-Var.ttf", "manrope", "Manrope", "300 700", "normal", {"wght": (300, 700)}),
    ("JetBrainsMono-Regular.ttf", "jetbrainsmono", "JetBrains Mono", "400", "normal", {}),
]

# WHAT TO KEEP, and the part that is easy to get wrong.
#
# Our own copy is plain English, so Basic Latin plus Latin-1 would cover every word this project
# writes. It would NOT cover what this project QUOTES. Every claim carries a source's verbatim
# words, house style explicitly stops at the quotation mark, and a filing routinely contains a
# section sign, an em dash, curly quotes or an ellipsis. Subsetting those away would render a
# quotation with a box in it, or silently in a fallback face, which is a worse failure than a
# larger file: the quote is the mechanism the whole product rests on.
UNICODES = (
    "U+0000-00FF,"          # Basic Latin and Latin-1: our copy, plus degree, section, accents
    "U+0131,U+0152-0153,"   # dotless i and the OE ligatures, standard web-font practice
    "U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
    "U+2000-206F,"          # general punctuation: dashes, curly quotes, ellipsis, primes, dagger
    "U+2070-209F,"          # super and subscripts, for units in a quoted passage
    "U+20A0-20BF,"          # currency
    "U+2100-214F,"          # letterlike: numero, degrees C and F, trademark
    "U+2190-21FF,"          # arrows, used by the ask box's route rendering
    "U+2202,U+2206,U+220F,U+2211-2212,U+2215,U+221A,U+221E,U+2248,U+2260,U+2264-2265,"
    "U+25A0-25FF,"          # geometric shapes, for a bullet or a box glyph in a quoted table
    "U+FEFF,U+FFFD"
)

LICENCE_NOTE = """SIL Open Font License 1.1
=========================

The three typefaces served by this site are used under the SIL Open Font License, Version 1.1,
which permits embedding and redistribution. The licence text and its FAQ are published by SIL at
https://openfontlicense.org.

The copyright line and licence statement below are read directly out of each font's own `name`
table by scripts/site/fonts_build.py, so they are the fonts' own words rather than a
transcription.

{bodies}
The files in this directory are SUBSETS of the originals, produced by fonttools. The unmodified
originals are committed in the parent directory. No font here is renamed, and the reserved font
name provisions of the licence are therefore untouched.
"""


def _read_names(path: Path) -> dict:
    """Copyright, family, version and licence, out of the font's own name table."""
    from fontTools.ttLib import TTFont                              # noqa: PLC0415
    want = {0: "copyright", 1: "family", 5: "version", 13: "licence", 14: "licence_url"}
    out: dict = {}
    font = TTFont(path, lazy=True)
    try:
        for rec in font["name"].names:
            key = want.get(rec.nameID)
            # Platform 3 is the Windows/Unicode table, which is the one that is always present
            # and always UTF-16. Reading platform 1 as well would give the same strings twice.
            if key and rec.platformID == 3 and key not in out:
                out[key] = " ".join(str(rec).split())
    finally:
        font.close()
    return out


def build() -> int:
    try:
        from fontTools import subset                                # noqa: PLC0415
        from fontTools.ttLib import TTFont                          # noqa: PLC0415
        import brotli                                               # noqa: F401,PLC0415
    except ImportError:
        print("fonts_build: needs fonttools and brotli. pip install fonttools brotli",
              file=sys.stderr)
        return 2

    WEB.mkdir(parents=True, exist_ok=True)
    entries, bodies = [], []

    from fontTools.varLib import instancer                          # noqa: PLC0415

    for src_name, base, family, weight, style, axes in FACES:
        src = SRC / src_name
        if not src.exists():
            print(f"fonts_build: missing source {src}", file=sys.stderr)
            return 2

        names = _read_names(src)
        out = WEB / f"{base}.woff2"

        opts = subset.Options()
        opts.flavor = "woff2"
        opts.with_zopfli = False
        # Keep the variable axes. A variable font at one weight range is smaller than two static
        # cuts of it, and the display face genuinely uses more than one weight.
        opts.retain_gids = False
        opts.desubroutinize = False
        opts.layout_features = ["*"]
        # The name table is what carries the licence. Dropping it to save bytes would strip the
        # attribution off a font we are redistributing.
        opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
        opts.name_legacy = False
        opts.notdef_outline = True
        opts.recalc_bounds = True

        font = TTFont(src)
        # SUBSET FIRST, THEN INSTANCE, and the order is load-bearing rather than stylistic.
        # Instancing first leaves the variation table describing glyphs the subsetter is about
        # to remove, and fontTools then raises KeyError on the first glyph that carries no
        # deltas of its own (`space`, in Manrope). Subsetting first hands the instancer a font
        # whose glyph set and variation data already agree.
        subsetter = subset.Subsetter(options=opts)
        subsetter.populate(unicodes=subset.parse_unicodes(UNICODES))
        subsetter.subset(font)
        if axes and "fvar" in font:
            # Pinning an axis to a number removes it. Narrowing it to a pair keeps it over a
            # smaller range. Both shrink the delta tables, which is where a variable font's
            # weight actually lives.
            font = instancer.instantiateVariableFont(font, axes, updateFontNames=False)
        font.flavor = "woff2"
        font.save(out)
        font.close()

        before, after = src.stat().st_size, out.stat().st_size
        entries.append({
            "file": out.name, "family": family, "weight": weight, "style": style,
            "bytes": after, "source": src_name, "source_bytes": before,
            "copyright": names.get("copyright", ""),
            "version": names.get("version", ""),
            "licence": names.get("licence", ""),
            "licence_url": names.get("licence_url", ""),
        })
        bodies.append(
            f"{family}\n{'-' * len(family)}\n"
            f"{names.get('copyright', '')}\n"
            f"{names.get('licence', '')}\n"
            f"Version: {names.get('version', '')}\n"
            f"Served as: {out.name}\n")
        print(f"  {family:16} {before:>8,} -> {after:>7,} bytes  "
              f"({100 * after / before:.0f}% of the original)")

    MANIFEST.write_text(json.dumps({"faces": entries}, indent=2) + "\n", encoding="utf-8")
    (WEB / "OFL.txt").write_text(LICENCE_NOTE.format(bodies="\n".join(bodies)), encoding="utf-8")

    total = sum(e["bytes"] for e in entries)
    print(f"fonts_build: {len(entries)} face(s), {total:,} bytes total, "
          f"manifest and licence written to {WEB.relative_to(REPO_ROOT)}/")
    return 0


def manifest() -> dict:
    """What is committed. Reads the manifest only, so the site build needs no font tooling.

    A MISSING MANIFEST RAISES. Returning an empty face list instead was the exact failure this
    module was written to end, rebuilt one layer up: `theme.css` would emit no `@font-face` rule
    while still writing Fraunces, Manrope and JetBrains Mono into every font stack, so the whole
    site would publish looking fine and silently serving Georgia to every reader. The same rule
    `tokens()` follows applies here, fail loudly rather than render a grey approximation.
    """
    if not MANIFEST.exists():
        raise FileNotFoundError(
            f"{MANIFEST} is missing. The site cannot serve its typefaces without it. "
            f"Run: pip install fonttools brotli && python3 scripts/site/fonts_build.py")
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not doc.get("faces"):
        raise ValueError(f"{MANIFEST} lists no faces, so nothing would be served")
    return doc


def face_css(url_prefix: str) -> str:
    """The `@font-face` block, derived from the manifest so it can never name a missing file."""
    out = []
    for f in manifest()["faces"]:
        out.append(
            f'@font-face{{font-family:"{f["family"]}";'
            f'src:url("{url_prefix}{f["file"]}") format("woff2");'
            f'font-weight:{f["weight"]};font-style:{f["style"]};font-display:swap}}')
    return "".join(out)


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    m = manifest()
    ok("the web fonts are committed", len(m["faces"]) == len(FACES),
       f"{len(m['faces'])} in the manifest, {len(FACES)} expected")

    for f in m["faces"]:
        path = WEB / f["file"]
        ok(f"{f['family']} is on disk", path.exists(), str(path))
        if path.exists():
            ok(f"...and the manifest's byte count is right for {f['family']}",
               path.stat().st_size == f["bytes"],
               f"{path.stat().st_size} on disk, {f['bytes']} recorded")
        # Serving a font without its licence is the part that is actually a problem, so it is
        # checked rather than assumed.
        ok(f"...and {f['family']} carries its copyright line",
           bool(f["copyright"]) and "Copyright" in f["copyright"], f["copyright"])
        ok(f"...and {f['family']} is under the Open Font License",
           "Open Font License" in f["licence"], f["licence"][:60])

    ok("the licence file ships beside the fonts", (WEB / "OFL.txt").exists())

    css = face_css("fonts/")
    ok("every committed face reaches a @font-face rule",
       all(f["file"] in css for f in m["faces"]) and css.count("@font-face") == len(m["faces"]))
    ok("...and nothing is referenced that is not committed",
       all((WEB / f["file"]).exists() for f in m["faces"]))
    ok("the fonts swap rather than blocking the first paint", "font-display:swap" in css)

    # A WEB FONT IS A COST A READER PAYS ON A PHONE. The whole point of subsetting is that the
    # three faces together stay under what one unsubset TrueType would have cost.
    total = sum(f["bytes"] for f in m["faces"])
    ok("three faces cost less than 200 KB in total", total < 200_000, f"{total:,} bytes")

    if failures:
        print(f"\nfonts_build self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\nfonts_build self-test: all passed ({total:,} bytes of type)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", action="store_true", help="print the committed manifest")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.manifest:
        print(json.dumps(manifest(), indent=2))
        return 0
    return build()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"fonts_build: broke: {exc}", file=sys.stderr)
        sys.exit(2)
