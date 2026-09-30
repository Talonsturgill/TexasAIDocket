import sys; sys.path.insert(0,'.'); import shell; from common import *
scene = figs('spanish_human_pct') + r'''
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, 0.002], exposure: W.exposure * 1.22, tone: W.tone, fov: 55, near: 0.05, far: 200 });
  /* ONE EXCEPTION. A classroom, a row of five desks by the window wall, and a reader at
   * spanish_human_pct of them, which is every one. The room is TXT.interior with the window lit. */
  TXT.interior(R, { w: 10.5, d: 8.5, h: 8.5, floor: 'concrete', wall: 0xdfe2e2, window: null, ceiling: false, light: 1.9 });
  const n = 5, withR = Math.round(n * FIG.spanish_human_pct / 100), z = -0.05;
  let readers = 0;
  for (let i = 0; i < n; i++) {
    const x = -2.9 + i * 1.45, d = F.desk(K, { seed: 60 + i }); d.position.set(x, 0, z); TXT.add(R, d); TXT.contact(R, d);
    if (i < withR) F.attend(K, { x, z, rotY: 0 }, { seed: 70 + i }).forEach((p) => { TXT.add(R, p); TXT.contact(R, p); readers++; });
  }
  if (readers !== withR) throw new Error('readers drawn wrong');
  /* the classroom's window band on the left wall at sill height, lit by the overcast day, with an
   * aluminium frame and mullions, so the readers sit against the light and the wall above stays
   * one plain value behind the type */
  { const WZ = -0.6, WL = 6.4, WH = 1.55, WY = 1.72, WX = -5.25 + 0.11;
    const pane = new THREE.Mesh(new THREE.PlaneGeometry(WL, WH), new THREE.MeshBasicMaterial({ color: 0xd6dfe6 }));
    pane.material.color.multiplyScalar(1.15); pane.rotation.y = Math.PI / 2; pane.position.set(WX, WY, WZ); TXT.add(R, pane);
    const al = new THREE.MeshStandardMaterial({ color: 0x9a9ea3, roughness: 0.45, metalness: 0.6 });
    const bar = (w, h, d, x, y, z) => { const m = TXT.roundedBox(w, h, d, 0.008, al); m.position.set(x, y, z); TXT.add(R, m); };
    bar(0.06, 0.07, WL + 0.1, WX + 0.02, WY - WH / 2, WZ); bar(0.06, 0.07, WL + 0.1, WX + 0.02, WY + WH / 2, WZ);
    bar(0.16, 0.05, WL + 0.2, WX + 0.08, WY - WH / 2 - 0.05, WZ);
    for (let k = 0; k <= 4; k++) bar(0.06, WH, 0.06, WX + 0.02, WY, WZ - WL / 2 + k * WL / 4); }
  /* the room a scorer works in: a teacher desk with a monitor and a paper stack at the back
   * right and a cabinet. No desk stands empty on the frame whose claim is that every answer is read */
  const cab = K.make('filing_cabinet', { drawers: 4 }); cab.position.set(4.6, 0, -3.8); TXT.add(R, cab); TXT.contact(R, cab);
  const td = K.make('desk', { seed: 3 }); td.position.set(2.6, 0, -3.3); TXT.add(R, td); TXT.contact(R, td);
  const mon = K.make('monitor', { seed: 2 }); mon.position.set(2.4, 0.76, -3.45); TXT.add(R, mon);
  const ds = K.make('document_stack', { seed: 4 }); ds.position.set(3.1, 0.76, -3.2); TXT.add(R, ds);
  TXT.frame(R, { from: [5.0, 1.1, 5.8], look: [0.2, 1.62, -1.2] });
  /* indoors the deck's key comes only through the window band, so it is dimmed to a trace: a
   * full key through the open side threw a hard shaft across the wall that no window cast */
  const rig5 = TXT.deckRig(R, W.rig, { target: [0, 0, -1.6], distance: 14, shadowFar: 30, normalBias: 0.03 }); rig5[0].intensity *= 0.18;
  TXT.weather(R, { grime: 0.45 });
  const cx = F.develop(await TXT.snapshot(R), gl);
  F.post(cx, { a: 0.3, type: ['.kick', '.count', '.hook', '.dek'], typeBlur: 34, typeFeather: 90 });
  TXDECK.finish(cx);
  window.__txDrawn = { desks: n, readers: readers };
'''
k,h,b,s = shell.copy(5)
shell.write(5, "Archetype FIGURE_SCALE. RENDERED through txthree.js in a TXT.interior classroom lit by the deck's rig and its window. A row of five desks, a reader in bluebonnet seated at every one, bent to the screen, the window wall behind.",
  k, h, b, s, scene, fit=(74, 100, 2))
