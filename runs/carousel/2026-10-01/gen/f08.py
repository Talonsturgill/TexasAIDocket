from common import page, write, figs
scene = figs('laredo_cameras') + r'''
  /* PUT TO VOTERS, at the scale of frame 7. Laredo's laredo_cameras cameras, one pole each, fill
   * fifteen ranks of the same lot from the same lens, on caliche this time, where frame 7 filled
   * three. Mesquite at the far edge and the lamp where frame 7 had them. The type stays where frame 7
   * has it, so the two frames differ in the count and the ground alone. */
  const R = PL.stage(TXT, gl, W, { fov: 50, near: 0.5, far: 5000 });
  const drawn = PL.lot(K, THREE, TXT, R, FIG.laredo_cameras);
  PL.lane(K, R, TXT, [0, 33], { length: 700, gravel: 0x5f5a50 });
  PL.lamp(K, R, TXT, [-6.5, -14], 0.5, { lit: 3.2, pool: 120, height: 6.0 });
  for (let k = 0; k < 12; k++) {
    const m = K.make('mesquite', { seed: 50 + k, height: 5 + (k % 3) });
    m.position.set(-55 + k * 10 + (k % 2) * 3, 0, -76 - (k % 3) * 7); m.scale.setScalar(0.8); TXT.add(R, m); TXT.contact(R, m);
  }
  for (let x = -60; x < 60; x += 20) { const f = K.make('barbed_wire_fence', { length: 20 }); f.position.set(x + 10, 0, -64); TXT.add(R, f); }
  PL.lotView(TXT, R);
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -20], distance: 70, shadowFar: 160, normalBias: 0.04 });
  TXT.ground(R, { surface: 'caliche', color: 0xa89c86, size: 6000, seed: 23 });
  TXT.scatter(R, { kind: 'grass', count: 5000, area: [-60, -80, 60, 1], seed: 8, scale: [0.12, 0.24], colors: [0x9a8c6c, 0x8a7d62, 0xa89a78] });
  TXT.scatter(R, { kind: 'grass', count: 9000, area: [-24, -2, 24, 1], seed: 18, scale: [0.12, 0.26], colors: [0x9a8c6c, 0x8a7d62, 0xa89a78] });
  TXT.weather(R, { grime: 0.45 });
  const cx = PL.develop(await TXT.snapshot(R), gl);
'''
write(8, page(8, 'Archetype FULL_BLEED. RENDERED through txthree.js in the deck\'s blueHour world. PUT TO VOTERS. Laredo\'s 165 cameras as one plate reader each, fifteen ranks filling the lot frame 7 used, from the same lens, on caliche.',
    'Laredo will ask its voters.',
    'Its council voted 7 to 2 for a nonbinding referendum in May on spending $1 million a year to keep 165 cameras.',
    'Put to voters', 'c2 c3', scene, drawn='{ poles: drawn }'))
