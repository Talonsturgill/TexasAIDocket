"""Rebuilds carousel no. 32 frame 6, its own model and camera, on four worlds of the new engine.

MEASUREMENT, NOT A TEMPLATE. It borrows no. 32's chassis model so the before and after differ in
the engine alone. It swallows that chassis's TXDECK.declare to set a new light, which a deck never
does. Render with:
    python3 .claude/skills/carousel-engine/render.py --slides-dir examples/world-proof/slides --out-dir out/world-proof
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
src = (ROOT / "runs/carousel/2026-09-23/slides/slide-06.html").read_text()
out = Path(__file__).resolve().parent / "slides"; out.mkdir(parents=True, exist_ok=True)
GRADE = ('{ exposure: 0.0, saturation: 1.06, contrast: 1.08, filmic: true, lift: [0.010, 0.012, 0.020], '
         'gain: [1.03, 1.0, 0.97], vignette: 0.22, bloom: { threshold: 0.78, strength: 0.26, radius: 12 }, '
         'grain: { amount: 0.018, size: 2, seed: 20260924 }, aberration: 0, dither: true, sharpen: 0.22 }')
def page(n, az, el, world, note, dark_ink=False, lamp=False):
    load = ('<script>window.__decl = TXDECK.declare; TXDECK.declare = function () { return null; };</script>\n'
            '<script src="@@ASSETS@@/js/deck/2026-09-23-gensetyard.js"></script>\n'
            '<script>TXDECK.declare = window.__decl;\n'
            'TXDECK.declare({ world: "proof-%s", light: { az: %s, el: %s }, sky: "%s", ground: "#1c2436", '
            'material: "#C9C4B6", accent: "#E0A33F", grade: %s });</script>' % (world, az, el, world, GRADE))
    h = src.replace('<script src="@@ASSETS@@/js/deck/2026-09-23-gensetyard.js"></script>', load)
    if dark_ink:
        h = h.replace("</style>", "  .hook, .dek { color:#15181d !important; } .tx-site { color:#3a3f47 !important; }\n</style>", 1)
        h = h.replace("ink: '#9AA0AC'", "ink: '#3a3f47'")
    a = h.index("  /* THE COUNT, FROM figures.json"); b = h.index("  const cx = Y.develop(")
    scene = ("""  /* %s */
  const UNITS = 40;
  const W = TXT.deckWorld();                /* the chassis declared sky: %s */
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 38 });
  TXT.frame(R, { fov: 38, from: [-17.5, 2.4, 10.5], look: [-3.0, 1.45, -2.2] });   // no. 32's camera, exactly
  TXT.sky(R);
  const rig = JSON.parse(JSON.stringify(W.rig)); rig.key.shadowSize = 34; rig.key.mapSize = 4096;
  TXT.deckRig(R, rig, { target: [-3, 0, -14], distance: 120, shadowFar: 320 });
  TXT.ground(R, { surface: 'caliche', size: 900, tile: 5 });
  /* the pad is bare and graded: grass only past its edge, stones on it */
  TXT.scatter(R, { kind: 'grass', count: 7000, area: [-120, -280, 90, 40], avoid: [[-26, -200, 14, 30]], seed: 3 });
  TXT.scatter(R, { kind: 'scrub', count: 240, area: [-170, -330, 130, 30], avoid: [[-30, -205, 18, 34]], seed: 7 });
  TXT.scatter(R, { kind: 'rock', count: 500, area: [-26, -60, 14, 3], avoid: [[-9.5, -186, 5.5, 4.4]], seed: 11 });   // none under the type
  const M = Y.mats(TXT);
  const hero = Y.genset(THREE, M, { lamp: %s });
  TXT.add(R, hero); TXT.contact(R, hero);
  for (let i = 1; i < UNITS; i++) {
    const g = Y.genset(THREE, M, { detail: i < 3, lamp: %s && i < 12 });
    g.position.set(0, 0, -i * 4.6);
    TXT.add(R, g); if (i < 8) TXT.contact(R, g);
  }
  const who = Y.person(THREE, { cloth: 0x3c4a5c });
  who.position.set(-7.3, 0, 1.1); who.rotation.y = -1.2;
  TXT.add(R, who); TXT.contact(R, who, { opacity: 0.8 });
  TXT.weather(R, {});
""" % (note, world, "true" if lamp else "false", "true" if lamp else "false"))
    h = h[:a] + scene + h[b:]
    h = h.replace('TXDECK.finish(cx, { bloom: { threshold: 0.8, strength: 0.18, radius: 10 } });', 'TXDECK.finish(cx);')
    (out / f"slide-{n:02d}.html").write_text(h)
page(1, -40, 10, "goldenHour", "GOLDEN HOUR, front lit")
page(2, 118, 5, "goldenHour", "GOLDEN HOUR, into the sun")
page(3, -60, 35, "blueHour", "BLUE HOUR, lamps on", lamp=True)
page(4, 30, 62, "highNoon", "HIGH NOON, bleached", dark_ink=True)
print("ok")
