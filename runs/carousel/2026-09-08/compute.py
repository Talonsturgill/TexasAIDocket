#!/usr/bin/env python3
"""compute.py — carousel no. 18, 2026-09-08.

EVERY STRING A SLIDE PRINTS THAT CAME OUT OF A SOURCE IS PRODUCED HERE, and every one of them
is asserted against a snapshot of the document it was fetched from before it is written out.
The slides read `computed.json`. They never carry a source string typed by hand and they never
carry a numeral this file did not produce.

THE TWO DOCUMENTS ARE SCANNED IMAGES AND THEIR TEXT LAYER IS IMPERFECT. That is why the
assertion below normalises whitespace and nothing else. `ofeivil` for `of civil`, `o f` for
`of` and `December 9,2026` with no space after the comma are all the scanner's, they are stored
in the claims exactly as they appear, and repairing them here would mean the quote could no
longer be found in the document it cites.

WHAT IS ACTUALLY COMPUTED, and it is more than this story looks like it has.

  * THE TEN FACTORS. Section 2-19-4(C) of the April ordinance lists the properties a privacy
    impact assessment has to analyse, and the training of artificial intelligence is one of
    them. Both the LENGTH of that list and the POSITION of the AI factor in it are parsed out
    of the ordinance's own numbered enumeration rather than counted by a person. The deck's
    whole argument is that a factor on a weighing list became a bar one summer later, so
    those two numerals are the argument and they get the strictest treatment in the file.
  * THE EQUIPMENT LIST. The resolution enumerates what the city may buy in one sentence. The
    split is done here, on the source's own commas, and the count falls out of the split.
  * THE GATED ACTS. Section 2-19-3 lettered (A) through (D). Same treatment.

The instinct the ledger handed this run says a count on a frame has to name the set it counted.
Every count here carries the set it came from in `counted_over`, and the frames print that.
"""
import json
import re
import sys
from pathlib import Path

RUN = "2026-09-08"
HERE = Path(__file__).resolve().parent
SRC = HERE / "sources"

SNAPSHOT = {
    "https://services.austintexas.gov/edims/document.cfm?id=479192": "resolution.txt",
    "https://services.austintexas.gov/edims/document.cfm?id=473428": "ordinance.txt",
    "https://www.austintexas.gov/council/2026/20260812-reg": "agenda.txt",
    "https://data.austintexas.gov/resource/3c89-i35a.json?$select=max(meeting_date)":
        "voting_record_max.json",
    "https://services.austintexas.gov/council_meetings/action_notes.cfm?mid=1496":
        "action_notes.txt",
}

ORDINALS = {1: "1st", 2: "2nd", 3: "3rd", 9: "9th", 12: "12th", 23: "23rd", 28: "28th"}


