#!/usr/bin/env python3
"""depth_floor.py — THE FRAME STANDS IN A PLACE.

WHY THIS EXISTS. 2026-09-20, the owner:

    "everything is very flat and 2d, we need to teach the automation and agents through
     research how to do more 2.5d and expand its artwork capabilities beyond this flat look"

WHAT WAS MEASURED, and it is not a missing capability.

`txscene.js` is a 2.5D scene bench: a ground plane, a horizon, a level pinhole camera, objects
placed at TRUE SCALE IN METRES, and one declared light casting every shadow onto the plane. It
was written on 2026-09-11 for this exact complaint, and its own docstring says so:

    "Twenty one decks shipped and the judges' craft finding was the same one every time, in
     different words: a small primitive floating in a gradient ... Every frame was drawn in
     screen pixels with no camera, so nothing had a size, nothing stood on anything, nothing
     cast a shadow onto anything."

Across 27 shipped decks, 241 frames:

    staged frames per deck      median 0, best ever 5
    distinct depth cues         median 0, best ever 5
    2026-09-18, -19, -20        ZERO depth cues, all three decks
    S.fade   (aerial perspective)   never used, 0 of 27 decks
    S.box / S.slab (form shading)   never used, 0 of 27 decks

`tx3d.js`, a full software 3D renderer with perspective, painter's z-sort, Lambert shading and
depth fog, is loaded by ONE frame of 241. `three.module.min.js` by none.

So the kit is complete and the frames do not reach for it. The camera is OPTIONAL, and a cue
nobody is asked for is a cue that does not appear. This is the third defect of that exact shape
found in one day, after THE ARTWORK CARRIES THE DATA and the round cap's missing floor.

WHAT DEPTH IS MADE OF, from the perception literature rather than from taste. The pictorial
depth cues are occlusion, relative size, height in the visual field, linear perspective, texture
gradient, aerial perspective, shading, and cast shadow. Occlusion is the most reliable and gives
only ordinal depth; relative size and texture gradient give metric depth; aerial perspective is
measurably more powerful than its reputation. Every one of them already has a call on the bench:

    relative size        S.ppm(Z)          px per metre at depth Z
    height in field      S.groundY(Z)      where the ground sits at depth Z
    linear perspective   S.project(X,Y,Z)  world metres to screen
    texture gradient     S.gridZ / gridX / strip
    aerial perspective   S.fade(hex, Z)    a hue toward sky with distance
    cast shadow          S.shadow(sprite)  from the deck's ONE declared light
    form shading         S.box / S.slab    a lit face and a shadow face on one solid
    occlusion            draw far first    the bench does not sort, the drawer decides

WHAT THIS GATE ASKS. A frame is STAGED when it builds the bench, places something THROUGH the
camera, and casts a shadow from the declared light. Enough frames staged, enough distinct cues
across the deck, and the scene's light agreeing with the chassis's.

THE LIGHT AGREEMENT IS THE HALF THAT IS EASIEST TO MISS. `TXDECK.declare` names one light for
the deck and `TXSCENE.create` takes its own `light:{az,el}`. Two surfaces holding their own copy
of one rule, with nothing in between checking they agree, is this repo's oldest defect: it has
shipped the wrong site URL on three decks, a missing hashtag block and a missing progress
counter the same way. Here it would put the scene's shadows running one way and the chassis's
running another, in one frame, under one sun.

WHY IT IS MEASURED IN THE CODE AND NOT IN THE PIXELS. Four pixel statistics were tried against
59 decks of the reference corpus first: modelling inside lit forms, count of value shelves,
aerial contrast ratio, mass under blur. NONE of them separated the two corpora. Depth here is a
property of how the frame was CONSTRUCTED, and the construction is in the source.

    depth_floor.py --date 2026-09-20
    depth_floor.py --slides-dir out/<date>/slides
    depth_floor.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "config" / "carousel" / "depth_floor.json"

# Each cue is a CALL a frame makes, so a claim about depth is a thing the renderer did rather
# than a sentence in a dossier. `S` is the conventional local alias and matching only `TXSCENE.`
# would miss every frame that actually projects, because all of them alias it first.
#
# CUES ARE BOUND TO THE BENCH INSTANCE, and the first cut of this file was not (2026-09-20,
# review). It matched any identifier before the dot, so `TXOBJ.sprite('school_bus')`, which
# BUILDS a sprite and places nothing, counted as placement, and any helper with a method called
# `project` or `box` counted as a depth cue. Measured on the corpus this was not hypothetical:
# 62 `J.sprite(` and 6 `E.sprite(` calls belong to things that are not the bench at all, against
# 29 frames that actually bind `S = TXSCENE.create`. A gate matching on a method name measures
# the vocabulary a frame happens to use.
BIND = re.compile(r"(?:(?:var|let|const)\s+)?([A-Za-z_$][\w$]*)\s*=\s*TXSCENE\.create\s*\(")

CUE_METHODS = {
    "LINEAR_PERSPECTIVE": ("project",),
    "RELATIVE_SIZE":      ("ppm",),
    "HEIGHT_IN_FIELD":    ("groundY", "depthAt"),
    "AERIAL":             ("fade",),
    # `shadowVec` RETURNS A VECTOR AND PAINTS NOTHING. Counting it here let a frame satisfy the
    # cast shadow requirement by asking which way the light falls and then not drawing it.
    "CAST_SHADOW":        ("shadow",),
    "TEXTURE_GRADIENT":   ("gridZ", "gridX", "strip"),
    "FORM_SHADING":       ("box", "slab"),
    "OCCLUSION":          ("row",),
    "PLACED_SPRITE":      ("sprite",),
}
# Placing something THROUGH the camera. A frame that builds the bench and then draws in screen
# pixels has a camera it did not use, which is 54 frames of this corpus.
PLACED = ("LINEAR_PERSPECTIVE", "RELATIVE_SIZE", "HEIGHT_IN_FIELD",
          "FORM_SHADING", "PLACED_SPRITE", "OCCLUSION")
# `PLACED_SPRITE` is a placement and NOT a depth cue on its own, so it does not count toward the
# deck's distinct cue total. A sprite pasted at a depth with nothing else is the old flat frame
# with a coordinate.
NOT_A_CUE = ("PLACED_SPRITE",)
# The plane the subject stands on. Without one the solids and their shadows float over the old
# empty background, which is the defect the bench exists for.
GROUND_METHODS = ("ground", "gridZ", "gridX", "strip")
CREATE = re.compile(r"TXSCENE\.create\s*\(")
# The cues a deck's distinct total is counted against.
CUE_NAMES = frozenset(CUE_METHODS) - frozenset(NOT_A_CUE)


def bench_aliases(src: str) -> set[str]:
    """Every name in this frame that holds a bench instance."""
    return {m.group(1) for m in BIND.finditer(src)} | {"TXSCENE"}


def calls(src: str, aliases: set[str], methods) -> list[str]:
    """The full argument text of each `<bench>.<method>( ... )` call, parens balanced."""
    if not aliases:
        return []
    pat = re.compile(r"\b(?:" + "|".join(re.escape(a) for a in sorted(aliases)) + r")\.(?:"
                     + "|".join(methods) + r")\s*\(")
    out = []
    for m in pat.finditer(src):
        i, depth, j = m.end() - 1, 0, m.end() - 1
        while j < len(src):
            if src[j] == "(":
                depth += 1
            elif src[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(src[i:j + 1])
    return out


def cues_in(src: str, aliases: set[str] | None = None) -> set[str]:
    a = aliases if aliases is not None else bench_aliases(src)
    return {k for k, ms in CUE_METHODS.items() if calls(src, a, ms)}


SHADOW_OFF = re.compile(r"shadow\s*:\s*false")


def paints_a_shadow(src: str, aliases: set[str]) -> bool:
    """A painted cast shadow: an explicit `shadow()`, or a solid that did not opt out.

    PER CALL, and the first cut searched the whole frame (2026-09-20, review). One decorative
    box carrying `shadow: false` suppressed implicit shadow recognition for every other solid in
    that frame, so five otherwise staged frames could fail the daily gate on one opt-out.
    """
    if calls(src, aliases, CUE_METHODS["CAST_SHADOW"]):
        return True
    return any(not SHADOW_OFF.search(c) for c in calls(src, aliases, ("box", "slab")))


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def scene_light(src: str) -> tuple[float, float] | None:
    """The az and el the frame hands the bench."""
    m = re.search(r"TXSCENE\.create\s*\(.*?light\s*:\s*\{([^}]*)\}", src, re.S)
    if not m:
        return None
    az = re.search(r"az\s*:\s*(-?[\d.]+)", m.group(1))
    el = re.search(r"el\s*:\s*(-?[\d.]+)", m.group(1))
    if not (az and el):
        return None
    return float(az.group(1)), float(el.group(1))


def chassis_light(chassis_src: str) -> tuple[float, float] | None:
    """The az and el the chassis declared for the whole deck."""
    m = re.search(r"TXDECK\.declare\s*\(.*?light\s*:\s*\{([^}]*)\}", chassis_src, re.S)
    if not m:
        return None
    az = re.search(r"az\s*:\s*(-?[\d.]+)", m.group(1))
    el = re.search(r"el\s*:\s*(-?[\d.]+)", m.group(1))
    if not (az and el):
        return None
    return float(az.group(1)), float(el.group(1))


# THE GPU BENCH STAGES A FRAME TOO, and until 2026-09-23 this file could not see it.
#
# Every cue above is a TXSCENE call, so a frame rendered through `assets/js/txthree.js`, which
# places a physically based object through a perspective camera onto a ground plane under a
# shadow mapped key light with fog, scored as unstaged with zero cues. The gate was measuring the
# TOOL rather than the depth. That mattered the day the print screen was deleted and the routine
# made the GPU bench the default, because the old answer would have been to keep drawing in 2D to
# satisfy a gate, which is how the flat look survives.
#
# The same discipline as the canvas bench: cues are calls on the BOUND instance, so a frame that
# imports the bench and draws nothing with it earns nothing.
GPU_BIND = re.compile(r"(?:(?:var|let|const)\s+)?([A-Za-z_$][\w$]*)\s*=\s*\(\s*await\s+import\s*\("
                      r"[^)]*txthree\.js[^)]*\)\s*\)\s*\.init\s*\(")
GPU_CUES = {
    "LINEAR_PERSPECTIVE": ("frame",),        # a perspective camera placed in the world
    "HEIGHT_IN_FIELD":    ("ground",),       # the plane everything stands on
    "FORM_SHADING":       ("mat.",),         # a physically based material under a key light
}


# THE STATIC FORM, which is what a frame writes once craft_floor refuses a dynamic import():
#     import { init } from '@@ASSETS@@/js/txthree.js';   const TXT = init(THREE);
GPU_STATIC = re.compile(r"import\s*\{\s*init(?:\s+as\s+([A-Za-z_$][\w$]*))?\s*\}\s*from\s*"
                        r"['\"][^'\"]*txthree\.js['\"]")


def _static_bench_names(src: str) -> set[str]:
    out = set()
    for m in GPU_STATIC.finditer(src):
        fn = m.group(1) or "init"
        out |= set(re.findall(r"(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*" + re.escape(fn)
                              + r"\s*\(", src))
    return out


def gpu_report(src: str) -> dict | None:
    """Staging for a frame rendered through txthree.js, or None if it does not use it."""
    names = {m.group(1) for m in GPU_BIND.finditer(src)} | _static_bench_names(src)
    if not names:
        return None
    alt = "|".join(re.escape(n) for n in sorted(names))
    def has(method: str) -> bool:
        return re.search(r"\b(?:" + alt + r")\." + re.escape(method).replace("\\.", "\\.")
                         + (r"" if method.endswith(".") else r"\s*\("), src) is not None
    cues = {k for k, ms in GPU_CUES.items() if any(has(m) for m in ms)}
    adds = len(re.findall(r"\b(?:" + alt + r")\.add\s*\(", src))
    looped = re.search(r"for\s*\([^)]*\)\s*\{[^}]*\b(?:" + alt + r")\.add\s*\(", src, re.S)
    if adds >= 2 or looped or ".clone(" in src:
        cues |= {"OCCLUSION", "RELATIVE_SIZE"}
    setup = re.search(r"\b(?:" + alt + r")\.setup\s*\((.*?)\)\s*;", src, re.S)
    if setup and re.search(r"\bfog\s*:", setup.group(1)):
        cues.add("AERIAL")
    deck_lit = has("deckRig")
    rigged = deck_lit or has("rig")
    added = adds >= 1
    shot = re.search(r"\.snapshot\s*\(", src) is not None
    if rigged and added:
        cues.add("CAST_SHADOW")
    placed = has("frame") and added
    grounded = has("ground")
    return {
        "cues": cues,
        "bench": True,
        "placed": placed,
        "shadow": rigged and added,
        "ground": grounded,
        "staged": placed and grounded and rigged and added and shot,
        # A frame lit by deckRig agrees with its chassis BY CONSTRUCTION, because the key's
        # direction is read from TXDECK.declare. A frame lit by TXT.rig alone carries its own key
        # position, which is a second copy of the light, and reads as unreadable, fail closed.
        "light": "deck" if deck_lit else None,
    }


def frame_report(name: str, src: str) -> dict:
    g = gpu_report(src)
    if g is not None:
        g["name"] = name
        return g
    al = bench_aliases(src)
    bench = bool(CREATE.search(src))
    hit = cues_in(src, al)
    casts = paints_a_shadow(src, al)
    grounded = bool(calls(src, al, GROUND_METHODS))
    placed = bool(hit & set(PLACED))
    return {
        "name": name,
        "cues": (hit | ({"CAST_SHADOW"} if casts else set())) - set(NOT_A_CUE),
        "bench": bench,
        "placed": placed,
        "shadow": casts,
        "ground": grounded,
        "staged": bench and placed and casts and grounded,
        "light": scene_light(src),
    }


def check(frames: list[dict], cfg: dict, deck_light=None) -> list[str]:
    probs: list[str] = []
    n = len(frames)
    floor = min(int(cfg["min_staged_frames"]), n)
    want_cues = min(int(cfg["min_distinct_cues"]), n)

    staged = [f for f in frames if f["staged"]]
    if len(staged) < floor:
        near = [f for f in frames if f["bench"] and not f["staged"]]
        extra = ""
        if near:
            def why(f):
                if not f["placed"]:
                    return "never places through the camera"
                if not f["ground"]:
                    return "draws no ground plane, so its solids float"
                return "casts no shadow"
            miss = ", ".join(f"{f['name']} ({why(f)})" for f in near[:3])
            extra = (f" {len(near)} frame(s) build the bench and stop short: {miss}. A camera a "
                     f"frame does not place through is a camera it did not use")
        probs.append(
            f"THE DECK DOES NOT STAND IN A PLACE. {len(staged)} of {n} frames are staged and "
            f"this deck needs {floor}. A staged frame builds the bench, places something through "
            f"the camera at true scale, and casts a shadow from the deck's one light.{extra}")

    got = set().union(*[f["cues"] for f in frames]) if frames else set()
    if len(got) < want_cues:
        unused = sorted(CUE_NAMES - got)
        probs.append(
            f"THE DECK USES {len(got)} DEPTH CUE(S) AND NEEDS {want_cues}. It has "
            f"{sorted(got) or '(none)'} and has not reached for {unused}. Depth is several weak "
            f"cues agreeing, not one strong one repeated")

    # ONE LIGHT, AND THE TWO SURFACES THAT HOLD IT MUST AGREE.
    if deck_light is not None:
        for f in frames:
            if f["light"] == "deck":
                continue      # txthree's deckRig reads the chassis's own light, so it agrees
            if f["light"] is None:
                # FAIL CLOSED (2026-09-20, review). `TXSCENE.create(cx, CAM)` and a call with no
                # `light` key both read as None here, and skipping them let the bench fall back
                # to its own default light while this check reported success. An unreadable light
                # on a STAGED frame is the one light invariant going unchecked, which is the
                # thing this is for. A flat frame is not asked, because it has no scene shadows.
                if f["staged"]:
                    probs.append(
                        f"{f['name']}: the scene light cannot be read from its TXSCENE.create "
                        f"call, and the chassis declared az {deck_light[0]} el {deck_light[1]}. "
                        f"The bench falls back to its own default when none is passed, so an "
                        f"unreadable light is an unchecked one. Pass light: {{az, el}} inline")
                continue
            if abs(f["light"][0] - deck_light[0]) > 1.0 or abs(f["light"][1] - deck_light[1]) > 1.0:
                probs.append(
                    f"{f['name']}: the scene light is az {f['light'][0]} el {f['light'][1]} and "
                    f"the chassis declared az {deck_light[0]} el {deck_light[1]}. One frame, one "
                    f"sun, two directions. The chassis is the deck's light and the bench is told "
                    f"it, never given its own")
    return probs


def frames_in(slides_dir: Path) -> list[dict]:
    out = []
    for p in sorted(slides_dir.glob("slide-*.html")):
        out.append(frame_report(p.name, p.read_text(encoding="utf-8", errors="replace")))
    return out


def deck_light_of(slides_dir: Path) -> tuple[float, float] | None:
    """The chassis's declared light, found through whichever chassis the frames load."""
    for p in sorted(slides_dir.glob("slide-*.html")):
        src = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"js/(deck/[\w.-]+\.js)", src)
        if not m:
            continue
        f = REPO / "assets" / "js" / m.group(1)
        if f.exists():
            got = chassis_light(f.read_text(encoding="utf-8"))
            if got:
                return got
    return None


