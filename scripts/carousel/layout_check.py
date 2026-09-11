#!/usr/bin/env python3
"""layout_check.py. Is there an IMAGE on this frame, and did the deck turn the page?

THE DEFECT THIS EXISTS FOR (2026-09-11, carousel no. 21)

Twenty one decks used one skeleton on every frame. A kicker at the top, a headline under it, a
small drawing under that, a source line at the bottom. The flow critic called it "the same page
nine times", and every gate in this suite was green while it said so, because every gate asks
whether what is on the frame is RIGHT and none asks where the image is or how much of the page
it takes. A magazine spread and a poster differ by exactly that. The decision has to be made per
frame, on purpose, from a short list, with a rule that stops the same choice being made twice in
a row, and a gate has to read the pixels afterwards and ask whether an image was drawn where the
plan said one would be.

`assets/js/txlayout.js` is where the planner makes that choice. It names ten archetypes and a
rotation rule on two single-line declarations. This file carries a copy of both, and its
`--self-test` reads the JS file and asserts the copies agree, so the planner in the browser and
the gate here can never disagree about what a name means. A copy nothing checks is the oldest
shape in GATE_LESSONS.

WHAT A DOSSIER DECLARES, from 2026-09-12 on. Three keys beside the ones `dossier_check` reads:

    layout: FULL_BLEED                       one of the ten archetype names
    primary_image:
      subject: "a school bus at true scale on a caliche lot"
      rect: [0, 0, 1080, 860]                x, y, w, h in the 1080 x 1350 frame, in px
      bleeds: [top, left, right]             which frame edges the image runs off, may be []
    accent: "#D8731F"                        the deck's ONE accent, or the word none on a
                                             frame that does not use it

WHAT IT MEASURES, on `storyboard.md` plus the rendered frames and the render report

    1  ROTATION      over the `layout` values in slide order. No archetype twice in a row, at
                     least `min_distinct` distinct on a deck of six or more, TYPE_AS_OBJECT at
                     most `max_type_as_object`, FULL_BLEED plus CLOSE_CROP at least
                     `min_full_bleed_or_close_crop` between them on a deck of six or more, and
                     every value one of the ten names.
    2  AREA          each rect's area over the frame's, at least `min_primary_area`.
    3  BLEED         at least `min_bleed_frames` rects touch a frame edge. A declared edge the
                     rect does not touch is a fail. A touched edge left undeclared is a warning.
    4  DETAIL        on the pixels. The frame at 540 x 675, the rect at that scale cut into 8 px
                     cells, every cell under a text box from the render report dropped, and the
                     luminance standard deviation of each cell that is left. At least a quarter
                     of them have to exceed 6.0. This is what says an image was drawn there
                     rather than a flat plate with type on it. ONE ARCHETYPE IS THE EXCEPTION
                     AND IT IS THE ONE THE TABLE DEFINES THAT WAY: on a DOCUMENT the type on
                     the page is the image, so its text cells count as detail instead of being
                     dropped, and the share is over every cell in the rect. The same frame
                     keeps its type in the silhouette measure below, for the same reason.
    5  SILHOUETTE    at thumb scale. The rect region fitted inside 54 x 68 px, the frame's ground
                     taken as the median colour OUTSIDE the rect at thumb scale (the whole
                     frame's when the rect is a full bleed), and every
                     pixel further than 12 Lab units from that ground marked as subject. The
                     subject has to cover at least 8 percent of the rect and its largest
                     4-connected component has to hold at least half of it. One readable
                     silhouette rather than dust. Text boxes are masked out here too, because a
                     headline is type, and a headline that is the only silhouette in a rect is
                     the exact frame this gate exists to refuse. A GRID is the exception, and
                     for the opposite reason: it is a count, so its subject has to come APART
                     into at least four pieces each holding two percent of it, which is what
                     makes the units countable in the feed.
    6  ACCENT        the deck's accent hex at thumb scale, 216 x 270. Pixels within 12 Lab units
                     of it are the accent. It has to be present, at 0.2 percent of the frame or
                     more, on at least three frames and at most six, and it may never cover more
                     than 8 percent of any frame. The flag red in config/brand.yaml is reserved
                     and is refused as an accent outright.

Lab is CIE76 over sRGB to XYZ to Lab under D65, written here, so this needs numpy and Pillow and
nothing else.

SCOPE. If no dossier declares a `layout`, the illustration system was not in force on that deck
and nothing is measured. That exits 0 with a note, unless `--require` is passed, which the
routine does, in which case it is a fail that says the run did not plan its layouts. If some
dossiers carry the keys and others do not, that is a fail whatever the flag, because a plan
that is half in a system is not in it.

    layout_check.py --run-dir out/<date>            a live run, frames under render/
    layout_check.py --run-dir runs/carousel/<date>  a shipped run, frames beside the storyboard
    layout_check.py --date <date>                   maps to out/<date>
    layout_check.py --self-test

Exit 0 clean, 1 findings, 2 could not run.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
JS_TABLE = REPO_ROOT / "assets" / "js" / "txlayout.js"

# THE TWO TABLES, copied from assets/js/txlayout.js. The self-test parses that file and asserts
# these agree with it. Edit both or neither.
ARCHETYPES = ["FULL_BLEED", "SPLIT_HORIZON", "TYPE_AS_OBJECT", "OBJECT_AND_CAPTION", "DIAGRAM", "GRID", "DOCUMENT", "MAP", "CLOSE_CROP", "FIGURE_SCALE"]
ROTATION = {"max_consecutive": 1, "min_distinct": 5, "max_type_as_object": 1, "min_full_bleed_or_close_crop": 2, "min_primary_area": 0.30, "min_bleed_frames": 4}

W, H = 1080, 1350
LONG_DECK = 6            # the distinct and the inside rules bind from this many frames up
EDGES = ("top", "left", "right", "bottom")
INSIDE = ("FULL_BLEED", "CLOSE_CROP")

DETAIL_SCALE = (540, 675)
CELL = 8
DETAIL_STD = 6.0
DETAIL_SHARE = 0.25

SIL_FIT = (54, 68)
THUMB = (216, 270)
LAB_NEAR = 12.0
SIL_COVER = 0.08
SIL_ONE = 0.50
# A GRID is a count, so its subject is expected to come apart: this many pieces at thumb scale,
# each at least PIECE_MIN of the subject, instead of one silhouette holding SIL_ONE of it.
GRID_PIECES = 4
PIECE_MIN = 0.02

ACCENT_PRESENT = 0.002
ACCENT_CAP = 0.08
ACCENT_MIN_FRAMES = 3
ACCENT_MAX_FRAMES = 6
FLAG_RED = "#BF0A30"     # config/brand.yaml `flag_red`. URGENT ONLY, never a deck's accent.

NOT_IN_FORCE = ("no dossier declares a layout, so the illustration system was not in force on "
                "this deck and nothing was measured")

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


# --------------------------------------------------------------------------- the JS table
def js_tables(js_path: Path = JS_TABLE):
    """(ARCHETYPES, ROTATION) as the browser has them. Raises rather than guesses."""
    if not js_path.exists():
        raise FileNotFoundError(f"{js_path} is missing")
    text = js_path.read_text(encoding="utf-8")
    m1 = re.search(r"^\s*var ARCHETYPES = (\[.*?\]);\s*$", text, re.M)
    m2 = re.search(r"^\s*var ROTATION = (\{.*?\});\s*$", text, re.M)
    if not m1:
        raise ValueError(f"{js_path.name} carries no single-line `var ARCHETYPES = [...];`")
    if not m2:
        raise ValueError(f"{js_path.name} carries no single-line `var ROTATION = {{...}};`")
    return json.loads(m1.group(1)), json.loads(m2.group(1))


def agreement(js_path: Path = JS_TABLE, archetypes=None, rotation=None) -> list[str]:
    """Every way the Python copy differs from the JS one. Empty means they agree."""
    archetypes = ARCHETYPES if archetypes is None else archetypes
    rotation = ROTATION if rotation is None else rotation
    try:
        ja, jr = js_tables(js_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"the JS table could not be read: {exc}. The gate can't vouch for a table it "
                f"can't compare against, so this is a fail rather than a skip"]
    out = []
    if list(ja) != list(archetypes):
        out.append(f"ARCHETYPES differ. JS has {ja}, Python has {list(archetypes)}")
    for k in sorted(set(jr) | set(rotation)):
        if jr.get(k) != rotation.get(k):
            out.append(f"ROTATION[{k!r}] is {jr.get(k)!r} in JS and {rotation.get(k)!r} in Python")
    return out


# --------------------------------------------------------------------------- the artifacts
def _dossier_module():
    spec = importlib.util.spec_from_file_location(
        "dossier_check", Path(__file__).resolve().parent / "dossier_check.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _slide_no(name: str) -> int | None:
    m = re.search(r"slide-(\d+)", name)
    return int(m.group(1)) if m else None


def find_renders(run_dir: Path) -> list[Path]:
    """A live run keeps png under render/, a shipped run keeps webp beside the storyboard."""
    for d in (run_dir / "render", run_dir):
        pngs = sorted(d.glob("slide-*.png")) or sorted(d.glob("slide-*.webp"))
        if pngs:
            return pngs
    return []


def find_report(run_dir: Path) -> Path | None:
    for p in (run_dir / "render" / "render_report.json", run_dir / "render_report.json"):
        if p.exists():
            return p
    return None


def text_boxes(report: dict) -> dict[int, list[tuple]]:
    """Per slide, every line box the render recorded, in frame px.

    `lines` is what the collision gate compares and it is tighter than the element's box, so a
    caption's margin is not thrown away with its glyphs. The block box is the fallback for a
    node that recorded no lines.
    """
    out: dict[int, list[tuple]] = {}
    for i, rec in enumerate(report.get("slides") or [], start=1):
        n = _slide_no(str(rec.get("file") or rec.get("png") or "")) or i
        boxes = []
        for node in rec.get("text_nodes") or []:
            lines = node.get("lines") or [[node.get("x", 0), node.get("y", 0),
                                          node.get("w", 0), node.get("h", 0)]]
            for b in lines:
                if len(b) == 4 and b[2] > 0 and b[3] > 0:
                    boxes.append(tuple(float(v) for v in b))
        out[n] = boxes
    return out


# --------------------------------------------------------------------------- colour
def lab(rgb):
    """sRGB (0 to 255) to CIE Lab under D65. Vectorised over any leading shape."""
    import numpy as np
    c = np.asarray(rgb, float) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16.0 / 116.0)
    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def lab_distance(p, q):
    import numpy as np
    return np.sqrt(((np.asarray(p, float) - np.asarray(q, float)) ** 2).sum(axis=-1))


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# --------------------------------------------------------------------------- the pixels
def load_frame(p: Path):
    """The frame at 1080 x 1350 whatever scale it was rendered at, so a rect is always in px."""
    from PIL import Image
    img = Image.open(p).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.BOX)
    return img


def _luma(a):
    return 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]


def detail_fraction(img, rect, boxes, count_text: bool = False) -> tuple[float, int, int]:
    """(share of kept cells with std above DETAIL_STD, cells kept, cells dropped for text).

    With `count_text`, which is the DOCUMENT archetype's case, a cell under type is not dropped
    but counted as detail, because on a drawn page the type IS the image. The share is then
    over every cell in the rect, and the third value still reports how many were under type.
    """
    import numpy as np
    from PIL import Image
    small = np.asarray(img.resize(DETAIL_SCALE, Image.BOX)).astype(float)
    luma = _luma(small)
    x, y, w, h = rect
    x0, y0 = int(round(x * 0.5)), int(round(y * 0.5))
    x1, y1 = int(round((x + w) * 0.5)), int(round((y + h) * 0.5))
    region = luma[y0:y1, x0:x1]
    rows, cols = region.shape[0] // CELL, region.shape[1] // CELL
    if rows == 0 or cols == 0:
        return 0.0, 0, 0
    cells = region[:rows * CELL, :cols * CELL].reshape(rows, CELL, cols, CELL)
    std = cells.std(axis=(1, 3))
    text = np.zeros(luma.shape, bool)
    for bx, by, bw, bh in boxes:
        text[max(0, int(by * 0.5)):int(np.ceil((by + bh) * 0.5)),
             max(0, int(bx * 0.5)):int(np.ceil((bx + bw) * 0.5))] = True
    dropped = text[y0:y0 + rows * CELL, x0:x0 + cols * CELL] \
        .reshape(rows, CELL, cols, CELL).any(axis=(1, 3))
    if count_text:
        return float(((std > DETAIL_STD) | dropped).mean()), int(dropped.size), int(dropped.sum())
    keep = ~dropped
    kept = int(keep.sum())
    if kept == 0:
        return 0.0, 0, int(dropped.sum())
    return float((std[keep] > DETAIL_STD).mean()), kept, int(dropped.sum())


def _components(mask) -> list[int]:
    """Sizes of every 4-connected True region. The mask is at most 54 x 68, so a plain
    breadth-first walk is the whole cost."""
    import numpy as np
    seen = np.zeros_like(mask, bool)
    h, w = mask.shape
    sizes = []
    for sy in range(h):
        for sx in range(w):
            if not mask[sy, sx] or seen[sy, sx]:
                continue
            q, size = deque([(sy, sx)]), 0
            seen[sy, sx] = True
            while q:
                cy, cx = q.popleft()
                size += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            sizes.append(size)
    return sizes


def _largest_component(mask) -> int:
    return max(_components(mask), default=0)


def ground_colour(img, rect=None):
    """The frame's ground: the median colour OUTSIDE the primary rect at thumb scale, because
    the subject is what differs from what surrounds it. When the rect leaves under a tenth of
    the frame outside it, a full bleed, the whole frame's median stands in."""
    import numpy as np
    from PIL import Image
    thumb = np.asarray(img.resize(THUMB, Image.BOX)).astype(float)
    if rect is not None:
        sx, sy = THUMB[0] / img.width, THUMB[1] / img.height
        x, y, w, h = rect
        keep = np.ones(thumb.shape[:2], bool)
        keep[max(0, int(y * sy)):int(np.ceil((y + h) * sy)), max(0, int(x * sx)):int(np.ceil((x + w) * sx))] = False
        if keep.mean() >= 0.10:
            return np.median(thumb[keep], axis=0)
    return np.median(thumb.reshape(-1, 3), axis=0)


