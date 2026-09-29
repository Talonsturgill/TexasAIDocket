import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('units', 'acres', 'units_per_group_max') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure * 1.12, tone: W.tone, fov: 34, near: 0.2, far: 12000 });
  /* ONE BLOCK AND A PERSON. A block of the record's larger group size on its pad at the field's
   * south edge, the step-up transformer at its east end, a resident at the pad's south-west corner
   * for the size. The camera stands south-west of it at eye height, the low sun over its left
   * shoulder, so every west end and every south face is lit. The yellow gas header runs out of the
   * right edge. */
''' + SITE + r'''
  const bz = S.side / 2 - 14, bx = -30;
  const blk = F.block(K, { units: FIG.units_per_group_max, seed: 6 });
  blk.position.set(bx, 0, bz); TXT.add(R, blk); TXT.contact(R, blk);
  const hdr = TXT.tube([[bx - 14, 0.55, bz - 2.9], [bx + 60, 0.55, bz - 2.9]], 0.14, K.mat('mgg-gasline', { color: 0xc9a227, roughness: 0.5, metalness: 0.3 }));
  hdr.castShadow = true; TXT.add(R, hdr);
  const who = K.make('person', { seed: 4, role: 'worker', pose: 'stand', hat: 'hard', vest: true });
  who.position.set(bx - 6.2, 0.0, bz + 5.2); who.rotation.y = -0.9; TXT.add(R, who); TXT.contact(R, who);
  const apron = TXT.roundedBox(34, 0.12, 5.0, 0.02, new THREE.MeshStandardMaterial({ color: 0xffffff, map: K.tex('concrete'), roughness: 0.92 }));
  apron.position.set(bx + 2, 0.06, bz + 6.0); apron.receiveShadow = true; TXT.add(R, apron);
  /* the block's own transformer stands behind its last unit from here, so it is moved to the pad's front corner where the lens sees it */
  blk.traverse(m => { if (m.isMesh && m.parent && m.parent !== blk && m.parent.userData && m.parent.userData.hvOut) m.visible = false; });
  const tx = K.make('padmount_transformer', { seed: 3 }); tx.rotation.y = -0.5; tx.position.set(bx + 11.4, 0.15, bz + 1.6); TXT.add(R, tx); TXT.contact(R, tx);
  TXT.frame(R, { from: [bx - 14, 1.2, bz + 12.5], look: [bx + 8, 1.2 + 26 * Math.tan(6.2 * Math.PI / 180), bz - 1] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [bx, 0, bz], distance: 120, shadowFar: 320, normalBias: 0.05 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.desert(TXT, R, { area: [bx - 70, bz + 6, bx + 60, bz + 60], avoid: [[bx - 24, bz + 3, bx + 20, bz + 9], [bx - 30, bz + 9, bx + 6, bz + 30]], scrub: 120, rock: 0, grass: 2600 });
  TXT.scatter(R, { kind: 'rock', count: 5000, area: [bx - 20, bz + 3.8, bx + 14, bz + 14], seed: 82, scale: [0.012, 0.04], colors: [0xa89c86, 0x8f8676, 0xb8ad98] });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 380, seed: 31 });
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45, floor: 0.45 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.hook', '.dek']);
  TXDECK.finish(cx);
  window.__txDrawn = { units: yard.userData.drawn + FIG.units_per_group_max };
'''
k,h,b,s = shell.copy(2)
shell.write(2, "Archetype FIGURE_SCALE. RENDERED through txthree.js in the deck's goldenHour world. One block of the record's larger group size on its pad with its step-up transformer, a worker at true scale at the pad corner, the field beyond.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:900px;", dek_css="width:860px;", fit=(84, 116, 2))
