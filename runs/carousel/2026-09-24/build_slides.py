#!/usr/bin/env python3
"""Writes the nine frames of the 2026-09-24 deck from one shell and nine bespoke scenes.

The shell is the furniture every frame shares: the fonts, the load order, the static site line,
the kicker, counter and source through TXLAYOUT.mount, and the figures from figures.json injected
as FIG so every number a scene draws is the computed one. The SCENE is written per frame and is
the whole of what makes it that frame. Nothing here draws a frame for another frame.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
FIG = json.loads((HERE / "figures.json").read_text(encoding="utf-8"))
OUT = HERE / "slides"
OUT.mkdir(exist_ok=True)

SHELL = """<!doctype html>
<!-- 2026-09-24, frame {n} of 9. Archetype {layout}. RENDERED through txthree.js in the deck's
     declared goldenHour world. {note} -->
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1080px; height:1350px; overflow:hidden; background:#131A24; }}
  body {{ position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }}
  canvas#art {{ position:absolute; left:0; top:0; width:1080px; height:1350px; }}
  .hook .num {{ font-family:"Manrope", sans-serif; font-weight:800; letter-spacing:-0.03em; }}
  .hook {{ position:absolute; font-family:"Fraunces", serif; font-weight:800; line-height:0.94;
          letter-spacing:-0.024em; color:#F4F1EA; font-variation-settings:"opsz" 144; z-index:10;
          text-shadow:0 2px 18px rgba(8,14,26,0.35); }}
  .dek  {{ position:absolute; font-size:30px; line-height:1.40; color:#F2F4F6; z-index:10;
          text-shadow:0 0 5px rgba(8,14,26,0.8), 0 1px 14px rgba(8,14,26,0.6); }}
  .tx-site {{ position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace;
             font-size:24px; letter-spacing:0.07em; line-height:1.5; color:#E6EBEF;
             white-space:nowrap; z-index:20; }}
  .kick, .count, .src, .tx-site {{ text-shadow:0 0 5px rgba(8,14,26,0.85), 0 1px 14px rgba(8,14,26,0.6); }}
  {css}
