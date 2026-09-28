"""Writes one slide's HTML shell around its own scene code. The shell is the house furniture every
frame shares (fonts, the chassis, the type block, the mount); the scene is the frame's own."""
import json, sys
from pathlib import Path

OUT = Path('/home/user/TexasAIDocket/out/2026-09-28/slides')

def write(n, comment, kicker, hook, dek, src, scene, hook_css="left:80px; top:150px; width:720px;",
          dek_css="width:660px;", fit=(88, 120, 3), extra_css="", extra_html="", body_attrs=""):
    html = f"""<!doctype html>
<!-- 2026-09-28, frame {n} of 9. {comment} -->
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1080px; height:1350px; overflow:hidden; background:#15171C; }}
  body {{ position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }}
  canvas#art {{ position:absolute; left:0; top:0; width:1080px; height:1350px; }}
  .hook {{ position:absolute; {hook_css} font-family:"Fraunces", serif; font-weight:800;
          line-height:0.95; letter-spacing:-0.008em; color:#F1ECE3; font-variation-settings:"opsz" 144; z-index:10; }}
  .dek  {{ position:absolute; left:82px; {dek_css} font-size:30px; line-height:1.4; color:#E2DBCF; z-index:10; }}
  .tx-site {{ position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace;
             font-size:24px; letter-spacing:0.07em; line-height:1.5; color:#C9BFAF; white-space:nowrap; z-index:20; }}
  .hook, .dek, .tx-site {{ text-shadow:0 0 6px rgba(12,12,14,0.8), 0 1px 16px rgba(12,12,14,0.55); }}
{extra_css}
</style>
</head>
<body{body_attrs}>
<canvas id="art" width="2160" height="2700"></canvas>
<div class="tx-site" id="site">texasaidocket.com</div>
<h1 class="hook" id="hook">{hook}</h1>
<p class="dek" data-follow="30">{dek}</p>
{extra_html}
<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txtype.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/deck/2026-09-28-watchtower.js"></script>
<script src="@@ASSETS@@/js/txlayout.js"></script>
<script type="module">
import * as THREE from '@@ASSETS@@/js/three.module.min.js';
import {{ init }} from '@@ASSETS@@/js/txthree.js';
import {{ initKit }} from '@@ASSETS@@/js/txkit.js';
window.renderReady = (async () => {{
  await document.fonts.ready;
  TXLAYOUT.mount(document.body, {{ kicker: {json.dumps(kicker)}, counter: "{n:02d} / 09", src: {json.dumps(src)}, ink: '#C9BFAF' }});
  TX.fitText(document.getElementById("hook"), {{ min: {fit[0]}, max: {fit[1]}, maxLines: {fit[2]} }});
  WATCH.follow();
  const TXT = init(THREE), K = initKit(THREE, TXT), F = WATCH, gl = F.glCanvas();
  F.installKit(K, THREE, TXT);
  const W = TXT.deckWorld();
{scene}
  return true;
}})();
</script>
</body>
</html>
"""
    (OUT / f"slide-{n:02d}.html").write_text(html)

def copy(n):
    c = json.load(open('/home/user/TexasAIDocket/out/2026-09-28/copy.json'))['slides'][f'S{n}']
    return c['kicker'], c['headline'], c['body'], c['cite']
