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
                   center needs electricity. Most cooling designs need water too", never "A
                   data center needs electricity and, in most cooling designs, water".
    comma density  Hard fail ABOVE THE CEILING FOR THE CALLING SURFACE. See below.
    hashtags       CAPTION ONLY, and a hard fail. Exactly the count `config/brand.yaml` sets,
                   standing alone on the last line, no duplicates. The post takes hashtags and
                   the slides and the site do not, and treating those as one rule is what shipped
                   a tagless post on 2026-08-18. Applied in `run()` and never inside `check()`,
                   because `check()` also judges the website.

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

# BRITISH SPELLING, WHICH IS INVISIBLE UNTIL SOMEBODY FROM TEXAS READS IT.
#
# "data centres" shipped across this site, on the one subject the record is most about. It is
# the exact shape of fault a lint is for: every instance reads fine, nothing objects, and the
# product quietly sounds like it was written somewhere else. It took the owner to catch it.
#
# The pairs are the ones this subject matter actually produces. `-ise` verbs are deliberately
# NOT here as a blanket rule, because "enterprise", "franchise", "advertise" and "comprise" are
# American too, and a rule that fires on those is a rule somebody switches off.
#
# THIS IS SPELLING, NOT QUOTATION. A verbatim quote keeps whatever the source wrote, and the
# callers already exclude quotes by construction.
BRITISH = {
    "centre": "center", "centres": "centers", "centred": "centered", "centring": "centering",
    "colour": "color", "colours": "colors", "coloured": "colored",
    "behaviour": "behavior", "behaviours": "behaviors",
    "neighbour": "neighbor", "neighbours": "neighbors",
    "neighbourhood": "neighborhood", "neighbourhoods": "neighborhoods",
    "labour": "labor", "harbour": "harbor", "favour": "favor", "favours": "favors",
    "favourite": "favorite", "honour": "honor", "rumour": "rumor", "vapour": "vapor",
    "metre": "meter", "metres": "meters", "litre": "liter", "litres": "liters",
    "fibre": "fibre-optic is a compound; the noun is fiber", "fibres": "fibers",
    "defence": "defense", "licence": "license", "offence": "offense", "practise": "practice",
    "programme": "program", "programmes": "programs",
    "modelling": "modeling", "modelled": "modeled", "labelled": "labeled",
    "travelled": "traveled", "cancelled": "canceled", "fuelled": "fueled",
    "analyse": "analyze", "analysed": "analyzed", "catalogue": "catalog",
    "grey": "gray", "storey": "story", "storeys": "stories",
    "aluminium": "aluminum", "sulphur": "sulfur",
}
BRITISH_RX = re.compile(r"\b(" + "|".join(sorted(BRITISH, key=len, reverse=True)) + r")\b",
                        re.IGNORECASE)
OPENER = re.compile(r"(?:^|(?<=[.!?])\s+|\n)\s*(And|But)\b")
# AN AGENDA ITEM NUMBER IS NOT FIRST PERSON. A period is a word boundary, so `\bI\b` matched
# the I in "No action taken due to I.3 failed", which is Brazoria County's own minute line and
# the best single fact the August 25th run had. The gate reported first person on a caption that
# contained none, and the only ways past it were to misquote the record or to drop the quote.
#
# A gate that can only be satisfied by damaging a verbatim quote is a gate that will be switched
# off, so the fix is here rather than in the copy. `I` is still first person everywhere else,
# including at the end of a sentence and before a comma. It is exempt only where a digit or a
# further Roman numeral follows the period, which is what an item identifier looks like and what
# a pronoun never does.
FIRST_PERSON = re.compile(r"\b(?:I(?!\.\s*[0-9IVX])|I'm|I've|I'll|we|we're|we've|we'll"
                          r"|our|ours|us|my|mine)\b", re.IGNORECASE)
