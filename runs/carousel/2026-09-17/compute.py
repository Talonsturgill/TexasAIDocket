#!/usr/bin/env python3
"""Every figure this deck states that it did not quote, computed so it can be re-run.

Three numerals on this deck are the deck's OWN arithmetic over documents this run read, and
they are the three this file produces. Everything else on a frame is quoted from a source and is
declared in aggregates.json with the string it came out of.

NOTHING HERE IS TYPED. The section count is the length of a list extracted from the fetched
statute text by a regular expression. The search-term count is the length of the list the slide
itself iterates. The figure count is the length of the list the slide itself draws.
"""
import json
import pathlib
import re

_HERE = pathlib.Path(__file__).resolve().parent
STATUTE = _HERE / "sources" / "bc-552-traiga.txt"
if not STATUTE.exists():
    STATUTE = _HERE.parents[2] / "out" / "2026-09-17" / "sources" / "bc-552-traiga.txt"
SLIDES = _HERE / "slides"
if not SLIDES.exists():
    SLIDES = _HERE.parents[2] / "out" / "2026-09-17" / "slides"

out = {}

# 1. EVERY SECTION IN CHAPTER 552, extracted from the statute page this run fetched. Frame 8
#    draws the list and its hook says none of them is headed Applicability, so the list and the
#    claim have to come from the same place.
text = re.sub(r"\s+", " ", STATUTE.read_text(errors="replace"))
secs = []
for s in re.findall(r"Sec\. 552\.\d{3}\.\s+[A-Z][A-Z ,;'\-]+?\.\s", text):
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    if s not in secs:
        secs.append(s)
applicability = [s for s in secs if "APPLICABILIT" in s.upper() or "SCOPE" in s.upper()]
out["sections_in_chapter_552"] = {
    "value": len(secs), "unit": "sections", "basis": "measured",
    "from": ["absences[3]"],
    "how": "every distinct 'Sec. 552.NNN. HEADING' in the fetched statute text, deduplicated in order",
    "members": secs,
}
out["sections_headed_applicability_or_scope"] = {
    "value": len(applicability), "unit": "sections", "basis": "measured",
    "from": ["absences[3]"],
    "how": "of the sections above, those whose heading contains APPLICABILIT or SCOPE",
    "members": applicability,
}

# 2. THE EIGHT SEARCH TERMS, read off the slide that draws them, so the frame's hook and the
#    frame's boxes can never disagree about how many there are.
f4 = (SLIDES / "slide-04.html").read_text()
terms = re.search(r"var TERMS = \[(.*?)\];", f4, re.S).group(1)
terms = [t.strip().strip('"') for t in terms.replace("\n", " ").split(",") if t.strip()]
out["terms_searched_on_the_announcement"] = {
    "value": len(terms), "unit": "search terms", "basis": "measured",
    "from": ["absences[0]"],
    "how": "the length of the TERMS list frame 4 iterates to draw its boxes",
    "members": terms,
}

# 3. THE 52 FIGURES, read off the slide that draws them. The slide itself throws if the rows do
#    not sum to the figure the source states, so the drawing and the claim cannot drift.
f6 = (SLIDES / "slide-06.html").read_text()
ranks = [int(x) for x in re.search(r"var RANKS = \[(.*?)\];", f6).group(1).split(",")]
out["figures_drawn_for_the_pilot"] = {
    "value": sum(ranks), "unit": "figures", "basis": "measured",
    "from": ["c14"],
    "how": "the sum of the RANKS array frame 6 draws, asserted against the source's own 52 by the slide itself",
    # EVERY RANK, NOT THE FIRST ONE TIMES THE COUNT. `{len(ranks)} rows of {ranks[0]}` was only
    # ever right while the ranks were equal, and the array it describes is ragged on purpose:
    # the short last rank is the frame's declared focal, because it is where the count stops
    # being round. The old expression would have printed "5 ranks of 11" and hidden exactly the
    # thing the frame is built to show.
    "members": [f"{len(ranks)} ranks of " + ", ".join(str(r) for r in ranks)],
}

print(json.dumps(out, indent=1))
(_HERE / "figures.json").write_text(json.dumps(out, indent=1) + "\n")
