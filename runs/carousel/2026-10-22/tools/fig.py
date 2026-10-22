"""Writes figures.json into a frame as window.FIG, so the frame's code reads every figure by name
and no number is typed into a frame. Idempotent: the FIG line is replaced in place on every run."""
import json, re, sys
from pathlib import Path
FIGS = json.loads((Path(__file__).resolve().parents[2] / "figures.json").read_text())
LINE = '<script>window.FIG = ' + json.dumps({k: (v["value"] if isinstance(v, dict) else v) for k, v in FIGS.items() if not k.startswith("_")}, separators=(",", ":")) + ';</script>'
def fill(html: str) -> str:
    html = re.sub(r'<script>window\.FIG = .*?;</script>\n', '', html)
    anchor = '<script src="@@ASSETS@@/js/noise.js"></script>'
    return html.replace(anchor, LINE + '\n' + anchor, 1)
if __name__ == "__main__":
    for f in sys.argv[1:]:
        p = Path(f); p.write_text(fill(p.read_text())); print("FIG ->", f)
