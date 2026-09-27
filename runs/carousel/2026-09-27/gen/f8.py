import sys, json
sys.path.insert(0, '.')
from common import page
FIG = json.load(open('../../figures.json'))
v = lambda k: FIG[k]['value'] if isinstance(FIG[k], dict) else FIG[k]
scene = f"""  const R = TXT.setup(gl, {{ w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 0.6], exposure: W.exposure * 0.82, tone: W.tone, fov: 40 }});
  /* ONE LANDLORD. Across the road three buildings stand in a row: the hero in the middle with its
   * five breezeway cores dark, as on frame 7, and a neighbour either side with its cores lit and
   * {v('other_building_front_units')} front units each, lit_units_low and lit_units_high of them
   * lit: figures.json, the complaint's low and high penetration share applied to the units,
   * rounded half up. The units are taken in one fixed order so the lit ones scatter. */
  const LIT_LOW = {v('lit_units_low')}, LIT_HIGH = {v('lit_units_high')};
  const ORDER = [[0,1],[3,2],[2,0],[1,2],[3,0],[0,2],[2,1],[1,0],[3,1],[0,0],[2,2],[1,1]];
  const mk = (n, seed, brick, siding) => F.hero(K, {{ seed, cores: 1, groupBays: 2, office: false, lampsOn: true, lampI: 10, poolI: 30,
    brick, siding, litUnits: ORDER.slice(0, n) }});
  const hero = F.hero(K, {{ office: false, lampsOn: false, lit: 0 }});
  const HL = hero.userData.dims.L;
  const nA = mk(LIT_LOW, 21, '#b99c7c', '#b8b9ad'), nB = mk(LIT_HIGH, 22, '#8f5a44', '#d2cbbb');
  const NL = nA.userData.dims.L, GAPB = 3;
  nA.position.set(-HL / 2 - GAPB - NL / 2, 0, 4); nB.position.set(HL / 2 + GAPB + NL / 2, 0, 4);
  [hero, nA, nB].forEach((b) => {{ TXT.add(R, b); TXT.contact(R, b); }});
  /* the lot in front of them, the four lane road at the camera, the near kerb the lens stands on */
  const CZ = 185;  /* the lens stands on the near kerb 60 m in from the road's far side */
  const road = K.make('road', {{ length: 600, lanes: 4, sidewalk: false, seed: 5 }}); road.position.set(0, 0, 104); road.rotation.y = 0.0; TXT.add(R, road);
  TXT.frame(R, {{ from: [-110, 2.0, 124], look: [-5, 11.5, 0] }});
  TXT.sky(R);
  TXT.deckRig(R, W.rig, {{ target: [0, 0, 60], distance: 220, shadowFar: 480 }});
  TXT.ground(R, {{ surface: 'asphalt', size: 6000, seed: 17 }});
  [-78, 78].forEach((x, i) => F.lotLamp(THREE, TXT, K, R, x, 24, {{ ry: Math.PI, i: 520, seed: 48 + i, height: 9 }}));
  [-110, 105].forEach((x, i) => {{ const o = K.make('live_oak', {{ seed: 90 + i, height: 9 }}); o.position.set(x, 0, 14); TXT.add(R, o); TXT.contact(R, o); }});
  /* the near verge under the lens: a streetlight just off frame left, its sodium pool on the lot */
  {{ const pl = new THREE.PointLight(F.SODIUM, 700, 40, 2); pl.position.set(-108, 9, 104); R.scene.add(pl); }}
  F.stalls(THREE, TXT, R, -112, 86, 12, {{ dir: -1 }});
  [['sedan', -17.5, 0x3b3e42], ['pickup', -6.3, 0x2c2f33], ['suv', 8.1, 0x44484c], ['sedan', 19.4, 0x6e7478]].forEach((c, i) => {{
    const v = K.make(c[0], {{ seed: 61 + i, color: c[2] }}); v.position.set(c[1] - 88, 0, 83.5); v.rotation.y = Math.PI; TXT.add(R, v); TXT.contact(R, v); }});
  R.scene.traverse((m) => {{ if (m.isMesh && m.material && m.material.emissive && m.material.emissiveIntensity > 1 && (m.material.emissive.getHex() & 0xff) > 0x80) m.material.emissiveIntensity = 0; }});
"""
f8 = page(8, 'GRID', 'RENDERED in the declared nightSodium world. From the near kerb, the hero dark between two lit neighbours.',
  "It binds one landlord",
  "The judgment is proposed and Pinnacle admits nothing. The government's claims against the remaining defendants go on. The complaint says AIRM and YieldStar penetration runs from at least around 26% to 69% in each listed submarket.",
  "The rest of the case", "c55 c56 c58 c59 c36   DRAWN",
  scene)
open('../../slides/slide-08.html', 'w').write(f8)
