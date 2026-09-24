#!/usr/bin/env python3
"""aggregates.json for 2026-09-24. Every figure the detector reads as a count is declared with
the claim it was READ from. This deck computes no count by addition: every one of these is the
draft's own printed figure, quoted, and the only arithmetic in the deck (the table's totals, the
three transits, the per Charger cap) is ASSERTED in compute.py against the draft rather than
published as a new number."""
import json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
F = json.loads((HERE / "figures.json").read_text())
Q = [  # phrase, slide, value, claim, the exact string in that claim the figure is read from
 ("75 seconds", "slide-02.html", F["delivery_hover"]["seconds"], "c19", "(approximately 75 seconds)"),
 ("75 seconds", "caption.txt", F["delivery_hover"]["seconds"], "c19", "(approximately 75 seconds)"),
 ("63 pounds", "slide-05.html", F["aircraft"]["weight_lb"], "c13", "weighs approximately 63 pounds"),
 ("8 pounds", "slide-05.html", F["aircraft"]["payload_lb"], "c13", "maximum payload weight of 8 pounds"),
 ("220 Chargers", "slide-06.html", F["total"]["chargers"], "c7", "Total 17,584 220 4,400 220,000 660,000"),
 ("4,400 Dropboxes", "slide-06.html", F["total"]["dropboxes"], "c7", "Total 17,584 220 4,400 220,000 660,000"),
 ("220,000 deliveries", "slide-06.html", F["total"]["deliveries_max"], "c7", "Total 17,584 220 4,400 220,000 660,000"),
 ("400 deliveries", "slide-07.html", F["noise"]["at_deliveries_per_location"], "c21", "At a rate of 400 average daily deliveries per day"),
 ("36 docks", "slide-06.html", F["charger_docks"]["typical"], "c32", "most Chargers would have around 36 docks"),
 ("three towers", "slide-06.html", {"three": 3}[F["charger_towers"]["towers_word"]], "c34", "arranged in three towers of twelve docks each"),
]
A = [dict(phrase=p, slide=sl, kind="count", value=v, quoted_from=c, quote=q,
          note="the draft's own printed figure, quoted; compute.py asserts the table's arithmetic rather than publishing a new number") for p, sl, v, c, q in Q]
A.append(dict(phrase="two official records", slide="first_comment.txt", kind="count", value=2, from_claims=["c1", "c4"],
              note="the FAA's review page (c1) and the draft EA itself (c4), the two documents every printed claim id resolves to"))
EXTRA = json.loads((HERE / "tmp" / "aggregates_extra.json").read_text()) if (HERE / "tmp" / "aggregates_extra.json").exists() else []
doc = {"date": "2026-09-24", "_note": __doc__.strip(),
       "aggregates": A + EXTRA}
(HERE / "aggregates.json").write_text(json.dumps(doc, indent=1) + "\n")
print("aggregates:", len(doc["aggregates"]))
