"""Every figure the November 1st deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}


def grab(cid, pattern, group=1):
    m = re.search(pattern, claims[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in its quote")
    return m.group(group)


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

grant = int(grab("c1", r"\$(\d+) million")) * 1_000_000
F("grant_usd", grant, ["c1"], "the WoodNext Foundation grant, dollars, from '$2 million'")
obl = int(grab("c25", r'"fundsObligatedAmt":"(\d+)"'))
tot = int(grab("c26", r'"estimatedTotalAmt":"(\d+)"'))
F("nsf_obligated_usd", obl, ["c25"], "NSF funds obligated to the ARM-MIP award, dollars")
F("nsf_total_usd", tot, ["c26"], "NSF estimated total for the ARM-MIP award, dollars")
m, d, y = (int(x) for x in grab("c27", r'"startDate":"(\d+/\d+/\d+)"').split("/"))
start = date(y, m, d)
m, d, y = (int(x) for x in grab("c28", r'"expDate":"(\d+/\d+/\d+)"').split("/"))
end = date(y, m, d)
F("award_start", start.isoformat(), ["c27"], "the award's start date")
F("award_end", end.isoformat(), ["c28"], "the award's end date")
months = (end.year - start.year) * 12 + (end.month - start.month) + (1 if end.day >= 28 else 0)
F("award_months", months, ["c27", "c28"], "computed: whole calendar months from the start date to the end date, the last month counted when the end date falls at its end")
F("award_years", months // 12, ["c27", "c28"], "computed: award_months divided by 12")
F("max_temp_c", int(grab("c10", r"up to ([\d,]+) degrees").replace(",", "")), ["c10"], "degrees Celsius the university says existing self driving labs can't handle")
F("papers_together", int(grab("c16", r"more than (\d+) papers")), ["c16"], "papers Karaman and Arróyave have published together, a floor")

UNIT = 100_000
F("button_unit_usd", UNIT, [], "a drawing rule: one alloy button stands for this many dollars. Not a claim")
F("grant_buttons", grant // UNIT, ["c1"], "computed: grant_usd divided by the drawing unit")
F("nsf_obligated_buttons", obl // UNIT, ["c25"], "computed: nsf_obligated_usd divided by the drawing unit")
F("nsf_total_buttons", tot // UNIT, ["c26"], "computed: nsf_total_usd divided by the drawing unit")
F("nsf_total_over_grant", round(tot / grant, 1), ["c1", "c26"], "computed: the NSF estimated total divided by the WoodNext grant, to one decimal place")
F("nsf_obligated_share_pct", round(100 * obl / tot), ["c25", "c26"], "computed: obligated over estimated total, as a whole percent")
F("grant_money_m", grant / 1e6, ["c1"], "computed: grant in millions")
F("nsf_total_money_m", tot / 1e6, ["c26"], "computed: NSF estimated total in millions")
F("nsf_obligated_money_m", obl / 1e6, ["c25"], "computed: NSF obligated in millions")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: v["value"] for k, v in figures.items() if k != "_note"}, indent=1))
