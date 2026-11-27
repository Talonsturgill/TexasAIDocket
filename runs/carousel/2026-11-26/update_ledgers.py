#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-26, carousel no. 88. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "out" else HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
STRUCT = json.loads((Path(__file__).resolve().parent / "structural_laws.json").read_text()) if (Path(__file__).resolve().parent / "structural_laws.json").exists() else []
from PIL import Image
D, N = "2026-11-26", 88
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0263", "related_items": ["tx-2026-0259", "tx-2026-0247"],
 "instrument": "Texas Tech Now's November 20th release on Texas Tech's FleetSpace work for Army aviation, and Texas Tech's Institute for Materials, Manufacturing and Sustainment page, fetched November 26th, 2026.",
 "topic": "Texas Tech's Institute for Materials, Manufacturing and Sustainment and Fort Worth based AVX Defense Technologies built an AI enabled maintenance decision tool and an engine life tracker under the Army's FleetSpace program, and Texas Tech says both have been provided to the Army, with every reported result from testing.",
 "angle": "Before it fails. An illustrative engine drawn to no maker's design and its flight record drawn as metal, from the record with holes to the share restored in testing, the files made smaller, the 480 hour phase, the blade the validator flags, the part a person inspects, the Lubbock to Fort Worth route, and the engine still on test at an open hangar door with the cased tools out on the apron.",
 "angle_note": "Dusk gold means what the software puts out, only. Every result is from testing. The tools are provided to the Army, never fielded or used. No aircraft type, unit, cost, accuracy or savings figure is drawn or written.",
 "entities": ["Texas Tech University", "Institute for Materials, Manufacturing and Sustainment", "AVX Defense Technologies", "U.S. Army", "Army Aviation and Missile Command", "Henry Johnston", "Tommy Dang", "GE Aerospace"],
 "places": ["Texas", "Lubbock", "Lubbock County", "Fort Worth", "Tarrant County"],
 "what_was_refused": "any service result, any aircraft type or unit, any adoption, fielding or purchase, any cost or contract value, any accuracy figure, any savings figure, and any hours run marker.",
 "keywords": ["aircraft maintenance", "predictive maintenance", "engine remaining useful life", "flight data", "neural networks", "FleetSpace", "Army aviation", "Texas Tech"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 explainer tone, nine slide artists. An illustrative turboshaft on an A frame stand with a gold tag and two gold hard cases in a cerulean studio (1), a finned titanium recorder feeding a punched aluminium record foil with burnt cells (2), a bead blasted record cassette with 37 gold blocks carrying one continuous trace and 63 damaged sockets (3), two milled bars on ground parallels against frosted glass ghosts of full stock on lapped granite, labelled volume and files (4), a relief of a brushed hour rule from a nickel zero stop across an indigo mat with a gold tab at the 480 tick (5), a pulled back macro of a heat tinted turbine stage under an indigo case wall, one blade with a gold hairline that stops partway (6), a bench close up of one twisted blade in a foam cutout, a borescope tip touching it and a gold tag on the root (7), a caliche relief of Texas with Lubbock and Tarrant raised and seven brass rivets on a milled route (8), the engine on test inside a bay at an open door with two gold cases out on a jointed concrete apron casting long shadows (9).",
 "structural_laws": STRUCT,
 "techniques": ["an illustrative turboshaft on a stand in a studio sweep", "a punched record foil from a recorder", "an orthographic record cassette with gold blocks and one trace", "milled bars on parallels against frosted glass ghosts", "an hour rule relief from a zero stop", "a macro turbine blade with an inlaid leading edge", "a bench close up of a probe on a flagged blade", "a caliche map relief with raised counties and rivets", "an engine on test seen from inside a bay through an open door"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "What the software puts out, only."},
 "ground": {"hex": "#ffc68a", "note": "Explainer tone sweep floor under cerulean and indigo."}})
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
