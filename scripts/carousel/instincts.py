#!/usr/bin/env python3
"""instincts.py — the machine's craft memory, where confidence is earned rather than claimed.

WHY THIS EXISTS, AND WHY IT IS NOT A PORT

The retro phase writes down what a run learned about making decks, and the next run's directors
room is handed the lessons that have earned their place. That much is the sibling's design and it
works.

What is not carried over is letting the model write the confidence number.

Look at the sibling's ledger. 101 entries. Forty-seven of them sit at 0.90 confidence, eight at
1.00. **Twenty-five entries have ever been confirmed even once.** The arithmetic only goes one
way: those numbers were typed at the moment the lesson was written, by the same model that had
just decided the lesson was worth writing. A machine allowed to grade its own lesson grades it
high, and then that number decides which lessons reach the next run's prompt.

That is the compute-not-generate law with a hole in it, in the one file that shapes how every
future deck gets made.

**So an entry here may not carry a confidence number at all.** It records what happened: the dates
it was confirmed and the dates it was contradicted. Confidence is derived from those events by
Laplace's rule of succession, and a hand-written confidence field is a hard fail on load.

    (confirmations + 1) / (confirmations + contradictions + 2)

A new instinct scores 0.5, which is the honest score for a lesson nothing has tested. Three clean
confirmations reach 0.8. The 0.7 injection bar therefore means "survived three runs", not "claimed
to matter". The rule is Laplace, 1774, an external standard rather than a number measured from our
own history, because a threshold derived from lessons we already believe would confirm whatever we
happened to write first.

    instincts.py --add --id palette-from-region --instinct "..." --evidence "..."
    instincts.py --confirm palette-from-region --date 2026-08-13
    instincts.py --contradict palette-from-region --date 2026-08-14
    instincts.py --top 5
    instincts.py --prune
    instincts.py --self-test

Exit 0 fine, 1 the ledger is malformed, 2 the tool could not run.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "carousel" / "instincts.json"

# The bar an instinct clears to be handed to the next run's directors room. Under the rule of
# succession this is three confirmations with no contradiction, which is a described event rather
# than a chosen number: it is what "0.7" MEANS here, not a dial anyone tuned.
INJECT_AT = 0.7
INJECT_TOP = 5

# Below this many tests, an instinct has not been tried enough to retire on the evidence.
MIN_TESTS_TO_RETIRE = 3

# Fields a model must never write. `confidence` is the whole point of this file. `score` and
# `weight` are the names it reaches for next once `confidence` is refused, which is worth
# refusing in advance rather than discovering in six months.
FORBIDDEN = ("confidence", "score", "weight", "strength", "certainty", "priority")

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def confidence(entry: dict) -> float:
    """Laplace's rule of succession over the entry's own event record."""
    c = len(entry.get("confirmed") or [])
    x = len(entry.get("contradicted") or [])
    return (c + 1) / (c + x + 2)


def tests(entry: dict) -> int:
    return len(entry.get("confirmed") or []) + len(entry.get("contradicted") or [])


def validate(doc: dict) -> list[str]:
    """Refuse a ledger that carries a claimed confidence, or a malformed entry."""
    problems = []
    entries = doc.get("entries")
    if not isinstance(entries, list):
        return ["the ledger has no `entries` list"]

    seen = set()
    for i, e in enumerate(entries):
        where = f"entry {i}" + (f" ({e.get('id')})" if isinstance(e, dict) and e.get("id") else "")
        if not isinstance(e, dict):
            problems.append(f"{where} is not an object")
            continue

        for field in FORBIDDEN:
            if field in e:
                problems.append(
                    f"{where} carries a written `{field}`. Confidence is DERIVED from the "
                    f"confirmed and contradicted dates, never typed. Record what happened and "
                    f"let the arithmetic say what it is worth")

        eid = e.get("id")
        if not eid or not ID_RE.match(str(eid)):
            problems.append(f"{where}: id must be a kebab slug, got {eid!r}")
        elif eid in seen:
            problems.append(f"{where}: duplicate id {eid!r}. An id is stable and never reused")
        else:
            seen.add(str(eid))

        for field in ("instinct", "evidence", "learned"):
            if not str(e.get(field) or "").strip():
                problems.append(f"{where}: `{field}` is required")

        inst = str(e.get("instinct") or "")
        if inst and len(inst.split()) > 40:
            problems.append(f"{where}: the instinct runs {len(inst.split())} words. One "
                            f"imperative sentence, or it is a note rather than an instinct")

        for field in ("confirmed", "contradicted"):
            v = e.get(field, [])
            if not isinstance(v, list):
                problems.append(f"{where}: `{field}` must be a list of dates")
                continue
            for dstr in v:
                try:
                    _dt.date.fromisoformat(str(dstr))
                except ValueError:
                    problems.append(f"{where}: {field} carries an unreadable date {dstr!r}")
    return problems


def load(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    problems = validate(doc)
    if problems:
        raise ValueError("; ".join(problems))
    return doc


def save(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def live(doc: dict) -> list[dict]:
    return [e for e in doc["entries"] if not e.get("retired")]


def top(doc: dict, n: int = INJECT_TOP, floor: float = INJECT_AT) -> list[dict]:
    """What the next run is handed. Sorted by earned confidence, then by most recently tested."""
    ranked = [e for e in live(doc) if confidence(e) >= floor]
    ranked.sort(key=lambda e: (-confidence(e), -tests(e), str(e.get("id"))))
    return ranked[:n]


def add(doc: dict, eid: str, instinct: str, evidence: str, date: str) -> dict:
    if any(e.get("id") == eid for e in doc["entries"]):
        raise ValueError(f"id {eid!r} already exists. An id is stable and never reused")
    entry = {"id": eid, "learned": date, "instinct": instinct.strip(),
             "evidence": evidence.strip(), "confirmed": [], "contradicted": []}
    doc["entries"].append(entry)
    return entry


def record(doc: dict, eid: str, field: str, date: str) -> dict:
    for e in doc["entries"]:
        if e.get("id") == eid:
            e.setdefault(field, [])
            if date not in e[field]:
                e[field].append(date)
                e[field].sort()
            return e
    raise ValueError(f"no instinct with id {eid!r}")


def prune(doc: dict, date: str) -> list[str]:
    """Retire what the evidence has turned against. Never delete.

    A deleted lesson is one the machine gets to learn again from scratch, at the cost of a run.
    'We tried this and it was wrong' is a lesson, so a retired entry keeps its evidence and simply
    stops being handed to the directors room.
    """
    retired = []
    for e in live(doc):
        if tests(e) >= MIN_TESTS_TO_RETIRE and \
                len(e.get("contradicted") or []) > len(e.get("confirmed") or []):
            e["retired"] = date
            retired.append(str(e.get("id")))
    return retired


def show(doc: dict) -> None:
    entries = sorted(doc["entries"], key=lambda e: (-confidence(e), str(e.get("id"))))
    if not entries:
        print("instincts: the ledger is empty. This repo has shipped no decks, so it has learned\n"
              "  nothing from running yet, and that is the honest state rather than a gap to fill.")
        return
    print(f"{'id':<34} {'conf':>5} {'tests':>6}  instinct")
    for e in entries:
        mark = " [retired]" if e.get("retired") else ""
        print(f"{str(e.get('id')):<34} {confidence(e):>5.2f} {tests(e):>6}  "
              f"{str(e.get('instinct'))[:60]}{mark}")


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def entry(c=0, x=0, **kw):
        e = {"id": kw.pop("id", "an-instinct"), "learned": "2026-08-12",
             "instinct": "Do the thing", "evidence": "it happened once",
             "confirmed": [f"2026-08-{13+i:02d}" for i in range(c)],
             "contradicted": [f"2026-09-{1+i:02d}" for i in range(x)]}
        e.update(kw)
        return e

    # THE ARITHMETIC. An untested lesson is a coin flip, and saying so is the whole point.
    ok("a brand new instinct scores 0.50, not 0.90", confidence(entry()) == 0.5)
    ok("one confirmation is 0.67, which is still under the injection bar",
       abs(confidence(entry(c=1)) - 2/3) < 1e-9)
    ok("two confirmations is 0.75", confidence(entry(c=2)) == 0.75)
    ok("three clean confirmations reach 0.80 and clear the bar",
       confidence(entry(c=3)) == 0.8 and confidence(entry(c=3)) >= INJECT_AT)
    ok("...and one contradiction against three drops it back under",
       confidence(entry(c=3, x=1)) < INJECT_AT)
    ok("a contradicted-only instinct falls to 0.25", confidence(entry(x=2)) == 0.25)
    ok("confidence never reaches 1.0, however long it holds", confidence(entry(c=500)) < 1.0)

    # THE REFUSAL. This is the flaw the sibling's ledger has, replayed.
    claimed = {"entries": [entry(confidence=0.9)]}
    probs = validate(claimed)
    ok("an entry carrying a written confidence is REFUSED", len(probs) == 1, str(probs))
    ok("...and the message says to record what happened instead",
       "never typed" in probs[0] or "DERIVED" in probs[0], str(probs))
    for alias in ("score", "weight", "certainty", "priority"):
        ok(f"...and the same for `{alias}`, the next word it would reach for",
           validate({"entries": [entry(**{alias: 0.9})]}) != [])

    ok("a clean ledger validates", validate({"entries": [entry(c=2)]}) == [])
    ok("an empty ledger validates, because zero decks means zero lessons",
       validate({"entries": []}) == [])

    # Shape.
    ok("a bad id is caught", validate({"entries": [entry(id="Not A Slug")]}) != [])
    ok("a duplicate id is caught",
       validate({"entries": [entry(id="a"), entry(id="a")]}) != [])
    ok("a missing evidence field is caught",
       validate({"entries": [entry(evidence="")]}) != [])
    ok("an unreadable date is caught",
       validate({"entries": [dict(entry(), confirmed=["not-a-date"])]}) != [])
    ok("a rambling instinct is caught, because a paragraph is a note not an instinct",
       validate({"entries": [entry(instinct="word " * 60)]}) != [])

    # INJECTION. The bar is an event, not a dial.
    doc = {"entries": [entry(id="ready", c=3), entry(id="new"), entry(id="shaky", c=1, x=2)]}
    picked = [e["id"] for e in top(doc)]
    ok("only an instinct that survived three runs is handed to the next one", picked == ["ready"],
       str(picked))
    ok("an untested instinct is not injected", "new" not in picked)
    ok("a contradicted instinct is not injected", "shaky" not in picked)

    doc = {"entries": [entry(id=f"i{i}", c=3 + i) for i in range(9)]}
    ok(f"at most {INJECT_TOP} are injected, strongest first", len(top(doc)) == INJECT_TOP)
    ok("...and the strongest is the most confirmed", top(doc)[0]["id"] == "i8")

    # RETIREMENT, which is not deletion.
    doc = {"entries": [entry(id="wrong", c=1, x=3), entry(id="right", c=3),
                       entry(id="young", c=0, x=1)]}
    retired = prune(doc, "2026-09-30")
    ok("an instinct the evidence turned against is retired", retired == ["wrong"], str(retired))
    ok("...and it is kept, not deleted, because relearning it costs a run",
       any(e["id"] == "wrong" for e in doc["entries"]))
    ok("...and it stops being injected", "wrong" not in [e["id"] for e in top(doc, floor=0.0)])
    ok("...and keeps its evidence for whoever proposes it again",
       doc["entries"][0].get("evidence"))
    ok("one contradiction is not enough to retire on", "young" not in retired)
    ok("a healthy instinct is untouched", "right" not in retired)
    ok("pruning twice changes nothing", prune(doc, "2026-10-01") == [])

    # Recording events.
    doc = {"entries": [entry(id="x")]}
    record(doc, "x", "confirmed", "2026-08-20")
    record(doc, "x", "confirmed", "2026-08-20")
    ok("recording the same date twice does not inflate the count",
       len(doc["entries"][0]["confirmed"]) == 1)
    ok("a confirmation moves the number", confidence(doc["entries"][0]) > 0.5)
    try:
        record(doc, "nope", "confirmed", "2026-08-20")
        ok("confirming an unknown id raises", False)
    except ValueError:
        ok("confirming an unknown id raises", True)
    try:
        add(doc, "x", "i", "e", "2026-08-20")
        ok("reusing an id raises", False)
    except ValueError:
        ok("reusing an id raises", True)

    # THE SHIPPED LEDGER, because this exists to guard that one.
    try:
        real = json.loads(LEDGER.read_text(encoding="utf-8"))
        probs = validate(real)
        ok("the shipped instincts.json validates", probs == [], str(probs[:3]))
        ok("...and starts empty, since this repo has shipped no decks",
           real.get("entries") == [])
    except OSError as exc:
        ok(f"the shipped ledger is readable ({exc})", False)

    if failures:
        print(f"\ninstincts self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\ninstincts self-test: all passed (rule of succession, injection at {INJECT_AT} which "
          f"is three clean confirmations)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--id")
    ap.add_argument("--instinct")
    ap.add_argument("--evidence")
    ap.add_argument("--confirm", metavar="ID")
    ap.add_argument("--contradict", metavar="ID")
    ap.add_argument("--date", help="defaults to today")
    ap.add_argument("--top", nargs="?", type=int, const=INJECT_TOP, metavar="N")
    ap.add_argument("--prune", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    path = Path(a.ledger)
    try:
        doc = load(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"instincts: cannot read {path}: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"instincts: the ledger is malformed: {exc}", file=sys.stderr)
        return 1

    date = a.date or _dt.date.today().isoformat()
    changed = False

    if a.validate:
        print(f"instincts: valid, {len(doc['entries'])} entr(y/ies)")
        return 0
    if a.add:
        if not (a.id and a.instinct and a.evidence):
            print("instincts: --add needs --id, --instinct and --evidence", file=sys.stderr)
            return 1
        try:
            add(doc, a.id, a.instinct, a.evidence, date)
        except ValueError as exc:
            print(f"instincts: {exc}", file=sys.stderr)
            return 1
        print(f"instincts: added {a.id} at {confidence(doc['entries'][-1]):.2f}, which is the "
              f"score of a lesson nothing has tested yet")
        changed = True
    for flag, field in ((a.confirm, "confirmed"), (a.contradict, "contradicted")):
        if flag:
            try:
                e = record(doc, flag, field, date)
            except ValueError as exc:
                print(f"instincts: {exc}", file=sys.stderr)
                return 1
            print(f"instincts: {flag} {field} on {date}, now {confidence(e):.2f} "
                  f"over {tests(e)} test(s)")
            changed = True
    if a.prune:
        retired = prune(doc, date)
        print(f"instincts: retired {len(retired)}" + (f" ({', '.join(retired)})" if retired else ""))
        changed = changed or bool(retired)

    if a.top is not None:
        picked = top(doc, a.top)
        if not picked:
            print("instincts: nothing has earned injection yet. Hand the run nothing rather than\n"
                  "  handing it a lesson no run has confirmed.")
        for e in picked:
            print(f"  [{confidence(e):.2f}] {e['instinct']}")
        return 0

    if changed:
        save(path, doc)
    elif not any((a.add, a.confirm, a.contradict, a.prune)):
        show(doc)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"instincts: broke: {exc}", file=sys.stderr)
        sys.exit(2)
