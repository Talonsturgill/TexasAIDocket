#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-27, carousel no. 89. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "out" else HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-11-27", 89
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
ACC = json.loads((OUT / "accent.json").read_text())["hex"]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), ACC), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0255", "related_items": ["tx-2026-0226", "tx-2026-0261"],
 "instrument": "The comptroller's proposed amendments to 34 TAC Rule 3.308 and their fiscal note in the Texas Register of November 20th, the comptroller's November 18th release and GovDelivery bulletin, fetched November 27th, 2026.",
 "topic": "Texas Comptroller Don Huffines proposed amendments to Rule 3.308 that would class cloud, AI and quantum computing as hosted technology services outside the tax on data processing, with his office's own fiscal note estimating the state and local revenue loss and a 30 day comment window.",
 "angle": "A sheet per million. The fiscal note's estimate drawn in the document's own material, kraft reams at a sheet per million dollars, from the rack the rule is about, through the old definition and the rented slot the new definition would leave out, to the rule's words on the page, the first and last fiscal years as measured stacks, the local share on a dais, the note's own word insignificant under the tallest stack's shadow, the cubbies of the comment window, and a letter on the stack.",
 "angle_note": "Dusk gold means the words of the proposal, only. Kraft is the estimate and cream is the rule. Nothing is adopted. No savings, no business, no city or transit authority is named or drawn.",
 "entities": ["Texas Comptroller of Public Accounts", "Don Huffines", "Robin Robinson", "Sarah Eckhardt", "Texas Legislature", "Texas Register"],
 "places": ["Texas"],
 "what_was_refused": "the release's framing of the rule as a tax cut for Texans, any savings figure, any named business or local government, any claim that the rule is adopted, and any loss figure for a year the note does not count.",
 "keywords": ["data processing tax", "sales tax", "cloud computing", "artificial intelligence", "hosted technology services", "Rule 3.308", "fiscal note", "public comment"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 watch tone, nine slide artists. A violet 42U rack with its hex door open, the rule's page clipped inside with one gold line and the fiscal 2027 stack at its foot on the sweep (1), a coil bound report with coral tabs and the customer's papers on a walnut service counter under a rose window (2), a cold aisle ending at a rack whose rented slot holds a cream archival box, perforated tile and glass bays (3), a TXBENCH relief of the Register page on an oak board with a gold paragraph, three emblem seals and a steel binder clip (4), the fiscal 2027 and 2032 kraft stacks turned on an oak table in a dusk room at a measured 2.2013 ratio (5), the two local stacks on a council dais ledge under a bronze seal (6), the note's page with its gold line crossed by the 2032 stack's shadow (7), a 30 cubby violet enamel sorter with the last cubby lit (8), the 2032 stack on a walnut desk carrying a reader's letter and pen (9).",
 "structural_laws": [],
 "techniques": ["a server rack with its door open in a studio sweep", "a service counter still life under a window", "a cold aisle ending on a rented slot", "a material relief of a Register page with seals", "two measured paper stacks at equal depth", "stacks on a council dais ledge", "a shadow across a highlighted line", "a pigeonhole sorter lit in its last cubby", "a letter resting on a paper stack"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The words of the proposal, only."},
 "ground": {"hex": "#ff8a5a", "note": "Watch tone sweep floor under violet and navy."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": mv["critic_note"], "move_note": mv["move_note"]})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
