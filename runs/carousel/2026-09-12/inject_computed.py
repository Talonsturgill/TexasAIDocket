#!/usr/bin/env python3
"""inject_computed.py — write computed.json into every frame, so no frame can hold a stale number.

THE DEFECT THIS EXISTS FOR, from carousel no. 19's own `avoid_next`:

    slide-05.html drew its plot at 180 px per day while compute.py held 300, so every y coordinate
    computed.json published for that frame described a plot nobody drew. Both were hand-synced
    literals. The fix is to INJECT each slide's computed block into its frame rather than
    retyping it.

Carousel no. 20 adopted it and its round 2 integrity judge still found five literals typed past
the marker. So this script does two jobs, not one.

1. It replaces the marker with the real block.
2. **It then AUDITS the frame for literals the block already carries**, and exits non-zero naming
   each one. A value that is merely correct today is the same shape as one that has drifted, and
   the only way to tell them apart is to forbid both.

Run it after every edit to any frame, before render.py. It is idempotent.

    python3 out/<run>/inject_computed.py --slides-dir out/<run>/slides
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARK_OPEN = "/* @@COMPUTED@@ */"
MARK_CLOSE = "/* @@END COMPUTED@@ */"

# Values a frame must never retype. Each is (json key, how it would appear as a literal).
# Only values distinctive enough that a false positive is unlikely: a bare 3 or 9 appears in
# coordinates legitimately, so the audit covers the strings a WRITER would type, not every number.
def audit_terms(C: dict) -> list[tuple[str, str]]:
    """The strings a WRITER would retype, not every number in the file.

    A bare 70 or 9 appears in coordinates legitimately, so the audit covers values distinctive
    enough that a false positive is unlikely: dates spelled out, lane mile totals with their
    thousands separators, and the four F1 figures, which are the ones a repair round is most
    tempted to hand sync into a frame.
    """
    out = [
        ("commission_date", C["commission_date"]),
        ("agenda_posts_on", C["agenda_posts_on"]),
        ("item_date", C["item_date"]),
        ("run_date", C["run_date"]),
        ("lane_miles_university", C["lane_miles_university"]),
        ("lane_miles_fed_2024", C["lane_miles_fed_2024"]),
        ("lane_miles_fed_2023", C["lane_miles_fed_2023"]),
        ("f1_unet", C["f1_unet"]),
        ("f1_model", C["f1_model"]),
        ("f1_thin_unet", C["f1_thin_unet"]),
        ("f1_thin_model", C["f1_thin_model"]),
        ("map50_low", C["map50_low"]),
        ("map50_high", C["map50_high"]),
    ]
    return [(k, str(v)) for k, v in out if v]


def block(C: dict) -> str:
    return (f"{MARK_OPEN}\nconst C = {json.dumps(C, indent=2)};\n{MARK_CLOSE}")


def inject(path: Path, C: dict) -> tuple[bool, list[str]]:
    src = path.read_text(encoding="utf-8")
    if MARK_OPEN not in src:
        return False, [f"{path.name}: no {MARK_OPEN} marker, so it holds no computed block"]
    pat = re.compile(re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_CLOSE), re.S)
    if pat.search(src):
        new = pat.sub(lambda _: block(C), src)
    else:
        new = src.replace(MARK_OPEN, block(C), 1)
    if new != src:
        path.write_text(new, encoding="utf-8")

    # Audit the frame OUTSIDE the injected block for literals the block already carries.
    body = pat.sub("", new)
    problems = []
    for key, literal in audit_terms(C):
        if literal in body:
            problems.append(
                f"{path.name}: types the literal {literal!r}, which computed.json already holds "
                f"as C.{key}. Read it from C instead. A literal that is merely correct today "
                f"looks exactly like one that has drifted.")
    return True, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides-dir", default=str(HERE / "slides"))
    args = ap.parse_args()

    computed = HERE / "computed.json"
    if not computed.exists():
        print("inject_computed: computed.json is missing. Run compute.py first.", file=sys.stderr)
        return 2
    C = json.loads(computed.read_text(encoding="utf-8"))

    slides = sorted(Path(args.slides_dir).glob("slide-*.html"))
    if not slides:
        print(f"inject_computed: no slides in {args.slides_dir}", file=sys.stderr)
        return 2

    injected, problems = 0, []
    for p in slides:
        ok, probs = inject(p, C)
        injected += 1 if ok else 0
        problems.extend(probs)

    for msg in problems:
        print(f"  FAIL  {msg}", file=sys.stderr)
    print(f"inject_computed: {injected} of {len(slides)} frame(s) carry the computed block, "
          f"{len(problems)} literal(s) found outside it")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
