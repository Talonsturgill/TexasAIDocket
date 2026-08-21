#!/usr/bin/env python3
"""house_style_check.py — the house rules, checked against the site that actually shipped.

WHY THE BUILT SITE AND NOT THE SOURCE

The copy a reader sees is assembled from f-strings across several builders and from fields in
the ledger. Grepping the Python finds the literals and misses everything the record supplied,
and grepping the ledger finds the record and misses the prose around it. The rendered page is
the only place the whole sentence exists.

Run against the real `docs/` this found four violations in copy written the same day the rules
were restated: two "cannot", a "we", and an "ours". They were invisible in review because every
one of them reads perfectly well. That is the entire argument for a lint.

THE RULE THAT MAKES THIS CORRECT: A QUOTE IS NEVER LINTED

Every claim in this record carries the source's own words, verbatim, and that is the mechanism
the whole product rests on. A source writes "July 31" and uses a curly apostrophe and cites a
range as "7-100". Rewriting any of that to fit house style would be falsifying a quotation,
which is a far worse failure than an inconsistent date.

So house style governs OUR prose and stops at the quotation mark. `<blockquote>` and `<cite>`
are stripped before checking, along with SVG geometry and markup attributes. If a violation is
reported here it is in a sentence this project wrote and can freely rewrite.

    house_style_check.py                 # checks docs/
    house_style_check.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "carousel"))

import caption_check                                               # noqa: E402

DOCS = REPO_ROOT / "docs"

MAIN = re.compile(r"<main\b[^>]*>(.*)</main>", re.DOTALL | re.IGNORECASE)
# Quoted material and its attribution. Stripped, never linted. See the module docstring.
QUOTED = re.compile(r"<(blockquote|cite)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
SVG = re.compile(r"<svg\b.*?</svg>", re.DOTALL | re.IGNORECASE)
# Script and style CONTENT, not just their tags. Stripping tags alone leaves the code between
# them, and the ask page ships its whole engine and index inline: the lint then read a
# JavaScript identifier "i" as a first-person pronoun. Code is not reader-facing copy.
CODE = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
# TEXT IN THE READER'S VOICE, not the record's. The ask box's starter questions are phrased the
# way a person types them, which includes "What can I still comment on?". The no-first-person
# rule exists so the record does not speak as "we"; it was never meant to stop the page quoting
# the reader back to themselves. Marked explicitly at the source rather than inferred, so the
# exemption is a decision somebody made and can be found.
# `[a-z][a-z0-9]*` for the same reason the house-voice pattern below needs it: `[a-z]+` matches
# only the "h" of <h2> and then fails its own \b against the digit, so the exemption never fires
# on a heading. It went unnoticed while both exemptions were used on <div> and <span> only.
READER_VOICE = re.compile(r'<([a-z][a-z0-9]*)\b[^>]*\bdata-voice="reader"[^>]*>.*?</\1>',
                          re.DOTALL | re.IGNORECASE)
# THE HOUSE NAMING ITS OWN WORK, which is the one place "our" is not the record editorialising.
# The no-first-person rule is about CLAIMS: a docket item that says "we verified" has put an
# author between the reader and the source, and that is what it exists to stop. A shelf label
# over this site's own article and its own video makes no claim at all, it says whose shelf it
# is, and the owner asked for it in those words (2026-08-19).
#
# Narrow on purpose, and marked at the source rather than inferred, so it is a decision somebody
# made and can be found, exactly like the reader-voice exemption above. It does not license
# first person in a sentence that asserts anything.
# `[a-z0-9]+` and not `[a-z]+`: on <h2> the latter matches "h" and then fails its own \b
# against the "2", so the exemption silently never fired on any heading, which is the only
# place it is used.
HOUSE_VOICE = re.compile(r'<([a-z][a-z0-9]*)\b[^>]*\bdata-voice="house"[^>]*>.*?</\1>',
                         re.DOTALL | re.IGNORECASE)
TAG = re.compile(r"<[^>]+>")

# A DATE CHIP, AND THE ONE EXEMPTION IT HAS TO EARN.
#
# The deadline cards on the front page carry the date at display size, "SEP 8" over "23 days
# left". That is a calendar tile, not a sentence, and the date rules are written for sentences:
# their own message says "read it aloud, nobody says a bare date in a sentence". Nobody reads a
# tile aloud either.
#
# The rule above is emphatic that `data-prose="data"` narrows the DENSITY measurement and never
# the construction rules, so a bare date inside a chip is still a violation. That stays true.
# This is not that marker and it is not a region: it is `<time datetime="2026-09-08">`, and it is
# exempt only for as long as its visible text is a faithful rendering OF ITS OWN ATTRIBUTE.
#
# The check derives the permitted renderings here, from the ISO value, rather than importing
# them from the builder. A checker that asks the generator what the right answer is will agree
# with the generator about a wrong answer. Anything else inside a `<time>` is reported as its own
# violation and left in the prose stream, so the element cannot be used as a wrapper to smuggle
# a sentence past the date rules. That is the difference between an exemption that is a promise
# about content and one that is a promise about a region.
_MONTH_ONLY = re.compile(r"\d{4}-\d{2}")
TIME_EL = re.compile(r'<time\b[^>]*\bdatetime="([^"]+)"[^>]*>(.*?)</time>',
                     re.DOTALL | re.IGNORECASE)


def _renderings(iso: str) -> set:
    """Every way this project is allowed to print one date, derived from the date itself.

    A MONTH-PRECISION VALUE RENDERS A MONTH, which is the same promise one step up. A chart
    axis labels a month and not a day, and `<time datetime="2026-01">Jan</time>` satisfies this
    exemption's actual test exactly: the visible text is a faithful rendering of its own
    attribute. Without this the axis had to print a bare "Jan" next to a figure, which the date
    rule correctly read as an abbreviated date loose in the prose stream.

    The day rules are untouched. `2026-01-08` still may not print as "Jan" here, because a
    value that knows its day and hides it is not rendering itself faithfully.
    """
    # A YEAR-PRECISION VALUE RENDERS A YEAR, which is the same promise one step up again. The
    # record's year view heads each block with the year it holds, and `<time datetime="2021">`
    # is exactly what that is. The rejections that matter are untouched: a value that knows its
    # month or its day and prints only the year is still not rendering itself faithfully,
    # because those values do not reach this branch.
    if re.fullmatch(r"\d{4}", iso.strip()):
        return {iso.strip()}
    if _MONTH_ONLY.fullmatch(iso.strip()):
        y, m = (int(x) for x in iso.strip().split("-"))
        d = _dt.date(y, m, 1)
        # THE WALL CALENDAR FORM. A month page prints its own number beside its name and year,
        # which is what the paper object on a wall does and what the record's month view now
        # does. It is a faithful rendering of a month-precision value: every part of it comes
        # out of the value and none of it is a day. Without this the header had to choose
        # between the house's own date rule and looking like a calendar.
        return {f"{d:%b}", f"{d:%b}".upper(), f"{d:%B}", f"{d:%B} {y}", f"{y}-{m:02d}",
                f"{m:02d} {d:%B} {y}", f"{m:02d}{d:%B}{y}"}
    try:
        d = _dt.date.fromisoformat(iso[:10])
    except ValueError:
        return set()
    n = d.day
    suf = "th" if 11 <= n <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    # THE ORDINAL FORM WITH ITS YEAR. "August 10th, 2026" is the house form for a full date and
    # was the one shape this set did not list, so a <time> could render its own value correctly
    # in the house style and still be reported. It matters wherever a list spans years: the
    # registry roster runs from 2013 to this month, and "August 10th" alone does not identify a
    # row in it. The rejections that matter are untouched: "10 August", a bare "August 10", and
    # a day-precision value that prints only its month.
    return {f"{d:%b} {n}".upper(), f"{d:%B} {n}{suf}", d.isoformat(),
            f"{d:%B} {d.year}", f"{d:%b} {n}", f"{d:%B} {n}{suf}, {d.year}"}


def _time_chips(body: str) -> tuple:
    """Strip the `<time>` elements that render their own datetime. Report the ones that do not."""
    problems = []

    def sub(m):
        iso, inner = m.group(1), _html.unescape(TAG.sub("", m.group(2))).strip()
        allowed = _renderings(iso)
        if not allowed:
            problems.append(f'<time datetime="{iso}">: not a date this can verify')
            return m.group(0)
        if inner in allowed:
            return " "
        problems.append(f'"{inner}" in a <time datetime="{iso}"> does not render that date. '
                        f"A time element is exempt from the date rules only while its text is "
                        f"what its own attribute says")
        return m.group(0)

    return TIME_EL.sub(sub, body), problems


# STRUCTURED DATA rendered as chips, labels and lists. A comma between two of Oncor's 22
# affected counties is a delimiter, not a writer leaning on commas, and a metadata row repeated
# once per card multiplies that delimiter by the number of cards. Measuring comma DENSITY over
# it says nothing about whether the prose breathes.
#
# This exemption is deliberately narrower than the others: it is subtracted from the DENSITY
# measurement only, and never from the construction rules. An em dash or a bare date inside a
# chip is still a violation, so the marker cannot be used to smuggle bad copy past the gate. It
# only stops a county list from being read as a sentence.
DATA_REGION = re.compile(r'<([a-z]+)\b[^>]*\bdata-prose="data"[^>]*>.*?</\1>',
                         re.DOTALL | re.IGNORECASE)
# Paragraph containers: where running prose lives. Used only to scope the comma DENSITY rule.
PARAGRAPH = re.compile(r"<(p|li)\b[^>]*>(.*?)</\1>", re.DOTALL | re.IGNORECASE)


def _stripped(page_html: str) -> str:
    """The shared work: main, minus quotes, code, SVG, reader voice and verified date chips."""
    m = MAIN.search(page_html)
    body = m.group(1) if m else page_html
    body = HOUSE_VOICE.sub(" ", READER_VOICE.sub(" ", QUOTED.sub(" ", CODE.sub(" ", SVG.sub(" ", body)))))
    return _time_chips(body)[0]


def time_chip_problems(page_html: str) -> list:
    """The `<time>` elements that claimed the date exemption without earning it."""
    m = MAIN.search(page_html)
    return _time_chips(m.group(1) if m else page_html)[1]


def our_prose(page_html: str) -> str:
    """What this project wrote, with everything it merely reproduced taken out."""
    return _less_names(_html.unescape(TAG.sub(" ", _stripped(page_html))), page_html)


def our_sentences(page_html: str) -> str:
    """The RUNNING PROSE on a page: paragraphs and list items, minus data, quotes and code.

    Commas per hundred words is a measure of how densely a SENTENCE is punctuated, so it is only
    meaningful over text that is made of sentences. A page is also full of text that is not:
    headlines, chips, counters, card titles. A docket title reads "PUCT Project 58000,
    rulemaking to update ERCOT transmission cost recovery, comment deadline reached", where both
    commas are structural, and an index page carrying a dozen of those would fail a density rule
    for doing its job. Neither the title nor the chip gets any better for being rewritten.

    So the rate is measured over paragraph containers. Every other rule still reads the whole
    page through `our_prose`, so nothing escapes the gate by living in a heading. Only the
    density heuristic narrows, and it narrows to the text the heuristic was designed for. The
    report prints the measured word count beside the rate, so the coverage is visible rather
    than assumed.
    """
    body = DATA_REGION.sub(" ", _stripped(page_html))
    runs = [inner for _tag, inner in PARAGRAPH.findall(body)]
    return _less_names(_html.unescape(TAG.sub(" ", " ".join(runs))), page_html)


#

# THE HEAD IS PUBLISHED COPY TOO, and it was the one place nothing looked. Everything above scopes
# to `<main>`, which is right for the page a reader scrolls and wrong for the sentence that
# represents the page everywhere else. The home page's description carried a banned colon from the
# day it was written, and it is the line that appears in a search result, in a shared link preview
# and in a chat unfurl. More people read that sentence than read the page.
#
# Checked for CONSTRUCTION only, never for comma density: these are two or three sentences and the
# density rule has an eighty word floor, so pointing it at them would measure noise.
HEAD = re.compile(r"<head\b[^>]*>(.*?)</head>", re.DOTALL | re.IGNORECASE)
HEAD_TEXT = re.compile(
    r"<title\b[^>]*>(?P<title>.*?)</title>"
    r"|<meta\b[^>]*\b(?:name|property)=\"(?:description|og:title|og:description)\"[^>]*"
    r"\bcontent=\"(?P<content>[^\"]*)\"",
    re.DOTALL | re.IGNORECASE)


# A PROPER NAME IN A TITLE, DECLARED BY THE PAGE THAT CARRIES IT.
#
# `<cite>` exempts a quoted name in the body and there is no markup to do that inside a <title>.
# The registry names a facility "Riot Corsicana Data Center I", and that trailing roman numeral
# is a first person pronoun to this checker, which was right on the letter and wrong on the
# page. Renaming the facility to satisfy the lint would publish a name no filing uses.
#
# So a page DECLARES its proper names and this strips exactly those strings, marked at the
# source in the same spirit as the reader-voice and house-voice exemptions above. It cannot
# widen by accident: only the exact declared string is removed, never a pattern, and a page
# that declares nothing is checked exactly as before.
#
# IT APPLIES TO THE BODY TOO, and for one run it did not. The head was where the problem was
# first found, so the strip went in beside the metadata reader and nowhere else. A facility
# dossier then printed "Galaxy Helios I" as the owner of record, in the body, and the same
# roman numeral was reported again in the same words. The registry spells that row with a
# letter where it spells the next one with a digit, which is the fact the page exists to show,
# so the name was never the thing to change.
#
# The declaration is an ATTRIBUTE, so it has to be read off the markup before the tags come
# out. Both callers do that and then subtract the declared strings from the text.
PROPER_NAME = re.compile(r'\bdata-proper-name="(?P<name>[^"]*)"', re.IGNORECASE)


def _declared(page_html: str) -> list[str]:
    """The proper names this page declares, longest first so a name is never half removed by a
    shorter one that happens to be its prefix."""
    found = {_html.unescape(g.group("name")).strip() for g in PROPER_NAME.finditer(page_html)}
    return sorted((n for n in found if n), key=len, reverse=True)


def _less_names(text: str, page_html: str) -> str:
    for name in _declared(page_html):
        text = text.replace(name, " ")
    return text


def page_metadata(page_html: str) -> str:
    """The reader-facing strings in the head: the title and the social descriptions."""
    m = HEAD.search(page_html)
    if not m:
        return ""
    found = [(g.group("title") or g.group("content") or "") for g in HEAD_TEXT.finditer(m.group(1))]
    return _less_names(_html.unescape(TAG.sub(" ", " ".join(found))), page_html)


def check_site(docs: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for page in sorted(docs.rglob("*.html")):
        try:
            text = page.read_text(encoding="utf-8")
        except OSError:
            continue
        prose = our_prose(text)
        problems = caption_check.check(prose)
        # An exemption that reports nothing when it is misused is a hole with a comment over it.
        problems += time_chip_problems(text)
        problems += [f"{p} (in the page metadata, which is what a search result shows)"
                     for p in caption_check.check(page_metadata(text))]
        # The rate is judged per PAGE, which is the unit a reader actually reads. A single
        # comma-heavy sentence can sit inside a page that breathes; a page whose average is over
        # the ceiling is a page that does not.
        running = our_sentences(text)
        # Measured on the same RUNNING PROSE scope as the comma rate, for the same reason. A chip,
        # a card and a heading are not sentences and a length rule has nothing to say about them.
        problems = problems + caption_check.long_sentences(running)
        rate = caption_check.rate_problem(running, caption_check.SITE_COMMA_CEILING)
        if rate:
            _r, _c, words = caption_check.comma_rate(running)
            problems = problems + [f"{rate}. Measured over {words} words of running prose"]
        if problems:
            out[str(page.relative_to(docs))] = problems
    return out


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    page = """<html><body><header>nav</header><main>
      <p>The commission set the hearing for August 11th.</p>
      <div class="claim">
        <blockquote>Comments are due August 21 and cannot be filed late.</blockquote>
        <cite>PUCT, Project 58000, retrieved 2026-08-11</cite>
      </div>
      <svg><text>40-60</text></svg>
    </main><footer>cannot</footer></body></html>"""

    prose = our_prose(page)
    ok("our own sentence survives the strip", "August 11th" in prose)
    ok("a quoted passage is removed before linting", "cannot be filed late" not in prose, prose)
    ok("...and so is its attribution", "Project 58000" not in prose)
    ok("SVG geometry is not prose", "40-60" not in prose)
    coded = our_prose('<main><p>Filed August 11th.</p>'
                      '<script>for (var i = 0; i < n; i++) { we.cannot(x); }</script>'
                      '<style>.a { width: 40-60px }</style></main>')
    ok("inline script is not prose", "cannot" not in coded and " i " not in f" {coded} ",
       coded)
    ok("inline style is not prose", "40-60" not in coded)
    ok("...and the sentence beside the code still is", "August 11th" in coded)
    voiced = our_prose('<main><p>Filed August 11th.</p>'
                       '<div data-voice="reader"><button>What can I comment on?</button></div>'
                       '</main>')
    ok("text marked as the reader's own voice is exempt", "What can I" not in voiced, voiced)
    ok("...and only what is marked", "August 11th" in voiced)

    # THE DATE CHIP EXEMPTION, PROVEN IN BOTH DIRECTIONS. It is worthless if it only ever
    # passes: the reason it exists is that a calendar tile is not a sentence, and the reason it
    # is safe is that the tile has to be showing its own datetime to get the exemption.
    chip = '<main><p>Filed August 11th.</p><time datetime="2026-09-08" class="big">SEP 8</time>'
    ok("a date chip rendering its own datetime is exempt from the date rules",
       not [p for p in caption_check.check(our_prose(chip + "</main>"))
            if "month" in p or "ordinal" in p],
       str(caption_check.check(our_prose(chip + "</main>"))))
    ok("...and it is not reported as an unearned exemption either",
       time_chip_problems(chip + "</main>") == [])
    lying = '<main><time datetime="2026-09-08">AUG 31</time></main>'
    ok("a chip whose text is not its own datetime is reported",
       any("does not render that date" in p for p in time_chip_problems(lying)),
       str(time_chip_problems(lying)))
    ok("...and its text stays in the prose, so the date rules see it too",
       "AUG 31" in our_prose(lying))
    smuggle = ('<main><time datetime="2026-09-08">The deadline is Sep 8 and we cannot '
               'extend it.</time></main>')
    ok("a sentence wrapped in a time element does not escape the rules",
       any("cannot" in p for p in caption_check.check(our_prose(smuggle))),
       str(caption_check.check(our_prose(smuggle))))
    ok("a time element with an unparseable datetime is reported, not waved through",
       any("not a date this can verify" in p
           for p in time_chip_problems('<main><time datetime="soon">SEP 8</time></main>')))
    ok("an unmarked first person is still caught",
       any("first person" in p for p in
           caption_check.check(our_prose("<main><p>What can I comment on?</p></main>"))))
    ok("the footer is outside main and not checked", "cannot" not in prose)
    ok("a clean page reports nothing", not caption_check.check(prose),
       str(caption_check.check(prose)))

    # THE GATE MUST GO RED. A violation in OUR prose is caught even when a quote nearby holds
    # the identical text legitimately.
    bad = page.replace("<p>The commission set the hearing for August 11th.</p>",
                       "<p>The hearing is August 11 and we cannot verify it.</p>")
    probs = caption_check.check(our_prose(bad))
    ok("a bare date in our own prose fails", any("ordinal" in p for p in probs), str(probs))
    ok('"cannot" in our own prose fails', any("can't" in p for p in probs))
    ok("first person in our own prose fails", any("first person" in p for p in probs))
    ok("...while the identical words inside the quote stay exempt",
       len([p for p in probs if "can't" in p]) == 1,
       "the quote's 'cannot' must not be counted a second time")

    ok("a page with no main element is still checked rather than skipped",
       bool(our_prose("<html><body><p>Filed August 11.</p></body></html>").strip()))

    # THE DATA EXEMPTION, and its limit. It must take a county list out of the DENSITY
    # measurement and leave it inside every construction rule, or it becomes a way to smuggle
    # bad copy onto the page behind an attribute.
    chips = ('<main><p>The line crosses the counties below.</p>'
             '<p class="meta" data-prose="data">Borden, Bosque, Brown, Callahan, Coke</p>'
             '</main>')
    ok("a county list is not counted as prose density",
       "Bosque" not in our_sentences(chips), our_sentences(chips))
    ok("...and the sentence beside it still is", "crosses the counties" in our_sentences(chips))
    # A HEADLINE is not a sentence. A docket title's commas are structural and rewriting the
    # title to satisfy a density rule would make the record harder to read, not easier.
    headline = ('<main><h3>PUCT Project 58000, cost recovery, deadline reached</h3>'
                '<p>The commission set a hearing.</p></main>')
    ok("a headline is outside the density measurement",
       "58000" not in our_sentences(headline), our_sentences(headline))
    ok("...but a headline is still read by the construction rules",
       "58000" in our_prose(headline))
    ok("a bare date in a headline still fails",
       any("ordinal" in p for p in caption_check.check(
           our_prose("<main><h3>Closes August 11</h3></main>"))))
    ok("a list item counts as running prose",
       "heard the county" in our_sentences('<main><li>The board heard the county.</li></main>'))
    ok("...and the same list is STILL read by the construction rules",
       "Bosque" in our_prose(chips))
    ok("a bare date inside a data chip still fails",
       any("ordinal" in p for p in caption_check.check(our_prose(
           '<main><p class="meta" data-prose="data">Closes August 11</p></main>'))))
    # The rate is what the marker was added for, so prove the marker changes the verdict.
    heavy = ('<main><p>' + ("The commission set a hearing and heard from the county. " * 12) +
             '</p><p class="meta" data-prose="data">' +
             ("Borden, Bosque, Brown, Callahan, Coke, Coleman, Comanche. " * 6) + '</p></main>')
    ok("the rate fails when a chip row is counted",
       caption_check.rate_problem(our_prose(heavy), caption_check.SITE_COMMA_CEILING) is not None)
    ok("...and passes once the chip row is recognised as data",
       caption_check.rate_problem(our_sentences(heavy), caption_check.SITE_COMMA_CEILING) is None,
       str(caption_check.rate_problem(our_sentences(heavy), caption_check.SITE_COMMA_CEILING)))
    # And the rate must still be able to go red on genuine prose, or the exemption has quietly
    # disabled the whole rule.
    wordy = '<main><p>' + ("The commission, having heard, set a date, and then, later, "
                           "adjourned the meeting. " * 8) + '</p></main>'
    ok("a genuinely comma-heavy page still fails on rate",
       caption_check.rate_problem(our_sentences(wordy), caption_check.SITE_COMMA_CEILING) is not None)

    # ---- the sentence length backstop ----------------------------------------
    long_p = ("<main><p>" + " ".join(["word"] * 40) + ".</p></main>")
    ok("a forty word sentence trips the backstop",
       len(caption_check.long_sentences(our_sentences(long_p))) == 1)
    ok("...and a normal one does not",
       not caption_check.long_sentences(our_sentences(
           "<main><p>The commission set the hearing for August 11th.</p></main>")))
    # THE PSEUDO-SENTENCE TRAP. Three deadline cards on the front page measured as one 82 word
    # sentence, because card text carries no full stop and a naive split joins it all together.
    # That names the wrong problem and invites somebody to rewrite prose that was fine. Cards are
    # marked as data upstream; requiring terminal punctuation is the second guard.
    cards = ("<main>" + "".join(
        f"<li><span>Open to you</span><span>AUG {d}</span>"
        f"<h3>Federal comment window open on reactor licensing and siting modernization</h3>"
        f"<span>Public comment closes</span></li>" for d in (11, 21, 31)) + "</main>")
    ok("a run of chips with no full stop is not read as one long sentence",
       not caption_check.long_sentences(our_sentences(cards)),
       str(caption_check.long_sentences(our_sentences(cards)))[:90])

    # A DECLARED PROPER NAME, IN THE BODY. The head was covered from the day the mechanism went
    # in and the body was not, so the same roman numeral was reported twice in two places.
    named = ('<html><head><title>Galaxy Helios I</title></head><main>'
             '<article data-proper-name="Galaxy Helios I">'
             '<p>The owner of record is Galaxy Helios I on that row.</p>'
             '</article></main></html>')
    ok("a declared name in the body is not read as first person",
       not any("first person" in p for p in caption_check.check(our_prose(named))),
       str(caption_check.check(our_prose(named)))[:120])
    ok("...and the same name undeclared still fails",
       any("first person" in p for p in
           caption_check.check(our_prose(named.replace(' data-proper-name="Galaxy Helios I"', "")))))
    ok("a declaration removes only the string it declares",
       "on that row" in our_prose(named))
    ok("a declaration on one page does not travel to another",
       any("first person" in p for p in caption_check.check(our_prose(
           '<html><main><p>The owner of record is Galaxy Helios I on that row.</p></main></html>'))))

    if failures:
        print(f"\nhouse_style_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nhouse_style_check self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--docs", default=str(DOCS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    docs = Path(a.docs)
    if not docs.exists():
        print("house_style_check: no docs/ built yet, nothing to check")
        return 0

    found = check_site(docs)
    pages = sum(1 for _ in docs.rglob("*.html"))
    if not found:
        print(f"house style: clean across {pages} page(s)")
        return 0

    n = sum(len(v) for v in found.values())
    print(f"house_style_check: {n} violation(s) in copy this project wrote\n", file=sys.stderr)
    for page, problems in found.items():
        print(f"  {page}", file=sys.stderr)
        for p in problems:
            print(f"    - {p}", file=sys.stderr)
    print("\n  Quoted source text is exempt and was not checked. Everything above is a "
          "sentence\n  this project wrote and can rewrite. Fix it in the builder, not in "
          "docs/.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"house_style_check: broke: {exc}", file=sys.stderr)
        sys.exit(1)
