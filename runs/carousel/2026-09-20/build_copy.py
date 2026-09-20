#!/usr/bin/env python3
"""build_copy.py — copy.json and canvas_text.json, built from what the browser laid out.

WHY THIS IS A SCRIPT. Round 3 rebuilt these two files by hand four times as frames changed,
and the third rebuild silently dropped the `S<n>` keys for `slide-NN.html` ones. Nothing
caught it for two gates, because copy_sync_check normalises both shapes and numeral_trace
does not: it looks up `S<n>`, missed every block, and read every frame as citing NOTHING.
It then reported four numerals as untraceable that were traced the whole time.

That is the shape this repo keeps paying for. A file rebuilt by hand under time pressure
drifts, and the drift shows up as a gate failing for a reason that is not the real one.
So the rebuild is one command, it always emits the same shape, and the claim ids come from
the dossiers rather than from whatever the last edit remembered.
"""
import json, re, pathlib, sys

RUN = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out/2026-09-20")

rep = json.loads((RUN / "render" / "render_report.json").read_text())
sb = (RUN / "storyboard.md").read_text()
old = json.loads((RUN / "copy.json").read_text())

meta = {}
for blk in re.findall(r"```yaml\n(.*?)```", sb, re.S):
    m = re.search(r"^slide:\s*(\d+)", blk, re.M)
    if not m:
        continue
    n = int(m.group(1))
    cm = re.search(r"^claims:\s*\[(.*?)\]", blk, re.M)
    hk = re.search(r'^  hook:\s*"(.*)"\s*$', blk, re.M)
    dk = re.search(r'^  dek:\s*"(.*)"\s*$', blk, re.M)
    meta[n] = {"claims": [x.strip() for x in cm.group(1).split(",") if x.strip()] if cm else [],
               "headline": hk.group(1) if hk else "", "body": dk.group(1) if dk else ""}

copy = {"date": old["date"], "carousel_no": old["carousel_no"], "_note": old["_note"], "slides": {}}
canvas = {"date": old["date"],
          "_note": "Strings this deck PAINTS on the art canvas with fillText. They are kept out of "
                   "copy.json because copy_sync_check holds every string there to having been laid "
                   "out by the browser, which a canvas call never is. They are recorded so a reader "
                   "of the run still sees every word the deck shows, and so a future gate closing "
                   "the DOM versus canvas overlap gap has the list to work from.",
          "slides": {}}

for s in rep["slides"]:
    n = int(re.search(r"(\d+)", s["file"]).group(1))
    m = meta.get(n, {})
    nodes = [x["text"] if isinstance(x, dict) else x for x in (s.get("text_nodes") or [])]
    cite = next((t for t in nodes if "TEXAS AI DOCKET" in t), "")
    kick = next((t for t in nodes if t != cite and not re.match(r"^\d\d / \d\d$", t)
                 and t != "texasaidocket.com" and t != m.get("headline") and t != m.get("body")), "")
    copy["slides"][f"S{n}"] = {"n": n, "file": s["file"], "kicker": kick,
                               "headline": m.get("headline", ""), "claims": m.get("claims", []),
                               "cite": cite,
                               "body": m.get("body", ""), "strings": nodes}
    ct = [x["text"] if isinstance(x, dict) else x for x in (s.get("canvas_text") or [])]
    if ct:
        canvas["slides"][f"S{n}"] = ct

(RUN / "copy.json").write_text(json.dumps(copy, indent=1, ensure_ascii=False) + "\n")
(RUN / "canvas_text.json").write_text(json.dumps(canvas, indent=1, ensure_ascii=False) + "\n")
print(f"copy.json: {len(copy['slides'])} slide(s), keys S1..S{len(copy['slides'])}")
print(f"canvas_text.json: {len(canvas['slides'])} slide(s) paint on the canvas")