def plan_problems(dossiers: dict[int, dict], cfg: dict) -> list[str]:
    """The depth block, at the STORYBOARD, before a frame is drawn.

    WHY IT LIVES HERE RATHER THAN IN dossier_check (2026-09-20, review). The routine tells a run
    that every dossier carries a `depth:` block and then runs the planning gate, and that gate
    knew nothing about depth, so a storyboard could omit every block and pass conception with the
    omission found only after nine frames were implemented. That is the sequencing failure this
    requirement exists to prevent, one layer up.

    It is in THIS file rather than added to `dossier_check` so that one module owns the whole
    rule: the floor, the cue vocabulary and both halves of the check. Two modules splitting one
    law is how the scene light and the chassis light came to disagree.
    """
    n = len(dossiers)
    floor = min(int(cfg["min_staged_frames"]), n)
    want = min(int(cfg["min_distinct_cues"]), n)
    probs, declared, all_cues = [], 0, set()
    for k in sorted(dossiers):
        d = dossiers[k].get("depth")
        if not isinstance(d, dict):
            continue
        cues = d.get("cues") or []
        if isinstance(cues, str):
            cues = [c.strip() for c in cues.replace(",", " ").split()]
        cues = [str(c).upper() for c in cues]
        bad = [c for c in cues if c not in CUE_NAMES]
        if bad:
            probs.append(f"frame {k}: depth.cues names {bad}, which are not cues this bench "
                         f"builds. The vocabulary is {sorted(CUE_NAMES)}")
        good = [c for c in cues if c in CUE_NAMES]
        if len(good) < 2:
            probs.append(f"frame {k}: depth names {len(good)} cue(s) and a staged frame builds "
                         f"at least two. Depth is several weak cues agreeing")
            continue
        if not isinstance(d.get("eye"), (int, float)) or not isinstance(d.get("horizon"), (int, float)):
            probs.append(f"frame {k}: depth needs a numeric `eye` and `horizon`. An object "
                         f"taller than the eye projects ABOVE the horizon, where the type is, "
                         f"and a frame that has not chosen them finds that out at the render")
            continue
        declared += 1
        all_cues |= set(good)
    if declared < floor:
        probs.insert(0, f"THE STORYBOARD PLANS {declared} STAGED FRAME(S) AND NEEDS {floor}. Add "
                        f"a `depth:` block naming eye, horizon and at least two cues to enough "
                        f"frames, before any of them is drawn")
    if declared >= floor and len(all_cues) < want:
        probs.append(f"the plan reaches for {len(all_cues)} distinct cue(s) and needs {want}. "
                     f"It has {sorted(all_cues) or '(none)'}")
    return probs


