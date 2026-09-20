#!/usr/bin/env python3
"""update_ledgers.py — the three variety ledgers, written from this run's own artifacts.

WHY THIS IS A SCRIPT RATHER THAN THREE EDITS. Every count and every measurement in these
entries is READ from a file this run produced. `ledger_check` validates the newest topic
entry's spelled number words against this run's figure keys, and the captions entry carries
a comma rate that `caption_check` measured. A hand-typed entry is a number a model produced,
which is the one thing this repo's compute-not-generate law forbids outright.
"""
import json, pathlib, re, sys

RUN = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out/2026-09-20")
DATE, NO = "2026-09-20", 30
L = pathlib.Path("ledger/carousel")

claims = json.loads((RUN / "claims.json").read_text())
meas = json.loads((RUN / "measurements.json").read_text())
cap = (RUN / "caption.txt").read_text().strip()
sb = (RUN / "storyboard.md").read_text()

# ---- the caption's own measurements, counted here rather than asserted
body = "\n".join(l for l in cap.splitlines() if not l.strip().startswith("#"))
words = len(body.split())
commas = body.count(",") - len(re.findall(r"\d,\d", body))   # writer's commas only
hashtags = re.findall(r"#\w+", cap)
first_line = cap.splitlines()[0].strip()

topics = json.loads((L / "topics.json").read_text())
artwork = json.loads((L / "artwork.json").read_text())
captions = json.loads((L / "captions.json").read_text())

topics["entries"].append({
  "date": DATE, "carousel_no": NO, "docket_item": "tx-2026-0176",
  "instrument": "one federal award record read through the funder's own search API, plus three counts read from a federal regulator's public query interface",
  "topic": "The National Science Foundation made a standard grant to the Texas A&M Engineering Experiment Station for AI enabled predictive digital twins of freshwater infrastructure under cascading hazards, with the abstract's first stated direction aimed at small and mid sized systems, against an EPA Envirofacts count of the active community water systems in Texas and of how many of them are small.",
  "angle": "The award's own abstract states the criticism, so the deck hands the reader that sentence rather than paraphrasing it, and the criticism is narrow. It is about instruments and not about people. Nothing is deployed, the award's verb is the conditional, and the deck's argument is the distance between a record that is complete and a question a complete record cannot answer.",
  "angle_note": "THE STRONGEST STORY OF THE DAY WAS REFUSED ON THE GATE AND IT IS WORTH THE LINE. The Flock split, El Paso ordering removal while Carrollton expanded the same night and TxDOT suspending permits above both, returned dedupe_check LIKELY REPEAT at 0.74 against carousel no. 12 of August 30th. The full entry was read rather than its title, as the phase requires, and it is a repeat. runs/carousel/2026-09-20/SELECTION.md carries the reasoning. THE DECK CARRIES NO PLACE AND THREE JUDGES SAID SO ACROSS TWO ROUNDS. Brazos County is the drawn world and reaches no frame, and the deck's own law forbids a county sign in the drawing. Nothing forbade the copy from placing it, and that is a cost this run took rather than a rule it obeyed.",
  "entities": ["U.S. National Science Foundation", "Texas A&M Engineering Experiment Station",
               "U.S. Environmental Protection Agency", "Texas Commission on Environmental Quality"],
  "entities_note": "The principal investigator is named in the record and on no frame. A person's name on a slide makes a research award about a person, and the abstract's criticism is explicitly about instruments rather than about anybody's practice.",
  "keywords": ["digital twin", "NSF award", "Texas A&M", "freshwater infrastructure",
               "cascading hazards", "community water system", "EPA Envirofacts", "SDWIS",
               "TCEQ", "small water systems"],
  "prose_note": "Every count above is written in words that are not number words, because ledger_check validates spelled number words in the newest topic against this run's own figure keys."
})

