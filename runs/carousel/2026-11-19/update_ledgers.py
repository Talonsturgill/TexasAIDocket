#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-19, carousel no. 82. Appends one entry to each variety ledger,
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
D, N = "2026-11-19", 82
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0252", "related_items": ["tx-2026-0218"],
 "instrument": "UT Arlington's November 12th, 2026 news release on its USDA funded screwworm smart trap project, with USDA ARS and APHIS screwworm pages for context, fetched November 19th, 2026.",
 "topic": "UT Arlington coordinates a $3.1 million USDA funded project against New World screwworm, which has reemerged with more than 120 confirmed animal cases, most in Texas. Its AI smart trap is meant to tell wild flies from sterile ones and females from males, keep the wild females and release sterile flies and other insects, where today's traps catch everything and are sorted by hand. The trap isn't built; a prototype is expected next spring and the project runs through June 2028.",
 "angle": "A door with a choice behind it. A fly at a clear glass funnel's mouth, an aluminium block with a well for each kind of fly and the wild female's well rimmed in gold, a glass Y that keeps the wild fly and frees the rest, a stepped rack of tubes for the monitored traps in a lab, a bucket trap on mesquite with the program's own flies streaming past, a resin relief of release swaths from Edinburg led back to Kerrville, stoneware boxes in rows with the lifted box showing its doors, a fence of posts by month to June 2028 at blue hour, and the unbuilt glass on a cedar bench beside a phone framing a calf's hide.",
 "angle_note": "Every frame is drawn to illustrate. The trap is never drawn as a field device, with no camera, flap, circuit, accuracy or catch count. No fly size is claimed, so no fly stands beside an object that measures it. The 80 million a week and the 100 traps never share a frame. Gold means the fly the sort keeps only.",
 "entities": ["UT Arlington", "USDA", "APHIS", "USDA Agricultural Research Service", "Knipling-Bushland Livestock Insects Research Laboratory"],
 "places": ["Texas", "Kerrville", "Edinburg"],
 "what_was_refused": "fly size and appearance, irradiation method and trap mechanism (no primary page states them), the USDA dashboard's own figures (not opened), the Panama sterile fly supply (kept off so no frame sets two flows against each other), and an aircraft or release plume (no claim says aircraft).",
 "keywords": ["screwworm", "smart trap", "sterile flies", "livestock", "USDA", "APHIS", "UT Arlington", "AI"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 wonder tone, nine slide artists. TXT.studio sweeps (1, 2, 3, 7), TXT.interior lab (4), outdoor TXT.sky worlds (5, 8, 9), a TXBENCH relief (6). Spine assets/js/deck/2026-11-19-sortglass-bespoke.js with chassis models blowfly, beetle, sort_glass, cell_block, stone_plinth, dead_end_jar, bucket_trap and smartphone.",
 "structural_laws": [
  "FIG_INJECT FILLS A FRAME WITH EVERY FIGURE WHEN ITS CODE READS window.FIG DYNAMICALLY, so a 'FIG must be empty' check written with Object.keys throws at the full render; a no-figure frame must read no FIG name at all.",
  "THE CHASSIS CELL_BLOCK'S WELLS ARE SOLID DISCS, so a fly placed in one is buried; frame 2 built its own bored block.",
  "A WARM HONEY KEY TURNS CLEAR GLASS AND A GOLD BAND PEACH, so the gold accent stops reading as one thing; keep glass cool tinted and seat the gold against cobalt.",
  "A BRIGHT HORIZON BAND IN A WINDOW OR SKY BEHIND A DEK LINE IS REFUSED BY QA AS A STRIKETHROUGH; place the type over flat wall or deep sky."],
 "techniques": ["a macro fly astride a clear glass funnel lip with the fork and a gold keep band seen through the glass", "a raked machined block of four glass topped cells, the wild female shut under the one gold rim", "a borosilicate Y on a caliche pedestal keeping one fly behind a gold band and freeing three and a beetle", "a stepped stand of 100 tubes of mixed catch in a cobalt lab with a sorter at a lamp", "a weathered bucket trap on a mesquite limb taking in a stream of 80 flies", "a caliche relief of South Texas with a fan of resin release swaths from Edinburg led back to Kerrville", "forty stoneware boxes on a periwinkle sweep, the two-door box pulled forward from its slot", "a blue hour pipe fence of 19 posts ending at a braced post beside a caliche road", "the unbuilt sort glass on a cedar bench beside a phone with a gold report pill"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The fly the sort keeps only."},
 "ground": {"hex": "#e4d8c3", "note": "Caliche under the wonder tone's cobalt and peach."}})
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
