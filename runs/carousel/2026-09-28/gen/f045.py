import sys, json; sys.path.insert(0,'.'); import shell
def scene(n):
    report = (n == 5)
    return r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [0x1b1c20, 0.0], exposure: W.exposure, tone: W.tone, fov: 44 });
  /* An office under a window full of storm light, seated at the desk. The same room, desk and camera
   * on frames 4 and 5: on 4 the PUCT order's page lies on the desk, on 5 the SPS report's page lies
   * over it. The window light is the deck's rig through the left wall. */
  const REPORT = ''' + ('true' if report else 'false') + r''';
  const ROOM = { w: 4.6, d: 4.4, h: 2.9 };
  TXT.interior(R, { w: ROOM.w, d: ROOM.d, h: ROOM.h, floor: 'concrete', wall: 0x9c9184, trim: 0x4a433c, window: 'left', ceiling: true, light: 3.4 });
  const desk = K.make('desk', { seed: 3, pedestal: 'right' });
  desk.position.set(0, 0, -1.3); TXT.add(R, desk); TXT.contact(R, desk);
  const stack = K.make('document_stack', { seed: 6, count: 3 }); stack.position.set(0.5, 0.76, -1.2); stack.rotation.y = -0.3; TXT.add(R, stack);
  /* the binders in quiet covers: a navy and a crimson read as a second accent and as flag red (round 1) */
  stack.traverse((m) => { if (m.isMesh && m.material && m.material.color) { const h = m.material.color.getHex(); const to = { 0x1f2a44: 0x3a3833, 0x6b1f23: 0x8f836c, 0x2d4a3a: 0x5d584d }[h]; if (to != null) { m.material = m.material.clone(); m.material.color.setHex(to); } } });
  const chair = K.make('office_chair', { seed: 2, style: 'task' }); chair.position.set(0.55, 0, -0.35); chair.rotation.y = Math.PI + 0.4; TXT.add(R, chair); TXT.contact(R, chair);

  /* THE PAGES. The order is a list of measures, a to n, as hairlines, line j left bare where the DOM
   * line lands. The report is a table of numbered metrics with the tenth line bare. */
  function page(entries, x, z, rot, lift, paper) {
    const t = F.pageTexture(THREE, entries, { top: 220, paper: paper });
    const m = new THREE.Mesh(new THREE.PlaneGeometry(0.216, 0.279), new THREE.MeshStandardMaterial({ map: t, roughness: 0.82 }));
    m.rotation.x = -Math.PI / 2; m.rotation.z = rot; m.position.set(x, 0.7615 + lift, z); m.receiveShadow = true; m.castShadow = true; TXT.add(R, m);
    return m;
  }
  const order = [{ kind: 'heading', w: 0.55 }, { kind: 'gap', h: 30 }];
  for (let i = 0; i < 14; i++) order.push(i === 9 ? { w: 0.05, indent: 0, a: 0.8 } : { w: 0.55 + 0.4 * ((i * 37) % 10) / 10, indent: 40 });   /* line j: only its letter's tick in the margin, the line itself bare (round 2) */
  page(order, -0.12, -1.24, 0.06, 0.0005, REPORT ? '#dcd5c6' : null);   /* under the report the order is the older, warmer sheet (round 1) */
  if (REPORT) {
    const rep = [{ kind: 'heading', w: 0.7 }, { kind: 'gap', h: 30 }];
    for (let i = 0; i < 14; i++) rep.push(i === 9 ? { w: 0.05, indent: 0, a: 0.8 } : { w: 0.4 + 0.5 * ((i * 53) % 10) / 10, indent: 20 });
    page(rep, -0.12, -1.24, -0.16, 0.004);   /* turned 13 degrees about the same line, so the rule lands where frame 4 put it and both corners show (round 1) */
  }
  /* THE WINDOW (round 2): the storm deck through the back wall's glass at the right edge, clear of the
   * hook and dek, so the room stands in the deck's world. A pane of sky, a sash and a mullion. */
  (function () {
    const c = document.createElement('canvas'); c.width = 64; c.height = 256; const g = c.getContext('2d');
    const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#8e99a6'); gr.addColorStop(0.62, '#c4c6c2'); gr.addColorStop(1, '#efe6d2');   /* panel round 1: the glass read as a dark frame, so it carries the storm's lit horizon */
    g.fillStyle = gr; g.fillRect(0, 0, 64, 256);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    const pane = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.3), new THREE.MeshBasicMaterial({ map: t, toneMapped: true }));
    pane.position.set(0.65, 1.55, -ROOM.d / 2 + 0.11);   /* panel round 2: the glass sat 1 cm behind the wall's face and only the sash showed */ TXT.add(R, pane);
    const sash = new THREE.MeshStandardMaterial({ color: 0xa39a8c, roughness: 0.7 });   /* panel round 3: a pale painted sash, since a black one read as a monitor bezel */
    [[0.2, 1.55, 0.06, 1.42], [1.1, 1.55, 0.06, 1.42], [0.65, 0.87, 0.96, 0.07], [0.65, 2.23, 0.96, 0.07], [0.65, 1.55, 0.03, 1.3]].forEach(function (b) {
      const m = TXT.roundedBox(b[2], b[3], 0.05, 0.008, sash); m.position.set(b[0], b[1], -ROOM.d / 2 + 0.13); TXT.add(R, m);
    });
  })();
  TXT.frame(R, { from: [0.2, 1.36, -0.22], look: [-0.12, 0.82, -1.42] });
  TXT.deckRig(R, W.rig, { target: [0, 0.8, -1.2], distance: 8, shadowFar: 20 });
  TXT.weather(R, { grime: 0.3 });
  /* the callout: the page's own line, set in DOM, with a leader landing on the bare line it names */
  /* the bare line's own place on the sheet that lies on top, turned with that sheet (round 2: the old
   * offset ran toward the lens instead of up the page and landed on blank paper) */
  const ROT = REPORT ? -0.16 : 0.06, LY = 0.279 * (0.5 - (220 + 70 + 30 + 9 * 44 + 22) / 2232);
  const lineAt = F.project(THREE, R, [-0.12 - LY * Math.sin(ROT) + 0.03 * Math.cos(ROT), 0.765, -1.24 - LY * Math.cos(ROT) + 0.03 * Math.sin(ROT)]);
  const lab = document.getElementById('lab1'), svg = document.getElementById('lead'), NS = 'http://www.w3.org/2000/svg';
  const lb = lab.getBoundingClientRect();
  const from = [lb.left + 40, lb.top - 8];
  const pl = document.createElementNS(NS, 'polyline');
  pl.setAttribute('points', from[0] + ',' + from[1] + ' ' + from[0] + ',' + (from[1] - 30) + ' ' + lineAt[0].toFixed(1) + ',' + lineAt[1].toFixed(1));
  pl.setAttribute('fill', 'none'); pl.setAttribute('stroke', '#F1ECE3'); pl.setAttribute('stroke-width', '2'); svg.appendChild(pl);
  window.__txLeaders = [{ target: 'the bare line on the page', at: lineAt, to: lineAt }];
  /* the accent underlines the whole quoted line, so it can't read as a meter half full (round 2) */
  { const rg = document.createRange(); rg.selectNodeContents(lab); const r0 = rg.getBoundingClientRect(); document.getElementById('acc').style.width = Math.round(r0.width) + 'px'; }
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.3, floor: 0.45, floorH: 420 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab'], { blur: 16 });
  TXDECK.finish(cx);
