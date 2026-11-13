#!/usr/bin/env python3
"""Figures for carousel no. 76, ERCOT's preliminary summary of the data center community impact RFI (tx-2026-0072).

Every value is read out of a claim quote by a pattern, or computed here from values that were.

RULES, stated so they are choices rather than accidents:
- zone counts and GW are read from c11 to c14, each from its own quote; zone_loads is Large plus Medium for that zone
- zones_gw_sum is the sum of the four zones' GW, kept as a computed value and never printed as a statewide total,
  because the zone page counts 429 reviewed loads and leaves out NOIE zones (c15, c16)
- not_submitted is issued (c3) minus submitted (c4), ASSERTED equal to the 32 of c6
- on_time plus late (c5) is ASSERTED equal to submitted (c4)
- medium_issued is issued minus the 245 Large Loads (c7)
- unanswered_pct is 100 minus the 83 percent answered (c17)
- days_to_report counts from the November 5th meeting (c1) to the December 10th report (c23)
- days_report_to_meeting counts from December 10th (c23) to the December 17th open meeting (c38)
- any drawing unit is a drawing scale and never a fleet: it is declared here with the rule that rounds it
"""
import json, re, datetime as dt
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def num(cid, pat, cast=int):
    m = re.search(pat, q(cid)); assert m, (cid, pat)
    return cast(m.group(1).replace(",", ""))
def half_up(x, places=0):
    e = Decimal("1") if places == 0 else Decimal("1." + "0" * places)
    v = Decimal(str(x)).quantize(e, rounding=ROUND_HALF_UP); return int(v) if places == 0 else float(v)

issued = num("c3", r"to (\d+) loads")
submitted = num("c4", r"^(\d+) of")
submitted_pct = num("c4", r"\((\d+)%\)")
gw_requested = num("c4", r"~(\d+) GW")
cap_pct = num("c4", r"\(~(\d+)%\)")
on_time = num("c5", r"^(\d+) RFIs")
late = num("c5", r"and (\d+) were")
medium_missing = num("c6", r"^(\d+) Medium")
large_all = num("c7", r"All (\d+) Large")
large_mw = num("c7", r"\((\d+) MW")
large_pct = num("c8", r"~(\d+)%")
large_gw = num("c8", r"~(\d+) GW")
gw_projects = num("c9", r"Among Large Loads, (\d+) projects")
gw_projects_pct = num("c9", r"representing (\d+)%")
west_pct = num("c10", r"with (\d+)% of capacity")
Z = {}
for cid, zone in (("c11", "West"), ("c12", "North"), ("c13", "South"), ("c14", "Houston")):
    m = re.match(r"(\d+) LL \S (\d+) ML \S (\d+) GW", q(cid)); assert m, cid
    Z[zone] = {"ll": int(m.group(1)), "ml": int(m.group(2)), "gw": int(m.group(3))}
reviewed = num("c15", r"N = (\d+) included")
answered_pct = num("c17", r"answered (\d+)%")
questions = num("c17", r"nearly ([\d,]+) RFI")
na_large = num("c19", r"Large Loads \(~(\d+)%\)")
na_medium = num("c19", r"Medium Loads \(~(\d+)%\)")
na_later_pct = num("c20", r"(\d+)% more")
dev_reviewed = num("c24", r"from (\d+) developers")
dev_questions = num("c24", r"approximately ([\d,]+) questions")
second_round_pct = num("c25", r"to (\d+)% of")
meeting = dt.date(2026, 11, 5); assert "November 5, 2026" in q("c1")
report = dt.date(2026, 12, 10); assert "December 10, 2026" in q("c23")
open_meeting = dt.date(2026, 12, 17); assert "December 17, 2026" in q("c38")
deadline = dt.date(2026, 10, 12); assert "October 12, 2026" in q("c34")

not_submitted = issued - submitted; assert not_submitted == medium_missing, (not_submitted, medium_missing)
assert on_time + late == submitted
medium_issued = issued - large_all
medium_submitted = submitted - large_all
unanswered_pct = 100 - answered_pct
zones_gw_sum = sum(z["gw"] for z in Z.values())
zones_loads_sum = sum(z["ll"] + z["ml"] for z in Z.values())

