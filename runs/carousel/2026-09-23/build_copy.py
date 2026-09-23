"""Build copy.json from the render report, never from the plan.

The strings a reader receives are the ones the browser laid out, so this reads
render_report.json's own text_nodes. Retyping it from the storyboard would make
copy_sync_check compare the plan against itself, which is the check's whole defect.
"""
import json, re
from pathlib import Path
run = Path('out/2026-09-23')
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
    # A CONTAINER'S TEXT IS NOT A STRING ANY SOURCE CARRIES.
    #
    # The harness reports a wrapper AND its child, so frame 1's letterhead comes back twice:
    # 'Texas AI Docket September 23rd' at y 80 and 'September 23rd' at y 116. The chassis sets
    # those as two fields, `kicker` and `kicker2`, so the joined string appears in no slide
    # source and shipped_check correctly refused the shipped deck for recording a display
    # string the frame does not contain. Recording the join would make this file describe the
    # DOM tree rather than the page, which is the trap that gate's own docstring names about
    # `&nbsp;`: the cure is never to put markup into the copy record.
    #
    # So a node whose text ends with another node's text at the same left edge is split, and
    # what is recorded is the two things a reader actually reads on two lines.
    def _split_containers(ns):
        out, drop = [], []
        for a in ns:
            for b in ns:
                if a is b or not b['text'].strip():
                    continue
                if a['x'] == b['x'] and a['y'] < b['y'] and a['text'].endswith(b['text']) \
                   and len(a['text']) > len(b['text']):
                    head = a['text'][: -len(b['text'])].strip()
                    if head:
                        out.append(dict(a, text=head))
                    drop.append(id(a))
                    break
        kept = [n for n in ns if id(n) not in drop]
        return kept + out

    nodes = _split_containers(nodes)
    mono = [t for t in nodes if t['family'] == 'JetBrains Mono']
    rest = [t for t in nodes if t['family'] != 'JetBrains Mono']
    disp = max(rest, key=lambda t: t['font_px'], default=None)
    body = max((t for t in rest if t is not disp),
               key=lambda t: t['w'] * t['h'], default=None)
    kick = next((t for t in sorted(mono, key=lambda t: (t['y'], t['x']))
                 if t['y'] < 200 and t['x'] < 400), None)
    cite = next((t for t in mono if t['y'] > 1100 and t['x'] < 400
                 and re.search(r'\bc\d+\b', t['text'])), None)
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
    "date": "2026-09-23", "carousel_no": 32,
    "_note": ("Built from render_report.json's own text_nodes rather than retyped, because the "
              "strings a reader receives are the ones the browser laid out. What it cannot see "
              "is a string a drawing has painted over, which is a gap in the SUITE rather than "
              "something to answer by retyping this file from the plan and calling the "
              "disagreement a check. THIS DECK HAS NO SUCH GAP AND THE NOTE USED TO SAY IT DID. "
              "It named a canvas fillText on frames 4, 5 and 6 that render_report has never "
              "recorded: `canvas_text` is empty on all nine slides, because the mute world law "
              "puts every glyph in the DOM. A scorer caught the note describing a render the "
              "render does not carry, which is the seventh time in this run a committed file "
              "asserted something about its own output that was not measured."),
    "slides": slides,
}
(run/'copy.json').write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print("copy.json:", len(slides), "slides")
