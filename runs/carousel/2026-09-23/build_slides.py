#!/usr/bin/env python3
"""Writes the nine RENDERED frames of carousel no. 32 from one shared shell.

Every frame renders the same hero object, the containerised gas generator set modelled once in
assets/js/deck/2026-09-23-gensetyard.js, through txthree.js, under the deck's one light read by
TXT.deckRig. The shell is shared so the furniture, the finish and the stage cannot drift between
frames. Each frame's SCENE is its own code below, because that is where the camera, the state of
the object and the figure it draws are decided, and where depth_floor reads the staging.

No print screen, at any point. print_ban refuses one.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "slides"

HEAD = """<!doctype html>
<!-- CAROUSEL 32, frame {n} of 9. Archetype {layout}. RENDERED through txthree.js.
{note} -->
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1080px; height:1350px; overflow:hidden; background:{bg}; }}
  body {{ position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }}
  canvas#art {{ position:absolute; left:0; top:0; width:1080px; height:1350px; }}
  .hook {{ position:absolute; font-family:"Fraunces", serif; font-weight:800; line-height:0.92;
          letter-spacing:-0.026em; color:{hook_ink}; font-variation-settings:"opsz" 144; z-index:10; }}
  .dek  {{ position:absolute; font-size:30px; line-height:1.40; color:{dek_ink}; z-index:10; }}
{extra_css}  .tx-site {{ position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace;
             font-size:24px; letter-spacing:0.07em; line-height:1.5; color:{site_ink};
             white-space:nowrap; z-index:20; }}
{css}
</style>
</head>
<body>
<canvas id="art" width="2160" height="2700"></canvas>
<div class="tx-site" id="site">texasaidocket.com</div>
{html}
<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txtype.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/deck/2026-09-23-gensetyard.js"></script>
<script src="@@ASSETS@@/js/txlayout.js"></script>
<script type="module">
import * as THREE from '@@ASSETS@@/js/three.module.min.js';
import {{ init }} from '@@ASSETS@@/js/txthree.js';
window.renderReady = (async () => {{
  await document.fonts.ready;
  TXLAYOUT.mount(document.body, {{
    kicker: {kicker!r}, {kicker2}counter: "{n:02d} / 09",
    src: {src!r}, ink: {furn_ink!r}
  }});
  TX.fitText(document.getElementById("hook"), {fit});
  YARD.follow();
  const TXT = init(THREE);
  const Y = YARD, gl = Y.glCanvas();
{scene}
  const cx = Y.develop(await TXT.snapshot(R), gl);
{after}
  TXDECK.finish(cx{finish});
  return true;
}})();
</script>
</body>
</html>
"""

LAB_CSS = """  .lab  {{ position:absolute; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.06em;
          line-height:1.35; color:{lab_ink}; white-space:nowrap; z-index:12; text-transform:uppercase; }}
"""
FIG_CSS = """  .fig  {{ position:absolute; font-family:"Fraunces", serif; font-weight:700; color:{hook_ink};
          font-variation-settings:"opsz" 144; line-height:1; z-index:12; }}
"""

DARK = dict(bg="#0D1117", hook_ink="#EEF0F3", dek_ink="#C9CCD4", lab_ink="#AEB3BD",
            site_ink="#9AA0AC", furn_ink="#9AA0AC")

FRAMES = []

# ---------------------------------------------------------------------------------------- 1
FRAMES.append(dict(
    n=1, layout="FULL_BLEED", **DARK,
    note="""     THE OPEN. The line of sets from off its near end at night, receding into fog. The count
     of sets built is behind_the_meter.units from figures.json, so the line IS the figure.
     One light, the deck's. No amber: a machinery frame.""",
    kicker="Texas AI Docket", kicker2='kicker2: "September 23rd", ',
    src="c1 c16 c17   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:176px; width:860px; font-size:168px; line-height:0.88; letter-spacing:-0.030em; }
  .dek  { left:82px; top:388px; width:640px; font-size:31px; }""",
    html="""<h1 class="hook" id="hook">Sought by</h1>
