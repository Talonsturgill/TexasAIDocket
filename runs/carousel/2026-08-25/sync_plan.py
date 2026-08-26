#!/usr/bin/env python3
"""Rebuild copy.json from the slides, then sync each dossier's declared display strings to them.

plan_render_check exists because a build refused and a stale render shipped to three judges.
It compares the dossier's `type:` block to the frame, so after a recut the dossier is the thing
that has to move. This reads the frames and writes both, so the plan and the render cannot
disagree by hand-editing one of them.
"""
import json, pathlib, re, html
ROOT = pathlib.Path(__file__).resolve().parents[3]
S = ROOT / "out/2026-08-25/slides"
TAG = re.compile(r"<[^>]+>")
def flat(inner):
    return html.unescape(re.sub(r"\s+", " ", TAG.sub(" ", inner.replace("<br>", " ")))).strip()

# ---- copy.json --------------------------------------------------------------------------
cp = ROOT / "out/2026-08-25/copy.json"; C = json.loads(cp.read_text())
display = {}
for n in range(1, 10):
    s = (S / f"slide-{n:02d}.html").read_text()
    body = s[s.index("<body>"):s.index("<script")]
    strings, d = [], {}
    for m in re.finditer(r'<div class="([a-z0-9_-]+)"[^>]*>(.*?)</div>', body, re.S):
        cls, txt = m.group(1), flat(m.group(2))
        if not txt:
            continue
        strings.append(txt)
        if cls in ("hook", "dek") and cls not in d:
            d[cls] = txt
    key = f"S{n}"
    C["slides"][key]["strings"] = strings
    C["slides"][key]["claims"] = sorted({"c" + i for i in re.findall(r"\bC(\d+)\b", " ".join(strings))},
                                        key=lambda c: int(c[1:]))
    display[n] = d
cp.write_text(json.dumps(C, indent=1, ensure_ascii=False) + "\n")

# ---- storyboard dossiers ------------------------------------------------------------------
sp = ROOT / "out/2026-08-25/storyboard.md"; s = sp.read_text()
changed = 0
for n, d in display.items():
    blocks = list(re.finditer(rf"^slide: {n}$(.*?)^```$", s, re.S | re.M))
    if not blocks:
        continue
    blk = blocks[0]; body = blk.group(1); new = body
    for field, val in d.items():
        esc = val.replace("\\", "\\\\").replace('"', '\\"')
        new2, k = re.subn(rf'^(  {field}: ").*?("\s*)$', lambda m: m.group(1) + esc + m.group(2),
                          new, count=1, flags=re.M)
        if k:
            new = new2; changed += 1
    s = s[:blk.start(1)] + new + s[blk.end(1):]
sp.write_text(s)
print(f"copy.json rebuilt from 9 frames; {changed} dossier display string(s) synced")
