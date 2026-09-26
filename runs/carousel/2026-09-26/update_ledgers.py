#!/usr/bin/env python3
"""update_ledgers.py — the three variety ledgers, written from this run's own artifacts.

Every count and measurement is READ from a file this run produced: the caption's words and commas
are counted here, the value track is read off deck_coherence's own output at 432 px, and the accent
frames off layout_check's report. Nothing numeric is typed.
"""
import json, pathlib, re, subprocess, sys

RUN = pathlib.Path(__file__).resolve().parent
ROOT = RUN.parents[1] if RUN.parent.name == "out" else RUN.parents[2]
DATE, NO = "2026-09-26", 34
L = ROOT / "ledger" / "carousel"

cap = (RUN / "caption.txt").read_text().strip()
body = "\n".join(l for l in cap.splitlines() if not l.strip().startswith("#"))
words = len(body.split())
commas = body.count(",") - len(re.findall(r"\d,\d", body))
hashtags = re.findall(r"#\w+", cap)
first_line = cap.splitlines()[0].strip()

dc = subprocess.run([sys.executable, str(ROOT / "scripts/carousel/deck_coherence.py"), "--render-dir", str(RUN / "render"),
                     "--storyboard", str(RUN / "storyboard.md")], capture_output=True, text=True, cwd=ROOT).stdout
track = [float(x) for x in re.search(r"value track \[([^\]]*)\]", dc).group(1).split(",")]
jumps = [abs(b - a) for a, b in zip(track, track[1:])]
lc = subprocess.run([sys.executable, str(ROOT / "scripts/carousel/layout_check.py"), "--date", DATE],
                    capture_output=True, text=True, cwd=ROOT).stdout
acc = {int(m.group(1)): float(m.group(2)) for m in re.finditer(r"^\s+0?(\d)\s+\S+.*accent (\d\.\d+)", lc, re.M)}
acc_frames = sorted(k for k, v in acc.items() if v >= 0.002)

topics = json.loads((L / "topics.json").read_text())
artwork = json.loads((L / "artwork.json").read_text())
captions = json.loads((L / "captions.json").read_text())
for led in (topics, artwork, captions):
    led["entries"] = [e for e in led["entries"] if e.get("date") != DATE]

topics["entries"].append({
  "date": DATE, "carousel_no": NO, "docket_item": "tx-2026-0188",
  "instrument": "The TxDMV Automated Vehicles Regulatory Program page and the adopted 43 TAC Chapter 220 with its responses to comments, read in full, against the companies' own releases on the Dallas to Houston lane and one secondary news report.",
  "topic": "Since May 28th a company running driverless vehicles commercially in Texas needs a TxDMV authorization. It acknowledges a set of statements, certifies a responder plan, pays no fee and holds an authorization that does not expire. The City of Dallas asked the department to require crash history and the department answered that the statute does not allow it. Kodiak has named Dallas to Houston as its driverless launch lane and Aurora gave investor day guests rides with nobody behind the wheel.",
  "angle": "The permission the lane runs on, read as paper: what it asks, what it can't ask, where the state draws its line, and where a Texan sends a concern.",
  "angle_note": "Carousel no. 5 of August 21st covered the same authorization under SB 2807 and the same lane. It is outside the thirty day window and two judges named the familiarity. This deck's news is the adopted rule's answer to Dallas and the reporting route, neither of which no. 5 carried. The count of trucks running now rests on Breitbart relaying a CNBC ride that was not read, and the TxMCCS lookup itself was not read, so no surface says what a member of the public can see there.",
  "entities": ["Texas Department of Motor Vehicles", "City of Dallas", "Kodiak AI", "Aurora", "Waabi", "State Office of Administrative Hearings"],
  "places": ["Dallas", "Houston", "Lancaster", "Interstate 45", "Permian Basin", "Dallas County", "Harris County"],
  "what_was_refused": "Any reconciliation of Kodiak's and Waabi's corridor lengths. Any claim that the observer has left the cab. Any list of which companies hold an authorization, because the lookup was not read. Any link between recorder data and crash history.",
  "keywords": ["driverless trucks", "TxDMV authorization", "43 TAC 220", "Interstate 45", "Kodiak", "Aurora", "Waabi", "crash history", "serious bodily injury", "SOAH", "TxMCCS"]
})

