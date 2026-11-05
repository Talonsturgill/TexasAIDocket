#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-03, carousel no. 67. Appends one entry to each variety ledger,
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
D, N = "2026-11-03", 67
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#8C5A3C"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0239", "related_items": ["tx-2026-0214", "tx-2026-0209"],
 "instrument": "Aurora Innovation's third quarter 2026 shareholder letter on SEC EDGAR, dated October 28th, and Aurora's own release on the Dallas to Houston route, both fetched November 3rd, 2026.",
 "topic": "Aurora's third quarter 2026 shareholder letter says its driverless trucks can now tell whether a weigh station is open, steer to an available scale lane and adapt to scale configurations, and that in November they will drive directly to customer sites through security checkpoints. It says more than 20 driverless trucks are built, the ramp is behind its prior plan, revenue was $3 million against a $257 million operating loss, FMCSA granted a cab beacon exemption, and Aurora expects more than 200 trucks by the end of February and more than 1,000 at the end of 2027. Charger Logistics plans to start between Dallas and Laredo under a non-binding MOU.",
 "angle": "A white tractor on a floodlit weigh station scale at night, the calls as lit rings on the apron, the nose at a November gate's primer stop bar, the built tractors in ranks, the slip as a steel rule and a primer stop, revenue and loss as a billet and a bar on a shared scale, the corridor as a clay relief with a white inlay and primer studs, the cab beacon, and a yard of white stalls running into primer paint.",
 "angle_note": "No Texas weigh station or customer is named, because the letter names none. Dallas to Laredo is drawn as Charger's plan in primer, never as an Aurora route. Every frame is drawn to illustrate.",
 "entities": ["Aurora Innovation", "Charger Logistics", "AUMOVIO", "FMCSA"],
 "places": ["Dallas", "Houston", "Laredo", "New Braunfels"],
 "what_was_refused": "any named Texas weigh station or customer site, any statement that the Dallas to Laredo route runs today, and any figure for trucks per week beyond the letter's expected 20 in early December.",
 "keywords": ["Aurora", "driverless trucks", "autonomous trucking", "weigh station", "FMCSA", "Dallas", "Houston", "Laredo", "shareholder letter"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in one staged floodlit weigh station and truck yard at night (frames 1 to 4, 8 and 9) with three TXBENCH material reliefs (5 to 7). Chassis assets/js/deck/2026-11-03-scalelane.js: truck_scale, scale_house, scale_signal, flood_pole, guard_gate, cab_beacon and yard_stalls, with the kit's semi_truck and highway, and primer rust as the one accent for what the letter expects and has not happened.",
 "structural_laws": [
  "LIGHT DESATURATES AN ACCENT. A primer albedo at the accent hex rendered ten to twenty Lab units off it under a cool flood, so the stop bar and the kerbs needed a warmer, more yellow albedo than the target to land within twelve.",
  "A LABEL ON A RELIEF IS STRUCK BY ITS GROOVES. Map labels crossed county grooves and route lines until each sat on dark Gulf or plain ground with a leader to its place.",
  "A RELIEF CAST NEEDS HEIGHT, NOT LENGTH. A long cast length over a low land plate stayed under the cast floor until the land itself stood proud and the county lines were cut into it.",
  "A YARD OF STALLS READS AS ONE PAINTED PLATE until the paint sits a value below the cabs and the asphalt is sealed near black.",
  "MOVING A RELIEF MOVES ITS RECT. The quarter's bar was raised and the dossier rect left behind measured empty bed under the detail floor until the rect was moved with it."],
 "techniques": [
  "a white tractor on a steel scale deck between yellow kerb rails, the scale house window lit beside it and a green signal over the lane",
  "the station from its flood pole, three lit rings on the apron at the three calls the letter names, each with a leader",
  "the tractor's nose at a guard gate boom with a single primer stop bar across the lane",
  "twenty tractors in two ranks facing the camera across a sealed yard",
  "a steel rule with a witness line, six machined week grooves and a primer clamp, three shims behind it",
  "a polished billet and a mill scale bar on one datum at one scale, a primer groove at the expected 2026 revenue",
  "a clay relief of Texas counties with a bead white inlay for Dallas to Houston and a row of primer studs for Charger's planned Dallas to Laredo",
  "an amber cab beacon lit on a stopped tractor's roof at night",
  "the yard from its light mast, 20 white stalls with tractors, primer kerbs closing the first 200 and the end of 1,000"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged night station and dark reliefs."},
 "accent": {"hex": "#8C5A3C", "name": "primer rust, what the letter expects and has not happened", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "November's stop bar on 3, the primer stop on 5, the expected 2026 revenue groove on 6, Charger's planned studs and New Braunfels on 7, the 200 and 1,000 stalls and kerbs on 9."},
 "ground": {"hex": "#08090C", "note": "The night yard's sealed asphalt and the reliefs' black bed."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens on who was told, then keeps the letter's ledger in its own tense, the three calls, the slip, the quarter and the two routes, and closes on whether a Texas scale house has weighed one yet.",
 "move_note": "Opens on Aurora telling its shareholders about weigh stations, lists the letter's claims as a ledger attributed to it, keeps Dallas to Laredo as Charger's plan under a non-binding MOU, and closes asking the one question the letter leaves open."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
