"""registry_changes.py — the state edits this list in place, and nobody was watching.

WHAT THIS IS FOR

The Comptroller's certified data center list is not append only. Rows are ADDED, and existing
rows are REWRITTEN while keeping their original effective date. Between the readings of August
19th and August 21st of 2026, two rows were added and two were changed in place. One of them,
`Hutto Data Center Campus LLC`, had its owner replaced by three different entities including a
POWER company, against an unchanged effective date of March 10th, 2025.

That single fact governs how every page on this site may speak about the registry.

    A ROW'S PARTIES ARE CURRENT AS OF THE READING. The effective date says when the exemption
    was granted. It does NOT say who held it then. `HELO1 DC` carries an effective date of June
    2021 and names Galaxy, which bought that site in late 2022, and CoreWeave, which leased it
    in 2025. Nothing is wrong with the row. It is simply not a historical record.

    A SECOND ROW IS STILL A SECOND CERTIFICATION. Cipher Black Pearl and Cedarvale each hold two
    rows with different dates and different occupants, and that remains the strongest evidence
    of tenancy changing hands. What cannot be said is that a single row shows who held it on its
    own effective date.

WHY IT IS COMPUTED AND NOT STORED

This is a pure function of the raw snapshots the collector already keeps, so it is derived at
build time rather than written into a ledger of its own. There is no second copy to fall out of
step, no append only file to protect, and a snapshot recovered later slots straight in.

THE RECORD STARTS WHEN THE SNAPSHOTS DO. The collector's first reading is August 19th of 2026,
so nothing before that can be reported and the page says so rather than implying the list was
stable before anyone was looking.

    registry_changes.py               # summarise what has changed
    registry_changes.py --self-test   # hermetic
"""
from __future__ import annotations

import argparse
import gzip
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "ledger" / "gridwatch" / "raw"
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
# A CELL HOLDING SEVERAL PARTIES HOLDS A LIST, and stripping tags alone glues the list into one
# string. Hutto Data Center Campus has three owners in one cell, and they came out as
# "Hutto Data Center 1 LLC Hutto Data Center 2 LLC Hutto Data Center Campus Power LLC". Where
# the state left no whitespace between two items the join was worse still: two registration
# numbers ran together into "LD370879-OP2LD370879-OP3", a token that is not either of them.
#
# It is not only unreadable. Two different lists can glue to the same string, and one list can
# glue to two different strings depending on the whitespace the state happened to leave, so the
# comparison this whole file performs was being made on a lossy rendering of the cell.
ITEM = re.compile(r"</li\s*>|<br\s*/?>", re.I)
JOIN = " / "


def cells(chunk: str) -> list[str]:
    out = []
    for c in CELL.findall(chunk):
        parts = [re.sub(r"\s+", " ", TAG.sub("", x)).strip() for x in ITEM.split(c)]
        t = JOIN.join(x for x in parts if x)
        if t:
            out.append(t)
    return out


def parse(html: str) -> dict[str, list[str]]:
    """Facility name to the rest of its row. The name is the key the state itself uses."""
    rows: dict[str, list[str]] = {}
    for m in ROW.finditer(html):
        c = cells(m.group(1))
        if len(c) >= 2:
            rows.setdefault(c[0], c[1:])
    return rows


