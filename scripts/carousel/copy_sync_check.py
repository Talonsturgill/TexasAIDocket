#!/usr/bin/env python3
"""copy_sync_check.py — does the record still say what the deck says?

WHY THIS EXISTS

Two failures, one file.

**The record goes stale.** During pixel review the showrunner edits display text straight into a
slide's HTML, because that is the fastest way to answer a critic. A kicker, a headline, a label.
`copy.json` is not touched, and from that moment the record of what the deck says disagrees with
the deck. In the sibling product slide 05's kicker was hand-edited from HOW IT STARTED to BEFORE
THE CLASS in the HTML while `copy.json` kept the old string, and the only thing that noticed was
the scorer's transcription pass at the ship gate, with no budget left to do anything about it.
There was no machine check. This is it.

**A slide cites a claim that does not exist.** Every factual string here carries a claim id, and
the site's whole promise is that the id resolves. Nothing checked that it does. `claims_check`
proves the claims file is well formed. `aggregate_check` proves the arithmetic on top of it. Both
look at the claims. Neither looks at whether the id a SLIDE cites is one of them, so a slide
citing `tx-2026-08-12-07` when the file stops at 05 satisfies every other gate in the run. That is
the same defect as the sibling's empty verification record, wearing different clothes: the promise
holds everywhere except where a reader would check it.

WHAT IT DOES

For every string in `copy.json`, verify it is present in what the browser actually laid out, which
is `render_report.json`'s per-slide `text_nodes[].text`. Then verify every claim id those slides
cite exists in `claims.json`.

**A third failure, found on 2026-08-16, and it is the one that made the other two ornamental.**
The key names this gate looked at were an ALLOWLIST, so a slide using a key the list did not
name was skipped in silence. Slides are bespoke and the copywriter names keys to suit the slide.
That deck used `hook`, `hook2`, `tag`, `tag2`, `dek`, `bodies`, `how`, `rows`, `attribution`,
`site`, `source2` and `when1`, and twelve of its nineteen key names were invisible here. The gate
reported clean having never read a word of the deck's prose. It is a denylist now.

DIRECTION, BOTH WAYS SINCE 2026-08-16. This file used to argue the reverse direction would flag
every slide number and axis label, and that a gate which cries wolf is worse than no gate. The
first half was true of a naive reverse check and the conclusion was wrong. Rendered-but-not-
authored is how a sentence reaches a published slide having entered no manifest, and everything
downstream that reads the manifest is then blind to it. It happened on five slides of that deck,
and the sentence carrying an untraced "SB 6" was one of them.

The reverse direction is kept quiet by three carve-outs rather than by not existing: nodes the
design marked `decorative`, standing furniture like the masthead and the slide counter, and a
prose-shape test so labels are never demanded. The provenance stamp is stripped from a node
rather than exempting the node, because it arrives concatenated with real text.

A FOURTH FAILURE, 2026-08-26. A QUOTATION THAT TRACES TO NOTHING.

Slide 7 of that run set `clinical care, research, advanced computing` under the attribution
`BOARD ITEM, AUGUST 12TH, 2026`, and no claim in the run's claims file carries that string. The
frame declared `c12` and `c23` and printed neither of them, so the minimal pair its whole
composition measured did not exist, and a granite plate set beneath a gap in a sentence the
board never wrote read as an assertion that the board had struck two words out.

**Every mechanical gate was green.** `claims_check` proves claims exist and carry sources and has
no opinion about what a frame prints. `aggregate_check` re-derived a declaration whose stated
derivation was false against both quotes. `noun_trace` checks NAMED THINGS and not quoted ones.
And this file's own two directions agreed with each other, because both were reading the same
authored string: `copy.json` said it, the render laid it out, the pair was in sync, and the
sentence was still not the document's. Three green gates, one source. Two of three judges caught
it by hand and one did not, and a single scorer would have shipped it.

**So this asks the question none of them ask: does the source actually say it.** A phrase the
deck presents as a document's own words must occur verbatim in a quote on one of the claims THAT
SLIDE declares. Both halves of that sentence are load bearing. Verbatim catches the invented
line. Per slide catches the provenance error, which happened three more times on the same deck:
slide 6 printed folios quoted by `c29` and `c30` while declaring `c27` and `c28`.

WHAT COUNTS AS PRESENTED AS THE SOURCE'S OWN WORDS, and what this gate therefore cannot see.

    a quoted phrase   text between quotation marks, straight or curly, carrying a space. This is
                      structural and needs no list of key names, which is the mistake the
                      allowlist above already cost this file once.
    a quote-named key any key whose name carries "quote" or "verbatim". A widening, not the
                      selector: a copywriter who names a key `quote` has said what it is.

    NOT COVERED, and stated rather than implied. An unquoted string sitting under a dated
    attribution is invisible here, because nothing in the artifact distinguishes it from a label.
    The 2026-08-26 frame is only visible because its lines were set as quotations. A design that
    prints a document's words with no marks around them is a design this gate is blind to, and
    closing that needs the DOSSIER to declare which regions are quotation, not a cleverer regex.

MEASURED, on every deck this repo has rendered: 33 quoted phrases across seven decks, all of them
tracing to a claim the slide declares. Zero false positives on real work, which is the number
that decides whether a gate survives its first month.

A FIFTH FAILURE, 2026-09-15. A CHARACTER THE HOUSE BANS ANYWHERE, ON A FRAME.

Frame 5 of carousel no. 25 shipped `SEPTEMBER 14-15, 2026` with an EN DASH in it, through the
render and through the machine qa pass, and a pixel critic reading the picture is what found it.
`CLAUDE.md` bans em dashes, en dashes, curly quotes and emoji anywhere, `caption_check` enforces
all four classes, and it is pointed at `caption.txt` and at the built site. Nothing was pointed
at the deck, so the nine frames a reader actually looks at were the one published surface with
no house-rule gate on them.

This file is the one that should have caught it, and could not, because its only comparison
operator is `skeleton()` and `skeleton()` deletes punctuation. See `banned_characters` below.

    copy_sync_check.py --date 2026-08-12
    copy_sync_check.py --self-test

Exit 0 in sync, 1 drifted, 2 the checker could not run.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# render.py records each node as `el.textContent.trim().replace(/\s+/g," ").slice(0, 80)`. That
# 80 is not ours to choose and it is the hard limit on what this gate can see: a long body string
# is truncated in the report, so its tail was never written down and no check here can ask about
# it.
#
# THE NEEDLE IS THEREFORE THE AUTHORED STRING PUT THROUGH THE SAME TRUNCATION, and matched whole.
# The first version of this file compared a 40 character prefix instead, which felt safer and was
# strictly worse: it threw away half the evidence the artifact does carry. Two bodies agreeing for
# 64 characters and diverging after passed it, which is exactly the shape a late edit takes.
#
# The remaining blind spot is real and is stated rather than papered over. A divergence beyond
# character 80 of a single string is invisible here. **The cure for that is widening the render's
# window, never loosening this comparison**, and there is a self-test below pinning the limit so
# nobody later mistakes it for a bug in the matcher and "fixes" it by shortening the needle.
# THE WINDOW IS THE REPORT'S, NOT THIS FILE'S. render.py stores each text node truncated, and
# that figure moved from 80 to 320 on 2026-08-19. Comparing today's constant against a report
# written at 80 mis-truncates every authored string longer than 80 characters and fails decks that
# were correct when they shipped. It did exactly that to the 2026-08-16 deck within one CI run of
# the widening, and this self-test caught it.
#
# So the report DECLARES its window and this reads it. `RENDER_WINDOW` is the fallback for reports
# written before the field existed, and it is 80 because that is what those reports actually hold.
RENDER_WINDOW = 80

# A DENYLIST, AND IT USED TO BE AN ALLOWLIST. THAT WAS THE HOLE.
#
# This was a tuple of key names the gate would look at: kicker, headline, subhead, body, label,
# labels, chip, chips, caption, stat, stats, note, footer, quote, source, title. Every other key
# was skipped in silence. Slides are bespoke, so the copywriter names keys to suit the slide, and
# on 2026-08-16 the deck used `hook`, `hook2`, `tag`, `tag2`, `dek`, `bodies`, `how`, `rows`,
# `attribution`, `site`, `source2` and `when1`. Twelve of the nineteen key names in that deck
# were invisible here, including every one carrying body prose.
#
# The gate reported clean and had checked 35 strings out of a deck whose prose it had never
# seen. That is how a sentence carrying an untraced "SB 6" reached a published slide with every
# gate green, and it is the shape GATE_LESSONS warns about: a check wired to nothing, passing.
#
# So the question is inverted. Everything is reader copy unless it is named here as machinery.
# A new key invented for tomorrow's slide is checked by default, and the failure mode of getting
# this list wrong is a gate that cries wolf rather than a gate that sleeps.
META_KEYS = frozenset({
    "claims", "claim_id", "claim_ids", "cid",          # citations, checked separately below
    "n", "slide", "index", "id",                       # position and identity
    "technique", "file", "path", "art", "palette",     # how it was drawn, never what it says
    "notes", "note_to_self", "todo",                   # planning residue, never rendered
})


def skeleton(s: str) -> str:
    """Lowercase alphanumerics only.

    Punctuation, case and whitespace differ freely between an authored string and what the
    browser lays out: a non-breaking space, a soft hyphen, a wrapped line. None of those is the
    defect this gate is looking for, which is a string REPLACED by a different one. Comparing
    skeletons ignores the noise and still catches the replacement.
    """
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def strings_in(node) -> list[str]:
    """Every reader-visible string in a slide record, however it is nested."""
    out = []
    if isinstance(node, str):
        if node.strip():
            out.append(node)
    elif isinstance(node, list):
        for item in node:
            out.extend(strings_in(item))
    elif isinstance(node, dict):
        for k, v in node.items():
            if k not in META_KEYS:
                out.extend(strings_in(v))
    return out


def claim_ids_in(node) -> set[str]:
    """Every claim id a slide cites, at any nesting depth."""
    out = set()
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("claim_ids", "claim_id", "claims"):
                if isinstance(v, str):
                    out.add(v)
                elif isinstance(v, list):
                    out.update(str(x) for x in v if isinstance(x, (str, int)))
            else:
                out |= claim_ids_in(v)
    elif isinstance(node, list):
        for item in node:
            out |= claim_ids_in(item)
    return out


def normalize_slides(raw) -> dict[str, dict]:
    """Accept either shape the run produces, without changing what is compared.

    `copy.json["slides"]` is a dict keyed S1..S9 in the record form and a list of per-slide
    objects in the copywriter's form. Both are real artifacts of a real run. A gate that crashes
    on one of them is a gate that gets commented out.
    """
    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items() if isinstance(v, (dict, list, str))}
    if isinstance(raw, list):
        out = {}
        for i, item in enumerate(raw, start=1):
            n = item.get("n") if isinstance(item, dict) else None
            try:
                n = int(n)
            except (TypeError, ValueError):
                n = i
            out[f"S{n}"] = item
        return out
    return {}


def slide_no(key: str) -> int | None:
    m = re.search(r"(\d+)", str(key))
    return int(m.group(1)) if m else None


def rendered_text(report: dict) -> dict[int, str]:
    """One skeleton per slide, being everything the browser laid out on it, concatenated.

    Concatenating is deliberate. A headline split across two spans is recorded as three nodes,
    the parent and each span, and an authored string that spans them matches none of the three
    individually. The question this gate asks is whether the words reached the slide, not which
    element holds them.
    """
    out: dict[int, str] = {}
    for rec in report.get("slides") or []:
        n = rec.get("n") or rec.get("slide") or slide_no(rec.get("file", ""))
        if n is None:
            continue
        joined = " ".join(str(t.get("text", "")) for t in (rec.get("text_nodes") or []))
        out[int(n)] = skeleton(joined)
    return out


# THE REVERSE DIRECTION, AND WHAT KEEPS IT FROM CRYING WOLF.
#
# Authored-but-not-rendered was the only direction this gate checked, and the docstring argued
# the reverse would flag every slide number and axis label. That was true of a naive reverse
# check and it was the wrong conclusion: rendered-but-not-authored is how a sentence reaches a
# published slide having entered no manifest, which is invisible to every gate downstream that
# reads the manifest. It happened on 2026-08-16, on five slides.
#
# Three carve-outs make it quiet enough to keep.
#
# 1. `decorative`. render.py already marks nodes the design declares as furniture, and the
#    coordinates footer this deck prints is marked. The marker exists; nothing was reading it.
# 2. Standing furniture. The masthead and the slide counter appear on every slide, are never
#    authored per slide, and are matched as whole strings rather than by pattern-guessing.
# 3. PROSE SHAPE. A label is a few words with no sentence in it. Body prose either runs long or
#    ends a sentence. Only prose-shaped nodes are demanded, because a manifest of every axis
#    label is not what the manifest is for.
#
# The blind spot is stated rather than papered over: a SHORT unauthored string that is not
# furniture slips through. That is the deliberate price of a gate people do not learn to ignore.
STANDING_FURNITURE = frozenset({
    "texasaidocket",           # the masthead
    "texasaidocketcom",        # the closing card's address
})

SLIDE_COUNTER = re.compile(r"^\s*\d+\s*/\s*\d+\s*$")

# The provenance stamp the design doctrine prints beside a sourced figure, in the forms this
# engine emits: "CLAIM c7.", "CLAIM c7. QUOTED VERBATIM.", "CLAIM c7. COMPUTED.".
#
# It is not authored copy and demanding it appear in copy.json would be demanding the manifest
# carry its own citations, which this file already argues against in the other direction. The id
# inside it is not unchecked: the citation half below resolves every id a slide cites against
# claims.json.
#
# STRIPPED FROM THE NODE, NOT AN EXEMPTION FOR THE NODE. A stamp usually arrives concatenated
# into a parent element alongside real text, so exempting any node containing one would blind
# this gate to whatever sits beside it. Removing just the stamp leaves the rest to be judged.
# A STAMP TAKES A CLAIM ID, NOT ANY WORD. 2026-08-26.
#
# The first draft matched `CLAIMS?` followed by `[A-Za-z0-9_.-]+`, case insensitively, so the
# ordinary English word "claim" plus whatever came next was cut out of the middle of a sentence.
# Slide 2's dek reads "Each one with the claim whose own words prove its shape." and reached this
# gate as "Each one with the  own words prove its shape.", which matches no authored string,
# because no authored string says that. The gate then failed a correct frame and named a sentence
# nobody wrote, which is the worst kind of gate output: it sends the next reader looking for a
# defect in the deck instead of in the checker.
#
# A stamp's argument is a claim id. Requiring one keeps every real stamp stripped and puts the
# word "claim" back in the language.
CLAIM_STAMP = re.compile(
    r"\bCLAIMS?\s+[cC]\d+(?:\s*(?:,|and)\s*[cC]\d+)*\s*\.?"
    r"(\s*(QUOTED\s+VERBATIM|COMPUTED|MEASURED|MODELED)\s*\.?)?",
    re.IGNORECASE)


def is_prose(text: str) -> bool:
    """Whether a rendered string is body prose rather than a label.

    Long, or ends a sentence with enough words to be one. render.py truncates at
    RENDER_WINDOW, so a long body arrives without its terminal full stop and the length arm is
    what catches it.
    """
    t = " ".join(str(text).split())
    if len(t) >= 60:
        return True
    return len(t.split()) >= 5 and t.rstrip().endswith((".", "?", "!"))


def unauthored(report: dict, authored: dict[int, str]) -> list[str]:
    """Prose the browser laid out that no authored string accounts for."""
    out = []
    for rec in report.get("slides") or []:
        n = rec.get("n") or rec.get("slide") or slide_no(rec.get("file", ""))
        if n is None:
            continue
        hay = authored.get(int(n), "")
        for node in rec.get("text_nodes") or []:
            text = str(node.get("text", "")).strip()
            if not text or node.get("decorative"):
                continue
            if SLIDE_COUNTER.match(text):
                continue
            text = CLAIM_STAMP.sub(" ", text).strip()
            if not text:
                continue
            sk = skeleton(text)
            if not sk or sk in STANDING_FURNITURE or sk in hay:
                continue
            if not is_prose(text):
                continue
            shown = text if len(text) <= 56 else text[:53] + "..."
            out.append(f"S{n}: \"{shown}\" was laid out but is in no authored string")
    return out


# ---------------------------------------------------------------- quotations
#
# A quoted span, in the two mark shapes this project's copy actually contains. The house rule is
# straight quotes only, so a curly pair reaching here is already a `caption_check` violation, and
# a gate that cannot see it would be a gate defeated by a typographic slip.
#
# THE SPAN MUST CARRY A SPACE, and that is the carve-out rather than a character count. A single
# quoted word is a scare quote or a term of art, which every deck here uses and none of which is
# a document speaking. A quoted PHRASE is the source's own words or it is nothing. Written as a
# structural test on purpose: a minimum length would be a number typed by a person, and this
# project's law says numbers are computed or they are not published.
QUOTED_SPAN = re.compile(r"[\"“]([^\"“”]+)[\"”]")

# A key name that says what the value is. This is a WIDENING of the structural selector above and
# never the selector itself: `line_board` is what carried the 2026-08-26 defect, and no list of
# key names would have held it. See the allowlist note on META_KEYS for what that mistake costs.
QUOTE_KEY = re.compile(r"quote|verbatim", re.IGNORECASE)


def quoted_phrases(key: str, value: str) -> list[str]:
    """Every phrase in one authored string that is presented as a source's own words."""
    spans = [m.group(1).strip() for m in QUOTED_SPAN.finditer(value)]
    spans = [s for s in spans if " " in s]
    if spans:
        return spans
    v = value.strip()
    return [v] if QUOTE_KEY.search(str(key)) and " " in v else []


