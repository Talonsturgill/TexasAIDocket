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


# ---------------------------------------------------------------- what a filing IS
# THE OWNER SEARCH IS A SUBSTRING MATCH AND IT CANNOT BE TRUSTED. A query for "Meta" returns
# Metal Building Supplies. "Core Scientific" returns Core & Main, CORE Construction and a nail
# bar. "Prologis" returns that landlord's entire Texas portfolio. A pull that believed the
# endpoint would have summed a nail bar into a data centre headline.
#
# So membership is decided HERE, on the owner the filing itself carries, against a brand token
# this project already tracks. `owner_is()` is the whole rule and it is deliberately strict.
BRANDS = {
    "amazon": "Amazon", "vantage": "Vantage", "compass": "Compass", "cyrusone": "CyrusOne",
    "riot": "Riot", "qts": "QTS", "aligned": "Aligned", "ntt": "NTT", "oracle": "Oracle",
    "switch": "Switch", "google": "Google", "databank": "DataBank", "galaxy": "Galaxy",
    "microsoft": "Microsoft", "lancium": "Lancium", "cipher": "Cipher", "crusoe": "Crusoe",
    "fermi": "Fermi", "lambda": "Lambda",
    # Added after a wider pull surfaced them. Stream holds one certification and files; Digital
    # Realty files and holds NONE, which is a fact about it rather than a gap in this list.
    # `stream` carries a trailing boundary as well as a leading one, so Streamline and its kind
    # do not match, the same guard that keeps EVANTAGE HOLDINGS out of Vantage's column.
    r"stream\b": "Stream", "digital realty": "Digital Realty",
}


# OPERATORS THIS PROJECT TRACKS THAT FILE NOTHING UNDER THEIR OWN NAME. Checked, not assumed:
# each returned zero rows from the owner search. It is a real fact about how they operate, and
# saying it beats leaving a reader to wonder why a name they expect is missing.
NO_FILINGS = ("CoreWeave", "EdgeConneX", "Nscale", "Anthropic", "Whinstone", "Poolside")


def brand(rec: dict) -> str:
    """The tracked company whose name appears in this filing's OWNER field, or an empty string.

    Matched on the owner, never on the project name, because a project can be named for its
    tenant while the filing belongs to a developer, and the owner is the field the state
    actually verifies.
    """
    o = (rec.get("owner") or "").lower()
    # A key may carry its own trailing boundary. Escaping it wholesale would turn that into a
    # literal backslash-b and match nothing, silently, which is the shape of a filter that
    # quietly stops filtering.
    hits = [v for k, v in BRANDS.items()
            if re.search(r"\b" + (k if k.endswith(r"\b") else re.escape(k)), o)]
    return sorted(hits, key=len, reverse=True)[0] if hits else ""


# WHICH FILINGS ARE ABOUT A DATA CENTRE. Amazon builds fulfilment centres and Microsoft refreshes
# cafes, and neither belongs in a figure about compute. The test is what the FILING says, in its
# project name, its facility name or the scope the filer wrote, and the rule is stated on the
# published page so a reader can disagree with it.
# EXCLUDE FIRST. The airport code designation below is used by data centre operators AND by
# Amazon for warehouses, so "Fulfillment Center DFW7" matched the include list on its first
# version and would have put a warehouse into a figure about compute. A filing that names a
# building type this is not is out, whatever else it says.
NOT_DC = re.compile(
    r"\b(fulfil?lment|warehouse|distribution\s?cent|sortation|delivery\s?station|air\s?hub|"
    r"retail|store\b|restaurant|cafe|caf\u00e9|lobby|clinic|hotel|apartment|school|church|"
    r"office\s?(?:refresh|fit|remodel|renovation)|parking\s?garage|showroom)", re.I)