def snapshots(path: pathlib.Path = RAW) -> list[tuple[str, dict]]:
    out = []
    for p in sorted(path.glob("*-datacenters.html.gz")):
        try:
            html = gzip.open(p, "rt", encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        out.append((p.name[:10], parse(html)))
    return out


# WHAT THE COLUMNS ARE. The Comptroller's table is fixed and unlabelled after the facility name,
# so the reader gets a run of anonymous strings unless the shape is written down. Listing it here
# rather than in the page keeps the knowledge of the source beside the code that reads it.
COLUMNS = ("Effective", "Owner", "Owner ID", "Occupant", "Occupant ID",
           "Operator", "Operator ID", "Note")


def fields(entry: dict) -> list[dict]:
    """Only the columns that actually moved, named.

    Printing the whole row twice puts a reader in the position of diffing two long strings by
    eye, which is the job this page exists to have already done."""
    b, a = entry["before"], entry["after"]
    out = []
    for i in range(max(len(b), len(a))):
        was = b[i] if i < len(b) else ""
        now = a[i] if i < len(a) else ""
        if _norm_date(was) == _norm_date(now):
            continue
        out.append({"label": COLUMNS[i] if i < len(COLUMNS) else f"Column {i + 1}",
                    "was": was, "now": now})
    return out


def diff(before: dict, after: dict) -> dict:
    """What moved between two readings, by facility name."""
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = []
    for k in sorted(set(before) & set(after)):
        if before[k] != after[k]:
            changed.append({"name": k, "before": before[k], "after": after[k]})
    return {"added": added, "removed": removed, "changed": changed}


def _norm_date(s: str) -> str:
    return s.replace("-", "/")


def substantive(entry: dict) -> bool:
    """A changed row whose difference is more than a date being reformatted.

    The state normalised `04-16-2026` to `04/16/2026` on one row, which is not news and would
    bury the row where an owner was replaced. A change is substantive when the cells still
    differ after date separators are normalised.
    """
    b = [_norm_date(x) for x in entry["before"]]
    a = [_norm_date(x) for x in entry["after"]]
    return b != a


def history(path: pathlib.Path = RAW) -> list[dict]:
    """Every transition between consecutive readings, oldest first."""
    snaps = snapshots(path)
    out = []
    for (d0, r0), (d1, r1) in zip(snaps, snaps[1:]):
        d = diff(r0, r1)
        d["from"], d["to"] = d0, d1
        d["substantive"] = [c for c in d["changed"] if substantive(c)]
        out.append(d)
    return out


def load() -> dict:
    snaps = snapshots()
    return {"first": snaps[0][0] if snaps else None,
            "last": snaps[-1][0] if snaps else None,
            "readings": len(snaps),
            "history": history()}


def problems(data: dict) -> list[str]:
    out = []
    if data["readings"] and data["readings"] < 2:
        out.append("only one reading is held, so nothing can be compared yet")
    for h in data["history"]:
        if h["from"] >= h["to"]:
            out.append(f"transition {h['from']} to {h['to']} runs backwards")
    return out


def self_test() -> int:
    import tempfile
    checks = []

    def ok(n, c, x=""):
        checks.append(bool(c))
        print(f"  {'ok  ' if c else 'FAIL'}  {n}{'' if c else '  ' + str(x)}")

    def page(rows):
        body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return f"<html><table>{body}</table></html>"

    a = parse(page([["A", "01/01/2025", "Owner One"], ["B", "02/02/2025", "Owner Two"]]))
    ok("a row parses to its facility name and the rest", a["A"] == ["01/01/2025", "Owner One"], a)

    # THE PARSE DEFECT, replayed with the exact markup that produced it. The state writes the
    # parties as a list, and it does not always leave whitespace between the items.
    lst = parse(page([["A", "<ul><li>One LLC</li>\n<li>Two LLC</li></ul>",
                       "<ul><li>LD1-OP2</li><li>LD1-OP3</li></ul>"]]))
    ok("several parties in one cell stay several",
       lst["A"][0] == "One LLC / Two LLC", lst["A"])
    ok("...and two items with no whitespace between them do not fuse",
       lst["A"][1] == "LD1-OP2 / LD1-OP3", lst["A"])
    ok("a line break separates as a list item does",
       parse(page([["A", "One LLC<br>Two LLC"]]))["A"] == ["One LLC / Two LLC"],
       parse(page([["A", "One LLC<br>Two LLC"]])))
    # The comparison is what the parse is FOR, so the two lists that used to glue to one string
    # have to come out different.
    one = parse(page([["A", "<ul><li>X Y</li><li>Z</li></ul>"]]))
    two = parse(page([["A", "<ul><li>X</li><li>Y Z</li></ul>"]]))
    ok("two different lists no longer read as the same cell", one["A"] != two["A"],
       (one["A"], two["A"]))

    b = parse(page([["A", "01/01/2025", "Owner One"], ["C", "03/03/2025", "Owner Three"]]))
    d = diff(a, b)
    ok("an added row is reported", d["added"] == ["C"], d["added"])
    ok("a removed row is reported", d["removed"] == ["B"], d["removed"])
    ok("an untouched row is not reported", d["changed"] == [], d["changed"])

    # THE DEFECT THIS EXISTS FOR: an owner replaced while the date stands still.
    c = parse(page([["A", "01/01/2025", "Owner One Split, Owner One Power"]]))
    d2 = diff(a, c)
    ok("a row rewritten in place is reported", len(d2["changed"]) == 1, d2["changed"])
    ok("...and it is substantive", substantive(d2["changed"][0]))
    ok("...and the effective date is unchanged in it",
       d2["changed"][0]["before"][0] == d2["changed"][0]["after"][0])

    # AND THE NOISE IT MUST NOT REPORT AS NEWS.
    e = parse(page([["A", "01-01-2025", "Owner One"], ["B", "02/02/2025", "Owner Two"]]))
    d3 = diff(e, a)
    ok("a date reformatted alone is a change", len(d3["changed"]) == 1)
    ok("...but is not substantive", not substantive(d3["changed"][0]), d3["changed"][0])

    with tempfile.TemporaryDirectory() as t:
        p = pathlib.Path(t)
        import io
        for day, rows in (("2026-01-01", [["A", "01/01/2025", "X"]]),
                          ("2026-01-02", [["A", "01/01/2025", "Y"]]),
                          ("2026-01-03", [["A", "01/01/2025", "Y"], ["B", "01/03/2026", "Z"]])):
            with gzip.open(p / f"{day}-datacenters.html.gz", "wt", encoding="utf-8") as fh:
                fh.write(page(rows))
        h = history(p)
        ok("a transition per consecutive pair", len(h) == 2, len(h))
        ok("...oldest first", h[0]["from"] == "2026-01-01", h[0]["from"])
        ok("...catching the rewrite then the addition",
           len(h[0]["substantive"]) == 1 and h[1]["added"] == ["B"], h)

    # ONLY WHAT MOVED, AND NAMED. The page used to print the whole row twice.
    f = fields({"before": ["01/01/2025", "Owner One", "LD1-OW1"],
                "after": ["01/01/2025", "Owner Two", "LD1-OW1"]})
    ok("an unchanged column is not shown", len(f) == 1, f)
    ok("...and the one that moved carries its column name", f[0]["label"] == "Owner", f)
    ok("...with both sides of it", (f[0]["was"], f[0]["now"]) == ("Owner One", "Owner Two"), f)
    ok("a date that was only reformatted is not shown as a change",
       fields({"before": ["01-01-2025", "X"], "after": ["01/01/2025", "X"]}) == [],
       fields({"before": ["01-01-2025", "X"], "after": ["01/01/2025", "X"]}))
    ok("a column the state added is shown against an empty before",
       fields({"before": ["01/01/2025"], "after": ["01/01/2025", "New"]})
       == [{"label": "Owner", "was": "", "now": "New"}],
       fields({"before": ["01/01/2025"], "after": ["01/01/2025", "New"]}))

    ok("a single reading reports that nothing can be compared",
       problems({"readings": 1, "history": []}))
    ok("a backwards transition fails",
       problems({"readings": 2, "history": [{"from": "2026-02-02", "to": "2026-01-01"}]}))

    passed = sum(checks)
    print(f"\nregistry_changes self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    data = load()
    bad = problems(data)
    if bad:
        print(f"registry_changes: {len(bad)} problem(s)")
        for b in bad:
            print(f"  {b}")
        return 1
    print(f"registry_changes: {data['readings']} reading(s), "
          f"{data['first']} to {data['last']}")
    for h in data["history"]:
        print(f"  {h['from']} -> {h['to']}: "
              f"{len(h['added'])} added, {len(h['removed'])} removed, "
              f"{len(h['substantive'])} rewritten in place")
        for c in h["substantive"]:
            print(f"      {c['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
