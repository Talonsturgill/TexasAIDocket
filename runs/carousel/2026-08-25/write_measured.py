#!/usr/bin/env python3
"""Write every committed measurement from measurements.json and the live gate, never by hand.

Round 4 found three numbers committed twice with two different values: frame 7's falloff (22.1
in the storyboard, 17.2 in artwork.json), the bespoke median (0.1816 in the brief, 0.2465 in the
ledger), and the per frame value array (one set in RUN_RECORD.md, another in artwork.json). On a
product whose first law is that numbers are computed, two files disagreeing about one
measurement is a defect in how they are written, not in either number.

Round 8 found the same class again after a recut moved three frames' luminance, and found the
CAUSE of the recurrence: this script matched the OLD NUMBERS as literal strings, so the moment a
value moved twice the replacement silently stopped firing and every file kept the stale figure
under a script that reported success. Every pattern below matches the SHAPE of the sentence with
`[\\d.-]+` where a number goes, so it fires on any value and cannot go quietly dead. A rewrite
that matches nothing is a hard failure here, not a no-op.
"""
import json, pathlib, re, subprocess, statistics as st
ROOT = pathlib.Path("/home/user/TexasAIDocket")
M = json.loads((ROOT / "out/2026-08-25/measurements.json").read_text())

# The bespoke figure comes from the GATE, by running it, not from a note about it.
p = subprocess.run(["python3", "scripts/carousel/bespoke_check.py",
                    "--slides-dir", "out/2026-08-25/slides"],
                   cwd=ROOT, capture_output=True, text=True)
assert p.returncode == 0, p.stderr
bes = float(re.search(r"median pairwise similarity ([\d.]+)", p.stdout).group(1))
cp = re.search(r"closest pair: (\S+) and (\S+) at ([\d.]+)", p.stdout)
pair = [cp.group(1), cp.group(2), float(cp.group(3))]

med = M["per_frame_median_lstar"]
inside = M["frames_inside_declared_band"]
lo, hi = M["band_declared"]
fall = M["frame7_falloff_lstar"]
f6 = M["frame6"]
gut = M["frame7_repeat_gutters"]
WORD = "zero one two three four five six seven eight nine".split()
def w(i): return WORD[i] if 0 <= i < len(WORD) else str(i)
rank = sorted(range(9), key=lambda i: -med[i])          # brightest first, 0 based
def brighter_than(i):
    """The frames measurably brighter than frame i+1, named as the record names them."""
    return [k + 1 for k in rank if med[k] > med[i]]
def names(fs):
    if len(fs) == 1: return f"frame {fs[0]}"
    return "frames " + " and ".join([", ".join(str(f) for f in fs[:-1]), str(fs[-1])])

SUBS = []                                # (path, pattern, replacement) applied and COUNTED
def sub(path, pat, rep, n=1):
    SUBS.append((path, pat, rep, n))

# ---- artwork.json ------------------------------------------------------------------
ap = ROOT / "ledger/carousel/artwork.json"
A = json.loads(ap.read_text())
e = [x for x in A["entries"] if x["date"] == "2026-08-25"][0]
v = e["value"]
v["per_frame_median_L"] = med
v["deck_median_L"] = M["deck_median"]
v["mean_L"] = round(st.mean(med), 1)
v["sd_L"] = M["deck_sd"]
v["range_L"] = [min(med), max(med)]
v["frames_inside_declared_band"] = len(inside)
v["frame7_falloff_L"] = fall
v["frame7_repeat_gutters_L"] = M["frame7_repeat_gutters"]
v["biggest_junction"] = M["biggest_junction"]
v["measured_by"] = "out/2026-08-25/tmp/measure.py over the rendered PNGs at 216x270"
v["counted_by"] = ("out/2026-08-25/tmp/write_measured.py, over the array above. EVERY sentence "
                   "in this entry that carries one of these numbers is composed from it here "
                   "rather than typed beside it, because round 4 found this deck's falloff and "
                   "its bespoke median each committed twice with two different values.")
e["bespoke_median_similarity"] = bes
e["bespoke_closest_pair"] = pair
e["register"] = (
    f"a Texas notice case seen nine ways, wide range about a median of {M['deck_median']}. "
    f"Anodized rail, dark case interior and cream bond carry through six of the nine frames as "
    f"one object under changing light and camera. Measured against the mid value deck its own "
    f"storyboard declared, {w(len(inside))} of the nine sits inside the L* {lo} to {hi} band that "
    f"plan set, and the frames run {min(med)} to {max(med)}.")
e["techniques"] = [
    re.sub(r"brightening [\d.]+ L\* from first to last",
           f"brightening {fall} L* from first to last", t)
    for t in e["techniques"]]
ap.write_text(json.dumps(A, indent=1, ensure_ascii=False) + "\n")

