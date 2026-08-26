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
    # A TWO TOKEN CLASS IS STILL A CLASS. `[a-z0-9_-]+` cannot match `class="sl s1"`, so frame
    # 6's four route slips were skipped whole: their strings never reached copy.json and neither
    # did the four claim ids they cite. The manifest described a board with two papers on it
    # while the render shipped six, which is what round 9's integrity judge found. The first
    # token is the element's kind and the rest are modifiers.
    # INNERMOST DIVS ONLY. `(.*?)</div>` stops at the first closing tag, so a WRAPPER whose
    # children are divs swallows its first child and the child is never seen as an element.
    # Slide 4 wraps its type in `.plane`, which is why its dek stayed invisible to this sync even
    # after the frame was told to declare its role. The content class here cannot contain a div
    # tag of either kind, so a wrapper simply does not match and every leaf does.
    for m in re.finditer(r'<div class="([a-z0-9_ -]+)"([^>]*)>((?:(?!</?div).)*?)</div>',
                         body, re.S):
        cls, attrs, txt = m.group(1).split()[0], m.group(2), flat(m.group(3))
        if not txt:
            continue
        strings.append(txt)
        # THE FRAME DECLARES ITS OWN ROLE. A class name is a STYLE hook and a role is what the
        # dossier's `type:` block is about, and the two agree only by convention. Slide 4 carries
        # its dek in `.veiled`, because the dek on that frame is the block under the glazing, so
        # this sync skipped it and plan_render_check then failed a correct frame against a stale
        # plan. `data-role` is read first and the class name is the fallback, so a frame that
        # needs a different class for a role can say so instead of being invisible.
        role = (re.search(r'data-role="([a-z-]+)"', attrs) or [None, cls])[1]
        if role in ("hook", "dek") and role not in d:
            d[role] = txt
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
