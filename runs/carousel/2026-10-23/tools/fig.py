"""Writes figures.json into every slide's `window.FIG` line, so no frame carries a typed number."""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
fig = {k: v["value"] for k, v in json.loads((HERE / "figures.json").read_text()).items() if k not in ("_note", "pair")}   # pair backs the copy only, no frame draws it
line = "<script>window.FIG = " + json.dumps(fig) + ";</script>"
for p in sorted((HERE / "slides").glob("slide-*.html")):
    s = p.read_text()
    s2 = re.sub(r"<script>window\.FIG = .*?;</script>", line, s)
    if s2 != s: p.write_text(s2)
print("FIG written:", len(fig), "figures")
