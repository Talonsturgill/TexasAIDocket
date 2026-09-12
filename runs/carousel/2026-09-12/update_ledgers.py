#!/usr/bin/env python3
"""update_ledgers.py — append carousel no. 22's three variety-ledger entries.

WHY IT IS A SCRIPT RATHER THAN THREE HAND EDITS. Every figure in the artwork entry's `value`
block is MEASURED, off `measurements.json`, which is itself measured off the nine shipped PNGs.
A hand edit is where a planned number gets written down as a measured one, and the artwork
ledger is the file the light-deck cap is counted from, so a wrong number there silently changes
what the NEXT deck is allowed to be.

The derived windows at the top of captions.json are rewritten here too, from the entries
themselves, because they were hand-maintained until 2026-09-10 and had drifted. The critic on
this run found them still lagging by one entry and said so.

    python3 out/2026-09-12/update_ledgers.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent
DATE = "2026-09-12"
NO = 22


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def save(p: Path, d) -> None:
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def entries(d):
    return d["entries"] if isinstance(d, dict) and "entries" in d else d


def main() -> int:
    meas = load(RUN / "measurements.json")
    caption = (RUN / "caption.txt").read_text(encoding="utf-8").rstrip("\n")
    per = [meas["frames"][f"slide-{i:02d}"]["median_L"] for i in range(1, 10)]
    deck_L = meas["deck_median_L"]
    dark_i = min(range(9), key=lambda i: per[i])
    light_i = max(range(9), key=lambda i: per[i])

    words = len(caption.split())
    commas = caption.count(",")
    chars = len(caption)

    # ------------------------------------------------------------------ topics
    tp = ROOT / "ledger/carousel/topics.json"
    td = load(tp)
    te = entries(td)
    if not any(e.get("date") == DATE for e in te):
        te.append({
            "date": DATE,
            "carousel_no": NO,
            "docket_item": "tx-2026-0131",
            "topic": ("Texas State University's Ingram School of Engineering method for pavement "
                      "condition assessment, now in a second phase the university describes as "
                      "closer to statewide deployment with pixel-level detection of pavement "
                      "damage. TxDOT funds it and donated the mobile research van the imagery "
                      "comes off"),
            "angle": ("the judgement left the shoulder, and the same team's own peer reviewed "
                      "paper puts it back in a human hand. The deck builds one direction for six "
                      "frames and turns on c17, which says the precision of the technology often "
                      "leads to inaccuracies that must be verified by pavement engineers. The "
                      "record's own pavement condition score, where 70 or above is good or "
                      "better, is what aims the repair money either way"),
            "entities": [
                "Texas State University",
                "Ingram School of Engineering",
                "Texas Department of Transportation",
                "Texas Transportation Commission",
                "Feng Wang",
                "Jelena Tesic",
                "Sensors",
                "Mathematics",
            ],
            "entities_note": ("Written from claims.json rather than from memory. Every name "
                              "appears in a fetched quote. The record names San Marcos nowhere "
                              "in the quotes this deck rests on, so no frame draws a locator and "
                              "the only Texas place printed anywhere is Austin, on the "
                              "commission's own calendar."),
            "keywords": [
                "pavement condition assessment",
                "pavement condition score",
                "sampled portion",
                "pixel-level detection",
                "2D/3D pavement laser scanner",
                "mobile research van",
                "thin cracks",
                "F1",
                "verified by pavement engineers",
                "lane miles",
            ],
            "prose_note": ("The deck prints 28 verified claims' worth of ground and cites 19 of "
                           "them across the nine frames. Nine scout findings were refused, "
                           "including a vehicle-interaction count that no fetched page defines "
                           "and a TRB record set whose host disallows this client."),
        })
        save(tp, td)
        print(f"topics: appended {DATE}")

    # ----------------------------------------------------------------- artwork
    ap = ROOT / "ledger/carousel/artwork.json"
    ad = load(ap)
    ae = entries(ad)
    if not any(e.get("date") == DATE for e in ae):
        ae.append({
            "date": DATE,
            "carousel_no": NO,
            "written_from": ("machine_qa.json, render_report.json, measurements.json, "
                             "layout_check, bespoke_check, coherence_check, craft_floor and the "
                             "gates' exit codes. The value block is MEASURED off the nine "
                             "shipped PNGs at 432 px feed width by measure.py, never planned and "
                             "never asserted."),
            "register": ("CALICHE INK ON HOT MIX, at the end of a working day in September, sun "
                         "at azimuth -58 and elevation 18. The page IS the asphalt at #161310 "
                         "and the ink is the shoulder stone at #E4D8C3, so the type is cut out "
                         "of the road rather than printed on paper laid over it. The accent is "
                         "capitol granite #9A3B2A and it means a person."),
            "structural_laws": [
                ("THE ACCENT MEANS A PERSON AND MEANS NOTHING ELSE. Frames 1, 3, 5 and 7 carry "
                 "it and frames 2, 4, 6, 8 and 9 carry none. measure.py counted exactly those "
                 "four at or above a tenth of a percent. Frame 9's absence is the load bearing "
                 "one, because no claim puts this decision in a room with a named decider."),
                ("THE REGISTER INVERTED AT FRAME ONE, NOT AT ROUND THREE. The plan opened on a "
                 "paper register, the first frame rendered clean and measured a median L* of "
                 "91.5 against the cap's threshold of 60.0, and no amount of extra ink could "
                 "have moved a median that is counting the paper between the strokes. Ground and "
                 "ink were swapped, the same twin greys and the same drawing came back at 6.1."),
                ("ONE SCREEN PER LAYOUT. Halftone at cell 8 and 9 on the two full bleeds and the "
                 "type frame, hatch at cell 6 and 7 on the vehicle and the interior, stipple at "
                 "cell 5 on the two surfaces, line at cell 4 and 5 on the plan and the document. "
                 "bespoke_check reads median pairwise similarity 0.29 over 36 pairs."),
                ("EVERY OBJECT IS PLACED IN METRES ON A DECLARED CAMERA. The van, the semi, the "
                 "desk, the figures and the letter bodies all come out of TXSCENE at true scale, "
                 "so frame 3's person at 198 px against a van at 303 px is a solved comparison "
                 "rather than two sizes that looked right."),
            ],
            "techniques": [
                "TXINK halftone, hatch, stipple and line screens, one per layout",
                "TXSCENE at standing, seated and detail eye heights with one declared light",
                "TXFIG figures and TXOBJ catalogue objects, plus two sprites built in metres",
                "a two part contact shadow under every wheel and castor",
                "a lit lip on every crack, which is what a depth map sees and a photograph does not",
                "DOM type with a CSS shadow-stack extrusion on the type-as-object frame",
            ],
            "palette": {
                "ground": "#161310",
                "ink": "#E4D8C3",
                "dek": "#CFC0A4",
                "furniture": "#96876E",
                "accent": "#9A3B2A",
                "note": ("Measured by measure_palette.py against the 81 hexes of the last eight "
                         "decks, where a random colour's nearest neighbour is p10 9.03 and "
                         "median 27.17. The accent comes back CLEAR at dE 17.06 and the "
                         "furniture is closest at 11.50. Contrast against the ground, measured, "
                         "hook 13.14 to 1, dek 10.34, furniture 5.28. The accent is 2.67 to 1 "
                         "and never carries type, because a mark is not a word."),
            },
            "value": {
                "per_slide_median_L": per,
                "deck_median_L": deck_L,
                "darkest_frame": {"slide": dark_i + 1, "L": per[dark_i]},
                "brightest_frame": {"slide": light_i + 1, "L": per[light_i]},
                "light_cap_note": ("LIGHT_L is 60.0 and this deck measures %.1f, so it does not "
                                   "add to the light count. The window held 2 in 8 against a cap "
                                   "of 1 before this run, one of them under a named waiver, and "
                                   "the ledger required this deck to be dark." % deck_L),
                "planned_vs_measured": ("The register section planned a floor to keep rather "
                                        "than a ceiling to stay under, after the paper register "
                                        "was measured and abandoned. Seven frames sit at the "
                                        "page's own 6.1 and the two that lift are the ones "
                                        "carrying a light surface, the document at %.1f and the "
                                        "type frame's concrete at %.1f."
                                        % (per[1], per[5])),
                "measured_on": "the nine shipped PNGs resampled to 432 px feed width, by measure.py",
            },
            "type_skeletons": [
                ("kicker top left, counter top right, claim-id source line bottom left, site "
                 "line read from brand.yaml"),
                ("Fraunces display fitted per headline by TX.fitText, Manrope body, JetBrains "
                 "Mono for every figure and label"),
                ("frame 6 is the exception and says so: its headline is Manrope 800 standing on "
                 "the road as a raised body, which is the one TYPE_AS_OBJECT this deck spends"),
            ],
            "bespoke": ("36 pairs, median pairwise similarity 0.2865, closest pair frames 1 and "
                        "9 at 0.7395, which are deliberately the same road at two hours."),
            "construction": ("Nine frames rendered with zero errors and zero warnings. "
                             "machine_qa verdict WARN with zero fails on all nine. "
                             "layout_check --require clean, craft_floor clean with a deck median "
                             "variance of 3168.6 against a floor of 570.3, coherence_check "
                             "reading load max 61 against a ceiling of 65."),
            "avoid_next": [
                ("The caliche-on-hot-mix register is spent. It is the second dark register in "
                 "three runs and the ledger will be back over the light cap the moment "
                 "2026-09-09 rolls out of the window, so the NEXT deck has room to be light and "
                 "should measure it at frame one rather than plan it."),
                ("A smooth gradient under a coarse halftone BANDS, and the step between two dot "
                 "sizes comes out as an unbroken horizontal contour the full width of the frame. "
                 "qa.py reads it as a rule through the glyph band, correctly. Model falloff with "
                 "discrete marks or with a finer screen."),
                ("A stipple or halftone field on a dark register is mostly GROUND, so it is not "
                 "a mass. layout_check's silhouette measure saw a screened road as dust twice on "
                 "this deck. A frame that needs one readable silhouette needs one flat area."),
                ("Two spans in one headline element means the copy record calls the larger span "
                 "the hook. build_copy.py derives from the largest laid-out node, and this run "
                 "shipped a first draft whose frame 6 hook was recorded as AND COSTLY."),
            ],
            "panel": "written by the scoring phase",
        })
        save(ap, ad)
        print(f"artwork: appended {DATE}")

    # ---------------------------------------------------------------- captions
    cp = ROOT / "ledger/carousel/captions.json"
    cd = load(cp)
    ce = entries(cd)
    if not any(e.get("date") == DATE for e in ce):
        ce.append({
            "date": DATE,
            "carousel_no": NO,
            "opening_move": "the plain question",
            "structure": "Ladder",
            "closing_move": "Name what happens next and when",
            "first_line": caption.split("\n")[0],
            "words": words,
            "commas": commas,
            "commas_per_100w": round(commas / words * 100, 2) if words else 0.0,
            "chars": chars,
            "hashtags": ["#TxDOT", "#TexasStateUniversity", "#PavementConditionScore"],
            "critic_note": ("Candidate A was refused on three claim failures in one paragraph, a "
                            "scanner riding on the van that c5 lists as a separate investment, a "
                            "definition of statewide no claim carries, and a sentence that "
                            "inverts c15 by making a section mean the sample inside it. B was "
                            "taken with the one rewrite, which restored c23's closed-session "
                            "exception and fixed a pronoun reaching two sentences back for the "
                            "70. The showrunner then corrected the deck summary line, which the "
                            "critic had written without having seen the frames."),
            "move_note": ("The plain question was the right door because this story's whole "
                          "dispute is a classification boundary, a crack against a stain, and "
                          "the ladder was right because the record hands over four rungs that "
                          "stand on each other in physical order."),
        })
        # the derived windows, rewritten from the entries rather than maintained by hand
        if isinstance(cd, dict):
            # THE WINDOWS EXCLUDE THE NEWEST ENTRY. ledger_check re-derives them from the
            # entries BEFORE the newest date, because the list's job is to tell the NEXT run
            # what is off the menu and today's own move is off it by definition. Including it
            # made every one of the three lists disagree with its own file.
            prior = [e for e in ce if e.get("date") < DATE]
            cd["opening_moves_recent"] = [e["opening_move"] for e in prior[-6:]]
            cd["structures_recent"] = [e["structure"] for e in prior[-3:]]
            cd["closing_moves_recent"] = [e["closing_move"] for e in prior[-1:]]
        save(cp, cd)
        print(f"captions: appended {DATE}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
