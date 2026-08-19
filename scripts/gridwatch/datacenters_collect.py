#!/usr/bin/env python3
"""The Texas data center registry. Who is operating one, and since when.

WHY THIS SOURCE AND NOT ANOTHER. It is the only public source tested that NAMES DATA
CENTERS. ERCOT publishes a system total and per site metering is confidential, so every
other feed on this site measures the grid and leaves attribution to inference. The
Comptroller publishes a roster: owner, occupant, operator and an effective date, for every
facility registered for the state's data center exemption.

WHAT IT CANNOT DO, AND THIS IS A LAW HERE. It carries no county and no capacity, so it can
never say what any of these draw. The registry names facilities, ERCOT gives a system total,
and the distance between them is the gap this project already publishes honestly. A modelled
per site figure would trade the page's best property for a number, so this collector stores
what was filed and nothing derived from it.

WHAT IS STORED AND WHY TWICE. The roster is a CURRENT STATE, not a series: rows appear and
their exemptions end. So `datacenters.json` holds the whole roster as read, and
`datacenters.jsonl` appends one small record per read, carrying counts only. That keeps a
daily or weekly reading from writing 149 rows into an append only file forever while still
making the count a real series.

NOT ON THE DAILY CRON. Its own workflow at its own cadence, because an outage at the
Comptroller must never be able to cost an ERCOT demand day.
"""
from __future__ import annotations

import argparse
import collections
import datetime as _dt
import gzip
import hashlib
import html as _html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROSTER = REPO_ROOT / "ledger" / "gridwatch" / "datacenters.json"
SERIES = REPO_ROOT / "ledger" / "gridwatch" / "datacenters.jsonl"
RAW = REPO_ROOT / "ledger" / "gridwatch" / "raw"

URL = "https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php"
# The Comptroller's site answers a bare urllib agent with its own error page rather than the
# table, the same way EIA does. A browser agent is the difference between a reading and a
# silent zero, and a silent zero here would look exactly like a registry that emptied.
UA = "Mozilla/5.0 (X11; Linux x86_64) TexasAIDocket/1.0 (+https://texasaidocket.com)"

ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
DATE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")

# A registry that suddenly holds three rows is a parse that broke, not an industry that left.
# The floor is deliberately far below the 149 read in August 2026: it exists to catch a
# collapse, not to police growth, and a real drop should still be publishable.
PLAUSIBLE_ROWS = (25, 5000)


def fetch(url: str = URL) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


LI = re.compile(r"<li[^>]*>(.*?)</li>", re.S | re.I)


def _text(cell: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(TAG.sub(" ", cell))).strip()


def _names(cell: str) -> list[str]:
    """One cell's parties, as a list, because a facility can have more than one.

    THE REGISTRY NESTS A <ul class="dc-list"> INSIDE A CELL when a site has several owners or
    operators. Flattening that with the tag stripper produced "C1 Dallas - Allen (LOT 1) LLC
    Oracle America, Inc." as a single operator: two real companies welded into one name that
    belongs to neither, counted once, against a filer that does not exist.

    So a cell with list items yields its items and a plain cell yields itself. A facility with
    two operators counts once for each, which is what the registry says.
    """
    items = LI.findall(cell)
    if items:
        return [t for t in (_text(i) for i in items) if t]
    t = _text(cell)
    return [t] if t else []


def parse(page: str) -> dict:
    """Every registered facility, or an explanation of what did not match.

    THE HEADER IS FOUND, NOT ASSUMED. The page carries more than one table and the
    Comptroller controls the layout, so the columns are located by name and the row shape is
    checked against them. A parser that trusts position is a parser that silently reads the
    wrong column the first time a table is added above it.
    """
    rows = ROW.findall(page)
    header, idx = None, {}
    for r in rows:
        cells = [_text(c) for c in CELL.findall(r)]
        if "Data Center" in cells and "Effective Date" in cells:
            header, idx = cells, {c: i for i, c in enumerate(cells) if c}
            break
    if header is None:
        return {"verified": False,
                "note": "no table with a Data Center and Effective Date header; the "
                        "Comptroller may have changed the page"}

    need = ("Data Center", "Effective Date", "Owner Name", "Occupant Name", "Operator Name")
    missing = [c for c in need if c not in idx]
    if missing:
        return {"verified": False, "note": f"header is missing {', '.join(missing)}"}

    out = []
    for r in rows:
        cells = [_text(c) for c in CELL.findall(r)]
        if len(cells) <= idx["Effective Date"]:
            continue
        eff = cells[idx["Effective Date"]]
        m = DATE.match(eff)
        if not m:
            continue                       # header row, or a row that carries no date
        mm, dd, yyyy = m.groups()
        raw = CELL.findall(r)
        out.append({
            "name": cells[idx["Data Center"]],
            "effective": f"{yyyy}-{mm}-{dd}",
            "owners": _names(raw[idx["Owner Name"]]),
            "occupants": _names(raw[idx["Occupant Name"]]),
            "operators": _names(raw[idx["Operator Name"]]),
        })

    lo, hi = PLAUSIBLE_ROWS
    if not lo <= len(out) <= hi:
        return {"verified": False,
                "note": f"{len(out)} facilities is outside the plausible envelope {lo} to "
                        f"{hi}; the table shape probably changed"}
    if any(not r["name"] for r in out):
        return {"verified": False, "note": "a facility row carries no name"}

    out.sort(key=lambda r: (r["effective"], r["name"]))
    return {"verified": True, "note": "", "facilities": out}


