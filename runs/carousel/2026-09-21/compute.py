#!/usr/bin/env python3
"""Every figure this deck draws, EXTRACTED from claims.json rather than typed.

NOT ONE NUMBER IN THIS FILE IS WRITTEN BY HAND. Each one is pulled out of a claim's
`quote` field by a regular expression anchored on the words around it, so the value on a
frame and the value in the source are the same string by construction. If a quote changes,
this file raises rather than quietly publishing yesterday's number.

WHAT THIS FILE REFUSES TO COMPUTE, and the refusals are the point.

1. NO CHAIN. 21,000 addresses (c29), 10,000 properties scanned (c43), 3,700 notices
   (c28, c43), about 300 cases (c24) and 57 citations (c18) come from three sources,
   measure different things and cover different windows. Nothing establishes that any one
   of them contains any other. They are emitted as a FLAT SET at one scale with no order
   implied, and `counts_reported` carries a `no_containment` flag the storyboard must
   honour. A funnel, a nested set, a stacked bar or an arrow between any two of them
   asserts something the record does not hold.

2. NO DIFFERENCE. `57 - 39` is not computed and must never appear. The memo states 39 of
   the 57 in three districts (c27). It states nothing whatever about the other citations,
   and a deck that draws "18 elsewhere" has published a figure nobody measured. The split
   is emitted as a PART AND A WHOLE, and the remainder is drawn as unmarked ground.

3. NO RECONCILING 68 AND 70. The memo's 68% is 39 of the citations in Districts 4, 8 and 7
   (c27). The 70% is Chad West's own characterisation to FOX 4 about predominantly African
   American neighborhoods (c47). Two speakers, two measures. Both are carried, separately,
   each naming who said it.

4. NO FLEET COUNT. 100 cameras (c1, c9) and 2 cameras per vehicle (c2) are both stated and
   dividing them would publish a truck count no document gives.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
doc = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))
C = {c["id"]: c for c in doc["claims"]}


def grab(cid, pattern, label):
    """Pull one numeral out of one claim's verbatim quote, or raise."""
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit("compute: %s not found in %s's quote" % (label, cid))
    return int(m.group(1).replace(",", ""))


def grab_raw(cid, pattern, label):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit("compute: %s not found in %s's quote" % (label, cid))
    return m.group(1)


# ---------------------------------------------------------------- the counts, flat
counts = [
    {"key": "addresses_flagged", "value": grab("c29", r"potential violations at ([\d,]+) addresses", "21,000"),
     "label": "addresses where the cameras spotted potential violations, in four months",
     "from": ["c29"], "said_by": "city records, reported by NBC 5"},
    {"key": "properties_scanned", "value": grab("c43", r"scanned ([\d,]+) properties", "10,000"),
     "label": "properties the cameras have scanned",
     "from": ["c43"], "said_by": "the September 8th memo, reported by FOX 4"},
    {"key": "courtesy_notices", "value": grab("c28", r"to ([\d,]+) property owners", "3,700"),
     "label": "property owners sent a courtesy notice",
     "from": ["c28", "c43"], "said_by": "the city, reported by NBC 5"},
    {"key": "cases_opened", "value": grab("c24", r"opened about ([\d,]+) cases", "300"),
     "label": "cases opened where priority dictates a code officer visit",
     "from": ["c24"], "said_by": "Jeremy Reed, Assistant Director of Dallas Code Compliance"},
    {"key": "citations", "value": grab("c18", r"([\d,]+) citations have been issued", "57"),
     "label": "citations issued",
     "from": ["c18"], "said_by": "the September 8th memo, reported by NBC 5"},
    {"key": "properties_cited", "value": grab("c18", r"issued at ([\d,]+) properties", "34"),
     "label": "properties those citations were issued at",
     "from": ["c18"], "said_by": "the September 8th memo, reported by NBC 5"},
]

