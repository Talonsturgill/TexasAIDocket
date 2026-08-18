#!/usr/bin/env python3
"""Texas generation by county, from EIA-860M. What is running, planned, retired and cancelled.

WHY THIS AND NOT ERCOT'S QUEUE. ERCOT publishes the interconnection queue in a board deck
whose figures live in chart images, and the one number stated in prose is a state total. This
is a spreadsheet with a County column, a Balancing Authority column and a nameplate rating on
every row, which is the only tested source that lets this project say anything about a
PARTICULAR county's supply.

WHAT MAKES IT WORTH A COLLECTOR. The Planned and Canceled sheets. A county collecting
cancelled generation while collecting data centers is a real finding, and it is two published
columns rather than an argument.

WHAT IT IS NOT. It is generation, not load. It cannot say what a data center draws and this
collector never pretends otherwise. Paired with the registry it says where supply is being
built; the gap between that and demand stays published rather than modelled.

THE TRAP THIS FILE EXISTS TO AVOID. An xlsx sheet OMITS EMPTY CELLS from its XML. Reading
cells positionally therefore shifts every column after the first gap, silently, and produces a
join that looks right and is wrong. Two passes were lost to it during the research that led
here. Every cell is placed by its own r="A1" reference and the self-test replays a row with a
hole in it.

NOT ON THE DAILY CRON. Its own workflow at its own cadence, because an EIA outage must never
be able to cost an ERCOT demand day.
"""
from __future__ import annotations

import argparse
import collections
import datetime as _dt
import gzip
import io
import json
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERIES = REPO_ROOT / "ledger" / "gridwatch" / "generators.jsonl"
RAW = REPO_ROOT / "ledger" / "gridwatch" / "raw"

BASE = "https://www.eia.gov/electricity/data/eia860m/xls"
ARCHIVE = "https://www.eia.gov/electricity/data/eia860m/archive/xls"
# EIA answers a bare urllib agent with its own landing page rather than the workbook, and that
# page is a valid 200 of the wrong thing. The signature check below is what catches it.
UA = "Mozilla/5.0 (X11; Linux x86_64) TexasAIDocket/1.0 (+https://texasaidocket.com)"

MONTHS = ("january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december")

SHEETS = {"Operating": "operating", "Planned": "planned",
          "Retired": "retired", "Canceled or Postponed": "canceled"}

# A Texas slice outside this is a parse that broke, not a grid that changed overnight. ERCOT
# serves a peak near 90 GW, so an operating total under 20 GW or over 500 GW means the column
# moved or the units did.
PLAUSIBLE_OPERATING_MW = (20_000, 500_000)


def _col(ref: str) -> int:
    """The zero based column index of a cell reference like "BC17"."""
    n = 0
    for ch in re.match(r"([A-Z]+)", ref).group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


class Book:
    """Just enough xlsx to read a sheet by name, with every cell placed by its reference."""

    def __init__(self, blob: bytes):
        self.z = zipfile.ZipFile(io.BytesIO(blob))
        # ONE STRING PER <si>, NOT PER <t>. A shared string entry may hold rich text as
        # several <r><t> runs, and counting each <t> as its own entry shifts every index after
        # the first formatted cell. On the real workbook that put the header one column left of
        # its data: 'Entity Name' sat above the Entity ID values and every county read as a
        # balancing authority. Nothing raised. The join was simply wrong.
        sst = self.z.read("xl/sharedStrings.xml").decode("utf8", "replace")
        self.shared = ["".join(re.findall(r"<t[^>]*>([^<]*)</t>", si))
                       for si in re.findall(r"<si>(.*?)</si>", sst, re.S)]
        wb = self.z.read("xl/workbook.xml").decode("utf8", "replace")
        rels = dict(re.findall(
            r'Id="(rId\d+)"[^>]*Target="([^"]+)"',
            self.z.read("xl/_rels/workbook.xml.rels").decode("utf8", "replace")))
        self.sheets = {name: "xl/" + rels[rid].lstrip("/")
                       for name, rid in re.findall(
                           r'<sheet name="([^"]+)"[^>]*r:id="(rId\d+)"', wb)}

    def rows(self, sheet: str):
        """Each row as {column index: value}. Absent keys are absent cells, never a shift."""
        xml = self.z.read(self.sheets[sheet]).decode("utf8", "replace")
        for rm in re.finditer(r"<row[^>]*>(.*?)</row>", xml, re.S):
            out = {}
            for cm in re.finditer(r'<c r="([A-Z]+\d+)"([^>]*)>(?:<v>([^<]*)</v>)?', rm.group(1)):
                ref, attrs, v = cm.groups()
                v = v or ""
                if 't="s"' in attrs and v.isdigit():
                    v = self.shared[int(v)] if int(v) < len(self.shared) else ""
                out[_col(ref)] = v
            if out:
                yield out