</style>
</head>
<body>
<canvas id="art" width="2160" height="2700"></canvas>
<div class="tx-site" id="site">texasaidocket.com</div>
<h1 class="hook" id="hook">{hook}</h1>
<p class="dek" data-follow="{follow}">{dek}</p>
{extra}
<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txtype.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/deck/2026-09-24-droneline.js"></script>
<script src="@@ASSETS@@/js/txlayout.js"></script>
<script type="module">
import * as THREE from '@@ASSETS@@/js/three.module.min.js';
import {{ init }} from '@@ASSETS@@/js/txthree.js';
const FIG = {fig};
window.renderReady = (async () => {{
  await document.fonts.ready;
  TXLAYOUT.mount(document.body, {{ kicker: {kicker}, counter: "{n:02d} / 09", src: {src}, ink: '#E6EBEF' }});
  TX.fitText(document.getElementById("hook"), {{ min: {hmin}, max: {hmax}, maxLines: {hlines} }});
  LINE.follow();
  const TXT = init(THREE), L = LINE, gl = L.glCanvas();
  const W = TXT.deckWorld();
  const M = L.mats(TXT, THREE);
{scene}
  return true;
}})();
</script>
</body>
</html>
"""

FRAMES = {}

# ---------------------------------------------------------------------------------------- 1
FRAMES[1] = dict(
    layout="FULL_BLEED",
    note="THE COVER. From a patio across the block, the aircraft small at its true height and the lit line falling from it behind a neighbour's roof to a yard the reader can't see.",
    kicker="FAA draft, open for comment", src="c1 c2 c11 c17 c19 c31   TEXAS AI DOCKET",
    hook="The pod checks the spot",
    dek="Zipline wants FAA approval to fly delivery drones over Houston, San Antonio, Austin, Amarillo and El Paso. The FAA takes comment until October 11th.",
    css=""".hook { left:80px; top:150px; width:640px; } .dek { left:82px; width:640px; font-size:29px; }
  .haze { position:absolute; left:0; top:0; width:1080px; height:640px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.5) 68%, rgba(12,20,34,0) 100%);  -webkit-mask-image:linear-gradient(90deg, #000 0px, #000 822px, transparent 834px, transparent 856px, #000 868px, #000 1080px); }
  .floor { position:absolute; left:0; bottom:0; width:1080px; height:240px; z-index:5; background:linear-gradient(0deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.5) 60%, rgba(12,20,34,0) 100%); }""",
    hmin=86, hmax=112, hlines=2, follow=26, extra='<div class="haze" data-decorative></div><div class="floor" data-decorative></div>',
    scene="""
  /* THE POD OVER A BACK LAWN. The camera stands on the patio side light to the declared sun, the
   * pod hangs a couple of metres over the grass, and the line rises from it out of the top of
   * the frame toward an aircraft the reader can't see from here. The fence behind carries the
   * shut gate that frame 9 opens. */
  const sunB = -58 * Math.PI / 180, lookB = sunB + 96 * Math.PI / 180;
  const f = new THREE.Vector3(Math.sin(lookB), 0, Math.cos(lookB)), rt = new THREE.Vector3(-f.z, 0, f.x);
  const P = (a, s0, y) => [f.x * a + rt.x * s0, y || 0, f.z * a + rt.z * s0];
  const yaw = Math.atan2(f.x, f.z);
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 38 });
  /* solved: from a crouch the pod stands against open sky above the neighbour's ridge */
  TXT.frame(R, { from: P(0, 0, 0.5), look: P(20, 1.0, 3.2) });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: P(12, 2, 0), distance: 90, shadowFar: 260 });
  TXT.ground(R, { surface: 'grass', size: 900, tile: 3, seed: 11 });
  const podAt = P(7.5, 1.6, 2.0);
  /* the rear fence at 22 m with the gate shut in it, the house beyond, oaks */
  const fa = P(22, -26), fb = P(22, -2.5), fc = P(22, -1.5), fd = P(22, 30);
  TXT.add(R, L.fence(THREE, TXT, M, [fa[0], fa[2]], [fb[0], fb[2]]));
  TXT.add(R, L.fence(THREE, TXT, M, [fc[0], fc[2]], [fd[0], fd[2]]));
  const gate = TXT.roundedBox(1.0, 1.8, 0.05, 0.01, M.fence); const gp = P(22.03, -2.0, 0.92); gate.position.set(gp[0], gp[1], gp[2]); gate.rotation.y = yaw; TXT.add(R, gate);
  const h1 = L.house(THREE, TXT, M, { w: 17, d: 11, seed: 2, rise: 2.2 }); const hp = P(40, 2); h1.position.set(hp[0], 0, hp[2]); h1.rotation.y = yaw + Math.PI; TXT.add(R, h1);
  const h2 = L.house(THREE, TXT, M, { w: 16, d: 11, seed: 5, rise: 1.9 }); const hq = P(44, 26); h2.position.set(hq[0], 0, hq[2]); h2.rotation.y = yaw + Math.PI; TXT.add(R, h2);
  [[30, -14, 11, 41], [33, 20, 10, 43], [16, -16, 9, 45]].forEach(([a, s0, hh, sd]) => { const o = L.oak(THREE, TXT, M, { h: hh, seed: sd, lobes: 30 }); const op = P(a, s0); o.position.set(op[0], 0, op[2]); TXT.add(R, o); TXT.contact(R, o); });
  const turf = TXT.scatter(R, { kind: 'grass', count: 16000, near: false, clumping: 0.2, area: [-3, -20, 21, 22], seed: 3, scale: [0.12, 0.34] });
  turf.rotation.y = lookB;
  const pod = L.pod(THREE, TXT, M, {}); pod.position.set(podAt[0], podAt[1], podAt[2]); pod.rotation.y = 0.5; TXT.add(R, pod);
  TXT.add(R, L.line(THREE, M, [podAt[0], podAt[1] + 0.26, podAt[2]], [podAt[0], FIG.cruise.metres, podAt[2]], 0.022), { cast: false });
  TXT.weather(R, {});
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx);
""")


# ---------------------------------------------------------------------------------------- 2
FRAMES[2] = dict(
    layout="DIAGRAM",
    note="THE WHOLE HEIGHT. From off the block at about the aircraft's own height, the line falling from it between the roofs to one yard, leaders landing on what they name.",
    kicker="The whole height, one block", src="c11 c17 c19   TEXAS AI DOCKET",
    hook="It holds at <span class='num'>330</span> feet",
    dek="The pod goes down on a line and back up while the aircraft hovers, for about 75 seconds. The aircraft, the pod and the line are drawn larger than they are.",
    css=""".hook { left:80px; top:150px; width:410px; } .dek { left:82px; width:540px; }
  svg#lead { position:absolute; left:0; top:0; width:1080px; height:1350px; z-index:9; overflow:visible; }
  .haze { position:absolute; left:0; top:0; width:1080px; height:860px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.52) 70%, rgba(12,20,34,0) 100%);  -webkit-mask-image:linear-gradient(90deg, #000 0px, #000 794px, transparent 806px, transparent 830px, #000 842px, #000 1080px), linear-gradient(180deg, #000 0px, #000 185px, transparent 200px); }
  .floor { position:absolute; left:0; bottom:0; width:1080px; height:320px; z-index:5; background:linear-gradient(0deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.5) 60%, rgba(12,20,34,0) 100%); }
  .lab { font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.06em; fill:#E9EEF2; }""",
    hmin=80, hmax=104, hlines=2, follow=26,
    extra='<div class="haze" data-decorative></div><div class="floor" data-decorative></div><svg id="lead" viewBox="0 0 1080 1350"></svg>',
    scene="""
  /* THE HEIGHT, FROM figures.json: the aircraft holds at cruise.metres over one back yard, and
   * the camera stands off the block a little above that height, so the whole height of the line
   * and the roofs it drops between are in one view. */
  const H = FIG.cruise.metres;
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 0.45], exposure: W.exposure * 1.05, tone: W.tone, fov: 44 });
  const pod = [0, 1.2, 0];
  /* from off the neighbourhood's corner, a little above the aircraft, looking across the blocks
   * and away from the sun so the fronts are lit */
  /* the look point sits LEFT of the line by a fixed offset along the camera's own right vector,
   * so the line lands right of centre, clear of the type */
  { const cam = new THREE.Vector3(-120, 72, -112), f = new THREE.Vector3(-cam.x, 0, -cam.z).normalize(), rgt = new THREE.Vector3(-f.z, 0, f.x);
    const dh = Math.hypot(cam.x, cam.z);
    TXT.frame(R, { from: [cam.x, cam.y, cam.z], look: [-rgt.x * 26, cam.y - dh * Math.tan(6 * Math.PI / 180), -rgt.z * 26] }); }
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 260, shadowFar: 620 });
  TXT.ground(R, { surface: 'grass', size: 2200, tile: 6, seed: 12 });
  /* the neighbourhood: blocks of two back to back rows, a street between blocks, a fence down
   * every rear lot line, live oaks in the yards. The pod's yard is at the origin. */
  let k = 0;
  for (let z0 = -210; z0 <= 280; z0 += 70) {
    for (const [dz, face] of [[-12, Math.PI], [12, 0]]) for (let x = -230; x <= 300; x += 21) {
      const h = L.house(THREE, TXT, M, { w: 15 + (k % 3) * 1.3, d: 10, seed: k + 20, rise: 1.8 + (k % 2) * 0.5 });
      h.position.set(x + (k % 2) * 2, 0, z0 + dz + (dz < 0 ? -6 : 6)); h.rotation.y = face; TXT.add(R, h); k++;
    }
    const st = TXT.roundedBox(560, 0.05, 9, 0.01, M.asphalt); st.position.set(35, 0.03, z0 + 35); TXT.add(R, st, { cast: false });
    TXT.add(R, L.fence(THREE, TXT, M, [-240, z0], [310, z0]));
  }
  let q = 0;
  for (let z0 = -210; z0 <= 280; z0 += 70) for (let x = -220; x <= 300; x += 37) {
    const ox = x + (q % 3) * 5, oz = z0 + ((q % 2) ? 5 : -5);
    if (Math.hypot(ox, oz) < 16) { q++; continue; }   /* the delivery spot is open lawn, clear of any crown */
    const o = L.oak(THREE, TXT, M, { h: 9 + (q % 4), seed: 90 + q, lobes: 14 }); o.position.set(ox, 0, oz); TXT.add(R, o); q++;
  }
  const zip = L.zip(THREE, TXT, M, { span: FIG.aircraft.span_m, length: FIG.aircraft.length_m, height: FIG.aircraft.height_m, mode: 'hover', bay: true });
  zip.scale.setScalar(6); zip.position.set(0, H, 0); zip.rotation.y = 0.9; TXT.add(R, zip);
  /* the aircraft six times and the pod five, and the dek says so,
   * because at this distance true size is a few pixels. Only the height is true. */
  const p = L.pod(THREE, TXT, M, {}); p.scale.setScalar(5); p.position.set(pod[0], pod[1] + 1.0, pod[2] + 4); TXT.add(R, p);
  TXT.add(R, L.line(THREE, M, [0, H + zip.userData.bellyY * 6, 0], [0, pod[1] + 2.4, 4], 0.42), { cast: false });
  TXT.weather(R, {});
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx);
  /* THE LEADERS, each ending on its target's own projected coordinates */
  const A = L.project(THREE, R, [0, H, 0]), P = L.project(THREE, R, [0, pod[1] + 1.0, 4]);
  const svg = document.getElementById('lead'), ns = 'http://www.w3.org/2000/svg';
  const mk = (tag, at) => { const e = document.createElementNS(ns, tag); for (const k in at) e.setAttribute(k, at[k]); svg.appendChild(e); return e; };
  const la = [A[0] + 40, A[1] + 70], lp = [P[0] - 470, P[1] + 10];
  mk('path', { d: `M${la[0] + 4},${la[1] - 26} L${A[0] + 10},${A[1] + 10}`, stroke: '#E9EEF2', 'stroke-width': 2, fill: 'none' });
  const t1 = mk('text', { x: la[0], y: la[1], class: 'lab' }); t1.textContent = '330 FT';
  mk('path', { d: `M${lp[0] + 440},${lp[1] + 8} L${P[0] - 12},${P[1] - 4}`, stroke: '#E9EEF2', 'stroke-width': 2, fill: 'none' });
  const t2 = mk('text', { x: lp[0], y: lp[1], class: 'lab' }); t2.textContent = 'THE POD, ABOUT 75 SECONDS';
  window.__txLeaders = [{ target: 'the aircraft at 330 ft', at: [A[0], A[1]], to: [A[0] + 10, A[1] + 10] },
                        { target: 'the pod over one yard', at: [P[0], P[1]], to: [P[0] - 12, P[1] - 4] }];
""")

