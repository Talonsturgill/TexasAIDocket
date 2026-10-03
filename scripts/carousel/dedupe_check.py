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

EXCEPT THE THIRTY DAY RULE ITSELF, WHICH IS BINDING SINCE 2026-10-03, ON THE OWNER'S INSTRUCTION

Carousel no. 41 was Kodiak AI's Dallas to Houston lane seven days after carousel no. 34 was
Kodiak AI's Dallas to Houston lane. This gate said "worth reading" at 0.50, the run read it and
chose the story, two of three round 1 judges hard failed the window, and the deck shipped after
five rounds with variety at 5.5. So three measured things are now a REPEAT, exit 3, and a REPEAT
is not a signal: the routine picks another story. The same docket item, the same documents, or the
same company at the same place, inside the window. See the block comment above `thirty_day_rule`,
which carries what it was measured on. Everything else here still prints and decides nothing.

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

THE THIRD BLINDNESS, ADDED 2026-09-16, AND IT IS THE SAME SHAPE ONE LEVEL UP AGAIN

The beat says two decks are about the same KIND OF SUBJECT. It cannot say they were built by
reading the same KIND OF DOCUMENT. Carousel no. 26 read an NSF award record against a university's
own release, which is what carousel no. 11 did eighteen days earlier, and two of three judges
charged it independently while this gate was correctly quiet on words and correctly quiet on the
beat. `topics.json` asked for this in prose at decks 17, 19, 23 and 26.

So the documents each deck stood on are read out of its own committed `claims.json` and printed
beside the beat. See the block comment above `registrable`. It never moves the exit code either.

**PASS `--item` AND THE CANDIDATE'S OWN DOCUMENTS ARE COMPARED TOO.** Without it, only the window
is described, and the report says so rather than printing a clean line about a comparison that
did not happen.

    dedupe_check.py --item tx-2026-0125 --entities "PUCT, Oncor" --places "Hood County" \
                    --keywords "transmission, 765 kV"
    dedupe_check.py --item tx-2026-0125 --desc "the candidate"
    dedupe_check.py --self-test

**`--item` IS REQUIRED.** The thirty day rule compares the candidate's own docket item, so a run
without one has not been checked against the rule, and says so with exit 2 rather than a clean line.

Exit 0 nothing close, 1 a likely repeat to read before proceeding, 2 the ledger or the record
can't be read or no `--item` was given, 3 THE THIRTY DAY RULE IS BROKEN. Pick another story.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

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


# --------------------------------------------------------------------------- the instrument
#
# THE THIRD BLINDNESS, ADDED 2026-09-16, AND THE LEDGER ASKED FOR IT FOUR TIMES FIRST.
#
# Two of three judges on carousel no. 26 independently charged the deck for its INSTRUMENT: it
# reads an NSF award record against the university's own release, which is what carousel no. 11
# did eighteen days earlier on a robotics award. Topic, entities and keywords all differ, so the
# fingerprint above is correctly quiet, and the beat is `research-and-science` for both, which the
# beat report does say. What it does not say is that the two decks read THE SAME KIND OF DOCUMENT.
#
# `topics.json` has complained about this in prose at decks 17, 19, 23 and 26. Deck 23's note is
# the clearest: "Deck 17's angle_note already wrote in capitals that the gate does not compare
# INSTRUMENT, deck 19 added the field, and nothing reads it."
#
# WHY NOT READ THE `instrument` FIELD, WHICH NOW EXISTS. Measured on 2026-09-16: five of the
# twenty six entries carry one, and eleven of the sixteen inside the window do not, CAROUSEL 11
# INCLUDED. A gate keyed on that field is structurally unable to see the repeat it was built for,
# which is a gate that cannot go red on its own defect. The 2026-09-07 comment above predicted
# exactly this and chose the beat for the same reason.
#
# WHAT IS READ INSTEAD. Every deck's own `claims.json` carries the URL of every document it stood
# on, committed under `runs/carousel/<date>/`, for every deck this project has ever shipped. The
# documents a deck read ARE its instrument, in data the run already produced, with no new field,
# no typed vocabulary and nothing for a run to remember. Measured over all 26 shipped decks it
# names both repeats the ledger recorded by hand:
#
#   nsf.gov   2026-08-29 (17 claims) and 2026-09-16 (14), the pair two judges charged today
#   nih.gov   2026-09-09 (14) and 2026-09-13 (26), the pair deck 23's own note describes
#
# THE HONEST LIMIT, stated here rather than left to be inferred. A shared publisher is evidence of
# a shared instrument and is not proof of one: two ERCOT decks can read a board presentation and a
# market notice, which are different instruments at one host. And the reverse is invisible, since
# two clinical studies at two different publishers share no domain. This prints what it measured
# and decides nothing, exactly like the beat report beside it.
#
# IT NEVER CHANGES THE EXIT CODE. A repeated instrument is a variety judgement, four honest decks
# can share one, and a gate that refused one would be a gate deciding editorial.
RUNS = REPO_ROOT / "runs" / "carousel"


def registrable(host: str) -> str:
    """The site a URL belongs to: `api.nsf.gov` and `nsf.gov` are one site, so are the two NCBI
    subdomains. The last two labels, or three where the second to last is a two letter code, so
    `sos.state.tx.us` does not collapse to `tx.us` and take every Texas county with it.
    """
    parts = [p for p in host.lower().strip().split(".") if p]
    if len(parts) <= 2:
        return ".".join(parts)
    if len(parts[-1]) == 2 and len(parts[-2]) <= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _hosts(rows: list) -> dict:
    out: dict = {}
    for c in rows:
        if not isinstance(c, dict):
            continue
        url = str(c.get("url") or c.get("source_url") or "")
        m = re.match(r"https?://([^/?#]+)", url)
        if not m:
            continue
        host = m.group(1).lower().split(":")[0]
        host = host[4:] if host.startswith("www.") else host
        if host:
            out[host] = out.get(host, 0) + 1
    return out


