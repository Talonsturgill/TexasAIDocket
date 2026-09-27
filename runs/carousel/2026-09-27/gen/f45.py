import sys, json
sys.path.insert(0, '.')
from common import page
FIG = json.load(open('../../figures.json'))

F4 = """  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 30 });
  /* THE RESIDENT. Out in the lot 30 m from the lens, walking in toward the second breezeway of the
   * hero, which stands 70 m off with its cores lit. A pole light's pool around the resident's feet,
   * the lens on the resident's lit side. The lease is the person; the building is the dataset. */
  const hero = F.hero(K, { litUnits: [[1, 2], [2, 1], [4, 2]], lampI: 12, poolI: 40 });
  TXT.add(R, hero); TXT.contact(R, hero);
  const D = hero.userData.dims, zF = D.D / 2, core = hero.userData.cores[1];
  const SX0 = core.x != null ? core.x : core;
  const CAM = [SX0 - 18, 1.5, zF + 70];
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [SX0, 0, zF + 30], distance: 90, shadowFar: 200 });
  const gnd = TXT.ground(R, { surface: 'asphalt', size: 4000, seed: 13 });
  const walk = TXT.roundedBox(D.L + 4, 0.15, 3.2, 0.03, new THREE.MeshStandardMaterial({ color: 0x9a948a, roughness: 0.55 }));
  walk.position.set(0, 0.075, zF + 1.6); TXT.add(R, walk);
  F.stalls(THREE, TXT, R, SX0 - 30, zF + 3.8, 14, { dir: 1, curb: false });
  [['sedan', SX0 - 7.6, 0x44484c], ['suv', SX0 + 5.4, 0x2a2d31], ['pickup', SX0 - 21.2, 0x5b6068]].forEach((c, i) => {
    const v = K.make(c[0], { seed: 41 + i, color: c[2] }); v.position.set(c[1], 0, zF + 6.4); v.rotation.y = Math.PI; TXT.add(R, v); TXT.contact(R, v); });
  /* the resident, walking in */
  const PX = CAM[0] + 0.3 * 30 * (18.8 / 70) + 1.2, PZ = CAM[2] - 30;
  const p = K.make('person', { seed: 12, role: 'resident', pose: 'walk', build: 'female', hat: 'none', detail: 'full' });
  p.position.set(PX, 0, PZ); p.rotation.y = Math.PI - 0.5; TXT.add(R, p); TXT.contact(R, p);
  F.lotLamp(THREE, TXT, K, R, PX - 5, PZ - 3, { ry: 0.4, i: 260, seed: 47, height: 9 });
  { const f = new THREE.PointLight(F.SODIUM, 60, 14, 2); f.position.set(PX + 2.5, 4.5, PZ + 5); R.scene.add(f); }
  { const pool = new THREE.SpotLight(F.SODIUM, 900, 22, 0.42, 0.65, 2); pool.position.set(PX - 4.6, 8.6, PZ - 2.6); pool.target.position.set(PX, 0, PZ); R.scene.add(pool); R.scene.add(pool.target); }
  F.stalls(THREE, TXT, R, PX - 14, PZ + 3.5, 11, { dir: -1, curb: false });

  /* parked cars at two in the morning: no running lamps */
  R.scene.traverse((m) => { if (m.isMesh && m.material && m.material.emissive && m.material.emissiveIntensity > 1 && (m.material.emissive.getHex() & 0xff) > 0xc0) m.material.emissiveIntensity = 0; });
  TXT.frame(R, { from: CAM, look: [SX0 - 1, 11.3, zF] });
"""
f4 = page(4, 'FIGURE_SCALE', 'RENDERED in the declared nightSodium world. A resident at the foot of a lit breezeway stair of the hero.',
  "Leases feed the model",
  "The complaint says landlords' nonpublic lease data runs through a machine learning model whose learned parameters serve every AIRM client. It says the model is generally retrained three to four times a year. It says RealPage has data from over 16 million units.",
  "Where the data comes from", "c23 c24 c34   DRAWN", F4)
open('../../slides/slide-04.html', 'w').write(f4)

BY = FIG['texas_submarkets_by_area']
ORDER = [('Dallas-Plano-Irving, TX', 'Dallas-Plano-Irving'), ('Austin-Round Rock, TX', 'Austin-Round Rock'),
         ('Houston-The Woodlands-Sugar Land, TX', 'Houston'), ('San Antonio-New Braunfels, TX', 'San Antonio'),
         ('Fort Worth-Arlington, TX', 'Fort Worth')]
