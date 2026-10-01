"""The shell every frame of the 2026-10-01 deck shares. The scene in each frame is its own."""
import json
from pathlib import Path

RUN = Path('/home/user/TexasAIDocket/out/2026-10-01')
FIG = json.load(open(RUN / 'figures.json'))


def figs(*keys):
    return 'const FIG = ' + json.dumps({k: FIG[k]['value'] for k in keys}) + ';\n'


def page(n, note, hook, dek, kicker, src, scene, hook_css='', dek_css='', extra_css='', extra_html='',
         fit='{ min: 96, max: 128, maxLines: 2 }', post='{ a: 0.32 }', drawn='{}', follow=30):
    dek_html = f'<p class="dek" data-follow="{follow}">{dek}</p>' if dek else ''
    own = ['  .tx-site { font-size:24px; }']   # the furniture size every frame shares, stated in each frame
    if hook_css: own.append('  .hook { ' + hook_css + ' }')
    if dek_css: own.append('  .dek { ' + dek_css + ' }')
    if extra_css: own.append(extra_css)
    style = ('<style>\n' + '\n'.join(own) + '\n</style>\n') if own else ''
    return f'''<!doctype html>
<!-- 2026-10-01, frame {n} of 9. {note} -->
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
{style}</head>
<body>
<canvas id="art" width="2160" height="2700"></canvas>
<div class="tx-site" id="site">texasaidocket.com</div>
<h1 class="hook" id="hook">{hook}</h1>
{dek_html}
{extra_html}
<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txtype.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/deck/2026-10-01-plates.js"></script>
<script src="@@ASSETS@@/js/txlayout.js"></script>
<script type="module">
import * as THREE from '@@ASSETS@@/js/three.module.min.js';
import {{ init }} from '@@ASSETS@@/js/txthree.js';
import {{ initKit }} from '@@ASSETS@@/js/txkit.js';
window.renderReady = (async () => {{
  const TXT = init(THREE);
  const {{ K, gl, W }} = await PL.boot(THREE, TXT, initKit, {{ kicker: {json.dumps(kicker)}, counter: "{n:02d} / 09", src: {json.dumps(src)}, fit: {fit} }});
{scene}
  PL.post(cx, {post});
  TXDECK.finish(cx);
  window.__txDrawn = {drawn};
  return true;
}})();
</script>
</body>
</html>
'''


def write(n, html):
    (RUN / 'slides').mkdir(exist_ok=True)
    (RUN / 'slides' / f'slide-{n:02d}.html').write_text(html)
