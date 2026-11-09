#!/usr/bin/env python3
"""Figures for carousel no. 72, Texas A&M's AlphaFold-Multimer screen of the human mitochondrial proteome
(tx-2026-0244).

Every value is read out of a claim quote by a pattern, or computed here from values that were.

RULES, stated so they are choices rather than accidents:
- the pair count is checked against the curated list: n proteins make n(n-1)/2 distinct pairs, and the paper's
  630,003 must equal that for its 1123 proteins (an assertion, never a printed figure)
- shares are percent to two decimals, rounded half up; the paper's own "(0.46%)" in c9 must agree
- "one in N" is the pairs per likely interaction rounded to the nearest whole pair
"""
import json, re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}


def q(cid):
    return C[cid]["quote"]


def num(cid, pat, f=float):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return f(m.group(1).replace(",", ""))


proteins_release = num("c1", r"about ([\d,]+) proteins", int)
proteins_curated = num("c2", r"curated list of (\d+) proteins", int)
pairs = num("c4", r"Out of the ([\d,]+) possible protein pairs", int)
likely = num("c4", r"cataloged ([\d,]+) likely interactions", int)
likely_paper = num("c9", r"we predict (\d+) interactions", int)
share_paper = num("c9", r"\(([\d.]+)%\)", float)
proteins_involved = num("c9", r"involving (\d+) proteins", int)
iptm_cutoff = num("c8", r"use ([\d.]+) as a cutoff", float)
recall_pct = num("c8", r"gives (\d+)% recall", int)
fdr_pct = num("c8", r"false discovery rate of about (\d+)%", int)
precision_pct = num("c11", r"with (\d+)% precision", int)
tp_at90_pct = num("c12", r"~(\d+)% of all true positives", int)
at_precision_pct = num("c12", r"at (\d+)% precision", int)
new_pct = num("c14", r"remaining (\d+)% were not present", int)
orphans = num("c30", r"partner for (\d+) uncharacterized", int)
eukaryotes = num("c16", r"to (\d+) diverse eukaryotes", int)
disease_pct = num("c22", r"nearly (\d+)% of mitochondrial", int)

assert likely == likely_paper, (likely, likely_paper)
assert proteins_curated * (proteins_curated - 1) // 2 == pairs, "630,003 is every pair of 1123 proteins"
share_pct = float(Decimal(likely * 100) / Decimal(pairs)).__round__(10)
share_pct_2dp = float(Decimal(str(likely * 100 / pairs)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
assert share_pct_2dp == share_paper, (share_pct_2dp, share_paper)
one_in = int(Decimal(str(pairs / likely)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
not_likely = pairs - likely
new_count_floor_note = "new_pct of likely, never printed as a count"
proteins_without = proteins_curated - proteins_involved

F = {}
def put(k, v, frm, basis):
    F[k] = {"value": v, "from": frm, "basis": basis}
put("proteins_release", proteins_release, ["c1"], "about this many proteins exist within mitochondria, the release")
put("proteins_curated", proteins_curated, ["c2"], "the curated list the screen ran on")
put("pairs", pairs, ["c4", "c3"], "possible protein pairs screened")
put("likely", likely, ["c4", "c9", "c3"], "likely interactions catalogued, mean ipTM over the cutoff")
put("proteins_involved", proteins_involved, ["c9"], "proteins with at least one likely partner")
put("proteins_without", proteins_without, ["c2", "c9"], "curated proteins with no likely partner, computed")
put("share_pct", share_pct_2dp, ["c4", "c9"], "likely as a percent of pairs, two decimals half up, equals the paper's 0.46%")
put("one_in", one_in, ["c4"], "pairs per likely interaction, nearest whole pair")
put("not_likely", not_likely, ["c4"], "pairs under the cutoff, computed")
put("iptm_cutoff", iptm_cutoff, ["c8"], "mean ipTM cutoff")
put("recall_pct", recall_pct, ["c8"], "recall at the cutoff on the authors' test set")
put("fdr_pct", fdr_pct, ["c8", "c10"], "false discovery rate at the cutoff, about")
put("precision_pct", precision_pct, ["c11"], "precision the authors state")
put("tp_at90_pct", tp_at90_pct, ["c12"], "share of true positives recovered at 90% precision, approximate")
put("at_precision_pct", at_precision_pct, ["c12"], "the precision level for tp_at90_pct")
put("new_pct", new_pct, ["c14"], "share of predictions in no existing database")
put("orphans", orphans, ["c30"], "uncharacterized proteins given at least one predicted partner")
put("eukaryotes", eukaryotes, ["c16"], "other eukaryotes screened")
put("disease_pct", disease_pct, ["c22"], "nearly this percent of mitochondrial proteins carry disease-linked mutations")

# THE DRAWING UNITS, choices and never claims
import math
leg_cells = proteins_curated - 1                      # the triangle's leg in cells: each protein against every other
tile_side_cells = math.sqrt(likely)                   # a square tile holding the area of every likely pair
block_cols = math.ceil(tile_side_cells)               # the brass block laid out as close to square as whole cells allow
block_full_rows = likely // block_cols
block_last_row = likely - block_full_rows * block_cols
assert block_full_rows * block_cols + block_last_row == likely
new_cells = int(Decimal(str(likely * new_pct / 100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))   # drawing only, never printed
boss_total = 100                                      # the step frame's hundred calls, a drawing unit
boss_brass = round(boss_total * precision_pct / 100)  # 85 of 100 by the stated precision
boss_steel = boss_total - boss_brass                  # 15, which is the stated false discovery rate
assert boss_steel == fdr_pct
put("leg_cells", leg_cells, ["c2"], "cells along each leg of the half matrix, one protein against each other one")
put("tile_side_cells", round(tile_side_cells, 3), ["c4"], "side of a square tile whose area is every likely pair, drawing only")
put("block_cols", block_cols, ["c4"], "columns of the brass block, drawing only")
put("block_full_rows", block_full_rows, ["c4"], "full rows of the brass block, drawing only")
put("block_last_row", block_last_row, ["c4"], "cells in the block's last row, drawing only")
put("new_cells", new_cells, ["c4", "c14"], "cells of the block drawn as new, from the rounded share, drawing only and never printed")
put("boss_total", boss_total, [], "the hundred calls drawn above the step, a drawing unit")
put("boss_brass", boss_brass, ["c11"], "calls of a hundred drawn in brass, by the stated precision")
put("boss_steel", boss_steel, ["c11", "c10"], "calls of a hundred drawn in steel, equal to the stated false discovery rate")
json.dump({"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were.", **F},
          open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items()}))
