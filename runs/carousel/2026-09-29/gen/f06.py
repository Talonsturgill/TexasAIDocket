import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('units', 'acres') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 50, near: 0.05, far: 12000 });
  /* THE MACHINE. One unit at full detail at the field's south-west corner, the camera at the pad's
   * edge looking north at its south face, the low sun from the west raking along the intake
   * louvres. Past its south-west corner on the left, the yellow gas riser and valve stand against
   * the pad, the field going back and the Franklin ridge under haze. */
''' + SITE + r'''
  const ux = -S.side / 2 + 20, uz = S.side / 2 - 8;
  const u = F.unit(K, { seed: 7 });
  u.position.set(ux, 0.15, uz); TXT.add(R, u); TXT.contact(R, u);
  const padM = new THREE.MeshStandardMaterial({ color: 0xffffff, map: K.tex('concrete'), roughness: 0.92 });
  const pad = TXT.roundedBox(9, 0.15, 4.6, 0.02, padM); pad.position.set(ux - 0.6, 0.075, uz); pad.receiveShadow = true; TXT.add(R, pad);
  /* the unit and the camera turn together by TURN about the unit's centre, so the low sun from the west rakes the south face at about thirty degrees instead of grazing it */
  const TURN = -0.5, rotP = (px, pz) => { const dx = px - ux, dz = pz - uz; return [ux + dx * Math.cos(TURN) + dz * Math.sin(TURN), uz - dx * Math.sin(TURN) + dz * Math.cos(TURN)]; };
  u.rotation.y = TURN; pad.rotation.y = TURN;
  const D = 8, cx0 = ux - 3.05 + 0.3 * 0.373 * D * 1.0, e = rotP(cx0, uz + 1.175 + D), l = rotP(cx0, uz + 1.175), EYE = [e[0], 1.5, e[1]];
  TXT.frame(R, { from: EYE, look: [l[0], 1.5 + D * Math.tan(12.2 * Math.PI / 180), l[1]] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [ux, 0, uz], distance: 60, shadowFar: 140, normalBias: 0.05 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.desert(TXT, R, { area: [ux - 90, uz - 60, ux + 30, uz + 30], avoid: [[ux - 7, uz - 5, ux + 7, uz + 5], [EYE[0] - 8, EYE[2] - 5, EYE[0] + 8, EYE[2] + 2]], scrub: 260, rock: 0, grass: 1600 });
  TXT.scatter(R, { kind: 'rock', count: 4000, area: [EYE[0] - 8, EYE[2] - 9, EYE[0] + 8, EYE[2] - 2], seed: 83, scale: [0.012, 0.04], colors: [0xa89c86, 0x8f8676, 0xb8ad98] });
  F.ridge(THREE, TXT, R, { x: -5600, peak: 820, seed: 29, length: 70000 });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 380, seed: 31 });
  TXT.weather(R, { grime: 0.35 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.34, floor: 0.3, floorH: 220 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.hook', '.dek']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(6)
shell.write(6, "Archetype CLOSE_CROP. RENDERED through txthree.js in the deck's goldenHour world. One modular gas generator at the pad's edge, cropped by the right edge, the low sun raking along its intake louvres, the yellow gas riser and valve past its corner against the field and the Franklin ridge.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:900px;", dek_css="width:916px;", fit=(84, 116, 2))
