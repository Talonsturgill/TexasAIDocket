"""Writes a frame's HTML from its own pieces: the comment, the type, the labels and the frame's own script."""
import sys, json, html
from pathlib import Path
HEAD = '''<!doctype html>
<!-- 2026-10-22, frame {n} of 9. Archetype {layout}. {comment} -->
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
{style}</head>
<body>
<canvas id="art" width="2160" height="2700"></canvas>
<div class="tx-site" id="site" style="font-size:24px">texasaidocket.com</div>
<h1 class="hook" id="hook">{hook}</h1>
<p class="dek" data-follow="{follow}">{dek}</p>
{labels}<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txtype.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
{bench}<script src="@@ASSETS@@/js/deck/2026-10-22-stair.js"></script>
<script src="@@ASSETS@@/js/txlayout.js"></script>
{script}
</body>
</html>
'''
def esc(t):
    return html.escape(t, quote=False).replace("'", "&#39;").replace("Drawn to illustrate.", "Drawn&nbsp;to&nbsp;illustrate.")
spec = json.loads(Path(sys.argv[1]).read_text())
labels = "".join(f'<div class="lab" id="{i}">{esc(t)}</div>\n' for i, t in spec.get("labels", []))
out = HEAD.format(n=spec["n"], layout=spec["layout"], comment=spec["comment"], hook=esc(spec["hook"]), dek=esc(spec["dek"]),
                  follow=spec.get("follow", 24), labels=labels, script=Path(spec["script"]).read_text().rstrip(),
                  style=spec.get("style", ""), bench='<script src="@@ASSETS@@/js/txbench.js"></script>\n' if spec.get("bench") else "")
from fig import fill
Path(spec["out"]).write_text(fill(out))
print("wrote", spec["out"])
