#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-06, carousel no. 70. Appends one entry to each variety ledger,
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
D, N = "2026-11-06", 70
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0242", "related_items": [],
 "instrument": "ExxonMobil's third quarter 2026 earnings call transcript and its newsroom post on automated drilling, its Permian operations page, the Reuters report of August 2026 as republished by AJOT, and Helmerich & Payne's release of October 7th, 2026, all fetched November 6th, 2026.",
 "topic": "ExxonMobil says 3 of its Permian drilling rigs are automated, with robotic arms doing much of the heavy pipe handling on the rig floor. It expects automated rigs on about 25% of its Permian fleet next year and approximately half by 2028, with similar staffing. Reuters reported the arms move columns of pipe over 2 stories tall, a Red Zone gate around the floor at a Midland rig, the first H&P rig drilling 2 miles sideways in a little over 6 days, and Bart Cahir saying about a third of significant injuries in well drilling happen on the rig floor. H&P expects 7 more FlexRobotics systems for ExxonMobil over 12 months, 9 in all.",
 "angle": "The floor where people stood, at night under a cold flood. The gripper on the pipe, the Red Zone gate, the floor plate with its injury third lit, a stand of pipe over 2 stories beside a worker in a hard hat, the arm seating a pin in the box, the cabin of screens, 2 miles of lateral against the rig, 5 of 20 joints banded for next year and 10 of 20 on the rack for 2028.",
 "angle_note": "No source calls the rigs AI, so the deck says automated and robotic. The one-third incident figure is a stated potential, kept apart from Cahir's about a third of injuries. Every frame is drawn to illustrate, to no maker's or operator's design. The rack of twenty is a drawing unit for the whole fleet.",
 "entities": ["ExxonMobil", "Helmerich & Payne", "Reuters"],
 "places": ["Midland", "Midland County", "Permian Basin", "Houston"],
 "what_was_refused": "any claim the rigs use AI, any measured safety result, any number of workers per rig, the newsroom's more than half by year end 2028 merged with the call's approximately half, and any rig dimension as fact.",
 "keywords": ["ExxonMobil", "automated drilling rigs", "robotic pipe handling", "Permian Basin", "Midland", "Helmerich & Payne", "FlexRobotics", "rig floor safety"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES on a rig floor at night under a cold mast flood in the floodlit world (frames 1, 2, 4, 5 and 9), one built cabin interior (6) and three TXBENCH material reliefs (3 floor plate, 7 geologic section, 8 pipe rack). Chassis assets/js/deck/2026-11-06-rigfloor.js: drill_pipe, pipe_stand, pipe_robot, rig_mast, rig_floor and red_zone_gate models with the kit's person, desk, monitor and office_chair, and dusk_ember paint bands as the one accent for pipe work handed to a machine.",
 "structural_laws": [
  "A CAMERA BEHIND THE WRIST HIDES THE JAWS. From the side the arm reaches from, the wrist housing covers the gripper, so the jaws read only along the arm's axis or from three quarters.",
  "A BAND SCALED TO MEET AN ACCENT FLOOR BECOMES A BLOCK. Stretching an ember band four times its height to pass a coverage line drew a flat orange slab a critic took for a placeholder.",
  "A FOOT WASH OVER THE ACCENT KILLS IT. The bottom darkening wash dropped the ember bands on frames 4 and 9 below the accent floor, so a band near the footer needs its own hex or a moved wash.",
  "A FLAT PANE IS A DEAD WINDOW. A window drawn as one emissive plane read as a projector screen until it carried mullions, a sill and a night view.",
  "A HANGING PIN OVER AN EMPTY BOX DRAWS NO CONNECTION. The pin has to touch the box for the frame to show the act its headline names."],
 "techniques": [
  "a gripper's jaw closed on a vertical drill pipe at arm's length, an ember band on the pin",
  "a Red Zone pipe gate across the foreground with the arm and slips in the pool beyond",
  "a material relief of nine floor plate panels, three diamond tread in the lit pool",
  "racked stands over 2 stories beside a worker in a hard hat outside the gate",
  "a three quarter macro of a pin seated in the box in the slips, the arm in from the right",
  "a dark cabin of three screens and two joystick consoles, a night window on the floor",
  "an earth section relief with two miles of lateral against a rig pin",
  "a pipe rack relief of twenty joints, five banded in ember with a bracket",
  "a rack of twenty joints on the pipe deck, ten banded, the lit rig floor beyond"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged night world, a dark room and dark reliefs."},
 "accent": {"hex": "#B4664F", "name": "dusk_ember paint band, pipe work handed to a machine", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "One band on the gripped pin on 1, 2, 4 and 5, five of twenty on 8, ten of twenty on 9."},
 "ground": {"hex": "#08060F", "note": "The night sky and the dark deck."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens on the floor hands and the arm that replaced their pipe handling, climbs from three rigs to the 2028 plan as the company's expectations, and closes on the safety result the company has not published.",
 "move_note": "A ladder from the arm on one rig to the fleet plan, every figure attributed to ExxonMobil or Reuters, and a close naming what is still not public, a measured safety result."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
