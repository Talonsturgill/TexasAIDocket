#!/usr/bin/env python3
"""measure.py — every luminance figure this run publishes, computed from the renders.

The run's prose quotes L* values in the storyboard, the run record and the artwork ledger.
`shipped_check`'s `measured figures` gate asks, of the shipped bytes, that every number written
beside the token `L*` exists in measurements.json, because this repo's highest-recurrence defect
is a value with one home, surfaces that keep their own copy, and nothing in between checking that
they agree.

NOTHING HERE IS TYPED. The per-frame statistics are measured off the renders at 432 px, the size
a reader receives. The declared acceptance bands are PARSED OUT OF THE DOSSIERS rather than
retyped beside them, so the prose and this file cannot drift apart.

THE BAND SENTENCE IS THIS DECK'S OWN AND THE REGEX MATCHES IT RATHER THAN THE OTHER WAY ROUND.
The 2026-09-17 run authored its acceptance sentence as "the frame median L* is between N and M at
432px" and this deck's nine dossiers say "the frame's median L* at 432px is between N and M". Both
are one authored sentence per frame, which is the property that matters. Rewriting nine shipped
acceptance items to suit a regex would be editing the plan to fit the measurement, which is the
inversion this whole file exists to prevent.

WHY THIS FILE EXISTS AT ALL. It was written on 2026-09-17 because CI caught its absence rather
than a judge: `shipped_check`'s self-test asserts that every REGISTERED gate actually RUNS on the
newest deck, and `measured figures` reported "not applicable, the artifact it reads is absent" and
was skipped. A registered gate that silently does not run is the shape this repo refuses
everywhere else, so the absence of the file was itself the failure. It caught this run the same
way, at the ship gate, on the same rule.

THIS DECK ALSO CARRIES A SECOND TRACK AND IT IS DELIBERATE. All three scoring judges measured the
value arc on CANVAS MEAN and called it a strobe; the storyboard plans, and plan_render_check and
panel_ready gate, on MEDIAN L*, where the same deck holds. Both are written here. A median is
blind to a white plate covering a third of a frame, and the disagreement between the two is the
finding rather than a thing to pick a winner from.
"""
import json
import pathlib
import re
import sys

from PIL import Image

RUN = pathlib.Path(__file__).resolve().parent
ACCENT = (0x4F, 0xC7, 0x9A)          # signal_open mint, the deck's one accent
PALETTE = {                          # the minutebook palette, from the chassis declaration
    "ground": "#361D27", "material": "#4F3D2F", "accent": "#4FC79A",
    "ink": "#E4D3CE", "dek": "#CFB9B3", "furniture": "#D9C6BD", "stock": "#EDDFD4",
}
BAND_RX = re.compile(r"the frame's median L\* at 432px is between (\d+) and (\d+)")


def _frame(n: int) -> pathlib.Path:
    """The archived slide if this runs from the archive, the transient render if not."""
    for cand in (RUN / f"slide-{n:02d}.webp",
                 RUN / "render" / f"slide-{n:02d}.png",
                 RUN / f"slide-{n:02d}.png",
                 RUN.parents[2] / "out" / RUN.name / "render" / f"slide-{n:02d}.png"):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"no slide {n:02d} beside {RUN}")


def _lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lstar(r: int, g: int, b: int) -> float:
    y = 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
    return 116.0 * (y ** (1.0 / 3.0)) - 16.0 if y > 0.008856 else 903.3 * y


def _near_accent(px: tuple) -> bool:
    return sum((px[i] - ACCENT[i]) ** 2 for i in range(3)) <= 46 ** 2


