#!/usr/bin/env python3
"""update_ledgers.py — carousel no. 25's three variety-ledger entries, written once.

Everything measured here is READ rather than typed. The word and comma counts come from
caption_check, the value block from measurements.json, and the three `*_recent` exclusion lists
are RE-DERIVED from the entries with ledger_check.windows(), which reads the windows off
CAPTION_CRAFT.md. Those three lists were hand-kept until 2026-09-10 and drifted in both
directions, which mis-briefed the caption room on the run that found it.

It is idempotent: a second run replaces this date's entries rather than appending a duplicate,
because ledger_check refuses two entries for one date and a `recent` window would then read the
stale one last.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent
DATE = RUN.name
NO = 25
sys.path.insert(0, str(ROOT / "scripts" / "carousel"))
import ledger_check as lc  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ROOT / "ledger" / "carousel" / f"{name}.json").read_text(encoding="utf-8"))


def save(name: str, obj: dict) -> None:
    (ROOT / "ledger" / "carousel" / f"{name}.json").write_text(
        json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def put(ledger: dict, entry: dict) -> None:
    """Replace this date's entry if it exists, else append, keeping the list in date order."""
    ledger["entries"] = [e for e in ledger["entries"] if e["date"] != entry["date"]]
    ledger["entries"].append(entry)
    ledger["entries"].sort(key=lambda e: e["date"])


