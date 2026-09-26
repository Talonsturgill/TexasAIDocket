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

# THE VALUE ARC TOLERANCE, AND IT IS AN EXTERNAL STANDARD RATHER THAN A NUMBER OFF OUR OWN DECKS.
#
# One Munsell value step. Munsell value is the perceptually uniform lightness scale, and adjacent
# values are one plainly visible step apart by construction: under ASTM D1535 the luminance
# factors for V=4 and V=5 give CIE L* 41.2 and 51.8, and the step holds near 10 L* at the dark
# end too (V=1 is L* 10.4, V=2 is L* 20.5).
#
# So a deck whose median lands more than one Munsell step from its own plan is not a deck that
# came out slightly dark. It is a deck rendered at a different value than the one that was
# planned, which is the difference between a miss and a plan that was never executed.
#
# This is deliberately NOT derived from our own decks. GATE_LESSONS' rule for setting a threshold
# says a figure measured off our own corpus and re-derived is a ratchet with no floor, and the
# corpus here is four planned-against-measured pairs, which is not a distribution.
#
# What the four say, for whoever revisits this: 2026-08-29 planned near 32 and measured 15.6,
# 2026-08-30 planned 40 and measured 21.2, 2026-09-02 planned 30 and measured 20.4, and this
# run's FIRST render planned 24 and measured 6.3. Three of the four clear one Munsell step and
# the fourth sits just inside it, so this fires on the size of miss the evidence actually shows
# and stays quiet on the repaired deck, which measured 23.1 against 24.
MUNSELL_STEP_L = 10.0

# The measurement grid. 270 by 338, which is what every prior run's `measurements.json` was
# written on and what `ledger/carousel/artwork.json` records. 2026-09-03 measured its own arc on
# a second grid and disagreed with the ledger by 1.1, and its storyboard records the finding:
# two grids is two homes for one figure.
ARC_GRID = (270, 338)


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


def check_report_complete(base: Path, report: dict) -> list[str]:
    """THE RENDER REPORT AND THE RENDER DIRECTORY ARE THE DECK ON DISK, NO MORE AND NO LESS
    (Codex, PR 369).

    Every group here that reads the render reads `render_report.json`, and a frame with no record in
    it is skipped by all of them in silence. It happens: when the report is unreadable, `render.py
    --only 4` discards it and writes one holding slide 4 alone, and `qa.py` then measures that same
    subset, so the sky, the occlusion, the exemptions and the contrast of the other eight frames go
    unread into a scoring round. `print_ban` compares the report with the slides, and it runs in
    Phase 12b, not before each round. This does the same comparison before each round.

    The other direction matters as much. A frame a repair deleted or renamed keeps its record in the
    report, which `render.py` merges into, and its PNG in `render/`, and `assemble.py` builds the
    PDF from every `render/slide-*.png`. So a record or a PNG with no source in `slides/` is a frame
    the panel would read and the PDF would ship that the deck no longer has.
    """
    listed = {str(rec["file"]) for rec in (report.get("slides") or [])
              if isinstance(rec, dict) and rec.get("file")}
    on_disk = {f.name for f in (base / "slides").glob("slide-*.html")}
    missing, stale = sorted(on_disk - listed), sorted(listed - on_disk)
    orphans = sorted(p.name for p in (base / "render").glob("slide-*.png")
                     if p.with_suffix(".html").name not in on_disk)
    out = []
    if missing:
        out.append(f"the render report holds no record of {', '.join(missing)}, so every check here "
                   f"that reads the render skipped {'it' if len(missing) == 1 else 'them'}. Render the "
                   f"deck, run qa.py, then this again")
    if stale:
        out.append(f"the render report still holds {', '.join(stale)}, which "
                   f"{'is' if len(stale) == 1 else 'are'} no longer in slides/, so the panel would read "
                   f"a frame the deck doesn't have. Render the whole deck without --only, which writes "
                   f"a fresh report, then qa.py, then this again")
    if orphans:
        out.append(f"render/ still holds {', '.join(orphans)} with no source in slides/, and "
                   f"assemble.py builds the PDF from every render/slide-*.png, so the PDF would ship "
                   f"{'it' if len(orphans) == 1 else 'them'}. Delete "
                   f"{'it' if len(orphans) == 1 else 'them'} from out/<date>/render, assemble again, "
                   f"then run this again")
    return out


# A slide's own chassis, the one file under assets/ a run may write (`assets/js/deck/**`, Phase 10.5).
DECK_ASSET = re.compile(r"@@ASSETS@@/(js/deck/[^\"'?#\s)]+)")


def check_renders_current(base: Path, assets: Path | None = None) -> list[str]:
    """EVERY FRAME WAS RENDERED AFTER ITS LAST EDIT (Codex, PR 369).

    `load_machine_qa` holds the QA file to the render, and nothing held the render to the source. A
    repair edits `slides/slide-04.html`, and its `render.py --only` names another frame, or dies
    before it reaches this one. The PNG and the report record are the frame from before the repair,
    `qa.py` measures that PNG and writes a fresh file, the report's frame set still matches, and the
    panel scores, and `assemble.py` ships, pixels the repair never touched.

    So each PNG and the render report have to be no older than the frame's source: its own HTML,
    and the deck chassis it loads from `assets/js/deck/`, the one place under `assets/` a run writes,
    since a chassis edit restyles every frame that loads it. The engine is not held to this: a run
    never writes it, and a merge that moves it lands after the panel. `render.py` records no hash, so
    file times are the evidence, with `load_machine_qa`'s one second of slack. A frame with no PNG
    is `qa.py`'s "png missing", which `load_machine_qa` already stops on.
    """
    assets = Path(assets or (REPO_ROOT / "assets"))
    rdir = base / "render"
    rp = rdir / "render_report.json"
    reported = rp.stat().st_mtime if rp.exists() else None
    out = []
    for src in sorted((base / "slides").glob("slide-*.html")):
        png = rdir / (src.stem + ".png")
        if not png.exists():
            continue
        try:
            html = src.read_text(encoding="utf-8", errors="replace")
        except OSError:
            html = ""
        sources = [src] + [assets / rel for rel in sorted(set(DECK_ASSET.findall(html)))]
        stamped = [(q.stat().st_mtime, q) for q in sources if q.exists()]
        if not stamped:
            continue
        edited, newest = max(stamped)
        shown = newest.name if newest == src else f"assets/{newest.relative_to(assets)}"
        n = re.search(r"slide-0*(\d+)", src.name)
        again = (f"Render it with render.py --only {n.group(1) if n else '?'}, run qa.py, then this "
                 f"again")
        if png.stat().st_mtime + 1.0 < edited:
            out.append(f"render/{png.name} predates the last edit to {shown}, so the panel would "
                       f"score, and assemble.py would ship, {src.name} as it was before that edit. "
                       f"{again}")
        elif reported is not None and reported + 1.0 < edited:
            out.append(f"render/render_report.json predates the last edit to {shown}, so its record "
                       f"of {src.name} describes the frame before that edit. {again}")
    return out


