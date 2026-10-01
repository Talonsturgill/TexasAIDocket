from common import page, write, figs
scene = figs('jurisdictions_off_min') + r'''
  /* ONE TOWN LINE PER CITY OR COUNTY THAT SWITCHED THEM OFF. A rural two lane road running west
   * into the seam, seen from 2.5 m over the left lane and turned a little toward the right
   * shoulder. jurisdictions_off_min green town limit signs stand on that shoulder, each 1.26 times
   * further than the last, so each clears the one behind it. The nearest plate reader, switched
   * off, stands large on the same shoulder in the right foreground, its base in the near third. */
  const R = PL.stage(TXT, gl, W, { fov: 36, near: 0.05, far: 5000 });
  PL.lane(K, R, TXT, [-440, 0], { length: 1000, wheelPaths: false, asphalt: 0x252b2c });
  let drawn = 0;
  for (let i = 0; i < FIG.jurisdictions_off_min; i++) {
    const sg = PL.sign(K, R, TXT, [-26 * Math.pow(1.26, i), -7.5], Math.PI / 2, 1.0);
    sg.traverse((m) => { if (m.isMesh) m.castShadow = false; });   /* contact only, no hard cast shadow */
    drawn++;
  }
  const pole = PL.pole(K, { state: 'off', yaw: -Math.PI / 2, face: Math.PI / 2 });
  pole.position.set(-12, 0, -4.1); TXT.add(R, pole); TXT.contact(R, pole, { opacity: 0.8 });
  PL.lamp(K, R, TXT, [-70, 6.6], 0.5, { lit: 2.8, pool: 70 });
  PL.lamp(K, R, TXT, [-190, 6.6], 0.5, { lit: 2.4 });
  for (let x = -600; x < 0; x += 20) { const f = K.make('barbed_wire_fence', { length: 20 }); f.position.set(x + 10, 0, 11.5); TXT.add(R, f); }
  PL.trees(K, R, TXT, [[-700, -160, 'live_oak', 3, 12], [-820, -60, 'ashe_juniper', 4, 10], [-640, 90, 'live_oak', 5, 12], [-900, 140, 'ashe_juniper', 6, 11], [-420, -95, 'mesquite', 7, 7], [-300, 60, 'ashe_juniper', 8, 8], [-160, -40, 'mesquite', 9, 6], [-520, 30, 'live_oak', 10, 12]], { contact: false });
  TXT.scatter(R, { kind: 'grass', count: 6000, area: [-40, -9.5, 6, -6.2], seed: 23, scale: [0.18, 0.36], colors: [0x9a8c6c, 0x8a7d62, 0xa89a78] });
  TXT.scatter(R, { kind: 'grass', count: 6000, area: [-40, 6.2, 6, 9.5], seed: 24, scale: [0.18, 0.36], colors: [0x9a8c6c, 0x8a7d62, 0xa89a78] });
  TXT.scatter(R, { kind: 'grass', count: 22000, area: [-420, -60, 6, -6.2], avoid: [[-13.2, -5.3, -10.8, -2.9]], seed: 21, scale: [0.12, 0.26], colors: [0x9a8c6c, 0x8a7d62, 0xa89a78] });
  TXT.scatter(R, { kind: 'grass', count: 16000, area: [-420, 6.2, 6, 60], seed: 22, scale: [0.12, 0.26], colors: [0x9a8c6c, 0x8a7d62, 0xa89a78] });
  TXT.frame(R, { from: [0, 2.8, 1.8], look: [-100, 6.9, -25.0] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [-30, 0, -4], distance: 60, shadowFar: 180, normalBias: 0.04 });
  TXT.ground(R, { surface: 'caliche', color: PL.CALICHE, size: 9000, seed: 14 });
  TXT.weather(R, { grime: 0.4 });
  const cx = PL.develop(await TXT.snapshot(R), gl);
'''
write(4, page(4, 'Archetype SPLIT_HORIZON. RENDERED through txthree.js in the deck\'s blueHour world. AFTER THE PAUSE. A rural two lane road running into the seam, one green town limit sign per city or county the reporting counts on the right shoulder, the nearest plate reader dark in the right foreground.',
    'At least 14 cities and counties shut cameras off.',
    'More than 900 Flock cameras went dark after the state money was rescinded in late August. Plano, Robinson and Kendall County ended their contracts.',
    'After the pause', 'c1 c5', scene, fit='{ min: 80, max: 92, maxLines: 2 }', drawn='{ signs: drawn, poles: 1 }'))
