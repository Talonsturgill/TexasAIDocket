#!/usr/bin/env python3
"""print_ban.py — the print screen is DELETED, and this is what keeps it deleted.

THE OWNER, 2026-09-23, VERBATIM, and it is the whole reason this file exists:

    "delete that fallback bullshit look, make it impossible for me to have to tell u this again"

and the same day, on why:

    "a few days ago we made a bunch of updates to the automation so that it would stop just
    trying to use like that faded look with the stupid shapes because it looked bad. And so it
    would start actually creating like its own artwork for each run. But it's not doing that.
    It's reverted back to the same old bullshit artwork on these last runs."

WHAT THE LOOK WAS, MEASURED RATHER THAN GUESSED. `assets/js/txink.js` turned every frame into a
"print": the scene drawn in greys on an offscreen twin, then pushed through a halftone, line,
hatch or stipple screen onto a paper stock. Every surface became the same engraved texture, so a
steel enclosure, a pad of caliche and a sky all read as one faded etching. Loaded by frame:

    2026-09-14, -15, -16      9 of 9 frames printed
    2026-09-17, -18           0 of 9      the owner's fixes had landed
    2026-09-19, -20, -21, -23 9 of 9      REVERTED, every frame of every deck

and `txthree.js`, the GPU physically based bench that renders a solid with a real material, a
soft shadow and a specular, was loaded by ZERO frames in the history of this repository.

WHY IT KEPT COMING BACK, which is the part the September 20th fix missed. It was not drift. The
routine TOLD every run to print. `prompts/daily_routine.md` said every frame is "printed in paper
and ink rather than laid over a gradient" and pointed every director at
`examples/editorial-deck/`, a deck built on the print, as "what a 7 looks like". The treatment
director, the pixel critic and the flow critic each carried the same pointer. The September 20th
work added figure_bearing and depth_floor, both correct, and neither one asked whether a frame
was printed, so every run passed both new gates while doing exactly what the owner had rejected.
A fix that does not measure the defect does not hold, and that is now true in two places in this
repo's history.

THE REFERENCE THIS IS MEASURED AGAINST. The sister repository's own doctrine, THE RENDERED
LADDER: "hero slides should reach for the highest rung the story supports: GPU PBR, real
materials, soft shadow maps, IBL reflections, ACES. The default for object heroes." Its decks
render solid objects with material, light, cast shadow and contact, and carry one hero object
through all nine frames. There is no screen anywhere in them.

WHAT THIS CHECKS, three ways, because a ban that can be walked around is a suggestion.

  --assets    The print is gone from the bench. `assets/js/txink.js` does not exist and no file
              under `assets/js/` defines `TXINK` or a screen. Deleting a module is only a ban if
              nothing can quietly put it back.

  --run-dir   A run's slide sources and every chassis they load carry no print: no `txink.js`,
              no `TXINK`, no `.print(`, no screen mode. AND at least RENDERED_FLOOR frames render
              their subject through the GPU bench, which is the half that makes the old look
              impossible rather than merely unnamed. A deck that avoids the word "print" by
              drawing flat rectangles in 2D has not met the standard either.

              AND, from WORLD_SINCE, at least WORLD_FLOOR frames stand in a WORLD: they call
              `TXT.sky`, the dome, the light and the haze a render needs to be a place. A render
              in a void is the defect the print was deleted for, in a new material.

  --self-test Every way each check can fail, replayed.

THE WORLD, 2026-09-24. The owner, the next day: "the artwork hasnt hit the mark yet ever, and it
needs to be a SHOWSTOPPER every single slide should literally look world reknowned." Carousel
no. 32 was rendered, as ordered, and every frame was still a primitive in a near black void: the
bench gave a frame a flat background colour and a plane, and each chassis improvised its own sky.
`txthree.js` now carries the world (TXT.sky, TXT.ground surfaces, TXT.scatter, TXT.contact,
TXT.weather), measured on no. 32's own model in `examples/world-proof/`. The floor is five of
nine rather than nine, because an interior, a document on a desk or a hearing room is a real
frame with no sky in it, and a gate that forces a horizon into a courtroom makes worse art.

WHY NOT A PIXEL CHECK, stated so nobody spends an afternoon on it. Two render metrics were
calibrated on 2026-09-23 against today's printed deck, the owner's worked example and two decks
of the sister corpus. A high frequency residual flagged the owner's own example at 0.84, because
eighty crisp cubes have as many edges as a halftone. A spectral periodicity test scored one
printed deck at 0.00, because shipped WebP compression erases exactly the frequencies a screen
lives in. A flaky gate gets switched off, and this one must never be. The code is where the look
is chosen, so the code is where it is refused.

A SINCE-DATE, for the reason stated at RESERVE_SINCE in shipped_check: decks shipped on or
before PRINT_SINCE were drawn under a routine that ordered the print, and a gate does not judge
the work that produced it. They are still measured and printed.

EXIT CODES   0 clean    1 a check failed    2 the tool broke
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS = REPO_ROOT / "assets" / "js"
PRINT_SINCE = "2026-09-22"
RENDERED_FLOOR = 6
# THE WORLD. Decks on or before WORLD_SINCE were built before TXT.sky existed, so they are not
# judged on it. From the day after, five of nine frames stand in a world.
WORLD_SINCE = "2026-09-23"
# What txthree.js prints when a frame calls TXT.sky and its camera shows none of it. It must equal
# TXT.NO_SKY there, SKY_SHOWN must equal TXT.SKY_SHOWN, and the self-test reads the engine to hold
# them in step.
NO_SKY = "TXT: NO SKY IN FRAME"
# The line a renderer prints when its kept snapshot shows the sky after a preview that didn't.
SKY_SHOWN = "TXT: SKY IN FRAME"
SKY_MARK = re.compile(r"TXT: (NO SKY IN FRAME|SKY IN FRAME)(?: \[r(\d+)\])?")


def kept_no_sky(console_errors) -> bool:
    """True when the LAST sky line of any renderer on the page says it shows no sky.

    The engine names its renderer on every line, and a renderer's last snapshot is its verdict,
    the way this file's kept snapshot is the last on its context. A preview pointed at the ground
    and a kept frame that shows the sky print a no-sky line and then a line withdrawing it (Codex,
    PR 369). A line with no renderer named, as written before that, stands for renderer 0.
    """
    last = {}
    for e in console_errors or []:
        m = SKY_MARK.search(str(e))
        if m:
            last[m.group(2) or "0"] = m.group(1) == "NO SKY IN FRAME"
    return any(last.values())
WORLD_FLOOR = 5
DATED = re.compile(r"\d{4}-\d{2}-\d{2}$")
# THE WORLD IS THE ENGINE'S, NOT ANY METHOD CALLED sky (Codex on #353). No. 32's own chassis had
# `Y.sky(THREE, R)`, a dome of near black it painted itself, and a pattern that matched `.sky(` on
# any object would have counted that deck as standing in a world. So a frame is in a world when
# it calls `sky(` ON THE NAME IT BOUND TO txthree.js, found the way depth_floor finds its bench.
GPU_BIND = re.compile(r"(?:(?:var|let|const)\s+)?([A-Za-z_$][\w$]*)\s*=\s*\(\s*await\s+import\s*\("
                      r"[^)]*txthree\.js[^)]*\)\s*\)\s*\.init\s*\(")
GPU_STATIC = re.compile(r"import\s*\{\s*init(?:\s+as\s+([A-Za-z_$][\w$]*))?\s*\}\s*from\s*"
                        r"['\"][^'\"]*txthree\.js['\"]")

# What a print looks like in code. Scanned with comments stripped, because a chassis that
# explains why it no longer prints must be allowed to say the word.
PRINT_VOCAB = [
    (re.compile(r"txink\.js"), "loads txink.js, the deleted print screen"),
    (re.compile(r"\bTXINK\b"), "calls TXINK, the deleted print screen"),
    (re.compile(r"\.print\s*\(\s*c"), "pushes the frame through a print call"),
    (re.compile(r"\bscreen\s*:\s*\{[^}]*\bmode\s*:\s*['\"](?:halftone|line|hatch|stipple)"),
     "declares a print screen"),
    (re.compile(r"\bhalftone\b", re.I), "names a halftone"),
]
# What a rendered subject looks like in code: the GPU bench, loaded AND snapshotted, so a frame
# that imports it and draws nothing with it does not count.
RENDERED = (re.compile(r"txthree\.js"), re.compile(r"\.snapshot\s*\("))
CHASSIS_REF = re.compile(r"@@ASSETS@@/js/(deck/[A-Za-z0-9_.-]+\.js)")


def strip_comments(src: str) -> str:
    """HTML comments, JS block comments and JS line comments out, strings left alone.

    The line comment rule skips `://` so a URL inside a string is not cut in half.
    """
    src = re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    src = re.sub(r"(?<![:\\])//[^\n]*", " ", src)
    return src


def scan_source(name: str, src: str) -> list[str]:
    body = strip_comments(src)
    out = []
    for rx, why in PRINT_VOCAB:
        m = rx.search(body)
        if m:
            line = body.count("\n", 0, m.start()) + 1
            out.append(f"{name}:{line} {why}. The print screen is deleted on the owner's "
                       f"instruction of 2026-09-23 and a frame is RENDERED, never printed")
    return out


def is_rendered(src: str) -> bool:
    body = strip_comments(src)
    return all(rx.search(body) for rx in RENDERED)


def bench_names(body: str) -> set[str]:
    """Every name this frame bound to the txthree.js bench, in the dynamic or the static form."""
    names = {m.group(1) for m in GPU_BIND.finditer(body)}
    for m in GPU_STATIC.finditer(body):
        fn = m.group(1) or "init"
        names |= set(re.findall(r"(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*" + re.escape(fn)
                                + r"\s*\(", body))
    return names


def _placed(src: str, method: str) -> bool:
    """Rendered, and the bench's `method(` call precedes the kept snapshot ON THE SAME CONTEXT.

    The kept snapshot is the bench's last. Any `method(` call before it on the same render context
    counts, not only the first, so a frame that renders a preview context and then a final one,
    each with its own sky, is judged by the final one (Codex, #353).
    """
    if not is_rendered(src):
        return False
    body = strip_comments(src)
    names = bench_names(body)
    if not names:
        return False
    alt = "|".join(re.escape(n) for n in sorted(names))
    # THE BENCH'S OWN SNAPSHOT (Codex, #353). `helper.snapshot(R)` after the sky is not the render.
    shots = list(re.finditer(r"(?<![\w$.])(?:" + alt + r")\.snapshot\s*\(\s*([A-Za-z_$][\w$]*)?", body))
    if not shots or not shots[-1].group(1):
        return False
    kept = shots[-1]
    # THE SAME RENDER CONTEXT (Codex, #353). A call on one context and the kept snapshot of another
    # leaves the kept pixels in a void.
    for m in re.finditer(r"(?<![\w$.])(?:" + alt + r")\." + re.escape(method) + r"\s*\(\s*([A-Za-z_$][\w$]*)", body):
        if m.start() < kept.start() and m.group(1) == kept.group(1):
            return True
    return False


def in_world(src: str) -> bool:
    """Rendered AND standing in the engine's world: the bench's own sky, before the kept render."""
    return _placed(src, "sky")


def in_room(src: str) -> bool:
    """Rendered AND standing in a room the bench built: TXT.interior, before the kept render."""
    return _placed(src, "interior")


def check_assets(assets: Path = ASSETS) -> list[str]:
    out = []
    if (assets / "txink.js").exists():
        out.append(f"{assets / 'txink.js'} exists. It is the print screen, deleted on the owner's "
                   f"instruction of 2026-09-23. Delete it again and find what restored it")
    for f in sorted(assets.rglob("*.js")):
        if f.name in ("three.module.min.js", "d3.v7.min.js", "zdog.min.js",
                      "topojson-client.min.js"):
            continue
        # A PUBLISHED DECK'S CHASSIS IS HISTORY. `assets/js/deck/<date>-<name>.js` for a deck
        # shipped on or before PRINT_SINCE was written under a routine that ordered the print,
        # and its archived slides still load it. Rewriting it would be rewriting what was
        # published. It is refused here only if it DEFINES the screen, never for calling one
        # that no longer exists, which is now simply dead code in a file nothing re-renders.
        m = re.match(r"(\d{4}-\d{2}-\d{2})-", f.name)
        if f.parent.name == "deck" and m and m.group(1) <= PRINT_SINCE:
            continue
        body = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
        # DEFINING the screen, anywhere on the bench. A use is caught per run by check_run,
        # where the frame that makes it can be named.
        if re.search(r"(?:\b(?:global|window|globalThis|self)\.)?\bTXINK\s*=[^=]", body):
            out.append(f"{f.relative_to(assets.parent.parent)} defines TXINK, the deleted print "
                       f"screen")
        elif f.parent.name != "deck" and re.search(r"\bTXINK\s*\.", body):
            out.append(f"{f.relative_to(assets.parent.parent)} calls TXINK, the deleted print "
                       f"screen, from the shared bench")
    return out


def no_sky_frames(run_dir: Path) -> list[str]:
    """Frames whose render says the camera shows no sky, read off the run's render report.

    WHAT THE CAMERA SHOWS, NOT WHAT THE SOURCE CALLS (2026-09-26). No. 33's frame 4 called TXT.sky
    and looked straight down on a lawn. This gate counted the call and passed it, and a judge named
    the frame top-down in every one of the five rounds. TXT.snapshot now measures the horizon
    against the camera and says so on the console, render.py keeps console errors per frame, and
    this reads them, so the finding lands on the probe frame and not on a panel round.

    Measured through the engine on the shipped decks: no. 33's frame 4 and no. 34's frames 4 and 5
    fail, and no. 34's page on the cab seat passes. No. 33's frame 6 passes as shipped. It looked
    down through an orthographic camera for three rounds, in a source the run never committed, and
    then showed sky behind the type and failed for a horizon hidden behind the dek, which a count
    of sky in frame can't see.
    """
    frames, _ = read_sky_report(run_dir)
    return frames or []


def read_sky_report(run_dir: Path):
    """(frames, why): the frames whose kept snapshot shows no sky and "", or None and why the report
    can't be read, or None and "" when there is no report. A report that can't be read is not a
    clean report, and neither is a missing one where one should exist: both used to read as no
    finding at all (Codex, PR 369)."""
    import json
    for rel in ("render/render_report.json", "render_report.json"):
        rp = run_dir / rel
        if rp.is_file():
            try:
                rep = json.loads(rp.read_text(encoding="utf-8"))
                slides = rep.get("slides")
                if not isinstance(slides, list):
                    raise ValueError("no slides list")
            except (ValueError, AttributeError) as e:
                return None, f"{rel} can't be read ({e})"
            return [str(rec.get("file") or "?") for rec in slides
                    if isinstance(rec, dict) and kept_no_sky(rec.get("console_errors"))], ""
    return None, ""


def check_run(run_dir: Path, floor: int = RENDERED_FLOOR, chassis_root: Path = ASSETS,
              world_floor: int = WORLD_FLOOR) -> list[str]:
    slides_dir = run_dir / "slides"
    files = sorted(slides_dir.glob("slide-*.html"))
    if not files:
        return [f"{slides_dir} holds no slide-*.html, so there is nothing to check. A gate that "
                f"cannot find its subject does not report clean"]
    out, rendered, worlds, chassis, voids = [], 0, 0, set(), []
    for f in files:
        src = f.read_text(encoding="utf-8", errors="replace")
        out += scan_source(f.name, src)
        if is_rendered(src):
            rendered += 1
            if not (in_world(src) or in_room(src)):
                voids.append(f.name)
        if in_world(src):
            worlds += 1
        chassis.update(CHASSIS_REF.findall(strip_comments(src)))
    for rel in sorted(chassis):
        p = chassis_root / rel
        if p.exists():
            out += scan_source(rel, p.read_text(encoding="utf-8", errors="replace"))
    need = min(floor, len(files))
    if rendered < need:
        out.append(f"{rendered} of {len(files)} frames render their subject through the GPU bench "
                   f"(txthree.js, snapshotted), and the floor is {need}. A frame that avoids the "
                   f"print by drawing flat 2D shapes has not met the standard either: the owner "
                   f"asked for artwork each run actually creates, and the sister corpus renders "
                   f"solid objects with a material, a soft shadow and a contact")
    # History is not judged on a rule it predates: a dated run on or before WORLD_SINCE skips it.
    dated = DATED.match(run_dir.name)
    wneed = min(world_floor, len(files))
    if not (dated and run_dir.name <= WORLD_SINCE) and worlds < wneed:
        out.append(f"{worlds} of {len(files)} frames stand in a world (a rendered frame that calls "
                   f"TXT.sky), and the floor is {wneed}. A render in a flat background colour is an "
                   f"object in a void, the finding under thirty two decks. Five calls build the "
                   f"world: TXT.sky, TXT.deckRig, TXT.ground with a surface, TXT.contact, "
                   f"TXT.weather. See examples/world-proof/")
    # EVERY RENDERED FRAME STANDS SOMEWHERE (Codex, #353, and the owner's "every single slide").
    # Five of nine in the world, and the rest in a room the bench built, never in a flat colour:
    # a floor, a plane and a background colour are exactly the void no. 32 shipped.
    if not (dated and run_dir.name <= WORLD_SINCE) and voids:
        out.append(f"{', '.join(voids)} render{'s' if len(voids) == 1 else ''} a subject that stands in "
                   f"neither the world (TXT.sky) nor a room (TXT.interior), before the kept snapshot. "
                   f"An interior is a room built as geometry, never a flat background colour behind "
                   f"an object, which is the void every rendered frame of no. 32 shipped in")
    if not (dated and run_dir.name <= WORLD_SINCE) and worlds:
        frames, why = read_sky_report(run_dir)
        # A run directory is dated, and a dated run whose frames stand in the world has rendered them,
        # so a report that is missing there, or one that can't be read anywhere, is a check that did
        # not run. An undated directory is a fixture or a one-off --run-dir, and missing is allowed.
        if frames is None and (why or dated):
            why = why or "there is no render report (render/render_report.json or render_report.json)"
            out.append(f"the camera check did not run: {why}. TXT.snapshot measures whether each frame "
                       f"that calls TXT.sky shows any of it, and render.py keeps that in the report. "
                       f"Render the frames and run this again")
        for name in frames or []:
            out.append(f"{name} calls TXT.sky and its camera shows none of it, pitched below the horizon "
                       f"or looking straight down with nothing built overhead, so a reader sees objects in "
                       f"a void. Lift the camera until the horizon is in frame, or stand it inside something "
                       f"built (a room with TXT.interior, a cab, a canopy). No. 33's frame 4, a lawn seen "
                       f"straight down, was named top-down in all five panel rounds")
    return out


# ------------------------------------------------------------------------------------------ test

def self_test() -> int:
    fails = []

    def ok(label, cond, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + str(extra)[:200]}")
        if not cond:
            fails.append(label)

    rendered = ("<script type=\"module\">const T=await import('@@ASSETS@@/js/three.module.min.js');"
                "const X=(await import('@@ASSETS@@/js/txthree.js')).init(T);"
                "X.sky(R, X.worlds.goldenHour);const s=await X.snapshot(R);</script>")
    void = rendered.replace("X.sky(R, X.worlds.goldenHour);", "")
    printed = ("<script src=\"@@ASSETS@@/js/txink.js\"></script><script>"
               "M.print(cx, { screen: { mode: \"line\", cell: 6 } });</script>")

    ok("a rendered frame is clean", scan_source("s", rendered) == [], scan_source("s", rendered))
    ok("...and counts as rendered", is_rendered(rendered))
    ok("a printed frame is refused", len(scan_source("s", printed)) >= 2, scan_source("s", printed))
    ok("...and does not count as rendered", not is_rendered(printed))
    ok("TXINK alone is refused", scan_source("s", "<script>TXINK.print(cx,{})</script>") != [])
    ok("a halftone screen mode is refused",
       scan_source("s", "<script>go({ screen: { mode: 'halftone' } })</script>") != [])
    ok("a stipple screen mode is refused",
       scan_source("s", "<script>go({ screen: { cell: 7, mode: \"stipple\" } })</script>") != [])
    # A chassis that explains in a comment why it no longer prints must be allowed to say so,
    # or the explanation gets deleted to satisfy the gate and the next run loses the reason.
    ok("the word in a JS comment is allowed",
       scan_source("s", "<script>/* the TXINK print and its halftone are gone */ x()</script>") == [])
    ok("the word in an HTML comment is allowed",
       scan_source("s", "<!-- no txink.js, no halftone --><p>x</p>") == [])
    ok("a line comment is allowed",
       scan_source("s", "<script>// TXINK was here\nx()</script>") == [])
    ok("a URL in a string is not mistaken for a comment",
       is_rendered("<script>import('https://x/@@ASSETS@@/js/txthree.js'); a.snapshot(R)</script>"))
    ok("importing the bench without snapshotting it does not count",
       not is_rendered("<script>import('@@ASSETS@@/js/txthree.js')</script>"))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        a = root / "assets" / "js"
        (a / "deck").mkdir(parents=True)
        ok("clean assets pass", check_assets(a) == [], check_assets(a))
        (a / "txink.js").write_text("(function(g){ g.TXINK = {}; })(this)")
        got = check_assets(a)
        ok("the module coming back is CAUGHT", any("txink.js exists" in g for g in got), got)
        ok("...and so is TXINK being defined", any("defines TXINK" in g for g in got), got)
        (a / "txink.js").unlink()
        (a / "txother.js").write_text("window.TXINK = { print: function(){} };")
        ok("TXINK smuggled into another file is CAUGHT",
           any("defines TXINK" in g for g in check_assets(a)), check_assets(a))
        (a / "txother.js").unlink()
        (a / "deck" / "2026-09-20-old.js").write_text("TXINK.print(cx, {});")
        ok("a PUBLISHED deck's chassis calling the old print is history, not a failure",
           check_assets(a) == [], check_assets(a))
        (a / "deck" / "2099-01-01-new.js").write_text("global.TXINK = {};")
        ok("...but a NEW chassis defining it is CAUGHT",
           any("2099-01-01-new.js" in g for g in check_assets(a)), check_assets(a))
        (a / "deck" / "2099-01-01-new.js").unlink()
        (a / "deck" / "2026-09-20-old.js").unlink()

        run = root / "run"
        (run / "slides").mkdir(parents=True)
        for i in range(1, 10):
            (run / "slides" / f"slide-0{i}.html").write_text(rendered)
        ok("nine rendered frames pass", check_run(run, chassis_root=a) == [],
           check_run(run, chassis_root=a))
        for i in range(1, 5):
            (run / "slides" / f"slide-0{i}.html").write_text("<canvas></canvas><script>flat()</script>")
        got = check_run(run, chassis_root=a)
        ok("five rendered of nine is under the floor", any("5 of 9 frames" in g for g in got), got)
        (run / "slides" / "slide-01.html").write_text(rendered)
        ok("six rendered of nine meets it", check_run(run, chassis_root=a) == [],
           check_run(run, chassis_root=a))
        (run / "slides" / "slide-09.html").write_text(
            rendered + "<script src=\"@@ASSETS@@/js/deck/x-chassis.js\"></script>")
        (a / "deck" / "x-chassis.js").write_text("export const M = { print: (c, o) => TXINK.print(c, o) };")
        got = check_run(run, chassis_root=a)
        ok("a print hidden in the CHASSIS is caught",
           any("deck/x-chassis.js" in g for g in got), got)
        (a / "deck" / "x-chassis.js").write_text("/* no print here, on purpose */ export const M = {};")
        ok("a clean chassis passes", check_run(run, chassis_root=a) == [],
           check_run(run, chassis_root=a))
        three = root / "short"
        (three / "slides").mkdir(parents=True)
        for i in range(1, 4):
            (three / "slides" / f"slide-0{i}.html").write_text(rendered)
        ok("a three frame deck answers to three, never six", check_run(three, chassis_root=a) == [],
           check_run(three, chassis_root=a))
        empty = root / "empty"
        (empty / "slides").mkdir(parents=True)
        ok("a run with no slides is CAUGHT, never clean", check_run(empty, chassis_root=a) != [])

        # THE WORLD: rendered in a void is caught; a skyless interior or two is allowed.
        ok("a frame rendered in a void still counts as rendered", is_rendered(void))
        ok("...but does not stand in a world", not in_world(void))
        ok("the sky in a comment is not a sky",
           not in_world(void.replace("</script>", "/* X.sky(R, W) */</script>")))
        ok("a CHASSIS helper's sky is not the engine's world (no. 32's Y.sky)",
           not in_world(void.replace("</script>", "Y.sky(THREE, R);</script>")))
        ok("...nor is a sky on some other object with the bench's name as a suffix",
           not in_world(void.replace("</script>", "MAX.sky(R);</script>")))
        static = ("<script type=\"module\">import * as THREE from '@@ASSETS@@/js/three.module.min.js';"
                  "import { init } from '@@ASSETS@@/js/txthree.js';const TXT = init(THREE);"
                  "TXT.sky(R);const s = await TXT.snapshot(R);</script>")
        ok("the static import form, the one frames write, stands in a world", in_world(static), static)
        ok("...and an aliased init does too",
           in_world(static.replace("import { init }", "import { init as boot }").replace("= init(", "= boot(")))
        ok("a sky called AFTER the snapshot is not in the pixels that ship",
           not in_world(static.replace("TXT.sky(R);const s = await TXT.snapshot(R);",
                                       "const s = await TXT.snapshot(R);TXT.sky(R);")))
        ok("a sky on one render context and the kept snapshot of ANOTHER is not a world",
           not in_world(static.replace("TXT.sky(R);const s = await TXT.snapshot(R);",
                                       "TXT.sky(worldR);const s = await TXT.snapshot(keptR);")))
        ok("a later snapshot on some OTHER object is not the bench's render",
           not in_world(static.replace("const s = await TXT.snapshot(R);",
                                       "const s = await TXT.snapshot(R);helper.snapshot(R);")
                        .replace("TXT.sky(R);const s = await TXT.snapshot(R);",
                                 "const s = await TXT.snapshot(R);TXT.sky(R);helper.snapshot(R);")))
        ok("a preview context then a final one, each with its own sky, is judged by the FINAL one",
           in_world(static.replace("TXT.sky(R);const s = await TXT.snapshot(R);",
                                   "TXT.sky(pv);await TXT.snapshot(pv);TXT.sky(fin);const s = await TXT.snapshot(fin);")))
        ok("...but the same context under any name is",
           in_world(static.replace("TXT.sky(R);const s = await TXT.snapshot(R);",
                                   "TXT.sky(scene1);const s = await TXT.snapshot(scene1);")))
        ok("...but a sky before the LAST snapshot is, when a frame renders twice",
           in_world(static.replace("TXT.sky(R);const s = await TXT.snapshot(R);",
                                   "await TXT.snapshot(R);TXT.sky(R);const s = await TXT.snapshot(R);")))
        room = void.replace("const s=await X.snapshot(R);", "X.interior(R, {});const s=await X.snapshot(R);")
        ok("a room the bench built stands in a place", in_room(room) and not in_world(room), room)
        voids = root / "voids"
        (voids / "slides").mkdir(parents=True)
        for i in range(1, 10):
            (voids / "slides" / f"slide-0{i}.html").write_text(void)
        got = check_run(voids, chassis_root=a)
        ok("nine renders in a void are CAUGHT", any("0 of 9 frames stand in a world" in g for g in got), got)
        for i in range(1, 6):
            (voids / "slides" / f"slide-0{i}.html").write_text(rendered)
        for i in range(6, 10):
            (voids / "slides" / f"slide-0{i}.html").write_text(room)
        ok("five worlds and four ROOMS meet the floor", check_run(voids, chassis_root=a) == [],
           check_run(voids, chassis_root=a))
        (voids / "slides" / "slide-09.html").write_text(void)
        got = check_run(voids, chassis_root=a)
        ok("five worlds, three rooms and one render in a VOID is CAUGHT, and named",
           any("slide-09.html" in g and "neither the world" in g for g in got), got)
        (voids / "slides" / "slide-09.html").write_text("<canvas></canvas><script>drawTheMap()</script>")
        ok("...while a frame that is not rendered at all is print_ban's other rule, not this one",
           not any("neither the world" in g for g in check_run(voids, chassis_root=a)))
        (voids / "slides" / "slide-09.html").write_text(room)
        (voids / "slides" / "slide-05.html").write_text(room)
        got = check_run(voids, chassis_root=a)
        ok("four worlds of nine is under it", any("4 of 9 frames stand in a world" in g for g in got), got)
        hist = root / "2026-09-23"
        (hist / "slides").mkdir(parents=True)
        for i in range(1, 10):
            (hist / "slides" / f"slide-0{i}.html").write_text(void)
        ok("a deck on or before WORLD_SINCE is not judged on the world", check_run(hist, chassis_root=a) == [],
           check_run(hist, chassis_root=a))
        new = root / "2026-09-24"
        (new / "slides").mkdir(parents=True)
        for i in range(1, 10):
            (new / "slides" / f"slide-0{i}.html").write_text(void)
        ok("...and the day after, it is", any("stand in a world" in g for g in check_run(new, chassis_root=a)))
        probe = root / "probe"
        (probe / "slides").mkdir(parents=True)
        (probe / "slides" / "slide-01.html").write_text(void)
        ok("the PROBE frame answers to the world too, one of one",
           any("0 of 1 frames stand in a world" in g for g in check_run(probe, chassis_root=a)))

        # WHAT THE CAMERA SHOWS (2026-09-26): a frame that calls TXT.sky and looks straight down.
        import json as _json
        seen = root / "2026-09-27"
        (seen / "slides").mkdir(parents=True)
        (seen / "render").mkdir(parents=True)
        for i in range(1, 10):
            (seen / "slides" / f"slide-0{i}.html").write_text(rendered)

        def report(errors_on_6):
            (seen / "render" / "render_report.json").write_text(_json.dumps({"slides": [
                {"file": f"slide-0{i}.html", "console_errors": (errors_on_6 if i == 6 else [])}
                for i in range(1, 10)]}))
        report([])
        ok("nine frames whose cameras show their sky pass", check_run(seen, chassis_root=a) == [],
           check_run(seen, chassis_root=a))
        report([NO_SKY + ". This frame calls TXT.sky and its camera shows none of it"])
        got = check_run(seen, chassis_root=a)
        ok("a frame that CALLS TXT.sky and shows none of it is CAUGHT off the render, and named",
           any("slide-06.html" in g and "shows none of it" in g for g in got), got)
        ok("...and a report at the run root, where a shipped deck keeps it, is read too",
           (lambda: ((seen / "render_report.json").write_text(
               (seen / "render" / "render_report.json").read_text()),
               (seen / "render" / "render_report.json").unlink(),
               no_sky_frames(seen))[2])() == ["slide-06.html"])
        root_report = seen / "render_report.json"

        def at_root(errors_on_6):
            root_report.write_text(_json.dumps({"slides": [
                {"file": f"slide-0{i}.html", "console_errors": (errors_on_6 if i == 6 else [])}
                for i in range(1, 10)]}))
        # THE KEPT SNAPSHOT DECIDES, per renderer (Codex, PR 369): a preview pointed at the ground,
        # then a kept frame that shows the sky, withdraws the preview's line.
        at_root([NO_SKY + " [r1]. a preview", SKY_SHOWN + " [r1]. the kept snapshot"])
        ok("a preview's no-sky line, withdrawn by the same renderer's kept snapshot, is clean",
           check_run(seen, chassis_root=a) == [], check_run(seen, chassis_root=a))
        at_root([NO_SKY + " [r1]. one renderer", SKY_SHOWN + " [r2]. another renderer"])
        ok("...and another renderer's line withdraws nothing",
           no_sky_frames(seen) == ["slide-06.html"], no_sky_frames(seen))
        at_root([SKY_SHOWN + " [r1]. first", NO_SKY + " [r1]. a later snapshot at the ground"])
        ok("...and a later snapshot at the ground stands", no_sky_frames(seen) == ["slide-06.html"],
           no_sky_frames(seen))
        # A REPORT THAT CAN'T BE READ, OR ISN'T THERE, IS A CHECK THAT DID NOT RUN (Codex, PR 369).
        root_report.write_text('{"slides": [')
        ok("a report that can't be read is CAUGHT, never read as clean",
           any("did not run" in g for g in check_run(seen, chassis_root=a)), check_run(seen, chassis_root=a))
        root_report.unlink()
        ok("...and so is a dated run whose world frames have no report at all",
           any("did not run" in g for g in check_run(seen, chassis_root=a)), check_run(seen, chassis_root=a))
        ok("...while an undated fixture without one is not judged on it",
           not any("did not run" in g for g in check_run(three, chassis_root=a)), check_run(three, chassis_root=a))
        engine = (ASSETS / "txthree.js").read_text(encoding="utf-8")
        ok("the engine prints the exact words this gate reads, the withdrawal included",
           f"TXT.NO_SKY = '{NO_SKY}'" in engine and "console.error(TXT.NO_SKY" in engine
           and f"TXT.SKY_SHOWN = '{SKY_SHOWN}'" in engine and "console.error(TXT.SKY_SHOWN" in engine)

    # The real repository, which is the case that matters.
    ok("THIS repository's assets carry no print", check_assets() == [], check_assets())

    if fails:
        print(f"\nprint_ban self-test: {len(fails)} FAILED", file=sys.stderr)
        return 1
    print("\nprint_ban self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--assets", action="store_true", help="the bench carries no print screen")
    ap.add_argument("--run-dir", help="a run directory holding slides/")
    ap.add_argument("--date", help="shorthand for --run-dir out/<date>")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.assets or a.run_dir or a.date):
        print("print_ban: pass --assets, --run-dir, --date or --self-test", file=sys.stderr)
        return 2
    problems = []
    if a.assets:
        problems += check_assets()
    run = Path(a.run_dir) if a.run_dir else (REPO_ROOT / "out" / a.date if a.date else None)
    if run is not None:
        if not run.exists():
            print(f"print_ban: no such run directory {run}", file=sys.stderr)
            return 2
        problems += check_run(run)
    if problems:
        print(f"print_ban: FAIL, {len(problems)} problem(s)\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    what = " and ".join(x for x in ("assets" if a.assets else "", str(run) if run else "") if x)
    print(f"print_ban: clean ({what}). No print screen, and the frames are rendered")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"print_ban: the tool broke: {exc}", file=sys.stderr)
        sys.exit(2)
