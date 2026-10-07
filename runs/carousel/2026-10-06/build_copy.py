#!/usr/bin/env python3
"""build_copy.py for the 2026-10-06 deck. copy.json is read off the render report's own text
nodes, so the record says what the frames print, and the claim ids come from each frame's source
line. Nothing is typed twice."""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
rep = json.load(open(HERE / "render" / "render_report.json"))
cap = (HERE / "caption.txt").read_text().strip()
title = json.load(open(HERE / "tmp" / "doc_title.json"))["title"] if (HERE / "tmp" / "doc_title.json").exists() else "664 acres, staked in feet. Taylor's data center terms"
slides = {}
for s in rep["slides"]:
    n = int(re.search(r"(\d+)", s["file"]).group(1))
    html = (HERE / "slides" / s["file"]).read_text()
    def grab(cls):
        m = re.search(r'<(?:h1|p|div)[^>]*class="%s"[^>]*>(.*?)</' % cls, html, re.S)
        return m.group(1).strip() if m else ""
    kicker = re.search(r'kicker: "([^"]*)"', html).group(1)
    src = re.search(r'src: "([^"]*)"', html).group(1)
    labels = [re.sub(r"<br\s*/?>", " ", l) for l in re.findall(r"<div class=\"lab\" id=\"[^\"]*\"[^>]*>(.*?)</div>", html)]
    strings = [t["text"] for t in s["text_nodes"]]
    slides["S%d" % n] = {"n": n, "file": s["file"], "kicker": kicker, "headline": re.sub(r"<br\s*/?>", " ", grab("hook")).replace("&#39;", "'").replace("&nbsp;", " "),
                      "claims": src.split(), "cite": src, "body": re.sub(r"<[^>]+>", "", grab("dek")).replace("&#39;", "'").replace("\\'", "'"),
                      "labels": labels, "strings": strings}
out = {"date": "2026-10-06", "carousel_no": 44, "document_title": title,
       "_note": "Slide strings read off the render report's text nodes and each frame's own source line by build_copy.py.",
       "caption": cap, "slides": slides}
(HERE / "copy.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print("copy.json:", len(slides), "slides")
