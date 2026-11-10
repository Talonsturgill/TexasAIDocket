#!/usr/bin/env python3
"""Figures for carousel no. 73, TACC retires Frontera and a UT Southwestern simulation that took 64 Frontera CPU
nodes runs at almost the same speed on eight Vista GPU nodes (tx-2026-0245).

Every value is read out of a claim quote by a pattern, or computed here from values that were.

RULES, stated so they are choices rather than accidents:
- number words in quotes ("eight GPU nodes", "four SNARE", "seven years", "eight million") map through WORDS only
- node_ratio is cpu_nodes over gpu_nodes, asserted to be a whole number; it is a ratio of NODE COUNTS and never a
  speed ratio, because the Vista speed is given only as "almost the same speed"
- no Frontera node count at retirement is computed (8,008 plus 396 is arithmetic no page confirms)
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"four": 4, "seven": 7, "eight": 8}

def q(cid): return C[cid]["quote"]
def num(cid, pat, f=float):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return f(m.group(1).replace(",", ""))
def word(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return WORDS[m.group(1)]

cpu_nodes = num("c8", r"on (\d+) CPU nodes of Frontera", int)
atoms_million = num("c8", r"a ([\d.]+) million-atom system", float)
ns_per_day = num("c8", r"for (\d+) nanoseconds per day", int)
gpu_nodes = word("c9", r"using just (\w+) GPU nodes")
jobs_million = word("c1", r"having surpassed (\w+) million jobs")
years = word("c2", r"over (\w+) years of production")
snares = word("c11", r"and (\w+) SNARE protein complexes")
researchers = num("c23", r"more than ([\d,]+) U\.S\. researchers", int)
attendees = num("c18", r"More than (\d+) scientists", int)
universities = num("c18", r"from (\d+) universities", int)
tacc_years = num("c24", r"TACC turned (\d+) in June", int)
vista_nodes = num("c25", r"Vista’s (\d+) compute nodes", int)
frontera_nodes_2020 = num("c29", r"existing ([\d,]+) compute nodes", int)
expansion_nodes = num("c31", r"adds (\d+) Dell R640", int)
expansion_racks = num("c31", r"housed in (\d+) racks", int)
xeons_per_node = {"two": 2}[re.search(r"Each node contains (\w+) Intel", q("c30")).group(1)]

assert cpu_nodes % gpu_nodes == 0, (cpu_nodes, gpu_nodes)
node_ratio = cpu_nodes // gpu_nodes

F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
def put(k, v, frm, basis): F[k] = {"value": v, "from": frm, "basis": basis}
put("cpu_nodes", cpu_nodes, ["c8"], "Frontera CPU nodes the 5.3 million atom simulation ran on")
put("gpu_nodes", gpu_nodes, ["c9"], "Vista GPU nodes that gave almost the same speed, Rizo-Rey's account")
put("node_ratio", node_ratio, ["c8", "c9"], "cpu_nodes over gpu_nodes, a ratio of node counts, never of speed")
put("atoms_million", atoms_million, ["c8"], "million atoms in the simulated system")
put("ns_per_day", ns_per_day, ["c8"], "simulated nanoseconds per day on 64 Frontera CPU nodes")
put("jobs_million", jobs_million, ["c1"], "million jobs Frontera surpassed before retirement")
put("years", years, ["c2"], "years of production life, over")
put("snares", snares, ["c11"], "SNARE protein complexes in the simulation")
put("researchers", researchers, ["c23"], "U.S. researchers who have used TACC systems since 2001, more than")
put("attendees", attendees, ["c18"], "symposium attendees, more than")
put("universities", universities, ["c18"], "universities and other organizations at the symposium")
put("tacc_years", tacc_years, ["c24"], "TACC's age in June 2026")
put("vista_nodes", vista_nodes, ["c25"], "all Vista compute nodes; GH200 is the processor for the majority")
put("frontera_nodes_2020", frontera_nodes_2020, ["c29"], "Frontera's compute nodes before the 2020 expansion")
put("expansion_nodes", expansion_nodes, ["c31"], "nodes the expansion added")
put("expansion_racks", expansion_racks, ["c31"], "racks the expansion nodes were housed in")
put("xeons_per_node", xeons_per_node, ["c30"], "Intel Xeon Platinum 8280 processors per Frontera node")
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