assert sum(BY[k] for k, _ in ORDER) == FIG['texas_submarkets']['value']
CL = json.dumps([[name, BY[k]] for k, name in ORDER])
F5 = """  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, 0.00008], exposure: W.exposure * 1.0, tone: W.tone, fov: 60, far: 40000 });
  /* ONE BUILDING PER SUBMARKET. Appendix A's Texas rows, counted in compute.py (TOTAL) and split
   * by area (CL): TOTAL small garden buildings laid out one by one, each dealt to its area's
   * cluster in the order of the counts, two across, so a cluster's depth is its count. Seen
   * from a rise with the horizon in frame and the plain going to haze behind them. */
  const TOTAL = %TOTAL%;
  const CL = %CL%;
  const proto = F.hero(K, { seed: 30, cores: 1, groupBays: 1, office: false, lampsOn: true, lampLights: false, lit: 0.7, floors: 4 });
  const SX = 27, SZ = 30, GAP = 44, COLS = 2, ZOFF = 0;
  const widths = CL.map(([, n]) => Math.min(COLS, n) * SX);
  const x0 = [];
  { let x = -(widths.reduce((a, b) => a + b, 0) + GAP * (CL.length - 1)) / 2; widths.forEach((w) => { x0.push(x); x += w + GAP; }); }
  window.__cl = CL.map(([name, n], ci) => ({ name, n, at: [x0[ci] + widths[ci] / 2, 0, 18 + ZOFF] }));
  const avoid = [];
  let ci = 0, k = 0;
  for (let i = 0; i < TOTAL; i++) {
    while (k >= CL[ci][1]) { ci++; k = 0; }
    const b = proto.clone(); const c = k % COLS, r = Math.floor(k / COLS);
    b.position.set(x0[ci] + (c + 0.5) * SX, 0, -r * SZ + ZOFF); b.rotation.y = ((i * 37) % 7 - 3) * 0.01;
    TXT.add(R, b);
    /* each building's own paved lot in front of it, lit by its lamps */
    const pad = TXT.roundedBox(SX - 5, 0.1, 9, 0.03, new THREE.MeshStandardMaterial({ color: 0x6a645c, roughness: 0.8 }));
    pad.position.set(b.position.x, 0.05, b.position.z + 11); pad.receiveShadow = true; R.scene.add(pad);
    k++;
  }
  CL.forEach(([name, n], j) => {
    const rows = Math.ceil(n / COLS), cx = x0[j] + widths[j] / 2;
    F.lotLamp(THREE, TXT, K, R, cx, 16 + ZOFF, { ry: Math.PI, i: 900, seed: 60 + j, height: 9 });
    for (let r = 1; r < rows; r += 1) { const gl2 = new THREE.PointLight(F.SODIUM, 520, 28, 2); gl2.position.set(cx, 7, -r * SZ + SZ / 2 + ZOFF); R.scene.add(gl2); }
    avoid.push([x0[j] - 8, -(rows - 1) * SZ - 14, x0[j] + widths[j] + 8, 26]);
  });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -60], distance: 500, shadowFar: 1200 });
  TXT.ground(R, { surface: 'dirt', color: 0x4a3828, size: 30000, seed: 21 });
  TXT.frame(R, { from: [0, 339, 376], look: [0, 0, -251] });
  __cl.forEach((c) => { c.px = F.project(THREE, R, c.at); });
"""
LAB5 = """    __cl.forEach((c, i) => {
    const el = document.getElementById('k' + i);
    el.innerHTML = ''; const kn = document.createElement('span'); kn.className = 'kn'; kn.textContent = c.n; const nm = document.createElement('span'); nm.className = 'nm'; nm.textContent = c.name; el.appendChild(kn); el.appendChild(nm);
    const b = el.getBoundingClientRect();
    el.style.left = Math.max(80, Math.min(1000 - b.width, c.px[0] - b.width / 2)) + 'px';
    el.style.top = (c.px[1] + 16) + 'px';
    (window.__txLeaders = window.__txLeaders || []).push({ target: c.name, at: c.px, to: c.px });
  });
"""
f5 = page(5, 'GRID', 'RENDERED in the declared nightSodium world. One building per Texas row of Appendix A, five clusters by area.',
  "<span class=\"n48\">48</span> Texas submarkets",
  "The complaint lists them as places where it says aligned pricing harmed or is likely to harm renters. Frisco and Richardson are on the list. RealPage has its headquarters in Richardson.",
  "Appendix A of the complaint", "c15 c36 c37 c38   DRAWN",
  F5.replace('%CL%', CL).replace('%TOTAL%', str(FIG['texas_submarkets']['value'])), after=LAB5,
  extra_css='  .lab.k { text-align:center; font-size:24px; line-height:1.2; }\n  .lab.k .kn { font-size:34px; display:block; }\n  .lab.k .nm { display:block; white-space:normal; width:118px; margin:0 auto; }\n  .hook .n48 { font-variation-settings:"opsz" 40; }',
  extra_html=''.join(f'<div class="lab k" id="k{i}"></div>' for i in range(5)))
open('../../slides/slide-05.html', 'w').write(f5)
