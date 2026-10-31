#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-31, carousel no. 64. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "out" else HERE.parents[2]   # out/<date>/ or runs/carousel/<date>/
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-31", 64
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#B4664F"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0048", "related_items": ["tx-2026-0180", "tx-2026-0030", "tx-2026-0075"],
 "instrument": "City of League City Legistar records (matters, histories and vote rows for Resolutions 2022-185, 2023-197 and 2026-185 and Ordinance 2026-27), Harris County's sample ballot and elections page, the Texas Tribune of October 30th, Houston Public Media via KEDT, and the Census Bureau's 2020 place gazetteer, all fetched October 31st, 2026.",
 "topic": "League City votes on Proposition A on November 3rd, a special election the council ordered on August 11th and amended to call nonbinding. On October 13th the council passed a resolution directing removal of the city's fixed Flock license plate reader cameras if a majority rejects their continued use, and the mayor told the council the cameras would be bagged after certification. The Tribune reported it is the first such vote in Texas, with Kyle and Laredo planning theirs for May.",
 "angle": "Road paint at a single corner in the lastLight world: a car with its lamps on at a crosswalk, tally stripes of the leased cameras, a gutter pan ruler setting the lease's ceiling beside the Tribune's count, a field of raised markers for the agencies that can search, a crosswalk for each roll call with a bare saw cut among them, a resident on the terracotta warning panel, the crosswalk at paint height, a kerb strip of saw cut hours, and Texas as an asphalt slab with League City's counties in terracotta.",
 "angle_note": "Every frame is drawn to illustrate. One stripe, marker, bar or groove is one camera, agency, recorded vote or hour, each counted from the record by compute.py. No camera is drawn.",
 "entities": ["City of League City", "League City City Council", "Flock Safety", "Flock Group", "Harris County Elections", "Texas Tribune", "Houston Public Media"],
 "places": ["League City", "Galveston County", "Harris County", "Kyle", "Laredo"],
 "what_was_refused": "any claim that the cameras will come down (the vote is pending), the Flock transparency portal (a bot challenge, read only through the Tribune), leaguecitytx.gov (robots did not answer), the Legistar agenda packets on legistar1.granicus.com, and Galveston County's polling hours (not in the record).",
 "keywords": ["League City", "Proposition A", "Flock Safety", "license plate readers", "special election", "Legistar", "surveillance technology", "Galveston County"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world, staged, with two TXBENCH material reliefs. Chassis assets/js/deck/2026-10-31-roadpaint.js: thermo_bar, continental_crosswalk, curb_ramp_warning, raised_marker and gutter_rule, fresh and worn thermoplastic on asphalt, concrete, and dusk_ember terracotta as the one accent for the public.",
 "structural_laws": [
  "A CAMERA AT PAINT HEIGHT OVER A SIDEWALK SEES THE SIDEWALK. Frame 7's lower third was the slab's top face, not a bar, until the eye moved into the road off the kerb.",
  "A LIGHT THAT LIGHTS THE GROUND MERGES A COUNT. A spot over the crosswalks lifted the asphalt with the paint and the GRID came apart into three pieces; emissive paint kept the gaps dark.",
  "A RAISED INLAY UNDER A BEVELLED SLAB TOP IS HIDDEN. The county fills sat below the slab's bevel until they stood proud of it.",
  "A BIGGER PIN IS A SECOND SCALE. On a map whose dek says Census points, a wider stud read as a proportional symbol; colour and a collar carry emphasis without one.",
  "A ZOOM ON A LOW PITCHED CAMERA LOSES THE SKY. Narrowing the lens on frame 3 would have put the horizon out of frame, which print_ban refuses."],
 "techniques": [
  "the kit crossover head on at a stop bar, lamps lit in their housings, throwing light onto an eight bar crosswalk",
  "a plan relief of tally stripes, worn for the first lease and fresh for the cameras the second added",
  "a concrete gutter pan with a saw cut ruler and two inlaid bars, the lease's ceiling beside the Tribune's count",
  "a staggered field of raised pavement markers with six brass markers for the officers",
  "three crosswalks on one lane, seven worn, seven fresh with one bare saw cut, and eight fresh",
  "a resident on a terracotta curb ramp warning panel at the kerb, the crosswalk running away under a streetlight's cast",
  "the crosswalk at paint height from just off the kerb, chamfers lit over black gaps",
  "a kerb strip relief of saw cut grooves in rows of a day, a terracotta start bar at the head",
  "Texas extruded as an asphalt slab with county lines, League City's counties in terracotta and three Census studs"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight deck."},
 "accent": {"hex": "#B4664F", "name": "dusk_ember terracotta, the public", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The warning panel where the resident stands, the start bar of the hours, and League City's counties."},
 "ground": {"hex": "#0A090D", "note": "The lastLight world's dark sky and the flat frames' dark field."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the correction", "structure": "Two columns",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens by correcting what nonbinding suggests, sets the ballot's word against the council's own record in two columns, and closes on the certification date nobody has named.",
 "move_note": "Opens on what a nonbinding no would still reach, then the ballot and the hours, then the October 13th resolution and the mayor's words, and closes asking when the count will be certified."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
