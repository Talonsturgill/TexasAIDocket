import sys; sys.path.insert(0,'.'); import shell, json; from common import *
scene = figs('units', 'acres', 'plant_mw', 'plant_share_of_peak', 'first_request_mw', 'second_request_mw', 'peak_commit_mw') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40, near: 0.2, far: 12000 });
  /* THE RAMP AT ONE SCALE. Two lines ruled on the caliche south of the field, one metre of line
   * for every MW_PER_M megawatts: a pale line to the committed peak with survey stakes at the first
   * request, the second, and the peak; a grey line in the enclosures' own paint that stops at the
   * plant. Both lines start at one origin stake. The camera stands high and square to them. */
''' + SITE + r'''
  const MW_PER_M = 1000 / 14, L = (mw) => mw / MW_PER_M;
  const oz = Math.max.apply(null, yard.userData.units.map(u => u[1])) + 16, ox = -L(FIG.peak_commit_mw) / 2;
  const paint = (c, e) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.8, emissive: c, emissiveIntensity: e || 0 });
  /* the lines are raised painted beams on the caliche, 0.3 m high, so a reader sees two lengths and not two scratches */
  const line = (len, z, m) => { const b = TXT.roundedBox(len, 0.3, 0.45, 0.04, m); b.position.set(ox + len / 2, 0.15, z); b.castShadow = true; b.receiveShadow = true; TXT.add(R, b); TXT.contact(R, b); };
  /* the peak is a primer grey beam, the plant a tier in the enclosures' own paint laid on it from the same origin */
  const beam = TXT.roundedBox(L(FIG.peak_commit_mw), 0.4, 0.8, 0.04, paint(0x6c675f, 0.02)); beam.position.set(ox + L(FIG.peak_commit_mw) / 2, 0.2, oz); beam.castShadow = false; beam.receiveShadow = true; TXT.add(R, beam); TXT.contact(R, beam);
  /* the plant is its own bar from the same origin, in front of the peak's beam: a comparison of sizes, never an allocation of load, since no claim says which load the plant serves */
  /* the bar stands 1.6 m nearer the lens than the beam, so it is scaled and placed by the ratio of the two depths and its ends land on the beam's own zero and 366 on screen */
  const PX = ox + L(FIG.peak_commit_mw) / 2, KD = (28 - 1.6) / 28, tx0 = PX + (ox - PX) * KD, tlen = L(FIG.peak_commit_mw) * FIG.plant_share_of_peak * KD;
  const tier = TXT.roundedBox(tlen, 0.4, 0.8, 0.03, paint(0xd4d0c6, 0.32)); tier.position.set(tx0 + tlen / 2, 0.2, oz + 1.6); tier.castShadow = true; TXT.add(R, tier); TXT.contact(R, tier);
  const stakeM = new THREE.MeshStandardMaterial({ color: 0xf2f0ea, roughness: 0.6 });
  const stake = (mw, z) => { const x = ox + L(mw); const p = K.cyl(0.05, 0.05, 1.8, stakeM, x, 0, z, 10); TXT.add(R, p); return [x, 1.8, z]; };
  const at = {
    r1: stake(FIG.first_request_mw, oz),
    r2: stake(FIG.first_request_mw + FIG.second_request_mw, oz),
    peak: stake(FIG.peak_commit_mw, oz),
    plant: [ox + L(FIG.plant_mw), 0.0, oz],
    plant0: [ox, 0.0, oz]
  };
  at.o = stake(0, oz);
  const mid = ox + L(FIG.peak_commit_mw) / 2;
  TXT.frame(R, { from: [mid, 6.5, oz + 28], look: [mid, 6.5, oz - 6] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [mid, 0, oz], distance: 120, shadowFar: 320, normalBias: 0.05 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.desert(TXT, R, { area: [mid - 60, oz + 4, mid + 60, oz + 60], avoid: [[mid - 22, oz - 2, mid + 22, oz + 6]], scrub: 200, rock: 0, grass: 1600 });
  TXT.scatter(R, { kind: 'rock', count: 3200, area: [mid - 24, oz + 1.5, mid + 24, oz + 22], seed: 93, scale: [0.012, 0.04], colors: [0xa89c86, 0x8f8676, 0xb8ad98] });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 380, seed: 31 });
  TXT.weather(R, {});
  const labs = Array.prototype.slice.call(document.querySelectorAll('.lab')), svg = document.getElementById('lead'), NS = 'http://www.w3.org/2000/svg', leaders = [];
  /* every label names its own segment: a bracket over the stretch it measures, ticked down to the
   * stakes at its two ends, the label centred over the bracket. The peak's label ends at its own
   * stake. The plant's bracket runs under its tier and its label sits under the bracket */
  const bracket = (pts) => { const pl = document.createElementNS(NS, 'polyline'); pl.setAttribute('points', pts.map(p => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ')); pl.setAttribute('fill', 'none'); pl.setAttribute('stroke', '#F1ECE3'); pl.setAttribute('stroke-width', '2'); svg.appendChild(pl); };
  const P = {}; Object.keys(at).forEach(k => { P[k] = F.project(THREE, R, at[k]); });
  const top = P.o[1] - 18;
  const seg = (lab, a, b) => {
    const x0 = P[a][0], x1 = P[b][0];
    bracket([[x0 + 1, P[a][1] - 4], [x0 + 1, top], [x1 - 1, top], [x1 - 1, P[b][1] - 4]]);
    lab.style.whiteSpace = 'normal'; lab.style.textAlign = 'center'; lab.style.width = (x1 - x0 - 6) + 'px';
    const hh = lab.getBoundingClientRect().height; lab.style.left = (x0 + 3) + 'px'; lab.style.top = (top - 10 - hh) + 'px';
    leaders.push({ target: 'the stakes at ' + a + ' and ' + b, at: [x1, P[b][1] - 4], to: [x1, P[b][1] - 4] });
  };
  labs.forEach(function (lab) {
    const key = lab.dataset.at;
    if (key === 'r1') seg(lab, 'o', 'r1');
    else if (key === 'r2') seg(lab, 'r1', 'r2');
    else if (key === 'peak') { const p = P.peak, w = lab.getBoundingClientRect().width, hh = lab.getBoundingClientRect().height;
      bracket([[p[0], p[1] - 4], [p[0], top - 10]]); lab.style.left = Math.min(1000 - w, p[0] + 8 - w) + 'px'; lab.style.top = (top - 10 - hh) + 'px';
      leaders.push({ target: 'the stake at peak', at: [p[0], p[1] - 4], to: [p[0], p[1] - 4] }); }
    else if (key === 'plant') { const a0 = P.plant0, a1 = P.plant, yb = a0[1] + 22, w = lab.getBoundingClientRect().width;
      bracket([[a0[0] + 1, a0[1] + 4], [a0[0] + 1, yb], [a1[0] - 1, yb], [a1[0] - 1, a1[1] + 4]]);
      lab.style.left = ((a0[0] + a1[0]) / 2 - w / 2) + 'px'; lab.style.top = (yb + 10) + 'px';
      leaders.push({ target: 'the ends of the plant tier', at: [a1[0], a1[1] + 4], to: [a1[0], a1[1] + 4] }); }
  });
  window.__txLeaders = leaders;
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45, floor: 0.45 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.hook', '.dek', '.lab']);
  TXDECK.finish(cx);
  window.__txDrawn = { plant_len_m: L(FIG.plant_mw), peak_len_m: L(FIG.peak_commit_mw) };
'''
k,h,b,s = shell.copy(4)
labs = json.load(open('/home/user/TexasAIDocket/out/2026-09-29/copy.json'))['slides']['S4']['labels']
spec = [('r1', 90), ('r2', 150), ('peak', 90), ('plant', 60)]
labhtml = ''.join(f'<div class="lab" data-at="{a}" data-rise="{r}" style="left:80px; top:900px;">{t}</div>\n' for (a, r), t in zip(spec, labs))
shell.write(4, "Archetype DIAGRAM. RENDERED through txthree.js in the deck's goldenHour world. Two lines ruled on the caliche south of the field at one scale: a pale line to the committed peak with stakes at the first and second requests, a grey line that stops at the plant.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:900px;", dek_css="width:860px;", fit=(84, 116, 2), extra_css=LAB_CSS, extra_html=LEAD_HTML + labhtml)