<p class="dek">Two words decide who a permit halt reaches.</p>""",
    fit="{ min: 118, max: 168, maxLines: 1 }",
    scene="""
  /* THE COUNT, FROM figures.json. behind_the_meter.units, read out of c17 by compute.py. */
  const UNITS = 40;

  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 30, 165], exposure: 1.0, fov: 40 });
  TXT.environment(R, { intensity: 0.45 });
  TXT.deckRig(R, Y.RIG, { target: [0, 0, -50], distance: 140, shadowFar: 300 });
  const pad = TXT.ground(R, { color: Y.PAD, size: 600, roughness: 0.96 });
  Y.padMap(THREE, pad, { repeat: 150 });
  const M = Y.mats(TXT);

  /* THE LINE. Long axis across the camera, a 4.6 m pitch, which is a 2.44 m box and a walkway. */
  const PITCH = 4.6;
  for (let i = 0; i < UNITS; i++) {
    const g = Y.genset(THREE, M, { detail: i < 6 });
    g.position.set(0, 0, -i * PITCH);
    TXT.add(R, g);
  }
  for (const z of [-58, -118]) { const m = Y.mast(THREE, M, { height: 12 }); m.position.set(-10, 0, z); TXT.add(R, m); }

  /* THE YARD FENCE down the line's far side: galvanised posts every 3 m and a top rail, one
   * instanced mesh, so the line reads as a site with an edge rather than machines on a plain. */
  const postGeo = new THREE.CylinderGeometry(0.035, 0.035, 2.1, 8);
  const posts = new THREE.InstancedMesh(postGeo, M.galv, 70);
  const m4 = new THREE.Matrix4();
  for (let k = 0; k < 70; k++) { m4.makeTranslation(9.5, 1.05, 12 - k * 3); posts.setMatrixAt(k, m4); }
  TXT.add(R, posts);
  const topRail = Y.tile(THREE, 0.05, 0.05, 210, M.galv);
  topRail.position.set(9.5, 2.08, 12 - 105); TXT.add(R, topRail);

  /* Off the line's near end, looking down it, its vanishing point left of centre inside the
   * frame and the nearest stack tops under the dek. */
  TXT.frame(R, { fov: 40, from: [-12.5, 2.1, 23], look: [-5.4, 8.6, -26] });
  Y.sky(THREE, R);
""",
    after="",
    finish=', { bloom: { threshold: 0.8, strength: 0.18, radius: 10 } }',
))

# ---------------------------------------------------------------------------------------- 2
FRAMES.append(dict(
    n=2, layout="CLOSE_CROP", **DARK,
    note="""     INSIDE THE MACHINE'S OWN SPACE. The hero's radiator end and its stack, cropped by the top,
     left and right edges, at detail scale, with no wire, conduit or insulator anywhere. The set is
     turned so its radiator end faces the deck's light. What the frame is missing is the whole of
     the audit's reach.""",
    kicker="What the audit can do", kicker2="",
    src="c7 c10 c5   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:968px; width:920px; font-size:104px; }
  .dek  { left:82px; width:830px; font-size:29px; }""",
    html="""<h1 class="hook" id="hook">A connection to deny</h1>
<p class="dek" data-follow="22">The Governor's August 3rd letter says a project that fails to comply must be denied connection to the Texas grid. That audit covers data centers advancing through the interconnection queue.</p>""",
    fit="{ min: 80, max: 104, maxLines: 1 }",
    scene="""
  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 16, 90], exposure: 1.0, fov: 40 });
  TXT.environment(R, { intensity: 0.5 });
  TXT.deckRig(R, Y.RIG, { target: [0, 0, 0], distance: 40, shadowFar: 120 });
  const pad = TXT.ground(R, { color: Y.PAD, size: 300, roughness: 0.96 });
  Y.padMap(THREE, pad, { repeat: 80 });
  const M = Y.mats(TXT);

  /* THE HERO, turned half a turn so the radiator end and its louvres face the key. */
  const hero = Y.genset(THREE, M, {});
  hero.rotation.y = Math.PI;
  TXT.add(R, hero);
  /* the next set down the line, dark behind, so the crop sits in a yard rather than a void */
  const next = Y.genset(THREE, M, { detail: false });
  next.rotation.y = Math.PI; next.position.set(0, 0, -4.6);
  TXT.add(R, next);

  /* WHAT ONLY A CLOSE CROP SEES, added here rather than in the chassis because it is detail at
   * this range and noise at every other: forklift pockets through the skid's end rail, lifting
   * lugs at the four roof corners, and the bird screen behind the louvres. Still no cable. */
  for (const pz of [-0.7, 0.7]) {
    const pocket = Y.tile(THREE, 0.06, 0.2, 0.36, M.recess);
    pocket.position.set(-6.32, 0.28, pz); TXT.add(R, pocket);
  }
  for (const [lx, lz] of [[-6.0, 1.1], [-6.0, -1.1], [6.0, 1.1], [6.0, -1.1]]) {
    const lug = new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.022, 8, 16), M.galv);
    lug.position.set(lx, 3.46, lz); lug.rotation.y = Math.PI / 2; TXT.add(R, lug);
  }
  const mesh = new THREE.InstancedMesh(new THREE.BoxGeometry(0.01, 2.3, 0.012), M.skid, 40);
  const mm = new THREE.Matrix4();
  for (let k = 0; k < 40; k++) { mm.makeTranslation(-6.12, 1.9, -1.0 + k * 0.052); mesh.setMatrixAt(k, mm); }
  TXT.add(R, mesh);

  /* Close on the louvred end from low and off its corner, so the end fills the top two thirds
   * and leaves the top edge, and the pad in front of it holds the type. */
  TXT.frame(R, { fov: 46, from: [-13.5, 0.9, 2.8], look: [-3.8, 1.4, -0.6] });
  Y.sky(THREE, R);
""",
    after="",
    finish='',
))