# A ROMAN NUMERAL IS NOT A PRONOUN. "the 2027 State Water Plan (Phase I)" is the document's own
# name, and reporting it as a writer talking about themselves sends an editor looking for a
# first person that is not there. The anchor is the word in front, the same way an identifier
# is told from a range: a lone capital I after Phase, Part or Title is a numeral.
ROMAN_LABEL = re.compile(r"\b(?:Phase|Part|Title|Volume|Article|Book|Class|Type|Tier|Stage)\s+"
                         r"(?:I{1,3}|IV|VI{0,3}|IX|XI{0,3})\b")
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
    r"license|registration|account|invoice|order|"
    # An instrument's own file number, which is what a city or county actually calls the thing
    # it adopted. "Ordinance 2026-078" is a name. Rewriting it "2026 to 078" would leave a
    # reader unable to look it up, which is the whole point of printing it.
    r"ordinance|ordinances|resolution|resolutions|agreement|agreements|contract|"
    r"contracts|zone|matter|amendment|ord)\s*$", re.IGNORECASE)

# A ZIP+4 IS A ZIP, and the noun in front of it is a city and a state rather than the word
# "zip". "Austin, Texas 78711-3087" is the whole address of the office a comment is mailed to,
# and it is the one number on the page a reader might copy by hand. Matched on its own shape,
# five then four, immediately after a state, so it cannot reach an ordinary pair of figures.
ZIP_PLUS_FOUR = re.compile(r"(?:\b(?:Texas|TX|postal\s+code|zip(?:\s+code)?)\s*,?\s*)$",
                           re.IGNORECASE)

# "Ordinance 2026-078" is the NAME of a thing. "the amendment 4-1" is a vote on an amendment.
# Both put an identifier word immediately before a hyphenated pair, and the tell between them
# is the ARTICLE: a proper identifier does not take one and a common noun in a sentence does.
# Without this, adding `amendment` to the list above quietly exempted "passed the amendment
# 4-1", which is exactly the vote count the range rule exists to catch.
ARTICLED_NOUN = re.compile(r"\b(?:the|a|an|its|this|that|each|his|her|their|our)\s+\w+\s*$",
                           re.IGNORECASE)

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
#     A data center needs electricity and, in most cooling designs, water.
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

# SENTENCE LENGTH, AND WHY THIS NUMBER IS NOT MEASURED FROM OUR OWN WRITING.
#
# Owner's note, 2026-08-12: the writing here runs longer than the brand wants. The target lives in
# config/brand.yaml as a voice rule, one idea per sentence, because a target is a matter of taste
# and belongs where a writer reads it. This is the BACKSTOP, and a backstop needs a number.
#
# The comma ceiling was set at ten percent below its own measured corpus, and that only worked
# because it was stated as a one time move off an unconstrained corpus. Applied to sentence length
# the same method is a pure ratchet: every pass would measure a corpus the last pass had already
# cut, and three rounds arrive at nothing. So this is an EXTERNAL threshold. Plain-language
# guidance across style authorities puts comfortable running prose at fifteen to twenty words a
# sentence and treats thirty as the point where a reader has to re-read. Thirty is therefore a
# real edge rather than a reflection of the corpus, and it cannot creep, because it was never
# derived from us.
#
# It has headroom on purpose. The site's longest sentence measures 27 words, so this fails on
# regression rather than on today's writing, which is the job of a backstop. If a future pass wants
# the prose shorter than this, tighten the RULE in brand.yaml and leave the edge where it is.
SENTENCE_CEILING = 30

# ISO dates are correct as a citation stamp. Stripped before the date rules so a source line
# does not read as a house-style violation.
ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
URL = re.compile(r"https?://\S+")

