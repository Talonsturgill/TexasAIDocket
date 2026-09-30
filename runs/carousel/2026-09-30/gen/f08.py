import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 36, near: 0.1, far: 4000 });
  /* THE DOOR. The school's covered walkway to its front entrance seen from the lawn to its south
   * east, the parent walking under it toward the doors, the flagpole beside the entry walk. The
   * walkway's line is read off the kit school's own layout: posts 88 m north of the field's desk. */
  const C = F.campus(K, THREE, TXT, R, { oaks: true });
  /* the covered entry walk the kit school's front lacks at its doors, built out from the vestibule */
  F.canopy(K, THREE, TXT, R, { from: [-9.5, -88.6], len: 15, w: 3.2 });
  const parent = F.parent(K, { pose: 'walk' });
  parent.position.set(-9.1, 0, -75.8); parent.rotation.y = Math.PI + 0.05; TXT.add(R, parent); TXT.contact(R, parent);
  const crape = K.make('crape_myrtle', { seed: 3 }); crape.position.set(-17, 0, -76); TXT.add(R, crape); TXT.contact(R, crape);
  const bus8 = K.make('school_bus', { seed: 9, stopArm: true }); bus8.position.set(14, 0, -70.5); bus8.rotation.y = Math.PI / 2; TXT.add(R, bus8); TXT.contact(R, bus8);
  for (let i = 0; i < 5; i++) { const sh = K.make('shrub', { seed: 20 + i }); sh.position.set(-27 + i * 3.4, 0, -85.6); TXT.add(R, sh); TXT.contact(R, sh); }
  TXT.frame(R, { from: [-5.2, 1.6, -56], look: [-9.9, 5.6, -89] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -88], distance: 50, shadowFar: 120, normalBias: 0.04 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 6000, seed: 23 });
  F.grass(TXT, R, { count: 5000, area: [-26, -84, 16, -50], avoid: [[-11.7, -92, -7.3, -72]], scale: [0.06, 0.12], seed: 29 });
  TXT.weather(R, { grime: 0.35 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.22, type: ['.hook', '.dek'] });
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(8)
shell.write(8, "Archetype OBJECT_AND_CAPTION. RENDERED through txthree.js in the deck's overcast world. The school's covered walkway to its front doors seen from the lawn, a parent walking under it toward the entrance.",
  k, h, b, s, scene, dek_css="width:740px;", fit=(84, 112, 2))
