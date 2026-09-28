import sys, json; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  /* THE DATA. The two lines of the ledger as the two rails of a pipe corral fence. The top rail
   * carries one loose camera head for each camera the report counts as installed, 33, at one pitch
   * so every head is one size. The lower rail is the line the order named, and nothing stands on it.
   * detections_reported is not a zero, it is an empty rail, and no numeral is drawn near it. */
  const INSTALLED = 33, DETECTIONS_REPORTED = [];
  const PITCH = 0.42, RUN = (INSTALLED - 1) * PITCH, LEN = RUN + 1.2;
  const TOP = 1.95, LOW = 0.55;
  const fence = K.make('pipe_rail_fence', { seed: 2, length: LEN, spacing: LEN / 6, rails: [TOP, LOW], post: 2.08,
                                            flags: [0, 6], flag: F.ACCENT, flagAt: LOW + 0.1 });
  fence.position.set(0, 0, 0); TXT.add(R, fence);
  for (let i = 0; i < INSTALLED; i++) {
    const hd = K.make('wildfire_camera_station', { part: 'head', seed: 40 + i, pan: 1.3 + 0.08 * Math.sin(i * 1.7), tilt: -0.04 });   /* turned side on, so each white housing shows its length and not its dark window (panel round 4) */
    hd.position.set(-RUN / 2 + i * PITCH, TOP + 0.0365, 0.09); TXT.add(R, hd);
  }
  DETECTIONS_REPORTED.forEach(() => {});             /* the lower rail carries what the report gave it */

  /* the station behind the corral on the right, its heads toward the rails */
  const hero = F.station(K, { pan: [0.3, -0.3], tilt: [-0.06, -0.06] });
  hero.position.set(18, 0, -30); TXT.add(R, hero); TXT.contact(R, hero);   /* 57 m out, so its heads read smaller than the rail's (round 1) */
  const padM = new THREE.MeshStandardMaterial({ color: 0xd9ccb0, map: K.tex('concrete'), roughness: 0.96 });
  const pad = TXT.roundedBox(6, 0.06, 6, 0.02, padM); pad.position.set(18, 0.03, -30); TXT.add(R, pad);

  TXT.frame(R, { from: [-4.5, 1.2, 26.6], look: [-0.45, 2.9, 0] });   /* panel round 2: the whole row inside the frame, so all 33 can be counted */   /* within 10 degrees of square on, so the 33 heads stay one size (round 1) */
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -4], distance: 70, shadowFar: 180 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 7000, seed: 29 });
  F.grass(TXT, R, { count: 30000, area: [-50, -150, 50, 20], avoid: [[-8, -0.6, 8, 0.6], [-45, -2.0, 45, 9.0], [-60, -25, 60, -17], [15, -33, 21, -27]], scale: [0.55, 1.05] });
  F.caprock(K, TXT, R, { x: 330, z: -430, width: 620, height: 20, ry: 0.05 });   /* panel round 3: wide enough that its cut end leaves the frame */   /* round 2: in the thinned haze */
  /* a caliche two track runs along the corral in the foreground */
  const track = K.make('caliche_road', { seed: 12, length: 90, curve: 0.04 });
  track.position.set(0, 0, -21); track.rotation.y = Math.PI / 2 + 0.02; TXT.add(R, track);   /* round 2: the two track runs behind the corral, so the bare rail reads against pale caliche */
  TXT.weather(R, {});
  /* the two labels ride the two rails, measured through this camera */
  /* the two labels ride the two rails, measured through this camera: the count just over the
   * heads, the order's line just under the bare rail with the accent bar beneath it (round 1) */
  const q = -RUN / 2 + RUN * 0.12;
  const pT = F.project(THREE, R, [q, TOP + 0.62, 0.09]), pL = F.project(THREE, R, [q, LOW, 0.09]);
  const lt = document.getElementById('labT'), ll = document.getElementById('labL'), acc = document.getElementById('acc');
  lt.style.left = '80px'; lt.style.top = (pT[1] - 44) + 'px';
  ll.style.left = '80px'; ll.style.top = (pL[1] + 16) + 'px';
  acc.style.top = (pL[1] + 16 + 42) + 'px';
  { const rg = document.createRange(); rg.selectNodeContents(ll); acc.style.width = Math.round(rg.getBoundingClientRect().width) + 'px'; }   /* the whole line underlined (round 2) */
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.45, to: pT[1] - 10 });   /* round 2: the storm deck deepened down to the count label, so it holds its contrast over the haze */
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(6)
c=json.load(open('/home/user/TexasAIDocket/out/2026-09-28/copy.json'))['slides']['S6']
shell.write(6,
  "Archetype DIAGRAM. RENDERED through txthree.js in the deck's declared stormFront world. The two lines of the ledger as the two rails of a pipe corral fence: 33 loose camera heads on the top rail, one for each camera the report counts as installed, and the lower rail, the line the order named, bare between two posts tied with accent flagging, the station behind on the right.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:700px;", dek_css="width:710px;", fit=(84, 116, 3),
  extra_css='  .lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.04em; color:#F1ECE3; z-index:12; white-space:nowrap; text-shadow:0 0 6px rgba(12,12,14,0.9), 0 1px 12px rgba(12,12,14,0.7); }\n  #acc { position:absolute; left:80px; width:420px; height:14px; background:#2A7A9E; z-index:12; }',
  extra_html=f'<div id="acc"></div>\n<div class="lab" id="labT">{c["labels"][0]}</div>\n<div class="lab" id="labL">{c["labels"][1]}</div>')