def claim_quotes(claims: dict | None) -> dict[str, str]:
    """Each claim's id mapped to the skeleton of its quote.

    Only the QUOTE, never the claim's `text`. The claim text is this project's own sentence about
    the source and is exactly what went wrong upstream on 2026-08-26, where a recommendation was
    written up as a completed action. A frame quoting the record's paraphrase of a document and
    attributing it to the document would be the same fault one surface along.
    """
    cs = claims.get("claims") or claims.get("verified_claims") or [] if claims else []
    out = {}
    for c in cs:
        if not isinstance(c, dict):
            continue
        cid = next((str(c[k]) for k in ("id", "claim_id", "cid") if c.get(k)), None)
        if cid:
            out[cid] = skeleton(c.get("quote") or c.get("verbatim_quote") or "")
    return out


def untraced_quotations(copy: dict, claims: dict | None) -> tuple[list[str], int]:
    """Quoted phrases on a frame that no claim the slide declares actually contains.

    Returns (findings, how many phrases were examined). The count is returned and printed on
    success as well as on failure, because a run that checked nothing must not read like a run
    that found nothing.
    """
    if claims is None:
        return [], 0
    quotes = claim_quotes(claims)
    everything = " | ".join(quotes.values())
    slides = normalize_slides(copy.get("slides"))
    findings, checked = [], 0
    for key in sorted(slides, key=lambda k: (slide_no(k) or 0)):
        s = slides[key]
        if not isinstance(s, dict):
            continue
        declared = sorted(claim_ids_in(s))
        mine = " | ".join(quotes.get(c, "") for c in declared)
        for k, v in s.items():
            if k in META_KEYS:
                continue
            for val in ([v] if isinstance(v, str) else (v if isinstance(v, list) else [])):
                if not isinstance(val, str):
                    continue
                for phrase in quoted_phrases(k, val):
                    needle = skeleton(phrase)
                    if not needle:
                        continue
                    checked += 1
                    if needle in mine:
                        continue
                    shown = phrase if len(phrase) <= 64 else phrase[:61] + "..."
                    if needle in everything:
                        owner = [c for c, q in quotes.items() if q and needle in q]
                        findings.append(
                            f"{key}.{k}: \"{shown}\" is quoted from {', '.join(sorted(owner))}, "
                            f"which this slide does not declare. It declares "
                            f"{', '.join(declared) or 'nothing'}. Cite the claim the words came "
                            f"from")
                    else:
                        findings.append(
                            f"{key}.{k}: \"{shown}\" is set as a quotation and occurs in NO "
                            f"claim's quote. The slide declares {', '.join(declared) or 'nothing'}. "
                            f"Either the words are the source's, in which case they are a claim, "
                            f"or they are the deck's, in which case the marks around them say "
                            f"something untrue about who wrote them")
    return findings, checked


