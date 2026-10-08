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


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(base: Path, selected: list[int], assets: Path) -> dict:
    files = {}
    for n in selected:
        html = base / "slides" / f"slide-{n:02}.html"
        png = base / "render" / f"slide-{n:02}.png"
        for path in (html, png):
            files[str(path.relative_to(base))] = sha(path)
        # The shared chassis can restyle all three without changing their HTML.
        for rel in re.findall(r"@@ASSETS@@/(js/deck/[A-Za-z0-9_.-]+\.js)", html.read_text()):
            files["assets/" + rel] = sha(assets / rel)
    return files


def review_problems(review: dict, selected: list[int]) -> list[str]:
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
        for field in ("subject", "visual_consequence", "weakness", "repair"):
            if not isinstance(f.get(field), str) or not f[field].strip():
                out.append(f"frame {f.get('slide')}: reviewer must record {field}")
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
        if any(name not in required and not re.fullmatch(r"assets/js/deck/[A-Za-z0-9_.-]+\.js", name)
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
        out.extend(review_problems(record.get("review", {}), selected))
        return out
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        return [f"art preflight evidence is missing or unreadable: {e}"]


def build(base: Path, middle: int, assets: Path) -> None:
    from PIL import Image, ImageDraw
    import panel_ready
    import value_register

    numbers = sorted(int(p.stem.split("-")[1]) for p in (base / "slides").glob("slide-*.html"))
    if not numbers or not 1 < middle < numbers[-1]:
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
    record = {"version": 1, "selected": selected, "inputs": inputs(base, selected, assets),
              "value_measurements": rows, "review": {"decision": "revise", "frames": []}}
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
    return int(bool(bad))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date")
    parser.add_argument("--run", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--middle", type=int, default=4)
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
            build(base, args.middle, ROOT / "assets")
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
