#!/usr/bin/env python3
"""panel_ready.py — the deck is not scored until the run believes it is finished.

WHY THIS EXISTS, and it is the most expensive lesson this project has bought twice.

`scoring_rubric.yaml` records it in the owner's own words on 2026-08-26: "judges are becoming a
token burning crutch masking your inefficiencies". Carousel no. 7 was scored FIFTEEN times in one
run and never cleared the bar, going sideways rather than up across a night of work. Carousel
no. 8, the next day, was scored THREE times, and every one of those panels found defects a careful
pass would have found for nothing:

  round 1  a fabricated board quotation, and a record saying a board acted while citing the
           document that only asked it to
  round 2  a first comment pointing readers at a frame that had been rebuilt out from under it,
           and a MODELED disclosure rendering as a broken sentence behind an opaque plate
  round 3  six text nodes still exempt from the occlusion and contrast checks, after the run had
           reported the exemption removed

Every one of those is MECHANICALLY CHECKABLE. None needed a judge. A panel is a CHECK on a deck
the run already believes is finished, and a run that ships a half-considered frame into three
scorers is paying three model calls to be told what one measurement would have said.

So this gate stands between the deck and the panel. It does not measure taste, and it never will:
composition, story and voice are what the judges are for. It measures the things that kept
REACHING the judges because nothing else was looking.

RUN IT BY EXIT CODE, before you spawn a single scorer. Non-zero means the deck is not ready to be
scored, not that it is unshippable. Fix the frame and run it again.

    panel_ready.py --date 2026-08-26
    panel_ready.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The rubric's own contrast line. Read from the rubric rather than typed here, so it cannot drift.
DEFAULT_CONTRAST_FLOOR = 4.5
OCCLUSION_FRAC = 0.05      # any non-ornamental text node covered more than this is unfinished
MIN_GROUND_STD = 4.0       # residual after removing the local mean, over an open ground patch
ORNAMENT_CHARS = 3         # a "decorative" node carrying more words than this is not ornament


def rubric_contrast_floor() -> float:
    """The floor the rubric states, never a literal in this file."""
    p = REPO_ROOT / "config" / "carousel" / "scoring_rubric.yaml"
    try:
        import yaml
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:                                                # noqa: BLE001
        return DEFAULT_CONTRAST_FLOOR
    for node in (doc, doc.get("thresholds") if isinstance(doc, dict) else None):
        if isinstance(node, dict) and isinstance(node.get("contrast_floor"), (int, float)):
            return float(node["contrast_floor"])
    return DEFAULT_CONTRAST_FLOOR


# ------------------------------------------------------------------ the checks

def check_nothing_exempt(report: dict) -> list[str]:
    """NO TEXT A READER NEEDS MAY BE EXEMPT FROM THE GATES.

    `qa.py` returns early on any node marked `data-decorative`, BEFORE the occlusion and the
    contrast checks. That attribute means "this is furniture, do not judge its craft". On
    2026-08-26 the deck had it on every MODELED disclosure and every source attribution, which are
    the most load bearing strings on a frame in a project whose whole promise is that a reader can
    check it. A disclosure saying what the record does not give is the opposite of decoration.

    The cost: a MODELED line 29 percent covered by an opaque plate published as a broken sentence
    on the cover, and an 18px source attribution that never tripped the 24px floor. Both reached
    the scoring panel. Both were already measured in `render_report.json`.

    A star glyph and a rule carry no words and stay exempt. Anything with words does not.
    """
    bad = []
    for s in report.get("slides", []):
        for t in s.get("text_nodes", []):
            if not t.get("decorative"):
                continue
            text = (t.get("text") or "").strip()
            if len(text) > ORNAMENT_CHARS:
                bad.append(f"{s['file']}: '{text[:46]}' is marked data-decorative, so qa.py skips "
                           f"it before the occlusion and contrast checks. Text a reader needs is "
                           f"never ornament. Remove the attribute or remove the words")
    return bad


def check_nothing_occluded(report: dict) -> list[str]:
    """NO TEXT IS PUBLISHED WITH A PLATE ON TOP OF IT.

    `render.py` already measures this and writes `occluded` on the node. On 2026-08-26 slide 1's
    disclosure carried `occluded: {frac: 0.291, by: zeroplate}` and the run shipped it to three
    judges, because the node was decorative and `qa.py` had returned early. The instrument was
    right and nothing read it.
    """
    bad = []
    for s in report.get("slides", []):
        for t in s.get("text_nodes", []):
            occ = t.get("occluded") or {}
            frac = occ.get("frac") or 0
            if frac > OCCLUSION_FRAC:
                bad.append(f"{s['file']}: '{(t.get('text') or '')[:40]}' is {frac:.0%} covered by "
                           f".{occ.get('by', '?')}. A published sentence with a plate through it "
                           f"is an unfinished frame, not a style choice")
    return bad


def check_pointers(base: Path, report: dict) -> list[str]:
    """EVERY SLIDE NUMBER IN PUBLISHED COPY RESOLVES TO A FRAME THAT CARRIES WHAT IT NAMES.

    On 2026-08-26 the first comment said the item's technology words were "quoted whole on slide
    5" after slide 5 had been rebuilt into the repayment frame. The words were on slide 7. A
    reader following the pointer found nothing, on the one surface whose entire job is letting a
    reader check the deck. No gate read a slide number in published copy against the frame it
    named, so it took a judge.

    This checks the reference RESOLVES and that the frame is not obviously about something else.
    It cannot check that the sentence around it is true, which is what a reader is for.
    """
    bad = []
    frames = {}
    for s in report.get("slides", []):
        m = re.search(r"slide-0*(\d+)", s.get("file", ""))
        if m:
            frames[int(m.group(1))] = " ".join(
                (t.get("text") or "") for t in s.get("text_nodes", []))
    for name in ("caption.txt", "first_comment.txt"):
        p = base / name
        if not p.exists():
            continue
        body = p.read_text(encoding="utf-8")
        for m in re.finditer(r"\bslide (\d+)\b", body, re.I):
            n = int(m.group(1))
            if n not in frames:
                bad.append(f"{name} names slide {n} and the deck has no such frame")
                continue
            # the sentence around the pointer, so the message can show what was promised
            start = max(0, m.start() - 90)
            claim = body[start:m.end() + 30].strip().replace("\n", " ")
            # a pointer is suspect when NO content word near it appears on the frame it names
            words = [w for w in re.findall(r"[a-z]{5,}", claim.lower())
                     if w not in ("slide", "quoted", "whole", "words", "which", "these", "their")]
            hay = frames[n].lower()
            if words and not any(w in hay for w in words):
                bad.append(f"{name} points at slide {n} and not one content word of "
                           f"\"{claim[:70]}\" appears on that frame. A pointer left behind by a "
                           f"rebuilt frame is a false statement on a sources surface")
    return bad


def check_contrast(qa: dict, floor: float) -> list[str]:
    """EVERY LINE CLEARS THE RUBRIC'S OWN CONTRAST FLOOR.

    `qa.py` states 4.5 and enforces it as ADVICE: below it is a WARN on anything that is not
    primary text, so a run reads `fails: 0` next to a line measured at 1.5. On 2026-08-26 the
    site line, the only route a reader has from the feed to the record, measured 1.5 on one frame
    and 2.7 to 3.3 on three others, across two panels, and never stopped anything.

    A floor stated in public and enforced as a suggestion is not a floor.
    """
    bad = []
    pat = re.compile(r"contrast ~?([0-9.]+) on '([^']*)'|worst-point contrast ([0-9.]+) on '([^']*)'")
    for s in qa.get("slides", []):
        for w in list(s.get("warns", [])) + list(s.get("fails", [])):
            m = pat.search(w)
            if not m:
                continue
            ratio = float(m.group(1) or m.group(3))
            text = m.group(2) or m.group(4)
            if ratio < floor:
                bad.append(f"{s.get('file', '?')}: '{text[:40]}' measures {ratio:.1f} against the "
                           f"rubric's stated {floor} floor")
    return bad


def check_plan_matches(base: Path) -> list[str]:
    """THE DOSSIER DESCRIBES THE FRAME THE RUN ACTUALLY MADE.

    A dossier is what a pixel critic grades a frame against, so a stale one launders a defect
    into a pass. On 2026-08-26 slide 5 was rebuilt from the technology vocabulary onto the
    repayment stake and its dossier still declared `claims: [c12, c13]` and `numerals: []` while
    the frame printed c4, c5 and $1,000,000,000 twice. Two separate judges found it.
    """
    bad = []
    cp, sp = base / "copy.json", base / "storyboard.md"
    if not (cp.exists() and sp.exists()):
        return bad
    copy = json.loads(cp.read_text(encoding="utf-8")).get("slides") or {}
    board = sp.read_text(encoding="utf-8")
    for key, slide in copy.items():
        m = re.search(r"\d+", key)
        if not m:
            continue
        n = int(m.group(0))
        blk = re.search(r"```yaml\nslide: %d\n(.*?)\n```" % n, board, re.S)
        if not blk:
            bad.append(f"copy.json has {key} and storyboard.md has no dossier for slide {n}")
            continue
        dm = re.search(r"claims: \[([^\]]*)\]", blk.group(1))
        if not dm:
            continue
        planned = {c.strip() for c in dm.group(1).split(",") if c.strip()}
        declared = set(slide.get("claims") or [])
        missing = declared - planned
        if missing:
            bad.append(f"slide {n}: copy.json declares {sorted(missing)} and the dossier's claims "
                       f"list does not carry {'it' if len(missing) == 1 else 'them'}. The plan "
                       f"describes a frame the run no longer makes")
    return bad


def check_ground(base: Path) -> list[str]:
    """A GROUND A DOSSIER CALLS WORKED IS MEASURABLY WORKED.

    Measured as the residual standard deviation over an open ground patch after its own local
    mean is removed, which is what separates material from a gradient. On 2026-08-26 four frames
    whose dossiers promised worked ground rendered flat, and the cause was two bugs at once: every
    tooth loop thresholded a -1..1 noise signal as if it returned 0..1, painting a near uniform
    wash over seven eighths of the surface, and every loop ran at a frequency whose feature size
    was about 400px, which is not grain at any alpha.

    Skipped rather than failed when Pillow or numpy is absent, because a missing library is not a
    flat ground and this gate must not report a defect it did not measure.
    """
    try:
        from PIL import Image, ImageFilter
        import numpy as np
    except Exception:                                                # noqa: BLE001
        return []
    bad = []
    for png in sorted((base / "render").glob("slide-0*.png")):
        im = Image.open(png).convert("L")
        w, h = im.size
        best = None
        for (fx0, fy0, fx1, fy1) in ((0.10, 0.22, 0.85, 0.32), (0.10, 0.46, 0.85, 0.56),
                                     (0.10, 0.64, 0.85, 0.74)):
            c = im.crop((int(w * fx0), int(h * fy0), int(w * fx1), int(h * fy1)))
            a = np.asarray(c, dtype=float)
            local = np.asarray(c.filter(ImageFilter.BoxBlur(16)), dtype=float)
            std = float((a - local).std())
            best = std if best is None else min(best, std)
        if best is not None and best < MIN_GROUND_STD:
            bad.append(f"{png.name}: quietest ground patch measures {best:.2f} residual against a "
                       f"{MIN_GROUND_STD} floor. A gradient is a promise of light, not of material")
    return bad


# ------------------------------------------------------------------ driver

def run(date: str, out_root: Path | None = None) -> int:
    base = Path(out_root or (REPO_ROOT / "out")) / date
    rp = base / "render" / "render_report.json"
    qp = base / "render" / "machine_qa.json"
    if not rp.exists():
        print(f"panel_ready: no render report at {rp}", file=sys.stderr)
        return 2
    report = json.loads(rp.read_text(encoding="utf-8"))
    qa = json.loads(qp.read_text(encoding="utf-8")) if qp.exists() else {}
    floor = rubric_contrast_floor()

    groups = [
        ("nothing a reader needs is exempt from the gates", check_nothing_exempt(report)),
        ("no published text has a plate through it", check_nothing_occluded(report)),
        ("every slide number in published copy resolves", check_pointers(base, report)),
        (f"every line clears the rubric's {floor} contrast floor", check_contrast(qa, floor)),
        ("every dossier describes the frame the run made", check_plan_matches(base)),
        ("every ground a dossier calls worked is worked", check_ground(base)),
    ]
    problems = [p for _, ps in groups for p in ps]
    for title, ps in groups:
        print(f"  {'ok  ' if not ps else 'NOT READY'}  {title}")
        for p in ps:
            print(f"      - {p}")
    if problems:
        print(f"\npanel_ready: {len(problems)} thing(s) a judge should never have to find.\n"
              f"  The panel is a CHECK on a deck you already believe is finished. Fix these and\n"
              f"  run this again. Every one of them was found by a scorer on 2026-08-26 and every\n"
              f"  one of them is a measurement, not a matter of taste.", file=sys.stderr)
        return 1
    print("\npanel_ready: the deck is ready to be scored. What the judges find now is craft, "
          "story and voice,\n  which is what they are for.")
    return 0


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    # THE 2026-08-26 DEFECTS, REPLAYED. Each of these reached a scoring panel.
    rep = {"slides": [{"file": "slide-01.html", "text_nodes": [
        {"text": "MODELED. THE RECORD GIVES COST LINES AND NOT A SITE PLAN",
         "decorative": True, "font_px": 26}]}]}
    got = check_nothing_exempt(rep)
    ok("a MODELED disclosure marked decorative is CAUGHT", bool(got), str(got))

    rep2 = {"slides": [{"file": "slide-01.html", "text_nodes": [
        {"text": "MODELED. THE RECORD GIVES COST LINES", "font_px": 26,
         "occluded": {"w": 161, "h": 31, "frac": 0.291, "by": "zeroplate"}}]}]}
    got = check_nothing_occluded(rep2)
    ok("the cover's 29 percent occluded disclosure is CAUGHT", bool(got), str(got))
    ok("...and a hairline graze is not",
       not check_nothing_occluded({"slides": [{"file": "s", "text_nodes": [
           {"text": "a line", "occluded": {"frac": 0.02, "by": "x"}}]}]}))

    ok("a star glyph stays exempt, because it carries no words",
       not check_nothing_exempt({"slides": [{"file": "s", "text_nodes": [
           {"text": "*", "decorative": True}]}]}))

    qa = {"slides": [{"file": "slide-04.html",
                      "warns": ["low contrast ~1.5 on 'texasaidocket.com' (est.)"], "fails": []}]}
    got = check_contrast(qa, 4.5)
    ok("the site line at 1.5, reported by qa.py as a WARN, is CAUGHT", bool(got), str(got))
    ok("...and a line at 6.9 is not",
       not check_contrast({"slides": [{"file": "s", "warns": ["contrast ~6.9 on 'x'"],
                                       "fails": []}]}, 4.5))

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        b = Path(d)
        (b / "render").mkdir()
        (b / "copy.json").write_text(json.dumps(
            {"slides": {"S5": {"claims": ["c5", "c4", "c3"]}}}), encoding="utf-8")
        (b / "storyboard.md").write_text(
            "```yaml\nslide: 5\nclaims: [c12, c13]\nnumerals: []\n```\n", encoding="utf-8")
        got = check_plan_matches(b)
        ok("slide 5's stale dossier, which two judges found, is CAUGHT", bool(got), str(got))
        (b / "storyboard.md").write_text(
            "```yaml\nslide: 5\nclaims: [c5, c4, c3]\nnumerals: []\n```\n", encoding="utf-8")
        ok("...and a dossier that matches passes", not check_plan_matches(b))

        (b / "first_comment.txt").write_text(
            "The words the item does use for the technology are quoted whole on slide 5.",
            encoding="utf-8")
        rep3 = {"slides": [
            {"file": "slide-05.html", "text_nodes": [
                {"text": "THE REPAYMENT"}, {"text": "Who pays the billion back"}]},
            {"file": "slide-07.html", "text_nodes": [
                {"text": "digital technology, robotics, and automation"}]}]}
        got = check_pointers(b, rep3)
        ok("the first comment pointing at a rebuilt frame is CAUGHT", bool(got), str(got))
        (b / "first_comment.txt").write_text(
            "The words the item does use for the technology are quoted whole on slide 7.",
            encoding="utf-8")
        ok("...and the corrected pointer passes", not check_pointers(b, rep3))

    # EVERY CHECK MUST BE REACHABLE. A gate whose loader silently returns nothing reports clean
    # forever, which is the shape craft_floor shipped when it read a key qa.py never wrote.
    for fn, name in ((check_nothing_exempt, "check_nothing_exempt"),
                     (check_nothing_occluded, "check_nothing_occluded")):
        ok(f"{name} runs on an empty report without raising",
           fn({"slides": []}) == [])

    src = Path(__file__).read_text(encoding="utf-8")
    # BUILT FROM PARTS, because a literal needle in this file matches ITSELF and the assertion
    # then reports a flag that is only its own test. The first version of this line did exactly
    # that and went red on a clean file, which is a self-test lying in the safe direction and
    # still a self-test lying.
    dash = "-" * 2
    ok("this gate has no flag that softens it",
       not any(dash + f in src for f in ("allow", "skip", "force", "warn-only")))
    ok("the contrast floor is read from the rubric and not typed here",
       "rubric_contrast_floor" in src and "scoring_rubric.yaml" in src)

    if failures:
        print(f"\npanel_ready self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\npanel_ready self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.date:
        ap.error("--date is required")
    return run(args.date, Path(args.out) if args.out else None)


if __name__ == "__main__":
    raise SystemExit(main())
