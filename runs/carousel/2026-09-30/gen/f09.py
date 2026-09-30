import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = CAM + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 34, near: 0.05, far: 4000 });
  /* THE CLOSE. Frame 1's desk and camera, and now the parent leans over it and reads the screen. */
  const desk = F.desk(K, { seed: 7 }); desk.position.set(DESK.at[0], 0, DESK.at[1]); desk.rotation.y = DESK.rotY; TXT.add(R, desk); TXT.contact(R, desk);
  /* the parent stands at the desk's side, leaning over it and reading the lit screen, the same
   * parent as frame 8 in her own shirt, not the accent the scorers wear */
  const parent = F.attend(K, { x: DESK.at[0], z: DESK.at[1], rotY: DESK.rotY }, { sit: false, side: 1, gap: 0.5, make: (pose) => F.parent(K, { pose }) })[0];
  /* she stands a step toward the seat, so she looks down onto the screen's face and never over the lid's back */
  { const c = Math.cos(DESK.rotY), s2 = Math.sin(DESK.rotY); parent.position.x += 0.1 * s2; parent.position.z += 0.1 * c;
    const lp = new THREE.Vector3(); desk.updateMatrixWorld(true); desk.userData.laptop.getWorldPosition(lp); parent.rotation.y = Math.atan2(lp.x - parent.position.x, lp.z - parent.position.z); }
  TXT.add(R, parent); TXT.contact(R, parent);
  F.campus(K, THREE, TXT, R, { flagScale: 0.8 });
  /* the same campus as frame 1, and a pickup the parent drove, parked on the field's edge road */
  const bus9 = K.make('school_bus', { seed: 2, stopArm: false }); bus9.position.set(-30, 0, -70); bus9.rotation.y = Math.PI / 2; TXT.add(R, bus9); TXT.contact(R, bus9);
  const truck9 = K.make('pickup', { seed: 7, color: 0x6a4b3a }); truck9.position.set(-11, 0, -26); truck9.rotation.y = 1.2; TXT.add(R, truck9); TXT.contact(R, truck9);
  const bench9 = K.make('bench', { length: 1.8 }); bench9.position.set(-7.5, 0, -14); bench9.rotation.y = 0.3; TXT.add(R, bench9); TXT.contact(R, bench9);
  TXT.frame(R, HOME);
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -2], distance: 40, shadowFar: 120, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 6000, seed: 21 });
  F.grass(TXT, R, { count: 14000, area: [-14, -40, 14, 3.5], avoid: [[-1.25, -3.15, 0.6, -1.2], [-2.2, 1.2, 2.4, 3.4]], scale: [0.06, 0.12] });
  TXT.weather(R, { grime: 0.35 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.22, type: ['.kick', '.count', '.hook', '.dek'] });
  TXDECK.finish(cx);
  window.__txDrawn = { desks: 1, readers: 1 };
'''
k,h,b,s = shell.copy(9)
shell.write(9, "Archetype FULL_BLEED. RENDERED through txthree.js in the deck's overcast world. THE CLOSE. Frame 1's desk and camera with the parent standing at its side, leaning over it and reading the screen.",
  k, h, b, s, scene, fit=(96, 128, 2))
