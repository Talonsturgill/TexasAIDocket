#!/usr/bin/env python3
"""value_register.py — the faded look, measured off the frames, before a critic sees them.

    python3 scripts/carousel/value_register.py --render-dir out/<date>/render --probe --date <date>
    python3 scripts/carousel/value_register.py --render-dir out/<date>/render --date <date>
    python3 scripts/carousel/value_register.py --run runs/carousel/<date>
    python3 scripts/carousel/value_register.py --self-test

WHY THIS EXISTS

The owner, on October 4th, beside the sibling product's deck of the same morning, quoted in full
in knowledge/carousel/ILLUSTRATION_SYSTEM.md, THE STAGE: the sibling's art "wows me ... It's more
like bold. The Texas one, it's okay, but it's just more like faded colors and stuff."

Faded is a measurement, and it is not the one anybody guessed. Measured on every shipped frame of
the ten Texas decks from September 24th to October 4th and the twelve sibling decks from September
24th to October 5th, at 432 by 540 in CIE L* (measure_shipped.lstar), the colour is not the
difference: mean chroma was 11.5 here and 8.4 there. The VALUE is.

    share of the frame       Texas, 10 decks    sibling, 12 decks
    mid tones, L* 30 to 70        0.418              0.131
    near black, L* under 15       0.188              0.610
    deck median L*                 32.6               12.8

A Texas frame lived in the middle of the scale and a sibling frame lived at its ends: a dark field,
one lit thing, one bright edge. The cause was in the doctrine and the engine, not in any one run.
From September 24th the routine ordered "a photograph of a place at a time of day ... haze in the
distance", the daylight worlds fogged every ground toward a bright horizon haze, and chassis were
allowed a pale wash up to 0.55 over the art. Carousel no. 42 lifted the top of every frame by 0.35
and the bottom by 0.45 and shipped 0.698 of its pixels in the mid tones.

It also cost the run 44 minutes. That deck measured a median of L* 68.0, over the light deck line,
in a window that had already spent its one light deck on no. 38, and `ledger_check` only found out
at ship, after three panel rounds, so all nine frames were exposed down and judged again. This
gate asks both questions on the PROBE frame, in the first minute of the art build.

WHAT IT CHECKS

1. A probe frame: its mid tone share is at most PROBE_MID. Over the 107 sibling frames 2 exceed it
   (1.9 percent), both on the one deck of the twelve that was mostly snow plain. Over the 90 Texas
   frames 30 do.
2. A deck: the mean mid tone share of its frames is at most DECK_MID. All 12 sibling decks are
   under it (the highest 0.324) and 8 of the 10 Texas decks are over it (the lowest of those 0.406).
   The two that pass are the two darkest worlds Texas shipped, nightSodium on September 27th
   (0.143) and blueHour on September 26th (0.220).
3. The light deck cap, looked ahead. A frame or deck whose median reaches ledger_check's LIGHT_L,
   in a window of the seven previous decks that already holds LIGHT_CAP light decks, fails now
   rather than at ship.

What it does NOT check is taste. A deck can pass this and still be weak. It removes one measured
cause of weak, the one the owner named, and the critics and the panel judge the rest.

THE CURE is never a darker grade over the same frame, which only crushes a mid tone into a muddier
one. It is the world and the light: a staged world (`lastLight` or `floodlit` in txthree.js,
TXT.stage), a subject that fills the frame, the type on the dark field, and no pale wash over the
art. ILLUSTRATION_SYSTEM.md, THE BOLD TEST, is the doctrine.

The shipped-check adapter measures and reports decks dated on or before VALUE_SINCE without
failing them, because they were drawn under the earlier doctrine. Direct invocations still
return the measured result, including the historical calibration fixtures.

LOOK V2 (owner, November 14th, 2026: "make it 10x better, the artwork on the carousels is nowhere
near the quality it needs to be"). The staged dark world this gate pushed every deck into measured,
on the shipped Nov 14 deck, a median L* of 5.6, 0.62 of its pixels near black and a median chroma
of 2.2, and TikTok viewers gave it under 3 seconds. Lightness alone was the wrong axis: "faded" was
never mid tones, it was mid tones WITHOUT colour. The October 4th deck the owner called faded holds
0.62 of its pixels at L* 30 to 70 with chroma under 18; the look v2 proof of the Nov 14 story holds
0.04 there and 0.54 of its pixels at chroma 30 or more.

So for a run dated on or after config/carousel/look.json `v2_from` (or `--look v2`) the register is:
  1. GREY MID: the share of a frame at L* 30 to 70 with C* under GREY_C is at most V2_PROBE_GREY on a
     probe frame and V2_DECK_GREY on the deck mean. This is the faded look, measured on the right axis.
  2. VIVID: the share at C* V2_VIVID_C or more is at least V2_PROBE_VIVID on a probe frame and
     V2_DECK_VIVID on the deck mean. Colour is required, not tolerated.
  3. NO BLACK ROOM: the share under L* DARK is at most V2_FRAME_DARK on any frame and V2_DECK_DARK on
     the deck mean. A v2 frame shades toward its tone's violet or navy, never black.
  4. The light deck cap is unchanged.
Runs before v2_from keep the rules above exactly.

EXIT CODES: 0 within the register, 1 outside it or nothing to measure.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import measure_shipped as ms  # noqa: E402

REPO_ROOT = HERE.parents[1]
ARTWORK = REPO_ROOT / "ledger" / "carousel" / "artwork.json"

MID_LO, MID_HI = 30.0, 70.0   # the mid tones, in L*
DARK = 15.0                   # near black, in L*
PROBE_MID = 0.50              # the most of one probe frame that may sit in the mid tones
DECK_MID = 0.35               # the most of a deck, on the mean of its frames
VALUE_SINCE = "2026-10-07"    # last shipped deck before the staged-world upgrade reached main

# LOOK V2 (2026-11-14), calibrated on the Oct 4 faded deck (grey mid 0.62), the Nov 13 and 14 dark decks
# (near black 0.72 and 0.62, vivid 0.04 and 0.02) and the look v2 proof of Nov 14 (grey mid 0.04 mean,
# 0.14 worst frame; vivid 0.54 mean, 0.28 lowest; near black 0.04 mean, 0.08 worst)
GREY_C = 18.0                 # chroma under which a mid tone is grey
V2_VIVID_C = 30.0             # chroma at or over which a pixel is vivid
V2_PROBE_GREY = 0.30
V2_DECK_GREY = 0.20
V2_PROBE_VIVID = 0.20
V2_DECK_VIVID = 0.30
V2_FRAME_DARK = 0.25
V2_DECK_DARK = 0.12
LOOK_CONFIG = REPO_ROOT / "config" / "carousel" / "look.json"


def v2_from(path: Path = LOOK_CONFIG) -> str | None:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("v2_from") or None
    except (OSError, ValueError):
        return None


def is_v2(date: str | None, look: str | None = None) -> bool:
    """A look v2 run: named so by `--look`, or dated on or after look.json's v2_from."""
    if look:
        return look == "v2"
    start = v2_from()
    return bool(date and start and date >= start)


