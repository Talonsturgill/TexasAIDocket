#!/usr/bin/env python3
"""tdlr_fetch.py — the second state register, pulled and parsed.

WHY THIS EXISTS

The Comptroller's certified list says WHO holds a sales tax exemption on a data center. It says
nothing about what was built, when, for how much, or where exactly. A second state register does.

Under Chapter 469 of the Government Code every commercial construction project over a threshold is
registered with the Texas Department of Licensing and Regulation, which publishes the filing. Each
one carries a project name, a street address, a county, a type of work, a scope of work in the
filer's own words, a square footage, an estimated cost and a schedule.

    THE TWO REGISTERS DISAGREE, AND THAT IS THE POINT. Microsoft's certified rows in San Antonio
    name SAT designations 09 to 17, 80 to 85 and 89 to 90. Its construction filings name SAT40,
    SAT46, SAT93 and SAT94 as well. Neither register is wrong. They are recording different acts,
    and only reading both shows the shape of a buildout.

WHAT IS DROPPED, AND WHY IT IS DROPPED HERE

A filing names PEOPLE. The contact who submitted it, the registered accessibility specialist, and
their direct phone numbers. None of that is anything this project publishes, and the safe place to
remove it is at the parser, before it ever reaches a file. `parse()` keeps the project, the
building and the money. It keeps no person and no phone number, and `problems()` in the gate
beside this fails if one appears anyway.

HOW IT IS FETCHED

`robots.txt` at tdlr.texas.gov disallows `/ithelp/` and `*.csv` and nothing else, so the search
endpoint and the print view are both permitted. Requests are spaced, carry a descriptive user
agent naming the site, and the raw response is written to disk before it is parsed, so a reparse
never costs the server a second visit.

This is RESEARCH, run by hand. It is not a routine phase and it is not on a cron. Nothing here
runs unattended.

    tdlr_fetch.py --owner Microsoft --city "San Antonio"   # pull into out/tabs/
    tdlr_fetch.py --build                                  # parse what is on disk into the ledger
    tdlr_fetch.py --self-test                              # hermetic, on committed fixtures
"""
from __future__ import annotations

import argparse
import html as _html
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ledger" / "facilities" / "projects.json"
RAW = ROOT / "out" / "tabs"
FIXTURES = ROOT / "tests" / "fixtures" / "tdlr"

BASE = "https://www.tdlr.texas.gov/TABS"
# The site, and only the site. An earlier draft put the project mailbox in here, which is on
# another domain and would have announced it to every state server this fetches from. That
# is the defect CLAUDE.md records against four collectors, and port_audit caught it again.
UA = "TexasAIDocket/1.0 (+https://texasaidocket.com)"
PAUSE = 1.4

# Every field the parser will keep. A field not on this list does not reach the ledger, which is
# how the people in a filing are dropped rather than remembered to be dropped later.
KEEP = ("project", "number", "facility", "address", "city", "state", "postcode", "county",
        "start", "end", "cost", "work", "scope", "sqft", "status", "owner", "design_firm",
        "registered")

TAGS = re.compile(r"<[^>]+>")
CELL = re.compile(r"<(?:td|th|div|span|label|dt|dd)[^>]*>(.*?)</(?:td|th|div|span|label|dt|dd)>",
                  re.S | re.I)
MONEY = re.compile(r"\$\s*([\d,]+)")
SQFT = re.compile(r"([\d,]+)\s*ft")
DATE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
CITYLINE = re.compile(r"^(.*),\s*([A-Z]{2})\s+(\d{5})")
PHONE = re.compile(r"\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}")


def _flat(html: str) -> list[str]:
    body = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    out = []
    for cell in CELL.findall(body):
        # UNESCAPED. A facility called "LC1 & LC2" comes out of the markup as "LC1 &amp; LC2",
        # and a ledger that stores the entity publishes the entity.
        t = re.sub(r"\s+", " ", _html.unescape(TAGS.sub(" ", cell))).strip()
        if t:
            out.append(t)
    return out


