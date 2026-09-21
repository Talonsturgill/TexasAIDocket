"""Build copy.json from the render report, never from the plan.

The strings a reader receives are the ones the browser laid out, so this reads
render_report.json's own text_nodes. Retyping it from the storyboard would make
copy_sync_check compare the plan against itself, which is the check's whole defect.
"""
import json, re
from pathlib import Path
run = Path('out/2026-09-21')
rep = json.loads((run/'render/render_report.json').read_text())
sb  = (run/'storyboard.md').read_text()

claims = {}
for m in re.finditer(r"^slide:\s*(\d+)\s*$(.*?)(?=^slide:\s*\d+\s*$|\Z)", sb, re.M | re.S):
    n = int(m.group(1))
    c = re.search(r"^claims:\s*\[([^\]]*)\]", m.group(2), re.M)
    claims[n] = [x.strip() for x in c.group(1).split(',') if x.strip()] if c else []

slides = {}
for s in sorted(rep['slides'], key=lambda s: s['file']):
    n = int(re.search(r'(\d+)', s['file']).group(1))
    nodes = s['text_nodes']
    mono = [t for t in nodes if t['family'] == 'JetBrains Mono']
    rest = [t for t in nodes if t['family'] != 'JetBrains Mono']
    disp = max(rest, key=lambda t: t['font_px'], default=None)
    # THE BODY IS ONE LAID OUT STRING AND NEVER A JOIN OF SEVERAL. Frame 7 sets three
    # voices at one measure, and concatenating them produced a string that reached no
    # frame, which copy_sync_check correctly refused. The largest setting is the body and
    # the others are carried in `strings`, where the check can still see every one.
    body = max((t for t in rest if t is not disp),
               key=lambda t: t['w'] * t['h'], default=None)
    kick = next((t for t in mono if t['y'] < 200 and t['x'] < 400), None)
    cite = next((t for t in mono if t['y'] > 1100 and t['x'] < 400), None)
    slides[f"S{n}"] = {
        "n": n, "file": s['file'],
        "kicker": kick['text'] if kick else "",
        "headline": disp['text'] if disp else "",
        "claims": claims.get(n, []),
        "cite": cite['text'] if cite else "",
        "body": body['text'] if body else "",
        "strings": [t['text'] for t in nodes],
    }

doc = {
    "date": "2026-09-21", "carousel_no": 31,
    "_note": ("Built from render_report.json's own text_nodes rather than retyped, because the "
              "strings a reader receives are the ones the browser laid out. What it cannot see "
              "is a string a drawing has painted over, which is a gap in the SUITE rather than "
              "something to answer by retyping this file from the plan and calling the "
              "disagreement a check. On this deck that gap is the canvas fillText on frames 4, "
              "5 and 6, which qa.py transcribes and warns about by name."),
    "slides": slides,
}
(run/'copy.json').write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print("copy.json:", len(slides), "slides")
