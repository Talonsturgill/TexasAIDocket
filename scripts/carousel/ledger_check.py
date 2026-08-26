#!/usr/bin/env python3
"""ledger_check.py — the variety ledgers are DERIVED, so they are re-derived and compared.

WHY THIS EXISTS. 2026-08-26, and it is the third time.

The 2026-08-25 run recut its headline count from eight to seven when a director proved the
Texas Water Development Board's action was a petition denial rather than a restriction. Every
reader-facing surface was regenerated. The DURABLE MEMORY was not, and two scorers found it:

    ledger/carousel/topics.json   "the eight Texas governmental bodies that restricted a data
                                  center", "Two of the eight say ... on the other four the
                                  record says nothing" — against a run that computed 7, 5, 2, 0
    ledger/carousel/captions.json critic_note "widens to the eight"

The same round found all three caption exclusion lists disagreeing with the entries in the file
that holds them, wrong in BOTH directions:

    opening_moves_recent  held 'the quiet decision', in no entry; dropped 'the object', 2026-08-16
    structures_recent     held 'zoom out', in no entry;            dropped 'question and answer'
    closing_moves_recent  held a move last used 2026-08-19, outside a window of three

That is not cosmetic. Those three lists are what the caption room is handed BEFORE it writes, and
the room was told that 'the quiet decision', 'zoom out' and 'ask the one question the decision
leaves open' were off the table. It wrote all three anyway and coined freehand names for them,
which cleared the lists because a list can only exclude a name it shares. So the corruption did
not merely fail to prevent a repeat. It manufactured three new move names that are on none of
CAPTION_CRAFT.md's menus, which is how the next run's list gets corrupt too.

WHAT IT CHECKS

1. Every entry's `opening_move`, `structure` and `closing_move` is a name CAPTION_CRAFT.md
   actually carries. Freehand names are the mechanism, so they are the thing to refuse.
2. The three `*_recent` lists equal what the entries derive, at the window lengths the doctrine
   states. Derived data that is also stored is data that will disagree with itself.
3. Every spelled-out count in the newest topics entry's `topic` and `angle` prose is a value the
   run actually computed. Prose beside a number is where the recut goes stale.
4. No ledger carries two entries for one date. A writer that appends produces a duplicate the
   moment it re-runs, and `recent` windows then read the stale one last.

It reads the DOCTRINE for the menus rather than keeping its own copy, because a gate with its own
copy of a list is the defect it is here to catch.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIGHT_L = 60.0      # deck median L* at or above which a deck reads light
LIGHT_CAP = 1       # brand.yaml: at most once per eight runs
DOCTRINE = "knowledge/carousel/CAPTION_CRAFT.md"

# The counts the topic prose is ABOUT. A number word in that prose has to be one of these, not
# merely some figure the run computed: `brazoria_applications` is 4, and without this scoping
# "on the other four the record says nothing either way" would pass while being false.
COUNTING_FIGURES = ("restricted_count", "declined_count", "total_count", "stated_nonbinding",
                    "stated_binding", "force_unstated", "distinct_shapes", "late_cluster",
                    "acting_bodies", "repeat_bodies", "busiest_body_count",
                    "busiest_body_binding", "busiest_month_count")
WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def menus(text: str) -> dict[str, set[str]]:
    """Opening moves, structures and closing moves, read off the doctrine's own markdown."""
    def section(name: str) -> str:
        m = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
        return m.group(1) if m else ""
    opens = {m.group(1).strip().lower()
             for m in re.finditer(r"^\|\s*\*\*(.+?)\*\*\s*\|", section("Opening moves"), re.M)}
    structs = {m.group(1).strip().lower()
               for m in re.finditer(r"^-\s*\*\*(.+?)\.\*\*", section("Structures"), re.M)}
    closes = {m.group(1).strip().rstrip(".").lower()
              for m in re.finditer(r"^-\s+(.+)$", section("Closing moves"), re.M)}
    return {"opening_move": opens, "structure": structs, "closing_move": closes}


def norm(s: str) -> str:
    return (s or "").strip().rstrip(".").lower()


def on_menu(value: str, names: set[str]) -> bool:
    """Exact, or an unambiguous prefix of one menu entry.

    The closing moves are SENTENCES ("Stop on the strongest fact, with no wrap-up at all. This is
    often the best one."), and a ledger sensibly stores the head of one. A prefix of twelve or
    more characters that matches exactly one menu entry is that entry. Anything shorter, or
    matching two, is a freehand name and is refused: 'the procedural fact nobody expects' is a
    prefix of nothing.
    """
    if value in names:
        return True
    if len(value) < 12:
        return False
    return len([n for n in names if n.startswith(value)]) == 1


