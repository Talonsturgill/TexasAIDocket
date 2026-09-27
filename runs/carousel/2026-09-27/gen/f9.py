import sys
sys.path.insert(0, '.')
from common import page
scene = """  const R = TXT.setup(gl, { w: 1080, h: 1350, exposure: W.exposure, tone: W.tone, fov: 52 });
  /* A UNIT IN THE HERO at night: the kitchen side of a second floor apartment, the ceiling light
   * off, the resident standing at the counter with a laptop open toward them. The only cool light
   * in the room is the screen, the accent, and it models the face from the side the camera sees. */
  TXT.interior(R, { w: 5.2, d: 5.0, h: 2.6, floor: 'concrete', wall: 0x7a7064, window: 'left', windowColor: 0xffb25a, windowI: 0.12, windowW: 1.4, windowH: 1.2, ceiling: true, light: 0.16 });
  /* the window's sash and mullions, the lot's sodium beyond */
  { const sash = new THREE.MeshStandardMaterial({ color: 0xd8d2c6, roughness: 0.6 });
    [[0, 0.62, 1.44, 0.05], [0, -0.62, 1.44, 0.05], [0, 0, 1.24, 0.04]].forEach((b, i) => { const m = TXT.roundedBox(0.05, i < 2 ? 0.05 : 1.24, i < 2 ? b[2] : 0.04, 0.005, sash); m.position.set(-2.575, 1.43 + b[1], -0.5); R.scene.add(m); });
    [-0.72, 0.72].forEach((dz) => { const m = TXT.roundedBox(0.05, 1.29, 0.05, 0.005, sash); m.position.set(-2.575, 1.43, -0.5 + dz); R.scene.add(m); }); }
  TXT.frame(R, { from: [1.62, 2.05, -0.72], look: [-0.9, 1.3, -1.95] });
  /* indoors the deck's cool rim would put a second cool light in the room: it is warmed and dimmed */
  TXT.deckRig(R, Object.assign({}, W.rig, { rim: { color: 0xffb46a, i: 0.12, pos: [-8, 6, -8] }, fill: { color: 0x3a3026, i: 0.3, pos: [4, 4, 9] } }), { target: [0, 1, -1], distance: 8, shadowFar: 20 });
  /* the counter against the back wall: the kit desk at counter height, a veneer top the screen falls on */
  const counter = K.make('desk', { w: 2.2, d: 0.65, h: 0.95, pedestal: 'none', wood: 0x5a4636, seed: 3 });
  counter.visible = false;
  const lap = K.make('laptop', { open: 108, finish: 'space', screen: 'doc', seed: 2 });
  lap.position.set(-0.28, 0.918, -2.02); lap.rotation.y = 0; TXT.add(R, lap);
  lap.traverse((m) => { if (m.isMesh && m.material && m.material.emissive && m.material.emissiveIntensity > 0) {
    m.material = m.material.clone(); m.material.emissive = new THREE.Color(F.ACCENT); m.material.emissiveIntensity = 0.72; m.material.color = new THREE.Color(0x0b1016); } });
  /* the screen's light, in the accent, on the wall behind it and the resident's front */
  /* the screen's light thrown forward onto the resident's face and hands, never back onto the wall */
  const sl = new THREE.SpotLight(F.ACCENT, 3.2, 2.4, 0.9, 0.8, 2); sl.position.set(-0.28, 1.08, -1.9); sl.target.position.set(-0.34, 1.55, -1.5); R.scene.add(sl); R.scene.add(sl.target);
  const p = K.make('person', { seed: 23, role: 'resident', pose: 'stand', build: 'male', hat: 'none', detail: 'full' });
  p.position.set(-0.62, 0, -1.72); p.rotation.y = Math.PI + 0.5;
  p.traverse((m) => { if (m.isMesh && m.material && m.material.color) { const c = m.material.color, l = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b; if (l > 0.45) { m.material = m.material.clone(); m.material.color = new THREE.Color(0x8f8374); } } }); TXT.add(R, p); TXT.contact(R, p);
  const mug = TXT.lathe([[0, 0], [0.04, 0], [0.042, 0.005], [0.042, 0.095], [0.038, 0.1], [0.036, 0.012], [0, 0.012]], TXT.mat.clay(0xcfc6b4, { roughness: 0.4 }));
  mug.position.set(0.25, 0.918, -1.98); R.scene.add(mug);
  /* the kitchen: base cabinets under the counter, uppers on the back wall, a range and a fridge */
  const cab = new THREE.MeshStandardMaterial({ color: 0x8d7a64, roughness: 0.62 });
  const pull = TXT.mat.steel({ roughness: 0.35 });
  for (let i = 0; i < 4; i++) {
    const bx = -1.3 + i * 0.55 + 0.275;
    const base = TXT.roundedBox(0.53, 0.86, 0.58, 0.01, cab); base.position.set(bx, 0.43, -2.16); TXT.add(R, base);
    const hb = TXT.roundedBox(0.12, 0.012, 0.012, 0.004, pull); hb.position.set(bx, 0.78, -1.86); R.scene.add(hb);
    const up = TXT.roundedBox(0.53, 0.72, 0.33, 0.01, cab); up.position.set(bx, 1.86, -2.3); TXT.add(R, up);
    const hu = TXT.roundedBox(0.012, 0.1, 0.012, 0.004, pull); hu.position.set(bx + 0.2, 1.6, -2.13); R.scene.add(hu);
  }
  /* a subway tile backsplash between the counter and the uppers, and panel insets on every door */
  const tc = document.createElement('canvas'); tc.width = 256; tc.height = 128; const tg = tc.getContext('2d');
  tg.fillStyle = '#6f6a62'; tg.fillRect(0, 0, 256, 128); tg.fillStyle = '#b9b2a6';
  for (let r = 0; r < 4; r++) for (let c = -1; c < 5; c++) tg.fillRect(c * 64 + (r % 2) * 32 + 2, r * 32 + 2, 60, 28);
  const tt = new THREE.CanvasTexture(tc); tt.colorSpace = THREE.SRGBColorSpace; tt.wrapS = tt.wrapT = THREE.RepeatWrapping; tt.repeat.set(9, 2.4);
  const splash = new THREE.Mesh(new THREE.PlaneGeometry(2.24, 0.58), new THREE.MeshStandardMaterial({ map: tt, roughness: 0.35 }));
  splash.position.set(-0.2, 1.21, -2.395); R.scene.add(splash);
  const inset = new THREE.MeshStandardMaterial({ color: 0x6f604f, roughness: 0.7 });
  for (let i = 0; i < 4; i++) {
    const bx = -1.3 + i * 0.55 + 0.275;
    const a = TXT.roundedBox(0.4, 0.6, 0.01, 0.004, inset); a.position.set(bx, 0.42, -1.868); R.scene.add(a);
    const b = TXT.roundedBox(0.4, 0.56, 0.01, 0.004, inset); b.position.set(bx, 1.86, -2.132); R.scene.add(b);
  }
  const papers = K.make('document_stack', { seed: 9 }); papers.position.set(-0.95, 0.918, -2.15); papers.rotation.y = 0.3; TXT.contact(R, papers); TXT.add(R, papers);
  const top = TXT.roundedBox(2.24, 0.035, 0.64, 0.008, new THREE.MeshStandardMaterial({ color: 0x2c2926, roughness: 0.3 }));
  top.position.set(-0.2, 0.9, -2.14); TXT.add(R, top);
  const fridge = TXT.roundedBox(0.8, 1.78, 0.72, 0.03, TXT.mat.clay(0xb9b6ae, { roughness: 0.35 }));
  fridge.position.set(1.42, 0.89, -2.1); TXT.add(R, fridge); TXT.contact(R, fridge);
  const fh = TXT.roundedBox(0.02, 0.5, 0.03, 0.008, pull); fh.position.set(1.08, 1.2, -1.72); R.scene.add(fh);
  const fs = TXT.roundedBox(0.8, 0.006, 0.02, 0.002, new THREE.MeshStandardMaterial({ color: 0x3a3936 })); fs.position.set(1.42, 1.25, -1.735); R.scene.add(fs);
  /* the under-cabinet strip left on, low and warm, the one lamp a kitchen keeps at night: it lays a
   * run of light along the backsplash and the counter the laptop sits on */
  [-1.1, -0.45, 0.2, 0.85].forEach((x) => { const u = new THREE.PointLight(0xffc68a, 0.55, 1.6, 2); u.position.set(x, 1.47, -2.2); R.scene.add(u); });
  { const strip = TXT.roundedBox(2.1, 0.015, 0.03, 0.004, new THREE.MeshBasicMaterial({ color: 0xffe0b0 })); strip.position.set(-0.2, 1.49, -2.2); R.scene.add(strip); }
  /* the lot's sodium light through the window on the left wall */
  const warm = new THREE.PointLight(F.SODIUM, 1.8, 6, 2); warm.position.set(-2.2, 1.5, -0.5); R.scene.add(warm);
"""
f9 = page(9, 'CLOSE_CROP', 'RENDERED in a TXT.interior room. Over the resident shoulder at the kitchen counter, the laptop the one cool light.',
  "Comment before the court rules",
  "The notice was published September 18th and takes public comment within 60 days. Email <span style=\"white-space:nowrap\">ATR.Public-Comments-Tunney-Act-MB@usdoj.gov</span> in English, to the Technology and Digital Platforms Section of the Justice Department's Antitrust Division.",
  "What a Texan can do", "c1 c8 c9 c10 c11 c62   DRAWN",
  scene, hmin=84, hmax=118)
open('../../slides/slide-09.html', 'w').write(f9)
