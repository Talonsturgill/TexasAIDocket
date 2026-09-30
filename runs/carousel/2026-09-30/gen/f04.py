import sys; sys.path.insert(0,'.'); import shell; from common import *
LAB = '''  .lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:25px; font-weight:500; letter-spacing:0.05em; color:#1E2028; z-index:12; white-space:nowrap; text-shadow:0 0 3px rgba(240,242,242,0.6), 0 1px 10px rgba(240,242,242,0.45); }
  svg#lead { position:absolute; left:0; top:0; width:1080px; height:1350px; z-index:11; overflow:visible; }'''
HTML = '<svg id="lead" width="1080" height="1350" viewBox="0 0 1080 1350"></svg>\n<div class="lab" id="l1">LOW CONFIDENCE</div>\n<div class="lab" id="l2">CONDITION CODE</div>\n<div class="lab" id="l3">RANDOM SAMPLE</div>\n'
scene = figs('per4_engine', 'per4_people') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 42, near: 0.05, far: 4000 });
  /* THE HANDOFF, explained. A row of four desks from a standing eye: per4_engine alone and
   * per4_people with two readers at it, and three labels on leaders naming what sends an answer to
   * people. The leaders land on the readers' desk top, projected through this frame's camera. */
  const n = FIG.per4_engine + FIG.per4_people, xs = [], z = -5;
  let lastDesk = null;
  for (let i = 0; i < n; i++) { const d = F.desk(K, { seed: 40 + i }); const x = -3.1 + i * 1.5; d.position.set(x, 0, z); TXT.add(R, d); TXT.contact(R, d); xs.push(x); lastDesk = d; }
  const xr = xs[n - 1];
  /* the handed-off answer is read twice: one reader in the seat at the screen, one leaning in at its side */
  const pair = F.attend(K, { x: xr, z, rotY: 0 }, { seed: 51, side: 1 });
  pair.forEach((p) => { TXT.add(R, p); TXT.contact(R, p); });
  F.campus(K, THREE, TXT, R, {});
  /* a bus at the far curb */
  const bus4 = K.make('school_bus', { seed: 6 }); bus4.position.set(24, 0, -72); bus4.rotation.y = -Math.PI / 2; TXT.add(R, bus4); TXT.contact(R, bus4);
  TXT.frame(R, { from: [5.7, 2.15, 3.4], look: [-1.2, 2.95, -7.2] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -5], distance: 40, shadowFar: 120, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 6000, seed: 21 });
  F.grass(TXT, R, { count: 12000, area: [-12, -30, 12, 3], avoid: [[-3.7, -5.9, 3.0, -4.1]], scale: [0.07, 0.14], seed: 33 });
  TXT.weather(R, { grime: 0.35 });
  const lpw = new THREE.Vector3(); lastDesk.updateMatrixWorld(true); lastDesk.userData.laptop.getWorldPosition(lpw);
  const SITE = F.project(THREE, R, [lpw.x, lpw.y + 0.12, lpw.z]);
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.22, type: ['.kick', '.count', '.hook', '.dek'] });
  TXDECK.finish(cx);
  /* the labels sit in the sky band under the dek as a list of alternatives, any one of which
   * sends an answer to people: a bracket gathers them and ONE leader drops to the readers' screen */
  const dk = document.querySelector('.dek').getBoundingClientRect(), top0 = dk.bottom + 12, svg = document.getElementById('lead'), leaders = [];
  const line = (pts) => { const pl = document.createElementNS('http://www.w3.org/2000/svg', 'polyline'); pl.setAttribute('points', pts.map(p => p.join(',')).join(' ')); pl.setAttribute('fill', 'none'); pl.setAttribute('stroke', '#1E2028'); pl.setAttribute('stroke-width', '2'); svg.appendChild(pl); };
  let right = 0; const mids = [];
  ['l1', 'l2', 'l3'].forEach((id, i) => {
    const el = document.getElementById(id); el.style.left = '600px'; el.style.top = (top0 + i * 42) + 'px';
    const r = el.getBoundingClientRect(); right = Math.max(right, r.right); mids.push(r.top + r.height / 2);
  });
  const bx = right + 14, by = (mids[0] + mids[2]) / 2;
  mids.forEach((y) => line([[bx - 8, y], [bx, y]]));
  line([[bx, mids[0]], [bx, mids[2]]]);
  const to = [SITE[0], SITE[1] - 6];
  line([[bx, by], [bx + 18, by], to]);
  const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle'); c.setAttribute('cx', to[0]); c.setAttribute('cy', to[1]); c.setAttribute('r', '4'); c.setAttribute('fill', '#1E2028'); svg.appendChild(c);
  leaders.push({ target: "the readers' screen", at: to, to: to });
  window.__txLeaders = leaders;
  window.__txDrawn = { desks: n, withReaders: FIG.per4_people };
'''
k,h,b,s = shell.copy(4)
shell.write(4, "Archetype DIAGRAM. RENDERED through txthree.js in the deck's overcast world. A row of four desks on the practice field from a standing eye off the row's end, one reader in bluebonnet seated at the fourth and one leaning in at its side, three mono labels gathered by a bracket, one leader landing on its screen.",
  k, h, b, s, scene, fit=(84, 112, 2), extra_css=LAB, extra_html=HTML)
