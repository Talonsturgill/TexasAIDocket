from common import page, write
caps = '''<div class="cap" id="capL"><b>LEANDER</b><span>Stopped September 4th. The city says it was "in response to community concerns."</span></div>
<div class="cap" id="capR"><b>COLLEGE STATION</b><span>Kept, 4 to 2. "You can't afford the number of cops it would take," says its police chief.</span></div>'''
css = '''  .cap { position:absolute; top:1004px; width:400px; font-size:29px; font-weight:600; line-height:1.3; color:#E6E7EA; z-index:11; }
  .cap b { display:block; font-family:"JetBrains Mono", monospace; font-weight:500; font-size:24px; letter-spacing:0.08em; color:#F2F1EC; margin-bottom:6px; }
  #capL { left:80px; } #capR { left:510px; width:490px; }'''
scene = r'''
  /* THE TURN, and the biggest the hero gets. Two identical plate readers 3.2 m apart on one
   * concrete curb at the edge of a street, seen square on from the apron in front of them at a
   * crouch, so each runs from the curb to panels just under the top edge. Both cameras aim west at
   * one height. The street runs behind them and the lit lamp stands across it, its head in clear
   * sky between the two poles. The plain concrete apron holds the hook and a caption under each
   * pole, with no lane marking anywhere under the type. */
  const R = PL.stage(TXT, gl, W, { fov: 46, near: 0.05, far: 4000, fog: 0.0016 });
  const zP = -5.2;
  PL.lane(K, R, TXT, [0, zP - 6.4], { length: 900, shoulder: 1.6 });
  const conc = K.mat('pl-apron', { color: 0x6a6b6e, roughness: 0.92 }), curbM = K.mat('pl-curb', { color: 0x8d8d89, roughness: 0.85 });
  const apron = new THREE.Mesh(new THREE.BoxGeometry(200, 0.06, 11), conc); apron.position.set(0, 0.03, zP + 5.3); TXT.add(R, apron, { cast: false });
  const grime = new THREE.Mesh(new THREE.BoxGeometry(200, 0.004, 0.3), K.mat('pl-grime', { color: 0x2a2a2c, roughness: 1 })); grime.position.set(0, 0.062, zP + 0.6); TXT.add(R, grime, { cast: false });
  const curb = new THREE.Mesh(new THREE.BoxGeometry(200, 0.16, 0.9), curbM); curb.position.set(0, 0.08, zP); TXT.add(R, curb);
  const left = PL.pole(K, { state: 'off', yaw: -Math.PI / 2, face: 0 });
  left.position.set(-1.6, 0.16, zP); TXT.add(R, left); TXT.contact(R, left, { opacity: 0.85 });
  const right = PL.pole(K, { state: 'on', yaw: -Math.PI / 2, face: 0 });
  right.position.set(1.6, 0.16, zP); TXT.add(R, right); TXT.contact(R, right, { opacity: 0.85 });
  PL.lamp(K, R, TXT, [-1.0, zP - 18], -2.4, { lit: 3.2, pool: 140, height: 7.5, haloSize: 0.9 });
  /* the lamp's own throw, a shadow casting spot from its head toward the camera, so each pole lays
   * a long shadow forward across the apron under its own council's caption */
  const throwL = new THREE.SpotLight(0xfff0d8, 260, 45, 0.55, 0.6, 2);
  throwL.position.set(-1.0, 7.1, zP - 18); throwL.target.position.set(0, 0, zP + 7); throwL.castShadow = true;
  throwL.shadow.mapSize.set(2048, 2048); throwL.shadow.bias = -0.0004; throwL.shadow.radius = 4;
  R.scene.add(throwL, throwL.target);
  for (let i = 0; i < 16; i++) {
    const kind = i % 3 === 1 ? 'ashe_juniper' : 'live_oak', tr = K.make(kind, { seed: 30 + i });
    tr.position.set(-157 + i * 20 + (i % 2) * 5, 0, -70 - (i % 3) * 12); TXT.add(R, tr); TXT.contact(R, tr);
  }
  TXT.frame(R, { from: [0, 1.0, zP + 10.2], look: [0, 0.93, zP] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, zP], distance: 40, shadowFar: 100, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: PL.VERGE, size: 6000, seed: 16 });
  TXT.scatter(R, { kind: 'grass', count: 26000, area: [-80, -60, 80, zP - 11.8], seed: 6, scale: [0.14, 0.3], colors: [0x9a9474, 0x8f8a6a, 0xa49c7a] });
  TXT.weather(R, { grime: 0.4 });
  const cx = PL.develop(await TXT.snapshot(R), gl);
'''
write(6, page(6, 'Archetype OBJECT_AND_CAPTION. RENDERED through txthree.js in the deck\'s blueHour world. THE TURN. Two identical plate readers on one parkway, square on and as large as the hero gets in the deck, the lit lamp off centre behind, the hook and a caption under each pole on the near asphalt.',
    'Same pole. Two councils.', '', 'Two answers', 'c21 c22 c23 c7', scene, hook_css='top:842px;', extra_css=css, extra_html=caps,
    fit='{ min: 80, max: 84, maxLines: 2 }',
    post="{ a: 0, veilH: 620, veil: 0.44, type: ['.kick', '.hook', '.cap'] }", drawn='{ poles: 2 }'))
