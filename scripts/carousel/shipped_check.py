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
import io
import json
import contextlib
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
    import copy_sync_check as m
    copy, rep = _load(d / "copy.json"), _load(d / "render_report.json")
    if not (copy and rep):
        return None
    claims = _load(d / "claims.json")
    drifted, uncited = m.compare(copy, rep, claims)
    return drifted + uncited


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
    import craft_floor as m
    rep = _load(d / "render_report.json")
    if not rep:
        return None
    fails, _warns, _meta = m.check(rep, _load(d / "machine_qa.json"))
    return fails


def g_plan_render(d: Path):
    import plan_render_check as m
    sb, rep = d / "storyboard.md", _load(d / "render_report.json")
    if not (sb.exists() and rep):
        return None
    fails, _w, _s = m.check(sb.read_text(encoding="utf-8"), d / "slides", rep)
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
            flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
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
    """How much of the deck one primitive carries, measured on the shipped images.

    See scripts/carousel/construction_check.py for what it measures and why bespoke_check, which
    was already green on the deck that produced this finding, could not see it: that file
    compares drawing CODE and a reader sees the drawn OBJECT.

    NOT APPLICABLE to any deck drawn on or before CONSTRUCTION_SINCE, which is the run that
    taught it. Every one of those is reported as a note instead, and the notes are worth reading:
    run into history this finds 4 of 8, 6 of 9 and 7 of 9 on three earlier decks, so the primitive
    carrying a deck is a standing habit rather than one bad Tuesday.
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
    return None if code == 2 else problems


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
    """
    import run_complete as m
    if not (d / "score.json").exists():
        return None
    return list(m.check(d, m.threshold(), m.max_rounds()) or [])


GATES = [
    ("copy sync", g_copy_sync, HISTORY),
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
    # CURRENT, because it is a property of the deck being made now and because every deck older
    # than it was drawn without it. See its own docstring for why bespoke_check, which was
    # already green, could not see this: that file compares drawing CODE and a reader sees the
    # drawn OBJECT.
    ("construction", g_construction, CURRENT),
    ("completion", g_completion, HISTORY),
]


def shipped_runs() -> list:
    return sorted([p for p in RUNS.glob("2*") if (p / "copy.json").exists()]) if RUNS.exists() else []


def held(d: Path):
    """The panel's verdict where it refused the deck, as a sentence, or None.

    THIS FILE'S OWN BANNER SAYS IT REPORTS PROBLEMS IN WORK THAT IS ALREADY PUBLISHED, and it
    decided what was published from the presence of a run directory. A HELD run has a run
    directory because the delivery policy REQUIRES one: a failed run commits its evidence to its
    branch and does not merge. So the sweep judged unpublished work as published, and the branch
    of a run that was being honest about failing could never go green.

    Carousel no. 17, 2026-09-06, is the case. The panel returned 6.552 against a 6.8 bar with a
    hard fail, the deck was left exactly as the panel scored it, and this file then reported the
    completion gate's "THE DECK DID NOT SHIP" as a defect in published work. It is not a defect.
    It is the run saying what happened, and the gate reading it back as news.

    NOTHING IS FORGIVEN AND NOTHING IS DROPPED. Every finding on a held run is still printed, in
    full, under the date that carries it, the way a WAIVED finding already is. Only the fatal
    list is shorter. A held deck's findings are frequently the most useful output this sweep
    produces: on 2026-09-06 the quantifier gate independently caught the same sentence the reader
    judge hard failed the deck for, which is a gate agreeing with a judge and worth reading.

    THE TEST IS A HARD FAIL AND NOT `ship: false`, and the first draft of this function got that
    wrong in the direction that matters. `ship: false` says the panel REFUSED, which is not the
    same as the deck not publishing: the rubric caps the search at five rounds and says that past
    the cap a run ships whatever the weighted score is, stating it honestly. Four SHIPPED decks
    carry `ship: false` with an empty hard_fails list for exactly that reason, 2026-08-30 at
    6.582, 2026-09-02 at 6.562, 2026-09-03 at 6.762 and 2026-09-04 at 6.678. Reading `ship` alone
    put all four out of scope, which would have suppressed every future finding on four published
    decks. That is the opposite of what this file is for, and it is the failure mode of every
    exemption: the first draft of one is always too generous to the run that wrote it.

    A HARD FAIL is what stops a deck at any round whatever the median says, in the rubric's own
    words, and it is the only verdict that means the deck did not publish.

    AND IT IS NOT A WAY TO DODGE A GATE. `hard_fails` is written by `panel.py` from three judges'
    cards, not by the run, and a run carrying one does not merge, so there is nothing on the far
    side of this door to reach.
    """
    f = d / "score.json"
    if not f.exists():
        return None
    try:
        v = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    hf = len(v.get("hard_fails") or [])
    if v.get("ship") is not False or not hf:
        return None
    score, bar = v.get("weighted_score"), v.get("threshold")
    return (f"HELD by the panel, {score} against a {bar} bar, {hf} hard fail(s). A hard fail "
            f"stops a deck at any round, so this deck did not publish and this sweep's subject "
            f"does not include it. Every finding below is still printed")