# ---------------------------------------------------------------------------------------- 3
FRAMES[3] = dict(
    layout="CLOSE_CROP",
    note="THE THING THAT DECIDES. The pod at detail scale a metre over the lawn, the yard soft behind it in the low sun.",
    kicker="What the draft describes", src="c17   TEXAS AI DOCKET",
    hook="It judges the yard",
    dek="On the way down the pod steers itself sideways and evaluates the spot. If the spot is clear, it keeps descending.",
    css=""".hook { left:80px; top:150px; width:620px; } .dek { left:82px; width:560px; }
  .haze { position:absolute; left:0; top:0; width:820px; height:720px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.52) 0%, rgba(12,20,34,0.48) 68%, rgba(12,20,34,0) 100%); -webkit-mask-image:linear-gradient(90deg, #000 72%, transparent 100%); }""",
    hmin=84, hmax=110, hlines=2, follow=26, extra='<div class="haze" data-decorative></div>',
    scene="""
  /* THE POD, close, from low on the lawn so it stands against the sky clear of the fence, with
   * the shaded grass it is judging filling the bottom of the frame. */
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 2.2], exposure: W.exposure, tone: W.tone, fov: 30 });
  const P = [0, 1.02, 0];
  /* solved, not guessed: from a crouch the pod's centre lands near (1050, 650), its right flank
   * leaves the frame, its line passes right of the page counter, and its base clears the fence
   * top in open sky */
  TXT.frame(R, { from: [1.7, 0.6, 3.5], look: [-2.5, 1.2, -2] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 60, shadowFar: 160 });
  TXT.ground(R, { surface: 'grass', size: 600, tile: 2.5, seed: 13 });
  const house = L.house(THREE, TXT, M, { w: 17, d: 11, seed: 3, rise: 2.2 }); house.position.set(-22, 0, -26); TXT.add(R, house);
  TXT.add(R, L.fence(THREE, TXT, M, [-26, -12], [14, -12]));
  const oak = L.oak(THREE, TXT, M, { h: 11, seed: 72, lobes: 30 }); oak.position.set(9, 0, -20); TXT.add(R, oak);
  const pod = L.pod(THREE, TXT, M, {}); pod.position.set(P[0], P[1], P[2]); pod.rotation.y = 0.6; TXT.add(R, pod);
  TXT.add(R, L.line(THREE, M, [P[0], P[1] + 0.26, P[2]], [P[0], FIG.cruise.metres, P[2]], 0.0035), { cast: false });
  { const turf = TXT.scatter(R, { kind: 'grass', count: 9000, area: [-7, -11, 4, 3.3], seed: 5, scale: [0.08, 0.22], nearRadius: 5 }); }
  TXT.weather(R, { grime: 0.5 });
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx, { bloom: { threshold: 0.8, strength: 0.2, radius: 14 } });
""")

