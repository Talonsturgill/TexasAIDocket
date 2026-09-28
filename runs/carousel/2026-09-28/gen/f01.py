import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 30 });

  /* the station at the origin on its pad, heads splayed across the plain. The camera stands 38 m
   * south and 6 m west, low, so the mast lands on the right third and rises past the dek into the
   * dark deck, with the sun (az -68) on the left rear and every cast running right. */
  const hero = F.station(K, { pan: [0.95, -2.35], tilt: [-0.06, -0.1] });
  TXT.add(R, hero); TXT.contact(R, hero);
  TXT.frame(R, { from: [-5, 2.2, 30], look: [-3.6, 5.4, 0] });   /* a longer lens from the same spot, so the two heads read as cameras at feed size (round 1) */
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 90, shadowFar: 260 });

  /* the pad, graded caliche 7 m square, a hair proud of the grass */
  const padM = new THREE.MeshStandardMaterial({ color: 0xd9ccb0, map: K.tex('concrete'), roughness: 0.96 });
  const pad = TXT.roundedBox(7, 0.06, 7, 0.02, padM); pad.position.set(0, 0.03, 0); TXT.add(R, pad);
  /* the caliche road from the bottom right of the frame to the pad, curving */
  const road = K.make('caliche_road', { seed: 5, length: 60, curve: 0.12 });
  road.position.set(1.5 + 30 * Math.sin(0.1), 0, 3.5 + 30 * Math.cos(0.1)); road.rotation.y = 0.1;   /* round 2: turned toward the lens so it leaves by the bottom right */ TXT.add(R, road);
  /* a four strand barbed wire fence across the near left, the scale a reader measures the mast by */
  const fence = K.make('barbed_wire_fence', { seed: 4, length: 18, strands: 4, spacing: 3.4 });
  fence.position.set(-17, 0, 14); fence.rotation.y = 0.3;   /* round 2: its brace stood in line with the mast */ TXT.add(R, fence);
  /* the country: straw pasture, scrub on the rise, the caprock far out on the left */
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 7000, seed: 11 });
  F.grass(TXT, R, { count: 26000, area: [-90, -260, 90, 36], avoid: [[-4, -4, 4, 4], [0, 2, 16, 64]] });
  /* round 2: the breaks sit 400 m out, where the thinned haze still carries a silhouette */
  F.caprock(K, TXT, R, { x: -260, z: -390, width: 460, height: 24, ry: 0.15 });
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(1)
shell.write(1,
  "Archetype FULL_BLEED. RENDERED through txthree.js in the deck's declared stormFront world. THE COVER. The hero wildfire camera station on its caliche pad, 30 m out, its two heads splayed to the plain under the storm deck, a caliche road leading to it across cured straw grass.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:700px;", dek_css="width:640px;", fit=(92, 124, 3))