def run_plan(board: Path, cfg: dict) -> int:
    import dossier_check
    ds = dossier_check.parse_dossiers(board.read_text(encoding="utf-8"))
    if not ds:
        print(f"depth_floor: no dossiers parsed from {board}", file=sys.stderr)
        return 1
    probs = plan_problems(ds, cfg)
    if probs:
        print(f"depth_floor --plan: FAIL, {len(probs)} problem(s) in {board}\n", file=sys.stderr)
        for x in probs:
            print(f"  - {x}", file=sys.stderr)
        print("\n  knowledge/carousel/ILLUSTRATION_SYSTEM.md, 'THE FRAME STANDS IN A PLACE'.",
              file=sys.stderr)
        return 1
    print(f"depth_floor --plan: ok, {len(ds)} dossier(s) plan their camera")
    return 0


def run(slides_dir: Path) -> int:
    frames = frames_in(slides_dir)
    if not frames:
        print(f"depth_floor: no frames in {slides_dir}", file=sys.stderr)
        return 1
    probs = check(frames, load_config(), deck_light_of(slides_dir))
    staged = sum(1 for f in frames if f["staged"])
    got = sorted(set().union(*[f["cues"] for f in frames]))
    if probs:
        print(f"depth_floor: FAIL, {len(probs)} problem(s) in {slides_dir}\n", file=sys.stderr)
        for p in probs:
            print(f"  - {p}", file=sys.stderr)
        print("\n  knowledge/carousel/ILLUSTRATION_SYSTEM.md, 'THE FRAME STANDS IN A PLACE', "
              "is the standard. assets/js/txscene.js is the bench.", file=sys.stderr)
        return 1
    print(f"depth_floor: ok, {staged} of {len(frames)} frames staged, cues {got}")
    return 0