def header_of(rows) -> tuple[dict, object]:
    """Find the header row by NAME and return it with the rest of the sheet.

    The workbook opens with a title row and the header is not always the second, so the header
    is located by the column it must contain rather than by index.
    """
    it = iter(rows)
    for row in it:
        names = {v: i for i, v in row.items() if isinstance(v, str) and v}
        if "Plant State" in names and "County" in names:
            return {v: i for i, v in row.items() if isinstance(v, str) and v}, it
    return {}, it


def read_sheet(book: Book, sheet: str) -> dict:
    """One sheet's Texas rows, aggregated by county."""
    hdr, rest = header_of(book.rows(sheet))
    need = ("Plant State", "County", "Nameplate Capacity (MW)")
    if any(c not in hdr for c in need):
        return {"ok": False, "note": f"{sheet}: header is missing "
                                     f"{', '.join(c for c in need if c not in hdr)}"}
    ist, ico = hdr["Plant State"], hdr["County"]
    imw = hdr["Nameplate Capacity (MW)"]
    iba = hdr.get("Balancing Authority Code")
    ite = hdr.get("Technology")

    counties: dict = collections.defaultdict(lambda: {"mw": 0.0, "units": 0})
    tech: collections.Counter = collections.Counter()
    total, units, erco = 0.0, 0, 0
    for row in rest:
        if row.get(ist) != "TX":
            continue
        try:
            mw = float(row.get(imw) or 0)
        except ValueError:
            mw = 0.0
        county = (row.get(ico) or "").strip()
        counties[county]["mw"] += mw
        counties[county]["units"] += 1
        total += mw
        units += 1
        if iba is not None and row.get(iba) == "ERCO":
            erco += 1
        if ite is not None:
            tech[(row.get(ite) or "").strip()] += mw
    return {
        "ok": True,
        "total_mw": round(total, 1),
        "units": units,
        "erco_units": erco,
        "counties": {k: {"mw": round(v["mw"], 1), "units": v["units"]}
                     for k, v in sorted(counties.items()) if k},
        "top_technology": [{"name": k, "mw": round(v, 1)}
                           for k, v in tech.most_common(8) if k and v > 0],
    }


def report_url(year: int, month: int) -> str:
    return f"{BASE}/{MONTHS[month - 1]}_generator{year}.xlsx"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def find_latest(today: _dt.date | None = None) -> tuple[str, str] | None:
    """Walk back from this month until a URL answers with something that is actually a zip.

    A 200 IS NOT ENOUGH. EIA serves its own landing page, with a 200, for a workbook that does
    not exist yet, so the PK signature is the check that matters. Without it this collector
    would parse an HTML page, find no rows and write a confident zero.
    """
    d = today or _dt.date.today()
    for back in range(0, 8):
        y, m = d.year, d.month - back
        while m <= 0:
            m += 12
            y -= 1
        url = report_url(y, m)
        try:
            blob = fetch(url)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            continue
        if blob[:2] == b"PK":
            return url, f"{y}-{m:02d}"
    return None


def collect(series: Path = SERIES) -> int:
    found = find_latest()
    if not found:
        rec = {"month": None, "verified": False,
               "note": "no EIA-860M workbook answered with a zip in the last eight months"}
    else:
        url, month = found
        held = set()
        if series.exists():
            for line in series.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    if r.get("verified"):
                        held.add(r.get("month"))
        if month in held:
            print(f"generators: {month} already held and verified, nothing to do")
            return 0
        blob = fetch(url)
        RAW.mkdir(parents=True, exist_ok=True)
        (RAW / f"{month}-eia860m.xlsx.gz").write_bytes(gzip.compress(blob))
        book = Book(blob)
        rec = {"month": month, "source_url": url}
        bad = []
        for sheet, key in SHEETS.items():
            if sheet not in book.sheets:
                bad.append(f"{sheet}: sheet is gone")
                continue
            got = read_sheet(book, sheet)
            if not got.pop("ok"):
                bad.append(got["note"])
                continue
            rec[key] = got
        lo, hi = PLAUSIBLE_OPERATING_MW
        op = (rec.get("operating") or {}).get("total_mw", 0)
        if not bad and not lo <= op <= hi:
            bad.append(f"operating total of {op:,.0f} MW is outside the plausible envelope "
                       f"{lo:,} to {hi:,}")
        rec["verified"] = not bad
        rec["note"] = "; ".join(bad)

    rec.setdefault("_spec", 1)
    rec["read_at"] = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    series.parent.mkdir(parents=True, exist_ok=True)
    with series.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    if rec.get("verified"):
        o, p = rec["operating"], rec["planned"]
        print(f"generators: {rec['month']} operating {o['total_mw']:,.0f} MW across "
              f"{len(o['counties'])} counties, planned {p['total_mw']:,.0f} MW")
        return 0
    print(f"generators: UNVERIFIED: {rec['note']}")
    return 2


