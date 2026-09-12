#!/usr/bin/env python3
"""build_copy.py — derive copy.json from the render report's own laid-out text nodes.

WHY IT IS DERIVED RATHER THAN AUTHORED. Phase 12 is where display text gets edited straight into
a frame's HTML, because answering a critic that way is faster than going back through copy.json.
The moment that happens the record disagrees with the deck, and the email, the ledger and the
archive page are all built from the record. A copy.json authored by hand drifts. A copy.json
rebuilt from `render_report.json` after every round cannot.

The instinct this pays, carried at 0.80 in `ledger/carousel/instincts.json`:

    Reconcile copy.json against the render report's own text nodes rather than trusting
    copy_sync_check, which compares skeletons with every non-alphanumeric stripped and so cannot
    see a missing space.

Run it after every render pass, before copy_sync_check.

    python3 out/<run>/build_copy.py --render-dir out/<run>/render
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

# A node is the hook, the dek, or furniture, decided by the role the frame declares on it.
# A frame says so with data-role="hook" | "dek"; everything else is a label.
ROLE_KEYS = ("hook", "dek")


def slide_no(name: str) -> int:
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else 0


def collect(report: dict) -> dict:
    """Classify each frame's laid-out nodes into hook, dek and labels BY MEASUREMENT.

    render_report.json carries no role field, so the classification is made from what the page
    actually laid out. The HOOK is the largest non-decorative type on the frame. The DEK is the
    longest remaining run of body-sized type. Everything else is furniture, kept in document
    order so the counter, the kicker and the source line stay where the frame put them.

    Decorative nodes are excluded because the frame declared them decorative, and a deck's
    honesty labels are never decorative. See SKILL.md on the 2026-08-26 exemption defect.
    """
    slides = {}
    for entry in report.get("slides", []):
        n = slide_no(entry.get("file") or entry.get("png") or "")
        if not n:
            continue
        nodes = [x for x in entry.get("text_nodes", []) if (x.get("text") or "").strip()]
        live = [x for x in nodes if not x.get("decorative")]
        hook_node = max(live, key=lambda x: x.get("font_px", 0), default=None)
        rest = [x for x in nodes if x is not hook_node]
        body = [x for x in rest if not x.get("decorative") and x.get("font_px", 0) >= 26]
        dek_node = max(body, key=lambda x: len((x.get("text") or "").split()), default=None)
        if dek_node is not None and len((dek_node.get("text") or "").split()) < 6:
            dek_node = None

        def clean(x):
            return re.sub(r"\s+", " ", (x.get("text") or "")).strip()

        hook = clean(hook_node) if hook_node is not None else ""
        dek = clean(dek_node) if dek_node is not None else ""
        labels, claims = [], []
        for x in nodes:
            if x is hook_node or x is dek_node:
                continue
            labels.append(clean(x))
        for x in nodes:
            for cid in re.findall(r"\bc\d{1,3}\b", clean(x)):
                if cid not in claims:
                    claims.append(cid)
        slides[f"S{n}"] = {"hook": hook, "dek": dek, "labels": labels,
                           "claims": sorted(claims, key=lambda c: int(c[1:]))}
    return dict(sorted(slides.items(), key=lambda kv: slide_no(kv[0])))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-dir", default=str(HERE / "render"))
    ap.add_argument("--out", default=str(HERE / "copy.json"))
    args = ap.parse_args()

    rp = Path(args.render_dir) / "render_report.json"
    if not rp.exists():
        print(f"build_copy: {rp} is missing. Run render.py first.")
        return 2
    report = json.loads(rp.read_text(encoding="utf-8"))
    slides = collect(report)
    # THE TITLE, BECAUSE WITHOUT IT THE ARTICLE PAGE IS CALLED AFTER ITS DIRECTORY.
    # `site_context.load_runs` reads `document_title` then `title` then falls back to the run
    # date, and this manifest carried neither, so the September 12th article shipped with
    # "2026-09-12" as its h1, its browser title, its Open Graph title, its breadcrumb and its
    # NewsArticle.headline. A code review caught it. The name is the story's, not the day's.
    doc = {
        "run": "2026-09-12",
        "deck": 22,
        "document_title": "Texas State University's AI pavement inspection method",
        "note": ("Derived from render_report.json's own laid-out text nodes by build_copy.py. "
                 "Never authored by hand, so it cannot drift from the frames. "
                 "Rebuilt every round."),
        "slides": slides,
    }
    Path(args.out).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    print(f"build_copy: wrote {args.out} from {len(slides)} frame(s)")
    for k, v in slides.items():
        print(f"  {k}: hook {len(v['hook'].split())}w, dek {len(v['dek'].split())}w, "
              f"{len(v['labels'])} label(s), claims {v['claims']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