def opkey(name: str) -> str:
    """A grouping key for one operator, deliberately conservative.

    THE REGISTRY SPELLS ONE COMPANY SEVERAL WAYS. The first live read held "Amazon Data
    Services, Inc." seven times and "Amazon Data Services Inc." three more, which are one
    filer and would publish as two operators with the wrong counts against both.

    So the key folds case, collapses whitespace and drops the punctuation around a corporate
    suffix, AND NOTHING ELSE. It does not strip the suffix itself, does not stem, and does not
    fuzzy match: "Vantage Data Centers" and "Vantage Data Centers Management" stay separate,
    because merging two filers that are genuinely different is a worse error than listing one
    filer twice, and only the second is visible to a reader who knows the industry.
    """
    n = re.sub(r"\s+", " ", (name or "")).strip().lower()
    n = re.sub(r"[.,]", "", n)
    return n


def summarise(facs: list[dict]) -> dict:
    """The counts the page publishes, computed here so nothing downstream computes."""
    by_year = collections.Counter(f["effective"][:4] for f in facs)
    ops: collections.Counter = collections.Counter()
    spellings: dict = {}
    for f in facs:
        # The operator is the party actually running the site, and it is the name a reader
        # recognises. Where it is blank the occupant is the best available answer and is
        # labelled as such rather than silently substituted.
        names = f["operators"] or f["occupants"]
        # A facility counts ONCE per distinct operator, so a site listing the same filer twice
        # does not inflate it and a site with two real operators counts for both.
        for name in {n for n in names if n}:
            k = opkey(name)
            ops[k] += 1
            # The spelling shown is the one the registry uses most often for that filer, so
            # the page prints a name the Comptroller printed rather than one this code made.
            spellings.setdefault(k, collections.Counter())[name] += 1
    return {
        "total": len(facs),
        "by_year": dict(sorted(by_year.items())),
        "first_year": min(by_year) if by_year else None,
        "latest_year": max(by_year) if by_year else None,
        "operators": [{"name": spellings[k].most_common(1)[0][0], "sites": c}
                      for k, c in ops.most_common(12)],
        "distinct_operators": len(ops),
    }


def collect(roster: Path = ROSTER, series: Path = SERIES) -> int:
    today = _dt.date.today().isoformat()
    try:
        page = fetch().decode("utf-8", "replace")
    except Exception as exc:                                       # noqa: BLE001
        rec = {"date": today, "verified": False, "note": f"fetch failed: {exc}"}
    else:
        RAW.mkdir(parents=True, exist_ok=True)
        (RAW / f"{today}-datacenters.html.gz").write_bytes(gzip.compress(page.encode()))
        got = parse(page)
        if not got.get("verified"):
            rec = {"date": today, **got}
        else:
            facs = got["facilities"]
            digest = hashlib.sha256(
                json.dumps(facs, sort_keys=True).encode()).hexdigest()[:16]
            roster.parent.mkdir(parents=True, exist_ok=True)
            roster.write_text(json.dumps(
                {"_spec": 1, "read": today, "source": URL, "digest": digest,
                 "facilities": facs}, indent=1, ensure_ascii=False) + "\n",
                encoding="utf-8")
            rec = {"date": today, "verified": True, "note": "", "digest": digest,
                   **summarise(facs)}

    # A FAILED READ CARRIES NO COUNT FORWARD, same law as every other series here. The
    # record says plainly that this read is unverified rather than repeating the last one,
    # because a repeated count is indistinguishable from a registry that did not move.
    rec.setdefault("_spec", 1)
    rec["read_at"] = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    series.parent.mkdir(parents=True, exist_ok=True)
    with series.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    if rec.get("verified"):
        print(f"datacenters: {rec['total']} facilities, "
              f"{rec['distinct_operators']} operators, digest {rec['digest']}")
        return 0
    print(f"datacenters: UNVERIFIED: {rec['note']}")
    return 2


