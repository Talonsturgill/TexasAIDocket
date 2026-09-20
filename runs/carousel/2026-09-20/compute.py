#!/usr/bin/env python3
"""Every number this deck states by comparing or counting, computed from claims.json.

NOT ONE OF THESE IS TYPED. The seven raw counts are READ from `computed_values` in
claims.json, where each one records the EPA Envirofacts query that returned it and the fact
that it was measured twice, once by this run and once independently by the fact checker. This
file does the only two operations the deck performs ON TOP of them, and it does them in code
so a reader who disagrees can run it.

THE TWO OPERATIONS, AND WHY EACH IS SOUND.

1. CONTAINMENT, v2 inside v1. `v2`'s query is `v1`'s three filters PLUS one more predicate on
   POPULATION_SERVED_COUNT, so every row v2 counts is a row v1 counts. "3,579 of the 4,749" is
   therefore a statement about a subset and not arithmetic. It is the only relationship between
   the two this deck may state.

   WHAT IS REFUSED AND WHY. `v1 - v2` and `v1 - v3` are NOT computed here and must never appear
   on a frame. The fact checker's note says the population filters may exclude rows where
   POPULATION_SERVED_COUNT is null, and that was not tested, so the three counts are not a
   partition of anything. A subtraction would publish a figure for "the rest" that nobody
   measured. This is the single easiest number for a deck to invent and it is refused in code
   rather than in prose, so a later frame cannot quietly reach for it.

2. A RANKING OVER A NAMED SET. Texas against the four states that were independently
   re-verified, and those four only. The fact checker rejected a fifty state first place
   because forty four counts were never re-fetched, so this ranks five states and the frame
   that carries it names all five. A rank over a set the deck did not read is exactly the
   defect `noun_trace` and the aggregate gate exist for.
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
for cand in (HERE / "claims.json", HERE.parents[2] / "out" / HERE.name / "claims.json"):
    if cand.exists():
        CLAIMS = cand
        break
else:
    raise FileNotFoundError("no claims.json beside %s" % HERE)

doc = json.loads(CLAIMS.read_text(encoding="utf-8"))
V = {v["id"]: v for v in doc["computed_values"]}

STATES = {"v1": "Texas", "v4": "California", "v5": "Washington", "v6": "New York", "v7": "Florida"}

# 1. Containment. Stated as a pair, never as a difference.
subset = {
    "value": V["v2"]["value"],
    "of": V["v1"]["value"],
    "basis": "measured",
    "from": ["v2", "v1"],
    "how": ("v2's query is v1's three filters plus POPULATION_SERVED_COUNT less than 3301, so "
            "every row v2 counts is a row v1 counts. Read from claims.json computed_values by "
            "compute.py. Never a difference, because the filters may exclude null populations "
            "and the counts are not a partition."),
    "set_counted": ("active community water systems in Texas, EPA SDWIS WATER_SYSTEM, "
                    "PRIMACY_AGENCY_CODE TX, PWS_ACTIVITY_CODE A, PWS_TYPE_CODE CWS"),
}

# 2. Ranking over the five states this run actually read.
ranked = sorted(STATES, key=lambda k: -V[k]["value"])
rank_rows = [{"state": STATES[k], "value": V[k]["value"], "from": k} for k in ranked]
texas_rank = [r["state"] for r in rank_rows].index("Texas") + 1

ranking = {
    "value": texas_rank,
    "basis": "measured",
    "from": ranked,
    "how": ("the position of Texas when the five states this run independently re-verified are "
            "sorted by their own EPA count, descending, by compute.py. FIVE states, named on "
            "the frame. Not a national ranking, because forty four state counts were never "
            "re-fetched and a first place finish is a claim about all fifty."),
    "set_counted": "Texas, California, Washington, New York and Florida, and no other state",
    "rows": rank_rows,
}

# 3. The raw counts, passed through with their provenance so a frame can cite one by name.
raw = {vid: {"value": V[vid]["value"], "basis": "measured", "from": [vid],
             "how": V[vid]["how"], "set_counted": V[vid]["label"]}
       for vid in ("v1", "v2", "v3", "v4", "v5", "v6", "v7")}

out = {
    "_note": ("Every count this deck narrates, computed rather than typed. compute.py is "
              "executed at build time rather than copied, and every input is read out of "
              "claims.json. A number in the deck's prose that is not in this file is a number "
              "somebody typed. v1 minus v2 and v1 minus v3 are deliberately absent."),
    "small_systems_of_all": subset,
    "texas_rank_of_five": ranking,
    "counts": raw,
}
(HERE / "figures.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
print("figures.json written")
print("  subset      %s of %s" % (subset["value"], subset["of"]))
print("  rank        Texas is %s of %s states read" % (texas_rank, len(rank_rows)))
for r in rank_rows:
    print("     %-12s %5d  (%s)" % (r["state"], r["value"], r["from"]))
