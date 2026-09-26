#!/usr/bin/env python3
"""shipped_check.py — run the gates against what was actually published.

WHY THIS EXISTS, and it is the multiplier on every other gate in this suite.

An audit of `.github/workflows/guards.yml` on 2026-08-19 found that of its fifteen carousel
steps, THIRTEEN are `--self-test`. The only two that touch a real artifact are
`email_check --all` and `bespoke_check --slides-dir examples/demo-deck/slides`, and the second
of those points at a demo deck rather than at anything this project has ever published.

So CI proved, every run, that the checkers CAN go red, and almost never asked them whether the
product was clean. `coherence_check`, `craft_floor`, `run_complete`, `sources_block`,
`plan_render_check` and `absence_check` were in CI in no form at all. Six gates, all of them
written BY these runs to catch defects these runs shipped, protecting only the runs that
remembered to call them, which is the exact defect each was written for.

That is UPGRADE_BACKLOG item 6, and it outranks everything else on that page.

WHY ONE SCRIPT RATHER THAN NINE CI STEPS

`.github/workflows/**` is `human` owned, so a routine cannot connect its own gate. Every gate
built by an upgrade phase has therefore needed a maintainer to wire it, and three of them
waited. One step in the workflow calling one script here means the next gate is one function
call away, in a file the upgrade lane already owns.

WHAT IT DOES NOT DO

It does not re-render. The gates that need pixels (`qa.py`) need a browser, and a shipped run
already carries the machine_qa.json its render produced. This reads the committed artifacts and
asks whether they still agree with each other and with today's rules.

THE ONE JUDGEMENT IN HERE. A gate written after a deck shipped can be red on that deck for
reasons that are true and not actionable, which happened when the render window widened from 80
to 320 and turned an unchanged 2026-08-16 deck red. So each gate is registered with a scope:

    HISTORY   must hold for every deck ever shipped. A breach is a real regression.
    CURRENT   must hold for the newest deck. Older decks report as a note.

    shipped_check.py                 every shipped run
    shipped_check.py --run 2026-08-19
    shipped_check.py --self-test
"""
from __future__ import annotations

import argparse
import html
import io
import datetime as _dt
import json
import contextlib
import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"
sys.path.insert(0, str(Path(__file__).resolve().parent))

HISTORY, CURRENT = "history", "current"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# --------------------------------------------------------------------------- the gates
def g_copy_sync(d: Path):
    """AND THE POST'S OWN YEAR, which this adapter did not reach either.

    `copy_sync_check.redundant_year` enforces the rule that a date in the post's own year
    carries no year, on every authored string in `copy.json` and every node the browser laid
    out. It was added on 2026-09-23 out of frame 7 printing 2026 four times through nine green
    gates, and it was reachable only from `copy_sync_check.run()`. This adapter called
    `compare()` alone, so the production sweep could not see it.

    The run directory's own name carries the year, which is the same source `sources_block`
    uses and for the same reason: rebuilding an old run years later must render what that run
    published rather than what the clock says today.
    """
    import copy_sync_check as m
    copy, rep = _load(d / "copy.json"), _load(d / "render_report.json")
    if not (copy and rep):
        return None
    claims = _load(d / "claims.json")
    drifted, uncited = m.compare(copy, rep, claims)
    out = list(drifted) + list(uncited)
    if d.name[:4].isdigit():
        years = list(m.redundant_year(copy, rep, d.name[:4]))
        # ITS OWN SINCE-DATE, for the reason stated at RESERVE_SINCE and FIGURE_SINCE, and this
        # one was learned by running it. Wiring the check into the sweep turned ELEVEN already
        # published decks red in one go, back to 2026-09-02, over a rule nothing enforced when
        # they shipped. That is a gate reaching back to reclassify history, which is the exact
        # fault `g_completion`'s own docstring records about the threshold moving from 6.8 to
        # 6.7 and taking two held decks red with it. The decks did not change. The ruler did.
        #
        # The house rule itself is older than the gate, which is the uncomfortable half and is
        # why this is a note rather than a deletion: some of those decks broke a rule that was
        # in force. What none of them had was anything that could tell them. The finding is
        # MEASURED and PRINTED for every one of them, which is the difference between a
        # carve-out and a switched-off check, and published copy is not something a sweep can
        # fix anyway.
        if d.name <= YEAR_SINCE:
            if years and not out:
                return (f"the post's own year check was wired into this sweep on "
                        f"{_dt.date.fromisoformat(YEAR_SINCE) + _dt.timedelta(days=1)} and this "
                        f"deck shipped before anything enforced it. Run into it anyway it "
                        f"reports {len(years)} finding(s), first: {str(years[0])[:180]}")
        else:
            out += years
    return out


def g_quotations(d: Path):
    """Every phrase a frame sets as a source's own words, against the claims that slide declares.

    Registered separately from `copy sync` rather than folded into it, because the two answer
    different questions and a run reading one line needs to know which one broke. `compare` asks
    whether the deck and its manifest agree. This asks whether the DOCUMENT agrees, which is the
    question that was open on 2026-08-26 while both of the others were green.

    HISTORY scope, and that is a measurement rather than an assumption. Every deck this repo has
    shipped comes back clean, 23 quoted phrases across six of them, so this is not a rule written
    after the fact being applied backwards. See the trap written up on `aggregates` below.
    """
    import copy_sync_check as m
    copy, claims = _load(d / "copy.json"), _load(d / "claims.json")
    if not (copy and claims):
        return None
    findings, _checked = m.untraced_quotations(copy, claims)
    return findings


def g_aggregates(d: Path):
    import aggregate_check as m
    rep, agg = _load(d / "render_report.json"), _load(d / "aggregates.json")
    claims = _load(d / "claims.json")
    if not (rep and agg is not None and claims):
        return None
    # EVERY SURFACE THE CHECKER READS, ASKED FOR RATHER THAN LISTED. `aggregate_check` learned to
    # read the caption on 2026-08-26 and this adapter did not, so a caption-only figure came back
    # as a leftover declaration. The fix listed the caption here by hand, and the next day the
    # document title did the identical thing to the identical line. A gate wired to half its own
    # checker reports the half it can see, and a hand-kept list of surfaces is how it gets there.
    # `m.surfaces()` owns the list now, so this adapter cannot fall behind a third time.
    sf = m.surfaces(d)
    probs = m.check(rep, agg, claims, sf["caption"], sf["title"], sf["comment"])
    return list(probs) if probs else []


def g_dossiers(d: Path):
    """check(dossiers, expected, breathers), not (raw_text, report).

    The reachability assertion in the self-test is what caught this: the first draft passed the
    raw markdown where a parsed dict belongs, threw, and was silently skipped on every run. A
    registry entry whose loader always errors reports clean forever, which is the same shape as
    craft_floor reading a key qa.py never wrote.
    """
    import dossier_check as m
    sb = d / "storyboard.md"
    if not sb.exists():
        return None
    dossiers = m.parse_dossiers(sb.read_text(encoding="utf-8"))
    if not dossiers:
        return None
    rep = _load(d / "render_report.json") or {}
    expected = len(rep.get("slides") or []) or None
    return list(m.check(dossiers, expected, None) or [])


def g_coherence(d: Path):
    import coherence_check as m
    copy = _load(d / "copy.json")
    if not copy:
        return None
    fails, warns = m.check_copy(copy)
    sd = d / "slides"
    if sd.exists():
        f2, _ = m.check_type_spine(sd)
        f3, _ = m.check_site_line(sd)
        fails += f2 + f3
    return fails


def g_craft_floor(d: Path):
    """AND THE SOURCE SCAN, which this adapter did not reach.

    `craft_floor.network_calls` refuses a render-time Fetch API call in slide source, because
    over `file://` that is a promise nobody can keep and the frame renders empty with zero
    errors and zero warnings. It was added on 2026-09-23 and enforced only by the CLI, while
    `guards.yml` sweeps every shipped run through THIS function, which read the render report
    and never opened `slides/`. So a deck carrying the defect passes the production sweep
    whenever the direct pre-ship invocation is missed, which is the one place it matters.

    A review bot found it on the pull request that shipped the check. It is the same shape as
    `g_plan_render` twenty lines down and as GATE_LESSONS 79, written the same day: a rule
    enforced on one surface of a multi-surface product is a rule the product breaks on the
    other one. An adapter that silently covers less than the checker it names is worse than no
    adapter, because the registry says the gate ran.
    """
    import craft_floor as m
    rep = _load(d / "render_report.json")
    if not rep:
        return None
    fails, _warns, _meta = m.check(rep, _load(d / "machine_qa.json"))
    slides = d / "slides"
    if slides.is_dir():
        net, _n = m.network_calls(slides)
        fails = list(fails) + list(net)
    return fails


def g_plan_render(d: Path):
    """The claim-set comparison needs `copy.json` and the claim ids, and this passed neither.

    2026-09-07. The retro phase added the comparison to `plan_render_check` the same day, made
    its two new arguments optional so the three existing callers kept working, and left THIS
    caller, the one CI actually sweeps every shipped run with, passing the old three. So a
    future deck whose `copy.json` claim list drifts on a frame with no visible strip, or whose
    dossier names a claim that does not exist, passes the sweep. A review bot found it, and it
    is the same shape as the defect the comparison exists for: a surface that does not read the
    thing it is supposed to compare against.

    Both artifacts are loaded here and passed. A run missing either still gets the gate's own
    warning that it compared fewer surfaces than exist, which is why they are optional rather
    than required.
    """
    import plan_render_check as m
    sb, rep = d / "storyboard.md", _load(d / "render_report.json")
    if not (sb.exists() and rep):
        return None
    copy = _load(d / "copy.json")
    claims = _load(d / "claims.json") or {}
    ids = {c.get("id") for c in (claims.get("claims") or []) if isinstance(c, dict)} or None
    fails, _w, _s = m.check(sb.read_text(encoding="utf-8"), d / "slides", rep,
                            copy=copy or None, claim_ids=ids)
    return fails


def g_absences(d: Path):
    import absence_check as m
    copy = _load(d / "copy.json")
    if not copy:
        return None
    fails, _w, _s = m.check(copy, _load(d / "render_report.json"))
    return fails


