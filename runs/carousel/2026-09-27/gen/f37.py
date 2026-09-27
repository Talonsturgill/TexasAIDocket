import sys, json
sys.path.insert(0, '.')
from common import page
FIG = json.load(open('../../figures.json'))
LIMITS = FIG['software_limits']['value'] if isinstance(FIG['software_limits'], dict) else FIG['software_limits']
SCENE = """  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure * %EXPO%, tone: W.tone, fov: 36 });
  /* ONE CAMERA FOR FRAMES 3 AND 7, 150 m out on the lot, square to the hero's front, eye 1.7 m.
   * All five breezeway cores and both gable ends stand in frame, the storefront at the west end.
   * Frame 3 has the cores lit and two steel columns 12 m from the lens. Frame 7 is the same
   * picture with the cores switched off and the columns gone, their base plates left behind. */
  const hero = F.hero(K, { litUnits: [[2, 2], [4, 1]], lampI: 12, poolI: 40, officeI: 3.2, officeSpill: 60%LAMPS% });
  TXT.add(R, hero); TXT.contact(R, hero);
  const D = hero.userData.dims, L = D.L, zF = D.D / 2, CZ = zF + 150;
  TXT.frame(R, { from: [0, 1.7, CZ], look: [0, 13.2, zF] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, 20], distance: 160, shadowFar: 380 });
  TXT.ground(R, { surface: 'asphalt', size: 6000, seed: 13 });
  const walk = TXT.roundedBox(L + 4, 0.15, 3.2, 0.03, new THREE.MeshStandardMaterial({ color: 0x9a948a, roughness: 0.92 }));
  walk.position.set(0, 0.075, zF + 2.2); TXT.add(R, walk);
  F.stalls(THREE, TXT, R, -L / 2 + 2, zF + 30, 22, { dir: 1 });
  F.stalls(THREE, TXT, R, -L / 2 + 2, zF + 62, 22, { dir: -1 });
  [['sedan', -L / 2 + 8.2, 0x3b3e42, 34.5, 0], ['pickup', -L / 2 + 19.2, 0x6a2a20, 34.5, 0], ['suv', L / 2 - 14.9, 0x1f2226, 34.5, 0],
   ['sedan', -L / 2 + 30.2, 0xa8a8a2, 57.6, Math.PI], ['sedan', L / 2 - 20.4, 0x3a3f45, 57.6, Math.PI]].forEach((c, i) => {
    const v = K.make(c[0], { seed: 51 + i, color: c[2] }); v.position.set(c[1], 0, zF + c[3]); v.rotation.y = c[4]; TXT.add(R, v); TXT.contact(R, v);
  });
  F.lotLamp(THREE, TXT, K, R, -L / 2 + 16, zF + 46, { i: 150, seed: 43 });
  F.lotLamp(THREE, TXT, K, R, L / 2 - 16, zF + 46, { i: 150, seed: 44, ry: Math.PI });
  F.lotLamp(THREE, TXT, K, R, -L / 2 - 16, zF + 8, { ry: -Math.PI / 2, i: 150, seed: 37 });
  /* the near row, 22 m from the lens: dark cars nosed away, an island with crape myrtles */
  F.stalls(THREE, TXT, R, -16, CZ - 20, 12, { dir: -1 });
  [['pickup', -13.5, 0x2c2f33], ['sedan', -5.2, 0x8b8f93], ['sedan', 11.4, 0x22262a]].forEach((c, i) => {
    const v = K.make(c[0], { seed: 71 + i, color: c[2] }); v.position.set(c[1], 0, CZ - 22.8); v.rotation.y = Math.PI; TXT.add(R, v); TXT.contact(R, v);
  });
  const isl = TXT.roundedBox(34, 0.15, 3, 0.05, new THREE.MeshStandardMaterial({ color: 0x8e887d, roughness: 0.9 })); isl.position.set(-2, 0.075, CZ - 17.5); TXT.add(R, isl);
  [-21, 17].forEach((x, i) => { const m = K.make('crape_myrtle', { seed: 80 + i, bloom: false, height: 4.5 }); m.position.set(x, 0.15, CZ - 17.5); TXT.add(R, m); TXT.contact(R, m); });
  { const pl = new THREE.PointLight(F.SODIUM, 160, 30, 2); pl.position.set(-4, 8.6, CZ - 4); R.scene.add(pl); }
  [-L / 2 - 26, L / 2 + 24].forEach((x, i) => { const o = K.make('live_oak', { seed: 60 + i, height: 9 }); o.position.set(x, 0, zF + 6); TXT.add(R, o); TXT.contact(R, o); });
  /* where the two columns stand in frame 3: two steel base plates on the lot 12 m from the lens */
  const plateM = TXT.mat.steel({ roughness: 0.5 });
  const XA = -0.62, XB = 0.45, CZC = CZ - 12;
  [XA, XB].forEach((x) => { const p = TXT.roundedBox(0.8, 0.03, 0.8, 0.01, plateM); p.position.set(x, 0.015, CZC); TXT.add(R, p); TXT.contact(R, p);
    [[-0.3, -0.3], [0.3, -0.3], [-0.3, 0.3], [0.3, 0.3]].forEach((b) => { const bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.05, 8), plateM); bolt.position.set(x + b[0], 0.045, CZC + b[1]); R.scene.add(bolt); }); });
%EXTRA%
"""
COLS = f"""  /* THE TWO LIMITS AS TWO STEEL COLUMNS AT ONE SCALE, 0.25 m per percentage point from one zero
   * line: figures.json column_daily_m and column_weekly_m. A resident stands beside them. */
  const DAILY_M = {FIG['column_daily_m']}, WEEKLY_M = {FIG['column_weekly_m']};
  const steel = TXT.mat.clay(0x8c8a86, {{ metalness: 0.9, roughness: 0.35 }});
  const colA = TXT.roundedBox(0.5, DAILY_M, 0.5, 0.03, steel), colB = TXT.roundedBox(0.5, WEEKLY_M, 0.5, 0.03, steel);
  colA.position.set(XA, DAILY_M / 2 + 0.03, CZC); colB.position.set(XB, WEEKLY_M / 2 + 0.03, CZC);
  TXT.add(R, colA); TXT.add(R, colB); TXT.contact(R, colA); TXT.contact(R, colB);
  const man = K.make('person', {{ seed: 14, role: 'resident', pose: 'stand', build: 'male', hat: 'none', detail: 'full' }});
  man.position.set(XB + 0.78, 0, CZC + 0.2); man.rotation.y = -0.5; TXT.add(R, man); TXT.contact(R, man);
  window.__cols = {{ topA: F.project(THREE, R, [XA, DAILY_M + 0.03, CZC]), topB: F.project(THREE, R, [XB, WEEKLY_M + 0.03, CZC]) }};
"""
LABELS3 = """  const svg = document.getElementById('lead');
  const lab = (id, txt, at, x, y) => {
    const el = document.getElementById(id); el.textContent = txt;
    el.style.left = x + 'px'; el.style.top = y + 'px';
    const b = el.getBoundingClientRect();
    const from = x < at[0] ? [b.right + 8, b.top + b.height / 2] : [b.left - 8, b.top + b.height / 2];
    const end = [at[0] + (x < at[0] ? -10 : 10), at[1] + 4];
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    p.setAttribute('points', [from, [end[0], from[1]], end].map(q => q.join(',')).join(' '));
    p.setAttribute('fill', 'none'); p.setAttribute('stroke', '#EDE4D6'); p.setAttribute('stroke-width', '2'); svg.appendChild(p);
    (window.__txLeaders = window.__txLeaders || []).push({ target: txt, at: end, to: end });
  };
  lab('la', '3% a day', __cols.topA, __cols.topA[0] - 250, __cols.topA[1] + 40);
  lab('lb', '8% a week', __cols.topB, __cols.topB[0] - 290, __cols.topB[1] + 10);
"""
LABELS7 = """  /* one label per dark breezeway core, the limits in the order the judgment lists them,
   * set in the sky above the ridge with a leader down to the core */
  const svg = document.getElementById('lead');
  const NAMES = ["third-party<br>nonpublic data", "pooling<br>across owners", "rivals'<br>sensitive data", "required<br>acceptance", "built-in<br>rent floors"];
  const LIMITS = %LIMITS%;
  const cores = hero.userData.cores.slice(0, LIMITS);
  cores.forEach((c, i) => {
    const at = F.project(THREE, R, [c.x, D.eave - 0.4, zF]);
    const ridge = F.project(THREE, R, [c.x, D.ridge + 0.3, 0]);
    const el = document.getElementById('c' + i); el.innerHTML = NAMES[i];
    const b = el.getBoundingClientRect(), row = i % 2;
    const x = Math.max(80, Math.min(1000 - b.width, at[0] - b.width / 2)), y = ridge[1] - 24 - b.height - row * 70;
    el.style.left = x + 'px'; el.style.top = y + 'px';
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    const end = [at[0], at[1] - 4];
    p.setAttribute('x1', at[0]); p.setAttribute('y1', y + b.height + 6); p.setAttribute('x2', end[0]); p.setAttribute('y2', end[1]);
    p.setAttribute('stroke', '#EDE4D6'); p.setAttribute('stroke-width', '2'); svg.appendChild(p);
    (window.__txLeaders = window.__txLeaders || []).push({ target: 'core ' + (i + 1) + ', ' + NAMES[i].replace('<br>', ' '), at: end, to: end });
  });
"""
f3 = page(3, 'DIAGRAM', 'RENDERED in the declared nightSodium world. The shared lot camera, the five cores lit, two steel columns at one scale.',
  "3% a day,<br>8% a week",
  "The complaint says AIRM and YieldStar can accept recommendations automatically, and the default limits are 3% a day and 8% a week. It says a landlord who turns auto-accept on in effect hands pricing authority to RealPage inside those limits.",
  "The auto-accept limits", "c27 c28 c29   DRAWN TO ONE SCALE",
  SCENE.replace('%LAMPS%', '').replace('%EXPO%', '1.0').replace('%EXTRA%', COLS),
  after=LABELS3, extra_html='<svg class="lead" id="lead"></svg><div class="lab" id="la"></div><div class="lab" id="lb"></div>')
open('../../slides/slide-03.html', 'w').write(f3)
f7 = page(7, 'DIAGRAM', 'RENDERED in the declared nightSodium world. Frame 3 camera and lot, the five cores dark, the columns gone, the storefront on.',
  "The screen stays on",
  "Five of its limits on how Pinnacle may price. It isn't a ban on RealPage, and the government may review the code and pseudocode of Pinnacle's own product.",
  "What the judgment switches off", "c39 c40 c41 c50 c51 c46 c53   DRAWN",
  SCENE.replace('%LAMPS%', ', lampsOn: false').replace('%EXPO%', '0.82').replace('%EXTRA%', COLS),
  after=LABELS7.replace('%LIMITS%', str(LIMITS)), extra_html='<svg class="lead" id="lead"></svg>' + ''.join(f'<div class="lab" id="c{i}"></div>' for i in range(5)),
  extra_css='  .lab { font-size:24px; text-align:center; }', hmin=96, hmax=118, hlines=1)
open('../../slides/slide-07.html', 'w').write(f7)
