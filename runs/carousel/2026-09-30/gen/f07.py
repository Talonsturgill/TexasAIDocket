import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = CAM + figs('students_credited') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 34, near: 0.05, far: 4000 });
  /* THE TURN. Frame 1's field and camera, filled: one desk per student the agency said received
   * more credit, 425 across and the rows running north to the school's walk. Frame 1's own desk is
   * in the front row. The count is exact and the render reports it. */
  const COLS = 425, P = [1.1, 1.15];
  const field = F.field(K, THREE, TXT, { count: FIG.students_credited, cols: COLS, pitch: P, origin: [-212 * P[0] + DESK.at[0], DESK.at[1]], lidGlow: true, castShadow: false,
    near: (x, z) => Math.abs(x - DESK.at[0]) < 6 && z > DESK.at[1] - 9 });
  TXT.add(R, field);
  if (field.userData.drawn !== FIG.students_credited) throw new Error('field drew ' + field.userData.drawn);
  F.campus(K, THREE, TXT, R, { flag: false });
  /* one content expert rereading at a desk in the near rows, leaning over its lit screen, in the
   * accent that means a person is reading an answer */
  const ex = F.attend(K, { x: DESK.at[0] + P[0] * 2, z: DESK.at[1] - P[1] * 17, rotY: 0 }, { sit: false, side: -1, seed: 6 });
  ex.forEach((p) => { TXT.add(R, p); TXT.contact(R, p); });
  /* the buses at the curb along the wing, seen over the field, clear of the building's face */
  for (let i = 0; i < 2; i++) { const b = K.make('school_bus', { seed: 12 + i }); b.position.set(-30 + i * 13, 0, -70); b.rotation.y = Math.PI / 2; TXT.add(R, b); TXT.contact(R, b); }
  TXT.frame(R, { from: [HOME.from[0], 7.2, HOME.from[2]], look: [HOME.look[0], 5.4, HOME.look[2] - 40] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -6], distance: 50, shadowFar: 140, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 6000, seed: 21 });
  F.grass(TXT, R, { count: 6000, area: [-14, -2, 14, 4], scale: [0.06, 0.12] });
  TXT.weather(R, { grime: 0.35 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.24, type: ['.kick', '.count', '.hook', '.dek'], veil: 0.45, veilH: 220, dark: true });
  TXDECK.finish(cx);
  window.__txDrawn = { desks: field.userData.drawn, detailed: field.userData.detailed };
'''
DARKFOOT = '''  .tx-site, .src { color:#EEF0F0 !important; text-shadow:0 0 3px rgba(20,22,20,0.65), 0 1px 12px rgba(20,22,20,0.5) !important; }'''
k,h,b,s = shell.copy(7)
shell.write(7, "Archetype FULL_BLEED. RENDERED through txthree.js in the deck's overcast world. THE TURN. Frame 1's camera and field, filled with one desk per student credited in the fall review, rows running to the school, one content expert rereading at a desk in the near rows.",
  k, h, b, s, scene, fit=(84, 112, 2), extra_css=DARKFOOT)
