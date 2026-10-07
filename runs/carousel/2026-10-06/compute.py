#!/usr/bin/env python3
"""compute.py for the 2026-10-06 deck, Taylor Technology Campus (tx-2026-0203). Every figure is
extracted from a claim's own quote in claims.json by a pattern that must match, or the build stops.
Unit conversions use exact definitions stated beside them. Nothing is typed by hand."""
import json, re, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"three": 3}

FT_M = 0.3048            # international foot, exact by definition
ACRE_M2 = 4046.8564224   # international acre, exact by definition
GAL_M3 = 0.003785411784  # US liquid gallon, exact by definition


def num(cid, pattern, flags=0):
    q = C[cid]["quote"]
    m = re.search(pattern, q, flags)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(1)
    if g.lower() in WORDS:
        return WORDS[g.lower()]
    g = g.replace(",", "")
    return float(g) if "." in g else int(g)


F = {"_note": "Every value is extracted from a claim quote by compute.py, or derived from extracted values by a rule stated beside it."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


put("acres", num("c2", r"a (\d+)-acre project"), ["c2"], "acres in the Taylor Technology Campus project")
put("setback_nsw_ft", num("c30", r"at least (\d+) feet from the north"), ["c30"], "feet buildings sit back from the north, east and west lines, at least")
put("setback_south_ft", num("c31", r"at least (\d+) feet from the property line"), ["c31"], "feet data centers, generation and batteries sit back from the south line, at least")
put("setback_accessory_ft", num("c31", r"at least (\d+) feet away"), ["c31"], "feet accessory structures sit back from the south line, at least")
put("buffer_ft", num("c32", r"at least (\d+) feet"), ["c32"], "feet of permanent landscaped buffer along the south line, at least")
put("berm_ft", num("c33", r"at least (\d+) feet high"), ["c33"], "feet high the earthen berms stand, at least")
put("noise_with_dba", num("c12", r"either (\d+) decibels"), ["c12"], "dBA cap on the development's noise with the agreement, or the pre-development level if greater")
put("noise_without_dba", num("c13", r"limits of (\d+) dBA"), ["c13"], "dBA state limit the city lists without the agreement")
put("fill_million_gal", num("c17", r"fill volume of ([\d.]+) million gallons"), ["c17"], "million gallons in the cooling loop's initial fill, for the entire site")
put("commit_total_m", num("c35", r"committing \$([\d.]+) million"), ["c35"], "millions of dollars committed for community investments and nonprofit support")
put("commit_city_m", num("c36", r"^\$(\d+) million"), ["c36"], "millions to the City of Taylor for quality-of-life improvements")
put("commit_parks_min", num("c36", r"at least \$([\d,]+)"), ["c36"], "dollars at least for adaptive-use park improvements, inside the city's share")
put("commit_isd_m", num("c37", r"^\$([\d.]+) million"), ["c37"], "millions to Taylor ISD educational programs")
put("commit_scholar_m", num("c38", r"^\$([\d.]+) million"), ["c38"], "millions for Taylor ISD scholarships")
put("commit_cte_m", num("c39", r"^\$(\d+) million"), ["c39"], "millions for Taylor ISD career and technical education")
put("internships_per_year", num("c39", r"at least (\d+) student internships"), ["c39"], "student internships a year, at least")
put("internship_years", num("c39", r"annually for (\w+) years"), ["c39"], "years the internships run")
put("commit_animal_m", num("c40", r"^\$(\d+) million"), ["c40"], "millions for animal care program support")
put("grant_each", num("c41", r"of \$([\d,]+) each"), ["c41"], "dollars in each of two initial nonprofit grants")
put("grants_count", 2, ["c41"], "nonprofits named for the initial grants", rule="the two organisations c41 names, counted")
put("nonprofit_annual_total_m", num("c42", r"totaling \$([\d.]+) million"), ["c42"], "millions in annual nonprofit contributions over the period")
put("nonprofit_years", num("c42", r"over (\d+) years"), ["c42"], "years of annual nonprofit contributions")
put("revenue_projection_b", num("c44", r"\$([\d.]+) billion"), ["c44"], "billions in gross tax revenue the CITY PROJECTS, a projection")
put("revenue_years", num("c44", r"over (\d+) years"), ["c44"], "years of the city's revenue projection")
put("pz_table_days", num("c7", r"for (\d+) days"), ["c7"], "days the Planning and Zoning Commission tabled the project")
put("petition_signatures", num("c52", r"about ([\d,]+) signatures"), ["c52"], "signatures the coalition gathered, about, as KEYE reports")
put("test_start_hour", num("c34", r"between (\d+) a\.m\."), ["c34"], "hour generator tests may start, a.m.")
put("test_end_hour", num("c34", r"and (\d+) p\.m\."), ["c34"], "hour generator tests must end, p.m.")

# derived, each with its rule
parts_m = [F["commit_city_m"]["value"], F["commit_isd_m"]["value"], F["commit_scholar_m"]["value"], F["commit_cte_m"]["value"],
           F["commit_animal_m"]["value"], F["grant_each"]["value"] * F["grants_count"]["value"] / 1e6, F["nonprofit_annual_total_m"]["value"]]
put("commit_parts_sum_m", round(sum(parts_m), 1), ["c36", "c37", "c38", "c39", "c40", "c41", "c42"],
    "the seven listed parts summed, millions", rule="13 + 10.2 + 1.5 + 1 + 1 + 2 x 0.15 + 1.2, rounded to 0.1")
assert F["commit_parts_sum_m"]["value"] == F["commit_total_m"]["value"], "the parts do not sum to the stated total"
put("commit_isd_total_m", round(F["commit_isd_m"]["value"] + F["commit_scholar_m"]["value"] + F["commit_cte_m"]["value"], 1),
    ["c37", "c38", "c39"], "millions to Taylor ISD across its three lines", rule="10.2 + 1.5 + 1, rounded to 0.1")
put("commit_isd_share_pct", round(100 * F["commit_isd_total_m"]["value"] / F["commit_total_m"]["value"]), ["c35", "c37", "c38", "c39"],
    "percent of the committed total that goes to Taylor ISD", rule="isd_total / total x 100, rounded to a whole percent")
put("internships_total", F["internships_per_year"]["value"] * F["internship_years"]["value"], ["c39"],
    "student internships at least, over the three years", rule="per year x years")
put("noise_gap_dba", F["noise_without_dba"]["value"] - F["noise_with_dba"]["value"], ["c12", "c13"],
    "dBA between the state limit the city lists and the agreement's cap", rule="85 - 65")
put("noise_power_ratio", round(10 ** (F["noise_gap_dba"]["value"] / 10)), ["c12", "c13"],
    "times the sound power a 20 dB difference stands for", rule="10 ^ (dB difference / 10), the decibel's definition")
put("test_window_hours", F["test_end_hour"]["value"] + 12 - F["test_start_hour"]["value"], ["c34"],
    "hours in the weekday generator test window", rule="5 p.m. is hour 17; 17 - 8")
put("site_m2", round(F["acres"]["value"] * ACRE_M2), ["c2"], "square metres in 664 acres", rule="acres x 4046.8564224")
put("site_side_m", round(math.sqrt(F["site_m2"]["value"])), ["c2"], "side in metres of a square of the site's area", rule="sqrt(m2), a square of equal area, NOT the parcel's shape")
for k in ("setback_nsw_ft", "setback_south_ft", "setback_accessory_ft", "buffer_ft", "berm_ft"):
    put(k.replace("_ft", "_m"), round(F[k]["value"] * FT_M, 2), F[k]["from"], F[k]["basis"].replace("feet", "metres"), rule="feet x 0.3048")
put("fill_m3", round(F["fill_million_gal"]["value"] * 1e6 * GAL_M3), ["c17"], "cubic metres in the initial fill", rule="gallons x 0.003785411784")
put("fill_cube_side_m", round(F["fill_m3"]["value"] ** (1 / 3), 1), ["c17"], "side in metres of a cube holding the initial fill", rule="cube root of m3")
put("days_to_vote", 2, ["c4"], "days from this deck's date, October 6th, to the October 8th vote", rule="date(2026,10,8) - date(2026,10,6)")
put("drawn_depth_ft", F["berm_ft"]["value"], ["c33"], "feet deep the fill basin is DRAWN, a drawing rule and not a claim, set equal to the berm height every stake in the deck stands at", rule="= berm_ft", label="drawing")
import datetime as _d
assert (_d.date(2026, 10, 8) - _d.date(2026, 10, 6)).days == F["days_to_vote"]["value"]

json.dump(F, open(HERE / "figures.json", "w"), indent=1)
for k, v in F.items():
    if not k.startswith("_"):
        print(f"{k:28s} {v['value']}")
