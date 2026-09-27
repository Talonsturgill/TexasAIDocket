"""Shell shared by the nine frames: the head, the type styles and the script tags. The scene
code in each frame is its own."""
HEAD = '''<!doctype html>
<!-- 2026-09-27, frame {n} of 9. Archetype {layout}. {note} -->
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1080px; height:1350px; overflow:hidden; background:#171310; }}
  body {{ position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }}
  canvas#art {{ position:absolute; left:0; top:0; width:1080px; height:1350px; }}
  .hook {{ position:absolute; left:80px; top:{hook_top}px; width:900px; font-family:"Fraunces", serif; font-weight:800;
          line-height:0.95; letter-spacing:-0.008em; color:#F3EEE6; font-variation-settings:"opsz" 144; z-index:10; }}
  .dek  {{ position:absolute; left:82px; width:{dek_w}px; font-size:30px; line-height:1.4; color:#F0EAE0; z-index:10; }}
  .tx-site {{ position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace;
             font-size:24px; letter-spacing:0.07em; line-height:1.5; color:#E2D8C8; white-space:nowrap; z-index:20; }}
  .lab {{ position:absolute; font-family:"JetBrains Mono", monospace; font-size:24px; line-height:1.25; color:#EDE4D6;
         letter-spacing:0.02em; white-space:nowrap; z-index:12; }}
  .hook, .dek, .tx-site, .lab {{ text-shadow:0 0 6px rgba(10,8,6,0.9), 0 1px 16px rgba(10,8,6,0.65); }}
  svg.lead {{ position:absolute; left:0; top:0; width:1080px; height:1350px; z-index:11; pointer-events:none; }}
{extra_css}
</style>
</head>
<body>
<canvas id="art" width="2160" height="2700"></canvas>
<div class="tx-site" id="site">texasaidocket.com</div>
<h1 class="hook" id="hook">{hook}</h1>
<p class="dek" data-follow="{follow}">{dek}</p>
{extra_html}
<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txtype.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/deck/2026-09-27-nightrent.js"></script>
<script src="@@ASSETS@@/js/txlayout.js"></script>
<script type="module">
import * as THREE from '@@ASSETS@@/js/three.module.min.js';
import {{ init }} from '@@ASSETS@@/js/txthree.js';
import {{ initKit }} from '@@ASSETS@@/js/txkit.js';
window.renderReady = (async () => {{
  await document.fonts.ready;
  TXLAYOUT.mount(document.body, {{ kicker: "{kicker}", counter: "{counter}", src: "{src}", ink: '#E2D8C8' }});
  TX.fitText(document.getElementById("hook"), {{ min: {hmin}, max: {hmax}, maxLines: {hlines} }});
  NIGHTRENT.follow();
  const TXT = init(THREE), K = initKit(THREE, TXT), F = NIGHTRENT, gl = F.glCanvas();
  F.installKit(K, THREE, TXT);
  const W = TXT.deckWorld();
{scene}
  TXT.weather(R, {{}});
  const cx = F.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx);
{after}
  return true;
}})();
</script>
</body>
</html>
'''
def page(n, layout, note, hook, dek, kicker, src, scene, after='', hook_top=150, dek_w=880, follow=30,
         extra_css='', extra_html='', hmin=90, hmax=128, hlines=2):
    return HEAD.format(n=n, layout=layout, note=note, hook=hook, dek=dek, kicker=kicker,
                       counter=f"{n:02d} / 09", src=src, scene=scene, after=after, hook_top=hook_top,
                       dek_w=dek_w, follow=follow, extra_css=extra_css, extra_html=extra_html,
                       hmin=hmin, hmax=hmax, hlines=hlines)