def lab_lc(rgb):
    """CIE L* and C*ab of an sRGB array, D65."""
    s = np.asarray(rgb, float) / 255.0
    s = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = s @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return 116 * f[..., 1] - 16, np.hypot(500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2]))


def frame_stats(path: Path) -> dict:
    rgb = np.asarray(Image.open(path).convert("RGB").resize(ms.AT, Image.BOX), float)
    lum = ms.lstar(rgb)
    _, chroma = lab_lc(rgb)
    mid = (lum >= MID_LO) & (lum <= MID_HI)
    return {"frame": path.name,
            "median_L": round(float(np.median(lum)), 1),
            "mid": round(float(mid.mean()), 3),
            "dark": round(float((lum < DARK).mean()), 3),
            "grey_mid": round(float((mid & (chroma < GREY_C)).mean()), 3),
            "vivid": round(float((chroma >= V2_VIVID_C).mean()), 3),
            "median_C": round(float(np.median(chroma)), 1)}


def render_frames(render_dir: Path) -> list[Path]:
    return sorted(p for p in render_dir.glob("slide-*.png") if p.stem[6:].isdigit())


def light_window(art_path: Path = ARTWORK, before: str | None = None) -> tuple[int | None, list[str]]:
    """How many of the seven decks before this one already read light, by ledger_check's own rule,
    less the named waivers. Before `before` (a run date) when given, so a re-run of a shipped deck
    does not count itself. None, with the reason, when the ledger can't be read: an unknown window
    is never an empty one (Codex, PR 402)."""
    import ledger_check as lc
    try:
        art = json.loads(art_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, [f"{art_path}: {e}"]
    entries = sorted(art.get("entries", []), key=lambda e: e.get("date", ""))
    if before:
        entries = [e for e in entries if e.get("date", "") < before]
    light = [e["date"] for e in entries[-7:]
             if isinstance(e.get("value"), dict)
             and isinstance(e["value"].get("deck_median_L"), (int, float))
             and e["value"]["deck_median_L"] >= lc.LIGHT_L
             and e["date"] not in lc.LIGHT_CAP_WAIVED]
    return len(light), light


def judge_v2(rows: list[dict], probe: bool) -> list[str]:
    """LOOK V2: grey mid tones, the vivid floor and the black room. Messages that concern the faded
    look say "mid tones" so shipped_check's filter keeps reading them."""
    out = []
    for r in rows:
        if "grey_mid" not in r:
            continue
        if probe and r["grey_mid"] > V2_PROBE_GREY:
            out.append(f"LOOK V2: {r['frame']}: {r['grey_mid']:.3f} of the frame is grey mid tones (L* 30 to 70, "
                       f"chroma under {GREY_C:g}), over {V2_PROBE_GREY}. That is the faded look. Push the tone's "
                       f"colour into the sweep, the key and the materials; never grade it darker")
        if probe and r["vivid"] < V2_PROBE_VIVID:
            out.append(f"LOOK V2: {r['frame']}: only {r['vivid']:.3f} of the frame is vivid (chroma {V2_VIVID_C:g} or "
                       f"more), under {V2_PROBE_VIVID}. Stand it in TXT.studio in the deck's tone, give the subject "
                       f"a saturated material and spend the accent")
        if r["dark"] > V2_FRAME_DARK:
            out.append(f"LOOK V2: {r['frame']}: {r['dark']:.3f} of the frame is near black (L* under {DARK:g}), over "
                       f"{V2_FRAME_DARK}. A look v2 frame shades to its tone's violet or navy, never a black room: "
                       f"drop TXT.stage and the dark room, use TXT.studio and TXLOOK.typeWash")
    if not probe and rows and all("grey_mid" in r for r in rows):
        g = float(np.mean([r["grey_mid"] for r in rows]))
        v = float(np.mean([r["vivid"] for r in rows]))
        d = float(np.mean([r["dark"] for r in rows]))
        if g > V2_DECK_GREY:
            out.append(f"LOOK V2: the deck holds {g:.3f} of its pixels in grey mid tones on the mean, over "
                       f"{V2_DECK_GREY}. The Oct 4 deck the owner called faded holds 0.62")
        if v < V2_DECK_VIVID:
            out.append(f"LOOK V2: the deck holds {v:.3f} vivid pixels on the mean, under {V2_DECK_VIVID}. The look v2 "
                       f"proof of Nov 14 holds 0.54")
        if d > V2_DECK_DARK:
            out.append(f"LOOK V2: the deck holds {d:.3f} near black pixels on the mean, over {V2_DECK_DARK}. The "
                       f"shipped Nov 14 deck held 0.62 and viewers gave it under three seconds")
    return out


def judge(rows: list[dict], probe: bool, date: str | None, art_path: Path = ARTWORK,
          look: str | None = None) -> list[str]:
    import ledger_check as lc
    problems = []
    if not rows:
        return ["no frames to measure"]
    v2 = is_v2(date, look)
    if v2:
        problems += judge_v2(rows, probe)
    if probe and not v2:
        for r in rows:
            if r["mid"] > PROBE_MID:
                problems.append(
                    f"{r['frame']}: {r['mid']:.3f} of the frame sits in the mid tones (L* 30 to 70), over "
                    f"the probe's {PROBE_MID}. This is the faded look the owner rejected on 2026-10-04. "
                    f"Stage the deck in a dark world (lastLight or floodlit), let the subject fill the "
                    f"frame, and take any pale wash off the art. A darker grade over the same frame is "
                    f"not the cure")
    mean_mid = float(np.mean([r["mid"] for r in rows]))
    if not probe and not v2 and mean_mid > DECK_MID:
        worst = sorted(rows, key=lambda r: -r["mid"])[:3]
        problems.append(
            f"the deck's frames hold {mean_mid:.3f} of their pixels in the mid tones on the mean, over "
            f"{DECK_MID}. The sibling's twelve decks hold 0.131. Worst: "
            + ", ".join(f"{r['frame']} {r['mid']:.2f}" for r in worst)
            + ". Re-light those frames in the deck's staged world rather than grading them down")
    # A PROBE FRAME IS JUDGED ALONE, its lightness as well as its mid tones (Codex, PR 402): the
    # median over a render folder that still holds a retried run's dark frames hid a light probe.
    if probe:
        light = [r for r in rows if r["median_L"] >= lc.LIGHT_L]
        median = max((r["median_L"] for r in light), default=0.0)
        subject = "probe frame " + ", ".join(r["frame"] for r in light)
    else:
        median = float(np.median([r["median_L"] for r in rows]))
        light = median >= lc.LIGHT_L
        subject = "deck"
    if light:
        n, which = light_window(art_path, date)
        if n is None:
            problems.append(
                f"the {subject} reads light, median L* {median:.1f} against ledger_check's line of "
                f"{lc.LIGHT_L}, and the light deck window can't be read ({which[0]}), so this gate "
                f"can't tell whether brand.yaml's cap of {lc.LIGHT_CAP} in eight is spent. Fix the "
                f"ledger or choose a dark world")
        elif n >= lc.LIGHT_CAP:
            problems.append(
                f"the {subject} reads light, median L* {median:.1f} against "
                f"ledger_check's line of {lc.LIGHT_L}, and the seven decks before it already hold "
                f"{n} light deck(s) ({', '.join(which)}) against brand.yaml's cap of {lc.LIGHT_CAP} in "
                f"eight. Ledger_check fails this at ship, which cost no. 42 forty four minutes. "
                f"Choose a dark world now")
    return problems


def report(rows, problems, probe, as_json):
    mean_mid = float(np.mean([r["mid"] for r in rows])) if rows else 0.0
    if as_json:
        print(json.dumps({"frames": rows, "mean_mid": round(mean_mid, 3), "problems": problems}, indent=1))
        return
    for r in rows:
        print(f"  {r['frame']:16} median L* {r['median_L']:5.1f}  mid {r['mid']:.3f}  near black {r['dark']:.3f}"
              f"  grey mid {r.get('grey_mid', 0):.3f}  vivid {r.get('vivid', 0):.3f}")
    print(f"  {'probe' if probe else 'deck'} mean mid tone share {mean_mid:.3f}")
    for p in problems:
        print(f"  FAIL  {p}")
    if not problems:
        print("  ok    within the register")


def self_test() -> int:
    failures = 0

    def check(label, cond):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}")
        failures += 0 if cond else 1

    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        # a faded frame: a soft gradient from L* about 45 to 65, the whole frame in the mid tones
        g = np.linspace(105, 165, 540)[:, None, None] * np.ones((540, 432, 3))
        Image.fromarray(g.astype(np.uint8)).save(t / "slide-01.png")
        # a bold frame: a near black field, a lit subject, one bright edge
        b = np.full((540, 432, 3), 10, np.uint8)
        b[300:470, 90:340] = 205
        b[300:306, 90:340] = 250
        Image.fromarray(b).save(t / "slide-02.png")
        faded, bold = frame_stats(t / "slide-01.png"), frame_stats(t / "slide-02.png")
        empty = t / "empty.json"
        empty.write_text(json.dumps({"entries": []}))
        check(f"a soft mid grey gradient is faded: {faded['mid']:.3f} in the mid tones",
              faded["mid"] > 0.9 and bool(judge([faded], True, None, empty)))
        check(f"a lit subject on a near black field is not: {bold['mid']:.3f} in the mid tones, "
              f"{bold['dark']:.3f} near black", bold["mid"] < 0.05 and not judge([bold], True, None, empty))
        check("a deck of both is held to its mean", judge([faded, bold], False, None, empty) != [])
        check("a deck of bold frames passes", judge([bold, bold], False, None, empty) == [])
        # the light deck cap, looked ahead: a white frame after a window already holding one
        w = np.full((540, 432, 3), 238, np.uint8)
        w[200:400, 150:300] = 20
        Image.fromarray(w).save(t / "slide-03.png")
        white = frame_stats(t / "slide-03.png")
        held = t / "held.json"
        held.write_text(json.dumps({"entries": [{"date": "2026-09-01", "value": {"deck_median_L": 81.0}}]}))
        check(f"a high key frame (median L* {white['median_L']}) after a spent light deck fails at the probe",
              any("reads light" in p for p in judge([white], True, "2026-09-05", held)))
        check("...and passes in a window with none spent",
              not any("reads light" in p for p in judge([white], True, "2026-09-05", empty)))
        check("a light probe frame beside two dark ones a retried run left in the folder still fails",
              any("reads light" in p for p in judge([bold, white, bold], True, "2026-09-05", held)))
        missing = t / "no-such-ledger.json"
        check("an unreadable light deck ledger fails a light probe closed",
              any("can't be read" in p for p in judge([white], True, "2026-09-05", missing)))
        check("...and never troubles a dark one, which doesn't ask it",
              judge([bold], True, "2026-09-05", missing) == [])
        # LOOK V2: a vivid frame (a saturated blue sky over a warm coral subject) passes, the dark staged
        # frame that passed above fails, and the soft grey gradient still fails as faded
        v = np.zeros((540, 432, 3), np.uint8)
        v[:300] = (47, 120, 224); v[300:] = (255, 118, 80); v[360:470, 120:320] = (34, 211, 238)
        Image.fromarray(v).save(t / "slide-04.png")
        vivid = frame_stats(t / "slide-04.png")
        check(f"LOOK V2: a saturated sky over a warm subject passes (vivid {vivid['vivid']:.2f}, grey mid "
              f"{vivid['grey_mid']:.2f})", judge([vivid], True, None, empty, look="v2") == []
              and judge([vivid, vivid], False, None, empty, look="v2") == [])
        check("LOOK V2: the near black staged frame fails as a black room",
              any("near black" in p for p in judge([bold], True, None, empty, look="v2")))
        check("LOOK V2: the soft grey gradient fails as faded, on the grey mid axis",
              any("grey mid" in p for p in judge([faded], True, None, empty, look="v2")))
        check("LOOK V2: the vivid frame is still mid tone heavy, and the v1 rule would have failed it",
              vivid["mid"] > PROBE_MID and bool(judge([vivid], True, None, empty, look="v1")))
        check("LOOK V2: is_v2 reads look.json's v2_from by date", is_v2("2099-01-01") == bool(v2_from())
              and not is_v2("2026-01-01"))
    # the calibration anchors, from the shipped decks this was measured on
    for date, should_fail in (("2026-10-04", True), ("2026-09-27", False)):
        d = ms.RUNS / date
        if (d / "copy.json").exists():
            rows = [frame_stats(p) for p in ms.frames(d)]
            got = bool([p for p in judge(rows, False, None, empty_ledger()) if "mid tones" in p])
            check(f"shipped deck {date} {'fails' if should_fail else 'passes'} on its mid tones "
                  f"({np.mean([r['mid'] for r in rows]):.3f})", got == should_fail)
    print(f"value_register self-test: {'all passed' if not failures else str(failures) + ' FAILED'}")
    return 1 if failures else 0


def empty_ledger() -> Path:
    p = Path(tempfile.mkdtemp()) / "empty.json"
    p.write_text(json.dumps({"entries": []}))
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--render-dir", type=Path)
    ap.add_argument("--run", type=Path, help="a shipped run directory, read as the site serves it")
    ap.add_argument("--probe", action="store_true", help="judge each frame alone, as the probe frame")
    ap.add_argument("--date", help="the run's date, so the light window excludes the run itself")
    ap.add_argument("--look", choices=("v1", "v2"), help="judge as this look, overriding look.json's v2_from")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.run:
        paths = ms.frames(a.run)
        date = a.date or a.run.name
    elif a.render_dir:
        paths = render_frames(a.render_dir)
        date = a.date
    else:
        ap.error("give --render-dir or --run")
    rows = [frame_stats(p) for p in paths]
    problems = judge(rows, a.probe, date, look=a.look)
    report(rows, problems, a.probe, a.json)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