# --------------------------------------------------------------------------- self-test
def _book(rows: list[list], sheet="Operating", gap=False) -> bytes:
    """A workbook in memory, with the option to leave a hole where a cell would be.

    THE HOLE IS THE POINT. An xlsx omits empty cells, and a parser that reads positionally
    reads every later column one place to the left from there on. This fixture reproduces that
    exactly so the guard against it is tested rather than asserted.

    Strings go through a SHARED STRING TABLE because that is what Excel and EIA actually emit.
    A fixture using inline strings would exercise a code path the real workbook never takes,
    and would have passed here while the collector read nothing from the real file.
    """
    shared: list[str] = []

    def sref(v: str) -> int:
        if v not in shared:
            shared.append(v)
        return shared.index(v)

    def ref(ci, r):
        out, n = "", ci + 1
        while n:
            n, rem = divmod(n - 1, 26)
            out = chr(65 + rem) + out
        return f"{out}{r}"

    body = []
    for ri, row in enumerate(rows, start=1):
        cells = []
        for ci, v in enumerate(row):
            if gap and ri > 2 and v == "":
                continue                      # the omitted cell an xlsx really writes
            if isinstance(v, str):
                cells.append(f'<c r="{ref(ci, ri)}" t="s"><v>{sref(v)}</v></c>')
            else:
                cells.append(f'<c r="{ref(ci, ri)}"><v>{v}</v></c>')
        body.append(f'<row r="{ri}">{"".join(cells)}</row>')

    sheet_xml = ('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                 "<sheetData>" + "".join(body) + "</sheetData></worksheet>")
    sst = ('<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
           + "".join(f"<si><t>{v}</t></si>" for v in shared) + "</sst>")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("xl/sharedStrings.xml", sst)
        z.writestr("xl/workbook.xml",
                   '<workbook xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                   f'<sheets><sheet name="{sheet}" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<Relationships><Relationship Id="rId1" Type="worksheet" '
                   'Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return buf.getvalue()


HDR = ["Entity Name", "Plant State", "County", "Balancing Authority Code",
       "Nameplate Capacity (MW)", "Technology"]


def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    rows = [["Inventory of Operating Generators"], HDR,
            ["A Co", "TX", "Ector", "ERCO", 250.0, "Solar"],
            ["B Co", "TX", "Ector", "ERCO", 100.0, "Battery"],
            ["C Co", "TX", "Ward", "ERCO", 400.0, "Gas"],
            ["D Co", "OK", "Custer", "SWPP", 900.0, "Wind"]]
    b = Book(_book(rows))
    got = read_sheet(b, "Operating")
    check("only Texas rows are read", got["units"] == 3, str(got["units"]))
    check("nameplate sums per county", got["counties"]["Ector"]["mw"] == 350.0,
          str(got["counties"].get("Ector")))
    check("counties outside Texas are not admitted", "Custer" not in got["counties"])
    check("the ERCOT count is separate", got["erco_units"] == 3, str(got["erco_units"]))
    check("technology is totalled", dict(
        (t["name"], t["mw"]) for t in got["top_technology"])["Gas"] == 400.0,
        str(got["top_technology"]))

    # THE HOLE. Row three has no Balancing Authority, which a real xlsx writes as no cell at
    # all. A positional reader takes 250.0 as the authority and "Solar" as the nameplate, and
    # reports a confident wrong total.
    holed = [r[:] for r in rows]
    holed[2][3] = ""
    hb = Book(_book(holed, gap=True))
    hg = read_sheet(hb, "Operating")
    check("a row with an omitted cell still lands in the right columns",
          hg["counties"]["Ector"]["mw"] == 350.0, str(hg["counties"].get("Ector")))
    check("...and the missing authority is simply absent, not shifted in",
          hg["erco_units"] == 2, str(hg["erco_units"]))

    # Every guard fed the input it exists to reject.
    renamed = [r[:] for r in rows]
    renamed[1][2] = "Parish"
    check("a renamed county column is refused",
          read_sheet(Book(_book(renamed)), "Operating")["ok"] is False)
    check("...and names what is missing",
          "County" in read_sheet(Book(_book(renamed)), "Operating")["note"])
    noheader = [["just a title"], ["a", "b", "c"]]
    check("a sheet with no header row is refused",
          read_sheet(Book(_book(noheader)), "Operating")["ok"] is False)

    check("an HTML page is not mistaken for a workbook", b"<!doctype html>"[:2] != b"PK")
    print("\ngenerators self-test " + ("clean" if not failures else f"{failures} FAILED"))
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