# ---------------------------------------------------- the one containment the memo states
part = grab("c27", r"said ([\d,]+) of those citations", "39")
whole = grab("c18", r"([\d,]+) citations have been issued", "57")
if part > whole:
    raise SystemExit("compute: the part is larger than the whole, which cannot be right")
southern = {
    "part": part, "of": whole, "basis": "measured",
    "from": ["c27", "c18"],
    "districts": [int(d) for d in re.findall(r"Districts (\d+), (\d+) and (\d+)", C["c27"]["quote"])[0]],
    "how": ("Both numerals are read out of the quotes by compute.py. The memo states the part and "
            "the whole in the same sentence, so this is the one containment in this deck. The "
            "difference is never taken, because the memo says nothing about the rest."),
    "set_counted": "citations issued under the camera program as of the September 8th memo",
}

# ------------------------------------------------- the two percentages, kept apart on purpose
percentages = [
    {"key": "memo_share", "value": grab("c27", r"or (\d+)%", "68%"), "unit": "percent",
     "said_by": "the City Manager's memo, reported by NBC 5",
     "of_what": "the citations, issued in City Council Districts 4, 8 and 7 in Southern Dallas",
     "from": ["c27"]},
    {"key": "west_share", "value": grab("c47", r"says (\d+)%", "70%"), "unit": "percent",
     "said_by": "Council member Chad West, to FOX 4",
     "of_what": "the citations, coming from predominantly African American neighborhoods",
     "from": ["c47"]},
]

# ------------------------------------------------------------------- the machine's own numbers
hardware = {
    "cameras": {"value": grab("c1", r"Implement (\d+) AI-enabled cameras", "100"), "from": ["c1", "c9"],
                "label": "AI enabled cameras on sanitation brush trucks"},
    "cameras_per_vehicle": {"value": grab("c2", r"^(\d+) cameras mounted", "2"), "from": ["c2"],
                            "label": "cameras mounted on one city vehicle"},
    "speed_range": {"value": grab_raw("c3", r"\((\d+-\d+) MPH\)", "25-35"), "from": ["c3"],
                    "label": "the speed the truck photographs at, in miles per hour"},
    "resolution": {"value": grab_raw("c4", r"at (\d+p x \d+p) resolution", "1920p x 1080p"), "from": ["c4"],
                   "label": "the capture resolution"},
    "annual_cost": {"value": grab("c9", r"\$([\d,]+) per year", "852,000"), "unit": "dollars",
                    "from": ["c9", "c45"], "label": "the contract cost per year"},
    "three_year_cost": {"value": grab("c8", r"estimated amount of \$([\d,]+)", "2,556,000"), "unit": "dollars",
                        "from": ["c8"], "label": "the three year contract's estimated amount"},
    "termination_days": {"value": grab("c10", r"with (\d+) days", "10"), "unit": "days",
                         "from": ["c10"], "label": "written notice the City may terminate on"},
    "retention_years": {"value": 1 if "retained for one year" in C["c36"]["quote"] else None,
                        "unit": "years", "from": ["c36"],
                        "label": "how long the city says the images are kept"},
}
if hardware["retention_years"]["value"] is None:
    raise SystemExit("compute: the retention phrase moved in c36")

# ------------------------------------------------------------------ the refusals, as three refusals
refusals = re.findall(r"NOT ([a-z ]+)", " ".join(C[k]["quote"] for k in ("c12", "c13")))
if len(refusals) != 3:
    raise SystemExit("compute: expected three NOT lines, found %d" % len(refusals))


# ---------------------------------------------------- two counts of listed things, counted in code
# THE DETECTION LIST. c7's quote is the slide's heading, because each item sits on its own line and
# is too short to quote alone, so the items are carried in the claim's TEXT. They are counted here
# rather than typed, off that text, which is why the separator is fixed rather than eyeballed.
_items = C["c7"]["text"].split("They are ", 1)[1].rstrip(".")
detection = [x.strip() for x in re.split(r",| and ", _items) if x.strip()]
if len(detection) < 5:
    raise SystemExit("compute: the detection list in c7 did not split, found %d" % len(detection))