# ---------------------------------------------------------------------------------------- 4
FRAMES[4] = dict(
    layout="FULL_BLEED",
    note="THE EXCEPTION. The yard straight down from a few metres up, the kind of image the draft says goes to an operator. No reticle, no interface, because the draft describes none.",
    kicker="The operator step", src="c18   TEXAS AI DOCKET",
    hook="When it can't tell",
    dek="If the pod can't identify the target and judge it, the draft says an image goes to an operator for real-time evaluation. The draft gives no figure for how often.",
    css=""".hook { left:80px; top:150px; width:700px; } .dek { left:82px; width:600px; }
  .haze { position:absolute; left:0; top:0; width:900px; height:560px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.50) 0%, rgba(12,20,34,0.46) 68%, rgba(12,20,34,0) 100%); -webkit-mask-image:linear-gradient(90deg, #000 72%, transparent 100%); }
  .floor { position:absolute; left:0; bottom:0; width:1080px; height:200px; z-index:5; background:linear-gradient(0deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.5) 55%, rgba(12,20,34,0) 100%); }""",
    hmin=84, hmax=110, hlines=2, follow=26, extra='<div class="haze" data-decorative></div><div class="floor" data-decorative></div>',
    scene="""
  /* STRAIGHT DOWN from about the height the pod is released at over a yard, looking at the lawn
   * where it would land. The fence's long evening shadow lies across the top, where the type is. */
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 0.4], exposure: W.exposure * 3.1, tone: W.tone, fov: 52 });
  R.camera.up.set(0, 0, -1);
  TXT.frame(R, { from: [0.4, 7.4, 0.6], look: [0.4, 0, 0.61] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 60, shadowFar: 160 });
  TXT.ground(R, { surface: 'grass', size: 300, tile: 2.2, seed: 14 });
  /* the rear fence runs across the top of the view and throws its shadow over the lawn, a side
   * fence comes in from the left, the back step and patio at the bottom */
  TXT.add(R, L.fence(THREE, TXT, M, [-9, 2.4], [9, -1.6]));
  TXT.add(R, L.fence(THREE, TXT, M, [3.4, -0.2], [9, 8]));
  const patio = TXT.roundedBox(6.5, 0.12, 2.6, 0.02, M.concrete); patio.position.set(3.6, 0.06, 3.8); TXT.add(R, patio);
  const step = TXT.roundedBox(2.2, 0.2, 0.7, 0.02, M.concrete); step.position.set(3.0, 0.16, 2.4); TXT.add(R, step);
  /* THE POD, seen from above as it comes down over the lawn it is judging, its line rising back
   * toward the aircraft and its own long shadow on the grass */
  const pod = L.pod(THREE, TXT, M, {}); pod.position.set(1.25, 2.6, 1.3); pod.rotation.y = 0.7; TXT.add(R, pod);
  TXT.add(R, L.line(THREE, M, [1.25, 2.86, 1.3], [1.25, 90, 1.3], 0.012), { cast: false });
  const turf = TXT.scatter(R, { kind: 'grass', count: 1400, area: [-4, -3.4, 5, 3.4], avoid: [[-4, -3.6, 2.6, 0.2]], seed: 6, scale: [0.2, 0.45], near: false, clumping: 0.6 });
  TXT.weather(R, {});
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx);
""")

# ---------------------------------------------------------------------------------------- 5
FRAMES[5] = dict(
    layout="FIGURE_SCALE",
    note="THE SIZE OF IT. The aircraft on a charger dock behind a strip centre, built to the draft's dimensions from figures.json, a person beside it.",
    kicker="Illustrated to the draft's dimensions", src="c12 c13 c14 c30   TEXAS AI DOCKET",
    hook="About <span class='num'>63</span> pounds, fully loaded",
    dek="The draft gives a wingspan of about 7.8 feet, a length of about 8 feet and a maximum payload of 8 pounds. It calls the aircraft highly automated.",
    css=""".hook { left:80px; top:150px; width:690px; } .dek { left:82px; width:580px; }
  .haze { position:absolute; left:0; top:0; width:1080px; height:640px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.52) 68%, rgba(12,20,34,0) 100%); }
  .floor { position:absolute; left:0; bottom:0; width:1080px; height:240px; z-index:5; background:linear-gradient(0deg, rgba(12,20,34,0.50) 0%, rgba(12,20,34,0.40) 55%, rgba(12,20,34,0) 100%); }""",
    hmin=78, hmax=100, hlines=2, follow=26, extra='<div class="haze" data-decorative></div><div class="floor" data-decorative></div>',
    scene="""
  /* THE SIZE, FROM figures.json: span, length and height set the model; the person is 1.7 m. */
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure * 0.9, tone: W.tone, fov: 32 });
  /* solved: pulled back so the person's feet, the charger's base and the aircraft on its dock
   * all stand on the one pad in frame, the person a pace off the wingtip at the same depth */
  TXT.frame(R, { from: [-6.5, 1.4, 8.5], look: [0.0, 1.6, -0.5] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 70, shadowFar: 200 });
  TXT.ground(R, { surface: 'concrete', size: 700, tile: 4, joints: true, seed: 15 });
  /* the strip centre's blank back wall, running off the left */
  const back = new THREE.Group();
  const wall = TXT.roundedBox(60, 4.2, 1.0, 0.04, L.brickMat(THREE, 60, 4.2)); wall.position.set(0, 2.1, 0); back.add(wall);
  for (let i = 0; i < 7; i++) { const x = -26 + i * 8.6;
    const door = TXT.roundedBox(1.1, 2.3, 0.08, 0.01, M.kiosk); door.position.set(x, 1.15, 0.52); back.add(door);
    const lamp = TXT.roundedBox(0.3, 0.2, 0.25, 0.02, M.windowLit); lamp.position.set(x, 2.9, 0.6); back.add(lamp);
    const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 4.2, 8), M.galv); pipe.position.set(x + 2.6, 2.1, 0.6); back.add(pipe);
    const ac = TXT.roundedBox(1.8, 1.0, 1.4, 0.04, M.galv); ac.position.set(x + 1.4, 4.95, -0.4); back.add(ac); }
  const bin = TXT.roundedBox(2.0, 1.4, 1.4, 0.04, M.cloth[2]); bin.position.set(9, 0.7, 1.8); back.add(bin);
  back.position.set(8, 0, -44); back.rotation.y = -0.3; TXT.add(R, back);
  const coping = TXT.roundedBox(60.4, 0.3, 1.2, 0.03, M.trimWhite); coping.position.set(8, 4.3, -44); coping.rotation.y = -0.3; TXT.add(R, coping);
  /* the charger: a mast with a dock at shoulder height, the aircraft sitting on it */
  const mast = TXT.roundedBox(0.34, 2.6, 0.34, 0.012, M.galv); mast.position.set(1.5, 1.3, -0.6); mast.rotation.y = 0.55; TXT.add(R, mast); TXT.contact(R, mast);
  const arm = TXT.roundedBox(1.6, 0.12, 0.2, 0.02, M.galv); arm.position.set(0.7, 1.72, -0.4); TXT.add(R, arm);
  const dock = TXT.roundedBox(0.9, 0.16, 0.7, 0.04, M.trim); dock.position.set(0.1, 1.72, -0.2); TXT.add(R, dock);
  const zip = L.zip(THREE, TXT, M, { span: FIG.aircraft.span_m, length: FIG.aircraft.length_m, height: FIG.aircraft.height_m, mode: 'hover' });
  /* the draft: the aircraft attaches to the dock from below using its docking fin (c30) */
  zip.position.set(0.1, 1.64 - FIG.aircraft.height_m * 0.5, -0.2); zip.rotation.y = 0.55; TXT.add(R, zip);
  const who = L.person(THREE, M, { seed: 0 }); who.position.set(-1.0, 0, -0.9); who.rotation.y = 0.9; TXT.add(R, who); TXT.contact(R, who, { opacity: 0.8 });
  const base = TXT.roundedBox(1.2, 0.2, 1.2, 0.03, M.concrete); base.position.set(1.5, 0.1, -0.6); TXT.add(R, base);
  /* grit and gravel on the pad, and a painted stall line, so the ground under the type has tooth */
  TXT.scatter(R, { kind: 'rock', count: 500, area: [-8, -6, 8, 8], seed: 21, scale: [0.006, 0.02], nearRadius: 9 });
  const stripe = TXT.roundedBox(0.12, 0.012, 9, 0.004, M.trimWhite); stripe.position.set(-3.2, 0.006, 2.5); stripe.rotation.y = 0.35; TXT.add(R, stripe, { cast: false });
  TXT.weather(R, {});
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx);
""")