def silhouette(img, rect, boxes) -> tuple[float, float, int]:
    """(subject coverage of the rect, share of the subject in its largest component, and the
    number of pieces holding at least PIECE_MIN of the subject, which is what a GRID is held to)."""
    import numpy as np
    from PIL import Image
    x, y, w, h = rect
    s = min(SIL_FIT[0] / w, SIL_FIT[1] / h)
    tw, th = max(1, int(round(w * s))), max(1, int(round(h * s)))
    small = np.asarray(img.crop((x, y, x + w, y + h)).resize((tw, th), Image.BOX)).astype(float)
    subject = lab_distance(lab(small), lab(ground_colour(img, rect))) > LAB_NEAR
    for bx, by, bw, bh in boxes:
        X0, Y0 = max(0, int((bx - x) * s)), max(0, int((by - y) * s))
        X1, Y1 = min(tw, int(np.ceil((bx + bw - x) * s))), min(th, int(np.ceil((by + bh - y) * s)))
        if X1 > X0 and Y1 > Y0:
            subject[Y0:Y1, X0:X1] = False
    n = int(subject.sum())
    if n == 0:
        return 0.0, 0.0, 0
    sizes = _components(subject)
    return n / subject.size, max(sizes) / n, sum(1 for s in sizes if s >= PIECE_MIN * n)


