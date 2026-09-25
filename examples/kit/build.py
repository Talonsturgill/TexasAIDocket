#!/usr/bin/env python3
"""Proof pages for THE KIT (assets/js/txkit.js): every model rendered in the engine's world.

    python3 examples/kit/build.py --family homes --out out/kit/homes/slides
    python3 .claude/skills/carousel-engine/render.py --slides-dir out/kit/homes/slides --out-dir out/kit/homes/render

For a family it writes one LINEUP page (every model side by side with a 1.75 m person) and one
HERO page per model (a three-quarter close view). Each page logs `KIT_STATS {json}` through
console.error, which render.py records in render_report.json: build time and triangle count.
`--names a,b` limits it to some models. `--world` picks a TXT.worlds preset.

This is a harness, not a style. A deck composes its own frames.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1080px;height:1350px;overflow:hidden;background:#000}
canvas{position:absolute;left:0;top:0;width:1080px;height:1350px}</style></head><body>
<canvas id="art" width="2160" height="2700"></canvas>
<script src="@@ASSETS@@/js/noise.js"></script><script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script><script src="@@ASSETS@@/js/txdeck.js"></script>
<script>TXDECK.declare({ world: "kit-proof", light: { az: __AZ__, el: __EL__ }, sky: "__WORLD__", ground: "#222",
  material: "#999", accent: "#E0A33F", grade: { exposure: 0, saturation: 1.04, contrast: 1.06, filmic: true,
  vignette: 0.16, dither: true } });</script>
<script type="module">
import * as THREE from '@@ASSETS@@/js/three.module.min.js';
import { init } from '@@ASSETS@@/js/txthree.js';
import { initKit } from '@@ASSETS@@/js/txkit.js';
window.renderReady = (async () => {
  const TXT = init(THREE);
  const t0 = performance.now();
  const K = initKit(THREE, TXT);
  const gl = document.createElement('canvas'); gl.width = 2160; gl.height = 2700;
  const W = TXT.deckWorld();
  const FOV = __FOV__;
  const FOGK = 1;
  const R = TXT.setup(gl, { w: 1080, h: 1350, fog: [W.haze, W.fogDensity * 0.35 * FOGK], exposure: W.exposure, tone: W.tone, fov: FOV });
  const specs = __SPECS__;                         // [[name, opts], ...]
  const made = [], stats = [];
  let x = 0;
  for (const [name, opts] of specs) {
    const tb = performance.now();
    const g = K.make(name, opts || {});
    const bb = new THREE.Box3().setFromObject(g), sz = new THREE.Vector3(); bb.getSize(sz);
    // a run hundreds of metres long (a power line) pushes a lineup's camera so far back that the
    // haze swallows every model, so a lineup leaves it to its own hero page
    if (specs.length > 1 && Math.max(sz.x, sz.z) > 300) { stats.push({ name, skipped: 'too long for a lineup' }); continue; }
    g.position.x = x + sz.x / 2 - (bb.min.x + bb.max.x) / 2; x += sz.x + Math.max(1.2, sz.x * 0.25);
    made.push(g); stats.push({ name, ms: Math.round(performance.now() - tb), size: [sz.x, sz.y, sz.z].map(v => +v.toFixed(2)) });
  }
  const off = x / 2; made.forEach(g => { g.position.x -= off; TXT.add(R, g); });
  // a person for scale, 1.75 m, at the left end
  let who = null;
  if (__PERSON__) {
    who = K.registry.person ? K.make('person', { seed: 5 }) :
      new THREE.Mesh(new THREE.CapsuleGeometry(0.22, 1.3, 6, 12), new THREE.MeshStandardMaterial({ color: 0x3c4a5c, roughness: 0.8 }));
    if (!K.registry.person) who.position.y = 0.875;
    // every model in a lineup may have been left to its own hero page, and then the person stands alone
    const first = made.length ? new THREE.Box3().setFromObject(made[0]) : null;
    who.position.x = first ? first.min.x - 1.4 : 0; who.position.z = first ? first.max.z - 0.6 : 0;
    TXT.add(R, who);
  }
  const all = new THREE.Box3(); made.forEach(g => all.expandByObject(g)); if (who) all.expandByObject(who);
  const c = new THREE.Vector3(), s = new THREE.Vector3(); all.getCenter(c); all.getSize(s);
  const rad = Math.max(s.x, s.y * 1.25, s.z) * 0.62 + 0.5;
  const dist = rad / Math.tan(FOV * Math.PI / 360) * __DIST__;
  // a wide scene sits far from the camera, so the proof's haze thins with distance to keep it legible
  if (R.scene.fog && R.scene.fog.density) R.scene.fog.density *= Math.min(1, 45 / dist);
  const dir = new THREE.Vector3(__DIR__).normalize();
  const from = c.clone().add(dir.multiplyScalar(dist)); from.y = Math.max(from.y, 1.6);
  TXT.frame(R, { from: [from.x, from.y, from.z], look: [c.x, c.y * 0.9, c.z] });
  // the engine's far plane is 1 km, and a model hundreds of metres long is framed from further away
  R.camera.far = Math.max(R.camera.far, dist + rad * 4); R.camera.updateProjectionMatrix();
  TXT.sky(R);
  const rig = JSON.parse(JSON.stringify(W.rig)); rig.key.shadowSize = Math.max(12, rad * 2.2); rig.key.mapSize = 2048;
  TXT.deckRig(R, rig, { target: [c.x, 0, c.z], distance: Math.max(80, rad * 4), shadowFar: Math.max(200, rad * 10) });
  TXT.ground(R, { surface: '__SURFACE__', size: Math.max(600, rad * 30), tile: 4 });
  made.forEach(g => TXT.contact(R, g)); if (who) TXT.contact(R, who, { opacity: 0.8 });
  TXT.weather(R, {});
  const tb = performance.now();
  await TXT.snapshot(R);
  const info = R.renderer.info.render;
  console.error('KIT_STATS ' + JSON.stringify({ build_ms: Math.round(tb - t0), render_ms: Math.round(performance.now() - tb),
    triangles: info.triangles, calls: info.calls, models: stats }));
  const cx = document.getElementById('art').getContext('2d'); cx.scale(2, 2); cx.drawImage(gl, 0, 0, 1080, 1350);
  TXDECK.finish(cx);
  return true;
})();
</script></body></html>
"""


