import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 30, near: 0.3, far: 12000 });
  const yard = F.yard(K, THREE, TXT, { count: 813 });
  yard.position.set(40, 0, 0); TXT.add(R, yard);
  const dc = K.make('data_center', { seed: 4, length: 260, gensets: 0, fence: true });
  dc.position.set(40, 0, -170); TXT.add(R, dc); TXT.contact(R, dc);
  TXT.frame(R, { from: [-150, 22, 150], look: [60, 0, -60] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [40, 0, -60], distance: 400, shadowFar: 900 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.desert(TXT, R, { area: [-300, -500, 300, 300], avoid: [[-120, -300, 200, 90]] });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 420, seed: 31 });
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.0, floor: 0.3 });
  TXDECK.finish(cx);
  console.error('DBG yard', JSON.stringify(yard.userData.extent), yard.userData.drawn, JSON.stringify(dc.userData.size));
'''
shell.write(3, "PROBE", "El Paso County", "Probe", "A probe of the world.", "DRAWN", scene)
