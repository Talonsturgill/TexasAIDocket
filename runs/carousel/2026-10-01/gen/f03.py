from common import page, write, figs
scene = figs('cameras_funded_min') + r'''
  /* ONE POLE PER CAMERA THE FEE BOUGHT. cameras_funded_min poles in forty files and eighty ranks
   * at six metres on a fall pasture, the ranks running west into the seam. The camera stands raised
   * at 4.5 m, twelve metres short of the first rank, above the panels, so every pole shows its post
   * and footing, the near rank fills the lower third and the panels stay under the dek. It looks
   * down an aisle that sits left of centre. A juniper and live oak line closes the pasture past the
   * last rank, under the seam. */
  const R = PL.stage(TXT, gl, W, { fov: 40, near: 0.1, far: 5000, fog: 0.0018 });
  const field = PL.field(K, THREE, TXT, {
    count: FIG.cameras_funded_min, cols: 40, pitch: [6, 6], origin: [-117, 0], yaw: -Math.PI / 2, face: 0,
    near: (x, z) => z > -13 && Math.abs(x) < 40
  });
  field.rotation.y = Math.PI / 2;          /* local -z runs west, into the seam */
  TXT.add(R, field);
  const drawn = field.userData.drawn;
  /* the pasture fence at the far end of the ranks */
  for (let z = -150; z < 150; z += 20) { const f = K.make('barbed_wire_fence', { length: 20 }); f.rotation.y = Math.PI / 2; f.position.set(-480, 0, z + 10); TXT.add(R, f); }
  PL.lamp(K, R, TXT, [-50, 22], 0.5, { lit: 3.2, pool: 90, haloSize: 1.8, height: 5.0 });
  /* the tree line that closes the pasture, under the seam */
  const line = [];
  for (let i = 0; i < 46; i++) line.push([-540 - ((i * 5) % 7) * 6, -300 + i * 14 + ((i * 7) % 5) * 3, (i * 3) % 5 < 2 ? 'ashe_juniper' : 'live_oak', 60 + (i * 7) % 46, 12 + ((i * 3) % 5) * 1.0]);
  PL.trees(K, R, TXT, line, { contact: false });
  TXT.frame(R, { from: [12, 4.5, 6], look: [-188, -7.7, 36] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [-20, 0, 0], distance: 80, shadowFar: 200, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: 0x8a8466, size: 8000, seed: 19 });
  TXT.scatter(R, { kind: 'grass', count: 9000, area: [-140, -70, 7.4, 80], seed: 9, scale: [0.2, 0.45], colors: [0xc8bc92, 0xb8ac84, 0xa89c78] });
  TXT.scatter(R, { kind: 'grass', count: 2500, area: [7.6, -40, 12, 50], seed: 10, scale: [0.2, 0.4], colors: [0xc8bc92, 0xb8ac84] });
  TXT.weather(R, { grime: 0.35 });
  const cx = PL.develop(await TXT.snapshot(R), gl);
'''
write(3, page(3, 'Archetype FULL_BLEED. RENDERED through txthree.js in the deck\'s blueHour world. THE DOLLAR AS A SIZE. One plate reader per camera the fee bought, forty files by eighty ranks on a fall pasture, seen from a raised eye just short of the first rank.',
    'One dollar. At least 3,200 cameras.',
    'A Tribune analysis found the Motor Vehicle Crime Prevention Authority put at least $30 million of the fee toward the state\'s Flock network.',
    'What the fee bought', 'c15 c16 c17', scene, post='{ a: 0.42 }', drawn='{ poles: drawn }'))
