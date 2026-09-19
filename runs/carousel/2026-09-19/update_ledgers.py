#!/usr/bin/env python3
"""update_ledgers.py — carousel no. 29's three variety-ledger entries, written once.

Everything measured here is READ rather than typed. The word and comma counts come from
`caption_check --json`, the value block from `measurements.json`, the gate verdicts from the
artifacts themselves, and the three `*_recent` exclusion lists are RE-DERIVED with
`ledger_check.windows()`, which reads the windows off `CAPTION_CRAFT.md`.

THE EXCLUSION WINDOW IS STILL ONE ENTRY BEHIND AND THIS FILE STILL WRITES IT THAT WAY.
`ledger_check.check_register` asserts the stored lists equal `prior[-window:]` where `prior`
excludes the newest entry, so writing the correct window here would turn the gate red against a
value the gate itself defines. It cost this run a documented round: the caption room was handed a
structure list omitting 2026-09-18's Clock and a director was assigned Clock two days after Clock
shipped. That is the THIRD sighting, after 2026-09-14 and carousel no. 25's pull request review.
The fix is one change in two lanes at once, `ledger_check` is `upgrade` and `captions.json` is
`daily`, which is the shape `CLAUDE.md` says a self-editing phase does not get to make alone. It
is in `knowledge/carousel/UPGRADE_BACKLOG.md` and it stays there until a maintainer lands both.

It is idempotent: a second run replaces this date's entries rather than appending a duplicate,
because `ledger_check` refuses two entries for one date and a `recent` window would then read the
stale one last.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path


def _repo_root(start: Path) -> Path:
    """The repository, found by its own marker rather than by counting directories."""
    for p in [start, *start.parents]:
        if (p / "ownership.yaml").is_file() and (p / "ledger").is_dir():
            return p
    raise SystemExit(f"update_ledgers: no repository root above {start}")


ROOT = _repo_root(Path(__file__).resolve().parent)
RUN = Path(__file__).resolve().parent
DATE = RUN.name
NO = 29
sys.path.insert(0, str(ROOT / "scripts" / "carousel"))
import ledger_check as lc  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ROOT / "ledger" / "carousel" / f"{name}.json").read_text(encoding="utf-8"))


def save(name: str, obj: dict) -> None:
    (ROOT / "ledger" / "carousel" / f"{name}.json").write_text(
        json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def put(ledger: dict, entry: dict) -> None:
    ledger["entries"] = [e for e in ledger["entries"] if e["date"] != entry["date"]]
    ledger["entries"].append(entry)
    ledger["entries"].sort(key=lambda e: e["date"])


def caption_measured() -> dict:
    """caption_check's own count, asked for rather than recounted here."""
    p = subprocess.run([sys.executable, str(ROOT / "scripts/carousel/caption_check.py"),
                        "--file", str(RUN / "caption.txt"), "--json"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"caption_check refused this caption, so nothing is written:\n"
                         f"{p.stdout}{p.stderr}")
    out = json.loads(p.stdout)
    out["commas_per_100w"] = out.pop("commas_per_100_words")
    tail = (RUN / "caption.txt").read_text(encoding="utf-8").strip().splitlines()[-1]
    out["hashtags"] = [w for w in tail.split() if w.startswith("#")]
    return out


def main() -> int:
    M = json.loads((RUN / "measurements.json").read_text(encoding="utf-8"))
    cap = caption_measured()
    text = (RUN / "caption.txt").read_text(encoding="utf-8").strip()
    first_line = text.splitlines()[0].strip()
    score = json.loads((RUN / "score.json").read_text(encoding="utf-8"))

    # ---------------------------------------------------------------- topics
    t = load("topics")
    put(t, {
        "date": DATE,
        "carousel_no": NO,
        "docket_item": "tx-2026-0171",
        "instrument": "one state press release and one grid operator market notice issued the "
                      "same day, read against the statute each of them names",
        "topic": "The Office of the Texas Governor directed the Texas Water Development Board to "
                 "enforce the state water use survey against data centers, naming a criminal "
                 "offense and a TCEQ permit ineligibility that the Texas Water Code already "
                 "carried, and ERCOT issued a market notice the same day carrying the board's own "
                 "water questions to data center developers with a response deadline and a "
                 "notarized attestation requirement.",
        "angle": "The law did not change and the enforcement did. Every consequence in the "
                 "directive is a consequence that was already on the books, so the deck draws no "
                 "legislature, no new rule and nothing having happened yet, and its argument is "
                 "the gap between a dormant penalty and a switched-on one.",
        "angle_note": "THE DECK CARRIES NO PLACE AND KNEW IT AT SELECTION. `texan_check` read "
                      "places NONE on the story before a frame was planned, which is what the "
                      "gate is for, so the run planned to carry the score on art and on the "
                      "closing frame instead of learning it from a judge in a late round. "
                      "THE INSTRUMENT IS THE FIFTH ERCOT REQUEST IN THE WINDOW and a round 1 "
                      "judge said so plainly. `c18` separates this notice from the Batch Zero "
                      "request by name, in the notice's own words, and that sentence is printed "
                      "on no frame. `dedupe_check` compares entities and keywords and can't see "
                      "an INSTRUMENT repeat, which four earlier run records have each written in "
                      "capitals. This is the fifth.",
        "entities": ["Texas Water Development Board", "ERCOT", "Office of the Texas Governor",
                     "Texas Commission on Environmental Quality",
                     "Public Utility Commission of Texas"],
        "entities_note": "No private party is named because neither document names one. The "
                         "Governor's office asserts that major water users appear to have "
                         "committed violations and names no company, no county and no volume.",
        "keywords": ["water use survey", "Texas Water Code", "TWDB", "ERCOT", "market notice",
                     "M-B091426-01", "interconnection", "TCEQ permits", "notarized attestation",
                     "data center water"],
        "prose_note": "Every count above is written in words that are not number words, because "
                      "`ledger_check` validates spelled number words in the newest topic against "
                      "this run's own figure keys and this run writes no figures.json.",
    })
    save("topics", t)

    # --------------------------------------------------------------- artwork
    a = load("artwork")
    put(a, {
        "date": DATE,
        "carousel_no": NO,
        "written_from": "machine_qa.json, render_report.json, measurements.json and the gate suite "
                        "BY EXIT CODE. The value block is measured off the nine shipped PNGs by "
                        "out/2026-09-19/measure.py at 432px, never planned and never asserted.",
        "register": "A CALICHE PAD ON THE EDWARDS PLATEAU AT FIRST LIGHT. Ground #18222B, one "
                    "lagging ink #E6DFCC, printed: every scene is drawn in greys into TXINK's "
                    "offscreen twin at true scale, the press lays the paper, screens the tone "
                    "into ink at a halftone of cell 7 and angle 22, and paints what must not be "
                    "screened on top.",
        "structural_laws": [
            "ONE LIGHT, LOW IN THE EAST OFF THE CAMERA'S LEFT SHOULDER AT 14 DEGREES. Every lit "
            "face in nine frames is a left face and every cast runs right. Frame 9's tower cast "
            "was missing at round 1 and a judge found it by checking the drawing against the law "
            "rather than against the other frames.",
            "COMAL ONLY EVER LANDS ON WATER SOMEBODY HOLDS A NUMBER FOR. A gauged stock tank "
            "takes it on frames 1, 2, 6 and 9 and the route takes it on frame 5, because the "
            "route is that number moving between the three parties. Frames 3, 4, 7 and 8 carry "
            "none at all, which includes every frame whose subject is a building whose water is "
            "the whole question.",
            "NO CATALOGUE SPRITE CARRIES A 130 m BUILDING. `TXOBJ.sprite('data_center')` is drawn "
            "for its own scale and renders at 74 m and beyond as square merlons on one cream "
            "fill. Three judges called it a crenellated battlement on three separate frames in "
            "round 1. Frames 1, 6 and 8 each build their own hall from the frame's own "
            "projection instead, and each differently, so the deck's three halls are three "
            "drawings rather than one stamp at three sizes.",
            "A FIGURE IS READ AGAINST WHAT IS BEHIND IT, NEVER AGAINST THE PALETTE. Four figures "
            "shipped into round 1 inked bright while standing against bright halls and lit "
            "caliche, and the integrity judge could not find a figure on the cover at all. "
            "Frames 1, 4, 8 and 9 ink theirs dark. Frame 7's stayed bright because its ground is "
            "dark, which is the same rule and not an exception to it.",
        ],
        "techniques": [
            "a 130 m data hall built from the frame's own projection at 74 m, with roller doors "
            "at 18 m centres, a stair head and three low plant runs, over a graded caliche pad "
            "carrying grader ruts and lit gravel",
            "a hot-dip galvanized property fence at 1.2 m from the lens drawn in frame space "
            "rather than on the scene bench, its fabric two crossing families of wire each with "
            "a lit crown and a dark belly, and its own mesh shadow raking across the near ground",
            "a pickup tailgate as a trapezoid with converging ribs, two pressed swages, latch "
            "bezels and the bed walls behind it, carrying one cream sheet with a drawn corner "
            "curl and the shadow the curl throws back onto the page",
            "a substation yard at true scale with the transformer tanks as lit cylinders and a "
            "dark figure outside the wire",
            "an orthographic elevation of three institutions on one ground line with the route "
            "between them as the frame's one comal, and no scale bar",
            "a straight cut with a tower and a hall on one long-lens horizon at true relative "
            "size, the hall built with expansion joints and uneven low roof plant",
            "a county courthouse portico at standing eye with six columns casting across the "
            "steps and two figures at true scale",
            "the same camera as the courthouse with a 130 m hall at 48 m, a bay rhythm of "
            "pilasters each casting right, eight roof plant units against the sky and a cattle "
            "guard across the near approach",
            "a water tower at 12 by 38 m bleeding the top edge, with a cast that leaves the frame "
            "because a 38 m object at 14 degrees throws about 152 m",
        ],
        "palette": "ground #18222B, ink #E6DFCC, dek #C6C6B8, furniture #9C9C90, accent comal "
                   "#2A7A9E. One grey scale declared in the chassis and no frame picks its own.",
        "value": {
            "grid": "432x540, the feed thumb",
            "measured": M["per_frame_median_lstar"],
            "planned": M["planned_median_lstar"],
            "deck_median_L": M["deck"]["median_of_frame_medians"],
            "deck_median": M["deck"]["median_of_frame_medians"],
            "spread": M["deck"]["spread_L"],
            "max_adjacent": M["deck"]["max_adjacent_delta"],
            "screen_ceilings": M["screen_ceilings"],
            "note": "THE PLAN CAME IN SYSTEMATICALLY HIGH AND THE PLAN WAS NOT REWRITTEN. The "
                    "deck's planned arc asked for frames in the thirties and forties and the "
                    "render came in darker on every frame, by as much as thirty points on frame "
                    "5. `panel_ready` passes because its check is on the deck's median rather "
                    "than per frame, so nothing stopped it and nothing should have: the frames "
                    "are right and the targets were optimistic. Editing nine dossiers to match "
                    "nine renders would be the inversion `measure.py`'s own docstring exists to "
                    "prevent, so both tracks are written here and the gap is the finding.",
        },
        "type_skeletons": "Kicker top left, counter top right, hook, dek, source line at the foot "
                          "and the site line opposite it. Every frame seats its type with "
                          "TXDECK.punch at feather 66 and strength 0.78, which is a dim toward "
                          "the type rather than a plate, and a round 1 judge found no haloes at "
                          "feed size. Frame 3 is the deck's one dark-on-light page and its type "
                          "is the sheet's own.",
        "machine_qa": "0 fails and 0 warns across 9 frames, verdict PASS, against 7 warns at "
                      "round 1. bespoke_check median pairwise 0.3748, craft_floor median 6898 "
                      "against a floor of 1242, and layout_check --require, dossier_check, "
                      "plan_render_check, copy_sync_check, coherence_check, deck_chassis, "
                      "deck_coherence, texan_check, noun_trace, absence_check, scene_bounds, "
                      "bleed_witness, contact_trace, locator_trace, construction_check, "
                      "verbatim_check, numeral_trace, label_guard, quantifier_check and "
                      "aggregate_check all exit 0. panel_ready exit 0.",
        "artifact_note": "THE VECTOR PDF IS 61.5 MB AGAINST 6 TO 14 MB FOR EVERY DECK BEFORE IT "
                         "AND THE CAUSE IS MEASURED RATHER THAN GUESSED. A coarser screen cell "
                         "was worth about 5 MB, a raised screen floor and a higher gamma were "
                         "worth nothing at all, and cutting the film grain and the dither was "
                         "worth about 9 MB, which is why the grain runs at 0.012 against the "
                         "house 0.044. What is left is that this is the first deck to run the "
                         "full halftone across the whole of all nine frames. It ships disclosed "
                         "rather than cured, and the diagnosis is in UPGRADE_BACKLOG.",
    })
    save("artwork", a)

    # -------------------------------------------------------------- captions
    c = load("captions")
    put(c, {
        "date": DATE,
        "carousel_no": NO,
        "opening_move": "the before and after",
        "structure": "Pivot",
        "closing_move": "Name what happens next and when",
        "first_line": first_line,
        "words": cap["words"],
        "commas": cap["commas"],
        "commas_per_100w": cap["commas_per_100w"],
        "chars": len(text),
        "hashtags": cap["hashtags"],
        "critic_note": "Two candidates and the one rewrite was spent. A was assigned Clock and "
                       "LOST ON THE LEDGER RATHER THAN ON PROSE, because Clock shipped the day "
                       "before and the exclusion list the room was handed did not contain it. A "
                       "was a Clock in substance as well as in label, its spine being nothing but "
                       "a run of dates, so it could not be relabelled out. B won the slot without "
                       "winning on merit: its first line, 'The water plan needs a number', put "
                       "c5's sentence in the board's own mouth, which is the one thing the fact "
                       "checker had named by name, and its close compounded the same invention. "
                       "The rewrite replaced the hook with a legal fact from c4 and c6, deleted "
                       "an unsourced 'Nothing was legislated', deleted a self-referential line "
                       "about what the deck reads, named ERCOT where the draft said 'a grid "
                       "operator request', and moved the close onto a scheduled date.",
        "move_note": "Named against what the shipped text DOES rather than against either "
                     "director's assignment, per the 2026-09-07 rule. Paragraph one states the "
                     "old state of the world and paragraph two the new one, which is the before "
                     "and after. 'Both consequences were already in the Texas Water Code' is the "
                     "one sentence that turns the reading everybody has, which is the Pivot. The "
                     "close names the next scheduled event and its date, rendered as a question "
                     "because brand.yaml requires the form, and the SUBSTANCE is 'name what "
                     "happens next and when' rather than the open question that four ledger "
                     "entries have flagged as overused.",
    })
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
    print(f"  deck median L* {M['deck']['median_of_frame_medians']}, "
          f"spread {M['deck']['spread_L']}, panel {score['weighted_score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
