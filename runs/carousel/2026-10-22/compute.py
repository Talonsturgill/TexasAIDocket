"""Every figure the October 22nd deck states or draws, extracted from a claim quote or computed here.

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


def row(cid, label):
    """A Table 2 row: the label, then eleven cells, M1 100/80/50/20/0, M2 100/80/50/20/0, Base (c31)."""
    q = quote(cid)
    if not q.startswith(label):
        raise SystemExit(f"{cid}: quote does not open with {label!r}")
    cells = [float(x) for x in q[len(label):].split()]
    if len(cells) != 11:
        raise SystemExit(f"{cid}: {len(cells)} cells, expected 11")
    return cells


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

# the column order, read from c31's own header rather than assumed
ratios = [int(x) for x in re.findall(r"(\d+)%", quote("c31"))][:5]
if ratios != [100, 80, 50, 20, 0]:
    raise SystemExit(f"c31: unexpected M1 column order {ratios}")
F("junk_ratios_m1", ratios, ["c31"], "junk share of the training mix, percent, in the table's column order")

for key, cid, label, basis in (
    ("arc_cot", "c33", "Challenge (COT) Acc.", "ARC Challenge accuracy with chain of thought, Llama3 8B Instruct"),
    ("ruler_overall", "c34", "Long-Context (RULER) Overall", "RULER overall long context score, Llama3 8B Instruct"),
    ("ruler_cwe", "c35", "Comm Word Ext (CWE)", "RULER common word extraction, Llama3 8B Instruct"),
    ("var_tracking", "c36", "Variable Tracking", "RULER variable tracking, Llama3 8B Instruct"),
):
    cells = row(cid, label)
    F(key + "_m1", cells[:5], [cid, "c31"], basis + ", M1 at 100, 80, 50, 20 and 0 percent junk")
    F(key + "_base", cells[10], [cid, "c31"], basis + ", Base")
    for r, v in zip(ratios, cells[:5]):
        F(f"{key}_j{r}", v, [cid, "c31"], basis + f", M1 at {r} percent junk")

# the abstract's end points must agree with the table's, or the deck is reading two different numbers
a0, a1 = float(grab("c28", r"drops ([\d.]+) -> ([\d.]+)")), float(grab("c28", r"drops ([\d.]+) -> ([\d.]+)", 2))
if [a0, a1] != [figures["arc_cot_m1"]["value"][4], figures["arc_cot_m1"]["value"][0]]:
    raise SystemExit("c28 and c33 disagree on ARC Challenge COT")
c0, c1 = float(grab("c29", r"RULER-CWE ([\d.]+) -> ([\d.]+)")), float(grab("c29", r"RULER-CWE ([\d.]+) -> ([\d.]+)", 2))
if [c0, c1] != [figures["ruler_cwe_m1"]["value"][4], figures["ruler_cwe_m1"]["value"][0]]:
    raise SystemExit("c29 and c35 disagree on RULER CWE")

F("posts_million", int(grab("c16", r"the (\d+)-million public")), ["c16"], "million public Twitter/X posts the sets were drawn from")
F("junk_tokens_lt", int(grab("c18", r"token length < (\d+)")), ["c18"], "junk posts are shorter than this many tokens, M1")
F("junk_pop_gt", int(grab("c18", r"popularity of > (\d+)")), ["c18"], "junk posts have popularity over this, M1")
F("control_tokens_gt", int(grab("c18", r"token length > (\d+) >\d+ \(the 99th")), ["c18"], "control posts are longer than this many tokens, M1")
F("control_pop_eq", int(grab("c18", r"popularity of = (\d+)")), ["c18"], "control posts have this popularity, M1")
F("tokens_million", float(grab("c21", r"is ([\d.]+) million")), ["c21"], "million tokens each of junk and control, balanced")
F("models", int(grab("c27", r"of (\d+) LLMs")), ["c27"], "open models tested")
F("no_thinking_all_pct", int(grab("c39", r"over (\d+) %")), ["c39"], "percent of failures with No Thinking across all cases, over")
F("no_thinking_m1_pct", int(grab("c39", r"and (\d+) %")), ["c39"], "percent of failures with No Thinking under M1 junk")
F("it_multiple", float(grab("c44", r"consisting of ([\d.]+) ")), ["c44"], "instruction data as a multiple of the junk tokens")
F("it_from_k", int(grab("c43", r"from (\d+)k to")), ["c43"], "thousand Alpaca examples before the repair scale up")
F("it_to_k", int(grab("c43", r"to (\d+)k examples")), ["c43"], "thousand Alpaca examples after, the whole set")
F("cpt_million", float(grab("c45", r"0 to ([\d.]+) million")), ["c45"], "million C4 tokens of clean continual pre-training, at most")
F("gap_arc_pct", float(grab("c47", r"([\d.]+) % [\d.]+\\% \(ARC-C COT\)")), ["c47"], "absolute points the best repaired model trails Base on ARC Challenge COT")
F("reflect_iters", int(grab("c49", r"After (\d+) iterations")), ["c49"], "Ext-Reflect iterations to a baseline thought skipping rate")

# computed: the drop across the dose, in points, rounded to one decimal by the rule below
arc = figures["arc_cot_m1"]["value"]
F("arc_drop_pts", round(arc[4] - arc[0], 1), ["c33"], "points ARC Challenge COT lost from 0 to 100 percent junk, to one decimal")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print("figures.json:", len(figures) - 1, "figures")