def family_names(family: str) -> list[str]:
    """Names a family file defines, read from its K.define('name', ...) calls."""
    src = (REPO / "assets" / "js" / "kit" / f"{family}.js").read_text(encoding="utf-8")
    return re.findall(r"K\.define\(\s*['\"]([a-z0-9_]+)['\"]", src)


def page(specs, *, person=True, world="goldenHour", fov=34, dist=1.25, direction=(0.55, 0.32, 1.0),
         surface="grass", az=-40, el=18) -> str:
    return (PAGE.replace("__SPECS__", json.dumps(specs)).replace("__PERSON__", "true" if person else "false")
            .replace("__WORLD__", world).replace("__FOV__", str(fov)).replace("__DIST__", str(dist))
            .replace("__DIR__", ", ".join(str(v) for v in direction)).replace("__SURFACE__", surface)
            .replace("__AZ__", str(az)).replace("__EL__", str(el)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--names", default="")
    ap.add_argument("--world", default="goldenHour")
    ap.add_argument("--surface", default="grass")
    a = ap.parse_args()
    names = [n for n in a.names.split(",") if n] or family_names(a.family)
    if not names:
        print(f"no K.define calls found in assets/js/kit/{a.family}.js", file=sys.stderr)
        return 1
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("slide-*.html"):
        old.unlink()
    pages = [page([[n, {"seed": i + 1}] for i, n in enumerate(names)], world=a.world, surface=a.surface)]
    for i, n in enumerate(names):
        pages.append(page([[n, {"seed": 1}]], world=a.world, surface=a.surface, dist=1.05))
    for i, html in enumerate(pages, 1):
        (out / f"slide-{i:02d}.html").write_text(html, encoding="utf-8")
    print(f"{len(pages)} page(s): slide-01 is the lineup of {len(names)}, then one hero each: {', '.join(names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
