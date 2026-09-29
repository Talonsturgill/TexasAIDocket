import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('units', 'acres', 'service_life_years') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 0.55], exposure: W.exposure, tone: W.tone, fov: 30, near: 0.5, far: 12000 });
  /* THE PAD FROM 90 M UP. The whole field of units on a pad whose area is the record's acreage,
   * the data hall immediately north of it, the year fence bare along the west edge, the desert out
   * to the eastern range. The camera stands south-west and high, the sun at its back. */
''' + SITE + r'''
  const dc = K.make('data_center', { seed: 4, length: 260, gensets: 0, fence: true });
  dc.position.set(S.hall[0], 0, S.hall[2]); TXT.add(R, dc); TXT.contact(R, dc);
  const yf = F.yearFence(K, THREE, TXT, { spans: FIG.service_life_years, paid: 0 });
  yf.rotation.y = Math.PI / 2; yf.position.set(S.fence[0], 0, 18); TXT.add(R, yf);
  TXT.frame(R, { from: [-233, 40, 258], look: [30, 34, -120] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 320, shadowFar: 800, normalBias: 0.05 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.desert(TXT, R, { area: [-S.side / 2 - 260, -S.side / 2 - 300, S.side / 2 + 260, S.side / 2 + 260], avoid: [[-S.side / 2 - 2, -S.side / 2 - 140, S.side / 2 + 2, S.side / 2 + 2], [-360, 150, -110, 380]], scrub: 2600, rock: 0, grass: 0, scale: [0.35, 0.7] });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 380, seed: 31 });
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45, floor: 0.3 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.hook', '.dek']);
  TXDECK.finish(cx);
  window.__txDrawn = { units: yard.userData.drawn };
'''
k,h,b,s = shell.copy(3)
shell.write(3, "Archetype GRID. RENDERED through txthree.js in the deck's goldenHour world. The whole field from 90 m up on a pad whose area is the record's acreage, the data hall immediately north, the year fence bare along the west edge.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:900px;", dek_css="width:790px;", fit=(78, 104, 2),
  extra_css="  .dek { text-shadow:0 0 4px rgba(12,12,14,0.55), 0 1px 16px rgba(12,12,14,0.42); }")