# --------------------------------------------------------------------------- HASHTAGS
#
# THE POST TAKES HASHTAGS. THE SLIDES AND THE SITE DO NOT. That distinction is the whole rule,
# and collapsing it is what cost run No. 2 its tags.
#
# `config/brand.yaml` has always carried `linkedin_post.hashtags_exactly: 3`. It also carries
# `visual.on_slide_text_rules`, which says "no hashtags" about SLIDE text, where a hashtag would
# be absurd. `knowledge/carousel/CAPTION_CRAFT.md` then listed "any hashtag" under engagement
# bait, applying the slide rule to the post. The caption room reads CAPTION_CRAFT, so it wrote a
# caption with no tags, and nothing here checked, because this file had no hashtag rule at all.
#
# Run No. 1 on 2026-08-16 shipped "#GrimesCounty #ERCOT #Terafab". Run No. 2 on 2026-08-18
# shipped none. Two runs, two different answers to a question the config had already settled,
# and a fully green suite both times. That is the exact shape GATE_LESSONS.md is about: the rule
# existed, the surfaces disagreed, and no gate was connected to either.
#
# THE COUNT IS READ FROM brand.yaml AND NEVER TYPED HERE. brand.yaml is `human` owned, so the
# number stays a decision a maintainer makes in one place, and this file only enforces it. A
# missing file or a missing key FAILS rather than skips, because a hashtag gate that quietly
# turns itself off is worse than no hashtag gate: it reports clean on the run it should catch.
HASHTAG = re.compile(r"#[A-Za-z][A-Za-z0-9]*")
# What a tag may look like. A trailing "#" or "#2026" is a typo or a number, not a tag, and is
# reported rather than silently ignored.
MALFORMED_TAG = re.compile(r"#(?![A-Za-z])\S*|#[A-Za-z][A-Za-z0-9]*[^\sA-Za-z0-9#]+")


def linkedin_rule(key: str, kind):
    """One `linkedin_post` value from `config/brand.yaml`. Never a literal in this file.

    THE FOURTH INSTANCE OF THE SAME DEFECT (2026-08-25). `brand.yaml` has carried
    `caption_chars: [300, 900]`, `links_in_body: false` and `ends_with: engagement_question`ate
    the whole time, and this gate read only `hashtags_exactly`, so August 25th's caption shipped
    980 characters long, ending on a link, with the link in the body, past a green run. That is
    a rule stated in config, a surface keeping its own copy, and nothing in between checking they
    agree, which `CLAUDE.md` names three separate times as this project's recurring fault.

    Searched by key for the same reason `hashtags_required` searches: a gate that goes quiet
    because a maintainer moved a section fails open on the day it is needed.
    """
    import yaml
    doc = yaml.safe_load((REPO_ROOT / "config" / "brand.yaml").read_text(encoding="utf-8"))

    def find(node):
        if isinstance(node, dict):
            if isinstance(node.get("linkedin_post"), dict):
                got = node["linkedin_post"].get(key)
                if got is not None:
                    return got
            for v in node.values():
                got = find(v)
                if got is not None:
                    return got
        return None

    v = find(doc)
    if not isinstance(v, kind):
        raise SystemExit(
            f"caption_check: config/brand.yaml has no linkedin_post.{key}. That key is where this "
            f"is decided and the gate will not guess it. Restore the key rather than removing the "
            f"check")
    return v


def hashtags_required() -> int:
    """How many hashtags the post takes, per `config/brand.yaml`. Never a literal in this file."""
    import yaml
    path = REPO_ROOT / "config" / "brand.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))

    # Searched by key rather than by a fixed path. brand.yaml is human owned and its top level
    # has already been reorganised once, and a gate that goes quiet because a maintainer moved a
    # section is a gate that fails open on the day it is needed.
    def find(node):
        if isinstance(node, dict):
            if isinstance(node.get("linkedin_post"), dict):
                got = node["linkedin_post"].get("hashtags_exactly")
                if got is not None:
                    return got
            for v in node.values():
                got = find(v)
                if got is not None:
                    return got
        return None

    n = find(doc)
    if not isinstance(n, int):
        raise SystemExit(
            "caption_check: config/brand.yaml has no linkedin_post.hashtags_exactly. That key is "
            "where the post's hashtag count is decided, and this gate will not guess it. Restore "
            "the key rather than removing this check")
    return n


