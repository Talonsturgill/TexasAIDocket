import sys, json; sys.path.insert(0,'.'); import shell
FIG = json.load(open('/home/user/TexasAIDocket/out/2026-09-29/figures.json'))
scene = r'''
  const FIG = ''' + json.dumps({k: FIG[k]['value'] for k in ('units', 'acres', 'service_life_years')}) + r''';
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 0.38], exposure: W.exposure * 0.8, tone: W.tone, fov: 42, near: 0.3, far: 12000 });
  /* LAST LIGHT, INTO THE SUN. The camera stands on the shoulder of the public road east of the pad
   * and looks west over the field toward the Franklin ridge, where the sun is going down behind the
   * crest. The rows go to silhouette with lit seams, the year fence stands painted across the pad's
   * east edge as a dark banded line, and a wire fence on the public side recedes on the right. The
   * field stands at the pad's east edge in this frame so its nearest rows are close enough to read. */
  const S = F.site(FIG.acres);
  const yard = F.yard(K, THREE, TXT, { count: FIG.units });
  const ex = yard.userData.extent;
  yard.position.set(S.side / 2 - 40 - ex[0] / 2, 0, 0); TXT.add(R, yard);
  F.pad(K, THREE, TXT, R, S.side);
  const C = [S.side / 2 + 26, 3.2, 18], LK = [S.side / 2 + 26 - 346, 218];
  const dd = Math.hypot(LK[0] - C[0], LK[1] - C[2]), h = [(LK[0] - C[0]) / dd, (LK[1] - C[2]) / dd], r = [-h[1], h[0]];
  const along = (a, lat) => [C[0] + a * h[0] + lat * r[0], C[2] + a * h[1] + lat * r[1]];
  const yawTo = (v) => Math.atan2(-v[1], v[0]);
  /* the year fence across the pad's edge, all twenty panels painted, perpendicular to the view */
  const yf = F.yearFence(K, THREE, TXT, { spans: FIG.service_life_years, paid: FIG.service_life_years, spacing: 1.8, postH: 2.2 });
  { const p = along(52, -22); yf.position.set(p[0], 0, p[1]); yf.rotation.y = yawTo(r); } TXT.add(R, yf); TXT.contact(R, yf);
  /* the public road: asphalt to the left of the lens with a painted edge line, the shoulder under it */
  { const asphalt = new THREE.MeshStandardMaterial({ color: 0x3a3a3c, roughness: 0.96, map: K.tex('concrete') });
    const road = new THREE.Mesh(new THREE.PlaneGeometry(7.2, 260), asphalt); road.rotation.x = -Math.PI / 2; road.rotation.z = -yawTo(h) + Math.PI / 2;
    const p = along(120, -4.4); road.position.set(p[0], 0.015, p[1]); road.receiveShadow = true; TXT.add(R, road);
    const line = new THREE.Mesh(new THREE.PlaneGeometry(0.14, 260), new THREE.MeshStandardMaterial({ color: 0xe8e4da, roughness: 0.7 })); line.rotation.x = -Math.PI / 2; line.rotation.z = road.rotation.z;
    const q = along(120, -1.0); line.position.set(q[0], 0.02, q[1]); TXT.add(R, line); }
  /* the public side's wire fence: galvanised posts set in the ground, a top rail, a tension wire and
   * three strands on angled arms, receding along the right of the frame. No mesh texture: at this
   * distance a mesh only moires */
  { const g = new THREE.Group(), galv = K.finish.galvanized(), wire = K.mat('cl-wire', { color: 0xb9bcbf, roughness: 0.35, metalness: 0.8 });
    const n = 22, sp = 3.0, lat = 3.0;
    for (let i = 0; i < n; i++) { const a = 12 + i * sp; K.cyl(0.024, 0.024, 1.85, galv, a, 0, 0, 10, g);
      K.bar([a, 1.85, 0], [a, 2.2, -0.3], 0.012, galv, 6, g); }
    K.bar([12, 1.8, 0], [12 + (n - 1) * sp, 1.8, 0], 0.02, galv, 8, g);
    K.bar([12, 0.08, 0], [12 + (n - 1) * sp, 0.08, 0], 0.006, wire, 5, g);
    [1.95, 2.07, 2.19].forEach((y, k) => K.bar([12, y, -0.1 * (k + 0.5)], [12 + (n - 1) * sp, y, -0.1 * (k + 0.5)], 0.006, wire, 5, g));
    g.traverse(m => { if (m.isMesh) m.castShadow = true; });
    const p = along(0, lat); g.position.set(p[0], 0, p[1]); g.rotation.y = yawTo(h); TXT.add(R, g); }
  TXT.frame(R, { from: C, look: [LK[0], C[1] + dd * Math.tan(3.6 * Math.PI / 180), LK[1]] });
  TXT.sky(R);
  /* the sun stands just out of frame to the right over the thin band of the ridge, so the rows take the last light edge on and the ground runs warm to the lens */
  const rig = TXT.deckRig(R, W.rig, { target: [S.side / 2 - 60, 0, 30], distance: 240, shadowFar: 700, normalBias: 0.05 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11, bumpScale: 0 });
  { const a0 = along(9, -1.2), a1 = along(40, 12); }
  F.desert(TXT, R, { area: [S.side / 2 + 1, -40, S.side / 2 + 60, 90], avoid: [], scrub: 160, rock: 0, grass: 2600, scale: [0.06, 0.14], grassArea: [S.side / 2 + 1, -10, S.side / 2 + 40, 60] });
  /* fine gravel to the lens, so the near ground carries material and not only a gradient */
  TXT.scatter(R, { kind: 'rock', count: 2600, area: [C[0] - 40, C[2] - 20, C[0] - 2, C[2] + 20], seed: 91, scale: [0.012, 0.035], colors: [0xa89c86, 0x8f8676, 0xb8ad98] });
  F.ridge(THREE, TXT, R, { peak: 760, seg: 1100, dseg: 200 });
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45, floor: 0.45, fade: 260 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.hook', '.dek']);
  TXDECK.finish(cx);
  window.__txDrawn = { units: yard.userData.drawn };
'''
k,h,b,s = shell.copy(9)
shell.write(9,
  "Archetype FULL_BLEED. RENDERED through txthree.js in the deck's goldenHour world, into the sun. The field of 813 in silhouette from the shoulder of the public road east of the pad, the year fence painted across the pad's edge as a dark banded line, the Franklin ridge against the setting sun, a wire fence on the public side receding at the right.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:900px;", dek_css="width:880px;", fit=(80, 104, 2))