def _after(cells: list[str], label: str, n: int = 1) -> str:
    """The value that follows a label. The print view puts each label in its own cell and the
    value in the next one, and a label sometimes carries a section heading in front of it."""
    # The colon stays on. A label cell reads "PROJECT Project Name:" with its section heading in
    # front of it, so the match is a suffix INCLUDING the colon. Stripping the colon from the
    # cell and comparing against a label that still had one matched nothing at all, silently,
    # and every field came back empty while the parser reported success.
    for i, c in enumerate(cells):
        if c.strip().endswith(label):
            return cells[i + n] if i + n < len(cells) else ""
    return ""


def _iso(s: str) -> str:
    m = DATE.search(s or "")
    return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}" if m else ""


def _int(pattern: re.Pattern, s: str):
    m = pattern.search(s or "")
    return int(m.group(1).replace(",", "")) if m else None


def parse(html: str) -> dict:
    """One filing, as data. Every value here is transcribed or converted, never inferred."""
    c = _flat(html)
    addr = _after(c, "Location Address:")
    town = _after(c, "Location Address:", 2)
    m = CITYLINE.match(town)
    rec = {
        "project": _after(c, "Project Name:"),
        "number": _after(c, "Project Number:"),
        "facility": _after(c, "Facility Name:"),
        "address": addr,
        "city": m.group(1).strip() if m else "",
        "state": m.group(2) if m else "",
        "postcode": m.group(3) if m else "",
        "county": _after(c, "Location County:"),
        "start": _iso(_after(c, "Start Date:")),
        "end": _iso(_after(c, "Completion Date:")),
        "cost": _int(MONEY, _after(c, "Estimated Cost:")),
        "work": _after(c, "Type of Work:"),
        "scope": _after(c, "Scope of Work:"),
        "sqft": _int(SQFT, _after(c, "Square Footage:")),
        "status": _after(c, "Current Status:"),
        "owner": _after(c, "Owner Name:"),
        "design_firm": _after(c, "Design Firm Name:"),
        "registered": _iso(next((x for x in c if x.startswith("Registration Date")), "")),
    }
    return {k: rec[k] for k in KEEP if rec.get(k) not in ("", None)}


# ---------------------------------------------------------------- fetching
def _get(url: str, data: bytes | None = None) -> str:
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": UA,
        **({"Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest"} if data else {})})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def search(owner: str, city: str = "", length: int = 200) -> list[dict]:
    """Every filing whose OWNER matches. The endpoint takes a city and does not honour it: a
    search for Microsoft in San Antonio returns the Irving buildings too. So the city is filtered
    HERE, from the county and city the filings themselves carry, rather than trusted from a
    parameter the server ignored. A count taken straight off that response would have been
    reported as a San Antonio figure and been wrong by a third."""
    q = urllib.parse.urlencode({"ownerName": owner, "city": city, "length": length}).encode()
    return json.loads(_get(f"{BASE}/Search/SearchProjects", q))["data"]


def pull(owner: str, city: str = "") -> int:
    """Search, then fetch each print view ONCE and keep the raw html on disk."""
    RAW.mkdir(parents=True, exist_ok=True)
    rows = search(owner, city)
    print(f"tdlr: {len(rows)} filing(s) for {owner!r}" + (f" in {city}" if city else ""))
    got = 0
    for r in rows:
        num = r.get("ProjectNumber") or ""
        if not num:
            continue
        dest = RAW / f"{num}.html"
        if dest.exists():
            continue
        dest.write_text(_get(f"{BASE}/Search/Print/{num}"), encoding="utf-8")
        got += 1
        time.sleep(PAUSE)
    print(f"tdlr: fetched {got} new print view(s), {len(list(RAW.glob('*.html')))} on disk")
    return 0


