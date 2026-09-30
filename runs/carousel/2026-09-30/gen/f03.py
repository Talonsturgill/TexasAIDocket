import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('per100_engine', 'per100_people') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 36, near: 0.1, far: 4000 });
  /* THE SHARE. A block of one hundred desks on the practice field, ten by ten. Two readers are at
   * per100_people of them, drawn as the far left five by five so one in four reads as a quarter,
   * and per100_engine stand alone with their screens lit. The counts are asserted. */
  const N = FIG.per100_engine + FIG.per100_people, P = 1.6, x0 = -7.2, z0 = -18;
  /* the attended share drawn as one quarter of the square, the far left five by five: the near
   * quarter swelled to half the block in perspective at thumb size, the far one reads as a quarter */
  const read = new Set(); for (let i = 0; i < N; i++) { const c = i % 10, r = Math.floor(i / 10); if (c < 5 && r >= 5) read.add(i); }
  const field = F.field(K, THREE, TXT, { count: N, cols: 10, pitch: [P, P], origin: [x0, z0], near: () => true });
  TXT.add(R, field);
  let readers = 0;
  /* two people at each attended desk, because a routed answer is read twice (c31): one seated at
   * the screen and one leaning in at its side, both turned to it */
  field.userData.units.forEach(([x, z], i) => {
    if (!read.has(i)) return;
    F.attend(K, { x, z, rotY: 0 }, { seed: 30 + i * 2, side: i % 2 ? 1 : -1, detail: z < z0 - 1 ? 'low' : 'full' })
      .forEach((p) => { TXT.add(R, p); TXT.contact(R, p); readers++; });
  });
  if (read.size !== FIG.per100_people || field.userData.drawn - read.size !== FIG.per100_engine) throw new Error('split drawn wrong');
  F.campus(K, THREE, TXT, R, {});
  /* the school's drive beside the wing: a pickup and two sedans parked on it, shrubs along the front */
  const drive = K.make('road', { length: 40, lanes: 2, sidewalk: true }); drive.position.set(-22, 0, -76.5); TXT.add(R, drive);
  [['pickup', 0x7a7f86, -31], ['sedan', 0x8e2f2a, -24], ['sedan', 0xc9ccd0, -17.5]].forEach(([m, c, x], i) => { const v = K.make(m, { seed: 5 + i, color: c }); v.position.set(x, 0, -75.4); v.rotation.y = Math.PI / 2; TXT.add(R, v); TXT.contact(R, v); });
  for (let i = 0; i < 6; i++) { const sh = K.make('shrub', { seed: 3 + i }); sh.position.set(-16 + i * 6.5, 0, -84.6); TXT.add(R, sh); TXT.contact(R, sh); }
  TXT.frame(R, { from: [3, 7.5, 13], look: [-0.5, 6.3, -40] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -25], distance: 60, shadowFar: 140, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 6000, seed: 27 });
  F.grass(TXT, R, { count: 8000, area: [-16, -40, 16, 4], scale: [0.07, 0.14], seed: 31 });
  TXT.weather(R, { grime: 0.35 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.24, type: ['.kick', '.count', '.hook', '.dek'] });
  TXDECK.finish(cx);
  window.__txDrawn = { desks: field.userData.drawn, withReaders: read.size, alone: field.userData.drawn - read.size, readers: readers };
'''
k,h,b,s = shell.copy(3)
shell.write(3, "Archetype FIGURE_SCALE. RENDERED through txthree.js in the deck's overcast world. A block of one hundred desks on the practice field, ten by ten, two readers in bluebonnet at a seeded quarter of them, the rest alone with screens lit, the school wing beyond.",
  k, h, b, s, scene, fit=(80, 104, 2))
