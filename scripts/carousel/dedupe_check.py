#!/usr/bin/env python3
"""dedupe_check.py — does this story repeat one the record already told?

WHY A JUDGEMENT NEEDS A TOOL

Phase 5 asks the showrunner to check a candidate against `ledger/carousel/topics.json` and refuse
a repeat inside thirty days. That is a semantic judgement, and semantic judgements are made by
reading, and reading is where this fails.

In the sibling product the intended lead on one run was a near-exact repeat of a deck published
eleven days earlier. It survived the first pass because the showrunner read the ledger entry's
TRUNCATED TITLE rather than its full topic, angle, entities and keywords. It was caught by luck,
one step from shipping the same story twice inside the window.

This removes the luck. Given a candidate's entities and keywords, it greps the FULL text of every
entry inside the window and prints what shares the candidate's fingerprint, loudest first.

WHAT IT IS NOT

It does not replace the judgement and it must not be allowed to. A match means **stop and read
that entry in full before the directors room**, not "auto-reject". Two genuinely different
decisions can share every entity in Texas: the same commission, the same county, the same
company. Only a person reading both can say whether the STORY repeats.

So the exit codes are graded rather than binary, and the loudest one still says "read this",
never "reject this".

THE STANDING NOTES, ADDED 2026-09-04, AND THE DEFECT IS THE PREVIOUS RUN TALKING TO A WALL

`ledger/carousel/topics.json` carries an `angle_note` on some entries, written by the run that
shipped that deck for the run that comes next. Deck 14's says, in as many words:

    FOURTH DECK IN SEVEN BUILT ON WHAT A DOCUMENT DOES NOT SAY, and all three round 5 judges
    said so independently. THE NEXT RUN SHOULD PICK A STORY WHERE SOMETHING HAPPENED, not one
    where a document is quiet.

Deck 11's said the same thing about opening moves. Carousel 15's angle is that a document is
quiet, the fifth in eight, and both round 1 judges named it. **The run read that field AFTER the
deck was built**, which is the wrong order, and its own run record says so.

This gate compares topic, entities and keywords. It could not see `angle_note` at all, so the one
field written specifically for the phase this gate serves was read by nothing at the moment it
mattered. The cheapest honest fix is not a rule, it is a READING: every note inside the ledger's
own window is printed here, first, whether or not anything else fires.

**It never changes the exit code and it never will.** An angle is a judgement, and a gate that
refused one would be a gate deciding editorial. This file's whole argument is that the tool
removes the luck and the showrunner keeps the call. A note the run has read and disagreed with is
a decision. A note nobody read is the failure.

THE SECOND BLINDNESS, ADDED 2026-09-07, AND IT IS THE SAME SHAPE ONE LEVEL UP

Everything above compares WORDS. Deck 14 and deck 17 were both a Texas academic supercomputer
whose own documentation restricts access, four days apart, and they share no distinctive word,
so this gate scored the pair 0.35 and said "faint" while three judges scored variety 6.0 and
named the repeat. A bag of words cannot see that two stories are the same KIND of thing.

So the beat of each deck's own docket item is counted and printed beside the fingerprint, out of
`ledger/docket.json`, which already carries that classification. See the block comment above
`docket_beats`. Like the standing notes, it never moves the exit code.

    dedupe_check.py --entities "PUCT, Oncor, Hood County" --keywords "transmission, 765 kV"
    dedupe_check.py --desc "free text description of the candidate"
    dedupe_check.py --item tx-2026-0125 --desc "the candidate"
    dedupe_check.py --self-test

Exit 0 nothing close, 1 a likely repeat to read before proceeding, 2 the ledger cannot be read.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOPICS = REPO_ROOT / "ledger" / "carousel" / "topics.json"
DOCKET = REPO_ROOT / "ledger" / "docket.json"

# Words that carry no fingerprint. Matching on these would make every Texas story look like every
# other Texas story, which is the same as not checking. Kept short and specific: a stop list that
# grows quietly becomes a way to make a repeat invisible.
STOP = {
    "the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "for", "by", "with", "from",
    "is", "are", "was", "were", "be", "been", "it", "its", "this", "that", "these", "those",
    "texas", "texan", "state", "public", "new", "first", "more", "than", "about", "into",
    "ai", "artificial", "intelligence",     # every entry has these. They fingerprint nothing.
}

# THE BANDS. A judgement call about how loudly to speak, not about what to do, which stays with
# the showrunner. The numbers are shares of the candidate's distinctive terms, so they do not
# drift as the ledger grows.
LIKELY = 0.55        # over half the fingerprint in common. Read it before going further.
WORTH_READING = 0.30


def terms(*parts: str) -> set[str]:
    """The distinctive words in a candidate or an entry, lowercased and stripped of noise."""
    text = " ".join(p for p in parts if p)
    words = re.findall(r"[a-z0-9][a-z0-9'-]{2,}", text.lower())
    return {w for w in words if w not in STOP}


def entry_text(e: dict) -> str:
    """EVERY field, not the title. Reading the title alone is the failure this file exists for."""
    bits = []
    for k in ("title", "topic", "angle", "story", "summary", "why"):
        v = e.get(k)
        if isinstance(v, str):
            bits.append(v)
    for k in ("entities", "keywords", "counties", "tags"):
        v = e.get(k)
        if isinstance(v, list):
            bits.extend(str(x) for x in v)
        elif isinstance(v, str):
            bits.append(v)
    return " ".join(bits)


def in_window(e: dict, ref: _dt.date, days: int) -> bool:
    d = e.get("date") or e.get("published") or ""
    try:
        return 0 <= (ref - _dt.date.fromisoformat(str(d)[:10])).days <= days
    except ValueError:
        # An entry with no readable date is IN the window, deliberately. A malformed date must
        # not be a way to hide a repeat.
        return True


def compare(cand: set[str], ledger: dict, ref: _dt.date) -> list[dict]:
    window = int(ledger.get("window_days") or 30)
    out = []
    for e in ledger.get("entries") or []:
        if not in_window(e, ref, window):
            continue
        et = terms(entry_text(e))
        if not et or not cand:
            continue
        shared = cand & et
        # Measured against the CANDIDATE's fingerprint, so a long ledger entry cannot dilute its
        # own similarity by being verbose.
        score = len(shared) / len(cand)
        if score >= WORTH_READING * 0.6:
            out.append({"date": e.get("date", "?"),
                        "title": (e.get("title") or e.get("topic") or "")[:70],
                        "score": round(score, 2), "shared": sorted(shared)[:8]})
    return sorted(out, key=lambda r: -r["score"])


def standing_notes(ledger: dict, ref: _dt.date) -> list[dict]:
    """Every `angle_note` inside the ledger's OWN window, newest first.

    THE WINDOW IS READ FROM THE FILE and is the same one the repeat test uses. A count typed here
    would be a second opinion about how far back a lesson reaches, and this repo already has one
    written down in `window_days`. Fourteen entries carry three notes at the time this was built,
    so it is three lines rather than a wall.
    """
    window = int(ledger.get("window_days") or 30)
    out = []
    for e in ledger.get("entries") or []:
        note = e.get("angle_note")
        if not isinstance(note, str) or not note.strip():
            continue
        if not in_window(e, ref, window):
            continue
        out.append({"date": e.get("date", "?"),
                    "title": (e.get("title") or e.get("topic") or "")[:70],
                    "note": " ".join(note.split())})
    return sorted(out, key=lambda r: str(r["date"]), reverse=True)


# --------------------------------------------------------------------------- the beat
#
# THE FINGERPRINT CANNOT SEE THAT TWO DECKS ARE THE SAME KIND OF THING. 2026-09-07.
#
# Carousel no. 14, on 2026-09-03, was a Texas academic supercomputer whose own documentation
# restricts access. Carousel no. 17, four days later, was a Texas academic supercomputer whose
# own documentation restricts access. Variety scored 6.0, the deck's weakest criterion, and all
# three judges named the same cause. THIS GATE SCORED THE PAIR AT 0.35 and said "faint".
#
# It was right on its own terms. It compares topic, entities and keywords, and the two entity
# lists are disjoint: Texas A&M, Tarleton, TOP500, NVIDIA against TACC, UT Austin, NSF, Frontera,
# Horizon. Two different machines at two different universities share no distinctive word, so a
# bag of words is structurally unable to notice they are the same story told twice.
#
# `topics.json`'s own `angle_note` field has complained about this blindness at decks 8, 11, 14
# and 17, in prose, to nothing that could act on it.
#
# WHAT IS READ, AND WHY IT IS NOT A NEW FIELD. The obvious repair is an `instrument` field on the
# deck ledger. That ledger belongs to the `daily` lane, the field would need writing by a phase
# this one cannot edit, and every entry already committed would carry nothing, so a gate keyed on
# it would be asleep for a month and then depend on a run remembering. The record ALREADY carries
# the classification, computed and schema checked: every deck names its `docket_item`, and every
# docket item carries `topic`, which is the beat. Joining the two reads a fact that exists rather
# than asking for a new one.
#
# Measured over the seventeen decks in the ledger on the day this was written: three of the last
# four and four of the last seven sit on `research-and-science`, and nothing anywhere reported it.
#
# IT NEVER CHANGES THE EXIT CODE, for the same reason the standing notes never do. A beat is not
# a repeat, four genuinely different decisions can share one, and a gate that refused a beat would
# be a gate deciding editorial. This file's whole argument is that the tool removes the luck and
# the showrunner keeps the call. What it removes here is the luck of nobody having counted.
def docket_beats() -> dict:
    """Docket item id to its beat, or an empty map if the record cannot be read."""
    try:
        raw = json.loads(DOCKET.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    items = raw.get("items") if isinstance(raw, dict) else raw
    out = {}
    for i in items or []:
        if isinstance(i, dict) and i.get("id"):
            out[str(i["id"])] = str(i.get("topic") or "")
    return out


def beat_history(ledger: dict, beats: dict, ref: _dt.date) -> list[dict]:
    """Every deck inside the window, newest first, with the beat of the item it was built on.

    An entry whose beat cannot be resolved carries None and is REPORTED as unresolved rather
    than dropped. A check that cannot run is not a check that passed, GATE_LESSONS
    entry 37 ("A law with no mechanism, reported as a skip"), and a
    silently dropped row here would quietly shrink the count the reader is being shown.
    """
    window = int(ledger.get("window_days") or 30)
    out = []
    for e in ledger.get("entries") or []:
        if not in_window(e, ref, window):
            continue
        item = str(e.get("docket_item") or "")
        out.append({"date": str(e.get("date") or "?"),
                    "no": e.get("carousel_no"),
                    "item": item or None,
                    "beat": (beats.get(item) or None) if item else None,
                    "title": (e.get("title") or e.get("topic") or "")[:60]})
    return sorted(out, key=lambda r: str(r["date"]), reverse=True)


def beat_run(history: list[dict], cand: str | None) -> int:
    """How many decks at the head of the window already share the candidate's beat.

    A RUN LENGTH IS MEASURED, NEVER COMPARED TO A NUMBER TYPED HERE. There is no external
    standard for how many decks in a row on one beat is too many, and inventing one would be the
    typed threshold the compute-not-generate law refuses. So this counts and prints, and the
    showrunner decides what the count means.
    """
    if not cand:
        return 0
    n = 0
    for row in history:
        if row["beat"] != cand:
            break
        n += 1
    return n


def print_beat_report(history: list[dict], cand: str | None) -> None:
    if not history:
        return
    unresolved = [r for r in history if not r["beat"]]
    known = [r for r in history if r["beat"]]
    if not known:
        print("dedupe: no deck inside the window names a docket item this record can resolve to "
              "a beat, so the beat comparison could not run. That is a gap, not a clean "
              "result.\n", file=sys.stderr)
        return
    tally = {}
    for r in known:
        tally[r["beat"]] = tally.get(r["beat"], 0) + 1
    order = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))
    print(f"WHAT KIND OF THING THE LAST {len(known)} DECK(S) WERE, out of each one's own docket "
          f"item.\nThe fingerprint below compares words. This compares SUBJECT, which is what it "
          f"cannot see.\n")
    for beat, n in order:
        mark = "  <-- this candidate" if cand and beat == cand else ""
        print(f"  {n:>2}  {beat}{mark}")
    print()
    for r in history[:4]:
        print(f"  {r['date']}  {r['beat'] or 'beat unresolved'}  {r['title']}")
    if unresolved:
        print(f"\n  {len(unresolved)} deck(s) in the window could not be resolved to a beat: "
              f"{', '.join(r['date'] for r in unresolved)}. A row that cannot be read is not a "
              f"row that agrees.")
    if cand:
        run = beat_run(history, cand)
        share = tally.get(cand, 0)
        if run:
            print(f"\n  THE LAST {run} DECK(S) IN A ROW SIT ON `{cand}`, and this candidate would "
                  f"make it {run + 1}. Deck 14 and deck 17 were both a Texas academic "
                  f"supercomputer whose documentation restricts access, four days apart, and this "
                  f"gate scored that pair 0.35 because their entity lists are disjoint. Variety "
                  f"scored 6.0.")
        elif share:
            print(f"\n  `{cand}` is {share} of the {len(known)} deck(s) in the window, though not "
                  f"the most recent one.")
        else:
            print(f"\n  No deck in the window sits on `{cand}`.")
    print("\n  A beat is not a repeat and this NEVER changes the exit code. Four different "
          "decisions\n  can share one. It is here because nothing else counts it, and the ledger's "
          "own\n  angle_note field asked for this at decks 8, 11, 14 and 17 with nothing able to "
          "act.\n")


def print_standing_notes(notes: list[dict]) -> None:
    """First, before the verdict, because a lesson printed under a verdict is a lesson skipped."""
    if not notes:
        print("dedupe: no run inside the window left an angle note.\n")
        return
    print(f"WHAT THE LAST {len(notes)} RUN(S) TOLD THIS ONE, out of topics.json's own "
          f"`angle_note` field.\nRead these BEFORE choosing, not after building.\n")
    for n in notes:
        print(f"  {n['date']}  {n['title']}")
        for line in _wrap(n["note"]):
            print(f"      {line}")
        print()
    print("  These are JUDGEMENTS, not rules, and this gate will never fail one. A note you have\n"
          "  read and disagreed with is a decision. A note nobody read is how deck 14's "
          "instruction\n  reached deck 15 after the deck was built.\n")


def _wrap(text: str, width: int = 88) -> list[str]:
    out, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


def run(cand_terms: set[str], ref: _dt.date, item: str | None = None,
        beat: str | None = None) -> int:
    try:
        ledger = json.loads(TOPICS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"dedupe_check: cannot read {TOPICS}: {exc}", file=sys.stderr)
        return 2
    # PRINTED BEFORE ANYTHING ELSE, INCLUDING BEFORE THE ARGUMENT CHECK BELOW, so a run that gets
    # the invocation wrong still reads what the last run told it.
    print_standing_notes(standing_notes(ledger, ref))
    beats = docket_beats()
    if not beats:
        print(f"dedupe: {DOCKET} could not be read, so no deck's beat could be resolved and the "
              f"subject comparison did not run.\n", file=sys.stderr)
    else:
        cand_beat = beat or (beats.get(item) if item else None)
        if item and not cand_beat:
            print(f"dedupe: {item} is not in the record, so this candidate has no beat to "
                  f"compare. A deck about something the docket does not carry is a deck "
                  f"undermining the site it links to.\n", file=sys.stderr)
        print_beat_report(beat_history(ledger, beats, ref), cand_beat)
    if not cand_terms:
        print("dedupe_check: the candidate has no distinctive terms. Give --entities, "
              "--keywords or --desc with something specific in it", file=sys.stderr)
        return 2

    hits = compare(cand_terms, ledger, ref)
    window = ledger.get("window_days", 30)
    n = len(ledger.get("entries") or [])
    if not hits:
        print(f"dedupe: nothing close ({n} entr{'y' if n == 1 else 'ies'} in the ledger, "
              f"{window} day window)")
        return 0

    worst = hits[0]["score"]
    print(f"dedupe: {len(hits)} entr{'y' if len(hits) == 1 else 'ies'} share this "
          f"fingerprint, loudest first\n")
    for h in hits[:6]:
        band = ("LIKELY REPEAT" if h["score"] >= LIKELY else
                "worth reading" if h["score"] >= WORTH_READING else "faint")
        print(f"  [{band:>13}] {h['score']:.2f}  {h['date']}  {h['title']}")
        print(f"                   shared: {', '.join(h['shared'])}")
    if worst >= LIKELY:
        print("\n  READ THAT ENTRY IN FULL before the directors room. This is a signal, not a "
              "verdict: two different decisions can share every entity in Texas. The thirty day "
              "rule is still the showrunner's call, made after reading.")
        return 1
    print("\n  Nothing at the repeat threshold. Read the top entry anyway if it is your lead.")
    return 0


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    ref = _dt.date(2026, 8, 12)
    ledger = {
        "window_days": 30,
        "entries": [
            {"date": "2026-08-01",
             "title": "PUCT opens comment on large load demand management",
             "topic": "power-and-the-grid",
             "angle": "The commission is writing the rule that decides how fast a data center "
                      "can be told to stop drawing power",
             "entities": ["PUCT", "ERCOT", "Oncor"],
             "keywords": ["large load", "demand management", "curtailment"]},
            {"date": "2026-07-20",
             "title": "TEA's automated scoring engine grades the STAAR",
             "topic": "health-and-education",
             "entities": ["Texas Education Agency"],
             "keywords": ["STAAR", "automated scoring"]},
            {"date": "2026-05-02",     # outside the window
             "title": "PUCT large load demand management, earlier round",
             "entities": ["PUCT", "ERCOT", "Oncor"],
             "keywords": ["large load", "demand management", "curtailment"]},
        ],
    }

    # THE SIBLING'S ACTUAL NEAR MISS: a repeat whose TITLE reads differently. The title here
    # shares almost nothing; the angle, entities and keywords share nearly everything.
    repeat = terms("Oncor ERCOT PUCT", "curtailment large load demand management")
    hits = compare(repeat, ledger, ref)
    ok("a repeat is found even when the title reads differently",
       bool(hits) and hits[0]["score"] >= LIKELY, str(hits[:1]))
    ok("...and the entry it names is the recent one, not the old one",
       hits[0]["date"] == "2026-08-01", str(hits[:1]))

    # Reading the title alone is what let it through. Prove the tool reads more than the title.
    title_only = {"date": "2026-08-01", "title": "PUCT opens comment on large load demand "
                                                 "management"}
    ok("entry_text reads the angle, entities and keywords, not just the title",
       "curtailment" in entry_text(ledger["entries"][0])
       and "curtailment" not in entry_text(title_only))

    fresh = terms("Alabama-Coushatta tribal broadband", "spectrum licence rural")
    ok("an unrelated story is quiet", not compare(fresh, ledger, ref))

    old = terms("PUCT ERCOT Oncor curtailment large load demand management")
    outside = {"window_days": 30, "entries": [ledger["entries"][2]]}
    ok("an entry outside the window does not count", not compare(old, outside, ref))

    ok("a stop word alone fingerprints nothing", not terms("the state of Texas and AI"))
    ok("...but a real entity survives it", "oncor" in terms("Oncor in the state of Texas"))

    undated = {"window_days": 30, "entries": [{"title": "PUCT large load demand management",
                                               "keywords": ["curtailment", "large load"]}]}
    ok("an entry with no date is treated as inside the window, so a bad date cannot hide a "
       "repeat", bool(compare(old, undated, ref)))

    ok("an empty ledger is clean rather than an error",
       not compare(old, {"window_days": 30, "entries": []}, ref))

    # The score is a share of the CANDIDATE, so a verbose ledger entry cannot dilute itself.
    verbose = {"window_days": 30, "entries": [dict(ledger["entries"][0],
               angle=ledger["entries"][0]["angle"] + " " + "filler word here " * 60)]}
    ok("a verbose entry cannot dilute its own similarity",
       compare(repeat, verbose, ref)[0]["score"] >= LIKELY)

    # ---- THE STANDING NOTES (2026-09-04) ------------------------------------------------
    #
    # Deck 14 told deck 15 to pick a story where something happened. Deck 15 read that field after
    # it had built the deck, because nothing surfaced it at selection.
    noted = dict(ledger)
    noted["entries"] = [
        dict(ledger["entries"][0],
             angle_note="FOURTH DECK IN SEVEN BUILT ON WHAT A DOCUMENT DOES NOT SAY. THE NEXT "
                        "RUN SHOULD PICK A STORY WHERE SOMETHING HAPPENED."),
        ledger["entries"][1],
        dict(ledger["entries"][2], angle_note="an older note, outside the window"),
    ]
    ns = standing_notes(noted, ref)
    ok("deck 14's instruction to the next run is SURFACED", len(ns) == 1, str(ns))
    ok("...and it is the note itself, not a truncation of the title",
       bool(ns) and "SOMETHING HAPPENED" in ns[0]["note"], str(ns))
    ok("...and a note outside the thirty day window is not carried forward",
       all(n["date"] != "2026-05-02" for n in ns), str(ns))
    ok("a ledger with no angle notes surfaces nothing rather than raising",
       standing_notes(ledger, ref) == [])
    ok("an entry whose angle_note is blank is not a note",
       not standing_notes({"window_days": 30,
                           "entries": [dict(ledger["entries"][0], angle_note="   ")]}, ref))
    # THE NOTE NEVER MOVES THE VERDICT. Surfacing is reading, and a gate that failed on an angle
    # would be a gate deciding editorial, which this file's own docstring refuses.
    ok("surfacing a note changes no score and no band",
       compare(terms("Alabama-Coushatta tribal broadband"), noted, ref) == [])

    # AGAINST THE REAL LEDGER, because a parser proved only against fixtures this file wrote
    # agrees with this file. The day a run spells the field differently this goes red rather than
    # going quiet, which is the failure mode the whole upgrade exists to close.
    try:
        real = json.loads(TOPICS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        real = None
    if real is not None:
        carried = [e for e in real.get("entries") or [] if (e.get("angle_note") or "").strip()]
        ok(f"the shipped topics.json carries angle notes this reads ({len(carried)} entr"
           f"{'y' if len(carried) == 1 else 'ies'})", bool(carried))
        newest = max((str(e.get("date") or "") for e in real.get("entries") or []), default="")
        if newest:
            live = standing_notes(real, _dt.date.fromisoformat(newest[:10]))
            ok("...and at least one of them is inside the window on the newest entry's own date",
               bool(live), f"newest={newest}")

    # ---- THE BEAT (2026-09-07) ----------------------------------------------------------
    #
    # THE DISCRIMINATION FIRST, because a test whose input cannot tell a working implementation
    # from a broken one is measuring the agreement. That is GATE_LESSONS
    # entry 36 ("A test that cannot tell a working implementation from a broken one").
    # Deck 14 and deck 17 are the pair this exists for, and the point is that the WORD
    # comparison scores them faint. If that
    # first assertion ever goes red, the fingerprint has started seeing the pair on its own and
    # this whole addition should be re-argued rather than kept.
    d14 = {"date": "2026-09-03", "carousel_no": 14, "docket_item": "tx-2026-0119",
           "topic": "The Texas A&M University System's VISION supercomputer and its entry on the "
                    "world list at number 66, against documentation saying access is "
                    "invitation-only under a controlled beta",
           "entities": ["The Texas A&M University System", "Tarleton State University", "TOP500",
                        "West Campus Data Center", "NVIDIA"],
           "keywords": ["VISION", "TOP500", "controlled beta", "invitation-only", "petaflops",
                        "DGX", "general availability"]}
    d16 = {"date": "2026-09-05", "carousel_no": 16, "docket_item": "tx-2026-0124",
           "topic": "an ARPA-E award to a University of Houston led coalition to design permanent "
                    "magnets", "entities": ["Rice University"], "keywords": ["rare earths"]}
    d17_terms = terms("Texas Advanced Computing Center, Frontera, Horizon, "
                      "National Science Foundation",
                      "supercomputer, decommission, queues, user guide, allocation, open science")
    lg = {"window_days": 30, "entries": [d14, d16]}
    ref17 = _dt.date(2026, 9, 7)
    hits17 = compare(d17_terms, lg, ref17)
    ok("deck 17 against deck 14 is FAINT on words, which is the blindness this exists for",
       (not hits17) or hits17[0]["score"] < WORTH_READING, str(hits17))

    beats = {"tx-2026-0119": "research-and-science", "tx-2026-0124": "research-and-science",
             "tx-2026-0109": "state-policy"}
    hist = beat_history(lg, beats, ref17)
    ok("...and the beat history resolves both decks", [r["beat"] for r in hist]
       == ["research-and-science", "research-and-science"], str(hist))
    ok("...so the run at the head is two, and deck 17 would make it three",
       beat_run(hist, "research-and-science") == 2, str(hist))
    ok("a candidate on a different beat has no run",
       beat_run(hist, "state-policy") == 0, str(hist))

    # AN ENTRY WHOSE BEAT CANNOT BE READ IS REPORTED, NEVER DROPPED. A silently shortened
    # history is a count of the wrong set, which reads exactly like a count of the right one.
    lg2 = {"window_days": 30, "entries": [dict(d14, docket_item="tx-9999-9999"), d16]}
    h2 = beat_history(lg2, beats, ref17)
    ok("a deck whose docket item is not in the record keeps its row with no beat",
       len(h2) == 2 and h2[1]["beat"] is None, str(h2))
    ok("...and it BREAKS the run rather than being skipped over, so an unreadable row can never "
       "join two decks that were never adjacent",
       beat_run(h2, "research-and-science") == 1, str(h2))

    # OUTSIDE THE WINDOW IS OUTSIDE THE BEAT COMPARISON TOO, on the same window_days the repeat
    # test uses, so the two halves of this gate can never disagree about how far back it reaches.
    lg3 = {"window_days": 30, "entries": [dict(d14, date="2026-05-02"), d16]}
    ok("a deck outside the window is not in the beat history",
       [r["date"] for r in beat_history(lg3, beats, ref17)] == ["2026-09-05"],
       str(beat_history(lg3, beats, ref17)))

    ok("an unreadable record yields no beats rather than raising", isinstance(docket_beats(), dict))

    # AGAINST THE SHIPPED LEDGERS, because a fixture written beside the detector agrees with it.
    # Both files are committed, so this runs in CI as well as here.
    try:
        real_t = json.loads(TOPICS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        real_t = None
    real_b = docket_beats()
    # ASSERTED, NEVER GUARDED. Both files are committed, so an unreadable one is a failure and
    # not a skip. Written as a condition first, this whole block went quiet when the record could
    # not be resolved and the suite reported all passed. That is GATE_LESSONS
    # entry 37 ("A law with no mechanism, reported as a skip") exactly, where a
    # check that CANNOT RUN is the opposite of a check that did not need to.
    ok(f"the shipped ledgers both resolve, so this ran on real artifacts ({len(real_b)} record "
       f"item(s))", bool(real_t) and bool(real_b), f"topics={bool(real_t)} docket={len(real_b)}")
    if real_t and real_b:
        newest = max((str(e.get("date") or "") for e in real_t.get("entries") or []), default="")
        rh = beat_history(real_t, real_b, _dt.date.fromisoformat(newest[:10]))
        ok(f"every deck in the shipped window resolves to a beat ({len(rh)} in the window)",
           bool(rh) and all(r["beat"] for r in rh),
           str([r["date"] for r in rh if not r["beat"]]))
        newest_beat = rh[0]["beat"] if rh else None
        ok("...and the newest deck's own beat is a run of at least one, by construction",
           beat_run(rh, newest_beat) >= 1, str(rh[:3]))

    if failures:
        print(f"\ndedupe_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\ndedupe_check self-test: all passed (repeat band {LIKELY}, read band "
          f"{WORTH_READING})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--entities", default="")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--desc", default="")
    ap.add_argument("--date", help="reference date, default today")
    ap.add_argument("--item", help="the docket item this candidate is built on, e.g. "
                                   "tx-2026-0125. Its beat is compared against the window's")
    ap.add_argument("--beat", help="the beat itself, where the item is not admitted yet")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    ref = _dt.date.fromisoformat(a.date) if a.date else _dt.date.today()
    return run(terms(a.entities, a.keywords, a.desc), ref, a.item, a.beat)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"dedupe_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
