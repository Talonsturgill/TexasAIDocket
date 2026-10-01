from common import page, write
labels_html = '''<svg id="lead" width="1080" height="1350" style="position:absolute;left:0;top:0;z-index:9;pointer-events:none"></svg>
<div class="lab" id="l1">solar-powered</div>
<div class="lab" id="l2">LTE-connected</div>
<div class="lab" id="l3">the rear of passing vehicles</div>
<div class="lab" id="l4">make, model, and color</div>'''
css = '''  .lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; letter-spacing:0.03em; color:#F2F1EC; white-space:nowrap; z-index:11; }'''
scene = r'''
  /* THE THING ITSELF, in side view and close. The pole stands on the south parkway of a road
   * running east and west, its camera aimed west down the near lane, its panels facing south as
   * Texas installs face. A sedan a few metres down the lane shows the side the camera photographs,
   * its rear. The lit cobra head stands behind and left, where the declared key is. Four leaders
   * land on the parts the city's own words name, each label clear of the art it names. */
  const R = PL.stage(TXT, gl, W, { fov: 34, near: 0.05, far: 4000 });
  PL.road(K, R, TXT, [-200, -5.6], { length: 900, lanes: 2, sidewalk: false, parkway: 2.0 });
  const pole = PL.pole(K, { yaw: -Math.PI / 2, face: 0, tilt: 0.12 });
  pole.position.set(0, 0, 0); TXT.add(R, pole); TXT.contact(R, pole, { opacity: 0.8 });
  const car = K.make('sedan', { seed: 6, color: 0x5d636c, metallic: true });
  car.position.set(-4.8, 0, -7.4); car.rotation.y = -Math.PI / 2; TXT.add(R, car); TXT.contact(R, car);
  PL.lamp(K, R, TXT, [-14.6, -27.5], 0.5, { lit: 3.4, pool: 80, height: 8.0 });
  /* College Station's town line down the far shoulder, the deck's one accent, small */
  const sign = PL.sign(K, R, TXT, [-3.8, -14], 0.35, 0.6, 0x22c060);
  sign.traverse((m) => { if (m.isMesh) m.castShadow = false; });
  PL.trees(K, R, TXT, [[-120, -70, 'live_oak', 3], [-70, -95, 'ashe_juniper', 4], [-30, -120, 'ashe_juniper', 9], [40, -110, 'live_oak', 5], [90, -80, 'ashe_juniper', 6], [-180, -60, 'mesquite', 7]]);
  for (let x = -160; x < 160; x += 20) { const f = K.make('barbed_wire_fence', { length: 20 }); f.position.set(x + 10, 0, -16); TXT.add(R, f); }
  TXT.frame(R, { from: [1.4, 1.7, 17.5], look: [-0.9, 3.3, 0] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 40, shadowFar: 120, normalBias: 0.04 });
  TXT.ground(R, { surface: 'caliche', color: PL.CALICHE, size: 6000, seed: 12 });
  TXT.scatter(R, { kind: 'grass', count: 7000, area: [-80, -14, 80, 8], avoid: [[-0.8, -0.8, 0.8, 0.8]], seed: 5, scale: [0.14, 0.28], colors: [0x8a7d62, 0x7a7058, 0x9a8c6c] });
  TXT.weather(R, { grime: 0.45 });
  /* the leaders, each landing on the part it names through this frame's own camera */
  const H = 12 * 0.3048, pr = (p) => PL.project(THREE, R, p);
  const parts = {
    l1: pr([0.45, H + 0.3, 0.1]),
    l2: pr([pole.userData.puck.x, pole.userData.puck.y, pole.userData.puck.z]),
    l3: pr([-4.8 + 2.42, 0.8, -7.4]),
    l4: pr([-4.8 + 0.2, 0.75, -7.4 + 0.95])
  };
  const svg = document.getElementById('lead'), leaders = [];
  const lay = (id, x, y, side) => {
    const el = document.getElementById(id); el.style.left = x + 'px'; el.style.top = y + 'px';
    if (side === 'right') el.style.left = (x - el.getBoundingClientRect().width) + 'px';
    const b = el.getBoundingClientRect();
    const from = side === 'left' ? [b.left - 12, b.top + b.height / 2] : side === 'right' ? [b.right + 12, b.top + b.height / 2] : side === 'down' ? [b.left + 30, b.top - 12] : side === 'up' ? [b.right - 40, b.bottom + 10] : [b.right + 12, b.top + b.height / 2];
    const at = parts[id], line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    line.setAttribute('points', from.join(',') + ' ' + at.join(','));
    line.setAttribute('fill', 'none'); line.setAttribute('stroke', '#F2F1EC'); line.setAttribute('stroke-width', '2');
    svg.appendChild(line);
    const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    dot.setAttribute('cx', at[0]); dot.setAttribute('cy', at[1]); dot.setAttribute('r', '5'); dot.setAttribute('fill', '#F2F1EC');
    svg.appendChild(dot);
    leaders.push({ target: id, at: at, to: at });
  };
  lay('l1', parts.l1[0] + 70, parts.l1[1] - 14, 'left');
  lay('l2', parts.l2[0] - 70, parts.l2[1] - 14, 'right');
  lay('l3', 90, parts.l3[1] - 300, 'up');
  lay('l4', 90, parts.l4[1] + 110, 'down');
  window.__txLeaders = leaders;
  const cx = PL.develop(await TXT.snapshot(R), gl);
'''
write(2, page(2, 'Archetype DIAGRAM. RENDERED through txthree.js in the deck\'s blueHour world. HOW IT WORKS. The same plate reader close in side view, panels facing south, camera aimed west down the lane at the rear of a passing sedan, the lit lamp behind, four leaders in the city\'s own words.',
    'It runs on sunlight and a cell signal.',
    'College Station says the camera photographs the rear of passing vehicles by day and by night. It sorts each one by make, model and color so the data can be searched.',
    'How it works', 'c25 c26', scene, extra_css=css, extra_html=labels_html, fit='{ min: 96, max: 104, maxLines: 2 }', hook_css='line-height:1.04;', dek_css='width:920px;',
    post="{ a: 0.45, fade: 360, type: ['.kick', '.hook', '.dek', '.lab'] }", drawn='{ poles: 1, signs: 1 }'))