# ---------------------------------------------------------------------------------------- 3
FRAMES.append(dict(
    n=3, layout="DOCUMENT", **DARK,
    note="""     THE PAGE. The directive, posted on a notice board at the edge of the pad and turned into the
     deck's light, with the yard behind it in the fog. The page is the one lit sheet in the frame.
     Its two sentences are set on the page itself, projected onto its drawn rect through the
     frame's camera. Amber is the state's paper: it lands on the page's rule and nowhere else.""",
    kicker="The directive, as reported", kicker2="",
    src="c3 c11 c5   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:150px; width:920px; font-size:92px; }
  .dek  { left:82px; width:820px; font-size:29px; }
  .page { position:absolute; z-index:12; color:#16181D; }
  .page .k { font-family:"JetBrains Mono", monospace; font-size:19px; letter-spacing:0.08em; color:#4C4640; }
  .page .k { font-size:24px; }
  .page .q { font-family:"Fraunces", serif; font-weight:600; font-size:30px; line-height:1.12;
             letter-spacing:-0.012em; margin:9px 0 32px 0; font-variation-settings:"opsz" 72; }""",
    html="""<h1 class="hook" id="hook">Two scopes</h1>
<p class="dek" data-follow="20">One names who is asking. The other ties permits to audit results from ERCOT and the water board.</p>
<div class="page" id="page">
  <div class="k">THE GOVERNOR, AS CBS QUOTED IT&nbsp;&nbsp;c3</div>
  <div class="q">"TCEQ will issue no permits sought by data center projects"</div>
  <div class="k">A LAW FIRM'S READING&nbsp;&nbsp;c11</div>
  <div class="q" style="margin-bottom:0">"align its permitting decisions with forthcoming audit results from ERCOT and the Texas Water Development Board (TWDB)"</div>
</div>""",
    fit="{ min: 76, max: 92, maxLines: 1 }",
    scene="""
  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 10, 70], exposure: 1.0, fov: 38 });
  TXT.environment(R, { intensity: 0.45 });
  TXT.deckRig(R, Y.RIG, { target: [0, 1, 0], distance: 40, shadowFar: 120 });
  const pad = TXT.ground(R, { color: Y.PAD, size: 300, roughness: 0.96 });
  Y.padMap(THREE, pad, { repeat: 90 });
  const M = Y.mats(TXT);

  /* THE BOARD faces the key: its normal points back along the light's own ground direction, so
   * the page takes the deck's light square on and needs no second lamp. */
  const L = TXDECK.deck().light, az = L.az * Math.PI / 180;
  const nx = Math.sin(az), nz = Math.cos(az);
  const board = new THREE.Group();
  const ply = Y.tile(THREE, 1.06, 1.30, 0.04, TXT.mat.clay(0x4d443a, { roughness: 0.8 }));
  ply.position.set(0, 1.55, 0); board.add(ply);
  /* ONE post, on the board's centre line, so it leaves the frame between the source line and
   * the site line rather than through either of them */
  const post = Y.tile(THREE, 0.1, 1.3, 0.1, TXT.mat.clay(0x3a332b, { roughness: 0.85 }));
  post.position.set(0, 0.65, -0.075); board.add(post);
  /* THE PAGE, 0.90 m by 1.10 m, a posted notice. Paper white, the amber rule across its head. */
  const PW = 0.90, PH = 1.10, PY = 1.55;
  const paper = Y.tile(THREE, PW, PH, 0.004, TXT.mat.clay(0xefece4, { roughness: 0.85 }));
  paper.position.set(0, PY, 0.024); board.add(paper);
  const rule = Y.tile(THREE, PW - 0.12, 0.05, 0.004, Y.paperMat(THREE));
  rule.position.set(0, PY + PH / 2 - 0.07, 0.028); board.add(rule);
  board.rotation.y = Math.atan2(nx, nz);
  TXT.add(R, board);

  /* THE YARD BEHIND THE BOARD, in the fog: a line of sets across the view, far enough back that
   * their stacks stay under the dek. Forward is -n, right is forward x up. */
  const fx = -nx, fz = -nz, rx = -fz, rz = fx;
  for (let i = 0; i < 9; i++) {
    const t = 40 + (i % 3) * 5, lat = -26 + i * 6.5;
    const g = Y.genset(THREE, M, { detail: false });
    g.position.set(fx * t + rx * lat, 0, fz * t + rz * lat);
    g.rotation.y = Math.atan2(-fx, -fz) + Math.PI;
    TXT.add(R, g);
  }

  /* square on to the board, from the key side, a little low so the yard rises behind it */
  const D = 3.9;
  TXT.frame(R, { fov: 38, from: [nx * D, 1.45, nz * D], look: [0, 1.65, 0] });
  Y.sky(THREE, R);
""",
    after="""
  /* THE PAGE'S TYPE, onto the page's drawn rect through the camera, inset by its margin. */
  const corner = (u, v) => {
    const p = new THREE.Vector3(u * PW / 2, PY + v * PH / 2, 0.03).applyMatrix4(board.matrixWorld);
    return Y.project(THREE, R, [p.x, p.y, p.z]);
  };
  const cs = [corner(-1, 1), corner(1, 1), corner(-1, -1), corner(1, -1)];
  const x0 = Math.min(...cs.map(c => c.x)), x1 = Math.max(...cs.map(c => c.x));
  const y0 = Math.min(...cs.map(c => c.y)), y1 = Math.max(...cs.map(c => c.y));
  const pg = document.getElementById("page");
  const inset = (x1 - x0) * 0.08;
  pg.style.left = (x0 + inset) + "px";
  pg.style.top = (y0 + (y1 - y0) * 0.09) + "px";
  pg.style.width = (x1 - x0 - 2 * inset) + "px";
""",
    finish=', { bloom: { threshold: 0.9, strength: 0.08, radius: 8 } }',
))

# ---------------------------------------------------------------------------------------- 4
FRAMES.append(dict(
    n=4, layout="DIAGRAM", **DARK,
    note="""     ONE HUNDRED PLATES ON THE PAD, TEN BY TEN, UNDER A PARALLEL CAMERA. The number painted amber
     is data_center_share.percent from figures.json. Parallel, because perspective would shrink the
     far rows and a reader would read the shrink as a smaller share. The queue's 474 GW is stated
     on NO scale here, because it is a different denominator and nothing multiplies the two.""",
    kicker="What the queue holds", kicker2="",
    src="c8 c23   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:150px; width:920px; font-size:88px; }
  .dek  { left:82px; width:880px; font-size:28px; }
  .fig.big { font-size:96px; }""",
    html="""<h1 class="hook" id="hook">Ninety percent of the new ones</h1>
<p class="dek" data-follow="20">ERCOT counts more than 474 gigawatts of requests to connect. The Governor puts data centers at about ninety percent of the new ones.</p>
<div class="lab" id="l1">Approximate data center share<br>of new power requests</div>
<div class="fig big" id="f1">90%</div>
<div class="lab" id="l2">The whole queue,<br>on no scale here</div>
<div class="fig" id="f2" style="font-size:54px">474 GW</div>""",
    fit="{ min: 64, max: 88, maxLines: 2 }",
    scene="""
  /* THE SHARE, FROM figures.json. data_center_share.percent, read out of c23 by compute.py. */
  const SHARE = 90;
  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 60, 160], exposure: 1.0 });
  Y.ortho(THREE, R, 17.5);
  TXT.environment(R, { intensity: 0.5 });
  TXT.deckRig(R, Y.RIG, { target: [0, 0, 0], distance: 40, shadowFar: 120 });
  const pad = TXT.ground(R, { color: Y.PAD, size: 200, roughness: 0.96 });
  Y.padMap(THREE, pad, { repeat: 70 });
  const M = Y.mats(TXT);
  const amber = TXT.mat.clay(0xb8761c, { metalness: 0.1, roughness: 0.55 });
  const steel = TXT.mat.clay(0x6a6c70, { metalness: 0.3, roughness: 0.55 });

  /* TEN BY TEN, a 0.84 m plate at a 1.0 m pitch, filled row by row from the near edge so the ten
   * plain plates are the far row and the share reads as a fill level. */
  const N = 10, PITCH = 1.0;
  for (let k = 0; k < N * N; k++) {
    const r = Math.floor(k / N), c = k % N;
    const plate = Y.tile(THREE, 0.84, 0.18, 0.84, k < SHARE ? amber : steel);
    plate.position.set((c - (N - 1) / 2) * PITCH, 0.09, (N - 1) / 2 * PITCH - r * PITCH);
    TXT.add(R, plate);
  }
  TXT.frame(R, { from: [-24, 26, 34], look: [-0.6, 0, -2.2] });
""",
    after="""
  const put = (id, x, y) => { const e = document.getElementById(id); e.style.left = x + "px"; e.style.top = y + "px"; };
  put("l1", 620, 1000); put("f1", 620, 1062);
  put("l2", 80, 1010); put("f2", 80, 1072);
""",
    finish=', { aberration: 0 }',
))

