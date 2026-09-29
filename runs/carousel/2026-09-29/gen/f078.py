import sys, json; sys.path.insert(0,'.'); import shell
FIG = json.load(open('/home/user/TexasAIDocket/out/2026-09-29/figures.json'))
def scene(n):
    paid_key = 'bridge_years_max' if n == 7 else 'service_life_years'
    return r'''
  const FIG = ''' + json.dumps({k: FIG[k]['value'] for k in ('units', 'acres', 'service_life_years', 'bridge_years_max', 'bridge_expected_under_years')}) + r''';
  const PAID = FIG.''' + paid_key + r''';
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40, near: 0.3, far: 12000 });
  /* THE YEAR FENCE SIDE ON, one camera on frames 7 and 8. The fence runs north to south along the
   * pad's west edge, post 0 at its north end, one span per year of the estimated service life. The
   * camera stands in the desert west of it looking due east, square to the fence, so every span
   * projects at the same length and the painted run is the share of the life it stands for. The
   * low sun is behind the camera and lights every panel face on. Frame 7 paints the bridge's
   * panels, frame 8 every panel. Nothing else changes. */
  const S = F.site(FIG.acres);
  const yard = F.yard(K, THREE, TXT, { count: FIG.units });
  yard.position.set(S.yard[0], 0, S.yard[2]); TXT.add(R, yard);
  F.pad(K, THREE, TXT, R, S.side);
  const FX = S.fence[0], SP = 1.8, LEN = FIG.service_life_years * SP, Z0 = -LEN / 2;
  const yf = F.yearFence(K, THREE, TXT, { spans: FIG.service_life_years, paid: PAID, spacing: SP, postH: 3.0, collarAt: FIG.bridge_expected_under_years });
  yf.rotation.y = -Math.PI / 2; yf.position.set(FX, 0, Z0); TXT.add(R, yf); TXT.contact(R, yf);
  const blk = F.block(K, { units: 5, seed: 8 });
  blk.rotation.y = Math.PI / 2; blk.position.set(FX + 24, 0, 8); TXT.add(R, blk); TXT.contact(R, blk);
  const D = 73.4, EYE = [FX - D, 4.0, 0];
  TXT.frame(R, { from: EYE, look: [FX, 4.0 + D * Math.tan(7 * Math.PI / 180), 0] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [FX, 0, 0], distance: 160, shadowFar: 420, normalBias: 0.05 });
  TXT.ground(R, { surface: 'caliche', color: F.DESERT, size: 16000, seed: 11 });
  /* scrub and grass up to the fence, none on the strip of ground the footer sits over */
  F.desert(TXT, R, { area: [FX - D + 27, -60, FX - 1.2, 60], scrub: 420, rock: 260, grass: 2600, grassArea: [FX - D + 27, -45, FX - 1.2, 45] });
  TXT.scatter(R, { kind: 'rock', count: 2600, area: [FX - D + 8, -30, FX - D + 28, 30], seed: 91, scale: [0.012, 0.035], colors: [0xa89c86, 0x8f8676, 0xb8ad98] });
  F.ridge(THREE, TXT, R, { x: 9000, peak: 380, seed: 31 });
  TXT.weather(R, {});
  /* the posts the labels name, projected through this camera: post i stands at z = Z0 + i * SP */
  const post = (i, y) => F.project(THREE, R, [FX, y == null ? 3.0 : y, Z0 + i * SP]);
  const svg = document.getElementById('lead'), NS = 'http://www.w3.org/2000/svg', leaders = [];
  const line = (pts) => { const pl = document.createElementNS(NS, 'polyline'); pl.setAttribute('points', pts.map(p => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ')); pl.setAttribute('fill', 'none'); pl.setAttribute('stroke', '#14161A'); pl.setAttribute('stroke-width', '2'); svg.appendChild(pl); };
  const labs = Array.prototype.slice.call(document.querySelectorAll('.lab'));
  const p0 = post(0), pP = post(PAID), pL = post(FIG.service_life_years);
  const rowY = p0[1] - 212;
  /* the first label sits over the painted run, left aligned to post 0, the accent bar under it
   * spans post 0 to the last painted post, and one tick drops from each end of the bar */
  const l0 = labs[0]; l0.style.left = p0[0] + 'px'; l0.style.top = (rowY - 36) + 'px';
  const a = document.getElementById('acc'); a.style.left = p0[0] + 'px'; a.style.top = rowY + 'px'; a.style.width = (pP[0] - p0[0]) + 'px';
  line([[p0[0] + 1, rowY + 10], [p0[0] + 1, p0[1] - 8]]); line([[pP[0] - 1, rowY + 10], [pP[0] - 1, pP[1] - 8]]);
  leaders.push({ target: 'the top of fence post 0', at: [p0[0], p0[1] - 8], to: [p0[0], p0[1] - 8] });
  leaders.push({ target: 'the top of fence post ' + PAID, at: [pP[0], pP[1] - 8], to: [pP[0], pP[1] - 8] });
  if (labs[1]) {
    const l1 = labs[1], w = l1.getBoundingClientRect().width;
    l1.style.left = (pL[0] - w) + 'px'; l1.style.top = (rowY - 36 - 44) + 'px';
    line([[pL[0] - 1, rowY - 36 - 44 + 34], [pL[0] - 1, pL[1] - 8]]);
    leaders.push({ target: 'the top of fence post ' + FIG.service_life_years, at: [pL[0], pL[1] - 8], to: [pL[0], pL[1] - 8] });
  }
  window.__txLeaders = leaders;
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.3, floor: 0.3, floorH: 260 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.hook', '.dek']);
  TXDECK.finish(cx);
  window.__txDrawn = { spans: FIG.service_life_years, paid: PAID, spanPx: (pL[0] - p0[0]) / FIG.service_life_years, paidPx: pP[0] - p0[0] };
'''
for n in (7, 8):
    k,h,b,s = shell.copy(n)
    c = json.load(open('/home/user/TexasAIDocket/out/2026-09-29/copy.json'))['slides'][f'S{n}']
    labhtml = ''.join(f'<div class="lab">{t}</div>\n' for t in c['labels'])
    shell.write(n,
      ("Archetype SPLIT_HORIZON. RENDERED through txthree.js in the deck's goldenHour world. The year fence side on, twenty spans with sheet panels, one per year of the estimated service life, the camera square to it looking east with the sun behind. " +
       ("The bridge's panels are painted capitol granite, a galvanised collar on the post that ends the witness's expected span, the rest primer." if n == 7 else "Frame 7's camera, fence and block unchanged, every panel painted capitol granite.")),
      k, h, b, s, scene(n), hook_css="left:80px; top:150px; width:900px;", dek_css="width:916px;", fit=(72, 96, 2),
      extra_css='''  .lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; letter-spacing:0.03em; color:#14161A; z-index:12; white-space:nowrap; text-shadow:0 0 6px rgba(236,230,218,0.7), 0 0 14px rgba(236,230,218,0.45); }
  svg#lead { position:absolute; left:0; top:0; width:1080px; height:1350px; z-index:11; overflow:visible; }
  #acc { position:absolute; height:10px; background:#9A3B2A; z-index:12; }''',
      extra_html='<svg id="lead" width="1080" height="1350" viewBox="0 0 1080 1350"></svg>\n<div id="acc"></div>\n' + labhtml)