# ---------------------------------------------------------------------------------------- 6
FRAMES[6] = dict(
    layout="GRID",
    note="THE CEILING, COUNTED. The draft's maximum of charger towers gathered on one lot to be counted, five blocks for five metros, every count from figures.json.",
    kicker="The draft's maximum, not flights flown", src="c7 c24 c34   TEXAS AI DOCKET",
    hook="Up to <span class='num'>220</span> Chargers",
    dek="Across Amarillo, Austin, El Paso, Houston and San Antonio the draft caps the proposal at 4,400 Dropboxes and 220,000 deliveries a day. Each mast stands for one Charger, which the draft says would typically be 36 docks in three towers of twelve.",
    css=""".hook { left:80px; top:150px; width:860px; } .dek { left:82px; width:910px; font-size:27px; }
  .metro { position:absolute; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.06em; color:#EEF1F4; z-index:11; transform:translateX(-50%); white-space:nowrap; text-shadow:0 1px 8px rgba(8,14,26,0.6); }
  .haze { position:absolute; left:0; top:0; width:1080px; height:640px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.52) 70%, rgba(12,20,34,0) 100%); }""",
    hmin=86, hmax=112, hlines=1, follow=24, extra='<div class="haze" data-decorative></div>',
    scene="""
  /* THE COUNT, FROM figures.json: one mast per Charger the draft allows, per metro, every block
   * five masts wide so its DEPTH is its count, all five in one rank starting at one front line. The lot is turned
   * to face the declared sun and the camera stands 440 m off on the sun's side with a long lens,
   * which keeps every block at one scale (near parallel) while the horizon and the low sky stay in
   * the frame. At nine degrees each mast's long shadow falls behind it. */
  const blocks = [['HOUSTON', FIG.chargers.houston], ['SAN ANTONIO', FIG.chargers.san_antonio], ['AUSTIN', FIG.chargers.austin], ['AMARILLO', FIG.chargers.amarillo], ['EL PASO', FIG.chargers.el_paso]];
  const total = blocks.reduce((a, b) => a + b[1], 0);
  if (total !== FIG.total.chargers) throw new Error('blocks do not sum to the draft total');
  const yaw = TXDECK.deck().light.az * Math.PI / 180;
  const lot = new THREE.Group(); lot.rotation.y = yaw;
  const toW = (x, y, z) => { const v = new THREE.Vector3(x, y, z).applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw); return [v.x, v.y, v.z]; };
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 0.12], exposure: W.exposure, tone: W.tone, fov: 50 });
  TXT.frame(R, { from: toW(26, 50, 124), look: toW(0, 0, -30) });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: toW(0, 0, -6), distance: 300, shadowFar: 800 });
  TXT.ground(R, { surface: 'caliche', size: 6000, tile: 5, seed: 16 });
  const cols = 5, pitch = 2.7, gap = 6;
  const mastG = new THREE.BoxGeometry(0.6, 4.6, 0.6), armG = new THREE.BoxGeometry(0.9, 0.3, 0.3), baseG = new THREE.BoxGeometry(1.2, 0.3, 1.2), dockG = new THREE.BoxGeometry(0.6, 0.34, 0.6);
  const width = blocks.length * cols * pitch + (blocks.length - 1) * gap;
  let x0 = -width / 2;
  const labels = [];
  blocks.forEach(([name, n]) => {
    const rowsN = Math.ceil(n / cols);
    for (let i = 0; i < n; i++) {
      const c = i % cols, r = Math.floor(i / cols);
      const g = new THREE.Group();
      const m = new THREE.Mesh(mastG, M.galv); m.position.y = 2.3; g.add(m);
      /* one arm to one side with one dock, the charger of frame 5, never a cross */
      const a = new THREE.Mesh(armG, M.galv); a.position.set(0.45, 4.3, 0); g.add(a);
      const bs = new THREE.Mesh(baseG, M.concrete); bs.position.y = 0.15; g.add(bs);
      const d = new THREE.Mesh(dockG, M.trim); d.position.set(0.9, 4.1, 0); g.add(d);
      g.position.set(x0 + c * pitch + pitch / 2, 0, -r * pitch); lot.add(g);
    }
    /* each metro's masts stand on their own asphalt pad */
    const pad = TXT.roundedBox(cols * pitch + 2, 0.3, rowsN * pitch + 2, 0.05, M.asphalt); pad.position.set(x0 + cols * pitch / 2, 0.15, -(rowsN - 1) * pitch / 2); lot.add(pad);
    labels.push([name, x0 + cols * pitch / 2, 4]);
    x0 += cols * pitch + gap;
  });
  TXT.add(R, lot);
  TXT.weather(R, {});
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx);
  for (const [name, x, z] of labels) {
    const q = L.project(THREE, R, toW(x, 0, z));
    const d = document.createElement('div'); d.className = 'metro'; d.textContent = name;
    d.style.left = Math.max(110, Math.min(970, q[0])) + 'px'; d.style.top = (q[1] + 16) + 'px'; document.body.appendChild(d);
  }
""")

