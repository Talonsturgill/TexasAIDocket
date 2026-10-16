"""Build three native HTML render studies from the frozen October 16th figures."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
figures = json.loads((ROOT / "runs/carousel/2026-10-16/figures.json").read_text())
units = figures["units_affected"]["value"]
days = figures["days_creek_to_open"]["value"]
cols = 72
rows = (units + cols - 1) // cols
studies = [
    (1, "THE NATIONAL RECALL", "Anyone can ride.<br>Read the recall too.",
     f"The federal recall covers {units:,} potentially affected systems. That is a national count, separate from San Antonio's service opening.",
     f'''const count = {units}, columns = {cols}, rows = {rows};
function object(X,Y) {{
  const x=(X-36)/14, y=(Y-615)/10, col=Math.floor(x), row=Math.floor(y);
  if (col<0 || col>=columns || row<0 || row>=rows || row*columns+col>=count) return [0,0];
  const edge=Math.min(x-col,1-(x-col),y-row,1-(y-row));
  return edge<0.10 ? [0,0] : [Math.min(6,(edge-0.1)*65),1];
}}
const height=(X,Y)=>object(X,Y)[0], material=(X,Y)=>object(X,Y)[1];''',
     "Every ceramic mark is one potentially affected system. Drawn from the archived federal count."),
    (3, "THE ELAPSED TIME", f"{days} days.<br>Two separate records.",
     "From the car in Salado Creek to the opening. Texas Public Radio reported that the cars resumed running without riders during that interval.",
     f'''const span = {days}, left=110, width=860, pitch=width/span;
function height(X,Y) {{
  if (X<left || X>left+width || Y<660 || Y>1110) return 0;
  const edge=Math.min(X-left,left+width-X,Y-660,1110-Y);
  let h=Math.min(15,edge*1.4);
  if (Y>680 && Y<765 && Math.abs(((X-left)/pitch)%1-0.5)<0.10) h-=5;
  if (Y>900 && Y<995) h-=9;
  return h;
}}
const material=(X,Y)=>height(X,Y)>0 ? ((Y>900 && Y<995)?3:2):0;''',
     "One cut per elapsed day. The span describes dates and does not describe a continuous shutdown."),
    (9, "THE REMEDY FIELD", '"The remedy is currently<br>under development."',
     "The federal record's remedy field as read in the archived October 16th run. The service opening and the recall remedy describe separate events.",
     '''function object(X,Y) {
  const x=X-540,y=Y-905;
  if (Math.abs(x)>450 || Math.abs(y)>245) return [0,0];
  const edge=Math.min(450-Math.abs(x),245-Math.abs(y));
  let h=Math.min(20,edge*1.6),m=4;
  if (Math.abs(y)<62 && x>-365 && x<365) {h=8;m=3;}
  if (Math.abs(y)<47 && x>-350 && x<220) {h=17;m=1;}
  if (x>260 && x<320 && Math.abs(y)<100) {h=26;m=2;}
  return [h,m];
}
const height=(X,Y)=>object(X,Y)[0], material=(X,Y)=>object(X,Y)[1];''',
     "A physical field with an unfinished inset. The shape illustrates the recorded status and makes no safety claim.")
]
for number, kicker, title, body, geometry, label in studies:
    html = '''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
<style>*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1350px;overflow:hidden;background:#050A0F;color:#F4F0E7}
canvas{position:absolute;inset:0;width:1080px;height:1350px}.copy{position:absolute;left:82px;right:82px;top:90px}
.kicker{font:24px 'JetBrains Mono';letter-spacing:3px;color:#87B1BE;margin-bottom:40px}
h1{font:700 82px/1.02 'Space Grotesk';letter-spacing:-3px;margin:0 0 36px}p{font:32px/1.42 Manrope;margin:0;max-width:900px}
.label{position:absolute;left:82px;right:82px;top:1188px;font:24px/1.35 Manrope;color:#B6BFC6}
.footer{position:absolute;left:82px;bottom:46px;font:20px 'JetBrains Mono';color:#91A2AD}</style>
<script src="@@ASSETS@@/js/noise.js"></script><script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script><script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/txbench.js"></script><script src="@@ASSETS@@/js/deck/2026-10-16-studio-proof.js"></script>
</head><body><canvas id="art"></canvas><div class="copy"><div class="kicker">KICKER</div><h1>TITLE</h1><p>BODY</p></div>
<div class="label">LABEL</div><div class="footer" data-decorative>RENDERER STUDY / texasaidocket.com</div>
<script>window.renderReady=(async()=>{await document.fonts.ready;
const c=document.getElementById('art');c.width=2160;c.height=2700;const cx=c.getContext('2d');cx.scale(2,2);
GEOMETRY
TXBENCH.relief(cx,{x:0,y:0,w:1080,h:1350,scale:2,height,material,albedo:STUDIO.albedo,spec:STUDIO.spec,
  ambient:0.20,diffuse:0.98,softness:4,castLength:80,dither:true});
TXDECK.finish(cx);
})();</script></body></html>'''
    for key, value in (("KICKER", kicker), ("TITLE", title), ("BODY", body), ("LABEL", label), ("GEOMETRY", geometry)):
        html = html.replace(key, value)
    (HERE / "slides").mkdir(exist_ok=True)
    (HERE / "slides" / f"slide-{number:02}.html").write_text(html)
print("Built three studies from the frozen figures. They are renderer proofs, not a daily release.")