# ---------------------------------------------------------------- banned characters
#
# THE HOUSE BANS THREE CHARACTER CLASSES OUTRIGHT AND NO GATE READ THE DECK FOR THEM (2026-09-15).
#
# `CLAUDE.md`: "No em dashes or en dashes anywhere. No emojis. Straight quotes only." Anywhere
# includes a slide. `caption_check` enforces all three and is pointed at `caption.txt` and at the
# built site, never at the deck. `house_style_check` reads `docs/`. So the nine frames a reader
# actually looks at were the one published surface with no house-rule gate on them at all, and
# frame 5 of carousel no. 25 shipped `SEPTEMBER 14-15, 2026` with an EN DASH in the middle of it,
# through render and through the machine qa pass, until a pixel critic read the picture.
#
# WHY THIS FILE IS THE ONE THAT SHOULD HAVE CAUGHT IT. This gate already reads every authored
# string in `copy.json` and every node the browser laid out, in both directions, which is more of
# the deck's copy than anything else in the run sees. It could not see the dash because its only
# comparison operator is `skeleton()`, which keeps lowercase alphanumerics and DELETES every
# punctuation mark. The dash was present in the record and present in the render, so the sync
# direction was correctly, uselessly green. A gate whose normaliser erases the defect class is
# blind to it by construction, and the repair belongs beside the normaliser that erases it.
#
# WHY ONLY CHARACTERS, when `caption_check.check()` is imported here anyway and enforces fifteen
# rules. Every other rule in that file is a judgement about PROSE: a colon, a comma rate, a bare
# date, a sentence opener. Slide copy is mostly furniture, and furniture is where those rules
# produce noise a run learns to scroll past, which GATE_LESSONS names as worse than no gate. A
# dash is a dash on a label and in a sentence alike. These three classes are structural, they
# admit no exception anywhere in the house, and they are exactly the class GATE_LESSONS 46 calls
# safe: "a semicolon is a semicolon".
#
# ONE LIST, NOT A SECOND COPY OF ONE. `DASHES`, `CURLY` and `emojis()` are imported from
# `caption_check` rather than restated, because a list that exists in two files is two lists and
# the second one is always shorter. That is GATE_LESSONS 75, and this repo has already paid for
# it with two numeral tokenisers.
#
# BOTH SURFACES, DELIBERATELY. The render is what a reader receives and is the authority. The
# record is what every downstream gate, the ledger and the article page read. A pixel round edits
# HTML directly, so a character can enter either one alone, and checking only the render would
# leave a banned character in the committed record of what the deck says.
def banned_characters(copy: dict, report: dict) -> list[str]:
    """Em and en dashes, curly quotes and emoji, in the deck's copy and in its render.

    Returns one finding per (surface, character, string). Empty means the deck carries none.
    """
    try:
        import caption_check as house
    except ImportError as exc:                                          # pragma: no cover
        raise SystemExit(
            f"copy_sync: cannot import caption_check, which owns the banned character list "
            f"({exc}). This gate will not restate the list locally: a second copy is how the "
            f"two numeral tokenisers in this repo came to carry the same bug. Fix the import")

    def hits(s: str) -> list[tuple[str, str]]:
        out = [("dash", d) for d in sorted(set(house.DASHES.findall(s)))]
        out += [("curly quote", q) for q in sorted(set(house.CURLY.findall(s)))]
        out += [("emoji", e) for e in sorted(set(house.emojis(s)))]
        return out

    advice = {
        "dash": 'no em or en dashes anywhere. Write the range "X to Y", or split the sentence',
        "curly quote": "straight quotes only",
        "emoji": "not the register, not once",
    }
    findings: list[str] = []

    def note(where: str, kind: str, ch: str, s: str):
        shown = s if len(s) <= 56 else s[:53] + "..."
        msg = f"{where}: {kind} {ch!r} in \"{shown}\": {advice[kind]}"
        if msg not in findings:
            findings.append(msg)

    for key, slide in sorted(normalize_slides(copy.get("slides")).items(),
                             key=lambda kv: (slide_no(kv[0]) or 0)):
        for s in strings_in(slide):
            for kind, ch in hits(str(s)):
                note(f"copy.json {key}", kind, ch, str(s))
    # Anything else the manifest carries. `strings_in` honours META_KEYS, so how a frame was drawn
    # is still exempt and everything a reader could receive is examined by default.
    for s in strings_in({k: v for k, v in copy.items() if k != "slides"}):
        for kind, ch in hits(str(s)):
            note("copy.json", kind, ch, str(s))

    for rec in report.get("slides") or []:
        n = rec.get("n") or rec.get("slide") or slide_no(rec.get("file", ""))
        for t in rec.get("text_nodes") or []:
            s = str(t.get("text", ""))
            for kind, ch in hits(s):
                note(f"render slide {n}", kind, ch, s)
    return findings