# ---------------------------------------------------------------------------------------- 5
FRAMES.append(dict(
    n=5, layout="GRID", **DARK,
    note="""     FORTY SETS, COUNTABLE. Four columns by ten rows under a parallel camera from the key side,
     so every lit end reads and every cast falls the same way. The count is
     behind_the_meter.units from figures.json. No per unit rating anywhere: 76 over about 40 is a
     division no document performs.""",
    kicker="Behind the meter", kicker2="",
    src="c16 c17 c18   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:150px; width:920px; font-size:92px; }
  .dek  { left:82px; width:880px; font-size:28px; }""",
    html="""<h1 class="hook" id="hook">About forty, behind the meter</h1>
<p class="dek" data-follow="20">A gas compression company says it will supply one data center with 76 megawatts of behind-the-meter capacity from about 40 reciprocating gas engines.</p>
<div class="lab" id="l1" style="color:#DDE0E6">76 MW, behind the meter</div>""",
    fit="{ min: 72, max: 92, maxLines: 1 }",
    scene="""
  /* THE COUNT, FROM figures.json. behind_the_meter.units, read out of c17 by compute.py. */
  const UNITS = 40;
  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 175, 330], exposure: 1.0 });
  Y.ortho(THREE, R, 92);
  TXT.environment(R, { intensity: 0.45 });
  TXT.deckRig(R, Y.RIG, { target: [0, 0, 0], distance: 100, shadowFar: 240 });
  const pad = TXT.ground(R, { color: Y.PAD, size: 900, roughness: 0.96 });
  Y.padMap(THREE, pad, { repeat: 300 });
  const M = Y.mats(TXT);

  /* the walkways are wide enough that each set stands apart from its neighbours at thumb scale,
   * because a count a reader can't separate in the feed is not a count */
  const COLS = 4, PX = 16.8, PZ = 6.0;
  const ROWS = Math.ceil(UNITS / COLS);
  for (let k = 0; k < UNITS; k++) {
    const r = Math.floor(k / COLS), c = k % COLS;
    const g = Y.genset(THREE, M, { detail: true });
    g.position.set((c - (COLS - 1) / 2) * PX, 0, (ROWS - 1) / 2 * PZ - r * PZ);
    TXT.add(R, g);
  }
  /* high off the lit ends' corner of the block, so each set reads as a box with a lit end, a
   * door side and a stack, and the forty read as four columns of ten */
  TXT.frame(R, { from: [-130, 112, 100], look: [4, 12, -6] });
