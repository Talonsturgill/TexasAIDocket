import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('units', 'acres') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 32, near: 0.2, far: 12000 });
  /* THE COVER. A monument camera at the west end of a lane between two block rows, looking east
   * down the lane with the low sun at its back: every unit's west end and the lane's caliche take
   * the warm light, the rows converge on the horizon, and the count is felt as depth. */
  const S = F.site(FIG.acres);
  const probe = F.yard(K, THREE, TXT, { count: FIG.units });
  const zs0 = Array.from(new Set(probe.userData.units.map(u => Math.round(u[1] * 10) / 10))).sort((a, b) => a - b);
  const lz0 = (zs0[Math.floor(zs0.length / 2)] + zs0[Math.floor(zs0.length / 2) + 1]) / 2, xmin = Math.min.apply(null, probe.userData.units.map(u => u[0]));
  /* the units within about fifty metres of the lens on both sides of the lane are the full model */
  const yard = F.yard(K, THREE, TXT, { count: FIG.units, detail: [xmin - 5, lz0 - 12, xmin + 52, lz0 + 12] });
  yard.position.set(S.yard[0], 0, S.yard[2]); TXT.add(R, yard);
  F.pad(K, THREE, TXT, R, S.side);
  const zs = Array.from(new Set(yard.userData.units.map(u => Math.round(u[1] * 10) / 10))).sort((a, b) => a - b);
  const laneZ = (zs[Math.floor(zs.length / 2)] + zs[Math.floor(zs.length / 2) + 1]) / 2;
  const xs = yard.userData.units.map(u => u[0]), x0 = Math.min.apply(null, xs);
  const who = K.make('person', { seed: 4, role: 'worker', pose: 'stand', hat: 'hard', vest: true });
  who.position.set(x0 + 3.5, 0, laneZ + 0.9); who.rotation.y = -Math.PI / 2 - 0.4; TXT.add(R, who); TXT.contact(R, who);
  TXT.frame(R, { from: [x0 - 18, 1.6, laneZ - 0.2], look: [x0 + 120, 1.6 + 138 * Math.tan(2.4 * Math.PI / 180), laneZ - 0.6] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [x0 + 40, 0, laneZ], distance: 260, shadowFar: 700, normalBias: 0.05 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  F.desert(TXT, R, { area: [x0 - 60, laneZ - 60, x0 - 3, laneZ + 60], avoid: [[x0 - 24, laneZ - 4, x0 - 3, laneZ + 4]], scrub: 220, rock: 0, grass: 1800 });
  TXT.scatter(R, { kind: 'grass', count: 90, area: [x0 - 2, laneZ - 1.4, x0 + 60, laneZ + 1.4], seed: 71, scale: [0.3, 0.55], clumping: 0.7, colors: [0xb7a07a, 0xa89272, 0xc2ad86] });
  TXT.scatter(R, { kind: 'rock', count: 5000, area: [x0 - 17, laneZ - 1.7, x0 + 6, laneZ + 1.5], seed: 81, scale: [0.012, 0.04], colors: [0xa89c86, 0x8f8676, 0xb8ad98] });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 380, seed: 31 });
  TXT.weather(R, {});
  /* the accent under the hook's last line: the one customer who would carry the plant's costs */
  { const hk = document.getElementById('hook'), rg = document.createRange(); rg.selectNodeContents(hk); const rs = rg.getClientRects(), last = rs[rs.length - 1], a = document.getElementById('acc');
    a.style.top = (last.bottom + 4) + 'px'; a.style.height = '10px';
    const dk = document.querySelector('.dek'); dk.style.top = (parseFloat(dk.style.top) + 14) + 'px'; a.style.width = Math.round(last.width) + 'px'; }
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.4, floor: 0.35 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.hook', '.dek']);
  TXDECK.finish(cx);
  window.__txDrawn = { units: yard.userData.drawn, detailed: yard.userData.detailed };
'''
k,h,b,s = shell.copy(1)
shell.write(1, "Archetype FULL_BLEED. RENDERED through txthree.js in the deck's goldenHour world. THE COVER. The field of 813 modular gas generators from a monument camera at the west end of a lane between two block rows, looking east with the low sun behind, the rows converging on the horizon.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:900px;", dek_css="width:860px;", fit=(92, 124, 2),
  extra_css="  #acc { position:absolute; left:82px; height:14px; background:#9A3B2A; z-index:12; }", extra_html='<div id="acc"></div>\n')
