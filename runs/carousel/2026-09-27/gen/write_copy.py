"""copy.json built from render_report.json's own text nodes, the strings the browser laid out."""
import json, re
R = json.load(open('out/2026-09-27/render/render_report.json'))
caption = open('out/2026-09-27/caption.txt').read()
def expand(cite):
    out = []
    for a, b in re.findall(r'c(\d+)(?:\s+to\s+c(\d+))?', cite):
        out += [f"c{i}" for i in range(int(a), int(b or a) + 1)]
    return out
slides = {}
for s in sorted(R['slides'], key=lambda s: s['file']):
    n = int(re.search(r'(\d+)', s['file']).group(1))
    html = open(f"out/2026-09-27/slides/{s['file']}").read()
    kicker = re.search(r'kicker: "([^"]*)"', html).group(1)
    cite = re.search(r'src: "([^"]*)"', html).group(1)
    cite_n = re.sub(r'\s+', ' ', cite).strip()
    hook = re.search(r'<h1 class="hook" id="hook">(.*?)</h1>', html, re.S).group(1)
    hook = re.sub(r'<br>', ' ', re.sub(r'<(?!br)[^>]+>', '', hook)).replace('  ', ' ').strip()
    texts = [t['text'] for t in s['text_nodes']]
    body = next(t for t in texts if len(t) > 80 and t != hook)
    counter = f"{n:02d} / 09"
    labels = [t for t in texts if t not in ('texasaidocket.com', hook, body, kicker, counter, cite_n)
              and not any(t != u and t in u for u in texts)]
    slides[f"S{n}"] = {"n": n, "file": s['file'], "kicker": kicker, "headline": hook,
        "claims": expand(cite), "cite": cite_n, "body": body, "labels": labels, "strings": texts}
out = {"date": "2026-09-27", "carousel_no": 35, "document_title": "Pinnacle, RealPage and a rent recommended overnight",
       "_note": "Built from render_report.json's own text nodes rather than retyped, because the strings a reader receives are the ones the browser laid out. The screen on frame 2 and the page on frame 6 are drawn on canvases as bars, bands and ruled lines and carry no words.",
       "caption": caption, "slides": slides}
json.dump(out, open('out/2026-09-27/copy.json', 'w'), indent=1, ensure_ascii=False)
for k, v in slides.items(): print(k, v['headline'], '|', v['labels'])