""",
    after="""
  const e = document.getElementById("l1");
  e.style.left = "80px"; e.style.top = "1170px";
""",
    finish='',
))

# ---------------------------------------------------------------------------------------- 6
FRAMES.append(dict(
    n=6, layout="FIGURE_SCALE", **DARK,
    note="""     THE SIZE OF THE THING. The hero, whole, with a person at its lit end, and the rest of the
     line behind it in the fog: one set in front and behind_the_meter.units less one receding, so
     the frame still holds the count.""",
    kicker="The size of the thing", kicker2="",
    src="c16 c17   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:952px; width:900px; font-size:96px; }
  .dek  { left:82px; width:820px; font-size:29px; }""",
    html="""<h1 class="hook" id="hook">This is one of them</h1>
<p class="dek" data-follow="20">A single set on its skid, and somebody who works on it.</p>""",
    fit="{ min: 78, max: 96, maxLines: 1 }",
    scene="""
  /* THE COUNT, FROM figures.json: one in front, and the rest of behind_the_meter.units behind. */
  const UNITS = 40;
  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 20, 130], exposure: 1.0, fov: 34 });
  TXT.environment(R, { intensity: 0.45 });
  TXT.deckRig(R, Y.RIG, { target: [0, 0, -20], distance: 90, shadowFar: 220 });
  const pad = TXT.ground(R, { color: Y.PAD, size: 400, roughness: 0.96 });
  Y.padMap(THREE, pad, { repeat: 120 });
  const M = Y.mats(TXT);

  const hero = Y.genset(THREE, M, {});
  TXT.add(R, hero);
  for (let i = 1; i < UNITS; i++) {
    const g = Y.genset(THREE, M, { detail: i < 3 });
    g.position.set(0, 0, -i * 4.6);
    TXT.add(R, g);
  }
  /* THE KIT of somebody who works on it: a steel toolbox on the pad, wheel chocks at the skid,
   * and a folding step at the first door. Each is sized in metres, so each is a second ruler. */
  const tool = Y.tile(THREE, 0.62, 0.34, 0.3, TXT.mat.clay(0x2f3a48, { metalness: 0.4, roughness: 0.4 }));
  tool.position.set(-8.2, 0.17, 2.2); tool.rotation.y = 0.4; TXT.add(R, tool);
  const handle = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.012, 8, 16, Math.PI), M.galv);
  handle.position.set(-8.2, 0.34, 2.2); handle.rotation.y = 0.4; TXT.add(R, handle);
  for (const cz of [1.5, -1.5]) {
    const chock = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.26, 3), M.skid);
    chock.rotation.z = Math.PI / 2; chock.position.set(-6.55, 0.12, cz); TXT.add(R, chock);
  }
  const step = new THREE.Group();
  for (const sx of [-0.2, 0.2]) { const leg = Y.tile(THREE, 0.04, 0.9, 0.04, M.galv); leg.position.set(sx, 0.45, 0); step.add(leg); }
  for (const sy of [0.3, 0.6, 0.88]) { const tread = Y.tile(THREE, 0.44, 0.03, 0.18, M.galv); tread.position.set(0, sy, 0.02); step.add(tread); }
  step.position.set(-4.25, 0, 1.7); TXT.add(R, step);

  /* THE PERSON, standing on the pad a step off the lit end of the hero, in the key. */
  const who = Y.person(THREE, { cloth: 0x3c4a5c });
  who.position.set(-7.3, 0, 1.1);
  who.rotation.y = -1.2;
  TXT.add(R, who);

  /* from off the lit end's corner, a little above standing eye, close enough that the person
   * reads, with the stacks leaving the top edge and the pad below holding the type */
  TXT.frame(R, { fov: 38, from: [-17.5, 2.4, 10.5], look: [-3.0, 1.15, -2.2] });
  Y.sky(THREE, R);
""",
    after="",
    finish=', { bloom: { threshold: 0.8, strength: 0.18, radius: 10 } }',
))