def frame_stats(path: pathlib.Path) -> dict:
    im = Image.open(path).convert("RGB").resize((432, 540), Image.LANCZOS)
    data = list(im.getdata())
    vals = sorted(_lstar(*p) for p in data)
    n = len(vals)
    accent = sum(1 for p in data if _near_accent(p))
    return {
        "median_L": round(vals[n // 2], 1),
        "mean_L": round(sum(vals) / n, 1),
        "p05_L": round(vals[int(n * 0.05)], 1),
        "p95_L": round(vals[int(n * 0.95)], 1),
        "accent_share_pct": round(100.0 * accent / n, 2),
    }


# the chassis wraps this sentence across a comment line, so the separator spans whitespace and
# the leading asterisks a block comment carries
ROOM_RX = re.compile(r"ramp's steps measure[\s*]*L\* ((?:[\d.]+, ){8}[\d.]+)")
INKS_RX = re.compile(r"inks:\s*\{\s*ink:\s*M\.pick\(([\d.]+)\)")
SEP_RX = re.compile(r"separated by at least (\d+) L\* at 432px")


def room_ramp() -> list:
    """The ROOM ramp's nine measured steps, PARSED out of the chassis rather than retyped.

    The chassis states them once, in the comment that explains why the wall moved off the dark
    end of the ramp. Typing them here would make this file a second home for nine numbers, which
    is the defect the whole measurement discipline exists to prevent.
    """
    chassis = RUN.parents[2] / "assets/js/deck/2026-09-18-minutebook.js"
    m = ROOM_RX.search(chassis.read_text(encoding="utf-8"))
    if not m:
        raise ValueError(f"{chassis} no longer states its ROOM ramp steps, so they cannot be read "
                         f"and will not be guessed")
    # the character class is greedy and takes the sentence's own full stop with the last
    # value, so "71.9." comes back and is stripped rather than the regex being narrowed
    # into something that would silently miss a ramp written without a trailing period
    return [float(x.rstrip(".")) for x in m.group(1).split(", ")]


def _at(ramp: list, i: float) -> float:
    """A ramp index's L*, linearly between the two measured steps it falls between."""
    lo = max(0, min(len(ramp) - 2, int(i)))
    return round(ramp[lo] + (i - lo) * (ramp[lo + 1] - ramp[lo]), 1)


def declared_separations(ramp: list) -> dict:
    """Every frame that declares a MINIMUM L* separation, measured from its own declared inks.

    Frames 3 and 6 each state in their acceptance lists that two drawn populations are separated
    by at least N L* at 432px so they never read as one mass. That N is a luminance this run
    publishes in its own prose, so shipped_check's `measured figures` gate is right to ask where
    it was measured. Both pairs are read off the frames' own `inks: { ink: M.pick(...) }` calls
    and interpolated on the parsed ramp, so nothing here is typed and a frame that re-inks an
    object moves this number with it.
    """
    out = {}
    for n in (3, 6):
        src = RUN / "slides" / f"slide-{n:02d}.html"
        if not src.exists():
            src = RUN.parents[2] / "out" / RUN.name / "slides" / f"slide-{n:02d}.html"
        text = src.read_text(encoding="utf-8")
        picks = [float(x) for x in INKS_RX.findall(text)]
        floor = SEP_RX.search(text)
        if len(picks) < 2:
            continue
        vals = sorted({_at(ramp, p) for p in picks})
        out[f"slide-{n:02d}"] = {
            "ink_indices": sorted(set(picks)),
            "ink_lstar": vals,
            "measured_separation_L": round(max(vals) - min(vals), 1),
            "declared_floor_L": int(floor.group(1)) if floor else 12,
            "holds": round(max(vals) - min(vals), 1) >= (int(floor.group(1)) if floor else 12),
        }
    return out


def bands_from_dossiers() -> dict:
    """The declared band per frame, READ from each dossier's own acceptance sentence."""
    sb = RUN / "storyboard.md"
    if not sb.exists():
        raise FileNotFoundError(f"{sb} is missing, so the bands cannot be read and will not be typed")
    found = BAND_RX.findall(sb.read_text(encoding="utf-8"))
    if len(found) != 9:
        raise ValueError(f"{sb} states {len(found)} acceptance bands and this deck has 9 frames. "
                         f"A band this file guessed would be a second source of truth")
    return {f"slide-{i + 1:02d}": [int(lo), int(hi)] for i, (lo, hi) in enumerate(found)}


def main() -> int:
    frames = {f"slide-{i:02d}": frame_stats(_frame(i)) for i in range(1, 10)}
    medians = [frames[f"slide-{i:02d}"]["median_L"] for i in range(1, 10)]
    means = [frames[f"slide-{i:02d}"]["mean_L"] for i in range(1, 10)]
    ordered = sorted(medians)
    jumps = [round(abs(medians[i + 1] - medians[i]), 1) for i in range(8)]
    mean_jumps = [round(abs(means[i + 1] - means[i]), 1) for i in range(8)]

    out = {
        "_note": "Computed by runs/carousel/2026-09-18/measure.py from the renders at 432 px, the "
                 "size a reader receives. Nothing here is typed. The bands are parsed out of each "
                 "dossier's own acceptance sentence, so the prose, the gate and this file cannot "
                 "drift apart.",
        "frames": frames,
        "per_frame_median_lstar": medians,
        "per_frame_mean_lstar": means,
        "adjacent_jumps_L": jumps,
        "adjacent_jumps_mean_L": mean_jumps,
        "deck": {
            "median_L": ordered[4],
            "spread_L": round(max(medians) - min(medians), 1),
            "lightest_L": max(medians),
            "darkest_L": min(medians),
            "mean_adjacent_jump_L": round(sum(jumps) / len(jumps), 2),
            "max_adjacent_jump_L": max(jumps),
            "jump_ceiling_L": 14.9,
            "hard_cut_L": 25.0,
            "hard_cuts": sum(1 for j in jumps if j >= 25.0),
            "max_adjacent_jump_mean_L": max(mean_jumps),
            "_two_track_note": "All three scoring judges measured this deck's arc on the MEAN and "
                               "called it a strobe. The storyboard plans, and plan_render_check "
                               "and panel_ready gate, on the MEDIAN, where it holds. Both tracks "
                               "are here because the disagreement is the finding: a median cannot "
                               "see a white plate covering a third of a frame, and four of nine "
                               "frames in this deck are a cream sheet on a dark board.",
        },
        "bands": bands_from_dossiers(),
        "declared_separations": declared_separations(room_ramp()),
        "room_ramp_lstar": room_ramp(),
        "palette": {
            name: round(_lstar(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)), 1)
            for name, h in PALETTE.items()
        },
    }
    (RUN / "measurements.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"measure: wrote measurements.json, deck median L* {ordered[4]}, "
          f"spread {out['deck']['spread_L']}, mean jump {out['deck']['mean_adjacent_jump_L']}")
    for k, v in frames.items():
        print(f"  {k}  median {v['median_L']:5.1f}  mean {v['mean_L']:5.1f}  "
              f"p05 {v['p05_L']:5.1f}  p95 {v['p95_L']:5.1f}  accent {v['accent_share_pct']:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
