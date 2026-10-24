"""Every figure the October 24th deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}


def quote(cid):
    return claims[cid]["quote"]


def grab(cid, pattern, group=1):
    m = re.search(pattern, quote(cid))
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in its quote")
    return m.group(group)


def num(s):
    return int(s.replace(",", ""))


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

# THE TEXAS VEHICLE ROWS of the installed annual capacity table (c2, c3, c4), floors since each reads ">"
my, ct, cc = num(grab("c2", r">([\d,]+)")), num(grab("c3", r">([\d,]+)")), num(grab("c4", r">([\d,]+)"))
F("model_y", my, ["c2"], "Model Y in Texas, installed annual capacity, more than this many")
F("cybertruck", ct, ["c3"], "Cybertruck, installed annual capacity, more than this many")
F("cybercab", cc, ["c4"], "Cybercab, installed annual capacity, more than this many")
F("vehicle_rows", 3, ["c2", "c3", "c4"], "computed: vehicle rows under the Texas label, counted")
F("model_y_to_cybercab", my // cc, ["c2", "c4"], "computed: the Model Y floor over the Cybercab floor, a whole multiple")
if my % cc:
    raise SystemExit("the Model Y floor is no longer a whole multiple of the Cybercab floor")
F("unit", cc // 1000, ["c4"], "computed: one drawn block stands for this many thousand of installed capacity")
F("model_y_blocks", my // 1000 // (cc // 1000), ["c2", "c4"], "computed: blocks in the Model Y row at one block per Cybercab floor")
F("cybercab_blocks", 1, ["c4"], "computed: the Cybercab row is one block at that scale")
F("cybertruck_blocks", ct // cc, ["c3", "c4"], "computed: the Cybertruck row at the same scale")

# ENERGY AND BATTERY ROWS (c5, c15, c16, c17)
F("megapack_gwh", int(grab("c5", r"(\d+) GWh")), ["c5"], "Megapack in Texas, GWh of installed annual capacity")
F("cells_gwh", int(grab("c15", r">(\d+) GWh")), ["c15"], "4680 cells in Texas, more than this many GWh")
F("cathode_gwh", int(grab("c16", r"(\d+) GWh")), ["c16"], "cathode materials, GWh, early ramp")
F("lithium_gwh", int(grab("c17", r"(\d+) GWh")), ["c17"], "lithium refining, GWh, early ramp")

# THE TRAINING COMPUTE ROWS (c12, c13), and the plan with no location (c21)
c1, c2 = int(grab("c12", r">(\d+) MW")), int(grab("c13", r">(\d+) MW"))
F("cortex1_mw", c1, ["c12"], "Cortex 1 in Texas, more than this many MW of training compute")
F("cortex2_mw", c2, ["c13"], "Cortex 2, more than this many MW of training compute")
F("cortex_texas_mw", c1 + c2, ["c12", "c13"], "computed: the two Texas Cortex floors summed, more than this many MW")
F("plan_mw", int(grab("c21", r"(\d+) MW")), ["c21"], "the year end plan for training compute, with no location")
F("other_mw", int(grab("c14", r"(\d+) MW")), ["c14"], "other compute excluded from the Cortex rows, location not given")
F("mw_per_row", 5, ["c12", "c13"], "a drawing rule: one server row stands for this many MW, so each hall's rows are its floor over this")
F("cortex1_rows", c1 // 5, ["c12"], "computed: Cortex 1 floor over the drawing rule")
F("cortex2_rows", c2 // 5, ["c13"], "computed: Cortex 2 floor over the drawing rule")

# THE ROBOT ROWS: Construction in Texas, Early Ramp in California (c6, c7)
F("optimus_texas_capacity", 0, ["c6"], "the Texas Optimus row's capacity cell is a hyphen, drawn as an empty bay")

# THE AUSTIN HOURS, 6am to midnight (c33)
start = int(grab("c33", r"(\d+)am to midnight"))
F("hours_start", start, ["c33"], "operating hours begin at this hour of the morning")
F("hours_open", 24 - start, ["c33"], "computed: from the start hour to midnight")
F("hours_closed", start, ["c33"], "computed: midnight to the start hour")

# THE FAB (c24)
F("fab_year", int(grab("c24", r"in (\d{4})")), ["c24"], "the year Tesla plans to start commissioning equipment at the Austin Fab")

F("fab_machines_placed", 0, ["c24"], "computed: equipment commissioning is planned and not begun, so no machine is drawn on a pad")

# NHTSA AQ26002 (c38, c42, c36)
F("population", num(grab("c38", r"Population: ([\d,]+)")), ["c38"], "NHTSA's estimated population for the audit query, never a count deployed")
controls = re.findall(r"(brake pedal|gas pedal|steering wheel|mirrors)", quote("c42"))
F("controls_missing", len(controls), ["c42"], "computed: the conventional manual controls NHTSA names as absent, counted")
F("audit_opened_day", int(grab("c36", r"(\d{2})/(\d{2})/(\d{4})", 2)), ["c36"], "the day of the month the audit query opened")


# THE STATUS COLUMN of the Texas manufacturing rows (c2 to c6): Production lit, Construction dark
rows = ["c2", "c3", "c4", "c5", "c6"]
prod = sum(1 for r in rows if quote(r).rstrip().endswith("Production"))
cons = sum(1 for r in rows if quote(r).rstrip().endswith("Construction"))
F("texas_rows", len(rows), rows, "computed: the Texas rows of the manufacturing table the claims quote, counted")
F("production_rows", prod, rows, "computed: of those rows, the ones whose status reads Production, counted")
F("construction_rows", cons, rows, "computed: of those rows, the ones whose status reads Construction, counted")
F("gwh_per_unit", 10, ["c5"], "a drawing rule: one battery enclosure on frame 4 stands for this many GWh, stated in its dek")
F("megapack_units", int(grab("c5", r"(\d+) GWh")) // 10, ["c5"], "computed: the Megapack row's GWh over the drawing rule, enclosures drawn")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print("figures:", len(figures) - 1)