# ---------------------------------------------------------------------------------------- 7
FRAMES.append(dict(
    n=7, layout="DIAGRAM", **DARK,
    note="""     TWO RUNS OF DAYS AT ONE PITCH, standing on rails on the pad under a parallel camera so the
     runs compare by length. The first run is clocks.days_audit_to_halt plates, the second
     clocks.days_halt_to_report. The second run is amber, because it is the state's own clock:
     the days the agency has to answer on paper to the Governor's office.""",
    kicker="How long each step took", kicker2="",
    src="c9 c24 c4   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:150px; width:920px; font-size:88px; }
  .dek  { left:82px; width:860px; font-size:28px; }""",
    html="""<h1 class="hook" id="hook">Forty nine days, then twenty eight</h1>
<p class="dek" data-follow="20">The audit was ordered August 3rd. The directive came 49 days later. The agency answers to the Governor's office 28 days after that.</p>
<div class="lab" id="l1">August 3rd<br>audit ordered</div>
<div class="lab" id="l2">September 21st<br>halt directed</div>
<div class="lab" id="l3">By October 19th<br>agency answers</div>""",
    fit="{ min: 68, max: 88, maxLines: 2 }",
    scene="""
  /* THE SPANS, FROM figures.json. clocks.days_audit_to_halt and clocks.days_halt_to_report,
   * calendar differences computed by compute.py. */
  const FIRST = 49, SECOND = 28;
  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 60, 180], exposure: 1.0 });
  Y.ortho(THREE, R, 23);
  TXT.environment(R, { intensity: 0.5 });
  TXT.deckRig(R, Y.RIG, { target: [0, 0, 0], distance: 40, shadowFar: 120 });
  const pad = TXT.ground(R, { color: Y.PAD, size: 200, roughness: 0.96 });
  Y.padMap(THREE, pad, { repeat: 80 });
  const M = Y.mats(TXT);
  const plain = TXT.mat.clay(0xa9aba7, { metalness: 0.2, roughness: 0.5 });
  /* THE SECOND RUN IS THE STATE'S CLOCK, the twenty eight days the agency has to answer on paper,
   * so it wears the accent */
  const amber = Y.paperMat(THREE);

  /* ONE PITCH FOR BOTH RUNS, 0.4 m a day, left aligned, so 49 and 28 compare as lengths. Each
   * day stands as a plate 0.28 m wide and 1.1 m tall facing the key, so every day is a separate
   * lit thing. The runs lie along +Z, which is the frame's right under this camera. */
  const DAY = 0.4, Z0 = -9.8;
  const run = (n, x, mat, last) => {
    for (let d = 0; d < n; d++) {
      const p = Y.tile(THREE, 0.12, 2.0, 0.28, (last && d === n - 1) ? amber : mat);
      p.position.set(x, 1.12, Z0 + d * DAY + 0.14);
      TXT.add(R, p);
    }
  };
  /* a steel rail under each run, so a run is one thing standing on the pad and not dust */
  const rail = (n, x) => {
    const r = Y.tile(THREE, 0.5, 0.12, n * DAY + 0.2, M.skid);
    r.position.set(x, 0.06, Z0 + n * DAY / 2 - 0.02); TXT.add(R, r);
  };
  rail(FIRST, 3.4); rail(SECOND, -3.4);
  /* ONE SLAB UNDER BOTH RUNS, the concrete the hero stands on, so the two periods read as one
   * record laid on one surface rather than as two loose strips */
  const slab = Y.tile(THREE, 9.2, 0.08, FIRST * DAY + 1.0, M.conc);
  slab.position.set(0, 0.04, Z0 + FIRST * DAY / 2 - 0.02); TXT.add(R, slab);
  run(FIRST, 3.4, plain, false);
  run(SECOND, -3.4, amber, false);
  /* THE HERO in front of the runs, its door side to the light, cut by nothing: the deck's object
   * standing on the same pad the days are laid on */
  const hero = Y.genset(THREE, M, {});
  hero.rotation.y = -Math.PI / 2;
  hero.position.set(-17, 0, 3);
  TXT.add(R, hero);

  /* from the key side, a third of the way up, so the two runs stack one above the other */
  TXT.frame(R, { from: [-30, 20, 0], look: [2.2, 0.5, 0] });