DC_WORDS = re.compile(
    r"\b(data\s?cent(?:er|re)|datacent(?:er|re)|colo(?:cation)?|server\s?(?:room|hall)|"
    r"white\s?space|data\s?hall|substation|generator\s?yard|chiller\s?(?:plant|yard)|"
    r"critical\s?(?:power|load)|SAT\s?\d|AUS\s?\d{2}|DFW\s?\d{2}|SAN\s?\d{2}|"
    r"TX\s?\d{2,3}\b)", re.I)


def is_datacenter(rec: dict) -> bool:
    """What the FILING says it is. The rule is published on the page so a reader can disagree."""
    hay = " ".join(str(rec.get(k) or "") for k in ("project", "facility", "scope"))
    if NOT_DC.search(hay):
        return False
    return bool(DC_WORDS.search(hay))


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


# ---------------------------------------------------------------- joining the two registers
# THE STATE PUBLISHED THIS JOIN ON BOTH SIDES, so it is not invented. Vantage's Shackelford
# filings are owned by "Vantage Data Centers TX304, LLC", and that exact entity is the owner of
# record on a Comptroller row. Galaxy Helios II and DB Data Center Red Oak behave the same way.
#
# BUT ONLY FOR A SINGLE PURPOSE ENTITY. Joining on a parent company is not a building level link
# and the first version did it: matching "Microsoft Corporation" attached all twenty two
# Microsoft filings, and $3.6 billion, to a single facility called NADC. An entity named on many
# certifications identifies a company, not a project.
#
# So a party joins only when it is SPECIFIC: it names at most this many certified facilities.
# A number here is a judgement and it is stated rather than buried.
SINGLE_PURPOSE_MAX = 2


def joinable(parties_per_facility: list[set]) -> set:
    """The party names specific enough to identify a project rather than a company."""
    n: dict[str, int] = defaultdict(int)
    for parties in parties_per_facility:
        for p in parties:
            n[p] += 1
    return {p for p, c in n.items() if c <= SINGLE_PURPOSE_MAX}


def filings_for(parties: set, specific: set, by_party: dict) -> list[dict]:
    """Filings by the single purpose entities named on one facility's row."""
    out, seen = [], set()
    for p in parties & specific:
        for r in by_party.get(p, ()):
            if r["number"] not in seen:
                seen.add(r["number"])
                out.append(r)
    return sorted(out, key=lambda r: (r.get("start") or "", r["number"]))


def shared_buildings(recs: list[dict]) -> list[dict]:
    """Filings that look like the same building filed by two different owners.

    A statewide total adds up filings from many companies, and a campus where the landowner and
    the builder both file would be counted twice. Two filings at the same address for the same
    cost under different owners is the shape that would do it.

    It has found nothing so far, which is worth saying out loud rather than assuming: Lancium and
    Crusoe both filed a $292 million Abilene building, and they are two buildings on two streets
    that happen to cost the same. A check that has never fired is only useful if somebody knows
    it is running.
    """
    seen: dict[tuple, dict] = {}
    out = []
    for r in recs:
        k = ((r.get("address") or "").lower().strip(), r.get("cost"))
        if not k[0] or not k[1]:
            continue
        prev = seen.get(k)
        if prev and (prev.get("owner") or "") != (r.get("owner") or ""):
            out.append({"address": r.get("address", ""), "cost": r["cost"],
                        "filings": [prev["number"], r["number"]],
                        "owners": [prev.get("owner", ""), r.get("owner", "")]})
        seen[k] = r
    return out


# ---------------------------------------------------------------- the year view
def by_year(recs: list[dict]) -> list[dict]:
    """Capital and floor area filed per year, by the year a project was scheduled to START.

    EVERY YEAR IN THE SPAN APPEARS, including the empty ones. A chart that silently drops a year
    with no filings compresses the gaps out of the picture and makes a lumpy buildout look
    steady, which is the opposite of what this data says.
    """
    years = [int(r["start"][:4]) for r in recs if r.get("start")]
    if not years:
        return []
    out = []
    for y in range(min(years), max(years) + 1):
        rows = [r for r in recs if (r.get("start") or "")[:4] == str(y)]
        out.append({"year": y, "filings": len(rows),
                    "cost": sum(r.get("cost") or 0 for r in rows),
                    "sqft": sum(r.get("sqft") or 0 for r in rows)})
    return out


