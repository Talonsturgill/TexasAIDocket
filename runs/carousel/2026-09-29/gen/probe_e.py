import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 32, near: 0.3, far: 12000 });
  const blk = F.block(K, { units: 5 });
  blk.position.set(0, 0, 0); TXT.add(R, blk); TXT.contact(R, blk);
  const yard = F.yard(K, THREE, TXT, { count: 813 });
  yard.position.set(-60, 0, -150); TXT.add(R, yard);
  TXT.frame(R, { from: [-34, 2.0, 16], look: [40, 7, -30] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 120, shadowFar: 400 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.desert(TXT, R, { grass: 9000, area: [-300, -500, 200, 60], avoid: [[-20, -8, 20, 8], [-160, -260, 40, -40]] });
  const rg = F.ridge(THREE, TXT, R, {}); rg.geometry.computeBoundingBox(); console.error('DBG ridge', JSON.stringify(rg.geometry.boundingBox), JSON.stringify(rg.position));
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.0, floor: 0.3 });
  TXDECK.finish(cx);
  console.error('DBG fog', JSON.stringify(W.fogDensity), R.scene.fog && R.scene.fog.density, 'haze', W.haze, 'ridge', F.ridge.toString().length);
  document.title = 'drawn ' + yard.userData.drawn + ' blocks ' + yard.userData.blocks;
'''
shell.write(2, "PROBE", "El Paso County", "Probe frame", "A probe of the world.", "DRAWN", scene)