def g_sources(d: Path):
    """check(run_dir) takes the directory itself. Caught by the same reachability assertion."""
    import sources_block as m
    if not ((d / "copy.json").exists() and (d / "first_comment.txt").exists()):
        return None
    return list(m.check(d) or [])


def g_nouns(d: Path):
    import noun_trace as m
    cp, cl = _load(d / "copy.json"), _load(d / "claims.json")
    if not (cp and cl):
        return None
    fails, _w, _s = m.check(cp, cl)
    return fails


def g_locators(d: Path):
    """A named place in a document, on a frame, against the claims that deck declared.

    Registered CURRENT for the reason written under `aggregates` below. Run into history it
    finds 2026-08-22's caption saying `Item 33` and 2026-08-27's sources block calling a Brazos
    County notice a `Section 312.207` notice, and both are real. Both are also published, and a
    gate written on 2026-08-28 turning two shipped decks red is how a suite teaches a run to
    scroll past it. They are notes, and the newest deck is fatal.
    """
    import locator_trace as m
    claims = _load(d / "claims.json")
    if not (claims and (d / "render_report.json").exists()):
        return None
    fails, _w, _s = m.check(m.frame_strings(d), claims)
    return fails


def g_numerals(d: Path):
    """A numeral on a frame, against the claims that frame cites.

    Registered CURRENT for the reason written under `aggregates` above, and the measurement is
    the argument. Run into history it finds fifteen across eight decks and every one is real:
    2026-08-22 prints PROJECT 58482 on three frames while fourteen claims carry that number and
    none of the three frames declares one of them, 2026-08-28 prints 265.5 MW citing five claims
    with the figure in a sixth, and 2026-08-28 prints 100 MW, which no claim in that run carries
    at all. They are also published, and a gate written on 2026-08-29 turning eight shipped decks
    red is how a suite teaches a run to scroll past it. Notes for those, fatal for the newest.
    """
    import numeral_trace as m
    cp, cl = _load(d / "copy.json"), _load(d / "claims.json")
    if not (cp and cl and (d / "render_report.json").exists()):
        return None
    probs, _stats = m.check(cp, _load(d / "render_report.json"), cl, _load(d / "aggregates.json"))
    return probs


_SCRIPT = re.compile(r"<script\b[^>]*>(.*?)</script\s*>", re.S | re.I)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
_JS_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def _display_source(body: str) -> str:
    """The text a frame's source can DISPLAY: its markup's text, then its scripts' code.

    A FRAME'S SCRIPT IS NOT MARKUP (2026-09-26, carousel no. 34). This used to be one tag strip,
    `<[^>]+>`, over the whole file. A frame that sets its labels from JavaScript carries both a
    `<` (a loop's `i < 4`) and a `>` (an arrow's `=>`), and the strip read everything between them
    as one tag and deleted it. Six labels on frames 8 and 9 that were plainly string literals in
    the source were reported missing, and CI went red on a correct deck.

    So a script's body is lifted out BEFORE the tag strip and kept whole, since its string
    literals are what the frame displays. Only its block comments are removed. HTML comments go
    too. Neither is displayed, and a comment quoting the copy of a deck that was replaced is exactly
    the stale artifact this gate exists to catch. `//` line comments are left alone, because
    stripping them by regular expression would cut every `https://` in a string, and a gate that
    mis-parses its own input invents failures (GATE_LESSONS 27).

    Every step before the old flattening is unchanged in order: tags out, THEN entities decoded,
    THEN whitespace collapsed, for the reason written in `g_shipped_fresh`.
    """
    scripts = [_JS_BLOCK_COMMENT.sub(" ", m.group(1)) for m in _SCRIPT.finditer(body)]
    markup = _HTML_COMMENT.sub(" ", _SCRIPT.sub(" ", body))
    text = html.unescape(re.sub(r"<[^>]+>", " ", markup))
    return re.sub(r"\s+", " ", text + " \n " + " \n ".join(scripts))


def g_shipped_fresh(d: Path):
    """Every artifact in a shipped run must describe the deck beside it.

    WHY THIS EXISTS. 2026-08-26, and it is the worst thing this suite has missed.

    The 2026-08-25 run recut its deck around a computed selection after a judge proved the old
    headline false. The renders, the copy and the caption were all rebuilt. `slides/` was not
    copied, and `assemble_report.json` was not rebuilt, so the shipped directory carried the
    REFUTED seven-body HTML and recorded its PDF as "Seven ways to slow a data center" while the
    PNGs beside them showed a different deck. A scoring judge found it and called it what it is:
    a refuted count and its numerals presented as verified in the deliverable a reader downloads.

    Every gate in this suite passed, because each reads ONE artifact and asks whether it is
    internally right. Not one asked whether the artifacts agree with each other.

    CONTENT, NOT TIMESTAMPS. The obvious version compares mtimes, and mtimes do not survive a
    clone, so it would pass on CI forever and only ever fire on the machine that already knew.
    These three comparisons hold in a fresh checkout:

      1. every display string `copy.json` records is in the slide source of the frame it names
      2. `assemble_report.json`'s title is `copy.json`'s `document_title`, CURRENT scope only
      3. `machine_qa.json` describes as many frames as the run shipped
    """
    cp = _load(d / "copy.json")
    if not cp:
        return None
    problems = []
    slides_dir = d / "slides"
    if slides_dir.is_dir():
        for key, blk in sorted((cp.get("slides") or {}).items()):
            n = blk.get("n") or int(str(key).lstrip("Ss") or 0)
            src = slides_dir / f"slide-{n:02d}.html"
            if not src.exists():
                problems.append(f"copy.json describes {key} and {src.name} is not in slides/")
                continue
            body = src.read_text(encoding="utf-8", errors="replace")
            # AN ENTITY IS MARKUP AND THE PROBE IS DISPLAY COPY. 2026-09-19.
            #
            # THE DEFECT. This flattened tags and collapsed whitespace and left the literal
            # `&nbsp;` standing in the text. Frame 3 of carousel no. 29 sets its letterhead as
            # `OFFICE OF THE TEXAS GOVERNOR &nbsp; SEPTEMBER 14TH, 2026`, `copy.json` records the
            # string a reader sees with one space, and the gate reported that the shipped source
            # was not the deck beside it. The source WAS the deck beside it. CI went red on a
            # correct artifact, which is the most expensive shape a gate failure takes, because
            # the obvious cure is to put markup into the copy record and that would make the
            # record describe the HTML rather than the page.
            #
            # This gate's own docstring says its subject is "every display string `copy.json`
            # records is in the slide source of the frame it names", and a display string is what
            # the browser renders. `&nbsp;`, `&amp;` and every numeric entity are the same trap,
            # so the fix is the general one rather than a special case for one entity.
            #
            # THE ORDER MATTERS AND GETTING IT BACKWARDS INVENTS TAGS. Unescaping BEFORE the tag
            # strip would turn an escaped `&lt;div&gt;` in visible copy into `<div>` and then
            # delete it, so a frame that legitimately displays angle brackets would lose them.
            # Decode AFTER the tags are gone and BEFORE the whitespace collapse: U+00A0 is matched
            # by `\s` in str mode, so the collapse does the rest.
            # 2026-09-26: scripts are lifted out before the strip. See `_display_source`.
            flat = _display_source(body)
            for want in (blk.get("strings") or []):
                probe = re.sub(r"\s+", " ", str(want)).strip()
                if len(probe) >= 12 and probe not in flat:
                    problems.append(
                        f"{src.name} does not carry the string copy.json says it prints: "
                        f"{probe[:70]!r}. The shipped source is not the deck beside it")
                    break
    # THE PLAN IS AN ARTIFACT TOO, and it is the one the first version of this gate missed.
    # Round 6's hard fail was that the shipped SOURCE did not draw the deck beside it. That was
    # repaired in slides/, the PDF and the assembly record, and round 7 found the superseded
    # deck had simply moved one file over: slide 2's dossier said "fourteen" four times over a
    # frame rendering fifteen, slide 3 declared span_days 154 against a printed 156, and slide 8
    # still called itself the deck's quietest in a frame whose own code comment quotes that
    # sentence and calls it wrong.
    #
    # Only the YAML dossier blocks are read. The revision log around them narrates what was
    # wrong on purpose, and a gate that could not tell a plan from a history of plans would
    # force a run to delete its own reasoning.
    sb = d / "storyboard.md"
    figs = _load(d / "computed.json") or {}
    if sb.exists() and figs:
        # THE ALLOWLIST READ ONE LEVEL AND EVERY computed.json IN THIS REPO NESTS. 2026-09-04.
        #
        # This was `{v for v in figs.values() if isinstance(v, int)}`, which reads the TOP LEVEL
        # of computed.json. Not one run has ever put a figure there. `compute.py` writes
        # `{"run": ..., "note": ..., "values": {"<name>": {"value": 5, ...}}}`, so the set this
        # gate built was empty on every deck but one, and on that one it was `{14}` because
        # 2026-09-03 happened to carry a top level `"deck": 14`. A gate whose allowlist is empty
        # refuses every word-number a dossier states, including the ones the run genuinely
        # computed, and a gate whose allowlist is one accidental integer is worse, because it
        # passes.
        #
        # It went unseen because it fails LOUD in one direction only. An empty allowlist makes
        # the gate stricter, so a run that hit it read a finding about its own prose and reworded
        # the prose, which cleared the finding and left the cause. That is GATE_LESSONS' own
        # recurring shape from the other side: not a green banner over a broken check, but a red
        # one that keeps being answered in the wrong place.
        #
        # So the values are walked wherever they sit. A float that is a whole number counts,
        # because `5.0` and `five` are the same figure and a dossier says the word.
        def _ints(node, acc):
            if isinstance(node, dict):
                for v in node.values():
                    _ints(v, acc)
            elif isinstance(node, list):
                for v in node:
                    _ints(v, acc)
            elif isinstance(node, bool):
                pass
            elif isinstance(node, int):
                acc.add(node)
            elif isinstance(node, float) and node.is_integer():
                acc.add(int(node))
            return acc

        allowed = _ints(figs, set())
        words = ("two three four five six seven eight nine ten eleven twelve thirteen fourteen "
                 "fifteen sixteen seventeen eighteen nineteen twenty").split()
        value_of = {w: i + 2 for i, w in enumerate(words)}
        text = sb.read_text(encoding="utf-8", errors="replace")
        # NARROWED to the fields where a dossier states the deck's CLAIMS. `job:` says what the
        # frame is for and `numerals:` says what it computes, and both were wrong. `bands:` and
        # `composition:` describe LAYOUT, where "two columns, eight then seven" and "the deck has
        # spent eight frames" are correct and have no business in a figures file. The first
        # version of this read the whole block and fired on both of those, which is a gate that
        # would teach a run to stop writing down how a frame is built.
        # THE THIRD ORIGIN, one layer up, and `aggregate_check` had already paid for this lesson
        # in its own file: a figure can be neither counted nor computed, it can be QUOTED. A
        # `numerals:` entry reads `value_from: c21  # 459, nearly 1.6 million, six months`, and
        # "six months" is c21's own wording, not something this run calculated. Refusing it says
        # the honest route fails, which is the exact shape aggregate_check fixed with
        # `quoted_from` and the exact thing that file warns the next gate author about.
        #
        # So a word-number clears if the CLAIMS THE SAME BLOCK CITES contain it in their own
        # words. That is narrower than "any claim", so a dossier cannot clear a stale figure by
        # citing something unrelated, and it is checked against the fetched text rather than
        # against prose nobody reads.
        cl = _load(d / "claims.json") or {}
        cl = cl.get("claims") if isinstance(cl, dict) else cl
        by = {c["id"]: (str(c.get("quote", "")) + " " + str(c.get("text", ""))).lower()
              for c in (cl or []) if isinstance(c, dict) and c.get("id")}
        claimy = []
        for blk in re.findall(r"```yaml\n(.*?)```", text, re.S):
            cites = set(re.findall(r"\bc\d+\b", blk))
            for fm in re.finditer(r"^(job|numerals):(.*?)(?=^\S|\Z)", blk, re.S | re.M):
                claimy.append((fm.group(0), cites))
        for blk, cites in claimy:
            said = " ".join(by.get(c, "") for c in cites)
            for m in re.finditer(r"\b(" + "|".join(words) + r")\b", blk, re.I):
                word = m.group(1).lower()
                if value_of[word] in allowed:
                    continue
                # Hyphenated in the source and spaced in the plan is the same figure.
                if re.search(rf"(?<![a-z]){word}[ -]", said):
                    continue
                problems.append(
                    f"storyboard.md, a dossier job or numerals field, says {m.group(1)!r} "
                    f"and the run computed {sorted(allowed)}, while none of the claims that "
                    f"block cites ({', '.join(sorted(cites)) or 'none'}) uses the word either. "
                    f"A plan nobody regenerates is a plan that describes the last deck")
                break

    ar = _load(d / "assemble_report.json")
    if ar and cp.get("document_title") and ar.get("title") != cp["document_title"]:
        problems.append(f"assemble_report.json titles the built PDF {ar.get('title')!r} and "
                        f"copy.json titles the deck {cp['document_title']!r}. The assembly on "
                        f"disk is not this deck's")
    qa = _load(d / "machine_qa.json")
    if qa:
        shipped = len([k for k in (cp.get("slides") or {})])
        seen = len(qa.get("slides") or qa.get("frames") or [])
        if seen and shipped and seen != shipped:
            problems.append(f"machine_qa.json describes {seen} frame(s) and the run shipped "
                            f"{shipped}. The QA report is not this render's")
    return problems