def by_brand(recs: list[dict]) -> list[dict]:
    g: dict[str, list[dict]] = defaultdict(list)
    for r in recs:
        g[brand(r) or "(untracked)"].append(r)
    out = [{"brand": k, **totals(v),
            "counties": sorted({x.get("county") for x in v if x.get("county")})}
           for k, v in g.items()]
    return sorted(out, key=lambda d: (-d["cost"], d["brand"]))


def money(v) -> str:
    """A cost at the scale a reader reads it. The rounding rule is stated here rather than
    chosen per figure, because rounding is a computation and not a style decision."""
    v = int(v or 0)
    return f"${v / 1_000_000_000:.2f} billion" if v >= 1_000_000_000 else f"${v:,}"


def andlist(names: list[str]) -> str:
    """A, B and C. Two names take no comma, and ", ".join gets that wrong.

    Same rule the topic labels follow. A serial list takes a comma between every item but the
    last pair, so a list of six keeps its commas and a list of two reads "Crusoe and Digital
    Realty" rather than a sentence that lost its conjunction. The sentences these lists sit
    inside are generated and their length is data, so the rule is written once rather than
    guessed at each call site.
    """
    names = list(names)
    if len(names) < 3:
        return " and ".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def facility_panel(recs: list[dict], e) -> str:
    """What the state was told about building THIS facility, on the facility's own page.

    Only the filings reached through a single purpose entity named on this row. The join is the
    state's own, published on both sides, and it is refused for a parent company, so a page
    either shows its own buildings or shows nothing at all. Nothing here is an estimate this
    project made and nothing is attributed by resemblance.
    """
    if not recs:
        return ""
    t = totals(recs)

    def row(r):
        sq = f'<strong class="num">{r["sqft"]:,}</strong> sq ft' if r.get("sqft") else ""
        return (f'<div class="cbrow"><span class="cbd">{e((r.get("start") or "")[:4])}</span>'
                f'<span class="cbm"><strong class="num">{e(money(r.get("cost")))}</strong></span>'
                f'<span class="cbs">{sq}</span>'
                # THE STATE'S OWN PROJECT NAME, DECLARED AS ONE. Compass files buildings as
                # "DFW III-I" and "Compass Datacenters DFW I-II, LLC", and a roman numeral
                # segment leaves a standalone "I" that the house lint reads as first person. It
                # was right on the letter and wrong on the page. This string is transcribed by
                # the parser straight out of the filing and is never authored here, so it is
                # marked at the source exactly like a facility name, and only the exact string
                # is exempt.
                f'<span class="cbf" data-proper-name="{e(r.get("project", ""))}">'
                f'{e(r.get("project", ""))}</span>'
                f'<span class="cbc">{e(r.get("city", ""))}</span></div>')

    head = (f'<strong class="num">{e(money(t["cost"]))}</strong> across '
            f'<strong class="num">{t["filings"]:,}</strong> filing'
            + ("" if t["filings"] == 1 else "s"))
    if t["sqft"]:
        head += f', <strong class="num">{t["sqft"]:,}</strong> sq ft'
    return (
        f'<h2>What was filed to build it</h2>'
        f'<p>Texas registers every large construction project with a second agency. These '
        f'filings were made by a company this record already names.</p>'
        f'<p class="qnote" data-prose="data">{head}.</p>'
        f'<div class="cbtable cbfile" data-prose="data">'
        f'{"".join(row(r) for r in recs)}</div>'
        f'<p class="qnote">An estimated cost at filing is not a final cost, and a filing is not '
        f'proof a building went up. <a href="../../construction/">How this register works</a>.</p>')