def load_machine_qa(base: Path, report: dict) -> tuple[dict, list[str]]:
    """MACHINE QA MEASURED THE FRAMES THAT ARE HERE NOW (Codex, PR 369).

    The contrast group reads `machine_qa.json`, which `qa.py` writes and nothing else refreshes. A
    repaired round re-renders its frames with `render.py --only`, which rewrites the PNGs and the
    render report and leaves the QA file describing the frames it just replaced. A line repaired
    since then reads as failing, and a line broken since then reads as clean, which is the
    direction that reaches a panel. Until 2026-09-26 a missing file read as `{}` and passed.

    So the file has to exist, parse, be no older than the newest render and carry a record for
    every frame the render report lists. The age test is `gate_status.staleness`'s, with its one
    second of slack for a filesystem that rounds file times to the second. Running
    `qa.py --render-dir out/<date>/render` clears all four. Returns the QA, and the problems, which
    are empty only when the QA can be read as a reading of these frames.
    """
    rdir = base / "render"
    qp = rdir / "machine_qa.json"
    again = (f"Run python3 .claude/skills/carousel-engine/qa.py --render-dir {rdir}, then "
             f"this again")
    if not qp.exists():
        return {}, [f"render/machine_qa.json is missing, so no contrast was measured on these "
                    f"frames. {again}"]
    try:
        qa = json.loads(qp.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {}, [f"render/machine_qa.json can't be read ({e.__class__.__name__}). {again}"]
    if not isinstance(qa, dict) or not isinstance(qa.get("slides"), list):
        return {}, [f"render/machine_qa.json carries no list of slides. {again}"]
    drawn = max([p.stat().st_mtime for p in rdir.glob("slide-*.png")]
                + [(rdir / "render_report.json").stat().st_mtime])
    problems = []
    if qp.stat().st_mtime + 1.0 < drawn:
        problems.append(f"render/machine_qa.json predates the newest render, so what it says "
                        f"about contrast describes frames that were replaced. {again}")
    measured = {q.get("file") for q in qa["slides"] if isinstance(q, dict)}
    for rec in report.get("slides") or []:
        name = rec.get("file") if isinstance(rec, dict) else None
        if name and name not in measured:
            problems.append(f"{name}: render/machine_qa.json has no record of it, so its contrast "
                            f"was never measured. {again}")
    # A RECORD THAT CARRIES A FAIL IS NOT A CLEAN MEASUREMENT (Codex, PR 369). qa.py files "png
    # missing" on the frame and skips the frame before it counts the deck's fails, so it exits 0 on
    # a deck with a frame it never measured. Any fail on a frame's record stops the panel here,
    # because Phase 11 ships no FAIL and a panel on one is a round spent twice.
    for q in qa["slides"]:
        if isinstance(q, dict) and q.get("fails"):
            fails = [str(f) for f in q["fails"]]
            problems.append(f"{q.get('file') or '?'}: machine QA failed it ({fails[0][:120]}"
                            f"{f', and {len(fails) - 1} more' if len(fails) > 1 else ''}). Fix it, "
                            f"render it, run qa.py, then this again")
    return qa, problems


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

        # THE PROSE HALF OF THIS IS NOT CHECKED, and the reason is worth more than the check.
        #
        # A stale `job` line is a real defect: slide 5's still read "the board item's own
        # vocabulary for the technology" over a frame rebuilt into the repayment stake, a judge
        # found it, and the run had reported that dossier synced because the claims half of its
        # own edit landed and the prose half silently did not.
        #
        # I wrote an overlap check for it and it fired on slide 6, whose dossier reads "The
        # measured absence, stated as a count and drawn as an unbroken span" over a frame saying
        # SEARCHED, CASE INSENSITIVE and Twenty pages, no mention of AI. Zero shared words and a
        # perfectly accurate dossier, because a good plan ABSTRACTS the frame rather than
        # repeating it. A gate that misreports costs more than one that misses, since the run
        # then hunts for something that was never there, so the unsound check came out rather
        # than shipping behind a green banner.
        #
        # What would work is a signal rather than a similarity: a job naming a claim id the slide
        # does not declare, or quoting a string the frame does not carry. Slide 5's stale line did
        # neither, so that would not have caught it either. Written down as an open gap.
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


def check_scene_bounds(base: Path) -> list[str]:
    """A FIGURE THE PLAN PLACED IS INSIDE THE FRAME ITS OWN CAMERA GIVES IT.

    WIRED HERE ON 2026-09-14 AND THIS IS THE PHASE THAT EARNS IT. Carousel no. 24's cover put its
    only human figure at world X -13 at Z 9, which on that frame's own f 820 camera projects to
    x -644, off the left edge of a 1080 px frame. The frame's whole argument was true scale
    against a body, and the body was not in the picture.

    It reached the panel. Two of three judges found it independently, on a round already carrying
    three other frames, and closing it cost three scoring rounds. That is exactly what this file
    exists to prevent: a thing a judge should never have to find, which is a measurement rather
    than a matter of taste.

    `scene_bounds.problems` returns the outside-the-frame findings only. Its acceptance-band
    report is printed beside this rather than failed on, for the reason its own docstring gives.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import scene_bounds as m
    except Exception:                                                # noqa: BLE001
        return []
    return m.problems(base)


def check_bleed_witness(base: Path) -> list[str]:
    """A DECLARED BLEED IS DRAWN, read back out of the frame's own source.

    WIRED HERE ON 2026-09-17 AND THIS IS THE PHASE THAT EARNS IT, for the same reason
    `check_scene_bounds` above does. Carousel no. 27 declared a bleed on four frames that none of
    them makes: three sheets stopping 148 to 250 px above the bottom edge, and a panel whose
    declared top bleed is a hard edge 392 px inside the frame. `layout_check` measured the
    declaration against the declared rect and passed, both being typed into the same yaml block.
    Two craft judges found all four by reading the `N.sheet` call and subtracting, across four
    scoring rounds on a deck that shipped at 6.856 against an 8.0 bar, and a round 5 judge asked
    for this gate in one sentence.

    A FAILURE TO LOAD IS A FINDING, not an empty list. A gate that cannot run and reports clean
    is GATE_LESSONS 37, and this phase's whole promise is that nothing on this list reaches a
    judge.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import bleed_witness as m
    except Exception as exc:                                         # noqa: BLE001
        return [f"bleed_witness could not be loaded, so the drawn geometry was not read at all: "
                f"{exc}"]
    probs = m.problems(base)
    if probs is None:
        return [f"{base}/slides archives no slide HTML, so no frame's drawn geometry could be "
                f"read. That is a check that CANNOT RUN rather than a check that passed"]
    return probs


def scene_band_notes(base: Path) -> list[str]:
    """The acceptance bands a frame's own camera cannot reach. Read, never failed on."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import scene_bounds as m
        slides = base / "slides"
        if not slides.is_dir():
            return []
        reports, _ = m.check_deck(slides, base / "storyboard.md")
        return [line for r in reports for line in r["bands"]]
    except Exception:                                                # noqa: BLE001
        return []


def check_contacts(base: Path) -> list[str]:
    """NO ADDRESS A READER COULD WRITE TO THAT THIS RUN'S CLAIMS DO NOT CARRY.

    WIRED HERE ON 2026-09-14. That run's frame 2 set "Questions to BatchZero@ercot.com" inside a
    drawn facsimile of a real ERCOT notice, in the same serif as two verbatim quotations, on the
    frame whose whole argument is what that document does and does not say. No claim in the run
    carries an email address. A pixel critic caught it and every gate was green.

    Returns nothing when the run has no claims file or nothing published, which this file treats
    as no finding rather than as a pass, the same way check_ground treats a missing library.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import contact_trace as m
    except Exception:                                                # noqa: BLE001
        return []
    return m.problems(base) or []


def check_sky_in_frame(report: dict, base: Path | None = None) -> list[str]:
    """NO FRAME THAT STANDS SOMEWHERE POINTS ITS CAMERA WHERE THAT PLACE ISN'T.

    WIRED HERE ON 2026-09-26. `TXT.snapshot` prints a verdict on every snapshot of a frame that
    stands in the world or in a room, and render.py keeps it in the report. TXT.NO_SKY is a frame
    that calls TXT.sky while its camera shows none of it and stands inside nothing built, and
    TXT.NO_ROOM a frame that builds only a room and shows too little of it. print_ban reads the
    verdicts on the probe and in Phase 12b. This reads them before every panel round, because a
    repair can turn a settled frame toward the ground and the next round's judges would be the first
    to see it (Codex, PR 369). Through the engine, no. 33's frame 4 and no. 34's frames 4 and 5
    print NO_SKY, and a judge named no. 33's frame 4 top-down in all five rounds.

    Given the run directory, a frame whose source stands somewhere and whose render printed no
    verdict at all is named too, on a run dated after print_ban's VERDICT_SINCE: its pixels never
    went through the snapshot (Codex, PR 369). The reading is print_ban's own, the last verdict on
    the page, so a preview withdrawn by the kept snapshot is clean here too and the two can't
    drift. An import that fails raises rather than reading as clean.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from print_ban import place_verdict, in_world, in_room, VERDICT_SINCE, DATED
    out, verdicts = [], {}
    for rec in report.get("slides") or []:
        if not isinstance(rec, dict):
            continue
        name, v = str(rec.get("file") or "?"), place_verdict(rec.get("console_errors"))
        verdicts[name] = v
        if v == "no sky":
            out.append(f"{name} calls TXT.sky and its camera shows none of it, with nothing built "
                       f"around it. Lift the camera until the horizon is in frame, or stand it inside "
                       f"something built (the kit's semi_cab_interior, or a TXT.interior room filling "
                       f"half the frame). A roof, a canopy or a tree overhead is not an interior")
        elif v == "no room":
            out.append(f"{name} builds a room with TXT.interior and its camera shows too little of it, "
                       f"with nothing built around it. Point the camera into the room so it fills half "
                       f"the frame, or stand it inside, and keep the room drawn")
        elif v == "no render":
            out.append(f"{name}'s kept snapshot came out black or unreadable, so the frame fell back to "
                       f"whatever it draws instead, and a 2D fallback stands nowhere. Fix the render")
    if base is not None and DATED.match(base.name) and base.name > VERDICT_SINCE:
        for f in sorted((base / "slides").glob("slide-*.html")):
            src = f.read_text(encoding="utf-8", errors="replace")
            if f.name in verdicts and verdicts[f.name] is None and (in_world(src) or in_room(src)):
                out.append(f"{f.name} stands in the world or a room and its render printed no "
                           f"verdict, so its pixels never went through TXT.snapshot. Render it "
                           f"through TXT.snapshot, never a 2D fallback or a renderer called by hand")
    return out


def check_quantifiers(base: Path, articles: Path | None = None) -> list[str]:
    """EVERY UNIVERSAL ON EVERY PUBLISHED SURFACE NAMES ITS SET, THE WEB EDITION INCLUDED.

    WIRED HERE ON 2026-09-24 AND THIS IS THE PHASE THAT EARNS IT. `quantifier_check` has been a
    CURRENT gate in `shipped_check` since 2026-09-03, which is to say it ran in CI after a deck was
    finished and never before a panel. Carousel no. 33's run record printed its row as ABSENT, and
    its round 2 integrity judge hard failed the web edition for "A person enters in one sentence",
    an exclusive count the fetched draft refutes in seven other sentences. Three model calls and a
    scoring round were spent being told what a sweep of the fetched text says for nothing.

    `ledger=None`, deliberately. The gate's third rule compares the caption ledger's stored first
    line with the shipped caption, and the ledger is written at ship, after the panel. That is
    `shipped_check`'s question to ask. What belongs here is only what a judge would otherwise find.

    A FAILURE TO LOAD IS A FINDING, for the reason `check_bleed_witness` gives above.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import quantifier_check as m
    except Exception as exc:                                         # noqa: BLE001
        return [f"quantifier_check could not be loaded, so no universal on any surface was read: "
                f"{exc}"]
    return m.check(base, ledger=None, articles=articles)


# ------------------------------------------------------------------ the value arc

# THE PARSE RULE, STATED, because a gate that mis-parses its own input invents failures and they
# are convincing. Two shapes, and both were taken off real shipped storyboards rather than from an
# idea of how a plan is written:
#
#   FENCED   a fenced block whose lines read `F1  24  the lane`, under a paragraph or heading that
#            names the value arc. 2026-09-04 writes this and it is the form the spec asks for.
#   INLINE   `Planned per frame 32, 40, 28, ...` (2026-08-29) or `Planned value arc, 34, 22, ...`
#            (2026-08-30), inside a paragraph that names the value arc AND the word planned.
#
# Both are scoped to a span that names the value arc, so a comma list anywhere else in a
# storyboard cannot become a plan. 2026-09-03 declares a MEASUREMENT and no plan, which is read
# as no plan rather than as one, because `Per frame median L*, computed` carries no `planned`.
ARC_CUE = re.compile(r"value arc", re.I)
ARC_FRAME_LINE = re.compile(r"^\s*F\s*(\d+)\s+(-?\d+(?:\.\d+)?)\b", re.M)
ARC_INLINE = re.compile(r"\bplanned\b[^\n.]*?((?:-?\d+(?:\.\d+)?\s*,\s*){3,}-?\d+(?:\.\d+)?)",
                        re.I)


# THE TRAP INSIDE `ARC_INLINE`, NAMED HERE BECAUSE THIS IS WHERE SOMEBODY WILL READ IT.
#
# `ARC_INLINE` matches `planned` followed by `[^\n.]*?` and then the list, so the word and the
# numbers have to be on ONE LINE. On 2026-09-10 the plan wrote `## The value arc, planned` and
# put the nine values on the next line, and the parser read that deck as declaring no arc at all.
# The row printed `ok`, because a deck that declares nothing and a deck that clears its arc came
# out of `check_value_arc` as the same empty list.
#
# These two patterns are how the third case is told apart from the other two. A span that names a
# PLANNED arc and carries a comma list of four or more numbers has a plan in it. If the parser
# above could not reach that list, the plan was written in a form no machine compares, and that
# is a finding rather than silence.
#
# Commas only, deliberately, and 2026-09-03 is why. That storyboard narrates a value arc line
# separated by middots inside a paragraph explaining that the line was WRONG. It is prose about
# an arc rather than a declaration of one, and a looser pattern would report it as a defect.
ARC_LIST_ANYWHERE = re.compile(r"(?:-?\d+(?:\.\d+)?\s*,\s*){3,}-?\d+(?:\.\d+)?")
ARC_PLAN_WORD = re.compile(r"\bplanned\b", re.I)


def arc_spans(storyboard: str) -> list:
    """Every stretch of the plan that names the value arc, scoped the way the parser reads it.

    The span runs from the START OF THE CUE'S OWN PARAGRAPH to the next markdown heading, or a
    thousand two hundred characters, whichever comes first. Scoped so a number elsewhere in the
    plan cannot be read as an arc value.

    IT STARTS AT THE PARAGRAPH AND NOT AT THE CUE, and that is not tidiness. 2026-08-30 writes
    `Planned value arc, 34, 22, 40, ...`, where the word the parser keys on sits BEFORE the cue,
    so a span beginning at the cue read that deck as declaring nothing. The first version of this
    did exactly that and its own self-test caught it.
    """
    out = []
    for m in ARC_CUE.finditer(storyboard):
        head = storyboard.rfind("\n\n", 0, m.start())
        start = head + 2 if head >= 0 else 0
        tail = storyboard[start:]
        # The next heading AFTER the cue ends the span. Searched from past the cue rather than
        # from the top, because the cue is often inside a heading of its own and that heading
        # would otherwise close the span before its own paragraph.
        after = m.start() - start + len(m.group(0))
        cut = re.search(r"^#{1,6}[ \t]", tail[after:], re.M)
        out.append(tail[:(after + cut.start() if cut else min(len(tail), 1200))])
    return out


def unreadable_plan(storyboard: str) -> list:
    """Spans that declare a planned arc the parser above cannot reach. The third state.

    Empty for a storyboard that declares no arc, which is the ordinary case, and empty for one
    whose arc parses. Non-empty only where the plan is demonstrably in the file and demonstrably
    out of the parser's reach.
    """
    if planned_arc(storyboard):
        return []
    out = []
    for span in arc_spans(storyboard):
        if not ARC_PLAN_WORD.search(span):
            continue
        lst = ARC_LIST_ANYWHERE.search(span)
        if lst:
            out.append(" ".join(lst.group(0).split())[:120])
    return out


def arc_unread_finding(stuck: list) -> str:
    """The third state's one line, written once so the self-test can hold the REAL message.

    A message the test keeps its own copy of is a message the test agrees with rather than
    reads, which is how `caption_check`'s month rule stayed green over a form the site never
    rendered.
    """
    return (f"this storyboard DECLARES a planned value arc and this gate could not read it, so "
            f"the deck's register was compared against nothing while the row above it read as a "
            f"pass. The list is right there: {stuck[0]}. ARC_INLINE matches `planned` followed "
            f"by `[^\\n.]*?`, so the word and the numbers must be on ONE LINE, and a newline "
            f"between them is a plan no machine compares. Put the list back on the line that "
            f"carries the word, or use the fenced `F1  24  the lane` form "
            f"SLIDE_DOSSIER_SPEC.md gives")


def span_arc(storyboard: str) -> list:
    """The arc as a SUMMARY, written once in a span that names the value arc. The two old shapes.

    Kept separate from `planned_arc` so the dossier-by-dossier shape below can be cross checked
    against it rather than merged into it. Two homes for one figure is the defect this file
    already records about measurement grids, and it is a defect about plans too.
    """
    for span in arc_spans(storyboard):
        fenced = re.search(r"```[a-z]*\n(.*?)```", span, re.S)
        if fenced:
            rows = ARC_FRAME_LINE.findall(fenced.group(1))
            if len(rows) >= 3:
                return [float(v) for _n, v in sorted(rows, key=lambda r: int(r[0]))]
        inline = ARC_INLINE.search(span)
        if inline:
            return [float(x) for x in inline.group(1).split(",") if x.strip()]
    return []


# ------------------------------------------------------------- THE THIRD SHAPE (2026-09-13)
#
# THE DEFECT. Carousel no. 22 planned a median for every one of its nine frames and wrote each
# one into that frame's OWN dossier, under `art.value_structure`, as `Frame median L* planned at
# 22`. Nine declarations, one per frame, in the key `SLIDE_DOSSIER_SPEC.md` asks for the value
# structure in. No summary paragraph anywhere named the value arc, so `arc_spans` found nothing,
# `planned_arc` returned `[]`, `unreadable_plan` returned `[]` because it only looks inside an
# arc span, and this gate printed `(this storyboard declares no value arc this gate can read)`
# and passed the deck to three judges.
#
# The plan was 22, 46, 34, 30, 26, 18, 72, 26, 28, deck median 28. The deck measured 13.5, 28.8,
# 11.6, 11.1, 18.8, 11.1, 41.1, 11.1, 14.1, deck median 13.5. A miss of 14.5, half again a
# Munsell step, with four frames sitting inside half a point of each other at the floor. It was
# found by the showrunner writing a one-off `measure.py` AFTER the deck had shipped at 6.784,
# which is the same way carousel 15's collapse was found, which is what this check exists to
# stop happening a second time. It happened a second time.
#
# This is GATE_LESSONS 39: a gate that selects what to examine by an allowlist of FORMS sleeps
# on the form nobody thought of. The two span shapes were both taken off real storyboards, and
# the third was written the day after they were.
#
# SCOPED TO `value_structure` AND NOT TO THE DOSSIER, which is the whole of why this can be
# trusted. Acceptance items legitimately talk about medians, and they talk about the medians of
# REGIONS: `the punch column's median L* is at least 10 below the rail face median`, `the frame's
# median L* at 432px is 45 or higher`, `a contact shadow whose median L* differs from the floor
# beside it by 4 or more`. Read those as a plan and the gate invents a number the plan does not
# contain, which is GATE_LESSONS 27 and is the most convincing shape a false failure takes.
# `value_structure` is where the plan states what the frame comes out at, so that is where this
# looks and nowhere else.
DOSSIER_BLOCK = re.compile(r"```ya?ml\s*\nslide:\s*(\d+)\b(.*?)```", re.S)
VALUE_STRUCTURE = re.compile(r"^[ \t]*value_structure:(.*?)(?=^[ \t]{0,4}[A-Za-z_][\w]*:)",
                             re.S | re.M)
# The qualifier is required. `median L* 44` on its own is a sentence about a median and could be
# any region's; `frame median L*` and `planned median L*` are the frame's own figure.
FRAME_MEDIAN = re.compile(r"\b(?:planned\s+)?frame(?:'s)?\s+median\s+L\*|\bplanned\s+median\s+L\*",
                          re.I)
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
UNIT_AFTER = re.compile(r"\s*(?:px|pt|%)", re.I)


def _first_value(tail: str) -> float | None:
    """The first bare number in the rest of that sentence, or None.

    Stops at the sentence end so `Frame median L* planned at 18, the deck's floor. Lightest is
    the plate at 74` cannot reach across into a second figure, and skips a number carrying a
    unit so `at 432px is 45 or higher` cannot report the viewport as a lightness.
    """
    seg = tail[:60]
    cut = re.search(r"\.(?:\s|$)", seg)
    if cut:
        seg = seg[:cut.start()]
    for m in NUMBER.finditer(seg):
        if UNIT_AFTER.match(seg[m.end():m.end() + 4]):
            continue
        return float(m.group(0))
    return None


def dossier_arc(storyboard: str) -> tuple[dict, int]:
    """`({slide: planned median}, number of dossiers)`, read from each frame's own plan."""
    blocks = [(int(n), b) for n, b in DOSSIER_BLOCK.findall(storyboard)]
    found = {}
    for n, blk in blocks:
        vs = VALUE_STRUCTURE.search(blk)
        if not vs:
            continue
        seg = vs.group(1)
        m = FRAME_MEDIAN.search(seg)
        if not m:
            continue
        v = _first_value(seg[m.end():])
        if v is not None:
            found[n] = v
    return found, len(blocks)


def partial_dossier_plan(storyboard: str) -> list:
    """SOME frames declare a median and some do not, which is a plan for part of a deck.

    Reported rather than compared, because an arc of seven against a render of nine reaches
    `arc_verdict`'s length branch and is told it has a stale plan, which is the wrong diagnosis
    and sends a run looking in the wrong file. 2026-09-11 is the real shape: six of its nine
    dossiers write `Planned frame median L* 38` and three write `median L* 44` with no
    qualifier, so a reader of that file would say the plan is complete and a parser cannot.
    """
    found, total = dossier_arc(storyboard)
    if total < 3 or not found or len(found) == total:
        return []
    missing = [n for n in range(1, total + 1) if n not in found]
    return [f"{len(found)} of {total} dossiers state a planned frame median L* in their own "
            f"`value_structure` and frame(s) {', '.join(str(n) for n in missing)} do not, so the "
            f"deck's register was compared against a plan for part of it or against nothing at "
            f"all. Write `Frame median L* planned at <n>` into every dossier's value_structure, "
            f"or none of them and a summary span instead. A qualifier is required: `median L* 44` "
            f"reads as some region's median and `frame median L* 44` reads as the frame's"]


def arc_disagreement(storyboard: str) -> list:
    """A summary arc and a per dossier arc that do not agree. Two homes for one figure.

    Silent unless BOTH are complete, because a partial dossier plan is `partial_dossier_plan`'s
    finding and reporting it twice teaches a run to scroll past both.
    """
    span = span_arc(storyboard)
    found, total = dossier_arc(storyboard)
    if not span or total < 3 or len(found) != total or len(span) != total:
        return []
    per = [found[n] for n in sorted(found)]
    if per == span:
        return []
    off = [f"F{n}" for n in range(1, total + 1) if per[n - 1] != span[n - 1]]
    return [f"this storyboard states its value arc twice and the two disagree at "
            f"{', '.join(off)}. The summary span says {[f'{v:g}' for v in span]} and the "
            f"dossiers say {[f'{v:g}' for v in per]}. One of them is what the frames were drawn "
            f"to and the other is what the run will report. Delete one"]


def planned_arc(storyboard: str) -> list:
    """The planned per frame median L*, or `[]` when the deck declares none.

    A DECK THAT DECLARES NO ARC IS THE ORDINARY CASE, not a misread file. Nine of fifteen shipped
    storyboards declare nothing this can read, so a gate that treated silence as a defect would be
    red on most of what this project has published, and a row that is always red is ignored
    exactly as fast as one that is always green.

    A DECK THAT DECLARES ONE THIS CANNOT READ IS NOT THAT CASE, and telling the two apart is
    `unreadable_plan`'s whole job. Returning `[]` for both is the defect this file met on
    2026-09-10, and returning `[]` for a plan written nine times over in the dossiers is the same
    defect it met again on 2026-09-13.

    THE SUMMARY WINS WHERE BOTH EXIST, and `arc_disagreement` is what stops that being a quiet
    choice between two different plans.
    """
    span = span_arc(storyboard)
    if span:
        return span
    found, total = dossier_arc(storyboard)
    if total >= 3 and len(found) == total:
        return [found[n] for n in sorted(found)]
    return []


def measured_arc(base: Path) -> list:
    """The shipped PNGs' per frame median L*, on the grid every prior run measured on.

    ONE IMPLEMENTATION OF THE MEASUREMENT, borrowed rather than repeated. `plan_render_check`
    measures the same figure per frame against the band each dossier declares for itself, and a
    median computed two ways in one repository is GATE_LESSONS 34's finding under the finding:
    the defect was never the regex, it was that there was a second regex at all. The GRID stays
    this file's own, because 270 by 338 is what every prior run's `measurements.json` and
    `ledger/carousel/artwork.json` were written on.
    """
    import plan_render_check as prc
    return [prc.median_lstar(png, ARC_GRID)
            for png in sorted((base / "render").glob("slide-0*.png"))]


def _median(xs: list) -> float:
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def arc_verdict(planned: list, measured: list) -> list:
    """The pure half, so this can be replayed without an image library. Returns problems.

    THE DECK MEDIAN AND NOT THE FRAMES. A per frame rule would fire on every deck, because one
    frame landing eight points off its plan is ordinary and is the sort of thing a run fixes by
    eye. The deck median is the register, and a register that missed by a Munsell step is a plan
    nobody executed.
    """
    if not planned or not measured:
        return []
    if len(planned) != len(measured):
        return [f"the storyboard's value arc declares {len(planned)} frame(s) and the render "
                f"carries {len(measured)}, so the plan and the deck are not describing the same "
                f"deck. One of them is stale, and this refuses to compare them rather than "
                f"guessing which"]
    pm, mm = _median(planned), _median(measured)
    if abs(mm - pm) <= MUNSELL_STEP_L:
        return []
    worst = sorted(zip(range(1, len(planned) + 1), planned, measured),
                   key=lambda r: -abs(r[2] - r[1]))[:3]
    detail = ", ".join(f"F{i} planned {p:g} measured {m:g}" for i, p, m in worst)
    return [f"the deck's median L* measures {mm:g} against its own planned {pm:g}, a miss of "
            f"{abs(mm - pm):.1f} where one Munsell value step is {MUNSELL_STEP_L:g}. That is not "
            f"a deck that came out a little dark, it is a deck rendered at a different value than "
            f"the one that was planned. Furthest three: {detail}. Redraw the frames or rewrite "
            f"the arc, and say in the run record which you did"]


def check_value_arc(base: Path) -> list:
    """THE DECK COMES OUT AT THE VALUE ITS OWN PLAN ASKED FOR.

    THE DEFECT (2026-09-04). The first render of carousel 15 measured deck median L* 6.3 against
    a storyboard plan of 24, with eight of nine frames between 4.5 and 10.1. That is not a dark
    deck, it is an unlit one, and it was found by the showrunner writing a one-off `measure.py`
    AFTER three judges had already been spawned on it. Every deck before it missed its own plan
    too, by ten to nineteen points, and every one of them RECORDED the miss in the artwork ledger
    rather than preventing it.

    This gate exists so a judge never has to find a measurement, and the arc is a measurement.
    """
    sb = base / "storyboard.md"
    if not sb.exists():
        return []
    text = sb.read_text(encoding="utf-8")
    # THE TWO PLAN-SHAPE FINDINGS, BEFORE ANY MEASUREMENT. Both are about whether there is one
    # plan to measure against at all, and neither needs a PNG, so a deck with no render still
    # gets told its plan is in two pieces or in two places.
    shape = partial_dossier_plan(text) + arc_disagreement(text)
    planned = planned_arc(text)
    if shape:
        return shape
    if not planned:
        # THE THIRD STATE, ADDED 2026-09-10, AND THE ROW USED TO PRINT `ok` FOR IT.
        #
        # A declared arc nobody could read and a deck that cleared its arc came out of here as
        # the same empty list, so the group heading read `ok the deck comes out within one
        # Munsell step of its own planned value arc` in both cases. That run only measured its
        # arc at all because a session happened to read the note above and go looking. This is
        # GATE_LESSONS' oldest shape, a green banner measuring something narrower than the thing
        # it appears to certify, and the repair is one line in the storyboard.
        stuck = unreadable_plan(text)
        if stuck:
            return [arc_unread_finding(stuck)]
        # SAID OUT LOUD RATHER THAN PASSED OVER. Nine of fifteen shipped storyboards declare no
        # arc, so this is ordinary, and a run that declares one gets it checked.
        print("      (this storyboard declares no value arc this gate can read, so the deck's "
              "register was compared against nothing. SLIDE_DOSSIER_SPEC.md gives the form)")
        return []
    try:
        measured = measured_arc(base)
    except Exception as exc:                                         # noqa: BLE001
        # A CHECK THAT CANNOT RUN IS NOT A CHECK THAT PASSED. GATE_LESSONS 37: a skip is what a
        # check looks like when it is not needed, and this one is needed, because the plan is
        # right there. It goes in the failure list.
        return [f"this storyboard declares a value arc and the arc could not be measured: {exc}. "
                f"Install Pillow and numpy. A gate that reports clean because it could not look "
                f"is the shape this whole file exists to stop"]
    if not measured:
        return ["this storyboard declares a value arc and there are no slide PNGs under "
                "render/ to measure it against"]
    print(f"      planned {[f'{p:g}' for p in planned]}")
    print(f"      measured {[f'{m:g}' for m in measured]}  "
          f"deck median {_median(measured):g} against a plan of {_median(planned):g}")
    return arc_verdict(planned, measured)


# ------------------------------------------------------------------ driver

def run(date: str, out_root: Path | None = None, articles: Path | None = None,
        assets: Path | None = None) -> int:
    base = Path(out_root or (REPO_ROOT / "out")) / date
    rp = base / "render" / "render_report.json"
    qp = base / "render" / "machine_qa.json"
    if not rp.exists():
        print(f"panel_ready: no render report at {rp}", file=sys.stderr)
        return 2
    report = json.loads(rp.read_text(encoding="utf-8"))
    qa, qa_problems = load_machine_qa(base, report)
    current = check_renders_current(base, assets)
    floor = rubric_contrast_floor()
    # A CHECK THAT CANNOT RUN IS NOT A CHECK THAT PASSED (GATE_LESSONS 37). Contrast read off a QA
    # file that describes other frames, or no file, or frames from before the last edit, is not a
    # reading of this deck.
    contrast = (check_contrast(qa, floor) if not (qa_problems or current) else
                [f"CANNOT RUN: {qp.relative_to(base)} is not a reading of these frames, see above"])

    groups = [
        ("nothing a reader needs is exempt from the gates", check_nothing_exempt(report)),
        ("no published text has a plate through it", check_nothing_occluded(report)),
        ("every slide number in published copy resolves", check_pointers(base, report)),
        ("the render report holds a record of every frame on disk",
         check_report_complete(base, report)),
        ("every frame was rendered after its last edit", current),
        ("machine QA measured the frames that are here now", qa_problems),
        (f"every line clears the rubric's {floor} contrast floor", contrast),
        ("every dossier describes the frame the run made", check_plan_matches(base)),
        ("every ground a dossier calls worked is worked", check_ground(base)),
        ("every figure the plan placed is inside its own frame", check_scene_bounds(base)),
        ("every bleed a dossier declares is one the frame draws", check_bleed_witness(base)),
        ("every published address traces to a claim", check_contacts(base)),
        ("every frame that stands somewhere shows it: its sky, its room, or the inside of "
         "something built", check_sky_in_frame(report, base)),
        ("every universal on every published surface, the web edition included, names its set",
         check_quantifiers(base, articles)),
        (f"the deck comes out within one Munsell step ({MUNSELL_STEP_L:g} L*) of its own "
         f"planned value arc", check_value_arc(base)),
    ]
    problems = [p for _, ps in groups for p in ps]
    for title, ps in groups:
        print(f"  {'ok  ' if not ps else 'NOT READY'}  {title}")
        for p in ps:
            print(f"      - {p}")

    # PRINTED, NEVER FAILED ON. An acceptance band is prose and the number beside it is computed
    # from the plan's own camera, so a disagreement is a thing to READ before the panel rather
    # than a verdict. scene_bounds' docstring carries the argument.
    for line in scene_band_notes(base):
        print(f"  note        {line}")
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

    # ---- THE VALUE ARC, REPLAYED ON THIS RUN'S OWN TWO MEASUREMENTS ---------------------
    #
    # Carousel 15's FIRST render measured a deck median of 6.3 against a plan of 24. The repaired
    # deck measured 23.1 against the same plan. Both arrays below are the real per frame medians
    # off `out/2026-09-04/measurements.json` and the run record, not a fixture invented here.
    PLAN_15 = [24, 18, 21, 13, 88, 32, 28, 17, 25]
    SHIPPED_15 = [25.0, 15.1, 19.8, 14.0, 96.3, 27.2, 24.8, 15.8, 23.1]
    # The first render, eight of nine frames between 4.5 and 10.1 with the one light frame lit.
    FIRST_15 = [6.3, 4.5, 8.1, 5.2, 61.0, 9.4, 10.1, 5.0, 7.7]
    got = arc_verdict(PLAN_15, FIRST_15)
    ok("the first render of carousel 15, 6.3 against a plan of 24, is CAUGHT", bool(got), str(got))
    ok("...and the failure names the size of the miss in Munsell steps",
       bool(got) and "Munsell" in got[0], str(got))
    ok("...and the REPAIRED deck at 23.1 against the same plan passes",
       not arc_verdict(PLAN_15, SHIPPED_15), str(arc_verdict(PLAN_15, SHIPPED_15)))

    # A DECK THAT MISSES BY A LITTLE IS NOT A FINDING. Every deck here misses its plan, and a gate
    # that fires on ordinary behaviour gets switched off. 2026-09-02 planned 30 and measured 20.4.
    ok("a miss of 9.6, inside one Munsell step, is not a finding",
       not arc_verdict([30] * 9, [20.4] * 9))
    ok("...and a miss of 10.1, outside it, is",
       bool(arc_verdict([30] * 9, [19.9] * 9)))

    # A PLAN AND A RENDER OF DIFFERENT LENGTHS IS A STALE PLAN, and comparing them anyway is how
    # a gate invents a failure. It refuses rather than guessing which side moved.
    ok("a plan of eight frames against a render of nine REFUSES rather than comparing",
       bool(arc_verdict(PLAN_15[:8], SHIPPED_15)))
    ok("a deck declaring no arc is silent", not arc_verdict([], SHIPPED_15))

    # THE PER FRAME QUESTION IS NOT ASKED HERE, AND THE COVERAGE IS STATED RATHER THAN INFERRED.
    # 2026-09-16 shipped a deck whose median was 45.9 against a plan of 44, inside a tenth of a
    # Munsell step, with FIVE OF NINE frames outside the band their own dossiers declared and
    # three of those outside by more than twenty points. This gate passed it and was right to:
    # the register was the thing it measures. `plan_render_check` measures each frame against its
    # own declared band and runs at Phase 12b, before this. Both, or a deck can be at the planned
    # register and half drawn to a different plan.
    ok("a deck at its planned register with frames all over the place is NOT this gate's finding",
       not arc_verdict([44] * 9, [78, 77, 51, 34, 46, 21, 77, 44, 13]),
       str(arc_verdict([44] * 9, [78, 77, 51, 34, 46, 21, 77, 44, 13])))

    # THE BORROWED INSTRUMENT, PINNED. `measured_arc` calls `plan_render_check.median_lstar` so
    # this repository holds ONE implementation of this measurement. sRGB 128 is L* 53.6 by the
    # sRGB transfer function, which is a fact about the colour space rather than about our decks,
    # so a drift here is the instrument moving.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _d:
        _base = Path(_d)
        (_base / "render").mkdir()
        try:
            import plan_render_check as _prc
            from PIL import Image as _Im
            _Im.new("RGB", (1080, 1350), (128, 128, 128)).save(
                _base / "render" / "slide-01.png")
            _m = measured_arc(_base)
            ok("measured_arc reads the shared instrument and a mid grey measures L* 53.6",
               _m == [53.6], str(_m))
            ok("...and it is plan_render_check's function, not a second copy of the arithmetic",
               _prc.median_lstar(_base / "render" / "slide-01.png", ARC_GRID) == _m[0])
        except ImportError as exc:                                   # noqa: BLE001
            ok("Pillow is installed, because this gate measures pixels", False, str(exc))

    # ---- THE PARSE RULE, against the two shapes real storyboards actually write ---------
    FENCED = ("**The value arc, planned per frame median L\\***, measured off the PNGs.\n\n"
              "```\nF1  24   the lane\nF2  18   three heights\nF3  21   six in\n"
              "F4  13   the darkest frame\nF5  88   the turn\n```\n\nPlanned deck median **24**.\n")
    ok("the fenced `F1  24` form 2026-09-04 writes is read",
       planned_arc(FENCED) == [24, 18, 21, 13, 88], str(planned_arc(FENCED)))
    INLINE = ("## The value arc\n\nPlanned per frame 32, 40, 28, 26, 24, 40, 68, 30, 38. Planned "
              "deck median near 32.\n")
    ok("the inline form 2026-08-29 writes is read",
       planned_arc(INLINE) == [32, 40, 28, 26, 24, 40, 68, 30, 38], str(planned_arc(INLINE)))
    INLINE2 = "Planned value arc, 34, 22, 40, 58, 44, 71, 30, 47, 26. **Planned, and replaced.**\n"
    ok("the inline form 2026-08-30 writes is read",
       planned_arc(INLINE2) == [34, 22, 40, 58, 44, 71, 30, 47, 26], str(planned_arc(INLINE2)))

    # A MEASUREMENT IS NOT A PLAN. 2026-09-03's storyboard carries only what the render came out
    # at, written after the fact, and reading that as a plan would compare a deck to itself.
    MEASURED_ONLY = ("### The value arc\n\nPer frame median L*, computed:\n\n"
                     "`73.1 · 94.1 · 18.9 · 77.2 · 17.5`, **deck median 73.1**.\n")
    ok("a storyboard that records a MEASUREMENT and no plan declares no arc",
       planned_arc(MEASURED_ONLY) == [], str(planned_arc(MEASURED_ONLY)))
    ok("a comma list nowhere near the value arc declares nothing",
       planned_arc("The frame carries 12, 14, 16 and 18 ticks planned across the scale.") == [],
       str(planned_arc("The frame carries 12, 14, 16 and 18 ticks planned across the scale.")))

    # AGAINST THE REAL STORYBOARDS, because a parser tested only on strings this file wrote agrees
    # with this file. Every shipped storyboard that declares an arc has to still parse into one
    # value per frame, so the day a run writes it a third way this goes red rather than silent.
    parsed = 0
    for p in sorted((REPO_ROOT / "runs" / "carousel").glob("2*")):
        sb = p / "storyboard.md"
        if not sb.exists():
            continue
        txt = sb.read_text(encoding="utf-8")
        arc = planned_arc(txt)
        if not arc:
            continue
        parsed += 1
        frames = len(re.findall(r"```yaml\s*\nslide:\s*\d+", txt))
        ok(f"{p.name}: its declared arc parses into one value per frame "
           f"({len(arc)} of {frames})", len(arc) == frames, str(arc))
    ok("the parse rule was calibrated against real storyboards rather than only fixtures",
       parsed >= 2, f"{parsed} shipped storyboard(s) declare a readable arc")

    # ---- THE THIRD STATE, REPLAYED ON THE SHAPE THAT PRODUCED IT (2026-09-10) ----------
    #
    # The line below is carousel no. 20's plan as it stood when `panel_ready` was first run
    # against it, taken from that run's own account in runs/carousel/2026-09-10/storyboard.md
    # rather than invented here. The word `planned` is in the heading and the nine values are on
    # the NEXT line, and the row above it printed `ok`.
    STUCK = ("## The value arc, planned\n"
             "26, 12, 58, 16, 9, 34, 11, 20, 33, from `compute.py VALUE_ARC`.\n"
             "Deck median **20**, one frame over 50.\n")
    ok("the 2026-09-10 shape, planned on one line and the list on the next, parses to nothing",
       planned_arc(STUCK) == [], str(planned_arc(STUCK)))
    ok("...and it is now reported as a DECLARED arc that could not be read",
       bool(unreadable_plan(STUCK)), "the third state collapsed back into a pass")
    ok("...and the finding names the one-line rule, which is the trap",
       "ONE LINE" in arc_unread_finding(unreadable_plan(STUCK)),
       arc_unread_finding(unreadable_plan(STUCK)))

    # THE REPAIR THAT RUN MADE clears it, which is what makes the finding actionable rather than
    # a row somebody learns to scroll past.
    REPAIRED = ("## The value arc\n"
                "Planned per frame median L*, 26, 12, 58, 16, 9, 34, 11, 20, 33, from "
                "`compute.py VALUE_ARC`.\nDeck median **20**, one frame over 50.\n")
    ok("...and the one-line repair reads as nine planned values",
       planned_arc(REPAIRED) == [26, 12, 58, 16, 9, 34, 11, 20, 33], str(planned_arc(REPAIRED)))
    ok("...so a deck whose arc parses raises no third-state finding",
       not unreadable_plan(REPAIRED), str(unreadable_plan(REPAIRED)))

    # AND THE TWO CASES THIS MUST NOT FIRE ON, because a row that is always red is ignored
    # exactly as fast as one that is always green.
    ok("a storyboard declaring no arc at all raises no finding",
       not unreadable_plan("## The frames\n\nNothing about lightness here.\n"))
    ok("2026-09-03's measurement-only paragraph is not read as an unreadable plan",
       not unreadable_plan(MEASURED_ONLY), str(unreadable_plan(MEASURED_ONLY)))

    # AGAINST EVERY SHIPPED STORYBOARD, because a fixture written beside a detector agrees with
    # it. None of the twenty may raise this, and 2026-09-03 is the one that nearly did: it
    # narrates a wrong arc line in prose, separated by middots, which is why the pattern that
    # decides this takes commas only.
    noisy = [p.name for p in sorted((REPO_ROOT / "runs" / "carousel").glob("2*"))
             if (p / "storyboard.md").exists()
             and unreadable_plan((p / "storyboard.md").read_text(encoding="utf-8"))]
    ok("no shipped storyboard is reported as declaring an arc nobody could read", not noisy,
       str(noisy))

    # ---- THE FOURTH STATE, REPLAYED ON CAROUSEL 22 (2026-09-13) ------------------------
    #
    # Nine dossiers, each declaring its own frame's planned median in `art.value_structure`, and
    # no summary paragraph naming the value arc anywhere in the file. The strings below are
    # carousel 22's own, quoted off runs/carousel/2026-09-13/storyboard.md, including slide 5's
    # `at` where the other eight write `planned at` and slide 3's castor acceptance item, which
    # is the sentence a looser parser reads as a plan of 4.
    PLAN_22 = [22, 46, 34, 30, 26, 18, 72, 26, 28]
    TAIL_22 = ["planned at 22.", "planned at 46.", "planned at 34.", "planned at 30.", "at 26.",
               "planned at 18, the deck's floor.", "planned at 72.", "planned at 26.",
               "planned at 28."]
    ACCEPT_22 = ("  - all four castors carry a contact shadow whose median L* differs from the "
                 "floor beside it by 4 or more\n")
    BOARD_22 = "".join(
        f"```yaml\nslide: {i}\nlayout: DIAGRAM\nart:\n"
        f"  technique: \"screenprint\"\n"
        f"  value_structure: >\n"
        f"    The print screens the ground and the plate is the lightest mass. Frame median "
        f"L* {t}\n"
        f"  motion: \"left to right\"\nacceptance:\n{ACCEPT_22 if i == 3 else ''}"
        f"  - \"the hook is legible at 432px\"\n```\n\n"
        for i, t in enumerate(TAIL_22, 1))
    ok("carousel 22's plan, nine dossiers and no summary span, read as nothing by the OLD reader",
       span_arc(BOARD_22) == [], str(span_arc(BOARD_22)))
    # THE OLD THIRD STATE COULD NOT SEE IT EITHER, and this is the reason rather than a retelling
    # of it: `unreadable_plan` looks only INSIDE a span that names the value arc, and this file
    # has no such span, so there was nothing for it to look in. The gate printed `ok`.
    ok("...and there is no span naming the value arc, which is why the third state was blind",
       arc_spans(BOARD_22) == [], str(arc_spans(BOARD_22)))
    ok("...and it is now read as nine planned values",
       planned_arc(BOARD_22) == PLAN_22, str(planned_arc(BOARD_22)))
    ok("...and slide 3's castor acceptance item did not become a plan of 4",
       planned_arc(BOARD_22)[2] == 34, str(planned_arc(BOARD_22)))

    # THE MISS ITSELF, off the nine PNGs this run measured. Deck median 13.5 against a plan of 28.
    SHIPPED_22 = [13.5, 28.8, 11.6, 11.1, 18.8, 11.1, 41.1, 11.1, 14.1]
    got = arc_verdict(PLAN_22, SHIPPED_22)
    ok("carousel 22's collapse, 13.5 against a plan of 28, is CAUGHT", bool(got), str(got))
    ok("...and the finding names the 14.5 the run found by hand after it shipped",
       bool(got) and "14.5" in got[0], str(got))

    # A PARTIAL PLAN IS ITS OWN FINDING and not a stale-plan diagnosis. 2026-09-11's real shape:
    # six dossiers carry the qualifier and three write a bare `median L* 44`.
    PARTIAL = BOARD_22.replace("Frame median L* at 26.", "Its median L* 26.")
    ok("eight of nine dossiers declaring a median is reported as a PARTIAL plan",
       bool(partial_dossier_plan(PARTIAL)), str(partial_dossier_plan(PARTIAL)))
    ok("...and the finding names the frame that is missing",
       bool(partial_dossier_plan(PARTIAL)) and "frame(s) 5" in partial_dossier_plan(PARTIAL)[0],
       str(partial_dossier_plan(PARTIAL)))
    ok("...and an eight-value plan is NOT silently compared against a nine frame render",
       planned_arc(PARTIAL) == [], str(planned_arc(PARTIAL)))
    ok("...and a complete plan raises no partial finding",
       not partial_dossier_plan(BOARD_22), str(partial_dossier_plan(BOARD_22)))

    # TWO HOMES FOR ONE FIGURE. A summary span and a dossier plan that disagree is a deck whose
    # run record will report a different arc than the one the frames were drawn to.
    BOTH_AGREE = ("## The value arc\n\nPlanned per frame 22, 46, 34, 30, 26, 18, 72, 26, 28.\n\n"
                  + BOARD_22)
    BOTH_DIFFER = BOTH_AGREE.replace("Planned per frame 22, 46", "Planned per frame 24, 46")
    ok("a summary span agreeing with the dossiers raises nothing",
       not arc_disagreement(BOTH_AGREE), str(arc_disagreement(BOTH_AGREE)))
    ok("...and one that disagrees at F1 is CAUGHT and names F1",
       bool(arc_disagreement(BOTH_DIFFER)) and "F1" in arc_disagreement(BOTH_DIFFER)[0],
       str(arc_disagreement(BOTH_DIFFER)))
    ok("...and the summary is what planned_arc returns where both exist",
       planned_arc(BOTH_DIFFER)[0] == 24, str(planned_arc(BOTH_DIFFER)))

    # THE FALSE POSITIVES THIS MUST NOT PRODUCE, taken off real acceptance items rather than
    # imagined. All three talk about a median, none of them states the frame's planned one, and
    # all three sit outside `value_structure` where this does not look.
    for label, item in (
            ("a region's median, 2026-09-07",
             "  - \"the punch column's median L* is at least 10 below the rail face median\"\n"),
            ("a floor written at a viewport, 2026-09-10",
             "  - \"the frame's median L* at 432px is 45 or higher\"\n"),
            ("a relative shadow, 2026-09-13",
             "  - a contact shadow whose median L* differs from the floor by 4 or more\n")):
        blk = ("```yaml\nslide: 1\nart:\n  value_structure: >\n    A dark ground.\n"
               "  motion: \"none\"\nacceptance:\n" + item + "```\n")
        found, _total = dossier_arc(blk * 3)
        ok(f"{label} is not read as a planned frame median", not found, str(found))

    # AGAINST EVERY SHIPPED STORYBOARD AGAIN, for the two new findings. A fixture written beside
    # a detector agrees with it; twenty two real plans do not.
    partials, clashes, dossier_read = [], [], []
    for p in sorted((REPO_ROOT / "runs" / "carousel").glob("2*")):
        sb = p / "storyboard.md"
        if not sb.exists():
            continue
        txt = sb.read_text(encoding="utf-8")
        if partial_dossier_plan(txt):
            partials.append(p.name)
        if arc_disagreement(txt):
            clashes.append(p.name)
        found, total = dossier_arc(txt)
        if total >= 3 and len(found) == total:
            dossier_read.append(p.name)
    ok("no shipped storyboard whose arc already parses is reported as a partial plan",
       not [n for n in partials if planned_arc(
           (REPO_ROOT / "runs" / "carousel" / n / "storyboard.md").read_text(encoding="utf-8"))],
       str(partials))
    ok("no shipped storyboard states its arc twice and disagrees with itself", not clashes,
       str(clashes))
    ok("the dossier reader was calibrated against real storyboards rather than only fixtures",
       len(dossier_read) >= 1, f"{len(dossier_read)} shipped storyboard(s): {dossier_read}")

    # EVERY CHECK MUST BE REACHABLE. A gate whose loader silently returns nothing reports clean
    # forever, which is the shape craft_floor shipped when it read a key qa.py never wrote.
    for fn, name in ((check_nothing_exempt, "check_nothing_exempt"),
                     (check_nothing_occluded, "check_nothing_occluded")):
        ok(f"{name} runs on an empty report without raising",
           fn({"slides": []}) == [])

    # THE TWO CHECKS WIRED IN ON 2026-09-14, EACH REPLAYED AGAINST THE DEFECT IT EXISTS FOR.
    # A group added to the list above and never seen to go red is a row in a report, not a gate.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _t:
        _b = Path(_t) / "2026-09-14"
        (_b / "slides").mkdir(parents=True)
        (_b / "slides" / "slide-01.html").write_text(
            "<script>var W = 1080, H = 1350;"
            "var cam = { w: W, h: H, eye: 1.65, horizon: 940, f: 820, light: { az: -68, el: 14 } };"
            "var hand = TXFIG.figure({ height: 1.70 });"
            "S.sprite(hand, { X: -13, Z: 9, fade: false });</script>", encoding="utf-8")
        ok("carousel no. 24's off-frame cover figure is CAUGHT before the panel",
           bool(check_scene_bounds(_b)), str(check_scene_bounds(_b)))
        (_b / "slides" / "slide-01.html").write_text(
            (_b / "slides" / "slide-01.html").read_text(encoding="utf-8")
            .replace("X: -13, Z: 9", "X: -9.2, Z: 27"), encoding="utf-8")
        ok("...and the repair that shipped is clean", not check_scene_bounds(_b))

        # THE SKY CHECK WIRED IN ON 2026-09-26, replayed on the line the engine prints for no. 34's
        # frame 4, and on the clean frame beside it.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from print_ban import NO_SKY
        _sky = {"slides": [
            {"file": "slide-03.html", "console_errors": []},
            {"file": "slide-04.html", "console_errors": [NO_SKY + ". This frame calls TXT.sky and its "
                                                         "camera shows none of it"]}]}
        got = check_sky_in_frame(_sky)
        ok("a frame whose camera shows none of the sky it calls is CAUGHT before the panel, and named",
           len(got) == 1 and got[0].startswith("slide-04.html"), str(got))
        ok("...and a frame that shows its sky is clean",
           check_sky_in_frame({"slides": [_sky["slides"][0]]}) == [])
        from print_ban import SKY_SHOWN
        ok("...and so is a preview at the ground withdrawn by the renderer's kept snapshot",
           check_sky_in_frame({"slides": [{"file": "slide-04.html", "console_errors": [
               NO_SKY + " [r1]. a preview", SKY_SHOWN + " [r1]. the kept snapshot"]}]}) == [])
        from print_ban import NO_ROOM, ROOM_SHOWN, VERDICT_SINCE, NO_RENDER
        ok("a frame whose kept render came out black is CAUGHT before the panel, and named",
           [p[:13] for p in check_sky_in_frame({"slides": [{"file": "slide-05.html", "console_errors": [
               NO_RENDER + " [r1]. its render came out black"]}]})] == ["slide-05.html"])
        ok("a frame that builds only a room and shows too little of it is CAUGHT, and named",
           [p[:13] for p in check_sky_in_frame({"slides": [{"file": "slide-07.html", "console_errors": [
               NO_ROOM + " [r1]. too little of the room"]}]})] == ["slide-07.html"])
        # A FRAME THAT PRINTED NO VERDICT (Codex, PR 369), on a run dated after VERDICT_SINCE, whose
        # source calls TXT.sky before its kept snapshot: its pixels never went through the snapshot.
        with _tf.TemporaryDirectory() as _v:
            _vb = Path(_v) / "2026-09-27"
            (_vb / "slides").mkdir(parents=True)
            (_vb / "slides" / "slide-02.html").write_text(
                "<script type=\"module\">import * as THREE from '@@ASSETS@@/js/three.module.min.js';"
                "import { init } from '@@ASSETS@@/js/txthree.js';const TXT = init(THREE);"
                "const R = TXT.setup(cv);TXT.sky(R);const s = await TXT.snapshot(R);</script>",
                encoding="utf-8")
            _silent = {"slides": [{"file": "slide-02.html", "console_errors": []}]}
            ok("a world frame whose render printed no verdict is CAUGHT before the panel",
               any(p.startswith("slide-02.html") and "no verdict" in p
                   for p in check_sky_in_frame(_silent, _vb)), str(check_sky_in_frame(_silent, _vb)))
            ok("...and with the engine's clean verdict it is clean",
               check_sky_in_frame({"slides": [{"file": "slide-02.html", "console_errors": [
                   SKY_SHOWN + " [r1]. A verdict, not a defect"]}]}, _vb) == [])
            _early = Path(_v) / VERDICT_SINCE
            (_early / "slides").mkdir(parents=True)
            (_early / "slides" / "slide-02.html").write_text(
                (_vb / "slides" / "slide-02.html").read_text(encoding="utf-8"), encoding="utf-8")
            ok("...while a run dated VERDICT_SINCE, before the engine printed one, is not judged on it",
               check_sky_in_frame(_silent, _early) == [])
        # BUILT FROM PARTS, for the reason the flag check below gives: a literal needle matches itself.
        ok("...and the group is in the list the run reads, with the run directory",
           ("check_sky_in_frame" + "(report, base)") in Path(__file__).read_text(encoding="utf-8"))

        # THE CHECK WIRED IN ON 2026-09-17, replayed on carousel no. 27's own frame 4 numbers.
        # Without a storyboard this returns nothing, so the first assertion is that the check
        # is reading the plan at all rather than reporting clean on an absence.
        _bb = Path(_t) / "2026-09-17"
        (_bb / "slides").mkdir(parents=True)
        _plan = ("# Storyboard\n\n```yaml\nslide: 4\nlayout: CLOSE_CROP\njob: a job\n"
                 "primary_image:\n  subject: \"a printed announcement\"\n"
                 "  rect: [0, 396, 1080, 954]\n  bleeds: [left, right, bottom]\naccent: none\n```\n")
        (_bb / "storyboard.md").write_text(_plan, encoding="utf-8")
        (_bb / "slides" / "slide-04.html").write_text(
            "<script>N.sheet(cx, { x: -112, y: 366, w: 1304, h: 832, rot: 0.005 });</script>",
            encoding="utf-8")
        ok("carousel no. 27's bottom bleed that stops 152 px short is CAUGHT before the panel",
           any("declares bottom" in p for p in check_bleed_witness(_bb)),
           str(check_bleed_witness(_bb)))
        (_bb / "slides" / "slide-04.html").write_text(
            "<script>N.sheet(cx, { x: -112, y: 366, w: 1304, h: 984, rot: 0.005 });</script>",
            encoding="utf-8")
        ok("...and a sheet drawn to the bottom edge is clean on the SAME declaration",
           not check_bleed_witness(_bb), str(check_bleed_witness(_bb)))
        for _f in (_bb / "slides").glob("*.html"):
            _f.unlink()
        ok("...and a run with no slide HTML is a check that CANNOT RUN, never a clean one",
           any("CANNOT RUN" in p for p in check_bleed_witness(_bb)),
           str(check_bleed_witness(_bb)))

        (_b / "claims.json").write_text(
            json.dumps({"claims": [{"id": "c25", "text": "the notice names no load",
                                    "url": "https://www.ercot.com/services"}]}), encoding="utf-8")
        (_b / "render_report.json").write_text(json.dumps(
            {"slides": [{"file": "slide-02.html", "text_nodes": [
                {"text": "Questions to BatchZero@ercot.com"}]}]}), encoding="utf-8")
        ok("carousel no. 24's fabricated address is CAUGHT before the panel",
           bool(check_contacts(_b)), str(check_contacts(_b)))
        (_b / "render_report.json").write_text(json.dumps(
            {"slides": [{"file": "slide-02.html", "text_nodes": [
                {"text": "www.ercot.com/services"}]}]}), encoding="utf-8")
        ok("...and the host a cited claim carries is clean", not check_contacts(_b))

    # THE CHECK WIRED IN ON 2026-09-24, replayed END TO END through `run()`, because a function
    # this file defines and never calls is GATE_LESSONS 14: a self-test is not wiring. The deck is
    # the smallest one every other group reads as clean, so the only thing that can change the exit
    # code between the two runs is the web edition. The sentence is carousel no. 33's own, from
    # `ledger/articles/2026-09-24.json` as committed in 3dcc68ea, which reached a round 2 judge.
    import io as _io
    import contextlib as _cl
    with _tf.TemporaryDirectory() as _t:
        _root = Path(_t)
        _q = _root / "2026-09-24"
        (_q / "render").mkdir(parents=True)
        (_q / "slides").mkdir()
        (_q / "render" / "render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-01.html", "text_nodes": [{"text": "The pod picks the spot",
                                                      "font_px": 40}]}]}), encoding="utf-8")
        (_q / "slides" / "slide-01.html").write_text(
            "<html><body><h1>The pod picks the spot</h1></body></html>", encoding="utf-8")
        import os as _os
        _rpt = _q / "render" / "render_report.json"
        _mqa = _q / "render" / "machine_qa.json"

        def _qa_at(offset, slides=("slide-01.html",)):
            """A machine QA file `offset` seconds after the render report, on the clock, so the
            file-time comparison never depends on how fast this test runs."""
            _mqa.write_text(json.dumps({"slides": [{"file": f, "fails": [], "warns": []}
                                                   for f in slides]}), encoding="utf-8")
            _t = _rpt.stat().st_mtime + offset
            _os.utime(_mqa, (_t, _t))

        _qa_at(2)
        (_q / "storyboard.md").write_text("```yaml\nslide: 1\nlayout: FULL_BLEED\n```\n",
                                          encoding="utf-8")
        _arts = _root / "articles"
        _arts.mkdir()

        def _edition(para):
            (_arts / "2026-09-24.json").write_text(json.dumps({"sections": [{"paragraphs": [
                {"text": para, "claims": ["c18"]}]}]}), encoding="utf-8")

        _assets = _root / "assets"
        (_assets / "js" / "deck").mkdir(parents=True)

        def _printed():
            buf = _io.StringIO()
            with _cl.redirect_stdout(buf), _cl.redirect_stderr(_io.StringIO()):
                code = run("2026-09-24", out_root=_root, articles=_arts, assets=_assets)
            return buf.getvalue() + f"\nexit {code}"

        def _run():
            with _cl.redirect_stdout(_io.StringIO()), _cl.redirect_stderr(_io.StringIO()):
                return run("2026-09-24", out_root=_root, articles=_arts, assets=_assets)

        _edition("People appear elsewhere in the draft too.")
        ok("the smallest clean deck, with the repaired web edition, is ready to be scored",
           _run() == 0, "some other group is red on the fixture, so this case proves nothing")

        # MACHINE QA THAT ISN'T A READING OF THESE FRAMES (Codex, PR 369). Each case through run(),
        # on the deck the case above proved clean, so the QA file is the only thing that changed.
        _rep = json.loads(_rpt.read_text(encoding="utf-8"))
        _mqa.unlink()
        ok("a run with no machine QA is not ready: a missing file read as clean until 2026-09-26",
           _run() == 1 and any("missing" in p for p in load_machine_qa(_q, _rep)[1]),
           str(load_machine_qa(_q, _rep)[1]))
        _qa_at(-60)
        ok("machine QA older than the render report is stale, and the panel waits",
           _run() == 1 and any("predates" in p for p in load_machine_qa(_q, _rep)[1]),
           str(load_machine_qa(_q, _rep)[1]))
        _qa_at(2)
        # A real frame with a worked ground, so the ground group reads it as clean and the only
        # thing that can turn this red is its age.
        _png = _q / "render" / "slide-01.png"
        try:
            from PIL import Image as _Im
            import numpy as _np
            _Im.fromarray(_np.random.default_rng(7).integers(0, 256, (80, 64), dtype=_np.uint8)
                          ).save(_png)
        except ImportError:
            _png.write_bytes(b"\x89PNG\r\n\x1a\n")
        _t = _mqa.stat().st_mtime + 60
        _os.utime(_png, (_t, _t))
        ok("a frame re-rendered after qa.py ran is stale too, the render --only case",
           _run() == 1 and any("predates" in p for p in load_machine_qa(_q, _rep)[1]),
           str(load_machine_qa(_q, _rep)[1]))
        _qa_at(120)
        ok("...and qa.py run again after that frame clears it", _run() == 0,
           str(load_machine_qa(_q, _rep)[1]))
        # A FRAME EDITED AFTER ITS RENDER (Codex, PR 369). The repair's render.py --only named another
        # frame, so the PNG, its report record and the QA qa.py refreshed from that PNG all predate it.
        _src = _q / "slides" / "slide-01.html"
        _html = _src.read_text(encoding="utf-8")

        def _at(path, t):
            _os.utime(path, (t, t))

        _edit = _png.stat().st_mtime + 30
        _at(_src, _edit)
        ok("a slide edited after its PNG stops the panel, and names the frame and the edit",
           _run() == 1 and any("predates the last edit to slide-01.html" in p and "--only 1" in p
                               for p in check_renders_current(_q, _assets)),
           str(check_renders_current(_q, _assets)))
        ok("...and its contrast is a check that CANNOT RUN, not a clean one",
           "CANNOT RUN" in _printed(), "contrast read clean off pixels from before the edit")
        # the chassis the frame loads, edited after the PNG, stales the frame the same way
        _deck = _assets / "js" / "deck" / "2026-09-24-test.js"
        _deck.write_text("window.DECK = 1;", encoding="utf-8")
        _src.write_text(_html.replace("</body>", '<script src="@@ASSETS@@/js/deck/2026-09-24-test.js">'
                                                 '</script></body>'), encoding="utf-8")
        _at(_src, _png.stat().st_mtime - 30)
        _at(_deck, _png.stat().st_mtime + 30)
        ok("a deck chassis edited after a frame's PNG stops the panel, and names the chassis",
           _run() == 1 and any("assets/js/deck/2026-09-24-test.js" in p
                               for p in check_renders_current(_q, _assets)),
           str(check_renders_current(_q, _assets)))
        # a PNG rendered after the edit, and a report from before it: the crash after the screenshot
        _at(_png, _deck.stat().st_mtime + 5)
        _at(_rpt, _deck.stat().st_mtime - 5)
        _qa_at(20)
        ok("a render report older than the edit stops the panel even when the PNG is newer",
           _run() == 1 and any(p.startswith("render/render_report.json predates")
                               for p in check_renders_current(_q, _assets)),
           str(check_renders_current(_q, _assets)))
        _at(_rpt, _png.stat().st_mtime)
        _qa_at(10)
        ok("...and the frame rendered again, report and QA after it, is ready", _run() == 0,
           str(check_renders_current(_q, _assets)) + str(load_machine_qa(_q, _rep)[1]))
        _src.write_text(_html, encoding="utf-8")
        _deck.unlink()
        _at(_src, _png.stat().st_mtime - 30)
        _png.unlink()
        _qa_at(2, slides=())
        ok("machine QA with no record of a rendered frame never measured it",
           _run() == 1 and any(p.startswith("slide-01.html") for p in load_machine_qa(_q, _rep)[1]),
           str(load_machine_qa(_q, _rep)[1]))
        _mqa.write_text("{", encoding="utf-8")
        ok("machine QA that can't be read is not ready either",
           _run() == 1 and any("can't be read" in p for p in load_machine_qa(_q, _rep)[1]),
           str(load_machine_qa(_q, _rep)[1]))
        _qa_at(2)
        ok("...and with qa.py run again after the render, the same deck is ready", _run() == 0,
           str(load_machine_qa(_q, _rep)[1]))

        # A FRAME ON DISK THE RENDER REPORT NEVER RECORDED (Codex, PR 369): the report a repair's
        # `render.py --only` writes after discarding an unreadable one holds the repaired frame alone.
        _extra = _q / "slides" / "slide-02.html"
        _extra.write_text("<html><body><h1>The second frame</h1></body></html>", encoding="utf-8")
        ok("a frame on disk the render report holds no record of stops the panel, and is named",
           _run() == 1 and any("no record of slide-02.html" in p
                               for p in check_report_complete(_q, _rep)),
           str(check_report_complete(_q, _rep)))
        _extra.unlink()
        ok("...and without it the same deck is ready again", _run() == 0,
           str(check_report_complete(_q, _rep)))
        # THE OTHER DIRECTION (Codex, PR 369): a record and a PNG for a frame a repair deleted.
        _two = {"slides": list(_rep["slides"]) + [{"file": "slide-02.html", "text_nodes": []}]}
        ok("a report record for a frame no longer in slides/ stops the panel, and is named",
           any("still holds slide-02.html" in p for p in check_report_complete(_q, _two)),
           str(check_report_complete(_q, _two)))
        _orphan = _q / "render" / "slide-03.png"
        try:
            from PIL import Image as _Im
            import numpy as _np
            _Im.fromarray(_np.random.default_rng(3).integers(0, 256, (80, 64), dtype=_np.uint8)
                          ).save(_orphan)
        except ImportError:
            _orphan.write_bytes(b"\x89PNG\r\n\x1a\n")
        ok("a PNG in render/ with no source in slides/ stops the panel, because the PDF would ship it",
           _run() == 1 and any("slide-03.png" in p and "assemble.py" in p
                               for p in check_report_complete(_q, _rep)), str(check_report_complete(_q, _rep)))
        _orphan.unlink()
        # A QA RECORD THAT CARRIES A FAIL (Codex, PR 369): qa.py files "png missing" and exits 0.
        _mqa.write_text(json.dumps({"slides": [{"file": "slide-01.html", "fails": ["png missing"],
                                                "warns": []}]}), encoding="utf-8")
        _t = _rpt.stat().st_mtime + 2
        _os.utime(_mqa, (_t, _t))
        ok("a machine QA record that failed its frame, png missing, stops the panel",
           _run() == 1 and any("png missing" in p for p in load_machine_qa(_q, _rep)[1]),
           str(load_machine_qa(_q, _rep)[1]))
        _qa_at(2)
        ok("...and with qa.py clean again, the same deck is ready", _run() == 0,
           str(load_machine_qa(_q, _rep)[1]))
        _edition("A person enters in one sentence.")
        ok("carousel no. 33's 'A person enters in one sentence' in the web edition stops the "
           "panel", _run() == 1, "the deck reached the judges")
        ok("...and the finding names the web edition and the exclusive count",
           any("web edition" in p and "exclusive count" in p
               for p in check_quantifiers(_q, _arts)), str(check_quantifiers(_q, _arts)))

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
