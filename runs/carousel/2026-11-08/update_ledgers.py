#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-08, carousel no. 72. Appends one entry to each variety ledger,
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
D, N = "2026-11-08", 72
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#C9B393"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0244", "related_items": [],
 "instrument": "Texas A&M AgriLife Today's release of November 5th, 2026 on the mitochondrial interaction screen and the paper's Europe PMC record and full text (PMC13601606), fetched November 8th, 2026.",
 "topic": "Texas A&M scientists in College Station recast Google DeepMind's AlphaFold-Multimer as a yes or no test for protein interactions and screened every pairing of a curated list of 1123 mitochondrial proteins, 630,003 pairs. At a mean ipTM cutoff of 0.5, which the authors say gives 67% recall at a false discovery rate of about 15% on their test set, the screen kept 2,895 likely interactions, 57% of them in none of the databases checked, and gave 85 uncharacterized proteins their first probable partners. Years of lab work confirmed several in yeast and human cells and mapped copper's route to cytochrome c oxidase. The predictions are free online as MitoMatch.",
 "angle": "A teaching model of a pair of protein chains on a lab bench at last light, then the half matrix of every pair milled into a black plate, the 2,895 likely pairs as a brass tile among tiles of the same area, a hundred bosses above the 0.5 step with fifteen in steel, the brass block of every likely pair split new and known, a rack of 85 tubes, a stack of amber yeast plates with a plate open, and the cover's bench again with the brass block of the list set down beside the model.",
 "angle_note": "Every frame is drawn to illustrate. The models are teaching models, not structures from the paper. A tile's area is computed from the counts. The hundred bosses are a drawing unit for the stated false discovery rate. No count of confirmed pairs is drawn, because the release gives none.",
 "entities": ["Texas A&M AgriLife Research", "Texas A&M University", "Department of Biochemistry and Biophysics", "Google DeepMind", "AlphaFold-Multimer", "MitoMatch", "Texas A&M High Performance Research Computing", "The Welch Foundation"],
 "places": ["College Station"],
 "what_was_refused": "any count of lab-confirmed pairs, any binding strength, any treatment claim, and any figure not in the release or the paper's own text.",
 "keywords": ["Texas A&M", "College Station", "AlphaFold-Multimer", "mitochondria", "protein interactions", "MitoMatch", "AI in research", "ipTM"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "A MIX. Spatial scenes in one dark lab at last light (frames 1, 2, 7, 8 and 9, TXT.interior with the window on the far wall and a warm slot behind the subject) and material reliefs on a black anodised plate (frames 3 to 6, TXBENCH). Chassis assets/js/deck/2026-11-08-plate.js: protein_pair, lab_bench, half_matrix_plate, pair_block, microtube, tube_rack, petri_plate and culture_flask, with brass as the one accent for a likely pair.",
 "structural_laws": [
  "A TYPE WASH THAT FADES PAST THE DEK GREYS THE SUBJECT'S TOP. Four readings blamed the light and the stage fog for grey chain tops until both washes were made to end at the dek.",
  "A WINDOW ON THE CAMERA'S WALL DRAWS A SILL ACROSS THE TYPE. Putting the window on the far wall and the light in a slot behind the subject removed every hard edge behind the headline.",
  "A CELL UNDER A PIXEL ALIASES INTO STRIPES. One protein's band on the plate was drawn at a stated 12 px width, not one true cell.",
  "TXT.CONTACT ON A SMALL TILE SPREADS A BLACK FIELD. On the close it blacked out the whole foreground until it went back to standing on the bench.",
  "A KIT TAPE BAND READS AS A GREY STICKER ON A DISH. The stored plates ship without it."],
 "techniques": [
  "a space-filling teaching model of two protein chains in bone resin and brass on a black plinth",
  "the same two chains apart with the window's slot of light between them",
  "the half matrix of every pair milled into a black plate, one protein's row and column raised",
  "the same terrace ruled into tiles of equal area, one raised in polished brass",
  "a hundred bosses above a milled step at 0.5, eighty five brass and fifteen bead blasted steel",
  "the brass block of every likely pair, the new share bright and the known share in bronze",
  "a rack of 85 milky microtubes backlit at the bench",
  "a tower of inverted yeast plates in amber agar with one plate open on its colonies",
  "the cover's bench again with the brass block of the list set down beside the model"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A dark lab and a black plate."},
 "accent": {"hex": "#C9B393", "name": "brass, a likely pair", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The brass chain on 1 and 9, the brass tile on 4, the brass bosses on 5, the new share on 6, the block on 9."},
 "ground": {"hex": "#0D0E10", "note": "The black epoxy bench and the anodised plate."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens on the copper route the lab work mapped, then zooms out to the screen that pointed at it, the 2,895 of 630,003, the new share and the limits, and closes on the free list and the false discovery rate it carries.",
 "move_note": "From one finding to the whole screen to the list anyone can use, attributed to the paper and the release."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
