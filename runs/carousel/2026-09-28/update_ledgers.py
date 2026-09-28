#!/usr/bin/env python3
"""Append carousel no. 36's entries to the three variety ledgers.

Every count and measurement is READ from a file this run produced: the caption's words and commas
are counted here, the value track is read off deck_coherence's own output at 432 px, and the accent
frames off layout_check's report. Nothing numeric is typed."""
import json, pathlib, re, subprocess, sys

RUN = pathlib.Path(__file__).resolve().parent
ROOT = RUN.parents[1] if RUN.parent.name == "out" else RUN.parents[2]
DATE, NO = "2026-09-28", 36
L = ROOT / "ledger" / "carousel"
REND = RUN / "render" if (RUN / "render").exists() else ROOT / "out" / DATE / "render"

cap = (RUN / "caption.txt").read_text().strip()
body = "\n".join(l for l in cap.splitlines() if not l.strip().startswith("#"))
words = len(body.split())
commas = body.count(",") - len(re.findall(r"\d,\d", body))
hashtags = re.findall(r"#\w+", cap)
first_line = cap.splitlines()[0].strip()

dc = subprocess.run([sys.executable, str(ROOT / "scripts/carousel/deck_coherence.py"), "--render-dir", str(REND),
                     "--storyboard", str(RUN / "storyboard.md")], capture_output=True, text=True, cwd=ROOT).stdout
track = [float(x) for x in re.search(r"value track \[([^\]]*)\]", dc).group(1).split(",")]
jumps = [abs(b - a) for a, b in zip(track, track[1:])]
lc = subprocess.run([sys.executable, str(ROOT / "scripts/carousel/layout_check.py"), "--date", DATE],
                    capture_output=True, text=True, cwd=ROOT).stdout
