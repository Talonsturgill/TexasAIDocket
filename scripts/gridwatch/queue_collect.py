#!/usr/bin/env python3
"""The Queue Gap collector. How much large load asked ERCOT for power, and how much draws it.

WHY THIS IS A SEPARATE SERIES FROM THE DAILY READING. readings.jsonl is the physical system on
a scale of days, settled overnight from ERCOT's dashboards API. This is the interconnection
queue on a scale of months, published in a board deck. Different cadence, different source,
different failure modes, so a different file and a different workflow. An ERCOT MIS outage on
report day must never cost a demand day.

WHY THE PDF IS PARSED AND NOT READ. ERCOT's Monthly Operational Overview carries a text layer.
The two figures this series exists for are stated in prose on the "Loads Approved to Energize"
slide, not drawn in a chart, so they can be extracted by pattern and checked. That distinction
is the whole reason this collector is allowed to exist under the numeral law: the number is
LIFTED FROM PUBLISHED TEXT, byte for byte, never read off a chart image and never estimated. If
ERCOT ever moves these two figures into the chart, the pattern stops matching and this writes an
unverified record rather than guessing. That is the correct failure.

The stage-by-stage breakdown on the preceding slide IS a chart image and is deliberately not
collected. Three honest stages beat five invented ones.

WHY EXTRACTION IS STDLIB. zlib plus a regex over the text-showing operators gets these figures
exactly, which was measured against pypdf on the same file before this was written. A collector
that runs unattended for years is better off with no dependency to drift than with a nicer API.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as _dt
import gzip
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "queue.jsonl"
RAW = REPO_ROOT / "ledger" / "gridwatch" / "raw"

UA = ("TexasAIDocket/1.0 (+https://texasaidocket.com; "
      "monthly large load queue reading)")

# The report lands in the FOLLOWING month, on a day that moves. June's landed on the 17th of
# July, July's on the 17th of August, March's on the 16th of April. Rather than hard code a day
# that will be wrong, the collector walks the plausible window and takes the first that answers.
# Cheap: at most a couple of dozen HEAD-shaped requests, once a month.
BASE = "https://www.ercot.com/files/docs"
SCAN_DAYS = range(10, 29)

# The one sentence this series is built on, as ERCOT writes it:
#   "Of the 9,456 MW that have received Approval to Energize, ERCOT has observed a
#    non-simultaneous monthly peak consumption of 4,370 MW in July 2026"
FUNNEL_RE = re.compile(
    r"Of the ([\d,]+)\s*MW that have received Approval to Energize"
    r".*?peak consumption of ([\d,]+)\s*MW in (\w+ \d{4})",
    re.S)

# The all-time-peak anchor, which is what makes a gigawatt figure mean anything to a reader.
PEAK_RE = re.compile(r"new record of ([\d,]+)\s*MW\*? for the month of (\w+)")

# A reading outside these bounds is a parse that went wrong, not a grid that changed. Approval
# to Energize has run single-digit GW all year and observed operational load is a fraction of
# it; either figure leaving this envelope means the sentence moved or the units did, and the
# collector must fail loudly rather than append a number nobody can rebuild.
PLAUSIBLE_MW = (100, 200_000)


def _text(pdf: bytes) -> str:
    """Every literal string in the PDF's content streams, concatenated.

    Not a layout-preserving extraction and does not need to be. The patterns above match across
    a single slide's prose, and the slide's words arrive in reading order.
    """
    out: list[str] = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", pdf, re.S):
        try:
            data = zlib.decompress(m.group(1))
        except zlib.error:
            continue                      # uncompressed or an image stream; neither carries prose
        for tok in re.findall(rb"\((?:\\.|[^\\()])*\)", data):
            body = re.sub(rb"\\([()\\])", rb"\1", tok[1:-1])
            out.append(body.decode("latin-1"))
    return "".join(out)


def parse(pdf: bytes) -> dict:
    """The two funnel figures and the peak anchor, or an explanation of what did not match."""
    txt = _text(pdf)
    m = FUNNEL_RE.search(txt)
    if not m:
        return {"verified": False,
                "note": "the Approval to Energize sentence did not match; ERCOT may have moved "
                        "these figures into the chart"}
    approved = int(m.group(1).replace(",", ""))
    observed = int(m.group(2).replace(",", ""))
    lo, hi = PLAUSIBLE_MW
    for name, v in (("approved_to_energize_mw", approved), ("observed_operational_mw", observed)):
        if not lo <= v <= hi:
            return {"verified": False,
                    "note": f"{name} of {v} MW is outside the plausible envelope {lo} to {hi}"}
    if observed > approved:
        return {"verified": False,
                "note": f"observed {observed} MW exceeds approved {approved} MW, which inverts "
                        "the funnel and means the sentence was misread"}
    rec = {
        "approved_to_energize_mw": approved,
        "observed_operational_mw": observed,
        "reported_for": m.group(3),
        "verified": True,
        "note": "",
    }
    p = PEAK_RE.search(txt)
    if p:
        rec["month_peak_record_mw"] = int(p.group(1).replace(",", ""))
    return rec


def report_url(year: int, month: int) -> tuple[str, str] | None:
    """Find the Monthly Operational Overview for a given report month.

    Returns (url, published_date) or None. The publication day moves, so the window is walked.
    """
    pub_y, pub_m = (year + 1, 1) if month == 12 else (year, month + 1)
    for day in SCAN_DAYS:
        for name in report_names(year, month):
            url = f"{BASE}/{pub_y}/{pub_m:02d}/{day:02d}/{name}"
            req = urllib.request.Request(url, headers={"User-Agent": UA}, method="HEAD")
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    if r.status == 200:
                        return url, f"{pub_y}-{pub_m:02d}-{day:02d}"
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
                continue
    return None


def report_names(year: int, month: int) -> list[str]:
    """Every filename ERCOT has used for one month's report, the usual one first.

    THE NAME IS NOT STABLE. Every report through August carried its year. September's landed on
    October 16th as `ERCOT-Monthly-Operational-Overview-September.pdf`, with no year, and the
    collector asked only for the dated name, so it wrote "not published yet" every day for three
    weeks while the report sat on ERCOT's server. The grid watch page check went to STOPPED on
    November 1st. The yearless name is safe to ask for because the dated directory it sits in
    already pins the year, and `collect` refuses a report whose own month does not match.
    """
    mon = calendar.month_name[month]
    return [f"ERCOT-Monthly-Operational-Overview-{mon}-{year}.pdf",
            f"ERCOT-Monthly-Operational-Overview-{mon}.pdf"]


def months_owed(rows: list[dict], year: int, month: int, depth: int = 3) -> list[tuple[int, int]]:
    """The report months to read, oldest first: last month, and any month before it missed.

    The collector used to read last month only. A report it missed for any reason, a renamed
    file or a day ERCOT published late, was skipped for good the moment the calendar turned,
    because nothing ever asked for that month again. This walks back from last month to the
    newest verified reading, at most `depth` months, so one missed month is caught up the next
    day rather than never.
    """
    verified = {r.get("month") for r in rows if r.get("verified")}
    out = []
    y, m = year, month
    for _ in range(depth):
        key = f"{y}-{m:02d}"
        if key in verified:
            break
        out.append((y, m))
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return list(reversed(out))


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def held(path: Path = LEDGER) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def archive_pdf(key: str, pdf: bytes) -> Path:
    """Keep the first snapshot and store changed responses under their content digest."""
    RAW.mkdir(parents=True, exist_ok=True)
    original = RAW / f"{key}-moo.pdf.gz"

    def same(path: Path) -> bool:
        try:
            return gzip.decompress(path.read_bytes()) == pdf
        except (OSError, EOFError, zlib.error):
            return False

    target = original
    if original.exists():
        if same(original):
            return original
        target = RAW / f"{key}-moo-{hashlib.sha256(pdf).hexdigest()}.pdf.gz"
    try:
        # Exclusive creation preserves archives even if two collectors race.
        with target.open("xb") as fh:
            fh.write(gzip.compress(pdf, mtime=0))
    except FileExistsError:
        if not same(target):
            if target == original:
                return archive_pdf(key, pdf)
            raise ValueError(f"archive digest collision or corrupt snapshot: {target}")
    return target


def collect(year: int, month: int, path: Path = LEDGER) -> int:
    key = f"{year}-{month:02d}"
    if any(r.get("month") == key and r.get("verified") for r in held(path)):
        print(f"queue: {key} already held and verified, nothing to do")
        return 0

    found = report_url(year, month)
    if not found:
        rec = {"month": key, "verified": False,
               "note": "no Monthly Operational Overview published for this month yet",
               "source_url": None, "published": None}
    else:
        url, published = found
        try:
            pdf = fetch(url)
        except Exception as exc:                                   # noqa: BLE001
            rec = {"month": key, "verified": False, "source_url": url, "published": published,
                   "note": f"fetch failed: {exc}"}
        else:
            # Preserve the fetched evidence before parsing, including rejected responses.
            archived = archive_pdf(key, pdf)
            rec = {"month": key, "source_url": url, "published": published, **parse(pdf)}
            want = f"{calendar.month_name[month]} {year}"
            if rec.get("verified") and rec.get("reported_for") != want:
                # A yearless filename could in principle answer for the wrong year. The report's
                # own sentence names its month, so a mismatch is refused, never appended.
                rec = {"month": key, "verified": False, "source_url": url,
                       "published": published,
                       "note": f"report reads for {rec.get('reported_for')}, not {want}"}
            rec["raw_file"] = archived.name

    # A FAILED READ CARRIES NO NUMBER FORWARD. Same law as the daily series: the record says
    # plainly that this month is unverified rather than repeating last month's figure, because
    # a repeated figure is indistinguishable from a flat one.
    rec.setdefault("_spec", 1)
    rec["read_at"] = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    print(f"queue: {key} {'verified' if rec.get('verified') else 'UNVERIFIED: ' + rec['note']}")
    return 0 if rec.get("verified") else 2


# --------------------------------------------------------------------------- self-test
FIXTURE = (
    "PUBLIC 10 Loads Approved to Energize - Observations "
    "Of the 9,456 MW that have received Approval to Energize, ERCOT has observed a "
    "non-simultaneous monthly peak consumption of 4,370 MW in July 2026, which is a slight "
    "increase since June 2026. ERCOT set a new record of 91,134 MW* for the month of July"
)


def self_test() -> int:
    """Replay known-good and known-bad text and require the parser to sort them.

    A checker that cannot go red proves nothing, so every guard below is fed the input it
    exists to reject.
    """
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    class Fake:
        """The fixture, wrapped so parse() sees it the way it sees a real content stream."""
        @staticmethod
        def build(text: str) -> bytes:
            # Chunked mid-word the way a real content stream breaks a line, with the spaces
            # kept INSIDE the literals. A fixture that split on spaces would drop them and
            # test a string no PDF ever produces.
            chunks = [text[i:i + 40] for i in range(0, len(text), 40)]
            body = "".join(f"({c}) Tj\n" for c in chunks)
            return b"stream\n" + zlib.compress(body.encode("latin-1")) + b"\nendstream"

    good = parse(Fake.build(FIXTURE))
    check("the funnel sentence parses", good.get("verified") is True, str(good))
    check("approved figure is exact", good.get("approved_to_energize_mw") == 9456,
          str(good.get("approved_to_energize_mw")))
    check("observed figure is exact", good.get("observed_operational_mw") == 4370,
          str(good.get("observed_operational_mw")))
    check("the report month is carried", good.get("reported_for") == "July 2026",
          str(good.get("reported_for")))
    check("the peak anchor is carried", good.get("month_peak_record_mw") == 91134,
          str(good.get("month_peak_record_mw")))

    missing = parse(Fake.build("PUBLIC 10 A slide with no funnel sentence on it at all"))
    check("a missing sentence is unverified", missing.get("verified") is False)
    check("and says why", "did not match" in missing.get("note", ""), missing.get("note", ""))

    inverted = parse(Fake.build(FIXTURE.replace("4,370 MW in July", "94,370 MW in July")))
    check("an inverted funnel is refused", inverted.get("verified") is False, str(inverted))

    absurd = parse(Fake.build(FIXTURE.replace("9,456 MW that", "999,456 MW that")))
    check("an out-of-envelope figure is refused", absurd.get("verified") is False, str(absurd))

    names = report_names(2026, 9)
    check("the dated name is asked for first",
          names[0] == "ERCOT-Monthly-Operational-Overview-September-2026.pdf", str(names))
    check("the yearless name September shipped under is asked for too",
          "ERCOT-Monthly-Operational-Overview-September.pdf" in names, str(names))

    rows = [{"month": "2026-08", "verified": True}, {"month": "2026-09", "verified": False}]
    check("a missed month is owed beside last month",
          months_owed(rows, 2026, 10) == [(2026, 9), (2026, 10)], str(months_owed(rows, 2026, 10)))
    check("nothing is owed once last month verified",
          months_owed(rows + [{"month": "2026-10", "verified": True}], 2026, 10) == [])
    check("the walk crosses a year boundary",
          months_owed([{"month": "2025-11", "verified": True}], 2026, 1) == [(2025, 12), (2026, 1)])
    check("the walk is bounded", len(months_owed([], 2026, 10)) == 3)

    # Exercise the collector, not only its parser, without a network request or ledger write.
    import tempfile
    from unittest.mock import patch

    scratch = REPO_ROOT / "out" / "queue-self-test" / "tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        root = Path(tmp)
        raw = root / "raw"
        path = root / "queue.jsonl"
        bad_pdf = Fake.build("No matching sentence")
        good_pdf = Fake.build(FIXTURE)
        with patch(__name__ + ".RAW", raw), \
             patch(__name__ + ".report_url", return_value=("https://example.test/report.pdf", "2026-08-16")), \
             patch(__name__ + ".fetch", return_value=bad_pdf) as mocked_fetch:
            check("a failed parse appends an unverified reading", collect(2026, 7, path) == 2)
            original = raw / "2026-07-moo.pdf.gz"
            # Model a historical archive written with the old timestamped gzip encoding.
            original.write_bytes(gzip.compress(bad_pdf, mtime=123456789))
            prior = original.read_bytes()
            check("the rejected response is archived", gzip.decompress(prior) == bad_pdf)
            check("same bytes reuse the original archive", archive_pdf("2026-07", bad_pdf) == original
                  and original.read_bytes() == prior)
            mocked_fetch.return_value = good_pdf
            check("a corrected report verifies", collect(2026, 7, path) == 0)
            current = held(path)[-1]
            snapshot = raw / current["raw_file"]
            check("corrected bytes leave the first archive untouched", original.read_bytes() == prior)
            check("the verified reading identifies its corrected snapshot", snapshot != original
                  and gzip.decompress(snapshot.read_bytes()) == good_pdf)
            stable = snapshot.read_bytes()
            check("corrected snapshot is idempotent", archive_pdf("2026-07", good_pdf) == snapshot
                  and snapshot.read_bytes() == stable)
            count = len(held(path))
            mocked_fetch.reset_mock()
            check("an already verified month does not fetch or append", collect(2026, 7, path) == 0
                  and len(held(path)) == count and not mocked_fetch.called)
            check("a report for the wrong month is refused", collect(2026, 9, path) == 2)
            wrong = held(path)[-1]
            check("wrong month carries no figures", wrong["verified"] is False
                  and "observed_operational_mw" not in wrong and "not September 2026" in wrong["note"])
            check("wrong month evidence remains available", gzip.decompress((raw / wrong["raw_file"]).read_bytes()) == good_pdf)

    print("\nqueue_collect self-test " + ("clean" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--collect", action="store_true", help="read the latest published report")
    ap.add_argument("--month", help="report month as YYYY-MM; defaults to last month")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.collect:
        ap.print_help()
        return 1
    if a.month:
        y, m = (int(x) for x in a.month.split("-"))
        return collect(y, m)
    first = _dt.date.today().replace(day=1)
    prev = first - _dt.timedelta(days=1)
    codes = [collect(y, m) for y, m in months_owed(held(), prev.year, prev.month)]
    return max(codes, default=0)


if __name__ == "__main__":
    sys.exit(main())