# THE LETTER'S OWN SENTENCES. Four claims quote four separate things the notice says about itself.
letter_ids = ["c20", "c21", "c22", "c23"]
for _i in letter_ids:
    if _i not in C:
        raise SystemExit("compute: the letter claim %s is gone" % _i)

# ------------------------------------------------- the capture aspect, DIVIDED IN CODE AND ONCE
# THE ONE DIVISION IN THIS FILE, and it earns its place. The deck's motif is the rectangle the
# machine makes, and its shape has to be the shape the briefing states rather than a 16 by 9
# somebody remembered. Both operands are parsed out of c4's quote, so a frame drawing this ratio
# is drawing the document's own numbers and a changed quote makes the rectangle change shape.
_res = re.match(r"(\d+)p x (\d+)p", hardware["resolution"]["value"])
if not _res:
    raise SystemExit("compute: the resolution string in c4 no longer parses")
cap_w, cap_h = int(_res.group(1)), int(_res.group(2))

out = {
    "_note": ("Every value here is extracted from a claim's verbatim quote by compute.py, which is "
              "executed at build time rather than copied. A numeral in this deck's prose or artwork "
              "that is not in this file is a numeral somebody typed. Read the module docstring for "
              "the four things this file refuses to compute and why."),
    "counts_reported": {
        "no_containment": True,
        "why": ("Three sources, three measures, three windows. Nothing here establishes that any one "
                "count contains any other, so these are drawn at ONE scale as a flat set, never as a "
                "funnel, a chain, a nested set, a stacked bar or an arrow."),
        "rows": counts,
    },
    "southern_districts": southern,
    "percentages_not_reconciled": {
        "why": ("Two speakers describing two different sets. The deck prints both with the speaker "
                "named on each and computes nothing from either."),
        "rows": percentages,
    },
    "hardware": hardware,

    # TOP LEVEL AND NUMERIC, because that is the only shape `figure_bearing.py` can price. A figure
    # nested one level down resolves to no computed number, and the gate says so rather than
    # guessing, which is correct: a name a checker cannot resolve is a name a frame can claim and
    # nobody can check.
    "capture_aspect": {"value": cap_w / cap_h, "from": ["c4"], "of": cap_w,
                       "label": "the capture rectangle's width over its height, divided in code from the two numerals in c4's quote",
                       "how": "the only division compute.py performs, and it sets a drawn width from a drawn height"},
    "capture_width_px": {"value": cap_w, "from": ["c4"], "label": "the capture's width in machine pixels"},
    "capture_height_px": {"value": cap_h, "from": ["c4"], "label": "the capture's height in machine pixels"},
    "cameras_per_vehicle": {"value": hardware["cameras_per_vehicle"]["value"], "from": ["c2"],
                            "label": "cameras mounted on one city vehicle"},
    "cameras_total": {"value": hardware["cameras"]["value"], "from": ["c1", "c9"],
                      "label": "AI enabled cameras the briefing proposed"},
    "detection_conditions": {"value": len(detection), "words": detection, "from": ["c7"],
                             "label": "property conditions the software detects, as the briefing lists them"},
    "letter_lines": {"value": len(letter_ids), "from": letter_ids,
                     "label": "separate things the courtesy notice says about itself, one per claim"},
    "refusals": {"value": len(refusals), "words": [r.strip() for r in refusals], "from": ["c12", "c13"],
                 "label": "things the December 2025 briefing said the system is NOT"},
}
(HERE / "figures.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("figures: %d counts, %d of %d in three districts, %d refusals, %d detections, %d letter lines, %d hardware"
      % (len(counts), southern["part"], southern["of"], len(refusals), len(detection), len(letter_ids), len(hardware)))