# `one` is a pronoun far more often than it is a count. "any one of them", "every one of the
# seven" and "the one that binds" are all English rather than arithmetic, and a gate that reads
# them as counts fires on correct prose, which is a gate somebody switches off.
PRONOUN_ONE = re.compile(r"\b(any|each|every|no|some|this|that|the|which|than|only)\s+one\b", re.I)


def check_captions(cap: dict, menu: dict[str, set[str]]) -> list[str]:
    problems: list[str] = []
    entries = sorted(cap.get("entries", []), key=lambda e: e["date"])
    seen: dict[str, int] = {}
    for e in entries:
        seen[e["date"]] = seen.get(e["date"], 0) + 1
    for d, n in seen.items():
        if n > 1:
            problems.append(f"captions.json carries {n} entries dated {d}. A ledger writer that "
                            f"appends duplicates the moment it re-runs, and the recent windows "
                            f"then read the stale one last")
    for e in entries:
        for field, names in menu.items():
            v = norm(e.get(field))
            if not v:
                problems.append(f"captions.json {e['date']} has no {field}")
            elif not on_menu(v, names):
                problems.append(
                    f"captions.json {e['date']} {field} {e[field]!r} is on no {DOCTRINE} menu. A "
                    f"freehand name cannot be excluded by a list of real ones, which is how three "
                    f"excluded moves shipped on 2026-08-25")
    if not entries:
        return problems
    newest = entries[-1]["date"]
    prior = [e for e in entries if e["date"] < newest]
    want = {"opening_moves_recent": [e["opening_move"] for e in prior[-6:]],
            "structures_recent":    [e["structure"]    for e in prior[-3:]],
            "closing_moves_recent": [e["closing_move"] for e in prior[-3:]]}
    for key, expect in want.items():
        got = cap.get(key)
        if got != expect:
            extra = [x for x in (got or []) if x not in expect]
            missing = [x for x in expect if x not in (got or [])]
            problems.append(
                f"captions.json {key} disagrees with its own entries. It holds {got!r} and the "
                f"entries derive {expect!r}"
                + (f". {extra!r} appears in no entry" if extra else "")
                + (f". {missing!r} is in an entry and is not listed" if missing else ""))
    return problems


def check_register(art: dict) -> list[str]:
    """THE LIGHT DECK CAP, COUNTED RATHER THAN ASSERTED.

    `config/brand.yaml` reads: "Big Bend at dusk is the default. A light deck is allowed as a
    deliberate high-variance move, at most once per eight runs, and the ledger enforces the
    count." The ledger did not. Every `light_decks_used` value in `artwork.json` reads the
    literal 1 while meaning light FRAMES inside a deck, which is a different quantity from the
    one brand.yaml says is being counted, so the field looked like enforcement and enforced
    nothing.

    Measured off the shipped PNGs on 2026-08-26: 08-18 at deck median L* 82.7, 08-20 at 85.5 and
    08-26 at 86.7, three light decks inside an eight run window against a cap of one. Two of
    those three had already shipped before anyone counted.

    This is GATE_LESSONS' own recurring shape, a rule stated in config with a ledger field that
    appears to enforce it and nothing in between checking they measure the same thing, and it is
    why the count comes from `value.deck_median_L`, which is measured off the render, rather than
    from any field a run writes about itself.
    """
    problems: list[str] = []
    entries = sorted(art.get("entries", []), key=lambda e: e.get("date", ""))
    window = entries[-8:]
    light = [e for e in window
             if isinstance(e.get("value"), dict)
             and isinstance(e["value"].get("deck_median_L"), (int, float))
             and e["value"]["deck_median_L"] >= LIGHT_L]
    unmeasured = [e["date"] for e in window
                  if not (isinstance(e.get("value"), dict)
                          and isinstance(e["value"].get("deck_median_L"), (int, float)))]
    # THE MEASUREMENT IS NEW, SO THE CAP BINDS FROM WHERE IT EXISTS. Backfilling a measured
    # field into already published entries would be editing the durable memory to suit a check
    # written after them, which is the one thing an append only ledger is for refusing. The
    # entries without it are NOTED and not failed, and the note disappears on its own as eight
    # measured runs accumulate. What is never softened is the count itself, below.
    if unmeasured:
        print(f"  note  the light deck cap is counted over the {len(window) - len(unmeasured)} "
              f"entr(y/ies) carrying a measured deck_median_L. {len(unmeasured)} older "
              f"entr(y/ies) predate the measurement and are not counted: "
              f"{', '.join(unmeasured)}")
    if len(light) > LIGHT_CAP:
        problems.append(
            f"artwork.json: {len(light)} light deck(s) in the last {len(window)} runs "
            f"({', '.join(e['date'] + ' at L* ' + str(e['value']['deck_median_L']) for e in light)}) "
            f"against brand.yaml's cap of {LIGHT_CAP} per eight. Measured off the render, not "
            f"asserted by the run")
    return problems


