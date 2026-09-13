#!/usr/bin/env python3
"""fda_words.py - the FDA device list page's own word counts, measured off the saved snapshot.

Frame 9 prints that the page says nothing about children, and two of this run's three absences
are scoped to that page. Round 3's integrity judge was right that it was the one source in the
deck nobody outside the run could check, and right again that the verbatim_basis attached to it,
the premarket requirements sentence, says nothing about children and so evidences nothing.

The snapshot is now on disk and this is what it measures. The finding is sharper than the first
absence claimed: child, children and adult do not appear on the page at all, and the only two
occurrences of pediatric are inside two device NAMES in the list rather than in the page's text.
"""
import html
import json
import re
from pathlib import Path

RUN = Path(__file__).resolve().parent
SNAP = RUN / "tmp" / "fda_ai_devices.html"
WORDS = ("child", "children", "adult", "pediatric", "paediatric")


def page_text() -> str:
    raw = SNAP.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", body)))


def main() -> int:
    text = page_text()
    counts = {w: len(re.findall(r"\b" + w + r"\b", text, re.I)) for w in WORDS}
    where = [text[max(0, m.start() - 60):m.start() + 60].strip()
             for m in re.finditer(r"\bpediatric\b", text, re.I)]
    print(json.dumps({"snapshot": str(SNAP.relative_to(RUN.parent.parent)),
                      "bytes": SNAP.stat().st_size,
                      "prose_chars": len(text),
                      "counts": counts,
                      "pediatric_in_context": where}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