'''
for n in (4, 5):
    k,h,b,s = shell.copy(n)
    labs = json.load(open('/home/user/TexasAIDocket/out/2026-09-28/copy.json'))['slides'][f'S{n}']['labels']
    labhtml = ''.join(f'<div class="lab" id="lab{i+1}" style="top:{[1036, 1130, 1174][i]}px;">{t}</div>\n' for i, t in enumerate(labs))
    shell.write(n,
      ("Archetype DOCUMENT. RENDERED through txthree.js in a TXT.interior room lit by the deck's rig through its window. " +
       ("Seated at a desk under the storm light: the PUCT order's page on the desk, its measures as hairlines with line j set in DOM over one accent bar, a document stack behind it." if n == 4 else
        "Frame 4's room, desk and camera unchanged: the SPS annual report's page now over the order, turned against the order, its metric line and answer set in DOM over the same accent bar.")),
      k, h, b, s, scene(n), hook_css="left:80px; top:150px; width:900px;", dek_css="width:880px;", fit=(80, 112, 2),
      extra_css='''  .lab { position:absolute; left:80px; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.02em; color:#F1ECE3; z-index:12; white-space:nowrap; text-shadow:0 0 6px rgba(12,12,14,0.95), 0 1px 12px rgba(12,12,14,0.8); }
  #acc { position:absolute; left:80px; top:1080px; width:420px; height:12px; background:#2A7A9E; z-index:12; }
  svg#lead { position:absolute; left:0; top:0; width:1080px; height:1350px; z-index:11; overflow:visible; }''',
      extra_html='<svg id="lead" width="1080" height="1350" viewBox="0 0 1080 1350"></svg>\n<div id="acc"></div>\n' + labhtml)
