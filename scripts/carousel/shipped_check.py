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
        allowed = {v for v in figs.values() if isinstance(v, int) and not isinstance(v, bool)}
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
    print(f"shipped_check: {len(runs)} shipped run(s), every applicable gate clean on the "
          f"artifacts as committed")
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
