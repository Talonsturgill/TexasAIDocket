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
    colons         HARD FAIL. A colon in prose is a label bolted onto a sentence that could
                   have opened with the thing itself. A clock time and a ratio are numbers
                   rather than punctuation and are exempt.
    semicolons     HARD FAIL. A full stop that lost its nerve. Write two sentences.
    comma after    HARD FAIL, at any length. No comma after a coordinating conjunction or a
    a conjunction  relative pronoun, and no hedge fenced off by a pair of commas. Write "A data
                   centre needs electricity. Most cooling designs need water too", never "A
                   data centre needs electricity and, in most cooling designs, water".
    comma density  Hard fail ABOVE THE CEILING FOR THE CALLING SURFACE. See below.

THE COMMA CEILING IS PER SURFACE, AND ONE OF THE TWO IS DELIBERATELY UNSET

A ceiling is a fact about a body of writing, so it is measured on the surface it governs and
never imported from another. `rate_problem` takes the ceiling as an ARGUMENT for exactly that
reason, so a measured number cannot leak onto an unmeasured surface.

    SITE_COMMA_CEILING      LIVE at 3.97, and a hard fail. Measured on the site's own running
                            prose, which is the surface `house_style_check.py` enforces on.
                            `docket_build.gate_house_style` applies the same number to the
                            record's reader copy.
    CAPTION_COMMA_CEILING   None, on purpose. No caption has shipped, so there is nothing to
                            measure and any number here would be borrowed. Every construction
                            rule above applies to a caption today. Only DENSITY waits, and
                            `config/parity_map.yaml` carries the unblock condition so it cannot
                            be quietly forgotten.

The sibling product's 6.2 is a fact about ITS captions. Copying it would be publishing a number
typed by a person from another product's writing, which is what the compute-not-generate law
forbids, and its own config records what that cost when it happened: an imported figure produced
a 29 percent cut where 10 percent was asked for.

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

# ---------------------------------------------------------------- punctuation the house drops
# COLONS AND SEMICOLONS. Both are a writer reaching for a joint instead of a full stop. A colon
# announces that something is coming rather than saying it, and a semicolon glues two sentences
# that would each be stronger alone. The cure for either is the same: end the sentence.
#
# A numeric colon is not punctuation. "5:00 p.m." is a time and "4.5:1" is a ratio, and both
# are quantities a reader needs intact.
COLON = re.compile(r"(?<!\d):(?!\d)")
SEMICOLON = re.compile(r";")

# A COMMA IMMEDIATELY AFTER A CONJUNCTION. This is the construction the owner flagged:
#
#     A data centre needs electricity and, in most cooling designs, water.
#
# The tell is the comma after "and". It interrupts a simple compound the moment before it
# lands, and the sentence has to be re-read. Almost nothing is lost by splitting it in two.
# Deliberately narrow: a comma after a coordinating conjunction is a construction, not a list,
# so this cannot fire on "caliche, rust and flare orange".
CONJ_COMMA = re.compile(r"\b(and|but|or|nor|yet|so|which|that|though|although),", re.IGNORECASE)

# Throat clearing set off by commas. Hedge furniture with no content, and each one is a place
# where a sentence pauses to comment on itself instead of continuing.
HEDGE = re.compile(
    r",\s*(however|therefore|moreover|nevertheless|nonetheless|of course|in fact|"
    r"that is|for example|for instance|in particular|in other words|as it happens|"
    r"needless to say|to be clear|in general|in short)\s*,", re.IGNORECASE)