# ---------------------------------------------------------------- a date in the post's own year
#
# THE RULE HAD A GATE AND THE GATE COULD NOT SEE THE DECK (2026-09-23, carousel no. 32).
#
# `CLAUDE.md`: "A DATE IN THE POST'S OWN YEAR CARRIES NO YEAR", owner's instruction 2026-09-11,
# with the SITE named as the one exception because a record page is a permanent archive. A
# carousel is not the site. It is the post.
#
# `caption_check.post_shape_problems` enforces it and is reached only from `caption_check.run()`,
# which this run pointed at `caption.txt` and at nothing else. So frame 7 set "AUGUST 3RD, 2026"
# three times and a dek reading "The audit was ordered August 3rd, 2026", through two pixel
# review rounds and nine green gates, while the CAPTION of the same post printed the same three
# dates correctly without the year. **Two surfaces of one post gave two answers to a rule the run
# demonstrably knew**, and the only thing that found it was a scorer reading the picture.
#
# That is this repo's named recurring shape, said in `CLAUDE.md` about the missing hashtags, the
# missing progress counter and the wrong public URL: a rule stated in one place, a surface
# keeping its own copy, and nothing in between checking they agree. It is also the identical
# omission `banned_characters` above exists for, eight days later, one function down.
#
# WHY THIS RULE AND NOT THE REST OF `post_shape_problems`. The argument is the one written above
# for the character classes and it is the same argument. Length, the link rule and the required
# interrogative ending are judgements about a CAPTION as a whole and are meaningless applied to a
# label. A year printed beside a date is structural: it is redundant on a hook, on a dek, on an
# axis label and in a sentence alike, it admits no exception anywhere on this surface, and there
# is nothing to tune. GATE_LESSONS 46's test for a safe rule is "a semicolon is a semicolon".
#
# ONE PATTERN, NOT A SECOND COPY OF ONE. `DATED_YEAR` is imported from `caption_check` for the
# reason the line above imports `DASHES`: a pattern that exists in two files is two patterns and
# the second one is always the one that misses. GATE_LESSONS 75, and the two numeral tokenisers.
#
# THE YEAR COMES FROM THE RUN, NEVER FROM THE CLOCK. `sources_block.py` takes it from the run
# directory's own name so that rebuilding an old run renders what that run published, and the
# same reasoning applies with more force here: read this with `date.today()` and every archived
# deck starts failing on January 1st for copy that was correct when it shipped.
def redundant_year(copy: dict, report: dict, year: str) -> list[str]:
    """Dates printing the post's own year, in the deck's copy and in its render.

    `year` is the four-digit year of the RUN. A date in any other year keeps its year, which is
    what makes this a rule about redundancy rather than a rule against years.
    """
    try:
        import caption_check as house
    except ImportError as exc:                                          # pragma: no cover
        raise SystemExit(
            f"copy_sync: cannot import caption_check, which owns DATED_YEAR ({exc}). This gate "
            f"will not restate the pattern locally: a second copy is how the two numeral "
            f"tokenisers in this repo came to carry the same bug. Fix the import")
    if not (isinstance(year, str) and re.fullmatch(r"\d{4}", year)):
        raise SystemExit(
            f"copy_sync: redundant_year was given {year!r} as the post's year. It reads the run "
            f"date and never the clock, so an unreadable run date is a gate that cannot run "
            f"rather than a gate that passes")

    findings: list[str] = []

    def note(where: str, s: str):
        for m in house.DATED_YEAR.finditer(s):
            if m.group(1) != year:
                continue
            shown = m.group(0)
            # THE REPAIR IS THE STRING WITHOUT ITS YEAR, cut at the year's own span rather than
            # at a comma. The corpus writes both "AUGUST 25TH, 2026" and "AUGUST 25TH 2026", and
            # splitting on the comma hands the second one back unchanged, so the advice reads
            # "Write 'AUGUST 25TH 2026'" about the string that is already wrong. A gate that
            # misreports the repair is the same fault as one that misreports the figure.
            bare = shown[:m.start(1) - m.start(0)].rstrip().rstrip(",").rstrip()
            msg = (f"{where}: {shown!r} prints the year and this post ships in {year}. Write "
                   f"{bare!r}. A reader works the year out from the fact that they are reading "
                   f"it this week, and the first surface of a post is the only real estate it "
                   f"has. The year STAYS on any date outside {year}")
            if msg not in findings:
                findings.append(msg)

    for key, slide in sorted(normalize_slides(copy.get("slides")).items(),
                             key=lambda kv: (slide_no(kv[0]) or 0)):
        for s in strings_in(slide):
            note(f"copy.json {key}", str(s))
    for s in strings_in({k: v for k, v in copy.items() if k != "slides"}):
        note("copy.json", str(s))
    for rec in report.get("slides") or []:
        n = rec.get("n") or rec.get("slide") or slide_no(rec.get("file", ""))
        for t in rec.get("text_nodes") or []:
            note(f"render slide {n}", str(t.get("text", "")))
    return findings


def compare(copy: dict, report: dict, claims: dict | None) -> tuple[list[str], list[str]]:
    """Returns (drifted, uncited). Both empty means in sync."""
    drifted, uncited = [], []
    slides = normalize_slides(copy.get("slides"))
    laid_out = rendered_text(report)
    window = int(report.get("text_window") or RENDER_WINDOW)

    for key in sorted(slides, key=lambda k: (slide_no(k) or 0)):
        n = slide_no(key)
        if n is None:
            continue
        if n not in laid_out:
            drifted.append(f"{key}: authored but nothing rendered for slide {n}")
            continue
        haystack = laid_out[n]
        for s in strings_in(slides[key]):
            # Collapse whitespace first, then truncate, then skeletonise: the same order
            # render.py applies, so the needle is exactly what a dedicated node would hold.
            collapsed = re.sub(r"\s+", " ", str(s).strip())
            needle = skeleton(collapsed[:window])
            if not needle:
                continue
            if needle not in haystack:
                shown = s if len(s) <= 56 else s[:53] + "..."
                drifted.append(f"{key}: \"{shown}\" is in copy.json but was not laid out")

    # ...and the other way. Concatenated per slide for the same reason the forward direction
    # concatenates: a string split across spans is one authored string and three rendered nodes.
    authored_by_slide = {}
    for key in slides:
        n = slide_no(key)
        if n is None:
            continue
        authored_by_slide[n] = skeleton(" ".join(strings_in(slides[key])))
    drifted.extend(unauthored(report, authored_by_slide))

    if claims is not None:
        known = set()
        for c in (claims.get("claims") or claims.get("verified_claims") or []):
            if isinstance(c, dict):
                for k in ("id", "claim_id", "cid"):
                    if c.get(k):
                        known.add(str(c[k]))
                        break
        for key in sorted(slides, key=lambda k: (slide_no(k) or 0)):
            for cid in sorted(claim_ids_in(slides[key])):
                if cid not in known:
                    uncited.append(f"{key}: cites claim '{cid}', which is not in claims.json")
    return drifted, uncited


