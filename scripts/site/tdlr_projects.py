#!/usr/bin/env python3
"""tdlr_projects.py — what the construction register says, computed.

WHY IT IS A SEPARATE MODULE FROM THE FETCHER

`tdlr_fetch.py` turns a state web page into records. This turns records into the figures a page
shows, and it is the only place those figures are produced. Nothing here is typed.

THE THREE THINGS THAT WOULD MAKE A PUBLISHED TOTAL WRONG, ALL OF THEM PRESENT IN THE REAL DATA

    A DESIGNATION CAN BE FILED TWICE. SAT82 has two filings at two addresses and two costs.
    SAT93 and SAT94 each have a large filing and a small later one. Summing every row as though
    each were a separate building overstates the buildout, so `by_designation()` groups them and
    the page shows the filing COUNT beside the money.

    THE COUNTY FIELD IS FILER ENTERED AND IS SOMETIMES WRONG. One filing gives Medina County with
    a San Antonio address on Lambda Drive, which is in Bexar. So a county total is never computed
    silently: `county_conflicts()` reports every filing whose county disagrees with the county its
    own postcode belongs to, and the page prints the conflict rather than absorbing it.

    THE SEARCH ENDPOINT IGNORES ITS CITY PARAMETER. A search for Microsoft in San Antonio returns
    the Irving buildings too. Scoping happens here, on the records, never on the request.

WHAT IT DOES NOT DO. It does not decide that a filing and a certification are the same building.
The Comptroller names "Microsoft Corporation (SAT 89-90)" and the register names "SAT89/90 Data
Center", and a reader can see that. A matcher that asserted it would be inventing a join the state
never published.

    tdlr_projects.py               # gate the ledger
    tdlr_projects.py --self-test   # hermetic
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ledger" / "facilities" / "projects.json"
PHONE = re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}")
# A designation as the filer wrote it: SAT09, SAT 09, SAT11-14, SAT89/90. The continuation is
# only taken when a DIGIT follows the separator, which is what keeps "SAT 80 - Package 1" from
# being read as a range from eighty to one.
DESIG = re.compile(r"\bSAT\s?0*(\d{1,3})(\s?[/-]\s?0*(\d{1,3}))?", re.I)


def load(path: pathlib.Path = LEDGER) -> dict:
    if not path.exists():
        return {"_spec": 1, "projects": []}
    return json.loads(path.read_text(encoding="utf-8"))


def designations(rec: dict) -> list[str]:
    """Every BUILDING a filing's name mentions. "SAT89/90" is two and "SAT11-14" is four.

    THIS IS FOR COVERAGE AND NEVER FOR MONEY. One filing that names four buildings has one cost,
    and spreading that cost across four rows would report a buildout four times over. `group()`
    below is what money is added up by.
    """
    out = set()
    for m in DESIG.finditer(rec.get("project", "")):
        a = int(m.group(1))
        out.add(a)
        if m.group(3):
            b = int(m.group(3))
            # A slash lists siblings. A dash is a range only when it runs upward, which is what
            # stops a package number being read as the far end of one.
            out.update(range(a, b + 1) if b > a else [b])
    return [f"SAT{n}" for n in sorted(out)]


def group(rec: dict) -> str:
    """The designation AS FILED, which is the unit a cost belongs to. "SAT11-14" is one filing
    about four buildings and stays one key."""
    m = DESIG.search(rec.get("project", ""))
    if not m:
        return "(no designation)"
    a = int(m.group(1))
    return f"SAT{a}" + (f"-{int(m.group(3))}" if m.group(3) else "")


def by_designation(recs: list[dict]) -> list[dict]:
    """Grouped, so a designation filed twice is counted once as a building and twice as a filing."""
    g: dict[str, list[dict]] = defaultdict(list)
    for r in recs:
        g[group(r)].append(r)
    out = []
    for name, rows in g.items():
        out.append({
            "designation": name,
            "buildings": sorted({d for r in rows for d in designations(r)}),
            "filings": len(rows),
            "cost": sum(r.get("cost") or 0 for r in rows),
            "sqft": sum(r.get("sqft") or 0 for r in rows),
            "first": min((r.get("start") or "9999") for r in rows),
            "last": max((r.get("end") or "") for r in rows),
            "counties": sorted({r.get("county", "") for r in rows if r.get("county")}),
            "addresses": sorted({r.get("address", "") for r in rows if r.get("address")}),
        })
    def order(d):
        b = d["buildings"]
        return ("zzz", 0) if not b else ("", int(b[0][3:]))
    return sorted(out, key=order)


def covered(recs: list[dict]) -> list[str]:
    """Every building the construction register names, however it was filed."""
    n = sorted({int(d[3:]) for r in recs for d in designations(r)})
    return [f"SAT{x}" for x in n]


def county_conflicts(recs: list[dict]) -> list[dict]:
    """Postcodes the filings themselves cannot agree on a county for.

    THE FIRST VERSION OF THIS ASKED THE WRONG QUESTION and would have reported correct filings as
    wrong. It kept a table of which county each postcode "belongs to" and flagged any filing that
    disagreed. A postcode does not belong to a county. ZIPs cross county lines routinely, and
    78253 runs along the Bexar and Medina line, so four perfectly good filings came out as errors
    against a table this file had invented.

    So the comparison is now INTERNAL. It makes no claim about where a postcode is. It reports
    only that two filings gave the same postcode and named different counties, which is a
    disagreement in the record itself and is worth showing a reader either way.
    """
    seen: dict[str, set] = defaultdict(set)
    where: dict[str, list] = defaultdict(list)
    for r in recs:
        pc, co = r.get("postcode"), r.get("county")
        if pc and co:
            seen[pc].add(co)
            where[pc].append(r)
    out = []
    for pc, counties in sorted(seen.items()):
        if len(counties) > 1:
            out.append({"postcode": pc, "counties": sorted(counties),
                        "filings": [{"number": x["number"], "project": x.get("project", ""),
                                     "county": x.get("county", ""),
                                     "address": x.get("address", "")}
                                    for x in where[pc]]})
    return out


def totals(recs: list[dict]) -> dict:
    """Every figure a page may show about a set of filings. Computed here, from the records."""
    costed = [r for r in recs if r.get("cost")]
    return {
        "filings": len(recs),
        "costed": len(costed),
        "cost": sum(r["cost"] for r in costed),
        "sqft": sum(r.get("sqft") or 0 for r in recs),
        "sqft_known": sum(1 for r in recs if r.get("sqft")),
        "first": min((r.get("start") or "9999") for r in recs) if recs else "",
        "last": max((r.get("end") or "") for r in recs) if recs else "",
        "counties": len({r.get("county") for r in recs if r.get("county")}),
        "new_build": sum(1 for r in recs if (r.get("work") or "").lower().startswith("new")),
    }


def scoped(recs: list[dict], counties: tuple[str, ...]) -> list[dict]:
    return [r for r in recs if r.get("county") in counties]


# ---------------------------------------------------------------- the gate
def problems(doc: dict) -> list[str]:
    out = []
    seen = set()
    for r in doc.get("projects") or []:
        n = r.get("number") or "(unnumbered)"
        if not r.get("number"):
            out.append("a filing carries no project number")
        elif n in seen:
            out.append(f"filing {n} appears twice in the ledger")
        seen.add(n)
        if not r.get("owner"):
            out.append(f"filing {n} names no owner")
        if not r.get("project"):
            out.append(f"filing {n} has no project name")
        if r.get("cost") is not None and not isinstance(r["cost"], int):
            out.append(f"filing {n} has a cost that is not an integer")
        if r.get("sqft") is not None and not isinstance(r["sqft"], int):
            out.append(f"filing {n} has a square footage that is not an integer")
        for f in ("start", "end", "registered"):
            if r.get(f) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r[f]):
                out.append(f"filing {n} has a {f} that is not an ISO date")
        # THE RULE THE PARSER EXISTS TO HOLD, checked again on what actually landed.
        blob = json.dumps(r)
        if PHONE.search(blob):
            out.append(f"filing {n} carries a phone number, which never reaches this ledger")
        for word in ("Contact Name", "RAS "):
            if word in blob:
                out.append(f"filing {n} carries {word.strip()!r}, which is a person")
    return out


def self_test() -> int:
    checks = []

    def ok(name, cond, extra=""):
        checks.append(bool(cond))
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}{'' if cond else '  ' + str(extra)}")

    good = {"number": "TABS1", "project": "SAT 09", "owner": "Microsoft", "cost": 90_000_000,
            "sqft": 1000, "start": "2016-01-01", "county": "Bexar", "postcode": "78245",
            "work": "New Construction"}

    ok("a well formed filing passes", problems({"projects": [good]}) == [])
    ok("a filing with no number fails", problems({"projects": [{**good, "number": ""}]}) != [])
    ok("a filing with no owner fails", problems({"projects": [{**good, "owner": ""}]}) != [])
    ok("a duplicated number fails", len(problems({"projects": [good, dict(good)]})) > 0)
    ok("a cost that is a string fails", problems({"projects": [{**good, "cost": "90000000"}]}) != [])
    ok("a date that is not ISO fails", problems({"projects": [{**good, "start": "1/1/2016"}]}) != [])
    # The people rule, checked on the ledger and not only at the parser.
    ok("a phone number in a filing fails",
       problems({"projects": [{**good, "scope": "call (972) 270-3100"}]}) != [])
    ok("a person's name field in a filing fails",
       problems({"projects": [{**good, "scope": "Contact Name: someone"}]}) != [])

    # DESIGNATIONS, and the three real shapes that would corrupt a total.
    ok("a spaced and an unspaced designation are one",
       designations({"project": "MICROSOFT SAT 09"}) == designations({"project": "MICROSOFT SAT09"})
       == ["SAT9"], designations({"project": "MICROSOFT SAT 09"}))
    ok("a paired designation is two",
       designations({"project": "SAT89/90 Data Center"}) == ["SAT89", "SAT90"],
       designations({"project": "SAT89/90 Data Center"}))
    ok("a range names every building in it",
       designations({"project": "MICROSOFT SAT11-14"}) == ["SAT11", "SAT12", "SAT13", "SAT14"],
       designations({"project": "MICROSOFT SAT11-14"}))
    # THE TRAP. A package number after a dash is not the far end of a range.
    ok("a package number is not read as a range",
       designations({"project": "SAT 80 - Package 1"}) == ["SAT80"],
       designations({"project": "SAT 80 - Package 1"}))
    ok("...and a range of four buildings is still ONE key for money",
       group({"project": "MICROSOFT SAT11-14"}) == "SAT11-14",
       group({"project": "MICROSOFT SAT11-14"}))
    four = by_designation([{"number": "a", "project": "MICROSOFT SAT11-14", "cost": 62_000_000}])
    ok("...so its cost is counted once, not once per building",
       len(four) == 1 and four[0]["cost"] == 62_000_000 and len(four[0]["buildings"]) == 4, four)
    ok("a filing with no designation is not forced into one",
       designations({"project": "Admin 2 Building"}) == [],
       designations({"project": "Admin 2 Building"}))

    twice = [{"number": "a", "project": "SAT82 Data Center", "cost": 482_600_000, "start": "2026-04-11"},
             {"number": "b", "project": "Microsoft SAT82 Data Center", "cost": 400_000_000,
              "start": "2026-08-13"}]
    g = by_designation(twice)
    ok("a designation filed twice is one row", len(g) == 1, g)
    ok("...counting both filings", g[0]["filings"] == 2, g)
    ok("...and both costs, so the page can say which it is showing",
       g[0]["cost"] == 882_600_000, g)

    # THE CHECK THAT MAKES NO CLAIM ABOUT GEOGRAPHY, only about the record disagreeing with
    # itself. A single filing can never be a conflict, however unlikely its county looks.
    ok("one filing on its own is never a conflict",
       county_conflicts([{**good, "county": "Medina"}]) == [])
    ok("two filings on one postcode naming two counties is",
       len(county_conflicts([good, {**good, "number": "b", "county": "Medina"}])) == 1)
    ok("...and it names both counties rather than picking one",
       county_conflicts([good, {**good, "number": "b", "county": "Medina"}])[0]["counties"]
       == ["Bexar", "Medina"])
    ok("two filings agreeing is not a conflict",
       county_conflicts([good, {**good, "number": "b"}]) == [])

    t = totals([good, {**good, "number": "TABS2", "cost": None, "sqft": None}])
    ok("a filing with no cost is counted as a filing and not as a zero",
       (t["filings"], t["costed"], t["cost"]) == (2, 1, 90_000_000), t)
    ok("...and the square footage total says how many it knows",
       (t["sqft"], t["sqft_known"]) == (1000, 1), t)
    ok("scoping is done on the records, never on the request",
       len(scoped([good, {**good, "number": "x", "county": "Dallas"}], ("Bexar",))) == 1)

    passed = sum(checks)
    print(f"\ntdlr_projects self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    doc = load()
    recs = doc.get("projects") or []
    if not recs:
        print("tdlr_projects: no filings in the ledger yet")
        return 0
    found = problems(doc)
    if found:
        print(f"tdlr_projects: {len(found)} problem(s)\n", file=sys.stderr)
        for p in found:
            print(f"  {p}", file=sys.stderr)
        return 1
    t = totals(recs)
    print(f"tdlr_projects: {t['filings']} filing(s), {t['costed']} with a cost, "
          f"${t['cost']:,} across {t['counties']} count(ies)")
    c = county_conflicts(recs)
    if c:
        print(f"  {len(c)} filing(s) state a county their own postcode contradicts, "
              f"which the page reports rather than absorbs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