def accent_coverage(img, hex_colour: str) -> float:
    import numpy as np
    from PIL import Image
    thumb = np.asarray(img.resize(THUMB, Image.BOX)).astype(float)
    return float((lab_distance(lab(thumb), lab(np.array(hex_rgb(hex_colour), float))) <= LAB_NEAR).mean())


# --------------------------------------------------------------------------- the plan
def rotation_problems(seq: list[tuple[int, str]]) -> list[str]:
    """The rotation rule over (slide, layout) pairs in slide order."""
    out = []
    for n, a in seq:
        if a not in ARCHETYPES:
            out.append(f"slide {n}: `layout: {a}` is not an archetype. The ten are "
                       f"{', '.join(ARCHETYPES)}")
    names = [a for _, a in seq]
    run = 1
    for i in range(1, len(seq)):
        if names[i] == names[i - 1]:
            run += 1
            if run > ROTATION["max_consecutive"]:
                out.append(f"frames {seq[i - 1][0]} and {seq[i][0]} repeat {names[i]}. No "
                           f"archetype twice in a row, because the reader has just seen that page")
        else:
            run = 1
    if len(seq) >= LONG_DECK:
        distinct = len(set(names))
        if distinct < ROTATION["min_distinct"]:
            out.append(f"only {distinct} distinct archetype(s) across {len(seq)} frames "
                       f"({', '.join(sorted(set(names)))}). The rule is at least "
                       f"{ROTATION['min_distinct']} on a deck of {LONG_DECK} or more")
        inside = sum(1 for a in names if a in INSIDE)
        if inside < ROTATION["min_full_bleed_or_close_crop"]:
            out.append(f"FULL_BLEED and CLOSE_CROP {inside} between them. At least "
                       f"{ROTATION['min_full_bleed_or_close_crop']} on a deck of {LONG_DECK} or "
                       f"more, so the deck has frames the reader is inside rather than looking at")
    tao = names.count("TYPE_AS_OBJECT")
    if tao > ROTATION["max_type_as_object"]:
        out.append(f"TYPE_AS_OBJECT {tao} times, on slides "
                   f"{', '.join(str(n) for n, a in seq if a == 'TYPE_AS_OBJECT')}. At most "
                   f"{ROTATION['max_type_as_object']}, because twice is a trick")
    return out