""",
    after="""
  const p1 = Y.project(THREE, R, [3.4, 2.0, Z0]);
  const p2 = Y.project(THREE, R, [3.4, 2.0, Z0 + FIRST * DAY]);
  const p3 = Y.project(THREE, R, [-3.4, 2.0, Z0 + SECOND * DAY]);
  const put = (id, x, y) => { const e = document.getElementById(id); e.style.left = x + "px"; e.style.top = y + "px"; };
  put("l1", p1.x, p1.y - 74);
  put("l2", Math.min(p2.x - 210, 1000 - 270), p2.y - 74);
  put("l3", p3.x + 26, p3.y - 40);
""",
    finish=', { aberration: 0 }',
))

# ---------------------------------------------------------------------------------------- 8
FRAMES.append(dict(
    n=8, layout="SPLIT_HORIZON", **DARK,
    note="""     THE ENGINE ITSELF. The hero opened on its door side and turned into the deck's light, so the
     sixteen cylinder engine inside is lit: the thing c15's page is about. Behind it, the rest of
     behind_the_meter.units standing in the fog. The copy says only that the agency publishes an
     overview for engine operations and that nothing verified says whether these need one. c14's
     `typically` is never spent as `must`.""",
    kicker="The engine page", kicker2="",
    src="c15 c17   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:872px; width:920px; font-size:78px; }
  .dek  { left:82px; width:900px; font-size:27px; }""",
    html="""<h1 class="hook" id="hook">Engines have a page of their own</h1>
<p class="dek" data-follow="18">The agency publishes an "Overview of air permitting requirements and options for new internal combustion engine operations." Nothing verified says whether these engines need an air permit.</p>""",
    fit="{ min: 62, max: 78, maxLines: 2 }",
    scene="""
  /* THE COUNT, FROM figures.json. behind_the_meter.units: this one open, the rest behind it. */
  const UNITS = 40;
  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 24, 150], exposure: 1.0, fov: 36 });
  TXT.environment(R, { intensity: 0.55 });
  TXT.deckRig(R, Y.RIG, { target: [20, 0, 0], distance: 120, shadowFar: 280 });
  const pad = TXT.ground(R, { color: Y.PAD, size: 600, roughness: 0.96 });
  Y.padMap(THREE, pad, { repeat: 150 });
  const M = Y.mats(TXT);

  /* THE HERO, OPEN, turned a quarter so the open side looks down -X into the key and the
   * engine inside takes the lamp. */
  const hero = Y.genset(THREE, M, { open: true });
  hero.rotation.y = -Math.PI / 2;
  TXT.add(R, hero);
  /* the others, closed, in ranks behind it running away from the reader into the fog */
  for (let i = 1; i < UNITS; i++) {
    const g = Y.genset(THREE, M, { detail: false });
    g.rotation.y = -Math.PI / 2;
    g.position.set(6 + Math.floor((i - 1) / 3) * 8.5, 0, ((i - 1) % 3 - 1) * 14.5);
    TXT.add(R, g);
  }
  /* an inspection lamp on a stand at the opening, off, the engine lit by the deck's lamp alone */

  /* back and low off the open side, so the bay fills the top half and the pad holds the type */
  TXT.frame(R, { fov: 36, from: [-19, 1.3, 8], look: [0, 0.75, -2.6] });
  Y.sky(THREE, R);
""",
    after="",
    finish=', { bloom: { threshold: 0.8, strength: 0.18, radius: 10 } }',
))

