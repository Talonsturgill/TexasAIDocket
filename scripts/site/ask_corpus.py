#!/usr/bin/env python3
"""ask_corpus.py — what an answer is allowed to contain.

The written answer lane cannot mark its own homework. This file is the answer key, and it
guarantees two things the answering layer has no way to provide for itself.

  authorised_numerals   every numeral the model was actually shown. A reply containing a
                        numeral outside this set is refused rather than published. This is
                        numeral_lint moved from build time to answer time, enforcing the same
                        law on model prose that it enforces on the page.

  slugs                 every decision id. A citation to anything else is a failed check, so
                        a plausible looking link to a decision that does not exist can't be
                        returned.

DERIVED FROM THE PACK, NOT FROM THE LEDGER, AND THAT IS THE WHOLE POINT. The sibling product
authorises every numeral in its entire instrument series while showing the model only the
current reading, which makes its allow-list far more permissive than what the model actually
saw. Copying that here would not merely be loose, it would be useless. docs/weather.json is
231,769 bytes of time series, and authorising it would admit nearly every small number that
exists, at which point an invented figure passes by coincidence rather than by being true.

So the list is read off the pack's own text. The promise becomes exact and checkable.

    THE MODEL MAY STATE A NUMBER ONLY IF THAT NUMBER WAS IN WHAT IT WAS SHOWN.

TOKENISING HAS TO AGREE ACROSS THREE PLACES. numeral_lint reads the built page in Python, this
reads the pack in Python, and the worker's checker reads the model's reply in JavaScript. All
three use the same pattern, which takes 8,927 as ONE token rather than as 8 and 927. A checker
that split on the comma would authorise the digits either side of every thousands separator in
the record, which is most of the small numbers there are.
"""

import argparse
import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import ask_pack                                                    # noqa: E402
import docket_build as dk                                          # noqa: E402
import numeral_lint                                                # noqa: E402

LEDGER = Path(REPO) / "ledger" / "docket.json"
OUT_CORPUS = Path(REPO) / "docs" / "ask-corpus.json"
OUT_PACK = Path(REPO) / "docs" / "ask-pack.json"

# The one pattern, borrowed rather than retyped. Retyping it is how the page lint and the
# answer lint end up measuring different things.
NUMERAL = numeral_lint.NUMERAL


def normalise(tok: str) -> str:
    """One spelling per number.

    Commas go, so a model shown 8,927 may write 8927 and still pass. Leading zeros go, so the
    record's 2026-07-09 authorises the 9 in "July 9th". Trailing zeros after a decimal point
    go, so 76.50 and 76.5 agree. Without any of these the check would refuse correct answers,
    which reads to a visitor as the record being wrong.
    """
    tok = tok.replace(",", "")
    tok = tok.lstrip("0") or "0"
    if "." in tok:
        tok = tok.rstrip("0").rstrip(".") or "0"
    return tok


def numerals(text: str) -> set:
    """Every distinct number in a string, normalised."""
    return {normalise(m) for m in NUMERAL.findall(text)}


def build(today: str = None) -> dict:
    pack = ask_pack.build(today)
    items = dk.load(LEDGER)

    return {
        "generated": pack["generated"],
        "count": len(items),
        "slugs": sorted(it["id"] for it in items),
        # Read off the pack's text, which is the exact thing the model is handed.
        "authorised_numerals": sorted(numerals(pack["pack"])),
        "pack_chars": pack["chars"],
    }


def write(corpus_path: Path = OUT_CORPUS, pack_path: Path = OUT_PACK, today: str = None):
    corpus = build(today)
    pack = ask_pack.build(today)
    for path, blob in ((corpus_path, corpus), (pack_path, pack)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(blob, separators=(",", ":"), sort_keys=True),
                        encoding="utf-8")
    return corpus, pack


def self_test() -> int:
    ok = [True]

    def check(label, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
        if not cond:
            ok[0] = False

    print("normalising")
    for raw, want in (("07", "7"), ("0", "0"), ("00", "0"), ("76.50", "76.5"),
                      ("8,927", "8927"), ("1,781,547.9", "1781547.9"),
                      ("6.00", "6"), ("2026", "2026")):
        check(f"{raw} normalises to {want}", normalise(raw) == want, normalise(raw))

    print("tokenising, which has to match numeral_lint exactly")
    # The case that disables the whole gate if it is wrong. A thousands separator is part of
    # the number, not a boundary in it.
    check("8,927 is one token, not two",
          NUMERAL.findall("peak was 8,927 MW") == ["8,927"],
          str(NUMERAL.findall("peak was 8,927 MW")))
    check("a decimal survives",
          NUMERAL.findall("76.5 percent") == ["76.5"])
    check("the pattern is numeral_lint's own object", NUMERAL is numeral_lint.NUMERAL)

    c = build()
    allowed = set(c["authorised_numerals"])

    print("the allow-list covers what the model is shown")
    pack = ask_pack.build()["pack"]
    missing = [t for t in numerals(pack) if t not in allowed]
    check("every numeral in the pack is authorised", not missing, str(missing[:3]))

    print("and it can still refuse")
    # A list that passes everything proves nothing.
    invented = [t for t in ("87654321", "99999.7", "123456789") if t in allowed]
    check("a number the record does not contain is NOT authorised", not invented,
          str(invented))

    print("the list is derived from the PACK and not the ledger")
    # The proof: numerals that live only in dropped fields must be absent. Source urls carry
    # control numbers and the pack drops them, so at least one ledger numeral should not be
    # authorised. If every ledger numeral is authorised, the trim silently stopped working.
    ledger_only = [t for t in numerals(LEDGER.read_text(encoding="utf-8"))
                   if t not in allowed]
    check("the ledger contains numerals the pack does not authorise", bool(ledger_only),
          f"{len(ledger_only)} dropped, e.g. {sorted(ledger_only)[:3]}")

    print("slugs")
    items = dk.load(LEDGER)
    check("every decision has a slug", len(c["slugs"]) == len(items) == c["count"],
          f"{c['count']} decisions")
    check("slugs are unique", len(c["slugs"]) == len(set(c["slugs"])))
    check("a slug that does not exist is not listed",
          "tx-9999-9999" not in c["slugs"])

    print("size")
    blob = json.dumps(c, separators=(",", ":"))
    check("the allow-list is a sane size", len(allowed) < 20_000,
          f"{len(allowed)} numerals, corpus {len(blob)} chars")

    print()
    print("ask_corpus self-test clean" if ok[0] else "ask_corpus self-test FAILED")
    return 0 if ok[0] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--date", help="ISO date")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    corpus, pack = write(today=args.date)
    print(f"ask corpus -> {OUT_CORPUS} ({corpus['count']} decisions, "
          f"{len(corpus['authorised_numerals'])} numerals)")
    print(f"ask pack   -> {OUT_PACK} ({pack['chars']} chars, "
          f"roughly {round(pack['chars'] / 4)} tokens)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
