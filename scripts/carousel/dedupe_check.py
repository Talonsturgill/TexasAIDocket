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

    dedupe_check.py --entities "PUCT, Oncor, Hood County" --keywords "transmission, 765 kV"
    dedupe_check.py --desc "free text description of the candidate"
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


def run(cand_terms: set[str], ref: _dt.date) -> int:
    try:
        ledger = json.loads(TOPICS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"dedupe_check: cannot read {TOPICS}: {exc}", file=sys.stderr)
        return 2
    # PRINTED BEFORE ANYTHING ELSE, INCLUDING BEFORE THE ARGUMENT CHECK BELOW, so a run that gets
    # the invocation wrong still reads what the last run told it.
    print_standing_notes(standing_notes(ledger, ref))
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
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    ref = _dt.date.fromisoformat(a.date) if a.date else _dt.date.today()
    return run(terms(a.entities, a.keywords, a.desc), ref)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"dedupe_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
