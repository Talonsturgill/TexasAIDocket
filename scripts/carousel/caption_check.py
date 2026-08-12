#!/usr/bin/env python3
"""caption_check.py — the house rules, enforced on published copy rather than remembered.

WHY A LINT AND NOT A STYLE GUIDE

Every rule below is one a careful writer would keep for a while and then drift on, because
each is invisible in the sentence that breaks it. An em dash reads fine. "Cannot" reads fine.
"August 11" reads fine until you read it aloud next to "August 11th" and hear that nobody talks
that way. A style guide catches those on the day somebody rereads it; a lint catches them on
every run forever.

WHAT IT CHECKS, AND WHY EACH ONE IS HERE

    dashes         An em or en dash is the single loudest tell of machine-written copy.
    quotes         Curly quotes come from a word processor nobody here is using.
    emojis         Not the register. Not once.
    dates          Ordinal, month first. "August 11th", never "11 August", never a bare
                   "August 11". Read it aloud: if it sounds like a person talking, it takes
                   the ordinal. ISO stays correct in a citation stamp or a ledger field.
    contractions   "Cannot" is a register this product does not use. "Can't".
    openers        A sentence never opens with "And" or "But".
    first person   Published copy has no "I", "we" or "our". The record speaks, not its author.
    ranges         "X to Y", never "X-Y".

    commas         MEASURED AND REPORTED, NOT FAILED. See below.

THE COMMA CEILING IS DELIBERATELY NOT SET YET

The sibling product enforces 6.2 commas per 100 words, which is ten percent below the mean it
measured across its own shipped captions. That number is a fact about ITS corpus. Copying it
here would be publishing a number typed by a person from another product's writing, which is
the exact thing this project's compute-not-generate law forbids, and the rule is "ten percent
below what each surface actually ships" rather than "6.2".

So this measures the rate, prints it, and records it. When twenty captions have shipped, the
ceiling gets computed from those twenty and turned on. `config/parity_map.yaml` carries that as
a deferred divergence with its unblock condition, so it cannot be quietly forgotten.

    caption_check.py --file out/<run>/caption.txt
    caption_check.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Months, for the date rules. Abbreviations are caught separately: "Aug 11" is not house style
# in a sentence either.
MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December")
MONTH_ABBR = r"\b(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\.?\s+\d{1,2}\b"

DASHES = re.compile(r"[—–‒―]")
CURLY = re.compile(r"[‘’“”]")
# A bare "August 11" with no ordinal. The lookahead lets "August 11th" and "August 2026" pass.
BARE_DATE = re.compile(rf"\b(?:{MONTHS})\s+\d{{1,2}}\b(?!\s*(?:st|nd|rd|th)\b)", re.IGNORECASE)
DAY_FIRST = re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{MONTHS})\b", re.IGNORECASE)
OF_MONTH = re.compile(rf"\bthe\s+\d{{1,2}}(?:st|nd|rd|th)\s+of\s+(?:{MONTHS})\b", re.IGNORECASE)
CANNOT = re.compile(r"\bcannot\b", re.IGNORECASE)
OPENER = re.compile(r"(?:^|(?<=[.!?])\s+|\n)\s*(And|But)\b")
FIRST_PERSON = re.compile(r"\b(?:I|I'm|I've|I'll|we|we're|we've|we'll|our|ours|us|my|mine)\b",
                          re.IGNORECASE)
# A numeric range written with a hyphen. Guarded so a bill number or a hyphenated word does
# not trip it.
NUM_RANGE = re.compile(r"(?<![\w-])\d[\d,]*(?:\.\d+)?\s*[-‐‑]\s*\d[\d,]*(?:\.\d+)?(?![\w-])")

# A HYPHENATED IDENTIFIER IS NOT A RANGE. "Commissioners Hearing Room 7-100" is a room, and
# rewriting it "7 to 100" would be nonsense that also loses the reader the room. The tell is
# always the noun in front of it, so that is what gets checked. Found by running this lint
# against the real record, which is the only place these show up.
IDENT_INTRO = re.compile(
    r"\b(?:room|rooms|suite|ste|project|projects|docket|dockets|control\s+number|"
    r"number|no\.?|section|sections|rule|rules|chapter|chapters|subchapter|item|items|"
    r"case|application|tariff|unit|building|bldg|box|phone|fax|zip|form|permit|"
    r"license|registration|account|invoice|order)\s*$", re.IGNORECASE)

# ISO dates are correct as a citation stamp. Stripped before the date rules so a source line
# does not read as a house-style violation.
ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
URL = re.compile(r"https?://\S+")


def _ordinal(month_day: str) -> str:
    """"August 11" to "August 11th", with the RIGHT suffix.

    A message that suggests "July 31th" teaches the writer nothing and costs the gate its
    credibility, which is most of what a gate has.
    """
    month, _, day = month_day.rpartition(" ")
    n = int(day)
    suf = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{month} {n}{suf}"


def emojis(text: str) -> list[str]:
    """Any pictographic character. Category So covers the emoji blocks and the dingbats."""
    out = []
    for ch in text:
        if unicodedata.category(ch) == "So" and ord(ch) > 0x2000:
            out.append(ch)
    return out


def comma_rate(body: str) -> tuple[float, int, int]:
    """Commas per 100 words. Measured every run so the ceiling can be computed, not guessed."""
    words = len(re.findall(r"\b[\w'-]+\b", body))
    commas = body.count(",")
    return (round(commas / words * 100, 2) if words else 0.0), commas, words


def check(text: str) -> list[str]:
    """Every house-rule violation in this copy, as sentences a writer can act on."""
    problems: list[str] = []
    # Citations are not prose. A URL and an ISO stamp are exempt from the sentence rules.
    prose = ISO.sub(" ", URL.sub(" ", text))

    for d in set(DASHES.findall(text)):
        problems.append(f"dash {d!r}: no em or en dashes anywhere. Split the sentence, or "
                        f"write the range as X to Y")
    for q in set(CURLY.findall(text)):
        problems.append(f"curly quote {q!r}: straight quotes only")
    for e in set(emojis(text)):
        problems.append(f"emoji {e!r}: not the register, not once")

    for m in set(BARE_DATE.findall(prose)):
        problems.append(f'"{m}": dates take the ordinal. Write "{_ordinal(m)}". '
                        f"Read it aloud: nobody says a bare date in a sentence")
    for m in set(DAY_FIRST.findall(prose)):
        problems.append(f'"{m}": month first. Write "August 11th", never "11 August"')
    for m in set(OF_MONTH.findall(prose)):
        problems.append(f'"{m}": drop "the" and "of". Write "August 11th"')
    for m in set(re.findall(MONTH_ABBR, prose)):
        problems.append(f'"{m}": spell the month out in a sentence')

    for m in set(CANNOT.findall(prose)):
        problems.append(f'"{m}": never "cannot", always "can\'t"')
    for m in set(OPENER.findall(prose)):
        problems.append(f'a sentence opens with "{m}": rewrite the opening')
    for m in set(FIRST_PERSON.findall(prose)):
        problems.append(f'first person "{m}": published copy has no I, we or our. '
                        f"The record speaks, not its author")
    for m in NUM_RANGE.finditer(prose):
        before = prose[max(0, m.start() - 28):m.start()]
        if IDENT_INTRO.search(before):
            continue                       # a room, a docket, a section: an identifier
        msg = f'range "{m.group(0)}": write it "X to Y"'
        if msg not in problems:
            problems.append(msg)
    return problems


def run(text: str, *, quiet: bool = False) -> int:
    problems = check(text)
    rate, commas, words = comma_rate(text)

    if not quiet:
        print(f"caption_check: {words} words, {commas} commas, {rate} per 100 words")
        # MEASURED, NOT GATED. The ceiling is computed from this product's own shipped copy
        # once there is enough of it; see the module docstring.
        print("  comma rate is recorded, not enforced: the ceiling is computed from this "
              "product's first twenty shipped captions, never copied from another product")

    if problems:
        print(f"\ncaption_check: {len(problems)} house-rule violation(s)\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    if not quiet:
        print("caption_check: clean")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def catches(text, needle):
        return any(needle in p for p in check(text))

    clean = ("The commission set a hearing for August 11th. Comments close September 3rd at "
             "5:00 p.m. central. The filing runs 40 to 60 pages and can't be searched. "
             "Source: https://example.com/docket-2026 retrieved 2026-08-11.")
    ok("house-clean copy passes", not check(clean), str(check(clean)))

    # THE DASH RULE.
    ok("an em dash fails", catches("Load rose sharply—then fell.", "no em or en dashes"))
    ok("an en dash fails", catches("Pages 40–60 are redacted.", "no em or en dashes"))
    ok("a hyphenated word is fine", not catches("A well-sited data centre.", "dash"))

    # THE DATE RULES. These are the ones a writer drifts on.
    ok("a bare date fails", catches("The hearing is August 11.", "dates take the ordinal"))
    ok("...and names the fix", catches("The hearing is August 11.", "August 11th"))
    ok("the suggested ordinal is the RIGHT one, not a blanket th",
       catches("Filed July 31.", "July 31st") and catches("Filed May 22.", "May 22nd")
       and catches("Filed June 3.", "June 3rd") and catches("Filed April 12.", "April 12th"),
       str([p for p in check("Filed July 31.") if "ordinal" in p]))
    ok("an ordinal date passes", not catches("The hearing is August 11th.", "ordinal"))
    ok("day-first fails", catches("The hearing is 11 August.", "month first"))
    ok('"the 11th of August" fails', catches("Filed the 11th of August.", 'drop "the"'))
    ok("an abbreviated month fails", catches("Filed Aug 11.", "spell the month out"))
    ok("a year after a month is not a date violation",
       not catches("Filed in August 2026 by the utility.", "ordinal"))
    ok("an ISO stamp in a citation is exempt",
       not check("Retrieved 2026-08-11 from the commission's filing system."),
       str(check("Retrieved 2026-08-11 from the commission's filing system.")))
    ok("a date inside a URL is exempt",
       not catches("See https://example.com/2026-08-11/order for the order.", "ordinal"))

    # REGISTER.
    ok('"cannot" fails', catches("The figure cannot be verified.", "always \"can't\""))
    ok('"can\'t" passes', not catches("The figure can't be verified.", "cannot"))
    ok('a sentence opening "And" fails', catches("Load rose. And it held.", 'opens with "And"'))
    ok('a sentence opening "But" fails', catches("Load rose. But it held.", 'opens with "But"'))
    ok('"and" mid-sentence is fine', not catches("Load rose and held.", "opens with"))
    ok("a first line opening And fails", catches("And then it closed.", 'opens with "And"'))

    ok("first person fails", catches("We verified the filing.", "first person"))
    ok("...including possessive", catches("Our reading of the order.", "first person"))
    ok('"us" as a word fails', catches("The order reached us late.", "first person"))
    ok("a word containing we is fine", not catches("The weather drove the peak.", "first person"))
    ok("a word containing I is fine", not catches("The Interconnection filed it.", "first person"))

    # RANGES AND PUNCTUATION.
    ok("a hyphen range fails", catches("The filing runs 40-60 pages.", "write it"))
    ok('"40 to 60" passes', not catches("The filing runs 40 to 60 pages.", "range"))
    ok("a bill number is not a range", not catches("SB 6 and HB 149 apply.", "range"))
    for ident in ("Commissioners Hearing Room 7-100 is open to the public.",
                  "Filed under Project 58000-2 at the commission.",
                  "See Section 39-101 of the code.",
                  "Control Number 2026-14341 in the filing system."):
        ok(f"an identifier is not a range: {ident.split()[0]}",
           not catches(ident, "range"), str([p for p in check(ident) if "range" in p]))
    ok("a real range still fails even near an identifier word",
       catches("The order in Room 7 runs 40-60 pages.", "write it"))
    ok("a curly apostrophe fails", catches("It can’t be verified.", "straight quotes"))
    ok("an emoji fails", catches("Big news \U0001F680 today.", "not the register"))
    ok("a degree sign is not an emoji", not catches("It hit 104 degrees.", "register"))

    # THE COMMA MEASUREMENT, which is reported and deliberately not gated.
    rate, commas, words = comma_rate("One, two, three, four five six seven eight nine ten.")
    ok("the comma rate is measured per 100 words", commas == 3 and words == 10 and rate == 30.0,
       f"{commas}/{words}={rate}")
    ok("a comma-heavy caption still passes, because the ceiling is not set yet",
       not check("The order, filed today, which runs long, was, in the end, posted."),
       "commas must not fail until the ceiling is computed from shipped copy")
    ok("the source of that decision is written down where it can be found",
       "parity_map" in __doc__ and "twenty" in __doc__)

    ok("empty copy is clean rather than a crash", not check(""))
    ok("a violation reports as an actionable sentence, not a code",
       all(len(p) > 20 and " " in p for p in check("Filed August 11—see 40-60.")))

    if failures:
        print(f"\ncaption_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\ncaption_check self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", help="path to the caption copy")
    ap.add_argument("--text", help="copy passed inline")
    ap.add_argument("--json", action="store_true", help="machine-readable result")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()
    if not (a.file or a.text):
        ap.print_help()
        return 0

    text = Path(a.file).read_text(encoding="utf-8") if a.file else a.text
    if a.json:
        rate, commas, words = comma_rate(text)
        problems = check(text)
        print(json.dumps({"ok": not problems, "problems": problems, "words": words,
                          "commas": commas, "commas_per_100_words": rate}, indent=2))
        return 1 if problems else 0
    return run(text)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"caption_check: broke: {exc}", file=sys.stderr)
        sys.exit(1)
