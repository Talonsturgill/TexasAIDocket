#!/usr/bin/env python3
"""Every measured or counted number in a dossier, written from the artifacts.

Round 6's hard fail was that the SHIPPED SOURCE did not draw the deck beside it. That was fixed
in three files and the superseded deck simply moved one file over: round 7 found slide 2's
dossier saying "fourteen" four times over a frame that renders fifteen, slide 3 declaring
span_days 154 against a printed 156, slide 6 printing 70.8 and 18.4 where measurements.json says
70.6 and 18.2, and slide 8 still calling itself the deck's quietest in a frame whose own code
comment quotes that sentence, calls it wrong, fixes the pixels and leaves the plan alone.

A plan nobody regenerates is a plan that describes the last deck. This regenerates it.
"""
import json, pathlib, re
ROOT = pathlib.Path("/home/user/TexasAIDocket")
F = json.loads((ROOT / "out/2026-08-25/figures.json").read_text())
M = json.loads((ROOT / "out/2026-08-25/measurements.json").read_text())
V = lambda k: F[k]["value"]
med, junc = M["per_frame_median_lstar"], M["junctions"]
W = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
     "fifteen sixteen seventeen").split()
n, bodies = V("restricted_count"), V("acting_bodies")
half = (n + 1) // 2
p = ROOT / "out/2026-08-25/storyboard.md"; s = p.read_text()

PAIRS = [
 # slide 2, the frame that grew from seven to fourteen to fifteen while its plan stood still
 ("  Show that the fourteen actions are a typology rather than one action repeated, by listing all\n"
  "  fourteen instruments on one sheet, in two columns, under one hard shadow.",
  f"  Show that the {W[n]} actions are a typology rather than one action repeated, by listing all\n"
  f"  {W[n]} of them on one sheet, in two columns, under one broad occlusion gradient."),
 ('  - computed_by: "out/2026-08-25/compute.py, distinct_shapes, seven instruments across seven bodies"',
  f'  - computed_by: "out/2026-08-25/compute.py, restricted_count and acting_bodies, {W[n]} actions\n'
  f'      across {W[bodies]} local governments. distinct_shapes is NOT declared and is not published:\n'
  f'      len(set()) over labels compute.py writes can only equal the number of labels, so no two\n'
  f'      alike was a sentence that could not be false. `resolutions` is the substantive version."'),
 ("    middle third carries fourteen instrument names in two columns of seven, set hanging indent in\n"
  "    toner, the left column's first rows in light and the right column crossed by the shadow.",
  f"    middle third carries {W[n]} instrument names in two columns, {W[half]} then {W[n-half]}, set\n"
  f"    hanging indent in toner, the left column's first rows in light and the right column in shade."),
 ("    Lightest is the lit half of the sheet. Darkest is the shadow core at the sheet's top left",
  "    Lightest is the lit wedge at the sheet's upper left. Darkest is the shade core at the LOWER\n"
  "    RIGHT, which is where the code puts it. An earlier draft of this line had the core top left\n"
  "    and the lit half to the right, describing the opposite of what draws"),
 ('  - "every one of the fourteen instrument names is legible at 1080px and none is clipped by the shadow edge"',
  f'  - "every one of the {W[n]} instrument names is legible at 1080px and each carries the claim id\n'
  f'     whose own words prove its shape"'),
 ('  - "fourteen lines under a diagonal is one step from a table with a gradient on it, and a table is furniture"',
  f'  - "{W[n]} lines under a diagonal is one step from a table with a gradient on it, and a table is furniture"\n'
  f'  - "a HARD edge cannot ship on this frame. {W[n]} lines fill the sheet and machine QA reads a value\n'
  f'     boundary across a glyph band as the strikethrough it looks like at feed size"'),
 ("  Show WHEN the fourteen actions fell, by seating one letterboard tile per action against its month,",
  f"  Show WHEN the {W[n]} actions fell, by seating one letterboard tile per action against its month,"),
 ('  - computed_by: "out/2026-08-25/compute.py, span_days, 154"',
  f'  - computed_by: "out/2026-08-25/compute.py, span_days, {V("span_days")}"'),
]
# the measured lines, composed from measurements.json rather than typed
PAIRS += [
 (f"    step: measured, it is 70.8 and frame 7 immediately after it is 52.4, a 18.4 L* drop, which is",
  f"    step: measured, it is {med[5]} and frame 7 immediately after it is {med[6]}, a "
  f"{abs(junc[5])} L* drop, which is"),
 ("    L*, and the frame's field at 52.4 is 18.4 L* under frame 6 before it. It is not the deck's",
  f"    L*, and the frame's field at {med[6]} is {abs(junc[5])} L* under frame 6 before it. It is not the deck's"),
 ("    right. The frame is the deck's quietest and it sits between its two loudest.",
  f"    right. Measured it is {med[7]}, with frames 7 and 9 at {med[6]} and {med[8]} either side, so it\n"
  f"    is the BRIGHTEST of the deck's last three. An earlier draft called it the quietest between\n"
  f"    its two loudest, which was wrong on both halves and was reported repaired twice without being\n"
  f"    touched. It is written from measurements.json now."),
]
hit = 0
for a, b in PAIRS:
    if a in s:
        s = s.replace(a, b); hit += 1
p.write_text(s)
print(f"{hit} of {len(PAIRS)} dossier passages regenerated from the artifacts")