def check_topics(top: dict, figures: dict | None) -> list[str]:
    problems: list[str] = []
    entries = sorted(top.get("entries", []), key=lambda e: e["date"])
    seen: dict[str, int] = {}
    for e in entries:
        seen[e["date"]] = seen.get(e["date"], 0) + 1
    for d, n in seen.items():
        if n > 1:
            problems.append(f"topics.json carries {n} entries dated {d}")
    if not entries or figures is None:
        return problems
    ok = {figures[k]["value"] for k in COUNTING_FIGURES if k in figures}
    allowed = {WORDS[v] for v in ok if 0 <= v < len(WORDS)}
    newest = entries[-1]
    for field in ("topic", "angle"):
        prose = newest.get(field) or ""
        masked = PRONOUN_ONE.sub(lambda m: m.group(0)[:-3] + "___", prose)
        for m in re.finditer(r"\b(" + "|".join(WORDS) + r")\b", masked, re.I):
            w = m.group(1).lower()
            if w not in allowed:
                problems.append(
                    f"topics.json {newest['date']} {field} says {w!r} and the run computed "
                    f"{sorted(ok)} for the counts that prose is about. A recut regenerates the "
                    f"deck and leaves the durable memory narrating the old number")
    return problems


def run(cap: dict, top: dict, figures: dict | None, doctrine: str,
        art: dict | None = None) -> list[str]:
    out = check_captions(cap, menus(doctrine)) + check_topics(top, figures)
    if art is None:
        f = REPO_ROOT / "ledger" / "carousel" / "artwork.json"
        art = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    return out + check_register(art)


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            fails += 1

    doc = (REPO_ROOT / DOCTRINE).read_text(encoding="utf-8")
    M = menus(doc)
    ok("the doctrine's ten opening moves are read off the doctrine", len(M["opening_move"]) == 10,
       str(sorted(M["opening_move"])))
    ok("...its eight structures too", len(M["structure"]) == 8, str(sorted(M["structure"])))
    ok("...and its five closing moves", len(M["closing_move"]) == 5, str(sorted(M["closing_move"])))

    base = {"entries": [
        {"date": "2026-08-20", "opening_move": "the plain question", "structure": "question and answer",
         "closing_move": "name what happens next and when"},
        {"date": "2026-08-21", "opening_move": "the before and after", "structure": "clock",
         "closing_move": "point at the record, plainly, without a call to action"},
        {"date": "2026-08-22", "opening_move": "the deadline", "structure": "zoom in",
         "closing_move": "name what is still not public, and how big that is"},
        {"date": "2026-08-25", "opening_move": "the quiet decision", "structure": "zoom out",
         "closing_move": "ask the one question the decision leaves open"}]}
    good = dict(base,
                opening_moves_recent=["the plain question", "the before and after", "the deadline"],
                structures_recent=["question and answer", "clock", "zoom in"],
                closing_moves_recent=["name what happens next and when",
                                      "point at the record, plainly, without a call to action",
                                      "name what is still not public, and how big that is"])
    ok("a ledger whose lists match its entries passes", not check_captions(good, M),
       str(check_captions(good, M)))

    # THE 2026-08-25 DEFECT, both directions.
    bad = json.loads(json.dumps(good))
    bad["structures_recent"] = ["zoom out", "zoom in", "clock"]
    p = check_captions(bad, M)
    ok("a list holding a move that is in no entry FAILS", any("structures_recent" in x for x in p))
    ok("...and the report names the move that appears in no entry",
       any("zoom out" in x and "no entry" in x for x in p), str(p))
    ok("...and names the one that is in an entry and unlisted",
       any("question and answer" in x for x in p), str(p))

    free = json.loads(json.dumps(good))
    free["entries"][-1]["opening_move"] = "the procedural fact nobody expects"
    p = check_captions(free, M)
    ok("a freehand move name that is on no menu FAILS",
       any("on no" in x and "procedural fact" in x for x in p), str(p))

    dup = json.loads(json.dumps(good))
    dup["entries"].append(json.loads(json.dumps(dup["entries"][-1])))
    ok("two entries for one date FAIL",
       any("2 entries dated" in x for x in check_captions(dup, M)))

    # TOPICS. The eight that stayed after the run recut to seven.
    figs = {"restricted_count": {"value": 7}, "declined_count": {"value": 3},
            "total_count": {"value": 10}, "stated_nonbinding": {"value": 5},
            "stated_binding": {"value": 2}, "force_unstated": {"value": 0},
            "distinct_shapes": {"value": 7}, "late_cluster": {"value": 3},
            "brazoria_applications": {"value": 4}}
    t_ok = {"entries": [{"date": "2026-08-25",
                         "topic": "the seven Texas governmental bodies that acted on a data center",
                         "angle": "Five of the seven stop nothing and two changed a legal state"}]}
    ok("topic prose whose counts the run computed passes", not check_topics(t_ok, figs),
       str(check_topics(t_ok, figs)))
    t_bad = {"entries": [{"date": "2026-08-25",
                          "topic": "the eight Texas governmental bodies that restricted a data center",
                          "angle": "Two of the eight say they stop nothing and on the other four "
                                   "the record says nothing either way"}]}
    p = check_topics(t_bad, figs)
    ok("the stale 'eight' FAILS", any("'eight'" in x for x in p), str(p))
    ok("...and so does 'four', which IS a computed figure but not one of these counts",
       any("'four'" in x for x in p), str(p))
    ok("...reported on both the topic and the angle",
       any("topic says" in x for x in p) and any("angle says" in x for x in p), str(p))

    ok("a closing move stored as the head of the doctrine's sentence is accepted",
       on_menu("stop on the strongest fact", M["closing_move"]))
    ok("...while a freehand name that prefixes nothing is not",
       not on_menu("the procedural fact nobody expects", M["opening_move"]))
    ok("...and a prefix too short to be unambiguous is not",
       not on_menu("stop on", M["closing_move"]))
    t_pron = {"entries": [{"date": "2026-08-25",
                           "topic": "taken as a pattern rather than as any one of them",
                           "angle": "the record speaks to force on every one of the seven"}]}
    ok("'any one' and 'every one' are read as English, not as a count",
       not check_topics(t_pron, figs), str(check_topics(t_pron, figs)))
    t_count = {"entries": [{"date": "2026-08-25", "topic": "x",
                            "angle": "nine of the seven changed a legal state"}]}
    ok("...while a bare count that the run did not compute still FAILS",
       any("'nine'" in x for x in check_topics(t_count, figs)))

    print("\nledger_check self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="run date, to read out/<date>/figures.json")
    ap.add_argument("--ledger-dir", default="ledger/carousel")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    d = REPO_ROOT / a.ledger_dir
    cp, tp = d / "captions.json", d / "topics.json"
    for p in (cp, tp):
        if not p.exists():
            print(f"ledger_check: {p} does not exist", file=sys.stderr)
            return 2
    figures = None
    if a.date:
        fp = REPO_ROOT / "out" / a.date / "figures.json"
        if not fp.exists():
            fp = REPO_ROOT / "runs/carousel" / a.date / "figures.json"
        if not fp.exists():
            print(f"ledger_check: --date {a.date} was given and no figures.json was found for it. "
                  f"The topic prose check needs the run's computed counts", file=sys.stderr)
            return 2
        figures = json.loads(fp.read_text(encoding="utf-8"))

    problems = run(json.loads(cp.read_text(encoding="utf-8")),
                   json.loads(tp.read_text(encoding="utf-8")),
                   figures, (REPO_ROOT / DOCTRINE).read_text(encoding="utf-8"))
    if problems:
        print(f"ledger_check: {len(problems)} problem(s)\n", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        print("\n  These lists and this prose are DERIVED. Recompose them from the entries and "
              "from figures.json rather than editing them beside it.", file=sys.stderr)
        return 1
    print("ledger_check: the variety ledgers agree with their own entries and with the run's "
          "computed counts")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"ledger_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
