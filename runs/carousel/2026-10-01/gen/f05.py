from common import page, write, figs
scene = figs('el_paso_days') + r'''
  /* UNDER THE CLOCK. No claim reports a camera taken down and the revised terms are unpublished,
   * so the plate reader still stands, whole, on its four bolt footing at the shoulder of a far west
   * road at blue hour. A broken ridge of tan rock holds the horizon behind it, which places it in
   * the Trans-Pecos, and the lit lamp stands across the road on the key side. A grade rod beside it
   * carries the 60 days in bands, the clock the item carried as filed. */
  const R = PL.stage(TXT, gl, W, { fov: 50, near: 0.05, far: 14000 });
  const pole = PL.pole(K, { yaw: -Math.PI / 2, face: 0, seed: 7 }); pole.position.set(0, 0, 0); TXT.add(R, pole); TXT.contact(R, pole, { opacity: 0.85 });
  /* a grade rod beside it painted in el_paso_days bands of 5 cm, black and white with a red mark
   * at every tenth, the clock the item carried as filed, counted in the art */
  const rod = new THREE.Group(), bw = 0.05;
  const red = K.mat('rod-red', { color: 0xb8352a, roughness: 0.5 }), wht = K.mat('rod-wht', { color: 0xe8e6df, roughness: 0.5 }), blk = K.mat('rod-blk', { color: 0x141414, roughness: 0.5 });
  let bands = 0;
  for (let i = 0; i < FIG.el_paso_days; i++) {
    const tenth = (i + 1) % 10 === 0, b = TXT.roundedBox(0.085, tenth ? bw : bw - 0.004, 0.085, 0.004, tenth ? red : (i % 2 ? wht : blk));
    b.position.set(0, 0.03 + i * bw + bw / 2, 0); rod.add(b); bands++;
  }
  rod.position.set(-1.4, 0, 0.6); rod.rotation.z = 0.02; TXT.add(R, rod); TXT.contact(R, rod, { opacity: 0.8 });
  PL.lane(K, R, TXT, [-200, -6.2], { length: 1200, shoulder: 2.0, gravel: 0x7a6e5e });
  PL.lamp(K, R, TXT, [-9, -12], 0.5, { lit: 3.2, pool: 120, height: 7.0 });
  [[-2600, -7200, 1100, 300], [-1500, -7600, 900, 360], [-500, -7000, 1000, 260], [500, -7800, 1200, 330], [1500, -7300, 900, 240]].forEach((q, i) => {
    const r = K.make('mesa', { kind: 'butte', width: q[2], height: q[3], rock: 'tan', seed: 40 + i }); r.position.set(q[0], 0, q[1]); TXT.add(R, r, { cast: false });
  });
  PL.trees(K, R, TXT, [[-60, -40, 'mesquite', 3], [40, -55, 'mesquite', 4], [-130, -70, 'mesquite', 5], [90, -35, 'mesquite', 6], [-25, -30, 'mesquite', 8]]);
  TXT.frame(R, { from: [1.6, 1.6, 8.4], look: [-1.5, 0.5, -2] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 30, shadowFar: 80, normalBias: 0.04 });
  TXT.ground(R, { surface: 'caliche', color: 0x9a8c74, size: 12000, seed: 15 });
  TXT.scatter(R, { kind: 'grass', count: 6000, area: [-40, -30, 40, -1.0], avoid: [[-1, -1, 1, 1]], seed: 11, scale: [0.12, 0.26], colors: [0x9a8c6c, 0x8a7d62, 0xa89a78] });
  TXT.scatter(R, { kind: 'grass', count: 3000, area: [-8, -1.0, 8, 6], avoid: [[-1, -1, 1, 1]], seed: 16, scale: [0.08, 0.16], colors: [0x8f826c, 0x9a8c74, 0xa39579] });
  TXT.weather(R, { grime: 0.45 });
  const cx = PL.develop(await TXT.snapshot(R), gl);
'''
write(5, page(5, 'Archetype FIGURE_SCALE. RENDERED through txthree.js in the deck\'s blueHour world. UNDER THE CLOCK. The plate reader still standing whole on its footing at the shoulder of a far west road, a broken tan ridge on the horizon, the lit lamp across the road. The type sits at the foot.',
    'El Paso voted on a 60 day clock.',
    'As filed, the item called for removing every Flock fixed camera under city control within 60 days. The council passed it as revised on September 15th.',
    'El Paso', 'c32', scene, hook_css='top:842px; width:700px;', dek_css='width:920px;', fit='{ min: 88, max: 104, maxLines: 2 }',
    post="{ a: 0.4, to: 130, fade: 120, veilH: 480, veil: 0.42 }", drawn='{ poles: 1, bands: bands }'))