def post_shape_problems(text: str) -> list[str]:
    """The three `linkedin_post` rules that live in brand.yaml and had no gate (2026-08-25).

    Length, the link rule and the required ending. All three were stated in config, all three
    were broken on a run this file reported clean, and that is the fourth time this project has
    shipped a rule stated in one place and a surface keeping its own copy of it.

    POST LEVEL, and kept out of `check()` on purpose. `check()` is fed prose fragments by the
    suite and by other callers, and a caption length rule applied to a fragment fails everything.
    Same reason `hashtag_problems` is its own function, and the caption surface is the only
    caller of either.
    """
    problems: list[str] = []
    # THE THREE brand.yaml RULES THIS GATE NEVER READ (2026-08-25). Length, the link rule and
    # the required ending. All three were stated in config and all three were broken on a run
    # this file reported clean.
    lo, hi = linkedin_rule("caption_chars", list)
    n = len(text.strip())
    if not (lo <= n <= hi):
        problems.append(
            f"the caption is {n} characters and brand.yaml's linkedin_post.caption_chars band is "
            f"{lo} to {hi}. Over the top of it the stake sits below the mobile fold; under the "
            f"bottom of it there is no room for a source")
    body = HASHTAG.sub("", text).strip()
    if not linkedin_rule("links_in_body", bool):
        for hit in set(URL.findall(body)) | set(re.findall(r"\b[a-z0-9-]+\.(?:com|org|net|gov)\b",
                                                          body, re.I)):
            problems.append(
                f"link {hit!r} in the body: brand.yaml sets linkedin_post.links_in_body false, "
                f"because a link suppresses reach and the sources go in the first comment")
    if linkedin_rule("ends_with", str) == "engagement_question" and not body.rstrip().endswith("?"):
        tail = body.rstrip().split("\n")[-1][-70:]
        problems.append(
            f"the caption does not end on a question, and brand.yaml sets linkedin_post.ends_with "
            f"to engagement_question. It ends {tail!r}")

    return problems


def hashtag_problems(text: str, required: int | None = None) -> list[str]:
    """The post's hashtag block, judged. CAPTION SURFACE ONLY.

    Deliberately NOT part of `check()`. `check()` is imported by `docket_build`,
    `house_style_check` and `waterwatch_page` to judge the SITE's reader copy, and a hashtag rule
    living in there would demand hashtags on every page of the record. The post is the one
    surface this applies to, so it is applied on the one code path that reads a caption.

    Three things are checked and each has failed somewhere in this product's short life:
      count      exactly what brand.yaml says. Zero is the regression this gate exists for.
      placement  the tags are the LAST line and appear nowhere earlier. A tag mid-sentence is
                 the engagement-bait tic the craft doctrine is right to hate.
      duplicates two spellings of one tag is a wasted slot out of a very small budget.
    """
    required = hashtags_required() if required is None else required
    problems: list[str] = []
    body = ISO.sub(" ", URL.sub(" ", text))        # a URL fragment is not a tag

    tags = HASHTAG.findall(body)
    if len(tags) != required:
        problems.append(
            f"{len(tags)} hashtag(s), and the post takes exactly {required}. "
            f"config/brand.yaml sets the count and says niche over broad, at the very end. "
            f"A post that ships without them reaches the audience that already follows it")

    for m in set(MALFORMED_TAG.findall(body)):
        problems.append(f'"{m.strip()}" is not a hashtag: a tag is "#" then a letter, then '
                        f"letters and digits only")

    lowered = [t.lower() for t in tags]
    for t in sorted({t for t in lowered if lowered.count(t) > 1}):
        problems.append(f'duplicate hashtag "{t}": {required} slots is the whole budget')

    if tags:
        lines = [ln for ln in body.strip().splitlines() if ln.strip()]
        last = lines[-1] if lines else ""
        in_last = len(HASHTAG.findall(last))
        if in_last != len(tags):
            problems.append(
                f"{len(tags) - in_last} hashtag(s) sit above the last line. The tags are a block "
                f"at the very end, never inside a sentence")
        elif HASHTAG.sub("", last).strip():
            problems.append("the last line mixes prose with the hashtags. The tags stand alone "
                            "on the final line, after the closing move")
    return problems


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
    # IGNORECASE, because the site ships its deadline chips uppercase. `short_date()` returns
    # "AUG 31" and this pattern only matched "Aug 31", so the one place a bare abbreviated date
    # actually renders was the one place the gate could not see, while its own self-test claims
    # "a bare date inside a data chip still fails". May was the only month it caught, through a
    # different rule, which is what made the gap visible at all.
    for m in set(re.findall(MONTH_ABBR, prose, re.IGNORECASE)):
        problems.append(f'"{m}": spell the month out in a sentence')

    for m in set(CANNOT.findall(prose)):
        problems.append(f'"{m}": never "cannot", always "can\'t"')
    for m in {x.lower() for x in BRITISH_RX.findall(prose)}:
        problems.append(f'"{m}" is British spelling: write "{BRITISH[m]}". This site is '
                        f"published in Texas")
    for m in set(OPENER.findall(prose)):
        problems.append(f'a sentence opens with "{m}": rewrite the opening')
    for m in set(FIRST_PERSON.findall(ROMAN_LABEL.sub(" ", prose))):
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
        if IDENT_INTRO.search(before) and not ARTICLED_NOUN.search(before):
            continue                       # a room, a docket, a section: an identifier
        # The range pattern lets a comma sit inside its digits, so an address reaches here as
        # "78711-3087," with the sentence's own punctuation attached.
        if re.fullmatch(r"\d{5}-\d{4},?", m.group(0)) and ZIP_PLUS_FOUR.search(before):
            continue                       # a postal code, in an address
        msg = f'range "{m.group(0)}": write it "X to Y"'
        if msg not in problems:
            problems.append(msg)
    return problems