# ---------------------------------------------------------------------------------------- 9
FRAMES.append(dict(
    n=9, layout="OBJECT_AND_CAPTION", **DARK,
    note="""     THE CLOSE. The hearing room with nobody in it: rows of folding chairs facing a table, and on
     the table the one amber sheet, the cancellation. Rendered under the deck's light like every
     other frame, so the room reads as the same world as the yard.""",
    kicker="Where a Texan could have spoken", kicker2="",
    src="c12 c13 c4   TEXAS AI DOCKET",
    css="""  .hook { left:80px; top:872px; width:920px; font-size:88px; }
  .dek  { left:82px; width:880px; font-size:27px; }
  .lab.note { left:82px; top:1150px; white-space:normal; width:840px; color:#C9CCD4; }""",
    html="""<h1 class="hook" id="hook">A hearing with no date</h1>
<p class="dek" data-follow="18">The agency canceled the notice and comment hearing on data center permit O4791, captioned to Vantage Data Centers TX11. It says the hearing will be rescheduled for a later date. Separately, TCEQ answers to the Governor's office by October 19th.</p>
<div class="lab note" id="l1">No date yet for the hearing.</div>""",
    fit="{ min: 70, max: 88, maxLines: 1 }",
    scene="""
  const R = TXT.setup(gl, { w: 1080, h: 1350, bg: Y.SKY, fog: [Y.FOG, 10, 34], exposure: 1.05, fov: 40 });
  TXT.environment(R, { intensity: 0.5 });
  TXT.deckRig(R, Y.RIG, { target: [0, 0, -2], distance: 30, shadowFar: 90 });
  const floor = TXT.ground(R, { color: 0x302b27, size: 120, roughness: 0.7 });
  Y.padMap(THREE, floor, { repeat: 50, tint: 0x3c424c });
  const M = Y.mats(TXT);
  /* the room's chairs are pale moulded seats on galvanised frames, so the empty rows are the lit
   * thing in a dark room, the way every set in the yard is */
  M.seat = TXT.mat.clay(0xa9acb1, { metalness: 0.05, roughness: 0.5 });

  /* SIX ROWS OF EIGHT, a narrow aisle down the middle, all facing the table. */
  for (let r = 0; r < 6; r++) for (let c = 0; c < 8; c++) {
    const ch = Y.chair(THREE, M);
    const x = (c - 3.5) * 0.58 + (c >= 4 ? 0.1 : -0.1);
    ch.position.set(x, 0, -r * 1.05);
    TXT.add(R, ch);
  }
  /* THE TABLE, and the one amber sheet on it: the cancellation, the state's paper. */
  const top = Y.tile(THREE, 2.6, 0.05, 0.8, TXT.mat.clay(0x5a4632, { roughness: 0.55 }));
  top.position.set(0, 0.74, 2.4); TXT.add(R, top);
  for (const [lx, lz] of [[-1.2, 2.1], [1.2, 2.1], [-1.2, 2.7], [1.2, 2.7]]) {
    const leg = Y.tile(THREE, 0.05, 0.72, 0.05, M.skid); leg.position.set(lx, 0.36, lz); TXT.add(R, leg);
  }
  const sheet = Y.tile(THREE, 0.22, 0.004, 0.28, Y.paperMat(THREE));
  sheet.position.set(0.3, 0.77, 2.35); sheet.rotation.y = 0.2; TXT.add(R, sheet);
  /* the cancellation, posted on the front of the table where the room would have read it */
  const notice = Y.tile(THREE, 0.62, 0.80, 0.004, Y.paperMat(THREE));
  notice.position.set(-0.55, 0.42, 1.99); TXT.add(R, notice, { cast: false });
  for (const cxp of [-0.6, 0.6]) {
    const ch = Y.chair(THREE, M); ch.position.set(cxp, 0, 3.2); ch.rotation.y = Math.PI; TXT.add(R, ch);
  }

  /* from the back of the room, raised, looking down the aisle to the table, so the rows fill the
   * top of the frame and the floor in front of them holds the caption */
  TXT.frame(R, { fov: 40, from: [0.3, 4.6, -12.5], look: [0.1, -2.3, 0.6] });
  Y.sky(THREE, R);
""",
    after="",
    finish='',
))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in FRAMES:
        extra = ""
        if 'class="lab' in f["html"]:
            extra += LAB_CSS.format(**f)
        if 'class="fig' in f["html"]:
            extra += FIG_CSS.format(**f)
        html = HEAD.format(extra_css=extra, **f)
        (OUT / f"slide-{f['n']:02d}.html").write_text(html, encoding="utf-8")
    print(f"wrote {len(FRAMES)} frames to {OUT}")


if __name__ == "__main__":
    main()
