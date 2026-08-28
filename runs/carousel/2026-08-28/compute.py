#!/usr/bin/env python3
"""Every numeral the deck prints, computed here from claims.json and nowhere else.

The law this file exists for is in CLAUDE.md. No numeral on a frame is typed by a person or
produced by a model. A figure reaches a slide as a string this file emitted, or it does not
reach a slide.

Two figures in this docket look alike and are not the same thing, so they are kept apart by
name here rather than by care later. GEN_MW is what GOODNIT1 can generate, a commission
finding. LOAD_ONE_MW is the size of the first data center, a different commission finding.
CONTENDED_TOTAL_MW is neither. It is Ensign and Crusoe's arithmetic, which the order records
without adopting, and every string derived from it carries the attribution in its own key.
"""
import json, pathlib, sys

RUN = pathlib.Path(__file__).resolve().parent
CLAIMS = json.loads((RUN / "claims.json").read_text())["claims"]
BY = {c["id"]: c for c in CLAIMS}

def quoted(cid, needle):
    """Assert a figure is actually in the claim's verbatim quote before using it."""
    q = BY[cid]["quote"]
    if needle not in q:
        sys.exit(f"compute: {needle!r} is not in claim {cid}'s quote. Refusing to invent it.")
    return needle

# --- figures, each pinned to the quote it came out of --------------------------------------
GEN_MW            = float(quoted("c3",  "265.5")[:5])   # GOODNIT1's generating capacity
LOAD_ONE_MW       = float(quoted("c5",  "265")[:3])     # the Crusoe One data center
LOAD_TWO_MW       = float(quoted("c5",  "260")[:3])     # the Crusoe Two data center
CONTENDED_MW      = float(quoted("c12", "525.5")[:5])   # THE APPLICANTS' FIGURE
WINDOW_MIN        = int(quoted("c9",  "30 minutes")[:2])
ELECTED_MIN       = int(quoted("c9",  "10 minutes")[:2])
NOTICE_MIN        = int(quoted("c10", "60 minutes")[:2])

def mw(v):   return f"{v:,.1f} MW" if v % 1 else f"{v:,.0f} MW"
def mins(v): return f"{v} minutes"

# --- THE ARITHMETIC SLIDE 6's HOOK PROMISES AND THE FRAME NEVER SHOWED --------------------
#
# Slide 6 reads "The applicants did the arithmetic." and then printed 525.5 and 265.5 on one
# chart without ever saying they were related. A reader judge found it: the sum is the deck's
# only available stake, it needed no new source, and it was sitting on the frame unsaid.
#
# The applicants' contention is that curtailing under Condition 1 takes the Crusoe Two Load
# AND GOODNIT1's generation together. That is 260 plus 265.5, and it is where 525.5 comes from.
#
# ASSERTED, NOT ASSUMED. If the sum ever stops matching the quoted total, this file stops the
# build rather than printing a relationship the record does not support.
COMPONENT_SUM = LOAD_TWO_MW + GEN_MW
if abs(COMPONENT_SUM - CONTENDED_MW) > 1e-9:
    sys.exit(f"compute: {LOAD_TWO_MW} + {GEN_MW} is {COMPONENT_SUM}, not the quoted "
             f"{CONTENDED_MW}. The applicants' total is not these two components. "
             f"Refusing to publish the sum.")

out = {
  # ---- the strings a frame may print -------------------------------------------------------
  "gen_mw":        mw(GEN_MW),
  "load_one_mw":   mw(LOAD_ONE_MW),
  "load_two_mw":   mw(LOAD_TWO_MW),
  "contended_mw":  mw(CONTENDED_MW),
  "window":        mins(WINDOW_MIN),
  "elected":       mins(ELECTED_MIN),
  "notice":        mins(NOTICE_MIN),

  # ---- ratios, for GEOMETRY. None of these is printed as a numeral -------------------------
  "ratio_contended_to_gen": CONTENDED_MW / GEN_MW,
  "ratio_two_to_gen":       LOAD_TWO_MW / GEN_MW,
  "ratio_one_to_gen":       LOAD_ONE_MW / GEN_MW,
  "ratio_elected_to_window": ELECTED_MIN / WINDOW_MIN,
  "ratio_window_to_notice":  WINDOW_MIN / NOTICE_MIN,

  # ---- the scale every megawatt plane on this deck is drawn at ----------------------------
  # One scale, declared once, so two frames can be compared by eye and be right to do so.
  #
  # THE SPAN IS THE DRAWABLE HEIGHT, MEASURED, NOT A ROUND NUMBER. At 560 the tallest marker
  # sat at y 440 with its recess opening at 388, and the hook plate on slide 6 ends at y 426.5,
  # measured off the render. The top of the deck's largest figure was painted over by the hook
  # above it. 490 puts that opening at 458 and clears the plate by 31 px.
  #
  # An axis that runs under the furniture is the same defect as a truncated one: the reader is
  # shown less of the quantity than the frame claims to be showing.
  "px_per_mw": 490.0 / CONTENDED_MW,

  # ---- the sum, as the frame prints it. Both components and the total are quoted figures ----
  "component_sum_expr": f"{mw(LOAD_TWO_MW)} load + {mw(GEN_MW)} generation",
  "contended_over_gen": CONTENDED_MW / GEN_MW,

  # ---- attribution, carried beside the figure so a frame can't print one without the other -
  "contended_attribution": "the applicants' count, which the order records",
  "gen_attribution":       "the commission's finding",
}
for k in ("gen","load_one","load_two","contended"):
    src = {"gen": GEN_MW, "load_one": LOAD_ONE_MW, "load_two": LOAD_TWO_MW, "contended": CONTENDED_MW}[k]
    out[f"{k}_px"] = round(src * out["px_per_mw"], 2)

# --- dates. Quoted in the source in one form and printed in the house's, so the conversion
# --- is a computation here rather than a re-typing on a frame.
import datetime, re

def ordinal(d):
    n = d.day
    suf = "th" if 11 <= n <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{d:%B} {n}{suf}, {d.year}"

def date_from(cid, pattern, fmt):
    m = re.search(pattern, BY[cid]["quote"])
    if not m:
        sys.exit(f"compute: no date matching {pattern!r} in claim {cid}'s quote.")
    return datetime.datetime.strptime(m.group(0), fmt).date()

ORDER_DATE     = date_from("c25", r"July \d{1,2}, \d{4}", "%B %d, %Y")
REHEARING_DATE = date_from("c26", r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d")
COMMENT_DATE   = date_from("c24", r"September \d{1,2}, \d{4}", "%B %d, %Y")

out["order_date"]     = ordinal(ORDER_DATE)
out["rehearing_date"] = ordinal(REHEARING_DATE)
out["comment_date"]   = ordinal(COMMENT_DATE)
out["days_order_to_rehearing"] = (REHEARING_DATE - ORDER_DATE).days
out["docket"] = "59220"

# The one column every figure on slide 5 is set against, so three rows align without three
# separately typed x positions drifting apart.
SAFE_L = 80.0
# The slope chart's axis furniture. A judge called "100 MW" and "0 MW" numerals that traced
# to nothing, and the call was right: an axis unit is published copy like any other numeral.
SCALE_STEP_MW = 100.0
out["axis_zero_label"]  = mw(0)
out["scale_step_label"] = mw(SCALE_STEP_MW)
out["scale_step_px"]    = round(SCALE_STEP_MW * out["px_per_mw"], 2)
out["fig_col_x"] = SAFE_L + 16.0
out["label_col_x"] = out["fig_col_x"] + 404.0

(RUN / "computed.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