# Periods that do not end a sentence. Each entry names WHAT MUST FOLLOW, because in this corpus
# the same token does both jobs and only the continuation tells them apart. Measured on the built
# site rather than taken from a general list, which is why `U.S` and `St` are absent: they do not
# occur here, and a guess would be an untested branch pretending to be coverage.
#
#   NUMBERING  "Reinvestment Zone No. 11" abbreviates, but the ask engine also writes "It is
#              primary. No. It sits outside the window" as an answer, 39 times against 28. Only a
#              DIGIT next proves the abbreviation.
#   MID_NAME   a corporate suffix genuinely ends some sentences ("the certified occupant is
#              Google LLC.") and genuinely sits inside others ("Compal Technology, Inc. and PDC
#              TP 01 LOT A LLC"). A LOWERCASE word next proves the sentence ran on, because no
#              sentence here opens lowercase.
#   TITLE      a personal title is never a sentence's last word, so it needs no continuation test.
_NUMBERING = ("No", "Nos")
_MID_NAME = ("Inc", "LLC", "Co", "Corp", "Ltd", "a.m", "p.m")
_TITLE = ("Dr", "Mr", "Mrs", "Ms", "Sen", "Rep", "Gov")


def _ends_sentence(text: str, i: int) -> bool:
    """Is the terminal mark at `text[i]` a full stop, or an abbreviation's period?

    A blanket rule was tried and rejected on measurement. "A period followed by a lowercase
    letter never ends a sentence" is true of clean prose and false here, because the ask engine
    prints a question string straight after a sentence ("Read the first seven words. should the
    League City Police Department...") and the sources view prints a hostname the same way. A
    blanket rule welds those into one long pseudo-sentence, which is the exact trap the caller's
    own docstring exists to prevent. So the test is scoped to named tokens, and every token in
    the lists was seen doing this in the built site.
    """
    if text[i] != ".":
        return True                                   # ! and ? are never abbreviations
    m = re.search(r"([A-Za-z][A-Za-z.]*)$", text[:i])
    tok = m.group(1) if m else ""
    nxt = text[i + 1:].lstrip()[:1]
    if tok in _TITLE:
        return False
    if tok in _NUMBERING:
        return not nxt.isdigit()
    if tok in _MID_NAME:
        return not nxt.islower()
    return True