def plan_of(n: int, d: dict) -> tuple[dict | None, list[str]]:
    """One slide's declaration, normalised, plus everything wrong with its shape."""
    probs = []
    layout = str(d.get("layout") or "").strip()
    if not layout:
        probs.append(f"slide {n}: `layout` is empty")
    pi = d.get("primary_image")
    if not isinstance(pi, dict):
        probs.append(f"slide {n}: `primary_image` is missing or is not a mapping of subject, "
                     f"rect and bleeds")
        pi = {}
    subject = str(pi.get("subject") or "").strip()
    if not subject:
        probs.append(f"slide {n}: `primary_image.subject` is empty. Name the thing that is drawn")
    rect = pi.get("rect")
    ok_rect = (isinstance(rect, list) and len(rect) == 4
               and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in rect))
    if not ok_rect:
        probs.append(f"slide {n}: `primary_image.rect` must be [x, y, w, h] in frame px, got "
                     f"{rect!r}")
        rect = None
    else:
        rect = [float(v) for v in rect]
        if rect[2] <= 0 or rect[3] <= 0:
            probs.append(f"slide {n}: `primary_image.rect` has no area, got {rect}")
            rect = None
    bleeds = pi.get("bleeds")
    if bleeds is None or not isinstance(bleeds, list):
        probs.append(f"slide {n}: `primary_image.bleeds` must be a list of edges, [] when the "
                     f"image touches none")
        bleeds = []
    bleeds = [str(b).strip().lower() for b in bleeds]
    for b in bleeds:
        if b not in EDGES:
            probs.append(f"slide {n}: `bleeds` names {b!r}, and an edge is one of "
                         f"{', '.join(EDGES)}")
    if "accent" not in d or d.get("accent") is None:
        probs.append(f"slide {n}: `accent` is missing. Write the deck's accent hex, or the word "
                     f"none on a frame that does not use it")
        accent = None
    else:
        accent = str(d.get("accent")).strip()
        if accent.lower() in ("none", ""):
            accent = None
        elif not HEX.match(accent):
            probs.append(f"slide {n}: `accent: {accent}` is neither a hex colour nor the word none")
            accent = None
        else:
            accent = accent.upper()
    if probs:
        return None, probs
    # Touching is judged on the rect as declared, so a rect that overshoots the frame still
    # touches. Area and the pixels use the part of it that is on the frame.
    x, y, w, h = rect
    touched = set()
    if y <= 0:
        touched.add("top")
    if x <= 0:
        touched.add("left")
    if x + w >= W:
        touched.add("right")
    if y + h >= H:
        touched.add("bottom")
    cx0, cy0 = max(0, x), max(0, y)
    cx1, cy1 = min(W, x + w), min(H, y + h)
    clamped = (int(round(cx0)), int(round(cy0)), int(round(cx1 - cx0)), int(round(cy1 - cy0)))
    if clamped[2] <= 0 or clamped[3] <= 0:
        return None, [f"slide {n}: `primary_image.rect` {rect} lies entirely off the frame"]
    return {"slide": n, "layout": layout, "subject": subject, "rect": clamped,
            "declared": set(bleeds), "touched": touched, "accent": accent}, []