def g_measured(d: Path):
    """Every L* figure printed in the run's prose exists in its own measurements.json.

    THE HIGHEST RECURRENCE DEFECT IN THIS REPO, and it has now happened four times.

    Round 4 found frame 7's falloff committed twice with two values, 22.1 in the storyboard and
    17.2 in artwork.json. Round 7 found slide 6 printing 70.8 and 18.4 where measurements.json
    said 70.6 and 18.2. Round 8 recut three frames, moved six medians, and left the storyboard,
    the run record and the artwork ledger each carrying the previous deck's numbers. The writer
    that composes them from measurements.json existed the whole time and had gone silently dead,
    because it matched the OLD NUMBERS as literal strings.

    That is the shape CLAUDE.md names three separate times: a value with one home, surfaces that
    keep their own copy, and nothing in between checking they agree. A writer is not the check. A
    writer can stop firing. This ASKS, of the shipped bytes, and it cannot go quiet, because a
    figure that is absent from measurements.json is absent whatever wrote it.

    Scope is deliberately narrow and therefore certain: a number written next to the token `L*`.
    Every one of those is a luminance this run measured, so every one has to be in the file. A
    bare decimal elsewhere in the prose may be anything and is not this gate's business.
    """
    mp = d / "measurements.json"
    if not mp.exists():
        return None
    M = json.loads(mp.read_text(encoding="utf-8"))

    def walk(v):
        if isinstance(v, dict):
            for x in v.values():
                yield from walk(x)
        elif isinstance(v, list):
            for x in v:
                yield from walk(x)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            yield round(float(v), 1)

    known = set(walk(M))
    # A DELTA IS MEASURED TOO. The prose names junctions as positive drops, so both signs count,
    # and it names ranges, which are max minus min over the medians.
    known |= {abs(x) for x in known}
    med = M.get("per_frame_median_lstar") or []
    if med:
        known.add(round(max(med) - min(med), 1))
        known |= {round(abs(a - b), 1) for a in med for b in med}

    # `1.6 L*` style figures with one decimal, and integers written the same way.
    NUM = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d)?)\s*L\\?\*")
    out = []
    for name in ("storyboard.md", "RUN_RECORD.md"):
        f = d / name
        if not f.exists():
            continue
        for m in NUM.finditer(f.read_text(encoding="utf-8")):
            v = round(float(m.group(1)), 1)
            if v not in known:
                out.append(f"{name}: prints {m.group(1)} L* and measurements.json holds no such "
                           f"figure. Every luminance in this run's prose is written from that "
                           f"file by out/<date>/tmp/write_measured.py. A number here that is not "
                           f"there is a number somebody typed, or one a rewrite stopped reaching")
    return out


def g_ledgers(d: Path):
    """The variety ledgers, against the run whose figures their prose narrates.

    CURRENT scope, and the reason is in the gate itself: the three `*_recent` exclusion lists
    derive from the NEWEST entry and the topic prose is checked against that run's computed
    counts, so asking an older deck about today's ledger is asking the wrong question.

    This adapter is also the whole reason `ledger_check` is a gate rather than a script somebody
    remembers to run. `.github/workflows/**` and `prompts/**` are the human actor's, so a routine
    that writes a gate cannot connect it. One step in the workflow calls this file, so a new gate
    is one function away in a file the upgrade lane already owns. `port_audit`'s wiring check
    caught this one unconnected, which is exactly what that check exists for.
    """
    import ledger_check as m
    fp = d / "figures.json"
    led = REPO_ROOT / "ledger/carousel"
    if not (fp.exists() and (led / "captions.json").exists() and (led / "topics.json").exists()):
        return None
    return list(m.run(json.loads((led / "captions.json").read_text(encoding="utf-8")),
                      json.loads((led / "topics.json").read_text(encoding="utf-8")),
                      json.loads(fp.read_text(encoding="utf-8")),
                      (REPO_ROOT / m.DOCTRINE).read_text(encoding="utf-8")) or [])


# The gate did not exist when deck 13 was drawn, and deck 13 is what taught it. A gate that
# retroactively fails the work that motivated it is judging published work by a rule written
# after it, which this file's own `shipped fresh` comment already refuses two gates above.
CONSTRUCTION_SINCE = "2026-09-02"


def g_construction(d: Path):
    """How many frames trigger the bright-region proxy, measured on shipped images.

    See scripts/carousel/construction_check.py for what it measures and why bespoke_check, which
    was already green on the deck that produced this finding, could not see it: that file
    compares drawing CODE and a reader sees the drawn OBJECT.

    NOT APPLICABLE to any deck drawn on or before CONSTRUCTION_SINCE, which is the run that
    taught it. Every one of those is reported as a note instead, and the notes are worth reading:
    run into history this finds 4 of 8, 6 of 9 and 7 of 9 on three earlier decks, so a reviewer
    can still see where the proxy fires without treating it as object identity.
    """
    if d.name <= CONSTRUCTION_SINCE:
        return ("this gate was written during the " + CONSTRUCTION_SINCE + " run and that deck "
                "is what taught it. A gate does not judge the work that produced it")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "construction_check", Path(__file__).resolve().parent / "construction_check.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    code, problems, _rows = m.check(d)
    if code == 2:
        return None
    if code == getattr(m, "ADVISORY", 3):
        return [
            ADVISORY + p + " The detector measures connected bright-region fill, not object "
            "identity. On 2026-09-18 it classified a lit records-room wall and a car scene as "
            "document plates. Keep the measurement in the review record; leave the ship "
            "decision to bespoke_check and the panel."
            for p in problems
        ]
    return problems


# The illustration system, the layout keys in every dossier and the gate that reads them, were
# built during the 2026-09-11 run, and that deck was planned and drawn without any of it. Same
# reasoning as CONSTRUCTION_SINCE: a gate does not judge the work that produced it.
LAYOUT_SINCE = "2026-09-11"


