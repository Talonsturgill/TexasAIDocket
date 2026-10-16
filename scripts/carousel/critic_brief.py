#!/usr/bin/env python3
"""Give visual reviewers the craft row, lower-third plan and current native crops.

Adapted from alaskaaicarousels scripts/critic_brief.py at
03da46445a18974351cc6e74835679b3de2c89c8 for the Texas YAML dossiers.
Read-only. Missing plans or stale crop sets exit 2, never list partial evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import dossier_check as dc
import native_crops


def brief(text: str, render_dir: Path, only=None):
    match = dc.CRAFT_PLAN_HEAD_RE.search(text)
    rows, showstopper = {}, None
    if match:
        block = re.split(r"^##\s", text[match.end():], maxsplit=1, flags=re.M)[0]
        for line in block.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and re.fullmatch(r"\d{1,2}", cells[0]):
                rows[int(cells[0])] = cells[1:3]
        selected = re.search(r"^\s*[-*]?\s*Showstopper frame:\s*(\d+)", block, re.M | re.I)
        if selected:
            showstopper = int(selected.group(1))
    dossiers = dc.parse_dossiers(text)
    blocks, problems = [], []
    for slide in only or sorted(dossiers):
        dossier = dossiers.get(slide, {})
        lower = dc.bottom_clause(dc.text_of(dc.dig(dossier, "composition.bands")))
        row = rows.get(slide, [])
        crops = native_crops.read(render_dir, slide)
        if not row or not lower:
            problems.append(f"slide {slide:02}: missing craft row or lower-third plan")
        if not crops.get("tiles"):
            problems.append(crops.get("stale") or crops.get("missing"))
        blocks.append({"slide": slide, "shot": row[0] if row else None,
                       "largest_object": row[1] if row else None, "lower_third": lower,
                       "showstopper": showstopper == slide, "native_crops": crops})
    if not blocks:
        problems.append("no slide dossiers found")
    return blocks, problems


def render_block(block):
    lines = [f"CRAFT LINES, slide {block['slide']:02}",
             f"  shot: {block['shot']}", f"  largest object and modelling: {block['largest_object']}",
             f"  lower third: {block['lower_third']}", f"  showstopper: {block['showstopper']}"]
    crops = block["native_crops"]
    if crops.get("tiles"):
        lines.append("  Native crops at 100 percent. Read every tile before judging surface artifacts.")
        for tile in crops["tiles"]:
            x0, y0, x1, y1 = tile["design"]
            lines.append(f"    design x {x0} to {x1}, y {y0} to {y1}: {tile['path']}")
    else:
        lines.append("  " + (crops.get("stale") or crops.get("missing")))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--render-dir")
    parser.add_argument("--slide", type=int, action="append", help="repeat to select several frames")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    base = Path(args.run_dir)
    storyboard = base / "storyboard.md"
    if not storyboard.exists():
        print(f"critic_brief: {storyboard} missing")
        return 2
    blocks, problems = brief(storyboard.read_text(), Path(args.render_dir) if args.render_dir else base / "render", args.slide)
    if args.json:
        print(json.dumps({"slides": blocks, "problems": problems}, indent=2))
    else:
        print("\n\n".join(render_block(block) for block in blocks))
        for problem in problems:
            print("[REPAIR] " + problem)
    return 2 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