# ---------------------------------------------------------------------------------------- 7
FRAMES[7] = dict(
    layout="SPLIT_HORIZON",
    note="THE NOISE FINDING. Across the fence the pod holds over the next yard. Below the cut, on the neighbour's shaded lawn, the draft's estimate, its screening line and its conclusion, in its own figures and with no bar drawn.",
    kicker="The draft's noise finding", src="c21 c26 c29 c35   TEXAS AI DOCKET",
    hook="It finds no significant impact",
    dek="The draft ties 400 deliveries a day to places like a large apartment complex. At that rate it estimates delivery noise at no more than DNL 58.1 dB at any distance from a delivery point. It calls 59.7 dB the line below which a rise of 1.5 dB or more can't be significant.",
    css=""".hook { left:80px; top:790px; width:900px; letter-spacing:0.005em; } .dek { left:82px; width:910px; font-size:27px; }
  .haze { position:absolute; left:0; top:0; width:1080px; height:300px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.5) 55%, rgba(12,20,34,0) 100%);  -webkit-mask-image:linear-gradient(90deg, #000 0px, #000 732px, transparent 744px, transparent 764px, #000 776px, #000 1080px); }
  .bars { position:absolute; left:82px; top:1104px; width:916px; z-index:10; }
  .bar { height:16px; background:#C9D2DA; margin:0 0 10px 0; }
  .bl { font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.05em; color:#E2E6EA; margin:0 0 6px 0; }""",
    hmin=60, hmax=72, hlines=1, follow=18,
    extra='<div class="haze" data-decorative></div><div class="bars" id="bars"></div>',
    scene="""
  /* THE BARS, FROM figures.json, from zero at one scale: the draft's delivery figure against the
   * FAA's threshold. One hue, no zone, a bar and never a dial. */
  /* THE DRAFT'S OWN FIGURES, AS TEXT. No bars: DNL is a logarithmic average and any bar drawn from
   * zero, or scaled by energy, makes a claim about the margin that the draft does not make. The
   * frame prints the draft's estimate and its screening line, both from figures.json, and says
   * what the draft concluded. */
  const box = document.getElementById('bars');
  for (const t of [`THE DRAFT'S ESTIMATE, DNL ${FIG.noise.delivery_dnl_db_any_distance} dB`, `ITS SCREENING LINE, DNL ${FIG.noise.screening_dnl_db} dB`]) {
    const l = document.createElement('div'); l.className = 'bl'; l.textContent = t; box.appendChild(l); }
  /* THE YARD NEXT DOOR. The camera stands in the shade of the neighbour's own house, so the
   * lower half of the frame is shaded lawn and the type sits on it. */
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 38 });
  /* solved: the fence base, the cut, lands near y 746, above the hook, so the type sits on the
   * shaded lawn below it */
  TXT.frame(R, { from: [0, 2.45, 0], look: [-1.0, -1.7, -30] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -14], distance: 120, shadowFar: 300 });
  TXT.ground(R, { surface: 'grass', size: 900, tile: 4, seed: 17 });
  /* the neighbour's house behind the camera throws the shade; the shared fence, the next yard */
  const own = L.house(THREE, TXT, M, { w: 18, d: 12, h: 5.2, seed: 6, rise: 2.4 }); own.position.set(4, 0, 12); TXT.add(R, own);
  TXT.add(R, L.fence(THREE, TXT, M, [-20, -14], [16, -14]));
  const next = L.house(THREE, TXT, M, { w: 16, d: 11, seed: 7, rise: 2.0 }); next.position.set(-6, 0, -40); TXT.add(R, next); TXT.contact(R, next);
  const far = L.house(THREE, TXT, M, { w: 15, d: 11, seed: 8 }); far.position.set(18, 0, -44); TXT.add(R, far);
  const who = L.person(THREE, M, { seed: 2, lookUp: true }); who.position.set(2.4, 0, -11.5); who.rotation.y = Math.PI; TXT.add(R, who); TXT.contact(R, who, { opacity: 0.7 });
  const pod = L.pod(THREE, TXT, M, {}); pod.position.set(1.5, 2.4, -21); TXT.add(R, pod);
  TXT.add(R, L.line(THREE, M, [1.5, 2.82, -21], [1.5, 90, -21], 0.06), { cast: false });
  TXT.weather(R, {});
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx);
""")