# ---- storyboard.md ----------------------------------------------------------------
SB = "out/2026-08-25/storyboard.md"
j67 = M["junctions"][5]
sub(SB, r"measured, it is [\d.]+ and frame 7 immediately after it is [\d.]+, a [\d.]+ L\* drop",
        f"measured, it is {med[5]} and frame 7 immediately after it is {med[6]}, a "
        f"{abs(j67)} L* drop")
sub(SB, r"It is not the brightest frame in the deck, frames? [\d and,]*\d(?:,)? (?:is|are),",
        f"It is not the brightest frame in the deck, {names(brighter_than(5))} "
        f"{'is' if len(brighter_than(5)) == 1 else 'are'},")
sub(SB, r"L\*, and the frame's field at [\d.]+ is [\d.]+ L\* under frame 6 before it\. It is not the deck's\n"
        r"    darkest field, frame 3 at [\d.]+ is,",
        f"L*, and the frame's field at {med[6]} is {abs(j67)} L* under frame 6 before it. It is not the deck's\n"
        f"    darkest field, frame 3 at {med[2]} is,")
sub(SB, r"Measured it is [\d.]+, with frames 7 and 9 at [\d.]+ and [\d.]+ either side, so it\n"
        r"    is the BRIGHTEST of the deck's last three\.",
        f"Measured it is {med[7]}, with frames 7 and 9 at {med[6]} and {med[8]} either side, so "
        f"it\n    is the BRIGHTEST of the deck's last three.")
sub(SB, r"\b22\.1 L\*", f"{fall} L*", n=0)               # optional legacy form

# ---- RUN_RECORD.md ----------------------------------------------------------------
RR = "runs/carousel/2026-08-25/RUN_RECORD.md"
bj = M["biggest_junction"]
sub(RR, r"Per frame median L\\\*: [\d., ]+\. Deck median [\d.]+, sd\n[\d.]+\. The biggest junction "
        r"is [-\d.]+ between frames\n\d+ and \d+\. Frame 7's falloff\nmeasures [\d.]+ L\\\* in the "
        r"gutters between its four repeat lines\. Frame 6's\ncards read [\d.]+ against cork at "
        r"[\d.]+\.",
        f"Per frame median L\\*: {', '.join(str(x) for x in med)}. Deck median {M['deck_median']}, sd\n"
        f"{M['deck_sd']}. The biggest junction is {bj['delta']} between frames\n"
        f"{bj['between']} and {bj['between'] + 1}. Frame 7's falloff\n"
        f"measures {fall} L\\* in the gutters between its four repeat lines. Frame 6's\n"
        f"cards read {f6['card_a']} against cork at {f6['cork_under']}.")
sub(RR, r"Measured medians, frame by frame, are [\d., ]+ and [\d.]+,\nwith a median of medians of "
        r"[\d.]+ and a range of [\d.]+ L\\\*\. \w+ frames? sits? inside the declared band\nand "
        r"\w+ do(?:es)? not\.",
        f"Measured medians, frame by frame, are {', '.join(str(x) for x in med[:-1])} and {med[-1]},\n"
        f"with a median of medians of {M['deck_median']} and a range of "
        f"{round(max(med) - min(med), 1)} L\\*. {w(len(inside)).capitalize()} frame"
        f"{'' if len(inside) == 1 else 's'} sit{'s' if len(inside) == 1 else ''} inside the "
        f"declared band\nand {w(9 - len(inside))} do not.")
sub(RR, r"Measured, 6 is now [\d.]+ and 7 is [\d.]+\.",
        f"Measured, 6 is now {med[5]} and 7 is {med[6]}.")
sub(RR, r"span [\d.]+ L\\\* rather than a field the eye read as flat\.",
        f"span {fall} L\\* rather than a field the eye read as flat.")
sub(RR, r"Measured after the rebuild it is [\d.]+ L\\\*, monotonic, [\d.]+ to [\d.]+\.",
        f"Measured after the rebuild it is {fall} L\\*, monotonic, {gut[0]} to {gut[-1]}.")

# ---- apply, and REFUSE to pass on a pattern that matched nothing --------------------
dead, applied = [], 0
for path, pat, rep, n in SUBS:
    f = ROOT / path
    txt = f.read_text()
    new, cnt = re.subn(pat, rep, txt)
    if cnt == 0 and n:
        dead.append((path, pat[:74]))
    applied += cnt
    if cnt:
        f.write_text(new)
if dead:
    for path, pat in dead:
        print(f"DEAD PATTERN  {path}  /{pat}/")
    raise SystemExit("a measurement rewrite matched nothing. That is how the stale numbers "
                     "shipped last time: the script reported success over a file it never "
                     "touched. Fix the pattern or the sentence, do not ignore this.")

print(json.dumps({"per_frame": med, "deck_median": M["deck_median"], "sd": M["deck_sd"],
                  "inside_band": inside, "frame7_falloff": fall, "frame6": f6,
                  "bespoke_median": bes, "closest_pair": pair,
                  "rewrites_applied": applied}, indent=1))
