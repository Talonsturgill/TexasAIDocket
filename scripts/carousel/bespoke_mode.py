#!/usr/bin/env python3
"""bespoke_mode.py, is this a BESPOKE run (owner, 2026-11-14, knowledge/carousel/BESPOKE.md).

A run is bespoke when its date is on or after config/carousel/bespoke.json `bespoke_from`, or when
the chassis its slides load declares `bespoke: true`. The gates that pull frames together (the value
strobe cap, the archetype rotation) report and never block on a bespoke run, because a change of
world between two frames is the point there.

    python3 scripts/carousel/bespoke_mode.py --date 2026-11-20      prints true or false
    python3 scripts/carousel/bespoke_mode.py --dir out/2026-11-20   reads the chassis too
    python3 scripts/carousel/bespoke_mode.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "carousel" / "bespoke.json"
DATE = re.compile(r"(20\d\d-\d\d-\d\d)")
CHASSIS = re.compile(r"js/deck/([\w.-]+\.js)")
DECLARES = re.compile(r"TXDECK\.declare\(\{[^}]*?\bbespoke\s*:\s*true", re.S)


def bespoke_from() -> str | None:
    try:
        return json.loads(CONFIG.read_text()).get("bespoke_from")
    except (OSError, ValueError):
        return None


def by_date(date: str | None) -> bool:
    start = bespoke_from()
    return bool(start and date and date >= start)


def chassis_declares(d: Path) -> bool:
    """Any slide HTML in d, d/slides or ../slides loading a chassis that declares bespoke: true."""
    cands = [d, d / "slides", d.parent / "slides"]
    for c in cands:
        if not c.is_dir():
            continue
        for h in sorted(c.glob("slide-*.html")):
            m = CHASSIS.search(h.read_text(errors="ignore"))
            if not m:
                continue
            js = ROOT / "assets" / "js" / "deck" / m.group(1)
            if js.exists() and DECLARES.search(js.read_text(errors="ignore")):
                return True
            return False
    return False


def is_bespoke(date: str | None = None, d: Path | None = None) -> bool:
    if date is None and d is not None:
        m = DATE.search(str(d.resolve()))
        date = m.group(1) if m else None
    if by_date(date):
        return True
    return bool(d and chassis_declares(d))


def self_test() -> int:
    ok = True
    def chk(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name); ok = ok and cond
    chk("a run with no date and no chassis is not bespoke", not is_bespoke(None, None))
    chk("the look v2 proof (no bespoke declare) is not bespoke",
        not is_bespoke(None, ROOT / "examples" / "look-v2-proof" / "2026-11-14"))
    chk("the declare regex finds bespoke true", bool(DECLARES.search('TXDECK.declare({ world: "x", bespoke: true, light: {')))
    chk("the declare regex ignores a deck without it", not DECLARES.search('TXDECK.declare({ world: "x", look: "v2" })'))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date"); ap.add_argument("--dir", type=Path); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    print("true" if is_bespoke(a.date, a.dir) else "false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