def check(run_dir: Path, require: bool = False):
    """(code, problems, rows). Rows are per-frame dicts of the measured numbers, plus dicts
    carrying only a `note` for anything said about the deck as a whole."""
    run_dir = Path(run_dir)
    board = run_dir / "storyboard.md"
    if not board.exists():
        return 2, [f"no storyboard.md in {run_dir}"], []
    dossiers = _dossier_module().parse_dossiers(board.read_text(encoding="utf-8"))
    dossiers = {n: d for n, d in dossiers.items() if isinstance(d, dict)}
    if not dossiers:
        return 2, [f"no dossiers could be read from {board}"], []

    declared = {n: d for n, d in dossiers.items() if "layout" in d}
    if not declared:
        if require:
            return 1, ["no dossier declares a layout, so the run did not plan its layouts. From "
                       "2026-09-12 every dossier carries `layout`, `primary_image` and `accent`, "
                       "and a deck whose frames were not each given an archetype, a rect and a "
                       "bleed is the same page nine times waiting to happen"], []
        return 0, [], [{"note": NOT_IN_FORCE}]

    problems: list[str] = []
    warnings: list[str] = []
    if len(declared) != len(dossiers):
        without = sorted(set(dossiers) - set(declared))
        problems.append(f"slide(s) {', '.join(map(str, without))} carry no `layout` while "
                        f"slide(s) {', '.join(map(str, sorted(declared)))} do. The illustration "
                        f"system is all or nothing within a deck, because a rotation rule over "
                        f"half a deck rotates nothing")

    plans: dict[int, dict] = {}
    for n in sorted(declared):
        plan, probs = plan_of(n, declared[n])
        problems.extend(probs)
        if plan:
            plans[n] = plan

    # 1. rotation, on every slide that named a layout, whether or not the rest of it parsed
    seq = [(n, str(declared[n].get("layout") or "").strip()) for n in sorted(declared)]
    problems.extend(rotation_problems([(n, a) for n, a in seq if a]))

    # 2. area and 3. bleed, on the plan
    bleed_frames = []
    for n in sorted(plans):
        p = plans[n]
        p["area"] = (p["rect"][2] * p["rect"][3]) / (W * H)
        if p["area"] < ROTATION["min_primary_area"]:
            problems.append(f"slide {n}: the primary image rect {list(p['rect'])} is "
                            f"{p['area']:.3f} of the frame. At least "
                            f"{ROTATION['min_primary_area']:.2f}, or the image is the small "
                            f"drawing under the headline that twenty one decks already made")
        if p["touched"]:
            bleed_frames.append(n)
        for e in sorted(p["declared"] - p["touched"]):
            problems.append(f"slide {n}: `bleeds` declares {e} and the rect {list(p['rect'])} "
                            f"does not reach that edge. A bleed the plan claims and the frame "
                            f"does not have is a critic grading against the wrong plan")
        for e in sorted(p["touched"] - p["declared"]):
            warnings.append(f"slide {n}: the rect reaches the {e} edge and `bleeds` does not "
                            f"say so")
    if plans and len(bleed_frames) < ROTATION["min_bleed_frames"]:
        problems.append(f"{len(bleed_frames)} frame(s) bleed ({', '.join(map(str, bleed_frames)) or 'none'}). "
                        f"At least {ROTATION['min_bleed_frames']}, because an image held inside "
                        f"the margins on every frame is a drawing in a slot rather than a page")

    # 6, the declared half. One accent, never the flag red.
    hexes = sorted({p["accent"] for p in plans.values() if p["accent"]})
    deck_accent = None
    if len(hexes) > 1:
        problems.append(f"the dossiers name {len(hexes)} accents ({', '.join(hexes)}). A deck "
                        f"has ONE")
    elif hexes:
        deck_accent = hexes[0]
        if deck_accent == FLAG_RED:
            problems.append(f"the accent is {FLAG_RED}, the flag red config/brand.yaml reserves "
                            f"for urgent signals. It is never a deck's accent")
            deck_accent = None
    elif plans:
        problems.append("no dossier names an accent hex, every one says none. A deck has one "
                        "accent and it is present on at least "
                        f"{ACCENT_MIN_FRAMES} frames")

    # the pixels
    pngs = find_renders(run_dir)
    if not pngs:
        return 2, [f"no rendered slides under {run_dir} (render/slide-*.png or slide-*.webp)"] + problems, []
    rep = find_report(run_dir)
    if not rep:
        return 2, [f"no render_report.json under {run_dir}, and the text boxes it carries are "
                   f"what keeps a headline from counting as image detail"] + problems, []
    try:
        boxes = text_boxes(json.loads(rep.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValueError, AttributeError) as exc:
        return 2, [f"{rep} could not be read: {exc}"] + problems, []

    frames = {_slide_no(p.name) or i: p for i, p in enumerate(pngs, start=1)}
    for n in sorted(set(plans) - set(frames)):
        problems.append(f"slide {n} declares a layout and no frame slide-{n:02d} was rendered")
    for n in sorted(set(frames) - set(declared)):
        problems.append(f"frame {frames[n].name} was rendered and no dossier declares its layout")

    rows: list[dict] = []
    present, over = [], []
    for n in sorted(plans):
        p = plans[n]
        if n not in frames:
            continue
        img = load_frame(frames[n])
        tb = boxes.get(n, [])
        # A DOCUMENT's type is its image, so its text cells count as detail rather than being
        # dropped. Every other archetype is measured on what is left once the type is gone.
        is_doc = p["layout"] == "DOCUMENT"
        detail, kept, dropped = detail_fraction(img, p["rect"], tb, count_text=is_doc)
        cover, one, pieces = silhouette(img, p["rect"], [] if is_doc else tb)
        acc = accent_coverage(img, deck_accent) if deck_accent else None
        row = {"frame": n, "name": frames[n].name, "layout": p["layout"], "area": p["area"],
               "touched": p["touched"], "declared": p["declared"], "detail": detail,
               "cells": kept, "text_cells": dropped, "sil_cover": cover, "sil_one": one,
               "pieces": pieces, "accent": acc}
        rows.append(row)
        # 4
        if kept == 0:
            problems.append(f"slide {n}: the rect {list(p['rect'])} has no 8 px cell that is not "
                            f"under type, so there is no room in it for an image at all")
        elif detail < DETAIL_SHARE:
            problems.append(f"slide {n}: {detail:.2f} of the {kept} cells inside the primary "
                            f"image rect carry any detail (luminance std over {DETAIL_STD:.0f}), "
                            f"under the {DETAIL_SHARE:.2f} line. The plan says {p['subject']!r} "
                            f"is drawn there and the pixels say a flat plate is")
        # 5. A GRID is a count, so it is held to coming apart rather than to holding together.
        if cover < SIL_COVER:
            problems.append(f"slide {n}: at thumb scale the subject covers {cover:.3f} of the "
                            f"rect against the frame's own ground, under {SIL_COVER:.2f}. Whatever "
                            f"is drawn there disappears in the feed")
        elif p["layout"] == "GRID":
            if pieces < GRID_PIECES:
                problems.append(f"slide {n}: at thumb scale the subject comes apart into {pieces} "
                                f"piece(s) of {PIECE_MIN:.0%} or more, under {GRID_PIECES}. A GRID "
                                f"is a count, and units a reader can't separate in the feed are "
                                f"not countable")
        elif one < SIL_ONE:
            problems.append(f"slide {n}: at thumb scale the largest piece of the subject holds "
                            f"{one:.2f} of it, under {SIL_ONE:.2f}. That is dust rather than one "
                            f"readable silhouette")
        # 6, the measured half
        if acc is not None:
            if acc >= ACCENT_PRESENT:
                present.append(n)
            if acc > ACCENT_CAP:
                over.append((n, acc))
            if p["accent"] and acc < ACCENT_PRESENT:
                warnings.append(f"slide {n}: the dossier says this frame uses the accent and "
                                f"{acc:.4f} of it is that colour")
    if deck_accent and rows:
        if len(present) < ACCENT_MIN_FRAMES:
            problems.append(f"the accent {deck_accent} is present on {len(present)} frame(s) "
                            f"({', '.join(map(str, present)) or 'none'}), under "
                            f"{ACCENT_MIN_FRAMES}. One accent, used, is what makes a deck read as "
                            f"one deck")
        if len(present) > ACCENT_MAX_FRAMES:
            problems.append(f"the accent {deck_accent} is present on {len(present)} frames "
                            f"({', '.join(map(str, present))}), over {ACCENT_MAX_FRAMES}. An "
                            f"accent on every frame is a second ink rather than an accent")
        for n, a in over:
            problems.append(f"slide {n}: the accent {deck_accent} covers {a:.3f} of the frame, "
                            f"over the {ACCENT_CAP:.2f} cap. Restraint is what makes it an accent")
    rows.extend({"note": "warning: " + w} for w in warnings)
    return (1 if problems else 0), problems, rows


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    """Synthetic frames drawn with numpy, one direction and the other on every measurement."""
    import tempfile
    import numpy as np
    import yaml
    from PIL import Image

    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + str(extra)[:300]}")
        if not cond:
            fails += 1

    # (h) THE TWO COPIES OF THE TABLE. The JS file is the browser's, this file's is the gate's,
    # and this is the only thing that stops them drifting.
    probs = agreement()
    ok(f"the Python tables agree with {JS_TABLE.relative_to(REPO_ROOT)}", probs == [], probs)
    ok("a mutated ROTATION is CAUGHT",
       agreement(rotation=dict(ROTATION, min_distinct=ROTATION["min_distinct"] - 1)))
    ok("a mutated ARCHETYPES list is CAUGHT", agreement(archetypes=ARCHETYPES[:-1]))
    ok("a missing JS file is a fail rather than a skip",
       agreement(js_path=REPO_ROOT / "assets" / "js" / "no-such-file.js"))

    ACC = "#D8731F"
    GROUND, INK = (28, 36, 48), (150, 140, 120)
    PLAN = [
        ("FULL_BLEED", [0, 0, 1080, 1350], ["top", "left", "right", "bottom"]),
        ("OBJECT_AND_CAPTION", [80, 150, 920, 800], []),
        ("DIAGRAM", [0, 300, 1080, 700], ["left", "right"]),
        ("CLOSE_CROP", [0, 0, 1080, 860], ["top", "left", "right"]),
        ("GRID", [80, 200, 920, 700], []),
        ("SPLIT_HORIZON", [0, 567, 1080, 783], ["left", "right", "bottom"]),
        ("MAP", [100, 100, 880, 900], []),
        ("TYPE_AS_OBJECT", [0, 0, 1080, 700], ["top", "left", "right"]),
        ("FIGURE_SCALE", [80, 300, 920, 1050], ["bottom"]),
    ]
    TEXT = [(80, 96, 500, 30), (80, 1180, 700, 60)]     # a kicker and a caption line
    ACCENT_ON = (1, 3, 5, 7)

    PAGE = (100, 400, 880, 800)   # a page of type, for the DOCUMENT case

    def render(d: Path, flat=(), accent_on=ACCENT_ON, accent_hex=ACC, big=(), scale=1, doc=(),
               units=()):
        """Nine frames plus the render report, in the shape render.py writes. `doc` frames
        carry one page-sized text box instead of a subject; `units` frames carry their subject
        as twelve separate blobs, the way a GRID does."""
        rng = np.random.default_rng(7)
        (d / "render").mkdir(parents=True, exist_ok=True)
        slides = []
        for i, (layout, rect, _b) in enumerate(PLAN, start=1):
            a = np.empty((H, W, 3), np.uint8)
            a[:] = GROUND
            x, y, w, h = rect
            text = list(TEXT)
            if i in doc:
                text.append(PAGE)
            elif i in units or layout == "GRID":
                # twelve units on a 4 by 3 grid, each a textured block with ground between
                for r in range(3):
                    for c in range(4):
                        ux0, uy0 = x + int(w * (0.08 + c * 0.22)), y + int(h * (0.12 + r * 0.24))
                        ux1, uy1 = ux0 + int(w * 0.14), uy0 + int(h * 0.16)
                        blob = np.full((uy1 - uy0, ux1 - ux0, 3), INK, float)
                        blob += rng.integers(-45, 46, size=(uy1 - uy0, ux1 - ux0, 1))
                        a[uy0:uy1, ux0:ux1] = np.clip(blob, 0, 255).astype(np.uint8)
            else:
                # one subject, about 44 percent of its rect, textured unless the frame is a plate
                bx0, by0 = x + int(w * 0.1), y + int(h * 0.15)
                bx1, by1 = x + int(w * 0.9), y + int(h * 0.70)
                blob = np.full((by1 - by0, bx1 - bx0, 3), INK, float)
                if i not in flat:
                    blob += rng.integers(-45, 46, size=(by1 - by0, bx1 - bx0, 1))
                a[by0:by1, bx0:bx1] = np.clip(blob, 0, 255).astype(np.uint8)
            # type, as light glyph noise inside the text boxes
            for tx, ty, tw, th in text:
                a[ty:ty + th, tx:tx + tw] = np.clip(
                    220 + rng.integers(-30, 31, size=(th, tw, 1)), 0, 255).astype(np.uint8)
            if i in accent_on:
                size = 400 if i in big else 100
                a[40:40 + size, W - 40 - size:W - 40] = hex_rgb(accent_hex)
            img = Image.fromarray(a)
            if scale != 1:
                img = img.resize((W * scale, H * scale), Image.NEAREST)
            img.save(d / "render" / f"slide-{i:02d}.png", compress_level=0)
            slides.append({"file": f"slide-{i:02d}.html", "png": f"slide-{i:02d}.png", "ok": True,
                           "text_nodes": [{"text": f"text {k}", "x": tx, "y": ty, "w": tw, "h": th,
                                           "font_px": 24, "lines": [[tx, ty, tw, th]], "anc": []}
                                          for k, (tx, ty, tw, th) in enumerate(text)]})
        (d / "render" / "render_report.json").write_text(json.dumps(
            {"canvas": {"width": W, "height": H, "scale": scale}, "text_window": 320,
             "slides": slides}))

    def board(d: Path, layouts=None, rects=None, bleeds=None, accent_on=ACCENT_ON,
              accent_hex=ACC, drop=()):
        parts = ["# Storyboard\n\nProse around the plan.\n"]
        for i, (layout, rect, bl) in enumerate(PLAN, start=1):
            blk = {"slide": i, "job": f"job {i}",
                   "layout": (layouts or {}).get(i, layout),
                   "primary_image": {"subject": f"subject {i}",
                                     "rect": (rects or {}).get(i, rect),
                                     "bleeds": (bleeds or {}).get(i, bl)},
                   "accent": accent_hex if i in accent_on else "none"}
            if i in drop:
                for k in ("layout", "primary_image", "accent"):
                    blk.pop(k)
            parts.append("```yaml\n" + yaml.safe_dump(blk, sort_keys=False) + "```\n")
        (d / "storyboard.md").write_text("\n".join(parts))

    # Scratch stays inside the tree. out/ is gitignored, and a sandboxed write outside the
    # working tree is the prompt an unattended run has nobody to answer.
    scratch = REPO_ROOT / "out" / "layout_check"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as td:
        root = Path(td)
        d = root / "clean"
        render(d)

        # (a) a clean deck
        board(d)
        code, probs, rows = check(d)
        ok("a clean deck passes", code == 0 and not probs, probs)
        meas = [r for r in rows if "frame" in r]
        ok("...and every frame was measured", len(meas) == 9, len(meas))
        ok("...with the textured subject reading as detail on every frame",
           all(r["detail"] >= DETAIL_SHARE for r in meas), [round(r["detail"], 2) for r in meas])
        ok("...and as one silhouette, on every frame that is not a count",
           all(r["sil_one"] >= SIL_ONE for r in meas if r["layout"] != "GRID"),
           [round(r["sil_one"], 2) for r in meas])
        code, probs, rows = check(d, require=True)
        ok("...and passes with --require too", code == 0, probs)

        # the real renders are 2x, and the rect is in frame px whatever the scale
        d2 = root / "twox"
        render(d2, scale=2)
        board(d2)
        code, probs, rows = check(d2)
        ok("a deck rendered at 2x measures the same", code == 0 and not probs, probs)

        # (b) a consecutive repeat
        board(d, layouts={2: "DIAGRAM"})
        code, probs, _ = check(d)
        ok("a consecutive repeat FAILS and names the frames",
           code == 1 and any("frames 2 and 3 repeat DIAGRAM" in p for p in probs), probs)

        # the rest of the rotation rule, three breaches on one plan and each named
        board(d, layouts={2: "POSTER", 4: "MAP", 5: "TYPE_AS_OBJECT"})
        code, probs, _ = check(d)
        ok("a name off the list FAILS", any("not an archetype" in p for p in probs), probs)
        ok("TYPE_AS_OBJECT twice FAILS", any("TYPE_AS_OBJECT 2 times" in p for p in probs), probs)
        ok("one inside frame on a nine frame deck FAILS",
           any("FULL_BLEED and CLOSE_CROP 1 between them" in p for p in probs), probs)
        board(d, layouts={2: "DIAGRAM", 4: "CLOSE_CROP", 5: "DIAGRAM", 6: "FULL_BLEED",
                          7: "DIAGRAM", 8: "CLOSE_CROP", 9: "DIAGRAM"})
        code, probs, _ = check(d)
        ok("three distinct archetypes on nine frames FAILS",
           any("only 3 distinct" in p for p in probs), probs)

        # (c) a rect under the area line, (3) a declared bleed the rect misses, and the count.
        # Slides 3, 6 and 9 are pulled inside the margins, so only 1, 4 and 8 still bleed.
        board(d, rects={2: [80, 150, 400, 400], 3: [40, 300, 1000, 700],
                        6: [40, 567, 1000, 700], 9: [80, 300, 920, 1000]},
              bleeds={2: ["left"], 3: [], 6: [], 9: []})
        code, probs, _ = check(d)
        ok("a rect under 0.30 of the frame FAILS and says the area",
           code == 1 and any("slide 2" in p and "0.110 of the frame" in p for p in probs), probs)
        ok("a declared bleed the rect does not reach FAILS",
           any("declares left" in p for p in probs), probs)
        ok("three bleeding frames on a nine frame deck FAILS",
           any("3 frame(s) bleed (1, 4, 8)" in p for p in probs), probs)
        board(d, bleeds={1: []})
        code, probs, rows = check(d)
        ok("a touched edge left undeclared is a warning and not a fail",
           code == 0 and any("reaches the top edge" in r.get("note", "") for r in rows), probs)

        # (d) a flat plate where the plan says an image is
        df = root / "flat"
        render(df, flat=(1,))
        board(df)
        code, probs, rows = check(df)
        ok("a flat plate inside the rect FAILS on detail, naming the slide and the plan's subject",
           code == 1 and any("slide 1" in p and "flat plate" in p and "subject 1" in p for p in probs),
           probs)
        ok("...while every textured frame beside it passes",
           all(r["detail"] >= DETAIL_SHARE for r in rows if r.get("frame", 1) != 1),
           [(r.get("frame"), round(r.get("detail", 0), 2)) for r in rows if "frame" in r])
        img = load_frame(df / "render" / "slide-01.png")
        boxes = text_boxes(json.loads((df / "render" / "render_report.json").read_text()))[1]
        with_text, kept, dropped = detail_fraction(img, (0, 0, W, H), boxes)
        without, _, _ = detail_fraction(img, (0, 0, W, H), [])
        ok("the type on that frame was dropped rather than counted as image detail",
           dropped > 0 and without > with_text and with_text < DETAIL_SHARE,
           f"with {with_text:.3f} without {without:.3f} dropped {dropped}")

        # (d2) the two archetypes the table defines differently. A page of type is the image
        # on a DOCUMENT and a flat plate anywhere else. Twelve units are a count on a GRID and
        # dust anywhere else.
        dd = root / "doc"
        render(dd, doc=(2,))
        board(dd, layouts={2: "DOCUMENT"}, rects={2: [80, 380, 920, 840]})
        code, probs, rows = check(dd)
        ok("a page of type declared as a DOCUMENT passes, the type being the image",
           code == 0 and not probs, probs)
        board(dd, layouts={2: "OBJECT_AND_CAPTION"}, rects={2: [80, 380, 920, 840]})
        code, probs, rows = check(dd)
        ok("...and the same page declared as an OBJECT_AND_CAPTION FAILS as a flat plate",
           code == 1 and any("slide 2" in p and "flat plate" in p for p in probs), probs)
        code, probs, rows = check(d)
        five = [r for r in rows if r.get("frame") == 5][0]
        ok("the clean deck's GRID comes apart into countable pieces",
           five["pieces"] >= GRID_PIECES and five["sil_one"] < SIL_ONE,
           f"pieces {five['pieces']} largest {five['sil_one']:.2f}")
        board(d, layouts={5: "MAP"})
        code, probs, rows = check(d)
        ok("...and those same twelve pieces declared as a MAP FAIL as dust",
           code == 1 and any("slide 5" in p and "dust" in p for p in probs), probs)
        board(d)

        # (e) accent, both directions and the cap
        d8 = root / "accent8"
        render(d8, accent_on=tuple(range(1, 9)))
        board(d8, accent_on=tuple(range(1, 9)))
        code, probs, _ = check(d8)
        ok("the accent on 8 frames FAILS restraint",
           code == 1 and any("present on 8 frames" in p and "over 6" in p for p in probs), probs)
        d1 = root / "accent1"
        render(d1, accent_on=(1,))
        board(d1, accent_on=(1,))
        code, probs, _ = check(d1)
        ok("the accent on 1 frame FAILS presence",
           code == 1 and any("present on 1 frame(s)" in p and "under 3" in p for p in probs), probs)
        db = root / "big"
        render(db, big=(3,))
        board(db)
        code, probs, _ = check(db)
        ok("the accent over 8 percent of one frame FAILS the cap",
           code == 1 and any("slide 3" in p and "over the 0.08 cap" in p for p in probs), probs)
        board(d, accent_on=())
        code, probs, _ = check(d)
        ok("a deck where every dossier says none FAILS, a deck has one accent",
           any("every one says none" in p for p in probs), probs)

        # (i) the flag red
        dr = root / "red"
        render(dr, accent_hex=FLAG_RED)
        board(dr, accent_hex=FLAG_RED)
        code, probs, _ = check(dr)
        ok("the flag red as the accent FAILS",
           code == 1 and any("flag red" in p for p in probs), probs)

        # (f) half a deck in the system
        board(d, drop=(5,))
        code, probs, _ = check(d)
        ok("keys missing on one slide of nine FAILS, all or nothing",
           code == 1 and any("all or nothing" in p and "slide(s) 5 carry no" in p for p in probs),
           probs)
        code, probs, _ = check(d, require=True)
        ok("...with --require as well", code == 1)

        # (g) not in force at all
        board(d, drop=tuple(range(1, 10)))
        code, probs, rows = check(d)
        ok("no keys at all passes without --require, with the note",
           code == 0 and not probs and any(r.get("note") == NOT_IN_FORCE for r in rows), (probs, rows))
        code, probs, _ = check(d, require=True)
        ok("...and FAILS with --require, saying the run did not plan its layouts",
           code == 1 and any("did not plan its layouts" in p for p in probs), probs)

        # could not run, both artifacts
        board(d)
        for p in (d / "render").glob("slide-*.png"):
            p.unlink()
        code, probs, _ = check(d)
        ok("no renders is could-not-run, never a pass", code == 2, (code, probs))
        (d / "storyboard.md").unlink()
        code, probs, _ = check(d)
        ok("no storyboard is could-not-run", code == 2, (code, probs))

    # the colour maths, against values a reader can check by hand
    import numpy as np
    white, black = lab(np.array([255, 255, 255], float)), lab(np.array([0, 0, 0], float))
    ok("Lab of white is L 100 and of black is L 0",
       abs(white[0] - 100.0) < 0.01 and abs(black[0]) < 0.01 and abs(white[1]) < 0.01,
       (white, black))
    ok("the flag red and the accent are far apart in Lab",
       lab_distance(lab(np.array(hex_rgb(FLAG_RED), float)), lab(np.array(hex_rgb(ACC), float))) > 30)

    print("\nlayout_check self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


# --------------------------------------------------------------------------- cli
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], allow_abbrev=False)
    ap.add_argument("--run-dir")
    ap.add_argument("--date", help="maps to out/<date>")
    ap.add_argument("--require", action="store_true",
                    help="a deck with no layouts declared is a fail rather than a note")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.run_dir or a.date):
        print("layout_check: pass --run-dir, --date or --self-test", file=sys.stderr)
        return 2
    rd = Path(a.run_dir) if a.run_dir else REPO_ROOT / "out" / a.date
    if not rd.is_dir():
        print(f"layout_check: not a directory: {rd}", file=sys.stderr)
        return 2
    code, problems, rows = check(rd, require=a.require)
    for r in rows:
        if "frame" not in r:
            continue
        edges = "".join(e[0].upper() if e in r["touched"] else "." for e in EDGES)
        acc = f"accent {r['accent']:.4f}" if r["accent"] is not None else "accent none"
        print(f"  {r['frame']:02d}  {r['layout']:<19} area {r['area']:.3f}  bleeds {edges}  "
              f"detail {r['detail']:.2f} of {r['cells']} cells ({r['text_cells']} under type)  "
              f"silhouette {r['sil_cover']:.3f} one {r['sil_one']:.2f}  {acc}")
    for r in rows:
        if "note" in r:
            print(f"  {r['note']}")
    if code == 2:
        print("\nlayout_check: could not run. " + problems[0], file=sys.stderr)
        for p in problems[1:]:
            print(f"  {p}", file=sys.stderr)
        return 2
    if problems:
        print(f"\nlayout_check: {len(problems)} problem(s)\n")
        for p in problems:
            print(f"  {p}")
        return 1
    measured = sum(1 for r in rows if "frame" in r)
    if measured:
        print(f"\nlayout_check: {measured} frame(s) measured, the rotation holds, every rect "
              f"carries an image and the accent is used with restraint")
    return 0


if __name__ == "__main__":
    sys.exit(main())
