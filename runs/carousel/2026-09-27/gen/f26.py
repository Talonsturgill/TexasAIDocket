import sys, json
sys.path.insert(0, '.')
from common import page
FIG = json.load(open('../../figures.json'))
NEAR, CLOSE = FIG['band_near_px'], FIG['band_close_px']
ROOM = """  /* THE LEASING OFFICE at night. The storefront glass on the left wall with the lot's sodium pool
   * outside it, a veneer desk against the back wall, a 27 inch monitor, an office chair. */
  TXT.interior(R, { w: 4.0, d: 5.4, h: 2.8, floor: 'concrete', wall: 0x5f5a52, window: null, ceiling: false, light: 0.3 });
  /* the storefront: bronze mullions on the glass, the lot's sodium beyond it */
  const bronze = new THREE.MeshStandardMaterial({ color: 0x4a3a28, roughness: 0.45, metalness: 0.6 });
  { const sill = TXT.roundedBox(2.1, 0.08, 0.1, 0.01, bronze); sill.position.set(-0.8, 0.5, -2.55); R.scene.add(sill); }
  const desk = K.make('desk', { w: 1.7, d: 0.8, h: 0.74, pedestal: 'right', wood: 0x5a4636, seed: 4 });
  desk.position.set(0.45, 0, -2.2); TXT.add(R, desk); TXT.contact(R, desk);
  /* the desk's cable grommet sits behind the type in both office frames: hidden */
  desk.traverse((m) => { if (m.isMesh && (m.geometry.type === 'TorusGeometry' || m.geometry.type === 'CircleGeometry')) m.visible = false; });
  /* the veneer's long grain streaks read as ruled lines under the type: the top keeps its colour and sheen and loses the streaks */
  desk.traverse((m) => { if (m.isMesh && m.material && m.material.map) { m.material = m.material.clone(); m.material.map = null; m.material.color = new THREE.Color(0x4a3a2c); } });
  const mon = K.make('monitor', { inches: 27, screen: 'chart', seed: 3 });
  mon.position.set(0.45, 0.74, -2.35); TXT.add(R, mon);
  /* the screen: a canvas drawn from figures.json, the recommendation line and its two bands, the
   * wide lit accept bar and the small outlined decline box. No word is drawn on it. */
  const cv = document.createElement('canvas'); cv.width = 1024; cv.height = 576;
  const g = cv.getContext('2d');
  g.fillStyle = '#0c131b'; g.fillRect(0, 0, 1024, 576);
  g.fillStyle = '#1b2733'; g.fillRect(0, 0, 1024, 44);
  for (let i = 0; i < 6; i++) { g.fillStyle = i === 2 ? '#2f4458' : '#17222d'; g.fillRect(24 + i * 150, 54, 132, 22); }
  const LY = 250, NEAR = %NEAR%, CLOSE = %CLOSE%;
  g.fillStyle = 'rgba(127,178,217,0.18)'; g.fillRect(40, LY - CLOSE, 944, CLOSE * 2);
  g.fillStyle = 'rgba(127,178,217,0.45)'; g.fillRect(40, LY - NEAR, 944, NEAR * 2);
  g.strokeStyle = '#7FB2D9'; g.lineWidth = 4; g.beginPath(); g.moveTo(40, LY); g.lineTo(984, LY); g.stroke();
  g.fillStyle = '#7FB2D9'; g.fillRect(40, 440, 720, 100);
  g.strokeStyle = 'rgba(127,178,217,0.8)'; g.lineWidth = 5; g.strokeRect(800, 466, 150, 48);
  window.__scr = { LY, NEAR, CLOSE };
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  let screen = null;
  mon.traverse((m) => { if (m.isMesh && m.material && m.material.emissiveMap && !screen) screen = m; });
  screen.material = new THREE.MeshStandardMaterial({ color: 0x050607, roughness: 0.9, metalness: 0.0, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: window.__EI || 0.68 });
  mon.updateMatrixWorld(true);
  const sw = screen.geometry.parameters.width, sh = screen.geometry.parameters.height;
  window.__uv = (u, v) => { const p = new THREE.Vector3((u - 0.5) * sw, (0.5 - v) * sh, 0); screen.localToWorld(p); return [p.x, p.y, p.z]; };
  /* the screen's own light on the desk and the wall behind */
  const sl = new THREE.PointLight(F.ACCENT, 1.4, 3.2, 2); sl.position.set(0.45, 0.86, -1.9); R.scene.add(sl);
  /* the lot's sodium through the storefront */
  const warm = new THREE.PointLight(F.SODIUM, 3.0, 4, 2); warm.position.set(-1.4, 0.9, -1.9); R.scene.add(warm);
"""
F2 = """  const R = TXT.setup(gl, { w: 1080, h: 1350, exposure: W.exposure, tone: W.tone, fov: 38 });
""" + ROOM + """  /* a filing cabinet by the storefront, a stack of lease files on the desk */
  const fc = K.make('filing_cabinet', { seed: 3, color: 0x8a7f70 }); fc.position.set(-1.5, 0, -2.25); TXT.add(R, fc); TXT.contact(R, fc);
  const chair = K.make('office_chair', { seed: 2 });
  chair.position.set(0.5, 0, -1.25); chair.rotation.y = Math.PI - 0.1; TXT.add(R, chair); TXT.contact(R, chair);
  TXT.frame(R, { from: [-0.25, 1.47, 0.25], look: [0.3, 1.2, -2.35] });
  TXT.deckRig(R, Object.assign({}, W.rig, { key: Object.assign({}, W.rig.key, { i: (W.rig.key.i || 1) * 0.35 }) }), { target: [0, 1, -1.5], distance: 8, shadowFar: 20 });
  window.__pts = { line: F.project(THREE, R, __uv(0.05, __scr.LY / 576)),
    near: F.project(THREE, R, __uv(0.05, (__scr.LY - __scr.NEAR) / 576)),
    close: F.project(THREE, R, __uv(0.05, (__scr.LY - __scr.CLOSE) / 576)),
    bar: F.project(THREE, R, __uv(0.06, 490 / 576)), box: F.project(THREE, R, __uv(0.855, 514 / 576)) };
"""
LAB2 = """  const svg = document.getElementById('lead');
  const lab = (id, txt, at, dy) => {
    const el = document.getElementById(id); el.textContent = txt;
    el.style.right = (1080 - at[0] + 64) + 'px'; el.style.top = (at[1] + dy) + 'px';
    const b = el.getBoundingClientRect();
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    const from = [b.right + 8, b.top + b.height / 2];
    p.setAttribute('points', [from, [at[0] - 4, at[1]]].map(q => q.join(',')).join(' '));
    p.setAttribute('fill', 'none'); p.setAttribute('stroke', '#EDE4D6'); p.setAttribute('stroke-width', '2'); svg.appendChild(p);
    (window.__txLeaders = window.__txLeaders || []).push({ target: txt, at: [at[0] - 4, at[1]], to: [at[0] - 4, at[1]] });
  };
  lab('l2', '5%', __pts.close, -52);
  lab('l1', '2.5%', __pts.near, -20);
  lab('l0', 'recommended', __pts.line, 14);
  const lab2 = (id, txt, at, x, y) => {
    const el = document.getElementById(id); el.textContent = txt; el.style.left = x + 'px'; el.style.top = y + 'px';
    const b = el.getBoundingClientRect(), from = x < at[0] ? [b.right + 8, b.top + b.height / 2] : [b.left - 8, b.top + b.height / 2];
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    p.setAttribute('points', [from, [at[0], at[1]]].map(q => q.join(',')).join(' '));
    p.setAttribute('fill', 'none'); p.setAttribute('stroke', '#EDE4D6'); p.setAttribute('stroke-width', '2'); svg.appendChild(p);
    (window.__txLeaders = window.__txLeaders || []).push({ target: txt, at: at, to: at });
  };
  lab2('l3', 'bulk acceptance', __pts.bar, __pts.bar[0] - 300, __pts.bar[1] + 40);
  lab2('l4', 'decline, with a reason', __pts.box, __pts.box[0] - 250, __pts.box[1] + 90);
"""
f2 = page(2, 'CLOSE_CROP', 'RENDERED in a TXT.interior room. The leasing office at night from behind the empty chair, the recommendation screen drawn from figures.json.',
  "Yes in bulk, no with a reason",
  "A manager can accept in bulk and must give \"specific business commentary\" to decline, the complaint says. Across landlords nationally, it puts nearly 60% of final floor plan prices within 2.5% of RealPage's recommendation and more than 85% within 5%.",
  "The leasing office", "c21 c30 c31 c33   DRAWN",
  F2.replace('%NEAR%', str(NEAR)).replace('%CLOSE%', str(CLOSE)),
  after=LAB2, extra_css='  .hook { line-height:1.03; }', extra_html='<svg class="lead" id="lead"></svg><div class="lab" id="l0"></div><div class="lab" id="l1"></div><div class="lab" id="l2"></div><div class="lab" id="l3"></div><div class="lab" id="l4"></div>')