acc = {int(m.group(1)): float(m.group(2)) for m in re.finditer(r"^\s+0?(\d)\s+\S+.*accent (\d\.\d+)", lc, re.M)}
acc_frames = sorted(k for k, v in acc.items() if v >= 0.002)
srt = sorted(track); med = srt[len(srt) // 2]

topics = json.loads((L / "topics.json").read_text())
artwork = json.loads((L / "artwork.json").read_text())
captions = json.loads((L / "captions.json").read_text())
for led in (topics, artwork, captions):
    led["entries"] = [e for e in led["entries"] if e.get("date") != DATE]

topics["entries"].append({
  "date": DATE, "carousel_no": NO, "docket_item": "tx-2026-0192",
  "instrument": "The PUCT order approving Southwestern Public Service Company's system resiliency plan in Docket 57463 (Item 108), read against SPS's first annual resiliency plan report in Project 57941 (Item 7) and the plan application with its testimony (Item 2), all from the PUCT Interchange, with the wildfire plan rule, the staff pro forma and the Texas Tribune's hearing report beside them.",
  "topic": "The PUCT order approving SPS's resiliency plan lists the number of AI camera fire detections among the evaluation metrics the parties agreed and SPS will carry into its annual reports. SPS's first annual report, filed May 1st, 2026, answered that line with 33 cameras installed and 34 projected, and gives no count of detections, while it counts ignitions, wildfires and its camera costs to the dollar.",
  "angle": "Agreed to count fire detections, counted cameras: what the Panhandle utility's AI smoke cameras are, what the order asked its reports to carry, what the report put on that line, and where the next answer will be filed.",
  "angle_note": "The detections metric is one the parties agreed and the order approved, so the deck says agreed and never that the state asked. The absence is scoped to that line of that report, and the deck says a missing count isn't a count of none. The 97 cameras the Tribune reports are a service territory count and stay off every frame. The wildfire mitigation plan law and its 30 day window are a different rule from the resiliency plan, so the deck says so and never offers the window as a way into this matter.",
  "entities": ["Public Utility Commission of Texas", "Southwestern Public Service Company", "Xcel Energy", "Pano AI", "Texas House State Affairs Committee", "The Texas Tribune"],
  "places": ["Texas Panhandle", "Hutchinson County", "Moore County"],
  "what_was_refused": "Any count of detections, including zero. Any claim the cameras did or did not detect a fire. The Tribune's 97 cameras as a Texas count. The 30 day wildfire plan window as a route into Docket 57463. Any claim the state authored the metric rather than approving what the parties agreed.",
  "keywords": ["Xcel Energy", "Southwestern Public Service", "AI cameras", "wildfire", "Pano AI", "PUCT", "resiliency plan", "annual report", "Smokehouse Creek", "Texas Panhandle"]
})

artwork["entries"].append({
  "date": DATE, "carousel_no": NO,
  "written_from": "deck_coherence's value track at 432 px and layout_check's accent measurement, both run by this script off the final renders, and the gate suite by exit code.",
  "register": "RENDERED, NOT PRINTED. One stormFront world declared once in assets/js/deck/2026-09-28-watchtower.js with the haze pulled to a dust grey, a denser cloud deck, a thinner fog and more sky light, one wildfire_camera_station hero built in the chassis with boxed white PTZ heads, the key at azimuth -68 elevation 10, and the one accent #2A7A9E kept to a DOM bar under the line the order named.",
  "structural_laws": [
    "THE KIT'S POLE IS A PRIMITIVE AT DETAIL SCALE. Frame 2 was named in three panel rounds, the trunk twice and the pole top once, and read only when recomposed onto a whole distribution line at the distance the kit holds.",
    "A PRESET'S FOG CAN CLOSE THE WORLD. stormFront's density fogged the plain to a white wall at 150 m and hid every mesa placed kilometres out. The caprock read only at 400 m under a thinner fog.",
    "A ROUND FACE ON A CAMERA READS AS A LAMP. Boxed white housings with a small rectangular window read as cameras at feed size, and a yoke plate stops a head floating over its turntable.",
    "A PANE BEHIND A WALL'S FACE RENDERS NOTHING. The window glass on 4 and 5 sat 1 cm behind the interior wall and only its black sash showed, which three judges read as a monitor.",
    "A MAST UNDER THE SITE LINE STRIKES IT AT EVERY PAN THAT KEEPS BOTH HEADS. Frame 3 was recomposed with the mast just left of the footer and the heads dropped below the dek."
  ],
  "techniques": [
    "one wildfire_camera_station model in the chassis, shot from 30 m through a 30 degree lens, level with its crossarm at 12 m, from a corral 57 m off, beside a pipe yard and from a ranch gate",
    "33 loose camera heads on the top rail of a pipe corral seen square on, the lower rail left bare, one head per camera the report counts",
    "two galvanized tubes on timber cribbing from one end plate at the plan and anticipated camera capital on one scale",
    "a hearing room of 160 seats in ten rows with eight white binders placed where a reader can count them",
    "a kit distribution line of 40 ft class poles receding across the plain, and a kit ranch gate closed across a caliche road with a Texan turned toward the mast"
  ],
  "value": {"per_frame_median_L": track, "deck_median_L": med, "max_adjacent_delta": round(max(jumps), 1),
            "mean_adjacent_delta": round(sum(jumps) / len(jumps), 2), "note": "Measured by deck_coherence at 432 px off the final renders."},
  "accent": {"hex": "#2A7A9E", "name": "comal, the line the state's order named", "frames_above_floor": acc_frames,
             "note": "A DOM bar under the quoted detections line on 4, 5 and 6. The binders' spine tabs on 8 carry it under the floor."},
  "ground": {"hex": "#15171C", "note": "The deck's declared ground."}
})

captions["entries"].append({
  "date": DATE, "carousel_no": NO, "opening_move": "the quiet decision", "structure": "Ledger",
  "closing_move": "name what happens next and when", "first_line": first_line,
  "words": words, "commas": commas, "commas_per_100w": round(100 * commas / words, 2), "chars": len(cap), "hashtags": hashtags,
  "critic_note": "The critic chose A. After three panel rounds the order's line was reframed as a metric the parties agreed, the unscoped 30 day wildfire plan window was dropped for SPS's own statement that its 2027 report carries a full year of data, and the close was rewritten to name the next filing, since the room's own close repeated the last run's substance and ledger_check refused it.",
  "move_note": "Opens on the filing date, lays the order's line against the report's answer and what the report does count, and closes on the next filing and when it comes, put as the question it leaves."
})

for name, obj in (("topics", topics), ("artwork", artwork), ("captions", captions)):
    (L / f"{name}.json").write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}.json: {len(obj['entries'])} entries, newest {obj['entries'][-1]['date']}")
print(f"caption measured: {words} words, {commas} writer commas, {len(cap)} chars; accent frames {acc_frames}; track {track}")
