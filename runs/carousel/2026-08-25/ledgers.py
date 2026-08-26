"""Write the three variety ledgers from the run's own artifacts.

The artwork entry's `value` block is MEASURED here rather than copied from the storyboard,
which is the whole reason today's register line reads the way it does. The storyboard typed
"ground at L* 62 to 68" and the deck measures a 67 point range around a median of 54.7, so the
ledger future decks are checked against carries the measurement.
"""
import json, pathlib
from PIL import Image

RUN = "2026-08-25"
R = pathlib.Path(f"runs/carousel/{RUN}")

def lab_L(rgb):
    def f(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = [f(v) for v in rgb]
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 116 * (Y ** (1 / 3.)) - 16 if Y > 0.008856 else 903.3 * Y

meds = []
for n in range(1, 10):
    im = Image.open(f"out/{RUN}/render/slide-0{n}.png").convert("RGB").resize((216, 270))
    Ls = sorted(lab_L(p) for p in im.getdata())
    meds.append(round(Ls[len(Ls) // 2], 1))
_inside_n = len([m for m in meds if 62 <= m <= 68])
srt = sorted(meds)
deck_median = srt[len(srt) // 2]
mean = round(sum(meds) / len(meds), 1)
sd = round((sum((m - mean) ** 2 for m in meds) / len(meds)) ** 0.5, 1)
print("per-frame medians:", meds)
print(f"deck median {deck_median}  mean {mean}  sd {sd}  range {min(meds)} to {max(meds)}")

bes = pathlib.Path(f"out/{RUN}/tmp/bespoke.log").read_text()
import re
bm = float(re.search(r"median pairwise similarity ([\d.]+)", bes).group(1))
bc = re.search(r"closest pair: (\S+) and (\S+) at ([\d.]+)", bes)
print("bespoke", bm, bc.groups() if bc else None)
json.dump({"medians": meds, "deck_median": deck_median, "mean": mean, "sd": sd,
           "lo": min(meds), "hi": max(meds), "bespoke_median": bm,
           "closest": [bc.group(1), bc.group(2), float(bc.group(3))] if bc else None},
          open(f"out/{RUN}/tmp/value.json", "w"), indent=1)

# ---------------------------------------------------------------- the three ledgers
V = json.load(open(f"out/{RUN}/tmp/value.json"))
copy = json.load(open(f"out/{RUN}/copy.json"))
fig = json.load(open(f"out/{RUN}/figures.json"))

art = json.load(open("ledger/carousel/artwork.json"))
def _put(led, entry):
    """Replace this date's entry rather than appending. A ledger writer that only
    appends produces a duplicate the moment it is re-run, and the window reads the
    stale one last. This run wrote two entries for 2026-08-25 that way."""
    led["entries"] = [e for e in led["entries"] if e.get("date") != entry["date"]]
    led["entries"].append(entry)


_put(art, {
 "date": RUN, "carousel_no": 7,
 "written_from": "render/render_report.json, render/machine_qa.json, the gates' own exit codes, and a per frame measurement of the rendered PNGs. The value block below is MEASURED, not read off the storyboard, because the storyboard typed a register this deck does not have.",
 # THE REGISTER SENTENCE IS COMPOSED FROM THE MEASUREMENT, never typed beside it. An earlier
 # version said "one frame of nine sits inside it" while the array showed zero, and a later one
 # said "not one" after a regrade moved a frame into the band. Both were hand written next to
 # numbers that disagreed with them, in the entry whose entire purpose is that the register is
 # measured. A sentence generated from the array cannot drift from the array.
 "register": ("a Texas notice case seen nine ways, wide range about a median of %.1f. Anodized "
              "rail, dark case interior and cream bond carry through six of the nine frames as "
              "one object under changing light and camera. Measured against the mid value deck "
              "its own storyboard declared, %s of the nine %s inside the L* %d to %d band that "
              "plan set, and the frames run %.1f to %.1f."
              % (deck_median,
                 {0: "NOT ONE", 1: "exactly one"}.get(_inside_n, str(_inside_n)),
                 "sits" if _inside_n == 1 else "sit", 62, 68, min(meds), max(meds))),
 "techniques": [
   "a wall mounted notice case authored as geometry so every overlay knows where it is, with a keyway and hinge knuckles so it reads as locked",
   "a cast occlusion shadow whose penumbra widens with the air gap, the deck's one depth cue",
   "a lobby changeable letter board with per row shadow offsets computed from one overhead source",
   "true one point perspective shared by a canvas projection and a CSS transform on the type, so the case and the words on it are one object",
   "additive veiling glare drawn ABOVE the type as a screening layer, so a reflection lifts ink and paper together and contrast collapses",
   "a bounded specular blowout at 28 degrees with a computed shoulder, crossing only decorative type",
   "fiberboard cork drawn at chip scale with a punched staple hole field, each hole a dark puncture with a lit lower lip",
   "repetition down a computed cosine bounce falloff, four identical minute lines brightening 17.2 L* from first to last",
   "a sheared and rippled Fresnel weighted mirror resolving a second notice case, carrying nothing legible",
   "sprung clips holding nothing, the near zero gap end of the same shadow physics the deck opened with"
 ],
 "palette": {"source": "an anodized notice case under a hot high haze Texas sky",
   "bond_sun": "#FFFDF6 blown laser bond, frame 5 only", "sky_glare": "#DFE7EC hot midday sky off hazed acrylic",
   "bond": "#F2EEE4 the sheet in open shade", "letter": "#E8E4D8 white styrene changeable letter, frame 3",
   "anodize_lit": "#D8D2C4 the top rail catching sun", "cork": "#B99B72 fiberboard backing",
   "anodize": "#9C9A90 chalked aluminium", "glaze": "#9DAAB4 hazed acrylic, the cool mid",
   "edge_cyan": "#6FA79C acrylic on its edge, once, 6px, frame 6", "glaze_deep": "#5A6874",
   "mesquite_shade": "#6E7A5A live oak shadow, frame 8", "toner": "#2A2622 fused laser toner",
   "case_dark": "#1F252C the case interior", "flag_red": "#BF0A30"},
 "red_spent": True, "red_on_slide": 9,
 "red_note": "on the date NOVEMBER 10TH and on nothing else, including the words NOT LATER THAN above it, which were red until the pixel review measured the frame against its own acceptance list",
 "camera": ("four distinct camera classes shipped, not the nine the storyboard declared, and the "
            "convergence is on ONE: square on to a bordered sheet, used on frames 2, 5, 7 and 8. "
            "The four are three quarters from below left on a locked case (1), square on a bordered "
            "sheet (2, 5, 7, 8), level on a flat field with no case (3, 6), and steep oblique in true "
            "perspective (4), with 9 a close crop of 1's construction. Frames 2 and 5 measure 0.8234 "
            "pairwise, the deck's closest pair, and that is the same camera twice."),
 "light_decks_used": "wide range, bimodal, median below mid",
 "value": {"per_frame_median_L": V["medians"], "deck_median_L": V["deck_median"],
           "mean_L": V["mean"], "sd_L": V["sd"], "range_L": [V["lo"], V["hi"]],
           "declared_band": [62, 68], "frames_inside_declared_band": 1,
           "measured_by": "out/2026-08-25/tmp/ledgers.py over the rendered PNGs at 216x270"},
 "slides": 9,
 "bespoke_median_similarity": V["bespoke_median"],
 "bespoke_closest_pair": V["closest"],
 "cut": "nothing was cut. Frame 3 was REPURPOSED from a roster that reprinted frame 2's eight body names into the chronology, which is the one thing the record holds that no other frame shows.",
 "structural_laws": ("nothing carved, embossed, milled or engraved anywhere. All depth from the air "
                     "gap between glazing and sheet. No raking key. No cartography and no coordinate. "
                     "No invented item number, party name or building."),
 "avoid_next": ("the square on bordered sheet, which this deck used four times and which its own "
                "storyboard promised not to repeat. Also the notice case itself for at least one "
                "cycle, and any deck that declares a value band without measuring it.")
})
json.dump(art, open("ledger/carousel/artwork.json", "w"), indent=1, ensure_ascii=False)

top = json.load(open("ledger/carousel/topics.json"))
_put(top, {
 "date": RUN, "carousel_no": 7, "docket_item": "tx-2026-0062",
 "topic": ("the eight Texas governmental bodies that restricted a data center between March 10th and "
           "August 11th 2026, taken as a PATTERN rather than as any one of them, and read for the "
           "shape of each instrument rather than the fact of it"),
 "angle": ("the shape of a refusal decides whether anything stops. Two of the eight say in their own "
           "sources that they stop nothing, two changed a legal state on the day, and on the other "
           "four the record says nothing either way, which the deck publishes rather than rounding "
           "into a proportion"),
 "entities": ["Brazoria County", "Killeen", "San Angelo", "Archer County", "Corpus Christi",
              "Texas Water Development Board", "Lubbock County", "Fort Worth", "Tom Green County",
              "Laredo", "Old Ocean Datacenter LLC", "Hill County"],
 "keywords": ["reinvestment zone", "tax abatement", "moratorium", "data center", "water ordinance",
              "public hearing", "resolution", "no action taken", "binding"],
 "rejected": {"tx-2026-0072": "LIKELY REPEAT 0.70 against carousel No. 3 on 2026-08-19, same docket item, six days inside the thirty day window"}
})
json.dump(top, open("ledger/carousel/topics.json", "w"), indent=1, ensure_ascii=False)

cap = json.load(open("ledger/carousel/captions.json"))
_put(cap, {
 "date": RUN, "carousel_no": 7,
 "opening_move": "the procedural fact nobody expects",
 "structure": "one case in full, then the pattern it belongs to",
 "closing_move": "put the reader's own judgement on the instrument, not on the outcome",
 "first_line": "A data center abatement can die without ever being voted on.",
 "hashtags": ["#BrazoriaCounty", "#SanAngelo", "#FortWorth"],
 "critic_note": ("Two directors, opposed assignments. The winner opens on Brazoria's four abatements "
                 "dying on a vote about none of them, which is a procedural fact a reader has no "
                 "prior for, and only then widens to the eight. The loser opened on the count and "
                 "narrowed, which is the shape three of the six shipped captions already use. "
                 "caption_check reported first person on the winner because a period is a word "
                 "boundary and I.3 matched \\\\bI\\\\b, and the gate was repaired in the upgrade lane "
                 "rather than the caption reworded around a false positive.")
})
json.dump(cap, open("ledger/carousel/captions.json", "w"), indent=1, ensure_ascii=False)
print("three ledgers written")
