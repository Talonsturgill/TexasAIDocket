#!/usr/bin/env python3
"""deck_coherence.py — measure whether the nine RENDERED frames read as one deck.

WHY THIS EXISTS (2026-09-16, owner). "all the slides don't really flow together."

`deck_chassis.py` reads the SOURCE and proves the nine frames were cut from one piece of stock.
This reads the PIXELS and proves they came out that way. Both are needed and neither substitutes
for the other, which is GATE_LESSONS' oldest shape: a rule stated in config, a surface that keeps
its own copy, and nothing in between checking they agree.

WHAT IT MEASURES, and the thresholds are DATA in `config/carousel/deck_coherence.json`, derived
from a corpus rather than chosen:

    value track        each frame's MEDIAN L*, in slide order. Nine numbers, and the deck's
                       whole flow problem lives in the differences between them
    mean adjacent jump the strobe measure. The reference product's median deck moves 2.6 L*
                       between adjacent frames. This product's median deck moved 21.0
    hard cuts          adjacent pairs more than 25 L* apart. Ninety percent of reference decks
                       carry at most one. Not one of this product's nineteen decks did

THE SCORER WAS READING THIS BACKWARDS, which is why it never surfaced. On 2026-09-16 the craft
judge wrote "a genuine value arc (measured 77.8, 77.5, 51.0, 34.1, 45.9, 20.8, 77.5, 43.5, 13.0;
spread 64.8)" and gave the deck credit for it. Frame 6 to frame 7 is a 57 point jump in one
swipe, back to near white from near black, and then down again. That is not an arc, it is a
sawtooth, and the rubric rewarded its amplitude because nothing measured ADJACENCY. A spread is
a property of a set. A deck is a sequence.

WHAT THIS IS NOT. It is not a rule that a deck must be flat. One hard cut is allowed and is the
deck's turn, and the deck says in its storyboard where that turn is, so the cut is a decision
somebody made rather than a thing that happened. Undeclared is a fail even at one.

EXIT CODES
    0  the nine frames read as one deck
    1  a violation, or the checker was called wrongly
    2  the checker itself broke

RUN IT BY EXIT CODE, never by reading the last line.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / "config" / "carousel" / "deck_coherence.json"

# The measurement is taken at this size. Small enough that it is the deck's MASSES being
# measured and not its detail, which is the same reason a painter squints at a canvas.
SAMPLE = (216, 270)


def load_config(path: Path = CONFIG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["thresholds"]


def median_lstar(path: Path) -> float:
    """A frame's median L*, the value a reader sees when the frame is a thumbnail."""
    import numpy as np
    from PIL import Image

    im = Image.open(path).convert("RGB").resize(SAMPLE)
    a = np.asarray(im).astype(np.float64) / 255.0
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    Y = lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722
    L = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
    return float(np.median(L))


def frames_in(render_dir: Path) -> list[Path]:
    """The nine frames in slide order, whatever the engine happened to write."""
    for pat in ("slide-*.png", "slide-*.webp", "slide-*.jpg"):
        got = sorted(p for p in render_dir.glob(pat) if "thumb" not in p.name)
        if got:
            return got
    return []


def declared_cuts(storyboard: Path | None) -> set[int]:
    """Which frame a declared hard cut lands ON, read from the storyboard.

    The declaration is one line the storyboard carries for the frame that turns:

        VALUE CUT: frame 6

    A set rather than a single value because a storyboard may carry the line once per frame it
    applies to, and because an empty set is the honest answer when there is no storyboard.
    """
    if not storyboard or not storyboard.exists():
        return set()
    text = storyboard.read_text(encoding="utf-8", errors="replace")
    return {int(m) for m in re.findall(r"VALUE\s+CUT\s*:\s*frame\s+(\d+)", text, re.I)}


def measure(render_dir: Path, storyboard: Path | None = None,
            cfg: dict | None = None) -> dict:
    cfg = cfg or load_config()
    files = frames_in(render_dir)
    if len(files) < 2:
        return {"error": f"need at least 2 frames in {render_dir}, found {len(files)}"}

    track = [median_lstar(f) for f in files]
    jumps = [abs(track[i + 1] - track[i]) for i in range(len(track) - 1)]
    hard_t = cfg["hard_cut_Lstar"]["value"]
    # A jump between frame i and i+1 is attributed to frame i+2 in one-based slide numbers,
    # because the cut is what the reader meets when they arrive at that frame.
    cuts = [(i + 2, round(j, 1)) for i, j in enumerate(jumps) if j > hard_t]

    mean_jump = sum(jumps) / len(jumps)
    declared = declared_cuts(storyboard)

    problems: list[str] = []
    ceiling = cfg["mean_adjacent_jump_Lstar"]["max"]
    if mean_jump > ceiling:
        problems.append(
            f"the deck strobes. Mean adjacent value jump is {mean_jump:.1f} L* against a ceiling "
            f"of {ceiling} ({cfg['mean_adjacent_jump_Lstar']['from']}). The reference product's "
            f"median deck moves 2.6. Hold one ground across the deck and let the SUBJECT change, "
            f"not the stock")

    max_cuts = cfg["max_hard_cuts"]["max"]
    if len(cuts) > max_cuts:
        where = ", ".join(f"frame {n} ({d} L*)" for n, d in cuts)
        problems.append(
            f"{len(cuts)} hard cuts against a ceiling of {max_cuts}: {where}. One cut is the "
            f"deck's turn. Two or more is a strobe, and every deck this product shipped had at "
            f"least two")

    if cfg.get("declared_cut_required"):
        for n, d in cuts:
            if n not in declared:
                problems.append(
                    f"frame {n} arrives on a {d} L* cut that the storyboard never declared. "
                    f"Write 'VALUE CUT: frame {n}' in the storyboard if it is the turn, or hold "
                    f"the value if it is not. A cut is a decision somebody makes, never a thing "
                    f"that happens")

    return {
        "render_dir": str(render_dir),
        "frames": [f.name for f in files],
        "value_track": [round(v, 1) for v in track],
        "adjacent_jumps": [round(j, 1) for j in jumps],
        "mean_adjacent_jump": round(mean_jump, 2),
        "spread": round(max(track) - min(track), 1),
        "hard_cuts": cuts,
        "declared_cuts": sorted(declared),
        "problems": problems,
        "ok": not problems,
    }