F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
def put(k, v, frm, basis): F[k] = {"value": v, "from": frm, "basis": basis}
put("issued", issued, ["c3"], "loads the RFI was issued to")
put("submitted", submitted, ["c4"], "loads that submitted")
put("submitted_pct", submitted_pct, ["c4"], "percent of issued loads that submitted, as ERCOT states it")
put("gw_requested", gw_requested, ["c4"], "approximate GW of requested interconnection capacity the submissions cover")
put("cap_pct", cap_pct, ["c4"], "approximate percent of requested capacity the submissions cover")
put("on_time", on_time, ["c5"], "RFIs submitted on time")
put("late", late, ["c5"], "RFIs submitted late")
put("not_submitted", not_submitted, ["c3", "c4", "c6"], "issued minus submitted, asserted equal to the Medium Load responses not submitted")
put("large_all", large_all, ["c7"], "Large Loads, all of which responded")
put("large_mw", large_mw, ["c7"], "the Large Load threshold in MW")
put("medium_issued", medium_issued, ["c3", "c7"], "loads issued the RFI that are not Large Loads")
put("medium_submitted", medium_submitted, ["c4", "c7"], "submitted loads that are not Large Loads")
put("large_pct", large_pct, ["c8"], "approximate percent of requested capacity in Large Loads")
put("large_gw", large_gw, ["c8"], "approximate GW in Large Loads")
put("gw_projects", gw_projects, ["c9"], "Large Load projects requesting more than 1 GW")
put("gw_projects_pct", gw_projects_pct, ["c9"], "percent of capacity those projects represent")
put("west_pct", west_pct, ["c10"], "West Texas share of capacity")
for zone, cid in (("West", "c11"), ("North", "c12"), ("South", "c13"), ("Houston", "c14")):
    k = zone.lower(); z = Z[zone]
    put(k + "_ll", z["ll"], [cid], f"{zone} load zone Large Loads in the reviewed dataset")
    put(k + "_ml", z["ml"], [cid], f"{zone} load zone Medium Loads in the reviewed dataset")
    put(k + "_gw", z["gw"], [cid], f"{zone} load zone peak requested capacity, GW")
    put(k + "_loads", z["ll"] + z["ml"], [cid], f"{zone} load zone loads, Large plus Medium")
put("zones_gw_sum", zones_gw_sum, ["c11", "c12", "c13", "c14"], "sum of the four zones' GW, a drawing check, never printed as a statewide total")
put("zones_loads_sum", zones_loads_sum, ["c11", "c12", "c13", "c14"], "sum of the four zones' loads, a drawing check")
put("reviewed", reviewed, ["c15"], "loads in the reviewed dataset behind the zone page")
put("answered_pct", answered_pct, ["c17"], "percent of questions answered")
put("unanswered_pct", unanswered_pct, ["c17"], "100 minus the percent answered")
put("questions", questions, ["c17"], "nearly this many RFI questions")
put("na_large", na_large, ["c19"], "approximate N/A rate among Large Loads, percent")
put("na_medium", na_medium, ["c19"], "approximate N/A rate among Medium Loads, percent")
put("na_later_pct", na_later_pct, ["c20"], "how much more often 2028 and later projects answered N/A, percent")
put("dev_reviewed", dev_reviewed, ["c24"], "developers whose verification responses were reviewed")
put("dev_questions", dev_questions, ["c24"], "approximate verification questions reviewed")
put("second_round_pct", second_round_pct, ["c25"], "percent of developers expected to get a second round RFI")
put("days_to_report", (report - meeting).days, ["c1", "c23"], "days from the November 5th meeting to the December 10th report")
put("days_report_to_meeting", (open_meeting - report).days, ["c23", "c38"], "days from the December 10th report to the December 17th open meeting")
put("days_deadline_to_meeting", (meeting - deadline).days, ["c34", "c1"], "days from the October 12th deadline to the November 5th meeting")