def run(date: str, out_root: Path) -> int:
    d = out_root / date
    copy_p, rep_p, claims_p = d / "copy.json", d / "render" / "render_report.json", d / "claims.json"

    for p in (copy_p, rep_p):
        if not p.exists():
            print(f"copy_sync: {p} is missing. Run the render before this gate.", file=sys.stderr)
            return 2
    try:
        copy = json.loads(copy_p.read_text(encoding="utf-8"))
        report = json.loads(rep_p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"copy_sync: unreadable artifact: {exc}", file=sys.stderr)
        return 2

    claims = None
    if claims_p.exists():
        try:
            claims = json.loads(claims_p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("copy_sync: claims.json is unreadable, so citations are NOT checked this run",
                  file=sys.stderr)

    drifted, uncited = compare(copy, report, claims)
    untraced, quoted_n = untraced_quotations(copy, claims)
    banned = banned_characters(copy, report)
    # The post's own year, off the run directory's name. Never the clock. See `redundant_year`.
    m_year = re.match(r"(\d{4})-\d{2}-\d{2}$", date)
    if not m_year:
        print(f"copy_sync: {date!r} is not a run date, so the post's own year cannot be read and "
              f"the redundant-year rule cannot run. That is a failure, not a skip.",
              file=sys.stderr)
        return 2
    dated = redundant_year(copy, report, m_year.group(1))
    n_slides = len(normalize_slides(copy.get("slides")))

    if not drifted and not uncited and not untraced and not banned and not dated:
        extra = ("" if claims is not None
                 else ", citations and quotations unchecked (no claims.json)")
        print(f"copy sync: clean, {n_slides} slide(s) match what the browser laid out{extra}")
        print("copy sync: no em dash, en dash, curly quote or emoji in the copy or the render")
        print(f"copy sync: no date on any frame prints {m_year.group(1)}, the post's own year")
        if claims is not None:
            print(f"copy sync: {quoted_n} quoted phrase(s) traced to a claim the slide declares")
        return 0

    if drifted:
        print(f"copy sync: {len(drifted)} string(s) in copy.json did not reach the render\n")
        for m in drifted:
            print(f"  {m}")
        print("\n  This is the record disagreeing with the deck. It almost always means a slide's\n"
              "  HTML was edited during pixel review and copy.json was not updated to match.\n"
              "  FIX copy.json to say what the slide says. Never edit the slide to match a stale\n"
              "  record: the render is what a reader receives.")
    if uncited:
        print(f"\ncopy sync: {len(uncited)} citation(s) point at nothing\n")
        for m in uncited:
            print(f"  {m}")
        print("\n  A slide citing a claim id that is not in the claims file breaks the one promise\n"
              "  this project makes about every fact. Add the claim or drop the citation.")
    if untraced:
        print(f"\ncopy sync: {len(untraced)} quotation(s) the record does not support, "
              f"of {quoted_n} checked\n")
        for m in untraced:
            print(f"  {m}")
        print("\n  A frame that sets words in quotation marks is telling a reader a document said\n"
              "  them. On 2026-08-26 one did not, and every other gate was green on it, because\n"
              "  copy.json, the render and the dossier all agreed with each other about a string\n"
              "  nobody had checked against a source. FIX THE FRAME, never the claim: writing a\n"
              "  new claim to fit a line the deck already drew is how the fabrication becomes\n"
              "  permanent.")
    if banned:
        print(f"\ncopy sync: {len(banned)} banned character(s) in the deck\n")
        for m in banned:
            print(f"  {m}")
        print("\n  CLAUDE.md bans these ANYWHERE, and a slide is anywhere. `caption_check` has\n"
              "  enforced the same three classes since it existed and has only ever been pointed\n"
              "  at the caption and the built site, so the nine frames were the one published\n"
              "  surface with no house-rule gate on them. On 2026-09-15 frame 5 shipped an en\n"
              "  dash through the render and the machine qa pass, and a pixel critic reading the\n"
              "  picture is what caught it. FIX BOTH SURFACES: the slide's HTML and copy.json.")
    if dated:
        print(f"\ncopy sync: {len(dated)} date(s) printing the post's own year\n")
        for m in dated:
            print(f"  {m}")
        print("\n  CLAUDE.md, owner's instruction 2026-09-11. The SITE is the one exception and a\n"
              "  deck is not the site, it is the post. `caption_check` has held this rule since\n"
              "  the day it was written and is only ever pointed at caption.txt, so on 2026-09-23\n"
              "  frame 7 set \"AUGUST 3RD, 2026\" three times while the caption of the same post\n"
              "  printed the same dates correctly. FIX BOTH SURFACES: the slide's HTML and\n"
              "  copy.json. Drop only the year, never the date.")
    return 1


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def report_of(*per_slide):
        return {"slides": [{"file": f"slide-{i:02d}.png", "n": i,
                            "text_nodes": [{"text": t} for t in texts]}
                           for i, texts in enumerate(per_slide, start=1)]}

    claims = {"claims": [{"id": "tx-2026-08-12-01"}, {"id": "tx-2026-08-12-02"}]}

    # THE SIBLING'S ACTUAL DEFECT, replayed. The HTML was hand-edited during pixel review and the
    # record kept the old kicker.
    copy = {"slides": {"S1": {"kicker": "HOW IT STARTED", "headline": "Four counties, one grid"}}}
    rep = report_of(["BEFORE THE CLASS", "Four counties, one grid"])
    drift, _ = compare(copy, rep, None)
    ok("a hand-edited kicker that left copy.json behind is CAUGHT", len(drift) == 1, str(drift))
    ok("...and the string it names is the stale one, not the good one",
       "HOW IT STARTED" in drift[0], str(drift))

    rep_ok = report_of(["HOW IT STARTED", "Four counties, one grid"])
    ok("a synced slide is clean", compare(copy, rep_ok, None) == ([], []))

    # Noise that must NOT trip it, or the gate gets switched off inside a week.
    for label, authored, laid in [
        ("case differs", "Four Counties, One Grid", "FOUR COUNTIES, ONE GRID"),
        ("punctuation differs", "Hood County, Texas", "Hood County Texas"),
        ("the browser wrapped a line", "Four counties one grid", "Four counties  one\ngrid"),
        ("a straight quote became a glyph", 'the "large load" rule', "the large load rule"),
    ]:
        d, _ = compare({"slides": {"S1": {"headline": authored}}}, report_of([laid]), None)
        ok(f"tolerates {label}", d == [], str(d))

    # The 80 character truncation in render.py. A long body can only ever be matched on a prefix.
    long_body = ("The commission opened a comment window on the rule that decides how quickly a "
                 "large load can be told to stop drawing power from the grid")
    truncated = long_body[:80]
    d, _ = compare({"slides": {"S1": {"body": long_body}}}, report_of([truncated]), None)
    ok("a long string truncated by the render still matches", d == [], str(d))

    # ...and a body rewritten anywhere INSIDE that window is still caught. This is the case the
    # first version of this file got wrong: it compared 40 characters, so a body that diverged at
    # character 64 passed. Every character the artifact recorded is now used.
    replaced = ("The commission opened a comment window on the rule that decides who pays for "
                "the transmission line instead")
    d, _ = compare({"slides": {"S1": {"body": long_body}}}, report_of([replaced[:80]]), None)
    # BOTH DIRECTIONS SPEAK HERE, and that is the improvement rather than a duplicate. The
    # authored body did not reach the slide, AND prose reached the slide that nobody authored.
    # Before the reverse direction existed only the first half was visible, and a slide whose
    # prose was typed in fresh rather than edited produced no finding at all.
    ok("a body rewritten inside the render's window is caught", len(d) == 2, str(d))
    ok("...as authored-but-not-rendered",
       any("is in copy.json but was not laid out" in x for x in d), str(d))
    ok("...and as rendered-but-not-authored",
       any("is in no authored string" in x for x in d), str(d))

    # THE KNOWN LIMIT, pinned so it stays a known limit. render.py writes down the first 80
    # characters of a node and no more, so a divergence past that point was never recorded and
    # cannot be asked about. This test exists to stop a later reader treating the miss as a bug
    # in the matcher and shortening the needle to "fix" it, which would trade a documented blind
    # spot for an undocumented one twice the size.
    tail_edit = long_body[:RENDER_WINDOW] + " and then something else entirely happened"
    d, _ = compare({"slides": {"S1": {"body": long_body}}},
                   report_of([tail_edit[:RENDER_WINDOW]]), None)
    ok("a divergence PAST the render's 80 character window is knowingly not detectable",
       d == [], str(d))

    # A headline split across spans: the parent and each child are separate nodes, and no single
    # one contains the whole authored string.
    d, _ = compare({"slides": {"S1": {"headline": "Four counties one grid"}}},
                   report_of(["Four counties", "one grid"]), None)
    ok("a headline split across two elements still matches", d == [], str(d))

    # Nesting and list shapes, both of which real artifacts use.
    d, _ = compare({"slides": [{"n": 1, "chips": ["PUCT", "ERCOT"]}]},
                   report_of(["PUCT ERCOT"]), None)
    ok("the list form of slides is read, not crashed on", d == [], str(d))
    d, _ = compare({"slides": [{"n": 1, "chips": ["PUCT", "RAILROAD COMMISSION"]}]},
                   report_of(["PUCT ERCOT"]), None)
    ok("...and a missing chip inside a list is still caught", len(d) == 1, str(d))

    # A slide that rendered nothing at all is the loudest possible version of this.
    d, _ = compare({"slides": {"S2": {"headline": "Anything"}}}, report_of(["S1 only"]), None)
    ok("a slide with no render at all is caught", len(d) == 1, str(d))

    # CITATIONS. The gap between claims_check and the deck.
    _, un = compare({"slides": {"S1": {"headline": "x", "claim_ids": ["tx-2026-08-12-01"]}}},
                    report_of(["x"]), claims)
    ok("a citation that resolves is clean", un == [], str(un))
    _, un = compare({"slides": {"S1": {"headline": "x", "claim_ids": ["tx-2026-08-12-07"]}}},
                    report_of(["x"]), claims)
    ok("a slide citing a claim that does not exist is CAUGHT", len(un) == 1, str(un))
    ok("...and it names the id", "tx-2026-08-12-07" in un[0], str(un))

    _, un = compare({"slides": {"S1": {"headline": "x", "claim_ids": ["tx-2026-08-12-01"]}}},
                    report_of(["x"]), None)
    ok("citations are skipped rather than guessed when claims.json is absent", un == [])

    # claim_ids must not be hunted for in the rendered text. A correct slide does not print its
    # own citations, and an earlier shape of this check failed every deck for that reason.
    d, _ = compare({"slides": {"S1": {"headline": "x", "claim_ids": ["tx-2026-08-12-01"]}}},
                   report_of(["x"]), claims)
    ok("a claim id is never expected to appear in the artwork", d == [], str(d))

    # Nested citation shapes, since the copywriter emits per-string ids too.
    _, un = compare({"slides": {"S1": {"headline": "x",
                                       "stats": [{"stat": "x", "claim_id": "tx-2026-08-12-09"}]}}},
                    report_of(["x"]), claims)
    ok("a citation nested inside a stat is still checked", len(un) == 1, str(un))

    # ---------------------------------------------------------------- the denylist
    # THE HOLE THAT MADE THIS GATE ORNAMENTAL. Key names were an allowlist, so a slide using a
    # key the list did not name was skipped in silence. The 2026-08-16 deck used hook, hook2,
    # tag, tag2, dek, bodies, how, rows, attribution, site, source2 and when1, and twelve of its
    # nineteen key names were invisible here. The gate reported clean having never read the
    # deck's prose.
    d, _ = compare({"slides": {"S1": {"dek": "A key name nobody thought of in advance"}}},
                   report_of(["something else entirely"]), None)
    ok("a key name the gate was never taught is still checked", len(d) == 1, str(d))
    d, _ = compare({"slides": {"S1": {"hook": "One roof.", "tag2": "SITE PLAN NOT PUBLIC."}}},
                   report_of(["One roof. SITE PLAN NOT PUBLIC."]), None)
    ok("...and an invented key that DID render is clean", d == [], str(d))
    d, _ = compare({"slides": {"S1": {"headline": "x", "technique": "hachured soil section"}}},
                   report_of(["x"]), None)
    ok("machinery keys are still not demanded on the slide", d == [], str(d))

    # ---------------------------------------------------------------- the reverse direction
    # A sentence typed straight into a slide's HTML enters no manifest, so nothing downstream
    # that reads the manifest can see it. That is how an untraced "SB 6" reached a published
    # slide on 2026-08-16 with every gate green.
    def rich(nodes):
        return {"slides": [{"n": 1, "file": "slide-01.png", "text_nodes": nodes}]}

    prose = "This sentence was typed straight into the slide and entered no manifest at all."
    d, _ = compare({"slides": {"S1": {"headline": "Authored"}}},
                   rich([{"text": "Authored"}, {"text": prose}]), None)
    ok("prose that was rendered but never authored is CAUGHT", len(d) == 1, str(d))

    # The three carve-outs, each of which must stay quiet or the gate gets ignored.
    d, _ = compare({"slides": {"S1": {"headline": "Authored"}}},
                   rich([{"text": "Authored"}, {"text": prose, "decorative": True}]), None)
    ok("...unless the design marked it decorative", d == [], str(d))
    d, _ = compare({"slides": {"S1": {"headline": "Authored"}}},
                   rich([{"text": "Authored"}, {"text": "TEXAS AI DOCKET"},
                         {"text": "03 / 08"}, {"text": "10,000 FT A SIDE"}]), None)
    ok("...and the masthead, the counter and a label are not demanded", d == [], str(d))

    # The provenance stamp is furniture, but STRIPPED rather than exempting its whole node,
    # because it arrives concatenated with real text and exempting the node would blind the gate
    # to whatever sits beside it.
    d, _ = compare({"slides": {"S1": {"tag": "THE PLANT IS ANNOUNCED."}}},
                   rich([{"text": "THE PLANT IS ANNOUNCED. CLAIM c7. QUOTED VERBATIM."}]), None)
    ok("a claim stamp beside authored text is not demanded", d == [], str(d))
    d, _ = compare({"slides": {"S1": {"headline": "Authored"}}},
                   rich([{"text": "Authored"}, {"text": prose + " CLAIM c9."}]), None)
    ok("...but unauthored prose beside a stamp is still CAUGHT", len(d) == 1, str(d))
    d, _ = compare({"slides": {"S1": {"tag": "THE PLANT IS ANNOUNCED."}}},
                   rich([{"text": "THE PLANT IS ANNOUNCED. CLAIMS c7, c9 and c11. COMPUTED."}]), None)
    ok("a multi id stamp is stripped too", d == [], str(d))
    # The word "claim" is English before it is furniture.
    _dek = "Each one with the claim whose own words prove its shape."
    ok("the ENGLISH word claim is not eaten out of a sentence",
       CLAIM_STAMP.sub(" ", _dek).strip() == _dek,
       repr(CLAIM_STAMP.sub(" ", _dek).strip()))
    d, _ = compare({"slides": {"S1": {"dek": _dek}}}, rich([{"text": _dek}]), None)
    ok("...so a dek that uses it comes back clean", d == [], str(d))
    ok("a real stamp is still removed",
       CLAIM_STAMP.sub(" ", "THE PLANT IS ANNOUNCED. CLAIM c7. QUOTED VERBATIM.").strip()
       == "THE PLANT IS ANNOUNCED.")

    # The shipped deck of 2026-08-16, which is the artifact this direction was built from. It
    # must come back clean, or the carve-outs are wrong in the other direction.
    shipped = REPO_ROOT / "runs" / "carousel" / "2026-08-16"
    if (shipped / "copy.json").exists() and (shipped / "render_report.json").exists():
        sd, su = compare(json.loads((shipped / "copy.json").read_text(encoding="utf-8")),
                         json.loads((shipped / "render_report.json").read_text(encoding="utf-8")),
                         json.loads((shipped / "claims.json").read_text(encoding="utf-8")))
        # THE WINDOW REGRESSION, pinned. On 2026-08-19 render.py's window widened from 80 to 320 and
    # this file's constant widened with it, which mis-truncated every authored string longer than
    # 80 characters when replayed against a report written at 80. The 2026-08-16 deck failed in CI
    # within one run. The window belongs to the REPORT, and a report without the field is 80.
    _long = "x" * 200
    _rep80 = {"slides": [{"n": 1, "text_nodes": [{"text": _long[:80]}]}]}
    _rep320 = {"text_window": 320, "slides": [{"n": 1, "text_nodes": [{"text": _long}]}]}
    _copy = {"slides": {"S1": {"body": _long}}}
    ok("a report written at 80 is compared at 80, not at today's constant",
       compare(_copy, _rep80, None)[0] == [], str(compare(_copy, _rep80, None)[0]))
    ok("...and a report that declares 320 is compared at 320",
       compare(_copy, _rep320, None)[0] == [], str(compare(_copy, _rep320, None)[0]))
    ok("...and real drift past character 80 is still caught at 320",
       compare({"slides": {"S1": {"body": _long + " and a sentence never rendered."}}},
               _rep320, None)[0] != [])

    ok("the first shipped deck passes both directions", sd == [] and su == [],
           str(sd + su)[:300])

    # ---------------------------------------------------------------- quotations
    # THE 2026-08-26 DEFECT, REPLAYED AGAINST THE RUN'S OWN CLAIMS FILE.
    #
    # The claims half is the real committed artifact and is not reconstructed. The frame half is,
    # from the storyboard's own `replanned` block written before this gate existed, at
    # runs/carousel/2026-08-26/held/storyboard.md: a line reading "clinical care, research,
    # advanced computing" under the attribution BOARD ITEM, AUGUST 12TH, 2026, on a frame
    # declaring c12 and c23. That is the artifact as it reached the panel.
    #
    # A MISSING FILE IS A FAILURE HERE AND NOT A SKIP. A skip and a check that cannot run print
    # the same colour, and this is the one case in the file that proves the gate goes red on
    # something that really happened.
    held = REPO_ROOT / "runs" / "carousel" / "2026-08-26"
    if not (held / "claims.json").exists():
        ok("the 2026-08-26 claims file is present to replay the defect against", False,
           str(held / "claims.json"))
    else:
        real_claims = json.loads((held / "claims.json").read_text(encoding="utf-8"))
        shipped_to_panel = {"slides": {"S7": {
            "claims": ["c12", "c23"],
            "kicker": "TWO DOCUMENTS",
            "hook": "The difference is two words wide",
            "attribution_board": "BOARD ITEM, AUGUST 12TH, 2026",
            "line_board": '"clinical care, research, advanced computing"',
        }}}
        f, n = untraced_quotations(shipped_to_panel, real_claims)
        ok("the fabricated board quotation of 2026-08-26 is CAUGHT", len(f) == 1, str(f))
        ok("...and it is named as occurring in no claim at all",
           bool(f) and "occurs in NO" in f[0], str(f))
        ok("...and the message names the claims the frame did declare",
           bool(f) and "c12, c23" in f[0], str(f))
        ok("...and the phrase was examined rather than skipped", n == 1, str(n))

        # THE REPAIRED FRAME, the real committed copy.json, must come back clean. A gate that
        # cannot tell the fix from the defect has not measured anything.
        repaired = json.loads((held / "copy.json").read_text(encoding="utf-8"))
        f, n = untraced_quotations(repaired, real_claims)
        ok("the repaired deck of 2026-08-26 is clean", f == [], str(f)[:300])
        ok("...and it checked the phrases rather than passing by examining none", n > 0, str(n))

        # THE PROVENANCE HALF, and it is the discrimination test for this gate. A version that
        # compared against EVERY claim in the file instead of the slide's own would pass this,
        # and the two implementations are indistinguishable without it. The words below are c23's
        # quote, verbatim, printed on a frame that declares only c12. That is the shape slide 6
        # shipped three times over on the same deck.
        wrong = {"slides": {"S9": {
            "claims": ["c12"],
            "above_line": '"technology, data and AI are embedded to support clinicians"'}}}
        f, _ = untraced_quotations(wrong, real_claims)
        ok("a real quote cited to the WRONG claim is caught", len(f) == 1, str(f))
        ok("...and it names the claim the words actually came from",
           bool(f) and "c23" in f[0], str(f))
        ok("...and the same words on the slide that DOES declare c23 are clean",
           untraced_quotations({"slides": {"S9": {
               "claims": ["c23"],
               "above_line": '"technology, data and AI are embedded to support clinicians"'}}},
               real_claims)[0] == [])

    # CALIBRATION ON EVERY DECK THIS REPO HAS RENDERED. A gate is only worth keeping if it is
    # quiet on real work, and the count is asserted beside the silence so a run that examined
    # nothing cannot read as a run that found nothing.
    seen_decks = 0
    for name, expect_checked in (("2026-08-16", 4), ("2026-08-18", 3), ("2026-08-19", 6),
                                 ("2026-08-20", 0), ("2026-08-21", 1), ("2026-08-22", 9)):
        base = REPO_ROOT / "runs" / "carousel" / name
        if not ((base / "copy.json").exists() and (base / "claims.json").exists()):
            continue
        seen_decks += 1
        f, n = untraced_quotations(json.loads((base / "copy.json").read_text(encoding="utf-8")),
                                   json.loads((base / "claims.json").read_text(encoding="utf-8")))
        ok(f"{name}: no untraced quotation on a shipped deck", f == [], str(f)[:200])
        ok(f"{name}: {expect_checked} quoted phrase(s) examined", n == expect_checked, str(n))
    ok("the calibration read the shipped decks rather than finding none", seen_decks >= 5,
       str(seen_decks))

    # THE CARVE-OUTS, each of which has to stay quiet or the gate gets switched off.
    cl2 = {"claims": [{"id": "c1", "quote": "the queue holds 6,180 megawatts of large load"}]}
    d1 = {"slides": {"S1": {"claims": ["c1"], "tag": 'the so-called "queue" of large load'}}}
    ok("a single quoted word is a scare quote and is not demanded",
       untraced_quotations(d1, cl2)[0] == [], str(untraced_quotations(d1, cl2)))
    d2 = {"slides": {"S1": {"claims": ["c1"], "line": '"holds 6,180 megawatts"'}}}
    ok("a quoted phrase the declared claim carries passes",
       untraced_quotations(d2, cl2)[0] == [], str(untraced_quotations(d2, cl2)))
    d3 = {"slides": {"S1": {"claims": ["c1"], "line": '"holds 6,180 gigawatts"'}}}
    ok("...and one word changed inside it is CAUGHT", len(untraced_quotations(d3, cl2)[0]) == 1)
    # PUNCTUATION AND CASE ARE NOT THE DEFECT. The render sets quotations in the deck's own
    # typography, so a comparison that failed on a capital would fail on every correct frame.
    d4 = {"slides": {"S1": {"claims": ["c1"], "line": '"HOLDS 6,180 MEGAWATTS"'}}}
    ok("case and punctuation differences are tolerated",
       untraced_quotations(d4, cl2)[0] == [], str(untraced_quotations(d4, cl2)))
    # THE KEY NAME ARM, which is a widening and not the selector.
    d5 = {"slides": {"S1": {"claims": ["c1"], "band_quote": "holds 6,180 megawatts"}}}
    ok("a key named quote is checked without any marks around its value",
       untraced_quotations(d5, cl2)[1] == 1)
    d6 = {"slides": {"S1": {"claims": ["c1"], "band_quote": "holds 6,180 gigawatts"}}}
    ok("...and goes red the same way", len(untraced_quotations(d6, cl2)[0]) == 1)
    # A CLAIM'S TEXT IS NOT A QUOTE. The record's own sentence about a document is where the
    # 2026-08-26 recommendation was written up as a completed action, and a frame quoting that
    # sentence back would be the same fault one surface along.
    cl3 = {"claims": [{"id": "c1", "text": "The board appropriated the money.", "quote": "x y"}]}
    d7 = {"slides": {"S1": {"claims": ["c1"], "line": '"The board appropriated the money"'}}}
    ok("a frame quoting the claim's TEXT rather than its quote is caught",
       len(untraced_quotations(d7, cl3)[0]) == 1, str(untraced_quotations(d7, cl3)))
    # NO CLAIMS FILE MEANS NOTHING WAS CHECKED, and the count says so rather than reporting clean.
    ok("with no claims file the gate reports zero checked rather than clean",
       untraced_quotations(d3, None) == ([], 0))
    # A slide that declares nothing cannot support a quotation, and the message has to say so
    # rather than crashing on an empty list.
    d8 = {"slides": {"S1": {"line": '"holds 6,180 megawatts"'}}}
    ok("a quotation on a slide that declares no claim is caught",
       len(untraced_quotations(d8, cl2)[0]) == 1, str(untraced_quotations(d8, cl2)))
    ok("...and the message says the slide declares nothing",
       "declares nothing" in untraced_quotations(d8, cl2)[0][0])
    ok("the module header states the blind spot rather than implying coverage",
       "NOT COVERED" in (__doc__ or "") and "unquoted string" in (__doc__ or ""))

    # ---------------------------------------------------------- BANNED CHARACTERS, 2026-09-15
    #
    # REPLAYED AGAINST A REAL SHIPPED DECK, not against a fixture invented here. GATE_LESSONS 16
    # and 63: a fixture written by the author of a detector agrees with the detector, and only a
    # real artifact carries the shapes nobody thought to write down. This deck prints a MIDDLE DOT
    # five times in its furniture, which is legitimate, non-ASCII, and exactly the kind of
    # character a lazier rule would have failed.
    #
    # THE NEWEST SHIPPED RUN, not a pinned date, so the replay follows the corpus forward. If no
    # shipped run carries a render report this FAILS rather than skipping: a skipped test and a
    # passing test are the same colour, which is GATE_LESSONS 15.
    shipped = sorted(p for p in (REPO_ROOT / "runs" / "carousel").glob("*/render_report.json"))
    ok("a shipped run with a render report exists to replay this against", bool(shipped),
       "runs/carousel/*/render_report.json matched nothing")
    if shipped:
        live = shipped[-1].parent
        real_copy = json.loads((live / "copy.json").read_text(encoding="utf-8"))
        real_rep = json.loads((live / "render_report.json").read_text(encoding="utf-8"))
        ok(f"the shipped deck at {live.name} carries no banned character",
           banned_characters(real_copy, real_rep) == [],
           str(banned_characters(real_copy, real_rep)))
        # ...and that is not a vacuous pass, which needs a deck whose render actually carries
        # legitimate non-ASCII: a clean result on an all-ASCII deck proves only that there was
        # nothing to find.
        #
        # THIS USED TO ASK THE NEWEST DECK FOR THAT WITNESS AND THE NEWEST DECK DOES NOT OWE IT.
        # It read the middle dot in 2026-09-15's furniture and assumed the corpus would keep
        # handing it one. On 2026-09-16 a deck shipped whose every surface is straight quotes and
        # plain ASCII, which is the house rule being obeyed rather than broken, and this assertion
        # went red on a deck that was right. A test that fails when the product gets cleaner is
        # measuring the corpus, not the detector.
        #
        # So the witness is SEARCHED FOR, newest first, and the tolerance claim is made against
        # the deck that can carry it. The non-vacuity guarantee needs SOME real shipped deck with
        # non-ASCII in it, never this particular one. It still FAILS rather than skipping when no
        # shipped deck carries any, because a skipped test and a passing test are the same colour.
        def rendered_text(rep: dict) -> str:
            return " ".join(str(t.get("text", ""))
                            for rec in (rep.get("slides") or [])
                            for t in (rec.get("text_nodes") or []))

        witness, witness_rep = None, None
        for cand in reversed(shipped):
            rep = json.loads(cand.read_text(encoding="utf-8"))
            if any(ord(c) > 0x7F for c in rendered_text(rep)):
                witness, witness_rep = cand.parent, rep
                break
        ok("a shipped deck whose render carries non-ASCII exists to prove the pass is not vacuous",
           witness is not None,
           "no shipped deck carries a character above ASCII, so the tolerance claim proves nothing")
        if witness is not None:
            witness_copy = json.loads((witness / "copy.json").read_text(encoding="utf-8"))
            ok(f"...and that deck ({witness.name}) is clean, so legitimate non-ASCII is tolerated",
               banned_characters(witness_copy, witness_rep) == [],
               str(banned_characters(witness_copy, witness_rep)))

        # THE DEFECT AS IT SHIPPED. The en dash goes back into the string that carried it.
        hurt = json.loads(json.dumps(real_rep))
        put = 0
        for rec in hurt.get("slides") or []:
            for t in rec.get("text_nodes") or []:
                if "SEPTEMBER" in str(t.get("text", "")) and " TO " in str(t.get("text", "")):
                    t["text"] = str(t["text"]).replace(" TO ", "–", 1)
                    put += 1
        if not put:                      # no dated range on this deck: put one on slide 1
            slides = hurt.get("slides") or [{}]
            slides[0].setdefault("text_nodes", []).append(
                {"text": "SEPTEMBER 14–15, 2026"})
            put = 1
        found = banned_characters(real_copy, hurt)
        ok("the 2026-09-15 defect, put back into the real render, is CAUGHT",
           len(found) == put, str(found))
        ok("...and the finding names the render, the character and the string",
           bool(found) and "render slide" in found[0] and "dash" in found[0]
           and "SEPTEMBER" in found[0], str(found))
        ok("...and tells the writer to spend X to Y instead",
           bool(found) and "X to Y" in found[0], str(found))

        # WHY THIS GATE WAS BLIND. Its normaliser deletes the character class. Stated as an
        # assertion so that nobody later "simplifies" the two checks into one comparison.
        ok("skeleton() erases a dash, which is why the sync direction could never see one",
           skeleton("SEPTEMBER 14–15") == skeleton("SEPTEMBER 1415"))

    # THE RECORD IS CHECKED TOO, because a pixel round can edit HTML alone or copy alone.
    cq = {"slides": {"S1": {"line": "the board’s decision"}}}
    p = banned_characters(cq, {})
    ok("a curly quote in copy.json alone is caught", len(p) == 1, str(p))
    ok("...and the finding names copy.json and the slide", bool(p) and "copy.json S1" in p[0])
    em = {"slides": {"S1": {"line": "the load rose—then fell"}}}
    ok("an em dash in copy.json alone is caught", len(banned_characters(em, {})) == 1)
    ej = {"slides": [{"n": 1}]}
    rep_ej = {"slides": [{"n": 1, "text_nodes": [{"text": "grid \U0001F600"}]}]}
    ok("an emoji in the render alone is caught", len(banned_characters(ej, rep_ej)) == 1)

    # THE CHARACTERS THIS DECK LEGITIMATELY PRINTS MUST NOT FAIL. A middle dot separates the
    # stamp's fields, a degree sign and a multiplication sign are figures, and a hyphen is a
    # hyphen. A rule that swept "non-ASCII" or "any dash" would fail correct frames, and a gate
    # that fails a correct product is how a gate gets switched off.
    fine = {"slides": {"S1": {
        "stamp": "ERCOT BOARD · ITEM 10 · SEPTEMBER 14TH TO 15TH, 2026",
        "note": "a 12-week window at 104°F across 3 × 400 MW"}}}
    ok("a middle dot, a degree sign, a times sign and a hyphen all pass",
       banned_characters(fine, {}) == [], str(banned_characters(fine, {})))

    # HOW IT IS DRAWN IS NOT READER COPY. META_KEYS already exempts `palette` and `technique`,
    # and this check inherits that rather than keeping its own opinion of what counts.
    drawn = {"slides": {"S1": {"palette": "bond — forging", "technique": "hatch — c6"}}}
    ok("a dash in a key META_KEYS exempts is not reported",
       banned_characters(drawn, {}) == [], str(banned_characters(drawn, {})))

    # ONE LIST. If caption_check stops owning these, this must break loudly rather than drift.
    import caption_check as _house
    ok("the banned classes are imported from caption_check, never restated here",
       _house.DASHES.search("a–b") is not None and _house.CURLY.search("“x”")
       is not None and _house.emojis("\U0001F600") == ["\U0001F600"])

    # ------------------------------------------------- A DATE IN THE POST'S OWN YEAR, 2026-09-23
    #
    # THE DEFECT AS IT SHIPPED, verbatim from carousel no. 32's frame 7 before a scorer read the
    # picture. All four of these go green on the pre-fix code, because the pre-fix code did not
    # look at a slide at all.
    frame7 = {"slides": {"S7": {
        "kicker": "AUGUST 3RD, 2026",
        "dek": "The audit was ordered August 3rd, 2026. The directive came 49 days later."}}}
    rep7 = {"slides": [{"n": 7, "text_nodes": [{"text": "AUGUST 3RD, 2026"}]}]}
    hits = redundant_year(frame7, rep7, "2026")
    ok("the 2026-09-23 defect is CAUGHT on the record and on the render",
       len(hits) == 3, str(hits))
    ok("...and the ALL CAPS form is seen, which is the only form a hook ever sets",
       any("AUGUST 3RD, 2026" in h and "render slide 7" in h for h in hits), str(hits))
    ok("...and the finding names the bare date to write instead",
       any("'August 3rd'" in h for h in hits), str(hits))
    ok("...and it names the surface, so a repair lands on the frame that was named",
       any(h.startswith("copy.json S7") for h in hits), str(hits))

    # THE HALF THAT MAKES IT A RULE ABOUT REDUNDANCY. A date outside the post's year keeps it.
    other = {"slides": {"S1": {"line": "the rule was adopted September 5th, 2019"}}}
    ok("a date outside the post's own year is untouched",
       redundant_year(other, {}, "2026") == [], str(redundant_year(other, {}, "2026")))
    ok("...and the same date IS caught in a post from that year",
       len(redundant_year(other, {}, "2019")) == 1, str(redundant_year(other, {}, "2019")))
    bare = {"slides": {"S1": {"line": "the audit was ordered August 3rd"}}}
    ok("the corrected form passes", redundant_year(bare, {}, "2026") == [],
       str(redundant_year(bare, {}, "2026")))

    # A GATE THAT CANNOT READ ITS YEAR IS RED, NEVER GREEN. GATE_LESSONS 37: a skip and an
    # unavailable check are not the same event. The year comes off the run directory's name, so
    # a caller that hands this a clock, a None or a date it cannot parse gets a refusal.
    for bad in (None, "2026-09-23", "26", 2026):
        try:
            redundant_year(bare, {}, bad)
        except SystemExit:
            pass
        else:
            ok(f"a year of {bad!r} refuses to run", False, "it returned instead of refusing")
            break
    else:
        ok("a year it cannot read is a refusal to run, not a pass", True)

    # ONE PATTERN. If caption_check stops owning DATED_YEAR this breaks loudly rather than drift,
    # and the case that matters is the uppercase month: GATE_LESSONS 35 is a date rule that could
    # see every form except the one the renderer emits.
    ok("DATED_YEAR is imported from caption_check and reads an uppercase month",
       _house.DATED_YEAR.search("AUGUST 3RD, 2026") is not None)

    ok("the repair is cut at the year, not at a comma, so an uncommaed date is not handed back",
       any("Write 'AUGUST 25TH'" in h
           for h in redundant_year({"slides": {"S7": {"k": "AUGUST 25TH 2026"}}}, {}, "2026")),
       str(redundant_year({"slides": {"S7": {"k": "AUGUST 25TH 2026"}}}, {}, "2026")))

    # REPLAYED AGAINST THE REAL SHIPPED CORPUS, for the reason the character replay above is.
    #
    # AND NOT AS "every shipped deck is clean", WHICH IS THE ASSERTION THIS BLOCK STARTED AS AND
    # WHICH WENT RED ON 21 OF 31 DECKS. The rule was written on 2026-09-11 and the corpus reaches
    # back to 2026-08-16, so most of it was drawn before the rule existed and three decks after
    # it broke it. **A test that asserts the corpus is clean is measuring the corpus**, which is
    # the trap written up against the non-ASCII witness forty lines above, and it would have put
    # this gate's own suite permanently red over copy nobody is going to redraw.
    #
    # What a replay owes is DISCRIMINATION: on real rendered strings, does the rule separate the
    # year it is about from every other year on the same frames? So the corpus is measured rather
    # than graded, and the two halves are asserted against each other.
    corpus_hits, other_years = 0, 0
    for cand in shipped:
        live = cand.parent
        cp = live / "copy.json"
        if not cp.exists():
            continue
        yr = live.name[:4]
        rep = json.loads(cand.read_text(encoding="utf-8"))
        cpy = json.loads(cp.read_text(encoding="utf-8"))
        found = redundant_year(cpy, rep, yr)
        corpus_hits += len(found)
        ok(f"{live.name}: every finding is a date in {yr} and no other year",
           all(f"prints the year and this post ships in {yr}" in h for h in found), str(found))
        # ...and the same deck read as though it shipped in a year it cannot contain must be
        # silent. This is the half that proves the rule is about the POST'S year rather than
        # about years, and it cannot pass by accident on a deck with no dates at all.
        #
        # THE COUNTERFACTUAL YEAR IS 1999 AND IT IS NOT AN ARBITRARY NUMBER. The first cut of
        # this probe used 2025 and 2027, and it went red with ten findings, correctly: the record
        # carries real dates in the years either side of the post and those decks print them with
        # their years, which is the rule working. A counterfactual probe has to name a year the
        # corpus cannot contain, or it measures the record rather than the rule.
        quiet = redundant_year(cpy, rep, "1999")
        ok(f"{live.name}: read as a 1999 post, the same frames report nothing",
           quiet == [], str(quiet))
        other_years += len(quiet)
    ok("the rule fires on real shipped rendered strings, so the replay is not vacuous",
       corpus_hits > 0, f"{corpus_hits} findings across {len(shipped)} shipped decks")
    ok("...and is silent on every one of them under a year the corpus cannot hold",
       other_years == 0, f"{other_years} findings under a counterfactual year")

    if failures:
        print(f"\ncopy_sync_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\ncopy_sync_check self-test: all passed (each report is compared at the window it "
          f"declares, falling back to {RENDER_WINDOW} chars for reports written before the field)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="run date, e.g. 2026-08-12")
    ap.add_argument("--out", default=str(REPO_ROOT / "out"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.date:
        print("copy_sync_check: pass --date or --self-test", file=sys.stderr)
        return 2
    return run(a.date, Path(a.out))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"copy_sync_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