open('../../slides/slide-02.html', 'w').write(f2)

N = FIG['judgment_requirements']['value']
F6 = """  const R = TXT.setup(gl, { w: 1080, h: 1350, exposure: W.exposure, tone: W.tone, fov: 40 });
""" + ROOM + """  desk.scale.z = 1.25; desk.position.z = -2.2 - 0.1;
  /* the monitor slid to the desk's right end and turned to the chair, so its glow falls across the
   * page while its lit face stays out from behind the hook */
  mon.position.x += 0.43; mon.position.z += 0.16; mon.rotation.y = -0.62; mon.position.y -= 0.05; mon.updateMatrixWorld(true); sl.intensity = 0;
  /* the monitor's light gathered onto the page it governs, so the desk behind the type stays dark */
  { const ms = new THREE.SpotLight(F.ACCENT, window.__SLI || 3.5, 2.4, 0.32, 0.7, 2); ms.position.set(0.66, 1.05, -2.25); ms.target.position.set(0.24, 0.745, -1.97); R.scene.add(ms); R.scene.add(ms.target); }
  /* the proposed final judgment on the desk, a letter page with one ruled entry per requirement
   * the judgment numbers, counted in compute.py. Entries are drawn as ruled lines, never words. */
  const N = %N%;
  const pc = document.createElement('canvas'); pc.width = 816; pc.height = 1056;
  const q = pc.getContext('2d');
  q.fillStyle = '#ececec'; q.fillRect(0, 0, 816, 1056);
  q.fillStyle = '#6d6a64'; q.fillRect(250, 70, 316, 14); q.fillRect(300, 96, 216, 10);
  const top = 150, step = (1000 - top) / N;
  window.__entries = [];
  for (let i = 0; i < N; i++) {
    const y = top + i * step;
    q.fillStyle = '#3d3a35'; q.fillRect(70, y + 10, 26, 10);
    q.fillStyle = '#77736b';
    const lines = 2 + (i * 7 % 3);
    for (let k = 0; k < lines; k++) q.fillRect(120, y + 8 + k * 22, k === lines - 1 ? 300 + (i * 53 % 260) : 620, 9);
    q.strokeStyle = '#a8a298'; q.lineWidth = 3; q.beginPath(); q.moveTo(70, y + step - 8); q.lineTo(746, y + step - 8); q.stroke();
    window.__entries.push((y + 22) / 1056);
  }
  const ptex = new THREE.CanvasTexture(pc); ptex.colorSpace = THREE.SRGBColorSpace; ptex.anisotropy = 8;
  const PW = 0.216, PH = 0.279;
  const page = new THREE.Mesh(new THREE.PlaneGeometry(PW, PH), new THREE.MeshStandardMaterial({ map: ptex, roughness: 0.9, color: 0xf2eee6 }));
  page.rotation.x = -Math.PI / 2; page.rotation.z = 0.06; page.position.set(0.3, 0.7415, -1.97); page.castShadow = false; page.receiveShadow = true; R.scene.add(page);
  TXT.contact(R, page);
  const pen = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.14, 12), TXT.mat.clay(0x1b1d22, { roughness: 0.35 }));
  pen.rotation.z = Math.PI / 2; pen.rotation.y = 1.45; pen.position.set(0.14, 0.7465, -1.98); R.scene.add(pen);
  /* the lot's sodium through the storefront glass behind the desk, the mullions' shadows across
   * the page */
  { const sp = new THREE.SpotLight(F.SODIUM, 2, 7, 0.55, 0.5, 2); sp.position.set(-0.9, 2.3, -3.4); sp.target.position.set(0.35, 0.74, -1.85);
    sp.castShadow = true; sp.shadow.mapSize.set(1024, 1024); sp.shadow.bias = -0.0005; R.scene.add(sp); R.scene.add(sp.target); }
  /* a dark leather desk pad under the page and the margin notes beside it */
  /* the veneer is flat now, so the margin notes need no pad under them */
  page.position.y = 0.7455;
  page.updateMatrixWorld(true);
  const pageUV = (u, v) => { const p = new THREE.Vector3((u - 0.5) * PW, (0.5 - v) * PH, 0.001); page.localToWorld(p); return F.project(THREE, R, [p.x, p.y, p.z]); };
  TXT.frame(R, { from: [0.34, 1.52, -1.28], look: [0.34, 0.74, -2.02] });
  TXT.deckRig(R, W.rig, { target: [0, 1, -1.5], distance: 8, shadowFar: 20 });
  window.__pe = [4, 5, 8].map((i) => pageUV(0.92, __entries[i]));
"""
LAB6 = """  const svg = document.getElementById('lead');
  let floor = 0;
  [['e0', 'v. a chief antitrust compliance officer'], ['e1', 'vi. inspect its documents'], ['e2', 'ix. a monitor if the Court finds that Pinnacle has violated the terms']].forEach(([id, txt], k) => {
    const at = __pe[k], el = document.getElementById(id); el.textContent = txt;
    el.style.left = '806px'; el.style.width = '194px'; el.style.whiteSpace = 'normal';
    const top = Math.max(at[1] - 44, floor);
    el.style.top = top + 'px';
    const b = el.getBoundingClientRect(); floor = b.bottom + 8;
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    p.setAttribute('points', [[b.left - 10, b.top + 15], [b.left - 24, b.top + 15], [at[0] + 6, at[1]]].map(q => q.join(',')).join(' '));
    p.setAttribute('fill', 'none'); p.setAttribute('stroke', '#EDE4D6'); p.setAttribute('stroke-width', '2'); svg.appendChild(p);
    (window.__txLeaders = window.__txLeaders || []).push({ target: txt, at: at, to: at });
  });
"""
f6 = page(6, 'DOCUMENT', 'RENDERED in the leasing office. The proposed final judgment on the desk, one ruled entry per numbered requirement.',
  "Nine terms for Pinnacle",
  "The impact statement sums up the proposed judgment against Pinnacle in nine terms. Beside the data limits they require a compliance officer, an annual audit and inspections.",
  "The proposed final judgment", "c3 c12 c39 to c48   DRAWN",
  F6.replace('%N%', str(N)).replace('%NEAR%', str(NEAR)).replace('%CLOSE%', str(CLOSE)),
  after=LAB6, extra_html='<svg class="lead" id="lead"></svg><div class="lab" id="e0"></div><div class="lab" id="e1"></div><div class="lab" id="e2"></div>')
open('../../slides/slide-06.html', 'w').write(f6)
