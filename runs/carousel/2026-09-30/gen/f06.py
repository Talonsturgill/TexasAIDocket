import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('per1000_improved') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 36, near: 0.1, far: 4000 });
  /* THE FALL REVIEW, from frame 3's camera. The same lawn now holds one thousand desks, one per
   * exam, and the screens of per1000_improved of them are lit, the share of exams reviewed that
   * improved, drawn per thousand and placed by a seeded draw. The counts are asserted. */
  const COLS = 40, ROWS = 25, N = COLS * ROWS, P = 1.45, x0 = -(COLS - 1) * P / 2, z0 = -16;
  const field = F.field(K, THREE, TXT, { count: N, cols: COLS, pitch: [P, P], origin: [x0, z0], lidGlow: false, screen: 'off', castShadow: false,
    near: (x, z) => z > z0 - 4 && Math.abs(x) < 9 });
  TXT.add(R, field);
  const rng = TX.rng(20260930 + 6), picked = new Set();
  while (picked.size < FIG.per1000_improved) { const i = Math.floor(rng() * N); const c = i % COLS, r = Math.floor(i / COLS); if (r >= 3 && r < 13 && Math.abs(c - COLS / 2) < 9) picked.add(i); }
  /* the review's content experts reread the typed answers on every exam. The share that
   * improved is drawn as the experts whose rereading raised a score: a person in the accent seated
   * at the screen, which is lit, while every other screen is dark. All seventeen stand inside the
   * frame's middle rows so the count can be read in the pixels. */
  let improved = 0;
  const lit = new THREE.MeshBasicMaterial({ color: 0xf4f8fb }); lit.color.multiplyScalar(2.2);
  field.userData.units.forEach(([x, z], i) => {
    if (!picked.has(i)) return;
    const sc = new THREE.Mesh(new THREE.PlaneGeometry(0.29, 0.19), lit); sc.position.set(x + 0.04, 0.865, z - 0.284); TXT.add(R, sc);
    F.attend(K, { x, z, rotY: 0 }, { seed: 80 + i % 23, detail: 'low' }).forEach((p) => { TXT.add(R, p); TXT.contact(R, p); });
    improved++;
  });
  if (field.userData.drawn !== N || improved !== FIG.per1000_improved) throw new Error('drawn wrong');
  F.campus(K, THREE, TXT, R, {});
  TXT.frame(R, { from: [3, 7.5, 13], look: [-0.5, 6.3, -40] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -30], distance: 80, shadowFar: 180, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 6000, seed: 27 });
  F.grass(TXT, R, { count: 6000, area: [-16, -14, 16, 10], scale: [0.06, 0.12], seed: 39 });
  TXT.weather(R, { grime: 0.35 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.22, type: ['.kick', '.count', '.hook', '.dek'] });
  TXDECK.finish(cx);
  window.__txDrawn = { desks: field.userData.drawn, improved: improved };
'''
k,h,b,s = shell.copy(6)
shell.write(6, "Archetype SPLIT_HORIZON. RENDERED through txthree.js in the deck's overcast world. Frame 3's camera on the practice field, now one thousand desks, one per exam, every screen dark but the share of them that improved, lit, a content expert in bluebonnet seated at each.",
  k, h, b, s, scene, fit=(84, 112, 2))
