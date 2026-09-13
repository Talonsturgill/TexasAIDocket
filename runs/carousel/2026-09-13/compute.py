#!/usr/bin/env python3
"""compute.py — every figure this deck draws or prints, computed from the claims file.

No numeral on a slide is typed. The two cohort sizes come from claim c20 and the retained
feature count from c22, both read out of the claims file rather than restated here, and the
grid geometry on frame 5 is derived from them.
"""
import json, re, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.load(open(RUN / "claims.json"))["claims"]}

def only_ints(claim_id, pattern):
    """Pull a figure out of a claim's own quote, so the value is the source's and not ours."""
    m = re.search(pattern, claims[claim_id]["quote"])
    if not m:
        sys.exit(f"compute: {pattern!r} not in {claim_id}'s quote")
    return int(m.group(1))

def only_floats(claim_id, pattern):
    m = re.search(pattern, claims[claim_id]["quote"])
    if not m:
        sys.exit(f"compute: {pattern!r} not in {claim_id}'s quote")
    return m.group(1)

train   = only_ints("c20", r"cohort of (\d+) patients")
extern  = only_ints("c20", r"independent cohort of (\d+) patients")
feats   = only_ints("c22", r"retained (\d+) nonzero")
c_train = only_floats("c22", r"C-index of (0\.\d+) \(95% CI, 0\.\d+-0\.\d+\) in the training")
c_ext   = only_floats("c22", r"and (0\.\d+) \(95% CI, 0\.\d+-0\.\d+\) in external")

COLS = 22                      # chosen so the upper block is nine full rows and a reader can count rows
def block(n):
    full, rest = divmod(n, COLS)
    return {"n": n, "cols": COLS, "full_rows": full, "last_row": rest,
            "rows": full + (1 if rest else 0)}

# FRAME 8'S TWO COUNTS. Its hook says two of the panel's departments are Texan and its dek says
# three leave the sheet. Those are number WORDS, so `numeral_trace` never looks at them, and the
# dossier cited a computation that did not exist until this block. One claim is one named
# department. A department is Texan when its OWN quoted byline names a Texas city, which is the
# part that has to be read off the source rather than decided here.
DEPT_IDS = ["c11", "c12", "c13", "c14", "c15"]
TEXAS_CITIES = ("Houston", "Dallas", "Galveston", "Austin", "San Antonio", "Texas")
texan_ids = [i for i in DEPT_IDS
             if any(t in claims[i]["quote"] or t in claims[i]["text"] for t in TEXAS_CITIES)]
outside_ids = [i for i in DEPT_IDS if i not in texan_ids]

out = {
    "_note": "every value here is read from out/2026-09-13/claims.json, never typed",
    "cohort_train": train, "cohort_external": extern, "features_retained": feats,
    "c_index_train": c_train, "c_index_external": c_ext,
    "grid": {"upper": block(train), "lower": block(extern)},
    "departments": {"total": len(DEPT_IDS),
                    "texan": len(texan_ids), "texan_ids": texan_ids,
                    "outside": len(outside_ids), "outside_ids": outside_ids},
}
(RUN / "computed.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))

# The slides cannot fetch a JSON file from the run directory, so the same object is also emitted
# as a script the engine can load by relative path. One source, two spellings, no typed numeral.
(RUN / "computed.js").write_text("window.TXCOMPUTED = " + json.dumps(out) + ";\n")
