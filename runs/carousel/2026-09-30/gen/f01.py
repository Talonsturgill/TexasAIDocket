import sys; sys.path.insert(0,'.'); import shell; from common import *
CAM = r'''
  /* THE HOME CAMERA, shared exactly by frames 1, 7 and 9: seated eye behind the desk's empty seat,
   * looking north over it to the laptop and past it to the school wing 92 m out. */
  const HOME = { from: [-0.9, 1.02, 3.3], look: [0.1, 1.8, -8] };
  const DESK = { at: [-0.45, -2.35], rotY: 0.55 };
'''
scene = CAM + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 34, near: 0.05, far: 4000 });
  /* THE COVER. One desk alone on the practice field, its laptop open and lit, the school wing,
   * its flags and the oaks soft in haze on the horizon. */
  const desk = F.desk(K, { seed: 7 }); desk.position.set(DESK.at[0], 0, DESK.at[1]); desk.rotation.y = DESK.rotY; TXT.add(R, desk); TXT.contact(R, desk);
  F.campus(K, THREE, TXT, R, { flagScale: 0.8 });
  /* the campus beyond the field: a school bus at the curb by the wing's west end, a pecan and a
   * bench at the practice field's edge */
  const bus1 = K.make('school_bus', { seed: 2, stopArm: false }); bus1.position.set(-30, 0, -70); bus1.rotation.y = Math.PI / 2; TXT.add(R, bus1); TXT.contact(R, bus1);
  const pecan1 = K.make('pecan', { seed: 8 }); pecan1.position.set(34, 0, -48); TXT.add(R, pecan1); TXT.contact(R, pecan1);
  const bench1 = K.make('bench', { length: 1.8 }); bench1.position.set(-7.5, 0, -14); bench1.rotation.y = 0.3; TXT.add(R, bench1); TXT.contact(R, bench1);
  TXT.frame(R, HOME);
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -2], distance: 40, shadowFar: 120, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 6000, seed: 21 });
  F.grass(TXT, R, { count: 14000, area: [-14, -40, 14, 3.5], avoid: [[-1.25, -3.15, 0.4, -1.55], [-2.2, 1.2, 2.4, 3.4]], scale: [0.06, 0.12] });
  TXT.weather(R, { grime: 0.35 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.22, type: ['.kick', '.count', '.hook', '.dek'], veil: 0.45, veilH: 420 });
  TXDECK.finish(cx);
  window.__txDrawn = { desks: 1 };
'''
k,h,b,s = shell.copy(1)
shell.write(1, "Archetype FULL_BLEED. RENDERED through txthree.js in the deck's overcast world. THE COVER. One student combo desk alone on a straw practice field, its laptop open and lit, seen from behind its empty seat at a seated eye, the school wing, flags and live oaks in haze on the horizon.",
  k, h, b, s, scene, hook_css="left:80px; top:132px; width:900px;", fit=(90, 104, 2))