def _sentences(text: str) -> list[str]:
    """`text` cut at its real full stops, abbreviations left whole."""
    out, start = [], 0
    for m in re.finditer(r"(?<=[.!?])\s+", text):
        if _ends_sentence(text, m.start() - 1):
            out.append(text[start:m.start()])
            start = m.end()
    out.append(text[start:])
    return out


def long_sentences(text: str, ceiling: int = SENTENCE_CEILING) -> list[str]:
    """Every sentence over the backstop, named with its length and where it starts.

    Split on terminal punctuation and REQUIRED to end in it, so a run of chips or headings that
    carries no full stop cannot be concatenated into one enormous pseudo-sentence. That is not a
    hypothetical: the front page's three deadline cards measured as a single 82 word sentence,
    which named the wrong problem and would have been fixed by rewriting prose that was already
    fine. Structured regions are excluded upstream by `data-prose="data"`; this is the second
    guard, for anything not marked.

    THE SPLIT IS ABBREVIATION AWARE, AND IT HAS TO BE. Splitting on every period let a long
    sentence hide inside its own abbreviation: 44 words on tx-2026-0027 read as two passing
    halves because "Compal Technology, Inc." and "6:00 p.m." each looked like a full stop. The
    gate reported the shorter halves and shipped the sentence. A backstop defeated by writing
    "Inc." is not a backstop, it is a gate with a published bypass.
    """
    out = []
    for raw in _sentences(text):
        s = " ".join(raw.split())
        if not s.endswith((".", "!", "?")):
            continue
        n = len(s.split())
        if n > ceiling:
            out.append(f"sentence of {n} words, over the {ceiling} word backstop. "
                       f"Split it at a clause. Starts \"{s[:60]}...\"")
    return out


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
    # CAPTION SURFACE ONLY, and this is the only path that reaches it. See `hashtag_problems`.
    problems += hashtag_problems(text)
    problems += post_shape_problems(text)
    rate, commas, words = comma_rate(text)
    rp = rate_problem(text)
    if rp:
        problems.append(rp)

    if not quiet:
        ceil = ("no ceiling yet, measured after 20 shipped captions"
                if COMMA_CEILING is None else f"ceiling {COMMA_CEILING}")
        tags = HASHTAG.findall(text)
        print(f"caption_check: {words} words, {commas} commas, {rate} per 100 words ({ceil})")
        print(f"caption_check: {len(tags)} hashtag(s) of {hashtags_required()} required"
              + (f", {' '.join(tags)}" if tags else ""))

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
    ok("a hyphenated word is fine", not catches("A well-sited data center.", "dash"))

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
    ok("a roman numeral label is not a pronoun",
       not catches("The board adopted the 2027 State Water Plan (Phase I).", "first person"))
    ok("...and a real first person beside one still fails",
       catches("We read the plan (Phase I) closely.", "first person"))
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
    # THE INSTRUMENTS A CITY ACTUALLY ADOPTS, and the address it takes comments at. Both came
    # out of running this lint against the real record, which is where these turn up.
    for ident in ("The council adopted Ordinance 2026-078 that evening.",
                  "It signed Resolution No. 010-26 asking the Legislature to act.",
                  "The city adopted the code under ORD-2026-08 the same day.",
                  "Mail it to the Chief Clerk, Austin, Texas 78711-3087, before it shuts."):
        ok(f"an instrument or an address is not a range: {ident.split()[2]}",
           not catches(ident, "range"), str([p for p in check(ident) if "range" in p]))
    # A VOTE IS NOT AN IDENTIFIER, and this is the pair that keeps the exemption honest. The
    # words in front are the only difference between a name and a count, and "voted 5-0" reads
    # correctly as "voted 5 to 0" while "Ordinance 2026 to 078" does not exist.
    for vote in ("The court voted 5-0 to deny the reinvestment zone.",
                 "Commissioners passed the amendment 4-1 that night.",
                 "The commission rejected the permit 4-0 in open session."):
        ok(f"a vote count is still a range: {vote.split()[2]}", catches(vote, "write it"))
    ok("a real range still fails even near an identifier word",
       catches("The order in Room 7 runs 40-60 pages.", "write it"))
    # BRITISH SPELLING. The first pair is the one that shipped, on the one subject this record
    # is most about, and it took the owner reading the live site to find it.
    ok("data centres fails", catches("Three data centres were approved.", "British spelling"))
    ok("...and names the American form",
       catches("Three data centres were approved.", 'write "centers"'))
    ok("...and it is caught capitalised", catches("Centre Street rules apply.", "British"))
    for fine in ("Three data centers were approved.", "The enterprise franchise will advertise.",
                 "The program comprises a license and a practice.",
                 "It will analyze the fiber optic route."):
        ok(f"American spelling passes: {fine.split()[1]}", not catches(fine, "British"), fine)
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
    flagged = "A data center needs electricity and, in most cooling designs, water."
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

    # AN AGENDA ITEM NUMBER IS NOT A PRONOUN. Brazoria County's minute reads "No action taken
    # due to I.3 failed", and this gate reported first person on a caption quoting it. The only
    # ways past were to misquote the record or drop its best fact, which is how a gate stops
    # being run at all. Both directions are asserted, because the exemption must not become a
    # hole a real pronoun fits through.
    ok("an agenda item number is not first person",
       not catches('The minute reads "No action taken due to I.3 failed".', "first person"))
    ok("...and a Roman numbered item is not either",
       not catches('Item I.IV was postponed by the court.', "first person"))
    ok("...while a real first person still FAILS",
       catches("I read the minute myself.", "first person"))
    ok("...and so does one at the end of a sentence",
       catches("The clerk read it and so did I.", "first person"))
    ok("...and so does a plural one", catches("We read the minute.", "first person"))

    # THE BACKSTOP'S OWN BYPASS. Splitting on every period let a long sentence hide inside its
    # own abbreviation, and both fixtures below are real shipped copy, not invented ones. The
    # first ran 44 words on tx-2026-0027 and reported as two passing halves for as long as the
    # gate existed, because "Compal Technology, Inc." and "6:00 p.m." each read as a full stop.
    hidden = ("The City of Taylor published a public notice that its City Council would consider "
              "an Amended and Restated Tax Abatement Agreement with Compal Technology, Inc. and "
              "PDC TP 01 LOT A LLC at the regularly scheduled meeting on August 13th, 2026 at "
              "6:00 p.m.")
    ok("a long sentence cannot hide behind Inc. and p.m.",
       any("44 words" in x for x in long_sentences(hidden)), str(long_sentences(hidden)))
    numbered = ("Brazoria County Commissioners Court opened and closed a public hearing on the "
                "creation of Brazoria County Reinvestment Zone No. 26-01 on March 10th, 2026 and "
                "then refused to create the zone.")
    ok("...nor behind a zone number",
       any("31 words" in x for x in long_sentences(numbered)), str(long_sentences(numbered)))
    # THE OTHER HALF, AND THE REASON THE RULE IS TOKEN SCOPED RATHER THAN BLANKET. Each of these
    # tokens genuinely ends sentences too. Welding them shut would manufacture the pseudo-sentence
    # this gate's own docstring exists to prevent, so both directions are asserted.
    answer = ("One source backs it. It is primary. No. It sits outside the window the record "
              "measures and nothing in the file moves it back inside that window today.")
    ok('...but "No." answering a question still ends its sentence',
       not long_sentences(answer), str(long_sentences(answer)))
    suffix = ("The certified occupant is Google LLC. Alphabet has moved to acquire the parent "
              "and the record does not yet carry a filing that names the new owner of the site.")
    ok("...and a corporate suffix ending a sentence still ends it",
       not long_sentences(suffix), str(long_sentences(suffix)))
    # A QUESTION STRING PRINTED AFTER PROSE IS NOT A CONTINUATION. The ask engine writes exactly
    # this, which is why "a period before a lowercase letter never ends a sentence" was measured
    # and rejected: as a blanket rule it welds these two into one 34 word sentence.
    lowered = ("Read the first seven words. should the League City Police Department renew the "
               "camera contract it signed with the vendor in the spring of the following year")
    ok("...and a lowercase question string after prose is not welded on",
       not long_sentences(lowered), str(long_sentences(lowered)))

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
    # THE HASHTAG RULE, and the regression it was written for.
    #
    # Run No. 1 shipped three tags, run No. 2 shipped none, and every gate was green both times,
    # because brand.yaml said one thing, CAPTION_CRAFT.md said the opposite, and nothing checked.
    # These cases prove this gate goes red on the run that actually happened.
    need = hashtags_required()
    ok("the required count is read from brand.yaml, not typed here", need == 3, str(need))
    tagged = "The commission met.\n\n#Texas #ERCOT #DataCenters"
    ok("a correctly tagged post passes", not hashtag_problems(tagged), str(hashtag_problems(tagged)))

    # THE ACTUAL 2026-08-18 REGRESSION.
    ok("a post with NO hashtags fails",
       any("takes exactly" in p for p in hashtag_problems("The commission met.")),
       str(hashtag_problems("The commission met.")))
    ok("...and the real shipped caption that lost them fails this gate",
       any("takes exactly" in p for p in
           hashtag_problems("Everyone guesses more screens.\n\nBoard policy reached "
                            "second reading.")))
    ok("too few hashtags fails",
       any("takes exactly" in p for p in hashtag_problems("It met.\n\n#Texas #ERCOT")))
    ok("too many hashtags fails",
       any("takes exactly" in p for p in
           hashtag_problems("It met.\n\n#Texas #ERCOT #Data #Grid")))
    ok("a hashtag mid-sentence fails on placement",
       any("above the last line" in p for p in
           hashtag_problems("The #ERCOT queue grew.\n\n#Texas #Grid")))
    ok("prose sharing the last line with the tags fails",
       any("mixes prose" in p for p in
           hashtag_problems("It met.\n\nRead more #Texas #ERCOT #Grid")))
    ok("a duplicate tag fails",
       any("duplicate hashtag" in p for p in
           hashtag_problems("It met.\n\n#Texas #texas #Grid")))
    ok("a url fragment is not counted as a hashtag",
       not hashtag_problems("See https://example.com/a#section here.\n\n#Texas #ERCOT #Grid"),
       str(hashtag_problems("See https://example.com/a#section here.\n\n#Texas #ERCOT #Grid")))

    # THE SEPARATION THAT KEEPS THE WEBSITE OUT OF THIS.
    ok("check() does NOT demand hashtags, because it also judges the site",
       not any("hashtag" in p for p in check("The commission met on August 11th.")))
    ok("...and run() DOES, because that is the caption path",
       "hashtag_problems(text)" in open(__file__, encoding="utf-8").read())

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

    # THE THREE brand.yaml RULES (2026-08-25), each direction.
    _lo, _hi = linkedin_rule("caption_chars", list)
    _tags = " ".join(f"#Tag{i}" for i in range(1, hashtags_required() + 1))
    _ok = ("Something happened in Bexar County and the record says so plainly. "
           * 4)[: _hi - len(_tags) - 40] + " Is that worth it?\n\n" + _tags
    ok("a caption inside the band, ending on a question, with no link, is clean",
       not post_shape_problems(_ok), str(post_shape_problems(_ok))[:160])
    _long = ("Something happened in Bexar County and the record says so plainly. " * 20
             + "Is that worth it?\n\n" + _tags)
    ok("...a caption over the band FAILS",
       any("caption_chars band" in x for x in post_shape_problems(_long)), str(post_shape_problems(_long))[:120])
    _link = _ok.replace("Is that worth it?", "The record is at texasaidocket.com. Is that worth it?")
    ok("...a link in the body FAILS",
       any("links_in_body" in x for x in post_shape_problems(_link)), str(post_shape_problems(_link))[:120])
    _noq = _ok.replace("Is that worth it?", "That is what the record says.")
    ok("...and a caption that does not end on a question FAILS",
       any("ends_with" in x for x in post_shape_problems(_noq)), str(post_shape_problems(_noq))[:120])

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
