import sys; sys.path.insert(0,'.'); import shell
scene = r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [0x1b1c20, 0.0], exposure: W.exposure, tone: W.tone, fov: 46 });
  /* A committee hearing room, from behind the dais: the lawmakers' own view of the gallery. The
   * room's back wall at z = -12 is the gallery's rear wall, the window on the left wall throws the
   * deck's low storm light across the rows, and the dais bench runs across the foreground. */
  const ROOM = { w: 34, d: 24, h: 10 };   /* panel round 3: a room wide and tall enough that its back wall has no edge in frame, so it can't read as a plate */
  TXT.interior(R, { w: ROOM.w, d: ROOM.d, h: ROOM.h, floor: 'concrete', wall: 0x3b4250, trim: 0x1f232b,   /* panel round 1: a lit brown wall read as a plate behind the type */ window: 'left', ceiling: true, light: 2.6 });
  TXT.frame(R, { from: [0.6, 3.5, 9.6], look: [0, 0.9, -3.2] });   /* higher and further back, so the back wall's foot drops under the dek and the dais sinks under the label (round 1) */
  TXT.deckRig(R, W.rig, { target: [0, 0, 0], distance: 40, shadowFar: 90 });
  /* the dais and the witness podium in the well facing it */
  const dais = K.make('hearing_dais', { seed: 2, curve: 12, seats: 7, mics: false });   /* round 2: the goosenecks crossed the footer */
  dais.position.set(0, 0, 6.2); dais.rotation.y = Math.PI; TXT.add(R, dais); TXT.contact(R, dais);
  const pod = K.make('podium', { seed: 1 }); pod.position.set(0, 0, 4.4);   /* in the well on the aisle, between the front row and the dais (round 1) */ TXT.add(R, pod); TXT.contact(R, pod);

  /* THE DATA. One seat for each utility the hearing counted: 160 seats, ten rows of sixteen, and a
   * white plan binder standing on 8 of them, the 8 that had complied. The seats face the dais. */
  const TOTAL = 160, FILED = 8, ROWS = 10, PER = TOTAL / ROWS;
  const seats = K.make('public_seating', { seed: 5, rows: ROWS, perRow: PER, aisle: true, color: 0x5d6b82, frame: 'chrome' });
  const SZ = -1.6;
  seats.position.set(0, 0, SZ); TXT.add(R, seats); TXT.contact(R, seats);
  /* the seating model's own grid, pitch 0.56 m, rows 0.95 m, a 0.9 m aisle, reproduced here so a
   * binder stands on a seat and not between two */
  const xs = [];
  for (let i = 0; i < PER / 2; i++) xs.push(-0.45 - (PER / 2 - 1 - i) * 0.56 - 0.28);
  for (let i = 0; i < PER / 2; i++) xs.push(0.45 + i * 0.56 + 0.28);
  /* WHICH EIGHT is not in the record, so the seats are chosen to be seen: spread over the rows a
   * reader can count at feed size, two to a near row (round 1). The count is FILED, never the pick. */
  const rng = TX.rng(F.SEED + 8);
  const picked = [[0, 6], [0, 10], [2, 4], [2, 11], [4, 7], [4, 12], [6, 3], [8, 10]].slice(0, FILED).map((p) => p[0] * PER + p[1]);
  const binderM = new THREE.MeshStandardMaterial({ color: 0xf6f3ec, roughness: 0.6 });
  const tabM = new THREE.MeshStandardMaterial({ color: F.ACCENT, roughness: 0.5 });
  picked.forEach((k) => {
    const j = Math.floor(k / PER), i = k % PER;
    const lx = xs[i], lz = (j - (ROWS - 1) / 2) * -0.95;
    const x = lx, z = SZ + lz;
    const b = TXT.roundedBox(0.4, 0.46, 0.075, 0.012, binderM);   /* a 3 in binder standing on the seat against its back, face to the dais */
    b.position.set(x, 0.47 + 0.23, z - 0.12); b.rotation.set(-0.12, (rng() - 0.5) * 0.3, 0); TXT.add(R, b);
    const tab = TXT.roundedBox(0.016, 0.44, 0.08, 0.003, tabM); tab.position.set(-0.2, 0, 0); b.add(tab);
  });
  TXT.weather(R, {});
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.atmosphere(cx, { a: 0.3, floor: 0.45, floorH: 300 });
  F.soften(cx, ['.tx-site', '.src', '.kick', '.count', '.lab']);
  TXDECK.finish(cx);
'''
k,h,b,s = shell.copy(8)
shell.write(8,
  "Archetype GRID. RENDERED through txthree.js in a TXT.interior room lit by the deck's rig through its window. A committee hearing room from the back of the gallery: a curved dais, a witness podium in the well, and 160 seats in ten rows of sixteen, one for each utility the hearing counted, eight of them carrying a white plan binder with an accent spine tab.",
  k, h, b, s, scene, hook_css="left:80px; top:150px; width:900px;", dek_css="width:900px;", fit=(84, 116, 2),
  extra_css='  .lab { position:absolute; font-family:"JetBrains Mono", monospace; font-size:24px; letter-spacing:0.06em; color:#C9BFAF; z-index:12; text-shadow:0 0 6px rgba(12,12,14,0.9); }',
  extra_html='<div class="lab" id="lab1" style="left:80px; top:1180px;">ONE SEAT FOR EACH UTILITY THE HEARING COUNTED</div>')