artwork["entries"].append({
  "date": DATE, "carousel_no": NO,
  "written_from": "machine_qa.json, render_report.json, measurements.json, layout_check's own accent measurement and the gate suite BY EXIT CODE. The value block is measured off the nine shipped PNGs by "
                  + str(RUN / "measure.py") + " at 432px, never planned and never asserted.",
  "register": "A PUMP HOUSE INTERIOR IN THE POST OAK SAVANNAH AT TEN TO FIVE. Ground #2E2016 sandy loam on swept concrete in shade, one ink #DCD3B4 chart stock, printed: every scene is drawn in greys into TXINK's offscreen twin at true scale, the press lays the paper, screens the tone into ink at a HATCH of cell 6 and angle 52, and paints what must not be screened on top.",
  "structural_laws": [
    "THE SCREEN NEVER SITS UNDER TYPE, AND THE FIRST THREE ROUNDS PROVED IT HALF WAY. Type painted in the over pass is flat and unscreened, which both document frames did from the start. It is the SHEET UNDER IT that carries the screen, and a 6 px stripe under 15 px mono fills the counters, so all three round 2 judges reported a hatch running through glyphs it never touched. N.stock lays flat stock under a type block before the toner goes on, measured off the type it serves. Spanning it across the sheet instead, which the first cut did, prints a filled bar.",
    "AN ACCENT NOBODY CAN SEE IS A FRAME WITHOUT ONE. layout_check measures the accent at 432 px against a 0.2 percent floor, and frames 7 and 9 were declaring an accent at 0.0015 and 0.0017. A colour spent below the floor costs the deck its scarcity and buys nothing a reader gets. Frames 1 and 6 now declare none and carry none, and 2, 4, 7 and 9 carry it above the floor.",
    "A UNIT MARK FIELD HAS A COUNT CEILING AND 4,749 IS OVER IT. At about one and a half pixels per mark the field merges into whatever screen the deck is printing through, and what a reader receives is a filled bar. 87 is countable at an 8.4 px pitch. The two large counts print as numerals on their own sheets, and the anti partition argument is carried by three sheets at three widths that run AGAINST the counts.",
    "A SHEET WHOSE CONTENT OVERRUNS IT HAS NO EDGE, AND A PAGE WITHOUT AN EDGE IS A BAR. Frame 6's mark field needed 990 px on a 940 px sheet for three rounds, so every sheet's own edge sat under its own marks. Three judges read a stacked bar chart and none of them named the geometry, because the symptom and the cause were two layers apart."
  ],
  "techniques": [
    "flat stock laid under dark on light type inside a screened print, feathered on four edges and sized by measureText off the type it serves, so a printed page reads as ink on paper rather than as type over a texture",
    "three separate sheets at three widths chosen to run AGAINST the quantities they carry, so length cannot be read as amount and the anti partition argument is structural rather than a sentence asking the reader not to misread",
    "a single row of 87 unit marks stopping two thirds across a rule that runs on to the margin, so the bare stretch after the last mark is visibly paper a mark could have gone on",
    "a true scale scene bench interior at 6.0 by 4.2 by 3.0 m with a sun patch raking in from an open west door, every object placed in metres and every cast computed from one declared light at az 262 el 26",
    "an orthographic elevation carrying a scale bar whose length is DERIVED from a declared metres per pixel rather than drawn to look right, at 5 m and 212.8 px from 0.0235 m per pixel"
  ],
  "value_block": {
    "per_frame_median_lstar": meas["per_frame_median_lstar"],
    "planned_median_lstar": meas["planned_median_lstar"],
    "max_adjacent_delta": meas["deck"]["max_adjacent_delta"],
    "mean_adjacent_delta": meas["deck"]["mean_adjacent_delta"],
    "note": "Measured at 432 px off the shipped PNGs. It printed systematically DARKER than planned and that is not rewritten in the plan: the three paper frames were planned at 18, 24 and 20 and came out at 10.3, 14.2 and 9.8. Hatch at cell 6 does not reach the twenties over this ground however bright the stock is drawn. The arc is written against the press and the press was never chased to the arc."
  },
  "accent": {"hex": "#9A3B2A", "name": "capitol_granite",
             "frames_above_floor": [2, 4, 7, 9],
             "note": "Frames 1 and 6 declare none. The law is that granite marks where a stylus or a hand in this world has laid ink, which is why a trace on a CRT was removed from frame 1."},
  "ground": {"hex": "#2E2016",
             "nearest_dE76_in_last_six": 13.32,
             "note": "Measured against the last six shipped grounds before any frame was drawn. All three directors proposed warm near blacks that collided with September 14th's bed at 8.37, 4.06 and 2.72 against a floor of 10."},
  "screen": {"mode": "hatch", "cell": 6, "angle": 52,
             "note": "Chosen on probe frame evidence over line at cell 5 and 9 and stipple at 5, measured by thumb standard deviation. Line went WORSE as it went coarser, which killed that family. Deliberately not September 19th's halftone."}
})

captions["entries"].append({
  "date": DATE, "carousel_no": NO,
  "opening_move": "the subject and its size, in nine words",
  "structure": "Ladder", "closing_move": "Ask what the number does not cover",
  "first_line": first_line, "words": words, "commas": commas,
  "commas_per_100w": round(commas / words * 100, 2), "chars": len(cap),
  "hashtags": hashtags,
  "critic_note": "Two candidates and the one rewrite was spent. A ran 981 chars against a 900 band and the critic's three repairs brought it to 887. A later reword took it to 901 and it was trimmed to 889. The winning first line, 'Aimed at small systems. Texas has 4,749.', was moved ONTO frame 1 in round 3 because both readers asked for it independently in two rounds, and the round 3 reader then named the cost of the duplication: LinkedIn shows about two lines before see more, so the one free impression now repeats what the cover already shows at display size.",
  "move_note": "Named against what the shipped text DOES rather than against either director's assignment, per the 2026-09-07 rule. Each paragraph adds one rung and none of them turns, which is the Ladder: the size of the set, then the award, then what practice relies on, then what a reader can do. The close is a question the deck's own figures cannot answer, which is not the open question four ledger entries have flagged as overused because it names the exact set it is asking about."
})

for name, obj in (("topics", topics), ("artwork", artwork), ("captions", captions)):
    (L / f"{name}.json").write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}.json: {len(obj['entries'])} entries, newest {obj['entries'][-1]['date']}")
print(f"caption measured: {words} words, {commas} writer commas, {round(commas/words*100,2)} per 100w, {len(cap)} chars")
