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
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
SNAP = RUN / "tmp" / "fda_ai_devices.html"
OUT = RUN / "fda_words.json"
URL = ("https://www.fda.gov/medical-devices/software-medical-device-samd/"
       "artificial-intelligence-enabled-medical-devices")
WORDS = ("child", "children", "adult", "pediatric", "paediatric")


def page_text() -> str:
    raw = SNAP.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", body)))


def main() -> int:
    """Measure the snapshot if it is here, and otherwise SAY the result is the committed one.

    THE SNAPSHOT DIES WITH THE CONTAINER AND THE RESULT MUST NOT. It is fetched into
    `out/<date>/tmp/`, which `CLAUDE.md` requires and `.gitignore` excludes, so the committed
    copy of this script beside the deck had nothing to read and raised FileNotFoundError on the
    one figure frame 9 and two of this run's absences rest on. A measurement whose input is gone
    and whose output was only ever printed to a terminal is a measurement nobody can check,
    which is the same fault as a typed numeral wearing a script's clothes.

    So the result is written to `fda_words.json` beside this file and committed. Re-fetching the
    URL is how a later reader re-derives it, and the page is mutable, so the committed figure is
    dated and says which bytes it was taken from rather than claiming to be today's.
    """
    if not SNAP.exists():
        if OUT.exists():
            print(OUT.read_text(encoding="utf-8"), end="")
            print(f"fda_words: {SNAP} is gone, so the figures above are the committed measurement "
                  f"of the bytes it names. Re-fetch {URL} to take a fresh one", file=sys.stderr)
            return 0
        print(f"fda_words: no snapshot at {SNAP} and no committed {OUT.name}. Fetch {URL} into "
              f"{SNAP} and run this again", file=sys.stderr)
        return 1
    text = page_text()
    counts = {w: len(re.findall(r"\b" + w + r"\b", text, re.I)) for w in WORDS}
    where = [text[max(0, m.start() - 60):m.start() + 60].strip()
             for m in re.finditer(r"\bpediatric\b", text, re.I)]
    out = {"url": URL,
           "measured_on": RUN.name,
           "snapshot": str(SNAP.relative_to(RUN.parent.parent)),
           "bytes": SNAP.stat().st_size,
           "prose_chars": len(text),
           "counts": counts,
           "pediatric_in_context": where}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