# THE COMMA CEILING IS A PROPERTY OF A SURFACE, so it is a per-surface number and never a
# global one. A ceiling measured on one body of writing and enforced on another is a number
# typed by a person from somebody else's corpus, which is what the compute-not-generate law
# forbids, and config/parity_map.yaml records what that mistake cost the sibling product: an
# imported figure produced a 29 percent cut where 10 percent was asked for.
#
# WEBSITE. Measured on RUNNING PROSE, which is the surface the gate enforces on, counting only
# the commas a writer CHOSE, over the corpus AS IT STOOD BEFORE ANY COMMA RULE TOUCHED IT
# (main at 11f2918, 2026-08-12): 170 commas in 3,853 words across the 20 published pages
# carrying 80 words or more of it, which is 4.41 per hundred. Ten percent below what the
# surface shipped is 4.41 x 0.9, so the ceiling is 3.97.
#
# THREE THINGS THIS NUMBER GOT WRONG BEFORE IT GOT RIGHT, each of which made it a different
# number, and all three are the same mistake: measuring something other than what is enforced.
#
#   1 The first version measured WHOLE PAGE text at 5.92 and enforced on running prose, which
#     excludes headlines, chips and card titles. The ceiling was about a quarter looser than
#     the rule it claimed to apply.
#   2 The second counted every comma, including the one in "August 11th, 2026" and the
#     thousands separator in "6,180". Neither is a density decision, and the tell was that the
#     gate's own advice, split the sentence at the comma, cannot be followed at either.
#   3 The third measured the corpus AFTER a round of tightening under the first ceiling, which
#     is a RATCHET. Ten percent below an already-cut corpus cuts again, and three passes of
#     that arrive at zero. The baseline has to be the writing as it stood before the rule
#     existed, which is why the commit is named above.
#
# Recompute only when the corpus has grown enough that a new measurement means something, and
# measure the same three things: running prose, chosen commas, untouched writing.
#
# THE FIRST VERSION OF THIS NUMBER MEASURED THE WRONG SURFACE and is worth keeping in view. It
# was derived from whole-page text at 5.92 per hundred, then enforced against running prose,
# which excludes headlines, chips and card titles and measures 4.21. The ceiling was therefore
# about 27 percent looser than the rule it claimed to apply, and `brand.yaml` stated a
# `measured_over` that its own number contradicted. Eleven of twenty pages sat above a correctly
# derived ceiling while the gate reported clean.
#
# THE TEN PERCENT STEP IS A ONE TIME MOVE OFF AN UNCONSTRAINED CORPUS. Re-deriving it from a
# corpus this ceiling has already tightened is a ratchet with no floor, and three rounds of it
# would arrive at zero. Recompute only when the corpus has grown enough that the measurement
# means something new, and say so here with the date when you do.
SITE_COMMA_CEILING = 3.97
#
# CAPTIONS. No ceiling yet, ON PURPOSE. No caption has shipped, so there is nothing to measure
# and any number here would be borrowed. The construction rules below still apply to a caption
# at any length; only the DENSITY rule waits. Measure the mean across the first 20 shipped
# captions, take ten percent off it in code, and set this. Until then a caption's rate is
# reported and never failed on.
CAPTION_COMMA_CEILING = None
#
# The default for a caller that does not name its surface. Callers should name it.
COMMA_CEILING = CAPTION_COMMA_CEILING
COMMA_FLOOR_WORDS = 80          # below this a rate is noise, so it is measured and not judged

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


# COMMAS A WRITER CANNOT CHOOSE. The date comma in "August 11th, 2026" is required by this
# project's own date rule, and the thousands separator in "6,180" is required by how a number is
# written. Neither is a density decision, and the tell is that the gate's own advice, "split the
# sentence at the comma", is impossible at either one. Counting them punished an item for citing
# three dates and handed back a fix nobody could apply.
STRUCTURAL_COMMA = re.compile(
    rf"\b(?:{MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?,(?=\s*\d{{4}})|(?<=\d),(?=\d{{3}}\b)",
    re.IGNORECASE)


def comma_rate(body: str) -> tuple[float, int, int]:
    """Commas per 100 words, counting only the ones a writer chose to put there.

    Measured every run so the ceiling can be computed rather than guessed.
    """
    words = len(re.findall(r"\b[\w'-]+\b", body))
    commas = STRUCTURAL_COMMA.sub(" ", body).count(",")
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
    if COLON.search(prose):
        problems.append("colon: the house does not use them. A colon announces that something "
                        "is coming instead of saying it. End the sentence and start the next")
    if SEMICOLON.search(prose):
        problems.append("semicolon: the house does not use them. It glues two sentences that "
                        "would each be stronger alone. Use a full stop")
    for m in set(CONJ_COMMA.findall(prose)):
        problems.append(f'comma after "{m}": this interrupts the sentence the moment before '
                        f"it lands, so a reader has to go back. Split it in two")
    for m in set(HEDGE.findall(prose)):
        problems.append(f'"{m}" set off by commas: throat clearing. The sentence is stronger '
                        f"without it")

    for m in NUM_RANGE.finditer(prose):
        before = prose[max(0, m.start() - 28):m.start()]
        if IDENT_INTRO.search(before):
            continue                       # a room, a docket, a section: an identifier
        msg = f'range "{m.group(0)}": write it "X to Y"'
        if msg not in problems:
            problems.append(msg)
    return problems