def check_run(d: Path, newest: bool) -> tuple:
    """Returns (fatal, notes). Each is a list of strings."""
    fatal, notes = [], []
    hold = held(d)
    if hold:
        notes.append(f"{d.name}  {hold}")
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
        if hold:
            notes.append(line + "   [held deck, not published work]")
        elif scope == HISTORY or newest:
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
    for d in runs:
        f, n = check_run(d, d.name == newest)
        fatal += f
        notes += n
    for n in notes:
        print(f"  note  {n}")
    if fatal:
        print(f"\nshipped_check: {len(fatal)} problem(s) in work that is already published\n",
              file=sys.stderr)
        for f in fatal:
            print(f"  - {f}", file=sys.stderr)
        return 1
    # THE CLOSING LINE NAMES THE WAIVERS. "every applicable gate clean" over a sweep carrying a
    # waived finding is the narrow-measurement sentence this file exists to catch, in this file.
    # IT NAMES THE HELD RUNS FOR THE SAME REASON. Calling a held run a shipped run in the count,
    # one line under a note saying the panel refused it, would be this file telling the exact
    # kind of half truth it was written to catch.
    n_waived = sum(1 for n in notes if "WAIVED." in n)
    held_names = [d.name for d in runs if held(d)]
    n_shipped = len(runs) - len(held_names)
    print(f"shipped_check: {n_shipped} shipped run(s), every applicable gate clean on the "
          f"artifacts as committed" +
          (f", except {n_waived} named waiver(s) reported above and not fatal" if n_waived else "") +
          (f". {len(held_names)} run(s) HELD and out of scope, reported above and not fatal: "
           f"{', '.join(held_names)}" if held_names else ""))
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

    # EVERY GATE MUST BE REACHABLE. The failure this guards against is a registry entry whose
    # loader silently returns None on every run, which reports clean forever. Same shape as
    # craft_floor reading a key qa.py never wrote.
    runs = shipped_runs()
    # THE NEWEST PUBLISHED DECK. A held run is missing whatever a run writes at ship, so it
    # reports gates as not-applicable that are alive on every deck that shipped, and this check
    # would read that as a dead registry entry. It is a question about the GATES.
    live_runs = [r for r in runs if not held(r)]
    if live_runs:
        newest = live_runs[-1]
        reached = []
        for name, fn, _scope in GATES:
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    r = fn(newest)
                if r is not None:
                    reached.append(name)
            except Exception:                          # noqa: BLE001
                pass
        ok(f"every registered gate actually runs on the newest published deck ({newest.name})",
           len(reached) == len(GATES),
           f"reached {reached}, missing {[g[0] for g in GATES if g[0] not in reached]}")

    # A gate that returns problems must be reported as fatal on the newest deck.
    def boom(_d):
        return ["a deliberately broken gate"]
    GATES.append(("selftest probe", boom, CURRENT))
    try:
        # THE NEWEST PUBLISHED DECK, not simply the newest directory. A held run is out of this
        # sweep's scope, so pointing the fatality proof at one would prove nothing and would go
        # quiet exactly when a real regression arrived. A self-test that cannot go red is the
        # thing this file is about.
        live = [r for r in runs if not held(r)]
        if live:
            f, n = check_run(live[-1], True)
            ok("a failing gate on the newest published deck is FATAL",
               any("selftest probe" in x for x in f), str(f))
            f, n = check_run(runs[0], False) if len(runs) > 1 else ([], ["skipped"])
            if len(runs) > 1:
                ok("...and on an older deck a CURRENT-scope gate is a note rather than fatal",
                   not any("selftest probe" in x for x in f), str(f))
        # THE HELD CASE, BOTH DIRECTIONS.
        holds = [r for r in runs if held(r)]
        if holds:
            f, n = check_run(holds[-1], True)
            ok("a failing gate on a HELD deck is a note and never fatal",
               not any("selftest probe" in x for x in f), str(f))
            ok("...and the finding is still PRINTED in full, never dropped",
               any("selftest probe" in x for x in n), str(n))
            ok("...and the hold names its score, so the sweep says why it stood down",
               any("HELD by the panel" in x and "hard fail" in x for x in n), str(n))
        # THE DISCRIMINATOR, and this is the assertion that would have caught my own first draft.
        # `ship: false` alone is NOT a hold: the rubric ships a deck past the round cap whatever
        # the weighted score is, so four published decks carry it with no hard fail. Reading
        # `ship` alone put all four out of scope and would have silenced this sweep on them.
        refused = []
        for r in runs:
            try:
                v = json.loads((r / "score.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if v.get("ship") is False and not (v.get("hard_fails") or []):
                refused.append(r.name)
        ok("a deck the panel refused on the NUMBER alone is still published work",
           all(not held(RUNS / name) for name in refused),
           f"refused-on-number: {refused}")
    finally:
        GATES.pop()

    # THE WAIVER, BOTH DIRECTIONS. A waiver that stopped a finding being REPORTED, or that
    # covered a finding nobody named, would be the switch-off this whole file argues against.
    def waived_probe(_d):
        return [WAIVED + "a named and waived finding", "an unnamed finding beside it"]
    GATES.append(("selftest waiver", waived_probe, CURRENT))
    try:
        # A PUBLISHED DECK, because the third assertion here is the one that proves a waiver
        # narrows nothing beside itself, and on a held deck nothing is fatal so it proves nothing.
        if live_runs:
            f, n = check_run(live_runs[-1], True)
            ok("a waived finding is NOT fatal on the newest published deck",
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
        # NOT `held`, which is now a module function this scope would shadow for its whole body.
        waived_label = LABEL_ABSENT_WAIVED.pop(newest.name)
        try:
            f, n = check_run(newest, True)
            ok("...and WITHOUT the waiver it is FATAL, never a not-applicable",
               any("label gate could not run" in x for x in f), f"{f} / {n}")
        finally:
            LABEL_ABSENT_WAIVED[newest.name] = waived_label

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
