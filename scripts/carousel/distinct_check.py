#!/usr/bin/env python3
"""distinct_check.py, the bespoke deck's difference gate (owner, 2026-11-14).

WHY THIS EXISTS.

    "I want every single slide to really be like custom. I don't want this in just some kind of
     template. I want like bespoke artwork on every single slide ... so that sure, they say they
     follow the same flow like for a post, but you can tell that it's custom artwork."

Every gate before this one pulled the frames together: one chassis, one world, one light, a value
track capped per step, a rubric whose 10 was "any frame unmistakably from this deck". The only gate
that pushed them apart, bespoke_check.py, read code tokens, so nine frames built from one twelve call
recipe with different arguments passed at 0.10 to 0.43 while looking like one slide nine times. This
gate reads the PIXELS and the TYPE as rendered.

WHAT IT MEASURES, off the rendered frames and render_report.json:

    image    each frame at 48 x 60 in OKLab: the correlation of its lightness structure with every
             other frame's, and the overlap of their colour histograms. Two frames whose combined
             similarity passes `max_pair_similarity` are near copies.
    adjacent the mean similarity of each frame to the next. A reader swipes, so adjacency is what
             reads as a template.
    type     the headline's rendered box (the largest type on the frame), placed in a 3 x 3 grid by
             its centre. At least `min_type_places` distinct cells across the deck, and never more
             than `max_type_same_run` frames in a row in one cell.

The thresholds are config/carousel/bespoke.json `distinct`. The tone, grade and type faces are meant
to repeat (they are the spine), which is why the colour term is weighted below the structure term.

EXIT CODES
    0  the frames differ enough to read as custom
    1  a violation, or the checker was called wrongly
    2  the checker itself broke

USAGE
    distinct_check.py --render-dir DIR        frames slide-NN.png and render_report.json in DIR
    distinct_check.py --run runs/carousel/D   a shipped run, frames slide-NN.webp
    distinct_check.py ... --json              the measurements as JSON
    distinct_check.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "carousel" / "bespoke.json"

DEFAULTS = {
    "max_pair_similarity": 0.86,
    "max_adjacent_mean": 0.45,
    "min_type_places": 4,
    "max_type_same_run": 2,
    "structure_weight": 0.65,
}


def thresholds() -> dict:
    t = dict(DEFAULTS)
    try:
        t.update(json.loads(CONFIG.read_text()).get("distinct", {}))
    except (OSError, ValueError):
        pass
    return t


def _srgb_to_oklab(rgb):
    import numpy as np
    c = rgb.astype("float64") / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    lms = np.cbrt(c @ M1.T)
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    return lms @ M2.T


def frame_features(path: Path):
    import numpy as np
    from PIL import Image
    im = Image.open(path).convert("RGB").resize((48, 60), Image.LANCZOS)
    lab = _srgb_to_oklab(np.asarray(im))
    L = lab[..., 0]
    s = L - L.mean()
    n = np.sqrt((s * s).sum()) or 1.0
    struct = (s / n).ravel()
    a = np.clip((lab[..., 1] + 0.25) / 0.5, 0, 0.9999)
    b = np.clip((lab[..., 2] + 0.25) / 0.5, 0, 0.9999)
    li = np.clip(L, 0, 0.9999)
    idx = (np.floor(li * 4) * 64 + np.floor(a * 8) * 8 + np.floor(b * 8)).astype(int).ravel()
    hist = np.bincount(idx, minlength=256).astype("float64")
    hist /= hist.sum()
    return struct, hist


def similarity(fa, fb, w: float) -> float:
    import numpy as np
    corr = float(np.dot(fa[0], fb[0]))           # -1 .. 1, structure
    inter = float(np.minimum(fa[1], fb[1]).sum())  # 0 .. 1, colour
    return w * max(corr, 0.0) + (1 - w) * inter


def hook_cell(text_nodes: list) -> tuple | None:
    """The headline is the largest type on the frame. Its rendered lines give the box."""
    nodes = [t for t in text_nodes if t.get("font_px") and t.get("text", "").strip()]
    if not nodes:
        return None
    big = max(nodes, key=lambda t: (t["font_px"], len(t["text"])))
    lines = big.get("lines") or [[big["x"], big["y"], big["w"], big["h"]]]
    x0 = min(l[0] for l in lines); y0 = min(l[1] for l in lines)
    x1 = max(l[0] + l[2] for l in lines); y1 = max(l[1] + l[3] for l in lines)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    col = min(2, int(cx / (1080 / 3))); row = min(2, int(cy / (1350 / 3)))
    return (row, col)


def load_deck(render_dir: Path | None, run: Path | None):
    d = render_dir or run
    rep_path = d / "render_report.json"
    report = json.loads(rep_path.read_text()) if rep_path.exists() else {"slides": []}
    by_file = {}
    for s in report.get("slides", []):
        m = re.search(r"slide-(\d+)", s.get("file", ""))
        if m:
            by_file[int(m.group(1))] = s
    frames = []
    ext = ("png",) if render_dir else ("webp", "png")
    for n in range(1, 21):
        p = None
        for e in ext:
            q = d / f"slide-{n:02d}.{e}"
            if q.exists():
                p = q
                break
        if p is None:
            continue
        frames.append((n, p, by_file.get(n, {}).get("text_nodes", [])))
    return frames


def judge(frames, t: dict) -> dict:
    feats = {n: frame_features(p) for n, p, _ in frames}
    nums = [n for n, _, _ in frames]
    w = t["structure_weight"]
    pairs = []
    for i, a in enumerate(nums):
        for b in nums[i + 1:]:
            pairs.append((a, b, round(similarity(feats[a], feats[b], w), 3)))
    adjacent = [s for a, b, s in pairs if b == a + 1]
    adj_mean = round(sum(adjacent) / len(adjacent), 3) if adjacent else 0.0
    cells = {n: hook_cell(tn) for n, _, tn in frames}
    places = len({c for c in cells.values() if c is not None})
    run, worst_run, prev = 0, 0, None
    for n in nums:
        c = cells[n]
        run = run + 1 if (c is not None and c == prev) else 1
        worst_run = max(worst_run, run)
        prev = c
    problems = []
    near = [(a, b, s) for a, b, s in pairs if s > t["max_pair_similarity"]]
    for a, b, s in near:
        problems.append(f"frames {a} and {b} are near copies as images (similarity {s} > {t['max_pair_similarity']})")
    if adj_mean > t["max_adjacent_mean"]:
        problems.append(f"each frame reads like the one before it (adjacent mean {adj_mean} > {t['max_adjacent_mean']})")
    if any(c is not None for c in cells.values()):
        if places < t["min_type_places"]:
            problems.append(f"the headline sits in only {places} place(s) across the deck; the rule is at least {t['min_type_places']}")
        if worst_run > t["max_type_same_run"]:
            problems.append(f"the headline sits in one place on {worst_run} frames in a row; the rule is at most {t['max_type_same_run']}")
    else:
        problems.append("no render_report.json text nodes, so the type placement was not measured")
    return {
        "frames": nums, "adjacent_mean": adj_mean,
        "max_pair": max((s for _, _, s in pairs), default=0.0),
        "pairs_over": near, "type_cells": {n: cells[n] for n in nums},
        "type_places": places, "type_same_run": worst_run, "problems": problems,
        "ok": not problems, "thresholds": t,
    }


def self_test() -> int:
    import tempfile
    import numpy as np
    from PIL import Image
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        print(("PASS " if cond else "FAIL ") + name)
        ok_all = ok_all and cond

    rng = np.random.default_rng(7)
    with tempfile.TemporaryDirectory() as td:
        same = Path(td) / "same"; diff = Path(td) / "diff"
        same.mkdir(); diff.mkdir()
        base = np.zeros((1350, 1080, 3), np.uint8)
        base[700:, :, :] = (40, 30, 60)
        base[900:1200, 300:800, :] = (220, 140, 90)
        slides_same, slides_diff = [], []
        for n in range(1, 10):
            img = base.copy()
            img[900:1200, 300 + n * 3:800, :] = (220, 140, 90)
            Image.fromarray(img).save(same / f"slide-{n:02d}.png")
            slides_same.append({"file": f"slide-{n:02d}.html", "text_nodes": [
                {"text": "Headline", "font_px": 90, "x": 80, "y": 150, "w": 900, "h": 200, "lines": [[80, 150, 800, 90]]}]})
            # different: a different composition and type place per frame
            img2 = np.full((1350, 1080, 3), [(30 * n) % 255, 120, (200 - 15 * n) % 255], np.uint8)
            y = int(rng.integers(0, 1000)); x = int(rng.integers(0, 700))
            img2[y:y + 350, x:x + 380, :] = (250 - 20 * n, 60 + 15 * n, 90)
            if n % 2:
                img2[:, : 200 + 50 * n, :] = (20, 20 + 20 * n, 80)
            else:
                img2[: 150 + 60 * n, :, :] = (240, 200 - 10 * n, 40 + 10 * n)
            Image.fromarray(img2).save(diff / f"slide-{n:02d}.png")
            places = [(80, 150), (600, 1000), (80, 900), (600, 150), (400, 550), (80, 550), (650, 600), (300, 1050), (80, 150)]
            px, py = places[n - 1]
            slides_diff.append({"file": f"slide-{n:02d}.html", "text_nodes": [
                {"text": "Headline", "font_px": 90, "x": px, "y": py, "w": 380, "h": 180, "lines": [[px, py, 360, 90]]}]})
        (same / "render_report.json").write_text(json.dumps({"slides": slides_same}))
        (diff / "render_report.json").write_text(json.dumps({"slides": slides_diff}))
        t = dict(DEFAULTS)
        rs = judge(load_deck(same, None), t)
        rd = judge(load_deck(diff, None), t)
        ok("nine near copies with the type in one place fail", not rs["ok"])
        ok("the near copies are named as pairs", len(rs["pairs_over"]) > 0)
        ok("one type place is named", any("only 1 place" in p for p in rs["problems"]))
        ok("nine different frames with the type moving pass", rd["ok"])
        ok("type places counted", rd["type_places"] >= 4)
    return 0 if ok_all else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--render-dir", type=Path)
    ap.add_argument("--run", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.self_test:
            return self_test()
        if not (a.render_dir or a.run):
            ap.error("give --render-dir or --run")
        frames = load_deck(a.render_dir, a.run)
        if len(frames) < 2:
            print("distinct_check: fewer than two frames found", file=sys.stderr)
            return 1
        r = judge(frames, thresholds())
    except SystemExit:
        raise
    except Exception as e:  # the gate itself broke
        print(f"distinct_check: broke: {e!r}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, indent=1, default=list))
    else:
        print(f"distinct: adjacent mean {r['adjacent_mean']}, max pair {r['max_pair']}, "
              f"type in {r['type_places']} place(s), longest same-place run {r['type_same_run']}")
        for p in r["problems"]:
            print("  FAIL " + p)
        print("distinct: OK" if r["ok"] else "distinct: FAIL")
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