def rate_problem(text: str, ceiling: float | None = COMMA_CEILING) -> str | None:
    """The comma rate, judged only where a rate means anything, against the SURFACE's ceiling.

    `ceiling` is None where the surface has not been measured yet. That is not a loophole, it is
    the honest state of a surface with no corpus: the rate is still computed and reported, and
    the construction rules still apply, but nothing is failed against a number nobody measured.

    Under COMMA_FLOOR_WORDS a single comma swings the number by whole points, so a short block
    is measured and reported and never failed on density alone.
    """
    rate, commas, words = comma_rate(text)
    if ceiling is None or words < COMMA_FLOOR_WORDS or rate <= ceiling:
        return None
    over = round(rate - ceiling, 2)
    cut = int(commas - (ceiling / 100.0) * words) + 1
    return (f"comma rate {rate} per 100 words, over the {ceiling} ceiling by {over}. "
            f"Split about {cut} sentence(s) at the comma. Never delete the comma and leave a "
            f"run-on")


def run(text: str, *, quiet: bool = False) -> int:
    problems = check(text)
    rate, commas, words = comma_rate(text)
    rp = rate_problem(text)
    if rp:
        problems.append(rp)

    if not quiet:
        ceil = ("no ceiling yet, measured after 20 shipped captions"
                if COMMA_CEILING is None else f"ceiling {COMMA_CEILING}")
        print(f"caption_check: {words} words, {commas} commas, {rate} per 100 words ({ceil})")

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
             "Filed by the commission, https://example.com/docket-2026, "
             "retrieved 2026-08-11.")
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

    # ---- PUNCTUATION THE HOUSE DROPS -------------------------------------------------
    ok("a colon fails", catches("Two feeds are read here: one for demand.", "colon"))
    ok("a semicolon fails", catches("It was filed; the hearing follows.", "semicolon"))
    ok("a time is not a colon", not catches("Comments close at 5:00 p.m.", "colon"))
    ok("a ratio is not a colon", not catches("Contrast reads 4.5:1 at worst.", "colon"))
    ok("a colon inside a URL is exempt",
       not catches("See https://example.com/order for it.", "colon"))
    ok("...and the fix is named, not just the fault",
       any("End the sentence" in x for x in check("Read here: one for demand.")))

    # THE CONSTRUCTION THE OWNER FLAGGED, verbatim.
    flagged = "A data centre needs electricity and, in most cooling designs, water."
    ok("the flagged comma-after-conjunction fails", catches(flagged, 'comma after "and"'))
    ok("...for the right reason", any("Split it in two" in x for x in check(flagged)))
    for c in ("but", "or", "which", "though"):
        ok(f'comma after "{c}" fails', catches(f"It held {c}, for a time, it fell.",
                                               f'comma after "{c}"'))
    ok("a list is not a conjunction comma",
       not catches("Caliche, rust and flare orange are the palette.", "comma after"))
    ok("a comma BEFORE and is fine, since that is a clause boundary",
       not catches("The rule passed, and the hearing closed.", "comma after"))

    ok("hedge furniture fails", catches("The order, however, was late.", "throat clearing"))
    ok("...and so does in fact", catches("It was, in fact, filed.", "throat clearing"))

    # ---- THE COMMA CEILING, per surface, computed from that surface's own copy ---------
    # The ceiling must BE the arithmetic it claims, not merely sit near it. Asserting the
    # relationship rather than the literal is what stops the two drifting apart, which is
    # exactly how the first version came to state a baseline measured on a different surface
    # from the one it was enforced against.
    ok("the site ceiling really is ten percent below its stated baseline",
       abs(SITE_COMMA_CEILING - round(4.41 * 0.9, 2)) < 0.005, str(SITE_COMMA_CEILING))
    ok("the caption ceiling is honestly absent until captions ship",
       CAPTION_COMMA_CEILING is None)
    # Long enough to clear COMMA_FLOOR_WORDS, or the rate is correctly not judged at all.
    heavy = ("The order, filed today, which runs long, was posted late, after review, " * 7 +
             "and the commission met.")
    ok("copy over the site ceiling fails on rate",
       rate_problem(heavy, SITE_COMMA_CEILING) is not None, f"{comma_rate(heavy)[0]}")
    ok("...and says how many sentences to split",
       "Split about" in (rate_problem(heavy, SITE_COMMA_CEILING) or ""))
    # THE HALF THAT MATTERS MOST: an unmeasured surface must not inherit a measured one's
    # number. The same copy that fails against the site ceiling is not failed against a
    # caption ceiling nobody has measured, and the construction rules still catch it.
    ok("...and the identical copy is NOT failed on a surface with no measurement",
       rate_problem(heavy, CAPTION_COMMA_CEILING) is None)
    # `heavy` is DENSE and grammatically clean, which is what makes it the density fixture: it
    # trips no construction rule at all. So the claim that construction survives an absent
    # ceiling needs its own fixture, or it would be proving nothing.
    ok("...and the density fixture is clean on construction, as a density fixture should be",
       not check(heavy), str(check(heavy)))
    ok("...while construction is still enforced where there is no ceiling",
       catches("It ran and, briefly, stopped.", "comma after")
       and rate_problem("It ran and, briefly, stopped.", CAPTION_COMMA_CEILING) is None)
    lean = " ".join(["The commission met and set a hearing for August 11th."] * 12)
    ok("lean copy passes the rate",
       rate_problem(lean, SITE_COMMA_CEILING) is None, str(comma_rate(lean)[0]))
    ok("a short block is not judged on rate, because one comma swings it",
       rate_problem("One, two, three.", SITE_COMMA_CEILING) is None)
    ok("...but a short block still fails on construction",
       catches("It ran and, briefly, stopped.", "comma after"))

    # THE COMMA MEASUREMENT, which is reported and deliberately not gated.
    rate, commas, words = comma_rate("One, two, three, four five six seven eight nine ten.")
    ok("the comma rate is measured per 100 words", commas == 3 and words == 10 and rate == 30.0,
       f"{commas}/{words}={rate}")
    # ONLY THE COMMAS A WRITER CHOSE. A date comma is required by this file's own date rule and
    # a thousands separator is required by how a number is written, so neither is a density
    # decision. The tell is that the gate's advice, split the sentence at the comma, cannot be
    # followed at either one. Counting them punished an item for citing three dates.
    ok("a date comma is not counted", comma_rate("Comments close September 4th, 2026.")[1] == 0,
       str(comma_rate("Comments close September 4th, 2026.")))
    ok("a thousands separator is not counted",
       comma_rate("The queue holds 6,180 megawatts.")[1] == 0)
    ok("...but a chosen comma in the same sentence still is",
       comma_rate("On September 4th, 2026, the commission met.")[1] == 1,
       str(comma_rate("On September 4th, 2026, the commission met.")))
    ok("...and a list comma between numbers still is",
       comma_rate("It holds 6,180, 4,200 and 900 megawatts.")[1] == 1,
       str(comma_rate("It holds 6,180, 4,200 and 900 megawatts.")))
    src = open(__file__, encoding="utf-8").read()
    ok("the ceiling's provenance is written down where it can be found",
       "4.41" in src and "3,853 words" in src)
    ok("...and it names the surface it was measured on, because the first one did not",
       "RUNNING PROSE" in src)

    # THE DOCSTRING IS ASSERTED ON, not the source. The two are different targets and the
    # difference matters: the header once said "MEASURED AND REPORTED, NOT FAILED" and "the
    # ceiling is deliberately not set yet" for as long as a live 5.33 was hard-failing three
    # gates, because the only test guarding it had been loosened from `in __doc__` to
    # `in open(__file__).read()`, which a comment anywhere in the file satisfies. A maintainer
    # reading the header would have believed density was unenforced.
    doc = __doc__ or ""
    ok("the module header states the ceiling is live rather than pending",
       "LIVE at" in doc and "HARD FAIL" in doc)
    ok("...and names both surfaces, so the per-surface rule is visible from the top",
       "SITE_COMMA_CEILING" in doc and "CAPTION_COMMA_CEILING" in doc)
    ok("...and every hard-fail rule appears in the header's list",
       all(w in doc for w in ("colons", "semicolons", "comma density")))
    ok("...and the header does not still claim density is unenforced",
       "NOT FAILED" not in doc and "DELIBERATELY NOT SET YET" not in doc)

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
