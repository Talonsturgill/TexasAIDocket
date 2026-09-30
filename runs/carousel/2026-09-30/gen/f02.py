import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('training_sample') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 36, near: 0.1, far: 4000 });
  /* HOW IT LEARNED. The school's football field south of the wing, covered goal line to goal line
   * with one desk per human scored field test answer the engine is programmed on for a question:
   * 60 rows down the field by 50 across. The count is exact and the render reports it. */
  const FF = F.footballField(THREE, TXT, R, { center: [6, -12] });
  const ROWS = 60, COLS = FIG.training_sample / ROWS, pz = FF.L / ROWS, px = FF.W / COLS;
  const field = F.field(K, THREE, TXT, { count: FIG.training_sample, cols: COLS, pitch: [px, pz], origin: [FF.west + px / 2, FF.south - pz / 2], lidGlow: true,
    near: (x, z) => z > FF.south - 7 && x < FF.west + 16 });
  TXT.add(R, field);
  if (field.userData.drawn !== FIG.training_sample) throw new Error('field drew ' + field.userData.drawn);
  const post = F.goalPost(K, THREE, TXT); post.position.set(6, 0, FF.south + FF.EZ + 0.4); window.__txEncodings = { training_sample: FIG.training_sample }; TXT.add(R, post); TXT.contact(R, post);
  F.campus(K, THREE, TXT, R, {});
  /* the field's own furniture: light poles down both sidelines and a chain link fence behind the
   * south end zone */
  [[-1, -14], [-1, -52], [1, -14], [1, -52]].forEach(([sd, z], i) => { const lp = K.make('streetlight', { height: 18, reach: 1.2, finish: 'galvanized' }); lp.position.set(6 + sd * (FF.W / 2 + 7), 0, z); lp.rotation.y = sd > 0 ? -Math.PI / 2 : Math.PI / 2; TXT.add(R, lp); TXT.contact(R, lp); });
  const endFence = K.make('chain_link_fence', { length: 64, height: 1.83 }); endFence.position.set(6, 0, FF.south + FF.EZ + 5.5); TXT.add(R, endFence);
  TXT.frame(R, { from: [-3, 13, FF.south + FF.EZ + 24], look: [7, 4.2, FF.north - 30] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [6, 0, -30], distance: 110, shadowFar: 260, normalBias: 0.05 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 6000, seed: 25 });
  TXT.weather(R, { grime: 0.3 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.22, type: ['.kick', '.count', '.hook', '.dek'], veil: 0.45, veilH: 220, dark: true });
  TXDECK.finish(cx);
  window.__txDrawn = { desks: field.userData.drawn, detailed: field.userData.detailed };
'''
DARKFOOT = '''  .tx-site, .src { color:#EEF0F0 !important; text-shadow:0 0 3px rgba(20,22,20,0.65), 0 1px 12px rgba(20,22,20,0.5) !important; }'''
k,h,b,s = shell.copy(2)
shell.write(2, "Archetype FULL_BLEED. RENDERED through txthree.js in the deck's overcast world. The school's football field covered goal line to goal line with one desk per human scored field test answer, seen from above the south end zone past the goal post, the school wing beyond.",
  k, h, b, s, scene, fit=(84, 116, 2), extra_css=DARKFOOT)