# --------------------------------------------------------------------------- self-test
GOOD = """<table><tr><th>Data Center</th><th>Effective Date</th><th>Owner Name</th>
<th>Owner Registration Number</th><th>Occupant Name</th><th>Occupant Registration Number</th>
<th>Operator Name</th><th>Operator Registration Number</th><th>Exemption End Date</th></tr>
%s</table>"""
ROWFMT = ("<tr><td>%s</td><td>%s</td><td>Owner LLC</td><td>DC1-OW1</td><td>Occ Inc</td>"
          "<td>DC1-OC1</td><td>%s</td><td>DC1-OP1</td><td>12/31/2035</td></tr>")


def _page(n=40, operator="Amazon Data Services"):
    rows = "".join(ROWFMT % (f"Site {i} Data Center", f"0{1 + i % 9}/1{i % 9}/202{i % 6}",
                             operator if i % 3 else "Google LLC")
                   for i in range(n))
    return GOOD % rows


def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    good = parse(_page())
    check("a well formed registry parses", good.get("verified") is True, str(good)[:120])
    check("every facility is read", len(good.get("facilities", [])) == 40,
          str(len(good.get("facilities", []))))
    check("the effective date becomes ISO",
          all(re.match(r"\d{4}-\d{2}-\d{2}$", f["effective"]) for f in good["facilities"]))
    check("rows come back oldest first",
          [f["effective"] for f in good["facilities"]]
          == sorted(f["effective"] for f in good["facilities"]))

    s = summarise(good["facilities"])
    check("the total is the row count", s["total"] == 40, str(s["total"]))
    check("years are counted", sum(s["by_year"].values()) == 40, str(s["by_year"]))
    check("operators are ranked", s["operators"][0]["sites"] >= s["operators"][-1]["sites"],
          str(s["operators"][:2]))

    # EVERY GUARD IS FED THE INPUT IT EXISTS TO REJECT. A checker that cannot go red proves
    # nothing about the thing it guards.
    check("a page with no registry table is refused",
          parse("<html><table><tr><td>nothing</td></tr></table></html>")
          .get("verified") is False)
    check("...and says why",
          "Comptroller may have changed" in parse("<p>hi</p>").get("note", ""))
    renamed = _page().replace("<th>Operator Name</th>", "<th>Running It</th>")
    check("a renamed column is refused rather than read positionally",
          parse(renamed).get("verified") is False, str(parse(renamed))[:90])
    check("a collapsed registry is refused", parse(_page(3)).get("verified") is False)
    nameless = _page().replace("<td>Site 1 Data Center</td>", "<td>  </td>")
    check("a nameless facility is refused", parse(nameless).get("verified") is False)

    # The occupant stands in when no operator is named, and is not silently dropped.
    noop = parse(_page().replace("<td>Amazon Data Services</td>", "<td></td>"))
    if noop.get("verified"):
        s2 = summarise(noop["facilities"])
        check("a blank operator falls back to the occupant",
              any(o["name"] == "Occ Inc" for o in s2["operators"]), str(s2["operators"][:3]))

    merged = parse(_page(30, operator="Amazon Data Services, Inc."))
    both = merged["facilities"]
    both[0]["operators"] = ["Amazon Data Services Inc."]   # same filer, no commas
    s3 = summarise(both)
    names = [o["name"] for o in s3["operators"]]
    check("one filer spelled two ways counts once",
          sum(1 for n in names if "amazon" in n.lower()) == 1, str(names[:4]))
    check("...and the shown spelling is one the registry used",
          any(o["name"] in ("Amazon Data Services, Inc.", "Amazon Data Services Inc.")
              for o in s3["operators"]), str(names[:3]))
    check("but two genuinely different filers stay apart",
          opkey("Vantage Data Centers") != opkey("Vantage Data Centers Management"))

    # A plausible page PLUS one facility whose operator cell nests a list, which is how the
    # registry files a site with more than one operator.
    twin = ROWFMT % ("Twin Op Data Center", "01/05/2025",
                     '<ul class="dc-list"><li>Alpha Power LLC</li><li>Beta Compute Inc</li></ul>')
    two = parse(_page().replace("</table>", twin + "</table>"))
    twinrec = next(f for f in two["facilities"] if f["name"] == "Twin Op Data Center")
    check("a cell listing two operators yields two",
          twinrec["operators"] == ["Alpha Power LLC", "Beta Compute Inc"],
          str(twinrec["operators"]))
    s4 = summarise([twinrec])
    check("...and each is counted once",
          {o["name"] for o in s4["operators"]} == {"Alpha Power LLC", "Beta Compute Inc"},
          str(s4["operators"]))
    check("...and neither is welded into one name",
          not any(" LLCBeta" in o["name"] or "LLC Beta" in o["name"]
                  for o in s4["operators"]), str(s4["operators"]))

    print("\ndatacenters self-test " + ("clean" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.collect:
        ap.print_help()
        return 1
    return collect()


if __name__ == "__main__":
    sys.exit(main())