def report(m: dict) -> int:
    if "error" in m:
        print(f"deck_coherence: {m['error']}", file=sys.stderr)
        return 1
    print(f"deck_coherence: value track {m['value_track']}")
    print(f"                jumps {m['adjacent_jumps']}  mean {m['mean_adjacent_jump']}  "
          f"spread {m['spread']}")
    if m["ok"]:
        print(f"deck_coherence: ok, {len(m['frames'])} frames read as one deck")
        return 0
    print(f"\ndeck_coherence: FAIL, {len(m['problems'])} problem(s)\n", file=sys.stderr)
    for p in m["problems"]:
        print(f"  - {p}", file=sys.stderr)
    print("\n  config/carousel/deck_coherence.json carries the derivation of every threshold "
          "above.", file=sys.stderr)
    return 1


# --------------------------------------------------------------------------- self test

def self_test() -> int:
    """Replays the 2026-09-16 deck and the reference decks it was measured against.

    Runs on synthetic tracks rather than rendered images, because what is under test is the
    JUDGEMENT and not the luminance maths, and a self-test that needs nine PNGs is a self-test
    that stops being run.
    """
    cfg = load_config()
    fails = []

    def judge(track: list[float], declared: set[int]) -> list[str]:
        jumps = [abs(track[i + 1] - track[i]) for i in range(len(track) - 1)]
        hard_t = cfg["hard_cut_Lstar"]["value"]
        cuts = [(i + 2, round(j, 1)) for i, j in enumerate(jumps) if j > hard_t]
        out = []
        if sum(jumps) / len(jumps) > cfg["mean_adjacent_jump_Lstar"]["max"]:
            out.append("strobes")
        if len(cuts) > cfg["max_hard_cuts"]["max"]:
            out.append("hard cuts")
        for n, _ in cuts:
            if n not in declared:
                out.append(f"undeclared cut at {n}")
        return out

    def case(label, track, declared, want_fail):
        got = judge(track, declared)
        if want_fail and not got:
            fails.append(f"{label}: expected a refusal, deck passed")
        if not want_fail and got:
            fails.append(f"{label}: expected a pass, got {got}")

    # The deck that prompted this file, measured off its own shipped renders.
    case("2026-09-16, the deck the owner complained about",
         [77.8, 77.5, 51.0, 34.1, 45.9, 20.8, 77.5, 43.5, 13.0], set(), True)
    # The worst Texas deck measured, 2026-09-15.
    case("2026-09-15, light dark light dark",
         [8.6, 90.4, 10.1, 8.6, 87.2, 18.8, 70.7, 92.9, 9.5], set(), True)
    # A reference deck that holds one ground the whole way, 2026-08-07.
    case("a reference deck holding one ground",
         [3.3, 2.7, 8.5, 2.9, 2.6, 1.9, 5.6, 6.1, 2.2], set(), False)
    # One declared turn is legitimate.
    case("one DECLARED cut is the deck's turn",
         [8.0, 7.2, 9.1, 8.8, 62.0, 60.4, 58.9, 61.2, 59.0], {5}, False)
    # The same deck with the turn undeclared is not.
    case("the same cut undeclared is a fail",
         [8.0, 7.2, 9.1, 8.8, 62.0, 60.4, 58.9, 61.2, 59.0], set(), True)
    # Two cuts is a strobe however they are declared.
    case("two cuts is a strobe even when declared",
         [8.0, 7.5, 62.0, 60.0, 9.0, 8.4, 9.9, 8.1, 7.6], {3, 5}, True)
    # A gentle ramp across the whole deck is a palette arc and is allowed.
    case("a gentle ramp across nine frames is allowed",
         [8.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0], set(), False)

    if fails:
        print(f"deck_coherence --self-test: FAIL, {len(fails)} case(s)", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("deck_coherence --self-test: ok, 7 cases")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--render-dir", help="the directory holding the rendered frames")
    ap.add_argument("--date", help="shorthand for runs/carousel/<date>")
    ap.add_argument("--storyboard", help="where the VALUE CUT declaration lives")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    sb = Path(a.storyboard) if a.storyboard else None
    if a.date and not a.render_dir:
        a.render_dir = str(REPO_ROOT / "runs" / "carousel" / a.date)
        if sb is None:
            sb = REPO_ROOT / "runs" / "carousel" / a.date / "storyboard.md"
    if not a.render_dir:
        print("deck_coherence: need --render-dir or --date", file=sys.stderr)
        return 1

    rd = Path(a.render_dir)
    if not rd.is_dir():
        print(f"deck_coherence: no such directory {rd}", file=sys.stderr)
        return 1

    m = measure(rd, sb)
    if a.json:
        print(json.dumps(m, indent=1))
        return 0 if m.get("ok") else 1
    return report(m)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                    # pragma: no cover
        print(f"deck_coherence: the gate itself broke: {exc}", file=sys.stderr)
        sys.exit(2)