def claim_hosts(path: Path) -> dict | None:
    """Host to claim count for one deck's committed claims file, or None if it cannot be read.

    NONE IS NOT AN EMPTY DICT. A deck whose claims file is missing has not been compared, and
    reporting that as "no shared documents" is the shape GATE_LESSONS 37 is about.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    rows = raw.get("claims") if isinstance(raw, dict) else raw
    return _hosts(rows) if isinstance(rows, list) else None


def item_hosts(item: str) -> dict | None:
    """The documents the candidate's own docket item stands on, by host."""
    try:
        raw = json.loads(DOCKET.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    items = raw.get("items") if isinstance(raw, dict) else raw
    for i in items or []:
        if isinstance(i, dict) and str(i.get("id")) == item:
            return _hosts(i.get("claims") or [])
    return None


def as_sites(hosts: dict | None) -> dict | None:
    if hosts is None:
        return None
    out: dict = {}
    for host, n in hosts.items():
        out[registrable(host)] = out.get(registrable(host), 0) + n
    return out


def source_history(ledger: dict, ref: _dt.date, runs: Path | None = None) -> list[dict]:
    """Every deck inside the window with the hosts its own claims file cites, newest first."""
    window = int(ledger.get("window_days") or 30)
    base = runs or RUNS
    out = []
    for e in ledger.get("entries") or []:
        if not in_window(e, ref, window):
            continue
        date = str(e.get("date") or "")
        hosts = claim_hosts(base / date / "claims.json") if date else None
        out.append({"date": date or "?", "no": e.get("carousel_no"),
                    "title": (e.get("title") or e.get("topic") or "")[:60],
                    "hosts": hosts, "sites": as_sites(hosts)})
    return sorted(out, key=lambda r: str(r["date"]), reverse=True)


# TWO LEVELS, REPORTED SEPARATELY, AND THE REASON IS THAT COLLAPSING THEM LIES IN ONE DIRECTION.
#
# `api.nsf.gov` and `nsf.gov` are one publisher. `gov.texas.gov` and `sboe.texas.gov` are the
# Governor's office and the State Board of Education, which are not. Both pairs are subdomains of
# one registered name, so no rule over the string can tell them apart, and measured over the
# shipped corpus a site level join puts ten decks under `texas.gov` and buries the two real
# instrument repeats underneath it.
#
# So the exact address is reported as the strong signal, and a shared organisation at DIFFERENT
# addresses is reported beside it as the weak one, labelled. That keeps `pmc.ncbi.nlm.nih.gov`
# against `eutils.ncbi.nlm.nih.gov`, which is a real instrument repeat the ledger recorded by
# hand, and keeps the reader's judgement over `texas.gov`.
def shared_sources(history: list[dict], cand: dict | None, level: str = "hosts") -> list[dict]:
    """Addresses (or organisations) read by more than one deck, or by the candidate and a deck."""
    seen: dict = {}
    for row in history:
        for key in (row[level] or {}):
            seen.setdefault(key, []).append(row)
    out = []
    for key, rows in seen.items():
        by_cand = bool(cand and key in cand)
        if len(rows) < 2 and not by_cand:
            continue
        out.append({"site": key, "candidate": by_cand,
                    "decks": [{"date": r["date"], "n": (r[level] or {}).get(key, 0)}
                              for r in rows]})
    # NEWEST FIRST, NOT LONGEST FIRST. A source four decks in a row have read is a standing habit
    # of this project and a source YESTERDAY read is the one a reader is about to meet twice, so
    # the ordering is by the most recent deck on each row. Sorted by run length instead, the
    # nsf.gov pair two judges charged carousel 26 for sat seventh and off the end of the list,
    # under four older rows about legistar and the utility commission.
    out.sort(key=lambda r: r["site"])
    out.sort(key=lambda r: (r["candidate"], max(d["date"] for d in r["decks"]),
                            len(r["decks"])), reverse=True)
    return out


def print_source_report(history: list[dict], cand: dict | None, item: str | None) -> None:
    if not history:
        return
    unread = [r for r in history if r["hosts"] is None]
    known = [r for r in history if r["hosts"]]
    if not known:
        print("dedupe: no deck inside the window has a readable claims file, so the documents "
              "these decks read could not be compared. That is a gap, not a clean result.\n",
              file=sys.stderr)
        return
    print(f"WHAT KIND OF DOCUMENT THE LAST {len(known)} DECK(S) READ, out of each deck's own "
          f"claims file.\nThe beat above compares SUBJECT. This compares INSTRUMENT, which two "
          f"judges charged\ncarousel 26 for and which topics.json asked for at decks 17, 19, 23 "
          f"and 26.\n")
    for r in history[:6]:
        hosts = r["hosts"]
        if hosts is None:
            print(f"  {r['date']}  claims file not readable  {r['title']}")
            continue
        top = ", ".join(f"{s} ({n})" for s, n in
                        sorted(hosts.items(), key=lambda kv: -kv[1])[:3]) or "no source urls"
        print(f"  {r['date']}  {top}")
    strong = shared_sources(history, cand, "hosts")
    if strong:
        print("\n  THE SAME ADDRESS, READ BY MORE THAN ONE DECK:")
        for s in strong[:8]:
            who = ", ".join(f"{d['date']} ({d['n']})" for d in s["decks"])
            mark = "  <-- and by this candidate" if s["candidate"] else ""
            print(f"    {s['site']:<30} {who}{mark}")
    else:
        print("\n  No address in the window is read by two decks.")
    strong_names = {s["site"] for s in strong}
    weak = [s for s in shared_sources(history, as_sites(cand), "sites")
            if s["site"] not in strong_names]
    if weak:
        print("\n  THE SAME ORGANISATION AT DIFFERENT ADDRESSES, which is weaker evidence and is\n"
              "  here to be read rather than acted on. One state domain covers many bodies:")
        for s in weak[:5]:
            who = ", ".join(f"{d['date']} ({d['n']})" for d in s["decks"])
            mark = "  <-- and by this candidate" if s["candidate"] else ""
            print(f"    {s['site']:<30} {who}{mark}")
    if cand is None:
        why = (f", because {item} is not in the record" if item else ", because no --item was "
               "given")
        print(f"\n  THE CANDIDATE'S OWN DOCUMENTS WERE NOT COMPARED{why}. The window above is "
              f"what there was to read. Pass --item <docket id> and this names the decks that "
              f"read the same kind of document.")
    elif not cand:
        print("\n  The candidate's item carries no source url, so it has no instrument to "
              "compare.")
    if unread:
        print(f"\n  {len(unread)} deck(s) in the window have no readable claims file: "
              f"{', '.join(r['date'] for r in unread)}. A row that cannot be read is not a row "
              f"that agrees.")
    print("\n  AN INSTRUMENT IS NOT A REPEAT and this NEVER changes the exit code. A shared "
          "publisher is\n  evidence of a shared instrument, not proof: one host publishes a board "
          "presentation and a\n  market notice. And two studies at two publishers share no site "
          "at all, so this can miss.\n")


# --------------------------------------------------------------------------- the thirty day rule
#
# THE BINDING TIER, ADDED 2026-10-03 ON THE OWNER'S INSTRUCTION, AND IT REVERSES THIS FILE'S OLDEST
# ARGUMENT ON PURPOSE.
#
# Everything above prints and leaves the call to the showrunner, and carousel no. 41 is what that
# cost. It was Kodiak AI's Dallas to Houston lane seven days after carousel no. 34 was Kodiak AI's
# Dallas to Houston lane. The fingerprint read 0.50 against the 0.55 band, the run read the entry
# and chose the story anyway, two of three round 1 judges hard failed the thirty day window, and
# the deck shipped after five rounds with variety at 5.5. Measured afterwards, 12 of the 16 claims
# on its docket item cite an address no. 34 had already cited, and its decider is a company no. 34
# named, at places no. 34 named. Three facts the record already held, and nothing read them.
#
# The owner's answer was to make the thirty day rule strict. So a candidate is a REPEAT, exit 3,
# when a deck inside the window was built on
#
#   THE SAME ITEM       the candidate's own docket item
#   THE SAME DOCUMENTS  addresses that at least LIKELY of the candidate item's claims cite, read
#                       out of that deck's own committed claims file
#   THE SAME COMPANY    the company that decides the candidate's item, named by that deck, or a
#   AT THE SAME PLACE   company that decided that deck's item, named by the candidate, with a place
#                       the two share
#
# WHAT IT WAS MEASURED ON, BEFORE IT WAS TRUSTED. Every shipped deck, each against the decks in the
# thirty days before it, through this function, on the day it was written. It refuses two of forty
# one. No. 19 was built on the same Austin council item as no. 18 a day earlier, and no. 41 is the
# Kodiak pair. Both scored variety 5.5. The company rule fires on no. 41 alone, which the documents
# rule catches too, and it stays because it is the one that still fires when a company's next
# release is a new document about the same lane. The self-test replays both refusals and two
# passes against the committed ledgers.
#
# WHY A COMPANY AND NOT ANY DECIDER. The Public Utility Commission is named by ten decks, and two of
# its decisions about one county inside a month are two decisions. A company's own plan told twice
# in a month is one story. The decider's type is read off the record, so no list typed here decides
# who counts.
#
# WHY LIKELY AND NOT A NEW NUMBER. It is this file's own band for "over half in common". The two
# decks it refuses sit at 0.75 and 1.00 of their claims on a window deck's documents, and no other
# deck in the corpus comes above 0.12, so the band was not tuned to the answer.
#
# WHAT IT CAN'T SEE, said so the next reader does not assume it. A deck in the window with no
# readable claims file is not compared on documents, and it is named rather than counted as clean.
# A statewide item with no counties shares a place only through `--places`. A company named by a
# shorter name than the record's ("Oncor" against "Oncor Electric Delivery") is not matched, and the
# documents rule is what catches that pair.
GENERIC_ORG = {"inc", "llc", "corp", "corporation", "company", "ltd", "group", "holdings"}
NOT_A_PLACE = {"", "texas", "statewide"}


def doc_address(url: str) -> str | None:
    """One document's address: host without `www.`, path without a trailing slash, and the query.

    THE QUERY IS KEPT. Legistar serves every meeting from one path and tells them apart by `ID=`,
    and so do the NSF award search and the utility commission's filings. The first measurement of
    this rule dropped the query and refused three more decks (no. 6, no. 13 and no. 30), each of
    which had read a DIFFERENT filing or award at an address it shared with an earlier deck.
    """
    s = urlsplit(str(url).strip())
    if s.scheme not in {"http", "https"} or not s.netloc:
        return None
    host = s.netloc.lower().split(":")[0]
    host = host[4:] if host.startswith("www.") else host
    addr = host + s.path.rstrip("/")
    # ONLY THE HOST IS CASE FOLDED (Codex, PR 397). A path or a query value can be case sensitive,
    # so /Reports/ABC.pdf and /reports/abc.pdf, or ?id=AbC and ?id=abc, stay two documents.
    return addr + ("?" + s.query if s.query else "")


def _addresses(rows) -> list[str]:
    out = []
    for c in rows or []:
        if isinstance(c, dict):
            a = doc_address(str(c.get("url") or c.get("source_url") or ""))
            if a:
                out.append(a)
    return out


def deck_addresses(date: str, runs: Path | None = None) -> set[str] | None:
    """Every address a shipped deck's own claims file cites, or None if it can't be read."""
    try:
        raw = json.loads(((runs or RUNS) / date / "claims.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    rows = raw.get("claims") if isinstance(raw, dict) else raw
    return set(_addresses(rows)) if isinstance(rows, list) else None


def record_items() -> dict:
    """Docket item id to the item, or an empty map if the record can't be read."""
    try:
        raw = json.loads(DOCKET.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    items = raw.get("items") if isinstance(raw, dict) else raw
    return {str(i["id"]): i for i in items or [] if isinstance(i, dict) and i.get("id")}


def _name(n) -> frozenset:
    return frozenset(w for w in terms(str(n or "")) if w not in GENERIC_ORG)


COMPOUND = re.compile(r",|;|&|\band\b|\bwith\b", re.I)


def constituents(company: str | None) -> list[str]:
    """The organisations a decider names. The record carries compound deciders such as
    "Amazon.com, Inc. and Wiwynn Corporation", and a deck naming Amazon alone names one of them
    (Codex, PR 397). A fragment with no distinctive word, "Inc." here, is not an organisation."""
    return [p.strip() for p in COMPOUND.split(str(company or "")) if _name(p)]


def names_company(names, company: str | None) -> str | None:
    """The first of `names` that names one of `company`'s organisations in full, or None.

    IN FULL, ONE WAY. Every distinctive word of the organisation's name must be in the other name,
    so "Kodiak AI" matches "Kodiak AI" and a deck naming "Dallas" does not match a company called
    Dallas Anything.
    """
    for part in constituents(company):
        want = _name(part)
        for n in names or []:
            if want <= _name(n):
                return str(n)
    return None


def place_key(p) -> str:
    """'Dallas County' and 'Dallas' are one place for this purpose, and so are case and commas."""
    p = re.sub(r"[^a-z0-9 ]", " ", str(p or "").lower())
    return " ".join(re.sub(r"\bcounty\b", " ", p).split())


def _places(raw) -> set[str]:
    return {k for k in map(place_key, raw or []) if k not in NOT_A_PLACE}


def item_places(item: dict) -> set[str]:
    geo = item.get("geography") or {}
    raw = list(geo.get("counties") or []) if isinstance(geo, dict) else []
    if isinstance(geo, dict) and isinstance(geo.get("metro"), str):
        raw.append(geo["metro"])
    return _places(raw)


def company_of(item: dict) -> str | None:
    """The item's decider when the record types it a company, else None."""
    d = item.get("decider") or {}
    if isinstance(d, dict) and str(d.get("type") or "") == "company" and d.get("name"):
        return str(d["name"])
    return None


def thirty_day_rule(item_id: str, ref: _dt.date, ledger: dict, items: dict,
                    entities=(), places=(), runs: Path | None = None) -> dict:
    """The decks inside the window the candidate repeats, and the ones it could not be compared to.

    THE WINDOW EXCLUDES THE REFERENCE DATE ITSELF. A run that writes its own ledger entry and then
    checks again would otherwise find itself, on the same item, and refuse its own deck.
    """
    window = int(ledger.get("window_days") or 30)
    cand = items.get(item_id) or {}
    addrs = _addresses(cand.get("claims"))
    company = company_of(cand)
    cplaces = item_places(cand) | _places(places)
    cnames = [*entities, (cand.get("decider") or {}).get("name") or ""]
    out = {"repeats": [], "uncompared": [], "checked": 0}
    for e in ledger.get("entries") or []:
        date = str(e.get("date") or "")[:10]
        try:
            gap = (ref - _dt.date.fromisoformat(date)).days
        except ValueError:
            gap = None              # undated is inside, as `in_window` holds, so a bad date hides nothing
        if gap is not None and not 0 < gap <= window:
            continue
        out["checked"] += 1
        other = str(e.get("docket_item") or "")
        oitem = items.get(other) or {}
        why = []
        if other and other == item_id:
            why.append(f"the same docket item, {item_id}")
        seen = deck_addresses(date, runs) if gap is not None else None
        if seen is None:
            out["uncompared"].append(date or "undated")
        elif addrs:
            hit = [a for a in addrs if a in seen]
            if len(hit) / len(addrs) >= LIKELY:
                top = ", ".join(f"{a} ({n})" for a, n in Counter(hit).most_common(3))
                why.append(f"the same documents, {len(hit)} of the {len(addrs)} claims on {item_id} "
                           f"cite an address this deck cited: {top}")
        shared = sorted(cplaces & (item_places(oitem) | _places(e.get("places"))))
        if shared:
            ocompany = company_of(oitem)
            if company and names_company([*(e.get("entities") or []), ocompany or ""], company):
                why.append(f"the same company at the same place, {company} at {', '.join(shared)}")
            elif ocompany and names_company(cnames, ocompany):
                why.append(f"the same company at the same place, {ocompany} at {', '.join(shared)}")
        if why:
            out["repeats"].append({"date": date or "undated", "no": e.get("carousel_no"),
                                   "item": other or None,
                                   "title": (e.get("title") or e.get("topic") or "")[:70],
                                   "why": why})
    return out


def print_thirty_day(rule: dict, item: str) -> None:
    print(f"THE THIRTY DAY RULE, binding since 2026-10-03, for {item}. The same item, the same "
          f"documents, or\nthe same company at the same place, inside the window.\n")
    for r in rule["repeats"]:
        print(f"  REPEAT  {r['date']}  carousel no. {r['no']}  {r['title']}")
        for w in r["why"]:
            for line in _wrap(w, 84):
                print(f"          {line}")
    if rule["repeats"]:
        print("\n  PICK ANOTHER STORY. This is not a signal to read and weigh, and it is not the "
              "showrunner's call.\n  Carousel no. 41 read this gate's warning, chose the repeat, "
              "and spent five panel rounds on it.")
    else:
        print(f"  {item} clears it against the {rule['checked']} deck(s) in the window.")
    if rule["uncompared"]:
        print(f"\n  {len(rule['uncompared'])} deck(s) in the window have no readable claims file, "
              f"so their documents were not compared: {', '.join(rule['uncompared'])}. A row that "
              f"can't be read is not a row that agrees.")
    print()


def frames_on_told_items(copy: dict, claims, ledger: dict, ref: _dt.date,
                         items: dict | None = None) -> list[str]:
    """A BUILT deck whose close, or two or more of its frames, rests on a story the window told.

    Selection is where the rule is meant to bite. This is the backstop `panel_ready.py` runs before
    every panel round, for the material a run brings in AFTER selection. Carousel no. 41 picked a
    new item and then built frames 8 and 9 on tx-2026-0188, the item carousel no. 34 told a week
    before, and two judges hard failed it in round 1. One frame of context is allowed. The close,
    or a second frame, is the old story told again.

    A CLAIM IS TRACED TO A STORY TWO WAYS. By its own `docket_item` when it carries one, and
    otherwise by its address: a claim citing a document that the told item's record claims cite,
    and that no other item in the record cites, is that story's material. Three of the forty two claims
    files under runs/ carry `docket_item` and nothing requires it, so a check keyed on the field
    alone could not run on an ordinary deck. On no. 41's claims file the two ways agree claim for
    claim.

    ONE ITEM'S DOCUMENT, NEVER A HUB. The first cut traced by any address the told item cited, and
    replayed over every shipped deck it flagged carousel no. 24's close for citing the utility
    commission's meeting calendar, which carousel no. 3's item also cites and so do two other
    items. Judges scored no. 24's variety 7.8. A document three stories cite is a calendar, not a
    story, so an address is traced only when exactly one record item cites it. TxDMV's program
    page, which no. 41's round 1 close stood on, is cited by one.

    Replayed over every shipped deck with the hub rule, it flags one, carousel no. 9 on
    2026-08-27. Its close pointed the reader at the utility commission's comment window on Project
    58482, the item carousel no. 6 was built on five days earlier, which is no. 41's round 1 fault.
    """
    window = int(ledger.get("window_days") or 30)
    items = record_items() if items is None else items
    if not items:
        # FAIL CLOSED (Codex, PR 397). With no record, no claim without a docket_item can be traced,
        # and a comparison that never ran must not read as a deck that passed it.
        return [f"CANNOT RUN: {DOCKET} can't be read, so no frame could be traced to the story it "
                f"tells"]
    told, told_at = {}, {}
    cited_by = Counter(a for i in items.values() if isinstance(i, dict)
                       for a in set(_addresses(i.get("claims"))))
    for e in ledger.get("entries") or []:
        try:
            gap = (ref - _dt.date.fromisoformat(str(e.get("date") or "")[:10])).days
        except ValueError:
            continue
        it = str(e.get("docket_item") or "")
        if 0 < gap <= window and it and it not in told:
            told[it] = e
            for a in _addresses((items.get(it) or {}).get("claims")):
                if cited_by[a] == 1:
                    told_at.setdefault(a, it)
    of = {}
    for c in claims or []:
        if not isinstance(c, dict):
            continue
        own = str(c.get("docket_item") or "")
        addr = doc_address(str(c.get("url") or c.get("source_url") or "")) or ""
        of[str(c.get("id"))] = own or told_at.get(addr, "")
    slides = copy.get("slides") or {}
    keyed = slides.items() if isinstance(slides, dict) else enumerate(slides, 1)

    def frame_no(key, s) -> int:
        # `n` where the copy carries it. Decks before it carried one key their slides S1 to S9 or
        # name the file, and reading 0 for every frame made each one the close.
        for v in (s.get("n"), s.get("file"), key):
            m = re.search(r"\d+", str(v or ""))
            if m and int(m.group()):
                return int(m.group())
        return 0
    rows = [dict(s, n=frame_no(k, s)) for k, s in keyed if isinstance(s, dict)]
    nums = [s["n"] for s in rows]
    if not nums:
        return ["CANNOT RUN: copy.json carries no slides, so no frame's claims could be read"]
    if not of:
        return ["CANNOT RUN: claims.json carries no claims, so no frame could be traced to the "
                "story it tells"]
    last, hits = max(nums), {}
    for s in rows:
        if not isinstance(s, dict):
            continue
        for c in s.get("claims") or []:
            it = of.get(str(c))
            if it in told:
                hits.setdefault(it, set()).add(int(s.get("n") or 0))
    problems = []
    for it, frames in sorted(hits.items()):
        if len(frames) >= 2 or last in frames:
            e = told[it]
            where = ", ".join(str(n) for n in sorted(frames))
            close = " including the close" if last in frames else ""
            problems.append(f"frame(s) {where}{close} rest on {it}, the item carousel no. "
                            f"{e.get('carousel_no')} was built on, {e.get('date')}, inside the "
                            f"thirty day window. Replace that material. The rule is binding")
    return problems


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
        beat: str | None = None, entities=(), places=()) -> int:
    code = _report(cand_terms, ref, item, beat)
    # THE THIRTY DAY RULE, LAST, because it is the verdict and the run reads top down.
    try:
        ledger = json.loads(TOPICS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 2
    items = record_items()
    if not item or item not in items:
        why = (f"{item} is not in the record" if item and items else
               f"{DOCKET} can't be read" if item else "no --item was given")
        print(f"THE THIRTY DAY RULE WAS NOT CHECKED, because {why}. It compares the candidate's "
              f"own docket item,\nso pass --item with an admitted item. A rule that could not run "
              f"is not a rule that passed.", file=sys.stderr)
        return 2
    rule = thirty_day_rule(item, ref, ledger, items, entities, places)
    print_thirty_day(rule, item)
    return 3 if rule["repeats"] else code


def _report(cand_terms: set[str], ref: _dt.date, item: str | None = None,
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
    # THE INSTRUMENT, after the beat and before the fingerprint, because it is the question the
    # two above cannot answer and the run reads top down.
    print_source_report(source_history(ledger, ref), item_hosts(item) if item else None, item)
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
        print("\n  READ THAT ENTRY IN FULL before the directors room. This word fingerprint is a "
              "signal, not a verdict:\n  two different decisions can share every entity in Texas. "
              "The thirty day rule below is the verdict,\n  and it binds whatever this line says.")
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

    # ---- THE INSTRUMENT (2026-09-16) ----------------------------------------------------
    #
    # THE DISCRIMINATION FIRST, for the same reason the beat block above states it: a test whose
    # input cannot tell a working implementation from a broken one is measuring the agreement.
    # Carousel 11 and carousel 26 are the pair this exists for, and the point is that the WORD
    # comparison and the BEAT comparison both pass them.
    d11 = {"date": "2026-08-29", "carousel_no": 11, "docket_item": "tx-2026-0100",
           "title": "An NSF robotics award at UT Austin",
           "entities": ["The University of Texas at Austin", "National Science Foundation"],
           "keywords": ["robotics", "award abstract", "mobile manipulation"]}
    d26_terms = terms("The University of Texas at Arlington, Fort Worth Police Department, "
                      "Department of Justice",
                      "tutor, de-escalation, undergraduate courses, police training")
    lgi = {"window_days": 30, "entries": [d11]}
    refi = _dt.date(2026, 9, 16)
    ok("carousel 26 against carousel 11 is FAINT on words, which is the blindness this is for",
       (not compare(d26_terms, lgi, refi))
       or compare(d26_terms, lgi, refi)[0]["score"] < WORTH_READING, str(compare(d26_terms, lgi, refi)))

    ok("a subdomain and its parent are one site", registrable("api.nsf.gov") == "nsf.gov"
       and registrable("nsf.gov") == "nsf.gov")
    ok("...and two deep subdomains of one organisation are too",
       registrable("pmc.ncbi.nlm.nih.gov") == registrable("eutils.ncbi.nlm.nih.gov") == "nih.gov")
    ok("...and a two letter country code keeps three labels, so sos.state.tx.us is not tx.us",
       registrable("sos.state.tx.us") == "state.tx.us", registrable("sos.state.tx.us"))
    ok("...and a bare pair is itself", registrable("ercot.com") == "ercot.com")

    # AGAINST THE REAL SHIPPED CLAIMS FILES, because a fixture written beside a detector agrees
    # with it. Both decks' files are committed, so this runs in CI too, and the day a run writes
    # its claim urls under a different key this goes red instead of going quiet.
    real_ledger = {"window_days": 30, "entries": [
        {"date": "2026-08-29", "carousel_no": 11, "title": "carousel 11"},
        {"date": "2026-09-16", "carousel_no": 26, "title": "carousel 26"}]}
    hist = source_history(real_ledger, refi)
    ok("both shipped decks' claims files resolve to the documents they read",
       all(r["hosts"] for r in hist), str([(r["date"], r["hosts"] is None) for r in hist]))
    strong = shared_sources(hist, None, "hosts")
    ok("THE INSTRUMENT REPEAT TWO JUDGES NAMED IS FOUND: both decks read api.nsf.gov",
       any(s["site"] == "api.nsf.gov" and len(s["decks"]) == 2 for s in strong), str(strong))
    ok("...and the newest deck in the pair is named on the row",
       any(s["site"] == "api.nsf.gov" and "2026-09-16" in [d["date"] for d in s["decks"]]
           for s in strong), str(strong))

    # THE SECOND REAL INSTANCE, which the ledger recorded by hand at deck 23 and which is only
    # visible at the organisation level: two NCBI addresses, four days apart.
    nih = {"window_days": 30, "entries": [{"date": "2026-09-09"}, {"date": "2026-09-13"}]}
    weak = shared_sources(source_history(nih, _dt.date(2026, 9, 13)), None, "sites")
    ok("the clinical literature pair deck 23 wrote up by hand is found at the organisation level",
       any(s["site"] == "nih.gov" and len(s["decks"]) == 2 for s in weak), str(weak))
    ok("...and it is NOT claimed at the address level, because the two addresses differ",
       not any(s["site"].endswith("nih.gov") for s in
               shared_sources(source_history(nih, _dt.date(2026, 9, 13)), None, "hosts")))

    # TWO DECKS THAT SHARE NOTHING SHARE NOTHING. Without this the assertions above would pass on
    # an implementation that reported every pair as a repeat.
    apart = {"window_days": 30, "entries": [{"date": "2026-09-11"}, {"date": "2026-09-09"}]}
    ok("two decks with no source in common report no shared address",
       not shared_sources(source_history(apart, _dt.date(2026, 9, 13)), None, "hosts"),
       str(shared_sources(source_history(apart, _dt.date(2026, 9, 13)), None, "hosts")))

    # A DECK WHOSE CLAIMS FILE CANNOT BE READ KEEPS ITS ROW AND IS REPORTED, never dropped. A
    # silently shortened history is a count of the wrong set, which reads like a count of the
    # right one.
    # 2026-09-06 is inside the window and no deck shipped that day, so there is no run directory.
    missing = {"window_days": 30, "entries": [{"date": "2026-09-16"}, {"date": "2026-09-06"}]}
    hm = source_history(missing, refi)
    ok("a deck with no readable claims file keeps its row with hosts None",
       len(hm) == 2 and any(r["hosts"] is None for r in hm), str(hm))

    # THE CANDIDATE'S OWN DOCUMENTS, out of the record rather than out of a flag somebody types.
    cand_hosts = item_hosts("tx-2026-0161")
    ok("the candidate's own item resolves to the documents it stands on",
       bool(cand_hosts) and "uta.edu" in cand_hosts, str(cand_hosts))
    ok("an item the record does not hold reports None rather than an empty comparison",
       item_hosts("tx-9999-9999") is None)

    # ---- THE THIRTY DAY RULE (2026-10-03), BINDING ---------------------------------------
    #
    # AGAINST THE COMMITTED LEDGERS FIRST, because the pair this exists for is real. Carousel no. 41
    # was Kodiak AI's Dallas to Houston lane seven days after carousel no. 34, the fingerprint said
    # 0.50 and "worth reading", and the deck spent five panel rounds on the repeat.
    items = record_items()
    ok(f"the record resolves for the rule ({len(items)} item(s))", bool(items))
    led = real_t or {"window_days": 30, "entries": []}
    by_date = {str(e.get("date"))[:10]: e for e in led.get("entries") or []}
    e41 = by_date.get("2026-10-03", {})
    r41 = thirty_day_rule("tx-2026-0198", _dt.date(2026, 10, 3), led, items,
                          e41.get("entities") or [], e41.get("places") or [])
    vs34 = [r for r in r41["repeats"] if r["no"] == 34]
    ok("CAROUSEL NO. 41 IS REFUSED against carousel no. 34", bool(vs34), str(r41["repeats"]))
    ok("...on the same documents, the Kodiak release no. 34 had already cited",
       bool(vs34) and any("same documents" in w and "kodiak.ai/news" in w for w in vs34[0]["why"]),
       str(vs34))
    ok("...and on the same company at the same place, Kodiak AI on the lane",
       bool(vs34) and any("same company" in w and "Kodiak AI" in w for w in vs34[0]["why"]),
       str(vs34))
    bare = thirty_day_rule("tx-2026-0198", _dt.date(2026, 10, 3), led, items)
    ok("...and the company rule needs no --entities or --places, because the record carries both",
       any(r["no"] == 34 and any("same company" in w for w in r["why"]) for r in bare["repeats"]),
       str(bare["repeats"]))
    ok("the reference date is outside its own window, so a run that rechecks after writing its "
       "ledger entry does not refuse itself",
       not any(r["date"] == "2026-10-03" for r in r41["repeats"]), str(r41["repeats"]))
    e19 = by_date.get("2026-09-09", {})
    r19 = thirty_day_rule(str(e19.get("docket_item")), _dt.date(2026, 9, 9), led, items)
    ok("carousel no. 19, on the same Austin council item as no. 18 a day earlier, is refused",
       any(r["no"] == 18 and "the same docket item" in r["why"][0] for r in r19["repeats"]),
       str(r19["repeats"]))

    # THE DISCRIMINATION, because a rule that refused everything would pass every case above.
    # Carousel no. 40 is a Houston hospital study the day before no. 41. No. 37 is a utility
    # commission deck, and ten decks name the commission, which is why the company rule reads the
    # decider's TYPE and never a bare shared name.
    for d in ("2026-10-02", "2026-09-29"):
        e = by_date.get(d, {})
        r = thirty_day_rule(str(e.get("docket_item")), _dt.date.fromisoformat(d), led, items,
                            e.get("entities") or [], e.get("places") or [])
        ok(f"carousel no. {e.get('carousel_no')} ({d}) clears the rule", not r["repeats"],
           str(r["repeats"]))

    ok("a company is matched in full and one way, so a deck naming Dallas is not Dallas Widgets",
       names_company(["Dallas", "City of Dallas"], "Dallas Widgets LLC") is None
       and names_company(["Kodiak AI", "IKEA"], "Kodiak AI") == "Kodiak AI")
    ok("a county and its city are one place, and Texas is no place",
       place_key("Dallas County") == place_key("Dallas") == "dallas"
       and not _places(["Texas", "statewide"]))
    ok("an address keeps its query, so two council meetings at one path are two documents",
       doc_address("https://elpasotexas.legistar.com/MeetingDetail.aspx?ID=1")
       != doc_address("https://ElPasoTexas.legistar.com/MeetingDetail.aspx?ID=2")
       and doc_address("https://www.kodiak.ai/news/x/") == doc_address("http://kodiak.ai/news/x"))
    ok("only the host is case folded, so a case sensitive path or query is its own document "
       "(Codex, PR 397)",
       doc_address("https://Example.org/Reports/ABC.pdf") != doc_address("https://example.org/reports/abc.pdf")
       and doc_address("https://x.org/d?id=AbC") != doc_address("https://x.org/d?id=abc")
       and doc_address("https://WWW.Example.org/Reports/ABC.pdf") == doc_address("https://example.org/Reports/ABC.pdf"))
    ok("a compound decider is matched by any one of its organisations, and 'Inc.' is none",
       names_company(["Amazon.com"], "Amazon.com, Inc. and Wiwynn Corporation") == "Amazon.com"
       and constituents("Amazon.com, Inc. and Wiwynn Corporation") == ["Amazon.com", "Wiwynn Corporation"])
    ok("...and a deck naming neither organisation does not match it",
       names_company(["Microsoft", "Inc."], "Amazon.com, Inc. and Wiwynn Corporation") is None)
    ok("an unreadable record is a check that CANNOT RUN, never a clean one (Codex, PR 397)",
       any("CANNOT RUN" in p for p in frames_on_told_items(
           {"slides": {"S1": {"n": 1, "claims": ["c1"]}}}, [{"id": "c1", "url": "https://a.org/x"}],
           {"window_days": 30, "entries": []}, _dt.date(2026, 10, 3), items={})))
    fx_items = {"tx-1": {"decider": {"name": "Acme Freight", "type": "company"},
                         "geography": {"counties": ["Ector"]}, "claims": []}}
    fx = {"window_days": 30, "entries": [{"date": "2026-09-30", "carousel_no": 9,
                                          "docket_item": "tx-2", "entities": ["Acme Freight"],
                                          "places": ["Midland"]}]}
    ok("the same company at a DIFFERENT place is not a repeat",
       not thirty_day_rule("tx-1", _dt.date(2026, 10, 3), fx, fx_items, runs=Path("/nonexistent"))
       ["repeats"])
    fx["entries"][0]["places"] = ["Ector County"]
    ok("...and the same company at the same place is",
       bool(thirty_day_rule("tx-1", _dt.date(2026, 10, 3), fx, fx_items,
                            runs=Path("/nonexistent"))["repeats"]))
    ok("...and a window deck with no claims file is named as not compared, never counted clean",
       thirty_day_rule("tx-1", _dt.date(2026, 10, 3), fx, fx_items,
                       runs=Path("/nonexistent"))["uncompared"] == ["2026-09-30"])

    # THE BACKSTOP A BUILT DECK MEETS IN panel_ready.py. No. 41 picked a new item and then built
    # frames 8 and 9 on tx-2026-0188, no. 34's item, which two round 1 judges hard failed. The
    # committed claims file still carries those claims, so round 1's citations replay exactly.
    try:
        c41 = json.loads((RUNS / "2026-10-03" / "claims.json").read_text(encoding="utf-8"))["claims"]
        copy41 = json.loads((RUNS / "2026-10-03" / "copy.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError):
        c41, copy41 = None, None
    ok("no. 41's committed claims and copy resolve", bool(c41) and bool(copy41))
    if c41 and copy41:
        ref41 = _dt.date(2026, 10, 3)
        ok("the shipped deck, after its repair, rests on nothing the window told",
           not frames_on_told_items(copy41, c41, led, ref41),
           str(frames_on_told_items(copy41, c41, led, ref41)))
        r1 = json.loads(json.dumps(copy41))
        r1["slides"]["S8"]["claims"] = ["c33", "c34"]
        r1["slides"]["S9"]["claims"] = ["c35", "c36"]
        got = frames_on_told_items(r1, c41, led, ref41)
        ok("ROUND 1's frames 8 and 9 on TxDMV's authorization are CAUGHT before the panel",
           any("tx-2026-0188" in p and "no. 34" in p and "the close" in p for p in got), str(got))
        one = json.loads(json.dumps(copy41))
        one["slides"]["S4"]["claims"] = ["c2", "c33"]
        ok("...one middle frame of context is allowed",
           not frames_on_told_items(one, c41, led, ref41))
        close = json.loads(json.dumps(copy41))
        close["slides"]["S9"]["claims"] = ["c2", "c35"]
        ok("...and the close alone is not",
           bool(frames_on_told_items(close, c41, led, ref41)))
        ok("a copy with no slides is a check that CANNOT RUN, never a clean one",
           any("CANNOT RUN" in p for p in frames_on_told_items({"slides": {}}, c41, led, ref41)))
        bare41 = [{k: v for k, v in c.items() if k != "docket_item"} for c in c41]
        ok("...and round 1 is caught BY ADDRESS when the claims carry no docket_item, as 39 of "
           "the 42 claims files under runs/ don't",
           any("tx-2026-0188" in p for p in frames_on_told_items(r1, bare41, led, ref41)),
           str(frames_on_told_items(r1, bare41, led, ref41)))
        ok("...and the shipped deck is still clean that way",
           not frames_on_told_items(copy41, bare41, led, ref41))
        nless = json.loads(json.dumps(r1))
        for v in nless["slides"].values():
            v.pop("n", None)
        ok("a copy whose slides carry no `n` reads the frame from its key, so not every frame is "
           "the close", any("9 including the close" in p and "8" in p
                            for p in frames_on_told_items(nless, c41, led, ref41)),
           str(frames_on_told_items(nless, c41, led, ref41)))

    # A HUB IS NOT A STORY. Carousel no. 24's close cites the utility commission's meeting
    # calendar, which no. 3's item cites and two other items cite too. Its variety scored 7.8.
    try:
        c24 = json.loads((RUNS / "2026-09-14" / "claims.json").read_text(encoding="utf-8"))
        copy24 = json.loads((RUNS / "2026-09-14" / "copy.json").read_text(encoding="utf-8"))
        c9 = json.loads((RUNS / "2026-08-27" / "claims.json").read_text(encoding="utf-8"))
        copy9 = json.loads((RUNS / "2026-08-27" / "copy.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        c24 = copy24 = c9 = copy9 = None
    ok("no. 24's and no. 9's committed claims and copy resolve", bool(c24 and copy9))
    if c24 and copy24:
        rows24 = c24.get("claims") if isinstance(c24, dict) else c24
        ok("carousel no. 24's close on a calendar three items cite is NOT a told story",
           not frames_on_told_items(copy24, rows24, led, _dt.date(2026, 9, 14)),
           str(frames_on_told_items(copy24, rows24, led, _dt.date(2026, 9, 14))))
    if c9 and copy9:
        rows9 = c9.get("claims") if isinstance(c9, dict) else c9
        got9 = frames_on_told_items(copy9, rows9, led, _dt.date(2026, 8, 27))
        ok("carousel no. 9's close on no. 6's comment window five days later IS caught",
           any("tx-2026-0002" in p and "the close" in p for p in got9), str(got9))

    # WIRED, NOT ONLY DEFINED (GATE_LESSONS 14): the exit code a run reads.
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        code41 = run(terms("Kodiak AI, IKEA", "driverless, safety case"), _dt.date(2026, 10, 3),
                     "tx-2026-0198", None, ["Kodiak AI", "IKEA"], [])
        code_none = run(terms("Kodiak AI", "driverless"), _dt.date(2026, 10, 3))
    ok("run() exits 3 on carousel no. 41, which the routine treats as binding", code41 == 3,
       f"exit {code41}")
    ok("...and exits 2 without --item, because the rule could not run", code_none == 2,
       f"exit {code_none}")

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
    ap.add_argument("--places", default="", help="places the candidate is about, comma "
                                                 "separated, beyond its item's own counties")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    ref = _dt.date.fromisoformat(a.date) if a.date else _dt.date.today()
    split = lambda s: [x.strip() for x in s.split(",") if x.strip()]   # noqa: E731
    return run(terms(a.entities, a.keywords, a.desc), ref, a.item, a.beat,
               split(a.entities), split(a.places))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"dedupe_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
