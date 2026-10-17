#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-17, carousel no. 53. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-17", 53
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0217", "related_items": ["tx-2026-0151"],
 "instrument": "MD Anderson's October 13th, 2026 research news release on SPACER, the Nature Biomedical Engineering article page of the same date read for its abstract, and two National Cancer Institute dictionary entries read through the NCI glossary API.",
 "topic": "MD Anderson and collaborating Texas institutions published SPACER in Nature Biomedical Engineering on October 13th, 2026, an AI model that reads spatial transcriptomics and groups of neighboring cells to infer why immune cells gather in some tissue regions and avoid others. Applied across 37 datasets it was four to 21 times more effective than existing approaches in the team's benchmarks. Its leading physical finding is that mucins may form barriers that keep T cells away from tumors, and in melanoma and gastric cancer datasets more mucin went with poorer responses to checkpoint inhibitors. No use in patient care is reported.",
 "angle": "Nine material reliefs of one dark bench under a low key: a nest walled by a glossy mucin coat with ember T cells halted outside, a panorama of 37 slides cut across the swipe, a machined rule at two scales for four and 21, the cover's camera on a nest with no coat where T cells press in, the wall at macro, four cores by cancer type and mucin, and the slide back on a microscope stage in darkfield with its funders engraved on the label.",
 "angle_note": "Every section, slide, cell and stage is drawn to illustrate. No patient's or dataset's tissue is depicted, heights separate materials and are not measured, one slide stands for each dataset, and rim height on the cores is not a measurement. No claim places the work in Houston or Harris County, so the deck and caption name MD Anderson and Texas institutions only.",
 "entities": ["MD Anderson", "SPACER", "Nature Biomedical Engineering", "Tao Wang", "Linghua Wang", "Cancer Prevention and Research Institute of Texas", "National Cancer Institute"],
 "places": ["Texas"],
 "what_was_refused": "cprit.texas.gov answered 403 to the fetcher, so no CPRIT figure or voter sentence is carried. The journal page's author order does not support co-led, so co-led stays MD Anderson's word. The postal route metaphor was refused as overclaiming what the model tracks.",
 "keywords": ["MD Anderson", "SPACER", "spatial transcriptomics", "T cells", "mucin", "checkpoint inhibitors", "melanoma", "gastric cancer", "immunotherapy", "AI model"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-17/update_ledgers.py.",
 "register": "RELIEF, NOT A SCENE. Nine material reliefs through txbench.js declared once in assets/js/deck/2026-10-17-section.js (key az 300 el 16, ground #05040A), a darkfield bench. No camera, no sky, no room and no kit model. Materials: black glass, plum stroma, oxblood tumor cells, a pale mucin glaze, ember T cells, steel, frosted label, slide glass, a plum black anodised stage and a warm ground bevel.",
 "structural_laws": [
  "A WOBBLED OUTLINE STRIPES THE FORM THAT FOLLOWS IT. A three octave noise on the wall's centre line changed its slope every 60 to 120 px and printed vertical bands across the dome with the cast and the specular both off. Smooth sums of sines fixed it.",
  "A LOW KEY NEEDS A LOW SHININESS. At elevation 16 the half vector tilts about 37 degrees, so a dome whose flank never reaches that slope returns no highlight at shininess 150.",
  "LIGHT FROM BELOW IS AN EDGE, NOT A DISC. A screened disc over the aperture read as a plate; darkfield, a ring and a lit section outline, read as transmitted light.",
 "A SMOOTH GLAZE READS AS A CURB. The wall failed two audition readings as a flat extrusion and passed once it became a heap of about 1,400 overlapping glossy globules, each catching the key as its own point.",
  "A GRID ON A PLATE READS AS GRAPH PAPER. The panel charged a filled micrometer grid as a chart twice, and the frames passed the detail floor instead on engraved scales along the rule's own edges and a tooth on the bars."],
 "techniques": [
  "a tumor nest in a pebbled glossy mucin coat at macro, ember T cells halted on the stroma outside it",
  "the left half of a panorama of 37 glass slides on a black bench, the seam slide cut",
  "the panorama's right half, the lower row ending short on bare bench",
  "a machined rule close, a frosted one unit bar and a steel four unit bar named SPACER casting long, a terrace running off toward 21",
  "the whole rule at one scale, one, four and 21 units, each track labelled on its own baseline over an engraved 21 unit scale",
  "the cover's camera on an uncoated nest, studded outer cells with T cells pressed in and a kerb round one neighborhood",
  "the mucin wall at macro as a heap of glossy globules on a long S, T cells banked on its outer foot and its cast over the tumor",
  "four cores by melanoma and gastric and by lower and higher mucin, T cells inside the low cores and outside the glazed rims",
  "the whole slide on a black microscope stage under knurled clips, the cover's nest under the lens in darkfield, five engraved funder lines and a leader to the Texas fund"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A darkfield relief deck."},
 "accent": {"hex": "#B4664F", "name": "dusk ember", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The T cells and nothing else, the brown a pathologist sees when T cells are stained."},
 "ground": {"hex": "#05040A", "note": "The deck's declared ground behind the render."}})
cap = (OUT / "caption.txt").read_text().strip()
body = "\n".join(l for l in cap.splitlines() if not l.startswith("#"))
words = len(re.findall(r"[A-Za-z0-9'][A-Za-z0-9',.%-]*", body))
commas = body.count(",") - len(re.findall(r"\d,\d", body))
add("captions", {"date": D, "carousel_no": N, "opening_move": "the plain question", "structure": "Question and answer",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": round(100 * commas / words, 2),
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "The critic refused both candidates as written and demanded one rewrite of A: no Houston (no claim carries it), the benchmark scoped in c4's own terms, and traced hashtags. The shipped caption is that rewrite, with the panel's later repairs: the release's stated purpose in place of a narrowed one, absences that name the release, and the line about the frames removed.",
 "move_note": "Opens on the question a reader who has watched a checkpoint drug fail already asks, answers it with the mucin finding and its limits, and closes on whether a mucin reading could ever guide a checkpoint drug."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