# ---------------------------------------------------------------------------------------- 8
FRAMES[8] = dict(
    layout="DOCUMENT",
    note="WHO PREPARED IT. The draft lying on a cedar patio table in raking light, its prepared by line and a table of maximums on the page, the line crossing overhead.",
    kicker="Its own words", src="c6 c7 c27 c36   TEXAS AI DOCKET",
    hook="Zipline prepared it",
    dek="The draft says Zipline prepared it under FAA supervision. Its noise figures rest on testing Zipline collected, in a report ICF prepared for the FAA. The page sets passages from across the draft side by side.",
    css=""".hook { left:80px; top:150px; width:900px; } .dek { left:82px; width:800px; }
  .floor { position:absolute; left:0; bottom:0; width:1080px; height:230px; z-index:5; background:linear-gradient(0deg, rgba(12,20,34,0.50) 0%, rgba(12,20,34,0.40) 55%, rgba(12,20,34,0) 100%); }
  .haze { position:absolute; left:0; top:0; width:1080px; height:700px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.5) 0%, rgba(12,20,34,0.46) 68%, rgba(12,20,34,0) 100%); }""",
    hmin=76, hmax=100, hlines=1, follow=24, extra='<div class="haze" data-decorative></div><div class="floor" data-decorative></div>',
    scene="""
  /* THE PAGE, drawn on a canvas in the deck's own type and laid on the table as a texture. Its
   * five rules are the metros' maximum deliveries from figures.json, at one scale. */
  const pc = document.createElement('canvas'); pc.width = 1700; pc.height = 2200;
  const g = pc.getContext('2d');
  g.fillStyle = '#EFE9DD'; g.fillRect(0, 0, 1700, 2200);
  g.fillStyle = '#1D232B'; g.font = '600 64px Manrope'; g.textBaseline = 'top';
  const wrap = (txt, x, y, w, lh, font) => { g.font = font; let line = '', yy = y; for (const w0 of txt.split(' ')) { const t = line ? line + ' ' + w0 : w0; if (g.measureText(t).width > w && line) { g.fillText(line, x, yy); line = w0; yy += lh; } else line = t; } g.fillText(line, x, yy); return yy + lh; };
  let y = wrap('Draft Environmental Assessment for Zipline International Inc. Proposed Drone Package Delivery Operations in Multiple Texas Metropolitan Areas', 150, 170, 1400, 84, '700 66px Manrope');
  y = wrap('September 2026', 150, y + 20, 1400, 60, '500 44px Manrope');
  g.fillRect(150, y + 40, 1400, 6);
  y = wrap('Zipline prepared this draft environmental assessment (draft EA) under the supervision of the FAA', 150, y + 100, 1400, 104, '700 84px Manrope');
  g.fillRect(150, y + 60, 1400, 3);
  /* TABLE 2.2-1 AS THE DRAFT PRINTS IT, row by row from figures.json, which compute.py extracts from
   * c7's own quote, so the page carries the draft's numbers and no chart the draft does not draw */
  y = wrap('Table 2.2-1. Maximum Number of Zipline Chargers, Dropboxes, and Deliveries per Day by Metro Area', 150, y + 100, 1400, 54, '700 44px Manrope');
  { const heads = ['Area (square miles)', 'Zipline Chargers', 'Zipline Dropboxes', 'Maximum Deliveries per Day', 'Maximum Transits per Day'];
    g.font = '600 28px Manrope'; let x = 470, hy = y + 30, deep = 0;
    for (const h of heads) { const words = h.split(' '); let line = '', ly = hy, lines = 0;
      for (const w0 of words) { const t = line ? line + ' ' + w0 : w0; if (g.measureText(t).width > 196 && line) { g.fillText(line, x + 200 - g.measureText(line).width, ly); line = w0; ly += 32; lines++; } else line = t; }
      g.fillText(line, x + 200 - g.measureText(line).width, ly); deep = Math.max(deep, lines + 1); x += 216; }
    y = hy + deep * 32; }
  const fmt = (v) => v.toLocaleString('en-US');
  const rows = [['Houston', FIG.metros['Houston']], ['San Antonio', FIG.metros['San Antonio']], ['Austin', FIG.metros['Austin']], ['Amarillo', FIG.metros['Amarillo']], ['El Paso', FIG.metros['El Paso']], ['Total', FIG.total]];
  y += 30;
  for (const [n, r] of rows) { g.font = (n === 'Total' ? '700' : '500') + ' 42px Manrope'; g.fillText(n, 150, y); let x = 470;
    for (const k of ['area_sq_mi', 'chargers', 'dropboxes', 'deliveries_max', 'transits_max']) { const t = fmt(r[k]); g.fillText(t, x + 200 - g.measureText(t).width, y); x += 216; } y += 72; }
  g.fillRect(150, y + 20, 1400, 6);
  y = wrap('Noise exposure estimates are provided for the Platform 2 UA (P2 Zip) based on sound level testing data collected by Zipline (2025, 2026).', 150, y + 90, 1400, 68, '600 52px Manrope');
  const tex = new THREE.CanvasTexture(pc); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  /* THE DRAFT PROPPED ON ITS CLIPBOARD ON THE PATIO TABLE, square to a low camera, so the page
   * reads and the yard, the back fence, the neighbour's roof and the low sky stand behind it */
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 1.2], exposure: W.exposure * 1.25, tone: W.tone, fov: 44 });
  TXT.frame(R, { from: [0.05, 1.12, 1.35], look: [0.0, 1.13, 0.0] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0.8, 0], distance: 40, shadowFar: 120 });
  TXT.ground(R, { surface: 'grass', size: 500, tile: 3, seed: 18 });
  /* the cedar table, boards with gaps */
  const cedar = L.cedarMat(THREE);
  for (let i = 0; i < 15; i++) { const b = TXT.roundedBox(0.13, 0.04, 1.02, 0.008, cedar); b.position.set(-1.05 + i * 0.15, 0.74, 0.09); TXT.add(R, b); }
  for (const x of [-1.05, 1.05]) for (const z of [0.52, -0.34]) { const leg = TXT.roundedBox(0.08, 0.72, 0.08, 0.01, M.fence); leg.position.set(x, 0.36, z); TXT.add(R, leg); }
  const lean = new THREE.Group();
  const board = TXT.roundedBox(0.47, 0.62, 0.012, 0.006, M.fence); board.position.set(0, 0.31, -0.008); lean.add(board);
  const clip = TXT.roundedBox(0.12, 0.035, 0.02, 0.006, M.galv); clip.position.set(0, 0.6, 0.006); lean.add(clip);
  const page = new THREE.Mesh(new THREE.PlaneGeometry(0.4318, 0.5588), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.88 }));
  page.position.set(0, 0.29, 0.0005); lean.add(page);
  lean.rotation.x = -0.42; lean.position.set(0, 0.76, 0.12); TXT.add(R, lean);
  page.castShadow = false;
  /* what it leans on: a closed binder lying behind it */
  const binder = TXT.roundedBox(0.32, 0.07, 0.4, 0.01, M.cloth[0]); binder.position.set(0.02, 0.795, -0.2); TXT.add(R, binder); TXT.contact(R, binder, { opacity: 0.6 });
  const mug = TXT.lathe([[0.001, 0], [0.045, 0], [0.047, 0.1], [0.043, 0.1], [0.041, 0.006], [0.001, 0.006]], M.trimWhite, { segments: 40 }); mug.position.set(0.42, 0.76, 0.3); TXT.add(R, mug); TXT.contact(R, mug, { opacity: 0.7 });
  /* the yard behind: the back fence, the neighbour's roof over it */
  TXT.add(R, L.fence(THREE, TXT, M, [-30, -12], [30, -12]));
  const nb = L.house(THREE, TXT, M, { w: 16, d: 11, seed: 9, rise: 2.0 }); nb.position.set(-5, 0, -26); nb.rotation.y = Math.PI; TXT.add(R, nb);
  const nb2 = L.house(THREE, TXT, M, { w: 15, d: 11, seed: 10, rise: 1.8 }); nb2.position.set(14, 0, -30); nb2.rotation.y = Math.PI; TXT.add(R, nb2);
  TXT.weather(R, { skip: [page] });
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx);
""")