def self_test() -> int:
    fails = []

    def ok(label: str, cond: bool, detail: str = "") -> None:
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + (f"  [{detail}]" if not cond else ""))
        if not cond:
            fails.append(label)

    cfg = {"min_staged_frames": 5, "min_distinct_cues": 4}

    def frame(name, src):
        return frame_report(name, src)

    FLAT = "<script>cx.fillRect(0,0,100,100); cx.fill()</script>"
    STAGED = ("<script>var S = TXSCENE.create(cx, {eye:1.4, horizon:640, light:{az:-40,el:38}});"
              "S.ground({}); S.gridZ({}); S.fade('#fff', 30);"
              "S.shadow(bus,{X:2,Z:30}); S.sprite(bus,{X:2,Z:30});"
              "var p = S.project(0,0,30); S.ppm(30); S.groundY(30);</script>")

    # THE DEFECT: nine frames drawn in screen pixels.
    flat = [frame(f"slide-{i:02d}.html", FLAT) for i in range(1, 10)]
    probs = check(flat, cfg)
    ok("nine flat frames fail", bool(probs), "passed")
    ok("...and the message names the count and the floor",
       any("0 of 9 frames are staged" in p and "needs 5" in p for p in probs), str(probs[:1]))

    staged9 = [frame(f"slide-{i:02d}.html", STAGED) for i in range(1, 10)]
    ok("nine staged frames pass", not check(staged9, cfg), str(check(staged9, cfg)[:1]))

    mixed = staged9[:5] + flat[5:]
    ok("five staged of nine meets a five frame floor", not check(mixed, cfg))
    ok("...and four does not", bool(check(staged9[:4] + flat[4:], cfg)))

    # A CAMERA BUILT AND NOT USED. 54 frames of this corpus load the bench and draw in pixels.
    unused = ("<script>var S = TXSCENE.create(cx, {eye:1.4, horizon:640, light:{az:-40,el:38}});"
              "S.ground({}); cx.fillRect(0,0,100,100);</script>")
    probs = check([frame("slide-01.html", unused)] * 9, cfg)
    ok("a bench built and never placed through fails", bool(probs))
    ok("...and the message says so rather than reporting a missing bench",
       any("never places through the camera" in p for p in probs), str(probs[:1]))

    # PLACED BUT UNLIT. A thing at true scale with no shadow does not sit on the ground.
    noshadow = ("<script>var S = TXSCENE.create(cx, {eye:1.4, horizon:640, light:{az:-40,el:38}});"
                "S.ground({}); S.project(0,0,30); S.ppm(30);</script>")
    probs = check([frame("slide-01.html", noshadow)] * 9, cfg)
    ok("placed with no cast shadow is not staged", bool(probs))
    ok("...and the message names the shadow",
       any("casts no shadow" in p for p in probs), str(probs[:1]))

    # THE CUE COUNT. One strong cue repeated is not depth.
    onecue = ("<script>var S = TXSCENE.create(cx, {eye:1.4, horizon:640, light:{az:-40,el:38}});"
              "S.ground({}); S.project(0,0,30); S.shadow(b,{});</script>")
    probs = check([frame(f"slide-{i:02d}.html", onecue) for i in range(1, 10)], cfg)
    ok("a deck with two cues is refused", bool(probs))
    ok("...and the message names the cues it has not reached for",
       any("has not reached for" in p and "AERIAL" in p for p in probs), str(probs[:1]))

    # THE ALIAS. Matching only `TXSCENE.` would miss every frame that actually projects.
    BOUND = "var S = TXSCENE.create(cx, {}); "
    ok("a bound alias is recognised", "LINEAR_PERSPECTIVE" in cues_in(BOUND + "S.project(0,0,4)"))
    ok("...and so is the full name", "LINEAR_PERSPECTIVE" in cues_in("TXSCENE.project(0,0,4)"))
    ok("...and a bare word is not mistaken for a call", not cues_in("the project is late"))

    # CUES ARE BOUND TO THE BENCH INSTANCE. 62 `J.sprite(` calls in this corpus belong to
    # something that is not the bench, and an unbound match counted every one of them.
    ok("an UNBOUND identifier is not the bench",
       not cues_in(BOUND + "TXOBJ.sprite('bus'); J.project(1,2,3)"))
    ok("...so a frame that only BUILDS a sprite has placed nothing",
       not frame_report("f", BOUND + "S.ground({}); TXOBJ.sprite('bus'); S.shadow(b,{})")["placed"])
    ok("the alias is found without a declarator too",
       "TXSCENE" in bench_aliases("S = TXSCENE.create(cx,{})") and
       "S" in bench_aliases("S = TXSCENE.create(cx,{})"))

    # shadowVec RETURNS A VECTOR AND PAINTS NOTHING.
    ok("S.shadowVec alone is not a cast shadow",
       not frame_report("f", BOUND + "S.ground({}); S.project(0,0,9); S.shadowVec()")["shadow"])
    ok("...and S.shadow is", frame_report("f", BOUND + "S.ground({}); S.shadow(b,{})")["shadow"])

    # THE OPT-OUT IS PER CALL. One decorative unshadowed box used to silence the whole frame.
    mixed_box = BOUND + "S.ground({}); S.box({X:0,Z:9,shadow:false}); S.box({X:2,Z:9});"
    ok("one shadow:false beside a default box still casts",
       frame_report("f", mixed_box)["shadow"], "the opt-out went frame wide")
    ok("...and a lone shadow:false box does not",
       not frame_report("f", BOUND + "S.ground({}); S.box({X:0,Z:9,shadow:false})")["shadow"])

    # A STAGED FRAME STANDS ON A RENDERED PLANE.
    ok("placed and shadowed with NO ground is not staged",
       not frame_report("f", BOUND + "S.project(0,0,9); S.shadow(b,{})")["staged"])
    ok("...and gridZ counts as the plane being rendered",
       frame_report("f", BOUND + "S.gridZ({}); S.project(0,0,9); S.shadow(b,{})")["staged"])

    # ONE LIGHT, TWO SURFACES.
    agree = check(staged9, cfg, deck_light=(-40.0, 38.0))
    ok("a scene light matching the chassis passes", not agree, str(agree[:1]))
    probs = check(staged9, cfg, deck_light=(64.0, 26.0))
    ok("A SCENE LIGHT DISAGREEING WITH THE CHASSIS FAILS", bool(probs), "it passed")
    ok("...and the message names both",
       any("az -40.0 el 38.0" in p and "az 64.0 el 26.0" in p for p in probs), str(probs[:1]))
    ok("a one degree difference is tolerated, not a ten",
       not check(staged9, cfg, deck_light=(-40.5, 38.4)))

    ok("the chassis light is read out of a declare block",
       chassis_light('TXDECK.declare({world:"lamp", light:{az:64, el:26}, ground:"#000"})')
       == (64.0, 26.0))
    ok("the scene light is read out of a create block",
       scene_light("TXSCENE.create(cx, {w:1080, light:{az:-35, el:40}})") == (-35.0, 40.0))

    # THE COMPOUND PLACERS. S.box is placement AND a cast shadow in one call, and a gate that
    # only knows the low level names measures which style a frame is written in.
    BOXONLY = ("<script>var S = TXSCENE.create(cx, {eye:1.4, horizon:560, light:{az:64,el:26}});"
               "S.ground({}); S.gridZ({}); S.box({X:0, Z:10, w:2, h:2, d:2});</script>")
    r = frame_report("slide-01.html", BOXONLY)
    ok("a frame whose only placer is S.box is staged", r["staged"], str(r))
    ok("...and S.box counts as its own cast shadow", r["shadow"])
    OFF = BOXONLY.replace("d:2}", "d:2, shadow:false}")
    ok("...unless the call passes shadow:false", not frame_report("s", OFF)["shadow"])
    ok("a frame placing only with S.sprite is placed",
       frame_report("s", "var S = TXSCENE.create(cx,{}); S.ground({});"
                         "S.sprite(b,{X:1,Z:9}); S.shadow(b,{X:1,Z:9});")["placed"])

    # AN UNREADABLE SCENE LIGHT FAILS CLOSED ON A STAGED FRAME.
    opaque = ("<script>var S = TXSCENE.create(cx, CAM); S.ground({}); S.project(0,0,9);"
              "S.shadow(b,{});</script>")
    probs = check([frame(f"slide-{i:02d}.html", opaque) for i in range(1, 10)], cfg,
                  deck_light=(64.0, 26.0))
    ok("a scene light that cannot be read is refused", bool(probs), "it passed")
    ok("...and the message says the bench falls back to its own default",
       any("unreadable light is an unchecked one" in p for p in probs), str(probs[:1]))
    ok("a FLAT frame is not asked for a light it has no shadows from",
       not any("unreadable" in p for p in check(flat, cfg, deck_light=(64.0, 26.0))))

    # THE PLAN GATE, at the storyboard, before a frame exists.
    good_plan = {i: {"slide": i, "depth": {"eye": 1.4, "horizon": 560,
                                           "cues": ["LINEAR_PERSPECTIVE", "CAST_SHADOW",
                                                    "AERIAL", "RELATIVE_SIZE"]}}
                 for i in range(1, 10)}
    ok("a storyboard planning nine cameras passes", not plan_problems(good_plan, cfg))
    bare = {i: {"slide": i} for i in range(1, 10)}
    probs = plan_problems(bare, cfg)
    ok("a storyboard with NO depth blocks is refused", bool(probs))
    ok("...and it says so before a frame is drawn",
       any("PLANS 0 STAGED FRAME" in p for p in probs), str(probs[:1]))
    one_cue = {**good_plan, 1: {"slide": 1, "depth": {"eye": 1.4, "horizon": 560,
                                                      "cues": ["AERIAL"]}}}
    ok("a frame naming one cue is refused",
       any("at least two" in p for p in plan_problems(one_cue, cfg)))
    bogus = {**good_plan, 2: {"slide": 2, "depth": {"eye": 1.4, "horizon": 560,
                                                    "cues": ["VIBES", "AERIAL", "CAST_SHADOW"]}}}
    ok("a cue outside the vocabulary is named",
       any("VIBES" in p for p in plan_problems(bogus, cfg)))
    nogeo = {**good_plan, 3: {"slide": 3, "depth": {"cues": ["AERIAL", "CAST_SHADOW"]}}}
    ok("a depth block with no eye or horizon is refused",
       any("numeric `eye` and `horizon`" in p for p in plan_problems(nogeo, cfg)))
    onecue_deck = {i: {"slide": i, "depth": {"eye": 1.4, "horizon": 560,
                                             "cues": ["AERIAL", "CAST_SHADOW"]}}
                   for i in range(1, 10)}
    ok("a plan reaching for two cues across the deck is refused",
       any("distinct cue" in p for p in plan_problems(onecue_deck, cfg)))

    # THE FLOOR SCALES DOWN TO A SHORT DECK AND NEVER UP.
    ok("a three frame deck needs three staged", not check(staged9[:3], cfg))
    ok("...and two of three is refused", bool(check(staged9[:2] + flat[:1], cfg)))

    try:
        c = load_config()
        ok("config carries a floor", isinstance(c.get("min_staged_frames"), int))
        ok("...and it is derived rather than asserted", bool(c.get("derived_from")))
    except Exception as exc:                                             # noqa: BLE001
        ok("config loads", False, str(exc))

    # AND IT REFUSES THE DECKS THAT ACTUALLY SHIPPED.
    for date in ("2026-09-18", "2026-09-19", "2026-09-20"):
        sd = REPO / "runs" / "carousel" / date / "slides"
        if not sd.is_dir():
            continue
        got = check(frames_in(sd), load_config(), deck_light_of(sd))
        ok(f"the shipped {date} deck is refused", bool(got), "it passed")

    # THE GPU BENCH, 2026-09-23. A frame rendered through txthree.js places a physically based
    # object through a perspective camera onto a ground plane under a shadow mapped key light,
    # and this gate used to score it as unstaged with zero cues.
    GPU = ("<script type=\"module\">window.renderReady=(async()=>{"
           "const THREE=await import('@@ASSETS@@/js/three.module.min.js');"
           "const T=(await import('@@ASSETS@@/js/txthree.js')).init(THREE);"
           "const R=T.setup(c,{w:1080,h:1350,fog:[0x0f1520,10,40]});"
           "T.deckRig(R,T.rigs.arcticNight); T.ground(R,{});"
           "const m=new THREE.Mesh(g,T.mat.steel()); for (let i=0;i<40;i++){ T.add(R,m.clone()); }"
           "T.frame(R,{from:[1,2,3]}); await T.snapshot(R);})();</script>")
    g = frame("g", GPU)
    ok("a GPU rendered frame is STAGED", g["staged"], str(g))
    ok("...and carries at least five distinct cues", len(g["cues"]) >= 5, str(sorted(g["cues"])))
    ok("...and its light agrees with the chassis by construction", g["light"] == "deck", str(g["light"]))
    ok("nine GPU frames satisfy the deck floor",
       check([frame(f"s{i}", GPU) for i in range(9)], cfg, (40.0, 30.0)) == [])
    rigonly = frame("r", GPU.replace("T.deckRig(R", "T.rig(R"))
    ok("a GPU frame lit by its OWN rig carries a second copy of the light and fails closed",
       any("cannot be read" in x for x in check([rigonly] * 9, cfg, (40.0, 30.0))),
       str(check([rigonly] * 9, cfg, (40.0, 30.0)))[:160])
    ok("importing the GPU bench and drawing nothing with it is NOT staged",
       not frame("i", "<script type=\"module\">const T=(await import('@@ASSETS@@/js/txthree.js')).init(THREE);"
                 "</script>")["staged"])
    ok("a GPU frame that never snapshots is NOT staged",
       not frame("n", GPU.replace("await T.snapshot(R);", ""))["staged"])
    ok("a GPU frame with no ground plane is NOT staged",
       not frame("f", GPU.replace("T.ground(R,{});", ""))["staged"])
    STATIC = GPU.replace("const T=(await import('@@ASSETS@@/js/txthree.js')).init(THREE);",
                         "").replace("<script type=\"module\">",
                                     "<script type=\"module\">import { init } from "
                                     "'@@ASSETS@@/js/txthree.js';const T=init(THREE);")
    ok("the STATIC import form binds the bench too, and stages",
       frame("s", STATIC)["staged"] and frame("s", STATIC)["light"] == "deck", str(frame("s", STATIC)))
    ok("...and a static import with nothing drawn is NOT staged",
       not frame("s0", "<script type=\"module\">import { init } from '@@ASSETS@@/js/txthree.js';"
                       "const T=init(THREE);</script>")["staged"])

    print(f"\ndepth_floor self-test: {'FAIL' if fails else 'ok'}, {len(fails)} failure(s)")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date")
    ap.add_argument("--slides-dir")
    ap.add_argument("--out-root", default=None)
    ap.add_argument("--plan", action="store_true",
                    help="the storyboard's depth blocks, before a frame is drawn")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.plan:
        root = Path(a.out_root) if a.out_root else (REPO / "runs" / "carousel")
        if a.date and not (root / a.date).exists() and (REPO / "out" / a.date).exists():
            root = REPO / "out"
        board = (Path(a.slides_dir).parent / "storyboard.md") if a.slides_dir \
            else (root / a.date / "storyboard.md")
        if not board.exists():
            print(f"depth_floor: no storyboard at {board}", file=sys.stderr)
            return 1
        return run_plan(board, load_config())
    if a.slides_dir:
        return run(Path(a.slides_dir))
    if not a.date:
        ap.error("--date, --slides-dir or --self-test")
    root = Path(a.out_root) if a.out_root else (REPO / "runs" / "carousel")
    if not (root / a.date).exists() and (REPO / "out" / a.date).exists():
        root = REPO / "out"
    return run(root / a.date / "slides")


if __name__ == "__main__":
    sys.exit(main())
