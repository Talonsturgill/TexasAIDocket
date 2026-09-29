import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 34, near: 0.3, far: 12000 });
  const h = K.make('ranch_house', { seed: 12, material: 'brick', garage: 'right' });
  h.rotation.y = Math.PI / 2 + 0.25; h.position.set(0, 0, 0); TXT.add(R, h); TXT.contact(R, h);
  const yard = F.yard(K, THREE, TXT, { count: 813 });
  yard.position.set(900, 0, -500); TXT.add(R, yard);
  TXT.frame(R, { from: [-24, 1.6, 20], look: [10, 3.2, -6] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 120, shadowFar: 300 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.desert(TXT, R, { area: [-120, -200, 200, 60], avoid: [[-14, -14, 14, 14]] });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 420, seed: 31 });
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.0, floor: 0.3 });
  TXDECK.finish(cx);
'''
shell.write(4, "PROBE", "El Paso County", "Probe", "A probe of the world.", "DRAWN", scene)