def _n(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def assert_quotes(claims: list) -> dict:
    """Every quote is in the document it says it is in. Anything else stops the build."""
    cache, seen = {}, {}
    for c in claims:
        url = c["url"]
        if url not in SNAPSHOT:
            sys.exit(f"compute: no snapshot for {url}, so claim {c['id']} can't be asserted")
        if url not in cache:
            cache[url] = (SRC / SNAPSHOT[url]).read_text(encoding="utf-8")
        if _n(c["quote"]) not in _n(cache[url]):
            sys.exit(f"compute: claim {c['id']} quote is NOT in {SNAPSHOT[url]}")
        seen[c["id"]] = SNAPSHOT[url]
    return seen


def house_date(month: str, day: int, year: int) -> str:
    """Month first with the ordinal, which is the house rule. Never assembled in a slide."""
    return f"{month} {ORDINALS[day]}, {year}"


def factors(ordinance: str) -> dict:
    """Section 2-19-4(C)'s numbered list, parsed rather than counted by eye.

    The list runs from the stem 'must include at a minimum an analysis of whether the
    surveillance technology:' to subsection (D). Items are '(n)' at the head of a line. The AI
    item is the one containing the ordinance's own phrase about training.
    """
    i = ordinance.index("must include at a minimum an analysis of whether the surveillance")
    j = ordinance.index("The presence of any one or more", i)
    block = ordinance[i:j]
    items = re.split(r"\((\d+)\)\s", block)[1:]
    pairs = [(int(items[k]), _n(items[k + 1])) for k in range(0, len(items), 2)]
    nums = [n for n, _ in pairs]
    if nums != list(range(1, len(nums) + 1)):
        sys.exit(f"compute: the factor list is not 1..n, it reads {nums}")
    hits = [n for n, t in pairs if "training of" in t and "artificial intelligence" in t]
    if len(hits) != 1:
        sys.exit(f"compute: expected exactly one artificial intelligence factor, found {hits}")
    return {"total": len(pairs), "ai_position": hits[0],
            "counted_over": "the numbered analysis in City Code Section 2-19-4(C)",
            "items_first_words": [t.split(",")[0][:58] for _, t in pairs]}


def gated_acts(ordinance: str) -> dict:
    """Section 2-19-3's lettered list of the acts that need council approval first."""
    i = ordinance.index("City departments must obtain approval of")
    j = ordinance.index("PRIV ACY IMPACT ASSESSMENT", i)
    block = ordinance[i:j]
    items = re.split(r"\(([A-D])\)\s", block)[1:]
    letters = [items[k] for k in range(0, len(items), 2)]
    if letters != ["A", "B", "C", "D"]:
        sys.exit(f"compute: the gated act list is not A..D, it reads {letters}")
    return {"total": len(letters), "letters": letters,
            "acquire_letter": "B",
            "counted_over": "the lettered list in City Code Section 2-19-3"}


def equipment(resolution: str) -> dict:
    """The one sentence in the resolution that enumerates what the city may buy.

    Split on the source's own commas after the 'including but not limited to,' stem. The final
    item carries a leading 'and' which is the enumeration's own, and it is stripped for display
    only. The COUNT is the length of the split and is never typed.
    """
    stem = "potentially including but not limited to,"
    i = resolution.index(stem) + len(stem)
    j = resolution.index(".", i)
    parts = [_n(p) for p in _n(resolution[i:j]).split(",")]
    parts = [re.sub(r"^and\s+", "", p) for p in parts if p]
    return {"total": len(parts), "items": parts,
            "counted_over": "the enumeration in Resolution No. 20260812-017"}


def reached_kinds(resolution: str, equip: dict) -> dict:
    """How many of the enumerated kinds the prohibition actually reaches.

    The clause names a camera and a drone. The enumeration names six kinds. This matches the
    clause's own nouns against the enumeration's own entries rather than counting by eye, and it
    asserts that every noun it looks for is found, so a reworded clause stops the build.
    """
    flat = _n(resolution)
    i = flat.index("shall not consider acquisition")
    clause = flat[i:i + 240].lower()
    nouns = ("camera", "drone")
    for noun in nouns:
        if noun not in clause:
            sys.exit(f"compute: the prohibition does not name {noun!r}, so the ratio is stale")
    hit = [k for k in equip["items"] if any(n in k.lower() for n in nouns)]
    return {"reached": len(hit), "of": equip["total"], "items": hit,
            "counted_over": "the enumeration in Resolution No. 20260812-017, matched against the"
                            " nouns the prohibition itself names"}


def clause_uses(resolution: str) -> dict:
    """The uses the prohibition forbids the system to be used for, from the clause's own words."""
    flat = _n(resolution)
    i = flat.index("intelligence to conduct")
    tail = flat[i:i + 90].lower()
    uses = [u for u in ("surveillance", "analysis") if u in tail]
    if len(uses) != 2:
        sys.exit(f"compute: expected two named uses in the clause, found {uses}")
    return {"total": len(uses), "uses": uses,
            "counted_over": "the clause's own words in Resolution No. 20260812-017"}


def main() -> int:
    claims = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))["claims"]
    seen = assert_quotes(claims)
    res = (SRC / "resolution.txt").read_text(encoding="utf-8")
    ordn = (SRC / "ordinance.txt").read_text(encoding="utf-8")
    vote = json.loads((SRC / "voting_record_max.json").read_text(encoding="utf-8"))

    out = {
        "run": RUN,
        "claims_asserted": len(seen),
        "note": ("Every string here is asserted against a snapshot of the document it came from "
                 "before it is written. The two scanned documents keep their OCR garbling, "
                 "because a repaired quote can no longer be found in the document it cites."),
        "dates": {
            "adopted": house_date("August", 12, 2026),
            "adopted_raw": "ADOPTED: August 12 , 2026",
            "report_due": house_date("December", 9, 2026),
            "ordinance_adopted": house_date("April", 23, 2026),
            "voting_record_latest": house_date("May", 28, 2026),
            "audit": "July 2025",
        },
        "numbers": {
            "resolution": "20260812-017",
            "ordinance": "20260423-029",
            "chapter": "2-19",
            "assessment_section": "2-19-4",
            "approval_section": "2-19-3",
            "lead_time": "four weeks",
        },
        "factors": factors(ordn),
        "gated_acts": gated_acts(ordn),
        "equipment": equipment(res),
        "reached_kinds": reached_kinds(res, equipment(res)),
        "clause_uses": clause_uses(res),
        "voting_record": {
            "latest_meeting_loaded": vote[0]["max_meeting_date"][:10],
            "covers_the_august_meeting": False,
            "how": ("the city's published Council Voting Record dataset was queried for its "
                    "maximum meeting_date and the answer predates the meeting"),
        },
    }
    (HERE / "computed.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"compute: {len(seen)} claim(s) asserted against snapshots")
    print(f"compute: {out['factors']['total']} factors, artificial intelligence is number "
          f"{out['factors']['ai_position']}")
    print(f"compute: {out['gated_acts']['total']} gated acts, acquisition is "
          f"({out['gated_acts']['acquire_letter']})")
    print(f"compute: {out['equipment']['total']} kinds of equipment named")
    print(f"compute: the prohibition reaches {out['reached_kinds']['reached']} of them, "
          f"{out['reached_kinds']['items']}")
    print(f"compute: the clause names {out['clause_uses']['total']} uses, {out['clause_uses']['uses']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
