#!/usr/bin/env python3
"""ship_images.py — make the shipped deck weigh what a phone can afford.

WHY THIS EXISTS

The render engine screenshots every slide at 2x into lossless PNG, which is exactly right for the
pixel critic loop and exactly wrong for everything after it. A critic needs every pixel the
browser drew. A reader on a phone off a county road needs the page to arrive.

In the sibling product those PNGs averaged about 4 MB each, nine per deck, and the public archive
served them straight from raw content hosting. That is roughly 34 MB per run committed to git
forever and a 40 MB page for whoever opens it. The archive was not a page, it was a download.

This converts the SHIPPED copies to WebP at full 2x resolution. The originals under `out/` are
untouched, because the review loop still needs them and they are scratch anyway.

**EVERY NUMBER THIS PRINTS IS MEASURED ON THE FILES IN FRONT OF IT.** No compression ratio is
quoted from a previous run and no quality claim is asserted. The law this project publishes is
that numerals are computed from data, and a script whose entire output is numerals is the last
place to make an exception. It measures the sizes it actually produced and computes PSNR against
the source, per slide, and prints what it found. If the encode is worse than expected on some
future deck, the output says so rather than repeating a number from a commit message.

THE SOCIAL SCRAPER EXCEPTION. LinkedIn, Slack and Facebook still treat WebP `og:image`
inconsistently, so slide 1 also ships as `og.jpg`, and every `og:image` and schema.org image
points at that and never at the WebP. This is not caution about an old browser. It is that the
unfurl is the first thing a reader sees and it is rendered by somebody else's code.

    ship_images.py --run 2026-08-12
    ship_images.py --all --force        # backfill; without --force it only reports
    ship_images.py --all --dry-run
    ship_images.py --self-test

Exit 0 on success, 1 if any run failed to convert, 2 if the tool could not run.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, features
except ImportError:                                                     # pragma: no cover
    print("ship_images: Pillow and numpy are required", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"

# 82 sits above the point where WebP's chroma handling starts showing on flat brand colour and a
# long way under where the file stops shrinking. It is a starting point, not a promise: the PSNR
# printed per slide is the actual measurement, and QUALITY_FLOOR_DB is what decides pass or fail.
QUALITY = 82

# THE LADDER, walked in order until a slide clears the quality floor. One fixed quality was the
# wrong instrument for a deck whose whole premise is that no two slides are drawn alike: flat
# fields encode beautifully at 82 and high frequency texture does not. Stops rather than a
# search because each step is a full encode of a 2160x2700 image, and four attempts on the two
# worst slides of a deck is cheap where a bisection is not.
QUALITY_LADDER = (82, 88, 92, 96)

# THE OG CARD WALKS A LADDER TOO, and until 2026-08-27 it did not.
#
# The ladder above exists because "one fixed quality was the wrong instrument for a deck whose
# whole premise is that no two slides are drawn alike". That reasoning was applied to the nine
# slides and NOT to the JPEG cut from slide 1, which kept a single `OG_QUALITY = 90` and was
# then measured against the same 40 dB floor. On 2026-08-27 slide 1 was a dark high bay with
# long smooth gradients, JPEG's worst case, and the card encoded at 38.2 dB. The gate refused it
# correctly and the run had nothing to turn: the only lever was a constant, and a constant is not
# an instrument.
#
# JPEG rather than WebP, so the ladder runs higher and further. The floor is the same 40 dB and
# is not moved, because moving a floor to pass an encode is the one repair this file must never
# make.
OG_QUALITY_LADDER = (90, 94, 96, 97)

# 40 dB is the conventional visually-lossless threshold for photographic content, and it is an
# EXTERNAL number rather than one measured from our own decks. That matters: a threshold derived
# from our own corpus is a ratchet, and a threshold derived from an encode we already accepted
# would pass anything we happened to ship first.
QUALITY_FLOOR_DB = 40.0


def psnr(a: Image.Image, b: Image.Image) -> float:
    """Peak signal to noise, in dB, computed from the two images actually on disk.

    Infinite when the encode is bit-identical, which lossy WebP never is, so a returned `inf` is a
    signal that something compared a file with itself rather than a suspiciously good encode.
    """
    x = np.asarray(a.convert("RGB"), dtype=np.float64)
    y = np.asarray(b.convert("RGB"), dtype=np.float64)
    if x.shape != y.shape:
        return float("nan")
    mse = float(np.mean((x - y) ** 2))
    if mse == 0:
        return float("inf")
    return 20.0 * math.log10(255.0) - 10.0 * math.log10(mse)


def convert_one(png: Path, dry: bool) -> dict:
    """Encode one slide and MEASURE the result. Returns what was measured, never what was hoped.

    QUALITY IS RAISED UNTIL THE SLIDE MEETS THE FLOOR, rather than one attempt at 82 and a
    complaint. The deck of 2026-08-16 is why. Its stipple paper register and its hachured soil
    section are high frequency texture, which is webp's worst case, and both encoded under the
    40 dB floor at quality 82: 39.0 and 40.0. The gate refused them correctly, they shipped with
    no webp beside their png, and the site published two broken images and dropped two more
    slides. One fixed quality for eight bespoke slides was the wrong instrument, because the
    whole point of this deck engine is that no two slides are drawn alike.

    The floor is never lowered to make a slide pass. The encoder is asked to work harder, and if
    it still cannot reach the floor the png is what ships, which is bigger and correct.
    """
    webp = png.with_suffix(".webp")
    src_bytes = png.stat().st_size
    if dry:
        return {"name": png.name, "src": src_bytes, "dst": None, "psnr": None, "wrote": False}

    with Image.open(png) as im:
        im.load()
        db, used = None, None
        for q in QUALITY_LADDER:
            im.save(webp, "WEBP", quality=q, method=6)
            with Image.open(webp) as out:
                out.load()
                db = psnr(im, out)
            used = q
            if db >= QUALITY_FLOOR_DB:
                break

    # Nothing on the ladder cleared the floor, so there is no honest webp for this slide. Remove
    # the one just written: leaving a visibly degraded file beside the png is how a later step
    # picks it up believing it passed.
    if db < QUALITY_FLOOR_DB:
        webp.unlink(missing_ok=True)
        return {"name": png.name, "src": src_bytes, "dst": None, "psnr": db, "wrote": False,
                "quality": used, "floor_missed": True}

    return {"name": png.name, "src": src_bytes, "dst": webp.stat().st_size, "psnr": db,
            "wrote": True, "path": webp, "quality": used}


def write_og(png: Path, dest: Path, dry: bool) -> dict | None:
    """Slide 1 as JPEG, for the unfurl. Rendered by somebody else's code, so it stays boring.

    Walks OG_QUALITY_LADDER until the encode clears QUALITY_FLOOR_DB, the same way a slide
    does. A dark frame with long smooth gradients is JPEG's worst case and one fixed quality
    cannot answer it.
    """
    if dry:
        return {"name": dest.name, "src": png.stat().st_size, "dst": None, "psnr": None,
                "wrote": False}
    with Image.open(png) as im:
        rgb = im.convert("RGB")
        db, used = 0.0, OG_QUALITY_LADDER[0]
        for q in OG_QUALITY_LADDER:
            rgb.save(dest, "JPEG", quality=q, optimize=True, progressive=True)
            with Image.open(dest) as out:
                out.load()
                db = psnr(rgb, out)
            used = q
            if db >= QUALITY_FLOOR_DB:
                break
    out = {"name": dest.name, "src": png.stat().st_size, "dst": dest.stat().st_size,
           "psnr": db, "wrote": True, "path": dest, "quality": used}
    if db < QUALITY_FLOOR_DB:
        out["floor_missed"] = True
    return out


def ship(run_dir: Path, dry: bool, keep_png: bool = False) -> tuple[list[dict], list[str]]:
    pngs = sorted(run_dir.rglob("slide-*.png"))
    if not pngs:
        return [], [f"{run_dir.name}: no slide PNGs found"]

    results, problems = [], []
    for png in pngs:
        try:
            results.append(convert_one(png, dry))
        except (OSError, ValueError) as exc:
            problems.append(f"{png.name}: {exc}")

    first = pngs[0]
    try:
        og = write_og(first, first.parent / "og.jpg", dry)
        if og:
            results.append(og)
    except (OSError, ValueError) as exc:
        problems.append(f"og.jpg: {exc}")

    # A SLIDE THAT COULD NOT MEET THE FLOOR IS NOT A PROBLEM, IT IS A PNG.
    #
    # This used to record it as a problem, which is what happened on 2026-08-16, and a problem
    # is what the run reported and then published around. The honest outcome is that the slide
    # ships in the format that is correct for it, so this reports the fact and keeps the png.
    # `load_runs` in site_build resolves webp then png per slide, so a mixed deck renders whole.
    for r in results:
        if r.get("floor_missed"):
            print(f"  {r['name']}: {r['psnr']:.1f} dB at quality {r['quality']}, under the "
                  f"{QUALITY_FLOOR_DB} dB floor even at the top of the ladder. Shipping the PNG, "
                  f"which is bigger and correct.")
        elif r["psnr"] is not None and not math.isnan(r["psnr"]) \
                and r["psnr"] < QUALITY_FLOOR_DB:
            problems.append(f"{r['name']}: {r['psnr']:.1f} dB is under the {QUALITY_FLOOR_DB} dB "
                            f"floor. The encode is visible, so do not ship it")

    # PER FILE, NOT ALL OR NOTHING. A png whose webp cleared the floor is redundant and goes. A
    # png that is the slide's only shipping format has to stay, and deleting it because some
    # OTHER slide was fine is how a deck loses an image entirely.
    if not dry and not keep_png and not problems:
        for png in pngs:
            if png.with_suffix(".webp").exists():
                png.unlink()
    return results, problems


def report(run_name: str, results: list[dict], dry: bool) -> None:
    wrote = [r for r in results if r["dst"] is not None]
    src = sum(r["src"] for r in results)
    dst = sum(r["dst"] for r in wrote) if wrote else 0
    verb = "would convert" if dry else "converted"
    print(f"\n{run_name}: {verb} {len(results)} image(s)")
    for r in results:
        if r["dst"] is None:
            print(f"  {r['name']:<20} {r['src']/1e6:6.2f} MB")
            continue
        db = "identical" if math.isinf(r["psnr"]) else f"{r['psnr']:.1f} dB"
        print(f"  {r['name']:<20} {r['src']/1e6:6.2f} MB -> {r['dst']/1e6:5.2f} MB   {db}")
    if wrote and dst:
        # Computed here, from these files, not carried forward from any previous run.
        print(f"  {'total':<20} {src/1e6:6.2f} MB -> {dst/1e6:5.2f} MB   {src/dst:.1f}x smaller")
        got = [r["psnr"] for r in wrote if not math.isinf(r["psnr"]) and not math.isnan(r["psnr"])]
        if got:
            print(f"  quality {min(got):.1f} to {max(got):.1f} dB measured, floor is "
                  f"{QUALITY_FLOOR_DB}")


def self_test() -> int:
    import tempfile
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    ok("this Pillow can write WebP at all", features.check("webp"))

    rng = np.random.default_rng(20260812)
    with tempfile.TemporaryDirectory() as td:
        run = Path(td) / "2026-08-12"
        run.mkdir(parents=True)

        # A slide-like image: large flat brand fields, hard type edges, one graded band. Random
        # noise would be the wrong fixture entirely, because noise is the one thing WebP cannot
        # compress and it would understate the saving by an order of magnitude.
        # Built in int16 and clipped back, NOT accumulated in uint8. The first version of this
        # fixture did `img += grain` on a uint8 array, so the top of the gradient wrapped 255 to
        # 4 and scattered black speckle across the brightest band in the frame. It then measured
        # 34 dB and 99x, and both numbers were about the wrapped fixture rather than the encoder.
        # A gate whose fixture is pathological measures its fixture.
        w, h = 1080, 1350
        img = np.zeros((h, w, 3), dtype=np.int16)
        img[:, :] = (20, 24, 48)                                    # the dusk ground
        img[120:360, 80:1000] = (228, 216, 195)                     # a caliche type block
        band = np.linspace(0, 255, h - 700, dtype=np.int16)[:, None]
        img[700:, :, 0] = band                                      # a graded ember band
        img[900:1000, 100:900] = (191, 10, 48)                      # the reserved red, flat
        img += rng.integers(0, 6, img.shape, dtype=np.int16)        # a little grain
        img = np.clip(img, 0, 255).astype(np.uint8)
        for i in (1, 2):
            Image.fromarray(img).save(run / f"slide-{i:02d}.png")

        before = sum(p.stat().st_size for p in run.glob("slide-*.png"))

        results, problems = ship(run, dry=True)
        ok("a dry run reports and writes nothing", not problems
           and not any(p.suffix == ".webp" for p in run.iterdir()), str(problems))
        ok("...and still counts every slide plus the unfurl", len(results) == 3, str(len(results)))

        results, problems = ship(run, dry=False, keep_png=True)
        ok("a real run converts without problems", problems == [], str(problems))
        ok("every slide got a webp", all((run / f"slide-{i:02d}.webp").exists() for i in (1, 2)))
        ok("slide 1 also got an og.jpg, because scrapers still mishandle webp",
           (run / "og.jpg").exists())

        # THE OG LADDER, and that it can still go red. Added 2026-08-27 with the ladder
        # itself, because a repair with no self-test is the repair that quietly stops
        # working. The first assertion proves the ladder CLIMBS, the second proves the
        # floor is still a floor and was not moved to pass an encode.
        og_row = next((r for r in results if r.get("name") == "og.jpg"), None)
        ok("the og card records the quality the ladder actually used",
           bool(og_row) and og_row.get("quality") in OG_QUALITY_LADDER,
           str(og_row))
        with Image.open(run / "slide-01.png") as base:
            probe = base.convert("RGB")
            worst = run / "og-probe.jpg"
            probe.save(worst, "JPEG", quality=1, optimize=True, progressive=True)
            with Image.open(worst) as bad:
                bad.load()
                ok("an encode the floor should refuse measures below it",
                   psnr(probe, bad) < QUALITY_FLOOR_DB)
            worst.unlink()

        after = sum(p.stat().st_size for p in run.glob("slide-*.webp"))
        ok(f"the deck got smaller ({before/1e6:.2f} MB to {after/1e6:.2f} MB, "
           f"{before/after:.1f}x)", after < before)

        got = [r["psnr"] for r in results if r["psnr"] is not None]
        ok(f"every encode measured above the {QUALITY_FLOOR_DB} dB floor "
           f"({min(got):.1f} dB worst)", all(g >= QUALITY_FLOOR_DB for g in got), str(got))

        # THE MEASUREMENT MUST BE ABLE TO FAIL, or printing it is decoration.
        crushed = run / "crushed.webp"
        with Image.open(run / "slide-01.png") as im:
            im.save(crushed, "WEBP", quality=1, method=0)
            with Image.open(crushed) as out:
                bad = psnr(im, out)
        ok(f"a deliberately crushed encode measures under the floor ({bad:.1f} dB)",
           bad < QUALITY_FLOOR_DB)

        # And that a bad encode is REFUSED rather than reported and shipped.
        floor_hits = [r for r in results if r["psnr"] is not None and r["psnr"] < QUALITY_FLOOR_DB]
        ok("nothing under the floor was allowed through this run", floor_hits == [])

        # PSNR sanity: identical images are infinite, different shapes are not a number.
        with Image.open(run / "slide-01.png") as a:
            ok("an identical pair measures infinite, which flags a self-comparison",
               math.isinf(psnr(a, a)))
            ok("a size mismatch is nan rather than a confident wrong number",
               math.isnan(psnr(a, a.resize((100, 100)))))

        # The PNGs go only when the WebP is there AND nothing failed.
        ok("the source PNGs survive with --keep", all((run / f"slide-{i:02d}.png").exists()
                                                      for i in (1, 2)))
        ship(run, dry=False)
        ok("...and are removed once every slide has a verified webp beside it",
           not any(run.glob("slide-*.png")))

        empty = Path(td) / "2026-08-13"
        empty.mkdir()
        _, problems = ship(empty, dry=True)
        ok("a run with no slides says so rather than reporting success", problems != [])

    if failures:
        print(f"\nship_images self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\nship_images self-test: all passed (quality {QUALITY}, floor {QUALITY_FLOOR_DB} dB, "
          f"every figure measured on the files themselves)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="one run date, e.g. 2026-08-12")
    ap.add_argument("--all", action="store_true", help="every run under runs/carousel/")
    ap.add_argument("--dry-run", action="store_true", help="report, change nothing")
    ap.add_argument("--force", action="store_true",
                    help="with --all, actually rewrite runs that have already shipped")
    ap.add_argument("--keep", action="store_true", help="keep the source PNGs")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    dry = a.dry_run
    if a.run:
        dirs = [RUNS / a.run]
    elif a.all:
        dirs = sorted(p for p in RUNS.glob("*") if p.is_dir()) if RUNS.exists() else []
        # `--all` reaches back across every run that has already shipped, and CLAUDE.md puts
        # overwriting shipped artifacts under runs/ on the short list of things that stop and ask.
        # A backfill is a real and occasionally necessary operation, so it is not forbidden, it is
        # made deliberate: without --force it reports what it would do and writes nothing.
        if not dry and not a.force:
            print("ship_images: --all rewrites artifacts in runs that have already shipped, "
                  "which is a deliberate act.\n  Showing what it would do. Add --force to "
                  "actually write.\n")
            dry = True
    else:
        print("ship_images: pass --run <date>, --all, or --self-test", file=sys.stderr)
        return 2
    if not dirs:
        print(f"ship_images: nothing to do under {RUNS}")
        return 0

    bad = 0
    for d in dirs:
        if not d.exists():
            print(f"ship_images: {d} does not exist", file=sys.stderr)
            bad += 1
            continue
        results, problems = ship(d, dry, keep_png=a.keep)
        report(d.name, results, dry)
        for p in problems:
            print(f"  PROBLEM: {p}", file=sys.stderr)
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"ship_images: broke: {exc}", file=sys.stderr)
        sys.exit(2)