# DRAWING SCALES, declared here so no frame types a size. One copper lamination stands for one GW: 12.7 mm thick with a
# 1 mm separator, so a pack of n bars is n * 0.0137 - 0.001 m wide, rounded half up to the millimetre. One cable reel
# stands for one load. The trench is drawn 24 m long and covered for the answered share of its length.
BAR_M, SEP_M, TRENCH_M = 0.0127, 0.001, 24.0
def pack_w(n): return half_up(n * (BAR_M + SEP_M) - SEP_M, 3)
put("bar_m", BAR_M, [], "thickness of one copper lamination, metres, a drawing scale for one GW")
put("sep_m", SEP_M, [], "separator between laminations, metres, a drawing scale")
put("pack_w_total", pack_w(gw_requested), ["c4"], "face width of the gw_requested pack, metres, drawn and never printed")
for zone in ("West", "North", "South", "Houston"):
    put("pack_w_" + zone.lower(), pack_w(Z[zone]["gw"]), [{"West":"c11","North":"c12","South":"c13","Houston":"c14"}[zone]], f"face width of the {zone} pack, metres, drawn and never printed")
put("trench_m", TRENCH_M, [], "drawn trench length, metres, a drawing scale")
put("trench_covered_m", half_up(TRENCH_M * answered_pct / 100, 2), ["c17"], "grated length of the trench, the answered share of its drawn length")
put("trench_open_m", half_up(TRENCH_M * unanswered_pct / 100, 2), ["c17"], "open length of the trench, the unanswered share of its drawn length")
put("reels_large", large_all, ["c7"], "cable reels drawn on frame 2, one per Large Load")
put("reels_lit", gw_projects, ["c9"], "reels in the lit front block on frame 2, one per project over 1 GW")
# COOLING BY RATE AND BY COUNT, from the summary's own tables (ercot_ci_rfi.txt pages 4 and 5), read from the fetched
# text rather than typed. Page 4 prints questions per category for Large and Medium Loads, A to E between the RD and F
# rows; page 5 prints N/A answers per category, A to E, for pre-2028 and 2028+ facilities. ERCOT's sentence that the
# largest fraction of unanswered questions related to cooling (c18) reads, against these tables, as the highest RATE:
# cooling ranks first by N/A rate and not first by N/A count, so no surface may say cooling was the largest share.
SRC = (HERE / "tmp" / "src" / "ercot_ci_rfi.txt").read_text().splitlines()
num = lambda t: int(t.replace(",", ""))
def block_before(total):
    i = SRC.index(total); return [num(x) for x in SRC[i - 9:i]]   # FI, RD, A, B, C, D, E, F, G
def five_before(total):
    i = SRC.index(total); return [num(x) for x in SRC[i - 5:i]]   # A, B, C, D, E
qL, qM = block_before("38,883")[2:7], block_before("28,029")[2:7]
assert sum(block_before("38,883")) == num("38,883") and sum(block_before("28,029")) == num("28,029")
naP, naL = five_before("3,849"), five_before("7,705")
assert sum(naP) == num("3,849") and sum(naL) == num("7,705")
cats = ["financial assistance", "power self-sufficiency", "water", "cooling", "community impact"]
na = [p_ + l_ for p_, l_ in zip(naP, naL)]; q = [a_ + b_ for a_, b_ in zip(qL, qM)]
rate = [n_ / q_ for n_, q_ in zip(na, q)]
rank_rate = sorted(range(5), key=lambda k: -rate[k]).index(3) + 1
rank_count = sorted(range(5), key=lambda k: -na[k]).index(3) + 1
assert rank_rate == 1, "cooling is not first by N/A rate"
put("cooling_rate_rank", rank_rate, ["c18"], "cooling's rank among the five N/A categories by N/A answers per question asked, from the page 4 and 5 tables; never printed")
put("cooling_count_rank", rank_count, ["c18"], "cooling's rank among the five N/A categories by count of N/A answers, from the page 5 table; never printed, and the reason no surface says largest share")
STUB_ROW = 10
put("stubs_early", STUB_ROW, [], "capped conduit stubs in frame 7's row for projects due before 2028, a drawing scale")
put("stubs_later", half_up(STUB_ROW * (1 + na_later_pct / 100)), ["c20"], "capped conduit stubs in frame 7's row for projects due in 2028 or later, the early row grown by na_later_pct, rounded half up")
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print({k: v["value"] for k, v in F.items() if k != "_note"})
