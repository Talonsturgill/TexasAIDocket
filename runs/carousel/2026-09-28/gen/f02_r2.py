import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  /* The kind of pole the Smokehouse Creek fire started at, standing and whole: the kit's 40 ft class
   * distribution pole, weathered hard, its down guy and yellow guard beside it. The camera is low
   * at 0.9 m, 5 m off the pole on its sunlit side, so the pole rises out of the top edge on the
   * right with its lit face toward the lens. The station is left out of this one frame: at any
   * distance the type allows it was a hairline behind the dek (round 1).
   * Nothing here is broken, burnt or smoking: the record describes no break. */
  const pole = K.make('utility_pole', { seed: 8, height: 10.7, transformer: true, guy: true, guyDir: 1, insulators: 'porcelain' });
  pole.position.set(0, 0, 0); pole.rotation.y = 0.5; TXT.add(R, pole); TXT.contact(R, pole);
  /* round 2: creosote gone silver, matte, so the pole reads as weathered wood and not satin */
  pole.traverse((m) => { if (m.isMesh && m.material && m.material.map && m.material.color && m.geometry && m.geometry.boundingSphere == null) m.geometry.computeBoundingSphere(); if (m.isMesh && m.material && m.material.map && m.geometry.boundingSphere && m.geometry.boundingSphere.radius > 3) { m.material = new THREE.MeshStandardMaterial({ color: 0x6f675c, roughness: 0.93, metalness: 0 });   /* panel round 1: the grain texture's full height streaks read as a curtain, so the trunk is plain weathered wood and its age is in the checks, tag and bolt */ if ('clearcoat' in m.material) m.material.clearcoat = 0; if ('sheen' in m.material) m.material.sheen = 0; } });
  /* AGE AT DETAIL SCALE (round 1): the close crop is where age shows, so the face toward the lens
   * carries drying checks, the long splits a treated pine pole opens as it weathers, and the
   * aluminium tag and the through bolt every pole carries at eye height. */
  (function () {
    const az = Math.atan2(-1.68, 1.26), rad = (y) => 0.15 + (0.105 - 0.15) * y / 10.7;
    const crack = new THREE.MeshStandardMaterial({ color: 0x241f1a, roughness: 0.95 });
    [[-0.5, 0.3, 1.1], [-0.22, 1.5, 2.3], [0.06, 0.2, 0.8], [0.3, 2.2, 3.1], [0.48, 0.9, 1.6], [-0.08, 3.2, 3.8]]   /* round 2: short staggered splits, never full height */.forEach(function (c) {
      const a = az + c[0], y0 = c[1], y1 = c[2], r0 = rad((y0 + y1) / 2);
      const m = new THREE.Mesh(new THREE.BoxGeometry(0.007, y1 - y0, 0.012), crack);
      m.position.set(Math.sin(a) * (r0 - 0.002), (y0 + y1) / 2, Math.cos(a) * (r0 - 0.002)); m.rotation.y = a; TXT.add(R, m);
    });
    const tagM = new THREE.MeshStandardMaterial({ color: 0xe6e7e3, roughness: 0.4, metalness: 0.2, emissive: 0x2a2a28 });
    const a = az + 0.18, r1 = rad(1.6);
    const tag = TXT.roundedBox(0.075, 0.105, 0.004, 0.004, tagM); tag.position.set(Math.sin(a) * (r1 + 0.002), 1.6, Math.cos(a) * (r1 + 0.002)); tag.rotation.y = a; TXT.add(R, tag);
    const bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.03, 8), new THREE.MeshStandardMaterial({ color: 0x5b5a55, roughness: 0.6, metalness: 0.7 }));
    const b2 = az - 0.25, r2 = rad(2.3); bolt.rotation.x = Math.PI / 2; bolt.rotation.y = b2;
    const bg = new THREE.Group(); bg.position.set(Math.sin(b2) * r2, 2.3, Math.cos(b2) * r2); bg.rotation.y = b2; bolt.rotation.set(Math.PI / 2, 0, 0); bg.add(bolt); TXT.add(R, bg);
  })();
  /* the line it carries runs off to the east, one more pole in the grass */
  const pole2 = K.make('utility_pole', { seed: 9, height: 10.7, transformer: false, guy: false, insulators: 'porcelain' });
  pole2.position.set(40, 0, -30); pole2.rotation.y = 0.5; TXT.add(R, pole2); TXT.contact(R, pole2);

  TXT.frame(R, { from: [-1.68, 1.0, 1.26], look: [-1.68 + 30 * Math.sin(0.70), 3.9, 1.26 - 30 * Math.cos(0.70)] });   /* 2.1 m off the pole, so its face fills the right quarter and bleeds the edge (round 1) */
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 60, shadowFar: 200 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 7000, seed: 31 });
  F.grass(TXT, R, { count: 34000, area: [-40, -220, 60, 10], avoid: [[-0.6, -0.6, 0.6, 0.6]], scale: [0.7, 1.4] });
  const fence = K.make('barbed_wire_fence', { seed: 11, length: 60, strands: 4, spacing: 3.6 });
  fence.position.set(14, 0, -16); fence.rotation.y = -0.5; TXT.add(R, fence);
  F.caprock(K, TXT, R, { x: 900, z: -2400, width: 1300, height: 70, ry: -0.2 });
  TXT.weather(R, { grime: 1.0, height: 2.5 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45, floor: 0.45, floorH: 330 });   /* round 2: the gold blades and the pole's edge go to one value under the footer */
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(2)
shell.write(2,
  "Archetype CLOSE_CROP. RENDERED through txthree.js in the deck's declared stormFront world. The kind of pole the Smokehouse Creek fire started at, standing and whole: a weathered 40 ft class distribution pole cropped close from a low eye, its guy wire and guard beside it, and a second pole down the line.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:740px;", dek_css="width:700px;", fit=(84, 112, 3))
