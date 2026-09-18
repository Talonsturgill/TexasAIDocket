#!/usr/bin/env python3
"""Every number this deck states by counting or by date arithmetic, computed from the claims.

NOT ONE OF THESE IS TYPED. The three agenda dates come out of claims.json, the count is the
length of that set and the two spans are datetime subtraction. That is the whole point of the
file: a run that types "two weeks later" onto a frame has made a factual assertion in the
largest type on the page with nothing behind it.
"""
import datetime as dt, json, pathlib, re

# THE CLAIMS FILE BESIDE THIS ONE FIRST, and the scratch copy only as a fallback.
# The first cut read ROOT/"out/2026-09-18/claims.json" with ROOT as parents[2], which is two
# faults in one line. parents[2] of runs/carousel/<date>/compute.py is `runs/`, not the repo
# root, so the path was wrong wherever it ran from. And `out/` is gitignored and dies with the
# container, so a script CERTIFYING A PUBLISHED FIGURE could not be re-run from a fresh
# checkout, which is the one thing it exists to allow. The shipped claims.json sits beside this
# file and is the copy a reader can actually get.
HERE = pathlib.Path(__file__).resolve().parent
for _cand in (HERE / "claims.json",
              HERE.parents[2] / "out" / HERE.name / "claims.json",
              HERE.parent / "claims.json"):
    if _cand.exists():
        CLAIMS_PATH = _cand
        break
else:
    raise FileNotFoundError("no claims.json beside %s or in this run's scratch" % HERE)
claims = {c["id"]: c for c in json.loads(CLAIMS_PATH.read_text())["claims"]}

# The meeting date each agenda header states, parsed out of the quote rather than retyped.
HEADERS = {"c1": claims["c1"]["quote"], "c11": claims["c11"]["quote"], "c6": claims["c6"]["quote"]}
MONTHS = {"SEPTEMBER": 9, "September": 9}

def meeting_date(quote: str) -> dt.date:
    m = re.search(r"(SEPTEMBER|September)\s+(\d{1,2}),\s*(\d{4})", quote)
    if not m:
        raise ValueError(f"no meeting date in {quote!r}")
    return dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))

dates = {cid: meeting_date(q) for cid, q in HEADERS.items()}
distinct = sorted(set(dates.values()))

first, mid, last = distinct[0], distinct[1], distinct[2]
span_first_to_last = (last - first).days
span_first_to_mid = (mid - first).days

out = {
    "agenda_dates": [d.isoformat() for d in distinct],
    "agenda_count": len(distinct),
    "days_first_to_last": span_first_to_last,
    "weeks_first_to_last": span_first_to_last // 7,
    "days_first_to_mid": span_first_to_mid,
    "weeks_first_to_mid": span_first_to_mid // 7,
}
if __name__ == "__main__":
    print(json.dumps(out, indent=2))
