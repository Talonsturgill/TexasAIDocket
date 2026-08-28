#!/usr/bin/env python3
"""The check proposal 10 asks for, run here as evidence rather than shipped as a gate.

Pull every string the deck prints that is NOT a verbatim quote, find every document-structure
locator in it, and require each to appear in some claim's quote, text or source_title. Six
instances of this defect were found by judges across three passes, every one of them TRUE and
every one uncarried, which is why the gate has to ask a claim rather than ask a human to care.
"""
import json, re, sys, pathlib

RUN = pathlib.Path("out/2026-08-28")
copy = json.loads((RUN / "copy.json").read_text())
claims = json.loads((RUN / "claims.json").read_text())["claims"]

hay = "  ".join(
    " ".join(str(c.get(k) or "") for k in ("quote", "text", "source_title")) for c in claims
).casefold()
hay = re.sub(r"\s+", " ", hay)

LOCATOR = re.compile(
    r"\b(ordering paragraph|findings? of fact|conclusions? of law|condition|section|exhibit"
    r"|item|project|docket|control number|attachment|appendix|schedule|paragraph)\b"
    r"(\s+(?:no\.?\s*)?\d+)?", re.I)

bad, checked = [], 0
for key, sl in sorted(copy["slides"].items()):
    strings = [sl.get("hook", ""), sl.get("dek", "")] + list(sl.get("labels") or [])
    for s in strings:
        if not s or s.strip().startswith('"'):   # a verbatim quote is exempt, as the house law says
            continue
        for m in LOCATOR.finditer(s):
            tok = re.sub(r"\s+", " ", m.group(0)).strip().casefold()
            checked += 1
            if tok in hay:
                continue
            head = m.group(1).casefold()
            if not m.group(2) and head in hay:    # a bare locator word, no number to carry
                continue
            bad.append((key, s.strip(), m.group(0)))

for k, s, t in bad:
    print(f"  {k}: {t!r} is printed on the frame and appears in no claim field")
    print(f"      in: {s[:90]}")
print(f"\nlocator sweep: {checked} locator token(s) across 9 slides, {len(bad)} untraced")
sys.exit(1 if bad else 0)