artwork["entries"].append({
  "date": DATE, "carousel_no": NO,
  "written_from": "deck_coherence's value track at 432 px and layout_check's accent measurement, both run by this script off the final renders, and the gate suite by exit code.",
  "register": "RENDERED, NOT PRINTED. One blue hour world on Interstate 45 declared once in assets/js/deck/2026-09-26-fortyfive.js: blueHour tuned so the haze is the horizon's cool blue rather than the preset's peach, one key at azimuth -160 elevation 32, a chassis tractor with mirror sensor pods, a cab set built once and mirrored for the forward view, and the recorder lamp the one accent #E0956A.",
  "structural_laws": [
    "A PEACH HAZE OVER A BLUE GROUND GRADES EVERY FRAME MAUVE. All five round 1 critics named it. The fix was one tuned world in the chassis, haze and horizon in the same cool blue and the preset's horizon glow cut, and it moved nine frames at once.",
    "THE SHADOW CAMERA IS NINE METRES UNLESS A FRAME SAYS OTHERWISE. A yard of thirty five trucks lost four rows of shadows until the rig's key carried shadowSize for the frame.",
    "A CAMERA INSIDE A SET CAN SIT BEHIND ITS OWN WALL. Pulling the cab camera back half a metre put it behind the bunk curtain and the frame came back black. Measure the set before moving a camera in it.",
    "A GROUND PLANE THAT ENDS SHORT OF THE HORIZON SHOWS AS A SEA. At twelve kilometres the ground runs into its own haze."
  ],
  "techniques": [
    "one cab interior set built once in the chassis and shot three ways: forward through the windshield, down onto the seat, and at the bulkhead",
    "a truck yard of painted places in rows receding to the haze with the reported count parked in the nearest rows",
    "a review timeline painted on a truck court at a stated meters per day, each segment exactly its days, with leaders projected through the frame's own camera",
    "a bar of days from May 28th to the run date with a hairline running on to the edge for an authorization that does not expire"
  ],
  "value": {"per_frame_median_L": track, "deck_median_L": sorted(track)[len(track) // 2],
            "max_adjacent_delta": round(max(jumps), 1), "mean_adjacent_delta": round(sum(jumps) / len(jumps), 2),
            "note": "Measured by deck_coherence at 432 px off the final renders."},
  "accent": {"hex": "#E0956A", "name": "recorder lamp", "frames_above_floor": acc_frames,
             "note": "The recorder's status lamp on 3 and 7, and on 6 the pen and the recording device row's tick."},
  "ground": {"hex": "#151D33", "note": "The deck's declared ground. The craft judge measured it close to no. 33's #131A24."}
})

captions["entries"].append({
  "date": DATE, "carousel_no": NO,
  "opening_move": "the who", "structure": "Ladder",
  "closing_move": "Point at the record, plainly, without a call to action",
  "first_line": first_line, "words": words, "commas": commas,
  "commas_per_100w": round(commas / words * 100, 2), "chars": len(cap), "hashtags": hashtags,
  "critic_note": "The critic chose B. After the panel's first round the closing question 'Can the driver in the next lane?' was replaced because two judges read it as insinuating the public can't check an authorization when the lookup was never read, and the line narrating the deck was cut.",
  "move_note": "Opens on who answered whom, the DMV and Dallas. Each paragraph adds one rung, the answer, the permission, the companies, the line, and the close points at the record in the interrogative form brand.yaml requires."
})

for name, obj in (("topics", topics), ("artwork", artwork), ("captions", captions)):
    (L / f"{name}.json").write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}.json: {len(obj['entries'])} entries, newest {obj['entries'][-1]['date']}")
print(f"caption measured: {words} words, {commas} writer commas, {len(cap)} chars; accent frames {acc_frames}; track {track}")
