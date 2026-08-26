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
    n_slides = len(normalize_slides(copy.get("slides")))

    if not drifted and not uncited:
        extra = "" if claims is not None else ", citations unchecked (no claims.json)"
        print(f"copy sync: clean, {n_slides} slide(s) match what the browser laid out{extra}")
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
