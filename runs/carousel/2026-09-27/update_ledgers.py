#!/usr/bin/env python3
"""Append carousel no. 35's entries to the three variety ledgers.

Every count and measurement is READ from a file this run produced: the caption's words and commas
are counted here, the value track is read off deck_coherence's own output at 432 px, and the accent
frames off layout_check's report. Nothing numeric is typed."""
import json, pathlib, re, subprocess, sys

RUN = pathlib.Path(__file__).resolve().parent
ROOT = RUN.parents[1] if RUN.parent.name == "out" else RUN.parents[2]
DATE, NO = "2026-09-27", 35
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
  "date": DATE, "carousel_no": NO, "docket_item": "tx-2026-0189",
  "instrument": "The Federal Register notice of September 18th, 2026 in United States et al. v. RealPage et al., read in full from the govinfo PDF: the notice, the proposed Final Judgment against Pinnacle and the Competitive Impact Statement, with the amended complaint's Appendix A counted row by row in code.",
  "topic": "The Justice Department's proposed Final Judgment against Pinnacle Property Management Services, which the government places in Frisco, would bar it from third-party rent software fed by nonpublic data or pooled across owners, add a compliance officer, an annual audit and inspections, and binds Pinnacle alone while the case against RealPage and the others continues. Public comment is open for 60 days from the notice.",
  "angle": "Where the rent is set: the software the complaint describes, the Texas landlord the judgment binds, and the route a Texan has to comment before the court rules.",
  "angle_note": "The complaint's description of the software is an allegation and every frame attributes it. The proposed judgment's own definition places Pinnacle in Dallas while the complaint and the impact statement say Frisco, so the deck and caption say the government places it in Frisco. No close date is printed because the impact statement runs the window from the later of two publications.",
  "entities": ["U.S. Department of Justice Antitrust Division", "Pinnacle Property Management Services", "RealPage", "Cushman and Wakefield", "Camden Property Trust", "Willow Bridge Property Company"],
  "places": ["Frisco", "Richardson", "Dallas", "Houston", "Austin", "San Antonio", "Fort Worth", "Collin County"],
  "what_was_refused": "Any claim that the judgment will change a rent Pinnacle charges. Any close date for the comment window. Any statement of the complaint's allegations as findings. Any count of Pinnacle's Texas units, because no fetched record gave one.",
  "keywords": ["RealPage", "Pinnacle", "algorithmic pricing", "rent", "antitrust", "Tunney Act", "proposed final judgment", "Frisco", "Appendix A", "public comment"]
})

artwork["entries"].append({
  "date": DATE, "carousel_no": NO,
  "written_from": "deck_coherence's value track at 432 px and layout_check's accent measurement, both run by this script off the final renders, and the gate suite by exit code.",
  "register": "RENDERED, NOT PRINTED. One nightSodium world declared once in assets/js/deck/2026-09-27-nightrent.js, one garden_apartment hero built in the chassis with five breezeway cores, a leasing storefront and walk pools, the key at azimuth 196 elevation 26, and the storefront's room light the one accent #7FB2D9, carried into the office monitor and the resident's laptop.",
  "structural_laws": [
    "A MOTIF THAT CHANGES STATE NEEDS ONE CAMERA ON BOTH SIDES OF THE CHANGE. Frames 3 and 7 were first built from two cameras and nobody could see the lamps go out. One shared camera made it the deck's turn.",
    "A LIT CORE IS INVISIBLE AT FEED SIZE UNTIL ITS LIGHT REACHES THE GROUND. Wall packs alone read as specks. A pool on the walk under each core is what the thumb sees.",
    "A FIGURE AT THE BUILDING IS A SPECK. Frame 4's resident read only when brought to 30 m from the lens with the building behind.",
    "WOOD GRAIN AND A BRIGHT WINDOW BEHIND TYPE READ AS RULES. The office desk lost its veneer streaks and the storefront glass was dimmed before qa.py passed the dek.",
    "INDOORS THE DECK RIG'S COOL RIM IS A SECOND ACCENT. The kitchen frame warmed and dimmed it."
  ],
  "techniques": [
    "one garden apartment model in the chassis, shot from the lot, from 150 m square on, from across a four lane road and repeated 48 times in five clusters",
    "a canvas screen texture drawn from figures.json on a kit monitor, bands at 30 px per percentage point",
    "two brushed steel columns at 0.25 m per percentage point on base plates, with a standing resident for scale, and the plates left behind on the frame that turns the lamps off",
    "an office and a kitchen built with TXT.interior, with bronze mullions, an under cabinet strip light and spot lights aimed at what they light"
  ],
  "value": {"per_frame_median_L": track, "deck_median_L": med, "max_adjacent_delta": round(max(jumps), 1),
            "mean_adjacent_delta": round(sum(jumps) / len(jumps), 2), "note": "Measured by deck_coherence at 432 px off the final renders."},
  "accent": {"hex": "#7FB2D9", "name": "leasing office screen", "frames_above_floor": acc_frames,
             "note": "The leasing office monitor on 2 and 6 and the resident's laptop on 9. The storefront carries it on 1, 3 and 7 under the floor at that distance."},
  "ground": {"hex": "#171310", "note": "The deck's declared ground."}
})

captions["entries"].append({
  "date": DATE, "carousel_no": NO, "opening_move": "the place", "structure": "Pivot",
  "closing_move": "ask the one question the decision leaves open", "first_line": first_line,
  "words": words, "commas": commas, "commas_per_100w": round(100 * commas / words, 2), "chars": len(cap), "hashtags": hashtags,
  "critic_note": "The critic chose A with four fixes. After review the line placing Pinnacle in Frisco was narrowed from the government's filings to the complaint and the impact statement, because the judgment's own definition says Dallas, and the software limits were given their start, 180 days after the stipulation order is entered.",
  "move_note": "Opens on Frisco and why it is in the case twice, pivots from what the complaint says the software does to what the judgment cuts off, and closes on the question the judgment leaves open for every other landlord."
})

for name, obj in (("topics", topics), ("artwork", artwork), ("captions", captions)):
    (L / f"{name}.json").write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}.json: {len(obj['entries'])} entries, newest {obj['entries'][-1]['date']}")
print(f"caption measured: {words} words, {commas} writer commas, {len(cap)} chars; accent frames {acc_frames}; track {track}")