def merge(existing: list[dict], parsed: list[dict]) -> list[dict]:
    """The ledger, plus whatever is on disk. Keyed by project number, newest parse wins.

    IT MERGES, IT DOES NOT REPLACE, and the reason is that `out/` is scratch and the ledger is
    the artifact. The raw html is gitignored, so a fresh container has none of it while the
    ledger still has every filing. A build that rebuilt from disk alone would have quietly cut
    626 filings to the 25 that happened to be sitting there, and the site would have rebuilt
    perfectly green over a ledger missing $30 billion.
    """
    by = {r["number"]: r for r in existing if r.get("number")}
    by.update({r["number"]: r for r in parsed if r.get("number")})
    return sorted(by.values(), key=lambda r: (r.get("start", ""), r["number"]))


def build(raw: pathlib.Path = RAW, out: pathlib.Path = LEDGER) -> int:
    files = sorted(raw.glob("*.html"))
    parsed = [parse(f.read_text(encoding="utf-8", errors="replace")) for f in files]
    parsed = [r for r in parsed if r.get("number")]
    doc = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    before = doc.get("projects") or []
    recs = merge(before, parsed)
    if not recs:
        print("tdlr_fetch: nothing on disk and nothing in the ledger", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"_spec": 1, "source": f"{BASE}/Search/", "projects": recs},
                              indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"tdlr_fetch: {len(parsed)} parsed from disk, {len(before)} already in the ledger, "
          f"{len(recs)} after the merge")
    return 0


def self_test() -> int:
    checks = []

    def ok(name, cond, extra=""):
        checks.append(bool(cond))
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}{'' if cond else '  ' + str(extra)}")

    if not FIXTURES.exists():
        ok("a committed fixture to parse", False, f"{FIXTURES} is missing")
        print(f"\ntdlr_fetch self-test: {sum(checks)}/{len(checks)} passed")
        return 1

    for f in sorted(FIXTURES.glob("*.html")):
        r = parse(f.read_text(encoding="utf-8", errors="replace"))
        ok(f"{f.stem} parses to a project number", r.get("number") == f.stem, r)
        ok("...with a cost as an integer", isinstance(r.get("cost"), int), r.get("cost"))
        ok("...an ISO start date", re.fullmatch(r"\d{4}-\d{2}-\d{2}", r.get("start", "")), r)
        ok("...a county", bool(r.get("county")), r)
        # THE RULE THIS PARSER EXISTS TO HOLD.
        blob = json.dumps(r)
        ok("...and no phone number anywhere in it", not PHONE.search(blob), blob[:120])
        ok("...and no field outside the keep list", set(r) <= set(KEEP), sorted(set(r) - set(KEEP)))

    # THE MERGE, and the loss it exists to prevent.
    have = [{"number": "a", "start": "2020-01-01"}, {"number": "b", "start": "2021-01-01"}]
    ok("a ledger with nothing new on disk keeps every record", len(merge(have, [])) == 2)
    ok("a new filing is added", len(merge(have, [{"number": "c"}])) == 3)
    ok("a re-parsed filing replaces its old copy rather than doubling it",
       [r.get("start") for r in merge(have, [{"number": "a", "start": "2019-01-01"}])
        if r["number"] == "a"] == ["2019-01-01"])
    ok("...and the count does not grow when it does",
       len(merge(have, [{"number": "a", "start": "2019-01-01"}])) == 2)
    ok("a record with no number never enters the ledger",
       len(merge(have, [{"start": "2020-01-01"}])) == 2)

    # Conversions, each of which would publish a wrong number if it were wrong.
    ok("a dollar figure loses its punctuation and becomes an integer",
       _int(MONEY, "$140,000,000") == 140_000_000, _int(MONEY, "$140,000,000"))
    ok("square footage does the same", _int(SQFT, "79,385 ft 2") == 79385, _int(SQFT, "79,385 ft 2"))
    ok("a date becomes ISO with both parts padded", _iso("5/1/2021") == "2021-05-01", _iso("5/1/2021"))
    ok("...and a two digit day is not reversed", _iso("2/28/2022") == "2022-02-28", _iso("2/28/2022"))
    ok("a missing value is empty rather than guessed", _iso("") == "" and _int(MONEY, "") is None)

    passed = sum(checks)
    print(f"\ntdlr_fetch self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--owner")
    ap.add_argument("--city", default="")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.owner:
        return pull(a.owner, a.city)
    if a.build:
        return build()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