def g_layout(d: Path):
    """Is there an image inside the rect the plan declared, and did the deck turn the page.

    See scripts/carousel/layout_check.py for the six measurements. The rotation and the rect are
    read off the dossiers, the detail and the silhouette are read off the shipped frames inside
    that rect, with the render report's text boxes masked out so a headline never counts as
    image, and the accent is counted at thumb scale.

    NOT `--require`. The routine runs the gate with that flag so a run that skipped planning its
    layouts fails. Here, on already published decks, a deck with no layout keys is one drawn
    before the system existed, and the gate's own scope rule reports that as a note and measures
    nothing.

    THE MEASUREMENT IS TAKEN BEFORE THE DATE IS CONSULTED, and that ordering is load bearing.
    `g_construction` returns before importing its gate on an old deck, which is fine there
    because its since-date is behind the newest deck. This gate's since-date IS the newest deck,
    so an early return would mean shipped_check's loop never loads `layout_check` on the one
    sweep `gate_wiring` grades, and the census would report a wired gate as an orphan. So the
    gate runs on every deck, and on a deck on or before LAYOUT_SINCE its findings are reported as
    a note rather than fatal. Nothing is hidden and nothing is judged by a rule newer than it.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "layout_check", Path(__file__).resolve().parent / "layout_check.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    code, problems, _rows = m.check(d)
    if code == 2:
        return None
    if d.name <= LAYOUT_SINCE and problems:
        return ("this gate was written during the " + LAYOUT_SINCE + " run and that deck was "
                "drawn without the illustration system. Run into it anyway it reports "
                f"{len(problems)} problem(s), first: {str(problems[0])[:150]}")
    return problems


# THE TWO GATES NOTHING EVER RAN, wired in 2026-09-03.
#
# `label_guard` and `quantifier_check` have existed for days, `gate_status` lists them, and
# neither was registered here or in guards.yml. So neither had ever run against a published deck,
# and when they were finally run by hand on 2026-09-03 BOTH were red on the shipped deck. That is
# this file's own founding lesson repeating: a checker wired to nothing certifies nothing, and an
# umbrella that says "every carousel gate" while omitting two of them is worse than no umbrella,
# because it turns unverified gates green.
LABEL_SINCE = "2026-09-02"
QUANTIFIER_SINCE = "2026-08-23"

# A FINDING IN ALREADY PUBLISHED COPY THAT NO ACTION CLEARS, named one by one, with the date and
# the reason. Same shape and same reasoning as `ledger_check.LIGHT_CAP_WAIVED`, and the same
# refusal: a waiver stops a finding BLOCKING and never stops it being measured or reported.
#
# The alternative was moving QUANTIFIER_SINCE forward to cover deck 14, and that is the move this
# file exists to refuse. A since-date says the gate was not wired when the deck shipped. Here the
# gate was wired that day, it went red on the deck's own frames, and the owner read both findings
# and said post as-is. Writing that down as "not applicable" would be the suite lying about what
# it saw, which is the whole GATE_LESSONS shape. So each finding is quoted, kept in the output,
# and carries who let it ship.
#
# Keyed by run date, then by a substring of the finding. Nothing matches by accident and a
# finding this table has never seen is fatal, which its self-test asserts.
QUANTIFIER_WAIVED = {
    "2026-09-03": {
        "slide-05.html asserts SOURCE SILENCE": (
            "Owner's instruction on 2026-09-03, given after being shown this exact sentence and "
            "the second finding below. Carousel no. 14 had already been rendered and posted when "
            "quantifier_check was first pointed at a slide, because `surfaces` read only "
            "`render/render_report.json` and a shipped deck archives it at the run root. The "
            "sentence is substantively true, the record does carry no source joining the two "
            "screening figures, and it is still the banned construction. Re-rendering a posted "
            "deck was declined. Recorded in the run record"),
        "slide-08.html prints the universal 'Not one of them'": (
            "Same instruction, same reason. This one cannot be cleared by declaring it either, "
            "because a declaration names the figures.json key the universal ranges over and this "
            "run computed no figure for institutions with a published researcher count. Writing "
            "a declaration against a key that does not measure the set would be a worse answer "
            "than carrying the finding"),
    },
}

# A DECK THAT MADE ITSELF UNCHECKABLE, named the same way and for the same reason. An absent
# label gate is a problem rather than a not-applicable, so the ordinary answer is that the sweep
# goes red until the run archives its frames. That answer needs the frames to still exist.
LABEL_ABSENT_WAIVED = {
    "2026-09-03": (
        "Carousel no. 14 was rendered and posted from a container that has since been reclaimed, "
        "and `out/` is gitignored, so `out/2026-09-03/slides/` no longer exists anywhere. The "
        "artifact cannot be archived after the fact and there is no action left that clears this. "
        "The cause is the ship step naming only NEXT_RUN.md where it says copy artifacts, written "
        "up as a proposal in knowledge/carousel/UPGRADE_BACKLOG.md because prompts/ is human lane. "
        "This waiver covers ONE date. Deck 15 shipping without its frames is fatal"),
}

# A finding that is measured, reported and not fatal. `check_run` routes on this prefix, so any
# gate can use it and none of them can hide a finding to do so.
WAIVED = "[waived] "
ADVISORY = "[advisory] "


def _by_module(name: str, d: Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parent / (name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def g_labels(d: Path):
    """Every label a frame prints beside a claim id is words that claim says.

    NOT APPLICABLE on or before LABEL_SINCE, and that date is a LIMITATION rather than politeness
    to old work. This gate reads the capitalised words before an id as a label, which is right for
    a deck that sets discrete labels and wrong for one that sets a whole dek in capitals. Six
    published decks do the latter, so run into history it reports WAS, RATHER and THAN as
    unsupported labels, which is the false positive mode `label_guard` refuses to have.

    Narrowing the heuristic so a caps SENTENCE is not read as a caps LABEL is the fix, and it is
    a design change rather than a wiring one. Until it lands this binds forward only, and the
    older decks are reported as notes so the limitation stays visible rather than forgotten.
    """
    if d.name <= LABEL_SINCE:
        return ("this gate reads capitalised words before a claim id as a label, and this deck "
                "sets running prose in capitals, so it would report sentence words as labels")
    # `audit`, NOT `check`. `check` is the label test alone, and the two states where the gate
    # could not run were decided afterwards by the CLI. This adapter called `check`, so a deck
    # that archived no slide HTML came back as an empty list and was swept up as a PASS while the
    # gate's own CLI reported exit 2 on it. One gate answering two ways depending on who asked.
    m = _by_module("label_guard", d)
    try:
        return m.audit(d)[1]
    except m.Absent as a:
        # AN ABSENT GATE ON A DECK THIS GATE COVERS IS A PROBLEM, NOT A NOT-APPLICABLE, and the
        # first attempt at this fix returned a string here. `check_run` reads any string as "not
        # applicable" whatever the gate's scope, so the sweep still exited 0 and still printed
        # "every applicable gate clean" over a deck whose label gate had not run. That is the same
        # defect as the PASS it replaced, said out loud instead of silently. Review caught it.
        #
        # A deck after LABEL_SINCE that archived no slide HTML did not fail this gate, it made
        # itself uncheckable, and the fix is in the ship step rather than here. So it is a
        # PROBLEM, the scope machinery makes it fatal on the newest deck and a note on an older
        # one, and the next run archiving its frames clears it.
        why = LABEL_ABSENT_WAIVED.get(d.name)
        line = f"the label gate could not run on this deck: {a}"
        return [f"{WAIVED}{line}  WAIVED. {why}" if why else line]


def g_quantifiers(d: Path):
    """A universal over a set names the set it ranges over.

    NOT APPLICABLE on or before QUANTIFIER_SINCE. Run into history this is clean on thirteen of
    fourteen earlier decks, and the one it catches, 2026-08-23, is a genuine undeclared universal
    in already published copy that cannot now be cleared, because a run's `quantifiers.json` is
    written by the run. A gate that is permanently red with no action that clears it is a gate
    somebody switches off, which is the call `ledger_check` and this file already make twice.
    """
    if d.name <= QUANTIFIER_SINCE:
        return ("this gate was not wired when the deck shipped and its declaration file is "
                "written by the run, so a finding here can never be cleared")
    probs = _by_module("quantifier_check", d).check(d)
    # THE WAIVER DOES NOT SOFTEN THE MEASUREMENT. Every finding is still computed and still
    # reported under the date that carries it. What a named waiver changes is only whether an
    # already published surface BLOCKS this sweep, and only for a date and a phrase somebody
    # named on the record. A finding this file has never seen is not covered by one.
    waived = QUANTIFIER_WAIVED.get(d.name) or {}
    out = []
    for p in probs:
        why = next((w for phrase, w in waived.items() if phrase in p), None)
        out.append(p if why is None else f"{WAIVED}{p}  WAIVED. {why}")
    return out


# THE CHASSIS AND THE COHERENCE GATES ARRIVED ON 2026-09-16 and no deck on or before that date
# has a chassis, because the system did not exist. Same reasoning as CONSTRUCTION_SINCE and
# LAYOUT_SINCE, stated for the third time because it keeps being the right answer: a gate does
# not judge the work that produced it.
DECK_SINCE = "2026-09-16"
# One rule inside that gate is newer than the gate. See `g_deck_chassis` for why it gets its own
# date rather than moving DECK_SINCE, which would take three older rules down with it.
RESERVE_SINCE = "2026-09-17"


def g_deck_chassis(d: Path):
    """The nine frames were cut from one piece of stock.

    REGISTERED BECAUSE CI WAS ONLY EXERCISING THE FIXTURE (2026-09-16, review). `guards.yml` ran
    this gate's self-test and ran it against `examples/lamp-deck/`, which is a deck that cannot
    change. Neither asked it about the deck a run had just shipped, so a run that skipped or
    misapplied its Phase 11 commands could ship a chassis-less deck and CI would still report
    green, on the strength of a fixture and an example. That is `gate_wiring.py`'s own finding
    in a new place: a gate nothing points at the real subject of.
    """
    if d.name <= DECK_SINCE:
        return ("the chassis system did not exist when this deck shipped, so it loads no "
                "chassis and could not have")
    sd = d / "slides"
    if not sd.is_dir() or not sorted(sd.glob("slide-*.html")):
        return None
    probs = _by_module("deck_chassis", d).check_deck(sd)
    # THE RESERVE ORDER RULE WAS ADDED DURING THE 2026-09-17 RUN, out of that deck's own frame 9,
    # and that frame had shipped by the time the rule existed. Only the findings that rule makes
    # are demoted, and only on that deck: a since-date on the whole gate would have taken the
    # chassis, finish and plate rules down with it. The finding is still MEASURED and still
    # PRINTED, which is the difference between a carve-out and a switched-off check.
    if d.name <= RESERVE_SINCE:
        held = [p for p in probs if "Position, then measure" in p]
        probs = [p for p in probs if "Position, then measure" not in p]
        if held and not probs:
            return (f"the type reserve ordering rule was added on {RESERVE_SINCE} out of this "
                    f"deck's own frame 9 and this deck was drawn before it. Run into it anyway "
                    f"it reports {len(held)} finding(s), first: {str(held[0])[:180]}")
    return probs


def g_deck_coherence(d: Path):
    """The rendered frames read as one deck rather than nine pictures."""
    if d.name <= DECK_SINCE:
        return ("the coherence thresholds were derived on " + DECK_SINCE + " and every deck on "
                "or before it strobes by them, which is the finding rather than a fault to fix "
                "in published work")
    m = _by_module("deck_coherence", d)
    if not m.frames_in(d):
        return None
    got = m.measure(d, d / "storyboard.md")
    if "error" in got:
        return [got["error"]]
    return list(got.get("problems") or [])


YEAR_SINCE = "2026-09-22"   # the newest deck shipped before the check was wired
def g_print_ban(d: Path):
    """The print screen is deleted, and a shipped deck may not carry it or fall short of the render.

    Owner, 2026-09-23: "delete that fallback bullshit look, make it impossible for me to have to
    tell u this again." `print_ban.check_run` refuses a printed frame and counts rendered ones.

    Its own since-date, for the reason stated at RESERVE_SINCE: every deck on or before
    PRINT_SINCE was drawn under a routine that ORDERED the print, in so many words, and pointed
    every director at an example built on it. They are the decks that produced this rule and a
    gate does not judge the work that produced it. They are still measured and printed, which is
    the difference between a carve-out and a switched-off check. From the day after, a printed
    deck is red here, in CI, on every build.
    """
    import print_ban as m
    if not (d / "slides").is_dir():
        return None
    probs = m.check_run(d)
    if probs and d.name <= m.PRINT_SINCE:
        return (f"the print screen was deleted on 2026-09-23 and this deck was drawn under a "
                f"routine that ordered it. Run into it anyway it reports {len(probs)} finding(s), "
                f"first: {str(probs[0])[:160]}")
    return probs


FIGURE_SINCE = "2026-09-20"


def g_figure_bearing(d: Path):
    """The frames draw the story's own computed numbers rather than a scene beside them.

    Its own since-date rather than DECK_SINCE, and for the reason stated at RESERVE_SINCE: this
    rule is newer than the chassis system and folding it into that date would retroactively fail
    four decks on a law that did not exist when they were drawn. They are the decks that produced
    the law. A gate does not judge the work that produced it.

    They ARE still measured and printed, because the difference between a carve-out and a
    switched-off check is whether the finding is visible.
    """
    board = d / "storyboard.md"
    if not board.exists():
        return None
    m = _by_module("figure_bearing", d)
    import dossier_check as _dc
    dossiers = _dc.parse_dossiers(board.read_text(encoding="utf-8"))
    if not dossiers:
        return None
    probs = m.check(dossiers, m.computed_keys(d),
                    int(m.load_config()["min_figure_bearing_frames"]),
                    (d / "slides") if (d / "slides").is_dir() else None,
                    m.figure_values(d))
    if d.name <= FIGURE_SINCE:
        if probs:
            return (f"THE ARTWORK CARRIES THE DATA was written on {FIGURE_SINCE} out of this "
                    f"deck and the three before it, and they were drawn before it existed. Run "
                    f"into it anyway it reports: {str(probs[0])[:200]}")
        return None
    return probs


DEPTH_SINCE = "2026-09-20"


def g_depth_floor(d: Path):
    """The frames stand on the scene bench rather than in screen pixels.

    Its own since-date, for the reason stated at RESERVE_SINCE and FIGURE_SINCE: this rule is
    newer than every deck under it and a gate does not judge the work that produced it. The
    finding is still measured and still printed.
    """
    sd = d / "slides"
    if not sd.is_dir() or not sorted(sd.glob("slide-*.html")):
        return None
    m = _by_module("depth_floor", d)
    probs = m.check(m.frames_in(sd), m.load_config(), m.deck_light_of(sd))
    if d.name <= DEPTH_SINCE:
        if probs:
            return (f"THE FRAME STANDS IN A PLACE was written on {DEPTH_SINCE} out of this deck "
                    f"and the 26 before it. Run into it anyway it reports: {str(probs[0])[:200]}")
        return None
    return probs


def g_completion(d: Path):
    """`check(run_dir, bar, cap)`, and the cap is the whole point of the third argument.

    This called `check(d, m.threshold())` and let `cap` default to None, which makes the ONE
    path in run_complete that is under the bar and not a failure unreachable from here. A deck
    shipped on the round cap with no hard fail, exactly what the rubric licenses and what
    run_complete's own CLI passes the cap to allow, was reported by this gate as never having
    shipped. Two gates reading one rubric and disagreeing about it, because one of them was
    only asking half the question.

    GATE_LESSONS' recurring shape, from the other side: not a green banner measuring something
    narrower than it claimed, but a red one. The verdict was still wrong for the same reason.

    AND THE BAR IS THE ONE THE DECK WAS SCORED AGAINST, not the one in the rubric today.

    On 2026-09-13 the owner lowered the threshold from 6.8 to 6.7. Two decks that had been HELD
    under the old bar, no. 14 at 6.762 and 2026-09-09 at 6.714, immediately went red here, because
    this gate read today's rubric and found `ship: false` sitting beside a number that now clears
    it. Neither deck changed. Neither run did anything wrong. A number this project chose to move
    had reached back and reclassified history.

    That is the same fault this file already refuses everywhere else, and the notes above say so in
    as many words: a gate does not judge the work that produced it, and an older deck is not
    answerable to a rule written after it. `score.json` records the `threshold` it was judged
    against, so the honest question is whether each deck met ITS bar. That is also the STRICTER
    reading. A deck held at 6.8 stays held at 6.8 forever, and lowering the bar cannot launder it
    into a deck that shipped.

    The live run is a different question and `run_complete --date` still answers it from the
    rubric, because a deck being scored today is answerable to today's bar.
    """
    import run_complete as m
    p = d / "score.json"
    if not p.exists():
        return None
    try:
        bar = json.loads(p.read_text(encoding="utf-8")).get("threshold")
    except json.JSONDecodeError:
        bar = None
    if not isinstance(bar, (int, float)) or isinstance(bar, bool):
        bar = m.bar_in_force(d.name)  # a deck that recorded no bar answers to the one that applied
    return list(m.check(d, float(bar), m.max_rounds()) or [])


# The bar a deck answers to now lives in `run_complete.BAR_HISTORY`, because the site builder
# needs the same answer and two copies of a rule about history is how history gets two versions.


def g_verbatim(d: Path):
    """Every fragment a frame sets as a source's own words, against the claim it names.

    REGISTERED ON 2026-09-10, AND THE REASON IS THE POINT. `verbatim_check` was the one file in
    scripts/carousel that nothing in this repository ran: absent from `guards.yml`, absent from
    every phase of the routine, absent from this registry. Its own `--self-test` had been red on
    a clean checkout of main for days, over an assertion pinned to "the newest shipped deck",
    and nothing found out because nothing opened the file. `gate_wiring.py` is the census that
    now refuses that state, and this entry is what clears it.

    THE DECLARED HALF ONLY. The discovery half warns by design, because a machine cannot tell an
    authored label from a paraphrase, and a warning is not a finding a sweep over already
    published work can act on.

    HISTORY rather than CURRENT, which is safe for the reason the gate's own self-test asserts
    deck by deck across all twenty: the declared half fires only on a dossier that DECLARES a
    fragment, so a deck drawn before `SLIDE_DOSSIER_SPEC.md` grew its `verbatim:` key declares
    none and is clean rather than retroactively judged.
    """
    import verbatim_check as m
    sb, cj, rp = d / "storyboard.md", d / "claims.json", d / "render_report.json"
    if not (sb.exists() and cj.exists() and rp.exists()):
        return None
    dossiers = m.parse_dossiers(sb.read_text(encoding="utf-8"))
    if not dossiers:
        return None
    claims = json.loads(cj.read_text(encoding="utf-8")).get("claims") or []
    fails, _declared, _slides = m.check_declared(
        dossiers, claims, json.loads(rp.read_text(encoding="utf-8")))
    return list(fails)


def g_contacts(d: Path):
    """Every published email address, host and telephone number, against this run's claims.

    HISTORY, and the measurement that earns it is in the gate's own docstring: across all 23
    shipped decks carrying a claims file and a published surface, the only contact tokens on any
    of them are this site's own host and its own item pages. A gate that returns nothing on
    twenty three decks of correct work is judging a rule those decks already kept, which is the
    test HISTORY has to pass and most gates here cannot.

    It returns None for a deck that archived no render report and no copy.json, which is three of
    them, and the sweep reports that as not applicable rather than as clean.
    """
    import contact_trace as m
    return m.problems(d)


def g_scene_bounds(d: Path):
    """Every figure the plan placed, against the frame its own camera puts it in.

    REGISTERED THE DAY THE GATE WAS WRITTEN, 2026-09-14, and this registry is the only route it
    has. `guards.yml` and `prompts/daily_routine.md` are both `human` lane, so the actor that
    writes a carousel gate is structurally unable to wire one anywhere else, which is the whole
    argument in `gate_wiring.py`'s header.

    THE FATAL HALF ONLY. `scene_bounds.problems()` returns the outside-the-frame findings and
    not the acceptance-band report, which compares a computed number to a sentence and prints
    rather than decides. A sweep over already published work can act on the first and not on the
    second.

    HISTORY rather than CURRENT, and it is the rare gate that earns it. The rule here is not one
    this project invented and later changed: it is `TXSCENE.project`, the engine's own
    arithmetic, pinned by this gate's self-test against `assets/js/txscene.js`. A deck drawn
    before the gate existed is judged by exactly the projection it was drawn with. Decks with no
    TXFIG figure in them return nothing, which is most of the corpus and is honest rather than
    lucky.
    """
    import scene_bounds as m
    return m.problems(d)


# `bleed_witness` was written during the 2026-09-17 run, out of that deck's own panel findings,
# and that deck was drawn without it. Same carve-out and same reasoning as LAYOUT_SINCE.
BLEED_SINCE = "2026-09-17"


def g_bleed_witness(d: Path):
    """Does the frame DRAW the bleed its dossier declares, read out of the slide's own source.

    REGISTERED THE DAY THE GATE WAS WRITTEN, 2026-09-17, and this registry is its only route to
    CI. See `gate_wiring.py`'s header for why: the actor that writes a carousel gate owns neither
    `guards.yml` nor `prompts/daily_routine.md`. The live-run route is `panel_ready.py`, which
    this lane also owns and which the routine runs before it spawns a panel.

    THE MEASUREMENT IS TAKEN BEFORE THE DATE IS CONSULTED, for the reason `g_layout` states one
    screen up: this gate's since-date IS the newest deck, so an early return would leave the
    module unloaded on the one sweep `gate_wiring` grades and the census would call a wired gate
    an orphan.

    CURRENT with a since-date, rather than HISTORY. Run back over the corpus the gate is clean on
    all 27 decks before no. 27, which is the honest result and not a waiver: the four findings it
    has are all on the deck that produced it. Those are reported as a note here because that deck
    had already shipped when the gate existed, and everything after it is fatal.
    """
    import bleed_witness as m
    probs = m.problems(d)
    if probs is None:
        return None
    if d.name <= BLEED_SINCE and probs:
        return (f"this gate was written during the {BLEED_SINCE} run out of that deck's own "
                f"panel findings, and that deck was drawn without it. Run into it anyway it "
                f"reports {len(probs)} frame(s) declaring a bleed the drawing does not make, "
                f"first: {str(probs[0])[:180]}")
    return probs


# THE CRAWL BOUNDARY, WIRED HERE ON 2026-09-19 BECAUSE THE LANE THAT WROTE IT CANNOT WIRE IT.
#
# `scripts/shared/crawl_boundary.py` reads this project's disallow list out of
# `SOURCES_REGISTRY.md`, which is `human` owned on purpose: an unattended run that can edit its own
# boundary does not have one. It was written after a run's own research helper carried the boundary
# as a tuple of HOSTS and fetched a `capitol.texas.gov/TLODOCS/` url, which is a disallowed PATH on
# an allowed host.
#
# WHAT THIS ADAPTER ASKS, AND IT IS A QUESTION ABOUT PUBLISHED WORK RATHER THAN ABOUT THE PARSER.
# Every claim a shipped deck stands on names a url. A deck citing a url inside the boundary has
# published evidence this project said it would not fetch, which is a promise broken on the one
# surface a sceptic checks. That is exactly the kind of fact this file exists to find, and nothing
# else in the suite could see it: `claims_check` proves a claim is fetched and quoted and has no
# opinion about where from.
#
# AND IT IS ALSO THE WIRING. `gate_wiring` accepts three routes and the only one inside this lane
# is a registry entry here, so a gate the upgrade actor writes is otherwise structurally unable to
# be connected. The alternative was an import for its own sake, which is the mention-is-not-a-
# reference fault GATE_LESSONS 14 is about, wearing the fix's clothes.
#
# A PARSE THAT CANNOT RUN IS A FAILURE, NEVER AN EMPTY BOUNDARY. `rules()` raises rather than
# returning a short list, and that exception is allowed to reach the sweep's `could not run` note
# rather than being swallowed into a clean result.
#
# CURRENT SCOPE, AND THE THREE DECKS IT HOLDS BACK ARE A REAL FINDING RATHER THAN A WAIVER.
# Measured 2026-09-19 over every shipped deck: 2026-08-16 cites `lrl.texas.gov` on c28, c29 and
# c31, and 2026-08-21 cites it on c3 through c8, both BEFORE that host was decided off limits on
# August 25th. 2026-09-07 cites `docs.tacc.utexas.edu` on eighteen claims, which is a SUBDOMAIN of
# the host the registry names, and whether the registry's domain-wide statement reaches a
# subdomain with its own robots.txt is a question for the maintainer who owns that file rather
# than for this lane. All three are printed as notes under their own dates, so nothing is hidden,
# and none of them can be repaired from here: those artifacts are published and `daily` owned.
def g_crawl_boundary(d: Path):
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "shared"))
    import crawl_boundary as m
    raw = _load(d / "claims.json")
    rows = raw.get("claims") if isinstance(raw, dict) else raw
    if not isinstance(rows, list) or not rows:
        return None
    b = m.rules()
    out, seen = [], set()
    for c in rows:
        if not isinstance(c, dict):
            continue
        url = str(c.get("source_url") or c.get("url") or "")
        why = m.forbidden(url, b) if url else None
        if why and url not in seen:
            seen.add(url)
            out.append(f"{c.get('id', '?')} cites {url[:90]}, and {why[:150]}")
    return out


GATES = [
    ("copy sync", g_copy_sync, HISTORY),
    ("crawl boundary", g_crawl_boundary, CURRENT),
    ("quotations", g_quotations, HISTORY),
    # CURRENT, not HISTORY, and the reason is the lesson this whole file is built on.
    # aggregate_check gained the `quoted_from` route AFTER 2026-08-18 shipped. That deck
    # declared five quoted figures through `computed_by` because it was the only route that
    # existed, and today's gate calls that wrong. The deck did not change. The ruler did, which
    # is exactly what happened when the render window went 80 to 320 and turned an untouched
    # 2026-08-16 deck red. Judging published work by a rule written after it is how a suite
    # teaches people to ignore it.
    ("aggregates", g_aggregates, CURRENT),
    ("dossiers", g_dossiers, CURRENT),
    ("coherence", g_coherence, CURRENT),
    ("craft floor", g_craft_floor, CURRENT),
    ("deck chassis", g_deck_chassis, CURRENT),
    ("deck coherence", g_deck_coherence, CURRENT),
    ("print ban", g_print_ban, CURRENT),
    ("figure bearing", g_figure_bearing, CURRENT),
    ("depth floor", g_depth_floor, CURRENT),
    ("plan vs render", g_plan_render, CURRENT),
    ("absences", g_absences, HISTORY),
    ("nouns", g_nouns, HISTORY),
    ("locators", g_locators, CURRENT),
    ("numerals", g_numerals, CURRENT),
    ("sources block", g_sources, HISTORY),
    ("labels", g_labels, CURRENT),
    ("quantifiers", g_quantifiers, CURRENT),
    # CURRENT, for the reason already written above about `aggregates`. Run into history this
    # finds 2026-08-19, whose assemble_report titles the PDF "Texas AI Docket, August 19th 2026"
    # where copy.json titles the deck "Batch Zero, and the calendar with a hole in it". That is a
    # CONVENTION that changed, not a stale artifact, and judging published work by a rule written
    # after it is how a suite teaches a run to ignore it. The defect this exists for is a run
    # shipping artifacts that describe a deck it already replaced, which is a property of the
    # deck being made now.
    ("shipped fresh", g_shipped_fresh, CURRENT),
    # CURRENT: measurements.json is written per run, and a deck shipped before this
    # writer existed has no file for the gate to ask.
    ("measured figures", g_measured, CURRENT),
    ("ledgers", g_ledgers, CURRENT),
    ("verbatim", g_verbatim, HISTORY),
    # CURRENT, because it is a property of the deck being made now and because every deck older
    # than it was drawn without it. See its own docstring for why bespoke_check, which was
    # already green, could not see this: that file compares drawing CODE and a reader sees the
    # drawn OBJECT.
    ("construction", g_construction, CURRENT),
    # CURRENT, and for the same reason as construction one line up: every deck older than the
    # illustration system was drawn without a layout to hold it to, and the gate's own scope
    # rule already measures nothing on those. What this scope protects is the deck being made
    # now, which is the one that can still be redrawn.
    ("layout", g_layout, CURRENT),
    # CURRENT, and it is the other half of the `layout` line above. That gate measures a declared
    # bleed against the declared rect, both typed into the same yaml block, and this one measures
    # it against the geometry the slide actually draws.
    ("bleed witness", g_bleed_witness, CURRENT),
    ("completion", g_completion, HISTORY),
    ("scene bounds", g_scene_bounds, HISTORY),
    ("contacts", g_contacts, HISTORY),
]


def shipped_runs() -> list:
    return sorted([p for p in RUNS.glob("2*") if (p / "copy.json").exists()]) if RUNS.exists() else []


def check_run(d: Path, newest: bool) -> tuple:
    """Returns (fatal, notes). Each is a list of strings."""
    fatal, notes = [], []
    for name, fn, scope in GATES:
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                probs = fn(d)
        except Exception as exc:                       # noqa: BLE001
            notes.append(f"{d.name}  {name}: could not run ({type(exc).__name__}: {exc})")
            continue
        if probs is None:
            notes.append(f"{d.name}  {name}: not applicable, the artifact it reads is absent")
            continue
        if isinstance(probs, str):
            # A GATE RETURNING A STRING says "not applicable, and here is the real reason". The
            # only reason on offer used to be a missing artifact, so a gate that simply postdates
            # the deck reported one that was sitting right there. A note giving the wrong reason
            # is the defect this whole file exists to catch, in the file itself.
            notes.append(f"{d.name}  {name}: not applicable, {probs}")
            continue
        # AN ADVISORY IS A MEASUREMENT, NOT A WAIVER. It stays visible and never enters the fatal
        # list. Construction uses this route because its pixel segmentation can measure a bright
        # bounding-box fill but cannot establish that two scenes depict the same object.
        for p in [str(x) for x in probs if str(x).startswith(ADVISORY)]:
            notes.append(f"{d.name}  {name}: ADVISORY. {p[len(ADVISORY):]}")
        probs = [x for x in probs if not str(x).startswith(ADVISORY)]

        # A WAIVED FINDING IS SPLIT OUT HERE RATHER THAN DROPPED BY THE GATE. It is reported on
        # its own line, in full, under the date that carries it, so the sweep's output still
        # contains every finding it made. Only the fatal list is shorter.
        for p in [str(x) for x in probs if str(x).startswith(WAIVED)]:
            notes.append(f"{d.name}  {name}: {p[len(WAIVED):]}")
        probs = [x for x in probs if not str(x).startswith(WAIVED)]
        if not probs:
            continue
        head = str(probs[0])[:150]
        line = f"{d.name}  {name}: {len(probs)} problem(s). First: {head}"
        if scope == HISTORY or newest:
            fatal.append(line)
        else:
            notes.append(line + "   [older deck, gate is newer than it]")
    return fatal, notes


def run(only: str | None = None) -> int:
    runs = shipped_runs()
    if only:
        runs = [p for p in runs if p.name == only]
        if not runs:
            print(f"shipped_check: no shipped run named {only}", file=sys.stderr)
            return 1
    if not runs:
        print("shipped_check: no shipped runs to check")
        return 0
    newest = shipped_runs()[-1].name
    fatal, notes = [], []

    # THE IMPORT SPY, and it is here rather than in `gate_wiring` because this loop is the only
    # place the measurement exists. `gate_wiring` asks whether every carousel gate is run by
    # something, and one of the three answers it accepts is "this registry loaded it". That
    # answer is MEASURED, not grepped, because a mention is not a reference and
    # GATE_LESSONS entry 14 ("A self-test is not wiring") is the record of what counting a
    # mention bought: every gate satisfied `port_audit` permanently off its own
    # `--self-test` line.
    #
    # Two routes into this suite and both are watched. An ordinary `import` lands in
    # `sys.modules`. `spec_from_file_location` does not, and that is how `g_construction` loads
    # its gate, so a spy watching only the first would have called `construction_check` unwired
    # and been wrong about one of the two gates the census was written for.
    before, spec_seen = set(sys.modules), set()
    _original = importlib.util.module_from_spec

    def _spy(spec):
        spec_seen.add(spec.name)
        return _original(spec)

    importlib.util.module_from_spec = _spy
    try:
        for d in runs:
            f, n = check_run(d, d.name == newest)
            fatal += f
            notes += n
    finally:
        importlib.util.module_from_spec = _original

    # THE CENSUS IS GRADED ONLY WHEN THE SWEEP COVERED THE NEWEST DECK, and this is a real
    # condition rather than a convenience. A gate that does not apply to an older deck returns
    # before it imports anything, so a narrowed sweep genuinely loads less and would report
    # gates as unwired that are wired. A skip that means "not covered at all" belongs in the
    # failure list and not in a note, so this one says which it is out loud.
    if only in (None, newest):
        import gate_wiring as _gw
        loaded = ((set(sys.modules) - before) | spec_seen) & set(_gw.gates())
        fatal += [f"gate wiring: {p}" for p in _gw.check(loaded)]
    else:
        notes.append(f"gate wiring: NOT TAKEN. --run {only} is a narrowed sweep and a gate that "
                     f"does not apply to that deck never loads, so the census would be wrong "
                     f"rather than merely absent. Run with no --run to take it")

    for n in notes:
        print(f"  note  {n}")
    if fatal:
        print(f"\nshipped_check: {len(fatal)} problem(s) in work that is already published\n",
              file=sys.stderr)
        for f in fatal:
            print(f"  - {f}", file=sys.stderr)
        return 1
    # THE CLOSING LINE NAMES ADVISORIES AND WAIVERS. "Every applicable gate clean" over either
    # would be the narrow-measurement sentence this file exists to catch, in this file.
    n_advisory = sum(1 for n in notes if "ADVISORY." in n)
    n_waived = sum(1 for n in notes if "WAIVED." in n)
    suffix = []
    if n_advisory:
        suffix.append(f"{n_advisory} advisory finding(s) reported above and not fatal")
    if n_waived:
        suffix.append(f"{n_waived} named waiver(s) reported above and not fatal")
    print(f"shipped_check: {len(runs)} shipped run(s), no fatal finding on the artifacts as "
          f"committed" + (", with " + "; ".join(suffix) if suffix else ""))
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    ok("there are shipped runs to check at all", bool(shipped_runs()),
       "runs/carousel carries no run with a copy.json, so this gate is inert")

    # A DECK ANSWERS TO THE BAR IT WAS SCORED AGAINST. Replays 2026-09-13, when the threshold
    # moved 6.8 to 6.7 and two decks HELD under the old bar went red here without changing.
    import json as _json
    import tempfile as _tempfile
    with _tempfile.TemporaryDirectory() as _t:
        _d = Path(_t) / "2026-09-03"
        _d.mkdir()
        held = {"weighted_score": 6.762, "threshold": 6.8, "ship": False,
                "hard_fails": [], "rounds": 5}
        (_d / "score.json").write_text(_json.dumps(held), encoding="utf-8")
        ok("a deck held at its own 6.8 bar stays held after the bar moves to 6.7",
           not g_completion(_d),
           f"reported {g_completion(_d)}, so lowering the rubric laundered a held deck")

        # and the bar it records is not a way to escape a verdict either
        (_d / "score.json").write_text(_json.dumps({**held, "weighted_score": 6.0, "rounds": 1}),
                                       encoding="utf-8")
        ok("a deck under its own bar and under the cap still fails", bool(g_completion(_d)),
           "a recorded threshold must not excuse a deck that simply did not finish")

        # a deck that records no threshold answers to the current rubric
        (_d / "score.json").write_text(
            _json.dumps({"weighted_score": 6.0, "ship": False, "hard_fails": [], "rounds": 1}),
            encoding="utf-8")
        ok("a deck recording no threshold falls back to the rubric", bool(g_completion(_d)),
           "an absent threshold must not read as no bar at all")

    # ---- AN ENTITY IS MARKUP, AND THE DECODE MAY NOT BECOME A WAY TO PASS. 2026-09-19 --------
    #
    # The real artifact, replayed: frame 3 of carousel no. 29 sets its letterhead with `&nbsp;`
    # between the two halves and `copy.json` records the string a reader sees. The gate reported
    # that the shipped source was not the deck beside it and CI went red on a correct artifact.
    #
    # The adversarial half is the one that matters. A decode that quietly widened the comparison
    # would be a loosening, so the case below proves a string the frame genuinely does NOT carry
    # still fails, with the SAME entity sitting in the same place. Delete the `html.unescape` call
    # in `g_shipped_fresh` and the first assertion goes red; delete the substring test instead of
    # decoding and the second one does.
    with _tempfile.TemporaryDirectory() as _t:
        _d = Path(_t) / "2026-09-19"
        (_d / "slides").mkdir(parents=True)
        (_d / "copy.json").write_text(_json.dumps({"slides": {"S3": {
            "n": 3, "strings": ["OFFICE OF THE TEXAS GOVERNOR SEPTEMBER 14TH, 2026"]}}}),
            encoding="utf-8")
        (_d / "slides" / "slide-03.html").write_text(
            '<p class="sheethead">OFFICE OF THE TEXAS GOVERNOR &nbsp; SEPTEMBER 14TH, 2026</p>',
            encoding="utf-8")
        ok("a display string the frame prints through `&nbsp;` is found, not reported missing",
           not g_shipped_fresh(_d), str(g_shipped_fresh(_d)))
        (_d / "slides" / "slide-03.html").write_text(
            '<p class="sheethead">OFFICE OF THE TEXAS GOVERNOR &nbsp; SEPTEMBER 41ST, 2026</p>',
            encoding="utf-8")
        ok("...and a string the frame does NOT carry still fails, with the entity still there",
           bool(g_shipped_fresh(_d)),
           "the entity decode became a way to pass, which is a loosening rather than a repair")
        # THE ORDER GUARD. `copy.json` records what a reader SEES, so a frame displaying angle
        # brackets records them bare and the html escapes them. Unescaping before the tag strip
        # would turn `&lt;section&gt;` into `<section>` and then delete it as markup, and the
        # frame would be reported as not carrying copy it plainly displays.
        (_d / "copy.json").write_text(_json.dumps({"slides": {"S3": {
            "n": 3, "strings": ["the tag <section> is shown to the reader"]}}}),
            encoding="utf-8")
        (_d / "slides" / "slide-03.html").write_text(
            "<p>the tag &lt;section&gt; is shown to the reader</p>", encoding="utf-8")
        ok("...and an escaped angle bracket a frame DISPLAYS is not eaten as a tag",
           not g_shipped_fresh(_d), str(g_shipped_fresh(_d)))

    # ---- A FRAME'S SCRIPT IS NOT MARKUP, AND THE TAG STRIP ATE IT. 2026-09-26 ----------------
    #
    # The real artifact, replayed: carousel no. 34's frame 8 sets its timeline labels from a
    # JavaScript array, `const names = ['10 DAYS TO APPEAL A DECISION', ...]`, and its script
    # also carries `for (let i = 0; i < 4; i++)` and `(p) => ...`. The tag strip `<[^>]+>` read
    # from that `<` to the arrow's `>` as one tag and deleted every literal in between, so six
    # strings on frames 8 and 9 that are plainly in the source were reported missing and CI's
    # `shipped_check` step went red on a correct deck.
    #
    # The adversarial half. Reading script text must not become a way to pass, so a string that
    # sits only in a script's block comment, or only in an HTML comment, still fails. Measured
    # on 2026-09-26 by mutation: remove `_display_source`'s comment strips and the second
    # assertion goes red, search the raw file instead of lifting the scripts and the second and
    # third both do, and go back to the one-regex strip and the first one does.
    with _tempfile.TemporaryDirectory() as _t:
        _d = Path(_t) / "2026-09-26"
        (_d / "slides").mkdir(parents=True)
        (_d / "copy.json").write_text(_json.dumps({"slides": {"S8": {
            "n": 8, "strings": ["10 DAYS TO APPEAL A DECISION"]}}}), encoding="utf-8")
        _frame8 = ('<h1>The line is serious bodily injury</h1>\n<script>\n'
                   'for (let i = 0; i < 4; i++) { ticks.push(i); }\n'
                   "const names = ['10 DAYS TO APPEAL A DECISION', 'STATE FILES IN 10 DAYS'];\n"
                   'names.forEach((n, i) => label(n, i));\n</script>\n')
        (_d / "slides" / "slide-08.html").write_text(_frame8, encoding="utf-8")
        ok("a label a frame's script sets as a string literal is found, past a `<` and a `=>`",
           not g_shipped_fresh(_d), str(g_shipped_fresh(_d)))
        (_d / "slides" / "slide-08.html").write_text(
            _frame8.replace("'10 DAYS TO APPEAL A DECISION', ", "")
            .replace("<script>\n", "<script>\n/* was '10 DAYS TO APPEAL A DECISION' */\n"),
            encoding="utf-8")
        ok("...and a string only a script COMMENT carries still fails",
           bool(g_shipped_fresh(_d)),
           "reading script text became a way to pass on a comment, which is a loosening")
        (_d / "slides" / "slide-08.html").write_text(
            "<!-- 10 DAYS TO APPEAL A DECISION -->\n" +
            _frame8.replace("'10 DAYS TO APPEAL A DECISION', ", ""), encoding="utf-8")
        ok("...and a string only an HTML COMMENT carries still fails",
           bool(g_shipped_fresh(_d)),
           "an HTML comment reads as display copy, which is a loosening")
        # A NUMERAL COMPOSED AT RUNTIME IS NOT A STRING THE SOURCE CARRIES. Frame 2 of the same
        # deck builds `miles + " MILES, KODIAK'S FIGURE"`. That stays a finding on purpose: the
        # gate can't tell a fresh 219 from a stale 240 it can't see, and accepting the fragments
        # would pass exactly the refuted-count deck it exists for.
        (_d / "copy.json").write_text(_json.dumps({"slides": {"S2": {
            "n": 2, "strings": ["219 MILES, KODIAK'S FIGURE"]}}}), encoding="utf-8")
        (_d / "slides" / "slide-02.html").write_text(
            '<script>const miles = FIG.v; txt(0, 0, miles + " MILES, KODIAK\'S FIGURE");</script>',
            encoding="utf-8")
        ok("...and a label composed from a variable is still NOT found in the source",
           bool(g_shipped_fresh(_d)), "fragments of a composed string are being accepted")

    # ---- THE CRAWL BOUNDARY ADAPTER HAS TO BITE, 2026-09-19 ---------------------------------
    #
    # The registry is read live, so the assertion names the defect rather than a host: a claim
    # citing the disallowed PATH on the allowed host that a run's helper actually fetched.
    with _tempfile.TemporaryDirectory() as _t:
        _d = Path(_t) / "2026-09-19"
        _d.mkdir()
        (_d / "claims.json").write_text(_json.dumps({"claims": [
            {"id": "c1", "source_url": "https://capitol.texas.gov/TLODOCS/89R/HB1.pdf"},
            {"id": "c2", "source_url": "https://www.ercot.com/services/notices/x"}]}),
            encoding="utf-8")
        probs = g_crawl_boundary(_d)
        ok("a claim citing the 2026-09-19 disallowed path is CAUGHT",
           probs and any("c1" in p for p in probs), str(probs))
        ok("...and the permitted claim beside it is not", probs and len(probs) == 1, str(probs))

    # EVERY GATE MUST BE REACHABLE. The failure this guards against is a registry entry whose
    # loader silently returns None on every run, which reports clean forever. Same shape as
    # craft_floor reading a key qa.py never wrote.
    runs = shipped_runs()
    if runs:
        newest = runs[-1]
        reached = []
        for name, fn, _scope in GATES:
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    r = fn(newest)
                if r is not None:
                    reached.append(name)
            except Exception:                          # noqa: BLE001
                pass
        ok(f"every registered gate actually runs on the newest deck ({newest.name})",
           len(reached) == len(GATES),
           f"reached {reached}, missing {[g[0] for g in GATES if g[0] not in reached]}")

    # A gate that returns problems must be reported as fatal on the newest deck.
    def boom(_d):
        return ["a deliberately broken gate"]
    GATES.append(("selftest probe", boom, CURRENT))
    try:
        if runs:
            f, n = check_run(runs[-1], True)
            ok("a failing gate on the newest deck is FATAL",
               any("selftest probe" in x for x in f), str(f))
            f, n = check_run(runs[0], False) if len(runs) > 1 else ([], ["skipped"])
            if len(runs) > 1:
                ok("...and on an older deck a CURRENT-scope gate is a note rather than fatal",
                   not any("selftest probe" in x for x in f), str(f))
    finally:
        GATES.pop()

    # AN ADVISORY IS NOT A WAIVER AND NOT A SILENT PASS. It must remain visible while never
    # entering the fatal list, which is the construction detector's calibrated contract.
    def advisory_probe(_d):
        return [ADVISORY + "a measured craft signal"]
    GATES.append(("selftest advisory", advisory_probe, CURRENT))
    try:
        if runs:
            f, n = check_run(runs[-1], True)
            ok("an advisory is NOT fatal on the newest deck",
               not any("a measured craft signal" in x for x in f), str(f))
            ok("...and is still reported, in full, as an advisory",
               any("ADVISORY" in x and "a measured craft signal" in x for x in n), str(n))
    finally:
        GATES.pop()

    # THE WAIVER, BOTH DIRECTIONS. A waiver that stopped a finding being REPORTED, or that
    # covered a finding nobody named, would be the switch-off this whole file argues against.
    def waived_probe(_d):
        return [WAIVED + "a named and waived finding", "an unnamed finding beside it"]
    GATES.append(("selftest waiver", waived_probe, CURRENT))
    try:
        if runs:
            f, n = check_run(runs[-1], True)
            ok("a waived finding is NOT fatal on the newest deck",
               not any("a named and waived finding" in x for x in f), str(f))
            ok("...and is still reported, in full, as a note",
               any("a named and waived finding" in x for x in n), str(n))
            ok("...while a finding beside it that no waiver names is still fatal",
               any("an unnamed finding beside it" in x for x in f), str(f))
    finally:
        GATES.pop()

    # AN ABSENT LABEL GATE IS FATAL WITHOUT A WAIVER, and the first fix here returned a string,
    # which `check_run` reads as not-applicable whatever the scope. So the sweep exited 0 over a
    # deck whose label gate had not run. The waiver is lifted for the length of this case: what is
    # under test is that the ordinary answer is red, not that today's named date is exempt.
    if runs and runs[-1].name in LABEL_ABSENT_WAIVED:
        newest = runs[-1]
        f, n = check_run(newest, True)
        ok("a waived absent label gate is a note on the newest deck",
           any("label gate could not run" in x for x in n) and
           not any("label gate could not run" in x for x in f), f"{f} / {n}")
        held = LABEL_ABSENT_WAIVED.pop(newest.name)
        try:
            f, n = check_run(newest, True)
            ok("...and WITHOUT the waiver it is FATAL, never a not-applicable",
               any("label gate could not run" in x for x in f), f"{f} / {n}")
        finally:
            LABEL_ABSENT_WAIVED[newest.name] = held

    # AND THE TABLE MATCHES ON SUBSTRINGS, so an entry that matches nothing is dead weight the
    # next reader will trust. Every waived phrase has to be a finding the gate actually makes.
    for date, table in QUANTIFIER_WAIVED.items():
        d = RUNS / date
        if not (d / "copy.json").exists():
            ok(f"the waiver for {date} names a shipped run", False, "no such run")
            continue
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            raw = _by_module("quantifier_check", d).check(d)
        for phrase in table:
            ok(f"the {date} waiver for {phrase[:40]!r} matches a finding the gate still makes",
               any(phrase in str(p) for p in raw),
               "nothing matches it, so the entry is stale and should be deleted")

    ok("the newest run is identified as the newest",
       (not runs) or shipped_runs()[-1].name == max(p.name for p in shipped_runs()))

    # THE MEASURED FIGURE GATE (2026-08-26). Four rounds of the same defect, and the writer that
    # was supposed to prevent it had gone silently dead.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        (t / "measurements.json").write_text(json.dumps({
            "per_frame_median_lstar": [51.3, 64.1, 14.4, 30.8, 81.4, 73.6, 52.1, 55.2, 48.7],
            "deck_median": 52.1, "deck_sd": 19.3, "frame7_falloff_lstar": 16.5,
            "junctions": [12.8, -49.7, 16.4, 50.6, -7.8, -21.5, 3.1, -6.5]}))
        ok("a run with no prose to read is not a finding", g_measured(t) == [])
        (t / "RUN_RECORD.md").write_text("The falloff measures 16.5 L\\* across the repeats.\n")
        ok("a figure that IS in measurements.json passes", g_measured(t) == [], str(g_measured(t)))
        (t / "RUN_RECORD.md").write_text("The falloff measures 22.1 L\\* across the repeats.\n")
        ok("a stale figure is CAUGHT", len(g_measured(t)) == 1, str(g_measured(t)))
        (t / "RUN_RECORD.md").write_text("frame 6 is 73.6 and frame 7 is 52.1, a 21.5 L* drop.\n")
        ok("a junction written as a positive drop passes", g_measured(t) == [], str(g_measured(t)))
        (t / "RUN_RECORD.md").write_text("a range of 67.0 L\\* across the nine.\n")
        ok("a range over the medians passes", g_measured(t) == [], str(g_measured(t)))
        (t / "RUN_RECORD.md").write_text("a range of 61.0 L\\* across the nine.\n")
        ok("...and a wrong range is CAUGHT", len(g_measured(t)) == 1, str(g_measured(t)))
        (t / "RUN_RECORD.md").write_text("the deck ships 9 frames and 46 claims.\n")
        ok("a bare number that is not a luminance is not this gate's business",
           g_measured(t) == [], str(g_measured(t)))
        (t / "measurements.json").unlink()
        ok("no measurements.json means not applicable, never a silent pass",
           g_measured(t) is None)

    print("\nshipped_check self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="one shipped run date")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.run)


if __name__ == "__main__":
    raise SystemExit(main())
