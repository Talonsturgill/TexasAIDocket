#!/usr/bin/env python3
"""Bind a three-frame art review to its rendered images and source.

The cover, an evidence frame and the close are reviewed before the other six
frames are built. Darkness is measured by value_register; visual judgement
belongs to the reviewer. A recorded approval never survives a changed image.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SINCE = "2026-10-07"  # first new run is October 8th; shipped history is preserved
ROLES = ("cover", "evidence", "close")
STUDIO_SINCE = "2026-10-16"

# THE BESPOKE ROUTE (weekly machine pass 2026-11-18, queue art-preflight-has-no-bespoke-route,
# nos. 78, 80 and 81). A bespoke run has no three-frame audition: each frame is scored cold by its
# own carousel-slide-critic, and three runs in a row then assembled this review BY HAND from those
# verdicts and re-assembled it after every repair of frame 1, the hardest frame or the close.
# `--write --critics <file>` binds the critics' own hand-backs instead. Nothing the review proves
# gets weaker: the critic's verdict must be `ship` at or above bespoke.json `critic_ship`, carry all
# six points of THE SLIDE BAR, and name the SHA-256 of the exact render it read, which must equal
# the render bound here. A changed image therefore still needs a new critic. A source edit that
# leaves the render byte-identical rebinds to the same verdict, because the critic judged pixels.
# Dated so it applies only from the first run after the pass: a run dated on or before
# CRITIC_SINCE can't use it, and the art director's shape is checked exactly as before.
CRITIC_SINCE = "2026-11-18"
CRITIC_SOURCE = "carousel-slide-critic"
# The six points the critic hands back (.claude/agents/carousel-slide-critic.md, "Hand back").
CRITIC_POINTS = ("only_this_sentence", "one_idea", "composed", "crafted", "unlike_neighbours", "honest")


def bespoke_config() -> dict:
    return json.loads((ROOT / "config/carousel/bespoke.json").read_text())


def critic_problems(frame: dict, render_digest: str | None, run: str) -> list[str]:
    """A slide critic's hand-back stands in for the art director's reading of one frame."""
    n = frame.get("slide")
    cfg = bespoke_config()
    start = cfg.get("bespoke_from")
    if not (re.fullmatch(r"\d{4}-\d{2}-\d{2}", run) and run > CRITIC_SINCE
            and isinstance(start, str) and run >= start):
        return [f"frame {n}: a slide critic verdict binds only a bespoke run dated after {CRITIC_SINCE}"]
    critic = frame.get("critic")
    if not isinstance(critic, dict) or critic.get("slide") != n:
        return [f"frame {n}: the critic hand-back is missing or names another slide"]
    out = []
    score, bar = critic.get("score"), cfg["artists"]["critic_ship"]
    if critic.get("verdict") != "ship" or type(score) not in (int, float) or not math.isfinite(score) or score < bar:
        out.append(f"frame {n}: the slide critic did not ship it at {bar} or more; repair and re-score the frame")
    points = critic.get("points")
    if (not isinstance(points, dict) or set(points) != set(CRITIC_POINTS)
            or not all(type(v) in (int, float) and math.isfinite(v) for v in points.values())):
        out.append(f"frame {n}: the critic hand-back must score all six points of THE SLIDE BAR")
    if not isinstance(critic.get("fixes"), list):
        out.append(f"frame {n}: the critic hand-back must carry its fixes list")
    if not render_digest or frame.get("render_sha256") != render_digest:
        out.append(f"frame {n}: the critic read a different render; score this exact image again")
    return out


def load_critics(path: Path) -> dict:
    """Hand-backs, each with the `render_sha256` of the PNG the critic was given, keyed by slide."""
    data = json.loads(path.read_text())
    rows = data.get("frames", []) if isinstance(data, dict) else data
    out = {}
    for row in rows:
        if not isinstance(row, dict) or type(row.get("slide")) is not int:
            raise ValueError("each critic hand-back needs its integer slide")
        out[row["slide"]] = row
    return out


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def asset_paths(html: Path) -> set[str]:
    return {"assets/" + rel for rel in re.findall(
        r"@@ASSETS@@/(js/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_.-]+\.js)", html.read_text())}


def inputs(base: Path, selected: list[int], assets: Path) -> dict:
    files = {}
    for n in selected:
        html = base / "slides" / f"slide-{n:02}.html"
        png = base / "render" / f"slide-{n:02}.png"
        for path in (html, png):
            files[str(path.relative_to(base))] = sha(path)
        # Shared renderers and the chassis can change pixels without changing the HTML.
        for name in sorted(asset_paths(html)):
            files[name] = sha(assets / name.removeprefix("assets/"))
    return files


def review_problems(review: dict, selected: list[int], inputs_map: dict | None = None,
                    run: str = "") -> list[str]:
    out = []
    if review.get("decision") != "accept":
        out.append("art preflight needs an accepted visual review; repair the named frames")
    frames = review.get("frames", [])
    if not isinstance(frames, list):
        return out + ["review.frames must be a list"]
    if [f.get("slide") for f in frames if isinstance(f, dict)] != selected:
        out.append("the review must cover the selected cover, evidence frame and close in order")
    for f, role in zip(frames, ROLES):
        if not isinstance(f, dict):
            out.append("each reviewed frame must be an object")
            continue
        if f.get("role") != role:
            out.append(f"frame {f.get('slide')}: expected role {role}")
        if f.get("source") == CRITIC_SOURCE:
            out.extend(critic_problems(f, (inputs_map or {}).get(f"render/slide-{f.get('slide'):02}.png")
                                       if type(f.get("slide")) is int else None, run))
            continue
        for field in ("subject", "visual_consequence", "weakness", "repair"):
            if not isinstance(f.get(field), str) or not f[field].strip():
                out.append(f"frame {f.get('slide')}: reviewer must record {field}")
    return out


def frame_inputs(digests: dict, n: int, base: Path) -> dict:
    own = {f"slides/slide-{n:02}.html", f"render/slide-{n:02}.png"}
    own.update(asset_paths(base / "slides" / f"slide-{n:02}.html"))
    return {k: v for k, v in digests.items() if k in own}


def studio_problems(record: dict, base: Path) -> list[str]:
    """The rehearsal includes the hardest frame and reviews its finished image at feed size."""
    plan = record.get("plan", {})
    if plan.get("hardest_frame") != record["selected"][1]:
        return ["the art audition must include the plan's hardest frame"]
    out = []
    for key in ("visual_argument", "build_risk", "distinct_from_recent"):
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            out.append(f"art_plan.json needs {key}")
    for frame in record.get("review", {}).get("frames", []):
        n = frame.get("slide")
        if frame.get("inputs") != frame_inputs(record["inputs"], n, base):
            out.append(f"frame {n}: its review is not bound to its source, image and shared assets")
        if frame.get("source") == CRITIC_SOURCE:
            continue  # its judgement is the critic's six points, checked in review_problems
        for key in ("encoding_reads", "dominant_subject_finished", "feed_legible"):
            if frame.get(key) is not True:
                out.append(f"frame {n}: {key} needs a positive visual judgement")
    return out


def check(base: Path, assets: Path = ROOT / "assets", archived: bool = False) -> list[str]:
    path = base / "art_preflight.json"
    try:
        record = json.loads(path.read_text())
        selected = record["selected"]
        if (not isinstance(selected, list) or len(selected) != 3 or selected[0] != 1
                or not all(type(n) is int for n in selected) or not 1 < selected[1] < selected[2]):
            return ["art preflight must select frame 1, an evidence frame and the final frame"]
        numbers = [int(p.stem.split("-")[1]) for p in (base / "slides").glob("slide-*.html")]
        if not numbers or selected[-1] != max(numbers):
            return ["art preflight does not include the final frame"]
        required = {f"{folder}/slide-{n:02}.{extension}" for n in selected
                    for folder, extension in (("slides", "html"), ("render", "png"))}
        if not required.issubset(record["inputs"]):
            return ["art preflight input list omits a selected source or image"]
        if any(name not in required and not re.fullmatch(r"assets/js/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_.-]+\.js", name)
               for name in record["inputs"]):
            return ["art preflight input list contains a path outside its three-frame proof"]
        if archived and "shipped_inputs" in record:
            # ship_images replaces working PNGs with measured WebP encodes. Keep
            # the original review intact and verify the delivered bytes separately.
            from ship_images import QUALITY_FLOOR_DB
            expected = record["shipped_inputs"]
            htmls = {f"slides/slide-{n:02}.html" for n in selected}
            images = {row["to"] for row in record["encodings"]}
            if set(expected) != htmls | images or len(images) != 3 or len(record["encodings"]) != 3:
                return ["the delivered art proof must contain all three sources and images"]
            for n, row in zip(selected, record["encodings"]):
                if (row["to"] not in (f"slide-{n:02}.png", f"slide-{n:02}.webp")
                        or row["from_sha256"] != record["inputs"][f"render/slide-{n:02}.png"]
                        or expected[row["to"]] != row["to_sha256"]
                        or not math.isfinite(row["psnr_db"]) or row["psnr_db"] < QUALITY_FLOOR_DB):
                    return ["a delivered image is not bound to its reviewed render and quality floor"]
                if expected[f"slides/slide-{n:02}.html"] != record["inputs"][f"slides/slide-{n:02}.html"]:
                    return ["a delivered source differs from the reviewed source"]
            current = {name: sha(base / name) for name in expected}
        else:
            current = inputs(base, selected, assets) if not archived else {
                name: sha(base / name) for name in record["inputs"] if not name.startswith("assets/")}
            expected = {k: v for k, v in record["inputs"].items()
                        if not archived or not k.startswith("assets/")}
        if set(expected) != set(current):
            return ["art preflight input list is incomplete; rebuild the three-frame proof"]
        out = [f"art preflight is stale: {name}; render and review the changed frame again"
               for name, digest in current.items() if expected.get(name) != digest]
        # Approval carries the same digest map, so rewriting the manifest cannot
        # silently transfer an earlier review to a replacement PNG or chassis.
        if record.get("review", {}).get("inputs") != record["inputs"]:
            out.append("the visual review is not bound to these images and this chassis")
        out.extend(review_problems(record.get("review", {}), selected, record["inputs"], base.name))
        if record.get("version", 1) >= 2:
            out.extend(studio_problems(record, base))
            if not archived and json.loads((base / "art_plan.json").read_text()) != record.get("plan"):
                out.append("the art plan changed after the audition; rebuild and review the proof")
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", base.name) and base.name > STUDIO_SINCE:
            out.append("this run needs the studio audition with art_plan.json; rebuild the proof")
        return out
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        return [f"art preflight evidence is missing or unreadable: {e}"]


def bind_review(base: Path, record: dict, plan: dict, old: dict, critics: dict | None) -> None:
    """Carry every still-bound review, bind fresh critic hand-backs, and decide acceptance."""
    selected = record["selected"]
    old_frames = {f.get("slide"): f for f in old.get("review", {}).get("frames", [])}
    per_frame = {str(n): frame_inputs(record["inputs"], n, base) for n in selected}
    kept = [old_frames[n] for n in selected if n in old_frames
            and old_frames[n].get("inputs") == per_frame[str(n)]
            and old.get("plan") == plan]
    # THE BESPOKE ROUTE: a frame without a still-bound review takes its slide critic's
    # hand-back when that critic read this exact render (CRITIC_SINCE above).
    bound = {f["slide"]: f for f in kept}
    for n, role in zip(selected, ROLES):
        row = (critics or {}).get(n)
        if n in bound or row is None:
            continue
        digest = record["inputs"][f"render/slide-{n:02}.png"]
        frame = {"slide": n, "role": role, "source": CRITIC_SOURCE,
                 "critic": {k: v for k, v in row.items() if k != "render_sha256"},
                 "render_sha256": row.get("render_sha256"), "inputs": per_frame[str(n)]}
        if not critic_problems(frame, digest, base.name):
            bound[n] = frame
    frames = [bound[n] for n in selected if n in bound]
    record.update(version=2, plan=plan, frame_inputs=per_frame,
                  needs_review=[n for n in selected if n not in bound])
    record["review"] = {"decision": "revise", "inputs": record["inputs"], "frames": frames}
    # An art director's kept frame still needs its whole earlier review accepted; a critic
    # frame carries its own verdict and is re-checked by review_problems below.
    directors = [f for f in frames if f.get("source") != CRITIC_SOURCE]
    if (len(frames) == 3 and (not directors or old.get("review", {}).get("decision") == "accept")
            and not studio_problems(record, base)
            and not review_problems(record["review"] | {"decision": "accept"}, selected,
                                    record["inputs"], base.name)):
        record["review"]["decision"] = "accept"


def build(base: Path, middle: int | None, assets: Path, critics: dict | None = None) -> None:
    from PIL import Image, ImageDraw
    import panel_ready
    import value_register

    plan_path = base / "art_plan.json"
    plan = json.loads(plan_path.read_text()) if plan_path.exists() else None
    if plan is not None:
        if middle is not None and middle != plan.get("hardest_frame"):
            raise ValueError("--middle differs from art_plan.json's hardest_frame")
        middle = plan.get("hardest_frame")
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", base.name) and base.name > STUDIO_SINCE:
        raise ValueError("write art_plan.json and name the hardest frame before the audition")
    if critics and plan is None:
        raise ValueError("the bespoke route binds critics only to a run with art_plan.json")
    middle = 4 if middle is None else middle
    numbers = sorted(int(p.stem.split("-")[1]) for p in (base / "slides").glob("slide-*.html"))
    if not numbers or type(middle) is not int or not 1 < middle < numbers[-1]:
        raise ValueError("render frame 1, an evidence frame and the final frame first")
    selected = [1, middle, numbers[-1]]
    stale = panel_ready.check_renders_current(base, assets)
    if stale:
        raise ValueError(stale[0])
    report = json.loads((base / "render/render_report.json").read_text())
    qa, problems = panel_ready.load_machine_qa(base, report)
    if problems or qa.get("verdict") not in ("PASS", "WARN"):
        raise ValueError(problems[0] if problems else "the three-frame proof has not passed machine QA")
    rows = [value_register.frame_stats(base / "render" / f"slide-{n:02}.png") for n in selected]
    problems = value_register.judge(rows, True, base.name)
    if problems:
        raise ValueError(problems[0])
    # THE DETAIL FLOOR, READ BEFORE THE REVIEW (2026-10-30, queue detail-floor-fights-the-dark-
    # staged-world, three runs). Phase 12's layout_check holds every frame to it; read here, a
    # frame whose rect is mostly dark field is fixed before a review is bound to its pixels,
    # instead of rebinding the review after. Same floor, same message, never less.
    import layout_check
    problems = layout_check.frame_detail_problems(base, selected)
    if problems:
        raise ValueError(problems[0])
    # THE PLAN NAMES WHAT THE FRAME BUILDS, before a review is bound to it (weekly machine pass
    # 2026-11-27, queue dossier-drifts-from-the-render, nos. 87, 88, 89). A director who accepts a
    # frame its plan no longer describes is overruled by the next director who reads both.
    import plan_render_check
    sb = base / "storyboard.md"
    if sb.exists():
        problems = plan_render_check.model_drift_problems(
            sb.read_text(encoding="utf-8"), base / "slides", only=set(selected),
            assets=assets, date=base.name if re.fullmatch(r"\d{4}-\d{2}-\d{2}", base.name) else None)
        if problems:
            raise ValueError(problems[0])
    record = {"version": 1, "selected": selected, "inputs": inputs(base, selected, assets),
              "value_measurements": rows, "review": {"decision": "revise", "frames": []}}
    if plan is not None:
        old_path = base / "art_preflight.json"
        bind_review(base, record, plan, json.loads(old_path.read_text()) if old_path.exists() else {},
                    critics)
    (base / "art_preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    sheet = Image.new("RGB", (3 * 452, 590), "#0c1118")
    draw = ImageDraw.Draw(sheet)
    for i, (n, role) in enumerate(zip(selected, ROLES)):
        pic = Image.open(base / "render" / f"slide-{n:02}.png").convert("RGB")
        pic.thumbnail((432, 540))
        sheet.paste(pic, (i * 452 + 10, 10))
        draw.text((i * 452 + 10, 563), f"{n:02}  {role}", fill="#f5f2e9")
    sheet.save(base / "art_preflight.webp", quality=92)


def archive(base: Path, destination: Path, assets: Path) -> None:
    """Bind compressed delivery to reviewed PNGs without duplicating those PNGs."""
    from PIL import Image
    from ship_images import QUALITY_FLOOR_DB, psnr
    problems = check(base, assets)
    if problems:
        raise ValueError(problems[0])
    record = json.loads((base / "art_preflight.json").read_text())
    delivered, encodings = {}, []
    for n in record["selected"]:
        html = f"slides/slide-{n:02}.html"
        if sha(destination / html) != record["inputs"][html]:
            raise ValueError(f"the archived {html} differs from its accepted source")
        delivered[html] = record["inputs"][html]
        image = next((destination / f"slide-{n:02}.{ext}" for ext in ("webp", "png")
                      if (destination / f"slide-{n:02}.{ext}").exists()), None)
        if image is None:
            raise ValueError(f"the shipped image for frame {n} is absent")
        with Image.open(base / "render" / f"slide-{n:02}.png") as original, Image.open(image) as encoded:
            db = psnr(original, encoded)
        if db < QUALITY_FLOOR_DB:
            raise ValueError(f"{image.name} is below the shipping quality floor: {db:.2f} dB")
        delivered[image.name] = sha(image)
        encodings.append({"to": image.name, "to_sha256": delivered[image.name],
                          "from_sha256": record["inputs"][f"render/slide-{n:02}.png"],
                          "psnr_db": round(db, 3) if math.isfinite(db) else 999.0})
    record.update(shipped_inputs=delivered, encodings=encodings)
    (destination / "art_preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    problems = check(destination, assets, archived=True)
    if problems:
        raise ValueError(problems[0])


def self_test() -> int:
    from PIL import Image
    bad = 0
    def test(label, yes):
        nonlocal bad
        print(("ok   " if yes else "FAIL ") + label)
        bad += not yes
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        assets = base / "assets"
        (assets / "js/deck").mkdir(parents=True)
        (assets / "js/deck/test.js").write_text("one light")
        (base / "slides").mkdir()
        (base / "render").mkdir()
        selected = [1, 4, 9]
        for n in selected:
            (base / "slides" / f"slide-{n:02}.html").write_text(
                '<script src="@@ASSETS@@/js/deck/test.js"></script>')
            (base / "render" / f"slide-{n:02}.png").write_bytes(b"reviewed pixels")
        digest = inputs(base, selected, assets)
        review = {"decision": "accept", "inputs": digest, "frames": [
            {"slide": n, "role": role, "subject": "named subject", "visual_consequence": "a visible change",
             "weakness": "none observed", "repair": "none required"} for n, role in zip(selected, ROLES)]}
        record = {"selected": selected, "inputs": digest, "review": review}
        path = base / "art_preflight.json"
        def save(): path.write_text(json.dumps(record))
        save()
        test("a review of these three images is accepted", not check(base, assets))
        png = base / "render/slide-04.png"
        png.write_bytes(b"replacement pixels")
        test("a replacement evidence image invalidates approval", bool(check(base, assets)))
        record["inputs"] = inputs(base, selected, assets); save()
        test("rewriting the manifest does not transfer old approval", bool(check(base, assets)))
        png.write_bytes(b"reviewed pixels"); record["inputs"] = digest; save()
        (assets / "js/deck/test.js").write_text("a pale wash")
        test("a chassis edit invalidates the live preflight", bool(check(base, assets)))
        test("archived pixels do not depend on a future engine", not check(base, assets, archived=True))
        record["review"]["frames"] = record["review"]["frames"][:1]; save()
        test("a cover-only review cannot approve the evidence frame and close", bool(check(base, assets, True)))
        record["review"] = review
        record["inputs"] = {k:v for k,v in digest.items() if k != "render/slide-09.png"}
        record["review"]["inputs"] = record["inputs"]; save()
        test("even an approved manifest must contain all three images", bool(check(base, assets, True)))
        path.unlink()
        test("missing evidence fails closed", bool(check(base, assets)))
    with tempfile.TemporaryDirectory() as directory:
        base, delivered = Path(directory) / "live", Path(directory) / "shipped"
        (base / "slides").mkdir(parents=True); (base / "render").mkdir()
        (delivered / "slides").mkdir(parents=True)
        selected = [1, 4, 9]
        for n in selected:
            body = "<h1>A reviewed composition</h1>"
            (base / "slides" / f"slide-{n:02}.html").write_text(body)
            (delivered / "slides" / f"slide-{n:02}.html").write_text(body)
            pic = Image.new("RGB", (80, 100), (20 + n, 40, 60))
            pic.save(base / "render" / f"slide-{n:02}.png")
            pic.save(delivered / f"slide-{n:02}.webp", lossless=True)
        digest = inputs(base, selected, base / "assets")
        review = {"decision": "accept", "inputs": digest, "frames": [
            {"slide": n, "role": role, "subject": "a named subject", "visual_consequence": "a visible change",
             "weakness": "none observed", "repair": "none required"} for n, role in zip(selected, ROLES)]}
        (base / "art_preflight.json").write_text(json.dumps({"selected": selected, "inputs": digest, "review": review}))
        archive(base, delivered, base / "assets")
        test("compressed delivery preserves the review without archiving duplicate PNGs",
             not check(delivered, archived=True) and not (delivered / "render").exists())
        Image.new("RGB", (80, 100), "white").save(delivered / "slide-04.webp", lossless=True)
        test("a replaced delivered image fails the archive check", bool(check(delivered, archived=True)))
        try:
            archive(base, delivered, base / "assets")
            rejected = False
        except ValueError:
            rejected = True
        test("a different image cannot be exported as a faithful encode", rejected)
    # THE BESPOKE ROUTE (2026-11-18): the critics' hand-backs bind only the exact renders they
    # read, only at or above critic_ship with all six points, and only from the next run.
    bar = bespoke_config()["artists"]["critic_ship"]
    with tempfile.TemporaryDirectory() as directory:
        def bespoke_run(name):
            base = Path(directory) / name
            assets = base / "assets"
            (assets / "js/deck").mkdir(parents=True)
            (assets / "js/deck/test.js").write_text("spine")
            (base / "slides").mkdir()
            (base / "render").mkdir()
            for n in (1, 4, 9):
                (base / "slides" / f"slide-{n:02}.html").write_text(
                    f'<script src="@@ASSETS@@/js/deck/test.js"></script><h1>frame {n}</h1>')
                (base / "render" / f"slide-{n:02}.png").write_bytes(f"pixels {n}".encode())
            plan = {"hardest_frame": 4, "visual_argument": "a named argument",
                    "build_risk": "a named risk", "distinct_from_recent": "a named difference"}
            (base / "art_plan.json").write_text(json.dumps(plan))
            return base, assets, plan
        def handbacks(base, change=None):
            out = {}
            for n in (1, 4, 9):
                row = {"slide": n, "score": bar + 0.5, "points": {k: 8 for k in CRITIC_POINTS},
                       "fixes": [], "verdict": "ship",
                       "render_sha256": sha(base / "render" / f"slide-{n:02}.png")}
                row.update((change or {}).get(n, {}))
                out[n] = row
            return out
        def bind(base, assets, plan, critics, old=None):
            record = {"version": 1, "selected": [1, 4, 9], "inputs": inputs(base, [1, 4, 9], assets),
                      "review": {"decision": "revise", "frames": []}}
            bind_review(base, record, plan, old or {}, critics)
            (base / "art_preflight.json").write_text(json.dumps(record))
            return record
        base, assets, plan = bespoke_run("2026-11-19")
        rec = bind(base, assets, plan, handbacks(base))
        test("three shipped critic hand-backs on these renders accept the bespoke review",
             rec["review"]["decision"] == "accept" and not check(base, assets))
        accepted = rec
        (base / "render/slide-04.png").write_bytes(b"repaired pixels")
        test("a repaired render goes stale under the critic route", bool(check(base, assets)))
        read_before = {f["slide"]: f["render_sha256"] for f in accepted["review"]["frames"]}
        rec = bind(base, assets, plan, {n: dict(r, render_sha256=read_before[n])
                                        for n, r in handbacks(base).items()}, accepted)
        test("a critic who read the earlier render can't bind the repaired one",
             rec["review"]["decision"] == "revise" and rec["needs_review"] == [4])
        rec = bind(base, assets, plan, handbacks(base), accepted)
        test("a fresh critic on the repaired render rebinds it", rec["review"]["decision"] == "accept"
             and not check(base, assets))
        (base / "slides/slide-09.html").write_text(
            '<script src="@@ASSETS@@/js/deck/test.js"></script><h1>frame 9, source only</h1>')
        rec = bind(base, assets, plan, handbacks(base), rec)
        test("a source edit that leaves the render byte-identical keeps the critic's verdict",
             rec["review"]["decision"] == "accept" and not check(base, assets))
        for label, change in (("a rework verdict", {4: {"verdict": "rework"}}),
                              ("a ship verdict under critic_ship", {4: {"score": bar - 0.5}}),
                              ("a hand-back missing a point", {4: {"points": {k: 8 for k in CRITIC_POINTS[:-1]}}}),
                              ("a hand-back naming another slide", {4: {"slide": 5}})):
            rec = bind(base, assets, plan, handbacks(base, change))
            test(f"{label} does not bind the frame", rec["review"]["decision"] == "revise"
                 and 4 in rec["needs_review"])
        rec = bind(base, assets, plan, handbacks(base))
        rec["review"]["frames"][1]["critic"]["verdict"] = "rework"
        (base / "art_preflight.json").write_text(json.dumps(rec))
        test("a stored critic frame edited to rework fails the check", bool(check(base, assets)))
        rec["review"]["frames"][1]["critic"]["verdict"] = "ship"
        rec["review"]["frames"][1]["render_sha256"] = "0" * 64
        (base / "art_preflight.json").write_text(json.dumps(rec))
        test("a stored critic frame bound to another render fails the check", bool(check(base, assets)))
        director = {"slide": 1, "role": "cover", "subject": "s", "visual_consequence": "v",
                    "weakness": "w", "repair": "r", "encoding_reads": True,
                    "dominant_subject_finished": True, "feed_legible": True,
                    "inputs": frame_inputs(inputs(base, [1, 4, 9], assets), 1, base)}
        old = {"plan": plan, "review": {"decision": "revise", "frames": [director]}}
        rec = bind(base, assets, plan, {n: r for n, r in handbacks(base).items() if n != 1}, old)
        test("a director frame from a review left at revise does not ride in on the critics",
             rec["review"]["decision"] == "revise")
        closed, assets_c, plan_c = bespoke_run(CRITIC_SINCE)
        rec = bind(closed, assets_c, plan_c, handbacks(closed))
        test("a run dated on or before CRITIC_SINCE can't use the critic route",
             rec["review"]["decision"] == "revise" and rec["needs_review"] == [1, 4, 9])
        rec["review"] = accepted["review"] | {"inputs": rec["inputs"]}
        (closed / "art_preflight.json").write_text(json.dumps(rec))
        test("a critic-shaped review copied into a closed run fails the check", bool(check(closed, assets_c)))
    # WIRED, NOT DECORATIVE (2026-10-30): the audition's detail read exists only if build calls it
    # before writing the proof, and a refactor that drops the call would leave layout_check's own
    # self-test green. Read the source of build, not the docstring.
    import inspect
    src = inspect.getsource(build)
    at_call, at_write = src.find("layout_check.frame_detail_problems(base, selected)"), src.find("art_preflight.json\").write_text")
    test("build reads the detail floor on its three frames before it writes the proof", 0 < at_call < at_write)
    # Same shape for the plan's model names (weekly machine pass 2026-11-27): wired before the write.
    at_models = src.find("plan_render_check.model_drift_problems(")
    test("build refuses a frame whose dossier names a model it does not build, before it writes the proof",
         0 < at_models < at_write and "only=set(selected)" in src)
    return int(bool(bad))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date")
    parser.add_argument("--run", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--middle", type=int, help="legacy selection; new runs read art_plan.json")
    parser.add_argument("--critics", type=Path, help="with --write on a bespoke run: the slide critics' "
                        "hand-backs, each with the render_sha256 of the PNG it read")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    base = args.run or ROOT / "out" / str(args.date)
    if not args.run and not args.date:
        parser.error("give --date or --run")
    if args.archive:
        try:
            archive(base, args.archive, ROOT / "assets")
            print(f"Art review bound to the images delivered in {args.archive}")
            return 0
        except (OSError, ValueError, KeyError) as e:
            print(f"art preflight: {e}", file=sys.stderr)
            return 1
    if args.write:
        try:
            build(base, args.middle, ROOT / "assets",
                  load_critics(args.critics) if args.critics else None)
            print(f"Wrote {base / 'art_preflight.json'} and the three-frame proof. Review the images.")
            return 0
        except (OSError, ValueError, KeyError) as e:
            print(f"art preflight: {e}", file=sys.stderr)
            return 1
    problems = check(base, archived=bool(args.run))
    for problem in problems:
        print("FAIL " + problem)
    if not problems:
        print("art preflight: the accepted review matches all three frames")
    return int(bool(problems))


if __name__ == "__main__":
    sys.exit(main())
