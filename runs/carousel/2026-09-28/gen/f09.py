import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  /* The station at the origin. The camera stands on the caliche road 67 m south and 14 m west of
   * the mast, the road running away up the rise to its pad. A Texan stands on the left verge 11 m
   * out, and a pasture fence runs from the near right up beside the road to the mast, the leading
   * line of the frame. The sun (az -68) is behind the lens's left shoulder, so the figure is lit on
   * the side the lens sees and every cast runs right and away. */
  const CAM = [-9, 1.6, 36];   /* 37 m from the mast, so its two heads read facing the lens at feed size (round 1) */
  const toCam = Math.atan2(CAM[0], CAM[2]);                /* a head's +z turned toward the lens */
  const CAMERAS_PER_SITE = 2;   /* THE DATA: the site's two heads, both turned to the lens */
  const hero = F.station(K, { pan: Array(CAMERAS_PER_SITE).fill(toCam), tilt: Array(CAMERAS_PER_SITE).fill(-0.04) });
  TXT.add(R, hero); TXT.contact(R, hero);
  const dir = [Math.sin(0.2094), -Math.cos(0.2094)], rt = [-dir[1], dir[0]];   /* 12 degrees right of north, and its right hand */
  TXT.frame(R, { from: CAM, look: [CAM[0] + 60 * Math.sin(0.06), 6.5, CAM[2] - 60 * Math.cos(0.06)] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [-8, 0, 32], distance: 120, shadowFar: 320 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 7000, seed: 19 });
  const padM = new THREE.MeshStandardMaterial({ color: 0xd9ccb0, map: K.tex('concrete'), roughness: 0.96 });
  const pad = TXT.roundedBox(6, 0.06, 6, 0.02, padM); pad.position.set(0, 0.03, 0); TXT.add(R, pad);

  /* the road from frame 1 arrives here, from behind the lens up to the pad */
  const rd = Math.atan2(-dir[0], -dir[1]);
  const road = K.make('caliche_road', { seed: 9, length: 76, curve: 0.06 });
  road.position.set(CAM[0] + dir[0] * 30, 0, CAM[2] + dir[1] * 30); road.rotation.y = rd; TXT.add(R, road);

  /* A pasture fence 3.4 m left of the road from 13 m out, behind the figure, to the mast, one T-post every
   * 1.9 m of its drawn length. It carries no figure (panel round 3: the copy no longer states one). */
  /* THE GATE (round 1): a galvanized pipe ranch gate closed across the road 9.5 m out, the Texan
   * standing at it, and the fence of 30 T-posts leaving its hinge side for the mast. */
  const G = [CAM[0] + dir[0] * 9.5, CAM[2] + dir[1] * 9.5];
  const gate = K.make('ranch_gate', { seed: 3, fence: true });
  gate.position.set(G[0], 0, G[1]); gate.rotation.y = Math.atan2(-rt[1], rt[0]); TXT.add(R, gate); TXT.contact(R, gate);
  const POSTS = 30, SP = 1.9, L = 5 + (POSTS - 1) * SP;
  const A = [G[0] - rt[0] * 7.2, G[1] - rt[1] * 7.2], B = [-3.2, -2.5];   /* round 2: the fence ends at the pad behind the mast */
  const dx = B[0] - A[0], dz = B[1] - A[1], len = Math.hypot(dx, dz);
  const fence = K.make('barbed_wire_fence', { seed: 6, length: L, strands: 4, spacing: SP });
  fence.position.set(A[0] + dx / 2, 0, A[1] + dz / 2);
  fence.rotation.y = Math.atan2(-dz, dx);
  fence.scale.x = len / L;
  TXT.add(R, fence);

  /* a Texan on the left verge, three quarter toward the lens */
  const who = K.make('person', { seed: 14, role: 'resident', pose: 'look_up', hat: 'cowboy' });   /* panel round 1: turned up the road toward the mast, so the frame reads a Texan looking at the machine and not a mannequin's face */   /* round 2: the cap shaded the face the frame is about */
  who.position.set(CAM[0] - 0.9, 0, CAM[2] - 8.6); who.rotation.y = Math.PI + 0.35; TXT.add(R, who); TXT.contact(R, who);

  F.grass(TXT, R, { count: 34000, area: [-70, -120, 40, 76], avoid: [[-12, 8, -2, 40], [-3, -3, 3, 3]], scale: [0.6, 1.2] });
  F.caprock(K, TXT, R, { x: -230, z: -380, width: 420, height: 12, ry: -0.3 });   /* round 2: in the thinned haze */
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45, floor: 0.45, floorH: 520 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(9)
shell.write(9,
  "Archetype FIGURE_SCALE. RENDERED through txthree.js in the deck's declared stormFront world. The close: a Texan at a pipe gate on the caliche road below the station, a barbed wire fence running from the gate up the rise to the mast, whose two heads face the lens.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:700px;", dek_css="width:680px;")
