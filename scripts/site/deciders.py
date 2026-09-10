#!/usr/bin/env python3
"""deciders.py — one public body, however many ways the record spells it.

WHY THIS EXISTS

The record holds 123 decisions and 84 distinct decider strings, and three of those strings are
one federal agency:

    National Science Foundation                    4 decisions
    U.S. National Science Foundation               5 decisions
    United States National Science Foundation      4 decisions

A reader asking what the National Science Foundation has decided got four of thirteen, and the
box was confident about it. Two more pairs differ only by a leading "The".

This is `entities.py`'s comma problem in a different ledger, so it is solved the same way and
the two files should be read together. What is different is the ledger and the display rule, and
both differences are stated below rather than left for somebody to discover.

TWO LAYERS, AND THE LINE BETWEEN THEM IS THE POINT

  1. RESOLUTION IS MECHANICAL. Case, punctuation and a leading definite article are removed, and
     two strings that come out identical are one body. There is no judgment in this. "The
     University of Texas at Austin" and "University of Texas at Austin" resolve together because
     English does not carry identity in an article.

  2. EVERYTHING ELSE IS CURATED, in `config/decider_groups.json`, as data owned by a human. Every
     entry states its reason and an entry with no reason fails the gate.

WHY THE U.S. PREFIX IS NOT MECHANICAL, WHICH IS THE ONE DECISION IN THIS FILE WORTH ARGUING
WITH. Stripping it would have merged the three NSF spellings for free and no config would have
been needed. It would also merge the U.S. Chamber of Commerce with a local chamber of commerce,
and that is wrong in a way nothing here could catch, because both are real bodies and both file.
A rule is only mechanical if it is right without knowing who is being named.

THE DISPLAY NAME IS THE RECORD'S OWN, and no name is typed in the config. Where a body's
spellings disagree the most frequent wins, ties broken by the longest, so a reader sees a string
some source actually filed. `entities.py` curates a display name because "Oracle" is shorter than
anything the state ever wrote; here the record's own spellings are already the body's real names
and picking one is cheaper and more honest than inventing a fourth.

THE GATE IS THE POINT, NOT THE FIX. Merging the NSF today is worth little if the next agency to
arrive under two spellings splits again in silence. So a name that is a trailing sub-phrase of
another decider name is a COLLISION CANDIDATE, and every candidate must be declared either the
same body or a distinct one, with a reason. There are four in the record today and the gate names
any fifth the day it appears.

    deciders.py                # the gate, and a summary
    deciders.py --self-test    # hermetic
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ledger" / "docket.json"
GROUPS = ROOT / "config" / "decider_groups.json"


def mechanical_key(name: str) -> str:
    """The rule with no judgment in it. Case, punctuation, and a leading definite article."""
    s = re.sub(r"[^a-z0-9 ]+", " ", str(name).lower())
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^the\s+", "", s)


def _config(path: pathlib.Path | None = None) -> dict:
    p = path or GROUPS
    if not p.exists():
        return {"same": [], "distinct": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _display(names: list[str], counts: Counter) -> str:
    """The spelling the record uses most, ties broken by the longest.

    Never a name from the config. See the note at the top about why a display name typed by
    this project is a fourth spelling of something that already had three.
    """
    return sorted(names, key=lambda n: (-counts[n], -len(n), n))[0]


def resolve(counts: Counter, cfg: dict | None = None) -> dict[str, str]:
    """Every decider string in the record, mapped to the name its body publishes under.

    `counts` is name -> how many decisions carry it, which is what decides the display name.
    A name in no group and colliding with nothing maps to itself.
    """
    cfg = _config() if cfg is None else cfg
    # union-find over the names, seeded by the mechanical key and then joined by the config
    parent: dict[str, str] = {n: n for n in counts}

    def find(a: str) -> str:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    by_key: dict[str, list[str]] = {}
    for n in counts:
        by_key.setdefault(mechanical_key(n), []).append(n)
    for group in by_key.values():
        for other in group[1:]:
            union(group[0], other)

    for entry in cfg.get("same") or []:
        # A MEMBER THE RECORD DOES NOT CARRY IS IGNORED, never invented. That is what lets this
        # file name a body before its first decision lands.
        present = [m for m in (entry.get("members") or []) if m in counts]
        for other in present[1:]:
            union(present[0], other)

    families: dict[str, list[str]] = {}
    for n in counts:
        families.setdefault(find(n), []).append(n)
    out: dict[str, str] = {}
    for members in families.values():
        name = _display(members, counts)
        for m in members:
            out[m] = name
    return out


def counts_of(items: list) -> Counter:
    return Counter((it.get("decider") or {}).get("name", "") for it in items
                   if (it.get("decider") or {}).get("name"))


def candidates(counts: Counter) -> list[tuple[str, str]]:
    """Pairs where one decider's name ends the other's, which is how a body splits in two.

    Word aligned on the mechanical key, so "Foundation" does not collide with "Science
    Foundation" by accident of letters, and a pair the mechanical layer already joined is not
    reported, because it is already one body.
    """
    keys = {mechanical_key(n): n for n in counts}
    out = []
    for short in sorted(keys):
        for long in sorted(keys):
            if short != long and long.endswith(" " + short):
                out.append((keys[short], keys[long]))
    return out


def declared(cfg: dict) -> set[frozenset]:
    """Every pair a human has ruled on, in either direction."""
    out: set[frozenset] = set()
    for kind in ("same", "distinct"):
        for entry in cfg.get(kind) or []:
            members = entry.get("members") or []
            for i, a in enumerate(members):
                for b in members[i + 1:]:
                    out.add(frozenset((mechanical_key(a), mechanical_key(b))))
    return out


def report(items: list, cfg: dict | None = None) -> tuple[int, list[str]]:
    """The gate. Returns an exit code and the lines to print."""
    cfg = _config() if cfg is None else cfg
    counts = counts_of(items)
    lines, bad = [], []

    for kind in ("same", "distinct"):
        for entry in cfg.get(kind) or []:
            members = entry.get("members") or []
            if not str(entry.get("note") or "").strip():
                bad.append(f"a {kind} entry states no reason: {members}")
            if len(members) < 2:
                bad.append(f"a {kind} entry needs at least two members: {members}")

    mapped = resolve(counts, cfg)
    bodies = sorted(set(mapped.values()))
    lines.append(f"{len(counts)} decider strings resolve to {len(bodies)} bodies")
    for body in bodies:
        spellings = sorted(n for n in counts if mapped[n] == body)
        if len(spellings) > 1:
            total = sum(counts[s] for s in spellings)
            lines.append(f"  {body}  {total} decisions across {len(spellings)} spellings")
            for s in spellings:
                lines.append(f"      {counts[s]:3d}  {s}")

    # EVERY COLLISION CANDIDATE MUST HAVE BEEN RULED ON. This is the half that catches the next
    # one rather than the last one.
    ruled = declared(cfg)
    for short, long in candidates(counts):
        pair = frozenset((mechanical_key(short), mechanical_key(long)))
        if pair not in ruled:
            bad.append(f"undeclared collision: {short!r} ends {long!r}. "
                       f"Say in config/decider_groups.json whether they are the same body")
    if bad:
        lines.append("")
        lines.extend("  FAIL  " + b for b in bad)
    lines.append("")
    lines.append("deciders: every string resolves and every collision is declared" if not bad
                 else f"deciders: {len(bad)} problem(s)")
    return (1 if bad else 0), lines


def self_test() -> int:
    ok = [True]

    def check(label, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
        if not cond:
            ok[0] = False

    print("the mechanical layer, which has no judgment in it")
    check("a leading article is not identity",
          mechanical_key("The University of Texas at Austin")
          == mechanical_key("University of Texas at Austin"))
    check("case and punctuation are not identity",
          mechanical_key("Public Utility Commission of Texas.")
          == mechanical_key("public utility commission  of texas"))
    # THE ONE THE MECHANICAL LAYER MUST REFUSE. If this ever passes, somebody has taught the
    # regex to strip a national qualifier and the U.S. Chamber of Commerce has quietly become a
    # local one.
    check("a U.S. prefix is NOT stripped, because it can be the whole of the difference",
          mechanical_key("U.S. Chamber of Commerce") != mechanical_key("Chamber of Commerce"))
    check("an article inside the name is left alone",
          mechanical_key("Texas Politics Project at the University of Texas at Austin")
          != mechanical_key("University of Texas at Austin"))

    print("the display name comes off the record, never out of the config")
    counts = Counter({"National Science Foundation": 4,
                      "U.S. National Science Foundation": 5,
                      "United States National Science Foundation": 4})
    cfg = {"same": [{"note": "one agency", "members": list(counts)}], "distinct": []}
    got = resolve(counts, cfg)
    check("the most frequent spelling wins",
          set(got.values()) == {"U.S. National Science Foundation"}, str(sorted(set(got.values()))))
    tie = Counter({"Alpha Board": 2, "Alpha Board of Texas": 2})
    tied = resolve(tie, {"same": [{"note": "one", "members": list(tie)}], "distinct": []})
    check("a tie is broken by the longest, so the fuller name shows",
          set(tied.values()) == {"Alpha Board of Texas"}, str(sorted(set(tied.values()))))

    print("a member the record does not carry is ignored rather than invented")
    partial = resolve(Counter({"National Science Foundation": 1}),
                      {"same": [{"note": "x", "members": ["National Science Foundation",
                                                          "Nonexistent Agency"]}],
                       "distinct": []})
    check("naming an absent body changes nothing",
          partial == {"National Science Foundation": "National Science Foundation"}, str(partial))

    print("the gate goes red, which is the only reason to have one")
    live = Counter({"National Science Foundation": 1, "U.S. National Science Foundation": 1})
    code, _ = report([{"decider": {"name": n}} for n, c in live.items() for _ in range(c)],
                     {"same": [], "distinct": []})
    check("an undeclared collision fails", code == 1)
    code, _ = report([{"decider": {"name": n}} for n, c in live.items() for _ in range(c)],
                     {"same": [{"note": "one agency", "members": list(live)}], "distinct": []})
    check("...and declaring it as one body clears it", code == 0)
    code, _ = report([{"decider": {"name": n}} for n, c in live.items() for _ in range(c)],
                     {"same": [], "distinct": [{"note": "two bodies", "members": list(live)}]})
    check("...and declaring them distinct clears it too, without merging them", code == 0)
    code, _ = report([{"decider": {"name": n}} for n, c in live.items() for _ in range(c)],
                     {"same": [{"note": "   ", "members": list(live)}], "distinct": []})
    check("a group with no stated reason fails", code == 1)

    print()
    print("deciders self-test clean" if ok[0] else "deciders self-test FAILED")
    return 0 if ok[0] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    # THE MAP, FOR CALLERS THAT ARE NOT PYTHON. `tests/ask_worker_retrieval.mjs` scores a decider
    # case by comparing the body a route names against the body a decision belongs to, and it
    # reads the ledger directly. Shelling out for the map keeps one implementation of who is who,
    # which is the whole point of this file.
    ap.add_argument("--map", action="store_true",
                    help="print every decider spelling mapped to its body, as JSON")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.map:
        doc = json.loads(LEDGER.read_text(encoding="utf-8"))
        items = doc if isinstance(doc, list) else doc["items"]
        json.dump(resolve(counts_of(items)), sys.stdout, indent=1, sort_keys=True)
        return 0
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    items = doc if isinstance(doc, list) else doc["items"]
    code, lines = report(items)
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
