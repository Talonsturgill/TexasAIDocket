from common import page, write, figs
scene = figs('laredo_yes', 'laredo_no') + r'''
  /* WHERE IT IS DECIDED. An empty council chamber at blue hour from the centre aisle well behind
   * the public seats, far enough back that all nine dais chairs are in frame. The dais carries one chair per vote cast on Laredo's referendum call
   * (laredo_yes + laredo_no), named in the dek, and nobody sits anywhere. Behind the dais a long window holds the
   * deck's blue hour: the amber seam low, a lit cobra head, and one plate reader in silhouette on
   * the shoulder outside, so the object the room decides stands just beyond it. A ceiling wash from
   * camera left lights the dais front, the lightest thing in the room after the window. */
  const SEATS = FIG.laredo_yes + FIG.laredo_no;   /* one dais chair per vote cast on Laredo's referendum call */
  const R = PL.stage(TXT, gl, W, { fov: 50, near: 0.05, far: 300, fog: 0.0, exposure: 1.6 });
  TXT.interior(R, { w: 22, d: 20, h: 13, floor: 'concrete', wall: 0x7d7768, window: null, ceiling: true, light: 0.9 });
  /* oak pilasters down both side walls, and a ceiling high enough that its edge sits above the
   * type: the wall goes dark upward as the wash falls off, so no edge crosses the hook */
  const oak = K.mat('pl-pilaster', { color: 0x4a3322, roughness: 0.6 });
  for (let z = -8.5; z < 10; z += 2.5) [-10.85, 10.85].forEach((x) => { const pz = new THREE.Mesh(new THREE.BoxGeometry(0.16, 13, 0.5), oak); pz.position.set(x, 6.5, z); TXT.add(R, pz); });
  /* the window: the outside painted from the deck's own sky values, mullions every 1.5 m */
  const pc = document.createElement('canvas'); pc.width = 1800; pc.height = 500; const p = pc.getContext('2d');
  const sky = p.createLinearGradient(0, 0, 0, 500);
  [[0, '#0d1d48'], [0.4, '#2c4a8a'], [0.66, '#7088bb'], [0.8, '#d49a68'], [0.855, '#e8a868'], [0.86, '#1a1d27'], [1, '#12141b']].forEach((s) => sky.addColorStop(s[0], s[1]));
  p.fillStyle = sky; p.fillRect(0, 0, 1800, 500);
  p.fillStyle = '#151821';
  for (let x = 0; x < 1800; x += 26) { const h = 10 + 18 * Math.abs(Math.sin(x * 0.013) * Math.cos(x * 0.0071)); p.beginPath(); p.ellipse(x, 430, 30, h, 0, Math.PI, 0); p.fill(); }
  p.fillStyle = '#0c0e14';
  p.fillRect(1183, 330, 10, 106);                                     /* the plate reader's mast, panels on the seam */
  p.save(); p.translate(1188, 300); p.scale(1.5, 1.5);
  [[-58, 0], [4, 0]].forEach((q) => { p.beginPath(); p.moveTo(q[0], q[1] - 20); p.lineTo(q[0] + 54, q[1] - 20); p.lineTo(q[0] + 58, q[1] + 8); p.lineTo(q[0] + 4, q[1] + 8); p.closePath(); p.fill(); });
  p.fillRect(-3, 8, 6, 34); p.beginPath(); p.ellipse(0, 12, 9, 5, 0, 0, Math.PI * 2); p.fill();   /* stalk and LTE puck */
  p.fillRect(-14, 24, 30, 15); p.fillRect(14, 28, 10, 7); p.restore();                         /* camera head and its hood */
  p.fillRect(520, 130, 8, 306); p.fillRect(520, 130, 70, 6);          /* the cobra head */
  const glow = p.createRadialGradient(588, 140, 2, 588, 140, 70); glow.addColorStop(0, 'rgba(255,242,208,1)'); glow.addColorStop(0.18, 'rgba(255,226,170,0.75)'); glow.addColorStop(1, 'rgba(255,214,150,0)');
  p.fillStyle = glow; p.fillRect(500, 60, 180, 180);
  const tex = new THREE.CanvasTexture(pc); tex.colorSpace = THREE.SRGBColorSpace;
  const pane = new THREE.Mesh(new THREE.PlaneGeometry(9, 2.5), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }));
  pane.position.set(0, 3.05, -9.88); R.scene.add(pane);
  const mull = K.mat('pl-mullion', { color: 0x2a2724, roughness: 0.6, metalness: 0.3 });
  for (let i = 0; i <= 6; i++) { const m = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.6, 0.1), mull); m.position.set(-4.5 + i * 1.5, 3.05, -9.84); TXT.add(R, m); }
  [1.8, 4.3].forEach((y) => { const m = new THREE.Mesh(new THREE.BoxGeometry(9.1, 0.1, 0.12), mull); m.position.set(0, y, -9.84); TXT.add(R, m); });
  const dais = K.make('hearing_dais', { seats: SEATS, curve: 9, wood: 0x5a3a24, mics: true, plates: true, steps: true });
  dais.position.set(0, 0, -7.2); TXT.add(R, dais); TXT.contact(R, dais);
  const flags = K.make('flags_pair', {}); flags.position.set(-6.2, 0, -8.6); TXT.add(R, flags); TXT.contact(R, flags);
  /* blue grey carpet under the public seats, in straight rows either side of the centre aisle */
  const carpet = new THREE.Mesh(new THREE.BoxGeometry(18, 0.012, 24), K.mat('pl-carpet', { color: 0x384050, roughness: 1 }));
  carpet.position.set(0, 0.006, 5.5); TXT.add(R, carpet, { cast: false });
  const seats = K.make('public_seating', { rows: 4, perRow: 10, aisle: true, color: 0x2e3a52, frame: 'black' });
  seats.position.set(0, 0.012, 1.0); seats.rotation.y = Math.PI; TXT.add(R, seats); TXT.contact(R, seats);
  const back = K.make('public_seating', { rows: 4, perRow: 10, aisle: true, color: 0x2e3a52, frame: 'black', seed: 7 });
  back.position.set(0, 0.012, 7.4); back.rotation.y = Math.PI; TXT.add(R, back); TXT.contact(R, back);
  /* the ceiling wash on the dais front, from camera left */
  const wash = new THREE.SpotLight(0xfff0d8, 520, 32, 0.55, 0.7, 2);
  wash.position.set(-4, 7.0, 1.5); wash.target.position.set(-1.5, 1.0, -6.6); R.scene.add(wash, wash.target);
  const fill = new THREE.SpotLight(0xfff0d8, 220, 30, 0.5, 0.8, 2);
  fill.position.set(-9, 6.0, -1); fill.target.position.set(-4.5, 1.2, -7); R.scene.add(fill, fill.target);
  /* a low graze down each side wall so the pilasters read */
  [-9.5, 9.5].forEach((x) => { const gz = new THREE.PointLight(0xffe8cc, 40, 16, 2); gz.position.set(x, 3.5, 0); R.scene.add(gz); });
  /* blue hour comes in through the glass and rims the chair tops and the dais lip */
  const dusk = new THREE.SpotLight(0x8fa8e0, 140, 22, 0.8, 0.9, 2);
  dusk.position.set(0, 3.4, -9.5); dusk.target.position.set(0, 1.2, -5.5); R.scene.add(dusk, dusk.target);
  /* a soft dark footprint under each block of public seats, so the rows stand on the carpet */
  const fc = document.createElement('canvas'); fc.width = 128; fc.height = 128; const fx = fc.getContext('2d');
  const rg = fx.createRadialGradient(64, 64, 8, 64, 64, 63); rg.addColorStop(0, 'rgba(0,0,0,0.75)'); rg.addColorStop(0.7, 'rgba(0,0,0,0.45)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
  fx.fillStyle = rg; fx.fillRect(0, 0, 128, 128);
  const ft = new THREE.CanvasTexture(fc);
  [seats, back].forEach((blk) => {
    const bb = new THREE.Box3().setFromObject(blk), sz = bb.getSize(new THREE.Vector3()), c = bb.getCenter(new THREE.Vector3());
    [-1, 1].forEach((side) => {
      const q = new THREE.Mesh(new THREE.PlaneGeometry(sz.x * 0.5, sz.z * 1.05), new THREE.MeshBasicMaterial({ map: ft, transparent: true, depthWrite: false, color: 0x000000, opacity: 0.8 }));
      q.material.opacity = 0.55; q.rotation.x = -Math.PI / 2; q.position.set(c.x + side * sz.x * 0.27, 0.02, c.z); q.renderOrder = 1; R.scene.add(q);
    });
  });
  TXT.frame(R, { from: [0, 1.5, 13.8], look: [0, 1.9, -6] });
  TXT.deckRig(R, W.rig, { target: [0, 0, -3], distance: 18, shadowFar: 44, normalBias: 0.03 });
  TXT.weather(R, { grime: 0.15 });
  const cx = PL.develop(await TXT.snapshot(R), gl);
'''
write(9, page(9, 'Archetype SPLIT_HORIZON. RENDERED through txthree.js in a room TXT.interior builds, lit by the deck\'s rig. THE CLOSE. An empty council chamber from the centre aisle, nine chairs at the dais, a long window behind it holding blue hour with a plate reader in silhouette outside.',
    'League City votes next.',
    'Its voters answer a nonbinding question on November 3rd. Laredo\'s council voted 7 to 2 to ask its own in May.',
    'Where it is decided', 'c34 c35 c2', scene, dek_css='width:918px;', post='{ a: 0.32, veil: 0.45, veilH: 520 }', drawn='{ chairs: SEATS }'))
