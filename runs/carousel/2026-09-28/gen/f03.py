import sys, json; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  /* Up level with the crossarm at 12 m, on the station's sunlit side, the two heads at kit detail on
   * the right two thirds, one turned toward the lens and one away, the mast dropping out of the
   * bottom and the plain far below. THE DATA: two cameras to a site, each head carrying its own
   * leader from the one label that names them. */
  const CAMERAS_PER_SITE = 2;
  const hero = F.station(K, { pan: [-1.1, 1.9], tilt: [-0.1, -0.06], enclosure: false });   /* the enclosure sits under the site line from up here, and a reader can't see it (round 1) */
  TXT.add(R, hero); TXT.contact(R, hero);
  const CAM = [-4.05, 12.0, 2.2];
  TXT.frame(R, { from: CAM, look: [1.06, 12.35, -0.94] });   /* round 2: the mast just left of the site line and the heads dropped below the dek, since a bright mast behind the site line struck it in every pan that kept both heads in frame */
  TXT.sky(R);
  TXT.deckRig(R, W.rig, { target: [0, 8, 0], distance: 40, shadowFar: 90 });
  TXT.ground(R, { surface: 'grass', color: F.STRAW, size: 7000, seed: 37 });
  F.grass(TXT, R, { count: 70000, area: [-80, -160, 80, 40], avoid: [[-3, -3, 3, 3]], scale: [0.7, 1.3] });   /* panel round 4: the plain 12 m below read as a flat plane with sprites */
  const padM = new THREE.MeshStandardMaterial({ color: 0xd9ccb0, map: K.tex('concrete'), roughness: 0.96 });
  const pad = TXT.roundedBox(7, 0.06, 7, 0.02, padM); pad.position.set(0, 0.03, 0); TXT.add(R, pad);
  const road = K.make('caliche_road', { seed: 5, length: 90, curve: 0.2 }); road.position.set(4, 0, 46); road.rotation.y = 0.2; TXT.add(R, road);
  F.caprock(K, TXT, R, { x: 380, z: -330, width: 420, height: 14, ry: -0.6 });   /* round 2: in the thinned haze */
  TXT.weather(R, {});

  /* leaders, as DOM SVG polylines that end on the thing they name, each target taken from the
   * model's own userData through this camera */
  const L = hero.userData.lenses, heads = hero.userData.heads;
  const ant = [0, hero.userData.dims.H - 0.45 - 1.4, -(0.11 + (0.2 - 0.11) * 0.05) - 0.36];
  const svg = document.getElementById('lead'), NS = 'http://www.w3.org/2000/svg';
  const leaders = [];
  /* ELBOW LEADERS (round 1): out of the label's last glyph along its own line, then straight up
   * to the head, so each reads as annotation rather than as a cable from the mast. A dark keyline
   * under the cream stroke keeps it off the plain. */
  function leader(fromXY, world, label, y) {
    const at = F.project(THREE, R, world);
    const side = at[0] < fromXY[0] ? 1 : -1;   /* a bracket: up from the label's end, then across to the head's near side */
    const pts = [[fromXY[0], y], [fromXY[0], at[1] + 6 * side], [at[0] + side * 34, at[1] + 6 * side]];
    [['#15171C', '5', '0.45'], ['#F1ECE3', '2', '1']].forEach(function (st) {
      const p = document.createElementNS(NS, 'polyline');
      p.setAttribute('points', pts.map((q) => q[0].toFixed(1) + ',' + q[1].toFixed(1)).join(' '));
      p.setAttribute('fill', 'none'); p.setAttribute('stroke', st[0]); p.setAttribute('stroke-width', st[1]); p.setAttribute('stroke-opacity', st[2]);
      svg.appendChild(p);
    });
    const dot = document.createElementNS(NS, 'circle'); dot.setAttribute('cx', at[0]); dot.setAttribute('cy', at[1]); dot.setAttribute('r', '6');
    dot.setAttribute('fill', 'none'); dot.setAttribute('stroke', '#F1ECE3'); dot.setAttribute('stroke-width', '2'); svg.appendChild(dot);
    leaders.push({ target: label, at: at, to: at });
  }
  /* the leaders leave the label's LAST GLYPH, measured off the text itself (round 2: the box's right
   * edge is not where the words end) */
  const rg = document.createRange(); rg.selectNodeContents(document.getElementById('lab1'));
  const rs = rg.getClientRects(), l1 = rs[rs.length - 1];
  for (let i = 0; i < CAMERAS_PER_SITE; i++) {
    const h = heads[i];
    leader([l1.right + 12, 0], [h.x, h.y + 0.26, h.z], 'camera head ' + (i + 1), l1.top + l1.height / 2 - 6 + i * 12);
  }
  window.__txLeaders = leaders;
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { floor: 0.45, floorH: 470 });   /* round 2: the labels and footer sit on a shadowed plain */
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab'], { feather: 120 });   /* round 2: a wider feather, so the blur leaves no seam across the mast under the site line */
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(3)
c=json.load(open('/home/user/TexasAIDocket/out/2026-09-28/copy.json'))['slides']['S3']
labs=c['labels']
shell.write(3,
  "Archetype DIAGRAM. RENDERED through txthree.js in the deck's declared stormFront world. Level with the station's crossarm at 12 m on its sunlit side: the two camera heads at kit detail, one turned toward the lens and one away, DOM SVG elbow leaders from the label landing on each head, the plain far below.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:520px;", dek_css="width:500px;", fit=(76, 98, 3),
  extra_css='''  .lab { position:absolute; left:80px; font-family:"JetBrains Mono", monospace; font-size:22px; letter-spacing:0.03em; color:#F1ECE3; z-index:12; max-width:470px; line-height:1.25; text-shadow:0 0 6px rgba(12,12,14,0.9), 0 1px 12px rgba(12,12,14,0.7); }
  svg#lead { position:absolute; left:0; top:0; width:1080px; height:1350px; z-index:11; overflow:visible; }''',
  extra_html=f'<svg id="lead" width="1080" height="1350" viewBox="0 0 1080 1350"></svg>\n<div class="lab" id="lab1" style="top:1058px;">{labs[0]}</div>\n<div class="lab" id="lab2" style="top:1098px;">{labs[1]}</div>\n<div class="lab" id="lab3" style="top:1162px;">{labs[2]}</div>')