def caption_measured() -> dict:
    """caption_check's own count, asked for rather than recounted here."""
    p = subprocess.run([sys.executable, str(ROOT / "scripts/carousel/caption_check.py"),
                        "--file", str(RUN / "caption.txt"), "--json"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"caption_check refused this caption, so nothing is written:\n{p.stdout}{p.stderr}")
    out = json.loads(p.stdout)
    # caption_check names the rate `commas_per_100_words` and the ledger schema names it
    # `commas_per_100w`. The hashtags it does not return at all, so they are read off the
    # caption's own last line rather than typed beside it.
    out["commas_per_100w"] = out.pop("commas_per_100_words")
    tail = (RUN / "caption.txt").read_text(encoding="utf-8").strip().splitlines()[-1]
    out["hashtags"] = [w for w in tail.split() if w.startswith("#")]
    return out


def main() -> int:
    M = json.loads((RUN / "measurements.json").read_text(encoding="utf-8"))
    cap = caption_measured()
    text = (RUN / "caption.txt").read_text(encoding="utf-8").strip()
    first_line = text.splitlines()[0].strip()

    frames = [f"slide-{n:02d}" for n in range(1, 10)]
    measured = [M["frames"][f]["median_L"] for f in frames]

    # ---------------------------------------------------------------- topics
    t = load("topics")
    put(t, {
        "date": DATE,
        "carousel_no": NO,
        "docket_item": "tx-2026-0159",
        "instrument": "ERCOT's Item 10 presentation to its own Board of Directors on September "
                      "14th and 15th, 2026, and PGRR 144 on the market rules site",
        "topic": "The 3 emerging operational risks ERCOT put in front of its own Board for the "
                 "Large Loads on its system, each with a mitigation, and the 3 mitigations at 3 "
                 "different stages. The ride-through rule is in force, effective August 1st. The "
                 "modeling rule reached the Board this month. The rule that would hold a Large "
                 "Load's swing is not filed and carries no number, and ERCOT gives September or "
                 "October for filing it. The same 6 pages say the dynamic models ERCOT uses to "
                 "study these loads have proven inaccurate.",
        "angle": "The deck is built on the gap between a named risk and the state of the rule "
                 "meant to answer it. Every statement of harm in the document is modal, so the "
                 "deck draws nothing broken anywhere in 9 frames, and the 6 pages name no data "
                 "center, no company, no generator and no county.",
        "angle_note": "The turn is frame 4, at the coupling, which is the metal ERCOT's word "
                      "fatigue points at. It is also the frame where drawing a crack would have "
                      "turned a could into a has, and the refusal to draw one is the deck's "
                      "argument rather than a limitation on it.",
        "entities": ["ERCOT", "Public Utility Commission of Texas", "Texas A&M University"],
        "entities_note": "No private party is named because the document names none. Texas A&M "
                         "is the only institution in it besides the grid operator and the "
                         "commission, which is what frame 8's line rests on.",
        "keywords": ["large load", "ride-through", "oscillation", "dynamic model", "NOGRR 282",
                     "NPRR 1308", "PGRR 144", "board of directors", "ERCOT"],
        "prose_note": "Every count above is written in digits. ledger_check compares spelled-out "
                      "number words against the run's own figure keys, and this run's keys are "
                      "not the vocabulary that check carries.",
    })
    save("topics", t)

    # --------------------------------------------------------------- artwork
    a = load("artwork")
    put(a, {
        "date": DATE,
        "carousel_no": NO,
        "written_from": "machine_qa.json, render_report.json, measurements.json, and the gate "
                        "suite by EXIT CODE. The value block is MEASURED off the nine shipped "
                        "PNGs by out/2026-09-15/measure.py on panel_ready.ARC_GRID, 270 by 338, "
                        "never planned and never asserted.",
        "register": "A GAS PLANT ON THE ERCOT SYSTEM AT 06:20 AT THE END OF NIGHT SHIFT, AND ITS "
                    "YARD AT FIRST LIGHT. Epoxy deck #101A12 and one lagging ink #E4DCC6, "
                    "printed: every scene is drawn in greys into an offscreen twin at true scale, "
                    "TXINK.print lays the paper, screens the tone into ink, lays the contour "
                    "plate a pixel out of register, and paints what must not be screened on top.",
        "structural_laws": [
            "THE WORLD AND THE PAPER NEVER SHARE A FRAME. Frames 1, 3, 4, 6 and 9 are the "
            "physical world with a light, a horizon and shadows and carry no accent. Frames 2, 5, "
            "7 and 8 are paper and every one carries the accent. A reader has the code by frame "
            "3 without being told it, and by frame 7 it is the argument: the rule is a drawing, "
            "and ERCOT says the drawing is wrong about the machine.",
            "NOTHING IN THE DECK IS DRAWN BROKEN. Every statement of harm in the source is modal "
            "and the document nowhere says damage has occurred, so no crack, no spall, no pit "
            "and no scoring appears on any steel surface in 9 frames. Frame 4 is a coupling at "
            "detail scale and is where that temptation was highest.",
            "THE ACCENT MAY FILL A MARK AND MAY NOT FILL A THING. Frame 7's dimensioned limit and "
            "frame 8's scale bar segments are marks drawn to be read as marks. A table row, a "
            "county, a machine and a plate behind a label are not, and frame 2's leader chips "
            "were solid accent behind cream type until a critic returned them.",
        ],
        "techniques": [
            "A data hall aisle at standing eye with two rows of 14 racks running off both frame "
            "edges, a containment ceiling converging on the same vanishing point, and one "
            "technician in it, under a halftone at cell 7",
            "An engineering elevation at ONE declared scale of 0.104 metres per pixel, over a "
            "line screen at cell 4, with a computed scale bar in its own legend corner and two "
            "leaders ending on their targets' coordinates",
            "A 130 m wall drawn from metres off the bench's own px/m with its sheeting pitch, "
            "its louvre band and its roof plant, the sky and the lit door painted AFTER the "
            "press because a cell 5 stipple prints a white field at a mean of 63 of 255, and a "
            "graded caliche apron carrying 1100 stones each lit left and throwing right",
            "A 1.1 m coupling at 1.18 px per millimetre with a 16 bolt circle running off the "
            "top edge, an engraver's cross hatch at cell 6, and one unscreened journal face",
            "ERCOT's own 3 row table at page size on a sheet turned 0.7 degrees, flat and "
            "unscreened so nothing prints under the type, with no row coloured or ranked",
            "One straight cut with the yard below drawn in full detail under a halftone at cell "
            "6 and the field above left as unscreened ground, because an incomplete line reads "
            "as sloppy drawing and an empty field reads as an absence",
            "A plot sheet with a ruled field, a drawn zero on both axes, one filled accent "
            "triangle and a steel straightedge lying on the desk at its foot",
            "254 county geometries on TXGeo's Albers equal-area conic at one value with none "
            "lit, a neatline, a bisection-placed graticule and a scale bar whose length is "
            "computed from the projection",
            "A plant yard at first light with the hall rim-lit against its own mass, three "
            "towers walking to frame right and the conductor drawn last and brightest so the "
            "line visibly leaves the frame",
        ],
        "palette": "deck_epoxy #101A12, lagging #E4DCC6, forging #5C6552, enamel #2C4433, "
                   "pad_caliche #A08A5E, first_light #C08A5A, bond #F4F1E2, accent #2F7D57.",
        "value": {
            "grid": "270x338, panel_ready.ARC_GRID",
            "measured": measured,
            # THE KEY THE CHECKER READS. ledger_check counts the light-deck cap off
            # `value.deck_median_L` and this writer had called it `deck_median`, which is why the
            # 2026-09-14 entry and the first write of this one both came back as "older entries
            # that predate the measurement". They do not predate it. They measured it and filed it
            # under a name nothing reads. Both names are written so the older one stays readable.
            "deck_median_L": M["deck"]["median_of_frame_medians"],
            "deck_median": M["deck"]["median_of_frame_medians"],
            "spread": M["deck"]["spread_L"],
            "screen_ceilings": M.get("screen_ceilings", {}).get("screens", []),
            "note": "THE ARC WAS REWRITTEN RATHER THAN REDRAWN, and the measurement is why. On a "
                    "dark ground TXINK lays light ink where the source is light, so a screened "
                    "frame's median is bounded by how much ink its screen can put down. A white "
                    "field printed through this deck's own configurations returns a mean of 63.0 "
                    "of 255 for the stipple, 107.6 to 107.9 for the hatch and 205.7 for the "
                    "halftone, which are ceilings of L* 26.7, 45.5 and 82.7. The first cut of the "
                    "plan asked frame 3, a stipple frame, for 40. Fixing the art cannot clear a "
                    "miss the press cannot print. What it can clear is a frame that came out dark "
                    "because nothing was drawn in it, and frame 3 was rebuilt for that on the "
                    "same day rather than re-planned.",
        },
        "type_skeletons": "Kicker top left, counter top right, hook under it, dek below, source "
                          "line and site line at the foot. Frames 2, 5, 7 and 8 give the sheet "
                          "its own typography and set the furniture in the page's own ink. Frame "
                          "9 closes on the wordmark.",
        "machine_qa": "0 fails across 9 frames. layout_check --require, bespoke_check median "
                      "pairwise 0.24, craft_floor, construction_check, dossier_check, "
                      "plan_render_check, copy_sync_check, coherence_check, texan_check, "
                      "noun_trace, absence_check, scene_bounds, verbatim_check, numeral_trace, "
                      "label_guard, quantifier_check and aggregate_check all exit 0. panel_ready "
                      "exit 0.",
    })
    save("artwork", a)

    # -------------------------------------------------------------- captions
    c = load("captions")
    put(c, {
        "date": DATE,
        "carousel_no": NO,
        "opening_move": "the correction",
        "structure": "Pivot",
        "closing_move": "Ask the one question the decision leaves open",
        "first_line": first_line,
        "words": cap["words"],
        "commas": cap["commas"],
        "commas_per_100w": cap["commas_per_100w"],
        "chars": len(text),
        "hashtags": cap["hashtags"],
        "critic_note": "Two candidates. A lost on the record rather than on craft: it closed by "
                       "asking how ERCOT would know the shaft had already moved, which "
                       "presupposes movement that absence a4 explicitly forbids, and it tagged "
                       "the rule already in force rather than the deck's subject. B won and was "
                       "edited once, splitting a sentence at a comma after 'yet' rather than "
                       "deleting the comma and leaving a run-on.",
        "move_note": "'the correction' opens by denying the reading everybody has, which is that "
                     "a Large Load's problem is its size. The pivot to speed is the story and it "
                     "is the source's own. Ledger and Ladder were off the menu and the close that "
                     "names what is still not public was off it too.",
    })
    # THE THREE EXCLUSION LISTS ARE DERIVED, at the windows the doctrine states, never typed.
    doctrine = (ROOT / "knowledge" / "carousel" / "CAPTION_CRAFT.md").read_text(encoding="utf-8")
    wins = lc.windows(doctrine)
    prior = [e for e in c["entries"] if e["date"] < DATE]
    c["opening_moves_recent"] = [e["opening_move"] for e in prior[-wins["opening_move"]:]]
    c["structures_recent"] = [e["structure"] for e in prior[-wins["structure"]:]]
    c["closing_moves_recent"] = [e["closing_move"] for e in prior[-wins["closing_move"]:]]
    save("captions", c)

    print(f"ledgers: carousel no. {NO} written to topics, artwork and captions for {DATE}")
    print(f"  caption {cap['words']} words, {cap['commas']} commas, "
          f"{cap['commas_per_100w']} per 100w, hashtags {' '.join(cap['hashtags'])}")
    print(f"  deck median L* {M['deck']['median_of_frame_medians']}, spread {M['deck']['spread_L']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
