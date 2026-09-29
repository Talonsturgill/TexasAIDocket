import sys, json; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('units', 'acres') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 42, near: 0.05, far: 12000 });
  /* THE FINDINGS ON THE SITE THEY JUDGE. The step-up transformer at the end of the block nearest the
   * pad's south-west corner, its low voltage cabinet door square to the lens, the judges' proposal
   * for decision posted in the door's clear document pocket. The camera faces north-east into the
   * field with the low sun behind its left shoulder, so the door and the page take the light. The
   * right third looks past the cabinet's edge at its radiator fins, the next enclosure and the
   * field under the eastern range. */
''' + SITE + r'''
  const SC = 1.25, PHI = 136 * Math.PI / 180, TH = 316 * Math.PI / 180;
  const f = [Math.sin(PHI), Math.cos(PHI)], n = [-f[0], -f[1]], rt = [-Math.cos(PHI), Math.sin(PHI)];
  const T = [-S.side / 2 - 14, S.side / 2 + 12];
  const tx = K.make('padmount_transformer', { seed: 3, xcolor: 0x34453a }); tx.scale.setScalar(SC); tx.rotation.y = TH; tx.position.set(T[0], 0, T[1]); TXT.add(R, tx); TXT.contact(R, tx);
  /* the fins on the cabinet's far side stand in its own shadow and would close the view past its edge */
  tx.traverse(m => { if (m.isMesh && m.position.x > 0.9 && m.position.z < 0.7) m.visible = false; });
  /* matte utility paint: a metallic door mirrors the sky in a patch behind the hook */
  const matte = K.mat('pmt-green|matte', { color: 0x34453a, roughness: 0.78, metalness: 0.08 });
  tx.traverse(m => { if (m.isMesh && m.material && m.material.color && m.material.color.getHex() === 0x34453a) m.material = matte; if (m.isMesh && m.material && m.material.color && m.material.color.getHex() === 0xdcdad2) m.visible = false; });
  const at = (lx, y, lz) => [T[0] + rt[0] * lx + n[0] * lz, y, T[1] + rt[1] * lx + n[1] * lz];
  const DOOR = 1.145 * SC + 0.004;
  /* the door furniture, in the door's own plane: two leaves, a handle bar, a hasp, hinge knuckles */
  const green = K.mat('pmt-green|door', { color: 0x34453a, roughness: 0.78, metalness: 0.08 });
  const dark = K.mat('mgg-dark', { color: 0x17191c, roughness: 0.7, metalness: 0.2 });
  const onDoor = (m, lx, y, dz) => { const p = at(lx, y, DOOR + (dz || 0)); m.position.set(p[0], p[1], p[2]); m.rotation.y = TH; m.castShadow = false; TXT.add(R, m); return m; };
  onDoor(TXT.roundedBox(0.012, 1.55, 0.01, 0.003, dark), 0.0, 1.12, 0.002);
  onDoor(TXT.roundedBox(0.05, 0.34, 0.05, 0.012, K.mat('mgg-stack', { color: 0x6f6a64, roughness: 0.45, metalness: 0.7 })), -0.07, 1.05, 0.03);
  onDoor(TXT.roundedBox(0.09, 0.05, 0.04, 0.01, dark), -0.07, 1.3, 0.025);
  [0.55, 1.1, 1.65].forEach(y => onDoor(TXT.roundedBox(0.04, 0.12, 0.04, 0.012, green), 0.9, y, 0.02));
  /* a vent of pressed slats across the door's upper leaf, and road dust rising up the door from its sill */
  for (let i = 0; i < 9; i++) onDoor(TXT.roundedBox(0.62, 0.018, 0.02, 0.005, green), 0.36, 1.66 + i * 0.034, 0.012).rotation.x = -0.5;
  { const dc = document.createElement('canvas'); dc.width = 8; dc.height = 256; const dg = dc.getContext('2d'), gr = dg.createLinearGradient(0, 256, 0, 0);
    gr.addColorStop(0, 'rgba(176,150,112,0.85)'); gr.addColorStop(0.35, 'rgba(176,150,112,0.35)'); gr.addColorStop(1, 'rgba(176,150,112,0)'); dg.fillStyle = gr; dg.fillRect(0, 0, 8, 256);
    const dt = new THREE.CanvasTexture(dc); dt.colorSpace = THREE.SRGBColorSpace;
    const dust = new THREE.Mesh(new THREE.PlaneGeometry(1.86, 0.7), new THREE.MeshStandardMaterial({ map: dt, transparent: true, roughness: 1, depthWrite: false }));
    onDoor(dust, 0, 0.62, 0.006); dust.castShadow = false; }
  /* the page, a tabloid sheet of the proposal for decision, and the clear pocket over it */
  const PW = 0.28, PH = 0.43, PX = 0.62, PY = 1.06;
  const entries = [{ kind: 'heading', w: 0.5 }, { w: 0.34, t: 10 }, { w: 0.42, t: 10 }];
  const tpage = F.pageTexture(THREE, entries, { top: 150, left: 150 });
  const page = new THREE.Mesh(new THREE.PlaneGeometry(PW, PH), new THREE.MeshStandardMaterial({ map: tpage, roughness: 0.85 }));
  onDoor(page, PX, PY, 0.012); page.castShadow = false; page.receiveShadow = true;
  const pocketM = new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.16, roughness: 0.08, metalness: 0, clearcoat: 1 });
  onDoor(TXT.roundedBox(PW + 0.03, PH + 0.03, 0.008, 0.003, pocketM), PX, PY - 0.005, 0.02).castShadow = false;
  const lipM = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.12, transparent: true, opacity: 0.9, emissive: 0xfff4e0, emissiveIntensity: 0.25 });
  onDoor(TXT.roundedBox(PW + 0.03, 0.01, 0.014, 0.003, lipM), PX, PY + PH / 2 + 0.01, 0.022).castShadow = false;
  /* the next enclosure and its block behind, and the field */
  const blk = F.block(K, { units: 5, seed: 12 });
  const bp = at(6.5, 0, -12); blk.position.set(bp[0], 0, bp[2]); blk.rotation.y = TH; TXT.add(R, blk); TXT.contact(R, blk);
  const DCAM = 1.5, CX = 0.80, EYE = at(CX, 1.25, DOOR + DCAM), LOOK = at(CX, 1.25, DOOR);
  TXT.frame(R, { from: EYE, look: LOOK });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [T[0], 0, T[1]], distance: 50, shadowFar: 120, normalBias: 0.05 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 380, seed: 31 });
  TXT.weather(R, { grime: 0.4 });
  /* the judges' two lines are set ON the page: the page's own corners, projected, bound the block */
  const a0 = F.project(THREE, R, at(PX - PW / 2, PY + PH / 2, DOOR + 0.012)), a1 = F.project(THREE, R, at(PX + PW / 2, PY - PH / 2, DOOR + 0.012));
  const pg = document.getElementById('pg');
  const padX = 0.1 * (a1[0] - a0[0]);
  pg.style.left = (a0[0] + padX) + 'px'; pg.style.width = (a1[0] - a0[0] - 2 * padX) + 'px';
  pg.style.top = (a0[1] + 0.26 * (a1[1] - a0[1])) + 'px';
  window.__txPage = { rect: [a0[0], a0[1], a1[0], a1[1]], text: pg.getBoundingClientRect().toJSON() };
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.3, floor: 0.3, floorH: 220 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.hook', '.dek']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(5)
labs = json.load(open('/home/user/TexasAIDocket/out/2026-09-29/copy.json'))['slides']['S5']['labels']
pg = '<div id="pg">' + ''.join(f'<p class="qt">"{t}"</p>' for t in labs) + '</div>\n'
shell.write(5, "Archetype DOCUMENT. RENDERED through txthree.js in the deck's goldenHour world. The step-up transformer's cabinet door square to the lens, the judges' proposal for decision in its clear pocket with their two lines set on the page, the fins, the next enclosure and the field past the cabinet's edge.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:600px;", dek_css="width:590px;", fit=(80, 112, 2),
  extra_css='''  #pg { position:absolute; z-index:9; }
  .qt { font-family:"Fraunces", serif; font-weight:560; font-size:25px; line-height:1.24; color:#1F1D1A; margin-bottom:18px; font-variation-settings:"opsz" 24; }''',
  extra_html=pg)
