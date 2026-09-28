import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  /* The kind of pole the Smokehouse Creek fire started at, standing and whole: the kit's 40 ft class
   * distribution pole, weathered hard, its down guy and yellow guard beside it. The camera is low
   * at 0.9 m, 5 m off the pole on its sunlit side, so the pole rises out of the top edge on the
   * right with its lit face toward the lens. The station is left out of this one frame: at any
   * distance the type allows it was a hairline behind the dek (round 1).
   * Nothing here is broken, burnt or smoking: the record describes no break. */
  /* PANEL ROUND 3 RECOMPOSE. The trunk was named in round 1 and round 2 and the pole top in round 3,
   * each time at detail scale, where the kit's pole is a primitive. So the frame steps back to the
   * distance where the kit holds: a three phase distribution line of the kit's own 40 ft class poles
   * crossing the plain away from the lens, the nearest 26 m out on the right third, the kind of line
   * the Smokehouse Creek fire started at, standing and whole under the storm deck. */
  const AZ = -0.0886;                                  /* the line's own bearing, the crossarms square across it */
  const line = K.make('power_line', { structure: 'utility_pole', structures: [[3.6, 4, AZ], [7.6, -41, AZ], [11.6, -86, AZ], [15.6, -131, AZ], [19.6, -176, AZ]],
                                      transformer: false, guy: false, insulators: 'porcelain', seed: 8 });
  TXT.add(R, line); TXT.contact(R, line);
  TXT.frame(R, { from: [-2, 1.5, 30], look: [-2, 4.6, 0] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 60, shadowFar: 200 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 7000, seed: 31 });
  F.grass(TXT, R, { count: 34000, area: [-60, -220, 60, 28], avoid: [], scale: [0.7, 1.4] });
  const fence = K.make('barbed_wire_fence', { seed: 11, length: 60, strands: 4, spacing: 3.6 });
  fence.position.set(14, 0, -16); fence.rotation.y = -0.5; TXT.add(R, fence);
  F.caprock(K, TXT, R, { x: -250, z: -380, width: 420, height: 20, ry: 0.2 });
  TXT.weather(R, { grime: 1.0, height: 2.5 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45, floor: 0.45, floorH: 330 });   /* round 2: the gold blades and the pole's edge go to one value under the footer */
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(2)
shell.write(2,
  "Archetype FULL_BLEED. RENDERED through txthree.js in the deck's declared stormFront world. The kind of line the Smokehouse Creek fire started at, standing and whole: a three phase distribution line of 40 ft class wood poles crossing the plain away from the lens under the storm deck, the caprock breaks in the haze.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:700px;", dek_css="width:630px;", fit=(84, 112, 3))
