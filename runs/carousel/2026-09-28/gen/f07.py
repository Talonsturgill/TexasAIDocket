import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 36 });
  /* THE DATA. Two lengths of the station's own galvanized tube, one scale, one end plate: the plan's
   * 2026 camera capital and the anticipated 2026 camera capital. Both lie at z = 0, square on to the
   * lens, stacked on timber dunnage the way pipe is stacked in a yard, so the ratio of their lengths
   * on the image is the ratio of the dollars. */
  const PLAN = 6423554, ANTICIPATED = 10537400;
  const BASE = 2.9, LP = BASE, LA = BASE * ANTICIPATED / PLAN;   /* metres of tube per plan */
  const X0 = -3.0, RT = 0.11;
  const galv = new THREE.MeshStandardMaterial({ color: 0xe4e6e5, roughness: 0.42, metalness: 0.18 });   /* panel round 1: pale galvanizing gone chalky, lighter than the grass */   /* round 2: bright galvanizing that takes the storm sky on its top */   /* round 1: at 0.45 metal the tube mirrored the straw and read as a log */   /* hot dip galvanizing gone dull in the yard, which takes the light rather than mirroring the storm */
  const galvDark = new THREE.MeshStandardMaterial({ color: 0x6d7173, roughness: 0.5, metalness: 0.8 });
  const wood = new THREE.MeshStandardMaterial({ color: 0xffffff, map: K.tex('wood', { color: '#7a6a55' }), roughness: 0.92 });
  function tube(len, y) {
    const t = new THREE.Mesh(new THREE.CylinderGeometry(RT, RT, len, 24), galv);
    t.rotation.z = Math.PI / 2; t.position.set(X0 + len / 2, y, 0); TXT.add(R, t);
    const p = TXT.roundedBox(0.03, 0.34, 0.34, 0.008, galvDark); p.position.set(X0 - 0.015, y, 0); TXT.add(R, p);   /* the end plate */
    const e = new THREE.Mesh(new THREE.RingGeometry(RT * 0.8, RT, 24), galvDark); e.rotation.y = Math.PI / 2; e.position.set(X0 + len + 0.001, y, 0); TXT.add(R, e);
    return t;
  }
  function dunnage(x, y) { const b = TXT.roundedBox(0.15, 0.15, 1.0, 0.01, wood); b.position.set(x, y + 0.075, 0); TXT.add(R, b); TXT.contact(R, b); return b; }
  /* lower layer: the anticipated length on four blocks on the pad */
  [X0 + 0.4, X0 + LA * 0.36, X0 + LA * 0.68, X0 + LA - 0.4].forEach((x) => dunnage(x, 0.06));
  const yLow = 0.06 + 0.15 + RT;
  tube(LA, yLow);
  /* upper layer: the plan length on blocks laid across the lower tube */
  [X0 + 0.4, X0 + LP * 0.5, X0 + LP - 0.4].forEach((x) => dunnage(x, yLow + RT));
  const yUp = yLow + RT + 0.15 + RT;
  tube(LP, yUp);

  /* the pad and the station behind, its heads turned away across the grass */
  const padM = new THREE.MeshStandardMaterial({ color: 0xd9ccb0, map: K.tex('concrete'), roughness: 0.96 });
  const pad = TXT.roundedBox(14, 0.06, 9, 0.02, padM); pad.position.set(-0.5, 0.03, 2.4); TXT.add(R, pad);   /* the yard's caliche pad runs to the near grass (round 1) */
  const hero = F.station(K, { pan: [2.6, 3.4], tilt: [-0.05, -0.05] });
  hero.position.set(2.6, 0, -16); TXT.add(R, hero); TXT.contact(R, hero);   /* close on the right third, clear of the narrowed dek (round 1) */
  const pad2 = TXT.roundedBox(6, 0.06, 6, 0.02, padM); pad2.position.set(2.6, 0.03, -16); TXT.add(R, pad2);

  TXT.frame(R, { from: [-0.72, 1.25, 11.2], look: [-0.72, 2.55, 0] });
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 0, -6], distance: 60, shadowFar: 160 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 7000, seed: 23 });
  F.grass(TXT, R, { count: 26000, area: [-60, -160, 60, 14], avoid: [[-7.5, -2.2, 6.5, 7.0], [0.3, -19, 6.7, -13]], scale: [0.6, 1.2] });
  F.caprock(K, TXT, R, { x: -240, z: -400, width: 420, height: 22, ry: 0.25 });   /* round 2: in the thinned haze */
  TXT.weather(R, {});
  /* the labels ride the tube ends they name, measured through this camera */
  const pU = F.project(THREE, R, [X0, yUp + RT + 0.1, 0]), pL = F.project(THREE, R, [X0, yLow - RT - 0.12, 0]);
  const lu = document.getElementById('labU'), ll = document.getElementById('labL');
  lu.style.left = pU[0] + 'px'; lu.style.top = (pU[1] - 38) + 'px';
  ll.style.left = pL[0] + 'px'; ll.style.top = (pL[1] + 8) + 'px';
  window.__txLeaders = [];
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { floor: 0.22 });   /* round 2: the pale pad stays pale under the footer */
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(7)
import json
c=json.load(open('/home/user/TexasAIDocket/out/2026-09-28/copy.json'))['slides']['S7']
shell.write(7,
  "Archetype OBJECT_AND_CAPTION. RENDERED through txthree.js in the deck's declared stormFront world. Two lengths of the station's own galvanized tube stacked on timber dunnage on the pad, square on and left aligned on one end plate, at the plan's 2026 camera capital and the anticipated 2026 camera capital on one scale, the station behind with its heads turned away across the grass.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:620px;", dek_css="width:560px;", fit=(80, 108, 3),
  extra_css='  .lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:26px; letter-spacing:0.05em; color:#F1ECE3; z-index:12; white-space:nowrap; text-shadow:0 0 6px rgba(12,12,14,0.9), 0 1px 12px rgba(12,12,14,0.7); }',
  extra_html=f'<div class="lab" id="labU">{c["labels"][0]}</div>\n<div class="lab" id="labL">{c["labels"][1]}</div>')
