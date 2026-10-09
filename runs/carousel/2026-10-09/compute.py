#!/usr/bin/env python3
"""compute.py for the 2026-10-09 deck, UTMB and OpenEvidence (tx-2026-0208).
Every figure is extracted from a claim's own quote in claims.json by a pattern that must match, or the
build stops. A count is a count of things a quote lists or numbers, done here. A span is date
arithmetic on dates the quotes print. Nothing is typed by hand."""
import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "half": 0.5}
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                       "August", "September", "October", "November", "December"], 1)}


def grab(cid, pattern):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    return m


def num(cid, pattern):
    g = grab(cid, pattern).group(1)
    if g.lower() in WORDS:
        return WORDS[g.lower()]
    g = g.replace(",", "").replace("$", "")
    return float(g) if "." in g else int(g)


def date(cid, pattern):
    m = grab(cid, pattern)
    return dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


# UTMB's own account
put("campuses", num("c11", r"on (\w+) campuses"), ["c11"], "campuses UTMB has hospitals on")
put("clinics", num("c12", r"more than (\d+) clinics"), ["c12"], "clinics across Southeast Texas, more than", floor=True)
put("share_using", num("c9", r"more than (\w+) of UTMB clinicians"), ["c9"],
    "share of UTMB clinicians actively using OpenEvidence, more than, with no denominator printed", floor=True)
announced = date("c3", r"(\w+) (\d+), (\d{4})")
put("announced", announced.isoformat(), ["c3"], "date of UTMB's release")
live_month = grab("c4", r"went live at UTMB in (\w+)").group(1)
put("live_month", live_month, ["c4"], "month the integration went live, no year printed")
# months from the go-live month to the release month, counted on the calendar. The release prints no
# day or year for March, so the count is of calendar months, March to September.
put("months_live", announced.month - MONTHS[live_month], ["c4", "c3"],
    "calendar months from the go-live month to the release month, March to September")

# the statute
conds = [cid for cid in ("c20", "c21", "c22") if re.match(r"\((\d)\)", C[cid]["quote"])]
put("conditions", len(conds), conds, "numbered conditions in Sec. 183.005(a)")
effective = date("c25", r"eff\. (\w+) (\d+), (\d{4})")
put("statute_effective", effective.isoformat(), ["c25"], "date Sec. 183.005 took effect")
put("days_effective_to_release", (announced - effective).days, ["c25", "c3"],
    "days from the statute taking effect to UTMB's release")
put("bill", num("c24", r"S\.B\. (\d+)"), ["c24"], "the Senate bill that added the section")

# the Qualified Health contract, tx-2026-0094
initial = num("c29", r"value set at (\$[\d,]+)")
first = num("c30", r"increased the value to (\$[\d,]+)")
added = num("c34", r"additional value is (\$[\d,]+)")
total = num("c35", r"Qualified Health to (\$[\d,]+)")
if first + added != total:
    raise SystemExit(f"contract amounts do not add: {first} + {added} != {total}")
put("contract_initial", initial, ["c29"], "dollars, the December 2024 agreement")
put("contract_first", first, ["c30"], "dollars, after the October 2025 first amendment")
put("contract_added", added, ["c34"], "dollars the third amendment adds")
put("contract_total", total, ["c35"], "dollars, the agreement's total value")
put("contract_multiple", round(total / initial, 1), ["c29", "c35"], "total over initial, rounded to one decimal")
put("institutions", num("c31", r"all (\w+) U\.T\. System"), ["c31"], "UT System health-related institutions the third amendment extends to")

# the Regents' door
meeting = grab("c42", r"(\w+) (\d+)-(\d+), (\d{4})")
m_start = dt.date(int(meeting.group(4)), MONTHS[meeting.group(1)], int(meeting.group(2)))
put("regents_meeting", m_start.isoformat(), ["c42"], "first day of the Regents' next regular meeting")
put("regents_meeting_days", int(meeting.group(3)) - int(meeting.group(2)) + 1, ["c42"], "days the meeting runs")
put("days_to_meeting", (m_start - dt.date(2026, 10, 9)).days, ["c42"], "days from October 9th, 2026, the run date, to the meeting's first day")
put("hours_notice", num("c44", r"at least (\d+) hours"), ["c44"], "hours ahead a person gives a name and topic")

# the vendor's own claim, always attributed
put("vendor_consultations_m", num("c39", r"over (\d+) million"), ["c39"], "millions of consultations OpenEvidence says it has supported, more than", floor=True, attributed="OpenEvidence")

# the measured counter-image, tx-2026-0151
put("cindex_train", num("c40", r"C-index of ([\d.]+) \("), ["c40"], "C-index on the training cohort")
put("cindex_external", num("c40", r"and ([\d.]+) \(95% CI, 0\.491"), ["c40"], "C-index in external validation")

# what UTMB's release prints, scanned rather than asserted
release = (HERE / "sources" / "utmb_openevidence.txt").read_text(encoding="utf-8")
body = release[release.find("UTMB collaborates with OpenEvidence to integrate"):release.find("Close Off-Canvas")]
put("release_percent_figures", len(re.findall(r"\d\s*%|\bpercent\b", body)), ["c1"],
    "percent figures in the body of UTMB's release of September 22nd, scanned from the saved copy")
put("release_accuracy_mentions", len(re.findall(r"accura|error rate|outcome", body, re.I)), ["c1"],
    "mentions of accuracy, an error rate or an outcome in the body of the release")

put("release_diagnostic_mentions", len(re.findall(r"diagnos", body, re.I)), ["c1"],
    "uses of any form of diagnose, diagnosis or diagnostic in the body of the release, the statute's term")
put("release_patient_mentions", len(re.findall(r"patient", body, re.I)), ["c1"],
    "mentions of patients in the body of the release")
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}, indent=1))