# ---------------------------------------------------------------- the drawing
CW, CH = 1000.0, 300.0     # the field, in user units. The svg scales to its container.
CPAD_L, CPAD_B, CPAD_T = 8.0, 34.0, 14.0


def columns(rows: list[dict], key: str) -> str:
    """One column per year, one hue, no ramp.

    The grid watch bar carries no severity ramp because a colour ramp is a verdict. The same
    holds here: the height is the whole message and every column is the same colour at the same
    intensity. A reader compares lengths, which is the one comparison a bar chart is good at.
    """
    if not rows:
        return ""
    hi = max(r[key] for r in rows) or 1
    n = len(rows)
    gap = 6.0
    w = (CW - CPAD_L * 2 - gap * (n - 1)) / n
    floor = CH - CPAD_B
    bars = ""
    for i, r in enumerate(rows):
        x = CPAD_L + i * (w + gap)
        h = (r[key] / hi) * (floor - CPAD_T)
        bars += (f'<g class="cyr"><rect class="cybar" x="{x:.2f}" y="{floor - h:.2f}" '
                 f'width="{w:.2f}" height="{max(h, 1.0):.2f}" rx="2"/>'
                 f'<text class="cylab" x="{x + w / 2:.2f}" y="{CH - 10:.2f}">{r["year"]}</text>'
                 f'<title>{r["year"]}</title></g>')
    return (f'<svg class="cysvg" viewBox="0 0 {int(CW)} {int(CH)}" role="img" '
            f'aria-labelledby="cyttl" preserveAspectRatio="none">'
            f'<title id="cyttl">Construction capital filed per year, by the year each project '
            f'was scheduled to start.</title>'
            f'<line class="cyaxis" x1="0" y1="{floor:.2f}" x2="{int(CW)}" y2="{floor:.2f}"/>'
            f'{bars}</svg>')


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

    # WHO A FILING BELONGS TO. The endpoint's owner search is a substring match and returns a
    # nail bar for "Core Scientific", so membership is decided on the owner field here.
    ok("a tracked owner is recognised", brand({"owner": "Amazon Data Services, Inc."}) == "Amazon")
    ok("a substring match that is not the company is not",
       brand({"owner": "Metal Building Supplies of Texas"}) == "",
       brand({"owner": "Metal Building Supplies of Texas"}))
    ok("...nor is a company that merely starts the same way",
       brand({"owner": "Core & Main LP"}) == "", brand({"owner": "Core & Main LP"}))
    ok("...nor a nail bar", brand({"owner": "AUREA NAIL BAR"}) == "")
    # The two guards that stop a substring from becoming a company.
    ok("a leading boundary keeps EVANTAGE out of Vantage's column",
       brand({"owner": "EVANTAGE HOLDINGS LLC"}) == "",
       brand({"owner": "EVANTAGE HOLDINGS LLC"}))
    ok("a trailing boundary keeps Streamline out of Stream's",
       brand({"owner": "Streamline Services LLC"}) == "",
       brand({"owner": "Streamline Services LLC"}))
    ok("...while Stream itself still matches", brand({"owner": "Stream Data Centers"}) == "Stream")
    ok("the brand comes off the OWNER, never the project name",
       brand({"owner": "Some Developer LLC", "project": "Microsoft SAT99"}) == "",
       brand({"owner": "Some Developer LLC", "project": "Microsoft SAT99"}))

    # WHAT A FILING IS ABOUT. Exclusions run first, because the airport code convention is shared
    # between data halls and warehouses.
    ok("a data centre filing is one", is_datacenter({"project": "SAT46",
                                                     "scope": "New data center building"}))
    ok("a warehouse using the same naming convention is NOT",
       not is_datacenter({"project": "Fulfillment Center DFW7", "scope": "Racking"}))
    ok("...even with the designation first",
       not is_datacenter({"project": "DFW7 Fulfillment", "scope": ""}))
    ok("a cafe refresh is not", not is_datacenter({"project": "MICROSOFT CAFE REFRESH"}))
    ok("a colocation building is", is_datacenter({"project": "AUS02",
                                                  "scope": "New colocation facility"}))
    ok("a substation on a campus is", is_datacenter({"scope": "New substation and switchgear"}))

    # THE YEAR VIEW, and the gap it must not hide.
    yrs = by_year([{"start": "2020-01-01", "cost": 10, "sqft": 1},
                   {"start": "2022-01-01", "cost": 30, "sqft": 3}])
    ok("a year with no filings still appears", [y["year"] for y in yrs] == [2020, 2021, 2022], yrs)
    ok("...as a zero rather than a hole", yrs[1]["cost"] == 0 and yrs[1]["filings"] == 0, yrs)
    ok("no filings at all is an empty view rather than a crash", by_year([]) == [])

    svg = columns(yrs, "cost")
    ok("the drawing has one column per year", svg.count("cybar") == 3, svg.count("cybar"))
    ok("...and an empty year still draws a visible floor",
       'height="1.00"' in svg, [x for x in svg.split() if x.startswith("height")])
    ok("...and it is deterministic", columns(yrs, "cost") == svg)
    ok("nothing to draw is an empty string, not a broken svg", columns([], "cost") == "")

    # THE JOIN, and the overclaim it refuses. A parent company name is not a building.
    facs = [{"a-corp", "vantage-tx304"}, {"a-corp", "vantage-tx305"}, {"a-corp"}]
    spec = joinable(facs)
    ok("a single purpose entity is joinable", "vantage-tx304" in spec, sorted(spec))
    ok("a parent named on three facilities is not", "a-corp" not in spec, sorted(spec))
    by = {"vantage-tx304": [{"number": "x"}], "a-corp": [{"number": "y"}]}
    got = filings_for({"a-corp", "vantage-tx304"}, spec, by)
    ok("...so the join takes the building and leaves the company",
       [r["number"] for r in got] == ["x"], got)
    ok("a facility naming no specific party joins nothing",
       filings_for({"a-corp"}, spec, by) == [])
    ok("one filing reached by two parties is not counted twice",
       len(filings_for({"vantage-tx304", "vantage-tx305"},
                       joinable([{"vantage-tx304", "vantage-tx305"}]),
                       {"vantage-tx304": [{"number": "x"}],
                        "vantage-tx305": [{"number": "x"}]})) == 1)

    # DOUBLE COUNTING ACROSS OWNERS, which a statewide total is exposed to and a single
    # company view is not.
    same = [{"number": "a", "address": "1 Way", "cost": 5, "owner": "A LLC"},
            {"number": "b", "address": "1 WAY", "cost": 5, "owner": "B LLC"}]
    ok("one building filed by two owners is reported", len(shared_buildings(same)) == 1, same)
    ok("...matching the address case insensitively",
       shared_buildings(same)[0]["filings"] == ["a", "b"])
    ok("the same owner filing twice is not a cross owner duplicate",
       shared_buildings([same[0], {**same[1], "owner": "A LLC"}]) == [])
    ok("two buildings that merely cost the same are not",
       shared_buildings([same[0], {**same[1], "address": "2 Way"}]) == [])
    ok("a filing with no cost is never paired",
       shared_buildings([{**same[0], "cost": None}, {**same[1], "cost": None}]) == [])

    # THE JOINER, whose whole reason is the two item case a naive join reads wrong.
    ok("two names take the conjunction and no comma", andlist(["A", "B"]) == "A and B")
    ok("three names take commas and the conjunction", andlist(["A", "B", "C"]) == "A, B and C")
    ok("one name is itself", andlist(["A"]) == "A")
    ok("no names is nothing", andlist([]) == "")
    ok("the list is not consumed", (lambda g: (andlist(g), len(g)))(["A", "B"])[1] == 2)

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