# ---------------------------------------------------------------------------------------- 9
FRAMES[9] = dict(
    layout="FULL_BLEED",
    note="THE DOOR. Low on the lawn looking toward the sun, the gate standing open with light across the grass, a parcel in the foreground, the aircraft small and climbing away.",
    kicker="Public comment", src="c2 c3 c18   TEXAS AI DOCKET",
    hook="Comments close October <span class='num'>11th</span>",
    dek="The draft gives no figure for how often an operator is sent an image. Email <span style='white-space:nowrap'>9-FAA-Drone-Environmental@faa.gov</span> and name the Zipline Texas Draft EA in the subject line.",
    css=""".hook { left:80px; top:150px; width:640px; } .dek { left:82px; width:650px; font-size:28px; }
  .floor { position:absolute; left:0; bottom:0; width:1080px; height:240px; z-index:5; background:linear-gradient(0deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.5) 60%, rgba(12,20,34,0) 100%); }
  .haze { position:absolute; left:0; top:0; width:1080px; height:880px; z-index:5; background:linear-gradient(180deg, rgba(12,20,34,0.54) 0%, rgba(12,20,34,0.54) 74%, rgba(12,20,34,0) 100%); -webkit-mask-image:radial-gradient(circle at 870px 474px, transparent 0px, transparent 24px, #000 175px); }""",
    hmin=80, hmax=104, hlines=2, follow=22, extra='<div class="haze" data-decorative></div><div class="floor" data-decorative></div>',
    scene="""
  /* INTO THE SUN THROUGH THE GATE. The camera looks a few degrees left of the declared sun's
   * bearing, so the sun sits right of centre, and the open gate in the rear fence is set on
   * the sun's own bearing, so the low light comes through the gap. The aircraft has gone. */
  const sunB = -58 * Math.PI / 180, lookB = sunB + 9 * Math.PI / 180;
  const s = new THREE.Vector3(Math.sin(sunB), 0, Math.cos(sunB)), sr = new THREE.Vector3(-s.z, 0, s.x);
  const S = (a, s0) => [s.x * a + sr.x * s0, s.z * a + sr.z * s0];
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure * 0.7, tone: W.tone, fov: 36 });
  TXT.frame(R, { from: [0, 0.75, 0], look: [Math.sin(lookB) * 100, 7, Math.cos(lookB) * 100] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [s.x * 10, 0, s.z * 10], distance: 90, shadowFar: 240 });
  TXT.ground(R, { surface: 'grass', size: 900, tile: 4, seed: 19 });
  /* the rear fence across the view at 16 m, the gate gap on the sun's own bearing */
  const yaw = Math.atan2(s.x, s.z);
  const g0 = S(16, -30), g1 = S(16, -0.6), g2 = S(16, 0.6), g3 = S(16, 24);
  TXT.add(R, L.fence(THREE, TXT, M, g0, g1)); TXT.add(R, L.fence(THREE, TXT, M, g2, g3));
  const gate = TXT.roundedBox(1.0, 1.8, 0.05, 0.01, M.fence); const gp = S(15.5, 0.62); gate.position.set(gp[0], 0.92, gp[1]); gate.rotation.y = yaw + 1.2; TXT.add(R, gate);
  /* the parcel on the grass, whole, its long shadow reaching back toward the lens */
  const box = TXT.roundedBox(0.36, 0.24, 0.3, 0.012, M.package); const bp = S(4.6, -0.2); box.position.set(bp[0], 0.12, bp[1]); box.rotation.y = 0.4; TXT.add(R, box); TXT.contact(R, box);
  const tape = TXT.roundedBox(0.37, 0.245, 0.05, 0.004, M.trimWhite); tape.position.set(bp[0], 0.12, bp[1]); tape.rotation.y = 0.4; TXT.add(R, tape);
  const turf = TXT.scatter(R, { kind: 'grass', count: 6000, area: [-16, -16, 16, 16], seed: 9, scale: [0.12, 0.36], nearRadius: 8 });
  /* the neighbours' houses beyond the fence, off the sun's bearing so the light still comes through the gate */
  [[36, -16, 4], [40, 13, 5]].forEach(([a, s0, sd]) => { const h = L.house(THREE, TXT, M, { w: 16, d: 11, seed: sd, rise: 2.0 }); const hp = S(a, s0); h.position.set(hp[0], 0, hp[1]); h.rotation.y = yaw + Math.PI; TXT.add(R, h); });
  TXT.weather(R, {});
  const cx = L.develop(await TXT.snapshot(R), gl);
  TXDECK.finish(cx, { bloom: { threshold: 0.7, strength: 0.34, radius: 20 } });
""")


def js(v):
    return json.dumps(v)


def build(only=None):
    for n, f in FRAMES.items():
        if only and n not in only:
            continue
        html = SHELL.format(n=n, layout=f["layout"], note=f["note"], css=f["css"], hook=f["hook"],
                            dek=f["dek"], follow=f["follow"], extra=f["extra"], fig=js(FIG),
                            kicker=js(f["kicker"]), src=js(f["src"]), hmin=f["hmin"], hmax=f["hmax"],
                            hlines=f["hlines"], scene=f["scene"])
        (OUT / ("slide-%02d.html" % n)).write_text(html, encoding="utf-8")
        print("wrote slide-%02d.html" % n)


if __name__ == "__main__":
    import sys
    build([int(a) for a in sys.argv[1:]] or None)
